#!/usr/bin/env python3
"""P957 top-k-4 relation-matrix sufficiency audit."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import low_term_total2_fixed_leaf_shared_product_gate_probe as product_gate  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p957_topk4_relation_matrix_sufficiency.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p957_topk4_relation_matrix_sufficiency_probe.json"
SCHEMA = "ecdlp.low_term_total2_p957_topk4_relation_matrix_sufficiency.v1"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_POST_MIN = 1144
DIRECT_RE = re.compile(
    r"low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_(\d+)_(\d+)_probe\.json$"
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


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def compact_form(form: tuple[tuple[int, ...], int, tuple[int, ...]]) -> dict[str, Any]:
    coeffs, rhs, terms = form
    return {"coeffs": list(coeffs), "rhs": rhs, "terms": list(terms)}


def modular_rank(rows: list[tuple[int, ...]], modulus: int) -> int:
    matrix = [[value % modulus for value in row] for row in rows if row]
    if not matrix:
        return 0
    rank = 0
    column_count = max(len(row) for row in matrix)
    for column in range(column_count):
        pivot = None
        for index in range(rank, len(matrix)):
            if column < len(matrix[index]) and matrix[index][column] % modulus:
                pivot = index
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][column] % modulus, -1, modulus)
        matrix[rank] = [(value * inv) % modulus for value in matrix[rank]]
        for index in range(len(matrix)):
            if index == rank or column >= len(matrix[index]):
                continue
            factor = matrix[index][column] % modulus
            if factor:
                matrix[index] = [
                    (value - factor * matrix[rank][pos]) % modulus
                    for pos, value in enumerate(matrix[index])
                ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def row_salt_signature(row_keys: list[str]) -> str:
    salts = []
    for key in row_keys:
        parts = str(key).split(":")
        salts.append(parts[-1] if parts else str(key))
    return "+".join(sorted(salts))


def direct_artifact_paths(state_dir: Path, post_min: int) -> list[tuple[int, int, Path]]:
    paths: list[tuple[int, int, Path]] = []
    for path in state_dir.glob("low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_*_probe.json"):
        if path.name.startswith("._"):
            continue
        match = DIRECT_RE.search(path.name)
        if not match:
            continue
        start, end = int(match.group(1)), int(match.group(2))
        if start >= post_min:
            paths.append((start, end, path))
    return sorted(paths)


def selected_topk4_cases(state_dir: Path, post_min: int, target: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for start, end, path in direct_artifact_paths(state_dir, post_min):
        payload = load_json(path)
        for case in payload.get("cases") or []:
            if str(case.get("target")) != target:
                continue
            if not case.get("public_low_prefix_gate_selected"):
                continue
            if not case.get("direct_union_public_key_verified") or not case.get("direct_below_rho"):
                continue
            if str(case.get("selector")) != "mode_low_term_span_total3":
                continue
            if int_value(case.get("top_k")) != 4:
                continue
            cases.append(
                {
                    "artifact": str(path),
                    "direct_union_derived_secret": case.get("direct_union_derived_secret"),
                    "direct_union_rank": int_value(case.get("direct_union_rank")),
                    "direct_union_relation_count": int_value(case.get("direct_union_relation_count")),
                    "direct_verifier_replay_ops": int_value(case.get("direct_verifier_replay_ops")),
                    "direct_verifier_replay_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
                    "end": end,
                    "rho": int_value(case.get("rho")),
                    "row_keys": [str(value) for value in case.get("row_keys") or []],
                    "row_salt_signature": row_salt_signature([str(value) for value in case.get("row_keys") or []]),
                    "selector": case.get("selector"),
                    "source": payload.get("source"),
                    "start": start,
                    "target": target,
                    "top_k": int_value(case.get("top_k")),
                    "transfer_index": int_value(case.get("transfer_index")),
                    "window": f"{start}_{end}",
                }
            )
    return sorted(
        cases,
        key=lambda row: (
            float_value(row.get("direct_verifier_replay_ops_over_rho"), 10**18),
            int_value(row.get("transfer_index")),
            str(row.get("artifact")),
        ),
    )


def find_source_case(source: dict[str, Any], target: str, case: dict[str, Any]) -> dict[str, Any] | None:
    candidates = product_gate.source_cases(source, {target}, {int_value(case.get("transfer_index"))})
    wanted_keys = sorted(str(value) for value in case.get("row_keys") or [])
    for candidate in candidates:
        row_keys = sorted(str(item.get("row_key")) for item in candidate.get("row_leaf_keys") or [])
        if row_keys != wanted_keys:
            continue
        if str(candidate.get("selector")) != str(case.get("selector")):
            continue
        if int_value(candidate.get("top_k")) != int_value(case.get("top_k")):
            continue
        return candidate
    return None


def replay_case(
    case: dict[str, Any],
    source_cache: dict[str, dict[str, Any]],
    spec_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]]]],
) -> dict[str, Any]:
    source_path = str(case.get("source") or "")
    if not source_path:
        return {**case, "replay_error": "missing source path"}
    if source_path not in source_cache:
        source_cache[source_path] = product_gate.load_json(Path(source_path))
    source = source_cache[source_path]
    if source_path not in spec_cache:
        spec_cache[source_path] = repair_probe.build_specs(repair_probe.source_parameters(source))
    verifier, records, config_source, specs_by_target = spec_cache[source_path]
    probe_args = repair_probe.probe_args_from_source(source)
    source_case = find_source_case(source, str(case.get("target")), case)
    if source_case is None:
        return {**case, "replay_error": "source case not found"}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    contexts = product_gate.build_case_contexts(
        source,
        source_case,
        verifier,
        records,
        config_source,
        specs_by_target,
        probe_args,
        context_cache,
    )
    direct_rows, direct_ops, rho, _profiles, union = product_gate.direct_profiles(verifier, contexts)
    forms: list[tuple[tuple[int, ...], int, tuple[int, ...]]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    row_event_counts = {}
    for direct_row in direct_rows:
        scan = direct_row["_scan"]
        row_event_counts[str(direct_row["row_key"])] = len(scan.get("relation_events") or [])
        for event in scan.get("relation_events") or []:
            coeffs, rhs, terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            forms.append((key[0], key[1], tuple(int(term) for term in terms)))
    first_built = contexts[0]["built"] if contexts else {}
    order = int_value(first_built.get("order"))
    replay = {
        **case,
        "challenge_seed": first_built.get("challenge_seed"),
        "coefficient_rank": modular_rank([form[0] for form in forms], order) if order else 0,
        "form_count": len(forms),
        "forms": [compact_form(form) for form in forms],
        "order": order,
        "p": int_value(first_built.get("p")),
        "public": list(first_built.get("public") or []),
        "replay_direct_ops": direct_ops,
        "replay_direct_ops_over_rho": ratio(direct_ops, rho) if rho else None,
        "replay_rho": rho,
        "replay_union_derived_secret": union.get("union_derived_secret"),
        "replay_union_public_key_verified": bool(union.get("union_public_key_verified")),
        "replay_union_rank": int_value(union.get("union_rank")),
        "replay_union_relation_count": int_value(union.get("union_relation_count")),
        "row_event_counts": row_event_counts,
    }
    replay["matches_stored"] = bool(
        replay["replay_union_public_key_verified"]
        and replay["replay_union_derived_secret"] == case.get("direct_union_derived_secret")
        and replay["replay_union_rank"] == int_value(case.get("direct_union_rank"))
        and replay["replay_union_relation_count"] == int_value(case.get("direct_union_relation_count"))
    )
    return replay


def compact_replay(row: dict[str, Any], include_forms: bool = False) -> dict[str, Any]:
    out = {
        "artifact": row.get("artifact"),
        "challenge_seed": row.get("challenge_seed"),
        "coefficient_rank": row.get("coefficient_rank"),
        "form_count": row.get("form_count"),
        "matches_stored": row.get("matches_stored"),
        "order": row.get("order"),
        "p": row.get("p"),
        "public": row.get("public"),
        "row_keys": row.get("row_keys"),
        "selector": row.get("selector"),
        "stored_secret": row.get("direct_union_derived_secret"),
        "top_k": row.get("top_k"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }
    if include_forms:
        out["forms"] = row.get("forms")
    return out


def summarize(replayed: list[dict[str, Any]], selected_total: int) -> dict[str, Any]:
    ok = [row for row in replayed if not row.get("replay_error")]
    matching = [row for row in ok if row.get("matches_stored")]
    forms = []
    for row in ok:
        for form in row.get("forms") or []:
            forms.append((tuple(int(value) for value in form["coeffs"]), int(form["rhs"])))
    unique_forms = sorted(set(forms))
    orders = Counter(int_value(row.get("order")) for row in ok)
    primary_order = orders.most_common(1)[0][0] if orders else 0
    public_groups: dict[tuple[int, ...], list[dict[str, Any]]] = defaultdict(list)
    transfer_groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    row_pairs = Counter()
    secrets = Counter()
    for row in ok:
        public_groups[tuple(int(value) for value in row.get("public") or [])].append(row)
        transfer_groups[int_value(row.get("transfer_index"))].append(row)
        row_pairs[tuple(sorted(str(value) for value in row.get("row_keys") or []))] += 1
        secrets[int_value(row.get("replay_union_derived_secret"), -1)] += 1
    largest_public_group = max((len(group) for group in public_groups.values()), default=0)
    largest_transfer_group = max((len(group) for group in transfer_groups.values()), default=0)
    global_rank = modular_rank([form[0] for form in unique_forms], primary_order) if primary_order else 0
    shared_public_ready = largest_public_group >= 8
    global_matrix_ready = bool(
        ok
        and len(public_groups) == 1
        and global_rank >= max(2, min(16, len(unique_forms)))
    )
    claim = (
        "P957_SINGLE_PUBLIC_RELATION_MATRIX_READY"
        if global_matrix_ready
        else "P957_FORMS_RECONSTRUCTED_GLOBAL_MATRIX_DESCENT_OPEN"
        if ok and len(unique_forms) > 0
        else "NEGATIVE_RESULT_P957_FORM_RECONSTRUCTION_FAILED"
    )
    return {
        "claim_status": claim,
        "distinct_public_count": len(public_groups),
        "distinct_secret_count": len([secret for secret in secrets if secret >= 0]),
        "distinct_transfer_count": len(transfer_groups),
        "global_coefficient_rank": global_rank,
        "global_matrix_ready": global_matrix_ready,
        "largest_same_public_group_size": largest_public_group,
        "largest_same_transfer_group_size": largest_transfer_group,
        "matching_replay_count": len(matching),
        "non_oracle_matrix_boundary": (
            "not ready: selected cases replay to explicit forms, but they are spread across distinct public challenges; target descent/global matrix glue is not proven"
            if ok and not global_matrix_ready
            else "ready under this audit's narrow single-public criterion"
            if global_matrix_ready
            else "not ready: form reconstruction failed"
        ),
        "order_counts": {str(key): value for key, value in sorted(orders.items())},
        "primary_order": primary_order,
        "replay_error_count": len([row for row in replayed if row.get("replay_error")]),
        "replayed_count": len(replayed),
        "row_pair_reuse_top": [
            {"count": count, "row_keys": list(row_keys)}
            for row_keys, count in row_pairs.most_common(8)
        ],
        "selected_topk4_below_rho_total": selected_total,
        "shared_public_matrix_candidate": shared_public_ready,
        "unique_form_count": len(unique_forms),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    all_cases = selected_topk4_cases(Path(args.state_dir), int(args.post_min), args.target)
    if int(args.max_cases) > 0:
        cases = all_cases[: int(args.max_cases)]
    else:
        cases = all_cases
    source_cache: dict[str, dict[str, Any]] = {}
    spec_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]]]] = {}
    replayed = [replay_case(case, source_cache, spec_cache) for case in cases]
    summary = summarize(replayed, len(all_cases))
    examples = [row for row in replayed if not row.get("replay_error") and row.get("matches_stored")]
    examples = sorted(
        examples,
        key=lambda row: (
            float_value(row.get("replay_direct_ops_over_rho"), 10**18),
            int_value(row.get("transfer_index")),
        ),
    )[: int(args.example_limit)]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "examples": [compact_replay(row, include_forms=True) for row in examples],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FORM-REPLAY: relation forms are reconstructed from verifier events, not inferred from stored rank summaries.",
            "MATRIX-READINESS: aggregate rank is not credited as an index-calculus matrix unless public challenges and target descent are compatible.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this tests relation-form availability and grouping, not full relation collection or deployed-curve complexity.",
        ],
        "method": "p957_topk4_relation_matrix_sufficiency",
        "parameters": {
            "max_cases": int(args.max_cases),
            "post_min": int(args.post_min),
            "target": args.target,
        },
        "replayed_cases": [compact_replay(row) for row in replayed],
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=DEFAULT_POST_MIN)
    parser.add_argument("--max-cases", type=int, default=0, help="0 means replay all selected top-k-4 below-rho cases")
    parser.add_argument("--example-limit", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"selected_total={summary['selected_topk4_below_rho_total']} "
        f"replayed={summary['replayed_count']} "
        f"matches={summary['matching_replay_count']} "
        f"errors={summary['replay_error_count']} "
        f"unique_forms={summary['unique_form_count']} "
        f"global_rank={summary['global_coefficient_rank']} "
        f"distinct_public={summary['distinct_public_count']} "
        f"matrix_ready={summary['global_matrix_ready']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
