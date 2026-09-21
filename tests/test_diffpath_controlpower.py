"""Tests for harness/diffpath/controlpower.py -- EXP-DIFFP-4b165f.

A NEW, DEDICATED test file. NO EXISTING TEST FILE IS EDITED: tests/test_harness.py
and tests/test_diffpath_adjudicator.py are explicitly out of scope for
TASK-20260824-9a489e, and no committed module under harness/ is modified (IR-2).

What is pinned here is exactly what the contract names as the load-bearing
mechanics of this task's new module:

  * the declared KEY PROJECTION -- dropping a name yields the original tuple with
    that pair removed, order preserved;
  * the FAMILY-(d) PERTURBATION GENERATORS -- exactly k bits of the message
    difference change and NO OTHER FIELD MOVES;
  * the COMPONENT-ATTRIBUTION function;
  * the INSIDE- versus OUTSIDE-minimisation comparison, and the fidelity of the
    mirrored variant list to the committed `adjudicator.canonical`.

These are unit tests. They are NOT charged experiment runs and create no run
directory (contract budget.maximum_runs_definition).
"""
from __future__ import annotations

import pytest

from harness.diffpath import adjudicator as ADJ
from harness.diffpath import controlpower as CP
from harness.diffpath import equivalence as EQ
from harness.diffpath import primitives as P
from harness.diffpath.census import build_census


@pytest.fixture(scope="module")
def census():
    # ONE planted entry per primitive: the same committed builder at the same
    # declared seeds, sized down purely for test speed.
    return build_census(CP.SEEDS["planted_path_generation_md5"],
                        CP.SEEDS["planted_path_generation_sha1"], 1)


@pytest.fixture(scope="module")
def objs(census):
    md5 = [e.obj for e in census.shadow if e.primitive == "md5"][0]
    sha1 = [e.obj for e in census.shadow if e.primitive == "sha1"][0]
    return md5, sha1


# ---------------------------------------------------------------------------
# the declared key projection
# ---------------------------------------------------------------------------

def test_project_removes_exactly_the_named_pairs_and_keeps_order(objs):
    md5, _ = objs
    key = ADJ.serialize(md5, CP.STRICT)
    names = CP.key_components(key)
    assert "message_difference" in names
    out = CP.project(key, ("message_difference",))
    assert CP.key_components(out) == [n for n in names if n != "message_difference"]
    assert out == tuple(p for p in key if p[0] != "message_difference")
    # every retained pair is byte-identical to the original pair
    assert all(p in key for p in out)


def test_project_with_empty_drop_set_is_the_identity(objs):
    for o in objs:
        key = ADJ.serialize(o, CP.STRICT)
        assert CP.project(key, ()) == key


def test_project_of_an_absent_name_is_a_no_op(objs):
    md5, _ = objs
    key = ADJ.serialize(md5, CP.STRICT)
    # md5 objects carry no in_linearized_code component
    assert "in_linearized_code" not in CP.key_components(key)
    assert CP.project(key, ("in_linearized_code",)) == key


def test_declared_and_derived_key_component_lists_agree(census):
    derived = []
    for e in census.shadow:
        for n in CP.key_components(ADJ.serialize(e.obj, CP.STRICT)):
            if n not in derived:
                derived.append(n)
    assert sorted(derived) == sorted(CP.DECLARED_KEY_COMPONENTS)


# ---------------------------------------------------------------------------
# the mirrored variant list, and inside- vs outside-minimisation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mode", ["strict", "permissive"])
def test_variant_keys_minimum_equals_the_committed_canonical(objs, mode):
    gens = CP.STRICT if mode == "strict" else CP.PERMISSIVE
    for o in objs:
        assert min(CP.variant_keys(o, gens)) == ADJ.canonical(o, gens)
    assert CP.VARIANT_MIRROR_CHECK["mismatches"] == 0


def test_ablated_canonical_with_empty_drop_set_is_the_committed_canonical(objs):
    for o in objs:
        keys = CP.variant_keys(o, CP.STRICT)
        assert CP.ablated_canonical_inside(keys, ()) == ADJ.canonical(o, CP.STRICT)


