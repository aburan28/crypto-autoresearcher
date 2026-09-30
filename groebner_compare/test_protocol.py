import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from .certificate import Rank, certify
from .runner import run, validate


FAKE = r'''
import json, sys, time
scenario = sys.argv[1]
for line in sys.stdin:
    q = json.loads(line)
    op = q['operation']
    if scenario == 'timeout':
        time.sleep(10)
    r = {'request_id': q['request_id'], 'status': 'ok',
         'basis_terms': q['instance']['equations'], 'trace_id': 't'}
    if op == 'apply':
        if scenario == 'bad-basis':
            r['basis_terms'] = [[0]]
        elif scenario == 'incompatible':
            r['status'] = 'incompatible'
    if scenario == 'bad-learn' and op == 'learn':
        r['basis_terms'] = [[0]]
    if scenario == 'unavailable':
        r['status'] = 'unavailable'
    if scenario == 'bad-id':
        r['request_id'] = -1
    if scenario == 'partial':
        sys.stdout.write('{'); sys.stdout.flush(); time.sleep(10)
    if op == 'verify_relations':
        r['vectors'] = [[1, 0], [2, 0], [0, 0]]
    print(json.dumps(r), flush=True)
'''


def manifest(scenario="ok", mode="learn_apply"):
    return {"schema": 1, "encoding": "synthetic-linear-v1",
            "ring": {"field": "GF(2)", "quotient": "x_i^2+x_i", "order": "degrevlex",
                     "nvars": 2, "variables": ["x0", "x1"]},
            "watchdog_seconds": 5,
            "instances": [{"id": "a", "equations": [[1]]},
                          {"id": "b", "equations": [[0, 1]]}],
            "backends": [{"id": "test-double", "mode": mode,
                          "command": [sys.executable, "-c", FAKE, scenario],
                          "provenance": "test double, not a solver benchmark"}]}


