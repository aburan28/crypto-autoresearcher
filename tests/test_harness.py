"""Correctness tests for the executable spine.

These guard the parts a research harness must never get wrong: curve
arithmetic, that solvers recover verifiable answers, that the summation
polynomial satisfies its defining identity, and that the run wrapper produces a
complete, certificate-verified, immutable record.
"""
from __future__ import annotations

import os
import random

import pytest
import sympy

from harness import rho, semaev
from harness.runner import RunResult, curve_id, write_run
from harness.toycurve import EllipticCurve, generate_instance


def test_textbook_curve_order_and_group_law():
    # y^2 = x^3 + 2x + 2 over F_17 has order 19 (classic example).
    E = EllipticCurve(17, 2, 2)
    assert E.order() == 19
    G = (5, 1)
    assert E.is_on_curve(G)
    assert E.mul(19, G) is None
    # additive homomorphism on scalars
    assert E.add(E.mul(3, G), E.mul(4, G)) == E.mul(7, G)
    # negation
    assert E.add(G, E.negate(G)) is None


@pytest.mark.parametrize("bits", [6, 8, 10, 12])
def test_generated_instance_is_consistent_and_deterministic(bits):
    a = generate_instance(seed=5, field_bits=bits)
    b = generate_instance(seed=5, field_bits=bits)
    assert a == b                                   # deterministic
    E = a.curve()
    assert E.is_on_curve(a.P) and E.is_on_curve(a.Q)
    assert E.mul(a.n, a.P) is None                  # P has order dividing n (prime)
    assert a.P is not None
    assert E.mul(a.k, a.P) == a.Q                   # Q = k P


@pytest.mark.parametrize("bits", [6, 8, 10, 12, 14])
def test_rho_recovers_verifiable_discrete_log(bits):
    inst = generate_instance(seed=11, field_bits=bits)
    res = rho.solve(inst)
    assert res.solved
    # independent verification, not trusting the solver
    assert inst.curve().mul(res.k, inst.P) == inst.Q


def test_summation_polynomial_vanishing_identity():
    E = EllipticCurve(101, 2, 3)
    random.seed(0)
    checked = 0
    for _ in range(500):
        A = E.lift_x(random.randrange(101))
        B = E.lift_x(random.randrange(101))
        if A is None or B is None:
            continue
        C = E.negate(E.add(A, B))       # A + B + C = O
        if C is None:
            continue
        assert semaev.s3_eval(2, 3, A[0], B[0], C[0], 101) == 0
        checked += 1
    assert checked > 20


def test_s4_has_exact_support_degree_and_frozen_witness():
    x4 = sympy.symbols("x4")
    s4 = semaev.s4_expr(2, 3)

    assert s4.free_symbols == {semaev.x1, semaev.x2, semaev.x3, x4}
    assert semaev._t not in s4.free_symbols
    assert sympy.Poly(
        s4, semaev.x1, semaev.x2, semaev.x3, x4
    ).total_degree() == 12
    witness = {
        semaev.x1: 1,
        semaev.x2: 3,
        semaev.x3: 5,
        x4: 41,
    }
    assert int(s4.subs(witness)) % 101 == 0


def test_factor_base_legacy_and_target_subgroup_scopes():
    inst = generate_instance(seed=1, field_bits=6)
    E = inst.curve()
    expected_legacy = [34, 4, 25, 40, 30]
    expected_subgroup = {12, 13, 18, 24, 33}

    assert inst.n == 11
    assert E.order() // inst.n == 5
    assert semaev.build_factor_base(inst, 5) == expected_legacy
    assert semaev.build_factor_base(
        inst, 5, scope="full_curve"
    ) == expected_legacy

    subgroup_base = semaev.build_factor_base(
        inst, 5, scope="target_subgroup"
    )
    assert subgroup_base == semaev.build_factor_base(
        inst, 5, scope="target_subgroup"
    )
    assert len(subgroup_base) == 5
    assert len(set(subgroup_base)) == 5
    assert set(subgroup_base) == expected_subgroup
    for x in subgroup_base:
        canonical_lift = E.lift_x(x)
        assert canonical_lift is not None
        assert E.mul(inst.n, canonical_lift) is None

    with pytest.raises(ValueError):
        semaev.build_factor_base(inst, 6, scope="target_subgroup")
    with pytest.raises(ValueError):
        semaev.build_factor_base(inst, 5, scope="unknown")


