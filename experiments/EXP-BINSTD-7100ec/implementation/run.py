#!/usr/bin/env python3
"""EXP-BINSTD-7100ec Stage 0: HOLD-B curve-blindness census + rho gap + Delta.

Stage 0 only (grep + Python arithmetic). Freezes preregistered predictions,
runs C1 corpus census, independently recomputes C2 matched-rho table with the
(227,55) n=17 fixture, builds C3 signed Delta(m) table with branch labels,
restates cafcf1/HOLD-X4 support and cites the c07598 section, then writes
RESULTS.md with exactly one O-* label.

No Magma/Sage/AUXIN/Bedrock. No break / exponent / security verdict.
No lambda_x measurement. Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPERIMENT_ID = "EXP-BINSTD-7100ec"
HYPOTHESIS_ID = "H-BINSTD-72f0cc"
APPROVED_BY = "DEC-20261002-e4e699"
OUTCOMES = (
    "O-C1-HOLD",
    "O-C1-COUNTEREXAMPLE",
    "O-C2-FAIL",
    "O-C3-MIXED",
    "O-IMPEDIMENT",
)
FIPS_M = (163, 233, 283, 409, 571)
PREDICTED_GAPS = {163: 3.67, 233: 4.43, 283: 4.57, 409: 4.84, 571: 5.08}
GAP_TOL = 0.05
RHO_NEG_CONST = math.sqrt(math.pi) / 2.0
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO = EXP_ROOT.parents[1]
AUDIT = REPO / "analysis" / "binstd-curve-audit" / "binary-curve-params.txt"

FIPS_PAIRS = {
    163: ("sect163k1", "sect163r2"),
    233: ("sect233k1", "sect233r1"),
    283: ("sect283k1", "sect283r1"),
    409: ("sect409k1", "sect409r1"),
    571: ("sect571k1", "sect571r1"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    text = json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8")
    return sha256_bytes(text.encode())


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def parse_audit(path: Path) -> Dict[str, Dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"===== (\S+) =====", text)
    curves: Dict[str, Dict[str, Any]] = {}
    for i in range(1,len(blocks), 2):
        name, body = blocks[i], blocks[i + 1]
        bits_m = re.search(r"EC-Parameters:\s*\((\d+)\s*bit\)", body)
        order_m = re.search(r"Order:\s*\n((?:\s*[0-9a-fA-F:]+\n)+)", body)
        cof_m = re.search(r"Cofactor:\s*(\d+)", body)
        order = None
        if order_m:
            hexdigits = "".join(c for c in order_m.group(1) if c in "0123456789abcdefABCDEF")
            order = int(hexdigits, 16)
        curves[name] = {
            "name": name,
            "bits": int(bits_m.group(1)) if bits_m else None,
            "order_r": order,
            "cofactor_h": int(cof_m.group(1)) if cof_m else None,
        }
    return curves


def rho_neg_bits(r: int) -> float:
    return 0.5 * math.log2(math.pi * r / 4.0)


def rho_tau_bits(r: int, m: int) -> float:
    return 0.5 * math.log2(math.pi * r / (4.0 * m))


def n17_fixture() -> Dict[str, Any]:
    neg = int(round(RHO_NEG_CONST * (2 ** 8)))
    tau = int(round(neg / math.sqrt(17)))
    n = 2 ** 16
    return {
        "n": 17,
        "fixture_negation": neg,
        "fixture_tau": tau,
        "expected": [227, 55],
        "pass": neg == 227 and tau == 55,
        "continuous_negation": RHO_NEG_CONST * math.sqrt(n),
        "continuous_tau": math.sqrt(math.pi * n / (4.0 * 17)),
        "ratio_neg_over_tau": neg / tau if tau else None,
        "sqrt_17": math.sqrt(17),
        "convention": "negation 0.886*2^(n/2) with n=16 half; tau = neg/sqrt(17)",
    }


def build_c2(curves: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    gaps = {}
    for m, (k_name, b_name) in FIPS_PAIRS.items():
        k, b = curves[k_name], curves[b_name]
        if not k["order_r"] or not b["order_r"]:
            raise RuntimeError(f"missing order for {k_name}/{b_name}")
        k_rho_tau = rho_tau_bits(k["order_r"], m)
        b_rho_neg = rho_neg_bits(b["order_r"])
        h_bit = 0.0 if k["cofactor_h"] == b["cofactor_h"] else 0.5
        predicted = 0.5 * math.log2(m) + h_bit
        gap = b_rho_neg - k_rho_tau
        gaps[m] = {
            "Delta_rho_bits": gap,
            "predicted_0_5_log2_m_plus_hbit": predicted,
            "abs_err": abs(gap - predicted),
            "preregistered_target": PREDICTED_GAPS[m],
            "abs_err_vs_prereg": abs(gap - PREDICTED_GAPS[m]),
            "h_bit": h_bit,
            "K": {
                "name": k_name,
                "r": k["order_r"],
                "h": k["cofactor_h"],
                "rho_tau_bits": k_rho_tau,
                "rho_neg_bits": rho_neg_bits(k["order_r"]),
            },
            "B": {
                "name": b_name,
                "r": b["order_r"],
                "h": b["cofactor_h"],
                "rho_neg_bits": b_rho_neg,
            },
        }
        rows.append({"m": m, **gaps[m]})

    controls = {
        "sect193r1": {
            "has_frobenius_row": False,
            "note": "prime m=193 non-Koblitz; must NOT receive <tau,-1> baseline",
            "rho_neg_bits": rho_neg_bits(curves["sect193r1"]["order_r"]),
        },
        "sect193r2": {
            "has_frobenius_row": False,
            "note": "prime m=193 non-Koblitz; must NOT receive <tau,-1> baseline",
            "rho_neg_bits": rho_neg_bits(curves["sect193r2"]["order_r"]),
        },
        "sect239k1": {
            "has_frobenius_row": True,
            "note": "Koblitz not in FIPS; must receive a Frobenius row",
            "rho_neg_bits": rho_neg_bits(curves["sect239k1"]["order_r"]),
            "rho_tau_bits": rho_tau_bits(curves["sect239k1"]["order_r"], 239),
            "h": curves["sect239k1"]["cofactor_h"],
        },
    }
    max_err = max(g["abs_err_vs_prereg"] for g in gaps.values())
    fixture = n17_fixture()
    return {
        "audit_sha256": sha256_file(AUDIT),
        "convention": {
            "rho_neg": "0.5*log2(pi*r/4) = log2(0.886*sqrt(r))",
            "rho_tau": "0.5*log2(pi*r/(4*m))",
            "Delta_rho": "rho_neg(B-m) - rho_tau(K-m)",
        },
        "rows": rows,
        "gaps_by_m": {str(k): v for k, v in gaps.items()},
        "nearby_object_controls": controls,
        "n17_fixture": fixture,
        "max_abs_err_vs_prereg": max_err,
        "c2_pass": max_err <= GAP_TOL and fixture["pass"],
    }


def freeze_predictions() -> Dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "frozen_at": utc_now(),
        "C1_predicted_counterexample_count": 0,
        "C2_Delta_rho_targets_bits": {str(k): v for k, v in PREDICTED_GAPS.items()},
        "C2_gap_tolerance_bits": GAP_TOL,
        "C2_n17_fixture": [227, 55],
        "C3_blind_Delta_min_bits": 3.6,
        "C3_aware_relation_Delta_max_bits": -3.1,
        "consequence_under_C1": "five IC columns (one per m), not ten",
        "note": "Predictions frozen before result interpretation. Do not edit after Stage-0 freeze.",
        "amazon_bedrock": "NOT SELECTED",
    }


def c1_inclusion_rules() -> str:
    return """# C1 inclusion rules (EXP-BINSTD-7100ec Stage 0)

