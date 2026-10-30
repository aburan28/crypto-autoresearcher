#!/usr/bin/env python3
"""Presigned S3 access for scripts/checkpoint.sh, standard library only.

  checkpoint_presign.py post <bucket> <region> <key-prefix> <seconds>
      Print an upload token: base64 JSON {url, fields, prefix, expires} for an
      S3 presigned POST policy that lets the holder write (not read, list or
      delete) any key under <key-prefix> until it expires (7 days at most).
  checkpoint_presign.py get <bucket> <region> <key> <seconds>
      Print a presigned GET URL for one object.

Credentials come from the environment (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
optional AWS_SESSION_TOKEN); checkpoint.sh exports them from the AWS profile.
"""
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import urllib.parse

MAX_SECONDS = 7 * 24 * 3600


def signing_key(secret, date, region):
    k = ("AWS4" + secret).encode()
    for part in (date, region, "s3", "aws4_request"):
        k = hmac.new(k, part.encode(), hashlib.sha256).digest()
    return k


def creds():
    try:
        return os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], os.environ.get("AWS_SESSION_TOKEN")
    except KeyError:
        sys.exit("checkpoint_presign: AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY not set")


def presign_post(bucket, region, prefix, seconds):
    access, secret, token = creds()
    now = dt.datetime.now(dt.timezone.utc)
    date, amzdate = now.strftime("%Y%m%d"), now.strftime("%Y%m%dT%H%M%SZ")
    expires = now + dt.timedelta(seconds=seconds)
    credential = f"{access}/{date}/{region}/s3/aws4_request"
    fields = {
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": credential,
        "x-amz-date": amzdate,
    }
    if token:
        fields["x-amz-security-token"] = token
    conditions = [
        {"bucket": bucket},
        ["starts-with", "$key", prefix],
        ["content-length-range", 0, 5 * 1024**3],
    ] + [{k: v} for k, v in fields.items()]
    policy = base64.b64encode(json.dumps({
        "expiration": expires.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "conditions": conditions,
    }).encode()).decode()
    fields["policy"] = policy
    fields["x-amz-signature"] = hmac.new(signing_key(secret, date, region), policy.encode(), hashlib.sha256).hexdigest()
    blob = {
        "url": f"https://{bucket}.s3.{region}.amazonaws.com/",
        "fields": fields,
        "prefix": prefix,
        "expires": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return base64.b64encode(json.dumps(blob, separators=(",", ":")).encode()).decode()


def presign_get(bucket, region, key, seconds):
    access, secret, token = creds()
    now = dt.datetime.now(dt.timezone.utc)
    date, amzdate = now.strftime("%Y%m%d"), now.strftime("%Y%m%dT%H%M%SZ")
    host = f"{bucket}.s3.{region}.amazonaws.com"
    path = "/" + urllib.parse.quote(key, safe="/-_.~")
    q = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": f"{access}/{date}/{region}/s3/aws4_request",
        "X-Amz-Date": amzdate,
        "X-Amz-Expires": str(seconds),
        "X-Amz-SignedHeaders": "host",
    }
    if token:
        q["X-Amz-Security-Token"] = token
    query = "&".join(f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}" for k, v in sorted(q.items()))
    canonical = "\n".join(["GET", path, query, f"host:{host}\n", "host", "UNSIGNED-PAYLOAD"])
    to_sign = "\n".join(["AWS4-HMAC-SHA256", amzdate, f"{date}/{region}/s3/aws4_request",
                         hashlib.sha256(canonical.encode()).hexdigest()])
    sig = hmac.new(signing_key(secret, date, region), to_sign.encode(), hashlib.sha256).hexdigest()
    return f"https://{host}{path}?{query}&X-Amz-Signature={sig}"


def main():
    if len(sys.argv) != 6 or sys.argv[1] not in ("post", "get"):
        sys.exit(__doc__)
    mode, bucket, region, target, seconds = sys.argv[1:]
    seconds = int(seconds)
    if not 0 < seconds <= MAX_SECONDS:
        sys.exit(f"checkpoint_presign: lifetime must be 1..{MAX_SECONDS} seconds (S3 caps SigV4 at 7 days)")
    print((presign_post if mode == "post" else presign_get)(bucket, region, target, seconds))


if __name__ == "__main__":
    main()
