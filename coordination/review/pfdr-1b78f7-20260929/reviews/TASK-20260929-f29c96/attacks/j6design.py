"""Design extraction and null generators for J6 / PTM (TASK-20260929-f29c96).

Everything here is read from the committed rows (frozen counts) and from
attacks/out/02_bundles.jsonl (relation multiplicities).  No solver import.
"""
import json
import math
import os
import statistics
from collections import Counter, defaultdict

import numpy as np

from rtlib import (OUT, P, RANDOMS, RUNS, RUNGS, STRUCT, build_index, canonical_rows,
                   censored, iter_jsonl, usable)

SUB = RANDOMS["subgroup"]
DIK = RANDOMS["dickson"]


def frozen_count(r, cl):
    h = r["harvest"]
    return h["SS"]["at_A_fix"]["pairs_nonformal"] if cl == "SS" else h[cl]["at_stop"]["pairs_nonformal"]


class Design:
    def __init__(self):
        self.main = build_index(canonical_rows("census-m3") + canonical_rows("census-m4")
                                + canonical_rows("census-m5"))
        self.sr = build_index(list(iter_jsonl(os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz"))))
        self.bund = {}
        for line in open(os.path.join(OUT, "out", "02_bundles.jsonl")):
            r = json.loads(line)
            if r["mode"] != "census":
                continue
            want = "A_fix" if r["class"] == "SS" else "stop"
            if r["scope"] != want:
                continue
            src = "sr" if r["file"].startswith(P + "stage-r") else "main"
            self.bund[(src, r["m"], r["bits"], r["curve"], r["arm"], r["class"])] = r
        self.cells = {}
        for m in (3, 4, 5):
            for b in RUNGS:
                for cl in ("TT", "SS"):
                    self.cells[(cl, m, b)] = self._cell_design("main", cl, m, b, range(5))
        self.mult = {}
        self.phi = {}
        for m in (3, 4, 5):
            for cl in ("TT", "SS"):
                for b in RUNGS:
                    self.mult[(cl, m, b)], self.phi[(cl, m, b)] = self._mult(cl, m, b)
        self.D = {}
        for k, d in self.cells.items():
            s2 = mu = 0.0
            for fam in ("sub", "dik"):
                for j, v in d["rand"][fam].items():
                    if v is not None:
                        s2 += statistics.variance(v)
                        mu += statistics.mean(v)
            self.D[k] = s2 / mu if mu > 0 else 1.0
        self.resid = {}
        for cl in ("TT", "SS"):
            for m in (3, 4, 5):
                es = []
                for b in RUNGS:
                    d = self.cells[(cl, m, b)]
                    for fam in ("sub", "dik"):
                        for j, v in d["rand"][fam].items():
                            if v is None:
                                continue
                            mb = statistics.mean(v)
                            for x in v:
                                es.append((x - mb) / math.sqrt(max(mb, 1.0)) * math.sqrt(1.5))
                self.resid[(cl, m)] = np.array(es, dtype=float)

    def _cell_design(self, src, cl, m, b, curves):
        ix = self.main if src == "main" else self.sr
        d = {"rand": {"sub": {}, "dik": {}}, "kept": {}, "F": {}, "obs": {}}
        for j in curves:
            for fam, arms in (("sub", SUB), ("dik", DIK)):
                rs = [ix.get(("main", m, b, j, a, "census")) for a in arms]
                if all(r is not None and usable(r) for r in rs):
                    d["rand"][fam][j] = [frozen_count(r, cl) for r in rs]
                    d["F"][(fam, j)] = rs[0]["fb_size"]
                else:
                    d["rand"][fam][j] = None
        for A in STRUCT:
            fam = "dik" if A == "dickson" else "sub"
            kept = []
            for j in curves:
                rs = [ix.get(("main", m, b, j, a, "census")) for a in (A,) + RANDOMS[A]]
                if any(r is None for r in rs) or rs[0]["fb_size"] != rs[1]["fb_size"]:
                    continue
                if not all(usable(r) for r in rs) or any(censored(r) for r in rs):
                    continue
                kept.append(j)
                d["obs"][(A, j)] = frozen_count(rs[0], cl)
            d["kept"][A] = kept
        return d

    def _mult(self, cl, m, b, allow_ref=True):
        """Pooled multiplicity histogram of the random arms (complete instances) and the
        relation-level gamma frailty phi; nearest complete rung (scaled) if none."""
        hist = Counter()
        n_inst = 0
        trip = defaultdict(dict)
        for j in range(5):
            for a in SUB + DIK:
                rec = self.bund.get(("main", m, b, j, a, cl))
                if rec is None or not rec["complete"]:
                    continue
                n_inst += 1
                for k, v in rec["mult_hist"].items():
                    hist[int(k)] += v
                trip[(j, a in DIK)][a] = rec["relations"]
        if n_inst >= 24 and sum(hist.values()) > 0:
            num = den = 0.0
            for t in trip.values():
                if len(t) == 3:
                    v = list(t.values())
                    mb = statistics.mean(v)
                    num += statistics.variance(v) - mb
                    den += mb * mb
            phi = max(0.0, num / den) if den > 0 else 0.0
            return {"hist": dict(hist), "source_rung": b, "scale": 1.0, "n_inst": n_inst}, phi
        if not allow_ref:
            return None, None
        # nearest complete rung below
        for bb in sorted([x for x in RUNGS if x != b], key=lambda x: (abs(x - b), -x)):
            h2, phi2 = self._mult(cl, m, bb, allow_ref=False)
            if h2 is not None:
                Fb = statistics.mean(v for (fam, j), v in self.cells[(cl, m, b)]["F"].items())
                Fr = statistics.mean(v for (fam, j), v in self.cells[(cl, m, bb)]["F"].items())
                sc = Fb / Fr
                hist = Counter()
                for k, v in h2["hist"].items():
                    kk = int(round(k * sc)) if k > 6 else k
                    hist[max(1, kk)] += v
                return {"hist": dict(hist), "source_rung": bb, "scale": sc, "n_inst": h2["n_inst"]}, phi2
        return {"hist": {1: 1}, "source_rung": None, "scale": 1.0, "n_inst": 0}, 0.0


# -- generators -----------------------------------------------------------------------------

def gen_counts(gen, rng, mu, shape, cl, m, b, des, kappa=None):
    """Draw counts with per-curve mean vector mu (length J) for `shape` = (R, n_arms);
    returns an int/float array (R, n_arms, J).  kappa: optional per-arm multiplier array of
    length n_arms (planted excess scales the mean / the relation rate)."""
    mu = np.asarray(mu, dtype=float)
    R, n = shape
    J = len(mu)
    kap = np.ones(n) if kappa is None else np.asarray(kappa, dtype=float)
    M = mu[None, None, :] * kap[None, :, None] * np.ones((R, n, J))
    if gen == "G-POIS":
        return rng.poisson(M)
    if gen == "G-NB":
        D = max(des.D[(cl, m, b)], 1.0)
        if D <= 1.0 + 1e-9:
            return rng.poisson(M)
        k = np.where(M > 0, M / (D - 1.0), 1.0)
        lam = rng.gamma(shape=np.maximum(k, 1e-9), scale=1.0 / np.maximum(k, 1e-9)) * M
        return rng.poisson(lam)
    if gen == "G-CP":
        info, phi = des.mult[(cl, m, b)], des.phi[(cl, m, b)]
        hist = info["hist"]
        tot = sum(hist.values())
        bs = np.array(sorted(hist), dtype=float)
        ps = np.array([hist[int(x)] / tot for x in bs])
        EB = float((bs * ps).sum())
        lam = M / EB
        if phi and phi > 0:
            G = rng.gamma(shape=1.0 / phi, scale=phi, size=(R, n, J))
            lam = lam * G
        out = np.zeros((R, n, J), dtype=float)
        for bv, pv in zip(bs, ps):
            out += bv * rng.poisson(lam * pv)
        return out
    if gen == "G-RES":
        es = des.resid[(cl, m)]
        e = es[rng.integers(0, len(es), size=(R, n, J))]
        return np.maximum(0.0, np.rint(M + np.sqrt(np.maximum(M, 1.0)) * e))
    raise ValueError(gen)


def zstat(A, Rr):
    """A: (R, J) structured counts; Rr: (R, 3, J) random counts -> z, C_R, kappa (frozen A1)."""
    C_A = A.sum(axis=1)
    C_R = Rr.sum(axis=(1, 2)) / 3.0
    s2 = Rr.var(axis=1, ddof=1).sum(axis=1)
    V = np.maximum(s2, C_R)
    SD = np.sqrt(V * 4.0 / 3.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(SD > 0, (C_A - C_R) / SD, np.nan)
        kap = np.where(C_R > 0, C_A / C_R, np.nan)
    return z, C_R, kap


def cell_means(des, cl, m, b, A):
    """Per-kept-curve null mean of A's cell: mean of its matched random triple (frozen counts)."""
    d = des.cells[(cl, m, b)]
    fam = "dik" if A == "dickson" else "sub"
    return [statistics.mean(d["rand"][fam][j]) for j in d["kept"][A]], d["kept"][A]
