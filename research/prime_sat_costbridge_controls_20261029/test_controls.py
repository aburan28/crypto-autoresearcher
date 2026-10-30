"""Fixed software assertions and actual receipts; no scientific solver calls."""
import argparse
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "coordination/prime_sat_costbridge_controls_20261029/software-contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text())
CONTROLS = {row["id"]: row for row in CONTRACT["controls"]}
DETAILS = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reference = load("fixed_reference", ROOT / "research/prime_sat_costbridge_20261029/reference.py")
checker = load("fixed_checker", ROOT / "research/prime_sat_costbridge_20261029/check_reference.py")
cover = load("fixed_cover", HERE / "prefix_cover.py")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def add(P, Q, p, a):
    """Separate tiny-fixture group oracle, never operational search."""
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u and (y + v) % p == 0:
        return None
    num, den = (3*x*x + a, 2*y) if x == u else (v-y, u-x)
    slope = num * pow(den % p, p-2, p) % p
    z = (slope*slope-x-u) % p
    return (z, (slope*(x-z)-y) % p)


def oracle(spec):
    p, a, b = (spec[k] for k in ("p", "a", "b"))
    points = [(x, y) for x in range(p) for y in range(p)
              if (y*y-x*x*x-a*x-b) % p == 0]
    return {(P[0], Q[0]) for P in points for Q in points
            if P[0] in spec["D1"] and Q[0] in spec["D2"]
            and add(P, Q, p, a) == tuple(spec["target"])}


def mutant(messages):
    """In-memory only: a known-unsound control with named guards suppressed."""
    path = ROOT / "research/prime_sat_costbridge_20261029/check_reference.py"
    module = types.ModuleType("deliberately_unsound_guard_control")
    source = path.read_bytes()
    exec(compile(source, str(path), "exec"), module.__dict__)
    patch = ("_original_require = _require\n"
             "def _require(condition, message):\n"
             f"    if message in {tuple(messages)!r}:\n"
             "        return\n"
             "    return _original_require(condition, message)\n")
    exec(compile(patch, "<in-memory-guard-control>", "exec"), module.__dict__)
    DETAILS.append({"mutant": True, "suppressed_messages": messages,
                    "transformation": patch, "transformation_sha256": hashlib.sha256(patch.encode()).hexdigest(),
                    "original_source_sha256": hashlib.sha256(source).hexdigest()})
    return module


