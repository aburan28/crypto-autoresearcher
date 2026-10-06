"""Target registry: deployed curves, self-verified before any sweep runs.

Every entry carries the field, model, coefficients, prime subgroup order n
and cofactor h.  ``verify`` recomputes, from those numbers alone, that

* n is prime and h*n lies in the Hasse interval,
* a deterministic point on the stated curve equation is killed by h*n,
  which with n > 4 sqrt(q) pins #E(F_q) = h*n exactly (the order of the
  point is divisible by n, n | #E, and only one multiple of n is in the
  interval),

so a typo in a constant is caught here, not reported as a curve property.
Entries that fail verification are excluded from every sweep and listed as
such; nothing is guessed.

Extension-field groups (G2 of pairing curves, GLS-type families) are
``structural`` entries: the sweeper needs only n and the eigenvalues of the
declared endomorphisms on the subgroup, both of which are public and
re-derived here (ψ acts on G2 as multiplication by p; a GLS ψ satisfies
ψ² = -1), so no extension-field curve arithmetic is required for them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isqrt

from sympy import isprime


@dataclass
class Target:
    name: str
    p: int
    model: str                       # 'weierstrass' | 'montgomery' | 'edwards' | 'structural'
    coeffs: dict
    n: int                           # prime subgroup order
    h: int                           # cofactor: #E(F_q) = h * n
    ext_degree: int = 1              # q = p^ext_degree
    cost_model: str = "weierstrass_jacobian_a=-3"
    declared_generators: list[dict] = field(default_factory=list)
    notes: str = ""
    family: str = "deployed"
    verified: bool | None = None
    verification: str = ""

    @property
    def q(self) -> int:
        return self.p ** self.ext_degree

    @property
    def order(self) -> int:
        return self.h * self.n

    @property
    def trace(self) -> int:
        return self.q + 1 - self.order


# ---------------------------------------------------------------------------
# affine arithmetic in each model (verification only; slow and obvious)
# ---------------------------------------------------------------------------

def _w_add(p, a, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def _m_add(p, A, B, P, Q):
    """B y^2 = x^3 + A x^2 + x."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + 2 * A * x1 + 1) * pow(2 * B * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (B * lam * lam - A - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def _e_add(p, a, d, P, Q):
    """a x^2 + y^2 = 1 + d x^2 y^2, identity (0, 1); complete for a square, d non-square."""
    x1, y1 = P
    x2, y2 = Q
    x1x2 = x1 * x2 % p
    y1y2 = y1 * y2 % p
    dxy = d * x1x2 * y1y2 % p
    x3 = (x1 * y2 + y1 * x2) * pow((1 + dxy) % p, -1, p) % p
    y3 = (y1y2 - a * x1x2) * pow((1 - dxy) % p, -1, p) % p
    return (x3, y3)


def _sqrt(a: int, p: int) -> int | None:
    from sympy.ntheory import sqrt_mod
    r = sqrt_mod(a % p, p)
    return None if r is None else int(r)


def _mul(add, identity, k, P):
    R = identity
    Q = P
    while k:
        if k & 1:
            R = add(R, Q)
        Q = add(Q, Q)
        k >>= 1
    return R


