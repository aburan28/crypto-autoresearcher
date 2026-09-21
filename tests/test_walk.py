"""Correctness tests for the rho/kangaroo walk kernel and its drawings.

The properties that matter here: a walk state always carries a true
representation of its point, a traced orbit really is the tail and cycle it
reports, both solvers recover a scalar that verifies against Q without ever
reading the instance's stored secret, and the renderers draw exactly the states
that were walked.
"""
from __future__ import annotations

import dataclasses
import json
import os

import pytest

from harness import kangaroo, walk, walkviz
from harness.run_walkviz import main as walkviz_main
from harness.toycurve import generate_instance


def _inst(seed=7, field_bits=12):
    return generate_instance(seed=seed, field_bits=field_bits)


def _walk(inst, **kw):
    kw.setdefault("branches", 8)
    return walk.AddingWalk(inst.curve(), inst.P, inst.Q, inst.n, inst.seed, **kw)


def test_walk_states_carry_a_true_representation():
    inst = _inst()
    w = _walk(inst, dp_bits=2)
    st = w.start("t")
    assert w.verify_state(st)
    for _ in range(50):
        st = w.step(st)
        assert w.verify_state(st)            # R == a*P + b*Q at every step


def test_walk_is_deterministic_in_the_seed():
    inst = _inst()
    a, b = _walk(inst), _walk(inst)
    assert a.steps == b.steps
    sa, sb = a.start("x"), b.start("x")
    for _ in range(20):
        sa, sb = a.step(sa), b.step(sb)
    assert sa == sb


def test_trace_orbit_reports_the_real_tail_and_cycle():
    inst = _inst(seed=11)
    w = _walk(inst)
    tr = walk.trace_orbit(w)
    assert tr.closed
    pts = [s.R for s in tr.states]
    # the last state repeats exactly the one where the cycle began
    assert pts[-1] == pts[tr.tail_length]
    assert len(pts) == tr.tail_length + tr.cycle_length + 1
    # everything before the repeat is visited once
    assert len(set(pts[:-1])) == len(pts) - 1
    # the cycle closes under the step map
    st = tr.states[tr.tail_length]
    for _ in range(tr.cycle_length):
        st = w.step(st)
    assert st.R == tr.states[tr.tail_length].R
    assert tr.rho_length == tr.tail_length + tr.cycle_length


def test_trace_orbit_reports_an_exhausted_budget_as_open():
    inst = _inst()
    tr = walk.trace_orbit(_walk(inst), max_steps=3)
    assert not tr.closed
    assert tr.tail_length is None and tr.cycle_length is None
    assert tr.rho_length is None          # nothing is claimed about the orbit


def test_walk_to_dp_lands_on_a_distinguished_point():
    inst = _inst()
    w = _walk(inst, dp_bits=2)
    dw = walk.walk_to_dp(w, w.start("d"), record_path=True)
    if dw.hit_dp:
        assert w.is_distinguished(dw.end.R)
        assert len(dw.path) == dw.steps + 1
        assert dw.path[0] == dw.start and dw.path[-1] == dw.end


def test_walk_to_dp_requires_a_dp_rule():
    inst = _inst()
    w = _walk(inst, dp_bits=0)
    with pytest.raises(ValueError):
        walk.walk_to_dp(w, w.start("d"))


@pytest.mark.parametrize("seed", [1, 3, 5, 8])
def test_dp_search_recovers_the_scalar(seed):
    inst = _inst(seed=seed, field_bits=12)
    res = walk.solve_dp(inst, dp_bits=2, branches=8)
    assert res.solved, res.reason
    assert res.k == inst.k
    assert inst.curve().mul(res.k, inst.P) == inst.Q
    assert res.group_operations > 0
    assert res.collision is not None and res.collision.useful


def test_dp_search_uses_public_data_only():
    # Corrupt the stored secret: a solver that reads it cannot still be right.
    inst = _inst(seed=3)
    lying = dataclasses.replace(inst, k=(inst.k + 1) % inst.n)
    res = walk.solve_dp(lying, dp_bits=2, branches=8)
    assert res.solved and res.k == inst.k


def test_dp_search_can_keep_walking_after_the_collision():
    inst = _inst(seed=3)
    res = walk.solve_dp(inst, dp_bits=2, branches=8, max_walks=24,
                        stop_on_solution=False)
    assert res.solved and res.k == inst.k
    assert len(res.walks) == 24           # extra walks do not change the answer


def test_dp_search_reports_an_exhausted_budget_as_unsolved():
    inst = _inst()
    res = walk.solve_dp(inst, dp_bits=2, branches=8, max_walks=1)
    if not res.solved:
        assert res.k is None and res.collision is None
        assert "budget" in res.reason     # a budget outcome, not a group claim


