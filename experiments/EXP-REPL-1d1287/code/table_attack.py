"""
C5: table-based preprocessing attack reproduction (baby-step giant-step,
Shanks). This is a classical S,T time-memory tradeoff for discrete log in a
generic group: precompute S = ceil(sqrt(N)) baby steps once (the "table"),
then each online query costs T online group operations to recover any
logarithm, with the empirical relation S*T ~= N (S=T=O(sqrt(N))).

This is the REPRODUCED, MEASURED attack used for the (S,T) frontier
placement of every trained model. It is a legitimate precomputation attack
achieving the classical Shanks tradeoff; the asymptotically tighter
Corrigan-Gibbs-Kogan generic-preprocessing bound S*T^2 = Omega(N) that the
trained models are compared against is used as the MODELED bound curve only
(per spec: measured and modeled numbers never share a column). BSGS's
(S,T)=(sqrt(N),sqrt(N)) satisfies S*T^2 = N^1.5 >= N, i.e. sits safely
inside/above the bound rather than saturating it -- documented as a scope
limitation of this reproduction, not a tight-frontier attack.
"""
import json, math, random, time
from ec import load_curves, ec_add, ec_mul

def bsgs_table(curve):
    N = curve.N
    m = math.ceil(math.sqrt(N))
    table = {}
    P = None
    for j in range(m):
        table[P] = j
        P = ec_add(P, curve.G, curve.a, curve.p)
    return table, m

def bsgs_solve(curve, table, m, Y):
    # giant stride = -m*G
    mG = ec_mul(m, curve.G, curve.a, curve.p)
    neg_mG = (mG[0], (-mG[1]) % curve.p) if mG else None
    cur = Y
    steps = 0
    for i in range(m + 1):
        if cur in table:
            j = table[cur]
            k = (i * m + j) % curve.N
            return k, steps + 1
        cur = ec_add(cur, neg_mG, curve.a, curve.p)
        steps += 1
    return None, steps

def run_c5(curve_name, n_targets=30, seed=999):
    curves = load_curves()
    curve = curves[curve_name]
    t0 = time.time()
    table, m = bsgs_table(curve)
    table_build_seconds = time.time() - t0

    rng = random.Random(seed)
    targets = [rng.randrange(curve.N) for _ in range(n_targets)]
    steps_list = []
    correct = 0
    for k_true in targets:
        Y = curve.scalar_mul(k_true)
        k_rec, steps = bsgs_solve(curve, table, m, Y)
        steps_list.append(steps)
        if k_rec == k_true:
            correct += 1

    S_entries = len(table)
    bits_per_entry = curve.p.bit_length() * 2 + curve.N.bit_length()  # (x,y) key + index value
    S_bits = S_entries * bits_per_entry
    T_mean = sum(steps_list) / len(steps_list)
    T_max = max(steps_list)

    result = {
        "curve": curve_name, "N": curve.N,
        "S_entries": S_entries, "S_bits": S_bits,
        "T_mean_group_ops": T_mean, "T_max_group_ops": T_max,
        "predicted_T_sqrtN": math.sqrt(curve.N),
        "predicted_S_sqrtN": math.sqrt(curve.N),
        "S_times_T_measured": S_entries * T_mean,
        "N": curve.N,
        "n_targets_tested": n_targets,
        "n_correctly_recovered": correct,
        "success_rate": correct / n_targets,
        "table_build_seconds": table_build_seconds,
        "attack_type": "classical_Shanks_BSGS",
        "note": (
            "Reproduces the classical S=T=O(sqrt(N)), S*T=N Shanks tradeoff. "
            "Used as the measured point on the (S,T) frontier plot; the "
            "S*T^2=Omega(N) generic-preprocessing bound remains the modeled "
            "curve per the measured_vs_modeled separation in the spec."
        ),
    }
    return result

if __name__ == "__main__":
    out = {}
    for cname in ["curve_1", "curve_2"]:
        out[cname] = run_c5(cname)
        print(cname, out[cname]["success_rate"], out[cname]["T_mean_group_ops"], out[cname]["S_entries"])
    with open("/tmp/wt-run-exp/experiments/EXP-REPL-1d1287/c5-table-attack.json", "w") as f:
        json.dump(out, f, indent=2)
