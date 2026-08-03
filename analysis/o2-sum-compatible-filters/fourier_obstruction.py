#!/usr/bin/env python3
"""
Numerical verification of a Fourier obstruction theorem for sum-compatible
filters on a cyclic group, i.e. the object (O2) of claim_a_adjudication.md.

The theorem being checked (see fourier_obstruction.md for statement + proof):

  Let G be cyclic of order N with generator G0, so x <-> [x]G0 identifies G
  with Z/N and `x` IS the discrete logarithm. Let h: G -> [M], let
  A_c = h^{-1}(c) with density alpha_c, and let

     ghat_t(xi) = E_x[ e(t h(x)/M) e(-xi x/N) ]          (t != 0)
     Delta      = max_{t != 0} max_xi | ghat_t(xi) |
     delta      = max_c max_{xi != 0} | indicatorhat_{A_c}(xi) |

  (T1) exact identity, f = group law:
         eps_+ = (1/M) sum_t sum_xi ghat_t(xi) |ghat_t(xi)|^2
  (T2) group-law bound:      eps_+     <= 1/M + Delta
  (T3) arbitrary-f bound:    eps_joint <= max_c alpha_c + M * delta

Delta and delta measure correlation of h with a CHARACTER OF THE DISCRETE
LOGARITHM. So any filter clearing Wagner's bar must correlate with the dlog.

Everything here is exact enumeration over the whole group (no sampling), so
these are identities/inequalities checked to floating-point, not statistics.
"""
import numpy as np
import hashlib

# ---------------------------------------------------------------- primitives

def is_prime(n):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def curve_order(p, a, b):
    """#E(F_p) = p + 1 + sum_x chi(x^3+ax+b)."""
    tot = p + 1
    e = (p - 1) // 2
    for x in range(p):
        v = (x * x % p * x + a * x + b) % p
        if v:
            tot += 1 if pow(v, e, p) == 1 else -1
    return tot


