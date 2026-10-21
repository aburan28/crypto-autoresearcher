"""Independent replay of one bounded k11 solver stage's retained raw outputs.

This checker reads serialized formulas and solver stdout rather than trusting
the runner's SAT, point, or censoring summaries. It implements its own GF(2^61)
and elliptic-curve arithmetic for full-point certificates. A solver assertion
of UNSAT remains unproved and is never promoted to an absence certificate.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
import tarfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = "EXP-ICPERF-018b0c"
HERE = ROOT / "experiments" / EXPERIMENT
FIELD_MASK = (1 << 61) - 1
REDUCTION = (1 << 5) | (1 << 2) | (1 << 1) | 1
SEED = 20261017
LIMITS = {"memory_bytes": 8 * (1 << 30), "max_models": 64, "seed": SEED, "threads": 1}


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_bytes())


def check_call_bundle(run_dir: Path, result: dict) -> int:
    """Independently bind the raw call tree, fixed bundle, and run summary."""
    manifest_path = run_dir / "calls-manifest.json"
    bundle_path = run_dir / "calls.tar.gz"
    assert sha_file(manifest_path) == result["calls_manifest_sha256"]
    manifest = read(manifest_path)
    assert manifest["schema"] == "icperf-k11-call-tree-v1"
    assert manifest["bundle_path"] == bundle_path.name
    assert bundle_path.stat().st_size == manifest["bundle_size_bytes"]
    assert sha_file(bundle_path) == manifest["bundle_sha256"] == result["calls_bundle_sha256"]
    expected = manifest["files"]
    names = [row["path"] for row in expected]
    assert names == sorted(set(names))
    assert all(name.startswith("calls/") and
               all(part not in ("", ".", "..") for part in name.split("/"))
               for name in names)
    calls = run_dir / "calls"
    assert calls.is_dir()
    assert not any(path.is_symlink() for path in calls.rglob("*"))
    actual = sorted(path.relative_to(run_dir).as_posix()
                    for path in calls.rglob("*") if path.is_file())
    assert actual == names
    by_name = {row["path"]: row for row in expected}
    for row in expected:
        path = run_dir / row["path"]
        assert path.stat().st_size == row["size_bytes"]
        assert sha_file(path) == row["sha256"]
    seen = []
    with tarfile.open(bundle_path, mode="r:gz") as archive:
        for member in archive:
            assert member.isfile() and member.name in by_name
            row = by_name[member.name]
            assert member.name not in seen and member.size == row["size_bytes"]
            source = archive.extractfile(member)
            assert source is not None
            digest = hashlib.sha256()
            for chunk in iter(lambda: source.read(1 << 20), b""):
                digest.update(chunk)
            assert digest.hexdigest() == row["sha256"]
            seen.append(member.name)
    assert seen == names
    return len(names)


def gf_mul(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 61):
            a = (a & FIELD_MASK) ^ REDUCTION
    return result


def gf_square(a: int) -> int:
    return gf_mul(a, a)


def gf_pow(a: int, exponent: int) -> int:
    result = 1
    while exponent:
        if exponent & 1:
            result = gf_mul(result, a)
        a = gf_square(a)
        exponent >>= 1
    return result


def gf_inv(a: int) -> int:
    assert a != 0
    return gf_pow(a, (1 << 61) - 2)


def phi3(a: int, b: int, c: int, gamma: int) -> int:
    def q(t: int) -> int:
        return gf_square(t) ^ t
    return gf_mul(gf_mul(q(a), q(b)), q(c)) ^ gf_mul(gamma, gf_square(a ^ b ^ c))


def point_neg(p: tuple[int, int]) -> tuple[int, int]:
    return p[0], p[0] ^ p[1]


def on_curve(p: tuple[int, int] | None, b: int) -> bool:
    if p is None:
        return True
    x, y = p
    return gf_square(y) ^ gf_mul(x, y) == gf_mul(gf_square(x), x) ^ b


def point_add(p: tuple[int, int] | None, q: tuple[int, int] | None, b: int):
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if y1 != y2 or x1 == 0:
            assert y1 ^ y2 == x1 or (x1 == 0 and y1 == y2)
            return None
        slope = x1 ^ gf_mul(y1, gf_inv(x1))
        x3 = gf_square(slope) ^ slope
        y3 = gf_square(x1) ^ gf_mul(slope ^ 1, x3)
    else:
        slope = gf_mul(y1 ^ y2, gf_inv(x1 ^ x2))
        x3 = gf_square(slope) ^ slope ^ x1 ^ x2
        y3 = gf_mul(slope, x1 ^ x3) ^ x3 ^ y1
    answer = (x3, y3)
    assert on_curve(answer, b)
    return answer


def point_scale(k: int, p: tuple[int, int] | None, b: int):
    result = None
    while k:
        if k & 1:
            result = point_add(result, p, b)
        p = point_add(p, p, b)
        k >>= 1
    return result


def lift_phi(t: int, gamma: int, b: int) -> tuple[int, int] | None:
    if t == 0:
        return None
    x = gf_mul(gamma, 1 ^ gf_inv(t))
    if x in (0, gamma):
        return None
    beta = x ^ gf_mul(b, gf_inv(gf_square(x)))
    trace = 0
    term = beta
    for _ in range(61):
        trace ^= term
        term = gf_square(term)
    if trace:
        return None
    halftrace = 0
    term = beta
    for _ in range(31):
        halftrace ^= term
        term = gf_square(gf_square(term))
    p = (x, gf_mul(x, halftrace))
    assert on_curve(p, b)
    return p


def exact_point_rows(assignment: int, base: dict, chain: dict,
                     arm: dict) -> list[dict]:
    width = arm["base_dimension"]
    assert width == 11 and arm["primary_variables"] == 454
    mask = (1 << width) - 1
    ts = [((assignment >> (j * width)) & mask) ^ arm["offset"] for j in range(8)]
    us = [(assignment >> (8 * width + j * 61)) & FIELD_MASK for j in range(6)]
    scan, = [row for row in base["candidate_scans"] if row["offset"] == arm["offset"]]
    if any(t not in set(scan["accepted_phi"]) for t in ts):
        return []
    gamma, b = chain["gamma"], chain["curve"]["b_polynomial_bits"]
    triples = [(ts[0], ts[1], us[0])]
    triples.extend((us[j - 1], ts[j + 1], us[j]) for j in range(1, 6))
    triples.append((us[5], ts[7], arm["target_coordinate"]))
    if any(phi3(*triple, gamma) != 0 for triple in triples):
        return []
    lifted = [lift_phi(t, gamma, b) for t in ts]
    if any(p is None for p in lifted):
        return []
    representatives = scan["selected_representatives"]
    canonical = {row[0]: (j, point_scale(4, tuple(row[1:]), b))
                 for j, row in enumerate(representatives)}
    assert len(canonical) == len(representatives)
    target = tuple(chain["target_channels"][chain["selected_channel"]])
    subgroup = tuple(chain["subgroup_target"])
    assert point_scale(4, target, b) == subgroup
    rows = []
    for sign_mask in range(256):
        points = [point_neg(p) if sign_mask & (1 << j) else p
                  for j, p in enumerate(lifted)]
        total = None
        for p in points:
            total = point_add(total, p, b)
        if total != target:
            continue
        coefficients = {}
        for t, p in zip(ts, points):
            index, canonical_point = canonical[t & ~1]
            image = point_scale(4, p, b)
            assert image in (canonical_point, point_neg(canonical_point))
            coefficients[index] = coefficients.get(index, 0) + (1 if image == canonical_point else -1)
        row = [[index, coefficient] for index, coefficient in sorted(coefficients.items()) if coefficient]
        reconstructed = None
        for index, coefficient in row:
            p = point_scale(abs(coefficient), point_scale(4, tuple(representatives[index][1:]), b), b)
            reconstructed = point_add(reconstructed, point_neg(p) if coefficient < 0 else p, b)
        assert reconstructed == subgroup
        rows.append({"sign_mask": sign_mask, "points": [list(p) for p in points],
                     "projected_row": row})
    return rows


def parse_xcnf(blob: bytes) -> tuple[int, list[list[int]], list[tuple[list[int], bool]]]:
    lines = blob.decode("ascii").splitlines()
    header = lines.pop(0).split()
    assert len(header) == 4 and header[:2] == ["p", "cnf"]
    nvars, nconstraints = map(int, header[2:])
    clauses, xors = [], []
    saw_xor = False
    for line in lines:
        assert line.endswith(" 0")
        if line.startswith("x"):
            saw_xor = True
            tokens = [int(x) for x in line[1:].split()]
            assert tokens[-1] == 0 and 2 <= len(tokens) - 1 <= 3
            xors.append(([abs(x) for x in tokens[:-1]], tokens[0] > 0))
        else:
            assert not saw_xor
            tokens = [int(x) for x in line.split()]
            assert tokens[-1] == 0
            clauses.append(tokens[:-1])
    assert len(clauses) + len(xors) == nconstraints
    assert all(1 <= abs(x) <= nvars for row in clauses for x in row)
    assert all(1 <= x <= nvars for row, _ in xors for x in row)
    return nvars, clauses, xors


def parse_sat_model(stdout: str, nvars: int) -> list[bool]:
    values = {}
    statuses = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("s "):
            statuses.append(line)
        elif line.startswith("v "):
            for token in line[2:].split():
                literal = int(token)
                if literal:
                    var = abs(literal)
                    assert 1 <= var <= nvars
                    assert var not in values or values[var] == (literal > 0)
                    values[var] = literal > 0
    assert statuses == ["s SATISFIABLE"] and len(values) == nvars
    return [False] + [values[j] for j in range(1, nvars + 1)]


def verify_xcnf(values: list[bool], clauses: list[list[int]],
                xors: list[tuple[list[int], bool]]) -> None:
    assert all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)
    assert all(bool(sum(values[var] for var in row) & 1) == rhs for row, rhs in xors)


def add_blocks(raw: bytes, assignments: list[int]) -> bytes:
    lines = raw.splitlines(keepends=True)
    header = lines[0].decode("ascii").split()
    nvars, constraints = map(int, header[2:])
    assert header[:2] == ["p", "cnf"] and constraints == len(lines) - 1
    split = next((i for i, line in enumerate(lines[1:], 1) if line.startswith(b"x")), len(lines))
    blocks = []
    for assignment in assignments:
        assert 0 <= assignment < (1 << 454)
        literals = [(-j if (assignment >> (j - 1)) & 1 else j) for j in range(1, 455)]
        blocks.append((" ".join(map(str, literals)) + " 0\n").encode())
    return (f"p cnf {nvars} {constraints + len(blocks)}\n".encode()
            + b"".join(lines[1:split]) + b"".join(blocks) + b"".join(lines[split:]))


def call_input(stage: str, label: str, index: int | None, channel: int,
               positive: dict, formulas: dict, targets: dict, chain: dict):
    if stage == "positive":
        control = positive["controls"][label]
        fixture = control["source_row"]["synthetic_control"]
        path = ROOT / control["formula_path"]
        raw_sha, packed_sha = control["formula_raw_sha256"], control["formula_gzip_sha256"]
        arm = {"kind": "torsion_phi", "base_dimension": 11, "offset": 4096,
               "primary_variables": 454, "target_coordinate": fixture["synthetic_target_phi"]}
        bound = dict(chain, selected_channel=0,
                     target_channels=[fixture["synthetic_raw_target"]] * 4,
                     subgroup_target=fixture["synthetic_projected_target"])
    else:
        arm, = [a for a in formulas["arms"] if a["target_index"] == index
                and a["base_kind"] == label and a["channel"] == channel]
        target = targets["admitted"][index]
        path = ROOT / arm["gzip_path"]
        raw_sha, packed_sha = arm["raw_xcnf_sha256"], arm["gzip_sha256"]
        bound = dict(chain, selected_channel=channel,
                     target_channels=target["raw_channels"],
                     subgroup_target=target["subgroup_point"])
    packed = path.read_bytes()
    assert sha(packed) == packed_sha
    raw = gzip.decompress(packed)
    assert sha(raw) == raw_sha
    return raw, arm, bound


def check_call(run_dir: Path, row: dict, stage: str, base: dict, arm: dict,
               bound: dict, raw: bytes) -> list[tuple]:
    assert row["status"] not in ("host_admission_stop", "panel_wall_censored",
                                 "infrastructure_or_input_failure")
    call_dir = run_dir / row["call_dir"]
    assert call_dir.resolve().is_relative_to((run_dir / "calls").resolve())
    summary_blob = (call_dir / "summary.json").read_bytes()
    assert sha(summary_blob) == row["summary_sha256"]
    summary = json.loads(summary_blob)
    assert summary["status"] == row["status"] and summary["input_sha256"] == sha(raw)
    assert summary["base_kind"] == row["base_kind"]
    assert summary["target_index"] == row.get("target_index")
    assert summary["channel"] == row.get("channel", 0)
    assert summary["host"] == row["host"]
    assert len(summary["host"]["load_average_before"]) == 3
    assert all(math.isfinite(x) and x >= 0 for x in summary["host"]["load_average_before"])
    assert summary["limits"]["wall_seconds"] <= 300
    assert all(summary["limits"][k] == v for k, v in LIMITS.items())
    assert 0 <= len(summary["attempts"]) <= 64
    assert len(summary["attempts"]) == row["attempts"]
    assert math.isfinite(summary["total_wall_seconds"]) and summary["total_wall_seconds"] >= 0
    assert summary["total_wall_seconds"] == row["total_wall_seconds"]
    assert 0 <= summary["point_filter_wall_seconds"] <= summary["call_wrapper_wall_seconds"]
    assert 0 <= summary["point_filter_cpu_seconds"]
    assert summary["total_wall_seconds"] <= summary["call_wrapper_wall_seconds"]
    blocked = []
    certified_rows = []
    for j, attempt in enumerate(summary["attempts"], 1):
        attempt_dir = call_dir / f"attempt-{j:04d}"
        assert read(attempt_dir / "attempt.json") == attempt
        exact_input = add_blocks(raw, blocked)
        assert (attempt_dir / "input.xcnf").read_bytes() == exact_input
        assert attempt["input_sha256"] == sha(exact_input)
        assert attempt["blocked_primary"] == len(blocked)
        assert attempt["command"][-1] == str(attempt_dir / "input.xcnf")
        assert attempt["command"][0] == "/opt/homebrew/bin/cryptominisat5"
        assert attempt["command"][1:9] == ["--verb", "0", "--threads", "1", "--maxsol", "1", "--random", str(SEED)]
        assert attempt["command"][9] == "--maxtime" and 1 <= int(attempt["command"][10]) <= 300
        if attempt["outcome"] == "solver_launch_failure":
            assert "process" not in attempt
            continue
        stdout_blob = (attempt_dir / "stdout.txt").read_bytes()
        stderr_blob = (attempt_dir / "stderr.txt").read_bytes()
        process = attempt["process"]
        assert sha(stdout_blob) == process["stdout_sha256"]
        assert sha(stderr_blob) == process["stderr_sha256"]
        stdout = stdout_blob.decode(errors="replace")
        statuses = [line.strip() for line in stdout.splitlines() if line.startswith("s ")]
        assert attempt["solver_status_lines"] == statuses
        if process["wall_timeout"]:
            assert attempt["outcome"] == "wall_censored"
        elif process["rss_watchdog_tripped"]:
            assert attempt["outcome"] == "memory_censored"
        elif process["returncode"] == 20 and statuses == ["s UNSATISFIABLE"]:
            assert attempt["outcome"] == "solver_reported_exhausted_unvalidated"
        elif process["returncode"] == 0 and statuses in (["s UNKNOWN"], ["s INDETERMINATE"]):
            assert attempt["outcome"] == "solver_unknown_censored"
        elif process["returncode"] != 10 or statuses != ["s SATISFIABLE"]:
            assert attempt["outcome"] == "solver_failure_or_unclassified"
        else:
            nvars, clauses, xors = parse_xcnf(exact_input)
            values = parse_sat_model(stdout, nvars)
            verify_xcnf(values, clauses, xors)
            assignment = sum(1 << (k - 1) for k in range(1, 455) if values[k])
            assert assignment not in blocked
            assert attempt["primary_assignment_hex"] == hex(assignment)
            assert attempt["full_xcnf_model_verified"] is True
            cert_blob = (attempt_dir / "certificate.json").read_bytes()
            assert sha(cert_blob) == attempt["certificate_sha256"]
            cert = json.loads(cert_blob)
            assert cert["assignment_hex"] == hex(assignment)
            assert cert["schema"] == "icperf-k11-full-point-check-v1"
            assert cert["experiment_id"] == EXPERIMENT
            assert cert["base_kind"] == row["base_kind"]
            assert cert["target_index"] == row.get("target_index")
            assert cert["channel"] == row.get("channel", 0)
            exact_rows = exact_point_rows(assignment, base, bound, arm)
            assert cert["result"].get("full_point_certificates", []) == exact_rows
            assert cert["result"].get("certified", False) == bool(exact_rows)
            if exact_rows:
                assert attempt["outcome"] in ("point_relation_certified",
                                              "point_relation_certified_after_wall_cap")
                certified_rows.extend((tuple(map(tuple, c["projected_row"])) for c in exact_rows))
            else:
                assert attempt["outcome"] in ("rejected_primary", "wall_censored")
                blocked.append(assignment)
    assert summary["blocked_primary_count"] == len(blocked)
    if summary["attempts"]:
        last_outcome = summary["attempts"][-1]["outcome"]
        if last_outcome == "rejected_primary":
            assert summary["status"] == ("model_cap_censored" if len(summary["attempts"]) == 64
                                         else "wall_censored")
        else:
            assert summary["status"] == last_outcome
    else:
        assert summary["status"] == "wall_censored"
    return certified_rows


def main() -> None:
    if sys.flags.optimize:
        raise ValueError("optimized Python disables scientific validation assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    result = read(run_dir / "raw-result.json")
    launch = read(run_dir / "launch.json")
    environment = read(run_dir / "environment.json")
    spec = yaml.safe_load((HERE / "specification.yaml").read_text())["experiment"]
    plan_blob = (ROOT / spec["input_bindings"]["trial_plan"]).read_bytes()
    plan = json.loads(plan_blob)
    assert result["experiment_id"] == EXPERIMENT
    assert result["step"] == launch["trial_id"]
    assert result["plan_sha256"] == launch["plan_sha256"] == sha(plan_blob)
    assert result["source_commit"] == environment["commit"]
    assert math.isfinite(result["total_wall_seconds"]) and result["total_wall_seconds"] >= 0
    assert plan["specification_sha256"] == sha((HERE / "specification.yaml").read_bytes())
    assert sha(Path(__file__).read_bytes()) == plan["source_sha256"][str(Path(__file__).relative_to(ROOT))]
    for name in ("target_manifest", "positive_manifest", "formula_manifest", "historical_chain",
                 "weighted_base", "local_random_base", "solver_binary"):
        binding = spec["input_bindings"][name]
        bound_path = Path(binding["path"])
        if not bound_path.is_absolute():
            bound_path = ROOT / bound_path
        assert sha(bound_path.read_bytes()) == binding["sha256"]
    targets = read(HERE / "inputs/target_manifest.json")
    positive = read(HERE / "inputs/positive_manifest.json")
    formulas = read(HERE / "inputs/formula_manifest.json")
    chain = read(ROOT / "research/icperf_binary_torsion_m8_chain_20261017/chain.json")
    bases = {label: read(ROOT / f"research/icperf_binary_torsion_k11_{name}_20261017/base.json")
             for label, name in (("weighted", "weighted"), ("local_random", "local_control"))}
    run_manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    assert run_manifest["id"] == launch["run_id"]
    assert run_manifest["experiment_id"] == EXPERIMENT
    assert run_manifest["code"]["commit"] == environment["commit"]
    assert run_manifest["code"]["command"] == launch["argv"]
    assert run_manifest["environment"]["solver_sha256"] == spec["input_bindings"]["solver_binary"]["sha256"]
    assert run_manifest["result"]["outcome"] == result["status"]
    assert run_manifest["result"]["certificate"] == {"kind": "none", "verified": False}
    bundled_files = check_call_bundle(run_dir, result)
    bundle_cost = result["calls_bundle"]
    assert bundle_cost["raw_file_count"] == bundled_files
    assert bundle_cost["tar_bytes"] == (run_dir / "calls.tar.gz").stat().st_size
    assert bundle_cost["manifest_bytes"] == (run_dir / "calls-manifest.json").stat().st_size
    assert all(math.isfinite(bundle_cost[key]) and bundle_cost[key] >= 0
               for key in ("wall_seconds", "cpu_seconds"))
    assert bundle_cost["wall_seconds"] <= result["total_wall_seconds"]
    all_rows = set()
    checked = 0
    for ordinal, row in enumerate(result["calls"]):
        if result["step"] == "positive":
            assert ordinal < 2
            label = ("weighted", "local_random")[ordinal]
            index, channel = None, 0
        else:
            if row["status"] == "gated_by_positive_controls":
                assert ordinal == 0 and len(result["calls"]) == 1
                break
            index, within = divmod(ordinal, 8)
            base_slot, channel = divmod(within, 4)
            label = (("weighted", "local_random") if index % 2 == 0
                     else ("local_random", "weighted"))[base_slot]
        assert row["base_kind"] == label
        assert math.isfinite(row["input_decompression_wall_seconds"])
        assert row["input_decompression_wall_seconds"] >= 0
        if result["step"] == "natural":
            assert row["target_index"] == index and row["channel"] == channel
        if row["status"] in ("host_admission_stop", "panel_wall_censored",
                             "infrastructure_or_input_failure"):
            assert ordinal == len(result["calls"]) - 1 or result["step"] == "positive"
            continue
        raw, arm, bound = call_input(result["step"], label, index, channel,
                                     positive, formulas, targets, chain)
        exact_rows = check_call(run_dir, row, result["step"], bases[label], arm, bound, raw)
        for projected in exact_rows:
            all_rows.add((label, index, projected))
        checked += 1
    output = {"schema": "icperf-k11-independent-run-check-v1",
              "scope": "replayed raw XCNF models and exact points; unproved solver UNSAT remains unvalidated",
              "run_id": launch["run_id"], "stage": result["step"],
              "raw_result_sha256": sha((run_dir / "raw-result.json").read_bytes()),
              "source_sha256": sha(Path(__file__).read_bytes()),
              "raw_call_files_bound": bundled_files,
              "bundle_wall_seconds_charged": bundle_cost["wall_seconds"],
              "bundle_cpu_seconds_charged": bundle_cost["cpu_seconds"],
              "calls_manifest_sha256": result["calls_manifest_sha256"],
              "calls_bundle_sha256": result["calls_bundle_sha256"],
              "calls_checked_from_raw": checked,
              "distinct_projected_rows": len(all_rows),
              "validated": True}
    with (run_dir / "independent_check.json").open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"calls_checked_from_raw": checked,
                      "distinct_projected_rows": len(all_rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
