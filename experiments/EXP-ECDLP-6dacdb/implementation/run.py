#!/usr/bin/env python3
"""EXP-ECDLP-6dacdb: transfer exposure.

Part A: embedding-degree census of seeded random curves over special-form
versus matched random toy primes. Part B: exact embedding-degree lower bound
(order of p modulo l exceeds 10^6) for deployed special-prime curves and the
transfer threshold k* under stated, recalled, optimistic L(1/3) constants.
Pure Python 3 standard library. Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402

# ----------------------------------------------------------------------------
# affine short-Weierstrass arithmetic over F_p (any size)
# ----------------------------------------------------------------------------


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def count_points(p: int, a: int, b: int) -> int:
    table = [0] * p
    for y in range(p):
        table[y * y % p] = 1
    total = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        total += 1 if table[v] else -1
    return total


def factor_small(n: int) -> dict:
    f = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def mult_order(p: int, l: int, cap: int | None = None) -> int | None:
    """Order of p modulo l by direct search (cap = None: full search up to l-1)."""
    x = p % l
    if x == 0:
        return None
    v = x
    k = 1
    limit = (l - 1) if cap is None else cap
    while v != 1:
        v = v * x % l
        k += 1
        if k > limit:
            return None
    return k


def random_point(p, a, b, rng):
    while True:
        x = rng.randrange(p)
        v = (x * x * x + a * x + b) % p
        if v == 0:
            return (x, 0)
        if pow(v, (p - 1) // 2, p) == 1:
            # Tonelli-Shanks
            y = sqrt_mod(v, p)
            return (x, y)


def sqrt_mod(n, p):
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        bexp = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, bexp * bexp % p, t * bexp * bexp % p, r * bexp % p
    return r


# ----------------------------------------------------------------------------
# part A
# ----------------------------------------------------------------------------


def census_prime(p: int, arm: str, curves: int, seed: int) -> dict:
    rng = random.Random(f"EXP-ECDLP-6dacdb:{seed}:{arm}:{p}")
    rows = []
    anomalous = 0
    ctrl_count = None
    while len(rows) + anomalous < curves:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a * a * a + 27 * b * b) % p == 0:
            continue
        n = count_points(p, a, b)
        if ctrl_count is None:
            P = random_point(p, a, b, rng)
            ctrl_count = {"a": a, "b": b, "order": n,
                          "hasse": abs(n - p - 1) <= 2 * math.isqrt(p) + 1,
                          "point_killed": ec_mul(n, P, a, p) is None}
        if n == p:
            anomalous += 1
            continue
        l = max(factor_small(n))
        k = mult_order(p, l)
        rows.append({"a": a, "b": b, "order": n, "l": l, "k": k, "t": (l - 1) // k if k else None})
    out = {"p": p, "arm": arm, "rows": rows, "anomalous": anomalous, "ctrl_count": ctrl_count}
    if p % 4 == 3:
        n = p + 1  # y^2 = x^3 + x is supersingular
        assert count_points(p, 1, 0) == n
        l = max(factor_small(n))
        out["supersingular_control"] = {"l": l, "k": mult_order(p, l)}
    return out


def part_a(d_list, bits, per_d, curves, seeds):
    cells = []
    for seed in seeds:
        for d in d_list:
            specials = primeset.special_primes(d, bits, per_d)
            for i, sp in enumerate(specials):
                cells.append({"d": d, "seed": seed, "special": sp,
                              "census": census_prime(sp["p"], "special", curves, seed)})
                rp = primeset.matched_random_prime(bits, seed, f"d{d}:{i}")
                cells.append({"d": d, "seed": seed, "random": rp,
                              "census": census_prime(rp["p"], "random", curves, seed)})
                print(f"part A d={d} seed={seed} pair {i} done", file=sys.stderr, flush=True)
    return cells


def tests(cells, seed):
    rng = random.Random(f"EXP-ECDLP-6dacdb:perm:{seed}")
    sp = [r for c in cells for r in c["census"]["rows"] if c["census"]["arm"] == "special"]
    rd = [r for c in cells for r in c["census"]["rows"] if c["census"]["arm"] == "random"]
    def log2t(rows):
        return [math.log2(r["t"]) for r in rows if r["t"]]
    xs, ys = log2t(sp), log2t(rd)
    obs = statistics.fmean(xs) - statistics.fmean(ys)
    pooled = xs + ys
    n = len(xs)
    count = 0
    reps = 10000
    for _ in range(reps):
        rng.shuffle(pooled)
        diff = statistics.fmean(pooled[:n]) - statistics.fmean(pooled[n:])
        if abs(diff) >= abs(obs):
            count += 1
    perm_p = (count + 1) / (reps + 1)
    def frac_small(rows):
        return sum(1 for r in rows if r["k"] and r["k"] <= 20) / len(rows)
    f1, f2 = frac_small(sp), frac_small(rd)
    se = math.sqrt(f1 * (1 - f1) / len(sp) + f2 * (1 - f2) / len(rd)) if sp and rd else None
    bins = [(1, 1), (2, 2), (3, 4), (5, 16), (17, 10 ** 12)]
    def hist(rows):
        h = [0] * len(bins)
        for r in rows:
            t = r["t"] or 0
            for i, (lo, hi) in enumerate(bins):
                if lo <= t <= hi:
                    h[i] += 1
        return h
    h1, h2 = hist(sp), hist(rd)
    def chi2(h1, h2):
        stat = 0.0
        n1, n2 = sum(h1), sum(h2)
        for u, v in zip(h1, h2):
            tot = u + v
            if tot == 0:
                continue
            e1, e2 = tot * n1 / (n1 + n2), tot * n2 / (n1 + n2)
            stat += (u - e1) ** 2 / e1 + (v - e2) ** 2 / e2
        return stat
    obs_chi = chi2(h1, h2)
    allrows = sp + rd
    cnt = 0
    for _ in range(2000):
        rng.shuffle(allrows)
        if chi2(hist(allrows[:len(sp)]), hist(allrows[len(sp):])) >= obs_chi:
            cnt += 1
    return {"mean_log2_t": {"special": statistics.fmean(xs), "random": statistics.fmean(ys),
                            "difference": obs, "permutation_p_value": perm_p},
            "small_k_fraction": {"special": f1, "random": f2, "difference": f1 - f2,
                                 "standard_error": se},
            "t_histogram": {"bins": bins, "special": h1, "random": h2,
                            "chi_square": obs_chi, "permutation_p_value": (cnt + 1) / 2001},
            "smallest_k": {"special": sorted((r["k"], r["l"]) for r in sp if r["k"])[:3],
                           "random": sorted((r["k"], r["l"]) for r in rd if r["k"])[:3]},
            "n_curves": {"special": len(sp), "random": len(rd)}}


# ----------------------------------------------------------------------------
# part B
# ----------------------------------------------------------------------------

P256_P = 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1
DEPLOYED = [
    {"name": "Curve25519", "p": 2 ** 255 - 19, "special": True,
     "special_form": "u^5 - 19 at u = 2^51",
     "l": 2 ** 252 + 27742317777372353535851937790883648493, "h": 8,
     "model": "montgomery", "A": 486662, "u": 9, "provenance": "recalled; verified by ladder"},
    {"name": "P-256", "p": P256_P, "special": True, "special_form": "Solinas 2^256 - 2^224 + 2^192 + 2^96 - 1",
     "l": 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551, "h": 1,
     "model": "weierstrass", "a": P256_P - 3,
     "b": 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
     "G": (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5),
     "provenance": "recalled; verified by [l]G = O"},
    {"name": "secp256k1", "p": 2 ** 256 - 2 ** 32 - 977, "special": True, "special_form": "2^256 - 2^32 - 977",
     "l": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141, "h": 1,
     "model": "weierstrass", "a": 0, "b": 7,
     "G": (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
           0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8),
     "provenance": "recalled; verified by [l]G = O"},
    {"name": "P-521", "p": 2 ** 521 - 1, "special": True, "special_form": "Mersenne 2^521 - 1",
     "l": 0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409,
     "h": 1, "model": "weierstrass", "a": 2 ** 521 - 4,
     "b": 0x51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
     "G": (0xC6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
           0x11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650),
     "provenance": "aburan28/crypto src/ecc/curve_zoo.rs; verified by [l]G = O"},
    {"name": "Ed448", "p": 2 ** 448 - 2 ** 224 - 1, "special": True, "special_form": "u^2 - u - 1 at u = 2^224",
     "l": 2 ** 446 - 0x8335dc163bb124b65129c96fde933d8d723a70aadc873d6d54a7bb0d, "h": 4,
     "model": None, "provenance": "aburan28/crypto src/ecc/ed448.rs; order RECALLED, no base point bound here"},
    {"name": "brainpoolP256r1", "p": 0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
     "special": False, "special_form": None,
     "l": 0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7, "h": 1,
     "model": "weierstrass",
     "a": 0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
     "b": 0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
     "G": (0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262,
           0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997),
     "provenance": "aburan28/crypto src/ecc/curve_zoo.rs; verified by [l]G = O"},
]

CONSTANTS = {"GNFS_1.923": (64 / 9) ** (1 / 3), "exTNFS_1.747": (48 / 9) ** (1 / 3),
             "SNFS_or_STNFS_1.526": (32 / 9) ** (1 / 3)}


def montgomery_ladder_is_infinity(k: int, u: int, A: int, p: int) -> bool:
    """x-only ladder on B y^2 = x^3 + A x^2 + x; returns True iff [k]P = O."""
    a24 = (A + 2) * pow(4, -1, p) % p
    X2, Z2, X3, Z3 = 1, 0, u, 1
    for bit in bin(k)[2:]:
        if bit == "1":
            X2, Z2, X3, Z3 = X3, Z3, X2, Z2
        # X3 = add(X2,Z2,X3,Z3) ; X2 = double(X2,Z2)
        t0 = (X2 + Z2) % p
        t1 = (X2 - Z2) % p
        t2 = (X3 + Z3) % p
        t3 = (X3 - Z3) % p
        s = t0 * t3 % p
        r = t1 * t2 % p
        X3n = (s + r) ** 2 % p
        Z3n = u * (s - r) ** 2 % p
        aa, bb = t0 * t0 % p, t1 * t1 % p
        e = (aa - bb) % p
        X2n = aa * bb % p
        Z2n = e * (bb + a24 * e) % p
        X2, Z2, X3, Z3 = X2n, Z2n, X3n, Z3n
        if bit == "1":
            X2, Z2, X3, Z3 = X3, Z3, X2, Z2
    return Z2 % p == 0


def l_cost_log2(c: float, log_q: float) -> float:
    """log2 of L_Q(1/3, c) = exp(c (ln Q)^{1/3} (ln ln Q)^{2/3}), log_q = ln Q."""
    return c * log_q ** (1 / 3) * math.log(log_q) ** (2 / 3) / math.log(2)


def part_b(k_cap: int) -> list[dict]:
    rows = []
    for cv in DEPLOYED:
        p, l, h = cv["p"], cv["l"], cv["h"]
        row = {"name": cv["name"], "special": cv["special"], "special_form": cv["special_form"],
               "bits_p": p.bit_length(), "bits_l": l.bit_length(), "provenance": cv["provenance"]}
        row["p_prime"] = primeset.is_prime(p)
        row["l_prime"] = primeset.is_prime(l)
        row["hasse"] = abs(p + 1 - h * l) <= 2 * math.isqrt(p) + 1
        if cv["model"] == "weierstrass":
            G = cv["G"]
            on = (G[1] ** 2 - (G[0] ** 3 + cv["a"] * G[0] + cv["b"])) % p == 0
            row["base_point_on_curve"] = on
            row["order_check_lG_is_O"] = on and ec_mul(l, G, cv["a"], p) is None
        elif cv["model"] == "montgomery":
            row["order_check_lG_is_O"] = montgomery_ladder_is_infinity(l, cv["u"], cv["A"], p)
        else:
            row["order_check_lG_is_O"] = None
        t0 = time.time()
        k = mult_order(p, l, cap=k_cap)
        row["embedding_degree"] = k if k else f"> {k_cap}"
        row["embedding_degree_search_seconds"] = time.time() - t0
        rho_log2 = math.log2(0.886) + 0.5 * math.log2(l)
        row["rho_cost_log2"] = rho_log2
        thresholds = {}
        for name, c in CONSTANTS.items():
            kstar = 0
            kstar_div = 0
            for kk in range(1, 10000):
                cost = l_cost_log2(c, kk * math.log(p))
                if cost < rho_log2:
                    kstar = kk
                if cost - math.log2(1000) < rho_log2:
                    kstar_div = kk
                if cost > rho_log2 + 20:
                    break
            thresholds[name] = {"c": c, "k_star": kstar, "k_star_cost_div_1e3": kstar_div,
                                "cost_log2_at_k1": l_cost_log2(c, math.log(p))}
        row["transfer_threshold"] = thresholds
        rows.append(row)
        print(f"part B {cv['name']} done", file=sys.stderr, flush=True)
    return rows


def deployed_table(rows) -> str:
    lines = ["| curve | special | l bits | k_actual | rho log2 | k* GNFS | k* exTNFS | k* SNFS/STNFS | order check |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        th = r["transfer_threshold"]
        lines.append(f"| {r['name']} | {r['special']} | {r['bits_l']} | {r['embedding_degree']} | "
                     f"{r['rho_cost_log2']:.1f} | {th['GNFS_1.923']['k_star']} | {th['exTNFS_1.747']['k_star']} | "
                     f"{th['SNFS_or_STNFS_1.526']['k_star']} | {r['order_check_lG_is_O']} |")
    lines.append("")
    lines.append("Constants are recalled and the o(1) is dropped: k* is optimistic for the attacker. "
                 "k_actual is an exact lower bound from direct exponentiation.")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", nargs="+", default=["A", "B"])
    ap.add_argument("--d", type=int, nargs="+", default=[2, 3, 4, 5])
    ap.add_argument("--bits", type=int, default=16)
    ap.add_argument("--primes-per-d", type=int, default=3)
    ap.add_argument("--curves", type=int, default=64)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--k-cap", type=int, default=10 ** 6)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    raw = {"experiment_id": "EXP-ECDLP-6dacdb", "hypothesis_id": "H-ECDLP-bd1572", "argv": sys.argv}
    if "A" in args.part:
        cells = part_a(args.d, args.bits, args.primes_per_d, args.curves, args.seeds)
        raw["part_a"] = {"cells": cells, "tests": tests(cells, args.seeds[0]),
                         "supersingular_controls": [c["census"].get("supersingular_control")
                                                    for c in cells if "supersingular_control" in c["census"]]}
    if "B" in args.part:
        rows = part_b(args.k_cap)
        raw["part_b"] = {"constants": CONSTANTS, "rows": rows}
        with open(os.path.join(args.out, "deployed-table.md"), "w", encoding="utf-8") as fh:
            fh.write(deployed_table(rows))
    raw["wall_clock_seconds"] = time.time() - started
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    src = os.path.abspath(__file__)
    manifest = {"experiment_id": "EXP-ECDLP-6dacdb", "command": " ".join(sys.argv),
                "python": platform.python_version(), "platform": platform.platform(),
                "source_sha256": {"run.py": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                                  "primeset.py": hashlib.sha256(open(os.path.join(os.path.dirname(src), "primeset.py"), "rb").read()).hexdigest()},
                "raw_result_sha256": hashlib.sha256(open(raw_path, "rb").read()).hexdigest(),
                "started_unix": started, "finished_unix": time.time(),
                "asserts_nothing_about": "the hypothesis; observations only"}
    try:
        manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        manifest["git_commit"] = None
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for k, v in manifest.items():
            fh.write(f"{k}: {json.dumps(v)}\n")


if __name__ == "__main__":
    main()
