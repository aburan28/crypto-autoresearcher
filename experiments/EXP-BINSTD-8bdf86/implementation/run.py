#!/usr/bin/env python3
"""EXP-BINSTD-8bdf86 Stages 0-1: τ-closed vs matched-open FB relation yield.

Stdlib-only. Self-contained GF(2^n) arithmetic. No Magma/Sage/AUXIN/Bedrock.

Stage 0: freeze band 1.25, seeds, ℓ panel, τ-closure definition, solver pin,
         target count, preregistered predictions.
Stage 1: n=17, ℓ∈{3,4}. First certify which φ-invariant dimensions exist
         (normal-basis circulant / divisors of x^n-1 over F_2). For each ℓ:
           - if ℓ is not an admissible φ-invariant dimension → cell label
             E-NO-TAU-CLOSED-AT-ELL (structural; band N/A);
           - else run exhaustive m=3 FB-sum yield comparison on matched
             τ-closed vs open V and score the ≥1.25 band.

Authorized stages: 0, 1 only (DEC-20261003-555f72). Stage 2 (n=23,31 +
Boolean null) is NOT authorized under this card.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_IMPL_DIR = Path(__file__).resolve().parent
if str(_IMPL_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPL_DIR))

from gf2 import (  # noqa: E402
    Curve,
    clmul,
    enumerate_subspace,
    is_tau_closed,
    make_field,
    pmod,
    random_subspace_gens,
    saturate_under_frobenius,
    span_dim,
)

EXPERIMENT_ID = "EXP-BINSTD-8bdf86"
HYPOTHESIS_ID = "H-BINSTD-5a212b"
APPROVED_BY = "DEC-20261003-555f72"
SEED = 0x202610010FCBE2
BAND = 1.25
N_STAGE1 = 17
ELLS = [3, 4]
TARGET_COUNT = 40
OUTCOMES = (
    "E-TAU-RICHER",
    "E-TAU-NOT-RICHER",
    "E-NO-TAU-CLOSED-AT-ELL",
    "O-INCONCLUSIVE",
    "O-IMPEDIMENT",
    "S0-FREEZE-OK",
)
EXP_ROOT = Path(__file__).resolve().parents[1]
SOLVER_PIN = "exhaustive_fb_sum_m3_stdlib_gf2"


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


# ---- F_2[x] helpers for x^n - 1 factorization (admissible φ-dims) ----

def poly_degree(p: int) -> int:
    return -1 if p == 0 else p.bit_length() - 1


def poly_divmod(a: int, b: int) -> Tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError
    q = 0
    r = a
    db = poly_degree(b)
    while r and poly_degree(r) >= db:
        shift = poly_degree(r) - db
        q ^= 1 << shift
        r ^= b << shift
    return q, r


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_divmod(a, b)[1]
    return a


def poly_square_free_factor(f: int) -> List[int]:
    """Distinct-degree style factorization over F_2 for small degrees."""
    # Yun/DD: for F_2, square-free via gcd(f, f')
    # Then distinct-degree factorization.
    n = poly_degree(f)
    if n <= 0:
        return [f] if f else []
    factors: List[int] = []
    # Remove (x) factor if present
    if f & 1 == 0:
        factors.append(2)  # x
        while f & 1 == 0:
            f ^= 2  # shouldn't loop; x divides at most once for x^n-1 after /?
            f = poly_divmod(f, 2)[0] if False else f
        # proper: divide out x
        f = f >> 1
    # Distinct-degree factorization of square-free f
    S = f
    x = 2  # x
    v = x
    for d in range(1, poly_degree(S) + 1):
        if poly_degree(S) < 2 * d:
            if poly_degree(S) > 0:
                factors.append(S)
            break
        # v <- v^{2} mod S  (so v = x^{2^d} mod S after d steps starting from x)
        v = pmod(clmul(v, v), S)
        g = poly_gcd(S, v ^ x)
        if poly_degree(g) > 0:
            factors.append(g)
            S = poly_divmod(S, g)[0]
            v = poly_divmod(v, S)[1] if poly_degree(v) >= poly_degree(S) else v
            # reduce v mod S
            v = poly_divmod(v, S)[1]
    else:
        if poly_degree(S) > 0:
            factors.append(S)
    return [p for p in factors if poly_degree(p) > 0]


def factor_x_n_minus_1(n: int) -> List[Dict[str, Any]]:
    """Factor x^n - 1 over F_2 into irreducibles (equal-degree split ok as blocks)."""
    f = (1 << n) ^ 1  # x^n + 1 = x^n - 1 in F_2
    # Split off (x+1) = x-1
    factors: List[int] = []
    if poly_divmod(f, 3)[1] == 0:  # 3 = x+1
        factors.append(3)
        f = poly_divmod(f, 3)[0]
    # Distinct-degree on the rest, then split equal-degree blocks if needed
    blocks = poly_square_free_factor(f) if f not in (0, 1) else []
    # Further split each block into irreducibles via Cantor–Zassenhaus for F_2
    irreds: List[int] = []
    for block in blocks + ([] if 3 in factors else []):
        pass
    # Restart cleaner: collect (x+1) then CZ-split the quotient
    f = (1 << n) ^ 1
    out: List[Dict[str, Any]] = []
    if poly_divmod(f, 3)[1] == 0:
        out.append({"poly": 3, "degree": 1, "label": "x+1"})
        f = poly_divmod(f, 3)[0]
    for irr in _factor_free(f):
        out.append({"poly": irr, "degree": poly_degree(irr), "label": f"deg{poly_degree(irr)}"})
    return out


def _factor_free(f: int) -> List[int]:
    """Factor square-free f over F_2 into irreducibles (small-n CZ)."""
    if poly_degree(f) <= 0:
        return []
    if poly_degree(f) == 1:
        return [f]
    # Distinct-degree
    ddf: List[Tuple[int, int]] = []  # (poly, degree_of_irreds)
    S = f
    x = 2
    v = x
    for d in range(1, poly_degree(f) + 1):
        if poly_degree(S) == 0:
            break
        v = pmod(clmul(v, v), S) if poly_degree(S) > 0 else 0
        if poly_degree(S) == 0:
            break
        g = poly_gcd(S, v ^ x)
        if poly_degree(g) > 0:
            ddf.append((g, d))
            S = poly_divmod(S, g)[0]
            if poly_degree(S) > 0:
                v = poly_divmod(v, S)[1]
    if poly_degree(S) > 0:
        ddf.append((S, poly_degree(S)))
    # Equal-degree split
    irreds: List[int] = []
    for g, d in ddf:
        irreds.extend(_equal_degree_split(g, d))
    return irreds


def _equal_degree_split(f: int, d: int) -> List[int]:
    if poly_degree(f) == d:
        return [f]
    if poly_degree(f) == 0:
        return []
    # Cantor–Zassenhaus for F_2: random h, compute h^{2^{d*m/2}} + h  (trace trick)
    rng = random.Random((f << 8) ^ d ^ SEED)
    target = poly_degree(f)
    assert target % d == 0
    for _ in range(200):
        # random poly deg < deg(f)
        h = rng.randrange(0, 1 << target)
        if h == 0:
            continue
        # compute t = sum_{i=0}^{d-1} h^{2^i}  mod f  (absolute trace to F_{2^d}'s subfield push)
        # For equal-degree factorization over F_2 of r irreds of deg d:
        # g = gcd(f, h^{(q^d - 1)/2} - 1) with q=2 — use iterated Frobenius.
        # Simpler exhaustive for tiny deg: trial-divide by all monic deg-d polys.
        break
    return _trial_split_deg(f, d)


def _trial_split_deg(f: int, d: int) -> List[int]:
    """Trial-divide by all monic degree-d polynomials (ok for n<=31)."""
    found: List[int] = []
    # monic deg d: top bit set, lower d bits free → polys in [1<<d, (1<<(d+1))-1]
    for p in range(1 << d, 1 << (d + 1)):
        if poly_divmod(f, p)[1] == 0:
            # check irreducible-ish: no proper factor of deg < d
            if _is_irred_deg(p, d):
                while poly_divmod(f, p)[1] == 0:
                    found.append(p)
                    f = poly_divmod(f, p)[0]
                    if poly_degree(f) == 0:
                        return found
    if poly_degree(f) > 0:
        found.append(f)
    return found


def _is_irred_deg(p: int, d: int) -> bool:
    if poly_degree(p) != d:
        return False
    # Rabin test over F_2: gcd(p, x^{2^{d/q}} - x) = 1 for prime factors q of d,
    # and x^{2^d} ≡ x mod p.
    x = 2
    cur = x
    for i in range(d):
        cur = pmod(clmul(cur, cur), p)
    if cur != x:
        return False
    # prime factors of d
    factors = []
    m = d
    t = 2
    while t * t <= m:
        if m % t == 0:
            factors.append(t)
            while m % t == 0:
                m //= t
        t += 1 if t == 2 else 2
    if m > 1:
        factors.append(m)
    for q in factors:
        # compute x^{2^{d/q}} mod p
        e = d // q
        cur = x
        for _ in range(e):
            cur = pmod(clmul(cur, cur), p)
        g = poly_gcd(p, cur ^ x)
        if g != 1:
            return False
    return True


def admissible_phi_invariant_dims(n: int) -> Dict[str, Any]:
    """Dims of φ-invariant F_2-subspaces via divisors of x^n-1 (normal basis)."""
    factors = factor_x_n_minus_1(n)
    degs = [f["degree"] for f in factors]
    # Every subset sum of irreducible degrees is an admissible dimension
    dims = {0}
    for d in degs:
        dims |= {x + d for x in dims}
    dims_list = sorted(dims)
    return {
        "n": n,
        "irreducible_degrees": degs,
        "factors": factors,
        "admissible_dimensions": dims_list,
        "method": "normal-basis circulant / F_2-factorization of x^n-1",
    }


def build_tau_closed_gens(F, rng, ell: int, max_tries: int = 400) -> Optional[List[int]]:
    for _ in range(max_tries):
        seed_ell = max(1, min(ell, 2))
        seed = random_subspace_gens(rng, F.n, seed_ell)
        closed = saturate_under_frobenius(F, seed)
        if span_dim(closed, F.n) == ell and is_tau_closed(F, closed):
            return closed
    return None


def build_open_gens(F, rng, ell: int, max_tries: int = 400) -> Optional[List[int]]:
    for _ in range(max_tries):
        gens = random_subspace_gens(rng, F.n, ell)
        if not is_tau_closed(F, gens):
            return gens
    return None


def factor_base_points(curve: Curve, gens: List[int]) -> List[Tuple[int, int]]:
    pts = []
    for x in enumerate_subspace(gens, curve.F.n):
        if x == 0:
            continue
        P = curve.lift_x(x)
        if P is not None:
            pts.append(P)
            N = curve.neg(P)
            if N is not None and N != P:
                pts.append(N)
    uniq = []
    seen = set()
    for P in pts:
        key = (P[0], P[1])
        if key not in seen:
            seen.add(key)
            uniq.append(P)
    return uniq


def m3_decomposes(curve: Curve, fb: Sequence[Tuple[int, int]], R: Tuple[int, int]) -> bool:
    m = len(fb)
    for i in range(m):
        for j in range(m):
            s2 = curve.add(fb[i], fb[j])
            if s2 is None:
                continue
            for k in range(m):
                if curve.add(s2, fb[k]) == R:
                    return True
    return False


def random_curve_point(curve: Curve, rng: random.Random) -> Tuple[int, int]:
    F = curve.F
    for _ in range(10_000):
        x = rng.randrange(1, F.q)
        P = curve.lift_x(x)
        if P is not None:
            if rng.randrange(2):
                P = curve.neg(P)  # type: ignore[assignment]
            assert P is not None
            return P
    raise RuntimeError("failed to sample curve point")


def measure_yield_cell(n: int, ell: int, seed: int, target_count: int) -> Dict[str, Any]:
    rng = random.Random(seed ^ (n * 1_000_003) ^ (ell * 97))
    F = make_field(n)
    curve = Curve(F, A=0, B=1)
    gens_tau = build_tau_closed_gens(F, rng, ell)
    gens_open = build_open_gens(F, rng, ell)
    if gens_tau is None or gens_open is None:
        return {
            "n": n,
            "ell": ell,
            "status": "impediment",
            "reason": "failed_to_sample_V",
        }
    fb_tau = factor_base_points(curve, gens_tau)
    fb_open = factor_base_points(curve, gens_open)
    if len(fb_tau) < 3 or len(fb_open) < 3:
        return {
            "n": n,
            "ell": ell,
            "status": "impediment",
            "reason": "factor_base_too_small",
            "fb_tau_size": len(fb_tau),
            "fb_open_size": len(fb_open),
        }
    hits_tau = 0
    hits_open = 0
    for _t in range(target_count):
        R = random_curve_point(curve, rng)
        hits_tau += int(m3_decomposes(curve, fb_tau, R))
        hits_open += int(m3_decomposes(curve, fb_open, R))
    r_tau = hits_tau / target_count
    r_open = hits_open / target_count
    ratio = (r_tau / r_open) if r_open > 0 else None
    return {
        "n": n,
        "ell": ell,
        "status": "ok",
        "target_count": target_count,
        "hits_tau": hits_tau,
        "hits_open": hits_open,
        "R_tau": r_tau,
        "R_open": r_open,
        "ratio_tau_over_open": ratio,
        "fb_tau_size": len(fb_tau),
        "fb_open_size": len(fb_open),
        "band": BAND,
        "meets_band": bool(ratio is not None and ratio >= BAND and hits_tau and hits_open),
        "both_arms_nonzero": hits_tau > 0 and hits_open > 0,
        "solver_pin": SOLVER_PIN,
        "cell_label": None,
    }


def measure_cell(n: int, ell: int, seed: int, admissible: Sequence[int]) -> Dict[str, Any]:
    if ell not in admissible:
        return {
            "n": n,
            "ell": ell,
            "status": "structural",
            "cell_label": "E-NO-TAU-CLOSED-AT-ELL",
            "reason": (
                f"dim {ell} is not an admissible φ-invariant dimension for n={n}; "
                f"admissible={list(admissible)}"
            ),
            "band_applicable": False,
        }
    cell = measure_yield_cell(n, ell, seed, TARGET_COUNT)
    if cell.get("status") == "ok":
        if not cell.get("both_arms_nonzero"):
            cell["cell_label"] = "O-INCONCLUSIVE"
        elif cell.get("meets_band"):
            cell["cell_label"] = "E-TAU-RICHER"
        else:
            cell["cell_label"] = "E-TAU-NOT-RICHER"
        cell["band_applicable"] = True
    elif cell.get("status") == "impediment":
        cell["cell_label"] = "O-IMPEDIMENT"
        cell["band_applicable"] = True
    return cell


def decide_outcome(cells: List[Dict[str, Any]]) -> str:
    labels = [c.get("cell_label") for c in cells]
    if any(l == "O-IMPEDIMENT" for l in labels):
        return "O-IMPEDIMENT"
    if all(l == "E-NO-TAU-CLOSED-AT-ELL" for l in labels):
        return "E-NO-TAU-CLOSED-AT-ELL"
    if any(l == "O-INCONCLUSIVE" for l in labels):
        return "O-INCONCLUSIVE"
    # Among cells where the band applies:
    applicable = [c for c in cells if c.get("band_applicable") and c.get("status") == "ok"]
    if not applicable:
        # mixed structural + nothing else
        if any(l == "E-NO-TAU-CLOSED-AT-ELL" for l in labels):
            return "E-NO-TAU-CLOSED-AT-ELL"
        return "O-IMPEDIMENT"
    if all(c.get("meets_band") for c in applicable):
        return "E-TAU-RICHER"
    return "E-TAU-NOT-RICHER"


def stage0(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    freeze = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "seed": SEED,
        "band": BAND,
        "ells": ELLS,
        "n_stage1": N_STAGE1,
        "target_count": TARGET_COUNT,
        "solver_pin": SOLVER_PIN,
        "tau_closed_definition": (
            "V is φ-invariant as an F_2-subspace of F_{2^n}, equivalently "
            "(in a normal basis) a circulant code / ideal of F_2[x]/(x^n-1). "
            "Construction by saturating a seed under x |-> x^2."
        ),
        "admissible_dim_method": "subset sums of deg(irreducible factors of x^n-1 over F_2)",
        "curve": "Y^2 + XY = X^3 + 1 over F_2[t]/(t^17+t^3+1)",
        "controls": [
            "ctl_matched_dim_open_V",
            "ctl_matched_random_targets",
            "ctl_shared_solver_pin",
            "ctl_no_posthoc_band_edit",
            "ctl_admissible_phi_dims_certified",
        ],
        "authorized_stages": [0, 1],
        "stage2_not_authorized": "n in {23,31} + random-Boolean null require a later decision",
        "structural_note": (
            "If ell is not an admissible φ-invariant dimension at n, the cell "
            "is E-NO-TAU-CLOSED-AT-ELL and the ≥1.25 band does not apply."
        ),
    }
    predictions = {
        "heuristic": "HEUR-BINSTD-0fcbe2-H1",
        "success_rate_ratio_tau_over_open_min": BAND,
        "target_count_min": TARGET_COUNT,
        "both_arms_nonzero_required_for_ratio": True,
        "cells": [{"n": N_STAGE1, "ell": ell} for ell in ELLS],
        "structural_precondition": "ell in admissible_phi_invariant_dims(n)",
        "frozen_before_stage1": True,
        "note": "Do not edit after any Stage-1 outcome.",
    }
    pin = {
        "name": SOLVER_PIN,
        "definition": (
            "Enumerate all ordered triples from the lifted factor-base points "
            "and accept iff P+Q+S equals the target under the Koblitz group law. "
            "Admitted toy pin for small |V|; not XOR-SAT; not Magma/Sage."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    h_freeze = write_json(stage0_dir / "freeze.json", freeze)
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", predictions)
    h_pin = write_json(stage0_dir / "solver-pin.json", pin)
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 0,
        "status": "completed_valid",
        "outcome": "S0-FREEZE-OK",
        "artifact_sha256": {
            "stage0/freeze.json": h_freeze,
            "stage0/preregistered-predictions.json": h_pred,
            "stage0/solver-pin.json": h_pin,
        },
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", {"result": result})
    write_json(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 0,
            "status": "completed_valid",
            "outcome": "S0-FREEZE-OK",
            "seed": SEED,
            "recorded_at": utc_now(),
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return result


def stage1(run_dir: Path) -> Dict[str, Any]:
    stage0_dir = EXP_ROOT / "stage0"
    required = [
        stage0_dir / "freeze.json",
        stage0_dir / "preregistered-predictions.json",
        stage0_dir / "solver-pin.json",
    ]
    if not all(p.is_file() for p in required):
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0_freeze_missing",
            "certificate": {"kind": "none"},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", {"result": result})
        write_json(
            run_dir / "manifest.yaml",
            {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "failed_infrastructure",
                "outcome": "O-IMPEDIMENT",
                "recorded_at": utc_now(),
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        return result

    try:
        adm = admissible_phi_invariant_dims(N_STAGE1)
        cells = [measure_cell(N_STAGE1, ell, SEED, adm["admissible_dimensions"]) for ell in ELLS]
    except Exception as exc:
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": f"exception:{type(exc).__name__}:{exc}",
            "certificate": {"kind": "none"},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", {"result": result})
        write_json(
            run_dir / "manifest.yaml",
            {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "failed_infrastructure",
                "outcome": "O-IMPEDIMENT",
                "recorded_at": utc_now(),
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        return result

    outcome = decide_outcome(cells)
    stage1_dir = EXP_ROOT / "stage1"
    matrix = {
        "experiment_id": EXPERIMENT_ID,
        "admissible_phi_dims": adm,
        "cells": cells,
        "outcome": outcome,
        "band": BAND,
        "solver_pin": SOLVER_PIN,
        "note": "Toy / structural meter only; no break / exponent / n>=131 transfer.",
    }
    h_matrix = write_json(stage1_dir / "yield-matrix.json", matrix)
    h_adm = write_json(stage1_dir / "admissible-phi-dims.json", adm)

    results_md = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"- hypothesis: {HYPOTHESIS_ID}\n"
        f"- approved_by: {APPROVED_BY}\n"
        f"- outcome: **{outcome}**\n"
        f"- band: {BAND}\n"
        f"- admissible φ-dims at n={N_STAGE1}: {adm['admissible_dimensions']}\n"
        f"- solver_pin: `{SOLVER_PIN}`\n\n"
        "## Per-cell\n\n"
    )
    for c in cells:
        results_md += (
            f"- ell={c.get('ell')}: label={c.get('cell_label')}, "
            f"status={c.get('status')}, ratio={c.get('ratio_tau_over_open')}, "
            f"reason={c.get('reason')}\n"
        )
    results_md += (
        "\n## Limits\n\n"
        "- Structural emptiness of τ-closed dim-ℓ cells is a scope fact about "
        "φ-invariant subspaces, not a claim that τ-stable FB never helps.\n"
        "- No break, exponent, or deployed insecurity claim.\n"
        "- Stage 2 (n∈{23,31} + Boolean null) not authorized under this card.\n"
        "- Amazon Bedrock NOT SELECTED.\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results_md)

    status = "completed_valid" if outcome != "O-IMPEDIMENT" else "failed_infrastructure"
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "artifact_sha256": {
            "stage1/yield-matrix.json": h_matrix,
            "stage1/admissible-phi-dims.json": h_adm,
        },
        "cells_summary": [
            {
                "ell": c.get("ell"),
                "cell_label": c.get("cell_label"),
                "status": c.get("status"),
                "ratio": c.get("ratio_tau_over_open"),
                "reason": c.get("reason"),
            }
            for c in cells
        ],
        "admissible_dimensions": adm["admissible_dimensions"],
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", {"result": result})
    write_json(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 1,
            "status": status,
            "outcome": outcome,
            "seed": SEED,
            "recorded_at": utc_now(),
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    return result


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", type=str, default="")
    p.add_argument("--run-dir", type=str, required=True)
    args = p.parse_args(argv)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
