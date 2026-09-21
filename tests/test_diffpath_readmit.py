"""Tests for harness/diffpath/readmit.py -- EXP-DIFFP-f26790, TASK-20260826-82c660.

A NEW DEDICATED TEST FILE. NO EXISTING TEST FILE IS EDITED (required_artifacts).

WHAT THESE TESTS ARE AND ARE NOT. They check that the per-instrument forcing
predicate implemented from the contract's STATEMENT behaves as the statement
says on cases whose answer is derivable from the statement plus the committed
edge records; that the consistent-pair gate is two-sided; and that the counting
rule reaches both extremes through the two degenerate instruments. THEY CHECK NO
CRYPTOGRAPHIC CLAIM OF ANY KIND. NO PATH IS CLAIMED NEW FOR MD5 OR SHA-1 AND NO
TEST HERE IS EVIDENCE ABOUT EITHER DIFFERENCE SPACE.
"""
import os

import pytest

from harness.diffpath import census as CEN
from harness.diffpath import controlpower as CP
from harness.diffpath import depgraph as DG
from harness.diffpath import readmit as RM


@pytest.fixture(scope="module")
def sub():
    """The committed substrate, behind this contract's own firewalls."""
    RM.install_independence_and_quarantine_firewall()
    census = CEN.build_census(RM.SEEDS["planted_path_generation_md5"],
                              RM.SEEDS["planted_path_generation_sha1"],
                              scan={"candidates": []})
    comps = RM.derive_key_components(census)
    components = comps["derived_union_in_first_appearance_order"]
    key_names = {p: set(v) for p, v in comps["derived_per_primitive"].items()}
    rep = {}
    for e in census.shadow:
        rep.setdefault(e.primitive, RM._serialised_key(e.obj))
    pop = DG.declared_population(census)
    edges = {p: DG.edge_records(pop["objects"][p], p, components)
             for p in ("md5", "sha1")}
    rt = RM.load_reused_O_E()
    return {"census": census, "components": components, "comps": comps,
            "key_names": key_names, "rep": rep, "edges": edges,
            "instruments": RM.build_instruments(rt), "rt": rt}


# ---------------------------------------------------------------------------
# IR-13 -- the key component list is DERIVED, never hard-coded
# ---------------------------------------------------------------------------

def test_key_components_are_derived_and_match_the_contracts_six_names(sub):
    c = sub["comps"]
    assert c["agrees_with_contract_as_a_set"], (
        "IR-13 STOP: the run-time-derived strict key component list differs "
        "from the contract's six names; that is a finding about the contract")
    assert set(c["derived_per_primitive"]["md5"]) == {
        "primitive", "length", "message_difference", "step_delta", "block_index"}
    assert "in_linearized_code" in c["derived_per_primitive"]["sha1"]
    assert all(c["name_list_is_constant_within_each_primitive"].values())


# ---------------------------------------------------------------------------
# the forcing predicate against the IDENTITY instrument (CTL-FORCE-PI side A)
# ---------------------------------------------------------------------------

def _force(sub, deleted, prim, iname, order):
    return RM.forcing_edges_for(deleted, prim,
                                sub["instruments"][iname]["projection"],
                                order, sub["key_names"], sub["rep"],
                                sub["edges"])


@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_identity_forces_the_length_row_on_both_primitives(sub, order):
    """The statement: a retained d with a derivation-backed edge d -> length."""
    for prim in ("md5", "sha1"):
        ev = _force(sub, "length", prim, "honest", order)
        assert ev["forced_literal_edge_only"], (prim, ev)
        assert all(e["edge_label"] == "derived_and_witnessed"
                   for e in ev["forcing_edges"])
        assert "step_delta" in {e["X"] for e in ev["forcing_edges"]}


@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_identity_forces_the_flag_row_on_sha1_by_the_message_difference_edge(
        sub, order):
    ev = _force(sub, "in_linearized_code", "sha1", "honest", order)
    assert ev["forced_literal_edge_only"]
    assert {e["X"] for e in ev["forcing_edges"]} == {"message_difference"}
    assert not ev["vacuous_row"]


@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_the_flag_row_on_md5_is_vacuous_and_not_edge_forced(sub, order):
    """THE DECLARED SPECIFICATION GAP, PINNED BY A TEST RATHER THAN BY PROSE.

    On MD5 in_linearized_code is not a key component, so the row's deletion is
    the identity; and the committed graph carries NO derived_and_witnessed edge
    into that column on MD5. The two readings the module reports therefore
    disagree here and ONLY here.
    """
    ev = _force(sub, "in_linearized_code", "md5", "honest", order)
    assert ev["vacuous_row"] is True
    assert ev["forced_literal_edge_only"] is False
    assert ev["forced_edge_or_vacuous"] is True
    assert ev["vacuous_row_derivation"]


