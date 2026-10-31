"""Write real worker artifacts only to its assigned per-Job/Pod S3 prefix."""
from __future__ import annotations
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import gzip
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlsplit


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


@contextmanager
def stored_payload(path):
    """Keep logical bytes lossless; stored artifacts >=1 MiB are gzip encoded."""
    path = Path(path)
    logical_sha = sha_file(path)
    with path.open("rb") as source:
        if path.stat().st_size < 1048576:
            yield source, {"bytes": path.stat().st_size, "sha256": logical_sha,
                           "stored_bytes": path.stat().st_size, "stored_sha256": logical_sha,
                           "content_encoding": "identity", "suffix": ""}
        else:
            with tempfile.TemporaryFile() as encoded:
                with gzip.GzipFile(filename="", fileobj=encoded, mode="wb", mtime=0) as gz:
                    shutil.copyfileobj(source, gz)
                size = encoded.tell()
                encoded.seek(0)
                digest = hashlib.sha256()
                for block in iter(lambda: encoded.read(1048576), b""):
                    digest.update(block)
                encoded.seek(0)
                yield encoded, {"bytes": path.stat().st_size, "sha256": logical_sha,
                                "stored_bytes": size, "stored_sha256": digest.hexdigest(),
                                "content_encoding": "gzip", "suffix": ".gz"}


def upload_tree(root: Path) -> dict:
    root = Path(root)
    uri = os.environ.get("ISOLAB_RESULTS_URI", "")
    parsed = urlsplit(uri)
    prefix = parsed.path.lstrip("/")
    expected = "runs/" + os.environ.get("ISOLAB_JOB_ID", "") + "/" + os.environ.get("POD_UID", "") + "/"
    record = {"schema": "classical.ecdlp.endpoint-reuse.upload-receipt.v1",
              "recorded_at": datetime.now(timezone.utc).isoformat(),
              "planned_results_uri": uri, "payload_upload_complete": False, "objects": []}
    try:
        if parsed.scheme != "s3" or not parsed.netloc or parsed.query or parsed.fragment or prefix != expected:
            raise ValueError("results URI must be the exact assigned runs/Job/Pod prefix")
        import boto3
        client = boto3.client("s3")
        files = sorted(p for p in root.rglob("*") if p.is_file() and p.name != "upload-status.json")
        for path in files:
            relative = path.relative_to(root).as_posix()
            with stored_payload(path) as (stream, stored):
                stored_name = relative + stored["suffix"]
                request = {"Bucket": parsed.netloc, "Key": prefix + stored_name, "Body": stream,
                           "ContentLength": stored["stored_bytes"],
                           "ChecksumSHA256": base64.b64encode(bytes.fromhex(stored["stored_sha256"])).decode(),
                           "Metadata": {"logical-sha256": stored["sha256"], "stored-sha256": stored["stored_sha256"]}}
                if stored["content_encoding"] == "gzip":
                    request["ContentEncoding"] = "gzip"
                reply = client.put_object(**request)
            record["objects"].append({"path": relative, **stored,
                                      "uri": "s3://" + parsed.netloc + "/" + prefix + stored_name,
                                      "version_id": reply.get("VersionId"),
                                      "returned_checksum_sha256": reply.get("ChecksumSHA256"),
                                      "put_object_returned": True})
        record["payload_upload_complete"] = True
    except Exception as error:
        # No credentials, headers or traceback are serialized.
        record["error_type"] = type(error).__name__
        record["error"] = str(error) if isinstance(error, ValueError) else "Storage SDK failed; no credentials or request details serialized."
    status = root / "upload-status.json"
    status.write_text(json.dumps(record, indent=2) + "\n")
    receipt_put_returned = False
    if "client" in locals():
        try:
            with stored_payload(status) as (stream, stored):
                request = {"Bucket": parsed.netloc, "Key": prefix + status.name + stored["suffix"], "Body": stream,
                           "ContentLength": stored["stored_bytes"],
                           "ChecksumSHA256": base64.b64encode(bytes.fromhex(stored["stored_sha256"])).decode(),
                           "Metadata": {"logical-sha256": stored["sha256"], "stored-sha256": stored["stored_sha256"]}}
                if stored["content_encoding"] == "gzip":
                    request["ContentEncoding"] = "gzip"
                client.put_object(**request)
                receipt_put_returned = True
        except Exception as error:
            record.update({"receipt_upload_error_type": type(error).__name__,
                           "receipt_upload_error": "Storage SDK failed; no credentials or request details serialized."})
            status.write_text(json.dumps(record, indent=2) + "\n")
    # A record cannot certify its own transport. This returned flag controls the
    # container exit status; the external collector must GET/version/hash-check it.
    return {**record, "receipt_put_returned": receipt_put_returned}
