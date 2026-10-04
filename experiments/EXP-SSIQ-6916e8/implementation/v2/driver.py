#!/usr/bin/env python3
"""EXP-SSIQ-6916e8 driver, PROTOCOL VERSION 2 (frozen specification v1 +
AMD-20260926-f9acf7), task TASK-20260926-fba7e0, run RUN-SSIQ-004595.

Copied from the version-1 driver (implementation/driver.py, sha256
349f2bff...2157002, bound by RUN-SSIQ-81bd08) and changed ONLY where the
amendment requires it:

  * fallback_rule: route ladder R1 -> R2 -> R3 when alginit RAISES a caught
    PARI error at stage 1; gate G-A2 on every A2-based base order (R1 path
    "A1 fails C-ALG" and R3); stage consistency (stage 2 reuses the stage-1
    route verbatim; a stage-2 error or structure-constant mismatch makes every
    PARI-side cell of that route NOT_COMPUTED, cause CONSTRUCTION); the
    terminal case; a per-prime route record in prime_status.
  * tally_rule: every planned item (946 primary lattices, 484 A6, 462 M-INDEX
    ideals, 506 control values) gets exactly one state COMPUTED_VALID |
    COMPUTED_EXCLUDED | NOT_COMPUTED (with cause CONSTRUCTION | INFRASTRUCTURE);
    NOT_COMPUTED is never a mismatch; codes, precedence and blocking cells as
    declared.
  * D-9: the full gp version string is captured from stderr. (The C-6
    reproducibility comparison is the separate helper compare_runs.py.)
  * a gp stage call that returns no record (crash / kill) raises InfraError
    (C-4: a crash is never a route failure).

Phases:
  phase P  prime search (PARI nextprime + proven isprime) for tiers M and L
  phase 1a per prime: PARI stage1 route R1 (the version-1 call, unchanged)
  gate     stopping rule: C-ALG (b) failure under R1 -> STOP, F-INSTR, no R
  phase 1b per prime: A2 in Python; base-order rule; routes R2/R3 only where R1
           raised; gate G-A2 (PARI matdet of the A2 Gram via a matdet-only call)
  phase 2  per prime: PARI stage2 on the chosen route (base, C-TRD, C-NONMAX,
           A3, C-NEAR, A4, A5, A6, PARI matdet of the A2 Grams)
  analysis independent Python instruments on every lattice (C-CROSS), C-ALG,
           R values, states, counts, outcome codes (tally_rule)

Exact arithmetic only: every pass/fail decision uses fractions.Fraction or
Python int. The only floats are the M-EXP "report_only" renderings and
timings, which never enter a decision.

No curve, isogeny, key or attack is constructed (handoff C-6).
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
PROTOCOL_VERSION = 2
AMENDMENT_ID = "AMD-20260926-f9acf7"
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
V1_DIR = os.path.dirname(HERE)                  # implementation/ (version-1 files, read only)
EXP_DIR = os.path.dirname(V1_DIR)
AMENDMENT_PATH = os.path.join(EXP_DIR, "amendments", "AMD-20260926-f9acf7.yaml")
V1_SHA256 = {  # bound by RUN-SSIQ-81bd08's manifest; verified at start, never modified
    "build_lattices.gp": "65d1f7b2e81c3f98e2a6b14895a36feb9861048de7b6e065bd1f47cb5d5f313f",
    "driver.py": "349f2bff4453419c18f7945f2148872a12bca70532467a8f7e2fd685a2157002",
    "check.py": "39b9e1bf711e90f5b8f4b27636072e242681bb55da4bec1e52dcd9f22d8d58c1"}
NOT_COMPUTED, VALID, EXCLUDED = "NOT_COMPUTED", "COMPUTED_VALID", "COMPUTED_EXCLUDED"
CONSTRUCTION, INFRASTRUCTURE = "CONSTRUCTION", "INFRASTRUCTURE"
PRECEDENCE = ["F-INFRA", "F-INSTR", "INVALID", "F-NORM", "F-SUB", "INCONCLUSIVE-INSTRUMENT", "INCONCLUSIVE-NEAR",
              "INCONCLUSIVE-CONSTRUCTION", "INCONCLUSIVE"]


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


def analyse_a2(p, pres, basis_override=None):
    a, b = pres["a"], pres["b"]
    basis = [[Fraction(v) for v in e] for e in (basis_override or a2_basis(p, pres))]
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
def sh(cmd, stream="stdout"):
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, cwd=EXP_DIR)
        return cp.stdout if stream == "stdout" else cp.stderr
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
        # D-9: gp prints its --version banner to STDERR; capture it from there.
        "gp_version_full": sh([GP_BIN, "--version"], "stderr").strip(),
        "gp_version_full_stdout": sh([GP_BIN, "--version"]).strip(),
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
        "implementation_dir": os.path.relpath(HERE, os.path.dirname(os.path.dirname(EXP_DIR))),
        "v1_implementation_sha256": {n: sha256_file(os.path.join(V1_DIR, n)) for n in sorted(V1_SHA256)},
        "specification_sha256": sha256_file(os.path.join(EXP_DIR, "specification.yaml")),
        "amendment_id": AMENDMENT_ID,
        "amendment_sha256": sha256_file(AMENDMENT_PATH),
        "protocol_version": PROTOCOL_VERSION,
    }
    env["v1_implementation_unchanged"] = env["v1_implementation_sha256"] == V1_SHA256
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
    ap.add_argument("--dev-inject", default="",
                    help="DEVELOPMENT ONLY (requires --dev-primes): comma-separated fault injections of the form "
                         "<p>:<R1|R2|R3|S2> (make that route's stage-1 alginit, or the stage-2 alginit, raise) or "
                         "<p>:A2BAD (replace A2 by the non-maximal order Z<1,i,j,k>). Never used for the recorded run.")
    args = ap.parse_args()
    dev = [int(x) for x in args.dev_primes.split(",")] if args.dev_primes else None
    inject = set(x for x in args.dev_inject.split(",") if x)
    if inject and not dev:
        sys.exit("--dev-inject requires --dev-primes (development only)")
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
    print("[env] git_head=%s dirty=%s gp=%s v1_unchanged=%s" % (env["git_head"], env["git_dirty"],
          env["gp_version_short"], env["v1_implementation_unchanged"]), flush=True)
    if not env["v1_implementation_unchanged"] and not dev:
        sys.exit("version-1 implementation files differ from the sha256 values bound by RUN-SSIQ-81bd08; refusing")

    raw = {"experiment_id": EXPERIMENT_ID, "spec_version": SPEC_VERSION, "protocol_version": PROTOCOL_VERSION,
           "amendment_id": AMENDMENT_ID, "amendment_sha256": env["amendment_sha256"],
           "prior_run": "RUN-SSIQ-81bd08", "run_id": args.run_id,
           "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
           "base_seed": BASE_SEED,
           "seed_derivation": ("seed(arm, p, index) = int(sha256('%d:<arm>:<p>:<index>').hexdigest()[:16], 16); "
                               "A4: PARI setrand(seed('A4', p, k)) k=1..20 before the alpha search; "
                               "A6: Python random.Random(seed('A6', p, k)) k=0..21 for the diagonal split and "
                               "off-diagonal entries; PARI setrand(1) immediately before every alginit call "
                               "(alginit's internal randomness, if any, is thereby fixed)." % BASE_SEED),
           "m_list": M_LIST, "a4_max_attempts": A4_MAX_ATTEMPTS,
           "dev_injections": sorted(inject),
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

    def stage_call(label, p, a, b, maxord, stage_script):
        """One stage-1 or stage-2 gp call. A caught PARI error comes back as a record with
        'error'; NO record at all is a crash / kill -> InfraError (never a route failure)."""
        pre = "DEV_INJECT_FAIL=1;\n" if ("%d:%s" % (p, label)) in inject else ""
        r = gp_call("%s p=%d" % (label, p), pre + stage_script)
        if not r:
            raise InfraError("gp %s at p=%d returned no record (crash or kill; returncode %s)"
                             % (label, p, raw["gp_calls"][-1]["returncode"]))
        return r[0]

    def call_text(a, b, maxord):
        return ("alginit(nfinit(y), [%d, %d])" % (a, b)) if maxord else ("alginit(nfinit(y), [%d, %d], , 0)" % (a, b))

    def parse_stage1(s1, p, route):
        """C-ALG (a)/(b), structure constants, ijk relations of one stage-1 attempt (exact)."""
        fin = [int(x) for x in s1["ramified_finite"]]
        hil = {h["place"]: int(h["symbol"]) for h in s1["hilbert"]}
        hil_ok = all((v == -1) == (k in (str(p), "inf")) for k, v in hil.items()) and hil.get("inf") == -1 \
            and hil.get(str(p)) == -1
        calg_a = {"ramified_finite": fin, "ramified_infinite_count": s1["ramified_infinite_count"],
                  "algramifiedplaces_ok": fin == [p] and s1["ramified_infinite_count"] == 1,
                  "hilbert": hil, "hilbert_ok": hil_ok}
        alg = Alg(s1["multable"], s1["one"])
        prods = s1["algmul_products"]
        sc_ok = all([alg.MT[i][r_][j] for r_ in range(4)] == [F(v) for v in prods[4 * i + j]]
                    for i in range(4) for j in range(4))
        return {"calg_a": calg_a, "calg_a_pass": calg_a["algramifiedplaces_ok"] and hil_ok,
                "calg_b": {"nrd_one": s1["nrd_one"], "nrd_two": s1["nrd_two"],
                           "pass": F(s1["nrd_one"]) == 1 and F(s1["nrd_two"]) == 4},
                "structure_constants_reproduce_algmul": sc_ok, "ijk_relations_ok": s1["ijk_relations_ok"],
                "_alg": alg}

    def adopt(st, s1, chk):
        """Record the CHOSEN route's stage-1 data under the version-1 field names."""
        st["calg_a"] = chk["calg_a"]
        st["calg_a_pass"] = chk["calg_a_pass"]
        st["calg_b"] = chk["calg_b"]
        st["multable_stage1"] = s1["multable"]
        st["one_stage1"] = s1["one"]
        st["algmul_products_stage1"] = s1["algmul_products"]
        st["algbasis_natural"] = s1["algbasis_natural"]
        st["splitting_pol"] = s1["splitting_pol"]
        st["ijk_images"] = [s1["i_image"], s1["j_image"], s1["k_image"]]
        st["stage1_gp_ms"] = s1["ms"]
        st["structure_constants_reproduce_algmul"] = chk["structure_constants_reproduce_algmul"]
        st["ijk_relations_ok"] = chk["ijk_relations_ok"]

    def attempt_record(route, s1, a, b, maxord, chk):
        att = {"route": route, "call": call_text(a, b, maxord), "call_gp_echo": s1.get("call"),
               "presentation": [a, b], "maxord_flag": maxord, "setrand_before_alginit": 1,
               "error": s1.get("error")}
        if chk is not None:
            att.update({"calg_a_pass": chk["calg_a_pass"], "calg_a": chk["calg_a"], "calg_b": chk["calg_b"],
                        "structure_constants_reproduce_algmul": chk["structure_constants_reproduce_algmul"],
                        "ijk_relations_ok": chk["ijk_relations_ok"], "multable": s1["multable"], "one": s1["one"],
                        "algmul_products": s1["algmul_products"],
                        "ijk_images": [s1["i_image"], s1["j_image"], s1["k_image"]]})
        return att

    def a1_analysis(s1, chk, p):
        alg = chk["_alg"]
        an = analyse_pari_lattice(s1["A1"], alg, p)
        calg = order_checks(alg, an["basis_f"])
        calg["a_ramification"] = chk["calg_a_pass"]
        calg["structure_constants"] = chk["structure_constants_reproduce_algmul"]
        return an, calg

    def mapped_a2(alg, s1, p):
        im = [alg.one, [F(v) for v in s1["i_image"]], [F(v) for v in s1["j_image"]],
              [F(v) for v in s1["k_image"]]]
        return [[sum(x[t] * im[t][r_] for t in range(4)) for r_ in range(4)] for x in A2[p]["basis"]]

    def gate_a2(p):
        """Gate G-A2: the Python A2 cell at p must be valid (C-ALG, C-CROSS) with R = 1 exactly."""
        a2 = A2[p]
        r = gp_call("g_a2_dets p=%d" % p, "print(\"@@JSON \", jobj([jkv(\"stage\", jq(\"dets\")), "
                    "jkv(\"extra_dets_pari\", jlist(apply(G->jr(matdet(G)), [%s])))]));\n" % gp_mat(a2["gram"]))
        if not r:
            raise InfraError("gp g_a2_dets at p=%d returned no record" % p)
        dp = F(r[0]["extra_dets_pari"][0])
        dy = det(a2["gram"])
        calg_pass = summarize_bool(a2["calg"])
        cross = dp == dy
        R = dy * 16 / (p * p) if cross else None
        return {"evaluated": True, "det_pari": fstr(dp), "det_python": fstr(dy), "calg": dict(a2["calg"]),
                "calg_pass": calg_pass, "ccross_pass": cross, "R": fstr(R) if R is not None else None,
                "pass": calg_pass and cross and R == 1}

    def base_precheck(alg, basis, p):
        """R3 / A2-fallback base: C-ALG (c) in PARI coordinates (regular-representation instrument)
        and the mapped basis reproduces the Python A2 Gram exactly. Full C-CROSS (algnorm Gram,
        PARI matdet) is evaluated on the stage-2 'base' record."""
        oc = order_checks(alg, basis)
        g = alg.gram(basis)
        return {"c_order_checks": oc, "c_pass": summarize_bool(oc),
                "gram_regrep_equals_python_A2_gram": g is not None and g == A2[p]["gram"]}

    try:
        # -------------------------------------------------- phase P: primes
        cls_map = {"1": "3mod4", "2": "5mod8", "3": "1mod8"}
        if dev:
            raw["DEVELOPMENT_MODE"] = "NOT A RUN RECORD: dev primes %s, injections %s" % (dev, sorted(inject))
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

        # -------------------------------------------------- phase 1a: route R1 (version-1 call, unchanged)
        S1 = {}
        CHK = {}
        for e in plist:
            p, pres = e["p"], e["presentation"]
            a, b = pres["a"], pres["b"]
            s1 = stage_call("R1", p, a, b, 1, "stage1(%d, %d, %d, 1);\n" % (p, a, b))
            st = raw["prime_status"].setdefault(str(p), {})
            st["stage1_error"] = s1.get("error")
            chk = None if s1.get("error") else parse_stage1(s1, p, "R1")
            st["route_attempts"] = [attempt_record("R1", s1, a, b, 1, chk)]
            st["route_attempts"][0]["outcome"] = ("alginit raised: route ladder entered" if s1.get("error") else
                                                  "did not raise: version 1 applies verbatim; no further route")
            S1[p], CHK[p] = s1, chk

        # stopping rule (version 1, R1 only): C-ALG (b) failure -> STOP before any R
        bfail = [p for p in S1 if CHK[p] is not None and not CHK[p]["calg_b"]["pass"]]
        if bfail:
            raw["status"] = "stopped_calg_b"
            raw["stop_reason"] = "C-ALG (b) failed under R1 at primes %s: reduced-norm instrument wrong; no R computed" % bfail
            raise StopIteration

        # -------------------------------------------------- phase 1b: A2, base-order rule, routes R2/R3, gate G-A2
        A2 = {}
        CH = {}        # p -> (stage-1 record, checks, a, b, maxord) of the CHOSEN route
        A1SRC = {}     # p -> (route, analysis, calg, stage-1 record) of the recorded A1 cell
        for e in plist:
            p, pres = e["p"], e["presentation"]
            a, b = pres["a"], pres["b"]
            st = raw["prime_status"][str(p)]
            A2[p] = analyse_a2(p, pres)
            if ("%d:A2BAD" % p) in inject:   # development-only fault injection (non-maximal Z<1,i,j,k>)
                A2[p] = analyse_a2(p, pres, [[int(i == j) for j in range(4)] for i in range(4)])
            st["g_a2"] = {"evaluated": False}
            s1, chk = S1[p], CHK[p]
            if chk is not None:
                # ---- R1 did not raise: version 1 verbatim at this prime; no further route
                adopt(st, s1, chk)
                st["construction_route"], st["presentation_used"], st["maxord_flag"] = "R1", [a, b], 1
                an, calg = a1_analysis(s1, chk, p)
                A1SRC[p] = ("R1", an, calg, s1)
                CH[p] = (s1, chk, a, b, 1)
                if summarize_bool(calg):
                    st["base"] = "A1"
                    st["base_basis"] = [[1 if i == j else 0 for i in range(4)] for j in range(4)]
                elif st["ijk_relations_ok"] and st["calg_a_pass"]:
                    st["g_a2"] = gate_a2(p)
                    bb = mapped_a2(chk["_alg"], s1, p)
                    st["a2_fallback_precheck"] = base_precheck(chk["_alg"], bb, p)
                    if st["g_a2"]["pass"]:
                        st["base"] = "A2_fallback"
                        st["base_basis"] = bb
                    else:
                        st["base"] = "none"
                        st["base_none_reason"] = "R1: A1 failed C-ALG and gate G-A2 failed (A2 fallback not available)"
                else:
                    st["base"] = "none"
                    st["base_none_reason"] = "R1: A1 failed C-ALG and the algebra fails C-ALG (a) or the ijk relations"
                st["fallback_used"] = st["base"] == "A2_fallback"
                continue
            # ---- R1 RAISED: route R2 = alginit(nfinit(y), [b, a]) (same algebra, generators swapped)
            chosen = False
            s2 = stage_call("R2", p, b, a, 1, "stage1(%d, %d, %d, 1);\n" % (p, b, a))
            chk2 = None if s2.get("error") else parse_stage1(s2, p, "R2")
            att2 = attempt_record("R2", s2, b, a, 1, chk2)
            st["route_attempts"].append(att2)
            if chk2 is not None:
                alg_ok = chk2["calg_a_pass"] and chk2["calg_b"]["pass"] and chk2["structure_constants_reproduce_algmul"]
                att2["algebra_checks_pass"] = alg_ok
                if alg_ok:
                    an, calg = a1_analysis(s2, chk2, p)
                    att2["A1_calg_pass"], att2["A1_ccross_pass"] = summarize_bool(calg), an["ccross_pass"]
                    A1SRC[p] = ("R2", an, calg, s2)
                    if summarize_bool(calg) and an["ccross_pass"]:
                        adopt(st, s2, chk2)
                        st["construction_route"], st["presentation_used"], st["maxord_flag"] = "R2", [b, a], 1
                        st["base"] = "A1"
                        st["base_basis"] = [[1 if i == j else 0 for i in range(4)] for j in range(4)]
                        CH[p] = (s2, chk2, b, a, 1)
                        chosen = True
                        att2["outcome"] = "valid base order (A1 of the (b, a) algebra)"
                    else:
                        att2["outcome"] = "A1 computed but fails C-ALG (c) or C-CROSS: recorded as the A1 cell, EXCLUDED; go to R3"
                else:
                    att2["outcome"] = "algebra fails C-ALG (a)/(b) or the structure-constant check: go to R3"
            else:
                att2["outcome"] = "alginit raised: go to R3"
            if not chosen:
                # ---- route R3 = alginit(nfinit(y), [a, b], , 0); base = spec A2 order mapped in
                s3 = stage_call("R3", p, a, b, 0, "stage1(%d, %d, %d, 0);\n" % (p, a, b))
                chk3 = None if s3.get("error") else parse_stage1(s3, p, "R3")
                att3 = attempt_record("R3", s3, a, b, 0, chk3)
                st["route_attempts"].append(att3)
                ok3 = False
                if chk3 is not None:
                    alg_ok = chk3["calg_a_pass"] and chk3["calg_b"]["pass"] and \
                        chk3["structure_constants_reproduce_algmul"] and chk3["ijk_relations_ok"] is True
                    att3["algebra_checks_pass"] = alg_ok
                    if alg_ok:
                        st["g_a2"] = gate_a2(p)
                        bb = mapped_a2(chk3["_alg"], s3, p)
                        pc = base_precheck(chk3["_alg"], bb, p)
                        att3["base_precheck"] = pc
                        ok3 = st["g_a2"]["pass"] and pc["c_pass"] and pc["gram_regrep_equals_python_A2_gram"]
                        att3["outcome"] = ("valid base order (A2 order mapped into the R3 algebra)" if ok3 else
                                           "gate G-A2 or the mapped-base C-ALG (c) / Gram check failed")
                    else:
                        att3["outcome"] = "algebra fails C-ALG (a)/(b), the structure-constant check or the ijk relations"
                else:
                    att3["outcome"] = "alginit raised"
                if ok3:
                    adopt(st, s3, chk3)
                    st["construction_route"], st["presentation_used"], st["maxord_flag"] = "R3", [a, b], 0
                    st["base"] = "A2_fallback"
                    st["base_basis"] = bb
                    CH[p] = (s3, chk3, a, b, 0)
                else:
                    st["construction_route"], st["presentation_used"], st["maxord_flag"] = "none", None, None
                    st["base"] = "none"
                    st["base_none_reason"] = "TERMINAL CASE: every declared route (R1, R2, R3) failed to yield a valid base order"
            st["fallback_used"] = st["base"] == "A2_fallback"

        # -------------------------------------------------- phase 2 (chosen route reused verbatim)
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
                if not r:
                    raise InfraError("gp dets_only at p=%d returned no record" % p)
                S2[p] = {"error": "no valid base order", "extra_dets_pari": r[0]["extra_dets_pari"]}
                continue
            _, _, ra, rb, rmax = CH[p]
            B = cols_to_mat(st["base_basis"])
            script = "stage2(%d, %d, %d, %d, %s, %s, %s, [%s], [%s], %d);\n" % (
                p, ra, rb, rmax, gp_mat(B), gp_vec(Ns), gp_vec(seeds),
                ",".join(gp_mat(h[1]) for h in Hinfo), ",".join(gp_mat(G) for G in extra), A4_MAX_ATTEMPTS)
            S2[p] = stage_call("S2", p, ra, rb, rmax, script)
            S2[p]["_H"] = Hinfo
            st["stage2_call"] = call_text(ra, rb, rmax)
            st["stage2_error"] = S2[p].get("error")
            if not S2[p].get("error"):
                st["stage2_multable_equals_stage1"] = S2[p]["multable"] == st["multable_stage1"]
            else:
                # stage 2 raised: the A2 cell is still computed in Python; its PARI matdet comes from a
                # matdet-only call (as at a prime without a base order), so no instrument is left uncomputed
                r = gp_call("dets_only p=%d" % p, "print(\"@@JSON \", jobj([jkv(\"stage\", jq(\"dets\")), "
                            "jkv(\"extra_dets_pari\", jlist(apply(G->jr(matdet(G)), [%s])))]));\n"
                            % ",".join(gp_mat(G) for G in extra))
                if not r:
                    raise InfraError("gp dets_only at p=%d returned no record" % p)
                S2[p]["extra_dets_pari"] = r[0]["extra_dets_pari"]
            print("[stage2] p=%s (%s, %s) route=%s base=%s gp_ms=%s" % (p if p < 10 ** 6 else "~2^%d" % p.bit_length(),
                  e["tier"], e["class"], st["construction_route"], st["base"], S2[p].get("ms")), flush=True)

        # -------------------------------------------------- analysis
        for e in plist:
            analyse_prime(e, A1SRC, S2, A2, raw)
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
    print("[routes] " + json.dumps(raw["counts"]["summary"]["route_record"], sort_keys=True), flush=True)
    print("[counts] " + json.dumps({k: v for k, v in raw["counts"]["summary"].items() if k != "route_record"},
                                   sort_keys=True), flush=True)
    print("[blocking] %d items: %s" % (len(raw["outcome"]["blocking_cells"]), raw["outcome"]["blocking_cells"][:80]),
          flush=True)
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
    """S1 here is A1SRC: p -> (route, analysis, calg, stage-1 record) of the recorded A1 cell."""
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

    def missing(name, arm, idx, why, cause=CONSTRUCTION):
        L.append({"id": "%s:%s" % (p, name), "p": str(p), "tier": e["tier"], "class": e["class"], "arm": arm,
                  "name": name, "idx": idx, "missing": True, "missing_reason": why, "valid": False,
                  "state": NOT_COMPUTED, "not_computed_cause": cause, "not_computed_reason": why,
                  "exclusion_reasons": ["NOT_COMPUTED (%s): %s" % (cause, why)]})

    def controls_not_computed(why, cause=CONSTRUCTION):
        ctrl["status"] = "not_computed"
        ctrl["not_computed"] = {"cause": cause, "reason": why}
        ctrl["C-NOSCALE"] = [{"idx": k, "missing": True, "state": NOT_COMPUTED, "not_computed_cause": cause,
                              "not_computed_reason": why, "pass": None} for k in range(1, 21)]

    names_rest = ["A3"] + ["A4_%d" % k for k in range(1, 21)] + ["A5_%d" % k for k in range(1, 21)] + \
                 ["A6_%d" % k for k in range(22)]
    route = st.get("construction_route")
    a1src = S1.get(p)            # (route, analysis, calg, stage-1 record) or None
    stage_ok = not s2.get("error") and "lattices" in s2 and st.get("stage2_multable_equals_stage1") is True
    if st["base"] != "none" and not stage_ok:
        why_stage = ("STAGE CONSISTENCY: stage 2 on route %s raised: %s" % (route, s2.get("error")) if s2.get("error")
                     else "STAGE CONSISTENCY: stage-2 structure constants differ from stage 1 on route %s" % route)
    # ---- A1
    if a1src is None:
        if route == "R3":
            why_a1 = "PARI maximal-order computation raised under R1 and R2 (A1 not computed at an R3 prime)"
        else:
            why_a1 = "no PARI maximal order: " + "; ".join("%s %s -> %s" % (t["route"], t["call"], t.get("error") or t.get("outcome"))
                                                         for t in st.get("route_attempts", []))
        missing("A1", "A1", None, why_a1)
    elif st["base"] != "none" and not stage_ok and a1src[0] == route:
        st["a1_stage1_record_not_counted"] = {"route": a1src[0], "det_pari": a1src[3]["A1"]["det_pari"],
                                              "note": "stage-1 A1 values of a route whose stage 2 was inconsistent"}
        missing("A1", "A1", None, why_stage)
    else:
        r_a1, an1, calg1, s1a = a1src
        L.append(finish(lat_entry(p, e, "A1", "A1", None, "O0_basis_form",
                                  an1["basis_f"], 1, [[F(v) for v in row] for row in s1a["A1"]["gram"]],
                                  {"gram_nrd_unscaled": s1a["A1"]["gram_nrd_unscaled"], "algebra_route": r_a1,
                                   "algebra_call": s1a.get("call")}), an1, calg1, p))
    if st["base"] == "none":
        why = "no valid base order at this prime (%s)" % st.get("base_none_reason", "")
        for nm in names_rest:
            missing(nm, nm.split("_")[0], None, why)
        controls_not_computed(why)
        return
    if not stage_ok:
        for nm in names_rest:
            missing(nm, nm.split("_")[0], None, why_stage)
        controls_not_computed(why_stage)
        return
    calg_a = st["calg_a_pass"]
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
    ctrl["C-TRD"]["base_calg_pass"] = base_ent["calg_pass"]      # v2 tally input (state)

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
    # v2 tally inputs (state): C-CROSS = lattice instruments + index and trace-form-det instruments agree
    c["index_instruments_agree"] = F(rN["index_pari"]) == idx_py
    c["trace_form_det_instruments_agree"] = F(rN["trace_form_det_pari"]) == tf_det_py
    c["lattice_calg_pass"] = entN["calg_pass"]
    c["ccross_pass"] = entN["ccross_pass"] and c["index_instruments_agree"] and c["trace_form_det_instruments_agree"]
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
    calgP["base_valid"] = base_ent["valid"]   # v2: C-ALG and C-CROSS of the base (v1: C-ALG only)
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
                      "lattices_valid": near["C-NEAR-O0"]["valid"] and near["C-NEAR-P0"]["valid"],
                      # v2 tally inputs (state)
                      "lattices_ccross_pass": near["C-NEAR-O0"]["ccross_pass"] and near["C-NEAR-P0"]["ccross_pass"],
                      "lattices_calg_pass": near["C-NEAR-O0"]["calg_pass"] and near["C-NEAR-P0"]["calg_pass"]}
    ctrl["C-NEAR"]["pass"] = ctrl["C-NEAR"]["O0_ok"] and ctrl["C-NEAR"]["P0_ok"] and ctrl["C-NEAR"]["lattices_valid"]

    # ---- A4 / A5 / C-NOSCALE
    ctrl["C-NOSCALE"] = []
    Binv = inv(cols_to_mat(B))
    parents = {0: (B, 1, base_ent), 1: (PB, p, entP)}
    for k in range(1, 21):
        nm = "A4_%d" % k
        rI = recs.get(nm)
        if rI is None or rI.get("error"):
            why4 = (rI or {}).get("error", "no record")
            missing(nm, "A4", k, why4)
            missing("A5_%d" % k, "A5", k, "parent A4 ideal not computed")
            ctrl["C-NOSCALE"].append({"idx": k, "missing": True, "state": NOT_COMPUTED,
                                      "not_computed_cause": CONSTRUCTION,
                                      "not_computed_reason": "parent A4 ideal not computed: " + why4, "pass": None})
            continue
        anI = analyse_pari_lattice(rI, alg2, p)
        IB = anI["basis_f"]
        inI = span_checker(IB)
        idxI_py = abs(det(matmul(Binv, cols_to_mat(IB))))
        calgI = dict(common)
        calgI["d_I_subset_O"] = all(inB(x) for x in IB)
        calgI["d_OI_subset_I"] = all(inI(alg2.mul(o, x)) for o in B for x in IB)
        calgI["base_valid"] = base_ent["valid"]   # v2: C-ALG and C-CROSS of the base (v1: C-ALG only)
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
        cn["lattice_calg_pass"] = entI["calg_pass"]   # v2 tally input (state)
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
            missing(nm, "A6", k, (r6 or {}).get("error", "parent lattice not computed"))
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


