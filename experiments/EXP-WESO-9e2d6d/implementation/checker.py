"""IV-4 checker: recompute Stage C/D summaries from the per-sample and per-null
records and compare them with raw-result.json.  Independent code path: smooth
counts are recomputed from the stored FACTORISATIONS (not the ell_max field),
and every factorisation is re-verified with sympy (product equals the integer;
each factor passes sympy.isprime), independent of PARI.

Usage: python3 -B checker.py --run-dir <run dir>   -> writes checker_result.json
"""
import argparse
import gzip
import json
import math
import os

import sympy


def load(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(l) for l in f]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    rd = a.run_dir
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    primecache = set()
    out = {"per_prime": {}, "mismatches": []}

    def verify(value, fac):
        prod = 1
        for q, e in fac:
            q = int(q)
            if q not in primecache:
                if not sympy.isprime(q):
                    return False
                primecache.add(q)
            prod *= q ** int(e)
        return prod == int(value)

    def ellmax(fac):
        return max([int(q) for q, _ in fac], default=1)

    def cmp(label, key, got, want):
        ok = (got == want) if not isinstance(want, float) else (abs(got - want) <= 1e-12 * max(1.0, abs(want)))
        if not ok:
            out["mismatches"].append({"prime": label, "key": key, "recomputed": got, "raw": want})
        return ok

    total_fac_fail = 0
    for res in raw.get("per_prime", []):
        label = res["label"]
        samples = load(os.path.join(rd, "samples.%s.jsonl.gz" % label))
        nulls = load(os.path.join(rd, "nulls.%s.jsonl.gz" % label))
        main = [r for r in samples if r["arm"] in ("R1", "R2")]
        main.sort(key=lambda r: (r["arm"], r["index"]))
        n1 = sorted([r for r in nulls if r["arm"] == "NULL1"], key=lambda r: r["index"])
        n2 = sorted([r for r in nulls if r["arm"] == "NULL2"], key=lambda r: r["index"])
        ff = sum(1 for r in samples if not verify(r["delta"], r["fac"])) + sum(1 for r in nulls if not verify(r["n"], r["fac"]))
        total_fac_fail += ff
        N = len(main)
        cmp(label, "N", N, res["N"])
        em = [ellmax(r["fac"]) for r in main]
        e1 = [ellmax(r["fac"]) for r in n1]
        e2 = [ellmax(r["fac"]) for r in n2]
        # NULL-1 bit-length matching
        bl_ok = all(int(n["n"]).bit_length() == int(s["delta"]).bit_length() for n, s in zip(n1, main))
        for c in res["cells"]:
            B = c["B"]
            cmp(label, "S_delta@u%s" % c["u"], sum(1 for e in em if e < B), c["S_delta"])
            cmp(label, "S_null1@u%s" % c["u"], sum(1 for e in e1 if e < B), c["S_null1"])
            cmp(label, "S_null2@u%s" % c["u"], sum(1 for e in e2 if e < B), c["S_null2"])
            cmp(label, "f_emp@u%s" % c["u"], sum(1 for e in em if e < B) / N, c["f_emp"])
        for t in res["TC-2"]:
            cmp(label, "TC2_m%d" % t["m"], sum(1 for e in em if e == 1 or math.log(e) < t["x_m"]), t["observed"])
        cmp(label, "TC1_M", min(em), res["TC-1"]["M"])
        cmp(label, "SEED2_dups", N - len(set(r["order_hash"] for r in main)), res["SEED-2"]["duplicate_order_hashes"])
        cmp(label, "SEED2_delta1", sum(1 for r in main if int(r["delta"]) == 1), res["SEED-2"]["delta_eq_1_count"])
        cmp(label, "TC3_delta_prime", sum(1 for r in main if int(r["delta"]) > 1 and len(r["fac"]) == 1 and r["fac"][0][1] == 1),
            res["TC-3"]["delta_prime_count"])
        cmp(label, "delta_max", max(int(r["delta"]) for r in main), res["delta_max"])
        X = int(raw["admissible_tables"][label]["X_max"]) if "admissible_tables" in raw else None
        out["per_prime"][label] = {"records_main": N, "records_all_samples": len(samples), "records_nulls": len(nulls),
                                   "sympy_factorisation_failures": ff, "null1_bitlength_matched": bl_ok,
                                   "all_delta_le_X": (max(int(r["delta"]) for r in samples) <= X) if X else None}
        if not bl_ok:
            out["mismatches"].append({"prime": label, "key": "NULL1_bitlengths"})
    out["sympy_factorisation_failures_total"] = total_fac_fail
    out["verdict"] = "PASS" if (not out["mismatches"] and total_fac_fail == 0) else "FAIL"
    with open(os.path.join(rd, "checker_result.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(out["verdict"], len(out["mismatches"]), total_fac_fail)


if __name__ == "__main__":
    main()
