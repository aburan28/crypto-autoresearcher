#!/usr/bin/env python3
"""J7 / J10 (vi) -- TASK-20260924-d95e70. Exact structure of the m = 2 descent,
checked on the 92 archived instances (U62, C20, S10) with my own descent.

Derivation (char 2, x_1, x_2 in V = {deg < 9}):
  S_3 = (x_1 x_2)^2 + x_R x_1 x_2 + x_R^2 (x_1^2 + x_2^2) + B
      = phi(Q) + x_R^2 (x_1 + x_2)^2 + B,  phi(y) = y^2 + x_R y,
  where Q = x_1 x_2 = sum_{s=0}^{16} Q_s t^s with Q_s = sum_{i+j=s} v_i v_{9+j}
  (deg Q <= 16 < 17, so no reduction), and Q^2 = sum_s Q_s t^{2s} because
  Q_s^2 = Q_s in B. phi is F_2-linear with kernel {0, x_R}, so rank 16.
  Hence: (i) the quadratic part of f_k is sum_s T[k][s] Q_s with
  T[k][s] = bit k of phi(t^s); (ii) rank T = 16; (iii) the left kernel of T is
  spanned by c_k = Tr(t^k / x_R^2) (image of phi = {z : Tr(z / x_R^2) = 0}),
  so ell = sum_k c_k f_k is the unique non-zero combination with no quadratic
  part; its linear part is Tr(x_1) + Tr(x_2) restricted to V.
Checked: (i)-(iii) on every instance; and that the quadratic parts of the
null instances are NOT of this form (coefficient of v_i v_{9+j} not a function
of i + j), on all 124 null instances."""
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rtlib as R  # noqa: E402
from j7b_substitution import load_sets  # noqa: E402

RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
EQ = []
for d in range(3):
    EQ.extend(sum(1 << i for i in c) for c in combinations(range(18), d))


def rank_rows(rows):
    e = R.Echelon()
    for r in rows:
        e.add(r)
    return e.rank()


def conv_form(fs):
    """Return (is_convolution, T as list of 17 ints over s) for the quadratic parts."""
    T = [0] * 17
    ok = True
    for k, f in enumerate(fs):
        coef = {}
        for m in f:
            if bin(m).count("1") == 2:
                a = [i for i in range(18) if (m >> i) & 1]
                if not (a[0] < 9 <= a[1]):
                    return False, None
                coef[(a[0], a[1] - 9)] = 1
        for s in range(17):
            vals = {coef.get((i, s - i), 0) for i in range(9) if 0 <= s - i < 9}
            if len(vals) != 1:
                ok = False
            elif vals.pop():
                T[k] |= 1 << s
    return ok, T


def main():
    curve, by, sets = load_sets()
    B = curve["B"]
    rows = []
    for sname in ("U62", "C20", "S10"):
        for idx in sets[sname]:
            xR = by[idx]["x_R"]
            fs = R.descent(B, xR)
            ok, T = conv_form(fs)
            # predicted T from phi
            Tp = [0] * 17
            for s in range(17):
                z = R.gmul(R.tpow(s), R.tpow(s)) ^ R.gmul(xR, R.tpow(s))
                for k in range(17):
                    if (z >> k) & 1:
                        Tp[k] |= 1 << s
            c, ell = R.ell_of(B, xR, fs)
            # left kernel check: sum_k c_k T[k] == 0
            lk = 0
            for k in range(17):
                if c[k]:
                    lk ^= T[k]
            rows.append({"set": sname, "idx": idx, "convolution_form": ok, "T_matches_phi": T == Tp,
                         "rank_T": rank_rows(T), "c_in_left_kernel": lk == 0,
                         "ell_support": sorted(ell)})
    iset = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]
    nulls = {}
    for sname in ("N-AFF62", "N-F262"):
        cnt = 0
        ranks = {}
        for inst in iset[sname]:
            fs = [frozenset(EQ[j] for j in range(172) if (int(h, 16) >> j) & 1) for h in inst["E_hex"]]
            ok, _ = conv_form(fs)
            cnt += ok
            # rank of the 17 quadratic parts as vectors over the 81 bilinear monomials
            q = []
            for f in fs:
                v = 0
                for m in f:
                    if bin(m).count("1") == 2:
                        v |= 1 << m.bit_length()  # injective enough? use a dict index instead
                q.append(sum(1 << (sorted([i for i in range(18) if (m >> i) & 1])[0] * 9 + sorted([i for i in range(18) if (m >> i) & 1])[1] - 9)
                             for m in f if bin(m).count("1") == 2))
            r = rank_rows(q)
            ranks[r] = ranks.get(r, 0) + 1
        nulls[sname] = {"instances": len(iset[sname]), "convolution_form_count": cnt,
                        "rank_of_quadratic_parts_distribution": ranks}
    s3q = {}
    for sname in ("U62",):
        for idx in sets[sname][:62]:
            fs = R.descent(B, by[idx]["x_R"])
            q = [sum(1 << (min(i for i in range(18) if (m >> i) & 1) * 9 + max(i for i in range(18) if (m >> i) & 1) - 9)
                     for m in f if bin(m).count("1") == 2) for f in fs]
            r = rank_rows(q)
            s3q[r] = s3q.get(r, 0) + 1
    summ = {"instances": len(rows),
            "convolution_form_all": all(r["convolution_form"] for r in rows),
            "T_matches_phi_all": all(r["T_matches_phi"] for r in rows),
            "rank_T_distribution": {str(k): sum(1 for r in rows if r["rank_T"] == k) for k in sorted({r["rank_T"] for r in rows})},
            "c_in_left_kernel_all": all(r["c_in_left_kernel"] for r in rows),
            "U62_rank_of_quadratic_parts_over_81_bilinear_monomials": s3q,
            "nulls": nulls}
    json.dump({"summary": summ, "rows": rows}, open(os.path.join(HERE, "structure.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
