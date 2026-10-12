"""Rank-only instrument: same pivcols as the dense column pass; own certificates."""
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy", reason="gf2 extra")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.gf2 import kernels, rank_only  # noqa: E402
from crypto_autoresearcher.gf2.closure import Closure  # noqa: E402


def _pack(dense, C):
    R = dense.shape[0]
    W = (C + 63) // 64
    if W * 64 - C:
        dense = np.concatenate([dense, np.zeros((R, W * 64 - C), np.uint8)], axis=1)
    return np.ascontiguousarray(np.packbits(dense, axis=1, bitorder="little")).view(np.uint64).reshape(R, W).copy()


def _cases(seed=1, n=40):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        R, C = int(rng.integers(1, 80)), int(rng.integers(1, 120))
        dens = float(rng.choice([0.02, 0.05, 0.15, 0.4]))
        yield _pack((rng.random((R, C)) < dens).astype(np.uint8), C), C
    for _ in range(10):
        R, C = int(rng.integers(20, 60)), int(rng.integers(30, 90))
        base = (rng.random((8, C)) < 0.25).astype(np.uint8)
        comb = (rng.random((R, 8)) < 0.35).astype(np.uint8)
        yield _pack((comb @ base % 2).astype(np.uint8), C), C


def test_sparse_pivcols_match_dense_reference():
    for M, C in _cases():
        ref = rank_only.dense_reference_pivcols(M, C)
        res = rank_only.rank_profile(M, C, want_cert=True, algorithm="sparse")
        assert res.pivcols == ref, (res.backend, res.rank, len(ref))
        assert res.rank == len(ref)
        assert res.certificate is not None
        assert rank_only.verify_certificate(M, C, res.certificate)


def test_dense_algorithm_matches_column_pass():
    for M, C in _cases(seed=2, n=20):
        log = kernels.column_pass(M.copy(), C, keep_ops=False)
        res = rank_only.rank_profile(M, C, want_cert=False, algorithm="dense")
        assert res.pivcols == tuple(int(x) for x in log.cs.tolist())
        assert res.backend == "dense"


def test_auto_matches_on_small_and_forces_dense_on_large():
    rng = np.random.default_rng(3)
    M, C = _pack((rng.random((30, 40)) < 0.1).astype(np.uint8), 40), 40
    res = rank_only.rank_profile(M, C, want_cert=True, algorithm="auto")
    assert res.pivcols == rank_only.dense_reference_pivcols(M, C)
    # Force the large-matrix auto path without building a huge array: patch the threshold.
    old = rank_only.SPARSE_MAX_WORDS
    try:
        rank_only.SPARSE_MAX_WORDS = 0
        res2 = rank_only.rank_profile(M, C, want_cert=False, algorithm="auto")
        assert res2.backend == "dense"
        assert res2.pivcols == res.pivcols
    finally:
        rank_only.SPARSE_MAX_WORDS = old


def test_macaulay_rank_matches_closure_rank():
    eqs = [[0b11, 0b100, 0], [0b101, 0b1], [0b110, 0b10, 0]]
    cl = Closure(4, 3, 3)
    M = cl.build_M(eqs)
    log = kernels.column_pass(M.copy(), cl.C, keep_ops=False)
    rec = rank_only.macaulay_rank(eqs, 4, 3, 3, want_cert=True, algorithm="sparse")
    assert rec["rank"] == int(log.K)
    assert rec["pivcols"] == [int(x) for x in log.cs.tolist()]
    assert rec["one"] == (cl.const_col in rec["pivcols"])
    assert rec["instrument"] == "gf2.rank_only"
    assert rec.get("certificate_ok") is True


def test_verify_rejects_tampered_certificate():
    rng = np.random.default_rng(4)
    M, C = _pack((rng.random((25, 40)) < 0.12).astype(np.uint8), 40), 40
    res = rank_only.rank_profile(M, C, want_cert=True, algorithm="sparse")
    bad = rank_only.RankCertificate(
        pivcols=res.certificate.pivcols,
        pivot_rows=res.certificate.pivot_rows,
        comb=tuple(c[:-1] if c else c for c in res.certificate.comb),
    )
    if any(res.certificate.comb):
        assert not rank_only.verify_certificate(M, C, bad)
