#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-a8efe2 / TASK-20261001-f5e965.

BEFORE any Stage 1 encode:
  - dual-modulus exhibit at n=9
  - preregistered predictions commit
  - basis-type census from binary-curve-params.txt
  - primary-text reverify checklist for m in {233,283,409,571} sect*r1/r2
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gf2n import (
    N,
    PENTANOMIAL_MOD,
    TRINOMIAL_MOD,
    is_irreducible,
    poly_to_string,
    weight,
)
from runpack import EXP_ROOT, REPO_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-54aa8c"
CURVE_PARAMS = REPO_ROOT / "analysis/binstd-curve-audit/binary-curve-params.txt"
REVERIFY_M = [233, 283, 409, 571]


def dual_modulus_exhibit() -> dict:
    tri_ok, tri_det = is_irreducible(TRINOMIAL_MOD)
    pent_ok, pent_det = is_irreducible(PENTANOMIAL_MOD)
    # Also record that the design-session candidate matches the frozen pentanomial.
    design_cand = (1 << 9) | (1 << 4) | (1 << 2) | (1 << 1) | 1
    return {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 0,
        "n": N,
        "trinomial": {
            "poly": poly_to_string(TRINOMIAL_MOD),
            "modulus_int": TRINOMIAL_MOD,
            "modulus_hex": hex(TRINOMIAL_MOD),
            "weight": weight(TRINOMIAL_MOD),
            "irreducible": tri_ok,
            "rabin_details": tri_det,
        },
        "pentanomial": {
            "poly": poly_to_string(PENTANOMIAL_MOD),
            "modulus_int": PENTANOMIAL_MOD,
            "modulus_hex": hex(PENTANOMIAL_MOD),
            "weight": weight(PENTANOMIAL_MOD),
            "irreducible": pent_ok,
            "rabin_details": pent_det,
            "design_session_candidate": "x^9 + x^4 + x^2 + x + 1",
            "matches_design_session_candidate": design_cand == PENTANOMIAL_MOD,
            "note": "Re-verified irreducible; frozen as Stage-0 pentanomial exhibit.",
        },
        "both_irreducible": bool(tri_ok and pent_ok),
        "naive_term_count_ratio_modeled": {
            "label": "MODELED",
            "value": 5 / 3,
            "note": (
                "Naive 5-vs-3 reduction-term ratio is a MODELED first guess "
                "expected to be a POOR predictor of measured clause_width_ratio; "
                "never mixed into measured columns."
            ),
        },
    }


def preregistered_predictions() -> dict:
    return {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 0,
        "committed_before_stage1": True,
        "committed_at": utc_now(),
        "heuristics": ["HEUR-BINSTD-340284-H1", "HEUR-BINSTD-340284-H2"],
        "predictions": {
            "A_axis_purity_N_leaf": {
                "quantity": "leaf_or_solution_count_ratio (pentanomial/trinomial)",
                "interval": [0.95, 1.05],
                "claim_tier": "observational",
            },
            "B_clause_width_direction": {
                "quantity": "clause_width_ratio (pentanomial/trinomial, F-set)",
                "direction": "> 1",
                "modeled_naive_guess": {
                    "label": "MODELED",
                    "value": 5 / 3,
                    "note": "Poor predictor; separate from measured ratios.",
                },
            },
            "C_unmatched_relabelling": {
                "quantity": "discriminator_unmatched_effect on N_leaf / solution-count",
                "expectation": "large effect vs real-basis arm (instrument power check)",
            },
            "D_width_matched_relabelling": {
                "quantity": "discriminator_width_matched_ratio",
                "interval": [0.9, 1.1],
            },
            "E_certificate_equality": {
                "quantity": "certificate_set_equality at Stage 1",
                "expectation": "true (brute-force verified)",
            },
        },
        "measured_vs_modeled": (
            "Clause-width histograms, substitution-variable counts, solution "
            "multisets, wall_s, peak_rss are MEASURED. Naive 5-vs-3 is MODELED."
        ),
        "source": (
            "IDEA-20260922-9d12bd; H-BINSTD-340284; "
            "analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-9d12bd.yaml"
        ),
    }


def parse_census(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"===== (sect\S+) =====", text)
    rows = []
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        bt = re.search(r"Basis Type:\s*(\S+)", body)
        m_bit = re.search(r"\((\d+) bit\)", body)
        # Named degree from curve id when present (sectNNNk1 / sectNNNr1)
        named = re.match(r"sect(\d+)([kr]\d+)", name)
        named_m = int(named.group(1)) if named else None
        poly_lines = []
        in_poly = False
        for line in body.splitlines():
            if line.strip().startswith("Polynomial:"):
                in_poly = True
                rest = line.split(":", 1)[1].strip()
                if rest:
                    poly_lines.append(rest)
                continue
            if in_poly:
                if line.startswith("=====") or line.startswith("EC-") or line.startswith("Field") or line.startswith("Basis") or line.startswith("Element"):
                    break
                if line.strip():
                    poly_lines.append(line.strip())
                else:
                    break
        rows.append(
            {
                "curve_id": name,
                "named_field_degree": named_m,
                "ec_parameters_bit_label": int(m_bit.group(1)) if m_bit else None,
                "basis_type": bt.group(1) if bt else None,
                "polynomial_excerpt": " ".join(poly_lines)[:200] if poly_lines else None,
                "source": str(path.relative_to(REPO_ROOT)),
                "claim_strength": "SECONDARY_until_primary_text_verified",
            }
        )
    pp = [r for r in rows if r["basis_type"] == "ppBasis"]
    tp = [r for r in rows if r["basis_type"] == "tpBasis"]
    by_type = {"ppBasis": len(pp), "tpBasis": len(tp), "other": len(rows) - len(pp) - len(tp)}
    return {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 0,
        "source": str(path.relative_to(REPO_ROOT)),
        "grep_method": "split on ===== sect* ===== headers; read Basis Type field",
        "n_rows": len(rows),
        "census_pp_vs_tp_rows": by_type,
        "rows": rows,
        "note": (
            "Census rows from the OpenSSL audit dump are SECONDARY until "
            "primary-text checklist items are marked verified."
        ),
    }


