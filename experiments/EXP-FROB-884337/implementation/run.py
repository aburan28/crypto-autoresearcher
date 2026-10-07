"""Frozen measurement for EXP-FROB-884337.

Writes manifest.yaml, raw-result.json, and reading.yaml. Does not edit
the ledger. A crash is an infrastructure failure, not a value of b.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from ntheory import (
    POLY,
    affine_points,
    branching,
    discriminant,
    fmul,
    in_subfield,
    norm,
)


def _flags(block: dict) -> dict:
    n = block["n_points"]
    k = block["n_image"]
    num = block["b_num"]
    den = block["b_den"]
    return {
        "mean_fibre_num": n,
        "mean_fibre_den": k,
        "l_eq_1": k > 0 and n == 2 * k,
        "l_eq_0": k > 0 and n == k,
        "l_ge_2": k > 0 and n >= 4 * k,
        "b_num": num,
        "b_den": den,
        "b_eq_1": den > 0 and num == den,
        "b_eq_2": den > 0 and num == 2 * den,
        "b_le_4": den > 0 and num <= 4 * den,
        "b_gt_4": den > 0 and num > 4 * den,
        "b_ge_6": den > 0 and num >= 6 * den,
        "loops_agree": block["loops_agree"],
        "max_fanout": block["max_fanout"],
        "n_points": n,
        "n_image": k,
    }


def build_report() -> dict:
    disc = discriminant()
    points = affine_points()
    x_block = branching(points, lambda pt: pt[0])
    norm_block = branching(points, lambda pt: norm(pt[0]))
    order = {pt: i for i, pt in enumerate(points)}
    random_block = branching(points, lambda pt: order[pt] % 7)
    subset = points[:30]
    id_of = {pt: i for i, pt in enumerate(subset)}

    def identity_label(pt):
        if pt in id_of:
            return ("id", id_of[pt])
        return ("outside", pt[0], pt[1])

    # Infinity is one label, so each singleton pair contributes one value.
    def identity_branching():
        block = branching(subset, identity_label)
        # Re-score sums at infinity as one shared label. branching() omits
        # them. The identity control counts that one label.
        # Implemented by a second pass only for pairs whose sum is infinity:
        # those pairs currently contribute 0, and must contribute 1.
        from ntheory import add

        fibres: dict = {}
        for pt in subset:
            fibres.setdefault(identity_label(pt), []).append(pt)
        image = list(fibres)
        extra = 0
        for s in image:
            for t in image:
                saw_finite = False
                saw_inf = False
                for left in fibres[s]:
                    for right in fibres[t]:
                        if add(left, right) is None:
                            saw_inf = True
                        else:
                            saw_finite = True
                if saw_inf and not saw_finite:
                    extra += 1
        block = dict(block)
        block["b_num"] = block["b_num"] + extra
        block["b_num_swapped"] = block["b_num_swapped"] + extra
        block["loops_agree"] = block["b_num"] == block["b_num_swapped"]
        if extra and block["max_fanout"] == 0:
            block["max_fanout"] = 1
        return block

    ident = identity_branching()
    x_flags = _flags(x_block)
    n_flags = _flags(norm_block)
    r_flags = _flags(random_block)
    i_flags = _flags(ident)
    z = 7  # the basis element z
    norm_hom = in_subfield(norm(z)) and norm(fmul(z, fadd_one(z))) == fmul(norm(z), norm(fadd_one(z)))
    image_values = {norm(pt[0]) for pt in points}
    checks = {
        "discriminant_nonzero": disc != 0,
        "at_least_30_points": len(points) >= 30,
        "norm_lands_in_subfield": all(in_subfield(v) for v in image_values),
        "norm_is_multiplicative_on_z": norm_hom,
        "x_loops_agree": x_flags["loops_agree"],
        "norm_loops_agree": n_flags["loops_agree"],
        "random_loops_agree": r_flags["loops_agree"],
        "identity_loops_agree": i_flags["loops_agree"],
        "x_is_L1_b2": x_flags["l_eq_1"] and x_flags["b_eq_2"],
        "identity_is_L0_b1": i_flags["l_eq_0"] and i_flags["b_eq_1"],
        "random_uses_seven_bins": r_flags["n_image"] == 7,
        "random_b_ge_6": r_flags["b_ge_6"],
        "norm_image_at_most_7": n_flags["n_image"] <= 7,
    }
    passed = all(checks.values())
    if not passed:
        row = "instrument_failure"
    elif not n_flags["l_ge_2"]:
        row = "not_lossy"
    elif n_flags["b_gt_4"]:
        row = "explanation_1"
    elif n_flags["b_le_4"] and n_flags["l_ge_2"]:
        row = "bounded_branching"
    else:
        row = "instrument_failure"
    return {
        "schema": "frob-884337-norm-branching-v1",
        "experiment_id": "EXP-FROB-884337",
        "polynomial": list(POLY),
        "discriminant": disc,
        "affine_point_count": len(points),
        "x": x_flags,
        "norm": n_flags,
        "random_label": r_flags,
        "identity30": i_flags,
        "norm_image_size": n_flags["n_image"],
        "checks": checks,
        "reading_row": row,
        "attack_claimed": False,
        "max_fanout_does_not_choose_row": True,
        "secondary": {"norm_max_fanout": n_flags["max_fanout"]},
    }


def fadd_one(u: int) -> int:
    from ntheory import fadd

    return fadd(u, 1)


def write_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    report = build_report()
    raw = run_dir / "raw-result.json"
    reading = run_dir / "reading.yaml"
    manifest = run_dir / "manifest.yaml"
    raw.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading.write_text(
        yaml.safe_dump(
            {
                "reading_row": report["reading_row"],
                "attack_claimed": False,
                "b_num": report["norm"]["b_num"],
                "b_den": report["norm"]["b_den"],
                "l_ge_2": report["norm"]["l_ge_2"],
                "affine_point_count": report["affine_point_count"],
                "norm_image_size": report["norm_image_size"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    manifest.write_text(
        yaml.safe_dump(
            {
                "experiment_id": "EXP-FROB-884337",
                "schema": report["schema"],
                "reading_row": report["reading_row"],
                "attack_claimed": False,
                "command": "python3 experiments/EXP-FROB-884337/implementation/run.py --run-dir <run_dir>",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
