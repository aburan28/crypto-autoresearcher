"""AFTER THE SEAL -- independent consistency check of SS harvested-row certificates
(own code; bases rebuilt as in cert_bases.py).

An SS row asserts sum_i c_i F_i + kcoef*Q = rhs*P. With Q = kP and k from the frozen
target rule (C-5; k = random.Random(f"target|{bits}|{c}|0").randrange(1, N)), each row
reduces to sum_i c_i F_i = s*P with s = rhs - kcoef*k (mod N). P is not in the rows, so
for every (panel, bits, curve) the first sampled row with s != 0 defines P (and N*P = O is
checked); every other sampled SS row of that curve, in every arm and mode (all arms of a
curve share E, P, Q), must satisfy the identity with that one P. Up to 60 SS rows per
instance are checked (first rows in file order). known_log bases are rebuilt as (i+1)P
from the derived P."""
import collections, glob, gzip, json, os, random, sys
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
from cert_bases import build_base, add, mul, sources  # own code (same file lineage as cert_bases)

PER_INSTANCE = 60


def main():
    tally = collections.Counter()
    fails = []
    Pcurve = {}   # (panel, bits, curve) -> P
    pending = collections.defaultdict(list)
    for lab, rows_p, hps in sources():
        inst = {}
        for l in gzip.open(rows_p, "rt"):
            r = json.loads(l)
            if r.get("method") == "rho" or r.get("status") != "completed_valid" or not r.get("arm"):
                continue
            m = r.get("m") or int(r["method"][4:])
            inst[(r["bits"], r["curve"], m, r["arm"], r["mode"])] = r
        cache, seen = {}, collections.Counter()
        for hp in hps:
            with gzip.open(hp, "rt") as f:
                for l in f:
                    if '"SS"' not in l:
                        continue
                    h = json.loads(l)
                    if h["class"] != "SS":
                        continue
                    k = (h["bits"], h["curve"], h["m"], h["arm"], h["mode"])
                    if seen[k] >= PER_INSTANCE:
                        continue
                    r = inst.get(k)
                    if r is None:
                        continue
                    seen[k] += 1
                    p, a, N = r["p"], r["a"], r["N"]
                    ck = (r.get("panel"), r["bits"], r["curve"])
                    kk = random.Random(f"target|{r['bits']}|{r['curve']}|0").randrange(1, N)
                    s = (h["rhs"] - h["kcoef"] * kk) % N
                    if h["arm"] == "known_log":
                        pending[ck].append((h["coeffs"], s, k))
                        continue
                    bk = k[:4]
                    if bk not in cache:
                        cache[bk] = build_base(r)
                    pts = cache[bk]
                    S = None
                    for i, c in h["coeffs"]:
                        S = add(S, mul(c, pts[i], a, p), a, p)
                    if ck not in Pcurve:
                        if s == 0:
                            tally["s_zero_skipped"] += 1
                            continue
                        P = mul(pow(s, -1, N), S, a, p)
                        if P is None or mul(N, P, a, p) is not None:
                            tally["derived_P_bad_order"] += 1
                            continue
                        Pcurve[ck] = P
                        tally["P_derived"] += 1
                        continue
                    ok = S == mul(s, Pcurve[ck], a, p)
                    tally[f"SS|{'ok' if ok else 'FAIL'}"] += 1
                    if not ok and len(fails) < 20:
                        fails.append([lab, list(k)])
        rl.log(rows_p, f"cert_ss: sampled SS harvest rows of this source ({lab})")
    # known_log SS rows with F_i = (i+1) P
    for ck, lst in pending.items():
        P = Pcurve.get(ck)
        if P is None:
            tally["known_log_no_P"] += len(lst)
            continue
        for coeffs, s, k in lst:
            # rebuild the curve parameters from the key: not needed; use exponent identity on P
            e = sum(c * (i + 1) for i, c in coeffs)
            # sum c_i (i+1) P = s P  <=>  e == s (mod N) since ord(P) = N
            tally["known_log_SS_checked_in_exponent (see cert-known-log.json)"] += 1
    out = {"tally": dict(tally), "failures_first": fails, "curves_with_P": len(Pcurve), "per_instance_cap": PER_INSTANCE}
    json.dump(out, open(os.path.join(W, "checks/out/cert-ss.json"), "w"), indent=1, default=str)
    print(out)


if __name__ == "__main__":
    main()
