#!/usr/bin/env python3
"""Certificate mathematics for EXP-PFDR-bb0d26 with auditor-written arithmetic. Read-only.

Shares no code with the producer: no import of run.py, check.py, vendor/curve.py or the C kernel.
Own Miller-Rabin, own Jacobian-coordinate group law, own Euler criterion, own Tonelli-Shanks, own
pair-sum counter (collections.Counter over (u+v) mod p). The only thing taken from the producer side is
the SEEDING CONVENTION needed to regenerate a specific job's label sets (random.Random seeded by
int.from_bytes(sha256("EXP-PFDR-bb0d26|kind|block|cell|c[|k]"), "big"); random_point draws
x = randrange(p) until f(x) is a square, takes the smaller root y, then negates if random() >= 0.5).
That convention is stated by specification.yaml l.103-114 and was read from run.py/_rng and
vendor/curve.py random_point; the arithmetic that verifies the counts is independent.

Units checked:
  census-toy-main  RUN-PFDR-4d8c71 (replayed): (a) every distinct curve of the jobs file: p prime,
      N prime, N != p, Hasse, nonsingular, j != 0, 1728, and [N]P = O for two random points, which with
      N prime and N > 4 sqrt(p) certifies #E(F_p) = N; (b) every record: T is the least half-box
      parameter for (r, n), and for r = 1 the enumeration is forced (enumerated = n, no skips, last = [n]);
      (c) a nonce-chosen sample of jobs: gap_C, gap_D and all 20 null_C, null_D recounted from regenerated
      label sets.
  selftest RUN-PFDR-e44a19 (not replayed): every known-answer set of fixtures/kat.json recounted (C, D);
      label universes recounted; half-box table recomputed; selftest.json all-pass.
  analyze-main RUN-PFDR-243425 / analyze-final RUN-PFDR-089edc (replayed): see blind_rederive.py; here
      only the cross-file identity of analysis-main.json and analysis.json cells and the flags files.

Usage: cert_check.py EXP_DIR NONCE
"""
import collections
import hashlib
import json
import math
import os
import random
import sys

EXP = "EXP-PFDR-bb0d26"


