#!/usr/bin/env python3
"""Independently classify the merged six-stream prime-order census.

The census point counts are imported observations. This checker binds their
bytes, regenerates the candidate-index set from our separate seed file,
retests primality and both acceptance profiles, and compares overlapping exact
orders and the independently assessed eleven skipped curves.
"""

import collections
import datetime as dt
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CENSUS = REPO / "research" / "nist_seed_provenance_20261016" / "census"
RAW = ROOT / "raw"
STREAMS = {
    "prime239v3": 863711343,
    "prime192v2": 863966734,
    "P-521": 871002724,
    "P-256": 871696354,
    "P-384": 872952608,
    "P-224": 891607927,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def family_eligible(n, p, is_prime):
    return bool(is_prime and n > 2**160 and n > 4 * __import__("math").isqrt(p)
                and n != p and all(pow(p, k, n) != 1 for k in range(1, 21)))


def main():
    output = RAW / "full_census_crosscheck_v4.json"
    gp_input = RAW / "full_census_primality_v4.gp"
    gp_stdout = RAW / "full_census_primality_v4.stdout"
    gp_stderr = RAW / "full_census_primality_v4.stderr"
    for path in (output, gp_input, gp_stdout, gp_stderr):
        if path.exists():
            raise FileExistsError(path)
    started = dt.datetime.now(dt.timezone.utc)
    tic = time.monotonic()
    targets_path = ROOT / "targets.json"
    targets = json.loads(targets_path.read_text())
    by_name = {x["name"]: x for x in targets}
    by_run = {run: [] for run in STREAMS.values()}
    for item in targets:
        if item["kind"] == "prime":
            by_run[item["unix_time"]].append(item)
    candidates_path = RAW / "candidates.jsonl"
    candidates = collections.defaultdict(dict)
    with candidates_path.open() as source:
        for line in source:
            row = json.loads(line)
            if row["target"] in STREAMS:
                candidates[row["target"]][row["index"]] = row

    inputs = {str(targets_path.relative_to(REPO)): sha(targets_path),
              str(candidates_path.relative_to(REPO)): sha(candidates_path)}
    orders = {}
    gp_lines = ["default(parisizemax, 1000000000);\n"]
    requests = []
    for rep, run in STREAMS.items():
        p = int(by_name[rep]["p"])
        path = CENSUS / f"orders_{run}.txt"
        inputs[str(path.relative_to(REPO))] = sha(path)
        rows = {}
        with path.open() as source:
            for line in source:
                i, n, nt = map(int, line.split())
                require(i not in rows and i in candidates[rep], f"duplicate or unknown {rep}/{i}")
                rows[i] = (n, nt)
                if n or nt:
                    gp_lines.append(f'print("{run} {i} ", isprime({n}), " ", isprime({nt}));\n')
                    requests.append((run, i))
        expected = {i for i, row in candidates[rep].items()
                    if row["variants"]["nist_fips_186_2"]["b_roots"]}
        require(set(rows) == expected, f"seeded-coefficient set differs for {rep}")
        require(max(rows) <= max(t["candidate_index"] for t in by_run[run]),
                f"out-of-window index in {rep}")
        orders[rep] = rows
    gp_lines.append("quit;\n")
    gp_input.write_text("".join(gp_lines))
    gp_version = subprocess.run(["gp", "--version-short"], text=True,
                                capture_output=True, check=True).stdout.strip()
    with gp_input.open() as source:
        completed = subprocess.run(["gp", "-q", "-f"], stdin=source,
                                   text=True, capture_output=True)
    gp_stdout.write_text(completed.stdout)
    gp_stderr.write_text(completed.stderr)
    require(completed.returncode == 0, f"GP returned {completed.returncode}")
    prime = {}
    for line in completed.stdout.splitlines():
        run, i, n_prime, nt_prime = map(int, line.split())
        key = (run, i)
        require(key not in prime, f"duplicate GP result {key}")
        require(n_prime in (0, 1) and nt_prime in (0, 1), f"bad GP result {key}")
        prime[key] = (bool(n_prime), bool(nt_prime))
    require(set(prime) == set(requests), "GP result coverage differs")

    source_summary_path = CENSUS / "summary.json"
    inputs[str(source_summary_path.relative_to(REPO))] = sha(source_summary_path)
    expected_summary = {int(row["run"].split("(")[1].split(")")[0]): row
                        for row in json.loads(source_summary_path.read_text())}
    results = {}
    for rep, run in STREAMS.items():
        p = int(by_name[rep]["p"])
        accepted, long_order, twist_only = [], [], []
        root_alternative, family = [], []
        both_prime, other_reject = [], []
        for i, (n, nt) in sorted(orders[rep].items()):
            pn, pt = prime.get((run, i), (False, False))
            if pn and pt:
                both_prime.append(i)
            if pn:
                if n.bit_length() > p.bit_length():
                    long_order.append(i)
                elif n != p and all(pow(p, k, n) != 1 for k in range(1, 1024)):
                    accepted.append(i)
                else:
                    other_reject.append(i)
            elif pt:
                twist_only.append(i)
            canonical_ok = family_eligible(n, p, pn)
            alternate_ok = p % 4 == 3 and family_eligible(nt, p, pt)
            if canonical_ok or alternate_ok:
                family.append(i)
                if alternate_ok and not canonical_ok:
                    root_alternative.append(i)
        require(not other_reject, f"unclassified prime orders for {rep}")
        expected = expected_summary[run]
        require(accepted == expected["accepted"] and
                long_order == expected["n_longer_than_p"] and
                twist_only == expected["only_twist_prime"] and
                len(orders[rep]) == expected["candidates"],
                f"published classifier disagreement for {rep}")
        published = sorted(t["candidate_index"] for t in by_run[run])
        require(set(published) <= set(accepted), f"published anchor filtered in {rep}")
        results[rep] = {
            "run": run, "p_bits": p.bit_length(),
            "stream_blocks": max(published), "seeded_coefficients": len(orders[rep]),
            "published": published,
            "screen_accepted": accepted,
            "screen_skipped": [i for i in accepted if i not in published],
            "screen_rejected_order_too_wide": long_order,
            "only_quadratic_twist_prime": twist_only,
            "both_curve_and_twist_prime": both_prime,
            "seeded_opposite_root_only_prime": root_alternative,
            "broad_family_both_seeded_roots": family,
            "broad_family_unpublished": [i for i in family if i not in published],
        }

    # Compare all candidate orders independently assessed in the other project.
    assessed_path = REPO / "research" / "nist_seed_skipped_curves_20261016" / "assessed.json"
    inputs[str(assessed_path.relative_to(REPO))] = sha(assessed_path)
    assessed = json.loads(assessed_path.read_text())["candidate_rows"]
    assessed_keys = set()
    for item in assessed:
        run, i = item["timestamp"], item["seed_ordinal_one_based"]
        rep = next(rep for rep, value in STREAMS.items() if value == run)
        n0, _ = orders[rep][i]
        require(n0 == int(item["n_hex"], 16), f"independent skipped order differs: {run}/{i}")
        require(candidates[rep][i]["seed"].lower() == item["seed_hex"].lower(),
                f"independent skipped seed differs: {run}/{i}")
        assessed_keys.add((run, i))
    skipped_keys = {(x["run"], i) for x in results.values() for i in x["screen_skipped"]}
    require(assessed_keys == skipped_keys, "independent eleven-candidate assessment differs")
    for run, items in by_run.items():
        rep = next(rep for rep, value in STREAMS.items() if value == run)
        for target in items:
            i = target["candidate_index"]
            require(candidates[rep][i]["seed"].lower() == target["published_seed"].lower(),
                    f"published seed differs: {target['name']}")
            require(orders[rep][i][0] == int(target["published_subgroup_order"]),
                    f"published order differs: {target['name']}")

    # Compare the prior frozen prefix, preserving the stopped campaign's scope.
    retry_path = RAW / "family_campaign" / "retry_plan.json"
    inputs[str(retry_path.relative_to(REPO))] = sha(retry_path)
    retry = json.loads(retry_path.read_text())
    stop_path = RAW / "family_campaign" / "campaign_stop.json"
    inputs[str(stop_path.relative_to(REPO))] = sha(stop_path)
    stop = json.loads(stop_path.read_text())
    require(stop["retry_plan_sha256"] == sha(retry_path), "stop record plan binding differs")
    stop_correction_path = RAW / "family_campaign" / "campaign_stop_correction.json"
    inputs[str(stop_correction_path.relative_to(REPO))] = sha(stop_correction_path)
    stop_correction = json.loads(stop_correction_path.read_text())
    require(stop_correction["original_sha256"] == sha(stop_path),
            "stop record correction binding differs")
    prior_check_path = RAW / "full_census_crosscheck_v2.json"
    require(stop["crosscheck_v2_sha256"] == sha(prior_check_path),
            "stop record census binding differs")
    inputs[str(prior_check_path.relative_to(REPO))] = sha(prior_check_path)
    extra_segments = []
    frozen_paths = {segment["path"] for segment in retry["source_segments"]}
    for name, metadata in stop["additional_files"].items():
        if name.endswith((".jsonl", ".jsonl.partial")):
            if name in frozen_paths:
                require(any(segment["sha256"] == metadata["sha256"]
                            for segment in retry["source_segments"]
                            if segment["path"] == name),
                        f"duplicate segment digest differs: {name}")
                continue
            extra_segments.append({"target": "P-256", "path": name,
                                   "sha256": metadata["sha256"],
                                   "rows": metadata["completed_rows"]})
    overlaps = collections.Counter()
    seen = collections.defaultdict(set)
    for segment in retry["source_segments"] + extra_segments:
        rep = segment["target"]
        path = ROOT / segment["path"]
        require(sha(path) == segment["sha256"], f"frozen segment changed: {path}")
        with path.open() as source:
            header = json.loads(next(source))
            require(header["target"] == rep, f"segment header differs: {path}")
            rows = [json.loads(line) for line in source]
        require(len(rows) == segment["rows"], f"segment length differs: {path}")
        p = int(by_name[rep]["p"])
        run = STREAMS[rep]
        for row in rows:
            i = row["index"]
            require(i not in seen[rep] and row["seed"] == candidates[rep][i]["seed"],
                    f"overlap duplicate or seed mismatch: {rep}/{i}")
            seen[rep].add(i)
            n0, nt = orders[rep].get(i, (0, 0))
            pn, pt = prime.get((run, i), (False, False))
            want_c = family_eligible(n0, p, pn)
            want_o = family_eligible(nt, p, pt) if p % 4 == 3 else want_c
            require(row["family_accept_canonical"] == want_c and
                    row["family_accept_other"] == want_o,
                    f"independent family acceptance differs: {rep}/{i}")
            if row["status"] == "COUNTED":
                if n0:
                    require(int(row["canonical"]["order"]) == n0,
                            f"exact canonical order differs: {rep}/{i}")
                    overlaps["exact_canonical_orders"] += 1
                expected_other = nt if p % 4 == 3 else n0
                if expected_other:
                    require(int(row["other"]["order"]) == expected_other,
                            f"exact other order differs: {rep}/{i}")
                    overlaps["exact_other_orders"] += 1
            overlaps["prefix_rows"] += 1
    require(overlaps["prefix_rows"] ==
            stop_correction["corrections"]["expected_total_overlap_rows"],
            "unexpected retained-prefix coverage")

    totals = {key: sum(len(row[key]) for row in results.values()) for key in
              ("published", "screen_accepted", "screen_skipped",
               "screen_rejected_order_too_wide", "only_quadratic_twist_prime",
               "both_curve_and_twist_prime",
               "seeded_opposite_root_only_prime", "broad_family_both_seeded_roots",
               "broad_family_unpublished")}
    totals["stream_blocks"] = sum(row["stream_blocks"] for row in results.values())
    totals["seeded_coefficients"] = sum(row["seeded_coefficients"] for row in results.values())
    require(totals["stream_blocks"] == 21753 and totals["seeded_coefficients"] == 11042 and
            totals["published"] == 10 and totals["screen_skipped"] == 11 and
            totals["screen_rejected_order_too_wide"] == 17 and
            totals["only_quadratic_twist_prime"] == 47 and
            totals["both_curve_and_twist_prime"] == 1 and
            totals["seeded_opposite_root_only_prime"] == 31 and
            totals["broad_family_unpublished"] == 59,
            "unexpected aggregate counts")
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                text=True, capture_output=True, check=True).stdout.strip()
    ended = dt.datetime.now(dt.timezone.utc)
    record = {
        "status": "validated", "scope": "six recovered prime-field timestamp streams only",
        "started_utc": started.isoformat(), "ended_utc": ended.isoformat(),
        "elapsed_seconds": round(time.monotonic() - tic, 3),
        "command": sys.argv, "git_head": git_commit,
        "python": platform.python_version(), "gp_version": gp_version,
        "gp_command": ["gp", "-q", "-f"], "gp_returncode": completed.returncode,
        "gp_input_sha256": sha(gp_input), "gp_stdout_sha256": sha(gp_stdout),
        "gp_stderr_sha256": sha(gp_stderr), "script_sha256": sha(Path(__file__)),
        "input_sha256": inputs,
        "ru_maxrss_unit": "bytes" if sys.platform == "darwin" else "KiB",
        "peak_self_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_child_rss_native": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "gp_primality_queries": len(requests),
        "independent_skipped_order_matches": len(assessed_keys),
        "published_order_matches": sum(len(items) for items in by_run.values()),
        "overlap": dict(overlaps), "totals": totals, "streams": results,
    }
    with output.open("x") as sink:
        json.dump(record, sink, indent=2, sort_keys=True)
        sink.write("\n")
    print(json.dumps({"output": str(output), "sha256": sha(output),
                      "totals": totals, "overlap": dict(overlaps)}, sort_keys=True))


if __name__ == "__main__":
    main()
