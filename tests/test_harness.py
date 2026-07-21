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


def test_yield_measurement_and_structured_bases():
    from harness import semaev
    inst = generate_instance(seed=1, field_bits=12)
    rb = semaev.factor_base_random(inst, 20)
    ib = semaev.factor_base_interval(inst, 20)
    ab = semaev.factor_base_ap(inst, 20, step=3)
    assert len(rb) == 20 and len(ib) == 20 and len(ab) == 20
    E = inst.curve()
    assert all(E.lift_x(x) is not None for x in rb + ib + ab)
    # interval base is consecutive on-curve x-coordinates
    assert ib == sorted(ib)
    y, found, cert = semaev.measure_yield(inst, rb, 100)
    assert 0.0 <= y <= 1.0 and found >= 0
    if cert:
        assert semaev.verify_decomposition_certificate(cert)


def test_powered_yield_counts_and_ci():
    from harness import semaev
    from harness.run_yield_powered import katz_log_ci
    inst = generate_instance(seed=1, field_bits=12)
    rb = semaev.factor_base_random(inst, 20)
    f, n, cert = semaev.measure_yield_counts(inst, rb, 500)
    assert 0 <= f <= n <= 500 and n > 0
    if cert:
        assert semaev.verify_decomposition_certificate(cert)
    # Katz CI: undefined on a zero count; ordered and bracketing otherwise
    assert katz_log_ci(0, 10, 5, 10) == (None, None, None)
    r, lo, hi = katz_log_ci(40, 100, 30, 100)
    assert lo < r < hi
    # larger counts -> tighter interval than tiny counts at the same ratio
    _, lo_big, hi_big = katz_log_ci(400, 1000, 300, 1000)
    _, lo_small, hi_small = katz_log_ci(4, 10, 3, 10)
    assert (hi_big - lo_big) < (hi_small - lo_small)
