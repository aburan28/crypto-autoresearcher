"""INDEPENDENT re-verification of RUN-SMTH-71b1b0-001.

This file deliberately imports NOTHING from smth71b1b0_core.py or run_exp.py.
Every quantity it checks it recomputes from scratch, with different code and,
where it matters, a different algorithm:

  * factorisation is re-done by PURE TRIAL DIVISION up to sqrt(N) -- no
    Miller-Rabin, no Pollard rho -- on a deterministic subsample of every arm;
  * the elliptic curve, the factor base and the Semaev invariants are re-derived
    from the frozen seed by a second implementation;
  * every reported statistic (KS-DS-1, KS2-DS-1, TAIL-DS-1, DECAY-1, RATE-DS-1)
    is recomputed from the dumped largest-prime-factor arrays by a second
    implementation and compared to raw-result.json.

Usage: python3 verify_run.py --run-dir <dir> --out <verification-report.json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from array import array
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SPEC_PATH = os.path.join(REPO, "experiments", "EXP-SMTH-71b1b0", "specification.yaml")
SPEC_SHA256 = "e193a1966b264804b17976c1575f7bded858936005cab393f31763fef8a0e432"

MASTER_SEED = 4403196
DOMAIN = "EXP-SMTH-71b1b0/v1"
FB_SIZE = 512
N_PAIRS = 130816
BITS = (16, 20)
SUBSAMPLE_PER_ARM = 400

RHO_FROZEN = {2: 0.30684282, 3: 0.0486083883, 4: 0.00491092564,
              5: 0.000354724692, 6: 1.96496897e-05}
BANDS_FROZEN = {2: (0.038355, 2.454743), 3: (0.006076, 0.388867),
                4: (0.000613866, 0.039287405), 5: (4.43406e-05, 0.002837798)}


# --- independent deterministic bit source (same documented construction) ----
class Stream:
    """SHA256 counter-mode byte stream, re-implemented from the documented rule."""

    def __init__(self, label):
        self.key = ("%d:%s:%s" % (MASTER_SEED, DOMAIN, label)).encode()
        self.buf = bytearray()
        self.ctr = 0
        self.pos = 0

    def bits(self, nbits):
        nb = (nbits + 7) // 8
        while len(self.buf) - self.pos < nb:
            self.buf += hashlib.sha256(self.key + self.ctr.to_bytes(8, "big")).digest()
            self.ctr += 1
        blk = bytes(self.buf[self.pos:self.pos + nb])
        self.pos += nb
        if self.pos > (1 << 16):
            del self.buf[:self.pos]
            self.pos = 0
        return int.from_bytes(blk, "big") >> (nb * 8 - nbits)


def sqrt_mod(a, p):
    """Tonelli-Shanks. Returns r with r*r == a (mod p), or None."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        t = t * c % p
        r = r * b % p
    return r


