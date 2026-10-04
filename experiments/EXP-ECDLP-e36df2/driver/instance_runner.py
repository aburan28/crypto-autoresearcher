"""Stage 2/3 per-curve driver for EXP-ECDLP-e36df2.

Processes all of a curve's tested primes TOGETHER (not independently),
because the cross-prime degeneracy screen (specification.yaml Stage 2)
needs x(mS) mod p_i / y(mS) mod p_i at the SAME m across every one of that
curve's primes simultaneously. [m]S mod p^K is computed via
frozen_ref.pmul (the same padic.pmul used by a26bde's instrument.py),
starting from the point reduced mod p^K ONCE per instance -- never via
exact-Fraction arithmetic in this stage, per specification.yaml's licensed
replacement (reduction mod p^K commutes with the group law).

Memory-bounding requirement (specification.yaml Stage 2 / handoff
constraint): NO full per-m table is retained. Only running aggregate
counts, the (rare, bounded) flagged-multiple census, and a chi-square
histogram of size p (NOT of size N_i) are kept per instance.
"""
from __future__ import annotations

import math
import time
from fractions import Fraction

from frozen_ref import (
    pmul, to_affine, reduce_point_mod, split_point, FormalGroup,
    _exponent,
)
import fastseries
import sections

DEFECT_MARGIN = 40
ESCALATION_MARGINS = (40, 60, 75)  # matches instrument.split_point's own
# margin-escalation pattern, reused here as required by specification.yaml
# Stage 2's on-curve sanity check against silent precision underflow.
WORKING_DEGREE = 80


def _on_curve_mod(x, y, A, B, mod):
    return (y * y - (x ** 3 + A * x + B)) % mod == 0


def _mS_affine_at_margin(S_exact, p, Kreq, margin, m, A):
    """Recompute [m]S mod p^(Kreq+margin) via pmul at a specific escalated
    margin, independent of any cached per-instance state -- used only on
    the rare on-curve-check failure path."""
    N = p ** (Kreq + margin)
    S_mod = reduce_point_mod(S_exact, N, p)
    if S_mod is None:
        return None
    S_proj = (S_mod[0] % N, S_mod[1] % N, 1)
    mS_proj = pmul(m, S_proj, A, N)
    return to_affine(mS_proj, N, p)


class PrimeState:
    __slots__ = (
        "p", "n", "N_i", "Kreq", "margin_big", "N_big", "t_S_big",
        "d_S", "v", "reduced_log", "S_proj_big",
        "u_x", "u_y", "u_rand",
        "n_agree_x", "n_excl_x", "n_total_x",
        "n_agree_y", "n_excl_y", "n_total_y",
        "n_agree_rand", "n_total_rand",
        "n_skipped", "n_precision_fail",
        "hist_x", "hist_y",
        "order", "trace",
    )


def _build_prime_state(A, B, x0, y0, S_exact, fg, p, n, order, trace,
                        seed, curve_idx, mu0_target=20):
    st = PrimeState()
    st.p, st.n, st.order, st.trace = p, n, order, trace
    st.N_i = math.ceil(mu0_target * p)

    lift_fn_S = lambda N: reduce_point_mod(S_exact, N, p)
    _, _, v = split_point(p, 2, lift_fn_S, n, fg)
    st.Kreq = v + 2
    st.margin_big = st.Kreq + DEFECT_MARGIN
    st.N_big = p ** st.margin_big
    t_S_big, d_S, v_check = split_point(p, st.margin_big, lift_fn_S, n, fg)
    assert v_check == v
    st.t_S_big, st.d_S, st.v = t_S_big, d_S, v

    fastseries.self_check_equivalence(fg.log, st.N_big, p)
    st.reduced_log = fastseries.reduce_series_once(fg.log, st.N_big, p)

    S_mod_big = reduce_point_mod(S_exact, st.N_big, p)
    st.S_proj_big = (S_mod_big[0] % st.N_big, S_mod_big[1] % st.N_big, 1)

    NK = p ** st.Kreq
    # m=1 baselines, computed ONCE, outside and never re-entering the main
    # loop (removes the m=1 tautology named in EV-ECDLP-95ec68 /
    # DEC-20260911-74c9dc; specification.yaml Stage 2).
    x0_true, y0_true = x0 % p, y0 % p
    t_S_proj_big = (t_S_big[0] % st.N_big, t_S_big[1] % st.N_big, 1)

    s_x_1 = sections.s_x_section(A, B, p, st.margin_big, x0_true, y0_true)
    s_y_1 = sections.s_y_section(A, B, p, st.margin_big, x0_true, y0_true)
    s_r_1 = sections.s_rand_section(A, B, p, st.margin_big, x0_true, y0_true,
                                     seed, curve_idx, 1)
    st.u_x = sections.digit_of_section_minus_torsion(
        s_x_1, p, t_S_proj_big, A, st.N_big, st.reduced_log)
    st.u_y = sections.digit_of_section_minus_torsion(
        s_y_1, p, t_S_proj_big, A, st.N_big, st.reduced_log)
    st.u_rand = sections.digit_of_section_minus_torsion(
        s_r_1, p, t_S_proj_big, A, st.N_big, st.reduced_log)

    st.n_agree_x = st.n_excl_x = st.n_total_x = 0
    st.n_agree_y = st.n_excl_y = st.n_total_y = 0
    st.n_agree_rand = st.n_total_rand = 0
    st.n_skipped = st.n_precision_fail = 0
    st.hist_x = [0] * p
    st.hist_y = [0] * p
    return st


