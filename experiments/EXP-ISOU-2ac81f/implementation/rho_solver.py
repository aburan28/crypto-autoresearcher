"""
Pollard rho with distinguished points, matched across every curve solved in
this census (frozen walk function / partition count / DP parameter /
multiplier-generation seed, per the handoff's "MATCHED SOLVER ACROSS EVERY
CURVE" constraint). No automorphism/negation-map speedup is used.

Walk function (frozen):
    r = 20 partitions, by (x mod r).
    partition 0            -> DOUBLE the current point.
    partition 1..r-1       -> ADD a precomputed multiplier M_j = [s_j]P +
                               [t_j]Q, with (s_j, t_j) drawn once per curve
                               from random.Random(MULTIPLIER_SCHEDULE_SEED)
                               reduced mod that curve's own N (the schedule
                               SEED and generation PROCEDURE are identical
                               across every curve; the resulting integers
                               necessarily differ because N differs, which
                               is unavoidable and is what "matched
                               implementation" means here, not literally
                               identical integers -- see run manifest).
Each step (add or double) increments the Q1 group-operation counter exactly
once, via ec_group_ops.GroupOpCounter, in the affine common coordinate
system (ec_group_ops.py). This module never touches ec_jacobian.py's
counters.

Distinguished point: x's low DP_BITS bits (of its integer representative in
[0, p)) are all zero. DP_BITS is derived from N (see distinguished_point_bits)
so the expected number of stored distinguished points per solve stays small
regardless of N, and this derivation is fixed BEFORE any solve.

Termination: a censored run (step cap reached before a collision) is
reported as CENSORED with its step count at cutoff -- never as a slow curve,
per AGENTS.md rule 5 and the contract's stopping rules.
"""
from __future__ import annotations

import hashlib
import random

from ec_group_ops import GroupOpCounter, ec_add_affine, ec_double_affine, ec_scalar_mult_affine

R_PARTITIONS = 20
MULTIPLIER_SCHEDULE_SEED = 0xC0FFEE


