"""G3 ceiling predicate for EXP-ECDLP-56117b.

Authored from the frozen formal statement in
``experiments/EXP-ECDLP-56117b/specification.yaml`` (``g3_predicate``),
which copies ``experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml``
Section 3. This module does not read, import, copy, or sys.path-insert
any path in ``independence.forbidden_paths``.

Reading P2: a uniformly random function on Z_N together with an
independent Bernoulli(theta) DP marking. Selection uses only
``w(d) = S_d + 4*W*h_d`` with a seeded ascending tie-break. Exact basin
sizes are used to SCORE a selection, never to MAKE it. The basin array
is not allocated until after STATIC(T)_r (and NULL_A, when requested)
have been chosen.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Frozen parameters from specification.yaml g3_predicate.exact_parameter_table
# N = 2^24, T = 256, T_sel = 128. W is real-valued, not rounded. Use the
# table; do not recompute T.
# ---------------------------------------------------------------------------

N_FROZEN = 16777216
T_FROZEN = 256
T_SEL_FROZEN = 128

# Experiment-local salt so this family's streams are not an accidental
# copy of any other experiment's seed schedule. Not a map family.
EXPERIMENT_SALT = 0x56117B

# Sentinels used by the basin resolver (must match the C source).
_UNVIS = -1
_INSTK = -2
_UNREACH = -3
_CAPPED = -4

FROZEN_A_PARAMS: dict[float, dict[str, float | int]] = {
    0.0625: {"W": 64.0, "theta": 0.015625000, "cap": 512},
    0.125: {"W": 90.509668, "theta": 0.011048544, "cap": 725},
    0.25: {"W": 128.0, "theta": 0.007812500, "cap": 1024},
}


def frozen_params(a: float) -> dict[str, float | int]:
    if a not in FROZEN_A_PARAMS:
        raise ValueError(f"a={a} is not in the frozen table {{1/16, 1/8, 1/4}}")
    return dict(FROZEN_A_PARAMS[a])


# ===========================================================================
# PRNG streams (specification.yaml g3_predicate.what_this_section_does_not_specify)
#
# (i) pool-start PRNG: numpy PCG64, SeedSequence([SALT, 3, s]), starts drawn
#     as uint32 in [0, N), consumed sequentially, prefetched in batches of
#     65536 (prefetch does not change the stream order).
# (ii) tie-break key stream: numpy PCG64, SeedSequence([SALT, 400 + s]),
#     one uint64 key per pool DP, ASCENDING on ties of w(d).
# (iii) map f and DP marking D: independent PCG64 streams
#     SeedSequence([SALT, 1, s]) for f (uniform on Z_N per domain point)
#     and SeedSequence([SALT, 2, s]) for D (independent Bernoulli(theta)).
# NULL_A permutation: SeedSequence([SALT, 300 + s]), as the contract names.
# ===========================================================================

POOL_START_BATCH = 65536


def _pcg64(*keys: int) -> np.random.Generator:
    ss = np.random.SeedSequence(list(int(k) for k in keys))
    return np.random.Generator(np.random.PCG64(ss))


def stream_ids(seed: int) -> dict[str, Any]:
    s = int(seed)
    return {
        "map_f": {"kind": "numpy.PCG64", "seedsequence": [EXPERIMENT_SALT, 1, s]},
        "dp_mark": {"kind": "numpy.PCG64", "seedsequence": [EXPERIMENT_SALT, 2, s]},
        "pool_starts": {
            "kind": "numpy.PCG64",
            "seedsequence": [EXPERIMENT_SALT, 3, s],
            "batch": POOL_START_BATCH,
        },
        "tie_break": {
            "kind": "numpy.PCG64",
            "seedsequence": [EXPERIMENT_SALT, 400 + s],
            "note": "declared stream seeded 400+s; uint64 keys; ASCENDING on w-ties",
        },
        "null_a": {
            "kind": "numpy.PCG64",
            "seedsequence": [EXPERIMENT_SALT, 300 + s],
            "note": "permutation of the pool's own (S,h) multiset",
        },
        "experiment_salt": EXPERIMENT_SALT,
    }


def generate_instance(
    N: int, theta: float, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    """Uniform random function f: Z_N -> Z_N and independent Bernoulli(theta) D."""
    rng_f = _pcg64(EXPERIMENT_SALT, 1, int(seed))
    rng_d = _pcg64(EXPERIMENT_SALT, 2, int(seed))
    f = rng_f.integers(0, N, size=N, dtype=np.uint32)
    is_dp = (rng_d.random(N) < float(theta)).astype(np.uint8)
    return f, is_dp


# ===========================================================================
# Exact-basin resolver (C). Fallback: numpy layer-pull + leftover classify.
# ===========================================================================

_C_SOURCE = r"""
#include <stdint.h>
#include <stdlib.h>

