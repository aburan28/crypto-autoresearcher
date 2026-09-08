"""Exact fresh-kernel transition rows and same-fiber pair TV certificates.

Producer-side module for EXP-CRYPTO-5e8beb. Builds K_l(x, b) transition rows
from the literal laws in `fixtures.py`, and computes exact rational
same-fiber pair total-variation certificates, distinguishing:

  - `delta_l` (per-label maximum same-fiber pair TV, spec `quantities.delta_l`)
  - `delta`   (joint one-step TV, maximum over pairs of the nu-weighted sum
              of per-label TVs across the kernel's own labels -- spec
              `quantities.delta`, explicitly NOT `sum_l nu(l)*delta_l`)
  - `per_operation_max` (max_l delta_l, spec `quantities.per_operation_max`)

All arithmetic is exact `fractions.Fraction`; no floating point is used
anywhere in this module. Nothing here is invoked at import time, and calling
these functions on the fixed 272-partition panel is scientific fixture
evaluation reserved for a later, separately authorized run -- this task
(`maximum_runs: 0`) only defines the functions.

Spec cross-reference:
  - `kernels.common_law`, `kernels.translation_order` -> reduce_law, build_K.
  - `quantities.K`, `quantities.delta_l`, `quantities.delta`,
    `quantities.per_operation_max`, `quantities.TV`, `quantities.maximizer_ties`
    -> total_variation, PairCertificate, KernelCertificate, certify_kernel.
  - `controls.public_prime_rigidity`, `controls.hidden_uniform` are exact
    consequences of this generic machinery, not special-cased here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import fixtures


# --- translation reduction (specification.kernels.translation_order) -------

def reduce_law(raw_mu_for_label: Dict[int, Fraction], N: int) -> Dict[int, Fraction]:
    """Reduce a raw {signed_delta: Fraction} law to ascending residues mod N,
    combining exact masses of any translations that collide after reduction.
    """
    reduced: Dict[int, Fraction] = {}
    for delta, prob in raw_mu_for_label.items():
        r = delta % N
        reduced[r] = reduced.get(r, Fraction(0)) + prob
    return dict(sorted(reduced.items()))


def reduced_law(kernel_name: str, N: int) -> dict:
    """Full law for a kernel at a given N, with every label's mu reduced mod N."""
    raw = fixtures.raw_law_for(kernel_name, N)
    mu = {label: reduce_law(raw["mu"][label], N) for label in raw["labels"]}
    return {"labels": list(raw["labels"]), "nu": dict(raw["nu"]), "mu": mu}


# --- transition rows K_l(x, b) ----------------------------------------------

def build_K(law: dict, N: int, feature: Sequence[int]) -> Dict[int, Dict[int, Dict[int, Fraction]]]:
    """K[x][l][b] = sum_{delta: v(x+delta)=b} mu_l(delta), for every state x."""
    K: Dict[int, Dict[int, Dict[int, Fraction]]] = {}
    for x in range(N):
        K[x] = {}
        for l in law["labels"]:
            row: Dict[int, Fraction] = {}
            for delta, prob in law["mu"][l].items():
                nxt = (x + delta) % N
                b = feature[nxt]
                row[b] = row.get(b, Fraction(0)) + prob
            K[x][l] = row
    return K


# --- exact total variation ---------------------------------------------------

def total_variation(p: Dict[int, Fraction], q: Dict[int, Fraction]) -> Fraction:
    """Half the exact sum of absolute mass differences over the union of outcomes."""
    outcomes = set(p) | set(q)
    total = sum(abs(p.get(o, Fraction(0)) - q.get(o, Fraction(0))) for o in outcomes)
    return Fraction(total) / 2


# --- fibers and same-fiber pairs ---------------------------------------------

def fibers_of(feature: Sequence[int], N: int) -> Dict[int, List[int]]:
    fibers: Dict[int, List[int]] = {}
    for x in range(N):
        fibers.setdefault(feature[x], []).append(x)
    return fibers


