#!/usr/bin/env python3
"""Summarize singleton bridge selector rules from nullspace scout artifacts."""

from __future__ import annotations

import argparse
import csv
import glob
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


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


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
    }


def support_for_form(form: dict[str, Any]) -> tuple[int, ...]:
    coeffs = form.get("coeffs") or []
    return tuple(index for index, coeff in enumerate(coeffs[1:]) if int_value(coeff) != 0)


def support_key(support: tuple[int, ...]) -> str:
    return ",".join(str(item) for item in support)


def support_signature(cert: dict[str, Any]) -> tuple[str, ...]:
    return tuple(support_key(support_for_form(form)) for form in cert.get("forms") or [])


def has_forbidden_support(cert: dict[str, Any], forbidden: set[tuple[int, ...]]) -> bool:
    return any(support_for_form(form) in forbidden for form in cert.get("forms") or [])


def parse_supports(raw: str) -> set[tuple[int, ...]]:
    supports: set[tuple[int, ...]] = set()
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        supports.add(tuple(int(part.strip()) for part in chunk.split(",") if part.strip()))
    return supports


def load_singleton_rows(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            artifact = row.get("artifact") or ""
            if not artifact:
                continue
            rows[artifact] = {
                **row,
                "bank_def11779": int_value(row.get("bank_def11779")),
                "bank_rank11779": int_value(row.get("bank_rank11779")),
                "bank_unique11779": int_value(row.get("bank_unique11779")),
                "best_direct": float_value(row.get("best_direct")),
                "candidate_count": int_value(row.get("candidate_count")),
                "family_false": int_value(row.get("family_false")),
                "family_rank11779": int_value(row.get("family_rank11779")),
                "family_verified": int_value(row.get("family_verified")),
                "window": row.get("window"),
            }
    return rows


def is_singleton_pass(row: dict[str, Any]) -> bool:
    return (
        int_value(row.get("bank_rank11779")) == 16
        and int_value(row.get("bank_def11779")) == 0
        and int_value(row.get("family_verified")) == 11
        and int_value(row.get("family_false")) == 0
        and int_value(row.get("family_rank11779")) == 16
    )


def window_from_path(path: Path) -> str:
    name = path.name
    marker = "strictbridge11779_"
    if marker not in name:
        return ""
    tail = name.split(marker, 1)[1]
    return tail.split("_allmodes", 1)[0]


def compact_cert(path: Path, cert: dict[str, Any], singleton_row: dict[str, Any] | None) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    direct = float_value(selected.get("direct_ops_over_rho") or cert.get("direct_ops_over_rho"))
    return {
        "artifact": str(path),
        "direct_ops_over_rho": direct,
        "forms_count": int_value(cert.get("forms_count")),
        "selector": selected.get("selector"),
        "singleton_repair_pass": bool(singleton_row and is_singleton_pass(singleton_row)),
        "support_signature": list(support_signature(cert)),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": window_from_path(path),
    }


def summarize_group(items: list[dict[str, Any]]) -> dict[str, Any]:
    artifacts = {item["artifact"] for item in items}
    pass_artifacts = {
        item["artifact"] for item in items if item.get("singleton_repair_pass")
    }
    direct_values = [
        value
        for value in (float_value(item.get("direct_ops_over_rho")) for item in items)
        if value is not None
    ]
    support_counter: Counter[str] = Counter()
    for item in items:
        support_counter.update(item.get("support_signature") or [])
    best = min(
        items,
        key=lambda item: (
            float_value(item.get("direct_ops_over_rho")) is None,
            float_value(item.get("direct_ops_over_rho")) or 10**9,
            item.get("artifact") or "",
        ),
    )
    return {
        "artifact_count": len(artifacts),
        "best_certificate": best,
        "candidate_certificate_count": len(items),
        "direct_ops_over_rho": stat(direct_values),
        "singleton_repair_pass_artifact_count": len(pass_artifacts),
        "support_counts": dict(sorted(support_counter.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scout-glob", required=True)
    parser.add_argument("--singleton-summary", type=Path, required=True)
    parser.add_argument("--forbidden-supports", default="3,6")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(path) for path in sorted(glob.glob(args.scout_glob))]
    forbidden = parse_supports(args.forbidden_supports)
    singleton_rows = load_singleton_rows(args.singleton_summary)
    clean_certs: list[dict[str, Any]] = []
    mixed_forbidden_certs: list[dict[str, Any]] = []
    mixed_nonforbidden_certs: list[dict[str, Any]] = []
    artifact_status = Counter()
    for path in paths:
        payload = load_json(path)
        certs = [
            cert
            for cert in payload.get("certificates") or []
            if isinstance(cert, dict) and factor_bank.certificate_is_usable(cert)
        ]
        if not certs:
            artifact_status["no_candidate_certificate"] += 1
            continue
        singleton_row = singleton_rows.get(str(path))
        items: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for cert in certs:
            item = compact_cert(path, cert, singleton_row)
            items.append((cert, item))
        all_clean = not any(has_forbidden_support(cert, forbidden) for cert, _item in items)
        if all_clean:
            clean_certs.extend(item for _cert, item in items)
        else:
            for cert, item in items:
                if has_forbidden_support(cert, forbidden):
                    mixed_forbidden_certs.append(item)
                else:
                    mixed_nonforbidden_certs.append(item)
        artifact_status["clean_artifact" if all_clean else "mixed_forbidden_support_artifact"] += 1

    by_selector: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_support_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_selector_support: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in clean_certs:
        selector = str(item.get("selector") or "unknown")
        signature = ";".join(item.get("support_signature") or [])
        by_selector[selector].append(item)
        by_support_signature[signature].append(item)
        by_selector_support[f"{selector}|{signature}"].append(item)

    rules = {
        "by_selector": {
            key: summarize_group(values)
            for key, values in sorted(by_selector.items())
        },
        "by_selector_support_signature": {
            key: summarize_group(values)
            for key, values in sorted(by_selector_support.items())
        },
        "by_support_signature": {
            key: summarize_group(values)
            for key, values in sorted(by_support_signature.items())
        },
    }
    single_candidate_passes = [
        row
        for row in singleton_rows.values()
        if int_value(row.get("candidate_count")) == 1 and is_singleton_pass(row)
    ]
    best_singletons = sorted(
        [row for row in singleton_rows.values() if is_singleton_pass(row)],
        key=lambda row: (
            float_value(row.get("best_direct")) is None,
            float_value(row.get("best_direct")) or 10**9,
            row.get("artifact") or "",
        ),
    )[:12]
    payload = {
        "artifact_status_counts": dict(sorted(artifact_status.items())),
        "best_singleton_repair_artifacts": best_singletons,
        "clean_candidate_certificate_count": len(clean_certs),
        "created_at": now_iso(),
        "forbidden_supports": [list(support) for support in sorted(forbidden)],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rules are mined from the current low-term total-2 factor namespace.",
            "HEURISTIC: selector/support summaries are candidate public rules, not asymptotic claims.",
            "NO SPEEDUP CLAIM: direct below-rho bridge certificates are not an end-to-end ECDLP algorithm.",
        ],
        "mixed_candidate_certificate_count": len(mixed_forbidden_certs) + len(mixed_nonforbidden_certs),
        "mixed_forbidden_candidate_certificate_count": len(mixed_forbidden_certs),
        "mixed_nonforbidden_candidate_certificate_count": len(mixed_nonforbidden_certs),
        "rule_scope": [
            "Selector/support rules are computed only from whole-artifact-clean certificates.",
            "Non-forbidden certificates inside mixed artifacts are counted separately and excluded from rules.",
        ],
        "rules": rules,
        "schema": "ecdlp.low_term_total2_bridge_rule_minimizer.v2",
        "singleton_summary": {
            "passing_artifact_count": sum(1 for row in singleton_rows.values() if is_singleton_pass(row)),
            "single_candidate_passing_artifact_count": len(single_candidate_passes),
            "tested_artifact_count": len(singleton_rows),
        },
        "source_artifacts": {
            "scout_glob": args.scout_glob,
            "singleton_summary": str(args.singleton_summary),
        },
        "summary": {
            "best_direct_ops_over_rho": (
                float_value(best_singletons[0].get("best_direct")) if best_singletons else None
            ),
            "clean_artifact_count": artifact_status.get("clean_artifact", 0),
            "clean_candidate_certificate_count": len(clean_certs),
            "dominant_selector": max(
                rules["by_selector"].items(),
                key=lambda item: item[1]["candidate_certificate_count"],
            )[0] if rules["by_selector"] else None,
            "mixed_forbidden_support_artifact_count": artifact_status.get(
                "mixed_forbidden_support_artifact", 0
            ),
            "mixed_nonforbidden_candidate_certificate_count": len(mixed_nonforbidden_certs),
            "single_candidate_passing_artifact_count": len(single_candidate_passes),
            "singleton_passing_artifact_count": sum(
                1 for row in singleton_rows.values() if is_singleton_pass(row)
            ),
            "singleton_tested_artifact_count": len(singleton_rows),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
