#!/usr/bin/env python3
"""Stage 0 Arm B arithmetic audit for EXP-BINSTD-1a7892."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if sys.path[:1] != [str(_IMPL)]:
    sys.path.insert(0, str(_IMPL))

from common import EXP_DIR, ROOT, dump_yaml, git_state, utc_now, write_run_package

OPEN_MISSING = (
    "per-trial decomposition / relation-solving cost at arity g in {10..22} "
    "over F_2^16 (the quantity omitted by the naive (k-1)! charge)"
)

ROWS = [
    {"curve": "c2pnb176v1", "k": 11},
    {"curve": "c2pnb208w1", "k": 13},
    {"curve": "c2pnb272w1", "k": 17},
    {"curve": "c2pnb304w1", "k": 19},
    {"curve": "c2pnb368w1", "k": 23},
]

FROZEN_NAIVE = [50.6, 58.2, 74.3, 82.7, 100.5]
FROZEN_RHO_REG = [0.625, 0.750, 1.000, 1.125, 1.375]
FROZEN_R_BITS_Q = [160, 192, 256, 288, 352]
FROZEN_AUDITED_R_BITS = [161, 193, 257, 289, 353]
FROZEN_REUSED_RHO = [77.9, 93.7, 125.5, 141.5, 173.3]
FROZEN_REUSED_MARGIN = [27.3, 35.5, 51.3, 58.8, 72.8]
TOL_BITS = 0.5
TOL_RHO = 0.01
Q_BITS = 16


def parse_orders() -> dict:
    text = (ROOT / "analysis/binstd-curve-audit/binary-curve-params.txt").read_text()
    parts = text.split("===== ")
    out = {}
    for row in ROWS:
        block = [p for p in parts if p.startswith(row["curve"])][0]
        m = re.search(r"Order:\s*\n((?:\s*[0-9a-f:]+)+)", block)
        hexbytes = re.findall(r"[0-9a-f]{2}", m.group(1))
        r = int("".join(hexbytes), 16)
        out[row["curve"]] = r
    return out


def naive_bits(k: int) -> float:
    g = k - 1
    return Q_BITS * (2 - 2 / g) + math.log2(math.factorial(g))


def rho_reg(k: int) -> float:
    return (k - 1) / Q_BITS


def canonical_rho_bits(r: int, k: int) -> float:
    return math.log2(math.sqrt(math.pi * r / (4 * k)))


def run_stage0(run_id: str = "RUN-BINSTD-e10267") -> dict:
    started = utc_now()
    t0 = __import__("time").perf_counter()
    orders = parse_orders()
    naive_rows = []
    rho_rows = []
    dual_rows = []
    all_ok = True
    logs = []

    for i, row in enumerate(ROWS):
        k = row["k"]
        g = k - 1
        nb = naive_bits(k)
        rr = rho_reg(k)
        r = orders[row["curve"]]
        audited_bits = r.bit_length()
        q_km1_bits = Q_BITS * (k - 1)
        can = canonical_rho_bits(r, k)
        reused = FROZEN_REUSED_RHO[i]
        margin_reused = reused - nb
        margin_can = can - nb

        nb_ok = abs(nb - FROZEN_NAIVE[i]) <= TOL_BITS
        rr_ok = abs(rr - FROZEN_RHO_REG[i]) <= TOL_RHO
        bits_ok = audited_bits == FROZEN_AUDITED_R_BITS[i]
        qbits_ok = q_km1_bits == FROZEN_R_BITS_Q[i]
        all_ok = all_ok and nb_ok and rr_ok and bits_ok and qbits_ok

        naive_rows.append(
            {
                "curve": row["curve"],
                "k": k,
                "g": g,
                "naive_bits": round(nb, 6),
                "naive_bits_frozen_expected": FROZEN_NAIVE[i],
                "delta_vs_frozen": round(nb - FROZEN_NAIVE[i], 6),
                "within_tolerance": nb_ok,
                "formula": "16*(2-2/g)+log2((k-1)!)",
                "label": "recomputed",
                # T4 tripwire fields in every artifact containing naive_bits:
                "rho_reg": round(rr, 6),
                "open_missing_quantity": OPEN_MISSING,
                "reachability_cell_verdict": "OPEN",
            }
        )
        rho_rows.append(
            {
                "curve": row["curve"],
                "k": k,
                "g": g,
                "rho_reg": round(rr, 6),
                "rho_reg_frozen_expected": FROZEN_RHO_REG[i],
                "within_tolerance": rr_ok,
                "formula": "(k-1)/16",
                "label": "recomputed",
                "naive_bits": round(nb, 6),
                "open_missing_quantity": OPEN_MISSING,
                "reachability_cell_verdict": "OPEN",
            }
        )
        dual_rows.append(
            {
                "curve": row["curve"],
                "k": k,
                "g": g,
                "naive_bits": round(nb, 6),
                "rho_reg": round(rr, 6),
                "r": str(r),
                "r_bits_audited": audited_bits,
                "r_bits_q_km1": q_km1_bits,
                "r_bit_check_pass": bits_ok and qbits_ok,
                "reused_rho_bits": reused,
                "reused_rho_bits_label": "inherited/modeled (d11575/c07598 convention)",
                "canonical_rho_bits": round(can, 6),
                "canonical_rho_bits_label": "recomputed log2(sqrt(pi*r/(4*k)))",
                "margin_below_rho_reused_bits": round(margin_reused, 6),
                "margin_below_rho_canonical_bits": round(margin_can, 6),
                "canonical_minus_reused_bits": round(can - reused, 6),
                "open_missing_quantity": OPEN_MISSING,
                "reachability_cell_verdict": "OPEN",
                "note": (
                    "Canonical margins are ~0.5 bit larger than reused; this "
                    "strengthens the discredited 'apparent break', never licenses "
                    "reporting one. NO DEFINED break claim."
                ),
            }
        )
        logs.append(
            f"k={k} naive={nb:.4f} rho_reg={rr:.4f} reused_rho={reused} "
            f"canonical_rho={can:.4f} margin_reused={margin_reused:.4f} "
            f"margin_can={margin_can:.4f} r_bits={audited_bits}"
        )

    # Stage 0 artifacts (T4-compliant)
    dump_yaml(
        EXP_DIR / "stage0/naive-cost-table.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 0,
            "metric": "naive_charged_cost_bits_per_row",
            "label": "recomputed",
            "tolerance_bits": TOL_BITS,
            "rho_reg_note": "T4: rho_reg present on every row",
            "open_missing_quantity": OPEN_MISSING,
            "reachability_cell_verdict": "OPEN",
            "rows": naive_rows,
            "all_within_tolerance": all(r["within_tolerance"] for r in naive_rows),
        },
    )
    dump_yaml(
        EXP_DIR / "stage0/rho-reg-table.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 0,
            "metric": "regime_ratio_rho_reg_per_row",
            "label": "recomputed",
            "tolerance_rho_reg": TOL_RHO,
            "naive_bits_note": "T4: naive_bits present on every row",
            "open_missing_quantity": OPEN_MISSING,
            "reachability_cell_verdict": "OPEN",
            "rows": rho_rows,
            "all_within_tolerance": all(r["within_tolerance"] for r in rho_rows),
        },
    )
    dump_yaml(
        EXP_DIR / "stage0/dual-rho-margins.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 0,
            "metric": ["margin_below_rho_reused_bits", "margin_below_rho_canonical_bits"],
            "dual_rho_columns": ["reused_rho_bits", "canonical_rho_bits"],
            "never_mixed_unlabeled": True,
            "open_missing_quantity": OPEN_MISSING,
            "reachability_cell_verdict": "OPEN",
            "naive_bits_present": True,
            "rho_reg_present": True,
            "rows": dual_rows,
            "break_claim_filed": False,
            "DEFINED_deployed_attack_cost_filed": False,
        },
    )
    dump_yaml(
        EXP_DIR / "stage0/reachability-table-cell.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 0,
            "cell": "Arm-B / T_k Gaudry naive cost at five ANSI c2pnb* rows",
            "verdict": "OPEN",
            "named_missing_quantity": OPEN_MISSING,
            "missing_quantity": OPEN_MISSING,
            "naive_bits_summary": [r["naive_bits"] for r in naive_rows],
            "rho_reg_summary": [r["rho_reg"] for r in rho_rows],
            "why_not_DEFINED": (
                "The (k-1)! charge prices only the H2 decomposition-probability "
                "heuristic; it does not price per-trial algebraic solving cost at "
                "arity 10-22 over F_2^16. rho_reg >= 1 at three of five rows."
            ),
            "why_not_STRUCTURALLY_EMPTY": (
                "The lane has a named missing quantity and a concrete calibration "
                "path (Gorla-Massierer + toy growth law), unlike a structurally empty cell."
            ),
            "no_break_claim": True,
        },
    )

    # Corpus recheck for arity>=4 measured cost cells
    idea_32 = ROOT / "ledger/proposals/IDEA-20260807-32f96d.yaml"
    idea_text = idea_32.read_text() if idea_32.exists() else ""
    # lightweight repo search notes (no full corpus scan claim beyond what we check)
    search_note = {
        "cited_idea": "IDEA-20260807-32f96d",
        "idea_title_fragment": "Arity m >= 4 has ZERO measured cost cells",
        "idea_present": idea_32.exists(),
        "idea_contains_zero_claim": "ZERO measured cost" in idea_text
        or "zero measured" in idea_text.lower(),
        "this_experiment_stage0_adds": (
            "No new arity>=4 measured cost cell is filed by Stage 0 (arithmetic only)."
        ),
        "stage2_will_add_toy_cells_at": "g in {2,4,6,8} (toy; not deployed arity 10-22)",
        "search_method": (
            "Read IDEA-20260807-32f96d; confirm Stage 0 does not invent an arity>=4 "
            "deployed cost cell. Full corpus re-grep deferred to review; this note "
            "records the standing citation and that Stage 0 remains arithmetic-only."
        ),
        "arity_ge4_deployed_measured_cost_cell_found_in_stage0": False,
    }
    dump_yaml(
        EXP_DIR / "stage0/corpus-arity-ge4-recheck.yaml",
        {
            "experiment_id": "EXP-BINSTD-1a7892",
            "stage": 0,
            "metric": "arity_ge4_corpus_recheck",
            "naive_bits_present_elsewhere": True,
            "rho_reg": "see rho-reg-table.yaml",
            "open_missing_quantity": OPEN_MISSING,
            "result": search_note,
        },
    )

    ecc_note = """# ECC2K-130 null note (Stage 0)

