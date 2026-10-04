"""BR-2 self-tests. Own seeds only (declared in SEEDS); none of the
specification's seeds is used.
"""
import copy
import random
import time

import numpy as np

import br_field as F
import br_curve as C
import br_system as S
import br_macaulay as MC
import br_linalg as LA
import br_closure as CL
import br_sat as SAT
import br_rcb as RCB
import br_wdag_check as WC

SEEDS = {
    "points": 8638143101,
    "descent": 8638143102,
    "macaulay_rows": 8638143103,
    "small_systems": 8638143104,
    "substitution": 8638143105,
    "wdag": 8638143106,
    "exhaustive_s": 8638143107,
    "field_axioms": 8638143108,
    "small_systems_nv8": 8638144104,
}


# ----------------------------------------------------------------------------
def t_irreducible():
    r = F.irreducibility_checks()
    return {"pass": bool(r["irreducible"]), "detail": r}


def t_field_axioms(n=2000):
    rng = random.Random(SEEDS["field_axioms"])
    bad = 0
    for _ in range(n):
        a, b, c = (rng.randrange(1 << 17) for _ in range(3))
        if F.mul(a, F.mul(b, c)) != F.mul(F.mul(a, b), c):
            bad += 1
        if F.mul(a, b ^ c) != (F.mul(a, b) ^ F.mul(a, c)):
            bad += 1
        if F.mul(a, b) != F.mul(b, a):
            bad += 1
        if a and F.mul(a, F.inv(a)) != 1:
            bad += 1
    # vectorized multiply agrees with scalar multiply
    arr_a = np.array([rng.randrange(1 << 17) for _ in range(500)], dtype=np.uint64)
    arr_b = np.array([rng.randrange(1 << 17) for _ in range(500)], dtype=np.uint64)
    vm = F.vmul(arr_a, arr_b)
    vbad = sum(int(vm[i]) != F.mul(int(arr_a[i]), int(arr_b[i])) for i in range(500))
    # half-trace root finding
    hbad = 0
    for _ in range(n):
        c = rng.randrange(1 << 17)
        roots = F.solve_quadratic_z(c)
        if F.trace(c) == 0:
            if len(roots) != 2 or any((F.sqr(z) ^ z) != c for z in roots):
                hbad += 1
        elif roots:
            hbad += 1
    return {"pass": bad == 0 and vbad == 0 and hbad == 0, "triples": n,
            "axiom_failures": bad, "vector_vs_scalar_failures": vbad,
            "quadratic_root_failures": hbad}


def t_S3_points(A, B, n=300):
    rng = random.Random(SEEDS["points"])

    def rand_point():
        while True:
            x = rng.randrange(1, 1 << 17)
            P = C.lift_x(x, A, B, rng.randrange(2))
            if P is not None:
                return P
    ok = 0
    tested = 0
    off_curve = 0
    nonvacuous = 0
    while tested < n:
        P1, P2 = rand_point(), rand_point()
        if P1[0] == P2[0]:
            continue
        Sp = C.padd(P1, P2, A, B)
        Sm = C.padd(P1, C.neg(P2), A, B)
        for P in (P1, P2, Sp, Sm):
            if not C.on_curve(P, A, B):
                off_curve += 1
        tested += 1
        if C.S3(P1[0], P2[0], Sp[0], B) == 0 and C.S3(P1[0], P2[0], Sm[0], B) == 0:
            ok += 1
        # the test is not vacuous: a random third x almost never satisfies S_3
        if C.S3(P1[0], P2[0], rng.randrange(1 << 17), B) != 0:
            nonvacuous += 1
    # doubling consistency: P + P via the doubling branch equals the x of 2P
    dbl_ok = 0
    for _ in range(50):
        P = rand_point()
        D2 = C.padd(P, P, A, B)
        if D2 is None or C.on_curve(D2, A, B):
            dbl_ok += 1
    return {"pass": ok == tested and off_curve == 0 and dbl_ok == 50,
            "pairs": tested, "S3_zero_on_both_sum_and_difference": ok,
            "points_off_curve": off_curve, "random_third_x_nonzero": nonvacuous,
            "doublings_on_curve": dbl_ok}


