#!/usr/bin/env python3
"""
RT-EXP-1 -- the bucket-gain ladder.  Specified by RT-20260803-be45a8 as the
cheapest decisive test of the hole it found in the (O2) line.

THE HOLE.  Every theorem in that line bounds
    delta = Pr[h(P+Q) = f(h(P),h(Q))],
the q_c-weighted AVERAGE over target buckets.  A Wagner level fixes ONE bucket c
and one offset d, CHOSEN AFTER SEEING h, and is paid at max_{c,d} pi_c(d).  Since
delta = sum_c q_c pi_c, always max_c pi_c >= delta -- so the published bound
constrains a LOWER bound on the attacker's rate and says nothing about the
attacker.

WHAT THIS MEASURES.  The quantity the attacker is actually paid at:

    G  =  M * max_{c,d} pi_c(d),        pi_c(d) = Pr[h(P+Q)=c | h(P)+h(Q)+d=c]

G ~ 1 means no exploitable filtering gain at that bucket.  G growing with p for a
CHEAP h would be a real attack signal.

EXACT, NO SAMPLING.  With 1_a the indicator of level set a and (.) cyclic
convolution over Z/N (dlog indexing, so P_i+P_j has dlog i+j):

    W_s[k] = #{(i,j) : i+j=k, h(i)+h(j)=s}  =  sum_a (1_a * 1_{s-a})[k]

which is a convolution in the ALPHABET index too, so all M of them come from one
M-axis FFT of the N-axis FFTs -- M length-N transforms, not M^2.  Then

    num(c,s) = sum_{k: h(k)=c} W_s[k],   den(s) = (n *_M n)[s],   pi = num/den

with s = c-d.  Every count is exact over all N^2 pairs.

THE PLANTED POSITIVE CONTROL is the part RT-20260803-be45a8 insists on: the old
P2 control is flat by ALGEBRAIC IDENTITY, so it calibrates only the maximal-signal
end and never shows the instrument resolves the M*T ~ 1 boundary where closure is
actually decided.  Here a theta = p^{-1/9} dlog mixture is planted, which sits
near that boundary.  If the ladder cannot see the planted signal, the ladder --
not the filter -- is what failed, and no null result from it means anything.
"""
import hashlib
import sys

import numpy as np

sys.path.insert(0, ".")
from fourier_obstruction import is_prime, curve_order, dlog_table


