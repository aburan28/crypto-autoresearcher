"""EXP-DREG-001 §11 — the degree-3 syzygy, extracted and identified.

The graded deficit at D=3 is exactly 1 for every full system. This probe extracts
that single syzygy from the left kernel of the degree-3 Macaulay matrix, with row
provenance (which generator, which monomial multiplier), and shows it is a
PRODUCT / shared-factor relation

    ( sum_{i in S} q_i ) * ( L ) = 0 ,   L affine

by (a) checking every participating generator carries the SAME multiplier set, and
(b) verifying the product vanishes identically in the Boolean ring.

Also runs the support-matched null as a control: the null has NO degree-3 syzygy.

The supports (S, L) are coordinate-dependent — they vary with n and the random R —
while the COUNT is exactly 1. That combination (robust dimension, coordinate-
dependent generators) is the signature of a graded Betti number.

Run:
  DOT_SAGE=experiments/EXP-DREG-001/runtime/sage TMPDIR=/Volumes/Volume/tmp \
  sage -python experiments/EXP-DREG-001/characterization/syzygy_degree3.py \
       --n-list 12,15,18
"""
import argparse
import itertools
import sys
from pathlib import Path

CODE = (Path(__file__).resolve().parent.parent
        / "runs" / "RUN-DREG-001-VALIDATE-N12-A" / "code")
sys.path.insert(0, str(CODE))

from sage.all import GF, BooleanPolynomialRing, matrix  # noqa: E402
from h012_peel_rank import build_system, boolean_null  # noqa: E402
from ic_first_fall_fast import multiply, mono_deg  # noqa: E402

F2 = GF(2)
D = 3


def macaulay_with_provenance(gens, nb, D):
    """Degree-<=D Macaulay rows, remembering (generator index, multiplier) per row."""
    rows, info = [], []
    for gi, f in enumerate(gens):
        fdeg = max(mono_deg(m) for m in f)
        if fdeg > D:
            continue
        for md in range(0, D - fdeg + 1):
            for combo in itertools.combinations(range(nb), md):
                prod = multiply(f, frozenset(combo))
                if prod and max(mono_deg(m) for m in prod) <= D:
                    rows.append(prod)
                    info.append((gi, combo))
    cols = sorted(set().union(*rows), key=lambda m: (mono_deg(m), tuple(sorted(m))))
    colidx = {m: i for i, m in enumerate(cols)}
    M = matrix(F2, len(rows), len(cols), sparse=True)
    for ri, prod in enumerate(rows):
        for m in prod:
            M[ri, colidx[m]] = 1
    return M, info


def analyze(n, t, ti, seed):
    built = build_system(n, t, ti, seed)
    if built is None:
        print(f"n={n}: build_system failed")
        return
    rng, nb, gens, eq_degs = built
    print(f"\n=== n={n} nb={nb} ({eq_degs.count(2)} quadric, {eq_degs.count(3)} cubic) ===")

    # control: support-matched null
    Mn, _ = macaulay_with_provenance(boolean_null(gens, nb, rng), nb, D)
    print(f"  NULL control: degree-3 left-kernel dim = {Mn.left_kernel().dimension()}"
          f"  (expect 0)")

    M, info = macaulay_with_provenance(gens, nb, D)
    K = M.left_kernel()
    print(f"  SEM: {M.nrows()} rows x {M.ncols()} cols, rank={M.rank()},"
          f" left-kernel dim = {K.dimension()}  (= graded deficit at D=3)")

    B = BooleanPolynomialRing(nb, "z")
    z = B.gens()

    def to_poly(monoset):
        p = B.zero()
        for m in monoset:
            term = B.one()
            for v in m:
                term *= z[v]
            p += term
        return p

    for vi, v in enumerate(K.basis()):
        by_gen = {}
        for i in v.support():
            gi, combo = info[i]
            by_gen.setdefault(gi, set()).add(combo)
        mult_sets = list(by_gen.values())
        common = mult_sets[0]
        factors = all(s == common for s in mult_sets)
        gdeg = {gi: max(mono_deg(m) for m in gens[gi]) for gi in by_gen}
        S = sorted(by_gen)
        lvars = sorted({x for c in common for x in c})
        has_const = () in common
        print(f"  -- syzygy #{vi}: {len(v.support())} rows,"
              f" {len(S)} generators (quadrics={sum(1 for g in S if gdeg[g] == 2)},"
              f" cubics={sum(1 for g in S if gdeg[g] == 3)})")
        print(f"     shared multiplier set across ALL generators? {factors}")
        if not factors:
            continue
        print(f"     L = {'1 + ' if has_const else ''}"
              f"{' + '.join('z%d' % j for j in lvars)}   (|L support| = {len(lvars)})")
        Q = B.zero()
        for gi in S:
            Q += to_poly(gens[gi])
        L = B.one() if has_const else B.zero()
        for j in lvars:
            L += z[j]
        print(f"     VERIFY  Q*L == 0 in the Boolean ring:  {Q * L == B.zero()}"
              f"   (Q: {len(Q.monomials())} monomials, degree {Q.degree()})")
        # Sharper structure: the subset-sum of quadrics DEGENERATES to an affine
        # form. Once Q is affine, Q*(1+Q) = Q + Q^2 = 0 is the Boolean identity
        # (squaring is additive in char 2 and z^2 = z), so the syzygy is automatic.
        # The Semaev-specific content is the degeneration itself: in the support-
        # matched null no subset of quadrics sums to an affine form (kernel dim 0).
        print(f"     Q affine (deg <= 1)? {Q.degree() <= 1}"
              f"   L affine? {L.degree() <= 1}"
              f"   L == 1+Q ? {L == B.one() + Q}"
              f"   Q == 1+L ? {Q == B.one() + L}")
        if Q.degree() <= 1 and L.degree() <= 1:
            P = Q if (L == B.one() + Q) else L
            print(f"     => relation is the Boolean identity P*(1+P) = 0 with the"
                  f" AFFINE form P = {P}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-list", default="12,15,18")
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--ti", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    for n in [int(x) for x in args.n_list.split(",")]:
        analyze(n, args.t, args.ti, args.seed)


if __name__ == "__main__":
    main()