def padd(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def find_prime_order_curve(pmin, pmax):
    """Smallest prime-order curve with p in [pmin, pmax]."""
    for p in range(pmin, pmax):
        if not is_prime(p):
            continue
        for a in range(0, 8):
            for b in range(1, 12):
                if (4 * a ** 3 + 27 * b * b) % p == 0:
                    continue
                n = curve_order(p, a, b)
                if is_prime(n):
                    return p, a, b, n
    return None


def dlog_table(p, a, b, N):
    """pts[i] = [i]G0 for a generator G0; index i IS the discrete log."""
    G0 = None
    for x in range(p):
        v = (x * x % p * x + a * x + b) % p
        if v and pow(v, (p - 1) // 2, p) == 1:
            y = next(yy for yy in range(p) if yy * yy % p == v)
            G0 = (x, y)
            break
    pts = [None] * N
    cur = None
    for i in range(N):
        pts[i] = cur
        cur = padd(cur, G0, p, a)
    assert cur is None, "generator did not have full order"
    return G0, pts


# ------------------------------------------------------------ the quantities

def eps_group_law(hv, M, S):
    """Exact E_{x,y} 1[h(x+y) = h(x)+h(y) mod M]."""
    a = hv[:, None]
    bb = hv[None, :]
    return float(np.mean(hv[S] == (a + bb) % M))


def eps_best_f(hv, M, S):
    """Exact max over ALL f: E_{x,y} 1[h(x+y) = f(h(x),h(y))]."""
    N = len(hv)
    flat = ((hv[:, None] * M + hv[None, :]) * M + hv[S]).ravel()
    cnt = np.bincount(flat, minlength=M ** 3).reshape(M, M, M)
    return float(cnt.max(axis=2).sum()) / (N * N)


def fourier_quantities(hv, M):
    """Delta (over g_t) and delta (over indicators A_c)."""
    N = len(hv)
    Delta = 0.0
    gh = []
    for t in range(M):
        g = np.exp(2j * np.pi * t * hv / M)
        ghat = np.fft.fft(g) / N
        gh.append(ghat)
        if t != 0:
            Delta = max(Delta, float(np.abs(ghat).max()))
    delta = 0.0
    alpha = np.bincount(hv, minlength=M) / N
    for c in range(M):
        ind = (hv == c).astype(float)
        ihat = np.fft.fft(ind) / N
        ihat[0] = 0.0                      # xi != 0 only
        delta = max(delta, float(np.abs(ihat).max()))
    return Delta, delta, alpha, gh


def identity_rhs(gh, M):
    """(1/M) sum_t sum_xi ghat_t(xi) |ghat_t(xi)|^2 -- must equal eps_+."""
    tot = 0.0 + 0.0j
    for t in range(M):
        ghat = gh[t]
        tot += np.sum(ghat * np.abs(ghat) ** 2)
    return tot / M


# ------------------------------------------------------------------- filters

def h_x_mod(pts, p, M):
    """Low bits of the x-coordinate (the filter measured in the F1 search)."""
    return np.array([(0 if P is None else P[0]) % M for P in pts], dtype=np.int64)


def h_sha(pts, M):
    """Structureless null."""
    out = []
    for P in pts:
        s = b"O" if P is None else b"%d,%d" % P
        out.append(int.from_bytes(hashlib.sha256(s).digest()[:8], "big") % M)
    return np.array(out, dtype=np.int64)


def h_dlog(N, M):
    """The dlog pull-back: satisfies F1 but violates the cost clause."""
    return np.arange(N, dtype=np.int64) % M


def report(tag, hv, M, S, note=""):
    N = len(hv)
    ep = eps_group_law(hv, M, S)
    ej = eps_best_f(hv, M, S)
    Delta, delta, alpha, gh = fourier_quantities(hv, M)
    rhs = identity_rhs(gh, M)
    id_err = abs(rhs.real - ep) + abs(rhs.imag)
    b2 = 1.0 / M + Delta
    b3 = float(alpha.max()) + M * delta
    print(
        f"{tag:<26} M={M:<4d} eps_+={ep:.5f} eps_f={ej:.5f} "
        f"1/M={1.0/M:.5f} | Delta={Delta:.5f} delta={delta:.5f} | "
        f"(T1)err={id_err:.2e} (T2){'OK ' if ep <= b2 + 1e-12 else 'FAIL'} "
        f"bnd={b2:.5f} (T3){'OK ' if ej <= b3 + 1e-12 else 'FAIL'} "
        f"bnd={min(b3,1.0):.5f} {note}"
    )
    return dict(eps_plus=ep, eps_f=ej, Delta=Delta, delta=delta,
                id_err=id_err, t2=ep <= b2 + 1e-12, t3=ej <= b3 + 1e-12)


# ---------------------------------------------------------------------- main

def main():
    print("=" * 118)
    print("PART 1 -- Z/N positive control (a group where a sum-compatible filter"
          " provably exists)")
    print("=" * 118)
    for N in (1024, 1021):
        S = (np.arange(N)[:, None] + np.arange(N)[None, :]) % N
        for M in (4, 16, 64):
            hv = np.arange(N, dtype=np.int64) % M
            note = "(M | N: exact homomorphism)" if N % M == 0 else "(M does not divide N: 2 candidates)"
            report(f"Z/{N} h=x mod M", hv, M, S, note)
        print()

    print("=" * 118)
    print("PART 2 -- prime-order E(F_p): the case that matters")
    print("=" * 118)
    results = []
    for lo, hi in ((500, 700), (1100, 1300), (1900, 2100)):
        found = find_prime_order_curve(lo, hi)
        if not found:
            continue
        p, a, b, N = found
        G0, pts = dlog_table(p, a, b, N)
        S = (np.arange(N)[:, None] + np.arange(N)[None, :]) % N
        print(f"\ncurve y^2 = x^3 + {a}x + {b} over F_{p}, #E = {N} (prime), "
              f"G0 = {G0},  1/sqrt(N) = {1/np.sqrt(N):.5f}")
        for M in (4, 16):
            r = report("  h = x-coord mod M", h_x_mod(pts, p, M), M, S)
            results.append((N, M, "x mod M", r))
            r = report("  h = SHA256 mod M", h_sha(pts, M), M, S)
            results.append((N, M, "sha", r))
            r = report("  h = dlog mod M", h_dlog(N, M), M, S, "<-- cost clause violated")
            results.append((N, M, "dlog", r))

    print()
    print("=" * 118)
    print("PART 3 -- does Delta for the x-coordinate filter scale like N^{-1/2}?")
    print("  (this is the quantity the theorem turns the whole (h,f,M) sweep into)")
    print("=" * 118)
    print(f"{'N':>8} {'M':>4} {'Delta':>10} {'1/sqrt(N)':>10} {'ratio':>8}")
    for lo, hi in ((500, 700), (1100, 1300), (1900, 2100), (3900, 4100), (7900, 8100)):
        found = find_prime_order_curve(lo, hi)
        if not found:
            continue
        p, a, b, N = found
        G0, pts = dlog_table(p, a, b, N)
        for M in (16,):
            Delta, delta, alpha, gh = fourier_quantities(h_x_mod(pts, p, M), M)
            print(f"{N:>8} {M:>4} {Delta:>10.5f} {1/np.sqrt(N):>10.5f} "
                  f"{Delta*np.sqrt(N):>8.3f}")

    print()
    print("=" * 118)
    print("SUMMARY")
    print("=" * 118)
    bad_id = [r for r in results if r[3]["id_err"] > 1e-9]
    bad_t2 = [r for r in results if not r[3]["t2"]]
    bad_t3 = [r for r in results if not r[3]["t3"]]
    print(f"  (T1) exact identity   : {len(results)-len(bad_id)}/{len(results)} hold to 1e-9")
    print(f"  (T2) group-law bound  : {len(results)-len(bad_t2)}/{len(results)} hold")
    print(f"  (T3) arbitrary-f bound: {len(results)-len(bad_t3)}/{len(results)} hold")
    for label, bad in (("T1", bad_id), ("T2", bad_t2), ("T3", bad_t3)):
        for N, M, tag, r in bad:
            print(f"    VIOLATION {label}: N={N} M={M} {tag} {r}")


if __name__ == "__main__":
    main()
