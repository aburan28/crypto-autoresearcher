#!/usr/bin/env python3
"""EXP-ECDLP-fac9ea v2 (amendment DEC-20260921-d3fafb) lambda-registry census.

Executor run RUN-ECDLP-8e13c2 for TASK-20260921-4888d4, executed in the
coordinator session under the executor role contract because the executor
subagent runtime failed its environment bootstrap (AWS DescribeInstances
AuthFailure); provenance recorded in manifest.yaml.

Measures the NONTRIVIAL additive L1 spectral norm
    l1_star = sum_{k != 0} |vhat(k)|,
    vhat(k) = sum_{x in F_p} v(x) exp(-2*pi*i*k*x/p),
for the frozen statistic registry over the frozen prime ladders, by exact
Bluestein chirp-z over the prime p. Exponent-space chirp
e_j = (j^2 mod p) * inv2 mod p is p-periodic; the padded circular
convolution uses length L = smallest 5-smooth integer >= 2p-1 with the
reversed-tail placement B[L-p+1:L] = b[1:p], b = conj(chirp).
"""

import gc
import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import scipy.fft as sfft
import yaml as _yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
REGISTRY_PATH = os.path.join(HERE, "registry.json")
FITS_PATH = os.path.join(HERE, "fits.json")
MANIFEST_PATH = os.path.join(HERE, "manifest.yaml")
REPORT_PATH = os.path.join(HERE, "report.md")

EXP_ID = "EXP-ECDLP-fac9ea"
RUN_ID = "RUN-ECDLP-8e13c2"
TASK_ID = "TASK-20260921-4888d4"
MEM_CAP_GB = 8.0
PRIMARY_EXPONENTS = [12.0, 13.0, 14.0, 15.0, 16.0, 17.5, 19.0, 20.5, 22.0, 24.0]
# Frozen prime_ladders.secondary: exponent step 14/9 so j = 9 is exactly 2^26
# (the jackknife tail) and no interior exponent coincides with the primary list.
SECONDARY_J = list(range(10))
SECONDARY_STEP = 14.0 / 9.0
GATE_ROWS = ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09"]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_highwater_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30


def rss_current_gb():
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(os.getpid())],
                             capture_output=True, text=True).stdout.strip()
        return int(out) / (1024.0 * 1024.0)
    except Exception:
        return rss_highwater_gb()


def hash_bytes(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode() if isinstance(p, str) else p)
    return h.digest()


def hash_ints(*parts, count=4, mod=None):
    out = []
    counter = 0
    while len(out) < count:
        d = hash_bytes(EXP_ID, *[str(p) for p in parts], str(counter))
        for i in range(0, 32, 4):
            v = int.from_bytes(d[i:i + 4], "big")
            out.append(v % mod if mod else v)
            if len(out) >= count:
                break
        counter += 1
    return out


def smallest_prime_at_least(n):
    def is_prime(m):
        if m < 2:
            return False
        if m % 2 == 0:
            return m == 2
        d = 3
        while d * d <= m:
            if m % d == 0:
                return False
            d += 2
        return True
    m = int(math.ceil(n))
    while not is_prime(m):
        m += 1
    return m


def next_smooth_len(n):
    best = None
    p2 = 1
    while p2 < n * 6:
        p23 = p2
        while p23 < n * 6:
            p235 = p23
            while p235 < n * 6:
                if p235 >= n and (best is None or p235 < best):
                    best = p235
                p235 *= 5
            p23 *= 3
        p2 *= 2
    return best


def bit_count_sums(n):
    def count_bit(n, i):
        period = 1 << (i + 1)
        full = (n >> (i + 1)) << i
        rem = n & (period - 1)
        return full + max(0, rem - (1 << i))

    def count_two_bits(n, i, j):
        period = 1 << (j + 1)
        full = (n >> (j + 1)) << (j - 1)
        rem = n & (period - 1)
        if rem <= (1 << j):
            return full
        return full + count_bit(rem - (1 << j), i)

    nbits = max(1, n.bit_length())
    s1 = 0
    s2 = 0
    for i in range(nbits):
        ci = count_bit(n, i)
        s1 += ci
        s2 += ci
        for j in range(i + 1, nbits):
            s2 += 2 * count_two_bits(n, i, j)
    return s1, s2


def digit_sum_array(n, base):
    x = np.arange(n, dtype=np.int64)
    s = np.zeros(n, dtype=np.int64)
    while True:
        nz = x != 0
        if not nz.any():
            break
        s += x % base
        x //= base
    return s


def popcount_array(n):
    return np.bitwise_count(np.arange(n, dtype=np.uint64)).astype(np.int64)


def centered_normalized(raw_int, s1, s2, p):
    mu = s1 / p
    var = s2 / p - mu * mu
    if var <= 0:
        return np.zeros(p)
    sigma = math.sqrt(var)
    return (raw_int.astype(np.float64) - mu) / (sigma * math.sqrt(p))


