#!/usr/bin/env python3
"""Stage A of EXP-HQC-982268 -- INSTRUMENT VALIDATION ONLY.

TASK-20260806-64b506 (executor) / BATCH-6fddee / GOAL-HQC-001.
Authorized by DEC-20260806-5289fb: STAGE A ONLY, 1692 core-seconds, 4 cores,
2 GB, one run.  Stages B1-B4 and C are NOT authorized and are NOT run here.

WHAT THIS SCRIPT DELIBERATELY DOES NOT DO
-----------------------------------------
It does NOT compute or report log2_A_k or log2_A_m on any space-(T) arm.
That is the measurement of EXP-HQC-982268 and it is not authorized by
DEC-20260806-5289fb.  The joint-moment estimator is exercised ONLY on the
i.i.d.-by-construction NULL arms (CTRL-BS, NULL-M, NULL-P), because the
contract's INV-NULL gate is *defined* as a statement about log2 Ahat_k on
those arms and cannot be evaluated at all otherwise.  Every joint-moment
number this script produces is a null-arm number.  The (T) arms are used only
for the diagnostics Stage A is chartered to measure (qhat, phat, gammahat,
Var(W_1), Corr(W_i,W_j), tie rate, w(etilde) tail) and for the hard
invariants D2 / D3 / D5.

Nothing here says anything about HQC, about assumption A17 or A5, about any
decoding-failure rate, or about any standardized HQC parameter set.
Claim tier: TOY, hard ceiling.

A timeout, crash, missing dependency or budget exhaustion is an INFRASTRUCTURE
outcome and is never evidence about the mathematics (AGENTS.md rule 5).

Re-run:
    PYTHONDONTWRITEBYTECODE=1 python3 stage_a.py --out-dir . --scratch <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import platform
import resource
import subprocess
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
ORACLE_DIR = os.path.join(
    REPO, "coordination", "goals", "GOAL-HQC-001", "batches", "BATCH-003",
    "tasks", "TASK-20260803-6f50df")

# sha256 values as published in oracle_report.md's deliverables table.
ORACLE_REPORT_HASHES = {
    "oracle.py": "96c54ed52af92043cd9c5569d6005235fc8886cf6f247d1a1d5f13605510cd79",
    "test_oracle.py": "b3c52cc0320f34084a85da193393001a038823613bd9229fbf6d66366c6befbc",
    "oracle_values.json": "a3d655823945f4fe99cec11944f49206f16a2779abbfe6a15c013629d52a28e5",
}

MASTER_SEED = 20260804                    # EXP-HQC-982268.replication.seed_scheme
DERIV_STRING = b"EXP-HQC-982268/v1"

# EXP-HQC-982268.inputs.parameter_sets, verbatim.  PS-D2/PS-D4 belong to the
# OPTIONAL stage D, which is not authorized, and are not defined here.
PARAM_SETS = [
    dict(id="PS-A", role="ANCHOR - true HQC-1 parameters, verbatim",
         n=17669, n_e=46, n_2=384, dup=3, d_i=192,
         omega=66, omega_r=75, omega_e=75, N=17664,
         tau=0.99972, p_star_exact=0.339788, m=16,
         log2_p_i_6_1_4=-10.7950),
    dict(id="PS-R1", role="ORDER-MATCHED to HQC-1, dup 3 -> 1",
         n=5923, n_e=46, n_2=128, dup=1, d_i=64,
         omega=39, omega_r=44, omega_e=44, N=5888,
         tau=0.99409, p_star_exact=0.347921, m=16, log2_p_i_6_1_4=None),
    dict(id="PS-R3", role="ORDER-MATCHED to HQC-3",
         n=7187, n_e=56, n_2=128, dup=1, d_i=64,
         omega=45, omega_r=51, omega_e=51, N=7168,
         tau=0.99735, p_star_exact=0.364929, m=17, log2_p_i_6_1_4=None),
    dict(id="PS-R5", role="ORDER-MATCHED to HQC-5",
         n=11549, n_e=90, n_2=128, dup=1, d_i=64,
         omega=59, omega_r=67, omega_e=67, N=11520,
         tau=0.99749, p_star_exact=0.376188, m=30, log2_p_i_6_1_4=None),
]

TABLE10_TAILS = {"1e-3": 6169, "1e-4": 6203, "1e-5": 6232, "1e-6": 6257}

N_JACK_BATCHES = 200
CTRL_BS_REPLICATES = 20
T_STAB_THRESHOLD = 30


# --------------------------------------------------------------------------
# exact helpers
# --------------------------------------------------------------------------

def is_prime(v: int) -> bool:
    if v < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if v % p == 0:
            return v == p
    d, s = v - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, v)
        if x in (1, v - 1):
            continue
        for _ in range(s - 1):
            x = x * x % v
            if x == v - 1:
                break
        else:
            return False
    return True


def two_is_primitive(v: int) -> bool:
    o = v - 1
    fac, t, d = [], v - 1, 2
    while d * d <= t:
        if t % d == 0:
            fac.append(d)
            while t % d == 0:
                t //= d
        d += 1
    if t > 1:
        fac.append(t)
    if pow(2, o, v) != 1:
        return False
    return all(pow(2, o // f, v) != 1 for f in fac)


def smallest_ring_n(N: int) -> int:
    """SPEC 4.1's own rule: smallest prime > N with 2 primitive modulo it."""
    v = N + 1
    while True:
        if is_prime(v) and two_is_primitive(v):
            return v
        v += 1


def binom_tail_lower_q(d_i: int, p: Fraction) -> Fraction:
    """Rigorous LOWER end of the INV-Q bracket, exact rational:
       P[Bin(d_i,p) > d_i/2] + (1/2) P[Bin(d_i,p) = d_i/2]."""
    one_m = 1 - p
    half = d_i // 2
    tot = Fraction(0)
    for j in range(half + 1, d_i + 1):
        tot += math.comb(d_i, j) * p ** j * one_m ** (d_i - j)
    tot += Fraction(1, 2) * math.comb(d_i, half) * p ** half * one_m ** (d_i - half)
    return tot


def sha_key(*parts) -> bytes:
    h = hashlib.sha256()
    h.update(DERIV_STRING)
    for p in parts:
        h.update(b"|")
        h.update(p if isinstance(p, bytes) else str(p).encode())
    return h.digest()[:16]                     # first 128 bits, per the contract


# --------------------------------------------------------------------------
# counter-mode PRNG -- the single source of randomness on the (T) arms
# --------------------------------------------------------------------------

class CTRStream:
    """SHA-256 in counter mode.  A deterministic function of (key, domain);
    every (trial, vector) pair gets its own domain, so any trial is replayable
    in isolation -- which is what CTRL-REPLAY / D5 depends on."""
    __slots__ = ("key", "dom", "ctr", "buf", "pos")

    def __init__(self, key: bytes, dom: bytes):
        self.key, self.dom, self.ctr, self.buf, self.pos = key, dom, 0, b"", 0

    def _refill(self, nbytes: int) -> None:
        chunks = [self.buf[self.pos:]]
        need = nbytes - len(chunks[0])
        while need > 0:
            chunks.append(hashlib.sha256(
                self.key + self.dom + self.ctr.to_bytes(8, "little")).digest())
            self.ctr += 1
            need -= 32
        self.buf = b"".join(chunks)
        self.pos = 0

    def u32(self) -> int:
        if len(self.buf) - self.pos < 4:
            self._refill(512)
        v = int.from_bytes(self.buf[self.pos:self.pos + 4], "little")
        self.pos += 4
        return v

    def below(self, bound: int) -> int:
        lim = (1 << 32) - ((1 << 32) % bound)
        while True:
            v = self.u32()
            if v < lim:
                return v % bound


def fixed_weight_support(stream: CTRStream, n: int, w: int) -> list:
    """Floyd's algorithm: exactly w DISTINCT indices, uniform over w-subsets.
    No Bernoulli step anywhere -- the uniform SampleFixedWeightVect$ shape
    the contract requires (space_T_guarantees_and_drift_detectors)."""
    seen, out = set(), []
    for i in range(n - w, n):
        j = stream.below(i + 1)
        if j in seen:
            seen.add(i)
            out.append(i)
        else:
            seen.add(j)
            out.append(j)
    return out


def support_to_int(supp, nbytes: int) -> int:
    ba = bytearray(nbytes)
    for a in supp:
        ba[a >> 3] |= 1 << (a & 7)
    return int.from_bytes(bytes(ba), "little")


