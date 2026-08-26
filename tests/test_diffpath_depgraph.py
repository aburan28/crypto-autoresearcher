"""Tests for harness/diffpath/depgraph.py -- the NEW module of EXP-DIFFP-04082e.

A NEW DEDICATED TEST FILE. NO EXISTING TEST FILE IS EDITED: tests/test_harness.py,
tests/test_diffpath_adjudicator.py and tests/test_diffpath_controlpower.py are
explicitly out of scope (IR-2).

WHAT IS PINNED HERE, AND WHY EACH ONE: the edge detector against a KNOWN-EDGE and
a KNOWN-NO-EDGE population, because a constancy test that cannot return NO EDGE is
vacuous; the well-formedness gate on BOTH sides, because a gate that accepts
everything is not a gate; the exclusion rules, because an excluded cell that
silently entered a differing-cell count would be the failure H-3 exists to stop;
and the counting rule against the two degenerate instruments, because a count with
no demonstrated capacity to be large is the 96/96-and-0/3000 failure one layer up.
"""
from harness.diffpath import depgraph as DG
from harness.diffpath import primitives as P
from harness.diffpath.pathobj import PathObject, bsdr_encode


def _obj(oid, primitive="md5", length=4, md=None, sd=None, block=0, flag=None):
    md = md if md is not None else tuple(range(16))
    sd = sd if sd is not None else tuple(range(length))
    kw = dict(id=oid, primitive=primitive, step_range=(0, length - 1),
              provenance="internal", source_ref="test", status="readable",
              path_data={"kind": "unit_test"},
              step_delta=sd,
              step_delta_signed=tuple(bsdr_encode(x) for x in sd),
              block_index=block)
    if primitive == "md5":
        kw.update(delta_m=md, delta_m_signed=tuple(bsdr_encode(x) for x in md))
    else:
        dv = md
        kw.update(dv=dv, dv_seed_window=tuple(dv[:16]),
                  in_linearized_code=(P.sha1_in_linearized_code(list(dv))
                                      if flag is None else flag))
    return PathObject(**kw)


# --- the edge detector -----------------------------------------------------

def test_edge_detector_reports_EDGE_on_a_known_edge_population():
    objs = [_obj(f"A{i}", length=4 + (i % 3)) for i in range(30)]
    rec = DG.detect_edge(objs, "step_delta", "length")
    assert rec["verdict"] == "EDGE"
    assert rec["groups_non_constant_in_Y"] == 0
    assert rec["population_size"] == 30
    assert "counterexample_certificate" not in rec


def test_edge_detector_reports_NO_EDGE_with_a_full_counterexample_certificate():
    a = _obj("B0", block=0)
    b = _obj("B1", block=1)
    rec = DG.detect_edge([a, b], "step_delta", "block_index")
    assert rec["verdict"] == "NO EDGE"
    cert = rec["counterexample_certificate"]
    assert len(cert["objects"]) == 2
    assert cert["objects"][0]["Y_value"] != cert["objects"][1]["Y_value"]


def test_edge_detector_flags_a_population_whose_Y_is_constant():
    objs = [_obj(f"C{i}", block=0) for i in range(5)]
    rec = DG.detect_edge(objs, "message_difference", "block_index")
    assert rec["verdict"] == "EDGE"
    assert rec["Y_CONSTANT_ON_POPULATION"] is True
    assert rec["LOW_DISTINCT_X"] is True


def test_edge_detector_flags_singleton_only_groups():
    objs = [_obj(f"D{i}", md=tuple([i] + list(range(15)))) for i in range(6)]
    rec = DG.detect_edge(objs, "message_difference", "block_index")
    assert rec["SINGLETON_GROUPS_ONLY"] is True
    assert rec["max_group_size"] == 1


# --- the well-formedness gate, BOTH SIDES ----------------------------------

def test_gate_accepts_a_well_formed_object_of_each_primitive():
    assert DG.wf_violations(_obj("E0")) == []
    dv = tuple(P.sha1_expand(list(range(16)), 20))
    assert DG.wf_violations(_obj("E1", primitive="sha1", length=20, md=dv)) == []


def test_gate_rejects_the_deliberately_malformed_flipped_flag_object():
    dv = tuple(P.sha1_expand(list(range(16)), 20))
    good = _obj("F0", primitive="sha1", length=20, md=dv)
    bad = DG.malformed_null_family_e(good)
    v = DG.wf_violations(bad)
    assert v, "a gate that accepts everything is not a gate"
    assert any("in_linearized_code" in c for c in v)


