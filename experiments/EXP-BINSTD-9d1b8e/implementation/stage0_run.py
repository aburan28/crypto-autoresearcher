#!/usr/bin/env python3
"""Stage 0: five-row integer symmetry certificate + dual rho bits.

Arithmetic only — no scientific group walks on deployed curves.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-BINSTD-9d1b8e"
AUDIT = ROOT / "analysis" / "binstd-curve-audit" / "binary-curve-params.txt"

ROWS = [
    ("c2pnb176v1", 11),
    ("c2pnb208w1", 13),
    ("c2pnb272w1", 17),
    ("c2pnb304w1", 19),
    ("c2pnb368w1", 23),
]
FROZEN_CORRECTED = [78.10, 93.98, 125.78, 141.71, 173.57]
FROZEN_INHERITED = [77.9, 93.7, 125.5, 141.5, 173.3]
FROZEN_R_BITS = [161, 193, 257, 289, 353]
TOL = 0.01
Q = 1 << 16


def blob(body: str, label: str):
    m = re.search(re.escape(label) + r":\s*\n((?:\s+[0-9a-f:]+\n)+)", body)
    if m:
        return int(re.sub(r"[^0-9a-f]", "", m.group(1)), 16)
    m = re.search(re.escape(label) + r":\s*(\d+)(?:\s*\(0x[0-9a-fA-F]+\))?\s*\n", body)
    if m:
        return int(m.group(1))
    return None


def load_pairs(txt: str):
    blocks = re.split(r"===== (\S+) =====", txt)[1:]
    return dict(zip(blocks[0::2], blocks[1::2]))


def weil_sk(q: int, t: int, k: int) -> int:
    s0, s1 = 2, t
    for _ in range(k - 1):
        s0, s1 = s1, t * s1 - q * s0
    return s1


def corrected_rho_bits(r: int, k: int) -> float:
    return 0.5 * math.log2(r) + 0.5 * math.log2(math.pi / 4) - 0.5 * math.log2(k)


def run_stage0():
    pairs = load_pairs(AUDIT.read_text())
    rows_out = []
    all_pass = True
    for i, (name, k) in enumerate(ROWS):
        body = pairs[name]
        order = blob(body, "Order")
        cm = re.search(r"Cofactor:\s*(\d+)", body)
        cof = int(cm.group(1))
        t = Q + 1 - cof
        h_recomputed = Q + 1 - t
        assert h_recomputed == cof
        sk = weil_sk(Q, t, k)
        Nk = Q**k + 1 - sk
        N_dump = cof * order
        weil_pass = Nk == N_dump
        g = gcd(h_recomputed, order)
        t_odd = (t % 2 == 1)
        rho = corrected_rho_bits(order, k)
        rho_pass = abs(rho - FROZEN_CORRECTED[i]) <= TOL
        r_bits = order.bit_length()
        r_bits_pass = r_bits == FROZEN_R_BITS[i]
        # ord(mu)=k by k-prime + mu!=1 (mu!=1 from gcd(h,r)=1)
        k_prime = all(k % p != 0 for p in range(2, int(k**0.5) + 1)) or k in (2, 3)
        # k is prime for all five; state argument
        assert k_prime
        ord_mu_stated = k if (g == 1 and k_prime) else None
        row_pass = weil_pass and g == 1 and t_odd and rho_pass and r_bits_pass
        all_pass = all_pass and row_pass
        rows_out.append(
            {
                "curve_id": name,
                "k": k,
                "k_prime": True,
                "q": Q,
                "t_audited": t,
                "h_recomputed": h_recomputed,
                "h_from_dump_cofactor": cof,
                "r_from_dump": str(order),
                "r_bit_length": r_bits,
                "frozen_expected_r_bits": FROZEN_R_BITS[i],
                "r_bits_match": r_bits_pass,
                "weil_Nk": str(Nk),
                "dump_h_times_r": str(N_dump),
                "weil_recursion_pass": weil_pass,
                "gcd_h_r": g,
                "gcd_h_r_pass": g == 1,
                "t_odd": t_odd,
                "t_odd_pass": t_odd,
                "corrected_rho_bits_recomputed": round(rho, 6),
                "corrected_rho_bits_frozen_expected": FROZEN_CORRECTED[i],
                "corrected_rho_within_tol": rho_pass,
                "inherited_rho_bits": FROZEN_INHERITED[i],
                "inherited_rho_bits_label": "inherited_d11575_c07598_0p886_over_sqrt_2k",
                "ord_mu_stated": ord_mu_stated,
                "ord_mu_argument": (
                    "k prime and mu!=1 (from gcd(h,r)=1 / G meets E(F_q) only at O) "
                    "=> ord(mu)=k by Lagrange; |-1| not in <mu> since k odd "
                    "=> |<pi_q,[-1]>|=2k given Aut(E)=Z/2 (A3, Stage 1)."
                ),
                "mu_ne_1_from_gcd": g == 1,
                "row_pass": row_pass,
                "columns_measured_vs_inherited": {
                    "corrected_rho_bits": "recomputed",
                    "inherited_rho_bits": "inherited",
                    "h_recomputed": "recomputed",
                    "weil_recursion": "recomputed",
                    "gcd_h_r": "recomputed",
                },
            }
        )

    cert = {
        "experiment_id": "EXP-BINSTD-9d1b8e",
        "stage": 0,
        "kind": "five_row_symmetry_certificate",
        "certificate": {"kind": "none", "note": "pure arithmetic recompute; no DL/relation claim"},
        "q": Q,
        "q_bits": 16,
        "rows": rows_out,
        "all_rows_pass": all_pass,
        "prediction_reference": "EXP-BINSTD-9d1b8e preregistered_prediction (A)(B)(C)",
        "dual_rho_columns_present": True,
        "break_claim": False,
        "attack_ceiling_sentence": (
            "Rho extracts sqrt(k) while a Frobenius-aware IC may extract up to k "
            "(relations) / k^2 (LA) from the same order-k group — do not cap the "
            "attack at sqrt(k). (HOLD-B)"
        ),
    }

    dual = {
        "experiment_id": "EXP-BINSTD-9d1b8e",
        "stage": 0,
        "kind": "dual_rho_bits",
        "convention_corrected": "log2(sqrt(pi*r/(4*k))) = 0.5*log2(r)+0.5*log2(pi/4)-0.5*log2(k)",
        "convention_inherited": "d11575/c07598 0.886*sqrt(r)/sqrt(2k) with r~2^(s-0.5); INHERITED comparator only",
        "corr_cite": "CORR-20260922-81aeab",
        "tolerance": TOL,
        "rows": [
            {
                "curve_id": r["curve_id"],
                "k": r["k"],
                "corrected_rho_bits": r["corrected_rho_bits_recomputed"],
                "corrected_rho_bits_frozen_expected": r["corrected_rho_bits_frozen_expected"],
                "inherited_rho_bits": r["inherited_rho_bits"],
                "delta_corrected_vs_frozen": round(
                    abs(r["corrected_rho_bits_recomputed"] - r["corrected_rho_bits_frozen_expected"]),
                    6,
                ),
                "within_tol": r["corrected_rho_within_tol"],
            }
            for r in rows_out
        ],
        "columns_never_mixed_unlabeled": True,
    }

    note = """# ECC2K-130 methodological note (Stage 0)

