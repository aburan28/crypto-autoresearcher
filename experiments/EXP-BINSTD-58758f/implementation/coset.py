"""Coset classification, windows, and signed-sum census for EXP-BINSTD-58758f."""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass

from curve import Curve, is_prime
from gf2n import make_field


# Frozen cells from specification.yaml
N19_MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # t^19+t^5+t^2+t+1
N17_MOD = (1 << 17) | (1 << 3) | 1  # t^17+t^3+1

CELLS = {
    "n19_koblitz_h4": {
        "n": 19,
        "mod": N19_MOD,
        "A": 0,
        "B": 1,
        "expected_E": 523492,
        "expected_l": 130873,
        "expected_h": 4,
        "curve_id": "koblitz-n19-a0b1",
    },
    "n17_rc1_h4": {
        "n": 17,
        "mod": N17_MOD,
        "A": 97044,
        "B": 126251,
        "expected_E": 4 * 32603,
        "expected_l": 32603,
        "expected_h": 4,
        "curve_id": "rc1-n17-A97044-B126251",
    },
    "n19_koblitz_h2": {
        "n": 19,
        "mod": N19_MOD,
        "A": 1,
        "B": 1,
        "expected_E": 525086,
        "expected_l": 262543,
        "expected_h": 2,
        "curve_id": "koblitz-n19-a1b1",
    },
}


@dataclass
class PointRec:
    P: tuple
    x: int
    cls: int  # 0,1,2,3 for h=4; 0 or 1 for h=2 (parity-only bookkeeping)


def build_curve(cell_name: str):
    cell = CELLS[cell_name]
    F = make_field(cell["n"], cell["mod"])
    E = Curve(F, cell["A"], cell["B"])
    return F, E, cell


def verify_order(E: Curve, cell: dict) -> dict:
    order = E.count_by_trace()
    h = cell["expected_h"]
    l = order // h
    out = {
        "group_order_E_measured": order,
        "group_order_E_expected": cell["expected_E"],
        "order_match": order == cell["expected_E"],
        "cofactor_h": h,
        "l_measured": l,
        "l_expected": cell["expected_l"],
        "l_prime": is_prime(l),
        "l_match": l == cell["expected_l"],
    }
    out["pass"] = out["order_match"] and out["l_match"] and out["l_prime"] and (order % h == 0)
    return out


def find_order4_point(E: Curve):
    """Return a point T4 of order 4 ([2]T4 = T2 ≠ O, [4]T4 = O)."""
    T2 = E.lift_x(0)
    assert T2 is not None and E.mul(2, T2) is None
    F = E.F
    for x in range(F.q):
        P = E.lift_x(x)
        if P is None:
            continue
        if E.mul(2, P) == T2:
            # order is 4 (not 2)
            if E.mul(4, P) is None and P != T2:
                return P, T2
    raise RuntimeError("no order-4 point found")


_ORDER4_CACHE = {}


def order4_pair(E: Curve):
    key = id(E)
    if key not in _ORDER4_CACHE:
        _ORDER4_CACHE[key] = find_order4_point(E)
    return _ORDER4_CACHE[key]


def coset_class_h4(E: Curve, P, l: int) -> int:
    """Return Z/4 class for P under E ≅ Z/(4l) via [l]P ∈ {O,T4,T2,-T4}."""
    if P is None:
        return 0
    Pl = E.mul(l, P)
    if Pl is None:
        return 0
    T4, T2 = order4_pair(E)
    if Pl == T2:
        return 2
    if Pl == T4:
        return 1
    if Pl == E.neg(T4):
        return 3
    # Should not happen if order is exactly 4l and P on curve
    raise RuntimeError(f"unexpected [l]P not in <T4>: {Pl}")


def coset_class_h2(E: Curve, P, l: int) -> int:
    """For h=2, only Z/2 bookkeeping: 0 if in C (order|l), else 1."""
    if P is None:
        return 0
    return 0 if E.mul(l, P) is None else 1


def parity_bit(F, A: int, x: int) -> int:
    return F.trace(x) ^ F.trace(A)


def window_deg_lt(dim: int) -> list[int]:
    return list(range(1 << dim))


def random_subspace(n: int, dim: int, rng: random.Random) -> list[int]:
    """Random dim-dimensional F_2-subspace of F_2^n (as bitstrings)."""
    basis = []
    while len(basis) < dim:
        v = rng.randrange(1, 1 << n)
        # gaussian eliminate against existing basis
        w = v
        for b in basis:
            # reduce using leading bits
            if w.bit_length() == b.bit_length():
                w ^= b
        if w == 0:
            continue
        # insert sorted by bit_length
        basis.append(w)
        basis.sort(key=lambda x: -x.bit_length())
        # re-reduce
        for i in range(len(basis)):
            for j in range(len(basis)):
                if i == j:
                    continue
                if basis[i].bit_length() == basis[j].bit_length():
                    # keep unique leading lengths; if collide xor
                    pass
        # simpler: use matrix rank check
        if _rank(basis) < len(basis):
            basis.pop()
    # enumerate span
    out = []
    for mask in range(1 << dim):
        v = 0
        for i in range(dim):
            if (mask >> i) & 1:
                v ^= basis[i]
        out.append(v)
    return out