def test_gate_rejects_a_length_perturbation_that_leaves_the_arrays_stale():
    v = DG.wf_violations(DG._perturb_length(_obj("G0"), "t"))
    assert any("step_range" in c for c in v)


def test_gate_rejects_a_primitive_swap():
    assert DG.wf_violations(DG._perturb_primitive(_obj("H0"), "t")) != []


def test_gate_accepts_a_step_delta_perturbation_and_a_block_index_move():
    assert DG.wf_violations(DG._perturb_step_delta(_obj("I0"), (0, 33), "t")) == []
    assert DG.wf_violations(DG._perturb_block_index(_obj("I1"), 5, "t")) == []


# --- the exclusion rules ---------------------------------------------------

def _families(constructible=True):
    return {
        "d_message_difference": {
            "declaration": DG.FAMILY_DECLARATIONS["d_message_difference"],
            "NOT_CONSTRUCTIBLE_on_every_primitive": False,
            "per_primitive": {}},
        "d_in_linearized_code": {
            "declaration": DG.FAMILY_DECLARATIONS["d_in_linearized_code"],
            "NOT_CONSTRUCTIBLE_on_every_primitive": not constructible,
            "per_primitive": {}},
    }


def test_exclusions_cover_diagonal_forced_and_not_constructible():
    comps = ["message_difference", "in_linearized_code", "block_index"]
    forced = {"in_linearized_code": {"sha1": [{"X": "message_difference",
                                              "Y": "in_linearized_code",
                                              "derivation": "d"}]}}
    sel = DG.select_cells(comps, _families(constructible=False), forced)
    reasons = {c["exclusion"] for c in sel["excluded"]}
    assert reasons == {"diagonal", "forced_by_the_graph", "not_constructible"}
    for c in sel["excluded"]:
        assert c["reason"]
        assert c["value"] is None
    adj = {(c["family"], c["row_deletes"]) for c in sel["adjudicated"]}
    assert ("d_message_difference", "message_difference") not in adj
    assert ("d_message_difference", "in_linearized_code") not in adj
    assert ("d_in_linearized_code", "block_index") not in adj
    assert ("d_message_difference", "block_index") in adj


# --- the counting rule against the degenerate instruments -----------------

def _draws():
    return [("md5", 0, ["k0"]), ("md5", 1, ["a"]), ("sha1", 2, ["b"])]


def test_counting_rule_ignores_the_k0_arm_and_counts_only_perturbed_draws():
    v = DG.cell_verdict(_draws(), lambda keys, prim: False)
    assert v["perturbed_draws_k_ge_1"] == 2
    assert v["verdict"] == "NOT DETECTED"


def test_counting_rule_reaches_both_extremes_on_the_degenerate_instruments():
    always_member = DG.cell_verdict(_draws(), lambda keys, prim: True)
    always_non = DG.cell_verdict(_draws(), lambda keys, prim: False)
    assert always_member["verdict"] == "DETECTED"
    assert always_member["strict_member_draws"] == 2
    assert always_non["verdict"] == "NOT DETECTED"
    assert always_non["strict_member_draws"] == 0


def test_counting_rule_can_be_filtered_per_primitive():
    v = DG.cell_verdict(_draws(), lambda keys, prim: True, prim_filter="sha1")
    assert v["perturbed_draws_k_ge_1"] == 1


# --- contract-shape invariants --------------------------------------------

def test_every_result_carries_census_completeness_never_summed():
    v = DG.cell_verdict(_draws(), lambda keys, prim: False)
    cc = v["census_completeness"]
    assert cc["readable"] == 0
    assert cc["quarantined_not_read"] == 1
    assert cc["acquisition_gap"] == 8
    assert cc["shadow_planted_carried_separately"] == 16


def test_the_module_never_names_the_quarantine_path():
    src = open(DG.__file__, encoding="utf-8").read()
    assert "GOAL-MD5-001/quarantine" not in src


def test_ensure_does_not_stub_semaev_when_real_sympy_already_loaded():
    """Regression: a second ensure() after runner loaded sympy must not
    replace harness.semaev with the empty diffpath stub (CI breakage of
    tests/test_harness.py when test_diffpath_depgraph is collected)."""
    import sys

    import sympy  # noqa: F401 — real sympy present
    from harness.diffpath import compat

    before = sys.modules.get("harness.semaev")
    result = compat.ensure()
    after = sys.modules.get("harness.semaev")
    assert result.get("sympy_shim_used") is False
    assert getattr(after, "__diffpath_stub__", False) is False
    if before is not None:
        assert after is before
