"""PTM-2 .. PTM-5: known-false label sets of exactly n labels built on the recorded main-block curves of a cell
(p, a, b read from the job records; no curve generated, no seed block touched), counted exactly with the reviewer
kernel, and read against the RECORDED null arm of the same cell (M, V from the 20 recorded null counts per curve)
with the frozen flag, null and class rules (common.classify; the recorded plant arm decides plant recovery).

Objects (all RNG streams are reviewer streams: sha256('TASK-20261029-11526b|<object>|<cell>|<c>|<rep>')):
  PTM-2(f)  label AP of m labels (x0 + k w, first m in L) plus n - m uniform labels of L, m chosen per curve by error
            diffusion so that the cumulative AP-internal count tracks f x the cumulative recorded null mean
            (m = 0, i.e. no AP, is allowed; needed where f x mu < 1). f = 0.10 and 0.15; known kappa_true ~ 1 + f.
  PTM-3     a uniform (n + k)-subset of L, then greedy removal (exact, one label at a time, of the label in the most
            coincidences, with incremental bookkeeping verified by a final recount) until n remain; k chosen per
            curve by error diffusion toward 0.85 x mu (cells with mu < 100 per set) or fixed per cell by a pilot on
            curves 0 and 1 (mu >= 100). Known kappa ~ 0.85.
  PTM-4a    uniform n-subset of L (decided by the label predicate chi(f(x)) = 1 plus a table).
  PTM-4b    geometric progression x0 g^k, g a primitive root mod p, first n terms in L.
  PTM-4c    inverse interval: x = k^-1 mod p for k = t, t+1, ..., first n in L (membership: one inversion and one
            comparison, a polynomial-time label predicate at every p) [reviewer addition].
  PTM-5s    uniform n-subset of L inside an interval of length 4n.
  PTM-5h    uniform n-subset of L inside an interval of length floor(p/2) [reviewer addition, moderate excess].
Usage: python3 -I -B ptm_sets.py <cell> <objects comma list> <reps for PTM-2(0.10)>
Writes outputs/ptm-cells/<cell>.json.
"""
import hashlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import common as C  # noqa: E402


# ---------------------------------------------------------------- builders

def ap_labels(p, a, b, mcap, rng):
    x0 = int(rng.integers(0, p))
    w = int(rng.integers(1, p))
    out = []
    k0 = 0
    while len(out) < mcap:
        ks = np.arange(k0, k0 + 4 * mcap + 64, dtype=np.int64)
        xs = (x0 + (ks % p) * w) % p
        xs = xs[C.in_L(xs, p, a, b)]
        out.extend(xs.tolist())
        k0 += len(ks)
    return np.array(out[:mcap], dtype=np.int64)


def ptm2_curve(p, a, b, n, target, rng):
    mcap = n // 2
    ap = ap_labels(p, a, b, mcap, rng)
    cache = {}

    def internal(m):
        if m < 4:
            return 0
        if m not in cache:
            cache[m] = C.count_CD(ap[:m], p)[0]
        return cache[m]
    if target <= 0:
        m = 0
    elif internal(mcap) < target:
        m = mcap
    else:
        lo, hi = 3, mcap
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if internal(mid) >= target:
                hi = mid
            else:
                lo = mid
        m = hi
        m_lo = lo if lo >= 4 else 0
        if abs(internal(m_lo) - target) < abs(internal(m) - target):
            m = m_lo
    labs = ap[:m]
    fill = C.uniform_labels(n - m, p, a, b, rng, exclude=labs)
    X = np.concatenate([labs, fill])
    return X, m, internal(m)


