"""Summary checks over rt_probe_output.json (null vs analytic 1/p; multiplier-set pattern)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
o = json.load(open(os.path.join(HERE, "rt_probe_output.json")))
rows = o["B_rows"]
an = sum(r["lifts"]["recorded"]["naive"]["cells"] / r["p"] for r in rows)
sim = sum(r["null_mean"] for r in rows)
print(f"analytic sum cells/p = {an:.1f}; simulated random-odd-function null mean = {sim:.1f}; ratio {sim/an:.4f}")
j0 = [r for r in rows if r["A"] == 0]
ok = 0
for r in j0:
    lam, n, p, z = r["j0_lambda"], r["n"], r["p"], r["j0_zeta_teich_mod_p"]
    mt = dict((d, c) for d, c in r["lifts"]["recorded"]["teichmuller"]["multiplier_set"])
    mp = [d for d, _ in r["lifts"]["perturbed"]["teichmuller"]["multiplier_set"]]
    exp = sorted({lam, lam * lam % n, (n - lam) % n, (n - lam * lam % n) % n, n - 1})
    ok += sorted(mt) == exp and mt[lam] == z and mt[lam * lam % n] == z * z % p and mt[n - 1] == p - 1 and mp == [n - 1]
print(f"j=0 curves: {len(j0)}; canonical-lift Teichmuller multiplier set == mu_6 minus 1 with ratio = matching root of unity mod p, "
      f"and perturbed-lift set == {{-1}}: {ok} of {len(j0)}")
nonj0 = [r for r in rows if r["A"] != 0]
print("non-j=0 curves, both lifts, both sections, multiplier set == {-1}:",
      all([d for d, _ in r["lifts"][l][s]["multiplier_set"]] == [r["n"] - 1]
          for r in nonj0 for l in ("recorded", "perturbed") for s in ("naive", "teichmuller")))
print("j=0 curves, naive section, both lifts, multiplier set == {-1}:",
      all([d for d, _ in r["lifts"][l]["naive"]["multiplier_set"]] == [r["n"] - 1] for r in j0 for l in ("recorded", "perturbed")))
print("distinct curves:", len(rows), "| cells per section-lift:", sum(r["lifts"]["recorded"]["naive"]["cells"] for r in rows))