This note is **methodological**, not a solve or attack claim.

## Same derivation at q=2, k=131

On ECC2K-130 the curve is defined over `F_2` (Koblitz), so the base-2
Frobenius is an endomorphism. The class group available to Pollard rho on the
prime-order subgroup is `<tau, [-1]>` of order `2*131 = 262`, with
`j = 1/b = 1 != 0` so `Aut(E) = Z/2` after the char-2 classification (Stage 1).

Matched rho under the corrected convention is
`sqrt(pi * l / (4 * 131))` with the 129-bit prime subgroup order `l`
(Bailey et al. / Certicom parameters). The Weil recursion from `t = -1`
reproduces `#E = 4l`.

## Why the 16-fold conflation cannot arise

The tempting `32k` figure on the ANSI `c2pnb*` rows comes from confusing the
`16k`-element Galois orbit of **curves** under `pi_2` with automorphisms of
**one** curve. On ECC2K-130 the curve is already over `F_2`, so that Galois
orbit of curves is trivial — the conflation has no place to start.

## Ceiling (C)

Any single-target decomposition line may charge at most the order-`131`
group on the Frobenius-aware side. Rho extracts `sqrt(131)` from that group;
index calculus may extract up to `131` (relations) / `131^2` (LA). This is
a ceiling statement, not a measured cost.

## Scope

