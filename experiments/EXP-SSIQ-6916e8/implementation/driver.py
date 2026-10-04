#!/usr/bin/env python3
"""EXP-SSIQ-6916e8 driver (frozen specification v1, task TASK-20260926-7d20e4).

Executes the single deterministic run RUN-SSIQ-81bd08:

  phase P  prime search (PARI nextprime + proven isprime) for tiers M and L
  phase 1  per prime: PARI stage1 (algebra, C-ALG (a)/(b), structure constants,
           arm A1); Python arm A2 (hand-written order, evaluated entirely in
           Python in (1, i, j, k) coordinates); A1 C-ALG -> base-order rule
  gate     stopping rule: C-ALG (b) failure anywhere -> STOP, F-INSTR, no R
  phase 2  per prime: PARI stage2 (base, C-TRD, C-NONMAX, A3, C-NEAR, A4, A5,
           A6, PARI matdet of the A2 Grams)
  analysis independent Python instruments on every lattice (C-CROSS),
           C-ALG checks, R values, counts, frozen outcome codes

Exact arithmetic only: every pass/fail decision uses fractions.Fraction or
Python int. The only floats are the M-EXP "report_only" renderings and
timings, which never enter a decision.

No curve, isogeny, key or attack is constructed (handoff C-4).
"""

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
from fractions import Fraction

EXPERIMENT_ID = "EXP-SSIQ-6916e8"
SPEC_VERSION = 1
BASE_SEED = 20260926
TIER_S = [2, 3, 5, 7, 11, 13, 17, 19, 23, 101, 103, 109, 113]
M_LIST = [2, 3, 4, 5, 6, 8, 12, 30, 97, 1024]
WATCHDOG_SECONDS = 3600
WATCHDOG_MARGIN = 60          # internal deadline = watchdog - margin
MEMORY_CAP_BYTES = 4 * 1024 ** 3
GP_BIN = "/usr/bin/gp"
GP_PARISIZEMAX = "1G"
A4_MAX_ATTEMPTS = 1000000
HERE = os.path.dirname(os.path.abspath(__file__))
GP_FILE = os.path.join(HERE, "build_lattices.gp")
EXP_DIR = os.path.dirname(HERE)


class InfraError(Exception):
    """Timeout / crash / watchdog: F-INFRA, never evidence."""


# ----------------------------------------------------------------- exact linear algebra
def F(s):
    return Fraction(s)


def fstr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def det(M):
    """Exact determinant by Fraction Gaussian elimination (instrument D-PY)."""
    n = len(M)
    A = [[Fraction(v) for v in row] for row in M]
    d = Fraction(1)
    for c in range(n):
        piv = None
        for r in range(c, n):
            if A[r][c] != 0:
                piv = r
                break
        if piv is None:
            return Fraction(0)
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            d = -d
        d *= A[c][c]
        for r in range(c + 1, n):
            if A[r][c] != 0:
                f = A[r][c] / A[c][c]
                for k in range(c, n):
                    A[r][k] -= f * A[c][k]
    return d


