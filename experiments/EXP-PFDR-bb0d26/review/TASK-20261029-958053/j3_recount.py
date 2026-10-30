#!/usr/bin/env python3
"""J3 kernel spot-check: disjoint brute-force recount of C and D on nonce-sampled census jobs.

TASK-20261029-958053, REVIEW-PFDR-bb0d26-20261029, EXP-PFDR-bb0d26 (RUN-PFDR-4d8c71 toy-main-jobs.jsonl).

usage:
  j3_recount.py select  <toy-main-jobs.jsonl> <out_sample.json>
  j3_recount.py recount <toy-main-jobs.jsonl> <sample.json> <out_recount.json> [--workers 4]

Written from the hypothesis statement (ledger/hypotheses/H-PFDR-727bfc.yaml) and the specification text
(counting_convention, log_gap_builder, null_builder, planted_builder) only. It does not import or call run.py,
check.py, labelsum.c or vendor/curve.py. Taken from the producer by the review plan's allowance: the seeded
stream derivation random.Random(int(sha256("EXP-PFDR-bb0d26|" + "|".join(labels)))) with labels
("gap"|"plant", block, cell, c) and ("null", block, cell, c, k) (run.py _rng / job), and the semantics of the
vendored Curve.random_point (x = rng.randrange(p) until f(x) is a square, y = the smaller root, then keep P if
rng.random() < 0.5 else -P), re-typed here. Every elliptic-curve operation (affine add, double, double-and-add)
and every square-root / Legendre computation below is this file's own code, on y^2 = x^3 + a x + b over F_p with
(p, a, b) taken from the job record.

Nonce: sha256 of the ASCII hex string of the full commit sha that first added review-plan.yaml (git log
--diff-filter=A), 1eddb4740bb8f4cf74fb27b1b1533a29e4ca120d.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
from collections import Counter
from fractions import Fraction

EXP = "EXP-PFDR-bb0d26"
NONCE_COMMIT = "1eddb4740bb8f4cf74fb27b1b1533a29e4ca120d"
NONCE = hashlib.sha256(NONCE_COMMIT.encode("ascii")).hexdigest()
NULL_REPS = 20


# ------------------------------------------------------------------ seeded streams (allowed derivation)
def stream(*labels) -> random.Random:
    d = hashlib.sha256("|".join(map(str, (EXP,) + labels)).encode()).digest()
    return random.Random(int.from_bytes(d, "big"))


# ------------------------------------------------------------------ own field and curve arithmetic
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
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):  # deterministic for n < 3.3e24
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


def legendre(v: int, p: int) -> int:
    v %= p
    if v == 0:
        return 0
    return 1 if pow(v, (p - 1) // 2, p) == 1 else -1


def my_sqrt(v: int, p: int) -> int:
    """Cipolla square root (own code; deliberately a different algorithm from Tonelli-Shanks)."""
    v %= p
    if v == 0:
        return 0
    assert legendre(v, p) == 1
    t = 0
    while legendre(t * t - v, p) != -1:
        t += 1
    w2 = (t * t - v) % p

    def mul(x, y):  # elements of F_p[sqrt(w2)] as (c0, c1)
        return ((x[0] * y[0] + x[1] * y[1] * w2) % p, (x[0] * y[1] + x[1] * y[0]) % p)

    r, base, e = (1, 0), (t, 1), (p + 1) // 2
    while e:
        if e & 1:
            r = mul(r, base)
        base = mul(base, base)
        e >>= 1
    assert r[1] == 0 and r[0] * r[0] % p == v
    return r[0]


class Curve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p
        assert (4 * self.a ** 3 + 27 * self.b ** 2) % p != 0

    def f(self, x: int) -> int:
        return (x * x * x + self.a * x + self.b) % self.p

    def on(self, P) -> bool:
        return P is None or (P[1] * P[1] - self.f(P[0])) % self.p == 0

    def in_L(self, x: int) -> bool:  # label universe: f(x) a nonzero square
        return legendre(self.f(x), self.p) == 1

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, p - 2, p) % p      # doubling
        else:
            lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p                  # chord
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def mul(self, k: int, P):
        """Affine left-to-right double-and-add; negative k via -P."""
        if k < 0:
            k, P = -k, self.neg(P)
        R = None
        for bit in bin(k)[2:] if k else "":
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def random_point(self, rng: random.Random):
        """Re-typed semantics of the vendored Curve.random_point (allowed seed derivation)."""
        while True:
            x = rng.randrange(self.p)
            fx = self.f(x)
            if fx == 0:
                P = (x, 0)
            elif legendre(fx, self.p) == 1:
                y = my_sqrt(fx, self.p)
                P = (x, min(y, self.p - y))
            else:
                continue
            return P if rng.random() < 0.5 else self.neg(P)


# ------------------------------------------------------------------ set builders from the statement
def half_box_need(n: int) -> int:
    return -(-102 * n // 100) + 8              # ceil(1.02 n) + 8, exact


def half_box_T(r: int, n: int) -> int:
    T = 0
    while ((2 * T + 1) ** r - 1) // 2 < half_box_need(n):
        T += 1
    return T


def half_box(r: int, T: int):
    """[-T, T]^r, lexicographic with every coordinate ascending from -T, first nonzero entry positive."""
    for v in itertools.product(range(-T, T + 1), repeat=r):
        nz = next((x for x in v if x != 0), 0)
        if nz > 0:
            yield v


def gap_set(E: Curve, r: int, n: int, rng: random.Random):
    pts = [E.random_point(rng) for _ in range(r)]
    T = half_box_T(r, n)
    labels, seen = [], set()
    enumerated = dup = inf = 0
    first = last_collected = last_enum = None
    for v in half_box(r, T):
        enumerated += 1
        last_enum = list(v)
        Q = None
        for ci, Pi in zip(v, pts):
            if ci:
                Q = E.add(Q, E.mul(ci, Pi))
        if Q is None:
            inf += 1
            continue
        if Q[0] in seen:
            dup += 1
            continue
        seen.add(Q[0])
        labels.append(Q[0])
        if first is None:
            first = list(v)
        last_collected = list(v)
        if len(labels) == n:
            break
    status = "ok" if len(labels) == n else "degenerate"
    meta = {"T": T, "enumerated": enumerated, "duplicate_skips": dup, "infinity_skips": inf,
            "first": first, "last_collected": last_collected, "last_enumerated": last_enum,
            "labels_collected": len(labels), "half_box_size": ((2 * T + 1) ** r - 1) // 2}
    return labels, meta, status, pts


def null_set(E: Curve, n: int, rng: random.Random):
    out, seen = [], set()
    while len(out) < n:
        x = rng.randrange(E.p)
        if x in seen:
            continue
        if E.in_L(x):
            seen.add(x)
            out.append(x)
    return out


def internal_counts(E: Curve, ap: list[int]) -> list[int]:
    """internal[m] = C of the first m AP labels, incrementally (C rises by m_s when a pair joins sum s)."""
    p, ms, C, res = E.p, Counter(), 0, [0]
    for i, u in enumerate(ap):
        for v in ap[:i]:
            s = (u + v) % p
            C += ms[s]
            ms[s] += 1
        res.append(C)
    return res


def plant_set(E: Curve, n: int, rng: random.Random, null_C: list[int]):
    p = E.p
    x0 = rng.randrange(p)
    w = rng.randrange(1, p)
    cap = n // 2
    ap, k = [], 0
    while len(ap) < cap:
        xk = (x0 + k * w) % p
        if E.in_L(xk):
            ap.append(xk)
        k += 1
    inter = internal_counts(E, ap)
    tot = sum(null_C)
    m_exact = next((m for m in range(4, cap + 1) if Fraction(inter[m]) >= Fraction(3, 10) * Fraction(tot, len(null_C))), None)
    m_float = next((m for m in range(4, cap + 1) if inter[m] >= 0.30 * (tot / len(null_C))), None)
    feasible = m_exact is not None
    m = m_exact if feasible else cap
    out, seen = list(ap[:m]), set(ap[:m])
    while len(out) < n:
        x = rng.randrange(p)
        if x in seen:
            continue
        if E.in_L(x):
            seen.add(x)
            out.append(x)
    return out, {"m": m, "internal": inter[m], "feasible": feasible, "m_float_rule": m_float,
                 "internal_m_minus_1": inter[m - 1] if m >= 1 else None, "x0": x0, "w": w}


# ------------------------------------------------------------------ brute-force counting (own)
def count_CD(labels: list[int], p: int) -> tuple[int, int]:
    """C = sum_s binom(m_s, 2), m_s = #{{u, v}: u != v, u + v = s mod p}; D = #{s : m_s >= 1}."""
    assert len(set(labels)) == len(labels)
    cnt = Counter()
    L = list(labels)
    for i in range(len(L) - 1):
        u = L[i]
        cnt.update([(u + v) % p for v in L[i + 1:]])
    return sum(m * (m - 1) // 2 for m in cnt.values()), len(cnt)


# ------------------------------------------------------------------ sampling by nonce
def key(rec) -> str:
    return hashlib.sha256(f"{NONCE}|{rec['cell']}|{rec['c']}".encode()).hexdigest()


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def select(recs):
    ok = [r for r in recs if r["status"] == "ok"]
    chosen, why = [], {}
    for bits in (20, 24, 28):
        for r in (1, 2, 3):
            pool = sorted((x for x in ok if x["bits"] == bits and x["r"] == r), key=key)
            chosen.append(pool[0])
            why[(pool[0]["cell"], pool[0]["c"])] = f"A: stratum bits={bits} r={r}, min nonce key of {len(pool)} ok records"
    for n in (1024, 2048, 4096):
        pool = sorted((x for x in ok if x["n"] == n and (x["cell"], x["c"]) not in why), key=key)
        for x in pool[:2]:
            chosen.append(x)
            why[(x["cell"], x["c"])] = f"B: n={n}, one of the 2 smallest nonce keys of {len(pool)} remaining ok records"
    degen = [x for x in recs if x["status"] == "degenerate"]
    return ([{"cell": x["cell"], "c": x["c"], "bits": x["bits"], "r": x["r"], "n": x["n"], "key": key(x),
              "why": why[(x["cell"], x["c"])]} for x in chosen],
            [{"cell": x["cell"], "c": x["c"], "bits": x["bits"], "r": x["r"], "n": x["n"]} for x in degen])


# ------------------------------------------------------------------ one job
def recount_job(args):
    rec, gap_only = args
    E = Curve(rec["p"], rec["a"], rec["b_coef"])
    N, n, r, cell, c, block = rec["N"], rec["n"], rec["r"], rec["cell"], rec["c"], rec["block"]
    out = {"cell": cell, "c": c, "bits": rec["bits"], "r": r, "n": n, "p": E.p, "N": N, "fields": {}}
    curve_checks = {"p_prime": is_prime(E.p), "N_prime": is_prime(N),
                    "hasse": abs(E.p + 1 - N) <= 2 * int(E.p ** 0.5) + 2}
    labels, meta, status, pts = gap_set(E, r, n, stream("gap", block, cell, c))
    curve_checks["base_points_on_curve"] = all(E.on(P) for P in pts)
    curve_checks["N_times_base_points_is_O"] = all(E.mul(N, P) is None for P in pts)
    out["curve_checks"] = curve_checks
    out["gap_meta_own"] = meta
    out["gap_status_own"] = status
    F = out["fields"]

    def cmp(name, own, recd):
        F[name] = {"own": own, "recorded": recd, "equal": own == recd}

    rm = rec["gap_meta"]
    cmp("status", status, rec["status"])
    for k in ("T", "enumerated", "duplicate_skips", "infinity_skips", "first"):
        cmp(f"gap_meta.{k}", meta[k], rm.get(k))
    cmp("gap_meta.last", meta["last_collected"] if status == "ok" else meta["last_enumerated"], rm.get("last"))
    if gap_only or status != "ok":
        return out
    assert all(E.in_L(x) for x in labels)
    gC, gD = count_CD(labels, E.p)
    cmp("gap_C", gC, rec["gap_C"])
    cmp("gap_D", gD, rec["gap_D"])
    nulls = [null_set(E, n, stream("null", block, cell, c, k)) for k in range(NULL_REPS)]
    nCD = [count_CD(s, E.p) for s in nulls]
    for k in range(NULL_REPS):
        cmp(f"null_C[{k}]", nCD[k][0], rec["null_C"][k])
        cmp(f"null_D[{k}]", nCD[k][1], rec["null_D"][k])
    # the plant threshold uses the recorded null_C (equal to the recount if the fields above are equal)
    pl, pm = plant_set(E, n, stream("plant", block, cell, c), [x[0] for x in nCD])
    pC, pD = count_CD(pl, E.p)
    cmp("plant_C", pC, rec["plant_C"])
    cmp("plant_D", pD, rec["plant_D"])
    cmp("plant_m", pm["m"], rec["plant_m"])
    cmp("plant_internal", pm["internal"], rec["plant_internal"])
    cmp("plant_feasible", pm["feasible"], rec["plant_feasible"])
    out["plant_own_extra"] = {k: pm[k] for k in ("m_float_rule", "internal_m_minus_1", "x0", "w")}
    out["plant_threshold_exact"] = {"three_tenths_mean_null_C": str(Fraction(3, 10) * Fraction(sum(x[0] for x in nCD), NULL_REPS)),
                                    "internal_m_ge_threshold": True if pm["feasible"] else None,
                                    "internal_m_minus_1_below_threshold":
                                        (pm["m"] == 4) or (Fraction(pm["internal_m_minus_1"]) < Fraction(3, 10) * Fraction(sum(x[0] for x in nCD), NULL_REPS))}
    out["all_equal"] = all(v["equal"] for v in F.values())
    return out


def main(argv):
    if argv[0] == "select":
        recs = load(argv[1])
        chosen, degen = select(recs)
        with open(argv[2], "w") as f:
            json.dump({"nonce_commit": NONCE_COMMIT, "nonce": NONCE,
                       "procedure": ("key(rec) = sha256(nonce + '|' + cell + '|' + str(c)). A: for each (bits, r) in "
                                     "{20,24,28} x {1,2,3}, the ok record of that stratum with the smallest key. B: for each "
                                     "n in {1024, 2048, 4096}, the 2 not-yet-chosen ok records with that n and the smallest "
                                     "keys. G: every degenerate record (gap builder only; no C or D is recorded for them)."),
                       "jobs": chosen, "degenerate_gap_only": degen}, f, indent=1)
        print(json.dumps(chosen, indent=1))
        return 0
    if argv[0] == "recount":
        workers = 4
        if "--workers" in argv:
            workers = int(argv[argv.index("--workers") + 1])
        recs = load(argv[1])
        by = {(r["cell"], r["c"]): r for r in recs}
        with open(argv[2]) as f:
            sample = json.load(f)
        tasks = [(by[(j["cell"], j["c"])], False) for j in sample["jobs"]]
        tasks += [(by[(j["cell"], j["c"])], True) for j in sample["degenerate_gap_only"]]
        tasks.sort(key=lambda t: -t[0]["n"])
        import multiprocessing as mp
        import time
        t0 = time.time()
        with mp.Pool(workers) as pool:
            res = pool.map(recount_job, tasks, chunksize=1)
        res.sort(key=lambda o: (o["bits"], o["r"], o["n"], o["c"]))
        summary = {"jobs_recounted_all_arms": sum(1 for t in tasks if not t[1]),
                   "degenerate_gap_only": sum(1 for t in tasks if t[1]),
                   "fields_compared": sum(len(o["fields"]) for o in res),
                   "fields_differing": [f"{o['cell']}/c{o['c']}/{k}" for o in res for k, v in o["fields"].items() if not v["equal"]],
                   "curve_checks_failed": [f"{o['cell']}/c{o['c']}/{k}" for o in res for k, v in o["curve_checks"].items() if not v],
                   "wall_seconds": round(time.time() - t0, 1),
                   "python": sys.version, "executable": sys.executable}
        with open(argv[3], "w") as f:
            json.dump({"summary": summary, "jobs": res}, f, indent=1)
        print(json.dumps(summary, indent=1))
        return 0 if not summary["fields_differing"] and not summary["curve_checks_failed"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
