"""Pollard kangaroo (lambda) for ECDLP over an interval, with DP traps.

Rho searches the whole subgroup; kangaroo searches an interval [lo, hi] and
costs ~2*sqrt(hi-lo) group operations, which is the better method whenever the
scalar is known to be confined. Both are the same object underneath -- a
pseudorandom walk whose steps are recorded as a scalar offset -- so this module
mirrors `walk.py`: the trajectory is retained, so tame and wild herds can be
traced and drawn, not just counted.

Public data only; `ECDLPInstance.k` is never read. A recovered scalar is
re-verified by recomputing k*P before it is returned, and a scalar outside the
declared interval is rejected rather than reported.

Scope: exact arithmetic at toy scale. Operation counts are properties of the
tested interval widths and jump parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int
from .walk import _pt


@dataclass(frozen=True)
class Kangaroo:
    """One kangaroo's trajectory. `R == base + distance*P` at every step."""
    label: str
    herd: str            # "tame" | "wild"
    base_offset: int     # tame: known scalar of the start; wild: 0 (start is Q)
    R: Point
    distance: int
    jumps: int
    hit_dp: bool
    path: list[Point] = field(default_factory=list)


@dataclass(frozen=True)
class KangarooResult:
    solved: bool
    k: int | None
    group_operations: int
    jumps: int
    distinguished_points: int
    kangaroos: list[Kangaroo]
    interval: tuple[int, int]
    reason: str = ""


class JumpWalk:
    """Pseudorandom jump set of mean size `mean_jump`, indexed by x mod r."""

    def __init__(self, E: EllipticCurve, P: Point, n: int, seed: int,
                 branches: int = 16, mean_jump: int = 8, dp_bits: int = 3,
                 tag: str = "kangaroo"):
        if branches < 2:
            raise ValueError("a jump walk needs r >= 2 branches")
        if mean_jump < 1:
            raise ValueError("mean_jump must be >= 1")
        self.E, self.P, self.n = E, P, n
        self.branches, self.dp_bits = branches, dp_bits
        self.group_operations = 0
        self._dp_mask = (1 << dp_bits) - 1
        # Jump sizes spread over [1, 2*mean_jump] so the mean is ~mean_jump.
        self.jump_scalars = [1 + _seed_int(seed, f"{tag}_s{j}") % (2 * mean_jump)
                             for j in range(branches)]
        self.jump_points = [self.mul(s, P) for s in self.jump_scalars]

    def add(self, A: Point, B: Point) -> Point:
        self.group_operations += 1
        return self.E.add(A, B)

    def mul(self, k: int, pt: Point) -> Point:
        k %= self.n
        result, addend = None, pt
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result

    def branch(self, R: Point) -> int:
        return (R[0] if R is not None else 0) % self.branches

    def hop(self, R: Point, distance: int) -> tuple[Point, int]:
        j = self.branch(R)
        return self.add(R, self.jump_points[j]), distance + self.jump_scalars[j]

    def is_distinguished(self, R: Point) -> bool:
        if R is None:
            return False
        return (R[0] & self._dp_mask) == 0


