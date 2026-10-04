"""Independent reference reconstruction for EXP-CRYPTO-5e8beb.

This module is the independent checker required by the frozen specification
(`computation.independent_checker`) and the task handoff constraint:
"Producer dynamic programming and reference latent-path enumeration must use
separate code; reference cannot import producer kernel, DP or TV helpers."

Accordingly this module does **not** import `fixtures.py`, `kernels.py` or
`transcripts.py`. It re-derives, from the frozen specification text alone,
its own copies of:

  - the SHA256 rejection-shuffle partition generator,
  - the six kernel laws,
  - transition-row construction and pairwise TV,
  - full latent-path enumeration of (label, private-draw) sequences (rather
    than the producer's DP recursion), for both the real process and the
    representative-based simulator,
  - the persistent-control (assumption-trap) law.

A bug shared between this file and the producer modules would have to be an
independent transcription error made twice from the same specification text;
it would not be masked by a single shared helper.

Nothing in this module executes at import time, and calling these functions
against the fixed panel is scientific fixture evaluation reserved for a
later, separately authorized run (`maximum_runs: 0` in this task).
"""
from __future__ import annotations

import hashlib
import itertools
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

REFERENCE_EXP_ID = "EXP-CRYPTO-5e8beb"


# --- independent SHA256 rejection-shuffle reconstruction --------------------

def _reference_digest(N: int, q: int, seed: int, counter: int) -> int:
    payload = "%s|N=%d|q=%d|seed=%d|counter=%d" % (REFERENCE_EXP_ID, N, q, seed, counter)
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest(), byteorder="big")


