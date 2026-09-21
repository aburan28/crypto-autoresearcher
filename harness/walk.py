"""Random-walk kernel shared by the ECDLP rho and kangaroo solvers.

`rho.py` solves with a Floyd-cycled Teske walk, which finds a collision but
throws the walk away. Everything else the rho/kangaroo family needs -- the
distinguished-point (DP) collision search that real campaigns such as
ECC2K-130 actually run, the tail/cycle shape of a single trajectory, and the
merging forest of short walks -- needs the *trajectory itself*. This module
exposes the walk as a first-class object so it can be stepped, traced,
serialised, drawn, and shared between solvers.

Nothing here uses `ECDLPInstance.k`: walks see public data only. A recovered
scalar is always re-verified by recomputing k*P before it is returned
(docs/claims-and-verification.md).

Scope: exact arithmetic over the toy prime fields of `toycurve.py`. Iteration
counts observed here are properties of the tested subgroup orders and walk
parameters; transferring them to a cryptographic-scale curve is an assumption
this module does not make and does not license.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Iterator

from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int


@dataclass(frozen=True)
class WalkState:
    """A point on the walk together with its known representation.

    Invariant, checked by `AddingWalk.verify_state`: R == a*P + b*Q.
    """
    R: Point
    a: int
    b: int

    def key(self) -> tuple[int, int] | None:
        return self.R


@dataclass(frozen=True)
class RhoTrace:
    """One trajectory iterated until it repeats a point -- the rho shape.

    `states[i]` is the walk after i steps. `tail_length` is rho's straight
    segment (states 0..tail_length-1 are visited once), `cycle_length` the
    loop it falls into. `closed` is False when the step budget ran out first,
    in which case the tail/cycle fields are None and nothing about the orbit
    is claimed.
    """
    states: list[WalkState]
    tail_length: int | None
    cycle_length: int | None
    closed: bool
    group_operations: int

    @property
    def rho_length(self) -> int | None:
        if not self.closed:
            return None
        return self.tail_length + self.cycle_length


@dataclass(frozen=True)
class DPWalk:
    """A short walk run until it lands on a distinguished point.

    `path` is populated only when requested; the solver itself needs just the
    endpoints, but the drawings need every vertex.
    """
    label: str
    start: WalkState
    end: WalkState
    steps: int
    hit_dp: bool
    path: list[WalkState] = field(default_factory=list)


@dataclass(frozen=True)
class Collision:
    """Two distinct representations of the same group element."""
    first: WalkState
    second: WalkState

    @property
    def useful(self) -> bool:
        return self.first.b != self.second.b


class AddingWalk:
    """Teske r-adding walk on <P> with coefficient bookkeeping.

    The branch table T_s = c_s*P + d_s*Q is derived from `seed`, so two
    sessions constructing the same walk step identically. `dp_bits` selects
    the distinguished-point property |{x : x = 0 mod 2^dp_bits}|, giving DP
    walks of expected length 2^dp_bits steps.
    """

    def __init__(self, E: EllipticCurve, P: Point, Q: Point, n: int, seed: int,
                 branches: int = 32, dp_bits: int = 0, tag: str = "walk"):
        if branches < 2:
            raise ValueError("an r-adding walk needs r >= 2 branches")
        if dp_bits < 0:
            raise ValueError("dp_bits must be >= 0")
        self.E, self.P, self.Q, self.n = E, P, Q, n
        self.seed, self.branches, self.dp_bits, self.tag = seed, branches, dp_bits, tag
        self.group_operations = 0
        self._dp_mask = (1 << dp_bits) - 1
        self.steps: list[tuple[Point, int, int]] = []
        for s in range(branches):
            c = _seed_int(seed, f"{tag}_c{s}") % n
            d = _seed_int(seed, f"{tag}_d{s}") % n
            T = self._add(self._mul(c, P), self._mul(d, Q))
            self.steps.append((T, c, d))

    # -- counted arithmetic -------------------------------------------------
    def _add(self, A: Point, B: Point) -> Point:
        self.group_operations += 1
        return self.E.add(A, B)

    def _mul(self, k: int, pt: Point) -> Point:
        """Double-and-add, charging one group operation per add and double."""
        k %= self.n
        result, addend = None, pt
        while k > 0:
            if k & 1:
                result = self._add(result, addend)
            addend = self._add(addend, addend)
            k >>= 1
        return result

    # -- walk ---------------------------------------------------------------
    def branch(self, R: Point) -> int:
        return (R[0] if R is not None else 0) % self.branches

    def step(self, st: WalkState) -> WalkState:
        T, c, d = self.steps[self.branch(st.R)]
        return WalkState(self._add(st.R, T), (st.a + c) % self.n, (st.b + d) % self.n)

    def iterate(self, st: WalkState) -> Iterator[WalkState]:
        while True:
            st = self.step(st)
            yield st

    def is_distinguished(self, R: Point) -> bool:
        if R is None:
            return False
        return (R[0] & self._dp_mask) == 0

    def start(self, label: str) -> WalkState:
        """A deterministic starting state a*P + b*Q with b != 0."""
        a = _seed_int(self.seed, f"{self.tag}_a0_{label}") % self.n
        b = (_seed_int(self.seed, f"{self.tag}_b0_{label}") % (self.n - 1)) + 1
        return WalkState(self._add(self._mul(a, self.P), self._mul(b, self.Q)), a, b)

    def verify_state(self, st: WalkState) -> bool:
        """Recompute a*P + b*Q and compare -- the walk's own certificate."""
        return self.E.add(self.E.mul(st.a, self.P), self.E.mul(st.b, self.Q)) == st.R

    # -- solving ------------------------------------------------------------
    def scalar_from(self, col: Collision) -> int | None:
        """k from a collision, or None if the relation is degenerate/wrong.

        Verified by recomputing k*P; a collision that does not verify is
        reported as no result rather than as a candidate.
        """
        db = (col.second.b - col.first.b) % self.n
        if db == 0:
            return None
        k = (col.first.a - col.second.a) * pow(db, -1, self.n) % self.n
        if self.E.mul(int(k), self.P) != self.Q:
            return None
        return int(k)


