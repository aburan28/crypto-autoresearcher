#!/usr/bin/env python3
"""Separate exact fixed target setup from the two archived C proxy studies."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import tarfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
STUDIES = [
    {
        "label": "m37",
        "m": 37,
        "qpow": 28,
        "r_add": 128,
        "archive": ROOT
        / "research/isogeny_volcano_rho_20261005/data/raw_solves.tar.gz",
    },
    {
        "label": "m41",
        "m": 41,
        "qpow": 40,
        "r_add": 128,
        "archive": ROOT
        / "research/isogeny_volcano_rho_m41_20261006/data/raw_solves.tar.gz",
    },
]
RESAMPLES = 50_000
ROOT_SEED = 2026101304


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mode(path: Path, mode: int) -> tuple[np.ndarray, int]:
    pattern = re.compile(rf"^raw/c0_m{mode}_r[0-9]+[.]csv$")
    ops: list[int] = []
    verified = 0
    with tarfile.open(path, "r:gz") as archive:
        members = sorted(
            (member for member in archive.getmembers() if pattern.match(member.name)),
            key=lambda member: member.name,
        )
        if not members:
            raise ValueError(f"no mode {mode} rows in {path}")
        for member in members:
            extracted = archive.extractfile(member)
            if extracted is None:
                raise ValueError(f"cannot read {member.name}")
            with io.TextIOWrapper(extracted, encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    ops.append(int(row["ops"]))
                    verified += int(row["ok"])
    return np.asarray(ops, dtype=np.float64), verified


def independent_percentile_ratio(
    numerator: np.ndarray, denominator: np.ndarray, *, seed_parts: list[int]
) -> dict[str, float | int | str]:
    rng = np.random.default_rng(np.random.SeedSequence(seed_parts))
    draws = np.empty(RESAMPLES, dtype=np.float64)
    batch = 1_000
    for start in range(0, RESAMPLES, batch):
        stop = min(RESAMPLES, start + batch)
        size = stop - start
        num = rng.choice(numerator, (size, len(numerator)), replace=True).mean(axis=1)
        den = rng.choice(denominator, (size, len(denominator)), replace=True).mean(axis=1)
        draws[start:stop] = num / den
    point = float(np.mean(numerator) / np.mean(denominator))
    low, high = (float(value) for value in np.quantile(draws, [0.025, 0.975]))
    return {
        "estimand": "ratio_of_arithmetic_means",
        "ratio": point,
        "ci95_low": low,
        "ci95_high": high,
        "bits": math.log2(point),
        "bits_ci95_low": math.log2(low),
        "bits_ci95_high": math.log2(high),
        "method": "independent-arm percentile bootstrap",
        "resamples": RESAMPLES,
        "root_seed": ROOT_SEED,
    }


def main() -> None:
    rows = []
    for study in STUDIES:
        neg, neg_verified = load_mode(study["archive"], 0)
        frob, frob_verified = load_mode(study["archive"], 1)
        if neg_verified != len(neg) or frob_verified != len(frob):
            raise ValueError(f"unverified archived row in {study['label']}")
        setup = study["qpow"] - 1 + study["r_add"]
        if np.any(neg <= setup) or np.any(frob <= setup):
            raise ValueError(f"setup exceeds total count in {study['label']}")
        total = independent_percentile_ratio(
            neg, frob, seed_parts=[ROOT_SEED, study["m"], 1]
        )
        target_dependent = independent_percentile_ratio(
            neg - setup, frob - setup, seed_parts=[ROOT_SEED, study["m"], 2]
        )
        model_bits = 0.5 * math.log2(study["m"])
        rows.append(
            {
                "label": study["label"],
                "m": study["m"],
                "archive": str(study["archive"].relative_to(ROOT)),
                "archive_sha256": file_sha256(study["archive"]),
                "negation_rows": len(neg),
                "frobenius_rows": len(frob),
                "all_rows_verified": True,
                "fixed_setup_operations_per_solve": setup,
                "fixed_setup_derivation": "(QPOW - 1) target doublings + R_ADD target-table additions",
                "mean_total_ops": {
                    "rho-neg": float(np.mean(neg)),
                    "rho-frob": float(np.mean(frob)),
                },
                "mean_setup_excluded_target_dependent_ops": {
                    "rho-neg": float(np.mean(neg - setup)),
                    "rho-frob": float(np.mean(frob - setup)),
                },
                "total_ops_neg_over_frob": total,
                "setup_excluded_target_dependent_ops_neg_over_frob": target_dependent,
                "model": {"sqrt_m": math.sqrt(study["m"]), "rho_bits": model_bits},
                "setup_excluded_residual_bits": target_dependent["bits"] - model_bits,
            }
        )
    output = {
        "schema": "archived-koblitz-fixed-setup-reanalysis/v1",
        "status": "EXPLORATORY_DERIVED_REANALYSIS",
        "claim_boundary": (
            "contextual reanalysis of archived independent-arm C studies; "
            "not pooled with the fresh ecbench ladder and not ledger evidence"
        ),
        "warning": (
            "after fixed setup is removed, counts still include walk starts, "
            "look-ahead additions, cycle escapes, and abandoned work; recovery "
            "and verification are excluded, and the counts are not identical to "
            "ecbench walk_operations"
        ),
        "studies": rows,
    }
    target = Path(__file__).with_name("archived-setup-reanalysis.json")
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
