"""
Precompute, once per curve, the full table k -> kP for k in [0, N), and the
limb-encoded arrays for every presentation. Cached to disk so the O(N)
group-law walk (incremental point addition) and any subsequent randomness
(the fixed random projective representative, the scrambled-null PRF) is
computed exactly once and then reused identically across every architecture,
capacity and training seed -- this is required for the matched-pair
guarantee (dataset differs only in presentation, nothing else).
"""
import json
import os
import random
import numpy as np
from ec import Curve, ec_add, load_curves, PRF_KEY
import hashlib

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def build_point_table(curve: Curve):
    xs = np.zeros(curve.N, dtype=np.int64)
    ys = np.zeros(curve.N, dtype=np.int64)
    P = None
    for k in range(curve.N):
        if P is None and k > 0:
            raise RuntimeError("point at infinity mid-walk: generator order wrong")
        xs[k] = P[0] if P else 0
        ys[k] = P[1] if P else 0
        P = ec_add(P, curve.G, curve.a, curve.p)
    return xs, ys

def int_to_limbs_vec(vals, n_limbs, limb_bits=4):
    # vals: np.array of python ints (object dtype for safety with large ints not needed here, int64 fine)
    out = np.zeros((len(vals), n_limbs), dtype=np.int64)
    mask = (1 << limb_bits) - 1
    for i in range(n_limbs):
        shift = limb_bits * (n_limbs - 1 - i)
        out[:, i] = (vals >> shift) & mask
    return out

def prf_limbs(curve_name, k, n_limbs_out, limb_bits=4):
    needed_bytes = (n_limbs_out * limb_bits + 7) // 8 + 8
    out = b""
    counter = 0
    while len(out) < needed_bytes:
        h = hashlib.sha256(PRF_KEY + curve_name.encode() + int(k).to_bytes(8, "big") + counter.to_bytes(4, "big"))
        out += h.digest()
        counter += 1
    val = int.from_bytes(out, "big")
    mask = (1 << limb_bits) - 1
    return [(val >> (limb_bits * i)) & mask for i in range(n_limbs_out - 1, -1, -1)]

def precompute_curve(curve: Curve):
    cache_path = os.path.join(CACHE_DIR, f"{curve.name}.npz")
    if os.path.exists(cache_path):
        d = np.load(cache_path)
        return d
    print(f"[precompute] {curve.name}: N={curve.N} p={curve.p} walking group...")
    xs, ys = build_point_table(curve)
    nL = curve.n_limbs_coord

    affine = np.concatenate([int_to_limbs_vec(xs, nL), int_to_limbs_vec(ys, nL)], axis=1)
    x_only = int_to_limbs_vec(xs, nL)

    # fixed random projective representative per k, deterministic given a
    # fixed presentation-level PRNG seed (not the per-run training seed) so
    # the dataset itself is identical across training seeds/architectures.
    rng = random.Random(hash((curve.name, "projective_fixed_seed")) & 0xFFFFFFFF)
    p = curve.p
    Z = np.array([rng.randrange(1, p) for _ in range(curve.N)], dtype=np.int64)
    Z2 = (Z * Z) % p
    Z3 = (Z2 * Z) % p
    Xp = (xs * Z2) % p
    Yp = (ys * Z3) % p
    projective = np.concatenate([
        int_to_limbs_vec(Xp, nL), int_to_limbs_vec(Yp, nL), int_to_limbs_vec(Z, nL)
    ], axis=1)

    # planted leaky (C3): overwrite last x-limb with top 4 bits of k
    planted = affine.copy()
    shift = max(curve.N.bit_length() - 5, 0)
    top4 = (np.arange(curve.N, dtype=np.int64) >> shift) & 0xF
    planted[:, nL - 1] = top4

    # scrambled null: PRF(key, k) -> limb string of the SAME length as affine
    n_limbs_affine = affine.shape[1]
    scrambled = np.zeros((curve.N, n_limbs_affine), dtype=np.int64)
    for k in range(curve.N):
        scrambled[k, :] = prf_limbs(curve.name, k, n_limbs_affine)

    msb = (np.arange(curve.N, dtype=np.int64) < (curve.N // 2)).astype(np.int64)

    np.savez(cache_path, affine=affine, x_only=x_only, projective=projective,
              planted=planted, scrambled=scrambled, msb=msb,
              xs=xs, ys=ys, n_limbs_coord=nL, n_limbs_affine=n_limbs_affine)
    print(f"[precompute] {curve.name}: done, cached at {cache_path}")
    return np.load(cache_path)

if __name__ == "__main__":
    curves = load_curves()
    for name, c in curves.items():
        precompute_curve(c)
