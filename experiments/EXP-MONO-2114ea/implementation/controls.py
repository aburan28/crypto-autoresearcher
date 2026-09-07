"""
Subgroup-coset controls for EXP-MONO-2114ea.

`subgroup_control` below is copied VERBATIM (byte-for-byte, comments
included) from experiments/EXP-MONO-c819ba/implementation/controls.py --
this contract's own frozen requirement (specification.yaml
`inputs.reused_subgroup_construction`) is to reuse that CORRECTED
subgroup-construction function exactly, not to reconstruct it from prose.
Do not modify it. `verify_subgroup_control_source_verbatim` below diffs
this copy against the c819ba source at run time, mirroring
EXP-MONO-b1423c's own implementation/run.py::verify_subgroup_control_source_verbatim.

Everything below the verbatim-copy marker is NEW to this contract: the
planted, graded, multi-curve subgroup-coset perturbation construction
(specification.yaml `inputs.planted_perturbation_construction`), used only
for Stage 2/3 (Stage 1 uses the RO3 cells' own already-reviewed reproduction
path, not this perturbation code).
"""
import os
import re


# ---- verbatim copy of EXP-MONO-c819ba/implementation/controls.py::subgroup_control ----
def subgroup_control(cs, k):
    """FB = H_k = {(a,b) in Z/n1 x Z/n2 : b == 0 mod k}, order n1*(n2/k) = N/k
    exactly. Requires k | n2. NOTE: the naive "image of scalar mult-by-k" (which
    has order N/gcd(k,N) only for CYCLIC groups) is WRONG here whenever E(F_p)
    is non-cyclic with even n1 (its kernel -- the full k-torsion -- is larger
    than gcd(k,N), so its image is smaller than N/k); this coordinate
    construction is exact regardless of cyclic/non-cyclic structure."""
    if cs.n2 % k != 0:
        return None, None
    h = cs.n1 * (cs.n2 // k)
    coords = [(a, b) for a in range(cs.n1) for b in range(0, cs.n2, k)]
    assert len(coords) == h
    return coords, h
# ---- end verbatim copy ----


def verify_subgroup_control_source_verbatim():
    """Confirm this file's copy of subgroup_control matches
    EXP-MONO-c819ba's own source verbatim (byte-for-byte), per this
    contract's `inputs.reused_subgroup_construction` requirement. Mirrors
    EXP-MONO-b1423c's own implementation/run.py::
    verify_subgroup_control_source_verbatim exactly."""
    src_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "EXP-MONO-c819ba", "implementation", "controls.py"))
    with open(src_path) as f:
        src = f.read()
    m = re.search(r"def subgroup_control.*?return coords, h\n", src, re.S)
    orig = m.group(0)
    here_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls.py")
    with open(here_path) as f:
        mine = f.read()
    m2 = re.search(r"def subgroup_control.*?return coords, h\n", mine, re.S)
    mine_func = m2.group(0)
    return orig == mine_func, src_path


# ============================================================================
# NEW: planted, graded, multi-curve subgroup-coset perturbation construction.
# specification.yaml `inputs.planted_perturbation_construction`.
# ============================================================================

def smallest_admissible_subgroup_index(cs):
    """Smallest integer k>=2 with k | cs.n2 -- the subgroup of SMALLEST INDEX
    h>1 (in the "index" sense: H_k has order N/k, i.e. index k in E(F_p))
    that cs.n2 admits via `subgroup_control`, per
    `planted_perturbation_construction`'s "choosing the subgroup of the
    smallest index h>1 that the curve's own N admits". Raises
    ConstructionFailure-style ValueError if cs.n2 has no divisor in
    [2, cs.n2] other than itself trivially satisfied (n2>=2 always admits
    k=n2 at worst, so this only fails when n2==1)."""
    if cs.n2 < 2:
        raise ValueError(f"n2={cs.n2} admits no subgroup of index>1 (n2<2)")
    k = 2
    while k <= cs.n2:
        if cs.n2 % k == 0:
            return k
        k += 1
    raise ValueError(f"no divisor of n2={cs.n2} found in [2,{cs.n2}] (unreachable)")


def fixed_coset_for_curve(cs):
    """The ONE fixed proper-subgroup coset used for this curve's own planted
    perturbation: the subgroup H_k itself (the trivial/identity coset of
    H_k), where k is the smallest admissible index per
    `smallest_admissible_subgroup_index`. Disclosed choice (see
    implementation.md): using H_k itself (rather than a shifted coset gH_k)
    is the simplest well-defined choice and keeps the exact closed-form
    spectrum identity (Shat(chi)=h on the annihilator of H, 0 elsewhere,
    H-MONO-663fb4 mechanism step (5)) directly applicable without an extra
    character-twist factor; a shifted coset would have identical |Shat|
    magnitude (hence identical C, Var) since |chi(g)|=1 for every character,
    so this choice does not narrow the tested effect-size grid in any way
    that a shifted coset would have avoided.
    Returns (coset_coords, k, h_size)."""
    k = smallest_admissible_subgroup_index(cs)
    coords, h_size = subgroup_control(cs, k)
    if coords is None:
        raise ValueError(f"subgroup_control(cs,{k}) returned None despite k|n2 check")
    return coords, k, h_size


