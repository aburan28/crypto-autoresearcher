#!/usr/bin/env python3
"""Summarize preregistered rule-replay scout sweeps and promotion gates."""

from __future__ import annotations

import argparse
import glob
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WINDOW_RE = re.compile(r"ruleprefix2_(?P<window>\d+_\d+)_order(?P<order>\d+)_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    return match.group("window") if match else ""


def support_for_form(form: dict[str, Any]) -> list[int]:
    coeffs = form.get("coeffs") or []
    return [idx for idx, coeff in enumerate(coeffs[1:]) if int_value(coeff) != 0]


def cert_supports(payload: dict[str, Any]) -> list[list[int]]:
    certs = payload.get("certificates") or []
    supports: list[list[int]] = []
    for cert in certs:
        if not isinstance(cert, dict):
            continue
        supports.extend(
            support_for_form(form)
            for form in cert.get("forms") or []
            if isinstance(form, dict)
        )
    return supports


def gate_path(state_dir: Path, prefix: str, window: str, suffix: str) -> Path:
    return state_dir / f"{prefix}_strictbridge11779_ruleprefix2_{window}_{suffix}.json"


def maybe_load_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = load_json(path)
    return {
        "claim_status": payload.get("claim_status"),
        "path": str(path),
        "summary": payload.get("candidate_summary") or payload.get("summary") or {},
    }


def summarize_artifact(path: Path, state_dir: Path) -> dict[str, Any]:
    payload = load_json(path)
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    window = window_from_path(path)
    verified = summary.get("best_verified") or []
    candidate_count = int_value(summary.get("candidate_certificate_count"))
    trace_count = int_value(summary.get("nonzero_projection_selection_count"))
    verified_count = int_value(summary.get("verified_nonzero_projection_selection_count"))
    direct_values = [
        value
        for value in (float_value(row.get("direct_ops_over_rho")) for row in verified if isinstance(row, dict))
        if value is not None
    ]
    deficiency = gate_path(
        state_dir,
        "low_term_total2_deficiency_direction_scorer",
        window,
        "order11779_probe",
    )
    bank = gate_path(
        state_dir,
        "low_term_total2_target_eliminated_factor_relation_bank",
        window,
        "repair_probe",
    )
    family = gate_path(
        state_dir,
        "low_term_total2_factor_substitution_family_holdout_scout",
        window,
        "family36_probe",
    )
    if candidate_count:
        category = "verified_bridge"
    elif trace_count:
        category = "trace_only"
    else:
        category = "no_projection"
    return {
        "best_direct_ops_over_rho": min(direct_values) if direct_values else None,
        "candidate_certificate_count": candidate_count,
        "category": category,
        "claim_status": payload.get("claim_status"),
        "direct_below_rho_verified_count": int_value(summary.get("direct_below_rho_verified_count")),
        "form_supports": cert_supports(payload),
        "gates": {
            "deficiency": maybe_load_summary(deficiency),
            "family36_holdout": maybe_load_summary(family),
            "repair_bank": maybe_load_summary(bank),
        },
        "path": str(path),
        "tested_selection_count": int_value(summary.get("tested_selection_count")),
        "verified_nonzero_projection_selection_count": verified_count,
        "window": window,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glob", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, default=Path("ecdlp_index_calculus_state"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in sorted(glob.glob(args.glob))]
    rows = [summarize_artifact(path, args.state_dir) for path in paths]
    categories = Counter(row["category"] for row in rows)
    status_counts = Counter(row["claim_status"] for row in rows)
    totals = {
        "candidate_certificate_count": sum(int_value(row.get("candidate_certificate_count")) for row in rows),
        "direct_below_rho_verified_count": sum(int_value(row.get("direct_below_rho_verified_count")) for row in rows),
        "nonzero_projection_selection_count": sum(
            int_value((load_json(Path(row["path"])).get("summary") or {}).get("nonzero_projection_selection_count"))
            for row in rows
        ),
        "tested_selection_count": sum(int_value(row.get("tested_selection_count")) for row in rows),
        "verified_nonzero_projection_selection_count": sum(
            int_value(row.get("verified_nonzero_projection_selection_count")) for row in rows
        ),
    }
    payload = {
        "category_counts": dict(sorted(categories.items())),
        "claim_status_counts": dict(sorted(status_counts.items())),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rule replay is tied to the current low-term factor namespace and strict order-11779 nullspace frontier.",
            "HEURISTIC: survival rates are scheduling evidence, not asymptotic complexity claims.",
            "NO SPEEDUP CLAIM: relation collection, filtering, sparse rank, and arbitrary target descent remain open cost gates.",
        ],
        "rows": rows,
        "schema": "ecdlp.low_term_total2_rule_replay_sweep_summarizer.v1",
        "source_glob": args.glob,
        "summary": {
            "best_verified_direct_ops_over_rho": min(
                [row["best_direct_ops_over_rho"] for row in rows if row["best_direct_ops_over_rho"] is not None],
                default=None,
            ),
            "positive_window_count": categories.get("verified_bridge", 0),
            "trace_only_window_count": categories.get("trace_only", 0),
            "window_count": len(rows),
            **totals,
        },
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
