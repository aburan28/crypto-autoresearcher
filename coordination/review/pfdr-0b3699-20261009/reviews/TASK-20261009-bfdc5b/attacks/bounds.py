"""U_A bounds, coverage and X_rel, re-implemented from analysis.upper_bound_U_A and
analysis.X_rel (EXP-PFDR-0b3699 specification.yaml) and A-INT_intervals
(EXP-PFDR-011cd0), before analyze_a.py was opened. TASK-20261009-bfdc5b.

Signed bound:  dev = (kappa* - kappa_hat)/SE*, q_lo = 0.05 quantile of dev,
               U = kappa_hat - q_lo x SE (SE = SD_null/C_R observed).
|dev| bound:   q_abs = 0.95 quantile of |dev|, U_abs = kappa_hat + q_abs x SE.
Both simulated at kappa = kappa_hat by the SIMULATION RULE (null draw;
Poisson-planted excess if kappa > 1; binomial thinning if kappa < 1).
Per-family quantiles averaged over the bank's families (RD-4).
"""
import numpy as np
import common as C


class Bounds:
    def __init__(self, model, bankCR, bankV, families, seed_tag, grid=None, planting="poisson"):
        self.model = model
        self.CR = bankCR
        self.V = bankV
        self.fam = families
        self.seed_tag = seed_tag
        self.planting = planting
        self.grid = np.round(np.arange(0.80, 1.40 + 1e-9, 0.0025), 6) if grid is None else grid
        self._q_lo = None
        self._q_abs = None

    def quantiles_at(self, kappa, rng_list):
        per = len(self.CR) // self.fam
        qlo, qabs = [], []
        for f in range(self.fam):
            sl = slice(f * per, (f + 1) * per)
            dev = C.dev_quantiles(self.model, rng_list[f], self.CR[sl], self.V[sl], kappa, self.planting)
            qlo.append(np.quantile(dev, 0.05))
            qabs.append(np.quantile(np.abs(dev), 0.95))
        return float(np.mean(qlo)), float(np.mean(qabs)), qlo, qabs

    def build_grid(self):
        rngs = [np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, self.seed_tag, f])) for f in range(self.fam)]
        ql, qa = [], []
        for k in self.grid:
            a, b, _, _ = self.quantiles_at(float(k), rngs)
            ql.append(a)
            qa.append(b)
        self._q_lo = np.array(ql)
        self._q_abs = np.array(qa)
        return self._q_lo, self._q_abs

    def q_lo(self, k):
        return np.interp(k, self.grid, self._q_lo)

    def q_abs(self, k):
        return np.interp(k, self.grid, self._q_abs)

    def observed(self, kappa_hat, SE, seed_extra):
        rngs = [np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, self.seed_tag, 1000 + seed_extra, f]))
                for f in range(self.fam)]
        qlo, qabs, qlo_f, qabs_f = self.quantiles_at(kappa_hat, rngs)
        U_s = kappa_hat - qlo * SE
        U_a = kappa_hat + qabs * SE
        Us_f = [kappa_hat - q * SE for q in qlo_f]
        Ua_f = [kappa_hat + q * SE for q in qabs_f]
        return {"kappa_hat": kappa_hat, "SE": SE, "q_lo": qlo, "q_abs": qabs, "U_signed": U_s, "U_absdev": U_a,
                "U_signed_per_family": Us_f, "U_absdev_per_family": Ua_f,
                "U_signed_mc_se": float(np.std(Us_f, ddof=1) / np.sqrt(len(Us_f))),
                "U_absdev_mc_se": float(np.std(Ua_f, ddof=1) / np.sqrt(len(Ua_f)))}


def synthetic_designs(model, rng, ndes, kappa, planting="poisson", chunk=250, design_model=None):
    """ndes synthetic designs at true kappa: returns kappa_hat_s, SE_s, CR_s, V_s, CA_s.
    design_model (optional) generates the data under a departure; model is the analysis model."""
    gm = model if design_model is None else design_model
    if hasattr(gm, "random_bank"):
        CR, V = gm.random_bank(rng, ndes)
        CA = gm.struct_total(rng, ndes, kappa, planting=planting).astype(np.float64)
    else:
        CR, V = C.random_bank(gm, rng, ndes, chunk=chunk)
        CA = gm.struct_total(rng, ndes, kappa, planting=planting).astype(np.float64)
    kh = CA / CR
    SE = np.sqrt(4 * V / 3) / CR
    return kh, SE, CR, V, CA


def coverage(bounds, kh, SE, kappa_true):
    Us = kh - bounds.q_lo(kh) * SE
    Ua = kh + bounds.q_abs(kh) * SE
    cs = float((Us >= kappa_true).mean())
    ca = float((Ua >= kappa_true).mean())
    n = len(kh)
    return {"designs": n, "coverage_signed": cs, "coverage_signed_mc_se": float(np.sqrt(cs * (1 - cs) / n)),
            "coverage_absdev": ca, "coverage_absdev_mc_se": float(np.sqrt(ca * (1 - ca) / n)),
            "U_signed_median": float(np.median(Us)), "U_absdev_median": float(np.median(Ua))}


def x_rel(model, CR, V, t, rng, planting, grid=None):
    grid = np.round(np.arange(1.00, 1.30 + 1e-9, 0.01), 2) if grid is None else grid
    pw = {}
    xr = None
    for k in grid:
        CA = model.struct_total(rng, CR.shape, float(k), planting=planting).astype(np.float64)
        p = float((C.z_from(CA, CR, V) > t).mean())
        pw[f"{k:.2f}"] = p
        if xr is None and p >= 0.5:
            xr = float(k)
    return ("X_rel > 1.30" if xr is None else xr), pw


def power_at(model, CR, V, t, rng, kappa, planting):
    CA = model.struct_total(rng, CR.shape, float(kappa), planting=planting).astype(np.float64)
    p = float((C.z_from(CA, CR, V) > t).mean())
    return p, float(np.sqrt(p * (1 - p) / len(CR)))
