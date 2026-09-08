#!/usr/bin/env python3
"""Fixed zero-run checks for TASK-20260908-5b034f.

This program parses the five source-bound prospective contracts and evaluates
17 predetermined arithmetic, static, and mock cases.  A PASS on an
``expected_finding`` case means the named definition gap was reproduced; it
does not mean the corresponding experiment contract passed review.
"""

from __future__ import annotations

import math
import struct
import time
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[5]
CORRECTIONS = ROOT / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260907-8e3963"
EXPERIMENT_IDS = (
    "EXP-ECDLP-184fc4",
    "EXP-ECDLP-0c717c",
    "EXP-ECDLP-1e6502",
    "EXP-ECDLP-2c3d20",
    "EXP-ECDLP-709063",
)


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)


DOCS: dict[str, dict] = {}
TEXTS: dict[str, str] = {}
RESULTS: list[tuple[str, str, float, str]] = []


def case(name: str, kind: str, function) -> None:
    started = time.perf_counter()
    detail = function()
    elapsed = time.perf_counter() - started
    if elapsed > 10.0:
        raise AssertionError(f"{name}: elapsed {elapsed:.6f}s exceeds 10s")
    RESULTS.append((name, kind, elapsed, str(detail)))
    print(f"PASS {len(RESULTS):02d} {kind} {name} {elapsed:.6f}s {detail}")


def contract(experiment_id: str) -> dict:
    return DOCS[experiment_id]["protocol_amendment"]


def load_all_strictly() -> str:
    for experiment_id in EXPERIMENT_IDS:
        path = CORRECTIONS / f"{experiment_id}.yaml"
        text = path.read_text(encoding="utf-8")
        TEXTS[experiment_id] = text
        DOCS[experiment_id] = yaml.load(text, Loader=UniqueKeyLoader)
        assert list(DOCS[experiment_id]) == ["protocol_amendment"]
    return "five unique-key YAML documents parsed"


def check_prospective_flags() -> str:
    for experiment_id in EXPERIMENT_IDS:
        p = contract(experiment_id)
        assert p["experiment_id"] == experiment_id
        assert p["approved_by"] is None
        assert p["execution_authorized"] is False
        assert p["evidence_eligible"] is False
        assert p["scientific_runs"] == 0
    return "all five remain prospective, unapproved, unauthorized, zero-run"


def check_184_counts() -> str:
    p = contract("EXP-ECDLP-184fc4")["effective_contract"]
    assert 525 + 14 + 9 + 16 + 3 == 567 == p["frozen_library"]["member_count"]
    c = p["exact_cell_accounting"]
    assert 7 * 2 * 3 == c["primary_curve_bundles"] == 42
    assert 42 * 567 == c["observed_member_spectra"] == 23814
    assert 23814 * 64 == c["permutation_null_spectra"] == 1524096
    return "567 members, 42 bundles, 23814 observed and 1524096 null spectra"


def check_184_finite_null_rules() -> str:
    xs = list(range(64))
    median = (xs[31] + xs[32]) / 2
    lo = xs[math.ceil(0.025 * 64) - 1]
    hi = xs[math.ceil(0.975 * 64) - 1]
    assert (median, lo, hi) == (31.5, 1, 62)
    tied = [7] * 64
    assert ((tied[31] + tied[32]) / 2, tied[1], tied[62]) == (7, 7, 7)
    p_upper = (1 + sum(x >= 7 for x in tied)) / 65
    p_lower = (1 + sum(x <= 7 for x in tied)) / 65
    assert p_upper == p_lower == 1
    median_zero = 0
    ratio = None if median_zero <= 0 else 9 / median_zero
    assert ratio is None
    return "one-based endpoints x2/x63, ties, and nonpositive-median ratio branch hold"


