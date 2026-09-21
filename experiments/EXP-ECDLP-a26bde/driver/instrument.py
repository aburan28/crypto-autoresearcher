"""High-level p-adic instrument built on padic.py + formalgroup.py:
reduction of Fraction points mod p^K, evaluation of formal-group series
p-adically, the unique homomorphic torsion section, the formal-group digit,
and the non-canonical Hensel-lift affine section used as the non-homomorphic
contrast (self-check 2 / Stage 3).

PRECISION_MARGIN: the division-free projective formulas can produce a
representative (X:Y:Z) carrying a REDUNDANT common factor of p (this shows
up exactly at the one step that subtracts a near-infinity point, P - Y,
where the addition formula's denominator-clearing factor H can pick up
positive valuation even though the resulting point is generic and away
from infinity). padic.normalize_proj divides this out, which is a valid
projective rescaling but costs working precision. All internal computation
here therefore runs at K + PRECISION_MARGIN digits and every chart
conversion asserts the achieved precision after normalization is still
>= the caller's requested K before truncating the final answer down to
exactly p^K. This is recorded, not silently absorbed: `AnomalousBreak`
aside, a `RuntimeError` here means the margin needs to be raised for that
instance, and callers can inspect it.
"""
from __future__ import annotations

from fractions import Fraction

from padic import (
    O_PROJ, is_identity, pneg, padd, pdbl, pmul, to_tw, from_tw, to_affine,
)

PRECISION_MARGIN = 40  # see padic.WORKING_DEGREE's comment and
# derivation_note.md BUG-EXP-a26bde-002: raised from an initial 24 (paired
# with WORKING_DEGREE=15) after empirical testing showed 24 digits of margin
# were NOT always enough to survive the precision consumed by the chart
# conversions in split_point below (measured consumption in the toy
# instances tested here: well under 20 digits per instance; 40 leaves a
# comfortable, explicitly checked safety factor -- see the round-trip
# assertion in split_point, which raises rather than silently returning a
# wrong digit if the margin is ever insufficient for a given instance).


class AnomalousBreak(ValueError):
    """Raised exactly at the pow(n, -1, p^K) step when p | n (the anomalous
    curve's argument-breaking point, per the contract's step 6)."""


def _exponent(N: int, p: int) -> int:
    k = 0
    while N % p == 0:
        N //= p
        k += 1
    if N != 1:
        raise ValueError(f"_exponent: {N} (after removing p-factors) != 1; "
                          "not a pure power of p")
    return k


def reduce_fraction_mod(fr, N: int, p: int) -> int:
    """Reduce a Fraction to an integer mod N=p^K. Raises if the denominator
    is divisible by p (not invertible mod N)."""
    fr = Fraction(fr)
    num, den = fr.numerator, fr.denominator
    if den % p == 0:
        raise ValueError(f"reduce_fraction_mod: denominator {den} divisible "
                          f"by p={p}, not invertible mod {N}")
    inv = pow(den % N, -1, N)
    return (num * inv) % N


def reduce_point_mod(pt, N: int, p: int):
    """Reduce an exact-rational affine point (Fraction, Fraction) to
    (x, y) mod N. Returns None (meaning: this is a skip case, n | m) if
    either coordinate's denominator is divisible by p."""
    x, y = pt
    try:
        xm = reduce_fraction_mod(x, N, p)
        ym = reduce_fraction_mod(y, N, p)
    except ValueError:
        return None
    return (xm, ym)


def eval_series_mod(series, t0: int, N: int, p: int) -> int:
    """Evaluate a Fraction power series at an integer t0 mod N, Horner-style.
    Each coefficient's denominator is asserted coprime to p (per the task:
    "assert rather than assume")."""
    result = 0
    for c in reversed(series):
        cm = reduce_fraction_mod(c, N, p)  # raises if a coeff denom hits p
        result = (result * t0 + cm) % N
    return result


