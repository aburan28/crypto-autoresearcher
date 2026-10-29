#!/usr/bin/env python3
"""P1 / P-N1 / P-N2 (SHF-20261016-3caa6f, SHF-20261017-e4d7f6): independent
arithmetic for crypto:papers/lll-degeneracy-note at a pinned commit.

1. Curve constants (copied from crypto:src/ecc/curve.rs and curve_zoo.rs) are
   checked independently: G on the curve, n probable-prime, n*G = O by our own
   Jacobian arithmetic, and |p + 1 - n| <= 2 sqrt(p) (so n = #E, cofactor 1).
2. Exact rational comparison n^4 > f64::MAX = (2^53 - 1) 2^971, and the f64
   path (Python float = IEEE binary64, round-to-nearest-even).
3. P-521 scaled diagonal: emulates big_to_f64_scaled(n^2, max_bits - 500)
   (crypto:src/cryptanalysis/lattice.rs:431-459) under correct rounding (what
   num-bigint 0.5.1's to_f64 does; crypto locks 0.4.8, not on disk) and under
   truncation, and the first Gram-Schmidt subtraction for row m.
4. The 'residual-dominates' condition (true b*_m[m] below one ulp of the
   scaled n*a entries) for each curve.
5. Re-counts the re-run table from the committed probe logs (P-N2).
6. Checks two numeric statements in research/notes/lattice-hnp/
   RESEARCH_LLL_GS_ANALYSIS.md §10.1 (f64::MAX ~ 2^1023; P-256 n smaller by ~2^192).

Usage: python3 -I p1_pn1_f64.py /home/user/crypto <rev>
"""
import math
import random
import re
import subprocess
import sys
from fractions import Fraction

repo, rev = sys.argv[1], sys.argv[2]

C = {
    "secp192k1": dict(p="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFEE37", a="0", b="3",
                      gx="DB4FF10EC057E9AE26B07D0280B7F4341DA5D1B1EAE06C7D",
                      gy="9B2F2F6D9C5628A7844163D015BE86344082AA88D95E2F9D",
                      n="FFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D"),
    "secp224k1": dict(p="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFE56D", a="0", b="5",
                      gx="A1455B334DF099DF30FC28A169A467E9E47075A90F7E650EB6B7A45C",
                      gy="7E089FED7FBA344282CAFBD6F7E319F7C0B0BD59E2CA4BDB556D61A5",
                      n="010000000000000000000000000001DCE8D2EC6184CAF0A971769FB1F7"),
    "secp256k1": dict(p="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", a="0", b="7",
                      gx="79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
                      gy="483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",
                      n="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"),
    "P-256": dict(p="ffffffff00000001000000000000000000000000ffffffffffffffffffffffff",
                  a="ffffffff00000001000000000000000000000000fffffffffffffffffffffffc",
                  b="5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b",
                  gx="6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296",
                  gy="4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5",
                  n="ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551"),
    "brainpoolP256r1": dict(p="A9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377",
                            a="7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9",
                            b="26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6",
                            gx="8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262",
                            gy="547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997",
                            n="A9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7"),
    "P-384": dict(p="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFF",
                  a="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFC",
                  b="B3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF",
                  gx="AA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7",
                  gy="3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F",
                  n="FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973"),
    "brainpoolP384r1": dict(p="8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53",
                            a="7BC382C63D8C150C3C72080ACE05AFA0C2BEA28E4FB22787139165EFBA91F90F8AA5814A503AD4EB04A8C7DD22CE2826",
                            b="04A8C7DD22CE28268B39B55416F0447C2FB77DE107DCD2A62E880EA53EEB62D57CB4390295DBC9943AB78696FA504C11",
                            gx="1D1C64F068CF45FFA2A63A81B7C13F6B8847A3E77EF14FE3DB7FCAFE0CBD10E8E826E03436D646AAEF87B2E247D4AF1E",
                            gy="8ABE1D7520F9C2A45CB1EB8E95CFD55262B70B29FEEC5864E19C054FF99129280E4646217791811142820341263C5315",
                            n="8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565"),
    "P-521": dict(p="1" + "F" * 130, a="1" + "F" * 129 + "C",
                  b="51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00",
                  gx="C6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66",
                  gy="11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650",
                  n="1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409"),
}
K_TABLE = {"secp192k1": 144, "secp224k1": 168, "secp256k1": 192, "P-256": 192,
           "brainpoolP256r1": 192, "P-384": 288, "brainpoolP384r1": 288, "P-521": 384}


