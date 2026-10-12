"""PTM-5 -- a synthetic GENERIC-GROUP mitm engine with collision harvest, over Z_N.

Own code (RF-4): no curve, no import of any crypto_autoresearcher module. Group elements are
residues v in Z_N (N an odd prime); the point at infinity is v = 0; the x-key of v is a seeded
uniformly random labelling of the +-class {v, N - v}; the y-bit is [v > N // 2]. Base logs
f_1..f_B are uniform distinct nonzero +-classes, k is uniform in [1, N), targets are
R_t = a_t + b_t k with a_t uniform in [0, N) and b_t uniform in [1, N). The floor's premise
(independent uniform unknown logs, x-key equality = +-equality) therefore holds EXACTLY.

Mirrors the engine under review (choices PTM-5):
* table (tails.py _build_numpy): arity h = (m+1)//2; level k = (a, +1) + (+-T) for every stored
  level-(k-1) tail T with first index >= a; one S_3 per (a, T); zero sums dropped; within an
  x-key, tails ordered as the numpy path leaves them (reversed parts, stable sort by key);
* search (decompose.py): m = 3 one scan j = 0..B-1; m = 4, 5 heads (i, +1), (i, -1) for i
  ascending, R' = R - s f_i (skipped if 0), last-level scan j = i..B-1; both roots R' -+ f_j
  looked up against tails with first index >= j; early return at the first hit; the relation
  chosen at the hit index by _search_order; charged range [lo, hit] (IC-4);
* harvest (harvest.py IC-5): TB/TT star rows from the table (formal duplicates dropped), SS star
  rows over every recorded encoding (full x-key group, i.e. WITHOUT the OBJ-5 first-run
  rebuild), rows emitted at the end of each attempt in recording order;
* solver (solver.py): census mode feeds decomposition rows only; on mode feeds TB then TT
  before the first attempt, then per attempt the decomposition row and that attempt's SS rows;
  PRIMARY stop = the first row that determines k; VARIANT stop = full rank (rank == B and k
  determined), recorded by continuing the same run.
Every relation and harvested row is checked against the true logs (internal consistency).
"""
import heapq
import json
import math
import os
import sys
import time

import numpy as np

MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n):
    if n < 2:
        return False
    for p in MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rung_prime(bits):
    rng = np.random.default_rng([575, bits, 0x5EED])
    n = int(rng.integers(1 << (bits - 1), 1 << bits)) | 1
    while True:
        if n.bit_length() != bits:
            n = (1 << (bits - 1)) + 1
        if is_prime(n):
            return n
        n += 2


def default_fb_size(N, m):
    return max(4, math.ceil((math.factorial(m) * N / 2) ** (1 / m) / 2))


class Elim:
    """Incremental elimination mod N; reduction in pivot-creation order via a heap."""

    def __init__(self, N):
        self.N = N
        self.piv = {}
        self.cnt = 0

    @property
    def rank(self):
        return len(self.piv)

    def add(self, co, kc, rh):
        N = self.N
        row = {}
        for c, v in co.items():
            v %= N
            if v:
                row[c] = v
        kc %= N
        rh %= N
        heap = [(self.piv[c][0], c) for c in row if c in self.piv]
        heapq.heapify(heap)
        while heap:
            _, c = heapq.heappop(heap)
            v = row.get(c)
            if not v:
                continue
            _, prow, pk, pr = self.piv[c]
            for cc, pv in prow.items():
                nv = (row.get(cc, 0) - v * pv) % N
                if nv:
                    if cc not in row and cc in self.piv:
                        heapq.heappush(heap, (self.piv[cc][0], cc))
                    row[cc] = nv
                else:
                    row.pop(cc, None)
            kc = (kc - v * pk) % N
            rh = (rh - v * pr) % N
        if row:
            c = min(row)
            inv = pow(row[c], -1, N)
            self.piv[c] = (self.cnt, {cc: vv * inv % N for cc, vv in row.items()}, kc * inv % N, rh * inv % N)
            self.cnt += 1
            return "pivot", None
        if kc:
            return "k", rh * pow(kc, -1, N) % N
        return "dep", None


def starts(first, n):
    out, j = [0] * (n + 1), 0
    first = list(first)
    for a in range(n + 1):
        while j < len(first) and first[j] < a:
            j += 1
        out[a] = j
    return out


