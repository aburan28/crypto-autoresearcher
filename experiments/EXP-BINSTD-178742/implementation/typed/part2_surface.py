"""Part 2 packaging surface: per-conjugate-family rank readout (FUTURE).

Declares the four-basis rank surface for later authorized execution. Does NOT
build curves, mint RUN-*, or score any rank row. No AUXIN/FROB/QSP values.
"""

from __future__ import annotations

from typing import Any, Dict, List


BASIS_NAMES: List[str] = [
    "raw_class",
    "raw_point",
    "orbit_quotient",
    "ker_g",
]


def packaging_surface() -> Dict[str, Any]:
    """Dry packaging probe: stage metadata and basis names only."""
    return {
        "module": "part2_surface",
        "stage": "P2_rank_readout",
        "status": "future_execution_stage",
        "scientific_scoring": False,
        "bases": list(BASIS_NAMES),
        "controls_declared": [
            "CTL-PLANTED",
            "CTL-FIXTURE",
            "CTL-FORCED-NEGATIVE",
            "CTL-ADMISSION-SELFTEST",
            "CTL-INSTRUMENT-SELFTEST",
            "null_object",
            "non_stable_subspace",
        ],
        "ok": True,
        "note": (
            "Packaging surface only. Part 2 rank readout (toy cells n<=41, "
            "certificates CERT-LABEL/CERT-QUOT/CERT-BIND, gates G0-G4) is a "
            "FUTURE execution stage and is not run here."
        ),
    }