def support_to_int_dense(supp, n: int) -> int:
    """Independent construction (numpy bit packing) used only by the D5 path."""
    v = np.zeros(n, dtype=np.uint8)
    v[np.asarray(supp, dtype=np.int64)] = 1
    return int.from_bytes(np.packbits(v, bitorder="little").tobytes(), "little")


def ring_mul_sparse(a_int: int, supp_b, n: int, mask: int) -> int:
    """SPARSE SHIFT-XOR path: a * b in F_2[X]/(X^n - 1)."""
    acc = 0
    for s in supp_b:
        acc ^= a_int << s
    return (acc & mask) ^ (acc >> n)


def ring_mul_dense(supp_a, supp_b, n: int) -> int:
    """INDEPENDENT code path for CTRL-REPLAY / D5.

    Dense GF(2) polynomial multiplication performed as ONE Python big-integer
    multiply in base 256.  Coefficient c_i of the integer product is the
    integer convolution sum_j a_j b_{i-j} <= min(|supp_a|,|supp_b|) <= 90 <
    256, so no carry crosses a byte boundary and c_i mod 2 is exactly the
    GF(2) coefficient.  Shares no shift, no XOR and no masking with
    ring_mul_sparse."""
    A = bytearray(n)
    for a in supp_a:
        A[a] = 1
    B = bytearray(n)
    for b in supp_b:
        B[b] = 1
    prod = int.from_bytes(bytes(A), "little") * int.from_bytes(bytes(B), "little")
    coeffs = np.frombuffer(prod.to_bytes(2 * n + 8, "little"), dtype=np.uint8)
    c = (coeffs[:2 * n] & 1).astype(np.uint8)
    folded = c[:n] ^ c[n:2 * n]                         # reduce mod X^n - 1
    return int.from_bytes(np.packbits(folded, bitorder="little").tobytes(), "little")


# --------------------------------------------------------------------------
# inner decoder: fold dup copies, size-128 fast Walsh-Hadamard, argmax
# --------------------------------------------------------------------------

