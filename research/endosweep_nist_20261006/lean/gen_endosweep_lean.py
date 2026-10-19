#!/usr/bin/env python3
"""Generate the data blocks of the endosweep Lean certificates.

Reads (repository-relative, from REPO):
  research/endosweep_nist_20261006/nist.json
  research/endosweep_nist_20261006/factorizations.jsonl
  std-curves nist/curves.json at the commit nist.json records (STD)
Writes:
  formal/CryptoResearch/Endosweep/NistCertificates.lean
  formal/CryptoResearch/Endosweep/Koblitz.lean   (template Koblitz.lean.in + data)

Every number is re-derived and cross-checked here first, so a mismatch fails
the generator rather than producing a Lean file that fails to check.
"""
import json
import sys
from math import isqrt, prod
from pathlib import Path

REPO = Path(sys.argv[1])
STD = Path(sys.argv[2])
HERE = Path(__file__).resolve().parent

nist = json.load(open(REPO / "research/endosweep_nist_20261006/nist.json"))
assert nist["std_curves_commit"] == "77fe6e3585ca2c2225b59d7df24b7c775437276f"
curves = nist["curves"]
facs = {}
for line in open(REPO / "research/endosweep_nist_20261006/factorizations.jsonl"):
    r = json.loads(line)
    assert "factors" in r, "every certificate is complete (B-571's since 2026-10-16)"
    facs[int(r["N"])] = [(int(p), e) for p, e in r["factors"]]
std = {c["name"]: c for c in json.load(open(STD / "nist/curves.json"))["curves"]}

TRIAL = 10 ** 8   # odd-exponent primes below this are proved prime in Lean by trial division


def min_deg(D):
    return (abs(D) + D % 2) // 4


def lean_name(key):
    name = key.split("/")[1].replace("-", "")
    # `B571` is the namespace of the (superseded) bound theorem; the exact certificate is `B571Exact`.
    return "B571Exact" if name == "B571" else name


def zt(x):
    a, b = x
    return f"⟨{a}, {b}⟩"


# ---------------------------------------------------------------- exact certificates
factored, scanned = [], []
for key, v in curves.items():
    e = v.get("exact")
    if not e:
        continue
    q, t, DK, f, deg = v["q"], v["t"], e["D_K"], e["f"], e["min_nonscalar_degree"]
    assert t * t - 4 * q == DK * f * f, key
    assert min_deg(DK) == deg, key
    assert DK < 0 and DK % 4 in (0, 1)
    if "factorization" in e:
        fac = [(int(p), x) for p, x in e["factorization"]]
        N = 4 * q - t * t
        assert facs[N] == fac, key           # the certificate file and nist.json agree
        assert prod(p ** x for p, x in fac) == N
        odd = [p for p, x in fac if x % 2]
        assert odd == sorted(odd) and len(set(odd)) == len(odd)
        core = prod(odd)
        if (-core) % 4 == 1:
            assert DK == -core
            case = 1
        else:
            assert DK == -4 * core and (-core) % 4 in (2, 3)
            case = 4
        small = [(p, isqrt(p) + 1) for p in odd if p < TRIAL]
        large = [p for p in odd if p >= TRIAL]
        for p, r in small:
            assert p < r * r and all(p % d for d in range(2, r))
        factored.append(dict(key=key, name=lean_name(key), q=q, t=t, DK=DK, f=f, deg=deg,
                             fac=fac, small=small, large=large, dup=v.get("duplicate_of")))
    else:
        assert DK == -7 and e["how"].startswith("the scan")
        scanned.append(dict(key=key, name=lean_name(key), q=q, t=t, DK=DK, f=f, deg=deg))