class Instance:
    def __init__(self, N, m, inst, lab):
        self.N, self.m, self.inst, self.lab = N, m, inst, lab
        self.h = (m + 1) // 2
        rng = np.random.default_rng([575, N.bit_length(), m, inst, 7])
        B = default_fb_size(N, m)
        self.B = B
        seen, f = set(), []
        while len(f) < B:
            v = int(rng.integers(1, N))
            c = min(v, N - v)
            if c in seen:
                continue
            seen.add(c)
            f.append(v)
        self.f = np.array(f, dtype=np.int64)
        self.k = int(rng.integers(1, N))
        self.build_table()
        self.head_i, self.head_s, self.jj = self.scan_order()

    # -- x-keys -------------------------------------------------------------------------
    def keys(self, v):
        N = self.N
        return self.lab[np.minimum(v, N - v)]

    # -- table ----------------------------------------------------------------------------
    def build_table(self):
        N, B, h, f = self.N, self.B, self.h, self.f
        B2 = 2 * B
        X = f.copy()
        V = 2 * np.arange(B, dtype=np.int64)
        NV = V + 1
        FIRST = np.arange(B, dtype=np.int64)
        s3 = 0
        parts = []
        for level in range(2, h + 1):
            last = level == h
            st = starts(FIRST.tolist(), B)
            parts = []
            for a in range(B):
                s = st[a]
                xs, v, nv = X[s:], V[s:], NV[s:]
                if not len(xs):
                    continue
                s3 += len(xs)
                plus = (f[a] + xs) % N
                minus = (f[a] - xs) % N
                ok1, ok2 = plus != 0, minus != 0
                if last:
                    parts.append((plus[ok1], 2 * a + B2 * v[ok1]))
                    parts.append((minus[ok2], 2 * a + B2 * nv[ok2]))
                    continue
                parts.append((plus[ok1], 2 * a + B2 * v[ok1], 2 * a + 1 + B2 * nv[ok1],
                              np.full(int(ok1.sum()), a, dtype=np.int64)))
                parts.append((minus[ok2], 2 * a + B2 * nv[ok2], 2 * a + 1 + B2 * v[ok2],
                              np.full(int(ok2.sum()), a, dtype=np.int64)))
            if not last:
                X, V, NV, FIRST = (np.concatenate([q[j] for q in parts]) for j in range(4))
        vals = np.concatenate([q[0] for q in reversed(parts)])
        dig = np.concatenate([q[1] for q in reversed(parts)])
        codes = (dig << 1) | (vals > N // 2).astype(np.int64)
        keys = self.keys(vals)
        order = np.argsort(keys, kind="stable")
        self.t_keys, self.t_codes, self.t_vals = keys[order], codes[order], vals[order]
        self.table_s3 = s3
        self.entries = len(codes)
        # per distinct key: max first index (first element of each group)
        first = ((self.t_codes >> 1) % B2) >> 1
        starts_mask = np.concatenate(([True], self.t_keys[1:] != self.t_keys[:-1]))
        self.u_keys = self.t_keys[starts_mask]
        self.u_start = np.flatnonzero(starts_mask)
        self.u_end = np.append(self.u_start[1:], len(self.t_keys))
        self.u_maxfirst = first[starts_mask]
        self.t_first = first
        self.base_keys = self.keys(f)

    def decode(self, code):
        B2 = 2 * self.B
        v, out = code >> 1, []
        for _ in range(self.h):
            v, d = divmod(v, B2)
            out.append((d >> 1, -1 if d & 1 else 1))
        return out, code & 1

    def lookup_maxfirst(self, keys):
        pos = np.searchsorted(self.u_keys, keys)
        pos = np.minimum(pos, len(self.u_keys) - 1)
        found = self.u_keys[pos] == keys
        return np.where(found, self.u_maxfirst[pos], -1), pos, found

    # -- scan order -------------------------------------------------------------------------
    def scan_order(self):
        B = self.B
        if self.m == 3:
            return (np.full(B, -1, dtype=np.int64), np.zeros(B, dtype=np.int64),
                    np.arange(B, dtype=np.int64))
        hi, hs, jj = [], [], []
        for i in range(B):
            for s in (1, -1):
                n = B - i
                hi.append(np.full(n, i))
                hs.append(np.full(n, s))
                jj.append(np.arange(i, B))
        return (np.concatenate(hi).astype(np.int64), np.concatenate(hs).astype(np.int64),
                np.concatenate(jj).astype(np.int64))

    # -- harvest: table classes --------------------------------------------------------------
    def table_rows(self):
        """TB rows (sorted by (base index, code)) then TT rows (sorted by (key, code)),
        plus pair counts. Each row = (coeffs dict, 0, 0)."""
        N, B, f = self.N, self.B, self.f
        base_index = {int(k): i for i, k in enumerate(self.base_keys.tolist())}
        tb, tt = [], []
        pairs_tt = pairs_tb = 0
        bk = set(base_index)
        for g in range(len(self.u_keys)):
            s, e = int(self.u_start[g]), int(self.u_end[g])
            key = int(self.u_keys[g])
            b = base_index.get(key)
            if e - s < 2 and b is None:
                continue
            tails = []
            for q in range(s, e):
                code = int(self.t_codes[q])
                tail, yb = self.decode(code)
                v = {}
                for i, sg in tail:
                    v[i] = v.get(i, 0) + sg
                    if v[i] == 0:
                        del v[i]
                tails.append((code, v, yb))
            first_y = int(f[b] > N // 2) if b is not None else tails[0][2]
            beta_key = ((b, 1),) if b is not None else None
            distinct, seen = [], set()
            for code, v, yb in tails:
                sig = 1 if yb == first_y else -1
                ov = {i: sig * c for i, c in v.items()}
                kk = tuple(sorted(ov.items()))
                if beta_key is not None and kk == beta_key:
                    continue
                if kk in seen:
                    continue
                seen.add(kk)
                distinct.append((code, ov))
            kp = len(distinct)
            if b is not None:
                pairs_tb += kp
                for code, ov in distinct:
                    co = {b: 1}
                    for i, c in ov.items():
                        co[i] = co.get(i, 0) - c
                    tb.append(((b, code), co))
            if kp >= 2:
                pairs_tt += kp * (kp - 1) // 2
                f0 = distinct[0][1]
                for code, ov in distinct[1:]:
                    co = dict(f0)
                    for i, c in ov.items():
                        co[i] = co.get(i, 0) - c
                    tt.append(((key, code), co))
        tb.sort(key=lambda r: r[0])
        tt.sort(key=lambda r: r[0])
        rows = [("TB", co) for _, co in tb] + [("TT", co) for _, co in tt]
        for _, co in rows:  # consistency: homogeneous base relation holds
            assert sum(c * int(f[i]) for i, c in co.items()) % N == 0
        return rows, pairs_tt, pairs_tb

    # -- one attempt ---------------------------------------------------------------------------
    def attempt(self, a, b, record):
        """Scan for target R = a + b k. Returns (s3_charged, relation_row or None, encodings,
        degenerate) where encodings (if record) is a list of (value, head_i, head_s, j, s_rec)."""
        N, f = self.N, self.f
        R = (a + b * self.k) % N
        if R == 0:
            return 0, None, [], 0
        if self.m == 3:
            Rp = np.full(len(self.jj), R, dtype=np.int64)
        else:
            Rp = (R - self.head_s * f[self.head_i]) % N
        valid = Rp != 0
        fj = f[self.jj]
        minus = (Rp - fj) % N   # R' - F_j  (s_rec = +1)
        plus = (Rp + fj) % N    # R' + F_j  (s_rec = -1)
        km = np.where(minus != 0, self.keys(minus), -1)
        kpl = np.where(plus != 0, self.keys(plus), -1)
        mfm, _, _ = self.lookup_maxfirst(km)
        mfp, _, _ = self.lookup_maxfirst(kpl)
        hit = valid & (((mfm >= self.jj) & (minus != 0)) | ((mfp >= self.jj) & (plus != 0)))
        hp = np.flatnonzero(hit)
        if len(hp):
            c = int(hp[0])
            charged = valid[:c + 1]
        else:
            c = None
            charged = valid
        s3 = int(charged.sum())
        upto = len(charged)
        degen = int(((minus[:upto] == 0) | (plus[:upto] == 0))[charged].sum())
        encs = []
        if record:
            idx = np.flatnonzero(charged)
            for q in idx.tolist():
                hi_, hs_, j = int(self.head_i[q]), int(self.head_s[q]), int(self.jj[q])
                if minus[q] != 0:
                    encs.append((int(minus[q]), hi_, hs_, j, 1))
                if plus[q] != 0:
                    encs.append((int(plus[q]), hi_, hs_, j, -1))
        rel = None
        if c is not None:
            rel = self.relation(c, int(Rp[c]), int(minus[c]), int(plus[c]), a, b, R)
        return s3, rel, encs, degen

    def relation(self, c, Rp, vminus, vplus, a, b, R):
        N, f = self.N, self.f
        j = int(self.jj[c])
        cands = []
        roots = []
        for v, sj in ((vminus, 1), (vplus, -1)):
            if v != 0:
                roots.append((int(self.keys(np.array([v]))[0]), v, sj))
        for key, v, sj in sorted(roots):  # s3_roots returns the roots sorted by x
            if v == 0:
                continue
            pos = int(np.searchsorted(self.u_keys, key))
            if pos >= len(self.u_keys) or self.u_keys[pos] != key:
                continue
            for q in range(int(self.u_start[pos]), int(self.u_end[pos])):
                if self.t_first[q] < j:
                    break
                code = int(self.t_codes[q])
                tail, yb = self.decode(code)
                tval = (Rp - sj * int(f[j])) % N  # the point the tail must sum to
                flip = yb != int(tval > N // 2)
                ot = [(i, -s if flip else s) for i, s in tail]
                sub = [(j, sj)] + ot
                headk = tuple((i, s < 0) for i, s in sub[:-2])
                order = headk + ((sub[-2][0], int(self.base_keys[sub[-1][0]])),)
                cands.append((order, sub))
        assert cands, "hit without a candidate"
        sub = min(cands, key=lambda c: c[0])[1]  # first minimal in iteration order, as min() in _tail_at
        rel = ([] if self.m == 3 else [(int(self.head_i[c]), int(self.head_s[c]))]) + sub
        co = {}
        for i, s in rel:
            co[i] = co.get(i, 0) + s
        co = {i: v for i, v in co.items() if v}
        assert (sum(v * int(f[i]) for i, v in co.items()) - R) % N == 0, "relation does not verify"
        return co, -b, a


def run_instance(N, m, inst, lab, mode, attempt_cap):
    """One mode of one instance. PRIMARY stop exactly as solver.py (first row that determines
    k: after an attempt the decomposition row is fed first, then -- mode on, k still unknown --
    that attempt's SS rows in emission order). VARIANT: the same run continued without stopping
    at k (remaining rows of the attempt fed, later attempts as before) until rank == B."""
    I = Instance(N, m, inst, lab)
    N, B, f, k = I.N, I.B, I.f, I.k
    trng = np.random.default_rng([575, N.bit_length(), m, inst, 11])  # shared target stream
    el = Elim(N)
    st = {"rows_fed": {"TT": 0, "TB": 0, "SS": 0}, "incr": {"decomp": 0, "TT": 0, "TB": 0, "SS": 0},
          "relations": 0, "search_s3": 0, "enc": 0, "degen": 0, "ss_pairs": 0, "ss_dup": 0,
          "k": None, "primary": None, "full": None, "attempts": 0}
    t_rows, pairs_tt, pairs_tb = I.table_rows()

    def snapshot():
        return {"S": I.table_s3 + st["search_s3"], "table_s3": I.table_s3, "search_s3": st["search_s3"],
                "attempts": st["attempts"], "relations": st["relations"],
                "rows_fed": dict(st["rows_fed"]), "incr": dict(st["incr"]), "rank": el.rank,
                "r_frozen": st["relations"] + (sum(st["rows_fed"].values()) if mode == "on" else 0),
                "enc_recorded": st["enc"], "degenerate": st["degen"],
                "ss_pairs": st["ss_pairs"], "ss_dup": st["ss_dup"]}

    def feed(cls, co, kc, rh):
        """Feed one row; record the stops; return True when the run is over (full stop)."""
        r0 = el.rank
        res, val = el.add(co, kc, rh)
        if cls == "decomp":
            st["relations"] += 1
        else:
            st["rows_fed"][cls] += 1
        st["incr"][cls] += el.rank - r0
        if res == "k":
            assert val == k, "wrong k"
            st["k"] = val
        if st["primary"] is None and st["k"] is not None:
            st["primary"] = snapshot()
        if st["primary"] is not None and st["full"] is None and el.rank == B:
            st["full"] = snapshot()
            return True
        return False

    over = False
    if mode == "on":
        for cls, co in t_rows:
            if feed(cls, co, 0, 0):
                over = True
                break
    store = {}
    groups = {}
    while not over and st["attempts"] < attempt_cap:
        st["attempts"] += 1
        a = int(trng.integers(0, N))
        b = int(trng.integers(1, N))
        s3, rel, encs, degen = I.attempt(a, b, record=(mode == "on"))
        st["search_s3"] += s3
        st["degen"] += degen
        ss_rows = []
        if mode == "on" and encs:
            st["enc"] += len(encs)
            keys = I.keys(np.array([e[0] for e in encs], dtype=np.int64)).tolist()
            cnt = {}
            for kk in keys:
                cnt[kk] = cnt.get(kk, 0) + 1
            hot = {kk for kk, n in cnt.items() if n > 1 or kk in store}
            for (v, hi_, hs_, j, s_rec), kk in zip(encs, keys):
                A = {}
                if hi_ >= 0:
                    A[hi_] = hs_
                A[j] = A.get(j, 0) + s_rec
                if A[j] == 0:
                    del A[j]
                elem = (st["attempts"], A, int(v > N // 2), a, b)
                if kk in hot:
                    g = groups.get(kk)
                    if g is None:
                        g = [None, None, set()]
                        for old in store.get(kk, []):
                            _ss_add(g, old, False, None)
                        groups[kk] = g
                    out = []
                    npairs, dup = _ss_add(g, elem, True, out)
                    st["ss_pairs"] += npairs
                    st["ss_dup"] += dup
                    for co, kc, rh in out:
                        assert (sum(c * int(f[i]) for i, c in co.items()) + kc * k - rh) % N == 0, "SS row does not verify"
                        ss_rows.append((co, kc, rh))
                store.setdefault(kk, []).append(elem)
        if rel is not None:
            if feed("decomp", *rel):
                break
        if mode == "on":
            # primary engine: SS rows only while k is unknown; the variant keeps feeding them
            for co, kc, rh in ss_rows:
                if feed("SS", co, kc, rh):
                    over = True
                    break
    return {"N": N, "m": m, "inst": inst, "B": B, "mode": mode, "entries": I.entries,
            "table_s3": I.table_s3, "pairs_TT": pairs_tt, "pairs_TB": pairs_tb,
            "primary": st["primary"], "full": st["full"], "attempt_cap_hit": st["primary"] is None,
            "full_missing": st["full"] is None}


def _ss_add(g, elem, is_new, out):
    """Group update as harvest._ss_add (full group). Returns (new pairs, dup)."""
    t, A, yb, a, b = elem
    if g[0] is None:
        g[0] = yb
    sig = 1 if yb == g[0] else -1
    oA = {i: sig * c for i, c in A.items()}
    dkey = (t, sig, tuple(sorted(oA.items())))
    if dkey in g[2]:
        return (0, 1 if is_new else 0)
    newp = len(g[2]) if is_new else 0
    g[2].add(dkey)
    if g[1] is None:
        g[1] = (t, sig, oA, a, b)
        return (newp, 0)
    if is_new:
        ft, sX, fA, aX, bX = g[1]
        co = dict(fA)
        for i, v in A.items():
            co[i] = co.get(i, 0) - sig * v
        co = {i: v for i, v in co.items() if v}
        kc = -(sX * bX - sig * b)
        rh = sX * aX - sig * a
        out.append((co, kc, rh))
    return (newp, 0)


def main():
    # usage: ptm5_engine.py OUT.jsonl m bits inst_lo inst_hi
    out, m, bits, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    N = rung_prime(bits)
    M = (N - 1) // 2
    prng = np.random.default_rng([575, bits, 0xABC])
    lab = np.zeros(M + 1, dtype=np.int64)
    lab[1:] = prng.permutation(M)
    done = set()
    if os.path.exists(out):
        for line in open(out):
            r = json.loads(line)
            done.add((r["m"], r["N"], r["inst"], r["mode"]))
    with open(out, "a") as fh:
        for inst in range(lo, hi):
            for mode in ("census", "on"):
                if (m, N, inst, mode) in done:
                    continue
                t0 = time.time()
                rec = run_instance(N, m, inst, lab, mode, attempt_cap=min(50 * N, 200000))
                rec["bits"] = bits
                rec["seconds"] = round(time.time() - t0, 3)
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
                fh.flush()


if __name__ == "__main__":
    main()
