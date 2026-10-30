#!/usr/bin/env python3
"""Exact, certificate-producing toy diagnostics for leads 3 and 4.

The Boolean quotient adaptation is NOT the published homogeneous XL algorithm.
No function uses an oracle model set to choose rows, cuts, or a stopping point.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import BoolRing, generate_s3


def pack(poly):
    return [[int(m), int(c)] for m, c in sorted(poly.items()) if c]


def unpack(poly):
    return {int(m): int(c) for m, c in poly}


def mask_order(mask):
    # Increasing degree, then the ascending list of variable indices, as in
    # the source slide's explicit initial-segment convention. Boolean masks
    # are squarefree here; homogeneous calibration below uses exponent tuples.
    return (mask.bit_count(), tuple(i for i in range(mask.bit_length()) if mask >> i & 1))


class Span:
    """Incremental Gaussian span with exact original-equation certificates."""

    def __init__(self, ring, equations):
        self.ring = ring
        self.equations = equations
        self.basis = {}
        self.counts = defaultdict(int)
        self.seen_columns = set()

    def update(self, target, source, scale, proof=False):
        p = self.ring.p
        prefix = "certificate_" if proof else ""
        for mon, coeff in source.items():
            target[mon] = (target.get(mon, 0) + scale * coeff) % p
            self.counts[prefix + "field_muls"] += 1
            self.counts[prefix + "field_adds"] += 1
            if not target[mon]:
                del target[mon]

    def reduce(self, row, proof=None):
        row = dict(row)
        while row:
            pivot = max(row, key=mask_order)
            if pivot not in self.basis:
                break
            base, cert = self.basis[pivot]
            factor = -row[pivot] % self.ring.p
            self.update(row, base, factor)
            if proof is not None:
                self.update(proof, cert, factor, proof=True)
        return row, proof

    def multiply_mask(self, poly, multiplier):
        out = {}
        for mon, coeff in poly.items():
            new = mon | multiplier
            out[new] = (out.get(new, 0) + coeff) % self.ring.p
            self.counts["monomial_term_products"] += 1
            self.counts["field_adds"] += 1
            if not out[new]:
                del out[new]
        return out

    def insert(self, equation_index, multiplier):
        self.counts["rows_generated"] += 1
        row = self.multiply_mask(self.equations[equation_index], multiplier)
        self.seen_columns.update(row)
        proof = {(equation_index, multiplier): 1}
        row, proof = self.reduce(row, proof)
        if not row:
            return False
        pivot = max(row, key=mask_order)
        inv = pow(row[pivot], -1, self.ring.p)
        self.counts["field_inversions"] += 1
        row = {m: c * inv % self.ring.p for m, c in row.items()}
        proof = {m: c * inv % self.ring.p for m, c in proof.items()}
        self.counts["field_muls"] += len(row)
        self.counts["certificate_field_muls"] += len(proof)
        self.basis[pivot] = (row, proof)
        self.counts["independent_rows"] += 1
        return True

    def is_ideal(self, active=None):
        self.counts["ideal_closure_checks"] += 1
        active = range(self.ring.n) if active is None else active
        # All input equations must be represented as well as closure under
        # variables. These are sufficient for equality with the input ideal.
        for equation in self.equations:
            if self.reduce(equation)[0]:
                return False
        for row, _ in self.basis.values():
            for var in active:
                if self.reduce(self.multiply_mask(row, 1 << var))[0]:
                    return False
        return True

    def certificate(self):
        return [{"pivot": pivot, "row": pack(row),
                 "combination": [[i, m, c] for (i, m), c in sorted(cert.items())]}
                for pivot, (row, cert) in sorted(self.basis.items())]

    def metrics(self):
        result = dict(self.counts)
        result["rank"] = len(self.basis)
        result["supported_columns"] = len(self.seen_columns)
        result["generated_matrix_entries"] = result.get("rows_generated", 0) * len(self.seen_columns)
        result["all_counted_field_ops"] = sum(v for k, v in self.counts.items()
                                                 if "field_" in k)
        return result


def monomial_batches(n, blocks, arm, partial_size):
    mons = sorted(range(1 << n), key=mask_order)
    if arm in ("full_block", "partial_block"):
        block_masks = [sum(1 << i for i in block) for block in blocks]
        group = lambda m: max((m & b).bit_count() for b in block_masks)
    else:
        group = int.bit_count
    groups = defaultdict(list)
    for mon in mons:
        groups[group(mon)].append(mon)
    for level in sorted(groups):
        batch = groups[level]
        if arm.startswith("partial"):
            for start in range(0, len(batch), partial_size):
                yield level, batch[start:start + partial_size]
        else:
            yield level, batch


def extract_models(ring, equations, fixed=None):
    fixed = fixed or {}
    active = [i for i in range(ring.n) if i not in fixed]
    models = []
    term_evaluations = 0
    for choices in itertools.product((0, 1), repeat=len(active)):
        bits = sum(v << i for i, v in fixed.items()) | sum(v << i for i, v in zip(active, choices))
        ok = True
        for poly in equations:
            term_evaluations += len(poly)
            if ring.eval(poly, bits):
                ok = False
                break
        if ok:
            models.append(bits)
    return models, {"root_candidate_assignments": 1 << len(active),
                    "root_term_evaluations": term_evaluations}


def macaulay(ring, equations, blocks, arm, config):
    equations = list(reversed(equations)) if arm == "aa_full_total_reverse_input" else equations
    span = Span(ring, equations)
    history = []
    status = "UNKNOWN"
    models = None
    extraction = {}
    for level, batch in monomial_batches(ring.n, blocks, arm, config["partial_check_batch"]):
        for mon in batch:
            for i in range(len(equations)):
                if span.counts["rows_generated"] >= config["max_rows"]:
                    status = "ROW_CAP"
                    break
                span.insert(i, mon)
            if status == "ROW_CAP":
                break
        history.append({"filtration_level": level, **span.metrics()})
        if 0 in span.basis:
            status, models = "UNSAT", []
            break
        if status == "ROW_CAP":
            break
        if span.is_ideal():
            models, extraction = extract_models(ring, equations)
            status = "SAT_COMPLETE" if models else "UNSAT"
            break
    return {"arm": arm, "status": status, "models": models,
            "equations": [pack(f) for f in equations],
            "basis": span.certificate(), "metrics": {**span.metrics(), **extraction},
            "history": history,
            "scope": "Boolean quotient monomial-multiple span; block filtration is not homogeneous XL"}


def select_cut(equations, n, b, policy, seed):
    """Public syntax only: no solutions, oracle counts, or trial solving."""
    ops = 0
    if policy in ("fixed_block", "aa_fixed_reverse_branches"):
        return list(range(b)), {"selection_operations": b, "selection_basis": "fixed variable order"}
    if policy == "random":
        order = sorted(range(n), key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).digest())
        return order[:b], {"selection_operations": n, "selection_basis": "public SHA256 ordering"}
    if policy == "degree_drop":
        scores = []
        for cut in itertools.combinations(range(n), b):
            cutmask = sum(1 << i for i in cut)
            # Lexicographically minimize the sorted remaining monomial degrees;
            # cancellations and assignments are deliberately not inspected.
            degrees = []
            for eq in equations:
                for mon in eq:
                    ops += 1
                    degrees.append((mon & ~cutmask).bit_count())
            scores.append((tuple(sorted(degrees, reverse=True)), cut))
        return list(min(scores)[1]), {"selection_operations": ops, "selection_basis": "syntactic degree-drop"}
    if policy == "min_fill":
        adj = {i: set() for i in range(n)}
        for eq in equations:
            for mon in eq:
                variables = [i for i in range(n) if mon >> i & 1]
                for i, j in itertools.combinations(variables, 2):
                    adj[i].add(j)
                    adj[j].add(i)
                    ops += 1
        chosen = []
        for _ in range(b):
            candidates = []
            for i, neighbors in adj.items():
                pairs = list(itertools.combinations(neighbors, 2))
                ops += len(pairs)
                candidates.append((sum(v not in adj[u] for u, v in pairs), len(neighbors), i))
            _, _, i = min(candidates)
            chosen.append(i)
            neighbors = adj.pop(i)
            for u, v in itertools.combinations(neighbors, 2):
                adj[u].add(v)
                adj[v].add(u)
            for u in neighbors:
                adj[u].discard(i)
        return chosen, {"selection_operations": ops, "selection_basis": "syntactic min-fill elimination order"}
    raise ValueError(policy)


def affine_candidates(ring, span, active, free_cap):
    linear = [row for row, _ in span.basis.values()
              if all(mon.bit_count() <= 1 for mon in row)]
    # Independently form an RREF of just affine consequences. This second
    # elimination is charged, and no nonlinear row is treated as linear.
    rows = [dict(f) for f in linear]
    pivots = []
    cursor = 0
    for var in active:
        key = 1 << var
        found = next((j for j in range(cursor, len(rows)) if rows[j].get(key)), None)
        if found is None:
            continue
        rows[cursor], rows[found] = rows[found], rows[cursor]
        inv = pow(rows[cursor][key], -1, ring.p)
        span.counts["field_inversions"] += 1
        span.counts["field_muls"] += len(rows[cursor])
        rows[cursor] = {m: c * inv % ring.p for m, c in rows[cursor].items()}
        for j in range(len(rows)):
            if j != cursor and rows[j].get(key):
                span.update(rows[j], rows[cursor], -rows[j][key] % ring.p)
        pivots.append(var)
        cursor += 1
    if any(set(row) == {0} for row in rows):
        return [], 0
    free = [i for i in active if i not in pivots]
    if len(free) > free_cap:
        return None, len(free)
    candidates = []
    for choices in itertools.product((0, 1), repeat=len(free)):
        values = dict(zip(free, choices))
        valid = True
        for row, pivot in zip(rows, pivots):
            val = (-row.get(0, 0) - sum(row.get(1 << v, 0) * values[v] for v in free)) % ring.p
            span.counts["field_muls"] += len(free)
            span.counts["field_adds"] += len(free) + 1
            if val not in (0, 1):
                valid = False
                break
            values[pivot] = val
        span.counts["affine_candidate_assignments"] += 1
        if valid:
            candidates.append(sum(v << i for i, v in values.items()))
    return candidates, len(free)


def residual(ring, equations, fixed, config):
    polys = [ring.restrict(f, fixed) for f in equations]
    active = [i for i in range(ring.n) if i not in fixed]
    span = Span(ring, polys)
    degree = config["residual_degree_cap"]
    for mon in sorted(range(1 << ring.n), key=mask_order):
        if any(mon >> i & 1 for i in fixed):
            continue
        for i, poly in enumerate(polys):
            # Test the actual reduced product degree. The Boolean quotient
            # is explicit; no ordinary-polynomial degree theorem is implied.
            product = span.multiply_mask(poly, mon)
            if max((m.bit_count() for m in product), default=0) <= degree:
                span.insert(i, mon)
    if 0 in span.basis:
        status, models, free = "UNSAT", [], 0
    else:
        candidates, free = affine_candidates(ring, span, active, config["affine_free_variable_cap"])
        if candidates is None:
            status, models = "UNKNOWN", None
        else:
            models = []
            for bits in candidates:
                span.counts["root_candidate_assignments"] += 1
                span.counts["root_term_evaluations"] += sum(len(f) for f in polys)
                if all(ring.eval(poly, bits) == 0 for poly in polys):
                    models.append(bits | sum(v << i for i, v in fixed.items()))
            status = "SAT_COMPLETE" if models else "UNSAT"
    return {"assignment": [[i, v] for i, v in sorted(fixed.items())], "status": status,
            "models": models, "free_variables": free, "basis": span.certificate(),
            "equations": [pack(f) for f in polys], "metrics": span.metrics()}


def backdoor(ring, equations, blocks, arm, config, seed):
    b = min(config["backdoor_bits"], ring.n)
    cut, selection = select_cut(equations, ring.n, b, arm, seed)
    assignments = list(itertools.product((0, 1), repeat=b))
    if arm == "aa_fixed_reverse_branches":
        assignments.reverse()
    branches = [residual(ring, equations, dict(zip(cut, values)), config) for values in assignments]
    metrics = defaultdict(int)
    for branch in branches:
        for key, val in branch["metrics"].items():
            metrics[key] += val
    metrics.update(selection)
    complete = all(branch["status"] != "UNKNOWN" for branch in branches)
    return {"arm": arm, "cut": cut, "strong_backdoor": complete,
            "status": "COMPLETE" if complete else "UNKNOWN",
            "legal_assignments": 1 << b, "checked_assignments": len(branches),
            "models": sorted(x for branch in branches for x in (branch["models"] or [])) if complete else None,
            "branches": branches, "metrics": dict(metrics)}


def make_fixtures(config):
    for p, s, target in itertools.product(config["primes"], config["digits"], config["targets"]):
        f = generate_s3(p, s, target, **config["curve"], curve_membership=False)
        for population in config["populations"]:
            polys = f["polynomials"]
            label = f"{population}-p{p}-s{s}-r{target}"
            if population == "matched_support_null":
                polys = [{m: 1 + int.from_bytes(hashlib.sha256(
                    f"{config['null_seed']}:{label}:{i}:{m}".encode()).digest(), "big") % (p - 1)
                          for m in poly} for i, poly in enumerate(polys)]
            yield label, population, f["ring"], polys, f["variable_blocks"], f.get("metadata", {})
    for p in config["primes"]:
        ring = BoolRing(4, p)
        yield f"affine-unsat-p{p}", "affine_unsat", ring, [{1: 1}, {0: p - 1, 1: 1}], [[0, 1], [2, 3]], {}
        # z is deliberately last; syntax policy can see it without a witness.
        ring = BoolRing(7, p)
        polys = []
        for i in range(3):
            x, y, z = 1 << i, 1 << (i + 3), 1 << 6
            polys.extend([{x: 1, y: 1, 0: p - 1}, {x | z: 1, y: 1, y | z: p - 1}])
        yield f"gate-backdoor-p{p}", "planted_gate_backdoor", ring, polys, [list(range(3)), list(range(3, 7))], {"known_backdoor": [6]}


def run(config, checkpoint_dir=None):
    cells = []
    if checkpoint_dir is not None:
        checkpoint_dir = Path(checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
    for label, population, ring, equations, blocks, metadata in make_fixtures(config):
        if ring.n > config["max_variables"]:
            raise ValueError("variable cap")
        # Oracle runs after the solver arms and never enters their arguments.
        lead3 = [macaulay(ring, equations, blocks, arm, config) for arm in config["lead3_arms"]]
        lead4 = [backdoor(ring, equations, blocks, arm, config, f"{config['null_seed']}:{label}")
                 for arm in config["lead4_arms"]]
        oracle, oracle_counts = extract_models(ring, equations)
        cells.append({"id": label, "population": population, "p": ring.p, "n": ring.n,
                      "equations": [pack(f) for f in equations], "blocks": blocks, "metadata": metadata,
                      "lead3": lead3, "lead4": lead4, "oracle_models": oracle,
                      "oracle_metrics": oracle_counts})
        if checkpoint_dir is not None:
            checkpoint = checkpoint_dir / (label + ".json")
            temporary = checkpoint.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(cells[-1], sort_keys=True, separators=(",", ":")) + "\n")
            temporary.replace(checkpoint)
        print(json.dumps({"algebra_cell_completed": label, "cells_completed": len(cells)}), file=sys.stderr, flush=True)
    try:
        from .source_calibration import run_calibration
    except ImportError:
        from source_calibration import run_calibration
    return {"schema": "prime-sat-algebra-result/v1", "config": config, "cells": cells,
            "source_calibration": run_calibration(config["source_calibration"]),
            "scope": config["scope"], "scientific_status": "unreviewed exact toy instrument output"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--checkpoint-dir")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    result = run(config, args.checkpoint_dir)
    Path(args.output).write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"output": args.output, "cells": len(result["cells"])}))


if __name__ == "__main__":
    main()