@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_no_empirical_only_edge_ever_forces_a_cell(sub, order):
    """Contract clause (2): an empirical_only edge may not force a cell."""
    for prim in ("md5", "sha1"):
        for row in sub["components"]:
            ev = _force(sub, row, prim, "honest", order)
            for e in ev["forcing_edges"]:
                assert e["edge_label"] == "derived_and_witnessed", (prim, row, e)


# ---------------------------------------------------------------------------
# the forcing predicate against a MOVING instrument (CTL-FORCE-PI side B)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_O_E_does_not_force_the_flag_row_on_sha1(sub, order):
    """O-E drops message_difference on sha1, which is the ONLY derivation-backed
    determiner of the flag, so the injectivity argument has NO ANTECEDENT and
    the cell is NOT forced for O-E. This is the whole content of RT-J8-1."""
    ev = _force(sub, "in_linearized_code", "sha1", "O-E", order)
    assert ev["forced_literal_edge_only"] is False
    assert ev["forced_edge_or_vacuous"] is False
    assert "message_difference" not in ev["retained_component_names"]


@pytest.mark.parametrize("order", sorted(RM.COMPOSITION_ORDERS))
def test_O_E_still_forces_the_length_row_on_sha1_via_step_delta(sub, order):
    ev = _force(sub, "length", "sha1", "O-E", order)
    assert ev["forced_literal_edge_only"] is True
    assert {e["X"] for e in ev["forcing_edges"]} == {"step_delta"}


def test_the_forced_set_is_not_invariant_across_the_projective_instruments(sub):
    """If the new rule returned the same forced set for every instrument it
    would be the old rule under a new name and would measure nothing."""
    for order in RM.COMPOSITION_ORDERS:
        ident = {(r, p) for r in sub["components"] for p in ("md5", "sha1")
                 if _force(sub, r, p, "honest", order)["forced_literal_edge_only"]}
        oe = {(r, p) for r in sub["components"] for p in ("md5", "sha1")
              if _force(sub, r, p, "O-E", order)["forced_literal_edge_only"]}
        assert ident != oe, order


def test_both_composition_orders_are_implemented_distinctly_and_are_compared():
    """H-7: the module must MEASURE the two orders, not assert their agreement.

    The two orders are separate code branches of retained_component_names, and
    a projection that is order-sensitive must be able to separate them.
    """
    key = (("a", 1), ("b", 2), ("c", 3))

    def proj_first_two(k, prim):
        return k[:2]

    a = RM.retained_component_names(key, "md5", proj_first_two, "a",
                                    "project_then_delete")
    b = RM.retained_component_names(key, "md5", proj_first_two, "a",
                                    "delete_then_project")
    assert a == ("b",)
    assert b == ("b", "c")
    assert a != b, ("the two orders must be genuinely different functions, "
                    "or reporting both would be theatre")


# ---------------------------------------------------------------------------
# CTL-PAIR-WF -- the consistent-pair gate, TWO-SIDED
# ---------------------------------------------------------------------------

def test_consistent_pair_is_accepted_on_sha1_and_moves_exactly_the_declared_pair(
        sub):
    e = next(x for x in sub["census"].shadow if x.primitive == "sha1")
    good = RM.perturb_consistent_pair(e.obj, (0,), "t", consistent=True)
    assert DG.wf_violations(good) == []
    before = dict(RM._serialised_key(e.obj))
    after = dict(RM._serialised_key(good))
    moved = sorted(n for n in set(before) | set(after)
                   if before.get(n) != after.get(n))
    assert moved == sorted(RM.CONSISTENT_PAIR_DECLARATION["moves"])
    assert good.in_linearized_code is False


def test_inconsistent_pair_is_rejected_on_sha1_by_W3(sub):
    e = next(x for x in sub["census"].shadow if x.primitive == "sha1")
    bad = RM.perturb_consistent_pair(e.obj, (0,), "t", consistent=False)
    v = DG.wf_violations(bad)
    assert any(c.startswith("W3_") for c in v), v


def test_the_md5_attempt_is_rejected_by_W3_and_is_reported_not_silently_dropped(
        sub):
    e = next(x for x in sub["census"].shadow if x.primitive == "md5")
    good = RM.perturb_consistent_pair(e.obj, (0,), "t", consistent=True)
    v = DG.wf_violations(good)
    assert any(c.startswith("W3_") for c in v), v