def verify(t: Target) -> Target:
    """Fill t.verified / t.verification; never raises on bad constants."""
    p, n, h = t.p, t.n, t.h
    q = t.q
    try:
        if not isprime(n):
            raise ValueError("n is not prime")
        N = h * n
        if t.model == "structural":
            if not isprime(p):
                raise ValueError("p is not prime")
            if h == 0:
                t.verified, t.verification = True, "structural entry: n prime; cofactor not declared, Hasse check skipped"
                return t
            if abs(q + 1 - N) > 2 * isqrt(q) + 1:
                raise ValueError("h*n is outside the Hasse interval")
            t.verified, t.verification = True, "structural entry: n prime, Hasse interval ok"
            return t
        if abs(q + 1 - N) > 2 * isqrt(q) + 1:
            raise ValueError("h*n is outside the Hasse interval")
        if not isprime(p):
            raise ValueError("p is not prime")
        if 4 * isqrt(q) >= n:
            raise ValueError("n too small to pin the group order from one point")
        # deterministic point search on the stated model
        found = False
        for x in range(2, 2 + 500):
            if t.model == "weierstrass":
                a, b = t.coeffs["a"] % p, t.coeffs["b"] % p
                rhs = (x * x * x + a * x + b) % p
                y = _sqrt(rhs, p)
                if y is None:
                    continue
                add = lambda P, Q: _w_add(p, a, P, Q)
                ident = None
                P = (x, y)
            elif t.model == "montgomery":
                A, B = t.coeffs["A"] % p, t.coeffs.get("B", 1) % p
                rhs = (x * x * x + A * x * x + x) * pow(B, -1, p) % p
                y = _sqrt(rhs, p)
                if y is None:
                    continue
                add = lambda P, Q: _m_add(p, A, B, P, Q)
                ident = None
                P = (x, y)
            elif t.model == "edwards":
                a, d = t.coeffs["a"] % p, t.coeffs["d"] % p
                # y^2 = (1 - a x^2) / (1 - d x^2)
                num = (1 - a * x * x) % p
                den = (1 - d * x * x) % p
                y = _sqrt(num * pow(den, -1, p) % p, p)
                if y is None:
                    continue
                add = lambda P, Q: _e_add(p, a, d, P, Q)
                ident = (0, 1)
                P = (x, y)
            else:
                raise ValueError(f"unknown model {t.model}")
            R = _mul(add, ident, N, P)
            if R != ident:
                raise ValueError(f"h*n does not kill the point with x={x}")
            # n must divide the order of P: h*P != identity
            if _mul(add, ident, h, P) == ident:
                continue   # unlucky small-order point; try another x
            found = True
            break
        if not found:
            raise ValueError("no point of order divisible by n found in 500 tries")
        t.verified = True
        t.verification = f"point with x={x} has order divisible by n and is killed by h*n; #E = h*n"
    except Exception as e:  # noqa: BLE001 - we want the message, whatever it is
        t.verified = False
        t.verification = f"VERIFICATION FAILED: {e}"
    return t


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

def _hex(s: str) -> int:
    return int(s.replace(" ", "").replace("\n", ""), 16)