def reverify_checklist(census: dict) -> dict:
    items = []
    for row in census["rows"]:
        m = row["named_field_degree"]
        cid = row["curve_id"]
        if m not in REVERIFY_M:
            continue
        if not re.search(r"r[12]$", cid):
            # still flag k1 siblings at those degrees as informational
            role = "informational_k_sibling"
        else:
            role = "required_reverify"
        bit_label = row["ec_parameters_bit_label"]
        degree_mismatch = bit_label is not None and m is not None and bit_label != m
        items.append(
            {
                "curve_id": cid,
                "named_field_degree": m,
                "ec_parameters_bit_label": bit_label,
                "basis_type_from_dump": row["basis_type"],
                "role": role,
                "primary_text_sources": [
                    "FIPS 186-4 Appendix D (or successor)",
                    "ANSI X9.62",
                ],
                "status": "needs_primary_text_check",
                "degree_label_mismatch_in_dump": degree_mismatch,
                "mismatch_note": (
                    f"Dump EC-Parameters bit label {bit_label} != named degree {m}"
                    if degree_mismatch
                    else None
                ),
                "verified_by": None,
                "verified_at": None,
            }
        )
    required = [i for i in items if i["role"] == "required_reverify"]
    return {
        "experiment_id": "EXP-BINSTD-a8efe2",
        "task_id": "TASK-20261001-f5e965",
        "stage": 0,
        "reverify_flag_m": REVERIFY_M,
        "primary_text_reverify_checklist_complete": False,
        "complete_note": (
            "Checklist ARTIFACT is complete (all flagged rows listed). "
            "Primary-text VERIFICATION of each row remains open "
            "(status=needs_primary_text_check). HOLD-I defect 3."
        ),
        "n_required_rows": len(required),
        "n_informational_rows": len(items) - len(required),
        "items": items,
        "asserts_nothing_about": "H1/H2 mathematics; encoder Stages 1–3",
    }


def main() -> int:
    t0 = time.perf_counter()
    started = utc_now()
    dual = dual_modulus_exhibit()
    preds = preregistered_predictions()
    census = parse_census(CURVE_PARAMS)
    checklist = reverify_checklist(census)

    dump_yaml(EXP_ROOT / "stage0" / "dual-modulus-n9.yaml", dual)
    dump_yaml(EXP_ROOT / "stage0" / "preregistered-predictions.yaml", preds)
    dump_yaml(EXP_ROOT / "stage0" / "basis-type-census.yaml", census)
    dump_yaml(EXP_ROOT / "stage0" / "primary-text-reverify-checklist.yaml", checklist)

    wall = time.perf_counter() - t0
    finished = utc_now()
    metrics = {
        "both_irreducible": dual["both_irreducible"],
        "census_pp_vs_tp_rows": census["census_pp_vs_tp_rows"],
        "primary_text_reverify_checklist_complete": checklist[
            "primary_text_reverify_checklist_complete"
        ],
        "checklist_artifact_written": True,
        "predictions_committed_before_stage1": True,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    stdout = (
        f"Stage 0 complete\n"
        f"  trinomial irreducible: {dual['trinomial']['irreducible']} ({dual['trinomial']['poly']})\n"
        f"  pentanomial irreducible: {dual['pentanomial']['irreducible']} ({dual['pentanomial']['poly']})\n"
        f"  census rows: {census['n_rows']} pp={census['census_pp_vs_tp_rows']['ppBasis']} "
        f"tp={census['census_pp_vs_tp_rows']['tpBasis']}\n"
        f"  reverify required rows: {checklist['n_required_rows']}\n"
        f"  predictions committed BEFORE Stage 1\n"
    )
    write_run_package(
        RUN_ID,
        stage=0,
        arm="stage0-dual-modulus-census",
        seed=None,
        command="python3 experiments/EXP-BINSTD-a8efe2/implementation/stage0_run.py",
        parameters={"n": 9, "reverify_flag_m": REVERIFY_M},
        metrics=metrics,
        valid=bool(dual["both_irreducible"]),
        invalid_reason=None if dual["both_irreducible"] else "modulus_not_irreducible",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none"},
    )
    print(stdout)
    return 0 if dual["both_irreducible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
