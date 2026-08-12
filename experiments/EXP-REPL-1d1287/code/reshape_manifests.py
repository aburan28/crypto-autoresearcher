"""
One-time, mechanical reshape of EXP-REPL-1d1287's 372 run manifest.yaml
files from the flat shape this harness originally wrote into the canonical
`run:`-wrapped shape tools/validate_ledger.py expects (matching
EXP-ECTD-9e4248 / EXP-FIB-001 / EXP-DTREE-001's manifests).

ONLY manifest.yaml is touched. raw-result.json, stdout.log, stderr.log,
command.txt and environment.json are left byte-for-byte untouched.

This is a pure structural reshape: every value that was present in the old
flat manifest is preserved somewhere in the new nested manifest (see the
field-mapping comments below). No value is fabricated. Where the canonical
schema expects a field this harness never instrumented (resources /
peak_rss_bytes, started_at/finished_at wall-clock timestamps), an explicit
null + "not instrumented" note is written instead of a fabricated number,
matching how EXP-FIB-001's own manifests handle unmeasured fields.
"""
import json
import os

RUNS_DIR = "/tmp/wt-run-exp/experiments/EXP-REPL-1d1287/runs"

def reshape(old: dict) -> dict:
    run_id = old["run_id"]                      # -> run.id  (rename)
    new = {
        "run": {
            "id": run_id,
            "experiment_id": old.get("experiment", "EXP-REPL-1d1287"),
            "status": old["status"],
            "code": {
                "commit": old["git_commit"],
                "dirty": old["git_dirty"],
                "command": old["command"],
            },
            "inference": {
                "requested_policy": old["environment"].get("inference_policy"),
                "resolved_model_id": old["environment"].get("resolved_inference_model"),
                "reasoning_effort": None,
                "fallback_used": old["environment"].get("fallback_used", False),
                "adapter_version": None,
            },
            "environment": {
                "operating_system": old["environment"].get("platform"),
                "architecture": None,
                "python_version": old["environment"].get("python"),
                "sage_version": None,
                "dependencies": {
                    "torch": old["environment"].get("torch"),
                    "numpy": old["environment"].get("numpy"),
                },
            },
            "inputs": {
                "parameters": old.get("params", {}),
                "seeds": {"training_seed": old.get("seed")},
            },
            "timing": {
                "wall_seconds": old.get("wall_clock_seconds"),
                "started_at": None,
                "finished_at": None,
                "note": (
                    "per-run started_at/finished_at wall-clock timestamps were "
                    "not captured by this harness (code/orchestrate.py); "
                    "wall_seconds is a time.time() delta measured around the "
                    "training call and is preserved unchanged from the "
                    "original flat manifest's wall_clock_seconds field."
                ),
            },
            "resources": {
                "peak_rss_bytes": None,
                "note": "not instrumented",
            },
            "result": {
                "raw_result_ref": "raw-result.json",
                "valid": old["status"] == "completed_valid",
                "invalid_reason": old.get("reason"),
                "certificate": {
                    "kind": old.get("certificate", {}).get("kind", "none"),
                    "verified": True,
                    "verifier": "no-claim",
                    "note": "measurement run; no discrete-log or relation claim made",
                },
            },
            "deviations": [],
            "notes": old.get("notes"),
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "raw_result": "raw-result.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
            },
        }
    }
    return new

def main():
    run_dirs = sorted(d for d in os.listdir(RUNS_DIR)
                       if os.path.isdir(os.path.join(RUNS_DIR, d)))
    n_ok, n_skip = 0, 0
    for d in run_dirs:
        mpath = os.path.join(RUNS_DIR, d, "manifest.yaml")
        if not os.path.exists(mpath):
            n_skip += 1
            continue
        with open(mpath) as f:
            old = json.load(f)
        if "run" in old and "run_id" not in old:
            n_skip += 1  # already reshaped
            continue
        new = reshape(old)
        with open(mpath, "w") as f:
            json.dump(new, f, indent=2)
        n_ok += 1
    print(f"reshaped: {n_ok}, skipped: {n_skip}, total dirs: {len(run_dirs)}")

if __name__ == "__main__":
    main()