# ----------------------------------------------------------------- counts and outcome (v2 tally_rule)
PRIMARY_ARMS = ["A1", "A2", "A3", "A4", "A5"]
PRIMARY_NAMES = ["A1", "A2", "A3"] + ["A4_%d" % k for k in range(1, 21)] + ["A5_%d" % k for k in range(1, 21)]
SUB_NAMES = ["A6_%d" % k for k in range(22)]
INDEX_NAMES = ["A3"] + ["A4_%d" % k for k in range(1, 21)]
CONTROL_NAMES = ["C-TRD", "C-NONMAX", "C-NEAR"] + ["C-NOSCALE_%d" % k for k in range(1, 21)]


def lattice_state(x):
    """(state, exclusion_classes) of a lattice record."""
    if x.get("missing"):
        return NOT_COMPUTED, []
    if x.get("valid"):
        return VALID, []
    cls = []
    if not x.get("calg_pass"):
        cls.append("C-ALG")
    if not x.get("ccross_pass") or any(r.startswith("C-CROSS") for r in x.get("exclusion_reasons", [])):
        cls.append("C-CROSS")
    return EXCLUDED, cls


def control_item(c, name, default_cause, default_reason):
    """State, verdict and codes of one planned control value. c is the per-prime controls record or None."""
    it = {"item": name, "state": None, "verdict": None, "codes": [], "exclusion_classes": [], "invalid": False}
    base = name.split("_")[0]
    rec = None
    if c is not None and c.get("status") == "computed":
        rec = c["C-NOSCALE"][int(name.split("_")[1]) - 1] if base == "C-NOSCALE" else c[base]
    elif c is not None and base == "C-NOSCALE" and c.get("C-NOSCALE"):
        rec = c["C-NOSCALE"][int(name.split("_")[1]) - 1]
    if rec is None or rec.get("missing"):
        nc = (rec or {}) if rec is not None else ((c or {}).get("not_computed") or {})
        cause = nc.get("not_computed_cause") or nc.get("cause") or default_cause
        reason = nc.get("not_computed_reason") or nc.get("reason") or default_reason
        it.update({"state": NOT_COMPUTED, "cause": cause, "reason": reason,
                   "codes": ["F-INFRA" if cause == INFRASTRUCTURE else "INCONCLUSIVE-CONSTRUCTION"]})
        return it
    if base == "C-TRD":
        cross, calg = rec["ccross_pass"], rec["base_calg_pass"]
        it["invalid"] = cross and not rec["ratio_ok"]
        ok = rec["ratio_ok"] and rec["R_ne_1"]
        why = "ratio %s (expected 16), R_T %s" % (rec["ratio_detT_over_detA"], rec["R_T"])
    elif base == "C-NONMAX":
        cross, calg = rec["ccross_pass"], rec["lattice_calg_pass"]
        it["invalid"] = cross and not (rec["ratio_ok"] and rec["index_ok"])
        ok = rec["index_ok"] and rec["ratio_ok"] and rec["trace_form_det_ne_p2"] and rec["R_ne_1"]
        why = "index %s ratio %s R %s trace_det_ne_p2 %s" % (rec["index_python"], rec["ratio"], rec["R"],
                                                              rec["trace_form_det_ne_p2"])
    elif base == "C-NEAR":
        cross, calg = rec["lattices_ccross_pass"], rec["lattices_calg_pass"]
        ok = rec["O0_ok"] and rec["P0_ok"]
        why = "det_O0 %s (expected %s), det_P0 %s (expected %s)" % (rec["det_O0"], rec["det_O0_expected"],
                                                                    rec["det_P0"], rec["det_P0_expected"])
    else:
        cross, calg = rec["ccross_pass"], rec["lattice_calg_pass"]
        it["invalid"] = cross and not rec["ratio_ok"]
        ok = rec["ratio_ok"] and rec["R_ne_1"]
        why = "ratio %s (expected %s), R %s" % (rec["ratio"], rec["ratio_expected"], rec["R_unscaled"])
    if it["invalid"]:
        it["codes"].append("INVALID")
    if not (cross and calg):
        it["state"] = EXCLUDED
        if not calg:
            it["exclusion_classes"].append("C-ALG")
            it["codes"].append("INCONCLUSIVE-CONSTRUCTION")
        if not cross:
            it["exclusion_classes"].append("C-CROSS")
            it["codes"].append("F-INSTR")
        it["reason"] = "excluded: " + ",".join(it["exclusion_classes"])
        return it
    it["state"] = VALID
    it["verdict"] = "pass" if ok else "mismatch"
    if not ok:
        it["reason"] = why
        if base == "C-NEAR":
            it["codes"].append("INCONCLUSIVE-NEAR")
        elif not it["invalid"]:
            it["codes"].append("INCONCLUSIVE")   # must-fail control with the right ratio but R = 1 etc.
    return it


