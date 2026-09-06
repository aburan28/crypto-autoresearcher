"""
EXP-MLKEM-12d9b8 closed-form realizability computation.
Exact integer arithmetic only (Python arbitrary-precision ints). No ML-KEM
implementation, no lattice software, no simulation, no attack.

Symbol-collision discipline: k_simon (Simon's own internal group/repetition
parameter, k_simon > c) and k_mlkem (ML-KEM module rank, in {2,3,4}) are
NEVER the same variable and are always printed with these exact names.
"""
import json
from fractions import Fraction

# ---------------------------------------------------------------------
# ML-KEM standardized parameters (FIPS 203), per specification.yaml inputs
# ---------------------------------------------------------------------
ML_KEM_PARAMS = {
    "ML-KEM-512":  {"k_mlkem": 2, "q": 3329, "eta1": 3, "eta2": 2},
    "ML-KEM-768":  {"k_mlkem": 3, "q": 3329, "eta1": 2, "eta2": 2},
    "ML-KEM-1024": {"k_mlkem": 4, "q": 3329, "eta1": 2, "eta2": 2},
}

C_SWEEP = [12, 13, 15, 20]
B_GRID_EXTREME = None  # set per-level: [1, q] per amendment MLKEM-CHG-2

# ---------------------------------------------------------------------
# Stage 1: variance formula + baseline-embedding control
#   Var(sum_i c_i * e_i) = sum_i c_i^2 * Var(e_i), e_i ~ CBD(eta) independent.
#   Var(CBD(eta)) = eta/2 exact (spec inputs.ml_kem_parameters.cbd_variance_formula)
# ---------------------------------------------------------------------
def variance_formula(coeffs, eta):
    """Exact variance (as Fraction) of sum_i c_i*e_i, e_i ~ CBD(eta) i.i.d."""
    var_e = Fraction(eta, 2)
    return sum(Fraction(c) ** 2 for c in coeffs) * var_e

def stage1_baseline_checks(eta):
    # m = 1, c_1 = 1 (zero inflation case): expect exactly eta/2
    v_m1 = variance_formula([1], eta)
    check_m1 = (v_m1 == Fraction(eta, 2))
    # m = 2, unit coefficients c_1=c_2=1: expect exactly eta (CBD convolution property)
    v_m2 = variance_formula([1, 1], eta)
    check_m2 = (v_m2 == Fraction(eta))
    return {
        "eta": eta,
        "m1_variance": str(v_m1),
        "m1_expected": str(Fraction(eta, 2)),
        "m1_check_pass": check_m1,
        "m2_variance": str(v_m2),
        "m2_expected": str(Fraction(eta)),
        "m2_check_pass": check_m2,
    }

# ---------------------------------------------------------------------
# Stage 2: Q table.  Q = k_simon * n^(c+1), n := k_mlkem * 256 (working def).
#   NOTE: here "k_simon" in the formula Q = k * n^(c+1) is SIMON'S OWN k
#   (k_simon > c). specification.yaml's preregistered_prediction.formula
#   substitutes k_mlkem for k_simon inside the Q formula
#   ("Q = k_mlkem * (k_mlkem*256)^(c+1)"); this is the contract's own stated
#   formula (metrics.primary Q_table item; preregistered_prediction.formula
#   (i)) and is reproduced exactly as written, with the substitution flagged
#   here for the symbol-collision audit: the contract's formula literally
#   reuses the numeral k_mlkem in the "k" slot of Simon's formula, which is
#   the SAME kind of working substitution as n := k_mlkem*256, disclosed as
#   such in the contract text; we do not silently invent a k_simon value.
# ---------------------------------------------------------------------
def q_table():
    table = {}
    for level, params in ML_KEM_PARAMS.items():
        k_mlkem = params["k_mlkem"]
        n = k_mlkem * 256
        table[level] = {}
        for c in C_SWEEP:
            Q = k_mlkem * (n ** (c + 1))
            table[level][c] = {"n": n, "Q": Q, "Q_str": str(Q), "Q_digits": len(str(Q))}
    return table

# ---------------------------------------------------------------------
# Stage 2b: trivial-floor control -- Q <= k_mlkem realizable without
# self-reduction (using all k_mlkem real rows directly, m = k_mlkem, B
# irrelevant since coefficients are unit/identity).
# ---------------------------------------------------------------------
def trivial_floor_check(qt):
    out = {}
    for level, params in ML_KEM_PARAMS.items():
        k_mlkem = params["k_mlkem"]
        results = {}
        for c in C_SWEEP:
            Q = qt[level][c]["Q"]
            results[c] = {
                "Q": Q,
                "k_mlkem": k_mlkem,
                "Q_le_k_mlkem": Q <= k_mlkem,
                "note": ("trivially realizable without self-reduction (Q <= k_mlkem)"
                         if Q <= k_mlkem else
                         "Q > k_mlkem: self-reduction would be required IF Q were "
                         "to be reached; floor case does not apply at this c"),
            }
        out[level] = results
    return out

