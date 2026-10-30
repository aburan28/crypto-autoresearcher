"""J2a(6): run count and order, schema completeness, seeds, raw/summary agreement, arm comparability, and an
independent recomputation of analysis /cells and the top-level reading from the recorded jobs file.

Read-only. Imports nothing from experiments/ (no run.py or check.py); the frozen rules are taken from
specification.yaml and coded here. Floats are recomputed from exact rationals with explicit left-fold sums
(the accumulation order of the recorded CPython 3.11 builtin sum) and compared both bit for bit and within
rel_tol 1e-9 / abs_tol 1e-12.

usage: python3 -I -B integrity.py <repo-root> <curves-regenerated.json> <out.json>
"""
import hashlib
import json
import math
import os
import random
import sys
from fractions import Fraction

import yaml

REPO, CURVES, OUT = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
EXP = "experiments/EXP-PFDR-bb0d26"
RUNS = os.path.join(REPO, EXP, "runs")
PLAN_IDS = [("selftest", "RUN-PFDR-e44a19"), ("census-toy-main", "RUN-PFDR-4d8c71"), ("analyze-main", "RUN-PFDR-243425"),
            ("census-toy-rep", "RUN-PFDR-cd03e2"), ("analyze-final", "RUN-PFDR-089edc")]
REL, ABS = 1e-9, 1e-12
groups = {}


def check(group, name, ok, detail=None):
    g = groups.setdefault(group, {"checks": 0, "failures": 0, "failed": []})
    g["checks"] += 1
    if not ok:
        g["failures"] += 1
        g["failed"].append({"check": name, "detail": detail})


def jl(path):
    with open(path) as f:
        return json.load(f)


def yl(path):
    with open(path) as f:
        return yaml.safe_load(f)


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


spec = yl(os.path.join(REPO, EXP, "specification.yaml"))["experiment"]
plan = jl(os.path.join(REPO, EXP, "trial-plan.json"))
journal = [json.loads(ln) for ln in open(os.path.join(REPO, EXP, "runbook-sessions/RBS-PFDR-bb0d26/journal.jsonl"))]
with open(os.path.join(REPO, EXP, "trial-plan.json"), "rb") as f:
    plan_sha = hashlib.sha256(f.read()).hexdigest()

# ------------------------------------------------------------------ (a) run count and order
G = "run_count_and_order"
dirs = sorted(d for d in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS, d)))
check(G, "exactly the five planned run directories", dirs == sorted(r for _, r in PLAN_IDS), dirs)
check(G, "spec replication.trials order and ids", [(t["trial_id"], t["run_id"]) for t in spec["replication"]["trials"]] == PLAN_IDS)
check(G, "trial-plan trials order and ids", [(t["id"], t["run_id"]) for t in plan["trials"]] == PLAN_IDS)
check(G, "spec budget maximum_runs is 5", spec["budget"]["maximum_runs"] == 5)
units = [e for e in journal if e["type"] == "unit_recorded"]
att2 = [e for e in units if e["seq"] > 9]
att1 = [e for e in units if e["seq"] < 9]
check(G, "journal attempt 2 records the five units in plan order", [(e["trial_id"], e["run_id"]) for e in att2] == PLAN_IDS,
      [(e["seq"], e["trial_id"], e["run_id"]) for e in att2])
check(G, "journal attempt 2 units valid and output_validated", all(e["valid"] and e["receipt_status"] == "output_validated" for e in att2))
check(G, "journal attempt 1 units not_run with no run directory or receipt",
      all(e["receipt_status"] == "not_run" and e["run_dir"] is None and e["receipt_sha256"] is None for e in att1))
check(G, "journal attempt 1 stopped before any launch (supervisor refused, exit 2)",
      any(e["type"] == "step_finished" and e["seq"] == 7 and e["exit_code"] == 2 for e in journal))
fin = journal[-1]
check(G, "session finished completed, 5 valid of 5", fin["type"] == "session_finished" and fin["status"] == "completed"
      and fin["summary"]["units"] == {"invalid": [], "total": 5, "valid": 5})
