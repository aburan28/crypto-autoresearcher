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


def _discrete_log_result(run_suffix, seed=7, wrong_k=False):
    inst = generate_instance(seed=seed, field_bits=8)
    res = rho.solve(inst)
    k = res.k + 1 if wrong_k else res.k
    return RunResult(
        run_suffix=run_suffix, curve_id=curve_id(inst.p, inst.a, inst.b, 8), seed=seed,
        parameters={"field_bits": 8}, metrics={"group_operations": res.group_operations},
        certificate={"kind": "discrete_log",
                     "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                                   "P": list(inst.P), "Q": list(inst.Q), "k": k}},
        stdout="ok\n")


def test_cairn_cross_check_absent_for_kind_none():
    """Stage 0 (docs/cairn-integration-plan.md) touches nothing when there is
    no certificate to re-check -- same contract as `_verify` returning
    "no-claim", covered above by test_run_wrapper_omits_optional_metadata_by_default
    for the sibling optional blocks."""
    from harness.runner import _cairn_cross_check
    assert _cairn_cross_check({"kind": "none"}, verified=True) is None


def test_cairn_cross_check_recorded_when_it_agrees(tmp_path):
    from unittest.mock import patch
    from tools import cairn_bridge

    rr = _discrete_log_result("cairn-agree-b8-s7")
    fake_verdict = cairn_bridge.CairnVerdict(
        status="accept", detail="verified: fake but agreeing",
        objective_id="sha256:" + "a" * 64, checker_sha256="deadbeef")
    with patch.object(cairn_bridge, "available", return_value=True), \
         patch.object(cairn_bridge, "score_certificate", return_value=fake_verdict):
        run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                            command="pytest", started=1.0, finished=2.0, out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    cross_check = manifest["result"]["certificate"]["cairn_cross_check"]
    assert cross_check["status"] == "accept"
    assert cross_check["objective_id"] == fake_verdict.objective_id


def test_cairn_disagreement_refuses_and_leaves_no_run_directory(tmp_path):
    """The same severity class as the N6 provenance refusal above: two
    independent implementations disagreeing about a witness means one of
    them has a bug, so the run is refused rather than recorded with a
    quietly-noted anomaly."""
    from unittest.mock import patch
    from tools import cairn_bridge

    rr = _discrete_log_result("cairn-disagree-b8-s7")  # internal check: verified True
    fake_verdict = cairn_bridge.CairnVerdict(
        status="reject", detail="mocked disagreement",
        objective_id="sha256:" + "b" * 64, checker_sha256="deadbeef")
    out = str(tmp_path)
    with patch.object(cairn_bridge, "available", return_value=True), \
         patch.object(cairn_bridge, "score_certificate", return_value=fake_verdict):
        with pytest.raises(RuntimeError, match="cairn disagreement"):
            write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                      command="pytest", started=1.0, finished=2.0, out_root=out)
    assert not os.path.exists(os.path.join(out, "runs", "RUN-SEMAEV-cairn-disagree-b8-s7"))


def test_cairn_unavailable_is_additive_never_a_new_hard_dependency(tmp_path):
    """A machine with no cairn build must behave exactly as it did before
    Stage 0 existed: the run writes normally, and the manifest says so
    rather than omitting the field."""
    from unittest.mock import patch
    from tools import cairn_bridge

    rr = _discrete_log_result("cairn-absent-b8-s7")
    with patch.object(cairn_bridge, "available", return_value=False):
        run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                            command="pytest", started=1.0, finished=2.0, out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    assert manifest["status"] == "completed_valid"
    cross_check = manifest["result"]["certificate"]["cairn_cross_check"]
    assert cross_check["status"] == "not_attempted"


def test_cairn_bridge_failure_is_not_attempted_not_a_crash(tmp_path):
    """A reachable-but-broken bridge (timeout, unparseable response) is the
    same "says nothing about the artifact" case as cairn's own `unavailable`
    verdict -- recorded, never crashes the run and never counts as either
    agreement or disagreement."""
    from unittest.mock import patch
    from tools import cairn_bridge

    rr = _discrete_log_result("cairn-broken-b8-s7")
    with patch.object(cairn_bridge, "available", return_value=True), \
         patch.object(cairn_bridge, "score_certificate",
                      side_effect=cairn_bridge.CairnUnavailableError("mocked timeout")):
        run_id = write_run("EXP-SEMAEV-001", "SEMAEV", rr, status="completed_valid",
                            command="pytest", started=1.0, finished=2.0, out_root=str(tmp_path))
    import yaml
    manifest = yaml.safe_load(
        open(os.path.join(tmp_path, "runs", run_id, "manifest.yaml")))["run"]
    cross_check = manifest["result"]["certificate"]["cairn_cross_check"]
    assert cross_check["status"] == "not_attempted"
    assert "mocked timeout" in cross_check["reason"]


