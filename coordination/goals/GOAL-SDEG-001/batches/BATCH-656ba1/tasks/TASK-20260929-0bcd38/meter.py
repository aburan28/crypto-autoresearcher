"""Blind re-derivation meter for W_query(B1), L=8 (TASK-20260929-0bcd38).

Written from specification.yaml + AMD-20260926-3479cf + AMD-20260928-7ce387 +
AMD-20260928-d3ed9e, the A1 idea text, the fixtures and the coordinator's
target extract only. Conventions are documented in rederivation_report.yaml.

Run: python3 meter.py <fixtures_json> <targets_json> <semaev_dir> <out_json>
"""
import hashlib
import itertools
import json
import random
import statistics
import sys

import numpy as np

DEG = 8


class Counter:
    """Charged F_p operation counter. Unit weights: mult=1; inversion=1 mult
    plus the counted extended-gcd division steps (AMD-20260926-3479cf C-4)."""

    def __init__(self):
        self.mul = 0
        self.add = 0
        self.inv = 0
        self.egcd_steps = 0

    def charged(self):
        return self.mul + self.inv + self.egcd_steps

    def snapshot(self):
        return (self.mul, self.add, self.inv, self.egcd_steps)


def inv_counted(x, p, cnt):
    r0, r1, s0, s1 = p, x % p, 0, 1
    steps = 0
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        steps += 1
    assert r0 == 1
    cnt.inv += 1
    cnt.egcd_steps += steps
    return s0 % p


