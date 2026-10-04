#!/usr/bin/env python3
"""EXP-CERTBIN-0f4599 Stages 0-1 launcher (frozen contract v1).

Stage 0: Freeze E_0 / F_{2^19} cell, order checksum, two (V,W) seed pairs,
         factor-base cardinalities, twin C(B+2,3), planted-instrument probe.
Stage 1: Enumerate the unordered 3-multiset image; read exact rate(U),
         rate(W), planted rate(P); write RESULTS.md with one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. Toy n=19.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from combinadic import (  # noqa: E402
    XorShift64,
    c_agree,
    dim_intersection,
    random_basis,
    span_list,
)
from curve import Curve, encode_point  # noqa: E402
from gf2n import Field, is_irreducible  # noqa: E402

EXPERIMENT_ID = "EXP-CERTBIN-0f4599"
HYPOTHESIS_ID = "H-CERTBIN-a3d441"
APPROVED_BY = "DEC-20261003-f561a3"
EXP_ROOT = Path(__file__).resolve().parents[1]

N = 19
MODULUS = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1
EXPECTED_ORDER = 523492
M = 3
N_TARGETS = 200
SEED_A = 2026100319
SEED_B = 2026100320
P_CEIL_MIN = 1.0 / 64.0
MAX_ADDS = 10_000_000
NULL_LO, NULL_HI = 0.5, 2.0
SLICE_MIN = 4.0


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


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def count_points(E: Curve) -> int:
    total = 1
    for x in range(E.F.q):
        total += len(E.solve_ys(x))
    return total


def factor_base(E: Curve, xs: list[int], r: int) -> list[tuple[int, int]]:
    pts = []
    for P in E.affine_points_with_x_in(xs):
        if E.smul(r, P) is None:
            pts.append(P)
    return pts


def pick_cells(E: Curve, r: int) -> list[dict]:
    cells = []
    for seed, tag in ((SEED_A, "seed_a"), (SEED_B, "seed_b")):
        rng = XorShift64(seed)
        chosen = None
        attempts = []
        for ell in range(4, 9):
            for trial in range(8):
                basis_v = random_basis(N, ell, rng)
                basis_w = random_basis(N, ell, rng)
                dcap = dim_intersection(basis_v, basis_w, N)
                if dcap > 0:
                    attempts.append({"ell": ell, "trial": trial, "reject": "W_meets_V"})
                    continue
                xs_v = span_list(basis_v, N)
                xs_w = span_list(basis_w, N)
                fb = factor_base(E, xs_v, r)
                sw = factor_base(E, xs_w, r)
                B = len(fb)
                ca, cb, okc = c_agree(B, M)
                if not okc:
                    raise RuntimeError("twin C disagree")
                ratio = (ca / r) if r else 0.0
                rec = {
                    "ell": ell,
                    "trial": trial,
                    "B": B,
                    "C": ca,
                    "C_twin": cb,
                    "C_over_r": ratio,
                    "sw": len(sw),
                    "dim_cap": dcap,
                }
                if ratio >= P_CEIL_MIN and ca <= MAX_ADDS and B >= 1 and len(sw) >= 16:
                    rec["accepted"] = True
                    chosen = {
                        "tag": tag,
                        "seed": seed,
                        "ell": ell,
                        "basis_v": basis_v,
                        "basis_w": basis_w,
                        "B": B,
                        "C": ca,
                        "p_ceil": min(1.0, ratio),
                        "sw": len(sw),
                        "fb_encoded": [encode_point(P) for P in fb],
                        "sw_encoded": [encode_point(P) for P in sw],
                    }
                    attempts.append(rec)
                    break
                rec["accepted"] = False
                attempts.append(rec)
            if chosen is not None:
                break
        if chosen is None:
            raise RuntimeError(f"no admissible (V,W) for {tag}")
        chosen["attempts"] = attempts
        cells.append(chosen)
    return cells


def enumerate_image(E: Curve, fb: list[tuple[int, int]]) -> tuple[set[str], int]:
    image: set[str] = set()
    adds0 = E.additions
    B = len(fb)
    for i in range(B):
        for j in range(i, B):
            sij = E.add(fb[i], fb[j])
            for k in range(j, B):
                s = E.add(sij, fb[k])
                if s is not None:
                    image.add(encode_point(s))
    return image, E.additions - adds0


def parse_point(s: str) -> tuple[int, int] | None:
    if s == "O":
        return None
    a, b = s.split(",")
    return (int(a, 16), int(b, 16))


def rebuild_fb(encoded: list[str]) -> list[tuple[int, int]]:
    out = []
    for s in encoded:
        P = parse_point(s)
        if P is None:
            raise RuntimeError("O in factor base")
        out.append(P)
    return out


def planted_hits(E: Curve, fb: list[tuple[int, int]], image: set[str], rng: XorShift64, n: int) -> dict:
    B = len(fb)
    hits = 0
    misses = 0
    for _ in range(n):
        i = rng.u64() % B
        j = rng.u64() % B
        k = rng.u64() % B
        i, j, k = tuple(sorted((i, j, k)))
        s = E.add(E.add(fb[i], fb[j]), fb[k])
        key = encode_point(s)
        if key in image:
            hits += 1
        else:
            misses += 1
    return {"n": n, "hits": hits, "misses": misses, "rate": hits / n if n else 0.0}


def outcome_label(rows: list[dict], artifact: str | None, impediment: str | None) -> str:
    if impediment:
        return "O-IMPEDIMENT"
    if artifact:
        return "O-ARTIFACT"
    if not rows:
        return "O-ARTIFACT"
    ratios = [row["rate_W_over_rate_U"] for row in rows]
    p_ok = all(row["rate_P"] == 1.0 for row in rows)
    u_ok = all(abs(row["rate_U"] - row["image_over_r"]) < 1e-15 for row in rows)
    if not p_ok or not u_ok:
        return "O-ARTIFACT"
    if all(NULL_LO <= x <= NULL_HI for x in ratios):
        return "O-NULL"
    if all(x >= SLICE_MIN for x in ratios):
        return "O-SLICE"
    return "O-INCONCLUSIVE"


def stage0(run_dir: Path) -> dict:
    irr, irr_details = is_irreducible(MODULUS)
    if not irr:
        raise RuntimeError(f"modulus not irreducible: {irr_details}")
    F = Field(N, MODULUS)
    twin_mul_ok = True
    rng = XorShift64(0xC0FFEE19)
    for _ in range(64):
        a, b = rng.bits(N), rng.bits(N)
        if F.mul_school(a, b) != F.mul_expand(a, b):
            twin_mul_ok = False
            break
    E = Curve(F)
    order = count_points(E)
    if order != EXPECTED_ORDER:
        raise RuntimeError(f"order {order} != expected {EXPECTED_ORDER}")
    if order % 4 != 0:
        raise RuntimeError("order not divisible by 4")
    r = order // 4
    if not is_probable_prime(r):
        raise RuntimeError(f"r={r} not prime")
    pts = E.affine_points_with_x_in([1, 2, 3, 4, 5])
    twin_add_ok = True
    if len(pts) >= 2:
        a = E.add_a(pts[0], pts[1])
        b = E.add_b(pts[0], pts[1])
        twin_add_ok = a == b
    cells = pick_cells(E, r)
    probe = cells[0]
    fb0 = rebuild_fb(probe["fb_encoded"])
    s = E.add(E.add(fb0[0], fb0[0]), fb0[0])
    planted_probe_on_curve = E.on_curve(s)
    torsion_ceil = min(1.0, cells[0]["C"] / 4.0)
    pred = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "n": N,
        "m": M,
        "modulus": hex(MODULUS),
        "order": order,
        "r": r,
        "p_ceil_min": P_CEIL_MIN,
        "null_band": [NULL_LO, NULL_HI],
        "slice_min": SLICE_MIN,
        "n_targets": N_TARGETS,
        "seeds": [SEED_A, SEED_B],
        "prediction_rate_U": "|image|/r (exact census)",
        "prediction_rate_P": 1.0,
        "prediction_rate_W_over_U_null": [NULL_LO, NULL_HI],
        "prediction_rate_W_over_U_slice": SLICE_MIN,
        "birthday_b": "1 + Theta(C/r) at C <= r/64",
        "torsion_nearby_N": 4,
        "torsion_ceiling_seed_a": torsion_ceil,
        "amazon_bedrock": "NOT_USED",
    }
    curve = {
        "equation": "y^2 + xy = x^3 + 1",
        "n": N,
        "modulus": hex(MODULUS),
        "irreducible": True,
        "order": order,
        "r": r,
        "cofactor": 4,
        "amazon_bedrock": "NOT_USED",
    }
    cells_out = []
    for c in cells:
        cells_out.append(
            {
                "tag": c["tag"],
                "seed": c["seed"],
                "ell": c["ell"],
                "basis_v": c["basis_v"],
                "basis_w": c["basis_w"],
                "B": c["B"],
                "C": c["C"],
                "p_ceil": c["p_ceil"],
                "sw": c["sw"],
                "fb_encoded": c["fb_encoded"],
                "sw_encoded": c["sw_encoded"],
                "attempts": c["attempts"],
            }
        )
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "curve.json", curve)
    write_json(EXP_ROOT / "stage0" / "cells.json", {"cells": cells_out})
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": "O-STAGE0-OK",
        "twin_mul_ok": twin_mul_ok,
        "twin_add_ok": twin_add_ok,
        "order": order,
        "r": r,
        "planted_probe_on_curve": planted_probe_on_curve,
        "cells": [
            {"tag": c["tag"], "B": c["B"], "C": c["C"], "p_ceil": c["p_ceil"], "ell": c["ell"]}
            for c in cells
        ],
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT_USED",
    }
    if not (twin_mul_ok and twin_add_ok and planted_probe_on_curve):
        raw["outcome"] = "O-ARTIFACT"
        raw["artifact"] = "stage0 twin or planted probe failed"
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": raw["outcome"],
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def stage1(run_dir: Path) -> dict:
    cells_path = EXP_ROOT / "stage0" / "cells.json"
    curve_path = EXP_ROOT / "stage0" / "curve.json"
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not (cells_path.is_file() and curve_path.is_file() and pred_path.is_file()):
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "impediment": "Stage-0 freeze missing",
            "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "outcome": "O-IMPEDIMENT", "amazon_bedrock": "NOT_USED"},
        )
        return raw
    cells = json.loads(cells_path.read_text())["cells"]
    curve = json.loads(curve_path.read_text())
    F = Field(N, int(curve["modulus"], 16))
    E = Curve(F)
    r = int(curve["r"])
    rows = []
    artifact = None
    for c in cells:
        fb = rebuild_fb(c["fb_encoded"])
        sw = rebuild_fb(c["sw_encoded"])
        if len(fb) != c["B"]:
            artifact = "B mismatch vs frozen cell"
            break
        ca, cb, okc = c_agree(len(fb), M)
        if not okc or ca != c["C"]:
            artifact = "C twin/freeze mismatch"
            break
        image, enum_adds = enumerate_image(E, fb)
        image_over_r = len(image) / r
        sw_set = {encode_point(P) for P in sw}
        inter = len(image & sw_set)
        rate_w = inter / len(sw_set) if sw_set else 0.0
        rate_u = image_over_r
        rng = XorShift64(c["seed"] ^ 0xA5A5A5A5)
        plant = planted_hits(E, fb, image, rng, N_TARGETS)
        if plant["rate"] != 1.0:
            artifact = f"rate(P)<1 on {c['tag']}"
        ratio = (rate_w / rate_u) if rate_u > 0 else float("inf")
        b = (ca / len(image)) if image else float("inf")
        L = (r.bit_length() - 1) - (max(len(image), 1).bit_length() - 1)
        rows.append(
            {
                "tag": c["tag"],
                "seed": c["seed"],
                "ell": c["ell"],
                "B": c["B"],
                "C": ca,
                "C_twin": cb,
                "r": r,
                "image": len(image),
                "image_over_r": image_over_r,
                "rate_U": rate_u,
                "rate_W": rate_w,
                "rate_W_over_rate_U": ratio,
                "rate_P": plant["rate"],
                "planted": plant,
                "sw": len(sw_set),
                "image_cap_sw": inter,
                "branching_b": b,
                "L_bits_floor": L,
                "enum_additions": enum_adds,
                "additions_charged": E.additions,
            }
        )
    label = outcome_label(rows, artifact, None)
    write_json(EXP_ROOT / "stage1" / "panels.json", {"rows": rows, "outcome": label})
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "null_band": [NULL_LO, NULL_HI],
            "slice_min": SLICE_MIN,
            "laws": ["U", "P", "W"],
            "planted_must_hit": True,
            "W_independent_of_V": True,
            "two_seeds": [SEED_A, SEED_B],
            "torsion_nearby_N": 4,
            "rows": [
                {
                    "tag": row["tag"],
                    "rate_U": row["rate_U"],
                    "rate_P": row["rate_P"],
                    "rate_W": row["rate_W"],
                    "ratio": row["rate_W_over_rate_U"],
                }
                for row in rows
            ],
        },
    )
    md = [
        f"# RESULTS — {EXPERIMENT_ID}",
        "",
        f"Hypothesis: {HYPOTHESIS_ID}",
        f"Approved by: {APPROVED_BY}",
        f"Outcome: **{label}**",
        "",
        "Claim tier: toy n=19. No ECDLP solve. No n>=131 exponent.",
        "Amazon Bedrock: NOT_USED.",
        "",
        "| seed | B | C | |image| | rate(U) | rate(P) | rate(W) | W/U | b |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row['tag']} | {row['B']} | {row['C']} | {row['image']} | "
            f"{row['rate_U']:.6g} | {row['rate_P']:.3f} | {row['rate_W']:.6g} | "
            f"{row['rate_W_over_rate_U']:.4g} | {row['branching_b']:.4g} |"
        )
    md.append("")
    md.append("Exactly one O-* label. O-NULL = E-NULL; O-SLICE = E-SLICE.")
    md.append("O-ARTIFACT / O-IMPEDIMENT are not mathematical negatives of the rates.")
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(md) + "\n")
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": label,
        "artifact": artifact,
        "rows": rows,
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": label,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        if args.stage == 0:
            stage0(run_dir)
        else:
            stage1(run_dir)
    except FileExistsError:
        raise
    except Exception as exc:  # noqa: BLE001
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": args.stage,
            "outcome": "O-IMPEDIMENT",
            "impediment": str(exc),
            "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
            "amazon_bedrock": "NOT_USED",
        }
        raw_path = run_dir / "raw-result.json"
        if not raw_path.exists():
            write_json(raw_path, raw)
        man_path = run_dir / "manifest.yaml"
        if not man_path.exists():
            write_yaml_manifest(
                man_path,
                {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": args.stage,
                    "outcome": "O-IMPEDIMENT",
                    "amazon_bedrock": "NOT_USED",
                },
            )
        print(f"IMPEDIMENT: {exc}", file=sys.stderr)
        return 1
    print(f"stage {args.stage} done in {time.time() - t0:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
