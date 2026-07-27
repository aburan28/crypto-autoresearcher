"""
Reviewer_P13REV_R1 independent numerical verification (TASK-20260724-P13-REV-R1).
v2: log-domain saddle-point Dickman rho, precomputed table + interpolation.
"""
import numpy as np

GAMMA = 0.5772156649015329
_nodes, _weights = np.polynomial.legendre.leggauss(96)

def Ein_arr(z):
    t = ((_nodes + 1.0) / 2.0)[:, None]      # map GL nodes [-1,1] -> [0,1]
    w = (_weights / 2.0)[:, None]
    zz = np.asarray(z, dtype=complex)[None, :]
    vals = (1.0 - np.exp(-t * zz)) / t
    return (w * vals).sum(axis=0)

def _xi(u):
    lo, hi = 1e-12, max(2.0, np.log(u) + 2 * np.log(np.log(u) + 1.5) + 2.0)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if (np.exp(mid) - 1.0) / mid < u:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

def logrho_scalar(u):
    """log(rho(u)) via saddle-point Laplace inversion, fully in log domain.

    Laplace transform: int_0^inf rho(u) e^{-s u} du = exp(gamma - Ein(s)).
    Saddle of e^{u s - Ein(s)} for u > 1 is at s = -xi with (e^xi - 1)/xi = u.
    rho(u) = e^gamma/(2 pi) int exp(u(-xi + i t) - Ein(-xi + i t)) dt.
    """
    if u <= 1.0:
        return 0.0
    xi = _xi(u)
    h, T = 0.05, 25.0
    tau = np.arange(0.0, T, h)
    E = Ein_arr(-xi + 1j * tau)
    E0 = Ein_arr(np.array([-xi + 0j]))[0]
    D = E - E0
    integrand = np.exp(-D.real) * np.cos(u * tau - D.imag)
    integ = np.trapezoid(integrand, dx=h)
    return GAMMA - u * xi - E0.real - np.log(np.pi) + np.log(integ)

# precompute table
UGRID = np.concatenate([np.arange(1.0, 30.0, 0.05), np.arange(30.0, 260.5, 0.5)])
LRHO = np.array([logrho_scalar(u) for u in UGRID])

def logrho(u):
    u = np.asarray(u, dtype=float)
    out = np.interp(u, UGRID, LRHO)
    return out

def rho(u):
    return float(np.exp(logrho(float(u))))

print("== validation of rho ==")
exact2 = 1 - np.log(2)
print(f"rho(2) = {rho(2):.8f}   exact 1-ln2 = {exact2:.8f}   relerr = {abs(rho(2)-exact2)/exact2:.2e}")
for u in (3, 4, 5, 6, 7, 8, 10):
    print(f"rho({u}) = {rho(u):.6e}   (log2 rho = {logrho(u)/np.log(2):.3f})")

# ---------- (2) Section 4.2 consistency checks ----------
print("\n== Sec 4.2 check 1: p = 5*2^248 - 1, B = 12589, 100000 samples ==")
lnp1 = np.log(5.0) + 248 * np.log(2.0)
lnB1 = np.log(12589.0)
u1 = (lnp1 - np.log(2.0)) / (3 * lnB1)
r1 = rho(u1)
print(f"ln(p/2) = {lnp1 - np.log(2):.4f}, ln B = {lnB1:.5f}, u = {u1:.4f}")
print(f"rho(u) = {r1:.6e}  = 1/{1/r1:.0f}   paper claims rho(u) ~ 1/69232 = {1/69232:.6e}")
print(f"expected #samples this smooth or better: 100000 * rho = {100000*r1:.3f} (observed: 1)")
for dB in (-1, +1):
    ub = (lnp1 - np.log(2.0)) / (3 * np.log(12589.0 + dB))
    print(f"sensitivity B={12589+dB}: u={ub:.4f}, rho={rho(ub):.3e} = 1/{1/rho(ub):.0f}")
