"""Successor for the nonportable archived-predecessor CI fixture.

Synthetic unit metadata is not an execution or an external study replay.
The original receipt, tests, checker and protocol hashes stay unchanged.
"""
from pathlib import Path
import copy
import json
from unittest.mock import patch


def test_full_role1_replay_rejects_near_valid_forgery_classes(tmp_path):
    from tools.ci_test_supersession import load_verified_module, verify_sources

    repo = Path(__file__).resolve().parents[3]
    record = json.loads((Path(__file__).parent / "supersession.json").read_text())
    verify_sources(repo, record["original_inputs"])
    helper = load_verified_module(repo, record["helpers"][0], "p192_portable_fixture")
    role1, role2 = helper.ROLE1, helper.ROLE2
    root = (tmp_path / "synthetic-protocol").resolve()
    root.mkdir()
    run, decision_path, protocol, decision = helper.build(root)

    def replay():
        errors = []
        binding = role2._role1_predecessor_binding(run, root, errors)
        return binding, errors

    # Preserve every original positive assertion, with actual direct parents.
    binding, errors = replay()
    assert errors == [] and binding is not None
    assert binding["receipt"] == role2.decode_canonical_json(
        (run / "independent-verifier-receipt.json").read_bytes())
    assert len(binding["artifact_inventory"]) == len(role2.ROLE1_REQUIRED_PATHS) == 20
    assert helper.git(root, "rev-parse", decision + "^") == protocol
    assert helper.git(root, "rev-parse", "HEAD^") == decision
    assert binding["decision_sha256"] == role2.sha256_path(decision_path)
    assert binding["artifact_tree_sha256"] == role2._artifact_inventory_digest(binding["artifact_inventory"])

    # Each original forgery must fail for its defect, after repository admission.
    mutations = [
        ("wrong_verifier_commit", "receipt verifier commit"),
        ("wrong_verifier_binary", "verifier binary binding"),
        ("shallow_receipt", "decision binding is incomplete"),
        ("malformed_inventory", "schema: [] is too short"),
        ("duplicate_comparison", "agreement field order"),
    ]
    for mutation, expected in mutations:
        name = "independent-agreement.json" if mutation == "duplicate_comparison" else "independent-verifier-receipt.json"
        path = run / name
        original = path.read_bytes()
        document = role2.decode_canonical_json(original)
        if mutation == "wrong_verifier_commit":
            document["verifier_commit"] = "3" * 40
        elif mutation == "wrong_verifier_binary":
            document["verifier"]["binary_sha256"] = "4" * 64
        elif mutation == "shallow_receipt":
            document = {"schema": "p192-wcm-independent-verifier-receipt-v1", "overall_status": "PASS"}
        elif mutation == "malformed_inventory":
            document["producer_artifacts_before"] = []
        else:
            document["comparisons"][1] = copy.deepcopy(document["comparisons"][0])
        try:
            path.write_bytes(role1._canonical_json_bytes(document))
            _, errors = replay()
            assert errors, mutation
            if mutation != "shallow_receipt":
                assert any(
                    "Role-1 run replay" in error
                    or "receipt/run-directory identity" in error
                    for error in errors
                ), mutation
            assert any(expected in error for error in errors), errors
            assert "Role-1 predecessor receipt/admitted repository differs from frozen value" not in errors
        finally:
            path.write_bytes(original)

    # Keep the exact repository gate and prove it runs before Git/code loading.
    wrong_root = tmp_path / "wrong-admitted-repository"
    wrong_root.mkdir()
    errors = []
    with patch.object(role2, "_git_stdout", side_effect=AssertionError("Git must not run")), patch.object(role2, "_load_role1_checker", side_effect=AssertionError("checker must not load")):
        refused = role2._role1_predecessor_binding(run, wrong_root, errors)
    assert refused is None
    assert errors == ["Role-1 predecessor receipt/admitted repository differs from frozen value"]

    original_decision = decision_path.read_bytes()
    try:
        decision_path.write_bytes(original_decision + b"\n")
        _, errors = replay()
        assert any("decision raw hash" in error for error in errors), errors
        assert any("decision working bytes" in error for error in errors), errors
    finally:
        decision_path.write_bytes(original_decision)
    helper.git(root, "commit", "--allow-empty", "-qm", "Synthetic incorrect archive parent")
    _, errors = replay()
    assert any("archive direct decision parent" in error for error in errors), errors
    verify_sources(repo, record["original_inputs"])
