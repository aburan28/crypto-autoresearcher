#!/usr/bin/env python3
"""V3: independent instance and chained-decomposition certificate checks.
Own arithmetic only (pure python ints mod p). No producer artifact read.
"""
import json
from itertools import combinations

P = 4099
W = range(0, 8)          # declared window [0, 8)

INST = [
    (4101, 2975, 3349, 1, 3091, 2292),
    (4101, 2975, 3349, 2, 1163, 3046),
    (4102, 1174, 2571, 1, 1343, 2173),
    (4102, 1174, 2571, 2, 3446, 264),
    (4103, 743, 2019, 1, 1903, 197),
    (4103, 743, 2019, 2, 3423, 3278),
    (4104, 1581, 2498, 1, 3746, 3001),
    (4104, 1581, 2498, 2, 3376, 3105),
    (4105, 181, 2138, 1, 2028, 1263),
    (4105, 181, 2138, 2, 344, 3919),
    (4106, 3669, 1241, 1, 940, 1845),
    (4106, 3669, 1241, 2, 276, 1845),
]

INF = None


def sqrt_mod(a):
    a %= P
    if a == 0:
        return 0
    if pow(a, (P - 1) // 2, P) != 1:
        return None
    assert P % 4 == 3
    return pow(a, (P + 1) // 4, P)


def on_curve(x, y, A, B):
    return (y * y - (x * x * x + A * x + B)) % P == 0


def add(Pt, Q, A):
    if Pt is INF:
        return Q
    if Q is INF:
        return Pt
    x1, y1 = Pt
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % P == 0:
        return INF
    if Pt == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1 % P, P - 2, P) % P
    else:
        lam = (y2 - y1) * pow((x2 - x1) % P, P - 2, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def neg(Pt):
    return INF if Pt is INF else (Pt[0], (-Pt[1]) % P)


out = []
for (seed, A, B, tgt, u, xR) in INST:
    disc = (4 * pow(A, 3, P) + 27 * B * B) % P
    j_num = (1728 * 4 * pow(A, 3, P)) % P
    j = j_num * pow(disc, P - 2, P) % P if disc else None
    pts = []
    for x in W:
        rhs = (x * x * x + A * x + B) % P
        y = sqrt_mod(rhs)
        if y is None:
            continue
        pts.append((x, y))
        assert on_curve(x, y, A, B)
    window_xs = [p[0] for p in pts]

    # u realised as x(P1 (+/-) P2) for two DISTINCT window points
    u_witness = None
    for i, j2 in combinations(range(len(pts)), 2):
        for s2 in (1, -1):
            Q = add(pts[i], pts[j2] if s2 == 1 else neg(pts[j2]), A)
            if Q is not INF and Q[0] == u:
                u_witness = (pts[i][0], pts[j2][0], s2, Q)
                break
        if u_witness:
            break

    # x_R realised as x(P1 (+/-) P2 (+/-) P3) with a third window point
    chain_witness = None
    for i, j2 in combinations(range(len(pts)), 2):
        for s2 in (1, -1):
            Q = add(pts[i], pts[j2] if s2 == 1 else neg(pts[j2]), A)
            if Q is INF or Q[0] != u:
                continue
            for k in range(len(pts)):
                if k in (i, j2):
                    continue
                for s3 in (1, -1):
                    Rp = add(Q, pts[k] if s3 == 1 else neg(pts[k]), A)
                    if Rp is not INF and Rp[0] == xR:
                        chain_witness = dict(
                            x1=pts[i][0], x2=pts[j2][0], sign2=s2,
                            x3=pts[k][0], sign3=s3, u_check=Q[0], xR_check=Rp[0])
                        break
                if chain_witness:
                    break
            if chain_witness:
                break
        if chain_witness:
            break

    # allow a repeated window point as the third summand (weaker variant)
    chain_witness_rep = None
    if chain_witness is None:
        for i, j2 in combinations(range(len(pts)), 2):
            for s2 in (1, -1):
                Q = add(pts[i], pts[j2] if s2 == 1 else neg(pts[j2]), A)
                if Q is INF or Q[0] != u:
                    continue
                for k in range(len(pts)):
                    for s3 in (1, -1):
                        Rp = add(Q, pts[k] if s3 == 1 else neg(pts[k]), A)
                        if Rp is not INF and Rp[0] == xR:
                            chain_witness_rep = dict(
                                x1=pts[i][0], x2=pts[j2][0], sign2=s2,
                                x3=pts[k][0], sign3=s3, repeated=True)
    out.append(dict(curve_seed=seed, target=tgt, A=A, B=B, u=u, x_R=xR,
                    nonsingular=(disc != 0), A_nonzero=(A != 0),
                    B_nonzero=(B != 0), j_invariant=j,
                    j_special=(j in (0, 1728)),
                    window_points_x=window_xs,
                    n_window_x=len(window_xs),
                    at_least_three_window_x=len(window_xs) >= 3,
                    u_in_window=(u in list(W)), xR_in_window=(xR in list(W)),
                    u_witness=None if not u_witness else
                    dict(x1=u_witness[0], x2=u_witness[1], sign2=u_witness[2]),
                    chain_certificate=chain_witness,
                    chain_certificate_repeated_point=chain_witness_rep))
    c = out[-1]
    print(f"{seed}/t{tgt} A={A} B={B} u={u} xR={xR} nonsing={c['nonsingular']} "
          f"j={j} special={c['j_special']} window_x={window_xs} "
          f"u_ok={c['u_witness'] is not None} chain_ok={chain_witness is not None}"
          f"{'' if chain_witness_rep is None else ' (repeated-point witness)'}")

trip = {}
for (seed, A, B, tgt, u, xR) in INST:
    trip.setdefault((A, B, xR), []).append(f"{seed}/t{tgt}")
print("\ndistinct generator triples (A,B,x_R):", len(trip))
for k, v in trip.items():
    if len(v) > 1:
        print("  DUPLICATE generator system:", k, v)
print("distinct curves (A,B):", len({(a, b) for (_, a, b, _, _, _) in INST}))
json.dump(out, open('v3_instances.json', 'w'), indent=1)
