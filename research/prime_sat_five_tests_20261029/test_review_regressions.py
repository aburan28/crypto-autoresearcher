import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("sat") / "solver.py"
SPEC = importlib.util.spec_from_file_location("prime_five_sat_solver", MODULE_PATH)
solver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(solver)


class FakeRing:
    def __init__(self, n):
        self.n = n
        self.counts = {}

    @staticmethod
    def eval(_poly, _bits):
        return 0

    @staticmethod
    def clean(poly):
        return poly


def fake_instance(p, s, target, a=1, b=1, curve_membership=False):
    return {"ring": FakeRing(1), "polynomials": [{}],
            "metadata": {"p": p, "s": s, "target": target, "a": a,
                         "b": b, "curve_membership": curve_membership}}


def fake_learned(ring, generators, *_args):
    status = "unsat" if ring.n == 2 and len(generators) > 1 else "sat"
    return {"status": status, "model": 0, "learned": []}


def test_verifier_recomputes_oracle_totals():
    with (patch.object(solver, "generate_s3", side_effect=fake_instance),
          patch.object(solver, "learned_solve", side_effect=fake_learned),
          patch.object(solver, "verify_learning", return_value=True),
          patch.object(solver, "z3_solve", return_value={"status": "sat", "model": 0}),
          patch.object(solver, "cvc5_solve", return_value={"status": "sat", "model": 0}),
          patch.object(solver, "lift_check", return_value={})):
        data = solver.run({"primes": [17], "digits": [1], "targets": [0]})
        assert solver.verify(data)
        data["rows"][0]["oracle_solution_count"] = 1_000_000
        data["rows"][0]["oracle_assignments"] = 0
        assert not solver.verify(data)


def test_failure_checkpoint_retains_rows_and_failing_cell():
    backend_calls = 0

    def backend(*_args):
        nonlocal backend_calls
        backend_calls += 1
        if backend_calls == 2:
            raise RuntimeError("injected backend failure")
        return {"status": "sat", "model": 0}

    checkpoints = []
    with (patch.object(solver, "generate_s3", side_effect=fake_instance),
          patch.object(solver, "learned_solve", side_effect=fake_learned),
          patch.object(solver, "verify_learning", return_value=True),
          patch.object(solver, "z3_solve", side_effect=backend),
          patch.object(solver, "cvc5_solve", return_value={"status": "sat", "model": 0}),
          patch.object(solver, "lift_check", return_value={})):
        try:
            solver.run({"primes": [17], "digits": [1], "targets": [0]}, checkpoint=checkpoints.append)
        except RuntimeError as exc:
            assert str(exc) == "injected backend failure"
        else:
            raise AssertionError("injected failure did not propagate")
    failure = checkpoints[-1]
    assert failure["status"] == "failed"
    assert len(failure["completed_rows"]) == 1
    assert failure["failing_cell"]["input"]["curve_membership"] is True
    assert failure["failing_cell"]["oracle_assignments"] == 2


def test_geometry_checker_rejects_false_ineligible_label():
    geometry_spec = importlib.util.spec_from_file_location(
        "prime_five_geometry_checker", Path(__file__).with_name("geometry") / "check_geometry.py")
    checker = importlib.util.module_from_spec(geometry_spec)
    geometry_spec.loader.exec_module(checker)
    curve = checker.expected_curve(17, 65536)
    assert curve["status"] == "selected"
    coset = checker.expected_coset(curve, 8, False)
    assert coset["status"] == "selected"
    row = {"kind": "empty_squarefree_control", "input": {"p": 17, "d": 8},
           "status": "ineligible_retained", "curve": curve, "coset": coset}
    result = {"config": {"graeffe": {"maximum_curve_candidates": 65536}},
              "graeffe": {"cells": [row]}, "saturation": {"cells": []}}
    with patch.dict(sys.modules, {"sympy": SimpleNamespace(Symbol=lambda _name: object())}):
        assert not checker.check(result)["valid"]