def trace_orbit(walk: AddingWalk, start: WalkState | None = None,
                max_steps: int = 100_000) -> RhoTrace:
    """Iterate one walk until it revisits a point, recording every state.

    This is the picture-generating counterpart of Floyd cycle detection: it
    costs O(rho length) memory and returns where the tail ends and the cycle
    begins, which Floyd never learns.
    """
    st = walk.start("trace") if start is None else start
    ops0 = walk.group_operations
    seen: dict[Point, int] = {st.R: 0}
    states = [st]
    for i in range(1, max_steps + 1):
        st = walk.step(st)
        prev = seen.get(st.R)
        if prev is not None:
            states.append(st)
            return RhoTrace(states, prev, i - prev, True,
                            walk.group_operations - ops0)
        seen[st.R] = i
        states.append(st)
    return RhoTrace(states, None, None, False, walk.group_operations - ops0)


def walk_to_dp(walk: AddingWalk, start: WalkState, label: str = "",
               max_steps: int = 100_000, record_path: bool = False) -> DPWalk:
    """Run one walk until it lands on a distinguished point or runs out.

    A walk that exhausts its budget is returned with `hit_dp=False`; that is a
    budget outcome, never evidence about the group.
    """
    if walk.dp_bits == 0:
        raise ValueError("walk_to_dp needs dp_bits > 0")
    st = start
    path = [st] if record_path else []
    for i in range(1, max_steps + 1):
        st = walk.step(st)
        if record_path:
            path.append(st)
        if walk.is_distinguished(st.R):
            return DPWalk(label, start, st, i, True, path)
    return DPWalk(label, start, st, max_steps, False, path)


@dataclass(frozen=True)
class DPSearchResult:
    """Outcome of a van Oorschot--Wiener distinguished-point rho search."""
    solved: bool
    k: int | None
    group_operations: int
    walks: list[DPWalk]
    steps: int
    distinguished_points: int
    collision: Collision | None
    reason: str = ""