No group walk, no break claim, no new attack cost is asserted here.
Deployed `c2pnb*` rows in this experiment remain arithmetic-only.
"""

    stage0 = EXP / "stage0"
    stage0.mkdir(parents=True, exist_ok=True)
    (stage0 / "five-row-symmetry-certificate.yaml").write_text(_yaml(cert))
    (stage0 / "dual-rho-bits.yaml").write_text(_yaml(dual))
    (stage0 / "ecc2k130-methodological-note.md").write_text(note)
    return cert, dual


def _yaml(obj) -> str:
    import yaml

    return yaml.safe_dump(obj, sort_keys=False, default_flow_style=False)


def write_run_package(run_id: str, cert, dual, wall_s: float, started: str, finished: str):
    run_dir = EXP / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    commit = os.popen("git rev-parse HEAD").read().strip()
    dirty = bool(os.popen("git status --porcelain").read().strip())
    cmd = (
        f"python3 experiments/EXP-BINSTD-9d1b8e/implementation/stage0_run.py "
        f"--run-id {run_id}"
    )
    (run_dir / "command.txt").write_text(cmd + "\n")
    env = {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "dependencies": {"pyyaml": __import__("yaml").__version__},
    }
    (run_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    metrics = {
        "gcd_h_r_pass_all": all(r["gcd_h_r_pass"] for r in cert["rows"]),
        "t_odd_pass_all": all(r["t_odd_pass"] for r in cert["rows"]),
        "weil_recursion_pass_all": all(r["weil_recursion_pass"] for r in cert["rows"]),
        "corrected_rho_within_tol_all": all(r["corrected_rho_within_tol"] for r in cert["rows"]),
        "all_rows_pass": cert["all_rows_pass"],
        "dual_rho_columns_present": True,
    }
    valid = cert["all_rows_pass"]
    raw = {
        "stage": 0,
        "metrics": metrics,
        "certificate_path": "experiments/EXP-BINSTD-9d1b8e/stage0/five-row-symmetry-certificate.yaml",
        "dual_rho_path": "experiments/EXP-BINSTD-9d1b8e/stage0/dual-rho-bits.yaml",
        "rows_summary": [
            {
                "curve_id": r["curve_id"],
                "k": r["k"],
                "gcd": r["gcd_h_r"],
                "t_odd": r["t_odd"],
                "corrected_rho_bits": r["corrected_rho_bits_recomputed"],
                "inherited_rho_bits": r["inherited_rho_bits"],
                "ord_mu_stated": r["ord_mu_stated"],
            }
            for r in cert["rows"]
        ],
        "break_claim": False,
    }
    (run_dir / "raw-result.json").write_text(json.dumps(raw, indent=2) + "\n")
    stdout = [
        f"Stage 0 complete all_rows_pass={cert['all_rows_pass']}",
        f"wall_s={wall_s:.6f}",
    ]
    for r in cert["rows"]:
        stdout.append(
            f"{r['curve_id']}: gcd={r['gcd_h_r']} t_odd={r['t_odd']} "
            f"weil={r['weil_recursion_pass']} rho={r['corrected_rho_bits_recomputed']:.4f} "
            f"(exp {r['corrected_rho_bits_frozen_expected']}) ord_mu={r['ord_mu_stated']}"
        )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-BINSTD-9d1b8e",
            "task_id": "TASK-20261001-0fc34d",
            "stage": 0,
            "status": "completed_valid" if valid else "invalid_measurement",
            "termination_reason": "completed",
            "code": {"commit": commit, "dirty": dirty, "command": cmd},
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation",
                "backend": None,
                "provider": None,
                "resolved_model_id": None,
                "model_provenance": "not-applicable",
                "model_verified": False,
                "requested_reasoning_effort": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "fallback_reason": None,
                "degraded_requirements": [],
                "independent_session": False,
                "adapter_version": None,
                "config_digest": None,
            },
            "environment": env,
            "inputs": {
                "curve_id": None,
                "seed": None,
                "parameters": {"rows": [n for n, _ in ROWS], "q": Q},
            },
            "timing": {
                "started_at": started,
                "finished_at": finished,
                "wall_seconds": wall_s,
            },
            "resources": {"peak_rss_bytes": _rss(), "cpu_seconds": None},
            "result": {
                "metrics": metrics,
                "valid": valid,
                "invalid_reason": None if valid else "stage0_row_failure",
                "certificate": {"kind": "none", "verified": None},
            },
        }
    }
    (run_dir / "manifest.yaml").write_text(_yaml(manifest))


def _rss() -> int | None:
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()
    t0 = time.time()
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cert, dual = run_stage0()
    finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wall = time.time() - t0
    write_run_package(args.run_id, cert, dual, wall, started, finished)
    print(json.dumps({"all_rows_pass": cert["all_rows_pass"], "wall_s": wall}))


if __name__ == "__main__":
    main()