def is_probable_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = random.Random(20261028)
    for _ in range(40):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def jac_double(P, a, p):
    X, Y, Z = P
    if Y == 0 or Z == 0:
        return (1, 1, 0)
    S = 4 * X * Y * Y % p
    M = (3 * X * X + a * pow(Z, 4, p)) % p
    X3 = (M * M - 2 * S) % p
    Y3 = (M * (S - X3) - 8 * pow(Y, 4, p)) % p
    Z3 = 2 * Y * Z % p
    return (X3, Y3, Z3)


def jac_add(P, Q, a, p):
    if P[2] == 0:
        return Q
    if Q[2] == 0:
        return P
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    U1 = X1 * Z2 * Z2 % p
    U2 = X2 * Z1 * Z1 % p
    S1 = Y1 * pow(Z2, 3, p) % p
    S2 = Y2 * pow(Z1, 3, p) % p
    if U1 == U2:
        return jac_double(P, a, p) if S1 == S2 else (1, 1, 0)
    H = (U2 - U1) % p
    R = (S2 - S1) % p
    X3 = (R * R - H ** 3 - 2 * U1 * H * H) % p
    Y3 = (R * (U1 * H * H - X3) - S1 * H ** 3) % p
    Z3 = H * Z1 * Z2 % p
    return (X3, Y3, Z3)


def mul(k, P, a, p):
    R = (1, 1, 0)
    for bit in bin(k)[2:]:
        R = jac_double(R, a, p)
        if bit == "1":
            R = jac_add(R, P, a, p)
    return R


F64_MAX = Fraction((2 ** 53 - 1) * 2 ** 971)
assert float(F64_MAX) == sys.float_info.max


def f64_trunc(x):
    """Largest binary64 <= x for a positive int x (truncating conversion)."""
    sh = max(x.bit_length() - 53, 0)
    return float(x >> sh) * 2.0 ** sh if sh < 1024 else math.inf


def big_to_f64_scaled(x, shift, conv):
    """crypto:src/cryptanalysis/lattice.rs big_to_f64_scaled, with `conv` as BigInt::to_f64."""
    if x == 0 or shift == 0:
        return conv(x)
    nb = x.bit_length()
    if nb + shift <= 1020:
        return conv(x) / 2.0 ** shift
    extra = nb - 1020
    return conv(x >> extra) * 2.0 ** (extra - shift)


print(f"commit {rev}")
print(f"f64::MAX = (2^53-1)*2^971 = {float(F64_MAX)!r}; log2 = {math.log2(float(F64_MAX)):.17f}")
print()
print("== 1-2. curve orders, n^4 against f64::MAX ==")
hdr = f"{'curve':16} {'n_bits':>6} {'order ok':>8} {'log2(n^4)':>12} {'n^4>MAX exact':>13} {'f64(n)^4':>10} {'k_bits 3n/4':>11} {'table k':>7}"
print(hdr)
info = {}
for name, c in C.items():
    p, a, b, gx, gy, n = (int(c[k], 16) for k in ("p", "a", "b", "gx", "gy", "n"))
    on = (gy * gy - gx ** 3 - a * gx - b) % p == 0
    prime = is_probable_prime(n)
    inf = mul(n, (gx, gy, 1), a, p)[2] == 0
    hasse = (p + 1 - n) ** 2 <= 4 * p
    ok = on and prime and inf and hasse
    exact = Fraction(n) ** 4 > F64_MAX
    fn = float(n)
    f4 = fn * fn * fn * fn
    kb = 3 * n.bit_length() // 4
    info[name] = dict(n=n, nbits=n.bit_length())
    print(f"{name:16} {n.bit_length():6d} {str(ok):>8} {4 * math.log2(n):12.6f} {str(exact):>13} {('inf' if math.isinf(f4) else 'finite'):>10} {kb:11d} {K_TABLE[name]:7d}")