def reference_generate_permutation(N: int, q: int, seed: int) -> List[int]:
    """Independent re-derivation of the Fisher-Yates SHA256 rejection shuffle."""
    perm = [i for i in range(N)]
    counter = 0
    i = N - 1
    while i >= 1:
        modulus = i + 1
        ceiling = (2 ** 256 // modulus) * modulus
        z = _reference_digest(N, q, seed, counter)
        counter += 1
        if z >= ceiling:
            continue
        j = z % modulus
        perm[i], perm[j] = perm[j], perm[i]
        i -= 1
    return perm


def reference_coordinate_cell_sizes(N: int, q: int) -> List[int]:
    sizes = [0 for _ in range(q)]
    for x in range(N):
        sizes[x % q] += 1
    return sizes


def reference_matched_feature(N: int, q: int, seed: int) -> Tuple[int, ...]:
    sizes = reference_coordinate_cell_sizes(N, q)
    perm = reference_generate_permutation(N, q, seed)
    feature = [-1 for _ in range(N)]
    cursor = 0
    for label in range(q):
        for _ in range(sizes[label]):
            feature[perm[cursor]] = label
            cursor += 1
    if cursor != N or any(v < 0 for v in feature):
        raise AssertionError("reference matched-feature construction did not cover every state")
    return tuple(feature)


def reference_coordinate_feature(N: int, q: int) -> Tuple[int, ...]:
    return tuple(x % q for x in range(N))


def reference_identity_feature(N: int) -> Tuple[int, ...]:
    return tuple(range(N))


def reference_constant_feature(N: int) -> Tuple[int, ...]:
    return tuple(0 for _ in range(N))


def reference_composite_feature(N: int, name: str) -> Tuple[int, ...]:
    if name == "mod3":
        return tuple(x % 3 for x in range(N))
    if name == "mod5":
        return tuple(x % 5 for x in range(N))
    if name == "identity":
        return reference_identity_feature(N)
    if name == "constant":
        return reference_constant_feature(N)
    raise KeyError(name)


def reference_partition_feature(kind: str, N: int, q=None, seed=None, name=None) -> Tuple[int, ...]:
    """One entry point mirroring every partition kind in the frozen panel."""
    if kind == "coordinate":
        return reference_coordinate_feature(N, q)
    if kind == "matched":
        return reference_matched_feature(N, q, seed)
    if kind == "identity":
        return reference_identity_feature(N)
    if kind == "constant":
        return reference_constant_feature(N)
    if kind in ("mod3", "mod5"):
        return reference_composite_feature(N, kind)
    raise KeyError(kind)


# --- independent literal kernel laws ----------------------------------------

def reference_raw_law(kernel_name: str, N: int) -> dict:
    """Independently re-typed literal laws (spec `kernels` block)."""
    if kernel_name == "R1":
        return {"labels": [0], "nu": {0: Fraction(1, 1)},
                "mu": {0: {-1: Fraction(1, 2), 1: Fraction(1, 2)}}}
    if kernel_name == "R2":
        return {"labels": [0], "nu": {0: Fraction(1, 1)},
                "mu": {0: {-1: Fraction(1, 4), 0: Fraction(2, 4), 1: Fraction(1, 4)}}}
    if kernel_name == "R3":
        return {"labels": [0], "nu": {0: Fraction(1, 1)},
                "mu": {0: {-1: Fraction(1, 4), 1: Fraction(3, 4)}}}
    if kernel_name == "R4":
        return {"labels": [0, 1], "nu": {0: Fraction(1, 2), 1: Fraction(1, 2)},
                "mu": {0: {-1: Fraction(1, 2), 1: Fraction(1, 2)},
                       1: {-2: Fraction(1, 2), 2: Fraction(1, 2)}}}
    if kernel_name == "P":
        labels = list(range(N))
        return {"labels": labels, "nu": {a: Fraction(1, N) for a in labels},
                "mu": {a: {a: Fraction(1, 1)} for a in labels}}
    if kernel_name == "U":
        return {"labels": [0], "nu": {0: Fraction(1, 1)},
                "mu": {0: {a: Fraction(1, N) for a in range(N)}}}
    raise KeyError(kernel_name)


def reference_reduce(mu_raw: Dict[int, Fraction], N: int) -> Dict[int, Fraction]:
    reduced: Dict[int, Fraction] = {}
    for delta, prob in mu_raw.items():
        residue = delta % N
        reduced[residue] = reduced.get(residue, Fraction(0)) + prob
    return {k: reduced[k] for k in sorted(reduced)}


def reference_law(kernel_name: str, N: int) -> dict:
    raw = reference_raw_law(kernel_name, N)
    return {
        "labels": list(raw["labels"]),
        "nu": dict(raw["nu"]),
        "mu": {label: reference_reduce(raw["mu"][label], N) for label in raw["labels"]},
    }


# --- independent transition rows and TV -------------------------------------

def reference_K_row(law: dict, N: int, feature: Sequence[int], x: int, l) -> Dict[int, Fraction]:
    row: Dict[int, Fraction] = {}
    for delta, prob in law["mu"][l].items():
        b = feature[(x + delta) % N]
        row[b] = row.get(b, Fraction(0)) + prob
    return row


def reference_tv(p: Dict[int, Fraction], q: Dict[int, Fraction]) -> Fraction:
    keys = set(p.keys()) | set(q.keys())
    acc = Fraction(0)
    for k in keys:
        acc += abs(p.get(k, Fraction(0)) - q.get(k, Fraction(0)))
    return acc / 2


def reference_fibers(feature: Sequence[int], N: int) -> Dict[int, List[int]]:
    fibers: Dict[int, List[int]] = {}
    for x in range(N):
        fibers.setdefault(feature[x], []).append(x)
    return fibers


def reference_same_fiber_pairs(feature: Sequence[int], N: int) -> List[Tuple[int, int]]:
    pairs = []
    for states in reference_fibers(feature, N).values():
        ordered = sorted(states)
        for a in range(len(ordered)):
            for b in range(a + 1, len(ordered)):
                pairs.append((ordered[a], ordered[b]))
    return sorted(pairs)


def reference_kernel_scores(kernel_name: str, N: int, feature: Sequence[int]) -> dict:
    """Independently recomputed delta_l / joint delta / per_operation_max."""
    law = reference_law(kernel_name, N)
    pairs = reference_same_fiber_pairs(feature, N)
    per_pair = []
    for x, xp in pairs:
        per_label = {
            l: reference_tv(
                reference_K_row(law, N, feature, x, l),
                reference_K_row(law, N, feature, xp, l),
            )
            for l in law["labels"]
        }
        joint = Fraction(0)
        for l in law["labels"]:
            joint += law["nu"][l] * per_label[l]
        per_pair.append({"x": x, "xp": xp, "per_label_tv": per_label, "joint_tv": joint})

    delta_l = {}
    for l in law["labels"]:
        delta_l[l] = max((row["per_label_tv"][l] for row in per_pair), default=Fraction(0))
    delta = max((row["joint_tv"] for row in per_pair), default=Fraction(0))
    per_operation_max = max(delta_l.values()) if delta_l else Fraction(0)
    return {
        "pairs": per_pair,
        "delta_l": delta_l,
        "delta": delta,
        "per_operation_max": per_operation_max,
    }


# --- independent latent-path enumeration (not a DP recursion) --------------

def _label_delta_choices(law: dict):
    """All (l, delta, probability) atomic one-step choices of this law."""
    choices = []
    for l in law["labels"]:
        for delta, prob in law["mu"][l].items():
            choices.append((l, delta, law["nu"][l] * prob))
    return choices


def reference_real_transcript_distribution(
    kernel_name: str, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Dict[tuple, Fraction]:
    """Enumerate every complete latent (l_1, a_1, ..., l_t, a_t) path directly
    (itertools.product over per-step choices) and accumulate transcript mass,
    per `computation.independent_checker`. No DP recursion is used.
    """
    law = reference_law(kernel_name, N)
    choices = _label_delta_choices(law)
    if horizon == 0:
        return {(feature[x0],): Fraction(1)}
    dist: Dict[tuple, Fraction] = {}
    for path in itertools.product(choices, repeat=horizon):
        prob = Fraction(1)
        x = x0
        steps = []
        for (l, delta, step_prob) in path:
            prob *= step_prob
            x = (x + delta) % N
            steps.append((l, feature[x]))
        if prob == 0:
            continue
        transcript = (feature[x0],) + tuple(steps)
        dist[transcript] = dist.get(transcript, Fraction(0)) + prob
    return dist


def reference_simulator_transcript_distribution(
    kernel_name: str, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Dict[tuple, Fraction]:
    """Enumerate latent paths for the representative-based simulator directly."""
    law = reference_law(kernel_name, N)
    choices = _label_delta_choices(law)
    fibers = reference_fibers(feature, N)
    b0 = feature[x0]
    if horizon == 0:
        return {(b0,): Fraction(1)}
    dist: Dict[tuple, Fraction] = {}
    for path in itertools.product(choices, repeat=horizon):
        prob = Fraction(1)
        c = b0
        steps = []
        for (l, delta, step_prob) in path:
            prob *= step_prob
            r = min(fibers[c])
            c = feature[(r + delta) % N]
            steps.append((l, c))
        if prob == 0:
            continue
        transcript = (b0,) + tuple(steps)
        dist[transcript] = dist.get(transcript, Fraction(0)) + prob
    return dist


def reference_full_transcript_tv(
    kernel_name: str, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Fraction:
    real = reference_real_transcript_distribution(kernel_name, N, feature, x0, horizon)
    sim = reference_simulator_transcript_distribution(kernel_name, N, feature, x0, horizon)
    return reference_tv(real, sim)


def reference_final_marginal_tv(
    kernel_name: str, N: int, feature: Sequence[int], x0: int, horizon: int
) -> Fraction:
    real = reference_real_transcript_distribution(kernel_name, N, feature, x0, horizon)
    sim = reference_simulator_transcript_distribution(kernel_name, N, feature, x0, horizon)

    def final_feature_marginal(dist):
        marg: Dict[int, Fraction] = {}
        for transcript, mass in dist.items():
            last = transcript[-1][1] if len(transcript) > 1 else transcript[0]
            marg[last] = marg.get(last, Fraction(0)) + mass
        return marg

    return reference_tv(final_feature_marginal(real), final_feature_marginal(sim))


# --- independent assumption-trap reconstruction -----------------------------

REFERENCE_TRAP_N = 11
REFERENCE_TRAP_HORIZON = 2
REFERENCE_TRAP_LABEL = 0


def reference_trap_real_distribution(x0: int) -> Dict[tuple, Fraction]:
    dist: Dict[tuple, Fraction] = {}
    for a in range(REFERENCE_TRAP_N):
        x1 = (x0 + a) % REFERENCE_TRAP_N
        x2 = (x0 + 2 * a) % REFERENCE_TRAP_N
        key = (x0, (REFERENCE_TRAP_LABEL, x1), (REFERENCE_TRAP_LABEL, x2))
        dist[key] = dist.get(key, Fraction(0)) + Fraction(1, REFERENCE_TRAP_N)
    return dist


def reference_trap_comparison_distribution(x0: int) -> Dict[tuple, Fraction]:
    dist: Dict[tuple, Fraction] = {}
    for a1, a2 in itertools.product(range(REFERENCE_TRAP_N), repeat=2):
        x1 = (x0 + a1) % REFERENCE_TRAP_N
        x2 = (x1 + a2) % REFERENCE_TRAP_N
        key = (x0, (REFERENCE_TRAP_LABEL, x1), (REFERENCE_TRAP_LABEL, x2))
        dist[key] = dist.get(key, Fraction(0)) + Fraction(1, REFERENCE_TRAP_N * REFERENCE_TRAP_N)
    return dist


def reference_trap_certificate(x0: int) -> dict:
    real = reference_trap_real_distribution(x0)
    comparison = reference_trap_comparison_distribution(x0)
    full_tv = reference_tv(real, comparison)

    def final_marg(dist):
        marg: Dict[int, Fraction] = {}
        for transcript, mass in dist.items():
            marg[transcript[-1][1]] = marg.get(transcript[-1][1], Fraction(0)) + mass
        return marg

    final_tv = reference_tv(final_marg(real), final_marg(comparison))
    return {
        "x0": x0,
        "real": real,
        "comparison": comparison,
        "full_transcript_tv": full_tv,
        "final_marginal_tv": final_tv,
        "classification": "bound_inapplicable",
    }


# --- agreement checking (used by driver.py, not evaluated by this task) ----

def agrees_exactly(producer_value, reference_value) -> bool:
    """No floating tolerances anywhere: exact equality only
    (spec `controls.independent_exact_tables`)."""
    return producer_value == reference_value
