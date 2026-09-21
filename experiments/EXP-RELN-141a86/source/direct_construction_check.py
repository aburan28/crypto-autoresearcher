"""
Step (b) of RUN-RELN-141a86-stage0c-minimality: direct construction of the
KNOWN closed-form expression for each target, in grammar_engine's own
representation, verified against the target's control table (zero residual
required) and node-counted by grammar_engine.node_count (the SAME function
used everywhere else in this contract).

Reuses control-tables/ from RUN-RELN-141a86-stage0bcde UNCHANGED (read-only;
not regenerated), and recovery_check.py's parse_expr / verify_expression_on_table
UNCHANGED (the same machinery already used and validated in the prior repair
run's self-test).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_engine as ge
import recovery_check as rc

STAGE0BCDE_TABLES = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "runs", "RUN-RELN-141a86-stage0bcde", "control-tables"))

TARGETS = [
    {
        "target_id": "INV-1_mean",
        "pack": "fb3_unsigned_m3_and_enum_unsigned_m3",
        "canonical_complexity": 9,
        "target_expr": "div(binomial(sub(add(B,m),CONST[1]),m),N)",
        "table_path": os.path.join(STAGE0BCDE_TABLES, "inv1-conservation-mean-table.json"),
        "target_key": "mean_measured",
    },
    {
        "target_id": "INV-7_p_fail",
        "pack": "enum_xclass_signed_m2",
        "canonical_complexity": 9,
        "target_expr": "div(binomial(sub(n,B),B),binomial(n,B))",
        "table_path": os.path.join(STAGE0BCDE_TABLES, "inv7-xclass-m2-table.json"),
        "target_key": "p_fail_closed_form",
    },
    {
        "target_id": "INV-8_d_reg",
        "pack": "degree_table",
        "canonical_complexity": 10,
        "target_expr": "ceil(div(add(mul(m,sub(B,CONST[1])),D_S),CONST[2]))",
        "table_path": os.path.join(STAGE0BCDE_TABLES, "inv8-semiregular-degree-table.json"),
        "target_key": "d_reg_closed_form",
    },
    {
        "target_id": "INV-7_p_exist",
        "pack": "enum_xclass_signed_m2",
        "canonical_complexity": 11,
        "target_expr": "sub(CONST[1],div(binomial(sub(n,B),B),binomial(n,B)))",
        "table_path": os.path.join(STAGE0BCDE_TABLES, "inv7-xclass-m2-table.json"),
        "target_key": "p_exist_closed_form",
    },
]


def main():
    results = []
    for t in TARGETS:
        expr = rc.parse_expr(t["target_expr"])
        canon = ge.canonicalize(expr)
        nc = ge.node_count(canon)
        with open(t["table_path"]) as f:
            rows = json.load(f)
        verification = rc.verify_expression_on_table(expr, rows, t["target_key"], tol=1e-9)
        results.append({
            "target_id": t["target_id"],
            "pack": t["pack"],
            "target_expr_string_input": t["target_expr"],
            "target_canonical_string": ge.to_canonical_string(canon),
            "canonical_node_count_declared": t["canonical_complexity"],
            "node_count_computed_by_grammar_engine": nc,
            "node_count_matches_declared": nc == t["canonical_complexity"],
            "table_path": t["table_path"],
            "target_key": t["target_key"],
            "n_rows": len(rows),
            "verification": verification,
            "zero_residual_confirmed": (
                verification.get("exact_match") is True
                and verification.get("max_residual") == 0.0
            ),
        })
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "runs", "RUN-RELN-141a86-stage0c-minimality", "direct-construction-results.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    for r in results:
        print(f"{r['target_id']}: node_count={r['node_count_computed_by_grammar_engine']} "
              f"(declared {r['canonical_node_count_declared']}, "
              f"match={r['node_count_matches_declared']}); "
              f"n_const={r['verification'].get('n_const')} "
              f"const_values={r['verification'].get('const_values')} "
              f"max_residual={r['verification'].get('max_residual')} "
              f"exact_match={r['verification'].get('exact_match')} "
              f"zero_residual_confirmed={r['zero_residual_confirmed']}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