def t_descent(B, n=300, anf_cases=3):
    rng = random.Random(SEEDS["descent"])
    bad = 0
    for _ in range(n):
        xR = rng.randrange(1 << 17)
        v = rng.randrange(1 << 18)
        E = S.E_S3(xR, B)
        bits = S.eval_system_at(E, v)
        val = C.S3(S.x1_of(v), S.x2_of(v), xR, B)
        if bits != [(val >> k) & 1 for k in range(17)]:
            bad += 1
    anf = []
    for _ in range(anf_cases):
        xR = rng.randrange(1 << 17)
        EA = S.E_S3(xR, B)
        EB, maxdeg = S.E_from_anf(S.anf_S3_direct(xR, B))
        only_parts = not EA[:, [c for c in S.QUAD_COLS if c not in S.BILINEAR_COLS]].any()
        anf.append({"x_R": xR, "equal": bool(np.array_equal(EA, EB)), "anf_max_degree": maxdeg,
                    "only_bilinear_linear_constant": bool(only_parts)})
    ok = bad == 0 and all(a["equal"] and a["anf_max_degree"] <= 2 and a["only_bilinear_linear_constant"] for a in anf)
    return {"pass": ok, "random_v_xR": n, "mismatches": bad, "full_anf_route": anf}


def _naive_row(E, mu, k):
    s = set()
    for j in np.flatnonzero(E[k]):
        m = S.E_MASKS[j] | S.mask_of(mu)
        if m in s:
            s.remove(m)
        else:
            s.add(m)
    return s


def t_macaulay_rows(B, sp4, n=40):
    rng = random.Random(SEEDS["macaulay_rows"])
    bad = 0
    for _ in range(n):
        xR = rng.randrange(1 << 17)
        E = S.E_S3(xR, B)
        if rng.random() < 0.5:        # also random dense systems
            E = np.array([[rng.randrange(2) for _ in range(S.NCOL_E)] for _ in range(17)], dtype=np.uint8)
        M = sp4.build(E)
        r = rng.randrange(sp4.nrows)
        mu, k = sp4.row_label(r)
        if sp4.poly_of_row(M[r]) != _naive_row(E, mu, k):
            bad += 1
    return {"pass": bad == 0, "rows_checked": n, "mismatches": bad}


def t_fixture(sp3, sp4, sp3_17, sp4_17, B):
    E = S.E_S3(12345, B)
    M3 = sp3.build(E)
    M4 = sp4.build(E)
    rec = RCB.rc_b(E, sp3_17, sp4_17)
    got = {
        "M_3": [int(M3.shape[0]), sp3.ncols],
        "M_4": [int(M4.shape[0]), sp4.ncols],
        "R'_3": rec.get("R3_shape"),
        "R'_4": rec.get("R4_shape"),
    }
    want = {"M_3": [323, 988], "M_4": [2924, 4048], "R'_3": [306, 834], "R'_4": [2618, 3214]}
    return {"pass": got == want, "got": got, "expected": want}


# ----------------------------------------------------------------------------
# brute-force literal fixpoint on small systems (independent arithmetic:
# Python-int bit vectors over mu_order(D, nv), XOR basis with pivot = top bit)
# ----------------------------------------------------------------------------
class IntSpan:
    def __init__(self):
        self.b = {}

    def reduce(self, v):
        while v:
            h = v.bit_length() - 1
            if h in self.b:
                v ^= self.b[h]
            else:
                return v
        return 0

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.b[v.bit_length() - 1] = v
            return True
        return False

    def dim(self):
        return len(self.b)


def brute_force_W(eqs_masks, nv, D):
    monos = S.mu_order(D, nv)
    idx = {S.mask_of(m): i for i, m in enumerate(monos)}
    deg = [len(m) for m in monos]
    topmask = 0
    for i, d in enumerate(deg):
        if d == D:
            topmask |= 1 << i

    def vec(masks):
        v = 0
        for m in masks:
            v ^= 1 << idx[m]
        return v

    def masks_of(v):
        out = []
        i = 0
        while v:
            if v & 1:
                out.append(S.mask_of(monos[i]))
            v >>= 1
            i += 1
        return out

    def times(j, v):
        acc = set()
        for m in masks_of(v):
            t = m | (1 << j)
            if t in acc:
                acc.remove(t)
            else:
                acc.add(t)
        return vec(acc)

    W = IntSpan()
    for mu in S.mu_order(D - 2, nv):
        mm = S.mask_of(mu)
        for f in eqs_masks:
            acc = set()
            for m in f:
                t = m | mm
                if t in acc:
                    acc.remove(t)
                else:
                    acc.add(t)
            W.add(vec(acc))
    rounds = 0
    while True:
        rounds += 1
        # spanning set of W cap B_{<=D-1}: kernel of the projection on degree D
        basis = list(W.b.values())
        rows = [(b & topmask, 1 << i) for i, b in enumerate(basis)]
        piv = {}
        kern = []
        for p, t in rows:
            while p:
                h = p.bit_length() - 1
                if h in piv:
                    p ^= piv[h][0]
                    t ^= piv[h][1]
                else:
                    piv[h] = (p, t)
                    break
            if not p:
                kern.append(t)
        low = []
        for t in kern:
            g = 0
            i = 0
            while t:
                if t & 1:
                    g ^= basis[i]
                t >>= 1
                i += 1
            if g:
                assert g & topmask == 0
                low.append(g)
        added = False
        for g in low:
            for j in range(nv):
                if W.add(times(j, g)):
                    added = True
        if not added:
            break
    return W, vec, rounds


