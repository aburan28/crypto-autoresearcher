"""EXP-ECDLP-869870 v2 fixture instrument (PA-ECDLP-869870-v1-to-v2).

Copy-adapted from experiments/EXP-ECDLP-869870/source/instrument.py.
v1 source/ is never edited. Two mixers, two walk projections:

- splitmix64: v1 mix64 / mix64_int; walk = TOP log2N bits (v1 step_fn);
  keys = v1 walk_keys (GOLDEN). Label walk_projection: top_bits.
- murmur3_fmix64: exact fmix64 from TASK-20260906-7ec3ea j2_rederive.py;
  walk = mix(x XOR K) mod N (LOW log2N bits); keys = sha256 key() with
  recorded v2 strings, NOT validator-7ec3ea|... . Label walk_projection: mod_N.

Basin / first-DP / selection functions are the v1 code path.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
C1 = np.uint64(0xbf58476d1ce4e5b9)
C2 = np.uint64(0x94d049bb133111eb)
GOLDEN = 0x9E3779B97F4A7C15
FMIX_C1 = np.uint64(0xff51afd7ed558ccd)
FMIX_C2 = np.uint64(0xc4ceb9fe1a85ec53)

RULES = ("published_weight", "count_only", "unselected", "generated_oracle", "global_oracle")
MIXERS = ("splitmix64", "murmur3_fmix64")

# Recorded v2 key-string scheme (re-keyed cell; not the validator's strings).
KEY_STRING_WALK = "ecdlp-869870-v2|{mixer}|walk|{seed}"
KEY_STRING_DP = "ecdlp-869870-v2|{mixer}|dp|{seed}"


def mix64(z: np.ndarray) -> np.ndarray:
    """splitmix64 finalizer on uint64 arrays (v1 mix64)."""
    z = z.astype(np.uint64, copy=True)
    z ^= z >> np.uint64(30)
    z *= C1
    z ^= z >> np.uint64(27)
    z *= C2
    z ^= z >> np.uint64(31)
    return z


def mix64_int(x: int) -> int:
    x &= 0xFFFFFFFFFFFFFFFF
    x ^= x >> 30
    x = (x * 0xbf58476d1ce4e5b9) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 27
    x = (x * 0x94d049bb133111eb) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 31
    return x


def fmix64(h: np.ndarray) -> np.ndarray:
    """MurmurHash3 64-bit fmix64; exact match of j2_rederive.py fmix64."""
    h = h.astype(np.uint64, copy=True)
    h ^= h >> np.uint64(33)
    h *= FMIX_C1
    h ^= h >> np.uint64(33)
    h *= FMIX_C2
    h ^= h >> np.uint64(33)
    return h


def fmix64_int(x: int) -> int:
    x &= 0xFFFFFFFFFFFFFFFF
    x ^= x >> 33
    x = (x * 0xff51afd7ed558ccd) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 33
    x = (x * 0xc4ceb9fe1a85ec53) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 33
    return x


def mixer_fn(name: str):
    if name == "splitmix64":
        return mix64
    if name == "murmur3_fmix64":
        return fmix64
    raise ValueError(name)


def sha256_key(s: str) -> int:
    """j2_rederive.py key(): first 8 bytes of sha256(s) as big-endian uint64."""
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def walk_keys(seed: int) -> tuple[int, int]:
    """v1 GOLDEN schedule. Used for the splitmix64 arm only."""
    K = mix64_int((seed * GOLDEN + 0x1) & 0xFFFFFFFFFFFFFFFF)
    K2 = mix64_int((seed * GOLDEN + 0x2) & 0xFFFFFFFFFFFFFFFF) ^ 0xA5A5A5A5A5A5A5A5
    return K, K2


def v2_key_strings(mixer: str, seed: int) -> dict:
    walk_s = KEY_STRING_WALK.format(mixer=mixer, seed=seed)
    dp_s = KEY_STRING_DP.format(mixer=mixer, seed=seed)
    return {
        "walk_key_string": walk_s,
        "dp_key_string": dp_s,
        "K": sha256_key(walk_s),
        "K2": sha256_key(dp_s),
        "scheme": "sha256_first8_be_uint64",
        "note": "re-keyed v2 strings; not validator-7ec3ea|...",
    }


def keys_for(mixer: str, seed: int) -> dict:
    """Return K, K2 and the recorded derivation for one (mixer, seed)."""
    if mixer == "splitmix64":
        K, K2 = walk_keys(seed)
        return {
            "mixer": mixer,
            "seed": seed,
            "K": K,
            "K2": K2,
            "walk_key_string": None,
            "dp_key_string": None,
            "key_derivation": "v1_walk_keys_GOLDEN",
            "walk_projection": "top_bits",
        }
    if mixer == "murmur3_fmix64":
        rec = v2_key_strings(mixer, seed)
        return {
            "mixer": mixer,
            "seed": seed,
            "K": rec["K"],
            "K2": rec["K2"],
            "walk_key_string": rec["walk_key_string"],
            "dp_key_string": rec["dp_key_string"],
            "key_derivation": rec["scheme"],
            "walk_projection": "mod_N",
        }
    raise ValueError(mixer)


def cell_params(log2N: int, T: int, a: float, N: int | None = None) -> dict:
    N = (1 << log2N) if N is None else int(N)
    W = math.sqrt(a * N / T)
    theta = 1.0 / W
    dp_threshold = int(math.floor(2.0 ** 64 / W))
    cap8 = int(round(8 * W))
    cap20 = int(round(20 * W))
    return {"log2N": log2N, "N": N, "T": T, "a": a, "W": W, "theta": theta,
            "dp_threshold": dp_threshold, "dp_density_exact": dp_threshold / 2.0 ** 64,
            "cap8": cap8, "cap20": cap20, "bits_per_entry": 2 * log2N}


def step_fn_top(x: np.ndarray, K: int, log2N: int, mix) -> np.ndarray:
    """f(x) = top log2N bits of mix(x XOR K). v1 walk projection."""
    z = mix(x.astype(np.uint64) ^ np.uint64(K))
    return (z >> np.uint64(64 - log2N)).astype(np.int64)


def step_fn_mod(x: np.ndarray, K: int, log2N: int, mix) -> np.ndarray:
    """f(x) = mix(x XOR K) mod N = low log2N bits. Validator J2 projection."""
    z = mix(x.astype(np.uint64) ^ np.uint64(K))
    mask = np.uint64((1 << log2N) - 1)
    return (z & mask).astype(np.int64)


def step_fn(x: np.ndarray, K: int, log2N: int, mixer: str = "splitmix64") -> np.ndarray:
    mix = mixer_fn(mixer)
    if mixer == "splitmix64":
        return step_fn_top(x, K, log2N, mix)
    if mixer == "murmur3_fmix64":
        return step_fn_mod(x, K, log2N, mix)
    raise ValueError(mixer)


def is_dp_fn(x: np.ndarray, K2: int, threshold: int, mixer: str = "splitmix64") -> np.ndarray:
    z = mixer_fn(mixer)(x.astype(np.uint64) ^ np.uint64(K2))
    return z < np.uint64(threshold)


def build_map(N: int, log2N: int, K: int, K2: int, threshold: int, mixer: str,
              chunk: int = 1 << 21):
    f = np.empty(N, dtype=np.int32)
    isdp = np.empty(N, dtype=bool)
    for lo in range(0, N, chunk):
        hi = min(N, lo + chunk)
        x = np.arange(lo, hi, dtype=np.int64)
        f[lo:hi] = step_fn(x, K, log2N, mixer)
        isdp[lo:hi] = is_dp_fn(x, K2, threshold, mixer)
    return f, isdp


def exact_first_dp(f: np.ndarray, isdp: np.ndarray, N: int):
    """Pointer jumping with DPs as absorbing fixed points (v1)."""
    idx = np.arange(N, dtype=np.int32)
    p = np.where(isdp, idx, f).astype(np.int32)
    d = np.where(isdp, 0, 1).astype(np.int32)
    rounds = 0
    k = 1
    while True:
        dp_ = d[p]
        d = d + dp_
        p = p[p]
        rounds += 1
        k *= 2
        del dp_
        if k > N:
            break
        if rounds >= 8 and bool(np.all(isdp[p] | (d > N))):
            break
    reach = isdp[p]
    return p, d, reach, rounds


def basin_sizes_at_cap(p, d, reach, isdp, N, cap):
    ok = reach & (d <= cap)
    bs = np.bincount(p[ok], minlength=N).astype(np.int64)
    capped_mass = int(np.count_nonzero(reach & (d > cap)))
    cycle_mass = int(np.count_nonzero(~reach))
    return bs, ok, capped_mass, cycle_mass


def compressed_hist(values: np.ndarray) -> dict:
    v = np.asarray(values)
    v = v[v > 0]
    u, c = np.unique(v, return_counts=True)
    top = np.sort(v)[::-1][:1000]
    return {"sizes": u.tolist(), "counts": c.tolist(), "top1000": top.tolist(),
            "n_basins": int(v.size), "total_mass": int(v.sum())}


def table_hash(dps: np.ndarray) -> str:
    s = np.sort(np.asarray(dps, dtype=np.int64))
    return hashlib.sha256(s.tobytes()).hexdigest()


def select_top(stat: np.ndarray, perm: np.ndarray, T: int) -> np.ndarray:
    order = np.lexsort((perm, stat))[::-1]
    return order[:T]


def select_rule(rule: str, pool: dict, T: int, perm: np.ndarray, W: float,
                bs_cap: np.ndarray, all_dps_sizes=None, all_dps_perm=None, all_dps=None):
    if rule == "published_weight":
        stat = pool["S"].astype(np.float64) + 4.0 * W * pool["h"].astype(np.float64)
    elif rule == "count_only":
        stat = pool["h"].astype(np.float64)
    elif rule == "unselected":
        stat = np.zeros(pool["dps"].size, dtype=np.float64)
    elif rule == "generated_oracle":
        stat = bs_cap[pool["dps"]].astype(np.float64)
    elif rule == "global_oracle":
        idx = select_top(all_dps_sizes.astype(np.float64), all_dps_perm, T)
        return all_dps[idx]
    else:
        raise ValueError(rule)
    idx = select_top(stat, perm, T)
    return pool["dps"][idx]


def exact_coverage(table: np.ndarray, bs: np.ndarray, N: int) -> float:
    return float(bs[table].sum()) / N


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float, float]:
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    ph = k / n
    den = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / den
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return ph, centre - half, centre + half


def online_eval(table: np.ndarray, term_dp: np.ndarray, term_ok: np.ndarray, lengths: np.ndarray,
                N: int, T: int, isdp_table_mask: np.ndarray) -> dict:
    M = term_dp.size
    hit = term_ok & isdp_table_mask[term_dp]
    hits = int(hit.sum())
    total_steps = int(lengths.sum())
    ph, lo, hi = wilson(hits, M)
    scaled = (total_steps / hits / math.sqrt(N / T)) if hits else float("inf")
    return {"M": M, "hits": hits, "c_hat": ph, "wilson_lo": lo, "wilson_hi": hi,
            "total_steps": total_steps, "scaled_cost_sampled": scaled}


def o_theta_correction_status() -> dict:
    """Attempt to instantiate the O(theta) correction from v1 (B4) + model.py.

    model.py states P/sqrt(NT) = sqrt(a) r (1 + r a / 2) with no O(theta)
    term. The v1 (B4) note says the closed forms hide O(theta) corrections
    and that N/T = 1 cells carry the largest duplicate-discard residual.
    No coefficient or subtractable form is present. Corrected residual is
    therefore not_evaluated (never a silent skip dressed as a pass).
    """
    return {
        "status": "not_evaluated",
        "reason": (
            "v1 specification (B4) note and source/model.py state the closed "
            "form P/sqrt(NT) = sqrt(a)*r*(1 + r*a/2) and that closed forms "
            "hide O(theta) corrections; they do not give a subtractable "
            "O(theta) term for published-weight scaled cost. Gate on "
            "corrected residual is not_evaluated. Raw residual is reported."
        ),
        "sources_read": [
            "experiments/EXP-ECDLP-869870/specification.yaml preregistered_prediction (B4)",
            "experiments/EXP-ECDLP-869870/source/model.py b4_scaled_precomp / B4_CONTRACT_VALUES",
        ],
        "correction_applied": False,
        "corrected_residual": None,
    }
