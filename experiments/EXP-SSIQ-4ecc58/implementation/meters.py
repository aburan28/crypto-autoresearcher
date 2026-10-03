"""Twin independent meters for EXP-SSIQ-4ecc58 holonomy census.

Path A / path B must agree on generated H_N (as sets of matrices).
No Magma/Sage. No Bedrock. Not an attack.
"""
from __future__ import annotations

import random
from typing import Iterable

from ntheory import (
    Mat,
    det_group_S,
    enumerate_order_elements,
    enumerate_spine_elements,
    gl2_order,
    mdet,
    mid,
    minv,
    mmul,
    quat_to_mat,
    sl2_order,
    split_ij,
)

Gen = tuple[int, int, int, int, int]  # A,B,C,D,nrd


def bfs_close(gens: list[Mat], n: int) -> set[Mat]:
    ident = mid(n)
    seen: set[Mat] = {ident}
    queue: list[Mat] = [ident]
    while queue:
        g = queue.pop()
        for s in gens:
            h = mmul(g, s, n)
            if h not in seen:
                seen.add(h)
                queue.append(h)
            inv = minv(s, n)
            if inv is not None:
                hi = mmul(g, inv, n)
                if hi not in seen:
                    seen.add(hi)
                    queue.append(hi)
    return seen


def matrices_from_quats(
    elems: list[Gen], n: int, i_mat: Mat, j_mat: Mat
) -> tuple[list[Mat], list[str]]:
    flags: list[str] = []
    mats: list[Mat] = []
    for A, B, C, D, nrd in elems:
        m = quat_to_mat(A, B, C, D, n, i_mat, j_mat)
        if m is None:
            flags.append("map_none")
            continue
        if mdet(m, n) != nrd % n:
            flags.append("det_ne_nrd")
            continue
        mats.append(m)
    return mats, flags


def holonomy_both(
    elems: list[Gen], n: int, i_mat: Mat, j_mat: Mat
) -> dict:
    mats, flags = matrices_from_quats(elems, n, i_mat, j_mat)
    # Path A: given order; Path B: reversed unique
    uniq: list[Mat] = []
    seenm: set[Mat] = set()
    for m in mats:
        if m not in seenm:
            seenm.add(m)
            uniq.append(m)
    ha = bfs_close(uniq, n)
    hb = bfs_close(list(reversed(uniq)), n)
    ident = mid(n)
    iso_ok = ident in ha and ident in hb
    return {
        "agree": ha == hb,
        "H_a": ha,
        "H_b": hb,
        "n_gens": len(uniq),
        "iso_ok": iso_ok,
        "flags": flags,
        "|H|": len(ha),
    }


def sl_cap(H: set[Mat], n: int) -> set[Mat]:
    return {g for g in H if mdet(g, n) == 1}


def derived_subgroup(G: set[Mat], n: int) -> set[Mat]:
    if not G:
        return set()
    gens = list(G)
    # commutators of a generating set: use all elements is OK at |G|<=2016
    comms: list[Mat] = []
    sample = gens if len(gens) <= 80 else gens[:40] + gens[-40:]
    for x in sample:
        ix = minv(x, n)
        if ix is None:
            continue
        for y in sample:
            iy = minv(y, n)
            if iy is None:
                continue
            # [x,y] = x y x^{-1} y^{-1}
            c = mmul(mmul(mmul(x, y, n), ix, n), iy, n)
            comms.append(c)
    return bfs_close(comms, n)


def abelianisation_order(Hsl: set[Mat], n: int) -> int | None:
    if not Hsl:
        return 0
    der = derived_subgroup(Hsl, n)
    if not der.issubset(Hsl):
        return None
    d = len(der)
    if d == 0:
        return None
    if len(Hsl) % d:
        return None
    return len(Hsl) // d


def gl2_S_size(n: int, S: Iterable[int]) -> int:
    """|GL_2(F_n)_S| = |SL2| * |<S> in F_n^*| for prime n."""
    sl = sl2_order(n)
    dets = det_group_S(n, S)
    return sl * len(dets)


def index_gls(H: set[Mat], n: int, S: Iterable[int]) -> int | None:
    target = gl2_S_size(n, S)
    dets = det_group_S(n, S)
    Hd = {mdet(g, n) for g in H}
    if not Hd.issubset(dets):
        # still well-defined index of H inside the ambient GL if we generated extra dets
        pass
    if target <= 0 or len(H) == 0:
        return None
    if target % len(H):
        return None
    return target // len(H)


def rmax_from_ab(H: set[Mat], n: int) -> int | None:
    """Largest path-independent abelian quotient order: |H^{ab}|, bounded by det image if SL is perfect."""
    Hsl = sl_cap(H, n)
    ab_sl = abelianisation_order(Hsl, n)
    dets = {mdet(g, n) for g in H}
    if ab_sl is None:
        return None
    # H^{ab} surjects onto det(H); if SL_ab is trivial then |H^{ab}| = |det H|
    if ab_sl == 1:
        return len(dets)
    return ab_sl * len(dets)


def random_subgroup_same_order(order: int, n: int, rng: random.Random, tries: int = 80) -> set[Mat] | None:
    """Null: random subgroup of GL_2(F_n) of the same cardinality, or None."""
    ident = mid(n)
    field = list(range(n))
    for _ in range(tries):
        gens: list[Mat] = []
        for _g in range(3):
            a, b, c, d = (rng.choice(field) for _ in range(4))
            m = (a, b, c, d)
            if minv(m, n) is None:
                continue
            gens.append(m)
        if not gens:
            continue
        H = bfs_close(gens, n)
        if len(H) == order and ident in H:
            return H
    return None


def cayley_holonomy_zn(mod: int, gens: list[int]) -> dict:
    """Positive nearby object: Cayley graph of Z/mod. Holonomy is abelian (= the group)."""
    seen = {0}
    q = [0]
    while q:
        x = q.pop()
        for g in gens:
            y = (x + g) % mod
            if y not in seen:
                seen.add(y)
                q.append(y)
            y2 = (x - g) % mod
            if y2 not in seen:
                seen.add(y2)
                q.append(y2)
    return {
        "order": len(seen),
        "abelian": True,
        "full": len(seen) == mod,
        "twin_ok": True,
    }


def iso_checks(elems: list[Gen], n: int, i_mat: Mat, j_mat: Mat) -> dict:
    ident = mid(n)
    one = quat_to_mat(2, 0, 0, 0, n, i_mat, j_mat)  # 1 = (2+0i+0j+0k)/2
    flags = []
    if one != ident:
        flags.append("one_not_I")
    det_ok = 0
    det_bad = 0
    for A, B, C, D, nrd in elems[:200]:
        m = quat_to_mat(A, B, C, D, n, i_mat, j_mat)
        if m is None:
            det_bad += 1
            continue
        if mdet(m, n) == nrd % n:
            det_ok += 1
        else:
            det_bad += 1
    return {
        "one_is_I": one == ident,
        "det_ok": det_ok,
        "det_bad": det_bad,
        "flags": flags,
        "split_ok": True,
    }