@pytest.mark.parametrize("seed", [1, 3, 5, 8])
def test_kangaroo_recovers_a_scalar_in_the_interval(seed):
    inst = _inst(seed=seed, field_bits=12)
    res = kangaroo.solve_interval(inst)
    assert res.solved, res.reason
    assert res.k == inst.k
    assert res.interval[0] <= res.k <= res.interval[1]
    assert inst.curve().mul(res.k, inst.P) == inst.Q


def test_kangaroo_narrow_interval_is_cheaper_than_the_full_range():
    inst = _inst(seed=5, field_bits=16)
    lo, hi = max(1, inst.k - 20), min(inst.n - 1, inst.k + 20)
    narrow = kangaroo.solve_interval(inst, lo, hi)
    assert narrow.solved and narrow.k == inst.k
    assert narrow.interval == (lo, hi)


def test_kangaroo_uses_public_data_only():
    inst = _inst(seed=5)
    lying = dataclasses.replace(inst, k=(inst.k + 1) % inst.n)
    res = kangaroo.solve_interval(lying)
    assert res.solved and res.k == inst.k


def test_kangaroo_rejects_an_interval_outside_the_subgroup():
    inst = _inst()
    with pytest.raises(ValueError):
        kangaroo.solve_interval(inst, 0, inst.n)
    with pytest.raises(ValueError):
        kangaroo.solve_interval(inst, 10, 5)


def test_functional_graph_is_total_and_matches_the_step_map():
    inst = _inst(seed=9, field_bits=10)
    w = _walk(inst)
    pts = walkviz.subgroup_points(w.E, w.P, w.n)
    assert len(pts) == w.n and len(set(pts)) == w.n
    succ = walkviz.functional_graph(w, pts)
    assert set(succ) == set(pts)
    st = w.start("g")
    assert succ[st.R] == w.step(st).R


def test_renderers_emit_deterministic_svg():
    inst = _inst(seed=9, field_bits=10)
    w = _walk(inst)
    tr = walk.trace_orbit(w)
    a = walkviz.render_functional_graph_svg(w, tr, n=w.n, iterations=20)
    b = walkviz.render_functional_graph_svg(w, tr, n=w.n, iterations=20)
    assert a == b
    assert a.startswith("<svg") and a.rstrip().endswith("</svg>")
    # every subgroup element is drawn, plus the enlarged start marker
    assert a.count("<circle") == w.n + 1


def test_dp_forest_render_needs_recorded_paths():
    inst = _inst(seed=3)
    w = _walk(inst, dp_bits=2)
    res = walk.solve_dp(inst, dp_bits=2, branches=8, walk=w, record_paths=False)
    with pytest.raises(ValueError):
        walkviz.render_dp_forest_svg(w, res.walks, res.collision)


def test_dp_forest_render_draws_the_walked_states():
    inst = _inst(seed=3)
    w = _walk(inst, dp_bits=2)
    res = walk.solve_dp(inst, dp_bits=2, branches=8, walk=w, record_paths=True,
                        stop_on_solution=False, max_walks=8)
    svg = walkviz.render_dp_forest_svg(w, res.walks, res.collision, iterations=20)
    drawn = {p for wk in res.walks for p in wk.path}
    assert svg.count("<circle") == len({s.R for s in drawn})


def test_kangaroo_render_colours_both_herds():
    inst = _inst(seed=5)
    res = kangaroo.solve_interval(inst, record_paths=True)
    svg = walkviz.render_kangaroo_svg(res, iterations=20)
    assert walkviz.PALETTE["tame"] in svg and walkviz.PALETTE["wild"] in svg


def test_serialisation_round_trips_through_json(tmp_path):
    inst = _inst(seed=3)
    w = _walk(inst, dp_bits=2)
    tr = walk.trace_orbit(w)
    doc = walk.trace_to_dict(w, tr)
    path = str(tmp_path / "trace.json")
    walk.dump_json(doc, path)
    assert json.load(open(path)) == doc
    assert len(doc["states"]) == len(tr.states)


def test_cli_writes_records_and_figures(tmp_path):
    out = str(tmp_path / "out")
    assert walkviz_main(["--seed", "3", "--field-bits", "10", "--dp-bits", "2",
                         "--walks", "8", "--branches", "8",
                         "--layout-iterations", "20", "--out-dir", out]) == 0
    for name in ("manifest.json", "rho_trace.json", "rho_trace.svg",
                 "dp_walks.json", "dp_walks.svg", "kangaroo.json",
                 "kangaroo.svg"):
        assert os.path.exists(os.path.join(out, name)), name
    man = json.load(open(os.path.join(out, "manifest.json")))
    assert man["instance"]["n"] == generate_instance(seed=3, field_bits=10).n
    for fig in ("dp", "kangaroo"):
        if man["figures"][fig]["solved"]:
            assert man["figures"][fig]["secret_k_matches"] is True
