"""Quadratic-chain linearization. No FLINT import or arithmetic on import."""
from collections import Counter
import hashlib
import itertools
import math


def scalar_columns(depth, terminal, p):
    size = 1 << depth

    def multiply_variable(index, mask):
        bit = 1 << index
        if not mask & bit:
            return {mask | bit: 1}
        reduced = mask ^ bit
        if index == depth - 1:
            return {reduced: (terminal + 2) % p}
        result = {reduced: 2}
        for row, coefficient in multiply_variable(index + 1, reduced).items():
            result[row] = (result.get(row, 0) + coefficient) % p
        return {row: value for row, value in result.items() if value}

    return [multiply_variable(0, mask) for mask in range(size)]


def scalar_powers(columns, maximum, p):
    size = len(columns)
    result = [[{i: 1} for i in range(size)]]
    for _ in range(maximum):
        output = []
        for vector in result[-1]:
            value = {}
            for j, coefficient in vector.items():
                for i, entry in columns[j].items():
                    value[i] = (value.get(i, 0) + coefficient * entry) % p
            output.append({i: entry for i, entry in value.items() if entry})
        result.append(output)
    return result


def matrix_from_columns(columns, rows, context):
    from flint import fmpz_mod_mat
    width = len(columns)
    return fmpz_mod_mat(rows, width, [columns[j].get(i, 0) for i in range(rows) for j in range(width)], context)


def tensor_operator(polynomial, width, alternating, scalar, context, p, counters):
    """Symmetric tensor polynomial action on an ordered or wedge basis."""
    size = len(scalar)
    basis = list(itertools.combinations(range(size), width)) if alternating else list(itertools.product(range(size), repeat=width))
    index = {state: i for i, state in enumerate(basis)}
    maximum = max((max(exponent) for exponent in polynomial), default=0)
    powers = scalar_powers(scalar, maximum, p)
    columns = []
    for state in basis:
        column = {}
        for exponents, coefficient in polynomial.items():
            choices = [powers[exponent][source].items() for exponent, source in zip(exponents, state)]
            for terms in itertools.product(*choices):
                targets = tuple(pair[0] for pair in terms)
                if alternating:
                    if len(set(targets)) != width:
                        counters["alternating_duplicate_terms_discarded"] += 1
                        continue
                    sign = -1 if sum(targets[i] > targets[j] for i in range(width) for j in range(i + 1, width)) & 1 else 1
                    row = index[tuple(sorted(targets))]
                else:
                    sign, row = 1, index[targets]
                value = coefficient * sign
                for _, entry in terms:
                    value = value * entry % p
                column[row] = (column.get(row, 0) + value) % p
                counters["tensor_term_accumulations"] += 1
        columns.append({row: value for row, value in column.items() if value})
    counters["operators_constructed"] += 1
    counters["operator_nonzero_entries"] += sum(len(c) for c in columns)
    return matrix_from_columns(columns, len(basis), context), basis


def fingerprint(matrix, p):
    result = hashlib.sha256()
    result.update(f"{matrix.nrows()}x{matrix.ncols()} mod {p}\n".encode())
    width = (p.bit_length() + 7) // 8
    for j in range(matrix.ncols()):
        for i in range(matrix.nrows()):
            result.update(int(matrix[i, j]).to_bytes(width, "big"))
    return result.hexdigest()


def pivots(rref, rank):
    result = []
    for i in range(rank):
        row = next((j for j in range(rref.ncols()) if rref[i, j]), None)
        if row is None:
            raise AssertionError("RREF rank exceeds nonzero rows")
        result.append(row)
    return result


def right_kernel(matrix, context, p):
    form, rank = matrix.rref()
    pivot_columns = pivots(form, rank)
    free = [j for j in range(matrix.ncols()) if j not in set(pivot_columns)]
    columns = []
    for j in free:
        vector = {j: 1}
        for i, pivot in enumerate(pivot_columns):
            value = -int(form[i, j]) % p
            if value:
                vector[pivot] = value
        columns.append(vector)
    kernel = matrix_from_columns(columns, matrix.ncols(), context)
    product = matrix * kernel
    assert all(not product[i, j] for i in range(product.nrows()) for j in range(product.ncols()))
    assert kernel.ncols() == matrix.ncols() - rank
    return kernel, {"rank": rank, "nullity": len(free), "pivot_columns": pivot_columns,
                    "kernel_columns": [[[i, value] for i, value in sorted(column.items())] for column in columns],
                    "kernel_annihilation_checked": True}


def column_basis(matrix, context):
    form, rank = matrix.rref()
    columns = pivots(form, rank)
    return matrix_from_columns([{i: int(matrix[i, j]) for i in range(matrix.nrows()) if matrix[i, j]} for j in columns], matrix.nrows(), context)


