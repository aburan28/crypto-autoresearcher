"""Shared review code for TASK-20261009-bfdc5b (red team, REVIEW-PFDR-20261009-eb0048).

Written from the frozen text of experiments/EXP-PFDR-0b3699/specification.yaml
(analysis.statistic, analysis.calibration_G-NB-R, analysis.upper_bound_U_A,
analysis.X_rel, analysis.PC-NULL-R_rule, analysis.permutation_null_RC-3) and
EXP-PFDR-011cd0 specification.yaml (CC-8, A-CAL_calibration, A-INT_intervals),
BEFORE experiments/EXP-PFDR-0b3699/analyze_a.py was opened by this session.
Imports no experiment script and no crypto_autoresearcher module.

Readings taken here (declared; the text leaves them open):
  RD-1 rho1_hat_b = sum_{j in b} nbar_j / sum_{j in b} mu_model(j), nbar_j the
       mean of r0, r1, r2 on curve j (A-CAL: "estimated from r0..r2 only").
  RD-2 D_b = max(D_hat_b, 1), D_hat_b = sum_{j in b} s_j^2 / sum_{j in b} nbar_j.
  RD-3 NB(mean m, variance D m) = numpy negative_binomial(n = m/(D-1), p = 1/D);
       Poisson when D == 1.
  RD-4 a "seed-averaged" quantile is the mean of the five per-family quantiles.
  RD-5 the U_A dev distribution at kappa is simulated with a bank of
       (C_R*, V*) null-random replicates and the structured total drawn in
       closed form (the sum over curves of independent NB with a common p is
       NB; of Poissons is Poisson; of Binomial(X_j, kappa) is
       Binomial(sum X_j, kappa)). Exact in law, not an approximation.
  RD-6 the per-synthetic-design bound in the coverage simulation uses q_lo
       (or q_abs) interpolated linearly on a kappa grid of step 0.0025
       computed from the same law; the text fixes no inner replicate count.
  RD-7 compound planting at kappa: the A-arm per-curve count is NB with mean
       kappa m_j and dispersion 1.307 x D_b (the A-arm dispersion the text
       names), drawn in closed form as a total; for kappa <= 1 the null rule.
"""
import json
import numpy as np

SCR = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/bfdc5b"
REVIEW_TOKEN = 0xBFDC5B  # this review's own seed root (independent of 0x0b3699)
RUNGS = (30, 32)
NULLS = ("random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub")


def load():
    d = np.load(f"{SCR}/counts.npz")
    return {k: d[k] for k in d.files}


def cc8(cA, r0, r1, r2):
    """CC-8 pooled statistic. Inputs are per-curve integer arrays (same curves)."""
    cA = np.asarray(cA, dtype=np.float64)
    R = np.vstack([r0, r1, r2]).astype(np.float64)
    C_A = cA.sum()
    C_R = R.sum() / 3.0
    s2 = R.var(axis=0, ddof=1)
    S2 = s2.sum()
    V = max(S2, C_R)
    SD = np.sqrt(4.0 * V / 3.0)
    return {"C_A": C_A, "C_R": C_R, "three_C_R": R.sum(), "sum_s2": S2, "V": V, "SD_null": SD,
            "z": (C_A - C_R) / SD, "kappa_rel": C_A / C_R, "SE": SD / C_R}


def fit_gnbr(d, mask=None):
    """rho1_hat_b and D_b per rung from r0..r2 (RD-1, RD-2)."""
    out = {}
    for b in RUNGS:
        sel = d["bits"] == b
        if mask is not None:
            sel = sel & mask
        R = np.vstack([d[f"cnt_random_sub_r{i}"][sel] for i in range(3)]).astype(np.float64)
        nbar = R.mean(axis=0)
        s2 = R.var(axis=0, ddof=1)
        rho1 = nbar.sum() / d["mu_model"][sel].sum()
        Dhat = s2.sum() / nbar.sum()
        out[b] = {"rho1_hat": rho1, "D_hat": Dhat, "D": max(Dhat, 1.0), "curves": int(sel.sum()),
                  "sum_nbar": nbar.sum(), "sum_s2": s2.sum(), "sum_mu_model": d["mu_model"][sel].sum()}
    return out


