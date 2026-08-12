#!/usr/bin/env python3
"""EXP-JMV-004 branch (a) - concrete cost of the JMV random self-reduction.

SCOUTING. Not an approved run; emits no run record.

Converts Corollary 1.2 (polylog(q) ORACLE QUERIES) into field operations, and
compares against Pollard rho at sqrt(n).

Model, all from the paper:
  m       = (log q)^(2+delta)                       [Thm 1.1, m = p(log q)]
  k       = lambda_triv ~ #{split p <= m} ~ pi(m)/2 [Sec 4.3]
  c       = C * m^(1/2) * log|mD|,  |D| <= 4q       [Lemma 4.1]
  r       >= log(2h/|S|^(1/2)) / log(k/c)           [Prop 3.1]
  h       ~ sqrt(|D|) ~ sqrt(q)                     [class number, order of magnitude]
  cost    = r * (per-step isogeny cost at typical l)

CRITICAL HONESTY NOTES
  1. C is the implied constant of Lemma 4.1. The paper says only that it is
     absolute; it never states a value. Pinning it needs the Bach-Sorenson
     explicit constants (JMV ref [2]). It is NOT assumed to be 1 here - it is
     SWEPT, and the threshold behaviour in C is the reported output.
  2. Both logarithm conventions are computed. "log q" is ambiguous between bits
     and natural log, and the choice moves m by orders of magnitude. A
     conclusion that flips between conventions is reported as
     convention-dependent, not as a result.
  3. A uniformly random split prime l <= m is typically of size Theta(m), NOT
     small. Cheap l=2 steps are not what the theorem's generator set provides.
  4. Three per-step cost models are reported, because JMV's 2005 figure is not
     the only one available today:
       phi_l     O(l^3)      JMV Sec 4.1, via modular polynomials (Galbraith)
       velu      O(l)        plain Velu, given a kernel point
       sqrt_velu O(l^(1/2))  Bernstein-De Feo-Leroux-Smith 2020
     Which model holds is an assumption about available algorithms, and the
     feasibility verdict depends on it. That dependence is the finding, not a
     detail to be optimized away.
"""
import math

PER_STEP = {
    "phi_l    (O(l^3), JMV 2005)": lambda l: l ** 3,
    "velu     (O(l))": lambda l: l,
    "sqrt_velu(O(sqrt l))": lambda l: math.sqrt(l),
}


def pi_approx(m):
    """pi(m) via the logarithmic integral, the standard approximation."""
    if m < 3:
        return 0.0
    # li(m) - li(2), series-free numeric integration on log scale
    n, lo, hi, acc = 2000, 2.0, m, 0.0
    step = (math.log(hi) - math.log(lo)) / n
    for i in range(n):
        t = math.exp(math.log(lo) + (i + 0.5) * step)
        acc += (t / math.log(t)) * t * step / t  # dt = t*dlog t
    return acc


def model(bits, delta, C, convention="bits", eps=0.5):
    """Return the reduction cost model for a field of `bits` bits."""
    q_log = bits if convention == "bits" else bits * math.log(2)
    m = q_log ** (2 + delta)
    if m < 3:
        return None

    k = pi_approx(m) / 2.0                      # split primes only
    ln_q = bits * math.log(2)
    ln_D_m = math.log(4) + ln_q + math.log(m)   # log|mD|, |D| <= 4q
    c = C * math.sqrt(m) * ln_D_m

    ratio = k / c
    if ratio <= 1.0:
        return dict(m=m, k=k, c=c, ratio=ratio, vacuous=True)

    ln_h = 0.5 * ln_q                           # h ~ sqrt(q)
    ln_S = math.log(eps) + ln_h
    r = (math.log(2) + ln_h - 0.5 * ln_S) / math.log(ratio)

    typical_l = m                               # random split prime <= m is Theta(m)
    costs = {name: r * f(typical_l) for name, f in PER_STEP.items()}
    rho = 2 ** (bits / 2.0)                     # sqrt(n) group operations
    return dict(m=m, k=k, c=c, ratio=ratio, vacuous=False, r=r,
                typical_l=typical_l, costs=costs, rho=rho)