def wht128(a: np.ndarray) -> np.ndarray:
    """In-place fast Walsh-Hadamard transform along the last axis (128).
    Index 0 of the transform is the all-ones (zero-codeword) row."""
    n = a.shape[-1]
    lead = a.shape[:-1]
    h = 1
    while h < n:
        b = a.reshape(*lead, n // (2 * h), 2, h)
        u = b[..., 0, :].copy()
        v = b[..., 1, :].copy()
        b[..., 0, :] = u + v
        b[..., 1, :] = u - v
        h *= 2
    return a


def decode_blocks(bits: np.ndarray, n_e: int, n_2: int, dup: int):
    """bits: (B, N) uint8 -> (F, W, ties), each (B, n_e).

    Fold: HQC's duplicated inner code repeats the whole 128-bit RM(1,7)
    codeword `dup` times inside a block, so folded position p is the sum of
    copies 0..dup-1 at p (SPEC 3.4.3 / reference expand_and_sum).
    TIE RULE: deployed deterministic "take the maximum value", broken by
    LOWEST index (EXP-HQC-982268.inputs.decoder).  A13's coin flip is NOT
    used."""
    B = bits.shape[0]
    blk = bits.reshape(B, n_e, n_2)
    W = blk.sum(axis=2, dtype=np.int32)
    folded = blk.reshape(B, n_e, dup, 128).sum(axis=2, dtype=np.int32)
    v = (dup - 2 * folded).astype(np.int32)
    t = wht128(v.reshape(-1, 128)).reshape(B, n_e, 128)
    av = np.abs(t)
    mx = av.max(axis=2)
    idx = av.argmax(axis=2)                     # numpy argmax -> FIRST (lowest)
    ties = (av == mx[:, :, None]).sum(axis=2) > 1
    val = np.take_along_axis(t, idx[:, :, None], axis=2)[:, :, 0]
    F = ~((idx == 0) & (val > 0))               # F_j = 1 unless the zero codeword
    return F, W, ties


def rm17_codewords() -> np.ndarray:
    idx = np.arange(128, dtype=np.uint8)
    rows = []
    for a in range(128):
        inner = np.zeros(128, dtype=np.uint8)
        for bit in range(7):
            if (a >> bit) & 1:
                inner ^= (idx >> bit) & 1
        rows.append(inner)
        rows.append(inner ^ 1)
    return np.array(rows, dtype=np.uint8)


def brute_force_decode(bits_block: np.ndarray, dup: int) -> np.ndarray:
    """Exhaustive minimum-distance search over the 256 duplicated codewords."""
    cw = np.tile(rm17_codewords(), (1, dup))
    d = (bits_block[:, None, :].astype(np.int16) ^ cw[None, :, :]).sum(axis=2)
    return d.argmin(axis=1) != 0


# --------------------------------------------------------------------------
# joint-moment estimator -- NULL ARMS ONLY
# --------------------------------------------------------------------------

def mubar_from_hist(hist, n_e: int, k: int):
    T = int(np.sum(hist))
    if T == 0:
        return float("nan")
    num = 0
    for s in range(k, n_e + 1):
        c = int(hist[s])
        if c:
            num += c * math.comb(s, k)
    return (num / T) / math.comb(n_e, k)


def log2_A_from_hist(hist, n_e: int, k: int):
    T = int(np.sum(hist))
    if T == 0:
        return None
    ssum = sum(int(hist[s]) * s for s in range(n_e + 1))
    q = ssum / T / n_e
    if q <= 0:
        return None
    mu = mubar_from_hist(hist, n_e, k)
    if not (mu > 0):
        return None
    return math.log2(mu) - k * math.log2(q)


def jackknife_log2_A(bh: np.ndarray, n_e: int, k: int):
    total = bh.sum(axis=0)
    point = log2_A_from_hist(total, n_e, k)
    if point is None:
        return None, None, None, 0
    vals = []
    for i in range(bh.shape[0]):
        v = log2_A_from_hist(total - bh[i], n_e, k)
        if v is None:
            return point, None, None, 0
        vals.append(v)
    b = len(vals)
    mean = sum(vals) / b
    se = math.sqrt((b - 1) / b * sum((v - mean) ** 2 for v in vals))
    return point, se, (b - 1) * (mean - point), b


def hist_of(S, n_e: int) -> np.ndarray:
    return np.bincount(np.asarray(S, dtype=np.int64), minlength=n_e + 1)[:n_e + 1]


def batch_hists(S, n_e: int, nb: int) -> np.ndarray:
    T = len(S)
    nb = max(1, min(nb, T))
    e = np.linspace(0, T, nb + 1).astype(int)
    return np.array([hist_of(S[e[i]:e[i + 1]], n_e) for i in range(nb)])


def evaluable_k(hist, n_e: int, floor: int = T_STAB_THRESHOLD):
    """Largest run of k >= 2 with at least `floor` trials having S >= k.
    (The contract's own T_stab reasoning: a Gaussian SE is meaningless unless
    the S-range carrying the estimand's mass is actually sampled.)"""
    ks = []
    for k in range(2, n_e + 1):
        if int(np.sum(hist[k:])) >= floor:
            ks.append(k)
        else:
            break
    return ks


def t_stab_required(n_e: int, q: float, k: int):
    if not (0.0 < q < 1.0) or k > n_e:
        return None, None
    pmf = np.array([math.comb(n_e, s) * q ** s * (1 - q) ** (n_e - s)
                    for s in range(n_e + 1)])
    contrib = np.array([pmf[s] * math.comb(s, k) if s >= k else 0.0
                        for s in range(n_e + 1)])
    tot = float(contrib.sum())
    if tot <= 0:
        return None, None
    s90 = int(np.searchsorted(np.cumsum(contrib), 0.90 * tot))
    tail = float(pmf[s90:].sum())
    return s90, (T_STAB_THRESHOLD / tail if tail > 0 else None)


def rel_variance_V(n_e: int, q: float, k: int):
    if not (0.0 < q < 1.0) or k > n_e:
        return None
    try:
        s = sum(math.comb(k, j) * math.comb(n_e - k, j) * q ** (k + j)
                for j in range(0, k + 1))
        v = s / (math.comb(n_e, k) * q ** (2 * k)) - 1.0
        return v if math.isfinite(v) else None
    except (OverflowError, ZeroDivisionError, ValueError):
        return None


# --------------------------------------------------------------------------
# oracle-diff helpers
# --------------------------------------------------------------------------

def deep_diff(a, b, path="", out=None, limit=600):
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append((path + "/" + str(k), "missing_in_rerun", None, None))
            elif k not in b:
                out.append((path + "/" + str(k), "missing_in_committed", None, None))
            else:
                deep_diff(a[k], b[k], path + "/" + str(k), out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, "length", len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                deep_diff(x, y, "%s/[%d]" % (path, i), out, limit)
    else:
        if type(a) is not type(b) and not (isinstance(a, (int, float))
                                           and isinstance(b, (int, float))):
            out.append((path, "type", str(type(a)), str(type(b))))
        elif a != b:
            out.append((path, "value", a, b))
    return out


def classify_diff(path: str) -> str:
    low = path.lower()
    if "provenance" in low:
        return "provenance"
    last = low.rsplit("/", 1)[-1]
    if last in ("timings", "seconds", "elapsed", "wall", "wall_seconds",
                "total_seconds", "elapsed_seconds") or "/timings/" in low:
        return "timing"
    return "computed_value"


# --------------------------------------------------------------------------
# (T) arm worker
# --------------------------------------------------------------------------

def _t_shard(args):
    (ps, shard, n_trials, wall_cap, batch, want_replay) = args
    t_cpu0, t_w0 = time.process_time(), time.time()

    n, N, n_e, n_2, dup = ps["n"], ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    om, omr, ome = ps["omega"], ps["omega_r"], ps["omega_e"]
    key = sha_key(ps["id"], "T", shard, MASTER_SEED)
    mask_n, mask_N = (1 << n) - 1, (1 << N) - 1
    nbytes_n, nbytes_N = (n + 7) // 8, N // 8
    cap_D3 = 2 * om * omr + ome
    replay_stride = max(1, n_trials // want_replay) if want_replay else 0

    F_all = np.zeros((n_trials, n_e), dtype=np.uint8)
    wtot = np.zeros(n_trials, dtype=np.int32)
    Wsum = np.zeros(n_e, dtype=np.float64)
    Wsq = np.zeros(n_e, dtype=np.float64)
    tie_count = d2_fail = d3_fail = d3_max_w = 0
    replay_checked = replay_mismatch = 0
    done, truncated = 0, False
    buf = np.zeros((batch, nbytes_N), dtype=np.uint8)

    t = 0
    while t < n_trials:
        b = min(batch, n_trials - t)
        for i in range(b):
            ti = t + i
            sx = fixed_weight_support(CTRStream(key, b"v0" + ti.to_bytes(8, "little")), n, om)
            sy = fixed_weight_support(CTRStream(key, b"v1" + ti.to_bytes(8, "little")), n, om)
            s1 = fixed_weight_support(CTRStream(key, b"v2" + ti.to_bytes(8, "little")), n, omr)
            s2 = fixed_weight_support(CTRStream(key, b"v3" + ti.to_bytes(8, "little")), n, omr)
            se = fixed_weight_support(CTRStream(key, b"v4" + ti.to_bytes(8, "little")), n, ome)

            xi = support_to_int(sx, nbytes_n)
            yi = support_to_int(sy, nbytes_n)
            r1 = support_to_int(s1, nbytes_n)
            r2 = support_to_int(s2, nbytes_n)
            ei = support_to_int(se, nbytes_n)

            # D2 -- exact weights on EVERY trial, both as index sets and as
            # popcounts of the constructed ring elements.
            if (xi.bit_count() != om or yi.bit_count() != om
                    or r1.bit_count() != omr or r2.bit_count() != omr
                    or ei.bit_count() != ome
                    or len(set(sx)) != om or len(set(sy)) != om
                    or len(set(s1)) != omr or len(set(s2)) != omr
                    or len(set(se)) != ome):
                d2_fail += 1

            epp = ring_mul_sparse(xi, s2, n, mask_n) ^ ring_mul_sparse(r1, sy, n, mask_n) ^ ei
            et = epp & mask_N

            # D3 -- hard support cap, checked on EVERY trial
            w_et = et.bit_count()
            d3_max_w = max(d3_max_w, w_et)
            if w_et > cap_D3 or epp.bit_count() > cap_D3:
                d3_fail += 1

            buf[i] = np.frombuffer(et.to_bytes(nbytes_N, "little"), dtype=np.uint8)

            # D5 -- CTRL-REPLAY through the independent dense-GF(2) path
            if replay_stride and (ti % replay_stride == 0) and replay_checked < want_replay:
                epp2 = (ring_mul_dense(sx, s2, n) ^ ring_mul_dense(s1, sy, n)
                        ^ support_to_int_dense(se, n))
                if (epp2 & mask_N) != et:
                    replay_mismatch += 1
                replay_checked += 1

        bits = np.unpackbits(buf[:b], axis=1, bitorder="little")[:, :N]
        F, W, ties = decode_blocks(bits, n_e, n_2, dup)
        F_all[t:t + b] = F
        Wf = W.astype(np.float64)
        Wsum += Wf.sum(axis=0)
        Wsq += (Wf * Wf).sum(axis=0)
        wtot[t:t + b] = W.sum(axis=1)
        tie_count += int(ties.sum())
        t += b
        done = t
        if time.time() - t_w0 > wall_cap:
            truncated = True
            break

    return dict(
        ps_id=ps["id"], shard=shard, trials_requested=n_trials, trials_done=done,
        truncated=truncated, F=F_all[:done], wtot=wtot[:done],
        Wsum=Wsum, Wsq=Wsq,
        tie_count=tie_count, tie_denom=done * n_e,
        d2_fail=d2_fail, d3_fail=d3_fail, d3_max_w=d3_max_w, d3_cap=cap_D3,
        replay_checked=replay_checked, replay_mismatch=replay_mismatch,
        replay_stride=replay_stride,
        cpu_seconds=time.process_time() - t_cpu0, wall_seconds=time.time() - t_w0,
        key_hex=key.hex())


def _null_m_shard(args):
    """NULL-M: e-tilde ~ Bernoulli(phat)^{tensor N}; identical n_e, n_2, dup
    and identical decoder.  On this arm A_k = 1 is a theorem."""
    (ps, shard, n_trials, phat, wall_cap, batch) = args
    t_cpu0, t_w0 = time.process_time(), time.time()
    N, n_e, n_2, dup = ps["N"], ps["n_e"], ps["n_2"], ps["dup"]
    seed = int.from_bytes(sha_key(ps["id"], "NULL-M", shard, MASTER_SEED)[:8], "little")
    rng = np.random.default_rng(seed)
    S = np.zeros(n_trials, dtype=np.int16)
    wt = np.zeros(n_trials, dtype=np.int32)
    tie_count, done, truncated, t = 0, 0, False, 0
    while t < n_trials:
        b = min(batch, n_trials - t)
        bits = (rng.random((b, N), dtype=np.float32) < phat).astype(np.uint8)
        F, W, ties = decode_blocks(bits, n_e, n_2, dup)
        S[t:t + b] = F.sum(axis=1)
        wt[t:t + b] = W.sum(axis=1)
        tie_count += int(ties.sum())
        t += b
        done = t
        if time.time() - t_w0 > wall_cap:
            truncated = True
            break
    return dict(ps_id=ps["id"], shard=shard, trials_done=done, truncated=truncated,
                S=S[:done], wtot=wt[:done], tie_count=tie_count,
                tie_denom=done * n_e, seed=seed,
                cpu_seconds=time.process_time() - t_cpu0,
                wall_seconds=time.time() - t_w0)


# --------------------------------------------------------------------------
# phases
# --------------------------------------------------------------------------

def phase_oracle(scratch, results, skip=False):
    t0, c0 = time.time(), time.process_time()
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = {"gate": "ORACLE-AGREEMENT"}
    if skip:
        out.update(status="skipped_developer_smoke_path", core_seconds=0.0,
                   cpu_seconds_self=0.0, cpu_seconds_children=0.0, wall_seconds=0.0)
        results["oracle"] = out
        return out

    hashes = {}
    for fn, expect in ORACLE_REPORT_HASHES.items():
        got = hashlib.sha256(open(os.path.join(ORACLE_DIR, fn), "rb").read()).hexdigest()
        hashes[fn] = dict(expected_in_oracle_report=expect, observed=got,
                          match=(got == expect))
    out["committed_file_hashes"] = hashes
    out["committed_file_hashes_all_match"] = all(v["match"] for v in hashes.values())

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    rerun_path = os.path.join(scratch, "oracle_values_rerun.json")
    cmd = [sys.executable, "oracle.py", "--out", rerun_path, "--seed", "20260803"]
    try:
        p = subprocess.run(cmd, cwd=ORACLE_DIR, env=env, capture_output=True,
                           text=True, timeout=900)
        rc, err = p.returncode, p.stderr
    except subprocess.TimeoutExpired:
        rc, err = -1, "TIMEOUT after 900 s (INFRASTRUCTURE outcome)"
    out["oracle_rerun_command"] = " ".join(cmd)
    out["oracle_rerun_returncode"] = rc
    out["oracle_rerun_stderr_tail"] = err[-2000:] if err else ""

    if rc == 0 and os.path.exists(rerun_path):
        committed = json.load(open(os.path.join(ORACLE_DIR, "oracle_values.json")))
        rerun = json.load(open(rerun_path))
        buckets = {"computed_value": [], "timing": [], "provenance": []}
        for d in deep_diff(rerun, committed):
            buckets[classify_diff(d[0])].append(
                dict(path=d[0], kind=d[1], rerun=str(d[2])[:200],
                     committed=str(d[3])[:200]))
        out["diff_counts"] = {k: len(v) for k, v in buckets.items()}
        out["computed_value_diffs"] = buckets["computed_value"][:80]
        out["provenance_diffs"] = buckets["provenance"][:40]
        out["timing_diff_paths_sample"] = [d["path"] for d in buckets["timing"]][:25]
        out["agreement_on_computed_values"] = (len(buckets["computed_value"]) == 0)
        out["status"] = ("evaluated_AGREE" if not buckets["computed_value"]
                         else "evaluated_DISAGREE")
    else:
        out["status"] = "not_evaluable"
        out["reason"] = "oracle.py re-run did not complete; see returncode/stderr"

    try:
        p2 = subprocess.run([sys.executable, "test_oracle.py"], cwd=ORACLE_DIR,
                            env=env, capture_output=True, text=True, timeout=900)
        out["test_oracle_returncode"] = p2.returncode
        out["test_oracle_tail"] = (p2.stdout + p2.stderr)[-4000:]
        out["test_oracle_pass"] = (p2.returncode == 0)
    except subprocess.TimeoutExpired:
        out["test_oracle_returncode"] = -1
        out["test_oracle_pass"] = False
        out["test_oracle_tail"] = "TIMEOUT after 900 s (INFRASTRUCTURE outcome)"

    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    out["cpu_seconds_self"] = time.process_time() - c0
    out["cpu_seconds_children"] = ((ru1.ru_utime - ru0.ru_utime)
                                   + (ru1.ru_stime - ru0.ru_stime))
    out["core_seconds"] = out["cpu_seconds_self"] + out["cpu_seconds_children"]
    out["wall_seconds"] = time.time() - t0
    results["oracle"] = out
    return out


def phase_contract_checks(results):
    t0, c0 = time.time(), time.process_time()
    rows = []
    for ps in PARAM_SETS:
        r = dict(id=ps["id"], role=ps["role"])
        r["N_equals_n_e_times_n_2"] = (ps["N"] == ps["n_e"] * ps["n_2"])
        r["n_2_equals_128_dup"] = (ps["n_2"] == 128 * ps["dup"])
        r["d_i_equals_64_dup"] = (ps["d_i"] == 64 * ps["dup"])
        nn = smallest_ring_n(ps["N"])
        r["ring_rule_n_computed"] = nn
        r["ring_rule_n_tabulated"] = ps["n"]
        r["ring_rule_match"] = (nn == ps["n"])
        r["tau_computed"] = ps["N"] / ps["n"]
        r["tau_tabulated"] = ps["tau"]
        r["tau_abs_diff"] = abs(ps["N"] / ps["n"] - ps["tau"])
        cap = 2 * ps["omega"] * ps["omega_r"] + ps["omega_e"]
        r["D3_cap"] = cap
        r["N_times_p_star"] = ps["N"] * ps["p_star_exact"]
        r["D3_cap_over_expected_w_on_space_M"] = cap / (ps["N"] * ps["p_star_exact"])
        pstar = Fraction(str(ps["p_star_exact"]))
        lo = binom_tail_lower_q(ps["d_i"], pstar)
        r["INV_Q_lower_rigorous"] = float(lo)
        r["INV_Q_lower_log2"] = math.log2(float(lo)) if lo > 0 else None
        if ps["log2_p_i_6_1_4"] is not None:
            r["INV_Q_upper_p_i_log2"] = ps["log2_p_i_6_1_4"]
            r["INV_Q_upper_p_i"] = 2.0 ** ps["log2_p_i_6_1_4"]
            r["INV_Q_upper_source"] = ("frozen regression fixture, "
                                       "EXP-HQC-982268.required_artifacts.fixed_artifacts")
            r["INV_Q_evaluable"] = True
        else:
            r["INV_Q_upper_p_i"] = None
            r["INV_Q_evaluable"] = False
            r["INV_Q_upper_not_evaluable_reason"] = (
                "Proposition 6.1.4's closed form for p_i is not transcribed "
                "anywhere in this task's read scope (it lives in BATCH-001 "
                "dfr_model_transcription.md), and the frozen fixture supplies "
                "p_i only at HQC-1/3/5 (dup 3 and 5), never at dup = 1. "
                "Reconstructing it from memory would be fabrication, so the "
                "upper end of the INV-Q bracket is reported as NOT EVALUABLE "
                "rather than guessed. The rigorous LOWER end is computed.")
        rows.append(r)
    out = dict(gate="CONTRACT-STRUCTURAL-CHECKS", per_set=rows,
               cpu_seconds=time.process_time() - c0, wall_seconds=time.time() - t0)
    results["contract_checks"] = out
    return out


def phase_smoke(results):
    """Self-tests of this script's own primitives, run BEFORE spending the
    measurement budget so a defect is not discovered by spending it."""
    t0, c0 = time.time(), time.process_time()
    checks = {}

    H = np.ones((1, 1), dtype=np.int64)
    for _ in range(7):
        H = np.block([[H, H], [H, -H]])
    v = np.random.default_rng(7).integers(-3, 4, size=(5, 128)).astype(np.int32)
    checks["wht_matches_dense_hadamard"] = bool(
        np.array_equal(wht128(v.copy()), (v.astype(np.int64) @ H.T).astype(np.int32)))
    checks["hadamard_row0_all_ones"] = bool(np.all(H[0] == 1))

    rng = np.random.default_rng(11)
    dec = {}
    for dup, p in ((1, 0.35), (3, 0.34)):
        n_2 = 128 * dup
        bits = (rng.random((400, n_2)) < p).astype(np.uint8)
        F, _, _ = decode_blocks(bits.reshape(400, 1, n_2), 1, n_2, dup)
        Fb = brute_force_decode(bits, dup)
        dec["dup%d_agree" % dup] = int((F[:, 0] == Fb).sum())
        dec["dup%d_total" % dup] = 400
        dec["dup%d_wht_failure_rate" % dup] = float(F[:, 0].mean())
    checks["decoder_vs_bruteforce"] = dec

    st = CTRStream(b"smoke-key-------", b"ring")
    n = 251
    sa = fixed_weight_support(st, n, 7)
    sb = fixed_weight_support(st, n, 9)
    ai = support_to_int(sa, (n + 7) // 8)
    checks["ring_sparse_equals_dense"] = bool(
        ring_mul_sparse(ai, sb, n, (1 << n) - 1) == ring_mul_dense(sa, sb, n))

    ok = True
    for i in range(50):
        s = fixed_weight_support(CTRStream(b"smoke-key-------", b"fw%d" % i), 1000, 66)
        ok &= (len(s) == 66 and len(set(s)) == 66 and all(0 <= a < 1000 for a in s))
    checks["fixed_weight_exact_and_distinct"] = bool(ok)

    a = [CTRStream(b"k" * 16, b"d1").u32() for _ in range(5)]
    b_ = [CTRStream(b"k" * 16, b"d1").u32() for _ in range(5)]
    c = [CTRStream(b"k" * 16, b"d2").u32() for _ in range(5)]
    checks["prng_replayable"] = (a == b_)
    checks["prng_domains_differ"] = (a != c)

    # estimator identity on an exact toy law: mubar_k = q^k for i.i.d. indicators
    ne_t, q_t, k_t = 8, 0.25, 3
    hist = np.array([round(1e9 * math.comb(ne_t, s) * q_t ** s * (1 - q_t) ** (ne_t - s))
                     for s in range(ne_t + 1)], dtype=np.int64)
    got = mubar_from_hist(hist, ne_t, k_t)
    checks["estimator_exact_on_binomial_law"] = dict(
        expected=q_t ** k_t, observed=got, rel_err=abs(got - q_t ** k_t) / q_t ** k_t)

    out = dict(gate="SMOKE-SELF-TESTS", checks=checks,
               all_pass=bool(checks["wht_matches_dense_hadamard"]
                             and checks["ring_sparse_equals_dense"]
                             and checks["fixed_weight_exact_and_distinct"]
                             and checks["prng_replayable"] and checks["prng_domains_differ"]
                             and dec["dup1_agree"] == 400 and dec["dup3_agree"] == 400
                             and checks["estimator_exact_on_binomial_law"]["rel_err"] < 1e-6),
               cpu_seconds=time.process_time() - c0, wall_seconds=time.time() - t0)
    results["smoke"] = out
    return out


def phase_calibrate(results, t_trials, m_trials):
    t0, c0 = time.time(), time.process_time()
    rows = {}
    for ps in PARAM_SETS:
        r = _t_shard((ps, 900, t_trials, 180.0, 32, 0))
        m = _null_m_shard((ps, 900, m_trials, ps["p_star_exact"], 180.0, 32))
        rows[ps["id"]] = dict(
            T_trials=r["trials_done"], T_cpu=r["cpu_seconds"],
            T_core_seconds_per_trial=r["cpu_seconds"] / max(1, r["trials_done"]),
            T_trials_per_core_second=r["trials_done"] / max(1e-9, r["cpu_seconds"]),
            M_trials=m["trials_done"], M_cpu=m["cpu_seconds"],
            M_core_seconds_per_trial=m["cpu_seconds"] / max(1, m["trials_done"]))
    out = dict(gate="CALIBRATION", per_set=rows,
               cpu_seconds=time.process_time() - c0, wall_seconds=time.time() - t0)
    results["calibration"] = out
    return out


def git_state():
    def run(*a):
        try:
            return subprocess.run(a, cwd=REPO, capture_output=True, text=True,
                                  timeout=60).stdout.strip()
        except Exception as exc:                       # noqa: BLE001
            return "unavailable: %s" % exc
    porcelain = run("git", "status", "--porcelain")
    return dict(commit=run("git", "rev-parse", "HEAD"),
                branch=run("git", "rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(porcelain), dirty_entries=porcelain.splitlines()[:40],
                dirty_entry_count=len(porcelain.splitlines()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--core-seconds", type=float, default=1692.0)
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--wall-cap", type=float, default=1700.0)
    ap.add_argument("--tiny", action="store_true",
                    help="developer smoke path; NOT the authorized run")
    ap.add_argument("--postprocess", action="store_true",
                    help="deterministic post-processing of an existing "
                         "stage_a_results.json; samples nothing")
    args = ap.parse_args(argv)

    if args.postprocess:
        return postprocess(os.path.join(args.out_dir, "stage_a_results.json"))

    t_start = time.time()
    results = {
        "task_id": "TASK-20260806-64b506",
        "experiment_id": "EXP-HQC-982268",
        "hypothesis_id": "H-HQC-18d1b4",
        "approving_decision": "DEC-20260806-5289fb",
        "stage": "A",
        "authorized_scope": "STAGE A ONLY (DEC-20260806-5289fb); B1-B4 and C NOT run",
        "claim_tier": "toy",
        "role": "executor -- observations only; no interpretation, no status change",
        "measurement_prohibition": (
            "log2_A_k / log2_A_m are NOT computed or reported on any space-(T) "
            "arm. Joint-moment numbers appear ONLY on the three "
            "i.i.d.-by-construction null arms, because the contract's INV-NULL "
            "gate is defined as a statement about log2 Ahat_k on those arms and "
            "is otherwise not evaluable at all."),
        "command": " ".join([sys.executable] + sys.argv),
        "git": git_state(),
        "environment": dict(
            python=sys.version, python_executable=sys.executable,
            platform=platform.platform(), machine=platform.machine(),
            numpy=np.__version__,
            cpu_count=os.cpu_count(),
            affinity=len(os.sched_getaffinity(0)),
            sympy_present=_mod_present("sympy"), sage_present=_mod_present("sage"),
            scipy_present=_mod_present("scipy"),
            third_party_used=["numpy"],
        ),
        "seed_scheme": dict(master_seed=MASTER_SEED,
                            derivation_string=DERIV_STRING.decode(),
                            prng="SHA-256 counter mode, 128-bit key = "
                                 "sha256(deriv || set_id || arm || shard || master)[:16]; "
                                 "per-(trial,vector) domain b'v<i>' || trial_le64",
                            null_M_prng="numpy PCG64 (np.random.default_rng), "
                                        "seed derived by the same SHA-256 scheme",
                            null_P_prng="numpy PCG64, same derivation"),
        "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    phase_oracle(args.scratch, results, skip=args.tiny)
    phase_contract_checks(results)
    phase_smoke(results)

    budget = args.core_seconds
    spent = (results["oracle"]["core_seconds"]
             + results["contract_checks"]["cpu_seconds"]
             + results["smoke"]["cpu_seconds"])

    phase_calibrate(results, 40 if args.tiny else 300, 40 if args.tiny else 400)
    spent += results["calibration"]["cpu_seconds"]

    reserve_overhead = 20.0 if args.tiny else 110.0
    reserve_nullP = 5.0 if args.tiny else 20.0
    reserve_nullM = 40.0 if args.tiny else 330.0
    reserve_bs = 10.0 if args.tiny else 60.0
    t_allow = max(0.0, budget - spent - reserve_overhead - reserve_nullP
                  - reserve_nullM - reserve_bs)
    share = {"PS-A": 0.40, "PS-R1": 0.20, "PS-R3": 0.20, "PS-R5": 0.20}

    alloc = {}
    for ps in PARAM_SETS:
        cal = results["calibration"]["per_set"][ps["id"]]
        T = int(t_allow * share[ps["id"]] / max(cal["T_core_seconds_per_trial"], 1e-9))
        if args.tiny:
            T = min(T, 160)
        T = max(T, 4 * 8)
        T -= T % args.cores
        Tm = int(reserve_nullM * share[ps["id"]] / max(cal["M_core_seconds_per_trial"], 1e-9))
        if args.tiny:
            Tm = min(Tm, 160)
        Tm = max(Tm, 4 * 8)
        Tm -= Tm % args.cores
        alloc[ps["id"]] = dict(core_seconds_allocated=t_allow * share[ps["id"]],
                               T_core_seconds_per_trial=cal["T_core_seconds_per_trial"],
                               trials_planned=T,
                               null_M_trials_planned=Tm,
                               null_M_core_seconds_per_trial=cal["M_core_seconds_per_trial"])
    results["budget_allocation"] = dict(
        authorized_core_seconds=budget, spent_before_T_arms=spent,
        reserved_null_M=reserve_nullM, reserved_null_P=reserve_nullP,
        reserved_CTRL_BS=reserve_bs, reserved_overhead=reserve_overhead,
        core_seconds_for_T_arms=t_allow, share=share, per_set=alloc,
        contract_stage_A_modeled_trials=8_000_000,
        contract_stage_A_modeled_throughput_trials_per_core_second=8_000_000 / 1692.0,
        note=("The contract models Stage A as 8e6 trials in 1692 core-seconds, "
              "i.e. 4728 trials/core-second, a MODELED figure (budget_basis: "
              "'EVERY NUMBER IN THE TABLE IS MODELED'). Trial counts here are "
              "sized to the MEASURED throughput instead. Under ST-1 a truncated "
              "run is a valid partial measurement at the smaller T; k values "
              "whose requirement exceeds the achieved T are reported as NOT "
              "REACHED, never as null results."))

    # ---- (T) arms, args.cores shards each --------------------------------
    remaining_wall = args.wall_cap - (time.time() - t_start)
    per_shard_wall = max(30.0, remaining_wall * 0.55)
    replay_target = 8 if args.tiny else 400
    jobs = []
    for ps in PARAM_SETS:
        per = alloc[ps["id"]]["trials_planned"] // args.cores
        for sh in range(args.cores):
            jobs.append((ps, sh, per, per_shard_wall, 64, replay_target // args.cores))

    w0 = time.time()
    with mp.Pool(processes=args.cores) as pool:
        shard_results = pool.map(_t_shard, jobs)
    t_arm_wall = time.time() - w0
    t_arm_cpu = sum(r["cpu_seconds"] for r in shard_results)
    spent += t_arm_cpu

    # ---- aggregate (T) diagnostics ---------------------------------------
    t_ana0 = time.process_time()
    Fmat, diagnostics = {}, {}
    for ps in PARAM_SETS:
        rs = sorted([r for r in shard_results if r["ps_id"] == ps["id"]],
                    key=lambda r: r["shard"])
        F = np.concatenate([r["F"] for r in rs], axis=0)
        wt = np.concatenate([r["wtot"] for r in rs]).astype(np.float64)
        for r in rs:                        # release the per-shard copies
            r["F"] = None
            r["wtot"] = None
        Fmat[ps["id"]] = F
        n_e, N = ps["n_e"], ps["N"]
        T = F.shape[0]
        S = F.sum(axis=1).astype(np.int16)
        hist = hist_of(S, n_e)

        phat = float(wt.mean() / N)
        var_w = float(wt.var(ddof=1)) if T > 1 else float("nan")
        gamma = var_w / (N * phat * (1 - phat)) if (T > 1 and 0 < phat < 1) else float("nan")
        gamma_se = math.sqrt(2.0 / max(1, T - 1))
        Wsum = sum(r["Wsum"] for r in rs)
        Wsq = sum(r["Wsq"] for r in rs)
        meanW = Wsum / T
        varW_per_block = (Wsq - T * meanW ** 2) / (T - 1) if T > 1 else np.full(n_e, np.nan)
        varW1 = float(np.mean(varW_per_block))
        meanW1 = float(np.mean(meanW))
        corrW = ((var_w / (n_e * varW1) - 1.0) / (n_e - 1)) if varW1 > 0 else None
        qhat = float(S.mean() / n_e)

        tails = {}
        for tail, key in ((1e-3, "1e-3"), (1e-4, "1e-4"), (1e-5, "1e-5"), (1e-6, "1e-6")):
            need = 1.0 / tail
            row = dict(trials_needed_at_least=need, trials_achieved=T,
                       table10_published=TABLE10_TAILS[key] if ps["id"] == "PS-A" else None)
            if T >= need:
                row["quantile_observed"] = float(np.quantile(wt, 1.0 - tail))
                row["reachable"] = True
                if ps["id"] == "PS-A":
                    row["deviation_from_table10"] = (row["quantile_observed"]
                                                     - TABLE10_TAILS[key])
            else:
                row.update(quantile_observed=None, reachable=False,
                           reason="achieved T < 1/tail at the authorized budget "
                                  "(INFRASTRUCTURE/BUDGET limit, not a result)")
            tails[key] = row

        diagnostics[ps["id"]] = dict(
            trials=T, trials_planned=alloc[ps["id"]]["trials_planned"],
            truncated_shards=[r["shard"] for r in rs if r["truncated"]],
            q_hat=qhat, p_hat=phat, p_star_contract=ps["p_star_exact"],
            p_hat_minus_p_star=phat - ps["p_star_exact"],
            gamma_hat=gamma, gamma_hat_se_approx=gamma_se,
            var_w_etilde=var_w, var_W1=varW1, mean_W1=meanW1, corr_W_hat=corrW,
            var_W1_binomial_reference=ps["n_2"] * phat * (1 - phat),
            tie_rate=sum(r["tie_count"] for r in rs) / max(1, sum(r["tie_denom"] for r in rs)),
            S_histogram=[int(x) for x in hist],
            block_failure_counts=[int(x) for x in F.sum(axis=0)],
            w_etilde_mean=float(wt.mean()), w_etilde_max=int(wt.max()) if T else None,
            upper_tail_quantiles=tails,
            cpu_seconds=sum(r["cpu_seconds"] for r in rs),
            trials_per_core_second=T / max(1e-9, sum(r["cpu_seconds"] for r in rs)),
            shard_keys=[r["key_hex"] for r in rs],
            D1=dict(gamma_hat=gamma,
                    drift_alarm_band=[0.95, 1.05],
                    in_drift_alarm_band=bool(0.95 <= gamma <= 1.05),
                    ps_a_extra_band=([0.55, 0.85] if ps["id"] == "PS-A" else None),
                    in_ps_a_extra_band=(bool(0.55 <= gamma <= 0.85)
                                        if ps["id"] == "PS-A" else None)),
            D2=dict(trials_checked=T, deviations=sum(r["d2_fail"] for r in rs)),
            D3=dict(trials_checked=T, violations=sum(r["d3_fail"] for r in rs),
                    cap=rs[0]["d3_cap"], max_w_etilde_observed=max(r["d3_max_w"] for r in rs)),
            D5=dict(trials_checked=sum(r["replay_checked"] for r in rs),
                    mismatches=sum(r["replay_mismatch"] for r in rs),
                    stride=[r["replay_stride"] for r in rs]),
        )

    # ---- NULL-P ----------------------------------------------------------
    null_p, null_p_bh = {}, {}
    for ps in PARAM_SETS:
        n_e = ps["n_e"]
        q = diagnostics[ps["id"]]["q_hat"]
        Tp = 2000 if args.tiny else 10_000_000
        seed = int.from_bytes(sha_key(ps["id"], "NULL-P", 0, MASTER_SEED)[:8], "little")
        rng = np.random.default_rng(seed)
        Sp = (rng.binomial(n_e, q, size=Tp).astype(np.int16) if 0 < q < 1
              else np.zeros(Tp, np.int16))
        null_p_bh[ps["id"]] = batch_hists(Sp, n_e, N_JACK_BATCHES)
        null_p[ps["id"]] = dict(trials=Tp, q_input=q, seed=seed,
                                q_hat_recovered=float(Sp.mean() / n_e),
                                S_histogram=[int(x) for x in hist_of(Sp, n_e)])
        del Sp

    # ---- NULL-M ----------------------------------------------------------
    nm_jobs = []
    for ps in PARAM_SETS:
        per = alloc[ps["id"]]["null_M_trials_planned"] // args.cores
        for sh in range(args.cores):
            nm_jobs.append((ps, sh, per, diagnostics[ps["id"]]["p_hat"],
                            max(20.0, (args.wall_cap - (time.time() - t_start)) * 0.5), 64))
    w0 = time.time()
    with mp.Pool(processes=args.cores) as pool:
        nm_results = pool.map(_null_m_shard, nm_jobs)
    nm_wall = time.time() - w0
    nm_cpu = sum(r["cpu_seconds"] for r in nm_results)
    spent += nm_cpu

    null_m, null_m_bh = {}, {}
    for ps in PARAM_SETS:
        rs = sorted([r for r in nm_results if r["ps_id"] == ps["id"]],
                    key=lambda r: r["shard"])
        S = np.concatenate([r["S"] for r in rs])
        wt = np.concatenate([r["wtot"] for r in rs]).astype(np.float64)
        for r in rs:
            r["S"] = None
            r["wtot"] = None
        n_e, N = ps["n_e"], ps["N"]
        T = len(S)
        ph = diagnostics[ps["id"]]["p_hat"]
        gm = (float(wt.var(ddof=1)) / (N * ph * (1 - ph))) if T > 1 else float("nan")
        se = math.sqrt(2.0 / max(1, T - 1))
        null_m_bh[ps["id"]] = batch_hists(S, n_e, N_JACK_BATCHES)
        null_m[ps["id"]] = dict(
            trials=T, truncated_shards=[r["shard"] for r in rs if r["truncated"]],
            p_input=ph, q_hat=float(S.mean() / n_e),
            gamma_hat=gm, gamma_hat_se_approx=se,
            gamma_hat_z_vs_one=(gm - 1.0) / se,
            TC5_within_3_se_of_one=bool(abs(gm - 1.0) <= 3 * se),
            tie_rate=sum(r["tie_count"] for r in rs) / max(1, sum(r["tie_denom"] for r in rs)),
            S_histogram=[int(x) for x in hist_of(S, n_e)], seeds=[r["seed"] for r in rs],
            cpu_seconds=sum(r["cpu_seconds"] for r in rs))
        del S, wt

    # ---- CTRL-BS ---------------------------------------------------------
    ctrl_bs, ctrl_bs_reps = {}, {}
    for ps in PARAM_SETS:
        F = Fmat[ps["id"]]
        n_e, T = ps["n_e"], F.shape[0]
        rng = np.random.default_rng(
            int.from_bytes(sha_key(ps["id"], "CTRL-BS", 0, MASTER_SEED)[:8], "little"))
        reps = []
        deviations = []
        for _r in range(CTRL_BS_REPLICATES):
            off, o, mode = None, None, "coprime_offsets"
            for _attempt in range(50):
                o, seen, tries = [], set(), 0
                while len(o) < n_e and tries < 200 * n_e:
                    tries += 1
                    v = int(rng.integers(1, max(2, T)))
                    if math.gcd(v, T) == 1 and v not in seen:
                        o.append(v)
                        seen.add(v)
                if len(o) < n_e:
                    # Fewer than n_e units modulo T exist (or were found).
                    # Fall back to drawing the OFFSETS THEMSELVES distinct --
                    # pairwise-distinct offsets are the property CTRL-BS
                    # actually needs (blocks of a pseudo-trial must come from
                    # distinct true trials). Recorded as a deviation.
                    mode = "distinct_offsets_fallback"
                    off = list(map(int, rng.choice(T, size=min(n_e, T),
                                                   replace=False)))
                    while len(off) < n_e:
                        off.append(off[-1])
                    break
                off = [(j * o[j]) % T for j in range(n_e)]
                if len(set(off)) == n_e:
                    break
            if mode != "coprime_offsets" or len(set(off)) != n_e:
                deviations.append(dict(replicate=_r, mode=mode,
                                       distinct=len(set(off)) == n_e))
            Fb = np.empty_like(F)
            for j in range(n_e):
                Fb[:, j] = np.roll(F[:, j], -off[j])
            Sb = Fb.sum(axis=1).astype(np.int16)
            reps.append(dict(offsets_distinct=bool(len(set(off)) == n_e),
                             offsets_head=off[:8], hist=hist_of(Sb, n_e),
                             bh=batch_hists(Sb, n_e, N_JACK_BATCHES)))
            del Fb, Sb
        ctrl_bs_reps[ps["id"]] = reps
        ctrl_bs[ps["id"]] = dict(
            trials=T, n_replicates=len(reps),
            offset_construction_deviations=deviations,
            offsets_all_distinct=all(r["offsets_distinct"] for r in reps),
            block_marginals=[float(x) for x in F.mean(axis=0)],
            block_marginal_min=float(F.mean(axis=0).min()),
            block_marginal_max=float(F.mean(axis=0).max()),
            replicate0_S_histogram=[int(x) for x in reps[0]["hist"]])

    # ---- INV-NULL --------------------------------------------------------
    inv_null = {}
    for ps in PARAM_SETS:
        n_e = ps["n_e"]
        arms = {}

        for name, bh in (("NULL-P", null_p_bh[ps["id"]]), ("NULL-M", null_m_bh[ps["id"]])):
            tot = bh.sum(axis=0)
            ks = evaluable_k(tot, n_e)
            cells = []
            for k in ks:
                pt, se, bias, nb = jackknife_log2_A(bh, n_e, k)
                cells.append(dict(k=k, log2_A_null=pt, jackknife_se=se,
                                  jackknife_bias=bias, n_batches=nb,
                                  trials_with_S_ge_k=int(np.sum(tot[k:])),
                                  abs_z=(abs(pt) / se) if (pt is not None and se) else None,
                                  INV_NULL_fires=bool(pt is not None and se
                                                      and abs(pt) > 3 * se)))
            arms[name] = dict(
                trials=int(tot.sum()), k_evaluated=ks, cells=cells,
                k_first_not_reached=(max(ks) + 1 if ks else 2),
                not_reached_reason=("fewer than %d trials have S >= k at the "
                                    "achieved T; NOT REACHED, not a null result"
                                    % T_STAB_THRESHOLD),
                any_fire=any(c["INV_NULL_fires"] for c in cells))

        reps = ctrl_bs_reps[ps["id"]]
        tot = reps[0]["hist"]
        ks = evaluable_k(tot, n_e)
        cells = []
        for k in ks:
            vals = [log2_A_from_hist(r["hist"], n_e, k) for r in reps]
            vals = [v for v in vals if v is not None]
            pt_j, se_j, _b, _n = jackknife_log2_A(reps[0]["bh"], n_e, k)
            if len(vals) >= 2:
                mean = sum(vals) / len(vals)
                se_rep = math.sqrt(sum((v - mean) ** 2 for v in vals) / (len(vals) - 1))
            else:
                mean, se_rep = (vals[0] if vals else None), None
            cand = [s for s in (se_rep, se_j) if s is not None]
            se_use = max(cand) if cand else None
            cells.append(dict(k=k, log2_A_null_replicate_mean=mean,
                              se_across_20_offset_replicates=se_rep,
                              jackknife_se_replicate0=se_j, se_used=se_use,
                              n_replicates=len(vals),
                              trials_with_S_ge_k=int(np.sum(tot[k:])),
                              abs_z=(abs(mean) / se_use) if (mean is not None and se_use) else None,
                              INV_NULL_fires=bool(mean is not None and se_use
                                                  and abs(mean) > 3 * se_use)))
        arms["CTRL-BS"] = dict(
            trials=int(tot.sum()), k_evaluated=ks, cells=cells,
            k_first_not_reached=(max(ks) + 1 if ks else 2),
            offsets_all_distinct=all(r["offsets_distinct"] for r in reps),
            any_fire=any(c["INV_NULL_fires"] for c in cells),
            se_note=("The 20 offset-set replicates share the SAME underlying "
                     "(T) trials, so their spread captures offset-choice "
                     "variability only and UNDERSTATES the sampling SE. The "
                     "larger of (replicate spread, jackknife over 200 "
                     "contiguous trial batches) is used."))
        inv_null[ps["id"]] = arms

    # ---- forward-looking sizing (NOT a measurement) ----------------------
    sizing = {}
    for ps in PARAM_SETS:
        n_e, q = ps["n_e"], diagnostics[ps["id"]]["q_hat"]
        rows = []
        for k in range(2, min(n_e, 34) + 1):
            s90, tstab = t_stab_required(n_e, q, k)
            rows.append(dict(k=k, s_90=s90, T_stab=tstab, V=rel_variance_V(n_e, q, k)))
        sizing[ps["id"]] = dict(
            q_hat_used=q, m=ps["m"], rows=rows,
            note=("T_stab = 30/P[S >= s_90] under S ~ Bin(n_e, qhat): the "
                  "contract's pre-registered SIZING convention. T_prec needs an "
                  "epsilon the contract does not fix, so it is not computed. "
                  "These are forward-looking sizing numbers for a stage that is "
                  "NOT authorized, not measurements of anything."))

    ana_cpu = time.process_time() - t_ana0
    spent += ana_cpu
    ru = resource.getrusage(resource.RUSAGE_SELF)
    ruc = resource.getrusage(resource.RUSAGE_CHILDREN)

    results.update(dict(
        diagnostics_T=diagnostics, null_P=null_p, null_M=null_m, ctrl_BS=ctrl_bs,
        INV_NULL=inv_null, k_max_sizing=sizing,
        timing=dict(oracle_core_seconds=results["oracle"]["core_seconds"],
                    contract_checks_core_seconds=results["contract_checks"]["cpu_seconds"],
                    smoke_core_seconds=results["smoke"]["cpu_seconds"],
                    calibration_core_seconds=results["calibration"]["cpu_seconds"],
                    T_arm_core_seconds=t_arm_cpu, T_arm_wall_seconds=t_arm_wall,
                    null_M_core_seconds=nm_cpu, null_M_wall_seconds=nm_wall,
                    analysis_core_seconds=ana_cpu,
                    total_core_seconds_accounted=spent,
                    authorized_core_seconds=args.core_seconds,
                    within_budget=bool(spent <= args.core_seconds),
                    total_wall_seconds=time.time() - t_start,
                    rusage_self_cpu_seconds=ru.ru_utime + ru.ru_stime,
                    rusage_children_cpu_seconds=ruc.ru_utime + ruc.ru_stime,
                    rusage_total_cpu_seconds=(ru.ru_utime + ru.ru_stime
                                              + ruc.ru_utime + ruc.ru_stime),
                    peak_rss_mb_self=ru.ru_maxrss / 1024.0,
                    peak_rss_mb_largest_child=ruc.ru_maxrss / 1024.0),
        finished_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    ))

    def enc(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(str(type(o)))

    outp = os.path.join(args.out_dir, "stage_a_results.json")
    with open(outp, "w") as fh:
        json.dump(results, fh, indent=1, default=enc, allow_nan=True)
    print("WROTE", outp)
    print("core_seconds_accounted=%.1f / %.1f  wall=%.1f"
          % (spent, args.core_seconds, time.time() - t_start))
    return 0


# --------------------------------------------------------------------------
# POST-PROCESSING PASS (--postprocess)
#
# Added AFTER the single authorized measurement run, and recorded as such in
# run_manifest.yaml.  It SAMPLES NO HQC OBJECT and re-runs no measurement: it
# is deterministic arithmetic on values already recorded in
# stage_a_results.json, plus a decoder cross-check on i.i.d. Bernoulli blocks
# (which construct no ring element and no fixed-weight vector).  The main code
# path above is unmodified, so re-running the script reproduces the
# measurement exactly.
# --------------------------------------------------------------------------

def esym_mean(q, k: int) -> float:
    """e_k(q_0..q_{n-1}) / C(n,k)."""
    e = [1.0] + [0.0] * k
    for x in q:
        for j in range(min(k, len(e) - 1), 0, -1):
            e[j] += e[j - 1] * x
    return e[k] / math.comb(len(q), k)


def postprocess(path: str):
    t0, c0 = time.time(), time.process_time()
    with open(path) as fh:
        res = json.load(fh)
    by_id = {p["id"]: p for p in PARAM_SETS}

    # (1) CTRL-BS: what its expectation ACTUALLY is, from the recorded
    #     empirical block marginals.  The contract asserts E[Ahat_k] = 1
    #     EXACTLY for every k, by construction.  Under the shuffle the blocks
    #     of a pseudo-trial come from distinct independent true trials, so
    #     mubar_k^BS = e_k(q_0..q_{n_e-1})/C(n_e,k) while the denominator is
    #     qbar^k.  Maclaurin's inequality gives e_k/C(n_e,k) <= qbar^k with
    #     equality iff every q_j is equal, so E[log2 Ahat_k^BS] <= 0 with a
    #     computable floor -- not 0 exactly.
    bs = {}
    for pid, v in res["ctrl_BS"].items():
        q = v["block_marginals"]
        n_e = len(q)
        qbar = sum(q) / n_e
        ks = [c["k"] for c in res["INV_NULL"][pid]["CTRL-BS"]["cells"]]
        rows = []
        for k in ks:
            ek = esym_mean(q, k)
            floor = (math.log2(ek) - k * math.log2(qbar)) if (ek > 0 and qbar > 0) else None
            se = next((c["se_used"] for c in res["INV_NULL"][pid]["CTRL-BS"]["cells"]
                       if c["k"] == k), None)
            rows.append(dict(k=k, maclaurin_floor_log2_A=floor,
                             se_used=se,
                             floor_over_se=(abs(floor) / se) if (floor and se) else None))
        bs[pid] = dict(n_e=n_e, q_bar=qbar,
                       block_marginal_spread=max(q) - min(q), rows=rows)
    res["ctrl_BS_expectation_analysis"] = dict(
        finding=("The contract's claim 'E[Ahat_k] = 1 EXACTLY, for every k, by "
                 "construction' is not exact. It holds only when every block "
                 "marginal q_j is identical; with empirically unequal q_j "
                 "Maclaurin's inequality forces E[log2 Ahat_k^BS] <= 0. The "
                 "computed floor is reported per cell beside the SE actually "
                 "used, so a reader can see how far below the noise it sits."),
        per_set=bs)

    # (2) Cross-reference every INV-NULL cell against the contract's OWN
    #     T_stab requirement, recomputed at that ARM's own qhat.
    xref = {}
    for pid in res["INV_NULL"]:
        n_e = by_id[pid]["n_e"]
        per_arm = {}
        for arm, a in res["INV_NULL"][pid].items():
            if arm == "NULL-P":
                q = res["null_P"][pid]["q_hat_recovered"]
            elif arm == "NULL-M":
                q = res["null_M"][pid]["q_hat"]
            else:
                q = res["diagnostics_T"][pid]["q_hat"]
            T = a["trials"]
            rows = []
            for c in a["cells"]:
                k = c["k"]
                s90, tstab = t_stab_required(n_e, q, k)
                rows.append(dict(k=k, s_90=s90, T_stab=tstab, T_achieved=T,
                                 T_meets_T_stab=(bool(tstab is not None and T >= tstab)),
                                 INV_NULL_fires=c["INV_NULL_fires"]))
            adm = [r["k"] for r in rows if r["T_meets_T_stab"]]
            fired = [r["k"] for r in rows if r["INV_NULL_fires"]]
            fired_admissible = [r["k"] for r in rows
                                if r["INV_NULL_fires"] and r["T_meets_T_stab"]]
            per_arm[arm] = dict(
                q_hat_used=q, trials=T,
                k_admissible_under_T_stab=adm,
                k_max_admissible=(max(adm) if adm else None),
                k_fired=fired, k_fired_while_admissible=fired_admissible,
                rows=rows)
        xref[pid] = per_arm
    res["INV_NULL_vs_T_stab"] = dict(
        purpose=("Stage A's k-evaluability floor (at least 30 trials with "
                 "S >= k) is WEAKER than the contract's own T_stab = "
                 "30/P[S >= s_90]. This cross-reference separates cells that "
                 "the contract would admit from cells reported beyond it."),
        per_set=xref)

    # (3) Extended decoder cross-check.  The smoke-phase check ran at p ~ p*,
    #     where dup = 3 essentially never fails, so the dup = 3 FAILURE branch
    #     was not exercised.  Sweep p so it is.  i.i.d. Bernoulli blocks only:
    #     no ring element and no fixed-weight vector is constructed.
    rng = np.random.default_rng(20260806)
    dec_rows = []
    for dup in (1, 3):
        n_2 = 128 * dup
        for p in (0.30, 0.34, 0.38, 0.42, 0.46, 0.50):
            M = 600
            bits = (rng.random((M, n_2)) < p).astype(np.uint8)
            F, _, ties = decode_blocks(bits.reshape(M, 1, n_2), 1, n_2, dup)
            Fb = brute_force_decode(bits, dup)
            dec_rows.append(dict(dup=dup, p=p, blocks=M,
                                 agree=int((F[:, 0] == Fb).sum()),
                                 wht_failures=int(F[:, 0].sum()),
                                 bruteforce_failures=int(Fb.sum()),
                                 tie_blocks=int(ties.sum())))
    res["decoder_cross_check_extended"] = dict(
        method=("size-128 folded Walsh-Hadamard argmax vs exhaustive "
                "minimum-distance search over all 256 duplicated RM(1,7) "
                "codewords, on i.i.d. Bernoulli(p) blocks"),
        note=("This is CTRL-DEC in spirit. The contract assigns CTRL-DEC to "
              "stage C at 1e5 trials/set, which is NOT authorized; this is a "
              "600-block-per-cell instrument check at Stage A scale and is "
              "labelled as such, not as CTRL-DEC discharged."),
        rows=dec_rows,
        all_agree=all(r["agree"] == r["blocks"] for r in dec_rows),
        failure_branch_exercised_at_dup3=any(
            r["dup"] == 3 and r["bruteforce_failures"] > 0 for r in dec_rows))

    res["postprocess"] = dict(
        ran_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        cpu_seconds=time.process_time() - c0, wall_seconds=time.time() - t0,
        samples_any_hqc_object=False,
        note=("Deterministic post-processing of already-recorded values plus "
              "an i.i.d.-Bernoulli decoder cross-check. Added to stage_a.py "
              "AFTER the single authorized measurement run; the measurement "
              "code path was not modified."))

    def enc(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.bool_):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(str(type(o)))

    with open(path, "w") as fh:
        json.dump(res, fh, indent=1, default=enc, allow_nan=True)
    print("POSTPROCESSED", path, "cpu=%.2f s" % (time.process_time() - c0))
    return 0


def _mod_present(name: str) -> bool:
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


if __name__ == "__main__":
    sys.exit(main())