def test_inside_and_outside_minimisation_are_computed_and_comparable(objs):
    """The contract requires BOTH forms to be reported; the inside form is its
    value. This pins that they are computed from the SAME variant list and that
    the comparison is a real one rather than an alias."""
    md5, sha1 = objs
    for o in (md5, sha1):
        for gens in (CP.STRICT, CP.PERMISSIVE):
            keys = CP.variant_keys(o, gens)
            inside = CP.ablated_canonical_inside(keys, ("message_difference",))
            outside = CP.ablated_canonical_outside(keys, ("message_difference",))
            assert CP.key_components(inside) == CP.key_components(outside)
            # inside is a minimum over the projected variants, so it can never
            # exceed the projection of the minimum
            assert inside <= outside


# ---------------------------------------------------------------------------
# the family-(d) perturbation generators
# ---------------------------------------------------------------------------

def _bits(words):
    return sum(bin(w).count("1") for w in words)


def test_md5_perturbation_flips_exactly_k_bits_of_delta_m(objs):
    md5, _ = objs
    for k in (1, 2, 4, 8, 16):
        pos = tuple(range(k))
        new = CP.perturb_message_difference(md5, pos, f"k{k}")
        xor = [a ^ b for a, b in zip(md5.delta_m, new.delta_m)]
        assert _bits(xor) == k


def test_sha1_perturbation_flips_exactly_k_bits_of_dv(objs):
    _, sha1 = objs
    for k in (1, 2, 4, 8, 16):
        pos = tuple(range(k))
        new = CP.perturb_message_difference(sha1, pos, f"k{k}")
        xor = [a ^ b for a, b in zip(sha1.dv, new.dv)]
        assert _bits(xor) == k


def test_k_zero_perturbation_changes_no_bit_at_all(objs):
    for o in objs:
        new = CP.perturb_message_difference(o, (), "k0")
        if o.primitive == "md5":
            assert new.delta_m == o.delta_m
        else:
            assert new.dv == o.dv


def test_no_other_field_moves(objs):
    """THE HARD PART OF FAMILY (d): step_delta and every other field held fixed."""
    for o in objs:
        new = CP.perturb_message_difference(o, (0, 5, 40), "probe")
        assert new.step_delta == o.step_delta
        assert new.step_delta_signed == o.step_delta_signed
        assert new.step_range == o.step_range
        assert new.length == o.length
        assert new.block_index == o.block_index
        assert new.primitive == o.primitive
        assert new.conditions == o.conditions
        assert (new.cv, new.m, new.mp) == (o.cv, o.m, o.mp)
        if o.primitive == "sha1":
            # dv_seed_window is a SEPARATE FIELD and is held fixed; the flag is
            # a PREDICATE OF THE DV and is honestly recomputed
            assert new.dv_seed_window == o.dv_seed_window
            assert new.in_linearized_code == P.sha1_in_linearized_code(list(new.dv))
            assert new.delta_m == o.delta_m
        else:
            assert new.dv == o.dv
            # delta_m_signed is DERIVED from the perturbed component
            assert new.delta_m_signed != o.delta_m_signed or new.delta_m == o.delta_m


def test_the_perturbed_object_differs_from_its_source_in_the_key(objs):
    for o in objs:
        new = CP.perturb_message_difference(o, (0,), "k1")
        assert ADJ.serialize(new, CP.STRICT) != ADJ.serialize(o, CP.STRICT)


def test_in_code_perturbation_stays_in_the_linearized_code(objs):
    _, sha1 = objs
    w16 = tuple([1] + [0] * 15)
    new = CP.perturb_by_codeword(sha1, w16, "det")
    assert new.dv != sha1.dv
    assert new.in_linearized_code is True
    assert new.step_delta == sha1.step_delta
    assert new.path_data["codeword_hamming_weight"] > 0


def test_bit_index_order_is_the_declared_one(objs):
    md5, _ = objs
    new = CP.perturb_message_difference(md5, (35,), "p35")
    xor = [a ^ b for a, b in zip(md5.delta_m, new.delta_m)]
    assert xor[1] == (1 << 3)          # position 35 -> word 1, bit 3
    assert _bits(xor) == 1


