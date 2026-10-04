"""J2 (1): own field and curve checks. Output: field_curve_checks.json (next to this file)."""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gf219 as G  # noqa: E402

out = {}

# (a) modulus irreducible (Rabin / C-SELF (i) form) and via the multiplicative-order route
ok, top, gcds = G.irreducibility_rabin(G.F_POLY)
out["modulus_int"] = G.F_POLY
out["modulus_irreducible_gcd_test"] = {"t^(2^19)=t": top, "gcd_i_1..9_all_1": all(g == 1 for g in gcds.values()), "irreducible": ok}
out["mersenne_2^19-1_prime"] = G.is_prime(G.ORD)
# tables built => t^(2^19-1) = 1 and powers of t hit every nonzero residue => every nonzero residue is a unit => field
out["powers_of_t_cover_all_nonzero_residues"] = bool((G.LOG[1:] >= 0).all())

# (b) the four lexicographically smaller pentanomials t^19 + t^a + t^b + t^c + 1 are reducible
smaller = []
for (a, b, c) in [(3, 2, 1), (4, 2, 1), (4, 3, 1), (4, 3, 2)]:
    m = (1 << 19) | (1 << a) | (1 << b) | (1 << c) | 1
    ok2, top2, gcds2 = G.irreducibility_rabin(m)
    witness = {str(i): g for i, g in gcds2.items() if g != 1}
    smaller.append({"abc": [a, b, c], "irreducible": ok2, "t^(2^19)=t": top2, "nontrivial_gcd_witness_i_to_factor": witness})
out["smaller_pentanomials"] = smaller
# (5,2,1) is the first candidate after those four
out["lexicographic_order_note"] = "candidates (a>b>c>=1) in lexicographic order: (3,2,1),(4,2,1),(4,3,1),(4,3,2),(5,2,1)"

# (c) field-mult table vs carryless multiply on random pairs
rng = random.Random(4242)
bad = 0
for _ in range(20000):
    x = rng.randrange(1 << 19)
    y = rng.randrange(1 << 19)
    if G.fmul(x, y) != G.mulmod(x, y):
        bad += 1
out["table_mult_vs_clmul_mismatches_20000"] = bad
# field axioms on 10^4 random triples
bad = 0
for _ in range(10000):
    x, y, z = (rng.randrange(1 << 19) for _ in range(3))
    if G.fmul(x, G.fmul(y, z)) != G.fmul(G.fmul(x, y), z):
        bad += 1
    if G.fmul(x, y ^ z) != G.fmul(x, y) ^ G.fmul(x, z):
        bad += 1
    if x and G.fmul(x, G.finv(x)) != 1:
        bad += 1
out["field_axiom_failures_10000_triples"] = bad

# (d) Tr(t^j), j < 19
out["tau_Tr_t^j"] = G.TAU
out["tau_ones_at"] = [j for j in range(19) if G.TAU[j]]
out["tau_matches_spec_reading_(j=0,17)"] = [j for j in range(19) if G.TAU[j]] == [0, 17]
# linear trace equals direct trace on random elements
bad = sum(1 for _ in range(2000) for z in [rng.randrange(1 << 19)] if G.tr(z) != G.trace_direct(z))
out["linear_trace_vs_direct_mismatches_2000"] = bad
ell_lin_vars = []
for j in range(10):
    if G.TAU[j]:
        ell_lin_vars += [j, 10 + j]
out["ell_lin_variables"] = ell_lin_vars

