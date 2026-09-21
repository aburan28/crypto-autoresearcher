"""
Exact-integer convolution (PRIMARY metric) and FFT-based character-side
cross-check (SECONDARY, float, tolerance 1e-10 relative) over the group
E(F_p) presented as Z/n1 x Z/n2 via curve.build_coordinate_map.
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


def exact_stats(N_m_array, N, F, m):
    """Ordered-convention stats from an exact-integer N_m array over the whole group."""
    total = int(N_m_array.sum())
    mean = total / N
    var = float(np.mean((N_m_array.astype(np.float64) - mean) ** 2))
    # exact variance via integer sum of squares to avoid float cancellation:
    sumsq = int((N_m_array.astype(object) ** 2).sum())
    var_exact_num = sumsq * N - total * total  # = N^2 * Var * N ... see below
    # Var = E[X^2] - (E[X])^2 = sumsq/N - (total/N)^2 = (sumsq*N - total^2) / N^2
    var_exact = var_exact_num / (N * N)
    predicted_mean = (F ** m) / N
    max_rel_dev = float(np.max(np.abs(N_m_array.astype(np.float64) - predicted_mean)) / predicted_mean) if predicted_mean != 0 else None
    return {
        "sum_N_m": total,
        "mean_ordered": mean,
        "predicted_mean_ordered_Fm_over_N": predicted_mean,
        "var_ordered_exact": var_exact,
        "max_rel_dev_ordered": max_rel_dev,
    }


def character_spectrum(fb_coords, n1, n2):
    """FFT2 of the FB indicator over Z/n1 x Z/n2 gives Shat(chi) for every
    character simultaneously, chi indexed by (j1,j2). float64/complex128,
    SECONDARY cross-check only."""
    ind = indicator_grid(fb_coords, n1, n2).astype(np.complex128)
    Shat = np.fft.fft2(ind)
    return Shat


def var_from_character_side(Shat, N, m):
    """Var_R N_m(R) = (1/N^2) sum_{chi!=1} |Shat(chi)|^{2m}."""
    mag2 = (np.abs(Shat) ** 2)
    total_all = np.sum(mag2 ** m)
    trivial = mag2[0, 0] ** m  # chi = trivial character is at index (0,0)
    return float((total_all - trivial) / (N ** 2))


def max_C(Shat):
    """C = max_{chi != 1} |Shat(chi)|."""
    mag = np.abs(Shat).copy()
    mag[0, 0] = -1  # exclude trivial character
    idx = np.unravel_index(np.argmax(mag), mag.shape)
    return float(mag[idx]), idx
