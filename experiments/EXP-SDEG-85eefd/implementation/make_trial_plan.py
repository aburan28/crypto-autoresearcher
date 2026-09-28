"""Generate trial-plan-v2.json (C-5, C-8, C-9; protocol v4 header fields). Enumerates cells and seed LABELS
only; evaluates no frozen label. Usage: python3 make_trial_plan.py OUT.json"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import decks  # noqa: E402
import fixtures  # noqa: E402
import labels  # noqa: E402

NS = labels.FROZEN_NS
REL = "experiments/EXP-SDEG-85eefd"


def build() -> dict:
    fxs = fixtures.load_fixtures()
    cells, rho_cells, ident = [], [], []
    for fx in fxs:
        L, s = fx["L"], fx["seed"]
        fid = fixtures.fixture_id(fx)
        ident.append({"fixture": fid, "n_tuples": 1000,
                      "label_pattern": labels.cell_lab(NS, "identity", L, s, "<i>", "<field>"),
                      "stop_on_failure": True})
        for deck in decks.DECKS + (decks.CONTROL_DECK,):
            qs = []
            for j in range(decks.N_PLANTED):
                qs.append({"query_id": f"L{L}-s{s}-{deck}-planted-{j:02d}", "kind": "planted", "j": j,
                           "labels": [labels.cell_lab(NS, "planted", L, s, deck, j, k) for k in range(5)],
                           "draw": "r = uniform(label, 2|V|); index = r // 2; sign = +1 if r even else -1"})
            for j in range(decks.N_RANDOM):
                qs.append({"query_id": f"L{L}-s{s}-{deck}-random-{j:02d}", "kind": "random", "j": j,
                           "labels": [labels.cell_lab(NS, "random", L, s, deck, j)],
                           "draw": "k = SHA256(label) mod q; R = k G"})
            cell = {"cell_id": f"{fid}-{deck}", "fixture": fid, "L": L, "seed": s, "p": fx["p"],
                    "q": fx["N"], "deck": deck,
                    "role": "primary" if deck in decks.DECKS else "control_known_structure_positive",
                    "deck_rule": {
                        "interval_x": "smallest L liftable x >= 0",
                        "subgroup_x": "liftable elements of the order-L subgroup of F_p^*",
                        "random_x": f"|V| = |interval_x|; labels {labels.cell_lab(NS, 'random_x', L, s, '<i>')}, "
                                    "i = attempt counter from 0, rejection on non-liftable/duplicate",
                        "progression": "V = x({k G : k = 1..L})"}[deck],
                    "n_queries": len(qs), "backends": ["B0", "B1", "B2"], "oracle": "A5 exhaustive",
                    "b2_sage_crosscheck": L == 8, "queries": qs}
            cells.append(cell)
        rho_cells.append({"fixture": fid, "L": L, "seed": s, "n_targets": 64,
                          "target_labels": [labels.cell_lab(NS, "rho", L, s, t) for t in range(64)],
                          "walk_label_pattern": labels.cell_lab(NS, "rho_walk", L, s, "<t>", "<restart>.<j>{c|d}"),
                          "draw": "k = SHA256(label) mod q; Q = k G"})
    primary = sum(c["n_queries"] for c in cells if c["role"] == "primary")
    control = sum(c["n_queries"] for c in cells if c["role"] != "primary")
    return {
        "trial_plan": "EXP-SDEG-85eefd protocol version 4 (cells unchanged from version 2)",
        "protocol_version": 4,
        "protocol_v4_note": ("AMD-20260928-d3ed9e accepts D-1 and OQ-17..OQ-19 as implemented and adds "
                             "driver fixes FX-1..FX-5; it changes no cell, query, label, draw, threshold, "
                             "statistic or outcome mapping."),
        "protocol_v3_note": ("AMD-20260928-7ce387 changes the analysis (primary W = decision cost, "
                             "W_triple condition, flat tolerance 0.02) and the execution host; it changes "
                             "no cell, query, label or draw, so the plan keeps its v2 file name and the "
                             "frozen label namespace 'EXP-SDEG-85eefd/v2'."),
        "experiment_id": "EXP-SDEG-85eefd",
        "protocol": {
            "specification": f"{REL}/specification.yaml",
            "specification_sha256": fixtures.sha256_file(fixtures.SPECIFICATION),
            "amendment": f"{REL}/amendments/AMD-20260926-3479cf.yaml",
            "amendment_sha256": fixtures.sha256_file(fixtures.AMENDMENT),
            "amendment_v3": f"{REL}/amendments/AMD-20260928-7ce387.yaml",
            "amendment_v3_sha256": fixtures.sha256_file(fixtures.AMENDMENT_V3),
            "amendment_v3_decision": "ledger/decisions/DEC-20260928-6b03c5.yaml",
            "amendment_v4": f"{REL}/amendments/AMD-20260928-d3ed9e.yaml",
            "amendment_v4_sha256": fixtures.sha256_file(fixtures.AMENDMENT_V4),
            "amendment_v4_decision": "ledger/decisions/DEC-20260928-48a648.yaml",
            "fixtures": f"{REL}/amendments/ic_leads_fixtures_v2.json",
            "fixtures_sha256": fixtures.sha256_file(fixtures.FIXTURE_JSON),
            "fixture_generator_sha256": fixtures.sha256_file(fixtures.FIXTURE_GEN),
        },
        "namespace": NS,
        "fixtures": [dict(fx, fixture_id=fixtures.fixture_id(fx)) for fx in fxs],
        "preconditions": {
            "fixture_reproduction": "sage -python ic_leads_fixtures_v2.py byte-identical to frozen JSON (stop on mismatch)",
            "identity_checks": ident,
            "admission_C9": {
                "macos_sage_steps": {"loadavg_15min_max": 14, "system_volume_free_gib_min": 5,
                                     "repo_volume_free_gib_min": 20},
                "linux_pod_charged_cells": {"loadavg_15min_max": "floor(cgroup cpu.max quota/period)",
                                            "run_volume_free_gib_min": 20, "root_free_gib_min": 5}},
        },
        "cells": cells,
        "rho": rho_cells,
        "per_query_watchdog_seconds": 3600,
        "memory_limit_gb": 8, "maximum_workers": 1, "maximum_runs": 1,
        "execution_hosts": {
            "charged": {"host": "RunPod pod (Linux, no Sage)", "maximum_workers": 16,
                        "memory_limit_gb_per_process": 8,
                        "steps": ["identity checks", "B0", "B1", "B2", "B2 split cross-check (no Sage, L=8)",
                                  "A5 oracle", "witness replay", "rho"]},
            "sage": {"host": "repository Mac", "maximum_workers": 1,
                     "steps": ["fixture reproduction (C-1)", "B2 literal FGLM cross-check (L=8)"]},
            "merge": {"host": "repository Mac", "steps": ["consistency checks", "accounting audit",
                                                          "metrics", "outcome mapping"]}},
        "accounting_audit": {"fraction": 0.10,
                             "selection": f"lowest ceil(10%) of SHA256('{NS}|audit|<query_id>') over primary+control queries"},
        "bootstrap": {"resamples": 2000, "label": labels.lab(NS, "bootstrap")},
        "totals": {"fixtures": len(fxs), "cells": len(cells),
                   "primary_cells": sum(1 for c in cells if c["role"] == "primary"),
                   "primary_queries_per_backend": primary, "control_queries_per_backend": control,
                   "rho_targets": 64 * len(fxs)},
    }


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "trial-plan-v2.json"
    plan = build()
    out.write_text(json.dumps(plan, indent=1, sort_keys=True) + "\n")
    print(json.dumps(plan["totals"]))
