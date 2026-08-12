"""EXP-DREG-001 §11 — degree-4 generic/extra syzygy isolation.

Establishes what the semi-regular prediction's "expected" syzygies actually ARE at
degree 4, and how many extra (Semaev-specific) ones the real system carries.

Generic space G = the classical trivial syzygies among the quadrics:
  - Frobenius:  q_i^2 = q_i           (one per quadric)
  - Koszul:     q_a * q_b + q_b * q_a (one per unordered pair)
Both are expressed as GF(2) row-combinations of the degree-4 Macaulay rows.

Measured result (full systems n=3k): rank(G) == nrows - pred[4] EXACTLY, and G lies
in the left kernel. So the semi-regular baseline is precisely the classical trivial
syzygies, and everything beyond it is the deficit:

    cumulative deficit at D=4 = pred[4] - rank = 8k = 8 * dim(V).

Scope: valid for FULL systems only (nb = 2n = m, i.e. n = 3k). At n=9 / n=17 the
system is variable/equation deficient, the generic space is larger than
Frobenius+Koszul, and this subtraction does not apply — the same structural reason
those are the deficient cells of §10.

Run:
  DOT_SAGE=experiments/EXP-DREG-001/runtime/sage TMPDIR=/Volumes/Volume/tmp \
  sage -python experiments/EXP-DREG-001/characterization/syzygy_degree4.py \
       --n-list 12,15,18
"""
import argparse
import itertools
import sys
import time
from pathlib import Path

CODE = (Path(__file__).resolve().parent.parent
        / "runs" / "RUN-DREG-001-VALIDATE-N12-A" / "code")
sys.path.insert(0, str(CODE))

from sage.all import GF, matrix, vector  # noqa: E402
from h012_peel_rank import build_system, semireg_rank_pred, peel_and_rank  # noqa: E402
from macaulay_export import macaulay_rows  # noqa: E402
from ic_first_fall_fast import multiply, mono_deg  # noqa: E402

F2 = GF(2)
D = 4


def analyze(n, t, ti, seed):
    k = (n + t - 1) // t
    built = build_system(n, t, ti, seed)
    if built is None:
        print(f"n={n}: build_system failed")
        return
    _rng, nb, gens, eq_degs = built
    pred, _ = semireg_rank_pred(eq_degs, nb, D + 1)
    degs = [max(mono_deg(m) for m in f) for f in gens]
    quads = [gi for gi, d in enumerate(degs) if d == 2]
    # see deficit_by_degree.py: full == exactly n quadrics + n cubics in nb = 2n vars
    full = (len(quads) == n and degs.count(3) == n
            and nb == 2 * n and len(gens) == 2 * n)

    # degree-4 Macaulay matrix with row provenance
    rowlab, rows = {}, []
    for gi, f in enumerate(gens):
        if degs[gi] > D:
            continue
        for md in range(0, D - degs[gi] + 1):
            for combo in itertools.combinations(range(nb), md):
                prod = multiply(f, frozenset(combo))
                if prod and max(mono_deg(m) for m in prod) <= D:
                    rowlab[(gi, combo)] = len(rows)
                    rows.append(prod)
    cols = sorted(set().union(*rows), key=lambda m: (mono_deg(m), tuple(sorted(m))))
    colidx = {m: i for i, m in enumerate(cols)}
    nrows = len(rows)
    M = matrix(F2, nrows, len(cols), sparse=True)
    for ri, prod in enumerate(rows):
        for m in prod:
            M[ri, colidx[m]] = 1

    t0 = time.time()
    rank = peel_and_rank(*macaulay_rows(gens, nb, D)[:2])["rank"]
    extra = pred[D] - rank

    def rowvec(idx):
        v = [0] * nrows
        for i in idx:
            v[i] ^= 1
        return vector(F2, v)

    def tc(m):
        return tuple(sorted(int(x) for x in m))

    G = []
    for qi in quads:                                   # Frobenius: q_i^2 = q_i
        s = set()
        for m in gens[qi]:
            s ^= {rowlab[(qi, tc(m))]}
        s ^= {rowlab[(qi, ())]}
        G.append(rowvec(s))
    for a, b in itertools.combinations(range(len(quads)), 2):   # Koszul pairs
        qa, qb = quads[a], quads[b]
        s = set()
        for m in gens[qb]:
            s ^= {rowlab[(qa, tc(m))]}
        for m in gens[qa]:
            s ^= {rowlab[(qb, tc(m))]}
        G.append(rowvec(s))
    Gmat = matrix(F2, G, sparse=True)
    rank_g = Gmat.rank()
    generic_expected = nrows - pred[D]
    in_kernel = (Gmat * M).is_zero()

    print(f"\n=== n={n} k={k} nb={nb} {'FULL' if full else 'DEFICIENT'} ===")
    print(f"  M4: {nrows} rows x {len(cols)} cols   rank={rank}   pred[4]={pred[D]}")
    print(f"  generic G: {len(G)} vectors "
          f"({len(quads)} Frobenius + {len(quads) * (len(quads) - 1) // 2} Koszul)")
    print(f"     G in left kernel?          {in_kernel}")
    print(f"     rank(G) = {rank_g}   nrows - pred[4] = {generic_expected}"
          f"   {'MATCH (baseline == classical trivial syzygies)' if rank_g == generic_expected else '<-- MISMATCH (isolation invalid here)'}")
    print(f"  extra (Semaev-specific) syzygies = pred[4] - rank = {extra}")
    if full:
        print(f"     8k = {8 * k}   "
              f"{'OK  => deficit = 8 * dim(V)' if extra == 8 * k else '<-- MISMATCH'}")
    print(f"  ({time.time() - t0:.0f}s)")


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
