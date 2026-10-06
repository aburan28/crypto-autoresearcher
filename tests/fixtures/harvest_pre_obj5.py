"""Collision harvest for the meet-in-the-middle engine (EXP-PFDR-1b78f7, IC-5).

The mitm engine computes many x-coordinates and keeps only the ones it looks
up.  This module harvests three classes of x-key coincidences among them, turns
each into a certified linear relation among the base logarithms (and k), and
counts them:

* TT -- two stored tails of the table sharing an x-key;
* TB -- a stored tail whose x-key is a base element's x;
* SS -- two search encodings sharing an x-key, where an encoding is one of the
  two finite points R' -/+ F_j of a CHARGED last-level S_3 solve (R' = R_t
  minus the fixed head of attempt t).  Encodings of the same or of different
  targets are both harvested.

Table-vs-search (TS) and search-vs-base coincidences are NOT harvested.

Elements and orientation
------------------------
A base element is F_b (vector e_b); a table element is a stored tail (its
aggregated integer vector v over base indices and its y-bit); a search element
is an encoding (target t, A = aggregated head + s F_j, point R_t - A, y-bit).
Elements sharing an x form a group, ordered base element first, then tails in
stored order, then encodings in recording order.  Every element is oriented to
the group's first element by y-bit (sigma = +1 if equal, else -1).

Formal duplicates, formal classes, rows
---------------------------------------
Two elements whose oriented rows are identical over the integers (same target
part, same aggregated base vector) are one element; the drop is ``dup_formal``.
Formal equivalence is equality of the target part and of the residual of the
oriented base vector reduced against the arm's formal basis (a formal-only
EliminationState, never fed a harvested row).  Rows are star rows: TB = base
vs each distinct tail, TT = first distinct tail vs each other, SS = first
distinct encoding vs each other.  A row X = Y is written

    sum_i c_i L_i + kcoef * k = rhs  (mod N),
    c = sigma_X A_X - sigma_Y A_Y,  kcoef = -(sigma_X b_t - sigma_Y b_u),
    rhs = sigma_X a_t - sigma_Y a_u      (table/base elements: a = b = 0)

and is re-verified as sum_i c_i F_i + kcoef Q == rhs P on an independent Curve
instance (curve.py add/mul, its own OpCounter, no numpy) BEFORE it enters any
elimination.  A failure raises ``CertificateFailure``.

Nothing here touches the solver's E.ops, DecompStats, table or elimination.
"""

from __future__ import annotations

import math
import random
import resource
import time
from collections import Counter

from . import _accel
from .curve import Curve, Point, primitive_root, sqrt_mod
from .linalg import EliminationState

CLASSES = ("TT", "TB", "SS")
T_BITS, H_BITS, J_BITS = 22, 24, 16  # descriptor fields: attempt, head id, base index
BYTES_PER_ENCODING = 12  # x (uint32) + packed descriptor (uint64) in the sorted runs


class CertificateFailure(Exception):
    """A harvested row failed its group-identity certificate (invalidation I-3)."""


class FormalBasisFailure(Exception):
    """The j = 0 lambda check failed on P (invalid run)."""


# -- formal bases ---------------------------------------------------------------------------

def formal_basis_known_log(size: int) -> list[dict[int, int]]:
    """{e_j - j e_1 : j = 2..|F|} with 1-based logs (0-based index j - 1 has log j)."""
    return [{j - 1: 1, 0: -j} for j in range(2, size + 1)]