# ---------------------------------------------------------------- number theory (own)
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):  # deterministic below 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def is_qr_nonzero(f: int, p: int) -> bool:
    return f % p != 0 and pow(f, (p - 1) // 2, p) == 1


def tonelli(n: int, p: int) -> int:
    n %= p
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


# ---------------------------------------------------------------- Jacobian group law (own)
INF = (1, 1, 0)


def jdbl(P, a, p):
    X, Y, Z = P
    if Z == 0 or Y == 0:
        return INF
    S = 4 * X * Y * Y % p
    M = (3 * X * X + a * pow(Z, 4, p)) % p
    X3 = (M * M - 2 * S) % p
    Y3 = (M * (S - X3) - 8 * pow(Y, 4, p)) % p
    return (X3, Y3, 2 * Y * Z % p)


def jadd(P, Q, a, p):
    if P[2] == 0:
        return Q
    if Q[2] == 0:
        return P
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1s, Z2s = Z1 * Z1 % p, Z2 * Z2 % p
    U1, U2 = X1 * Z2s % p, X2 * Z1s % p
    S1, S2 = Y1 * Z2s * Z2 % p, Y2 * Z1s * Z1 % p
    if U1 == U2:
        return jdbl(P, a, p) if S1 == S2 else INF
    H, R = (U2 - U1) % p, (S2 - S1) % p
    H2 = H * H % p
    H3 = H2 * H % p
    X3 = (R * R - H3 - 2 * U1 * H2) % p
    Y3 = (R * (U1 * H2 - X3) - S1 * H3) % p
    return (X3, Y3, H * Z1 * Z2 % p)


def jmul(k, P, a, p):
    R = INF
    for bit in bin(k)[2:]:
        R = jdbl(R, a, p)
        if bit == "1":
            R = jadd(R, P, a, p)
    return R


def affine(P, p):
    if P[2] == 0:
        return None
    zi = pow(P[2], -1, p)
    return (P[0] * zi * zi % p, P[1] * zi * zi * zi % p)


def jneg(P, p):
    return (P[0], (-P[1]) % p, P[2])


# ---------------------------------------------------------------- counting (own)
def count_CD(X, p):
    cnt = collections.Counter()
    n = len(X)
    for i in range(n):
        u = X[i]
        for j in range(i + 1, n):
            cnt[(u + X[j]) % p] += 1
    return sum(m * (m - 1) // 2 for m in cnt.values()), len(cnt)


# ---------------------------------------------------------------- label regeneration
def rng_of(*labels):
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


def rhs(x, a, b, p):
    return (x * x * x + a * x + b) % p


def rand_point(rng, a, b, p):
    while True:
        x = rng.randrange(p)
        f = rhs(x, a, b, p)
        if f == 0:
            y = 0
        elif pow(f, (p - 1) // 2, p) == 1:
            y = tonelli(f, p)
        else:
            continue
        y = min(y, p - y)
        if rng.random() >= 0.5:
            y = (-y) % p
        return (x, y, 1)


def need_of(n):
    return -(-(102 * n) // 100) + 8


def T_of(r, n):
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < need_of(n):
        T += 1
    return T


def half_box(r, T):
    import itertools
    for v in itertools.product(range(-T, T + 1), repeat=r):
        nz = next((e for e in v if e != 0), 0)
        if nz > 0:
            yield v


def gap_labels(rec):
    p, a, b, r, n = rec["p"], rec["a"], rec["b_coef"], rec["r"], rec["n"]
    rng = rng_of("gap", rec["block"], rec["cell"], rec["c"])
    pts = [rand_point(rng, a, b, p) for _ in range(r)]
    T = T_of(r, n)
    tabs = []
    for P in pts:
        tab = {0: INF}
        acc = INF
        for k in range(1, T + 1):
            acc = jadd(acc, P, a, p)
            tab[k], tab[-k] = acc, jneg(acc, p)
        tabs.append(tab)
    out, seen, enum, dup, inf = [], set(), 0, 0, 0
    last = None
    for v in half_box(r, T):
        enum += 1
        Q = INF
        for tab, ci in zip(tabs, v):
            Q = jadd(Q, tab[ci], a, p)
        A = affine(Q, p)
        if A is None:
            inf += 1
            continue
        if A[0] in seen:
            dup += 1
            continue
        seen.add(A[0])
        out.append(A[0])
        last = list(v)
        if len(out) == n:
            break
    return out, {"T": T, "enumerated": enum, "duplicate_skips": dup, "infinity_skips": inf, "last": last}


def null_labels(rec, k):
    p, a, b, n = rec["p"], rec["a"], rec["b_coef"], rec["n"]
    rng = rng_of("null", rec["block"], rec["cell"], rec["c"], k)
    out, seen = [], set()
    while len(out) < n:
        x = rng.randrange(p)
        if x in seen or not is_qr_nonzero(rhs(x, a, b, p), p):
            continue
        seen.add(x)
        out.append(x)
    return out


# ---------------------------------------------------------------- checks
def check_curves(recs):
    curves = {}
    for r in recs:
        curves.setdefault((r["bits"], r["p"], r["a"], r["b_coef"], r["N"]), 0)
        curves[(r["bits"], r["p"], r["a"], r["b_coef"], r["N"])] += 1
    rng = random.Random(0xA0D17)
    bad = []
    for (bits, p, a, b, N) in curves:
        why = []
        if not is_prime(p):
            why.append("p not prime")
        if not (2 ** (bits - 1) <= p < 2 ** bits):
            why.append("p bit length")
        if not is_prime(N):
            why.append("N not prime")
        if N == p:
            why.append("anomalous")
        if (N - p - 1) ** 2 > 4 * p:
            why.append("outside Hasse")
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            why.append("singular")
        if a % p == 0 or b % p == 0:
            why.append("j in {0,1728}")
        if N * N <= 16 * p:
            why.append("N <= 4 sqrt p: order not forced by one point")
        for _ in range(2):
            P = rand_point(rng, a, b, p)
            if jmul(N, P, a, p)[2] != 0:
                why.append("[N]P != O")
        if why:
            bad.append([bits, p, a, b, N, why])
    return {"distinct_curves": len(curves), "curves_failing": bad,
            "per_bits": dict(collections.Counter(k[0] for k in curves))}


def check_meta(recs):
    bad = []
    for r in recs:
        m = r["gap_meta"]
        if m is None:
            bad.append([r["cell"], r["c"], "no gap_meta"])
            continue
        if m["T"] != T_of(r["r"], r["n"]):
            bad.append([r["cell"], r["c"], "T", m["T"], T_of(r["r"], r["n"])])
        if r["r"] == 1 and (m["enumerated"] != r["n"] or m["duplicate_skips"] or m["infinity_skips"]
                            or m["first"] != [1] or m["last"] != [r["n"]]):
            bad.append([r["cell"], r["c"], "r=1 enumeration not forced", m])
        if r["status"] == "ok" and m["enumerated"] - m["duplicate_skips"] - m["infinity_skips"] != r["n"]:
            bad.append([r["cell"], r["c"], "enumerated - skips != n", m])
        if r["status"] == "degenerate" and m["enumerated"] != ((2 * m["T"] + 1) ** r["r"] - 1) // 2:
            bad.append([r["cell"], r["c"], "degenerate but half-box not exhausted", m])
    return {"records": len(recs), "failing": bad}


def recount_sample(recs, nonce):
    ok = [r for r in recs if r["status"] == "ok" and r["n"] <= 512]
    ok.sort(key=lambda r: hashlib.sha256(f"{nonce}|{r['cell']}|{r['c']}".encode()).hexdigest())
    chosen, seen_rb = [], set()
    for r in ok:  # one job per (bits, r) among n <= 512, i.e. 9 jobs spanning every bit size and rank
        if (r["bits"], r["r"]) not in seen_rb:
            seen_rb.add((r["bits"], r["r"]))
            chosen.append(r)
    out = []
    for r in chosen:
        X, meta = gap_labels(r)
        gC, gD = count_CD(X, r["p"])
        nulls = [count_CD(null_labels(r, k), r["p"]) for k in range(20)]
        res = {"cell": r["cell"], "c": r["c"], "p": r["p"],
               "gap": {"C": [gC, r["gap_C"]], "D": [gD, r["gap_D"]],
                       "meta_equal": all(meta[k] == r["gap_meta"][k] for k in meta)},
               "null_C_equal": [x[0] for x in nulls] == r["null_C"],
               "null_D_equal": [x[1] for x in nulls] == r["null_D"],
               "labels_in_universe": all(is_qr_nonzero(rhs(x, r["a"], r["b_coef"], r["p"]), r["p"]) for x in X),
               "labels_distinct": len(set(X)) == len(X) == r["n"]}
        res["pass"] = (gC == r["gap_C"] and gD == r["gap_D"] and res["gap"]["meta_equal"] and res["null_C_equal"]
                       and res["null_D_equal"] and res["labels_in_universe"] and res["labels_distinct"])
        out.append(res)
    return out


def check_selftest(exp):
    kat = json.load(open(os.path.join(exp, "implementation/fixtures/kat.json")))
    sets_bad = []
    for s in kat["sets"]:
        C, D = count_CD(s["X"], s["p"])
        if (C, D) != (s["C"], s["D"]) or len(set(s["X"])) != len(s["X"]):
            sets_bad.append([s["name"], [C, D], [s["C"], s["D"]]])
    lu_bad = []
    for e in kat["label_universe"]:
        L = [x for x in range(e["p"]) if is_qr_nonzero(rhs(x, e["a"], e["b"], e["p"]), e["p"])]
        if L != e["L"]:
            lu_bad.append([e["p"], e["a"], e["b"], len(L), len(e["L"])])
    hb_bad = [h for h in kat["half_box"] if h["T"] != T_of(h["r"], h["n"]) or h["need"] != need_of(h["n"])
              or h["size"] != ((2 * h["T"] + 1) ** h["r"] - 1) // 2]
    hv_bad = []
    for key, vecs in kat["half_box_vectors"].items():
        r, T = int(key[1]), int(key[3:])
        if [list(v) for v in half_box(r, T)] != vecs:
            hv_bad.append(key)
    st = json.load(open(os.path.join(exp, "runs/RUN-PFDR-e44a19/selftest.json")))
    names = collections.Counter(c["name"].split(":")[0] for c in st["checks"])
    return {"kat_sets": len(kat["sets"]), "kat_sets_failing": sets_bad,
            "label_universes": len(kat["label_universe"]), "label_universes_failing": lu_bad,
            "half_box_rows": len(kat["half_box"]), "half_box_failing": hb_bad,
            "half_box_vector_lists_failing": hv_bad,
            "selftest_json": {"pass": st["pass"], "checks": len(st["checks"]),
                              "checks_passing": sum(bool(c["pass"]) for c in st["checks"]),
                              "kernel_vs_brute_sets": names.get("kernel-vs-brute", 0),
                              "scaling_identity_sets": names.get("scaling-identity", 0)}}


def check_analyze_cross(exp):
    a = json.load(open(os.path.join(exp, "runs/RUN-PFDR-243425/analysis-main.json")))
    b = json.load(open(os.path.join(exp, "runs/RUN-PFDR-089edc/analysis.json")))
    f1 = json.load(open(os.path.join(exp, "runs/RUN-PFDR-243425/flags.json")))
    f2 = json.load(open(os.path.join(exp, "runs/RUN-PFDR-089edc/flags.json")))
    rep = os.path.getsize(os.path.join(exp, "runs/RUN-PFDR-cd03e2/toy-rep-jobs.jsonl"))
    keys = sorted((set(a) | set(b)) - {"stage"})
    return {"main_vs_final_differing_keys": [k for k in keys if a.get(k) != b.get(k)],
            "stages": [a["stage"], b["stage"]], "flags_main": f1, "flags_final": f2,
            "toy_rep_jobs_bytes": rep}


def main():
    exp, nonce = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in open(os.path.join(exp, "runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl")) if l.strip()]
    out = {"census_main_curves": check_curves(recs),
           "census_main_meta": check_meta(recs),
           "census_main_recount": recount_sample(recs, nonce),
           "selftest": check_selftest(exp),
           "analyze_cross": check_analyze_cross(exp)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