def valuation_modp(x: int, p: int, K: int) -> int:
    """p-adic valuation of an integer x given mod p^K (capped at K)."""
    x %= p ** K
    if x == 0:
        return K
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def curve_lift_projective(pt_mod, N: int) -> tuple:
    """Embed a point ALREADY KNOWN CORRECTLY mod N (i.e. genuinely on the
    curve mod N -- e.g. the output of reduce_point_mod on an exact global
    rational point, or the output of hensel_lift_point below) into
    projective (X:Y:1) form. This is NOT a lifting step: passing a point
    that is only known mod p (or mod some smaller p^k < N) and expecting
    this to correctly extend it to mod N is the bug this module had before
    (BUG-EXP-a26bde-001, see derivation_note.md): (x, y) with x, y < p
    happens to satisfy y^2 = x^3+a x+b only mod p, not mod p^K for K > 1
    (the residual y0^2-x0^3-a x0-b is a nonzero integer divisible by p but
    generally not by p^2), so naively embedding it and treating the result
    as valid mod p^K silently computes with an off-curve point. Any caller
    that only has a point mod p must call hensel_lift_point first."""
    x, y = pt_mod
    return (x % N, y % N, 1)


def hensel_lift_point(fg, p: int, N: int, x0: int, y0: int) -> tuple[int, int]:
    """Genuinely lift a point (x0, y0) known mod p (y0 != 0 mod p) to a
    point (x, y) mod N = p^K satisfying y^2 = x^3 + a x + b mod N exactly,
    by fixing x = x0 (the 'naive curve lift, applied to x only') and
    Hensel-lifting y via Newton iteration (hensel_lift_sqrt). This is the
    lift_point(E, R, k) deliverable of IDEA-20260905-dacf4f part (B); used
    whenever the input point is only known mod p (self-checks, anomalous
    recovery on synthetic points), never for a point already reduced from
    a known exact global rational point (which is already valid mod N via
    reduce_point_mod and should go through curve_lift_projective directly)."""
    a, b = fg.a, fg.b
    x0 = x0 % p
    y0 = y0 % p
    if y0 == 0:
        raise ValueError("hensel_lift_point: y0 == 0 mod p, cannot Hensel-lift "
                          "(2-torsion-adjacent point; Newton step needs 2y0 a unit)")
    K = _exponent(N, p)
    rhs_mod = (x0 ** 3 + a * x0 + b) % N
    y = hensel_lift_sqrt(y0, rhs_mod, p, K)
    return (x0 % N, y % N)


class PrecisionInsufficient(RuntimeError):
    """Raised when PRECISION_MARGIN (or WORKING_DEGREE) was not enough for a
    specific instance; a caller may retry with a larger margin. Never
    silently absorbed -- see BUG-EXP-a26bde-002 in derivation_note.md, where
    the earlier version of this module returned a WRONG digit rather than
    raising because its round-trip identity was never checked."""


def split_point(p: int, K: int, lift_fn, n: int, fg,
                 margins: tuple[int, ...] = (40, 60, 75)
                 ) -> tuple[tuple[int, int], int, int]:
    """split_point with AUTOMATIC MARGIN ESCALATION: some instances consume
    more of the working margin than others (measured: most instances are
    fine at margin=40, a minority need ~60 -- see derivation_note.md
    BUG-EXP-a26bde-003), so this retries `_split_point_at_margin` at each
    margin in `margins` (default capped at 75, comfortably under
    padic.WORKING_DEGREE=80's log/exp truncation floor -- going past that
    floor would stop being a margin problem and become silent truncation
    error, which the round-trip check inside `_split_point_at_margin` is
    NOT designed to rule out) until one succeeds, re-lifting the point at
    the correspondingly larger precision each time via `lift_fn`, a
    callable `N -> (x, y) mod N` that produces a point genuinely on the
    curve mod N (e.g. `lambda N: hensel_lift_point(fg, p, N, x0, y0)`, or a
    closure around reduce_point_mod for an exact global rational point).
    Propagates the final PrecisionInsufficient if every margin in `margins`
    fails."""
    last_exc = None
    for m in margins:
        N = p ** (K + m)
        P_full = lift_fn(N)
        try:
            return _split_point_at_margin(p, K, P_full, n, fg, margin=m)
        except AnomalousBreak:
            raise  # never retry past a genuine mathematical refusal
        except PrecisionInsufficient as e:
            last_exc = e
            continue
    raise last_exc