def _rank(vecs: list[int]) -> int:
    mat = list(vecs)
    r = 0
    for bit in range(max((v.bit_length() for v in mat), default=0) - 1, -1, -1):
        piv = None
        for i in range(r, len(mat)):
            if (mat[i] >> bit) & 1:
                piv = i
                break
        if piv is None:
            continue
        mat[r], mat[piv] = mat[piv], mat[r]
        for i in range(len(mat)):
            if i != r and ((mat[i] >> bit) & 1):
                mat[i] ^= mat[r]
        r += 1
    return r


def classify_window_points(E: Curve, xs: list[int], l: int, h: int) -> list[PointRec]:
    out = []
    for x in xs:
        P = E.lift_x(x)
        if P is None:
            continue
        if h == 4:
            cls = coset_class_h4(E, P, l)
        elif h == 2:
            cls = coset_class_h2(E, P, l)
        else:
            raise ValueError(f"unsupported h={h}")
        out.append(PointRec(P=P, x=x, cls=cls))
    return out


def coset_fractions_x(recs: list[PointRec], h: int) -> dict:
    """Fractions of window x-values by coarse class."""
    n = len(recs)
    if n == 0:
        return {"n_x": 0}
    if h == 4:
        c0 = sum(1 for r in recs if r.cls == 0)
        c2 = sum(1 for r in recs if r.cls == 2)
        c13 = sum(1 for r in recs if r.cls in (1, 3))
        return {
            "n_x": n,
            "class0": c0 / n,
            "class2": c2 / n,
            "class_1_or_3": c13 / n,
            "counts": {"class0": c0, "class2": c2, "class_1_or_3": c13},
            "modeled": {"class0": 0.25, "class2": 0.25, "class_1_or_3": 0.5},
        }
    c0 = sum(1 for r in recs if r.cls == 0)
    c1 = n - c0
    return {
        "n_x": n,
        "class0": c0 / n,
        "class1": c1 / n,
        "counts": {"class0": c0, "class1": c1},
        "modeled": {"class0": 0.5, "class1": 0.5},
        "z4_bookkeeping": "undefined",
    }


def sample_subgroup_targets(E: Curve, cofactor: int, n_targets: int, rng: random.Random) -> list:
    targets = []
    seen = set()
    tries = 0
    while len(targets) < n_targets and tries < n_targets * 2000:
        tries += 1
        x = rng.randrange(0, E.F.q)
        P = E.lift_x(x)
        if P is None:
            continue
        T = E.mul(cofactor, P)
        if T is None:
            continue
        key = (T[0], T[1])
        if key in seen:
            continue
        seen.add(key)
        targets.append(T)
    return targets


def sample_class2_mirrors(E: Curve, l: int, n_targets: int, rng: random.Random) -> list:
    """Points with class 2: [2l]P=O but [l]P!=O. Construct as T2 + C-point."""
    # Find the unique order-2 point T2 = (0, sqrt(B)).
    T2 = E.lift_x(0)
    assert T2 is not None
    mirrors = []
    seen = set()
    tries = 0
    while len(mirrors) < n_targets and tries < n_targets * 2000:
        tries += 1
        x = rng.randrange(1, E.F.q)
        P = E.lift_x(x)
        if P is None:
            continue
        Cpt = E.mul(4, P)  # lands in C when h=4
        if Cpt is None:
            continue
        M = E.add(T2, Cpt)
        if M is None:
            continue
        # verify class 2
        if E.mul(l, M) is None:
            continue
        if E.mul(2 * l, M) is not None:
            continue
        key = (M[0], M[1])
        if key in seen:
            continue
        seen.add(key)
        mirrors.append(M)
    return mirrors


def class_of_point(E: Curve, P, l: int, h: int) -> int:
    if h == 4:
        return coset_class_h4(E, P, l)
    return coset_class_h2(E, P, l)


def _fb_index(recs: list[PointRec]):
    """Map point -> list of indices in recs (include both P and -P via x lookup)."""
    by_x = defaultdict(list)
    for i, r in enumerate(recs):
        by_x[r.x].append(i)
    return by_x


