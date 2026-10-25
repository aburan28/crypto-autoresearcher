"""R1 attribution: rank versus regulator versus naive-height offset (red team, TASK-20261023-7b5dc6).

For each run curve:
  * canonical heights (Silverman normalisation hhat ~ h(x)/2) by the doubling limit
    hhat(P) = 1/2 lim 4^-k h(x(2^k P)), k = 7 (k = 6 kept as a convergence check);
  * the height-pairing Gram matrix of independent points (GZ: the 8 source points, BK: the 9 source
    points, both from the sealed pages of VAL-20261022-2dd0e7; rank-7 curve: 7 independent window points
    chosen greedily by naive height), its determinant R_L (regulator of the listed sublattice; the true
    regulator is R_L / index^2 and the true rank may be larger, so lattice counts below are LOWER bounds
    on #{P : hhat(P) <= T});
  * N_lat(T) = #{v in Z^r : v^T M v <= T} (exact Fincke-Pohst enumeration while small);
  * for every enumerated window point (H <= 3e5): the offset hhat(P) - h(x(P))/2;
  * T_eff(H): the canonical radius whose lattice ball holds as many points as the naive window does.
Output rt_heights_output.json.
"""
import json, math, os, sys, time
from fractions import Fraction
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L

K = 7
CURVES = {
    "382623908456a1": [0, 0, 0, -10012, 346900],
    "grunewald-zimmert-1977-rank-ge-8": [1, -1, 1, -6494556985832, 6351402068900282539],
    "brumer-kramer-1977-rank-ge-9": [1, -1, 1, -1608154463, 25555312501831],
}
SOURCE_POINTS = {
    "grunewald-zimmert-1977-rank-ge-8": [(1634797, 320450201), (-2569043, -2464593799), (1725397, 530370401),
                                         (1536847, 10928201), (-1037903, -3459834799), (-947303, -3413266399),
                                         (1536949, 13272713), (13057, 2503312241)],
    "brumer-kramer-1977-rank-ge-9": [(23045, 844952), (34381, 3285026), (25583, 1062950), (20803, 1040006),
                                     (21715, 923702), (17731, 1608326), (15371, 2106046), (19507, 1258166),
                                     (18715, 1409582)],
}


def logh_int(X, D):
    m = max(abs(X), D)
    b = m.bit_length()
    return math.log(m) if b < 1000 else (b - 60) * math.log(2) + math.log(m >> (b - 60))


def hhat(ai, x: Fraction, k=K):
    b2, b4, b6, b8 = L.b_invariants(ai)
    X, D = x.numerator, x.denominator
    ests = [logh_int(X, D) / 2]
    for j in range(1, k + 1):
        D2 = D * D; D3 = D2 * D; D4 = D2 * D2; X2 = X * X
        num = X2 * X2 - b4 * X2 * D2 - 2 * b6 * X * D3 - b8 * D4
        den = D * (4 * X2 * X + b2 * X2 * D + 2 * b4 * X * D2 + b6 * D3)
        if den == 0:
            return 0.0, 0.0
        g = math.gcd(num, den)
        X, D = num // g, den // g
        if D < 0:
            X, D = -X, -D
        ests.append(logh_int(X, D) / (2 * 4 ** j))
    return ests[-1], ests[-2]


def gram(ai, pts):
    r = len(pts)
    h = [hhat(ai, P[0])[0] for P in pts]
    M = np.zeros((r, r))
    err = 0.0
    for i in range(r):
        M[i, i] = h[i]
        for j in range(i + 1, r):
            S = L.add(ai, pts[i], pts[j])
            hs, hs5 = hhat(ai, S[0])
            err = max(err, abs(hs - hs5))
            M[i, j] = M[j, i] = (hs - h[i] - h[j]) / 2
    return M, err


def count_lattice(M, T, cap=400000):
    """#{v in Z^r : v^T M v <= T} by Fincke-Pohst; returns None if it exceeds cap."""
    r = M.shape[0]
    Q = np.linalg.cholesky(M).T  # M = Q^T Q, Q upper triangular
    # q_ii and mu_ij for the standard recursion
    q = np.zeros((r, r))
    for i in range(r):
        q[i, i] = Q[i, i] ** 2
        for j in range(i + 1, r):
            q[i, j] = Q[i, j] / Q[i, i]
    cnt = 0
    x = [0] * r

    def rec(i, rem):
        nonlocal cnt
        if cnt > cap:
            return
        c = -sum(q[i, j] * x[j] for j in range(i + 1, r))
        w = math.sqrt(max(rem, 0.0) / q[i, i])
        lo, hi = math.ceil(c - w - 1e-12), math.floor(c + w + 1e-12)
        for v in range(lo, hi + 1):
            x[i] = v
            nr = rem - q[i, i] * (v - c) ** 2
            if nr < -1e-12:
                continue
            if i == 0:
                cnt += 1
            else:
                rec(i - 1, nr)
        x[i] = 0

    rec(r - 1, T)
    return cnt if cnt <= cap else None