def t_small_W(n_min=5, n_max=60, nv=6, D=3, need_deep=3, need_deep_one=0,
              seed=None, neq_choices=(1, 2, 2, 3, 3, 4), densities=(0.15, 0.25, 0.4)):
    rng = random.Random(SEEDS["small_systems"] if seed is None else seed)
    results = []
    deep = 0
    deep_one = 0
    witnesses = []
    i = 0
    while i < n_max:
        i += 1
        neq = rng.choice(list(neq_choices))
        sysmonos = S.mu_order(2, nv)
        density = rng.choice(list(densities))
        E = np.array([[1 if rng.random() < density else 0 for _ in sysmonos] for _ in range(neq)], dtype=np.uint8)
        sp = MC.Space(nv, D, neq)
        M = sp.build(E)
        wc = CL.WClosure(sp, M)
        rec = wc.run()
        eqs_masks = [[S.mask_of(sysmonos[j]) for j in np.flatnonzero(E[k])] for k in range(neq)]
        Wb, vec, rounds = brute_force_W(eqs_masks, nv, D)
        # equality: same dimension, and every literal RREF row lies in the brute span
        contained = all(Wb.reduce(vec(sp.poly_of_row(r))) == 0 for r in wc.final_rows)
        same = contained and Wb.dim() == rec["final_dim"]
        # every element of W vanishes on the common zeros (soundness sanity)
        zeros = [u for u in range(1 << nv)
                 if all(S.eval_system_at(E[k:k + 1], u, nv)[0] == 0 for k in range(neq))]
        vanish = True
        for r in wc.final_rows:
            ms = sp.poly_of_row(r)
            for u in zeros:
                val = 0
                for m in ms:
                    if m & u == m:
                        val ^= 1
                if val:
                    vanish = False
        res = {"system": i, "neq": neq, "density": density,
               "equations": [[list(sysmonos[j]) for j in np.flatnonzero(E[k])] for k in range(neq)],
               "literal_dims": rec["dims"], "fixpoint_index": rec["fixpoint_index"],
               "one_first_iteration": rec["one_first_iteration"],
               "brute_force_dim": Wb.dim(), "brute_force_rounds": rounds,
               "equal": bool(same), "vanishes_on_common_zeros": vanish,
               "n_common_zeros": len(zeros)}
        if rec["one"]:
            l0 = CL.LevelZeroSolver(sp, M)
            cert = wc.witness(l0)
            chk = WC.Checker([[list(sysmonos[j]) for j in np.flatnonzero(E[k])] for k in range(neq)],
                             D=D, nv=nv, neq=neq).check(cert)
            res["witness_valid"] = chk["valid"]
            res["witness_nodes"] = chk["node_count"]
            witnesses.append((cert, chk["valid"], rec["one_first_iteration"]))
        results.append(res)
        if rec["fixpoint_index"] >= 2:
            deep += 1
        if rec["one"] and rec["one_first_iteration"] >= 2:
            deep_one += 1
        if len(results) >= n_min and deep >= need_deep and deep_one >= need_deep_one:
            break
    ok = (len(results) >= 5 and deep >= 1 and deep_one >= need_deep_one
          and all(r["equal"] and r["vanishes_on_common_zeros"] for r in results)
          and all(r.get("witness_valid", True) for r in results))
    kept = results if len(results) <= 80 else [r for r in results if r.get("one_first_iteration") not in (None, 0)] + results[:10]
    return {"pass": ok, "nv": nv, "D": D, "seed": SEEDS["small_systems"] if seed is None else seed,
            "systems_generated": len(results), "fixpoint_index_ge_2": deep,
            "refuted_first_at_iteration_ge_2": deep_one,
            "refuted_total": sum(1 for r in results if r.get("one_first_iteration") is not None),
            "witnesses_checked": sum(1 for r in results if "witness_valid" in r),
            "witnesses_valid": sum(1 for r in results if r.get("witness_valid") is True),
            "all_equal_to_brute_force": all(r["equal"] for r in results),
            "stopping_rule": "generate until >= %d systems, >= %d with fixpoint index >= 2 and >= %d refuted first at iteration >= 2 (cap %d)" % (n_min, need_deep, need_deep_one, n_max),
            "fixpoint_index_definition": "first i with dim W^(i+1) == dim W^(i)",
            "systems_listed": "all" if len(results) <= 80 else "refuted at iteration >= 1, plus the first 10",
            "systems": kept}