def count_decomps_m2(E: Curve, recs: list[PointRec], targets: list, l: int, h: int):
    """Count signed 2-decompositions T = Q1 + Q2 with Qi in {±P : P in recs}."""
    signed = []
    for r in recs:
        signed.append((r.P, r.cls, r.x))
        Nm = E.neg(r.P)
        nc = ((-r.cls) % 4) if h == 4 else r.cls
        signed.append((Nm, nc, r.x))

    by_pt = {}
    for P, c, x in signed:
        by_pt[(P[0], P[1])] = (c, x)

    mod = 4 if h == 4 else 2
    per_target = []
    violations = 0
    total = 0
    verified = 0
    for T in targets:
        tcls = coset_class_h4(E, T, l) if h == 4 else coset_class_h2(E, T, l)
        cnt = 0
        for Q1, c1, _x1 in signed:
            R = E.sub(T, Q1)
            if R is None:
                continue
            hit = by_pt.get((R[0], R[1]))
            if hit is None:
                continue
            c2, _x2 = hit
            if (c1 + c2) % mod != tcls % mod:
                violations += 1
            if E.add(Q1, R) == T:
                verified += 1
            cnt += 1
        per_target.append(cnt)
        total += cnt
    return {
        "per_target_counts": per_target,
        "total": total,
        "mean": (total / len(targets)) if targets else 0.0,
        "class_sum_violations": violations,
        "certificate_verified_count": verified,
        "m": 2,
    }


def count_decomps_m3(E: Curve, recs: list[PointRec], targets: list, l: int, h: int,
                     instrument_ceiling: int = 5_000_000):
    """MITM census for T = Q1+Q2+Q3 with Qi in {±P : P in recs}."""
    signed = []
    for r in recs:
        signed.append((r.P, r.cls, r.x, 1))
        Nm = E.neg(r.P)
        nc = ((-r.cls) % 4) if h == 4 else r.cls  # Z/2: -1≡1
        signed.append((Nm, nc, r.x, -1))

    pair_map = defaultdict(list)
    ops = 0
    n = len(signed)
    for i in range(n):
        for j in range(i, n):
            ops += 1
            if ops > instrument_ceiling:
                return {
                    "per_target_counts": [],
                    "total": 0,
                    "mean": 0.0,
                    "class_sum_violations": 0,
                    "certificate_verified_count": 0,
                    "m": 3,
                    "termination_reason": "instrument_ceiling",
                    "ops": ops,
                    "targets_completed": 0,
                }
            S = E.add(signed[i][0], signed[j][0])
            key = ("O",) if S is None else (S[0], S[1])
            pair_map[key].append(signed[i][1] + signed[j][1])

    mod = 4 if h == 4 else 2
    per_target = []
    violations = 0
    total = 0
    verified = 0
    completed = 0
    for T in targets:
        tcls = coset_class_h4(E, T, l) if h == 4 else coset_class_h2(E, T, l)
        cnt = 0
        for Q3, c3, x3, _e3 in signed:
            ops += 1
            if ops > instrument_ceiling:
                return {
                    "per_target_counts": per_target,
                    "total": total,
                    "mean": (total / completed) if completed else 0.0,
                    "class_sum_violations": violations,
                    "certificate_verified_count": verified,
                    "m": 3,
                    "termination_reason": "instrument_ceiling",
                    "ops": ops,
                    "targets_completed": completed,
                }
            R = E.sub(T, Q3)
            key = ("O",) if R is None else (R[0], R[1])
            for csum2 in pair_map.get(key, ()):
                if (csum2 + c3) % mod != tcls % mod:
                    violations += 1
                verified += 1
                cnt += 1
        per_target.append(cnt)
        total += cnt
        completed += 1
    return {
        "per_target_counts": per_target,
        "total": total,
        "mean": (total / len(targets)) if targets else 0.0,
        "class_sum_violations": violations,
        "certificate_verified_count": verified,
        "m": 3,
        "termination_reason": "completed",
        "ops": ops,
        "targets_completed": completed,
    }


def build_windows(E: Curve, cell: dict, seed: int, deg_dim: int = 10):
    rng = random.Random(seed)
    F = E.F
    V_xs = window_deg_lt(deg_dim)
    V0_xs = [x for x in V_xs if parity_bit(F, cell["A"], x) == 0]
    rand_xs = random_subspace(cell["n"], deg_dim - 1, rng)
    h = cell["expected_h"]
    l = cell["expected_l"]
    V = classify_window_points(E, V_xs, l, h)
    V0 = classify_window_points(E, V0_xs, l, h)
    Rand = classify_window_points(E, rand_xs, l, h)
    if h == 4:
        VC = [r for r in V if r.cls == 0]
    else:
        VC = [r for r in V if r.cls == 0]
    return {
        "V": V,
        "V_C": VC,
        "V0": V0,
        "random": Rand,
        "meta": {
            "deg_dim": deg_dim,
            "n_V_xs": len(V_xs),
            "n_V0_xs": len(V0_xs),
            "n_random_xs": len(rand_xs),
            "n_V_pts": len(V),
            "n_VC_pts": len(VC),
            "n_V0_pts": len(V0),
            "n_random_pts": len(Rand),
        },
    }


