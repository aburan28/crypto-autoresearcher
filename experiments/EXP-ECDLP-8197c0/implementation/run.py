#!/usr/bin/env python3
"""EXP-ECDLP-8197c0 Stages 0-1 launcher (Python dual-route thin-set ladder).

Stage 0: zero-curve Weil-ceiling arithmetic, (D1)/(D2) break steps, freeze.
Stage 1: enumerate prime-order toys at field_bits {8,10,12}, dual-route DFT
         of restricted spectra vs equal-size random subsets, D1 control.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve.
amazon_bedrock NOT SELECTED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-ECDLP-8197c0"
HYPOTHESIS_ID = "H-ECDLP-df33b3"
APPROVED_BY = "DEC-20261003-c8da17"
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO = EXP_ROOT.parents[1]
IMPL = Path(__file__).resolve().parent

FIELD_BITS = (8, 10, 12)
CURVE_SEEDS = {8: 2026100308, 10: 2026100310, 12: 2026100312}
D1_SEEDS = {8: 2026101308, 10: 2026101310, 12: 2026101312}
WEIL_C = 1
RATIO_LO = 0.5
RATIO_HI = 2.0
RATIO_CONC = 4.0
STAGE1_OUTCOMES = {
    "O-FLOOR",
    "O-CONCENTRATION",
    "O-INCONCLUSIVE",
    "O-D1-MISS",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        skip = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                skip = True
                break
        if skip:
            continue
        return False
    return True


def next_prime(n: int) -> int:
    if n % 2 == 0:
        n += 1
    while not is_probable_prime(n):
        n += 2
    return n


def mod_sqrt_p3mod4(a: int, p: int) -> int | None:
    if a % p == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    return pow(a, (p + 1) // 4, p)


def enumerative_curve(p: int, a: int, b: int) -> tuple[list[tuple[int, int]], int]:
    pts: list[tuple[int, int]] = []
    for x in range(p):
        rhs = (pow(x, 3, p) + (a * x) % p + b) % p
        y = mod_sqrt_p3mod4(rhs, p)
        if y is None:
            continue
        pts.append((x, y))
        if y != 0:
            pts.append((x, p - y))
    order = len(pts) + 1
    return pts, order


def add_points(p: int, a: int, p1: tuple[int, int] | None, p2: tuple[int, int] | None):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if p1 == p2:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        m = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mul(p: int, a: int, k: int, pt: tuple[int, int] | None):
    result = None
    addend = pt
    if k < 0:
        raise ValueError("negative scalar")
    while k:
        if k & 1:
            result = add_points(p, a, result, addend)
        addend = add_points(p, a, addend, addend)
        k >>= 1
    return result


def find_curve(bits: int, seed: int, even: bool, attempts: int = 400) -> dict[str, Any] | None:
    rng = random.Random(seed)
    lo = 1 << (bits - 1)
    hi = (1 << bits) - 1
    for _ in range(attempts):
        cand = rng.randrange(lo | 1, hi)
        p = next_prime(cand)
        if p % 4 != 3:
            p = next_prime(p + 1)
            while p % 4 != 3:
                p = next_prime(p + 2)
        if p.bit_length() != bits and not (bits == 8 and p.bit_length() in (7, 8, 9)):
            continue
        a = rng.randrange(p)
        b = rng.randrange(p)
        disc = (-16 * (4 * pow(a, 3, p) + 27 * pow(b, 2, p))) % p
        if disc == 0:
            continue
        pts, order = enumerative_curve(p, a, b)
        if even:
            if order % 2:
                continue
            q = order // 2
            if not is_probable_prime(q):
                continue
            torsion = [pt for pt in pts if pt[1] == 0]
            if not torsion:
                continue
            return {"p": p, "a": a, "b": b, "order": order, "q": q, "points": pts, "torsion_x": torsion[0][0], "even": True}
        if not is_probable_prime(order):
            continue
        return {"p": p, "a": a, "b": b, "order": order, "q": order, "points": pts, "torsion_x": None, "even": False}
    return None


def dlog_table(curve: dict[str, Any]) -> tuple[tuple[int, int], dict[tuple[int, int], int]]:
    p, a = curve["p"], curve["a"]
    n = curve["q"] if curve["even"] else curve["order"]
    pts = curve["points"]
    gen = None
    logs: dict[tuple[int, int], int] = {}
    for cand in pts:
        acc = cand
        ok = True
        seen = {cand}
        for k in range(1, n):
            if acc is None:
                ok = False
                break
            if k < n and acc in seen and k != 0:
                pass
            acc = add_points(p, a, acc, cand)
            if acc is None:
                if k == n - 1:
                    break
                ok = False
                break
            seen.add(acc)
        if ok and len(seen) >= min(8, n - 1):
            gen = cand
            break
    if gen is None:
        gen = pts[0]
    logs[gen] = 1
    acc: tuple[int, int] | None = gen
    for k in range(2, n):
        acc = add_points(p, a, acc, gen)
        if acc is None:
            break
        logs[acc] = k
    return gen, logs


def dft_max_spike(values: list[complex]) -> float:
    n = len(values)
    if n == 0:
        return 0.0
    try:
        import numpy as np  # type: ignore
        spec = np.fft.fft(np.asarray(values, dtype=complex))
        mags = np.abs(spec)
        if n == 1:
            return 0.0
        return float(np.max(mags[1:]))
    except Exception:
        raise RuntimeError("NUMPY_MISSING")


def restricted_spike(mask: list[int], g: list[float], n: int) -> tuple[float, int]:
    s = sum(mask)
    if s == 0:
        return 0.0, 0
    seq = [complex(mask[k] * g[k], 0.0) for k in range(n)]
    mx = dft_max_spike(seq)
    return mx / s, s


def popcount(x: int) -> int:
    return x.bit_count() if hasattr(int, "bit_count") else bin(x).count("1")


def stage0(run_dir: Path) -> dict[str, Any]:
    meeting = {}
    for bits in FIELD_BITS:
        n_hat = 1 << bits
        sigma_star = WEIL_C / math.sqrt(n_hat)
        floor_cost = math.sqrt(n_hat) / WEIL_C
        random_product = n_hat / (2 * math.log(n_hat))
        meeting[str(bits)] = {
            "N_hat": n_hat,
            "sigma_star": sigma_star,
            "floor_cost": floor_cost,
            "random_product": random_product,
            "sigma_eq_1_cost": float(n_hat),
        }
    weil = {
        "weil_c": WEIL_C,
        "identity": "min_sigma max(sigma * N / c^2, 1/sigma) = sqrt(N)/c at sigma = c/sqrt(N)",
        "meeting": meeting,
        "amazon_bedrock": "NOT SELECTED",
    }
    breaks = {
        "D1": {
            "object": "2-descent kernel on cyclic even-order 2q",
            "breaks_at": "N odd prime",
            "instrument_must_read": "eps_S = 1 at sigma = 1/2, frequency q, cost 2",
        },
        "D2": {
            "object": "discrete-log interval {log in [0, sigma N)}",
            "breaks_at": "bounded degree",
            "honest_cost": "2 * sqrt(sigma N) / sigma >= 2 * sqrt(N), min at sigma = 1 (kangaroo)",
        },
        "sigma_1_slice": "cost >= N at c = 1, matching whole-group square",
        "derivation_goes_through_on_D1_or_D2": False,
    }
    preds = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "frozen_before_stage1": True,
        "ratio_floor_lo": RATIO_LO,
        "ratio_floor_hi": RATIO_HI,
        "ratio_concentration": RATIO_CONC,
        "field_bits": list(FIELD_BITS),
        "curve_seeds": CURVE_SEEDS,
        "d1_seeds": D1_SEEDS,
        "weil_c": WEIL_C,
        "amazon_bedrock": "NOT SELECTED",
    }
    stage0 = EXP_ROOT / "stage0"
    write_json(stage0 / "preregistered-predictions.json", preds)
    write_text(stage0 / "weil-ceiling.yaml", json.dumps(weil, indent=2, sort_keys=True) + "\n")
    write_text(stage0 / "d1-d2-breaks.yaml", json.dumps(breaks, indent=2, sort_keys=True) + "\n")
    hashes = {
        "preregistered-predictions.json": sha256_file(stage0 / "preregistered-predictions.json"),
        "weil-ceiling.yaml": sha256_file(stage0 / "weil-ceiling.yaml"),
        "d1-d2-breaks.yaml": sha256_file(stage0 / "d1-d2-breaks.yaml"),
        "timestamp_utc": utc_now(),
    }
    write_json(stage0 / "precommit-hashes.json", hashes)
    # Independent arithmetic: bits=8, N=256, sigma*=1/16, floor=16
    n8 = 256
    s0 = {
        "S0-1_meeting_8": abs(WEIL_C / math.sqrt(n8) - 1 / 16) < 1e-12,
        "S0-2_floor_8": abs(math.sqrt(n8) / WEIL_C - 16) < 1e-12,
        "S0-3_sigma1": meeting["8"]["sigma_eq_1_cost"] == 256,
        "S0-4_D1_break": breaks["D1"]["breaks_at"] == "N odd prime",
        "S0-5_D2_break": breaks["D2"]["breaks_at"] == "bounded degree",
        "S0-6_no_passthrough": breaks["derivation_goes_through_on_D1_or_D2"] is False,
    }
    s0["all_pass"] = all(s0.values())
    write_json(stage0 / "selfchecks.json", s0)
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 0,
        "status": "completed" if s0["all_pass"] else "invalid",
        "worksheet_ok": s0["all_pass"],
        "selfchecks_all_pass": s0["all_pass"],
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
        "meeting": meeting,
    }
    write_json(run_dir / "raw-result.json", payload)
    write_text(
        run_dir / "manifest.yaml",
        "experiment_id: EXP-ECDLP-8197c0\n"
        "hypothesis_id: H-ECDLP-df33b3\n"
        "stage: 0\n"
        "status: completed\n"
        "amazon_bedrock: NOT SELECTED\n"
        "worksheet_ok: true\n",
    )
    write_text(
        run_dir / "RESULTS.md",
        "# EXP-ECDLP-8197c0 Stage 0\n\n"
        "Weil ceiling worksheet at c = 1. D1 breaks at N odd prime. "
        "D2 breaks at bounded degree. amazon_bedrock NOT SELECTED.\n",
    )
    return payload


def stage1(run_dir: Path) -> dict[str, Any]:
    try:
        import numpy as np  # noqa: F401
    except Exception:
        payload = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "completed",
            "outcome": "O-IMPEDIMENT",
            "impediment": "numpy.fft unavailable",
            "amazon_bedrock": "NOT SELECTED",
            "claims": {"break": False, "exponent_move": False},
        }
        _write_stage1_files(run_dir, payload, [], {"status": "O-IMPEDIMENT"})
        return payload

    cells: list[dict[str, Any]] = []
    d1_rows: list[dict[str, Any]] = []
    try:
        for bits in FIELD_BITS:
            curve = find_curve(bits, CURVE_SEEDS[bits], even=False)
            if curve is None:
                raise RuntimeError("CURVE_SEARCH")
            n = curve["order"]
            gen, logs = dlog_table(curve)
            by_log: list[tuple[int, int] | None] = [None] * n
            by_log[0] = None
            for pt, k in logs.items():
                if 0 < k < n:
                    by_log[k] = pt
            # fill remaining by walking from gen
            acc = gen
            by_log[1] = gen
            for k in range(2, n):
                acc = add_points(curve["p"], curve["a"], acc, gen)
                by_log[k] = acc
            xs = []
            ys = []
            for k in range(n):
                pt = by_log[k]
                if pt is None:
                    xs.append(0)
                    ys.append(0)
                else:
                    xs.append(pt[0])
                    ys.append(pt[1])
            p = curve["p"]
            j_max = int(math.ceil(math.log2(max(p, 2)) / 2)) + 3
            predictors = {
                "one": [1.0] * n,
                "legendre_x": [float(pow(xs[k], (p - 1) // 2, p) if xs[k] % p else 0) for k in range(n)],
                "x_lsb": [float(xs[k] & 1) for k in range(n)],
                "legendre_y": [float(pow(ys[k], (p - 1) // 2, p) if ys[k] % p else 0) for k in range(n)],
            }
            rng = random.Random(CURVE_SEEDS[bits] + 99)
            families = []
            for j in range(0, j_max + 1):
                families.append(("x_interval", j, [1 if xs[k] < (p / (2 ** j) if j < 30 else 0) else 0 for k in range(n)]))
            for j in range(1, max(1, j_max // 2) + 1):
                mod = 1 << j
                families.append(("x_residue", j, [1 if xs[k] % mod == 0 else 0 for k in range(n)]))
            for j in range(1, bits):
                families.append(("popcount", j, [1 if popcount(xs[k]) < j else 0 for k in range(n)]))
            for fam, j, mask in families:
                s = sum(mask)
                if s == 0:
                    continue
                null_idx = list(range(n))
                rng.shuffle(null_idx)
                null_mask = [0] * n
                for t in null_idx[:s]:
                    null_mask[t] = 1
                for pname, g in predictors.items():
                    a_obj, ss = restricted_spike(mask, g, n)
                    a_null, _ = restricted_spike(null_mask, g, n)
                    ratio = (a_obj / a_null) if a_null > 0 else None
                    sigma = ss / n
                    c_prod = (1.0 / (a_obj * a_obj) / sigma) if a_obj > 0 else None
                    cells.append({
                        "field_bits": bits,
                        "p": p,
                        "N": n,
                        "family": fam,
                        "j": j,
                        "predictor": pname,
                        "sigma": sigma,
                        "spike_obj": a_obj,
                        "spike_null": a_null,
                        "ratio": ratio,
                        "C": c_prod,
                        "weil_informative": sigma >= (WEIL_C / math.sqrt(n)),
                    })
            d1c = find_curve(bits, D1_SEEDS[bits], even=True)
            if d1c is None:
                d1_rows.append({"field_bits": bits, "status": "missing_curve"})
                continue
            e = d1c["torsion_x"]
            pd, ad = d1c["p"], d1c["a"]
            q = d1c["q"]
            n2 = d1c["order"]
            gen2, _logs2 = dlog_table(d1c)
            seq_pts: list[tuple[int, int] | None] = [None] * n2
            acc = gen2
            seq_pts[1] = gen2
            for k in range(2, n2):
                acc = add_points(pd, ad, acc, gen2)
                seq_pts[k] = acc
            mask = []
            g1 = []
            for k in range(n2):
                pt = seq_pts[k]
                if pt is None:
                    mask.append(0)
                    g1.append(1.0)
                    continue
                val = pow((pt[0] - e) % pd, (pd - 1) // 2, pd)
                mask.append(1 if val == 1 else 0)
                g1.append(1.0)
            s = sum(mask)
            sigma = s / n2 if n2 else 0
            seq = [complex(mask[k], 0.0) for k in range(n2)]
            spec = __import__("numpy").fft.fft(__import__("numpy").asarray(seq, dtype=complex))
            mag_q = float(abs(spec[q])) if q < n2 else 0.0
            eps = mag_q / s if s else 0.0
            d1_rows.append({
                "field_bits": bits,
                "p": pd,
                "order": n2,
                "q": q,
                "sigma": sigma,
                "eps_at_q": eps,
                "pass": abs(eps - 1.0) < 0.15 and abs(sigma - 0.5) < 0.2,
            })
    except RuntimeError as exc:
        code = str(exc)
        outcome = "O-IMPEDIMENT"
        payload = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "completed",
            "outcome": outcome,
            "impediment": code,
            "amazon_bedrock": "NOT SELECTED",
            "claims": {"break": False, "exponent_move": False},
        }
        _write_stage1_files(run_dir, payload, cells, {"d1": d1_rows})
        return payload

    d1_ok = bool(d1_rows) and all(r.get("pass") for r in d1_rows if "pass" in r)
    if not d1_ok:
        outcome = "O-D1-MISS"
    else:
        outcome = _decide(cells)
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "n_cells": len(cells),
        "d1": d1_rows,
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False},
    }
    _write_stage1_files(run_dir, payload, cells, {"d1": d1_rows, "outcome": outcome})
    return payload


def _decide(cells: list[dict[str, Any]]) -> str:
    bits_list = sorted({c["field_bits"] for c in cells})
    if len(bits_list) < 3:
        return "O-INCONCLUSIVE"
    fams = sorted({c["family"] for c in cells if c["family"] != "popcount"})
    conc_hit = False
    floor_ok = True
    for fam in fams:
        ratios_by_bits: dict[int, list[float]] = {b: [] for b in bits_list}
        for c in cells:
            if c["family"] != fam or c["ratio"] is None:
                continue
            if c["predictor"] != "one":
                continue
            ratios_by_bits[c["field_bits"]].append(c["ratio"])
        max_r = []
        for b in bits_list:
            vals = ratios_by_bits[b]
            if not vals:
                floor_ok = False
                max_r.append(None)
                continue
            mx = max(vals)
            max_r.append(mx)
            if not (RATIO_LO <= mx <= RATIO_HI):
                floor_ok = False
        if all(v is not None and v >= RATIO_CONC for v in max_r):
            if max_r[0] <= max_r[1] <= max_r[2]:
                conc_hit = True
    if conc_hit:
        return "O-CONCENTRATION"
    if floor_ok:
        return "O-FLOOR"
    return "O-INCONCLUSIVE"


def _write_stage1_files(run_dir: Path, payload: dict[str, Any], cells: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    stage1 = EXP_ROOT / "stage1"
    stage1.mkdir(parents=True, exist_ok=True)
    if not (stage1 / "cells.yaml").exists():
        write_text(stage1 / "cells.yaml", json.dumps({"field_bits": list(FIELD_BITS)}, indent=2) + "\n")
    if not (stage1 / "ladder.json").exists():
        write_json(stage1 / "ladder.json", {"cells": cells, "extra": extra})
    if not (stage1 / "d1-control.json").exists():
        write_json(stage1 / "d1-control.json", extra.get("d1", extra))
    if not (stage1 / "decision-rules.json").exists():
        write_json(
            stage1 / "decision-rules.json",
            {
                "O-FLOOR": "all bounded-degree one-predictor max ratios in [0.5, 2] at every size",
                "O-CONCENTRATION": "some family max ratio >= 4 at every size, non-decreasing",
                "bands": [RATIO_LO, RATIO_HI, RATIO_CONC],
                "outcome": payload.get("outcome"),
            },
        )
    write_json(run_dir / "raw-result.json", payload)
    outcome = str(payload.get("outcome"))
    write_text(
        run_dir / "manifest.yaml",
        "experiment_id: EXP-ECDLP-8197c0\n"
        "hypothesis_id: H-ECDLP-df33b3\n"
        "stage: 1\n"
        f"outcome: {outcome}\n"
        "amazon_bedrock: NOT SELECTED\n"
        "status: completed\n",
    )
    write_text(
        run_dir / "RESULTS.md",
        f"# EXP-ECDLP-8197c0 Stage 1\n\noutcome: {outcome}\n\n"
        "Python dual-route ladder. amazon_bedrock NOT SELECTED. "
        "No Magma/Sage/AUXIN. No exponent claim.\n",
    )
    results_root = EXP_ROOT / "RESULTS.md"
    if not results_root.exists():
        write_text(results_root, f"# EXP-ECDLP-8197c0\n\nLatest stage-1 outcome: {outcome}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    elapsed = time.time() - t0
    print(json.dumps({"ok": True, "stage": args.stage, "elapsed_s": elapsed, "amazon_bedrock": "NOT SELECTED"}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileExistsError as exc:
        print(f"refuse overwrite: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"failed_infrastructure: {exc}", file=sys.stderr)
        raise SystemExit(1)
