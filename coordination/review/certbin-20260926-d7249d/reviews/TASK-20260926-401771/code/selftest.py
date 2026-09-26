"""VC-1 self-tests of the J1 verifier's own construction. Writes work/selftest.json.
Seed for every random choice here: numpy PCG64(20260926401771)."""
import functools
import json
import sys
import time

import numpy as np

import certs
import descent
import gf19
import kern
import layout as LY

A_LIT, B_LIT = 46693, 306147
P_LIT, Q_LIT = (82737, 282850), (510336, 243234)
Q_ORD, KQ = 261823, 5170
SEED = 20260926401771

g = np.random.Generator(np.random.PCG64(SEED))
res = {"seed": SEED}
t0 = time.time()


def rint(n):
    return int(g.integers(0, n))


# ---------------------------------------------------------------- field
f = {}
f["modulus"] = gf19.MOD
f["modulus_irreducible"] = gf19.irreducible(gf19.MOD)
smaller = {}
for (a, b, c) in [(3, 2, 1), (4, 2, 1), (4, 3, 1), (4, 3, 2)]:
    poly = (1 << 19) | (1 << a) | (1 << b) | (1 << c) | 1
    smaller["t^19+t^%d+t^%d+t^%d+1" % (a, b, c)] = "reducible" if not gf19.irreducible(poly) else "IRREDUCIBLE"
f["smaller_pentanomials"] = smaller
bad = 0
for _ in range(10000):
    a, b, c = rint(1 << 19), rint(1 << 19), rint(1 << 19)
    m = gf19.mul
    if m(a, b) != m(b, a) or m(m(a, b), c) != m(a, m(b, c)) or m(a, b ^ c) != m(a, b) ^ m(a, c):
        bad += 1
    if a and m(a, gf19.inv(a)) != 1:
        bad += 1
f["axioms_10000_triples_failures"] = bad
L = kern.lib()
badc = 0
for _ in range(100000):
    a, b = rint(1 << 19), rint(1 << 19)
    if L.k_gfmul(a, b) != gf19.mul(a, b):
        badc += 1
f["C_mul_vs_python_mul_100000_pairs_mismatches"] = badc
f["t19_reduces_to"] = gf19.mul(1 << 18, 2)  # t^19 = t^5 + t^2 + t + 1 = 39
f["pass"] = (f["modulus_irreducible"] and all(v == "reducible" for v in smaller.values()) and bad == 0
             and badc == 0 and f["t19_reduces_to"] == 39)
res["field"] = f

# ---------------------------------------------------------------- curve
E = gf19.Curve(A_LIT, B_LIT)
c = {}
c["P_on_curve"] = E.on_curve(P_LIT)
c["Q_on_curve"] = E.on_curve(Q_LIT)
c["qP_is_O"] = E.mult(Q_ORD, P_LIT) is None
c["qQ_is_O"] = E.mult(Q_ORD, Q_LIT) is None
c["Q_eq_5170P"] = E.mult(KQ, P_LIT) == Q_LIT
c["q_prime"] = all(Q_ORD % d for d in range(2, int(Q_ORD ** 0.5) + 1))
c["Tr_A"] = gf19.trace(A_LIT)
c["tau_Tr_t^j_j0..18"] = [gf19.trace(1 << j) for j in range(19)]
# group-law sanity on random subgroup and random lifted points
assoc_bad = 0
for _ in range(30):
    pts = []
    while len(pts) < 3:
        P = E.lift_x(rint(1 << 19))
        if P is not None:
            pts.append(P)
    X, Y, Z = pts
    if E.add(E.add(X, Y), Z) != E.add(X, E.add(Y, Z)) or not E.on_curve(E.add(X, Y)):
        assoc_bad += 1
    if E.add(X, E.neg(X)) is not None or E.add(X, X) != E.double(X):
        assoc_bad += 1
