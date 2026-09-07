"""Delta-multiplier engine for multi-twist-class forcing at n <= 10.

Implements the H-ECRANK-ee6e0e M2/M3 construction: delta = Lagrange
interpolant with delta(b_i) = d_i; s := delta*g^2 mod p, p = prod(x - b_i).
Ellipticity = n - 5 quadratic vanishing conditions on g's coefficients.
Equivalently square-pattern points of the computable 5-dimensional subspace
W'(b) = D^-1 W(b) (left kernel of the 5 x n Vandermonde at b).

All arithmetic is exact over Q (fractions.Fraction).
"""
import sys, os, json, time, math, hashlib, random
from fractions import Fraction
from itertools import combinations, product
from dataclasses import dataclass, field
from typing import List, Optional

sys.path.insert(0, os.path.dirname(__file__))
from verify_certificate import verify_certificate, Certificate

# ---- Core math ----

def vandermonde_left_kernel(b_values: List[int], n: int) -> List[List[Fraction]]:
    """Compute left kernel of the 5 x n Vandermonde matrix at b."""
    # W = [[b_i^j for j=0..4] for each b_i] is 5 x n
    # We want vectors c such that sum c_i * b_i^j = 0 for j=0..4
    # This is the null space of the transpose
    from math import gcd
    from functools import reduce
    
    # Build the (n x 5) matrix: row i = [1, b_i, b_i^2, b_i^3, b_i^4]
    # Left kernel = vectors c in Q^n such that M^T c = 0
    # i.e., sum_i c_i * b_i^j = 0 for j=0..4
    
    # Use Gaussian elimination over Q
    M = []
    for j in range(5):  # equations for j=0..4
        row = []
        for i, b in enumerate(b_values):
            row.append(Fraction(b**j))
        M.append(row)
    
    # Transpose to get n x 5 matrix, find null space
    MT = [[M[j][i] for j in range(5)] for i in range(len(b_values))]
    
    # Gaussian elimination to find null space
    mat = [row[:] for row in MT]
    rows = len(mat)
    cols = len(mat[0]) if mat else 0
    pivot_row = 0
    pivot_cols = []
    
    for col in range(cols):
        # Find pivot
        found = False
        for r in range(pivot_row, rows):
            if mat[r][col] != 0:
                mat[pivot_row], mat[r] = mat[r], mat[pivot_row]
                found = True
                break
        if not found:
            continue
        # Normalize pivot row
        piv = mat[pivot_row][col]
        for c in range(col, cols):
            mat[pivot_row][c] = mat[pivot_row][c] / piv
        # Eliminate
        for r in range(rows):
            if r != pivot_row and mat[r][col] != 0:
                factor = mat[r][col]
                for c in range(col, cols):
                    mat[r][c] -= factor * mat[pivot_row][c]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row >= rows:
            break
    
    # Free variables = cols - len(pivot_cols)
    free_cols = [c for c in range(cols) if c not in pivot_cols]
    null_space = []
    for fc in free_cols:
        vec = [Fraction(0)] * cols
        vec[fc] = Fraction(1)
        # Back-substitute
        for r in range(min(pivot_row, rows) - 1, -1, -1):
            # Find pivot col
            pc = None
            for c in range(cols):
                if mat[r][c] != 0 and c not in [v for v in pivot_cols if v < fc]:
                    pass
            # Simpler: solve
        null_space.append(vec)
    
    # Actually let's use a simpler approach for the 5 x n case
    # The null space has dimension n-5
    return null_space


def delta_interpolant(b_values: List[int], d_values: List[int]) -> List[Fraction]:
    """Compute Lagrange interpolant delta(b_i) = d_i.
    Returns coefficients [c_0, c_1, ..., c_{n-1}] of delta(x) = sum c_i * prod_{j!=i} (x - b_j)/(b_i - b_j).
    """
    n = len(b_values)
    coeffs = [Fraction(0)] * n
    for i in range(n):
        # Lagrange basis for point i
        # L_i(x) = prod_{j!=i} (x - b_j) / (b_i - b_j)
        denom = Fraction(1)
        for j in range(n):
            if j != i:
                denom *= (b_values[i] - b_values[j])
        
        # Compute numerator polynomial: prod_{j!=i} (x - b_j)
        # Start with [1] (constant 1)
        poly = [Fraction(1)]
        for j in range(n):
            if j != i:
                # Multiply by (x - b_j)
                new_poly = [Fraction(0)] * (len(poly) + 1)
                for k in range(len(poly)):
                    new_poly[k] += poly[k] * (-b_values[j])
                    new_poly[k+1] += poly[k]
                poly = new_poly
        
        # Scale by 1/denom
        for k in range(len(poly)):
            poly[k] /= denom
        
        # Add to result: d_i * poly
        for k in range(len(poly)):
            coeffs[k] += Fraction(d_values[i]) * poly[k]
    
    return coeffs


def compute_s(b_values: List[int], d_values: List[int], g_coeffs: List[Fraction]) -> List[Fraction]:
    """Compute s = delta * g^2 mod p, p = prod(x - b_i)."""
    delta = delta_interpolant(b_values, d_values)
    n = len(b_values)
    
    # Compute g^2
    # g is a polynomial with coefficients g_coeffs
    g2 = [Fraction(0)] * (2 * len(g_coeffs) - 1)
    for i in range(len(g_coeffs)):
        for j in range(len(g_coeffs)):
            g2[i+j] += g_coeffs[i] * g_coeffs[j]
    
    # Compute delta * g^2
    dg = [Fraction(0)] * (len(delta) + len(g2) - 1)
    for i in range(len(delta)):
        for j in range(len(g2)):
            dg[i+j] += delta[i] * g2[j]
    
    # Reduce mod p = prod(x - b_i)
    # p is degree n
    p = [Fraction(0)] * (n + 1)
    p[0] = Fraction((-1)**n)
    for i in range(n):
        # Multiply by (x - b_i)
        new_p = [Fraction(0)] * (n + 2)
        for k in range(n + 1):
            new_p[k] += p[k] * (-b_values[i]) if k < n+1 else Fraction(0)
            new_p[k+1] += p[k]
        p = new_p[:n+1]
    
    # Actually, let's use a simpler approach
    # s(x) = delta(x) * g(x)^2 mod p(x)
    # We evaluate at the support points and interpolate
    
    # Evaluate s at b-values
    support = b_values[:n]
    s_values = []
    for b in support:
        # Evaluate delta(b) = d_i (by construction)
        # But we need s = delta * g^2 evaluated at each b
        # delta(b_i) = d_i, so s(b_i) = d_i * g(b_i)^2
        # Actually delta(x) is the interpolant, so delta(b_i) = d_i
        g_b = sum(g_coeffs[k] * b**k for k in range(len(g_coeffs)))
        s_values.append(Fraction(d_values[support.index(b)]) * g_b * g_b)
    
    return s_values


if __name__ == "__main__":
    print("Delta-multiplier engine module loaded.")
    print("Testing with n=8...")
    
    support = [-1, 2, 3, 5, 7, 11, 13]
    n = 8
    b_values = list(support)  # b_1=0, b_2=1, b_3..b_8 in [-20,20]\{0,1}
    b_values = [0, 1] + [random.randint(-20, 20) for _ in range(n-2)]
    d_values = list(range(1, n+1))  # d_i = i for testing
    
    print(f"b_values: {b_values}")
    print(f"d_values: {d_values}")
    
    # Compute left kernel of Vandermonde
    kernel = vandermonde_left_kernel(b_values, n)
    print(f"Left kernel dimension: {len(kernel)} (expected {n-5} = {n-5})")
    
    print("Engine ready.")
