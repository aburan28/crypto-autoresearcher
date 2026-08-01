#!/usr/bin/env python3
"""Audit whether source-family known-factor hits compose into direct certificates.

The known-column source-family expansion can verify a public motif through
known-factor substitution.  The later direct-certificate and factor-rank
pipeline is stricter: it only consumes direct public source rows.  This scout
keeps that boundary visible by comparing source-family hits against the direct
certificate/rank artifacts for the same validation window.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WINDOW_RE = re.compile(r"_(\d+)_(\d+)_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def window_from_path(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def row_window(row: dict[str, Any]) -> str:
    return str(row.get("window") or "")


def row_case(row: dict[str, Any]) -> dict[str, Any]:
    hit_case = row.get("hit_case")
    if isinstance(hit_case, dict):
        return hit_case
    structural_case = row.get("structural_case")
    if isinstance(structural_case, dict):
        return structural_case
    scanned_rows = row.get("scanned_rows")
    if isinstance(scanned_rows, list) and scanned_rows and isinstance(scanned_rows[0], dict):
        return scanned_rows[0]
    return {}


def case_public(case: dict[str, Any]) -> dict[str, Any]:
    public = case.get("public")
    return public if isinstance(public, dict) else {}


def case_metrics(case: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("case")
    return metrics if isinstance(metrics, dict) else {}


def canonical_rows(row_keys: Any) -> list[str]:
    if not isinstance(row_keys, list):
        return []
    return sorted(str(row) for row in row_keys)


def public_signature(public: dict[str, Any]) -> dict[str, Any]:
    features = public.get("features") if isinstance(public.get("features"), dict) else {}
    return {
        "row_keys": canonical_rows(public.get("row_keys")),
        "selected_support": features.get("selected_support") or [],
        "selector": public.get("selector"),
        "top_k": int_value(public.get("top_k")),
        "transfer_index": int_value(public.get("transfer_index")),
    }


def cert_selected(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected")
    return selected if isinstance(selected, dict) else {}


def cert_matches_public(cert: dict[str, Any], public: dict[str, Any]) -> bool:
    selected = cert_selected(cert)
    transfer_index = int_value(public.get("transfer_index"))
    selector = public.get("selector")
    top_k = int_value(public.get("top_k"))
    if int_value(selected.get("transfer_index")) != transfer_index:
        return False
    if selector and selected.get("selector") != selector:
        return False
    if top_k and int_value(selected.get("top_k")) != top_k:
        return False
    public_rows = canonical_rows(public.get("row_keys"))
    selected_rows = canonical_rows(selected.get("row_keys"))
    return not public_rows or not selected_rows or public_rows == selected_rows


def score_matches_public(score: dict[str, Any], public: dict[str, Any]) -> bool:
    candidate = score.get("candidate")
    if not isinstance(candidate, dict):
        return False
    transfer_index = int_value(public.get("transfer_index"))
    selector = public.get("selector")
    top_k = int_value(public.get("top_k"))
    if int_value(candidate.get("transfer_index")) != transfer_index:
        return False
    if selector and candidate.get("selector") != selector:
        return False
    if top_k and int_value(candidate.get("top_k")) != top_k:
        return False
    return True


def compact_certificate(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert_selected(cert)
    return {
        "certificate_status": cert.get("certificate_status"),
        "forms_count": int_value(cert.get("forms_count")),
        "public_key_verified": bool(cert.get("public_key_verified")),
        "rank": int_value(cert.get("rank")),
        "selected": {
            "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
            "row_keys": canonical_rows(selected.get("row_keys")),
            "selector": selected.get("selector"),
            "top_k": int_value(selected.get("top_k")),
            "transfer_index": int_value(selected.get("transfer_index")),
        },
        "window": cert.get("window"),
    }


def compact_score(score: dict[str, Any]) -> dict[str, Any]:
    candidate = score.get("candidate")
    if not isinstance(candidate, dict):
        candidate = {}
    return {
        "claim_status": score.get("claim_status"),
        "candidate": {
            "artifact": candidate.get("artifact"),
            "direct_ops_over_rho": candidate.get("direct_ops_over_rho"),
            "selector": candidate.get("selector"),
            "top_k": int_value(candidate.get("top_k")),
            "transfer_index": int_value(candidate.get("transfer_index")),
        },
        "rank_gain": int_value(score.get("rank_gain")),
        "unique_factor_relation_gain": int_value(score.get("unique_factor_relation_gain")),
    }


def load_artifact_map(
    paths: list[Path],
    include_cumulative: bool,
    wanted_windows: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for path in paths:
        if not include_cumulative and "_cumulative_" in path.name:
            continue
        window = window_from_path(path)
        if not window:
            continue
        if wanted_windows is not None and window not in wanted_windows:
            continue
        mapped[window] = {"path": path, "payload": load_json(path)}
    return mapped


def direct_audit(window: str, public: dict[str, Any], direct_by_window: dict[str, dict[str, Any]]) -> dict[str, Any]:
    artifact = direct_by_window.get(window)
    if not artifact:
        return {
            "artifact": None,
            "certificate_count": 0,
            "exists": False,
            "matching_certificate_count": 0,
            "passing_certificate_count": 0,
            "matching_certificates": [],
        }
    payload = artifact["payload"]
    certificates = [cert for cert in payload.get("certificates") or [] if isinstance(cert, dict)]
    matching = [cert for cert in certificates if cert_matches_public(cert, public)]
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        "artifact": str(artifact["path"]),
        "certificate_count": len(certificates),
        "exists": True,
        "matching_certificate_count": len(matching),
        "passing_certificate_count": int_value(summary.get("passing_certificate_count")),
        "matching_certificates": [compact_certificate(cert) for cert in matching[:5]],
    }


def rank_audit(window: str, public: dict[str, Any], rank_by_window: dict[str, dict[str, Any]]) -> dict[str, Any]:
    artifact = rank_by_window.get(window)
    if not artifact:
        return {
            "artifact": None,
            "exists": False,
            "matching_score_count": 0,
            "matching_scores": [],
            "summary": {},
        }
    payload = artifact["payload"]
    scores = [score for score in payload.get("scores") or [] if isinstance(score, dict)]
    matching = [score for score in scores if score_matches_public(score, public)]
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        "artifact": str(artifact["path"]),
        "exists": True,
        "matching_score_count": len(matching),
        "matching_scores": [compact_score(score) for score in matching[:5]],
        "summary": summary,
    }


def bridge_status(hit: bool, direct: dict[str, Any], rank: dict[str, Any]) -> str:
    has_direct_match = int_value(direct.get("matching_certificate_count")) > 0
    has_rank_match = int_value(rank.get("matching_score_count")) > 0
    if hit and has_direct_match and has_rank_match:
        return "SOURCE_FAMILY_HIT_HAS_DIRECT_CERTIFICATE_AND_RANK_SCORE"
    if hit and has_direct_match:
        return "SOURCE_FAMILY_HIT_HAS_DIRECT_CERTIFICATE_NO_MATCHING_RANK_SCORE"
    if hit and direct.get("exists"):
        return "KNOWN_FACTOR_HIT_WITH_DIRECT_WINDOW_NO_MATCHING_CERTIFICATE"
    if hit:
        return "KNOWN_FACTOR_HIT_WITHOUT_DIRECT_CERTIFICATE"
    if direct.get("exists"):
        return "NO_SOURCE_FAMILY_HIT_BUT_DIRECT_CERTIFICATE_WINDOW_EXISTS"
    return "NO_SOURCE_FAMILY_HIT_NO_DIRECT_CERTIFICATE"


def load_source_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            rows.append({"artifact": path, "row": row})
    rows.sort(key=lambda item: (row_window(item["row"]), str(item["artifact"])))
    return rows


def audit_rows(
    source_rows: list[dict[str, Any]],
    direct_by_window: dict[str, dict[str, Any]],
    rank_by_window: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    audited: list[dict[str, Any]] = []
    for item in source_rows:
        row = item["row"]
        case = row_case(row)
        public = case_public(case)
        metrics = case_metrics(case)
        window = row_window(row)
        direct = direct_audit(window, public, direct_by_window)
        rank = rank_audit(window, public, rank_by_window)
        hit = bool(row.get("hit"))
        audited.append(
            {
                "artifact": str(item["artifact"]),
                "bridge_status": bridge_status(hit, direct, rank),
                "case_metrics": {
                    "direct_ops_over_rho": metrics.get("direct_ops_over_rho"),
                    "known_structural_motifs": metrics.get("known_structural_motifs") or [],
                    "public_known_factor_verified": bool(metrics.get("public_known_factor_verified")),
                    "recoverable_form_count": int_value(metrics.get("recoverable_form_count")),
                    "verified_motifs": metrics.get("verified_motifs") or [],
                },
                "cost_over_rho": float_value(row.get("cost_over_rho")),
                "direct_certificate": direct,
                "hit": hit,
                "rank_scorer": rank,
                "scanned_candidate_count": int_value(row.get("scanned_candidate_count")),
                "selected_structural": bool(row.get("selected_structural")),
                "source_public": public_signature(public),
                "support_report_count": int_value(row.get("support_report_count")),
                "window": window,
            }
        )
    return audited


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_family_hit_count = sum(1 for row in rows if row["hit"])
    direct_matching_hit_count = sum(
        1 for row in rows if row["hit"] and int_value(row["direct_certificate"].get("matching_certificate_count")) > 0
    )
    rank_matching_hit_count = sum(
        1 for row in rows if row["hit"] and int_value(row["rank_scorer"].get("matching_score_count")) > 0
    )
    known_factor_hit_count = sum(
        1 for row in rows if row["hit"] and row["case_metrics"].get("public_known_factor_verified")
    )
    known_factor_hit_without_direct_certificate_count = sum(
        1
        for row in rows
        if row["bridge_status"]
        in {
            "KNOWN_FACTOR_HIT_WITHOUT_DIRECT_CERTIFICATE",
            "KNOWN_FACTOR_HIT_WITH_DIRECT_WINDOW_NO_MATCHING_CERTIFICATE",
        }
    )
    direct_window_no_source_hit_count = sum(
        1 for row in rows if row["bridge_status"] == "NO_SOURCE_FAMILY_HIT_BUT_DIRECT_CERTIFICATE_WINDOW_EXISTS"
    )
    return {
        "direct_matching_hit_count": direct_matching_hit_count,
        "direct_window_count": sum(1 for row in rows if row["direct_certificate"].get("exists")),
        "direct_window_no_source_hit_count": direct_window_no_source_hit_count,
        "known_factor_hit_count": known_factor_hit_count,
        "known_factor_hit_without_direct_certificate_count": known_factor_hit_without_direct_certificate_count,
        "rank_matching_hit_count": rank_matching_hit_count,
        "rank_window_count": sum(1 for row in rows if row["rank_scorer"].get("exists")),
        "source_family_hit_count": source_family_hit_count,
        "source_family_row_count": len(rows),
        "source_family_hit_without_direct_match_count": source_family_hit_count - direct_matching_hit_count,
        "status_counts": {
            status: sum(1 for row in rows if row["bridge_status"] == status)
            for status in sorted({row["bridge_status"] for row in rows})
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-family-artifacts", required=True, help="Comma-separated JSON paths or globs.")
    parser.add_argument(
        "--direct-cert-glob",
        default=(
            "ecdlp_index_calculus_state/"
            "low_term_total2_direct_relation_equation_certificate_22050_col15_lowterm_support5_*_probe.json"
        ),
        help="Direct certificate artifact glob.",
    )
    parser.add_argument(
        "--rank-scorer-glob",
        default=(
            "ecdlp_index_calculus_state/"
            "low_term_total2_factor_rank_candidate_scorer_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json"
        ),
        help="Factor-rank scorer artifact glob.",
    )
    parser.add_argument(
        "--include-cumulative",
        action="store_true",
        help="Include cumulative rank/certificate artifacts if the globs match them.",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_paths = parse_paths(args.source_family_artifacts)
    direct_paths = parse_paths(args.direct_cert_glob)
    rank_paths = parse_paths(args.rank_scorer_glob)
    source_rows = load_source_rows(source_paths)
    wanted_windows = {row_window(item["row"]) for item in source_rows}
    direct_by_window = load_artifact_map(direct_paths, args.include_cumulative, wanted_windows)
    rank_by_window = load_artifact_map(rank_paths, args.include_cumulative, wanted_windows)
    rows = audit_rows(source_rows, direct_by_window, rank_by_window)
    summary = summarize(rows)
    payload = {
        "artifacts": {
            "direct_certificates": [str(path) for path in direct_paths],
            "rank_scorers": [str(path) for path in rank_paths],
            "source_family": [str(path) for path in source_paths],
        },
        "claim_status": (
            "SOURCE_FAMILY_BRIDGE_GAPS_FOUND"
            if summary["known_factor_hit_without_direct_certificate_count"]
            else "SOURCE_FAMILY_HITS_COMPOSE_TO_DIRECT_CERTIFICATES"
            if summary["source_family_hit_count"]
            else "NO_SOURCE_FAMILY_HITS_IN_AUDIT"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: compares source-family known-factor replay to the current direct-source certificate/rank pipeline.",
            "NEGATIVE RESULT: a bridge gap rules out automatic composition for these artifacts, not the broader index-calculus hypothesis.",
        ],
        "rows": rows,
        "schema": "ecdlp.low_term_total2_known_column_source_family_bridge_gap_scout.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