def solve_interval(inst: ECDLPInstance, lo: int | None = None,
                   hi: int | None = None, herd_size: int = 4,
                   branches: int = 16, dp_bits: int | None = None,
                   mean_jump: int | None = None,
                   max_jumps_per_kangaroo: int | None = None,
                   record_paths: bool = False) -> KangarooResult:
    """Recover k in [lo, hi] with tame and wild herds meeting at a DP.

    Tame kangaroos start at known scalars inside the interval; wild kangaroos
    start at Q. When a tame kangaroo at total distance `dt` from a start of
    known scalar `m` lands on the same point as a wild kangaroo at distance
    `dw`, then (m + dt)*P == (k + dw)*P, so k = m + dt - dw (mod n).

    Kangaroos are advanced round-robin so a merge is found by the shared DP
    table rather than by one herd out-running the other.
    """
    E, n = inst.curve(), inst.n
    lo = 1 if lo is None else lo
    hi = (n - 1) if hi is None else hi
    if not (0 <= lo <= hi < n):
        raise ValueError(f"interval [{lo}, {hi}] is not inside [0, {n - 1}]")
    width = hi - lo + 1
    if mean_jump is None:
        mean_jump = max(2, int(width ** 0.5) // 2 or 2)
    if dp_bits is None:
        dp_bits = max(1, (width.bit_length() // 4) or 1)
    if max_jumps_per_kangaroo is None:
        max_jumps_per_kangaroo = max(128, 8 * int(width ** 0.5) + 64)

    jw = JumpWalk(E, inst.P, n, inst.seed, branches=branches,
                  mean_jump=mean_jump, dp_bits=dp_bits)

    roos: list[Kangaroo] = []
    live: list[dict] = []
    for i in range(herd_size):
        # Tame: spread the starts across the interval, scalars known exactly.
        m = lo + (width * (2 * i + 1)) // (2 * herd_size)
        live.append({"label": f"T{i}", "herd": "tame", "base": m,
                     "R": jw.mul(m, inst.P), "d": 0, "jumps": 0,
                     "path": [], "done": False, "hit": False})
        # Wild: start at Q + delta*P for small known delta, so the herd spreads.
        delta = _seed_int(inst.seed, f"wild{i}") % max(1, mean_jump)
        live.append({"label": f"W{i}", "herd": "wild", "base": 0,
                     "R": jw.add(inst.Q, jw.mul(delta, inst.P)), "d": delta,
                     "jumps": 0, "path": [], "done": False, "hit": False})
    if record_paths:
        for r in live:
            r["path"].append(r["R"])

    # DP table: point -> list of (herd, base, distance)
    table: dict[Point, list[tuple[str, int, int]]] = {}
    total_jumps = 0
    solved_k: int | None = None

    def _finish() -> KangarooResult:
        for r in live:
            roos.append(Kangaroo(r["label"], r["herd"], r["base"], r["R"],
                                 r["d"], r["jumps"], r["hit"], list(r["path"])))
        if solved_k is None:
            return KangarooResult(False, None, jw.group_operations, total_jumps,
                                  len(table), roos, (lo, hi),
                                  reason="no tame/wild meeting produced a "
                                         "verified scalar within the jump budget")
        return KangarooResult(True, solved_k, jw.group_operations, total_jumps,
                              len(table), roos, (lo, hi))

    for _ in range(max_jumps_per_kangaroo):
        progressed = False
        for r in live:
            if r["done"]:
                continue
            progressed = True
            r["R"], r["d"] = jw.hop(r["R"], r["d"])
            r["jumps"] += 1
            total_jumps += 1
            if record_paths:
                r["path"].append(r["R"])
            if r["jumps"] >= max_jumps_per_kangaroo:
                r["done"] = True
            if not jw.is_distinguished(r["R"]):
                continue
            r["hit"] = True
            entry = (r["herd"], r["base"], r["d"])
            bucket = table.setdefault(r["R"], [])
            for herd, base, dist in bucket:
                if herd == r["herd"]:
                    continue
                if r["herd"] == "tame":
                    cand = (r["base"] + r["d"] - dist) % n
                else:
                    cand = (base + dist - r["d"]) % n
                if E.mul(int(cand), inst.P) != inst.Q:
                    continue          # collision, but not a usable relation
                if not (lo <= cand <= hi):
                    continue          # verified scalar outside declared interval
                solved_k = int(cand)
                return _finish()
            bucket.append(entry)
        if not progressed:
            break
    return _finish()


def kangaroos_to_dict(res: KangarooResult) -> dict:
    return {
        "kind": "kangaroo",
        "interval": [res.interval[0], res.interval[1]],
        "solved": res.solved,
        "k": res.k,
        "group_operations": res.group_operations,
        "jumps": res.jumps,
        "distinguished_points": res.distinguished_points,
        "kangaroos": [{"label": r.label, "herd": r.herd, "jumps": r.jumps,
                       "distance": r.distance, "hit_dp": r.hit_dp,
                       "end": _pt(r.R), "path": [_pt(p) for p in r.path]}
                      for r in res.kangaroos],
    }
