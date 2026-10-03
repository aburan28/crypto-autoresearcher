#!/usr/bin/env python3
"""Stage 0: period+tau arithmetic certificates vs d11575 ten-cell baseline.

Pure arithmetic — zero scientific GHS attack runs on deployed curves.
certificate.kind on the run manifest is none.
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from contextlib import redirect_stdout
from math import gcd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from period_tau import d11575_stated_period, divisors_of, n_period, tau, ten_divisors
from runpack import EXP_ROOT, dump_text, dump_yaml, utc_now, write_run_package

ROWS = [
    ("c2pnb176v1", 11),
    ("c2pnb208w1", 13),
    ("c2pnb272w1", 17),
    ("c2pnb304w1", 19),
    ("c2pnb368w1", 23),
]
D = 16
FROZEN_TAU = {
    "tau_16": 5,
    "tau_N_prime_k": 10,
    "tau_144_k9": 15,
    "tau_240_k15": 20,
    "tau_336_k21": 20,
}


def run_stage0(run_id: str) -> dict:
    cells = []
    mismatches = []
    for curve_id, k in ROWS:
        assert gcd(D, k) == 1
        N = D * k
        divs = ten_divisors(D, k)
        assert len(divs) == 10
        assert divs == divisors_of(N)
        for c in divs:
            recomputed = n_period(c, D)
            inherited = d11575_stated_period(c, D, k)
            match = recomputed == inherited
            if not match:
                mismatches.append(
                    {
                        "curve_id": curve_id,
                        "k": k,
                        "c": c,
                        "recomputed_n": recomputed,
                        "inherited_d11575_n": inherited,
                    }
                )
            family = "c_divides_d" if D % c == 0 else "c_equals_j_times_k"
            cells.append(
                {
                    "curve_id": curve_id,
                    "k": k,
                    "N": N,
                    "c": c,
                    "gcd_c_d": gcd(c, D),
                    "n_recomputed": recomputed,
                    "n_inherited_d11575": inherited,
                    "period_match": match,
                    "family": family,
                    "columns": {
                        "n_recomputed": "recomputed",
                        "n_inherited_d11575": "inherited",
                    },
                }
            )

    n_cells = len(cells)
    n_match = sum(1 for c in cells if c["period_match"])
    period_match_rate = n_match / n_cells if n_cells else 0.0

    tau_rows = []
    tau_16 = tau(16)
    tau_rows.append(
        {
            "label": "tau_16",
            "argument": 16,
            "recomputed": tau_16,
            "frozen_expected": FROZEN_TAU["tau_16"],
            "pass": tau_16 == FROZEN_TAU["tau_16"],
            "divisors": divisors_of(16),
        }
    )
    prime_k_tau_pass = True
    for curve_id, k in ROWS:
        tN = tau(D * k)
        ok = tN == FROZEN_TAU["tau_N_prime_k"]
        prime_k_tau_pass = prime_k_tau_pass and ok
        tau_rows.append(
            {
                "label": f"tau_N_prime_k_{curve_id}",
                "argument": D * k,
                "k": k,
                "recomputed": tN,
                "frozen_expected": FROZEN_TAU["tau_N_prime_k"],
                "pass": ok,
                "divisors": divisors_of(D * k),
                "multiplicative_check": {
                    "tau_d": tau(D),
                    "tau_k": tau(k),
                    "product": tau(D) * tau(k),
                    "gcd_d_k": gcd(D, k),
                    "formula": "tau(d)*tau(k) when gcd(d,k)=1",
                },
            }
        )
    for label, arg, key in [
        ("tau_144_k9", 144, "tau_144_k9"),
        ("tau_240_k15", 240, "tau_240_k15"),
        ("tau_336_k21", 336, "tau_336_k21"),
    ]:
        t = tau(arg)
        tau_rows.append(
            {
                "label": label,
                "argument": arg,
                "recomputed": t,
                "frozen_expected": FROZEN_TAU[key],
                "pass": t == FROZEN_TAU[key],
                "divisors": divisors_of(arg),
            }
        )

    tau_table_pass = all(r["pass"] for r in tau_rows)

    comparison = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 0,
        "observation_kind": "d11575_period_comparison",
        "d": D,
        "rows": [list(r) for r in ROWS],
        "cells": cells,
        "n_cells": n_cells,
        "n_match": n_match,
        "period_match_rate_d11575_cells": period_match_rate,
        "mismatches": mismatches,
        "hard_fail_any_mismatch": len(mismatches) > 0,
        "prediction_reference": "EXP-BINSTD-f124db preregistered_prediction (A)",
        "break_claim": False,
        "security_ordering_claim": False,
    }

    certificate = {
        "experiment_id": "EXP-BINSTD-f124db",
        "stage": 0,
        "observation_kind": "period_tau_certificate",
        "certificate": {
            "kind": "none",
            "note": "period/tau arithmetic recompute; not a discrete_log/decomposition/key_recovery claim",
        },
        "formula": "n(c)=d/gcd(c,d); tau(dk)=tau(d)*tau(k) when gcd(d,k)=1",
        "period_match_rate_d11575_cells": period_match_rate,
        "tau_table": tau_rows,
        "tau_table_pass": tau_table_pass,
        "frozen_tau": FROZEN_TAU,
        "literature_mmt": {
            "attempted": False,
            "literature_unrecovered": True,
            "note": (
                "Optional MMT abstract/tables retrieval not performed this run; "
                "provenance remains recalled until verified_by after an actual read."
            ),
            "provenance": "recalled",
        },
        "prediction_reference": "EXP-BINSTD-f124db preregistered_prediction (A)(B)",
        "break_claim": False,
        "security_ordering_claim": False,
    }

    method_note = """# Stage 0 methodological note — EXP-BINSTD-f124db

