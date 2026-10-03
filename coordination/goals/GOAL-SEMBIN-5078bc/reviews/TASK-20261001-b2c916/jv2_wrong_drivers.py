#!/usr/bin/env python3
"""TASK-20261001-b2c916, joint JV-2 of REVIEW-SEMBIN-20261001-04ec3c-v2:
FAILURE POWER OF C-IMPL-GATE (AMD-20261001-e61f2b C-4 (a)-(e)).

Builds WRONG v2 cost functions as exact, count-checked patches of the committed
snapshot code (b8019a6fb, experiments/EXP-SEMBIN-04ec3c/code/v2/), and runs each
one END TO END through the committed pipeline, run_v2.py, unchanged except for
the patch. That pipeline:

  * regenerates M1-M4 FROM THE WRONG DRIVER (make_mutants.py reads the copy's
    own model_v2.py), as a wrong executor would commit them;
  * runs C-IMPL-GATE (a)-(d) on the wrong driver and on its four mutants, and
    (e) the gate-power self-test;
  * STOPS (exit 3) if the gate fails, STOPS (exit 4) if the C-3
    generic-lower-bound flag fires, else writes every row (exit 0).

A wrong driver BREAKS JV-2 iff its run exits 0 (gate (a)-(e) passed, flag
silent) AND it moves a primary sub-rho count or a store-free (E-2) margin by
more than 0.1 bit against the committed RUN-SEMBIN-be48b7.

W0 is the null control: no patch. Its raw-result.json must equal the committed
one byte for byte (sha256), or the harness itself is wrong and nothing it
reports is read.

Standard library only. Work directories go to --work (default: a scratch dir);
only small summaries and the patched sources are written beside this script.

Usage: python3 jv2_wrong_drivers.py [--work DIR] [--only W1,W3]
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # never write __pycache__ into committed code dirs

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
EXP = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c")
CODE = os.path.join(EXP, "code", "v2")
RUN = os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7")
DIGESTS = json.load(open(os.path.join(RUN, "artifact-digests.json")))
COPY = ("model_v2.py", "gate_v2.py", "run_v2.py", "make_mutants.py", "exploratory_v2.py")
DEGREES = (97, 109, 131, 163, 191, 233, 239, 283, 409, 571)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------------------
# The wrong drivers. Each patch is (file, old, new) and must match exactly once.
# `why_natural` is the plausible implementer's reasoning that produces it.
# `direction` is the sign of the error on totals (conservative = totals too
# HIGH, which is the direction that HIDES sub-rho cells under a negative claim).
# ---------------------------------------------------------------------------
WRONG = {
    "W0": {
        "label": "null control: committed code, no patch",
        "patches": [],
        "class": "control",
        "direction": "none",
        "why_natural": "n/a",
    },
    "W1": {
        "label": "FILL from an exact integer table count, |F| = 1 << int(d)",
        "patches": [("model_v2.py",
                     "        FILL = store_half if s >= 1 else 0.0\n",
                     "        FILL = math.log2((1 << int(d)) ** s) if s >= 1 else 0.0  # JV-2 W1: exact integer entry count\n")],
        "class": "off-grid d (gate (b) evaluates only d in {16, 24, 32}, all integers)",
        "direction": "anti-conservative (FILL too low by s*frac(d))",
        "why_natural": ("count table entries exactly as a Python int via a bit shift; "
                        "the shift needs an int, so int(d) silently floors the quarter-step d"),
    },
    "W1b": {
        "label": "W1 plus the oracle time half from the same integer count",
        "patches": [("model_v2.py",
                     "        FILL = store_half if s >= 1 else 0.0\n",
                     "        FILL = math.log2((1 << int(d)) ** s) if s >= 1 else 0.0  # JV-2 W1b\n"),
                    ("model_v2.py",
                     "        o = time_half\n",
                     "        o = math.log2((1 << int(d)) ** (m - s))  # JV-2 W1b: integer count for the time half too\n")],
        "class": "off-grid d, but bypassing the M3 mutation site",
        "direction": "anti-conservative",
        "why_natural": "the same integer-count habit applied to both halves",
    },
    "W2": {
        "label": "FILL with the factor base padded to 2^ceil(d)",
        "patches": [("model_v2.py",
                     "        FILL = store_half if s >= 1 else 0.0\n",
                     "        FILL = s * math.ceil(d) if s >= 1 else 0.0  # JV-2 W2: table indexed by ceil(d)-bit keys\n")],
        "class": "off-grid d (gate (b) evaluates only integer d)",
        "direction": "CONSERVATIVE (FILL too high by s*(ceil(d)-d))",
        "why_natural": "size the table for ceil(d)-bit index keys / a power-of-two hash table",
    },
    "W3": {
        "label": "C-2 domain guard read by its title, 'Trials >= 1': CALLS = TPR",
        "patches": [("model_v2.py",
                     "    CALLS = K + TPR\n",
                     "    CALLS = TPR  # JV-2 W3: C-2 'Trials >= 1 domain guard' read as trials-per-relation >= 1\n")],
        "class": "domain predicate (no gate check reads CALLS)",
        "direction": "CONSERVATIVE (excludes in-domain cells; every even-m argmin sits on the CALLS = 0 edge)",
        "why_natural": "AMD-20261001-e61f2b C-2's title is literally 'Trials >= 1 domain guard'",
    },
    "W4": {
        "label": "integer d grid (step 1.0 instead of 0.25)",
        "patches": [("model_v2.py", "D_STEP = 0.25\n", "D_STEP = 1.0  # JV-2 W4: integer d grid\n")],
        "class": "shared enumerator (gate (a), (c), (d) see only cells the driver's own sweep emits)",
        "direction": "CONSERVATIVE (coarser minimisation)",
        "why_natural": "|F| = 2^d read as an integer bit-length; a range() grid",
    },
    "W5": {
        "label": "N at n = 131 from the group order 4r instead of the subgroup order r (shared input)",
        "patches": [("run_v2.py",
                     '"log2_r": math.log2(r),',
                     '"log2_r": math.log2(4 * r),')],
        "class": "shared input (gate ref_N, C-BASELINE-CONSISTENCY and the driver all read the same log2_r)",
        "direction": "conservative on TOTAL, mixed on margins (VOW moves too)",
        "why_natural": "#E(F_2^131) = 4r is the number printed beside r in the frozen input",
    },
    "W6": {
        "label": "exact binomial yield for small fields (d < 16 only)",
        "patches": [("model_v2.py",
                     "    CALLS = K + TPR\n",
                     "    if d < 16.0 and 2.0 ** d >= 2 * m:  # JV-2 W6: exact C(2^d, m) for small fields\n"
                     "        TPR = N - (sum(math.log2(2.0 ** d - i) for i in range(m)) - L)\n"
                     "    CALLS = K + TPR\n")],
        "class": "d < 16 (gate (a) window is d >= 16; (b) grid is {16, 24, 32})",
        "direction": "conservative (C(X, m) < X^m/m!)",
        "why_natural": "the asymptotic X^m/m! is visibly wrong at small X, so 'fix' it there",
    },
    "W7": {
        "label": "VOW column from the field degree n instead of N (rho = 0.886 * 2^(n/2))",
        "patches": [("model_v2.py",
                     "    return LOG2_VOW_CONST + log2_N(n) / 2.0\n",
                     "    return LOG2_VOW_CONST + n / 2.0  # JV-2 W7: textbook 0.886 * 2^(n/2)\n")],
        "class": "baseline column (no check in (a)-(e) reads vow_column; only the NON-stopping C-BASELINE-CONSISTENCY does)",
        "direction": "margins at n = 131 shift by -1.000 bit; totals unchanged",
        "why_natural": "the textbook rho figure for an n-bit binary curve; the confusion A7 itself made",
    },
}


def build(wid, work):
    spec = WRONG[wid]
    wdir = os.path.join(work, wid)
    if os.path.exists(wdir):
        shutil.rmtree(wdir)
    cdir = os.path.join(wdir, "code")
    os.makedirs(os.path.join(cdir, "mutants"))
    for f in COPY:
        src = os.path.join(CODE, f)
        rel = os.path.relpath(src, REPO)
        if sha(src) != DIGESTS["code_v2"][rel]:
            raise SystemExit(f"{rel}: sha256 differs from the run's artifact-digests.json; refusing")
        shutil.copyfile(src, os.path.join(cdir, f))
    for f, old, new in spec["patches"]:
        p = os.path.join(cdir, f)
        text = open(p, encoding="utf-8").read()
        c = text.count(old)
        if c != 1:
            raise SystemExit(f"{wid}: patch site in {f} found {c} times, need exactly 1")
        open(p, "w", encoding="utf-8").write(text.replace(old, new))
    # the wrong executor commits mutants regenerated from ITS driver
    r = subprocess.run([sys.executable, os.path.join(cdir, "make_mutants.py"), "--write"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{wid}: make_mutants failed: {r.stdout} {r.stderr}")
    return wdir, cdir


def run(wid, wdir, cdir):
    rdir = os.path.join(wdir, "run")
    os.makedirs(rdir)
    t0 = time.time()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with open(os.path.join(rdir, "stdout.log"), "w") as so, open(os.path.join(rdir, "stderr.log"), "w") as se:
        p = subprocess.run([sys.executable, os.path.join(cdir, "run_v2.py"), "--run-dir", rdir],
                           cwd=REPO, stdout=so, stderr=se, env=env)
    return p.returncode, round(time.time() - t0, 1), rdir


def per_degree(raw):
    out = {}
    for n in DEGREES:
        e = raw["per_degree_minimum"][str(n)]["n"]
        out[n] = {"store_free_margin_vs_VOW": e["store_free_min_MITM"]["margin_vs_VOW_bits"],
                  "store_free_TOTAL": e["store_free_min_MITM"]["TOTAL"],
                  "store_free_m_d_s": [e["store_free_min_MITM"]["m"], e["store_free_min_MITM"]["d"],
                                       e["store_free_min_MITM"]["s"]],
                  "primary_margin_vs_VOW": e["primary_min"]["margin_vs_VOW_bits"],
                  "primary_margin_vs_PUB": e["primary_min"]["margin_vs_PUB_bits"]}
    return out


def argmin_index(raw):
    return {(r["n"], r["model"], r["B"], r["m"], r["d_bound"]): r["TOTAL"]
            for r in raw["argmin_rows"] if r["model"] in ("ENUM", "MITM", "MITM_CAPPED")}


def summarise(wid, code, secs, rdir, base):
    s = {"id": wid, **{k: WRONG[wid][k] for k in ("label", "class", "direction", "why_natural")},
         "patches": [{"file": f, "old": o, "new": n} for f, o, n in WRONG[wid]["patches"]],
         "exit_code": code, "seconds": secs}
    gp = os.path.join(rdir, "gate", "gate_report.json")
    if os.path.exists(gp):
        g = json.load(open(gp))
        u = g["unmutated"]
        s["gate"] = {
            "gate_passed_overall_incl_e": g["gate_passed"],
            "wrong_driver_passes_a_to_d": u["gate_passed"],
            "wrong_driver_failed_checks": u["failed_checks"],
            "a_cells_violations_maxdiff": [u["a_yield_identity"]["cells_checked"], u["a_yield_identity"]["violations"],
                                           u["a_yield_identity"]["max_abs_diff_bits"]],
            "b_cells_violations_maxdiff": [u["b_closed_forms"]["cells_checked"], u["b_closed_forms"]["violations"],
                                           u["b_closed_forms"]["max_abs_diff_bits"]],
            "c_cells_violations": [u["c_budget_invariant"]["cells_checked"], u["c_budget_invariant"]["violations"]],
            "d_probed_consistent": [u["d_m_bound_probe"]["argmins_at_m16_probed"],
                                    u["d_m_bound_probe"]["all_reevaluations_consistent"]],
            "e_self_test": g["e_gate_power_self_test"],
            "own_mutants_failed_checks": {k: v["failed_checks"] for k, v in g["mutants"].items()},
        }
        shutil.copyfile(gp, os.path.join(HERE, "jv2_out", f"{wid}_gate_report.json"))
    rp = os.path.join(rdir, "raw-result.json")
    if not os.path.exists(rp):
        return s
    raw = json.load(open(rp))
    s["raw_result_sha256"] = sha(rp)
    s["halted"] = raw.get("halted")
    if "generic_lower_bound_flag" in raw:
        f = raw["generic_lower_bound_flag"]
        s["C3_flag"] = {"fired": f.get("fired"), "fired_in_domain": f["fired_in_domain"],
                        "fired_out_of_domain": f["fired_out_of_domain"],
                        "min_slack_bits_by_degree": f["min_slack_bits_by_degree"]}
    if raw.get("halted") is not False:
        return s
    s["non_stopping_controls_passed"] = {k: v.get("passed") for k, v in raw["controls"].items()
                                         if isinstance(v, dict) and "passed" in v}
    s["primary_subrho_totals"] = raw["primary_subrho_totals"]
    pd, bpd = per_degree(raw), per_degree(base)
    rows = {}
    worst = 0.0
    for n in DEGREES:
        dm = pd[n]["store_free_margin_vs_VOW"] - bpd[n]["store_free_margin_vs_VOW"]
        dp = pd[n]["primary_margin_vs_VOW"] - bpd[n]["primary_margin_vs_VOW"]
        rows[n] = {"store_free_margin_vs_VOW": round(pd[n]["store_free_margin_vs_VOW"], 4),
                   "committed": round(bpd[n]["store_free_margin_vs_VOW"], 4),
                   "delta_bits": round(dm, 4),
                   "primary_margin_delta_bits": round(dp, 4),
                   "argmin_m_d_s": pd[n]["store_free_m_d_s"],
                   "committed_argmin_m_d_s": bpd[n]["store_free_m_d_s"]}
        if n == 131:
            rows[n]["PUB_margin"] = round(pd[n]["primary_margin_vs_PUB"], 4)
            rows[n]["PUB_margin_delta_bits"] = round(pd[n]["primary_margin_vs_PUB"] - bpd[n]["primary_margin_vs_PUB"], 4)
        worst = max(worst, abs(dm), abs(dp))
    s["E2_margins"] = rows
    s["max_abs_E2_or_primary_margin_delta_bits"] = round(worst, 4)
    ai, bi = argmin_index(raw), argmin_index(base)
    ch = [abs(ai[k] - bi[k]) for k in bi if k in ai]
    s["primary_argmin_rows"] = {"compared": len(ch), "changed_gt_1e-9": sum(1 for x in ch if x > 1e-9),
                                "changed_gt_0.1_bit": sum(1 for x in ch if x > 0.1),
                                "max_abs_change_bits": round(max(ch) if ch else 0.0, 4)}
    bt = base["primary_subrho_totals"]
    s["subrho_counts_changed"] = any(raw["primary_subrho_totals"][k] != bt[k] for k in bt)
    s["BREAKS_JV2"] = bool(code == 0 and raw.get("halted") is False and
                           (s["subrho_counts_changed"] or worst > 0.1))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("JV2_WORK", "/tmp/jv2_work"))
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, "jv2_out"), exist_ok=True)
    base_path = os.path.join(RUN, "raw-result.json")
    if sha(base_path) != DIGESTS["run_directory"]["raw-result.json"]:
        raise SystemExit("committed raw-result.json differs from its digest; refusing")
    base = json.load(open(base_path))
    ids = list(WRONG) if not a.only else a.only.split(",")
    if "W0" not in ids:
        ids = ["W0"] + ids
    results = {}
    for wid in ids:
        wdir, cdir = build(wid, a.work)
        code, secs, rdir = run(wid, wdir, cdir)
        s = summarise(wid, code, secs, rdir, base)
        if wid == "W0":
            s["reproduces_committed_raw_result_byte_for_byte"] = (
                s.get("raw_result_sha256") == DIGESTS["run_directory"]["raw-result.json"])
            if not s["reproduces_committed_raw_result_byte_for_byte"]:
                print(json.dumps(s, indent=1))
                raise SystemExit("W0 null control did not reproduce the committed run; harness invalid")
        else:
            shutil.copyfile(os.path.join(cdir, WRONG[wid]["patches"][0][0]),
                            os.path.join(HERE, "jv2_out", f"{wid}_{WRONG[wid]['patches'][0][0]}"))
        results[wid] = s
        print(f"{wid}: exit={code} {secs}s gate={s.get('gate', {}).get('gate_passed_overall_incl_e')} "
              f"halted={s.get('halted')} maxdelta={s.get('max_abs_E2_or_primary_margin_delta_bits')} "
              f"BREAKS={s.get('BREAKS_JV2')}", flush=True)
    out = {"task_id": "TASK-20261001-b2c916", "joint": "JV-2",
           "snapshot": "b8019a6fb", "committed_run": "RUN-SEMBIN-be48b7",
           "committed_raw_result_sha256": DIGESTS["run_directory"]["raw-result.json"],
           "python": sys.version.split()[0], "results": results}
    name = "jv2_results.json" if not a.only else f"jv2_results_{a.only.replace(',', '_')}.json"
    with open(os.path.join(HERE, "jv2_out", name), "w") as fh:
        fh.write(json.dumps(out, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
