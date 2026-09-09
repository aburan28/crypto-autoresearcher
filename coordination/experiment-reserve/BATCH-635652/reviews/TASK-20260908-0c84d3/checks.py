"""Independent fixed definition checks for TASK-20260908-0c84d3.

This program performs no curve generation, scientific sampling, null/control
panel, solver invocation, timing experiment, or prospective pipeline.  Its
only arithmetic objects are fixed integers, fixed rational ranks, abstract
index permutations, and fixed slope vectors.  Hash, parse, and Git custody
comparisons are administrative under the committed handoff and are reported
separately from the 120 counted cases.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import platform
import resource
import signal
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import yaml


TASK_ID = "TASK-20260908-0c84d3"
AUTHORITY_COMMIT = "7b36178fe6c0cc92242071bf42cb4e81c5aa0cc9"
CLAIM_COMMIT = "86a0b56ab699e7ee85316a7feffb9d57a66fd348"
SOURCE_SNAPSHOT = "a2367801c92ab890c7990b5f1aae98e7fe907402"
CASE_CAP = 240
PRIOR_CASE_EXECUTIONS = 120
PRIOR_SUITE_INVOCATIONS = 1
EXPECTED_CASES = 120
CASE_TIMEOUT_SECONDS = 10
AGGREGATE_WALL_CPU_CAP_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024**3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CURRENT_DIR = ROOT / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260908-689717"
THIRD_DIR = ROOT / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260908-92d6dd"
TOKENS = ("184fc4", "1e6502", "2c3d20")
HANDOFF_PATH = ROOT / "ledger/handoffs/TASK-20260908-0c84d3.yaml"


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


HANDOFF = read_yaml(HANDOFF_PATH)["handoff"]
CURRENT = {
    token: read_yaml(CURRENT_DIR / f"EXP-ECDLP-{token}.yaml")["protocol_amendment"]
    for token in TOKENS
}
THIRD = {
    token: read_yaml(THIRD_DIR / f"EXP-ECDLP-{token}.yaml")["protocol_amendment"]
    for token in TOKENS
}
ORIGINAL = {
    token: read_yaml(ROOT / f"experiments/EXP-ECDLP-{token}/specification.yaml")["experiment"]
    for token in TOKENS
}


def at(document: Any, dotted: str) -> Any:
    node = document
    for key in dotted.split("."):
        node = node[key]
    return node


def remove_path(document: dict[str, Any], dotted: str) -> None:
    keys = dotted.split(".")
    node: Any = document
    for key in keys[:-1]:
        if not isinstance(node, dict) or key not in node:
            return
        node = node[key]
    if isinstance(node, dict):
        node.pop(keys[-1], None)


META_PATHS = [
    "task_id",
    "predecessor_task_id",
    "revision_label",
    "authored_under_task",
    "correction_authority",
    "authorship",
    "inference",
    "precedence_and_source_map",
    "current_source_bindings",
    "third_correction_choices",
    "third_revision_history",
    "fourth_correction_choices",
]
ALLOWED_CHANGES = {
    "184fc4": [
        "effective_contract.permutation_null_and_inference.stream",
        "effective_contract.permutation_null_and_inference.joint_null_required",
        "effective_contract.permutation_null_and_inference.global_statistic",
        "effective_contract.permutation_null_and_inference.rank_interpretation",
        "effective_contract.decision_rules.concentration_candidate",
    ],
    "1e6502": [
        "effective_contract.spectral_null_and_delta_thresholds.family_statistic",
        "effective_contract.spectral_null_and_delta_thresholds.permutation_null",
        "effective_contract.spectral_null_and_delta_thresholds.sibling_definition_binding",
        "effective_contract.spectral_null_and_delta_thresholds.rank_interpretation",
        "effective_contract.spectral_null_and_delta_thresholds.general_candidate_threshold",
    ],
    "2c3d20": [
        "slopes.definition",
        "slopes.primary_abscissa",
        "slopes.logN_diagnostic",
        "null_inference_and_decisions.slope_review_candidate.identity",
        "null_inference_and_decisions.slope_review_candidate.original_falsifier",
    ],
}


def retained_fields_equal(token: str) -> bool:
    current = copy.deepcopy(CURRENT[token])
    predecessor = copy.deepcopy(THIRD[token])
    for dotted in META_PATHS + ALLOWED_CHANGES[token]:
        remove_path(current, dotted)
        remove_path(predecessor, dotted)
    return current == predecessor


def fixed_rank(observed: float | Fraction | None, references: list[Any], eligible: bool = True) -> Fraction | None:
    if not eligible or observed is None or len(references) != 64:
        return None
    try:
        observed_finite = math.isfinite(float(observed))
        references_finite = all(value is not None and math.isfinite(float(value)) for value in references)
    except (TypeError, ValueError, OverflowError):
        return None
    if not observed_finite or not references_finite:
        return None
    return Fraction(1 + sum(value >= observed for value in references), 65)


def ols_slope(xs: list[float], ys: list[float]) -> float:
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("zero x dispersion")
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denominator


def sample_sd(values: list[float]) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def slope_route_eligible(true_gamma: float | None, null_gammas: list[float | None]) -> bool:
    if true_gamma is None or len(null_gammas) != 64:
        return False
    try:
        if not math.isfinite(true_gamma) or any(value is None or not math.isfinite(value) for value in null_gammas):
            return False
    except TypeError:
        return False
    finite_nulls = [float(value) for value in null_gammas if value is not None]
    sd = sample_sd(finite_nulls)
    if not math.isfinite(sd) or sd <= 0:
        return False
    mean = sum(finite_nulls) / 64
    ordered = sorted(finite_nulls)
    median = (ordered[31] + ordered[32]) / 2
    rank = fixed_rank(true_gamma, finite_nulls)
    effect = (true_gamma - mean) / sd
    return rank == Fraction(1, 65) and effect >= 2 and true_gamma > -0.25 and median < 0


def is_prime_fixed(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def sparse_partial_fisher_yates(n: int, draws: list[int]) -> list[int]:
    if not (1 <= n <= 2**256):
        raise ValueError("invalid certified N")
    count = min(1000, n)
    if len(draws) != count:
        raise ValueError("missing fixed draws")
    sparse: dict[int, int] = {}
    emitted: list[int] = []
    for index in range(count):
        offset = draws[index]
        if not 0 <= offset < n - index:
            raise ValueError("draw out of range")
        selected = index + offset
        emitted_value = sparse.get(selected, selected)
        sparse[selected] = sparse.get(index, index)
        sparse.pop(index, None)
        emitted.append(emitted_value)
    return emitted


CaseFunction = Callable[[], tuple[bool, str] | bool]
CASES: list[tuple[str, str, CaseFunction]] = []


def case(name: str, target: str, function: CaseFunction) -> None:
    CASES.append((name, target, function))


def check_retained_and_flags(token: str) -> tuple[bool, str]:
    record = CURRENT[token]
    flags = (
        record.get("approved_by") is None
        and record.get("execution_authorized") is False
        and record.get("evidence_eligible") is False
        and record.get("scientific_runs") == 0
    )
    return retained_fields_equal(token) and flags, "all non-authorized predecessor fields equal; approval and science flags remain closed"


# EXP-ECDLP-184fc4: 16 non-orbit cases, 66 state cases, and one mass case.
ec184 = CURRENT["184fc4"]["effective_contract"]
case("184 retained complete contract and authority flags", "EXP-ECDLP-184fc4", lambda: check_retained_and_flags("184fc4"))
case(
    "184 exact finite counts",
    "EXP-ECDLP-184fc4",
    lambda: (
        ec184["exact_cell_accounting"]["primary_curve_bundles"] == 7 * 2 * 3 == 42
        and ec184["exact_cell_accounting"]["members_per_bundle"] == 567
        and ec184["exact_cell_accounting"]["observed_member_spectra"] == 42 * 567 == 23814
        and ec184["exact_cell_accounting"]["permutation_null_spectra"] == 23814 * 64 == 1524096,
        "42 bundles, 567 members, 23814 observations, 1524096 references",
    ),
)
case(
    "184 member family and exceptional value",
    "EXP-ECDLP-184fc4",
    lambda: (
        sum([2, 3, 4, 5, 7, 8, 16, 32, 64, 128, 256]) + sum([2, 4, 8]) + 9 + 16 + 3 == 567
        and ec184["frozen_library"]["member_count"] == 567
        and "Every raw library member is defined to be zero at O" in ec184["frozen_library"]["exceptional_value"],
        "all frozen members and O are total",
    ),
)
case(
    "184 transform domains ties and degeneracy",
    "EXP-ECDLP-184fc4",
    lambda: (
        "a=1,...,N-1" in ec184["exact_spectrum_definitions"]["nonzero_domain"]
        and "breaking ties by increasing a" in ec184["exact_spectrum_definitions"]["half_energy"]
        and "Var(g)=0" in ec184["exact_spectrum_definitions"]["half_energy"]
        and "least a" in " ".join(ec184["exact_spectrum_definitions"]["exact_invariants"]),
        "nonzero spectrum, pair ties, and null degeneracy are explicit",
    ),
)
case(
    "184 exact real and order-2q controls",
    "EXP-ECDLP-184fc4",
    lambda: (
        "two conjugate peaks" in ec184["synthetic_real_cosine_control"]["required_signature"]
        and "every ordered pair" in " ".join(ec184["descent_control"]["blocking_checks"])
        and "delta(O)=+1" in ec184["descent_control"]["definition"]
        and "delta(T)=Legendre(3*e^2+A)" in ec184["descent_control"]["definition"]
        and "sole nonzero coefficient is H_q=2q" in ec184["descent_control"]["required_signature"],
        "control definitions cover O, T, every ordered pair, parity, and exact spectra",
    ),
)
rank184 = ec184["permutation_null_and_inference"]["rank_interpretation"]
case(
    "184 descriptive rank and unadopted calibration premises",
    "EXP-ECDLP-184fc4",
    lambda: (
        "deterministic descriptive comparison" in rank184["actual_interpretation"]
        and "not an exact or approximate calibrated p-value" in rank184["actual_interpretation"]
        and set(rank184["calibration_boundary"]) == {"A_ASSIGN", "A_SAMPLER", "status", "required_before_calibrated_claim"}
        and "neither is adopted" in rank184["calibration_boundary"]["status"]
        and "not asserted orvalidated" in rank184["calibration_boundary"]["A_SAMPLER"],
        "actual fixed SHA rank has no probability claim; A_ASSIGN and A_SAMPLER are future requirements",
    ),
)
case(
    "184 fixed eligible 42-cell family and all 64 references",
    "EXP-ECDLP-184fc4",
    lambda: (
        "all42cells" in ec184["permutation_null_and_inference"]["global_statistic"]
        and "r=0..63" in rank184["formula"]
        and "Retain all64reference statistics" in rank184["formula"]
        and ec184["permutation_null_and_inference"]["resamples"] == 64,
        "the unchanged family maximum has exactly 42 cells and 64 fixed comparisons",
    ),
)
case("184 minimum finite rank", "EXP-ECDLP-184fc4", lambda: (fixed_rank(2, [1] * 64) == Fraction(1, 65), "minimum is 1/65"))
case("184 maximum rank with all ties", "EXP-ECDLP-184fc4", lambda: (fixed_rank(1, [1] * 64) == 1, "all 64 equalities count against separation"))
case("184 one tied reference", "EXP-ECDLP-184fc4", lambda: (fixed_rank(1, [1] + [0] * 63) == Fraction(2, 65), "one equality gives 2/65"))
case(
    "184 empty missing and nonfinite refusal",
    "EXP-ECDLP-184fc4",
    lambda: (
        fixed_rank(1, [0] * 64, eligible=False) is None
        and fixed_rank(None, [0] * 64) is None
        and fixed_rank(1, [0] * 63) is None
        and fixed_rank(float("nan"), [0] * 64) is None
        and fixed_rank(1, [0] * 63 + [float("inf")]) is None
        and all(token in rank184["missing"] for token in ["empty eligible", "missing required", "nonfinite", "denominator", "redraw"]),
        "empty, missing, short, NaN, and infinity cases are unavailable without redraw",
    ),
)
case(
    "184 zero dispersion and ratio refusal",
    "EXP-ECDLP-184fc4",
    lambda: (
        "cannot satisfy a decision threshold" in ec184["permutation_null_and_inference"]["zero_dispersion_and_ratio_rules"]
        and "strictly positive finite median" in ec184["permutation_null_and_inference"]["zero_dispersion_and_ratio_rules"]
        and fixed_rank(2, [1] * 64) == Fraction(1, 65),
        "finite rank remains descriptive while standardized effect and nonpositive ratio are null",
    ),
)
hash184 = ec184["canonical_hash_schedules"]
case(
    "184 actual-value hash domains",
    "EXP-ECDLP-184fc4",
    lambda: (
        "|bits=" in hash184["curve_tag"] and "|stratum=" in hash184["curve_tag"] and "|replicate=" in hash184["curve_tag"]
        and "|r=" in hash184["null_tag"]
        and "actual values" in hash184["numeric_encoding"]
        and "EXP-ECDLP-184fc4|primary|bits=12|stratum=A|replicate=20260905"
        != "EXP-ECDLP-184fc4|primary|bits=12|stratum=B|replicate=20260905",
        "actual bit, stratum, replicate, kind, and null index bytes are distinct",
    ),
)
case(
    "184 unbiased bounded-draw boundaries",
    "EXP-ECDLP-184fc4",
    lambda: (
        (lambda modulus: (modulus - 1) < modulus and not (modulus < modulus))(3 * (2**256 // 3))
        and "V<M" in hash184["unbiased_bounded_draw"]
        and "n=1 still consumes one" in hash184["unbiased_bounded_draw"]
        and "all4096attempts reject" in hash184["unbiased_bounded_draw"],
        "V=M-1 accepts, V=M rejects, n=1 consumes, and exhaustion is total",
    ),
)
case(
    "184 sparse distinct certificate schedule",
    "EXP-ECDLP-184fc4",
    lambda: (
        sparse_partial_fisher_yates(5, [4, 0, 1, 0, 0]) == [4, 1, 3, 2, 0]
        and len(set(sparse_partial_fisher_yates(5, [4, 0, 1, 0, 0]))) == 5
        and "exactlymindices on success" in hash184["certificate_indices"]
        and "preserve partial indices" in hash184["certificate_check"],
        "fixed abstract draw emits five distinct ordered indices and preserves exhaustion prefixes",
    ),
)
case(
    "184 slopes bootstrap stopping artifacts and ceiling",
    "EXP-ECDLP-184fc4",
    lambda: (
        "six slopes" in ec184["slope_definitions"]["full_ladder"]
        and "64 matched null trajectories" in ec184["slope_definitions"]["null_slopes"]
        and "exactly10000 paired draws" in ec184["slope_definitions"]["interval"]
        and "Reuse that exact replicate triple" in ec184["slope_definitions"]["bootstrap_rng_schedule"]["sharing"]
        and "entire interval is null" in ec184["slope_definitions"]["bootstrap_rng_schedule"]["missing"]
        and len(ec184["required_artifacts"]) == 12
        and "42 declared artifacts" in " ".join(ec184["stopping_and_invalidation"])
        and "toy measurement" in ec184["proof_search_map"]["method_ceiling"],
        "six observed slopes, 64 matched slopes, fixed bootstrap, stop, artifacts, and toy ceiling are total",
    ),
)


def orbit_numerator(state: int) -> int:
    values = [66 - index for index in range(66)]
    return 1 + sum(values[(state + shift) % 66] >= values[state] for shift in range(1, 65))


for orbit_state in range(66):
    case(
        f"184 fixed 66-state assignment orbit state {orbit_state}",
        "EXP-ECDLP-184fc4",
        lambda orbit_state=orbit_state: (
            orbit_numerator(orbit_state) == max(1, orbit_state),
            f"state {orbit_state} numerator is {orbit_numerator(orbit_state)}",
        ),
    )
case(
    "184 assignment-only calibration counterexample mass",
    "EXP-ECDLP-184fc4",
    lambda: (
        Fraction(sum(orbit_numerator(state) == 1 for state in range(66)), 66) == Fraction(1, 33) > Fraction(1, 65),
        "two of 66 uniform base states receive nominal minimum 1/65",
    ),
)


# EXP-ECDLP-1e6502: 16 cases.
ec1e = CURRENT["1e6502"]["effective_contract"]
spectral1e = ec1e["spectral_null_and_delta_thresholds"]
rank1e = spectral1e["rank_interpretation"]
binding1e = spectral1e["sibling_definition_binding"]
case("1e retained complete contract and authority flags", "EXP-ECDLP-1e6502", lambda: check_retained_and_flags("1e6502"))
case(
    "1e precision member definitions",
    "EXP-ECDLP-1e6502",
    lambda: (
        ec1e["eight_base_digits"]["count"] == 8
        and ec1e["sixteen_post_functions"]["per_digit_count"] == 16
        and ec1e["sixteen_post_functions"]["total_post_function_members"] == 128
        and "102 spectra" in ec1e["precision_specific_analysis_sets"]["precision_2"]
        and "136 spectra" in ec1e["precision_specific_analysis_sets"]["precision_3"],
        "precision two has 102 and precision three has 136 named spectra",
    ),
)
case(
    "1e combined local member precision cell family",
    "EXP-ECDLP-1e6502",
    lambda: (
        all(token in spectral1e["family_statistic"] for token in ["member,precision,cell", "102at2", "136at3", "all36ordinary", "r=0..63", "local precision-specific"])
        and (102 + 136) * 36 == 8568
        and max(Fraction(5, 2), Fraction(7, 2)) == Fraction(7, 2)
        and fixed_rank(Fraction(7, 2), [Fraction(3)] * 64) == Fraction(1, 65),
        "one maximum spans all 8568 local entries and each same-index reference spans the same family",
    ),
)
expected_sibling_fields = [
    "effective_contract.exact_spectrum_definitions",
    "effective_contract.permutation_null_and_inference.finite_null_summary_and_tie_rules",
    "effective_contract.permutation_null_and_inference.zero_dispersion_and_ratio_rules",
]
case(
    "1e exact narrow sibling path hash and field set",
    "EXP-ECDLP-1e6502",
    lambda: (
        binding1e["fields"] == expected_sibling_fields
        and sha256(ROOT / binding1e["path"]) == binding1e["sha256"]
        and binding1e["sha256"] == "41768339fb7ba04e6268f3a37149238bf909dfc3f3e852fe966d346582006015",
        "the current 184 sibling and exactly three generic fields are bound",
    ),
)
case("1e sibling spectrum field resolves", "EXP-ECDLP-1e6502", lambda: (at(CURRENT["184fc4"], expected_sibling_fields[0]) == ec184["exact_spectrum_definitions"], "exact spectrum mapping exists"))
case("1e sibling finite summary field resolves", "EXP-ECDLP-1e6502", lambda: (at(CURRENT["184fc4"], expected_sibling_fields[1]) == ec184["permutation_null_and_inference"]["finite_null_summary_and_tie_rules"], "finite summary mapping exists"))
case("1e sibling zero dispersion field resolves", "EXP-ECDLP-1e6502", lambda: (at(CURRENT["184fc4"], expected_sibling_fields[2]) == ec184["permutation_null_and_inference"]["zero_dispersion_and_ratio_rules"], "zero-dispersion mapping exists"))
case(
    "1e sibling excludes 567 and 42 family constants",
    "EXP-ECDLP-1e6502",
    lambda: (
        all("permutation_null_and_inference" != field for field in binding1e["fields"])
        and "no567/42" in binding1e["scope"]
        and "remain exclusively local" in binding1e["scope"],
        "no whole sibling family mapping is imported",
    ),
)
hash1e = ec1e["canonical_hash_schedules"]
case(
    "1e precision-local streams and descriptive rank",
    "EXP-ECDLP-1e6502",
    lambda: (
        "|precision=" in hash1e["null_tag"]
        and "Different precisions" in spectral1e["permutation_null"]
        and "combined reference maximum is descriptive" in spectral1e["permutation_null"]
        and "deterministic descriptive comparison" in rank1e["actual_interpretation"]
        and "not an exact or approximate calibrated p-value" in rank1e["actual_interpretation"],
        "precision 2 and 3 keys stay separate and the combined rank is non-inferential",
    ),
)
case(
    "1e full ordered-pair domain includes exceptional pairs",
    "EXP-ECDLP-1e6502",
    lambda: (
        len([(i, j) for i in range(5) for j in range(5)]) == 25
        and (0, 0) in [(i, j) for i in range(5) for j in range(5)]
        and (2, 2) in [(i, j) for i in range(5) for j in range(5)]
        and (1, 4) in [(i, j) for i in range(5) for j in range(5)]
        and all(token in ec1e["blocking_pair_schedules"]["domain"] for token in ["every ordered pair", "including O", "equality", "inverse"]),
        "abstract n=5 enumeration contains O, equality, and inverse pairs",
    ),
)
case(
    "1e larger pair schedule is exact and retained",
    "EXP-ECDLP-1e6502",
    lambda: (
        all(token in ec1e["blocking_pair_schedules"]["larger_rungs"] for token in ["t=0..9999", "slot s=0,1", "Slots0,1 define the ordered pair", "Retain all duplicates", "exact10000 rows"])
        and "identical ordinary schedule" in ec1e["blocking_pair_schedules"]["sharing"]
        and "distinct anomalous-tag" in ec1e["blocking_pair_schedules"]["sharing"],
        "10,000 ordered pairs retain duplicates and have explicit ordinary/anomalous sharing",
    ),
)
case(
    "1e five controls refusal and disjoint order predicates",
    "EXP-ECDLP-1e6502",
    lambda: (
        [row["id"] for row in ec1e["five_blocking_self_checks"]]
        == ["SC1_torsion_homomorphism", "SC2_naive_defect_nonadditivity", "SC3_precision_consistency", "SC4_first_order_translation", "SC5_anomalous_recovery"]
        and "including O, equality and inverse" in ec1e["blocking_pair_schedules"]["domain"]
        and "bits10,stratumA,replicate20260905" in ec1e["five_blocking_self_checks"][4]["exact_test"]
        and "If that exact ordinary bundle is missing" in ec1e["five_blocking_self_checks"][4]["exact_test"]
        and "gcd(N,p)=1" in ec1e["prime_to_p_torsion_section"]["refusal_domain"]
        and "requires #E(F_p)=p" in ec1e["anomalous_sigma_algorithm"]["domain_refusal"],
        "SC1-SC5 are total; refusal fixture is exact; anomalous and ordinary domains are disjoint",
    ),
)
case(
    "1e fixed digit and Teichmuller identities",
    "EXP-ECDLP-1e6502",
    lambda: (
        tuple((32 // (5**index)) % 5 for index in range(3)) == (2, 1, 1)
        and pow(2, 5, 25) == 7
        and pow(2, 25, 125) == 57
        and 57 % 25 == 7
        and "Subtracting only c0 is forbidden" in ec1e["eight_base_digits"]["coordinate_digit_operator"]
        and "T_s(x0)=x0^(p^(s-1))" in ec1e["lifted_curve_and_hensel_section"]["teichmuller_x"],
        "the corrected source agrees with the archived fixed digit and precision identities",
    ),
)
case(
    "1e exact cell and recovery accounting",
    "EXP-ECDLP-1e6502",
    lambda: (
        ec1e["exact_cell_accounting"]["nonanomalous_curve_bundles"] == 6 * 2 * 3 == 36
        and ec1e["exact_cell_accounting"]["observed_nonanomalous_spectra"] == 36 * (102 + 136) == 8568
        and ec1e["exact_cell_accounting"]["permutation_null_spectra"] == 8568 * 64 == 548352
        and ec1e["exact_cell_accounting"]["anomalous_scalar_instances_target"] == 4 * 2 * 3 * 20 == 480,
        "36 bundles, 8568 spectra, 548352 references, and 480 target recoveries recompute",
    ),
)
case(
    "1e candidate all-reference and missing branches",
    "EXP-ECDLP-1e6502",
    lambda: (
        "p_joint=1/65" in spectral1e["general_candidate_threshold"]
        and "top-two-size median observed/null spike ratio is at least two in both" in spectral1e["general_candidate_threshold"]
        and "Retain all64reference statistics" in rank1e["formula"]
        and all(token in rank1e["missing"] for token in ["empty eligible", "missing required", "nonfinite", "denominator", "redraw"]),
        "the unchanged numeric gate uses the complete descriptive family and refuses incomplete values",
    ),
)
case(
    "1e stopping artifacts and method ceiling",
    "EXP-ECDLP-1e6502",
    lambda: (
        len(ec1e["required_artifacts"]) == 14
        and "Stop after 36 run artifacts" in " ".join(ec1e["stopping_and_invalidation"])
        and "watchdog stop censors" in " ".join(ec1e["stopping_and_invalidation"])
        and "all 136 member names" in ec1e["proof_search_map"]["quantifier_order"]
        and "toy curves" in ec1e["proof_search_map"]["method_ceiling"],
        "artifacts, counts, failures, all-member quantifier, and toy ceiling are explicit",
    ),
)


# EXP-ECDLP-2c3d20: 21 cases.
ec2c = CURRENT["2c3d20"]
slopes2c = ec2c["slopes"]
candidate2c = ec2c["null_inference_and_decisions"]["slope_review_candidate"]
case("2c retained complete contract and authority flags", "EXP-ECDLP-2c3d20", lambda: check_retained_and_flags("2c3d20"))
case(
    "2c immutable original registers log p slope",
    "EXP-ECDLP-2c3d20",
    lambda: (
        "slope gamma against log p" in ORIGINAL["2c3d20"]["metrics"]["primary"][0]
        and "lambda_2 slope above -0.25" in ORIGINAL["2c3d20"]["falsification_criterion"][2],
        "the original primary observable and strict threshold are source-bound",
    ),
)
case(
    "2c primary observed and matched-null slopes use ln p",
    "EXP-ECDLP-2c3d20",
    lambda: (
        "x=ln(p)" in slopes2c["definition"]
        and "natural log(p)" in candidate2c["identity"]
        and "observed andevery matched-null" in slopes2c["primary_abscissa"]
        and "Both true_gamma andall null_gamma" in candidate2c["original_falsifier"]
        and "no ln(N)surrogate" in candidate2c["original_falsifier"],
        "observed and every same-index null use actual p on all seven rungs",
    ),
)
case(
    "2c itinerary log N remains descriptive and separate",
    "EXP-ECDLP-2c3d20",
    lambda: (
        "descriptive x=ln(N) convention" in slopes2c["definition"]
        and "cannot trigger orreplace sigma_center_slope" in slopes2c["logN_diagnostic"]
        and ec2c["null_inference_and_decisions"]["statistic_inventory"][-1]["key"] == "itinerary_summary_slope"
        and ec2c["null_inference_and_decisions"]["statistic_inventory"][-1]["candidate_eligible"] is False,
        "N is retained only for the separately identified itinerary diagnostic",
    ),
)

FIXED_PRIMES = [4093, 16381, 65521, 262139, 1048573, 4194301, 16777213]
FIXED_BITS = [12, 14, 16, 18, 20, 22, 24]
FIXED_ORDERS = [prime + 1 + 2 * math.isqrt(prime) for prime in FIXED_PRIMES]
for bits, prime, order in zip(FIXED_BITS, FIXED_PRIMES, FIXED_ORDERS):
    case(
        f"2c fixed prime and Hasse-compatible order at {bits} bits",
        "EXP-ECDLP-2c3d20",
        lambda bits=bits, prime=prime, order=order: (
            prime.bit_length() == bits
            and is_prime_fixed(prime)
            and order != prime
            and abs(order - (prime + 1)) <= 2 * math.sqrt(prime),
            f"p={prime}, N={order}",
        ),
    )


def finite_axis_witness() -> tuple[bool, str]:
    x_p = [math.log(prime) for prime in FIXED_PRIMES]
    x_n = [math.log(order) for order in FIXED_ORDERS]
    y = [-0.2499 * value for value in x_p]
    gamma_p = ols_slope(x_p, y)
    gamma_n = ols_slope(x_n, y)
    return gamma_p > -0.25 and gamma_n < -0.25 and abs(gamma_p - gamma_n) > 1e-6, f"gamma_p={gamma_p:.12f}, gamma_N={gamma_n:.12f}"


case("2c finite p versus N threshold witness", "EXP-ECDLP-2c3d20", finite_axis_witness)
fixed_null_gammas = [-0.49 - 0.02 * index / 63 for index in range(64)]
case(
    "2c all 64 matched slopes satisfy restored route",
    "EXP-ECDLP-2c3d20",
    lambda: (
        slope_route_eligible(0.0, fixed_null_gammas)
        and len(fixed_null_gammas) == 64
        and "SAME null index" in candidate2c["matched_null"]
        and "Every observed and all64null trajectories" in candidate2c["matched_null"],
        "flat observed slope, 64 decaying same-index null slopes, rank 1/65, finite effect",
    ),
)
case(
    "2c slope route remains independent of tied scalar route",
    "EXP-ECDLP-2c3d20",
    lambda: (
        fixed_rank(1.0, [1.0] * 64) == 1
        and sample_sd([1.0] * 64) == 0
        and slope_route_eligible(0.0, fixed_null_gammas)
        and "EITHER" in ec2c["null_inference_and_decisions"]["review_candidate"]
        and "does not inherit" in ec2c["null_inference_and_decisions"]["review_candidate"],
        "scalar top-rung tie is ineligible while the independently complete slope route holds",
    ),
)
case("2c strict true gamma boundary", "EXP-ECDLP-2c3d20", lambda: (not slope_route_eligible(-0.25, fixed_null_gammas), "equality at -1/4 does not trigger"))
case("2c null median must decay", "EXP-ECDLP-2c3d20", lambda: (not slope_route_eligible(0.1, [-0.1] * 32 + [0.1] * 32), "median zero does not trigger"))
case("2c zero null dispersion is ineligible", "EXP-ECDLP-2c3d20", lambda: (not slope_route_eligible(0.0, [-0.5] * 64), "zero scale cannot become infinite effect"))
case(
    "2c missing nonfinite and incomplete slope refusal",
    "EXP-ECDLP-2c3d20",
    lambda: (
        not slope_route_eligible(None, fixed_null_gammas)
        and not slope_route_eligible(0.0, fixed_null_gammas[:-1])
        and not slope_route_eligible(float("nan"), fixed_null_gammas)
        and not slope_route_eligible(0.0, fixed_null_gammas[:-1] + [float("inf")])
        and "missing/invalid or SD nonpositive/nonfinite" in candidate2c["missing"],
        "missing, 63-reference, NaN, infinity, and nonpositive-scale branches cannot trigger",
    ),
)
case(
    "2c both strata same replicates r and partition identity",
    "EXP-ECDLP-2c3d20",
    lambda: (
        all(token in candidate2c["replication"] for token in ["BOTH strata", "SAME at leasttwo", "SAME r andpartition"])
        and CURRENT["2c3d20"]["frozen_scope"]["curve_strata"] == ["A", "B"]
        and CURRENT["2c3d20"]["frozen_scope"]["replicate_seeds"] == [20260905, 20260906, 20260907],
        "one r/partition and the same at least two replicate labels must hold in A and B",
    ),
)
case(
    "2c exact map matrix and slope counts",
    "EXP-ECDLP-2c3d20",
    lambda: (
        ec2c["exact_cell_accounting"]["primary_curve_bundles"] == 7 * 2 * 3 == 42
        and ec2c["exact_cell_accounting"]["primary_true_maps"] == 42 * 4 == 168
        and ec2c["exact_cell_accounting"]["primary_null_maps"] == 168 * 64 == 10752
        and ec2c["exact_cell_accounting"]["true_lumped_matrices"] == 168 * 40 == 6720
        and ec2c["exact_cell_accounting"]["null_lumped_matrices"] == 10752 * 40 == 430080
        and ec2c["exact_cell_accounting"]["lumped_slope_trajectories_true"] == 2 * 3 * 4 * 40 == 960
        and ec2c["exact_cell_accounting"]["lumped_slope_trajectories_null"] == 960 * 64 == 61440,
        "all seven typed fixed totals recompute",
    ),
)
case(
    "2c controls stopping artifacts and method ceiling",
    "EXP-ECDLP-2c3d20",
    lambda: (
        "for all pairs/scalars" in ec2c["order_2q_known_true_control"]["descent_symbol"]
        and "delta(O)=1" in ec2c["order_2q_known_true_control"]["descent_symbol"]
        and "delta(T)=Legendre(Delta)" in ec2c["order_2q_known_true_control"]["descent_symbol"]
        and len(ec2c["controls"]["blocking"]) == 8
        and "Stop at 42 complete primary bundles" in " ".join(ec2c["invalidation_and_stopping"])
        and len(ec2c["required_artifacts_for_future_execution"]) == 14
        and "toy diagnostic" in ec2c["proof_search_map"]["method_ceiling"],
        "full order-2q pairs, eight blocking controls, 42-stop, artifacts, and toy ceiling are explicit",
    ),
)


def git_bytes(revision: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)


def administrative_checks() -> dict[str, Any]:
    bindings = HANDOFF["source_bindings"]
    binding_rows = []
    parse_failures = []
    total_bytes = 0
    for entry in bindings:
        path = entry["path"]
        raw = git_bytes(AUTHORITY_COMMIT, path)
        live = (ROOT / path).read_bytes()
        total_bytes += len(live)
        authority_hash = hashlib.sha256(raw).hexdigest()
        live_hash = hashlib.sha256(live).hexdigest()
        binding_rows.append(
            {
                "path": path,
                "expected_sha256": entry["sha256"],
                "authority_sha256": authority_hash,
                "live_sha256": live_hash,
                "match": authority_hash == live_hash == entry["sha256"],
            }
        )
        try:
            if path.endswith((".yaml", ".yml")):
                yaml.safe_load(live)
            elif path.endswith(".json"):
                json.loads(live)
        except Exception as error:  # pragma: no cover - recorded failure path
            parse_failures.append({"path": path, "error": f"{type(error).__name__}: {error}"})
    claim_parent = subprocess.check_output(["git", "rev-parse", f"{CLAIM_COMMIT}^"], cwd=ROOT, text=True).strip()
    snapshot_parent = subprocess.check_output(["git", "rev-parse", f"{SOURCE_SNAPSHOT}^"], cwd=ROOT, text=True).strip()
    snapshot_receipt = json.loads(
        (ROOT / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260908-4ea7b6/snapshot.json").read_text()
    )
    snapshot_rows = []
    for path, expected in snapshot_receipt["source_path_sha256"].items():
        actual = hashlib.sha256(git_bytes(SOURCE_SNAPSHOT, path)).hexdigest()
        snapshot_rows.append({"path": path, "expected_sha256": expected, "snapshot_sha256": actual, "match": actual == expected})
    return {
        "declared_input_count": len(HANDOFF["inputs"]),
        "declared_binding_count": len(bindings),
        "input_binding_paths_exact": HANDOFF["inputs"] == [entry["path"] for entry in bindings],
        "declared_bytes_read": total_bytes,
        "binding_match_count": sum(row["match"] for row in binding_rows),
        "binding_failure_count": sum(not row["match"] for row in binding_rows),
        "binding_mismatches": [row for row in binding_rows if not row["match"]],
        "structured_parse_failures": parse_failures,
        "authority_handoff_matches_claim": git_bytes(AUTHORITY_COMMIT, "ledger/handoffs/TASK-20260908-0c84d3.yaml")
        == git_bytes(CLAIM_COMMIT, "ledger/handoffs/TASK-20260908-0c84d3.yaml"),
        "claim_parent": claim_parent,
        "claim_parent_matches_authority": claim_parent == AUTHORITY_COMMIT,
        "snapshot_parent": snapshot_parent,
        "snapshot_parent_matches_receipt": snapshot_parent == snapshot_receipt["parent_sha"],
        "snapshot_binding_count": len(snapshot_rows),
        "snapshot_binding_match_count": sum(row["match"] for row in snapshot_rows),
        "snapshot_mismatches": [row for row in snapshot_rows if not row["match"]],
    }


def timeout_handler(_signum: int, _frame: Any) -> None:
    raise TimeoutError("fixed case exceeded ten-second watchdog")


def install_memory_limit() -> dict[str, Any]:
    result = {"requested_bytes": MEMORY_LIMIT_BYTES, "installed": False, "error": None}
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        result["prior_soft"] = soft
        result["prior_hard"] = hard
        new_hard = MEMORY_LIMIT_BYTES if hard in (-1, resource.RLIM_INFINITY) else min(hard, MEMORY_LIMIT_BYTES)
        resource.setrlimit(resource.RLIMIT_AS, (min(MEMORY_LIMIT_BYTES, new_hard), new_hard))
        result["installed"] = True
        result["effective_soft"], result["effective_hard"] = resource.getrlimit(resource.RLIMIT_AS)
    except Exception as error:  # Darwin commonly rejects useful RLIMIT_AS values.
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def normalize_outcome(value: tuple[bool, str] | bool) -> tuple[bool, str]:
    if isinstance(value, tuple):
        return bool(value[0]), str(value[1])
    return bool(value), ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count-only", action="store_true")
    args = parser.parse_args()
    if len(CASES) != EXPECTED_CASES:
        raise AssertionError(f"planned case count {len(CASES)} != {EXPECTED_CASES}")
    if len({name for name, _, _ in CASES}) != len(CASES):
        raise AssertionError("duplicate case name")
    remaining_before = CASE_CAP - PRIOR_CASE_EXECUTIONS
    if args.count_only:
        print(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "prior_case_executions": PRIOR_CASE_EXECUTIONS,
                    "planned_final_suite_cases": len(CASES),
                    "remaining_before_suite": remaining_before,
                    "complete_rerun_reserved": remaining_before >= 2 * len(CASES),
                    "case_cap": CASE_CAP,
                },
                indent=2,
            )
        )
        return 0
    if remaining_before < len(CASES):
        raise RuntimeError("insufficient cumulative case allowance")

    memory_limit = install_memory_limit()
    administrative_started = time.perf_counter()
    administrative_cpu_started = time.process_time()
    administrative = administrative_checks()
    administrative_wall = time.perf_counter() - administrative_started
    administrative_cpu = time.process_time() - administrative_cpu_started

    signal.signal(signal.SIGALRM, timeout_handler)
    suite_started = time.perf_counter()
    suite_cpu_started = time.process_time()
    rows = []
    for name, target, function in CASES:
        row: dict[str, Any] = {"name": name, "target": target, "status": "started"}
        rows.append(row)
        started = time.perf_counter()
        cpu_started = time.process_time()
        signal.alarm(CASE_TIMEOUT_SECONDS)
        try:
            passed, detail = normalize_outcome(function())
            if not passed:
                raise AssertionError(detail or name)
            row["status"] = "passed"
            row["detail"] = detail
        except BaseException as error:  # Every failed attempt remains visible.
            row["status"] = "failed"
            row["error"] = f"{type(error).__name__}: {error}"
        finally:
            signal.alarm(0)
            row["wall_seconds"] = time.perf_counter() - started
            row["cpu_seconds"] = time.process_time() - cpu_started

    suite_wall = time.perf_counter() - suite_started
    suite_cpu = time.process_time() - suite_cpu_started
    maximum_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    receipt = {
        "schema": "crypto.autoresearch.independent_fixed_definition_checks.v1",
        "task_id": TASK_ID,
        "authority_commit": AUTHORITY_COMMIT,
        "claim_commit": CLAIM_COMMIT,
        "source_snapshot": SOURCE_SNAPSHOT,
        "suite_invocations_this_resume": PRIOR_SUITE_INVOCATIONS + 1,
        "current_suite_invocation": PRIOR_SUITE_INVOCATIONS + 1,
        "prior_case_executions": PRIOR_CASE_EXECUTIONS,
        "executed_cases_this_invocation": len(rows),
        "cumulative_case_executions": PRIOR_CASE_EXECUTIONS + len(rows),
        "passed": sum(row["status"] == "passed" for row in rows),
        "failed": sum(row["status"] != "passed" for row in rows),
        "case_cap": CASE_CAP,
        "unused_cases": CASE_CAP - PRIOR_CASE_EXECUTIONS - len(rows),
        "maximum_seconds_per_case": CASE_TIMEOUT_SECONDS,
        "maximum_aggregate_wall_cpu_seconds": AGGREGATE_WALL_CPU_CAP_SECONDS,
        "suite_wall_seconds": suite_wall,
        "suite_cpu_seconds": suite_cpu,
        "administrative_wall_seconds": administrative_wall,
        "administrative_cpu_seconds": administrative_cpu,
        "maximum_case_wall_seconds": max(row["wall_seconds"] for row in rows),
        "maximum_case_cpu_seconds": max(row["cpu_seconds"] for row in rows),
        "maximum_observed_rss_bytes": maximum_rss,
        "rss_units": "bytes on Darwin; platform-dependent getrusage units elsewhere",
        "workers": 1,
        "memory_limit": memory_limit,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "scientific_runs": 0,
        "prospective_pipelines": 0,
        "cases": rows,
        "administrative_checks": administrative,
        "contract_sha256": {
            token: sha256(CURRENT_DIR / f"EXP-ECDLP-{token}.yaml") for token in TOKENS
        },
        "checker_sha256": sha256(Path(__file__)),
        "interpretation": "Fixed definition, serialization, index, and arithmetic checks only; no scientific evidence, model-serving proof, approval, launch admission, or status transition.",
    }
    print(json.dumps(receipt, indent=2))
    return 1 if receipt["failed"] or administrative["binding_failure_count"] or administrative["structured_parse_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
