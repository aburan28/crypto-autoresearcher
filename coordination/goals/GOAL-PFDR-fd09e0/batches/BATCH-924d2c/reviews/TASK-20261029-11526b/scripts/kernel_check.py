"""Validate the reviewer counting kernel (common.count_CD) against a dictionary brute force and the KAT sets,
and the reviewer label-universe test against the Euler criterion in pure Python. Writes outputs/kernel-check.json."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402


def main():
    res = {"kat_sets": 0, "kat_mismatch": [], "random_sets": 0, "random_mismatch": [], "in_L_mismatch": 0}
    kat = json.load(open(C.KAT))
    for s in kat["sets"]:
        c, d = C.count_CD(s["X"], s["p"])
        res["kat_sets"] += 1
        if (c, d) != (s["C"], s["D"]):
            res["kat_mismatch"].append(s["name"])
    rng = C.review_np_rng("kernel-check")
    # random sets on primes of both kernel branches (bincount p <= 2^25, sort p > 2^25)
    for p in (1009, 65521, 1048573, 16777213, 268435399):
        for n in (4, 17, 64, 200, 400):
            X = rng.choice(min(p, 10**6), size=n, replace=False) if p > 10**6 else rng.choice(p, size=n, replace=False)
            X = (X * 7919 + 13) % p
            X = np.unique(X)
            c1 = C.count_CD(X, p)
            c2 = C.brute_CD(X, p)
            res["random_sets"] += 1
            if c1 != c2:
                res["random_mismatch"].append([p, int(len(X))])
    # structured set with many coincidences (an AP) on the sort branch
    p = 268435399
    X = np.array([(5 + 977 * k) % p for k in range(300)])
    res["ap_sort_branch"] = {"kernel": C.count_CD(X, p), "brute": C.brute_CD(X, p)}
    # label universe on a toy curve: compare with pure-Python Euler criterion
    p, a, b = 1048573, 12345, 678
    xs = np.arange(0, 5000)
    v = C.in_L(xs, p, a, b)
    for x in range(5000):
        f = (x ** 3 + a * x + b) % p
        ref = f != 0 and pow(f, (p - 1) // 2, p) == 1
        if bool(v[x]) != ref:
            res["in_L_mismatch"] += 1
    res["pass"] = not res["kat_mismatch"] and not res["random_mismatch"] and res["in_L_mismatch"] == 0 and \
        res["ap_sort_branch"]["kernel"] == res["ap_sort_branch"]["brute"]
    print(json.dumps(res))
    C.write_json("kernel-check.json", res)


if __name__ == "__main__":
    main()