c["group_law_30_triples_failures"] = assoc_bad
# S_3 on point pairs: 100 subgroup pairs from the literal P, Q and 100 pairs
# of lifted points of E; both x(P1 + P2) and x(P1 - P2).
s3_ok = 0
s3_total = 0
s3_random_x3_zero = 0
pairs_used = []
for i in range(200):
    if i < 100:
        P1 = E.add(E.mult(rint(Q_ORD), P_LIT), E.mult(rint(Q_ORD), Q_LIT))
        P2 = E.add(E.mult(rint(Q_ORD), P_LIT), E.mult(rint(Q_ORD), Q_LIT))
    else:
        P1 = P2 = None
        while P1 is None:
            P1 = E.lift_x(rint(1 << 19))
        while P2 is None:
            P2 = E.lift_x(rint(1 << 19))
    if P1 is None or P2 is None or P1[0] == P2[0]:
        continue
    for R in (E.add(P1, P2), E.add(P1, E.neg(P2))):
        s3_total += 1
        if R is not None and gf19.S3(P1[0], P2[0], R[0], B_LIT) == 0:
            s3_ok += 1
    if gf19.S3(P1[0], P2[0], rint(1 << 19), B_LIT) == 0:
        s3_random_x3_zero += 1
    if len(pairs_used) < 5:
        pairs_used.append([P1, P2])
c["S3_point_pairs_tested"] = s3_total
c["S3_vanishes"] = s3_ok
c["S3_on_random_x3_zero_count_of_200"] = s3_random_x3_zero
c["S3_example_pairs"] = pairs_used
c["pass"] = (c["P_on_curve"] and c["Q_on_curve"] and c["qP_is_O"] and c["qQ_is_O"] and c["Q_eq_5170P"]
             and c["q_prime"] and assoc_bad == 0 and s3_ok == s3_total and s3_total >= 200
             and s3_random_x3_zero < 10)
res["curve_and_S3"] = c

# ---------------------------------------------------------------- orders and codec
o = {}
o["E_layout_211_columns"] = len(LY.E_COLS) == 211
o["ann_coordinates"] = LY.NCOL4


def degrevlex_cmp(a, b):
    """EXP-CERTBIN-4e92d7: a > b iff deg a > deg b; or equal degree and, at the
    largest variable index where they differ, a does NOT contain v_i."""
    da, db = LY.popcount(a), LY.popcount(b)
    if da != db:
        return 1 if da > db else -1
    if a == b:
        return 0
    i = (a ^ b).bit_length() - 1
    return -1 if (a >> i) & 1 else 1


desc = sorted(LY.ANN_MASKS, key=functools.cmp_to_key(degrevlex_cmp), reverse=True)
o["ann_order_equals_descending_degrevlex_constant_last"] = desc == LY.ANN_MASKS
o["first_coordinate"] = [i for i in range(20) if (LY.ANN_MASKS[0] >> i) & 1]
o["last_coordinate_is_constant"] = LY.ANN_MASKS[-1] == 0
o["deg3_block_start"] = LY.DEG3_START
rt_bad = 0
for _ in range(200):
    Er = (g.integers(0, 2, size=(19, 211))).astype(np.uint8)
    h = LY.encode_E(Er)
    if not np.array_equal(LY.decode_E(h), Er):
        rt_bad += 1
o["codec_round_trip_200_failures"] = rt_bad
o["pass"] = (o["E_layout_211_columns"] and o["ann_coordinates"] == 6196 and
             o["ann_order_equals_descending_degrevlex_constant_last"] and o["last_coordinate_is_constant"]
             and rt_bad == 0)
res["orders_and_codec"] = o

# ---------------------------------------------------------------- descent routes
d = {}
xs = [0, 1, 1 << 18] + [rint(1 << 19) for _ in range(17)]
agree = 0
direct_bad = 0
for xR in xs:
    EA = descent.route_A(xR, B_LIT)
    EB, sdir = descent.route_B(xR, B_LIT)
    if np.array_equal(EA, EB):
        agree += 1
    # descended equations against direct evaluation at 50 random v
    for _ in range(50):
        u = rint(1 << 20)
        val = gf19.S3(u & 1023, (u >> 10) & 1023, xR, B_LIT)
        ev = descent.eval_system_at(EA, u)
        if any(((val >> k) & 1) != ev[k] for k in range(19)):
            direct_bad += 1
d["x_R_tested"] = len(xs)
d["route_A_eq_route_B"] = agree
d["direct_eval_mismatches_1000"] = direct_bad
d["pass"] = agree == len(xs) and direct_bad == 0
res["descent_two_routes"] = d

