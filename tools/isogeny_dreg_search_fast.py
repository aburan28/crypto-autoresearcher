#!/usr/bin/env python3
"""Fast engine for the certified exhaustive isogeny-class search.

Same search, same certificate, same functionals as the pure-Python
reference engine `tools/isogeny_dreg_search.py`, built to run the whole
F_p-isogeny class of a curve at p up to 2^40 (about 2^19..2^20 members)
in wall-clock hours on a few cores.  Three things change:

1.  Polynomial arithmetic over F_p is python-flint's `nmod_poly` (C), and
    rational ell-subgroups are read off as Frobenius EIGENSPACES of the
    ell-division polynomial: for each eigenvalue lambda of x^2 - t x + p
    mod ell, the kernel polynomial is gcd(psi_ell, D_lam (x^p - x) + N_lam)
    where x([lam]Q) = x - N_lam / D_lam.  One `pow_mod` and one gcd per
    eigenvalue, no modular polynomials, no Cantor-Zassenhaus.  The full
    factoring path of the reference engine remains the fallback for the
    scalar-Frobenius case (ell dividing the conductor).
2.  The class-number certificate is computed for 42-bit discriminants by a
    sieve over the values (B^2 - D)/4 of reduced binary quadratic forms,
    O(sqrt|D| log log |D|), then lifted to every suborder by the conductor
    formula.  It is cross-checked against the reference engine's brute
    form count at small |D| in the tests.
3.  Member expansion and measurement run in a multiprocessing pool with
    checkpoints, so a 2^40 class survives a session restart.

The per-codomain checks are unchanged: order N on random points, Phi_2 /
Phi_3 identities, and exact census equality at the end.  Nothing here
supports any crypto-scale claim.  Claim tier: toy.

    python3 tools/isogeny_dreg_search_fast.py --bits 40 --seed 7 --workers 4 \
        --out runs/demo40.json
    python3 tools/isogeny_dreg_search_fast.py --ladder 20,24,28,32,36,40 --seed 7 \
        --workers 4 --outdir analysis/isogeny-dreg-search/runs
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import isogeny_dreg_search as ref  # noqa: E402

try:
    import flint
    from flint import nmod_poly
    HAVE_FLINT = True
except ImportError:  # pragma: no cover
    HAVE_FLINT = False


# ---------------------------------------------------------------------------
# flint-backed division polynomials and eigenspace kernel polynomials
# ---------------------------------------------------------------------------


class DivPolyFlint:
    """f_n (n odd) / g_n (n even) as nmod_poly, same recursion as the reference."""

    def __init__(self, a, b, p):
        self.p = p
        self.a, self.b = a % p, b % p
        self.F = nmod_poly([b % p, a % p, 0, 1], p)
        self.F2 = self.F * self.F
        a2 = a * a % p
        self.cache = {
            0: nmod_poly([], p),
            1: nmod_poly([1], p),
            2: nmod_poly([1], p),
            3: nmod_poly([(-a2) % p, 12 * b % p, 6 * a % p, 0, 3], p),
            4: nmod_poly([(2 * (-8 * b * b - a * a * a)) % p, (2 * (-4 * a * b)) % p,
                          (2 * (-5 * a2)) % p, (2 * 20 * b) % p, (2 * 5 * a) % p, 0, 2], p),
        }

    def __call__(self, n):
        if n in self.cache:
            return self.cache[n]
        if n % 2 == 1:
            m = (n - 1) // 2
            if m % 2 == 1:
                val = self(m + 2) * self(m) ** 3 - 16 * self.F2 * self(m - 1) * self(m + 1) ** 3
            else:
                val = 16 * self.F2 * self(m + 2) * self(m) ** 3 - self(m - 1) * self(m + 1) ** 3
        else:
            m = n // 2
            val = self(m) * (self(m + 2) * self(m - 1) ** 2 - self(m - 2) * self(m + 1) ** 2)
        self.cache[n] = val
        return val


def eigenvalues_mod_ell(t, p, ell):
    return [lam for lam in range(1, ell) if (lam * lam - t * lam + p) % ell == 0]


def _to_list(f: "nmod_poly") -> list[int]:
    return ref._trim([int(c) for c in f.coeffs()])


def kernel_polynomials_fast(a, b, p, ell, t, rng):
    """Monic kernel polynomials of every rational cyclic ell-subgroup."""
    if ell == 2:
        cubic = nmod_poly([b % p, a % p, 0, 1], p)
        roots = sorted(int(r) for r, _ in cubic.roots())
        return [[(-r) % p, 1] for r in roots]
    n = (ell - 1) // 2
    dp = DivPolyFlint(a, b, p)
    psi = dp(ell)
    if psi.degree() != (ell * ell - 1) // 2:
        raise RuntimeError(f"psi_{ell} has wrong degree {psi.degree()}")
    psi = psi / int(psi.coeffs()[-1])
    x = nmod_poly([0, 1], p)
    xp = x.pow_mod(p, psi)
    out = {}
    need_full = False
    for lam in eigenvalues_mod_ell(t, p, ell):
        if lam % 2 == 1:
            N = 4 * dp.F * dp(lam - 1) * dp(lam + 1)
            D = dp(lam) ** 2
        else:
            N = dp(lam - 1) * dp(lam + 1)
            D = 4 * dp.F * dp(lam) ** 2
        g = psi.gcd((D * (xp - x) + N) % psi)
        if g.degree() == n:
            g = g / int(g.coeffs()[-1])
            out[tuple(_to_list(g))] = _to_list(g)
        elif g.degree() == psi.degree():
            need_full = True
        elif g.degree() != 0:
            need_full = True
    if need_full:
        # scalar Frobenius on E[ell] (ell | conductor): ell + 1 subgroups; use
        # the reference engine's full-factoring path (rare, slow, exact)
        return ref.rational_subgroups(a, b, p, ell, rng)
    return [list(k) for k in sorted(out)]


def count_roots_fast(coeffs, p):
    f = nmod_poly(coeffs, p)
    if f.degree() < 1:
        return 0
    x = nmod_poly([0, 1], p)
    g = f.gcd(x.pow_mod(p, f) - x)
    return g.degree()


def f3_fibre_roots_fast(a, b, p, k, samples, rng):
    total = 0
    mx = 0
    hist = {}
    for _ in range(samples):
        R = ref.random_point(a, b, p, rng)
        u1 = rng.randrange(1, p)
        g = ref.s3_fibre_poly(a, b, p, pow(u1, k, p), R[0])
        f = [0] * (2 * k + 1)
        for e, c in enumerate(g):
            f[e * k] = c
        f = ref._trim(f)
        r = count_roots_fast(f, p) if len(f) > 1 else 0
        total += r
        mx = max(mx, r)
        hist[r] = hist.get(r, 0) + 1
    return {"mean": total / samples, "max": mx, "histogram": dict(sorted(hist.items()))}


# ---------------------------------------------------------------------------
# Class-number certificate at 42-bit discriminants
# ---------------------------------------------------------------------------


def _primes_upto(n):
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if sieve[i]]


def class_number_sieve(D: int) -> int:
    """h(D) for a negative discriminant D (D = 0, 1 mod 4) by counting reduced
    primitive forms (A, B, C) with the values M(B) = (B^2 - D)/4 factored by a
    sieve over B.  Exact; O(sqrt|D| log log |D|) sieve plus divisor enumeration.
    """
    if D >= 0 or D % 4 not in (0, 1):
        raise ValueError("need a negative discriminant = 0,1 mod 4")
    Amax = math.isqrt(-D // 3) + 1
    par = (-D) % 2                     # B must have the parity of D
    Bs = list(range(par, Amax + 1, 2))  # B >= 0 only; B < 0 handled by symmetry
    nB = len(Bs)
    M = [(B * B - D) // 4 for B in Bs]
    Mmax = M[-1]
    plist = _primes_upto(math.isqrt(Mmax) + 1)
    factors = [[] for _ in range(nB)]
    rem = M[:]                          # cofactor after removing sieved primes
    for q in plist:
        # roots of B^2 = D (mod q); B runs over Bs = par + 2 i, so index i with
        # B = par + 2 i  ==>  i = (B - par)/2 mod q (2 invertible for odd q)
        if q == 2:
            idx_iter = range(nB)
            for i in idx_iter:
                while rem[i] % 2 == 0:
                    rem[i] //= 2
                    factors[i].append(2)
            continue
        Dq = D % q
        if Dq == 0:
            roots = [0]
        else:
            r = ref.sqrt_mod(Dq, q)
            if r is None:
                continue
            roots = [r, (q - r) % q] if r != 0 else [0]
        inv2 = pow(2, -1, q)
        for r in roots:
            i0 = ((r - par) * inv2) % q
            for i in range(i0, nB, q):
                while rem[i] % q == 0:
                    rem[i] //= q
                    factors[i].append(q)
    count = Fraction(0)
    for i, B in enumerate(Bs):
        m = M[i]
        if rem[i] > 1:
            factors[i].append(rem[i])   # leftover cofactor is prime
        # divisors of m from the prime multiset
        pf = {}
        for q in factors[i]:
            pf[q] = pf.get(q, 0) + 1
        divs = [1]
        for q, e in pf.items():
            divs = [d * q ** j for d in divs for j in range(e + 1)]
        lo = max(B, 1)
        smax = math.isqrt(m)
        for A in divs:
            if A < lo or A > smax:
                continue
            C = m // A
            if math.gcd(math.gcd(A, B), C) != 1:
                continue
            boundary = (A == C) or (B == A)
            if B == 0:
                w = Fraction(1, 2) if A == C else Fraction(1)
                count += w
            else:
                # B > 0 form, plus its mirror -B unless the mirror is excluded
                # (a reduced form with |B| = A or A = C requires B >= 0)
                if A == B == C:
                    count += Fraction(1, 3)
                else:
                    count += 1 if boundary else 2
    return count


def kronecker(D0, q):
    if q == 2:
        if D0 % 2 == 0:
            return 0
        return 1 if D0 % 8 in (1, 7) else -1
    return ref.legendre(D0, q)


def class_mass(p, t, brute_limit=1 << 24):
    """Sum over orders Z[pi] <= O <= O_K of the weighted class number: the
    number of F_p-isomorphism classes with trace t, each weighted 2/|Aut|.
    Equals H(4p - t^2)."""
    D = t * t - 4 * p
    D0, f = ref.fundamental_discriminant(D)
    if -D0 <= brute_limit:
        h0 = ref.class_number_weighted(D0)          # already weighted
        h0_unw = Fraction(1) if D0 in (-3, -4) else h0
    else:
        h0 = Fraction(class_number_sieve(D0))
        h0_unw = h0
    unit = 3 if D0 == -3 else (2 if D0 == -4 else 1)
    total = Fraction(0)
    for fp in range(1, f + 1):
        if f % fp:
            continue
        if fp == 1:
            total += h0
            continue
        h = h0_unw * fp / unit
        for q in set(_prime_factors(fp)):
            h *= Fraction(q - kronecker(D0, q), q)
        total += h
    return total, D, D0, f


def _prime_factors(n):
    out = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


# ---------------------------------------------------------------------------
# Parallel BFS + measurement
# ---------------------------------------------------------------------------

_CFG: dict = {}


def _init_worker(cfg):
    global _CFG
    _CFG = cfg


def _expand_and_measure(job):
    """job = (a, b, depth, primes_to_apply, measure_flag). Returns dict."""
    a, b, depth, primes, do_measure = job
    cfg = _CFG
    p, t, N = cfg["p"], cfg["t"], cfg["N"]
    rng = random.Random(f"{cfg['seed']}:w:{a}:{b}")
    j = ref.j_invariant(a, b, p)
    neighbours = []
    order_ok = 0
    mod_ok = 0
    for ell in primes:
        for h in kernel_polynomials_fast(a, b, p, ell, t, rng):
            a2, b2 = ref.velu_from_kernel_polynomial(a, b, p, h)
            if ref.is_singular(a2, b2, p):
                raise RuntimeError("Velu produced a singular curve")
            if not ref.verify_order(a2, b2, p, N, rng, samples=2):
                raise RuntimeError(f"codomain of {ell}-isogeny does not have order {N}")
            order_ok += 1
            if ell in ref.MODULAR:
                if ref.MODULAR[ell](j, ref.j_invariant(a2, b2, p), p) != 0:
                    raise RuntimeError(f"Phi_{ell}(j, j') != 0")
                mod_ok += 1
            neighbours.append((a2, b2, ell))
    out = {"a": a, "b": b, "j": j, "neighbours": neighbours,
           "order_ok": order_ok, "mod_ok": mod_ok}
    if do_measure:
        mrng = random.Random(f"{cfg['seed']}:member:{a}:{b}")
        out["F1_support"] = ref.f1_support(a, b, p)
        out["F3"] = f3_fibre_roots_fast(a, b, p, cfg["k"], cfg["samples"], mrng)
        if cfg["with_f2"] and cfg["h"]:
            R = ref.random_point(a, b, p, mrng)
            out["F2_dff"] = ref.f2_first_fall_degree(a, b, p, cfg["h"], R[0], cfg["D_max"])
    return out


def _has_rational_isogenies(D, ell, p):
    if ell == p:
        return False
    if D % ell == 0:
        return True
    return kronecker(D, ell) == 1


def search_fast(p, a, b, seed=7, k=4, h=None, samples=64, D_max=None, nulls=8,
                primes=ref.DEFAULT_PRIMES, with_f2=True, workers=4, batch=256,
                checkpoint=None, verbose=True, max_members=None):
    if not HAVE_FLINT:
        raise RuntimeError("python-flint is required for the fast engine (pip install python-flint)")
    t0 = time.time()
    a %= p
    b %= p
    rng = random.Random(seed)
    if h is None:
        h = ref.choose_subgroup_order(p)
    if D_max is None:
        D_max = (h or 0) + 8
    if ref.is_singular(a, b, p):
        raise ValueError("singular input curve")
    t = ref.trace_of(a, b, p, rng)
    if t % p == 0:
        raise ValueError("supersingular input curve: out of scope")
    N = p + 1 - t
    if not ref.verify_order(a, b, p, N, rng, samples=4):
        raise RuntimeError("input curve fails its own order check: trace computation is wrong")
    tc = time.time()
    predicted, D, D0, f = class_mass(p, t)
    t_census = time.time() - tc
    if verbose:
        print(f"p={p} t={t} N={N} D0={D0} f={f} predicted class mass {predicted} "
              f"(census {t_census:.1f}s)", file=sys.stderr)

    cfg = {"p": p, "t": t, "N": N, "seed": seed, "k": k, "h": h, "samples": samples,
           "D_max": D_max, "with_f2": with_f2}
    active = [ell for ell in primes if _has_rational_isogenies(D, ell, p)]

    members: dict = {}          # iso_key -> record
    explored: set = set()       # (iso_key, ell)
    order_ok = mod_ok = 0
    key0 = ref.iso_key(a, b, p)
    members[key0] = {"a": a, "b": b, "j": ref.j_invariant(a, b, p),
                     "aut": ref.aut_order(a, b, p), "depth": 0, "via": "input"}

    if checkpoint and os.path.exists(checkpoint):
        with open(checkpoint) as fh:
            ck = json.load(fh)
        if ck["p"] == p and ck["t"] == t and ck["seed"] == seed:
            members = {tuple(kk): vv for kk, vv in ck["members"]}
            explored = {(tuple(kk), ell) for kk, ell in ck["explored"]}
            order_ok, mod_ok = ck["order_ok"], ck["mod_ok"]
            if verbose:
                print(f"resumed {len(members)} members from checkpoint", file=sys.stderr)

    def observed():
        return sum(Fraction(2, m["aut"]) for m in members.values())

    def save_checkpoint():
        if not checkpoint:
            return
        tmp = checkpoint + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"p": p, "t": t, "seed": seed,
                       "members": [[list(kk), vv] for kk, vv in members.items()],
                       "explored": [[list(kk), ell] for kk, ell in explored],
                       "order_ok": order_ok, "mod_ok": mod_ok}, fh)
        os.replace(tmp, checkpoint)

    used = []
    # Generating set: every cheap active prime (ell <= 13, kernel polynomials
    # cost about a millisecond each) from the start, so the walk's diameter is
    # small and every pass keeps the pool busy; larger primes are admitted one
    # at a time only when the cheap ones reach a fixed point short of the census.
    cheap = [ell for ell in active if ell <= 13]
    stages = []
    if cheap:
        stages.append(cheap)
    for ell in active:
        if ell not in cheap:
            stages.append((stages[-1] if stages else []) + [ell])
    pending = set(members.keys())     # keys with an unexplored (key, ell) for the stage
    pool = Pool(workers, initializer=_init_worker, initargs=(cfg,))
    try:
        for gens_now in stages:
            pending = {kk for kk in members if any((kk, ell) not in explored for ell in gens_now)
                       or "F3" not in members[kk]}
            for ell in gens_now:
                if ell not in used:
                    used.append(ell)
            n_pass = 0
            while observed() != predicted and pending:
                jobs = []
                for key in pending:
                    m = members[key]
                    todo = [ell for ell in gens_now if (key, ell) not in explored]
                    jobs.append((m["a"], m["b"], m["depth"], todo, "F3" not in m))
                pending = set()
                added = 0
                done = 0
                for res in pool.imap_unordered(_expand_and_measure, jobs, chunksize=max(1, min(batch, len(jobs) // (4 * workers) + 1))):
                    key = ref.iso_key(res["a"], res["b"], p)
                    m = members[key]
                    for ell in gens_now:
                        explored.add((key, ell))
                    order_ok += res["order_ok"]
                    mod_ok += res["mod_ok"]
                    if "F3" in res:
                        m["F1_support"] = res["F1_support"]
                        m["F3"] = res["F3"]
                        if "F2_dff" in res:
                            m["F2_dff"] = res["F2_dff"]
                    for (a2, b2, ell) in res["neighbours"]:
                        k2 = ref.iso_key(a2, b2, p)
                        if k2 not in members:
                            members[k2] = {"a": a2, "b": b2, "j": ref.j_invariant(a2, b2, p),
                                           "aut": ref.aut_order(a2, b2, p),
                                           "depth": m["depth"] + 1, "via": f"ell={ell} from j={m['j']}"}
                            pending.add(k2)
                            added += 1
                    done += 1
                    if verbose and done % 20000 == 0:
                        print(f"  stage {gens_now}: {done}/{len(jobs)} jobs, {len(members)} members, "
                              f"{time.time() - t0:.0f}s", file=sys.stderr)
                    if max_members and len(members) >= max_members:
                        break
                n_pass += 1
                if n_pass % 25 == 0 or added == 0 or len(jobs) >= 20000:
                    save_checkpoint()
                if verbose and (n_pass % 10 == 0 or added == 0 or len(jobs) >= 5000):
                    print(f"  stage {gens_now} pass {n_pass}: {len(jobs)} jobs +{added} -> {len(members)} members, "
                          f"weighted {observed()} / {predicted}, {time.time() - t0:.0f}s", file=sys.stderr)
                if observed() > predicted:
                    raise RuntimeError("enumeration exceeds the class mass: key or Velu bug")
                if max_members and len(members) >= max_members:
                    break
            if observed() == predicted or (max_members and len(members) >= max_members):
                break
        # measure anything still unmeasured (found in the final pass)
        jobs = [(m["a"], m["b"], m["depth"], [], True) for m in members.values() if "F3" not in m]
        for res in pool.imap_unordered(_expand_and_measure, jobs, chunksize=max(1, batch // 8)):
            m = members[ref.iso_key(res["a"], res["b"], p)]
            m["F1_support"] = res["F1_support"]
            m["F3"] = res["F3"]
            if "F2_dff" in res:
                m["F2_dff"] = res["F2_dff"]
        save_checkpoint()
        t_enum = time.time() - t0
        # null set
        null_rows = []
        null_jobs = []
        for _ in range(nulls):
            na, nb, nt = ref.random_curve_with_other_trace(p, t, rng, 1 << 17)
            null_jobs.append((na, nb, nt))
        cfg_null = dict(cfg)
        res_list = []
        for (na, nb, nt) in null_jobs:
            # measured in-process with the same code path as members
            _init_worker(cfg_null)
            r = _expand_and_measure((na, nb, 0, [], True))
            r["trace"] = nt
            res_list.append(r)
        for r in res_list:
            row = {"a": r["a"], "b": r["b"], "trace": r["trace"], "j": r["j"],
                   "F1_support": r["F1_support"], "F3": r["F3"]}
            if "F2_dff" in r:
                row["F2_dff"] = r["F2_dff"]
            null_rows.append(row)
    finally:
        pool.close()
        pool.join()

    obs = observed()
    certified = (obs == predicted)
    rows = [{"a": m["a"], "b": m["b"], "j": m["j"], "aut": m["aut"], "depth": m["depth"],
             "via": m["via"], "F1_support": m["F1_support"], "F3": m["F3"],
             **({"F2_dff": m["F2_dff"]} if "F2_dff" in m else {})}
            for m in members.values()]
    report = _summarize(p, a, b, seed, k, h, samples, D_max, nulls, used, with_f2, rows, null_rows,
                        certified, obs, predicted, D, D0, f, t, N, order_ok, mod_ok,
                        t_enum, time.time() - t0, t_census, workers)
    return report


def _band(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5
    return {"min": min(vals), "max": max(vals), "mean": mu, "sd": sd, "n": len(vals)}


def _summarize(p, a, b, seed, k, h, samples, D_max, nulls, used, with_f2, rows, null_rows,
               certified, obs, predicted, D, D0, f, t, N, order_ok, mod_ok, t_enum, t_total,
               t_census, workers):
    f3_null = _band([r["F3"]["mean"] for r in null_rows])
    n_tot = sum(sum(r["F3"]["histogram"].values()) for r in null_rows) or 1
    mean_tot = sum(int(v) * c for r in null_rows for v, c in r["F3"]["histogram"].items()) / n_tot
    var_tot = sum((int(v) - mean_tot) ** 2 * c for r in null_rows
                  for v, c in r["F3"]["histogram"].items()) / max(1, n_tot - 1)
    se = (max(var_tot, float(k)) / samples) ** 0.5
    thresh = 4 * max(se, f3_null["sd"] if f3_null and f3_null["sd"] else se)
    null_dff = {x.get("F2_dff") for x in null_rows}
    survivors = []
    f3_hist = {}
    f2_hist = {}
    for r in rows:
        flags = []
        if r["F1_support"] != 13:
            flags.append(f"F1 support {r['F1_support']} != 13")
        if f3_null and abs(r["F3"]["mean"] - f3_null["mean"]) > thresh:
            flags.append(f"F3 mean {r['F3']['mean']:.3f} outside null band "
                         f"{f3_null['mean']:.3f}+-{thresh:.3f}")
        if with_f2 and h and r.get("F2_dff") not in null_dff:
            flags.append(f"F2 d_ff {r.get('F2_dff')} not in null set {sorted(x for x in null_dff if x is not None)}")
        if flags:
            survivors.append({"j": r["j"], "a": r["a"], "b": r["b"], "flags": flags})
        key = f"{r['F3']['mean']:.4f}"
        f3_hist[key] = f3_hist.get(key, 0) + 1
        k2 = str(r.get("F2_dff"))
        f2_hist[k2] = f2_hist.get(k2, 0) + 1
    # Bonferroni-style expected number of members outside +-thresh under the
    # null (Gaussian approx on per-curve means), for the reader's calibration
    z = thresh / se if se else float("inf")
    expected_false = len(rows) * math.erfc(z / math.sqrt(2))
    return {
        "instrument": "tools/isogeny_dreg_search_fast.py",
        "engine": "flint",
        "claim_tier": "toy",
        "input": {"p": p, "a": a, "b": b, "seed": seed, "k": k, "h": h, "samples": samples,
                  "D_max": D_max, "nulls": nulls, "primes_used": used, "with_f2": with_f2,
                  "workers": workers},
        "class": {"p": p, "trace": t, "order": N, "discriminant": D,
                  "fundamental_discriminant": D0, "conductor": f,
                  "observed_weighted": str(obs), "predicted_weighted": str(predicted),
                  "coverage_fraction": float(obs / predicted) if predicted else 0.0,
                  "order_checks_passed": order_ok, "modular_checks_passed": mod_ok},
        "class_size": len(rows),
        "exhaustive": certified,
        "exhaustive_note": ("every F_p-isomorphism class with this trace was reached and the "
                            "weighted count equals H(4p - t^2)" if certified else
                            f"NOT exhaustive: coverage {float(obs / predicted):.6f}"),
        "summary": {
            "F1_support": _band([r["F1_support"] for r in rows]),
            "F1_support_null": _band([r["F1_support"] for r in null_rows]),
            "F2_dff": _band([r.get("F2_dff") for r in rows]) if with_f2 else None,
            "F2_dff_null": _band([r.get("F2_dff") for r in null_rows]) if with_f2 else None,
            "F2_dff_histogram": f2_hist,
            "F3_mean": _band([r["F3"]["mean"] for r in rows]),
            "F3_mean_null": f3_null,
            "F3_mean_histogram": f3_hist,
            "F3_max_over_class": max(r["F3"]["max"] for r in rows),
            "F3_max_over_null": max(r["F3"]["max"] for r in null_rows) if null_rows else None,
            "F3_flag_threshold": thresh,
            "F3_null_per_sample_variance": var_tot,
            "F3_expected_false_flags_under_null": expected_false,
            "depth_max": max(r["depth"] for r in rows),
        },
        "survivors": survivors,
        "null": null_rows,
        "members": rows,
        "timing_seconds": {"census": t_census, "enumeration_and_measurement": t_enum,
                           "total": t_total},
    }


# ---------------------------------------------------------------------------
# CLI and ladder
# ---------------------------------------------------------------------------


def random_prime(bits, rng):
    while True:
        p = rng.randrange(2 ** (bits - 1), 2 ** bits) | 1
        if p > 3 and _is_probable_prime(p) and _is_prime_exact(p):
            return p


def _is_probable_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a_ in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a_, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _is_prime_exact(n):
    # deterministic for n < 3.3e24 with the bases above; belt and braces
    return _is_probable_prime(n)


def random_generic_curve(bits, seed):
    rng = random.Random(f"ladder:{bits}:{seed}")
    p = random_prime(bits, rng)
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if not ref.is_singular(a, b, p):
            return p, a, b


def write_report(report, path, keep_members=True):
    slim = dict(report)
    if not keep_members:
        slim["members_omitted"] = len(report["members"])
        slim.pop("members")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(slim, fh, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--p", type=int)
    ap.add_argument("--a", type=int)
    ap.add_argument("--b", type=int)
    ap.add_argument("--bits", type=int)
    ap.add_argument("--ladder", help="comma-separated bit sizes, one random generic curve each")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--h", type=int)
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--nulls", type=int, default=8)
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    ap.add_argument("--no-f2", action="store_true")
    ap.add_argument("--max-members", type=int)
    ap.add_argument("--members-limit", type=int, default=100000,
                    help="omit the per-member table from the JSON above this class size")
    ap.add_argument("--out")
    ap.add_argument("--outdir", default="analysis/isogeny-dreg-search/runs")
    ap.add_argument("--checkpoint-dir")
    args = ap.parse_args(argv)

    if args.ladder:
        sizes = [int(x) for x in args.ladder.split(",")]
        for bits in sizes:
            p, a, b = random_generic_curve(bits, args.seed)
            out = Path(args.outdir) / f"ladder-{bits:02d}bit-seed{args.seed}.json"
            ck = (Path(args.checkpoint_dir) / f"ckpt-{bits}-{args.seed}.json") if args.checkpoint_dir else None
            print(f"=== {bits} bits: p={p} a={a} b={b} ===", file=sys.stderr)
            rep = search_fast(p, a, b, seed=args.seed, k=args.k, h=args.h, samples=args.samples,
                              nulls=args.nulls, with_f2=not args.no_f2, workers=args.workers,
                              checkpoint=str(ck) if ck else None, max_members=args.max_members)
            write_report(rep, out, keep_members=rep["class_size"] <= args.members_limit)
            if rep["class_size"] > args.members_limit and args.checkpoint_dir:
                full = Path(args.checkpoint_dir) / f"members-{bits}-{args.seed}.json"
                with open(full, "w") as fh:
                    json.dump(rep["members"], fh)
            s = rep["summary"]
            print(f"{bits} bits: class_size={rep['class_size']} exhaustive={rep['exhaustive']} "
                  f"survivors={len(rep['survivors'])} F2={s['F2_dff_histogram']} "
                  f"F3 class {s['F3_mean']['mean']:.3f}+-{s['F3_mean']['sd']:.3f} "
                  f"null {s['F3_mean_null']['mean']:.3f} thr {s['F3_flag_threshold']:.3f} "
                  f"total {rep['timing_seconds']['total']:.0f}s -> {out}")
        return 0

    if args.bits:
        p, a, b = random_generic_curve(args.bits, args.seed)
    else:
        p, a, b = args.p, args.a, args.b
        if p is None or a is None or b is None:
            ap.error("give --p --a --b, --bits, or --ladder")
    ck = (Path(args.checkpoint_dir) / f"ckpt-{p}-{args.seed}.json") if args.checkpoint_dir else None
    rep = search_fast(p, a, b, seed=args.seed, k=args.k, h=args.h, samples=args.samples,
                      nulls=args.nulls, with_f2=not args.no_f2, workers=args.workers,
                      checkpoint=str(ck) if ck else None, max_members=args.max_members)
    if args.out:
        write_report(rep, args.out, keep_members=rep["class_size"] <= args.members_limit)
        s = rep["summary"]
        print(f"p={p} class_size={rep['class_size']} exhaustive={rep['exhaustive']} "
              f"survivors={len(rep['survivors'])} F2={s['F2_dff_histogram']} "
              f"F3 class {s['F3_mean']['mean']:.3f}+-{s['F3_mean']['sd']:.3f} null "
              f"{s['F3_mean_null']['mean']:.3f} thr {s['F3_flag_threshold']:.3f} "
              f"total {rep['timing_seconds']['total']:.0f}s -> {args.out}")
    else:
        rep.pop("members")
        print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