def j0_omega_lambda(E: Curve, P: Point) -> tuple[int, int]:
    """omega = primitive_root(p)^((p-1)/3) and the root lambda of
    lambda^2 + lambda + 1 = 0 mod N with lambda P == (omega x_P, y_P), checked on
    an independent curve instance.  Neither root matching raises."""
    p, N = E.p, E.order
    omega = pow(primitive_root(p), (p - 1) // 3, p)
    r = sqrt_mod((-3) % N, N)
    if r is None:
        raise FormalBasisFailure("-3 is not a square mod N: no cube root of unity mod N")
    Ev = Curve(E.p, E.a, E.b, E.order)
    target = (omega * P[0] % p, P[1])
    for lam in sorted({(-1 + r) * pow(2, -1, N) % N, (-1 - r) * pow(2, -1, N) % N}):
        if (lam * lam + lam + 1) % N == 0 and Ev.mul(lam, P) == target:
            return omega, lam
    raise FormalBasisFailure("neither root of lambda^2 + lambda + 1 maps P to (omega x_P, y_P)")


def formal_basis_j0(E: Curve, fb, omega: int, lam: int) -> list[dict[int, int]]:
    """e_b - eps*lambda*e_a for every base index a with omega*x_a a base x (index b)."""
    p, N = E.p, E.order
    rows = []
    for a_, Pa in enumerate(fb.points):
        b_ = fb.index.get(omega * Pa[0] % p)
        if b_ is None or b_ == a_:
            continue
        eps = 1 if fb.points[b_][1] == Pa[1] else -1
        rows.append({b_: 1, a_: (-eps * lam) % N})
    return rows


def census_elimination(N: int, formal_rows=()) -> EliminationState:
    """The census rank routine: EliminationState(N, "min_fill") seeded with the formal basis."""
    st = EliminationState(N, "min_fill")
    for r in formal_rows:
        st.add_row(dict(r), 0, 0)
    return st


# -- non-counting affine arithmetic (the recorder's scalar fallback) ----------------------

def _affine_add(p: int, a: int, P: Point, Q: Point) -> Point:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def _pack(t: int, hid: int, j: int, s: int, ybit: int) -> int:
    return ((((t << H_BITS) | hid) << J_BITS | j) << 2) | ((s < 0) << 1) | ybit


def unpack(desc: int) -> tuple[int, int, int, int, int]:
    """(attempt t, head id, base index j, sign s, y-bit) of a packed encoding descriptor."""
    ybit = desc & 1
    s = -1 if desc & 2 else 1
    desc >>= 2
    j = desc & ((1 << J_BITS) - 1)
    desc >>= J_BITS
    hid = desc & ((1 << H_BITS) - 1)
    return desc >> H_BITS, hid, j, s, ybit


class SearchRecorder:
    """Records the encodings of every charged last-level S_3 solve (IC-4).

    decompose.py calls push/pop around each fixed head element and
    ``scan(R', lo, hi)`` with the charged index range of each last-level scan.
    Encodings are computed here: vectorised with the formulas of _accel when
    numpy can be used, else by a non-counting affine addition.
    """

    def __init__(self, fb, p: int, a: int) -> None:
        self.fb, self.p, self.a, self.half = fb, p, a, p // 2
        self.heads: list[tuple] = [()]
        self.head_ids: dict[tuple, int] = {(): 0}
        self.stack: list[tuple[int, int]] = []
        self.t = 0
        self.encodings_recorded = 0
        self.degenerate_roots = 0
        self.seconds = 0.0
        self._xs: list = []
        self._desc: list = []
        self.np = None
        if _accel.usable(p):
            import numpy as np

            self.np = np
            self.FX = np.array([Pt[0] for Pt in fb.points], dtype=np.uint64)
            self.FY = np.array([Pt[1] for Pt in fb.points], dtype=np.uint64)

    def push(self, i: int, s: int) -> None:
        self.stack.append((i, s))

    def pop(self) -> None:
        self.stack.pop()

    def _hid(self) -> int:
        head = tuple(self.stack)
        hid = self.head_ids.get(head)
        if hid is None:
            hid = len(self.heads)
            if hid >= 1 << H_BITS:
                raise OverflowError("too many distinct heads for the descriptor")
            self.heads.append(head)
            self.head_ids[head] = hid
        return hid

    def scan(self, R: Point, lo: int, hi: int) -> None:
        if R is None or hi < lo:
            return
        t0 = time.perf_counter()
        hid, t = self._hid(), self.t
        if t >= 1 << T_BITS:
            raise OverflowError("attempt index exceeds the descriptor field")
        xR, yR = R
        if self.np is not None:
            self._scan_np(xR, yR, lo, hi, hid, t)
        else:
            self._scan_py(xR, yR, lo, hi, hid, t)
        self.seconds += time.perf_counter() - t0

    def _scan_py(self, xR, yR, lo, hi, hid, t) -> None:
        p, a, half = self.p, self.a, self.half
        xs, ds = [], []
        for j in range(lo, hi + 1):
            F = self.fb.points[j]
            deg = F[0] == xR
            if deg:
                self.degenerate_roots += 1
            for s in (1, -1):
                T = _affine_add(p, a, (xR, yR), (F[0], (-F[1]) % p if s > 0 else F[1]))
                if T is None:
                    continue
                xs.append(T[0])
                ds.append(_pack(t, hid, j, s, int(T[1] > half)))
        self.encodings_recorded += len(xs)
        self._xs.append(xs)
        self._desc.append(ds)

    def _scan_np(self, xR, yR, lo, hi, hid, t) -> None:
        np = self.np
        p = np.uint64(self.p)
        X, Y = self.FX[lo:hi + 1], self.FY[lo:hi + 1]
        xr, yr = np.uint64(xR), np.uint64(yR)
        dx = (X + (p - xr)) % p
        zero = dx == 0
        dx[zero] = 1
        inv = _accel.batch_inverse(dx, p)
        ssum = (X + xr) % p
        # R - F_j = R + (x_j, -y_j)
        lam = ((p - Y) % p + (p - yr)) % p * inv % p
        x1 = (lam * lam % p + (p - ssum)) % p
        y1 = (lam * ((xr + (p - x1)) % p) % p + (p - yr)) % p
        # R + F_j
        lam = (Y + (p - yr)) % p * inv % p
        x2 = (lam * lam % p + (p - ssum)) % p
        y2 = (lam * ((xr + (p - x2)) % p) % p + (p - yr)) % p
        n = len(X)
        xs = np.empty(2 * n, dtype=np.uint64)
        ys = np.empty(2 * n, dtype=np.uint64)
        xs[0::2], xs[1::2] = x1, x2
        ys[0::2], ys[1::2] = y1, y2
        keep = np.ones(2 * n, dtype=bool)
        for k in np.flatnonzero(zero).tolist():
            self.degenerate_roots += 1
            j = lo + k
            F = self.fb.points[j]
            for q, s in ((0, 1), (1, -1)):
                T = _affine_add(self.p, self.a, (xR, yR), (F[0], (-F[1]) % self.p if s > 0 else F[1]))
                if T is None:
                    keep[2 * k + q] = False
                else:
                    xs[2 * k + q], ys[2 * k + q] = T[0], T[1]
        js = np.repeat(np.arange(lo, hi + 1, dtype=np.uint64), 2)
        sneg = np.tile(np.array([0, 1], dtype=np.uint64), n)
        ybit = (ys > np.uint64(self.half)).astype(np.uint64)
        base = np.uint64(((t << H_BITS) | hid) << (J_BITS + 2))
        desc = base | (js << np.uint64(2)) | (sneg << np.uint64(1)) | ybit
        xs, desc = xs[keep], desc[keep]
        self.encodings_recorded += int(len(xs))
        self._xs.append(xs)
        self._desc.append(desc)

    def take(self):
        """This attempt's encodings in recording order: (x list/array, descriptor list/array)."""
        xs, ds = self._xs, self._desc
        self._xs, self._desc = [], []
        if self.np is not None:
            np = self.np
            if not xs:
                return np.empty(0, dtype=np.uint64), np.empty(0, dtype=np.uint64)
            return np.concatenate(xs), np.concatenate(ds)
        return [x for part in xs for x in part], [d for part in ds for d in part]


# -- the harvester --------------------------------------------------------------------------

def _vec_add(v: dict, i: int, c: int) -> None:
    nv = v.get(i, 0) + c
    if nv:
        v[i] = nv
    else:
        v.pop(i, None)


def _key(v: dict) -> tuple:
    return tuple(sorted(v.items()))


class _Class:
    def __init__(self) -> None:
        self.pairs_raw = self.pairs_formal = self.dup_formal = 0
        self.rows_emitted = self.rows_formal = self.rows_nonformal = 0
        self.cert_pass = self.cert_fail = 0
        self.k_determining_rows = 0
        self.fed = 0
        self.saturated_at = None
        self.increments: list[int] = []
        self.kept_rows: list[tuple] = []  # (coeffs, kcoef, rhs) for the permutation check

    def snapshot_pairs(self) -> dict:
        return {"pairs_raw": self.pairs_raw, "pairs_formal": self.pairs_formal,
                "pairs_nonformal": self.pairs_raw - self.pairs_formal}


class _SSGroup:
    """One x-key of the SS store with >= 2 encodings: the first distinct member
    (t, sigma, oriented A as a key, descriptor, y-bit, formal key) and the
    (duplicate key, formal key) of every distinct member."""
    __slots__ = ("first_ybit", "first", "keys")

    def __init__(self, first_ybit: int) -> None:
        self.first_ybit = first_ybit
        self.first = None
        self.keys: list[tuple] = []


class Harvester:
    """Per-instance harvest state.  The solver drives it:

    ``table_phase()`` once after the table is built, then per attempt
    ``begin_attempt(t, a, b)`` / decompose(..., recorder=h.recorder) /
    ``end_attempt()``, and ``finish(...)`` at the stop.
    """

    def __init__(self, E: Curve, P: Point, Q: Point, fb, table, mode: str,
                 target_label: str | None, formal_basis: dict | None = None,
                 attempt_budget: int | None = None, sink=None) -> None:
        if table is None or table.arity < 2:
            raise ValueError("harvest needs a mitm table of arity >= 2")
        t0 = time.perf_counter()
        self.E, self.P, self.Q, self.fb, self.table = E, P, Q, fb, table
        self.N, self.p = E.order, E.p
        self.mode, self.target_label, self.A_fix = mode, target_label, attempt_budget
        self.sink = sink
        self.retain_all = E.p.bit_length() <= 24
        self.Ev = Curve(E.p, E.a, E.b, E.order)  # independent instance, own OpCounter
        fbd = formal_basis or {"kind": "none", "rows": []}
        self.formal_kind = fbd.get("kind", "none")
        self.formal_rows = [dict(r) for r in fbd.get("rows", [])]
        self.formal = self._seeded()
        self.formal_rank = self.formal.rank
        self.U = len(fb) - self.formal_rank
        self.census = {c: self._seeded() for c in CLASSES}
        self.cls = {c: _Class() for c in CLASSES}
        self.recorder = SearchRecorder(fb, E.p, E.a)
        self.targets: dict[int, tuple[int, int]] = {}
        self.t = 0
        self._resid_cache: dict = {}
        # SS store: sorted runs of (x, packed descriptor); groups for colliding x only
        self.runs: list = []
        self.store_entries = 0
        self.last_batch = None
        self.ss_dup = 0
        self.at_A_fix = None
        self.table_info: dict = {}
        self.seconds = time.perf_counter() - t0

    # -- helpers ------------------------------------------------------------------------
    def _seeded(self) -> EliminationState:
        return census_elimination(self.N, self.formal_rows)

    def _residual(self, v: dict) -> tuple:
        """Canonical normal form of v modulo the formal span."""
        N = self.N
        if not self.formal_rows:
            return _key({c: x % N for c, x in v.items() if x % N})
        if self.formal_kind == "known_log":  # reduction by e_j - j e_1 == the log value
            return (sum(c * (i + 1) for i, c in v.items()) % N,)
        key = _key(v)
        hit = self._resid_cache.get(key)
        if hit is not None:
            return hit
        if True:
            row = {c: x % N for c, x in v.items() if x % N}
            for c in self.formal.order:
                x = row.get(c)
                if not x:
                    continue
                prow, _, _ = self.formal.pivots[c]
                for cc, pv in prow.items():
                    nv = (row.get(cc, 0) - x * pv) % N
                    if nv:
                        row[cc] = nv
                    else:
                        row.pop(cc, None)
            out = _key(row)
        if len(self._resid_cache) < 1_000_000:
            self._resid_cache[key] = out
        return out

    def certify(self, coeffs: dict, kcoef: int, rhs: int) -> bool:
        Ev, N = self.Ev, self.N
        S: Point = None
        for i, c in sorted(coeffs.items()):
            S = Ev.add(S, Ev.mul(c, self.fb.points[i]))
        S = Ev.add(S, Ev.mul(kcoef % N, self.Q))
        return S == Ev.mul(rhs % N, self.P)

    def _emit(self, cname: str, coeffs: dict, kcoef: int, rhs: int, formal: bool,
              attempt: int, elements: list) -> None:
        """Certify, count, feed the census elimination, retain."""
        c = self.cls[cname]
        c.rows_emitted += 1
        if formal:
            c.rows_formal += 1
        else:
            c.rows_nonformal += 1
        ok = self.certify(coeffs, kcoef, rhs)
        if not ok:
            c.cert_fail += 1
            raise CertificateFailure(f"{cname} row {c.rows_emitted} failed: "
                                     f"coeffs={coeffs} kcoef={kcoef} rhs={rhs}")
        c.cert_pass += 1
        st = self.census[cname]
        saturated_before = c.saturated_at is not None
        rank_after = None
        if not saturated_before:
            before = st.rank
            k = st.add_row(dict(coeffs), kcoef, rhs)
            c.fed += 1
            if k is not None:
                c.k_determining_rows += 1
            if st.rank > before:
                c.increments.append(c.rows_emitted)
            if st.rank - self.formal_rank >= self.U:
                c.saturated_at = c.rows_emitted
            rank_after = st.rank - self.formal_rank
        if self.retain_all:
            c.kept_rows.append((dict(coeffs), kcoef, rhs))
        if self.sink is not None and (self.retain_all or not saturated_before):
            self.sink({"class": cname, "attempt": attempt, "elements": elements,
                       "coeffs": sorted([i, v] for i, v in coeffs.items()),
                       "kcoef": kcoef % self.N, "rhs": rhs % self.N, "formal": formal,
                       "cert_ok": ok, "census_rank_after": rank_after})

    # -- table classes ------------------------------------------------------------------
    def table_phase(self) -> list[tuple]:
        """TB and TT groups of the table; returns the rows in feeding order
        (TB by base index then code, TT by x then code) as (class, coeffs, kcoef, rhs)."""
        t0 = time.perf_counter()
        fb, tab, half = self.fb, self.table, self.p // 2
        tb, tt = [], []
        tail_dups = 0
        for x, codes in tab.iter_keys_selected(fb.index.keys()):
            b = fb.index.get(x)
            tails = []
            for code in codes:
                tail, yb = tab.decode(code)
                v: dict = {}
                for i, s in tail:
                    _vec_add(v, i, s)
                tails.append((code, v, yb, tail))
            first_y = (fb.points[b][1] > half) if b is not None else tails[0][2]
            beta = None
            if b is not None:
                bv = {b: 1}
                beta = (bv, _key(bv), self._residual(bv))
            distinct, seen = [], set()
            all_keys = set()
            for code, v, yb, tail in tails:
                sig = 1 if yb == first_y else -1
                ov = {i: sig * c for i, c in v.items()}
                k = _key(ov)
                all_keys.add(k)
                if beta is not None and k == beta[1]:
                    self.cls["TB"].dup_formal += 1
                    continue
                if k in seen:
                    self.cls["TT"].dup_formal += 1
                    continue
                seen.add(k)
                distinct.append((code, ov, self._residual(ov), tail, yb))
            tail_dups += len(tails) - len(all_keys)
            kp = len(distinct)
            if beta is not None:
                self.cls["TB"].pairs_raw += kp
                self.cls["TB"].pairs_formal += sum(1 for d in distinct if d[2] == beta[2])
                for code, ov, res, tail, yb in distinct:
                    co = dict(beta[0])
                    for i, c in ov.items():
                        _vec_add(co, i, -c)
                    tb.append(((b, code), co, res == beta[2],
                               [{"base": b}, {"tail": tail, "ybit": yb}]))
            if kp >= 2:
                self.cls["TT"].pairs_raw += kp * (kp - 1) // 2
                cnt = Counter(d[2] for d in distinct)
                self.cls["TT"].pairs_formal += sum(n * (n - 1) // 2 for n in cnt.values())
                f = distinct[0]
                for code, ov, res, tail, yb in distinct[1:]:
                    co = dict(f[1])
                    for i, c in ov.items():
                        _vec_add(co, i, -c)
                    tt.append(((x, code), co, res == f[2],
                               [{"tail": f[3], "ybit": f[4]}, {"tail": tail, "ybit": yb}]))
        tb.sort(key=lambda r: r[0])
        tt.sort(key=lambda r: r[0])
        fed = []
        for cname, rows in (("TB", tb), ("TT", tt)):
            for _, co, formal, el in rows:
                self._emit(cname, co, 0, 0, formal, -1, el)
                fed.append((cname, co, 0, 0))
        E_t = tab.entries - tail_dups
        dk = tab.distinct_keys()
        self.table_info = {
            "entries": tab.entries, "distinct_x_keys": dk, "formally_distinct_tails": E_t,
            "scratch_statistic": ((tab.entries - dk) / (tab.entries ** 2 / self.N)
                                  if tab.entries else None)}
        self.E_t = E_t
        self.seconds += time.perf_counter() - t0
        return fed

    # -- search class -------------------------------------------------------------------
    def begin_attempt(self, t: int, a: int, b: int) -> None:
        self.t = t
        self.recorder.t = t
        self.targets[t] = (a, b)

    def _element(self, desc: int):
        t, hid, j, s, yb = unpack(desc)
        A: dict = {}
        head = self.recorder.heads[hid]
        for i, si in head:
            _vec_add(A, i, si)
        _vec_add(A, j, s)
        return t, A, yb, (t, [list(e) for e in head], j, s)

    def _group_from(self, descs: list[int]):
        """The group state of the stored encodings of one x (recording order), or None."""
        g = None
        for d in descs:
            g = self._ss_add(g, d, False, None)
        return g

    def _ss_add(self, g, desc: int, is_new: bool, out):
        """Add one encoding to group state g (None: start a group); return the state."""
        t, A, yb, descr = self._element(desc)
        if g is None:
            g = _SSGroup(yb)
        sig = 1 if yb == g.first_ybit else -1
        oA = {i: sig * c for i, c in A.items()}
        dkey = (t, sig, _key(oA))
        for dk, _ in g.keys:
            if dk == dkey:
                if is_new:
                    self.ss_dup += 1
                    self.cls["SS"].dup_formal += 1
                return g
        # with an empty formal basis, formal equivalence is identity (dup, handled above)
        fkey = (t, sig, self._residual(oA)) if self.formal_rows else None
        c = self.cls["SS"]
        if is_new:
            c.pairs_raw += len(g.keys)
            if fkey is not None:
                c.pairs_formal += sum(1 for _, fk in g.keys if fk == fkey)
        g.keys.append((dkey, fkey))
        if g.first is None:
            g.first = (t, sig, dkey[2], descr, yb, fkey)
            return g
        if is_new:
            ft, sX, fA, fdescr, fyb, ffk = g.first
            aX, bX = self.targets[ft]
            aY, bY = self.targets[t]
            co = dict(fA)  # sigma_X A_X
            for i, v in A.items():
                _vec_add(co, i, -sig * v)
            kcoef = -(sX * bX - sig * bY)
            rhs = sX * aX - sig * aY
            formal = fkey is not None and fkey == ffk
            out.append((co, kcoef, rhs, formal,
                        [{"enc": fdescr, "ybit": fyb}, {"enc": descr, "ybit": yb}]))
        return g

    def end_attempt(self) -> list[tuple]:
        """Harvest this attempt's encodings; return its SS rows (feeding order)."""
        t0 = time.perf_counter()
        xs, ds = self.recorder.take()
        self.last_batch = (xs, ds)
        rows: list = []
        n = len(xs)
        if n:
            np = self.recorder.np
            self.store_entries += n
            if np is not None:
                xs32 = xs.astype(np.uint32)
                order = np.argsort(xs32, kind="stable")
                bx, bd = xs32[order], ds[order]
                coll: dict[int, list[int]] = {}
                for rx, rd in self.runs:
                    L = np.searchsorted(rx, bx, "left")
                    R = np.searchsorted(rx, bx, "right")
                    for q in np.flatnonzero(R > L).tolist():
                        x = int(bx[q])
                        if x not in coll:
                            coll[x] = [int(v) for v in rd[L[q]:R[q]]]
                same = np.flatnonzero(bx[1:] == bx[:-1])
                hot = set(coll) | {int(bx[q]) for q in same.tolist()}
                if hot:
                    hx = np.array(sorted(hot), dtype=np.uint32)
                    states: dict = {}
                    for q in np.flatnonzero(np.isin(xs32, hx)).tolist():  # recording order
                        x = int(xs32[q])
                        g = states[x] if x in states else self._group_from(coll.get(x, []))
                        states[x] = self._ss_add(g, int(ds[q]), True, rows)
                del order, xs32
                self._merge_run(bx, bd)
            else:
                if not self.runs:
                    self.runs.append({})
                store = self.runs[0]
                for q in range(n):
                    x, d = xs[q], ds[q]
                    prev = store.get(x)
                    if prev is not None:
                        self._ss_add(self._group_from(prev), d, True, rows)
                        prev.append(d)
                    else:
                        store[x] = [d]
        for co, kcoef, rhs, formal, el in rows:
            self._emit("SS", co, kcoef, rhs, formal, self.t, el)
        if self.A_fix is not None and self.t == self.A_fix:
            self.at_A_fix = self._ss_snapshot(censored=False)
        self.seconds += time.perf_counter() - t0
        return [("SS", co, kcoef, rhs) for co, kcoef, rhs, _, _ in rows]

    def _merge_run(self, bx, bd) -> None:
        np = self.recorder.np
        self.runs.append((bx, bd))
        while len(self.runs) >= 2 and len(self.runs[-2][0]) <= 2 * len(self.runs[-1][0]):
            (ax, ad), (cx, cd) = self.runs[-2], self.runs[-1]
            pos = np.searchsorted(ax, cx, "right")
            pos += np.arange(len(cx), dtype=pos.dtype)
            tot = len(ax) + len(cx)
            ox = np.empty(tot, dtype=ax.dtype)
            od = np.empty(tot, dtype=ad.dtype)
            mask = np.ones(tot, dtype=bool)
            mask[pos] = False
            ox[mask] = ax
            ox[pos] = cx
            od[mask] = ad
            od[pos] = cd
            del mask, pos
            self.runs[-2:] = [(ox, od)]

    def _ss_snapshot(self, censored: bool) -> dict:
        c = self.cls["SS"]
        X = self.recorder.encodings_recorded - self.ss_dup
        return {"censored": censored,
                "encodings_recorded": self.recorder.encodings_recorded,
                "formally_distinct_encodings": X,
                "pairs_raw": c.pairs_raw, "pairs_formal": c.pairs_formal,
                "pairs_nonformal": c.pairs_raw - c.pairs_formal,
                "poisson_mean": X * (X - 1) / 2 * 2 / self.N}

    # -- stop -----------------------------------------------------------------------------
    def staircase(self) -> list[dict]:
        """Per class: the census rank staircase and, on instances <= 24 bits, the
        saturation index under 5 row permutations (random.Random(1..5))."""
        out = []
        for cname in CLASSES:
            c = self.cls[cname]
            final = self.census[cname].rank - self.formal_rank
            n = c.rows_emitted
            sat_idx = (c.increments[-1] / n) if (n and c.increments) else None
            rec = {"class": cname, "rows_emitted": n, "rows_fed": c.fed,
                   "formal_rank": self.formal_rank, "U": self.U,
                   "final_informative_rank": final, "increments": c.increments,
                   "saturation_index": sat_idx, "perm_saturation_indices": None}
            if self.retain_all and n and final > 0 and len(c.kept_rows) == n:
                perms = []
                for r in range(1, 6):
                    order = list(range(n))
                    random.Random(r).shuffle(order)
                    st = self._seeded()
                    reach = None
                    for q, idx in enumerate(order, 1):
                        co, kc, rh = c.kept_rows[idx]
                        st.add_row(dict(co), kc, rh)
                        if st.rank - self.formal_rank >= final:
                            reach = q
                            break
                    perms.append(reach / n if reach else None)
                rec["perm_saturation_indices"] = perms
            out.append(rec)
        return out

    def finish(self, s3_solves: int, table_s3_solves: int, terminated_by: str,
               on_block: dict | None = None) -> dict:
        t0 = time.perf_counter()
        N, rec = self.N, self.recorder
        search = s3_solves - table_s3_solves
        if self.A_fix is not None and self.at_A_fix is None:
            self.at_A_fix = self._ss_snapshot(censored=True)
        E_t = self.E_t
        X = rec.encodings_recorded - self.ss_dup
        means = {"TT": E_t * (E_t - 1) / 2 * 2 / N,
                 "TB": E_t * len(self.fb) * 2 / N,
                 "SS": X * (X - 1) / 2 * 2 / N}
        block: dict = {
            "mode": self.mode, "target_label": self.target_label,
            "attempt_budget_A_fix": self.A_fix, "terminated_by": terminated_by,
            "formal_basis_kind": self.formal_kind, "formal_basis_rank": self.formal_rank,
            "U": self.U, "table": dict(self.table_info)}
        for cname in CLASSES:
            c = self.cls[cname]
            block[cname] = {"at_stop": {
                "pairs_raw": c.pairs_raw, "pairs_formal": c.pairs_formal,
                "pairs_nonformal": c.pairs_raw - c.pairs_formal, "dup_formal": c.dup_formal,
                "rows_emitted": c.rows_emitted, "rows_formal": c.rows_formal,
                "rows_nonformal": c.rows_nonformal, "cert_pass": c.cert_pass,
                "cert_fail": c.cert_fail,
                "informative_rank": self.census[cname].rank - self.formal_rank,
                "k_determining_rows": c.k_determining_rows, "poisson_mean": means[cname]},
                "census_saturated_at_row": c.saturated_at}
        block["SS"]["at_A_fix"] = self.at_A_fix
        peak = self.store_entries
        block["ss_store"] = {
            "encodings_recorded": rec.encodings_recorded, "search_s3_charged": search,
            "degenerate_roots": rec.degenerate_roots,
            "identity_ok": rec.encodings_recorded == 2 * search - rec.degenerate_roots,
            "peak_entries": peak, "peak_bytes": peak * BYTES_PER_ENCODING}
        if on_block is not None:
            block["on"] = on_block
        if self.sink is not None and hasattr(self.sink, "staircase"):
            self.sink.staircase(self.staircase())
        self.seconds += time.perf_counter() - t0
        block["harvest_seconds"] = self.seconds + rec.seconds
        block["harvest_verify_group_ops"] = self.Ev.ops.group_ops
        block["worker_maxrss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        return block