prev_end = None
for tid, rid in PLAN_IDS:
    m = yl(os.path.join(RUNS, rid, "manifest.yaml"))["run"]
    rc = jl(os.path.join(RUNS, rid, "execution-receipt.json"))
    lj = jl(os.path.join(RUNS, rid, "launch.json"))
    check(G, f"{rid} identity (manifest, receipt, launch, raw-result)",
          m["id"] == rid and m["trial_id"] == tid and rc["run_id"] == rid and rc["trial_id"] == tid
          and lj["run_id"] == rid and lj["trial_id"] == tid)
    if prev_end is not None:
        check(G, f"{rid} starts after the previous trial finished (manifest and receipt)",
              m["timing"]["started_at"] >= prev_end[0] and rc["started_at"] >= prev_end[1],
              [m["timing"]["started_at"], prev_end])
    prev_end = (m["timing"]["finished_at"], rc["finished_at"])
    from datetime import datetime
    t_s = datetime.strptime(m["timing"]["started_at"], "%Y-%m-%dT%H:%M:%SZ")
    t_f = datetime.strptime(m["timing"]["finished_at"], "%Y-%m-%dT%H:%M:%SZ")
    check(G, f"{rid} manifest wall_seconds consistent with started/finished (within 2 s)",
          abs((t_f - t_s).total_seconds() - m["timing"]["wall_seconds"]) <= 2.0,
          [m["timing"], (t_f - t_s).total_seconds()])
    check(G, f"{rid} receipt interval brackets the manifest interval (to the second)",
          rc["started_at"][:19] <= m["timing"]["started_at"][:19] and m["timing"]["finished_at"][:19] <= rc["finished_at"][:19],
          [rc["started_at"], m["timing"]["started_at"], m["timing"]["finished_at"], rc["finished_at"]])
    env = jl(os.path.join(RUNS, rid, "environment.json"))
    check(G, f"{rid} environment.json python agrees with manifest python_version",
          env["python"].split()[0] == m["environment"]["python_version"], [env["python"], m["environment"]["python_version"]])
    check(G, f"{rid} receipt returncode 0 and check_returncode 0", rc["returncode"] == 0 and rc["check_returncode"] == 0)

# ------------------------------------------------------------------ (b) schema completeness
G = "schema"
impl = os.path.join(REPO, EXP, "implementation")
pyc = sorted(os.path.relpath(os.path.join(dp, fn), impl) for dp, _, fns in os.walk(impl) for fn in fns
             if fn.endswith((".py", ".c")) and "__pycache__" not in dp)
for tid, rid in PLAN_IDS:
    m = yl(os.path.join(RUNS, rid, "manifest.yaml"))["run"]
    need = ["id", "experiment_id", "hypothesis_id", "task_id", "trial_id", "status", "validity", "code", "environment",
            "inputs", "timing", "resources", "result", "artifacts"]
    check(G, f"{rid} manifest /run keys", all(k in m for k in need), [k for k in need if k not in m])
    check(G, f"{rid} code keys", all(k in m["code"] for k in ("commit", "dirty", "command", "code_sha256", "trial_plan_sha256")))
    check(G, f"{rid} code_sha256 covers every .py and .c under implementation/", sorted(m["code"]["code_sha256"]) == pyc,
          [sorted(m["code"]["code_sha256"]), pyc])
    check(G, f"{rid} environment keys", all(k in m["environment"] for k in ("host", "operating_system", "python_version",
                                                                            "gcc_version", "processor_count")))
    check(G, f"{rid} resources keys", all(k in m["resources"] for k in ("peak_rss_bytes", "cpu_seconds")))
    check(G, f"{rid} result certificate kind none", m["result"]["certificate"]["kind"] == "none")
    check(G, f"{rid} python_version 3.11.15", m["environment"]["python_version"] == "3.11.15", m["environment"]["python_version"])
    check(G, f"{rid} trial_plan_sha256 equals the plan file", m["code"]["trial_plan_sha256"] == plan_sha)
    check(G, f"{rid} commit 48bd193abf and dirty false", m["code"]["commit"] == "48bd193abff869348779b06e4bd9a93b7bbe1d95"
          and m["code"]["dirty"] is False)
    check(G, f"{rid} manifest artifacts equal plan artifacts minus manifest.yaml",
          m["artifacts"] == [a for a in next(t for t in plan["trials"] if t["id"] == tid)["artifacts"] if a != "manifest.yaml"])
    check(G, f"{rid} inputs.seed equals spec seed blocks", m["inputs"]["seed"] == {"main": 8100000, "rep": 8200000, "selftest": 8900000}
          and spec["replication"]["seeds"] == [8100000, 8200000, 8900000] and plan["defaults"]["seed_blocks"] == m["inputs"]["seed"])
    raw = jl(os.path.join(RUNS, rid, "raw-result.json"))
    check(G, f"{rid} raw-result keys", sorted(raw) == ["experiment", "invalid_reason", "run_id", "summary", "trial_id"])
    sk = {"selftest": {"selftest_pass", "cells", "cells_ok"}, "census-toy-main": {"jobs", "failed_infrastructure"},
          "census-toy-rep": {"jobs", "failed_infrastructure"},
          "analyze-main": {"outcome", "headline", "flagged_cells", "calibration", "fraction_valid"},
          "analyze-final": {"outcome", "headline", "flagged_cells", "calibration", "fraction_valid"}}[tid]
    check(G, f"{rid} raw-result summary keys per schema", sk <= set(raw["summary"]), sorted(raw["summary"]))
