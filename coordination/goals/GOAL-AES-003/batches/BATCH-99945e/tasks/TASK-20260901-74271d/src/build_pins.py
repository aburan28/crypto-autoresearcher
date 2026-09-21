#!/usr/bin/env python3
# build_pins.py -- TASK-20260901-74271d RUN 1 orchestrator (build + pins).
#
# Builds the three task-local binaries and runs the convention-drift /
# lineage pin block:
#   cc -O2 -pthread -o src/rbijarm046 src/rbijarm046.c      (J4 worker, new)
#   cc -O2 -pthread -o src/affarm046 src/affarm046.c        (byte-identical producer copy, J3)
#   cc -O2 -pthread -o src/rc8probe_feistel src/rc8probe_feistel.c  (byte-identical BATCH-014 copy, GUARD)
#   src/affarm046 pin 46060901          (FIPS-197 C.1 KAT + BATCH-003 anchors; lineage control)
#   src/rbijarm046 pin 46060901         (same KATs on the derived file; pin mode uses the AES table)
#   src/affarm046 pinidentity 46060901  (identity table + r=1..10 roundtrips on the lineage copy)
#   src/rbijarm046 pinbij 46064002      (FROZEN J4 table draw, PRE-ARM, pinned seed)
#   python3 src/draw_bij.py 46064002 runs/draw_bij.json  (independent Python draw cross-check)
# Any failure => nonzero exit => HALT (invalid_measurement, never a reading).
import json, subprocess, sys, datetime, os

TASKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(TASKDIR)

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {"cmd": " ".join(cmd), "exit": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr}

steps = []
steps.append(run(["cc", "-O2", "-pthread", "-o", "src/rbijarm046", "src/rbijarm046.c"]))
steps.append(run(["cc", "-O2", "-pthread", "-o", "src/affarm046", "src/affarm046.c"]))
steps.append(run(["cc", "-O2", "-pthread", "-o", "src/rc8probe_feistel", "src/rc8probe_feistel.c"]))

def jstep(cmd):
    r = run(cmd)
    try:
        r["json"] = json.loads(r["stdout"])
    except Exception as e:
        r["json"] = None
        r["parse_error"] = str(e)
    return r

steps.append(jstep(["src/affarm046", "pin", "46060901"]))
steps.append(jstep(["src/rbijarm046", "pin", "46060901"]))
steps.append(jstep(["src/affarm046", "pinidentity", "46060901"]))
steps.append(jstep(["src/rbijarm046", "pinbij", "46064002"]))
steps.append(jstep(["python3", "src/draw_bij.py", "46064002", "runs/draw_bij.json"]))

ok = all(s["exit"] == 0 for s in steps)
pin_aff = (steps[3].get("json") or {}).get("pin_pass")
pin_rbij = (steps[4].get("json") or {}).get("pin_pass")
pinid = (steps[5].get("json") or {}).get("pin_pass")
pinbij = (steps[6].get("json") or {})
# draw_bij.py's stdout is a summary; the full table is in runs/draw_bij.json
try:
    with open("runs/draw_bij.json") as f:
        drawpy = json.load(f)
except Exception:
    drawpy = (steps[7].get("json") or {})
frozen_table_match = (pinbij.get("sbox_table_hex") == drawpy.get("sbox_table_hex")
                      and pinbij.get("pi_table_hex") == drawpy.get("pi_table_hex"))
overall = ok and pin_aff and pin_rbij and pinid and pinbij.get("pinbij_pass") \
    and drawpy.get("nonlinearity_gate_pass") and frozen_table_match

out = {
    "schema": "crypto.autoresearch.build_pins.v1",
    "task_id": "TASK-20260901-74271d",
    "run": "RUN 1 (build + pin block; frozen J4 table drawn PRE-ARM at pinned seed 46064002)",
    "steps": steps,
    "checks": {
        "all_steps_exit_0": ok,
        "affarm046_kat_pin_pass": pin_aff,
        "rbijarm046_kat_pin_pass": pin_rbij,
        "affarm046_pinidentity_pass": pinid,
        "rbijarm046_pinbij_pass": pinbij.get("pinbij_pass"),
        "draw_bij_nonlinearity_gate_pass": drawpy.get("nonlinearity_gate_pass"),
        "frozen_table_C_vs_python_byte_match": frozen_table_match,
    },
    "frozen_J4_table": {
        "draw_seed": 46064002,
        "pi_table_hex": pinbij.get("pi_table_hex"),
        "sbox_affine_over_gf2": pinbij.get("sbox_affine_over_gf2"),
        "sbox_bijective": pinbij.get("sbox_bijective"),
        "discipline": "drawn once at the pinned seed BEFORE any arm; arm re-derives it; analyzer re-verifies byte-identity (PREREGISTRATION.md section 1)",
    },
    "overall_pass": overall,
    "procedure_note": "attempt 1 of RUN 1 correctly halted (exit 5) on frozen_table_C_vs_python_byte_match=false; root cause was an orchestrator bug (comparing the C table against draw_bij.py's stdout summary, which omits the table, instead of runs/draw_bij.json); fixed and rerun within the RUN 1 slot (producer precedent: fatal attempt preserved, repair within slot; rule 5). The draws themselves matched.",
    "on_failure": "HALT: invalid_measurement (build or pin defect), never a reading (rule 5)",
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "parse_attestation": "this file is machine-generated JSON; parsed whole with python3 json.load before task completion (stated in RESULTS.json)",
    "inference": {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
        "model_verified": False,
        "fallback_used": True,
        "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
        "degraded_requirements": [],
        "amendment": "DEC-20260831-0d1eeb",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    },
}
with open("runs/build_pins.json", "w") as f:
    f.write(json.dumps(out, indent=1))
print(json.dumps({"overall_pass": overall, "checks": out["checks"]}, indent=1))
sys.exit(0 if overall else 5)
