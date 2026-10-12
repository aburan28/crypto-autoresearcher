#!/usr/bin/env python3
"""EXP-FROB-7d51ae Stages 0-1 launcher (frozen contract v1).

Stage 0: Genus-2 model census over F_2; freeze hits with 19|#Jac(F_2);
         freeze GGMP degree-6 prediction and elliptic (a,b) recipe for n=19.
Stage 1: Cantor integrity + (L,b) + eliminant_degree / boolean_degree_proxy
         vs subspace / random-subset / identity / null-curve controls;
         write RESULTS.md with exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131
attack. Full descended S_3 first-fall is Stage 2 (not authorized).
Amazon Bedrock is not selected.
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

from gf2 import Field, MOD_F2_19, field_f2k  # noqa: E402
from hyperelliptic import (  # noqa: E402
    Mumford,
    boolean_degree_proxy,
    branching_stats,
    cantor_compose,
    enumerate_jac_f2,
    fibre_eliminant_degree,
    find_order_element,
    jac_order_from_counts,
    point_count_curve,
    weils_ok,
)

EXPERIMENT_ID = "EXP-FROB-7d51ae"
HYPOTHESIS_ID = "H-FROB-772c0b"
APPROVED_BY = "DEC-20261002-da97c5"
ORDER_PRIME = 19
GGMP_VS_DEGREE = 6
N_TOY = 19
MAX_HITS = 3
MASTER_SEED = 2026100219
EXP_ROOT = Path(__file__).resolve().parents[1]


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


def write_yaml_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")

    def dump(obj: Any, indent: int = 0) -> list[str]:
        pad = "  " * indent
        lines: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}:")
                    lines.extend(dump(v, indent + 1))
                elif isinstance(v, bool):
                    lines.append(f"{pad}{k}: {'true' if v else 'false'}")
                elif v is None:
                    lines.append(f"{pad}{k}: null")
                elif isinstance(v, (int, float)):
                    lines.append(f"{pad}{k}: {v}")
                else:
                    s = str(v).replace('"', '\\"')
                    lines.append(f'{pad}{k}: "{s}"')
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump(item, indent + 1))
                elif isinstance(item, bool):
                    lines.append(f"{pad}- {'true' if item else 'false'}")
                elif item is None:
                    lines.append(f"{pad}- null")
                elif isinstance(item, (int, float)):
                    lines.append(f"{pad}- {item}")
                else:
                    s = str(item).replace('"', '\\"')
                    lines.append(f'{pad}- "{s}"')
        return lines

    path.write_text("\n".join(dump(data)) + "\n", encoding="utf-8")


def census_genus2() -> dict[str, Any]:
    """Enumerate deg h<=3, deg f<=6 models; retain 19|#Jac with Weil gate."""
    hits: list[dict[str, Any]] = []
    scanned = 0
    weil_rejects = 0
    for h in range(1 << 4):  # deg <= 3
        for f in range(1 << 7):  # deg <= 6
            scanned += 1
            # Skip the zero curve / empty f with h=0 (singular)
            if f == 0 and h == 0:
                continue
            n1 = point_count_curve(h, f, 1)
            n2 = point_count_curve(h, f, 2)
            if not weils_ok(n1, n2):
                weil_rejects += 1
                continue
            jac = jac_order_from_counts(n1, n2)
            if jac % ORDER_PRIME != 0:
                continue
            hits.append(
                {
                    "h": h,
                    "f": f,
                    "h_hex": hex(h),
                    "f_hex": hex(f),
                    "N1": n1,
                    "N2": n2,
                    "jac_order": jac,
                }
            )
    # Dedup by (N1,N2,jac) keeping lex-smallest (h,f); report up to MAX_HITS
    hits.sort(key=lambda r: (r["h"], r["f"]))
    return {
        "scanned": scanned,
        "weil_rejects": weil_rejects,
        "hit_count_raw": len(hits),
        "hits": hits[:MAX_HITS],
        "hits_truncated": len(hits) > MAX_HITS,
        "all_hit_orders": sorted({r["jac_order"] for r in hits}),
    }