def deployed_targets() -> list[Target]:
    T: list[Target] = []
    # --- secp256k1 (Bitcoin) --------------------------------------------
    T.append(Target(
        "secp256k1", 2**256 - 2**32 - 977, "weierstrass", {"a": 0, "b": 7},
        _hex("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141"), 1,
        cost_model="weierstrass_jacobian_a=0", notes="j = 0, CM by Z[zeta_3]"))
    # --- NIST P-256 / secp256r1 ------------------------------------------
    T.append(Target(
        "NIST P-256", 2**256 - 2**224 + 2**192 + 2**96 - 1, "weierstrass",
        {"a": -3, "b": _hex("5AC635D8 AA3A93E7 B3EBBD55 769886BC 651D06B0 CC53B0F6 3BCE3C3E 27D2604B")},
        _hex("FFFFFFFF 00000000 FFFFFFFF FFFFFFFF BCE6FAAD A7179E84 F3B9CAC2 FC632551"), 1))
    # --- NIST P-384 ------------------------------------------------------
    T.append(Target(
        "NIST P-384", 2**384 - 2**128 - 2**96 + 2**32 - 1, "weierstrass",
        {"a": -3, "b": _hex("B3312FA7 E23EE7E4 988E056B E3F82D19 181D9C6E FE814112 0314088F "
                            "5013875A C656398D 8A2ED19D 2A85C8ED D3EC2AEF")},
        _hex("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF C7634D81 F4372DDF "
             "581A0DB2 48B0A77A ECEC196A CCC52973"), 1))
    # --- NIST P-521 ------------------------------------------------------
    T.append(Target(
        "NIST P-521", 2**521 - 1, "weierstrass",
        {"a": -3, "b": _hex("0051 953EB961 8E1C9A1F 929A21A0 B68540EE A2DA725B 99B315F3 B8B48991 "
                            "8EF109E1 56193951 EC7E937B 1652C0BD 3BB1BF07 3573DF88 3D2C34F1 "
                            "EF451FD4 6B503F00")},
        _hex("01FF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFA "
             "51868783 BF2F966B 7FCC0148 F709A5D0 3BB5C9B8 899C47AE BB6FB71E 91386409"), 1))
    # --- brainpoolP256r1 ----------------------------------------------------
    T.append(Target(
        "brainpoolP256r1",
        _hex("A9FB57DB A1EEA9BC 3E660A90 9D838D72 6E3BF623 D5262028 2013481D 1F6E5377"),
        "weierstrass",
        {"a": _hex("7D5A0975 FC2C3057 EEF67530 417AFFE7 FB8055C1 26DC5C6C E94A4B44 F330B5D9"),
         "b": _hex("26DC5C6C E94A4B44 F330B5D9 BBD77CBF 95841629 5CF7E1CE 6BCCDC18 FF8C07B6")},
        _hex("A9FB57DB A1EEA9BC 3E660A90 9D838D71 8C397AA3 B561A6F7 901E0E82 974856A7"), 1,
        cost_model="weierstrass_jacobian_generic_a"))
    # --- SM2 -------------------------------------------------------------
    T.append(Target(
        "SM2", _hex("FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF 00000000 FFFFFFFF FFFFFFFF"),
        "weierstrass",
        {"a": -3, "b": _hex("28E9FA9E 9D9F5E34 4D5A9E4B CF6509A7 F39789F5 15AB8F92 DDBCBD41 4D940E93")},
        _hex("FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF 7203DF6B 21C6052B 53BBF409 39D54123"), 1))
    # --- GOST R 34.10-2001 CryptoPro parameter sets (RFC 4357) ----------------
    T.append(Target(
        "GOST CryptoPro-A", _hex("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFD97"),
        "weierstrass", {"a": -3, "b": 0xA6},
        _hex("FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF 6C611070 995AD100 45841B09 B761B893"), 1,
        notes="id-GostR3410-2001-CryptoPro-A-ParamSet"))
    T.append(Target(
        "GOST CryptoPro-B", _hex("80000000 00000000 00000000 00000000 00000000 00000000 00000000 00000C99"),
        "weierstrass",
        {"a": -3, "b": _hex("3E1AF419 A269A5F8 66A7D3C2 5C3DF80A E9792593 73FF2B18 2F49D4CE 7E1BBC8B")},
        _hex("80000000 00000000 00000000 00000001 5F700CFF F1A624E5 E497161B CC8A198F"), 1,
        notes="id-GostR3410-2001-CryptoPro-B-ParamSet"))
    T.append(Target(
        "GOST CryptoPro-C", _hex("9B9F605F 5A858107 AB1EC85E 6B41C8AA CF846E86 789051D3 7998F7B9 022D759B"),
        "weierstrass", {"a": -3, "b": 0x805A},
        _hex("9B9F605F 5A858107 AB1EC85E 6B41C8AA 582CA351 1EDDFB74 F02F3A65 98980BB9"), 1,
        notes="id-GostR3410-2001-CryptoPro-C-ParamSet"))
    T.append(Target(
        "GOST 2001 test curve", _hex("80000000 00000000 00000000 00000000 00000000 00000000 00000000 00000431"),
        "weierstrass",
        {"a": 7, "b": _hex("5FBFF498 AA938CE7 39B8E022 FBAFEF40 563F6E6A 3472FC2A 514C0CE9 DAE23B7E")},
        _hex("80000000 00000000 00000000 00000001 50FE8A18 92976154 C59CFC19 3ACCF5B3"), 1,
        cost_model="weierstrass_jacobian_generic_a",
        notes="id-GostR3410-2001-TestParamSet (a test vector, not a deployed curve)"))
    # --- Curve25519 --------------------------------------------------------
    T.append(Target(
        "Curve25519", 2**255 - 19, "montgomery", {"A": 486662, "B": 1},
        2**252 + 27742317777372353535851937790883648493, 8,
        cost_model="twisted_edwards_a=-1_extended"))
    # --- Ed448-Goldilocks -----------------------------------------------------
    T.append(Target(
        "Ed448-Goldilocks", 2**448 - 2**224 - 1, "edwards", {"a": 1, "d": -39081},
        2**446 - 13818066809895115352007386748515426880336692474882178609894547503885, 4,
        cost_model="twisted_edwards_a=-1_extended",
        notes="cost model approximated by the a=-1 extended counts (a=1 is slightly dearer)"))
    # --- Curve1174 ----------------------------------------------------------
    T.append(Target(
        "Curve1174", 2**251 - 9, "edwards", {"a": 1, "d": -1174},
        2**249 - 11332719920821432534773113288178349711, 4,
        cost_model="twisted_edwards_a=-1_extended"))
    # --- Curve41417 --------------------------------------------------------
    T.append(Target(
        "Curve41417", 2**414 - 17, "edwards", {"a": 1, "d": 3617},
        2**411 - 33364140863755142520810177694098385178984727200411208589594759, 8,
        cost_model="twisted_edwards_a=-1_extended"))
    # --- E-521 ----------------------------------------------------------------
    T.append(Target(
        "E-521", 2**521 - 1, "edwards", {"a": 1, "d": -376014},
        2**519 - 337554763258501705789107630418782636071904961214051226618635150085779108655765, 4,
        cost_model="twisted_edwards_a=-1_extended"))
    # --- M-511 ---------------------------------------------------------------
    T.append(Target(
        "M-511", 2**511 - 187, "montgomery", {"A": 530438, "B": 1},
        2**508 + 10724754759635747624044531514068121842070756627434833028965540808827675062043, 8,
        cost_model="twisted_edwards_a=-1_extended"))
    # --- BN254 (alt_bn128) G1 ----------------------------------------------------
    bn_p = 21888242871839275222246405745257275088696311157297823662689037894645226208583
    bn_r = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    T.append(Target("BN254 G1", bn_p, "weierstrass", {"a": 0, "b": 3}, bn_r, 1,
                    cost_model="weierstrass_jacobian_a=0", notes="j = 0 pairing curve, k = 12"))
    # --- BLS12-381 G1 --------------------------------------------------------------
    bls_p = _hex("1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab")
    bls_r = _hex("73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001")
    bls_h1 = _hex("396c8c005555e1568c00aaab0000aaab")
    T.append(Target("BLS12-381 G1", bls_p, "weierstrass", {"a": 0, "b": 4}, bls_r, bls_h1,
                    cost_model="weierstrass_jacobian_a=0", notes="j = 0 pairing curve, k = 12"))
    return T