def inv(M):
    n = len(M)
    A = [[Fraction(v) for v in row] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [row[n:] for row in A]


def matvec(M, v):
    return [sum(M[r][c] * v[c] for c in range(len(v))) for r in range(len(M))]


def cols_to_mat(cols):
    """list of column vectors -> matrix (rows)."""
    return [[cols[j][i] for j in range(len(cols))] for i in range(len(cols[0]))]


def is_int(x):
    return Fraction(x).denominator == 1


def isqrt_exact(x):
    """Exact nonnegative square root of a nonnegative rational, or None."""
    x = Fraction(x)
    if x < 0:
        return None
    a, b = math.isqrt(x.numerator), math.isqrt(x.denominator)
    if a * a == x.numerator and b * b == x.denominator:
        return Fraction(a, b)
    return None


def gcd_frac(vals):
    """gcd of rationals (as the generator of the Z-module they span)."""
    g = Fraction(0)
    for v in vals:
        v = Fraction(v)
        if g == 0:
            g = abs(v)
        elif v != 0:
            num = math.gcd(g.numerator * v.denominator, v.numerator * g.denominator)
            g = Fraction(num, g.denominator * v.denominator)
    return g


# ----------------------------------------------------------------- seeds
def derive_seed(arm, p, index):
    """seed = first 16 hex digits of sha256("<base_seed>:<arm>:<p>:<index>")."""
    h = hashlib.sha256(("%d:%s:%d:%d" % (BASE_SEED, arm, p, index)).encode()).hexdigest()
    return int(h[:16], 16)


# ----------------------------------------------------------------- prime data
def pclass(p):
    if p == 2:
        return "2"
    if p % 4 == 3:
        return "3mod4"
    if p % 8 == 5:
        return "5mod8"
    return "1mod8"


def small_primes_upto(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i, v in enumerate(s) if v]


SMALL_PRIMES = small_primes_upto(10000)


def legendre(p, q):
    """Legendre symbol (p/q) for an odd prime q (Euler's criterion, exact ints)."""
    r = pow(p % q, (q - 1) // 2, q)
    return -1 if r == q - 1 else r


def presentation(p):
    """Frozen algebra presentation (a, b) and auxiliary q, c."""
    if p == 2:
        return {"a": -1, "b": -1, "q": None, "c": None}
    if p % 4 == 3:
        return {"a": -1, "b": -p, "q": None, "c": None}
    if p % 8 == 5:
        return {"a": -2, "b": -p, "q": None, "c": None}
    q = next(q for q in SMALL_PRIMES if q % 4 == 3 and legendre(p, q) == -1)
    c = next(c for c in range(q) if (c * c * p + 1) % q == 0)
    return {"a": -q, "b": -p, "q": q, "c": c}


def target_norms(p):
    ls = [l for l in SMALL_PRIMES if l != p][:3]
    l1, l2, l3 = ls
    Ns = [l1 ** k for k in range(1, 9)] + [l2 ** k for k in range(1, 7)] + \
         [l1 * l2, l1 ** 2 * l2, l1 * l2 ** 2, l1 ** 3 * l2 ** 3, l3, l1 * l3]
    return ls, Ns


def factor_small(m):
    out = []
    for l in SMALL_PRIMES:
        while m % l == 0:
            out.append(l)
            m //= l
    assert m == 1
    return out


def make_H(p, k, m):
    """Seeded random 4x4 upper-triangular integer matrix, positive diagonal of
    product m, off-diagonal H[i][j] (i < j) in [0, H[j][j]) -- the frozen
    wording "diagonal entry of their column". Returned as rows."""
    seed = derive_seed("A6", p, k)
    rng = random.Random(seed)
    diag = [1, 1, 1, 1]
    for l in factor_small(m):
        diag[rng.randrange(4)] *= l
    H = [[0] * 4 for _ in range(4)]
    for j in range(4):
        H[j][j] = diag[j]
        for i in range(j):
            H[i][j] = rng.randrange(diag[j])
    return seed, H


# ----------------------------------------------------------------- arm A2 (pure Python)
def qmul(a, b, x, y):
    x0, x1, x2, x3 = x
    y0, y1, y2, y3 = y
    return [x0 * y0 + a * x1 * y1 + b * x2 * y2 - a * b * x3 * y3,
            x0 * y1 + x1 * y0 - b * x2 * y3 + b * x3 * y2,
            x0 * y2 + x2 * y0 + a * x1 * y3 - a * x3 * y1,
            x0 * y3 + x3 * y0 + x1 * y2 - x2 * y1]


def qnrd(a, b, x):
    return x[0] ** 2 - a * x[1] ** 2 - b * x[2] ** 2 + a * b * x[3] ** 2


def a2_basis(p, pres):
    h, q4 = Fraction(1, 2), Fraction(1, 4)
    if p == 2:
        return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [h, h, h, h]]
    if p % 4 == 3:
        return [[1, 0, 0, 0], [0, 1, 0, 0], [h, 0, h, 0], [0, h, 0, h]]
    if p % 8 == 5:
        return [[1, 0, 0, 0], [h, 0, h, h], [0, q4, 2 * q4, q4], [0, 0, 0, 1]]
    q, c = pres["q"], pres["c"]
    return [[h, h, 0, 0], [0, 0, h, h], [0, Fraction(1, q), 0, Fraction(c, q)], [0, 0, 0, 1]]


def gram_from_q(qf, basis):
    n = len(basis)
    qs = [qf(v) for v in basis]
    A = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = Fraction(qs[i])
        for j in range(i + 1, n):
            s = [u + v for u, v in zip(basis[i], basis[j])]
            A[i][j] = A[j][i] = Fraction(qf(s) - qs[i] - qs[j], 2)
    return A


def analyse_a2(p, pres):
    a, b = pres["a"], pres["b"]
    basis = [[Fraction(v) for v in e] for e in a2_basis(p, pres)]
    M = cols_to_mat(basis)
    Minv = inv(M)
    inspan = lambda y: all(is_int(c) for c in matvec(Minv, y))
    contains_one = inspan([1, 0, 0, 0])
    closed = all(inspan(qmul(a, b, x, y)) for x in basis for y in basis)
    nrd_int = all(is_int(qnrd(a, b, x)) for x in basis)
    trd_int = all(is_int(2 * x[0]) for x in basis)
    G = gram_from_q(lambda v: qnrd(a, b, v), basis)
    return {"basis": basis, "gram": G, "calg": {"c_contains_one": contains_one, "c_closed": closed,
                                                 "c_nrd_integral": nrd_int, "c_trd_integral": trd_int}}


# ----------------------------------------------------------------- PARI-side instruments in Python
class Alg:
    """Structure constants exported by PARI; Python-side left-regular
    representation instrument (C-CROSS (ii))."""

    def __init__(self, multable, one):
        # multable[i] = matrix (rows) of left multiplication by e_i
        self.MT = [[[F(v) for v in row] for row in m] for m in multable]
        self.one = [F(v) for v in one]

    def L(self, x):
        return [[sum(x[i] * self.MT[i][r][c] for i in range(4)) for c in range(4)] for r in range(4)]

    def mul(self, x, y):
        return matvec(self.L(x), y)

    def trd(self, x):
        Lx = self.L(x)
        return sum(Lx[i][i] for i in range(4)) / 2

    def nrd(self, x):
        """Nrd(x) = + sqrt(det L_x); None if det L_x is not a rational square."""
        return isqrt_exact(det(self.L(x)))

    def gram(self, basis):
        n = len(basis)
        qs = [self.nrd(v) for v in basis]
        if any(q is None for q in qs):
            return None
        A = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            A[i][i] = qs[i]
            for j in range(i + 1, n):
                qij = self.nrd([u + v for u, v in zip(basis[i], basis[j])])
                if qij is None:
                    return None
                A[i][j] = A[j][i] = (qij - qs[i] - qs[j]) / 2
        return A


def span_checker(basis):
    Minv = inv(cols_to_mat(basis))
    return lambda y: all(is_int(c) for c in matvec(Minv, y))


def order_checks(alg, basis):
    inspan = span_checker(basis)
    return {"c_contains_one": inspan(alg.one),
            "c_closed": all(inspan(alg.mul(x, y)) for x in basis for y in basis),
            "c_nrd_integral": all(alg.nrd(x) is not None and is_int(alg.nrd(x)) for x in basis),
            "c_trd_integral": all(is_int(alg.trd(x)) for x in basis)}


def run_gp(script, timeout):
    """Run gp on a script; returns (records, stderr, rc, seconds)."""
    t0 = time.time()
    try:
        cp = subprocess.run([GP_BIN, "-q", "-D", "parisizemax=%s" % GP_PARISIZEMAX],
                            input=script, capture_output=True, text=True, timeout=timeout, cwd=HERE)
    except subprocess.TimeoutExpired:
        raise InfraError("gp call exceeded its watchdog share (%.0f s)" % timeout)
    recs = [json.loads(l[len("@@JSON "):]) for l in cp.stdout.splitlines() if l.startswith("@@JSON ")]
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return recs, cp.stderr, cp.returncode, time.time() - t0


def gp_mat(rows):
    return "[" + ";".join(",".join(fstr(v) for v in row) for row in rows) + "]"


def gp_vec(v):
    return "[" + ",".join(fstr(x) for x in v) + "]"


# ----------------------------------------------------------------- environment
def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=EXP_DIR).stdout
    except Exception as e:  # recorded, not hidden
        return "ERROR: %r" % (e,)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def capture_environment():
    import numpy
    import sympy
    env = {
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "numpy_version": numpy.__version__,
        "sympy_version": sympy.__version__,
        "numpy_used_in_computation": False,
        "sympy_used_in_driver": False,
        "sympy_used_in_check": True,
        "gp_binary": GP_BIN,
        "gp_binary_realpath": os.path.realpath(GP_BIN),
        "gp_version_short": sh([GP_BIN, "--version-short"]).strip(),
        "gp_version_full": sh([GP_BIN, "--version"]).strip() + sh([GP_BIN, "-q", "--version"]).strip(),
        "gp_sha256": sha256_file(GP_BIN),
        "gp_parisizemax": GP_PARISIZEMAX,
        "os_cpu_count": os.cpu_count(),
        "sched_getaffinity": len(os.sched_getaffinity(0)),
        "loadavg": os.getloadavg(),
        "workers_used": 1,
        "memory_cap_bytes_rlimit_as": MEMORY_CAP_BYTES,
        "git_head": sh(["git", "rev-parse", "HEAD"]).strip(),
        "git_branch": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip(),
        "git_status_porcelain": sh(["git", "status", "--porcelain", "--untracked-files=all"]),
        "implementation_sha256": {n: sha256_file(os.path.join(HERE, n))
                                  for n in sorted(os.listdir(HERE)) if os.path.isfile(os.path.join(HERE, n))},
        "specification_sha256": sha256_file(os.path.join(EXP_DIR, "specification.yaml")),
    }
    env["git_dirty"] = bool(env["git_status_porcelain"].strip())
    return env


