#!/usr/bin/env python3
"""Prepare and independently certify public inputs, never run a solver study.

Writes public curve certificates before drawing private target scalars. Private
labels/seeds stay outside public/. File hashes bind the actual preparation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "public"
PRIVATE = HERE / "private"
WORK = HERE / "work"
MAX_PART = 60 * 1024


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    assert not path.exists(), f"Refuse existing preparation output: {path}"
    path.write_text(json.dumps(value, indent=2) + "\n")


def run(args: list[str], log: Path) -> str:
    result = subprocess.run(args, text=True, capture_output=True)
    log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Preparation command failed: {log}")
    return result.stdout


def prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1))


def add(p: int, a: int, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y + v) % p == 0:
        return None
    slope = ((3*x*x+a)*pow(2*y, -1, p) if left == right
             else (v-y)*pow(u-x, -1, p)) % p
    xx = (slope*slope-x-u) % p
    return xx, (slope*(x-xx)-y) % p


def mul(p: int, a: int, point, k: int):
    total = None
    while k:
        if k & 1:
            total = add(p, a, total, point)
        point = add(p, a, point, point)
        k >>= 1
    return total


def read_tsv(path: Path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, header: list[str], rows: list[dict]):
    assert not path.exists(), path
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    assert path.stat().st_size <= MAX_PART, (path, path.stat().st_size)


def certify_fixtures(fixtures: list[dict]) -> list[dict]:
    excluded = {(int(r["p"]), int(r["a"]), int(r["b"]))
                for r in read_tsv(PUBLIC / "excluded-fixtures.tsv")}
    assert len(excluded) == 32 and len(fixtures) == 24
    seen = set()
    certificates = []
    for row in fixtures:
        p, a, b, x, y, r, n = (int(row[key]) for key in ("p", "a", "b", "Px", "Py", "r", "N"))
        assert prime(p) and prime(r) and 3 < p < 2**19 and 2 < r < 2**18
        assert 0 < a < p and 0 < b < p and (4*a**3+27*b*b) % p
        assert 0 <= x < p and 0 <= y < p and (y*y-x**3-a*x-b) % p == 0
        assert n % r == 0 and math.gcd(n//r, r) == 1
        assert n not in (p, p+1) and r != p
        assert mul(p, a, (x, y), r) is None
        assert (p, a, b) not in excluded | seen
        seen.add((p, a, b))
        if row["stratum"] == "power5":
            assert p % 5 == 1
        independent_n = 1
        for xx in range(p):
            rhs = (xx**3+a*xx+b) % p
            legendre = pow(rhs, (p-1)//2, p)
            assert legendre in (0, 1, p-1)
            independent_n += 1 if rhs == 0 else (2 if legendre == 1 else 0)
        assert independent_n == n, row["id"]
        certificates.append({"id": row["id"], "subgroup_bits": r.bit_length(),
                             "p": p, "r": r, "N": n, "cofactor": n//r,
                             "python_euler_count": independent_n,
                             "python_order_check_passed": True})
    for size in (12, 14, 16, 18):
        for stratum in ("ordinary", "power5"):
            assert sum(int(row["r"]).bit_length() == size and row["stratum"] == stratum
                       for row in fixtures) == 3
    return certificates


def history_parts() -> dict:
    original = WORK / "fixture-history.unsplit.jsonl"
    rows = original.read_bytes().splitlines(keepends=True)
    parts = []
    block = bytearray()
    count = 0
    for line in rows:
        assert len(line) <= MAX_PART
        if block and len(block) + len(line) > MAX_PART:
            path = PUBLIC / f"fixture-history-part-{len(parts):03d}.jsonl"
            path.write_bytes(block)
            parts.append({"path": path.name, "bytes": len(block), "rows": count, "sha256": sha(path)})
            block = bytearray()
            count = 0
        block.extend(line)
        count += 1
    if block:
        path = PUBLIC / f"fixture-history-part-{len(parts):03d}.jsonl"
        path.write_bytes(block)
        parts.append({"path": path.name, "bytes": len(block), "rows": count, "sha256": sha(path)})
    rebuilt = b"".join((PUBLIC / item["path"]).read_bytes() for item in parts)
    assert rebuilt == original.read_bytes()
    manifest = {"logical_stream": "fixture-history.jsonl", "bytes": len(rebuilt),
                "rows": len(rows), "sha256": sha(original), "parts": parts,
                "scope": "All deterministic curve-generator accept/reject outcomes; input preparation only."}
    write_json(PUBLIC / "fixture-history-manifest.json", manifest)
    return manifest


def main():
    assert not (PUBLIC / "fixtures.tsv").exists(), "Refuse existing cohort"
    for directory in (PUBLIC, PRIVATE, WORK):
        directory.mkdir(exist_ok=True)
    executable = WORK / "prepare-cohort"
    compiler = ["g++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Wconversion", "-Werror",
                str(HERE / "src/prepare_cohort.cpp"), "-o", str(executable)]
    run(compiler, WORK / "compile-final.log")
    self_tests = json.loads(run([str(executable), "--self-test"], WORK / "self-test-final.log"))
    prep = json.loads(run([str(executable), "--curves", str(PUBLIC / "fixtures.tsv"),
                          str(WORK / "fixture-history.unsplit.jsonl"),
                          str(PUBLIC / "excluded-fixtures.tsv")], WORK / "curve-preparation.log"))
    fixtures = read_tsv(PUBLIC / "fixtures.tsv")
    certs = certify_fixtures(fixtures)
    history = history_parts()
    source_hashes = {str(path.relative_to(HERE)): sha(path)
                     for path in (HERE / "src/prepare_cohort.cpp", HERE / "src/common.hpp", Path(__file__))}
    certificate = {"kind": "locally_certified_synthetic_solver_inputs", "fixtures": 24,
                   "subgroup_bits": [12, 14, 16, 18], "curves_per_size_stratum": 3,
                   "strata": ["ordinary", "power5"], "curve_seed_hex": "20261025ec0124",
                   "fixture_manifest_sha256": sha(PUBLIC / "fixtures.tsv"),
                   "excluded_manifest_sha256": sha(PUBLIC / "excluded-fixtures.tsv"),
                   "excluded_prior_curves": 32, "excluded_identity": "(p,a,b), stronger than full fixture identity",
                   "source_sha256": source_hashes, "history_sha256": history["sha256"],
                   "preparation_summary": prep, "fixed_development_self_tests": self_tests,
                   "checks": ["prime p/r by independent Python trial division",
                              "C++ complete root-frequency census and Euler census agree",
                              "independent Python Euler census agrees on each accepted curve",
                              "independent Python affine rP=O; nonidentity P and prime r",
                              "nonanomalous ordinary, nonsingular, j not0/1728, coprime cofactor",
                              "no prior32-curve reuse and no duplicate current curve"],
                   "authority": "Local synthetic input certificates; no canonical registry UID or solver-result status claimed.",
                   "per_fixture": certs}
    write_json(PUBLIC / "fixture-certificate.json", certificate)
    # This seal exists before private target scalars are drawn or public Q opened.
    write_json(PUBLIC / "fixture-freeze-before-targets.json",
               {"kind": "prospective_input_preparation_seal", "fixture_manifest_sha256": sha(PUBLIC / "fixtures.tsv"),
                "certificate_sha256": sha(PUBLIC / "fixture-certificate.json"),
                "source_sha256": source_hashes, "private_target_generation_not_yet_invoked": True,
                "not_repository_admission_or_scientific_approval": True})
    run([str(executable), "--targets", str(PUBLIC / "fixtures.tsv"), str(PUBLIC / "public-targets.tsv"),
         str(PRIVATE / "target-truth.tsv"), str(PRIVATE / "target-seeds.json")], WORK / "target-preparation.log")
    targets = read_tsv(PUBLIC / "public-targets.tsv")
    assert len(targets) == 768 and (PUBLIC / "public-targets.tsv").stat().st_size <= MAX_PART
    fixture_map = {row["id"]: row for row in fixtures}
    subsets = []
    target_counts = {key: 0 for key in fixture_map}
    for row in targets:
        fixture = fixture_map[row["fixture_id"]]
        p, a, b, r = (int(fixture[key]) for key in ("p", "a", "b", "r"))
        x, y, infinity = (int(row[key]) for key in ("Qx", "Qy", "Qinf"))
        assert infinity in (0, 1)
        if infinity:
            assert (x, y) == (0, 0)
            point = None
        else:
            assert 0 <= x < p and 0 <= y < p and (y*y-x**3-a*x-b) % p == 0
            point = (x, y)
        assert mul(p, a, point, r) is None
        ordinal = target_counts[row["fixture_id"]]
        target_counts[row["fixture_id"]] += 1
        subsets.append({"fixture_id": row["fixture_id"], "target_id": row["target_id"],
                        "ordinal": ordinal, "subset": "core" if ordinal < 8 else "extension"})
    assert set(target_counts.values()) == {32}
    write_tsv(PUBLIC / "target-subsets.tsv", ["fixture_id", "target_id", "ordinal", "subset"], subsets)
    fixture_header = list(fixtures[0])
    target_header = list(targets[0])
    shards = []
    for index in range(3):
        selected = [row for row in fixtures if row["id"].endswith(f"-{index}")]
        selected_ids = {row["id"] for row in selected}
        selected_targets = [row for row in targets if row["fixture_id"] in selected_ids]
        assert len(selected) == 8 and len(selected_targets) == 256
        fp = PUBLIC / f"fixtures-shard-{index}.tsv"
        tp = PUBLIC / f"public-targets-shard-{index}.tsv"
        write_tsv(fp, fixture_header, selected)
        write_tsv(tp, target_header, selected_targets)
        shards.append({"index": index, "fixtures": len(selected), "targets": len(selected_targets),
                       "fixture_ids": [row["id"] for row in selected],
                       "fixture_path": fp.name, "fixture_sha256": sha(fp),
                       "target_path": tp.name, "target_sha256": sha(tp)})
    assert len({key for shard in shards for key in shard["fixture_ids"]}) == 24
    write_json(PUBLIC / "fixture-shards.json", {"kind": "balanced_disjoint_input_shards", "shards": shards,
               "assignment": "one ordinary and one power5 curve at every subgroup size per shard",
               "union_fixture_manifest_sha256": sha(PUBLIC / "fixtures.tsv"),
               "union_target_manifest_sha256": sha(PUBLIC / "public-targets.tsv"),
               "not_independent_extra_replications": True})
    custody = {"schema": "classical-ecdlp-target-custody/v2", "public_target_count": 768,
               "targets_per_fixture": 32, "core_targets": 192, "extension_targets": 576,
               "subsets": "First8 ordinals per fixture core; remaining24 extension. Prospectively fixed before target generation.",
               "public_manifest_sha256": sha(PUBLIC / "public-targets.tsv"),
               "subset_manifest_sha256": sha(PUBLIC / "target-subsets.tsv"),
               "withheld_truth_sha256": sha(PRIVATE / "target-truth.tsv"),
               "withheld_seed_record_sha256": sha(PRIVATE / "target-seeds.json"),
               "fixture_seal_sha256": sha(PUBLIC / "fixture-freeze-before-targets.json"),
               "generation": "C++mt19937_64 seeded8 OS random_device words; uniform_int_distribution scalars with replacement;32 perfixture",
               "candidate_input": "Only public parameters and Q/target IDs; no scalar labels, private seeds or intermediate traces",
               "separation": "Source-enforced process interface; not OS-isolated confidentiality or formal blindness",
               "independent_public_input_check": "Python affine curve/subgroup membership on all768 public targets; private labels not read by checker",
               "reveal_policy": "Labels/seeds may be archived separately only after candidate outputs sealed, against prior commitments",
               "scientific_solver_measurement_performed": False}
    write_json(PUBLIC / "target-custody.json", custody)
    for path in PUBLIC.rglob("*"):
        if path.is_file():
            assert path.stat().st_size <= MAX_PART, (path, path.stat().st_size)
    summary = {"fixtures": 24, "public_targets": 768, "core_targets": 192, "extension_targets": 576,
               "candidate_curves": history["rows"], "history_parts": len(history["parts"]),
               "p_max": max(int(row["p"]) for row in fixtures), "all_public_files_at_most60KiB": True,
               "fixture_sha256": sha(PUBLIC / "fixtures.tsv"),
               "target_sha256": sha(PUBLIC / "public-targets.tsv"), "scope": "input_preparation_only"}
    write_json(PUBLIC / "preparation-summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
