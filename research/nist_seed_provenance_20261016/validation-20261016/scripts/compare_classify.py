#!/usr/bin/env python3
"""J2 (index sets), J5 (classifier from the stated criteria), J4 (twist bookkeeping)
on the six recorded orders files. Written before census/summary.json is opened.

Criteria as stated in the claim: prime n, bitlen(n) <= bitlen(p), n != p,
p^k != 1 (mod n) for 1 <= k < 2^10. Primality: gmpy2.is_prime (BPSW + 25 MR rounds).
Classes per row (n = N0, nt = Nt; 0 = early abort):
  accepted     : n passes all four criteria
  bitlen_reject: n prime, bitlen(n) > bitlen(p)
  other_reject : n prime, fails n != p or the MOV test (expected none)
  twist_only   : n not prime (0 or composite) and nt prime
Sensitivity (J5 a/b): n < p instead of the bitlen rule; MOV bound B = 20 (X9.62-1998,
per SEC 1 v2 commentary), B = 100 (SEC 1 v2 / X9.62a: p^B != 1 for 1 <= B < 100),
k <= 100, k < 2^10 (= SP 800-186 C.1, embedding degree >= 2^10); plus the smallest
k <= 10^5 with p^k == 1 (mod n) for every prime n.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import gmpy2

P = load_params()
q1 = json.load(open(os.path.join(ROOT, "out", "q1_seeds.json")))
published = {}
for name, rec in q1["seeds"].items():
    h = rec["hits"][0]
    published.setdefault(h["t"], []).append((h["block1"], name))


def isprime(n):
    return n > 1 and gmpy2.is_prime(n, 25)


def mov_ok(p, n, kmax_exclusive):
    x = 1
    pm = p % n
    for k in range(1, kmax_exclusive):
        x = (x * pm) % n
        if x == 1:
            return False
    return True


def emb_lower(p, n, lim=10 ** 5):
    x, pm = 1, p % n
    for k in range(1, lim + 1):
        x = (x * pm) % n
        if x == 1:
            return k
    return None   # > lim


res = {"runs": {}, "totals": {}, "mismatch_index_sets": [], "identity_failures": []}
tot = dict(blocks=0, b_exists=0, twist_only=0, bitlen=0, accepted=0, published=0, skipped=0)
for t, field, count in RUNS:
    p = P[FIELD_CURVE[field]]["p"]
    bl = p.bit_length()
    rows = []
    for line in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt")):
        i, n0, nt = map(int, line.split())
        rows.append((i, n0, nt))
    mine = [int(x) for x in open(os.path.join(ROOT, "out", f"q4_candidates_{t}.txt"))]
    rec_i = [r[0] for r in rows]
    missing = sorted(set(mine) - set(rec_i))
    extra = sorted(set(rec_i) - set(mine))
    if missing or extra or len(rec_i) != len(set(rec_i)) or rec_i != sorted(rec_i):
        res["mismatch_index_sets"].append({"t": t, "missing_in_recorded": missing,
                                           "extra_in_recorded": extra,
                                           "duplicates": len(rec_i) - len(set(rec_i)),
                                           "sorted": rec_i == sorted(rec_i)})
    acc, bit, oth, tw = [], [], [], []
    var = {"n_lt_p": [], "B20": [], "B100": [], "k_le_100": [], "k_lt_1024": []}
    diff_bitlen_vs_nltp = []
    emb = []
    zeros = {"N0": 0, "Nt": 0, "both": 0}
    for i, n0, nt in rows:
        if n0 == 0: zeros["N0"] += 1
        if nt == 0: zeros["Nt"] += 1
        if n0 == 0 and nt == 0: zeros["both"] += 1
        for val, lab in ((n0, "N0"), (nt, "Nt")):
            if val and (val - (p + 1)) ** 2 > 4 * p:
                res["identity_failures"].append({"t": t, "i": i, "col": lab, "why": "outside Hasse"})
        if n0 and nt and n0 + nt != 2 * (p + 1):
            res["identity_failures"].append({"t": t, "i": i, "why": "N0+Nt != 2(p+1)"})
        pn0 = isprime(n0) if n0 else False
        pnt = isprime(nt) if nt else False
        if pn0:
            emb.append(emb_lower(p, n0))
            base_ok = (n0 != p) and mov_ok(p, n0, 1 << 10)
            if n0.bit_length() > bl:
                bit.append(i)
            elif base_ok:
                acc.append(i)
            else:
                oth.append(i)
            # variants
            if n0 < p and base_ok: var["n_lt_p"].append(i)
            if (n0 < p) != (n0.bit_length() <= bl):
                diff_bitlen_vs_nltp.append({"i": i, "n_bits": n0.bit_length(), "n_lt_p": n0 < p})
            if n0.bit_length() <= bl and n0 != p:
                if mov_ok(p, n0, 21): var["B20"].append(i)
                if mov_ok(p, n0, 100): var["B100"].append(i)
                if mov_ok(p, n0, 101): var["k_le_100"].append(i)
                if mov_ok(p, n0, 1 << 10): var["k_lt_1024"].append(i)
        elif pnt:
            tw.append(i)
    pubs = sorted(published.get(t, []))
    pub_idx = [b for b, _ in pubs]
    r = {"field": field, "p_mod_4": p % 4, "blocks": count, "b_exists": len(rows),
         "twist_only": len(tw), "bitlen": len(bit), "accepted": len(acc), "other_reject": oth,
         "accepted_idx": acc, "bitlen_idx": bit, "twist_only_idx": tw,
         "published": pubs, "published_subset_accepted": set(pub_idx) <= set(acc),
         "n_published": len(pub_idx), "n_skipped": len(set(acc) - set(pub_idx)),
         "published_rank_among_accepted": [acc.index(b) + 1 if b in acc else None for b in pub_idx],
         "variants": {k: {"n": len(v), "same_as_accepted": v == acc, "idx": v} for k, v in var.items()},
         "rows_where_bitlen_and_n_lt_p_differ": diff_bitlen_vs_nltp,
         "min_embedding_degree_over_prime_N0": (min(e for e in emb if e) if any(emb) else None),
         "prime_N0_with_embedding_degree_le_1e5": sum(1 for e in emb if e),
         "zeros": zeros,
         "max_order_bits_by_hasse": (p + 1 + math.isqrt(4 * p) + 1).bit_length(),
         "bitlen_rule_can_fire": (p + 1 + math.isqrt(4 * p) + 1).bit_length() > bl}
    res["runs"][str(t)] = r
    tot["blocks"] += count; tot["b_exists"] += len(rows); tot["twist_only"] += len(tw)
    tot["bitlen"] += len(bit); tot["accepted"] += len(acc)
    tot["published"] += r["n_published"]; tot["skipped"] += r["n_skipped"]
res["totals"] = tot
res["twist_only_p3mod4_runs"] = sum(r["twist_only"] for r in res["runs"].values() if r["p_mod_4"] == 3)
res["n_runs_p3mod4"] = sum(1 for r in res["runs"].values() if r["p_mod_4"] == 3)
res["n_runs_p3mod4_with_twist_only"] = sum(1 for r in res["runs"].values() if r["p_mod_4"] == 3 and r["twist_only"])
# published curves: p < n?
res["published_p_lt_n"] = {c: P[c]["n"] > P[c]["p"] for c in PRIME_CURVES}
res["published_n_bits_gt_p_bits"] = {c: P[c]["n"].bit_length() > P[c]["p"].bit_length() for c in PRIME_CURVES}
res["published_mod4_and_b_root"] = {}
for c in PRIME_CURVES:
    p, b = P[c]["p"], P[c]["b"]
    entry = {"p_mod_4": p % 4}
    if p % 4 == 3:
        entry["b_is_(p+1)/4_root"] = pow(b * b % p, (p + 1) // 4, p) == b
    res["published_mod4_and_b_root"][c] = entry
res["legendre_minus1_p224"] = pow(P["P-224"]["p"] - 1, (P["P-224"]["p"] - 1) // 2, P["P-224"]["p"])

out = os.path.join(ROOT, "out", "j5_classification.json")
with open(out, "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
order_log("J5 my classification of the recorded orders (before summary.json)", out)

print("index-set mismatches:", res["mismatch_index_sets"])
print("identity failures (Hasse, N0+Nt):", res["identity_failures"][:10], len(res["identity_failures"]))
for t, r in res["runs"].items():
    print(t, r["field"], "p%4", r["p_mod_4"], "blocks", r["blocks"], "b", r["b_exists"], "tw", r["twist_only"],
          "bitlen", r["bitlen"], "acc", r["accepted"], "pub/skip", r["n_published"], r["n_skipped"],
          "pub<=acc", r["published_subset_accepted"], "ranks", r["published_rank_among_accepted"],
          "other", r["other_reject"], "zeros", r["zeros"], "bitlen can fire", r["bitlen_rule_can_fire"],
          "min emb<=1e5", r["min_embedding_degree_over_prime_N0"])
    print("    accepted", r["accepted_idx"], "published", r["published"])
    print("    bitlen", r["bitlen_idx"])
    print("    twist-only", r["twist_only_idx"])
    print("    variants", {k: (v["n"], v["same_as_accepted"]) for k, v in r["variants"].items()},
          "bitlen vs n<p differ:", r["rows_where_bitlen_and_n_lt_p_differ"])
print("totals", res["totals"])
print("twist-only in p=3 mod 4 runs", res["twist_only_p3mod4_runs"], "runs p=3 mod 4:", res["n_runs_p3mod4"],
      "of which with twist-only rows:", res["n_runs_p3mod4_with_twist_only"])
print("published p<n:", res["published_p_lt_n"])
print("published bitlen(n)>bitlen(p):", res["published_n_bits_gt_p_bits"])
print("published b root:", res["published_mod4_and_b_root"])
print("legendre(-1, p224) =", res["legendre_minus1_p224"])