# ---------------------------------------------------------------- exhaustive s
s = {}
full_bad = 0
for t in range(4):
    Er = (g.random((19, 211)) < 0.3).astype(np.uint8)
    if t == 3:  # a satisfiable one: make it vanish at a planted point
        u0 = rint(1 << 20)
        ev = descent.eval_system_at(Er, u0)
        for k in range(19):
            if ev[k]:
                Er[k, 0] ^= 1
    sE, sol = descent.s_from_E(Er)
    # naive, vectorized per-assignment evaluation over all 2^20 points
    U = np.arange(1 << 20, dtype=np.int64)
    allzero = np.ones(1 << 20, dtype=bool)
    for k in range(19):
        acc = np.zeros(1 << 20, dtype=np.uint8)
        for j in np.flatnonzero(Er[k]):
            m = LY.E_MASKS[j]
            acc ^= ((U & m) == m).astype(np.uint8)
        allzero &= (acc == 0)
    if not np.array_equal(np.flatnonzero(allzero), sol):
        full_bad += 1
s["full_naive_vs_mobius_systems"] = 4
s["full_naive_vs_mobius_mismatches"] = full_bad
s["planted_system_s"] = sE
# 200 random systems: 64 random points each against the Moebius truth table
pt_bad = 0
for _ in range(200):
    Er = (g.random((19, 211)) < 0.3).astype(np.uint8)
    tt = kern.mobius(LY.anf_u32(Er), 20)
    for _ in range(64):
        u = rint(1 << 20)
        ev = descent.eval_system_at(Er, u)
        if any(((int(tt[u]) >> k) & 1) != ev[k] for k in range(19)):
            pt_bad += 1
s["random_systems_200_x64_points_mismatches"] = pt_bad
s["pass"] = full_bad == 0 and pt_bad == 0 and sE >= 1
res["exhaustive_s"] = s

# ---------------------------------------------------------------- ring arithmetic
r = {}
Er = (g.random((19, 211)) < 0.3).astype(np.uint8)
S = certs.System(Er)
rows = [(LY.mask_of(sorted(g.choice(20, size=rint(3), replace=False).tolist())), rint(19)) for _ in range(40)]
p = S.rows_poly(rows)
ttp = kern.mobius(p.astype(np.uint32), 20) & 1
# truth table of sum mu*f_k computed pointwise
ttf = kern.mobius(LY.anf_u32(Er), 20)
U = np.arange(1 << 20, dtype=np.int64)
acc = np.zeros(1 << 20, dtype=np.uint32)
for mu, k in rows:
    acc ^= (((U & mu) == mu).astype(np.uint32) & ((ttf >> k) & 1))
r["rows_poly_truth_table_equal"] = bool(np.array_equal(ttp, acc))
vj_ok = True
for j in (0, 7, 19):
    q = certs.times_vj(p, j)
    ttq = kern.mobius(q.astype(np.uint32), 20) & 1
    if not np.array_equal(ttq, ttp & ((U >> j) & 1).astype(np.uint32)):
        vj_ok = False
r["times_vj_truth_table_equal"] = vj_ok
r["idempotent_vj_vj"] = bool(np.array_equal(certs.times_vj(certs.times_vj(p, 3), 3), certs.times_vj(p, 3)))
r["pass"] = r["rows_poly_truth_table_equal"] and vj_ok and r["idempotent_vj_vj"]
res["ring"] = r

# ---------------------------------------------------------------- elimination
e = {}


def bigint_rank(dense):
    basis = {}
    rank = 0
    for row in dense:
        v = int("".join("1" if b else "0" for b in row[::-1]) or "0", 2)
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                rank += 1
                break
    return rank


