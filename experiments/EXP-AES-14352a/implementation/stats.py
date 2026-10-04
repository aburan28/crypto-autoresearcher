"""Pre-registered Stage-1 statistics for EXP-AES-14352a (observations only)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


def wilson_ci(successes: int, n: int, z: float = 1.96) -> Tuple[Optional[float], Optional[float]]:
    if n <= 0:
        return None, None
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half) / denom, (centre + half) / denom


def binomial_sf_one_sided(k: int, n: int, p0: float) -> float:
    """P(X >= k) under Binomial(n, p0). Exact sum for small n."""
    if n <= 0:
        return 1.0
    p0 = min(max(p0, 0.0), 1.0)
    # Use survival function via cumulative
    # For numerical stability with small n (N=16 keys * pairs aggregated),
    # use log-space recursive computation.
    if p0 == 0.0:
        return 1.0 if k <= 0 else 0.0
    if p0 == 1.0:
        return 1.0 if k <= n else 0.0

    # Compute P(X=i) recursively
    # P(0) = (1-p)^n
    probs = [0.0] * (n + 1)
    probs[0] = (1.0 - p0) ** n
    for i in range(0, n):
        if probs[i] == 0.0:
            # restart from ratio when underflowed
            pass
        probs[i + 1] = probs[i] * (n - i) * p0 / ((i + 1) * (1.0 - p0)) if p0 < 1 else 0.0
    # renormalize if needed
    s = sum(probs)
    if s > 0:
        probs = [x / s for x in probs]
    return float(sum(probs[k:]))


def fisher_exact_greater(a: int, b: int, c: int, d: int) -> float:
    """One-sided Fisher exact P(odds ratio >= observed) for 2x2 [[a,b],[c,d]].

    Rows: AES / control; cols: accept / reject.
    a=aes_accept, b=aes_reject, c=ctrl_accept, d=ctrl_reject.
    """
    # Enumerate tables with same margins where aes_accept >= a
    row1 = a + b
    row2 = c + d
    col1 = a + c
    n = row1 + row2
    if n == 0:
        return 1.0

    def comb(n_: int, k_: int) -> float:
        if k_ < 0 or k_ > n_:
            return 0.0
        return float(math.comb(n_, k_))

    # Hypergeometric: P(X=k) = C(col1,k)*C(n-col1,row1-k)/C(n,row1)
    denom = comb(n, row1)
    if denom == 0:
        return 1.0
    p = 0.0
    lo = max(0, row1 - (n - col1))
    hi = min(row1, col1)
    for k in range(a, hi + 1):
        p += comb(col1, k) * comb(n - col1, row1 - k) / denom
    return float(min(1.0, max(0.0, p)))


def fpr_bits(rate: Optional[float], *, trials: Optional[int] = None) -> Optional[float]:
    if rate is None:
        return None
    if rate <= 0:
        # No observed false positives: report lower bound -log2(1/trials) if known.
        if trials is not None and trials > 0:
            return float(math.log2(trials))  # conservative lower bound on FPR bits
        return None
    if rate >= 1.0:
        return 0.0
    return float(-math.log2(rate))


def safe_rate(successes: int, trials: int) -> Optional[float]:
    if trials <= 0:
        return None
    return successes / trials


def safe_ratio(num: Optional[float], den: Optional[float]) -> Optional[float]:
    if num is None or den is None or den == 0:
        return None
    return num / den


def odds(successes: int, trials: int) -> Optional[float]:
    if trials <= 0:
        return None
    fails = trials - successes
    if fails == 0:
        return None  # infinite; caller handles
    return successes / fails


def odds_ratio(aes_s: int, aes_n: int, ctrl_s: int, ctrl_n: int) -> Optional[float]:
    o1 = odds(aes_s, aes_n)
    o0 = odds(ctrl_s, ctrl_n)
    if o1 is None or o0 is None or o0 == 0:
        return None
    return o1 / o0


def aggregate_primary_stats(
    *,
    aes_joint: int,
    aes_prd: int,
    aes_trials: int,
    ctrl_joint: int,
    ctrl_prd: int,
    ctrl_trials: int,
    ctrl_ffp: Optional[int] = None,
    graded_joint_by_r: Optional[Dict[int, Tuple[int, int]]] = None,
    sibling_joint: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Compute Stage-1 primary statistics. Observations only — no claim verdict."""

    rate_aes_joint = safe_rate(aes_joint, aes_trials)
    rate_ctrl_joint = safe_rate(ctrl_joint, ctrl_trials)
    rate_aes_prd = safe_rate(aes_prd, aes_trials)
    rate_ctrl_prd = safe_rate(ctrl_prd, ctrl_trials)

    gap = None
    if rate_aes_joint is not None and rate_ctrl_joint is not None:
        gap = rate_aes_joint - rate_ctrl_joint

    # Pre-registered: one-sided test AES joint rate > control.
    # Model: treat per-trial Bernoulli; null p = control MLE; Fisher exact on counts.
    p_fisher = fisher_exact_greater(
        aes_joint,
        aes_trials - aes_joint,
        ctrl_joint,
        ctrl_trials - ctrl_joint,
    )
    # Also binomial SF treating control rate as p0
    p0 = rate_ctrl_joint if rate_ctrl_joint is not None else 0.0
    p_binom = binomial_sf_one_sided(aes_joint, aes_trials, p0)

    ablation_ratio_control = safe_ratio(rate_ctrl_joint, rate_ctrl_prd)
    ablation_ratio_aes = safe_ratio(rate_aes_joint, rate_aes_prd)

    # HEUR-FP1: control joint vs product rate(P_RD)*rate(F_fp)
    heur_fp1: Dict[str, Any] = {"status": "incomplete"}
    if ctrl_ffp is not None and ctrl_trials > 0:
        rate_ffp = safe_rate(ctrl_ffp, ctrl_trials)
        product = None
        if rate_ctrl_prd is not None and rate_ffp is not None:
            product = rate_ctrl_prd * rate_ffp
        rel_err = None
        status = "ok"
        band_pass: Optional[bool] = None
        if product is None or rate_ctrl_joint is None:
            status = "incomplete"
        elif product == 0.0 and rate_ctrl_joint == 0.0:
            # Zero-event degenerate: joint == product == 0; not a >3× disagreement.
            status = "degenerate_zero_events"
            band_pass = True
            rel_err = 0.0
        elif product == 0.0 and rate_ctrl_joint > 0.0:
            status = "product_zero_joint_positive"
            band_pass = False
        elif product > 0:
            rel_err = abs(rate_ctrl_joint - product) / product
            band_pass = rel_err <= 3.0
        heur_fp1 = {
            "rate_prd_control": rate_ctrl_prd,
            "rate_ffp_control": rate_ffp,
            "product": product,
            "rate_joint_control": rate_ctrl_joint,
            "relative_error": rel_err,
            "band": "rel_err <= 3 (or both-zero degenerate)",
            "status": status,
            "pass": band_pass,
            "note": "HEUR-FP1 multiplicative check on control; observation only.",
        }

    # HEUR-FP2: odds-ratio AES vs control for association of F_fp with P_RD
    # Approximate via joint/prd conditional: among P_RD accepts, fraction with F_fp
    # = joint/prd when defined.
    heur_fp2: Dict[str, Any] = {"status": "incomplete"}
    or_aes = safe_ratio(rate_aes_joint, rate_aes_prd)  # conditional friend rate proxy
    or_ctrl = safe_ratio(rate_ctrl_joint, rate_ctrl_prd)
    # Use odds of joint among trials as secondary
    odds_r = odds_ratio(aes_joint, aes_trials, ctrl_joint, ctrl_trials)
    hf2_pass: Optional[bool]
    if or_aes is None or or_ctrl is None:
        hf2_pass = None  # degenerate / undefined conditional rates
    else:
        hf2_pass = or_aes > or_ctrl
    heur_fp2 = {
        "conditional_friend_rate_aes": or_aes,
        "conditional_friend_rate_control": or_ctrl,
        "odds_ratio_aes_vs_control_joint": odds_r,
        "pass_prediction_aes_gt_control": hf2_pass,
        "note": "HEUR-FP2: predicted stronger association on AES than control.",
    }

    graded = {}
    if graded_joint_by_r:
        for r, (s, n) in sorted(graded_joint_by_r.items()):
            graded[str(r)] = {
                "joint_accepts": s,
                "trials": n,
                "rate": safe_rate(s, n),
            }
        rates = [
            graded[str(r)]["rate"]
            for r in sorted(graded_joint_by_r)
            if graded[str(r)]["rate"] is not None
        ]
        non_decay = False
        if len(rates) >= 2:
            # Artifact tell: excess must not increase with r
            for i in range(1, len(rates)):
                if rates[i] is not None and rates[i - 1] is not None:
                    if rates[i] > rates[i - 1] + 1e-12:
                        non_decay = True
        graded["non_decay_artifact_tell"] = non_decay

    sibling = None
    if sibling_joint is not None:
        s, n = sibling_joint
        sibling = {
            "joint_accepts": s,
            "trials": n,
            "rate": safe_rate(s, n),
            "note": "Misaligned IDj=+1 mod 4; predicted null excess.",
        }

    ci_aes = wilson_ci(aes_joint, aes_trials)
    ci_ctrl = wilson_ci(ctrl_joint, ctrl_trials)

    return {
        "accept_rate_aes_r5_joint": {
            "accepts": aes_joint,
            "trials": aes_trials,
            "rate": rate_aes_joint,
            "wilson_ci_95": {"low": ci_aes[0], "high": ci_aes[1]},
        },
        "accept_rate_control_r10_joint": {
            "accepts": ctrl_joint,
            "trials": ctrl_trials,
            "rate": rate_ctrl_joint,
            "wilson_ci_95": {"low": ci_ctrl[0], "high": ci_ctrl[1]},
        },
        "accept_rate_aes_r5_prd": {
            "accepts": aes_prd,
            "trials": aes_trials,
            "rate": rate_aes_prd,
        },
        "accept_rate_control_r10_prd": {
            "accepts": ctrl_prd,
            "trials": ctrl_trials,
            "rate": rate_ctrl_prd,
        },
        "aes_minus_control_gap": gap,
        "one_sided_p_fisher_exact": p_fisher,
        "one_sided_p_binomial_sf_control_mle": p_binom,
        "control_fpr_joint_bits": fpr_bits(rate_ctrl_joint, trials=ctrl_trials),
        "control_fpr_prd_bits": fpr_bits(rate_ctrl_prd, trials=ctrl_trials),
        "control_fpr_bits_note": (
            "If accept count is 0, bits field is a lower bound log2(N_trials), "
            "not an extrapolated FPR."
        ),
        "ablation_ratio_control": ablation_ratio_control,
        "ablation_ratio_aes": ablation_ratio_aes,
        "preferential_suppression_ablation_control_lt_aes": (
            ablation_ratio_control is not None
            and ablation_ratio_aes is not None
            and ablation_ratio_control < ablation_ratio_aes
        ),
        "heur_fp1_product_check": heur_fp1,
        "heur_fp2_odds_ratio": heur_fp2,
        "graded_spot": graded,
        "sibling_misaligned": sibling,
        "preregistered_thresholds": {
            "primary_p": 0.01,
            "heur_fp1_rel_err_band": 3.0,
        },
        "measured_not_modelled": True,
        "published_acc_acp_margins_claimed": False,
    }
