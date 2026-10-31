#!/usr/bin/env python3
"""Mechanical F-2 fixture and P-5 derivation for EXP-RELN-dc761f.

This task is deliberately label-free: it derives inputs only.  It does not
draw any protocol-labelled values, run the RELN experiment, or edit the
specification or ledger.  PARI/GP is used only for exact curve cardinalities;
all scan, arithmetic, and P-5 accounting is independently implemented here.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml


TASK = "TASK-20261001-84833e"
EXP = "EXP-RELN-dc761f"
NAMESPACE = f"{EXP}/v1"
REPO = Path(os.environ.get("RELN_REPO_ROOT", Path.cwd())).resolve()
OUT = REPO / "coordination/goals/GOAL-RELN-001/batches/BATCH-79a580/tasks" / TASK
VOL = Path("/Volumes/SSD990")

F1 = [
    {"id": "b16-s11", "bits": 16, "seed": 11, "p": 62417, "a": 31838, "b": 5672, "N": 61979, "G": [0, 27690]},
    {"id": "b16-s12", "bits": 16, "seed": 12, "p": 49391, "a": 17959, "b": 16189, "N": 49367, "G": [6, 24294]},
    {"id": "b16-s13", "bits": 16, "seed": 13, "p": 39607, "a": 28493, "b": 1765, "N": 39581, "G": [0, 15550]},
    {"id": "b20-s11", "bits": 20, "seed": 11, "p": 855727, "a": 220250, "b": 149669, "N": 856153, "G": [3, 354997]},
    {"id": "b20-s12", "bits": 20, "seed": 12, "p": 855641, "a": 287740, "b": 209027, "N": 854363, "G": [0, 248685]},
    {"id": "b20-s13", "bits": 20, "seed": 13, "p": 911707, "a": 786752, "b": 903968, "N": 911033, "G": [2, 189920]},
    {"id": "b24-s11", "bits": 24, "seed": 11, "p": 9769087, "a": 1694034, "b": 548449, "N": 9773123, "G": [0, 3916788]},
    {"id": "b24-s12", "bits": 24, "seed": 12, "p": 15738469, "a": 11997084, "b": 5182456, "N": 15735007, "G": [4, 7793897]},
    {"id": "b24-s13", "bits": 24, "seed": 13, "p": 10589077, "a": 4368383, "b": 1627642, "N": 10593239, "G": [1, 4615285]},
]

F1_P5 = {
    "b16-s11": [10, 83, 10, 6, 38, 88, 72, 904, 2750, 166, 331, 662, 1324],
    "b16-s12": [9, 76, 9, 2, 33, 70, 8, 264, 2106, 178, 355, 709, 1417],
    "b16-s13": [9, 70, 9, 6, 29, 70, 72, 694, 1618, 129, 257, 514, 1028],
    "b20-s11": [16, 237, 16, 6, 103, 218, 72, 2464, 20860, 955, 1909, 3818, 7636],
    "b20-s12": [16, 237, 16, 7, 106, 226, 98, 2964, 22148, 911, 1821, 3641, 7281],
    "b20-s13": [16, 243, 16, 10, 115, 250, 200, 4580, 26008, 864, 1728, 3455, 6910],
    "b24-s11": [26, 626, 26, 14, 320, 668, 392, 17904, 202432, 3560, 7120, 14239, 28477],
    "b24-s12": [28, 757, 28, 12, 348, 720, 288, 16684, 240076, 5347, 10694, 21388, 42776],
    "b24-s13": [26, 646, 26, 10, 337, 694, 200, 13472, 224422, 3763, 7526, 15051, 30102],
}

P5_COLUMNS = ["B", "B2", "L", "L_fb", "n_lp", "scan_size", "R_full", "R_lp1", "R_lp2", "A_1/4", "A_1/2", "A_1", "A_2"]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def machine_reading() -> dict:
    root = shutil.disk_usage("/")
    if not VOL.exists():
        raise RuntimeError("C-7 repository volume /Volumes/SSD990 is absent")
    repo_vol = shutil.disk_usage(VOL)
    load15 = os.getloadavg()[2]
    reading = {
        "read_at": now(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "loadavg_15m": load15,
        "load_limit": 14.0,
        "root_free_gib": root.free / 2**30,
        "root_free_min_gib": 5.0,
        "repository_volume": str(VOL),
        "repository_free_gib": repo_vol.free / 2**30,
        "repository_free_min_gib": 20.0,
        "rss_limit_gib": 4.0,
        "workers": 1,
        "nice_required": 10,
        "tmpdir": os.environ.get("TMPDIR"),
    }
    if load15 > 14.0 or reading["root_free_gib"] < 5.0 or reading["repository_free_gib"] < 20.0:
        raise RuntimeError(json.dumps({"class": "infrastructure_error", "reason": "C-7 machine protection failed closed", "readings": reading}, sort_keys=True))
    return reading


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 17):
        if a >= n:
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


def next_prime(n: int) -> int:
    n = max(2, n)
    if n > 2 and n % 2 == 0:
        n += 1
    while not is_prime(n):
        n += 1 if n == 2 else 2
    return n


def ceil_root(n: int, degree: int) -> int:
    lo, hi = 0, 1
    while hi**degree < n:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**degree >= n:
            hi = mid
        else:
            lo = mid
    return hi


def sqrt_mod(n: int, p: int) -> int | None:
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        s += 1
        q //= 2
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    c, x, t, m = pow(z, q, p), pow(n, (q + 1) // 2, p), pow(n, q, p), s
    while t != 1:
        i, e = 1, (t * t) % p
        while e != 1:
            e = e * e % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        x, t, c, m = x * b % p, t * b * b % p, b * b % p, i
    return x


def least_point(p: int, a: int, b: int) -> list[int]:
    for x in range(p):
        y = sqrt_mod((x * x * x + a * x + b) % p, p)
        if y is not None:
            return [x, min(y, p - y)]
    raise RuntimeError("no affine point found")


def gp_card(p: int, a: int, b: int) -> int:
    source = f"E=ellinit([{a},{b}],{p}); print(ellcard(E)); quit()\n"
    proc = subprocess.run(["gp", "-q"], input=source, text=True, capture_output=True, check=True)
    values = [int(line.strip()) for line in proc.stdout.splitlines() if line.strip().isdigit()]
    if not values:
        raise RuntimeError(f"PARI returned no cardinality: {proc.stdout!r} {proc.stderr!r}")
    return values[-1]


def points_under(p: int, a: int, b: int, limit: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for x in range(limit):
        y = sqrt_mod((x * x * x + a * x + b) % p, p)
        if y is not None:
            out.append((x, y))
            if y:
                out.append((x, p - y))
    out.sort()
    return out


def batch_inverses(values: list[int], p: int) -> list[int]:
    prefix: list[int] = []
    acc = 1
    for value in values:
        if value:
            acc = acc * value % p
        prefix.append(acc)
    inv_acc = pow(acc, p - 2, p) if acc != 1 else 1
    result = [0] * len(values)
    for i in range(len(values) - 1, -1, -1):
        value = values[i]
        if value:
            result[i] = inv_acc * (prefix[i - 1] if i else 1) % p
            inv_acc = inv_acc * value % p
    return result


def scan_yield(p: int, a: int, b: int, n: int) -> dict:
    B = ceil_root(p, 5)
    B2 = ceil_root(p * p, 5)
    points = points_under(p, a, b, B2)
    counts = {"R_full": 0, "R_lp1": 0, "R_lp2": 0}
    seen: set[tuple[int, int]] = set()
    block_size = 4096
    for i, (x1, y1) in enumerate(points):
        for start in range(i, len(points), block_size):
            block = points[start : min(start + block_size, len(points))]
            denoms: list[int] = []
            nums: list[int] = []
            valid: list[bool] = []
            for x2, y2 in block:
                if x1 == x2:
                    if (y1 + y2) % p == 0:
                        denoms.append(0); nums.append(0); valid.append(False)
                    else:
                        denoms.append((2 * y1) % p); nums.append((3 * x1 * x1 + a) % p); valid.append(True)
                else:
                    denoms.append((x2 - x1) % p); nums.append((y2 - y1) % p); valid.append(True)
            inv = batch_inverses(denoms, p)
            for (x2, y2), num, slope_inv, ok in zip(block, nums, inv, valid):
                if not ok:
                    continue
                slope = num * slope_inv % p
                x3 = (slope * slope - x1 - x2) % p
                y3 = (slope * (x1 - x3) - y1) % p
                r = (x3, y3)
                if r in seen:
                    continue
                seen.add(r)
                high = (x1 >= B) + (x2 >= B)
                counts["R_full" if high == 0 else "R_lp1" if high == 1 else "R_lp2"] += 1
    n_edge = counts["R_lp1"] + counts["R_lp2"]
    if not n_edge:
        raise RuntimeError("P-5 scan found no LP edges")
    fb_x = {x for x, _ in points if x < B}
    lp_x = {x for x, _ in points if x >= B}
    n_lp = len(lp_x)
    def budget(k_num: int, k_den: int) -> int:
        top = k_num * (n_lp + 1) * n
        bot = k_den * n_edge
        return (top + bot - 1) // bot
    values = [B, B2, ceil_root(n, 5), len(fb_x), n_lp, len(points), counts["R_full"], counts["R_lp1"], counts["R_lp2"], budget(1, 4), budget(1, 2), budget(1, 1), budget(2, 1)]
    return {"columns": P5_COLUMNS, "values": values, "B": B, "B2": B2, "L": ceil_root(n, 5), "L_fb": len(fb_x), "n_lp": n_lp, "scan_size": len(points), "counts": counts, "n_edge": n_edge}


def checks(f: dict) -> dict:
    p, a, b, n = f["p"], f["a"], f["b"], f["N"]
    return {
        "p_prime": is_prime(p),
        "N_prime": is_prime(n),
        "discriminant_nonzero": (4 * a**3 + 27 * b**2) % p != 0,
        "N_not_p": n != p,
        "N_not_p_plus_1": n != p + 1,
        "embedding_degree_gt_20": all(pow(p, k, n) != 1 for k in range(1, 21)),
        "point_on_curve": (f["G"][1] ** 2 - (f["G"][0] ** 3 + a * f["G"][0] + b)) % p == 0,
    }


def derive_f2(seed: int) -> tuple[dict, list[dict]]:
    rejected: list[dict] = []
    for c in range(100000):
        x = int.from_bytes(hashlib.sha256(f"{NAMESPACE}|curve|28|{seed}|{c}".encode()).digest(), "big")
        p = next_prime(2**27 + (x % 2**27))
        if p.bit_length() != 28:
            rejected.append({"counter": c, "reason": "p_not_28_bits", "p": p}); continue
        a, b = (x >> 64) % p, (x >> 128) % p
        reason = None
        if a == 0 or b == 0:
            reason = "zero_coefficient"
        elif (4 * a**3 + 27 * b**2) % p == 0:
            reason = "singular"
        else:
            n = gp_card(p, a, b)
            if not is_prime(n): reason = "N_not_prime"
            elif n == p: reason = "N_equals_p"
            elif n == p + 1: reason = "N_equals_p_plus_1"
            elif not all(pow(p, k, n) != 1 for k in range(1, 21)): reason = "embedding_degree_not_gt_20"
            else:
                f = {"id": f"b28-s{seed}", "bits": 28, "seed": seed, "counter": c, "p": p, "a": a, "b": b, "N": n, "G": least_point(p, a, b)}
                return f, rejected
        rejected.append({"counter": c, "reason": reason, "p": p, "a": a, "b": b})
    raise RuntimeError(f"no F-2 fixture found for seed {seed}")


def main() -> int:
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    reading = machine_reading()
    f1_results = []
    for f in F1:
        card = gp_card(f["p"], f["a"], f["b"])
        p5 = scan_yield(f["p"], f["a"], f["b"], f["N"])
        result = {**f, "gp_N": card, "checks": checks(f), "p5": p5, "p5_matches_contract": p5["values"] == F1_P5[f["id"]], "gp_N_matches_contract": card == f["N"]}
        f1_results.append(result)
    f2_results = []
    for seed in (11, 12, 13):
        f, rejected = derive_f2(seed)
        f["checks"] = checks(f)
        f["p5"] = scan_yield(f["p"], f["a"], f["b"], f["N"])
        f["rejected_counters"] = rejected
        f2_results.append(f)
    output = {
        "schema": "crypto.autoresearch.reln_f2_p5.v1",
        "task_id": TASK,
        "experiment_id": EXP,
        "scientific_runs_performed": 0,
        "protocol_labels_drawn": False,
        "machine_protection": reading,
        "f1": f1_results,
        "f1_all_p5_match": all(x["p5_matches_contract"] for x in f1_results),
        "f1_all_point_counts_match": all(x["gp_N_matches_contract"] for x in f1_results),
        "f2": f2_results,
        "elapsed_seconds": time.time() - started,
    }
    (OUT / "derivation_output.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    report = {
        "schema": "crypto.autoresearch.reln_derivation_report.v1",
        "task_id": TASK,
        "experiment_id": EXP,
        "status": "completed",
        "scientific_runs_performed": 0,
        "protocol_labels_drawn": False,
        "command": "nice -n 10 env TMPDIR=/Volumes/SSD990/.tmp-agent /usr/bin/python3 derive_f2_p5.py",
        "machine_protection": reading,
        "f1_control": {"all_p5_match": output["f1_all_p5_match"], "all_point_counts_match": output["f1_all_point_counts_match"]},
        "f2_fixture_count": len(f2_results),
        "output": "derivation_output.json",
        "elapsed_seconds": output["elapsed_seconds"],
    }
    (OUT / "derivation_report.yaml").write_text(yaml.safe_dump(report, sort_keys=False))
    print(json.dumps({"status": "completed", "f1_all_p5_match": output["f1_all_p5_match"], "f1_all_point_counts_match": output["f1_all_point_counts_match"], "f2": [{"id": x["id"], "counter": x["counter"], "p": x["p"], "N": x["N"]} for x in f2_results], "elapsed_seconds": output["elapsed_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