def find_184_bootstrap_gap() -> str:
    interval = contract("EXP-ECDLP-184fc4")["effective_contract"]["slope_definitions"]["interval"]
    assert '"EXP-ECDLP-184fc4|slope-bootstrap|member"' in interval
    key_literal = "EXP-ECDLP-184fc4|slope-bootstrap|member"
    assert "stratum" not in key_literal
    assert "slope_kind" not in key_literal
    assert "counter=" not in interval and "sharing" not in interval
    return "expected_finding: key omits stratum/statistic dimensions and has no draw/sharing map"


def check_0c_counts_and_quantiles() -> str:
    c = contract("EXP-ECDLP-0c717c")["effective_contract"]["exact_cell_accounting"]
    assert 4 * 2 * 3 == c["primary_curve_bundles"] == 24
    assert 24 * 4 == c["primary_base_cells"] == 96
    assert 18 * 2 * 32 + 6 * 2 * 8 == c["underlying_null_permutations"] == 1248
    assert c["null_base_evaluations"] == 2496
    assert c["null_envelope_values"] == 4992
    assert (math.ceil(.025 * 32), math.ceil(.975 * 32)) == (1, 32)
    assert (math.ceil(.025 * 8), math.ceil(.975 * 8)) == (1, 8)
    return "24 bundles, 96 cells, 1248 permutations; R=32/R=8 endpoints hold"


def check_0c_bootstrap_keys() -> str:
    keys = []
    for gamma in ("1/3", "1/2"):
        for family in ("interval", "residue_zero"):
            for envelope in ("additive", "quadratic"):
                for stratum in ("A", "B"):
                    outputs = "log_p" if family == "interval" else "log_p,log_m_residue"
                    keys.append(
                        "EXP-ECDLP-0c717c|slope-bootstrap-v2|"
                        f"gamma={gamma}|base_family={family}|envelope={envelope}|"
                        f"stratum={stratum}|replicate_pool=20260905,20260906,20260907|"
                        f"shared_outputs={outputs}"
                    )
    assert len(keys) == len(set(keys)) == 16
    text = contract("EXP-ECDLP-0c717c")["effective_contract"]["slope_definition"]["bootstrap_rng_schedule"]
    assert "Distinct gamma, base_family, envelope or stratum keys never share a schedule" in text["sharing"]
    assert "log_p and log_m_residue slopes" in text["sharing"]
    return "16 dimension-separated keys; only named residue outputs share triples"


