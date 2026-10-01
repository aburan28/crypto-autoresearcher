#!/usr/bin/env python3
"""Separate-process verifier for EXP-CERTBIN-060020 (specification
object.verifier, V1-V6).

IMPORT RULE: this file imports only the Python standard library, numpy and
PyYAML. It imports nothing from experiments/EXP-CERTBIN-060020/impl/, from
crypto_autoresearcher (any module), from any archived impl/ or from any review
directory; main() asserts this at start and at exit.

Own components (written independently of impl/):
  * F_{2^n} by schoolbook carry-less multiplication and reduction; inverse by
    Fermat (a^(2^n - 2)); trace and half-trace by repeated squaring.
  * S_3 descent by the CLOSED FORM derived by hand from
    S_3 = ((x1 + x3) x2 + x1 x3)^2 + x1 x2 x3 + B:
      coefficient of v_i v_{l+j}: t^{2(i+j)} + x_R t^{i+j};
      of v_i: x_R^2 t^{2i}; of v_{l+j}: x_R^2 t^{2j}; constant: B.
  * exhaustive s by full-width bit-sliced monomial truth tables (2^nv bits).
  * subgroup (x(2E)) test by the x-only Lopez-Dahab Montgomery ladder;
    S3-PRIMARY targets by own affine formulas.
  * certificates: multilinear arithmetic on numpy arrays of monomial masks.
  * ann-v1: own GF(2) elimination and float BLAS products reduced mod 2.

    python3 verify_n19.py --run RUN_DIR --spec SPEC --out RUN_DIR
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import sys
import time
from itertools import combinations

import numpy as np
import yaml

FORBIDDEN_PREFIXES = ("crypto_autoresearcher",)
IMPL_MODULE_NAMES = ("common", "gf2n", "curve", "descent", "oracles", "arms", "closures",
                     "analysis", "literal", "driver", "selftest", "engine_provenance",
                     "make_trial_plan", "rcb", "certs")


def assert_independent():
    bad = [m for m in sys.modules if m.startswith(FORBIDDEN_PREFIXES)]
    here = os.path.dirname(os.path.abspath(__file__))
    for name in IMPL_MODULE_NAMES:
        mod = sys.modules.get(name)
        f = getattr(mod, "__file__", None) if mod else None
        if f and os.path.realpath(f) != os.path.realpath(__file__) and "EXP-CERTBIN" in f:
            bad.append(f"{name} ({f})")
    me = os.path.realpath(__file__)
    for m, mod in list(sys.modules.items()):
        f = os.path.realpath(getattr(mod, "__file__", None) or "") if getattr(mod, "__file__", None) else ""
        if f == me:
            continue
        if "/impl/" in f and "EXP-CERTBIN" in f:
            bad.append(f"{m} ({f})")
        if "coordination/review" in f:
            bad.append(f"{m} ({f})")
    del here
    if bad:
        raise SystemExit(f"verifier independence violated: {bad}")


# =============================================================================
# field
# =============================================================================
class GF:
    def __init__(self, n, f):
        self.n, self.f = n, f
        self.trm = 0
        for j in range(n):
            if self._tr_slow(1 << j):
                self.trm |= 1 << j

    def red(self, a):
        n, f = self.n, self.f
        while a >> n:
            d = a.bit_length() - 1 - n
            a ^= f << d
        return a

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            a <<= 1
            b >>= 1
        return self.red(r)

    def sq(self, a):
        return self.mul(a, a)

    def pw(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a):
        assert a
        return self.pw(a, (1 << self.n) - 2)

    def _tr_slow(self, a):
        r, x = 0, a
        for _ in range(self.n):
            r ^= x
            x = self.mul(x, x)
        return r

    def tr(self, a):
        return bin(a & self.trm).count("1") & 1



class Ell:
    """E: y^2 + x y = x^3 + a x^2 + b; affine, O = None."""

    def __init__(self, K, a, b):
        self.K, self.a, self.b = K, a, b

    def add(self, P, Q):
        K = self.K
        if P is None:
            return Q
        if Q is None:
            return P
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2:
            if y1 ^ y2 == x1:  # Q = -P  (-P = (x, x + y))
                return None
            if y1 == y2:
                if x1 == 0:
                    return None
                m = x1 ^ K.mul(y1, K.inv(x1))
                x3 = K.sq(m) ^ m ^ self.a
                return (x3, K.sq(x1) ^ K.mul(m ^ 1, x3))
        m = K.mul(y1 ^ y2, K.inv(x1 ^ x2))
        x3 = K.sq(m) ^ m ^ x1 ^ x2 ^ self.a
        y3 = K.mul(m, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def smul(self, k, P):
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R

    def ladder_is_O(self, k, x):
        """x-only Lopez-Dahab ladder: is [k](x, y) = O for a point with x != 0?"""
        K = self.K
        X1, Z1 = x, 1
        X2, Z2 = K.sq(K.sq(x)) ^ self.b, K.sq(x)
        for bit in bin(k)[3:]:
            if bit == "1":
                t1, t2 = K.mul(X1, Z2), K.mul(X2, Z1)
                Z1n = K.sq(t1 ^ t2)
                X1n = K.mul(x, Z1n) ^ K.mul(t1, t2)
                X2n = K.sq(K.sq(X2)) ^ K.mul(self.b, K.sq(K.sq(Z2)))
                Z2n = K.mul(K.sq(X2), K.sq(Z2))
                X1, Z1, X2, Z2 = X1n, Z1n, X2n, Z2n
            else:
                t1, t2 = K.mul(X1, Z2), K.mul(X2, Z1)
                Z2n = K.sq(t1 ^ t2)
                X2n = K.mul(x, Z2n) ^ K.mul(t1, t2)
                X1n = K.sq(K.sq(X1)) ^ K.mul(self.b, K.sq(K.sq(Z1)))
                Z1n = K.mul(K.sq(X1), K.sq(Z1))
                X1, Z1, X2, Z2 = X1n, Z1n, X2n, Z2n
        return Z1 == 0


# =============================================================================
# systems: layout, closed-form descent, exhaustive evaluation
# =============================================================================
class Layout:
    def __init__(self, nv):
        self.nv = nv
        self.mons = [()] + [(i,) for i in range(nv)] + list(combinations(range(nv), 2))
        self.masks = np.array([sum(1 << i for i in m) for m in self.mons], dtype=np.int64)
        self.ncol = len(self.mons)
        self.pair_col = {}
        for c, m in enumerate(self.mons):
            if len(m) == 2:
                self.pair_col[m] = c


def closed_form_E(K, lay, l, xR, Bc):
    n = K.n
    E = np.zeros((n, lay.ncol), dtype=np.uint8)

    def put(col, val):
        for k in range(n):
            if (val >> k) & 1:
                E[k, col] ^= 1
    xR2 = K.sq(xR)
    put(0, Bc)
    for i in range(l):
        put(1 + i, K.mul(xR2, K.sq(1 << i)))
        put(1 + l + i, K.mul(xR2, K.sq(1 << i)))
    for i in range(l):
        for j in range(l):
            tij = K.red(1 << (i + j))
            put(lay.pair_col[(i, l + j)], K.sq(tij) ^ K.mul(xR, tij))
    return E


def E_hex(E):
    out = []
    for row in E:
        v = 0
        for j in np.flatnonzero(row):
            v |= 1 << int(j)
        out.append(format(v, "x"))
    return out


def E_from_hex(hexes, ncol):
    E = np.zeros((len(hexes), ncol), dtype=np.uint8)
    for k, h in enumerate(hexes):
        v = int(h, 16)
        for j in range(ncol):
            if (v >> j) & 1:
                E[k, j] = 1
    return E


def E_sha(E):
    return hashlib.sha256(json.dumps(E_hex(E), separators=(",", ":")).encode()).hexdigest()


class Brute:
    """Full-width bit-sliced truth tables of the degree-<=2 monomials."""

    def __init__(self, lay):
        nv = lay.nv
        self.nv = nv
        nbits = 1 << nv
        u = np.arange(nbits, dtype=np.int64)
        var = [((u >> i) & 1).astype(np.uint8) for i in range(nv)]
        T = []
        for m in lay.mons:
            t = np.ones(nbits, dtype=np.uint8)
            for i in m:
                t = t & var[i]
            T.append(np.packbits(t, bitorder="little").view(np.uint64))
        self.T = np.array(T)

    def solve(self, E):
        acc = np.zeros(self.T.shape[1], dtype=np.uint64)
        for k in range(E.shape[0]):
            cols = np.flatnonzero(E[k])
            if cols.size:
                acc |= np.bitwise_xor.reduce(self.T[cols], axis=0)
        zeros = np.flatnonzero(np.unpackbits(acc.view(np.uint8), bitorder="little") == 0)
        return int(zeros.size), zeros.tolist()


# =============================================================================
# draw replay (V3)
# =============================================================================
def gen(seed):
    return np.random.Generator(np.random.PCG64(seed))


class Replay:
    def __init__(self, P):
        self.P = P
        self.K = GF(P["n"], P["modulus"])
        self.K17 = None
        self.lay = Layout(2 * P["l"])
        self.cur = Ell(self.K, P["A"], P["B"])
        self.br = Brute(self.lay)
        l, n = P["l"], P["n"]
        self.E0 = closed_form_E(self.K, self.lay, l, 0, P["B"])
        self.Ej = [closed_form_E(self.K, self.lay, l, 1 << j, P["B"]) ^ self.E0 for j in range(n)]
        U = self.E0.astype(bool)
        for e in self.Ej:
            U = U | e.astype(bool)
        self.U = U
        self.Upos = np.flatnonzero(U.ravel())
        low = np.zeros_like(U)
        low[:, :1 + 2 * l] = True
        self.SL = np.flatnonzero((U & low).ravel())
        self.tau = [self.K.tr(1 << j) for j in range(n)]
        ell = np.zeros(self.lay.ncol, dtype=np.uint8)
        for j in range(l):
            if self.tau[j]:
                ell[1 + j] ^= 1
                ell[1 + l + j] ^= 1
        self.ell_lin = ell
        self.systems = {}  # key -> dict(E, s, sols, meta)
        self.log = {}

    def E(self, xR):
        return closed_form_E(self.K, self.lay, self.P["l"], xR, self.P["B"])

    def keep(self, arm, role, E, s, sols, **meta):
        idx = sum(1 for k in self.systems if k.startswith(arm + ":"))
        key = f"{arm}:{idx}"
        self.systems[key] = {"E": E, "s": s, "sols": sols, "role": role, "arm": arm, **meta}
        return key

    def primary(self, seed, n_u, n_s, cap):
        P = self.P
        g = gen(seed)
        Pp, Qp = tuple(P["P"]), tuple(P["Q"])
        nu = ns = 0
        seen = set()
        self.all_x = set()
        self.classified = []
        att = 0
        outs = []
        while att < cap and (nu < n_u or ns < n_s):
            a = int(g.integers(0, P["q"]))
            b = int(g.integers(0, P["q"]))
            R = self.cur.add(self.cur.smul(a, Pp), self.cur.smul(b, Qp))
            if R is None:
                outs.append((att, "R_is_O", None))
            else:
                x = R[0]
                self.all_x.add(x)
                if x < (1 << P["l"]):
                    outs.append((att, "degenerate", None))
                elif x in seen:
                    outs.append((att, "duplicate", None))
                else:
                    seen.add(x)
                    E = self.E(x)
                    s, sols = self.br.solve(E)
                    self.classified.append((att, x, s))
                    if s == 0:
                        if nu < n_u:
                            self.keep("S3-U400", "unsat", E, s, sols, x_R=x, attempt=att)
                            nu += 1
                            outs.append((att, "kept:S3-U400", s))
                        else:
                            outs.append((att, "unsat_not_kept", s))
                    else:
                        if ns < n_s:
                            self.keep("S3-SAT100", "sat", E, s, sols, x_R=x, attempt=att)
                            ns += 1
                            outs.append((att, "kept:S3-SAT100", s))
                        else:
                            outs.append((att, "sat_not_kept", s))
            att += 1
        self.log["S3-PRIMARY"] = outs

    def conv(self, seed, n_slots, n_sat_slots, per_slot):
        g = gen(seed)
        slots = [k for k in self.systems if k.startswith("S3-U400:")][:n_slots]
        kept_sha = set()
        nq = 1 + self.lay.nv
        outs = []
        for i, sk in enumerate(slots):
            Es = self.systems[sk]["E"]
            need_u, need_s = True, i < n_sat_slots
            for att in range(per_slot):
                if not (need_u or need_s):
                    break
                bits = g.integers(0, 2, size=self.SL.size)
                Ed = np.zeros_like(Es)
                Ed[:, nq:] = Es[:, nq:]
                Ed.reshape(-1)[self.SL] = bits.astype(np.uint8)
                sha = E_sha(Ed)
                if np.array_equal(Ed, Es):
                    outs.append((i, att, "identity", None))
                    continue
                if sha in kept_sha:
                    outs.append((i, att, "duplicate", None))
                    continue
                s, sols = self.br.solve(Ed)
                if s == 0 and need_u:
                    self.keep("N-CONV19", "unsat", Ed, s, sols, slot=i, attempt=att,
                              x_R=self.systems[sk]["x_R"])
                    kept_sha.add(sha)
                    need_u = False
                    outs.append((i, att, "kept:unsat", s))
                elif s > 0 and need_s:
                    self.keep("N-CONV19", "sat", Ed, s, sols, slot=i, attempt=att,
                              x_R=self.systems[sk]["x_R"])
                    kept_sha.add(sha)
                    need_s = False
                    outs.append((i, att, "kept:sat", s))
                else:
                    outs.append((i, att, "not_needed", s))
        self.log["N-CONV19"] = outs

    def stream(self, arm, seed, with_ell, n_u, n_s, cap):
        g = gen(seed)
        n, ncol = self.P["n"], self.lay.ncol
        seen = set()
        got_u, got_s = [], []
        outs = []
        k = 0
        while k < cap and (len(got_u) < n_u or len(got_s) < n_s):
            flat = np.zeros(n * ncol, dtype=np.uint8)
            flat[self.Upos] = g.integers(0, 2, size=self.Upos.size).astype(np.uint8)
            M = flat.reshape(n, ncol)
            if with_ell:
                c = int(g.integers(0, 2))
                row = self.ell_lin.copy()
                row[0] ^= c
                M[n - 1] = row
            sha = E_sha(M)
            if sha in seen:
                outs.append((k, "duplicate", None))
            else:
                seen.add(sha)
                s, sols = self.br.solve(M)
                if s == 0 and len(got_u) < n_u:
                    got_u.append((k, M.copy(), s, sols))
                    outs.append((k, "kept:unsat", s))
                elif s > 0 and len(got_s) < n_s:
                    got_s.append((k, M.copy(), s, sols))
                    outs.append((k, "kept:sat", s))
                else:
                    outs.append((k, "not_needed", s))
            k += 1
        allk = sorted([(d, "unsat", M, s, so) for d, M, s, so in got_u] +
                      [(d, "sat", M, s, so) for d, M, s, so in got_s], key=lambda t: t[0])
        for d, role, M, s, so in allk:
            self.keep(arm, role, M, s, so, attempt=d)
        self.log[arm] = outs

    def aff(self, seed, n_fam, n_u, n_s):
        g = gen(seed)
        n, ncol = self.P["n"], self.lay.ncol
        fams = []
        for _ in range(n_fam):
            e0 = np.zeros(n * ncol, dtype=np.uint8)
            nz = np.flatnonzero(self.E0.ravel())
            e0[nz] = g.integers(0, 2, size=nz.size).astype(np.uint8)
            ej = []
            for j in range(n):
                e = np.zeros(n * ncol, dtype=np.uint8)
                nz = np.flatnonzero(self.Ej[j].ravel())
                e[nz] = g.integers(0, 2, size=nz.size).astype(np.uint8)
                ej.append(e.reshape(n, ncol))
            fams.append((e0.reshape(n, ncol), ej))
        outs = []
        for d, (e0, ej) in enumerate(fams, start=1):
            seen = set()
            ku = ks = 0
            for att, x, _ in self.classified:
                if ku >= n_u and ks >= n_s:
                    break
                M = e0.copy()
                for j in range(n):
                    if (x >> j) & 1:
                        M = M ^ ej[j]
                sha = E_sha(M)
                if sha in seen:
                    outs.append((d, att, "duplicate", None))
                    continue
                seen.add(sha)
                s, sols = self.br.solve(M)
                if s == 0 and ku < n_u:
                    self.keep("N-AFF19", "unsat", M, s, sols, family=d, attempt=att, x_R=x)
                    ku += 1
                    outs.append((d, att, "kept:unsat", s))
                elif s > 0 and ks < n_s:
                    self.keep("N-AFF19", "sat", M, s, sols, family=d, attempt=att, x_R=x)
                    ks += 1
                    outs.append((d, att, "kept:sat", s))
                else:
                    outs.append((d, att, "not_needed", s))
        self.log["N-AFF19"] = outs

    def randx(self, seed, quota, cap):
        P, K = self.P, self.K
        g = gen(seed)
        strata = {"X2E": [], "XE-NOT-2E": [], "TWIST": []}
        seen = set()
        outs = []
        tr_bad = []
        att = 0
        while att < cap and any(len(v) < quota for v in strata.values()):
            x = int(g.integers(0, 1 << P["n"]))
            a = att
            att += 1
            if x < (1 << P["l"]):
                outs.append((a, "degenerate", None, None))
                continue
            if x in seen:
                outs.append((a, "duplicate", None, None))
                continue
            seen.add(x)
            if x in self.all_x:
                outs.append((a, "primary_collision", None, None))
                continue
            c = x ^ P["A"] ^ K.mul(P["B"], K.inv(K.sq(x)))
            if K.tr(c):
                st = "TWIST"
            else:
                st = "X2E" if self.cur.ladder_is_O(P["q"], x) else "XE-NOT-2E"
                if (st == "X2E") != (K.tr(x) == K.tr(P["A"])):
                    tr_bad.append(a)
            if len(strata[st]) >= quota:
                outs.append((a, "quota_full", st, None))
                continue
            E = self.E(x)
            s, sols = self.br.solve(E)
            if s == 0:
                strata[st].append((a, x, E))
                outs.append((a, "kept:unsat", st, s))
            else:
                outs.append((a, "sat_recorded", st, s))
        allk = sorted([(a, x, E, st) for st, v in strata.items() for a, x, E in v], key=lambda t: t[0])
        for a, x, E, st in allk:
            self.keep("F-RANDX19", "unsat", E, 0, [], stratum=st, attempt=a, x_R=x)
        self.log["F-RANDX19"] = outs
        self.randx_tr_bad = tr_bad


# =============================================================================
# multilinear certificate arithmetic (V4)
# =============================================================================
def parity(masks):
    if masks.size == 0:
        return masks
    u, c = np.unique(masks, return_counts=True)
    return u[(c & 1) == 1]


def popc(a):
    a = a.astype(np.int64)
    c = np.zeros(a.shape, dtype=np.int64)
    x = a.copy()
    while np.any(x):
        c += x & 1
        x >>= 1
    return c


class Sys:
    def __init__(self, E, lay):
        self.f = [lay.masks[np.flatnonzero(E[k])] for k in range(E.shape[0])]


def rows_sum(pairs, sysf):
    """sum mu * f_k over pairs [(mu_mask, k)] -> parity array."""
    byk = {}
    for mu, k in pairs:
        byk.setdefault(k, []).append(mu)
    parts = []
    for k, mus in byk.items():
        fk = sysf.f[k]
        if fk.size == 0:
            continue
        mu = np.array(mus, dtype=np.int64)
        parts.append((mu[:, None] | fk[None, :]).ravel())
    if not parts:
        return np.zeros(0, dtype=np.int64)
    return parity(np.concatenate(parts))


def mu_mask(lst, nv):
    m = 0
    for i in lst:
        if not (isinstance(i, int) and 0 <= i < nv):
            raise ValueError(f"bad variable index {i!r}")
        if (m >> i) & 1:
            raise ValueError("repeated variable in mu")
        m |= 1 << i
    return m


def check_flat(body, sysf, nv, neq):
    """-> (algebra_ok, max|mu|, reasons)."""
    reasons = []
    try:
        C = body["C"]
        pairs = []
        for mu, k in C:
            if not (isinstance(k, int) and 0 <= k < neq):
                raise ValueError(f"bad k {k!r}")
            pairs.append((mu_mask(mu, nv), k))
    except Exception as exc:  # malformed
        return False, None, [f"format: {exc}"]
    if len(set(pairs)) != len(pairs):
        reasons.append("duplicate pairs")
    maxmu = max((bin(m).count("1") for m, _ in pairs), default=0)
    s = rows_sum(pairs, sysf)
    ok = s.size == 1 and int(s[0]) == 0
    if not ok:
        reasons.append(f"sum is not 1 ({s.size} monomials)")
    return ok and not reasons, maxmu, reasons


def check_wdag(body, sysf, nv, neq, D):
    """Rules (a)-(e) of wdag-v1 -> (valid, reasons, stats)."""
    reasons = []
    try:
        if body.get("D") != D or body.get("nv") != nv or body.get("neq") != neq:
            reasons.append(f"header mismatch D/nv/neq {body.get('D')}/{body.get('nv')}/{body.get('neq')}")
        nodes = body["nodes"]
        out = body["output"]
        polys = []
        degs = []
        maxmu = 0
        for i, nd in enumerate(nodes):
            if nd["id"] != i:
                raise ValueError(f"node {i} has id {nd['id']}")
            pairs = []
            for mu, k in nd["rows"]:
                if not (isinstance(k, int) and 0 <= k < neq):
                    reasons.append(f"(b) node {i}: k {k!r} out of range")
                    continue
                m = mu_mask(mu, nv)
                if bin(m).count("1") > D - 2:
                    reasons.append(f"(b) node {i}: |mu| = {bin(m).count('1')} > {D - 2}")
                maxmu = max(maxmu, bin(m).count("1"))
                pairs.append((m, k))
            acc = [rows_sum(pairs, sysf)]
            for j, c in nd["prods"]:
                if not (isinstance(j, int) and 0 <= j < nv):
                    raise ValueError(f"node {i}: bad variable {j!r}")
                if not (isinstance(c, int) and 0 <= c < i):
                    reasons.append(f"(a) node {i}: child {c!r} not < {i}")
                    continue
                if degs[c] > D - 1:
                    reasons.append(f"(c) node {i}: child {c} has degree {degs[c]} > {D - 1}")
                acc.append(polys[c] | np.int64(1 << j))
            p = parity(np.concatenate(acc)) if len(acc) > 1 else acc[0]
            dg = int(popc(p).max()) if p.size else -1
            if dg > D:
                reasons.append(f"(d) node {i}: degree {dg} > {D}")
            polys.append(p)
            degs.append(dg)
        if not (isinstance(out, int) and 0 <= out < len(nodes)):
            raise ValueError(f"bad output {out!r}")
        po = polys[out]
        if not (po.size == 1 and int(po[0]) == 0):
            reasons.append(f"(e) poly(output) is not 1 ({po.size} monomials)")
        stats = {"n_nodes": len(nodes), "n_rows": sum(len(nd["rows"]) for nd in nodes),
                 "n_prods": sum(len(nd["prods"]) for nd in nodes), "max_mu": maxmu,
                 "max_node_degree": max(degs) if degs else None}
    except Exception as exc:
        return False, [f"format: {exc}"], {}
    return not reasons, reasons, stats


# =============================================================================
# ann-v1 (V6)
# =============================================================================
class Space:
    """B_{<=D} in nv variables, coordinates sorted by (-degree, bitmask)."""

    def __init__(self, nv, D):
        mons = []
        for d in range(D + 1):
            for m in combinations(range(nv), d):
                mons.append(sum(1 << i for i in m))
        mons.sort(key=lambda m: (-bin(m).count("1"), m))
        self.nv, self.D = nv, D
        self.masks = np.array(mons, dtype=np.int64)
        self.C = len(mons)
        self.deg = popc(self.masks)
        self.index = {int(m): c for c, m in enumerate(mons)}
        self.low = np.flatnonzero(self.deg <= D - 1)
        self.const = self.index[0]
        idx = np.full(1 << nv, -1, dtype=np.int64) if nv <= 22 else None
        idx[self.masks] = np.arange(self.C)
        self.lookup = idx
        self.mulmap = [idx[self.masks[self.low] | (1 << j)] for j in range(nv)]

    def macaulay_dense(self, sysf, neq):
        mus = []
        for d in range(self.D - 1):
            for m in combinations(range(self.nv), d):
                mus.append(sum(1 << i for i in m))
        rows = np.zeros((len(mus) * neq, self.C), dtype=np.uint8)
        r = 0
        for mu in mus:
            for k in range(neq):
                fk = sysf.f[k]
                if fk.size:
                    p = parity(mu | fk)
                    rows[r, self.lookup[p]] = 1
                r += 1
        return rows


def gf2_nullspace(A):
    """Basis of {x : A x = 0} over F_2 (A uint8, rows x cols) -> uint8 matrix."""
    A = (A & 1).astype(np.uint8)
    nr, nc = A.shape
    nw = (nc + 63) // 64
    pad = nw * 64 - nc
    Ap = np.concatenate([A, np.zeros((nr, pad), np.uint8)], axis=1) if pad else A
    M = np.packbits(Ap, axis=1, bitorder="little").view(np.uint64).reshape(nr, nw).copy()
    pivcols = []
    r = 0
    for c in range(nc):
        if r >= nr:
            break
        w, b = c >> 6, np.uint64(c & 63)
        col = (M[r:, w] >> b) & np.uint64(1)
        nz = np.flatnonzero(col)
        if nz.size == 0:
            continue
        p = r + int(nz[0])
        if p != r:
            M[[r, p]] = M[[p, r]]
        colall = (M[:, w] >> b) & np.uint64(1)
        colall[r] = 0
        hit = np.flatnonzero(colall)
        if hit.size:
            M[hit] ^= M[r]
        pivcols.append(c)
        r += 1
    R = np.unpackbits(M[:r].view(np.uint8), axis=1, bitorder="little")[:, :nc]
    piv = np.array(pivcols, dtype=np.int64)
    isp = np.zeros(nc, dtype=bool)
    isp[piv] = True
    free = np.flatnonzero(~isp)
    Kb = np.zeros((free.size, nc), dtype=np.uint8)
    Kb[np.arange(free.size), free] = 1
    if piv.size:
        Kb[:, piv] = R[:, free].T
    return Kb


def matmul2(A, B):
    """(A @ B) mod 2 for 0/1 uint8 matrices, exact via float32 (dims < 2^24)."""
    return (np.rint(A.astype(np.float32) @ B.astype(np.float32)).astype(np.int64) & 1).astype(np.uint8)


def check_ann(body, sysf, sp, neq, M4dense=None):
    reasons = []
    try:
        if body.get("D") != sp.D or body.get("nv") != sp.nv or body.get("neq") != neq:
            reasons.append("header mismatch")
        Lh = body["L_hex"]
        nb = (sp.C + 7) // 8
        L = np.zeros((len(Lh), sp.C), dtype=np.uint8)
        for i, h in enumerate(Lh):
            v = int(h, 16)
            if v >> sp.C:
                raise ValueError("functional has bits beyond the coordinate count")
            L[i] = np.unpackbits(np.frombuffer(v.to_bytes(nb, "little"), dtype=np.uint8),
                                 bitorder="little")[:sp.C]
    except Exception as exc:
        return False, [f"format: {exc}"], {}
    if M4dense is None:
        M4dense = sp.macaulay_dense(sysf, neq)
    LT = L.T.copy()
    a1 = matmul2(M4dense, LT)
    bad_rows = np.flatnonzero(a1.any(axis=1))
    if bad_rows.size:
        reasons.append(f"(A1) {bad_rows.size} Macaulay rows not in S (first row index {int(bad_rows[0])})")
    Llow = L[:, sp.low]
    K = gf2_nullspace(Llow)  # basis of S cap B_{<=D-1}, low coordinates
    a2_bad = 0
    if K.shape[0]:
        KT = K.T.copy()
        for j in range(sp.nv):
            Lj = L[:, sp.mulmap[j]]
            if matmul2(Lj, KT).any():
                a2_bad += 1
    if a2_bad:
        reasons.append(f"(A2) closure fails for {a2_bad} variables")
    a3 = bool(L[:, sp.const].any())
    if not a3:
        reasons.append("(A3) no functional with lambda(1) = 1")
    stats = {"n_functionals": int(L.shape[0]), "dim_S_cap_B_le_D_minus_1": int(K.shape[0])}
    return not reasons, reasons, stats


# =============================================================================
# driver
# =============================================================================
def read_jsonl_gz(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(x) for x in f if x.strip()]


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def load_params(spec_path):
    spec = yaml.safe_load(open(spec_path))["experiment"]
    lp = spec["inputs"]["literal_parameters"]
    seeds = spec["replication"]["seeds"]
    P = {"n": 19, "l": 10, "modulus": int(lp["modulus"].split("(integer ")[1].rstrip(")")),
         "A": int(lp["A"]), "B": int(lp["B"]), "q": int(lp["q"]), "P": list(lp["P"]),
         "Q": list(lp["Q"]), "seeds": [int(s) for s in seeds]}
    assert P["modulus"] == (1 << 19) | (1 << 5) | (1 << 2) | 2 | 1
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quotas", default=None, help="development only: JSON quota override")
    ap.add_argument("--seeds", default=None, help="development only: JSON seed override")
    args = ap.parse_args()
    assert_independent()
    t0 = time.time()
    P = load_params(args.spec)
    if args.seeds:
        P["seeds"] = json.loads(open(args.seeds[1:]).read() if args.seeds.startswith("@") else args.seeds)
    Qt = {"u400": 400, "sat100": 100, "cap_primary": 5000, "conv_slots": 200, "conv_sat_slots": 50,
          "per_slot": 256, "stream_u": 200, "stream_s": 50, "stream_cap": 20000, "aff_fam": 5,
          "aff_u": 40, "aff_s": 10, "randx_quota": 200, "randx_cap": 30000}
    if args.quotas:
        Qt.update(json.loads(open(args.quotas[1:]).read() if args.quotas.startswith("@") else args.quotas))
    run = args.run
    timings = {}

    def tick(name, t):
        timings[name] = round(time.time() - t, 2)
        print(f"[verifier] {name} {timings[name]} s", flush=True)

    # ---- V3 replay + V1 rebuild + V2 exhaustive ------------------------------
    t = time.time()
    rp = Replay(P)
    sd = P["seeds"]
    rp.primary(sd[1], Qt["u400"], Qt["sat100"], Qt["cap_primary"])
    rp.conv(sd[2], Qt["conv_slots"], Qt["conv_sat_slots"], Qt["per_slot"])
    rp.stream("N-ELL19", sd[3], True, Qt["stream_u"], Qt["stream_s"], Qt["stream_cap"])
    rp.stream("N-F219", sd[4], False, Qt["stream_u"], Qt["stream_s"], Qt["stream_cap"])
    rp.aff(sd[5], Qt["aff_fam"], Qt["aff_u"], Qt["aff_s"])
    rp.randx(sd[6], Qt["randx_quota"], Qt["randx_cap"])
    tick("replay_and_rebuild", t)

    inst = read_jsonl_gz(os.path.join(run, "instances.jsonl.gz"))
    by_key = {r["key"]: r for r in inst}
    ncol = rp.lay.ncol
    # V3 comparison
    t = time.time()
    replay = {"per_arm": {}, "mismatches": []}
    arms = ["S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]
    for arm in arms:
        mine = [k for k in rp.systems if k.startswith(arm + ":")]
        theirs = [k for k in by_key if k.startswith(arm + ":")]
        mm = []
        for k in sorted(set(mine) | set(theirs), key=lambda z: int(z.split(":")[1])):
            a, b = rp.systems.get(k), by_key.get(k)
            if a is None or b is None:
                mm.append({"key": k, "reason": "missing in " + ("verifier" if a is None else "run")})
                continue
            if E_sha(a["E"]) != b["E_sha256"]:
                mm.append({"key": k, "reason": "E_sha256 differs"})
            if a.get("attempt") != b.get("attempt"):
                mm.append({"key": k, "reason": f"attempt {a.get('attempt')} != {b.get('attempt')}"})
            for fld in ("slot", "family", "stratum", "x_R"):
                if fld in a and a.get(fld) != b.get(fld):
                    mm.append({"key": k, "reason": f"{fld} differs"})
            if a["role"] != b["role"]:
                mm.append({"key": k, "reason": "role differs"})
        replay["per_arm"][arm] = {"verifier_kept": len(mine), "run_kept": len(theirs),
                                  "mismatches": len(mm), "pass": not mm}
        replay["mismatches"].extend(mm)
    # draw-log outcome sequences
    logs_cmp = {}
    for arm, fname in [("S3-PRIMARY", "draws-S3-PRIMARY.jsonl.gz"), ("N-CONV19", "draws-N-CONV19.jsonl.gz"),
                       ("N-ELL19", "draws-N-ELL19.jsonl.gz"), ("N-F219", "draws-N-F219.jsonl.gz"),
                       ("N-AFF19", "draws-N-AFF19.jsonl.gz"), ("F-RANDX19", "draws-F-RANDX19.jsonl.gz")]:
        path = os.path.join(run, fname)
        if not os.path.exists(path):
            logs_cmp[arm] = {"pass": False, "reason": "draw log missing"}
            continue
        theirs = read_jsonl_gz(path)
        mine = rp.log[arm]
        t_out = [d["outcome"] for d in theirs]
        m_out = [o[1] if arm == "F-RANDX19" else o[-2] for o in mine]
        t_s = [d.get("s") for d in theirs]
        m_s = [o[-1] for o in mine]
        same_out = t_out == m_out
        same_s = t_s == m_s
        logs_cmp[arm] = {"attempts_run": len(theirs), "attempts_verifier": len(mine),
                         "outcomes_equal": same_out, "s_equal": same_s, "pass": same_out and same_s}
    replay["draw_logs"] = logs_cmp
    replay["randx_tr19_violations_verifier"] = rp.randx_tr_bad
    replay["pass"] = all(v["pass"] for v in replay["per_arm"].values()) and all(v["pass"] for v in logs_cmp.values())
    replay["independence"] = "own PCG64 replay with numpy only; own keep rules; own closed-form descent; own exhaustive s"
    write_json(os.path.join(args.out, "draw-replay-verification.json"), replay)
    tick("draw_replay_compare", t)

    # V1 / V2
    t = time.time()
    cons = {"systems": len(inst), "E_mismatch": [], "s_mismatch": [], "solution_failures": [],
            "solution_list_mismatch": [], "verifier_missing": []}
    own_E = {}
    for r in inst:
        k = r["key"]
        Er = E_from_hex(r["E_hex"], ncol)
        a = rp.systems.get(k)
        if a is None:
            cons["verifier_missing"].append(k)
            own_E[k] = None
            continue
        own_E[k] = a["E"]
        if not np.array_equal(a["E"], Er):
            cons["E_mismatch"].append(k)
        if a["s"] != r["s"]:
            cons["s_mismatch"].append({"key": k, "run": r["s"], "verifier": a["s"]})
        if r["role"] == "sat":
            sols = r.get("solutions") or []
            for u in sols:
                val = [0] * Er.shape[0]
                for kk in range(Er.shape[0]):
                    acc = 0
                    for c in np.flatnonzero(a["E"][kk]):
                        m = int(rp.lay.masks[c])
                        if (u & m) == m:
                            acc ^= 1
                    val[kk] = acc
                if any(val):
                    cons["solution_failures"].append({"key": k, "u": u})
            if sorted(sols) != sorted(a["sols"]):
                cons["solution_list_mismatch"].append(k)
    cons["C-ORACLE2_pass"] = not (cons["s_mismatch"] or cons["solution_failures"] or cons["solution_list_mismatch"]
                                   or cons["verifier_missing"])
    cons["V1_construction_pass"] = not (cons["E_mismatch"] or cons["verifier_missing"])
    cons["closed_form_note"] = ("S_3 systems rebuilt by the verifier's closed form; drawn systems by the "
                                "verifier's own replay of each draw rule")
    tick("construction", t)

    # ---- V4 certificates --------------------------------------------------------
    t = time.time()
    nv, neq = rp.lay.nv, P["n"]
    sys_cache = {}

    def sysf_for(k):
        if k not in sys_cache:
            E = own_E.get(k)
            if E is None and k in by_key:
                E = E_from_hex(by_key[k]["E_hex"], ncol)
            sys_cache[k] = Sys(E, rp.lay) if E is not None else None
        return sys_cache[k]

    def verify_cert(rec):
        k = rec["key"]
        sf = sysf_for(k)
        out = {"key": k, "closure": rec["closure"], "format": rec["format"]}
        if sf is None:
            out.update(valid=False, counts=False, reasons=["unknown system"])
            return out
        D = {"M_3": 3, "M_4": 4, "W_4": 4, "W'_4": 4}.get(rec["closure"], 4)
        if rec["format"] == "flat-v1":
            ok, maxmu, reasons = check_flat(rec["body"], sf, nv, neq)
            out.update(valid=ok, max_mu=maxmu, n_pairs=len(rec["body"].get("C", [])), reasons=reasons)
            out["counts"] = bool(ok and maxmu is not None and maxmu <= D - 2)
            if ok and not out["counts"]:
                out["note"] = (f"valid unsatisfiability certificate (1 in M_{2 + maxmu}); "
                               f"max|mu| = {maxmu} > {D - 2}: does not count toward {rec['closure']}")
        elif rec["format"] == "wdag-v1":
            ok, reasons, stats = check_wdag(rec["body"], sf, nv, neq, D)
            out.update(valid=ok, reasons=reasons, **stats)
            out["counts"] = ok and rec["closure"] in ("W_4", "M_4") and (
                rec["closure"] == "W_4" or stats.get("n_prods", 1) == 0)
        else:
            out.update(valid=False, counts=False, reasons=["unknown format"])
        return out

    certs_path = os.path.join(run, "certificates.jsonl.gz")
    cert_results = [verify_cert(r) for r in read_jsonl_gz(certs_path)] if os.path.exists(certs_path) else []
    summ = {}
    for c in cert_results:
        arm = c["key"].split(":")[0]
        s = summ.setdefault(f"{c['closure']}|{arm}|{c['format']}",
                            {"submitted": 0, "valid": 0, "failed": 0, "counting": 0})
        s["submitted"] += 1
        s["valid"] += int(c["valid"])
        s["failed"] += int(not c["valid"])
        s["counting"] += int(c.get("counts", False))
    certver = {"results": cert_results, "summary": summ,
               "C-CERT_pass": all(c["valid"] for c in cert_results),
               "rules": "flat-v1: sum mu f_k == 1 in B, counts toward a closure of degree D iff max|mu| <= D-2; "
                        "wdag-v1: rules (a)-(e) of the specification with own multilinear arithmetic"}
    tick("certificates", t)

    # ---- V6 ann-v1 -----------------------------------------------------------------
    t = time.time()
    sp = Space(nv, 4)
    ann_path = os.path.join(run, "annihilators.jsonl.gz")
    ann_results = []
    ann_recs = read_jsonl_gz(ann_path) if os.path.exists(ann_path) else []
    na_path = os.path.join(run, "annihilators-nonarchived.json")
    if os.path.exists(na_path):
        for f in json.load(open(na_path))["files"]:
            fp = os.path.join(run, f["path"])
            if hashlib.sha256(open(fp, "rb").read()).hexdigest() != f["sha256"]:
                ann_results.append({"key": f["key"], "valid": False, "reasons": ["non-archived file hash mismatch"]})
                continue
            for r in read_jsonl_gz(fp):
                r["_nonarchived"] = True
                ann_recs.append(r)
    if True:
        for rec in ann_recs:
            sf = sysf_for(rec["key"])
            ok, reasons, stats = check_ann(rec["body"], sf, sp, neq)
            ann_results.append({"key": rec["key"], "valid": ok, "reasons": reasons,
                                "archived": not rec.get("_nonarchived", False), **stats})
    annver = {"results": ann_results, "submitted": len(ann_results),
              "verified": sum(r["valid"] for r in ann_results),
              "failed": sum(not r["valid"] for r in ann_results),
              "rules": "(A1)-(A3) with own M_4, own elimination for S cap B_{<=3}, float32 BLAS products mod 2"}
    tick("annihilators", t)

    # ---- V5 negative controls -----------------------------------------------------
    t = time.time()
    nc_path = os.path.join(run, "negative-controls-certificates.jsonl.gz")
    nc_results = []
    if os.path.exists(nc_path):
        for rec in read_jsonl_gz(nc_path):
            if rec["format"] == "ann-v1":
                sf = sysf_for(rec["key"])
                ok, reasons, _ = check_ann(rec["body"], sf, sp, neq)
                accepted = ok
            else:
                r = verify_cert(rec)
                reasons = r.get("reasons", [])
                accepted = bool(r.get("counts")) if rec["closure"] in ("M_4", "W_4") else bool(r.get("valid"))
            nc_results.append({"nc_id": rec["nc_id"], "kind": rec["kind"], "type": rec["type"],
                               "key": rec["key"], "closure": rec["closure"], "format": rec["format"],
                               "accepted": accepted, "rejected": not accepted, "reasons": reasons})
    ncver = {"results": nc_results, "n": len(nc_results),
             "accepted": [r["nc_id"] for r in nc_results if r["accepted"]],
             "C-VERIFIER_negatives_pass": all(r["rejected"] for r in nc_results) and len(nc_results) > 0}
    tick("negative_controls", t)

    timings["total"] = round(time.time() - t0, 2)
    meta = {"verifier": os.path.relpath(os.path.abspath(__file__)),
            "verifier_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
            "numpy": np.__version__, "timings_seconds_measured": timings,
            "modules_loaded_check": "no crypto_autoresearcher / impl / review module loaded (asserted)"}
    certver["meta"] = meta
    annver["meta"] = meta
    ncver["meta"] = meta
    cons["meta"] = meta
    write_json(os.path.join(args.out, "certificate-verification.json"), certver)
    write_json(os.path.join(args.out, "annihilator-verification.json"), annver)
    write_json(os.path.join(args.out, "negative-controls-verification.json"), ncver)
    write_json(os.path.join(args.out, "construction-verification.json"), cons)
    assert_independent()
    print(json.dumps({"C-CERT": certver["C-CERT_pass"], "ann_failed": annver["failed"],
                      "C-VERIFIER_negatives": ncver["C-VERIFIER_negatives_pass"],
                      "C-DRAW": replay["pass"], "C-ORACLE2": cons["C-ORACLE2_pass"],
                      "V1": cons["V1_construction_pass"], "timings": timings}), flush=True)


if __name__ == "__main__":
    main()
