"""EXP-PFDR-ca5e01 output checker: check.py <run_dir> <trial-plan.json> <trial-id>.

Exit 0 only when the trial's declared artifacts exist and pass the checks below.
It never edits an artifact and never interprets a result.

  selftest  selftest.json reports pass and >= 45 kernel-vs-brute checks.
  pilot     every declared cell has PILOT_CURVES ok pilot records; design.json's
            n_curves is re-derived from pilot-jobs.jsonl with the frozen rule.
  census    every (cell, curve) the design plans is present exactly once with
            NULL_REPS null counts, or is accounted for by a failed_infrastructure
            record for that same key (never hidden); a seeded sample of up to 4 small-base jobs (b <= 64) is
            recomputed from scratch and compared field by field, and each sampled
            structured base is recounted by brute force in Python (no kernel).
  analyze   per cell, S, M, kappa, z and z_cal are recomputed from the job records
            with independent sums; each cell class, the calibration gate,
            fraction_valid, the flagged list and the outcome are re-derived from the
            recorded statistics with the frozen thresholds. The bootstrap interval
            and replication statistics are not recomputed here (they are the
            producer's seeded resampling); the class rule reads the interval as
            recorded, so a wrong interval is visible in analysis.json only.
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402  (same sha256-bound directory)


def fail(msg: str) -> None:
    print("CHECK FAIL:", msg)
    sys.exit(3)


def load_jsonl(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def main() -> None:
    run_dir, plan_path, trial_id = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == trial_id)
    for name in trial["artifacts"]:
        if not os.path.exists(os.path.join(run_dir, name)):
            fail(f"missing artifact {name}")
    with open(os.path.join(run_dir, "raw-result.json")) as f:
        raw = json.load(f)
    if (raw.get("invalid_reason") or "").startswith("failed_infrastructure: "):
        fail(f"trial recorded {raw['invalid_reason']}")
    up = {k: os.path.join(run.RUNS_DIR, v) for k, v in trial.get("inputs_from", {}).items()}
    stage = trial["stage"]

    if stage == "selftest":
        with open(os.path.join(run_dir, "selftest.json")) as f:
            st = json.load(f)
        if not st.get("pass") or len(st.get("checks", [])) < 45:
            fail("selftest did not pass with >= 45 checks")
        if any(c["kernel"] != c["brute"] for c in st["checks"]):
            fail("a recorded kernel count differs from brute force")

    elif stage == "pilot":
        recs = [r for r in load_jsonl(os.path.join(run_dir, "pilot-jobs.jsonl")) if r["status"] == "ok"]
        with open(os.path.join(run_dir, "design.json")) as f:
            design = json.load(f)
        declared = {c["cell"] for c in run.cells()}
        if {c["cell"] for c in design["cells"]} != declared:
            fail("design.json cells differ from the declared cell grid")
        for c in design["cells"]:
            rs = [r for r in recs if r["cell"] == c["cell"]]
            if c["status"] != "ok":
                if len(rs) >= run.PILOT_CURVES:
                    fail(f"{c['cell']} marked incomplete but has all pilot records")
                continue
            if sorted(r["c"] for r in rs) != list(range(run.PILOT_CURVES)):
                fail(f"{c['cell']} pilot curves are not exactly 0..{run.PILOT_CURVES - 1}")
            vals = [x for r in rs for x in r["null"]]
            if len(vals) != run.PILOT_CURVES * run.NULL_REPS:
                fail(f"{c['cell']} pilot null count")
            mn = sum(vals) / len(vals)
            n = run.N_MAX if mn <= 0 else min(run.N_MAX, max(run.N_MIN, math.ceil(1.1 * run.TARGET_COINC / mn)))
            if n != c["n_curves"]:
                fail(f"{c['cell']} n_curves {c['n_curves']} != re-derived {n}")

    elif stage == "census":
        block = trial["block"]
        recs = load_jsonl(os.path.join(run_dir, f"{block}-jobs.jsonl"))
        with open(up["design"]) as f:
            design = json.load(f)
        only = None
        if block == "rep":
            with open(up["flags"]) as f:
                only = set(json.load(f)["flagged_cells"])
        planned = {(c["cell"], i) for c in design["cells"] if c["status"] == "ok"
                   and (only is None or c["cell"] in only) for i in range(c["n_curves"])}
        ok = {}
        for r in recs:
            if r["status"] == "ok":
                key = (r["cell"], r["c"])
                if key in ok:
                    fail(f"duplicate ok record {key}")
                if len(r["null"]) != run.NULL_REPS:
                    fail(f"{key} has {len(r['null'])} null counts")
                ok[key] = r
        missing = planned - set(ok)
        failed_keys = {(r["cell"], r["c"]) for r in recs if r["status"] != "ok"}
        if not all(str(r["status"]).startswith("failed_infrastructure:") for r in recs if r["status"] != "ok"):
            fail("a non-ok record is not labelled failed_infrastructure")
        unaccounted = missing - failed_keys
        if unaccounted:
            fail(f"{len(unaccounted)} planned jobs absent with no failed_infrastructure record for that key")
        if set(ok) - planned:
            fail("records outside the plan")
        small = sorted(k for k in ok if ok[k]["b"] <= 64)
        rng = random.Random(f"check|{run.EXP}|{block}")
        cellmap = {c["cell"]: c for c in design["cells"]}
        with tempfile.TemporaryDirectory() as bd:
            run.cmd_build(type("A", (), {"out": bd})())
            for key in rng.sample(small, min(4, len(small))):
                again = run.job(os.path.join(bd, "paircount"), cellmap[key[0]], block, key[1])
                for fld in ("p", "a", "N", "b", "null", "struct", "plant", "plant_L"):
                    if again[fld] != ok[key][fld]:
                        fail(f"replay mismatch {key} field {fld}")
                E, _ = run.get_curve(cellmap[key[0]]["bits"], block, key[1])
                cell = cellmap[key[0]]
                if cell["d"] == 1:
                    sb, _ = run.window_base(E, cell["b"], run._rng("struct", block, cell["cell"], key[1]))
                else:
                    sb, _ = run.gap_base(E, cell["b"], cell["d"], run._rng("struct", block, cell["cell"], key[1]))
                if run._brute(E, sb) != ok[key]["struct"]:
                    fail(f"brute-force recount mismatch {key}")

    elif stage == "analyze":
        with open(os.path.join(run_dir, trial["output"])) as f:
            an = json.load(f)
        main_recs = [r for r in load_jsonl(up["main"]) if r["status"] == "ok"]
        for row in an["cells"]:
            if "S" not in row:
                continue
            rs = [r for r in main_recs if r["cell"] == row["cell"]]
            S = sum(r["struct"] for r in rs)
            M = sum(sum(r["null"]) / len(r["null"]) for r in rs)
            if S != row["S"] or not math.isclose(M, row["M"], rel_tol=1e-9) \
                    or not math.isclose(S / M, row["kappa"], rel_tol=1e-9):
                fail(f"{row['cell']} S/M/kappa do not recompute")
            powered = M >= run.TARGET_COINC
            planted = row["plant_feasible_all"] and row["plant_kappa"] >= run.PLANT_KAPPA \
                and row["plant_z"] > run.PLANT_Z
            if not powered:
                cls = "inconclusive_underpowered"
            elif not planted:
                cls = "inconclusive_plant_not_recovered"
            elif abs(row["kappa"] - 1) >= run.FLAG_DEV and abs(row["z"]) > run.FLAG_Z:
                cls = "flagged"
            elif abs(row["kappa"] - 1) < run.NULL_DEV and 1 - 2 * run.NULL_DEV <= row["ci95"][0] \
                    and row["ci95"][1] <= 1 + 2 * run.NULL_DEV:
                cls = "null"
            else:
                cls = "intermediate"
            if cls != row["cls"]:
                fail(f"{row['cell']} class {row['cls']} != re-derived {cls}")
        for row in an["cells"]:
            if "S" not in row:
                continue
            rs = sorted((r for r in main_recs if r["cell"] == row["cell"]), key=lambda r: r["c"])
            V = sum(statistics.variance(r["null"]) for r in rs)
            sd = math.sqrt(V * (1 + 1 / run.NULL_REPS)) if V > 0 else float("nan")
            z = (row["S"] - row["M"]) / sd if sd == sd and sd > 0 else float("nan")
            if not (z == z and math.isclose(z, row["z"], rel_tol=1e-9, abs_tol=1e-12)):
                fail(f"{row['cell']} z does not recompute")
            pS = sum(r["null"][0] for r in rs)
            pM = sum(statistics.fmean(r["null"][1:]) for r in rs)
            pV = sum(statistics.variance(r["null"][1:]) for r in rs)
            zcal = (pS - pM) / math.sqrt(pV * (1 + 1 / (run.NULL_REPS - 1))) if pV > 0 else float("nan")
            if not math.isclose(zcal, row["z_cal"], rel_tol=1e-9, abs_tol=1e-12):
                fail(f"{row['cell']} z_cal does not recompute")
        zc = [r["z_cal"] for r in an["cells"] if r.get("powered")]
        cal_pass = bool(zc) and len(zc) > 1 and run.CAL_SD_LO <= statistics.pstdev(zc) <= run.CAL_SD_HI \
            and abs(statistics.fmean(zc)) <= run.CAL_MEAN_ABS
        if cal_pass != an["calibration"]["pass"]:
            fail("calibration gate does not re-derive")
        if zc and not math.isclose(statistics.pstdev(zc), an["calibration"]["sd"], rel_tol=1e-9):
            fail("calibration sd does not recompute")
        cls = [r["cls"] for r in an["cells"]]
        valid = [c for c in cls if c in ("null", "flagged", "intermediate")]
        frac = len(valid) / len(cls) if cls else 0.0
        if not math.isclose(frac, an["fraction_valid"], rel_tol=1e-9):
            fail("fraction_valid does not recompute")
        flagged = [r["cell"] for r in an["cells"] if r["cls"] == "flagged"]
        if flagged != an["flagged_cells"]:
            fail("flagged_cells do not re-derive")
        reps = {r["cell"]: r.get("replication") for r in an["cells"] if r["cls"] == "flagged"}
        survives = any(isinstance(v, dict) and v.get("survives") for v in reps.values())
        pending = any(v in ("not_run", "incomplete") for v in reps.values())
        if not cal_pass or frac < 0.5:
            outcome = "O-INVALID"
        elif survives:
            outcome = "O-STRUCT"
        elif pending:
            outcome = "O-PENDING-REPLICATION"
        elif valid and all(c == "null" for c in valid) and frac >= 0.8:
            outcome = "O-NULL"
        else:
            outcome = "O-MIXED"
        if outcome != an["outcome"]:
            fail(f"outcome {an['outcome']} != re-derived {outcome}")
        print("analyze outcome as recorded:", an["outcome"])
    else:
        fail(f"unknown stage {stage}")
    print("CHECK OK", trial_id)


if __name__ == "__main__":
    main()