def digits(p: int, s: int, value: int) -> tuple[int, ...]:
    return tuple((value // (p**j)) % p for j in range(s))


def check_1e_digits_and_teichmuller() -> str:
    assert digits(5, 3, 32) == (2, 1, 1)
    assert (32 - 2) % 25 != 0
    t2 = pow(2, 5, 25)
    t3 = pow(2, 25, 125)
    assert (t2, t3) == (7, 57)
    assert t3 % 25 == t2 and pow(t3, 5, 125) == t3
    assert digits(5, 3, t3)[:2] == digits(5, 2, t2)
    return "p=5,C=32 reconstruction and precision-2/3 Teichmuller identities hold"


def check_1e_sc4_schedule() -> str:
    no_eligible = []
    one_eligible = [(0 + j * 0) % 1 for j in range(10)]
    six_eligible = [(2 + j * 5) % 6 for j in range(12)]
    assert no_eligible == []
    assert one_eligible == [0] * 10
    assert six_eligible[:6] == [2, 1, 0, 5, 4, 3]
    assert len(set(six_eligible[:6])) == 6 and six_eligible[6:] == six_eligible[:6]
    return "m=0 refusal, m=1 retention, and coprime full-cycle duplicate rule hold"


def find_1e_pair_schedule_gap() -> str:
    p = contract("EXP-ECDLP-1e6502")["effective_contract"]
    sc1 = next(x for x in p["five_blocking_self_checks"] if x["id"] == "SC1_torsion_homomorphism")["exact_test"]
    anomalous = p["anomalous_sigma_algorithm"]["functional"]
    assert "10,000 SHA256-selected ordered pairs" in sc1
    assert "10,000 deterministic pairs" in anomalous
    missing_tokens = ("pair-index", "pair_offset", "pair-step", "|pair|", "duplicate policy")
    assert not any(token in sc1 for token in missing_tokens)
    assert not any(token in anomalous for token in missing_tokens)
    return "expected_finding: SC1/SC2 and anomalous pair selections lack domains/index schedules"


def check_2c_counts_and_streaming() -> str:
    p = contract("EXP-ECDLP-2c3d20")
    c = p["exact_cell_accounting"]
    expected = {
        "primary_curve_bundles": 42,
        "primary_true_maps": 168,
        "primary_null_maps": 10752,
        "true_lumped_matrices": 6720,
        "null_lumped_matrices": 430080,
        "lumped_slope_trajectories_true": 960,
        "lumped_slope_trajectories_null": 61440,
    }
    assert all(type(c[k]) is int and c[k] == v for k, v in expected.items())
    stream = p["stage_accounting_and_memory_conformance"]["streaming_order_and_lifetimes"]
    assert "260 full label arrays" in stream and "may never be resident together" in stream
    return "all seven map/matrix counts are typed integers and the 260-map lifetime is forbidden"


def check_2c_total_matching() -> str:
    true_size = 100
    null_sizes = (10, 190)
    candidates = [n for n in null_sizes if 0.8 <= n / true_size <= 1.2]
    assert candidates == []
    p = contract("EXP-ECDLP-2c3d20")["itinerary_statistics"]
    assert "no_size_match" in p["deterministic_size_matching"]
    assert "incomplete_64_match_coverage" in p["deterministic_size_matching"]
    assert "zero_dispersion_equal" in p["class_spectrum"]
    assert "No IEEE infinity is serialized" in p["class_spectrum"]
    return "missing-match and zero-dispersion branches are explicit and non-JSON infinity is barred"


def find_2c_direction_gap() -> str:
    p = contract("EXP-ECDLP-2c3d20")["null_inference_and_decisions"]
    assert "predeclared upper direction" in p["ranks"]
    assert "predeclared lower direction" in p["ranks"]
    assert set(p) == {"ranks", "multiplicity", "review_candidate", "no_separation"}
    whole = TEXTS["EXP-ECDLP-2c3d20"]
    assert "direction_by_metric" not in whole and "metric_directions:" not in whole
    return "expected_finding: no metric/statistic key is assigned to its required one-sided tail"


def check_2c_order_2q_certificate() -> str:
    q = 11
    divisors = (1, 2, q, 2 * q)
    admissible = [d for d in divisors if (2 * q) % d == 0 and q % d != 0 and 2 % d != 0]
    assert admissible == [2 * q]
    generation = contract("EXP-ECDLP-2c3d20")["order_2q_known_true_control"]["generation"]
    for token in ("a=0,...,19999", "v=0,...,4095", "[2q]P=O", "[q]P!=O", "[2]P!=O", "control_curve_exhausted"):
        assert token in generation
    return "fixed divisor attack leaves only order 2q; both sampler caps and exhaustion are frozen"


def check_709_capacities_and_rows() -> str:
    p = contract("EXP-ECDLP-709063")
    caps = p["portable_fixed_physical_table"]["exact_capacities"]
    expected = [(8, 0, 0), (4096, 256, 179), (32768, 2048, 1433), (262144, 16384, 11468)]
    assert [(x["budget_bytes"], x["slots"], x["usable_entries"]) for x in caps] == expected
    c = p["exact_cell_accounting"]
    assert all(type(c[k]) is int for k in (
        "total_unbounded_bsgs_rows", "total_rho_trial_rows", "total_arm_a_rows",
        "total_arm_b_rows", "total_representation_control_records", "total_algorithm_rows"
    ))
    assert 16 + 256 + 48 + 48 == c["total_algorithm_rows"] == 368
    assert c["total_representation_control_records"] == 8
    return "physical capacities, 368 algorithm rows, and 8 representation controls hold"


def scalar_cost_left_to_right(k: int) -> int:
    return k.bit_length() - 1 + k.bit_count() - 1


def check_709_limits_and_bsgs_formula() -> str:
    n, e, k = 101, 7, 37
    i_max = max(2000, 200 * math.isqrt(n) + 200)
    assert i_max == 2200
    ell = k // e
    full = (e - 1) + scalar_cost_left_to_right(e) + ell + scalar_cost_left_to_right(k)
    assert (ell, full) == (5, 22)
    q, r = divmod(n, e)
    g_num = e * q * (q - 1) // 2 + q * r
    assert g_num == sum(x // e for x in range(2, n))
    source = (ROOT / "harness/rho.py").read_text(encoding="utf-8")
    assert "max(2000, 200 * int(n ** 0.5) + 200)" in source
    assert "for offset in range(0, 12)" in source
    return "rho cap matches pinned default at toy N; actual and expected BSGS formulas recompute"


def find_709_encoding_and_scalar_conflicts() -> str:
    p = contract("EXP-ECDLP-709063")
    slot = p["portable_fixed_physical_table"]["slot_layout"]
    typed = p["stage_accounting_and_memory_conformance"]["typed_encodings"]
    assert "<IIII" in slot and "state=2 is O" in slot
    assert "<BII" in typed["point"] and "O is (0,0,0)" in typed["point"]
    assert struct.calcsize("<IIII") == 16
    assert struct.calcsize("<BII") + struct.calcsize("<I") == 13
    k = 13
    source_right_to_left_calls = k.bit_length() + k.bit_count()
    declared_left_to_right_calls = scalar_cost_left_to_right(k)
    assert (source_right_to_left_calls, declared_left_to_right_calls) == (7, 5)
    source = (ROOT / "harness/rho.py").read_text(encoding="utf-8")
    assert "addend = E.add(addend, addend)" in source
    assert "and its own SHA-256" in p["shared_instance_set"]["canonical_instance"]
    return "expected_finding: 16/13-byte O-state conflict, rho scalar-call delta 2, and manifest self-hash"


def main() -> None:
    case("strict_unique_key_parse", "static", load_all_strictly)
    case("prospective_authority_flags", "static", check_prospective_flags)
    case("184_exact_counts", "arithmetic", check_184_counts)
    case("184_finite_null_rules", "mock", check_184_finite_null_rules)
    case("184_bootstrap_domain_gap", "expected_finding", find_184_bootstrap_gap)
    case("0c_counts_and_quantiles", "arithmetic", check_0c_counts_and_quantiles)
    case("0c_bootstrap_key_separation", "static", check_0c_bootstrap_keys)
    case("1e_digits_and_teichmuller", "arithmetic", check_1e_digits_and_teichmuller)
    case("1e_sc4_exhaustion_and_cycle", "mock", check_1e_sc4_schedule)
    case("1e_pair_schedule_gap", "expected_finding", find_1e_pair_schedule_gap)
    case("2c_counts_and_memory_lifetime", "static", check_2c_counts_and_streaming)
    case("2c_total_class_matching", "mock", check_2c_total_matching)
    case("2c_tail_direction_gap", "expected_finding", find_2c_direction_gap)
    case("2c_full_order_control", "arithmetic", check_2c_order_2q_certificate)
    case("709_capacities_and_rows", "arithmetic", check_709_capacities_and_rows)
    case("709_rho_limit_and_bsgs_formula", "arithmetic", check_709_limits_and_bsgs_formula)
    case("709_encoding_scalar_selfhash_conflicts", "expected_finding", find_709_encoding_and_scalar_conflicts)
    total = sum(x[2] for x in RESULTS)
    assert len(RESULTS) == 17
    print(f"SUMMARY fixed_cases=17 failures=0 scientific_runs=0 reruns=0 total_case_seconds={total:.6f}")


if __name__ == "__main__":
    main()