# --- GOAL-MD5-001 F-6(a): md5_collision_pair pin-mechanism tests ------------
# DEC-20260820-32bf19 F-2(2), landed by TASK-20260821-f5f96a (BATCH-1f30fe).
# The md5_collision_pair certificate kind (BCP-2 collision_certificate_format)
# is exercised here on KNOWN-FALSE objects through the PRODUCTION path --
# write_run's own _verify dispatch, not a re-implementation of the checks --
# and the pin-mechanism distinctness assertion (BCP-2
# pin_mechanism_requirement, INV-13) is exercised with the REAL pinned
# registry and with ALIASED registries that must be detected as not distinct.

_MD5_BLOCK_A = "00" * 64          # one 512-bit block, hex-encoded
_MD5_BLOCK_B = "01" * 64          # a different 512-bit block, hex-encoded


def _md5_hex(data: bytes) -> str:
    import hashlib
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def _md5_pair_result(run_suffix, m1_hex, m2_hex, digest_hex,
                     verified_by=None):
    """A RunResult carrying an md5_collision_pair certificate, ready for the
    production write_run path. `verified_by` (when given) is a SOLVER-
    SUPPLIED value at the certificate's top level (a sibling of `statement`,
    per the BCP-2 schema) that the wrapper must clear (BCP-2's J5 fix)."""
    statement = {"messages": [m1_hex, m2_hex], "digest": digest_hex,
                 "implementations": ["IMPL-1", "IMPL-3"]}
    certificate = {"kind": "md5_collision_pair", "statement": statement}
    if verified_by is not None:
        certificate["verified_by"] = verified_by
    return RunResult(
        run_suffix=run_suffix, curve_id="MD5", seed=0,
        parameters={"kind": "md5_collision_pair"}, metrics={},
        certificate=certificate,
        stdout="ok\n")


def _read_run(out_root, run_id):
    import yaml, json
    run_dir = os.path.join(out_root, "runs", run_id)
    manifest = yaml.safe_load(
        open(os.path.join(run_dir, "manifest.yaml")))["run"]
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    return manifest, raw


def test_md5_collision_pair_noncolliding_pair_fails_with_named_checks(tmp_path):
    """Known-false object 1: two distinct blocks whose digests differ. The
    claimed digest is the TRUE digest of m1, so exactly the two m2 checks
    must fail and be named; the run is completed_invalid, not a result."""
    digest = _md5_hex(bytes.fromhex(_MD5_BLOCK_A))
    rr = _md5_pair_result("md5pair-nocoll-s0", _MD5_BLOCK_A, _MD5_BLOCK_B, digest)
    out = str(tmp_path)
    run_id = write_run("EXP-MDFIVE-001", "MDFIVE", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)
    manifest, raw = _read_run(out, run_id)
    cert = manifest["result"]["certificate"]
    assert manifest["status"] == "completed_invalid"
    assert manifest["result"]["valid"] is False
    assert cert["verified"] is False
    assert cert["failing_checks"] == ["digest_mismatch_impl1_m2",
                                      "digest_mismatch_impl3_m2"]
    # The pin-mechanism block is recorded at run time with the real registry.
    assert raw["certificate"]["pin_mechanism"]["distinct"] is True


def test_md5_collision_pair_tampered_digest_fails_with_named_checks(tmp_path):
    """Known-false object 2: a tampered claimed digest (one hex digit
    flipped). All four pinned-implementation digests mismatch and each is
    named."""
    digest = _md5_hex(bytes.fromhex(_MD5_BLOCK_A))
    tampered = ("0" if digest[0] != "0" else "1") + digest[1:]
    rr = _md5_pair_result("md5pair-tamper-s0", _MD5_BLOCK_A, _MD5_BLOCK_B, tampered)
    out = str(tmp_path)
    run_id = write_run("EXP-MDFIVE-001", "MDFIVE", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)
    manifest, _ = _read_run(out, run_id)
    cert = manifest["result"]["certificate"]
    assert manifest["status"] == "completed_invalid"
    assert cert["verified"] is False
    assert cert["failing_checks"] == [
        "digest_mismatch_impl1_m1", "digest_mismatch_impl1_m2",
        "digest_mismatch_impl3_m1", "digest_mismatch_impl3_m2"]