design = jl(os.path.join(RUNS, "RUN-PFDR-e44a19", "design.json"))
check(G, "design.json keys", set(design) == {"experiment", "rule", "toy_cells"}
      and all(set(c) == {"cell", "bits", "r", "n", "mu_ref", "n_curves"} for c in design["toy_cells"]))
st = jl(os.path.join(RUNS, "RUN-PFDR-e44a19", "selftest.json"))
check(G, "selftest.json keys", set(st) == {"pass", "checks"} and all(set(c) == {"name", "expected", "observed", "pass"} for c in st["checks"]))
cells_schema = ["cell", "bits", "r", "n", "cls", "curves", "S", "M", "V", "kappa", "ci95", "z", "plant_kappa", "plant_z",
                "plant_feasible_all", "z_cal", "d_ratio", "null_mean_over_formula", "kappa_even", "kappa_odd", "powered",
                "planted_recovered", "replication"]
schema_notes = []
for rid, fn in (("RUN-PFDR-243425", "analysis-main.json"), ("RUN-PFDR-089edc", "analysis.json")):
    an = jl(os.path.join(RUNS, rid, fn))
    top = ["experiment", "outcome", "headline", "calibration", "fraction_valid", "flagged_cells", "secondary_slope_logkappa_per_log2n", "cells"]
    check(G, f"{fn} top-level keys", all(k in an for k in top))
    check(G, f"{fn} calibration keys", set(an["calibration"]) == {"n", "mean", "sd", "pass"})
    for row in an["cells"]:
        miss = [k for k in cells_schema if k not in row]
        if row["cls"] == "invalid":
            schema_notes.append({"file": fn, "cell": row["cell"], "cls": row["cls"], "absent_schema_fields": miss,
                                 "present": sorted(row)})
        else:
            check(G, f"{fn} {row['cell']} cells[] keys", not miss, miss)

# ------------------------------------------------------------------ jobs file: seeds, completeness, arms
recs = [json.loads(ln) for ln in open(os.path.join(RUNS, "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")) if ln.strip()]
dcell = {c["cell"]: c for c in design["toy_cells"]}
G = "seeds_and_completeness"
check(G, "every record block main", all(r["block"] == "main" for r in recs), sorted({r["block"] for r in recs}))
check(G, "no replication or selftest record in the main file", not [r for r in recs if r["block"] in ("rep", "selftest")])
check(G, "every c in [0, n_curves) of its cell", all(0 <= r["c"] < dcell[r["cell"]]["n_curves"] for r in recs))
keys = [(r["cell"], r["c"]) for r in recs]
check(G, "no duplicate (cell, c)", len(keys) == len(set(keys)))
planned = {(c["cell"], i) for c in design["toy_cells"] for i in range(c["n_curves"])}
check(G, "record key set equals the planned key set", set(keys) == planned, [len(set(keys)), len(planned)])
check(G, "record count equals sum of n_curves", len(recs) == sum(c["n_curves"] for c in design["toy_cells"]) == 6657, len(recs))
check(G, "cell fields (bits, r, n) equal the design", all((r["bits"], r["r"], r["n"]) == (dcell[r["cell"]]["bits"], dcell[r["cell"]]["r"],
                                                           dcell[r["cell"]]["n"]) for r in recs))
cur = jl(CURVES)
check(G, "every record's curve regenerates from seed 8,100,000 + c (scripts/regen_curves.py)",
      cur["records_compared"] == len(recs) and not cur["regenerated_from_seed_8100000_plus_c_mismatches_or_invariant_failures"])
check(G, "PARI ellcard certifies every recorded N (scripts/regen_curves.py)",
      cur["pari"]["curves"] == 1580 and not cur["pari"]["failures"] and cur["pari"]["negative_control_wrong_order_N_plus_2"]["rejected"])
statuses = {}
for r in recs:
    statuses[r["status"]] = statuses.get(r["status"], 0) + 1
