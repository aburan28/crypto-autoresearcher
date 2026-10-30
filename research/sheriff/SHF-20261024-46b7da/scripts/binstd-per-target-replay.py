#!/usr/bin/env python3
"""Replay archived BINSTD ell=8/9 targets with an exhaustive pair-sum oracle.

This uses the pinned experiment's deterministic target and factor-base generator,
then checks all ordered triples with a separately written EC addition routine.
It checks archived counts; it is not a hardware or timing reproduction.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

PIN = "4647b1d072ffaebbbb85127bdc60343bbd372ec4"
ROOT = "experiments/EXP-BINSTD-8bdf86"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_pinned(checkout: Path, path: str) -> bytes:
    disk = (checkout / path).read_bytes()
    pinned = subprocess.check_output(["git", "show", f"{PIN}:{path}"], cwd=checkout)
    if disk != pinned:
        raise ValueError(f"checkout bytes differ from pinned source: {path}")
    return disk


def make_module(checkout: Path, authority_commit: str):
    path = f"{ROOT}/implementation/run.py"
    source = subprocess.check_output(["git", "show", f"{authority_commit}:{path}"], cwd=checkout)
    gf = f"{ROOT}/implementation/gf2.py"
    gf_bytes = subprocess.check_output(["git", "show", f"{authority_commit}:{gf}"], cwd=checkout)
    with tempfile.TemporaryDirectory(prefix="binstd-authority-") as dirname:
        tmp = Path(dirname)
        (tmp / "run.py").write_bytes(source)
        (tmp / "gf2.py").write_bytes(gf_bytes)
        spec = importlib.util.spec_from_file_location("binstd_authority_replay", tmp / "run.py")
        module = importlib.util.module_from_spec(spec)
        require(spec is not None and spec.loader is not None, "cannot import authority source")
        spec.loader.exec_module(module)
    return module, {path: sha(source), gf: sha(gf_bytes)}


def replay(checkout: Path, tag: str, ell: int) -> dict:
    run_id = {"ell89": "RUN-BINSTD-43abd4", "ell89r1": "RUN-BINSTD-a2a24c"}[tag]
    receipt_path = f"{ROOT}/runs/{run_id}/execution-receipt.json"
    receipt_raw = load_pinned(checkout, receipt_path)
    receipt = json.loads(receipt_raw)
    authority_commit = receipt["authority"]["commit"]
    run, hashes = make_module(checkout, authority_commit)
    hashes[receipt_path] = sha(receipt_raw)
    freeze_path = f"{ROOT}/stage0-{tag}/freeze.json"
    yield_path = f"{ROOT}/stage1-{tag}/yield-matrix.json"
    freeze_raw = load_pinned(checkout, freeze_path)
    yield_raw = load_pinned(checkout, yield_path)
    hashes.update({freeze_path: sha(freeze_raw), yield_path: sha(yield_raw)})
    raw_path = f"{ROOT}/runs/{run_id}/raw-result.json"
    raw_result = load_pinned(checkout, raw_path)
    hashes[raw_path] = sha(raw_result)
    require(hashes[raw_path] == receipt["artifact_sha256"]["raw-result.json"], "raw-result hash mismatch")
    require(sha(yield_raw) == json.loads(raw_result)["result"]["artifact_sha256"]["stage1/yield-matrix.json"], "yield matrix hash mismatch")
    freeze = json.loads(freeze_raw)
    archived = json.loads(yield_raw)
    require(freeze["n_stage1"] == 17 and freeze["target_count"] == 40, "unexpected frozen workload")
    require(freeze["band"] == 1.25 and ell in freeze["ells"], "unexpected frozen band or panel")
    cell = next(c for c in archived["cells"] if c["ell"] == ell)
    seed = freeze["seed"]
    rng = random.Random(seed ^ (17 * 1_000_003) ^ (ell * 97))
    F = run.make_field(17)
    curve = run.Curve(F, A=0, B=1)
    tau_gens = run.build_tau_closed_gens(F, rng, ell)
    open_gens = run.build_open_gens(F, rng, ell)
    if tau_gens is None or open_gens is None:
        raise AssertionError("pinned factor-base sampling failed")
    require(run.is_tau_closed(F, tau_gens) and not run.is_tau_closed(F, open_gens), "factor-base arm mismatch")
    bases = {"tau": run.factor_base_points(curve, tau_gens), "open": run.factor_base_points(curve, open_gens)}
    require(len(bases["tau"]) == cell["fb_tau_size"], "tau factor-base size mismatch")
    require(len(bases["open"]) == cell["fb_open_size"], "open factor-base size mismatch")

    @lru_cache(maxsize=131072)
    def inv(x: int) -> int:
        return F.inv(x)

    def add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x1 or x1 == 0:
                return None
            slope = x1 ^ F.mul(y1, inv(x1))
            x3 = F.mul(slope, slope) ^ slope
            y3 = F.mul(x1, x1) ^ F.mul(slope ^ 1, x3)
        else:
            slope = F.mul(y1 ^ y2, inv(x1 ^ x2))
            x3 = F.mul(slope, slope) ^ slope ^ x1 ^ x2
            y3 = F.mul(slope, x1 ^ x3) ^ x3 ^ y1
        return x3, y3

    def on_curve(P):
        if P is None:
            return True
        x, y = P
        return F.sqr(y) ^ F.mul(x, y) == F.mul(F.sqr(x), x) ^ 1

    pair_sets = {}
    for name, base in bases.items():
        require(all(on_curve(P) for P in base), f"{name} factor base has an off-curve point")
        pairs = {}
        for P in base:
            for Q in base:
                S = add(P, Q)
                require(on_curve(S), "pair-sum point is off curve")
                pairs.setdefault(S, (P, Q))
        pair_sets[name] = pairs

    rows = []
    for index in range(40):
        target = run.random_curve_point(curve, rng)
        require(on_curve(target), "target point is off curve")
        row = {"index": index, "target": list(target)}
        for name in ("tau", "open"):
            pair_set = pair_sets[name]
            witness = None
            for T in bases[name]:
                needed = add(target, (T[0], T[0] ^ T[1]))
                if needed in pair_set:
                    P, Q = pair_set[needed]
                    require(add(add(P, Q), T) == target, "triple witness did not reconstruct target")
                    witness = [list(P), list(Q), list(T)]
                    break
            row[name] = {"hit": witness is not None, "witness": witness}
        rows.append(row)
    observed = {name: sum(row[name]["hit"] for row in rows) for name in bases}
    archived_hits = {"tau": cell["hits_tau"], "open": cell["hits_open"]}

    def check_counts(candidate: dict) -> None:
        if candidate != observed:
            raise ValueError("archived hit counts do not match per-target replay")

    check_counts(archived_hits)
    require(4 * observed["tau"] < 5 * observed["open"], "replayed counts exceed frozen yield band")
    # A deliberately changed observation must fail the same count comparison.
    try:
        check_counts(dict(archived_hits, tau=archived_hits["tau"] + 1))
    except ValueError:
        pass
    else:
        raise AssertionError("tampered observation passed the count checker")
    return {"schema": "binstd.per_target_replay.v1", "pin": PIN,
            "authority_commit": authority_commit, "run_id": run_id, "panel": tag,
            "ell": ell, "source_sha256": hashes, "observed_hits": observed,
            "archived_hits": archived_hits,
            "factor_base_sizes": {k: len(v) for k, v in bases.items()},
            "pair_sum_cardinality": {k: len(v) for k, v in pair_sets.items()},
            "negative_control_rejected": True, "targets": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", type=Path, required=True)
    ap.add_argument("--panel", choices=["ell89", "ell89r1"], required=True)
    ap.add_argument("--ell", type=int, choices=[8, 9], required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    receipt = replay(args.checkout, args.panel, args.ell)
    encoded = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    if args.output.exists():
        if args.output.read_bytes() != encoded:
            raise ValueError(f"frozen replay receipt differs: {args.output}")
    else:
        args.output.write_bytes(encoded)
    print(f"{args.panel}/ell={args.ell}: {receipt['observed_hits']} ({len(receipt['targets'])} targets)")


if __name__ == "__main__":
    main()
