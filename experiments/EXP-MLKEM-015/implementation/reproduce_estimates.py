#!/usr/bin/env python3
"""Reproduce EXP-MLKEM-015 matched Kyber cost table.

Requires Sage with lattice-estimator on PYTHONPATH at the pinned commit
recorded in ../source-lock.yaml.
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from estimator import LWE, RC, schemes  # type: ignore
from estimator.lwe_dual import dual_hybrid  # type: ignore
from sage.all import RR, log  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "RUN-MLKEM-015-001"
NIST = {"Kyber512": 143, "Kyber768": 207, "Kyber1024": 272}
CARRIER = {"Kyber512": 139.5, "Kyber768": 195.1, "Kyber1024": 259.7}
MATZOV22 = {"Kyber512": 137.5, "Kyber768": 193.5, "Kyber1024": 257.8}
SCHEMES = {
    "Kyber512": schemes.Kyber512,
    "Kyber768": schemes.Kyber768,
    "Kyber1024": schemes.Kyber1024,
}


def lg2(x) -> float:
    return float(RR(log(x, 2)))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "vendor" / "lattice-estimator", text=True).strip()
    summaries = {}
    for name, params in SCHEMES.items():
        row = {}
        for cm_name, cm in [("MATZOV", RC.MATZOV), ("ADPS16", RC.ADPS16), ("GJ21", RC.GJ21)]:
            for fft in (False, True):
                r = dual_hybrid(params, red_cost_model=cm, fft=fft)
                row[f"dual_hybrid/{cm_name}/fft={fft}"] = lg2(r["rop"])
            for tag, fn in [("primal_usvp", LWE.primal_usvp), ("primal_bdd", LWE.primal_bdd)]:
                r = fn(params, red_cost_model=cm)
                row[f"{tag}/{cm_name}"] = lg2(r["rop"])
        dual_fft = row["dual_hybrid/MATZOV/fft=True"]
        primal_bdd = row["primal_bdd/MATZOV"]
        primal_usvp = row["primal_usvp/MATZOV"]
        best_name, best = min(
            [
                ("dual_hybrid/MATZOV/fft=True", dual_fft),
                ("primal_bdd/MATZOV", primal_bdd),
                ("primal_usvp/MATZOV", primal_usvp),
            ],
            key=lambda t: t[1],
        )
        summaries[name] = {
            "best_MATZOV_attack": best_name,
            "best_MATZOV_log2": best,
            "MATZOV_margin_vs_nist_bits": NIST[name] - best,
            "dual_fft_MATZOV_log2": dual_fft,
            "primal_bdd_MATZOV_log2": primal_bdd,
            "dual_fft_minus_primal_bdd_bits": dual_fft - primal_bdd,
            "carrier_claimed_log2": CARRIER[name],
            "carrier_claim_minus_our_dual_fft_bits": CARRIER[name] - dual_fft,
            "matzov2022_claimed_log2": MATZOV22[name],
            "matzov2022_claim_minus_our_dual_fft_bits": MATZOV22[name] - dual_fft,
            "coreSVP_primal_ADPS16_log2": row["primal_usvp/ADPS16"],
            "coreSVP_dual_hybrid_ADPS16_fft_log2": row["dual_hybrid/ADPS16/fft=True"],
            "raw": row,
        }
        print(name, json.dumps(summaries[name], indent=None))

    meta = {
        "run_id": "RUN-MLKEM-015-001",
        "experiment_id": "EXP-MLKEM-015",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "lattice_estimator_commit": commit,
        "platform": platform.platform(),
        "nist_cutoffs": NIST,
        "summaries_MATZOV_matched": {
            k: {kk: vv for kk, vv in v.items() if kk != "raw"} for k, v in summaries.items()
        },
        "raw_by_scheme": {k: v["raw"] for k, v in summaries.items()},
    }
    (OUT / "results.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("WROTE", OUT / "results.json")


if __name__ == "__main__":
    main()
