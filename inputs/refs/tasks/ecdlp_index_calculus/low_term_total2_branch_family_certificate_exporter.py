#!/usr/bin/env python3
"""Export branch-family duplicate-hit sweeps as relation certificates.

The branch-family streaming sweep records compact public relation hits for a
fixed low-term branch family.  This exporter turns verified duplicate-hit stops
into the same certificate-bank shape used by the target-eliminated factor-rank
audits:

    q * secret(Q) + sum_i a_i log(F_i) = rhs mod order.

The compact sweep rows preserve ``q_coeff``, ``rhs``, and factor-base term
indices.  In the verifier model, each listed term contributes ``-1`` to its
factor column, so the full linear form can be reconstructed without reading a
hidden scalar label.  The upstream sweep already checked public-key verification
for accepted branches; this exporter separately checks that the reconstructed
rowspace derives the same scalar.

This remains a toy-prime, model-bound index-calculus diagnostic.  It exports
relation-bank evidence for downstream rank/descent audits; it is not target
descent by itself.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_OUT = (
    "ecdlp_index_calculus_state/"
    "low_term_total2_branch_family_duplicate_hit_relation_certificates_probe.json"
)


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


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
        "sum": round(sum(values), 8),
    }


def parse_paths(raw_items: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in raw_items:
        for item in str(raw).split(","):
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


def rank_mod(matrix: list[list[int]], modulus: int) -> int:
    rows = [row[:] for row in matrix if any(value % modulus for value in row)]
    if not rows:
        return 0
    row_count = len(rows)
    col_count = len(rows[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if rows[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % modulus, -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = rows[row][col] % modulus
            if factor:
                rows[row] = [
                    (rows[row][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def rref_augmented(rows: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int], bool]:
    if not rows:
        return [], [], True
    reduced = [[value % modulus for value in row] for row in rows]
    nvars = len(reduced[0]) - 1
    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(nvars):
        pivot = None
        for row in range(pivot_row, len(reduced)):
            if reduced[row][col] % modulus:
                pivot = row
                break
        if pivot is None:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        inv = pow(reduced[pivot_row][col] % modulus, -1, modulus)
        reduced[pivot_row] = [(value * inv) % modulus for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row == pivot_row:
                continue
            factor = reduced[row][col] % modulus
            if factor:
                reduced[row] = [
                    (reduced[row][idx] - factor * reduced[pivot_row][idx]) % modulus
                    for idx in range(nvars + 1)
                ]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    for row in reduced:
        if all(row[col] % modulus == 0 for col in range(nvars)) and row[-1] % modulus:
            return reduced, pivot_cols, False
    return reduced, pivot_cols, True


def derive_secret_from_forms(forms: list[dict[str, Any]], modulus: int) -> dict[str, Any]:
    if not forms:
        return {"derived": False, "derived_secret": None, "rank": 0, "consistent": True}
    rows = [
        [int_value(value) % modulus for value in form.get("coeffs") or []]
        + [int_value(form.get("rhs")) % modulus]
        for form in forms
    ]
    reduced, pivot_cols, consistent = rref_augmented(rows, modulus)
    if not consistent or 0 not in pivot_cols:
        return {
            "consistent": consistent,
            "derived": False,
            "derived_secret": None,
            "rank": len(pivot_cols),
        }
    nvars = len(rows[0]) - 1
    free_cols = set(range(nvars)) - set(pivot_cols)
    row = pivot_cols.index(0)
    if any(reduced[row][col] % modulus for col in free_cols):
        return {
            "consistent": True,
            "derived": False,
            "derived_secret": None,
            "rank": len(pivot_cols),
        }
    return {
        "consistent": True,
        "derived": True,
        "derived_secret": reduced[row][-1] % modulus,
        "rank": len(pivot_cols),
    }


def form_from_hit(hit: dict[str, Any], order: int, factor_base_size: int) -> dict[str, Any]:
    coeffs = [0] * (1 + factor_base_size)
    coeffs[0] = int_value(hit.get("q_coeff")) % order
    terms = [int_value(term) for term in hit.get("terms") or []]
    for term in terms:
        if 0 <= term < factor_base_size:
            coeffs[1 + term] = (coeffs[1 + term] - 1) % order
    return {
        "coeffs": coeffs,
        "rhs": int_value(hit.get("rhs")) % order,
        "terms": terms,
    }


def unique_hits_for_branch(attempt: dict[str, Any], branch_key: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    seen: set[tuple[int, int, tuple[int, ...], str]] = set()
    for hit in attempt.get("hit_records") or []:
        if str(hit.get("branch_key")) != branch_key:
            continue
        if hit.get("duplicate"):
            continue
        terms = tuple(int_value(term) for term in hit.get("terms") or [])
        key = (
            int_value(hit.get("q_coeff")),
            int_value(hit.get("rhs")),
            terms,
            str(hit.get("row_key")),
        )
        if key in seen:
            continue
        seen.add(key)
        hits.append(hit)
    return hits


def factor_base_size_for_hits(hits: list[dict[str, Any]], requested: int) -> int:
    max_term = max([int_value(term) for hit in hits for term in hit.get("terms") or []] or [-1])
    return max(requested, max_term + 1)


def certificate_for_branch(
    artifact: Path,
    payload: dict[str, Any],
    group: dict[str, Any],
    attempt: dict[str, Any],
    branch_result: dict[str, Any],
    factor_base_size: int,
    min_rank: int,
    order: int,
) -> dict[str, Any] | None:
    branch_key = str(branch_result.get("branch_key"))
    hits = unique_hits_for_branch(attempt, branch_key)
    if len(hits) < max(1, min_rank):
        return None
    size = factor_base_size_for_hits(hits, factor_base_size)
    forms = [form_from_hit(hit, order, size) for hit in hits]
    derived = derive_secret_from_forms(forms, order)
    expected = int_value(branch_result.get("derived_secret"))
    rowspace_matches = bool(derived.get("derived")) and int_value(derived.get("derived_secret")) == expected
    upstream_verified = bool(branch_result.get("public_key_verified"))
    model_ops = attempt.get("model_ops") if isinstance(attempt.get("model_ops"), dict) else {}
    model_ratios = attempt.get("model_ops_over_rho") if isinstance(attempt.get("model_ops_over_rho"), dict) else {}
    window = str(group.get("window") or "")
    selected = {
        "artifact": str(artifact),
        "branch_key": branch_key,
        "clause": "branch_family_duplicate_hit",
        "direct_ops_over_rho": model_ratios.get("family_full_context_setup_integer"),
        "family_full_attempt_ops": int_value(model_ops.get("family_full_attempt_setup_integer")),
        "family_full_attempt_ops_over_rho": model_ratios.get("family_full_attempt_setup_integer"),
        "family_full_context_ops": int_value(model_ops.get("family_full_context_setup_integer")),
        "family_full_context_ops_over_rho": model_ratios.get("family_full_context_setup_integer"),
        "family_row_scan_ops": int_value(model_ops.get("family_row_scan_only_integer")),
        "family_row_scan_ops_over_rho": model_ratios.get("family_row_scan_only_integer"),
        "rho": int_value(attempt.get("rho"), int_value(group.get("rho"))),
        "row_keys": attempt.get("row_keys") or sorted({str(hit.get("row_key")) for hit in hits}),
        "secret": expected,
        "selector": str((payload.get("parameters") or {}).get("selector") or ""),
        "source_policy": attempt.get("source_policy"),
        "target": str((payload.get("parameters") or {}).get("target") or ""),
        "top_k": int_value((payload.get("parameters") or {}).get("top_k"), int_value(attempt.get("top_k"))),
        "transfer_index": int_value(attempt.get("transfer_index")),
        "window": window,
    }
    return {
        "certificate_status": (
            "BRANCH_FAMILY_PUBLIC_ROWSPACE_DERIVES_UPSTREAM_VERIFIED_SECRET"
            if upstream_verified and rowspace_matches
            else "BRANCH_FAMILY_ROWSPACE_NEEDS_REVIEW"
        ),
        "clause": "branch_family_duplicate_hit",
        "derived_secret": derived.get("derived_secret"),
        "expected_secret": expected,
        "factor_base_size": size,
        "forms": forms,
        "forms_count": len(forms),
        "hit_records": hits,
        "order": order,
        "product_factor": None,
        "public_key_verified": upstream_verified and rowspace_matches,
        "rank": int_value(derived.get("rank")),
        "rowspace_derived_secret": derived.get("derived_secret"),
        "rowspace_derives_expected_secret": rowspace_matches,
        "scan_row_count": len(attempt.get("context_rows") or []),
        "selected": selected,
        "source": str(group.get("source_path") or artifact),
        "source_case_selector": {
            "branch_key": branch_key,
            "selector": selected["selector"],
            "target": selected["target"],
            "top_k": selected["top_k"],
            "transfer_index": selected["transfer_index"],
        },
        "timing": None,
        "upstream_public_key_verified": upstream_verified,
        "window": window,
    }


def iter_branch_results(attempt: dict[str, Any]) -> list[dict[str, Any]]:
    results = [
        result
        for result in attempt.get("branch_results") or []
        if isinstance(result, dict)
    ]
    if results:
        return results
    best = attempt.get("best_branch")
    return [best] if isinstance(best, dict) else []


def collect_certificates(
    paths: list[Path],
    factor_base_size: int,
    min_rank: int,
    order: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    certificates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in paths:
        try:
            payload = load_json(path)
        except Exception as exc:
            errors.append({"artifact": str(path), "error": type(exc).__name__, "message": str(exc)})
            continue
        for group_index, group in enumerate(payload.get("groups") or []):
            if not isinstance(group, dict):
                continue
            for attempt_index, attempt in enumerate(group.get("attempts") or []):
                if not isinstance(attempt, dict):
                    continue
                emitted = False
                for branch_result in iter_branch_results(attempt):
                    if int_value(branch_result.get("rank")) < min_rank:
                        continue
                    cert = certificate_for_branch(
                        path,
                        payload,
                        group,
                        attempt,
                        branch_result,
                        factor_base_size,
                        min_rank,
                        order,
                    )
                    if cert is None:
                        continue
                    certificates.append(cert)
                    emitted = True
                if not emitted:
                    rejected.append(
                        {
                            "artifact": str(path),
                            "group_index": group_index,
                            "hit_record_count": len(attempt.get("hit_records") or []),
                            "max_branch_rank": max(
                                [int_value(result.get("rank")) for result in iter_branch_results(attempt)] or [0]
                            ),
                            "reason": "no_branch_result_meets_rank_and_unique_hit_threshold",
                            "transfer_index": int_value(attempt.get("transfer_index")),
                            "window": group.get("window"),
                        }
                    )
    return certificates, rejected, errors


def summarize(certificates: list[dict[str, Any]], rejected: list[dict[str, Any]]) -> dict[str, Any]:
    passing = [cert for cert in certificates if cert.get("public_key_verified")]
    ranks = [int_value(cert.get("rank")) for cert in certificates]
    forms = [int_value(cert.get("forms_count")) for cert in certificates]
    branch_counts = Counter(str((cert.get("selected") or {}).get("branch_key")) for cert in certificates)
    targets = sorted({str((cert.get("selected") or {}).get("target")) for cert in certificates})
    windows = sorted({str(cert.get("window")) for cert in certificates})
    cost_values = [
        float_value((cert.get("selected") or {}).get("family_full_context_ops_over_rho"))
        for cert in certificates
    ]
    return {
        "branch_counts": dict(sorted(branch_counts.items())),
        "certificate_count": len(certificates),
        "cost_over_rho_family_full_context": stat([float(value) for value in cost_values if value is not None]),
        "forms_count": stat(forms),
        "passing_certificate_count": len(passing),
        "rank": stat(ranks),
        "rejected_attempt_count": len(rejected),
        "targets": targets,
        "window_count": len(windows),
        "windows": windows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sweep-artifacts",
        nargs="+",
        required=True,
        help="Branch-family streaming sweep JSON paths or globs; comma-separated chunks are accepted.",
    )
    parser.add_argument("--factor-base-size", type=int, default=16)
    parser.add_argument("--min-rank", type=int, default=2)
    parser.add_argument(
        "--order",
        type=int,
        default=9887,
        help="Scalar-field order for the compact branch-family sweep forms.",
    )
    parser.add_argument("--out", default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = parse_paths(args.sweep_artifacts)
    certificates, rejected, errors = collect_certificates(paths, args.factor_base_size, args.min_rank, args.order)
    summary = summarize(certificates, rejected)
    payload = {
        "artifacts": {"sweep_artifacts": [str(path) for path in paths]},
        "certificates": certificates,
        "claim_status": (
            "BRANCH_FAMILY_DUPLICATE_HIT_CERTIFICATES_EXPORTED"
            if summary["passing_certificate_count"]
            else "BRANCH_FAMILY_DUPLICATE_HIT_CERTIFICATE_EXPORT_NO_PASSING_RECOVERY"
            if certificates
            else "NO_BRANCH_FAMILY_DUPLICATE_HIT_CERTIFICATES"
        ),
        "created_at": now_iso(),
        "errors": errors,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: forms are reconstructed from branch-family compact hit records using the verifier relation_linear_form convention.",
            "HEURISTIC: duplicate-hit relation supply is an index-calculus precursor signal, not a deployed-curve speedup claim.",
            "OPEN: target descent still requires reusable factor rank or a public fresh-target mapping plus full cost comparison against Pollard rho.",
        ],
        "rejected_attempts": rejected,
        "schema": "ecdlp.low_term_total2_branch_family_certificate_exporter.v1",
        "parameters": {
            "factor_base_size": args.factor_base_size,
            "min_rank": args.min_rank,
            "order": args.order,
        },
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"], "error_count": len(errors)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
