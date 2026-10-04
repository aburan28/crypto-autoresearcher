"""Static provenance gate: the k-free transport path must never read k.

This is a blocking Stage 1 gate. It parses kfree_transport.py by AST and
refuses any discrete-log scalar on the public function surface.
"""
from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_PARAM_NAMES = frozenset(
    {
        "k",
        "scalar",
        "dlog",
        "discrete_log",
        "withheld_scalar",
        "secret_k",
        "log_k",
    }
)

REQUIRED_FUNCTIONS = (
    "hensel_lift_without_projection",
    "canonical_order_n_lift",
    "ordinary_base_p_digits",
    "affine_digits",
)


def check_kfree_module(path: Path) -> dict:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    found = {}
    failures = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name not in REQUIRED_FUNCTIONS:
            continue
        params = [a.arg for a in node.args.args]
        found[node.name] = params
        bad = [name for name in params if name in FORBIDDEN_PARAM_NAMES]
        if bad:
            failures.append(
                {
                    "function": node.name,
                    "forbidden_params": bad,
                    "all_params": params,
                }
            )
    missing = [name for name in REQUIRED_FUNCTIONS if name not in found]
    if missing:
        failures.append({"missing_functions": missing})
    # canonical_order_n_lift must take the F_p point, n, and precision only
    # (plus the curve). It must not take a scalar.
    canon = found.get("canonical_order_n_lift")
    if canon is not None:
        if "P_fp" not in canon or "n" not in canon or "precision" not in canon:
            failures.append(
                {
                    "function": "canonical_order_n_lift",
                    "reason": "expected parameters include P_fp, n, precision",
                    "all_params": canon,
                }
            )
    passed = not failures
    return {
        "module": str(path),
        "functions": found,
        "forbidden_param_names": sorted(FORBIDDEN_PARAM_NAMES),
        "failures": failures,
        "passed": passed,
        "gate": "static_provenance",
        "meaning": (
            "The k-free transport module accepts an F_p point and never a "
            "discrete-log scalar. A statistic that reads k is measuring its own input."
        ),
    }


def main() -> None:
    import json
    import sys

    path = Path(__file__).resolve().parent / "kfree_transport.py"
    result = check_kfree_module(path)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