## Role (HOLD-H)

This packet is a **structural companion** to IDEA-20260922-d11575: it certifies
why the k-prime divisor lattice is minimal (`tau(N)=2*tau(16)=10`) and why the
conjugate-period formula generalises beyond the two special-case families.
It is **not** a competing attack lane and does **not** claim a break.

## What Stage 0 does

- Recomputes `n(c)=d/gcd(c,d)` for each of five curves × ten divisors and
  compares to d11575's inherited stated periods (`16/c` for `c|16`,
  `16/(c/k)` for `c=jk`) in a **separate inherited column**.
- Recomputes the frozen tau table: `tau(16)=5`, `tau(16k)=10` for prime `k`,
  and counterfactuals `tau(144)=15`, `tau(240)=20`, `tau(336)=20`.

## ECC2K-130 / d=1 null

At `d=1` the period formula and extra-divisor argument are **vacuous**
(ECC2K-130-shaped control). Stage 1 records that null; Stage 0 does not
run GHS on deployed curves.

## certificate.kind vocabulary

Run manifests for this experiment use `certificate.kind: none` only.
Period/tau/genus/orbit observations are **not** discrete-log solves.
Do not invent non-vocabulary kinds (e.g. `frobenius_order`) on manifests.
Stage YAML may carry `observation_kind` labels outside that field.

## Amazon Bedrock

Prohibited. Not used.
"""

    dump_yaml(EXP_ROOT / "stage0" / "d11575-period-comparison.yaml", comparison)
    dump_yaml(EXP_ROOT / "stage0" / "period-tau-certificate.yaml", certificate)
    dump_text(EXP_ROOT / "stage0" / "methodological-note.md", method_note)

    metrics = {
        "period_match_rate_d11575_cells": period_match_rate,
        "tau_table_pass": tau_table_pass,
        "n_cells": n_cells,
        "n_match": n_match,
        "literature_unrecovered": True,
        "certificate_kind_none_rate": 1.0,
        "break_claim": False,
    }
    valid = period_match_rate == 1.0 and tau_table_pass and len(mismatches) == 0
    return {
        "metrics": metrics,
        "valid": valid,
        "invalid_reason": None
        if valid
        else "Stage 0 hard-fail: period mismatch or tau table failure",
        "parameters": {"d": D, "rows": ROWS, "frozen_tau": FROZEN_TAU},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    started = utc_now()
    t0 = time.perf_counter()
    buf = io.StringIO()
    with redirect_stdout(buf):
        print(f"EXP-BINSTD-f124db Stage 0 run_id={args.run_id}")
        result = run_stage0(args.run_id)
        print(f"period_match_rate={result['metrics']['period_match_rate_d11575_cells']}")
        print(f"tau_table_pass={result['metrics']['tau_table_pass']}")
        print(f"valid={result['valid']}")
    wall = time.perf_counter() - t0
    finished = utc_now()
    write_run_package(
        args.run_id,
        stage=0,
        arm="period-tau-certificate",
        seed=None,
        command=(
            f"python3 experiments/EXP-BINSTD-f124db/implementation/stage0_run.py "
            f"--run-id {args.run_id}"
        ),
        parameters=result["parameters"],
        metrics=result["metrics"],
        valid=result["valid"],
        invalid_reason=result["invalid_reason"],
        termination_reason="completed",
        stdout_text=buf.getvalue(),
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate_note=(
            "Stage 0 period+tau arithmetic; certificate.kind=none; "
            "no discrete_log/decomposition/key_recovery claim"
        ),
    )
    print(buf.getvalue(), end="")


if __name__ == "__main__":
    main()