# ---- Z/(4l) generic replica -------------------------------------------------

def replica_coset(x: int) -> int:
    return x % 4


def replica_census(N: int, window_size: int, vc_size: int, v0_size: int, rand_size: int,
                   targets_C: int, mirrors: int, m_list: list[int], seed: int):
    """Relabelled Z/(4l) structure control with residue classes as cosets."""
    rng = random.Random(seed + 17)
    # Build windows as random subsets with forced coset structure for V_C.
    universe = list(range(N))
    V = rng.sample(universe, window_size)
    VC = [x for x in V if replica_coset(x) == 0]
    # If too few, top up from C
    Cset = [x for x in universe if replica_coset(x) == 0]
    while len(VC) < vc_size:
        pick = rng.choice(Cset)
        if pick not in VC:
            VC.append(pick)
    VC = VC[:vc_size]
    V0 = [x for x in V if (x % 2) == 0]  # parity surrogate on Z/N
    while len(V0) < v0_size:
        pick = rng.randrange(0, N, 2)
        if pick not in V0:
            V0.append(pick)
    V0 = V0[:v0_size]
    Rand = rng.sample(universe, rand_size)

    # targets in C
    targets = rng.sample(Cset, min(targets_C, len(Cset)))
    class2 = [x for x in universe if replica_coset(x) == 2]
    mirrors_t = rng.sample(class2, min(mirrors, len(class2)))

    def count_m(window, tlist, m):
        W = list(window)
        # For replica use unordered-with-signs via MITM on additive group
        if m == 2:
            Wset = set(W)
            total = 0
            per = []
            viol = 0
            for t in tlist:
                cnt = 0
                for a in W:
                    for e1 in (1, -1):
                        r = (t - e1 * a) % N
                        # r = e2 * b => b = e2*r with e2=±1 so r or -r in W
                        for e2 in (1, -1):
                            b = (e2 * r) % N
                            # wait: e1*a + e2*b = t => b = e2*(t - e1*a)
                            b = (e2 * ((t - e1 * a) % N)) % N
                            if b in Wset:
                                csum = (replica_coset((e1 * a) % N) + replica_coset((e2 * b) % N)) % 4
                                # signed element class: class(e*x)= e*class(x) mod 4
                                c1 = (e1 * replica_coset(a)) % 4
                                c2 = (e2 * replica_coset(b)) % 4
                                csum = (c1 + c2) % 4
                                tcls = replica_coset(t)
                                if csum != tcls:
                                    viol += 1
                                cnt += 1
                per.append(cnt)
                total += cnt
            return {"per_target_counts": per, "total": total,
                    "mean": total / len(tlist) if tlist else 0.0,
                    "class_sum_violations": viol, "m": 2}
        # m == 3
        signed = []
        for a in W:
            for e in (1, -1):
                signed.append(((e * a) % N, (e * replica_coset(a)) % 4))
        pair = defaultdict(list)
        for i in range(len(signed)):
            for j in range(i, len(signed)):
                s = (signed[i][0] + signed[j][0]) % N
                pair[s].append(signed[i][1] + signed[j][1])
        total = 0
        per = []
        viol = 0
        for t in tlist:
            cnt = 0
            for v, c3 in signed:
                need = (t - v) % N
                for csum2 in pair.get(need, ()):
                    csum = (csum2 + c3) % 4
                    if csum % 4 != replica_coset(t):
                        viol += 1
                    cnt += 1
            per.append(cnt)
            total += cnt
        return {"per_target_counts": per, "total": total,
                "mean": total / len(tlist) if tlist else 0.0,
                "class_sum_violations": viol, "m": 3}

    results = {"windows": {"V": len(V), "V_C": len(VC), "V0": len(V0), "random": len(Rand)},
               "yields": {}, "mirror_VC": {}, "fractions": {}}
    # fractions of V by class
    nV = len(V)
    results["fractions"] = {
        "class0": sum(1 for x in V if replica_coset(x) == 0) / nV,
        "class2": sum(1 for x in V if replica_coset(x) == 2) / nV,
        "class_1_or_3": sum(1 for x in V if replica_coset(x) in (1, 3)) / nV,
        "modeled": {"class0": 0.25, "class2": 0.25, "class_1_or_3": 0.5},
    }
    for m in m_list:
        results["yields"][m] = {
            "V": count_m(V, targets, m),
            "V_C": count_m(VC, targets, m),
            "V0": count_m(V0, targets, m),
            "random": count_m(Rand, targets, m),
        }
        results["mirror_VC"][m] = count_m(VC, mirrors_t, m)
    return results
