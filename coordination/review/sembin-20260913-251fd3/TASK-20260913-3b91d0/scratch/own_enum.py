#!/usr/bin/env python3
"""N1, step (3): recompute the ARM C empty-coset counts at three enumeration
cells with MY OWN GF(2^n) arithmetic, from the parameters c0-lower-bound.json
records (n, k, field_poly, curve A, B) and nothing else.

Written and run BEFORE opening experiments/EXP-SEMBIN-db9bc3/code/binary_field.py
or code/arm_c_coset.py.

Derivation of the x-coordinate image, mine:
  curve y^2 + x y = x^3 + A x^2 + B over F_{2^n}.
  x = 0: y^2 = B, and squaring is a bijection in char 2, so x = 0 is ALWAYS in
         the image (exactly one point).
  x != 0: put y = x u  =>  u^2 + u = x + A + B x^{-2}.  Over F_{2^n} the
         equation u^2 + u = z is solvable iff Tr(z) = 0 (two solutions), so
         x is in the image iff Tr(x + A + B x^{-2}) = 0.
  V = span{1, x, ..., x^{k-1}} is, in the polynomial basis, the integers
  0..2^k-1, so the coset of an element e is e >> k and there are 2^{n-k} cosets.
  A coset is EMPTY iff no image element lies in it.
"""
import json
import math
import sys

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/c0-lower-bound.json"
CELLS = [(16, 2), (18, 3), (20, 2)]


class GF2n:
    def __init__(self, n, poly):
        self.n = n
        self.poly = poly          # includes the x^n bit
        self.mask = (1 << n) - 1
        assert poly >> n == 1, "field_poly must be monic of degree n"

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.n:
                a ^= self.poly
        return r

    def is_irreducible(self):
        """x^(2^n) == x and gcd-free: test by checking x^(2^d) != x for d | n, d < n."""
        # cheap sufficient test for our use: the multiplicative order check below
        return True

    def trace_vector(self):
        """Tr(x^i) for i = 0..n-1, as a bit per i (Tr is F_2-linear)."""
        tv = 0
        for i in range(self.n):
            e = 1 << i
            acc = 0
            cur = e
            for _ in range(self.n):
                acc ^= cur
                cur = self.mul(cur, cur)
            # acc is the trace, an element of F_2 embedded as 0 or 1
            assert acc in (0, 1), f"trace of basis elt {i} is not in F_2: {acc}"
            if acc:
                tv |= 1 << i
        return tv

    def exp_table(self):
        """powers of the element x (= 2); returns (exp, log) if x generates, else None."""
        order = (1 << self.n) - 1
        exp = [0] * order
        log = [-1] * (1 << self.n)
        cur = 1
        for i in range(order):
            if log[cur] != -1:
                return None
            exp[i] = cur
            log[cur] = i
            cur <<= 1
            if cur >> self.n:
                cur ^= self.poly
        if cur != 1:
            return None
        return exp, log


def popcount_parity(z, tv):
    return bin(z & tv).count("1") & 1


def image_and_empty(n, k, poly, A, B):
    F = GF2n(n, poly)
    tv = F.trace_vector()
    tbl = F.exp_table()
    if tbl is None:
        raise SystemExit(f"element x is not a generator for n={n}; need another route")
    exp, log = tbl
    order = (1 << n) - 1
    size = 1 << n

    in_image = bytearray(size)
    in_image[0] = 1                      # x = 0 always
    trA = popcount_parity(A, tv)
    for i in range(order):
        x = exp[i]
        xinv = exp[(order - i) % order]
        xinv2 = F.mul(xinv, xinv)
        z = x ^ A ^ F.mul(B, xinv2)
        if popcount_parity(z, tv) == 0:
            in_image[x] = 1
    image_size = sum(in_image)

    ncos = 1 << (n - k)
    occupied = bytearray(ncos)
    for e in range(size):
        if in_image[e]:
            occupied[e >> k] = 1
    empty = ncos - sum(occupied)
    return image_size, ncos, empty, trA


def main():
    d = json.load(open(RUN))
    cells = {(c["n"], c["k"]): c for c in d["exact_enumeration_measured"]}
    out = []
    for (n, k) in CELLS:
        c = cells[(n, k)]
        size, ncos, empty, trA = image_and_empty(n, k, c["field_poly"],
                                                 c["curve"]["A"], c["curve"]["B"])
        delta = size / (1 << n)
        # two candidate binomial predictions for E[#empty cosets]
        pred_measured_delta = ncos * (1 - c["measured_delta"]) ** (2 ** k)
        pred_own_delta = ncos * (1 - delta) ** (2 ** k)
        # hypergeometric (sampling without replacement) variant
        pred_hyper = ncos * math.prod(
            [(1 << n) - size - j for j in range(2 ** k)]
        ) / math.prod([(1 << n) - j for j in range(2 ** k)]) if 2 ** k <= 16 else None
        row = {
            "n": n, "k": k,
            "my_x_image_size": size, "json_x_image_size_exact": c["x_image_size_exact"],
            "image_match": size == c["x_image_size_exact"],
            "my_delta": delta, "json_measured_delta": c["measured_delta"],
            "my_n_cosets": ncos, "json_n_cosets": c["n_cosets"],
            "my_empty_structured_V": empty,
            "json_empty_cosets_curve_structured_V": c["empty_cosets_curve_structured_V"],
            "empty_match": empty == c["empty_cosets_curve_structured_V"],
            "json_predicted_empty_cosets_binomial": c["predicted_empty_cosets_binomial"],
            "my_pred_using_json_delta": pred_measured_delta,
            "my_pred_using_my_delta": pred_own_delta,
            "my_pred_hypergeometric": pred_hyper,
            "json_random_V_mean": sum(c["empty_cosets_curve_random_V"]) / len(c["empty_cosets_curve_random_V"]),
            "json_null_mean": c["null_mean"], "json_null_sd": c["null_sd"],
            "trace_of_A": trA,
        }
        out.append(row)
        print(json.dumps(row, indent=1))
    json.dump(out, open("own_enum.json", "w"), indent=1)


if __name__ == "__main__":
    main()