class Greedy:
    """Exact greedy removal of the label in the most coincidences, with incremental bookkeeping."""

    def __init__(self, X, p):
        self.p = p
        self.X = np.asarray(X, dtype=np.int64)
        K = len(self.X)
        dt = np.int32 if p <= (1 << 25) else np.int16
        self.inX = np.zeros(p, dtype=bool)
        self.inX[self.X] = True
        self.m = np.zeros(p, dtype=dt)
        self.r = np.zeros(p, dtype=dt)
        for i0 in range(0, K - 1, 256):
            i1 = min(K - 1, i0 + 256)
            s = np.concatenate([(self.X[i] + self.X[i + 1:]) % p for i in range(i0, i1)])
            d = np.concatenate([(self.X[i] - self.X[i + 1:]) % p for i in range(i0, i1)])
            if p <= (1 << 25):
                self.m += np.bincount(s, minlength=p).astype(dt)
                self.r += np.bincount(d, minlength=p).astype(dt)
                self.r += np.bincount((-d) % p, minlength=p).astype(dt)
            else:
                np.add.at(self.m, s, 1)
                np.add.at(self.r, d, 1)
                np.add.at(self.r, (-d) % p, 1)
        self.part = np.zeros(K, dtype=np.int64)
        for i0 in range(0, K, 256):
            U = self.X[i0:i0 + 256]
            tot = self.m[(U[:, None] + self.X[None, :]) % p].astype(np.int64).sum(axis=1)
            tot -= self.m[(2 * U) % p].astype(np.int64)        # v = u is not a pair
            self.part[i0:i0 + 256] = tot - (K - 1)
        mm = self.m.astype(np.int64)
        self.C = int((mm * (mm - 1) // 2).sum())
        self.active = np.ones(K, dtype=bool)

    def remove_one(self):
        p = self.p
        act = np.flatnonzero(self.active)
        j = act[int(np.argmax(self.part[act]))]
        w = int(self.X[j])
        self.C -= int(self.part[j])
        self.active[j] = False
        oth = np.flatnonzero(self.active)
        Y = self.X[oth]
        delta = -(self.m[(Y + w) % p].astype(np.int64) - 1) - (
            self.r[(w - Y) % p].astype(np.int64) - 1 - self.inX[(2 * w - Y) % p] - self.inX[(2 * Y - w) % p])
        self.part[oth] += delta
        self.m[(Y + w) % p] -= 1
        self.r[(w - Y) % p] -= 1
        self.r[(Y - w) % p] -= 1
        self.inX[w] = False

    def labels(self):
        return self.X[self.active]


def ptm3_small(p, a, b, n, target, rng, kmax=24):
    """Error-diffusion choice of k among 0..kmax (pool = prefix of one uniform sequence)."""
    seq = C.uniform_labels(n + kmax, p, a, b, rng)
    best = None
    for k in range(0, kmax + 1):
        X = seq[:n + k]
        Cs = pair_greedy_small(X, p, k)
        if best is None or abs(Cs - target) < abs(best[1] - target):
            best = (k, Cs)
        if Cs < target or Cs == 0:
            break
    k, _ = best
    X = seq[:n + k]
    lab, Cf = pair_greedy_small(X, p, k, return_labels=True)
    return lab, k, Cf


def pair_greedy_small(X, p, k, return_labels=False):
    """Dense-matrix greedy for small pools (n <= 512 + kmax): recompute participations each step."""
    X = np.array(X, dtype=np.int64)
    alive = np.ones(len(X), bool)
    for _ in range(k):
        idx = np.flatnonzero(alive)
        Y = X[idx]
        S = (Y[:, None] + Y[None, :]) % p
        iu = np.triu_indices(len(Y), 1)
        sums = S[iu]
        u, inv, cnt = np.unique(sums, return_inverse=True, return_counts=True)
        w = cnt[inv] - 1
        part = np.bincount(iu[0], weights=w, minlength=len(Y)) + np.bincount(iu[1], weights=w, minlength=len(Y))
        alive[idx[int(np.argmax(part))]] = False
    Y = X[alive]
    Cf = C.count_CD(Y, p)[0]
    return (Y, Cf) if return_labels else Cf


def ptm3_large(p, a, b, n, k, rng):
    X = C.uniform_labels(n + k, p, a, b, rng)
    G = Greedy(X, p)
    for _ in range(k):
        G.remove_one()
    Y = G.labels()
    Cf = C.count_CD(Y, p)[0]
    if Cf != G.C:
        raise RuntimeError(f"greedy bookkeeping mismatch {Cf} != {G.C}")
    return Y, Cf


def factor(n):
    f, d = [], 2
    while d * d <= n:
        if n % d == 0:
            f.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        f.append(n)
    return f


def ptm4b(p, a, b, n, rng):
    qs = factor(p - 1)
    while True:
        g = int(rng.integers(2, p))
        if all(pow(g, (p - 1) // q, p) != 1 for q in qs):
            break
    x = int(rng.integers(1, p))
    out = []
    while len(out) < n:
        blk = []
        for _ in range(3 * (n - len(out)) + 16):
            blk.append(x)
            x = x * g % p
        blk = np.array(blk, dtype=np.int64)
        out.extend(blk[C.in_L(blk, p, a, b)].tolist())
    return np.array(out[:n], dtype=np.int64), g


def ptm4c(p, a, b, n, rng):
    t = int(rng.integers(1, p))
    out = []
    k0 = t
    while len(out) < n:
        blk = 3 * (n - len(out)) + 16
        ks = (np.arange(k0, k0 + blk, dtype=np.int64)) % p
        ks = ks[ks != 0]
        xs = C.powmod_vec(ks, p - 2, p)
        out.extend(xs[C.in_L(xs, p, a, b)].tolist())
        k0 += blk
    return np.array(out[:n], dtype=np.int64), t


def ptm5(p, a, b, n, length, rng):
    t = int(rng.integers(0, p))
    if length <= 8 * n:
        xs = (t + np.arange(length, dtype=np.int64)) % p
        xs = xs[C.in_L(xs, p, a, b)]
        if len(xs) < n:
            raise RuntimeError("interval holds fewer than n labels")
        return rng.choice(xs, size=n, replace=False), t
    taken, out = set(), []
    while len(out) < n:
        cand = (t + rng.integers(0, length, size=3 * (n - len(out)) + 64)) % p
        cand = cand[C.in_L(cand, p, a, b)]
        for x in cand.tolist():
            if x not in taken:
                taken.add(x)
                out.append(x)
                if len(out) == n:
                    break
    return np.array(out, dtype=np.int64), t


# ---------------------------------------------------------------- cell driver

def kappa_floor(recs, m):
    """Pooled least possible kappa for ANY set of n distinct residues: pair sums spread as evenly as possible."""
    cmin = 0
    for r in recs:
        P = r["n"] * (r["n"] - 1) // 2
        q, rem = divmod(P, r["p"])
        cmin += rem * (q + 1) * q // 2 + (r["p"] - rem) * q * (q - 1) // 2
    return cmin / float(m.sum())


def read_cell(cid, g, m, s2, plant_ok, boot_label):
    st = C.cell_stats_np(g, m, s2)
    ci, sdb = C.bootstrap_ci(g, m, 2000, C.review_np_rng("ptm-boot", boot_label))
    cls = C.classify(st["M"], st["kappa"], st["z"], ci, plant_ok)
    return {"S": st["S"], "M": st["M"], "kappa": st["kappa"], "z": st["z"], "ci95": ci, "cls": cls,
            "sign": "+" if st["kappa"] > 1 else "-"}


def main():
    cid = sys.argv[1]
    objs = sys.argv[2].split(",")
    reps10 = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    recs = [r for r in C.load_jobs() if r["cell"] == cid and r["status"] == "ok"]
    recs.sort(key=lambda r: r["c"])
    an = {c["cell"]: c for c in C.load_analysis()["cells"]}[cid]
    plant_ok = bool(an["planted_recovered"])
    n = recs[0]["n"]
    g0, m, s2, nulls = C.curve_arrays(recs)
    mu_cell = float(m.mean())
    out_path = os.path.join(C.OUT, "ptm-cells", f"{cid}.json")
    res = {}
    if os.path.exists(out_path):
        res = json.load(open(out_path)).get("objects", {})
    t_start = time.time()
    for obj in objs:
        runs = []
        nrep = reps10 if obj == "PTM-2@0.10" else (2 if obj == "PTM-2@0.15" else 1)
        k_fixed = None
        hist = []
        pilot_note = None
        if obj == "PTM-3" and mu_cell >= 100:
            kmode = sys.argv[4] if len(sys.argv) > 4 else "auto"
            floor = kappa_floor(recs, m)
            hist = []
            if kmode == "n" or floor > 0.85:
                k_fixed = n
                pilot_note = (f"kappa = 0.85 not attempted: pooled counting floor {floor:.4f}" if floor > 0.85 else
                              "kappa = 0.85 not reachable by the specified greedy at feasible k (reviewer diagnostic on "
                              "curve 0: kappa 0.973 at k = 1500, 0.961 at 3800, 0.951 at 8718); built at k = n") + \
                             "; the object is reported as the deficit set the construction reaches"
            else:
                rec0 = recs[0]
                for k in [max(4, (n // 16) * 2 ** i) for i in range(5)]:
                    t0 = time.time()
                    _, Cf = ptm3_large(rec0["p"], rec0["a"], rec0["b_coef"], n, k, C.review_np_rng("PTM-3-pilot", cid, 0, k))
                    hist.append((k, Cf / float(np.mean(rec0["null_C"]))))
                    print(cid, "PTM-3 pilot", k, round(hist[-1][1], 4), round(time.time() - t0, 1), flush=True)
                    if hist[-1][1] <= 0.85:
                        break
                if hist[-1][1] <= 0.85 and len(hist) >= 2:
                    (k1, r1), (k2, r2) = hist[-2], hist[-1]
                    k_fixed = int(round(math.exp(math.log(k1) + (0.85 - r1) * (math.log(k2) - math.log(k1)) / (r2 - r1))))
                    pilot_note = "k by log-linear interpolation between the last two pilot points on curve 0"
                else:
                    k_fixed = hist[-1][0]
                    pilot_note = "kappa = 0.85 not reached within k <= n on curve 0; built at k = n"
            print(cid, "PTM-3 k", k_fixed, "floor", round(floor, 4), flush=True)
        for rep in range(nrep):
            t0 = time.time()
            Cs, meta = [], []
            carry = 0.0
            h = hashlib.sha256()
            for rec, mu_c in zip(recs, m):
                p, a, b = rec["p"], rec["a"], rec["b_coef"]
                rng = C.review_np_rng(obj, cid, rec["c"], rep)
                if obj.startswith("PTM-2"):
                    f = float(obj.split("@")[1])
                    target = f * mu_c + carry
                    X, mm, internal = ptm2_curve(p, a, b, n, target, rng)
                    carry = target - internal
                    meta.append((mm, internal))
                elif obj == "PTM-3":
                    if k_fixed is None:
                        target = 0.85 * mu_c + carry
                        X, kk, Cf = ptm3_small(p, a, b, n, target, rng)
                        carry = target - Cf
                        meta.append((kk, Cf))
                    else:
                        X, Cf = ptm3_large(p, a, b, n, k_fixed, rng)
                        meta.append((k_fixed, Cf))
                elif obj == "PTM-4a":
                    X = C.uniform_labels(n, p, a, b, rng)
                elif obj == "PTM-4b":
                    X, gg = ptm4b(p, a, b, n, rng)
                elif obj == "PTM-4c":
                    X, tt = ptm4c(p, a, b, n, rng)
                elif obj == "PTM-5s":
                    X, tt = ptm5(p, a, b, n, 4 * n, rng)
                elif obj == "PTM-5h":
                    X, tt = ptm5(p, a, b, n, p // 2, rng)
                else:
                    raise ValueError(obj)
                X = np.asarray(X, dtype=np.int64)
                if len(X) != n or len(np.unique(X)) != n or not bool(C.in_L(X, p, a, b).all()):
                    raise RuntimeError(f"{obj} set on curve {rec['c']} is not n distinct labels of L")
                h.update(np.sort(X).tobytes())
                Cs.append(C.count_CD(X, p)[0])
                if obj == "PTM-3" and k_fixed is not None and len(Cs) % 10 == 0:
                    print(cid, obj, "curves done", len(Cs), round(time.time() - t0, 1), flush=True)
            g = np.array(Cs, dtype=np.float64)
            rd = read_cell(cid, g, m, s2, plant_ok, f"{obj}|{cid}|{rep}")
            rd.update({"rep": rep, "seconds": round(time.time() - t0, 1),
                       "labels_sha256": h.hexdigest(),
                       "counts_sha256": hashlib.sha256(np.array(Cs, dtype=np.int64).tobytes()).hexdigest()})
            if obj.startswith("PTM-2"):
                rd["realized_internal_fraction"] = float(sum(x[1] for x in meta) / m.sum())
                rd["curves_with_ap"] = int(sum(1 for x in meta if x[0] > 0))
                rd["m_range"] = [int(min(x[0] for x in meta)), int(max(x[0] for x in meta))]
            if obj == "PTM-3":
                rd["k_rule"] = "fixed by pilot" if k_fixed is not None else "error diffusion per curve"
                rd["k_range"] = [int(min(x[0] for x in meta)), int(max(x[0] for x in meta))]
                if k_fixed is not None:
                    rd["pilot"] = hist
                    rd["pilot_note"] = pilot_note
                    rd["kappa_counting_floor"] = kappa_floor(recs, m)
            runs.append(rd)
            print(cid, obj, rep, rd["cls"], round(rd["kappa"], 4), round(rd["z"], 2), rd["seconds"], flush=True)
        res[obj] = runs
        C.write_json(os.path.join("ptm-cells", f"{cid}.json"),
                     {"cell": cid, "n": n, "curves": len(recs), "mu_per_set": mu_cell, "plant_recovered_recorded": plant_ok,
                      "method": __doc__.strip().split("\n")[0], "objects": res}, sig=8)
    print("done", cid, round(time.time() - t_start, 1))


if __name__ == "__main__":
    main()
