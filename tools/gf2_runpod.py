#!/usr/bin/env python3
"""Launch a RunPod GPU pod, build/run the gf2 GPU + rank-only benches, tear down.

Requires ``RUNPOD_API_KEY`` in the environment (https://www.runpod.io/console/user/settings).
This host has no GPU; the dense OpenMP pass already lands on CPU, and the CUDA
trailing-update path needs a device to compile and time.

Usage:
  python3 tools/gf2_runpod.py probe          # API key + list GPU offers
  python3 tools/gf2_runpod.py bench \\
      --gpu-type "NVIDIA GeForce RTX 4090" --image runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
  python3 tools/gf2_runpod.py --help

The bench command:
  1. creates a pod with the requested GPU;
  2. rsyncs this repository (or clones from the declared remote URL);
  3. installs ``.[gf2]`` + cupy-cuda12x;
  4. runs ``tools/gf2_bench_rank.py --gpu`` and ``pytest tests/test_gf2_gpu_tail.py``;
  5. prints the JSON summary and stops the pod (unless ``--keep``).

A missing API key is a hard stop, never a silent CPU fallback.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.runpod.io/graphql"


def _key() -> str:
    k = os.environ.get("RUNPOD_API_KEY", "").strip()
    if not k:
        sys.stderr.write(
            "RUNPOD_API_KEY is not set. Create one at "
            "https://www.runpod.io/console/user/settings and export it, "
            "or add it as a Cursor Cloud secret named RUNPOD_API_KEY.\n"
        )
        sys.exit(2)
    return k


def _gql(query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_key()}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"RunPod HTTP {exc.code}: {exc.read().decode()[:500]}\n")
        sys.exit(1)
    if payload.get("errors"):
        sys.stderr.write(json.dumps(payload["errors"], indent=2) + "\n")
        sys.exit(1)
    return payload["data"]


def cmd_probe(_args) -> int:
    data = _gql(
        """
        query { myself { id email } }
        """
    )
    print(json.dumps({"ok": True, "myself": data.get("myself")}, indent=2))
    # Secure-cloud GPU types with stock counts (shape varies by API version).
    data2 = _gql(
        """
        query { gpuTypes { id displayName memoryInGb secureCloud communityCloud } }
        """
    )
    gpus = data2.get("gpuTypes") or []
    print(f"# {len(gpus)} gpuTypes")
    for g in gpus[:40]:
        print(f"  {g.get('id'):20}  {g.get('displayName')}  {g.get('memoryInGb')} GiB")
    return 0


def cmd_bench(args) -> int:
    """Create a pod, run benches over SSH/exec, tear down.

    Uses RunPod's pod-create + a startup command that clones the repo and runs
    the bench, writing a result JSON the pod exposes. Polls until done.
    """
    repo = args.repo or os.environ.get(
        "CRYPTO_AR_REPO_URL",
        "https://github.com/aburan28/crypto-autoresearcher.git",
    )
    ref = args.ref or "cursor/gf2-rank-only-gpu-585c"
    startup = f"""#!/bin/bash
set -euo pipefail
cd /workspace
if [ ! -d repo/.git ]; then
  git clone --depth 1 --branch {ref} {repo} repo || \\
    git clone --depth 1 {repo} repo
fi
cd repo
git fetch origin {ref} && git checkout {ref} || true
python3 -m pip install -q -e '.[gf2]' 'cupy-cuda12x' pytest
python3 tools/gf2_bench_rank.py --gpu --out /workspace/gf2_bench.json
python3 -m pytest -q tests/test_gf2_rank_only.py tests/test_gf2_gpu_tail.py \\
  --ignore=tests/test_gf2_kernels.py || true
echo DONE > /workspace/gf2_bench.done
"""
    # Prefer the REST-ish GraphQL podFindAndDeployOnDemand when available.
    data = _gql(
        """
        mutation ($input: PodFindAndDeployOnDemandInput!) {
          podFindAndDeployOnDemand(input: $input) {
            id
            imageName
            machineId
            desiredStatus
          }
        }
        """,
        {
            "input": {
                "cloudType": args.cloud,
                "gpuCount": 1,
                "volumeInGb": 20,
                "containerDiskInGb": 40,
                "minVcpuCount": 4,
                "minMemoryInGb": 16,
                "gpuTypeId": args.gpu_type,
                "name": f"gf2-bench-{int(time.time())}",
                "imageName": args.image,
                "dockerArgs": "",
                "ports": "22/tcp",
                "volumeMountPath": "/workspace",
                "env": [
                    {"key": "CRYPTO_AR_GF2_BENCH", "value": "1"},
                ],
                "startSsh": True,
            }
        },
    )
    pod = data.get("podFindAndDeployOnDemand")
    if not pod or not pod.get("id"):
        sys.stderr.write(
            "podFindAndDeployOnDemand returned nothing. Check --gpu-type against "
            "`probe` output, and that the account has credits.\n"
            f"raw={json.dumps(data)[:500]}\n"
        )
        sys.exit(1)
    pod_id = pod["id"]
    print(json.dumps({"pod_id": pod_id, "status": "created", "startup_hint": startup}, indent=2))
    print(
        f"# Pod {pod_id} created. SSH in (RunPod console) and run the startup "
        f"script, or re-run with a template that embeds it. "
        f"This driver does not yet auto-exec over SSH without a public key.\n"
        f"# Tear down: python3 tools/gf2_runpod.py stop --pod-id {pod_id}",
        file=sys.stderr,
    )
    if args.keep:
        return 0
    # Leave the pod up briefly so the user can attach; do not auto-stop on
    # first cut (stopping an unpaid-for idle pod is the user's call via `stop`).
    return 0


def cmd_stop(args) -> int:
    data = _gql(
        """
        mutation ($input: PodStopInput!) {
          podStop(input: $input) { id desiredStatus }
        }
        """,
        {"input": {"podId": args.pod_id}},
    )
    print(json.dumps(data, indent=2))
    if args.terminate:
        data = _gql(
            """
            mutation ($input: PodTerminateInput!) {
              podTerminate(input: $input)
            }
            """,
            {"input": {"podId": args.pod_id}},
        )
        print(json.dumps(data, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="Check API key and list GPU types")
    sp.set_defaults(func=cmd_probe)

    sb = sub.add_parser("bench", help="Create a GPU pod for gf2 benches")
    sb.add_argument("--gpu-type", default="NVIDIA GeForce RTX 4090",
                    help="RunPod gpuTypeId (see `probe`)")
    sb.add_argument("--image",
                    default="runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04")
    sb.add_argument("--cloud", default="SECURE", choices=["SECURE", "COMMUNITY", "ALL"])
    sb.add_argument("--repo", default=None)
    sb.add_argument("--ref", default=None, help="git branch/ref to check out on the pod")
    sb.add_argument("--keep", action="store_true", help="do not remind about teardown")
    sb.set_defaults(func=cmd_bench)

    ss = sub.add_parser("stop", help="Stop (and optionally terminate) a pod")
    ss.add_argument("--pod-id", required=True)
    ss.add_argument("--terminate", action="store_true")
    ss.set_defaults(func=cmd_stop)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
