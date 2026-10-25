"""Reproduce the two frozen BINSTD ell89 Stage-1 packages without editing them.

Use --run for a fresh (roughly 12-minute) replay, or pass both --existing-*
roots to verify already completed isolated replays. Requires local Git history.
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = pathlib.Path("experiments/EXP-BINSTD-8bdf86")
CASES = (
    ("ell89", "RUN-BINSTD-6f1bcc", "RUN-BINSTD-43abd4", "trial-plan-v2.json"),
    ("ell89r1", "RUN-BINSTD-f4d6e3", "RUN-BINSTD-a2a24c", "trial-plan-v3.json"),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def at_commit(commit, relative):
    git_env = os.environ.copy()
    git_env["GIT_NO_LAZY_FETCH"] = "1"
    return subprocess.check_output(
        ["git", "show", f"{commit}:{relative.as_posix()}"], cwd=ROOT, env=git_env
    )


def normalized_raw(path):
    result = read_json(path)["result"]
    result.pop("recorded_at", None)
    return result


def poly_remainder(a, b):
    while a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def poly_multiply(a, b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        b >>= 1
    return value


def poly_gcd(a, b):
    while b:
        a, b = b, poly_remainder(a, b)
    return a


def prime_divisors(n):
    divisors = []
    candidate = 2
    while candidate * candidate <= n:
        if n % candidate == 0:
            divisors.append(candidate)
            while n % candidate == 0:
                n //= candidate
        candidate += 1
    if n > 1:
        divisors.append(n)
    return divisors


def irreducible_over_f2(modulus):
    """Rabin's criterion, implemented separately from the runner's field code."""
    degree = modulus.bit_length() - 1
    x = poly_remainder(2, modulus)
    power = x
    powers = {0: x}
    for i in range(1, degree + 1):
        power = poly_remainder(poly_multiply(power, power), modulus)
        powers[i] = power
    if powers[degree] != x:
        return False
    return all(poly_gcd(powers[degree // q] ^ x, modulus) == 1
               for q in prime_divisors(degree))


def independent_polynomial_controls():
    field_modulus = (1 << 17) | (1 << 3) | 1
    require(irreducible_over_f2(field_modulus),
            "pinned degree-17 field polynomial is reducible")
    factors = (3, 313, 471)
    product = 1
    for factor in factors:
        require(irreducible_over_f2(factor),
                f"x^17-1 factor {factor} is reducible")
        product = poly_multiply(product, factor)
    require(product == (1 << 17) | 1, "x^17-1 factorization does not multiply out")
    degrees = [factor.bit_length() - 1 for factor in factors]
    sums = {0}
    for degree in degrees:
        sums |= {old + degree for old in sums}
    require(sorted(sums) == [0, 1, 8, 9, 16, 17],
            "x^17-1 factor-degree subset sums differ from archived dimensions")
    return {"field_modulus_irreducible": True,
            "x17_minus_one_irreducible_factor_bits": list(factors),
            "factor_degree_subset_sums": sorted(sums)}


def ordered_triple_control(replay, tag):
    """Compare the shortcut with direct triples using separate field arithmetic."""
    path = replay / "implementation/run.py"
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(f"binstd_replay_{tag}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    field = module.make_field(17)
    require(field.mod == ((1 << 17) | (1 << 3) | 1),
            "runner uses an unexpected degree-17 modulus")
    curve = module.Curve(field, A=0, B=1)
    modulus = field.mod

    def multiply(a, b):
        return poly_remainder(poly_multiply(a, b), modulus)

    def inverse(a):
        require(a != 0, "independent field inverse of zero")
        u, v, left, right = a, modulus, 1, 0
        while u != 1:
            require(u != 0, "independent field inverse failed")
            shift = u.bit_length() - v.bit_length()
            if shift < 0:
                u, v = v, u
                left, right = right, left
                shift = -shift
            u ^= v << shift
            left ^= right << shift
        result = poly_remainder(left, modulus)
        require(multiply(a, result) == 1, "independent field inverse is wrong")
        return result

    def on_curve(point):
        if point is None:
            return True
        x, y = point
        return (multiply(y, y) ^ multiply(x, y)) == (multiply(multiply(x, x), x) ^ 1)

    def add(p, q):
        if p is None:
            return q
        if q is None:
            return p
        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if y2 == (x1 ^ y1) or x1 == 0:
                return None
            require(y2 == y1, "independent curve addition got invalid equal-x points")
            slope = x1 ^ multiply(y1, inverse(x1))
            x3 = multiply(slope, slope) ^ slope
            y3 = multiply(x1, x1) ^ multiply(slope ^ 1, x3)
        else:
            slope = multiply(y1 ^ y2, inverse(x1 ^ x2))
            x3 = multiply(slope, slope) ^ slope ^ x1 ^ x2
            y3 = multiply(slope, x1 ^ x3) ^ x3 ^ y1
        return x3, y3

    rng = random.Random(20261022)
    factor_base = []
    for _ in range(4):
        point = module.random_curve_point(curve, rng)
        factor_base.extend((point, curve.neg(point)))
    require(len(set(factor_base)) == 8, "ordered-triple control has duplicate points")
    require(all(on_curve(point) for point in factor_base),
            "ordered-triple factor base has an off-curve point")

    direct_sums = []
    for a, b, c in itertools.product(factor_base, repeat=3):
        pair = add(a, b)
        require(curve.add(a, b) == pair, "runner pair sum differs from independent curve arithmetic")
        target = add(pair, c)
        require(on_curve(target), "independent triple sum is off curve")
        require(curve.add(curve.add(a, b), c) == target,
                "runner triple sum differs from independent curve arithmetic")
        direct_sums.append(target)
    direct_targets = set(direct_sums)

    positive_targets = list(dict.fromkeys(
        target for target in direct_sums if target is not None
    ))[:12]
    require(len(positive_targets) == 12, "ordered-triple control lacks positive targets")
    negative_targets = []
    for _ in range(1000):
        if len(negative_targets) == 12:
            break
        target = module.random_curve_point(curve, rng)
        require(on_curve(target), "sampled negative target is off curve")
        if target not in negative_targets and target not in direct_targets:
            negative_targets.append(target)
    require(len(negative_targets) == 12, "ordered-triple control lacks negative targets")
    for expected, targets in ((True, positive_targets), (False, negative_targets)):
        for target in targets:
            shortcut = module.m3_decomposes(curve, factor_base, target)
            direct = target in direct_targets
            require(direct == expected, "ordered-triple target has unexpected hit status")
            require(shortcut == direct, "pair shortcut disagrees with direct ordered triples")
    return {"factor_base_points": 8, "positive_targets": 12,
            "negative_targets": 12, "independent_triples": 512,
            "runner_arithmetic_matches_independent": True,
            "shortcut_matches_direct": True}


def prepare(tag, commit, env, trial_plan):
    replay_root = pathlib.Path(tempfile.mkdtemp(prefix=f"binstd-replay-{tag}-"))
    target = replay_root / EXP
    implementation = target / "implementation"
    implementation.mkdir(parents=True)
    for name in ("run.py", "gf2.py"):
        relative = EXP / "implementation" / name
        data = at_commit(commit, relative)
        require(digest(data) == env["source_sha256"][relative.as_posix()],
                f"{tag}: source hash drift in {relative}")
        (implementation / name).write_bytes(data)
    historical_plan = at_commit(commit, EXP / trial_plan)
    (target / trial_plan).write_bytes(historical_plan)
    shutil.copytree(ROOT / EXP / f"stage0-{tag}", target / f"stage0-{tag}")
    return replay_root


def run_case(tag, replay_root, trial_plan):
    target = replay_root / EXP
    args = [
        sys.executable, str(target / "implementation/run.py"),
        "--stage", "1", "--ells", "8,9", "--artifact-tag", tag,
        "--trial-plan", str(target / trial_plan),
        "--run-dir", str(target / "runs/replay"),
    ]
    if tag == "ell89r1":
        args.extend(("--seed", "8999122336642658"))
    subprocess.run(args, cwd=replay_root, check=True, timeout=1200)


def check_case(tag, stage0_run, stage1_run, trial_plan, replay_root):
    archived = ROOT / EXP
    env = read_json(archived / "runs" / stage1_run / "environment.json")
    commit = env["commit"]
    source_pins = {}
    for path, expected in sorted(env["source_sha256"].items()):
        actual = digest(at_commit(commit, pathlib.Path(path)))
        require(actual == expected, f"{tag}: source hash drift in {path}: {actual} != {expected}")
        source_pins[path] = actual
    spec = EXP / f"specification-{tag}.yaml"
    require(digest(at_commit(commit, spec)) == env["specification_sha256"],
            f"{tag}: dated specification hash drift")

    stage0 = read_json(archived / "runs" / stage0_run / "raw-result.json")["result"]
    frozen_pins = {}
    for relative, expected in sorted(stage0["artifact_sha256"].items()):
        actual_path = archived / relative.replace("stage0/", f"stage0-{tag}/", 1)
        actual = digest(actual_path.read_bytes())
        require(actual == expected, f"{tag}: freeze artifact hash drift in {relative}")
        frozen_pins[actual_path.relative_to(ROOT).as_posix()] = actual

    if replay_root is None:
        replay_root = prepare(tag, commit, env, trial_plan)
        run_case(tag, replay_root, trial_plan)
    replay = replay_root / EXP
    for name in ("run.py", "gf2.py"):
        relative = EXP / "implementation" / name
        require(digest((replay / "implementation" / name).read_bytes()) == source_pins[relative.as_posix()],
                f"{tag}: extracted replay source drift in {name}")
    outputs = {}
    for relative in (
        f"stage1-{tag}/yield-matrix.json",
        f"stage1-{tag}/admissible-phi-dims.json",
        f"RESULTS-{tag}.md",
    ):
        expected = (archived / relative).read_bytes()
        observed = (replay / relative).read_bytes()
        require(observed == expected,
                f"{tag}: replay output drift in {relative}: {digest(observed)} != {digest(expected)}")
        outputs[(EXP / relative).as_posix()] = digest(expected)
    require(normalized_raw(replay / "runs/replay/raw-result.json") == normalized_raw(
        archived / "runs" / stage1_run / "raw-result.json"),
        f"{tag}: raw result differs beyond recorded_at")
    controls = independent_polynomial_controls()
    controls["ordered_triples"] = ordered_triple_control(replay, tag)
    matrix = read_json(archived / f"stage1-{tag}/yield-matrix.json")
    require(matrix["outcome"] == "E-TAU-NOT-RICHER", f"{tag}: unexpected outcome")
    require(len(matrix["cells"]) == 2, f"{tag}: expected two cells")
    cells = []
    for cell in matrix["cells"]:
        require(cell["hits_open"] == 40 and cell["target_count"] == 40,
                f"{tag}: expected 40 targets and 40 open hits")
        require(cell["hits_tau"] / cell["hits_open"] == cell["ratio_tau_over_open"],
                f"{tag}: ratio does not match hits")
        require(cell["ratio_tau_over_open"] < matrix["band"] == 1.25,
                f"{tag}: ratio does not fail frozen band")
        cells.append({k: cell[k] for k in ("ell", "hits_tau", "hits_open", "ratio_tau_over_open", "cell_label")})
    return {
        "tag": tag, "stage0_run": stage0_run, "stage1_run": stage1_run,
        "commit": commit, "source_sha256": source_pins,
        "specification_sha256": env["specification_sha256"],
        "stage0_sha256": frozen_pins, "output_sha256": outputs,
        "raw_result_equal_except_recorded_at": True,
        "controls": controls,
        "seed": matrix.get("seed", read_json(archived / f"stage0-{tag}/freeze.json")["seed"]),
        "cells": cells,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="perform both isolated full replays")
    parser.add_argument("--existing-ell89", type=pathlib.Path)
    parser.add_argument("--existing-ell89r1", type=pathlib.Path)
    parser.add_argument("--receipt", type=pathlib.Path)
    args = parser.parse_args()
    existing = (args.existing_ell89, args.existing_ell89r1)
    if args.run == any(path is not None for path in existing) or (
        not args.run and not all(path is not None for path in existing)
    ):
        parser.error("choose --run or both --existing-ell89 and --existing-ell89r1")
    cases = [
        check_case(*case, None if args.run else existing[i])
        for i, case in enumerate(CASES)
    ]
    receipt = {
        "schema": "binstd-ell89-isolated-replay-v1",
        "status": "pass", "boundary": "same-source toy replay with bounded independent EC controls; no full-panel oracle or attack claim",
        "python": sys.version.split()[0], "cases": cases,
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
