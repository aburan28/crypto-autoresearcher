#!/usr/bin/env python3
"""Postprocess fresh target-67 windows into factor-rank frontier evidence.

The live fresh-window launcher emits several public source schedules for each
window.  This postprocessor turns any verified stops from those branches into
public relation certificates and reruns the marginal target-eliminated
factor-rank scorer, so a window is classified by reusable index-calculus value
rather than by below-rho direct recovery alone.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
BRANCH_SPECS = [
    {
        "key": "strict3",
        "role": "strict_no_noise_branch",
        "pattern": re.compile(
            r"low_term_total2_source_multiclause_target67_hybrid16_charge1_lowterm16_charge1_hash4_charge1_root1_(\d+)_(\d+)_probe\.json$"
        ),
    },
    {
        "key": "old_charge2",
        "role": "red_team_comparator",
        "pattern": re.compile(
            r"low_term_total2_source_multiclause_target67_lowterm16_charge1_hash4_charge2_(\d+)_(\d+)_probe\.json$"
        ),
    },
    {
        "key": "hash4_charge2_single",
        "role": "single_clause_comparator",
        "pattern": re.compile(
            r"low_term_total2_source_row_charge_target67_hash6_topk4_charge4le2_hit2_root0_(\d+)_(\d+)_target_selector_topk_first_probe\.json$"
        ),
    },
    {
        "key": "lowterm16_charge1_single",
        "role": "single_clause_comparator",
        "pattern": re.compile(
            r"low_term_total2_source_row_charge_target67_lowterm10_topk16_charge16le1_hit1_root1_(\d+)_(\d+)_target_selector_topk_root_saved_first_probe\.json$"
        ),
    },
    {
        "key": "hybrid16_charge1_single",
        "role": "single_clause_comparator",
        "pattern": re.compile(
            r"low_term_total2_source_row_charge_target67_hybrid6_topk16_charge16le1_hit2_root0_(\d+)_(\d+)_target_selector_topk_root_saved_first_probe\.json$"
        ),
    },
]

DEFAULT_BASE_CERTIFICATES = [
    STATE_DIR
    / "low_term_total2_relation_equation_certificate_target67_hybrid16_charge1_lowterm16_charge1_hash4_charge1_root1_1744_2071_probe.json",
    STATE_DIR / "low_term_total2_relation_equation_certificate_22050_topk7_16_charge16le2_1744_1903_probe.json",
]


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


def branch_specs(enabled: set[str] | None = None) -> list[dict[str, Any]]:
    if not enabled:
        return BRANCH_SPECS
    return [spec for spec in BRANCH_SPECS if str(spec["key"]) in enabled]


def source_paths(
    start_min: int,
    end_max: int | None,
    enabled_branches: set[str] | None = None,
) -> list[tuple[int, int, dict[str, Path]]]:
    windows: dict[tuple[int, int], dict[str, Path]] = {}
    for spec in branch_specs(enabled_branches):
        pattern = spec["pattern"]
        for path in STATE_DIR.glob("low_term_total2_*target67*probe.json"):
            match = pattern.match(path.name)
            if not match:
                continue
            start = int(match.group(1))
            end = int(match.group(2))
            if start < start_min:
                continue
            if end_max is not None and end > end_max:
                continue
            windows.setdefault((start, end), {})[str(spec["key"])] = path
    return [(start, end, windows[(start, end)]) for start, end in sorted(windows)]


def certificate_path(branch_key: str, start: int, end: int) -> Path:
    return STATE_DIR / f"low_term_total2_relation_equation_certificate_target67_{branch_key}_{start}_{end}_probe.json"


def compact_summary(source_path: Path) -> dict[str, Any] | None:
    if not source_path.exists():
        return None
    data = load_json(source_path)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    selected: list[dict[str, Any]] = []
    for audit in data.get("audits") or []:
        if not isinstance(audit, dict) or not isinstance(audit.get("selected"), dict):
            continue
        item = audit["selected"]
        selected.append(
            {
                "clause": item.get("clause"),
                "direct_ops_over_rho": item.get("direct_ops_over_rho"),
                "generated_plus_shared_ops_over_rho": item.get("generated_plus_shared_ops_over_rho"),
                "rank": item.get("rank"),
                "relation_count": item.get("relation_count"),
                "secret": item.get("secret"),
                "shared_ops_over_rho": item.get("shared_ops_over_rho"),
                "target": item.get("target"),
                "top_k": item.get("top_k"),
                "transfer_index": item.get("transfer_index"),
            }
        )
    return {
        "artifact": str(source_path),
        "selected": selected,
        "summary": summary,
    }


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.setdefault("COPYFILE_DISABLE", "1")
    return subprocess.run(cmd, check=True, text=True, capture_output=True, env=env)


def certificate_passes(path: Path) -> bool:
    if not path.exists():
        return False
    data = load_json(path)
    summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
    return (
        int_value(summary.get("certificate_count")) > 0
        and int_value(summary.get("passing_certificate_count")) == int_value(summary.get("certificate_count"))
    )


def maybe_export_certificate(source_path: Path, cert_path: Path, force: bool) -> dict[str, Any]:
    if cert_path.exists() and not force:
        return {
            "certificate": str(cert_path),
            "created": False,
            "passes": certificate_passes(cert_path),
            "stdout": None,
        }
    cmd = [
        sys.executable,
        "tasks/ecdlp_index_calculus/low_term_total2_source_relation_equation_certificate.py",
        "--source-charge",
        str(source_path),
        "--out",
        str(cert_path),
    ]
    try:
        result = run_checked(cmd)
        return {
            "certificate": str(cert_path),
            "created": True,
            "passes": certificate_passes(cert_path),
            "stdout": result.stdout.strip(),
        }
    except subprocess.CalledProcessError as error:
        return {
            "certificate": str(cert_path),
            "created": False,
            "passes": False,
            "returncode": error.returncode,
            "stderr": (error.stderr or "").strip(),
            "stdout": (error.stdout or "").strip(),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-min", type=int, default=2096)
    parser.add_argument("--end-max", type=int)
    parser.add_argument(
        "--branches",
        default=",".join(str(spec["key"]) for spec in BRANCH_SPECS),
        help="Comma-separated branch keys to scan.",
    )
    parser.add_argument(
        "--base-certificates",
        default=",".join(str(path) for path in DEFAULT_BASE_CERTIFICATES),
        help="Comma-separated base certificate JSON files.",
    )
    parser.add_argument("--force-certificates", action="store_true")
    parser.add_argument(
        "--out",
        default=str(STATE_DIR / "low_term_total2_rank_frontier_postprocess_target67_multibranch_probe.json"),
    )
    parser.add_argument(
        "--scorer-out",
        default=str(STATE_DIR / "low_term_total2_factor_rank_candidate_scorer_target67_multibranch_live_probe.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    enabled_branches = {item.strip() for item in str(args.branches).split(",") if item.strip()}
    specs_by_key = {str(spec["key"]): spec for spec in BRANCH_SPECS}
    windows = source_paths(args.start_min, args.end_max, enabled_branches)
    records: list[dict[str, Any]] = []
    candidates: list[str] = []
    certificate_exports: list[dict[str, Any]] = []

    for start, end, branch_paths in windows:
        record: dict[str, Any] = {
            "branches": {},
            "start": start,
            "end": end,
        }
        for branch_key in sorted(branch_paths):
            source_path = branch_paths[branch_key]
            branch = compact_summary(source_path)
            summary = (branch or {}).get("summary") or {}
            branch_record: dict[str, Any] = {
                "role": (specs_by_key.get(branch_key) or {}).get("role"),
                "source": branch,
            }
            has_verified_stop = (
                int_value(summary.get("stopped_count")) > 0
                and int_value(summary.get("unverified_stop_count")) == 0
            )
            if has_verified_stop:
                cert_path = certificate_path(branch_key, start, end)
                export = maybe_export_certificate(source_path, cert_path, args.force_certificates)
                export["branch"] = branch_key
                branch_record["certificate_export"] = export
                certificate_exports.append(export)
                if export.get("passes"):
                    candidates.append(str(cert_path))
            record["branches"][branch_key] = branch_record
        records.append(record)

    scorer_payload: dict[str, Any] | None = None
    scorer_stdout = None
    if candidates:
        scorer_cmd = [
            sys.executable,
            "tasks/ecdlp_index_calculus/low_term_total2_factor_rank_candidate_scorer.py",
            "--base-certificates",
            args.base_certificates,
            "--candidate-certificates",
            ",".join(candidates),
            "--out",
            args.scorer_out,
        ]
        result = run_checked(scorer_cmd)
        scorer_stdout = result.stdout.strip()
        scorer_payload = load_json(Path(args.scorer_out))

    scorer_summary = (scorer_payload or {}).get("summary") or {}
    payload = {
        "artifacts": {
            "base_certificates": [item for item in args.base_certificates.split(",") if item],
            "branches": sorted(enabled_branches),
            "candidate_certificates": candidates,
            "scorer": args.scorer_out if scorer_payload else None,
        },
        "certificate_exports": certificate_exports,
        "claim_status": (
            "LIVE_RANK_GAIN_CANDIDATES_FOUND"
            if int_value(scorer_summary.get("rank_gain_candidate_count")) > 0
            else "LIVE_VERIFIED_CANDIDATES_NO_RANK_GAIN"
            if candidates
            else "NO_VERIFIED_COMPARATOR_CANDIDATES"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: branch candidates are only promoted when public relation certificates pass.",
            "HEURISTIC: marginal factor-rank gain is an index-calculus collector objective, not a deployed-curve speedup claim.",
        ],
        "records": records,
        "schema": "ecdlp.low_term_total2_rank_frontier_postprocess.v1",
        "scorer_stdout": scorer_stdout,
        "summary": {
            "candidate_certificate_count": len(candidates),
            "candidate_branch_count": len({item.get("branch") for item in certificate_exports if item.get("passes")}),
            "certificate_export_count": len(certificate_exports),
            "greedy_rank_gain_total": int_value(scorer_summary.get("greedy_rank_gain_total")),
            "greedy_selected_count": int_value(scorer_summary.get("greedy_selected_count")),
            "rank_gain_candidate_count": int_value(scorer_summary.get("rank_gain_candidate_count")),
            "scanned_window_count": len(records),
            "unique_gain_candidate_count": int_value(scorer_summary.get("unique_gain_candidate_count")),
            "verified_candidate_count": sum(1 for item in certificate_exports if item.get("passes")),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