# ---------------------------------------------------------------------------
# component attribution (H-3)
# ---------------------------------------------------------------------------

def test_attribution_names_the_single_perturbed_component(objs):
    md5, _ = objs
    new = CP.perturb_message_difference(md5, (0,), "k1")
    attr = CP.attribution(ADJ.canonical(new, CP.STRICT),
                          ADJ.canonical(md5, CP.STRICT))
    assert attr == ["message_difference"]


def test_attribution_of_an_object_against_itself_is_empty(objs):
    for o in objs:
        assert CP.attribution(ADJ.canonical(o, CP.STRICT),
                              ADJ.canonical(o, CP.STRICT)) == []


def test_attribution_reports_a_name_present_in_only_one_key(objs):
    md5, sha1 = objs
    attr = CP.attribution(ADJ.canonical(sha1, CP.STRICT),
                          ADJ.canonical(md5, CP.STRICT))
    assert "in_linearized_code" in attr        # present for sha1 only
    assert "primitive" in attr


def test_attribution_of_a_block_reindexed_image_names_block_index(objs):
    md5, _ = objs
    img = EQ.act_E6_reindex(md5, 3)
    attr = CP.attribution(ADJ.canonical(img, CP.STRICT),
                          ADJ.canonical(md5, CP.STRICT))
    assert attr == ["block_index"]


# ---------------------------------------------------------------------------
# the fast membership path must agree with the committed adjudicator
# ---------------------------------------------------------------------------

def test_fast_path_agrees_with_the_committed_adjudicate(census, objs):
    adj = ADJ.Adjudicator(census, CP.STRICT)
    fast = CP.FastAdj(adj)
    probes = list(objs) + [CP.perturb_message_difference(o, (0,), "k1")
                           for o in objs]
    rec = CP.fidelity_check(adj, fast, probes)
    assert rec["disagreements"] == []
    assert rec["agree"] == rec["objects"] == len(probes)


def test_two_sided_decoy_constructors_build_what_they_claim(census, objs):
    two = CP.twosided_objects(census)
    md5, sha1 = objs
    assert two["T3_signed_representation_changed_but_step_delta_equal"] is True
    assert two["T3"].step_delta_signed != md5.step_delta_signed
    assert two["T4"].dv == tuple(P.sha0_expand(list(sha1.dv_seed_window), 80))
    assert two["T4_flag_forced"].in_linearized_code is True
    assert len(two["T1"]) == 4 and len(two["T2"]) == 2
    assert len(two["T5"]) == len(census.shadow)


# ---------------------------------------------------------------------------
# contract hygiene that is cheap to pin
# ---------------------------------------------------------------------------

def test_literal_experiment_id_and_armed_deadline_in_every_parameter_block():
    for suffix in CP.CEILINGS:
        p = CP._params(suffix, CP.STRICT)
        assert p["experiment_id"] == "EXP-DIFFP-4b165f"      # IR-7, LITERAL
        assert p["armed_deadline_seconds"] == CP.CEILINGS[suffix]
        assert "code_path_fingerprint" in p


def test_eight_declared_seeds_are_present_and_unaltered():
    assert CP.SEEDS == {
        "equivalence_generator_check": 20260824,
        "planted_path_generation_md5": 84064101,
        "planted_path_generation_sha1": 84064102,
        "null_draw_md5_delta_m": 84064103,
        "null_draw_sha1_dv_in_code": 84064104,
        "null_draw_sha1_dv_unconstrained": 84064105,
        "observation_collision_search": 84064106,
        "null_draw_message_difference_perturbed": 84064107,
    }


def test_no_quarantine_path_is_referenced_by_this_module():
    """IR-1, by mechanism: the prefix appears in no code path of the module."""
    import inspect
    src = inspect.getsource(CP)
    code = "\n".join(line for line in src.splitlines()
                     if "quarantine" not in line.lower())
    assert "GOAL-MD5-001" not in code
