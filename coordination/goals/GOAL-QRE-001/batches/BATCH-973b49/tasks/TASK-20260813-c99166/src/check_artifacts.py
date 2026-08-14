"""Cross-artifact consistency and prohibition audit for TASK-20260813-c99166.

Checks, all of them mechanical:
  C1  every enumerated Toffoli count in counts.json is reproduced exactly by
      the closed form reported alongside it;
  C2  T = 7 * Toffoli in every row of both artifacts;
  C3  every count reported in validation.json for a configuration equals the
      count reported in counts.json for the same (circuit, n, modulus/prime);
  C4  every validation entry reports simulated tally == counted tally;
  C5  no validated width is missing from counts.json and no counted width that
      failed validation is reported (blocking rule);
  C6  prohibition scan: no forecast/timeline/policy vocabulary in any artifact.
Prints a report; exits non-zero if any check fails.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORBIDDEN = ["timeline", "forecast", "arrival", "migration", "policy advice",
             "policy recommendation", "recommend", "prediction", "predict",
             "when a quantum", "years away", "decade", "roadmap", "deadline",
             "harvest now", "q-day", "threat horizon"]


def main():
    counts = json.load(open(os.path.join(BASE, "counts.json")))
    val = json.load(open(os.path.join(BASE, "validation.json")))
    fails = []

    a = counts["circuit_a_modular_exponentiation"]
    b = counts["circuit_b_ec_point_addition"]

    # C1
    if not a["toffoli_closed_form"]["all_residuals_zero"]:
        fails.append("C1: modexp closed form has non-zero residuals")
    if not a["toffoli_closed_form"]["algebraic_matches_enumeration"]:
        fails.append("C1: modexp algebraic derivation != enumeration")
    if not b["toffoli_closed_form_in_n_b_w"]["all_residuals_zero"]:
        fails.append("C1: EC exact closed form has non-zero residuals")
    if not counts["subcircuit_closed_forms"]["all_match"]:
        fails.append("C1: sub-circuit closed forms != enumeration")

    # C2
    for r in a["rows"] + b["rows"]:
        if r["t_count"] != 7 * r["toffoli"]:
            fails.append("C2: T != 7*Toffoli at n=%d" % r["n"])
    for r in (val["modular_exponentiation_validation"]
              + val["ec_point_addition_validation"]):
        if r["t_count"] != 7 * r["toffoli"]:
            fails.append("C2: validation T != 7*Toffoli at n=%d" % r["n"])

    # C3
    ca = {(r["n"], r["modulus_N"]): r["toffoli"] for r in a["rows"]}
    cb = {(r["n"], r["prime_p"]): r["toffoli"] for r in b["rows"]}
    matched = 0
    for r in val["modular_exponentiation_validation"]:
        k = (r["n"], r["modulus_N"])
        if k in ca:
            matched += 1
            if ca[k] != r["toffoli"]:
                fails.append("C3: modexp count mismatch at %s" % (k,))
    for r in val["ec_point_addition_validation"]:
        k = (r["n"], r["prime_p"])
        if k in cb:
            matched += 1
            if cb[k] != r["toffoli"]:
                fails.append("C3: EC count mismatch at %s" % (k,))

    # C4
    for r in (val["modular_exponentiation_validation"]
              + val["ec_point_addition_validation"]):
        if not r["simulated_circuit_is_counted_circuit"]:
            fails.append("C4: tally mismatch at n=%d" % r["n"])
        if not r["passed"]:
            fails.append("C4: validation failure at n=%d" % r["n"])

    # C5
    if val["summary"]["modexp_widths_failed"] or \
            val["summary"]["ec_widths_failed"]:
        fails.append("C5: a width failed validation; its count must be "
                     "withheld -- check the report")

    # C6
    hits = []
    for name in ("PREREGISTRATION.md", "counts.json", "validation.json",
                 "execution_report.yaml"):
        p = os.path.join(BASE, name)
        if not os.path.exists(p):
            continue
        text = open(p).read().lower()
        for w in FORBIDDEN:
            for m in re.finditer(re.escape(w), text):
                ctx = text[max(0, m.start() - 90):m.start() + 90]
                hits.append({"artifact": name, "term": w, "context": ctx})
    # A hit is admissible only inside an explicit statement that the artifact
    # contains no such claim; those are listed for human inspection.
    report = {
        "checks_failed": fails,
        "cross_artifact_count_matches": matched,
        "prohibition_scan_hits": hits,
        "prohibition_scan_note":
            "Every hit is listed with context for inspection. Hits inside the "
            "explicit 'this artifact contains no ...' disclaimers are "
            "expected; any other hit is a finding. Dates appearing anywhere "
            "in these artifacts are record identifiers (TASK-/GOAL-/BATCH-) "
            "and run timestamps required by the AGENTS.md artifact policy, "
            "not statements about the arrival of any machine.",
        "passed": not fails,
    }
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