check(G, "statuses only ok and degenerate", set(statuses) <= {"ok", "degenerate"}, statuses)
job_keys = ["cell", "block", "c", "p", "a", "b_coef", "N", "bits", "r", "n", "status", "null_C", "null_D", "gap_C", "gap_D",
            "gap_meta", "plant_m", "plant_internal", "plant_C", "plant_D", "plant_feasible", "seconds"]
check(G, "every jobs record carries the toy_jobs_jsonl schema fields", all(all(k in r for k in job_keys) for r in recs))
check(G, "every gap_meta carries T, enumerated, duplicate_skips, first, last",
      all(all(k in r["gap_meta"] for k in ("T", "enumerated", "duplicate_skips", "first", "last")) for r in recs))
census_m = yl(os.path.join(RUNS, "RUN-PFDR-4d8c71", "manifest.yaml"))["run"]
seconds_sum = round(sum(r["seconds"] for r in recs), 1)

G = "arm_comparability"
shared = {}
nfail = {"curve_shared": 0, "arms_present": 0, "D_range": 0, "C_ge_pairs_minus_D": 0, "plant_C_ge_internal": 0,
         "plant_m_range": 0, "plant_feasible_rule": 0, "gap_meta": 0, "curve_invariants": 0}
fail_examples = []


def ht(r, T):
    return ((2 * T + 1) ** r - 1) // 2