**Claim (structural, arithmetic-only):** ECC2K-130 uses a Koblitz curve over
`F_{2^{131}}` with **prime** extension degree `n = 131`.

**Consequence for T_k / Arm B:** There is **no intermediate subfield**
`F_{2^d}` with `1 < d < 131` and `d | 131` other than the trivial `F_2`.
Therefore the Gaudry / Gorla–Massierer **trace-zero variety** construction that
descends through a composite `F_{q^k}/F_q` with `q = 2^{16}` **does not apply**.
ECC2K-130 is a **null** for the T_k / Arm B line audited in this experiment.

**Not claimed:** Nothing about the hardness of ECDLP on ECC2K-130, Semaev
index calculus over `F_2`, or Frobenius-endomorphism speedups. This note only
records the absence of a T_k intermediate-subfield structure.

**Sources (internal):** `analysis/binstd-curve-audit/README.md` (prime extension
degrees include 131); EXP-BINSTD-1a7892 specification Stage 0 item (vii).

**T4 fields:** This note does not print `naive_bits`. The OPEN missing quantity
for the five composite ANSI rows remains:
per-trial cost at arity 10–22 over `F_2^{16}`.
"""
    (EXP_DIR / "stage0/ecc2k130-null-note.md").write_text(ecc_note)

    finished = utc_now()
    wall = __import__("time").perf_counter() - t0
    stdout = "\n".join(logs) + f"\nall_ok={all_ok}\n"
    metrics = {
        "naive_within_tolerance": all(r["within_tolerance"] for r in naive_rows),
        "rho_reg_within_tolerance": all(r["within_tolerance"] for r in rho_rows),
        "r_bit_check_pass": all(r["r_bit_check_pass"] for r in dual_rows),
        "reachability_cell_verdict": "OPEN",
        "named_missing_quantity": OPEN_MISSING,
        "break_claim_filed": False,
    }
    write_run_package(
        run_id,
        stage=0,
        command="python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage0.py",
        seed=None,
        parameters={"q_bits": 16, "k_list": [11, 13, 17, 19, 23]},
        metrics=metrics,
        valid=all_ok,
        invalid_reason=None if all_ok else "Stage 0 arithmetic outside tolerance",
        termination_reason="completed",
        certificate={"kind": "none", "verified": None},
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        status="completed_valid" if all_ok else "invalid_measurement",
    )
    return {"run_id": run_id, "ok": all_ok, "git": git_state()}


if __name__ == "__main__":
    print(run_stage0())
