"""Tests for the optional Frontier-CS / Harbor eval backend.

Every test here runs offline: the `frontier` CLI is faked, so no Docker, no API
key and no network is touched. That is deliberate — a test suite that silently
skipped whenever the benchmark was absent would tell you nothing on the machines
where it is absent, which is most of them.

The two that matter most are `test_unavailable_is_not_a_zero_score` and
`test_infrastructure_failure_is_not_a_capability_signal`. If either regresses,
this module starts manufacturing capability numbers out of missing tooling.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from orchestration.eval import harbor  # noqa: E402


def task(**over) -> harbor.HarborTask:
    base = dict(id="fcs-t1", track="algorithmic", problem="0",
                agent="codex", model="gpt-5.5")
    base.update(over)
    return harbor.HarborTask(**base)


def fake_run(payload, *, returncode: int = 0, stderr: str = ""):
    def _run(cmd, **kwargs):
        return subprocess.CompletedProcess(
            cmd, returncode,
            stdout=json.dumps(payload) if isinstance(payload, dict) else payload,
            stderr=stderr)
    return _run


ALL_PRESENT = harbor.Probe(available=True, frontier="/usr/bin/frontier",
                           harbor="/usr/bin/harbor", docker="/usr/bin/docker",
                           missing=[])


class ProbeTests(unittest.TestCase):
    def test_missing_everything_is_unavailable(self) -> None:
        p = harbor.probe(which=lambda _: None, env={})
        self.assertFalse(p.available)
        self.assertIn("frontier CLI", p.missing)
        self.assertIn("docker", p.missing)

    def test_uvx_substitutes_for_harbor_on_path(self) -> None:
        present = {"frontier", "docker", "uvx"}
        p = harbor.probe(which=lambda n: f"/bin/{n}" if n in present else None,
                         env={"OPENAI_API_KEY": "x"})
        self.assertTrue(p.available)
        self.assertTrue(any("uvx harbor" in n for n in p.notes))

    def test_absent_api_key_is_a_note_not_a_hard_block(self) -> None:
        present = {"frontier", "docker", "harbor"}
        p = harbor.probe(which=lambda n: f"/bin/{n}" if n in present else None,
                         env={})
        self.assertTrue(p.available)
        self.assertTrue(any("OPENAI_API_KEY" in n for n in p.notes))

    def test_unavailable_is_not_a_zero_score(self) -> None:
        """An absent benchmark must raise, never resolve to a score of 0.

        Recording 0.0 for "not installed" would put a fabricated capability
        number into an immutable record.
        """
        p = harbor.probe(which=lambda _: None, env={})
        with self.assertRaises(harbor.HarborUnavailable):
            p.require()
        with self.assertRaises(harbor.HarborUnavailable):
            harbor.run_trial(task(), 0, probe_result=p)


class CommandTests(unittest.TestCase):
    def test_command_matches_the_documented_cli(self) -> None:
        self.assertEqual(
            harbor.build_command(task(), frontier="frontier"),
            ["frontier", "harbor", "trial", "algorithmic", "0",
             "-a", "codex", "-m", "gpt-5.5", "--json"])

    def test_two_point_zero_track_is_accepted(self) -> None:
        cmd = harbor.build_command(task(track="2.0", problem="erdos_demo"))
        self.assertIn("2.0", cmd)
        self.assertIn("erdos_demo", cmd)

    def test_unknown_track_is_rejected_at_construction(self) -> None:
        with self.assertRaises(ValueError):
            task(track="not-a-track")

    def test_forbidden_model_is_rejected_at_task_construction(self) -> None:
        with self.assertRaisesRegex(ValueError, "forbidden by cost policy"):
            task(model="amazon-BeDrOcK/us.example-model")

    def test_forbidden_yaml_model_is_rejected_before_external_runner(self) -> None:
        document = {
            "harbor_suite": {
                "name": "forbidden-target-fixture",
                "tasks": [{
                    "id": "forbidden-1", "track": "algorithmic", "problem": "0",
                    "agent": "codex", "model": "amazon-bedrock/example",
                }],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "suite.yaml"
            path.write_text(yaml.safe_dump(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "forbidden by cost policy"):
                harbor.load_suite(path)


class ParseTests(unittest.TestCase):
    def test_score_is_rescaled_from_0_100_to_0_1(self) -> None:
        r = harbor.parse_trial_json(
            {"score": 75, "trial_status": "completed"}, task(), 0,
            wall_seconds=1.0)
        self.assertAlmostEqual(r.score, 0.75)
        self.assertTrue(r.passed)

    def test_zero_score_does_not_pass(self) -> None:
        r = harbor.parse_trial_json(
            {"score": 0, "trial_status": "completed"}, task(), 0,
            wall_seconds=1.0)
        self.assertFalse(r.passed)

    def test_infrastructure_failure_is_not_a_capability_signal(self) -> None:
        """AGENTS.md rule 5: a timeout is not evidence against the thing tested.

        It still counts as a non-pass, but it is labelled so it can be filtered
        out of a capability average rather than silently depressing it.
        """
        r = harbor.parse_trial_json(
            {"score": None, "trial_status": "AgentTimeoutError"}, task(), 0,
            wall_seconds=9.0)
        self.assertFalse(r.passed)
        self.assertEqual(r.stop_reason, "AgentTimeoutError")
        self.assertEqual(r.error, "AgentTimeoutError")
        self.assertTrue(any(v.grader == "infrastructure" for v in r.verdicts))

    def test_token_and_cost_fields_are_carried_through(self) -> None:
        r = harbor.parse_trial_json(
            {"score": 10, "trial_status": "completed", "n_input_tokens": 5,
             "n_cache_tokens": 2, "n_output_tokens": 7, "cost_usd": 0.42,
             "successful_submissions": 3},
            task(), 0, wall_seconds=1.0)
        self.assertEqual(r.usage["input_tokens"], 5)
        self.assertEqual(r.usage["output_tokens"], 7)
        self.assertEqual(r.steps, 3)
        self.assertIn("cost_usd=0.42", r.verdicts[0].detail)


class RunTests(unittest.TestCase):
    def test_successful_trial(self) -> None:
        r = harbor.run_trial(task(), 0, probe_result=ALL_PRESENT,
                             runner=fake_run({"score": 88,
                                              "trial_status": "completed"}))
        self.assertTrue(r.passed)
        self.assertAlmostEqual(r.score, 0.88)

    def test_nonzero_exit_is_recorded_not_raised(self) -> None:
        r = harbor.run_trial(task(), 0, probe_result=ALL_PRESENT,
                             runner=fake_run({}, returncode=2, stderr="boom"))
        self.assertFalse(r.passed)
        self.assertEqual(r.stop_reason, "frontier_error")
        self.assertIn("boom", r.error)

    def test_unparsable_output_is_recorded_not_raised(self) -> None:
        r = harbor.run_trial(task(), 0, probe_result=ALL_PRESENT,
                             runner=fake_run("not json at all"))
        self.assertFalse(r.passed)
        self.assertEqual(r.stop_reason, "unparsable_output")

    def test_timeout_is_recorded_not_raised(self) -> None:
        def _timeout(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd, 1)
        r = harbor.run_trial(task(timeout_seconds=1), 0,
                             probe_result=ALL_PRESENT, runner=_timeout)
        self.assertFalse(r.passed)
        self.assertEqual(r.stop_reason, "harness_timeout")

    def test_mutated_forbidden_target_never_reaches_external_runner(self) -> None:
        for field in ("agent", "model"):
            with self.subTest(field=field):
                candidate = task()
                setattr(candidate, field, "Amazon-BeDrOcK/example")
                calls = []

                def forbidden_runner(*args, **kwargs):
                    calls.append((args, kwargs))
                    raise AssertionError("forbidden target reached Harbor runner")

                with self.assertRaisesRegex(ValueError, "forbidden by cost policy"):
                    harbor.run_trial(
                        candidate, 0, probe_result=ALL_PRESENT,
                        runner=forbidden_runner)
                self.assertEqual(calls, [])


class SuiteTests(unittest.TestCase):
    SUITE = REPO / "evals" / "harbor" / "frontier-cs.yaml"

    def test_shipped_suite_loads_and_every_track_is_valid(self) -> None:
        suite = harbor.load_suite(self.SUITE)
        self.assertTrue(suite.tasks)
        for t in suite.tasks:
            self.assertIn(t.track, harbor.TRACKS)

    def test_filter_by_track_and_split(self) -> None:
        suite = harbor.load_suite(self.SUITE)
        self.assertTrue(all(t.track == "2.0"
                            for t in suite.filter(tracks=["2.0"]).tasks))
        self.assertTrue(all(t.split == "dev"
                            for t in suite.filter(splits=["dev"]).tasks))

    def test_run_suite_summary_flows_through_the_shared_report_path(self) -> None:
        suite = harbor.load_suite(self.SUITE).filter(splits=["dev"])
        summary, trials = harbor.run_suite(
            suite, trials=2, probe_result=ALL_PRESENT,
            runner=fake_run({"score": 50, "trial_status": "completed"}))
        self.assertEqual(len(trials), 2 * len(suite.tasks))
        self.assertTrue(summary.suite.startswith("frontier-cs::"))
        # the arm, not a harness backend id, is what a Frontier-CS score belongs to
        self.assertIn("codex:gpt-5.5", summary.backend)
        # grouping key is the Frontier-CS track
        self.assertTrue({s.kind for s in summary.tasks} <= set(harbor.TRACKS))


if __name__ == "__main__":
    unittest.main()
