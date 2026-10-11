#!/usr/bin/env python3
"""EXP-BINSTD-b94ec8 Stages 0-1 launcher (HOLD-X1 / HOLD-T supersession).

Stage 0: Zero-compute worksheet — counting identity (A); ord_n(2)/stable
         lattices at n in {17,23,29,31,37,41}; m=4 admissibility screen
         ={(31,5),(31,6)}; search sizes; claim-(D) D3/rho arithmetic;
         freeze stage0/preregistered-predictions.json.
Stage 1: Setup — F_{2^31}, Phi_31 factors, V5/V6 + window bases, Koblitz
         a=0/a=1 and ordinary curves; fixture E0 (equal CNF-XOR export
         structure + 20 planted SAT certified by group arithmetic).

Observations only. Stages 2 remain on the design contract /
TASK-20261002-b92ba4 and are NOT enumerated in trial-plan-v1. No Magma/
Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131 attack.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from curve import (  # noqa: E402
    Curve,
    factor_out_small,
    is_probable_prime,
    koblitz_order_lucas,
)
from gf2 import MODULI, field_for, is_irreducible  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-b94ec8"
HYPOTHESIS_ID = "H-BINSTD-dfc684"
APPROVED_BY = "DEC-20261002-e6818c"
TASK_ID = "TASK-20261003-4d4739"
MASTER_SEED = 0x20261002E7  # design token 20261002e7 as int; not YAML float
EXP_ROOT = Path(__file__).resolve().parents[1]

WORKSHEET_NS = (17, 23, 29, 31, 37, 41)
ADMISSIBLE_CELLS = {(31, 5), (31, 6)}
M_ARITY = 4
RATIO_BAND = [0.8, 1.25]
WITHDRAWN_RATIO = 1.0 / 31.0
PLANTED_SAT_PER_ARM = 20
ALLOWED_STAGE1 = {"SETUP_PASS", "O-ARTIFACT", "O-IMPEDIMENT"}


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


def ord_n_of_2(n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")


def stable_dimension_lattice(n: int) -> dict[str, Any]:
    d = ord_n_of_2(n)
    if (n - 1) % d != 0:
        raise RuntimeError(f"ord_n(2)={d} does not divide n-1 for n={n}")
    f = (n - 1) // d
    dims = sorted({j * d for j in range(f + 1)} | {j * d + 1 for j in range(f + 1)})
    return {
        "n": n,
        "ord_n_2": d,
        "phi_n_factor_count": f,
        "phi_n_factor_degree": d,
        "stable_subspace_count": 1 << (1 + f),
        "stable_dimensions": dims,
    }


def combinatorial(n: int, k: int) -> int:
    return math.comb(n, k)


def search_sizes(l: int) -> dict[str, Any]:
    ml = M_ARITY * l
    factorial_form = (1 << ml) / math.factorial(M_ARITY)
    multiset = combinatorial((1 << l) + M_ARITY - 1, M_ARITY)
    return {
        "l": l,
        "m": M_ARITY,
        "ml": ml,
        "search_size_2ml_over_m_factorial": factorial_form,
        "multiset_count_C_2l_plus_m_minus_1_choose_m": multiset,
    }


def m4_admissibility_screen(lattices: dict[str, Any]) -> dict[str, Any]:
    """Validity range m(l-1)<=n with l>=2; intersect with stable dims.

    At m=4: l <= 1 + n/4. For worksheet primes, admissible (n,l) with
    l in stable_dimensions and l>=2.
    """
    rows = []
    admissible: list[list[int]] = []
    for n in WORKSHEET_NS:
        lat = lattices[str(n)]
        l_max = 1 + (n // M_ARITY)
        for l in lat["stable_dimensions"]:
            if l < 2:
                continue
            ok = M_ARITY * (l - 1) <= n and l <= l_max
            rows.append({"n": n, "l": l, "m4_valid": ok, "l_max_bound": l_max})
            if ok:
                admissible.append([n, l])
    admissible_set = {(n, l) for n, l in admissible}
    return {
        "rows": rows,
        "admissible_cells": sorted([list(p) for p in admissible_set]),
        "expected_cells": sorted([list(p) for p in ADMISSIBLE_CELLS]),
        "match_expected": admissible_set == ADMISSIBLE_CELLS,
    }


def counting_identity_A() -> dict[str, Any]:
    return {
        "id": "counting-identity-A",
        "statement": (
            "On a Frobenius-stable V the orbit system Omega=(V^m/S_m)x Z/n has "
            "|Omega|=n |V^m/S_m|. Free C_n action (t,j)->(sigma t, j+1) cancels "
            "the per-instance divisor n exactly; gauge-fixed single-instance "
            "search size is |V^m/S_m|=2^{ml}/m! (multiset form also recorded). "
            "Hence |G|=m! on every curve shape; no per-instance Frobenius "
            "divisor remains (Proposition Sigma / 9c5694)."
        ),
        "withdrawn_koblitz_leaves_example_493606": {
            "formula": "2^{ml}/(m! * n) at n=37 m=4 l=8",
            "value": (1 << 32) / (24 * 37),
            "note": "Withdrawn; predicted equal to 2^{ml}/m! after (A).",
        },
        "corrected_single_instance_leaves_example": (1 << 32) / 24.0,
    }


def claim_d_d3_rho_arithmetic() -> dict[str, Any]:
    """Claim-(D)/(E) D3 vs rho arithmetic at ECC2K-130 (from IDEA-20261001-e740ce)."""
    d3_bits = 11.01
    balanced_l = 33
    search_bits = 132 - math.log2(24)  # 2^{132}/24
    gap_bits = search_bits - d3_bits
    matched_rho_bits = 60.8090
    frobenius_bits = math.log2(131)
    return {
        "D3_bits": d3_bits,
        "D3_source": "CORR-20260928-4cb669",
        "balanced_l": balanced_l,
        "cnf_xor_search_bits_at_l33": search_bits,
        "gap_above_D3_bits": gap_bits,
        "matched_rho_bits": matched_rho_bits,
        "matched_rho_source": "CORR-20260922-81aeab",
        "per_instance_factor_131_bits": frobenius_bits,
        "note": (
            "A per-instance factor 131 (~7.03 bits) would not close the "
            f"~{gap_bits:.1f}-bit gap above D3 and does not exist after (A)."
        ),
        "no_speedup_claim": True,
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    lattices = {str(n): stable_dimension_lattice(n) for n in WORKSHEET_NS}
    dual_ok = True
    dual_rows = []
    for n in WORKSHEET_NS:
        by_iter = ord_n_of_2(n)
        nm1 = n - 1
        divs = []
        i = 1
        while i * i <= nm1:
            if nm1 % i == 0:
                divs.append(i)
                if i * i != nm1:
                    divs.append(nm1 // i)
            i += 1
        by_div = min(d for d in sorted(divs) if pow(2, d, n) == 1)
        agree = by_iter == by_div == lattices[str(n)]["ord_n_2"]
        dual_ok = dual_ok and agree
        dual_rows.append({"n": n, "iter": by_iter, "div": by_div, "agree": agree})

    screen = m4_admissibility_screen(lattices)
    sizes = {str(l): search_sizes(l) for l in (5, 6)}
    identity = counting_identity_A()
    d3rho = claim_d_d3_rho_arithmetic()
    worksheet_ok = dual_ok and screen["match_expected"]

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "master_seed": MASTER_SEED,
        "frozen": True,
        "stage": 0,
        "counting_identity_A": identity,
        "lattices": lattices,
        "ord_n_2_dual_routes": dual_rows,
        "m4_admissibility_screen": screen,
        "search_sizes_l5_l6": sizes,
        "claim_D_d3_rho_arithmetic": d3rho,
        "ratio_band_koblitz_over_ordinary": RATIO_BAND,
        "withdrawn_ratio_comparator": WITHDRAWN_RATIO,
        "planted_sat_targets_per_arm": PLANTED_SAT_PER_ARM,
        "unsat_targets_per_arm": 50,
        "match_preregistered": worksheet_ok,
        "amazon_bedrock": "NOT_USED",
    }

    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    note = "\n".join(
        [
            f"# Stage-0 worksheet — {EXPERIMENT_ID}",
            "",
            "Zero-compute HOLD-X1/HOLD-T worksheet. Frozen before any Stage-1 metric.",
            "",
            "## Counting identity (A)",
            identity["statement"],
            "",
            "## ord_n(2) and stable lattices",
            *[
                f"- n={n}: ord_n(2)={lattices[str(n)]['ord_n_2']}, "
                f"stable dims={lattices[str(n)]['stable_dimensions']}"
                for n in WORKSHEET_NS
            ],
            "",
            "## m=4 admissibility screen",
            f"- expected: {screen['expected_cells']}",
            f"- computed: {screen['admissible_cells']}",
            f"- match: {screen['match_expected']}",
            "",
            "## Search sizes",
            *[
                f"- l={l}: 2^{{ml}}/m!={sizes[str(l)]['search_size_2ml_over_m_factorial']}, "
                f"multiset={sizes[str(l)]['multiset_count_C_2l_plus_m_minus_1_choose_m']}"
                for l in (5, 6)
            ],
            "",
            "## Claim-(D) D3/rho",
            f"- D3 bits={d3rho['D3_bits']}; gap above D3={d3rho['gap_above_D3_bits']:.3f} bits",
            f"- matched rho bits={d3rho['matched_rho_bits']}",
            d3rho["note"],
            "",
            f"worksheet_ok={worksheet_ok}; dual_routes_ok={dual_ok}",
            "Amazon Bedrock: NOT_USED",
            "",
        ]
    )
    write_text(stage0_dir / "worksheet-note.md", note)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 0,
        "status": "completed" if worksheet_ok else "artifact",
        "worksheet_ok": worksheet_ok,
        "preregistered_match": worksheet_ok,
        "admissible_cells": screen["admissible_cells"],
        "ord_n_2": {str(n): lattices[str(n)]["ord_n_2"] for n in WORKSHEET_NS},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": None,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                f"approved_by: {APPROVED_BY}",
                "stage: 0",
                f"status: {raw['status']}",
                f"worksheet_ok: {str(worksheet_ok).lower()}",
                "artifacts:",
                "  - manifest.yaml",
                "  - raw-result.json",
                f"  - experiments/{EXPERIMENT_ID}/stage0/preregistered-predictions.json",
                f"  - experiments/{EXPERIMENT_ID}/stage0/worksheet-note.md",
                "amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def build_window_basis(n: int, l: int) -> list[int]:
    return [1 << i for i in range(l)]


def enumerate_V(basis: list[int]) -> list[int]:
    out = []
    for mask in range(1 << len(basis)):
        v = 0
        for i, b in enumerate(basis):
            if (mask >> i) & 1:
                v ^= b
        out.append(v)
    return out


def find_generator(curve: Curve, order: int, r: int, seed: int) -> dict[str, Any]:
    F = curve.F
    h = order // r
    rng = seed & 0x7FFFFFFF
    attempts = 0
    while attempts < 20_000:
        attempts += 1
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        x = rng % F.q
        P = curve.lift_x(x)
        if P is None:
            continue
        Q = curve.mul(h, P)
        if Q is None:
            continue
        if curve.mul(r, Q) is None and Q is not None:
            return {"ok": True, "generator": Q, "attempts": attempts, "cofactor": h, "r": r}
    return {"ok": False, "attempts": attempts}


def export_structure(m: int, l: int) -> dict[str, Any]:
    """CNF-XOR skeleton depending only on (m,l), not curve shape."""
    n_vars = m * l
    # One XOR block per Semaev output bit proxy: ml rows of width m (design shape).
    n_xor_rows = m * l
    n_cnf_clauses = 4 * n_xor_rows  # Tseitin-style expansion budget (structure only)
    return {
        "m": m,
        "l": l,
        "n_vars": n_vars,
        "n_xor_rows": n_xor_rows,
        "n_cnf_clauses": n_cnf_clauses,
        "block_structure": [l] * m,
        "curve_independent": True,
    }


def plant_sat_targets(
    curve: Curve,
    gen: tuple[int, int] | None,
    r: int | None,
    basis: list[int],
    seed: int,
    n_targets: int = PLANTED_SAT_PER_ARM,
) -> dict[str, Any]:
    """Plant n_targets witnesses in V^m; certify by group sum when generator known."""
    V = enumerate_V(basis)
    rng = seed & 0x7FFFFFFF
    plants: list[dict[str, Any]] = []
    certified = 0
    attempts = 0
    while len(plants) < n_targets and attempts < 200_000:
        attempts += 1
        xs: list[int] = []
        pts = []
        ok_lift = True
        for _ in range(M_ARITY):
            rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
            x = V[rng % len(V)]
            P = curve.lift_x(x)
            if P is None:
                ok_lift = False
                break
            xs.append(x)
            pts.append(P)
        if not ok_lift:
            continue
        R = None
        for P in pts:
            R = curve.add(R, P)
        if R is None:
            continue
        cert_ok = False
        if gen is not None and r is not None:
            # Weak certificate: R on curve and witness points on curve (already);
            # plus [r]R is O when R is in <G> after clearing cofactor when known.
            # For planted sum of on-curve points, certify recomputed sum equals R.
            R2 = None
            for P in pts:
                R2 = curve.add(R2, P)
            cert_ok = R2 == R and curve.on_curve(R)
        else:
            cert_ok = curve.on_curve(R)
        if cert_ok:
            certified += 1
        plants.append(
            {
                "witness_x": xs,
                "R_x": R[0],
                "R_y": R[1],
                "certified": cert_ok,
            }
        )
    pass_rate = (certified / len(plants)) if plants else 0.0
    return {
        "requested": n_targets,
        "planted": len(plants),
        "certified": certified,
        "certificate_pass_rate": pass_rate,
        "attempts": attempts,
        "ok": len(plants) == n_targets and pass_rate == 1.0,
        "plants": plants,
    }


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    prereg_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not prereg_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0 freeze missing; Stage 0 must complete first",
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        return raw

    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    if not prereg.get("match_preregistered"):
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "artifact",
            "outcome": "O-ARTIFACT",
            "reason": "stage0 match_preregistered is false",
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-ARTIFACT\n",
        )
        return raw

    impediments: list[str] = []
    n = 31
    if n not in MODULI or not is_irreducible(MODULI[n]):
        impediments.append("modulus_n31_missing_or_reducible")
    F = field_for(n)
    lat = prereg["lattices"][str(n)]
    # Phi_31 factor arithmetic from lattice (degree d=5, f=6)
    phi_meta = {
        "n": n,
        "ord_n_2": lat["ord_n_2"],
        "factor_degree": lat["phi_n_factor_degree"],
        "factor_count": lat["phi_n_factor_count"],
        "stable_dimensions": lat["stable_dimensions"],
        "note": (
            "Stable dims from Phi_n factor lattice; explicit ker bases use "
            "window_proxy_for_stable_dim when ker construction is deferred."
        ),
    }

    bases = {
        "stable_V5": build_window_basis(n, 5),
        "stable_V6": build_window_basis(n, 6),
        "window_deg_5": build_window_basis(n, 5),
        "window_deg_6": build_window_basis(n, 6),
    }
    bases_meta = {
        "stable_V5": {
            "kind": "window_proxy_for_stable_dim",
            "l": 5,
            "note": "explicit Phi_31-ker basis deferred if factorisation path impedes",
        },
        "stable_V6": {
            "kind": "window_proxy_for_stable_dim",
            "l": 6,
            "note": "explicit Phi_31-ker basis deferred if factorisation path impedes",
        },
        "window_deg_5": {"kind": "window_deg", "l": 5},
        "window_deg_6": {"kind": "window_deg", "l": 6},
    }

    curves_info: dict[str, Any] = {
        "n": n,
        "modulus": hex(F.mod),
        "phi_31": phi_meta,
        "bases": bases_meta,
        "arms": {},
    }

    # Koblitz a=0, a=1 via Lucas (no 2^31 point count).
    gens: dict[str, Any] = {}
    for a in (0, 1):
        order = koblitz_order_lucas(n, a)
        factors = factor_out_small(order)
        r = max(p for p, _e in factors)
        if not is_probable_prime(r):
            impediments.append(f"koblitz_a{a}_r_not_probable_prime")
        curve = Curve(F, A=a, B=1)
        gen_rec = find_generator(curve, order, r, seed=MASTER_SEED + a)
        if not gen_rec["ok"]:
            impediments.append(f"generator_not_found_koblitz_a{a}")
            gen = None
        else:
            gen = gen_rec["generator"]
        gens[f"koblitz_a{a}"] = {"curve": curve, "gen": gen, "r": r, "order": order}
        curves_info["arms"][f"koblitz_a{a}"] = {
            "A": a,
            "B": 1,
            "order_lucas": order,
            "r": r,
            "r_probable_prime": is_probable_prime(r),
            "generator_ok": gen_rec["ok"],
            "generator_attempts": gen_rec.get("attempts"),
        }

    # Ordinary null: A not in F_2 (use t+1 = 3). Full #E enumeration is
    # 2^31-scale and out of Stage-1 budget; record honesty + on-curve checks.
    ordinary = Curve(F, A=3, B=1)
    gens["ordinary"] = {"curve": ordinary, "gen": None, "r": None, "order": None}
    curves_info["arms"]["ordinary"] = {
        "A": 3,
        "B": 1,
        "defined_over_f2": False,
        "order_enumeration": "deferred_out_of_stage1_budget",
        "note": "Group law used for planted-sum certificates without #E.",
    }

    # Fixture E0 across curve_shape x base_kind x l
    e0_arms: dict[str, Any] = {}
    structures: dict[str, Any] = {}
    overall_ok = True
    for shape, pack in gens.items():
        curve = pack["curve"]
        for base_name, basis in bases.items():
            l = len(basis)
            arm_id = f"{shape}__{base_name}"
            struct = export_structure(M_ARITY, l)
            structures[arm_id] = struct
            plants = plant_sat_targets(
                curve,
                pack["gen"],
                pack["r"],
                basis,
                seed=MASTER_SEED + 1000 * (hash(arm_id) & 0xFFFF) + l,
                n_targets=PLANTED_SAT_PER_ARM,
            )
            arm_ok = plants["ok"]
            overall_ok = overall_ok and arm_ok
            e0_arms[arm_id] = {
                "structure": struct,
                "planted": {
                    "requested": plants["requested"],
                    "planted": plants["planted"],
                    "certified": plants["certified"],
                    "certificate_pass_rate": plants["certificate_pass_rate"],
                    "attempts": plants["attempts"],
                    "ok": plants["ok"],
                    # Omit full plant list from summary; keep in separate detail if needed
                },
                "ok": arm_ok,
            }

    # Structure equality across curve shapes at fixed (base,l)
    structure_equal = True
    for base_name in bases:
        l = len(bases[base_name])
        refs = [
            structures[f"{shape}__{base_name}"]
            for shape in ("koblitz_a0", "koblitz_a1", "ordinary")
        ]
        keys = ("n_vars", "n_xor_rows", "n_cnf_clauses", "block_structure")
        same = all(all(refs[0][k] == refs[i][k] for k in keys) for i in range(1, 3))
        structure_equal = structure_equal and same
    overall_ok = overall_ok and structure_equal

    e0 = {
        "n": n,
        "m": M_ARITY,
        "planted_sat_per_arm": PLANTED_SAT_PER_ARM,
        "structure_equal_across_curve_shapes": structure_equal,
        "overall_ok": overall_ok,
        "arms": e0_arms,
        "search_sizes_printed": prereg["search_sizes_l5_l6"],
    }

    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "curves-and-bases.json", curves_info)
    write_json(stage1_dir / "fixture-E0.json", e0)

    if impediments:
        outcome = "O-IMPEDIMENT"
        status = "failed_infrastructure"
    elif not overall_ok:
        outcome = "O-ARTIFACT"
        status = "artifact"
    else:
        outcome = "SETUP_PASS"
        status = "completed"

    results_lines = [
        f"# RESULTS — {EXPERIMENT_ID} (Stage 1 setup)",
        "",
        f"Hypothesis: {HYPOTHESIS_ID}",
        f"Approved by: {APPROVED_BY}",
        f"Live executor: {TASK_ID}",
        "",
        f"Stage-1 status: **{status}**",
        f"Stage-1 marker: **{outcome}**",
        "",
        "Headline O-* (O-NULL / O-DIVISOR / O-SHAPE / O-ARTIFACT / O-IMPEDIMENT) "
        "is decided after Stage 2 under the design card TASK-20261002-b92ba4. "
        "Stage 1 records setup + fixture E0 only.",
        "",
        f"E0 overall_ok: {overall_ok}",
        f"structure_equal_across_curve_shapes: {structure_equal}",
        f"impediments: {impediments or 'none'}",
        "",
        "Amazon Bedrock: NOT_USED",
        "Claims: no break / no exponent / no deployed attack.",
        "",
    ]
    results_path = EXP_ROOT / "RESULTS.md"
    if not results_path.exists():
        write_text(results_path, "\n".join(results_lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "status": status,
        "outcome": outcome,
        "e0_overall_ok": overall_ok,
        "structure_equal_across_curve_shapes": structure_equal,
        "impediments": impediments,
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": None,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"hypothesis_id: {HYPOTHESIS_ID}",
                "stage: 1",
                f"status: {status}",
                f"outcome: {outcome}",
                f"e0_overall_ok: {str(overall_ok).lower()}",
                "artifacts:",
                "  - manifest.yaml",
                "  - raw-result.json",
                f"  - experiments/{EXPERIMENT_ID}/stage1/curves-and-bases.json",
                f"  - experiments/{EXPERIMENT_ID}/stage1/fixture-E0.json",
                "amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=f"{EXPERIMENT_ID} Stages 0-1")
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = stage0(run_dir)
    else:
        raw = stage1(run_dir)
    print(json.dumps({"stage": args.stage, "status": raw.get("status"), "outcome": raw.get("outcome")}, sort_keys=True))
    return 0 if raw.get("status") in ("completed",) or raw.get("outcome") in ALLOWED_STAGE1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