# --- independent primality / trial division --------------------------------
def small_primes(limit):
    s = bytearray([1]) * (limit + 1)
    s[0:2] = b"\x00\x00"
    for i in range(2, isqrt(limit) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    return array("i", [i for i in range(limit + 1) if s[i]])


PRIMES_1M = small_primes(1 << 20)


def lpf_by_trial_division(n: int):
    """Largest prime factor by exhaustive trial division. No probabilistic test.

    Every integer in this run is at most p**2 < 2**40, so a prime list up to
    2**20 covers sqrt(n) and the surviving cofactor is prime by construction.
    """
    if n <= 1:
        return 1, True
    m = n
    largest = 1
    for p in PRIMES_1M:
        if p * p > m:
            break
        if m % p == 0:
            largest = p
            while m % p == 0:
                m //= p
    if m > 1:
        if m > (1 << 40):
            return largest, False
        largest = m
    return largest, True


def is_prime_slow(n):
    if n < 2:
        return False
    for p in PRIMES_1M:
        if p * p > n:
            break
        if n % p == 0:
            return n == p
    return True


def next_prime_slow(n):
    c = n if n % 2 else n + 1
    while not is_prime_slow(c):
        c += 2
    return c


# --- independent curve / factor base re-derivation --------------------------
def rederive(bits):
    st = Stream("prime:bits%d" % bits)
    while True:
        v = st.bits(bits - 1) | (1 << (bits - 2))
        p = next_prime_slow(v | (1 << (bits - 1)))
        if p.bit_length() == bits:
            break
    cs = Stream("curve:bits%d" % bits)
    nb = 8 * ((bits + 7) // 8) + 64
    while True:
        a = cs.bits(nb) % p
        b = cs.bits(nb) % p
        if (4 * pow(a, 3, p) + 27 * b * b) % p == 0:
            continue
        # exact point count, written differently: sum of Legendre symbols
        order = p + 1
        for x in range(p):
            rhs = (x * x * x + a * x + b) % p
            if rhs == 0:
                continue
            order += 1 if pow(rhs, (p - 1) // 2, p) == 1 else -1
        if order == p + 1:
            continue
        break
    fb = []
    x = 0
    while len(fb) < FB_SIZE:
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0 or pow(rhs, (p - 1) // 2, p) == 1:
            fb.append(x)
        x += 1
    return p, a, b, order, fb


def invariants(x1, x2, a, b, p):
    c2 = (x1 - x2) ** 2 % p
    c1 = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
    c0 = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    inv = pow(c2, p - 2, p)              # Fermat inverse, not pow(c2,-1,p)
    return (-c1) * inv % p, c0 * inv % p, (c2, c1, c0)


def s3_eval(x1, x2, z, a, b, p):
    return ((x1 - x2) ** 2 * z * z
            - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * z
            + ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2))) % p


# --- independent Dickman rho (different scheme: Euler/Heun, different step) --
def rho_table(h=1e-4, umax=60.0):
    per = int(round(1.0 / h))
    npts = int(round(umax / h)) + 1
    tab = array("d", bytes(8 * npts))
    for i in range(per + 1):
        tab[i] = 1.0
    for i in range(per, npts - 1):
        u = i * h
        j = i - per
        pred = tab[i] - h * tab[j] / u
        tab[i + 1] = tab[i] - 0.5 * h * (tab[j] / u + tab[j + 1] / (u + h))
        if tab[i + 1] < 0:
            tab[i + 1] = 0.0
    return tab, h, umax


def rho_of(tab, h, umax, u):
    if u <= 1.0:
        return 1.0
    if u >= umax:
        return 0.0
    x = u / h
    i = int(x)
    f = x - i
    return tab[i] * (1 - f) + tab[i + 1] * f


# --- independent statistics -------------------------------------------------
def ecdf_pairs(sorted_vals):
    """(value, cumulative count) at every distinct value."""
    out = []
    i = 0
    n = len(sorted_vals)
    while i < n:
        v = sorted_vals[i]
        while i < n and sorted_vals[i] == v:
            i += 1
        out.append((v, i))
    return out


def ks2(a_sorted, b_sorted):
    ea, eb = ecdf_pairs(a_sorted), ecdf_pairs(b_sorted)
    na, nb = len(a_sorted), len(b_sorted)
    vals = sorted(set([v for v, _ in ea]) | set([v for v, _ in eb]))
    ia = ib = 0
    ca = cb = 0
    d = 0.0
    for v in vals:
        while ia < len(ea) and ea[ia][0] <= v:
            ca = ea[ia][1]
            ia += 1
        while ib < len(eb) and eb[ib][0] <= v:
            cb = eb[ib][1]
            ib += 1
        d = max(d, abs(ca / na - cb / nb))
    return d


def ks1_dickman(sorted_vals, log_d, tab, h, umax):
    n = len(sorted_vals)
    d = 0.0
    for v, c in ecdf_pairs(sorted_vals):
        z = 0.0 if v <= 1 else math.log(v) / log_d
        f = 0.0 if z <= 0 else rho_of(tab, h, umax, 1.0 / z)
        d = max(d, abs(c / n - f))
    # also check the left limits
    prev = 0
    for v, c in ecdf_pairs(sorted_vals):
        z = 0.0 if v <= 1 else math.log(v) / log_d
        f = 0.0 if z <= 0 else rho_of(tab, h, umax, 1.0 / z)
        d = max(d, abs(prev / n - f))
        prev = c
    return d


def smooth_fraction(sorted_vals, D, u):
    c = 0
    for v in sorted_vals:
        if v ** u <= D:
            c += 1
        else:
            break
    return c / len(sorted_vals), c


def tail_fraction(sorted_vals, D):
    c = 0
    for v in reversed(sorted_vals):
        if v * v >= D:
            c += 1
        else:
            break
    return c / len(sorted_vals), c


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t0 = time.time()
    rep = {"verifier": "experiments/EXP-SMTH-71b1b0/implementation/verify_run.py",
           "independent_of": ["smth71b1b0_core.py", "run_exp.py"],
           "run_id": "RUN-SMTH-71b1b0-001", "checks": [], "started_utc":
           time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    def check(cid, ok, detail):
        rep["checks"].append({"id": cid, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + cid + ": " + detail, flush=True)

    h = hashlib.sha256()
    with open(SPEC_PATH, "rb") as fh:
        h.update(fh.read())
    check("V0-SPEC-DIGEST", h.hexdigest() == SPEC_SHA256,
          "specification.yaml sha256 = %s" % h.hexdigest())

    raw = json.load(open(os.path.join(args.run_dir, "raw-result.json")))
    if raw.get("status") != "completed":
        check("V0-STATUS", False, "raw-result status is %r; verification of a "
              "non-completed run is limited to the digest gate" % raw.get("status"))
        json.dump(rep, open(args.out, "w"), indent=2)
        return 1

    tabs = rho_table()
    ctx = {}
    for bits in BITS:
        p, a, b, order, fb = rederive(bits)
        rec = raw["construction"][str(bits)]
        ok = (p == rec["p"] and a == rec["a"] and b == rec["b"]
              and order == rec["curve_order"])
        check("V1-CURVE-bits%d" % bits, ok,
              "re-derived p=%d a=%d b=%d #E=%d ; recorded p=%d a=%d b=%d #E=%d"
              % (p, a, b, order, rec["p"], rec["a"], rec["b"], rec["curve_order"]))
        check("V1-ORDINARY-bits%d" % bits, order != p + 1,
              "trace = %d (0 would be supersingular); #E = %d, p+1 = %d"
              % (p + 1 - order, order, p + 1))
        fb_sha = hashlib.sha256("\n".join(str(x) for x in fb).encode()).hexdigest()
        check("V1-FACTORBASE-bits%d" % bits, fb_sha == rec["factor_base_sha256"],
              "re-derived factor base sha256 %s vs recorded %s (size %d)"
              % (fb_sha, rec["factor_base_sha256"], len(fb)))
        onc = all((x * x * x + a * x + b) % p == 0
                  or pow((x * x * x + a * x + b) % p, (p - 1) // 2, p) == 1 for x in fb)
        distinct_increasing = all(fb[i] < fb[i + 1] for i in range(len(fb) - 1))
        check("V1-FB-ONCURVE-bits%d" % bits, onc and distinct_increasing and len(fb) == FB_SIZE,
              "all 512 x are x-coordinates of points of E(F_p); strictly increasing "
              "and distinct = %s" % distinct_increasing)
        ctx[bits] = (p, a, b, fb)

    # ---- Semaev invariants: leading coefficient never zero, roots check ----
    for bits in BITS:
        p, a, b, fb = ctx[bits]
        st = Stream("verify:sem%d" % bits)
        bad_lead = 0
        root_checked = 0
        root_ok = 0
        sym_ok = 0
        sym_checked = 0
        for _ in range(200):
            i = st.bits(16) % FB_SIZE
            j = st.bits(16) % FB_SIZE
            if i == j:
                continue
            if i > j:
                i, j = j, i
            x1, x2 = fb[i], fb[j]
            e1, e2, (c2, c1, c0) = invariants(x1, x2, a, b, p)
            if c2 == 0:
                bad_lead += 1
            disc = (c1 * c1 - 4 * c2 * c0) % p
            if disc == 0 or pow(disc, (p - 1) // 2, p) == 1:
                # roots exist in F_p: verify S_3 vanishes and e_1, e_2 are their
                # sum and product
                r = sqrt_mod(disc, p)
                if r is not None:
                    inv2c2 = pow(2 * c2 % p, p - 2, p)
                    z1 = (-c1 + r) * inv2c2 % p
                    z2 = (-c1 - r) * inv2c2 % p
                    root_checked += 1
                    if s3_eval(x1, x2, z1, a, b, p) == 0 and s3_eval(x1, x2, z2, a, b, p) == 0:
                        root_ok += 1
                    sym_checked += 1
                    if (z1 + z2) % p == e1 and z1 * z2 % p == e2:
                        sym_ok += 1
        check("V2-LEADCOEF-bits%d" % bits, bad_lead == 0,
              "leading coefficient (x_i-x_j)^2 was nonzero on every sampled off-diagonal "
              "pair (%d zero)" % bad_lead)
        check("V2-ROOTS-bits%d" % bits, root_checked > 0 and root_ok == root_checked,
              "S_3(x_i,x_j,Z) vanishes at both recovered roots on %d/%d split pairs"
              % (root_ok, root_checked))
        check("V2-SYMFUN-bits%d" % bits, sym_checked > 0 and sym_ok == sym_checked,
              "(e_1,e_2) equals (root sum, root product) on %d/%d split pairs"
              % (sym_ok, sym_checked))

    # ---- arm dumps: digests, and independent LPF re-factorisation ----------
    arms = {}
    for arm, meta in raw["arms"].items():
        path = os.path.join(REPO, meta["lpf_dump_path"])
        hh = hashlib.sha256()
        with open(path, "rb") as fh:
            data = fh.read()
        hh.update(data)
        buf = array("q")
        buf.frombytes(data)
        arms[arm] = buf
        check("V3-DUMP-%s" % arm,
              hh.hexdigest() == meta["lpf_dump_sha256"] and len(buf) == N_PAIRS,
              "%d values, sha256 %s" % (len(buf), hh.hexdigest()))

    for arm, meta in raw["arms"].items():
        bits = meta["bits"]
        p, a, b, fb = ctx[bits]
        p2 = p * p
        buf = arms[arm]
        st = Stream("verify:sub:%s" % arm)
        idxs = sorted({st.bits(32) % N_PAIRS for _ in range(SUBSAMPLE_PER_ARM)})
        mismatch = []
        if arm.startswith("NULL"):
            ns = Stream("null:bits%d" % bits)
            nb = p2.bit_length()
            want = set(idxs)
            k = 0
            for t in range(N_PAIRS):
                while True:
                    v = ns.bits(nb)
                    if v < p2:
                        break
                if t in want:
                    lpf, ok = lpf_by_trial_division(v + 1)
                    if not ok or lpf != buf[t]:
                        mismatch.append((t, v + 1, lpf, buf[t]))
                    k += 1
        else:
            # rebuild the (i,j) enumeration independently and pick the sampled indices
            want = set(idxs)
            t = 0
            for i in range(FB_SIZE):
                for j in range(i + 1, FB_SIZE):
                    if t in want:
                        e1, e2, _ = invariants(fb[i], fb[j], a, b, p)
                        N = e1 * p + e2 + 1 if arm.startswith("TREAT-ENCB") \
                            else max(e1, 1) * max(e2, 1)
                        lpf, ok = lpf_by_trial_division(N)
                        if not ok or lpf != buf[t]:
                            mismatch.append((t, N, lpf, buf[t]))
                    t += 1
        check("V4-REFACTOR-%s" % arm, not mismatch,
              "%d records re-factored by pure trial division; %d mismatches%s"
              % (len(idxs), len(mismatch),
                 "" if not mismatch else " first=" + repr(mismatch[0])))

    # ---- pair count and enumeration order ---------------------------------
    cnt = 0
    bad = 0
    for i in range(FB_SIZE):
        for j in range(i + 1, FB_SIZE):
            cnt += 1
            if j <= i:
                bad += 1
    check("V5-PAIRCOUNT", cnt == N_PAIRS and bad == 0,
          "independent enumeration yields %d pairs, %d with j <= i (contract: 130816, 0)"
          % (cnt, bad))

    # ---- statistics recomputed independently ------------------------------
    tab, hh_, umax = tabs
    tol = 1e-12
    for bits in BITS:
        D = 2 ** (2 * bits)
        log_d = math.log(D)
        tv = sorted(v for v in arms["TREAT-ENCB.bits%d" % bits] if v > 0)
        nv = sorted(v for v in arms["NULL-UNIF-D.bits%d" % bits] if v > 0)
        ev = sorted(v for v in arms["CTRL-ENCA.bits%d" % bits] if v > 0)
        rec = raw["per_field_size"][str(bits)]

        v_ks2 = ks2(tv, nv)
        check("V6-KS2-bits%d" % bits, abs(v_ks2 - rec["KS2-DS-1"]["value"]) <= 1e-12,
              "independent KS2-DS-1 = %.10f, reported %.10f, threshold %s, "
              "independent verdict pass=%s"
              % (v_ks2, rec["KS2-DS-1"]["value"], rec["KS2-DS-1"]["threshold"],
                 v_ks2 <= rec["KS2-DS-1"]["threshold"]))

        v_ks2a = ks2(ev, nv)
        check("V6-ENCAPOWER-bits%d" % bits,
              abs(v_ks2a - rec["CTRL-ENCA-POWER"]["ks2_enca_vs_null"]) <= 1e-12,
              "independent ENC-A vs null KS2 = %.10f, reported %.10f; rejects=%s"
              % (v_ks2a, rec["CTRL-ENCA-POWER"]["ks2_enca_vs_null"],
                 v_ks2a > rec["KS2-DS-1"]["threshold"]))

        tt, _ = tail_fraction(tv, D)
        tn, _ = tail_fraction(nv, D)
        check("V6-TAIL-bits%d" % bits,
              abs((tt - tn) - rec["TAIL-DS-1"]["value_signed"]) <= 1e-12,
              "independent TAIL-DS-1 = %.10f (treatment %.10f, null %.10f), reported %.10f"
              % (tt - tn, tt, tn, rec["TAIL-DS-1"]["value_signed"]))

        f2, _ = smooth_fraction(tv, D, 2)
        f6, _ = smooth_fraction(tv, D, 6)
        ratio = f6 / f2 if f2 else None
        ok = (ratio is None and rec["DECAY-1"]["ratio"] is None) or \
             (ratio is not None and abs(ratio - rec["DECAY-1"]["ratio"]) <= 1e-12)
        check("V6-DECAY-bits%d" % bits, ok,
              "independent DECAY-1 ratio = %s (u6 %.8g / u2 %.8g), reported %s, "
              "threshold 0.006404, fires=%s"
              % (ratio, f6, f2, rec["DECAY-1"]["ratio"],
                 ratio is not None and ratio > 0.006404))

        rate_ok = True
        rate_detail = []
        for u in (2, 3, 4, 5):
            fu, _ = smooth_fraction(tv, D, u)
            repd = rec["RATE-DS-1"]["treatment"][str(u)]["observed_fraction"]
            rate_ok = rate_ok and abs(fu - repd) <= 1e-12
            lo, hi = BANDS_FROZEN[u]
            rate_detail.append("u=%d obs=%.8g band=[%.6g,%.6g] in=%s"
                               % (u, fu, lo, hi, lo <= fu <= hi))
        check("V6-RATE-bits%d" % bits, rate_ok,
              "independent RATE-DS-1: " + "; ".join(rate_detail))

        v_ks1 = ks1_dickman(tv, log_d, tab, hh_, umax)
        rep_ks1 = rec["KS-DS-1"]["value"]
        check("V6-KS1-bits%d" % bits, abs(v_ks1 - rep_ks1) <= 5e-4,
              "independent KS-DS-1 = %.8f (Heun, step 1e-4) vs reported %.8f "
              "(RK4, step 2e-5); agreement tolerance 5e-4 reflects the two "
              "different rho integrations, not the data" % (v_ks1, rep_ks1))

    rep["wall_seconds"] = round(time.time() - t0, 3)
    rep["all_pass"] = all(c["pass"] for c in rep["checks"])
    rep["n_checks"] = len(rep["checks"])
    json.dump(rep, open(args.out, "w"), indent=2)
    print("VERIFIER: %d checks, all_pass=%s, %.1fs"
          % (rep["n_checks"], rep["all_pass"], rep["wall_seconds"]), flush=True)
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