print()
print("Claims: only secp256k1 among the 256-bit curves has n^4 > f64::MAX; every 384-bit curve does.")
print(f"  256-bit curves with n^4 > MAX: {[k for k in ('secp256k1', 'P-256', 'brainpoolP256r1') if Fraction(info[k]['n']) ** 4 > F64_MAX]}")
print(f"  384-bit curves with n^4 > MAX: {[k for k in ('P-384', 'brainpoolP384r1') if Fraction(info[k]['n']) ** 4 > F64_MAX]}")
print(f"  P-521 floor(3*521/4) = {3 * 521 // 4}; probes use 384 = 3/4*512: {3 * 512 // 4 == 384}")
n256, nk1 = info["P-256"]["n"], info["secp256k1"]["n"]
print(f"  2^256 - n(secp256k1): log2 = {math.log2(2 ** 256 - nk1):.3f}; 2^256 - n(P-256): log2 = {math.log2(2 ** 256 - n256):.3f}")
print(f"  n(secp256k1) - n(P-256): log2 = {math.log2(nk1 - n256):.3f}   (analysis §10.1 says '~2^192')")
print(f"  log2(f64::MAX) = {math.log2(float(F64_MAX)):.6f}   (analysis §10.1 says 'f64::MAX ~ 2^1023')")
print(f"  P-256 n^4 / f64::MAX = {float(Fraction(n256) ** 4 / F64_MAX):.12f} (below 1 by ~2^{math.log2(1 - float(Fraction(n256) ** 4 / F64_MAX)):.1f})")
print()

print("== 3. P-521 scaled diagonal and the first GS subtraction (row m against rows 0..m-1) ==")
n = info["P-521"]["n"]
nn = n * n
max_bits = nn.bit_length()
shift = max_bits - 500
print(f"bits(n^2) = {max_bits}; scale_shift = max_bits - 500 = {shift}")
print(f"exact n^2 / 2^{shift} = 2^500 * (1 - {float(1 - Fraction(nn, 2 ** (shift + 500))):.3e})")
rng = random.Random(1)
for mode, conv in (("round-to-nearest (num-bigint 0.5.1 to_f64)", float), ("truncation (hypothetical)", f64_trunc)):
    diag = big_to_f64_scaled(nn, shift, conv)
    worst = 0.0
    for _ in range(64):
        a_l = rng.randrange(1, n)
        bi = big_to_f64_scaled(n * a_l, shift, conv)
        dot = bi * diag
        norm = diag * diag
        mu = dot / norm
        resid = bi - mu * diag
        worst = max(worst, abs(resid))
    print(f"  {mode}: diag == 2^500: {diag == 2.0 ** 500}; diag = 2^500*(1 - {1 - diag / 2.0 ** 500:.3e});"
          f" max |b*_m[l]| after subtracting mu*b*_l over 64 random a_l: {worst!r}"
          + (f" (= 2^{math.log2(worst):.1f})" if worst else ""))
print(f"  true scaled b*_m[m] = 2^384 / 2^{shift} = 2^{384 - shift}")
print()

