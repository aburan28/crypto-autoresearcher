"""Fixed software validation; tiny oracles are confined to this test file."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

import adapter

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "coordination/prime_sat_prefix_adapter_20261030/software-contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text())
FIXTURES = {item["id"]: item for item in CONTRACT["fixed_generic_fixtures"]}
ASSERTIONS, OBSERVATIONS, FORBIDDEN_CALLS = [], [], []


def evaluate(poly, bits, p):
    return sum(coefficient for mask, coefficient in poly.items()
               if int(mask) & bits == int(mask)) % p


def clause_satisfied(clause, bits):
    return any(((bits >> (abs(literal)-1)) & 1) == int(literal > 0) for literal in clause)


def block(bits, depth):
    return [-(i+1) if bits & (1 << i) else i+1 for i in range(depth)]


def add_points(left, right, p, a):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y+v) % p == 0:
        return None
    numerator, denominator = (3*x*x+a, 2*y) if left == right else (v-y, u-x)
    slope = numerator * pow(denominator % p, p-2, p) % p
    out_x = (slope*slope-x-u) % p
    return out_x, (slope*(x-out_x)-y) % p


def point_oracle(cell):
    p, a, b, s = (cell[key] for key in ("p", "a", "b", "s"))
    points = [(x, y) for x in range(1 << s) for y in range(p)
              if (y*y-x*x*x-a*x-b) % p == 0]
    return sorted({(left[0], right[0]) for left in points for right in points
                   if add_points(left, right, p, a) == tuple(cell["target"])})


def fixed_transcript(cell, arm):
    """Only the predeclared <=128-assignment cell, no search engine."""
    legacy = adapter._legacy()
    ring, polynomials, domain = legacy.build(cell, arm)
    assert cell == CONTRACT["fixed_legacy_fixture"]["cell"]
    assert arm in CONTRACT["fixed_legacy_fixture"]["arms"]
    assert 1 << ring.n <= CONTRACT["fixed_legacy_fixture"]["maximum_boolean_assignments_per_arm"]
    models, learned = {}, []
    for bits in range(1 << ring.n):
        if not all(clause_satisfied(clause, bits) for clause in domain):
            continue
        values = [evaluate(poly, bits, ring.p) for poly in polynomials]
        if all(value == 0 for value in values):
            models.setdefault(bits & ((1 << (2*cell["s"]))-1), bits)
        else:
            first = next(i for i, value in enumerate(values) if value)
            certificate = [{} for _ in values]
            certificate[first] = {0: pow(values[first], ring.p-2, ring.p)}
            learned.append({"depth": ring.n, "prefix": bits, "clause": block(bits, ring.n),
                            "certificate": certificate})
    return ring, polynomials, domain, {"status": "complete", "models": list(models.values()),
                                       "learned": learned}


def guard(name):
    def forbidden(*args, **kwargs):
        FORBIDDEN_CALLS.append(name)
        raise AssertionError("forbidden solver/search/oracle entry point: " + name)
    return forbidden


legacy = adapter._legacy()
for _name in ("solve", "refute", "census", "reference", "controls", "verify", "run", "Minisat22"):
    if hasattr(legacy, _name):
        setattr(legacy, _name, guard("encoding." + _name))
sys.modules["core"].refute = guard("core.refute")
import pysat.solvers
pysat.solvers.Minisat22 = guard("pysat.Minisat22")
pysat.solvers.Solver = guard("pysat.Solver")


class AdapterControls(unittest.TestCase):
    def check(self, name, condition, details=None):
        ASSERTIONS.append({"name": name, "passed": bool(condition), "details": details})
        self.assertTrue(condition, name)

    def reject(self, name, data):
        try:
            adapter.verify_transcript(**data)
        except ValueError as error:
            self.check(name, True, {"error": str(error)})
        else:
            self.check(name, False, {"error": "invalid input accepted"})

    def test_fixed_generic(self):
        for name, fixture in FIXTURES.items():
            with self.subTest(fixture=name):
                data = copy.deepcopy(fixture["input"])
                data["answer"] = copy.deepcopy(fixture["answer"])
                before = copy.deepcopy(data)
                result = adapter.verify_transcript(**data)
                self.check(name + ":valid", result["valid"])
                self.check(name + ":input_unchanged", data == before)
                self.check(name + ":status", result["declared_status"] == data["answer"]["status"])
                self.check(name + ":prime_premise", result["prime_field_verified"] is False)
                complete = name != "censored_gap"
                self.check(name + ":coverage", result["cover_complete"] is complete)
                self.check(name + ":declared_completion", result["projected_model_set_complete"] is
                           (complete and data["answer"]["status"] == "complete"))
                if name == "censored_gap":
                    self.check(name + ":gap", result["uncovered"] == 2)
                if data["n"] <= 5:
                    roots = [bits for bits in range(1 << data["n"])
                             if all(clause_satisfied(c, bits) for c in data["domain_cnf"])
                             and all(evaluate(poly, bits, data["p"]) == 0 for poly in data["polynomials"])]
                    expected = sorted({bits & ((1 << data["projected_bits"])-1) for bits in roots})
                    self.check(name + ":sound_projection", set(result["projected_models"]) <= set(expected))
                    if result["projected_model_set_complete"]:
                        self.check(name + ":exact_projection", result["projected_models"] == expected)
                    if name == "auxiliary_fiber_projection_only":
                        self.check(name + ":full_roots_are_not_output", roots == [0, 2, 4, 6]
                                   and len(data["answer"]["models"]) == 2)
                if name == "large_root_refutation":
                    self.check(name + ":one_node", result["costs"]["coverage"]["trie_nodes"] == 1)
                OBSERVATIONS.append({"fixture": name, "verification": result})

    def test_malformed_schema(self):
        base = {**copy.deepcopy(FIXTURES["complete_projected_roots"]["input"]),
                "answer": copy.deepcopy(FIXTURES["complete_projected_roots"]["answer"])}
        def case(name, modify):
            data = copy.deepcopy(base)
            modify(data)
            self.reject("schema:" + name, data)
        for key in ("p", "n", "projected_bits"):
            for value in (True, 2.0):
                case(key + ":" + repr(value), lambda d, k=key, v=value: d.update({k: v}))
        for key, value in (("p", 1), ("n", -1), ("projected_bits", -1), ("projected_bits", 3)):
            case(key + ":" + str(value), lambda d, k=key, v=value: d.update({k: v}))
        for mask in (True, 1.0, -1, 4, "01", "+1", "-1", "1.0", ""):
            case("mask:" + repr(mask), lambda d, v=mask: d.update(polynomials=[{v: 1}]))
        case("mask_alias", lambda d: d.update(polynomials=[{1: 1, "1": 1}]))
        for coefficient in (True, 1.0, 0, -1, 5, 6):
            case("coefficient:" + repr(coefficient), lambda d, v=coefficient: d.update(polynomials=[{1: v}]))
        for key, value in (("polynomials", {}), ("polynomials", [None]), ("domain_cnf", {})):
            case("container:" + key + repr(value), lambda d, k=key, v=value: d.update({k: v}))
        for key in ("models", "learned"):
            case("answer_container:" + key, lambda d, k=key: d["answer"].update({k: {}}))
        for key in ("status", "models", "learned"):
            case("missing:" + key, lambda d, k=key: d["answer"].pop(k))
        for key in ("depth", "prefix", "clause", "certificate"):
            case("entry_missing:" + key, lambda d, k=key: d["answer"]["learned"][0].pop(k))
        case("answer_not_mapping", lambda d: d.update(answer=[]))
        case("entry_not_mapping", lambda d: d["answer"].update(learned=[None]))
        case("status_unknown", lambda d: d["answer"].update(status="unsat"))
        case("status_bool", lambda d: d["answer"].update(status=True))
        for certificate in (None, {}, [], [{}], [{}, {}], [None]):
            case("certificate:" + repr(certificate),
                 lambda d, v=certificate: d["answer"]["learned"][0].update(certificate=v))
        for key in ("depth", "prefix"):
            for value in (True, 1.0, -1, 3):
                case(key + ":" + repr(value), lambda d, k=key, v=value: d["answer"]["learned"][0].update({k: v}))
        for clause in ([1], [], [-1, -2], [0], [-3], [-1, -1], [True], [-1.0]):
            case("clause:" + repr(clause), lambda d, v=clause: d["answer"]["learned"][0].update(clause=v))
        for model in (True, 0.0, -1, 4, 1):
            case("model:" + repr(model), lambda d, v=model: d["answer"].update(models=[v]))
        case("corrupt_multiplier", lambda d: d["answer"]["learned"][0].update(certificate=[{0: 2}]))
        case("clause_order", lambda d: d["answer"]["learned"][0].update(depth=2, prefix=1, clause=[2, -1]))
        case("multiplier_mask_alias", lambda d: d["answer"]["learned"][0].update(certificate=[{0: 1, "0": 1}]))
        case("false_restriction", lambda d: d["answer"]["learned"][0].update(prefix=0, clause=[1]))
        closing = copy.deepcopy(FIXTURES["global_refutation_nonconstant_multipliers"])
        closing["answer"]["learned"].append({"depth": True})
        self.reject("schema:malformed_after_closure", {**closing["input"], "answer": closing["answer"]})

    def test_projection_and_domain(self):
        def data(name):
            fixture = copy.deepcopy(FIXTURES[name])
            return {**fixture["input"], "answer": fixture["answer"]}
        duplicate = data("auxiliary_fiber_projection_only")
        duplicate["answer"]["models"].append(4)
        self.reject("models:repeated_projection_distinct_aux", duplicate)
        missing = data("complete_projected_roots")
        missing["answer"]["models"].remove(2)
        self.reject("models:missing_complete_projection", missing)
        missing["answer"]["status"] = "censored"
        report = adapter.verify_transcript(**missing)
        self.check("models:missing_censored_accepted", report["valid"] and not report["projected_model_set_complete"])
        full = data("complete_projected_roots")
        full["domain_cnf"] = [[1]]
        self.reject("domain:unsupported_full_cube_cnf", full)
        base = data("canonical_aux_upper_bound")
        for name, clauses in (
            ("projected", [[1], [3, -4, -5], [-3, -4, -5]]),
            ("partial", [[-3, 4], [3, -4, -5], [-3, -4, -5]]),
            ("order", [[4, -3, -5], [3, -4, -5], [-3, -4, -5]]),
            ("duplicate_variable", [[-3, -3, -5], [3, -4, -5], [-3, -4, -5]]),
            ("missing", base["domain_cnf"][:-1]),
            ("duplicate_value", base["domain_cnf"][:2] + [base["domain_cnf"][0]]),
            ("valid_value_blocked", [[3, 4, -5], [3, -4, -5], [-3, -4, -5]]),
            ("float_literal", [[-3.0, 4, -5], [3, -4, -5], [-3, -4, -5]]),
            ("bool_literal", [[True, 4, -5], [3, -4, -5], [-3, -4, -5]]),
        ):
            item = copy.deepcopy(base)
            item["domain_cnf"] = clauses
            self.reject("domain:" + name, item)
        for bound in (-1, 9, True, 5.0):
            item = copy.deepcopy(base)
            item["aux_bound"] = bound
            self.reject("domain:bound:" + repr(bound), item)
        item = copy.deepcopy(base)
        item["answer"]["models"] = [20]
        self.reject("domain:model_outside_aux_bound", item)
        empty = data("empty_auxiliary_domain")
        empty["answer"]["learned"] = [{"depth": 0, "prefix": 0, "clause": [], "certificate": None}]
        self.reject("domain:malformed_even_when_empty", empty)

    def test_legacy_compatibility(self):
        cell = CONTRACT["fixed_legacy_fixture"]["cell"]
        expected = point_oracle(cell)
        self.check("legacy:known_projection", (2, 3) in expected)
        for arm in CONTRACT["fixed_legacy_fixture"]["arms"]:
            with self.subTest(arm=arm):
                ring, polynomials, domain, transcript = fixed_transcript(cell, arm)
                self.check(arm + ":fixed_model14", 14 in transcript["models"])
                self.check(arm + ":fixed_bad_leaf0", any(row["prefix"] == 0 for row in transcript["learned"]))
                old_costs = legacy.verify_search(cell, ring, polynomials, domain, transcript, expected)
                report = adapter.verify_encoding_search(cell, arm, transcript)
                self.check(arm + ":same_complete_projections", report["coordinate_pairs"] == [list(pair) for pair in expected])
                self.check(arm + ":complete", report["projected_model_set_complete"])
                self.check(arm + ":separate_costs", "construction" in report["costs"]
                           and "witness_reconstruction_and_check" in report["costs"])
                for witness in report["witnesses"]:
                    P, Q = (tuple(point) for point in witness["points"])
                    self.check(arm + ":witness:" + str(witness["x"]),
                               all((y*y-x*x*x-cell["a"]*x-cell["b"]) % cell["p"] == 0 for x, y in (P, Q))
                               and add_points(P, Q, cell["p"], cell["a"]) == tuple(cell["target"]))
                as_json = json.loads(json.dumps(transcript))
                self.check(arm + ":json_masks", adapter.verify_encoding_search(cell, arm, as_json)["coordinate_pairs"] == report["coordinate_pairs"])
                censored = copy.deepcopy(transcript)
                censored["status"] = "censored"
                censored["models"].remove(14)
                legacy.verify_search(cell, ring, polynomials, domain, censored, expected)
                checked = adapter.verify_encoding_search(cell, arm, censored)
                self.check(arm + ":censored_preserved", checked["declared_status"] == "censored"
                           and not checked["projected_model_set_complete"] and not checked["cover_complete"])
                for mutation in ("missing_model14", "missing_leaf0", "bad_multiplier", "invalid_model0", "duplicate_model14"):
                    bad = copy.deepcopy(transcript)
                    if mutation == "missing_model14":
                        bad["models"].remove(14)
                    elif mutation == "missing_leaf0":
                        bad["learned"] = [row for row in bad["learned"] if row["prefix"] != 0]
                    elif mutation == "bad_multiplier":
                        row = next(row for row in bad["learned"] if row["prefix"] == 0)
                        multiplier = next(poly for poly in row["certificate"] if poly)
                        self.check(arm + ":fixed_leaf_inverse1", multiplier == {0: 1})
                        multiplier[0] = 2
                    elif mutation == "invalid_model0":
                        bad["models"].append(0)
                    else:
                        bad["models"].append(14)
                    for label, call in (
                        ("old", lambda: legacy.verify_search(cell, ring, polynomials, domain, bad, expected)),
                        ("new", lambda: adapter.verify_encoding_search(cell, arm, bad)),
                    ):
                        try:
                            call()
                        except (AssertionError, ValueError):
                            self.check(arm + ":" + mutation + ":" + label, True)
                        else:
                            self.check(arm + ":" + mutation + ":" + label, False)
                OBSERVATIONS.append({"fixture": "legacy:" + arm, "expected_pairs": expected,
                                     "transcript_sha256": hashlib.sha256(json.dumps(transcript, sort_keys=True).encode()).hexdigest(),
                                     "old_verification_counters_test_only": old_costs,
                                     "new_verification": report})

    def test_no_solver_guard(self):
        self.check("custody:no_forbidden_entrypoint_called", FORBIDDEN_CALLS == [])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    receipt_path = Path(args.receipt)
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {
        "schema": "prime-prefix-adapter-software-results/v1", "task_id": "TASK-20261030-08faf8",
        "actor": "root producer", "attempts": [], "scientific_runs": 0,
        "benchmark_runs": 0, "solver_invocations": 0, "performance_claim": False}
    if len(receipt["attempts"]) >= 4:
        raise RuntimeError("fixed suite invocation budget exhausted")
    paths = list(CONTRACT["source_integrity"]["frozen_files"]) + [
        str(HERE.relative_to(ROOT) / filename) for filename in ("adapter.py", "test_adapter.py", "README.md")]
    paths.append(str(CONTRACT_PATH.relative_to(ROOT)))
    hashes = lambda: {path: hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths}
    before = hashes()
    for path, expected in CONTRACT["source_integrity"]["frozen_files"].items():
        if before[path] != expected:
            raise RuntimeError("frozen source mismatch: " + path)
    now = lambda: datetime.now(timezone.utc).isoformat()
    start, stream = now(), io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(AdapterControls))
    after = hashes()
    code = int(not result.wasSuccessful() or before != after or bool(FORBIDDEN_CALLS))
    receipt["attempts"].append({"argv": [sys.executable, "-B", *sys.argv], "cwd": str(ROOT),
        "environment": {"PYTHONDONTWRITEBYTECODE": "1", "mechanism": "python -B"},
        "started_at": start, "finished_at": now(), "stdout": "", "stderr": stream.getvalue(),
        "returncode": code, "tests_run": result.testsRun, "assertion_outcomes": ASSERTIONS,
        "observations": OBSERVATIONS, "source_sha256_before": before, "source_sha256_after": after,
        "no_solver_guard": {"passed": not FORBIDDEN_CALLS, "forbidden_calls": FORBIDDEN_CALLS},
        "tiny_oracle_scope": "Only fixed generic n<=5 and p5 four-arm n<=7 fixtures; no scientific samples"})
    receipt["status"] = "passed" if code == 0 else "failed"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(stream.getvalue(), end="")
    print("Receipt:", receipt_path, "status:", receipt["status"], "assertions:", len(ASSERTIONS))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
