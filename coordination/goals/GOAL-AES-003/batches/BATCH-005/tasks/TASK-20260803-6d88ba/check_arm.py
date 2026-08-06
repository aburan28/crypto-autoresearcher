# Independent re-derivation of every reported scalar from the occupancy histogram
# alone. Does not trust the engine's own n, n_alt, N or n_mod8.
import json, sys, math
from functools import reduce
def check(path, label):
    d = json.load(open(path))
    h = {int(k): int(v) for k, v in d["occ_hist"].items()}
    N = sum(b*c for b, c in h.items())
    slots = sum(h.values())
    n = sum(c * (b*(b-1)//2) for b, c in h.items())
    S2 = sum(c * b * b for b, c in h.items())
    n_alt = (S2 - N) // 2
    nz = [b for b in h if b > 0]
    g = reduce(math.gcd, nz) if nz else 0
    return {
        "arm": label, "engine_report": {k: d[k] for k in
            ("engine","r","j0","cw","wbits","threads","N","N_ok","n","n_alt","agree",
             "n_mod8","n_mod16","max_occ","counter_integrity_ok","seconds")},
        "matrix": d["matrix"], "key": d["key"], "base": d["base"],
        "independent_recheck": {
            "N_from_hist": N, "N_equals_2^32": N == 2**32,
            "slots_from_hist": slots, "slots_equals_2^32": slots == 2**32,
            "n_from_hist": n, "n_alt_from_hist": n_alt,
            "n_matches_engine": n == d["n"], "n_alt_matches_engine": n_alt == d["n_alt"],
            "n_mod8_from_hist": n % 8, "n_mod8_matches_engine": n % 8 == d["n_mod8"],
            "n_mod256_from_hist": n % 256,
        },
        "READING_B_fiber_divisibility": {
            "gcd_of_nonzero_fiber_sizes": g,
            "all_nonzero_fibers_multiple_of_256": (g % 256 == 0) if g else None,
            "all_nonzero_fibers_multiple_of_16": (g % 16 == 0) if g else None,
            "distinct_nonzero_fiber_sizes": len(nz),
            "max_occ_from_hist": max(nz) if nz else 0,
        },
        "occ_hist": dict(sorted(h.items())),
        "VALID_MEASUREMENT": bool(d["N_ok"] and d["agree"] and d["counter_integrity_ok"]
                                  and N == 2**32 and n == d["n"]),
    }
if __name__ == "__main__":
    print(json.dumps(check(sys.argv[1], sys.argv[2]), indent=1))
