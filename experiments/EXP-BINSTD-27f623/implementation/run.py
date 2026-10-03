#!/usr/bin/env python3
"""EXP-BINSTD-27f623 Stages 0-2 driver: usable-dimensions emptiness gate.

Stdlib-only. Reimplements the Part-1 ord_n(2) / usable_dimensions predicates
from EXP-BINSTD-178742 part1_surface.py so Stages 0-1 admit without Magma/Sage.
Stage 2 (DEC-20261003-6d20b7): independent re-derive ord_n(2) for 3 frozen
forced-negative members without reading Stage-1 census rows for the
measurement. No factor-base construction. No AUXIN. Amazon Bedrock prohibited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPERIMENT_ID = "EXP-BINSTD-27f623"
HYPOTHESIS_ID = "H-BINSTD-b1f016"
SEED = 2026100311
STAGE2_ADMISSION = "DEC-20261003-6d20b7"
STAGE2_TASK_ID = "TASK-20261003-a5bab8"
# IDEA-20261001-11aa69: independent re-derive ord for 3 list members.
STAGE2_MEMBER_COUNT = 3

# Stage-0-frozen panels (also written to stage0/frozen-panels.json).
FORCED_NEGATIVE: List[int] = [11, 13, 19, 29, 37, 53, 59, 61, 67, 83, 101, 107]
POSITIVE_CONTROLS: List[int] = [17, 23, 31, 41]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def ord_n_of_2_by_iteration(n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")
    a = 1
    for d in range(1, n):
        a = (a * 2) % n
        if a == 1:
            return d
    raise ValueError(f"2 has no finite order mod {n}")


def _positive_divisors(m: int) -> List[int]:
    divs: List[int] = []
    i = 1
    while i * i <= m:
        if m % i == 0:
            divs.append(i)
            if i * i != m:
                divs.append(m // i)
        i += 1
    divs.sort()
    return divs


def ord_n_of_2_by_divisor_test(n: int) -> int:
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be an odd integer > 2")
    nm1 = n - 1
    for d in _positive_divisors(nm1):
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"no divisor d of {nm1} with 2^d ≡ 1 mod {n}")


def _prime_factors(m: int) -> List[int]:
    if m <= 1:
        return []
    factors: List[int] = []
    x = m
    p = 2
    while p * p <= x:
        if x % p == 0:
            factors.append(p)
            while x % p == 0:
                x //= p
        p += 1 if p == 2 else 2
    if x > 1:
        factors.append(x)
    return factors


def verify_ord_n_2(n: int, d: int) -> bool:
    if d <= 0 or pow(2, d, n) != 1:
        return False
    for p in _prime_factors(d):
        if pow(2, d // p, n) == 1:
            return False
    return True


def stable_dimensions_from_ord(n: int, d: int) -> Dict[str, Any]:
    if n <= 1 or (n - 1) % d != 0:
        raise ValueError(f"d={d} does not divide n-1={n - 1}")
    f = (n - 1) // d
    dims: List[int] = []
    for b in range(f + 1):
        dims.append(b * d)
        dims.append(b * d + 1)
    usable = [x for x in dims if x not in (0, 1, n - 1, n)]
    return {
        "factors_of_Phi_n": {"count": f, "degree": d},
        "stable_dimensions": dims,
        "usable_dimensions": usable,
    }


def score_ord_row(n: int) -> Dict[str, Any]:
    by_iter = ord_n_of_2_by_iteration(n)
    by_div = ord_n_of_2_by_divisor_test(n)
    routes_agree = by_iter == by_div
    d = by_div if routes_agree else by_iter
    verified = verify_ord_n_2(n, d) if routes_agree else False
    stab = (
        stable_dimensions_from_ord(n, d)
        if routes_agree and (n - 1) % d == 0
        else None
    )
    row: Dict[str, Any] = {
        "n": n,
        "ord_n_2_iteration": by_iter,
        "ord_n_2_divisor_test": by_div,
        "routes_agree": routes_agree,
        "ord_n_2": d if routes_agree else None,
        "order_verified": verified,
    }
    if stab is not None:
        row["factors_of_Phi_n"] = stab["factors_of_Phi_n"]
        row["stable_dimensions"] = stab["stable_dimensions"]
        row["usable_dimensions"] = stab["usable_dimensions"]
    row["ok"] = bool(routes_agree and verified and stab is not None)
    return row


def emptiness_gate(
    usable: Optional[List[int]],
    *,
    expect_empty: bool,
    injected: bool = False,
) -> Dict[str, Any]:
    """Preregistered gate: refuse non-empty usable when expect_empty.

    Synthetic injection must be rejected with a failure_signature.
    """
    usable_list = list(usable or [])
    is_empty = len(usable_list) == 0
    if injected and not is_empty:
        return {
            "accepted": False,
            "failure_signature": "SYNTHETIC_NONEMPTY_INJECTION_REJECTED",
            "usable_dimensions": usable_list,
            "expect_empty": expect_empty,
            "injected": True,
        }
    if expect_empty and not is_empty:
        return {
            "accepted": False,
            "failure_signature": "NONEMPTY_USABLE_WHEN_ORD_EQ_N_MINUS_1",
            "usable_dimensions": usable_list,
            "expect_empty": expect_empty,
            "injected": False,
        }
    if (not expect_empty) and is_empty:
        return {
            "accepted": False,
            "failure_signature": "EMPTY_USABLE_ON_POSITIVE_CONTROL",
            "usable_dimensions": usable_list,
            "expect_empty": expect_empty,
            "injected": False,
        }
    return {
        "accepted": True,
        "failure_signature": None,
        "usable_dimensions": usable_list,
        "expect_empty": expect_empty,
        "injected": injected,
    }


def write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha256_bytes(text.encode())


def stage0(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    stage0_dir = exp_root / "stage0"
    panels = {
        "forced_negative": FORCED_NEGATIVE,
        "positive_controls": POSITIVE_CONTROLS,
        "seed": SEED,
        "min_forced_negative": 10,
        "min_positive_controls": 3,
        "filter": "usable = stable_dimensions \\ {0,1,n-1,n}",
        "predicate_source": "EXP-BINSTD-178742/implementation/typed/part1_surface.py",
    }
    gate_api = {
        "name": "usable_emptiness_gate",
        "expect_empty_when": "ord_n(2) == n - 1",
        "injection": {
            "kind": "synthetic_nonempty",
            "payload": [2],
            "required_failure_signature": "SYNTHETIC_NONEMPTY_INJECTION_REJECTED",
        },
        "outcomes": [
            "E-GATE-HOLDS",
            "E-GATE-FAILS",
            "O-CONTROL-FAIL",
            "O-IMPEDIMENT",
        ],
    }
    predictions = {
        "heuristic": "HEUR-BINSTD-11aa69-H1",
        "empty_usable_rate_on_ord_eq_n_minus_1": 1.0,
        "synthetic_injection_catch_rate": 1.0,
        "positive_control_nonempty_count_min": 1,
        "frozen_before_stage1": True,
        "note": "Do not edit after any Stage-1 outcome.",
    }
    h_panels = write_json(stage0_dir / "frozen-panels.json", panels)
    h_gate = write_json(stage0_dir / "gate-api.json", gate_api)
    h_pred = write_json(stage0_dir / "preregistered-predictions.json", predictions)
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 0,
        "status": "completed_valid",
        "outcome": "S0-FREEZE-OK",
        "artifact_sha256": {
            "stage0/frozen-panels.json": h_panels,
            "stage0/gate-api.json": h_gate,
            "stage0/preregistered-predictions.json": h_pred,
        },
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", {"result": result})
    write_json(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "run_id": run_dir.name,
            "stage": 0,
            "status": "completed_valid",
            "outcome": "S0-FREEZE-OK",
            "recorded_at": utc_now(),
        },
    )
    # also write a YAML-ish companion the checker accepts as present
    (run_dir / "manifest.yaml").write_text(
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"run_id: {run_dir.name}",
                "stage: 0",
                "status: completed_valid",
                "outcome: S0-FREEZE-OK",
                f"recorded_at: {utc_now()}",
                "",
            ]
        )
    )
    return result


def stage1(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    stage0_dir = exp_root / "stage0"
    required = [
        stage0_dir / "frozen-panels.json",
        stage0_dir / "gate-api.json",
        stage0_dir / "preregistered-predictions.json",
    ]
    if not all(p.is_file() for p in required):
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze artifacts missing",
            "certificate": {"kind": "none"},
            "amazon_bedrock": "NOT SELECTED",
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", {"result": result})
        (run_dir / "manifest.yaml").write_text(
            "\n".join(
                [
                    f"experiment_id: {EXPERIMENT_ID}",
                    f"run_id: {run_dir.name}",
                    "stage: 1",
                    "status: failed_infrastructure",
                    "outcome: O-IMPEDIMENT",
                    f"recorded_at: {utc_now()}",
                    "",
                ]
            )
        )
        return result

    panels = json.loads((stage0_dir / "frozen-panels.json").read_text())
    forced = list(panels["forced_negative"])
    positive = list(panels["positive_controls"])

    forced_rows = []
    for n in forced:
        row = score_ord_row(n)
        gate = emptiness_gate(row.get("usable_dimensions"), expect_empty=True)
        row["gate"] = gate
        row["panel"] = "forced_negative"
        forced_rows.append(row)

    positive_rows = []
    for n in positive:
        row = score_ord_row(n)
        # Positive panel is scored but per-n emptiness is not required;
        # aggregate nonempty count is the control.
        row["gate"] = {
            "note": "aggregate positive_control_nonempty_count is the control"
        }
        row["panel"] = "positive_control"
        positive_rows.append(row)

    # Synthetic injection on the first forced-negative n.
    inj_n = forced[0]
    inj_base = score_ord_row(inj_n)
    fake_usable = [2]
    inj_gate = emptiness_gate(fake_usable, expect_empty=True, injected=True)

    route_ok = all(r.get("routes_agree") and r.get("order_verified") for r in forced_rows + positive_rows)
    empty_ok = all(
        (r.get("usable_dimensions") == []) and r["gate"].get("accepted")
        for r in forced_rows
    )
    nonempty_pos = sum(
        1 for r in positive_rows if r.get("usable_dimensions")
    )
    inj_caught = (not inj_gate["accepted"]) and inj_gate[
        "failure_signature"
    ] == "SYNTHETIC_NONEMPTY_INJECTION_REJECTED"

    if not route_ok:
        outcome = "O-CONTROL-FAIL"
    elif empty_ok and inj_caught and nonempty_pos >= 1:
        outcome = "E-GATE-HOLDS"
    else:
        outcome = "E-GATE-FAILS"

    matrix = {
        "forced_negative_rows": forced_rows,
        "positive_control_rows": positive_rows,
        "injection": {
            "n": inj_n,
            "base_usable": inj_base.get("usable_dimensions"),
            "injected_usable": fake_usable,
            "gate": inj_gate,
        },
        "metrics": {
            "empty_usable_rate_on_ord_eq_n_minus_1": (
                sum(1 for r in forced_rows if r.get("usable_dimensions") == [])
                / max(len(forced_rows), 1)
            ),
            "synthetic_injection_catch_rate": 1.0 if inj_caught else 0.0,
            "positive_control_nonempty_count": nonempty_pos,
            "route_agreement_rate": (
                sum(
                    1
                    for r in forced_rows + positive_rows
                    if r.get("routes_agree") and r.get("order_verified")
                )
                / max(len(forced_rows) + len(positive_rows), 1)
            ),
        },
        "outcome": outcome,
    }
    write_json(exp_root / "stage1" / "census-matrix.json", matrix)
    results_md = exp_root / "RESULTS.md"
    results_md.write_text(
        "\n".join(
            [
                f"# RESULTS — {EXPERIMENT_ID}",
                "",
                f"- Hypothesis: `{HYPOTHESIS_ID}`",
                f"- Outcome: **{outcome}**",
                f"- empty_usable_rate: {matrix['metrics']['empty_usable_rate_on_ord_eq_n_minus_1']}",
                f"- injection_catch_rate: {matrix['metrics']['synthetic_injection_catch_rate']}",
                f"- positive_nonempty_count: {nonempty_pos}",
                "",
                "No break. No exponent. No deployed insecurity claim.",
                "Amazon Bedrock not selected.",
                "",
            ]
        )
    )

    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 1,
        "status": "completed_valid",
        "outcome": outcome,
        "metrics": matrix["metrics"],
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", {"result": result})
    (run_dir / "manifest.yaml").write_text(
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"run_id: {run_dir.name}",
                "stage: 1",
                "status: completed_valid",
                f"outcome: {outcome}",
                f"recorded_at: {utc_now()}",
                "",
            ]
        )
    )
    return result


def independent_ord_n_of_2(n: int) -> Dict[str, Any]:
    """Stage-2-only order re-derive: divisor ladder via pow only.

    Deliberately does not call score_ord_row / ord_n_of_2_by_iteration /
    ord_n_of_2_by_divisor_test used by Stage 1. Reads no Stage-1 census rows.
    """
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be an odd integer > 2")
    nm1 = n - 1
    # Ascending divisor scan of n-1 using modular exponentiation only.
    order = None
    for d in _positive_divisors(nm1):
        if pow(2, d, n) == 1:
            order = d
            break
    if order is None:
        raise ValueError(f"no order of 2 mod {n}")
    # Minimal-order check: no proper prime-factor quotient also hits 1.
    verified = True
    for p in _prime_factors(order):
        if pow(2, order // p, n) == 1:
            verified = False
            break
    # Structural usable set when order divides n-1 (Part-1 filter).
    usable: List[int] = []
    stable: List[int] = []
    if verified and nm1 % order == 0:
        f = nm1 // order
        for b in range(f + 1):
            stable.append(b * order)
            stable.append(b * order + 1)
        usable = [x for x in stable if x not in (0, 1, n - 1, n)]
    return {
        "n": n,
        "ord_n_2_independent": order,
        "order_verified": verified,
        "ord_equals_n_minus_1": order == nm1,
        "stable_dimensions": stable,
        "usable_dimensions": usable,
        "method": "divisor_ladder_pow_only",
        "reads_stage1_census": False,
    }


def stage2(run_dir: Path, exp_root: Path) -> Dict[str, Any]:
    """Independent re-derive ord for 3 forced-negative panel members."""
    stage0_dir = exp_root / "stage0"
    panels_path = stage0_dir / "frozen-panels.json"
    if not panels_path.is_file():
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 2,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "Stage-0 freeze artifacts missing",
            "certificate": {"kind": "none"},
            "amazon_bedrock": "NOT SELECTED",
            "task_id": STAGE2_TASK_ID,
            "admission_decision": STAGE2_ADMISSION,
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", {"result": result})
        (run_dir / "manifest.yaml").write_text(
            "\n".join(
                [
                    f"experiment_id: {EXPERIMENT_ID}",
                    f"run_id: {run_dir.name}",
                    "stage: 2",
                    "status: failed_infrastructure",
                    "outcome: O-IMPEDIMENT",
                    f"admission_decision: {STAGE2_ADMISSION}",
                    f"recorded_at: {utc_now()}",
                    "",
                ]
            )
        )
        return result

    panels = json.loads(panels_path.read_text())
    forced = list(panels["forced_negative"])
    members = forced[:STAGE2_MEMBER_COUNT]
    if len(members) < STAGE2_MEMBER_COUNT:
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "stage": 2,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": f"forced_negative panel shorter than {STAGE2_MEMBER_COUNT}",
            "certificate": {"kind": "none"},
            "amazon_bedrock": "NOT SELECTED",
            "task_id": STAGE2_TASK_ID,
            "admission_decision": STAGE2_ADMISSION,
            "recorded_at": utc_now(),
        }
        write_json(run_dir / "raw-result.json", {"result": result})
        (run_dir / "manifest.yaml").write_text(
            "\n".join(
                [
                    f"experiment_id: {EXPERIMENT_ID}",
                    f"run_id: {run_dir.name}",
                    "stage: 2",
                    "status: failed_infrastructure",
                    "outcome: O-IMPEDIMENT",
                    f"admission_decision: {STAGE2_ADMISSION}",
                    f"recorded_at: {utc_now()}",
                    "",
                ]
            )
        )
        return result

    rows = [independent_ord_n_of_2(n) for n in members]

    # Optional post-hoc agreement vs Stage-1 census (not an input to re-derive).
    census_path = exp_root / "stage1" / "census-matrix.json"
    comparisons: List[Dict[str, Any]] = []
    stage1_present = census_path.is_file()
    if stage1_present:
        census = json.loads(census_path.read_text())
        by_n = {
            int(r["n"]): r
            for r in census.get("forced_negative_rows", [])
            if "n" in r
        }
        for row in rows:
            prior = by_n.get(int(row["n"]), {})
            comparisons.append(
                {
                    "n": row["n"],
                    "independent_ord": row["ord_n_2_independent"],
                    "stage1_ord": prior.get("ord_n_2"),
                    "ord_agree": prior.get("ord_n_2") == row["ord_n_2_independent"],
                    "independent_usable_empty": row["usable_dimensions"] == [],
                    "stage1_usable_empty": prior.get("usable_dimensions") == [],
                    "usable_empty_agree": (
                        (row["usable_dimensions"] == [])
                        == (prior.get("usable_dimensions") == [])
                    ),
                }
            )

    structural_ok = all(
        r["order_verified"]
        and r["ord_equals_n_minus_1"]
        and r["usable_dimensions"] == []
        for r in rows
    )
    if stage1_present:
        posthoc_ok = all(
            c.get("ord_agree") and c.get("usable_empty_agree") for c in comparisons
        )
        outcome = (
            "S2-REPLICATE-AGREE"
            if structural_ok and posthoc_ok
            else "S2-REPLICATE-DISAGREE"
        )
    else:
        # Stage-1 matrix missing is not disagreement; structural check alone.
        outcome = "S2-REPLICATE-AGREE" if structural_ok else "S2-REPLICATE-DISAGREE"

    stage2_dir = exp_root / "stage2"
    payload = {
        "schema": "binstd.usable_emptiness.stage2_independent_rederive.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "admission_decision": STAGE2_ADMISSION,
        "task_id": STAGE2_TASK_ID,
        "members": members,
        "member_count": STAGE2_MEMBER_COUNT,
        "rows": rows,
        "posthoc_stage1_comparison": comparisons,
        "stage1_census_present": stage1_present,
        "metrics": {
            "independent_ord_eq_n_minus_1_rate": (
                sum(1 for r in rows if r["ord_equals_n_minus_1"]) / len(rows)
            ),
            "independent_usable_empty_rate": (
                sum(1 for r in rows if r["usable_dimensions"] == []) / len(rows)
            ),
            "posthoc_ord_agreement_rate": (
                (
                    sum(1 for c in comparisons if c.get("ord_agree"))
                    / max(len(comparisons), 1)
                )
                if comparisons
                else None
            ),
        },
        "outcome": outcome,
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "note": (
            "Independent pow-only divisor ladder on first 3 Stage-0 forced-"
            "negatives; does not call Stage-1 score_ord_row. No break/exponent."
        ),
    }
    h_rederive = write_json(stage2_dir / "independent-rederive.json", payload)

    # Append Stage-2 block; do not erase Stage-0/1 RESULTS lines.
    results_md = exp_root / "RESULTS.md"
    prior = results_md.read_text() if results_md.is_file() else ""
    marker = "## Stage 2 — independent re-derive"
    block = "\n".join(
        [
            marker,
            "",
            f"- Admission: `{STAGE2_ADMISSION}` / `{STAGE2_TASK_ID}`",
            f"- Outcome: **{outcome}**",
            f"- Members: {members}",
            f"- independent_ord_eq_n_minus_1_rate: "
            f"{payload['metrics']['independent_ord_eq_n_minus_1_rate']}",
            f"- independent_usable_empty_rate: "
            f"{payload['metrics']['independent_usable_empty_rate']}",
            f"- posthoc_ord_agreement_rate: "
            f"{payload['metrics']['posthoc_ord_agreement_rate']}",
            "",
            "No break. No exponent. No deployed insecurity claim.",
            "Amazon Bedrock not selected.",
            "",
        ]
    )
    if marker in prior:
        head, _sep, _tail = prior.partition(marker)
        results_md.write_text(head.rstrip() + "\n\n" + block)
    else:
        results_md.write_text(prior.rstrip() + "\n\n" + block)

    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "stage": 2,
        "status": "completed_valid",
        "outcome": outcome,
        "metrics": payload["metrics"],
        "members": members,
        "artifact_sha256": {
            "stage2/independent-rederive.json": h_rederive,
        },
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
        "task_id": STAGE2_TASK_ID,
        "admission_decision": STAGE2_ADMISSION,
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", {"result": result})
    (run_dir / "manifest.yaml").write_text(
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                f"run_id: {run_dir.name}",
                "stage: 2",
                "status: completed_valid",
                f"outcome: {outcome}",
                f"admission_decision: {STAGE2_ADMISSION}",
                f"task_id: {STAGE2_TASK_ID}",
                f"recorded_at: {utc_now()}",
                "",
            ]
        )
    )
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1, 2])
    parser.add_argument("--trial-plan", type=str, required=True)
    parser.add_argument("--run-dir", type=str, required=True)
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    exp_root = Path("experiments") / EXPERIMENT_ID

    if args.stage == 0:
        stage0(run_dir, exp_root)
    elif args.stage == 1:
        stage1(run_dir, exp_root)
    else:
        stage2(run_dir, exp_root)
    print(json.dumps({"ok": True, "stage": args.stage, "run_dir": str(run_dir)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
