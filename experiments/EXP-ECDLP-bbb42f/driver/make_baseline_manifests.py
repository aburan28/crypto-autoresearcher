#!/usr/bin/env python3
"""Extracts per-curve CTRL-BASELINE (rho + BSGS) manifests from the three
census run results.json files into results/baseline_manifests/, one file
per bit size, per required_artifacts_note."""
from __future__ import annotations

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(BASE, "runs")
OUT = os.path.join(BASE, "results", "baseline_manifests")


def main():
    os.makedirs(OUT, exist_ok=True)
    for run_id, bit_size in [
        ("RUN-ECDLP-bbb42f-1", 20),
        ("RUN-ECDLP-bbb42f-2", 24),
        ("RUN-ECDLP-bbb42f-3", 28),
    ]:
        with open(os.path.join(RUNS, run_id, "results.json")) as f:
            data = json.load(f)
        manifest = {
            "bit_size": bit_size,
            "p": data["p"],
            "run_id": run_id,
            "solver": "pollard_rho_plain (rho_bsgs.py) + bsgs (rho_bsgs.py)",
            "curves": [
                {
                    "curve_index": c["curve_index"], "a": c["a"], "b": c["b"], "N": c["N"],
                    "P": c["baseline"]["P"], "Q": c["baseline"]["Q"], "k_true": c["baseline"]["k_true"],
                    "rho": {k: v for k, v in c["baseline"]["rho"].items()},
                    "bsgs": {k: v for k, v in c["baseline"]["bsgs"].items()},
                }
                for c in data["curves"]
            ],
        }
        outpath = os.path.join(OUT, f"baseline_manifest_bits{bit_size}.json")
        with open(outpath, "w") as f:
            json.dump(manifest, f, indent=2)
        print("wrote", outpath)


if __name__ == "__main__":
    main()