def run_curve(curve_idx, A, B, x0, y0, primes, seed, mu0_target=20,
              progress_every=None):
    """primes: list of {"p","n","order","trace"} dicts for this curve.
    Returns (per_prime_results: list[dict], flagged_x: dict, flagged_y: dict)."""
    t_wall0 = time.time()
    t_cpu0 = time.process_time()

    S_exact = (Fraction(x0), Fraction(y0))
    fg = FormalGroup(A, B, D=WORKING_DEGREE)

    states = [
        _build_prime_state(A, B, x0, y0, S_exact, fg, pe["p"], pe["n"],
                            pe["order"], pe["trace"], seed, curve_idx,
                            mu0_target)
        for pe in primes
    ]
    max_m = max(st.N_i for st in states) + 1

    flagged_x: dict[int, dict] = {}
    flagged_y: dict[int, dict] = {}

    for m in range(2, max_m + 1):
        per_prime_xy = {}  # p -> (x_mod_p, y_mod_p) or None if skipped
        per_prime_mod = {}  # p -> (x_mod_K, y_mod_K, achieved_Nn) or None

        for st in states:
            try:
                mS_proj = pmul(m, st.S_proj_big, A, st.N_big)
                x_mod, y_mod, Nn = to_affine(mS_proj, st.N_big, st.p)
            except ValueError:
                # Z not a unit mod p after normalizing == the n | m skip
                # case (mirrors instrument.reduce_point_mod's "denominator
                # divisible by p" convention, restated for pmul's
                # projective path).
                st.n_skipped += 1
                per_prime_xy[st.p] = None
                per_prime_mod[st.p] = None
                continue

            # On-curve sanity check against silent precision underflow
            # (specification.yaml Stage 2), with instrument.split_point's
            # own margin-escalation pattern (40,60,75) on failure.
            NK = st.p ** st.Kreq
            if not _on_curve_mod(x_mod, y_mod, A, B, NK):
                escalated = None
                for margin in ESCALATION_MARGINS:
                    if margin <= st.margin_big - st.Kreq:
                        continue  # already at/above this margin and failed
                    try:
                        cand = _mS_affine_at_margin(S_exact, st.p, st.Kreq,
                                                     margin, m, A)
                    except ValueError:
                        cand = None
                    if cand is not None and _on_curve_mod(cand[0], cand[1], A, B, NK):
                        escalated = cand
                        break
                if escalated is None:
                    st.n_precision_fail += 1
                    per_prime_xy[st.p] = None
                    per_prime_mod[st.p] = None
                    continue
                x_mod, y_mod, Nn = escalated

            per_prime_xy[st.p] = (x_mod % st.p, y_mod % st.p)
            per_prime_mod[st.p] = (x_mod, y_mod, Nn)

        present_states = [st for st in states if per_prime_xy[st.p] is not None]
        x_flag = bool(present_states) and all(
            per_prime_xy[st.p][0] in (1, st.p - 1) for st in present_states)
        y_flag = bool(present_states) and all(
            per_prime_xy[st.p][1] in (1, st.p - 1) for st in present_states)
        if x_flag:
            flagged_x[m] = {st.p: per_prime_xy[st.p][0] for st in states
                             if per_prime_xy[st.p] is not None}
        if y_flag:
            flagged_y[m] = {st.p: per_prime_xy[st.p][1] for st in states
                             if per_prime_xy[st.p] is not None}

        for st in states:
            if m > st.N_i + 1:
                continue
            mod_data = per_prime_mod[st.p]
            if mod_data is None:
                continue  # already counted in n_skipped above
            x_mod, y_mod, Nn = mod_data
            m_mod_n = m % st.n
            t_mS_proj = pmul(m_mod_n, (st.t_S_big[0] % st.N_big,
                                        st.t_S_big[1] % st.N_big, 1),
                              A, st.N_big)

            x0_true, y0_true = x_mod % st.p, y_mod % st.p
            try:
                s_x_pt = sections.s_x_section(A, B, st.p, st.margin_big, x0_true, y0_true)
                s_y_pt = sections.s_y_section(A, B, st.p, st.margin_big, x0_true, y0_true)
                s_r_pt = sections.s_rand_section(A, B, st.p, st.margin_big, x0_true,
                                                  y0_true, seed, curve_idx, m)

                d_x = sections.digit_of_section_minus_torsion(
                    s_x_pt, st.p, t_mS_proj, A, st.N_big, st.reduced_log)
                d_y = sections.digit_of_section_minus_torsion(
                    s_y_pt, st.p, t_mS_proj, A, st.N_big, st.reduced_log)
                d_r = sections.digit_of_section_minus_torsion(
                    s_r_pt, st.p, t_mS_proj, A, st.N_big, st.reduced_log)
            except (ValueError, ZeroDivisionError):
                st.n_precision_fail += 1
                continue

            if not x_flag:
                st.n_total_x += 1
                st.hist_x[d_x] += 1
                if d_x == (m * st.u_x) % st.p:
                    st.n_agree_x += 1
            else:
                st.n_excl_x += 1

            if not y_flag:
                st.n_total_y += 1
                st.hist_y[d_y] += 1
                if d_y == (m * st.u_y) % st.p:
                    st.n_agree_y += 1
            else:
                st.n_excl_y += 1

            st.n_total_rand += 1
            if d_r == (m * st.u_rand) % st.p:
                st.n_agree_rand += 1

        if progress_every and m % progress_every == 0:
            print(f"  curve {curve_idx}: m={m}/{max_m} "
                  f"elapsed={time.time()-t_wall0:.1f}s", flush=True)

    wall = time.time() - t_wall0
    cpu = time.process_time() - t_cpu0

    results = []
    for st, pe in zip(states, primes):
        chi_x = _chi_square(st.hist_x, st.n_total_x, st.p)
        chi_y = _chi_square(st.hist_y, st.n_total_y, st.p)
        results.append({
            "curve_idx": curve_idx, "p": st.p, "A": A, "B": B, "x0": x0, "y0": y0,
            "n": st.n, "order": st.order, "trace": st.trace,
            "N_i": st.N_i, "Kreq": st.Kreq, "v": st.v, "d_S": st.d_S,
            "u_S_x": st.u_x, "u_S_y": st.u_y, "u_S_rand": st.u_rand,
            "n_skipped_n_divides_m": st.n_skipped,
            "n_precision_insufficient": st.n_precision_fail,
            "s_x": {"n_agree": st.n_agree_x, "n_total_after_exclusion": st.n_total_x,
                    "n_excluded_degenerate": st.n_excl_x,
                    "mu_0_i": (st.n_total_x / st.p) if st.p else None,
                    "chi_square": chi_x},
            "s_y": {"n_agree": st.n_agree_y, "n_total_after_exclusion": st.n_total_y,
                    "n_excluded_degenerate": st.n_excl_y,
                    "mu_0_i": (st.n_total_y / st.p) if st.p else None,
                    "chi_square": chi_y},
            "s_rand": {"n_agree": st.n_agree_rand, "n_total_after_exclusion": st.n_total_rand,
                       "mu_0_i": (st.n_total_rand / st.p) if st.p else None},
            "wall_seconds_curve_shared": wall,
            "cpu_seconds_curve_shared": cpu,
        })

    return results, flagged_x, flagged_y


def _chi_square(hist, n_total, p):
    if n_total <= 0:
        return {"statistic": None, "dof": p - 1, "note": "no data"}
    exp = n_total / p
    stat = sum((c - exp) ** 2 / exp for c in hist)
    return {"statistic": stat, "dof": p - 1, "expected_per_bin": exp}