# ----------------------------------------------------------------------------
def t_substitution(B, sp3_17, sp4_17, n=150):
    rng = random.Random(SEEDS["substitution"])
    cases = 0
    bad = 0
    ell_bad = 0
    systems = 0
    while cases < n:
        xR = rng.randrange(1 << 9, 1 << 17)
        E = S.E_S3(xR, B)
        if rng.random() < 0.5:
            # random lower part on the linear/constant columns, S_3 quadratic part
            E = E.copy()
            E[:, :19] = np.array([[rng.randrange(2) for _ in range(19)] for _ in range(17)], dtype=np.uint8)
        ker = RCB.left_kernel(E[:, S.QUAD_COLS])
        if len(ker) != 1:
            continue
        c = ker[0]
        ell = np.zeros(S.NCOL_E, dtype=np.uint8)
        for k in np.flatnonzero(c):
            ell ^= E[k]
        lin = [i for i in range(18) if ell[S.E_COL[1 << i]]]
        if not lin:
            continue
        const = int(ell[0])
        jstar = lin[0]
        Ep, others = RCB.substitute(E, jstar, lin, const)
        systems += 1
        for _ in range(10):
            up = rng.randrange(1 << 17)
            u = 0
            for newi, old in enumerate(others):
                if (up >> newi) & 1:
                    u |= 1 << old
            a = const
            for i in lin:
                if i != jstar:
                    a ^= (u >> i) & 1
            if a:
                u |= 1 << jstar
            if S.eval_system_at(ell.reshape(1, -1), u)[0] != 0:
                ell_bad += 1
            if S.eval_system_at(E, u) != S.eval_system_at(Ep, up, nv=17):
                bad += 1
            cases += 1
    return {"pass": bad == 0 and ell_bad == 0, "cases": cases, "systems": systems,
            "mismatches": bad, "ell_nonzero_on_extension": ell_bad}


def t_exhaustive_s(B, n=6):
    rng = random.Random(SEEDS["exhaustive_s"])
    rows = []
    ok = True
    for i in range(n):
        xR = rng.randrange(1 << 9, 1 << 17)
        E = S.E_S3(xR, B)
        s1, sols = SAT.count_s(E, want_solutions=True)
        s2 = SAT.count_s_unpacked(E)
        sA = SAT.oracle_A(xR, B)
        s3 = SAT.direct_count_VxV(xR, B)
        # every listed solution satisfies every equation, checked pointwise
        pw = all(not any(S.eval_system_at(E, u)) for u in sols)
        rows.append({"x_R": xR, "s_bitsliced": s1, "s_unpacked": s2, "s_oracle_A": sA,
                     "s_direct_VxV": s3, "solutions_pointwise_ok": pw})
        ok &= (s1 == s2 == sA == s3) and pw
        if i % 2 == 1:
            # a random system as well (bit-sliced vs unpacked)
            Er = np.array([[rng.randrange(2) for _ in range(S.NCOL_E)] for _ in range(17)], dtype=np.uint8)
            Er[:, 19:] = 0
            Er[:, 19 + rng.randrange(153)] = 1
            a, _ = SAT.count_s(Er)
            b = SAT.count_s_unpacked(Er)
            rows.append({"random_system": True, "s_bitsliced": a, "s_unpacked": b})
            ok &= (a == b)
    return {"pass": bool(ok), "cases": rows}


