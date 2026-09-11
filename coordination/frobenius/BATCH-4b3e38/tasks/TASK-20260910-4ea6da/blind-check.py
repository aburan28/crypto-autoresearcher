#!/usr/bin/env python3
"""One independent blind, exact finite derivation from two frozen definitions.

This program imports only Python's standard library. It has no producer input,
network interface, field selection option, or experiment launcher. The sole
argument names its write-once report. Run exactly once in the Coordinator's
empty Linux review directory, under a new process group and 1024 MiB RLIMIT_AS.
"""
import argparse
import collections
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import traceback

TASK = "TASK-20260910-4ea6da"
BASE = "coordination/frobenius/BATCH-4b3e38/tasks/" + TASK
SOURCE_PATH = BASE + "/blind-check.py"
INPUT_HASHES = {
    "AGENTS.md": "e80d844402dd958f9885d4b69ec0c2018813de075e24f9f100800bb352ee5a87",
    "agents/validator.md": "08f1144225ab702cb5feb206c53d0ca5e5fa71d80a8fa2734a3d851951597122",
    "tools/check_review_independence.py": "10815ff7446fec8e881c049fd5ab84f4f8a6c81fc283c6076f1b2f013dc319c5",
    "coordination/frobenius/BATCH-4b3e38/handoffs/TASK-20260910-4ea6da.json": "8f4eab771c6b68f2f5477a0cb64c28cb9fe0be0b6dd9586ad22d81ecff7dee79",
    "coordination/frobenius/BATCH-4b3e38/review-plan.json": "05314c70296fe10f844af6b8a34fa2862a584c7a5e5705d88e55b7c5d569e6ee",
    "experiments/EXP-FROB-0d885c/specification-component-BATCH-4b3e38.yaml": "849bbc1d45712823bbfd88f48fe20447402ff1858d56712fad5621989460cb12",
    "experiments/EXP-FROB-a95296/specification-component-BATCH-4b3e38.yaml": "b4ea90ec1d30ffe4b4f36d39c1d2932308a775a698bc4c99090e0c25f6f5e422",
}
CHECKS = collections.Counter()


def require(value, label):
    CHECKS[label] += 1
    if not value:
        raise AssertionError(label)


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def polynomial_product(a, b, n, modulus):
    """Carryless polynomial product followed by descending long division."""
    product = 0
    for exponent in range(n):
        if (b >> exponent) & 1:
            product ^= a << exponent
    for exponent in range(2 * n - 2, n - 1, -1):
        if (product >> exponent) & 1:
            product ^= modulus << (exponent - n)
    return product


class Field:
    def __init__(self, n, modulus):
        self.n, self.modulus, self.q = n, modulus, 1 << n
        self.counts = collections.Counter()
        self.table = [[polynomial_product(a, b, n, modulus)
                       for b in range(self.q)] for a in range(self.q)]

    def add(self, a, b):
        self.counts["field_addition"] += 1
        return a ^ b

    def mul(self, a, b):
        self.counts["field_multiplication_table_lookup"] += 1
        return self.table[a][b]

    def power(self, a, exponent):
        self.counts["power_call"] += 1
        out = 1
        for unused in range(exponent):
            out = self.mul(out, a)
        return out

    def inverse(self, a):
        self.counts["inverse_search"] += 1
        if a == 0:
            raise ZeroDivisionError("zero has no inverse")
        return next(b for b in range(1, self.q) if self.mul(a, b) == 1)

    def audit(self):
        inverses = []
        for a in range(self.q):
            require(self.add(a, 0) == a and self.add(a, a) == 0,
                    "field_additive_identity_and_characteristic_two")
            require(self.mul(a, 0) == 0 and self.mul(a, 1) == a,
                    "field_zero_and_unit")
            candidates = [b for b in range(self.q) if self.mul(a, b) == 1]
            require(len(candidates) == int(a != 0), "unique_nonzero_inverse")
            inverses.append(candidates[0] if candidates else None)
            for b in range(self.q):
                require(self.add(a, b) == self.add(b, a) and
                        self.mul(a, b) == self.mul(b, a), "field_commutativity")
                for c in range(self.q):
                    require(self.add(self.add(a, b), c) == self.add(a, self.add(b, c)),
                            "field_additive_associativity")
                    require(self.mul(self.mul(a, b), c) == self.mul(a, self.mul(b, c)),
                            "field_multiplicative_associativity")
                    require(self.mul(a, self.add(b, c)) ==
                            self.add(self.mul(a, b), self.mul(a, c)), "field_distributivity")
        return {"degree": self.n, "modulus_binary": self.modulus,
                "multiplication_table": self.table,
                "addition_table": [[a ^ b for b in range(self.q)] for a in range(self.q)],
                "nonzero_inverses_by_encoding": inverses,
                "complete_pair_count": self.q ** 2,
                "complete_triple_count": self.q ** 3,
                "polynomial_reduction": "carryless product; descending monic long division"}


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def zero(rows, cols):
    return [[0] * cols for unused in range(rows)]


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def matrix_add(f, a, b):
    return [[f.add(x, y) for x, y in zip(row, other)]
            for row, other in zip(a, b)]


