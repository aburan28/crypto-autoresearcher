"""EXP-DREG-001 §11 hypothesis 4 — alpha-orbit invariance: NEGATIVE RESULT.

The measured count (deficit = 8 * dim V) suggests the extra syzygies might form
k orbits of size 8 under the field's multiplication-by-alpha action. This probe
tests the SIMPLEST realization of that action and REFUTES it.

Action tested: multiplication by alpha realized as the companion matrix C of the
field modulus, acting block-wise on the Weil-descent components of the generators
(generator index shifts within its descent block; monomial multipliers held fixed).

Result: this action preserves neither the syzygy space nor even the UNIVERSAL
generic space G (Frobenius + Koszul). Since any correct field symmetry must fix
those classical syzygies, the operator is provably incomplete: a correct action
must also co-transform the Boolean variables (u1 is a full-field variable, so
multiplying a relation by alpha mixes variable coordinates as well as generator
components). That is a Weil-restriction module calculation, not this one-line
operator.

Recorded as a refuted hypothesis (AGENTS rule 8). The derivation of 8*dim(V) from
the correct Weil-restriction / Frobenius symmetry remains OPEN; the count itself is
exact and reproducible (see syzygy_degree4.py).

Run:
  DOT_SAGE=experiments/EXP-DREG-001/runtime/sage TMPDIR=/Volumes/Volume/tmp \
  sage -python experiments/EXP-DREG-001/characterization/alpha_action_test.py --n 12
"""
import argparse
import itertools
import sys
from pathlib import Path

CODE = (Path(__file__).resolve().parent.parent
        / "runs" / "RUN-DREG-001-VALIDATE-N12-A" / "code")
sys.path.insert(0, str(CODE))

from sage.all import GF, matrix, vector  # noqa: E402
from h012_peel_rank import build_system  # noqa: E402
from ic_first_fall_fast import multiply, mono_deg  # noqa: E402
from semaev_tree import build_field_and_curve  # noqa: E402

F2 = GF(2)
D = 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--ti", type=int, default=0)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    n, t = args.n, args.t

    # companion matrix of multiplication by alpha in the _vector_() basis
    Fq, _E, _alpha, _A, _B = build_field_and_curve(n)
    g = Fq.gen()
    C = matrix(F2, n, n)
    for l in range(n):
        col = (g * (g ** l))._vector_()
        for m in range(n):
            C[m, l] = col[m]
    print(f"n={n}  field {Fq}")
    print(f"  companion matrix charpoly == field modulus? "
          f"{C.charpoly() == Fq.modulus().change_ring(F2)}")

    _rng, nb, gens, _eq_degs = build_system(n, t, args.ti, args.seed)
    degs = [max(mono_deg(m) for m in f) for f in gens]
    # descent blocks: gens[0:n] = components of E1 (cubics), gens[n:2n] = E2 (quadrics)
    assert set(degs[:n]) == {3} and set(degs[n:2 * n]) == {2}, \
        "unexpected generator block order"

    rowlab, rows, rowinfo = {}, [], []
    for gi, f in enumerate(gens):
        for md in range(0, D - degs[gi] + 1):
            for combo in itertools.combinations(range(nb), md):
                prod = multiply(f, frozenset(combo))
                if prod and max(mono_deg(m) for m in prod) <= D:
                    rowlab[(gi, combo)] = len(rows)
                    rows.append(prod)
                    rowinfo.append((gi, combo))
    cols = sorted(set().union(*rows), key=lambda m: (mono_deg(m), tuple(sorted(m))))
    colidx = {m: i for i, m in enumerate(cols)}
    nrows = len(rows)
    M = matrix(F2, nrows, len(cols), sparse=True)
    for ri, prod in enumerate(rows):
        for m in prod:
            M[ri, colidx[m]] = 1
    K = M.left_kernel()
    print(f"  M4 {nrows}x{len(cols)} rank={M.rank()} left-kernel dim={K.dimension()}")

    def phi(v):
        """alpha-action: shift descent components by C within each block."""
        w = [0] * nrows
        for r in v.support():
            gi, combo = rowinfo[r]
            base, l = (0, gi) if gi < n else (n, gi - n)
            for m in range(n):
                if C[m, l]:
                    r2 = rowlab.get((base + m, combo))
                    if r2 is not None:
                        w[r2] ^= 1
        return vector(F2, w)

    def rowvec(idx):
        v = [0] * nrows
        for i in idx:
            v[i] ^= 1
        return vector(F2, v)

    def tc(m):
        return tuple(sorted(int(x) for x in m))

    quads = list(range(n, 2 * n))
    G = []
    for qi in quads:
        s = set()
        for m in gens[qi]:
            s ^= {rowlab[(qi, tc(m))]}
        s ^= {rowlab[(qi, ())]}
        G.append(rowvec(s))
    for a, b in itertools.combinations(range(len(quads)), 2):
        qa, qb = quads[a], quads[b]
        s = set()
        for m in gens[qb]:
            s ^= {rowlab[(qa, tc(m))]}
        for m in gens[qa]:
            s ^= {rowlab[(qb, tc(m))]}
        G.append(rowvec(s))
    Gspace = matrix(F2, G).row_space()

    kfail = sum(1 for v in K.basis() if phi(v) not in K)
    gfail = sum(1 for v in G if phi(v) not in Gspace)
    print(f"\n  [test] Phi(K) subset K ?  failures = {kfail}/{K.dimension()}"
          f"  -> {'INVARIANT' if kfail == 0 else 'NOT INVARIANT'}")
    print(f"  [test] Phi(G) subset G ?  failures = {gfail}/{len(G)}"
          f"  -> {'INVARIANT' if gfail == 0 else 'NOT INVARIANT'}")
    print("\n  Failing on the universal generic space G means the operator is"
          "\n  incomplete, not that the syzygies lack a field symmetry. See the"
          "\n  module docstring: OPEN, needs the Weil-restriction action.")


if __name__ == "__main__":
    main()
