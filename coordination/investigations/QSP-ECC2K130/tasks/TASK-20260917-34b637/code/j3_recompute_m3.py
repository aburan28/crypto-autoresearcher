"""J3(b),(c),(d): recompute every M3 complete-splitter row from (n, n', d) ALONE.

beta, the exact corollary and the conservative corollary depend on (n, n', d)
only -- NOT on N, and therefore not on any instrument.  So the complete-splitter
margins can be checked without trusting I1, I2 or I3 at all.  That is the point
of this script: it recomputes the columns from the definitions in
H-QSP-5540d7 (B) and compares them to the archived ones with EXACT rational
arithmetic (Fraction), then falls back to float only for the comparison with
the archived float.
"""
import json, sys
from fractions import Fraction as Fr
from math import log2

S2B = "experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S2B/raw-result.json"
raw = json.load(open(S2B))
rows = raw["M3_complete_splitters"]
near = raw["M3_near_complete"]

def recompute(n, npr, d):
    q, r = divmod(n, npr)
    l = Fr(log2(d)).limit_denominator(10**9) if (d & (d-1)) else Fr(d.bit_length()-1)  # exact when d is a power of 2
    beta = l * n / (npr * npr)
    exact = Fr(n, n + npr - r)
    cons = Fr(n * (npr - 1), npr * (n + npr - r))
    bound = max(d ** (q + 1), 2 ** (npr - r))
    return q, r, l, beta, exact, cons, bound

bad = []
eq_exact = []
eq_cons = []
min_dbe = None; min_dbc = None
cells = {}
HDR = "  n  np   d  q   r       N       beta      exact       cons        b-e        b-c    bound chk"
print(HDR)
for row in rows:
    n, npr, d, N = row["n"], row["n_prime"], row["d"], row["N"]
    q, r, l, beta, exact, cons, bound = recompute(n, npr, d)
    dbe, dbc = beta - exact, beta - cons
    ok = []
    if row["q"] != q: ok.append("q")
    if row["r"] != r: ok.append("r")
    if abs(float(beta) - row["beta"]) > 1e-12: ok.append("beta")
    if abs(float(exact) - row["corollary_exact"]) > 1e-12: ok.append("exact")
    if abs(float(cons) - row["corollary_conservative"]) > 1e-12: ok.append("cons")
    if abs(float(dbe) - row["beta_minus_exact"]) > 1e-12: ok.append("b-e")
    if abs(float(dbc) - row["beta_minus_conservative"]) > 1e-12: ok.append("b-c")
    if row["bound"] != bound: ok.append("bound")
    if N != 2 ** npr: ok.append("N!=2^n'")
    if dbe < 0: ok.append("F2-EXACT-BREACH")
    if dbc < 0: ok.append("F2-CONS-BREACH")
    # decidability of the weaken/reject split (J3(d))
    for k in ("beta", "corollary_exact", "corollary_conservative",
              "beta_minus_exact", "beta_minus_conservative"):
        if row.get(k) is None: ok.append("missing:" + k)
    if ok: bad.append((row, ok))
    if dbe == 0: eq_exact.append(row)
    if dbc == 0: eq_cons.append(row)
    min_dbe = dbe if min_dbe is None or dbe < min_dbe else min_dbe
    min_dbc = dbc if min_dbc is None or dbc < min_dbc else min_dbc
    cells.setdefault((n, npr), []).append(d)
    print(f"{n:>3} {npr:>3} {d:>3} {q:>2} {r:>3} {N:>7} {float(beta):>10.6f} {float(exact):>10.6f} "
          f"{float(cons):>10.6f} {float(dbe):>10.6f} {float(dbc):>10.6f} {bound:>8} {'OK' if not ok else ','.join(ok)}")

print()
print("rows recomputed                      :", len(rows))
print("rows disagreeing with the archive    :", len(bad))
print("min(beta - exact)  recomputed        :", min_dbe, "=", float(min_dbe))
print("min(beta - conservative) recomputed  :", min_dbc, "=", float(min_dbc))
print("archived min(beta-exact)             :", raw["tail_checks"]["minimum_beta_minus_exact_over_complete_splitters"])
print("archived min(beta-conservative)      :", raw["tail_checks"]["minimum_beta_minus_conservative_over_complete_splitters"])
print("rows with beta == exact (EQUALITY)   :", len(eq_exact))
print("   their (n,n',d):", sorted({(r_["n"], r_["n_prime"], r_["d"]) for r_ in eq_exact}))
print("   per (n,n',d) counts:", {k: sum(1 for r_ in eq_exact if (r_['n'],r_['n_prime'],r_['d'])==k)
                                  for k in sorted({(r_['n'],r_['n_prime'],r_['d']) for r_ in eq_exact})})
print("archived rows literally carrying beta_minus_exact == 0.0 :",
      sum(1 for r_ in rows if r_["beta_minus_exact"] == 0.0))
print("complete-splitter cells and counts   :",
      {k: len(v) for k, v in sorted(cells.items())})
print()
# J3(d): are BOTH thresholds recorded on every complete splitter AND every near-complete row?
miss_c = sum(1 for r_ in rows if r_.get("corollary_exact") is None or r_.get("corollary_conservative") is None)
miss_n = sum(1 for r_ in near if r_.get("corollary_exact") is None or r_.get("corollary_conservative") is None)
print("complete splitters missing a threshold:", miss_c)
print("near-complete rows missing a threshold:", miss_n, "of", len(near))
# I3 coverage on the 65 (the AMD-20260917-001 cap)
i3_off = [r_ for r_ in rows if not r_.get("i3_run")]
print("complete splitters with i3_run False  :", len(i3_off),
      "->", sorted({(r_["n"], r_["n_prime"], r_["d"], r_["N"]) for r_ in i3_off}))
