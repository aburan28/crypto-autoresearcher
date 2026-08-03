#!/bin/sh
# Mint presigned URLs for objects in the S3 source store.
#
# RUN THIS ON A MACHINE THAT HAS YOUR AWS CREDENTIALS -- your laptop, not a
# Claude Code session container. It reads the bucket with your AWS CLI and
# writes a list of time-limited URLs that a session can fetch without ever
# holding a credential.
#
#   ./tools/presign_sources.sh                       # whole bucket, 12h expiry
#   ./tools/presign_sources.sh incoming/             # one prefix
#   ./tools/presign_sources.sh incoming/ 3600        # and a shorter expiry
#
# Then hand the printed file to the session, which consumes it directly:
#
#   python3 tools/fetch_s3_sources.py --package INBOX-$(date +%Y%m%d) \
#       --urls-file urls.txt --dry-run
#
# Why presigned URLs rather than putting your keys in the container: the grant
# is scoped to exactly these objects, it is read-only, and it expires on its
# own. A long-lived access key in an ephemeral cloud container is none of those
# things.
#
# The output file contains working signed credentials for the objects listed.
# It is written outside the repository and must never be committed -- anyone
# holding it can read those objects until it expires.

set -eu

BUCKET="${BUCKET:-crypto-autoresearcher}"
PREFIX="${1:-}"
EXPIRES="${2:-43200}"                    # 12 hours; SigV4 caps at 604800 (7 days)
OUT="${OUT:-${TMPDIR:-/tmp}/presigned-sources-$(date +%Y%m%d-%H%M%S).txt}"

if ! command -v aws >/dev/null 2>&1; then
    echo "error: aws CLI not found. This script runs on YOUR machine, not in a" >&2
    echo "       session container. Install it or use the S3 console instead." >&2
    exit 1
fi

if [ "$EXPIRES" -gt 604800 ]; then
    echo "error: --expires-in caps at 604800 seconds (7 days) for SigV4." >&2
    exit 1
fi

echo "bucket:  s3://$BUCKET/$PREFIX" >&2
echo "identity:" >&2
aws sts get-caller-identity --output text >&2 || {
    echo "error: no usable AWS credentials. Run 'aws configure' or set AWS_PROFILE." >&2
    exit 1
}

# --output text with a flat query gives one key per line and, unlike the
# default table output, does not wrap or truncate long keys.
KEYS=$(aws s3api list-objects-v2 --bucket "$BUCKET" --prefix "$PREFIX" \
        --query 'Contents[?Size>`0`].Key' --output text | tr '\t' '\n')

if [ -z "$KEYS" ]; then
    echo "no objects under s3://$BUCKET/$PREFIX" >&2
    exit 1
fi

: > "$OUT"
COUNT=0
# Read from a here-doc rather than a pipe so the loop runs in this shell and
# COUNT survives it; keys containing spaces stay intact because IFS is unset
# per-read and the whole line is one key.
while IFS= read -r KEY; do
    [ -n "$KEY" ] || continue
    URL=$(aws s3 presign "s3://$BUCKET/$KEY" --expires-in "$EXPIRES")
    printf '%s\n' "$URL" >> "$OUT"
    COUNT=$((COUNT + 1))
    printf '  %s\n' "$KEY" >&2
done <<EOF
$KEYS
EOF

echo >&2
echo "$COUNT presigned URL(s) -> $OUT" >&2
echo "expires in $EXPIRES seconds ($((EXPIRES / 3600))h)" >&2
echo >&2
echo "This file grants read access to those objects until it expires." >&2
echo "Do not commit it. Paste its contents to the session, or upload it there." >&2
printf '%s\n' "$OUT"