def test_md5_collision_pair_identical_messages_fail_m1_equals_m2(tmp_path):
    """Known-false object 3: m1 == m2 with the TRUE digest claimed. All four
    digests agree, so the ONLY failing check must be m1_equals_m2 -- a
    collision certificate for identical messages is not a collision."""
    digest = _md5_hex(bytes.fromhex(_MD5_BLOCK_A))
    rr = _md5_pair_result("md5pair-same-s0", _MD5_BLOCK_A, _MD5_BLOCK_A, digest)
    out = str(tmp_path)
    run_id = write_run("EXP-MDFIVE-001", "MDFIVE", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)
    manifest, raw = _read_run(out, run_id)
    cert = manifest["result"]["certificate"]
    assert manifest["status"] == "completed_invalid"
    assert cert["verified"] is False
    assert cert["failing_checks"] == ["m1_equals_m2"]
    # Even a failing certificate carries the run-time pin-mechanism record.
    assert raw["certificate"]["pin_mechanism"]["distinct"] is True


def test_md5_pin_mechanism_real_registry_is_distinct():
    """The REAL pinned registry (IMPL-1 hashlib/OpenSSL vs IMPL-3 _md5/
    CPython) must be distinct at the mechanism level: distinct module files
    and distinct runtime types, probed through the runner's own callables."""
    from harness import runner

    record, distinct = runner._md5_pin_mechanism(runner._MD5_IMPL_FUNCS)
    assert distinct is True
    f1, f3 = record["IMPL-1"]["module_file"], record["IMPL-3"]["module_file"]
    t1, t3 = record["IMPL-1"]["runtime_type"], record["IMPL-3"]["runtime_type"]
    assert f1 and f3 and f1 != f3
    assert t1 != t3
    # The mechanism, not the names: IMPL-1 resolves into the OpenSSL-backed
    # _hashlib extension, IMPL-3 into CPython's standalone _md5 extension.
    assert "_hashlib" in os.path.basename(f1)
    assert os.path.basename(f3).startswith("_md5")
    assert t1.startswith("_hashlib.")
    assert t3.startswith("_md5.")


def test_md5_pin_mechanism_real_registry_library_linkage_distinct():
    """Library linkage (BCP-2 pin_mechanism_requirement, third axis): the
    IMPL-1 extension links a crypto library (libcrypto); the IMPL-3
    extension links no crypto library (libSystem only). Checked with
    otool -L on the resolved module files -- Darwin only, where the pin was
    made; on other platforms the linkage axis is not re-checked here."""
    import platform
    import shutil
    import subprocess

    from harness import runner

    record, distinct = runner._md5_pin_mechanism(runner._MD5_IMPL_FUNCS)
    assert distinct is True
    if platform.system() != "Darwin" or shutil.which("otool") is None:
        import pytest
        pytest.skip("otool -L linkage check is Darwin-only; the pin's "
                    "linkage determination was made on Darwin")
    linkage = {}
    for impl_id in runner.PINNED_MD5_IMPLEMENTATIONS:
        out = subprocess.run(["otool", "-L", record[impl_id]["module_file"]],
                             capture_output=True, text=True).stdout
        linkage[impl_id] = out
    assert "libcrypto" in linkage["IMPL-1"]
    assert "libcrypto" not in linkage["IMPL-3"]
    assert "libSystem" in linkage["IMPL-3"]


def test_md5_pin_mechanism_aliased_registry_is_detected_not_distinct():
    """An ALIASED registry -- both slots pointing at one implementation's
    code path -- must be detected as NOT distinct. This is the edit BCP-2's
    pin_mechanism_requirement exists to catch: the names would still read
    IMPL-1/IMPL-3, but the mechanism (module file + runtime type) does not."""
    from harness import runner

    for aliased in (
        {"IMPL-1": runner._md5_impl1_hash, "IMPL-3": runner._md5_impl1_hash},
        {"IMPL-1": runner._md5_impl3_hash, "IMPL-3": runner._md5_impl3_hash},
    ):
        record, distinct = runner._md5_pin_mechanism(aliased)
        assert distinct is False
        assert record["IMPL-1"]["module_file"] == record["IMPL-3"]["module_file"]
        assert record["IMPL-1"]["runtime_type"] == record["IMPL-3"]["runtime_type"]


