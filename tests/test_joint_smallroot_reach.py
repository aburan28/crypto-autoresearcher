"""Exact arithmetic controls for the successor instrument; no performance claims."""
from fractions import Fraction
from itertools import product
from math import comb

import pytest

from tools import joint_smallroot_reach as J


def test_full_box_finite_budget_is_derived_from_explicit_row_powers():
    for n,d,t in ((1,2,1),(2,2,1),(3,2,1),(2,1,3),(3,2,2)):
        exponents = list(product(range(d*t+1), repeat=n))
        powers = [min(e)//d for e in exponents]
        modulus = sum(t-k for k in powers)
        scaling = sum(sum(e) for e in exponents)
        assert J.full_box_budget(n,d,t) == Fraction(t*len(exponents)-modulus, scaling)
    assert J.full_box_budget(1,2,1) == Fraction(1,3)
    assert J.full_box_budget(3,2,1) == Fraction(1,81)


def test_univariate_asymptote_and_multivariate_limits():
    for d in (1,2,3,4,8):
        assert J.full_box_limit(1,d) == Fraction(1,d)
    for n in (1,2,3,5):
        finite = J.full_box_budget(n,2,1000)
        assert abs(float(finite-J.full_box_limit(n,2))) < 0.002
    assert 3*J.full_box_limit(3,2) == Fraction(1,4)


def test_single_s3_t1_exact_accounting():
    r, _, _ = J.single_lattice(J.s3(),1)
    assert r["dimension"] == 13
    assert r["row_modulus_exponent"] == 12
    assert r["budget"] == 1
    assert r["coordinate_exponents"] == [11,11,11]
    assert r["equal_bound_volume_per_equation"] == "1/11"
    assert r["legacy_q_as_budget_volume_per_equation"] == "12/11"


def test_symbolically_expanded_s3_matches_successor_coefficients():
    import sympy as S
    x,y,z=S.symbols("x y z")
    a,b=2,3
    f=(x-y)**2*z**2-2*((x+y)*(x*y+a)+2*b)*z+(x*y-a)**2-4*b*(x+y)
    assert dict(S.Poly(f,x,y,z).terms()) == J.s3(a,b)


@pytest.mark.parametrize("joint", [False,True])
def test_exact_determinant_matches_materialized_integer_matrix(joint):
    import sympy as S
    polys=J.joint_system() if joint else [J.s3()]
    r, columns, rows=(J.joint_lattice(polys,1) if joint
                      else J.single_lattice(polys[0],1))
    bounds=[2]*len(columns[0])
    matrix=J.coefficient_matrix(polys,1,columns,rows,101,bounds)
    assert abs(int(S.Matrix(matrix).det())) == J.predicted_determinant(r,101,bounds)
    # Every off-diagonal nonzero is earlier than its unique pivot.
    assert all(matrix[i][j] == 0 for i in range(len(matrix))
               for j in range(i+1,len(matrix)))


def test_each_single_row_has_the_required_root_divisibility():
    # A genuine elliptic addition fixture on y²=x³+2x+3 mod 101:
    # P=(1,39), Q=(3,6), P+Q=(41,15). Check before using the x-only relation.
    p=101
    points=[(1,39),(3,6)]
    for x,y in points:
        assert (y*y-x*x*x-2*x-3)%p == 0
    x1,y1=points[0]; x2,y2=points[1]
    slope=(y2-y1)*pow(x2-x1,-1,p)%p
    x3=(slope*slope-x1-x2)%p
    root=(x1,x2,x3)
    f=J.s3()
    assert sum(c*J._scale(e,root) for e,c in f.items())%p == 0
    r,columns,descriptors=J.single_lattice(f,2)
    rows=J.coefficient_matrix([f],2,columns,descriptors,p,[1,1,1])
    for row in rows:
        assert sum(c*J._scale(e,root) for c,e in zip(row,columns))%(p*p) == 0


def test_joint_rows_are_independent_and_use_all_three_equations():
    r,_,_=J.joint_lattice(J.joint_system(),1)
    assert r["dimension"] == 31
    assert r["row_power_histogram"] == {"0":28,"1":3}
    assert r["budget"] == 3
    assert r["coordinate_exponents"] == [11,11,11,11,19,19]
    assert r["equal_bound_volume_per_equation"] == "3/41"


def test_total_degree_joint_count_against_direct_monomial_enumeration():
    # Independent direct enumeration, rather than the generating-function formula.
    for t in (1,2):
        degree=4*t
        monomials=[a for a in product(range(degree+1),repeat=6) if sum(a)<=degree]
        budget=sum(sum(min(a[i],a[i+1])//2 for i in (0,2,4)) for a in monomials)
        r=J.total_degree_joint_budget(t)
        assert r["dimension"] == len(monomials) == comb(degree+6,6)
        assert r["budget"] == budget
        assert r["coordinate_exponents"] == [sum(a[i] for a in monomials) for i in range(6)]


def test_candidate_is_explicitly_not_an_optimizer_or_a_solver():
    r,_,_=J.joint_lattice(J.joint_system(),1)
    assert not r["optimality_claimed"]
    assert not r["root_extraction_implemented"]
    assert not r["lll_and_norm_factors_charged"]
    with pytest.raises(ValueError):
        J.joint_lattice(J.joint_system(),4)


@pytest.mark.parametrize("args",[(0,2,1),(1,0,1),(1,2,0)])
def test_invalid_full_box_parameters_are_rejected(args):
    with pytest.raises(ValueError):
        J.full_box_budget(*args)
