"""The rank-profile solver (crypto_autoresearcher.gf2.rankprofile) returns the
exact engine's M_D record, and every certificate it returns sums to 1.

  * native row_leads / row_lead_weight == their numpy references;
  * macaulay_profile == Closure.macaulay_closure (rank, one, dims_by_deg) on
    random and edge-case systems (duplicate, zero, constant, linear-only,
    sparse, dense, planted-solution), with and without the F5/Frobenius
    filter and the row reordering; planted-solution systems are never refuted;
  * the native row builder equals Closure.build_M, Shape equals Closure's
    tables, the native certificate check equals closure.eval_cert, and
    kernels.rows_sum equals the XOR of the built rows;
  * kernels.map_processes returns map's results in order, with closures, and
    runs its workers single-threaded;
  * w_profile == Closure.w_closure field for field;
  * both hold with the syndrome test on, forced onto most rows, switched off,
    with every new block reduced row by row or stacked under the basis, and
    with no test at all;
  * the annihilator, syndrome, reduction and product kernels equal their
    numpy references; a row's syndrome is zero exactly when it lies in the
    span, and rows with independent syndromes add exactly the rank all rows
    add;
  * archived RC-1 M_D and W_D records of RUN-CERTBIN-c417e0 are reproduced
    (the full sweep is ``tools/gf2_replay_rc1.py --solver rankprofile``).
"""
import gzip
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import pytest

np = pytest.importorskip("numpy", reason="the gf2 engine needs the optional `gf2` extra (numpy)")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.gf2 import closure as fc  # noqa: E402
from crypto_autoresearcher.gf2 import kernels, rankprofile, reference  # noqa: E402

RUN = ROOT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
native = pytest.mark.skipif(kernels.backend() != "native", reason="native kernels unavailable")


def _monos(nv, deg=2):
    out = [0] + [1 << i for i in range(nv)]
    if deg >= 2:
        out += [(1 << i) | (1 << j) for i, j in combinations(range(nv), 2)]
    return out


def _ev(f, x):
    return sum(1 for m in f if (m & x) == m) & 1


def _systems(seed=3, n=120):
    rng = np.random.default_rng(seed)
    kinds = ["rand", "sparse", "dense", "dup", "zero", "const", "linear", "planted"]
    for t in range(n):
        nv, D = int(rng.integers(3, 10)), int(rng.integers(2, 6))
        neq = int(rng.integers(1, 2 * nv + 3))
        kind = kinds[t % len(kinds)]
        p = {"sparse": 0.08, "dense": 0.85}.get(kind, 0.5)
        eqs = [[m for m in _monos(nv) if rng.random() < p] for _ in range(neq)]
        if kind == "dup" and neq > 1:
            eqs[-1] = list(eqs[0])
        if kind == "zero":
            eqs[int(rng.integers(neq))] = []
        if kind == "const":
            eqs[int(rng.integers(neq))] = [0]
        if kind == "linear":
            eqs = [[m for m in _monos(nv, 1) if rng.random() < 0.5] for _ in range(neq)]
        x = None
        if kind == "planted":
            x = int(rng.integers(1 << nv))
            eqs = [f if _ev(f, x) == 0 else ([m for m in f if m] if 0 in f else f + [0]) for f in eqs]
        yield nv, D, eqs, x


@native
def test_row_leads_and_lead_weight_match_reference():
    rng = np.random.default_rng(0)
    for _ in range(60):
        R, C = int(rng.integers(0, 120)), int(rng.integers(1, 300))
        W = (C + 63) // 64
        M = rng.integers(0, 2 ** 63, size=(R, W), dtype=np.uint64)
        if C % 64:
            M[:, -1] &= np.uint64((1 << (C % 64)) - 1)
        M[rng.random(R) < 0.3] = 0
        if R > 2:
            M[1] = M[0] ^ M[2]                      # a dependent row
        assert np.array_equal(kernels.row_leads(M, C), reference.row_leads(M, C))
        lead, weight = kernels.row_lead_weight(M)
        bits = np.unpackbits(M.view(np.uint8), axis=1, bitorder="little")
        assert np.array_equal(weight, bits.sum(axis=1))
        want = np.array([int(np.flatnonzero(b)[0]) if b.any() else -1 for b in bits], dtype=np.int64)
        assert np.array_equal(lead, want)


