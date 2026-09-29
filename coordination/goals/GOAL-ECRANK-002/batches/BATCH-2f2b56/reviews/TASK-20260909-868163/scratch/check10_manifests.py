#!/usr/bin/env python3
"""J2 check 10: verify all seven v2 manifests carry (a) the nested run schema,
(b) the independence disclosure, (c) the recorded provenance
(fallback_used true, resolved_model_id vllm/qwen3.8-27b, model_verified false).
Also record the source_sha256_v2 run_v2.py hash per manifest (integrity observation).
"""
import yaml

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
RUNS = [
    "RUN-ECRANK-73275e-R9-known-false-v2",
    "RUN-ECRANK-73275e-R10-planted-elliptic-n6",
    "RUN-ECRANK-73275e-R11-planted-n8",
    "RUN-ECRANK-73275e-R12-construct-n6-replication",
    "RUN-ECRANK-73275e-R13-construct-n6-replay",
    "RUN-ECRANK-73275e-R14-construct-n8-rescoped",
    "RUN-ECRANK-73275e-R15-null-v2",
]
BASE = f"{ROOT}/experiments/EXP-ECRANK-73275e/runs"

# RUN_REQUIRED_TOP per spec SR-3: id, experiment_id, status, code, environment,
# inputs, results, stdout, stderr, timestamps, resources, validity, model provenance
REQUIRED = ["id", "experiment_id", "status", "code", "environment", "inputs",
            "result", "timing", "resources", "inference", "validity",
            "stdout", "stderr"]

for run in RUNS:
    p = f"{BASE}/{run}/manifest.yaml"
    d = yaml.safe_load(open(p))
    top = list(d.keys())
    nested = (top == ["run"])
    r = d.get("run", {})
    missing = [k for k in REQUIRED if k not in r]
    inf = r.get("inference", {})
    fb = inf.get("fallback_used")
    rmid = inf.get("resolved_model_id")
    mv = inf.get("model_verified")
    disc = r.get("independence_disclosure")
    disc_ok = isinstance(disc, str) and "Same-machine replication" in disc
    sv2 = r.get("code", {}).get("source_sha256_v2", {})
    runv2 = sv2.get("run_v2.py", "N/A")
    print(f"== {run} ==")
    print(f"  nested_run_schema (top==['run']): {nested}  top_keys={top}")
    print(f"  missing_required_fields: {missing if missing else 'none'}")
    print(f"  independence_disclosure present: {disc_ok}")
    print(f"  provenance: fallback_used={fb} resolved_model_id={rmid} model_verified={mv}")
    print(f"  source_sha256_v2 run_v2.py: {runv2[:16]}")
    print()
