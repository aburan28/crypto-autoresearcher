#!/usr/bin/env python3
"""EXP-FROB-f495ea Stages 0-1 launcher (frozen contract v1).

Stage 0: Genus-1 Artin-Schreier census (deg-3 odd f over F_2) — N_1 in
         {1,2,3,4,5}; freeze preregistered predictions; dual count check.
Stage 1: Hit counts at genus 5 (deg 11) and genus 6 (deg 13): number of
         F_2-normal-form models with 131 | #Jac(F_2)=P(1); genus-2
         histogram for H1; write RESULTS.md with exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131
attack. Amazon Bedrock is not selected.
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

from gf2 import (  # noqa: E402
    Field,
    as_add_h2_h,
    eval_poly_f2,
    is_monic_degree,
    poly_compose_x_plus_b,
    poly_degree,
)

EXPERIMENT_ID = "EXP-FROB-f495ea"
HYPOTHESIS_ID = "H-FROB-f3d248"
APPROVED_BY = "DEC-20261002-cf888a"
TARGET_PRIME = 131
LADDER_PRIMES = (19, 23, 31, 41)
EXP_ROOT = Path(__file__).resolve().parents[1]

# Genus g = (deg f - 1) // 2 for odd-degree Artin-Schreier y^2+y=f(x).
GENUS_DEG = {1: 3, 2: 5, 5: 11, 6: 13}


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


def point_count_as(f_coeffs: int, k: int) -> int:
    """#C(F_{2^k}) for affine AS y^2+y=f(x) plus one point at infinity.

    For each x, the equation in y has 2 solutions iff Tr(f(x))=0, else 0.
    """
    field = Field(k)
    zeros = 0
    for x in range(1 << k):
        fx = eval_poly_f2(f_coeffs, x, field)
        if field.trace(fx) == 0:
            zeros += 1
    return 1 + 2 * zeros


def point_count_as_alt(f_coeffs: int, k: int) -> int:
    """Second implementation: expand f in the field basis and count via table."""
    field = Field(k)
    # Precompute powers of x for each x — identical semantics, different loop.
    n = 1  # infinity
    deg = poly_degree(f_coeffs)
    for x in range(1 << k):
        # Evaluate by summing coeff_i * x^i
        acc = 0
        xp = 1
        for i in range(deg + 1):
            if (f_coeffs >> i) & 1:
                acc ^= xp
            xp = field.mul(xp, x)
        if field.trace(acc) == 0:
            n += 2
    return n


def lpoly_from_point_counts(q: int, genus: int, counts: list[int]) -> list[int]:
    """Return coefficients a_0..a_{2g} of L(T)=prod(1-alpha_i T) from N_1..N_g.

    Uses Newton identities: n a_n = -sum_{j=1}^n P_j a_{n-j}, P_j = q^j+1-N_j.
    Functional equation fills a_{2g-i} = q^{g-i} a_i.
    """
    if len(counts) < genus:
        raise ValueError("need N_1..N_g")
    g = genus
    a = [0] * (2 * g + 1)
    a[0] = 1
    P = [0] * (2 * g + 1)
    for j in range(1, g + 1):
        P[j] = (q**j) + 1 - counts[j - 1]
    for n in range(1, g + 1):
        s = 0
        for j in range(1, n + 1):
            s += P[j] * a[n - j]
        if s % n != 0:
            # Over integers the division must be exact for a Weil polynomial.
            raise ValueError(f"Newton identity not integral at n={n}: s={s}")
        a[n] = -s // n
    # Functional equation
    for i in range(g):
        a[2 * g - i] = (q ** (g - i)) * a[i]
    a[g]  # middle already set when g even? For i=g from FE: a_g = q^0 a_g.
    # When only first g coeffs from Newton, FE sets a_{g+1}..a_{2g}.
    # For the middle coefficient when using FE with i=g: a_g = a_g — OK.
    # But Newton only computed a_1..a_g; for hyperelliptic the middle a_g is
    # already from Newton. FE for i=0..g-1 sets the upper half.
    return a


def jac_order_f2(f_coeffs: int, genus: int) -> dict[str, Any]:
    counts = [point_count_as(f_coeffs, k) for k in range(1, genus + 1)]
    a = lpoly_from_point_counts(2, genus, counts)
    p1 = sum(a)
    return {
        "f": f_coeffs,
        "f_hex": hex(f_coeffs),
        "genus": genus,
        "N": counts,
        "L_coeffs": a,
        "P1": p1,
        "divisible_by_131": (p1 % TARGET_PRIME) == 0,
        "ladder_divisors": [p for p in LADDER_PRIMES if p1 % p == 0],
    }


def normal_form_orbit_min(f: int, deg: int) -> int:
    """Lex-minimal representative under f(x+b)+h^2+h, b in F_2, deg h <= deg//2."""
    best = None
    max_h_deg = deg // 2
    # h runs over all polys of degree <= max_h_deg
    for h in range(1 << (max_h_deg + 1)):
        for b in (0, 1):
            g = poly_compose_x_plus_b(f, b)
            g = as_add_h2_h(g, h)
            if not is_monic_degree(g, deg):
                continue
            if best is None or g < best:
                best = g
    if best is None:
        raise RuntimeError(f"no monic degree-{deg} in orbit of {f:#x}")
    return best


