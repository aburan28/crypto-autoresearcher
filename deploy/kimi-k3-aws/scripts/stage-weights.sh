#!/usr/bin/env bash
# Stage ~1.5 TB of Kimi-K3 MXFP4 weights into S3 for FSx for Lustre to serve.
#
#   ./stage-weights.sh s3://my-bucket/models/Kimi-K3 [local-staging-dir]
#
# Run this ONCE from a staging host with fast egress (not from a GPU node -- you do
# not want a p6-b200 sitting idle at $/hour while 1.5 TB downloads). An m7i.8xlarge
# with a large gp3 volume is plenty.
#
# The point of routing through S3 + FSx rather than pulling to each node: every GPU
# node reads the same copy. Pulling 1.5 TB per node from Hugging Face is both slow
# and a good way to get rate-limited mid-deploy.
set -euo pipefail

S3_URI="${1:?usage: stage-weights.sh s3://bucket/prefix [local-dir]}"
LOCAL_DIR="${2:-/mnt/staging/Kimi-K3}"
REPO="moonshotai/Kimi-K3"

command -v s5cmd >/dev/null || {
    echo "s5cmd not found. Install: https://github.com/peak/s5cmd/releases" >&2
    exit 1
}
python3 -c 'import huggingface_hub' 2>/dev/null || pip install -q "huggingface_hub[hf_transfer]"

# hf_transfer uses parallel range requests; without it this download is single-stream
# and takes hours instead of tens of minutes.
export HF_HUB_ENABLE_HF_TRANSFER=1

mkdir -p "${LOCAL_DIR}"
AVAIL_GB=$(df -BG --output=avail "${LOCAL_DIR}" | tail -1 | tr -dc '0-9')
if [ "${AVAIL_GB}" -lt 1800 ]; then
    echo "Only ${AVAIL_GB} GB free at ${LOCAL_DIR}; need ~1800 GB for K3 + slack." >&2
    exit 1
fi

echo "==> Downloading ${REPO} to ${LOCAL_DIR} (~1.5 TB, this takes a while)"
huggingface-cli download "${REPO}" \
    --local-dir "${LOCAL_DIR}" \
    --max-workers 16

echo "==> Sanity-checking the checkpoint"
for required in config.json tokenizer_config.json; do
    [ -f "${LOCAL_DIR}/${required}" ] || { echo "missing ${required}" >&2; exit 1; }
done
SHARDS=$(find "${LOCAL_DIR}" -name '*.safetensors' | wc -l)
BYTES=$(du -sb "${LOCAL_DIR}" | cut -f1)
echo "    ${SHARDS} safetensors shards, $(( BYTES / 1024**3 )) GiB total"
[ "${SHARDS}" -gt 0 ] || { echo "no safetensors shards found" >&2; exit 1; }

echo "==> Recording architecture facts for sizing.py"
python3 - "${LOCAL_DIR}/config.json" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
interesting = [k for k in cfg if any(
    t in k.lower() for t in ("layer", "expert", "kv", "rope", "head", "hidden", "kda", "linear")
)]
print("    config.json keys relevant to sizing:")
for k in sorted(interesting):
    print(f"      {k} = {cfg[k]}")
print("    -> update KEY_ALIASES/PLACEHOLDER in sizing.py from these, then re-run")
print("       sizing.py WITHOUT --assume to get measured rather than estimated numbers.")
PY

echo "==> Uploading to ${S3_URI}"
s5cmd --numworkers 64 cp "${LOCAL_DIR}/*" "${S3_URI}/"

cat <<EOF

==> Done. Next: create the FSx for Lustre filesystem with an S3 data repository
    association pointing at ${S3_URI}, and enable GPUDirect Storage so tensors load
    straight into HBM instead of bouncing through host memory.

    Then bind it with a PersistentVolumeClaim named 'fsx-models' (the name the
    LWS manifests mount).
EOF
