"""Independent, fixed software assertions for TASK-20261029-3c8d06.

No solver, experiment, benchmark, sweep, or arithmetic UNSAT certification.
The permitted tiny exhaustive oracles apply only to frozen fixtures.
"""
import argparse
import contextlib
import copy
import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest


TASK = "TASK-20261029-3c8d06"
ROOT = Path(__file__).resolve().parents[3]
SELF = Path(__file__).resolve()
PYTHON = "/home/ec2-user/prime-sat-research-venv/bin/python"
OLD = "research/prime_sat_costbridge_20261029/"
NEW = "research/prime_sat_costbridge_controls_20261029/"
EXPECTED = {
    OLD + "reference.py": "a05b0c30df5b5b4b9763e6bb422ee5f9212d5345aa573448827cd830ca4678ad",
    OLD + "check_reference.py": "af276a95753493ba8885b19f85cf9d53fe5f52746990256b0d04795aff68451e",
    OLD + "test_reference.py": "7588f9fb28c793f4eb4f7758504b4c0de3d48bdceb42fd8f20ab883cbffce883",
    OLD + "unit-test-results.json": "10598ae6b78d998b0fdb40a9e3c012b0f8f4ead6cdd19a45b1b7e03adbdef4c3",
    NEW + "prefix_cover.py": "10ef5f615218649660eaf62212e9dcb58045f08ebb414663a4c14ed63c090c2c",
}
REGRESSION = [PYTHON, "-B", "-m", "unittest", "discover", "-s",
              OLD.rstrip("/"), "-p", "test_reference.py", "-v"]