def enumerate_normal_forms(deg: int) -> list[int]:
    """All monic degree-deg F_2-polys, reduced to AS normal-form orbit mins."""
    seen: set[int] = set()
    forms: list[int] = []
    # Monic of degree deg: leading bit set; lower deg bits free → 2^deg candidates
    leading = 1 << deg
    for lower in range(1 << deg):
        f = leading | lower
        rep = normal_form_orbit_min(f, deg)
        if rep not in seen:
            seen.add(rep)
            forms.append(rep)
    forms.sort()
    return forms


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    deg = GENUS_DEG[1]
    forms = enumerate_normal_forms(deg)
    rows = []
    bad = []
    for f in forms:
        n1 = point_count_as(f, 1)
        n1b = point_count_as_alt(f, 1)
        ok = n1 == n1b and n1 in {1, 2, 3, 4, 5}
        row = {
            "f": f,
            "f_hex": hex(f),
            "N1": n1,
            "N1_alt": n1b,
            "in_elliptic_range": n1 in {1, 2, 3, 4, 5},
            "dual_agree": n1 == n1b,
            "ok": ok,
        }
        rows.append(row)
        if not ok:
            bad.append(row)

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "frozen_at_stage": 0,
        "predictions": {
            "genus1_N1_universe": [1, 2, 3, 4, 5],
            "genus1_normal_form_count": len(forms),
            "target_prime": TARGET_PRIME,
            "ladder_primes": list(LADDER_PRIMES),
            "hit_count_g5_is_integer": True,
            "hit_count_g6_is_integer": True,
            "stage1_decides_O_HIT_or_O_EMPTY": True,
        },
        "genus1_census_ok": len(bad) == 0,
        "genus1_rows": rows,
    }
    freeze = {
        "experiment_id": EXPERIMENT_ID,
        "arm": "genus1_census",
        "degree": deg,
        "normal_form_count": len(forms),
        "all_N1_in_1_to_5": len(bad) == 0,
        "dual_count_failures": [r for r in rows if not r["dual_agree"]],
        "bad_rows": bad,
        "amazon_bedrock": "NOT_USED",
    }

    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    write_json(stage0_dir / "genus1-census.json", freeze)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed" if len(bad) == 0 else "artifact",
        "genus1_census_ok": len(bad) == 0,
        "normal_form_count": len(forms),
        "freeze": freeze,
        "preregistered": {
            "genus1_N1_universe": [1, 2, 3, 4, 5],
            "target_prime": TARGET_PRIME,
        },
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                "stage: 0",
                "arm: genus1_census",
                f"approved_by: {APPROVED_BY}",
                f"genus1_census_ok: {str(len(bad) == 0).lower()}",
                "artifacts:",
                "  - raw-result.json",
                "  - manifest.yaml",
                "stage0_paths:",
                "  - experiments/EXP-FROB-f495ea/stage0/preregistered-predictions.json",
                "  - experiments/EXP-FROB-f495ea/stage0/genus1-census.json",
                "scientific_conclusion: null",
                "amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    # Gate: Stage 0 freeze must exist and pass
    g1_path = EXP_ROOT / "stage0" / "genus1-census.json"
    if not g1_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 1,
            "status": "impediment",
            "outcome": "O-IMPEDIMENT",
            "reason": "missing stage0/genus1-census.json",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        return raw

    g1 = json.loads(g1_path.read_text(encoding="utf-8"))
    if not g1.get("all_N1_in_1_to_5"):
        outcome = "O-ARTIFACT"
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 1,
            "status": "artifact",
            "outcome": outcome,
            "reason": "genus-1 census failed; table void",
            "amazon_bedrock": "NOT_USED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: {outcome}\n",
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            f"# RESULTS — {EXPERIMENT_ID}\n\nOutcome: **{outcome}**\n\n"
            "Genus-1 census failed; no hit counts kept.\n",
        )
        return raw

    # Genus-2 histogram (H1 validation arm): all normal forms deg 5
    g2_forms = enumerate_normal_forms(GENUS_DEG[2])
    g2_hist: dict[str, int] = {}
    g2_rows = []
    for f in g2_forms:
        info = jac_order_f2(f, 2)
        key = str(info["P1"])
        g2_hist[key] = g2_hist.get(key, 0) + 1
        g2_rows.append({"f_hex": info["f_hex"], "P1": info["P1"], "N": info["N"]})
        # Weil ceiling for g=2,q=2: (1+sqrt(2))^4 ≈ 33.97
        if info["P1"] > 34 or info["P1"] < 1:
            outcome = "O-ARTIFACT"
            raw = {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "outcome": outcome,
                "reason": f"genus-2 P1={info['P1']} outside Weil ceiling",
                "amazon_bedrock": "NOT_USED",
                "claims": {"break": False, "exponent_move": False},
            }
            write_json(run_dir / "raw-result.json", raw)
            write_text(
                run_dir / "manifest.yaml",
                f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: {outcome}\n",
            )
            return raw

    # Genus 5 and 6 hit tables
    panels: dict[str, Any] = {}
    hits: dict[str, list[dict[str, Any]]] = {}
    for genus in (5, 6):
        deg = GENUS_DEG[genus]
        forms = enumerate_normal_forms(deg)
        hit_rows = []
        # Dual-count check on five fixed polynomials (first five forms)
        dual_ok = True
        dual_checks = []
        for f in forms[:5]:
            n1a = point_count_as(f, 1)
            n1b = point_count_as_alt(f, 1)
            dual_checks.append({"f_hex": hex(f), "N1": n1a, "N1_alt": n1b, "ok": n1a == n1b})
            if n1a != n1b:
                dual_ok = False
        if not dual_ok:
            outcome = "O-ARTIFACT"
            raw = {
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "outcome": outcome,
                "reason": "dual point-count disagreement",
                "dual_checks": dual_checks,
                "amazon_bedrock": "NOT_USED",
                "claims": {"break": False, "exponent_move": False},
            }
            write_json(run_dir / "raw-result.json", raw)
            write_text(
                run_dir / "manifest.yaml",
                f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: {outcome}\n",
            )
            write_text(
                EXP_ROOT / "RESULTS.md",
                f"# RESULTS — {EXPERIMENT_ID}\n\nOutcome: **{outcome}**\n\n"
                "Dual point-count implementations disagree.\n",
            )
            return raw

        for f in forms:
            info = jac_order_f2(f, genus)
            if info["divisible_by_131"]:
                hit_rows.append(
                    {
                        "f_hex": info["f_hex"],
                        "P1": info["P1"],
                        "N": info["N"],
                        "ladder_divisors": info["ladder_divisors"],
                    }
                )
        panels[f"genus_{genus}"] = {
            "degree": deg,
            "normal_form_count": len(forms),
            "hit_count_131": len(hit_rows),
            "dual_checks": dual_checks,
        }
        hits[f"genus_{genus}"] = hit_rows

    hit_g5 = panels["genus_5"]["hit_count_131"]
    hit_g6 = panels["genus_6"]["hit_count_131"]
    if hit_g5 >= 1 or hit_g6 >= 1:
        outcome = "O-HIT"
    else:
        outcome = "O-EMPTY"

    # Ladder note: Stage 1 records which ladder primes divide any P1 among
    # scanned forms; eliminant degree is Stage 2 (not authorized here).
    ladder_hits = []
    for genus in (5, 6):
        for row in hits[f"genus_{genus}"]:
            for p in row["ladder_divisors"]:
                ladder_hits.append({"genus": genus, "prime": p, "f_hex": row["f_hex"], "P1": row["P1"]})
    # Also scan genus-2 forms for ladder primes (toy)
    for row in g2_rows:
        for p in LADDER_PRIMES:
            if row["P1"] % p == 0:
                ladder_hits.append({"genus": 2, "prime": p, "f_hex": row["f_hex"], "P1": row["P1"]})

    control_table = {
        "genus1_ok": True,
        "genus2_histogram_P1": g2_hist,
        "genus2_form_count": len(g2_forms),
        "dual_count_instrument": "point_count_as vs point_count_as_alt on five forms per genus",
        "tau_canonicalisation_cost_field_additions": 1,
        "ladder_hits_recorded": ladder_hits,
        "eliminant_degree": "UNMEASURED_STAGE2",
    }

    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "panels.json", {"panels": panels, "hits": hits})
    write_json(stage1_dir / "control-table.json", control_table)

    results = "\n".join(
        [
            f"# RESULTS — {EXPERIMENT_ID}",
            "",
            f"Hypothesis: {HYPOTHESIS_ID}",
            f"Approved by: {APPROVED_BY}",
            f"Source idea: IDEA-20261002-8f26ce",
            "",
            f"## Outcome: **{outcome}**",
            "",
            "Exactly one O-* label from H-FROB-f3d248.",
            "",
            "### Hit counts (131 | P(1))",
            f"- genus 5 (deg 11): **{hit_g5}** / {panels['genus_5']['normal_form_count']} normal forms",
            f"- genus 6 (deg 13): **{hit_g6}** / {panels['genus_6']['normal_form_count']} normal forms",
            "",
            "### Controls",
            "- Genus-1 N_1 census in {1,2,3,4,5}: PASS (Stage 0)",
            "- Dual point-count agreement on five forms/genus: PASS",
            f"- Genus-2 P(1) histogram: `{json.dumps(g2_hist, sort_keys=True)}`",
            "- Tau-orbit canonicalisation cost: 1 field addition (predicted)",
            "- Eliminant degree on ladder: UNMEASURED (Stage 2 not authorized)",
            "",
            "### Scope",
            "- Toy / arithmetic-table tier. No ECDLP solve. No n>=131 attack.",
            "- A zero hit count does not exclude non-Artin-Schreier Jacobians.",
            "- Amazon Bedrock was not used.",
            "",
            "### Artifacts",
            "- experiments/EXP-FROB-f495ea/stage0/",
            "- experiments/EXP-FROB-f495ea/stage1/panels.json",
            "- experiments/EXP-FROB-f495ea/stage1/control-table.json",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "hit_count_g5": hit_g5,
        "hit_count_g6": hit_g6,
        "panels": panels,
        "control_table": control_table,
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {"break": False, "exponent_move": False},
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                "stage: 1",
                "arm: as_hit_table",
                f"approved_by: {APPROVED_BY}",
                f"outcome: {outcome}",
                f"hit_count_g5: {hit_g5}",
                f"hit_count_g6: {hit_g6}",
                "artifacts:",
                "  - raw-result.json",
                "  - manifest.yaml",
                "scientific_conclusion: null",
                "amazon_bedrock: NOT_USED",
                "",
            ]
        ),
    )
    return raw


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=int, required=True, choices=[0, 1])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args()
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1":
        print("unsupported trial plan schema", file=sys.stderr)
        return 2
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial plan experiment_id mismatch", file=sys.stderr)
        return 2
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