# (e) curve: B != 0, #E by trace count, q prime, P, Q, Q = [5170]P, Tr(A)
import numpy as np  # noqa: E402
xs = np.arange(1, 1 << 19, dtype=np.int64)
w = xs ^ G.A_CURVE ^ G.vmulc(G.vsq(G.EXP[(G.ORD - G.LOG[xs]) % G.ORD]), G.B_CURVE)
cnt0 = int((G.vtr(w) == 0).sum())
nE = 1 + 1 + 2 * cnt0
out["B_nonzero"] = G.B_CURVE != 0
out["order_by_trace_count"] = nE
out["order_equals_523646"] = nE == 523646
out["order_factor"] = [2, G.Q_ORDER] if nE == 2 * G.Q_ORDER else None
out["q_prime"] = G.is_prime(G.Q_ORDER)
out["h"] = nE // G.Q_ORDER if nE % G.Q_ORDER == 0 else None
P = G.P_PT
Q = G.Q_PT
out["P_on_curve"] = G.on_curve(P)
out["Q_on_curve"] = G.on_curve(Q)
out["qP_is_O"] = G.smul(G.Q_ORDER, P) is None
out["qQ_is_O"] = G.smul(G.Q_ORDER, Q) is None
out["P_not_O"] = P is not None
out["Q_eq_5170P"] = G.smul(G.K_Q, P) == Q
out["Tr_A"] = G.tr(G.A_CURVE)
# group-law self-checks: [#E] of random points is O; S_3 relation on random point pairs
bad_order = 0
bad_s3 = 0
for _ in range(300):
    while True:
        x = rng.randrange(1, 1 << 19)
        R = G.lift_x(x)
        if R is not None:
            break
    if G.smul(nE, R) is not None:
        bad_order += 1
    while True:
        x2 = rng.randrange(1, 1 << 19)
        R2 = G.lift_x(x2)
        if R2 is not None and x2 != x:
            break
    for S in (G.padd(R, R2), G.padd(R, G.pneg(R2))):
        if S is not None and G.S3(R[0], R2[0], S[0]) != 0:
            bad_s3 += 1
out["random_points_order_divides_#E_failures_300"] = bad_order
out["S3(x1,x2,x(P1+-P2))=0_failures_600"] = bad_s3
# scalar-mult consistency: [a]P + [b]P = [a+b]P
bad = 0
for _ in range(200):
    a = rng.randrange(G.Q_ORDER)
    b = rng.randrange(G.Q_ORDER)
    if G.padd(G.smul(a, P), G.smul(b, P)) != G.smul((a + b) % G.Q_ORDER, P):
        bad += 1
out["scalar_mult_additivity_failures_200"] = bad
# 2E membership criterion Tr(x) == Tr(A) on random non-twist x (C-TR19 statement, own check)
bad = 0
n_checked = 0
for _ in range(400):
    x = rng.randrange(1, 1 << 19)
    R = G.lift_x(x)
    if R is None:
        continue
    n_checked += 1
    in2E = G.smul(G.Q_ORDER, R) is None
    if in2E != (G.tr(x) == G.tr(G.A_CURVE)):
        bad += 1
out["2E_iff_TrX_eq_TrA_checked"] = n_checked
out["2E_iff_TrX_eq_TrA_failures"] = bad

# S_3 descent: my Moebius interpolation is exact (degree <= 2) -- checked at random points for random x_R
bad = 0
for _ in range(50):
    xR = rng.randrange(1024, 1 << 19)
    E = G.descend_E(xR)
    for _ in range(40):
        v = rng.randrange(1 << 20)
        if G.eval_E_at(E, v) != G.S3(v & 1023, v >> 10, xR):
            bad += 1
out["descent_vs_direct_S3_eval_failures_2000"] = bad
# two routes to s on random x_R
bad = 0
for _ in range(20):
    xR = rng.randrange(1024, 1 << 19)
    s1, sol1 = G.s_bruteforce(xR, True)
    s2, sol2 = G.s_quadratic(xR)
    E = G.descend_E(xR)
    s3, sol3 = G.s_system(E, True)
    if not (s1 == s2 == s3 and sol1 == sol2 == sol3):
        bad += 1
out["s_three_routes_disagreements_20"] = bad

out["all_pass"] = bool(
    out["modulus_irreducible_gcd_test"]["irreducible"] and out["powers_of_t_cover_all_nonzero_residues"]
    and all(not s["irreducible"] for s in smaller)
    and out["order_equals_523646"] and out["q_prime"] and out["P_on_curve"] and out["Q_on_curve"]
    and out["qP_is_O"] and out["qQ_is_O"] and out["Q_eq_5170P"] and out["Tr_A"] == 1
    and out["table_mult_vs_clmul_mismatches_20000"] == 0 and out["field_axiom_failures_10000_triples"] == 0
    and out["random_points_order_divides_#E_failures_300"] == 0 and out["S3(x1,x2,x(P1+-P2))=0_failures_600"] == 0
    and out["2E_iff_TrX_eq_TrA_failures"] == 0 and out["descent_vs_direct_S3_eval_failures_2000"] == 0
    and out["s_three_routes_disagreements_20"] == 0 and out["scalar_mult_additivity_failures_200"] == 0
)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_curve_checks.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