def test_decomposition_certificate_verifies_independently():
    inst = generate_instance(seed=3, field_bits=8)
    m = semaev.measure_s3_decomposition(inst, factor_base_size=16)
    assert m.groebner_basis_size >= 1
    if m.decomposition_found:
        assert semaev.verify_decomposition_certificate(m.certificate)
        # tampering must be detected
        bad = {"kind": "decomposition",
               "statement": {**m.certificate["statement"],
                             "target": [m.certificate["statement"]["target"][0],
                                        (m.certificate["statement"]["target"][1] + 1)]}}
        assert not semaev.verify_decomposition_certificate(bad)


def test_run_wrapper_writes_complete_immutable_record(tmp_path):
    inst = generate_instance(seed=7, field_bits=8)
    res = rho.solve(inst)
    cid = curve_id(inst.p, inst.a, inst.b, 8)
    rr = RunResult(
        run_suffix="test-b8-s7", curve_id=cid, seed=7,
        parameters={"field_bits": 8, "solver": "pollard_rho"},
        metrics={"group_operations": res.group_operations},
        certificate={"kind": "discrete_log",
                     "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                                   "P": list(inst.P), "Q": list(inst.Q), "k": res.k}},
        stdout="ok\n")
    out = str(tmp_path)
    run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)
    run_dir = os.path.join(out, "runs", run_id)
    for artifact in ("manifest.yaml", "command.txt", "environment.json",
                     "stdout.log", "stderr.log", "raw-result.json"):
        assert os.path.exists(os.path.join(run_dir, artifact))
    import yaml
    manifest = yaml.safe_load(open(os.path.join(run_dir, "manifest.yaml")))["run"]
    assert manifest["result"]["certificate"]["verified"] is True
    assert manifest["status"] == "completed_valid"
    # immutability: re-writing the same run id is refused
    with pytest.raises(FileExistsError):
        write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                  command="pytest", started=1.0, finished=2.0, out_root=out)


def test_run_wrapper_invalidates_bad_certificate(tmp_path):
    inst = generate_instance(seed=7, field_bits=8)
    rr = RunResult(
        run_suffix="badcert-b8-s7", curve_id="TOY", seed=7,
        parameters={"field_bits": 8}, metrics={},
        certificate={"kind": "discrete_log",
                     "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                                   "P": list(inst.P), "Q": list(inst.Q),
                                   "k": inst.k + 1}})   # wrong k
    run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    assert manifest["status"] == "completed_invalid"
    assert manifest["result"]["valid"] is False


def test_run_wrapper_omits_optional_metadata_by_default(tmp_path):
    # backward compatibility: no exemplar metadata -> keys absent entirely
    rr = RunResult(
        run_suffix="optmeta-absent", curve_id="TOY", seed=1,
        parameters={"field_bits": 8}, metrics={},
        certificate={"kind": "none"})
    run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0,
                       out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    assert "heuristic_validation" not in manifest
    assert "cost_model" not in manifest


def test_run_wrapper_records_optional_exemplar_metadata(tmp_path):
    hv = {"heuristic_id": "H1",
          "statement_ref": "inputs/P13-WESOLOWSKI-2026/paper_fulltext.md#heuristic-1",
          "prediction": "largest-prime-factor CDF matches rho(u)",
          "theoretical_distribution": "dickman_de_bruijn rho(u)",
          "sample_size": 1000,
          "scale_relevance": "toy-scale: shape check only, not crypto-scale evidence"}
    cm = {"operation_unit": "group_operation",
          "assumptions": ["optimistic: constant-time group operation"],
          "notes": "matched generic baseline"}
    rr = RunResult(
        run_suffix="optmeta-present", curve_id="TOY", seed=1,
        parameters={"field_bits": 8}, metrics={},
        certificate={"kind": "none"},
        heuristic_validation=hv, cost_model=cm)
    run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0,
                       out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    assert manifest["heuristic_validation"] == hv
    assert manifest["cost_model"] == cm


# --- GOAL-ENDO-001 N6: executed-source pinning -------------------------------
# Open since DEC-20260807-c8aa8b, promoted to blocking by CORR-20260807-0f5d56.
# `code.commit` plus a `dirty` boolean does not identify the code that ran; 17
# of EXP-ICINV-4d33aa's 19 measurement runs were in that state, which is why an
# EXP-INSTR-85b102 root cause is permanently unrecoverable.

