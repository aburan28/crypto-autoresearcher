"""Producer full-history transcript dynamic programming, simulator propagation
and the separately classified persistent-control (assumption-trap) law.

Producer-side module for EXP-CRYPTO-5e8beb. Two exact DP propagations:

  - `propagate_real`: the true joint distribution over (hidden state, full
    transcript), hidden state marginalized only *after* the transcript is
    retained (spec `computation.producer`).
  - `propagate_simulator`: the simulator's distribution over (current
    feature, full transcript), which replaces the true hidden state by its
    fiber representative at every step (spec `quantities.simulator`).

Plus the assumption trap (spec `assumption_trap`): a persistent hidden
translation A reused at both of two steps, which violates the freshness
premise and is tagged `bound_inapplicable`, never a counterexample.

Nothing here is invoked at import time or executed by this task
(`maximum_runs: 0`); these are pure functions for a later authorized run.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Sequence, Tuple

import fixtures
import kernels

Transcript = Tuple  # (b0, (l1, b1), (l2, b2), ..., (lt, bt))


# --- producer: real joint (hidden state, transcript) distribution -----------

def propagate_real(
    law: dict, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Dict[Tuple[int, Transcript], Fraction]:
    """Exact DP over (hidden_state, transcript) starting deterministically at
    x0 (spec `quantities.initial_states`: no averaging over starts).
    """
    init_transcript: Transcript = (feature[x0],)
    dist: Dict[Tuple[int, Transcript], Fraction] = {(x0, init_transcript): Fraction(1)}
    for _ in range(horizon):
        new_dist: Dict[Tuple[int, Transcript], Fraction] = {}
        for (h, transcript), mass in dist.items():
            for l in law["labels"]:
                p_l = law["nu"][l]
                if p_l == 0:
                    continue
                for delta, p_delta in law["mu"][l].items():
                    if p_delta == 0:
                        continue
                    nh = (h + delta) % N
                    nb = feature[nh]
                    nt = transcript + ((l, nb),)
                    key = (nh, nt)
                    new_dist[key] = new_dist.get(key, Fraction(0)) + mass * p_l * p_delta
        dist = new_dist
    return dist


def transcript_marginal(joint: Dict[Tuple[int, Transcript], Fraction]) -> Dict[Transcript, Fraction]:
    """Marginalize hidden state out of a (hidden_state, transcript) joint,
    performed only after the full transcript has been retained.
    """
    marg: Dict[Transcript, Fraction] = {}
    for (_, transcript), mass in joint.items():
        marg[transcript] = marg.get(transcript, Fraction(0)) + mass
    return marg


def final_feature_marginal(transcript_dist: Dict[Transcript, Fraction]) -> Dict[int, Fraction]:
    """Marginal over the final observed feature only (secondary metric
    `final_marginal_TV`). Explicitly distinct from the full joint transcript
    comparison used for the frozen coupling bound: final-marginal agreement
    is never a substitute for full-transcript agreement (spec
    `assumption_trap.exact_expected`).
    """
    result: Dict[int, Fraction] = {}
    for transcript, mass in transcript_dist.items():
        last = transcript[-1][1] if len(transcript) > 1 else transcript[0]
        result[last] = result.get(last, Fraction(0)) + mass
    return result


def real_transcript_distribution(
    law: dict, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Tuple[Dict[Tuple[int, Transcript], Fraction], Dict[Transcript, Fraction]]:
    joint = propagate_real(law, N, feature, x0, horizon)
    return joint, transcript_marginal(joint)


# --- simulator: distribution over (current feature, transcript) ------------

def propagate_simulator(
    law: dict, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Dict[Tuple[int, Transcript], Fraction]:
    """Simulator DP: at each step, replace the true hidden state by the fiber
    representative r_c = min fiber(c) of the current observed feature c
    (spec `quantities.simulator`), then apply the same fresh label/private law.
    """
    fibers = kernels.fibers_of(feature, N)
    b0 = feature[x0]
    init_transcript: Transcript = (b0,)
    dist: Dict[Tuple[int, Transcript], Fraction] = {(b0, init_transcript): Fraction(1)}
    for _ in range(horizon):
        new_dist: Dict[Tuple[int, Transcript], Fraction] = {}
        for (c, transcript), mass in dist.items():
            r = fixtures.representative(fibers[c])
            for l in law["labels"]:
                p_l = law["nu"][l]
                if p_l == 0:
                    continue
                for delta, p_delta in law["mu"][l].items():
                    if p_delta == 0:
                        continue
                    nb = feature[(r + delta) % N]
                    nt = transcript + ((l, nb),)
                    key = (nb, nt)
                    new_dist[key] = new_dist.get(key, Fraction(0)) + mass * p_l * p_delta
        dist = new_dist
    return dist


def simulator_transcript_distribution(
    law: dict, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Tuple[Dict[Tuple[int, Transcript], Fraction], Dict[Transcript, Fraction]]:
    joint = propagate_simulator(law, N, feature, x0, horizon)
    return joint, transcript_marginal(joint)


# --- bound evaluation (specification.quantities.bound) ----------------------

def coupling_bound(t: int, delta: Fraction) -> Fraction:
    """bound = min(1, t*delta), evaluated exactly."""
    return min(Fraction(1), t * delta)


def is_vacuous(bound: Fraction) -> bool:
    return bound >= 1


# --- assumption trap (specification.assumption_trap) ------------------------
# N=11, feature=identity, all 11 states, horizon=2. A single hidden
# translation A ~ Uniform{0,...,10} is drawn once and reused at both steps;
# the public label is 0 at both steps. This violates the freshness
# assumption central to the coupling bound and is explicitly out of that
# theorem's premise -- never treated as a counterexample to it.

TRAP_N = 11
TRAP_HORIZON = 2
TRAP_LABEL = 0


def trap_real_distribution(x0: int) -> Dict[Transcript, Fraction]:
    """Persistent-private trap process: real transcript distribution."""
    dist: Dict[Transcript, Fraction] = {}
    for a in range(TRAP_N):
        x1 = (x0 + a) % TRAP_N
        x2 = (x0 + 2 * a) % TRAP_N
        transcript: Transcript = (x0, (TRAP_LABEL, x1), (TRAP_LABEL, x2))
        dist[transcript] = dist.get(transcript, Fraction(0)) + Fraction(1, TRAP_N)
    return dist


def trap_comparison_distribution(x0: int) -> Dict[Transcript, Fraction]:
    """Comparison simulator: fresh-uniform U process (independent draws at
    each step) with the same initial feature, over the same two steps
    (spec `assumption_trap.comparison_simulator`).
    """
    dist: Dict[Transcript, Fraction] = {}
    for a1 in range(TRAP_N):
        x1 = (x0 + a1) % TRAP_N
        for a2 in range(TRAP_N):
            x2 = (x1 + a2) % TRAP_N
            transcript: Transcript = (x0, (TRAP_LABEL, x1), (TRAP_LABEL, x2))
            dist[transcript] = dist.get(transcript, Fraction(0)) + Fraction(1, TRAP_N * TRAP_N)
    return dist


def trap_final_marginal(dist: Dict[Transcript, Fraction]) -> Dict[int, Fraction]:
    """Marginal over the final identity feature value x2 only."""
    marg: Dict[int, Fraction] = {}
    for transcript, mass in dist.items():
        x2 = transcript[-1][1]
        marg[x2] = marg.get(x2, Fraction(0)) + mass
    return marg


@dataclass(frozen=True)
class TrapCertificate:
    x0: int
    real: Dict[Transcript, Fraction]
    comparison: Dict[Transcript, Fraction]
    full_transcript_tv: Fraction
    final_marginal_tv: Fraction
    classification: str  # always "bound_inapplicable"


def certify_trap(x0: int) -> TrapCertificate:
    real = trap_real_distribution(x0)
    comparison = trap_comparison_distribution(x0)
    full_tv = kernels.total_variation(real, comparison)
    real_marg = trap_final_marginal(real)
    comp_marg = trap_final_marginal(comparison)
    final_tv = kernels.total_variation(real_marg, comp_marg)
    return TrapCertificate(x0, real, comparison, full_tv, final_tv, "bound_inapplicable")


def certify_all_trap_starts() -> Dict[int, TrapCertificate]:
    """All 11 persistent-control starts (spec `fixed_counts.trap_full_transcript_checks`)."""
    return {x0: certify_trap(x0) for x0 in range(TRAP_N)}
