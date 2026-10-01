"""How surprising is 'exactly one of the 30 U-labelled targets is decomposable'?
Under the generator's declared procedure (find_points.sage second loop: n uniform
random bits per target, no root test) each U target is a uniform element of
F_{2^n}, so the number of decomposable U targets per cell is Binomial(10, p_cell)
with p_cell = fraction of x_R in F_{2^n} admitting an S_4 decomposition with
x1,x2,x3 in V on E or on the twist coset (v1_target_fractions_*.json, exact
counts). Poisson-binomial over the three cells. Validator's own arithmetic; the
fractions are exact, the model assumption (uniform, independent targets) is the
generator's stated procedure, not a verified fact."""
import json, os
from itertools import product
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
cells = ["n15l5", "n17l6", "n19l6"]
frac = {}
for c in cells:
    d = json.load(open(f"{HERE}/v1_target_fractions_{c}.json"))
    N = 1 << d["n"]
    fE, fT = d["E"]["decomposable_targets_xR"] / N, d["twist"]["decomposable_targets_xR"] / N
    frac[c] = (fE, fT, fE + fT)

def binom_pmf(k, n, p): return comb(n, k) * p ** k * (1 - p) ** (n - k)

def dist(ps, n=10):
    # distribution of total count over cells, each Binomial(n, p_cell)
    tot = {0: 1.0}
    for p in ps:
        new = {}
        for k, pk in tot.items():
            for j in range(n + 1):
                new[k + j] = new.get(k + j, 0.0) + pk * binom_pmf(j, n, p)
        tot = new
    return tot

either = [frac[c][2] for c in cells]
E_only = [frac[c][0] for c in cells]
twist_only = [frac[c][1] for c in cells]
d_either = dist(either); d_E = dist(E_only); d_T = dist(twist_only)
observed = {"n15l5": 0, "n17l6": 0, "n19l6": 1}   # v1_decomp_search_*.json: U instances with a decomposition
p_pattern = 1.0
for c, k in observed.items():
    p_pattern *= binom_pmf(k, 10, frac[c][2])

out = {
    "fractions_(E,twist,either)": {c: list(frac[c]) for c in cells},
    "expected_SAT_U_instances_of_30_uniform_targets_either_kind": 10 * sum(either),
    "P_observed_pattern_(0,0,1)": p_pattern,
    "P_total_at_most_1": d_either[0] + d_either[1],
    "P_total_exactly_0": d_either[0],
    "expected_E_only": 10 * sum(E_only),
    "P_total_at_most_1_E_only": d_E[0] + d_E[1],
    "expected_twist_only (if U targets had been screened against E-decompositions only)": 10 * sum(twist_only),
    "P_total_at_most_1_twist_only": d_T[0] + d_T[1],
    "model": "U targets uniform in F_{2^n} and independent, as the generator's second loop states; 10 per cell",
}
json.dump(out, open(f"{HERE}/v1_u_label_probability.json", "w"), indent=1)
print(json.dumps(out, indent=1))
