#!/usr/bin/env python3
"""EXP-CSIDH-999626 Stages 0-1 launcher (p=419 memory-cap probe vs blind control).

Stage 0: Zero-compute freeze of disc=-419, C/C_blind formulas, M labels,
         twin form enumerations, N=1 nearby object, and O-* rules.
Stage 1: Exhaustive reduced-form census of disc=-419 by two independent
         loops, certify N, evaluate C and C_blind at M=2 and M=M_free for
         G in {1,2}, and emit exactly one O-* label.

Observations only. No quantum algorithm. No CSIDH-512 bit level.
No Magma/Sage/Bedrock. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-CSIDH-999626"
HYPOTHESIS_ID = "H-CSIDH-73e6ab"
APPROVED_BY = "DEC-20261006-3cccf4"
TASK_ID = "TASK-20261006-5a2994"
SOURCE_IDEA = "IDEA-20261005-1896e8"
QUESTION_ID = "RQ-CSIDH-64343f"
DISC = -419
PINNED_P = 419
WRONG_DISC = -4 * 419
EXP_ROOT = Path(__file__).resolve().parents[1]
STAGE0_OK = "S0-FREEZE-OK"
STAGE1_LABELS = (
    "O-SEPARATES",
    "O-NO-BIND",
    "O-BLIND-MOVED",
    "O-G-NOT-COMMON",
    "O-N1-GAP",
    "O-MISMATCH",
    "O-WRONG-DISC",
    "O-IMPEDIMENT",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def claims() -> dict[str, bool]:
    return {"attack": False, "break": False, "exponent_move": False}


def is_reduced(a: int, b: int, c: int) -> bool:
    if a <= 0:
        return False
    if abs(b) > a or a > c:
        return False
    if abs(b) == a or a == c:
        return b >= 0
    return True


def form_disc(a: int, b: int, c: int) -> int:
    return b * b - 4 * a * c


def enumerate_a_outer(disc: int) -> list[tuple[int, int, int]]:
    if disc >= 0:
        raise ValueError("need negative discriminant")
    forms: list[tuple[int, int, int]] = []
    a_max = int(math.isqrt((-disc) // 3)) + 2
    for a in range(1, a_max + 1):
        for b in range(-a, a + 1):
            num = b * b - disc
            den = 4 * a
            if num % den != 0:
                continue
            c = num // den
            if is_reduced(a, b, c) and form_disc(a, b, c) == disc:
                forms.append((a, b, c))
    return sorted(forms)


def enumerate_b_outer(disc: int) -> list[tuple[int, int, int]]:
    if disc >= 0:
        raise ValueError("need negative discriminant")
    forms: list[tuple[int, int, int]] = []
    a_max = int(math.isqrt((-disc) // 3)) + 2
    b_max = a_max
    seen: set[tuple[int, int, int]] = set()
    for b in range(-b_max, b_max + 1):
        for a in range(max(1, abs(b)), a_max + 1):
            num = b * b - disc
            den = 4 * a
            if num % den != 0:
                continue
            c = num // den
            if is_reduced(a, b, c) and form_disc(a, b, c) == disc:
                seen.add((a, b, c))
    return sorted(seen)


def n_from_class_number(n_cls: int) -> int:
    return max(1, math.ceil(math.log2(max(n_cls, 2))))


def m_free_from_n(n: int) -> int:
    return 2 ** math.ceil(math.sqrt(n))


def probe_c(g: int, m: int, n: int, m_free: int) -> int:
    if m <= 0:
        raise ValueError("M must be positive")
    return g * (2 ** math.ceil(math.sqrt(n))) * math.ceil(m_free / m)


def c_blind(g: int, n: int) -> int:
    return g * (2 ** math.ceil(math.sqrt(n)))


def freeze_payload() -> dict[str, Any]:
    return {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "pinned": {
            "p": PINNED_P,
            "p_check": "4*3*5*7-1 and p≡3 mod 4",
            "order": "Z[(1+sqrt(-p))/2]",
            "disc": DISC,
            "wrong_disc_control": WRONG_DISC,
        },
        "formulas": {
            "n": "max(1, ceil(log2(max(N,2))))",
            "M_free": "2^{ceil(sqrt(n))}",
            "C": "G * 2^{ceil(sqrt(n))} * ceil(M_free/M)",
            "C_blind": "G * 2^{ceil(sqrt(n))}",
            "source": "IDEA-20261005-1896e8; stand-in inside KN-LIT-071 shape",
        },
        "labels_M": ["2", "M_free"],
        "G_levels": [1, 2],
        "twin_enumeration": {
            "route_A": "a-outer then b in [-a,a]",
            "route_B": "b-outer then a >= |b|",
        },
        "nearby_object": {
            "forced_N": 1,
            "note": "Not asserted to be the class number of -419. Must return ratio 1.",
        },
        "not_claimed": [
            "CSIDH-512 security level",
            "Peikert simulator reproduction",
            "SQALE cost-model reproduction",
            "quantum algorithm execution",
            "ordinary ECDLP improvement",
        ],
        "source_idea": SOURCE_IDEA,
        "hypothesis_id": HYPOTHESIS_ID,
        "experiment_id": EXPERIMENT_ID,
    }


def stage0(run_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    freeze = freeze_payload()
    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", {
        "amazon_bedrock": "NOT SELECTED",
        "decision_rules": {
            "O-SEPARATES": "enumerations agree; M_free>=4; C(1,2)/C(1,M_free) integer >=2; C_blind ratio=1; G-scale leaves ratios unchanged; N=1 ratio=1",
            "O-NO-BIND": "enumerations agree and M_free<4 (ratio cannot be >=2)",
            "O-BLIND-MOVED": "C_blind differs across M labels",
            "O-G-NOT-COMMON": "either ratio changes when G is replaced by 2G",
            "O-N1-GAP": "forced N=1 produces ratio other than 1",
            "O-MISMATCH": "the two form enumerations disagree on N or on the form set",
            "O-WRONG-DISC": "an enumeration used disc=-4*419 rather than -419",
            "O-IMPEDIMENT": "timeout/crash/infra; never mathematical negative",
        },
        "numeric_N_not_preregistered": True,
        "split_threshold": 2,
        "source_idea": SOURCE_IDEA,
    })
    write_json(stage0_dir / "protocol-freeze.json", freeze)
    write_text(stage0_dir / "worksheet-note.md", (
        "# Stage 0 freeze — EXP-CSIDH-999626\n\n"
        "Pinned: p=419, disc=-419 (not -4*419).\n\n"
        "C(G,M)=G*2^{ceil(sqrt(n))}*ceil(M_free/M); "
        "C_blind drops the ceil(M_free/M) factor.\n\n"
        "Nearby object N=1 must return ratio 1.\n"
        "No form census in this stage. Amazon Bedrock is NOT SELECTED.\n"
    ))
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": claims(),
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "result": {
            "artifacts": [
                "stage0/preregistered-predictions.json",
                "stage0/protocol-freeze.json",
                "stage0/worksheet-note.md",
            ],
            "note": "Zero-compute freeze. Stage 1 performs the census.",
            "outcome": STAGE0_OK,
            "stage": 0,
        },
        "source_idea": SOURCE_IDEA,
        "task_id": TASK_ID,
        "trial_plan_approved_by": plan.get("approved_by"),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(run_dir / "manifest.yaml", (
        f"amazon_bedrock: NOT SELECTED\n"
        f"experiment_id: {EXPERIMENT_ID}\n"
        f"hypothesis_id: {HYPOTHESIS_ID}\n"
        f"approved_by: {APPROVED_BY}\n"
        f"outcome: {STAGE0_OK}\n"
        f"stage: 0\n"
        f"wrap_note: 'Nested run: wrapped flat manifest for validate_ledger'\n"
    ))
    write_text(run_dir / "RESULTS.md", (
        f"# RUN Stage 0 — {EXPERIMENT_ID}\n\nOutcome: **{STAGE0_OK}**\n\nProtocol freeze only.\n"
    ))
    return raw


def ratios_for(n_cls: int) -> dict[str, Any]:
    n = n_from_class_number(n_cls)
    m_free = m_free_from_n(n)
    out: dict[str, Any] = {"n": n, "M_free": m_free}
    for g in (1, 2):
        c2 = probe_c(g, 2, n, m_free)
        cm = probe_c(g, m_free, n, m_free)
        ratio = c2 / cm
        b2 = c_blind(g, n)
        bm = c_blind(g, n)
        out[f"G{g}"] = {
            "C_M2": c2,
            "C_Mfree": cm,
            "ratio": ratio,
            "C_blind_M2": b2,
            "C_blind_Mfree": bm,
            "blind_ratio": b2 / bm,
        }
    return out


def decide_label(payload: dict[str, Any]) -> str:
    if payload.get("wrong_disc"):
        return "O-WRONG-DISC"
    if payload.get("mismatch"):
        return "O-MISMATCH"
    if payload.get("n1_gap"):
        return "O-N1-GAP"
    if payload.get("blind_moved"):
        return "O-BLIND-MOVED"
    if payload.get("g_not_common"):
        return "O-G-NOT-COMMON"
    if payload["M_free"] < 4:
        return "O-NO-BIND"
    ratio = payload["G1"]["ratio"]
    if ratio == int(ratio) and int(ratio) >= 2:
        return "O-SEPARATES"
    return "O-NO-BIND"


def stage1(run_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    freeze_path = EXP_ROOT / "stage0" / "protocol-freeze.json"
    if not freeze_path.exists():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 1")
    forms_a = enumerate_a_outer(DISC)
    forms_b = enumerate_b_outer(DISC)
    mismatch = forms_a != forms_b
    n_cls = len(forms_a)
    # Wrong-disc control: compute count at -1676 but do not use it as N.
    forms_wrong = enumerate_a_outer(WRONG_DISC)
    wrong_disc_used = False
    stats = ratios_for(n_cls)
    n1 = ratios_for(1)
    n1_gap = n1["G1"]["ratio"] != 1
    blind_moved = stats["G1"]["blind_ratio"] != 1 or stats["G2"]["blind_ratio"] != 1
    g_not_common = (
        stats["G1"]["ratio"] != stats["G2"]["ratio"]
        or stats["G2"]["C_M2"] != 2 * stats["G1"]["C_M2"]
        or stats["G2"]["C_Mfree"] != 2 * stats["G1"]["C_Mfree"]
    )
    payload = {
        "N": n_cls,
        "N_route_A": len(forms_a),
        "N_route_B": len(forms_b),
        "mismatch": mismatch,
        "wrong_disc": wrong_disc_used,
        "wrong_disc_count_information_only": len(forms_wrong),
        "n1_gap": n1_gap,
        "blind_moved": blind_moved,
        "g_not_common": g_not_common,
        "M_free": stats["M_free"],
        "n": stats["n"],
        "G1": stats["G1"],
        "G2": stats["G2"],
        "N1_control": n1,
        "forms": [{"a": a, "b": b, "c": c} for a, b, c in forms_a],
    }
    label = decide_label(payload)
    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "census.json", {
        "amazon_bedrock": "NOT SELECTED",
        "disc": DISC,
        "p": PINNED_P,
        "N": n_cls,
        "N_route_A": len(forms_a),
        "N_route_B": len(forms_b),
        "forms": payload["forms"],
        "n": stats["n"],
        "M_free": stats["M_free"],
        "G1": stats["G1"],
        "G2": stats["G2"],
        "reconstruction_ok": not mismatch,
    })
    write_json(stage1_dir / "control-table.json", {
        "amazon_bedrock": "NOT SELECTED",
        "N1_control": n1,
        "wrong_disc": {
            "disc": WRONG_DISC,
            "count_information_only": len(forms_wrong),
            "used_as_N": False,
        },
        "blind_ratio_G1": stats["G1"]["blind_ratio"],
        "g_scale_ok": not g_not_common,
        "twin_ok": not mismatch,
    })
    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}\n"
        f"Approved by: {APPROVED_BY}\n"
        f"Task: {TASK_ID}\n"
        f"Source: {SOURCE_IDEA}\n\n"
        f"Stage-1 package outcome: **{label}**\n\n"
        f"| Quantity | Value |\n| --- | --- |\n"
        f"| disc | {DISC} |\n"
        f"| N (route A / B) | {len(forms_a)} / {len(forms_b)} |\n"
        f"| n | {stats['n']} |\n"
        f"| M_free | {stats['M_free']} |\n"
        f"| C(1,2)/C(1,M_free) | {stats['G1']['ratio']} |\n"
        f"| C_blind ratio | {stats['G1']['blind_ratio']} |\n"
        f"| G=2 ratios unchanged | {not g_not_common} |\n"
        f"| N=1 nearby ratio | {n1['G1']['ratio']} |\n\n"
        "Instrument C is defined in IDEA-20261005-1896e8. It is not a CSIDH-512 "
        "security level, not Peikert's simulator, and not SQALE. No quantum "
        "algorithm was run. Amazon Bedrock is NOT SELECTED.\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    write_text(run_dir / "RESULTS.md", results)
    raw = {
        "amazon_bedrock": "NOT SELECTED",
        "approved_by": APPROVED_BY,
        "claims": claims(),
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "result": {
            "N": n_cls,
            "M_free": stats["M_free"],
            "artifacts": [
                "stage1/census.json",
                "stage1/control-table.json",
            ],
            "note": "Exact form census + integer probe. No quantum run. No CSIDH-512 figure.",
            "outcome": label,
            "ratio_G1": stats["G1"]["ratio"],
            "reconstruction_ok": not mismatch,
            "stage": 1,
        },
        "source_idea": SOURCE_IDEA,
        "task_id": TASK_ID,
        "trial_plan_approved_by": plan.get("approved_by"),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(run_dir / "manifest.yaml", (
        f"amazon_bedrock: NOT SELECTED\n"
        f"experiment_id: {EXPERIMENT_ID}\n"
        f"hypothesis_id: {HYPOTHESIS_ID}\n"
        f"approved_by: {APPROVED_BY}\n"
        f"outcome: {label}\n"
        f"stage: 1\n"
        f"wrap_note: 'Nested run: wrapped flat manifest for validate_ledger'\n"
    ))
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("experiment_id mismatch", file=sys.stderr)
        return 2
    started = time.time()
    try:
        if args.stage == 0:
            stage0(run_dir, plan)
        else:
            stage1(run_dir, plan)
    except FileExistsError as exc:
        print(f"O-IMPEDIMENT overwrite-refuse: {exc}", file=sys.stderr)
        return 3
    print(f"stage {args.stage} complete in {time.time()-started:.3f}s amazon_bedrock=NOT_SELECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