class ProtocolTests(unittest.TestCase):
    def run_case(self, spec):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "receipt"
        result = run(spec, output)[0]
        events = [json.loads(line) for line in
                  (output / "backend-0/events.jsonl").read_text().splitlines()]
        return result, events, output

    def test_certificate_checks_ideal_and_groebner_property(self):
        self.assertTrue(certify(2, [[1]], [[1]])["verified"])
        self.assertFalse(certify(2, [[1]], [[0]])["verified"])
        self.assertFalse(certify(2, [[1]], []) ["verified"])
        # These generators define the correct ideal but are not a GB.
        self.assertFalse(certify(2, [[1, 2], [3]], [[1, 2], [3]])["verified"])
        self.assertTrue(certify(2, [[1, 2], [3]], [[1], [2]])["verified"])
        self.assertEqual(certify(2, [], []) ["root_count"], 4)
        self.assertEqual(certify(2, [[0]], [[0]])["root_count"], 0)
        self.assertTrue(certify(2, [[1, 1]], []) ["verified"])
        with self.assertRaises(ValueError):
            certify(2, [[True]], [])

    def test_learning_and_apply_are_both_charged(self):
        result, events, output = self.run_case(manifest())
        self.assertEqual(result["verified_instances"], 2)
        self.assertEqual([e["operation"] for e in events],
                         ["learn", "basis_verification", "apply", "basis_verification"])
        self.assertGreater(result["phase_seconds"]["learn"], 0)
        self.assertGreaterEqual(result["total_wall_seconds"], sum(result["phase_seconds"].values()))
        self.assertIsNone(result["verified_relation_rank"])
        self.assertIsNone(result["full_dlp_speedup"])
        with self.assertRaises(FileExistsError):
            run(manifest(), output)

    def test_rejected_trace_and_false_positive_fall_back(self):
        for scenario in ("incompatible", "bad-basis", "bad-learn"):
            with self.subTest(scenario=scenario):
                result, events, _ = self.run_case(manifest(scenario))
                self.assertEqual(result["verified_instances"], 2)
                self.assertIn("fallback", result["phase_seconds"])
                self.assertGreater(result["phase_seconds"]["fallback"], 0)
                self.assertTrue(any(e["operation"] == "fallback" for e in events))

    def test_missing_worker_and_failures_are_unknown(self):
        for scenario in ("unavailable", "bad-id", "timeout", "partial", "missing"):
            with self.subTest(scenario=scenario):
                spec = manifest(scenario, "cold")
                spec["watchdog_seconds"] = .15 if scenario in ("timeout", "partial") else 5
                if scenario == "missing":
                    spec["backends"][0]["command"] = ["/no-such-groebner-worker"]
                result, events, _ = self.run_case(spec)
                self.assertEqual(result["verified_instances"], 0)
                self.assertEqual(result["attempted_instances"], 2)
                self.assertTrue(all(r["root_count"] is None for r in result["results"]))
                self.assertEqual(len(events), 2)

    def test_cold_mode_restarts_worker(self):
        _, _, output = self.run_case(manifest(mode="cold"))
        self.assertEqual(len(list((output / "backend-0").glob("*.requests.jsonl"))), 2)

    def test_warm_baseline_uses_same_worker_without_traces(self):
        result, events, output = self.run_case(manifest(mode="warm"))
        self.assertEqual(len(list((output / "backend-0").glob("*.requests.jsonl"))), 1)
        self.assertEqual(result["trace_apply_attempts"], 0)
        self.assertEqual([e["operation"] for e in events if e["operation"] != "basis_verification"],
                         ["solve", "solve"])

    def test_rank_counts_independence_in_declared_field(self):
        rank = Rank(3, 2)
        self.assertEqual(rank.add([[1, 1], [2, 2], [0, 0]]), 1)
        self.assertEqual(rank.add([[1, 2]]), 1)
        self.assertEqual(rank.add([[2, 1]]), 0)
        with self.assertRaises(ValueError):
            Rank(4, 2)
        with self.assertRaises(ValueError):
            rank.add([[1, 0], [1]])
        self.assertEqual(len(rank.pivots), 2)

    def test_independent_verification_and_rank_are_charged(self):
        spec = manifest()
        spec["relation_verifier"] = {"modulus": 3, "width": 2,
            "command": [sys.executable, "-c", FAKE, "ok"],
            "provenance": "test-only relation verifier double"}
        result, _, _ = self.run_case(spec)
        self.assertEqual(result["verified_relation_rank"], 1)
        self.assertEqual([r["relation_rank_increment"] for r in result["results"]], [1, 0])
        self.assertIn("verify_relations", result["phase_seconds"])
        self.assertIn("relation_rank", result["phase_seconds"])
        self.assertAlmostEqual(result["verified_rank_per_total_second"],
                               1 / result["total_wall_seconds"])

    def test_manifest_validation(self):
        for key, value in (("nvars", 13), ("field", "GF(3)"), ("order", "lex")):
            spec = manifest()
            spec["ring"][key] = value
            with self.assertRaises(ValueError):
                validate(spec)
        spec = manifest()
        spec["instances"][1]["id"] = "a"
        with self.assertRaises(ValueError):
            validate(spec)

    def test_sympy_adapter(self):
        spec = json.loads(Path("groebner_compare/smoke.json").read_text())
        spec["backends"][0]["command"][0] = sys.executable
        result, _, _ = self.run_case(spec)
        self.assertEqual(result["verified_instances"], 4)

    @unittest.skipUnless(Path("experiments/pdp-scaling/boolean_f5b.py").is_file(),
                         "BooleanF5B adapter belongs to cryptanalysis")
    def test_repository_f5b_adapter(self):
        spec = json.loads(Path("groebner_compare/smoke.json").read_text())
        spec["backends"][0]["command"] = [sys.executable, "-m", "groebner_compare.worker", "repository-f5b"]
        result, _, _ = self.run_case(spec)
        self.assertEqual(result["verified_instances"], 4)

    @unittest.skipUnless(os.environ.get("TEST_GROEBNER_SAGE"), "Sage integration job only")
    def test_polybori_adapter(self):
        spec = json.loads(Path("groebner_compare/smoke.json").read_text())
        spec["backends"][0]["command"] = ["sage", "-python", "-m", "groebner_compare.worker", "polybori"]
        result, events, _ = self.run_case(spec)
        self.assertEqual(result["verified_instances"], 4, json.dumps(events))

    @unittest.skipUnless(os.environ.get("TEST_GROEBNER_JULIA"), "Julia integration job only")
    def test_julia_adapter(self):
        spec = json.loads(Path("groebner_compare/smoke.json").read_text())
        # Identical repeat exercises apply; changed constant exercises rejection.
        repeat = copy.deepcopy(spec["instances"][0])
        repeat["id"] = "same-support-control"
        spec["instances"].insert(1, repeat)
        spec["watchdog_seconds"] = 180
        spec["backends"] = [{"id": "julia", "mode": "learn_apply",
            "command": ["julia", "--project=.ci-julia", "groebner_compare/worker.jl"],
            "provenance": "CI resolved packages saved as artifact"}]
        result, events, _ = self.run_case(spec)
        self.assertEqual(result["verified_instances"], 5, json.dumps(events))
        self.assertTrue(any(e["operation"] == "apply" and e["status"] == "ok" for e in events))
        self.assertIn("fallback", result["phase_seconds"])


if __name__ == "__main__":
    unittest.main()
