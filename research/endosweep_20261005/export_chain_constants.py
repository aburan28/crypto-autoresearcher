"""Export a verified chain endomorphism as constants for a native implementation.

For each step of the chain (kernel polynomial h of degree s = (ell-1)/2) the
isogeny in projective P^2 coordinates (x = X/Z, y = Y/Z) is

    X' = N_h(X, Z) * psi_h(X, Z),   Y' = Y * M_h(X, Z),   Z' = Z * psi_h(X, Z)^3,

with psi = h, N(x) = x psi(x)^2 + V(x) psi(x) + U(x) the numerator of the
Velu x-map, and M = N' psi - 2 N psi' the numerator of y * dX/dx (the
y-map of a normalised isogeny).  All three polynomials are produced here
from h alone by traces in F_p[T]/(h), checked against the trace-based point
evaluation of ``explicit.KernelIsogeny`` at random points, and written as
hex strings.  Test vectors (a point of prime order, its image, the
eigenvalue, GLV decompositions) let the native code prove itself without
any Python at runtime.

Run from the repository root:

    python3 research/endosweep_20261005/export_chain_constants.py \
        --target "GOST CryptoPro-B" --element 4,1 --out research/endosweep_20261005/cryptopro_b_chain_5_5_7.constants.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from harness.endosweep import explicit as EX          # noqa: E402
from harness.endosweep import lattice as LA           # noqa: E402
from harness.endosweep import quadorder as QO         # noqa: E402
from harness.endosweep.targets import deployed_targets, verify   # noqa: E402
from harness.endosweep.toyverify import Curve         # noqa: E402


def pderiv(f, p):
    return EX._trim([(i * c) % p for i, c in enumerate(f)][1:]) if len(f) > 1 else [0]


def rational_map_polys(E: Curve, h: list[int], ell: int):
    """(N, psi, M) with X = N/psi^2 and Y = y * M/psi^3, computed from h by traces."""
    p, a, b = E.p, E.a, E.b
    s = len(h) - 1
    iso = EX.KernelIsogeny(E, h, ell)          # provides power sums ps[k] = sum x_i^k
    ps = iso.ps

    def trace(f):
        f = EX.pmod(f, h, p)
        return sum(c * ps[k] for k, c in enumerate(f)) % p

    # Q(x, T) = (psi(x) - psi(T)) / (x - T) = sum_k x^k Q_k(T), Q_k = sum_{j>k} c_j T^(j-1-k)
    Q = []
    for k in range(s):
        Qk = [0] * (s - k)
        for j in range(k + 1, s + 1):
            Qk[j - 1 - k] = h[j] % p
        Q.append(EX._trim(Qk))
    vT = EX._trim([2 * a % p, 0, 6 % p])
    uT = EX._trim([4 * b % p, 4 * a % p, 0, 4 % p])
    # V(x) = sum_k x^k Tr(v(T) Q_k(T))
    V = EX._trim([trace(EX.pmul(vT, Q[k], p)) for k in range(s)]) if s else [0]
    # Q(x,T)^2 = sum_k x^k R_k(T),  U(x) = sum_k x^k Tr(u(T) R_k(T))
    R = [[0] for _ in range(2 * s - 1)] if s else [[0]]
    for i in range(s):
        for j in range(s):
            R[i + j] = EX.padd(R[i + j], EX.pmul(Q[i], Q[j], p), p)
    U = EX._trim([trace(EX.pmul(uT, R[k], p)) for k in range(2 * s - 1)]) if s else [0]
    psi2 = EX.pmul(h, h, p)
    N = EX.padd(EX.padd(EX.pmul([0, 1], psi2, p), EX.pmul(V, h, p), p), U, p)
    M = EX.psub(EX.pmul(pderiv(N, p), h, p), EX.pscale(EX.pmul(N, pderiv(h, p), p), 2, p), p)
    assert len(N) - 1 == ell, (len(N) - 1, ell)
    # self-check against the trace evaluation at random points
    rng = random.Random(1)
    for _ in range(3):
        P = E.point(rng.randrange(1 << 30))
        img = iso(P)
        x0, y0 = P
        den = pow(sum(c * pow(x0, i, p) for i, c in enumerate(h)) % p, -1, p)
        Xn = sum(c * pow(x0, i, p) for i, c in enumerate(N)) * den * den % p
        Yn = y0 * sum(c * pow(x0, i, p) for i, c in enumerate(M)) % p * pow(den, 3, p) % p
        assert img == (Xn, Yn), "rational-map polynomials disagree with trace evaluation"
    return N, h, M


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="GOST CryptoPro-B")
    ap.add_argument("--element", default="4,1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--vectors", type=int, default=4)
    args = ap.parse_args(argv)
    T = next(t for t in deployed_targets() if t.name.lower() == args.target.lower())
    verify(T)
    assert T.verified, T.verification
    p, a, b, n, h = T.p, T.coeffs["a"] % T.p, T.coeffs["b"] % T.p, T.n, T.h
    D = QO.small_discriminant_scan(QO.frobenius_discriminant(T.q, T.trace), 2_000_000).found
    ea, eb = (int(v) for v in args.element.split(","))
    res = EX.build_chain_endomorphism(p, a, b, n, h, D, (ea, eb), curve_name=T.name)
    assert res.found, res.note
    E = Curve(p, a, b)
    steps = []
    cur = E
    for ell, hpoly in zip(res.steps, res.kernel_polys):
        N, psi, M = rational_map_polys(cur, hpoly, ell)
        iso = EX.KernelIsogeny(cur, hpoly, ell)
        steps.append({
            "ell": ell,
            "domain": {"a": hex(cur.a), "b": hex(cur.b)},
            "codomain": {"a": hex(iso.codomain.a), "b": hex(iso.codomain.b)},
            "kernel_poly_low_first": [hex(c) for c in hpoly],
            "N_low_first": [hex(c) for c in N],
            "psi_low_first": [hex(c) for c in psi],
            "M_low_first": [hex(c) for c in M],
        })
        cur = iso.codomain
    assert cur.j() == E.j()
    u = res.isomorphism_u
    # full-chain evaluation on test vectors, through the same maps
    chain = [EX.KernelIsogeny(Curve(p, int(s["domain"]["a"], 16), int(s["domain"]["b"], 16)),
                              [int(c, 16) for c in s["kernel_poly_low_first"]], s["ell"]) for s in steps]
    u2, u3 = u * u % p, pow(u, 3, p)

    def phi(P):
        for m in chain:
            P = m(P)
        return (u2 * P[0] % p, u3 * P[1] % p)

    P = EX.point_of_order(E, n, h, 2)
    img = phi(P)
    lam = res.eigenvalue
    assert E.mul(lam, P) == img
    red = LA.reduce([1, lam], n)
    vectors = []
    rng = random.Random(7)
    for i in range(args.vectors):
        Q = EX.point_of_order(E, n, h, 100 + 37 * i)
        k = rng.randrange(1, n)
        k1, k2 = red.decompose(k)
        kQ = E.mul(k, Q)
        vectors.append({"P": [hex(Q[0]), hex(Q[1])], "phiP": [hex(c) for c in phi(Q)],
                        "k": hex(k), "k1": str(k1), "k2": str(k2), "kP": [hex(kQ[0]), hex(kQ[1])]})
        assert E.add(E.mul(k1, Q), E.mul(k2, phi(Q))) == kQ
    out = {
        "target": T.name, "p": hex(p), "a": hex(a), "b": hex(b), "n": hex(n), "cofactor": h,
        "D_K": D, "element": [ea, eb], "matched_element": list(res.matched_element),
        "degree": res.degree, "steps": steps,
        "isomorphism_u": hex(u),
        "eigenvalue": hex(lam),
        "glv_basis": [[str(x) for x in row] for row in red.basis],
        "babai_bound_bits": red.babai_bound.bit_length(),
        "test_vectors": vectors,
        "coordinates": "projective P^2 (x=X/Z, y=Y/Z): X'=N(X,Z)*psi(X,Z), Y'=Y*M(X,Z), Z'=Z*psi(X,Z)^3 with "
                       "homogenised polynomials; final isomorphism (x,y)->(u^2 x, u^3 y).",
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("steps", "test_vectors", "glv_basis")}, indent=1))
    print("steps:", [(s["ell"], len(s["N_low_first"]) - 1, len(s["M_low_first"]) - 1) for s in steps])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
