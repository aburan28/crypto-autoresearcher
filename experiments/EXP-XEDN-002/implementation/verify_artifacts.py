#!/usr/bin/env python3
"""EXP-XEDN-002 artifact self-check (completion gate, not a measurement).

This script performs no new experiment. It reads the immutable run records and
checks the four mechanical parts of the executor completion gate:

  1. every run directory holds exactly the six required filenames;
  2. every manifest carries the required non-empty keys, with field_bits <= 32
     so the claim tier stays toy;
  3. the closed forms recorded by arm A agree with an INDEPENDENT recomputation
     written here from the derivation (this file imports nothing from
     xedn2_lib.py, so a bug in the shared library cannot hide);
  4. every number printed in the analysis.md tables is present, to the printed
     precision, in the raw-result.json of the run that produced it.

Exit status 0 means all checks passed. Any failure prints FAIL lines and exits 1.
It writes no artifact and consumes no run slot.

Usage:  python3 experiments/EXP-XEDN-002/implementation/verify_artifacts.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction
from math import log

import yaml

EXP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS_DIR = os.path.join(EXP_DIR, "runs")

REQUIRED_FILES = {
    "manifest.yaml", "command.txt", "environment.json",
    "stdout.log", "stderr.log", "raw-result.json",
}

PRIMES = [5, 7, 11, 13, 101, 211, 431, 809]
HIST_PRIMES = [5, 7, 11, 13]

failures: list[str] = []
checks = 0


def check(ok: bool, label: str, detail: str = "") -> None:
    global checks
    checks += 1
    if ok:
        print(f"  ok   {label}")
    else:
        failures.append(f"{label}: {detail}")
        print(f"  FAIL {label}  {detail}")


# ------------------------------------------------------- independent closed form
# Re-derived here directly from derivation.md sections 1.3-1.5, deliberately not
# imported: N_slots counts (b, x) pairs with deg b = 6 exactly and x monic
# quadratic; N_hit counts those pairs the frozen predicate accepts.

def ind_n_slots(p: int) -> int:
    return (p - 1) * p ** 8


def ind_q_pred(p: int) -> int:
    """Hits per fixed x: pairs (y squarefree, nonzero) with deg(y^2 - x^3) = 6."""
    return (p ** 4 - 3 * p ** 3 + 2 * p ** 2 + p - 1) // 2


def ind_n_hit(p: int) -> int:
    return p ** 2 * ind_q_pred(p)


def ind_p_lift(p: int) -> Fraction:
    return Fraction(ind_n_hit(p), ind_n_slots(p))


def ind_alpha_eff(p1: int, p2: int) -> float:
    return -log(float(ind_p_lift(p2)) / float(ind_p_lift(p1))) / log(p2 / p1)


# ---------------------------------------------------------------- 1. file layout

print("[1] run directory layout")
run_ids = sorted(os.listdir(RUNS_DIR))
check(len(run_ids) > 0, "runs directory non-empty", str(run_ids))
for rid in run_ids:
    d = os.path.join(RUNS_DIR, rid)
    present = {f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))}
    check(present == REQUIRED_FILES, f"{rid} has exactly the six required files",
          f"missing={sorted(REQUIRED_FILES - present)} extra={sorted(present - REQUIRED_FILES)}")
    check(re.fullmatch(r"RUN-XEDN-002-[A-Z0-9]+", rid) is not None,
          f"{rid} matches the run-id convention")

# ------------------------------------------------------------- 2. manifest schema

print("[2] manifest schema")
MANIFEST_PATHS = [
    ("id",), ("experiment_id",), ("purpose",), ("status",),
    ("code", "commit"), ("code", "dirty_tree"), ("code", "command"),
    ("code", "entrypoint"),
    ("environment", "python"), ("environment", "os"),
    ("environment", "packages", "numpy"), ("environment", "packages", "sympy"),
    ("environment", "cpu_count"), ("environment", "memory_gb"),
    ("inputs", "parameters", "field_bits"),
    ("inputs", "parameters", "primes"),
    ("inputs", "parameters", "surface_family"),
    ("inputs", "parameters", "section_shape"),
    ("inputs", "parameters", "predicate"),
    ("inputs", "seeds"),
    ("timing", "started_at"), ("timing", "finished_at"),
    ("timing", "wall_clock_seconds"), ("timing", "peak_memory_mb"),
    ("result", "validity"), ("result", "validity_reason"),
    ("result", "certificate", "kind"), ("result", "summary"),
    ("inference", "requested_policy"), ("inference", "resolved_model"),
    ("inference", "reasoning_effort"), ("inference", "fallback_used"),
    ("inference", "fallback_reason"),
]

manifests: dict[str, dict] = {}
for rid in run_ids:
    with open(os.path.join(RUNS_DIR, rid, "manifest.yaml")) as fh:
        doc = yaml.safe_load(fh)
    check(isinstance(doc, dict) and "run" in doc, f"{rid} manifest has top-level 'run'")
    run = doc["run"]
    manifests[rid] = run
    missing = []
    for path in MANIFEST_PATHS:
        node = run
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
            if node is None:
                break
        empty = node is None or (not isinstance(node, bool) and
                                 not isinstance(node, (int, float)) and not node)
        if empty:
            missing.append(".".join(path))
    check(not missing, f"{rid} manifest keys all present and non-empty", str(missing))
    check(run["id"] == rid, f"{rid} manifest id matches directory name", str(run["id"]))
    check(run["experiment_id"] == "EXP-XEDN-002", f"{rid} experiment_id")
    fb = run["inputs"]["parameters"]["field_bits"]
    check(isinstance(fb, int) and fb <= 32, f"{rid} field_bits={fb} keeps the tier toy")
    check(run["result"]["certificate"]["kind"] == "none",
          f"{rid} certificate.kind is none (no solve, no relation claimed)")
    with open(os.path.join(RUNS_DIR, rid, "command.txt")) as fh:
        cmd_txt = fh.read()
    check(run["code"]["command"].strip() in cmd_txt,
          f"{rid} command.txt contains the manifest command")

# ------------------------------------------- 3. independent closed-form agreement

print("[3] arm A closed forms vs independent recomputation")
arm_a_run = "RUN-XEDN-002-A2"
with open(os.path.join(RUNS_DIR, arm_a_run, "raw-result.json")) as fh:
    raw_a = json.load(fh)
table_a = {row["p"]: row for row in raw_a["arm_a_table"]}
check(sorted(table_a) == sorted(PRIMES), "arm A covers the contracted prime list",
      str(sorted(table_a)))
for p in PRIMES:
    row = table_a[p]
    check(row["N_slots"] == ind_n_slots(p), f"N_slots({p})",
          f"{row['N_slots']} != {ind_n_slots(p)}")
    check(row["N_hit"] == ind_n_hit(p), f"N_hit({p})",
          f"{row['N_hit']} != {ind_n_hit(p)}")
    exact = Fraction(row["P_lift_exact"])
    check(exact == ind_p_lift(p), f"P_lift({p}) exact rational",
          f"{exact} != {ind_p_lift(p)}")
    check(abs(row["P_lift_float"] - float(ind_p_lift(p))) <= 1e-15 * float(ind_p_lift(p)) + 1e-300,
          f"P_lift({p}) float")
    # exact identity 2 p^3 P_lift = 1 - 2/p + p^-3, derivation.md 1.5
    ident = Fraction(1) - Fraction(2, p) + Fraction(1, p ** 3)
    check(2 * p ** 3 * ind_p_lift(p) == ident, f"identity 2p^3*P_lift at p={p}")
for rec in raw_a["alpha_eff_consecutive_all_sizes"]:
    got, want = rec["alpha_eff"], ind_alpha_eff(rec["p1"], rec["p2"])
    check(abs(got - want) < 1e-12, f"alpha_eff {rec['p1']}->{rec['p2']}", f"{got} != {want}")
    check(want < 3.0, f"alpha_eff {rec['p1']}->{rec['p2']} strictly below the limit 3")
check(raw_a["limiting_alpha"] == 3, "limiting alpha recorded as 3")
check(raw_a["derivation_self_checks_all_pass"] is True, "arm A derivation self-checks pass")

print("[3b] arm B and arm C totals vs the same closed form")
with open(os.path.join(RUNS_DIR, "RUN-XEDN-002-B", "raw-result.json")) as fh:
    raw_b = json.load(fh)
check(raw_b["arm_a_b_agree_at_every_enumerated_size"] is True,
      "arm B reports exact agreement on every enumerated slice")
bad_units = [u for u in raw_b["per_unit_results"] if u["hits_frozen"] != ind_q_pred(u["p"])]
check(not bad_units,
      f"all {len(raw_b['per_unit_results'])} arm B x-marginals equal the independent Q(p)",
      str([(u["p"], u["x"], u["hits_frozen"]) for u in bad_units[:5]]))
disagreeing = [u for u in raw_b["per_unit_results"]
               if u["frozen_vs_reference_disagreements"] != 0
               or u["hits_ref_predicate_semantics"] != u["hits_frozen"]]
check(not disagreeing, "zero frozen-vs-independent disagreements on every arm B marginal",
      str([(u["p"], u["x"]) for u in disagreeing[:5]]))
for p_str, comp in raw_b["comparison_with_arm_a"].items():
    p = int(p_str)
    check(comp["agrees_with_closed_form"] is True, f"arm B p={p} agrees with closed form")
    check(comp["hits_frozen_observed"] == comp["closed_form_for_enumerated_slice"],
          f"arm B p={p} observed == closed form for the enumerated slice",
          f"{comp['hits_frozen_observed']} != {comp['closed_form_for_enumerated_slice']}")
    check(comp["closed_form_per_x"] == ind_q_pred(p),
          f"arm B p={p} per-x closed form equals independent Q(p)={ind_q_pred(p)}")
    check(comp["x_invariance_holds"] is True and len(comp["distinct_per_x_hit_counts"]) == 1,
          f"arm B p={p} hit count is x-invariant",
          str(comp["distinct_per_x_hit_counts"]))
    full = comp.get("full_space_verified_with_frozen_predicate", False)
    if p in [5, 7]:
        check(full is True, f"arm B p={p} full slot space verified")
        check(comp["full_space_N_hit_observed"] == ind_n_hit(p),
              f"arm B full-space total at p={p} equals N_hit",
              f"{comp['full_space_N_hit_observed']} != {ind_n_hit(p)}")
        check(p in raw_b["full_slot_space_exhausted_at"], f"p={p} listed as fully exhausted")
    else:
        check(full is False, f"arm B p={p} NOT claimed as full-space verified", str(full))
        check(p in raw_b["b_marginals_only_at"],
              f"p={p} listed as b-marginals only, not as exhaustive")
check(raw_b["total_slots_enumerated"] == sum(u["slots"] for u in raw_b["per_unit_results"]),
      "arm B slot total equals the sum of its marginals")

with open(os.path.join(RUNS_DIR, "RUN-XEDN-002-C", "raw-result.json")) as fh:
    raw_c = json.load(fh)
hist = {rec["p"]: rec for rec in raw_c["monic_x_frozen_semantics"]}
check(sorted(hist) == HIST_PRIMES, "arm C covers p = 5, 7, 11, 13", str(sorted(hist)))
for p in HIST_PRIMES:
    rec = hist[p]
    check(rec["hit_slots_total"] == ind_n_hit(p),
          f"arm C hit-slot total at p={p} equals N_hit",
          f"{rec['hit_slots_total']} != {ind_n_hit(p)}")
    check(rec["section_points_total"] == 2 * rec["hit_slots_total"],
          f"arm C points = 2 x slots at p={p}")
    check(rec["all_point_counts_even"] is True, f"arm C per-surface point counts even at p={p}")
    check(rec["n_surfaces"] == (p - 1) * p ** 6, f"arm C surface count at p={p}")
    at_least = rec["at_least_s_slots"]
    fracs = [at_least[str(s)]["fraction"] for s in range(1, 10)]
    check(all(fracs[i] >= fracs[i + 1] for i in range(8)),
          f"arm C P[>= s] monotone non-increasing at p={p}", str(fracs))
    check(fracs[8] <= 1.0 / p, f"arm C P[>= 9] <= 1/p at p={p}",
          f"{fracs[8]} vs {1.0 / p}")
check(raw_c["all_totals_match_closed_form"] is True, "arm C totals match closed form flag")
check(raw_c["largest_completed_size"] == 13, "arm C largest completed size is 13")
check(raw_c["sizes_skipped"] == [], "arm C skipped no size", str(raw_c["sizes_skipped"]))

with open(os.path.join(RUNS_DIR, "RUN-XEDN-002-CTRL", "raw-result.json")) as fh:
    raw_ctrl = json.load(fh)
expected_verdicts = {
    "control_1_frozen_predicate": "pass",
    "control_2_planted_section": "pass",
    "control_3_smoke_consistency": "pass",
    "control_4_isotriviality": "discharged_with_finding",
    "control_5_degenerate_section": "pass",
}
check(raw_ctrl["verdicts"] == expected_verdicts, "control verdicts as reported",
      json.dumps(raw_ctrl["verdicts"]))

# ------------------------------------------- 4. analysis.md tables vs raw results

print("[4] analysis.md tables vs raw-result.json")


def cells(line: str) -> list[str]:
    return [c.strip().strip("*").strip("`").strip().replace(",", "").replace("**", "")
            for c in line.strip().strip("|").split("|")]


with open(os.path.join(EXP_DIR, "analysis.md")) as fh:
    md_lines = fh.readlines()

seen_plift, seen_hist, seen_alpha, seen_armb = 0, 0, 0, 0
for line in md_lines:
    if not line.lstrip().startswith("|"):
        continue
    c = cells(line)
    # P_lift table: p | N_slots | N_hit | exact | float | 2p^3 P
    if len(c) == 6 and c[0].isdigit() and int(c[0]) in PRIMES and "/" in c[3]:
        p = int(c[0])
        row = table_a[p]
        seen_plift += 1
        check(int(c[1]) == row["N_slots"], f"analysis.md N_slots({p})")
        check(int(c[2]) == row["N_hit"], f"analysis.md N_hit({p})")
        check(Fraction(c[3]) == Fraction(row["P_lift_exact"]), f"analysis.md P_lift({p}) exact")
        check(abs(float(c[4]) - row["P_lift_float"]) <= 5e-7 * row["P_lift_float"],
              f"analysis.md P_lift({p}) float", f"{c[4]} vs {row['P_lift_float']}")
    # alpha_eff row
    if len(c) == 8 and c[0] == "alpha_eff":
        seen_alpha += 1
        recs = raw_a["alpha_eff_consecutive_all_sizes"]
        check(len(recs) == 7, "seven consecutive alpha_eff records")
        for got, rec in zip(c[1:], recs):
            check(abs(float(got) - rec["alpha_eff"]) <= 5e-7,
                  f"analysis.md alpha_eff {rec['p1']}->{rec['p2']}",
                  f"{got} vs {rec['alpha_eff']}")
    # arm C table: s | p=5 | p=7 | p=11 | p=13
    if len(c) == 5 and c[0].isdigit() and 1 <= int(c[0]) <= 9:
        s = int(c[0])
        seen_hist += 1
        for got, p in zip(c[1:], HIST_PRIMES):
            want = hist[p]["at_least_s_slots"][str(s)]["fraction"]
            check(abs(float(got) - want) <= 5e-7 * max(want, 1e-9),
                  f"analysis.md P[>= {s}] at p={p}", f"{got} vs {want}")
    # arm B coverage table: p | mode | x | slots | pct | frozen hits | closed form | agree
    if len(c) == 8 and c[0].isdigit() and int(c[0]) in HIST_PRIMES and c[-1] == "yes":
        p = int(c[0])
        seen_armb += 1
        comp = raw_b["comparison_with_arm_a"][str(p)]
        check(int(c[5]) == comp["hits_frozen_observed"],
              f"analysis.md arm B frozen hits at p={p}", c[5])
        check(int(c[3]) == comp["slots_enumerated"],
              f"analysis.md arm B slots enumerated at p={p}", c[3])

check(seen_plift == len(PRIMES), "all 8 P_lift rows cross-checked", str(seen_plift))
check(seen_alpha == 1, "alpha_eff row cross-checked", str(seen_alpha))
check(seen_hist == 9, "all 9 arm C rows cross-checked", str(seen_hist))
check(seen_armb == 4, "all 4 arm B coverage rows cross-checked", str(seen_armb))

# quoted criteria must be verbatim from the frozen specification
with open(os.path.join(EXP_DIR, "specification.yaml")) as fh:
    spec = yaml.safe_load(fh)["experiment"]
md = "".join(md_lines)


def flat(text: str) -> str:
    return " ".join(text.replace("*", "").replace("`", "").replace(">", "").split())


for key in ("success_criterion", "falsification_criterion"):
    check(flat(spec[key]) in flat(md), f"analysis.md quotes {key} verbatim")

# --------------------------------------------------- 5. reproduction spot-check

if "--reproduce" in sys.argv:
    print("[5] reproduction spot-check: re-executing recorded work at this revision")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import arm_a_closed_form as A                                    # noqa: E402
    import arm_b_exhaustive as B                                     # noqa: E402
    import arm_c_histogram as C                                      # noqa: E402

    redo_a = {row["p"]: row for row in A.arm_a_table()}
    check(redo_a == table_a, "arm A table reproduces byte-identically",
          str([p for p in table_a if redo_a.get(p) != table_a[p]]))

    # arm B: the cheapest recorded marginals, one per fully exhausted size
    for p in [5, 7]:
        rec = next(u for u in raw_b["per_unit_results"] if u["p"] == p)
        x0, x1 = rec["x"][0], rec["x"][1]
        redo = B.enumerate_marginal((p, x0, x1))
        same = all(redo[k] == rec[k] for k in
                   ("slots", "hits_frozen", "hits_ref_predicate_semantics",
                    "hits_true_square", "frozen_vs_reference_disagreements"))
        check(same, f"arm B marginal p={p} x={rec['x']} reproduces",
              f"{ {k: redo[k] for k in ('slots', 'hits_frozen')} }")
    # the recorded arm-B x lists are seeded, so the plan itself must reproduce
    for p, k in B.MARGINAL_PLAN.items():
        want = raw_b["planned_coverage"][str(p)]["x_list"]
        got = [[x0, x1, 1] for (x0, x1) in B.x_slice(p, k)]
        check(got == want, f"arm B seeded x list at p={p} reproduces", str(got))

    # arm C: the two smallest sizes, re-fibered from scratch
    for p in [5, 7]:
        _, ysq, nonzero, sf = C.all_y(p)
        _, X3 = C.all_x(p, True)
        cen = C.census(p, True, nonzero & sf, ysq, X3)
        redo = C.summarize(p, cen["counts"], cen["pairs"], True,
                           "frozen_predicate_semantics")
        rec = hist[p]
        # json turns the integer s keys into strings; compare through json
        same = all(json.loads(json.dumps(redo[k])) == rec[k] for k in
                   ("n_surfaces", "hit_slots_total", "section_points_total",
                    "max_slots_on_a_surface", "histogram_slots_per_surface",
                    "at_least_s_slots"))
        check(same, f"arm C census p={p} reproduces",
              f"{ {k: redo[k] for k in ('hit_slots_total', 'max_slots_on_a_surface')} }")
else:
    print("[5] reproduction spot-check skipped (pass --reproduce to run it)")

print()
print(f"{checks} checks, {len(failures)} failures")
if failures:
    print("FAILURES:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ARTIFACT SELF-CHECK PASSED")
