"""EXP-SMTH-71b1b0 measurement core.

Direct B-smoothness measurement of the half-arity Semaev partial-map integer
invariants against a MEASURED null at the actual X, under the frozen contract
experiments/EXP-SMTH-71b1b0/specification.yaml
(sha256 e193a1966b264804b17976c1575f7bded858936005cab393f31763fef8a0e432).

This module implements ONLY what the frozen contract specifies.  Every constant
below is quoted from that contract; nothing here is tuned, and no threshold is
recomputed.  See implementation/implementation.md for the list of
implementation-level determinations the contract delegates.

Memory discipline (contract budget.bounded_working_set_required): every
per-record buffer is PREALLOCATED at its full, contract-declared size before a
single record is produced.  Peak resident memory is therefore fixed at process
start-up by the shard buffer, the preallocated arrays and the interpreter
baseline, and does not grow with records already produced.  That is the exact
property RUN-SMTH-PILOT-002 violated.

No network is used.  No socket module is imported anywhere in this file.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import signal
import sys
import time
from array import array
from math import gcd, isqrt

# ---------------------------------------------------------------------------
# FROZEN CONTRACT CONSTANTS.  Quoted, never derived at run time.
# ---------------------------------------------------------------------------
SPEC_SHA256 = "e193a1966b264804b17976c1575f7bded858936005cab393f31763fef8a0e432"
SPEC_BYTES = 17950

MASTER_SEED = 4403196                       # deterministic_construction.master_seed
DOMAIN = "EXP-SMTH-71b1b0/v1"               # deterministic_construction.domain
FIELD_SIZES_BITS = (16, 20)                 # deterministic_construction.field_sizes_bits
FB_SIZE = 512                               # measured_quantity.factor_base.size
N_PAIRS = 130816                            # enumeration.count_n = C(512,2)
ARITY_M = 4                                 # measured_quantity.arity

RUNGS_U = (2, 3, 4, 5)                      # metrics.rungs_u
DECAY_PROBE_U = 6                           # metrics.decay_probe_u
TAIL_Z = 0.5                                # metrics: fraction with z >= 0.5

KS_DS_1_THRESHOLD = 0.05                    # decision_rules.KS-DS-1.threshold
KS2_DS_1_THRESHOLD = 0.006373               # decision_rules.KS2-DS-1.threshold
TAIL_DS_1_THRESHOLD = 0.01                  # decision_rules.TAIL-DS-1.threshold
DECAY_1_THRESHOLD = 0.006404                # decision_rules.DECAY-1.threshold

# decision_rules.RATE-DS-1.rho_frozen / bands_frozen, quoted verbatim.
RHO_FROZEN = {
    2: 0.30684282, 3: 0.0486083883, 4: 0.00491092564,
    5: 0.000354724692, 6: 1.96496897e-05,
}
BANDS_FROZEN = {
    2: (0.038355, 2.454743),
    3: (0.006076, 0.388867),
    4: (0.000613866, 0.039287405),
    5: (4.43406e-05, 0.002837798),
}

# Arm identifiers.  Order below IS the production order and it enforces
# null_calibration.ordering_constraint: every null arm is drawn, factored and
# committed before any treatment record is factored.
NULL_ARMS = tuple(f"NULL-UNIF-D.bits{b}" for b in FIELD_SIZES_BITS)
TREATMENT_ARMS = tuple(f"TREAT-ENCB.bits{b}" for b in FIELD_SIZES_BITS)
ENCA_ARMS = tuple(f"CTRL-ENCA.bits{b}" for b in FIELD_SIZES_BITS)
ARM_ORDER = NULL_ARMS + TREATMENT_ARMS + ENCA_ARMS
TOTAL_RECORDS = len(ARM_ORDER) * N_PAIRS    # 784896

SHARD_RECORDS = 1024                        # shard buffer size, fixed


# ---------------------------------------------------------------------------
# Budget instrumentation
# ---------------------------------------------------------------------------
class BudgetStop(Exception):
    """Raised at a record boundary when a contract ceiling has been crossed."""


class Budget:
    """Hard budget enforcement.  A crossing stops at the NEXT RECORD BOUNDARY."""

    def __init__(self, wall_seconds, cpu_seconds, peak_rss_bytes, t0=None):
        self.wall_seconds = wall_seconds
        self.cpu_seconds = cpu_seconds
        self.peak_rss_bytes = peak_rss_bytes
        self.t0 = t0 if t0 is not None else time.time()
        self.stop_reason = None
        self._flag = False

    def install_alarm(self):
        def _handler(signum, frame):
            self._flag = True
            self.stop_reason = "wall_clock_ceiling (SIGALRM)"
        remaining = int(max(1, self.wall_seconds - (time.time() - self.t0)))
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(remaining)

    def flagged(self):
        return self._flag

    def check(self):
        """Full ceiling check.  Call at shard boundaries."""
        if self._flag:
            raise BudgetStop(self.stop_reason)
        wall = time.time() - self.t0
        if wall > self.wall_seconds:
            self.stop_reason = f"wall_clock_ceiling: {wall:.1f}s > {self.wall_seconds}s"
            raise BudgetStop(self.stop_reason)
        cpu = cpu_seconds_self_and_children()
        if cpu > self.cpu_seconds:
            self.stop_reason = f"cpu_ceiling: {cpu:.1f}s > {self.cpu_seconds}s"
            raise BudgetStop(self.stop_reason)
        rss = peak_rss_bytes()
        if rss > self.peak_rss_bytes:
            self.stop_reason = f"peak_rss_ceiling: {rss} > {self.peak_rss_bytes}"
            raise BudgetStop(self.stop_reason)


def peak_rss_bytes() -> int:
    """Peak resident set size of this process, in bytes (VmHWM, authoritative)."""
    try:
        with open("/proc/self/status", "r") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def current_rss_bytes() -> int:
    try:
        with open("/proc/self/statm", "r") as fh:
            return int(fh.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except OSError:
        return 0


def cpu_seconds_self_and_children() -> float:
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def apply_hard_rlimits(peak_rss_bytes_cap: int, cpu_seconds_cap: int) -> dict:
    """Kernel-enforced backstops.

    RLIMIT_AS caps the virtual address space.  Since RSS <= VA always, an AS cap
    at the contract's peak-RSS ceiling is a strictly conservative hard guarantee
    that peak RSS cannot cross that ceiling.
    """
    applied = {}
    try:
        resource.setrlimit(resource.RLIMIT_AS, (peak_rss_bytes_cap, peak_rss_bytes_cap))
        applied["RLIMIT_AS"] = peak_rss_bytes_cap
    except (ValueError, OSError) as exc:      # pragma: no cover
        applied["RLIMIT_AS_error"] = repr(exc)
    try:
        cpu = int(max(1, cpu_seconds_cap))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        applied["RLIMIT_CPU"] = cpu
    except (ValueError, OSError) as exc:      # pragma: no cover
        applied["RLIMIT_CPU_error"] = repr(exc)
    return applied


# ---------------------------------------------------------------------------
# Deterministic bit source
# ---------------------------------------------------------------------------
class DRBG:
    """SHA256 counter-mode deterministic byte stream.

    Key = "<master_seed>:<domain>:<label>".  Block i = SHA256(key || i as 8-byte
    big-endian).  This is the only source of randomness anywhere in this
    measurement; there is no call to os.urandom, random.SystemRandom, or the
    clock in any generative path.
    """

    def __init__(self, label: str, master_seed: int = MASTER_SEED, domain: str = DOMAIN):
        self.label = label
        self.key = f"{master_seed}:{domain}:{label}".encode()
        self._ctr = 0
        self._buf = b""
        self._off = 0
        self.bytes_drawn = 0

    def _refill(self):
        self._buf = hashlib.sha256(self.key + self._ctr.to_bytes(8, "big")).digest()
        self._ctr += 1
        self._off = 0

    def read(self, nbytes: int) -> bytes:
        out = bytearray()
        while len(out) < nbytes:
            if self._off >= len(self._buf):
                self._refill()
            take = min(nbytes - len(out), len(self._buf) - self._off)
            out += self._buf[self._off:self._off + take]
            self._off += take
        self.bytes_drawn += nbytes
        return bytes(out)

    def bits(self, nbits: int) -> int:
        nbytes = (nbits + 7) // 8
        v = int.from_bytes(self.read(nbytes), "big")
        return v >> (nbytes * 8 - nbits)


# ---------------------------------------------------------------------------
# Primality, factorisation, largest prime factor
# ---------------------------------------------------------------------------
def _sieve(limit: int) -> list:
    s = bytearray([1]) * (limit + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, isqrt(limit) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    return [i for i in range(limit + 1) if s[i]]


SMALL_PRIMES = _sieve(1000)                 # 168 primes; trial-division prefix
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin.  The base set (2..37) is a proven witness set
    for every n < 3.317e24; every integer factored here is < 2**40."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _brent(n: int) -> int:
    """Pollard-Brent rho.  Parameters are derived deterministically FROM n, so
    the factorisation of a given integer is reproducible bit-for-bit."""
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    seed = int.from_bytes(hashlib.sha256(b"brent:" + n.to_bytes(16, "big")).digest()[:8], "big")
    attempt = 0
    while True:
        s = seed ^ (attempt * 0x9E3779B97F4A7C15)
        y = 1 + (s % (n - 1))
        c = 1 + ((s >> 17) % (n - 1))
        attempt += 1
        m = 128
        g = r = q = 1
        x = ys = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
        if g == n:
            g = 1
            y = ys
            while g == 1:
                y = (y * y + c) % n
                g = gcd(abs(x - y), n)
        if g != n and g != 1:
            return g
        if attempt > 64:
            return 0            # give up -> caller records an INCOMPLETE record


def factor_complete(n: int):
    """COMPLETE factorisation (never trial-division-truncated).

    Returns (factors dict prime->exponent, complete flag).  `complete` is False
    only if the rho stage gives up, in which case the record is counted as an
    incomplete factorisation and is never counted as smooth or non-smooth.
    """
    fac = {}
    if n <= 0:
        return fac, False
    m = n
    for p in SMALL_PRIMES:
        if p * p > m:
            break
        if m % p == 0:
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            fac[p] = e
    if m == 1:
        return fac, True
    stack = [m]
    guard = 0
    while stack:
        guard += 1
        if guard > 512:
            return fac, False
        v = stack.pop()
        if v == 1:
            continue
        if is_prime(v):
            fac[v] = fac.get(v, 0) + 1
            continue
        d = _brent(v)
        if d in (0, 1, v):
            return fac, False
        stack.append(d)
        stack.append(v // d)
    return fac, True


def product_of(fac: dict) -> int:
    pr = 1
    for p, e in fac.items():
        pr *= p ** e
    return pr


# ---------------------------------------------------------------------------
# Curve, factor base, Semaev half-arity invariants
# ---------------------------------------------------------------------------
def next_prime(n: int) -> int:
    if n <= 2:
        return 2
    c = n if n % 2 else n + 1
    while not is_prime(c):
        c += 2
    return c


def derive_prime(bits: int) -> dict:
    """A prime p of bitlength EXACTLY `bits`, deterministic in
    (master_seed, domain, bits)."""
    drbg = DRBG(f"prime:bits{bits}")
    tries = 0
    while True:
        tries += 1
        v = drbg.bits(bits - 1) | (1 << (bits - 2))
        cand = v | (1 << (bits - 1))
        p = next_prime(cand)
        if p.bit_length() == bits:
            return {"p": p, "tries": tries, "seed_label": f"prime:bits{bits}"}


def count_points(p: int, a: int, b: int) -> int:
    """#E(F_p) by exact enumeration of x, using a quadratic-residue table.
    Toy scale only; exact, auditable, and independent of any library."""
    sq = bytearray(p)
    for y in range((p + 1) // 2):
        sq[y * y % p] = 1
    total = 1                                   # the point at infinity
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            total += 1
        elif sq[rhs]:
            total += 2
    return total


def derive_curve(bits: int) -> dict:
    """Deterministic ordinary curve over F_p, from (master_seed, domain, bits).

    E: y^2 = x^3 + a x + b, non-singular (4a^3+27b^2 != 0) and ORDINARY.  Over a
    prime field with p > 3 a curve is supersingular exactly when the trace
    t = p + 1 - #E is zero, so the ordinarity test is #E != p + 1 and it is
    exact, not probabilistic.
    """
    pinfo = derive_prime(bits)
    p = pinfo["p"]
    drbg = DRBG(f"curve:bits{bits}")
    t = 0
    rejected = []
    while True:
        t += 1
        a = drbg.bits(8 * ((bits + 7) // 8) + 64) % p
        b = drbg.bits(8 * ((bits + 7) // 8) + 64) % p
        if (4 * a * a * a + 27 * b * b) % p == 0:
            rejected.append({"t": t, "a": a, "b": b, "reason": "singular"})
            continue
        order = count_points(p, a, b)
        if order == p + 1:
            rejected.append({"t": t, "a": a, "b": b, "reason": "supersingular (trace 0)"})
            continue
        return {
            "bits": bits, "p": p, "a": a, "b": b,
            "curve_order": order, "trace": p + 1 - order,
            "ordinary": True, "candidate_index": t,
            "rejected_candidates": rejected,
            "prime_tries": pinfo["tries"],
        }


def build_factor_base(p: int, a: int, b: int, size: int) -> list:
    """frozen_deterministic_subset: the first `size` x-coordinates in F_p, in
    increasing integer order, that are x-coordinates of points of E(F_p)."""
    xs = []
    x = 0
    while len(xs) < size:
        if x >= p:
            raise RuntimeError("factor base exhausted the field")
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0 or pow(rhs, (p - 1) // 2, p) == 1:
            xs.append(x)
        x += 1
    return xs


def s3_coeffs(x1: int, x2: int, a: int, b: int, p: int):
    """S_3(x1, x2, Z) = c2 Z^2 + c1 Z + c0 over F_p."""
    c2 = (x1 - x2) ** 2 % p
    c1 = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
    c0 = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    return c2, c1, c0


def s3_invariants(x1: int, x2: int, a: int, b: int, p: int):
    """(e_1, e_2): the elementary symmetric functions of the root multiset of
    S_3(x1, x2, Z), each reduced to its representative in [0, p-1]."""
    c2, c1, c0 = s3_coeffs(x1, x2, a, b, p)
    inv = pow(c2, -1, p)                     # c2 = (x1-x2)^2 != 0 for x1 != x2
    e1 = (-c1) * inv % p
    e2 = c0 * inv % p
    return e1, e2


def enc_b(e1: int, e2: int, p: int) -> int:
    """ENC-B, the PRIMARY DECISION ENCODING: a bijection [0,p)^2 -> [1, p^2]."""
    return e1 * p + e2 + 1


def enc_a(e1: int, e2: int) -> int:
    """ENC-A, POWER CERTIFICATE ONLY, never a decision variable about HEUR-DS-1."""
    return max(e1, 1) * max(e2, 1)


# ---------------------------------------------------------------------------
# Dickman rho.  SECONDARY REFERENCE ONLY (null_calibration.dickman_status).
# ---------------------------------------------------------------------------
RHO_H = 2e-5
RHO_UMAX = 60.0
_RHO_PER = int(round(1.0 / RHO_H))
_RHO_NPTS = int(round(RHO_UMAX / RHO_H)) + 1


def build_rho_table() -> array:
    """RK4 integration of rho'(u) = -rho(u-1)/u from rho == 1 on [0,1], step
    2e-5 -- the provenance recorded in decision_rules.RATE-DS-1.rho_provenance."""
    tab = array("d", bytes(8 * _RHO_NPTS))
    for i in range(_RHO_PER + 1):
        tab[i] = 1.0
    h = RHO_H
    for i in range(_RHO_PER, _RHO_NPTS - 1):
        u = i * h
        j = i - _RHO_PER
        r0 = tab[j]
        r1 = tab[j + 1]
        rmid = 0.5 * (r0 + r1)
        k1 = -r0 / u
        k2 = -rmid / (u + 0.5 * h)
        k4 = -r1 / (u + h)
        nxt = tab[i] + (h / 6.0) * (k1 + 4.0 * k2 + k4)
        tab[i + 1] = nxt if nxt > 0.0 else 0.0
    return tab


def rho_at(tab: array, u: float) -> float:
    if u <= 1.0:
        return 1.0
    if u >= RHO_UMAX:
        return 0.0
    x = u / RHO_H
    i0 = int(x)
    f = x - i0
    return tab[i0] * (1.0 - f) + tab[i0 + 1] * f


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def ks_two_sample_int(a_sorted, b_sorted) -> float:
    """Exact two-sample Kolmogorov-Smirnov statistic.

    Computed on the sorted integer LPF values.  z = ln(LPF)/ln(D) is strictly
    increasing in LPF, so the statistic is identical to the one on z and no
    floating-point tie can perturb it.
    """
    na, nb = len(a_sorted), len(b_sorted)
    i = j = 0
    d = 0.0
    while i < na and j < nb:
        va, vb = a_sorted[i], b_sorted[j]
        v = va if va <= vb else vb
        while i < na and a_sorted[i] == v:
            i += 1
        while j < nb and b_sorted[j] == v:
            j += 1
        diff = abs(i / na - j / nb)
        if diff > d:
            d = diff
    if i < na:
        d = max(d, abs(1.0 - j / nb))
    if j < nb:
        d = max(d, abs(i / na - 1.0))
    return d


def ks_one_sample_vs_dickman(lpf_sorted, log_d: float, rho_tab: array) -> float:
    """sup_z |F_n(z) - rho(1/z)|, evaluated at every jump of F_n."""
    n = len(lpf_sorted)
    d = 0.0
    i = 0
    while i < n:
        v = lpf_sorted[i]
        j = i
        while j < n and lpf_sorted[j] == v:
            j += 1
        z = 0.0 if v <= 1 else math.log(v) / log_d
        f = 0.0 if z <= 0.0 else rho_at(rho_tab, 1.0 / z)
        below = i / n
        above = j / n
        if above - f > d:
            d = above - f
        if f - below > d:
            d = f - below
        i = j
    return d


# ---------------------------------------------------------------------------
# Arm production
# ---------------------------------------------------------------------------
def _pair_stream(fb):
    """enumeration.rule, verbatim: for i in range(512): for j in range(i+1, 512)."""
    n = len(fb)
    for i in range(n):
        xi = fb[i]
        for j in range(i + 1, n):
            yield i, j, xi, fb[j]


class ArmResult:
    __slots__ = ("arm", "bits", "count", "incomplete", "product_mismatch",
                 "lpf_sha256", "int_sha256", "min_int", "max_int",
                 "extra")

    def __init__(self):
        self.extra = {}


def produce_arm(arm: str, bits: int, ctx: dict, buf: array, budget: Budget,
                progress=None, limit: int = None) -> ArmResult:
    """Fill `buf` (preallocated, length N_PAIRS) with the largest prime factor of
    every record of `arm`, streaming, with a fixed-size shard buffer.

    Returns an ArmResult.  Raises BudgetStop at a record boundary if a ceiling
    is crossed.
    """
    p = ctx["p"]
    a = ctx["a"]
    b = ctx["b"]
    fb = ctx["fb"]
    p2 = p * p

    res = ArmResult()
    res.arm = arm
    res.bits = bits
    res.incomplete = 0
    res.product_mismatch = 0
    res.min_int = None
    res.max_int = None

    lpf_hash = hashlib.sha256()
    int_hash = hashlib.sha256()
    shard = []                                   # fixed-size shard buffer
    idx = 0
    n_target = N_PAIRS if limit is None else min(limit, N_PAIRS)

    if arm.startswith("NULL-UNIF-D"):
        drbg = DRBG(f"null:bits{bits}")
        nbits = p2.bit_length()
        rejections = 0

        def records():
            nonlocal rejections
            for _ in range(n_target):
                while True:
                    v = drbg.bits(nbits)
                    if v < p2:
                        break
                    rejections += 1
                yield None, None, v + 1
        src = records()
    elif arm.startswith("TREAT-ENCB"):
        def records():
            for i, j, xi, xj in _pair_stream(fb):
                e1, e2 = s3_invariants(xi, xj, a, b, p)
                yield i, j, enc_b(e1, e2, p)
        src = records()
        rejections = 0
    elif arm.startswith("CTRL-ENCA"):
        def records():
            for i, j, xi, xj in _pair_stream(fb):
                e1, e2 = s3_invariants(xi, xj, a, b, p)
                yield i, j, enc_a(e1, e2)
        src = records()
        rejections = 0
    else:                                        # pragma: no cover
        raise ValueError(f"unknown arm {arm}")

    pair_order_ok = True
    for i, j, N in src:
        if idx >= n_target:
            break
        if i is not None and not (0 <= i < j < FB_SIZE):
            pair_order_ok = False
        fac, complete = factor_complete(N)
        if not complete:
            res.incomplete += 1
            lpf = 0
        else:
            if product_of(fac) != N:
                res.product_mismatch += 1
            lpf = max(fac) if fac else 1
        buf[idx] = lpf
        shard.append((N, lpf))
        if res.min_int is None or N < res.min_int:
            res.min_int = N
        if res.max_int is None or N > res.max_int:
            res.max_int = N
        idx += 1
        if budget.flagged():
            budget.check()
        if len(shard) >= SHARD_RECORDS:
            for Nv, lv in shard:
                int_hash.update(b"%d\n" % Nv)
                lpf_hash.update(b"%d\n" % lv)
            shard.clear()
            budget.check()
            if progress is not None:
                progress(idx)
    for Nv, lv in shard:
        int_hash.update(b"%d\n" % Nv)
        lpf_hash.update(b"%d\n" % lv)
    shard.clear()
    if progress is not None:
        progress(idx)

    res.count = idx
    res.lpf_sha256 = lpf_hash.hexdigest()
    res.int_sha256 = int_hash.hexdigest()
    res.extra["pair_order_ok"] = pair_order_ok
    res.extra["null_rejection_draws"] = rejections
    return res


# ---------------------------------------------------------------------------
# Per-arm summary statistics
# ---------------------------------------------------------------------------
def arm_summary(lpf_sorted, n: int, D: int, log_d: float, rho_tab: array,
                incomplete: int) -> dict:
    """Every per-arm metric named in metrics.per_arm."""
    valid = [v for v in lpf_sorted if v > 0]     # v == 0 marks an incomplete record
    nv = len(valid)
    smooth = {}
    for u in list(RUNGS_U) + [DECAY_PROBE_U]:
        # LPF <= D**(1/u)  <=>  LPF**u <= D, exact in integers.
        c = 0
        for v in valid:
            if v ** u <= D:
                c += 1
            else:
                break                            # valid is sorted ascending
        smooth[u] = {"count": c, "fraction": c / nv if nv else None,
                     "Bsm_floor": int(round(math.floor(D ** (1.0 / u))))}
    tail_c = 0
    for v in reversed(valid):
        if v * v >= D:
            tail_c += 1
        else:
            break
    grid = [i / 1000.0 for i in range(1001)]
    cdf = []
    k = 0
    for g in grid:
        # count of z <= g  <=>  ln(LPF) <= g*ln(D)  <=>  LPF <= D**g
        thr = D ** g
        while k < nv and valid[k] <= thr:
            k += 1
        cdf.append(k / nv if nv else None)
    return {
        "n_records": n,
        "n_valid": nv,
        "incomplete_factorizations": incomplete,
        "smooth": {str(u): smooth[u] for u in smooth},
        "tail_fraction_z_ge_0.5": tail_c / nv if nv else None,
        "tail_count_z_ge_0.5": tail_c,
        "z_min": (math.log(valid[0]) / log_d) if nv and valid[0] > 1 else 0.0,
        "z_max": (math.log(valid[-1]) / log_d) if nv else None,
        "z_mean": (sum(math.log(v) for v in valid if v > 1) / log_d / nv) if nv else None,
        "z_cdf_grid_step": 0.001,
        "z_cdf_on_grid": cdf,
        "ks_vs_dickman": ks_one_sample_vs_dickman(valid, log_d, rho_tab),
    }


def rate_band_report(summary: dict) -> dict:
    """RATE-DS-1: observed smooth fraction against the FROZEN factor-8 bands."""
    out = {}
    for u in RUNGS_U:
        lo, hi = BANDS_FROZEN[u]
        obs = summary["smooth"][str(u)]["fraction"]
        out[str(u)] = {
            "observed_fraction": obs,
            "rho_frozen": RHO_FROZEN[u],
            "band_frozen": [lo, hi],
            "in_band": (obs is not None and lo <= obs <= hi),
        }
    out["all_rungs_in_band"] = all(v["in_band"] for k, v in out.items() if k != "all_rungs_in_band")
    return out


def decay_report(summary: dict) -> dict:
    """DECAY-1: ratio of the u=6 smooth fraction to the u=2 rung."""
    f6 = summary["smooth"][str(DECAY_PROBE_U)]["fraction"]
    f2 = summary["smooth"]["2"]["fraction"]
    ratio = None if (f2 in (None, 0)) else f6 / f2
    return {
        "statistic": "ratio of the u=6 smooth fraction to the u=2 rung, treatment arm",
        "fraction_u6": f6, "fraction_u2": f2, "ratio": ratio,
        "threshold": DECAY_1_THRESHOLD,
        "fires_if": "ratio > 0.006404",
        "fired": (ratio is not None and ratio > DECAY_1_THRESHOLD),
        "undefined": ratio is None,
    }
