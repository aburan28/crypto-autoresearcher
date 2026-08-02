#!/usr/bin/env python3
"""Stage external source documents into an `inputs/` package from S3 or URLs.

Written for the case where the papers live outside the repository -- an S3
bucket, or anywhere reachable by URL -- and need to arrive in the shape the rest
of the harness already understands:

    inputs/<PACKAGE>/
      sources/<name>          the bytes
      sources/<name>.sha256   its hash, in `shasum -a 256` format
      sources/<name>.FAIL     written instead when a fetch fails
      provenance.json         one record per object, retrieved or not

That layout is not arbitrary. It matches `inputs/ECTD-TESKE-20260731/`, so
`tools/build_source_index.py` picks the package up with no extra wiring:
`SOURCES.md` gains a row per file, and CI recomputes every hash from then on.

Two credential paths, because they carry different risk:

  --bucket/--prefix   boto3's default chain. This session's ambient AWS_* vars
                      belong to the *session platform* (the access key begins
                      `prox`, paired with /opt/rclone/rclone-filestore), not to
                      any user account -- so this path needs real credentials
                      supplied deliberately through the environment's config.
                      The tool prints which credential source it resolved
                      before transferring anything.
  --urls-file         one URL per line, presigned or public. No credentials
                      enter the container at all, which makes it the safer
                      default for a one-off ingest. Presigned URLs expire;
                      that is a feature here.

What this tool does NOT do: decide that a fetched file is worth citing. Staging
is not curation. Every file it writes is an input, not evidence, and becomes
knowledge only through /curate-knowledge with a KN-LIT entry.

Usage:
    python3 tools/fetch_s3_sources.py --package INBOX-20260802 \
        --bucket my-bucket --prefix papers/ [--region us-east-1] [--dry-run]
    python3 tools/fetch_s3_sources.py --package INBOX-20260802 \
        --urls-file urls.txt [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
import urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "crypto.autoresearch.source_provenance.v1"
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"

# Keeps a key like `papers/2026/wesolowski.pdf` from colliding with
# `drafts/wesolowski.pdf` once both are flattened into one sources/ directory.
_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_name(key: str) -> str:
    """Flatten an object key to a single filename, preserving distinctness."""
    trimmed = key.strip("/")
    return _SAFE.sub("_", trimmed) or "unnamed"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# Listing
# --------------------------------------------------------------------------

def list_s3(bucket: str, prefix: str, region: str | None,
            endpoint_url: str | None, profile: str | None) -> list[dict]:
    import boto3

    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    creds = session.get_credentials()
    # Printed, not silently used: an operator who sees `prox...` here knows the
    # transfer is about to run as the session platform rather than as them.
    if creds:
        print(f"credentials: source={creds.method} key={creds.access_key[:4]}...",
              file=sys.stderr)
    else:
        print("credentials: NONE resolved -- anonymous request", file=sys.stderr)

    client = session.client("s3", region_name=region, endpoint_url=endpoint_url,
                            verify=CA_BUNDLE if os.path.exists(CA_BUNDLE) else None)
    objects = []
    for page in client.get_paginator("list_objects_v2").paginate(
            Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents") or []:
            if obj["Key"].endswith("/"):      # directory placeholder, not a file
                continue
            objects.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "etag": (obj.get("ETag") or "").strip('"'),
                "url": f"s3://{bucket}/{obj['Key']}",
                "name": safe_name(obj["Key"]),
            })
    return sorted(objects, key=lambda o: o["key"]), client


def list_urls(path: str) -> list[dict]:
    objects = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            parsed = urllib.parse.urlparse(url)
            # Presigned URLs carry a long query string; the basename of the path
            # is the real filename and the signature must not become part of it.
            base = posixpath.basename(parsed.path) or "unnamed"
            objects.append({
                "key": parsed.path.lstrip("/"),
                "size": None,
                "etag": None,
                "url": url,
                "name": safe_name(base),
            })
    return objects


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_s3(client, bucket: str, obj: dict, dest: str) -> dict:
    client.download_file(bucket, obj["key"], dest)
    head = client.head_object(Bucket=bucket, Key=obj["key"])
    last_modified = head.get("LastModified")
    return {
        # VersionId pins WHICH bytes were read when the bucket is versioned. On
        # an unversioned bucket it is absent, and the object can be replaced
        # under the same key with nothing in the record showing it -- which is
        # the reason the sha256 below is recorded rather than trusted to S3.
        "revision_id": head.get("VersionId"),
        "content_type": head.get("ContentType"),
        "last_modified": (last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")
                          if last_modified else None),
    }


def fetch_url(url: str, dest: str) -> dict:
    """Fetch over the session proxy, which re-terminates TLS.

    curl rather than requests: the CA bundle, proxy variables and redirect
    behaviour are already configured for it in this environment.
    """
    cmd = ["curl", "-sS", "-L", "--fail", "-o", dest,
           "-w", "%{http_code} %{content_type}", url]
    if os.path.exists(CA_BUNDLE):
        cmd[1:1] = ["--cacert", CA_BUNDLE]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"curl exit {proc.returncode}: {proc.stderr.strip()[:200]}")
    status, _, ctype = proc.stdout.strip().partition(" ")
    return {"http_status": int(status) if status.isdigit() else None,
            "content_type": ctype or None}


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package", required=True,
                    help="package directory name under inputs/, e.g. INBOX-20260802")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--bucket", help="S3 bucket to list and download from")
    src.add_argument("--urls-file", help="file of URLs, one per line (presigned or public)")
    ap.add_argument("--prefix", default="", help="key prefix within the bucket")
    ap.add_argument("--region", default=None)
    ap.add_argument("--endpoint-url", default=None, help="for S3-compatible stores")
    ap.add_argument("--profile", default=None, help="named AWS profile")
    ap.add_argument("--task-id", default=None, help="TASK-* id to record as the fetcher")
    ap.add_argument("--goal-id", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be fetched; write nothing")
    args = ap.parse_args()

    package_dir = os.path.join(REPO, "inputs", args.package)
    sources_dir = os.path.join(package_dir, "sources")

    client = None
    if args.bucket:
        objects, client = list_s3(args.bucket, args.prefix, args.region,
                                  args.endpoint_url, args.profile)
    else:
        objects = list_urls(args.urls_file)

    if not objects:
        print("no objects matched; nothing to do", file=sys.stderr)
        return 1

    print(f"{len(objects)} object(s) to stage into inputs/{args.package}/sources/")
    if args.dry_run:
        for obj in objects:
            size = f"{obj['size']:,} B" if obj["size"] is not None else "size unknown"
            print(f"  {obj['url']}  ->  {obj['name']}  ({size})")
        print("\ndry run: nothing written")
        return 0

    os.makedirs(sources_dir, exist_ok=True)
    attempts, retrieved = [], 0
    for obj in objects:
        dest = os.path.join(sources_dir, obj["name"])
        record = {
            "source_id": obj["name"],
            "url": obj["url"] if not args.urls_file else _redact(obj["url"]),
            "purpose": "external source document staged for curation",
            "retrieved_at": now(),
            "status": "unretrieved",
            "bytes": None,
            "sha256": None,
            "vendored_path": os.path.relpath(dest, REPO),
            "reason": None,
        }
        try:
            extra = (fetch_s3(client, args.bucket, obj, dest) if args.bucket
                     else fetch_url(obj["url"], dest))
            record.update(extra)
            record["bytes"] = os.path.getsize(dest)
            record["sha256"] = sha256_file(dest)
            record["status"] = "retrieved"
            # Same sidecar format `shasum -a 256` writes, so the two packages
            # this repo already carries and this one verify identically.
            with open(dest + ".sha256", "w", encoding="utf-8") as fh:
                fh.write(f"{record['sha256']}  {obj['name']}\n")
            if os.path.exists(dest + ".FAIL"):
                os.remove(dest + ".FAIL")
            retrieved += 1
            print(f"  ok    {obj['name']}  {record['bytes']:,} B  {record['sha256'][:16]}")
        except Exception as exc:                  # noqa: BLE001 - recorded, not swallowed
            record["reason"] = str(exc)[:300]
            if os.path.exists(dest):
                os.remove(dest)
            # A failure marker is provenance: it says the source was sought.
            with open(dest + ".FAIL", "w", encoding="utf-8") as fh:
                fh.write(f"FAIL {obj['name']}\n")
            print(f"  FAIL  {obj['name']}: {record['reason']}", file=sys.stderr)
        attempts.append(record)

    provenance = {
        "schema": SCHEMA,
        "task_id": args.task_id,
        "goal_id": args.goal_id,
        "generated_at": now(),
        "generator": "tools/fetch_s3_sources.py",
        "policy_note": (
            "Staged from an external object store. These bytes are INPUTS, not "
            "results: nothing here is evidence for or against any hypothesis "
            "until a KN-LIT entry and a ledger record say so."
        ),
        "origin": ({"kind": "s3", "bucket": args.bucket, "prefix": args.prefix,
                    "region": args.region, "endpoint_url": args.endpoint_url}
                   if args.bucket else
                   {"kind": "urls", "urls_file": args.urls_file,
                    "note": "presigned query strings redacted from this record"}),
        "attempts": attempts,
    }
    with open(os.path.join(package_dir, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
        fh.write("\n")

    print(f"\n{retrieved}/{len(objects)} retrieved into inputs/{args.package}/")
    print("next: python3 tools/build_source_index.py   # index + verify hashes")
    return 0 if retrieved else 1


def _redact(url: str) -> str:
    """Drop a presigned signature before it reaches a committed record."""
    parsed = urllib.parse.urlparse(url)
    if not parsed.query:
        return url
    kept = [(k, v) for k, v in urllib.parse.parse_qsl(parsed.query)
            if not k.lower().startswith(("x-amz-", "signature", "sig", "token"))]
    query = urllib.parse.urlencode(kept)
    return urllib.parse.urlunparse(parsed._replace(query=query or ""))


if __name__ == "__main__":
    raise SystemExit(main())