def test_source_provenance_pins_every_executed_repo_module():
    from harness import runner

    prov = runner.source_provenance()
    assert prov["all_pinned"] is True
    assert prov["file_count"] > 0
    # It must find the modules this test actually imported, not a declared list.
    assert "harness/runner.py" in prov["files"]
    assert "harness/toycurve.py" in prov["files"]
    for rel, entry in prov["files"].items():
        assert entry["status"] in {"clean", "modified", "untracked"}, rel
        assert entry["sha256"] and len(entry["sha256"]) == 64, rel
    # Nothing outside the repo, and nothing that is not Python source.
    assert all(not r.startswith("/") and r.endswith(".py") for r in prov["files"])


def test_source_provenance_hash_matches_the_file_on_disk():
    """The pin must be the file's real content hash, or it pins nothing."""
    import hashlib
    from harness import runner

    prov = runner.source_provenance()
    rel = "harness/toycurve.py"
    with open(os.path.join(runner.REPO, rel), "rb") as fh:
        expected = hashlib.sha256(fh.read()).hexdigest()
    assert prov["files"][rel]["sha256"] == expected


def test_untracked_source_is_distinguished_from_untracked_run_output():
    """The original N6 defect: outputs and source were both 'untracked'."""
    from harness import runner

    split = runner.untracked_source_vs_output()
    assert set(split) == {"untracked_source_code", "untracked_other_count",
                          "untracked_output_count"}
    assert isinstance(split["untracked_source_code"], list)
    # Run outputs live under experiments/*/runs/ and must never be counted as
    # source, which is what made an untracked .py invisible.
    assert all(not p.startswith("experiments/") or "/runs/" not in p
               for p in split["untracked_source_code"])


def test_run_manifest_carries_source_pins(tmp_path):
    inst = generate_instance(seed=11, field_bits=8)
    res = rho.solve(inst)
    rr = RunResult(
        run_suffix="n6-b8-s11", curve_id=curve_id(inst.p, inst.a, inst.b, 8),
        seed=11, parameters={"field_bits": 8},
        metrics={"group_operations": res.group_operations},
        certificate={"kind": "discrete_log",
                     "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                                   "P": list(inst.P), "Q": list(inst.Q), "k": res.k}},
        stdout="ok\n")
    out = str(tmp_path)
    run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)

    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(out, "runs", run_id, "manifest.yaml")))["run"]
    source = manifest["code"]["source"]
    assert source["all_pinned"] is True
    assert source["files"]["harness/runner.py"]["sha256"]
    # The legacy fields survive: this is additive, so old readers still work.
    assert manifest["code"]["commit"] and "dirty" in manifest["code"]
    assert "untracked_output_count" in manifest["code"]["untracked"]


def test_write_run_refuses_when_executed_source_cannot_be_pinned(tmp_path):
    """N6 is blocking: an unpinnable run is refused, not silently recorded."""
    from unittest.mock import patch

    from harness import runner as runner_module

    inst = generate_instance(seed=13, field_bits=8)
    res = rho.solve(inst)
    rr = RunResult(
        run_suffix="n6-refuse-b8-s13", curve_id=curve_id(inst.p, inst.a, inst.b, 8),
        seed=13, parameters={"field_bits": 8},
        metrics={"group_operations": res.group_operations},
        certificate={"kind": "discrete_log",
                     "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                                   "P": list(inst.P), "Q": list(inst.Q), "k": res.k}},
        stdout="ok\n")
    unpinnable = {"files": {"harness/ghost.py": {"sha256": None,
                                                 "status": "unreadable"}},
                  "file_count": 1, "all_pinned": False, "all_clean": False,
                  "modified": [], "untracked": [],
                  "unreadable": ["harness/ghost.py"]}
    out = str(tmp_path)
    with patch.object(runner_module, "source_provenance", return_value=unpinnable):
        with pytest.raises(RuntimeError, match="not pinnable"):
            write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                      command="pytest", started=1.0, finished=2.0, out_root=out)
    # And it must not leave a half-written run directory behind.
    assert not os.path.exists(os.path.join(out, "runs", "RUN-SEMAEV-n6-refuse-b8-s13"))
