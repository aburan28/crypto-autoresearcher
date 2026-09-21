#!/usr/bin/env python3
"""Machine-check the P1511/IDEA-117 FD-width derivation gate."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ecdlp_index_calculus_state"
RESEARCH = ROOT / "research"
IDEA_ROOT = Path("/Volumes/Volume/crypto-autoresearcher")
DERIVATION = IDEA_ROOT / "ideas/artifacts/ECDLP-IDEA-117/fd_width_gate.md"
RESULT = STATE / "p1511_fd_width_gate.json"
NOTE = RESEARCH / "p1511_fd_width_gate.md"

INPUTS = {
    STATE / "p1490_rational_lift_selector_norm.json":
        "1fbb457f642dab18cab43c69bf694f9a41b68c6ecefa365d7432e1ac7107cbab",
    STATE / "p1490_rational_lift_selector_norm_audit.json":
        "da5b6d4b194d9c03a29622ac03fe3e8c6dae33f1e99c788c46b82fb38f85fa7a",
    STATE / "p1491_pointwise_selector_subresultant.json":
        "26fc025c2de2c8ce331bacc8e556d47557159eea755fbc4e86d87da2d1d483be",
    STATE / "p1491_pointwise_selector_subresultant_audit.json":
        "31b1c95e09addd661e693d88fbdce2e1589fec47c7752e20b69f0bd7e0db6bc4",
    STATE / "p1505_endpoint_moment_source_tag_gate.json":
        "a8c7e0a1cb69fa762102fc1a9339390e3844081eb60245dd353f38e59a16b672",
    STATE / "p1505_endpoint_moment_source_tag_gate_audit.json":
        "2ffc182297fad777955b89d1234a6cc280e6fe4dca32db8d851fe31b37c3562b",
    STATE / "p1510_global_truncated_marked_resultant_compiler.json":
        "55435eda07e37e1b30f882f20480c3bc612e83094640a0203ab5c6096cb0f589",
    STATE / "p1510_global_truncated_marked_resultant_compiler_audit.json":
        "25268ebd0c65ea83672088b93b4490fd47236876fd31037dbe76f753f1a455b6",
    DERIVATION:
        "97cd97a70ddf6279bdc86cc6a5055574edb6d62c0070642a4f70889cda9a32d9",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def join_tree_is_valid(edges: list[set[str]], tree_edges: list[tuple[int, int]]) -> bool:
    adjacency = {index: set() for index in range(len(edges))}
    for left, right in tree_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if len(tree_edges) != len(edges) - 1:
        return False
    seen = set()
    frontier = [0]
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(adjacency[current] - seen)
    if len(seen) != len(edges):
        return False
    attributes = set().union(*edges)
    for attribute in attributes:
        containing = {index for index, edge in enumerate(edges) if attribute in edge}
        start = next(iter(containing))
        reached = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency[current]:
                if neighbor in containing and neighbor not in reached:
                    reached.add(neighbor)
                    frontier.append(neighbor)
        if reached != containing:
            return False
    return True


def render_note(payload: dict[str, Any]) -> str:
    rows = payload["empirical_support"]
    lines = [
        "# P1511 FD-Width Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Checked Boundary",
        "",
        "The source-labelled serial transition query has the valid join tree",
        "`E1(t,i,V)-E2(V,j,W)-E4(U,m,W)-E3(k,l,U)`. It is already acyclic",
        "once its relations are supplied. The unresolved cost is constructing or",
        "implicitly semijoining those relations with exact provenance.",
        "",
        "| r | pair sources | triple sources | distinct A3 x | P1510 slot formula |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['r']} | {row['pair_source_count']} | "
            f"{row['triple_source_count']} | {row['distinct_A3_x_count']} | "
            f"{row['p1510_output_slots_formula']} |"
        )
    lines += [
        "",
        "P1510 emits exactly `60r^2-9` slots per synthetic target. Repeating",
        "that complete object for `Theta(r)` relation rows costs `Theta(r^3)`,",
        "or `q^(3/5)` on `q=Theta(r^5)`, above rho's `q^(1/2)` boundary.",
        "",
        "## Decision",
        "",
        "The degree-aware join theorem does not itself create the missing input",
        "iterator. No sub-`r^1.5` source-preserving iterator is derived, so this",
        "route returns `REVISE`. The only admissible continuation is a factorized",
        "marked-polynomial semijoin that filters before dense A2/A3 emission.",
        "This result is not a lower bound against all such algebraic semijoins and",
        "does not establish relation collection, descent, or a rho/Shoup break.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    frozen_hashes = {str(path): sha256(path) for path in INPUTS}
    exact_hashes = all(frozen_hashes[str(path)] == expected for path, expected in INPUTS.items())

    p1490_audit = load(STATE / "p1490_rational_lift_selector_norm_audit.json")
    p1491 = load(STATE / "p1491_pointwise_selector_subresultant.json")
    p1491_audit = load(STATE / "p1491_pointwise_selector_subresultant_audit.json")
    p1505 = load(STATE / "p1505_endpoint_moment_source_tag_gate.json")
    p1505_audit = load(STATE / "p1505_endpoint_moment_source_tag_gate_audit.json")
    p1510 = load(STATE / "p1510_global_truncated_marked_resultant_compiler.json")
    p1510_audit = load(STATE / "p1510_global_truncated_marked_resultant_compiler_audit.json")

    candidate_rows = p1491["candidate_generation_cells"]
    scaling_by_r = {row["r"]: row for row in p1510["synthetic_scaling"]["rows"]}
    empirical_support = []
    for row in candidate_rows:
        r = int(row["selector_degree_r"])
        empirical_support.append({
            "L": int(row["L"]),
            "r": r,
            "pair_source_count": int(row["pair_source_count"]),
            "expected_pair_source_count": math.comb(2 * r + 1, 2),
            "triple_source_count": int(row["triple_source_count"]),
            "expected_triple_source_count": math.comb(2 * r + 2, 3),
            "distinct_A3_x_count": int(row["distinct_A3_x_count"]),
            "p1510_output_slots_formula": 60 * r * r - 9,
            "p1510_output_slots_observed": (
                int(scaling_by_r[r]["output_slots"]) if r in scaling_by_r else None
            ),
        })

    ambiguity_rows = [cell["source_collisions"] for cell in p1505["cells"]]
    join_edges = [
        {"t", "i", "V"},
        {"V", "j", "W"},
        {"U", "m", "W"},
        {"k", "l", "U"},
    ]
    checks = {
        "all_frozen_hashes_exact": exact_hashes,
        "serial_source_join_has_valid_acyclic_join_tree": join_tree_is_valid(
            join_edges, [(0, 1), (1, 2), (2, 3)]
        ),
        "pair_source_counts_equal_oriented_multiset_formula": all(
            row["pair_source_count"] == row["expected_pair_source_count"]
            for row in empirical_support
        ),
        "triple_source_counts_equal_oriented_multiset_formula": all(
            row["triple_source_count"] == row["expected_triple_source_count"]
            for row in empirical_support
        ),
        "all_endpoint_x_values_have_ambiguous_provenance": all(
            row["all_endpoint_x_source_ambiguous"] for row in ambiguity_rows
        ),
        "p1510_output_slots_equal_60r2_minus_9": all(
            int(row["output_slots"]) == 60 * int(row["r"]) ** 2 - 9
            for row in p1510["synthetic_scaling"]["rows"]
        ),
        "p1510_symbolic_per_target_exponent_is_two":
            p1510["synthetic_scaling"]["symbolic_state_bound"]
            == "O(r^2) endpoint-polynomial coefficient slots",
        "current_complete_campaign_exponent_three_exceeds_rho": 3.0 > 2.5,
        "all_prior_independent_audits_pass": (
            p1490_audit["status"].startswith("PASS")
            and p1491_audit["status"].startswith("PASS")
            and p1505_audit["status"].startswith("PASS")
            and p1510_audit["status"].startswith("PASS")
        ),
        "relation_and_breakthrough_gates_remain_false": (
            not p1510["gates"]["relation_collection_completed"]
            and not p1510["gates"]["blind_descent_completed"]
            and not p1510["gates"]["generic_shoup_breakthrough"]
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"P1511 FD-width gate failed checks: {failed}")

    payload = {
        "schema": "autolab.ecdlp.p1511_fd_width_gate.v1",
        "status": "REVISE_P1511_ACYCLIC_JOIN_INPUT_GENERATION_STILL_CUBIC",
        "source": str(Path(__file__).resolve()),
        "source_sha256": sha256(Path(__file__).resolve()),
        "derivation": str(DERIVATION),
        "derivation_sha256": sha256(DERIVATION),
        "frozen_hashes": frozen_hashes,
        "relational_schema": {
            "edges": [sorted(edge) for edge in join_edges],
            "join_tree_edges": [[0, 1], [1, 2], [2, 3]],
            "join_tree_valid": True,
            "functional_dependency_boundary": (
                "Each transition triple is functional after two adjacent attributes are fixed; "
                "no FD constructs an unfixed source relation or implicit neighbor iterator."
            ),
        },
        "empirical_support": empirical_support,
        "cost_boundary": {
            "q_as_function_of_r": "Theta(r^5)",
            "required_per_target_source_query_exponent": "alpha<3/2",
            "p1510_per_target_output_exponent": 2.0,
            "theta_r_targets_complete_campaign_exponent": 3.0,
            "complete_campaign_q_exponent": 0.6,
            "pollard_rho_r_exponent": 2.5,
            "pollard_rho_q_exponent": 0.5,
        },
        "checks": checks,
        "check_count": len(checks),
        "check_pass_count": sum(checks.values()),
        "claim_status": {
            "fd_width_join_mechanism": "not_reproduced",
            "factorized_source_marked_semijoin": "open",
            "relation_collection": "not_attempted",
            "blind_descent": "not_attempted",
            "generic_shoup_breakthrough": "not_attempted",
        },
        "interpretation": (
            "The exact source join is acyclic after its transition relations are supplied, "
            "but current exact input construction remains cubic over a complete relation campaign. "
            "P1510 provides source-coded quadratic A2 compilation, not the sub-r^1.5 implicit "
            "semijoin iterator required by IDEA-117. This is a scoped revise result, not a lower "
            "bound against every factorized algebraic semijoin."
        ),
        "next_action": (
            "Derive a factorized source-marked semijoin that returns only common A2/A3 factors "
            "and source jets without dense degree-r^3 expansion or all surface-pair queries."
        ),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    write_atomic(RESULT, encoded)
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(
        f"status={payload['status']} checks={payload['check_pass_count']}/{payload['check_count']}"
    )


if __name__ == "__main__":
    main()