def partition_of(x: int) -> int:
    """
    Partition function mapping x -> {0, ..., R_PARTITIONS-1}, used to pick
    the walk's next transition. Deliberately NOT a simple "x mod r": an
    early self-test (implementation.md, "walk partition function revision")
    found that "x mod R_PARTITIONS" correlates with the distinguished-point
    test (also a low-bits-of-x condition) enough to produce short
    functional-graph cycles at a rate far above the random-function
    heuristic (~30-40% of seeds censored on a toy curve where a censored
    walk should be rare). A SHA-256-based hash of x decorrelates the
    partition decision from any structural property of x, which is the
    standard fix for this class of walk-function weakness and is frozen
    here, identically, for every curve solved in this census.
    """
    h = hashlib.sha256(x.to_bytes((x.bit_length() + 7) // 8 or 1, "big")).digest()
    return int.from_bytes(h[:4], "big") % R_PARTITIONS


def modinv_general(x, n):
    """Modular inverse via extended Euclid; works for composite n too
    (needed for null-object curves whose order N' is not required to be
    prime), returns None if x is not invertible mod n."""
    x %= n
    if x == 0:
        return None
    g, a, _b = _egcd(x, n)
    if g != 1:
        return None
    return a % n


def _egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = _egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def distinguished_point_bits(N: int) -> int:
    bits = N.bit_length()
    return max(2, bits // 2 - 4)


def build_multipliers(P, Qd, a, p, N, schedule_seed=MULTIPLIER_SCHEDULE_SEED):
    rng = random.Random(schedule_seed)
    mults = []
    for _ in range(R_PARTITIONS):
        s = rng.randrange(1, N)
        t = rng.randrange(1, N)
        M = ec_add_affine(
            ec_scalar_mult_affine(s, P, a, p),
            ec_scalar_mult_affine(t, Qd, a, p),
            a, p,
        )
        mults.append((s, t, M))
    return mults


def _step(X, a, p, mults):
    if X is None:
        return None
    part = partition_of(X[0])
    if part == 0:
        return ec_double_affine(X, a, p)
    return ec_add_affine(X, mults[part][2], a, p)


def _shortest_cycle_length(P, a, p, mults, trial_steps):
    """
    Floyd (tortoise/hare) cycle detection on a SHORT trial walk, used ONLY
    to screen out a multiplier set whose functional graph happens to have
    a pathologically short dominant cycle (see implementation.md, "short
    additive-walk cycles"): the naive r-adding walk can, for a specific
    (unlucky) set of jump vectors, collapse onto a cycle far shorter than
    the O(sqrt(N)) the random-function heuristic predicts, in which case a
    single walk relying only on distinguished points can loop for a very
    long time (or, within a bounded step cap, censor) without ever
    detecting the collision. Returns the found cycle length, or None if no
    cycle was found within trial_steps (does not guarantee no short cycle
    exists elsewhere in the graph -- it is a screen, not a proof).
    """
    tortoise = P
    hare = P
    for _ in range(trial_steps):
        tortoise = _step(tortoise, a, p, mults)
        hare = _step(_step(hare, a, p, mults), a, p, mults)
        if tortoise is None or hare is None:
            return None
        if tortoise == hare:
            # measure the cycle length
            mu = 0
            hare2 = P
            tortoise2 = tortoise
            # find cycle length lam by advancing a pointer from the meeting
            # point until it returns
            lam = 1
            hare3 = _step(tortoise, a, p, mults)
            while hare3 != tortoise and lam < trial_steps:
                hare3 = _step(hare3, a, p, mults)
                lam += 1
            return lam
    return None


def build_validated_multipliers(P, Qd, a, p, N, trial_steps=20000, short_cycle_threshold=None,
                                 max_attempts=25):
    """
    Screens candidate multiplier sets (schedule_seed = MULTIPLIER_SCHEDULE_SEED,
    MULTIPLIER_SCHEDULE_SEED+1, ...) against _shortest_cycle_length, rejecting
    any whose trial walk reveals a cycle shorter than short_cycle_threshold,
    and using the first that passes. This is a STRUCTURAL, pre-solve
    screening step (identical procedure applied to every curve, base curve,
    class member, and null object alike), not a per-seed or per-outcome
    adjustment: it never looks at DLP solve cost data, only at the
    walk-function's own cycle structure for this curve. The number of
    attempts needed is recorded (an honest, reported implementation
    deviation) rather than hidden.
    """
    if short_cycle_threshold is None:
        # Want P(cycle has zero distinguished points) = (1 - 2^-dp_bits)^threshold
        # to be comfortably small; threshold = 8 * 2^dp_bits gives ~e^-8.
        dp_bits = distinguished_point_bits(N)
        short_cycle_threshold = max(200, 8 * (1 << dp_bits))
    for attempt in range(max_attempts):
        schedule_seed = MULTIPLIER_SCHEDULE_SEED + attempt
        mults = build_multipliers(P, Qd, a, p, N, schedule_seed=schedule_seed)
        cyc = _shortest_cycle_length(P, a, p, mults, trial_steps)
        if cyc is None or cyc >= short_cycle_threshold:
            return mults, attempt, cyc
    # exhausted attempts: return the last candidate anyway, flagged
    return mults, max_attempts - 1, cyc


class RhoResult:
    def __init__(self):
        self.status = None  # "solved" | "censored" | "restart_degenerate"
        self.k = None
        self.group_ops = 0
        self.adds = 0
        self.doubles = 0
        self.steps_at_cutoff = 0
        self.dp_bits = None
        self.wall_seconds = None
        self.restarts = 0
        self.multiplier_screen_attempts = 0
        self.multiplier_schedule_seed_used = None
        self.screened_cycle_length = None


def solve_rho(P, Qd, a, p, N, seed, max_steps, time_budget_seconds, time_fn,
              multipliers_cache=None):
    """
    P: generator (base point). Qd: target = [k]P for the (unknown to the
    solver) k being recovered. Returns a RhoResult.

    multipliers_cache: optional dict keyed by id(P) (or any caller-supplied
    key) to reuse an already-screened multiplier set across the 16 seeds
    solved on the same curve (screening is a structural, per-curve
    property, not a per-seed one -- see build_validated_multipliers).
    """
    dp_bits = distinguished_point_bits(N)
    if multipliers_cache is not None and "mults" in multipliers_cache:
        mults = multipliers_cache["mults"]
        screen_attempts = multipliers_cache["attempts"]
        schedule_seed_used = multipliers_cache["schedule_seed"]
        screened_cycle_length = multipliers_cache["cycle_length"]
    else:
        mults, screen_attempts, screened_cycle_length = build_validated_multipliers(P, Qd, a, p, N)
        schedule_seed_used = MULTIPLIER_SCHEDULE_SEED + screen_attempts
        if multipliers_cache is not None:
            multipliers_cache["mults"] = mults
            multipliers_cache["attempts"] = screen_attempts
            multipliers_cache["schedule_seed"] = schedule_seed_used
            multipliers_cache["cycle_length"] = screened_cycle_length
    start_time = time_fn()
    total_group_ops = 0
    total_adds = 0
    total_doubles = 0
    restarts = 0

    rng = random.Random(seed)
    result = RhoResult()
    result.dp_bits = dp_bits
    result.multiplier_screen_attempts = screen_attempts
    result.multiplier_schedule_seed_used = schedule_seed_used
    result.screened_cycle_length = screened_cycle_length

    while True:
        u0 = rng.randrange(1, N)
        v0 = rng.randrange(1, N)
        X = ec_add_affine(
            ec_scalar_mult_affine(u0, P, a, p),
            ec_scalar_mult_affine(v0, Qd, a, p),
            a, p,
        )
        u, v = u0, v0
        dp_seen = {}
        steps = 0
        ctr = GroupOpCounter()
        while True:
            if X is None:
                # degenerate: point at infinity mid-walk; restart with a
                # fresh (u0, v0) rather than special-casing infinity steps.
                restarts += 1
                break
            steps += 1
            xi = X[0]
            part = partition_of(xi)
            if part == 0:
                X = ec_double_affine(X, a, p, ctr)
                u = (2 * u) % N
                v = (2 * v) % N
            else:
                s_j, t_j, M_j = mults[part]
                X = ec_add_affine(X, M_j, a, p, ctr)
                u = (u + s_j) % N
                v = (v + t_j) % N

            elapsed = time_fn() - start_time
            if elapsed > time_budget_seconds or steps + total_group_ops > max_steps:
                result.status = "censored"
                result.group_ops = total_group_ops + ctr.total
                result.adds = total_adds + ctr.adds
                result.doubles = total_doubles + ctr.doubles
                result.steps_at_cutoff = result.group_ops
                result.wall_seconds = elapsed
                result.restarts = restarts
                return result

            if X is not None and (X[0] % (1 << dp_bits)) == 0:
                key = X
                if key in dp_seen:
                    u2, v2 = dp_seen[key]
                    inv = modinv_general((v2 - v) % N, N)
                    if v == v2 or inv is None:
                        # degenerate collision (v == v2, or v2-v not
                        # invertible mod N): cannot solve for k from this
                        # pair; restart the whole walk with a fresh random
                        # start (recorded, never silently dropped).
                        restarts += 1
                        break
                    k = ((u - u2) * inv) % N
                    total_group_ops += ctr.total
                    total_adds += ctr.adds
                    total_doubles += ctr.doubles
                    result.status = "solved"
                    result.k = k
                    result.group_ops = total_group_ops
                    result.adds = total_adds
                    result.doubles = total_doubles
                    result.wall_seconds = time_fn() - start_time
                    result.restarts = restarts
                    return result
                else:
                    dp_seen[key] = (u, v)
        total_group_ops += ctr.total
        total_adds += ctr.adds
        total_doubles += ctr.doubles