enum { UNVIS = -1, INSTK = -2, UNREACH = -3, CAPPED = -4 };

int resolve_basins(const uint32_t *f, const uint8_t *is_dp,
                   int32_t n, int32_t cap,
                   int32_t *first_dp, int32_t *dist)
{
    int32_t *path;
    int32_t start, x, plen, i, j, d, dlen, st;

    if (n <= 0) return 0;
    path = (int32_t *)malloc((size_t)n * sizeof(int32_t));
    if (!path) return -1;

    for (i = 0; i < n; i++) {
        if (is_dp[i]) {
            first_dp[i] = i;
            dist[i] = 0;
        } else {
            first_dp[i] = UNVIS;
            dist[i] = -1;
        }
    }

    for (start = 0; start < n; start++) {
        if (first_dp[start] != UNVIS) continue;
        plen = 0;
        x = start;
        for (;;) {
            st = first_dp[x];
            if (st == INSTK) break;
            if (st != UNVIS) break;
            first_dp[x] = INSTK;
            path[plen++] = x;
            x = (int32_t)f[x];
        }
        if (first_dp[x] >= 0) {
            d = first_dp[x];
            dlen = dist[x];
            for (i = plen - 1; i >= 0; i--) {
                dlen++;
                if (dlen > cap) {
                    for (j = i; j >= 0; j--) {
                        first_dp[path[j]] = CAPPED;
                        dist[path[j]] = dlen;
                        dlen++;
                    }
                    break;
                }
                first_dp[path[i]] = d;
                dist[path[i]] = dlen;
            }
        } else if (first_dp[x] == CAPPED) {
            dlen = dist[x];
            for (i = plen - 1; i >= 0; i--) {
                dlen++;
                first_dp[path[i]] = CAPPED;
                dist[path[i]] = dlen;
            }
        } else {
            /* UNREACH or INSTK (DP-free cycle): whole path unreachable. */
            for (i = 0; i < plen; i++) {
                first_dp[path[i]] = UNREACH;
                dist[path[i]] = -1;
            }
        }
    }
    free(path);
    return 0;
}