def tally(raw, note_path):
    L = raw["lattices"]
    byid = {x["id"]: x for x in L}
    ctl = {c["p"]: c for c in raw["controls"]}
    infra = raw["status"] == "infra_failure"
    default_cause = INFRASTRUCTURE if infra else CONSTRUCTION
    if infra:
        default_reason = "run stopped by infrastructure failure before this item: %s" % raw.get("infra_error")
    elif raw["status"] == "stopped_calg_b":
        default_reason = "run stopped by the C-ALG (b) stopping rule: %s" % raw.get("stop_reason")
    else:
        default_reason = "no record produced"
    primes = [e["p"] for e in raw["primes"]]
    slots = primes + ["UNKNOWN_PRIME_SLOT_%d" % i for i in range(len(primes), 22)]
    items = []
    # ---- set states on the lattice records themselves (every record, planned or auxiliary)
    for x in L:
        stt, cls = lattice_state(x)
        x["state"] = stt
        if stt == EXCLUDED:
            x["exclusion_classes"] = cls
    for ps in slots:
        for kind, names in (("primary", PRIMARY_NAMES), ("sub", SUB_NAMES), ("index", INDEX_NAMES)):
            for nm in names:
                lid = "%s:%s" % (ps, nm)
                x = byid.get(lid)
                arm = nm.split("_")[0]
                iid = lid if kind != "index" else "%s:M-INDEX:%s" % (ps, nm)
                it = {"id": iid, "lattice": lid, "p": ps, "kind": kind, "arm": arm if kind != "sub" else "A6",
                      "codes": [], "verdict": None}
                if x is None or x.get("missing"):
                    cause = (x or {}).get("not_computed_cause", default_cause)
                    reason = (x or {}).get("not_computed_reason", default_reason)
                    it.update({"state": NOT_COMPUTED, "cause": cause, "reason": reason,
                               "codes": ["F-INFRA" if cause == INFRASTRUCTURE else "INCONCLUSIVE-CONSTRUCTION"]})
                else:
                    stt, cls = lattice_state(x)
                    it["state"] = stt
                    if stt == EXCLUDED:
                        it["exclusion_classes"] = cls
                        it["reason"] = "; ".join(x["exclusion_reasons"])
                        if "C-ALG" in cls:
                            it["codes"].append("INCONCLUSIVE-INSTRUMENT" if arm == "A2" else "INCONCLUSIVE-CONSTRUCTION")
                        if "C-CROSS" in cls:
                            it["codes"].append("F-INSTR")
                    elif kind == "index":
                        ok = x["index_equals_n_squared"] is True
                        it["verdict"] = "pass" if ok else "mismatch"
                        if not ok:
                            it["codes"].append("F-NORM")
                            it["reason"] = "[O:I] %s != n(I)^2 with n(I) %s" % (x["index_python"], x["n_python"])
                    else:
                        rk = "R_sub" if kind == "sub" else "R"
                        ok = F(x[rk]) == 1
                        it["verdict"] = "pass" if ok else "mismatch"
                        it["value"] = x[rk]
                        if not ok:
                            it["codes"].append("F-SUB" if kind == "sub" else
                                               "INCONCLUSIVE-INSTRUMENT" if arm == "A2" else "F-NORM")
                            it["reason"] = "%s = %s" % (rk, x[rk])
                items.append(it)
        c = ctl.get(ps)
        for nm in CONTROL_NAMES:
            it = control_item(c, nm, default_cause, default_reason)
            it.update({"id": "%s:%s" % (ps, nm), "p": ps, "kind": "control", "arm": nm.split("_")[0]})
            items.append(it)

    # ---- counts
    def cnt(sel):
        xs = [i for i in items if sel(i)]
        return {"planned": len(xs), "computed_valid": sum(1 for i in xs if i["state"] == VALID),
                "computed_excluded": sum(1 for i in xs if i["state"] == EXCLUDED),
                "not_computed": sum(1 for i in xs if i["state"] == NOT_COMPUTED),
                "not_computed_construction": sum(1 for i in xs if i["state"] == NOT_COMPUTED and i["cause"] == CONSTRUCTION),
                "not_computed_infrastructure": sum(1 for i in xs if i["state"] == NOT_COMPUTED and i["cause"] == INFRASTRUCTURE),
                "pass": sum(1 for i in xs if i["verdict"] == "pass"),
                "mismatch": sum(1 for i in xs if i["verdict"] == "mismatch")}
    summ = {"primes_planned": 22, "primes_listed": len(primes)}
    summ["M_R"] = cnt(lambda i: i["kind"] == "primary")
    summ["M_R_by_arm"] = {a: cnt(lambda i, a=a: i["kind"] == "primary" and i["arm"] == a) for a in PRIMARY_ARMS}
    summ["M_SUB"] = cnt(lambda i: i["kind"] == "sub")
    summ["M_INDEX"] = cnt(lambda i: i["kind"] == "index")
    summ["controls"] = {k: cnt(lambda i, k=k: i["kind"] == "control" and i["arm"] == k)
                        for k in ("C-TRD", "C-NONMAX", "C-NEAR", "C-NOSCALE")}
    summ["controls_total"] = cnt(lambda i: i["kind"] == "control")
    summ["M_NORMHIT_hits"] = sum(1 for x in L if x["arm"] == "A4" and x.get("normhit") is True)
    summ["M_NORMHIT_misses"] = [x["id"] for x in L if x["arm"] == "A4" and x.get("normhit") is False]
    # M-CROSS (version-1 definition: computed lattice records failing C-CROSS, plus C-TRD / C-NOSCALE instrument
    # failures), plus v2 additions listed separately: A3/A4 index/n and C-NONMAX index/trace-det instruments
    cross_fail = [x["id"] for x in L if not x.get("missing") and x.get("ccross_pass") is False]
    ctrl_cross_fail = []
    extra_cross = [x["id"] for x in L if not x.get("missing") and x["arm"] in ("A3", "A4") and
                   not (x.get("index_instruments_agree") and x.get("n_instruments_agree"))]
    for c in raw["controls"]:
        if c.get("status") != "computed":
            continue
        if not c["C-TRD"]["ccross_pass"]:
            ctrl_cross_fail.append(c["p"] + ":C-TRD")
        if not (c["C-NONMAX"]["index_instruments_agree"] and c["C-NONMAX"]["trace_form_det_instruments_agree"]):
            extra_cross.append(c["p"] + ":C-NONMAX instruments")
        for cn in c["C-NOSCALE"]:
            if not cn.get("missing") and not cn["ccross_pass"]:
                ctrl_cross_fail.append("%s:C-NOSCALE_%d" % (c["p"], cn["idx"]))
    summ["M_CROSS_disagreements"] = len(cross_fail) + len(ctrl_cross_fail) + len(extra_cross)
    summ["M_CROSS_list"] = cross_fail + ctrl_cross_fail + extra_cross
    # route record (M-VALID)
    summ["route_record"] = {p: {"construction_route": s.get("construction_route"), "base": s.get("base"),
                                "routes_attempted": [t["route"] for t in s.get("route_attempts", [])],
                                "g_a2_pass": s.get("g_a2", {}).get("pass")}
                            for p, s in raw["prime_status"].items()}
    summ["fallback_primes"] = [p for p, s in raw["prime_status"].items() if s.get("fallback_used")]
    summ["non_R1_primes"] = [p for p, s in raw["prime_status"].items() if s.get("construction_route") != "R1"]
    summ["calg_a_fail_primes"] = [p for p, s in raw["prime_status"].items() if s.get("calg_a_pass") is False]
    summ["calg_b_fail_primes"] = [p for p, s in raw["prime_status"].items()
                                  if s.get("calg_b") and not s["calg_b"]["pass"]]
    summ["computed_lattice_records"] = sum(1 for x in L if not x.get("missing"))
    summ["excluded_lattice_records_by_class"] = {
        "C-ALG": sorted(x["id"] for x in L if x.get("state") == EXCLUDED and "C-ALG" in x.get("exclusion_classes", [])),
        "C-CROSS": sorted(x["id"] for x in L if x.get("state") == EXCLUDED and "C-CROSS" in x.get("exclusion_classes", []))}

    # ---- codes
    trig = set()
    for i in items:
        trig.update(i["codes"])
    if infra:
        trig.add("F-INFRA")
    if raw["status"] == "stopped_calg_b":
        trig.add("F-INSTR")
    if summ["M_CROSS_disagreements"]:
        trig.add("F-INSTR")
    # auxiliary (non-planned) lattice records failing C-ALG / C-CROSS (base, C-NONMAX, C-NEAR lattices) are
    # already reflected in the dependent planned items' states; C-CROSS failures there count in M-CROSS.
    blocking = [i for i in items if not (i["state"] == VALID and i["verdict"] == "pass")]
    note_ok = os.path.isfile(note_path)

    def allpass(kind):
        xs = [i for i in items if i["kind"] == kind]
        return all(i["state"] == VALID and i["verdict"] == "pass" for i in xs)
    s = {"S1": allpass("primary") and summ["M_R"]["planned"] == 946,
         "S2": allpass("sub") and summ["M_SUB"]["planned"] == 484,
         "S3": allpass("index") and summ["M_INDEX"]["planned"] == 462,
         "S4": allpass("control") and summ["controls_total"]["planned"] == 506,
         "S5": summ["M_CROSS_disagreements"] == 0,
         "S6_file_present": note_ok,
         "S7": "pending: evaluated by check.py after the driver"}
    umbrella = []
    for i in blocking:
        if not i["codes"]:   # defensive: a blocking item with no specific code
            i["codes"].append("INCONCLUSIVE")
            trig.add("INCONCLUSIVE")
    if not trig and not all(v is True for k, v in s.items() if k != "S7"):
        trig.add("INCONCLUSIVE")
        umbrella = [k for k, v in s.items() if k != "S7" and v is not True]
    trig = sorted(trig, key=PRECEDENCE.index)
    primary = trig[0] if trig else "SUCCESS"
    code_cells = {c: [i["id"] for i in blocking if c in i["codes"]] for c in PRECEDENCE}
    outcome = {"primary_code": primary, "triggered_codes": trig, "success_conditions": s,
               "primary_code_note": ("tally_rule of AMD-20260926-f9acf7; SUCCESS is conditional on S6 (note content, "
                                     "judged by review) and S7 (check.py exit 0); precedence: " + " > ".join(PRECEDENCE)),
               "blocking_cells": [i["id"] for i in blocking],
               "blocking_detail": [{k: i.get(k) for k in ("id", "kind", "state", "cause", "reason", "verdict", "codes",
                                                          "exclusion_classes") if i.get(k) is not None}
                                   for i in blocking],
               "cells_by_code": code_cells,
               "umbrella_INCONCLUSIVE_success_conditions": umbrella,
               "cells_not_computed": [i["id"] for i in items if i["kind"] != "control" and i["state"] == NOT_COMPUTED],
               "controls_not_computed": [i["id"] for i in items if i["kind"] == "control" and i["state"] == NOT_COMPUTED],
               "controls_failed": [i["id"] for i in items if i["kind"] == "control" and i["verdict"] == "mismatch"],
               "controls_excluded": [i["id"] for i in items if i["kind"] == "control" and i["state"] == EXCLUDED],
               "F_NORM_cells": [i["id"] for i in items if i["kind"] == "primary" and i["verdict"] == "mismatch" and i["arm"] != "A2"],
               "M_INDEX_mismatch_cells": [i["id"] for i in items if i["kind"] == "index" and i["verdict"] == "mismatch"],
               "F_SUB_cells": [i["id"] for i in items if i["kind"] == "sub" and i["verdict"] == "mismatch"],
               "D_STD_cells": [i["id"] for i in items if i["arm"] == "A2" and "INCONCLUSIVE-INSTRUMENT" in i["codes"]],
               "INVALID_cells": [i["id"] for i in items if i["kind"] == "control" and i.get("invalid")],
               "instrument_disagreement_cells": summ["M_CROSS_list"],
               "construction_exclusions": [i["id"] for i in items if i["state"] == EXCLUDED and
                                           "INCONCLUSIVE-CONSTRUCTION" in i["codes"]]}
    counts = {"summary": summ,
              "item_states": [{k: i.get(k) for k in ("id", "kind", "state", "cause", "verdict", "codes")
                               if i.get(k) is not None} for i in items]}
    # per arm per prime (version-1 style, report only)
    per = {}
    for i in items:
        if i["kind"] in ("primary", "sub"):
            d = per.setdefault(i["arm"], {}).setdefault(i["p"], {"planned": 0, "computed_valid": 0, "computed_excluded": 0,
                                                                 "not_computed": 0, "R_eq_1": 0, "R_ne_1": 0})
            d["planned"] += 1
            d[{VALID: "computed_valid", EXCLUDED: "computed_excluded", NOT_COMPUTED: "not_computed"}[i["state"]]] += 1
            if i["verdict"] == "pass":
                d["R_eq_1"] += 1
            elif i["verdict"] == "mismatch":
                d["R_ne_1"] += 1
    counts["per_arm_per_prime"] = per
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
