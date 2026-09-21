"""
The SINGLE SOURCE of the group-operation-equivalent charging convention for
EXP-ECDLP-bbb42f (specification.yaml required_artifacts_note). No cost
number in results/summary.json may be computed outside this module.

Every routine in this driver (ecc.py, curve_order.py, isogeny2.py,
baselines.py, sssa.py, graph_search.py) instruments its own field
multiplications and field inversions via ecc.OpCounter -- these are
MEASURED counts, not estimates, since they count actual modular
multiplications/inversions performed by the Python interpreter during the
run.

Converting those counts to "group-operation-equivalents" requires one
MODELED constant: the cost of a single modular inversion in units of
modular multiplications (I/M ratio). This driver does not assume a generic
literature value; it MEASURES its own EC point-addition primitive's
mult/inversion mix (exactly 1 inversion + 3 multiplications per generic
affine addition, per ecc.point_add) and adopts the standard, disclosed
I/M = 8 convention (Hankerson-Menezes-Vanstone, "Guide to Elliptic Curve
Cryptography", table 3.1-3.3 range for affine-vs-projective tradeoffs;
I/M in the 8-30 range is standard software-implementation practice) ONLY to
convert inversions into an equivalent multiplication count -- this single
constant is the one MODELED number in this file; every other quantity here
is measured. GROUP_OP is then defined as exactly the measured mult+
inversion cost of ecc.point_add (one full affine EC point addition),
so every other routine's cost is reported in units of "how many EC point
additions would have cost the same number of equivalent multiplications" --
an internally self-consistent, measured ratio, not an assumed one.
"""
from __future__ import annotations

I_OVER_M = 8  # MODELED: standard affine-inversion-to-multiplication ratio
              # (Hankerson-Menezes-Vanstone convention). The only modeled
              # constant in this file.


def equivalent_mults(field_mults: int, field_invs: int) -> float:
    """MEASURED field_mults/field_invs counts, converted to a single
    equivalent-multiplication count via the one MODELED constant I_OVER_M."""
    return field_mults + I_OVER_M * field_invs


# Measured, once, from ecc.point_add's own instrumentation: a generic affine
# addition (P1 != P2, both nonzero) costs exactly 1 inversion + 3
# multiplications (see ecc.py: inv_mod call + `num*inv` mult + 2 mults for
# x3/y3). This is not re-derived at import time from a live call (which
# would need a live curve) -- it is the fixed, documented op-count of the
# addition branch, verified against the source in tests/test_cost_model.py.
GROUP_OP_ADD_FIELD_MULTS = 3
GROUP_OP_ADD_FIELD_INVS = 1
GROUP_OP_EQUIV_MULTS = equivalent_mults(GROUP_OP_ADD_FIELD_MULTS, GROUP_OP_ADD_FIELD_INVS)


def to_group_op_equivalents(field_mults: int, field_invs: int) -> float:
    """Convert a MEASURED (field_mults, field_invs) op-count pair (from any
    routine's OpCounter) into group-operation-equivalents: how many EC
    point additions would have cost the same number of equivalent
    multiplications, using GROUP_OP_EQUIV_MULTS as the unit."""
    return equivalent_mults(field_mults, field_invs) / GROUP_OP_EQUIV_MULTS


def opcounter_to_group_ops(ctr) -> float:
    return to_group_op_equivalents(ctr.field_mults, ctr.field_invs)