# ----------------------------------------------------------------------------
def _renumber(cert, perm):
    """Apply an id permutation (old -> new) to a certificate."""
    c = copy.deepcopy(cert)
    for nd in c["nodes"]:
        nd["id"] = perm[nd["id"]]
        nd["prods"] = [[j, perm[x]] for j, x in nd["prods"]]
    c["output"] = perm[c["output"]]
    return c


def t_checker(B, sp4):
    """The checker accepts valid witnesses and rejects at least one corrupted
    witness per rule (a)-(e)."""
    rng = np.random.default_rng(SEEDS["wdag"])
    # find an 18-variable system refuted by W_4 but not M_4 (witness with prods)
    # and one refuted by M_4 (one-node witness): S_3 descents at random x_R.
    wit_W = None
    wit_M = None
    tries = 0
    while (wit_W is None or wit_M is None) and tries < 400:
        tries += 1
        xR = int(rng.integers(1 << 9, 1 << 17))
        E = S.E_S3(xR, B)
        if rng.random() < 0.3:
            E = E.copy()
            E[:, :19] = rng.integers(0, 2, size=(17, 19)).astype(np.uint8)
        s, _ = SAT.count_s(E)
        if s != 0:
            continue
        M = sp4.build(E)
        st = CL.macaulay_stats(sp4, M)
        if st["one"] and wit_M is None:
            wc = CL.WClosure(sp4, M)
            wc.run()
            wit_M = (E, wc.witness(CL.LevelZeroSolver(sp4, M)))
        elif not st["one"] and wit_W is None:
            wc = CL.WClosure(sp4, M)
            rec = wc.run()
            if rec["one"]:
                wit_W = (E, wc.witness(CL.LevelZeroSolver(sp4, M)))
    out = {"tries": tries, "cases": []}
    ok = True

    def case(name, E, cert, expect_valid, expect_rule=None):
        nonlocal ok
        res = WC.Checker(S.equations_from_E(E)).check(cert)
        good = (res["valid"] == expect_valid) and (expect_rule is None or expect_rule in res["failed_rules"])
        ok &= good
        out["cases"].append({"case": name, "expected_valid": expect_valid, "expected_rule": expect_rule,
                             "valid": res["valid"], "failed_rules": res["failed_rules"],
                             "nodes": res["node_count"], "as_expected": bool(good)})
        return res

    if wit_W is None or wit_M is None:
        out["pass"] = False
        out["note"] = "could not construct base witnesses"
        return out
    EW, cW = wit_W
    EM, cM = wit_M
    case("valid W_4 witness (with prods)", EW, cW, True)
    case("valid one-node M_4 witness", EM, cM, True)
    # (a): reverse the ids so every child id exceeds its parent's
    n = len(cW["nodes"])
    perm = {i: n - 1 - i for i in range(n)}
    case("(a) child id not less than parent (ids reversed)", EW, _renumber(cW, perm), False, "a")
    # (b): add a |mu| = 3 row twice to the output (cancels algebraically)
    c = copy.deepcopy(cW)
    outn = [nd for nd in c["nodes"] if nd["id"] == c["output"]][0]
    outn["rows"] = outn["rows"] + [[[0, 1, 2], 3], [[0, 1, 2], 3]]
    case("(b) |mu| = 3 row (added twice, sum unchanged)", EW, c, False, "b")
    c = copy.deepcopy(cM)
    c["nodes"][0]["rows"] = c["nodes"][0]["rows"] + [[[], 17]]
    case("(b) k = 17", EM, c, False, "b")
    # (c): a degree-4 child used twice in prods of the output (sum unchanged)
    c = copy.deepcopy(cW)
    mx = max(nd["id"] for nd in c["nodes"])
    k4 = next(k for k in range(17) if EW[k, S.QUAD_COLS].any())
    y = {"id": mx + 1, "rows": [[[0, 1], k4]], "prods": []}
    old = [nd for nd in c["nodes"] if nd["id"] == c["output"]][0]
    newout = {"id": mx + 2, "rows": copy.deepcopy(old["rows"]),
              "prods": copy.deepcopy(old["prods"]) + [[5, mx + 1], [5, mx + 1]]}
    c["nodes"] = c["nodes"] + [y, newout]
    c["output"] = mx + 2
    r = case("(c) degree-4 child used in prods (twice, sum unchanged)", EW, c, False, "c")
    # (d): a node of degree 5 (only constructible together with (b) or (c)
    # violations at D = 4 for quadratic f_k, since (b) and (c) imply (d))
    c = copy.deepcopy(cM)
    c["nodes"][0]["rows"] = c["nodes"][0]["rows"] + [[[10, 11, 12], k4]]
    case("(d) node of degree 5 via a |mu| = 3 row", EM, c, False, "d")
    c = copy.deepcopy(cW)
    mx = max(nd["id"] for nd in c["nodes"])
    yy = {"id": mx + 1, "rows": [[[0, 1], k4]], "prods": []}
    z = {"id": mx + 2, "rows": [], "prods": [[17, mx + 1]]}
    old = [nd for nd in c["nodes"] if nd["id"] == c["output"]][0]
    newout = {"id": mx + 3, "rows": copy.deepcopy(old["rows"]), "prods": copy.deepcopy(old["prods"])}
    c["nodes"] = c["nodes"] + [yy, z, newout]
    c["output"] = mx + 3
    case("(d) node of degree 5 via v_17 * (degree-4 child)", EW, c, False, "d")
    # (e): drop one row from the output; point the output at a child; re-key
    c = copy.deepcopy(cM)
    c["nodes"][0]["rows"] = c["nodes"][0]["rows"][1:]
    case("(e) one row removed", EM, c, False, "e")
    if len(cW["nodes"]) > 1:
        c = copy.deepcopy(cW)
        child = [nd["id"] for nd in c["nodes"] if nd["id"] != c["output"]][0]
        c["output"] = child
        case("(e) output points at a child node", EW, c, False, "e")
    c = copy.deepcopy(cM)
    c["nodes"][0]["rows"] = [[mu, (k + 1) % 17] if i == 0 else [mu, k] for i, (mu, k) in enumerate(c["nodes"][0]["rows"])]
    case("(e) one k changed", EM, c, False, "e")
    case("(e) valid witness checked against another system", EM, cW, False, "e")
    out["pass"] = bool(ok)
    out["note_rule_d"] = ("At D = 4 with quadratic f_k, rules (b) and (c) imply (d) (rows give degree <= 4, "
                          "products of degree-<=3 children give degree <= 4), so a (d) violation is only "
                          "constructible together with a (b) or (c) violation; the checker is required to "
                          "report (d) among the failed rules.")
    return out


