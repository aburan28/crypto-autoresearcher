"""Truncation calibration for logP_DK at X = 10^6 (instrument check; no target curves).

    python3 calibrate.py OUT

Draws 2,000 fundamental discriminants D in [-10^13, -10^12] (seed 20261030),
takes h(D) from PARI quadclassunit (GRH-conditional), L(1, chi_D) = pi h / sqrt|D|,
and records log P_X(D) - log L(1, chi_D). The tolerance used by analyze.py's
positive control is the maximum absolute error over the sample.
"""
import json, math, random, sys
import cypari2
from analyze import X, primes_upto, kron, term

N = 2000
SEED = 20261030


def main():
    out = sys.argv[1]
    P = cypari2.Pari(); P.allocatemem(2 * 10**9)
    primes = primes_upto(X); rng = random.Random(SEED); errs = []; ds = []
    while len(errs) < N:
        D = -rng.randrange(10**12, 10**13)
        if not P.isfundamental(D): continue
        h = int(P.quadclassunit(D)[0])
        logL = math.log(math.pi * h / math.sqrt(-D))
        logP = sum(term(kron(D, l), l) for l in primes)
        errs.append(logP - logL); ds.append(D)
    a = sorted(abs(e) for e in errs)
    res = dict(n=N, seed=SEED, X=X, D_range=[-10**13, -10**12], class_number="PARI quadclassunit (GRH)",
               mean_err=sum(errs) / N, max_abs_err=a[-1], q999_abs_err=a[int(0.999 * N) - 1],
               tolerance_abs_log=a[-1], discriminants=ds, errors=errs)
    json.dump(res, open(out, "w"), indent=1)
    print({k: v for k, v in res.items() if k not in ("discriminants", "errors")})


if __name__ == "__main__":
    main()
