"""GPU trailing-update kernel equals the CPU reference when a device is present."""
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy", reason="gf2 extra")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.gf2 import gpu as gf2gpu  # noqa: E402


def test_gpu_module_reports_availability_without_raising():
    ok, reason = gf2gpu.available()
    assert isinstance(ok, bool)
    assert isinstance(reason, str)


def test_cpu_tail_chunk_tables_equals_direct():
    rng = np.random.default_rng(0)
    R, W, ch, npiv, nr = 128, 64, 16, 24, 40
    M = rng.integers(0, 2**64, size=(R, W), dtype=np.uint64)
    rows = rng.choice(R, size=nr, replace=False).astype(np.int32)
    cw = (npiv + 63) // 64
    cfs = rng.integers(0, 2**64, size=(nr, cw), dtype=np.uint64)
    if npiv < 64:
        cfs[:, 0] &= (np.uint64(1) << npiv) - np.uint64(1)
    Bs = rng.integers(0, 2**64, size=(npiv, W), dtype=np.uint64)
    A = M.copy()
    B = M.copy()
    gf2gpu.cpu_tail_chunk(A, W, 0, 0, ch, rows, cfs, cw, Bs, W, npiv, True)
    gf2gpu.cpu_tail_chunk(B, W, 0, 0, ch, rows, cfs, cw, Bs, W, npiv, False)
    assert np.array_equal(A, B)
    # idempotent on a second identical call from the same start
    C = M.copy()
    gf2gpu.cpu_tail_chunk(C, W, 0, 0, ch, rows, cfs, cw, Bs, W, npiv, True)
    assert np.array_equal(A, C)


@pytest.mark.skipif(not gf2gpu.available()[0], reason=gf2gpu.available()[1])
def test_gpu_tail_matches_cpu():
    rng = np.random.default_rng(7)
    R, W, ch, npiv, nr = 512, 256, 64, 48, 200
    M = rng.integers(0, 2**64, size=(R, W), dtype=np.uint64)
    rows = rng.choice(R, size=nr, replace=False).astype(np.int32)
    cw = (npiv + 63) // 64
    cfs = rng.integers(0, 2**64, size=(nr, cw), dtype=np.uint64)
    cfs[:, 0] &= (np.uint64(1) << min(npiv, 64)) - np.uint64(1) if npiv <= 64 else np.uint64(-1)
    Bs = rng.integers(0, 2**64, size=(npiv, W), dtype=np.uint64)
    Mc = M.copy()
    gf2gpu.cpu_tail_chunk(Mc, W, 0, 0, ch, rows, cfs, cw, Bs, W, npiv, True)
    Mg = gf2gpu.gpu_tail_chunk(M, W, 0, 0, ch, rows, cfs, cw, Bs, W, npiv, True)
    assert np.array_equal(Mc, Mg)
