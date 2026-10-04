#!/usr/bin/env python3
"""Fit-observation package of EXP-ECDLP-5cad48.

Authorized computation only under DEC-20260907-03e776 /
v1_stage2_fit_authorized. Consumes recorded Stage 2 / H3 / Stage 1
tables. Does not classify W. Does not set fit_of_a true.
Certificate kind none. No a98ea9 Stage 5.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[3]
EXP = REPO / "experiments" / "EXP-ECDLP-5cad48"
AUTH = EXP / "amendments" / "v1_stage2_fit_authorized.yaml"
S2_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2" / "raw-result.json"
H3_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S2H3" / "raw-result.json"
S1_RAW = EXP / "runs" / "RUN-ECDLP-5cad48-S1" / "raw-result.json"

CELLS = (
    {"id": "S2-P523", "p": 523, "M_grid": (5, 8, 12)},
    {"id": "S2-P1033", "p": 1033, "M_grid": (6, 10, 16)},
    {"id": "S2-P2063", "p": 2063, "M_grid": (7, 13, 21)},
    {"id": "S2-P4111", "p": 4111, "M_grid": (8, 16, 28)},
    {"id": "S2-P8219", "p": 8219, "M_grid": (9, 20, 37)},
    {"id": "S2-P16417", "p": 16417, "M_grid": (11, 25, 49)},
    {"id": "S2-P32779", "p": 32779, "M_grid": (13, 32, 64)},
    {"id": "S2-P65539", "p": 65539, "M_grid": (16, 40, 84)},
)
COVERED = ("floor(Mx/p)", "x mod M", "quadratic_character")
ALL_ARMS = (
    "floor(Mx/p)",
    "x mod M",
    "quadratic_character",
    "sha",
    "shuffle",
    "P2",
    "planted_theta",
)
N_PAIRS_STAGE2 = 1_000_000
H2_C0 = 0.25
Z95 = 1.96
SEED = 20260803


def _git_info() -> dict:
    def _run(args):
        try:
            return subprocess.run(
                ["git"] + args, cwd=REPO, capture_output=True, text=True, timeout=30
            ).stdout.strip()
        except Exception as exc:
            return f"error: {exc}"

    dirty = _run(["status", "--porcelain"])
    return {
        "commit": _run(["rev-parse", "HEAD"]),
        "dirty": dirty != "",
        "dirty_summary": dirty[:2000],
    }


def peak_rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def refuse_unless_authorized() -> None:
    text = AUTH.read_text()
    rec = yaml.safe_load(text)
    block = rec.get("protocol_amendment", rec)
    if not block.get("fit_of_a_execution_authorized"):
        raise SystemExit("refuse: fit_of_a_execution_authorized is not true")
    if block.get("SMALL_W_or_LARGE_W"):
        raise SystemExit("refuse: authorization classified W")
    if block.get("fit_of_a"):
        raise SystemExit("refuse: authorization set fit_of_a true")


def index_cells(raw: dict) -> dict:
    return {cell["id"]: cell for cell in raw["cells"]}


def arm_rec(cell: dict, m: int, arm: str) -> dict:
    for block in cell["Ms"]:
        if int(block["M"]) == int(m):
            return block["arms"][arm]
    raise KeyError(f"missing M={m} in {cell['id']}")


def ols_unconstrained(rows: list[dict]) -> dict | None:
    if len(rows) < 3:
        return None
    log_m = np.log(np.array([r["M"] for r in rows], dtype=np.float64))
    log_p = np.log(np.array([r["p"] for r in rows], dtype=np.float64))
    y = np.log(np.array([r["W"] for r in rows], dtype=np.float64))
    x = np.column_stack([np.ones(len(rows)), log_m, log_p])
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return {"c": float(beta[0]), "a": float(beta[1]), "b": float(beta[2]), "n": len(rows)}


def ols_constrained(rows: list[dict]) -> dict | None:
    if len(rows) < 2:
        return None
    log_m = np.log(np.array([r["M"] for r in rows], dtype=np.float64))
    log_p = np.log(np.array([r["p"] for r in rows], dtype=np.float64))
    y = np.log(np.array([r["W"] for r in rows], dtype=np.float64)) + 0.5 * log_p
    x = np.column_stack([np.ones(len(rows)), log_m])
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return {"c": float(beta[0]), "a": float(beta[1]), "b": -0.5, "n": len(rows)}


def jackknife(rows: list[dict], fit_fn) -> dict:
    full = fit_fn(rows)
    primes = sorted({r["p"] for r in rows})
    left = []
    for p in primes:
        sub = [r for r in rows if r["p"] != p]
        est = fit_fn(sub)
        if est is not None:
            left.append({"left_out_p": p, **est})
    out = {
        "full": full,
        "leave_one_prime": left,
        "n_primes_represented": len(primes),
        "interval_a": None,
        "interval_b": None,
    }
    if full is None or len(left) < 2:
        return out
    a_i = np.array([e["a"] for e in left], dtype=np.float64)
    b_i = np.array([e["b"] for e in left], dtype=np.float64)
    n = float(len(left))
    se_a = math.sqrt(((n - 1.0) / n) * float(np.sum((a_i - a_i.mean()) ** 2)))
    se_b = math.sqrt(((n - 1.0) / n) * float(np.sum((b_i - b_i.mean()) ** 2)))
    out["interval_a"] = [full["a"] - Z95 * se_a, full["a"] + Z95 * se_a]
    out["interval_b"] = [full["b"] - Z95 * se_b, full["b"] + Z95 * se_b]
    out["se_a"] = se_a
    out["se_b"] = se_b
    return out


def h3_gate(h3: dict) -> dict:
    cells = index_cells(h3)
    checks = []
    failed = False
    for cell_id, m_grid in (("S2-P523", (5, 8, 12)), ("S2-P1033", (6, 10, 16))):
        cell = cells[cell_id]
        for m in m_grid:
            for arm in COVERED:
                rec = arm_rec(cell, m, arm)
                w_exact = float(rec["W_exact"])
                w_mult = (m - 1) / float(N_PAIRS_STAGE2)
                scale = max(w_exact, w_mult)
                thresh = 0.25 * scale
                mean_b = float(rec["mean_bias_jack"])
                se_b = float(rec["se_bias_jack"])
                biases = np.array([abs(float(d["bias_jack"])) for d in rec["draws"]], dtype=np.float64)
                p99 = float(np.percentile(biases, 99))
                mean_fail = abs(mean_b) + 2.0 * se_b >= thresh
                p99_fail = p99 >= thresh
                row = {
                    "cell": cell_id,
                    "M": m,
                    "arm": arm,
                    "W_exact": w_exact,
                    "W_multinomial": w_mult,
                    "scale": scale,
                    "threshold": thresh,
                    "mean_bias_jack": mean_b,
                    "se_bias_jack": se_b,
                    "p99_abs_bias_jack": p99,
                    "mean_fail": mean_fail,
                    "p99_fail": p99_fail,
                }
                checks.append(row)
                if mean_fail or p99_fail:
                    failed = True
    return {
        "pass": not failed,
        "n_pairs_stage2": N_PAIRS_STAGE2,
        "formula": "fail if |mean_bias_jack|+2*se >= 0.25*scale or p99(|bias_jack|) >= 0.25*scale",
        "two_prime_n1e7_does_not_prove_n1e6_on_six_larger": True,
        "checks": checks,
    }


def collect_rows(s2: dict, arm: str, response: str) -> tuple[list[dict], list[dict]]:
    cells = index_cells(s2)
    kept: list[dict] = []
    excluded: list[dict] = []
    for spec in CELLS:
        cell = cells[spec["id"]]
        for m in spec["M_grid"]:
            rec = arm_rec(cell, m, arm)
            sha = arm_rec(cell, m, "sha")
            w_plugin = float(rec["W_plugin"])
            w_jack = float(rec["W_jack"])
            min_q = float(rec["min_q"])
            h2_fail = (m * min_q) < H2_C0
            reason = None
            w = None
            if response == "W_plugin":
                if h2_fail:
                    reason = "H2"
                elif w_plugin <= 0:
                    reason = "nonpositive_W_plugin"
                else:
                    w = w_plugin
            else:
                w_rel = w_plugin - float(sha["W_plugin"])
                if h2_fail:
                    reason = "H2"
                elif w_rel <= 0:
                    reason = "nonpositive_W_rel"
                else:
                    w = w_rel
            row = {
                "cell": spec["id"],
                "p": spec["p"],
                "M": m,
                "arm": arm,
                "W_plugin": w_plugin,
                "W_jack": w_jack,
                "min_q": min_q,
                "cs_proxy": (
                    1.0 + math.sqrt(w_plugin / min_q)
                    if min_q > 0 and w_plugin >= 0
                    else None
                ),
            }
            if w is None:
                excluded.append({**row, "reason": reason})
            else:
                kept.append({**row, "W": w})
    return kept, excluded


def p2_sha_gate(s2: dict) -> dict:
    cells = index_cells(s2)
    per_prime = []
    ok = True
    for spec in CELLS:
        cell = cells[spec["id"]]
        ratios = []
        for m in spec["M_grid"]:
            p2 = float(arm_rec(cell, m, "P2")["W_plugin"])
            sha = float(arm_rec(cell, m, "sha")["W_plugin"])
            if p2 > 0 and sha > 0:
                ratios.append({"M": m, "ratio": p2 / sha})
        if ratios:
            prime_ok = all(r["ratio"] >= 10.0 for r in ratios)
            if not prime_ok:
                ok = False
        else:
            prime_ok = None
        per_prime.append({"cell": spec["id"], "p": spec["p"], "ok": prime_ok, "ratios": ratios})
    return {"pass": ok, "per_prime": per_prime}


def planted_sha_gate(s2: dict) -> dict:
    cells = index_cells(s2)
    hits = []
    for spec in CELLS:
        cell = cells[spec["id"]]
        hit = False
        for m in spec["M_grid"]:
            planted = float(arm_rec(cell, m, "planted_theta")["W_plugin"])
            sha = float(arm_rec(cell, m, "sha")["W_plugin"])
            if planted > 0 and sha > 0 and planted > sha:
                hit = True
        if hit:
            hits.append(spec["id"])
    return {"pass": len(hits) >= 3, "n_primes_exceeding_sha": len(hits), "cells": hits}


def fit_arm(s2: dict, arm: str) -> dict:
    plugin_rows, plugin_excl = collect_rows(s2, arm, "W_plugin")
    rel_rows, rel_excl = collect_rows(s2, arm, "W_rel")
    plugin_primes = {r["p"] for r in plugin_rows}
    rel_primes = {r["p"] for r in rel_rows}
    return {
        "arm": arm,
        "covered": arm in COVERED,
        "W_plugin": {
            "unconstrained": jackknife(plugin_rows, ols_unconstrained),
            "constrained_Weil": jackknife(plugin_rows, ols_constrained),
            "n_rows": len(plugin_rows),
            "n_primes": len(plugin_primes),
            "eight_primes_represented": len(plugin_primes) == 8,
            "exclusions": plugin_excl,
        },
        "W_rel": {
            "unconstrained": jackknife(rel_rows, ols_unconstrained),
            "constrained_Weil": jackknife(rel_rows, ols_constrained),
            "n_rows": len(rel_rows),
            "n_primes": len(rel_primes),
            "eight_primes_represented": len(rel_primes) == 8,
            "exclusions": rel_excl,
        },
    }


def main() -> int:
    refuse_unless_authorized()
    t0 = time.time()
    s2 = json.loads(S2_RAW.read_text())
    h3 = json.loads(H3_RAW.read_text())
    s1 = json.loads(S1_RAW.read_text())
    if s2["run_id"] != "RUN-ECDLP-5cad48-S2":
        raise SystemExit("refuse: unexpected Stage 2 run id")
    if len(s2["cells"]) != 8:
        raise SystemExit("refuse: Stage 2 table is not eight primes")

    h3_result = h3_gate(h3)
    p2_result = p2_sha_gate(s2)
    planted_result = planted_sha_gate(s2)
    fits = {arm: fit_arm(s2, arm) for arm in ALL_ARMS}

    covered_eight = all(
        fits[arm]["W_plugin"]["eight_primes_represented"]
        and fits[arm]["W_rel"]["eight_primes_represented"]
        for arm in COVERED
    )
    classification_eligible = bool(
        h3_result["pass"] and covered_eight and p2_result["pass"] and planted_result["pass"]
    )

    n_neg_jack = 0
    for cell in s2["cells"]:
        for block in cell["Ms"]:
            for rec in block["arms"].values():
                if float(rec["W_jack"]) < 0:
                    n_neg_jack += 1

    elapsed = time.time() - t0
    raw = {
        "experiment_id": "EXP-ECDLP-5cad48",
        "run_id": "RUN-ECDLP-5cad48-S2FIT",
        "stage": 2,
        "package": "eight_prime_fit_observation",
        "authorized_by": "DEC-20260907-03e776",
        "certificate": {"kind": "none"},
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
        "fit_of_a_execution_authorized": True,
        "classification_eligible": classification_eligible,
        "a98ea9_stage5_authorized": False,
        "H3_executed": True,
        "data_sources": {
            "stage2": "RUN-ECDLP-5cad48-S2",
            "h3": "RUN-ECDLP-5cad48-S2H3",
            "stage1": "RUN-ECDLP-5cad48-S1",
        },
        "n_cells": 8,
        "n_pairs_stage2": N_PAIRS_STAGE2,
        "seed": SEED,
        "negative_W_jack_count": n_neg_jack,
        "H3_gate": h3_result,
        "P2_vs_sha_gate": p2_result,
        "planted_vs_sha_gate": planted_result,
        "eight_prime_representation_after_exclusions": covered_eight,
        "fits": fits,
        "elapsed_seconds": elapsed,
        "peak_rss_bytes": peak_rss_bytes(),
        "git": _git_info(),
        "not_a_W_decay_claim": True,
        "later_classification_rule_not_applied": True,
        "stage1_run_id_checked": s1["run_id"],
    }

    run_dir = EXP / "runs" / "RUN-ECDLP-5cad48-S2FIT"
    run_dir.mkdir(parents=True, exist_ok=True)
    raw_path = run_dir / "raw-result.json"
    raw_path.write_text(json.dumps(raw, indent=2) + "\n")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        "  id: RUN-ECDLP-5cad48-S2FIT\n"
        "  experiment_id: EXP-ECDLP-5cad48\n"
        "  status: valid\n"
        "  certificate_kind: none\n"
        "  SMALL_W_or_LARGE_W: false\n"
        "  fit_of_a: false\n"
        "  classification_eligible_is_not_a_W_class: true\n"
        f"  raw_result_sha256: {raw_hash}\n"
    )
    (run_dir / "environment.json").write_text(
        json.dumps(
            {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__},
            indent=2,
        )
        + "\n"
    )
    (run_dir / "command.txt").write_text(
        "python3 experiments/EXP-ECDLP-5cad48/implementation/stage2_fit.py\n"
    )
    stdout = [
        f"RUN-ECDLP-5cad48-S2FIT elapsed={elapsed:.3f}s raw_sha256={raw_hash}",
        "Fit-observation only. W unclassified. fit_of_a false.",
        f"classification_eligible={classification_eligible} H3_gate={h3_result['pass']}",
        f"eight_primes_after_exclusions={covered_eight}",
    ]
    for arm in COVERED:
        full = fits[arm]["W_plugin"]["unconstrained"]["full"]
        if full:
            stdout.append(
                f"{arm} unconstrained a={full['a']:.8e} b={full['b']:.8e} n={full['n']}"
            )
    (run_dir / "stdout.log").write_text("\n".join(stdout) + "\n")
    (run_dir / "stderr.log").write_text("")
    (EXP / "execution-report-fit.yaml").write_text(
        "experiment_id: EXP-ECDLP-5cad48\n"
        "run_id: RUN-ECDLP-5cad48-S2FIT\n"
        "stage: 2\n"
        "package: eight_prime_fit_observation\n"
        "status: valid\n"
        "certificate:\n"
        "  kind: none\n"
        "SMALL_W_or_LARGE_W: false\n"
        "fit_of_a: false\n"
        "fit_of_a_execution_authorized: true\n"
        f"classification_eligible: {str(classification_eligible).lower()}\n"
        "a98ea9_stage5_authorized: false\n"
        f"raw_result_sha256: {raw_hash}\n"
        "not_a_W_decay_claim: true\n"
        "later_classification_rule_not_applied: true\n"
    )
    print("\n".join(stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