# ---------------------------------------------------------------------
# Stage 3: combinatorial ceiling.
#   combinatorial_ceiling <= (2B+1)^k_mlkem (spec preregistered_prediction (ii))
#   Extreme-B check per amendment MLKEM-CHG-2: B = 1 and B = q (CAPPED, no
#   search beyond q).
# ---------------------------------------------------------------------
def combinatorial_ceiling(B, k_mlkem):
    return (2 * B + 1) ** k_mlkem

def stage3_ceilings():
    out = {}
    for level, params in ML_KEM_PARAMS.items():
        k_mlkem = params["k_mlkem"]
        q = params["q"]
        out[level] = {
            "k_mlkem": k_mlkem,
            "q": q,
            "B_grid": [1, q],
            "ceiling_at_B": {
                1: combinatorial_ceiling(1, k_mlkem),
                q: combinatorial_ceiling(q, k_mlkem),
            },
        }
    return out

# ---------------------------------------------------------------------
# Stage 4: realizability verdict = ceiling(B=q) vs Q(level, c), per level per c.
#   B = q is the operative ceiling per amendment MLKEM-CHG-2 (do not search B>q).
#   REALIZABLE iff ceiling_at_Bq >= Q for that (level, c); else UNREALIZABLE,
#   on the combinatorial-ceiling axis alone (independent of stage 0).
# ---------------------------------------------------------------------
def realizability_verdict(qt, ceilings):
    out = {}
    for level in ML_KEM_PARAMS:
        k_mlkem = ML_KEM_PARAMS[level]["k_mlkem"]
        ceiling_Bq = ceilings[level]["ceiling_at_B"][ML_KEM_PARAMS[level]["q"]]
        ceiling_B1 = ceilings[level]["ceiling_at_B"][1]
        level_out = {}
        for c in C_SWEEP:
            Q = qt[level][c]["Q"]
            verdict = "REALIZABLE" if ceiling_Bq >= Q else "UNREALIZABLE"
            margin = ceiling_Bq - Q  # negative => shortfall; the "exact numeric margin"
            level_out[c] = {
                "Q": Q,
                "combinatorial_ceiling_B1": ceiling_B1,
                "combinatorial_ceiling_Bq": ceiling_Bq,
                "verdict_on_combinatorial_axis": verdict,
                "margin_Bq_minus_Q": margin,
                "margin_digits": len(str(abs(margin))),
                "orders_of_magnitude_shortfall_approx": (
                    len(str(Q)) - len(str(ceiling_Bq)) if verdict == "UNREALIZABLE" else 0
                ),
            }
        out[level] = level_out
    return out

if __name__ == "__main__":
    result = {}

    # Stage 1
    stage1 = {}
    for level, params in ML_KEM_PARAMS.items():
        stage1[level] = {
            "eta1": stage1_baseline_checks(params["eta1"]),
            "eta2": stage1_baseline_checks(params["eta2"]),
        }
    result["stage1_baseline_embedding_control"] = stage1
    all_pass = all(
        v["eta1"]["m1_check_pass"] and v["eta1"]["m2_check_pass"] and
        v["eta2"]["m1_check_pass"] and v["eta2"]["m2_check_pass"]
        for v in stage1.values()
    )
    result["stage1_all_checks_pass"] = all_pass

    # Stage 2
    qt = q_table()
    result["stage2_Q_table"] = qt
    result["stage2b_trivial_floor_check"] = trivial_floor_check(qt)

    # Stage 3
    ceilings = stage3_ceilings()
    result["stage3_combinatorial_ceiling"] = ceilings

    # Stage 4
    verdicts = realizability_verdict(qt, ceilings)
    result["stage4_realizability_verdict"] = verdicts

    # Overall per-level verdict robustness across c sweep
    overall = {}
    for level in ML_KEM_PARAMS:
        vs = set(verdicts[level][c]["verdict_on_combinatorial_axis"] for c in C_SWEEP)
        overall[level] = {
            "verdicts_across_c_sweep": {c: verdicts[level][c]["verdict_on_combinatorial_axis"] for c in C_SWEEP},
            "robust_single_verdict": vs.pop() if len(vs) == 1 else sorted(vs),
        }
    result["overall_verdict_by_level"] = overall

    print(json.dumps(result, indent=2, default=str))
