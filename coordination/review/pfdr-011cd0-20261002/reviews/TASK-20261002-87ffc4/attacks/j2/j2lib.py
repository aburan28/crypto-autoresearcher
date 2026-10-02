"""TASK-20261002-87ffc4 red team, joint J2: helpers for the Lemma L1/L2 checks.

Own code (standard library + numpy). The engine's curve.py, _accel.py (a
dependency of tails.py), factor_base.py and tails.py are loaded BY FILE PATH
into a private package name, for the J2 toy enumeration only (card RT-6); no
solver, harvester, CLI or analysis module is imported or executed.

tail_rule() is this reviewer's reimplementation of the stored set of
tails.py (orderings (i_1, s_1)..(i_h, s_h), i_1 <= .. <= i_h, s_1 = +1, every
suffix sum nonzero, identity sums dropped), checked against the real
TailTable by j2_validate_engine.py before it is used anywhere.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import types

ENGINE_DIR = os.path.join(
    os.environ.get("RT_WT", "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/"
                   "scratchpad/wt-pfdr011cd0-5753edf2e"),
    "src", "crypto_autoresearcher", "index_calculus")


def load_engine():
    """curve, _accel, factor_base, tails loaded by file path under 'rtengine'."""
    if "rtengine" not in sys.modules:
        pkg = types.ModuleType("rtengine")
        pkg.__path__ = [ENGINE_DIR]
        sys.modules["rtengine"] = pkg
    mods = {}
    for name in ("curve", "_accel", "factor_base", "tails"):
        full = f"rtengine.{name}"
        if full in sys.modules:
            mods[name] = sys.modules[full]
            continue
        spec = importlib.util.spec_from_file_location(full, os.path.join(ENGINE_DIR, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods


def vec_of(tail, s):
    v = [0] * s
    for i, sg in tail:
        v[i] += sg
    return tuple(v)


def tail_rule(s: int, h: int, L=None, N=None):
    """Every tail the tails.py build stores, as (tail, vector).

    With L (logs mod N) the build's L-dependent drops are applied: a level-k
    candidate whose sum is the identity (sum . L == 0 mod N) is not stored, and
    nothing is built on it (the suffix rule). Without L only formally-zero
    sums (the zero integer vector) are dropped, i.e. the L-free superset V_0.
    """
    def is_identity(vec):
        if L is None:
            return all(c == 0 for c in vec)
        return sum(c * l for c, l in zip(vec, L)) % N == 0

    level = []
    for i in range(s):
        t = ((i, 1),)
        v = vec_of(t, s)
        if L is not None and is_identity(v):
            continue  # a base point that is the identity is not a point (U-model extension)
        level.append(t)
    for _k in range(2, h + 1):
        nxt = []
        for a in range(s):
            if L is not None and is_identity(vec_of(((a, 1),), s)):
                continue
            for T in level:
                if T[0][0] < a:
                    continue
                negT = tuple((i, -sg) for i, sg in T)
                for cand in (((a, 1),) + T, ((a, 1),) + negT):
                    if is_identity(vec_of(cand, s)):
                        continue
                    nxt.append(cand)
        level = nxt
    return [(t, vec_of(t, s)) for t in level]


def canon_pm(v):
    """Representative of {v, -v} (first nonzero coordinate positive)."""
    for c in v:
        if c > 0:
            return tuple(v)
        if c < 0:
            return tuple(-x for x in v)
    return tuple(v)


def harvester_elements(tails, s):
    """Formally distinct elements up to sign (harvester dup_formal), split into
    the TT element set (vectors equal to +-e_b removed: the harvester drops
    them as TB formal duplicates of the base element at x(F_b)) and the list
    of degenerate +-e_b vectors."""
    seen = {}
    for t, v in tails:
        k = canon_pm(v)
        seen.setdefault(k, []).append(t)
    unit = set()
    for b in range(s):
        e = [0] * s
        e[b] = 1
        unit.add(tuple(e))
    tt = [k for k in seen if k not in unit]
    deg = [k for k in seen if k in unit]
    return tt, deg, seen


def monic_mod(vec, N):
    v = [c % N for c in vec]
    for c in v:
        if c:
            inv = pow(c, -1, N)
            return tuple(x * inv % N for x in v)
    return None


def dependent_mod(u, w, N):
    """u and w linearly dependent over F_N (both nonzero mod N assumed)."""
    mu, mw = monic_mod(u, N), monic_mod(w, N)
    return mu is not None and mw is not None and mu == mw


def signed_pair_classes(pairs, N):
    """Map every signed pair (u, w, sigma) to its projective class [u - sigma w]
    over F_N. Returns (classes: dict class -> list of (pair_index, sigma)),
    excluded counts {'zero': .., 'dependent': ..}."""
    classes = {}
    excl = {"zero": 0, "dependent": 0}
    for idx, (u, w) in enumerate(pairs):
        if dependent_mod(u, w, N):
            excl["dependent"] += 2
            continue
        for sg in (1, -1):
            r = tuple(a - sg * b for a, b in zip(u, w))
            key = monic_mod(r, N)
            if key is None:
                excl["zero"] += 1
                continue
            classes.setdefault(key, []).append((idx, sg))
    return classes, excl