def structural_targets() -> list[Target]:
    """Groups whose decomposition structure is fixed by public eigenvalue relations."""
    T: list[Target] = []
    bn_p = 21888242871839275222246405745257275088696311157297823662689037894645226208583
    bn_r = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    bls_p = _hex("1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab")
    bls_r = _hex("73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001")
    for name, p, r in (("BN254 G2", bn_p, bn_r), ("BLS12-381 G2", bls_p, bls_r)):
        # G2 lives on the sextic twist over F_{p^2}; psi acts as [p] on G2, and
        # r | Phi_12(p) so p has order 12 mod r.  The j=0 automorphism acts as
        # a primitive cube root of unity, p^4 mod r.
        assert pow(p, 12, r) == 1 and pow(p, 4, r) != 1 and pow(p, 6, r) != 1
        T.append(Target(
            name, p, "structural", {}, r, 0, ext_degree=2,
            cost_model="weierstrass_jacobian_a=0",
            declared_generators=[
                {"name": "psi (untwist-Frobenius-twist)", "eigenvalue": p % r,
                 "cost_key": "g2_psi", "kind": "frobenius", "order_mod_n": 12},
                {"name": "zeta_3 automorphism", "eigenvalue": pow(p, 4, r),
                 "cost_key": "unit", "kind": "unit", "order_mod_n": 3},
            ],
            family="structural",
            notes="costs in F_{p^2} multiplications; n = r is the G2 subgroup order"))
    return T


