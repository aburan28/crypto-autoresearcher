"""Verify E3 free-module relation inputs and recover a toy known-answer scalar.

Finding sections, their integer coordinates and a full-index kernel is NOT
implemented here. Those are mandatory producer inputs, never inferred from a
count or a floating determinant. This module is prospective certificate plumbing.
"""
from sage.all import GF, Integer, ZZ, matrix, vector


def recover(curve, subgroup_order, generator, target, images, relations,
            generator_coordinates, target_coordinates):
    ell = Integer(subgroup_order)
    if not ell.is_prime():
        raise ValueError("This verifier requires a prime-order subgroup")
    if not curve.base_field().is_prime_field():
        raise ValueError("This scope is prime-field toy fixtures")
    r = len(images)
    if not r:
        raise ValueError("Generator images are missing")
    zero = curve(0)
    points = [curve(point) for point in images]
    generator, target = curve(generator), curve(target)
    if generator == zero or ell * generator != zero:
        raise ValueError("Base generator does not have the supplied prime order")
    if any(ell * point != zero for point in points + [target]):
        raise ValueError("A supplied point is outside the ell-torsion group")
    # For this finite prime-field scope, require the entire rational ell-torsion
    # to be cyclic; otherwise [ell]P=O alone does not establish membership in <G>.
    if Integer(curve.cardinality()) % (ell**2) == 0:
        raise ValueError("Cyclic subgroup membership requires a separate certificate here")

    def coordinates(values):
        if len(values) != r:
            raise ValueError("Integer coordinate dimension mismatch")
        return vector(ZZ, values)

    def image(values):
        result = zero
        for coefficient, point in zip(values, points):
            result += coefficient * point
        return result

    vg, vq = coordinates(generator_coordinates), coordinates(target_coordinates)
    if image(vg) != generator or image(vq) != target:
        raise ValueError("Supplied section coordinates do not specialize to their targets")
    rows = [coordinates(row) for row in relations]
    if not rows or any(image(row) != zero for row in rows):
        raise ValueError("A supplied relation does not specialize to O")
    lattice = matrix(ZZ, rows).row_module()
    if lattice.rank() != r:
        raise ValueError("Relations do not have full integer rank")
    basis = lattice.basis_matrix()
    index = abs(basis.det())
    if index != ell:
        raise ValueError("Relation lattice has a proper index; full kernel not certified")
    kernel = basis.change_ring(GF(ell)).right_kernel()
    if kernel.dimension() != 1:
        raise ValueError("Unexpected quotient dimension")
    functional = kernel.basis()[0]
    denominator = functional.dot_product(vg.change_ring(GF(ell)))
    if not denominator:
        raise ValueError("Generator does not generate the certified quotient")
    scalar = Integer(functional.dot_product(vq.change_ring(GF(ell))) / denominator)
    if scalar * generator != target:
        raise ValueError("Final scalar verification failed")
    return dict(scalar=int(scalar), subgroup_order=int(ell), relation_index=int(index),
                integer_relation_rank=r, verified=True,
                scope="Supplied-vector certificate only; no section finder or cost claim")
