#!/usr/bin/env python3
"""EXP-BINSTD-ce4668 Stages 0-1: poly vs normal usable_dimensions basis-swap.

Stdlib-only. Reimplements Part-1 ord_n(2) / usable_dimensions from
EXP-BINSTD-178742 part1_surface.py and scores matched-dim geometric-
progression spans under polynomial vs normal ambient bases.

Stage 0: freeze P_n pair seeds, dim bands, predicate code hash, predictions.
Stage 1: n=17 panel (>=20 pairs); median abs diff of usable readout;
         shuffle-null control; write RESULTS.md with exactly one O-*.

No Magma/Sage/AUXIN/Bedrock. No break / exponent / n>=131 transfer.
No Stage 2 (n=23,31) under this card.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

EXPERIMENT_ID = "EXP-BINSTD-ce4668"
HYPOTHESIS_ID = "H-BINSTD-533de4"
APPROVED_BY = "DEC-20261003-d10361"
SEED = 20261003880180
TOY_N = (17, 23, 31)
STAGE1_N = 17
MIN_PAIRS = 20
OUTCOMES = ("O-DIVERGE", "O-EQUIVALENT", "O-ARTIFACT", "O-IMPEDIMENT")
EXP_ROOT = Path(__file__).resolve().parents[1]

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode())

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")

# ---- Part-1 predicates (copied semantics from part1_surface.py) ----

def ord_n_of_2_by_iteration(n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")

def _positive_divisors(m: int) -> List[int]:
    divs: List[int] = []
    i = 1
    while i * i <= m:
        if m % i == 0:
            divs.append(i)
            if i * i != m:
                divs.append(m // i)
        i += 1
    divs.sort()
    return divs

def ord_n_of_2_by_divisor_test(n: int) -> int:
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be an odd integer > 2")
    for d in _positive_divisors(n - 1):
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"no divisor d of {n - 1} with 2^d ≡ 1 mod {n}")

def _prime_factors(m: int) -> List[int]:
    if m <= 1:
        return []
    factors: List[int] = []
    x = m
    p = 2
    while p * p <= x:
        if x % p == 0:
            factors.append(p)
            while x % p == 0:
                x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        factors.append(x)
    return factors

def verify_ord_n_2(n: int, d: int) -> bool:
    if d <= 0 or pow(2, d, n) != 1:
        return False
    for p in _prime_factors(d):
        if pow(2, d // p, n) == 1:
            return False
    return True

def stable_dimensions_from_ord(n: int, d: int) -> Dict[str, Any]:
    if n <= 1 or (n - 1) % d != 0:
        raise ValueError(f"d={d} does not divide n-1={n - 1}")
    f = (n - 1) // d
    dims: List[int] = []
    for b in range(f + 1):
        dims.append(b * d)
        dims.append(b * d + 1)
    usable = [x for x in dims if x not in (0, 1, n - 1, n)]
    return {"factors_of_Phi_n": {"count": f, "degree": d}, "stable_dimensions": dims, "usable_dimensions": usable}

def score_ord_row(n: int) -> Dict[str, Any]:
    by_iter = ord_n_of_2_by_iteration(n)
    by_div = ord_n_of_2_by_divisor_test(n)
    routes_agree = by_iter == by_div
    d = by_div if routes_agree else by_iter
    verified = verify_ord_n_2(n, d) if routes_agree else False
    stab = stable_dimensions_from_ord(n, d) if routes_agree and (n - 1) % d == 0 else None
    row: Dict[str, Any] = {"n": n, "ord_n_2_iteration": by_iter, "ord_n_2_divisor_test": by_div, "routes_agree": routes_agree, "ord_n_2": d if routes_agree else None, "order_verified": verified}
    if stab is not None:
        row["factors_of_Phi_n"] = stab["factors_of_Phi_n"]
        row["stable_dimensions"] = stab["stable_dimensions"]
        row["usable_dimensions"] = stab["usable_dimensions"]
        row["usable_cardinality"] = len(stab["usable_dimensions"])
    row["ok"] = bool(routes_agree and verified and stab is not None)
    return row

def predicate_source_hash() -> str:
    src = Path(__file__).read_text(encoding="utf-8")
    marker = "# ---- Part-1 predicates"
    end = "# ---- GF(2^n) basis arithmetic"
    i = src.find(marker); j = src.find(end)
    if i < 0 or j < 0 or j <= i:
        raise RuntimeError("predicate block markers missing")
    return sha256_bytes(src[i:j].encode())

# ---- GF(2^n) basis arithmetic ----

def gf2_rank(rows: List[int], n: int) -> int:
    mats = list(rows); rank = 0
    for col in range(n):
        pivot = None
        for r in range(rank, len(mats)):
            if (mats[r] >> col) & 1:
                pivot = r; break
        if pivot is None:
            continue
        mats[rank], mats[pivot] = mats[pivot], mats[rank]
        for r in range(len(mats)):
            if r != rank and ((mats[r] >> col) & 1):
                mats[r] ^= mats[rank]
        rank += 1
    return rank

def _poly_mod(a: int, mod: int) -> int:
    mdeg = mod.bit_length() - 1
    while a.bit_length() - 1 >= mdeg:
        a ^= mod << ((a.bit_length() - 1) - mdeg)
    return a

def poly_mul_mod(a: int, b: int, mod: int) -> int:
    res = 0; a = _poly_mod(a, mod)
    while b:
        if b & 1: res ^= a
        b >>= 1; a <<= 1; a = _poly_mod(a, mod)
    return _poly_mod(res, mod)

IRRED: Dict[int, int] = {17: (1 << 17) | (1 << 3) | 1, 23: (1 << 23) | (1 << 5) | 1, 31: (1 << 31) | (1 << 3) | 1}

def field_square(x: int, n: int) -> int:
    return poly_mul_mod(x, x, IRRED[n])

def normal_basis_coords(elem_poly: int, n: int, normal_gen: int) -> int:
    cols: List[int] = []; b = normal_gen & ((1 << n) - 1); cur = b
    for _ in range(n):
        cols.append(cur); cur = field_square(cur, n)
    rows = [0] * n
    for j, col in enumerate(cols):
        for i in range(n):
            if (col >> i) & 1: rows[i] |= 1 << j
    aug = [rows[i] | (((elem_poly >> i) & 1) << n) for i in range(n)]
    r = 0; pivots = [-1] * n
    for col in range(n):
        pivot = None
        for rr in range(r, n):
            if (aug[rr] >> col) & 1: pivot = rr; break
        if pivot is None: continue
        aug[r], aug[pivot] = aug[pivot], aug[r]
        for rr in range(n):
            if rr != r and ((aug[rr] >> col) & 1): aug[rr] ^= aug[r]
        pivots[col] = r; r += 1
    if r < n: return -1
    sol = 0
    for col in range(n):
        pr = pivots[col]
        if pr >= 0 and ((aug[pr] >> n) & 1): sol |= 1 << col
    return sol

def find_normal_generator(n: int, seed: int) -> int:
    rng = random.Random(seed ^ (n * 0x9E3779B9))
    for _ in range(10000):
        cand = rng.randrange(1, 1 << n)
        if normal_basis_coords(1, n, cand) >= 0:
            if all(normal_basis_coords(1 << e, n, cand) >= 0 for e in range(n)):
                return cand
    raise RuntimeError(f"no normal generator found for n={n}")

def gp_span_poly(n: int, alpha: int, ell: int) -> List[int]:
    gens: List[int] = []; cur = 1
    for _ in range(ell):
        gens.append(cur & ((1 << n) - 1)); cur = poly_mul_mod(cur, alpha, IRRED[n])
    return gens

def gp_span_normal_pattern(n: int, alpha_bits: int, ell: int, beta: int) -> List[int]:
    gens_poly: List[int] = []; cur = 1
    for _ in range(ell):
        code = cur & ((1 << n) - 1); acc = 0; b = beta
        for i in range(n):
            if (code >> i) & 1: acc ^= b
            b = field_square(b, n)
        gens_poly.append(acc); cur = poly_mul_mod(cur, alpha_bits, IRRED[n])
    return gens_poly

def is_frobenius_stable(gens: Sequence[int], n: int) -> bool:
    base = list(gens); r0 = gf2_rank(base, n)
    extended = list(base) + [field_square(g, n) for g in base]
    return gf2_rank(extended, n) == r0

def usable_readout(gens: Sequence[int], n: int, usable: Sequence[int]) -> int:
    dim = gf2_rank(list(gens), n)
    if dim not in set(usable): return 0
    if not is_frobenius_stable(gens, n): return 0
    return len(usable)

def dim_band(n: int) -> Tuple[int, int]:
    return n // 8, n // 4

def build_pairs_for_n(n: int, beta: int, seed: int, count: int) -> List[Dict[str, Any]]:
    lo, hi = dim_band(n); rng = random.Random(seed ^ n)
    usable = score_ord_row(n)["usable_dimensions"]; pairs: List[Dict[str, Any]] = []; attempts = 0
    while len(pairs) < count and attempts < count * 200:
        attempts += 1; ell = rng.randint(lo, hi); alpha = rng.randrange(2, 1 << n)
        if alpha == 0: continue
        v_poly = gp_span_poly(n, alpha, ell)
        if gf2_rank(v_poly, n) != ell: continue
        v_norm = gp_span_normal_pattern(n, alpha, ell, beta)
        if gf2_rank(v_norm, n) != ell: continue
        up = usable_readout(v_poly, n, usable); un = usable_readout(v_norm, n, usable)
        pairs.append({"n": n, "ell": ell, "alpha": alpha, "usable_card_poly": up, "usable_card_normal": un, "abs_diff": abs(up - un), "tau_stable_poly": is_frobenius_stable(v_poly, n), "tau_stable_normal": is_frobenius_stable(v_norm, n), "part1_usable": list(usable), "part1_usable_card": len(usable)})
    if len(pairs) < count:
        raise RuntimeError(f"only built {len(pairs)}/{count} pairs for n={n}")
    return pairs

def stage0(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"; pred_hash = predicate_source_hash()
    betas = {str(n): find_normal_generator(n, SEED) for n in TOY_N}
    census = {str(n): score_ord_row(n) for n in TOY_N}
    for n, row in census.items():
        if not row["ok"]: raise RuntimeError(f"Part-1 census failed for n={n}")
    pair_plan = {"seed": SEED, "min_pairs_per_n": MIN_PAIRS, "toy_n": list(TOY_N), "stage1_n": STAGE1_N, "dim_band_rule": "ell in [floor(n/8), floor(n/4)]", "pair_construction": "V_poly = GP in poly basis; V_normal = same α-pattern via normal generator β", "usable_readout_definition": "|U(n)| if τ-stable and dim(V) in U(n), else 0", "normal_generators_poly_coords": betas, "irreducible_poly_bitmasks": {str(k): v for k, v in IRRED.items()}}
    predictions = {"heuristic": "HEUR-BINSTD-880180-H1", "primary_metric": "median_abs_diff_usable_dimensions_poly_vs_normal", "diverge_threshold": 1, "null": "shuffle pair labels; shuffle median must be < observed when observed >= 1", "frozen_before_stage1": True, "note": "Do not edit after any Stage-1 outcome."}
    h_plan = write_json(stage0_dir / "frozen-pair-plan.json", pair_plan)
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", predictions)
    h_census = write_json(stage0_dir / "part1-census.json", census)
    h_pin = write_json(stage0_dir / "predicate-pin.json", {"predicate_source_sha256": pred_hash, "source_file": "experiments/EXP-BINSTD-ce4668/implementation/run.py", "reference": "EXP-BINSTD-178742/implementation/typed/part1_surface.py"})
    result = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY, "stage": 0, "status": "completed_valid", "outcome": "S0-FREEZE-OK", "artifact_sha256": {"stage0/frozen-pair-plan.json": h_plan, "stage0/preregistered-predictions.json": h_pred, "stage0/part1-census.json": h_census, "stage0/predicate-pin.json": h_pin}, "predicate_source_sha256": pred_hash, "claims": {"break": False, "exponent_move": False}, "certificate": {"kind": "none"}, "amazon_bedrock": "NOT SELECTED", "recorded_at": utc_now()}
    write_json(run_dir / "raw-result.json", result)
    write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "stage": 0, "status": "completed_valid", "amazon_bedrock": "NOT SELECTED", "recorded_at": result["recorded_at"]})
    return result

def stage1(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"; stage1_dir = EXP_ROOT / "stage1"
    required = [stage0_dir / "frozen-pair-plan.json", stage0_dir / "preregistered-predictions.json", stage0_dir / "part1-census.json", stage0_dir / "predicate-pin.json"]
    if not all(p.is_file() for p in required):
        result = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "stage": 1, "status": "impediment", "outcome": "O-IMPEDIMENT", "reason": "Stage-0 freeze artifacts missing", "claims": {"break": False, "exponent_move": False}, "amazon_bedrock": "NOT SELECTED", "recorded_at": utc_now()}
        write_json(run_dir / "raw-result.json", result); write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "impediment", "amazon_bedrock": "NOT SELECTED"})
        write_text(EXP_ROOT / "RESULTS.md", "# RESULTS — EXP-BINSTD-ce4668\n\nLabel: **O-IMPEDIMENT**\n\nStage-0 freeze missing; no median claimed.\n"); return result
    pin = json.loads((stage0_dir / "predicate-pin.json").read_text())
    if pin.get("predicate_source_sha256") != predicate_source_hash():
        result = {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "artifact", "outcome": "O-ARTIFACT", "reason": "predicate hash drift vs Stage-0 pin", "claims": {"break": False, "exponent_move": False}, "amazon_bedrock": "NOT SELECTED", "recorded_at": utc_now()}
        write_json(run_dir / "raw-result.json", result); write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "stage": 1, "status": "artifact"})
        write_text(EXP_ROOT / "RESULTS.md", "# RESULTS — EXP-BINSTD-ce4668\n\nLabel: **O-ARTIFACT**\n\nPredicate source hash drifted after Stage-0 freeze.\n"); return result
    plan = json.loads((stage0_dir / "frozen-pair-plan.json").read_text())
    beta = int(plan["normal_generators_poly_coords"][str(STAGE1_N)])
    pairs = build_pairs_for_n(STAGE1_N, beta, plan["seed"], plan["min_pairs_per_n"])
    diffs = [p["abs_diff"] for p in pairs]; median_diff = float(statistics.median(diffs))
    rng = random.Random(plan["seed"] ^ 0xC0FFEE); shuffled = [p["usable_card_normal"] for p in pairs]; rng.shuffle(shuffled)
    shuffle_diffs = [abs(pairs[i]["usable_card_poly"] - shuffled[i]) for i in range(len(pairs))]; shuffle_median = float(statistics.median(shuffle_diffs))
    if median_diff >= 1:
        if shuffle_median >= median_diff: label, status, reason = "O-ARTIFACT", "artifact", "nonzero median but shuffle null does not drop"
        else: label, status, reason = "O-DIVERGE", "completed_valid", "median_abs_diff >= 1 with shuffle null below"
    else:
        label, status, reason = "O-EQUIVALENT", "completed_valid", "median_abs_diff == 0; bases equivalent for this predicate at n=17"
    panels = {"n": STAGE1_N, "pair_count": len(pairs), "median_abs_diff": median_diff, "shuffle_median": shuffle_median, "histogram_abs_diff": {str(k): diffs.count(k) for k in sorted(set(diffs))}, "pairs": pairs}
    controls = {"predicate_pin_ok": True, "min_pairs": plan["min_pairs_per_n"], "pairs_built": len(pairs), "shuffle_null": {"median": shuffle_median, "rule": "shuffle median < observed when observed >= 1"}, "repeatability_note": "Deterministic under frozen seed."}
    h_panels = write_json(stage1_dir / "panels.json", panels); h_ctl = write_json(stage1_dir / "control-table.json", controls)
    write_text(EXP_ROOT / "RESULTS.md", f"# RESULTS — EXP-BINSTD-ce4668\n\nLabel: **{label}**\n\n- hypothesis: {HYPOTHESIS_ID}\n- approved_by: {APPROVED_BY}\n- stage1_n: {STAGE1_N}\n- pair_count: {len(pairs)}\n- median_abs_diff: {median_diff}\n- shuffle_median: {shuffle_median}\n- reason: {reason}\n- claims: break=false, exponent_move=false\n- amazon_bedrock: NOT SELECTED\n- note: Stage 2 (n=23,31) not authorized under this card.\n")
    result = {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "approved_by": APPROVED_BY, "stage": 1, "status": status, "outcome": label, "reason": reason, "median_abs_diff": median_diff, "shuffle_median": shuffle_median, "pair_count": len(pairs), "artifact_sha256": {"stage1/panels.json": h_panels, "stage1/control-table.json": h_ctl}, "claims": {"break": False, "exponent_move": False}, "certificate": {"kind": "none"}, "amazon_bedrock": "NOT SELECTED", "recorded_at": utc_now()}
    write_json(run_dir / "raw-result.json", result)
    write_json(run_dir / "manifest.yaml", {"experiment_id": EXPERIMENT_ID, "hypothesis_id": HYPOTHESIS_ID, "stage": 1, "status": status, "outcome": label, "amazon_bedrock": "NOT SELECTED", "recorded_at": result["recorded_at"]})
    return result

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", type=str, required=True)
    ap.add_argument("--run-dir", type=str, required=True)
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir); run_dir.mkdir(parents=True, exist_ok=True)
    if not Path(args.trial_plan).is_file():
        print(f"missing trial plan: {args.trial_plan}", file=sys.stderr); return 2
    try:
        if args.stage == 0: stage0(run_dir)
        else: stage1(run_dir)
    except FileExistsError as exc:
        print(f"refuse overwrite: {exc}", file=sys.stderr); return 1
    except Exception as exc:
        err = {"experiment_id": EXPERIMENT_ID, "stage": args.stage, "status": "impediment", "outcome": "O-IMPEDIMENT", "reason": f"{type(exc).__name__}: {exc}", "claims": {"break": False, "exponent_move": False}, "amazon_bedrock": "NOT SELECTED", "recorded_at": utc_now()}
        raw = run_dir / "raw-result.json"
        if not raw.exists(): raw.write_text(json.dumps(err, indent=2, sort_keys=True) + "\n")
        man = run_dir / "manifest.yaml"
        if not man.exists(): man.write_text(json.dumps({"experiment_id": EXPERIMENT_ID, "status": "impediment"}, indent=2) + "\n")
        print(f"impediment: {exc}", file=sys.stderr); return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
