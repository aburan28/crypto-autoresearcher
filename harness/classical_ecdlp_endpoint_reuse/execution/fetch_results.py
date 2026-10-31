#!/usr/bin/env python3
"""Read/version/hash-check a real worker upload receipt and its actual objects."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import urlsplit


def s3_parts(uri):
    value = urlsplit(uri)
    if value.scheme != "s3" or not value.netloc or value.query or value.fragment or not value.path.lstrip("/").startswith("runs/"):
        raise ValueError("a real per-job S3 results URI is required")
    return value.netloc, value.path.lstrip("/")


def destination(root, relative):
    value = PurePosixPath(relative)
    if not value.parts or value.is_absolute() or ".." in value.parts or str(value) != relative:
        raise ValueError("unsafe producer artifact path")
    path = root / value
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("producer path escapes fresh result directory")
    return path


def download(client, uri, version, output):
    bucket, key = s3_parts(uri)
    if not version or version == "null":
        raise ValueError("an actual object VersionId is required")
    response = client.get_object(Bucket=bucket, Key=key, VersionId=version)
    if response.get("VersionId") != version:
        raise ValueError("server returned a different result object version")
    digest, length = hashlib.sha256(), 0
    with Path(output).open("xb") as stream:
        while True:
            block = response["Body"].read(1048576)
            if not block:
                break
            length += len(block)
            if length > response["ContentLength"]:
                raise ValueError("result stream exceeds the server-declared object length")
            digest.update(block)
            stream.write(block)
    if length != response["ContentLength"]:
        raise ValueError("result stream is incomplete")
    return {"bytes": length, "sha256": digest.hexdigest(), "uri": uri, "version_id": version}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--receipt-uri", required=True)
    p.add_argument("--receipt-version-id")
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    audit_path = a.out.with_name(a.out.name + ".fetch.json")
    if a.out.exists() or audit_path.exists():
        p.error("fresh raw-output and collector-receipt paths required")
    import boto3
    client = boto3.client("s3")
    bucket, key = s3_parts(a.receipt_uri)
    if not key.endswith(("/upload-status.json", "/upload-status.json.gz")):
        p.error("the actual worker upload-status object is required")
    version = a.receipt_version_id
    if not version:
        version = client.head_object(Bucket=bucket, Key=key).get("VersionId")
    a.out.mkdir(parents=True)
    checks = []
    with tempfile.TemporaryDirectory() as scratch:
        receipt_stored = Path(scratch) / "receipt"
        receipt_check = download(client, a.receipt_uri, version, receipt_stored)
        receipt_raw = gzip.decompress(receipt_stored.read_bytes()) if key.endswith(".gz") else receipt_stored.read_bytes()
        receipt = json.loads(receipt_raw)
        if receipt.get("schema") != "classical.ecdlp.endpoint-reuse.upload-receipt.v1":
            raise ValueError("wrong producer receipt schema")
        expected_prefix = key.rsplit("/", 1)[0] + "/"
        seen = set()
        for ordinal, record in enumerate(receipt["objects"]):
            relative = record["path"]
            if relative in seen:
                raise ValueError("duplicate producer artifact path")
            seen.add(relative)
            got_bucket, got_key = s3_parts(record["uri"])
            if got_bucket != bucket or got_key != expected_prefix + relative + record.get("suffix", ""):
                raise ValueError("a producer receipt points outside its own exact Job/Pod prefix")
            transport = Path(scratch) / f"object-{ordinal}"
            check = download(client, record["uri"], record["version_id"], transport)
            if check["bytes"] != record["stored_bytes"] or check["sha256"] != record["stored_sha256"]:
                raise ValueError("stored artifact bytes differ from the producer receipt")
            dest = destination(a.out, relative)
            dest.parent.mkdir(parents=True, exist_ok=True)
            digest, length = hashlib.sha256(), 0
            opener = gzip.open if record["content_encoding"] == "gzip" else open
            if record["content_encoding"] not in ("gzip", "identity"):
                raise ValueError("unknown producer transport encoding")
            with opener(transport, "rb") as source, dest.open("xb") as target:
                while True:
                    block = source.read(1048576)
                    if not block:
                        break
                    length += len(block)
                    if length > record["bytes"]:
                        raise ValueError("decoded artifact exceeds its declared logical bytes")
                    digest.update(block)
                    target.write(block)
            if length != record["bytes"] or digest.hexdigest() != record["sha256"]:
                raise ValueError("logical artifact differs from the producer receipt")
            checks.append({"path": relative, "bytes": length, "sha256": digest.hexdigest(),
                           "stored_object": check})
        (a.out / "upload-status.json").write_bytes(receipt_raw)
    audit = {"schema": "classical.ecdlp.endpoint-reuse.fetch-receipt.v1",
             "source_receipt": receipt_check, "source_receipt_logical_sha256": hashlib.sha256(receipt_raw).hexdigest(),
             "payload_upload_complete": receipt["payload_upload_complete"], "files": checks,
             "native_equations_verified": False, "isolation_attested": False, "scientific_review": False}
    audit_path.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({"collector_receipt": str(audit_path), "files": len(checks),
                      "payload_upload_complete": receipt["payload_upload_complete"]}))
    raise SystemExit(0 if receipt["payload_upload_complete"] else 1)


if __name__ == "__main__":
    main()
