#!/usr/bin/env python3
"""Stage 0: HOLD-S lattice + citation re-reads + conversion + notation lock."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import EXP_ROOT, dump_text, dump_yaml, peak_rss_bytes, utc_now, write_run_package
from soundness import ord_n_of_2, stable_dimensions, verify_ord_n_2

RUN_ID = "RUN-BINSTD-f9fb37"

FIPS_N = [163, 233, 283, 409, 571]
TOY_N = [17, 23, 29, 31, 37, 41]
FORBIDDEN_MEASUREMENT = [29, 37, 163]


def build_lattice() -> dict:
    rows = []
    for n in FIPS_N + TOY_N:
        d = ord_n_of_2(n)
        ok = verify_ord_n_2(n, d)
        stab = stable_dimensions(n, d)
        row = {
            "n": n,
            "family": "FIPS_Koblitz" if n in FIPS_N else "toy",
            "ord_n_2": d,
            "ord_verified": ok,
            "phi_factor_count": stab["phi_factor_count"],
            "phi_factor_degree": stab["phi_factor_degree"],
            "stable_dimensions": stab["stable_dimensions"],
            "mid_dimensions": stab["mid_dimensions"],
            "mid_lane_empty": stab["mid_lane_empty"],
            "forbidden_as_measurement_cell": n in FORBIDDEN_MEASUREMENT,
            "label": "RECOMPUTED",
        }
        rows.append(row)
    empty_flags = {
        163: next(r["mid_lane_empty"] for r in rows if r["n"] == 163),
        29: next(r["mid_lane_empty"] for r in rows if r["n"] == 29),
        37: next(r["mid_lane_empty"] for r in rows if r["n"] == 37),
    }
    return {
        "experiment_id": "EXP-BINSTD-38e4ad",
        "task_id": "TASK-20261001-b78ef3",
        "stage": 0,
        "notation": {"n": "field_degree", "m": "Semaev_arity", "l": "window_dimension"},
        "method": (
            "ord_n(2) = least d|(n-1) with 2^d ≡ 1 (mod n); mid-dimensions are "
            "stable dims excluding {0,1,n-1,n}; empty mid-lane <=> Phi_n irreducible "
            "over F_2 (d=n-1)."
        ),
        "rows": rows,
        "lattice_empty_flags": {
            "n_163_mid_empty": empty_flags[163],
            "n_29_mid_empty": empty_flags[29],
            "n_37_mid_empty": empty_flags[37],
            "all_required_empty": all(empty_flags.values()),
        },
        "forbidden_measurement_cells": FORBIDDEN_MEASUREMENT,
        "prior_comparator_8fe0ef": {
            "label": "MODELED/PRIOR",
            "note": (
                "IDEA-20260915-8fe0ef stated 163:none mid; 233:29k; 283:94k; "
                "409:204k; 571:114k; toys 17/23/31/41 mid; 29/37 empty. "
                "Stage 0 RECOMPUTES; prior is comparator only."
            ),
        },
        "no_deployed_curve_break_claimed": True,
        "no_fixed_target_satisfiability_claim": True,
    }


CITATION_NOTES = """# Citation re-read notes — EXP-BINSTD-38e4ad Stage 0

Task: `TASK-20261001-b78ef3`. HOLD-S. Observations/documentation only.
No deployed-curve break claim. No fixed-target orbit-clause satisfiability claim.

Re-read in full (claim sections and mechanism) of the three title-only citations
named by IDEA-20260922-2a3771 / HOLD-S review Step 1. Distinctions vs the
HOLD-S-corrected H1 (soundness null under a77711 A1/A2) are recorded below.

## IDEA-20260904-3c7a91

- **Title/claim axis:** PDP CNF-XOR model admits no above-leaf pruning; conflict
  count ≈ 2^{m l}/|G|; solver engineering cannot move the search exponent.
- **Object:** leaf-completeness / unit-propagation structure of the descended
  Semaev CNF, independent of Frobenius.
- **Distinction vs corrected H1:** 3c7a91 is about *solver pruning of one PDP
  instance*. Corrected H1 is about whether *coordinate squaring is a symmetry of
  one fixed-target solution set* (it is not: A1 maps solutions to the conjugate
  instance). No shared claim that orbit clauses on one CNF are
  satisfiability-preserving. Citation is background on leaf enumeration, not a
  soundness warrant for fixed-target Frobenius clauses.

## IDEA-20260915-eee7e4

- **Title/claim axis:** Side-constrained core — add `x_i ∈ x(E)` per block to
  shrink leaves from |V|^m to |V ∩ x(E)|^m ≈ 2^{m(l-1)} without losing
  E-decompositions (constant-factor, no exponent move).
- **Object:** E-membership / twist-side filter on the factor-base alphabet.
- **Distinction vs corrected H1:** eee7e4 is a *sound* local alphabet filter
  (side bit). Corrected H1 rejects treating Frobenius orbit equivalence as a
  *sound filter on one fixed R*. H2 in this packet (membership orbit-collapse on
  a tau-stable V) is preprocessing-only counting, not the eee7e4 solver-side
  constraint. Do not conflate E-side blocking clauses with tau-orbit clauses.

