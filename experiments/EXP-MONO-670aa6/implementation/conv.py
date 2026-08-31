"""
Exact-integer convolution (PRIMARY metric path) and FFT-based character-side
cross-check (SECONDARY, float, tolerance 1e-10 relative) over the group
E(F_p) presented as Z/n1 x Z/n2 via curve.build_coordinate_map.

Two computational routes to the SAME "convolution side" (exact-integer N_m
array) are provided:

  1. `convolution_tower` -- direct circular-roll summation (the literal
     algorithm EXP-MONO-c819ba used), O(F) numpy roll-adds per convolution
     step. Used for Stage 0's fixture identity gate and as an independent
     cross-check on a sample of primary-panel real-arm cells.

  2. `fft_exact_tower` -- computes the identical circular m-fold
     autoconvolution of the factor-base indicator via
     N_m = round(Re(ifft2(fft2(indicator)^m))), which is mathematically
     IDENTICAL to route 1 (both compute the group's m-fold circular
     autoconvolution of the same indicator function; route 2 merely uses
     the convolution theorem instead of direct summation). This is the
     route used for the 20,100 null/null-object draws in Stage 2/3, where
     route 1's O(F) per-step cost is not affordable at that draw count
     within the declared 7200s budget (see implementation.md). Both routes
     are exercised and cross-checked against each other on every primary
     real-arm cell (dual_path_control).
"""
import numpy as np


def indicator_grid(coord_list, n1, n2):
    """coord_list: iterable of (k1,k2) coordinates. Returns int64 array shape (n1,n2)."""
    grid = np.zeros((n1, n2), dtype=np.int64)
    for (a, b) in coord_list:
        grid[a, b] += 1
    return grid


def convolve_step(N_prev, fb_coords):
    """N_next[R] = sum_{P in FB} N_prev[R-P], via circular roll-sum. EXACT
    (int64 arithmetic, no floating point)."""
    out = np.zeros_like(N_prev)
    for (da, db) in fb_coords:
        out += np.roll(np.roll(N_prev, da, axis=0), db, axis=1)
    return out


def convolution_tower(fb_coords, n1, n2, max_m):
    """Returns dict m -> N_m array (int64), for m = 1..max_m, via iterated
    exact convolution starting from the FB indicator itself (N_1)."""
    ind = indicator_grid(fb_coords, n1, n2)
    tower = {1: ind}
    cur = ind
    for m in range(2, max_m + 1):
        cur = convolve_step(cur, fb_coords)
        tower[m] = cur
    return tower


def character_spectrum(fb_coords, n1, n2):
    """FFT2 of the FB indicator over Z/n1 x Z/n2 gives Shat(chi) for every
    character simultaneously, chi indexed by (j1,j2). float64/complex128."""
    ind = indicator_grid(fb_coords, n1, n2).astype(np.complex128)
    Shat = np.fft.fft2(ind)
    return Shat


def fft_exact_Nm(Shat, m, n1, n2):
    """Route 2's exact-integer N_m array: round(Re(ifft2(Shat^m))). Exact
    (to double-precision rounding, verified <1e-9 relative residual against
    route 1 on every real-arm cell -- see dual_path_control checks) because
    the entries of N_m are non-negative integers bounded well within
    double-precision's exact-integer range at this toy scale (N <= 2048,
    F <= N, so max N_m entry << 2^53)."""
    raw = np.fft.ifft2(Shat ** m)
    real = raw.real
    rounded = np.round(real)
    max_imag = float(np.max(np.abs(raw.imag)))
    max_round_err = float(np.max(np.abs(real - rounded)))
    return rounded.astype(np.int64), max_imag, max_round_err


def exact_stats(N_m_array, N, F, m):
    """Ordered-convention stats from an exact-integer N_m array over the whole group."""
    total = int(N_m_array.sum())
    mean = total / N
    sumsq = int((N_m_array.astype(object) ** 2).sum())
    var_exact_num = sumsq * N - total * total
    var_exact = var_exact_num / (N * N)
    predicted_mean = (F ** m) / N
    max_rel_dev = (float(np.max(np.abs(N_m_array.astype(np.float64) - predicted_mean)) / predicted_mean)
                   if predicted_mean != 0 else None)
    return {
        "sum_N_m": total,
        "mean_ordered": mean,
        "predicted_mean_ordered_Fm_over_N": predicted_mean,
        "var_ordered_exact": var_exact,
        "max_rel_dev_ordered": max_rel_dev,
    }


