"""Check 5 (validator, VAL-20260929-sembin473340): is the 'formal' convention
the Macaulay filtration of {f} union S_fe in the POLYNOMIAL ring F_2[u]?

In F_2[u_0..u_{N-1}] (no u^2 = u reduction; monomials are exponent vectors),
with generators G = {f_1..f_k} (squarefree, as given) union
S_fe = {u_j^2 + u_j : j < N}:
    V'_D = span{ mu * g : g in G, mu a monomial, deg mu + deg g <= D }
    falls'(D) = dim(V'_D cap F_2[u]_{<=D-1});  new'(D) = falls'(D) - dim V'_{D-1}
Claim tested: new'(D) == new_falls_formal(D) (vbr.py) for every D, hence the
same d_ff. Proof sketch recorded in the validation report: pi: F_2[u] -> B is
onto degree-wise, ker pi cap F_2[u]_{<=D} = S_fe-multiples of degree <= D
(u_j^2 lead terms are pairwise coprime, so S_fe is a Groebner basis for any
degree-compatible order), hence ker pi cap F_2[u]_{<=D} is inside V'_D and
cancels in the difference.

Multiplying by a monomial in F_2[u] is an exponent shift, so rows have no
cancellation; linear algebra is on int bitsets over the monomials of degree
<= Dmax.

usage: python3 polyring_formal_check.py OUT.json
"""
import sys, os, json, random, itertools, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vbr  # noqa: E402
import blind_rederive as BR  # noqa: E402  (system construction, see its header)


def monomials_upto(N, Dmax):
    out = []
    for d in range(Dmax + 1):
        for c in itertools.combinations_with_replacement(range(N), d):
            e = [0] * N
            for i in c:
                e[i] += 1
            out.append(tuple(e))
    return out


def poly_profile(eqs, N, Dmax):
    monos = monomials_upto(N, Dmax)
    idx = {m: i for i, m in enumerate(monos)}
    deg = [sum(m) for m in monos]
    # generators as dict: list of exponent tuples
    gens = []
    for f in eqs:
        terms = [tuple((t >> j) & 1 for j in range(N)) for t in f]
        gens.append((max(sum(t) for t in terms), terms))
    for j in range(N):
        sq = [0] * N; sq[j] = 2
        li = [0] * N; li[j] = 1
        gens.append((2, [tuple(sq), tuple(li)]))
    prof = {}
    prev = 0
    for D in range(0, Dmax + 1):
        rows = []
        for dg, terms in gens:
            if dg > D:
                continue
            for mu in monos:
                if sum(mu) + dg > D:
                    continue
                r = 0
                for t in terms:
                    r ^= 1 << idx[tuple(a + b for a, b in zip(mu, t))]
                rows.append(r)
        top = 0
        for i, d in enumerate(deg):
            if d == D:
                top |= 1 << i
        dV = vbr.rank(rows)
        dT = vbr.rank([r & top for r in rows])
        falls = dV - dT
        prof[D] = (dV, falls, falls - prev)
        prev = dV
    return prof


def compare(eqs, N, Dmax):
    pp = poly_profile(eqs, N, Dmax)
    bp = vbr.profile(eqs, N, Dmax, "formal")
    new_p = [pp[D][2] for D in range(1, Dmax + 1)]
    new_b = [bp[D][2] for D in range(1, Dmax + 1)]
    return new_p == new_b, new_p, new_b, vbr.dff(pp), vbr.dff(bp)


def main():
    out = dict(hand_example=None, random_small=None, experiment_systems=[])
    t0 = time.time()
    # (a) the hand-worked example: N = 3, f = u0u1 + u0 + u1
    f = frozenset({0b011, 0b001, 0b010})
    ok, np_, nb, dp, db = compare([f], 3, 3)
    red = vbr.profile([f], 3, 3, "reduced")
    out["hand_example"] = dict(N=3, f="u0u1 + u0 + u1", agree=ok, polyring_new_falls_D1toD3=np_,
                               formal_new_falls_D1toD3=nb, polyring_dff=dp, formal_dff=db,
                               reduced_new_falls_D1toD3=[red[D][2] for D in (1, 2, 3)],
                               reduced_dff=vbr.dff(red))
    # (b) random small systems, N in 2..4, degree <= 3 generators
    rng = random.Random(4733400929)
    agree = total = 0; differs_from_reduced = 0; bad = []
    for _ in range(300):
        N = rng.randint(2, 4)
        k = rng.randint(1, 3)
        eqs = []
        for _ in range(k):
            f = frozenset(m for m in range(1 << N) if vbr.popc(m) <= 3 and rng.random() < 0.4)
            if f:
                eqs.append(f)
        if not eqs:
            continue
        ok, np_, nb, dp, db = compare(eqs, N, N)
        total += 1; agree += ok
        if not ok:
            bad.append(dict(N=N, eqs=[sorted(f) for f in eqs], poly=np_, formal=nb))
        if vbr.dff(vbr.profile(eqs, N, N, "reduced")) != db:
            differs_from_reduced += 1
    out["random_small"] = dict(agree=agree, total=total, systems_where_formal_dff_differs_from_reduced=differs_from_reduced,
                               disagreements=bad[:5])
    # (c) real experiment systems: all 35 of (4,3) (N = 6, Dmax 6) and the (6,4)
    #     s = 0 Semaev system plus 3 nulls (N = 8, Dmax 6)
    for (n, npr, limit) in ((4, 3, None), (6, 4, 4)):
        cnt = 0
        for kind, idx, meta, eqs in BR.systems(n, npr):
            if limit is not None and cnt >= limit:
                break
            N = 2 * npr; Dmax = min(N, 6)
            c0 = time.time()
            ok, np_, nb, dp, db = compare(eqs, N, Dmax)
            out["experiment_systems"].append(dict(cell=[n, npr], kind=kind, idx=idx, agree=ok,
                                                  polyring_new_falls=np_, formal_new_falls=nb,
                                                  polyring_dff=dp, formal_dff=db,
                                                  seconds=round(time.time() - c0, 2)))
            print(json.dumps(out["experiment_systems"][-1]), flush=True)
            cnt += 1
    out["elapsed_seconds"] = round(time.time() - t0, 1)
    out["summary"] = dict(hand=out["hand_example"]["agree"],
                          random_small=f'{out["random_small"]["agree"]}/{out["random_small"]["total"]}',
                          experiment=f'{sum(e["agree"] for e in out["experiment_systems"])}/{len(out["experiment_systems"])}')
    print(json.dumps(out["summary"]), json.dumps(out["hand_example"]))
    json.dump(out, open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
