"""Departure laws for J-DISP and J-COV (TASK-20261009-bfdc5b).

Each law produces, per replicate, the pooled (C_R, V) of three random arms and the
structured-arm total C_A at a given kappa by the frozen SIMULATION RULE applied to that
law's null draw (Poisson-planted excess (kappa - 1) m_j added per curve for kappa > 1;
binomial thinning for kappa < 1). Per-curve draws throughout (no closed forms).

kinds:
  nb_D          NB with per-rung D given (e.g. the 99% upper end of D_hat)
  zinf          zero-inflated: 0 w.p. pi, else NB(m/(1-pi), D)
  cluster       X = sum_k k Pois(lambda_j c_k), lambda_j = m_j / sum_k k c_k (clumped relations)
  gamma_shared  curve effect G_j ~ Gamma(1/tau2, tau2) shared by every arm on the curve
  gamma_unshared_A  curve effect for the randoms; A gets an independent effect G'_j
  A_overdispersed   randoms G-NB-R; A arm NB with dispersion rhoA x D
"""
import numpy as np
import common as C


class Law:
    def __init__(self, model, kind, **kw):
        self.model = model
        self.kind = kind
        self.kw = kw
        self.m = model.m
        self.D = model.D  # per-curve array of the rung D
        self.n = model.ncurves

    def _nb(self, rng, mean, D, size):
        D = np.broadcast_to(D, mean.shape) if np.ndim(D) else np.full(mean.shape, D)
        out = np.empty(size, dtype=np.float64)
        pois = D <= 1.0
        # per-curve D may differ (rungs); draw by unique D values
        for Dv in np.unique(D):
            s = D == Dv
            if Dv > 1.0:
                out[..., s] = rng.negative_binomial(mean[s] / (Dv - 1.0), 1.0 / Dv, size=size[:-1] + (int(s.sum()),))
            else:
                out[..., s] = rng.poisson(mean[s], size=size[:-1] + (int(s.sum()),))
        return out

    def draw(self, rng, reps):
        """Returns (x3, a): x3 (reps, 3, n) random arms, a (reps, n) structured-arm null draw."""
        n, m = self.n, self.m
        k = self.kind
        if k == "nb_D":
            Dc = np.where(self.model.bits == 30, self.kw["D"][30], self.kw["D"][32])
            x = self._nb(rng, m, Dc, (reps, 4, n))
        elif k == "zinf":
            pi = self.kw["pi"]
            x = self._nb(rng, m / (1 - pi), self.D, (reps, 4, n))
            x *= rng.random((reps, 4, n)) >= pi
        elif k == "cluster":
            c = np.asarray(self.kw["c"], dtype=float)  # c[0] for size 1, c[1] size 2, ...
            lam = m / np.sum((np.arange(len(c)) + 1) * c)
            x = np.zeros((reps, 4, n))
            for i, ci in enumerate(c):
                if ci > 0:
                    x += (i + 1) * rng.poisson(lam * ci, size=(reps, 4, n))
        elif k in ("gamma_shared", "gamma_unshared_A"):
            t2 = self.kw["tau2"]
            G = rng.gamma(1.0 / t2, t2, size=(reps, 1, n))
            mm = m * G
            if k == "gamma_unshared_A":
                G2 = rng.gamma(1.0 / t2, t2, size=(reps, 1, n))
                mm = np.concatenate([np.broadcast_to(mm, (reps, 3, n)), m * G2], axis=1)
            else:
                mm = np.broadcast_to(mm, (reps, 4, n))
            # within-arm dispersion: NB with the rung D around the gamma-mixed mean
            x = np.empty((reps, 4, n))
            for b in C.RUNGS:
                s = self.model.bits == b
                Dv = self.model.rung_D[b]
                lamg = rng.gamma(mm[:, :, s] / (Dv - 1.0), Dv - 1.0) if Dv > 1 else mm[:, :, s]
                x[:, :, s] = rng.poisson(lamg)
        elif k == "A_overdispersed":
            x = self._nb(rng, m, self.D, (reps, 4, n))
            x[:, 3, :] = self._nb(rng, m, self.D * self.kw["rhoA"], (reps, n))
        else:
            raise ValueError(k)
        return x[:, :3, :], x[:, 3, :]

    def joint(self, rng, reps, kappa, chunk=250):
        """(C_R, V, C_A) per replicate at kappa by the frozen rule on this law."""
        CR = np.empty(reps)
        V = np.empty(reps)
        CA = np.empty(reps)
        done = 0
        while done < reps:
            k = min(chunk, reps - done)
            x3, a = self.draw(rng, k)
            if kappa > 1.0:
                a = a + rng.poisson((kappa - 1.0) * self.m, size=a.shape)
            elif kappa < 1.0:
                a = rng.binomial(a.astype(np.int64), kappa)
            tot = x3.sum(axis=1)
            sq = (x3 * x3).sum(axis=1)
            s2 = ((sq - tot * tot / 3.0) / 2.0).sum(axis=1)
            cr = tot.sum(axis=1) / 3.0
            CR[done:done + k] = cr
            V[done:done + k] = np.maximum(s2, cr)
            CA[done:done + k] = a.sum(axis=1)
            done += k
        return CR, V, CA
