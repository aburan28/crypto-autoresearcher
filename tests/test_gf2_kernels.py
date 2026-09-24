"""The fast GF(2) kernels reproduce the archived CERTBIN engines exactly.

Three layers:
  * native kernels == numpy reference (crypto_autoresearcher.gf2.reference,
    copied from the archived engines) on random and structured matrices;
  * the reference itself == the archived EXP-CERTBIN-4e92d7 / e94b27 code it
    was copied from (so the chain reaches the code that produced run records);
  * the fast Closure reproduces archived RC-1 closure records and certificates
    of RUN-CERTBIN-c417e0 (the full sweep is tools/gf2_replay_rc1.py).
"""
import gzip
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.gf2 import closure as fc  # noqa: E402
from crypto_autoresearcher.gf2 import kernels, reference  # noqa: E402

E94 = ROOT / "experiments/EXP-CERTBIN-e94b27"
RUN = E94 / "runs/RUN-CERTBIN-c417e0"
E4E = ROOT / "experiments/EXP-CERTBIN-4e92d7/impl"

native = pytest.mark.skipif(kernels.backend() != "native", reason="native kernels unavailable")


def _load(path, name):
    """Import an archived module by path without writing bytecode into it."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    before = set(sys.modules)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(path.parent))
        sys.dont_write_bytecode = old
        # sibling imports (e.g. `from macaulay import ...`) must not leak into
        # other tests under their bare names
        for m in set(sys.modules) - before:
            del sys.modules[m]
    return mod


def _pack(dense, C):
    R = dense.shape[0]
    W = (C + 63) // 64
    if W * 64 - C:
        dense = np.concatenate([dense, np.zeros((R, W * 64 - C), np.uint8)], axis=1)
    return np.ascontiguousarray(np.packbits(dense, axis=1, bitorder="little")).view(np.uint64).reshape(R, W).copy()


def _random_cases(seed=0, n=120):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        R, C = int(rng.integers(0, 300)), int(rng.integers(1, 520))
        dens = float(rng.choice([0.005, 0.03, 0.1, 0.5]))
        yield _pack((rng.random((R, C)) < dens).astype(np.uint8), C), C
    for _ in range(30):  # low-rank: many dependent rows, long X sets
        R, C = int(rng.integers(40, 250)), int(rng.integers(64, 400))
        base = (rng.random((16, C)) < 0.3).astype(np.uint8)
        comb = (rng.random((R, 16)) < 0.3).astype(np.uint8)
        yield _pack((comb @ base % 2).astype(np.uint8), C), C


def _same_log(ref, log, keep=True):
    ps, cs, Xs, tot = ref
    ok = np.array_equal(ps, log.ps) and np.array_equal(cs, log.cs) and tot == log.ops_strict
    if keep:
        ok = ok and len(Xs) == len(log.Xs) and all(np.array_equal(a, b) for a, b in zip(Xs, log.Xs))
    return ok


# ---------------------------------------------------------------------------
# native == reference
# ---------------------------------------------------------------------------
@native
@pytest.mark.parametrize("algorithm", ["blocked", "direct"])
def test_column_pass_matches_reference(algorithm):
    for M, C in _random_cases():
        A, B, B2 = M.copy(), M.copy(), M.copy()
        ref = reference.column_pass(A, C, True)
        assert _same_log(ref, kernels.column_pass(B, C, True, algorithm=algorithm))
        assert np.array_equal(A, B), "final matrix differs"
        assert _same_log(ref, kernels.column_pass(B2, C, False, algorithm=algorithm), keep=False)
        assert np.array_equal(A, B2)


@native
def test_row_pass_json_and_hashes_match_reference():
    for M, C in _random_cases(seed=1, n=60):
        assert kernels.row_pass(M, C) == reference.row_pass(M, C)
        ps, cs, Xs, _ = reference.column_pass(M.copy(), C, True)
        log = kernels.column_pass(M.copy(), C, True)
        canon_ops = kernels.canon([[int(p), int(c), X.tolist()] for p, c, X in zip(ps, cs, Xs)]).encode()
        assert kernels.ops_json_bytes(log) == canon_ops
        Z, _ = reference.row_pass(M, C)
        h = kernels.trace_hashes(log, Z)
        assert h["h_set"] == kernels.sha(kernels.canon([sorted(cs.tolist()), Z]))
        assert h["h_strict"] == kernels.sha(kernels.canon([[int(p), int(c)] for p, c in zip(ps, cs)]))
        assert h["h_rank"] == kernels.sha(kernels.canon(len(ps)))


@native
def test_replays_backtrace_products_match_reference():
    rng = np.random.default_rng(2)
    for M, C in _random_cases(seed=2, n=40):
        R, W = M.shape
        ps, cs, Xs, _ = reference.column_pass(M.copy(), C, True)
        log = kernels.column_pass(M.copy(), C, True)
        planes = np.stack([_pack((rng.random((R, C)) < 0.1).astype(np.uint8), C) for _ in range(3)]) \
            if R else np.zeros((3, 0, W), np.uint64)
        assert np.array_equal(reference.replay_planes(planes.copy(), ps, cs, Xs),
                              kernels.replay_planes(planes.copy(), log))
        for stop in (False, True):
            P0 = np.ascontiguousarray(planes[0])
            assert np.array_equal(reference.replay_direct(P0, ps, cs, Xs, stop),
                                  kernels.replay_direct(P0, log, stop))
        S = rng.integers(0, 2 ** 63, size=(R, 2), dtype=np.uint64)
        assert np.array_equal(reference.backtrace(ps, Xs, S.copy()), kernels.backtrace(log, S.copy()))
    for nv, D in ((6, 3), (6, 4), (8, 4)):
        cl = fc.Closure(nv, D, 3)
        low = np.flatnonzero(cl.col_deg <= D - 1)
        dense = np.zeros((50, cl.C), np.uint8)
        dense[:, low] = rng.random((50, low.size)) < 0.2
        rows = cl.pack(dense)
        assert np.array_equal(reference.products(rows, cl.maps, nv, cl.C, cl.W),
                              kernels.products(rows, cl.colmap, cl.maps, nv, cl.C, cl.W))


def test_xview_behaves_like_a_list():
    M, C = next(_random_cases(seed=3, n=1))
    log = kernels.column_pass(M.copy(), C, True)
    ref = reference.column_pass(M.copy(), C, True)[2]
    view = log.Xs
    assert len(view) == len(ref)
    assert all(np.array_equal(a, b) for a, b in zip(view, ref))
    if len(ref):
        assert np.array_equal(view[-1], ref[-1])
        assert [x.tolist() for x in view[:3]] == [x.tolist() for x in ref[:3]]


# ---------------------------------------------------------------------------
# reference == the archived code it was copied from
# ---------------------------------------------------------------------------
def test_reference_matches_archived_4e92d7_elim():
    ae = _load(E4E / "elim.py", "_arch_elim_4e92d7")
    for M, C in _random_cases(seed=4, n=25):
        aps, acs, aXs = ae.column_pass(M.copy(), C, keep_ops=True)
        ps, cs, Xs, _ = reference.column_pass(M.copy(), C, True)
        assert list(ps) == aps and list(cs) == acs
        assert all(np.array_equal(a, b) for a, b in zip(aXs, Xs))
        assert reference.row_pass(M, C) == ae.row_pass(M, C)


def test_eliminate_matches_archived_4e92d7_on_a_macaulay_matrix():
    ae = _load(E4E / "elim.py", "_arch_elim_4e92d7")
    mac = _load(E4E / "macaulay.py", "_arch_mac_4e92d7")
    gf = _load(E4E / "gf2n.py", "_arch_gf2n_4e92d7")
    F = gf.TableField()
    S = mac.MacaulayShape(3)
    for xR in (5, 70001):
        M = S.build(mac.descended_E(F, 126251, xR))
        a, acp, al = ae.eliminate(M, S.C)
        b, bcp, bl = fc.eliminate(M, S.C)
        assert (acp, al) == (bcp, bl)
        assert (a.p, a.c, a.Z, a.rank, a.pivcols) == (b.p, b.c, b.Z, b.rank, b.pivcols)
        assert (a.h_rank, a.h_set, a.h_strict, a.h_ops) == (b.h_rank, b.h_set, b.h_strict, b.h_ops)
        assert all(np.array_equal(x, y) for x, y in zip(a.X, b.X))


# ---------------------------------------------------------------------------
# fast Closure == archived RC-1 records
# ---------------------------------------------------------------------------
def _rc1(keys):
    inst = _load(E94 / "impl/instances.py", "_arch_inst_e94b27")
    mac = _load(E94 / "impl/macaulay.py", "_arch_mac_e94b27")
    sets = json.loads((RUN / "instance-sets.json").read_text())["sets"]
    eqs = {}
    for recs in sets.values():
        for r in recs:
            if r["key"] in keys:
                E = inst.E_from_hex(r["E_hex"])
                eqs[r["key"]] = [[fc.mono_mask(mac.EQ_MONS[j]) for j in np.flatnonzero(E[k])] for k in range(17)]
    rows = [json.loads(line) for line in gzip.open(RUN / "closures.jsonl.gz", "rt")]
    certs = {(c["key"], c["closure"]): c["C"] for c in map(json.loads, gzip.open(RUN / "certificates.jsonl.gz", "rt"))}
    return eqs, [r for r in rows if r["key"] in keys], certs


@pytest.mark.skipif(not (RUN / "closures.jsonl.gz").exists(), reason="RC-1 run package absent")
def test_closure_reproduces_archived_rc1_records():
    keys = {"U62:F-S3:27", "N-AFF62:F-AFF-1:8"}
    eqs, rows, certs = _rc1(keys)
    driver = {"wall_seconds", "label", "role", "certificate", "key", "set", "idx", "closure",
              "engine_self_check_sum_is_1", "ell_in_W4_le1"}
    cls = {D: fc.Closure(18, D, 17) for D in (3, 4, 5)}
    checked = 0
    for rec in rows:
        kind, D = rec["closure"][0], int(rec["closure"][2])
        want_cert = (rec["key"], rec["closure"]) in certs
        run = cls[D].macaulay_closure if kind == "M" else cls[D].w_closure
        got, cert = run(eqs[rec["key"]], want_cert=want_cert)
        for k, v in rec.items():
            if k not in driver:
                assert got[k] == v, (rec["key"], rec["closure"], k)
        if want_cert:
            assert fc.cert_to_json(cert) == certs[(rec["key"], rec["closure"])]
            assert fc.eval_cert(cert, eqs[rec["key"]]) == [0]
        checked += 1
    assert checked == 8  # M_3, M_4, W_4, M_5 for each key


def test_reference_backend_fallback_gives_the_same_closure(tmp_path):
    """With CRYPTO_AR_GF2_BACKEND=reference (or no compiler) the same API runs
    on numpy and returns the same record and certificate."""
    import subprocess
    code = (
        "import json,sys; sys.path.insert(0, %r)\n"
        "from crypto_autoresearcher.gf2 import closure as fc, kernels\n"
        "eqs=[[0b11, 0b100, 0], [0b101, 0b1], [0b110, 0b10, 0]]\n"
        "cl=fc.Closure(4, 3, 3); rec, cert = cl.w_closure(eqs)\n"
        "m, mc = fc.Closure(4, 4, 3).macaulay_closure(eqs)\n"
        "print(json.dumps([kernels.backend(), rec, cert, m, mc]))\n" % str(ROOT / "src"))
    out = {}
    for mode in ("reference", "auto"):
        env = dict(__import__("os").environ, CRYPTO_AR_GF2_BACKEND=mode)
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, check=True)
        out[mode] = json.loads(p.stdout)
    assert out["reference"][0] == "reference"
    assert out["reference"][1:] == out["auto"][1:]
