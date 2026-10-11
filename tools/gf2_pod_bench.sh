#!/bin/bash
# Runs on a RunPod GPU pod (see tools/gf2_runpod.py run): fetch this repo's
# branch $REF (sparse: src, tools, tests), run the GPU correctness tests and the
# CPU-vs-GPU benchmark, and serve /workspace/out on port 8000 for the driver.
set -uo pipefail
REF=${REF:-main}
REPO=${REPO:-https://github.com/aburan28/crypto-autoresearcher.git}
mkdir -p /workspace/out
cd /workspace/out && (python3 -m http.server 8000 >/dev/null 2>&1 &)
{
  set -x
  nvidia-smi || true
  cd /workspace
  rm -rf repo
  git clone --depth 1 --filter=blob:none --sparse --branch "$REF" "$REPO" repo
  cd repo && git sparse-checkout set src tools tests
  git log -1 --format='%H %s'
  python3 -m pip install -q numpy cupy-cuda12x pytest
  python3 -m pytest -q tests/test_gf2_gpu_tail.py tests/test_gf2_rankprofile.py -k "gpu or cupy"
  echo "pytest_exit=$?" > /workspace/out/pytest.txt
  python3 tools/gf2_bench_gpu.py --reps "${REPS:-3}" --out /workspace/out/result.json
} > /workspace/out/log.txt 2>&1
echo done > /workspace/out/done
sleep infinity
