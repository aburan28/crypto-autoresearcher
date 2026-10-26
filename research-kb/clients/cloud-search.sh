#!/bin/sh
# Dependency-free fallback for managed cloud sessions without custom MCP support.
set -eu
: "${RESEARCH_KB_URL:?set the HTTPS service URL}"
: "${RESEARCH_KB_TOKEN:?configure a per-client secret in the cloud runtime}"
case "$RESEARCH_KB_URL" in
  https://*) ;;
  *) echo 'RESEARCH_KB_URL must use HTTPS' >&2; exit 2 ;;
esac
test "$#" -gt 0 || { echo 'usage: cloud-search.sh query words' >&2; exit 2; }
curl --fail-with-body --silent --show-error --max-time 30 --get \
  --header "Authorization: Bearer $RESEARCH_KB_TOKEN" \
  --data-urlencode "q=$*" \
  "${RESEARCH_KB_URL%/}/v1/search"
