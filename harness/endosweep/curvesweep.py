"""Cross-curve chain sweep: ``chainsweep``'s catalogue and operation model on every curve.

``chainsweep.py`` did one curve (GOST CryptoPro-B) exhaustively and froze the
result for a native measurement.  This module runs the same pipeline on every
verified curve with a small CM discriminant, with what changes from curve to
curve made explicit:

* **the curve's own arithmetic.**  The scalar multiplications are counted with
  the doubling formula the curve admits (``a = 0``: dbl-2009-l 2M + 5S;
  ``a = -3``, or a model isomorphic to one: dbl-2001-b 3M + 5S; otherwise
  dbl-2007-bl 1M + 8S plus a multiplication by ``a``), the same addition
  formulas (add-2007-bl 11M + 5S, madd-2007-bl 7M + 4S) and a Fermat
  inversion priced for the curve's own prime.  Curves defined in Edwards or
  Montgomery form are counted on their short Weierstrass model, and the
  report says so;
* **degree-2 steps.**  When 2 splits or ramifies the catalogue contains
  2-isogenies (Bandersnatch's ``sqrt(-2)`` is one); a 2-step is counted with
  Velu's formula in Jacobian coordinates, ``X' = (X d + v Z^4) d``,
  ``Y' = Y (d^2 - v Z^4) d``, ``Z' = Z d`` with ``d = X - x_0 Z^2``: 7M + 3S,
  4M + 1S on an affine input.  The odd steps are ``chainsweep``'s counts,
  which mirror the crypto repository's evaluators;
* **automorphisms.**  ``D = -3`` and ``D = -4`` curves have the unit
  ``zeta_3`` or ``i``, one multiplication; no chain can beat it and none is
  built.  The unit's action is verified on a point;
* **completeness per curve.**  The catalogue bounds (largest norm, largest
  step) grow until the lower bound on every chain outside them exceeds the
  export factor times the cheapest chain, so each curve's catalogue provably
  contains every chain within that factor of its cheapest;
* **construction.**  Every ordering within the factor is built on the curve
  by ``explicit.build_chain_endomorphism`` (pinned omega eigenvalue, the
  element itself) and verified on points with a GLV-2 reconstruction.

Operation counts, not timings; the odd-step and table counts were confirmed
exactly by the crypto repository's counting build on CryptoPro-B
(aburan28/crypto#1423), the rest follows the same formulas.

    python -m harness.endosweep.curvesweep --std-curves STD_CURVES_CHECKOUT \\
        --extra research/endosweep_curves_20261006 --out-dir research/endosweep_curves_20261006
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import time
from dataclasses import asdict, dataclass, field

from . import chainsweep as CS
from . import explicit as EX
from . import lattice as LA
from . import quadorder as QO
from .targets import Target, verify, weierstrass_target
from .toyverify import Curve

VARIANTS = CS.VARIANTS


# ---------------------------------------------------------------------------
# per-curve arithmetic
# ---------------------------------------------------------------------------

@dataclass
class Arith:
    dbl: tuple[int, int]
    add: tuple[int, int] = (11, 5)
    madd: tuple[int, int] = (7, 4)
    inv: tuple[int, int] = (8, 256)
    note: str = ""


def _is_fourth_power(x: int, p: int) -> bool:
    x %= p
    if x == 0:
        return False
    from math import gcd
    return pow(x, (p - 1) // gcd(4, p - 1), p) == 1


def arithmetic(p: int, a: int) -> Arith:
    """Jacobian doubling for y^2 = x^3 + a x + b over F_p, and a Fermat inversion."""
    a %= p
    inv = (bin(p - 2).count("1"), (p - 2).bit_length())
    if a == 0:
        return Arith((2, 5), inv=inv, note="a = 0: dbl-2009-l 2M + 5S")
    if a == p - 3:
        return Arith((3, 5), inv=inv, note="a = -3: dbl-2001-b 3M + 5S")
    if _is_fourth_power(-3 * pow(a, -1, p), p):
        return Arith((3, 5), inv=inv, note="isomorphic to an a = -3 model (-3/a is a fourth power): 3M + 5S")
    if min(a, p - a) <= 16:
        return Arith((1, 8), inv=inv, note=f"small a = {a if a < p // 2 else a - p}: dbl-2007-bl 1M + 8S")
    return Arith((2, 8), inv=inv, note="general a: dbl-2007-bl 1M + 8S + 1M for a")


# ---------------------------------------------------------------------------
# chain counts (odd steps from chainsweep, 2-steps and units here)
# ---------------------------------------------------------------------------

def step_ops(ell: int, variant: str, first: bool) -> tuple[int, int]:
    if ell == 2:
        return (4, 1) if first else (7, 3)
    return CS.step_ops(ell, variant, first)


def chain_ops(order, variant: str) -> dict:
    if not order:                      # a unit: x -> beta x (or y -> i y)
        return {"M": 1, "S": 0, "I": 0, "M_eq": 1}
    M = S = 0
    for i, ell in enumerate(order):
        m, s = step_ops(ell, variant, i == 0)
        M, S = M + m, S + s
    m, s = CS.tail_ops(variant)
    return {"M": M + m, "S": S + s, "I": 0, "M_eq": M + m + S + s}


def distinct_orders(steps) -> list[tuple[int, ...]]:
    """Distinct orderings of a multiset of steps, without enumerating n! permutations."""
    from sympy.utilities.iterables import multiset_permutations
    return sorted(tuple(o) for o in multiset_permutations(sorted(steps)))


def best_order(steps, variant: str):
    """The cheapest ordering, in closed form: only the first step's position
    matters (it alone sees the affine input), so the prime with the largest
    first-step saving goes first and the rest follow in ascending order."""
    steps = sorted(steps)
    if not steps:
        return (), chain_ops((), variant)

    def saving(ell):
        return sum(step_ops(ell, variant, False)) - sum(step_ops(ell, variant, True))

    first = max(sorted(set(steps)), key=lambda ell: (saving(ell), -ell))
    rest = list(steps)
    rest.remove(first)
    o = tuple([first] + rest)
    return o, chain_ops(o, variant)


def admissible_primes(D: int, upto: int) -> list[int]:
    return [q for q in range(2, upto + 1) if CS.split_or_ramified(D, q)]


def ramified(D: int, ell: int) -> bool:
    return QO.kronecker_symbol_disc(D, ell) == 0


def outside_lower_bound(D: int, nmax: int, lmax: int, variant: str) -> dict:
    """``chainsweep.outside_lower_bound`` with 2-steps admitted and ramified
    primes at most once.

    The norm of a primitive element is a product of split primes (any power,
    from a power of one prime ideal) and ramified primes to the first power
    (a ramified prime ideal squared is the rational prime, which a primitive
    element does not contain); inert primes never occur.  The search ranges
    over every such multiset, principal or not, so it is still a lower bound.
    """
    ell = lmax + 1
    while not CS.split_or_ramified(D, ell):
        ell += 1
    first, later = step_ops(ell, variant, True), step_ops(ell, variant, False)
    tail = CS.tail_ops(variant)
    bound_i = min(sum(first), sum(later)) + sum(tail)
    primes = admissible_primes(D, lmax)
    best = [None]

    def dfs(start, ms, prod):
        if ms:
            c = chain_ops(best_order(ms, variant)[0], variant)["M_eq"]
            if best[0] is not None and c >= best[0][0]:
                return
            if prod > nmax:
                best[0] = (c, list(ms))
                return
        for i in range(start, len(primes)):
            q = primes[i]
            if ms and ms[-1] == q and ramified(D, q):
                continue
            dfs(i, ms + [q], prod * q)

    dfs(0, [], 1)
    bound_ii, witness = best[0]
    return {"variant": variant, "large_step": {"ell": ell, "bound": bound_i},
            "large_norm": {"bound": bound_ii, "cheapest_multiset": witness},
            "bound": min(bound_i, bound_ii)}


def _spf_sieve(nmax: int) -> list[int]:
    spf = list(range(nmax + 1))
    i = 2
    while i * i <= nmax:
        if spf[i] == i:
            for j in range(i * i, nmax + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    return spf


def catalogue(D: int, nmax: int, lmax: int) -> list[dict]:
    """Every primitive non-scalar element with norm <= nmax and prime factors <= lmax."""
    spf = _spf_sieve(nmax)
    adm = set(admissible_primes(D, lmax))
    out = []
    for N in range(2, nmax + 1):
        steps, m = [], N
        while m > 1:
            q = spf[m]
            if q not in adm:
                break
            steps.append(q)
            m //= q
        if m > 1:
            continue
        for el in QO.elements_of_norm(D, N):
            out.append({"a": el.a, "b": el.b, "norm": N, "steps": sorted(steps)})
    return out


def multiset_orderings(steps) -> int:
    from collections import Counter
    from math import factorial
    c = Counter(steps)
    r = factorial(len(steps))
    for v in c.values():
        r //= factorial(v)
    return r


def cost_bounded_multisets(D: int, limit: float, variant: str = "optimised") -> list[tuple[int, ...]]:
    """Every realizable multiset of step degrees whose cheapest chain costs <= limit.

    Realizable: split primes with any multiplicity, ramified primes at most
    once (the norms of primitive elements).  Adding a step never lowers the
    cheapest cost (every step costs something in any position), so a
    depth-first search over non-decreasing primes, pruned at ``limit``, is
    exhaustive.  A prime can occur only if its cheapest single step (affine
    first step plus the tail) fits under ``limit``.
    """
    tail = sum(CS.tail_ops(variant))
    ell_max = 3                          # odd step costs grow with ell: stop at the first that cannot fit
    while sum(step_ops(ell_max + 2, variant, True)) + tail <= limit:
        ell_max += 2
    primes = [q for q in admissible_primes(D, ell_max)
              if sum(step_ops(q, variant, True)) + tail <= limit]
    out: list[tuple[int, ...]] = []

    def dfs(start, ms):
        if ms:
            if chain_ops(best_order(ms, variant)[0], variant)["M_eq"] > limit:
                return
            out.append(tuple(ms))
        for i in range(start, len(primes)):
            q = primes[i]
            if ms and ms[-1] == q and ramified(D, q):
                continue
            dfs(i, ms + [q])

    dfs(0, [])
    return out


def complete_catalogue(D: int, factor: float, nmax0: int = 20000, lmax0: int = 61,
                       seed_cap: int = 4_000_000) -> dict:
    """Every element whose cheapest chain costs at most ``factor`` x the cheapest.

    A norm-bounded seed catalogue gives a first cheapest cost c0; then every
    realizable step multiset of cost <= factor * c0 is enumerated
    (:func:`cost_bounded_multisets`) and each product N is tested for
    primitive elements of norm N.  The result contains every chain within
    ``factor`` of the true cheapest (which is <= c0); nothing is truncated by
    a norm or step bound.
    """
    nmax, lmax = max(nmax0, 8 * QO.min_nonscalar_degree(D)), lmax0
    while True:
        seed = catalogue(D, nmax, lmax)
        if seed or nmax >= seed_cap:
            break
        nmax, lmax = min(nmax * 4, seed_cap), lmax * 2
    if not seed:
        return {"catalogue": [], "nmax": nmax, "lmax": lmax, "best": None, "limit": None, "complete": False,
                "multisets": 0, "seed_best": None}
    c0 = min(best_order(e["steps"], "optimised")[1]["M_eq"] for e in seed)
    limit = factor * c0
    multisets = cost_bounded_multisets(D, limit)
    cat = []
    for ms in multisets:
        N = 1
        for q in ms:
            N *= q
        for el in QO.elements_of_norm(D, N):
            cat.append({"a": el.a, "b": el.b, "norm": N, "steps": list(ms)})
    best = min((best_order(e["steps"], "optimised")[1]["M_eq"] for e in cat), default=None)
    return {"catalogue": cat, "nmax": max((e["norm"] for e in cat), default=0),
            "lmax": max((max(e["steps"]) for e in cat), default=0), "best": best, "limit": limit,
            "seed_best": c0, "complete": True, "multisets": len(multisets)}


# ---------------------------------------------------------------------------
# scalar multiplication with the curve's arithmetic (chainsweep's recoding)
# ---------------------------------------------------------------------------

def _batch(ar: Arith, n: int) -> tuple[int, int]:
    return n + ar.inv[0] + 2 * (n - 1) + 3 * n, ar.inv[1] + n


def _table(ar: Arith, w: int) -> tuple[int, int]:
    c = 1 << (w - 2)
    if c == 1:
        return 0, 0
    return ar.dbl[0] + (c - 1) * ar.add[0], ar.dbl[1] + (c - 1) * ar.add[1]


def baseline_ops(ar: Arith, k: int, w: int, table: str) -> tuple[int, int]:
    d = CS.wnaf_digits(k, w)
    nz = sum(1 for x in d if x)
    M, S = _table(ar, w)
    if table == "affine":
        bm, bs = _batch(ar, 1 << (w - 2))
        M, S, add = M + bm, S + bs, ar.madd
    else:
        add = ar.add
    return (M + (len(d) - 1) * ar.dbl[0] + (nz - 1) * add[0],
            S + (len(d) - 1) * ar.dbl[1] + (nz - 1) * add[1])


def glv_ops(ar: Arith, k1: int, k2: int, w: int, table: str, chain: dict) -> tuple[int, int]:
    d1, d2 = CS.wnaf_digits(abs(k1), w), CS.wnaf_digits(abs(k2), w)
    L = max(len(d1), len(d2))
    nz = sum(1 for x in d1 if x) + sum(1 for x in d2 if x)
    tm, ts = _table(ar, w)
    M, S = 2 * tm + chain["M"], 2 * ts + chain["S"]
    if table == "affine":
        bm, bs = _batch(ar, 2 * (1 << (w - 2)))
        M, S, add = M + bm, S + bs, ar.madd
    else:
        add = ar.add
    return M + (L - 1) * ar.dbl[0] + (nz - 1) * add[0], S + (L - 1) * ar.dbl[1] + (nz - 1) * add[1]


def scalar_model(ar: Arith, n: int, lam: int, chain: dict, *, widths=(3, 4, 5, 6, 7),
                 samples: int = 200, seed: int = 7) -> dict:
    rng = random.Random(seed)
    ks = [rng.randrange(1, n) for _ in range(samples)]
    red = LA.reduce([1, lam], n)
    halves = [red.decompose(k) for k in ks]
    base, glv = {}, {}
    for table in ("affine", "jacobian"):
        for w in widths:
            base[f"{table}/w{w}"] = statistics.fmean(sum(baseline_ops(ar, k, w, table)) for k in ks)
            glv[f"{table}/w{w}"] = statistics.fmean(sum(glv_ops(ar, k1, k2, w, table, chain)) for k1, k2 in halves)
    bb = min(base, key=base.get)
    bg = min(glv, key=glv.get)
    return {"baseline": {k: round(v, 1) for k, v in base.items()}, "glv": {k: round(v, 1) for k, v in glv.items()},
            "best_baseline": bb, "best_glv": bg, "ratio": round(base[bb] / glv[bg], 4),
            "coeff_bits_babai": red.babai_bound.bit_length()}


# ---------------------------------------------------------------------------
# one curve
# ---------------------------------------------------------------------------

@dataclass
class CurveResult:
    name: str
    source: str
    p_bits: int
    n_bits: int
    model: str
    D: int
    class_number: int
    arithmetic: str = ""
    kind: str = ""                      # "automorphism" | "chain" | "none"
    catalogue_elements: int = 0
    catalogue_orders: int = 0
    nmax: int = 0
    lmax: int = 0
    complete: bool = False
    outside_bound: int | None = None
    best_element: list[int] | None = None
    best_order: list[int] | None = None
    best_chain_M_eq: dict = field(default_factory=dict)
    within_factor: int = 0
    built: int = 0
    verified: int = 0
    eigenvalues_consistent: bool | None = None
    best_verified: bool = False
    model_ops: dict = field(default_factory=dict)
    rows: list[dict] = field(default_factory=list)
    note: str = ""
    elapsed_s: float = 0.0


def verify_automorphism(Tw: Target, D: int) -> tuple[bool, int, str]:
    """The unit of Z[zeta_3] or Z[i] acts on a point of order n as a predicted scalar."""
    p, n, h = Tw.p, Tw.n, Tw.h
    a, b = Tw.coeffs["a"] % p, Tw.coeffs["b"] % p
    E = Curve(p, a, b)
    P = EX.point_of_order(E, n, h, 2)
    from sympy.ntheory import sqrt_mod
    if D == -3:
        if a != 0:
            return False, 0, "D = -3 but a != 0 on this model"
        s = sqrt_mod(-3 % p, p)
        beta = (-1 + s) * pow(2, -1, p) % p                 # a primitive cube root of unity
        img = (beta * P[0] % p, P[1])
        r = sqrt_mod(-3 % n, n)
        cands = [(-1 + r) * pow(2, -1, n) % n, (-1 - r) * pow(2, -1, n) % n]
        what = "(x, y) -> (beta x, y), beta^3 = 1"
    elif D == -4:
        if b != 0:
            return False, 0, "D = -4 but b != 0 on this model"
        i = sqrt_mod(-1 % p, p)
        img = ((-P[0]) % p, i * P[1] % p)
        r = sqrt_mod(-1 % n, n)
        cands = [r, n - r]
        what = "(x, y) -> (-x, i y), i^2 = -1"
    else:
        return False, 0, "not a unit discriminant"
    for lam in cands:
        if E.mul(lam, P) == img:
            return True, lam, what
    return False, 0, what + ": no eigenvalue matched"


def sweep_curve(T: Target, D: int, *, source: str, factor: float = 2.0, build: bool = True,
                build_limit: int = 60, build_seconds: float = 900.0, seed: int = 20261006,
                progress=None) -> CurveResult:
    t0 = time.time()
    Tw = weierstrass_target(T)
    if Tw.verified is None:
        verify(Tw)
    if not Tw.verified:
        raise RuntimeError(f"{T.name}: the short Weierstrass model does not verify: {Tw.verification}")
    p, n, h = Tw.p, Tw.n, Tw.h
    a, b = Tw.coeffs["a"] % p, Tw.coeffs["b"] % p
    ar = arithmetic(p, a)
    res = CurveResult(T.name, source, p.bit_length(), n.bit_length(), T.model, D,
                      CS.class_number(D), arithmetic=ar.note
                      + ("" if T.model == "weierstrass" else f" (counted on the short Weierstrass model of this {T.model} curve)"))
    if D in (-3, -4):
        ok, lam, what = verify_automorphism(Tw, D)
        res.kind = "automorphism"
        res.best_chain_M_eq = {"optimised": 1, "generic": 1}
        res.best_verified = ok
        res.verified = int(ok)
        res.note = what
        if ok:
            res.model_ops = scalar_model(ar, n, lam, chain_ops((), "optimised"))
        res.elapsed_s = round(time.time() - t0, 2)
        return res
    res.kind = "chain"
    cc = complete_catalogue(D, factor)
    cat = cc["catalogue"]
    res.catalogue_elements = len(cat)
    res.nmax, res.lmax, res.complete = cc["nmax"], cc["lmax"], cc["complete"]
    res.outside_bound = cc["limit"]
    if not cat:
        res.kind, res.note = "none", "no element with a smooth norm found"
        res.elapsed_s = round(time.time() - t0, 2)
        return res
    rows = []
    for el in cat:
        order, _ = best_order(el["steps"], "optimised")
        rows.append({"element": [el["a"], el["b"]], "norm": el["norm"], "steps": el["steps"],
                     "order": list(order), "orderings": multiset_orderings(el["steps"]),
                     "ops": {"optimised": chain_ops(order, "optimised"),
                             "generic": chain_ops(tuple(el["steps"]), "generic")}})
    res.catalogue_orders = sum(r["orderings"] for r in rows)
    best = min(r["ops"]["optimised"]["M_eq"] for r in rows)
    chosen = sorted((r for r in rows if r["ops"]["optimised"]["M_eq"] <= factor * best),
                    key=lambda r: (r["ops"]["optimised"]["M_eq"], r["norm"], r["order"]))
    res.within_factor = len(chosen)
    bestrow = chosen[0]
    res.best_element, res.best_order = bestrow["element"], bestrow["order"]
    res.best_chain_M_eq = {v: bestrow["ops"][v]["M_eq"] for v in VARIANTS}
    root = QO.omega_eigenvalues(D, n)[0]
    eig: dict[tuple, set] = {}
    lam_best = None
    if build:
        import signal

        def _alarm(signum, frame):
            raise TimeoutError(f"construction exceeded its {build_seconds} s budget")

        for r in chosen[:build_limit]:
            t1 = time.time()
            old_handler = signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(int(build_seconds))
            try:
                cr = EX.build_chain_endomorphism(p, a, b, n, h, D, tuple(r["element"]), curve_name=T.name,
                                                 steps=r["order"], conjugates=False, omega_root=root)
                r["found"] = cr.found
                r["note"] = cr.note
                if cr.found:
                    r["eigenvalue"] = hex(cr.eigenvalue)
                    r["glv_check"] = cr.glv_check
                    eig.setdefault(tuple(r["element"]), set()).add(min(cr.eigenvalue, n - cr.eigenvalue))
                    if r is bestrow:
                        lam_best = cr.eigenvalue
            except Exception as e:  # noqa: BLE001 - recorded, never dropped
                r["found"] = False
                r["note"] = f"build raised {type(e).__name__}: {e}"
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            r["build_seconds"] = round(time.time() - t1, 2)
            res.built += 1
            res.verified += int(bool(r.get("found")))
            if progress:
                progress(T.name, r)
        res.eigenvalues_consistent = all(len(v) == 1 for v in eig.values())
        res.best_verified = bool(bestrow.get("found"))
    if lam_best is not None:
        res.model_ops = scalar_model(ar, n, lam_best, bestrow["ops"]["optimised"])
    res.rows = chosen
    res.elapsed_s = round(time.time() - t0, 2)
    return res


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def _scan(T: Target, disc_bound: int):
    verify(T)
    if not T.verified:
        return None, T.verification
    Dfrob = QO.frobenius_discriminant(T.q, T.trace)
    if Dfrob >= 0:
        return None, "not ordinary"
    scan = QO.small_discriminant_scan(Dfrob, disc_bound)
    return scan.found, scan.certificate


def _key(T: Target) -> tuple:
    W = weierstrass_target(T)
    p = W.p
    # the j-invariant and the group order identify the curve up to twist and isomorphism
    a, b = W.coeffs["a"] % p, W.coeffs["b"] % p
    den = (4 * pow(a, 3, p) + 27 * b * b) % p
    j = 1728 * 4 * pow(a, 3, p) * pow(den, -1, p) % p if den else None
    return (p, j, W.n, W.h)


def _progress(name: str, row: dict) -> None:
    print(f"    {name}: {row['element']} as {'·'.join(map(str, row['order']))} "
          f"{'verified' if row.get('found') else 'NOT verified'} in {row['build_seconds']} s", flush=True)


def _work(args):
    T, D, source, factor, build = args
    try:
        r = sweep_curve(T, D, source=source, factor=factor, build=build, progress=_progress)
        return asdict(r)
    except Exception as e:  # noqa: BLE001
        return {"name": T.name, "source": source, "D": D, "error": f"{type(e).__name__}: {e}"}


def _load_checkpoint(path: str | None) -> dict[str, dict]:
    """Finished curves from an earlier, interrupted run (one JSON object per line).

    A curve whose sweep raised is not taken from the checkpoint: it runs again.
    A truncated last line (the run died while writing it) is ignored.
    """
    done: dict[str, dict] = {}
    if not path or not os.path.exists(path):
        return done
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "error" not in r:
                done[r["name"]] = r
    return done


def _fmt_element(a: int, b: int) -> str:
    """a + b*omega as written in the reports: "4 + ω", "ω", "29 + 2ω"."""
    wb = ("" if abs(b) == 1 else str(abs(b))) + "ω"
    if a == 0:
        return ("−" if b < 0 else "") + wb
    return f"{a} {'+' if b >= 0 else '−'} {wb}"


def markdown(results: list[dict], scans: dict, factor: float) -> str:
    L = ["# Endomorphism sweep across curves", ""]
    L.append("Every verified prime-field curve of the std-curves database and of the arkworks-rs/curves "
             "workspace, scanned for a small CM discriminant (|D_K| <= 2 000 000); for every curve that has one, "
             "the cheapest endomorphism (a unit, or the chain sweep's cheapest isogeny chain over a catalogue "
             f"proved to contain every chain within {factor:g}x of it), its construction on the curve, and the "
             "modelled best GLV-2 configuration against the best width-w NAF with the curve's own arithmetic. "
             "Operation counts (M_eq = M + S), not timings.")
    L.append("")
    distinct = {k: s for k, s in scans.items() if not s.get("duplicate_of")}
    small = sum(1 for s in distinct.values() if s.get("D") is not None)
    clean = sum(1 for s in distinct.values() if s.get("D") is None and s.get("verified"))
    failed = sum(1 for s in distinct.values() if not s.get("verified"))
    L.append(f"- Curves scanned: **{len(scans)}**, of which **{len(scans) - len(distinct)}** repeat another entry (same "
             f"p, j-invariant, order and cofactor; marked in the last table), leaving **{len(distinct)}** distinct "
             f"curves.  With a small CM discriminant: **{small}**; certified free of any non-scalar endomorphism of "
             f"degree below 500 000 (|D_K| > 2 000 000): **{clean}**"
             + (f"; failed verification: **{failed}**" if failed else "") + ".")
    L.append("")
    L.append("## Curves with a cheap endomorphism")
    L.append("")
    L.append("| curve | source | p bits | n bits | D_K | h(D) | kind | cheapest | order | chain M_eq (opt / gen) | "
             "catalogue complete | verified on points | modelled best baseline | modelled best GLV | ratio | arithmetic |")
    L.append("|:--|:--|--:|--:|--:|--:|:--|:--|:--|--:|:--|:--|:--|:--|--:|:--|")
    for r in sorted(results, key=lambda r: (r.get("kind") != "chain", -(r.get("model_ops", {}) or {}).get("ratio", 0),
                                            r["name"])):
        if "error" in r:
            L.append(f"| {r['name']} | {r['source']} | | | {r['D']} | | error | {r['error']} | | | | | | | | |")
            continue
        mo = r.get("model_ops") or {}
        if r["kind"] == "automorphism":
            cheapest, order = ("zeta_3" if r["D"] == -3 else "i"), "—"
            comp = "—"
        else:
            cheapest = _fmt_element(*r["best_element"])
            order = "·".join(map(str, r["best_order"]))
            comp = (f"yes (≥ {r['outside_bound']:g} outside; N ≤ {r['nmax']}, ℓ ≤ {r['lmax']})" if r["complete"]
                    else f"NO (bound {r['outside_bound']:g})")
        ver = ("yes" if r["best_verified"] else "NO") + (f" ({r['verified']}/{r['built']} elements)"
                                                          if r["kind"] == "chain" else "")
        L.append(f"| {r['name']} | {r['source']} | {r['p_bits']} | {r['n_bits']} | {r['D']} | {r['class_number']} | "
                 f"{r['kind']} | {cheapest} | {order} | {r['best_chain_M_eq'].get('optimised')} / "
                 f"{r['best_chain_M_eq'].get('generic')} | {comp} | {ver} | "
                 f"{mo.get('best_baseline', '')} {mo.get('baseline', {}).get(mo.get('best_baseline', ''), '')} | "
                 f"{mo.get('best_glv', '')} {mo.get('glv', {}).get(mo.get('best_glv', ''), '')} | "
                 f"{mo.get('ratio', '')} | {r['arithmetic']} |")
    L.append("")
    L.append(f"## Every element within {factor:g}x of the cheapest, per curve")
    L.append("")
    L.append("Each element at its cheapest step order; `verified` is the construction on the curve "
             "(closed walk, action as the predicted scalar on a point of order n, GLV-2 reconstruction).")
    for r in sorted((r for r in results if r.get("kind") == "chain" and "error" not in r), key=lambda r: r["name"]):
        L.append("")
        L.append(f"### {r['name']} (D = {r['D']}, h = {r['class_number']})")
        L.append("")
        L.append("| element | norm | order | M_eq optimised | M_eq generic | verified | build s |")
        L.append("|:--|--:|:--|--:|--:|:--|--:|")
        for row in r.get("rows", []):
            L.append(f"| {_fmt_element(*row['element'])} | {row['norm']} | {'·'.join(map(str, row['order']))} | "
                     f"{row['ops']['optimised']['M_eq']} | {row['ops']['generic']['M_eq']} | "
                     f"{'yes' if row.get('found') else ('NO: ' + str(row.get('note', 'not built')))} | "
                     f"{row.get('build_seconds', '')} |")
    L.append("")
    L.append("## Every curve scanned")
    L.append("")
    L.append("| curve | source | p bits | verified | discriminant certificate |")
    L.append("|:--|:--|--:|:--|:--|")
    for name, s in sorted(scans.items()):
        L.append(f"| {name} | {s['source']} | {s.get('p_bits', '')} | {s.get('verified')} | "
                 f"{s.get('certificate', '')}{' (duplicate of ' + s['duplicate_of'] + ')' if s.get('duplicate_of') else ''} |")
    L.append("")
    return "\n".join(L) + "\n"


def _provenance(args) -> dict:
    """What the run read: the std-curves commit (when the checkout is a git repository), the extra
    categories' own declared sources, and whether python-flint did the polynomial arithmetic."""
    import subprocess
    out: dict = {}
    try:
        out["std_curves_commit"] = subprocess.run(["git", "-C", args.std_curves, "rev-parse", "HEAD"], check=True,
                                                  capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        out["std_curves_commit"] = None
    if args.extra:
        import glob
        out["extra"] = {}
        for path in sorted(glob.glob(os.path.join(args.extra, "*", "curves.json"))):
            doc = json.load(open(path))
            out["extra"][os.path.basename(os.path.dirname(path))] = {k: doc[k] for k in ("desc", "commit") if k in doc}
    flint = EX._flint()
    out["python_flint"] = getattr(flint, "__version__", None) if flint else None
    return out


def main(argv=None) -> int:
    from multiprocessing import Pool
    from .corpus import load_std_curves
    ap = argparse.ArgumentParser(description="the chain sweep on every curve with a small CM discriminant")
    ap.add_argument("--std-curves", required=True, help="a J08nY/std-curves checkout")
    ap.add_argument("--extra", default=None, help="a directory of further std-curves-format categories")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--factor", type=float, default=2.0)
    ap.add_argument("--disc-bound", type=int, default=2_000_000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--checkpoint", default=None,
                    help="append each finished curve to this JSON-lines file, and skip the curves it "
                         "already holds (resumes an interrupted run)")
    args = ap.parse_args(argv)
    loaded = [(T, e, "std-curves") for T, e, _ in load_std_curves(args.std_curves)]
    if args.extra:
        loaded += [(T, e, os.path.basename(os.path.normpath(args.extra)) + "/" + e.category)
                   for T, e, _ in load_std_curves(args.extra)]
    scans: dict[str, dict] = {}
    seen: dict[tuple, str] = {}
    jobs = []
    for T, e, source in loaded:
        if args.only and args.only.lower() not in e.name.lower():
            continue
        if T is None:
            continue
        D, cert = _scan(T, args.disc_bound)
        s = {"source": source, "p_bits": T.p.bit_length(), "verified": T.verified, "certificate": cert, "D": D}
        if T.verified:
            k = _key(T)
            if k in seen:
                s["duplicate_of"] = seen[k]
                scans[e.name] = s
                continue
            seen[k] = e.name
        scans[e.name] = s
        if D is not None:
            jobs.append((T, D, source, args.factor, not args.no_build))
    print(f"{len(scans)} curves scanned, {len(jobs)} with a small discriminant (duplicates removed)", flush=True)
    done = _load_checkpoint(args.checkpoint)
    results = [done[T.name] for T, *_ in jobs if T.name in done]
    if results:
        print(f"{len(results)} curves taken from the checkpoint {args.checkpoint}", flush=True)
    jobs = [j for j in jobs if j[0].name not in done]
    with Pool(args.workers) as pool:
        for r in pool.imap_unordered(_work, jobs):
            results.append(r)
            if args.checkpoint:
                with open(args.checkpoint, "a") as f:
                    f.write(json.dumps(r, default=str) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
            if "error" in r:
                print(f"ERROR {r['name']}: {r['error']}", flush=True)
            else:
                print(f"[{r['elapsed_s']:7.1f}s] {r['name']:44s} D={r['D']:7d} {r['kind']:12s} "
                      f"best={r['best_chain_M_eq'].get('optimised')} verified={r['verified']}/{max(r['built'], 1)} "
                      f"ratio={(r.get('model_ops') or {}).get('ratio')}", flush=True)
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "curves.json"), "w") as f:
        json.dump({"factor": args.factor, "disc_bound": args.disc_bound, "provenance": _provenance(args),
                   "scans": scans, "results": sorted(results, key=lambda r: r["name"])}, f, indent=1, default=str)
        f.write("\n")
    with open(os.path.join(args.out_dir, "curves.md"), "w") as f:
        f.write(markdown(results, scans, args.factor))
    bad = [r["name"] for r in results if "error" in r or not r.get("best_verified")]
    print("unverified or failed:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
