"""Hash-driven jump-sum walks on (Z, +). Shared walk generator; not a sumset meter."""
from __future__ import annotations
import hashlib
from freeze import FAMILIES, RADDING_R, UNIT_MAX


def _h64(*parts: object) -> int:
    msg = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "little")


def weight_class(m: int, w: int) -> tuple[int, ...]:
    out: list[int] = []

    def rec(start: int, left: int, acc: int) -> None:
        if left == 0:
            out.append(acc)
            return
        for i in range(start, m - left + 1):
            rec(i + 1, left - 1, acc | (1 << i))

    rec(0, w, 0)
    return tuple(out)


def sigma(family: str, m: int) -> tuple[int, ...]:
    if family == "Ja_radding":
        cap = 1 << (m // 3 + 1)
        return tuple(1 + (_h64("Ja", m, i) % cap) for i in range(RADDING_R))
    if family == "Jb_signed_bits":
        bits = []
        for i in range(m):
            bits.append(1 << i)
            bits.append(-(1 << i))
        return tuple(bits)
    if family == "Jc_exchanges":
        pairs = []
        for t in range(32):
            a = _h64("Jc", m, t, 0) % m
            b = _h64("Jc", m, t, 1) % m
            if a == b:
                b = (b + 1) % m
            pairs.append((1 << a) - (1 << b))
        return tuple(pairs)
    if family == "Jd_unit":
        return tuple(range(1, UNIT_MAX + 1))
    raise ValueError(family)


def jump_sums(family: str, m: int, t: int, seed: int) -> tuple[int, ...]:
    sig = sigma(family, m)
    y = 0
    acc = 0
    seen = [0]
    for step in range(t):
        idx = _h64("walk", family, m, seed, y, step) % len(sig)
        acc += sig[idx]
        y = acc
        seen.append(acc)
    return tuple(dict.fromkeys(seen))


def rng_subset(universe_m: int, size: int, seed: int) -> tuple[int, ...]:
    cap = 1 << universe_m
    chosen: set[int] = set()
    k = 0
    while len(chosen) < size:
        chosen.add(_h64("Wprime", universe_m, seed, k) % cap)
        k += 1
    return tuple(sorted(chosen))


def decay_set(base: tuple[int, ...], m: int, q_pct: int, seed: int) -> tuple[int, ...]:
    if q_pct == 0:
        return base
    n = len(base)
    replace = (q_pct * n) // 100
    if q_pct == 100:
        return rng_subset(m, n, seed + 9000)
    items = list(base)
    cap = 1 << m
    used = set(items)
    for i in range(replace):
        used.discard(items[i])
        v = _h64("Wq", m, seed, q_pct, i) % cap
        while v in used:
            v = (v + 1) % cap
        items[i] = v
        used.add(v)
    return tuple(items)


def millirho(card_x_j: int, card_xp_j: int) -> int:
    if card_x_j <= 0:
        return 10**9
    return (1000 * card_xp_j) // card_x_j


assert FAMILIES[0] == "Ja_radding"
