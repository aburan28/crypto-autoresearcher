"""R1 independent cross-check of the Lean data blocks against the committed JSON.

Run: python3 -I check_data.py
Parses formal/CryptoResearch/Endosweep/{NistCertificates,Koblitz}.lean with regexes,
then recomputes everything from nist.json / factorizations.jsonl / published hex.
"""
import json
import re
import sys
from math import isqrt, gcd

ROOT = "/home/user/wt/lean"
RES = ROOT + "/research/endosweep_nist_20261006"
NIST = json.load(open(RES + "/nist.json"))["curves"]
FACS = [json.loads(l) for l in open(RES + "/factorizations.jsonl") if l.strip()]
FAC_BY_N = {int(r["N"]): r for r in FACS}

import cypari2
pari = cypari2.Pari()
pari.allocatemem(2 * 10 ** 9)


def isprime(n):
    return bool(pari.isprime(n))  # PARI isprime: proven (APRCL/ECPP-style), not BPSW only


def lean_blocks(path):
    src = open(path).read()
    out = {}
    for m in re.finditer(r"def (\w+) : (\w+) where\n(.*?)(?=\n\n)", src, re.S):
        name, typ, body = m.group(1), m.group(2), m.group(3)
        fields = {}
        for fm in re.finditer(r"^\s+(\w+|δ|μ) := (.*)$", body, re.M):
            fields[fm.group(1)] = fm.group(2).strip()
        out[name] = (typ, fields)
    return out, src


def pyval(s):
    s = s.replace("⟨", "(").replace("⟩", ")")
    return eval(s, {})


fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("FAIL:", msg)


# ----------------------------------------------------------------- NistCertificates
blocks, src = lean_blocks(ROOT + "/formal/CryptoResearch/Endosweep/NistCertificates.lean")
name2key = {"P192": "nist/P-192", "P224": "nist/P-224", "P256": "nist/P-256", "P384": "nist/P-384",
            "P521": "nist/P-521", "B163": "nist/B-163", "B233": "nist/B-233", "B283": "nist/B-283",
            "B409": "nist/B-409", "Curve25519": "other/Curve25519", "Ed25519": "other/Ed25519",
            "Curve448": "other/Curve448", "Ed448": "other/Ed448", "Ed448Goldilocks": "other/Ed448-Goldilocks",
            "K163": "nist/K-163", "K233": "nist/K-233", "K283": "nist/K-283", "K409": "nist/K-409", "K571": "nist/K-571"}
