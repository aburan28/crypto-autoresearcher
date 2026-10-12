"""Part 2 scoring surface: per-conjugate-family rank readout scaffolding.

Exposes:
  - packaging_surface(): dry stage metadata / basis names
  - score_part2(...): callable Part 2 scoring API shape for a later /run

Full curve builds / rank matrices are heavy and may be stubbed with
status: not_executed_on_scoring_impl_card on this card. The path must remain
importable and wired so a later /run can invoke it. No AUXIN/FROB/QSP values.
No RUN-* minting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


BASIS_NAMES: List[str] = [
    "raw_class",
    "raw_point",
    "orbit_quotient",
    "ker_g",
]

CONTROLS_DECLARED: List[str] = [
    "CTL-PLANTED",
    "CTL-FIXTURE",
    "CTL-FORCED-NEGATIVE",
    "CTL-ADMISSION-SELFTEST",
    "CTL-INSTRUMENT-SELFTEST",
    "null_object",
    "non_stable_subspace",
]

CERTIFICATES_DECLARED: List[str] = [
    "CERT-LABEL",
    "CERT-QUOT",
    "CERT-BIND",
]

GATES_DECLARED: List[str] = ["G0", "G1", "G2", "G3", "G4"]

TOY_N_POSITIVE: List[int] = [17, 23, 31, 41]
TOY_N_FORCED_NEGATIVE: List[int] = [19, 29, 37]
TOY_N_MAX: int = 41


def score_part2(
    ns: Optional[Sequence[int]] = None,
    *,
    execute_curve_builds: bool = False,
    write_artifacts: bool = False,
) -> Dict[str, Any]:
    """Part 2 four-basis rank readout scoring API (scaffolding).

    Declares bases, controls, certificates, gates, and toy n≤41 scope. Full
    curve builds and rank matrices remain stubbed unless execute_curve_builds
    is True AND a later scientific /run supplies the heavy dependencies.

    On the scoring-impl card, leave execute_curve_builds=False so the result
    carries status: not_executed_on_scoring_impl_card.
    """
    if write_artifacts:
        raise ValueError(
            "write_artifacts=True is forbidden on the scoring-impl path; "
            "artifact writes belong to a later authorized /run under runs/"
        )
    ns_list = list(TOY_N_POSITIVE if ns is None else ns)
    for n in ns_list:
        if n > TOY_N_MAX:
            raise ValueError(
                f"Part 2 toy scope is n<={TOY_N_MAX}; refused n={n}"
            )

    base: Dict[str, Any] = {
        "module": "part2_surface",
        "stage": "P2_rank_readout",
        "scientific_scoring": bool(execute_curve_builds),
        "write_artifacts": False,
        "runs_minted": False,
        "bases": list(BASIS_NAMES),
        "controls_declared": list(CONTROLS_DECLARED),
        "certificates_declared": list(CERTIFICATES_DECLARED),
        "gates_declared": list(GATES_DECLARED),
        "toy_n_positive": list(TOY_N_POSITIVE),
        "toy_n_forced_negative": list(TOY_N_FORCED_NEGATIVE),
        "ns_requested": ns_list,
        "cells": [],
        "ranks": [],
        "ok": True,
    }

    if not execute_curve_builds:
        base["status"] = "not_executed_on_scoring_impl_card"
        base["note"] = (
            "Part 2 scoring path importable and wired. Bases/controls/"
            "certificates/gates declared. Curve builds and four-basis rank "
            "matrices stubbed on the scoring-impl card; a later /run may set "
            "execute_curve_builds=True after dependencies are available."
        )
        # Structured empty cell placeholders for each requested n × a∈{0,1}.
        for n in ns_list:
            for a in (0, 1):
                base["cells"].append(
                    {
                        "n": n,
                        "a": a,
                        "status": "not_executed_on_scoring_impl_card",
                        "bases": list(BASIS_NAMES),
                        "ranks": None,
                    }
                )
        return base

    # Heavy path reserved for a later scientific /run with curve libraries.
    base["status"] = "curve_builds_requested_but_unavailable"
    base["ok"] = False
    base["problems"] = [
        "execute_curve_builds=True requires curve/order libraries not admitted "
        "on this stdlib-only typed/ tree; keep stubbed or extend under a later "
        "amendment that admits the dependency"
    ]
    base["note"] = (
        "Scoring API entered the curve-build branch but the stdlib-only "
        "typed/ tree cannot build Koblitz cells here. Stub remains the "
        "supported path until a dependency amendment."
    )
    return base


def packaging_surface() -> Dict[str, Any]:
    """Dry packaging probe: stage metadata and basis names only."""
    # Capability smoke: call score_part2 in stub mode (no curve builds).
    stub = score_part2(ns=[17], execute_curve_builds=False)
    ok = stub.get("status") == "not_executed_on_scoring_impl_card" and stub.get(
        "ok", False
    )
    return {
        "module": "part2_surface",
        "stage": "P2_rank_readout",
        "status": "packaging_probe_with_scoring_api",
        "scientific_scoring": False,
        "score_part2_callable": True,
        "bases": list(BASIS_NAMES),
        "controls_declared": list(CONTROLS_DECLARED),
        "certificates_declared": list(CERTIFICATES_DECLARED),
        "gates_declared": list(GATES_DECLARED),
        "stub_smoke": {
            "status": stub.get("status"),
            "ok": stub.get("ok"),
            "bases": stub.get("bases"),
            "cell_count": len(stub.get("cells") or []),
        },
        "ok": bool(ok),
        "note": (
            "Packaging surface + score_part2 API present. Part 2 rank readout "
            "(toy cells n<=41) is not executed here; invoke score_part2 via "
            "run.py --run --score-part2 on a later authorized /run."
        ),
    }
