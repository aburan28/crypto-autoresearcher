"""
EXP-PMA-001 deterministic instance-grid generation.

specification.yaml pins the reciprocal-minor formula (p_S = (t+1)/(t+d_S)),
the field list, the grid sizes (8 finite-field / 4 rational grid instances,
plus perturbed instances, plus a single allowed widening), and the exclusion
categories, but it does not pin literal numeric d_S values -- that is an
executor-level operational choice, analogous to a seed. This module states
that choice explicitly, once, and applies it identically to every field and
every stage; it is disclosed as a protocol-interpretation decision in
implementation.md, not silently assumed.

Rule (frozen for this execution, never adjusted after runs began):
  - NONEMPTY_SUBSETS gives a fixed canonical index 0..14 for the 15 nonempty
    subsets of {1,2,3,4} (see common.py).
  - "Parameter box" for a field = allowed_values, the deterministic list of
    candidate d_S values for that field (nonzero, != 1).
      * F_q (q in {3,5,7}): allowed_values = [2, 3, ..., q-1]. NOTE: F_3's
        box has exactly one element ({2}); every d_S in every F_3 instance
        is forced to 2, so every "prescribed table" over F_3 is numerically
        identical. This is a genuine executability tension in the frozen
        contract for the smallest field, not a defect introduced here; it
        is disclosed as an anomaly in implementation.md and the execution
        report, and F_3's grid is executed exactly as the (degenerate, but
        well-defined) single-table box dictates.
      * Q: allowed_values = [2, 3, ..., 46] (45 candidates), ample for
        within-instance distinctness across all 15 subsets.
  - Grid instance m (0-indexed) assigns d_S = allowed_values[(idx(S) + 5*m)
    % len(allowed_values)] for finite fields, or allowed_values[(idx(S) +
    15*m) % len(allowed_values)] for Q (using a coarser stride so the 15
    values of one instance stay pairwise distinct whenever the box is large
    enough, e.g. Q).
  - Perturbed candidate-obstruction instance m (0-indexed) uses a different
    deterministic stride: d_S = allowed_values[(2*idx(S) + 3 + 7*m) %
    len(allowed_values)] (finite fields) or (2*idx(S) + 7 + 11*m) (Q).
  - The single allowed widening fallback continues the same grid-instance
    formula at m = 8, 9, ..., 15 (finite fields) or m = 4..11 (Q).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from common import NONEMPTY_SUBSETS

Instance = Dict[Tuple[int, ...], int]


def allowed_values(field_label) -> List[int]:
    if field_label == "Q":
        return list(range(2, 47))
    q = field_label
    return list(range(2, q))


def grid_instance(field_label, m: int) -> Instance:
    box = allowed_values(field_label)
    stride = 15 if field_label == "Q" else 5
    return {S: box[(idx + stride * m) % len(box)] for idx, S in enumerate(NONEMPTY_SUBSETS)}


def perturbed_instance(field_label, m: int) -> Instance:
    box = allowed_values(field_label)
    base = 7 if field_label == "Q" else 3
    stride = 11 if field_label == "Q" else 7
    return {S: box[(2 * idx + base + stride * m) % len(box)] for idx, S in enumerate(NONEMPTY_SUBSETS)}


def widening_instance(field_label, m: int) -> Instance:
    """m continues the grid_instance numbering past the base grid (m=8.. for
    finite fields, m=4.. for Q), per the single-widening-fallback rule."""
    return grid_instance(field_label, m)


def degenerate_zero_q_fixture(field_label, target_pair=(1, 2)) -> Instance:
    """Forces q_{i,j} = 0 for target_pair by setting d_i = 1 (collapsing
    p_i to the constant 1) and d_ij = d_j (so p_i*p_j - p_ij = p_j - p_j =
    0 once p_i = 1 and d_ij = d_j make p_ij = p_j). All other subsets take
    harmless distinct box values so only the targeted degeneracy fires."""
    box = allowed_values(field_label)
    inst = {S: box[idx % len(box)] for idx, S in enumerate(NONEMPTY_SUBSETS)}
    i, j = target_pair
    inst[(i,)] = 1
    d_j = inst[(j,)]
    pair_key = tuple(sorted((i, j)))
    inst[pair_key] = d_j
    return inst


def exceptional_pole_collision_fixture(field_label, colliding=((1,), (2,))) -> Instance:
    """Sets two distinct subsets' d_S equal (pole collision), without
    forcing d=1 anywhere, isolating this exceptional-locus category from
    the q_ij=0 / cancellation-at-t=-1 category."""
    box = allowed_values(field_label)
    inst = {S: box[(idx + 1) % len(box)] for idx, S in enumerate(NONEMPTY_SUBSETS)}
    a, b = colliding
    inst[b] = inst[a]
    return inst


def find_zero_discriminant_fixture(field_label, domain, search_range=40):
    """Deterministic bounded search (first hit in a fixed scan order) for a
    prescribed instance where some anchor-triple Delta_ijk is identically
    zero after canonical reduction. Returns (instance, triple) or
    (None, None) if none is found within search_range attempts -- absence
    is reported honestly, not papered over."""
    from common import build_p_table, delta_ijk, ANCHOR_TRIPLES

    box = allowed_values(field_label)
    if len(box) == 0:
        return None, None
    for m in range(search_range):
        inst = {S: box[(idx + m) % len(box)] for idx, S in enumerate(NONEMPTY_SUBSETS)}
        p_table = build_p_table(inst, domain)
        for tri in ANCHOR_TRIPLES:
            D = delta_ijk(p_table, tri[0], tri[1], tri[2], domain).reduced()
            if D.is_zero():
                return inst, tri
    return None, None