def restrict_operators(kernel, operators, context):
    from flint import fmpz_mod_mat
    dimension = kernel.ncols()
    if not dimension:
        return [], {"dimension": 0, "restriction_identities_checked": True}
    form, rank = kernel.transpose().rref()
    assert rank == dimension
    rows = pivots(form, rank)
    minor = fmpz_mod_mat([[int(kernel[i, j]) for j in range(dimension)] for i in rows], context)
    restricted = []
    for operator in operators:
        image = operator * kernel
        target = fmpz_mod_mat([[int(image[i, j]) for j in range(dimension)] for i in rows], context)
        action = minor.solve(target)
        assert kernel * action == image
        restricted.append(action)
    for left, right in itertools.combinations(restricted, 2):
        assert left * right == right * left
    return restricted, {"dimension": dimension, "independent_kernel_rows": rows,
                        "restriction_identities_checked": True, "restricted_operators_commute": True}


def rational_characters(operators, context, p):
    from flint import fmpz_mod_mat
    from core import ExtractionUnknown
    dimension = operators[0].nrows() if operators else 0
    if not dimension:
        return [], {"dimension": 0, "complete": True}
    bound = 2 * math.comb(dimension, 2)
    if p <= bound:
        raise ExtractionUnknown("Separating-element existence bound does not fit this field")
    identity = fmpz_mod_mat([[int(i == j) for j in range(dimension)] for i in range(dimension)], context)
    for parameter in range(bound + 1):
        separator = operators[0] + parameter * operators[1] + (parameter * parameter % p) * operators[2]
        characteristic = separator.charpoly()
        roots = characteristic.roots()
        if len(roots) != dimension or any(multiplicity != 1 for _, multiplicity in roots):
            continue
        states = []
        for root, _ in roots:
            eigenvectors, record = right_kernel(separator - int(root) * identity, context, p)
            if record["nullity"] != 1:
                raise AssertionError("A squarefree separator has a non-simple eigenspace")
            row = next(i for i in range(dimension) if eigenvectors[i, 0])
            inverse = pow(int(eigenvectors[row, 0]), -1, p)
            state = []
            for operator in operators:
                value = operator * eigenvectors
                coefficient = int(value[row, 0]) * inverse % p
                assert value == coefficient * eigenvectors
                state.append(coefficient)
            states.append(tuple(state))
        assert len(set(states)) == dimension
        return sorted(states), {"dimension": dimension, "separator_parameter": parameter,
                                "parameter_bound_inclusive": bound,
                                "characteristic_coefficients": [int(characteristic[i]) for i in range(dimension + 1)],
                                "squarefree_split_roots": sorted(int(x) for x, _ in roots),
                                "all_joint_eigenidentities_checked": True, "complete": True}
    raise ExtractionUnknown("No completely split separating spectrum was certified")


def solve_stratum(parameters, depth, terminal, target, name):
    from flint import fmpz_mod_ctx
    from core import relation_polynomial
    p = parameters["p"]
    if depth < 1 or terminal in (2, p - 2):
        raise ValueError("Separable generic Dickson fibre required")
    context = fmpz_mod_ctx(p)
    scalar = scalar_columns(depth, terminal, p)
    slots = {"distinct": (0, 1, 2), "twoequal": (0, 0, 1), "allequal": (0, 0, 0)}[name]
    width = max(slots) + 1
    polynomial, elementary = relation_polynomial(parameters, target[0], slots)
    counters = Counter()
    operator, basis = tensor_operator(polynomial, width, name == "distinct", scalar, context, p, counters)
    kernel, kernel_certificate = right_kernel(operator, context, p)
    projection = None
    if name == "twoequal" and kernel.ncols():
        difference, _ = tensor_operator({(1, 0): 1, (0, 1): p - 1}, 2, False, scalar, context, p, counters)
        before = kernel.ncols()
        kernel = column_basis(difference * kernel, context)
        projection = {"pre_projection_dimension": before, "off_diagonal_image_dimension": kernel.ncols(),
                      "method": "image of commuting x-y; removes exactly diagonal eigencharacters"}
    operators = [tensor_operator(poly, width, name == "distinct", scalar, context, p, counters)[0] for poly in elementary]
    restricted, restriction = restrict_operators(kernel, operators, context)
    states, extraction = rational_characters(restricted, context, p)
    assert len(states) == kernel.ncols()
    return {"stratum": name, "states": states, "basis_dimension": len(basis),
            "scalar_dimension": len(scalar), "matrix_sha256": fingerprint(operator, p),
            "scalar_columns": [[[i, v] for i, v in sorted(col.items())] for col in scalar],
            "root_polynomial_terms": len(polynomial),
            "root_polynomial_maximum_individual_degree": max((max(e) for e in polynomial), default=0),
            "kernel_certificate": kernel_certificate, "off_diagonal_projection": projection,
            "restriction": restriction, "extraction": extraction, "counters": dict(counters),
            "root_domain_enumeration_used_by_solver": False, "dense_Dickson_expansion_used_by_solver": False}