# ---------------------------------------------------------------- B-571 (the superseded bound)
# The partial certificate of 2026-10-06..16 (four proven primes and a 130-digit composite cofactor C)
# is no longer in factorizations.jsonl: the complete certificate replaced it.  The bound theorem is kept,
# so its data are re-derived here from the complete certificate: the four primes found by trial division
# and ECM, and C = the product of the two primes CADO-NFS found.
b = curves["nist/B-571"]
N571 = 4 * b["q"] - b["t"] ** 2
assert b["exact"] and "factorization" in b["exact"] and not b.get("bound")
fac571 = facs[N571]
os571 = [137, 1502689, 5608493523058319, 3563521804312876303]   # the partial certificate's primes
assert all(x == 1 for _, x in fac571) and [p for p, _ in fac571[:4]] == os571
split571 = [p for p, _ in fac571[4:]]                              # p38, p93 (CADO-NFS)
assert [len(str(p)) for p in split571] == [38, 93]
C571 = prod(split571)
P571 = prod(os571)
assert P571 * C571 == N571
from math import gcd
assert gcd(P571, C571) == 1
r571 = isqrt(C571)
assert r571 * r571 < C571 < (r571 + 1) ** 2
assert 10 ** 129 <= C571 < 10 ** 130
B = 10 ** 7
assert all(p > B for p in split571)                                 # so C has no divisor in (1, 10^7)
lo = P571 * B
assert lo == 41144834294568711165300914428595243383362010000000     # the bound the old nist.json recorded
assert lo % 4 == 0 and 2 ** 164 < lo and 2 ** 162 < lo // 4
assert lo <= abs(b["exact"]["D_K"]) and lo // 4 <= b["exact"]["min_nonscalar_degree"]
small571 = [(p, isqrt(p) + 1) for p in os571 if p < TRIAL]
large571 = [p for p in os571 if p >= TRIAL]

# ---------------------------------------------------------------- Koblitz
def lucas(mu, m):
    v0, v1 = 2, mu
    for _ in range(m):
        v0, v1 = v1, mu * v1 - 2 * v0
    return v0


def zmul(mu, x, y):
    a, b_ = x
    c, d = y
    return (a * c - 2 * b_ * d, a * d + b_ * c + mu * b_ * d)


def zpow(mu, x, k):
    r = (1, 0)
    for _ in range(k):
        r = zmul(mu, r, x)
    return r


kcerts = []
for name in ("K-163", "K-233", "K-283", "K-409", "K-571"):
    v = curves["nist/" + name]
    s = std[name]
    m = int(v["field"].split("^")[1].split(",")[0])
    mu = 1 if v["a"] == 1 else -1
    n, h = int(s["order"], 16), int(s["cofactor"], 16)
    t, f = v["t"], v["exact"]["f"]
    delta = tuple(int(x) for x in v["tau"]["delta"])
    lam = int(v["tau"]["eigenvalue"], 16)
    assert v["q"] == 2 ** m
    assert h == 3 - mu and h * n == 2 ** m + 1 - lucas(mu, m) and t == lucas(mu, m)
    tm = zpow(mu, (0, 1), m)
    assert zmul(mu, delta, (-1, 1)) == (tm[0] - 1, tm[1])
    a_, b_ = delta
    assert a_ * a_ + mu * a_ * b_ + 2 * b_ * b_ == n
    assert f == abs(tm[1]) and t * t - 4 * 2 ** m == -7 * f * f
    assert (lam * lam - mu * lam + 2) % n == 0
    kcerts.append(dict(name=name.replace("-", ""), m=m, mu=mu, n=n, h=h, t=t, f=f, delta=delta, lam=lam))
# K-163 cross-check against tests/test_endosweep.py
assert kcerts[0]["n"] == 0x04000000000000000000020108A2E0CC0D99F8A5EF


# ---------------------------------------------------------------- emit NistCertificates.lean
def fac_lean(fac):
    return "[" + ", ".join(f"({p}, {x})" for p, x in fac) + "]"


def pr_lean(xs):
    return "[" + ", ".join(f"({p}, {r})" for p, r in xs) + "]"