def run_all(A, B):
    t0 = time.time()
    sp3 = MC.Space(18, 3, 17)
    sp4 = MC.Space(18, 4, 17)
    sp3_17 = MC.Space(17, 3, 17)
    sp4_17 = MC.Space(17, 4, 17)
    out = {"seeds": SEEDS}
    tests = [
        ("irreducibility", lambda: t_irreducible()),
        ("field_axioms_and_root_finding", lambda: t_field_axioms()),
        ("S3_against_point_addition", lambda: t_S3_points(A, B)),
        ("descended_equations_against_direct_evaluation", lambda: t_descent(B)),
        ("macaulay_rows_against_naive_multiply", lambda: t_macaulay_rows(B, sp4)),
        ("fixture_dimensions", lambda: t_fixture(sp3, sp4, sp3_17, sp4_17, B)),
        ("literal_W_against_brute_force_fixpoint", lambda: t_small_W()),
        ("literal_W_deep_refutations_and_witnesses_nv8_D3",
         lambda: t_small_W(n_min=5, n_max=4000, nv=8, D=3, need_deep=1, need_deep_one=2,
                           seed=SEEDS["small_systems_nv8"], neq_choices=range(3, 9),
                           densities=(0.08, 0.12, 0.2, 0.3))),
        ("substitution_against_direct_evaluation", lambda: t_substitution(B, sp3_17, sp4_17)),
        ("exhaustive_s_routes", lambda: t_exhaustive_s(B)),
        ("wdag_checker_positive_and_negative", lambda: t_checker(B, sp4)),
    ]
    allpass = True
    for name, fn in tests:
        t = time.time()
        try:
            r = fn()
        except Exception as e:           # a crash in a self-test is a failure
            r = {"pass": False, "exception": repr(e)}
        r["seconds"] = round(time.time() - t, 2)
        out[name] = r
        allpass &= bool(r["pass"])
        print("selftest %-50s %s (%.1fs)" % (name, "PASS" if r["pass"] else "FAIL", r["seconds"]), flush=True)
    out["all_pass"] = bool(allpass)
    out["seconds"] = round(time.time() - t0, 2)
    return out
