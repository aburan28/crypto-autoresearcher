"""Counters for EXP-MONO-1a1be2 (TASK-20261029-a97206): ctypes wrapper of code/kernel.c, matched random
and twin bases, the four-convention exhaustive histogrammer with its independent recount, and the
target-sampled arm-C counter.

Definitions (IDEA-20261023-f15270 assumptions[0], L2 to L4). D = factor base (symmetric set of points,
|D| = B), X = x(D) with one lift L(x) per x (the point of that x with the smaller y code), t2 = number
of 2-torsion points in D, m = tuple size (m = n in the contract; independent here so that the known-answer
tests can use small fields with several m).

  T_A(R) = #ordered m-tuples of D with sum R
  T_M(R) = #multisets of size m of D with sum R
  T_S(R) = #(ordered x-tuple in X^m, sign vector eps in {+-1}^m) with sum_i eps_i L(x_i) = R
  T_X(R) = #x-multisets (multisets of X, size m) for which at least one point multiset over them sums to R
  (T_M(R) = sum over x-multisets of c(R), c = # point multisets over the x-multiset with sum R,
   T_X(R) = # x-multisets with c(R) >= 1; each point multiset over an x-multiset is a choice of how many
   copies of L(x) and of -L(x) for each x, 2-torsion x having a single point.)

Targets: all N group elements, indexed idx(P) = 2 code(x) + [code(y) > code(-y)], idx(O) = 2Q. Generic
target: not O, not in E[2], not a sum of m-2l points of D (l >= 1) [the set S].

The independent recount (R1) of every convention recomputes the histogram with the base list reversed
and the kernel in reference-arithmetic mode (inversion by Fermat, z^(Q-2)) and compares every target.
Arithmetic correctness itself is established by the known-answer tests against naive Python.
"""
from __future__ import annotations

import ctypes
import hashlib
import math
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

import numpy as np

import fqn
from fqn import FQ
from curves import Curve

HERE = os.path.dirname(os.path.abspath(__file__))
CC_FLAGS = ["-O3", "-Wall", "-Wextra", "-shared", "-fPIC", "-std=c11"]

K_ORD, K_ORD2, K_MS, K_MSW, K_XM, K_MARK = 0, 1, 2, 3, 4, 5