def lg(x):
    return math.log2(x) if x > 0 else float("-inf")


def main():
    print("=" * 100)
    print("EXP-JMV-004 branch (a): concrete cost of the JMV self-reduction under the PROVEN bound")
    print("=" * 100)

    print("\n[1] Is the proven eigenvalue separation k/c > 1 non-vacuous at cryptographic size?")
    print("    (q = 2^256; entries are k/c; 'VACUOUS' means the proven bound gives no expansion)\n")
    print(f"    {'convention':<12}{'delta':>7}" + "".join(f"{'C='+str(c):>12}" for c in [0.5, 1, 2, 4, 8]))
    for conv in ("bits", "natural"):
        for delta in (0.25, 0.5, 1.0, 2.0, 3.0):
            row = f"    {conv:<12}{delta:>7}"
            for C in (0.5, 1, 2, 4, 8):
                res = model(256, delta, C, conv)
                row += f"{'VACUOUS':>12}" if res["vacuous"] else f"{res['ratio']:>12.2f}"
            print(row)

    print("\n[2] Total reduction cost at q = 2^256, delta = 2, C = 1 (log2 of field operations)\n")
    for conv in ("bits", "natural"):
        res = model(256, 2.0, 1.0, conv)
        if res["vacuous"]:
            print(f"    {conv:<10} VACUOUS")
            continue
        print(f"    {conv:<10} m=2^{lg(res['m']):.1f}  k/c={res['ratio']:.2f}  r={res['r']:.1f} steps  "
              f"typical l=2^{lg(res['typical_l']):.1f}")
        for name, cost in res["costs"].items():
            verdict = "cheaper than rho" if cost < res["rho"] else "MORE than rho"
            print(f"        {name:<28} 2^{lg(cost):>6.1f} field ops   ({verdict}; rho = 2^{lg(res['rho']):.0f})")

    print("\n[3] Cheapest admissible delta at q = 2^256, C = 1 (minimise cost subject to k/c > 1)\n")
    for conv in ("bits", "natural"):
        for name in PER_STEP:
            best = None
            d = 0.05
            while d <= 6.0:
                res = model(256, d, 1.0, conv)
                if not res["vacuous"]:
                    cst = res["costs"][name]
                    if best is None or cst < best[1]:
                        best = (d, cst, res["r"], res["m"])
                d += 0.05
            if best:
                print(f"    {conv:<10}{name:<28} delta*={best[0]:.2f}  cost=2^{lg(best[1]):.1f}  "
                      f"r={best[2]:.0f}  m=2^{lg(best[3]):.1f}")

    print("\n[4] Crossover: is the reduction cheaper than just solving the dlog? (C=1, delta*=cheapest admissible)\n")
    print(f"    {'bits':>6}{'rho=sqrt(n)':>14}" + "".join(f"{n.split()[0]:>14}" for n in PER_STEP))
    for bits in (64, 96, 128, 160, 192, 224, 256, 320, 384, 512):
        row = f"    {bits:>6}{'2^'+format(bits/2,'.0f'):>14}"
        for name in PER_STEP:
            best = None
            d = 0.05
            while d <= 6.0:
                res = model(bits, d, 1.0, "bits")
                if not res["vacuous"]:
                    cst = res["costs"][name]
                    if best is None or cst < best:
                        best = cst
                d += 0.05
            row += f"{'VACUOUS':>14}" if best is None else f"{'2^'+format(lg(best),'.0f'):>14}"
        print(row)

    print("\n" + "=" * 100)
    print("Reminder: C is UNPINNED. Every number above is conditional on the swept C and on")
    print("which per-step isogeny algorithm is assumed. Nothing here bears on GRH, on real")
    print("attack cost, or on the hardness of any dlog instance.")
    print("=" * 100)


if __name__ == "__main__":
    main()
