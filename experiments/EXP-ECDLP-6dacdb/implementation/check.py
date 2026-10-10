#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-6dacdb run artifacts. Reads only.

Shares no code with run.py. Part A: for a seeded sample of recorded curves it
recounts #E with its own Legendre table, re-derives l as the largest prime
factor and recomputes the multiplicative order of p modulo l, and it
recomputes the small-k fraction and the t histogram of every arm from the
rows; every supersingular control must read k = 2 and every CTRL-COUNT must
hold. Part B: for every deployed row it re-tests primality of p and l, the
Hasse interval, the base point (where bound) and [l]G = O with its own
scalar multiplication (affine, short Weierstrass; Montgomery x-only ladder for
Curve25519), re-verifies the recorded embedding-degree claim by direct
exponentiation up to a replay cap, and recomputes k* from the stated L(1/3)
formula and constants. Exit 0 iff no problem.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

EXP = "EXP-ECDLP-6dacdb"
SAMPLE_ROWS = 12
REPLAY_K_CAP = 20000
CURVES = {
    "Curve25519": {"p": 2 ** 255 - 19, "A": 486662, "u": 9, "montgomery": True},
    "P-256": {"p": 2 ** 256 - 2 ** 224 + 2 ** 192 + 2 ** 96 - 1, "a": -3,
              "b": 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
              "G": (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                    0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)},
    "secp256k1": {"p": 2 ** 256 - 2 ** 32 - 977, "a": 0, "b": 7,
                  "G": (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
                        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)},
    "P-521": {"p": 2 ** 521 - 1, "a": -3,
              "b": 0x51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
              "G": (0xC6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
                    0x11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650)},
    "Ed448": {"p": 2 ** 448 - 2 ** 224 - 1},
    "brainpoolP256r1": {"p": 0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
                        "a": 0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
                        "b": 0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
                        "G": (0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262,
                              0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997)},
}
ORDERS = {
    "Curve25519": (2 ** 252 + 27742317777372353535851937790883648493, 8),
    "P-256": (0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551, 1),
    "secp256k1": (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141, 1),
    "P-521": (0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409, 1),
    "Ed448": (2 ** 446 - 0x8335dc163bb124b65129c96fde933d8d723a70aadc873d6d54a7bb0d, 4),
    "brainpoolP256r1": (0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7, 1),
}
CONSTANTS = {"GNFS_1.923": (64 / 9) ** (1 / 3), "exTNFS_1.747": (48 / 9) ** (1 / 3),
             "SNFS_or_STNFS_1.526": (32 / 9) ** (1 / 3)}


def is_prime(n, rounds=48):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = random.Random(n ^ 0x6dacdb)
    bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41] + [rng.randrange(2, n - 1) for _ in range(rounds)]
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


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


def ladder_is_infinity(k, u, A, p):
    a24 = (A + 2) * pow(4, -1, p) % p
    X2, Z2, X3, Z3 = 1, 0, u, 1
    for bit in bin(k)[2:]:
        if bit == "1":
            X2, Z2, X3, Z3 = X3, Z3, X2, Z2
        t0, t1, t2, t3 = (X2 + Z2) % p, (X2 - Z2) % p, (X3 + Z3) % p, (X3 - Z3) % p
        s, r = t0 * t3 % p, t1 * t2 % p
        X3n, Z3n = (s + r) ** 2 % p, u * (s - r) ** 2 % p
        aa, bb = t0 * t0 % p, t1 * t1 % p
        e = (aa - bb) % p
        X2, Z2, X3, Z3 = aa * bb % p, e * (bb + a24 * e) % p, X3n, Z3n
        if bit == "1":
            X2, Z2, X3, Z3 = X3, Z3, X2, Z2
    return Z2 == 0


def count_points(p, a, b):
    table = bytearray(p)
    for y in range(p):
        table[y * y % p] = 1
    total = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v:
            total += 1 if table[v] else -1
    return total


def largest_prime_factor(n):
    lpf, q = 1, 2
    while q * q <= n:
        while n % q == 0:
            lpf, n = q, n // q
        q += 1
    return max(lpf, n) if n > 1 else lpf


def order_mod(p, l, cap):
    v, x, k = p % l, p % l, 1
    while v != 1:
        v = v * x % l
        k += 1
        if k > cap:
            return None
    return k


def l_log2(c, ln_q):
    return c * ln_q ** (1 / 3) * math.log(ln_q) ** (2 / 3) / math.log(2)


