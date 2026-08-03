#!/usr/bin/env python3
"""Content-addressed source store over s3://crypto-autoresearcher.

Specification: `docs/s3-source-store.md`. Read it first — this file implements
that layout and the reasoning for it lives there, not here.

    blobs/sha256/<aa>/<bb>/<digest>      immutable, write-once bytes
    packages/<PACKAGE-ID>/manifest.json  immutable; what one ingest produced
    index/by-{src,lit}/<ID>.json         alias: ledger ID -> digest
    incoming/                            unmanaged drop zone

Subcommands:

    plan    list a prefix and show what adoption would do. Writes nothing,
            needs only s3:ListBucket, and is the safe first call against an
            unfamiliar bucket.
    adopt   hash each object under a prefix, copy it to its blob key, write a
            package manifest. Server-side copy: bytes never transit this
            container.
    pull    materialise a package into inputs/<PACKAGE>/ in the layout
            tools/build_source_index.py already reads and verifies.
    verify  re-hash blobs and confirm each manifest entry resolves.

Credentials come from boto3's default chain and the resolved source is printed
before anything is transferred. That check is not decorative here: this
session's ambient AWS_* variables are the agent proxy's signing stub
(`AWS_ACCESS_KEY_ID=proxy-injected`), which authenticates as nobody.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = "crypto-autoresearcher"          # arn:aws:s3:::crypto-autoresearcher
SCHEMA = "crypto.autoresearch.s3_source_store.v1"
PROVENANCE_SCHEMA = "crypto.autoresearch.source_provenance.v1"
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"

BLOB_PREFIX = "blobs/sha256"
PACKAGE_PREFIX = "packages"
ALIAS_PREFIX = {"src": "index/by-src", "lit": "index/by-lit"}

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

# Streamed in parts so a 500 MB thesis does not have to fit in memory.
CHUNK = 1 << 20


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def blob_key(digest: str) -> str:
    if not _DIGEST.match(digest):
        raise ValueError(f"not a sha256 digest: {digest!r}")
    return f"{BLOB_PREFIX}/{digest[:2]}/{digest[2:4]}/{digest}"


def safe_name(key: str) -> str:
    """Flatten an object key to one filename while keeping distinct keys distinct."""
    return _SAFE.sub("_", key.strip("/")) or "unnamed"


def logical_name(key: str) -> str:
    """The name a human would call this file: its basename, sanitised."""
    return _SAFE.sub("_", os.path.basename(key.strip("/"))) or "unnamed"


def client(region: str | None, profile: str | None, endpoint_url: str | None = None,
           quiet: bool = False):
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    creds = session.get_credentials()
    if not quiet:
        if creds is None:
            print("credentials: NONE resolved", file=sys.stderr)
        else:
            key = creds.access_key
            print(f"credentials: source={creds.method} key={key[:8]}...", file=sys.stderr)
            if key.startswith("proxy-"):
                print("  WARNING: this is the agent proxy's signing stub, not a real\n"
                      "  AWS credential. It authenticates as nobody and every call\n"
                      "  will fail with InvalidAccessKeyId.", file=sys.stderr)
    return session.client("s3", region_name=region, endpoint_url=endpoint_url,
                          verify=CA_BUNDLE if os.path.exists(CA_BUNDLE) else None)


def list_objects(s3, bucket: str, prefix: str) -> list[dict]:
    out = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents") or []:
            if obj["Key"].endswith("/") or obj["Size"] == 0:
                continue                      # directory placeholder, not a file
            out.append({"key": obj["Key"], "size": obj["Size"],
                        "etag": (obj.get("ETag") or "").strip('"')})
    return sorted(out, key=lambda o: o["key"])


def digest_object(s3, bucket: str, key: str) -> str:
    """SHA-256 an object by streaming it.

    Deliberately not ETag: ETag is only an MD5 for single-part uploads, is a
    different construction for multipart ones, and is not a content hash the
    harness can compare against a locally recomputed value.
    """
    body = s3.get_object(Bucket=bucket, Key=key)["Body"]
    h = hashlib.sha256()
    for chunk in iter(lambda: body.read(CHUNK), b""):
        h.update(chunk)
    return h.hexdigest()


def object_exists(s3, bucket: str, key: str) -> bool:
    import botocore

    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as exc:
        if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


# --------------------------------------------------------------------------

def cmd_plan(args) -> int:
    s3 = client(args.region, args.profile, args.endpoint_url)
    objects = list_objects(s3, args.bucket, args.prefix)
    if not objects:
        print(f"no objects under s3://{args.bucket}/{args.prefix}")
        return 1
    total = sum(o["size"] for o in objects)
    print(f"{len(objects)} object(s), {total:,} bytes under "
          f"s3://{args.bucket}/{args.prefix}\n")
    for obj in objects:
        print(f"  {obj['size']:>12,}  {obj['key']}  ->  {logical_name(obj['key'])}")
    print("\nplan only: nothing written. `adopt` would hash each object and copy it")
    print("to blobs/sha256/<aa>/<bb>/<digest>, then write a package manifest.")
    return 0


def cmd_adopt(args) -> int:
    s3 = client(args.region, args.profile, args.endpoint_url)
    objects = list_objects(s3, args.bucket, args.prefix)
    if not objects:
        print(f"no objects under s3://{args.bucket}/{args.prefix}", file=sys.stderr)
        return 1

    files, adopted, already = [], 0, 0
    for obj in objects:
        digest = digest_object(s3, args.bucket, obj["key"])
        key = blob_key(digest)
        head = s3.head_object(Bucket=args.bucket, Key=obj["key"])
        if object_exists(s3, args.bucket, key):
            # Content addressing makes this safe to skip: the key encodes the
            # bytes, so an existing object at this key IS these bytes.
            already += 1
            print(f"  dedup {logical_name(obj['key'])}  {digest[:16]}")
        else:
            s3.copy_object(
                Bucket=args.bucket, Key=key,
                CopySource={"Bucket": args.bucket, "Key": obj["key"]},
                MetadataDirective="REPLACE",
                Metadata={"sha256": digest,
                          "original-filename": logical_name(obj["key"]),
                          "package": args.package,
                          "ingested-at": now()},
                ContentType=head.get("ContentType", "application/octet-stream"),
            )
            adopted += 1
            print(f"  store {logical_name(obj['key'])}  {digest[:16]}  {obj['size']:,} B")
        files.append({
            "logical_name": logical_name(obj["key"]),
            "sha256": digest,
            "blob_key": key,
            "bytes": obj["size"],
            "content_type": head.get("ContentType"),
            "origin_key": obj["key"],
            "origin_version_id": head.get("VersionId"),
        })

    manifest = {
        "schema": SCHEMA,
        "package_id": args.package,
        "created_at": now(),
        "bucket": args.bucket,
        "source_prefix": args.prefix,
        "note": ("Inputs, not results. Nothing here is evidence for or against a "
                 "hypothesis until a KN-LIT entry and a ledger record say so."),
        "files": sorted(files, key=lambda f: f["logical_name"]),
    }
    manifest_key = f"{PACKAGE_PREFIX}/{args.package}/manifest.json"
    if object_exists(s3, args.bucket, manifest_key) and not args.replace_manifest:
        print(f"\nREFUSE: {manifest_key} exists. Manifests are immutable — use a new\n"
              f"--package id, or pass --replace-manifest only to repair a failed run.",
              file=sys.stderr)
        return 1
    s3.put_object(Bucket=args.bucket, Key=manifest_key,
                  Body=(json.dumps(manifest, indent=2) + "\n").encode(),
                  ContentType="application/json")
    print(f"\n{adopted} stored, {already} already present -> s3://{args.bucket}/{manifest_key}")
    return 0


def cmd_pull(args) -> int:
    s3 = client(args.region, args.profile, args.endpoint_url)
    manifest_key = f"{PACKAGE_PREFIX}/{args.package}/manifest.json"
    manifest = json.loads(s3.get_object(Bucket=args.bucket, Key=manifest_key)["Body"].read())

    package_dir = os.path.join(REPO, "inputs", args.package)
    sources_dir = os.path.join(package_dir, "sources")
    os.makedirs(sources_dir, exist_ok=True)

    attempts, ok = [], 0
    for entry in manifest["files"]:
        name = safe_name(entry["logical_name"])
        dest = os.path.join(sources_dir, name)
        record = {"source_id": name,
                  "url": f"s3://{args.bucket}/{entry['blob_key']}",
                  "purpose": "external source document pulled from the S3 source store",
                  "retrieved_at": now(), "status": "unretrieved",
                  "bytes": None, "sha256": None,
                  "vendored_path": os.path.relpath(dest, REPO),
                  "revision_id": entry.get("origin_version_id"), "reason": None}
        try:
            s3.download_file(args.bucket, entry["blob_key"], dest)
            h = hashlib.sha256()
            with open(dest, "rb") as fh:
                for chunk in iter(lambda: fh.read(CHUNK), b""):
                    h.update(chunk)
            actual = h.hexdigest()
            # The key claims a digest; this recomputes it locally rather than
            # trusting the store. A mismatch here means corruption in transit
            # or a blob written under the wrong key -- either way, not usable.
            if actual != entry["sha256"]:
                raise RuntimeError(f"digest mismatch: key says {entry['sha256'][:16]}, "
                                   f"bytes hash to {actual[:16]}")
            with open(dest + ".sha256", "w", encoding="utf-8") as fh:
                fh.write(f"{actual}  {name}\n")
            if os.path.exists(dest + ".FAIL"):
                os.remove(dest + ".FAIL")
            record.update(status="retrieved", bytes=os.path.getsize(dest), sha256=actual)
            ok += 1
            print(f"  ok    {name}  {record['bytes']:,} B  {actual[:16]}")
        except Exception as exc:              # noqa: BLE001 - recorded, not swallowed
            record["reason"] = str(exc)[:300]
            if os.path.exists(dest):
                os.remove(dest)
            with open(dest + ".FAIL", "w", encoding="utf-8") as fh:
                fh.write(f"FAIL {name}\n")
            print(f"  FAIL  {name}: {record['reason']}", file=sys.stderr)
        attempts.append(record)

    provenance = {
        "schema": PROVENANCE_SCHEMA,
        "generated_at": now(),
        "generator": "tools/s3_source_store.py pull",
        "task_id": args.task_id, "goal_id": args.goal_id,
        "policy_note": manifest.get("note"),
        "origin": {"kind": "s3_source_store", "bucket": args.bucket,
                   "package_id": args.package, "manifest_key": manifest_key},
        "attempts": attempts,
    }
    with open(os.path.join(package_dir, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
        fh.write("\n")
    print(f"\n{ok}/{len(manifest['files'])} pulled into inputs/{args.package}/")
    print("next: python3 tools/build_source_index.py   # index + verify hashes")
    return 0 if ok else 1


def cmd_verify(args) -> int:
    s3 = client(args.region, args.profile, args.endpoint_url)
    manifest_key = f"{PACKAGE_PREFIX}/{args.package}/manifest.json"
    manifest = json.loads(s3.get_object(Bucket=args.bucket, Key=manifest_key)["Body"].read())
    bad = []
    for entry in manifest["files"]:
        if not object_exists(s3, args.bucket, entry["blob_key"]):
            bad.append((entry["logical_name"], "blob missing"))
            continue
        actual = digest_object(s3, args.bucket, entry["blob_key"])
        if actual != entry["sha256"]:
            bad.append((entry["logical_name"], f"digest {actual[:16]} != {entry['sha256'][:16]}"))
    for name, why in bad:
        print(f"  FAIL  {name}: {why}", file=sys.stderr)
    print(f"{len(manifest['files']) - len(bad)}/{len(manifest['files'])} verified")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bucket", default=BUCKET)
    ap.add_argument("--region", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--endpoint-url", default=None, help="for S3-compatible stores")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="list a prefix; write nothing")
    p.add_argument("--prefix", default="incoming/")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("adopt", help="hash a prefix into blobs/ and write a manifest")
    p.add_argument("--prefix", default="incoming/")
    p.add_argument("--package", required=True)
    p.add_argument("--replace-manifest", action="store_true",
                   help="overwrite an existing manifest; only to repair a failed run")
    p.set_defaults(func=cmd_adopt)

    p = sub.add_parser("pull", help="materialise a package into inputs/")
    p.add_argument("--package", required=True)
    p.add_argument("--task-id", default=None)
    p.add_argument("--goal-id", default=None)
    p.set_defaults(func=cmd_pull)

    p = sub.add_parser("verify", help="re-hash blobs referenced by a manifest")
    p.add_argument("--package", required=True)
    p.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