## In scope
- Files under `ledger/` and `knowledge/` whose text discusses binary /
  characteristic-two / FIPS-sect / Koblitz index-calculus **cost** laws
  (time, relation yield as a multiplicative cost, degree/size laws used as
  cost).
- A filed law is a counterexample to C1 if it reads curve coefficients `a` or
  `b` as an input to the cost expression other than through `lambda_x` / `r`
  (or an explicitly labelled Assumption-1 scalar named as such).

## Out of scope / pre-registered exceptions
- Trace-parity arity constraints `Tr(x)+Tr(a)` that bound admissible arity
  (constraint on `m`, not a multiplicative cost factor) — pre-registered
  exception class per HOLD-B / IDEA-20260922-1a081a review.
- Proposals that are only design text without a filed cost formula.
- Records filed after the Stage-0 freeze timestamp.

## Method
1. Scan `ledger/**/*.yaml` and `knowledge/**/*.md` for binary-IC cost markers.
2. For each candidate, record whether `a`/`b` appear outside `lambda_x` /
   yield / order contexts.
3. Emit `c1-census.json` with `counterexamples` list (possibly empty).
"""


def scan_c1() -> Dict[str, Any]:
    roots = [REPO / "ledger", REPO / "knowledge"]
    markers = re.compile(
        r"(index.?calculus|Semaev|factor.?base|relation.?collect|Koblitz|"
        r"sect1(63|93|233|239|283|409|571)|characteristic.?two|binary.?curve|"
        r"lambda_x|Frobenius.?blind|cost.?law)",
        re.I,
    )
    costish = re.compile(r"(cost|complexity|bit.?ops|T_IC|relation.?yield|degree.?law)", re.I)
    ab_cost = re.compile(
        r"(?:\bread(?:s|ing)?\b.{0,40}\b[ab]\b.{0,40}\bcost\b)|"
        r"(?:\bcost\b.{0,40}\bcurve\s+coefficient)|"
        r"(?:\bdepends on\b.{0,20}\b[ab]\b.{0,30}\b(?!lambda))",
        re.I,
    )
    lambda_ok = re.compile(r"lambda[_x]|yield|order\s+r\b", re.I)

    candidates: List[Dict[str, Any]] = []
    counterexamples: List[Dict[str, Any]] = []
    scanned = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".md"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            scanned += 1
            if not markers.search(text) or not costish.search(text):
                continue
            rel = path.relative_to(REPO).as_posix()
            ab_hits = [m.group(0) for m in ab_cost.finditer(text)]
            entry = {
                "path": rel,
                "binary_ic_markers": True,
                "cost_markers": True,
                "ab_cost_heuristic_hits": ab_hits[:5],
                "mentions_lambda_x": bool(re.search(r"lambda_x", text, re.I)),
            }
            candidates.append(entry)
            for hit in ab_hits:
                if lambda_ok.search(hit):
                    continue
                if re.search(r"Tr\s*\(.*a|trace.?parity|arity", hit, re.I):
                    entry.setdefault("exception_class", []).append("trace_parity_arity")
                    continue
                counterexamples.append(
                    {
                        "path": rel,
                        "hit": hit[:200],
                        "reason": "heuristic: a/b appears in cost phrasing outside lambda_x",
                    }
                )
                break

    return {
        "freeze_timestamp": utc_now(),
        "scanned_files": scanned,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "counterexamples": counterexamples,
        "counterexample_count": len(counterexamples),
        "pre_registered_exceptions": ["trace_parity_arity_constraint"],
        "method": "grep markers + ab_cost heuristic; not a substitute for human audit",
    }


def build_c3(c2: Dict[str, Any]) -> Dict[str, Any]:
    cells = []
    for m in FIPS_M:
        gap = c2["gaps_by_m"][str(m)]
        delta_rho = gap["Delta_rho_bits"]
        h_bit = gap["h_bit"]
        blind = {
            "m": m,
            "line_class": "frobenius_blind",
            "branch": "baseline_inherit",
            "Delta_bits": delta_rho,
            "sign_ok": delta_rho > 0 and delta_rho >= 3.6,
        }
        aware_rel = h_bit - 0.5 * math.log2(m)
        aware = {
            "m": m,
            "line_class": "frobenius_aware_relation",
            "branch": "relation_dominated_m_fold",
            "Delta_bits": aware_rel,
            "sign_ok": aware_rel < 0 and abs(aware_rel) >= 3.1,
        }
        aware_la = h_bit - 1.5 * math.log2(m)
        la = {
            "m": m,
            "line_class": "frobenius_aware_LA",
            "branch": "LA_dominated_m2",
            "Delta_bits": aware_la,
            "sign_ok": aware_la < 0,
            "note": "reported column only; C3 primary claim uses relation-dominated branch",
        }
        cells.extend([blind, aware, la])

    blind_ok = all(c["sign_ok"] for c in cells if c["line_class"] == "frobenius_blind")
    aware_ok = all(c["sign_ok"] for c in cells if c["line_class"] == "frobenius_aware_relation")
    return {
        "cells": cells,
        "blind_all_positive_ge_3_6": blind_ok,
        "aware_relation_all_negative_mag_ge_3_1": aware_ok,
        "c3_pass": blind_ok and aware_ok,
        "note": "Assumption-1 resolutions are inputs labelled per cell, never tested here.",
    }


def write_support_notes() -> None:
    write_text(
        EXP_ROOT / "stage0" / "support-restatement-cafcf1.md",
        """# HB1-2 support restatement (cafcf1 / HOLD-X4)