# ----------------------------------------------------------------- lattice analysis
def analyse_pari_lattice(rec, alg, p):
    """Independent Python instruments on a PARI-side lattice record."""
    out = {"ccross": {}, "notes": []}
    basis = [[F(v) for v in col] for col in rec["basis"]]
    s = F(rec.get("form_scale", "1"))
    gram = [[F(v) for v in row] for row in rec["gram"]]
    out["basis_f"] = basis
    out["gram_nrd_unscaled_str"] = rec.get("gram_nrd_unscaled")
    out["det_pari"] = F(rec["det_pari"])
    out["det_python"] = det(gram)
    out["ccross"]["i_det_agree"] = out["det_pari"] == out["det_python"]
    if "gram_nrd_unscaled" in rec:
        gu = [[F(v) for v in row] for row in rec["gram_nrd_unscaled"]]
        gr = alg.gram(basis)
        out["gram_regrep_unscaled"] = gr
        out["ccross"]["ii_nrd_gram_agree"] = gr is not None and gr == gu
        out["ccross"]["scaling_consistent"] = [[v / s for v in row] for row in gu] == gram
        out["det_pari_unscaled"] = F(rec["det_pari_unscaled"])
        out["det_python_unscaled"] = det(gu)
        out["ccross"]["i_det_unscaled_agree"] = out["det_pari_unscaled"] == out["det_python_unscaled"]
        out["n_python"] = gcd_frac([gu[i][i] for i in range(len(gu))] +
                                   [2 * gu[i][j] for i in range(len(gu)) for j in range(i + 1, len(gu))])
    out["ccross_pass"] = all(out["ccross"].values())
    out["R"] = out["det_pari"] * 16 / (p * p) if out["ccross"]["i_det_agree"] else None
    return out


