#!/usr/bin/env python3
"""EXP-BINSTD-cec99c Stages 0-1: unique-orbit yield after Frob×neg collapse.

In-Python Koblitz arithmetic + dual orbit meters (orbit_a vs orbit_b).
Not a Magma/Sage presence detector. No ECDLP solve. No n>=131.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import Curve  # noqa: E402
from gf2 import MODULI, field_for  # noqa: E402
from orbit_a import canonical_a, unique_orbit_count_a  # noqa: E402
from orbit_b import canonical_b, unique_orbit_count_b  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-cec99c"
HYPOTHESIS_ID = "H-BINSTD-d09592"
APPROVED_BY = "DEC-20261003-be1d8e"
EXP_ROOT = Path(__file__).resolve().parents[1]

CURVE_A = 1
CURVE_B = 1
ELL = 3
RHO_NUM, RHO_DEN = 1, 2
SURPLUS_MULTS = ((1, 1), (3, 2), (2, 1))
CATALOG_SEED = 2026100311
COLLECT_SEED = 2026100312
AUTHORIZED_STAGE1_N = (17,)
FREEZE_N = (17, 23, 31)
WALK_MAX_LEN = 8
WALK_TRIES_CAP = 4000


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


def poly_x_span(n: int, ell: int) -> list[int]:
    # V = span{ t^0, ..., t^{ell-1} } as bitmasks in F_2^n
    out = []
    for mask in range(1 << ell):
        x = 0
        for j in range(ell):
            if mask & (1 << j):
                x ^= 1 << j
        out.append(x)
    return sorted(set(out))


def factor_base(curve: Curve, xs: list[int]) -> list[tuple[int, int]]:
    pts: list[tuple[int, int]] = []
    seen = set()
    for x in xs:
        if x == 0:
            continue
        P = curve.lift_x(x)
        if P is None:
            continue
        for Q in (P, curve.neg(P)):
            if Q is None or Q in seen:
                continue
            if not curve.on_curve(Q):
                raise RuntimeError("lift not on curve")
            seen.add(Q)
            pts.append(Q)
    return pts


def collect_s3(curve: Curve, fb: list[tuple[int, int]]) -> list[tuple[tuple[int, int], ...]]:
    """All F_2-linear FB subsets that sum to O, plus S_3 triples."""
    import itertools

    rels = []
    seen = set()

    def add_rel(pts):
        rel = tuple(sorted(set(pts)))
        if len(rel) < 2 or rel in seen:
            return
        seen.add(rel)
        rels.append(rel)

    for P in fb:
        add_rel((P, curve.neg(P)))
    m = len(fb)
    for k in range(2, min(m, 6) + 1):
        for comb in itertools.combinations(fb, k):
            acc = None
            for P in comb:
                acc = curve.add(acc, P)
            if acc is None:
                add_rel(comb)
    fb_set = set(fb)
    for i in range(m):
        for j in range(i + 1, m):
            S = curve.add(fb[i], fb[j])
            if S is None:
                continue
            R = curve.neg(S)
            if R in fb_set:
                add_rel((fb[i], fb[j], R))
    return rels


def collect_walks(
    curve: Curve,
    fb: list[tuple[int, int]],
    need: int,
    rng: random.Random,
    existing: list[tuple[tuple[int, int], ...]],
) -> list[tuple[tuple[int, int], ...]]:
    rels = list(existing)
    seen = set(existing)
    tries = 0
    while len(rels) < need and tries < WALK_TRIES_CAP:
        tries += 1
        acc = None
        support: list[tuple[int, int]] = []
        length = rng.randint(3, WALK_MAX_LEN)
        for _ in range(length):
            Q = fb[rng.randrange(len(fb))]
            acc = curve.add(acc, Q)
            support.append(Q)
        if acc is not None:
            continue
        rel = tuple(sorted(set(support)))
        if len(rel) < 2 or rel in seen:
            continue
        seen.add(rel)
        rels.append(rel)
    return rels


def identity_unique_count(rels) -> int:
    return len({tuple(sorted(r)) for r in rels})


def freeze_v_rows() -> list[dict[str, Any]]:
    rows = []
    for n in FREEZE_N:
        F = field_for(n)
        curve = Curve(F, CURVE_A, CURVE_B)
        xs = poly_x_span(n, ELL)
        fb = factor_base(curve, xs)
        rows.append(
            {
                "n": n,
                "ell": ELL,
                "curve_A": CURVE_A,
                "curve_B": CURVE_B,
                "modulus": MODULI[n],
                "v_xcoords": xs,
                "fb_size": len(fb),
                "fb_points": [{"x": p[0], "y": p[1]} for p in fb],
            }
        )
    return rows


def dual_ok(F, n: int, rels) -> bool:
    if not rels:
        return True
    ca = [canonical_a(F, n, r) for r in rels]
    cb = [canonical_b(F, n, r) for r in rels]
    return ca == cb and unique_orbit_count_a(F, n, rels) == unique_orbit_count_b(F, n, rels)


def synthetic_conjugate_probe(F, n: int, seed_rel) -> dict[str, Any]:
    from orbit_a import apply_ks

    orbit = []
    for k in range(min(4, n)):
        mapped = tuple(sorted(apply_ks(F, p, k, False) for p in seed_rel))
        orbit.append(mapped)
    ua = unique_orbit_count_a(F, n, orbit)
    ub = unique_orbit_count_b(F, n, orbit)
    return {
        "raw": len(orbit),
        "unique_a": ua,
        "unique_b": ub,
        "twins_agree": ua == ub,
        "expected_unique": 1,
        "pass": ua == ub == 1,
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    rows = freeze_v_rows()
    n17 = next(r for r in rows if r["n"] == 17)
    F = field_for(17)
    curve = Curve(F, CURVE_A, CURVE_B)
    fb = [(p["x"], p["y"]) for p in n17["fb_points"]]
    if len(fb) < 3:
        raise RuntimeError("n=17 factor base too small for S3 probe")
    seed_rel = tuple(sorted(fb[:3]))
    probe = synthetic_conjugate_probe(F, 17, seed_rel)
    null_rels = [tuple(sorted(fb[i : i + 2])) for i in range(0, min(6, len(fb) - 1))]
    null_r = identity_unique_count(null_rels) / max(1, len(null_rels))
    twins = dual_ok(F, 17, [seed_rel] + null_rels)
    pred = {
        "schema": "EXP-BINSTD-cec99c.preregistered-predictions.v1",
        "rho": {"numer": RHO_NUM, "denom": RHO_DEN},
        "surplus_multipliers": [{"numer": a, "denom": b} for a, b in SURPLUS_MULTS],
        "catalog_seed": CATALOG_SEED,
        "collect_seed": COLLECT_SEED,
        "ell": ELL,
        "authorized_stage1_n": list(AUTHORIZED_STAGE1_N),
        "freeze_n": list(FREEZE_N),
        "orbit_group": "frobenius_times_negation",
        "no_n_object_keys": True,
        "amazon_bedrock": "NOT SELECTED",
    }
    catalog = {
        "schema": "EXP-BINSTD-cec99c.v-catalog.v1",
        "cells": rows,
        "note": "list rows with integer n; never n-as-object-key",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", pred)
    write_json(EXP_ROOT / "stage0" / "v-catalog.json", catalog)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": "O-STAGE0-OK" if probe["pass"] and twins and null_r == 1.0 else "O-ARTIFACT",
        "twin_ok": twins,
        "conjugate_probe": probe,
        "null_identity_R": null_r,
        "fb_size_n17": n17["fb_size"],
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "outcome": raw["outcome"],
            "valid": raw["outcome"] == "O-STAGE0-OK",
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    cat_path = EXP_ROOT / "stage0" / "v-catalog.json"
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not cat_path.is_file() or not pred_path.is_file():
        raise FileNotFoundError("Stage 0 freeze missing")
    catalog = json.loads(cat_path.read_text(encoding="utf-8"))
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    if not isinstance(catalog.get("cells"), list):
        raise RuntimeError("v-catalog cells must be a list of rows")
    row = next(r for r in catalog["cells"] if r.get("n") == 17)
    n = int(row["n"])
    F = field_for(n)
    curve = Curve(F, int(row["curve_A"]), int(row["curve_B"]))
    fb = [(int(p["x"]), int(p["y"])) for p in row["fb_points"]]
    fb_size = len(fb)
    rng = random.Random(COLLECT_SEED)
    s3 = collect_s3(curve, fb)
    panels = []
    twin_ok = True
    surplus_met = True
    band_ok = True
    for sm in pred["surplus_multipliers"]:
        need = (int(sm["numer"]) * fb_size) // int(sm["denom"])
        if need < 1:
            need = 1
        bag = collect_walks(curve, fb, need, rng, s3)
        raw_n = len(bag)
        if raw_n < need:
            surplus_met = False
        used = bag[:need] if raw_n >= need else bag
        ua = unique_orbit_count_a(F, n, used)
        ub = unique_orbit_count_b(F, n, used)
        if ua != ub or not dual_ok(F, n, used):
            twin_ok = False
        R_num, R_den = ua, max(1, len(used))
        # R >= rho iff ua * rho_den >= len(used) * rho_num
        holds = ua * RHO_DEN >= len(used) * RHO_NUM if used else False
        if used and not holds:
            band_ok = False
        null_u = identity_unique_count(used)
        panels.append(
            {
                "n": n,
                "ell": ELL,
                "surplus_numer": int(sm["numer"]),
                "surplus_denom": int(sm["denom"]),
                "need_raw": need,
                "raw": len(used),
                "unique_a": ua,
                "unique_b": ub,
                "R_numer": R_num,
                "R_den": R_den,
                "rho_numer": RHO_NUM,
                "rho_den": RHO_DEN,
                "band_holds": holds,
                "null_identity_unique": null_u,
                "null_R_is_one": null_u == len(used) and len(used) > 0,
                "fb_size": fb_size,
            }
        )
    if not twin_ok:
        outcome = "O-ARTIFACT"
    elif not surplus_met:
        outcome = "O-INCONCLUSIVE"
    elif not all(p["null_R_is_one"] for p in panels):
        outcome = "O-ARTIFACT"
    elif band_ok:
        outcome = "O-SUPPORT"
    else:
        outcome = "O-FAIL-BAND"
    write_json(EXP_ROOT / "stage1" / "panels.json", {"cells": panels})
    write_json(
        EXP_ROOT / "stage1" / "control-table.json",
        {
            "cells": [
                {
                    "n": p["n"],
                    "surplus_numer": p["surplus_numer"],
                    "surplus_denom": p["surplus_denom"],
                    "null_R_is_one": p["null_R_is_one"],
                    "twins_agree": p["unique_a"] == p["unique_b"],
                }
                for p in panels
            ]
        },
    )
    results = "\n".join(
        [
            f"# EXP-BINSTD-cec99c Stage 1 RESULTS",
            "",
            f"outcome: {outcome}",
            f"hypothesis: {HYPOTHESIS_ID}",
            f"approved_by: {APPROVED_BY}",
            "",
            "Exactly one O-* label. Toy unique-orbit retention only.",
            "No ECDLP solve. No exponent. No n>=131. No Magma/Sage/AUXIN/Bedrock.",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "twin_ok": twin_ok,
        "surplus_met": surplus_met,
        "band_ok": band_ok,
        "s3_count": len(s3),
        "claims": {"break": False, "exponent_move": False, "n_ge_131": False},
        "amazon_bedrock": "NOT SELECTED",
        "magma_sage_auxin": "NOT USED",
        "wall_clock_seconds": time.time() - t0,
        "panel_count": len(panels),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "valid": outcome in {"O-SUPPORT", "O-FAIL-BAND", "O-INCONCLUSIVE", "O-ARTIFACT", "O-IMPEDIMENT"},
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if "bedrock" in args.trial_plan.lower() or "bedrock" in str(run_dir).lower():
        print("Bedrock prohibited", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            raw = stage0(run_dir)
        else:
            raw = stage1(run_dir)
    except FileExistsError as exc:
        print(f"IMPEDIMENT overwrite: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"stage": args.stage, "outcome": raw.get("outcome")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