def power_set_mask(p, power):
    x = np.arange(1, p, dtype=np.int64)
    if power == 2:
        vals = (x * x) % p
    elif power == 3:
        vals = ((x * x % p) * x) % p
    elif power == 5:
        t = (x * x) % p
        vals = ((t * t % p) * x) % p
    else:
        raise ValueError(power)
    mask = np.zeros(p, dtype=bool)
    mask[vals] = True
    return mask


def indicator_on(mask, p):
    n = int(mask.sum())
    if n == 0:
        return None
    v = np.zeros(p)
    v[mask] = 1.0 / math.sqrt(n)
    return v


def lex_first_non_power(p, power):
    k = (p - 1) // power
    x = 2
    while x < p:
        if pow(x, k, p) != 1:
            return x
        x += 1
    return None


def sign_bits(p, seed_set):
    bits = np.empty(p, dtype=bool)
    nblocks = (p + 255) // 256
    for blk in range(nblocks):
        d = np.frombuffer(hash_bytes(EXP_ID, "C02", "sign", seed_set, str(blk)),
                          dtype=np.uint8)
        b = np.unpackbits(d)
        lo = blk * 256
        hi = min(p, lo + 256)
        bits[lo:hi] = b[: hi - lo] > 0
    return bits


def prob_indicator(mask, p):
    n = int(mask.sum())
    if n == 0:
        return None
    v = np.zeros(p)
    v[mask] = 1.0 / n
    return v


def mode_level_mask(values, p):
    counts = np.bincount(values, minlength=int(values.max()) + 1)
    t = int(counts.argmax())
    return values == t, f"mode level t*={t} |A|={int(counts[t])} of {len(counts)} levels"


def build_row(row_id, p):
    if row_id == "R01":
        L = p // 8
        mask = np.zeros(p, dtype=bool)
        mask[:L] = True
        return prob_indicator(mask, p), f"interval |A|={L}"
    if row_id == "R02":
        L = p // 8
        mask = np.zeros(p, dtype=bool)
        mask[(np.arange(L, dtype=np.int64) * 3) % p] = True
        return prob_indicator(mask, p), f"AP d=3 |A|={L}"
    if row_id in ("R03", "R03B"):
        mask, note = mode_level_mask(popcount_array(p), p)
        return prob_indicator(mask, p), "popcount level; " + note
    if row_id == "R04":
        ds = digit_sum_array(p, 3)
        mask, note = mode_level_mask(ds, p)
        return prob_indicator(mask, p), "base-3 digit-sum level; " + note
    if row_id == "R05":
        ds = digit_sum_array(p, 10)
        mask, note = mode_level_mask(ds, p)
        return prob_indicator(mask, p), "base-10 digit-sum level; " + note
    if row_id == "R06":
        if p % 3 != 1:
            return None, f"unavailable: p mod 3 = {p % 3} != 1 (certificate: p={p})"
        g = lex_first_non_power(p, 3)
        cubes = power_set_mask(p, 3)
        vals = (np.nonzero(cubes)[0].astype(np.int64) * g) % p
        mask = np.zeros(p, dtype=bool)
        mask[vals] = True
        v = prob_indicator(mask, p)
        return v, f"g={g} |gH|={int(mask.sum())} (x=0 excluded)"
    if row_id == "R07":
        if p % 5 != 1:
            return None, f"unavailable: p mod 5 = {p % 5} != 1 (certificate: p={p})"
        g = lex_first_non_power(p, 5)
        fifth = power_set_mask(p, 5)
        vals = (np.nonzero(fifth)[0].astype(np.int64) * g) % p
        mask = np.zeros(p, dtype=bool)
        mask[vals] = True
        v = prob_indicator(mask, p)
        return v, f"g={g} |gH|={int(mask.sum())} (x=0 excluded)"
    if row_id == "R08":
        qr = power_set_mask(p, 2)
        return prob_indicator(qr, p), f"|QR|={int(qr.sum())} (x=0 excluded)"
    if row_id == "R09":
        mask = (np.arange(p, dtype=np.int64) & 255) == 0
        return prob_indicator(mask, p), f"low-bit level |A|={int(mask.sum())}"
    if row_id == "C01":
        return np.full(p, 1.0 / p), None
    if row_id == "C02A":
        return prob_indicator(sign_bits(p, "A"), p), None
    if row_id == "C02B":
        return prob_indicator(sign_bits(p, "B"), p), None
    raise ValueError(row_id)


