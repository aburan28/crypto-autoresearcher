"""Tests for harness/macaulay_fp (TASK-20260903-ba41aa).

These are TESTS of an instrument, not runs and not evidence about any
hypothesis.  Expected integers come from committed records (KN-FIND-006,
EXP-DREG-001 characterization, EXP-ALPF-013) or from planted constructions
whose answer is forced; no expected value was adjusted to fit an observation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

import pytest

from harness.macaulay_fp import (
    P256_PRIME,
    ColumnSpace,
    Echelon,
    PreflightAbort,
    Ring,
    analyze_degrees,
    analyze_layer,
    block_factored_system,
    boolean_masks_to_poly,
    default_frobenius,
    deficit_profile,
    digit_presentation,
    direct_presentation,
    dreg_boolean_null,
    f_V,
    fall_content_contains,
    first_nontrivial_syzygy,
    first_nonzero_fall,
    growth_of_extra_generator,
    histogram_matched_system,
    koszul_count,
    layer_rows,
    localization_gate,
    membership_generator,
    poly_from_terms,
    poly_to_boolean_masks,
    preflight,
    scramble_coefficients,
    semiregular_prediction,
    support_matched_system,
    verify_layer_two_eliminations,
)

REPO = Path(__file__).resolve().parents[1]
BOOL_METER = REPO / "experiments" / "EXP-SBRG-60c55e" / "driver" / "macaulay.py"
FIXTURE_DIR = REPO / "harness" / "macaulay_fp" / "fixtures"
FIXTURE_JSON = FIXTURE_DIR / "chained_gf2_n12_t3_seed2026.json"
FIXTURE_SHA256 = "62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5"
ARCHIVED_SYSTEM_HASH = "c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def load_boolean_meter():
    spec = importlib.util.spec_from_file_location("macaulay_boolean_archived", BOOL_METER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_builder():
    spec = importlib.util.spec_from_file_location("gf2_chained_builder", FIXTURE_DIR / "gf2_chained_builder.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def random_poly(ring: Ring, rng: random.Random, degree: int, density: float = 0.6, homogeneous: bool = False) -> dict:
    monos = ring.monomials_exact(degree) if homogeneous else ring.monomials_upto(degree)
    out = {}
    for m in monos:
        if rng.random() < density:
            out[m] = rng.randrange(1, ring.p) if ring.p > 2 else 1
    if not any(ring.mono_degree(m) == degree for m in out):
        top = ring.monomials_exact(degree)
        out[top[rng.randrange(len(top))]] = 1
    return out


def sympy_rank(p: int, rows: list, ncols: int) -> int:
    from sympy import GF
    from sympy.polys.matrices import DomainMatrix

    K = GF(p)
    dense = [[K(r.get(c, 0)) for c in range(ncols)] for r in rows]
    if not dense:
        return 0
    return DomainMatrix(dense, (len(dense), ncols), K).rank()


def fixture_polys():
    data = json.loads(FIXTURE_JSON.read_text())
    ring = Ring(2, data["nb"])
    polys = [{(sum(1 << v for v in m), ()): 1 for m in f} for f in data["generators"]]
    return data, ring, polys


# --------------------------------------------------------------------------
# G2: the p = 2 known answer (KN-FIND-006) on the chained GF(2) fixture
# --------------------------------------------------------------------------


def test_fixture_provenance_sha256_and_builder_determinism():
    assert hashlib.sha256(FIXTURE_JSON.read_bytes()).hexdigest() == FIXTURE_SHA256
    data = json.loads(FIXTURE_JSON.read_text())
    gb = load_builder()
    rebuilt = gb.build_fixture(12, 3, 0, 2026, "int")
    assert rebuilt["system_hash"] == data["system_hash"]
    assert rebuilt["generators"] == data["generators"]
    assert data["modulus_poly"] == "x^12 + x^7 + x^6 + x^5 + x^3 + x + 1"
    assert data["nb"] == 24 and sorted(data["eq_degs"]) == [2] * 12 + [3] * 12
    # Recorded, not asserted equal: the archived Sage run's system hash.  The
    # reconstruction is the same construction but NOT bit-identical (see
    # VALIDATION.md, deviation D1).
    assert data["archived_system_hash"] == ARCHIVED_SYSTEM_HASH
    assert data["matches_archived_system_hash"] is False


def test_known_answer_p2_cumulative_convention_kn_find_006():
    data, ring, polys = fixture_polys()
    assert default_frobenius(ring) is True
    layers = analyze_degrees(ring, polys, 2, 4, convention="cumulative")
    prof = deficit_profile(layers)
    assert prof.convention == "cumulative" and prof.frobenius_factor is True
    # DREG pred[D] (Boolean series): 12, 312, 3834 at D = 2, 3, 4
    assert prof.pred == (12, 312, 3834)
    # KN-FIND-006: graded deficit 1 at D = 3 and 31 at D = 4 (= 8k - 1, k = 4);
    # cumulative deficit at D = 4 equals 8k = 32.
    assert prof.deficit_graded[1] == 1
    assert prof.deficit_graded[2] == 31
    assert prof.deficit_cumulative[2] == 32
    # Explicit trivial count at D = 4: 12 Frobenius + 66 Koszul = 78 = rows - pred.
    assert prof.koszul_pairwise[2] == 78 == prof.koszul_series[2]
    assert prof.deficit_pairwise == prof.deficit_cumulative
    # Row counts match the DREG layer generator (no zero products in this system).
    assert prof.rows == (12, 312, 3912)
    assert all(l.zero_product_rows == 0 for l in layers)


def test_known_answer_null_arms_are_zero_at_p2():
    data, ring, polys = fixture_polys()
    # (i) KN-FIND-006's "support-matched null" = EXP-DREG-001 boolean_null, ported
    #     verbatim; RNG state continues after the builder's sample() call.
    rng = random.Random(data["rng_seed"])
    rng.sample(list(range(data["n_candidates"])), 3)
    null = dreg_boolean_null(ring, polys, rng)
    prof = deficit_profile(analyze_degrees(ring, null, 2, 4, convention="cumulative"))
    assert prof.deficit_graded[1] == 0 and prof.deficit_graded[2] == 0
    assert prof.deficit_cumulative[2] == 0
    # (ii) the port's own histogram-matched null at two seeds.
    for seed in (7, 11):
        hm, meta = histogram_matched_system(ring, polys, seed)
        assert meta.kind == "histogram_matched" and meta.degree_histogram_exact
        for t, q in zip(polys, hm):
            assert ring.degree_histogram(t) == ring.degree_histogram(q)
        prof = deficit_profile(analyze_degrees(ring, hm, 2, 4, convention="cumulative"))
        assert prof.deficit_cumulative == (0, 0, 0)
    # (iii) the IDENTICAL-support null is the identity at p = 2 and says so.
    sm, meta = support_matched_system(ring, polys, 7)
    assert meta.degenerate_at_p2 is True and sm == polys


def test_known_answer_per_layer_convention_recorded_not_matched():
    """Both conventions are reported; only the cumulative one is the KN-FIND-006
    convention (established from the DREG artifacts, see VALIDATION.md)."""
    data, ring, polys = fixture_polys()
    per = analyze_degrees(ring, polys, 2, 4, convention="per_layer")
    cum = analyze_degrees(ring, polys, 2, 4, convention="cumulative")
    assert [l.convention for l in per] == ["per_layer"] * 3
    assert [l.convention for l in cum] == ["cumulative"] * 3
    # Per-layer rows at D = 4: 12 * C(24,2) + 12 * 24 = 3312 + 288 = 3600.
    assert per[2].row_count == 3600
    # The two conventions are different objects: their D = 4 syzygy counts differ.
    assert per[2].syzygy_dim != cum[2].syzygy_dim


def test_series_boolean_factor_reproduces_dreg_pred_and_naive_differs():
    ring = Ring(2, 24)
    degs = [2] * 12 + [3] * 12
    boolean = semiregular_prediction(ring, degs, 5, frobenius=True)
    naive = semiregular_prediction(ring, degs, 5, frobenius=False)
    assert boolean.pred_cumulative == (0, 0, 12, 312, 3834, 29418)  # archived pred[5] = 29418
    assert naive.pred_cumulative[4] == 3846 and naive.pred_cumulative[5] != 29418
    assert boolean.hilbert_function[4] == 7104 and naive.hilbert_function[4] == 7092


# --------------------------------------------------------------------------
# G4: mod-2 agreement with the archived Boolean meter on its own fixtures
# --------------------------------------------------------------------------


def P(*masks):
    return frozenset(masks)


def test_mod2_boolean_multiplication_collapses_and_cancels():
    ring = Ring(2, 3)
    poly = boolean_masks_to_poly(ring, [0b001, 0b011])
    assert ring.mul_monomial(poly, (0b010, ())) == {}


def test_mod2_evaluate():
    ring = Ring(2, 3)
    poly = boolean_masks_to_poly(ring, [0, 0b001, 0b110])  # 1 + x0 + x1*x2
    assert ring.evaluate(poly, [0, 0, 0]) == 1
    assert ring.evaluate(poly, [1, 0, 0]) == 0
    assert ring.evaluate(poly, [1, 1, 1]) == 1


def test_mod2_gf2_rank():
    e = Echelon(2)
    e.extend([0b1000, 0b0100, 0b0010, 0b1000 ^ 0b0100])
    assert e.rank == 3 and e.stats.zero_rows == 1


def test_mod2_single_row_degree_fall_from_boolean_reduction():
    ring = Ring(2, 3)
    f = boolean_masks_to_poly(ring, [0b011, 0b001])
    layer = analyze_layer(ring, [f], 3)
    assert layer.fall_dim >= 1 and layer.full_rank >= layer.top_rank


def test_mod2_exact_syzygy_is_counted():
    ring = Ring(2, 2)
    f = boolean_masks_to_poly(ring, [0b011, 0b001])
    layer = analyze_layer(ring, [f, f], 2)
    assert layer.syzygy_dim >= 1


def test_mod2_first_nonzero_fall():
    ring = Ring(2, 3)
    f = boolean_masks_to_poly(ring, [0b011, 0b001])
    layers = analyze_degrees(ring, [f], 2, 3)
    assert first_nonzero_fall(layers) == 3


def test_mod2_random_matched_system_preserves_histograms_and_plants_root():
    ring = Ring(2, 3)
    templates = [boolean_masks_to_poly(ring, [0, 0b001, 0b010, 0b101]),
                 boolean_masks_to_poly(ring, [0b011, 0b100, 0b111])]
    planted = ([1, 0, 1], [])
    controls, meta = histogram_matched_system(ring, templates, 1234, planted_point=planted)
    assert len(controls) == len(templates)
    assert all(ring.evaluate(q, *planted) == 0 for q in controls)
    if meta.degree_histogram_exact:
        for t, q in zip(templates, controls):
            assert ring.degree_histogram(t) == ring.degree_histogram(q)


def test_mod2_random_controls_are_deterministic_for_seed():
    ring = Ring(2, 3)
    templates = [boolean_masks_to_poly(ring, [0, 1, 2, 3]), boolean_masks_to_poly(ring, [4, 5, 6])]
    a, ma = histogram_matched_system(ring, templates, 99, planted_point=([1, 0, 1], []))
    b, mb = histogram_matched_system(ring, templates, 99, planted_point=([1, 0, 1], []))
    assert a == b and ma == mb


def test_mod2_unplanted_null_is_bitwise_the_boolean_meters_null():
    m = load_boolean_meter()
    ring = Ring(2, 5)
    templates_b = [P(0, 0b00001, 0b00110, 0b10101), P(0b00011, 0b01100, 0b11100, 0b00111)]
    templates = [boolean_masks_to_poly(ring, t) for t in templates_b]
    for seed in (1, 2, 3):
        ours, _ = histogram_matched_system(ring, templates, seed)
        theirs, _ = m.random_matched_system(templates_b, 5, seed=seed)
        assert [poly_to_boolean_masks(q) for q in ours] == theirs


def test_mod2_batch_reuse_total_rank_matches_port_layer_rank():
    m = load_boolean_meter()
    fixed = [P(0b001, 0b010), P(0b100, 0)]
    targets = [[P(0b011, 0b101)], [P(0b110, 0b001)], [P(0b111, 0b010)]]
    stats = m.analyze_batch_reuse(fixed, targets, nvars=3, degree=2)
    ring = Ring(2, 3)
    for target, ts in zip(targets, stats.targets):
        polys = [boolean_masks_to_poly(ring, q) for q in fixed + target]
        assert analyze_layer(ring, polys, 2).full_rank == ts.total_rank
        assert ts.rowspace_intersection_dim >= 0


@pytest.mark.parametrize("seed", [11, 12, 13, 14])
def test_mod2_random_systems_agree_with_boolean_meter_layer_by_layer(seed):
    m = load_boolean_meter()
    rng = random.Random(seed)
    nvars = 6
    ring = Ring(2, nvars)
    polys = [random_poly(ring, rng, rng.choice([2, 3]), density=0.35) for _ in range(4)]
    polys_b = [poly_to_boolean_masks(q) for q in polys]
    for D in range(2, 5):
        ours = analyze_layer(ring, polys, D, "per_layer")
        theirs = m.analyze_layer(polys_b, nvars=nvars, degree=D)
        assert (ours.row_count, ours.top_rank, ours.full_rank, ours.fall_dim, ours.syzygy_dim,
                ours.zero_product_rows, ours.nnz_total, ours.nnz_top) == (
            theirs.row_count, theirs.top_rank, theirs.full_rank, theirs.fall_dim, theirs.syzygy_dim,
            theirs.zero_product_rows, theirs.nnz_total, theirs.nnz_top)
    layers = analyze_degrees(ring, polys, 2, 4)
    layers_b = m.analyze_degrees(polys_b, nvars, 2, 4)
    assert first_nonzero_fall(layers) == m.first_nonzero_fall(layers_b)


# --------------------------------------------------------------------------
# exact linear algebra: one-elimination identity, sympy oracle, P-256
# --------------------------------------------------------------------------


@pytest.mark.parametrize("p,n_sq,n_free", [(2, 6, 0), (4099, 5, 0), (4099, 0, 3), (65537, 3, 1)])
def test_single_elimination_equals_two_elimination_route(p, n_sq, n_free):
    rng = random.Random(p + n_sq + 10 * n_free)
    ring = Ring(p, n_sq, n_free)
    polys = [random_poly(ring, rng, 2, 0.5) for _ in range(3)]
    for D in (2, 3, 4):
        for conv in ("per_layer", "cumulative"):
            L = analyze_layer(ring, polys, D, conv)
            full, top = verify_layer_two_eliminations(ring, polys, D, conv)
            assert (L.full_rank, L.top_rank) == (full, top)
            assert L.fall_dim == full - top


@pytest.mark.parametrize("p,n_sq,n_free", [(3, 4, 0), (4099, 4, 0), (4099, 0, 2), (10007, 2, 1)])
def test_ranks_agree_with_sympy_domainmatrix_oracle(p, n_sq, n_free):
    rng = random.Random(1000 * p + n_sq + n_free)
    ring = Ring(p, n_sq, n_free)
    polys = [random_poly(ring, rng, rng.choice([2, 3]), 0.5) for _ in range(3)]
    for D in (3, 4):
        cols = ColumnSpace.build(ring, D)
        rows, _, _ = layer_rows(ring, polys, D, "cumulative")
        enc = [cols.encode(r) for r in rows]
        L = analyze_layer(ring, polys, D, "cumulative", columns=cols)
        assert L.full_rank == sympy_rank(p, enc, cols.ncols)
        top_start = cols.degree_start[D]
        top_rows = [{c - top_start: v for c, v in r.items() if c >= top_start} for r in enc]
        assert L.top_rank == sympy_rank(p, top_rows, cols.ncols_exact(D))


def test_arbitrary_precision_residues_at_p256():
    p = P256_PRIME
    ring = Ring(p, 0, 2)
    rng = random.Random(256)
    g1 = random_poly(ring, rng, 2, 0.9)
    g2 = random_poly(ring, rng, 2, 0.9)
    c1, c2 = rng.randrange(1, p), rng.randrange(1, p)
    g3 = ring.add(ring.scale(g1, c1), ring.scale(g2, c2))  # exact dependency with 256-bit coefficients
    assert all(isinstance(c, int) and 0 < c < p for c in g3.values())
    L = analyze_layer(ring, [g1, g2, g3], 2, "per_layer")
    assert L.row_count == 3 and L.full_rank == 2 and L.syzygy_dim == 1
    L4 = analyze_layer(ring, [g1, g2, g3], 4, "cumulative")
    cols = ColumnSpace.build(ring, 4)
    rows, _, _ = layer_rows(ring, [g1, g2, g3], 4, "cumulative")
    assert L4.full_rank == sympy_rank(p, [cols.encode(r) for r in rows], cols.ncols)
    # Without the planted dependency the same shape is full-rank at D = 2.
    assert analyze_layer(ring, [g1, g2], 2).syzygy_dim == 0
    # Coefficient products are reduced mod p at every step: no residue exceeds p.
    prod = ring.mul(g1, g2)
    assert max(prod.values()) < p and all(isinstance(c, int) for c in prod.values())


# --------------------------------------------------------------------------
# G3: planted-syzygy positive control (IDEA-20260903-afa56b) and planted fall
# --------------------------------------------------------------------------


def _plant_redundant(ring, rng, f1, f2, D_star, k):
    d1, d2 = ring.degree(f1), ring.degree(f2)
    planted = []
    for _ in range(k):
        while True:
            u = random_poly(ring, rng, D_star - d1, 0.8, homogeneous=True)
            v = random_poly(ring, rng, D_star - d2, 0.8, homogeneous=True)
            g = ring.add(ring.mul(u, f1), ring.mul(v, f2))
            if ring.degree(g) == D_star:
                planted.append(g)
                break
    return planted


@pytest.mark.parametrize("mode", ["squarefree", "ordinary"])
@pytest.mark.parametrize("k", [1, 2, 4, 8])
def test_planted_syzygy_control_recovers_exactly_k(mode, k):
    p = 4099
    # 10 squarefree variables keep D* = 3, 4 below the shape's D_reg = 6 (with 6
    # variables two quadrics reach D_reg = 4 and the series is truncated there).
    # The ring must leave room for k extra generators at D*: the semi-regular
    # Hilbert function of the EXTENDED sequence must stay positive at D* (with
    # 3 free variables and k = 8 cubics it goes negative at D* = 3 and the
    # series is truncated there).  Checked, not assumed.
    ring = Ring(p, 10, 0) if mode == "squarefree" else Ring(p, 0, 5)
    rng = random.Random(1000 + k + (7 if mode == "ordinary" else 0))
    f1 = random_poly(ring, rng, 2, 0.7)
    f2 = random_poly(ring, rng, 2, 0.7)
    for D_star in (3, 4):
        ext_pred = semiregular_prediction(ring, [2, 2] + [D_star] * k, D_star + 1, frobenius=False)
        assert ext_pred.hilbert_function[D_star] > 0 and (ext_pred.d_reg is None or ext_pred.d_reg > D_star)
        planted = _plant_redundant(ring, rng, f1, f2, D_star, k)
        base = analyze_layer(ring, [f1, f2], D_star, "cumulative")
        ext = analyze_layer(ring, [f1, f2] + planted, D_star, "cumulative")
        # Z_D = pred - rank (afa56b's census by the series route): exactly k more.
        assert ext.deficit_series - base.deficit_series == k
        # And by the explicit first-order route.
        assert ext.deficit_pairwise - base.deficit_pairwise == k
        # The planted rows add no rank (they are in the row space) and k rows.
        assert ext.full_rank == base.full_rank and ext.row_count == base.row_count + k
        # The pre-registered semi-regular growth of a degree-D* generator is 1 at D*.
        _, cum = growth_of_extra_generator(ring, [2, 2], D_star, D_star)
        assert cum[D_star] == 1


def test_planted_syzygies_at_mixed_degrees_match_sequential_prediction():
    """Two planted generators at D_1 < D_2: the raw census difference at every
    D equals the sum of the sequential semi-regular increments of the planted
    generators (the F5-equivalent count: every multiple of a redundant
    generator reduces to zero)."""
    p = 4099
    ring = Ring(p, 0, 3)
    rng = random.Random(4242)
    f1 = random_poly(ring, rng, 2, 0.7)
    f2 = random_poly(ring, rng, 2, 0.7)
    g1 = _plant_redundant(ring, rng, f1, f2, 3, 1)[0]
    g2 = _plant_redundant(ring, rng, f1, f2, 4, 1)[0]
    Dmax = 5
    seqs = [[2, 2], [2, 2, 3], [2, 2, 3, 4]]
    preds = [semiregular_prediction(ring, s, Dmax, frobenius=False).pred_cumulative for s in seqs]
    for D in range(3, Dmax + 1):
        base = analyze_layer(ring, [f1, f2], D, "cumulative")
        ext = analyze_layer(ring, [f1, f2, g1, g2], D, "cumulative")
        expected = (preds[1][D] - preds[0][D]) + (preds[2][D] - preds[1][D])
        assert ext.deficit_series - base.deficit_series == expected
        assert ext.full_rank == base.full_rank


@pytest.mark.parametrize("mode", ["ordinary", "squarefree"])
def test_planted_fall_generator_reports_fall_with_content_h(mode):
    p = 4099
    ring = Ring(p, 10, 0) if mode == "squarefree" else Ring(p, 0, 3)
    rng = random.Random(77 if mode == "ordinary" else 78)
    f1 = random_poly(ring, rng, 2, 0.7)
    f2 = random_poly(ring, rng, 2, 0.7)
    D = 4
    while True:
        u = random_poly(ring, rng, D - 2, 0.8, homogeneous=True)
        v = random_poly(ring, rng, D - 2, 0.8, homogeneous=True)
        h = random_poly(ring, rng, D - 1, 0.5)
        g = ring.add(ring.add(ring.mul(u, f1), ring.mul(v, f2)), h)
        if ring.degree(g) == D and ring.degree(h) == D - 1:
            break
    cols = ColumnSpace.build(ring, D)
    base = analyze_layer(ring, [f1, f2], D, "per_layer", columns=cols, want_fall_basis=True)
    ext = analyze_layer(ring, [f1, f2, g], D, "per_layer", columns=cols, want_fall_basis=True)
    assert ext.fall_dim == base.fall_dim + 1
    assert fall_content_contains(ring, ext, cols, h) is True
    assert fall_content_contains(ring, base, cols, h) is False
    # The new fall is g - u f1 - v f2 = h: the fall space grew by exactly span(h).
    e = Echelon(p)
    for b in base.fall_basis:
        e.add(e.encode(cols.encode(b)))
    assert not e.contains(e.encode(cols.encode(h)))
    e.add(e.encode(cols.encode(h)))
    for b in ext.fall_basis:
        assert e.contains(e.encode(cols.encode(b)))


# --------------------------------------------------------------------------
# G4: the s = 1 slice equals the direct f_V presentation
# --------------------------------------------------------------------------


def _toy_system(ring, xs):
    x1, x2 = xs
    return [ring.add(ring.add(ring.mul(ring.mul(x1, x1), x2), ring.scale(ring.mul(x1, x2), 3)),
                     ring.add(ring.mul(x2, x2), ring.constant(5)))]


@pytest.mark.parametrize("B", [3, 4, 5])
def test_s1_slice_equals_direct_presentation(B):
    p = 4099
    direct = direct_presentation(p, 2, B, _toy_system)
    digit = digit_presentation(p, 2, B, 1, _toy_system)
    assert direct.ring == digit.ring and direct.ring.mode == "ordinary"
    # membership generators equal generator for generator: prod_{j<B}(a - j) = f_V(x)
    assert list(direct.membership) == list(digit.membership)
    assert list(direct.generators) == list(digit.generators)
    assert digit.membership[0] == f_V(digit.ring, digit.ring.free_var(0), B)
    assert direct.membership[0] == membership_generator(direct.ring, direct.ring.free_var(0), B)
    # graded rank profiles coincide under both conventions
    for conv in ("per_layer", "cumulative"):
        a = analyze_degrees(direct.ring, list(direct.generators), 2, B + 2, conv)
        b = analyze_degrees(digit.ring, list(digit.generators), 2, B + 2, conv)
        assert [l.as_dict() for l in a] == [l.as_dict() for l in b]


def test_digit_presentation_base2_is_squarefree_and_s_digits_substitute():
    p = 4099
    pres = digit_presentation(p, 2, 2, 3, _toy_system)
    assert pres.ring.mode == "squarefree" and pres.ring.n_sq == 6 and pres.membership == ()
    x1 = pres.unknown_polys[0]
    assert x1 == {pres.ring.sq_var(0): 1, pres.ring.sq_var(1): 2, pres.ring.sq_var(2): 4}
    # a^2 -> a: squaring the linear digit form stays multilinear
    sq = pres.ring.mul(x1, x1)
    assert all(pres.ring.mono_degree(m) <= 2 for m in sq) and all(m[0] & (m[0] - 1) or True for m in sq)
    mixed = digit_presentation(p, 2, 2, 2, _toy_system, n_extra_free=1)
    assert mixed.ring.mode == "mixed" and mixed.ring.n_free == 1


# --------------------------------------------------------------------------
# G5: modes, conventions, Koszul, localization, nulls, pre-flight
# --------------------------------------------------------------------------


def test_mixed_mode_total_degree_grading_and_top_projection():
    p = 4099
    ring = Ring(p, 2, 1)  # a0, a1 squarefree; u free
    a0, a1, u = ring.sq_var(0), ring.sq_var(1), ring.free_var(0)
    f = poly_from_terms(ring, [(1, [0, 1], [2]), (1, [0], [0]), (1, [], [1])])  # a0 a1 u^2 + a0 + u
    assert ring.degree(f) == 4 and ring.top_form(f) == {(0b11, (2,)): 1}
    assert ring.mul_monomial(f, a0) == {(0b11, (2,)): 1, (0b01, (0,)): 1, (0b01, (1,)): 1}
    L = analyze_layer(ring, [f], 5, "per_layer")
    # multipliers of degree 1: a0, a1, u -> a0 f and a1 f collapse below degree 5
    assert L.row_count == 3 and L.top_rank == 1 and L.fall_dim == 2
    assert L.ncols_top == ring.count_monomials_exact(5)
    assert L.mode == "mixed"


def test_frobenius_default_and_counterexample_at_odd_p():
    ring = Ring(4099, 2, 0)
    f = {ring.sq_var(0): 1, ring.sq_var(1): 1}
    assert ring.mul(f, f) != f  # (a1 + a2)^2 = a1 + a2 + 2 a1 a2 in F_p[a]/(a^2 - a)
    assert default_frobenius(ring) is False
    r2 = Ring(2, 2, 0)
    f2 = {r2.sq_var(0): 1, r2.sq_var(1): 1}
    assert r2.mul(f2, f2) == f2 and default_frobenius(r2) is True
    assert default_frobenius(Ring(2, 2, 1)) is False


def test_koszul_counts_per_layer_and_cumulative():
    ring = Ring(10007, 0, 3)
    # EXP-ALPF-013: trivial_koszul(D) = sum_{i<j} C(n-1 + D-d_i-d_j, D-d_i-d_j)
    assert koszul_count(ring, [3, 3, 3], 6, "per_layer") == 3
    assert koszul_count(ring, [3, 3, 3], 7, "per_layer") == 9
    # pairs (2,2): multipliers of degree <= 4 in 3 free variables = C(7,3) = 35;
    # pairs (2,4) twice: degree <= 2 -> C(5,3) = 10 each.
    assert koszul_count(ring, [2, 2, 4], 8, "cumulative") == 35 + 10 + 10
    r2 = Ring(2, 24, 0)
    assert koszul_count(r2, [2] * 12 + [3] * 12, 4, "cumulative") == 78
    assert koszul_count(r2, [2] * 12 + [3] * 12, 5, "cumulative") == 2094  # = 31512 - 29418
    assert koszul_count(r2, [2] * 12 + [3] * 12, 4, "per_layer") == 66


def _alpf_pos_a(ring, rng):
    q = random_poly(ring, rng, 2, 0.9, homogeneous=True)
    return [ring.mul(q, random_poly(ring, rng, 1, 0.9, homogeneous=True)) for _ in range(3)]


def test_localization_gate_reproduces_alpf013_controls():
    p = 10007
    ring = Ring(p, 0, 3)
    rng = random.Random(13)
    # POS-A: three cubics sharing a quadratic factor -> d_ff = 4, nontriv 3, D_reg 7
    pos_a = _alpf_pos_a(ring, rng)
    layers = analyze_degrees(ring, pos_a, 3, 6, "per_layer", leading_forms=True)
    assert first_nontrivial_syzygy(layers) == 4
    assert layers[1].top_deficit_series == 3 and layers[1].deficit_pairwise == 3
    pred = semiregular_prediction(ring, [3, 3, 3], 8, frobenius=False)
    assert pred.d_reg == 7
    # NEG-1: three generic quadrics -> no fire, D_reg 4; NEG-2: cubics -> D_reg 7
    neg1 = [random_poly(ring, rng, 2, 0.9, homogeneous=True) for _ in range(3)]
    assert first_nontrivial_syzygy(analyze_degrees(ring, neg1, 2, 3, "per_layer", leading_forms=True)) is None
    assert semiregular_prediction(ring, [2, 2, 2], 6, frobenius=False).d_reg == 4
    neg2 = [random_poly(ring, rng, 3, 0.9, homogeneous=True) for _ in range(3)]
    assert first_nontrivial_syzygy(analyze_degrees(ring, neg2, 3, 6, "per_layer", leading_forms=True)) is None
    # POS-A with no summation rows: gate has nothing to localise on
    g = localization_gate(ring, pos_a, 4, subset=[])
    assert g.nontriv_full_pairwise == 3 == g.nontriv_fb_pairwise and g.involves_subset_direct is False
    assert g.localization_bit_pairwise == 0 and g.localization_bit_series == 0
    # synthetic gate-POS: generator 0 declared summation -> nontriv_full 3 > nontriv_fb 1
    g = localization_gate(ring, pos_a, 4, subset=[0])
    assert (g.nontriv_full_pairwise, g.nontriv_fb_pairwise) == (3, 1)
    assert g.involves_subset_shrink_pairwise and g.involves_subset_shrink_series and g.involves_subset_direct
    assert g.localization_bit_pairwise == 2 and g.n_subset_rows == 3
    # NEG-2 with a declared subset at D = 6: the Koszul-corrected (shrink) bit is
    # 0; the uncorrected DIRECT kernel comparison is True because the two Koszul
    # pairs through generator 0 leave with it (ker_full 3, ker_fb 1) -- which is
    # why EXP-ALPF-013 evaluates the gate only at a firing degree d_ff.
    g = localization_gate(ring, neg2, 6, subset=[0])
    assert g.localization_bit_pairwise == 0 and g.localization_bit_series == 0
    assert not g.involves_subset_shrink_pairwise and not g.involves_subset_shrink_series
    assert (g.ker_full, g.ker_fb, g.involves_subset_direct) == (3, 1, True)


def test_support_matched_null_at_odd_p_keeps_support_and_is_not_identity():
    ring = Ring(4099, 4, 0)
    rng = random.Random(5)
    polys = [random_poly(ring, rng, 2, 0.6) for _ in range(3)]
    sm, meta = support_matched_system(ring, polys, 7)
    assert meta.kind == "support_matched" and meta.degenerate_at_p2 is False
    assert [set(q) for q in sm] == [set(f) for f in polys]
    assert sm != polys
    again, _ = support_matched_system(ring, polys, 7)
    assert again == sm


def test_block_factored_null_has_block_product_structure():
    ring = Ring(4099, 6, 0)
    blocks = [[0, 1, 2], [3, 4, 5]]
    gens, meta, factors = block_factored_system(ring, blocks, [2, 2], seed=7, count=2,
                                                extra_generators=[{ring.sq_var(0): 1}])
    assert meta.kind == "block_factored" and len(gens) == 3
    for g, fs in zip(gens[:2], factors):
        assert ring.mul(fs[0], fs[1]) == g
        for m in fs[0]:
            assert ring.mono_degree(m) == 2 and m[0] & 0b111000 == 0
        for m in fs[1]:
            assert ring.mono_degree(m) == 2 and m[0] & 0b000111 == 0
        for m in g:
            assert ring.mono_degree(m) == 4
    same, _, _ = block_factored_system(ring, blocks, [2, 2], seed=7, count=2,
                                       extra_generators=[{ring.sq_var(0): 1}])
    assert same == gens
    # a block-factored generator in mixed mode with the free variable in a block
    rm = Ring(4099, 4, 1)
    g, _ = __import__("harness.macaulay_fp.nulls", fromlist=["block_factored_generator"]).block_factored_generator(
        rm, [[0, 1], [2, 3, -1]], [1, 2], random.Random(3))
    assert all(rm.mono_degree(m) == 3 for m in g)


def test_scramble_coefficients_targets_selected_monomials_only():
    ring = Ring(4099, 0, 2)
    rng = random.Random(9)
    polys = [random_poly(ring, rng, 2, 0.9) for _ in range(2)]
    const = ring.one()
    out, meta, selected = scramble_coefficients(ring, polys, 3, lambda gi, m, c: m == const)
    assert meta.kind == "coefficient_scramble"
    for f, g, sel in zip(polys, out, selected):
        assert set(f) == set(g) and sel == [const]
        assert all(f[m] == g[m] for m in f if m != const)


def test_preflight_gate_counts_and_aborts_before_allocation():
    ring = Ring(2, 24, 0)
    degs = [2] * 12 + [3] * 12
    pf = preflight(ring, degs, 5, "cumulative")
    assert (pf.rows, pf.cols, pf.cols_top) == (31512, 55455, 42504)  # archived nrows 31512 at D = 5
    assert dict(pf.rows_by_generator_degree) == {2: 27900, 3: 3612}
    with pytest.raises(PreflightAbort) as exc:
        preflight(ring, degs, 5, "cumulative", max_cols=50000)
    assert exc.value.counts.cols == 55455 and exc.value.max_cols == 50000
    data, ring2, polys = fixture_polys()
    with pytest.raises(PreflightAbort) as exc:
        analyze_layer(ring2, polys, 4, "cumulative", max_rows=1000)
    assert exc.value.counts.rows == 3912
    # counts are exact against the realised layer
    L = analyze_layer(ring2, polys, 4, "cumulative")
    assert L.preflight.rows == L.row_count + L.zero_product_rows and L.preflight.cols == L.ncols_full


def test_layer_result_records_convention_mode_and_prime():
    ring = Ring(65537, 3, 1)
    rng = random.Random(2)
    polys = [random_poly(ring, rng, 2, 0.5) for _ in range(2)]
    for conv in ("per_layer", "cumulative"):
        L = analyze_layer(ring, polys, 3, conv)
        d = L.as_dict()
        assert d["convention"] == conv and d["mode"] == "mixed" and d["p"] == 65537
        assert d["frobenius_factor"] is False
        assert all(isinstance(d[k], int) for k in ("row_count", "top_rank", "full_rank", "fall_dim", "syzygy_dim"))
