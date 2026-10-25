"""Red-team check (TASK-20261023-e5df50): population of class-number-one CM anomalous primes in [10^4, 10^5].

Anomalous ordinary reduction with CM by the maximal order of discriminant D (h = 1) exists iff
4p = 1 + |D| w^2 for an integer w (trace 1 is one of the CM traces). Independent of producer code.
"""
import json, os
def isprime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
LO, HI = 10_000, 100_000
out = {}
for D in (3, 4, 7, 8, 11, 19, 43, 67, 163):
    ps = sorted({(1 + D * w * w) // 4 for w in range(1, 2000) if (1 + D * w * w) % 4 == 0
                 and LO <= (1 + D * w * w) // 4 <= HI and isprime((1 + D * w * w) // 4)})
    out[f"D=-{D}"] = ps
summary = {k: len(v) for k, v in out.items()}
summary["total"] = sum(summary.values())
HERE = os.path.dirname(os.path.abspath(__file__))
json.dump({"counts": summary, "primes": out}, open(os.path.join(HERE, "rt_population.json"), "w"), indent=1)
print(summary)
