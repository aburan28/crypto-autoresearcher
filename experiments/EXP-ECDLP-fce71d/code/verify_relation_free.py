#!/usr/bin/env python3
"""Deterministic special-j eigenvalue relation audit (EXP-ECDLP-fce71d).

This is a bounded certificate audit, not an ECDLP solver.  It reads the
immutable EXP-ENDO-001 frozen instances, verifies the named point maps, and
searches a fixed {-1,0,1} coefficient box.  The synthetic control deliberately
has the same dimension but no relation in that box.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import sympy
import yaml

REPO = Path(__file__).resolve().parents[3]
# Make the repository-local harness importable when the frozen command is
# launched from the repository root or from an isolated worktree.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
FROZEN = REPO / "experiments" / "EXP-ENDO-001" / "frozen-instances.yaml"
RUN_ID = "RUN-ECDLP-fce71d-001"
EXP_ID = "EXP-ECDLP-fce71d"


def relation_vectors(values: list[int], modulus: int) -> list[list[int]]:
    out: list[list[int]] = []
    for coeffs in itertools.product((-1, 0, 1), repeat=len(values)):
        if all(c == 0 for c in coeffs):
            continue
        if sum(c * v for c, v in zip(coeffs, values)) % modulus == 0:
            out.append(list(coeffs))
    return out


def choose_root(poly: str, modulus: int) -> int:
    if poly == "j0":
        d = sympy.sqrt_mod(-3, modulus, all_roots=True)
        roots = sorted({((-1 + int(s)) * pow(2, -1, modulus)) % modulus for s in d})
        roots = [r for r in roots if (r * r + r + 1) % modulus == 0]
    else:
        roots = sorted({int(r) % modulus for r in sympy.sqrt_mod(-1, modulus, all_roots=True)})
        roots = [r for r in roots if (r * r + 1) % modulus == 0]
    if not roots:
        raise ValueError(f"no modular root for {poly} modulo {modulus}")
    return roots[0]


def map_point(cell: dict) -> tuple[int, int]:
    p = int(cell["p"])
    x, y = map(int, cell["P"])
    if cell["family"] == "j0":
        return (int(cell["zeta3"]) * x) % p, y
    if cell["family"] == "j1728":
        return (-x) % p, (int(cell["i_sqrt"]) * y) % p
    raise ValueError("map requested for generic cell")


def audit_cell(E, cell: dict) -> dict:
    fam = cell["family"]
    n = int(cell["n"])
    if not bool(sympy.isprime(n)):
        raise ValueError(f"subgroup order is not prime for {cell['cell_id']}")
    if fam == "j0":
        lam = choose_root("j0", n)
        eigenvalues = [1, lam, (lam * lam) % n]
        expected = [[1, 1, 1]]
    elif fam == "j1728":
        lam = choose_root("j1728", n)
        eigenvalues = [1, lam, (-1) % n, (-lam) % n]
        expected = [[1, 0, 1, 0], [0, 1, 0, 1]]
    else:
        raise ValueError(f"not a special-j cell: {cell['cell_id']}")
    P = tuple(map(int, cell["P"]))
    image = map_point(cell)
    # The frozen geometric map chooses one of the two conjugate roots.  Match
    # the scalar to that map rather than assuming SymPy's sorted root order.
    candidates = [lam]
    if fam == "j0":
        candidates.append((lam * lam) % n)
    else:
        candidates.append((-lam) % n)
    for candidate in candidates:
        if E.mul(candidate, P) == image:
            lam = candidate
            break
    if fam == "j0":
        eigenvalues = [1, lam, (lam * lam) % n]
    else:
        eigenvalues = [1, lam, (-1) % n, (-lam) % n]
    scalar_image = E.mul(lam, P)
    map_verified = image == scalar_image and E.is_on_curve(image)
    relations = relation_vectors(eigenvalues, n)
    expected_present = all(v in relations for v in expected)
    return {
        "cell_id": cell["cell_id"],
        "family": fam,
        "field_bits": int(cell["field_bits"]),
        "p": int(cell["p"]),
        "n": n,
        "curve_input_sha256": cell.get("sha256"),
        "eigenvalues": eigenvalues,
        "defining_polynomial": "L^2+L+1" if fam == "j0" else "L^2+1",
        "map_image": list(image),
        "scalar_image": list(scalar_image) if scalar_image is not None else None,
        "map_scalar_verified": map_verified,
        "relation_vectors": relations,
        "expected_relation_vectors_present": expected_present,
        "relation_count": len(relations),
    }


def main() -> int:
    t0 = time.time()
    doc = yaml.safe_load(FROZEN.read_text())
    cells = doc["cells"]
    selected = [c for c in cells if c["family"] in ("j0", "j1728")]
    generic = [c for c in cells if c["family"] == "generic"]
    results = []
    for cell in selected:
        from harness.toycurve import EllipticCurve
        E = EllipticCurve(int(cell["p"]), int(cell["a"]), int(cell["b"]))
        results.append(audit_cell(E, cell))
    synthetic = []
    for cell in selected:
        n = int(cell["n"])
        vals = [1, 2 % n, 4 % n]
        rels = relation_vectors(vals, n)
        synthetic.append({"cell_id": cell["cell_id"], "modulus": n,
                          "eigenvalues": vals, "relation_vectors": rels,
                          "relation_free": not rels})
    generic_boundary = [{"cell_id": c["cell_id"], "field_bits": int(c["field_bits"]),
                        "rank": 1, "extra_map_tested": False} for c in generic]
    all_maps = all(r["map_scalar_verified"] for r in results)
    all_expected = all(r["expected_relation_vectors_present"] for r in results)
    all_synth_free = all(s["relation_free"] for s in synthetic)
    raw = {
        "run_id": RUN_ID,
        "experiment_id": EXP_ID,
        "frozen_input": str(FROZEN.relative_to(REPO)),
        "frozen_input_sha256": hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
        "selected_cell_count": len(results),
        "special_j_results": results,
        "synthetic_control": synthetic,
        "generic_rank_one_boundary": generic_boundary,
        "summary": {
            "map_scalar_verification_rate": sum(r["map_scalar_verified"] for r in results) / len(results),
            "short_relation_present_rate": sum(r["expected_relation_vectors_present"] for r in results) / len(results),
            "synthetic_relation_free_control_rate": sum(s["relation_free"] for s in synthetic) / len(synthetic),
            "success_criterion_met": all_maps and all_expected and all_synth_free,
            "falsification_criterion_met": any(r["map_scalar_verified"] and r["relation_count"] == 0 for r in results),
        },
        "wall_clock_seconds": round(time.time() - t0, 6),
    }
    out = Path(os.environ.get("ECDLP_AUDIT_OUT", "raw-result.json"))
    out.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")
    print(json.dumps(raw["summary"], sort_keys=True))
    return 0 if all_maps and all_expected and all_synth_free else 2


if __name__ == "__main__":
    raise SystemExit(main())
