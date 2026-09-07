"""
Independent red-team verification of C2a's claimed non-sparsity, using ONLY
public curve parameters (p, b) from specification.yaml / design/ladder.json.
No discrete log, no cache, no stage of EXP-ECDLP-56ee42 is touched.

Method: exact Legendre-symbol classification of x in [0, p) against
y^2 = x^3 + x + b (mirrors J2's step_e_comparator_balance.py method, applied
to the x_bucket_partition(xs, p, 2) domain split instead of top_bit_fiber).

Vectorized modular exponentiation (square-and-multiply) via numpy int64
arrays, processed in chunks to bound memory.
"""
import time
import numpy as np

LADDER = [
    {"T": 17, "p": 131101,    "b": 27, "N": 131113},
    {"T": 19, "p": 524309,    "b": 80, "N": 525361},
    {"T": 21, "p": 2097169,   "b": 1,  "N": 2098321},
    {"T": 23, "p": 8388617,   "b": 21, "N": 8391797},
    {"T": 25, "p": 33554473,  "b": 49, "N": 33557891},
    {"T": 27, "p": 134217757, "b": 70, "N": 134234689},
]

CHUNK = 4_000_000

def legendre_vectorized_counts(p: int, b: int, half_boundary: int):
    """Sweep x in [0, p) in chunks; classify Legendre symbol of
    f(x) = x^3 + x + b mod p; accumulate (qr_count, zero_count, nqr_count)
    for fiber0 (x < half_boundary) and fiber1 (x >= half_boundary)."""
    e = (p - 1) // 2
    # bits of e, LSB first
    ebits = []
    ee = e
    while ee > 0:
        ebits.append(ee & 1)
        ee >>= 1

    fiber0_points = 0  # x < half_boundary
    fiber1_points = 0  # x >= half_boundary

    x0 = 0
    while x0 < p:
        x1 = min(x0 + CHUNK, p)
        xs = np.arange(x0, x1, dtype=np.int64)
        # rhs = x^3 + x + b mod p, overflow-safe
        x2 = (xs * xs) % p
        x3 = (x2 * xs) % p
        rhs = (x3 + xs + b) % p

        # vectorized modpow: rhs^e mod p
        base = rhs.copy()
        result = np.ones_like(rhs)
        for bit in ebits:
            if bit:
                result = (result * base) % p
            base = (base * base) % p
        # result: 1 => QR (2 points), 0 => rhs==0 (1 point), p-1 => NQR (0 points)
        pts = np.zeros_like(rhs)
        pts[result == 1] = 2
        pts[rhs == 0] = 1  # overrides in case result==0 too (0^e=0)
        # (NQR entries stay 0)

        mask0 = xs < half_boundary
        fiber0_points += int(pts[mask0].sum())
        fiber1_points += int(pts[~mask0].sum())

        x0 = x1

    return fiber0_points, fiber1_points


def main():
    print(f"{'T':>3} {'p':>10} {'half_boundary':>13} {'fiber0_pts(+inf)':>17} "
          f"{'fiber1_pts':>11} {'N':>10} {'sum_check':>10} "
          f"{'frac0':>9} {'frac1':>9} {'dev_from_half':>14} {'time_s':>7}")
    results = []
    for rung in LADDER:
        t0 = time.time()
        p, b, N = rung["p"], rung["b"], rung["N"]
        half_boundary = -(-p // 2)  # ceil(p/2)
        f0, f1 = legendre_vectorized_counts(p, b, half_boundary)
        # point at infinity: x(O)=0 by convention -> counted in fiber0
        f0_with_inf = f0 + 1
        total = f0_with_inf + f1
        dt = time.time() - t0
        frac0 = f0_with_inf / N
        frac1 = f1 / N
        dev = abs(frac0 - 0.5)
        results.append(dict(T=rung["T"], p=p, half_boundary=half_boundary,
                             fiber0_points=f0_with_inf, fiber1_points=f1, N=N,
                             sum_check=total, frac0=frac0, frac1=frac1,
                             dev_from_half=dev, time_s=dt))
        print(f"{rung['T']:>3} {p:>10} {half_boundary:>13} {f0_with_inf:>17} "
              f"{f1:>11} {N:>10} {total:>10} {frac0:>9.6f} {frac1:>9.6f} "
              f"{dev:>14.8f} {dt:>7.2f}")

    print()
    print("Sanity: sum_check should equal N exactly at every rung (else a bug).")
    for r in results:
        assert r["sum_check"] == r["N"], r
    print("All sum checks OK (fiber0+fiber1 == N exactly at every rung).")

    print()
    print("Comparison to top-bit COMPARATOR's measured imbalance (J2's table):")
    old_top_bit = {17: 0.00024406, 19: 0.00001523, 21: 0.00001144,
                   23: 0.00000095, 25: 0.00000149, 27: 0.00000016}
    for r in results:
        minority_frac = min(r["frac0"], r["frac1"])
        print(f"  T{r['T']}: C2a minority fiber fraction = {minority_frac:.6f} "
              f"vs top-bit minority fraction = {old_top_bit[r['T']]:.8f} "
              f"(ratio {minority_frac/old_top_bit[r['T']]:.3e}x larger)")

    print()
    print("Trend check (does deviation from 1/2 shrink as p grows, as claimed?):")
    for r in results:
        print(f"  T{r['T']}: p={r['p']:>10} dev_from_half={r['dev_from_half']:.8f} "
              f"  ln(p)/sqrt(p)={np.log(r['p'])/np.sqrt(r['p']):.6f}")

if __name__ == "__main__":
    main()