def test_consistent_pair_family_reports_constructibility_per_primitive(sub):
    fam = RM.build_consistent_pair_family(sub["census"])
    assert fam["per_primitive"]["sha1"]["CONSTRUCTIBLE"] is True
    assert fam["per_primitive"]["md5"]["CONSTRUCTIBLE"] is False
    assert fam["per_primitive"]["md5"]["consistent_side_rejection_gate_clauses"]
    assert fam["per_primitive"]["sha1"]["inconsistent_side_accepted_by_CTL_WF"] == 0
    moved = RM.measure_moved_components(fam)
    assert moved["sha1"]["declared_equals_measured_union"] is True
    assert moved["md5"]["measured_moved_components"] is None, (
        "H-8: an unmeasured moved set is null and NEVER an empty list")


# ---------------------------------------------------------------------------
# the counting rule against BOTH degenerate instruments
# ---------------------------------------------------------------------------

def test_the_degenerate_instruments_reach_both_extremes_through_one_path(sub):
    census = sub["census"]
    entry_keys = {e.id: (CP.variant_keys(e.obj, RM.STRICT), e.primitive)
                  for e in census.shadow}
    fams = DG.build_families(census)
    dk = DG.family_draw_keys(fams["d_block_index"])
    am = RM.cell_verdict_for(sub["instruments"]["always_member"], entry_keys,
                             dk, "primitive", "md5")
    an = RM.cell_verdict_for(sub["instruments"]["always_non_member"], entry_keys,
                             dk, "primitive", "md5")
    assert am["verdict"] == "DETECTED"
    assert an["verdict"] == "NOT DETECTED"
    assert am["strict_member_draws"] == am["perturbed_draws_k_ge_1"] > 0
    assert an["strict_member_draws"] == 0
    assert am["computed_per_primitive"] and an["computed_per_primitive"]


def test_pinning_is_reported_with_the_count_that_makes_it_so(sub):
    """CTL-READMIT-NULL's declared field, exercised on a synthetic cell set."""
    census = sub["census"]
    entry_keys = {e.id: (CP.variant_keys(e.obj, RM.STRICT), e.primitive)
                  for e in census.shadow}
    fams = DG.build_families(census)
    keys_cache = {"d_block_index": DG.family_draw_keys(fams["d_block_index"])}
    per_cell = [{"family": "d_block_index", "row_deletes": "primitive",
                 "primitive": "md5", "family_moves": ["block_index"],
                 "diagonal": False,
                 "forcing": RM.forcing_edges_for(
                     "primitive", "md5",
                     sub["instruments"]["honest"]["projection"],
                     "project_then_delete", sub["key_names"], sub["rep"],
                     sub["edges"])}]
    arms = RM.readmit_null(per_cell, "edge_only", entry_keys, keys_cache,
                           sub["instruments"], honest_detected=0,
                           adjudicated_total=1)
    assert arms["always_non_member"]["arm_was_arithmetically_pinned"] is True
    assert arms["always_non_member"]["the_count_that_makes_it_so"][
        "honest_detected_cell_count"] == 0
    assert arms["always_member"]["arm_was_arithmetically_pinned"] is False


# ---------------------------------------------------------------------------
# IR-1 / IR-12 -- the firewalls are MECHANISMS and are exercised as such
# ---------------------------------------------------------------------------

def test_the_audit_hook_actually_blocks_the_forbidden_prefix():
    RM.install_independence_and_quarantine_firewall()
    target = os.path.join(RM.REPO, RM.FORBIDDEN_PATH_LITERAL, "rt3_rederive.py")
    with pytest.raises(RM.FirewallBreach):
        open(target, "rb")


def test_the_audit_hook_actually_blocks_the_quarantine_prefix():
    RM.install_independence_and_quarantine_firewall()
    target = os.path.join(RM.REPO, RM.QUARANTINE_PATH_LITERAL, "anything.bin")
    with pytest.raises(RM.FirewallBreach):
        open(target, "rb")


def test_no_module_in_the_process_comes_from_the_forbidden_path():
    a = RM.assert_forbidden_path_absent_from_process()
    assert a["assertion_holds"], a["modules_loaded_from_the_forbidden_path"]


def test_the_criterion_set_excludes_this_contracts_own_new_artifacts():
    d = RM.digests()
    for rel in RM.THIS_CONTRACTS_OWN_ARTIFACTS:
        assert rel not in d["criterion_set"], (
            "CTL-FROZEN-4's criterion set must never contain the artifacts the "
            "contract requires this producer to create, or the control is "
            "vacuous")
    assert "harness/diffpath/depgraph.py" in d["criterion_set"]
    assert "harness/diffpath/controlpower.py" in d["criterion_set"]
    assert "harness/runner.py" in d["criterion_set"]