def synthetic_gls_targets(bits: int = 127, seed_offset: int = 0) -> list[Target]:
    """Synthetic F_{p^2} groups with the GLS relation psi^2 = -1 (and zeta_3).

    No curve is constructed: the lattice of a GLS decomposition depends only
    on n and the eigenvalue relations, which are theorems (Galbraith-Lin-
    Scott 2009; Longa-Sica 2012), so a prime n = 1 mod 12 of the right size
    exhibits the exact lattice geometry.  Labelled synthetic in every report.
    """
    from sympy import nextprime
    from sympy.ntheory import sqrt_mod
    from sympy.ntheory.residue_ntheory import nthroot_mod
    T: list[Target] = []
    p = 2**bits - 1 if isprime(2**bits - 1) else nextprime(2**bits)
    n = nextprime(p * p - 2 * p + seed_offset)
    while n % 12 != 1:
        n = nextprime(n)
    i_root = int(sqrt_mod(n - 1, n))
    z3 = int(nthroot_mod(1, 3, n, all_roots=True)[1])
    T.append(Target(
        f"synthetic GLS over F_p^2, p~2^{bits}", p, "structural", {}, n, 0, ext_degree=2,
        cost_model="twisted_edwards_a=-1_extended",
        declared_generators=[
            {"name": "psi (GLS twist Frobenius), psi^2=-1", "eigenvalue": i_root,
             "cost_key": "gls_psi", "kind": "frobenius", "order_mod_n": 4},
            {"name": "zeta_3 automorphism (j=0 variant)", "eigenvalue": z3,
             "cost_key": "unit", "kind": "unit", "order_mod_n": 3},
        ],
        family="synthetic", notes="costs in F_{p^2} multiplications"))
    return T


def synthetic_cm_targets(discs=(-7, -8, -11, -19, -43, -67, -163, -15, -20, -23, -24, -31, -47, -71),
                         bits: int = 256) -> list[Target]:
    """Synthetic prime-order CM curves over F_p with small discriminant D.

    For each D a prime p = (a^2 + |D| b^2)/4 is found with #E = p + 1 - a
    prime (one of the two twists), so E has CM by the maximal order of
    Q(sqrt D) and the whole cheap-endomorphism inventory of that order.  No
    curve equation is produced (it would need CM class polynomials); the
    sweeper only needs (p, n, D), and every endomorphism eigenvalue follows
    from D and n alone.  Labelled synthetic in every report.
    """
    import random
    from sympy import nextprime
    T: list[Target] = []
    for D in discs:
        rng = random.Random(D)
        absD = -D
        tau = D % 2
        found = None
        for _ in range(400000):
            b = rng.randrange(1 << (bits // 2 - absD.bit_length() // 2 - 2),
                              1 << (bits // 2 - absD.bit_length() // 2 - 1))
            a = rng.randrange(1 << (bits // 2 - 2), 1 << (bits // 2 - 1))
            # 4p = a^2 + |D| b^2 needs a = b*tau (mod 2); the parity of the
            # trace a then decides whether #E can be prime (D = 5 mod 8) or
            # must carry a cofactor 2 or 4 (2 splits or ramifies otherwise).
            if (a - b * tau) % 2:
                a += 1
            m = a * a + absD * b * b
            if m % 4:
                continue
            p = m // 4
            if p % 2 == 0 or p % 3 == 0 or p % 5 == 0 or p % 7 == 0 or not isprime(p):
                continue
            for t in (a, -a):
                N = p + 1 - t
                for h in (1, 2, 4):
                    if N % h == 0 and isprime(N // h):
                        found = (p, N // h, h)
                        break
                if found:
                    break
            if found:
                break
        if not found:
            continue
        p, n, h = found
        T.append(Target(
            f"synthetic CM D={D}, p~2^{p.bit_length()}", p, "structural",
            {"D": D}, n, h, cost_model="weierstrass_jacobian_generic_a",
            family="synthetic",
            notes=f"prime-order curve with CM by the maximal order of Q(sqrt({D})); class number h({D})"))
    return T


def all_targets(*, include_synthetic: bool = True) -> list[Target]:
    T = deployed_targets() + structural_targets()
    if include_synthetic:
        T += synthetic_gls_targets() + synthetic_cm_targets()
    return [verify(t) for t in T]