void accumulate_basins(const int32_t *first_dp, const int32_t *dist,
                       int32_t n, int32_t cap, int32_t *basin)
{
    int32_t i, d;
    for (i = 0; i < n; i++) {
        d = first_dp[i];
        if (d >= 0 && dist[i] >= 0 && dist[i] <= cap)
            basin[d] += 1;
    }
}
"""

_LIB = None


def _compile_lib() -> Any | None:
    digest = hashlib.sha256(_C_SOURCE.encode("utf-8")).hexdigest()[:16]
    so_path = Path(tempfile.gettempdir()) / f"g3_56117b_basins_{digest}.so"
    if not so_path.exists():
        c_path = Path(tempfile.gettempdir()) / f"g3_56117b_basins_{digest}.c"
        c_path.write_text(_C_SOURCE)
        try:
            subprocess.check_call(
                [
                    "gcc",
                    "-O3",
                    "-shared",
                    "-fPIC",
                    "-std=c11",
                    "-o",
                    str(so_path),
                    str(c_path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            return None
    lib = ctypes.CDLL(str(so_path))
    lib.resolve_basins.argtypes = [
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_int32),
    ]
    lib.resolve_basins.restype = ctypes.c_int32
    lib.accumulate_basins.argtypes = [
        ctypes.POINTER(ctypes.c_int32),
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_int32,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_int32),
    ]
    lib.accumulate_basins.restype = None
    return lib


def _get_lib() -> Any | None:
    global _LIB
    if _LIB is False:
        return None
    if _LIB is None:
        loaded = _compile_lib()
        _LIB = loaded if loaded is not None else False
    return _LIB if _LIB is not False else None


def _resolve_basins_numpy(
    f: np.ndarray, is_dp: np.ndarray, cap: int
) -> tuple[np.ndarray, np.ndarray]:
    """Layer-pull assignment up to cap, then classify leftovers.

    Correct, slower fallback if gcc is unavailable. Not used for selection.
    """
    n = int(f.shape[0])
    f64 = f.astype(np.intp, copy=False)
    first = np.full(n, _UNVIS, dtype=np.int32)
    dist = np.full(n, -1, dtype=np.int32)
    dp_idx = np.flatnonzero(is_dp)
    first[dp_idx] = dp_idx.astype(np.int32)
    dist[dp_idx] = 0
    for k in range(1, int(cap) + 1):
        succ_first = first[f64]
        succ_dist = dist[f64]
        mask = (first == _UNVIS) & (succ_first >= 0) & (succ_dist == k - 1)
        if not bool(mask.any()):
            break
        first[mask] = succ_first[mask]
        dist[mask] = np.int32(k)
    leftover = np.flatnonzero(first == _UNVIS)
    color = np.zeros(n, dtype=np.int8)  # 0 unknown, 1 stack, 2 unreach, 3 capped
    for start in leftover.tolist():
        if first[start] != _UNVIS:
            continue
        path: list[int] = []
        x = int(start)
        while True:
            if color[x] == 1:
                for y in path:
                    first[y] = _UNREACH
                    dist[y] = -1
                    color[y] = 2
                break
            if first[x] >= 0 or first[x] == _CAPPED or color[x] == 3:
                dlen = int(dist[x]) if first[x] >= 0 or first[x] == _CAPPED else 0
                tag = _CAPPED
                for y in reversed(path):
                    dlen += 1
                    first[y] = tag
                    dist[y] = dlen
                    color[y] = 3
                break
            if first[x] == _UNREACH or color[x] == 2:
                for y in path:
                    first[y] = _UNREACH
                    dist[y] = -1
                    color[y] = 2
                break
            color[x] = 1
            path.append(x)
            x = int(f64[x])
    return first, dist


def exact_basins(
    f: np.ndarray, is_dp: np.ndarray, cap: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    """Exact basin(d) for every DP d, plus cycle/capped mass fractions.

    basin(d) = #{ x : first_dp(x) = d AND dist(x) <= cap }.
    Points on a DP-free cycle are UNREACHABLE; points with dist > cap are CAPPED.
    """
    n = int(f.shape[0])
    f = np.ascontiguousarray(f, dtype=np.uint32)
    is_dp = np.ascontiguousarray(is_dp, dtype=np.uint8)
    first = np.empty(n, dtype=np.int32)
    dist = np.empty(n, dtype=np.int32)
    lib = _get_lib()
    used_c = False
    if lib is not None:
        rc = lib.resolve_basins(
            f.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
            is_dp.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            ctypes.c_int32(n),
            ctypes.c_int32(int(cap)),
            first.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            dist.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        )
        if rc == 0:
            used_c = True
    if not used_c:
        first, dist = _resolve_basins_numpy(f, is_dp, cap)
    basin = np.zeros(n, dtype=np.int32)
    if used_c and lib is not None:
        lib.accumulate_basins(
            first.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            dist.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            ctypes.c_int32(n),
            ctypes.c_int32(int(cap)),
            basin.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        )
    else:
        ok = (first >= 0) & (dist >= 0) & (dist <= int(cap))
        np.add.at(basin, first[ok], 1)
    n_f = float(n)
    mass = {
        "cycle_mass_frac": float(np.count_nonzero(first == _UNREACH)) / n_f,
        "capped_mass_frac": float(np.count_nonzero(first == _CAPPED)) / n_f,
        "assigned_mass_frac": float(np.count_nonzero((first >= 0) & (dist <= int(cap)) & (dist >= 0)))
        / n_f,
        "resolver": "c" if used_c else "numpy_fallback",
    }
    return basin, first, dist, mass


# ===========================================================================
# Precomputation pool (Bernstein-Lange procedure as the contract froze it)
# ===========================================================================

@dataclass
class Pool:
    dps: np.ndarray  # int32, length r*T
    S: np.ndarray  # float64 summed generating-walk lengths
    h: np.ndarray  # float64 hit counts
    tie_keys: np.ndarray  # uint64
    generating_walks: int
    capped_walks: int
    P: int  # group operations charged
    target_distinct: int


def build_pool(
    f: np.ndarray,
    is_dp: np.ndarray,
    N: int,
    cap: int,
    r: int,
    T: int,
    seed: int,
) -> Pool:
    """Walk independent uniform starts until the pool holds exactly r*T distinct DPs.

    A capped walk is a MISS: charged `cap` steps, contributes nothing.
    A walk that hits DP d with length L credits (S_d += L, h_d += 1).
    L = 0 if the start is itself a DP.
    """
    target = int(r) * int(T)
    rng = _pcg64(EXPERIMENT_SALT, 3, int(seed))
    tie_rng = _pcg64(EXPERIMENT_SALT, 400 + int(seed))
    S_map: dict[int, int] = {}
    h_map: dict[int, int] = {}
    walks = 0
    capped = 0
    P = 0
    batch = np.empty(0, dtype=np.uint32)
    bpos = 0

    def next_start() -> int:
        nonlocal batch, bpos
        if bpos >= batch.size:
            batch = rng.integers(0, N, size=POOL_START_BATCH, dtype=np.uint32)
            bpos = 0
        x = int(batch[bpos])
        bpos += 1
        return x

    f_u = f
    dp = is_dp
    cap_i = int(cap)
    while len(S_map) < target:
        x = next_start()
        walks += 1
        if dp[x]:
            S_map[x] = S_map.get(x, 0) + 0
            h_map[x] = h_map.get(x, 0) + 1
            continue
        L = 0
        hit = False
        while L < cap_i:
            x = int(f_u[x])
            L += 1
            P += 1
            if dp[x]:
                S_map[x] = S_map.get(x, 0) + L
                h_map[x] = h_map.get(x, 0) + 1
                hit = True
                break
        if not hit:
            capped += 1
            # the loop already charged `cap` steps into P
    dps = np.fromiter(S_map.keys(), dtype=np.int32, count=len(S_map))
    S = np.array([S_map[int(d)] for d in dps], dtype=np.float64)
    h = np.array([h_map[int(d)] for d in dps], dtype=np.float64)
    tie_keys = tie_rng.integers(0, np.iinfo(np.uint64).max, size=dps.size, dtype=np.uint64)
    return Pool(
        dps=dps,
        S=S,
        h=h,
        tie_keys=tie_keys,
        generating_walks=walks,
        capped_walks=capped,
        P=P,
        target_distinct=target,
    )


# ===========================================================================
# Selection: w(d) = S_d + 4*W*h_d. NO basin array is a parameter.
# ===========================================================================

def compute_weight(S: np.ndarray, h: np.ndarray, W: float) -> np.ndarray:
    """w(d) = S_d + 4 * W * h_d. Pool evidence only."""
    return np.asarray(S, dtype=np.float64) + (4.0 * float(W)) * np.asarray(h, dtype=np.float64)


def select_static_by_weight(
    dps: np.ndarray,
    S: np.ndarray,
    h: np.ndarray,
    W: float,
    T: int,
    tie_keys: np.ndarray,
) -> np.ndarray:
    """Return the T pool DPs of largest w(d); ties broken by tie_keys ASCENDING.

    This function's signature has no basin argument. Passing a basin size
    array is a TypeError. Selecting by true basin size is a named invalidation.
    """
    if dps.size < int(T):
        raise RuntimeError(f"pool has {dps.size} DPs, need T={T}")
    w = compute_weight(S, h, W)
    # lexsort: last key is primary. Primary = -w (so w descending),
    # secondary = tie_keys ascending.
    order = np.lexsort((tie_keys, -w))
    return np.asarray(dps, dtype=np.int32)[order[: int(T)]]


def select_null_a(
    pool: Pool,
    W: float,
    T: int,
    seed: int,
) -> np.ndarray:
    """Relabel the pool's own (S,h) multiset, then the same weight and tie-break.

    Tie-break keys stay with the DP identity. Only evidence pairs are permuted,
    from the stream seeded 300 + s.
    """
    rng = _pcg64(EXPERIMENT_SALT, 300 + int(seed))
    perm = rng.permutation(pool.dps.size)
    S_n = pool.S[perm]
    h_n = pool.h[perm]
    return select_static_by_weight(pool.dps, S_n, h_n, W, T, pool.tie_keys)


# ===========================================================================
# Scoring (exact basin sizes). Used AFTER selection.
# ===========================================================================

def top_share(basin: np.ndarray, is_dp: np.ndarray, t: int, N: int) -> tuple[float, int]:
    """TopShare(t) = (sum of the t largest basin(d) over all DPs d) / N."""
    sizes = basin[is_dp.astype(bool)]
    if sizes.size == 0:
        return 0.0, 0
    t_use = min(int(t), int(sizes.size))
    if t_use == sizes.size:
        total = int(sizes.sum())
    else:
        # largest t_use; np.partition is linear
        part = np.partition(sizes, sizes.size - t_use)
        total = int(part[sizes.size - t_use :].sum())
    return total / float(N), total


def static_coverage(basin: np.ndarray, selected: np.ndarray, N: int) -> tuple[float, int]:
    total = int(basin[np.asarray(selected, dtype=np.int32)].sum())
    return total / float(N), total


def basin_histogram(basin: np.ndarray, is_dp: np.ndarray) -> dict[str, Any]:
    sizes = basin[is_dp.astype(bool)]
    if sizes.size == 0:
        return {"n_dps": 0, "pairs": []}
    uniq, cnt = np.unique(sizes, return_counts=True)
    pairs = [[int(u), int(c)] for u, c in zip(uniq.tolist(), cnt.tolist())]
    return {"n_dps": int(sizes.size), "pairs": pairs}


@dataclass
class CellResult:
    payload: dict[str, Any]
    basin: np.ndarray | None
    is_dp: np.ndarray | None
    histogram: dict[str, Any]
    mass: dict[str, float]


def run_cell(
    *,
    N: int,
    T: int,
    T_sel: int,
    a: float,
    r: int,
    seed: int,
    compute_null_a: bool,
) -> CellResult:
    """One (N, a, r, seed) G3 measurement. Selection happens before basins exist."""
    params = frozen_params(a)
    W = float(params["W"])
    theta = float(params["theta"])
    cap = int(params["cap"])

    f, is_dp = generate_instance(N, theta, seed)
    pool = build_pool(f, is_dp, N, cap, r, T, seed)

    # --- selection path: pool evidence only; basin array does not exist ---
    selected = select_static_by_weight(pool.dps, pool.S, pool.h, W, T, pool.tie_keys)
    selected_null = (
        select_null_a(pool, W, T, seed) if compute_null_a else None
    )
    # --- end selection path ---

    basin, first, dist, mass = exact_basins(f, is_dp, cap)
    del f, first, dist

    ts_sel, ts_sel_count = top_share(basin, is_dp, T_sel, N)
    ts_T, ts_T_count = top_share(basin, is_dp, T, N)
    sc, sc_count = static_coverage(basin, selected, N)
    margin = ts_sel - sc

    exceedance = sc_count > ts_T_count
    payload: dict[str, Any] = {
        "N": int(N),
        "T": int(T),
        "T_sel": int(T_sel),
        "a": float(a),
        "r": int(r),
        "seed": int(seed),
        "modeled": {"W": W, "theta": theta, "cap": cap},
        "n_dps": int(np.count_nonzero(is_dp)),
        "pool": {
            "n_distinct": int(pool.dps.size),
            "target_distinct": int(pool.target_distinct),
            "generating_walks": int(pool.generating_walks),
            "capped_walks": int(pool.capped_walks),
            "capped_walk_fraction": (
                float(pool.capped_walks) / float(pool.generating_walks)
                if pool.generating_walks
                else 0.0
            ),
            "P": int(pool.P),
            "P_over_sqrt_NT": float(pool.P) / float(np.sqrt(float(N) * float(T))),
        },
        "top_share_Tsel": ts_sel,
        "top_share_Tsel_count": ts_sel_count,
        "top_share_T": ts_T,
        "top_share_T_count": ts_T_count,
        "static_cov": sc,
        "static_cov_count": sc_count,
        "margin": margin,
        "g3_s": bool(margin >= 0.0),
        "exact_coverage_exceedance": bool(exceedance),
        "mass": mass,
        "streams": stream_ids(seed),
        "selected_dps": [int(x) for x in selected.tolist()],
        "weight_formula": "w(d) = S_d + 4*W*h_d",
        "selection_used_basin_sizes": False,
    }
    if selected_null is not None:
        scn, scn_count = static_coverage(basin, selected_null, N)
        margin_null = ts_sel - scn
        payload["static_cov_null"] = scn
        payload["static_cov_null_count"] = scn_count
        payload["margin_null"] = margin_null
        payload["null_exceedance"] = bool(scn_count > ts_T_count)
        payload["margin_over_margin_null"] = (
            float(margin / margin_null) if margin_null != 0.0 else None
        )
        payload["selected_dps_null"] = [int(x) for x in selected_null.tolist()]
        if scn_count > ts_T_count:
            payload["exact_coverage_exceedance"] = True

    hist = basin_histogram(basin, is_dp)
    hist["cycle_mass_frac"] = mass["cycle_mass_frac"]
    hist["capped_mass_frac"] = mass["capped_mass_frac"]
    hist["assigned_mass_frac"] = mass["assigned_mass_frac"]
    return CellResult(payload=payload, basin=basin, is_dp=is_dp, histogram=hist, mass=mass)