def _negate_coord(c, n1, n2):
    a, b = c
    return ((-a) % n1, (-b) % n2)


def take_symmetric_prefix(ordered_coords, count, n1, n2):
    """Scan `ordered_coords` (a fixed, disclosed order) and greedily select
    a SYMMETRIC (closed under negation) prefix of exactly `count` elements,
    taking +/- pairs together and a self-negating (2-torsion, or (0,0))
    element only when it is the exact remaining odd slot -- the same
    deterministic-selection discipline EXP-MONO-b1423c's own
    `draw_symmetric_null_subset` uses for RANDOM draws, applied here to a
    FIXED prefix scan instead. `ordered_coords` must not contain
    duplicates. Raises ValueError if the scan is exhausted before reaching
    `count` (a curve/fraction combination for which this occurs is reported
    as `failed_infrastructure`, not silently truncated)."""
    chosen = []
    chosen_set = set()
    skipped_self_negating = []
    i = 0
    n = len(ordered_coords)
    candidate_set = set(ordered_coords)
    while len(chosen) < count:
        if i >= n:
            # second pass: only self-negating elements skipped earlier remain
            # eligible for the final odd slot.
            progressed = False
            for c in skipped_self_negating:
                if c not in chosen_set and count - len(chosen) == 1:
                    chosen.append(c)
                    chosen_set.add(c)
                    progressed = True
                    break
            if not progressed:
                raise ValueError(
                    f"take_symmetric_prefix: exhausted {n} candidates, "
                    f"reached {len(chosen)}/{count}")
            continue
        c = ordered_coords[i]
        i += 1
        if c in chosen_set:
            continue
        neg = _negate_coord(c, n1, n2)
        if neg == c:
            if count - len(chosen) == 1:
                chosen.append(c)
                chosen_set.add(c)
            else:
                skipped_self_negating.append(c)
            continue
        if neg not in candidate_set:
            # neg not present in the candidate list at all: cannot pair here.
            continue
        if len(chosen) + 2 > count:
            continue
        chosen.append(c)
        chosen.append(neg)
        chosen_set.add(c)
        chosen_set.add(neg)
    return chosen


def _has_self_negating(coords, n1, n2):
    return any(_negate_coord(c, n1, n2) == c for c in coords)


def construct_perturbed_factor_base(cs, fb_coords_orig, coset_coords, r):
    """specification.yaml `inputs.planted_perturbation_construction`: replace
    round(r * F) elements of `fb_coords_orig` (the curve's own real
    x-coordinate factor base, in coordinate space, in its own disclosed
    construction order) with that many elements of `coset_coords` (the
    fixed subgroup coset) NOT already in the factor base, preserving
    symmetry by construction (swap in +/- pairs / the exact odd
    self-negating slot on both the removed and added sides).

    DISCLOSED PRE-RUN ENGINEERING DECISION (implementation.md): round(r*F)
    can be ODD with NO self-negating (2-torsion or (0,0)) candidate
    available in either the removal side (fb_coords_orig) or the addition
    side (coset elements not already in the factor base) at these toy
    curve sizes -- an odd symmetric swap is then genuinely impossible.
    When this occurs, the requested count is decremented by 1 to the
    nearest EVEN number, identical in spirit to this lane's own
    `primary_F_of` convention ("F=N/4, forced even so a symmetric-subset
    prefix... stays exactly symmetric"). This is decided BEFORE any
    Stage-2/3 number is observed (a pure parity/feasibility check on the
    swap-candidate lists, not on any measured statistic), so it is not a
    post-hoc protocol change under `invalidation_rules`.

    Returns dict with perturbed_coords (list), removed (list), added
    (list), count (int, the count ACTUALLY used), count_requested_raw,
    count_parity_adjusted (bool), F (len(fb_coords_orig), preserved)."""
    F = len(fb_coords_orig)
    count_requested_raw = round(r * F)
    fb_set = set(fb_coords_orig)
    coset_not_in_fb = [c for c in coset_coords if c not in fb_set]

    count = count_requested_raw
    parity_adjusted = False
    if count % 2 == 1:
        removal_has_self_neg = _has_self_negating(fb_coords_orig, cs.n1, cs.n2)
        addition_has_self_neg = _has_self_negating(coset_not_in_fb, cs.n1, cs.n2)
        if not (removal_has_self_neg and addition_has_self_neg):
            count = count - 1
            parity_adjusted = True

    removed = take_symmetric_prefix(fb_coords_orig, count, cs.n1, cs.n2)
    added = take_symmetric_prefix(coset_not_in_fb, count, cs.n1, cs.n2)
    removed_set = set(removed)
    added_set = set(added)
    perturbed = [c for c in fb_coords_orig if c not in removed_set] + added
    assert len(perturbed) == F, f"perturbed size {len(perturbed)} != original F={F}"
    assert len(set(perturbed)) == F, "perturbed factor base contains duplicates"
    return {
        "perturbed_coords": perturbed,
        "removed": removed,
        "added": added,
        "count": count,
        "count_requested_raw": count_requested_raw,
        "count_parity_adjusted": parity_adjusted,
        "F": F,
        "fraction_requested": r,
    }
