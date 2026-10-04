#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 (AMD-EXP-GFPN-05ff43-20260923-rung31) -- shared context.

ADDITIVE ONLY (addendum A1-7 (1); DEC-20260923-8b2dbf AA-5 (d)). This module imports the archive-bound
v2 modules in experiments/EXP-GFPN-05ff43/implementation-v2/ READ-ONLY and never writes there:
  * sys.dont_write_bytecode is set BEFORE any v2 import, so no __pycache__ is created under
    implementation-v2/ even if the interpreter was started without -B;
  * the only thing changed in a v2 module is a module-level PATH/ID constant, inside this process
    (redirect_v2 below): v2_common.PLAN_PATH -> trial-plan-v2-a1.json, and v2_common.TASK_ID ->
    the addendum task id, so that no addendum artifact can carry TASK-20260923-cd932c (AA-5 (a)).
    No v2 function is replaced.
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
V2_DIR = os.path.join(EXP_DIR, "implementation-v2")
if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

EXPERIMENT_ID = "EXP-GFPN-05ff43"
PROTOCOL_VERSION = "2-a1"
ADDENDUM_ID = "AMD-EXP-GFPN-05ff43-20260923-rung31"
ADDENDUM_PATH = os.path.join(EXP_DIR, "amendments", "v2_addendum_rung31.yaml")
ADDENDUM_SHA256 = "2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c"
ADDENDUM_APPROVAL = "DEC-20260923-8b2dbf"
V2_AMENDMENT_ID = "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii"
V2_AMENDMENT_PATH = os.path.join(EXP_DIR, "amendments", "v1_to_v2_reanchor_and_arm_iii.yaml")
V2_AMENDMENT_SHA256 = "e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3"
V2_APPROVAL = "DEC-20260923-e788a1"

PLAN_A1_PATH = os.path.join(EXP_DIR, "trial-plan-v2-a1.json")
V2_PLAN_PATH = os.path.join(EXP_DIR, "trial-plan-v2.json")
LADDER_PATH = os.path.join(EXP_DIR, "implementation", "ladder.json")          # v1, frozen, read-only
LADDER_A1_PATH = os.path.join(HERE, "ladder-a1.json")                           # FB-1 only
RUNS_DIR = os.path.join(EXP_DIR, "runs")
ARCHIVES = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives")
RECEIPT_V2_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "snapshot-receipt.json")
RECEIPT_V2_PHASE_B = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "post-run-receipt.json")
RECEIPT_A1_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-4ff597", "snapshot-receipt.json")

V2_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2", "experiments/EXP-GFPN-05ff43/implementation-v2.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2.json"]
A1_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2-a1", "experiments/EXP-GFPN-05ff43/implementation-v2-a1.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json"]

TASK_ID_STAGE_1B = "TASK-20260923-4c64b5"      # development notes only
TASK_ID_RUNS = "TASK-20260923-6c7f55"          # every addendum run manifest (A1-7 (3); AA-5 (a))
FORBIDDEN_TASK_ID = "TASK-20260923-cd932c"     # v2_common.py line 46; never on an addendum artifact

P_RUNG31 = 1073741831
P_FB1 = 16777291
V2_PRIMES = (4111, 262151, 16777291)
V2_GATE_PACKAGES = ("RUN-GFPN-ac4487", "RUN-GFPN-3377f1", "RUN-GFPN-76420e", "RUN-GFPN-b231c1")
MAX_PACKAGES_SHARED = 48                       # DC-7 A-7, shared by v2 + addendum (AA-5 (e))
CAP_BYTES = 10737418240                        # AC-1 (DP-4 guard threshold above 12.0 GB: not lowered)
SHAPES = ("ecgfp5_shaped", "random_2torsion", "random_no2torsion")

# A1-1 target stream (31-bit plan) and A1-9 target stream (FB-1 plan). Recorded in the plan.
TARGET_STREAM_31 = "random.Random('2026092001:v2:targets:1073741831:<shape>')"
TARGET_STREAM_FB1 = "random.Random('2026092001:v2a1:targets:16777291:ecgfp5_shaped_fb1')"
HEALTH_SEED = "2026092001:v2a1:health:1073741831"   # A1-7 (b); AA-3 (a) uses the SAME seed strings at 16777291

OFF_SHAPE_LABEL = "off_shape_non_double_odd"
OFF_SHAPE_KEY = (16777291, "ecgfp5_shaped")        # A1-4: (p', curve_shape) rows read off-shape
OFF_SHAPE_TITLE = "EcGFp5-model curve with b a square, not double-odd; nearby object; no verdict"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def redirect_v2(plan_path=None, ladder_path=None, exp_dir=None, task_id=TASK_ID_RUNS):
    """Point the v2 modules at the addendum plan INSIDE THIS PROCESS (A1-7 (1); AA-5 (c)).
    Only module-level constants are set; no v2 file and no v2 function is changed."""
    import v2_common as C
    C.PLAN_PATH = plan_path or PLAN_A1_PATH
    if ladder_path:
        C.LADDER_PATH = ladder_path
    if exp_dir:
        C.EXP_DIR = exp_dir
    C.TASK_ID = task_id
    return C


def inference_block():
    return {
        "requested_policy": "executor-implementation",
        "resolved_model_id": None,
        "resolved_by": "not recorded by the executor; the dispatching session records the resolved binding",
        "backend": os.environ.get("AUTORESEARCH_BACKEND"),
        "policy_env": os.environ.get("AUTORESEARCH_POLICY"),
        "fallback_used": False,
        "fallback_reason": None,
        "bedrock_used": False,
        "note": "every number in this package comes from deterministic code (msolve, python-flint, PARI, pure Python); no model is in the arithmetic loop",
    }


def receipt_paths(receipt):
    """path_sha256 of a snapshot/post-run receipt as a dict {repo-relative path: sha256}."""
    ps = receipt.get("path_sha256") or {}
    if isinstance(ps, list):
        return {x["path"]: x["sha256"] for x in ps}
    return dict(ps)