# (SPLIT, MAX_SYNDROME_WORDS, RESTACK, dual): the default; a small primal
# prefix, so most rows are selected by syndrome; no syndrome test at all; a
# huge RESTACK, so every new block is reduced row by row; a tiny one, so every
# new block is stacked under the basis; elimination of everything.
KNOBS = [(1.0, 256, 1 / 16, True), (0.3, 256, 1 / 16, True), (0.3, 0, 1 / 16, True),
         (0.3, 256, 1e9, True), (0.3, 256, 1e-9, True), (1.0, 256, 1 / 16, False)]


def _mk(rng, R, C, dens):
    W = (C + 63) // 64
    d = (rng.random((R, C)) < dens).astype(np.uint8)
    d = np.concatenate([d, np.zeros((R, W * 64 - C), np.uint8)], 1)
    return np.ascontiguousarray(np.packbits(d, axis=1, bitorder="little")).view(np.uint64).reshape(R, W).copy()


@native
def test_annihilator_syndromes_and_reduction_match_reference_and_rank():
    rng = np.random.default_rng(1)
    for _ in range(150):
        C, R = int(rng.integers(1, 300)), int(rng.integers(0, 200))
        dens = float(rng.choice([0.01, 0.05, 0.3]))
        M = _mk(rng, R, C, dens)
        A = M.copy()
        log = kernels.column_pass(A, C, keep_ops=False)
        E, lead = np.ascontiguousarray(A[log.ps]), log.cs.astype(np.int64)
        K = kernels.annihilator([(E, np.arange(len(E)), lead)], C)
        o = np.argsort(-lead)
        Kr = reference.annihilator(np.ascontiguousarray(E[o]), lead[o].copy(), C, np.zeros_like(K))
        assert np.array_equal(K, Kr)
        assert not kernels.syndromes(M, K).any()
        Q = _mk(rng, int(rng.integers(1, 60)), C, dens)
        S = kernels.syndromes(Q, K)
        assert np.array_equal(S, reference.syndromes(Q, K))
        idx = rng.permutation(len(Q))[: len(Q) // 2]
        assert np.array_equal(kernels.syndromes(Q, K, idx=idx), S[idx])
        # independent syndromes <=> independent modulo span(M): the selected
        # rows add exactly the rank all of Q adds
        f = C - log.K
        sel = kernels.column_pass(S.copy(), max(f, 1), keep_ops=False).ps if f else np.zeros(0, np.int64)
        full = kernels.column_pass(np.concatenate([M, Q]), C, keep_ops=False).K
        part = kernels.column_pass(np.concatenate([M, Q[np.sort(sel)]]), C, keep_ops=False).K
        assert full == part == log.K + len(sel)
        # reduce_rows: lead-chain and full reduction, against the reference
        blocks = [(A, log.ps.astype(np.int64), lead, 7 + log.ps.astype(np.int64))]
        for full_red in (False, True):
            Q1, Q2 = Q.copy(), Q.copy()
            l1, X1 = kernels.reduce_rows(Q1, C, blocks, keep_ops=True, full=full_red)
            l2, X2 = reference.reduce_rows(Q2, C, blocks, True, full_red)
            assert np.array_equal(l1, l2) and np.array_equal(Q1, Q2)
            assert all(np.array_equal(a, b) for a, b in zip(X1, X2))
            assert np.array_equal(l1 < 0, ~S.any(axis=1))      # zero exactly when in the span
            if full_red and len(lead):
                assert not (Q1[:, lead >> 6] >> (lead & 63).astype(np.uint64) & np.uint64(1)).any()


@native
def test_product_syndromes_and_pairs_match_formed_products():
    rng = np.random.default_rng(4)
    for _ in range(25):
        nv, D = int(rng.integers(3, 10)), int(rng.integers(2, 6))
        sh = rankprofile.Shape(nv, D)
        colmap, maps = sh.product_tables
        low = sh.col_deg(np.arange(sh.C)) <= D - 1
        rows = _mk(rng, int(rng.integers(1, 30)), sh.C, 0.1)
        rows &= np.packbits(np.r_[low, np.zeros(sh.W * 64 - sh.C, bool)].astype(np.uint8),
                            bitorder="little").view(np.uint64)
        rows = np.ascontiguousarray(rows)
        P = kernels.products(rows, colmap, maps, nv, sh.C, sh.W)
        E = _mk(rng, int(rng.integers(0, 40)), sh.C, 0.2)
        log = kernels.column_pass(E, sh.C, keep_ops=False)
        K = kernels.annihilator([(E, log.ps.astype(np.int64), log.cs.astype(np.int64))], sh.C)
        addrs = np.uint64(rows.ctypes.data) + np.arange(len(rows), dtype=np.uint64) * np.uint64(sh.W * 8)
        S = kernels.product_syndromes(addrs, sh.W, sh.C, colmap, nv, K)
        assert np.array_equal(S, kernels.syndromes(P, K))
        assert np.array_equal(S, reference.product_syndromes(rows, colmap, nv, sh.C, K))
        q = rng.integers(0, nv * len(rows), size=20)
        j, f = np.divmod(q, len(rows))
        assert np.array_equal(kernels.product_pairs(addrs[f], j, sh.W, sh.C, colmap), P[q])
        assert np.array_equal(reference.product_pairs(rows[f], j, colmap, sh.C, sh.W), P[q])


@pytest.mark.parametrize("use_f5,order", [(True, "lead_desc"), (True, "built"), (False, "lead_desc")])
@pytest.mark.parametrize("split,synw,restack,dual", KNOBS)
def test_profile_matches_exact_engine(monkeypatch, use_f5, order, split, synw, restack, dual):
    for name, v in (("SPLIT", split), ("MAX_SYNDROME_WORDS", synw), ("RESTACK", restack)):
        monkeypatch.setattr(rankprofile, name, v)
    refuted = 0
    for nv, D, eqs, planted in _systems():
        want, _ = fc.Closure(nv, D, len(eqs)).macaulay_closure(eqs, want_cert=False)
        got, cert, info = rankprofile.macaulay_profile(eqs, nv, D, use_f5=use_f5, order=order, dual=dual)
        assert got == want, (nv, D, len(eqs))
        assert info["rows_kept"] <= info["rows_total"]
        assert got["rank"] <= info["rows_eliminated"] <= info["rows_kept"]
        assert len(info["pivcols"]) == got["rank"]
        if got["one"]:
            refuted += 1
            assert fc.eval_cert(cert, eqs) == [0]
        else:
            assert cert is None
        if planted is not None:
            assert not got["one"]
    assert refuted > 10


def test_f5_filter_drops_rows_and_keeps_the_span():
    rng = np.random.default_rng(5)
    nv, D = 12, 5
    eqs = [[m for m in _monos(nv) if rng.random() < 0.5] for _ in range(nv - 1)]
    keep = rankprofile.f5_keep(nv, D, eqs)
    cl = fc.Closure(nv, D, nv - 1)
    M = cl.build_M(eqs)
    assert keep.sum() < cl.R
    full = kernels.column_pass(M.copy(), cl.C, keep_ops=False)
    part = kernels.column_pass(np.ascontiguousarray(M[keep]), cl.C, keep_ops=False)
    assert np.array_equal(np.sort(full.cs), np.sort(part.cs))
    # every dropped row lies in the span of the kept rows
    both = np.ascontiguousarray(np.concatenate([M[keep], M[~keep]]))
    assert np.all(kernels.row_leads(both, cl.C)[keep.sum():] == -1)


def test_build_rows_shape_and_cert_check_match_closure():
    rng = np.random.default_rng(2)
    for t in range(30):
        nv, D, neq = int(rng.integers(2, 11)), int(rng.integers(2, 6)), int(rng.integers(1, 7))
        eqs = [[m for m in _monos(nv) if rng.random() < 0.4] for _ in range(neq)]
        if t % 5 == 0:
            eqs[0] = eqs[0] + eqs[0][:2]                 # repeated monomials cancel
        cl = fc.Closure(nv, D, neq)
        sh = rankprofile.Shape(nv, D)
        assert sh.C == cl.C and np.array_equal(sh.mu_mask.astype(np.int64), cl.mu_mask)
        assert np.array_equal(sh.col_deg(np.arange(sh.C)), cl.col_deg)
        assert np.array_equal(sh.masks.astype(np.int64), cl.col_mask)
        if D >= 2:
            assert np.array_equal(sh.product_tables[0], cl.colmap)
        rows = np.arange(cl.R)
        eoff, emon = kernels.pack_eqs(eqs)
        M, lead, weight = kernels.build_rows(eoff, emon, nv, D, cl.mu_mask[rows // neq].astype(np.uint64),
                                             (rows % neq).astype(np.int32), W=cl.W)
        want = cl.build_M(eqs)
        assert np.array_equal(M, want)
        assert all(np.array_equal(a, b) for a, b in zip((lead, weight), kernels.row_lead_weight(want)))
        cert = [(int(rng.integers(1 << nv)) & int(rng.integers(1 << nv)), int(rng.integers(neq)))
                for _ in range(int(rng.integers(1, 6)))]
        if t % 3 == 0:
            cert, eqs[0] = [(0, 0)], [0]
        assert rankprofile.cert_sums_to_one(cert, eqs, nv) == (fc.eval_cert(cert, eqs) == [0])
        if len(rows):
            pick = rng.integers(0, cl.R, size=int(rng.integers(1, 30)))
            mu_p = cl.mu_mask[pick // neq].astype(np.uint64)
            k_p = (pick % neq).astype(np.int32)
            assert np.array_equal(kernels.rows_sum(eoff, emon, nv, D, mu_p, k_p, cl.W),
                                  np.bitwise_xor.reduce(want[pick], axis=0))


@pytest.mark.parametrize("split,synw,restack,dual", KNOBS)
def test_w_profile_matches_exact_engine(monkeypatch, split, synw, restack, dual):
    for name, v in (("SPLIT", split), ("MAX_SYNDROME_WORDS", synw), ("RESTACK", restack)):
        monkeypatch.setattr(rankprofile, name, v)
    seen_iter = refuted = 0
    for nv, D, eqs, planted in _systems(seed=8, n=80):
        want, _ = fc.Closure(nv, D, len(eqs)).w_closure(eqs, want_cert=False)
        got, cert, _ = rankprofile.w_profile(eqs, nv, D, dual=dual)
        assert got == want, (nv, D, len(eqs))
        seen_iter += got["iterations_to_fixpoint"] > 0
        if got["one"]:
            refuted += 1
            assert fc.eval_cert(cert, eqs) == [0]
        if planted is not None:
            assert not got["one"]
    assert seen_iter > 0 and refuted > 5


@pytest.mark.skipif(not (RUN / "closures.jsonl.gz").exists(), reason="RC-1 run package absent")
def test_profile_reproduces_archived_rc1_records():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import gf2_replay_rc1 as replay
    finally:
        sys.path.remove(str(ROOT / "tools"))
    keys = {"U62:F-S3:27", "N-AFF62:F-AFF-1:8", "C20:F-S3:3"}
    eqs = replay.load_eqs()
    rows = [r for r in map(json.loads, gzip.open(RUN / "closures.jsonl.gz", "rt"))
            if r["key"] in keys]
    certs = {(c["key"], c["closure"]) for c in map(json.loads, gzip.open(RUN / "certificates.jsonl.gz", "rt"))}
    checked = 0
    for rec in rows:
        D = int(rec["closure"][2])
        run = rankprofile.macaulay_profile if rec["closure"][0] == "M" else rankprofile.w_profile
        got, cert, _ = run(eqs[rec["key"]], 18, D)
        for k, v in rec.items():
            if k not in replay.DRIVER_FIELDS:
                assert got[k] == v, (rec["key"], rec["closure"], k)
        if (rec["key"], rec["closure"]) in certs:
            assert cert is not None and fc.eval_cert(cert, eqs[rec["key"]]) == [0]
        checked += 1
    assert checked >= 8                                 # M_3, M_4, M_5 and W_4 per key


@native
def test_map_processes_matches_map():
    data = list(range(37))
    offset = 5                                           # a closure over local state
    assert kernels.map_processes(lambda x: (x * x + offset, kernels.inner_threads()), data, 3) == \
        [(x * x + offset, 1) for x in data]


def _mk_dense(rng, R, C, dens):
    W = (C + 63) // 64
    d = (rng.random((R, C)) < dens).astype(np.uint8)
    d = np.concatenate([d, np.zeros((R, W * 64 - C), np.uint8)], 1)
    return np.ascontiguousarray(np.packbits(d, axis=1, bitorder="little")).view(np.uint64).reshape(R, W).copy()


@native
def test_gpu_pass_algorithm_matches_blocked_pass_on_cpu():
    """gpu/rankpass.py run with numpy as its array module: same pivots, same
    order and same final matrix as the blocked CPU pass."""
    from crypto_autoresearcher.gf2.gpu import rankpass
    rng = np.random.default_rng(1)
    for t in range(80):
        R, C = int(rng.integers(0, 250)), int(rng.integers(1, 600))
        M = _mk_dense(rng, R, C, float(rng.choice([0.005, 0.03, 0.2, 0.5])))
        if R > 3 and t % 3 == 0:
            M[1] = M[0] ^ M[2]
        A = M.copy()
        log = kernels.column_pass(A, C, keep_ops=False, algorithm="blocked")
        B = M.copy()
        ps, cs = rankpass.column_pass(B, C, xp=np)
        assert np.array_equal(ps, log.ps) and np.array_equal(cs, log.cs) and np.array_equal(A, B)
    for t in range(100):
        v = rng.integers(1, 2 ** 63, size=int(rng.integers(1, 150)), dtype=np.uint64)
        nb = int(rng.integers(1, 65))
        got, want = rankpass.block_elim(v, nb), rankpass._block_elim_py(v.copy(), nb)
        assert all(np.array_equal(a, b) for a, b in zip(got, want))


@native
def test_solver_gpu_path_on_cpu_matches_exact_engine(monkeypatch):
    """The solver's GPU route (no op log; CPU rerun when a certificate is
    needed), with the GPU pass run through numpy and forced on every pass."""
    from crypto_autoresearcher.gf2.gpu import rankpass
    monkeypatch.setattr(rankpass, "XP", np)
    monkeypatch.setattr(rankprofile, "_gpu_ok", True)
    monkeypatch.setattr(rankprofile, "GPU_MIN_WORDS", 0)
    refuted = 0
    for nv, D, eqs, planted in _systems(seed=11, n=60):
        want, _ = fc.Closure(nv, D, len(eqs)).macaulay_closure(eqs, want_cert=False)
        got, cert, info = rankprofile.macaulay_profile(eqs, nv, D)
        assert got == want
        assert bool(info.get("gpu")) == (not got["one"])
        if got["one"]:
            refuted += 1
            assert fc.eval_cert(cert, eqs) == [0]
        wwant, _ = fc.Closure(nv, D, len(eqs)).w_closure(eqs, want_cert=False)
        wgot, wcert, _ = rankprofile.w_profile(eqs, nv, D)
        assert wgot == wwant
        if wgot["one"]:
            assert fc.eval_cert(wcert, eqs) == [0]
        nocert, c2, _ = rankprofile.macaulay_profile(eqs, nv, D, want_cert=False)
        assert nocert == want and c2 is None
    assert refuted > 5


def test_gpu_pass_on_device_matches_blocked_pass():
    """On a CUDA host: the CuPy pass gives the CPU pass's pivots and matrix,
    and the solver's GPU route gives the exact engine's records."""
    from crypto_autoresearcher.gf2 import gpu
    from crypto_autoresearcher.gf2.gpu import rankpass
    ok, why = gpu.available()
    if not ok:
        pytest.skip(why)
    import cupy as cp
    rng = np.random.default_rng(7)
    for t in range(40):
        R, C = int(rng.integers(1, 400)), int(rng.integers(1, 900))
        M = _mk_dense(rng, R, C, float(rng.choice([0.01, 0.1, 0.5])))
        A = M.copy()
        log = kernels.column_pass(A, C, keep_ops=False, algorithm="blocked")
        B = M.copy()
        ps, cs = rankpass.column_pass(B, C, xp=cp)
        assert np.array_equal(ps, log.ps) and np.array_equal(cs, log.cs) and np.array_equal(A, B)
    old = rankprofile.GPU_MIN_WORDS
    rankprofile.GPU_MIN_WORDS = 0
    try:
        for nv, D, eqs, _ in _systems(seed=13, n=30):
            want, _ = fc.Closure(nv, D, len(eqs)).macaulay_closure(eqs, want_cert=False)
            assert rankprofile.macaulay_profile(eqs, nv, D, gpu=True)[0] == want
    finally:
        rankprofile.GPU_MIN_WORDS = old


def test_profile_runs_on_the_reference_backend():
    code = (
        "import sys; sys.path.insert(0, %r)\n"
        "from crypto_autoresearcher.gf2 import rankprofile, kernels, closure as fc\n"
        "assert kernels.backend() == 'reference'\n"
        "eqs = [[3, 1, 0], [5, 4], [6, 2, 1], [7 & 6, 4, 0], [1, 0], [2]]\n"
        "a, _ = fc.Closure(3, 4, 6).macaulay_closure(eqs)\n"
        "b, c, _ = rankprofile.macaulay_profile(eqs, 3, 4)\n"
        "assert a == b, (a, b)\n"
        "wa, _ = fc.Closure(3, 4, 6).w_closure(eqs)\n"
        "wb, _, _ = rankprofile.w_profile(eqs, 3, 4)\n"
        "assert wa == wb, (wa, wb)\n"
        "assert (c is None) == (not b['one'])\n"
        "print('ok')\n" % str(ROOT / "src"))
    env = dict(__import__("os").environ, CRYPTO_AR_GF2_BACKEND="reference")
    out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