rk_bad = 0
rref_bad = 0
for t in range(60):
    nr, nc = rint(150) + 1, rint(300) + 1
    dens = (g.random((nr, nc)) < g.random()).astype(np.uint8)
    if t % 5 == 0 and nr > 3:
        dens[-1] = dens[0] ^ dens[1]
    Rm, rk, piv = kern.rref(kern.pack_rows(dens, (nc + 63) // 64), nc)
    if rk != bigint_rank(dens):
        rk_bad += 1
    Rd = kern.unpack_rows(Rm, nc)
    # RREF properties: pivot 1s, zeros elsewhere in pivot columns, zero tail rows
    okp = all(Rd[i, piv[i]] == 1 and Rd[:, piv[i]].sum() == 1 for i in range(rk)) and not Rd[rk:].any()
    okp = okp and all(not Rd[i, :piv[i]].any() for i in range(rk))
    if not okp:
        rref_bad += 1
e["random_matrices"] = 60
e["rank_vs_independent_bigint_mismatches"] = rk_bad
e["rref_property_failures"] = rref_bad
# basis of S cap B_{<=3}: random L
Ld = (g.random((300, LY.NCOL4)) < 0.5).astype(np.uint8)
Lp = kern.pack_rows(Ld, LY.WORDS4)
Kp, r3 = certs.basis_S_deg3(Lp)
nchk, _, _ = kern.parity_check(Lp, Kp)
e["S3_basis_dim_equals_1351_minus_rank"] = int(Kp.shape[0]) == 1351 - r3
e["S3_basis_annihilated"] = nchk == 0
e["S3_basis_rank_full"] = kern.rref(Kp, LY.NCOL4)[1] == Kp.shape[0]
e["pass"] = rk_bad == 0 and rref_bad == 0 and e["S3_basis_dim_equals_1351_minus_rank"] and nchk == 0 and \
    e["S3_basis_rank_full"]
res["elimination"] = e

# ---------------------------------------------------------------- certificate checkers on small planted systems
k = {}
Ep = np.zeros((19, 211), dtype=np.uint8)
Ep[0, LY.E_COL_OF_MASK[1]] = 1                    # f_0 = v_0
Ep[1, LY.E_COL_OF_MASK[1 | 2]] = 1                # f_1 = v_0 v_1 + 1
Ep[1, 0] = 1
Sp = certs.System(Ep)
k["flat_positive"] = certs.check_flat(Sp, {"C": [[[], 1], [[1], 0]]})["verified"]
k["flat_negative_row_removed"] = certs.check_flat(Sp, {"C": [[[], 1]]})["verified"]
wd = {"D": 4, "nv": 20, "neq": 19, "output": 1,
      "nodes": [{"id": 0, "rows": [[[], 0]], "prods": []}, {"id": 1, "rows": [[[], 1]], "prods": [[1, 0]]}]}
k["wdag_positive"] = certs.check_wdag(Sp, wd)["verified"]
wd_bad = json.loads(json.dumps(wd))
wd_bad["nodes"][1]["prods"] = [[2, 0]]
k["wdag_negative_wrong_j"] = certs.check_wdag(Sp, wd_bad)["verified"]
# degree discipline: a prods child of degree 4 (inserted pair, sum unchanged)
Ep2 = Ep.copy()
Ep2[2, LY.E_COL_OF_MASK[(1 << 5) | (1 << 6)]] = 1  # f_2 = v_5 v_6
Sp2 = certs.System(Ep2)
wd_deg = {"D": 4, "nv": 20, "neq": 19, "output": 3,
          "nodes": [{"id": 0, "rows": [[[], 0]], "prods": []},
                    {"id": 1, "rows": [[[], 1]], "prods": [[1, 0]]},
                    {"id": 2, "rows": [[[7, 8], 2]], "prods": []},
                    {"id": 3, "rows": [[[], 1]], "prods": [[1, 0], [9, 2], [9, 2]]}]}
rd = certs.check_wdag(Sp2, wd_deg)
k["wdag_negative_degree4_child"] = rd["verified"]
k["wdag_negative_degree4_child_violated"] = rd.get("violated")
rb = certs.check_wdag(Sp, {"D": 4, "nv": 20, "neq": 19, "output": 0,
                           "nodes": [{"id": 0, "rows": [[[], 1], [[1], 0], [[2, 3, 4], 0], [[2, 3, 4], 0]],
                                      "prods": []}]})
k["wdag_negative_mu3_one_node"] = rb["verified"]
k["wdag_negative_mu3_one_node_violated"] = rb.get("violated")
k["pass"] = (k["flat_positive"] and not k["flat_negative_row_removed"] and k["wdag_positive"] and
             not k["wdag_negative_wrong_j"] and not k["wdag_negative_degree4_child"] and
             not k["wdag_negative_mu3_one_node"] and rd.get("violated") == ["(c)"] and rb.get("violated") == ["(b)"])
res["certificate_checkers_planted"] = k

res["all_pass"] = all(res[s_]["pass"] for s_ in
                      ("field", "curve_and_S3", "orders_and_codec", "descent_two_routes", "exhaustive_s", "ring",
                       "elimination", "certificate_checkers_planted"))
res["seconds"] = round(time.time() - t0, 1)
json.dump(res, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k_: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k_, v in res.items()}, indent=1))