def gauss_heur(M, T):
    r = M.shape[0]
    return math.pi ** (r / 2) / math.gamma(r / 2 + 1) * T ** (r / 2) / math.sqrt(np.linalg.det(M))


def main():
    cnt = json.load(open(os.path.join(HERE, "rt_count_output.json")))["curves"]
    out = {"K_doublings": K, "normalisation": "Silverman: hhat(P) ~ h(x(P))/2", "curves": {}}
    for lab, ai in CURVES.items():
        t0 = time.time()
        wpts = sorted(cnt[lab]["points_adc"], key=lambda t: max(abs(t[0]), t[1] ** 2))
        if lab in SOURCE_POINTS:
            pts = [(Fraction(x), Fraction(y)) for x, y in SOURCE_POINTS[lab]]
            assert all(L.on_curve(ai, P) for P in pts)
        else:
            pts = []
            for a, d, c in wpts:
                P = L.point_from_adc(ai, a, d, c)
                trial = pts + [P]
                M, _ = gram(ai, trial)
                if np.linalg.eigvalsh(M).min() > 0.05:
                    pts = trial
                if len(pts) == 7:
                    break
        M, perr = gram(ai, pts)
        ev = np.linalg.eigvalsh(M)
        RL = float(np.linalg.det(M))
        # window points: offsets hhat - h/2
        offs = []
        for a, d, c in wpts:
            if c == 0:
                continue
            x = Fraction(a, d * d)
            hh, hh5 = hhat(ai, x)
            offs.append({"a": a, "d": d, "H": max(abs(a), d * d), "hhat": hh, "hhat_k5": hh5,
                         "offset": hh - math.log(max(abs(a), d * d)) / 2})
        # lattice counts on a T grid
        Tgrid = [0.5 * i for i in range(1, 61)]
        nl = {}
        for T in Tgrid:
            c_ = count_lattice(M, T)
            nl[T] = c_
            if c_ is None:
                break
        rec = {int(k): v for k, v in cnt[lab]["counts_mine"].items()}
        teff = {}
        for H, N in rec.items():
            if N <= 1:
                teff[H] = None
                continue
            ok = [T for T, c_ in nl.items() if c_ is not None and c_ >= N]
            teff[H] = min(ok) if ok else None
        out["curves"][lab] = {
            "basis": [[str(P[0]), str(P[1])] for P in pts], "rank_of_basis": len(pts),
            "gram": M.tolist(), "eigenvalues": ev.tolist(), "R_listed": RL,
            "pairing_convergence_max_abs(k6-k5)": perr,
            "basis_hhat": np.diag(M).tolist(),
            "N_lat": {str(T): c_ for T, c_ in nl.items()},
            "gauss_heuristic": {str(T): gauss_heur(M, T) for T in (5, 10, 15, 20, 30, 50, 100)},
            "window_offsets": {"n": len(offs), "min": min(o["offset"] for o in offs) if offs else None,
                               "median": float(np.median([o["offset"] for o in offs])) if offs else None,
                               "max": max(o["offset"] for o in offs) if offs else None,
                               "hhat_min": min(o["hhat"] for o in offs) if offs else None,
                               "hhat_max": max(o["hhat"] for o in offs) if offs else None,
                               "max_abs(k6-k5)": max(abs(o["hhat"] - o["hhat_k5"]) for o in offs) if offs else None},
            "window_points": offs if len(offs) <= 40 else offs[:40],
            "T_eff_by_H": {str(H): t for H, t in sorted(teff.items())},
            "seconds": round(time.time() - t0, 1)}
        print(lab, "R_L", RL, "eig", np.round(ev, 3), "hhat(basis)", np.round(np.diag(M), 3), "conv", perr,
              "offs", out["curves"][lab]["window_offsets"], "Teff", teff, round(time.time() - t0, 1), "s", flush=True)
    json.dump(out, open(os.path.join(HERE, "rt_heights_output.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