## IDEA-20260920-b9f0c5

- **Title/claim axis:** WDSat conflict audit on Frobenius-invariant factor bases
  at n=41 (cheap) / n=43 (decisive) vs null 2^{m l}/m!; basis-blind vs first
  pruning.
- **Object:** Whether an *invariant V* prunes SAT search on one fixed R,
  residual after a77711 closed invariant-ring rewriting.
- **Distinction vs corrected H1:** b9f0c5 *assumes* the factor base is
  tau-stable and asks a *search* question (conflicts vs orbit-naive null). This
  packet's corrected H1 asks the prior *soundness* question (A1/A2) at n=17 via
  exhaustive group-arithmetic census — not WDSat. Stage 1 primary instrument is
  the census; SAT is out of Stage 1 scope. b9f0c5 does not license fixed-target
  orbit-equivalence CNF clauses.

## Summary

| Citation   | Lives in                          | Supports fixed-target orbit CNF? |
|------------|-----------------------------------|----------------------------------|
| 3c7a91     | leaf-completeness / no pruning    | No                               |
| eee7e4     | E-side alphabet filter            | No                               |
| b9f0c5     | WDSat on invariant V vs null      | No (different question)          |
| corrected H1 | a77711 A1/A2 soundness census   | Explicitly under test as UNSOUND |

`citation_reread_complete: true`
"""

CONVERSION_NOTE = """# Conversion-cost note — EXP-BINSTD-38e4ad Stage 0 (HOLD-S)

Polynomial-basis ↔ normal-basis conversion for F_{2^n} is charged **O(n²) bit
operations once** (build the change-of-basis matrix once; apply as needed).

HOLD-S correction:
- This cost is a rounding error against any decomposition / relation-search
  budget at the scales considered in this lane.
- It is **recorded here once** and **dropped from the title and priority
  argument** of H-BINSTD-c3d68f / EXP-BINSTD-38e4ad.
- On ECC2K-130 the challenge is already in a type-II ONB (KN-LIT-661e97 prior
  pointer); access cost is zero there — cited as prior only, not re-derived.

`conversion_cost_note_present: true`
`label: DOCUMENTATION`
`no_priority_use: true`
"""

NOTATION_LOCK = """# Notation lock — EXP-BINSTD-38e4ad (HOLD-S)

| Symbol | Meaning                         | Forbidden overload                          |
|--------|----------------------------------|---------------------------------------------|
| **n**  | Field extension degree (=\\|⟨τ⟩\\| on Koblitz) | Never use n for Semaev arity                |
| **m**  | Semaev / decomposition arity     | Never use m for \\|⟨τ⟩\\| or field degree     |
| **l**  | Factor-base / window dimension  | —                                           |
| **V**  | Window subspace of F_{2^n}      | —                                           |
| **τ**  | Absolute Frobenius (x ↦ x²)      | —                                           |

Frozen Stage 1 cell: **n=17**, **m=2**, **l=8**.

Source IDEA-20260922-2a3771 mixed n/m in places; this experiment and all
artifacts under `experiments/EXP-BINSTD-38e4ad/` obey the lock above.
"""


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage0 = EXP_ROOT / "stage0"
    stage0.mkdir(parents=True, exist_ok=True)

    lattice = build_lattice()
    dump_yaml(stage0 / "lattice.yaml", lattice)
    dump_text(stage0 / "citation-reread-notes.md", CITATION_NOTES)
    dump_text(stage0 / "conversion-cost-note.md", CONVERSION_NOTE)
    dump_text(stage0 / "notation-lock.md", NOTATION_LOCK)

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "lattice_empty_flags": lattice["lattice_empty_flags"],
        "citation_reread_complete": True,
        "conversion_cost_note_present": True,
        "notation_lock_present": True,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    lines = [
        f"stage0 lattice empty flags: {lattice['lattice_empty_flags']}",
        f"rows: {len(lattice['rows'])}",
        "artifacts: lattice.yaml citation-reread-notes.md conversion-cost-note.md notation-lock.md",
        "no deployed-curve break claim; no fixed-target satisfiability claim",
    ]
    write_run_package(
        RUN_ID,
        stage=0,
        arm="lattice_citations",
        seed=None,
        command="python3 experiments/EXP-BINSTD-38e4ad/implementation/stage0_run.py",
        parameters={
            "curve_id": None,
            "fips_n": FIPS_N,
            "toy_n": TOY_N,
            "forbidden_measurement_cells": FORBIDDEN_MEASUREMENT,
        },
        metrics=metrics,
        valid=bool(lattice["lattice_empty_flags"]["all_required_empty"]),
        invalid_reason=None
        if lattice["lattice_empty_flags"]["all_required_empty"]
        else "required empty mid-lane flags failed",
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note="Stage 0 measurement/documentation only; certificate.kind=none",
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
