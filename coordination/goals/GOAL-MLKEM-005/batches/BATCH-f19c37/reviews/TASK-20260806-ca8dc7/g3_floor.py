"""RED TEAM check 1: operating characteristic of the FROZEN G3 rule on a
CORRECT instrument.  No committed datum is read.  Pure sampling theory."""
import numpy as np

# ---- exact P(t_nu > 1.0) by numerical integration of the Student-t density
def t_sf(x, nu, n=4_000_001, hi=60.0):
    from math import lgamma, log, pi, exp
    c = exp(lgamma((nu+1)/2) - lgamma(nu/2) - 0.5*log(nu*pi))
    u = np.linspace(x, hi, n)
    f = c * (1.0 + u*u/nu) ** (-(nu+1)/2)
    return float(np.trapezoid(f, u))

for nu in (7, 15, 31, 127, 1023):
    print("df=%5d  P(t>1.0) = %.6f" % (nu, t_sf(1.0, nu)))
print("normal limit P(Z>1) = 0.158655")
print()

# ---- G3 as frozen, on a PERFECT instrument.
# Model, stated explicitly: 13 grid points, 8 paired draws.  The true mean
# curve m(t) is EXACTLY non-increasing (a correct instrument).  Steps in the
# region where the frame law is already Haar are exactly zero -- this is not an
# assumption about the data, it is forced by the design: at t >= 0.1 the frozen
# family IS a Haar projector to within the run's own exact V (see report S4).
# Paired step differences are iid normal within a step (the most favourable
# possible noise model for the gate).
rng = np.random.default_rng(20260806)
NDRAW = 8
def g3_cell(n_flat, n_decr, true_steps, sd=1.0, trials=200_000):
    """returns (P_FAIL, P_TIE, P_PASS) for one cell under the frozen rule."""
    fail = tie = pas = 0
    steps = np.array([0.0]*n_flat + list(true_steps))
    for _ in range(trials):
        x = rng.standard_normal((steps.size, NDRAW)) * sd + steps[:, None]
        D = x.mean(1)
        SE = x.std(1, ddof=1) / np.sqrt(NDRAW)
        inc = D > 0
        if np.any(D > SE):
            fail += 1
        elif np.any(inc):
            tie += 1
        else:
            pas += 1
    return fail/trials, tie/trials, pas/trials

# n_flat = number of steps whose true value is zero (Haar-plateau steps).
# n_decr steps carry a true decrease of `dz` in SE units of the paired step.
for n_flat in (3, 4, 5):
    for dz in (2.0, 4.0, 8.0):
        f, t_, p = g3_cell(n_flat, 12-n_flat, [-dz]*(12-n_flat))
        print("flat_steps=%d  true decrease=%.0f SE : cell P(FAIL)=%.4f P(TIE)=%.4f P(PASS)=%.4f"
              "  ||  4-cell overall P(FAIL)=%.4f P(PASS)=%.6f"
              % (n_flat, dz, f, t_, p, 1-(1-f)**4, p**4))