print("== 4. residual-dominates condition: true component 2^k_bits/2^shift below one ulp of the scaled n*a entries ==")
for name in ("P-256", "brainpoolP256r1", "brainpoolP384r1", "P-384", "secp256k1", "P-521"):
    n = info[name]["n"]
    mb = (n * n).bit_length()
    sh = max(mb - 500, 0)
    entry_log2 = (n * (n - 1)).bit_length() - sh  # largest n*a_l, scaled
    ulp_log2 = entry_log2 - 53
    true_log2 = K_TABLE[name] - sh
    print(f"  {name:16} shift={sh:3d}  scaled n*a ~ 2^{entry_log2}  ulp ~ 2^{ulp_log2}  true b*_m[m] = 2^{true_log2}  dominated: {true_log2 < ulp_log2}")
print()

print("== 5. re-run table recount from committed probe logs (P-N2) ==")


def show(path):
    return subprocess.run(["git", "-C", repo, "-c", "gc.auto=0", "show", f"{rev}:{path}"],
                          capture_output=True, check=True).stdout.decode()


base = "research/lll_degeneracy_rerun_20261016/logs/"
probes = show(base + "probes.log")
hp = show(base + "p521_hp.log")
src = show("tests/lll_degeneracy_probe.rs")
pair_of = {}
for d, k in re.findall(r"\((0x[0-9A-Fa-f_]+),\s*(0x[0-9A-Fa-f_]+)(?:,\s*\d+)?\)", src):
    pair_of[int(d.replace("_", ""), 16)] = int(k.replace("_", ""), 16)
rows = {}
times = []
pat1 = re.compile(r"^(\S+)\s+k_bits=\s*(\d+) m=\s*(\d+) d_seed=0x([0-9A-F]+) k_seed=0x([0-9A-F]+)\s+→\s+(✓|✗).*\((\d+) ms\)")
for line in probes.splitlines():
    m = pat1.match(line)
    if m:
        cur, kb, mm, ds, ks, ok, ms = m.groups()
        key = (cur, "scaled f64", int(kb))
        r = rows.setdefault(key, {"runs": 0, "rec": 0, "pairs": set(), "rec_pairs": set()})
        r["runs"] += 1
        r["rec"] += ok == "✓"
        r["pairs"].add((int(ds, 16), int(ks, 16)))
        if ok == "✓":
            r["rec_pairs"].add((int(ds, 16), int(ks, 16)))
        times.append((cur, int(ms)))
pat2 = re.compile(r"^P-521\[(f64|HP)\]\s+k_bits=(\d+) m=\s*(\d+) reduction=\S+\s+d_seed=0x([0-9A-F]+)\s+→\s+(✓|✗)")
for line in hp.splitlines():
    m = pat2.match(line)
    if m:
        kind, kb, mm, ds, ok = m.groups()
        gs = "scaled f64" if kind == "f64" else "2048-bit fixed point"
        key = ("P-521", gs, int(kb))
        r = rows.setdefault(key, {"runs": 0, "rec": 0, "pairs": set(), "rec_pairs": set()})
        pair = (int(ds, 16), pair_of[int(ds, 16)])
        r["runs"] += 1
        r["rec"] += ok == "✓"
        r["pairs"].add(pair)
        if ok == "✓":
            r["rec_pairs"].add(pair)
print(f"  {'curve':16} {'GS':22} {'k_bits':>6} {'rec/distinct':>12} {'runs rec/total':>14}")
for (cur, gs, kb), r in rows.items():
    print(f"  {cur:16} {gs:22} {kb:6d} {len(r['rec_pairs']):5d} / {len(r['pairs']):<4d} {r['rec']:6d} / {r['runs']:<5d}")
t256 = [t for c, t in times if c in ("secp256k1", "P-256", "brainpoolP256r1")]
t384 = [t for c, t in times if c in ("P-384", "brainpoolP384r1")]
print(f"  probe times at n_bits 256: {min(t256)}-{max(t256)} ms ({len(t256)} probes); at 384: {min(t384)}-{max(t384)} ms ({len(t384)} probes)")