print("== NistCertificates FactoredCert / ScanCert")
largeprimes_all = set()
for name, (typ, f) in blocks.items():
    if typ not in ("FactoredCert", "ScanCert"):
        continue
    J = NIST[name2key[name]]
    q, t, DK, ff, deg = (pyval(f[k]) for k in ("q", "t", "DK", "f", "deg"))
    check(q == J["q"], f"{name} q")
    check(t == J["t"], f"{name} t")
    ex = J["exact"]
    check(DK == ex["D_K"], f"{name} D_K")
    check(ff == ex["f"], f"{name} f")
    check(deg == ex["min_nonscalar_degree"] if "min_nonscalar_degree" in ex else deg == 2, f"{name} deg vs json")
    # python harness recomputation
    check(deg == (abs(DK) + DK % 2) // 4, f"{name} deg closed form")
    check(t * t - 4 * q == DK * ff * ff, f"{name} identity")
    if typ == "FactoredCert":
        facs = pyval(f["factors"])
        small = pyval(f["smallPrimes"])
        large = pyval(f["largePrimes"])
        jfac = [(int(p), e) for p, e in ex["factorization"]]
        check(facs == jfac, f"{name} factors vs nist.json")
        cert = FAC_BY_N.get(4 * q - t * t)
        if cert is None:
            fails.append(f"{name} no factorizations.jsonl record")
        else:
            check([(int(p), e) for p, e in cert["factors"]] == jfac, f"{name} factors vs factorizations.jsonl")
        prod = 1
        for p, e in facs:
            prod *= p ** e
        check(prod == 4 * q - t * t, f"{name} product")
        odd = [p for p, e in facs if e % 2]
        check([p for p, _ in small] + large == odd, f"{name} odd split")
        check(all(p < 10 ** 8 for p, _ in small), f"{name} small < 1e8")
        check(all(p > 10 ** 8 for p in large), f"{name} large > 1e8")
        check(all(r * r > p for p, r in small), f"{name} r^2 > p")
        for p, _ in facs:
            check(isprime(p), f"{name} factor {p} prime (PARI)")
        largeprimes_all.update(large)
        # nist.exact_discriminant
        core, fpy = 1, 1
        for p, e in facs:
            fpy *= p ** (e // 2)
            if e % 2:
                core *= p
        if (-core) % 4 == 1:
            DKpy = -core
        else:
            DKpy, fpy = -4 * core, fpy // 2
        check((DKpy, fpy) == (DK, ff), f"{name} exact_discriminant recompute")
        print(f"  {name}: q,t,D_K,f,deg,factors match; {len(large)} large primes PARI-prime; D_K bits {abs(DK).bit_length()}")
    else:
        check(ex["D_K"] == -7, f"{name} scan D_K")
        m = q.bit_length() - 1
        check(q == 2 ** m, f"{name} q = 2^m")
        print(f"  {name}: q = 2^{m}, t, f match nist.json; identity holds")

# finding3 numeric re-check
print("== finding 3 numbers")
for name, (typ, f) in blocks.items():
    if typ != "FactoredCert":
        continue
    q, DK, deg = pyval(f["q"]), pyval(f["DK"]), pyval(f["deg"])
    print(f"  {name}: log2|DK|={abs(DK).bit_length()-1}.., log2 deg ~ {deg.bit_length()-1}, q>=2^223: {q >= 2**223}, deg>=2^220: {deg >= 2**220}")
    check(2 ** 162 <= abs(DK) < 2 ** 523, f"{name} DK range")
    check(deg >= 2 ** 160, f"{name} deg >= 2^160")
    if q >= 2 ** 223:
        check(deg >= 2 ** 220, f"{name} deg>=2^220")

# ----------------------------------------------------------------- B-571
print("== B-571")
J = NIST["nist/B-571"]
gv = lambda nm: pyval(re.search(rf"def {nm} : \w+ := (.*)", src).group(1))
q, t, P, C, rootC, B = gv("q"), gv("t"), gv("P"), gv("C"), gv("rootC"), gv("B")
kp = pyval(re.search(r"def knownPrimes : List Nat := (.*)", src).group(1))
absDK, degAL = gv("absDKAtLeast"), gv("degAtLeast")
check(q == J["q"] and q == 2 ** 571, "B571 q")
check(t == J["t"], "B571 t")
check(J["exact"] is None, "B571 exact None")
bd = J["bound"]
check(absDK == bd["abs_D_K_at_least"], "B571 absDK vs json")
check(degAL == bd["min_nonscalar_degree_at_least"], "B571 deg vs json")
cert = FAC_BY_N[4 * q - t * t]
check([(int(p), e) for p, e in cert["partial_factors"]] == [(p, 1) for p in kp], "B571 partial factors vs jsonl")
check(int(cert["cofactor"]) == C, "B571 cofactor vs jsonl")
pp = 1
for p in kp:
    pp *= p
check(pp == P and P * C == 4 * q - t * t, "B571 product")
check(gcd(P, C) == 1, "B571 gcd")
check(len(str(C)) == 130, "B571 digits")
check(isqrt(C) == rootC and rootC * rootC != C, "B571 not square")
for p in kp:
    check(isprime(p), f"B571 known prime {p} (PARI)")
check(not isprime(C), "B571 C composite")
# hypothesis (ii): no divisor 1<d<10^7 <=> no prime factor below 10^7
from sympy import primerange
small_div = [p for p in primerange(2, B) if C % p == 0]
check(small_div == [], f"B571 C has small prime factor {small_div[:5]}")
print(f"  C trial division by all primes < {B}: {len(small_div)} divisors -> hypothesis (ii) TRUE")
print(f"  P*B = {P*B}, json {bd['abs_D_K_at_least']}, log2 = {(P*B).bit_length()-1}..; deg_at_least/4 relation: {P*B == 4*degAL}")
print("  json how:", bd["how"])

# ----------------------------------------------------------------- Koblitz
print("== Koblitz KCert")
kb, ksrc = lean_blocks(ROOT + "/formal/CryptoResearch/Endosweep/Koblitz.lean")
# Published FIPS 186-4 / SEC 2 orders (hex) for cross-check, independent of the Lean file
PUB_N = {
    "K163": (0x4000000000000000000020108A2E0CC0D99F8A5EF, 2, 1),
    "K233": (0x8000000000000000000000000000069D5BB915BCD46EFB1AD5F173ABDF, 4, 0),
    "K283": (int("01FFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFE9AE 2ED07577 265DFF7F 94451E06 1E163C61".replace(" ", ""), 16), 4, 0),  # FIPS 186-4 D.1.3.2.3 grouped form
    "K409": (int("7FFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFE5F83 B2D4EA20 400EC455 7D5ED3E3 E7CA5B4B 5C83B8E0 1E5FCF".replace(" ", ""), 16), 4, 0),  # FIPS 186-4 grouped form
    "K571": (0x20000000000000000000000000000000000000000000000000000000000000000000000131850E1F19A63E4B391A8DB917F4138B630D84BE5D639381E91DEB45CFE778F637C1001, 4, 0),
}


def zmul(mu, x, y):
    a, b = x
    c, d = y
    return (a * c - 2 * b * d, a * d + b * c + mu * b * d)


def znorm(mu, x):
    a, b = x
    return a * a + mu * a * b + 2 * b * b


def lucas(mu, m):
    v0, v1 = 2, mu
    for _ in range(m - 1):
        v0, v1 = v1, mu * v1 - 2 * v0
    return v1 if m >= 1 else v0


for name, (typ, f) in kb.items():
    if typ != "KCert":
        continue
    m, mu, n, h, t, ff, lam = (pyval(f[k]) for k in ("m", "μ", "n", "h", "t", "f", "lam"))
    delta = pyval(f["δ"])
    pn, ph, a = PUB_N[name]
    check(n == pn, f"{name} n vs published hex")
    check(h == ph, f"{name} h vs published")
    check(mu == (1 if a == 1 else -1), f"{name} mu vs curve a")
    J = NIST[name2key[name]]
    check(t == J["t"], f"{name} t vs json")
    check(ff == J["exact"]["f"], f"{name} f vs json")
    check(J["q"] == 2 ** m, f"{name} q=2^m json")
    check([str(delta[0]), str(delta[1])] == J["tau"]["delta"], f"{name} delta vs json")
    check(lam == int(J["tau"]["eigenvalue"], 16), f"{name} lam vs json")
    check(J["tau"]["mu"] == mu, f"{name} mu vs json")
    # recompute everything
    V = lucas(mu, m)
    check(h * n == 2 ** m + 1 - V, f"{name} hn")
    check(t == V, f"{name} t=V")
    tm = (1, 0)
    for _ in range(m):
        tm = zmul(mu, tm, (0, 1))
    check(zmul(mu, delta, (-1, 1)) == (tm[0] - 1, tm[1]), f"{name} delta*(tau-1)")
    check(znorm(mu, delta) == n, f"{name} N(delta)")
    check(ff == abs(tm[1]), f"{name} f=|B|")
    check(t * t - 4 * 2 ** m == -7 * ff * ff, f"{name} -7 f^2")
    check((lam * lam - mu * lam + 2) % n == 0, f"{name} lam root")
    check(isprime(n), f"{name} n prime")
    print(f"  {name}: n,h match published hex; t,f,delta,lam match nist.json; all identities recompute")

print()
print("FAILURES:", len(fails))
for x in fails:
    print("  ", x)