# ---------------------------------------------------------------- curve ----
class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b

    def on(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % p == 0:
                return None
            lam = (3 * P[0] * P[0] + self.a) * pow(2 * P[1], -1, p) % p
        else:
            lam = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
        x = (lam * lam - P[0] - Q[0]) % p
        return (x, (lam * (P[0] - x) - P[1]) % p)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def sqrt(self, n):
        p = self.p
        n %= p
        if n == 0:
            return 0
        if pow(n, (p - 1) // 2, p) != 1:
            return None
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while pow(z, (p - 1) // 2, p) != p - 1:
            z += 1
        m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
        while t != 1:
            i, tt = 0, t
            while tt != 1:
                tt = tt * tt % p
                i += 1
            bb = pow(c, 1 << (m - i - 1), p)
            m, c, t, r = i, bb * bb % p, t * bb * bb % p, r * bb % p
        return r

    def lift(self, x):
        y = self.sqrt(x * x * x + self.a * x + self.b)
        return None if y is None else (x, min(y, self.p - y))


# ------------------------------------------------------ dense Semaev eval --
def horner_last_axis(arr, v, p):
    """Specialize the last axis of a dense coefficient array at v (Horner).
    Returns (result, dense_mults, sparse_mults). Dense charge: 8 mults per
    fiber. Sparse (alternative): per fiber, Horner from its top nonzero
    coefficient, so a fiber whose top nonzero degree is t costs t mults."""
    deg = arr.shape[-1] - 1
    out = arr[..., deg].copy()
    for k in range(deg - 1, -1, -1):
        out = (out * v + arr[..., k]) % p
    nfib = int(np.prod(arr.shape[:-1]))
    nz = arr != 0
    top = np.where(nz.any(axis=-1), deg - np.argmax(nz[..., ::-1], axis=-1), 0)
    return out, nfib * deg, int(top.sum())


def s5_eval(C5, xs, p):
    a = C5
    for v in reversed(xs):
        a, _, _ = horner_last_axis(a, v, p)
    return int(a)


def s4_eval(C4, xs, p):
    tot = 0
    for idx in itertools.product(range(5), repeat=4):
        c = int(C4[idx])
        if c:
            t = c
            for e, x in zip(idx, xs):
                t = t * pow(x, e, p) % p
            tot += t
    return tot % p


# ---------------------------------------------------- field-form PRS -------
def strip(A):
    A = list(A)
    while A and A[-1] == 0:
        A.pop()
    return A


def rem_field(A, B, p, cnt, log):
    """Remainder of A by B with one field inversion of lc(B) (v4 D-1).
    Per quotient step: 1 mult for the quotient coefficient, deg(B) mults and
    deg(B) adds for the update (the leading term cancels by construction)."""
    n, d = len(A) - 1, len(B) - 1
    inv = inv_counted(B[d], p, cnt)
    A = list(A)
    for i in range(n, d - 1, -1):
        q = A[i] * inv % p
        cnt.mul += 1
        if q:
            base = i - d
            for j in range(d):
                A[base + j] = (A[base + j] - q * B[j]) % p
        cnt.mul += d
        cnt.add += d
        A[i] = 0
    log.append((n, d))
    return strip(A[:d])


def prs_gcd_degree(FT, b, p, cnt, log):
    """Euclidean (field-form subresultant) sequence of (F_T, b). Stops at the
    first zero remainder (gcd = previous term) or at a nonzero constant
    remainder (coprime). Returns deg gcd(F_T, b)."""
    r0, r1 = FT, strip(b)
    if not r1:
        return len(FT) - 1
    if len(r1) == 1:
        return 0
    while True:
        r2 = rem_field(r0, r1, p, cnt, log)
        if not r2:
            return len(r1) - 1
        if len(r2) == 1:
            return 0
        r0, r1 = r1, r2


def monic_reading_cost(log):
    """Alternative field-form reading: make the divisor monic (d mults) after
    its inversion, then d mults per quotient step. Inversions charged
    separately (same count as primary)."""
    return sum(d + (n - d + 1) * d for n, d in log)


def poly_eval(A, x, p):
    r = 0
    for c in reversed(A):
        r = (r * x + c) % p
    return r


# ------------------------------------------------------------ table T -----
def build_table(E, pts, cnt):
    """T = {x(Pa + Pb), x(Pa - Pb) : a <= b} plus the point at infinity
    (a == b, Pa - Pa). Charged by point arithmetic from the lifted points
    (lift charged 3 mults + an instrumented square root), one hash probe per
    candidate, and the product expansion of F_T."""
    p = E.p
    probes = 0
    finite = set()
    for (x, y) in pts:
        cnt.mul += 3
        e = (p - 1) // 2
        cnt.mul += 2 * e.bit_length()
    n = len(pts)
    for i in range(n):
        for j in range(i, n):
            P, Q = pts[i], pts[j]
            if i == j:
                D = E.add(P, P)
                inv_counted(2 * P[1], p, cnt)
                cnt.mul += 4
                cands = [D[0]] if D is not None else []
            else:
                inv_counted(Q[0] - P[0], p, cnt)
                cnt.mul += 4
                cands = [R[0] for R in (E.add(P, Q), E.sub(P, Q)) if R is not None]
            for c in cands:
                probes += 1
                finite.add(c)
    Tf = sorted(finite)
    FT = [1]
    for v in Tf:
        new = [0] * (len(FT) + 1)
        for k, c in enumerate(FT):
            new[k + 1] = (new[k + 1] + c) % p
            new[k] = (new[k] - v * c) % p
        cnt.mul += len(FT)
        cnt.add += len(FT)
        FT = new
    return Tf, FT, probes


# ------------------------------------------------------------- oracles ----
def exhaustive_members(E, pts):
    signed = []
    for P in pts:
        signed += [P, E.neg(P)]
    sums = set()
    for combo in itertools.combinations_with_replacement(range(len(signed)), 5):
        S = None
        for c in combo:
            S = E.add(S, signed[c])
        sums.add(S)
    return sums


def pair_sums(E, pts):
    out = {None}
    for i in range(len(pts)):
        for j in range(i, len(pts)):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    A = pts[i] if s1 == 1 else E.neg(pts[i])
                    B = pts[j] if s2 == 1 else E.neg(pts[j])
                    out.add(E.add(A, B))
    return out


def triple_hits_by_points(E, R, trip, S2):
    """Point-arithmetic truth for one triple: exists signs with
    R - e3 P3 - e4 P4 - e5 P5 in {+-Pa +- Pb} (incl. O)."""
    for signs in itertools.product((1, -1), repeat=3):
        Q = R
        for s, P in zip(signs, trip):
            Q = E.sub(Q, P) if s == 1 else E.add(Q, P)
        if Q in S2:
            return True
    return False


def verify_witness(E, R, trip, pts, bpoly, FT_roots_ok):
    """Uncharged: find an explicit signed 5-term decomposition of R whose
    intermediate u = x(e1 P1 + e2 P2) is a common root of F_T and b (or O
    for the infinity element)."""
    p = E.p
    for signs in itertools.product((1, -1), repeat=3):
        Q = R
        for s, P in zip(signs, trip):
            Q = E.sub(Q, P) if s == 1 else E.add(Q, P)
        if Q is not None and (Q[0] not in FT_roots_ok or poly_eval(bpoly, Q[0], p) != 0):
            continue
        for i in range(len(pts)):
            for j in range(i, len(pts)):
                for s1 in (1, -1):
                    for s2 in (1, -1):
                        A = pts[i] if s1 == 1 else E.neg(pts[i])
                        B = pts[j] if s2 == 1 else E.neg(pts[j])
                        if E.add(A, B) == Q:
                            S = E.add(A, B)
                            for s, P in zip(signs, trip):
                                S = E.add(S, P if s == 1 else E.neg(P))
                            if S == R:
                                return True
    return False


# ---------------------------------------------------------- identities ----
def identity_checks(E, C5, C4, ntest, label):
    p = E.p
    rng = random.Random(label)

    def rpt():
        while True:
            P = E.lift(rng.randrange(p))
            if P is not None:
                return P if rng.random() < 0.5 else E.neg(P)

    s5_rel = s5_rand_nz = s4_rel = sym = eff = 0
    for _ in range(ntest):
        P = [rpt() for _ in range(4)]
        P5 = E.neg(E.add(E.add(P[0], P[1]), E.add(P[2], P[3])))
        Q3 = E.neg(E.add(E.add(P[0], P[1]), P[2]))
        if P5 is None or Q3 is None:
            continue
        eff += 1
        xs = [Q[0] for Q in P] + [P5[0]]
        s5_rel += s5_eval(C5, xs, p) == 0
        s4_rel += s4_eval(C4, [P[0][0], P[1][0], P[2][0], Q3[0]], p) == 0
        xr = [rpt()[0] for _ in range(5)]
        v = s5_eval(C5, xr, p)
        s5_rand_nz += v != 0
        perm = xr[:]
        rng.shuffle(perm)
        sym += s5_eval(C5, perm, p) == v
    return dict(ntest=ntest, effective_tests=eff, S5_zero_on_relations=s5_rel, S4_zero_on_relations=s4_rel,
                S5_nonzero_on_random=s5_rand_nz, S5_symmetric_on_random_perm=sym)


# --------------------------------------------------------------- driver ---
def meter_cell(cell, fixture, sem):
    p, a, b = fixture["p"], fixture["a"], fixture["b"]
    E = Curve(p, a, b)
    C5 = np.array(sem["S5"], dtype=np.int64).reshape((9,) * 5)
    C4 = np.array(sem["S4"], dtype=np.int64).reshape((5,) * 4)
    V = cell["V"]
    assert V == sorted(V)
    pts = [E.lift(x) for x in V]
    assert all(P is not None for P in pts), "non-liftable x in V"
    nV = len(V)
    tcnt = Counter()
    Tf, FT, probes = build_table(E, pts, tcnt)
    W_table = tcnt.charged() + probes
    Tset = set(Tf)
    members = exhaustive_members(E, pts)
    S2 = pair_sums(E, pts)
    triples = list(itertools.combinations_with_replacement(range(nV), 3))
    rows = []
    for qd in cell["queries"]:
        R_inf = qd["R"] is None
        R = None if R_inf else tuple(qd["R"])
        assert E.on(R)
        if R_inf:
            A4, fixed_dense, fixed_sparse = C4, 0, 0
        else:
            A4, fixed_dense, fixed_sparse = horner_last_axis(C5, R[0], p)
        dg = A4.shape[-1] - 1
        L1, L2, L3 = (dg + 1) ** 3 * dg, (dg + 1) ** 2 * dg, (dg + 1) * dg
        cnt = Counter()
        spec_dense = spec_sparse = 0
        spec_naive = 0
        prs_log = []
        cur_i = cur_j = None
        A3 = A2 = None
        first_hit = None
        snap_first = None
        hit_triples = []
        oracle_hit_triples = []
        inf_hits = 0
        deg_b_hist = {}
        gcd_deg_at_first = None
        witness_ok_all = True
        for t_idx, (i, j, k) in enumerate(triples):
            if i != cur_i:
                A3, dd, ss = horner_last_axis(A4, V[i], p)
                spec_dense += dd
                spec_sparse += ss
                cur_i, cur_j = i, None
            if j != cur_j:
                A2, dd, ss = horner_last_axis(A3, V[j], p)
                spec_dense += dd
                spec_sparse += ss
                cur_j = j
            bvec, dd, ss = horner_last_axis(A2, V[k], p)
            spec_dense += dd
            spec_sparse += ss
            spec_naive += L1 + L2 + L3
            bpoly = strip(int(c) for c in bvec)
            deg_b = len(bpoly) - 1
            deg_b_hist[deg_b] = deg_b_hist.get(deg_b, 0) + 1
            g = prs_gcd_degree(FT, bpoly, p, cnt, prs_log)
            inf_hit = deg_b < dg
            hit = g >= 1 or inf_hit
            trip_pts = (pts[i], pts[j], pts[k])
            truth = triple_hits_by_points(E, R, trip_pts, S2)
            if truth:
                oracle_hit_triples.append(t_idx)
            if hit:
                hit_triples.append(t_idx)
                inf_hits += inf_hit
                ok = verify_witness(E, R, trip_pts, pts, bpoly, Tset)
                witness_ok_all &= ok
                if first_hit is None and ok:
                    first_hit = t_idx
                    gcd_deg_at_first = g
                    snap_first = dict(mul=cnt.mul, add=cnt.add, inv=cnt.inv, egcd=cnt.egcd_steps,
                                      spec_dense=spec_dense, spec_sparse=spec_sparse,
                                      spec_naive=spec_naive, prs_log_len=len(prs_log),
                                      triples_done=t_idx + 1)
        full = dict(mul=cnt.mul, add=cnt.add, inv=cnt.inv, egcd=cnt.egcd_steps,
                    spec_dense=spec_dense, spec_sparse=spec_sparse, spec_naive=spec_naive,
                    prs_log_len=len(prs_log), triples_done=len(triples))
        dec = snap_first if snap_first is not None else full
        member_oracle = R in members

        def W(s, spec_key="spec_dense", fixed=fixed_dense, inv_unit=False, monic=False, adds=False):
            mults = monic_reading_cost(prs_log[:s["prs_log_len"]]) if monic else s["mul"]
            prs = mults + s["inv"] + (0 if inv_unit else s["egcd"])
            add_term = 0
            if adds:
                add_term = s["add"] + (s[spec_key] + fixed)
            return fixed + s[spec_key] + prs + add_term

        Wq = W(dec)
        Wq_primary = None if R_inf else Wq
        row = dict(
            query_id=qd["query_id"], cell_id=cell["cell_id"], deck=cell["deck"], seed=cell["seed"],
            R=None if R_inf else list(R),
            R_is_infinity=R_inf,
            backward_polynomial="S4(u,x3,x4,x5) [R = O alternative]" if R_inf else "S5(u,x3,x4,x5,x(R))",
            membership=bool(snap_first is not None),
            membership_exhaustive_oracle=bool(member_oracle),
            first_hit_triple_index=first_hit,
            first_hit_triple_x=[V[t] for t in triples[first_hit]] if first_hit is not None else None,
            gcd_degree_at_first_hit=gcd_deg_at_first,
            triples_processed=dec["triples_done"], triples_total=len(triples),
            W_query=Wq_primary,
            W_fixed_xR=None if R_inf else fixed_dense,
            W_triple=None if R_inf else Wq - fixed_dense,
            W_query_R_infinity_S4_alternative=Wq if R_inf else None,
            W_components=dict(fixed_xR_specialization=fixed_dense,
                              per_triple_specialization=dec["spec_dense"],
                              prs_mults=dec["mul"], prs_inversions=dec["inv"],
                              prs_egcd_steps=dec["egcd"]),
            W_alternatives=dict(
                spec_naive_per_triple=W(dec, spec_key="spec_naive"),
                spec_sparse_value_dependent=W(dec, spec_key="spec_sparse", fixed=fixed_sparse),
                W_fixed_xR_sparse=fixed_sparse,
                prs_monic_divisor=W(dec, monic=True),
                inversion_unit_cost=W(dec, inv_unit=True),
                with_additions=W(dec, adds=True),
                plus_amortized_table=Wq + W_table / 32.0,
                full_enumeration=W(full),
                full_enumeration_spec_naive=W(full, spec_key="spec_naive"),
            ),
            W_prs_charged=dec["mul"] + dec["inv"] + dec["egcd"],
            W_prs_per_triple=(dec["mul"] + dec["inv"] + dec["egcd"]) / dec["triples_done"],
            W_spec_per_triple=dec["spec_dense"] / dec["triples_done"],
            hit_triple_indices=hit_triples,
            point_arithmetic_hit_triple_indices=oracle_hit_triples,
            infinity_element_hits=inf_hits,
            witnesses_all_verified=witness_ok_all,
            deg_b_histogram={str(k): v for k, v in sorted(deg_b_hist.items())},
        )
        rows.append(row)
    cell_meta = dict(cell_id=cell["cell_id"], deck=cell["deck"], seed=cell["seed"], q=cell["q"], p=p,
                     V_size=nV, T_finite=len(Tf), T_with_infinity=len(Tf) + 1, deg_F_T=len(FT) - 1,
                     W_table=W_table, W_table_probes=probes, triples_total=len(triples))
    return rows, cell_meta


def med(xs):
    return statistics.median(xs) if xs else None


def main():
    fixtures_path, targets_path, sem_dir, out_path = sys.argv[1:5]
    fixtures = {(f["L"], f["seed"]): f for f in json.load(open(fixtures_path))["EXP-SDEG-85eefd"]}
    targets = json.load(open(targets_path))
    sems, idchecks = {}, {}
    for s in (1, 2, 3):
        sems[s] = json.load(open(f"{sem_dir}/semaev_L8_s{s}.json"))
        f = fixtures[(8, s)]
        assert (sems[s]["p"], sems[s]["a"], sems[s]["b"]) == (f["p"], f["a"], f["b"])
        E = Curve(f["p"], f["a"], f["b"])
        idchecks[s] = identity_checks(
            E, np.array(sems[s]["S5"], dtype=np.int64).reshape((9,) * 5),
            np.array(sems[s]["S4"], dtype=np.int64).reshape((5,) * 4), 1000,
            f"TASK-20260929-0bcd38|identity|L8|s{s}")
        print("identity", s, idchecks[s], flush=True)
    all_rows, cells = [], []
    for cell in targets["cells"]:
        rows, meta = meter_cell(cell, fixtures[(8, cell["seed"])], sems[cell["seed"]])
        ok_rows = [r for r in rows if not r["R_is_infinity"]]
        mem = [r["W_query"] for r in ok_rows if r["membership"]]
        non = [r["W_query"] for r in ok_rows if not r["membership"]]
        memt = [r["W_triple"] for r in ok_rows if r["membership"]]
        nont = [r["W_triple"] for r in ok_rows if not r["membership"]]
        V3 = meta["V_size"] ** 3
        meta.update(
            n_members=len(mem), n_nonmembers=len(non),
            oracle_agreement=all(r["membership"] == r["membership_exhaustive_oracle"] for r in rows),
            hit_set_agreement=all(r["hit_triple_indices"] == r["point_arithmetic_hit_triple_indices"] for r in rows),
            median_W_members=med(mem), median_W_nonmembers=med(non), median_W_all=med(mem + non),
            median_W_triple_members=med(memt), median_W_triple_nonmembers=med(nont),
            median_W_members_over_T=(med(mem) / meta["T_finite"]) if mem else None,
            median_W_nonmembers_over_T=(med(non) / meta["T_finite"]) if non else None,
            median_W_members_over_V3=(med(mem) / V3) if mem else None,
            median_W_nonmembers_over_V3=(med(non) / V3) if non else None,
            median_W_triple_nonmembers_over_T=(med(nont) / meta["T_finite"]) if non else None,
            median_W_triple_nonmembers_over_V3=(med(nont) / V3) if non else None,
            n_R_infinity_excluded=len(rows) - len(ok_rows),
            median_prs_per_triple_nonmembers=med([r["W_prs_per_triple"] for r in ok_rows if not r["membership"]]),
            median_prs_per_triple_over_T_nonmembers=(
                med([r["W_prs_per_triple"] for r in ok_rows if not r["membership"]]) / meta["T_finite"]) if non else None,
            median_alt_nonmembers={k: med([r["W_alternatives"][k] for r in ok_rows if not r["membership"]])
                                   for k in rows[0]["W_alternatives"]},
            median_alt_members={k: med([r["W_alternatives"][k] for r in ok_rows if r["membership"]])
                                for k in rows[0]["W_alternatives"]},
        )
        for r in rows:
            wq, wt = r["W_query"], r["W_triple"]
            r["W_over_T_finite"] = None if wq is None else wq / meta["T_finite"]
            r["W_over_V_cubed"] = None if wq is None else wq / V3
            r["W_triple_over_T_finite"] = None if wt is None else wt / meta["T_finite"]
            r["W_triple_over_V_cubed"] = None if wt is None else wt / V3
            r["T_finite"] = meta["T_finite"]
            r["V_size"] = meta["V_size"]
        cells.append(meta)
        all_rows.extend(rows)
        print(cell["cell_id"], {k: meta[k] for k in ("V_size", "T_finite", "n_members", "oracle_agreement",
                                                    "hit_set_agreement", "median_W_members",
                                                    "median_W_nonmembers")}, flush=True)
    out = dict(task="TASK-20260929-0bcd38", quantity="W_query(B1), L=8", n_queries=len(all_rows),
               identity_checks=idchecks, cells=cells, rows=all_rows)
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1)
    h = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    print("wrote", out_path, len(all_rows), h)


if __name__ == "__main__":
    main()