def same_fiber_pairs(feature: Sequence[int], N: int) -> List[Tuple[int, int]]:
    """All unordered same-fiber pairs x<x', across all labels, globally
    ascending in (x, x') so that a plain scan already yields the
    lexicographically least maximizer when ties are broken by first-seen.
    We still re-sort explicitly to not depend on fiber enumeration order.
    """
    pairs: List[Tuple[int, int]] = []
    for _, states in fibers_of(feature, N).items():
        states = sorted(states)
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                pairs.append((states[i], states[j]))
    pairs.sort()
    return pairs


# --- pair and kernel certificates -------------------------------------------

@dataclass(frozen=True)
class PairCertificate:
    x: int
    xp: int
    per_label_tv: Dict[int, Fraction]
    joint_tv: Fraction


def maximizer_witness(
    certs: Sequence[PairCertificate],
    value_of,
    max_value: Fraction,
) -> Optional[Tuple[int, int]]:
    """Lexicographically least pair among all exact maximizers of value_of(cert).
    Empty candidate set (no same-fiber pairs, or none reaching max_value) is a
    null witness, per `quantities.maximizer_ties`.
    """
    candidates = [(c.x, c.xp) for c in certs if value_of(c) == max_value]
    if not candidates:
        return None
    return min(candidates)


@dataclass(frozen=True)
class KernelCertificate:
    kernel_name: str
    pair_certs: Tuple[PairCertificate, ...]
    delta_l: Dict[int, Fraction]                       # per-label max same-fiber TV
    delta_l_witness: Dict[int, Optional[Tuple[int, int]]]
    delta: Fraction                                    # joint one-step TV (max over pairs)
    delta_witness: Optional[Tuple[int, int]]
    per_operation_max: Fraction                         # max_l delta_l
    per_operation_max_label: Optional[int]


def certify_kernel(kernel_name: str, N: int, feature: Sequence[int]) -> KernelCertificate:
    """Compute every same-fiber pair TV certificate for one (kernel, partition)
    and the derived delta_l / joint delta / per_operation_max quantities.

    Distinct from a naive `sum_l nu(l)*delta_l`: `delta` maximizes the
    nu-weighted sum of per-label TVs *pair by pair* (spec `quantities.delta`).
    """
    law = reduced_law(kernel_name, N)
    K = build_K(law, N, feature)
    pairs = same_fiber_pairs(feature, N)

    pair_certs: List[PairCertificate] = []
    for x, xp in pairs:
        per_label_tv = {l: total_variation(K[x][l], K[xp][l]) for l in law["labels"]}
        joint_tv = sum((law["nu"][l] * per_label_tv[l] for l in law["labels"]), Fraction(0))
        pair_certs.append(PairCertificate(x, xp, per_label_tv, joint_tv))

    delta_l: Dict[int, Fraction] = {}
    delta_l_witness: Dict[int, Optional[Tuple[int, int]]] = {}
    for l in law["labels"]:
        if pair_certs:
            m = max(c.per_label_tv[l] for c in pair_certs)
        else:
            m = Fraction(0)
        delta_l[l] = m
        delta_l_witness[l] = maximizer_witness(pair_certs, lambda c, l=l: c.per_label_tv[l], m)

    if pair_certs:
        delta = max(c.joint_tv for c in pair_certs)
    else:
        delta = Fraction(0)
    delta_witness = maximizer_witness(pair_certs, lambda c: c.joint_tv, delta)

    if delta_l:
        per_operation_max = max(delta_l.values())
        per_operation_max_label = min(l for l, v in delta_l.items() if v == per_operation_max)
    else:
        per_operation_max = Fraction(0)
        per_operation_max_label = None

    return KernelCertificate(
        kernel_name=kernel_name,
        pair_certs=tuple(pair_certs),
        delta_l=delta_l,
        delta_l_witness=delta_l_witness,
        delta=delta,
        delta_witness=delta_witness,
        per_operation_max=per_operation_max,
        per_operation_max_label=per_operation_max_label,
    )


def certify_all_kernels(N: int, feature: Sequence[int]) -> Dict[str, KernelCertificate]:
    """certify_kernel for all six declared kernels, in `fixtures.KERNEL_ORDER`."""
    return {name: certify_kernel(name, N, feature) for name in fixtures.KERNEL_ORDER}