# what u would give exactly 1/69232?
print(f"u^{-u} variant at u={u1:.4f}: u^-u = {u1**-u1:.3e} = 1/{u1**u1:.0f}")

print("\n== Sec 4.2 check 2: p = 27*2^500 - 1, B = e^23, 10000 samples ==")
lnp2 = np.log(27.0) + 500 * np.log(2.0)
u2 = (lnp2 - np.log(2.0)) / (3 * 23.0)
r2 = rho(u2)
print(f"ln(p/2) = {lnp2 - np.log(2):.4f}, u = {u2:.4f}")
print(f"rho(u) = {r2:.6e}  = 1/{1/r2:.0f}   paper claims rho(u) ~ 1/3312 = {1/3312:.6e}")
print(f"expected #samples: 10000 * rho = {10000*r2:.3f} (observed: 1)")
print(f"u^{-u} variant at u={u2:.4f}: u^-u = {u2**-u2:.3e} = 1/{u2**u2:.0f}")

# ---------- (3) Section 4.1 five pairs ----------
LN2 = np.log(2.0)

def model(bits, log2B, p0_mode):
    log2X = 0.5 * log2B + (bits - 1) / 6.0
    w = log2X / log2B
    if w < 1.0:
        return None
    log2Psi = log2X + logrho(w) / LN2
    log2M = log2Psi + log2X
    u = (bits - 1) / (3.0 * log2B)
    log2invP0 = u * np.log2(u) if p0_mode == "u^-u" else -logrho(u) / LN2
    return log2M + log2invP0, log2M, w, u

paper = {256: (106.5, 92.5), 384: (157.5, 138.6), 512: (204.2, 181.3),
         576: (230.9, 206.0), 768: (302.4, 272.2)}
grid = np.arange(1.0, 80.0, 0.05)

for mode in ("u^-u", "rho"):
    print(f"\n== Sec 4.1 reproduction, P0 = {mode} ==")
    for bits, (tp, mp) in paper.items():
        best = None
        for log2B in grid:
            res = model(bits, log2B, mode)
            if res is None:
                continue
            if best is None or res[0] < best[0]:
                best = (res[0], res[1], log2B, res[2], res[3])
        T, M, B, w, u = best
        print(f"log2p={bits}: time {T:.2f} (paper {tp}, delta {T-tp:+.2f}), "
              f"mem {M:.2f} (paper {mp}, delta {M-mp:+.2f}), "
              f"opt log2B={B:.2f}, w={w:.2f}, u={u:.2f}")

# ---------- (4) lower-bound constant factor ----------
print("\n== Sec 4.1 'M is a lower bound' constant-factor assessment ==")
for bits in paper:
    best = None
    for log2B in grid:
        res = model(bits, log2B, "u^-u")
        if res is None:
            continue
        if best is None or res[0] < best[0]:
            best = (res[0], res[1], log2B, res[2], res[3])
    T, M, B, w, u = best
    lnB = B * LN2
    ss = np.linspace(1e-6, 1.0, 20000)
    uu = w + np.log(ss) / lnB
    lr = np.where(uu > 1.0, logrho(np.clip(uu, 1.0, 260.0)), 0.0)
    rr = np.exp(lr)
    integ = np.trapezoid(ss * rr, ss)
    R = (rho(w) - integ) / rho(w)
    log2X = 0.5 * B + (bits - 1) / 6.0
    wX2 = (log2X - 1.0) / B
    psi_ratio = 0.5 * np.exp(logrho(wX2) - logrho(w))  # Psi(X/2)/Psi(X)
    trunc = 0.5 * (1 - psi_ratio)
    print(f"log2p={bits}: sum_d/(X*Psi) ~ {R:.3f} (so M overestimates the Dickman-model"
          f" sum by ~{1/R:.2f}x); rigorous truncation: sum d >= {trunc:.3f}*X*Psi"
          f" (M overstates provable LB by ~{1/trunc:.1f}x = {np.log2(1/trunc):.2f} bits)")