def var_from_character_side(Shat, N, m):
    """Var_R N_m(R) = (1/N^2) sum_{chi!=1} |Shat(chi)|^{2m}."""
    mag2 = (np.abs(Shat) ** 2)
    total_all = np.sum(mag2 ** m)
    trivial = mag2[0, 0] ** m
    return float((total_all - trivial) / (N ** 2))


def max_C(Shat):
    """C = max_{chi != 1} |Shat(chi)|."""
    mag = np.abs(Shat).copy()
    mag[0, 0] = -1
    idx = np.unravel_index(np.argmax(mag), mag.shape)
    return float(mag[idx]), idx


def cell_stats_fft(fb_coords, n1, n2, N, F, m_list=(1, 2, 3, 4)):
    """FFT/route-2 analogue of EXP-MONO-c819ba's roll-based `cell_stats`: ONE
    fft2 call yields Shat, from which every requested m's exact-integer N_m
    (route 2, rounded ifft2(Shat^m)), C, and C/F are all derived cheaply.
    Used for the legacy 8-curve sub-panel's F-ladder/m-ladder graded
    controls, where m up to 4 is needed per cell."""
    import math as _math
    Shat = character_spectrum(fb_coords, n1, n2)
    Cval, _ = max_C(Shat)
    per_m = {}
    for m in m_list:
        Nm_fft, max_imag, max_round_err = fft_exact_Nm(Shat, m, n1, n2)
        st = exact_stats(Nm_fft, N, F, m)
        var_char = var_from_character_side(Shat, N, m)
        rel_res = (abs(st["var_ordered_exact"] - var_char) / st["var_ordered_exact"]
                   if st["var_ordered_exact"] != 0 else 0.0)
        fact_m = _math.factorial(m)
        per_m[m] = {
            "var_ordered": st["var_ordered_exact"],
            "var_multiset": st["var_ordered_exact"] / (fact_m ** 2),
            "mean_ordered": st["mean_ordered"],
            "mean_multiset": st["mean_ordered"] / fact_m,
            "max_rel_dev": st["max_rel_dev_ordered"],
            "var_character_float": var_char,
            "l1_relative_residual": rel_res,
            "route2_max_imag_residual": max_imag,
            "route2_max_round_residual": max_round_err,
        }
    return {"F": F, "C": Cval, "C_over_F": Cval / F if F else None, "per_m": per_m, "Shat": Shat}


def stat_bundle_from_coords(fb_coords, n1, n2, N, F, m):
    """One fft2 call computes BOTH primary statistics (Var_m via exact-integer
    convolution side, and C/F via the same spectrum) for a single symmetric
    subset. Returns dict with var_exact (route 2, exact-integer), var_character
    (route-2-internal float cross-check), C, C_over_F, and route-2 diagnostics
    (max imaginary residual, max rounding residual) used to confirm the FFT
    route recovered an exact integer array."""
    Shat = character_spectrum(fb_coords, n1, n2)
    Nm_fft, max_imag, max_round_err = fft_exact_Nm(Shat, m, n1, n2)
    st = exact_stats(Nm_fft, N, F, m)
    var_char = var_from_character_side(Shat, N, m)
    Cval, _ = max_C(Shat)
    return {
        "var_exact": st["var_ordered_exact"],
        "var_character_float": var_char,
        "route2_var_relative_residual": (
            abs(st["var_ordered_exact"] - var_char) / st["var_ordered_exact"]
            if st["var_ordered_exact"] != 0 else 0.0),
        "C": Cval,
        "C_over_F": Cval / F if F else None,
        "route2_max_imag_residual": max_imag,
        "route2_max_round_residual": max_round_err,
        "Shat": Shat,
    }