def solve_dp(inst: ECDLPInstance, dp_bits: int | None = None,
             branches: int = 32, max_walks: int = 4096,
             max_steps_per_walk: int | None = None,
             record_paths: bool = False, stop_on_solution: bool = True,
             walk: AddingWalk | None = None) -> DPSearchResult:
    """Recover k by distinguished-point parallel collision search.

    This is the method a real campaign runs: independent short walks are
    launched from many starts, only distinguished points are stored, and the
    golden collision is two walks reporting the same DP with different
    representations. It parallelises with no shared state (each walk is
    independent), which Floyd rho does not -- the reason ECC2K-130-class
    computations are organised this way. Here every walk is run in one
    process, so the result is the collision structure, not a speedup claim.

    With `stop_on_solution=False` the search keeps launching walks after the
    golden collision, up to `max_walks`. The first verified relation is still
    what is reported; the extra walks exist to observe the DP forest (yield,
    merge structure, drawings) and change no reported scalar.
    """
    E = inst.curve()
    n = inst.n
    if dp_bits is None:
        # Aim for ~sqrt(n)/8 walks of ~8*log2(n) steps at toy scale.
        dp_bits = max(1, (n.bit_length() // 2) - 1)
    if walk is None:
        walk = AddingWalk(E, inst.P, inst.Q, n, inst.seed, branches=branches,
                          dp_bits=dp_bits, tag="rhodp")
    if max_steps_per_walk is None:
        max_steps_per_walk = max(64, 40 << dp_bits)

    ops0 = walk.group_operations
    seen: dict[Point, WalkState] = {}
    walks: list[DPWalk] = []
    steps = 0
    solved: tuple[int, Collision] | None = None
    for w in range(max_walks):
        dw = walk_to_dp(walk, walk.start(f"dp{w}"), label=f"W{w}",
                        max_steps=max_steps_per_walk, record_path=record_paths)
        walks.append(dw)
        steps += dw.steps
        if not dw.hit_dp:
            continue
        prev = seen.get(dw.end.R)
        if prev is None:
            seen[dw.end.R] = dw.end
            continue
        if solved is not None:
            continue
        col = Collision(prev, dw.end)
        k = walk.scalar_from(col)
        if k is None:
            # Same DP, same representation (the walks merged earlier): useless.
            continue
        solved = (k, col)
        if stop_on_solution:
            break
    if solved is not None:
        return DPSearchResult(True, solved[0], walk.group_operations - ops0,
                              walks, steps, len(seen), solved[1])
    return DPSearchResult(False, None, walk.group_operations - ops0, walks,
                          steps, len(seen), None,
                          reason="no distinguished-point collision yielded an "
                                 "invertible relation within the walk budget")


# -- serialisation ---------------------------------------------------------

def _pt(R: Point) -> list[int] | None:
    return None if R is None else [int(R[0]), int(R[1])]


def _state(st: WalkState) -> dict:
    return {"R": _pt(st.R), "a": int(st.a), "b": int(st.b)}


def trace_to_dict(walk: AddingWalk, tr: RhoTrace) -> dict:
    return {
        "kind": "rho_trace",
        "params": {"n": walk.n, "branches": walk.branches,
                   "dp_bits": walk.dp_bits, "seed": walk.seed},
        "closed": tr.closed,
        "tail_length": tr.tail_length,
        "cycle_length": tr.cycle_length,
        "rho_length": tr.rho_length,
        "group_operations": tr.group_operations,
        "states": [_state(s) for s in tr.states],
    }


def dp_walks_to_dict(walk: AddingWalk, walks: list[DPWalk],
                     collision: Collision | None = None) -> dict:
    return {
        "kind": "dp_walks",
        "params": {"n": walk.n, "branches": walk.branches,
                   "dp_bits": walk.dp_bits, "seed": walk.seed},
        "collision": None if collision is None else {
            "first": _state(collision.first), "second": _state(collision.second)},
        "walks": [{"label": w.label, "steps": w.steps, "hit_dp": w.hit_dp,
                   "start": _state(w.start), "end": _state(w.end),
                   "path": [_pt(s.R) for s in w.path]} for w in walks],
    }


def dump_json(obj: dict, path: str) -> None:
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")
