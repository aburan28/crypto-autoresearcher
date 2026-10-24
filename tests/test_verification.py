"""Curvesmash bridge controls. No provider calls or candidate execution."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from orchestration import cli, verification as verify


def invoke(*argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return verify.main(list(map(str, argv)))


class DiscoveryTests(unittest.TestCase):
    def test_entrypoint_and_discovery_need_no_optional_backend(self):
        with patch.object(verify, "_backend", side_effect=AssertionError("unexpected backend")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(cli.main(["verify", "--help"]), 0)
                self.assertIn("--expected-intake", output.getvalue())
            self.assertEqual(invoke("tracks"), 0)

    def test_six_distinct_registered_targets_and_current_single_reviewer(self):
        lock = verify.source_lock()
        self.assertEqual(len(lock["tracks"]), 6)
        for track in lock["tracks"]:
            config = json.loads((verify.SOURCE / f"tracks/{track}/verifier.json").read_text())
            self.assertEqual(config["review_standard"], "exploratory-single-review-v1")
            self.assertEqual(config["acceptance_policy"], "exploratory-v1")
            self.assertEqual(config["provider"]["model"], "gpt-6-astra")
            self.assertEqual(config["provider"]["reasoning_effort"], "high")
            self.assertEqual(config["limits"]["max_followups"], 1)
            self.assertEqual(config["objectives"][0]["score_source"], {"claim": 0})
        self.assertTrue({"bls12-381-g1-ecdlp", "bls12-381-g1-ecdlp-plain", "p256-ecdlp"}
                        <= set(lock["tracks"]))

    def test_init_is_write_once_and_selects_only_an_incomplete_unscored_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            self.assertEqual(invoke("init-curvesmash", "--track", "p256-ecdlp", "--out", root), 0)
            self.assertEqual(verify.source_lock(root), verify.source_lock())
            selected = (root / "tracks/p256-ecdlp/selected-submission.txt").read_text().strip()
            manifest = root / selected / "submission.json"
            original = manifest.read_bytes()
            self.assertIn("TODO:", original.decode())
            self.assertNotIn("score", json.loads(original))
            self.assertEqual(invoke("init-curvesmash", "--track", "p256-ecdlp", "--out", root), 2)
            self.assertEqual(manifest.read_bytes(), original)
            unknown = Path(tmp) / "unknown"
            self.assertEqual(invoke("init-curvesmash", "--track", "invented", "--out", unknown), 2)
            self.assertFalse(unknown.exists())

    def test_changed_or_symlinked_protected_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            shutil.copytree(verify.SOURCE, root)
            target = root / "tracks/p256-ecdlp/rules.md"
            target.write_text("changed rules")
            with self.assertRaisesRegex(ValueError, "protected source changed"):
                verify.source_lock(root)
            target.unlink()
            target.symlink_to(verify.SOURCE / "tracks/p256-ecdlp/rules.md")
            with self.assertRaisesRegex(ValueError, "protected source changed"):
                verify.source_lock(root)

    def test_missing_optional_dependency_is_actionable_and_unknown_phase_never_imports_it(self):
        error = ModuleNotFoundError("No module named llm_verifier", name="llm_verifier")
        with patch.object(verify.importlib, "import_module", side_effect=error):
            with contextlib.redirect_stderr(io.StringIO()) as output:
                self.assertEqual(verify.main(["preflight"]), 2)
            self.assertIn(".[verifier]", output.getvalue())
        with patch.object(verify, "_backend", side_effect=AssertionError("unexpected backend")):
            self.assertEqual(invoke("execute-and-review"), 2)


class OutputTests(unittest.TestCase):
    def test_an_output_cannot_alias_another_outputs_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "result.json"
            collision = Path(tmp) / ".result.json.autoresearch-lock"
            with self.assertRaisesRegex(ValueError, "reserved verification lock"), \
                    verify._fresh_outputs([target, collision]):
                self.fail("output aliases a reservation")
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_existing_and_dangling_output_are_never_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "result.json"
            target.write_text("earlier attempt")
            with self.assertRaises(FileExistsError), verify._fresh_outputs([target]):
                self.fail("reserved an existing output")
            self.assertEqual(target.read_text(), "earlier attempt")
            target.unlink()
            target.symlink_to(Path(tmp) / "missing")
            with self.assertRaises(FileExistsError), verify._fresh_outputs([target]):
                self.fail("reserved a dangling symlink")
            self.assertTrue(target.is_symlink())

    def test_concurrent_writer_is_refused_and_locks_release_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "result.json"
            with self.assertRaisesRegex(RuntimeError, "test interruption"):
                with verify._fresh_outputs([target]):
                    with self.assertRaises(FileExistsError), verify._fresh_outputs([target]):
                        self.fail("reserved an in-flight output")
                    raise RuntimeError("test interruption")
            self.assertEqual(list(Path(tmp).iterdir()), [])


@unittest.skipUnless(importlib.util.find_spec("llm_verifier"), "install .[verifier] for real phase integration")
class PhaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "challenge"
        verify.init_curvesmash("secp256k1-ecdlp", self.root)
        self.candidate = "submissions/secp256k1-ecdlp/candidate"
        (self.root / self.candidate / "proof.md").write_text(
            "Software packaging fixture only; this is not a supported attack claim.\n")
        (self.root / self.candidate / "submission.json").write_text(json.dumps({
            "version": 1, "title": "Software packaging fixture",
            "claims": [{"statement": "Software fixture only, not cryptanalytic evidence.",
                        "score": {"numerator": "10", "denominator": "4"},
                        "evidence": ["proof.md"]}], "experiments": [],
        }))
        self.options = ["--root", self.root, "--config", "tracks/secp256k1-ecdlp/verifier.json",
                        "--submission", self.candidate]
        self.intake = Path(self.temp.name) / "intake.json"

    def intake_args(self):
        self.assertEqual(invoke("intake", *self.options, "--out", self.intake), 0)
        digest = json.loads(self.intake.read_text())["sha256"]
        return ["--intake", self.intake, "--expected-intake", digest]

    def test_all_six_registered_configurations_are_self_contained(self):
        fixture = (self.root / self.candidate / "submission.json").read_text()
        for track in verify.source_lock()["tracks"]:
            with self.subTest(track=track):
                root = Path(self.temp.name) / track
                verify.init_curvesmash(track, root)
                candidate = f"submissions/{track}/candidate"
                (root / candidate / "submission.json").write_text(fixture)
                (root / candidate / "proof.md").write_text("Software packaging fixture only.\n")
                self.assertEqual(invoke("preflight", "--root", root,
                    "--config", f"tracks/{track}/verifier.json", "--submission", candidate), 0)

    def test_real_preflight_intake_and_empty_experiments_without_docker_or_provider(self):
        self.assertEqual(invoke("preflight", *self.options), 0)
        args = self.intake_args()
        packet = json.loads(self.intake.read_text())
        self.assertEqual(packet["data"]["preprocessing"]["adapter"], "curvesmash-v1")
        self.assertEqual(packet["data"]["manifest"]["claims"][0]["score"],
                         {"numerator": "5", "denominator": "2"})
        self.assertEqual(invoke("prepare-runtime", *args), 0)
        output = Path(self.temp.name) / "initial.json"
        with patch("llm_verifier.runner.DockerRunner.run", side_effect=AssertionError("candidate ran")):
            self.assertEqual(invoke("experiments", *args, "--out", output), 0)
        self.assertEqual(json.loads(output.read_text())["data"]["runs"], [])
        original = self.intake.read_bytes()
        self.assertEqual(invoke("intake", *self.options, "--out", self.intake), 2)
        self.assertEqual(self.intake.read_bytes(), original)

    def test_intake_binding_is_required_and_mismatches_produce_no_output(self):
        args = self.intake_args()
        output = Path(self.temp.name) / "initial.json"
        with patch.dict("os.environ", {"LLMV_EXPECTED_INTAKE": ""}):
            self.assertEqual(invoke("experiments", "--intake", self.intake, "--out", output), 2)
        args[-1] = "0" * 64
        self.assertEqual(invoke("experiments", *args, "--out", output), 2)
        self.assertFalse(output.exists())

    def test_tampered_artifacts_and_implementation_are_rejected(self):
        args = self.intake_args()
        packet = json.loads(self.intake.read_text())
        packet["data"]["files"]["proof.md"]["text"] = "altered"
        self.intake.write_text(json.dumps(packet))
        output = Path(self.temp.name) / "initial.json"
        self.assertEqual(invoke("experiments", *args, "--out", output), 2)
        self.assertFalse(output.exists())
        with patch("llm_verifier.artifacts.implementation", return_value={"content_sha256": "0" * 64}):
            self.assertEqual(invoke("preflight", *self.options), 2)

    def test_simulation_remains_nonpublishable_and_cannot_be_finalized(self):
        script = Path(self.temp.name) / "script.json"
        script.write_text(json.dumps({"initial_results": [], "initial_decision": {
            "kind": "judgment", "judgment": {"valid": True, "scores": None,
                "reason": "Scripted software test only; not a scientific review.",
                "evidence_refs": ["source:proof.md"],
                "review_standard": "exploratory-single-review-v1"}, "requests": []},
            "followup_results": [], "final_decision": None}))
        output = Path(self.temp.name) / "simulation.json"
        self.assertEqual(invoke("simulate", *self.options, "--script", script, "--out", output), 0)
        result = json.loads(output.read_text())
        self.assertTrue(result["simulation_only"])
        self.assertFalse(result["publishable"])
        self.assertNotIn("scores", result)
        dossier = result["dossier"]
        self.assertEqual(dossier["data"]["yukon_projection"]["scores"], [2.5])
        phases = dict(zip(("intake", "initial", "initial_review"), dossier["data"]["phases"]))
        files = {}
        for name, value in phases.items():
            path = Path(self.temp.name) / f"{name}.json"
            path.write_text(json.dumps(value))
            files[name] = path
        score, report = Path(self.temp.name) / "score.json", Path(self.temp.name) / "dossier.json"
        self.assertEqual(invoke("finalize", "--intake", files["intake"],
            "--expected-intake", phases["intake"]["sha256"],
            "--initial", files["initial"], "--initial-review", files["initial_review"],
            "--score", score, "--dossier", report), 2)
        self.assertFalse(score.exists())

    def test_one_scripted_followup_and_final_rejection_remain_explicit(self):
        manifest_path = self.root / self.candidate / "submission.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["experiments"] = [{"id": "probe", "source": "experiment.py",
            "purpose": "Software follow-up plumbing control, not an attack.",
            "input_schema": {"type": "object", "properties": {}, "required": [],
                             "additionalProperties": False}, "initial_inputs": []}]
        manifest_path.write_text(json.dumps(manifest))
        (self.root / self.candidate / "experiment.py").write_text(
            "raise RuntimeError('simulation must never execute this program')\n")
        request = {"kind": "followup", "judgment": None, "requests": [
            {"experiment": "probe", "inputs": {}, "reason": "Scripted plumbing check."}]}
        script = {"initial_results": [], "initial_decision": request,
            "followup_results": [{"checked": True}], "final_decision": {
                "kind": "judgment", "judgment": {"valid": False, "scores": None,
                    "reason": "The fixture supplies no cryptanalytic support.",
                    "evidence_refs": ["source:proof.md"],
                    "review_standard": "exploratory-single-review-v1"}, "requests": []}}
        path = Path(self.temp.name) / "script.json"
        path.write_text(json.dumps(script))
        output = Path(self.temp.name) / "simulation.json"
        self.assertEqual(invoke("simulate", *self.options, "--script", path, "--out", output), 0)
        data = json.loads(output.read_text())["dossier"]["data"]
        self.assertEqual(len(data["phases"]), 5)
        self.assertFalse(data["yukon_projection"]["valid"])
        self.assertIsNone(data["yukon_projection"]["scores"])
        script["final_decision"] = request
        path.write_text(json.dumps(script))
        rejected = Path(self.temp.name) / "second-followup.json"
        self.assertEqual(invoke("simulate", *self.options, "--script", path, "--out", rejected), 2)
        self.assertFalse(rejected.exists())

    def test_missing_provider_credentials_is_infrastructure_failure_with_no_review(self):
        args = self.intake_args()
        initial = Path(self.temp.name) / "initial.json"
        self.assertEqual(invoke("experiments", *args, "--out", initial), 0)
        review = Path(self.temp.name) / "review.json"
        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
            self.assertEqual(invoke("review-initial", *args, "--initial", initial, "--out", review), 2)
        self.assertFalse(review.exists())


if __name__ == "__main__":
    unittest.main()
