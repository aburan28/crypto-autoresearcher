#!/usr/bin/env python3
"""Static checks for the unexecuted P-192 weighted-CM protocol.

This validates protocol arithmetic, links, IDs, and pending state.  It never
enumerates a search box, factors a candidate norm, constructs an isogeny, or
runs a benchmark.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
EXP_PATH = ROOT / "experiments/EXP-SCURVE-1a8daf/specification.yaml"
RUN_PATH = ROOT / "research/p192-weighted-cm-20261006/run-family.yaml"
DEC_PATH = ROOT / "ledger/decisions/DEC-20261006-a39750.yaml"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{path}: expected mapping")
    return data


def count_pairs(v_max: int, x_max_inclusive: int) -> int:
    # t is odd.  Half the v values accept X/2+1 even x values and half accept
    # X/2 odd x values when V and X are even.
    assert v_max % 2 == 0 and x_max_inclusive % 2 == 0
    return (v_max // 2) * (x_max_inclusive + 1)


def main() -> int:
    exp = load(EXP_PATH)["experiment"]
    family = load(RUN_PATH)
    decision = load(DEC_PATH)["coordinator_decision"]

    assert exp["id"] == "EXP-SCURVE-1a8daf"
    assert exp["scientific_status"] == "not_started"
    assert exp["result_status"] == "no_result"
    assert exp["approved_by"] == "coordinator"
    assert decision["execution_authorized"] is False
    assert decision["knowledge_promotion"]["promoted"] == []

    curve = exp["inputs"]["curve"]
    order = exp["inputs"]["cm_order"]
    p = int(curve["p"])
    a = int(curve["a"])
    n = int(curve["n"])
    t = int(curve["trace_t"])
    d = int(order["discriminant_D"])
    c = int(order["C"])
    assert a == p - 3
    assert n == p + 1 - t
    assert d == t * t - 4 * p
    assert d == -5 * 11 * 31 * c
    assert d % 4 == 1 and d % 8 == 5 and d < -4
    lower = (abs(d) + 3) // 4
    declared = int(exp["centered_norm_search"]["algebra"]
                   ["non_scalar_lower_bound"]["value"])
    assert declared == lower

    boxes = exp["centered_norm_search"]["boxes"]
    prior = 0
    for box in boxes:
        count = count_pairs(int(box["v_max"]), int(box["x_max"]))
        assert count == int(box["raw_pair_count"])
        shell = int(box.get("shell_raw_pair_count", count))
        assert shell == count - prior
        prior = count

    runs = family["runs"]
    assert family["family_status"] == "pending_not_executed"
    assert family["scientific_results"] == []
    assert len(runs) == exp["planned_run_family"]["run_count"] == 8
    labels = [run["planned_run_label"] for run in runs]
    assert len(labels) == len(set(labels))
    assert all(run["status"] == "pending_not_executed" for run in runs)
    seen: set[str] = set()
    for expected_ordinal, run in enumerate(runs, 1):
        assert run["ordinal"] == expected_ordinal
        predecessor = run["predecessor"]
        if predecessor is not None:
            assert predecessor["planned_run_label"] in seen
        seen.add(run["planned_run_label"])

    assert family["native_source_pr"] == "https://github.com/aburan28/crypto/pull/1507"
    assert family["archive_reference_pr"] == "https://github.com/aburan28/crypto-autoresearcher/pull/1942"
    assert exp["budget"]["maximum_runs"] == 8
    assert exp["factor_bases_and_smoothness"]["algebraic_sieve_base"]["bound_inclusive"] == 65521
    assert exp["factor_bases_and_smoothness"]["mappable_base"]["bound_inclusive"] == 4093
    assert exp["factor_bases_and_smoothness"]["large_prime_rules"]["bound_inclusive"] == 2147483647

    for relative in (
        "ledger/questions/RQ-SCURVE-42f1a3.yaml",
        "ledger/proposals/IDEA-20261006-767793.yaml",
        "ledger/hypotheses/H-SCURVE-ec34c4.yaml",
        "ledger/decisions/DEC-20261006-a39750.yaml",
        "experiments/EXP-SCURVE-1a8daf/specification.yaml",
        "research/p192-weighted-cm-20261006/run-family.yaml",
        "research/p192-weighted-cm-20261006/REPORT.md",
        "research/p192-weighted-cm-20261006/protocol-flow.dot",
        "research/p192-weighted-cm-20261006/protocol-flow.svg",
        "research/p192-weighted-cm-20261006/REPORT.pdf",
    ):
        assert (ROOT / relative).is_file(), relative

    print("PASS: protocol arithmetic, IDs, links, and all-pending state")
    print("PASS: no scientific result is recorded")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