class FixedControls(unittest.TestCase):
    def accepted(self, spec):
        result = reference.solve(spec)
        checked = checker.verify(spec, result)
        self.assertTrue(checked["valid"], checked)
        self.assertTrue(checked["completeness_verified"])
        return result

    def rejection(self, spec, result, finding):
        self.assertEqual(result["input_sha256"], digest(spec))
        checked = checker.verify(spec, result)
        self.assertFalse(checked["valid"])
        self.assertEqual(checked["findings"], [finding])
        DETAILS.append({"original_checker": True, "finding": finding,
                        "input_sha256": digest(spec), "valid": checked["valid"]})

    def test_false_nonroot_guard_isolated(self):
        spec = copy.deepcopy(CONTROLS["false_nonroot_isolation"]["input"])
        result = self.accepted(spec)
        self.assertEqual(result["projected_pairs"], [])
        self.assertEqual(result["witnesses"], [])
        self.assertEqual(result["lift_records"][0]["kind"], "square")
        result["lift_records"] = [{"x": 2, "kind": "nonsquare", "twisted_root": 1}]
        self.rejection(spec, result, "invalid nonroot certificate")
        weakened = mutant(["invalid nonroot certificate"])
        self.assertTrue(weakened.verify(spec, result)["valid"])

    def test_invalid_inputs_with_matching_digest(self):
        control = CONTROLS["invalid_input_rehashed"]
        for case in control["cases"]:
            with self.subTest(finding=case["expected"]):
                base = copy.deepcopy(case.get("base_input", control["base_input"]))
                result = self.accepted(base)
                spec = dict(base, **case["mutation"])
                result["input_sha256"] = digest(spec)
                with self.assertRaises(ValueError):
                    reference.solve(spec)
                self.rejection(spec, result, case["expected"])

    def test_oncurve_wrong_sums(self):
        control = CONTROLS["oncurve_wrong_sum"]
        spec = copy.deepcopy(control["input"])
        valid = self.accepted(spec)
        self.assertEqual(valid["projected_pairs"], [[0, 4]])
        for case in control["mutations"]:
            with self.subTest(finding=case["expected"]):
                result = copy.deepcopy(valid)
                result["witnesses"] = [{"P": case["P"], "Q": case["Q"]}]
                for point, domain in ((case["P"], spec["D1"]), (case["Q"], spec["D2"])):
                    x, y = point
                    self.assertIn(x, domain)
                    self.assertEqual((y*y-x*x*x-spec["a"]*x-spec["b"]) % spec["p"], 0)
                self.assertEqual([case["P"][0], case["Q"][0]], [0, 4])
                actual_sum = add(tuple(case["P"]), tuple(case["Q"]), 5, 1)
                self.assertNotEqual(actual_sum, (0, 1))
                if case["expected"].endswith("ordinate"):
                    self.assertEqual(actual_sum, (0, 4))
                self.rejection(spec, result, case["expected"])
                weakened = mutant(["witness sum has wrong abscissa", "witness sum has wrong ordinate"])
                self.assertTrue(weakened.verify(spec, result)["valid"])

    def test_order_three_exception(self):
        spec = copy.deepcopy(CONTROLS["order_three_exception"]["input"])
        self.assertEqual(add((0, 1), (0, 1), 7, 0), (0, 6))
        self.assertIsNone(add((0, 6), (0, 1), 7, 0))
        result = self.accepted(spec)
        self.assertEqual(result["projected_pairs"], [[0, 0]])
        self.assertEqual(result["witnesses"], [{"P": [0, 6], "Q": [0, 6]}])
        result["projected_pairs"], result["witnesses"] = [], []
        self.rejection(spec, result, "projected set incomplete or spurious")

    def test_general_square_root_path(self):
        spec = copy.deepcopy(CONTROLS["tonelli_shanks_high_valuation"]["input"])
        self.assertEqual(17-1, 2**4)
        self.assertEqual((pow(2, 8, 17), pow(3, 8, 17)), (1, 16))
        result = self.accepted(spec)
        self.assertEqual(result["setup"], {"nonresidue": 3, "method": "deterministic_scan", "euler_probes": 2})
        self.assertEqual(set(map(tuple, result["projected_pairs"])), oracle(spec))
        root = reference._sqrt_square(9, 17, 3)
        self.assertEqual(root*root % 17, 9)
        for row in result["lift_records"]:
            value = (row["x"]**3+row["x"]+1) % 17
            roots = [y for y in range(17) if y*y % 17 == value]
            self.assertEqual(row.get("roots", []), roots)
        DETAILS.append({"fixture": "p17", "setup": result["setup"], "direct_root": root,
                        "execution_counts_verified": False})

    def test_prefix_fixed_cases(self):
        for case in CONTRACT["prefix_utility"]["fixed_cases"]:
            with self.subTest(case=case["id"]):
                kwargs = {k: case[k] for k in ("projected_bits", "aux_bound") if k in case}
                result = cover.verify_cover(case["n"], case["prefixes"], **kwargs)
                self.assertIs(result["covered"], case["covered"])
                self.assertIs(result["arithmetic_verified"], False)
                self.assertLessEqual(result["trie_nodes"], 1+sum(d for d, _ in case["prefixes"]))
                if "uncovered" in case:
                    self.assertEqual(result["uncovered"], case["uncovered"])
                m = case.get("projected_bits", case["n"])
                bound = case.get("aux_bound")
                def in_domain(b):
                    return bound is None or b >> m < bound
                def matched(b):
                    return any(b % (1 << d) == p for d, p in case["prefixes"])
                if result["covered"]:
                    self.assertIsNone(result["uncovered"])
                else:
                    gap = result["uncovered"]
                    self.assertTrue(0 <= gap < 1 << case["n"] and in_domain(gap))
                    self.assertFalse(matched(gap))
                if case["n"] <= 4:
                    self.assertEqual(result["covered"], all(matched(b) for b in range(1 << case["n"]) if in_domain(b)))
                DETAILS.append({"prefix_case": case["id"], "result": result,
                                "exhaustive_oracle_used": case["n"] <= 4})

    def test_prefix_invalid_inputs(self):
        cases = [("bool n", True, [], {}), ("bool depth", 2, [[True, 0]], {}),
                 ("bool prefix", 2, [[1, False]], {}), ("negative depth", 2, [[-1, 0]], {}),
                 ("depth>n", 2, [[3, 0]], {}), ("prefix==2^depth", 2, [[1, 2]], {}),
                 ("negative prefix", 2, [[1, -1]], {}), ("projected_bits>n", 2, [], {"projected_bits": 3}),
                 ("negative aux_bound", 2, [], {"aux_bound": -1}),
                 ("aux_bound>2^(n-m)", 2, [], {"projected_bits": 1, "aux_bound": 3}),
                 ("bool aux_bound", 2, [], {"aux_bound": True})]
        self.assertEqual([c[0] for c in cases], CONTRACT["prefix_utility"]["invalid_cases"])
        for name, n, prefixes, kw in cases:
            with self.subTest(case=name), self.assertRaises(ValueError):
                cover.verify_cover(n, prefixes, **kw)


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []

    def addSuccess(self, test):
        self.outcomes.append({"test": test.id(), "outcome": "passed"})
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.outcomes.append({"test": test.id(), "outcome": "failed"})
        super().addFailure(test, err)

    def addError(self, test, err):
        self.outcomes.append({"test": test.id(), "outcome": "error"})
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        self.outcomes.append({"test": subtest.id(), "outcome": "passed" if err is None else "failed"})
        super().addSubTest(test, subtest, err)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()
    paths = list(CONTRACT["source_integrity"]["frozen_files"]) + [
        str(HERE.relative_to(ROOT) / name) for name in ("prefix_cover.py", "test_controls.py", "README.md")]
    paths.append(str(CONTRACT_PATH.relative_to(ROOT)))
    hashes = lambda: {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths}
    before = hashes()
    for path, expected in CONTRACT["source_integrity"]["frozen_files"].items():
        if before[path] != expected:
            raise RuntimeError("frozen source mismatch: " + path)
    receipt_path = Path(args.receipt)
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema": "prime-controls-software-results/v1", "actor": "root producer",
        "task_id": "TASK-20261029-b1dce0", "attempts": [],
        "scientific_runs": 0, "benchmark_runs": 0, "solver_invocations": 0,
        "performance_claim": False}
    if len(receipt["attempts"]) + 2 > 4:
        raise RuntimeError("fixed software invocation budget reached")
    now = lambda: datetime.now(timezone.utc).isoformat()
    start = now()
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(FixedControls))
    after_suite = hashes()
    code = 0 if result.wasSuccessful() and before == after_suite else 1
    receipt["attempts"].append({"argv": CONTRACT["execution"]["producer_command"],
        "cwd": str(ROOT), "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
        "started_at": start, "finished_at": now(), "stdout": "", "stderr": stream.getvalue(),
        "returncode": code, "tests_run": result.testsRun, "assertion_outcomes": result.outcomes,
        "observations": DETAILS, "source_sha256_before": before, "source_sha256_after": after_suite})
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    regression_command = CONTRACT["execution"]["required_regression_command"]
    start = now()
    regression = subprocess.run(regression_command, cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, text=True)
    after = hashes()
    receipt["attempts"].append({"argv": regression_command, "cwd": str(ROOT),
        "environment": {"PYTHONDONTWRITEBYTECODE": "1"}, "started_at": start,
        "finished_at": now(), "stdout": regression.stdout, "stderr": regression.stderr,
        "returncode": regression.returncode, "source_sha256_before": after_suite, "source_sha256_after": after})
    receipt.update(source_sha256_before=before, source_sha256_after=after,
                   status="passed" if code == 0 and regression.returncode == 0 and before == after else "failed")
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(stream.getvalue(), end="")
    print(regression.stdout + regression.stderr, end="")
    print("Receipt:", receipt_path, "status:", receipt["status"])
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
