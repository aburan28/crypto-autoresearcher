"""OLS slope with a 95 percent t-interval. Own implementation (no scipy present).

t quantile obtained by bisecting the Student-t CDF written from the regularized
incomplete beta function of mpmath.  Self-checked against textbook values in
__main__.
"""
import mpmath as mp


def t_cdf(t, nu):
    t = mp.mpf(t)
    nu = mp.mpf(nu)
    x = nu / (nu + t * t)
    ib = mp.betainc(nu / 2, mp.mpf(0.5), 0, x, regularized=True)
    return 1 - ib / 2 if t > 0 else ib / 2


def t_quantile(q, nu):
    lo, hi = mp.mpf(0), mp.mpf(1)
    while t_cdf(hi, nu) < q:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, nu) < q:
            lo = mid
        else:
            hi = mid
    return float((lo + hi) / 2)


def ols(xs, ys, conf=0.95):
    n = len(xs)
    assert n == len(ys) and n >= 3
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    icpt = my - slope * mx
    resid = [y - (icpt + slope * x) for x, y in zip(xs, ys)]
    ssr = sum(r * r for r in resid)
    df = n - 2
    s2 = ssr / df
    se = (s2 / sxx) ** 0.5
    tq = t_quantile(1 - (1 - conf) / 2, df)
    return {
        "n": n, "slope": slope, "intercept": icpt, "df": df,
        "residual_variance": s2, "se_slope": se, "t_quantile": tq,
        "ci95": [slope - tq * se, slope + tq * se],
        "sxx": sxx, "ssr": ssr,
    }


def outcome_rule(ci):
    """Contract rule as stated in review_plan.blind_rederivation.quantity."""
    lo, hi = ci
    contains1 = lo <= 1 <= hi
    excl_half = not (lo <= 0.5 <= hi)
    contains0 = lo <= 0 <= hi
    excl_quarter = not (lo <= 0.25 <= hi)
    return {
        "contains_1": contains1, "excludes_0.5": excl_half,
        "contains_0": contains0, "excludes_0.25": excl_quarter,
        "excludes_0": not contains0,
        "outcome_I_interval_clause": contains1 and excl_half,
        "outcome_III_interval_clause": contains0 and excl_quarter,
    }


if __name__ == "__main__":
    for nu, want in ((2, 4.302653), (10, 2.228139), (46, 2.012896), (478, 1.964997)):
        got = t_quantile(0.975, nu)
        print(f"t_.975,{nu} = {got:.6f}  (textbook {want})  delta={abs(got-want):.2e}")
    # reproduce the producer-reported shape on the full-cell design (4 values, 120x each)
    xs = [s for s in (2, 3, 4, 5) for _ in range(120)]
    ys = [v for v in (5, 5, 6, 6) for _ in range(120)]
    print("n=480 replicated step:", ols(xs, ys))
