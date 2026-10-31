"""EXP-PFDR-2d36f9 output checker: check.py <run_dir> <trial-plan.json> <trial-id>.

Exit 0 only when the trial's declared artifacts exist and pass the checks below.
It never edits an artifact and never interprets a result.

  selftest  selftest.json reports pass, >= 81 kernel-vs-brute checks, the
            near-2^32 key checks, plant_internal (L in 1,2,3,5,9,14) and eight
            32-bit order certifications (N prime, Hasse, N*P = O on 4 points).
  pilot     every declared cell has PILOT_CURVES ok pilot records; design.json is
            re-derived from pilot-jobs.jsonl by run.build_design (n_curves,
            gamma_design, L per plant) and compared field by field.
  census    every (cell, curve) the design plans is present exactly once with
            NULL_REPS null counts, or is accounted for by a failed_infrastructure
            record for that same key; a seeded sample of up to 4 small-base jobs
            is recomputed from scratch and compared field by field, and each
            sampled structured base is recounted by brute force in Python.
  analyze   per cell, S, M, V, kappa, z and z_cal are recomputed from the job
            records with independent sums; each line's delta_hat is re-derived by
            OLS from its recorded kappa_by_rung and Nbar, its class re-derived
            from the recorded interval, the controls and the reading re-derived
            from the frozen rules. Bootstrap intervals are the producer's seeded
            resampling and are read as recorded.
  reanalysis  the descriptive stage-1 slopes are recomputed from the committed
            EXP-PFDR-ca5e01 analysis.json and main-jobs.jsonl.
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


def ols(xs: list, ys: list) -> tuple[float, float, list]:
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return float("nan"), float("nan"), [float("nan")] * n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    return slope, intercept, [y - (intercept + slope * x) for x, y in zip(xs, ys)]


def close(a, b, rel=1e-9, abs_=1e-12) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, float) and math.isnan(a) and isinstance(b, float) and math.isnan(b):
        return True
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)


def main() -> None:
    run_dir, plan_path, trial_id = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(plan_path) as f:
        plan = json.load(f)
    trial = next(t for t in plan["trials"] if t["id"] == trial_id)
    for name in trial["artifacts"]:
        if trial.get("allow_empty_artifacts") and name in trial["allow_empty_artifacts"]:
            if not os.path.exists(os.path.join(run_dir, name)):
                continue
        if not os.path.exists(os.path.join(run_dir, name)):
            fail(f"missing artifact {name}")
    with open(os.path.join(run_dir, "raw-result.json")) as f:
        raw = json.load(f)
    if (raw.get("invalid_reason") or "").startswith("failed_infrastructure: "):
        fail(f"trial recorded {raw['invalid_reason']}")
    up = {}
    for k, v in trial.get("inputs_from", {}).items():
        up[k] = v if os.path.isabs(v) else os.path.normpath(os.path.join(run.RUNS_DIR, v))
    stage = trial["stage"]

    if stage == "selftest":
        with open(os.path.join(run_dir, "selftest.json")) as f:
            st = json.load(f)
        if not st.get("pass"):
            fail("selftest did not pass")
        checks = st.get("checks", [])
        key_checks = st.get("key_checks", [])
        if len(checks) < 126:
            fail(f"selftest has {len(checks)} kernel-vs-brute checks (< 126)")
        if {c["bits"] for c in checks} != {10, 12, 14, 16, 20, 24, 28, 32}:
            fail("selftest does not cover the required bit sizes")
        if len(key_checks) < 9:
            fail(f"selftest has {len(key_checks)} near-2^32 key checks (< 9)")
        if any(c["kernel"] != c["brute"] for c in checks + key_checks):
            fail("a recorded kernel count differs from brute force")
        internal = st.get("plant_internal_checks", [])
        if sorted(c["L"] for c in internal) != [1, 2, 3, 5, 9, 14] \
                or any(not c["pass"] for c in internal):
            fail("plant_internal checks are missing or failed")
        order = st.get("order_certification", [])
        if sum(1 for c in order if c.get("bits") == 32) < 8:
            fail("eight 32-bit order certifications are required")
        if sum(1 for c in order if c.get("bits") == 28) < 4:
            fail("four 28-bit order certifications are required")
        if any(not c.get("pass") for c in order):
            fail("order certification is missing or failed")
        for c in order:
            if not (c.get("N_prime") and c.get("hasse") and c.get("points_ok") == 4):
                fail(f"order certification incomplete at seed {c.get('seed')}")
        kb = st.get("key_bound", {})
        if not (kb.get("pass") and kb.get("lt_2_64") and kb.get("p_lt_2_32")):
            fail("paircount key bound not certified")

    elif stage == "pilot":
        recs = [r for r in load_jsonl(os.path.join(run_dir, "pilot-jobs.jsonl"))
                if r["status"] == "ok"]
        with open(os.path.join(run_dir, "design.json")) as f:
            design = json.load(f)
        declared = {c["cell"] for c in run.cells()}
        if {c["cell"] for c in design["cells"]} != declared:
            fail("design.json cells differ from the declared cell grid")
        for c in design["cells"]:
            rs = [r for r in recs if r["cell"] == c["cell"]]
            if c.get("status") != "ok":
                if len(rs) >= run.PILOT_CURVES:
                    fail(f"{c['cell']} marked incomplete but has all pilot records")
                continue
            if sorted(r["c"] for r in rs) != list(range(run.PILOT_CURVES)):
                fail(f"{c['cell']} pilot curves are not exactly 0..{run.PILOT_CURVES - 1}")
            vals = [x for r in rs for x in r["null"]]
            if len(vals) != run.PILOT_CURVES * run.NULL_REPS:
                fail(f"{c['cell']} pilot null count")
        again = run.build_design(recs)
        for c, d in zip(again["cells"], design["cells"]):
            if c["cell"] != d["cell"]:
                fail("re-derived design cell order differs")
            if c.get("status") != d.get("status"):
                fail(f"{c['cell']} status does not re-derive")
            if c.get("status") == "ok" and c["n_curves"] != d["n_curves"]:
                fail(f"{c['cell']} n_curves does not re-derive")
        if len(again.get("plants", [])) != len(design.get("plants", [])):
            fail("plant design entries do not re-derive")
        for a, b in zip(again.get("plants", []), design.get("plants", [])):
            key = (a["bits"], a["theta"], a["gamma"])
            if key != (b["bits"], b["theta"], b["gamma"]):
                fail(f"plant entry order differs at {key}")
            for fld in ("L_lo", "L_hi", "feasible", "L_per_curve", "L_cap"):
                if a[fld] != b[fld]:
                    fail(f"plant {key} field {fld} does not re-derive")
            if not close(a["gamma_design"], b["gamma_design"]):
                fail(f"plant {key} gamma_design does not re-derive")

    elif stage == "census":
        block = trial["block"]
        recs = load_jsonl(os.path.join(run_dir, f"{block}-jobs.jsonl"))
        with open(up["design"]) as f:
            design = json.load(f)
        only = None
        if block == "rep":
            with open(up["flags"]) as f:
                only = set(json.load(f)["alive_cells"])
        planned = {(c["cell"], i) for c in design["cells"] if c.get("status") == "ok"
                   and (only is None or c["cell"] in only) for i in range(c["n_curves"])}
        ok = {}
        for r in recs:
            if r["status"] == "ok":
                key = (r["cell"], r["c"])
                if key in ok:
                    fail(f"duplicate ok record {key}")
                if len(r["null"]) != run.NULL_REPS:
                    fail(f"{key} has {len(r['null'])} null counts")
                if len(r["plant"]) != len(run.GAMMAS):
                    fail(f"{key} has {len(r['plant'])} plant counts")
                if not r.get("order", {}).get("pass"):
                    fail(f"{key} curve order not certified")
                ok[key] = r
        missing = planned - set(ok)
        failed_keys = {(r["cell"], r["c"]) for r in recs if r["status"] != "ok"}
        if not all(str(r["status"]).startswith("failed_infrastructure:")
                   for r in recs if r["status"] != "ok"):
            fail("a non-ok record is not labelled failed_infrastructure")
        unaccounted = missing - failed_keys
        if unaccounted:
            fail(f"{len(unaccounted)} planned jobs absent with no failed_infrastructure record")
        if set(ok) - planned:
            fail("records outside the plan")
        small = sorted(k for k in ok if ok[k]["b"] <= 64)
        rng = random.Random(f"check|{run.EXP}|{block}")
        cellmap = {c["cell"]: c for c in design["cells"]}
        with tempfile.TemporaryDirectory() as bd:
            run.cmd_build(type("A", (), {"out": bd})())
            for key in rng.sample(small, min(4, len(small))):
                cell = cellmap[key[0]]
                cfgs = run.plant_cfgs_for(design, cell, block, key[1])
                again = run.job(os.path.join(bd, "paircount"), cell, block, key[1], cfgs)
                for fld in ("p", "a", "N", "b", "null", "struct", "plant", "zn",
                            "plant_L"):
                    if again[fld] != ok[key][fld]:
                        fail(f"replay mismatch {key} field {fld}")
                E, G, _ = run.get_curve(cell["bits"], block, key[1])
                if cell["d"] == 1:
                    sb, _ = run.window_base(E, cell["b"],
                                            run._rng("struct", block, cell["bits"],
                                                     cell["theta"], cell["d"], key[1]))
                else:
                    sb, _ = run.gap_base(E, cell["b"], cell["d"],
                                         run._rng("struct", block, cell["bits"],
                                                  cell["theta"], cell["d"], key[1]))
                if run._brute(E, sb) != ok[key]["struct"]:
                    fail(f"brute-force recount mismatch {key}")
                pb = run.gamma_plant_base(E, G, cell["b"],
                                          ok[key]["plant_L"][run.GAMMAS[0]],
                                          run._rng("plant", block, cell["bits"],
                                                   cell["theta"], run.GAMMAS[0], key[1]))
                if run._brute(E, pb) != ok[key]["plant"][run.GAMMAS[0]]:
                    fail(f"brute-force plant recount mismatch {key}")

    elif stage == "analyze" and trial.get("mode") == "reanalysis":
        with open(os.path.join(run_dir, trial["output"])) as f:
            ra = json.load(f)
        with open(up["ca5e01_analysis"]) as f:
            analysis = json.load(f)
        main_recs = [r for r in load_jsonl(up["ca5e01_main"]) if r.get("status") == "ok"]
        nbar: dict = {}
        for r in main_recs:
            nbar.setdefault(r["cell"], {}).setdefault(r["c"], r["N"])
        for key, row in ra["slopes"].items():
            pts = []
            for cell in analysis.get("cells", []):
                if cell.get("theta") != row["theta"] or cell.get("d") != row["d"]:
                    continue
                if "kappa" not in cell or cell["kappa"] <= 0:
                    continue
                ns = nbar.get(cell["cell"], {})
                if not ns:
                    continue
                pts.append((statistics.fmean(math.log2(n) for n in ns.values()), cell["kappa"]))
            if len(pts) < 3:
                fail(f"reanalysis {key} has {len(pts)} points (< 3)")
            slope = ols([p[0] for p in pts], [math.log2(p[1]) for p in pts])[0]
            if not close(slope, row["slope"]):
                fail(f"reanalysis {key} slope does not recompute")
        if not ra.get("kind") == "reanalysis-ca5e01":
            fail("reanalysis kind is not descriptive-only")
        print("reanalysis lines:", len(ra["slopes"]))

    elif stage == "analyze":
        with open(os.path.join(run_dir, trial["output"])) as f:
            an = json.load(f)
        main_recs = [r for r in load_jsonl(up["main"]) if r["status"] == "ok"]
        rep_recs = []
        if up.get("rep") and os.path.exists(up["rep"]):
            rep_recs = [r for r in load_jsonl(up["rep"]) if r["status"] == "ok"]
        selftest_pass = False
        if up.get("selftest") and os.path.exists(up["selftest"]):
            with open(up["selftest"]) as f:
                selftest_pass = bool(json.load(f).get("pass"))
        if selftest_pass != an.get("selftest_pass"):
            fail("recorded selftest_pass differs from selftest.json")
        with open(up["design"]) as f:
            design = json.load(f)
        cellmap = {c["cell"]: c for c in design["cells"]}

        def stats(rs, kind):
            rs = sorted(rs, key=lambda r: r["c"])
            if kind == "struct":
                Ss = [r["struct"] for r in rs]
            elif kind == "zn":
                Ss = [r["zn"] for r in rs]
            elif kind.startswith("plant:"):
                Ss = [r["plant"][kind.split(":", 1)[1]] for r in rs]
            elif kind == "aa":
                Ss = [r["null"][0] for r in rs]
            Ms = [statistics.fmean(r["null"]) for r in rs]
            Vs = [statistics.variance(r["null"]) for r in rs]
            S, M, V = sum(Ss), sum(Ms), sum(Vs)
            pS = sum(r["null"][0] for r in rs)
            pM = sum(statistics.fmean(r["null"][1:]) for r in rs)
            pV = sum(statistics.variance(r["null"][1:]) for r in rs)
            sd = math.sqrt(V * (1 + 1 / run.NULL_REPS)) if V > 0 else float("nan")
            return {"S": S, "M": M, "V": V,
                    "kappa": S / M if M > 0 else float("nan"),
                    "z": (S - M) / sd if sd == sd and sd > 0 else float("nan"),
                    "z_cal": (pS - pM) / math.sqrt(pV * (1 + 1 / (run.NULL_REPS - 1)))
                    if pV > 0 else float("nan")}

        for row in an["cells"]:
            if "S" not in row:
                continue
            rs = [r for r in main_recs if r["cell"] == row["cell"]]
            st = stats(rs, "struct")
            if st["S"] != row["S"] or not close(st["M"], row["M"]) \
                    or not close(st["V"], row["V"]) \
                    or not close(st["kappa"], row["kappa"]) \
                    or not close(st["z"], row["z"]) \
                    or not close(st["z_cal"], row["z_cal"]):
                fail(f"{row['cell']} S/M/V/kappa/z/z_cal do not recompute")

        zc = [r["z_cal"] for r in an["cells"] if "z_cal" in r]
        cal_pass = bool(zc) and len(zc) > 1 and run.CAL_SD_LO <= statistics.pstdev(zc) <= run.CAL_SD_HI \
            and abs(statistics.fmean(zc)) <= run.CAL_MEAN_ABS
        if cal_pass != an["calibration"]["pass"]:
            fail("calibration gate does not re-derive")
        if zc and not close(statistics.pstdev(zc), an["calibration"]["sd"]):
            fail("calibration sd does not recompute")

        lines = an["lines"]
        struct_lines = [r for r in lines if r["kind"] == "struct"]
        plant_lines = [r for r in lines if r["kind"] == "plant"]
        zn_lines = [r for r in lines if r["kind"] == "zn"]
        aa_lines = [r for r in lines if r["kind"] == "aa"]
        if len(struct_lines) != 6 or len(plant_lines) != 8 or len(zn_lines) != 2 \
                or len(aa_lines) != 6:
            fail("line counts differ from the frozen grid")
        for row in lines:
            if not row["valid"]:
                if row["class"] != "invalid":
                    fail(f"{row['label']} invalid line is not class invalid")
                continue
            xs = [k["Nbar"] for k in row["kappa_by_rung"]]
            ys = [math.log2(k["kappa"]) if k["kappa"] > 0 else float("nan")
                  for k in row["kappa_by_rung"]]
            delta, _, resid = ols(xs, ys)
            if not close(delta, row["delta_hat"]):
                fail(f"{row['label']} delta_hat does not recompute")
            for a, b in zip(resid, row["residuals"]):
                if not close(a, b):
                    fail(f"{row['label']} residuals do not recompute")
            cls = run.classify(row["valid"], row["ci95"][0], row["ci95"][1])
            if cls != row["class"]:
                fail(f"{row['label']} class {row['class']} != re-derived {cls}")

        c3_pass = True
        for theta in run.THETAS:
            for gamma in run.GAMMAS:
                row = next(r for r in plant_lines
                           if r["theta"] == theta and r["gamma"] == gamma)
                slope_ok = row["valid"] and abs(row["delta_hat"] - row["gamma_design"]) <= run.PLANT_SLOPE_TOL
                gamma_ok = row["valid"] and abs(row["gamma_design"] - run._gamma_value(gamma)) <= run.PLANT_GAMMA_TOL
                if gamma == "0":
                    c3_pass = c3_pass and slope_ok and gamma_ok and row["class"] == "SUB-BE"
                elif gamma == "1/6":
                    c3_pass = c3_pass and slope_ok and gamma_ok and row["class"] == "SUB-BE-GROWING"
                elif gamma == "1/2":
                    c3_pass = c3_pass and slope_ok and gamma_ok and row["class"] == "ALIVE"
                else:
                    c3_pass = c3_pass and slope_ok and gamma_ok
        c4_pass = True
        for theta in run.THETAS:
            row = next(r for r in zn_lines if r["theta"] == theta)
            c4_pass = c4_pass and row["valid"] \
                and abs(row["delta_hat"] - (1.0 - theta)) <= run.ZN_TOL and row["class"] == "ALIVE"
        aa_cover = sum(1 for r in aa_lines if r["valid"] and r["ci95"][0] <= 0 <= r["ci95"][1])
        aa_alive = [r["label"] for r in aa_lines if r["class"] == "ALIVE"]
        c5_pass = aa_cover >= 5 and not aa_alive
        c6_pass = cal_pass
        for cid, expected in (("C3", c3_pass), ("C4", c4_pass), ("C5", c5_pass),
                              ("C6", c6_pass)):
            if bool(an["controls"][cid]["pass"]) != bool(expected):
                fail(f"control {cid} does not re-derive")
        valid_struct = [r for r in struct_lines if r["valid"]]
        alive = [r for r in valid_struct if r["class"] == "ALIVE"]
        if [r["label"] for r in valid_struct] != an["valid_lines"]:
            fail("valid_lines do not re-derive")
        if [r["label"] for r in alive] != an["alive_lines"]:
            fail("alive_lines do not re-derive")
        blocking = c3_pass and c4_pass and c5_pass and c6_pass
        block = an["block"]
        for row in alive:
            rep = row.get("replication") or {}
            if not rep.get("complete"):
                continue
            rungs = []
            for k in row["kappa_by_rung"]:
                cellname = k["cell"]
                rs = [r for r in rep_recs if r["cell"] == cellname]
                if len(rs) < cellmap[cellname].get("n_curves", 1):
                    fail(f"{row['label']} replication records missing at {cellname}")
                st = stats(rs, "struct")
                if st["M"] < run.TARGET_COINC:
                    fail(f"{row['label']} replication M below target")
                rungs.append((statistics.fmean(math.log2(r["N"]) for r in rs), st["kappa"]))
            delta = ols([x for x, _ in rungs],
                        [math.log2(k) for _, k in rungs])[0]
            if not close(delta, rep["delta_hat"]):
                fail(f"{row['label']} replication delta does not recompute")
            if rep["class"] != run.classify(True, rep["ci95"][0], rep["ci95"][1]):
                fail(f"{row['label']} replication class does not re-derive")
            if bool(rep["survives"]) != bool(rep["ci95"][0] > 0
                                             and rep["ci95"][1] >= run.DELTA_STAR):
                fail(f"{row['label']} replication survival does not re-derive")
        if not selftest_pass or not blocking or len(valid_struct) < 5:
            reading = "O-INVALID"
        elif any(r.get("replication", {}).get("survives") for r in alive):
            reading = "O-ALIVE"
        elif block == "main" and any(r.get("replication", {}).get("complete") is False
                                     for r in alive):
            reading = "O-PENDING-REPLICATION"
        elif valid_struct and all(r["class"] in ("SUB-BE", "SUB-BE-GROWING")
                                  for r in valid_struct):
            reading = "O-SUB-BE"
        else:
            reading = "O-MIXED"
        if reading != an["reading"]:
            fail(f"reading {an['reading']} != re-derived {reading}")
        print("analyze reading as recorded:", an["reading"])
    else:
        fail(f"unknown stage {stage}")
    print("CHECK OK", trial_id)


if __name__ == "__main__":
    main()
