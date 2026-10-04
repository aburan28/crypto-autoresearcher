"""Write trial-plan-v2.json: both attempt budgets (A1, A2) at all nine frozen
fixtures, with every control, label template and protocol hash. Label
strings are listed, never evaluated (no frozen draw is taken before an
admitted run). L and |S| are fixture properties computed with the uncharged
verifier arithmetic.

  python3 make_trial_plan.py [--out trial-plan-v2.json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fixtures
import labels
from audit import scan_set
from vcurve import VCurve

HERE = Path(__file__).resolve().parent
PROTOCOL_VERSION = 2
REPLICATES = 32
RHO_TARGETS = 64


def protocol_hashes() -> dict:
    return {"specification_sha256": fixtures.sha256_file(fixtures.SPECIFICATION),
            "amendment_sha256": fixtures.sha256_file(fixtures.AMENDMENT),
            "fixtures_sha256": fixtures.sha256_file(fixtures.FIXTURE_JSON),
            "fixture_generator_sha256": fixtures.sha256_file(fixtures.FIXTURE_GEN)}


def build() -> dict:
    ns = labels.FROZEN_NS
    fx_rows, cells = [], []
    for f in fixtures.load_fixtures():
        prm = fixtures.params(f)
        vc = VCurve(f["p"], f["a"], f["b"])
        S = scan_set(vc, prm["B2"])
        L = sum(1 for x in range(prm["B"]) if vc.lift_canonical(x) is not None)
        fid = fixtures.fixture_id(f)
        b, s = f["bits"], f["seed"]
        fx_rows.append({"fixture_id": fid, "bits": b, "seed": s, "p": f["p"], "q": f["N"],
                        "a": f["a"], "b": f["b"], "G": f["G"], "B": prm["B"], "B2": prm["B2"],
                        "L": L, "scan_size": len(S), "A1": prm["A1"], "A2": prm["A2"],
                        "generator_process": {"attempts": prm["A2"], "a1_prefix": prm["A1"]},
                        "target_label": labels.target_label(ns, b, s),
                        "attempt_label_template": labels.attempt_label(ns, b, s, "<j>") + "|{a,b}",
                        "rho_target_labels": [labels.lab(ns, "rho", b, s, t) for t in range(RHO_TARGETS)],
                        "audit_label_template": labels.lab(ns, "audit", b, s, "<j>"),
                        "horton_minimum_basis": b in (16, 20),
                        "expected_scan_group_ops_A2": prm["A2"] * len(S)})
        for budget in ("A1", "A2"):
            ctx = f"{b}|{s}|{budget}"
            cells.append({
                "cell_id": f"{fid}-{budget}", "fixture_id": fid, "budget": budget,
                "attempts": prm[budget],
                "controls": {
                    "rewire_labels": [f"{labels.rewire_label(ns, i)}|{ctx}|<draw>" for i in range(REPLICATES)],
                    "er_labels": [labels.lab(ns, "er", i, ctx) + "|<draw>" for i in range(REPLICATES)],
                    "planted_label": labels.lab(ns, "planted", ctx) + "|<draw>",
                    "scramble_label": labels.lab(ns, "scramble", ctx) + "|<draw>",
                    "known_positive_gate": "delta_proof > 1/4 on planted-dense graph (cycle rank ceil(|V|^1.5))",
                    "known_false_gate": "scrambled (a_j,b_j) must fail LP log recovery verification",
                    "accounting_audit": "SHA256-selected ~10% replay + completeness + charge formula + all certificates"}})
    order = sorted(fx_rows, key=lambda r: (r["expected_scan_group_ops_A2"], r["fixture_id"]))
    return {"experiment_id": fixtures.EXP_ID, "protocol_version": PROTOCOL_VERSION,
            "protocol": protocol_hashes(), "namespace": ns,
            "frozen_fixture_json_sha256": fixtures.FROZEN_JSON_SHA256,
            "budgets": {"A1": "ceil(q^{1/2})", "A2": "ceil(q^{3/5}); prefix-continuation of A1"},
            "replicates": {"rewire": REPLICATES, "erdos_renyi": REPLICATES},
            "rho_targets_per_fixture": RHO_TARGETS,
            "fixtures": fx_rows, "cells": cells,
            "execution_order": [r["fixture_id"] for r in order],
            "execution": {"one_fresh_process_per_fixture": True, "workers": 1,
                          "memory_limit_gib": 8, "nice": 10,
                          "stop_on_first_procedure_defect": True,
                          "horton_bits": [16, 20],
                          "admission": "explicit decision with execution_admission.currently_admitted true "
                                       "and target_ids containing EXP-RELN-c5a377; C-7 readings pass"},
            "analysis": "analysis.py (C-5 verdict rule, verbatim with the literal readings in implementation.md)"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "trial-plan-v2.json"))
    a = ap.parse_args(argv)
    Path(a.out).write_text(json.dumps(build(), indent=1, sort_keys=True) + "\n")
    print(a.out, fixtures.sha256_file(a.out))


if __name__ == "__main__":
    main()
