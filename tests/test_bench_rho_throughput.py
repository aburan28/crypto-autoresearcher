"""The benchmark's own guard: every implementation must reproduce the
reference walk exactly. A throughput number from an implementation that
computes something other than a rho step is worse than no number at all.

Fast by construction (tiny case); the C and GPU legs skip cleanly and
visibly where no toolchain or device exists.
"""
import pytest

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


@pytest.mark.parametrize("nbranch", [0, 1, 3, 31, 33, 100])
def test_non_power_of_two_branch_table_is_rejected(nbranch):
    """All three implementations index the branch table with `x & (n-1)`, so a
    non-power-of-two table is an out-of-bounds read in the C and CUDA paths,
    not merely a skewed branch distribution. It must never reach them."""
    with pytest.raises(ValueError, match="power of two"):
        build_case(1, nbranch=nbranch, nwalks=2, nsteps=1, dp_bits=0)


@pytest.mark.parametrize("dp_bits", [-1, 64, 999])
def test_out_of_range_dp_bits_is_rejected(dp_bits):
    """dp_bits >= 64 would shift a u64 by its own width: UB in C, and a
    silently different DP count in Python."""
    with pytest.raises(ValueError, match="dp_bits"):
        build_case(1, nbranch=32, nwalks=2, nsteps=1, dp_bits=dp_bits)


def test_power_of_two_branch_tables_are_accepted():
    for nbranch in (2, 4, 16, 32, 64):
        c = build_case(3, nbranch=nbranch, nwalks=2, nsteps=2, dp_bits=0)
        assert len(c.tx) == nbranch
        assert walk_batched(c) == walk_reference(c)