# ----------------------------------------------------------------------------- build
def compiler_record():
    cc = shutil.which("gcc") or shutil.which("cc")
    ver = subprocess.run([cc, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    return {"compiler": cc, "version": ver, "flags": list(CC_FLAGS)}


def build_kernel(outdir: str | None = None) -> str:
    """Compile kernel.c into a shared object in a temporary directory (default: a new mkdtemp).
    Returns the .so path. No binary is committed anywhere."""
    outdir = outdir or tempfile.mkdtemp(prefix="mono1a1be2-kernel-")
    src = os.path.join(HERE, "kernel.c")
    so = os.path.join(outdir, "kernel.so")
    rec = compiler_record()
    cmd = [rec["compiler"]] + CC_FLAGS + ["-o", so, src]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("kernel build failed:\n" + r.stdout + r.stderr)
    if r.stderr.strip():
        raise RuntimeError("kernel build produced warnings (treated as errors):\n" + r.stderr)
    return so


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# ----------------------------------------------------------------------------- indexing in Python
def target_index(F: FQ, P) -> int:
    """idx(P) as in the kernel, computed in Python (used to cross-check the kernel)."""
    if P is None:
        return 2 * F.Q
    x, y = P
    return 2 * F.to_code(x) + (1 if F.to_code(y) > F.to_code(F.neg(y)) else 0)


def points_to_arrays(F: FQ, pts):
    nb = len(pts)
    bx = np.zeros((nb, F.n), dtype=np.uint32)
    by = np.zeros((nb, F.n), dtype=np.uint32)
    for k, (x, y) in enumerate(pts):
        bx[k, :] = x
        by[k, :] = y
    return np.ascontiguousarray(bx.reshape(-1)), np.ascontiguousarray(by.reshape(-1))


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p) if a is not None else None


class Kernel:
    def __init__(self, so_path: str):
        self.so_path = so_path
        L = self.lib = ctypes.CDLL(so_path)
        vp, i32, i64, u32, u64 = ctypes.c_void_p, ctypes.c_int, ctypes.c_int64, ctypes.c_uint32, ctypes.c_uint64
        L.kinit.argtypes = [i32, u32, vp]; L.kinit.restype = i32
        L.kset_curve.argtypes = [vp, vp]; L.kset_curve.restype = None
        L.kset_ref.argtypes = [i32]; L.kset_ref.restype = None
        L.kpoint_index.argtypes = [vp, vp, i32]; L.kpoint_index.restype = u64
        L.kadd.argtypes = [vp, vp, i32, vp, vp, i32, vp, vp]; L.kadd.restype = i32
        L.kmul_test.argtypes = [vp, vp, vp]; L.kmul_test.restype = i32
        L.kinv_test.argtypes = [vp, vp]; L.kinv_test.restype = i32
        L.kcount_points.argtypes = [vp]; L.kcount_points.restype = u64
        L.krun.argtypes = [i32, i32, i32, vp, vp, vp, vp, vp, vp]; L.krun.restype = i32
        L.krun_sampled.argtypes = [i32, i32, vp, vp, i64, vp, i64, vp, vp]; L.krun_sampled.restype = i32
        L.khist_stats.argtypes = [vp, vp, u64, i64, vp, vp]; L.khist_stats.restype = i64
        L.kcmp.argtypes = [vp, vp, vp, u64, ctypes.c_uint8, vp]; L.kcmp.restype = None
        L.kmark_special.argtypes = [vp, vp, i64]; L.kmark_special.restype = None
        L.khist_sum.argtypes = [vp, vp, u64]; L.khist_sum.restype = u64
        L.kchi_batch.argtypes = [vp, i64, vp]; L.kchi_batch.restype = None
        L.kcollect.argtypes = [i32, i32, vp, vp, vp, i64]; L.kcollect.restype = i64
        self._bound = None
        self._ref = None

    # --- state
    def bind(self, E: Curve, ref: bool = False):
        F = E.F
        key = (F.q, F.n, F.g, E.a, E.b)
        if self._bound != key:
            g = np.array(F.g, dtype=np.uint32)
            rc = self.lib.kinit(F.n, F.q, _p(g))
            if rc != 0:
                raise RuntimeError(f"kinit failed: {rc}")
            a = np.array(E.a, dtype=np.uint32)
            b = np.array(E.b, dtype=np.uint32)
            self.lib.kset_curve(_p(a), _p(b))
            self._bound = key
        if self._ref != ref:
            self.lib.kset_ref(1 if ref else 0)
            self._ref = ref

    # --- single-element helpers for tests
    def mul(self, E, a, b):
        self.bind(E)
        o = np.zeros(E.F.n, dtype=np.uint32)
        A, B = np.array(a, dtype=np.uint32), np.array(b, dtype=np.uint32)
        self.lib.kmul_test(_p(A), _p(B), _p(o))
        return tuple(int(v) for v in o)

    def inv(self, E, a, ref=False):
        self.bind(E, ref)
        o = np.zeros(E.F.n, dtype=np.uint32)
        A = np.array(a, dtype=np.uint32)
        if self.lib.kinv_test(_p(A), _p(o)):
            raise ZeroDivisionError
        self.bind(E, False)
        return tuple(int(v) for v in o)

    def add(self, E, P, R):
        self.bind(E)
        n = E.F.n
        z = np.zeros(n, dtype=np.uint32)
        def arr(T):
            return (np.zeros(n, dtype=np.uint32), np.zeros(n, dtype=np.uint32), 1) if T is None else (
                np.array(T[0], dtype=np.uint32), np.array(T[1], dtype=np.uint32), 0)
        x1, y1, i1 = arr(P)
        x2, y2, i2 = arr(R)
        xo, yo = np.zeros(n, dtype=np.uint32), np.zeros(n, dtype=np.uint32)
        inf = self.lib.kadd(_p(x1), _p(y1), i1, _p(x2), _p(y2), i2, _p(xo), _p(yo))
        if inf:
            return None
        return (tuple(int(v) for v in xo), tuple(int(v) for v in yo))

    def point_index(self, E, P):
        self.bind(E)
        n = E.F.n
        if P is None:
            z = np.zeros(n, dtype=np.uint32)
            return int(self.lib.kpoint_index(_p(z), _p(z), 1))
        x, y = np.array(P[0], dtype=np.uint32), np.array(P[1], dtype=np.uint32)
        return int(self.lib.kpoint_index(_p(x), _p(y), 0))

    # --- point counting
    def count_points(self, E: Curve) -> int:
        self.bind(E)
        return int(self.lib.kcount_points(None))

    def valid_mask(self, E: Curve):
        """(N, mask) with mask[idx] bit0 = valid target, bit1 = O or 2-torsion."""
        self.bind(E)
        mask = np.zeros(2 * E.F.Q + 1, dtype=np.uint8)
        N = int(self.lib.kcount_points(_p(mask)))
        return N, mask

    # --- enumeration
    def run_hist(self, E, kind, m, pts, need2=False, ref=False, mask=None):
        F = E.F
        self.bind(E, ref)
        size = 2 * F.Q + 1
        bx, by = points_to_arrays(F, pts)
        if kind == K_MARK:
            h = h2 = None
        else:
            h = np.zeros(size, dtype=np.uint32)
            h2 = np.zeros(size, dtype=np.uint32) if need2 else h
        stats = np.zeros(4, dtype=np.uint64)
        rc = self.lib.krun(kind, m, len(pts), _p(bx), _p(by), _p(h), _p(h2), _p(mask), _p(stats))
        if rc != 0:
            raise RuntimeError(f"krun failed: {rc}")
        if int(stats[2]):
            raise RuntimeError("uint32 histogram overflow")
        self.bind(E, False)
        return h, (h2 if need2 else None), {"leaves": int(stats[0]), "cancellation_free": int(stats[1])}

    def collect_sums(self, E, m, pts):
        F = E.F
        self.bind(E)
        bx, by = points_to_arrays(F, pts)
        total = math.comb(len(pts) + m - 1, m) if m > 0 else 1
        out = np.zeros(max(total, 1), dtype=np.uint64)
        got = int(self.lib.kcollect(m, len(pts), _p(bx), _p(by), _p(out), total))
        if got != total:
            raise RuntimeError("kcollect count mismatch")
        return out[:total]

    def hist_stats(self, hist, mask):
        maxc = 1 << 16
        while True:
            a = np.zeros(maxc + 1, dtype=np.uint64)
            g = np.zeros(maxc + 1, dtype=np.uint64)
            mx = int(self.lib.khist_stats(_p(hist), _p(mask), hist.size, maxc, _p(a), _p(g)))
            if mx > maxc:
                maxc <<= 4
                continue
            return ({int(c): int(a[c]) for c in np.nonzero(a)[0]}, {int(c): int(g[c]) for c in np.nonzero(g)[0]})

    def cmp(self, h1, h2, mask, skip=0):
        out = np.zeros(4, dtype=np.uint64)
        self.lib.kcmp(_p(h1), _p(h2), _p(mask), h1.size, skip, _p(out))
        return {"differ": int(out[0]), "lt": int(out[1]), "gt": int(out[2]), "compared": int(out[3])}

    def hist_sum(self, hist, mask):
        return int(self.lib.khist_sum(_p(hist), _p(mask), hist.size))

    def mark_special(self, mask, idxs):
        a = np.array(sorted(set(int(i) for i in idxs)), dtype=np.uint64)
        if a.size:
            self.lib.kmark_special(_p(mask), _p(a), a.size)

    def chi_batch(self, E, xs):
        """chi(f(x)) for an (cnt, n) uint32 array of x-tuples."""
        self.bind(E)
        xs = np.ascontiguousarray(xs, dtype=np.uint32)
        out = np.zeros(xs.shape[0], dtype=np.int8)
        self.lib.kchi_batch(_p(xs), xs.shape[0], _p(out))
        return out

    def run_sampled(self, E, m, pts, keys, nsampled):
        F = E.F
        self.bind(E)
        bx, by = points_to_arrays(F, pts)
        keys = np.ascontiguousarray(keys, dtype=np.uint64)
        counts = np.zeros(max(keys.size, 1), dtype=np.uint32)
        stats = np.zeros(4, dtype=np.uint64)
        rc = self.lib.krun_sampled(m, len(pts), _p(bx), _p(by), keys.size, _p(keys), nsampled, _p(counts), _p(stats))
        if rc != 0:
            raise RuntimeError(f"krun_sampled failed: {rc}")
        if int(stats[3]):
            raise RuntimeError("overflow")
        return counts[:keys.size], {"multisets": int(stats[0]), "cancellation_free": int(stats[1]),
                                    "m_S": int(stats[2])}


# ----------------------------------------------------------------------------- exact combinatorics
def ncf_coefficient(B: int, t2: int, m: int) -> int:
    """Coefficient of z^m in ((1+z)/(1-z))^((B-t2)/2) (1+z)^t2: the number of size-m multisets of a
    symmetric base D (B points, t2 of them 2-torsion) with no cancelling pair (no P and -P together,
    no 2-torsion point twice)."""
    if (B - t2) % 2:
        raise ValueError("B - t2 must be even")
    one = [1] + [0] * m
    pair = [1] + [2] * m          # (1+z)/(1-z) = 1 + 2z + 2z^2 + ...
    tors = [1, 1] + [0] * (m - 1)
    tors = tors[: m + 1]

    def mulp(a, b):
        out = [0] * (m + 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b):
                    if i + j <= m:
                        out[i + j] += ai * bj
        return out

    def powp(a, e):
        r, base = one, a
        while e:
            if e & 1:
                r = mulp(r, base)
            e >>= 1
            if e:
                base = mulp(base, base)
        return r

    return mulp(powp(pair, (B - t2) // 2), powp(tors, t2))[m]


# ----------------------------------------------------------------------------- bases
def _sorted_points(F: FQ, pts):
    return sorted(pts, key=lambda P: (F.to_code(P[0]), F.to_code(P[1])))


def random_symmetric_base(E: Curve, t2: int, pairs: int, rng):
    """Random symmetric base with t2 points drawn from E(F_Q)[2] minus O (rng.permutation of the
    code-sorted roots, first t2) and `pairs` +- pairs on distinct x, x uniform over F_Q with f(x) a nonzero
    square (rejection, one rng.integers(0, q, size=n) per attempt), y = the smaller-code root, both signs.
    Uniform over +- classes. Returns the base sorted by (code x, code y)."""
    F = E.F
    roots = E.two_torsion_roots()
    if t2 > len(roots):
        raise ValueError("t2 exceeds the number of 2-torsion points of E(F_Q)")
    pts = []
    if t2:
        for i in sorted(int(j) for j in rng.permutation(len(roots))[:t2]):
            pts.append((roots[i], F.zero))
    seen = set()
    attempts = 0
    while len(seen) < pairs:
        attempts += 1
        if attempts > 1000 * pairs + 100000:
            raise ValueError("random base: too few +- classes available for the requested size")
        x = F.random_element(rng)
        if x in seen:
            continue
        y = F.sqrt(E.f(x))
        if y is None or F.is_zero(y):
            continue
        seen.add(x)
        pts.append((x, y))
        pts.append((x, F.neg(y)))
    return _sorted_points(F, pts)


def matched_random_base(E: Curve, B: int, t2: int, rng):
    """CTL-null object: size B, same t2, (B - t2)/2 +- pairs."""
    return random_symmetric_base(E, t2, (B - t2) // 2, rng)


def twin_base(E: Curve, B: int, t2: int, rng):
    """CTL-twin object: same t2, ceil((B - t2)/4) +- pairs (about half size). Size B' = t2 + 2 ceil((B-t2)/4)."""
    return random_symmetric_base(E, t2, -(-(B - t2) // 4), rng)


# ----------------------------------------------------------------------------- the S set
def s_set_indices(kernel: Kernel, E: Curve, D, m: int):
    """Sorted unique target indices of S = { sums of (m - 2l)-multisets of D : l >= 1, m - 2l >= 0 }."""
    parts = []
    mp = m - 2
    while mp >= 0:
        parts.append(kernel.collect_sums(E, mp, D))
        mp -= 2
    if not parts:
        return np.zeros(0, dtype=np.uint64)
    return np.unique(np.concatenate(parts))


# ----------------------------------------------------------------------------- exhaustive histogrammer
def _summary(hist_all: dict, hist_gen: dict):
    def summ(h):
        n = sum(h.values())
        s1 = sum(c * v for c, v in h.items())
        s2 = sum(c * c * v for c, v in h.items())
        zeros = h.get(0, 0)
        return {"targets": n, "sum": s1, "sumsq": s2, "zeros": zeros, "max": max(h) if h else None}
    return {"all": summ(hist_all), "generic": summ(hist_gen)}


def exhaustive_cell(kernel: Kernel, E: Curve, D, X_lifts, m: int, N: int, valid_mask, recount: bool = True,
                    keep: bool = False):
    """All four conventions over all N targets for the base D (any symmetric base) with an independent
    recount, the P2 identity residuals (M1) and the exact reference values.

    D: base points. X_lifts: for every distinct x of D one lift (the smaller y code); 2-torsion points
    appear once. valid_mask: kernel mask of E (copied; S is marked in the copy as bit value 4).
    Returns a JSON-friendly dict; with keep=True the count arrays and the mask are attached (small
    cells only: they are not freed)."""
    F = E.F
    Q = F.Q
    B = len(D)
    t2 = sum(1 for P in D if F.is_zero(P[1]))
    Dprime = []                                          # ordered x-tuples with sign classes
    for (x, y) in X_lifts:
        Dprime.append((x, y))
        Dprime.append((x, F.neg(y)))
    S_idx = s_set_indices(kernel, E, D, m)
    mask = valid_mask.copy()
    if S_idx.size:
        mask[S_idx.astype(np.int64)] |= 4
    out = {"m": m, "B": B, "t2": t2, "N": N, "size_X": len(X_lifts), "S_size": int(S_idx.size),
           "special_targets_O_and_E2": int(np.count_nonzero((mask & 3) == 3)),
           "generic_targets": int(np.count_nonzero((mask & 7) == 1)),
           "valid_targets": int(np.count_nonzero(mask & 1)),
           "conventions": {}, "recount": {}, "identities": {}}
    conv, ident, rec = out["conventions"], out["identities"], out["recount"]
    arrays = {}
    O = 2 * Q

    def recount_check(name, kind, pts, primary):
        if not recount:
            return
        h, _, _ = kernel.run_hist(E, kind, m, list(reversed(pts)), ref=True)
        c = kernel.cmp(primary, h, mask)
        rec[name] = {"differ": c["differ"], "compared": c["compared"]}

    def record(name, hist, leaves, extra=None):
        ha, hg = kernel.hist_stats(hist, mask)
        conv[name] = {"leaves": leaves, "hist_all": ha, "hist_gen": hg, "stats": _summary(ha, hg)}
        if extra:
            conv[name].update(extra)

    # ---- T_A: ordered point tuples
    TA, _, st = kernel.run_hist(E, K_ORD, m, D)
    record("A", TA, st["leaves"])
    ident["i_sum_A"] = {"observed": kernel.hist_sum(TA, mask), "expected": B ** m}
    if m == 2:
        ident["v_TA_O"] = {"observed": int(TA[O]), "expected": B}
    recount_check("A", K_ORD, D, TA)
    # (ii) T_A vs the sum over multisets of m!/prod(m_j!)
    TMW, _, _ = kernel.run_hist(E, K_MSW, m, D)
    ident["ii_TA_vs_weighted_multisets"] = kernel.cmp(TA, TMW, mask)
    if keep:
        arrays["A"], arrays["MW"] = TA, TMW
    del TA, TMW
    # ---- T_M: multisets
    TM, _, st = kernel.run_hist(E, K_MS, m, D)
    record("M", TM, st["leaves"], {"cancellation_free_multisets": st["cancellation_free"]})
    ident["i_sum_M"] = {"observed": kernel.hist_sum(TM, mask), "expected": math.comb(B + m - 1, m)}
    ident["vi_cancellation_free"] = {"observed": st["cancellation_free"], "expected": ncf_coefficient(B, t2, m)}
    if m == 2:
        ident["v_TM_O_twice"] = {"observed": 2 * int(TM[O]), "expected": B + t2}
    recount_check("M", K_MS, D, TM)
    # ---- T_X, and the T_M recount from x-multisets with canonical sign patterns
    TX, TMre, st = kernel.run_hist(E, K_XM, m, X_lifts, need2=True)
    ident["iv_TM_vs_xmultiset_recount"] = kernel.cmp(TM, TMre, mask)
    ident["iv_TX_not_above_TM"] = kernel.cmp(TX, TM, mask)
    record("X", TX, st["leaves"])
    if recount:
        h, h2, _ = kernel.run_hist(E, K_XM, m, list(reversed(X_lifts)), need2=True, ref=True)
        c1, c2 = kernel.cmp(TX, h, mask), kernel.cmp(TMre, h2, mask)
        rec["X"] = {"differ": c1["differ"], "differ_second": c2["differ"], "compared": c1["compared"]}
        del h, h2
    if keep:
        arrays["M"], arrays["X"], arrays["Mre"] = TM, TX, TMre
    del TM, TX, TMre
    # ---- T_S: ordered x-tuples with sign classes, against ordered tuples weighted by 2^j
    TA2, _, _ = kernel.run_hist(E, K_ORD2, m, D)
    TS, _, st = kernel.run_hist(E, K_ORD, m, Dprime)
    record("S", TS, st["leaves"])
    ident["i_sum_S"] = {"observed": kernel.hist_sum(TS, mask), "expected": (B + t2) ** m}
    ident["iii_TS_vs_TA_weighted_2j"] = kernel.cmp(TS, TA2, mask, skip=2)
    recount_check("S", K_ORD, Dprime, TS)
    if keep:
        arrays["S"], arrays["A2"] = TS, TA2
        out["arrays"], out["mask"] = arrays, mask
    del TS, TA2
    return out




# ----------------------------------------------------------------------------- arm C
def sample_targets(kernel: Kernel, E: Curve, s: int, rng, excluded_x_codes):
    """Targets by uniform x in F_Q with chi(f(x)) = +1 and a uniform sign, one representative per +- class
    (distinct x), excluding classes whose x lies in `excluded_x_codes` (the S set). Draws continue until s
    classes are held. rng draws, in blocks: integers(0, q, size=(block, n)) for x, then integers(0, 2,
    size=block) for the sign; block = max(1024, 2*remaining) (deterministic). Returns (keys, n_draws)
    with keys[i] = 2*code(x) + sign (the kernel target index of the representative)."""
    F = E.F
    keys, seen = [], set()
    draws = 0
    while len(keys) < s:
        block = max(1024, 2 * (s - len(keys)))
        if draws > 100 * s + 100000:
            raise ValueError("target sampler exceeded its draw bound: fewer than s eligible classes?")
        xs = rng.integers(0, F.q, size=(block, F.n))
        signs = rng.integers(0, 2, size=block)
        chi = kernel.chi_batch(E, xs)
        draws += block
        codes = np.zeros(block, dtype=np.uint64)
        for i in range(F.n - 1, -1, -1):
            codes = codes * np.uint64(F.q) + xs[:, i].astype(np.uint64)
        for c, sg, ch in zip(codes.tolist(), signs.tolist(), chi.tolist()):
            if ch != 1 or c in seen or c in excluded_x_codes:
                continue
            seen.add(c)
            keys.append(2 * c + sg)
            if len(keys) == s:
                break
    return np.array(keys, dtype=np.uint64), draws


def arm_c_cell(kernel: Kernel, E: Curve, D, m: int, s: int, target_rng, N: int):
    """Target-sampled, base-exhaustive counter. Enumerates all C(B+m-1, m) multisets of D once. Returns
    the per-target counts of the s sampled generic targets, the counts at the S targets (T4), the exact
    lambda = (N_cf - m_S)/(N - |S|) and the bookkeeping."""
    F = E.F
    B = len(D)
    t2 = sum(1 for P in D if F.is_zero(P[1]))
    S_idx = s_set_indices(kernel, E, D, m)
    S_x = {int(i) >> 1 for i in S_idx.tolist() if int(i) != 2 * F.Q}
    keys, draws = sample_targets(kernel, E, s, target_rng, S_x)
    allkeys = np.concatenate([keys, S_idx.astype(np.uint64)])
    counts, st = kernel.run_sampled(E, m, D, allkeys, keys.size)
    N_cf = ncf_coefficient(B, t2, m)
    lam = Fraction(N_cf - st["m_S"], N - int(S_idx.size))
    return {"sampled_counts": counts[:keys.size], "S_counts": counts[keys.size:], "keys": keys,
            "S_size": int(S_idx.size), "draws": draws, "B": B, "t2": t2, "N": N, "m": m, "s": s,
            "multisets": st["multisets"], "cancellation_free": st["cancellation_free"], "m_S": st["m_S"],
            "N_cf_formula": N_cf, "lambda": lam}


def poisson_pmf_list(lam: float, kmax: int):
    out = [math.exp(-lam)]
    for k in range(1, kmax + 1):
        out.append(out[-1] * lam / k)
    return out


def poisson_upper_tail(lam: float, c: int) -> float:
    """P(X >= c) for X ~ Poisson(lam), by summing the upper pmf terms (accurate for small tails)."""
    if c <= 0:
        return 1.0
    term = math.exp(-lam + c * math.log(lam) - math.lgamma(c + 1)) if lam > 0 else 0.0
    tot, k = 0.0, c
    while True:
        tot += term
        k += 1
        term *= lam / k
        if term < 1e-18 * tot or k > c + 2000:
            break
    return min(1.0, tot)


def poisson_summary(counts, lam: float):
    """Statistics of the empirical count law against Poisson(lam), keys as the IDEA's cdf.json.
    counts: integer array of per-target counts over the s sampled generic targets."""
    counts = np.asarray(counts, dtype=np.int64)
    s = int(counts.size)
    hist = {int(c): int(v) for c, v in zip(*np.unique(counts, return_counts=True))}
    mx = max(hist)
    mean = float(counts.mean())
    var = float(counts.var(ddof=1)) if s > 1 else float("nan")
    pm = poisson_pmf_list(lam, mx)
    emp, cum = [], 0
    for k in range(mx + 1):
        cum += hist.get(k, 0)
        emp.append(cum / s)
    cdf_p, c = [], 0.0
    for k in range(mx + 1):
        c += pm[k]
        cdf_p.append(min(1.0, c))
    ks = max(abs(a - b) for a, b in zip(emp, cdf_p))
    # chi-square with bins pooled from the right until expected >= 5
    bins_obs, bins_exp = [], []
    acc_o = acc_e = 0.0
    for k in range(mx + 1):
        acc_o += hist.get(k, 0)
        acc_e += s * pm[k]
        if acc_e >= 5.0 and k < mx:
            bins_obs.append(acc_o); bins_exp.append(acc_e); acc_o = acc_e = 0.0
    tail_e = s * poisson_upper_tail(lam, mx + 1)
    acc_o += 0
    acc_e += tail_e
    if bins_obs and acc_e < 5.0:
        bins_obs[-1] += acc_o; bins_exp[-1] += acc_e
    else:
        bins_obs.append(acc_o); bins_exp.append(acc_e)
    chi2 = sum((o - e) ** 2 / e for o, e in zip(bins_obs, bins_exp) if e > 0)
    tail = poisson_upper_tail(lam, mx)
    p_max = -math.expm1(s * math.log1p(-tail)) if tail < 1 else 1.0
    return {"s": s, "lambda": lam, "hist": {str(k): v for k, v in sorted(hist.items())},
            "cdf_empirical": emp, "cdf_poisson": cdf_p, "ks_stat": ks, "chi2_stat": chi2,
            "chi2_df": max(len(bins_obs) - 1, 0), "zero_fraction": hist.get(0, 0) / s,
            "coverage": 1 - hist.get(0, 0) / s, "dispersion_index": var / mean if mean > 0 else None,
            "max_count": mx, "p_max_pred": p_max, "mean": mean}


def x_lifts(F: FQ, pts):
    """One lift per distinct x of the base: the point with the smaller y code (2-torsion points once),
    sorted by code(x). This is L(x) of T_S and T_X."""
    best = {}
    for (x, y) in pts:
        cur = best.get(x)
        if cur is None or F.to_code(y) < F.to_code(cur):
            best[x] = y
    return [(x, best[x]) for x in sorted(best, key=F.to_code)]