def nl(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


L = []
for c in factored:
    dup = f" (same q and t as {c['dup']})" if c["dup"] else ""
    L.append(f"/-- {c['key']}{dup}: `D_K = {'−core' if c['DK'] % 4 == 1 else '−4·core'}`, `f = {c['f']}`. -/")
    L.append(f"def {c['name']} : FactoredCert where")
    L.append(f"  q := {c['q']}")
    L.append(f"  t := {c['t']}")
    L.append(f"  DK := {c['DK']}")
    L.append(f"  f := {c['f']}")
    L.append(f"  deg := {c['deg']}")
    L.append(f"  factors := {fac_lean(c['fac'])}")
    L.append(f"  smallPrimes := {pr_lean(c['small'])}")
    L.append(f"  largePrimes := {nl(c['large'])}")
    L.append("")
L.append("/-- Every curve whose `4q − t²` is completely factored (nist.json `exact.how`")
L.append("= \"complete factorisation of 4q - t^2 into primes\"). -/")
L.append("def factoredCerts : List FactoredCert :=")
L.append("  [" + ", ".join(c["name"] for c in factored) + "]")
L.append("")
for c in scanned:
    L.append(f"/-- {c['key']}: found by the scan, `t² − 4q = −7·f²`. -/")
    L.append(f"def {c['name']} : ScanCert where")
    L.append(f"  q := {c['q']}")
    L.append(f"  t := {c['t']}")
    L.append(f"  DK := {c['DK']}")
    L.append(f"  f := {c['f']}")
    L.append(f"  deg := {c['deg']}")
    L.append("")
L.append("/-- The Koblitz curves, whose `D_K = −7` the small-discriminant scan found. -/")
L.append("def scanCerts : List ScanCert :=")
L.append("  [" + ", ".join(c["name"] for c in scanned) + "]")
DATA_NIST = "\n".join(L)

DATA_B571 = f"""/-- B-571: `q = 2^571`. -/
def q : Int := {b['q']}
/-- B-571: the trace of Frobenius. -/
def t : Int := {b['t']}
/-- The four primes the partial certificate proved (PARI `isprime`), each to exponent 1. -/
def knownPrimes : List Nat := {nl(os571)}
/-- Their product. -/
def P : Nat := {P571}
/-- The 130-digit composite cofactor they left. -/
def C : Nat := {C571}
/-- The two primes CADO-NFS split `C` into (PARI `isprime` and ECPP; not proved in Lean). -/
def splitPrimes : List Nat := {nl(split571)}
/-- `⌊√C⌋`. -/
def rootC : Nat := {r571}
/-- The trial-division bound. -/
def B : Nat := {B}
/-- The bound the partial certificate gave (`= P·B`; nist.json `bound.abs_D_K_at_least` before 2026-10-16). -/
def absDKAtLeast : Nat := {lo}
/-- Its quarter (nist.json `bound.min_nonscalar_degree_at_least` before 2026-10-16). -/
def degAtLeast : Nat := {lo // 4}"""

DATA_B571_SMALL = pr_lean(small571)
DATA_B571_LARGE = nl(large571)

tmpl = (HERE / "NistCertificates.lean.in").read_text()
out = (tmpl.replace("@@DATA@@", DATA_NIST).replace("@@B571@@", DATA_B571)
       .replace("@@B571SMALL@@", DATA_B571_SMALL).replace("@@B571LARGE@@", DATA_B571_LARGE))
(REPO / "formal/CryptoResearch/Endosweep/NistCertificates.lean").write_text(out)

# ---------------------------------------------------------------- emit Koblitz.lean
K = []
for c in kcerts:
    K.append(f"/-- {c['name'][0]}-{c['name'][1:]}: `m = {c['m']}`, `μ = {c['mu']}`. -/")
    K.append(f"def {c['name']} : KCert where")
    K.append(f"  m := {c['m']}")
    K.append(f"  μ := {c['mu']}")
    K.append(f"  n := {c['n']}")
    K.append(f"  h := {c['h']}")
    K.append(f"  t := {c['t']}")
    K.append(f"  f := {c['f']}")
    K.append(f"  δ := {zt(c['delta'])}")
    K.append(f"  lam := {c['lam']}")
    K.append("")
K.append("/-- K-163, K-233, K-283, K-409, K-571. -/")
K.append("def koblitzCerts : List KCert := [" + ", ".join(c["name"] for c in kcerts) + "]")
K.append("")
K.append("/-- The closed arithmetic, checked by the kernel (GMP-backed `Nat`). -/")
K.append("theorem koblitz_holds : ∀ c ∈ koblitzCerts, c.Holds := by decide +kernel")
tmpl = (HERE / "Koblitz.lean.in").read_text()
(REPO / "formal/CryptoResearch/Endosweep/Koblitz.lean").write_text(tmpl.replace("@@DATA@@", "\n".join(K)))
print("factored:", [c["name"] for c in factored])
print("scanned:", [c["name"] for c in scanned])
print("koblitz:", [c["name"] for c in kcerts])
