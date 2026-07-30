#!/usr/bin/env python3
"""Inventory order-11779 ECDLP targets disjoint from the P740 target.

This is an inventory and validation helper, not a relation generator. It scans
the local verifier records for reductions with the requested base order, checks
that the P740 excluded target is rediscovered as a positive control, and records
any non-excluded target that could support a later disjoint-target transfer run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
ENV_MAIN = TASK_DIR / "environment" / "main.py"
DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_EXCLUDED_TARGET = "22050.cf1@11731"
SCHEMA = "ecdlp.low_term_total2_p741_order11779_disjoint_target_inventory.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_verifier_module() -> Any:
    spec = importlib.util.spec_from_file_location("ecdlp_verifier_main", ENV_MAIN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import verifier helpers from {ENV_MAIN}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_json(path: Path) -> Any:
    try:
        if path.is_file():
            with path.open() as f:
                return json.load(f)
    except Exception:
        return None
    return None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def target_key(label: str, p: int) -> str:
    return f"{label}@{int(p)}"


def target_sort_key(row: dict[str, Any]) -> tuple[int, str]:
    return (int(row["p"]), str(row["label"]))


def known_success_targets(state_dir: Path) -> set[str]:
    known: set[str] = set()
    plateau = load_json(state_dir / "plateau_report.json") or {}
    success_targets = plateau.get("success_targets")
    if isinstance(success_targets, dict):
        known.update(str(key) for key in success_targets)

    leaderboard = load_json(state_dir / "leaderboard.json") or {}
    best_by_label = leaderboard.get("best_by_label")
    if isinstance(best_by_label, dict):
        for row in best_by_label.values():
            if not isinstance(row, dict):
                continue
            label = row.get("best_label")
            prime = row.get("best_p")
            if label and prime is not None:
                known.add(target_key(str(label), int(prime)))

    for row in load_jsonl(state_dir / "runs.jsonl"):
        if not row.get("correctness"):
            continue
        label = row.get("best_label")
        prime = row.get("best_p")
        if label and prime is not None:
            known.add(target_key(str(label), int(prime)))
    return known


def scan_primes(verifier: Any, min_prime: int, prime_limit: int) -> list[int]:
    return [
        p
        for p in range(max(3, int(min_prime)), int(prime_limit))
        if verifier.is_prime(p)
    ]


def load_frontier_order_targets(state_dir: Path, order: int) -> list[dict[str, Any]]:
    frontier = load_json(state_dir / "frontier_targets.json") or {}
    candidates = frontier.get("candidates")
    if not isinstance(candidates, list):
        return []
    out: list[dict[str, Any]] = []
    for row in candidates:
        if not isinstance(row, dict):
            continue
        if int(row.get("base_order") or 0) != int(order):
            continue
        out.append(
            {
                "target": row.get("target"),
                "label": row.get("label"),
                "p": row.get("p"),
                "base_order": row.get("base_order"),
                "known_success_target": bool(row.get("known_success_target")),
                "priority_score": row.get("priority_score"),
                "reasons": row.get("reasons") or [],
            }
        )
    return out


def factor_base_summary(verifier: Any, record: dict[str, Any], inv: dict[str, Any]) -> dict[str, Any]:
    seed = f"{inv['label']}:{inv['p']}:{inv['base_order']}"
    try:
        factor_base = verifier.build_factor_base(
            record["ainvs"],
            int(inv["p"]),
            int(inv["base_order"]),
            seed=seed,
        )
    except Exception as exc:  # noqa: BLE001 - stored as verifier diagnostic.
        return {
            "factor_base_error": f"{type(exc).__name__}: {exc}",
            "factor_base_seed": seed,
            "factor_base_size": 0,
        }
    return {
        "factor_base_error": None,
        "factor_base_seed": seed,
        "factor_base_size": len(factor_base),
    }


def candidate_row(
    verifier: Any,
    record: dict[str, Any],
    inv: dict[str, Any],
    order: int,
    excluded_targets: set[str],
    known_targets: set[str],
    source: str,
) -> dict[str, Any]:
    target = target_key(str(inv["label"]), int(inv["p"]))
    base_order = int(inv.get("base_order") or 0)
    factor_summary = factor_base_summary(verifier, record, inv)
    flags = sorted(str(flag) for flag in (inv.get("flags") or []))
    reasons = ["exact_requested_order"]
    if target in excluded_targets:
        reasons.append("excluded_positive_control")
    else:
        reasons.append("disjoint_from_excluded_target")
    if "prime_order_index_calculus_target" in flags:
        reasons.append("prime_order_non_anomalous")
    if bool(inv.get("precomputed_target")):
        reasons.append("precomputed_target")
    if factor_summary["factor_base_error"] is None:
        reasons.append("factor_base_constructed")

    return {
        "target": target,
        "label": inv["label"],
        "isogeny_class": inv.get("isogeny_class"),
        "p": int(inv["p"]),
        "source": source,
        "order": int(inv.get("order") or 0),
        "twist_order": int(inv.get("twist_order") or 0),
        "base": verifier.point_to_json(inv["base"]),
        "base_order": base_order,
        "base_lpf": int(inv.get("base_lpf") or 0),
        "order_lpf": int(inv.get("order_lpf") or 0),
        "twist_lpf": inv.get("twist_lpf"),
        "embedding_degree": inv.get("embedding_degree"),
        "flags": flags,
        "precomputed_target": bool(inv.get("precomputed_target")),
        "known_success_target": target in known_targets,
        "excluded_target": target in excluded_targets,
        "is_disjoint_candidate": target not in excluded_targets,
        "generic_rho_steps": math.ceil(math.sqrt(math.pi * order / 2.0)),
        "verifier_invariant_score": float(inv.get("score") or 0.0),
        "reasons": reasons,
        **factor_summary,
    }


def p740_context(state_dir: Path) -> dict[str, Any]:
    summary = load_json(state_dir / "low_term_total2_p740_disjoint_source_bank_transfer_summary.json") or {}
    transfer = summary.get("transfer_summary") if isinstance(summary, dict) else None
    target_inventory = summary.get("target_inventory") if isinstance(summary, dict) else None
    return {
        "available": bool(summary),
        "claim_status": summary.get("claim_status") if isinstance(summary, dict) else None,
        "order": summary.get("order") if isinstance(summary, dict) else None,
        "transfer_summary": transfer if isinstance(transfer, dict) else None,
        "target_inventory": target_inventory if isinstance(target_inventory, dict) else None,
    }


def scan_inventory(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    verifier = load_verifier_module()
    records = verifier.load_records()
    known_targets = known_success_targets(args.state_dir)
    excluded_targets = {str(item) for item in args.exclude_target}
    primes = scan_primes(verifier, args.min_prime, args.prime_limit)

    exact_rows_by_target: dict[str, dict[str, Any]] = {}
    scan_errors: list[dict[str, Any]] = []
    reduction_checks = 0
    precomputed_checks = 0
    scanned_prime_checks = 0
    singular_skips = 0
    seen_target_keys: set[str] = set()

    for record in records:
        for target in record.get("precomputed_targets", []):
            p = int(target["p"])
            key = target_key(record["label"], p)
            if key in seen_target_keys:
                continue
            seen_target_keys.add(key)
            precomputed_checks += 1
            reduction_checks += 1
            try:
                inv = verifier.reduction_invariants(record, p)
            except Exception as exc:  # noqa: BLE001 - target-level inventory diagnostic.
                scan_errors.append({"target": key, "source": "precomputed", "error": f"{type(exc).__name__}: {exc}"})
                continue
            if int(inv.get("base_order") or 0) != int(args.order):
                continue
            exact_rows_by_target[key] = candidate_row(
                verifier,
                record,
                inv,
                args.order,
                excluded_targets,
                known_targets,
                "precomputed",
            )

        for p in primes:
            key = target_key(record["label"], p)
            if key in seen_target_keys:
                continue
            if verifier.discriminant(record["ainvs"]) % p == 0:
                singular_skips += 1
                seen_target_keys.add(key)
                continue
            seen_target_keys.add(key)
            scanned_prime_checks += 1
            reduction_checks += 1
            try:
                inv = verifier.reduction_invariants(record, p)
            except Exception as exc:  # noqa: BLE001 - keep scanning other reductions.
                scan_errors.append({"target": key, "source": "prime_scan", "error": f"{type(exc).__name__}: {exc}"})
                continue
            if int(inv.get("base_order") or 0) != int(args.order):
                continue
            exact_rows_by_target[key] = candidate_row(
                verifier,
                record,
                inv,
                args.order,
                excluded_targets,
                known_targets,
                "prime_scan",
            )

    exact_order_targets = sorted(exact_rows_by_target.values(), key=target_sort_key)
    disjoint_candidates = [row for row in exact_order_targets if row["is_disjoint_candidate"]]
    excluded_hits = [row for row in exact_order_targets if row["excluded_target"]]
    factor_base_errors = [row for row in exact_order_targets if row["factor_base_error"]]
    disjoint_ready = [row for row in disjoint_candidates if not row["factor_base_error"]]
    recommended = disjoint_ready[0] if disjoint_ready else (disjoint_candidates[0] if disjoint_candidates else None)

    if disjoint_ready:
        claim_status = "P741_DISJOINT_ORDER11779_TARGET_FOUND"
    elif disjoint_candidates:
        claim_status = "P741_DISJOINT_ORDER11779_TARGET_FOUND_FACTOR_BASE_OPEN"
    else:
        claim_status = "NEGATIVE_RESULT_P741_NO_DISJOINT_ORDER11779_TARGET_IN_SCAN_RANGE"

    elapsed = round(time.monotonic() - started, 6)
    output = {
        "schema": SCHEMA,
        "created_at": now_iso(),
        "claim_status": claim_status,
        "claim_status_taxonomy": "OBSERVATION" if disjoint_candidates else "NEGATIVE RESULT",
        "hypothesis": (
            f"The local verifier snapshot contains at least one order-{args.order} "
            f"target outside {sorted(excluded_targets)}."
        ),
        "assumptions": [
            "TOY-EVIDENCE: local verifier records are controlled benchmark curves, not deployment targets.",
            "MODEL-BOUND: this inventory validates target availability only, not relation generation or target descent.",
            "HEURISTIC: generic rho comparison uses the standard birthday-step estimate for order-sized groups.",
        ],
        "parameters": {
            "state_dir": str(args.state_dir),
            "order": int(args.order),
            "excluded_targets": sorted(excluded_targets),
            "min_prime": int(args.min_prime),
            "prime_limit": int(args.prime_limit),
            "precomputed_targets_included": True,
            "frontier_order_targets": load_frontier_order_targets(args.state_dir, args.order),
        },
        "baselines": {
            "pollard_rho_generic_steps": math.ceil(math.sqrt(math.pi * args.order / 2.0)),
            "pollard_rho_note": "Per independent target; no faster-than-rho relation pipeline is claimed by this inventory.",
        },
        "scan_summary": {
            "record_count": len(records),
            "scan_prime_count": len(primes),
            "precomputed_reduction_checks": precomputed_checks,
            "scanned_prime_reduction_checks": scanned_prime_checks,
            "prime_reduction_checks": reduction_checks,
            "singular_reductions_skipped": singular_skips,
            "scan_error_count": len(scan_errors),
            "exact_order_target_count": len(exact_order_targets),
            "excluded_exact_order_target_count": len(excluded_hits),
            "disjoint_exact_order_target_count": len(disjoint_candidates),
            "factor_base_error_count": len(factor_base_errors),
            "elapsed_seconds": elapsed,
        },
        "positive_control": {
            "excluded_target_rediscovered": bool(excluded_hits),
            "excluded_targets_found": [row["target"] for row in excluded_hits],
        },
        "negative_control": {
            "excluded_targets_counted_as_disjoint": [
                row["target"] for row in exact_order_targets if row["target"] in excluded_targets and row["is_disjoint_candidate"]
            ],
        },
        "exact_order_targets": exact_order_targets,
        "disjoint_candidates": disjoint_candidates,
        "excluded_targets": excluded_hits,
        "recommended_target": recommended,
        "p740_context": p740_context(args.state_dir),
        "interpretation": (
            "P741 closes the target-inventory prerequisite for a disjoint order-11779 transfer run "
            "if disjoint_exact_order_target_count is positive. It does not validate relation density, "
            "factor-bank transfer, sparse linear algebra cost, or target descent on the new target."
        ),
        "falsification_route": (
            "Materialize relation certificates for the recommended target and rerun the P740 factor-bank "
            "transfer. A zero-recovery or factor-support failure would narrow the P740 signal to same-target structure."
        ),
        "next_concrete_action": (
            "Run P742 to materialize verifier-backed relation certificates for the recommended disjoint "
            "order-11779 target, then apply the P740 training bank without using same-target certificates."
            if recommended
            else "Extend the target scan range or add new controlled verifier records with order-11779 reductions."
        ),
        "scan_errors": scan_errors[:50],
    }
    return output


def summary_from_output(output: dict[str, Any]) -> dict[str, Any]:
    recommended = output.get("recommended_target") or {}
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": output["created_at"],
        "claim_status": output["claim_status"],
        "claim_status_taxonomy": output["claim_status_taxonomy"],
        "order": output["parameters"]["order"],
        "excluded_targets": output["parameters"]["excluded_targets"],
        "scan_summary": output["scan_summary"],
        "positive_control": output["positive_control"],
        "negative_control": output["negative_control"],
        "recommended_target": {
            "target": recommended.get("target"),
            "label": recommended.get("label"),
            "p": recommended.get("p"),
            "base_order": recommended.get("base_order"),
            "factor_base_size": recommended.get("factor_base_size"),
            "generic_rho_steps": recommended.get("generic_rho_steps"),
            "flags": recommended.get("flags"),
        }
        if isinstance(recommended, dict)
        else None,
        "disjoint_candidate_targets": [row["target"] for row in output["disjoint_candidates"]],
        "excluded_exact_order_targets": [row["target"] for row in output["excluded_targets"]],
        "interpretation": output["interpretation"],
        "next_concrete_action": output["next_concrete_action"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--exclude-target", action="append", default=None)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--min-prime", type=int, default=8000)
    parser.add_argument("--prime-limit", type=int, default=12000)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.state_dir = args.state_dir.expanduser().resolve()
    args.exclude_target = args.exclude_target or [DEFAULT_EXCLUDED_TARGET]
    out = args.out or (args.state_dir / "low_term_total2_p741_order11779_disjoint_target_inventory.json")
    summary_out = args.summary_out or (
        args.state_dir / "low_term_total2_p741_order11779_disjoint_target_inventory_summary.json"
    )

    output = scan_inventory(args)
    write_json(out, output)
    summary = summary_from_output(output)
    write_json(summary_out, summary)

    print(f"wrote {out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": output["claim_status"],
                "scan_summary": output["scan_summary"],
                "recommended_target": summary["recommended_target"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
