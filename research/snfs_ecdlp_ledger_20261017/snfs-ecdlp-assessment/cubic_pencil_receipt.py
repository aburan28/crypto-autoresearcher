"""Exact finite construction checks; no ECDLP attack or solver benchmark.

The rank conclusion uses standard cubic-pencil geometry and Shioda--Tate.
The code verifies its explicit general-position and intersection inputs.
"""
from itertools import combinations
import json
import math
from pathlib import Path

from sympy import Matrix, isprime

P = 65537
A, B = 2, 3
assert isprime(P) and (4*A**3+27*B**2) % P


def add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y+v) % P == 0:
        return None
    if left == right:
        slope = (3*x*x+A)*pow(2*y, -1, P) % P
    else:
        slope = (v-y)*pow(u-x, -1, P) % P
    w = (slope*slope-x-u) % P
    return w, (slope*(x-w)-y) % P


def rref(matrix):
    rows = [[x % P for x in row] for row in matrix]
    rank, pivots = 0, []
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows))
                      if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        factor = pow(rows[rank][column], -1, P)
        rows[rank] = [x*factor % P for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                factor = rows[i][column]
                rows[i] = [(x-factor*y) % P
                           for x, y in zip(rows[i], rows[rank])]
        pivots.append(column)
        rank += 1
        if rank == len(rows):
            break
    return rows, pivots


def monomials(point, degree):
    x, y, z = point
    return [(x**i*y**j*z**(degree-i-j)) % P
            for i in range(degree+1) for j in range(degree-i+1)]


roots = {}
for y in range(P):
    roots.setdefault(y*y % P, []).append(y)
all_points = [(x, y) for x in range(P)
              for y in roots.get((x**3+A*x+B) % P, [])]
count = len(all_points)+1
assert (P+1-count) % P != 0  # Ordinary.

# A deterministic finite example, not campaign-seed allocation or random sampling.
# One root per x avoids whole blocks of P,-P pairs in the trial selection.
candidates = [(x, ys[0]) for x in range(P)
              if (ys := roots.get((x**3+A*x+B) % P, []))]
for offset in range(min(100, len(candidates)-8)):
    first = candidates[offset:offset+8]
    total = None
    for point in first:
        total = add(total, point)
    if total is None:
        continue
    ninth = (total[0], -total[1] % P)
    if ninth in first:
        continue
    points = [(*point, 1) for point in first+[ninth]]
    if any(int(Matrix(triple).det()) % P == 0
           for triple in combinations(points, 3)):
        continue
    if any(len(rref([monomials(point, 2) for point in subset])[1]) < 6
           for subset in combinations(points, 6)):
        continue
    break
else:
    raise RuntimeError('No general-position example found in deterministic search')

evaluations = [monomials(point, 3) for point in points]
rows, pivots = rref(evaluations)
assert len(pivots) == 8
nullspace = []
for free in set(range(10))-set(pivots):
    vector = [0]*10
    vector[free] = 1
    for row, column in enumerate(pivots):
        vector[column] = -rows[row][free] % P
    nullspace.append(vector)
assert len(nullspace) == 2

# Monomial order from monomials(): Z^3, YZ^2, Y^2Z, Y^3, XZ^2,
# XYZ, XY^2, X^2Z, X^2Y, X^3.
F = [-B % P, 0, 1, 0, -A % P, 0, 0, 0, 0, -1 % P]
assert all(sum(x*y for x, y in zip(row, F)) % P == 0
           for row in evaluations)
G = next(vector for vector in nullspace
         if len(rref([F, vector])[1]) == 2)

# With O=E_9, use sections E_1,...,E_7 and the proper transform
# of the line through the first two points. All are defined over F_P.
# Irreducible fibres give <S,T>=1+S.O+T.O-S.T for S != T.
gram = Matrix(8, 8, lambda i, j: 2 if i == j else 1)
for i in range(7):
    gram[i, 7] = gram[7, i] = 0 if i in (0, 1) else 1
assert gram.det() == 1
assert all(gram[:i, :i].det() > 0 for i in range(1, 9))

receipt = {
    'scope': 'Finite arithmetic/geometric input receipt; not a campaign experiment or ECDLP result',
    'field_prime': P,
    'curve': {'a': A, 'b': B, 'rational_point_count': count, 'ordinary': True},
    'base_points': points,
    'sum_of_base_points_in_original_curve_group': 'O',
    'checks': {
        'nine_distinct_rational_base_points': len(set(points)) == 9,
        'no_three_collinear': True,
        'no_six_on_a_conic': True,
        'cubic_evaluation_rank': len(pivots),
        'pencil_vector_space_dimension': 2,
        'eight_section_gram_positive_definite': True,
        'eight_section_gram_determinant': int(gram.det()),
    },
    'pencil': {'form': 'F + t G = 0; prescribed fibre at t=0',
               'monomial_order': ['Z^3', 'YZ^2', 'Y^2Z', 'Y^3', 'XZ^2',
                                  'XYZ', 'XY^2', 'X^2Z', 'X^2Y', 'X^3'],
               'F': F, 'G': G},
    'identity_identification': 'The pencil zero section is the ninth exceptional divisor. Its fibre is identified with the original group by translation by minus the ninth base point.',
    'gram_matrix': [list(map(int, gram.row(i))) for i in range(8)],
    'geometric_deductions': [
        'F smooth and G independent imply a smooth generic member.',
        'Nine distinct intersections exhaust Bezout degree 9, so base intersections are simple.',
        'Any reducible cubic has a line component; it would contain three of these simple base points. Hence all fibres are geometrically irreducible.',
        'Blowing up nine rational points gives Picard rank 10 with all divisor generators rational. Shioda-Tate gives geometric and arithmetic MW rank 8.',
        'The displayed rational sections have determinant-one positive height Gram matrix, giving the full E8 lattice in this setting.',
    ],
    'rank_claim_type': 'Deduction from standard geometry with checked inputs, not a zeta-function computation',
    'scaling_heuristic': {
        'height_convention': 'squared norm in the determinant-one E8 lattice',
        'V8': math.pi**4/24,
        'N(H)': 'approximately (pi^4/24) H^4',
        'necessary_count_threshold_H': '(p / (pi^4/24))^(1/4); not a coverage proof',
        'H_at_256_bit_size_proxy': (2.0**256/(math.pi**4/24))**0.25,
    },
    'sources': ['https://arxiv.org/html/0907.0298v3#S3.SS2',
                'https://jtnb.centre-mersenne.org/item/10.5802/jtnb.102.pdf'],
}
out = Path(__file__).with_name('cubic-pencil-receipt.json')
out.write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({'prime': P, 'curve_order': count, 'search_offset': offset,
                  'cubic_evaluation_rank': 8, 'gram_determinant': 1,
                  'rank_deduced_from_geometry': 8,
                  'receipt': str(out)}))
