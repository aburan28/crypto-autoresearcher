"""Exact 11-bit membership statistics for two archived ICPERF factor bases.

This script reads immutable input records and never invokes a solver. The BDD
clause count is for a hypothetical Tseitin encoding with one output variable
per reduced node and conditional equivalences, plus a root unit clause.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WIDTH = 11
DOMAIN = 1 << WIDTH
INPUTS = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
MANIFESTS = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json",
}


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def allowed_values(base: dict) -> set[int]:
    offset = base["selected_offset"]
    scan, = [row for row in base["candidate_scans"] if row["offset"] == offset]
    result = {value ^ offset for value in scan["accepted_phi"]}
    assert len(result) == len(scan["accepted_phi"]) == 632
    assert all(0 <= value < DOMAIN for value in result)
    return result


def anf(allowed: set[int]) -> dict:
    coefficients = [int(value in allowed) for value in range(DOMAIN)]
    for bit in range(WIDTH):
        for mask in range(DOMAIN):
            if mask & (1 << bit):
                coefficients[mask] ^= coefficients[mask ^ (1 << bit)]
    # Independent evaluation from the coefficient list for the full domain.
    for value in range(DOMAIN):
        evaluated = 0
        submask = value
        while True:
            evaluated ^= coefficients[submask]
            if submask == 0:
                break
            submask = (submask - 1) & value
        assert evaluated == int(value in allowed)
    histogram = Counter(mask.bit_count() for mask, coefficient in
                        enumerate(coefficients) if coefficient)
    return {"terms": sum(histogram.values()), "degree": max(histogram),
            "terms_by_degree": {str(degree): count for degree, count in
                                sorted(histogram.items())}}


def reduced_bdd(allowed: set[int], order: list[int]) -> dict:
    assert sorted(order) == list(range(WIDTH))
    unique: dict[tuple[int, int, int], int] = {}
    nodes: dict[int, tuple[int, int, int]] = {}

    def build(level: int, values: list[int]) -> int:
        first = values[0] in allowed
        if all((value in allowed) == first for value in values):
            return int(first)
        bit = order[level]
        low = build(level + 1, [value for value in values if not (value >> bit) & 1])
        high = build(level + 1, [value for value in values if (value >> bit) & 1])
        if low == high:
            return low
        key = (bit, low, high)
        if key not in unique:
            index = len(unique) + 2
            unique[key] = index
            nodes[index] = key
        return unique[key]

    root = build(0, list(range(DOMAIN)))

    def evaluate(value: int) -> int:
        index = root
        while index >= 2:
            bit, low, high = nodes[index]
            index = high if (value >> bit) & 1 else low
        return index

    assert all(evaluate(value) == int(value in allowed) for value in range(DOMAIN))
    # For z = ITE(bit, high, low), a terminal child needs one conditional
    # clause and a nonterminal child two; the accepted root adds one unit.
    clauses = 1 + sum((1 if low < 2 else 2) + (1 if high < 2 else 2)
                      for _, low, high in nodes.values())
    return {"order": order, "nodes_per_block": len(nodes),
            "added_variables_for_8_blocks": 8 * len(nodes),
            "clauses_per_block": clauses,
            "clauses_for_8_blocks": 8 * clauses,
            "truth_table_cases_verified": DOMAIN}


def main() -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    rows = {}
    input_sha = {}
    for label in INPUTS:
        base_blob = INPUTS[label].read_bytes()
        manifest_blob = MANIFESTS[label].read_bytes()
        input_sha[str(INPUTS[label].relative_to(ROOT))] = digest(base_blob)
        input_sha[str(MANIFESTS[label].relative_to(ROOT))] = digest(manifest_blob)
        base = json.loads(base_blob)
        manifest = json.loads(manifest_blob)
        allowed = allowed_values(base)
        arms = manifest["arms"]
        assert len(arms) == 4
        assert all(arm["membership_forbid_clauses"] == 11328 for arm in arms)
        assert all(arm["allowed_coordinate_values"] == 632 for arm in arms)
        rows[label] = {"accepted_values": len(allowed),
                       "membership_sha256": digest(bytes(int(x in allowed)
                                                         for x in range(DOMAIN))),
                       "anf": anf(allowed),
                       "bdd_lsb_first": reduced_bdd(allowed, list(range(WIDTH))),
                       "bdd_msb_first": reduced_bdd(allowed, list(range(WIDTH - 1, -1, -1))),
                       "archived_forbidden_clauses_for_8_blocks": 11328,
                       "archived_channel_0_cnf_clauses": arms[0]["cnf_clauses"],
                       "archived_channel_0_xor_rows": arms[0]["native_xor_rows"]}
    assert rows["weighted"]["archived_channel_0_cnf_clauses"] == rows["local_random"]["archived_channel_0_cnf_clauses"]
    assert rows["weighted"]["archived_channel_0_xor_rows"] == rows["local_random"]["archived_channel_0_xor_rows"]
    result = {"schema": "icperf-binary-membership-bdd-v1",
              "scope": "exact input predicate statistics only; no solver, regularity, relation, rank or end-to-end cost measurement",
              "source_sha256": digest(Path(__file__).read_bytes()),
              "input_sha256": input_sha,
              "curve": {"field_degree": 61, "prime_order": 576460752557211763,
                        "cofactor": 4},
              "factor_base_columns_per_arm": 316,
              "summands": 8,
              "boolean_domain_size": DOMAIN,
              "rows": rows,
              "execution": {"command": "python3 research/icperf_binary_membership_bdd_20261017/analyze.py",
                            "started_at": started_at,
                            "wall_seconds": time.perf_counter() - started_wall,
                            "cpu_seconds": time.process_time() - started_cpu,
                            "python_version": sys.version,
                            "platform": platform.platform(),
                            "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                                 cwd=ROOT, text=True).strip(),
                            "git_status_porcelain": subprocess.check_output(["git", "status", "--porcelain"],
                                                                             cwd=ROOT, text=True).splitlines()}}
    with (HERE / "result.json").open("x") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
    print(json.dumps({label: {"anf": row["anf"],
                              "bdd_lsb_first": {k: v for k, v in row["bdd_lsb_first"].items()
                                                if k in ("nodes_per_block", "clauses_for_8_blocks")}}
                      for label, row in rows.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