def _split_point_at_margin(p: int, K: int, P_full: tuple[int, int], n: int, fg,
                            margin: int) -> tuple[tuple[int, int], int, int]:
    """Single-pass computation of BOTH the torsion-section lift t(P) mod p^K
    and the formal-group digit d(P) = (psi(X_S)/p^v) mod p of X_S = P - t(P),
    for P a point reducing into <S> (n = the order of P mod p, coprime to p),
    at a FIXED margin (see split_point above for the escalating wrapper most
    callers should use). P_full MUST already be a point genuinely on the
    curve mod p^(K+margin) (from hensel_lift_point for a synthetic mod-p
    point, or reduce_point_mod for an exact global rational point evaluated
    at that same precision; passing a point only known to a smaller
    precision and letting this function's internal `% N` silently extend it
    is exactly BUG-EXP-a26bde-001, see derivation_note.md).

    Raises AnomalousBreak exactly at the division by n when p | n (the
    anomalous curve's argument-breaking point). Raises PrecisionInsufficient
    if the achieved precision falls short of K, OR if the round-trip check
    t(P) + X_S == P fails mod p^K (the module's own independent check that
    the subtraction that produced t(P) and the digit's own log-of-X_S came
    from mutually consistent data; this is what would have caught
    BUG-EXP-a26bde-002 immediately instead of silently returning a wrong
    on-curve-inconsistent point)."""
    a = fg.a
    Kw = K + margin
    N = p ** Kw
    Pproj = curve_lift_projective(P_full, N)

    # Step 1: [n]P via the (validated, division-free) projective ladder.
    nP = pmul(n, Pproj, a, N)
    if is_identity(nP):
        t0, N0 = 0, N
    else:
        t0, w0, N0 = to_tw(nP, N, p)  # requires Y unit mod p (checked inside)
    K0 = _exponent(N0, p)
    if K0 < K:
        raise PrecisionInsufficient(
            f"split_point: precision margin exhausted converting [n]P to "
            f"(t,w) (K0={K0} < requested K={K}); raise PRECISION_MARGIN")

    # Step 2: log(t0) mod N0 = psi([n]P).
    ell0 = eval_series_mod(fg.log, t0, N0, p)

    # Step 3: divide by n -- psi(X_S) = psi([n]P) / n. THIS is the
    # anomalous break point (division by n inside E_1 fails iff p | n).
    try:
        n_inv = pow(n % N0, -1, N0)
    except ValueError as e:
        import math
        raise AnomalousBreak(
            f"pow(n={n}, -1, N={N0}) failed: gcd(n, p)={math.gcd(n, p)} "
            f"!= 1 -- the torsion section does not exist (p | n)") from e
    ell1 = (ell0 * n_inv) % N0  # = psi(X_S) mod N0

    v = valuation_modp(ell1, p, K0)
    if v >= K0:
        raise ValueError("split_point: log(X_S) has valuation >= achieved "
                          "precision; increase K for this instance")
    if K0 - v < 1:
        raise PrecisionInsufficient(
            f"split_point: precision after removing v={v} digits (K0={K0}) "
            "is insufficient to read the digit; raise PRECISION_MARGIN")
    d = ((ell1 % (p ** K0)) // (p ** v)) % p

    # Step 4: X_S itself, in (t,w) chart form -- exp(psi(X_S)), then t(P) = P - X_S.
    t1 = eval_series_mod(fg.exp, ell1, N0, p)
    w1 = eval_series_mod(fg.w, t1, N0, p)
    X_S_proj = from_tw(t1, w1)
    neg_X_S = pneg(X_S_proj, N0)

    Pproj_N0 = (Pproj[0] % N0, Pproj[1] % N0, Pproj[2] % N0)
    tP_proj = padd(Pproj_N0, neg_X_S, a, N0)
    tP_x, tP_y, N1 = to_affine(tP_proj, N0, p)
    K1 = _exponent(N1, p)
    if K1 < K:
        raise PrecisionInsufficient(
            f"split_point: precision margin exhausted forming t(P) = P - X_S "
            f"(K1={K1} < requested K={K}); raise PRECISION_MARGIN")
    NK = p ** K
    t_affine = (tP_x % NK, tP_y % NK)

    # Independent round-trip check: t(P) + X_S must reproduce P. Done at the
    # SAME full precision N0 that produced tP_proj and X_S_proj (truncating
    # either operand down to p^K before adding would itself destroy X_S's
    # near-identity structure -- an earlier version of this check did
    # exactly that and reported a false failure; see derivation_note.md).
    # Compare projectively (cross-multiplication) rather than converting to
    # affine, so the identity case (n | m style coincidences) compares
    # cleanly too.
    recon = padd(tP_proj, X_S_proj, a, N0)
    if is_identity(recon) != is_identity(Pproj_N0):
        raise PrecisionInsufficient(
            "split_point: round-trip check t(P)+X_S == P failed (identity "
            "mismatch) -- raise PRECISION_MARGIN or WORKING_DEGREE")
    if not is_identity(recon):
        Xr, Yr, Zr = recon
        Xo, Yo, Zo = Pproj_N0
        cross_x = (Xr * Zo - Xo * Zr) % N0
        cross_y = (Yr * Zo - Yo * Zr) % N0
        vK = p ** K
        if cross_x % vK != 0 or cross_y % vK != 0:
            raise PrecisionInsufficient(
                "split_point: round-trip check t(P)+X_S == P failed mod "
                f"p^{K} -- raise PRECISION_MARGIN or WORKING_DEGREE "
                f"(cross_x val={valuation_modp(cross_x, p, K0)}, "
                f"cross_y val={valuation_modp(cross_y, p, K0)})")

    return t_affine, d, v


def torsion_section(n: int, p: int, K: int, lift_fn, fg) -> tuple[int, int]:
    """t(P) mod p^K only (see split_point for the combined computation)."""
    t_affine, _d, _v = split_point(p, K, lift_fn, n, fg)
    return t_affine


def digit(n: int, p: int, K: int, lift_fn, fg) -> tuple[int, int]:
    """(d, v) for X_S = P - t(P) mod p^K (see split_point)."""
    _t, d, v = split_point(p, K, lift_fn, n, fg)
    return d, v


# ---------------------------------------------------------------------------
# Non-canonical affine section s(R) := (x0 mod p^K, Hensel sqrt of RHS).
# Used as self-check 2's deliberately non-homomorphic section, and reused
# (per the contract's own procedure text) as "the Teichmuller section" of
# Stage 3's contrast arm -- see the derivation note for that naming note.
# ---------------------------------------------------------------------------

def hensel_lift_sqrt(y0: int, rhs_mod: int, p: int, K: int) -> int:
    """Given y0 with y0^2 == rhs_mod (mod p) and y0 != 0 mod p, Hensel-lift
    to y with y^2 == rhs_mod (mod p^K) by Newton iteration, doubling
    precision each step."""
    N = p ** K
    y = y0 % p
    prec = 1
    cur_mod = p
    while prec < K:
        prec = min(2 * prec, K)
        cur_mod = p ** prec
        # Newton step: y_{k+1} = y_k - (y_k^2 - rhs)/(2 y_k) mod cur_mod
        inv2y = pow((2 * y) % cur_mod, -1, cur_mod)
        y = (y - (y * y - rhs_mod) * inv2y) % cur_mod
    return y % N


def non_canonical_section(a: int, b: int, p: int, K: int, x0_true: int, y0_true: int):
    """s(R) := (x0 mod p^K, Hensel sqrt of RHS at x0 mod p^K), lifted from
    the known mod-p square root y0_true (so the branch matches R, not -R).
    NOTE: this is a fixed-x/Hensel-y section, NOT the Teichmuller section
    (see teichmuller_section below) -- kept as a second, independent
    non-canonical section for self-check (2)'s defect non-additivity test,
    where any non-homomorphic section will do."""
    N = p ** K
    x0 = x0_true % N
    rhs_mod = (x0 * x0 * x0 + a * x0 + b) % N
    y = hensel_lift_sqrt(y0_true % p, rhs_mod, p, K)
    return (x0, y)


def teichmuller_lift_scalar(a0: int, p: int, K: int) -> int:
    """The Teichmuller lift of a0 != 0 mod p to Z/p^K: the unique (p-1)-th
    root of unity congruent to a0 mod p, i.e. the root of f(x) = x^(p-1) - 1
    with f'(x) = (p-1) x^(p-2) a unit at a0 (true whenever a0 != 0 mod p),
    found by Newton iteration doubling precision each step. This is the
    x^p == x(1 + p q_p(x)) mod p^2 congruence's fixed point at q_p(x) == 0
    made precise to full precision K (see derivation_note.md Stage 0)."""
    if a0 % p == 0:
        raise ValueError("teichmuller_lift_scalar: a0 == 0 mod p has no "
                          "(p-1)-th root of unity lift")
    x = a0 % p
    prec = 1
    while prec < K:
        prec = min(2 * prec, K)
        cur_mod = p ** prec
        fx = (pow(x, p - 1, cur_mod) - 1) % cur_mod
        fpx = ((p - 1) * pow(x, p - 2, cur_mod)) % cur_mod
        fpx_inv = pow(fpx, -1, cur_mod)
        x = (x - fx * fpx_inv) % cur_mod
    return x % (p ** K)


def teichmuller_section(a: int, b: int, p: int, K: int, x0_true: int, y0_true: int):
    """The canonical Teichmuller section s(R) = (omega(x0), y), where
    omega(x0) is the Teichmuller lift of R's x-coordinate and y is the
    Hensel-lifted square root of the curve equation at omega(x0), branch
    fixed by y0_true mod p. This is the non-homomorphic contrast section of
    IDEA-20260905-848b77 part (E)(i) / this contract's Stage 3: since
    omega respects F_p^*'s multiplicative structure, not the elliptic
    addition law, s is not expected to be a group-law section, and its
    digit delta_1(s(m S)) is not expected to equal m * delta_1(s(S)) except
    by chance (rate ~ 1/p)."""
    N = p ** K
    x0 = x0_true % p
    if x0 == 0:
        # 0 is its own Teichmuller lift (0^(p-1) is not 1, but 0 is the
        # unique lift of 0 under Frobenius: 0^p = 0). Handle directly.
        x_t = 0
    else:
        x_t = teichmuller_lift_scalar(x0, p, K)
    rhs_mod = (x_t ** 3 + a * x_t + b) % N
    y = hensel_lift_sqrt(y0_true % p, rhs_mod, p, K)
    return (x_t % N, y)


# ---------------------------------------------------------------------------
# Anomalous discrete-log recovery (Smart / Satoh-Araki / Semaev), self-check
# (5) of IDEA-20260905-dacf4f and the "anomalous break" arm of the contract.
# ---------------------------------------------------------------------------

def anomalous_log(fg, p: int, P_mod: tuple[int, int], Q_mod: tuple[int, int],
                   margin: int = PRECISION_MARGIN) -> int:
    """Recover m with Q = [m] P on an anomalous curve (#E(F_p) == p), via the
    p-adic lift: Hensel-lift P, Q to precision p^2 (with margin headroom),
    compute [p]P~, [p]Q~ (both land in E_1, generic since P has order p),
    read psi of each in the (t,w) chart, and m = psi([p]Q~) / psi([p]P~) mod
    p (both have the same valuation v_p, generically 1; division is exact
    since psi is Z_p-linear on E_1: psi([p]Q~) = psi([p*m*P~ + correction])
    -- more precisely psi([p]([m]P)~) = m * psi([p]P~) to the precision this
    computes at, this is the defining Smart/Satoh-Araki/Semaev identity).
    Caller must independently verify [m]P == Q with a solver-independent
    verifier (harness/toycurve.py) before treating m as certified; this
    function returns the candidate only."""
    a = fg.a
    K = 2
    Kw = K + margin
    N = p ** Kw
    Pfull = hensel_lift_point(fg, p, N, P_mod[0], P_mod[1])
    Qfull = hensel_lift_point(fg, p, N, Q_mod[0], Q_mod[1])
    Pproj = curve_lift_projective(Pfull, N)
    Qproj = curve_lift_projective(Qfull, N)

    pP = pmul(p, Pproj, a, N)
    pQ = pmul(p, Qproj, a, N)
    if is_identity(pP):
        raise ValueError("anomalous_log: [p]P is exactly the identity to "
                          "the working precision; increase margin")
    tP, wP, NP = to_tw(pP, N, p)
    tQ, wQ, NQ = to_tw(pQ, N, p)
    KP = _exponent(NP, p)
    KQ = _exponent(NQ, p)
    ellP = eval_series_mod(fg.log, tP, NP, p)
    ellQ = eval_series_mod(fg.log, tQ, NQ, p)
    vP = valuation_modp(ellP, p, KP)
    vQ = valuation_modp(ellQ, p, KQ)
    if vP != vQ:
        raise ValueError(f"anomalous_log: valuation mismatch v(psi([p]P))="
                          f"{vP} != v(psi([p]Q))={vQ}; increase margin or "
                          "this instance is degenerate")
    if vP >= min(KP, KQ):
        raise ValueError("anomalous_log: valuation >= achieved precision; "
                          "increase margin")
    dP = ((ellP % (p ** KP)) // (p ** vP)) % p
    dQ = ((ellQ % (p ** KQ)) // (p ** vQ)) % p
    if dP % p == 0:
        raise ValueError("anomalous_log: psi([p]P)'s unit digit is 0 mod p "
                          "(should not happen for a generator); defect")
    m = (dQ * pow(dP, -1, p)) % p
    return m