def summarize_bool(d):
    return all(v is True for v in d.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--dev-primes", default=None,
                    help="DEVELOPMENT ONLY: comma-separated primes OUTSIDE the frozen set; skips the prime search. "
                         "Never used for the recorded run.")
    args = ap.parse_args()
    dev = [int(x) for x in args.dev_primes.split(",")] if args.dev_primes else None
    if dev:
        assert not set(dev) & set(TIER_S), "dev primes must lie outside the frozen tier S list"
        assert all(p < 2 ** 63 or p > 2 ** 64 for p in dev) and all(p < 2 ** 255 for p in dev)
    t_start = time.time()
    deadline = t_start + WATCHDOG_SECONDS - WATCHDOG_MARGIN
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_CAP_BYTES, MEMORY_CAP_BYTES))
    run_dir = os.path.abspath(args.run_dir)
    os.makedirs(run_dir, exist_ok=True)
    for fn in ("raw-result.json", "environment.json"):
        if os.path.exists(os.path.join(run_dir, fn)):
            sys.exit("refusing to overwrite existing %s (run records are immutable)" % fn)

    env = capture_environment()
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=1, sort_keys=True)
    print("[env] git_head=%s dirty=%s gp=%s" % (env["git_head"], env["git_dirty"], env["gp_version_short"]), flush=True)

    raw = {"experiment_id": EXPERIMENT_ID, "spec_version": SPEC_VERSION, "run_id": args.run_id,
           "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
           "base_seed": BASE_SEED,
           "seed_derivation": ("seed(arm, p, index) = int(sha256('%d:<arm>:<p>:<index>').hexdigest()[:16], 16); "
                               "A4: PARI setrand(seed('A4', p, k)) k=1..20 before the alpha search; "
                               "A6: Python random.Random(seed('A6', p, k)) k=0..21 for the diagonal split and "
                               "off-diagonal entries; PARI setrand(1) immediately before every alginit call "
                               "(alginit's internal randomness, if any, is thereby fixed)." % BASE_SEED),
           "m_list": M_LIST, "a4_max_attempts": A4_MAX_ATTEMPTS,
           "gp_calls": [], "primes": [], "lattices": [], "controls": [], "prime_status": {},
           "status": "running", "infra_error": None}
    gp_head = 'read("%s");\n' % GP_FILE

    def remaining():
        r = deadline - time.time()
        if r <= 5:
            raise InfraError("internal watchdog deadline reached")
        return r

    def gp_call(label, script):
        recs, err, rc, secs = run_gp(gp_head + script, remaining())
        raw["gp_calls"].append({"label": label, "script": script, "returncode": rc,
                                "seconds": round(secs, 3), "stderr": err, "n_records": len(recs)})
        return recs

    try:
        # -------------------------------------------------- phase P: primes
        cls_map = {"1": "3mod4", "2": "5mod8", "3": "1mod8"}
        if dev:
            raw["DEVELOPMENT_MODE"] = "NOT A RUN RECORD: dev primes %s" % dev
            plist = [{"p": p, "tier": "DEV", "class": pclass(p), "isprime_proven": None} for p in dev]
            recs = [{"primes": []}]
        else:
            recs = gp_call("primes", "emit_primes();\n")
            if not recs:
                raise InfraError("prime search produced no output")
            plist = [{"p": p, "tier": "S", "class": pclass(p), "isprime_proven": None,
                      "isprime_note": "tier S frozen literal list"} for p in TIER_S]
        for r in recs[0]["primes"]:
            p = int(r["p"])
            plist.append({"p": p, "tier": r["tier"], "class": cls_map[str(r["class"])],
                          "isprime_proven": int(r["isprime_proven"]), "class_check": pclass(p) == cls_map[str(r["class"])]})
        for e in plist:
            e["presentation"] = presentation(e["p"])
            e["l123"], e["target_norms"] = target_norms(e["p"])
        raw["primes"] = [{**e, "p": str(e["p"])} for e in plist]
        print("[primes] %d primes: %s" % (len(plist), [(e["tier"], e["class"]) for e in plist]), flush=True)

        # -------------------------------------------------- phase 1
        S1 = {}
        for e in plist:
            p, pres = e["p"], e["presentation"]
            r = gp_call("stage1 p=%d" % p, "stage1(%d, %d, %d);\n" % (p, pres["a"], pres["b"]))
            S1[p] = r[0] if r else {"error": "no output from stage1"}
            st = raw["prime_status"].setdefault(str(p), {})
            st["stage1_error"] = S1[p].get("error")
            if S1[p].get("error"):
                continue
            s1 = S1[p]
            fin = [int(x) for x in s1["ramified_finite"]]
            hil = {h["place"]: int(h["symbol"]) for h in s1["hilbert"]}
            hil_ok = all((v == -1) == (k in (str(p), "inf")) for k, v in hil.items()) and hil.get("inf") == -1 \
                and hil.get(str(p)) == -1
            st["calg_a"] = {"ramified_finite": fin, "ramified_infinite_count": s1["ramified_infinite_count"],
                            "algramifiedplaces_ok": fin == [p] and s1["ramified_infinite_count"] == 1,
                            "hilbert": hil, "hilbert_ok": hil_ok}
            st["calg_a_pass"] = st["calg_a"]["algramifiedplaces_ok"] and hil_ok
            st["calg_b"] = {"nrd_one": s1["nrd_one"], "nrd_two": s1["nrd_two"],
                            "pass": F(s1["nrd_one"]) == 1 and F(s1["nrd_two"]) == 4}
            st["multable_stage1"] = s1["multable"]
            st["one_stage1"] = s1["one"]
            st["algmul_products_stage1"] = s1["algmul_products"]
            st["algbasis_natural"] = s1["algbasis_natural"]
            st["splitting_pol"] = s1["splitting_pol"]
            st["ijk_images"] = [s1["i_image"], s1["j_image"], s1["k_image"]]
            st["stage1_gp_ms"] = s1["ms"]
            alg = Alg(s1["multable"], s1["one"])
            # structure constants reproduce algmul on all 16 basis products
            prods = s1["algmul_products"]
            sc_ok = all([alg.MT[i][r_][j] for r_ in range(4)] == [F(v) for v in prods[4 * i + j]]
                        for i in range(4) for j in range(4))
            st["structure_constants_reproduce_algmul"] = sc_ok
            st["ijk_relations_ok"] = s1["ijk_relations_ok"]
            S1[p]["_alg"] = alg

        # stopping rule: C-ALG (b) failure anywhere -> STOP before any R
        bfail = [p for p in S1 if not S1[p].get("error") and not raw["prime_status"][str(p)]["calg_b"]["pass"]]
        if bfail:
            raw["status"] = "stopped_calg_b"
            raw["stop_reason"] = "C-ALG (b) failed at primes %s: reduced-norm instrument wrong; no R computed" % bfail
            raise StopIteration

        # arms A1 (analysis) and A2, base-order rule
        A2 = {}
        for e in plist:
            p, pres = e["p"], e["presentation"]
            st = raw["prime_status"][str(p)]
            A2[p] = analyse_a2(p, pres)
            if S1[p].get("error"):
                st["base"] = "none"
                continue
            alg = S1[p]["_alg"]
            a1 = S1[p]["A1"]
            an = analyse_pari_lattice(a1, alg, p)
            calg = order_checks(alg, an["basis_f"])
            calg["a_ramification"] = st["calg_a_pass"]
            calg["structure_constants"] = st["structure_constants_reproduce_algmul"]
            S1[p]["_A1"] = (an, calg)
            if summarize_bool(calg):
                st["base"] = "A1"
                st["base_basis"] = [[1 if i == j else 0 for i in range(4)] for j in range(4)]
            elif st["ijk_relations_ok"] and st["calg_a_pass"]:
                st["base"] = "A2_fallback"
                im = [alg.one, [F(v) for v in S1[p]["i_image"]], [F(v) for v in S1[p]["j_image"]],
                      [F(v) for v in S1[p]["k_image"]]]
                st["base_basis"] = [[sum(x[t] * im[t][r_] for t in range(4)) for r_ in range(4)] for x in A2[p]["basis"]]
            else:
                st["base"] = "none"
            st["fallback_used"] = st["base"] == "A2_fallback"

        # -------------------------------------------------- phase 2
        S2 = {}
        for e in plist:
            p, pres = e["p"], e["presentation"]
            st = raw["prime_status"][str(p)]
            Ns = e["target_norms"]
            seeds = [derive_seed("A4", p, k) for k in range(1, 21)]
            Hinfo = [make_H(p, k, M_LIST[k % 10]) for k in range(22)]
            st["a4_seeds"] = [str(s) for s in seeds]
            st["a6_seeds"] = [str(h[0]) for h in Hinfo]
            extra = [A2[p]["gram"]]
            if st["base"] == "none":
                r = gp_call("dets_only p=%d" % p, "print(\"@@JSON \", jobj([jkv(\"stage\", jq(\"dets\")), "
                            "jkv(\"extra_dets_pari\", jlist(apply(G->jr(matdet(G)), [%s])))]));\n"
                            % ",".join(gp_mat(G) for G in extra))
                S2[p] = {"error": "no valid base order", "extra_dets_pari": r[0]["extra_dets_pari"] if r else None}
                continue
            B = cols_to_mat(st["base_basis"])
            script = "stage2(%d, %d, %d, %s, %s, %s, [%s], [%s], %d);\n" % (
                p, pres["a"], pres["b"], gp_mat(B), gp_vec(Ns), gp_vec(seeds),
                ",".join(gp_mat(h[1]) for h in Hinfo), ",".join(gp_mat(G) for G in extra), A4_MAX_ATTEMPTS)
            r = gp_call("stage2 p=%d" % p, script)
            S2[p] = r[0] if r else {"error": "no output from stage2"}
            S2[p]["_H"] = Hinfo
            st["stage2_error"] = S2[p].get("error")
            print("[stage2] p=%s (%s, %s) base=%s gp_ms=%s" % (p if p < 10 ** 6 else "~2^%d" % p.bit_length(),
                  e["tier"], e["class"], st["base"], S2[p].get("ms")), flush=True)

        # -------------------------------------------------- analysis
        for e in plist:
            analyse_prime(e, S1, S2, A2, raw)
        raw["status"] = "completed"
    except StopIteration:
        pass
    except (InfraError, MemoryError, subprocess.SubprocessError, OSError) as ex:
        raw["status"] = "infra_failure"
        raw["infra_error"] = repr(ex)
        print("[infra] %r" % (ex,), file=sys.stderr, flush=True)

    raw["counts"], raw["outcome"] = tally(raw, os.path.join(EXP_DIR, "derivation-note.md"))
    t_end = time.time()
    ru_self = resource.getrusage(resource.RUSAGE_SELF)
    ru_ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    raw["resources"] = {"wall_seconds": round(t_end - t_start, 3),
                        "peak_rss_kib_driver": ru_self.ru_maxrss,
                        "peak_rss_kib_largest_gp_child": ru_ch.ru_maxrss,
                        "cpu_user_seconds_driver": ru_self.ru_utime, "cpu_sys_seconds_driver": ru_self.ru_stime,
                        "cpu_user_seconds_children": ru_ch.ru_utime, "cpu_sys_seconds_children": ru_ch.ru_stime,
                        "gp_parisizemax": GP_PARISIZEMAX, "memory_cap_bytes_rlimit_as": MEMORY_CAP_BYTES,
                        "watchdog_seconds": WATCHDOG_SECONDS, "internal_deadline_seconds": WATCHDOG_SECONDS - WATCHDOG_MARGIN}
    raw["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_end))
    with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
        json.dump(raw, f, indent=None, separators=(",", ":"), default=fstr)
    print("[done] status=%s outcome=%s triggered=%s" % (raw["status"], raw["outcome"]["primary_code"],
                                                        raw["outcome"]["triggered_codes"]), flush=True)
    print("[counts] " + json.dumps(raw["counts"]["summary"], sort_keys=True), flush=True)
    print("[resources] " + json.dumps(raw["resources"], sort_keys=True), flush=True)
    return 0 if raw["status"] in ("completed", "stopped_calg_b") else 3


# ----------------------------------------------------------------- per-prime analysis
def lat_entry(p, e, name, arm, idx, coord, basis, scale, gram, extra=None):
    d = {"id": "%s:%s" % (p, name), "p": str(p), "tier": e["tier"], "class": e["class"], "arm": arm,
         "name": name, "idx": idx, "coord_system": coord,
         "basis": [[fstr(v) for v in col] for col in basis] if basis is not None else None,
         "form_scale": fstr(scale) if scale is not None else None,
         "gram": [[fstr(v) for v in row] for row in gram] if gram is not None else None}
    if extra:
        d.update(extra)
    return d


def finish(entry, an, calg, p):
    if an.get("gram_nrd_unscaled_str") is not None:
        entry["gram_nrd_unscaled"] = an["gram_nrd_unscaled_str"]
        entry["det_pari_unscaled"] = fstr(an["det_pari_unscaled"])
        entry["det_python_unscaled"] = fstr(an["det_python_unscaled"])
        entry["n_measured_python"] = fstr(an["n_python"])
    if an.get("gram_regrep_unscaled") is not None:
        entry["gram_regrep_unscaled"] = [[fstr(v) for v in row] for row in an["gram_regrep_unscaled"]]
    entry["det_pari"] = fstr(an["det_pari"])
    entry["det_python"] = fstr(an["det_python"])
    entry["ccross"] = an["ccross"]
    entry["ccross_pass"] = an["ccross_pass"]
    entry["calg"] = calg
    entry["calg_pass"] = summarize_bool(calg)
    entry["R"] = fstr(an["R"]) if an["R"] is not None else None
    reasons = []
    if not entry["calg_pass"]:
        reasons.append("C-ALG: " + ",".join(k for k, v in calg.items() if v is not True))
    if not entry["ccross_pass"]:
        reasons.append("C-CROSS: " + ",".join(k for k, v in an["ccross"].items() if v is not True))
    entry["valid"] = not reasons
    entry["exclusion_reasons"] = reasons
    return entry


def analyse_prime(e, S1, S2, A2, raw):
    p = e["p"]
    st = raw["prime_status"][str(p)]
    L = raw["lattices"]
    ctrl = {"p": str(p), "tier": e["tier"], "class": e["class"]}
    raw["controls"].append(ctrl)
    s2 = S2.get(p, {})
    # ---- A2 (Python-only construction; PARI matdet via extra_dets_pari)
    a2 = A2[p]
    det_py = det(a2["gram"])
    xd = s2.get("extra_dets_pari")
    det_pari = F(xd[0]) if xd else None
    ent = lat_entry(p, e, "A2", "A2", None, "ijk", a2["basis"], 1, a2["gram"],
                    {"presentation": {k: v for k, v in e["presentation"].items()}})
    an = {"det_pari": det_pari, "det_python": det_py,
          "ccross": {"i_det_agree": det_pari is not None and det_pari == det_py}}
    an["ccross_pass"] = an["ccross"]["i_det_agree"]
    an["R"] = det_py * 16 / (p * p) if an["ccross_pass"] else None
    ent["det_pari"] = fstr(det_pari) if det_pari is not None else None
    ent["det_python"] = fstr(det_py)
    ent["ccross"], ent["ccross_pass"] = an["ccross"], an["ccross_pass"]
    ent["calg"] = dict(a2["calg"])
    ent["calg_pass"] = summarize_bool(ent["calg"])
    ent["R"] = fstr(an["R"]) if an["R"] is not None else None
    reasons = []
    if not ent["calg_pass"]:
        reasons.append("C-ALG: " + ",".join(k for k, v in ent["calg"].items() if v is not True))
    if not ent["ccross_pass"]:
        reasons.append("C-CROSS: i_det_agree")
    ent["valid"], ent["exclusion_reasons"] = not reasons, reasons
    L.append(ent)

    def missing(name, arm, idx, why):
        L.append({"id": "%s:%s" % (p, name), "p": str(p), "tier": e["tier"], "class": e["class"], "arm": arm,
                  "name": name, "idx": idx, "missing": True, "missing_reason": why, "valid": False,
                  "exclusion_reasons": ["MISSING: " + why]})

    s1 = S1.get(p, {})
    names_all = ["A1", "A3"] + ["A4_%d" % k for k in range(1, 21)] + ["A5_%d" % k for k in range(1, 21)] + \
                ["A6_%d" % k for k in range(22)]
    if s1.get("error") or "_A1" not in s1:
        for nm in names_all:
            missing(nm, nm.split("_")[0], None, "stage1 failed: %s" % s1.get("error"))
        ctrl["status"] = "missing: stage1 failed"
        return
    alg = s1["_alg"]
    calg_a = st["calg_a_pass"]
    # ---- A1
    an1, calg1 = s1["_A1"]
    L.append(finish(lat_entry(p, e, "A1", "A1", None, "O0_basis_form",
                              an1["basis_f"], 1, [[F(v) for v in row] for row in s1["A1"]["gram"]],
                              {"gram_nrd_unscaled": s1["A1"]["gram_nrd_unscaled"]}), an1, calg1, p))
    if s2.get("error") or "lattices" not in s2:
        for nm in names_all[1:]:
            missing(nm, nm.split("_")[0], None, "stage2 not available: %s" % s2.get("error"))
        ctrl["status"] = "missing: stage2 not available"
        return
    # stage-2 structure constants must equal stage-1's (same alginit, fixed RNG state)
    st["stage2_multable_equals_stage1"] = s2["multable"] == s1["multable"]
    st["multable_stage2"] = s2["multable"]
    st["one_stage2"] = s2["one"]
    st["stage2_gp_ms"] = s2.get("ms")
    alg2 = Alg(s2["multable"], s2["one"])
    recs = {r["name"]: r for r in s2["lattices"]}
    B = [[F(v) for v in col] for col in recs["base"]["basis"]]
    inB = span_checker(B)
    common = {"a_ramification": calg_a, "stage2_matches_stage1": st["stage2_multable_equals_stage1"]}

    # ---- base
    anb = analyse_pari_lattice(recs["base"], alg2, p)
    calgb = dict(order_checks(alg2, anb["basis_f"]), **common)
    base_ent = finish(lat_entry(p, e, "base", "base", None, "O0_basis_form", anb["basis_f"], 1,
                                [[F(v) for v in r_] for r_ in recs["base"]["gram"]], {"base_kind": st["base"]}),
                      anb, calgb, p)
    base_ent["counted_in"] = "controls only (A1 is counted from stage1)"
    L.append(base_ent)
    det_base = anb["det_pari"]

    # ---- C-TRD
    rT = recs["C-TRD"]
    T = [[F(v) for v in row] for row in rT["gram"]]
    T_py = [[alg2.trd(x) * alg2.trd(y) - alg2.trd(alg2.mul(x, y)) for y in B] for x in B]
    detT_py = det(T)
    ok_cross = F(rT["det_pari"]) == detT_py and T_py == T
    ratio = detT_py / det_base if det_base else None
    RT = detT_py * 16 / (p * p)
    ctrl["C-TRD"] = {"trace_form": rT["gram"], "det_pari": rT["det_pari"], "det_python": fstr(detT_py),
                     "trace_form_python_regrep_agree": T_py == T, "ccross_pass": ok_cross and anb["ccross_pass"],
                     "ratio_detT_over_detA": fstr(ratio), "ratio_expected": "16", "R_T": fstr(RT),
                     "R_T_preregistered": "16", "R_T_equals_preregistered": RT == 16,
                     "ratio_ok": ratio == 16, "R_ne_1": RT != 1}
    ctrl["C-TRD"]["pass"] = ctrl["C-TRD"]["ratio_ok"] and ctrl["C-TRD"]["R_ne_1"] and ctrl["C-TRD"]["ccross_pass"]

    # ---- C-NONMAX
    rN = recs["C-NONMAX"]
    anN = analyse_pari_lattice(rN, alg2, p)
    calgN = dict(order_checks(alg2, anN["basis_f"]), **common)
    idx_py = abs(det(matmul(inv(cols_to_mat(B)), cols_to_mat(anN["basis_f"]))))
    tf = [[F(v) for v in row] for row in rN["trace_form"]]
    tf_det_py = det(tf)
    entN = finish(lat_entry(p, e, "C-NONMAX", "C-NONMAX", None, "O0_basis_form", anN["basis_f"], 1,
                            [[F(v) for v in r_] for r_ in rN["gram"]]), anN, calgN, p)
    L.append(entN)
    ratioN = anN["det_pari"] / det_base
    ctrl["C-NONMAX"] = {"trace_form": rN["trace_form"], "index_pari": rN["index_pari"], "index_python": fstr(idx_py), "index_expected": "8",
                        "index_ok": F(rN["index_pari"]) == 8 and idx_py == 8,
                        "ratio": fstr(ratioN), "ratio_expected": "64", "ratio_ok": ratioN == 64,
                        "trace_form_det_pari": rN["trace_form_det_pari"], "trace_form_det_python": fstr(tf_det_py),
                        "trace_form_det_ne_p2": tf_det_py != p * p and F(rN["trace_form_det_pari"]) == tf_det_py,
                        "R": entN["R"], "R_preregistered": "64", "R_ne_1": anN["R"] is not None and anN["R"] != 1,
                        "lattice_valid": entN["valid"]}
    c = ctrl["C-NONMAX"]
    c["pass"] = c["index_ok"] and c["ratio_ok"] and c["trace_form_det_ne_p2"] and c["R_ne_1"] and c["lattice_valid"]

    # ---- A3 = P
    rP = recs["A3"]
    anP = analyse_pari_lattice(rP, alg2, p)
    PB = anP["basis_f"]
    inP = span_checker(PB)
    idxP_py = abs(det(matmul(inv(cols_to_mat(B)), cols_to_mat(PB))))
    calgP = dict(common)
    calgP["e_P_subset_O"] = all(inB(x) for x in PB)
    calgP["e_OP_subset_P"] = all(inP(alg2.mul(o, x)) for o in B for x in PB)
    calgP["e_PO_subset_P"] = all(inP(alg2.mul(x, o)) for o in B for x in PB)
    calgP["e_p_divides_nrd_basis"] = all(alg2.nrd(x) is not None and is_int(alg2.nrd(x) / p) for x in PB)
    calgP["base_valid"] = base_ent["calg_pass"]
    entP = finish(lat_entry(p, e, "A3", "A3", None, "O0_basis_form", PB, p,
                            [[F(v) for v in r_] for r_ in rP["gram"]],
                            {"gram_nrd_unscaled": rP["gram_nrd_unscaled"]}), anP, calgP, p)
    nP_py = anP["n_python"]
    entP.update({"index_pari": rP["index_pari"], "index_python": fstr(idxP_py), "n_pari": rP["n_pari"],
                 "n_python": fstr(nP_py), "index_instruments_agree": F(rP["index_pari"]) == idxP_py,
                 "n_instruments_agree": F(rP["n_pari"]) == nP_py,
                 "index_equals_n_squared": idxP_py == nP_py ** 2,
                 "diagnostic_index_equals_p2": idxP_py == p * p,
                 "kernel_mod_p_dim": rP["kernel_mod_p_dim"]})
    if not (entP["index_instruments_agree"] and entP["n_instruments_agree"]):
        entP["valid"] = False
        entP["exclusion_reasons"].append("C-CROSS: index/n instrument disagreement")
    L.append(entP)

    # ---- C-NEAR
    near = {}
    for nm, sc, exp in (("C-NEAR-O0", 1, Fraction(p * p, 4)), ("C-NEAR-P0", p, Fraction(p, 4))):
        rr = recs[nm]
        ann = analyse_pari_lattice(rr, alg2, p)
        parent = inB if nm == "C-NEAR-O0" else inP
        calgn = dict(common)
        calgn["trace_zero_basis"] = all(alg2.trd(x) == 0 for x in ann["basis_f"])
        calgn["contained_in_parent"] = all(parent(x) for x in ann["basis_f"])
        entn = finish(lat_entry(p, e, nm, nm, None, "O0_basis_form", ann["basis_f"], sc,
                                [[F(v) for v in r_] for r_ in rr["gram"]]), ann, calgn, p)
        entn["R"] = None  # R is not the metric for rank-3 objects
        entn["det_expected"] = fstr(exp)
        entn["det_equals_expected"] = ann["det_pari"] == exp and ann["det_python"] == exp
        L.append(entn)
        near[nm] = entn
    ctrl["C-NEAR"] = {"det_O0": near["C-NEAR-O0"]["det_python"], "det_O0_expected": fstr(Fraction(p * p, 4)),
                      "det_P0": near["C-NEAR-P0"]["det_python"], "det_P0_expected": fstr(Fraction(p, 4)),
                      "O0_ok": near["C-NEAR-O0"]["det_equals_expected"], "P0_ok": near["C-NEAR-P0"]["det_equals_expected"],
                      "lattices_valid": near["C-NEAR-O0"]["valid"] and near["C-NEAR-P0"]["valid"]}
    ctrl["C-NEAR"]["pass"] = ctrl["C-NEAR"]["O0_ok"] and ctrl["C-NEAR"]["P0_ok"] and ctrl["C-NEAR"]["lattices_valid"]

    # ---- A4 / A5 / C-NOSCALE
    ctrl["C-NOSCALE"] = []
    Binv = inv(cols_to_mat(B))
    parents = {0: (B, 1, base_ent), 1: (PB, p, entP)}
    for k in range(1, 21):
        nm = "A4_%d" % k
        rI = recs.get(nm)
        if rI is None or rI.get("error"):
            missing(nm, "A4", k, (rI or {}).get("error", "no record"))
            missing("A5_%d" % k, "A5", k, "parent A4 ideal missing")
            ctrl["C-NOSCALE"].append({"idx": k, "missing": True, "pass": False})
            continue
        anI = analyse_pari_lattice(rI, alg2, p)
        IB = anI["basis_f"]
        inI = span_checker(IB)
        idxI_py = abs(det(matmul(Binv, cols_to_mat(IB))))
        calgI = dict(common)
        calgI["d_I_subset_O"] = all(inB(x) for x in IB)
        calgI["d_OI_subset_I"] = all(inI(alg2.mul(o, x)) for o in B for x in IB)
        calgI["base_valid"] = base_ent["calg_pass"]
        nI = anI["n_python"]
        entI = finish(lat_entry(p, e, nm, "A4", k, "O0_basis_form", IB, F(rI["form_scale"]),
                                [[F(v) for v in r_] for r_ in rI["gram"]],
                                {"gram_nrd_unscaled": rI["gram_nrd_unscaled"], "target_norm": rI["target_norm"],
                                 "seed": rI["seed"], "attempts": rI["attempts"],
                                 "alpha_base_coords": rI["alpha_base_coords"], "nrd_alpha": rI["nrd_alpha"]}),
                      anI, calgI, p)
        entI.update({"index_pari": rI["index_pari"], "index_python": fstr(idxI_py), "n_pari": rI["n_pari"],
                     "n_python": fstr(nI), "index_instruments_agree": F(rI["index_pari"]) == idxI_py,
                     "n_instruments_agree": F(rI["n_pari"]) == nI,
                     "index_equals_n_squared": idxI_py == nI ** 2,
                     "normhit": nI == F(rI["target_norm"])})
        if not (entI["index_instruments_agree"] and entI["n_instruments_agree"]):
            entI["valid"] = False
            entI["exclusion_reasons"].append("C-CROSS: index/n instrument disagreement")
        L.append(entI)
        parents[k + 1] = (IB, nI, entI)
        # C-NOSCALE
        du, ds = anI["det_python_unscaled"], anI["det_python"]
        ratio = du / ds
        Ru = du * 16 / (p * p)
        cn = {"idx": k, "n": fstr(nI), "det_unscaled": fstr(du), "det_scaled": fstr(ds),
              "ratio": fstr(ratio), "ratio_expected": fstr(nI ** 4), "ratio_ok": ratio == nI ** 4,
              "R_unscaled": fstr(Ru), "R_preregistered": fstr(nI ** 4), "R_ne_1": Ru != 1,
              "ccross_pass": anI["ccross"].get("i_det_unscaled_agree", False) and anI["ccross_pass"]}
        cn["pass"] = cn["ratio_ok"] and cn["R_ne_1"] and cn["ccross_pass"]
        ctrl["C-NOSCALE"].append(cn)
        # A5
        nm5 = "A5_%d" % k
        rO = recs.get(nm5)
        if rO is None or rO.get("error"):
            missing(nm5, "A5", k, (rO or {}).get("error", "no record"))
            continue
        anO = analyse_pari_lattice(rO, alg2, p)
        calgO = dict(order_checks(alg2, anO["basis_f"]), **common)
        calgO["d_I_OR_subset_I"] = all(inI(alg2.mul(x, o)) for x in IB for o in anO["basis_f"])
        calgO["parent_ideal_calg"] = entI["calg_pass"]
        L.append(finish(lat_entry(p, e, nm5, "A5", k, "O0_basis_form", anO["basis_f"], 1,
                                  [[F(v) for v in r_] for r_ in rO["gram"]],
                                  {"gram_nrd_unscaled": rO["gram_nrd_unscaled"]}), anO, calgO, p))

    # ---- A6
    Hinfo = s2["_H"]
    for k in range(22):
        nm = "A6_%d" % k
        r6 = recs.get(nm)
        m = M_LIST[k % 10]
        if r6 is None or r6.get("error") or k not in parents:
            missing(nm, "A6", k, (r6 or {}).get("error", "parent missing"))
            continue
        Mb, sc, pent = parents[k]
        an6 = analyse_pari_lattice(r6, alg2, p)
        H = [[F(v) for v in row] for row in cols_to_mat([[F(v) for v in c_] for c_ in r6["H"]])]
        H_planned = [[F(v) for v in row] for row in Hinfo[k][1]]
        m_meas = abs(det(H))
        m_meas_py = abs(det(matmul(inv(cols_to_mat(Mb)), cols_to_mat(an6["basis_f"]))))
        calg6 = dict(common)
        calg6["f_index_equals_planned_m"] = m_meas == m and F(r6["index_pari"]) == m and m_meas_py == m
        calg6["H_equals_planned"] = H == H_planned
        calg6["form_scale_equals_parent"] = F(r6["form_scale"]) == sc
        calg6["parent_valid"] = pent["valid"]
        ent6 = finish(lat_entry(p, e, nm, "A6", k, "O0_basis_form", an6["basis_f"], sc,
                                [[F(v) for v in r_] for r_ in r6["gram"]],
                                {"H": [[fstr(v) for v in row] for row in H_planned], "seed": str(Hinfo[k][0]),
                                 "m_planned": m, "m_measured": fstr(m_meas), "m_measured_python": fstr(m_meas_py),
                                 "parent": pent["name"]}), an6, calg6, p)
        ent6["R"] = None
        if an6["ccross"]["i_det_agree"]:
            ent6["R_sub"] = fstr(an6["det_pari"] * 16 / (m_meas * m_meas * p * p))
            det_parent = F(pent["det_python"])
            ent6["det_ratio_to_parent"] = fstr(an6["det_pari"] / det_parent) if det_parent else None
            ent6["det_ratio_equals_m2"] = an6["det_pari"] == m_meas * m_meas * det_parent
        else:
            ent6["R_sub"] = None
        L.append(ent6)
    ctrl["status"] = "computed"


def matmul(A, B):
    return [[sum(A[i][t] * B[t][j] for t in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


# ----------------------------------------------------------------- counts and outcome
PRIMARY_ARMS = ["A1", "A2", "A3", "A4", "A5"]


def tally(raw, note_path):
    L = raw["lattices"]
    primes = [e["p"] for e in raw["primes"]]
    per = {}
    summ = {"primes_planned": 22, "primes_listed": len(primes)}
    fnorm, fsub, dstd, excl, instr, idxmis = [], [], [], [], [], []
    for arm in PRIMARY_ARMS + ["A6"]:
        per[arm] = {}
    for x in L:
        if x["arm"] not in per:
            continue
        c = per[x["arm"]].setdefault(x["p"], {"planned": 0, "valid": 0, "R_eq_1": 0, "R_ne_1": 0, "excluded": 0,
                                               "missing": 0})
        c["planned"] += 1
        if x.get("missing"):
            c["missing"] += 1
            excl.append((x["id"], x["missing_reason"]))
            continue
        rkey = "R_sub" if x["arm"] == "A6" else "R"
        if not x["valid"]:
            c["excluded"] += 1
            reasons = "; ".join(x["exclusion_reasons"])
            if x["arm"] == "A2":
                if not x.get("calg_pass"):
                    dstd.append((x["id"], reasons))
                if not x.get("ccross_pass"):
                    instr.append((x["id"], reasons))
            else:
                if not x.get("ccross_pass") or any(r.startswith("C-CROSS") for r in x["exclusion_reasons"]):
                    instr.append((x["id"], reasons))
                if not x.get("calg_pass"):
                    excl.append((x["id"], reasons))
            continue
        c["valid"] += 1
        if F(x[rkey]) == 1:
            c["R_eq_1"] += 1
        else:
            c["R_ne_1"] += 1
            if x["arm"] == "A6":
                fsub.append(x["id"])
            elif x["arm"] == "A2":
                dstd.append((x["id"], "R=%s" % x[rkey]))
            else:
                fnorm.append(x["id"])
        if x["arm"] in ("A3", "A4") and not x["index_equals_n_squared"]:
            idxmis.append(x["id"])
    # M-R / M-SUB / M-INDEX totals
    def tot(arms, key):
        return sum(v[key] for a in arms for v in per[a].values())
    summ["M_R_planned"] = 22 * 43
    summ["M_R_listed"] = tot(PRIMARY_ARMS, "planned")
    summ["M_R_valid"] = tot(PRIMARY_ARMS, "valid")
    summ["M_R_R_eq_1"] = tot(PRIMARY_ARMS, "R_eq_1")
    summ["M_R_R_ne_1"] = tot(PRIMARY_ARMS, "R_ne_1")
    summ["M_R_excluded"] = tot(PRIMARY_ARMS, "excluded")
    summ["M_R_missing"] = tot(PRIMARY_ARMS, "missing")
    summ["M_R_by_arm"] = {a: {k: tot([a], k) for k in ("planned", "valid", "R_eq_1", "R_ne_1", "excluded", "missing")}
                          for a in PRIMARY_ARMS}
    summ["M_SUB_planned"] = 22 * 22
    summ["M_SUB_listed"] = tot(["A6"], "planned")
    summ["M_SUB_valid"] = tot(["A6"], "valid")
    summ["M_SUB_R_eq_1"] = tot(["A6"], "R_eq_1")
    summ["M_SUB_R_ne_1"] = tot(["A6"], "R_ne_1")
    summ["M_SUB_excluded_or_missing"] = tot(["A6"], "excluded") + tot(["A6"], "missing")
    ideals = [x for x in L if x["arm"] in ("A3", "A4")]
    summ["M_INDEX_planned"] = 22 * 21
    summ["M_INDEX_listed"] = len(ideals)
    summ["M_INDEX_evaluated"] = sum(1 for x in ideals if not x.get("missing") and x.get("calg_pass")
                                    and x.get("index_instruments_agree") and x.get("n_instruments_agree"))
    summ["M_INDEX_mismatches"] = len(idxmis)
    summ["M_NORMHIT_hits"] = sum(1 for x in L if x["arm"] == "A4" and x.get("normhit") is True)
    summ["M_NORMHIT_misses"] = [x["id"] for x in L if x["arm"] == "A4" and x.get("normhit") is False]
    # M-CROSS
    cross_fail = [x["id"] for x in L if not x.get("missing") and x.get("ccross_pass") is False]
    ctrl_cross_fail = []
    for c in raw["controls"]:
        if "C-TRD" in c and not c["C-TRD"]["ccross_pass"]:
            ctrl_cross_fail.append(c["p"] + ":C-TRD")
        for cn in c.get("C-NOSCALE", []):
            if not cn.get("missing") and not cn["ccross_pass"]:
                ctrl_cross_fail.append("%s:C-NOSCALE_%d" % (c["p"], cn["idx"]))
    summ["M_CROSS_disagreements"] = len(cross_fail) + len(ctrl_cross_fail)
    summ["M_CROSS_list"] = cross_fail + ctrl_cross_fail
    # controls
    cfail = {"C-TRD": [], "C-NOSCALE": [], "C-NONMAX": [], "C-NEAR": []}
    invalid = []
    s4_other = []
    for c in raw["controls"]:
        if c.get("status") != "computed":
            for k in cfail:
                cfail[k].append(c["p"] + ": not computed")
            continue
        t = c["C-TRD"]
        if not t["pass"]:
            cfail["C-TRD"].append(c["p"])
        if t["ccross_pass"] and not t["ratio_ok"]:
            invalid.append(c["p"] + ":C-TRD ratio")
        elif not t["R_ne_1"]:
            s4_other.append(c["p"] + ":C-TRD R=1")
        n_ = c["C-NONMAX"]
        if not n_["pass"]:
            cfail["C-NONMAX"].append(c["p"])
        if n_["lattice_valid"] and not (n_["ratio_ok"] and n_["index_ok"]):
            invalid.append(c["p"] + ":C-NONMAX ratio/index")
        for cn in c["C-NOSCALE"]:
            if not cn["pass"]:
                cfail["C-NOSCALE"].append("%s:%d" % (c["p"], cn["idx"]))
            if not cn.get("missing") and cn["ccross_pass"] and not cn["ratio_ok"]:
                invalid.append("%s:C-NOSCALE_%d ratio" % (c["p"], cn["idx"]))
        if not c["C-NEAR"]["pass"]:
            cfail["C-NEAR"].append(c["p"])
    summ["controls_failed"] = cfail
    summ["controls_pass_counts"] = {
        "C-TRD": sum(1 for c in raw["controls"] if c.get("status") == "computed" and c["C-TRD"]["pass"]),
        "C-NONMAX": sum(1 for c in raw["controls"] if c.get("status") == "computed" and c["C-NONMAX"]["pass"]),
        "C-NEAR": sum(1 for c in raw["controls"] if c.get("status") == "computed" and c["C-NEAR"]["pass"]),
        "C-NOSCALE": sum(1 for c in raw["controls"] if c.get("status") == "computed"
                         for cn in c["C-NOSCALE"] if cn["pass"])}
    summ["controls_planned"] = {"C-TRD": 22, "C-NONMAX": 22, "C-NEAR": 22, "C-NOSCALE": 440}
    summ["fallback_primes"] = [p for p, s in raw["prime_status"].items() if s.get("fallback_used")]
    summ["calg_a_fail_primes"] = [p for p, s in raw["prime_status"].items() if s.get("calg_a_pass") is False]
    summ["calg_b_fail_primes"] = [p for p, s in raw["prime_status"].items()
                                  if s.get("calg_b") and not s["calg_b"]["pass"]]

    # outcome codes (frozen criteria, applied mechanically)
    trig = []
    if raw["status"] == "infra_failure":
        trig.append("F-INFRA")
    if raw["status"] == "stopped_calg_b":
        trig.append("F-INSTR")
    if invalid:
        trig.append("INVALID")
    if fnorm or idxmis:
        trig.append("F-NORM")
    if fsub:
        trig.append("F-SUB")
    if dstd:
        trig.append("INCONCLUSIVE-INSTRUMENT")
    if cfail["C-NEAR"]:
        trig.append("INCONCLUSIVE-NEAR")
    if excl:
        trig.append("INCONCLUSIVE-CONSTRUCTION")
    if instr or summ["M_CROSS_disagreements"]:
        trig.append("F-INSTR")
    if s4_other or cfail["C-TRD"] or cfail["C-NONMAX"] or cfail["C-NOSCALE"]:
        trig.append("INCONCLUSIVE")
    note_ok = os.path.isfile(note_path)
    s = {
        "S1": summ["M_R_listed"] == 946 and summ["M_R_valid"] == 946 and summ["M_R_R_eq_1"] == 946,
        "S2": summ["M_SUB_listed"] == 484 and summ["M_SUB_valid"] == 484 and summ["M_SUB_R_eq_1"] == 484,
        "S3": summ["M_INDEX_listed"] == 462 and summ["M_INDEX_evaluated"] == 462 and summ["M_INDEX_mismatches"] == 0,
        "S4": not any(cfail.values()) and len(raw["controls"]) == 22,
        "S5": summ["M_CROSS_disagreements"] == 0,
        "S6_file_present": note_ok,
        "S7": "pending: evaluated by check.py after the driver",
    }
    order = ["F-INFRA", "F-INSTR", "INVALID", "F-NORM", "F-SUB", "INCONCLUSIVE-INSTRUMENT", "INCONCLUSIVE-NEAR",
             "INCONCLUSIVE-CONSTRUCTION", "INCONCLUSIVE"]
    trig = sorted(set(trig), key=order.index)
    all_s = all(v is True for k, v in s.items() if k != "S7")
    primary = trig[0] if trig else ("SUCCESS" if all_s else "INCONCLUSIVE")
    outcome = {"primary_code": primary, "triggered_codes": trig, "success_conditions": s,
               "primary_code_note": ("SUCCESS here is conditional on S6 (note content, judged by review) and S7 "
                                     "(check.py exit 0); precedence when several codes trigger: " + " > ".join(order)),
               "F_NORM_cells": fnorm, "M_INDEX_mismatch_cells": idxmis, "F_SUB_cells": fsub,
               "D_STD_cells": dstd, "instrument_disagreement_cells": instr,
               "construction_exclusions": excl, "INVALID_cells": invalid, "S4_other_failures": s4_other}
    counts = {"summary": summ, "per_arm_per_prime": per}
    # M-EXP (report only; floats never used in a decision)
    mexp = []
    for x in L:
        if x["arm"] in ("A3", "C-NEAR-P0") and not x.get("missing"):
            d = F(x["det_python"])
            pp = int(x["p"])
            rank = 4 if x["arm"] == "A3" else 3
            mexp.append({"p": x["p"], "lattice": x["arm"], "rank": rank, "det_exact": x["det_python"],
                         "report_only_float_log_p_det_over_rank":
                             (math.log(d.numerator) - math.log(d.denominator)) / math.log(pp) / rank if pp > 1 else None})
    counts["M_EXP_report_only"] = mexp
    return counts, outcome


if __name__ == "__main__":
    sys.exit(main())
