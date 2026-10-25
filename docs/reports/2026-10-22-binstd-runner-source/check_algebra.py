"""Independent GF(2) factor check and restored kernel-construction check."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

import sympy as sp


def main(repo: Path) -> dict:
    source = repo / "experiments/EXP-BINSTD-8bdf86/implementation/run.py"
    spec = importlib.util.spec_from_file_location("binstd_restored_run", source)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    x = sp.symbols("x")
    field_modulus = sp.Poly(x**17 + x**3 + 1, x, modulus=2)
    assert field_modulus.is_irreducible
    factors = sp.factor_list(sp.Poly(x**17 + 1, x, modulus=2))[1]
    assert len(factors) == 3 and all(multiplicity == 1 for _, multiplicity in factors)
    bit_factors = sorted(
        sum((int(poly.nth(power)) & 1) << power for power in range(poly.degree() + 1))
        for poly, _ in factors
    )
    assert bit_factors == [3, 313, 471]
    dims = sorted({
        sum(factors[i][0].degree() for i in range(3) if mask & (1 << i))
        for mask in range(1 << 3)
    })
    assert dims == [0, 1, 8, 9, 16, 17]
    observed = module.admissible_phi_invariant_dims(17)
    assert sorted(f["poly"] for f in observed["factors"]) == bit_factors
    assert observed["admissible_dimensions"] == dims

    field = module.make_field(17)
    kernels = []
    for ell in (8, 9):
        basis = module.build_tau_closed_from_factors(field, ell)
        assert basis is not None
        assert module.span_dim(basis, 17) == ell
        assert module.is_tau_closed(field, basis)
        kernels.append({"dimension": ell, "basis_size": len(basis), "frobenius_closed": True})
    assert module.build_tau_closed_from_factors(field, 3) is None
    assert module.build_tau_closed_from_factors(field, 4) is None
    curve = module.Curve(field, A=0, B=1)
    rng = random.Random(20261022)
    points = [module.random_curve_point(curve, rng) for _ in range(24)]

    def on_curve(point: tuple[int, int] | None) -> bool:
        if point is None:
            return True
        px, py = point
        left = field.sqr(py) ^ field.mul(px, py)
        right = field.mul(field.sqr(px), px) ^ 1
        return left == right

    assert all(on_curve(point) for point in points)
    for i in range(12):
        p, q, r = points[2 * i], points[(2 * i + 1) % 24], points[(2 * i + 2) % 24]
        assert curve.add(p, curve.neg(p)) is None
        assert on_curve(curve.add(p, q))
        assert curve.add(curve.add(p, q), r) == curve.add(p, curve.add(q, r))
    small_fb = points[:8]
    for target in points[8:16]:
        brute = any(
            curve.add(curve.add(p, q), r) == target
            for p in small_fb for q in small_fb for r in small_fb
        )
        assert module.m3_decomposes(curve, small_fb, target) == brute
    return {
        "schema": "binstd-toy-algebra-check-v1",
        "sympy_version": sp.__version__,
        "run_py_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "field_modulus_irreducible": True,
        "x17_plus_1_factors_bitmasks": bit_factors,
        "admissible_dimensions": dims,
        "restored_kernels": kernels,
        "nonadmissible_dimensions_checked": [3, 4],
        "curve_points_checked": len(points),
        "group_associativity_samples": 12,
        "small_fb_triple_membership_checks": 8,
        "limit": "toy checks only; no Lean proof or independent full relation-yield replay",
    }


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1]).resolve()), indent=2, sort_keys=True))
