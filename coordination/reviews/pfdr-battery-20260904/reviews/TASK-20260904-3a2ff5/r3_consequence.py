"""R3 consequence: the measured solving degree D_0(s) = d_lf = d_ff = 4 + floor(s/2) at
m = 2, d = 2, and what it does to IDEA-20260830-84cdb7's conditional exponent and to
EXP-PFDR-c04716's D_0 requirement.  TASK-20260904-3a2ff5 (derivation, not a run)."""
import json, math, os
from math import comb, log2
OUT = "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5"

def H(x): return -x*log2(x) - (1-x)*log2(1-x)
rows = []
for s in list(range(2, 13)) + [16, 20, 32, 64, 128]:
    n = 2*s
    D = 4 + s//2
    ND = sum(comb(n, j) for j in range(0, min(D, n)+1))
    B = 2**s
    rows.append({"s": s, "n_vars": n, "D_0 = d_lf = d_ff": D, "columns N_D": ND,
                 "log2 N_D": round(log2(ND), 3), "log_B(N_D)": round(log2(ND)/s, 4),
                 "linear-algebra exponent in B at omega=2": round(2*log2(ND)/s, 4),
                 "enumeration exponent in B": 1.0,
                 "D/n": round(D/n, 4), "2H(D/n)": round(2*H(D/n), 4) if 0 < D/n < 1 else None})
asym = {"limit D/n": 0.25, "2H(1/4)": round(2*H(0.25), 4),
        "columns ~ B^{2H(1/4)}": round(2*H(0.25), 4),
        "cost at omega=2 ~ B^{...}": round(4*H(0.25), 4),
        "cost at omega=2.807 ~ B^{...}": round(2*H(0.25)*2.807, 4)}
c04716 = {"D_0 required to beat rho (c04716 STATIC-001 thresholds)":
          {"256 bits, m=3": "T >= rho already at D_0 = 2",
           "256 bits, m=4, omega=2": "largest even D_0 with T < rho: 2",
           "256 bits, m=5, omega=2": "largest even D_0 with T < rho: 8",
           "256 bits, m=5, omega=2.807": "largest even D_0 with T < rho: 4"},
          "measured/derived D_0 at m=2": "4 + floor(s/2): 5,5,6,6,7,7,... exceeds 6 from s = 6",
          "derived d_ff at m>=3 (H-PFDR-4148b8, status specified)":
              {f"m={m}": f"{m*2**(m-1)} + floor((s-{2**(m-1)})/2) + 1 for s >= {2**(m-1)}"
               for m in (3, 4, 5)}}
out = {"table": rows, "asymptotics": asym, "cost_table_consequence": c04716,
       "note": "d_lf >= d_ff always; so ANY growth of d_ff in s refutes a uniform bound on "
               "d_lf without measuring d_lf at all.  The d_lf ladder's own contribution is "
               "only the upper direction d_lf = d_ff (no cascade beyond the first fall)."}
json.dump(out, open(os.path.join(OUT, "r3_consequence.json"), "w"), indent=1)
for r in rows[:12] + rows[12:]:
    print(r)
print(asym)
