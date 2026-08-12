"""EXP-MLKEM-007 -- orbit-score covariance estimation and fusion rules.

Fusion rules (specification.yaml inputs.orbit_and_scoring.fusion_rules):
  unfused_single_orbit  : orbit representative j=0 only (baseline)
  unweighted_mean       : naive average over the selected orbit (ablation)
  gls_covariance_aware  : GLS weights from the TRAINING-estimated wrong-candidate
                          orbit-score covariance Sigma
  random_signed_permutation : identical pipeline on size-matched random signed
                          permutations fixed before the secret is seen

GLS weights for a common mean under covariance Sigma:
    omega = Sigma^{-1} 1 / (1^T Sigma^{-1} 1)

Effective rank:  r_eff = (tr Sigma)^2 / tr(Sigma^2).
"""

import math


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def covariance(vectors, work=None):
    """Sample covariance of a list of equal-length vectors (ddof=1)."""
    if not vectors:
        return []
    d = len(vectors[0])
    N = len(vectors)
    mu = [0.0] * d
    for v in vectors:
        for i in range(d):
            mu[i] += v[i]
    mu = [x / N for x in mu]
    S = [[0.0] * d for _ in range(d)]
    for v in vectors:
        dv = [v[i] - mu[i] for i in range(d)]
        for i in range(d):
            di = dv[i]
            Si = S[i]
            for j in range(d):
                Si[j] += di * dv[j]
    den = max(N - 1, 1)
    for i in range(d):
        for j in range(d):
            S[i][j] /= den
    if work is not None:
        work.covariance_ops += N * d * d * 2 + d * d
        work.integer_ops += N * d * d * 2 + d * d
    return S


def effective_rank(S):
    d = len(S)
    tr = sum(S[i][i] for i in range(d))
    tr2 = 0.0
    for i in range(d):
        for j in range(d):
            tr2 += S[i][j] * S[j][i]
    if tr2 <= 0.0:
        return float("nan")
    return (tr * tr) / tr2


def inverse(S, ridge=0.0):
    d = len(S)
    A = [[S[i][j] + (ridge if i == j else 0.0) for j in range(d)] for i in range(d)]
    I = [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]
    for col in range(d):
        piv = max(range(col, d), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-300:
            return None
        A[col], A[piv] = A[piv], A[col]
        I[col], I[piv] = I[piv], I[col]
        p = A[col][col]
        A[col] = [x / p for x in A[col]]
        I[col] = [x / p for x in I[col]]
        for r in range(d):
            if r == col:
                continue
            f = A[r][col]
            if f == 0.0:
                continue
            A[r] = [A[r][t] - f * A[col][t] for t in range(d)]
            I[r] = [I[r][t] - f * I[col][t] for t in range(d)]
    return I


def gls_weights(S, ridge_rel=1e-9, work=None):
    """Weights omega with sum(omega) = 1 minimising the fused variance."""
    d = len(S)
    tr = sum(S[i][i] for i in range(d)) / max(d, 1)
    Sinv = inverse(S, ridge=ridge_rel * tr)
    if Sinv is None:
        return [1.0 / d] * d, False
    ones = [sum(Sinv[i][j] for j in range(d)) for i in range(d)]
    tot = sum(ones)
    if abs(tot) < 1e-300:
        return [1.0 / d] * d, False
    if work is not None:
        work.covariance_ops += d ** 3
        work.integer_ops += d ** 3
    return [x / tot for x in ones], True


def fuse(scores_vec, weights):
    return sum(w * s for w, s in zip(weights, scores_vec))


def standardise(values, mu, sd):
    if sd <= 0.0:
        return [0.0 for _ in values]
    return [(v - mu) / sd for v in values]


def quantile(sorted_vals, p):
    """Empirical p-quantile (upper), sorted_vals ascending."""
    if not sorted_vals:
        return float("nan")
    idx = int(math.ceil(p * len(sorted_vals))) - 1
    idx = min(max(idx, 0), len(sorted_vals) - 1)
    return sorted_vals[idx]


def wilson_interval(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))