Before any HB1-2 Weil-support trigger for IDEA-20260922-1a081a / HOLD-B is
read as fired, restate support against HOLD-X4 /
IDEA-20260926-cafcf1 (EXP-BINSTD-c05a0f, PR #1562).

- This Stage-0 card does **not** re-execute EXP-BINSTD-c05a0f.
- Citation is by id. If required certificate bytes are absent on this
  checkout and cannot be fetched read-only, the honest label is
  `O-IMPEDIMENT`, not a negative reading of C1–C3.
- DEC-20260928-63addc HOLD-B condition: do not treat HB1-2 as fired without
  this restatement.

Status for this run: restatement recorded; no HB1-2 trigger is asserted here.
Amazon Bedrock is NOT SELECTED.
""",
    )
    write_text(
        EXP_ROOT / "stage0" / "c07598-section.md",
        """# Absorbed section: IDEA-20260922-c07598 symmetry ledger

HOLD-B absorbs IDEA-20260922-c07598 as a symmetry-ledger section (corrected
`sqrt(2k)` / `sqrt(k)` convention). The same idea is also designed separately
as EXP-BINSTD-e6fc82 (PR #1545).

- This card **cites** that section; it does **not** re-run EXP-BINSTD-e6fc82.
- Symmetry figures used for C2 follow `sqrt(pi*r/(4k))` with `k=m` on Koblitz
  rows and negation-only on random partners, matching CORR-20260922-81aeab /
  the 1a081a review recomputation.

Amazon Bedrock is NOT SELECTED.
""",
    )


def choose_outcome(c1: Dict[str, Any], c2: Dict[str, Any], c3: Dict[str, Any]) -> str:
    if c1["counterexample_count"] > 0:
        return "O-C1-COUNTEREXAMPLE"
    if not c2["c2_pass"]:
        return "O-C2-FAIL"
    if not c3["c3_pass"]:
        return "O-C3-MIXED"
    return "O-C1-HOLD"


def write_results(outcome: str, c1: Dict[str, Any], c2: Dict[str, Any], c3: Dict[str, Any]) -> None:
    lines = [
        f"# RESULTS — {EXPERIMENT_ID}",
        "",
        f"**{outcome}**",
        "",
        f"- Hypothesis: `{HYPOTHESIS_ID}`",
        f"- Approved by: `{APPROVED_BY}`",
        f"- Stage: 0 (grep + arithmetic)",
        f"- Recorded at: {utc_now()}",
        "",
        "## Scope",
        "",
        "Composition / indexing observations only. No break. No exponent.",
        "No security verdict. No Magma/Sage/AUXIN/Bedrock.",
        "",
        "## C1",
        "",
        f"- Candidates scanned into census: {c1['candidate_count']}",
        f"- Counterexamples: {c1['counterexample_count']}",
        "",
        "## C2",
        "",
        f"- max |gap - prereg| bits: {c2['max_abs_err_vs_prereg']:.4f} (tol {GAP_TOL})",
        f"- n=17 fixture pass: {c2['n17_fixture']['pass']} "
        f"({c2['n17_fixture']['fixture_negation']}, {c2['n17_fixture']['fixture_tau']})",
        "",
        "## C3",
        "",
        f"- blind all Delta>0 and >=3.6: {c3['blind_all_positive_ge_3_6']}",
        f"- aware relation-dominated all Delta<0 mag>=3.1: "
        f"{c3['aware_relation_all_negative_mag_ge_3_1']}",
        "",
        "## Consequence under C1-HOLD path",
        "",
        "Reachability table needs five IC columns (one per m), not ten.",
        "",
        "Amazon Bedrock: NOT SELECTED.",
        "",
    ]
    write_text(EXP_ROOT / "RESULTS.md", "\n".join(lines))


def write_manifest(run_dir: Path, stage: int, outcome: str, extra: Dict[str, Any]) -> None:
    lines = [
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"approved_by: {APPROVED_BY}",
        f"stage: {stage}",
        f"outcome: {outcome}",
        f"recorded_at: {utc_now()}",
        "amazon_bedrock: NOT SELECTED",
        "claims:",
        "  break: false",
        "  exponent_move: false",
        "  security_verdict: false",
    ]
    for k, v in extra.items():
        lines.append(f"{k}: {json.dumps(v)}")
    write_text(run_dir / "manifest.yaml", "\n".join(lines) + "\n")


def run_stage0(run_dir: Path) -> Dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    if not AUDIT.is_file():
        outcome = "O-IMPEDIMENT"
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "stage": 0,
            "status": "failed_infrastructure",
            "outcome": outcome,
            "reason": f"missing audit dump {AUDIT}",
            "amazon_bedrock": "NOT SELECTED",
            "claims": {"break": False, "exponent_move": False},
        }
        write_json(run_dir / "raw-result.json", raw)
        write_manifest(run_dir, 0, outcome, {"impediment": "missing_audit_dump"})
        write_text(
            EXP_ROOT / "RESULTS.md",
            f"# RESULTS — {EXPERIMENT_ID}\n\n**{outcome}**\n\nMissing audit dump.\n",
        )
        return raw

    curves = parse_audit(AUDIT)
    c2 = build_c2(curves)
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", freeze_predictions())
    write_text(EXP_ROOT / "stage0" / "c1-inclusion-rules.md", c1_inclusion_rules())
    write_support_notes()

    c1 = scan_c1()
    write_json(EXP_ROOT / "stage0" / "c1-census.json", c1)
    write_text(
        EXP_ROOT / "stage0" / "c1-census.md",
        "# C1 census\n\n"
        f"- scanned_files: {c1['scanned_files']}\n"
        f"- candidates: {c1['candidate_count']}\n"
        f"- counterexamples: {c1['counterexample_count']}\n"
        f"- freeze: {c1['freeze_timestamp']}\n",
    )
    write_json(EXP_ROOT / "stage0" / "c2-rho-table.json", c2)
    c3 = build_c3(c2)
    write_json(EXP_ROOT / "stage0" / "c3-delta-table.json", c3)

    outcome = choose_outcome(c1, c2, c3)
    write_results(outcome, c1, c2, c3)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed",
        "outcome": outcome,
        "c1_counterexamples": c1["counterexample_count"],
        "c2_pass": c2["c2_pass"],
        "c3_pass": c3["c3_pass"],
        "max_c2_err": c2["max_abs_err_vs_prereg"],
        "n17_fixture": c2["n17_fixture"],
        "amazon_bedrock": "NOT SELECTED",
        "claims": {"break": False, "exponent_move": False, "security_verdict": False},
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_manifest(
        run_dir,
        0,
        outcome,
        {
            "c1_counterexamples": c1["counterexample_count"],
            "c2_pass": c2["c2_pass"],
            "c3_pass": c3["c3_pass"],
        },
    )
    return raw


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=int, required=True, choices=[0])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args(argv)
    if args.stage != 0:
        print("only Stage 0 is authorized under this trial plan", file=sys.stderr)
        return 2
    raw = run_stage0(Path(args.run_dir))
    print(json.dumps({"ok": True, "outcome": raw.get("outcome"), "status": raw.get("status")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