def leastT(r, n):
    need = -(-102 * n // 100) + 8
    T = 0
    while ht(r, T) < need:
        T += 1
    return T


for r in recs:
    key = (r["bits"], r["c"])
    cv = (r["p"], r["a"], r["b_coef"], r["N"])
    if key in shared and shared[key] != cv:
        nfail["curve_shared"] += 1
        fail_examples.append(("curve_shared", r["cell"], r["c"]))
    shared.setdefault(key, cv)
    p, N, n, rk = r["p"], r["N"], r["n"], r["r"]
    gm = r["gap_meta"]
    T = leastT(rk, n)
    e_r = [0] * (rk - 1) + [1]
    ok_meta = gm["T"] == T and gm["first"] == e_r and gm["enumerated"] <= ht(rk, T)
    if r["status"] == "ok":
        ok_meta &= gm["enumerated"] - gm["duplicate_skips"] - gm["infinity_skips"] == n
        if rk == 1:
            ok_meta &= gm["enumerated"] == n and gm["duplicate_skips"] == 0 and gm["last"] == [n]
        arms = (isinstance(r["null_C"], list) and len(r["null_C"]) == 20 and len(r["null_D"]) == 20
                and all(isinstance(r[k], int) for k in ("gap_C", "gap_D", "plant_C", "plant_D", "plant_m", "plant_internal"))
                and isinstance(r["plant_feasible"], bool))
        if not arms:
            nfail["arms_present"] += 1
            fail_examples.append(("arms_present", r["cell"], r["c"]))
            continue
        pairs = n * (n - 1) // 2
        CD = list(zip(r["null_C"], r["null_D"])) + [(r["gap_C"], r["gap_D"]), (r["plant_C"], r["plant_D"])]
        if not all(1 <= D <= min(pairs, p) for _, D in CD):
            nfail["D_range"] += 1
            fail_examples.append(("D_range", r["cell"], r["c"]))
        if not all(C >= pairs - D for C, D in CD):
            nfail["C_ge_pairs_minus_D"] += 1
            fail_examples.append(("C_ge_pairs_minus_D", r["cell"], r["c"]))
        if not r["plant_C"] >= r["plant_internal"]:
            nfail["plant_C_ge_internal"] += 1
            fail_examples.append(("plant_C_ge_internal", r["cell"], r["c"]))
        if not 4 <= r["plant_m"] <= n // 2:
            nfail["plant_m_range"] += 1
        thr_ok = (200 * r["plant_internal"] >= 3 * sum(r["null_C"])) if r["plant_feasible"] else \
            (r["plant_m"] == n // 2 and 200 * r["plant_internal"] < 3 * sum(r["null_C"]))
        if not thr_ok:
            nfail["plant_feasible_rule"] += 1
            fail_examples.append(("plant_feasible_rule", r["cell"], r["c"]))
    else:
        ok_meta &= gm["enumerated"] == ht(rk, T) and gm["enumerated"] - gm["duplicate_skips"] - gm["infinity_skips"] < n
    if not ok_meta:
        nfail["gap_meta"] += 1
        fail_examples.append(("gap_meta", r["cell"], r["c"]))
    inv = is_prime(p) and p.bit_length() == r["bits"] and is_prime(N) and N != p and (N - p - 1) ** 2 <= 4 * p \
        and (N - 1) // 2 >= n and r["a"] % p and r["b_coef"] % p and (4 * r["a"] ** 3 + 27 * r["b_coef"] ** 2) % p
    if not inv:
        nfail["curve_invariants"] += 1
        fail_examples.append(("curve_invariants", r["cell"], r["c"]))
for k, v in nfail.items():
    check(G, f"{k} over {len(recs)} records", v == 0, v)
arm_note = ("Each record carries one (p, a, b_coef, N, n) shared by its gap, 20 null and planted arms by construction "
            "(one record per (cell, block, c)); the checks above test that all arms are present and consistent with that "
            "n and curve, that every cell at the same bits uses the same curve for the same c (spec: cells at the same bits "
            "share the curve set), and the identities C >= n(n-1)/2 - D (sum_s binom(m_s,2) >= sum_s (m_s - 1)) and "
            "plant_C >= plant_internal (C is monotone under supersets). Regeneration of the arms on the recorded curve is "
            "J2b (recount-sample.json).")

# ------------------------------------------------------------------ raw/summary agreement
G = "raw_summary_agreement"
for rid, fn in (("RUN-PFDR-243425", "analysis-main.json"), ("RUN-PFDR-089edc", "analysis.json")):
    an = jl(os.path.join(RUNS, rid, fn))
    raw = jl(os.path.join(RUNS, rid, "raw-result.json"))
    for k in ("outcome", "headline", "flagged_cells", "calibration", "fraction_valid"):
        check(G, f"{rid} raw-result /summary/{k} == {fn} /{k}", raw["summary"][k] == an[k], [raw["summary"][k], an[k]])
    fl = jl(os.path.join(RUNS, rid, "flags.json"))
    check(G, f"{rid} flags.json == {{flagged_cells: {fn} /flagged_cells}}", fl == {"flagged_cells": an["flagged_cells"]})
    so = open(os.path.join(RUNS, rid, "stdout.log")).read()
    exp_so = (f"outcome {an['outcome']} | headline {an['headline']} | cells {len(an['cells'])} | flagged "
              f"{len(an['flagged_cells'])} | calibration {{'n': {an['calibration']['n']}, 'mean': {an['calibration']['mean']!r}, "
              f"'sd': {an['calibration']['sd']!r}, 'pass': {an['calibration']['pass']}}}\n")
    check(G, f"{rid} stdout.log states the analysis outcome, headline and calibration", so == exp_so)
    check(G, f"{rid} failed_jobs lists exactly the non-ok main records",
          sorted((x["cell"], x["c"], x["status"]) for x in an["failed_jobs"]) ==
          sorted((r["cell"], r["c"], r["status"]) for r in recs if r["status"] != "ok"))
    check(G, f"{rid} stage", an["stage"] == ("main" if fn == "analysis-main.json" else "final"))
raw = jl(os.path.join(RUNS, "RUN-PFDR-4d8c71", "raw-result.json"))
check(G, "census-toy-main /summary jobs == recount", raw["summary"]["jobs"] == len(recs))
check(G, "census-toy-main /summary failed_infrastructure == recount",
      raw["summary"]["failed_infrastructure"] == sum(r["status"].startswith("failed_infrastructure") for r in recs))
check(G, "census-toy-main /summary degenerate == recount", raw["summary"]["degenerate"] == statuses.get("degenerate", 0))
check(G, "census-toy-main invalid_reason states the 4 non-ok jobs",
      raw["invalid_reason"].startswith(f"{sum(r['status'] != 'ok' for r in recs)} jobs"))
rep_path = os.path.join(RUNS, "RUN-PFDR-cd03e2", "toy-rep-jobs.jsonl")
raw = jl(os.path.join(RUNS, "RUN-PFDR-cd03e2", "raw-result.json"))
check(G, "census-toy-rep jobs file empty and /summary all 0", os.path.getsize(rep_path) == 0
      and raw["summary"] == {"degenerate": 0, "failed_infrastructure": 0, "jobs": 0})
check(G, "census-toy-rep read flags.json of analyze-main, which lists no cell",
      jl(os.path.join(RUNS, "RUN-PFDR-243425", "flags.json")) == {"flagged_cells": []})
raw = jl(os.path.join(RUNS, "RUN-PFDR-e44a19", "raw-result.json"))
check(G, "selftest /summary agrees with selftest.json and design.json",
      raw["summary"] == {"cells": len(design["toy_cells"]), "cells_ok": len(design["toy_cells"]), "selftest_pass": st["pass"]}
      and st["pass"] is True and all(c["pass"] for c in st["checks"]) and len(st["checks"]) == 79)

# ------------------------------------------------------------------ independent recomputation of /cells
G = "cells_recomputation"
an = jl(os.path.join(RUNS, "RUN-PFDR-089edc", "analysis.json"))
rows = {r["cell"]: r for r in an["cells"]}


def lfold(xs):
    acc = 0
    for x in xs:
        acc = acc + x
    return acc


def mean_f(xs):
    return float(Fraction(sum(xs), len(xs)))


def var_py(xs):
    """sample variance as the 3.11 statistics module returns it for int data: exact, int if integral else float."""
    n = len(xs)
    mu = Fraction(sum(xs), n)
    v = sum((Fraction(x) - mu) ** 2 for x in xs) / (n - 1)
    return int(v) if v.denominator == 1 else float(v)


def sqrt_cr(q: Fraction) -> float:
    """correctly rounded sqrt of a non-negative rational."""
    r = math.sqrt(float(q))
    for _ in range(4):
        lo, hi = math.nextafter(r, -math.inf), math.nextafter(r, math.inf)
        if Fraction(r) ** 2 < q and (Fraction(r) + Fraction(hi)) ** 2 / 4 < q:
            r = hi
        elif Fraction(r) ** 2 > q and (Fraction(r) + Fraction(lo)) ** 2 / 4 > q:
            r = lo
        else:
            break
    return r


def boot_rng(cell):
    return random.Random(int.from_bytes(hashlib.sha256(f"EXP-PFDR-bb0d26|boot|{cell}|main".encode()).digest(), "big"))


cmp_stats = {"bit_identical": 0, "within_tolerance_only": 0, "out_of_tolerance": 0}
cmp_fail = []
cmp_within = []


def cmpf(cell, field, rec, mine):
    if rec is None or mine is None:
        ok = rec is None and mine is None
        cmp_stats["bit_identical" if ok else "out_of_tolerance"] += 1
        if not ok:
            cmp_fail.append([cell, field, rec, mine])
        return
    if isinstance(rec, (int, float)) and not isinstance(rec, bool) and rec == mine and type(rec) is type(mine):
        cmp_stats["bit_identical"] += 1
    elif math.isclose(rec, mine, rel_tol=REL, abs_tol=ABS):
        cmp_stats["within_tolerance_only"] += 1
        cmp_within.append([cell, field, rec, mine])
    else:
        cmp_stats["out_of_tolerance"] += 1
        cmp_fail.append([cell, field, rec, mine])


mine_rows = []
zc = []
for cell in design["toy_cells"]:
    cid, nc = cell["cell"], cell["n_curves"]
    okc = {}
    for r in recs:
        if r["cell"] == cid and r["status"] == "ok" and 0 <= r["c"] < nc and r["c"] not in okc:
            okc[r["c"]] = r
    row = rows[cid]
    if len(okc) < nc:
        check(G, f"{cid} invalid (fewer ok records than n_curves)", row["cls"] == "invalid" and row["curves"] == len(okc),
              [row["cls"], row["curves"], len(okc)])
        mine_rows.append({"cell": cid, "cls": "invalid", "curves": len(okc)})
        continue
    rs = [okc[c] for c in sorted(okc)]
    k = len(rs)
    means = [mean_f(r["null_C"]) for r in rs]
    dmeans = [mean_f(r["null_D"]) for r in rs]
    gC = [r["gap_C"] for r in rs]
    gD = [r["gap_D"] for r in rs]
    S = sum(gC)
    M = lfold(means)
    V = lfold(var_py(r["null_C"]) for r in rs)
    sd = math.sqrt(V * (1 + 1 / 20))
    Pl = sum(r["plant_C"] for r in rs)
    kappa, z = S / M, (S - M) / sd
    pS = sum(r["null_C"][0] for r in rs)
    pM = lfold(mean_f(r["null_C"][1:]) for r in rs)
    pV = lfold(var_py(r["null_C"][1:]) for r in rs)
    zcal = (pS - pM) / math.sqrt(pV * (1 + 1 / 19))
    fm = lfold(3 * math.comb(r["n"], 4) / r["p"] for r in rs)
    plant_kappa, plant_z = Pl / M, (Pl - M) / sd
    feas = all(r["plant_feasible"] for r in rs)
    d_ratio = sum(gD) / lfold(dmeans)
    rng = boot_rng(cid)
    bk, bd = [], []
    for _ in range(2000):
        idx = [rng.randrange(k) for _ in range(k)]
        m = lfold(means[i] for i in idx)
        md = lfold(dmeans[i] for i in idx)
        if m > 0:
            bk.append(sum(gC[i] for i in idx) / m)
        if md > 0:
            bd.append(sum(gD[i] for i in idx) / md)
    bk.sort()
    bd.sort()
    ci = [bk[int(2.5 / 100 * len(bk))], bk[int(97.5 / 100 * len(bk)) - 1]]
    dci = [bd[int(2.5 / 100 * len(bd))], bd[int(97.5 / 100 * len(bd)) - 1]]
    ev = [i for i, r in enumerate(rs) if r["c"] % 2 == 0]
    od = [i for i, r in enumerate(rs) if r["c"] % 2 == 1]
    ke = sum(gC[i] for i in ev) / lfold(means[i] for i in ev)
    ko = sum(gC[i] for i in od) / lfold(means[i] for i in od)
    powered = M >= 2500
    planted = feas and plant_kappa >= 1.15 and plant_z > 4
    if not powered:
        cls = "inconclusive_underpowered"
    elif not planted:
        cls = "inconclusive_plant_not_recovered"
    elif abs(kappa - 1) >= 0.10 and abs(z) > 4:
        cls = "flagged"
    elif abs(kappa - 1) < 0.05 and 0.90 <= ci[0] and ci[1] <= 1.10:
        cls = "null"
    else:
        cls = "intermediate"
    # exact-rational cross-check of the decisive comparisons (no float in the decision)
    Mx = sum(Fraction(sum(r["null_C"]), 20) for r in rs)
    check(G, f"{cid} powered decided identically in exact arithmetic", (Mx >= 2500) == powered)
    check(G, f"{cid} kappa within tolerance of exact S/M", math.isclose(kappa, float(Fraction(S) / Mx), rel_tol=REL, abs_tol=ABS))
    check(G, f"{cid} S exact", row["S"] == S and isinstance(row["S"], int), [row["S"], S])
    check(G, f"{cid} curves", row["curves"] == k == nc)
    check(G, f"{cid} plant_feasible_all", row["plant_feasible_all"] == feas)
    check(G, f"{cid} class", row["cls"] == cls, [row["cls"], cls])
    check(G, f"{cid} powered / planted_recovered", row["powered"] == powered and row["planted_recovered"] == planted)
    check(G, f"{cid} replication null (not flagged)", row["replication"] is None)
    for fld, val in (("M", M), ("V", V), ("kappa", kappa), ("z", z), ("z_cal", zcal), ("plant_kappa", plant_kappa),
                     ("plant_z", plant_z), ("null_mean_over_formula", M / fm), ("d_ratio", d_ratio),
                     ("kappa_even", ke), ("kappa_odd", ko), ("ci95[0]", ci[0]), ("ci95[1]", ci[1]),
                     ("d_ci95[0]", dci[0]), ("d_ci95[1]", dci[1])):
        rec = row[fld[:-3]][int(fld[-2])] if fld.endswith("]") else row[fld]
        cmpf(cid, fld, rec, val)
    if powered:
        zc.append(zcal)
    mine_rows.append({"cell": cid, "cls": cls, "kappa": kappa, "z": z, "powered": powered, "feas": feas,
                      "nmof": M / fm, "bits": cell["bits"], "r": cell["r"], "n": cell["n"]})
check(G, "/cells count and order", [r["cell"] for r in an["cells"]] == [c["cell"] for c in design["toy_cells"]])
# top level
G = "reading_recomputation"
cal_n = len(zc)
cal_mean = math.fsum(zc) / cal_n
mu = sum(Fraction(x) for x in zc) / cal_n
pvar = sum((Fraction(x) - mu) ** 2 for x in zc) / cal_n
cal_sd = sqrt_cr(pvar)
cal_pass = 0.75 <= cal_sd <= 1.25 and abs(cal_mean) <= 0.35
cmpf("calibration", "mean", an["calibration"]["mean"], cal_mean)
cmpf("calibration", "sd", an["calibration"]["sd"], cal_sd)
check(G, "calibration n and pass", an["calibration"]["n"] == cal_n and an["calibration"]["pass"] == cal_pass,
      [an["calibration"], cal_n, cal_pass])
classes = [r["cls"] for r in mine_rows]
valid = [c for c in classes if c in ("null", "flagged", "intermediate")]
frac = len(valid) / len(classes)
check(G, "fraction_valid bit-identical", an["fraction_valid"] == frac, [an["fraction_valid"], frac])
flagged = [r["cell"] for r in mine_rows if r["cls"] == "flagged"]
check(G, "flagged_cells", an["flagged_cells"] == flagged)
if not cal_pass or frac < 0.5:
    outcome = "O-INVALID"
elif flagged:
    outcome = "O-PENDING-REPLICATION"      # no replication records exist (empty toy-rep-jobs.jsonl)
elif valid and all(c == "null" for c in valid) and frac >= 0.8:
    outcome = "O-NULL"
else:
    outcome = "O-MIXED"
headline = {"O-STRUCT": "FALSIFY_SCOPED", "O-INVALID": "NOT_EVIDENCE", "O-NULL": "SUPPORT_SCOPED"}.get(outcome, "INCONCLUSIVE")
check(G, "outcome by the frozen toy_reading_rules", an["outcome"] == outcome, [an["outcome"], outcome])
check(G, "headline by the frozen headline rules", an["headline"] == headline, [an["headline"], headline])
pw = [r for r in mine_rows if r.get("powered")]
big = max(pw, key=lambda r: abs(r["z"]))
check(G, "largest_abs_z cell", an["largest_abs_z"]["cell"] == big["cell"])
cmpf("largest_abs_z", "z", an["largest_abs_z"]["z"], big["z"])
check(G, "powered_cells", an["powered_cells"] == len(pw))
check(G, "plant_infeasible_cells", an["plant_infeasible_cells"] == [r["cell"] for r in mine_rows if r.get("feas") is False])
check(G, "null_mean_anomalies", an["null_mean_anomalies"] == [r["cell"] for r in mine_rows if "nmof" in r and not 0.8 <= r["nmof"] <= 1.25])
for bits in (20, 24, 28):
    for rk in (1, 2, 3):
        pts = [(math.log2(r["n"]), math.log(r["kappa"])) for r in mine_rows if r["cls"] in ("null", "flagged", "intermediate")
               and r["bits"] == bits and r["r"] == rk and r["kappa"] > 0]
        key = f"b{bits}-r{rk}"
        if len(pts) >= 3:
            mx = math.fsum(t for t, _ in pts) / len(pts)
            my = math.fsum(v for _, v in pts) / len(pts)
            sxx = lfold((t - mx) ** 2 for t, _ in pts)
            cmpf("slope", key, an["secondary_slope_logkappa_per_log2n"].get(key), lfold((t - mx) * (v - my) for t, v in pts) / sxx)
        else:
            check(G, f"slope {key} absent (fewer than 3 valid cells)", key not in an["secondary_slope_logkappa_per_log2n"])
check(G, "reading_note null at O-NULL", an["reading_note"] is None)
check(G, "analysis-main identical to analysis except /stage (compare.py) -- recorded files",
      {k: v for k, v in jl(os.path.join(RUNS, "RUN-PFDR-243425", "analysis-main.json")).items() if k != "stage"}
      == {k: v for k, v in an.items() if k != "stage"})
dist = {}
for c in classes:
    dist[c] = dist.get(c, 0) + 1

out = {"script": "scripts/integrity.py", "python": sys.version, "executable": sys.executable,
       "groups": groups,
       "totals": {"checks": sum(g["checks"] for g in groups.values()), "failures": sum(g["failures"] for g in groups.values())},
       "statuses_in_main_jobs": statuses, "recomputed_class_distribution": dist,
       "descriptive": {"sum_of_job_seconds": seconds_sum, "census_manifest_cpu_seconds": census_m["resources"]["cpu_seconds"],
                       "census_manifest_wall_seconds": census_m["timing"]["wall_seconds"], "workers": 4,
                       "note": "per-job seconds are excluded from determinism; their sum is compared with the census CPU "
                               "and 4 x wall only as a plausibility reading"},
       "float_recomputation": {"method": "exact rationals, explicit left-fold sums, correctly rounded conversions; "
                                         "bootstrap re-implemented from the seeding convention (sha256 'EXP-PFDR-bb0d26|boot|<cell>|main', "
                                         "2000 resamples, randrange(k) k times, percentile indices int(0.025 B) and int(0.975 B) - 1)",
                               "tolerance": {"rel_tol": REL, "abs_tol": ABS}, "counts": cmp_stats,
                               "out_of_tolerance": cmp_fail, "within_tolerance_not_bit_identical": cmp_within[:20]},
       "schema_notes": schema_notes, "arm_comparability_note": arm_note,
       "arm_failure_examples": fail_examples[:20]}
with open(OUT, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(json.dumps(out["totals"]), json.dumps(cmp_stats), dist)
for g, v in groups.items():
    print(g, v["checks"], v["failures"], v["failed"][:3])
print("schema notes", json.dumps(schema_notes)[:600])