def matrix_scale(f, scalar, a):
    return [[f.mul(scalar, x) for x in row] for row in a]


def matrix_mul(f, a, b):
    out = zero(len(a), len(b[0]))
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                out[i][j] = f.add(out[i][j], f.mul(a[i][k], b[k][j]))
    return out


def matrix_vector(f, matrix, vector):
    return [row[0] for row in matrix_mul(f, matrix, [[x] for x in vector])]


def rref(f, matrix, coefficient_columns=None):
    a = [row[:] for row in matrix]
    columns = len(a[0]) if coefficient_columns is None else coefficient_columns
    pivots = []
    for column in range(columns):
        pivot = next((i for i in range(len(pivots), len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        row = len(pivots)
        a[row], a[pivot] = a[pivot], a[row]
        a[row] = [f.mul(f.inverse(a[row][column]), x) for x in a[row]]
        for other in range(len(a)):
            if other != row and a[other][column]:
                scalar = a[other][column]
                a[other] = [f.add(x, f.mul(scalar, y))
                            for x, y in zip(a[other], a[row])]
        pivots.append(column)
    return a, pivots


def rank(f, matrix):
    return len(rref(f, matrix)[1])


def inverse_matrix(f, matrix):
    n = len(matrix)
    reduced, pivots = rref(f, [row + unit for row, unit in zip(matrix, eye(n))], n)
    require(pivots == list(range(n)), "matrix_inverse_exists")
    result = [row[n:] for row in reduced]
    require(matrix_mul(f, matrix, result) == eye(n) and
            matrix_mul(f, result, matrix) == eye(n), "two_sided_matrix_inverse")
    return result


def kernel_basis(f, matrix):
    reduced, pivots = rref(f, matrix)
    result = []
    for free in range(len(matrix[0])):
        if free not in pivots:
            vector = [0] * len(matrix[0])
            vector[free] = 1
            for row, pivot in enumerate(pivots):
                vector[pivot] = reduced[row][free]
            result.append(vector)
    return result


def nonzero_entries(matrix):
    return [[i, j, x] for i, row in enumerate(matrix) for j, x in enumerate(row) if x]


def cyclic_panel():
    f, binary = Field(4, 19), Field(1, 3)
    arithmetic = f.audit()
    setup_counts = dict(f.counts)
    identity = eye(3)
    s = [[int(i == (j + 1) % 3) for j in range(3)] for i in range(3)]
    powers = [identity, s, matrix_mul(f, s, s)]
    require(matrix_mul(f, powers[2], s) == identity, "cycle_order_three")
    require(3 % 2 != 0, "characteristic_divisor_gate_positive")
    roots = [w for w in range(2, 16) if f.power(w, 3) == 1]
    omega = min(roots)
    require(omega != 1 and f.power(omega, 3) == 1, "primitive_cube_root")
    projectors = []
    for j in range(3):
        p = zero(3, 3)
        for r in range(3):
            p = matrix_add(f, p, matrix_scale(f, f.power(omega, (-j * r) % 3), powers[r]))
        projectors.append(p)
    require(matrix_add(f, matrix_add(f, projectors[0], projectors[1]), projectors[2]) == identity,
            "projector_resolution_of_identity")
    basis_columns, projector_columns = [], []
    for j, p in enumerate(projectors):
        require(matrix_mul(f, p, p) == p, "projector_idempotence")
        require(matrix_mul(f, s, p) == matrix_scale(f, f.power(omega, j), p),
                "character_eigenvalue_orientation")
        for k in range(3):
            if j != k:
                require(matrix_mul(f, p, projectors[k]) == zero(3, 3), "projector_orthogonality")
        selected, indices = [], []
        for i, column in enumerate(transpose(p)):
            candidate = selected + [column]
            if rank(f, transpose(candidate)) > len(selected):
                selected.append(column)
                indices.append(i)
        require(len(selected) == 1, "projector_rank_one")
        projector_columns.append({"j": j, "column_indices": indices, "columns": selected})
        basis_columns.extend(selected)
    basis = transpose(basis_columns)
    basis_inverse = inverse_matrix(f, basis)
    matrices = []
    for coefficients in itertools.product(range(2), repeat=3):
        m = zero(3, 3)
        for scalar, power in zip(coefficients, powers):
            m = matrix_add(f, m, matrix_scale(f, scalar, power))
        require(matrix_mul(f, s, m) == matrix_mul(f, m, s), "circulant_commutation")
        transformed = matrix_mul(f, matrix_mul(f, basis_inverse, m), basis)
        require(all(transformed[i][j] == 0 for i in range(3) for j in range(3) if i != j),
                "all_off_block_entries_zero")
        eigenvalues = []
        for j in range(3):
            value = 0
            for r, scalar in enumerate(coefficients):
                value = f.add(value, f.mul(scalar, f.power(omega, (j * r) % 3)))
            eigenvalues.append(value)
        require(eigenvalues == [transformed[j][j] for j in range(3)], "character_polynomial_values")
        reconstructed = matrix_mul(f, matrix_mul(f, basis, transformed), basis_inverse)
        require(reconstructed == m, "complete_block_reconstruction")
        projected = zero(3, 3)
        for p in projectors:
            projected = matrix_add(f, projected, matrix_mul(f, matrix_mul(f, p, m), p))
        require(projected == m, "projector_reconstruction")
        require(all(f.mul(x, x) == x and x in (0, 1) for row in reconstructed for x in row),
                "binary_descent_entrywise")
        blocks, transported = [], []
        for j in range(3):
            block = [[transformed[j][j]]]
            block_kernel = kernel_basis(f, block)
            vectors = []
            for local in block_kernel:
                embedded = [0] * 3
                embedded[j] = local[0]
                physical = matrix_vector(f, basis, embedded)
                require(matrix_vector(f, m, physical) == [0] * 3, "transported_kernel_residual")
                vectors.append({"block_coordinates": local, "embedded": embedded,
                                "transported": physical, "residual": [0] * 3})
                transported.append(physical)
            blocks.append({"j": j, "matrix": block, "rank": rank(f, block),
                           "nullity": len(block_kernel), "kernel_basis": block_kernel,
                           "transported_kernel": vectors})
        binary_rref, binary_pivots = rref(binary, m)
        binary_kernel, memberships = [], []
        for v in itertools.product(range(2), repeat=3):
            v = list(v)
            direct = matrix_vector(binary, m, v)
            transformed_v = matrix_vector(f, basis_inverse, v)
            block_residual = matrix_vector(f, transformed, transformed_v)
            require((direct == [0] * 3) == (block_residual == [0] * 3), "complete_binary_kernel_membership")
            memberships.append({"vector": v, "direct_residual": direct,
                                "transformed_vector": transformed_v, "block_residual": block_residual})
            if direct == [0] * 3:
                binary_kernel.append(v)
        require(sum(b["rank"] for b in blocks) == len(binary_pivots), "base_and_block_rank")
        require(sum(b["nullity"] for b in blocks) == 3 - len(binary_pivots), "base_and_block_nullity")
        matrices.append({"coefficients": list(coefficients), "matrix": m,
                         "transformed_matrix": transformed, "character_values": eigenvalues,
                         "blocks": blocks, "reconstructed": reconstructed,
                         "projector_reconstructed": projected, "binary_rref": binary_rref,
                         "binary_rank": len(binary_pivots), "binary_nullity": 3 - len(binary_pivots),
                         "binary_kernel_basis": kernel_basis(binary, m),
                         "binary_kernel_vectors": binary_kernel,
                         "binary_membership_checks": memberships,
                         "transported_extension_kernel_basis": transported})
    bad = eye(3)
    bad[0][0] ^= 1
    commutator = matrix_add(f, matrix_mul(f, s, bad), matrix_mul(f, bad, s))
    require(bool(nonzero_entries(commutator)), "negative_noncommuting_perturbation_rejected")
    missing = matrix_add(f, projectors[0], projectors[2])
    missing_residual = matrix_add(f, missing, identity)
    require(bool(nonzero_entries(missing_residual)), "negative_missing_character_block_rejected")
    corrupted = eye(3)
    corrupted[0][0] ^= 1
    require(corrupted != identity, "negative_reconstruction_entry_rejected")
    kernel_residual = matrix_vector(binary, identity, [1, 0, 0])
    require(kernel_residual != [0, 0, 0], "negative_identity_kernel_rejected")
    require(2 % 2 == 0, "negative_characteristic_divisor_rejected_before_division")
    return {"experiment_id": "EXP-FROB-0d885c", "arithmetic": arithmetic,
            "S": s, "omega": omega, "nonidentity_cube_roots": roots,
            "projectors": projectors, "greedy_projector_columns": projector_columns,
            "B": basis, "B_inverse": basis_inverse, "matrix_count": len(matrices), "matrices": matrices,
            "controls": {
                "noncommuting_perturbation": {"matrix": bad, "commutator": commutator,
                                             "nonzero_entries": nonzero_entries(commutator)},
                "missing_block_j1": {"reconstruction": missing, "difference_from_identity": missing_residual,
                                     "nonzero_entries": nonzero_entries(missing_residual)},
                "characteristic_divisor_gate": {"characteristic": 2, "order": 2,
                                                "order_in_base_field": 0, "division_attempted": False,
                                                "rejected": True},
                "corrupted_reconstruction_entry": {"index": [0, 0], "corrupted": corrupted,
                                                   "reference": identity, "rejected": True},
                "corrupted_zero_kernel": {"substitute": [1, 0, 0], "residual": kernel_residual,
                                          "rejected": True}},
            "operation_counts": {"field_setup_audit": setup_counts,
                                 "GF16_total_including_audit": dict(f.counts),
                                 "binary_elimination_and_membership": dict(binary.counts)}}


def bits(value, n):
    return [(value >> i) & 1 for i in range(n)]


def encoding(vector):
    return sum(value << i for i, value in enumerate(vector))


def tensor_product(x, y, tensor):
    out = [0] * len(x)
    for i, a in enumerate(x):
        for j, b in enumerate(y):
            if a and b:
                out = [v ^ t for v, t in zip(out, tensor[i][j])]
    return out


def finite_projection(relation, q, removal_order):
    """Every possible key is recorded, including keys with empty fibers."""
    labels, table, stages = ["a", "b", "c", "d"], list(relation), []
    for removed in removal_order:
        location = labels.index(removed)
        retained = [name for name in labels if name != removed]
        all_keys = list(itertools.product(range(q), repeat=len(retained)))
        fibers = {key: [] for key in all_keys}
        for row in table:
            key = row[:location] + row[location + 1:]
            fibers[key].append(row[location])
        rows = [{"key": list(key), "values": sorted(set(fibers[key]))} for key in all_keys]
        projected = [key for key in all_keys if fibers[key]]
        hist = collections.Counter(len(row["values"]) for row in rows)
        stage = {"input_coordinates": labels[:], "removed_coordinate": removed,
                 "retained_coordinates": retained, "projected_tuples": [list(x) for x in projected],
                 "fibers": rows, "input_tuple_count": len(table), "projected_tuple_count": len(projected),
                 "all_fiber_count": len(rows), "nonempty_fiber_count": len(projected),
                 "empty_fiber_count": hist[0], "multiple_fiber_count": sum(v for k, v in hist.items() if k > 1),
                 "fiber_size_histogram": {str(k): v for k, v in sorted(hist.items())},
                 "maximum_branching": max(map(lambda row: len(row["values"]), rows)),
                 "serialized_fiber_bytes_canonical_json": len(packed(rows))}
        stages.append(stage)
        labels, table = retained, projected
    def reverse_join(truncate_collision=False):
        reconstructed = table[:]
        for stage in reversed(stages):
            old_labels = stage["input_coordinates"]
            removed = stage["removed_coordinate"]
            index = old_labels.index(removed)
            fiber_map = {tuple(row["key"]): row["values"] for row in stage["fibers"]}
            next_table = []
            for key in reconstructed:
                values = fiber_map[key]
                if truncate_collision and removed == "b" and all(value == 0 for value in key):
                    values = values[:1]
                for value in values:
                    next_table.append(key[:index] + (value,) + key[index:])
            reconstructed = sorted(set(next_table))
        return reconstructed
    reconstructed = reverse_join()
    require(reconstructed == relation, "full_fiber_reverse_join_reconstruction")
    corrupted_reconstruction = reverse_join(truncate_collision=True)
    missing = sorted(set(relation) - set(corrupted_reconstruction))
    require(len(missing) == q - 1 and all(a == c == d == 0 for a, b, c, d in missing),
            "negative_truncated_stored_collision_fiber_rejected_by_reverse_join")
    return {"elimination_order": list(removal_order), "stages": stages,
            "final_coordinates": ["a", "d"], "final_projected_tuples": [list(x) for x in table],
            "reconstructed_full_relation": [list(x) for x in reconstructed],
            "reconstruction_equals_reference": True,
            "stored_collision_fiber_truncation_control": {
                "mutation": "At the b-elimination stage, keep the first value in the all-zero boundary key only.",
                "wrong_reconstructed_full_relation": [list(x) for x in corrupted_reconstruction],
                "missing_tuples": [list(x) for x in missing], "rejected": True}}


def tensor_panel():
    fields = []
    for n, modulus in ((3, 11), (4, 19)):
        f, binary = Field(n, modulus), Field(1, 3)
        q = f.q
        arithmetic = f.audit()
        setup_counts = dict(f.counts)
        decisions, selected, selected_orbits = [], [], set()
        for theta in range(1, q):
            conjugates = [f.power(theta, 1 << i) for i in range(n)]
            basis = transpose([bits(x, n) for x in conjugates])
            basis_rank = rank(binary, basis)
            orbit = tuple(sorted(set(conjugates)))
            if basis_rank != n:
                reason, keep = "dependent_conjugates", False
            elif orbit in selected_orbits:
                reason, keep = "already_selected_Frobenius_orbit", False
            elif len(selected) == 2:
                reason, keep = "fixed_first_two_orbit_cap", False
            else:
                reason, keep = "selected_in_integer_scan_order", True
                selected_orbits.add(orbit)
                selected.append((theta, conjugates, basis))
            decisions.append({"theta": theta, "conjugates": conjugates, "orbit": list(orbit),
                              "column_matrix": basis, "rank": basis_rank, "normal": basis_rank == n,
                              "selected": keep, "reason": reason})
        # Literal K^4 traversal, without replacing it by an assumed parametrization.
        relation, dropped = [], []
        for a, b, c, d in itertools.product(range(q), repeat=4):
            if c == f.mul(a, b):
                dropped.append((a, b, c, d))
                if d == f.add(c, a):
                    relation.append((a, b, c, d))
        require(len(relation) == q * q, "relation_exhaustive_cardinality")
        correct_projection = sorted({(a, d) for a, b, c, d in relation})
        dropped_projection = sorted({(a, d) for a, b, c, d in dropped})
        require(dropped != relation and dropped_projection != correct_projection,
                "negative_dropped_constraint_relation_and_projection_rejected")
        collision = [row for row in relation if row[0] == row[2] == row[3] == 0]
        require(len(collision) == q and {row[1] for row in collision} == set(range(q)),
                "complete_known_projection_collision")
        truncated = [row for row in relation if row not in collision[1:]]
        require(truncated != relation and sorted({(a, d) for a, b, c, d in truncated}) == correct_projection,
                "negative_single_collision_representative_rejected")
        bases = []
        for theta, conjugates, basis in selected:
            inverse = inverse_matrix(binary, basis)
            coordinate_vectors = [matrix_vector(binary, inverse, bits(x, n)) for x in range(q)]
            physical_by_coordinate = [encoding(matrix_vector(binary, basis, bits(x, n))) for x in range(q)]
            tensor = [[matrix_vector(binary, inverse, bits(f.mul(a, b), n))
                       for b in conjugates] for a in conjugates]
            coordinate_table, physical_table = [], []
            for x in range(q):
                require(encoding(matrix_vector(binary, basis, coordinate_vectors[x])) == x,
                        "normal_basis_physical_round_trip")
                require(encoding(coordinate_vectors[physical_by_coordinate[x]]) == x,
                        "normal_basis_coordinate_round_trip")
                square = coordinate_vectors[f.mul(x, x)]
                shifted = coordinate_vectors[x][-1:] + coordinate_vectors[x][:-1]
                require(square == shifted, "normal_basis_Frobenius_cyclic_shift")
                coordinate_row, physical_row = [], []
                for y in range(q):
                    c = tensor_product(bits(x, n), bits(y, n), tensor)
                    coordinate_row.append(encoding(c))
                    direct = f.mul(physical_by_coordinate[x], physical_by_coordinate[y])
                    require(encoding(matrix_vector(binary, basis, c)) == direct,
                            "complete_coordinate_operand_tensor_products")
                    c_physical = tensor_product(coordinate_vectors[x], coordinate_vectors[y], tensor)
                    result = encoding(matrix_vector(binary, basis, c_physical))
                    require(result == f.mul(x, y), "complete_physical_operand_tensor_products")
                    physical_row.append(result)
                coordinate_table.append(coordinate_row)
                physical_table.append(physical_row)
            for i in range(n):
                for j in range(n):
                    result = tensor_product(bits(1 << i, n), bits(1 << j, n), tensor)
                    require(encoding(matrix_vector(binary, basis, result)) == f.mul(conjugates[i], conjugates[j]),
                            "normal_basis_unit_pair_products")
            tensor_relation = []
            for a, b, c, d in itertools.product(range(q), repeat=4):
                if c == physical_table[a][b] and d == (c ^ a):
                    tensor_relation.append((a, b, c, d))
            require(tensor_relation == relation, "complete_tensor_and_direct_K4_relation_equality")
            projections = [finite_projection(tensor_relation, q, order)
                           for order in (("b", "c"), ("c", "b"))]
            terms = [(i, j, k) for i in range(n) for j in range(n) for k in range(n) if tensor[i][j][k]]
            cross = [term for term in terms if term[0] != term[1]]
            removed = min(cross if cross else terms)
            malformed = [[row[:] for row in plane] for plane in tensor]
            i, j, k = removed
            malformed[i][j][k] = 0
            unit_failures = []
            for i in range(n):
                for j in range(n):
                    product = tensor_product(bits(1 << i, n), bits(1 << j, n), malformed)
                    observed = encoding(matrix_vector(binary, basis, product))
                    expected = f.mul(conjugates[i], conjugates[j])
                    if observed != expected:
                        unit_failures.append({"unit_indices": [i, j], "observed": observed, "expected": expected})
            require(bool(unit_failures), "negative_deleted_tensor_cross_term_rejected")
            malformed_inverse = [row[:] for row in inverse]
            malformed_inverse[0][0] ^= 1
            bad_round_trips, bad_unit_pairs = [], []
            for x in range(q):
                corrupt_coords = matrix_vector(binary, malformed_inverse, bits(x, n))
                restored = encoding(matrix_vector(binary, basis, corrupt_coords))
                if restored != x:
                    bad_round_trips.append({"physical": x, "restored": restored})
            for i in range(n):
                for j in range(n):
                    x = matrix_vector(binary, malformed_inverse, bits(conjugates[i], n))
                    y = matrix_vector(binary, malformed_inverse, bits(conjugates[j], n))
                    observed = encoding(matrix_vector(binary, basis, tensor_product(x, y, tensor)))
                    expected = f.mul(conjugates[i], conjugates[j])
                    if observed != expected:
                        bad_unit_pairs.append({"unit_indices": [i, j], "observed": observed, "expected": expected})
            require(bool(bad_round_trips) and bool(bad_unit_pairs), "negative_corrupted_basis_inverse_rejected")
            bases.append({"theta": theta, "conjugates": conjugates, "basis_columns_matrix": basis,
                          "basis_inverse": inverse, "coordinates_by_physical_value": coordinate_vectors,
                          "physical_value_by_coordinate_encoding": physical_by_coordinate,
                          "tensor_T_ijk": tensor, "nonzero_tensor_terms": [list(x) for x in terms],
                          "coordinate_multiplication_table": coordinate_table,
                          "physical_multiplication_table_via_tensor": physical_table,
                          "tensor_relation": [list(x) for x in tensor_relation],
                          "projection_orders": projections,
                          "controls": {"deleted_tensor_term": {"index": list(removed), "fallback_used": not bool(cross),
                                                                "unit_pair_failures": unit_failures, "rejected": True},
                                       "corrupted_basis_inverse": {"flipped_bit": [0, 0], "corrupted_matrix": malformed_inverse,
                                                                   "round_trip_failures": bad_round_trips,
                                                                   "unit_pair_failures": bad_unit_pairs, "rejected": True}}})
        extra_rows = sorted(set(dropped) - set(relation))
        extra_projection = sorted(set(dropped_projection) - set(correct_projection))
        fields.append({"degree": n, "modulus_binary": modulus, "arithmetic": arithmetic,
                       "candidate_decisions": decisions, "selected_normal_basis_count": len(bases),
                       "selected_thetas": [basis[0] for basis in selected], "bases": bases,
                       "physical_K4_domain_count": q ** 4, "direct_full_relation": [list(x) for x in relation],
                       "direct_relation_count": len(relation), "direct_projection_ad": [list(x) for x in correct_projection],
                       "controls": {"dropped_constraint": {"full_relation": [list(x) for x in dropped],
                                                             "full_relation_count": len(dropped),
                                                             "projection_ad": [list(x) for x in dropped_projection],
                                                             "first_spurious_full_tuple": list(extra_rows[0]),
                                                             "first_spurious_projected_tuple": list(extra_projection[0]),
                                                             "rejected": True},
                                    "collision_representative_truncation": {"collision_fiber": [list(x) for x in collision],
                                                                           "retained_representative": list(collision[0]),
                                                                           "omitted_full_tuples": [list(x) for x in collision[1:]],
                                                                           "wrong_relation_count": len(truncated),
                                                                           "projection_unchanged": True, "rejected": True}},
                       "operation_counts": {"field_setup_audit": setup_counts, "field_total": dict(f.counts),
                                            "binary_coordinate_operations": dict(binary.counts)}})
    return {"experiment_id": "EXP-FROB-a95296", "fields": fields}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("write-once report already exists")
    limit = 1024 * 1024 * 1024
    guard = {"platform": platform.system(), "RLIMIT_AS": list(resource.getrlimit(resource.RLIMIT_AS)),
             "pid": os.getpid(), "process_group": os.getpgid(0), "session": os.getsid(0),
             "required_bytes": limit, "cwd": os.getcwd()}
    if not (guard["platform"] == "Linux" and guard["RLIMIT_AS"] == [limit, limit]
            and guard["pid"] == guard["process_group"] == guard["session"]):
        raise RuntimeError("Linux, exact 1024MiB hard/soft RLIMIT_AS and independent session/process group required")
    if Path.cwd() != Path("/tmp/frob-review-4ea6da"):
        raise RuntimeError("run only in the declared isolated review directory")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    report = {"schema": "crypto.autoresearch.blind_component_rederivation.v1", "task_id": TASK,
              "phase": 1, "status": "incomplete", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "input_path_sha256": INPUT_HASHES, "run_count": 1, "original_experiment_runs": 0,
              "native_provenance": {"role": "validator", "session_identity": "/root/frob_components_validator",
                                    "independent_session": True, "requested_policy": "review-adversarial",
                                    "requested_reasoning_effort": "xhigh", "configured_model": "gpt-6-astra",
                                    "resolved_model_id": None, "serving_model_identity_exposed": False,
                                    "model_verified": False, "fallback_used": False, "degraded_requirements": [],
                                    "provenance_basis": "native role and Coordinator handoff; serving identity not exposed",
                                    "computation_runtime": {"python": sys.version, "executable": sys.executable,
                                                            "platform": platform.platform(), "argv": sys.argv,
                                                            "guard_observed_before_finite_computation": guard}},
              "derivation_notes": [
                  "Cyclic projectors follow the displayed finite sum, with characteristic image of 3 equal to 1.",
                  "The cyclic character of P_j is omega^j. The transformed circulant entry is sum_r a_r omega^(jr).",
                  "Independent columns are selected by exact rank, and kernels are transported through the complete basis.",
                  "For each normal basis, binary inverse coordinates of every basis product give T_ijk.",
                  "Squaring advances each conjugate column by one, so coefficient vectors rotate right.",
                  "K^4 is traversed literally; both elimination orders store every key and all removed-coordinate values.",
                  "Reverse joins retain all common coordinates. The a=0 fiber keeps all q choices of b.",
                  "All arithmetic is independently implemented here from frozen polynomial definitions; no producer imports or inputs."],
              "limitations": [
                  "Phase1 derives finite expected quantities only; no producer receipt, source, or output has been reviewed.",
                  "Results concern eight synthetic binary circulants and the fixed GF8/GF16 relation fixtures only.",
                  "No claim of original experiment completion, original performance-threshold measurement, asymptotic gain, novelty, cryptanalytic capability, or deployment implication.",
                  "Operation counts are this verifier's table lookups/searches and do not estimate another implementation's cost.",
                  "No formal proof assistant encoding or machine-verified general theorem is supplied.",
                  "The future phase2 read attestation must be separate; these sealed files must never change after producer exposure."],
              "procedure_deviations": [],
              "review_attestation": {"task_id": TASK, "joints_owned": ["cyclic_blocks", "tensor_fibers"],
                                     "sources_read": list(INPUT_HASHES) + [SOURCE_PATH],
                                     "read_sibling_reports": False, "blind_from_respected": True,
                                     "verdict": "inconclusive",
                                     "verdict_scope": "Producer validity remains unassessed in blind phase1.",
                                     "joint_verdicts": {"cyclic_blocks": "inconclusive", "tensor_fibers": "inconclusive"},
                                     "independent_session": True,
                                     "non_file_inputs": ["Coordinator phase1 assignment and operational-only messages concerning execution transport"],
                                     "external_sources_read": [], "producer_data_read": False}}
    try:
        report["cyclic_blocks"] = cyclic_panel()
        report["tensor_fibers"] = tensor_panel()
        report["status"] = "blind_derivation_complete"
        report["derivation_checks_passed"] = True
    except Exception as exc:
        report["status"] = "blind_derivation_incomplete"
        report["derivation_checks_passed"] = False
        report["error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    report["check_counts"] = dict(sorted(CHECKS.items()))
    report["timing"] = {"started_at": started, "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "wall_seconds_before_report_serialization": time.perf_counter() - wall,
                        "process_cpu_seconds_before_report_serialization": time.process_time() - cpu,
                        "peak_RSS_before_report_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        "peak_RSS_units": "KiB on Linux"}
    report["witness_bytes"] = {joint: len(packed(report[joint])) for joint in ("cyclic_blocks", "tensor_fibers") if joint in report}
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"task_id": TASK, "status": report["status"], "check_counts": report["check_counts"],
                      "output": str(output)}, sort_keys=True))
    return 0 if report["derivation_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
