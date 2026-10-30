#!/usr/bin/env python3
"""Independent verifier: imports neither the producer nor its polynomial core."""
from __future__ import annotations
import argparse
import copy
import itertools
import json
from pathlib import Path


def poly(items, p):
    result = {}
    for mask, c in items:
        assert isinstance(mask, int) and mask >= 0
        result[mask] = (result.get(mask, 0) + c) % p
    return {m: c for m, c in result.items() if c}


def evaluate(f, bits, p):
    return sum(c for mask, c in f.items() if bits & mask == mask) % p


def add_multiple(dst, f, mon, c, p):
    for mask, a in f.items():
        new = mask | mon
        dst[new] = (dst.get(new, 0) + c * a) % p
        if not dst[new]:
            del dst[new]


def restriction(f, assignment, p):
    zeros = sum(1 << i for i, v in assignment.items() if v == 0)
    ones = sum(1 << i for i, v in assignment.items() if v == 1)
    result = {}
    for mask, c in f.items():
        if mask & zeros:
            continue
        new = mask & ~ones
        result[new] = (result.get(new, 0) + c) % p
    return {m: c for m, c in result.items() if c}


def order(mask):
    return mask.bit_count(), tuple(i for i in range(mask.bit_length()) if mask >> i & 1)


def reduce_row(f, basis, p):
    f = dict(f)
    while f:
        pivot = max(f, key=order)
        if pivot not in basis:
            return f
        add_multiple(f, basis[pivot], 0, -f[pivot], p)
    return f


def verify_basis(records, equations, p, n):
    basis = {}
    for entry in records:
        reconstructed = {}
        for i, mult, c in entry["combination"]:
            assert 0 <= i < len(equations) and 0 <= mult < 1 << n
            add_multiple(reconstructed, equations[i], mult, c, p)
        row = poly(entry["row"], p)
        assert reconstructed == row, "invalid original-equation certificate"
        assert row and row[entry["pivot"]] == 1
        assert max(row, key=order) == entry["pivot"]
        assert entry["pivot"] not in basis
        basis[entry["pivot"]] = row
    return basis


def affine_rank(basis, active, p):
    equations = [dict(row) for row in basis.values() if max((m.bit_count() for m in row), default=0) <= 1]
    rank = 0
    for var in active:
        mon = 1 << var
        idx = next((j for j in range(rank, len(equations)) if equations[j].get(mon)), None)
        if idx is None:
            continue
        equations[rank], equations[idx] = equations[idx], equations[rank]
        inv = pow(equations[rank][mon], -1, p)
        equations[rank] = {m: c * inv % p for m, c in equations[rank].items()}
        for j in range(rank + 1, len(equations)):
            if equations[j].get(mon):
                add_multiple(equations[j], equations[rank], 0, -equations[j][mon], p)
        rank += 1
    return rank


def all_models(equations, p, n, assignment=None):
    assignment = assignment or {}
    return [bits for bits in range(1 << n)
            if all((bits >> i & 1) == v for i, v in assignment.items())
            and all(evaluate(f, bits, p) == 0 for f in equations)]


def source_rank(matrix, p):
    # A second columnwise echelon implementation; no producer helpers.
    rows = [r[:] for r in matrix]
    pivots = {}
    for row in rows:
        for j, value in enumerate(row):
            if not value:
                continue
            if j in pivots:
                base = pivots[j]
                row = [(a - value * b) % p for a, b in zip(row, base)]
            else:
                inv = pow(value, -1, p)
                pivots[j] = [a * inv % p for a in row]
                break
    return len(pivots)


def check_source(data):
    cfg = data["input"]
    p = cfg["p"]
    equations = [{tuple(m): c % p for m, c in f} for f in cfg["polynomials"]]
    count = 0
    for item in data["matrices"]:
        columns = [tuple(m) for m in item["columns"]]
        expected = []
        for mult, i in item["row_labels"]:
            row = {tuple(a + b for a, b in zip(mon, mult)): c for mon, c in equations[i].items()}
            assert set(row) <= set(columns)
            expected.append([row.get(mon, 0) for mon in columns])
        assert expected == item["matrix"]
        rank = source_rank(expected, p)
        assert rank == item["rank"]
        assert len(columns) - rank == item["nullity"]
        count += 1
    models = []
    for values in itertools.product(range(p), repeat=len(cfg["variables"])):
        first = next((x for x in values if x), None)
        if first != 1:
            continue
        valid = True
        for f in equations:
            total = 0
            for mon, c in f.items():
                term = c
                for x, exponent in zip(values, mon):
                    term *= pow(x, exponent, p)
                total += term
            if total % p:
                valid = False
                break
        if valid:
            models.append(list(values))
    assert models == data["projective_models"]
    return count


