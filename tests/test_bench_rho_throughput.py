"""The benchmark's own guard: every implementation must reproduce the
reference walk exactly. A throughput number from an implementation that
computes something other than a rho step is worse than no number at all.

Fast by construction (tiny case); the C and GPU legs skip cleanly and
visibly where no toolchain or device exists.
"""
from harness.bench_rho_throughput import (
    A_COEF, B_COEF, P, build_case, self_test, walk_batched, walk_reference,
)


def test_implementations_agree_with_reference():
    errors, _notes = self_test(nwalks=6, nsteps=16, seed=4242)
    assert not errors, "; ".join(errors)


def test_batched_matches_reference_on_a_second_seed():
    c = build_case(99, nbranch=32, nwalks=8, nsteps=24, dp_bits=8)
    assert walk_batched(c) == walk_reference(c)


def test_walk_stays_on_curve():
    c = build_case(7, nbranch=32, nwalks=4, nsteps=20, dp_bits=0)
    x, y, _a, _b, _dps = walk_reference(c)
    for xi, yi in zip(x, y):
        assert (yi * yi - xi**3 - A_COEF * xi - B_COEF) % P == 0


def test_batching_does_not_change_the_distinguished_point_count():
    c = build_case(11, nbranch=32, nwalks=16, nsteps=40, dp_bits=4)
    assert walk_reference(c)[4] == walk_batched(c)[4]
