"""Operation-count cost model for decomposed scalar multiplication.

All costs are in base-field multiplications (M).  Every constant lives in
one table with its origin so a reader can replace it and re-run; nothing
here is a measurement.  Formula counts for curve operations are the standard
ones from the Explicit-Formulas Database (EFD, Bernstein-Lange); isogeny
evaluation counts are the x-only Montgomery-model counts used in the SIDH
literature.  Where a constant is a modelling choice rather than a formula
count it is marked ``assumption``.

The model is deliberately simple and conservative in the same direction for
every configuration: interleaved width-w NAF multi-scalar multiplication
with per-generator precomputed tables, generic (not mixed) additions in the
main loop unless affine tables are requested, and endomorphism images
computed once on the base point.  Because the sweeper compares
configurations on the SAME curve and group, systematic bias cancels; only
the relative constants (doubling vs. isogeny step vs. addition) matter, and
those are listed explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import log2


# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------

S_PER_M = 0.8        # assumption: a squaring costs 0.8 M
I_PER_M = 100.0      # assumption: a field inversion costs 100 M (batched where used)

# curve-operation counts (M, S) from the EFD; mixed = one input affine
CURVE_MODELS: dict[str, dict] = {
    "weierstrass_jacobian_a=-3": {
        "note": "EFD dbl-2001-b 3M+5S, add-2007-bl 11M+5S, madd-2007-bl 7M+4S",
        "DBL": (3, 5), "ADD": (11, 5), "mADD": (7, 4),
    },
    "weierstrass_jacobian_a=0": {
        "note": "EFD dbl-2009-l 2M+5S, add-2007-bl 11M+5S, madd-2007-bl 7M+4S",
        "DBL": (2, 5), "ADD": (11, 5), "mADD": (7, 4),
    },
    "weierstrass_jacobian_generic_a": {
        "note": "EFD dbl-2007-bl 1M+8S (general a), add-2007-bl 11M+5S, madd-2007-bl 7M+4S",
        "DBL": (1, 8), "ADD": (11, 5), "mADD": (7, 4),
    },
    "twisted_edwards_a=-1_extended": {
        "note": "EFD dbl-2008-hwcd 4M+4S, add-2008-hwcd-3 8M (a=-1), madd 7M",
        "DBL": (4, 4), "ADD": (8, 0), "mADD": (7, 0),
    },
    "twisted_edwards_a=-1_extended_fp2": {
        "note": "the a=-1 extended counts over F_{p^2}, converted to F_p multiplications with M2 = 3M, S2 = 2M "
                "(DBL 4M2+4S2 = 20M, ADD 8M2 = 24M, mADD 7M2 = 21M)",
        "DBL": (20, 0), "ADD": (24, 0), "mADD": (21, 0),
    },
    "genus2_affine_cantor_counted": {
        "note": "generic Cantor composition+reduction in affine Mumford form as implemented in genus2.py, "
                "operation counts measured there (M, S, I per op; I charged at I_PER_M); an upper bound on "
                "what explicit formulas cost",
        "DBL": (0, 0), "ADD": (0, 0), "mADD": (0, 0),   # filled at import by genus2.install_counted_model()
    },
    "genus2_projective_assumed": {
        "note": "ASSUMPTION: order-of-magnitude projective genus-2 Jacobian counts (DBL 30M+6S, ADD 40M+4S, "
                "mADD 36M+4S) in the range of Lange 2005 / Costello-Lauter 2011 explicit formulas; not verified "
                "in this session -- replace with cited or measured values before relying on absolute numbers",
        "DBL": (30, 6), "ADD": (40, 4), "mADD": (36, 4),
    },
}

# endomorphism evaluation costs in M (base field of the curve)
ENDOMORPHISM_COSTS: dict[str, dict] = {
    "unit": {"M": 1.0, "note": "zeta_3 or i: one constant multiplication of one coordinate"},
    "frobenius_conjugation": {"M": 0.0, "note": "p-power Frobenius on F_{p^2}: conjugation, free"},
    "gls_psi": {"M": 4.0, "note": "assumption: twist-Frobenius-untwist on F_{p^2}, ~2 constant mults in F_{p^2}"},
    "g2_psi": {"M": 6.0, "note": "assumption: untwist-Frobenius-twist on a sextic twist over F_{p^2}: 2 F_{p^2} mults"},
}

# x-only isogeny evaluation per step, (M, S), SIDH-literature counts
ISOGENY_STEP_COSTS: dict[int, tuple[int, int]] = {
    2: (4, 0),     # Costello-Longa-Naehrig 2016 / De Feo-Jao-Plut: 2-isogeny evaluation 4M
    3: (4, 2),     # 3-isogeny evaluation 4M+2S (Costello-Hisil 2017)
    4: (6, 2),     # 4-isogeny evaluation 6M+2S (CLN 2016)
}
ISOGENY_STEP_GENERIC_NOTE = ("odd ell > 3: Costello-Hisil 2017 x-only evaluation 4s M + 2 S "
                             "with s = (ell-1)/2")
ISOGENY_CHAIN_OVERHEAD_M = 20.0   # assumption: y-recovery + model conversions per endomorphism image

# F_{p^2} arithmetic in units of F_p multiplications
M2_PER_M = 3.0   # Karatsuba
S2_PER_M = 2.0   # (a+b)(a-b), 2ab


def isogeny_step_cost(ell: int) -> float:
    if ell in ISOGENY_STEP_COSTS:
        m, s = ISOGENY_STEP_COSTS[ell]
    elif ell % 2 == 1:
        s_ = (ell - 1) // 2
        m, s = 4 * s_, 2
    else:
        # even ell not in the table: chain of 2-isogenies
        k = ell.bit_length() - 1
        if 1 << k != ell:
            raise ValueError(f"no step cost for even non-power-of-two degree {ell}")
        return k * isogeny_step_cost(2)
    return m + S_PER_M * s


def op_cost(model: str, op: str) -> float:
    m, s = CURVE_MODELS[model][op]
    return m + S_PER_M * s


# ---------------------------------------------------------------------------
# configuration and cost
# ---------------------------------------------------------------------------

@dataclass
class Generator:
    """One cheap endomorphism used as a decomposition generator."""
    name: str
    eigenvalue: int           # lambda mod n
    cost_M: float             # cost of one application to a point
    kind: str                 # 'identity' | 'unit' | 'isogeny' | 'frobenius' | 'cycle' | 'product'
    degree: int = 1
    height: int = 1
    detail: dict = field(default_factory=dict)


@dataclass
class ScalarMulCost:
    total_M: float
    doublings: int
    additions: float
    precomp_M: float
    endomorphism_M: float
    window: int
    coeff_bits: int
    dim: int
    breakdown: dict


def multiscalar_cost(coeff_bits: int, gens: list[Generator], model: str,
                     *, affine_tables: bool = True,
                     windows: tuple[int, ...] = (2, 3, 4, 5, 6)) -> ScalarMulCost:
    """Cost of computing sum_i k_i * phi_i(P) with every |k_i| < 2^coeff_bits.

    Interleaved width-w NAF: coeff_bits doublings, d * coeff_bits / (w+1)
    additions on average, and per generator a table of 2^(w-2) odd multiples
    (1 DBL + (2^(w-2) - 1) ADD) plus one endomorphism image of the base
    point (or of the whole table when that is cheaper).  With affine tables
    the main-loop additions are mixed and a batched inversion is charged.
    """
    d = len(gens)
    best: ScalarMulCost | None = None
    DBL, ADD, mADD = (op_cost(model, "DBL"), op_cost(model, "ADD"), op_cost(model, "mADD"))
    for w in windows:
        table = 1 << (w - 2)
        endo = 0.0
        precomp = 0.0
        for g in gens:
            if g.kind == "identity":
                precomp += DBL + (table - 1) * ADD
                continue
            # apply endomorphism to the base point then rebuild the table,
            # or apply it to each table point -- take the cheaper
            once = g.cost_M + DBL + (table - 1) * ADD
            each = g.cost_M * table
            if each < once:
                endo += each
            else:
                endo += g.cost_M
                precomp += DBL + (table - 1) * ADD
        if affine_tables:
            # batched inversion of d * table points: 3M per point + one I
            precomp += 3.0 * d * table + I_PER_M
            loop_add = mADD
        else:
            loop_add = ADD
        doublings = max(coeff_bits - 1, 0)
        additions = d * coeff_bits / (w + 1)
        total = doublings * DBL + additions * loop_add + precomp + endo
        cand = ScalarMulCost(total, doublings, additions, precomp, endo, w, coeff_bits, d,
                             {"DBL": DBL, "loop_add": loop_add, "model": model,
                              "affine_tables": affine_tables})
        if best is None or cand.total_M < best.total_M:
            best = cand
    assert best is not None
    return best


def cycle_pump_cost(ell: int, steps: int) -> float:
    """Cost of one application of a chain of `steps` ell-isogenies."""
    return steps * isogeny_step_cost(ell) + ISOGENY_CHAIN_OVERHEAD_M


def pump_cost_per_height_bit(ell: int) -> float:
    """M per bit of height for a chain of ell-isogenies (height sqrt(ell)/step)."""
    return isogeny_step_cost(ell) / (log2(ell) / 2)