def verify(data):
    config = data["config"]
    counts = {"cells": 0, "lead3_arms": 0, "lead4_arms": 0, "branch_assignments": 0,
              "basis_certificates": 0, "complete_results": 0, "unknown_results": 0}
    for cell in data["cells"]:
        p, n = cell["p"], cell["n"]
        equations = [poly(f, p) for f in cell["equations"]]
        expected = all_models(equations, p, n)
        assert expected == sorted(cell["oracle_models"])
        counts["cells"] += 1
        for arm in cell["lead3"]:
            inputs = [poly(f, p) for f in arm["equations"]]
            assert inputs == (list(reversed(equations)) if arm["arm"] == "aa_full_total_reverse_input" else equations)
            basis = verify_basis(arm["basis"], inputs, p, n)
            counts["basis_certificates"] += len(basis)
            if arm["status"] not in ("UNKNOWN", "ROW_CAP"):
                assert sorted(arm["models"]) == expected
                if 0 in basis:
                    assert not expected
                else:
                    assert all(not reduce_row(f, basis, p) for f in inputs)
                    for row in basis.values():
                        for i in range(n):
                            product = {}
                            add_multiple(product, row, 1 << i, 1, p)
                            assert not reduce_row(product, basis, p), "non-ideal span reported complete"
                    assert len(basis) == (1 << n) - len(expected)
                counts["complete_results"] += 1
            else:
                assert arm["models"] is None
                counts["unknown_results"] += 1
            counts["lead3_arms"] += 1
        for arm in cell["lead4"]:
            cut = arm["cut"]
            assert len(cut) == len(set(cut)) == min(config["backdoor_bits"], n)
            seen = set()
            models = []
            complete = True
            for branch in arm["branches"]:
                assignment = dict(branch["assignment"])
                assert set(assignment) == set(cut) and set(assignment.values()) <= {0, 1}
                key = tuple(assignment[i] for i in cut)
                assert key not in seen
                seen.add(key)
                residual = [restriction(f, assignment, p) for f in equations]
                assert residual == [poly(f, p) for f in branch["equations"]]
                basis = verify_basis(branch["basis"], residual, p, n)
                assert all(max((m.bit_count() for m in row), default=0) <= config["residual_degree_cap"]
                           for row in basis.values())
                counts["basis_certificates"] += len(basis)
                if branch["status"] == "UNKNOWN":
                    assert branch["models"] is None
                    complete = False
                else:
                    if 0 not in basis:
                        active = [i for i in range(n) if i not in assignment]
                        free = len(active) - affine_rank(basis, active, p)
                        assert free <= config["affine_free_variable_cap"], "uncertified residual enumeration"
                    found = all_models(equations, p, n, assignment)
                    assert sorted(branch["models"]) == found
                    models.extend(found)
                counts["branch_assignments"] += 1
            assert seen == set(itertools.product((0, 1), repeat=len(cut)))
            assert arm["legal_assignments"] == arm["checked_assignments"] == len(seen)
            assert arm["strong_backdoor"] == complete
            if complete:
                assert sorted(models) == sorted(arm["models"]) == expected
                counts["complete_results"] += 1
            else:
                assert arm["models"] is None
                counts["unknown_results"] += 1
            for metric in ("all_counted_field_ops", "rows_generated", "root_term_evaluations"):
                assert arm["metrics"].get(metric, 0) == sum(b["metrics"].get(metric, 0) for b in arm["branches"])
            counts["lead4_arms"] += 1
    counts["source_matrices"] = check_source(data["source_calibration"])
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    parser.add_argument("--output")
    args = parser.parse_args()
    data = json.loads(Path(args.result).read_text())
    counts = verify(data)
    tampered = copy.deepcopy(data)
    record = next(record for cell in tampered["cells"] for arm in cell["lead3"] for record in arm["basis"])
    record["row"][0][1] += 1
    try:
        verify(tampered)
    except AssertionError:
        counts["tampered_certificate_rejected"] = True
    else:
        raise AssertionError("checker accepted an altered certificate")
    result = {"verified": True, "counts": counts,
              "scope": "Independent complete Boolean model-set and polynomial certificate checks; no speed or ECDLP claim"}
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
