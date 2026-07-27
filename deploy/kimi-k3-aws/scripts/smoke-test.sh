#!/usr/bin/env bash
# Smoke-test a deployed Kimi-K3 endpoint, then measure it honestly.
#
#   ./smoke-test.sh [endpoint]     # default: in-cluster service
set -euo pipefail

ENDPOINT="${1:-http://kimi-k3.default.svc.cluster.local}"
MODEL="kimi-k3"

echo "==> /health"
curl -fsS "${ENDPOINT}/health" && echo "    ok"

echo "==> /v1/models"
curl -fsS "${ENDPOINT}/v1/models" | python3 -m json.tool | head -20

echo
echo "==> Short completion (checks the decode path end to end)"
curl -fsS "${ENDPOINT}/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{
      \"model\": \"${MODEL}\",
      \"messages\": [{\"role\": \"user\", \"content\": \"Reply with exactly: deployment ok\"}],
      \"max_tokens\": 32,
      \"temperature\": 0
    }" | python3 -m json.tool

echo
echo "==> Long-context probe (exercises the 24 MLA layers' KV growth)"
# Builds a ~200k-token prompt. The point is to confirm the KV budget computed by
# sizing.py survives contact with a real long request before you trust a 1M claim.
python3 - "${ENDPOINT}" "${MODEL}" <<'PY'
import json, sys, time, urllib.request

endpoint, model = sys.argv[1], sys.argv[2]
filler = "The quick brown fox jumps over the lazy dog. " * 30000  # ~200k tokens
payload = {
    "model": model,
    "messages": [
        {"role": "user",
         "content": filler + "\n\nHow many times did the phrase about the fox appear? "
                             "Answer with a number only."}
    ],
    "max_tokens": 16,
    "temperature": 0,
}
req = urllib.request.Request(
    f"{endpoint}/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
)
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=1800) as resp:
        body = json.load(resp)
    dt = time.time() - t0
    usage = body.get("usage", {})
    print(f"    prompt_tokens={usage.get('prompt_tokens')} "
          f"completion_tokens={usage.get('completion_tokens')}")
    print(f"    wall={dt:.1f}s  answer={body['choices'][0]['message']['content']!r}")
except Exception as exc:
    print(f"    long-context probe FAILED: {exc}")
    print("    Re-run sizing.py against the real config.json -- the KV budget is "
          "the usual culprit.")
    sys.exit(1)
PY

cat <<'EOF'

==> For real numbers, use genai-perf or vllm bench rather than this script:

    vllm bench serve \
      --backend openai-chat --model kimi-k3 \
      --base-url ${ENDPOINT} \
      --dataset-name random --random-input-len 32000 --random-output-len 1000 \
      --max-concurrency 32 --num-prompts 200

    Report TTFT and inter-token latency separately -- with PD disaggregation they
    are governed by different node groups and a single blended number hides which
    half needs more capacity.
EOF