# ---------------------------------------------------------------- the statistic
def bucket_gain(hv, M, N):
    """G = M_eff*max_{c,d} pi_c(d). Exact.

    RUN AT M_eff, THE NUMBER OF NON-EMPTY LEVEL SETS -- this is [D]'s (H6)
    non-redundancy hypothesis, which the additive completion dropped and which
    RT-20260803-be45a8 identified as the missing hypothesis.  Without it a filter
    whose image is far smaller than M (popcount mod 40 reaches only 0..16) has
    empty buckets, den(s)=0, and pi blows up to a meaningless >M value.  A filter
    is entitled to no credit for buckets it never populates.
    """
    used = np.flatnonzero(np.bincount(hv, minlength=M) > 0)
    if len(used) < M:                      # relabel onto its actual image
        remap = -np.ones(M, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv, M = remap[hv], len(used)
    if M < 2:
        return float("nan"), float("nan"), M
    ind = np.zeros((M, N))
    for a in range(M):
        ind[a] = (hv == a)
    n = ind.sum(axis=1)                                    # level-set sizes

    A = np.fft.rfft(ind, axis=1)                           # M x (N/2+1)
    As = np.fft.fft(A, axis=0)                             # convolve over alphabet
    Ws = np.fft.ifft(As * As, axis=0)                      # -> W_s in Fourier(N)
    W = np.fft.irfft(Ws, n=N, axis=1).real                 # M x N counts

    # num[s,c] = sum over k with h(k)=c of W_s[k]
    num = np.stack([W[:, hv == c].sum(axis=1) for c in range(M)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(n) ** 2))         # (n *_M n)[s]

    pi = num / np.maximum(den[:, None], 1e-12)             # pi[s,c]
    assert den.min() > 0, "empty bucket survived M_eff reduction"
    G = M * float(pi.max())

    # delta for offset d: sum_c num[c-d, c] / N^2  -> best over d
    tot = float(N) ** 2
    deltas = [sum(num[(c - d) % M, c] for c in range(M)) / tot for d in range(M)]
    return G, M * max(deltas), M


# ---------------------------------------------------------------- filters
def _sha(v, M):
    return int(hashlib.sha256(str(int(v)).encode()).hexdigest(), 16) % M


def build(kind, xs, x2s, xQs, p, N, M, rng):
    if kind == "x mod M":
        return xs % M
    if kind == "floor(Mx/p)":
        return (xs * M) // p
    if kind == "popcount":                      # family J -- the RT counterexample
        return np.array([bin(int(v)).count("1") for v in xs]) % M
    if kind == "digitsum":
        return np.array([sum(int(d) for d in str(int(v))) for v in xs]) % M
    if kind == "x([2]P)":                       # cheap, one doubling
        return x2s % M
    if kind == "h_Q target-dep":                # cheap, one addition; [D] 7.6 item 5
        return xQs % M
    if kind.endswith(" SHUF"):
        # MATCHED-MARGINAL NULL: identical level-set sizes, structure destroyed.
        # Isolates genuine sum-compatibility from the free marginal-bias floor
        # ([D] section 8.3's f_const effect).  A positive alpha that SURVIVES
        # this is signal; one that does not is imbalance.
        base = build(kind[:-5], xs, x2s, xQs, p, N, M, rng)
        out = base.copy(); rng.shuffle(out); return out
    if kind == "sha [null]":
        return np.array([_sha(v, M) for v in xs])
    if kind == "P2 dlog-int [old ctrl]":
        return (np.arange(N) * M) // N
    if kind == "PLANTED theta=p^-1/9":
        theta = p ** (-1.0 / 9.0)
        base = np.array([_sha(v, M) for v in xs])
        pick = rng.random(N) < theta
        return np.where(pick, np.arange(N) % M, base)
    raise ValueError(kind)


KINDS = ("x mod M", "floor(Mx/p)", "popcount", "popcount SHUF",
         "digitsum", "digitsum SHUF", "x([2]P)",
         "h_Q target-dep", "sha [null]", "P2 dlog-int [old ctrl]",
         "P2 dlog-int [old ctrl] SHUF", "PLANTED theta=p^-1/9")


def curves_near(p_target, want=3):
    p, out = p_target, []
    while len(out) < want:
        while not is_prime(p):
            p += 1
        for a in range(0, 12):
            for b in range(1, 12):
                if (4 * a ** 3 + 27 * b * b) % p == 0:
                    continue
                nn = curve_order(p, a, b)
                if is_prime(nn):
                    out.append((p, a, b, nn))
                    break
            if len(out) >= want:
                break
        p += 1
    return out[:want]


def main():
    rng = np.random.default_rng(20260803)
    targets = (523, 1033, 2063, 4111, 8219, 16417, 32779, 65539)
    rows = {k: [] for k in KINDS}
    ps = []

    for t in targets:
        for (p, a, b, N) in curves_near(t, 3):
            G0, pts = dlog_table(p, a, b, N)
            xs = np.array([0 if P is None else P[0] for P in pts], dtype=np.int64)
            # x([2]P): dlog of [2]P is 2i mod N
            x2s = xs[(2 * np.arange(N)) % N]
            # target-dependent: fixed random target Q, h_Q(P) = x(P+Q)
            qi = int(rng.integers(1, N))
            xQs = xs[(np.arange(N) + qi) % N]
            M = max(3, int(round(N ** (1.0 / 3.0))))
            ps.append(p)
            for kind in KINDS:
                hv = build(kind, xs, x2s, xQs, p, N, M, rng)
                G, Md, Meff = bucket_gain(hv, M, N)
                rows[kind].append((p, N, Meff, G, Md))

    print(f"{'filter':>24} " + "".join(f"{p:>9}" for p in targets)
          + f"  {'alpha(G-1)':>11} {'95% CI':>18}")
    for kind in KINDS:
        r = rows[kind]
        byp, meff = {}, {}
        for (p, N, M, G, Md) in r:
            byp.setdefault(p, []).append(G)
            meff.setdefault(p, []).append(M)
        xs_, ys_ = [], []
        cells = []
        for p in sorted(byp):
            g = float(np.mean(byp[p]))
            cells.append(g)
            if g - 1.0 > 0:
                xs_.append(np.log(p)); ys_.append(np.log(g - 1.0))
        if len(xs_) >= 4:
            X = np.vstack([xs_, np.ones(len(xs_))]).T
            beta, res, *_ = np.linalg.lstsq(X, np.array(ys_), rcond=None)
            al = beta[0]
            dof = max(1, len(xs_) - 2)
            resid = np.array(ys_) - X @ beta
            s2 = float(resid @ resid) / dof
            se = float(np.sqrt(s2 * np.linalg.inv(X.T @ X)[0, 0]))
            ci = f"[{al-1.96*se:+.2f},{al+1.96*se:+.2f}]"
        else:
            al, ci = float("nan"), "n/a"
        mtail = int(np.mean(meff[max(meff)]))
        print(f"{kind:>24} " + "".join(f"{c:>9.4f}" for c in cells)
              + f"  {al:>+11.3f} {ci:>18}  Meff={mtail}")

    print()
    print("G = M*max_{c,d} pi_c(d), the rate a Wagner level is ACTUALLY paid at.")
    print("G ~ 1 => no exploitable bucket gain.  alpha(G-1) > 0 with CI excluding 0")
    print("for a CHEAP filter would be an attack signal; nulls should decay (alpha<0).")
    print("THE PLANTED ROW IS THE INSTRUMENT TEST: if it does not separate from the")
    print("sha null, this ladder cannot resolve the boundary and NO null result from")
    print("it is meaningful -- which is exactly the defect RT found in the P2 control.")


if __name__ == "__main__":
    main()
