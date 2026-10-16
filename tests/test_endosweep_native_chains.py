"""Frozen native chain sets of research/endosweep_native_chains_20261016.

Every exported constant is re-checked from the JSON alone, without the
harness's isogeny objects: the curve, the generator, each test point, the
chain evaluated from its Kohel-form polynomials (``x' = N/psi^2``,
``y' = y M/psi^3``, then ``(u^2 x, u^3 y)``), the eigenvalue, the GLV basis and
the decomposition.  The generalised ``chainsweep`` is also checked to leave
CryptoPro-B's model unchanged and to price 2-steps as ``curvesweep`` does.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import pytest

from harness.endosweep import chainsweep as CS
from harness.endosweep import curvesweep as CV
from harness.endosweep import lattice as LA
from harness.endosweep import quadorder as QO
from harness.endosweep.toyverify import Curve

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/endosweep_native_chains_20261016"
CURVES = {
    # file prefix: (database name, D_K, cheapest element, its cheapest order, cheapest optimised M_eq)
    "bandersnatch": ("arkworks/ed_on_bls12_381_bandersnatch", -8, [0, 1], [2], 6),
    "tom384": ("other/Tom-384", -619, [4, 1], [7, 5, 5], 80),
    "cp6_782": ("arkworks/cp6_782", -339, [4, 1], [7, 3, 5], 65),
}


def _ev(poly, x, p):
    acc = 0
    for c in reversed(poly):
        acc = (acc * x + c) % p
    return acc


def _apply_chain(ch, P, p):
    x, y = P
    for st in ch["steps"]:
        psi = [int(c, 16) for c in st["psi"]]
        N = [int(c, 16) for c in st["N"]]
        M = [int(c, 16) for c in st["M"]]
        d = pow(_ev(psi, x, p), -1, p)
        x, y = _ev(N, x, p) * d * d % p, y * _ev(M, x, p) % p * pow(d, 3, p) % p
    u = int(ch["isomorphism_u"], 16)
    return u * u * x % p, pow(u, 3, p) * y % p


def verify_chain_file(path: Path) -> dict:
    """Check every constant of one ``endosweep-chainsweep/1`` file; returns a summary."""
    d = json.loads(path.read_text())
    assert d["format"] == CS.FORMAT
    p, a, b, n = (int(d[k], 16) for k in ("p", "a", "b", "n"))
    h = d["cofactor"]
    E = Curve(p, a, b)
    D = d["D_K"]
    tau, m = QO.omega_trace_norm(D)
    lam = int(d["omega_root"], 16)
    assert (lam * lam - tau * lam + m) % n == 0
    cur = d["curve"]
    t = int(cur["trace"])
    assert p + 1 - t == h * n
    assert t * t - 4 * p == D * int(cur["conductor"]) ** 2
    G = tuple(int(c, 16) for c in cur["G"])
    assert E.on_curve(G) and E.mul(n, G) is None
    assert d["eigenvalues_consistent_across_orders"]
    limit = d["bounds"]["export_limit_M_eq"]
    for ch in d["chains"]:
        e = int(ch["eigenvalue"], 16)
        ma, mb = ch["matched_element"]
        assert (ma, mb) in ((ch["element"][0], ch["element"][1]), (-ch["element"][0], -ch["element"][1]))
        assert (e - (ma + mb * lam)) % n == 0
        assert QO.norm(D, *ch["element"]) == ch["norm"]
        prod = 1
        for ell in ch["order"]:
            prod *= ell
        assert prod == ch["norm"]
        assert (e * e - (2 * ma + mb * tau) * e + ch["norm"]) % n == 0
        (u1, v1), (u2, v2) = [[int(x) for x in row] for row in ch["glv_basis"]]
        assert (u1 + v1 * e) % n == 0 and (u2 + v2 * e) % n == 0
        assert abs(u1 * v2 - v1 * u2) == n
        assert ch["model_ops"]["optimised"]["M_eq"] <= limit
        assert ch["model_ops"] == {v: CS.chain_ops(ch["order"], v) for v in CS.VARIANTS}
        # the walk closes: consecutive steps chain, and the last codomain is E up to u
        prev = {"a": hex(a), "b": hex(b)}
        for st in ch["steps"]:
            assert st["domain"] == prev
            prev = st["codomain"]
            s = 1 if st["ell"] == 2 else (st["ell"] - 1) // 2
            assert (len(st["psi"]) - 1, len(st["N"]) - 1, len(st["M"]) - 1) == (
                (1, 3, 3) if st["ell"] == 2 else (s, st["ell"], 3 * s))
        u = int(ch["isomorphism_u"], 16)
        assert (pow(u, 4, p) * int(prev["a"], 16) - a) % p == 0
        assert (pow(u, 6, p) * int(prev["b"], 16) - b) % p == 0
        assert ch["test_vectors"]
        for tv in ch["test_vectors"]:
            P = tuple(int(c, 16) for c in tv["P"])
            phiP = tuple(int(c, 16) for c in tv["phiP"])
            kP = tuple(int(c, 16) for c in tv["kP"])
            assert E.on_curve(P) and E.mul(n, P) is None
            assert _apply_chain(ch, P, p) == phiP == E.mul(e, P)
            k, k1, k2 = int(tv["k"], 16), int(tv["k1"]), int(tv["k2"])
            assert (k - k1 - k2 * e) % n == 0
            assert E.mul(k, P) == kP == E.add(E.mul(k1, P), E.mul(k2, phiP))
    return {"chains": len(d["chains"]), "best": d["bounds"]["best_optimised_M_eq"]}


def _path(prefix: str) -> Path:
    return OUT / f"{prefix}.chains.constants.json"


@pytest.mark.parametrize("prefix", sorted(CURVES))
def test_chain_file_verifies(prefix):
    path = _path(prefix)
    if not path.exists():
        pytest.skip(f"{path.name} not generated")
    name, D, el, order, best = CURVES[prefix]
    d = json.loads(path.read_text())
    assert d["target"] == name and d["D_K"] == D
    s = verify_chain_file(path)
    assert s["best"] == best
    cheapest = min(d["chains"], key=lambda c: (c["model_ops"]["optimised"]["M_eq"], c["id"]))
    assert cheapest["element"] == el and cheapest["order"] == order
    assert path.stat().st_size < 4 << 20


@pytest.mark.parametrize("prefix", sorted(CURVES))
def test_model_uses_the_curves_own_doubling(prefix):
    mpath = OUT / f"{prefix}.model.json"
    if not mpath.exists():
        pytest.skip("not generated")
    d = json.loads(_path(prefix).read_text())
    model = json.loads(mpath.read_text())
    ar = CV.arithmetic(int(d["p"], 16), int(d["a"], 16))
    assert model["arithmetic"]["dbl"] == list(ar.dbl) == d["curve"]["arithmetic"]["dbl"]
    assert set(model["glv"]) == {c["id"] for c in d["chains"]}


def test_sha256sums():
    sums = OUT / "SHA256SUMS"
    if not sums.exists():
        pytest.skip("not generated")
    for line in sums.read_text().splitlines():
        digest, name = line.split()
        assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest, name


def test_cryptopro_b_model_unchanged_by_arith():
    """With CryptoPro-B's own arithmetic (a = -3, Fermat inversion 8M + 256S) the
    curve-generic model equals the original one exactly."""
    d = json.loads((ROOT / "research/endosweep_chainsweep_20261006/chains.constants.json").read_text())
    d = {**d, "chains": d["chains"][:2]}
    ar = CV.arithmetic(int(d["p"], 16), int(d["a"], 16))
    assert ar.dbl == CS.DBL and ar.inv == CS.INV_OPS
    old = CS.scalar_mult_model(d, samples=20)
    new = CS.scalar_mult_model(d, samples=20, arith=ar)
    new.pop("arithmetic")
    assert old == new


def test_two_step_counts_match_curvesweep():
    for variant in CS.VARIANTS:
        for order in ((2,), (2, 3), (3, 2), (7, 2, 5)):
            assert CS.chain_ops(order, variant) == CV.chain_ops(order, variant)


def test_two_step_rational_maps():
    """The 2-step Kohel form agrees with Velu on a small curve with a 2-torsion point."""
    p = 10007
    rng = random.Random(3)
    while True:
        x0, a = rng.randrange(p), rng.randrange(p)
        b = (-(x0 ** 3) - a * x0) % p          # (x0, 0) is on y^2 = x^3 + a x + b
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    E = Curve(p, a, b)
    N, psi, M = CS.rational_map_polys(E, [(-x0) % p, 1], 2)
    v = (3 * x0 * x0 + a) % p
    for _ in range(20):
        P = E.point(rng.randrange(1 << 20))
        x, y = P
        if x == x0:
            continue
        xs = (x + v * pow(x - x0, -1, p)) % p
        ys = y * (1 - v * pow(x - x0, -2, p)) % p
        d = pow(_ev(psi, x, p), -1, p)
        assert (_ev(N, x, p) * d * d % p, y * _ev(M, x, p) * pow(d, 3, p) % p) == (xs, ys)


@pytest.mark.parametrize("prefix", sorted(CURVES))
def test_glv_basis_is_reduced_and_short(prefix):
    if not _path(prefix).exists():
        pytest.skip("not generated")
    d = json.loads(_path(prefix).read_text())
    n = int(d["n"], 16)
    for ch in d["chains"]:
        red = LA.reduce([1, int(ch["eigenvalue"], 16)], n)
        assert [[str(x) for x in row] for row in red.basis] == ch["glv_basis"]
        # short: every entry within a small factor of sqrt(n)
        assert max(abs(int(x)) for row in ch["glv_basis"] for x in row) < 1 << (n.bit_length() // 2 + 8)


def test_cryptopro_b_export_unchanged():
    """The generalised export reproduces a frozen CryptoPro-B record byte for byte."""
    from harness.endosweep import explicit as EX
    d = json.loads((ROOT / "research/endosweep_chainsweep_20261006/chains.constants.json").read_text())
    i, rec = next((i, c) for i, c in enumerate(d["chains"]) if c["id"] == "4+1w/7.5.5")
    T, D = CS._target("GOST CryptoPro-B")
    root = int(d["omega_root"], 16)
    r = EX.build_chain_endomorphism(T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h, D, (4, 1),
                                    curve_name=T.name, steps=[7, 5, 5], conjugates=False, omega_root=root)
    assert CS.export_chain(T, D, r, root, vectors=2, seed=20261006 + i) == rec