def test_md5_collision_pair_verified_by_is_wrapper_populated(tmp_path):
    """BCP-2's J5 fix: any solver-provided verified_by is CLEARED and
    replaced exclusively with the wrapper's own recomputation, per pinned
    implementation. The solver's value must not survive into the record."""
    digest = _md5_hex(bytes.fromhex(_MD5_BLOCK_A))
    solver_claim = [{"implementation": "SOLVER-CLAIMED",
                     "computed_digest_m1": "0" * 32,
                     "computed_digest_m2": "0" * 32}]
    rr = _md5_pair_result("md5pair-vby-s0", _MD5_BLOCK_A, _MD5_BLOCK_A, digest,
                          verified_by=solver_claim)
    out = str(tmp_path)
    run_id = write_run("EXP-MDFIVE-001", "MDFIVE", rr, status="completed_valid",
                       command="pytest", started=1.0, finished=2.0, out_root=out)
    import json
    _, raw = _read_run(out, run_id)
    verified_by = raw["certificate"]["verified_by"]
    assert [e["implementation"] for e in verified_by] == ["IMPL-1", "IMPL-3"]
    assert all(e["computed_digest_m1"] == digest and e["computed_digest_m2"] == digest
               for e in verified_by)
    assert "SOLVER-CLAIMED" not in json.dumps(raw)


# ---------------------------------------------------------------------------
# harness/run_md4_ceiling.py (GOAL-MD5-001 BATCH-af29f6 TASK-20260821-de817d,
# EXP-MDFIVE-88f7d1). Additive only. These are the two audit-1 correctness
# gates the frozen contract requires to pass BEFORE any statistical run is
# trusted: the RFC 1320 published test vectors, and HEUR-H2's deterministic
# backward-inversion regression fixture.
# ---------------------------------------------------------------------------

def test_rfc1320_md4_vectors():
    """The standalone MD4 core (no hashlib) must reproduce every published
    RFC 1320 Appendix A.5 test vector exactly."""
    from harness.run_md4_ceiling import check_rfc1320_vectors

    result = check_rfc1320_vectors()
    assert result["all_ok"] is True, result
    assert len(result["vectors"]) == 7


def test_h2_backward_inversion_regression_fixture_md4_and_md5():
    """HEUR-H2 (H-MDFIVE-bf7767): forward_step/backward_step composition
    must be an exact identity on every sampled tuple for BOTH primitives'
    Round-1 conventions (MD4: no trailing '+= b'; MD5: with it) -- a single
    failure invalidates all downstream MITM search results."""
    from harness.run_md4_ceiling import h2_regression_fixture

    for mode in ("md4", "md5"):
        result = h2_regression_fixture(seed=8975317, n=10000, mode=mode)
        assert result["all_ok"] is True, (mode, result["failures"][:3])
        assert result["n"] == 10000


def test_md4_forward_backward_step_add_b_convention():
    """Regression pin for the specific bug this module's first draft hit:
    MD4's Round-1 operation (RFC 1320 sec 3.4, "[abcd k s]" notation) has NO
    trailing '+= b' term, unlike MD5's RFC 1321 FF/GG/HH/II macros. Using
    MD5's formula for MD4 fails every RFC 1320 A.5 vector -- this test pins
    the two conventions directly against a hand-computed example so a future
    edit that re-merges them is caught immediately, not just via the vector
    self-test."""
    from harness.run_md4_ceiling import (MD4_ADD_B, MD5_ADD_B, _IV,
                                         backward_step, forward_step)

    assert MD4_ADD_B is False
    assert MD5_ADD_B is True
    state = _IV
    xk, s, t = 0x11223344, 7, 0
    md4_next = forward_step(state, xk, s, t, add_b=False)
    md5_next = forward_step(state, xk, s, t, add_b=True)
    assert md4_next != md5_next
    assert backward_step(md4_next, xk, s, t, add_b=False) == state
    assert backward_step(md5_next, xk, s, t, add_b=True) == state


def test_md4_ceiling_brute_force_control_result_sets_equal():
    """The correctness control this contract requires before any k1=k2=10
    search result is trusted (invalidation_rules): the MITM hash-table
    search's result set must be IDENTICAL to the naive all-pairs search's
    result set on the fully brute-forceable k1=k2=6 subset."""
    from harness.run_md4_ceiling import (fixed_word_generation,
                                         generate_target, mitm_search,
                                         naive_all_pairs_search)

    fixed = fixed_word_generation(seed=20260821, free_bits=6)
    target = generate_target(8975316, fixed, "md4", free_bits=6)
    mitm = mitm_search(fixed, target, "md4", 6, 6, 6, 20)
    naive = naive_all_pairs_search(fixed, target, "md4", 6, 6, 20)
    assert sorted(mitm["solutions"]) == sorted(naive["solutions"])
    assert mitm["solutions"], "control target must be reachable in-window"
