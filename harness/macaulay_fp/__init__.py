"""harness.macaulay_fp -- exact F_p Macaulay deficit meter (TASK-20260903-ba41aa).

Port of ``experiments/EXP-SBRG-60c55e/driver/macaulay.py`` (Boolean, p = 2) to
any prime p with three ring modes (squarefree / digit, ordinary-monomial,
mixed), two multiplier conventions (per-layer, cumulative), the rank profile,
fall_dim, syzygy_dim, Koszul counts and series-based deficits, the
EXP-ALPF-013 localization bit, three null generators plus a coefficient-
scramble primitive, arbitrary-precision residues (Python ints), and a
pre-flight row / column gate.  Pure standard library; see VALIDATION.md.
"""

from .columns import ColumnSpace, PreflightAbort, PreflightCounts, multiplier_count, preflight
from .koszul import frobenius_count, koszul_count, koszul_pair_count
from .linalg import Echelon, EchelonStats, rank_of
from .localization import LocalizationResult, localization_gate
from .macaulay import (
    CONVENTIONS,
    DeficitProfile,
    LayerResult,
    RowProvenance,
    analyze_degrees,
    analyze_layer,
    deficit_profile,
    fall_content_contains,
    first_excess_fall,
    first_nontrivial_syzygy,
    first_nonzero_fall,
    generator_degrees,
    layer_rows,
    verify_layer_two_eliminations,
)
from .nulls import (
    NullMeta,
    block_factored_generator,
    block_factored_system,
    dreg_boolean_null,
    histogram_matched_polynomial,
    histogram_matched_system,
    random_form,
    scramble_coefficients,
    support_matched_system,
)
from .poly import Monomial, Poly, Ring, boolean_masks_to_poly, poly_from_terms, poly_to_boolean_masks
from .presentations import (
    Presentation,
    digit_presentation,
    direct_presentation,
    f_V,
    membership_generator,
    rename_direct_to_digit_s1,
    substitute,
)
from .series import SeriesPrediction, default_frobenius, growth_of_extra_generator, semiregular_prediction

P256_PRIME = 2**256 - 2**224 + 2**192 + 2**96 - 1

__all__ = [
    "CONVENTIONS", "P256_PRIME",
    "Ring", "Poly", "Monomial", "poly_from_terms", "boolean_masks_to_poly", "poly_to_boolean_masks",
    "ColumnSpace", "PreflightAbort", "PreflightCounts", "preflight", "multiplier_count",
    "Echelon", "EchelonStats", "rank_of",
    "LayerResult", "RowProvenance", "DeficitProfile", "layer_rows", "analyze_layer", "analyze_degrees",
    "deficit_profile", "first_nonzero_fall", "first_excess_fall", "first_nontrivial_syzygy",
    "generator_degrees", "verify_layer_two_eliminations", "fall_content_contains",
    "SeriesPrediction", "semiregular_prediction", "growth_of_extra_generator", "default_frobenius",
    "koszul_count", "koszul_pair_count", "frobenius_count",
    "LocalizationResult", "localization_gate",
    "NullMeta", "histogram_matched_polynomial", "histogram_matched_system", "dreg_boolean_null",
    "support_matched_system", "random_form", "block_factored_generator", "block_factored_system",
    "scramble_coefficients",
    "Presentation", "direct_presentation", "digit_presentation", "membership_generator", "f_V",
    "substitute", "rename_direct_to_digit_s1",
]