def main(argv):
    if len(argv) != 1:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(argv[0])
    errs = []
    try:
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        manifest = (run_dir / "manifest.yaml").read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"unreadable artifacts: {error}", file=sys.stderr)
        return 1
    if raw.get("experiment_id") != EXP or EXP not in manifest:
        errs.append("wrong experiment id")
    part_a, part_b = raw.get("part_a"), raw.get("part_b")
    replayed = 0
    if part_a:
        rng = random.Random("EXP-ECDLP-6dacdb:check")
        rows_by_arm = {"special": [], "random": []}
        all_rows = []
        for cell in part_a.get("cells") or []:
            census = cell.get("census") or {}
            p = census["p"]
            if not is_prime(p):
                errs.append(f"p={p}: not prime")
            ctrl = census.get("ctrl_count") or {}
            if not (ctrl.get("hasse") and ctrl.get("point_killed")):
                errs.append(f"p={p}: CTRL-COUNT failed")
            if ctrl and count_points(p, ctrl["a"], ctrl["b"]) != ctrl["order"]:
                errs.append(f"p={p}: CTRL-COUNT order recount differs")
            ss = census.get("supersingular_control")
            if ss is not None and ss.get("k") != 2:
                errs.append(f"p={p}: supersingular control k={ss.get('k')} != 2")
            for row in census.get("rows") or []:
                rows_by_arm[census["arm"]].append(row)
                all_rows.append((p, row))
        for p, row in rng.sample(all_rows, min(SAMPLE_ROWS, len(all_rows))):
            n = count_points(p, row["a"], row["b"])
            replayed += 1
            if n != row["order"]:
                errs.append(f"p={p} a={row['a']} b={row['b']}: recounted #E {n} != {row['order']}")
            l = largest_prime_factor(n)
            if l != row["l"]:
                errs.append(f"p={p}: largest prime factor {l} != recorded {row['l']}")
            k = order_mod(p, l, l)
            if k != row["k"] or (k and row["t"] != (l - 1) // k):
                errs.append(f"p={p} l={l}: recomputed k {k} != recorded {row['k']}")
        tests = part_a.get("tests") or {}
        for arm, rows in rows_by_arm.items():
            if not rows:
                continue
            frac = sum(1 for r in rows if r["k"] and r["k"] <= 20) / len(rows)
            if abs(frac - tests.get("small_k_fraction", {}).get(arm, -1)) > 1e-12:
                errs.append(f"{arm}: small-k fraction recomputed {frac} differs")
            mean = sum(math.log2(r["t"]) for r in rows if r["t"]) / sum(1 for r in rows if r["t"])
            if abs(mean - tests.get("mean_log2_t", {}).get(arm, -1)) > 1e-9:
                errs.append(f"{arm}: mean log2 t recomputed {mean} differs")
    if part_b:
        for row in part_b.get("rows") or []:
            name = row["name"]
            spec, (l, h) = CURVES.get(name), ORDERS.get(name, (None, None))
            if spec is None:
                errs.append(f"{name}: unknown curve row")
                continue
            p = spec["p"]
            if row.get("bits_p") != p.bit_length() or row.get("bits_l") != l.bit_length():
                errs.append(f"{name}: bit lengths differ from the checker's constants")
            if not is_prime(p) or not is_prime(l) or abs(p + 1 - h * l) > 2 * math.isqrt(p) + 1:
                errs.append(f"{name}: primality or Hasse check fails in the checker")
            if spec.get("montgomery"):
                ok = ladder_is_infinity(l, spec["u"], spec["A"], p)
            elif "G" in spec:
                G = spec["G"]
                ok = (G[1] ** 2 - (G[0] ** 3 + spec["a"] * G[0] + spec["b"])) % p == 0 and ec_mul(l, G, spec["a"] % p, p) is None
            else:
                ok = None
            if ok is False or (ok is not None and row.get("order_check_lG_is_O") is not True):
                errs.append(f"{name}: order check disagrees (checker {ok}, recorded {row.get('order_check_lG_is_O')})")
            k_rec = row.get("embedding_degree")
            k_small = order_mod(p, l, REPLAY_K_CAP)
            if isinstance(k_rec, int):
                if pow(p, k_rec, l) != 1 or (k_small is not None and k_small != k_rec):
                    errs.append(f"{name}: recorded embedding degree {k_rec} is not the order of p mod l")
            elif k_small is not None:
                errs.append(f"{name}: checker found embedding degree {k_small} but the row claims {k_rec}")
            rho = math.log2(0.886) + 0.5 * math.log2(l)
            if abs(rho - row.get("rho_cost_log2", 0)) > 1e-9:
                errs.append(f"{name}: rho cost mismatch")
            for cname, c in CONSTANTS.items():
                kstar = 0
                for kk in range(1, 10000):
                    cost = l_log2(c, kk * math.log(p))
                    if cost < rho:
                        kstar = kk
                    if cost > rho + 20:
                        break
                if (row.get("transfer_threshold") or {}).get(cname, {}).get("k_star") != kstar:
                    errs.append(f"{name} {cname}: k* recomputed {kstar} differs")
    if not part_a and not part_b:
        errs.append("neither part A nor part B present")
    for e in errs:
        print("FAIL:", e, file=sys.stderr)
    print(f"{EXP} check: parts {'A' if part_a else ''}{'B' if part_b else ''}, {replayed} curve row(s) recounted independently, {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