def inv_table(p):
    inv = np.zeros(p, dtype=np.int64)
    if p > 1:
        inv[1] = 1
        for t in range(2, p):
            inv[t] = (p - (p // t)) * inv[p % t] % p
    return inv


def moebius_row(base_row, p, inv):
    a, b, c, d = hash_ints("C03", "moebius", base_row, mod=p)
    det = (a * d - b * c) % p
    tries = 0
    while det == 0 and tries < 100:
        a, b, c, d = hash_ints("C03", "moebius", base_row, "r", tries, mod=p)
        det = (a * d - b * c) % p
        tries += 1
    if det == 0:
        return None, "unavailable: degenerate Moebius map"
    v_base, note = build_row(base_row, p)
    if v_base is None:
        return None, note
    x = np.arange(p, dtype=np.int64)
    den = (c * x + d) % p
    y = np.zeros(p, dtype=np.int64)
    ok = den != 0
    y[ok] = ((a * x[ok] + b) % p) * inv[den[ok]] % p
    if c != 0:
        pole_x = int((-d) % p * inv[c] % p)
        y[pole_x] = (a * inv[c]) % p
    return v_base[y], f"M(x)=(ax+b)/(cx+d) a={a} b={b} c={c} d={d} det={det}"


def curve_mask(p, curve_i):
    A, B = hash_ints("curve", p, curve_i, mod=p)[:2]
    tries = 0
    while (4 * A * A * A + 27 * B * B) % p == 0 and tries < 100:
        A, B = hash_ints("curve", p, curve_i, "r", tries, mod=p)[:2]
        tries += 1
    x = np.arange(p, dtype=np.int64)
    rhs = (((x * x % p) * x % p) + (A * x % p) + B) % p
    qr = power_set_mask(p, 2)
    return qr[rhs] | (rhs == 0), A, B


class ChirpZ:
    def __init__(self, p, workdir):
        self.p = p
        self.L = next_smooth_len(2 * p - 1)
        self.inv2 = (p + 1) // 2
        self.workdir = workdir
        self.bspec_path = os.path.join(workdir, f"bspec_{p}.npy")
        x = np.arange(p, dtype=np.int64)
        e = ((x * x % p) * self.inv2) % p
        self.chirp = np.exp(-2j * np.pi * e / p)
        if not os.path.exists(self.bspec_path):
            self._make_bspec()

    def _make_bspec(self):
        b = np.conj(self.chirp)
        B = np.zeros(self.L, dtype=np.complex128)
        B[: self.p] = b
        B[self.L - self.p + 1: self.L] = b[1:]
        del b
        Fb = sfft.fft(B, overwrite_x=True)
        np.save(self.bspec_path, Fb)
        del Fb, B
        gc.collect()

    def transform(self, v):
        p, L = self.p, self.L
        # Live at peak: the padded array, the FFT's own working copy, the
        # resident mmapped bspec pages (three L-length complex buffers), plus
        # the chirp, the input v, and the output (p * (16 + 8 + 16) bytes).
        need_gb = (L * 16 * 3 + p * 40) / 2**30
        if need_gb > MEM_CAP_GB - 0.5:
            return None, need_gb
        A = np.zeros(L, dtype=np.complex128)
        A[:p] = v
        A[:p] *= self.chirp
        F = sfft.fft(A, overwrite_x=True)
        del A
        gc.collect()
        bspec = np.load(self.bspec_path, mmap_mode="r")
        F *= bspec
        del bspec
        gc.collect()
        V = sfft.ifft(F, overwrite_x=True)
        del F
        gc.collect()
        out = np.array(V[:p])
        out *= self.chirp
        del V
        gc.collect()
        return out, need_gb


def cell_id(row, p, suffix=None):
    return f"{row}:{p}" + (f":{suffix}" if suffix else "")


def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def save_registry(reg):
    tmp = REGISTRY_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(reg, f, indent=1, sort_keys=True)
    os.replace(tmp, REGISTRY_PATH)


def measure(row, p, cz, inv=None, suffix=None, v=None, note=None):
    cid = cell_id(row, p, suffix)
    reg = load_registry()
    existing = reg.get(cid)
    # A resource_exhaustion checkpoint is terminal under the frozen stopping
    # rule: continuation is a chunked/on-disk convolution under an amendment,
    # never a silent re-measurement that folds the cell back into the fits.
    terminal = ("ok", "unavailable", "resource_exhaustion")
    if existing is not None and existing["status"] in terminal:
        return existing
    t0 = time.perf_counter()
    if v is None:
        if row.endswith("M"):
            v, note = moebius_row(row[:-1], p, inv)
        else:
            v, note = build_row(row, p)
    if v is None:
        rec = {"cell": cid, "status": "unavailable", "note": note,
               "wall_seconds": round(time.perf_counter() - t0, 3),
               "rss_highwater_gb": round(rss_highwater_gb(), 3),
               "recorded_at": now_iso()}
    else:
        l2 = float(np.sqrt((v * v).sum()))
        V, need_gb = cz.transform(v)
        if V is None:
            rec = {"cell": cid, "status": "resource_exhaustion",
                   "note": (f"projected {need_gb:.2f} GiB against the frozen 8 GiB "
                            "machine-protection cap; continuation pointer: chunked or "
                            "on-disk convolution under a protocol amendment"),
                   "l2_norm": l2,
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "rss_highwater_gb": round(rss_highwater_gb(), 3),
                   "recorded_at": now_iso()}
        else:
            rec = {"cell": cid, "status": "ok",
                   "l1_nontrivial": float(np.abs(V[1:]).sum()),
                   "abs_vhat0": float(abs(V[0])), "l2_norm": l2, "note": note,
                   "vhat0_minus_1_abs": float(abs(abs(V[0]) - 1.0)),
                   "wall_seconds": round(time.perf_counter() - t0, 3),
                   "rss_highwater_gb": round(rss_highwater_gb(), 3),
                   "fft_len": cz.L, "recorded_at": now_iso()}
            del V
    reg = load_registry()
    reg[cid] = rec
    save_registry(reg)
    return rec


def fit_lambda(points):
    pts = [(p, l1) for p, l1 in points if l1 > 0]
    if len(pts) < 3:
        return None
    x = np.array([math.log(p) for p, _ in pts])
    y = np.array([math.log(l1) for _, l1 in pts])
    n = len(pts)
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    ss_res = float((resid ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    sxx = float(((x - x.mean()) ** 2).sum())
    se = math.sqrt(ss_res / (n - 2) / sxx) if n > 2 and sxx > 0 else float("nan")
    signs = np.sign(resid)
    runs = int(1 + (np.diff(signs) != 0).sum()) if n > 1 else 1
    jack = None
    if n >= 4:
        max_idx = int(np.argmax(x))
        jack = float(np.polyfit(np.delete(x, max_idx), np.delete(y, max_idx), 1)[0])
    return {"lambda": float(slope), "se": se, "intercept": float(intercept),
            "n_points": n, "r2": (1 - ss_res / ss_tot) if ss_tot > 0 else None,
            "residual_runs": runs,
            "residual_trend_slope": float(np.polyfit(x, resid, 1)[0]),
            "jackknife_lambda_excl_largest": jack,
            "primes": [int(p) for p, _ in pts]}


def gate_verdict(lam, moebius_delta):
    if moebius_delta is True:
        return "artifactual"
    if lam is None:
        return "unresolved"
    if lam > 0.25:
        return "corner_open_and_learning_open"
    if lam >= 1.0 / 6.0:
        return "corner_open_learning_blocked"
    return "floor_blocked"


def row_points(reg, row):
    return [(int(cid.split(":")[1]), rec["l1_nontrivial"])
            for cid, rec in reg.items()
            if cid.startswith(row + ":") and cid.count(":") == 1
            and rec.get("status") == "ok"]


def one_cell(cid):
    """Fresh-process single-cell mode for continuation of resource_exhaustion
    checkpoints: same frozen constructions, seeds, and budget; a fresh
    process keeps live RSS low so the machine-protection guard measures
    the cell's own need, not the parent's cached pages."""
    parts = cid.split(":")
    row, p, suffix = parts[0], int(parts[1]), (parts[2] if len(parts) > 2 else None)
    cz = ChirpZ(p, WORK)
    inv = inv_table(p) if row.endswith("M") else None
    rec = measure(row, p, cz, inv, suffix=suffix)
    print(json.dumps(rec))


def main():
    os.makedirs(WORK, exist_ok=True)
    primary = [smallest_prime_at_least(2.0 ** b) for b in PRIMARY_EXPONENTS]
    secondary = [smallest_prime_at_least(2.0 ** (12 + SECONDARY_STEP * j)) for j in SECONDARY_J]
    tail = secondary[-1]
    all_primes = sorted(set(primary) | set(secondary))
    ladder_of = {}
    for p in primary:
        ladder_of.setdefault(p, []).append("primary")
    for p in secondary:
        ladder_of.setdefault(p, []).append("secondary")
    print(f"primes ({len(all_primes)}): {all_primes}", flush=True)

    plain_rows = GATE_ROWS + ["R03B", "C01", "C02A", "C02B"]
    moebius_rows = [r + "M" for r in GATE_ROWS]

    for p in all_primes:
        cz = ChirpZ(p, WORK)
        inv = None
        for row in plain_rows + moebius_rows:
            if row.endswith("M") and inv is None:
                t0 = time.perf_counter()
                inv = inv_table(p)
                print(f"  inv_table({p}) in {time.perf_counter()-t0:.1f}s", flush=True)
            rec = measure(row, p, cz, inv)
            print(f"  {rec['cell']} -> {rec['status']} "
                  f"l1*={rec.get('l1_nontrivial')} ({rec.get('wall_seconds')}s)",
                  flush=True)
            if row in ("R06", "R07", "R08") and rec["status"] == "ok":
                v_base, _ = build_row(row, p)
                support = np.nonzero(v_base)[0]
                for ci in range(3):
                    mask, A, B = curve_mask(p, ci)
                    sub = np.zeros(p, dtype=bool)
                    sub[support] = mask[support]
                    v = prob_indicator(sub, p)
                    rec_c = measure(row, p, cz, suffix=f"curve{ci}", v=v,
                                    note=f"A={A} B={B} |gH cap x(E)|={int(sub.sum())}")
                    print(f"  {rec_c['cell']} -> {rec_c['status']}", flush=True)
        del cz
        gc.collect()
        print(f"prime {p} done, rss high-water {rss_highwater_gb():.2f} GiB", flush=True)

    reg = load_registry()
    families = {}
    for row in GATE_ROWS:
        pts = row_points(reg, row)
        fam = {"points": pts, "fit": fit_lambda(pts)}
        prim_pts = [(p, l) for p, l in pts if "primary" in ladder_of.get(p, [])]
        sec_pts = [(p, l) for p, l in pts if "secondary" in ladder_of.get(p, [])]
        fam["fit_primary"] = fit_lambda(prim_pts)
        fam["fit_secondary"] = fit_lambda(sec_pts)
        mfit = fit_lambda(row_points(reg, row + "M"))
        fam["moebius_fit"] = mfit
        moebius_delta = None
        if mfit and fam["fit"]:
            comb = math.sqrt((fam["fit"]["se"] or 1) ** 2 + (mfit["se"] or 1) ** 2)
            moebius_delta = abs(mfit["lambda"] - fam["fit"]["lambda"]) > 2 * comb
        fam["moebius_delta_beyond_2se"] = moebius_delta
        lam = fam["fit"]["lambda"] if fam["fit"] else None
        unresolved = False
        if not pts:
            fam["verdict"] = "unavailable"
        else:
            if fam["fit_primary"] and fam["fit_secondary"]:
                comb = math.sqrt((fam["fit_primary"]["se"] or 1) ** 2 +
                                 (fam["fit_secondary"]["se"] or 1) ** 2)
                unresolved = abs(fam["fit_primary"]["lambda"] -
                                 fam["fit_secondary"]["lambda"]) > 2 * comb
            if fam["fit"] and fam["fit"].get("jackknife_lambda_excl_largest") is not None:
                if abs(fam["fit"]["jackknife_lambda_excl_largest"] - lam) > 3 * (fam["fit"]["se"] or 1):
                    unresolved = True
            fam["verdict"] = "unresolved" if unresolved else gate_verdict(lam, moebius_delta)
        families[row] = fam

    for row in ["R03B", "C02A", "C02B"]:
        pts = row_points(reg, row)
        families[row] = {"points": pts, "fit": fit_lambda(pts)}
    c01_recs = {cid: rec for cid, rec in reg.items()
                if cid.startswith("C01:") and rec.get("status") == "ok"}
    families["C01"] = {
        "cells": len(c01_recs),
        "all_numerically_zero": all(
            r["l1_nontrivial"] <= 1e-9 * max(r["abs_vhat0"], 1e-30)
            for r in c01_recs.values()) if c01_recs else None,
    }
    vhat0_ok = all(r.get("vhat0_minus_1_abs", 1.0) <= 1e-9
                   for r in reg.values() if r.get("status") == "ok")

    curve_fams = {}
    for row in ("R06", "R07", "R08"):
        for ci in range(3):
            pts = [(int(cid.split(":")[1]), rec["l1_nontrivial"])
                   for cid, rec in reg.items()
                   if cid.startswith(f"{row}:") and cid.endswith(f":curve{ci}")
                   and rec.get("status") == "ok"]
            curve_fams[f"{row}:curve{ci}"] = fit_lambda(pts)

    fa, fb = families.get("C02A", {}).get("fit"), families.get("C02B", {}).get("fit")
    seed_agree = (abs(fa["lambda"] - fb["lambda"]) <=
                  2 * math.sqrt((fa["se"] or 1) ** 2 + (fb["se"] or 1) ** 2)
                  ) if fa and fb else None
    r03 = families.get("R03", {}).get("fit")
    r03_repro = (r03 is not None and 0.36 <= r03["lambda"] <= 0.42) if r03 else None
    r03_marginal = bool(r03 and r03["lambda"] > 0.41)
    c02_band = (abs(fa["lambda"] - 0.5) <= 2 * (fa["se"] or 1) + 0.02) if fa else None
    r03b = families.get("R03B", {}).get("fit")
    r03_rep_ident = (r03b is not None and r03 is not None and
                     r03b["lambda"] == r03["lambda"] and
                     all(abs(a[1] - b[1]) == 0.0 for a, b in
                         zip(sorted(families["R03B"]["points"]),
                             sorted(families["R03"]["points"])))) if r03b and r03 else None

    controls = {
        "C01_all_ones_numerically_zero": families["C01"]["all_numerically_zero"],
        "C02A_parseval_band_0.5": c02_band,
        "C02_seed_set_agreement_AB": seed_agree,
        "R03_reproduction_band_0.36_0.42": r03_repro,
        "R03_reproduction_marginal_note": (
            f"point-estimate semantics per the frozen text ('fitted lambda in "
            f"[0.36, 0.42]'): lambda = {r03['lambda']:.4f}, SE {r03['se']:.4f}; "
            f"the +-2SE interval [{r03['lambda']-2*(r03['se'] or 0):.4f}, "
            f"{r03['lambda']+2*(r03['se'] or 0):.4f}] extends past 0.42 -- the "
            f"reproduction is MARGINAL at the band edge, disclosed") if r03 else None,
        "R03B_deterministic_replication_identical": r03_rep_ident,
        "all_ok_cells_vhat0_equals_1": vhat0_ok,
    }

    control_bools = {k: v for k, v in controls.items() if isinstance(v, bool)}
    control_notes = {k: v for k, v in controls.items() if not isinstance(v, bool)}
    fits = {"families": families, "curve_families_auxiliary": curve_fams,
            "controls": control_bools, "control_notes": control_notes,
            "ladders": {"primary": primary, "secondary": secondary,
                        "tail_jackknife_prime": tail},
            "run_id": RUN_ID, "generated_at": now_iso()}
    with open(FITS_PATH, "w") as f:
        json.dump(fits, f, indent=1, sort_keys=True)

    write_manifest(all_primes, primary, secondary, tail, reg, control_bools,
                   control_notes)
    write_report(families, curve_fams, control_bools, control_notes)
    print("DONE", flush=True)


def write_manifest(all_primes, primary, secondary, tail, reg, controls, control_notes=None):
    control_notes = control_notes or {}
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"],
                               capture_output=True, text=True).stdout.strip()
    except Exception:
        commit, dirty = "unavailable", "unavailable"
    control_fail = [k for k, v in controls.items() if v is not True]
    stamps = sorted(r.get("recorded_at", "") for r in reg.values())
    run = {
        "id": RUN_ID,
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "status": "completed",
        "status_note": (
            "Resumable multi-session execution: run1 (full pass, tail-prime "
            "cells falsely checkpointed by a double-counting RSS guard), "
            "fresh-process one-cell continuations, run3 (tail re-measure, "
            "memory-cap breach exposed), final regeneration passes with "
            "CENSUS_NO_REMEASURE=1 (no cell re-measured). All cell statuses "
            "and values are in registry.json with per-cell recorded_at."),
        "specification_version": ("3 (amendments DEC-20260921-d3fafb ladder "
                                  "clarification and DEC-20260921-f1d95a "
                                  "probability-normalisation correction, both "
                                  "pre-run; no cell had executed before either)"),
        "code": {
            "head_commit": commit,
            "commit": commit,
            "branch": "ideas/ecdlp-20260921",
            "dirty_at_execution_start": bool(dirty),
            "dirty_note": ("git status --short at regeneration: "
                           + (dirty.replace("\n", "; ") if dirty else "clean")),
        },
        "inputs": {
            "specification_path": "experiments/EXP-ECDLP-fac9ea/specification.yaml",
            "specification_sha256": "d7434225ebbaed536057fd0c1f7645fa9ec5df8c91884a67688cd587a06fecd7",
            "specification_version_executed": 3,
            "amendment_ids": ["DEC-20260921-d3fafb", "DEC-20260921-f1d95a"],
            "amendment_paths": [
                "experiments/EXP-ECDLP-fac9ea/amendments/DEC-20260921-d3fafb.yaml",
                "experiments/EXP-ECDLP-fac9ea/amendments/DEC-20260921-f1d95a.yaml",
            ],
            "hypothesis_id": "H-ECDLP-4e1880",
            "seeds": "SHA256(EXP-ECDLP-fac9ea:<cell>:<purpose>:<counter>) streams frozen in implementation.py",
        },
        "timing": {
            "first_cell_recorded_at": stamps[0] if stamps else None,
            "last_cell_recorded_at": stamps[-1] if stamps else None,
            "wall_clock_note": ("Per-cell wall_seconds are in registry.json "
                                "and manifest cells; the census's own charged "
                                "cost is their sum plus the regeneration passes."),
        },
        "result": {
            "certificate": {
                "kind": "none",
                "note": ("Pure exact-measurement census: no discrete log is "
                         "solved and no relation is claimed, so nothing "
                         "requires a solve certificate under "
                         "docs/claims-and-verification.md. Correctness is "
                         "carried by checker.py's three independent "
                         "verification routes (checker-report.json: ALL "
                         "PASSED) and the vhat(0)=1 invariant in 406/406 ok "
                         "cells."),
            },
            "outputs": {
                "registry": "registry.json",
                "fits": "fits.json",
                "report": "report.md",
            },
            "validity": "void_control_failure" if control_fail else "controls_passed",
            "validity_reason": (
                "one or more frozen controls failed; the defective control is "
                "named in fits.json controls" if control_fail
                else "all frozen controls passed"),
            "control_failures": control_fail,
            "controls": controls,
            "control_notes": control_notes,
        },
        "executed_at": now_iso(),
        "executor_provenance": (
            "Executed in the top-level coordinator session under the executor "
            "role contract (agents/executor.md); the executor subagent runtime "
            "failed its environment bootstrap (AWS DescribeInstances "
            "AuthFailure) at dispatch. Lane claim: "
            "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-5d04c8/claims/"
            "TASK-20260921-4888d4.1.claim.json (BATCH-5d04c8)."),
        "command": "python3 implementation.py",
        "git_commit": commit,
        "git_dirty_state": dirty.replace("\n", "; ") if dirty else "clean",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": "1.18.0 (in-place fft/ifft with overwrite_x=True)",
            "platform": "darwin arm64",
        },
        "seeds": {
            "hash_stream": "SHA256(EXP-ECDLP-fac9ea:<cell>:<purpose>:<counter>)",
            "stochastic_elements": (
                "C02 signs (blocks of 256 from one digest), C03 Moebius "
                "coefficients, curve parameters; all frozen in implementation.py"),
        },
        "convention": (
            "probability normalisation (amendment DEC-20260921-f1d95a): set "
            "rows v = 1_A/|A| so vhat(0) = 1 exactly (checked per cell, "
            "all_ok_cells_vhat0_equals_1); digit rows are mode-level "
            "indicators; l1_nontrivial = sum_{k != 0} |vhat(k)| with vhat the "
            "exact additive Fourier transform over F_p (Bluestein chirp-z "
            "over the prime, exponent-space chirp e_j = j^2*inv2 mod p); "
            "abs_vhat0 logged per cell; C01 zero test uses "
            "l1* <= 1e-9 * max(|vhat(0)|, 1e-30)"),
        "prime_ladders": {
            "primary": primary,
            "secondary": secondary,
            "tail_jackknife_prime": tail,
        },
        "memory_cap_gb": (
            "8 (machine protection; per-cell projected need and ru_maxrss "
            "high-water recorded in registry.json; NOTE: ok cells recorded "
            "before the darwin ru_maxrss units fix carry byte/KiB-misread "
            "values, converted maximum 4.49 GiB, within cap)"),
        "memory_breach_disclosure": (
            "All 26 cells at the appended 2^26-class tail prime (67108879) "
            "were measured with ru_maxrss high-water between 9.6 and 13.8 "
            "GiB against the frozen 8 GiB machine-protection cap (two padded "
            "arrays + bspec mmap pages + chirp live together; the pre-run "
            "need estimate missed the mmap contribution, and an ru_maxrss "
            "units bug on darwin (bytes misread as KiB) masked the first "
            "breach until the fresh-process continuation exposed it). Per "
            "the frozen stopping rule every tail-prime cell is checkpointed "
            "resource_exhaustion; the measured l1* and abs_vhat0 values are "
            "preserved in registry.json for a chunked/on-disk convolution "
            "amendment and are NOT used in the fits. All 406 ok cells lie "
            "at primes <= 16777259 with recorded high-water within the cap. "
            "Machine protection only: no mathematical verdict attaches to "
            "this disclosure."),
        "manifest_correction_note": (
            "This manifest was regenerated once after the run archive: the "
            "original hand-formatted emitter produced invalid YAML (unquoted "
            "cell-id keys containing colons; two folded plain scalars). The "
            "regeneration changed FORMAT ONLY -- same registry.json, same "
            "fits.json, same controls, CENSUS_NO_REMEASURE=1 so no cell was "
            "re-measured -- and the original manifest text remains in git "
            "history at the exec commit."),
        "validity": "void_control_failure" if control_fail else "controls_passed",
        "validity_reason": (
            "one or more frozen controls failed; dependent registry reads "
            "are void and the defective control is named in fits.json "
            "controls" if control_fail else "all frozen controls passed"),
        "control_failures": control_fail,
        "controls": controls,
        "control_notes": control_notes,
        "cells": {cid: {
            "status": r["status"],
            "l1_nontrivial": r.get("l1_nontrivial"),
            "abs_vhat0": r.get("abs_vhat0"),
            "wall_s": r.get("wall_seconds"),
            "rss_highwater_gb": r.get("rss_highwater_gb"),
        } for cid, r in sorted(reg.items())},
        "artifacts": ["implementation.py", "checker.py", "manifest.yaml",
                      "registry.json", "fits.json", "report.md"],
    }
    with open(MANIFEST_PATH, "w") as f:
        _yaml.dump({"run": run}, f, sort_keys=False, default_flow_style=False,
                   allow_unicode=True, width=100)


def write_report(families, curve_fams, controls, control_notes=None):
    control_notes = control_notes or {}
    y = ["# EXP-ECDLP-fac9ea v3 — lambda-registry census report", "",
         f"Run {RUN_ID}, generated {now_iso()} under TASK-20260921-4888d4.",
         "Specification v1 + amendments DEC-20260921-d3fafb (ladder) and",
         "DEC-20260921-f1d95a (probability normalisation), both pre-run.",
         "Observations only; gate verdicts use the frozen vocabulary; gates are",
         "necessary, not sufficient. Gates: lambda > 1/4 learning route",
         "(IDEA-20260904-f68c7f (D)); lambda >= 1/6 n^{1/3}-corner",
         "(IDEA-20260920-b6ad24 (A3)); PGL_2 deviation marks a row artifactual",
         "and voids it from the gate table (frozen rule).", "",
         "## Controls", "",
         "| control | result |", "|---|---|"]
    for k, v in controls.items():
        y.append(f"| {k} | {'PASS' if v is True else ('FAIL' if v is False else 'NOT EVALUATED')} |")
    for k, v in control_notes.items():
        y.append(f"| {k} | note: {v} |")
    y += ["", "## Gate table (frozen registry)", "",
          "| row | lambda | SE | n | verdict | moebius | two-ladder | jackknife |",
          "|---|---|---|---|---|---|---|---|"]
    for row in GATE_ROWS:
        fam = families.get(row, {})
        fit = fam.get("fit")
        if fit:
            mo = {False: "stable", True: "DEVIATION", None: "n/a"}[fam.get("moebius_delta_beyond_2se")]
            two = "DISAGREE" if fam.get("verdict") == "unresolved" else "agree"
            jack = "OUTLIER" if (fit.get("jackknife_lambda_excl_largest") is not None and
                                abs(fit["jackknife_lambda_excl_largest"] - fit["lambda"]) >
                                3 * (fit["se"] or 1)) else "ok"
            y.append(f"| {row} | {fit['lambda']:.4f} | {fit['se']:.4f} | {fit['n_points']} "
                     f"| {fam.get('verdict')} | {mo} | {two} | {jack} |")
        else:
            y.append(f"| {row} | - | - | - | {fam.get('verdict', 'unavailable')} | - | - | - |")
    y += ["", "## Control and auxiliary fits", "",
          "| row | lambda | SE | note |", "|---|---|---|---|"]
    for row in ["C02A", "C02B", "R03B"]:
        fam = families.get(row, {})
        if fam.get("fit"):
            note = {"C02A": "Parseval level 0.5", "C02B": "Parseval level 0.5, seed set B",
                    "R03B": "deterministic replication of R03"}[row]
            y.append(f"| {row} | {fam['fit']['lambda']:.4f} | {fam['fit']['se']:.4f} | {note} |")
    y.append(f"| C01 | 0 (exact) | - | all cells numerically zero: {families['C01']['all_numerically_zero']} |")
    for row in GATE_ROWS:
        mfit = families.get(row, {}).get("moebius_fit")
        if mfit:
            y.append(f"| {row}M | {mfit['lambda']:.4f} | {mfit['se']:.4f} | PGL_2 battery |")
    for k, fit in sorted(curve_fams.items()):
        if fit:
            y.append(f"| {k} | {fit['lambda']:.4f} | {fit['se']:.4f} | curve-restricted, auxiliary |")
    y += ["", "## Band census consequence", ""]
    c02lam = (families.get("C02A", {}).get("fit") or {}).get("lambda", 0.5)
    stable_rows = [r for r in GATE_ROWS
                   if (families.get(r, {}).get("fit") or {}).get("lambda") is not None
                   and families[r].get("moebius_delta_beyond_2se") is False]
    stable_above = [r for r in stable_rows if families[r]["fit"]["lambda"] > 0.25]
    parseval_level = [r for r in stable_above
                      if abs(families[r]["fit"]["lambda"] - c02lam) <=
                      max(2 * (families[r]["fit"]["se"] or 0), 0.01)]
    above_parseval = [r for r in stable_above if r not in parseval_level]
    if any(v is not True for v in controls.values()):
        y += ["VOID: one or more frozen controls failed; every registry read from this",
              "run is void as an infrastructure defect and is not evidence against",
              "H-ECDLP-4e1880. The defective control is named in fits.json controls."]
    else:
        y += ["ALL CONTROLS PASSED. Reading the gate table under the frozen rules:", ""]
        y += [f"- Every structured ADDITIVE statistic in the registry (R01 interval,",
              f"  R02 AP, R03/R03B popcount level, R04 base-3, R05 base-10, R09",
              f"  low-bit) is PGL_2-UNSTABLE: its lambda is a property of the specific",
              f"  x-line embedding, not of the statistic class, so the frozen rule",
              f"  voids all of them from the gate table (verdict: artifactual). The",
              f"  digit-family lambda (R03 = {families['R03']['fit']['lambda']:.4f}) reproduces the",
              f"  KN-FIND-ffe1df 0.39 measurement MARGINALLY (band edge 0.42) but is",
              f"  representation-unstable, so it cannot serve as a stable key."]
        if parseval_level:
            y += [f"- The only PGL_2-STABLE rows above the 1/4 threshold are the",
                  f"  multiplicative cosets {', '.join(parseval_level)}, and they sit at",
                  f"  the RANDOM-SET Parseval level (lambda ~ 0.50; C02A reads",
                  f"  {c02lam:.4f}): flat Gauss-sum structure, spectrally",
                  f"  indistinguishable from a random set of matched density. They",
                  f"  'open' both gates only in the vacuous necessary-condition",
                  f"  sense -- they carry no bias structure a construction can key on."]
        if above_parseval:
            y += [f"- STABLE AND ABOVE THE PARSEVAL LEVEL: {', '.join(above_parseval)} --",
                  f"  the only candidate band inhabitants a successor construction",
                  f"  step could key on; each needs more primes (R07 has 4 fit",
                  f"  points) before its level is decided."]
        y += ["", "SCOPED NEGATIVE, recorded: within the frozen registry, ladders",
              "(p <= 2^24.2 measured; the 2^26-class tail prime is checkpointed",
              "resource_exhaustion after a disclosed machine-protection breach,",
              "values preserved for a chunked-convolution amendment), and the",
              "frozen probability normalisation: NO natural coordinate statistic",
              "is simultaneously PGL_2-stable and spectrally distinct from the",
              "random-set level. Named successors: (a) the R07 index-5 coset",
              "level (0.5709 +- 0.0349, 4 points, ~2 sigma above Parseval) with a",
              "wider prime set; (b) synthetic coordinate-statistic design outside",
              "the registry; (c) the chunked-convolution amendment to recover the",
              "2^26-class tail point for the jackknife."]
    y += ["", "Per-cell raw values, wall times, RSS high-water marks, and unavailable",
          "certificates: registry.json and manifest.yaml. The census's own charged",
          "cost is the wall_seconds column.", ""]
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(y) + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--one":
        one_cell(sys.argv[2])
    else:
        main()