ASSERTIONS = []
OBSERVATIONS = []
MUTANTS = []
reference = checker = cover = None


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def canonical_digest(value):
    return sha_bytes(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def source_hashes():
    return {name: sha_bytes((ROOT / name).read_bytes())
            for name in [*EXPECTED, str(SELF.relative_to(ROOT))]}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load_target(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def on_curve(point, spec):
    x, y = point
    return (y * y - (x * x + spec["a"]) * x - spec["b"]) % spec["p"] == 0


def elementary_add(left, right, spec):
    """Ordinary group law, independently written; inversion uses Fermat."""
    p = spec["p"]
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        numerator, denominator = 3 * x1 * x1 + spec["a"], 2 * y1
    else:
        numerator, denominator = y2 - y1, x2 - x1
    slope = numerator * pow(denominator % p, p - 2, p) % p
    third_x = (slope ** 2 - x1 - x2) % p
    third_y = (y1 + slope * (third_x - x1)) % p
    return third_x, (-third_y) % p


def fixed_group_oracle(spec):
    """Used only for the single fixed p=17 case; no parameter sweep."""
    left = [(x, y) for x in spec["D1"] for y in range(spec["p"])
            if on_curve((x, y), spec)]
    right = [(x, y) for x in spec["D2"] for y in range(spec["p"])
             if on_curve((x, y), spec)]
    target = tuple(spec["target"])
    return sorted({(P[0], Q[0]) for P in left for Q in right
                   if elementary_add(P, Q, spec) == target})


class FixedAssertions(unittest.TestCase):
    def same(self, name, actual, expected):
        passed = actual == expected
        ASSERTIONS.append({"test": self.id(), "assertion": name,
                           "outcome": "holds" if passed else "breaks",
                           "actual": actual, "expected": expected})
        self.assertEqual(actual, expected, name)

    def truth(self, name, actual):
        self.same(name, bool(actual), True)

    def accepted(self, name, spec, result):
        outcome = checker.verify(spec, result)
        self.same(name, outcome["valid"], True)
        OBSERVATIONS.append({"name": name, "mutant": False, "checker": outcome})
        return outcome

    def rejected(self, name, spec, result, finding):
        outcome = checker.verify(spec, result)
        self.same(name + ".valid", outcome["valid"], False)
        self.same(name + ".exact_finding", outcome["findings"], [finding])
        OBSERVATIONS.append({"name": name, "mutant": False, "checker": outcome,
                             "artifact_sha256": canonical_digest(result)})
        return outcome

    def test_01_false_nonroot_isolation(self):
        spec = dict(p=5, a=1, b=1, target=[0, 1], D1=[2], D2=[])
        result = reference.solve(spec)
        self.accepted("false_nonroot.positive", spec, result)
        self.same("false_nonroot.f2", (2 ** 3 + 2 + 1) % 5, 1)
        self.same("false_nonroot.positive_pairs", result["projected_pairs"], [])
        self.same("false_nonroot.positive_witnesses", result["witnesses"], [])
        self.same("false_nonroot.root_row", result["lift_records"],
                  [{"x": 2, "kind": "square", "roots": [1, 4]}])
        self.same("false_nonroot.Z", result["setup"]["nonresidue"], 2)
        bad = copy.deepcopy(result)
        bad["lift_records"] = [{"x": 2, "kind": "nonsquare", "twisted_root": 1}]
        self.same("false_nonroot.digest_unchanged", bad["input_sha256"], canonical_digest(spec))
        self.same("false_nonroot.projected_equality_cannot_distinguish",
                  (bad["projected_pairs"], bad["witnesses"], spec["D2"]), ([], [], []))
        self.rejected("false_nonroot.original_rejection", spec, bad, "invalid nonroot certificate")
        source = (ROOT / (OLD + "check_reference.py")).read_text()
        before = '_require(value != 0 and w != 0 and w*w % p == z*value % p, "invalid nonroot certificate")'
        after = '_require(True, "invalid nonroot certificate")'
        self.same("false_nonroot.mutant_exactly_one_guard", source.count(before), 1)
        weakened = source.replace(before, after)
        namespace = {"__name__": "independent_nonroot_guard_mutant"}
        exec(compile(weakened, "<mutant_nonroot_guard_only>", "exec"), namespace)
        mutant_outcome = namespace["verify"](spec, bad)
        patch = "-" + before + "\n+" + after + "\n"
        MUTANTS.append({"id": "nonroot_guard_only", "mutant": True,
                        "original_source_sha256": sha_bytes(source.encode()),
                        "mutant_source_sha256": sha_bytes(weakened.encode()),
                        "patch_text": patch, "patch_sha256": sha_bytes(patch.encode()),
                        "negative_artifact_sha256": canonical_digest(bad),
                        "observed_checker_output": mutant_outcome,
                        "certification": False,
                        "meaning": "Guard-necessity control only; weakened acceptance is not certification."})
        self.same("false_nonroot.mutant_only_acceptance", mutant_outcome["valid"], True)

    def test_02_rehashed_input_guards(self):
        base = dict(p=5, a=1, b=1, target=[0, 1], D1=[], D2=[])
        zero_base = dict(p=7, a=1, b=0, target=[1, 3], D1=[], D2=[])
        cases = [
            ("duplicate", base, {"D1": [0, 0]}, "duplicate domain coordinate"),
            ("singular", base, {"a": 0, "b": 0}, "singular curve"),
            ("offcurve", base, {"target": [0, 2]}, "point off curve"),
            ("zero_ordinate", zero_base, {"target": [0, 0]}, "target has zero ordinate"),
        ]
        for label, valid_spec, mutation, finding in cases:
            with self.subTest(case=label):
                result = reference.solve(valid_spec)
                self.accepted("rehash." + label + ".base", valid_spec, result)
                malformed = copy.deepcopy(valid_spec)
                malformed.update(mutation)
                result["input_sha256"] = canonical_digest(malformed)
                independent_encoding = json.dumps(malformed, sort_keys=True, separators=(",", ":")).encode()
                self.same("rehash." + label + ".digest_matches",
                          result["input_sha256"], hashlib.sha256(independent_encoding).hexdigest())
                self.rejected("rehash." + label, malformed, result, finding)
                raised = None
                try:
                    reference.solve(malformed)
                except ValueError as error:
                    raised = str(error)
                self.truth("rehash." + label + ".producer_rejects", raised is not None)
                OBSERVATIONS.append({"name": "rehash." + label + ".producer_error",
                                     "mutant": False, "exception_type": "ValueError", "message": raised})

    def test_03_oncurve_sum_guards(self):
        spec = dict(p=5, a=1, b=1, target=[0, 1], D1=[0], D2=[4])
        result = reference.solve(spec)
        self.accepted("sum.positive", spec, result)
        self.same("sum.positive_projection", result["projected_pairs"], [[0, 4]])
        self.same("sum.positive_witness", result["witnesses"], [{"P": [0, 4], "Q": [4, 2]}])
        self.same("sum.positive_elementary_sum", elementary_add((0, 4), (4, 2), spec), (0, 1))
        cases = [
            ("abscissa", [0, 4], [4, 3], "witness sum has wrong abscissa"),
            ("ordinate", [0, 1], [4, 3], "witness sum has wrong ordinate"),
        ]
        for label, P, Q, finding in cases:
            with self.subTest(case=label):
                self.truth("sum." + label + ".P_on_curve", on_curve(P, spec))
                self.truth("sum." + label + ".Q_on_curve", on_curve(Q, spec))
                self.same("sum." + label + ".same_projection", [P[0], Q[0]], [0, 4])
                self.truth("sum." + label + ".same_domains", P[0] in spec["D1"] and Q[0] in spec["D2"])
                bad = copy.deepcopy(result)
                bad["witnesses"] = [{"P": P, "Q": Q}]
                self.same("sum." + label + ".digest", bad["input_sha256"], canonical_digest(spec))
                self.same("sum." + label + ".unchanged_projected_set", bad["projected_pairs"], [[0, 4]])
                total = elementary_add(tuple(P), tuple(Q), spec)
                if label == "abscissa":
                    self.truth("sum.abscissa.elementary_wrong_x", total is not None and total[0] != 0)
                else:
                    self.same("sum.ordinate.negates_both_summands",
                              (P, Q), ([0, (-4) % 5], [4, (-2) % 5]))
                    self.same("sum.ordinate.elementary_minus_R", total, (0, 4))
                self.rejected("sum." + label, spec, bad, finding)

    def test_04_order_three_exception(self):
        spec = dict(p=7, a=0, b=1, target=[0, 1], D1=[0], D2=[0])
        R = (0, 1)
        self.truth("order3.R_on_curve", on_curve(R, spec))
        twice = elementary_add(R, R, spec)
        self.same("order3.2R_is_minus_R", twice, (0, 6))
        self.same("order3.3R_is_infinity", elementary_add(twice, R, spec), None)
        self.same("order3.minus_R_pair_sum", elementary_add((0, 6), (0, 6), spec), R)
        result = reference.solve(spec)
        self.accepted("order3.positive", spec, result)
        self.same("order3.unique_exceptional_projection", result["projected_pairs"], [[0, 0]])
        self.same("order3.minus_R_witness", result["witnesses"], [{"P": [0, 6], "Q": [0, 6]}])
        bad = copy.deepcopy(result)
        bad["projected_pairs"], bad["witnesses"] = [], []
        self.same("order3.lift_coverage_retained", bad["lift_records"], result["lift_records"])
        self.same("order3.input_digest_retained", bad["input_sha256"], canonical_digest(spec))
        self.rejected("order3.omission", spec, bad, "projected set incomplete or spurious")

    def test_05_high_valuation_root_path(self):
        spec = dict(p=17, a=1, b=1, target=[0, 1], D1=list(range(17)), D2=list(range(17)))
        odd, valuation = 16, 0
        while odd % 2 == 0:
            odd //= 2
            valuation += 1
        self.same("p17.v2_p_minus_1", valuation, 4)
        self.same("p17.Euler2", pow(2, 8, 17), 1)
        self.same("p17.Euler3", pow(3, 8, 17), 16)
        result = reference.solve(spec)
        self.same("p17.setup", result["setup"],
                  {"method": "deterministic_scan", "nonresidue": 3, "euler_probes": 2})
        checked = self.accepted("p17.original_checker", spec, result)
        self.same("p17.no_authenticated_execution_counts", checked["execution_counts_verified"], False)
        oracle = fixed_group_oracle(spec)
        self.same("p17.projected_set_independent_group_oracle",
                  [tuple(pair) for pair in result["projected_pairs"]], oracle)
        self.same("p17.exact_lift_coordinate_coverage", [row["x"] for row in result["lift_records"]], list(range(17)))
        for row in result["lift_records"]:
            x = row["x"]
            value = (x ** 3 + x + 1) % 17
            roots = [y for y in range(17) if y * y % 17 == value]
            if roots:
                self.same("p17.x%d.both_signs" % x, row["roots"], roots)
                self.same("p17.x%d.classification" % x, row["kind"], "zero" if value == 0 else "square")
            else:
                self.same("p17.x%d.nonsquare_classification" % x, row["kind"], "nonsquare")
                self.truth("p17.x%d.nonzero_twisted_root" % x, type(row["twisted_root"]) is int and 0 < row["twisted_root"] < 17)
                self.same("p17.x%d.twisted_certificate" % x, row["twisted_root"] ** 2 % 17, 3 * value % 17)
        for index, witness in enumerate(result["witnesses"]):
            self.truth("p17.witness%d.P_on_curve" % index, on_curve(witness["P"], spec))
            self.truth("p17.witness%d.Q_on_curve" % index, on_curve(witness["Q"], spec))
            self.same("p17.witness%d.elementary_sum" % index,
                      elementary_add(tuple(witness["P"]), tuple(witness["Q"]), spec), (0, 1))
        root = reference._sqrt_square(9, 17, 3)
        self.same("p17.direct_general_root_squares_to_9", root * root % 17, 9)
        OBSERVATIONS.append({"name": "p17.fixed_outputs", "mutant": False,
                             "result": result, "independent_projected_oracle": oracle,
                             "direct_root_9": root, "setup_count_scope": "setup probes only; no total-operation or timing claim"})

    def test_06_fixed_prefix_coverage(self):
        cases = [
            ("large_cover", dict(n=256, prefixes=[(1, 0), (1, 1)]), True, None),
            ("large_hole", dict(n=256, prefixes=[(1, 0)]), False, 1),
            ("overlap_duplicates", dict(n=4, prefixes=[(1, 0), (3, 0), (1, 0), (1, 1)]), True, None),
            ("empty_prefix", dict(n=256, prefixes=[(0, 0)]), True, None),
            ("empty_zero_cube", dict(n=0, prefixes=[]), False, 0),
            ("aux_boundary", dict(n=4, projected_bits=1, aux_bound=3,
                                   prefixes=[(3, i) for i in (0, 1, 2, 3, 4, 5)]), True, None),
            ("aux_hole", dict(n=4, projected_bits=1, aux_bound=3,
                               prefixes=[(3, i) for i in (0, 1, 2, 3, 4)]), False, 5),
            ("empty_aux_domain", dict(n=4, projected_bits=1, aux_bound=0, prefixes=[]), True, None),
            ("censored_cover", dict(n=4, prefixes=[(2, 0), (2, 1)]), False, None),
        ]
        for label, kwargs, expected_cover, exact_gap in cases:
            with self.subTest(case=label):
                result = cover.verify_cover(**kwargs)
                name = "prefix." + label
                self.same(name + ".covered", result["covered"], expected_cover)
                self.truth(name + ".covered_is_bool", type(result["covered"]) is bool)
                self.truth(name + ".arithmetic_verified_stays_false", result["arithmetic_verified"] is False)
                self.truth(name + ".trie_nodes_canonical", type(result["trie_nodes"]) is int and result["trie_nodes"] >= 1)
                self.truth(name + ".symbolic_node_bound", result["trie_nodes"] <= 1 + sum(d for d, _ in kwargs["prefixes"]))
                n = kwargs["n"]
                m = kwargs.get("projected_bits", n)
                bound = kwargs.get("aux_bound")
                gap = result["uncovered"]
                if expected_cover:
                    self.same(name + ".no_gap", gap, None)
                else:
                    self.truth(name + ".gap_canonical", type(gap) is int and 0 <= gap < (1 << n))
                    self.truth(name + ".gap_in_aux_domain", bound is None or gap >> m < bound)
                    self.truth(name + ".gap_matches_no_prefix",
                               all(gap % (1 << d) != prefix for d, prefix in kwargs["prefixes"]))
                    if exact_gap is not None:
                        self.same(name + ".specified_exact_gap", gap, exact_gap)
                tiny_holes = None
                if n <= 4:
                    tiny_holes = [b for b in range(1 << n)
                                  if (bound is None or b >> m < bound)
                                  and all(b % (1 << d) != prefix for d, prefix in kwargs["prefixes"])]
                    self.same(name + ".independent_tiny_oracle", result["covered"], not tiny_holes)
                    if not expected_cover:
                        self.truth(name + ".gap_in_tiny_oracle", gap in tiny_holes)
                OBSERVATIONS.append({"name": name, "mutant": False, "input": kwargs,
                                     "output": result, "tiny_oracle_holes": tiny_holes,
                                     "cube_enumerated": n <= 4,
                                     "scope": "Boolean coverage only; no arithmetic SAT/UNSAT conclusion"})

    def test_07_fixed_prefix_input_rejections(self):
        cases = [
            ("bool_n", dict(n=True, prefixes=[])),
            ("bool_depth", dict(n=4, prefixes=[(True, 0)])),
            ("bool_prefix", dict(n=4, prefixes=[(1, True)])),
            ("negative_depth", dict(n=4, prefixes=[(-1, 0)])),
            ("depth_above_n", dict(n=4, prefixes=[(5, 0)])),
            ("prefix_at_2powerdepth", dict(n=4, prefixes=[(1, 2)])),
            ("negative_prefix", dict(n=4, prefixes=[(1, -1)])),
            ("projected_bits_above_n", dict(n=4, prefixes=[], projected_bits=5)),
            ("negative_aux_bound", dict(n=4, prefixes=[], projected_bits=1, aux_bound=-1)),
            ("aux_bound_above_capacity", dict(n=4, prefixes=[], projected_bits=1, aux_bound=9)),
            ("bool_aux_bound", dict(n=4, prefixes=[], projected_bits=1, aux_bound=True)),
        ]
        for label, kwargs in cases:
            with self.subTest(case=label):
                message = None
                try:
                    cover.verify_cover(**kwargs)
                except ValueError as error:
                    message = str(error)
                self.truth("prefix.invalid." + label + ".rejected", message is not None)
                OBSERVATIONS.append({"name": "prefix.invalid." + label, "mutant": False,
                                     "input": kwargs, "exception_type": "ValueError", "message": message})


class CapturedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "outcome": "holds"})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.outcomes.append({"test": test.id(), "outcome": "breaks", "diagnostics": self._exc_info_to_string(error, test)})

    def addError(self, test, error):
        super().addError(test, error)
        self.outcomes.append({"test": test.id(), "outcome": "inconclusive", "diagnostics": self._exc_info_to_string(error, test)})

    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        outcome = "holds" if error is None else "breaks"
        row = {"test": test.id(), "subtest": str(subtest), "outcome": outcome}
        if error is not None:
            row["diagnostics"] = self._exc_info_to_string(error, test)
        self.outcomes.append(row)