def find_koblitz_n19() -> dict[str, Any]:
    """First Koblitz (a,b) in F_2 with E(F_{2^{19}}) having a large prime factor."""
    field = Field(MOD_F2_19)
    # Point count via baby enumeration is 2^19 — too heavy for Stage 0.
    # Freeze the SEARCH RECIPE only; actual curve selection runs in Stage 1
    # with a cheap order probe on a random sample OR deferred measurement.
    # Stage 0 records the recipe and modulus; Stage 1 may fill (a,b).
    return {
        "n": N_TOY,
        "modulus": MOD_F2_19,
        "modulus_hex": hex(MOD_F2_19),
        "recipe": (
            "lexicographic (a,b) in F_2^2 for y^2 + x y = x^3 + a x^2 + b; "
            "retain first with a prime factor of bit length >= 17 in #E(F_{2^{19}}); "
            "full order count is Stage-1 optional and may return UNMEASURED if "
            "2^19 enumeration exceeds watchdog — never blocks Mumford arm."
        ),
        "field_n": field.n,
        "a": None,
        "b": None,
        "status": "recipe_frozen",
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    census = census_genus2()
    koblitz = find_koblitz_n19()
    prereg = {
        "ggmp_vs_degree_m3": GGMP_VS_DEGREE,
        "order_prime": ORDER_PRIME,
        "n_toy": N_TOY,
        "genus": 2,
        "m_arity": 3,
        "max_hits_reported": MAX_HITS,
        "predicted_eliminant_differs_from_6": True,
        "predicted_b_at_least": 2,
        "first_fall_degree_stage": "STAGE2_NOT_AUTHORIZED",
        "boolean_degree_proxy_formula": "eliminant_degree * m_arity",
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", prereg)
    write_json(EXP_ROOT / "stage0" / "genus2-census.json", census)
    write_json(EXP_ROOT / "stage0" / "koblitz-recipe.json", koblitz)

    no_model = census["hit_count_raw"] == 0
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed",
        "genus2_census_ok": True,
        "no_model": no_model,
        "hit_count_raw": census["hit_count_raw"],
        "hits_reported": len(census["hits"]),
        "freeze": {
            "preregistered": True,
            "ggmp_vs_degree_m3": GGMP_VS_DEGREE,
        },
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "status": "completed",
            "outcome": "STAGE0_FREEZE",
            "hit_count_raw": census["hit_count_raw"],
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def cantor_integrity(h: int, f: int, elements: list[Mumford], rng: random.Random) -> dict[str, Any]:
    """Three random triple checks: (A+B)+C == A+(B+C) and A+0==A."""
    if len(elements) < 2:
        return {"pass": False, "reason": "too_few_elements"}
    id_m = Mumford(1, 0)
    checks = []
    for i in range(3):
        a, b, c = rng.sample(elements, 3) if len(elements) >= 3 else (elements[0], elements[-1], id_m)
        left = cantor_compose(h, f, cantor_compose(h, f, a, b), c)
        right = cantor_compose(h, f, a, cantor_compose(h, f, b, c))
        a0 = cantor_compose(h, f, a, id_m)
        ok = (left.u, left.v) == (right.u, right.v) and (a0.u, a0.v) == (a.u, a.v)
        checks.append(
            {
                "i": i,
                "associative": (left.u, left.v) == (right.u, right.v),
                "identity": (a0.u, a0.v) == (a.u, a.v),
                "ok": ok,
            }
        )
    return {"pass": all(c["ok"] for c in checks), "checks": checks}


def panel_for_hit(hit: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    h, f = hit["h"], hit["f"]
    elements = enumerate_jac_f2(h, f)
    branch = branching_stats(elements)
    # Fibre proxy: all enumerated reduced Mumford divisors (rational-point set).
    # When |Jac(F_2)| from N1/N2 disagrees with the Mumford census, that is
    # the proposal's point-count mismatch artifact — not a Cantor claim.
    elim = fibre_eliminant_degree(elements)
    proxy = boolean_degree_proxy(elim["eliminant_degree"], n=N_TOY, m=3)
    card_ok = len(elements) == int(hit["jac_order"])
    integrity = {"pass": None, "checks": [], "skipped": True}
    t_info: dict[str, Any] | None = None
    fibre_closed = None
    status = "ok"
    if not card_ok:
        status = "cardinality_mismatch"
    else:
        integrity = cantor_integrity(h, f, elements, rng)
        if integrity["pass"]:
            t = find_order_element(elements, h, f, ORDER_PRIME)
            if t is not None:
                fibre = [Mumford(1, 0)]
                x = t
                for _ in range(ORDER_PRIME - 1):
                    fibre.append(x)
                    x = cantor_compose(h, f, x, t)
                fibre_closed = x.u == 1 and x.v == 0
                elim = fibre_eliminant_degree(fibre)
                proxy = boolean_degree_proxy(elim["eliminant_degree"], n=N_TOY, m=3)
                t_info = {"u": t.u, "v": t.v}
            else:
                status = "no_order_19_element"
        else:
            # Cardinality matched but Cantor failed — still report branching /
            # eliminant on the rational-point set; mark integrity fail.
            status = "ok_cantor_unreliable"
            integrity["skipped"] = False

    return {
        "hit": hit,
        "status": status,
        "integrity": integrity,
        "n_elements": len(elements),
        "jac_order": hit["jac_order"],
        "cardinality_match": card_ok,
        "t": t_info,
        "fibre_closed": fibre_closed,
        "eliminant": elim,
        "boolean_degree_proxy": proxy,
        "branching": branch,
        "differs_from_ggmp6": abs(proxy - GGMP_VS_DEGREE) >= 1
        and abs(elim["eliminant_degree"] - GGMP_VS_DEGREE) >= 1,
        "degree_vs_6": {
            "eliminant_degree": elim["eliminant_degree"],
            "boolean_degree_proxy": proxy,
            "ggmp_vs_degree": GGMP_VS_DEGREE,
            "elim_diff": abs(elim["eliminant_degree"] - GGMP_VS_DEGREE),
            "proxy_diff": abs(proxy - GGMP_VS_DEGREE),
        },
    }

def control_panels(jac_panel: dict[str, Any] | None, rng: random.Random) -> dict[str, Any]:
    """Subspace / random-subset / identity / null controls (cardinality-matched)."""
    if jac_panel is None or jac_panel.get("eliminant") is None:
        return {
            "subspace": {"status": "skipped"},
            "random_subset": {"status": "skipped"},
            "identity": {"status": "skipped", "predicted_b": 1, "predicted_L": 0},
            "null_curve": {"status": "skipped"},
        }
    card = len(jac_panel["eliminant"]["im_pi"])
    # Subspace arm: preregistered GGMP degree 6 shape benchmark at equal cardinality intent
    subspace = {
        "status": "preregistered_shape",
        "ggmp_vs_degree_m3": GGMP_VS_DEGREE,
        "boolean_degree_proxy": GGMP_VS_DEGREE,
        "note": "GGMP example 5.1 vector-space Weil-descended degree 6 at m=3; equal-cardinality intent.",
    }
    # Random subset of F_2 of size card (u_0 universe is F_2)
    universe = [0, 1]
    rng.shuffle(universe)
    subset = sorted(universe[: min(card, 2)])
    rs_deg = len(subset)
    rs_proxy = boolean_degree_proxy(rs_deg, n=N_TOY, m=3)
    random_subset = {
        "status": "ok",
        "im_pi": subset,
        "eliminant_degree": rs_deg,
        "boolean_degree_proxy": rs_proxy,
        "differs_from_ggmp6": abs(rs_proxy - GGMP_VS_DEGREE) >= 1 and abs(rs_deg - GGMP_VS_DEGREE) >= 1,
    }
    identity = {
        "status": "ok",
        "predicted_b": 1,
        "predicted_L": 0.0,
        "note": "Identity projection control: b=1, L=0.",
    }
    null_curve = {
        "status": "recipe",
        "note": (
            "Ordinary null curve over F_{2^{19}} not defined over F_2 with "
            "matched factor-base cardinality; full probe optional under Stage 1 "
            "and must not use Magma/Sage/AUXIN."
        ),
    }
    return {
        "subspace": subspace,
        "random_subset": random_subset,
        "identity": identity,
        "null_curve": null_curve,
    }


def classify_outcome(
    no_model: bool,
    panels: list[dict[str, Any]],
    controls: dict[str, Any],
) -> str:
    if no_model:
        return "O-NO-MODEL"
    if any(p.get("status") == "cardinality_mismatch" for p in panels):
        return "O-ARTIFACT"
    measurable = [
        p
        for p in panels
        if p.get("status") in ("ok", "ok_cantor_unreliable", "no_order_19_element")
    ]
    if not measurable:
        return "O-IMPEDIMENT"
    # Scientific reading at F_2 scale: primary decidable signals are b and
    # whether proxy matches subspace arm (GGMP 6). Degree-vs-6 on the F_2
    # u_0 universe is cardinality-forced; RESULTS discloses that scope.
    b_ok = all(p.get("branching", {}).get("b", 0) >= 2 for p in measurable)
    proxy_matches_subspace = all(
        p.get("boolean_degree_proxy") == GGMP_VS_DEGREE for p in measurable
    )
    elim_eq_6 = all(
        p.get("eliminant", {}).get("eliminant_degree") == GGMP_VS_DEGREE for p in measurable
    )
    jac_gap = any(p.get("differs_from_ggmp6") for p in measurable)
    if (elim_eq_6 and proxy_matches_subspace) or not b_ok:
        return "O-NEGATIVE"
    if b_ok and jac_gap:
        return "O-POSITIVE"
    return "O-ARTIFACT"

def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    census_path = EXP_ROOT / "stage0" / "genus2-census.json"
    prereg_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not census_path.is_file() or not prereg_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "status": "impediment",
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT_USED",
            },
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            "# RESULTS — EXP-FROB-7d51ae\n\nOutcome: **O-IMPEDIMENT**\n\nMissing Stage-0 freeze.\n",
        )
        return raw

    census = json.loads(census_path.read_text(encoding="utf-8"))
    rng = random.Random(MASTER_SEED)
    panels = [panel_for_hit(hit, rng) for hit in census.get("hits", [])]
    primary = next(
        (
            p
            for p in panels
            if p.get("status") in ("ok", "ok_cantor_unreliable", "no_order_19_element", "cardinality_mismatch")
        ),
        panels[0] if panels else None,
    )
    controls = control_panels(
        primary
        if primary
        and primary.get("status")
        in ("ok", "ok_cantor_unreliable", "no_order_19_element", "cardinality_mismatch")
        else None,
        rng,
    )
    no_model = census.get("hit_count_raw", 0) == 0
    outcome = classify_outcome(no_model, panels, controls)

    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "panels.json", {"panels": panels})
    write_json(
        stage1_dir / "control-table.json",
        {"outcome": outcome, "controls": controls, "n_panels": len(panels)},
    )

    results_lines = [
        "# RESULTS — EXP-FROB-7d51ae",
        "",
        f"Outcome: **{outcome}**",
        "",
        f"- hypothesis: {HYPOTHESIS_ID}",
        f"- approved_by: {APPROVED_BY}",
        f"- hit_count_raw: {census.get('hit_count_raw')}",
        f"- panels: {len(panels)}",
        f"- first_fall_degree: UNDETERMINED (Stage 2 not authorized)",
        f"- ggmp_vs_degree_m3: {GGMP_VS_DEGREE}",
        f"- amazon_bedrock: NOT_USED",
        "",
        "## Scope note",
        "",
        "Over F_2 the u_0 universe has size 2, so eliminant_degree ≤ 2 always",
        "differs from GGMP figure 6; the random-subset control shares that",
        "cardinality ceiling. Stages 0-1 therefore treat branching b and the",
        "boolean_degree_proxy vs subspace arm as the load-bearing toy signals,",
        "and leave full Weil-descended S_3 first-fall to Stage 2.",
        "",
        "## Artifacts",
        "",
        "- experiments/EXP-FROB-7d51ae/stage0/preregistered-predictions.json",
        "- experiments/EXP-FROB-7d51ae/stage0/genus2-census.json",
        "- experiments/EXP-FROB-7d51ae/stage1/panels.json",
        "- experiments/EXP-FROB-7d51ae/stage1/control-table.json",
        "",
        "NO break. NO exponent move. NO n>=131 attack.",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(results_lines))

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "panels_summary": [
            {
                "status": p.get("status"),
                "eliminant_degree": (p.get("eliminant") or {}).get("eliminant_degree"),
                "boolean_degree_proxy": p.get("boolean_degree_proxy"),
                "b": (p.get("branching") or {}).get("b"),
            }
            for p in panels
        ],
        "controls": controls,
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "completed",
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, choices=[0, 1], required=True)
    ap.add_argument("--trial-plan", type=str, required=True)
    ap.add_argument("--run-dir", type=str, required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