class Model:
    """G-NB-R null model at the realised curves: per-curve means m_j and per-rung D."""

    def __init__(self, d, fit, mask=None, D_override=None):
        sel = np.ones(len(d["bits"]), dtype=bool) if mask is None else mask
        self.bits = d["bits"][sel]
        mu = d["mu_model"][sel]
        self.m = np.empty(len(mu))
        self.D = np.empty(len(mu))
        for b in RUNGS:
            s = self.bits == b
            self.m[s] = fit[b]["rho1_hat"] * mu[s]
            self.D[s] = fit[b]["D"] if D_override is None else D_override[b]
        self.rungs = tuple(b for b in RUNGS if np.any(self.bits == b))  # single-rung masks allowed
        self.rung_M = {b: self.m[self.bits == b].sum() for b in self.rungs}
        self.rung_D = {b: float(self.D[self.bits == b][0]) for b in self.rungs}
        self.M = self.m.sum()
        self.ncurves = len(self.m)

    # per-curve draws -------------------------------------------------------
    def draw_curves(self, rng, reps, narms):
        """(reps, narms, ncurves) int array of independent G-NB-R null draws."""
        out = np.empty((reps, narms, self.ncurves), dtype=np.int32)
        for b in self.rungs:
            s = self.bits == b
            D = self.rung_D[b]
            m = self.m[s]
            if D > 1.0:
                out[:, :, s] = rng.negative_binomial(m / (D - 1.0), 1.0 / D, size=(reps, narms, s.sum()))
            else:
                out[:, :, s] = rng.poisson(m, size=(reps, narms, s.sum()))
        return out

    # closed-form totals (RD-5) ---------------------------------------------
    def null_total(self, rng, size, D_mult=1.0, mean_mult=1.0):
        tot = np.zeros(size, dtype=np.int64)
        for b in self.rungs:
            D = self.rung_D[b] * D_mult
            Mb = self.rung_M[b] * mean_mult
            if D > 1.0:
                tot += rng.negative_binomial(Mb / (D - 1.0), 1.0 / D, size=size)
            else:
                tot += rng.poisson(Mb, size=size)
        return tot

    def struct_total(self, rng, size, kappa, planting="poisson", comp_mult=1.307):
        """Structured-arm pooled total at kappa by the frozen simulation rule."""
        if kappa < 1.0:
            base = self.null_total(rng, size)
            return rng.binomial(base, kappa)
        if kappa == 1.0:
            return self.null_total(rng, size)
        if planting == "poisson":
            return self.null_total(rng, size) + rng.poisson((kappa - 1.0) * self.M, size=size)
        if planting == "compound":  # RD-7
            return self.null_total(rng, size, D_mult=comp_mult, mean_mult=kappa)
        raise ValueError(planting)


def random_bank(model, rng, reps, chunk=500):
    """Bank of (C_R*, V*) from three G-NB-R random arms per replicate."""
    CR = np.empty(reps)
    V = np.empty(reps)
    done = 0
    while done < reps:
        k = min(chunk, reps - done)
        x = model.draw_curves(rng, k, 3).astype(np.float64)
        tot = x.sum(axis=1)  # (k, curves)
        sq = (x * x).sum(axis=1)
        s2 = (sq - tot * tot / 3.0) / 2.0
        CR[done:done + k] = tot.sum(axis=1) / 3.0
        V[done:done + k] = np.maximum(s2.sum(axis=1), CR[done:done + k])
        done += k
    return CR, V


def z_from(CA, CR, V):
    return (CA - CR) / np.sqrt(4.0 * V / 3.0)


def dev_quantiles(model, rng, CR, V, kappa, planting="poisson"):
    """dev = (kappa* - kappa)/SE* on the bank; returns arrays for signed and |dev|."""
    CA = model.struct_total(rng, CR.shape, kappa, planting=planting).astype(np.float64)
    kst = CA / CR
    SE = np.sqrt(4.0 * V / 3.0) / CR
    return (kst - kappa) / SE


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=conv)


def nb_pmf_table(m, D, kmax):
    """(len(m), kmax+1) pmf of NB(mean m, variance D m); Poisson if D == 1. Recurrence, no scipy."""
    m = np.asarray(m, dtype=np.float64)
    out = np.empty((len(m), kmax + 1))
    if D > 1.0:
        r = m / (D - 1.0)
        p = 1.0 / D
        out[:, 0] = np.exp(r * np.log(p))
        for k in range(kmax):
            out[:, k + 1] = out[:, k] * (k + r) / (k + 1) * (1 - p)
    else:
        out[:, 0] = np.exp(-m)
        for k in range(kmax):
            out[:, k + 1] = out[:, k] * m / (k + 1)
    return out


def poisson_sf(kminus1, lam):
    """P(Poisson(lam) > kminus1) = P(X >= kminus1 + 1)."""
    import math
    s, t = 0.0, math.exp(-lam)
    for k in range(int(kminus1) + 1):
        s += t
        t *= lam / (k + 1)
    return max(0.0, 1.0 - s)
