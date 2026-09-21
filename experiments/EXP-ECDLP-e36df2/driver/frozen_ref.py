"""Read-only import shim onto EXP-ECDLP-a26bde's frozen driver modules.

Per TASK-20260911-9df234 / EXP-ECDLP-e36df2 specification.yaml
inputs.instrument: "The Executor ... MUST reuse or adapt (never modify in
place) experiments/EXP-ECDLP-a26bde/driver/instrument.py's padic.pmul,
split_point, teichmuller_lift_scalar and teichmuller_section -- either by
importing them read-only from the frozen module, or by copying the exact
function bodies into the new driver with a comment naming the source and
commit."

This module takes the import route: it inserts a26bde's driver/ directory
onto sys.path (read-only; no file under experiments/EXP-ECDLP-a26bde/ is
ever opened for writing here or anywhere else in this new driver) and
re-exports the frozen names needed. Source pin: commit
f177b8a4e9e50d042f6699391e651335f65c67e3 (last commit touching
instrument.py / curves.py as of this experiment's authoring), repo HEAD
3ebc071b95c9e9220b84b47ba5f09c0bb3980804 at the start of this run.
"""
from __future__ import annotations

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.join(_THIS_DIR, "..", "..", "..")
_A26BDE_DRIVER = os.path.join(_REPO_ROOT, "experiments", "EXP-ECDLP-a26bde", "driver")

for _p in (os.path.abspath(_REPO_ROOT), os.path.abspath(_A26BDE_DRIVER)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Frozen modules, imported read-only (never written to).
import padic  # noqa: E402
import instrument  # noqa: E402
import exactcurve  # noqa: E402
import curves as a26bde_curves  # noqa: E402
from formalgroup import FormalGroup  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

# Names this new driver reuses unmodified, per the specification's explicit
# list (padic.pmul, split_point, teichmuller_lift_scalar, teichmuller_section)
# plus the supporting pieces those functions need to be called correctly.
pmul = padic.pmul
padd = padic.padd
pdbl = padic.pdbl
pneg = padic.pneg
is_identity = padic.is_identity
to_tw = padic.to_tw
to_affine = padic.to_affine
normalize_proj = padic.normalize_proj
O_PROJ = padic.O_PROJ

split_point = instrument.split_point
torsion_section = instrument.torsion_section
reduce_point_mod = instrument.reduce_point_mod
reduce_fraction_mod = instrument.reduce_fraction_mod
eval_series_mod = instrument.eval_series_mod
valuation_modp = instrument.valuation_modp
hensel_lift_sqrt = instrument.hensel_lift_sqrt
teichmuller_lift_scalar = instrument.teichmuller_lift_scalar
teichmuller_section = instrument.teichmuller_section
hensel_lift_point = instrument.hensel_lift_point
curve_lift_projective = instrument.curve_lift_projective
_exponent = instrument._exponent
AnomalousBreak = instrument.AnomalousBreak
PrecisionInsufficient = instrument.PrecisionInsufficient
PRECISION_MARGIN = instrument.PRECISION_MARGIN

find_primes_for_curve = a26bde_curves._find_primes_for_curve