def main():
    global reference, checker, cover
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    receipt_path = Path(args.receipt).resolve()
    required = SELF.parent / "independent-results.json"
    if receipt_path != required:
        raise SystemExit("receipt must be the declared task output")
    if Path.cwd().resolve() != ROOT:
        raise SystemExit("run from the contracted working directory")
    if not sys.dont_write_bytecode or os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise SystemExit("-B and PYTHONDONTWRITEBYTECODE=1 are required")
    before = source_hashes()
    mismatches = {p: {"expected": expected, "actual": before[p]}
                  for p, expected in EXPECTED.items() if before[p] != expected}
    if mismatches:
        raise SystemExit("Frozen target mismatch before import: " + json.dumps(mismatches))
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        attempts = previous["attempts"]
    else:
        attempts = []
    if len(attempts) + 2 > 4:
        raise SystemExit("four suite invocation budget would be exceeded")
    reference = load_target("independent_target_reference", OLD + "reference.py")
    checker = load_target("independent_target_checker", OLD + "check_reference.py")
    cover = load_target("independent_target_cover", NEW + "prefix_cover.py")
    common = {"cwd": str(ROOT), "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
              "source_sha256_before": before}
    new_attempt = {**common, "invocation": len(attempts) + 1, "kind": "independent_fixed_suite",
                   "argv": [PYTHON, "-B", *sys.argv], "started_at": utc(),
                   "harness_source_sha256": before[str(SELF.relative_to(ROOT))],
                   "harness_source_text": SELF.read_text()}
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(FixedAssertions)
        result = unittest.TextTestRunner(stream=stderr, verbosity=2, resultclass=CapturedResult).run(suite)
    new_attempt.update(ended_at=utc(), stdout=stdout.getvalue(), stderr=stderr.getvalue(),
                       returncode=0 if result.wasSuccessful() else 1,
                       tests_run=result.testsRun, assertion_outcomes=ASSERTIONS,
                       test_outcomes=result.outcomes, observations=OBSERVATIONS,
                       mutant_guard_transformations=MUTANTS, source_sha256_after=source_hashes())
    attempts.append(new_attempt)
    old_before = source_hashes()
    regression_attempt = {"invocation": len(attempts) + 1, "kind": "exact_old_regression",
                          "argv": REGRESSION, "cwd": str(ROOT),
                          "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
                          "started_at": utc(), "source_sha256_before": old_before}
    completed = subprocess.run(REGRESSION, cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                               capture_output=True, text=True, check=False)
    regression_attempt.update(ended_at=utc(), stdout=completed.stdout, stderr=completed.stderr,
                              returncode=completed.returncode, source_sha256_after=source_hashes(),
                              assertion_outcomes=[{"name": "exact_old_regression_exit_zero",
                                                   "outcome": "holds" if completed.returncode == 0 else "breaks"}])
    attempts.append(regression_attempt)
    after = source_hashes()
    immutable = all(a["source_sha256_before"] == a["source_sha256_after"] for a in attempts)
    receipt = {
        "schema": "prime-controls-independent-execution/v1", "actor": "independent_reviewer",
        "task_id": TASK, "recorded_at": utc(), "attempts": attempts,
        "source_sha256_before": before, "source_sha256_after": after,
        "frozen_expected_sha256": EXPECTED, "original_sources_unchanged": immutable,
        "runtime": {"python_executable": sys.executable, "python_version": platform.python_version(),
                    "python_dont_write_bytecode": sys.dont_write_bytecode,
                    "canonical_agent_name": "/root/costbridge_controls_reviewer",
                    "requested_model": "gpt-6.1-sol", "requested_reasoning_effort": "xhigh",
                    "requested_runtime": "native_codex", "requested_fork_turns": "none",
                    "authenticated_model": None, "authenticated_reasoning_effort": None,
                    "opaque_session_uuid": None, "unknown_reason": "No provider probe or opaque session UUID exposed.",
                    "model_verified": False, "provider_probe_run": False, "opus_execution": False},
        "administrative_continuation": [
            "Epoch1 dispatch ended at provider usage-limit failure before outputs or suite invocations; release 0758a12082 reported by coordinator.",
            "Availability-only turn confirmed execution and waited without new scientific reads, writes or suites.",
            "Epoch2 renewed claim 32b0f64120 reported published by coordinator; owner reviewer-prime-controls; session prime-controls-independent; TTL60; branch codex/prime-sat-controls-review-20261030.",
            "Administrative messages conveyed ownership and source identity only, without producer outcomes or mathematical followups."
        ],
        "scientific_runs": 0, "benchmark_runs": 0, "solver_invocations": 0,
        "performance_claim": False, "arithmetic_unsat_certificate": False,
        "suite_invocations": len(attempts), "maximum_software_suite_invocations": 4,
        "scope": "Seven fixed software control families only; prime is assumed; no all-prime, formal, novelty, performance, SAT/UNSAT or ECDLP claim.",
        "overall_returncode": 0 if result.wasSuccessful() and completed.returncode == 0 and immutable else 1,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(new_attempt["stderr"], end="")
    print(completed.stdout, end="")
    print(completed.stderr, end="")
    print(json.dumps({"receipt": str(receipt_path), "suite_invocations": len(attempts),
                      "new_suite_tests": result.testsRun, "named_assertions": len(ASSERTIONS),
                      "new_suite_returncode": new_attempt["returncode"],
                      "old_regression_returncode": completed.returncode,
                      "original_sources_unchanged": immutable,
                      "overall_returncode": receipt["overall_returncode"]}, sort_keys=True))
    return receipt["overall_returncode"]


if __name__ == "__main__":
    raise SystemExit(main())
