"""Independent fixed software review; no scientific execution or solver calls.

The only enumeration below belongs to the fixed n<=5 generic fixtures and
the exact p5,s2 four-arm fixture (n<=7). The n256 case uses identities only.
"""
import argparse
import builtins
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import traceback
import types


TASK = "TASK-20261030-8e7037"
ROOT = Path(__file__).resolve().parents[3]
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()
FROZEN = {
    "research/prime_sat_followup_20261029/encoding.py":
        "2b18f50238db633eb91ac33a36660c52620e81c5f6fa1c9c78d40c261e99041f",
    "research/prime_sat_five_tests_20261029/core.py":
        "c67fc44404b282ac963f1021a4b6197ebbb4a8bf382c70a2576db45172065a4f",
    "research/prime_sat_costbridge_controls_20261029/prefix_cover.py":
        "10ef5f615218649660eaf62212e9dcb58045f08ebb414663a4c14ed63c090c2c",
    "research/prime_sat_prefix_adapter_20261030/adapter.py":
        "cbc038001273d0a351b86f94d3ac0708eb698e51ab3d8bbef39d7798c4e8fc65",
}
JOINTS = [
    "canonical_schema", "prefix_identity", "model_fiber_scope", "exact_domain",
    "coverage_and_censoring", "legacy_integration", "actual_execution_custody",
]
RECORDS, GUARD_CALLS, ORACLES, LEGACY = [], [], {}, {}
ACTIVE = None


def utc():
    return datetime.now(timezone.utc).isoformat()


def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in [*FROZEN, SELF]}


def need(label, condition, detail=None):
    entry = {"assertion": label, "outcome": "holds" if condition else "breaks"}
    if detail is not None:
        entry["detail"] = detail
    ACTIVE["assertions"].append(entry)
    if not condition:
        raise AssertionError(label + (": " + repr(detail) if detail is not None else ""))


def case(name, joint, operation):
    global ACTIVE
    ACTIVE = {"id": name, "joint": joint, "assertions": []}
    try:
        detail = operation()
        if detail is not None:
            ACTIVE["detail"] = detail
        ACTIVE["outcome"] = "holds"
    except BaseException as error:
        ACTIVE.update(outcome="breaks", exception_type=type(error).__name__,
                      exception=str(error), traceback=traceback.format_exc())
    RECORDS.append(ACTIVE)
    print(ACTIVE["outcome"].upper() + " " + name)


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def forbid(name):
    def fail(*args, **kwargs):
        GUARD_CALLS.append({"entry_point": name, "at": utc()})
        raise RuntimeError("FORBIDDEN_ENTRY_POINT:" + name)
    return fail


def guarded_range(*args):
    values = builtins.range(*args)
    if len(values) > 128:
        GUARD_CALLS.append({"entry_point": "operational_oversized_range",
                            "arguments": list(args), "at": utc()})
        raise RuntimeError("Operational range exceeds exact tiny fixture limit")
    return values


def setup():
    # Install a raising solver facade before legacy import: no solver object
    # can be constructed, and no solver implementation is imported.
    package = types.ModuleType("pysat")
    package.__path__ = []
    solvers = types.ModuleType("pysat.solvers")
    solvers.Minisat22 = forbid("pysat.solvers.Minisat22")
    package.solvers = solvers
    sys.modules["pysat"], sys.modules["pysat.solvers"] = package, solvers
    core = load("core", "research/prime_sat_five_tests_20261029/core.py")
    core.refute = forbid("core.refute")
    adapter = load("independent_target_adapter",
                   "research/prime_sat_prefix_adapter_20261030/adapter.py")
    legacy = adapter._legacy()
    for name in ("solve", "controls", "run", "verify", "census", "reference",
                 "refute", "Minisat22"):
        setattr(legacy, name, forbid("encoding." + name))
    cover = adapter._load("research/prime_sat_costbridge_controls_20261029/prefix_cover.py")
    adapter.range, cover.range, legacy.range = guarded_range, guarded_range, guarded_range
    return adapter, legacy


def variables(mask):
    """Independent set-of-variable monomial representation, valid inputs only."""
    mask = int(mask)
    result, bit = set(), 0
    while mask:
        if mask % 2:
            result.add(bit)
        bit += 1
        mask //= 2
    return frozenset(result)


def unpack(poly, p):
    return {variables(mask): value % p for mask, value in poly.items()}


def eval_poly(poly, bits, p):
    # Product evaluation, separately authored rather than target bit-mask test.
    value = 0
    for mask, coefficient in poly.items():
        product = 1
        for index in variables(mask):
            product *= (bits // (2 ** index)) % 2
        value += coefficient * product
    return value % p


def restrict_poly(poly, depth, prefix, p):
    out = Counter()
    for support, coefficient in unpack(poly, p).items():
        constant, remaining = 1, set()
        for index in support:
            if index < depth:
                constant *= (prefix // (2 ** index)) % 2
            else:
                remaining.add(index)
        out[frozenset(remaining)] += coefficient * constant
    return {support: value % p for support, value in out.items() if value % p}


def identity(poly_list, item, p):
    total = Counter()
    for poly, multiplier in zip(poly_list, item["certificate"]):
        residual = restrict_poly(poly, item["depth"], item["prefix"], p)
        for left, coefficient in residual.items():
            for right, factor in unpack(multiplier, p).items():
                total[left.union(right)] += coefficient * factor
    return {support: value % p for support, value in total.items() if value % p} == {
        frozenset(): 1}


def clause_satisfied(clause, bits):
    return any(((bits // (2 ** (abs(literal) - 1))) % 2 == 1)
               == (literal > 0) for literal in clause)


def block_leaf(value, depth):
    return [index + 1 if (value // (2 ** index)) % 2 == 0 else -(index + 1)
            for index in range(depth)]


def tiny_oracle(spec):
    n, m, p = spec["n"], spec["projected_bits"], spec["p"]
    if n > 5:
        raise AssertionError("generic tiny oracle forbidden above n5")
    answer = spec["answer"]
    domain = [bits for bits in range(2 ** n)
              if all(clause_satisfied(clause, bits) for clause in spec["domain_cnf"])]
    bound = spec["aux_bound"]
    declared_domain = [bits for bits in range(2 ** n)
                       if bound is None or bits // (2 ** m) < bound]
    need("independent_CNF_equals_numeric_domain", domain == declared_domain)
    roots = [bits for bits in domain
             if all(eval_poly(poly, bits, p) == 0 for poly in spec["polynomials"])]
    projected = sorted({bits % (2 ** m) for bits in roots})
    returned = sorted({bits % (2 ** m) for bits in answer["models"]})
    gaps = []
    for bits in domain:
        excluded = any(bits % (2 ** item["depth"]) == item["prefix"]
                       for item in answer["learned"])
        model_cylinder = bits % (2 ** m) in returned
        if not excluded and not model_cylinder:
            gaps.append(bits)
    for index, item in enumerate(answer["learned"]):
        need("independent_identity_" + str(index), identity(spec["polynomials"], item, p))
    return {"domain": domain, "full_roots": roots, "projected_roots": projected,
            "returned_projections": returned, "uncovered_assignments": gaps}


def generic_specs():
    prefix = {"depth": 1, "prefix": 1, "clause": [-1], "certificate": [{"0": 1}]}
    base = {"p": 5, "n": 2, "projected_bits": 2, "polynomials": [{"1": 1}],
            "domain_cnf": [], "aux_bound": None,
            "answer": {"status": "complete", "models": [0, 2], "learned": [prefix]}}
    specs = {"complete_projected_roots": deepcopy(base)}
    specs["censored_gap"] = deepcopy(base)
    specs["censored_gap"]["answer"].update(status="censored", models=[0])
    specs["censored_but_covered"] = deepcopy(base)
    specs["censored_but_covered"]["answer"]["status"] = "censored"
    specs["global_refutation_nonconstant_multipliers"] = {
        "p": 5, "n": 2, "projected_bits": 2,
        "polynomials": [{"1": 1}, {"1": 1, "0": 4}], "domain_cnf": [], "aux_bound": None,
        "answer": {"status": "complete", "models": [], "learned": [
            {"depth": 0, "prefix": 0, "clause": [], "certificate": [
                {"3": 1, "2": 4, "0": 1}, {"3": 4, "0": 4}]}]}}
    specs["auxiliary_fiber_projection_only"] = deepcopy(base)
    specs["auxiliary_fiber_projection_only"].update(n=3, aux_bound=2)
    specs["canonical_aux_upper_bound"] = deepcopy(base)
    specs["canonical_aux_upper_bound"].update(
        n=5, aux_bound=5, domain_cnf=[[-3, 4, -5], [3, -4, -5], [-3, -4, -5]])
    specs["empty_auxiliary_domain"] = deepcopy(base)
    specs["empty_auxiliary_domain"].update(
        projected_bits=1, aux_bound=0, domain_cnf=[[2], [-2]],
        answer={"status": "complete", "models": [], "learned": []})
    specs["large_root_refutation"] = {
        "p": 5, "n": 256, "projected_bits": 2, "polynomials": [{"0": 1}],
        "domain_cnf": [], "aux_bound": None,
        "answer": {"status": "complete", "models": [], "learned": [
            {"depth": 0, "prefix": 0, "clause": [], "certificate": [{"0": 1}]}]}}
    return specs


def accepted(adapter, name, spec):
    oracle = None if spec["n"] == 256 else tiny_oracle(spec)
    if oracle is not None:
        ORACLES[name] = oracle
    else:
        need("n256_independent_constant_identity", identity(
            spec["polynomials"], spec["answer"]["learned"][0], spec["p"]))
    report = adapter.verify_transcript(**deepcopy(spec))
    answer = spec["answer"]
    returned = sorted({value % (2 ** spec["projected_bits"]) for value in answer["models"]})
    need("valid", report["valid"] is True)
    need("returned_projected_models", report["projected_models"] == returned)
    need("declared_status_preserved", report["declared_status"] == answer["status"])
    need("primality_not_certified", report["prime_field_verified"] is False)
    need("proof_scope", "Boolean quotient identities modulo p" in report["proof_scope"])
    need("no_full_root_completeness_field", "full_models_complete" not in report)
    covered = True if oracle is None else not oracle["uncovered_assignments"]
    need("independent_coverage_agrees", report["cover_complete"] is covered)
    need("projected_completeness_status_conjunction",
         report["projected_model_set_complete"] is (covered and answer["status"] == "complete"))
    if covered:
        need("no_gap_when_covered", report["uncovered"] is None)
        if oracle is not None:
            need("actual_projected_roots_agree", oracle["projected_roots"] == returned)
    else:
        need("gap_is_noncovered_domain_assignment",
             report["uncovered"] in oracle["uncovered_assignments"])
        need("fixed_gap_2", report["uncovered"] == 2)
    if name == "auxiliary_fiber_projection_only":
        need("four_full_roots_two_projections", oracle["full_roots"] == [0, 2, 4, 6]
             and returned == [0, 2] and len(answer["models"]) == 2)
    costs = report["costs"]
    need("six_separate_cost_phases", set(costs) == {
        "parsing", "domain_validation", "restriction", "identity_check",
        "model_evaluation", "coverage"})
    term_visits = len(answer["learned"]) * sum(len(poly) for poly in spec["polynomials"])
    need("restriction_visits_counted", costs["restriction"].get("term_visits", 0) == term_visits)
    need("model_visits_counted", costs["model_evaluation"].get("term_visits", 0)
         == len(answer["models"]) * sum(len(poly) for poly in spec["polynomials"]))
    pair_products = sum(
        len(restrict_poly(poly, item["depth"], item["prefix"], spec["p"])) * len(q)
        for item in answer["learned"]
        for poly, q in zip(spec["polynomials"], item["certificate"]))
    need("all_identity_term_pairs_counted",
         costs["identity_check"].get("coefficient_multiplications", 0) == pair_products
         and costs["identity_check"].get("coefficient_additions", 0) == pair_products)
    need("domain_clause_visits_counted", costs["domain_validation"].get("clauses", 0)
         == len(spec["domain_cnf"]))
    need("domain_literal_visits_counted", costs["domain_validation"].get("literals", 0)
         == sum(map(len, spec["domain_cnf"])))
    supplied = len(answer["learned"]) + len(answer["models"])
    depths = sum(item["depth"] for item in answer["learned"]) + len(answer["models"]) * spec["projected_bits"]
    need("prefix_count", costs["coverage"]["prefixes"] == supplied)
    need("prefix_depth_sum", costs["coverage"]["prefix_depth_sum"] == depths)
    need("trie_allocation_bound", costs["coverage"]["trie_nodes"] <= 1 + depths)
    expected_entries = sum(map(len, spec["polynomials"])) + sum(
        len(q) for item in answer["learned"] for q in item["certificate"])
    need("all_polynomial_and_multiplier_entries_parsed",
         costs["parsing"].get("polynomial_entries", 0) == expected_entries)
    need("learned_entry_parsing_count", costs["parsing"].get("learned_entries", 0)
         == len(answer["learned"]))
    need("model_parsing_count", costs["parsing"].get("models", 0) == len(answer["models"]))
    if name == "large_root_refutation":
        need("n256_constant_work_recorded", costs["coverage"] == {
            "prefixes": 1, "prefix_depth_sum": 0, "trie_nodes": 1}
             and pair_products == 1 and term_visits == 1)
    return {"input": spec, "report": report, "oracle": oracle}


def set_path(spec, path, value, delete=False):
    target = spec
    for component in path[:-1]:
        target = target[component]
    if delete:
        del target[path[-1]]
    else:
        target[path[-1]] = value


def rejected(adapter, spec):
    try:
        unexpected = adapter.verify_transcript(**spec)
    except ValueError as error:
        need("raises_ValueError", True)
        # repr preserves int/string aliases and tuple/list distinctions;
        # raw JSON mapping keys cannot faithfully retain those invalid inputs.
        return {"input_repr": repr(spec), "rejection": str(error)}
    need("raises_ValueError", False, unexpected)


def negative_cases(adapter, specs):
    base = specs["complete_projected_roots"]
    def mutation(name, joint, path, value=None, fixture=None, delete=False):
        sample = deepcopy(specs[fixture] if fixture else base)
        set_path(sample, path, value, delete)
        case(name, joint, lambda: rejected(adapter, sample))

    typed = [
        ("p", ["p"], 5), ("n", ["n"], 2),
        ("projected_bits", ["projected_bits"], 2),
        ("depth", ["answer", "learned", 0, "depth"], 1),
        ("prefix", ["answer", "learned", 0, "prefix"], 1),
        ("model", ["answer", "models", 0], 0),
        ("coefficient", ["polynomials", 0, "1"], 1),
        ("multiplier_coefficient", ["answer", "learned", 0, "certificate", 0, "0"], 1),
        ("clause_literal", ["answer", "learned", 0, "clause", 0], -1),
    ]
    for label, path, value in typed:
        mutation("schema_bool_" + label, "canonical_schema", path, bool(value))
        mutation("schema_float_" + label, "canonical_schema", path, float(value))
    for value in (-1, 0, 1):
        mutation("modulus_below_two_" + str(value), "canonical_schema", ["p"], value)
    mutation("negative_n", "canonical_schema", ["n"], -1)
    for value in (-1, 3):
        mutation("projected_bits_bounds_" + str(value), "canonical_schema",
                 ["projected_bits"], value)
    for index, mask in enumerate((-1, 4, True, 1.0, "01", "+1", "-1", "1.0", "")):
        mutation("noncanonical_mask_" + str(index), "canonical_schema",
                 ["polynomials"], [{mask: 1}])
    mutation("int_string_alias_same_mask", "canonical_schema",
             ["polynomials"], [{1: 1, "1": 1}])
    for index, value in enumerate((0, -1, 5, 6)):
        mutation("noncanonical_coefficient_" + str(index), "canonical_schema",
                 ["polynomials", 0, "1"], value)
    for label, path, value in [
        ("polynomials_container", ["polynomials"], {}),
        ("polynomial_None", ["polynomials"], [None]),
        ("polynomial_list", ["polynomials"], [[]]),
        ("multiplier_None", ["answer", "learned", 0, "certificate", 0], None),
        ("multiplier_list", ["answer", "learned", 0, "certificate", 0], []),
        ("no_multipliers", ["answer", "learned", 0, "certificate"], []),
        ("too_many_multipliers", ["answer", "learned", 0, "certificate"], [{0: 1}, {}]),
        ("certificate_None", ["answer", "learned", 0, "certificate"], None),
        ("models_tuple", ["answer", "models"], (0, 2)),
        ("models_None", ["answer", "models"], None),
        ("learned_mapping", ["answer", "learned"], {}),
        ("learned_None", ["answer", "learned"], None),
        ("answer_None", ["answer"], None),
        ("learned_entry_list", ["answer", "learned", 0], []),
    ]:
        mutation(label, "canonical_schema", path, value)
    for key in ("status", "models", "learned"):
        mutation("missing_answer_" + key, "canonical_schema", ["answer", key], delete=True)
    for key in ("depth", "prefix", "clause", "certificate"):
        mutation("missing_learned_" + key, "canonical_schema",
                 ["answer", "learned", 0, key], delete=True)
    for index, value in enumerate(("finished", "", None, True)):
        mutation("unknown_status_" + str(index), "canonical_schema",
                 ["answer", "status"], value)
    closing = "global_refutation_nonconstant_multipliers"
    for label, malformed in [
        ("missing_certificate", {"depth": 0, "prefix": 0, "clause": []}),
        ("None_entry", None),
        ("bad_multiplier", {"depth": 0, "prefix": 0, "clause": [], "certificate": [None, {}]}),
    ]:
        learned = deepcopy(specs[closing]["answer"]["learned"]) + [malformed]
        mutation("post_closure_" + label, "canonical_schema",
                 ["answer", "learned"], learned, fixture=closing)
    mutation("post_closure_invalid_model", "model_fiber_scope",
             ["answer", "models"], [0], fixture=closing)
    mutation("wrong_identity_coefficient", "prefix_identity",
             ["answer", "learned", 0, "certificate", 0, "0"], 2)
    mutation("omit_required_multiplier_component", "prefix_identity",
             ["answer", "learned", 0, "certificate"], [{"3": 1, "2": 4, "0": 1}],
             fixture=closing)
    mutation("wrong_restriction_prefix_with_correct_clause", "prefix_identity",
             ["answer", "learned", 0],
             {"depth": 1, "prefix": 0, "clause": [1], "certificate": [{"0": 1}]})
    for label, key, value in [
        ("negative_depth", "depth", -1), ("depth_out_of_range", "depth", 3),
        ("negative_prefix", "prefix", -1), ("prefix_out_of_range", "prefix", 2),
    ]:
        mutation(label, "prefix_identity", ["answer", "learned", 0, key], value)
    for label, clause in [
        ("sign", [1]), ("empty_length", []), ("extra_length", [-1, 2]),
        ("zero_literal", [0]), ("negative_out_of_range", [-3]),
        ("positive_out_of_range", [3]), ("duplicate_literal", [-1, -1]),
        ("bool_literal", [False]), ("float_literal", [-1.0]),
    ]:
        mutation("prefix_clause_" + label, "prefix_identity",
                 ["answer", "learned", 0, "clause"], clause)
    sample = deepcopy(base)
    sample["answer"]["status"] = "censored"
    sample["answer"]["learned"][0].update(depth=2, prefix=1, clause=[2, -1])
    case("prefix_clause_wrong_order", "prefix_identity", lambda: rejected(adapter, sample))
    for label, models in [
        ("not_root", [1]), ("negative", [-1]), ("out_of_range", [4]),
        ("duplicate_same_assignment", [0, 0, 2]),
    ]:
        mutation("model_" + label, "model_fiber_scope", ["answer", "models"], models)
    mutation("duplicate_projection_distinct_full_witnesses", "model_fiber_scope",
             ["answer", "models"], [0, 4, 2], fixture="auxiliary_fiber_projection_only")
    mutation("model_aux5_outside_bound5", "model_fiber_scope",
             ["answer", "models"], [20, 2], fixture="canonical_aux_upper_bound")
    mutation("false_complete_missing_model2", "coverage_and_censoring",
             ["answer", "models"], [0])
    mutation("nonempty_domain_without_bound", "exact_domain", ["domain_cnf"], [[1]])
    bound_fixture = "canonical_aux_upper_bound"
    valid_domain = specs[bound_fixture]["domain_cnf"]
    domains = [
        ("projected_variable", [[1, 4, -5], *valid_domain[1:]]),
        ("partial_auxiliary_clause", [[-3, 4], *valid_domain[1:]]),
        ("wrong_literal_order", [[4, -3, -5], *valid_domain[1:]]),
        ("duplicate_variable", [[-3, 3, -5], *valid_domain[1:]]),
        ("missing_exclusion", valid_domain[:2]),
        ("duplicate_exclusion", [valid_domain[0], valid_domain[0], valid_domain[2]]),
        ("below_bound_same_count", [[3, 4, -5], *valid_domain[1:]]),
        ("bool_literal", [[True, 4, -5], *valid_domain[1:]]),
        ("float_literal", [[-3.0, 4, -5], *valid_domain[1:]]),
        ("clause_tuple", [tuple(valid_domain[0]), *valid_domain[1:]]),
        ("domain_tuple", tuple(valid_domain)),
    ]
    for label, domain in domains:
        mutation("domain_" + label, "exact_domain", ["domain_cnf"], domain, fixture=bound_fixture)
    for label, value in [("negative", -1), ("over_capacity", 9), ("bool", True), ("float", 5.0)]:
        mutation("bound_" + label, "exact_domain", ["aux_bound"], value, fixture=bound_fixture)
    mutation("empty_domain_malformed_certificate", "exact_domain",
             ["answer", "learned"], [{"depth": 0, "prefix": 0, "clause": [],
                                      "certificate": None}], fixture="empty_auxiliary_domain")
    mutation("empty_domain_invalid_model", "model_fiber_scope", ["answer", "models"],
             [0], fixture="empty_auxiliary_domain")


def point_sum(P, Q, p, a):
    # Separate, fixed-fixture group oracle. Does not call frozen affine_add.
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0:
        return None
    if P == Q:
        numerator, denominator = 3 * P[0] ** 2 + a, 2 * P[1]
    else:
        numerator, denominator = Q[1] - P[1], Q[0] - P[0]
    slope = numerator * pow(denominator, -1, p) % p
    x = (slope ** 2 - P[0] - Q[0]) % p
    y = (slope * (P[0] - x) - P[1]) % p
    return x, y


CELL = {"p": 5, "a": 1, "b": 1, "s": 2, "target": [0, 1]}
EXPECTED_PAIRS = [(2, 3), (3, 2), (3, 3)]
EXPECTED_PACKED = [11, 14, 15]


def independent_legacy_pairs():
    pairs, witnesses = [], {}
    for x in range(4):
        for z in range(4):
            lam = (x * z - 1) * 3 % 5
            P, Q = (x, (lam * x - 1) % 5), (z, (lam * z - 1) % 5)
            on_curve = all((Y ** 2 - X ** 3 - X - 1) % 5 == 0 for X, Y in (P, Q))
            if on_curve and point_sum(P, Q, 5, 1) == (0, 1):
                pairs.append((x, z))
                witnesses[(x, z)] = {"lambda": lam, "points": [P, Q]}
    need("separate_group_oracle_fixed_expected_pairs", pairs == EXPECTED_PAIRS)
    need("known_positive_witness", witnesses[(2, 3)] == {
        "lambda": 0, "points": [(2, 4), (3, 4)]})
    return pairs, witnesses


def leaf_transcript(legacy, arm):
    ring, polys, domain = legacy.build(deepcopy(CELL), arm)
    need("legacy_boolean_width_bound", ring.n <= 7)
    full_roots, canonical, learned = [], {}, []
    for bits in range(2 ** ring.n):
        if not all(clause_satisfied(clause, bits) for clause in domain):
            continue
        values = [eval_poly(poly, bits, 5) for poly in polys]
        projection = bits % 16
        if not any(values):
            full_roots.append(bits)
            canonical.setdefault(projection, bits)
        else:
            index = next(index for index, value in enumerate(values) if value)
            multiplier = [{} for _ in polys]
            multiplier[index] = {0: pow(values[index], -1, 5)}
            item = {"depth": ring.n, "prefix": bits,
                    "clause": block_leaf(bits, ring.n), "certificate": multiplier,
                    "rank": "untrusted-legacy-telemetry", "attempted_rows": -999}
            need("hand_leaf_identity_" + str(bits), identity(polys, item, 5))
            learned.append(item)
    need("fixed_legacy_projected_roots", sorted(canonical) == EXPECTED_PACKED)
    need("canonical_known_full_model14", canonical[14] == 14)
    need("invalid_leaf0_present", any(item["prefix"] == 0 for item in learned))
    return ring, polys, domain, {
        "status": "complete", "models": [canonical[key] for key in sorted(canonical)],
        "learned": learned, "costs": {"unauthenticated": "ignored"},
        "certificate_bytes": -12345}, full_roots


def legacy_accepted(adapter, legacy, arm, status):
    pairs, expected_witnesses = independent_legacy_pairs()
    ring, polys, domain, answer, full_roots = leaf_transcript(legacy, arm)
    answer["status"] = status
    direct_costs = legacy.verify_search(CELL, ring, polys, domain, deepcopy(answer), pairs)
    report = adapter.verify_encoding_search(deepcopy(CELL), arm, deepcopy(answer))
    need("old_direct_verifier_returned", isinstance(direct_costs, dict))
    need("wrapper_valid", report["valid"] is True)
    need("wrapper_projection_matches_independent_set", report["projected_models"] == EXPECTED_PACKED)
    need("wrapper_coordinate_pairs", report["coordinate_pairs"] == [list(pair) for pair in pairs])
    need("wrapper_status_preserved", report["declared_status"] == status)
    need("wrapper_covered", report["cover_complete"] is True and report["uncovered"] is None)
    need("wrapper_projected_completeness", report["projected_model_set_complete"] is (status == "complete"))
    need("wrapper_prime_external", report["prime_field_verified"] is False
         and "conditional on prime p" in report["proof_scope"])
    need("separate_construction_cost", isinstance(report["costs"]["construction"], dict))
    need("separate_reconstruction_cost", isinstance(
        report["costs"]["witness_reconstruction_and_check"], dict))
    need("reconstruct_each_projection", report["costs"]["witness_reconstruction_and_check"]["witnesses"] == 3)
    if arm == "membership":
        need("membership_truth_table_overhead_retained",
             report["costs"]["construction"]["membership_curve_tests"] == 32)
    observed = {}
    for witness in report["witnesses"]:
        pair = tuple(witness["x"])
        points = [tuple(point) for point in witness["points"]]
        need("witness_group_sum_" + str(pair), point_sum(*points, 5, 1) == (0, 1))
        need("witness_matches_independent_formula_" + str(pair),
             expected_witnesses[pair] == {"lambda": witness["lambda"], "points": points})
        observed[str(pair)] = witness
    need("all_three_witnesses_checked", len(observed) == 3)
    key = arm + "_" + status
    LEGACY[key] = {"transcript": answer, "full_roots_test_only": full_roots,
                   "direct_old_verifier_costs": direct_costs, "adapter_report": report}
    return LEGACY[key]


def legacy_rejected(adapter, legacy, arm, variant):
    ring, polys, domain, answer, full_roots = leaf_transcript(legacy, arm)
    if variant == "delete_model14":
        answer["models"].remove(14)
    elif variant == "delete_leaf0":
        answer["learned"] = [item for item in answer["learned"] if item["prefix"] != 0]
    elif variant == "corrupt_leaf0_multiplier":
        leaf = next(item for item in answer["learned"] if item["prefix"] == 0)
        component = next(q for q in leaf["certificate"] if q)
        need("fixed_leaf0_inverse_is_one", component == {0: 1})
        component[0] = 2
    elif variant == "invalid_model0":
        answer["models"].append(0)
    elif variant == "duplicate_projection":
        answer["models"].append(14)
    else:
        raise AssertionError("unknown fixed legacy variant")
    try:
        legacy.verify_search(CELL, ring, polys, domain, deepcopy(answer), EXPECTED_PAIRS)
    except AssertionError as error:
        old_error = str(error)
    else:
        need("direct_old_verifier_rejects_" + variant, False)
    need("direct_old_verifier_rejects_" + variant, True)
    try:
        adapter.verify_encoding_search(deepcopy(CELL), arm, deepcopy(answer))
    except ValueError as error:
        new_error = str(error)
    else:
        need("adapter_rejects_" + variant, False)
    need("adapter_rejects_" + variant, True)
    return {"transcript": answer, "direct_old_rejection": old_error,
            "adapter_rejection": new_error}


def run_suite():
    adapter, legacy = setup()
    specs = generic_specs()
    for name, spec in specs.items():
        joint = ("model_fiber_scope" if name == "auxiliary_fiber_projection_only" else
                 "exact_domain" if name in ("canonical_aux_upper_bound", "empty_auxiliary_domain") else
                 "prefix_identity" if name == "global_refutation_nonconstant_multipliers" else
                 "coverage_and_censoring")
        case(name, joint, lambda name=name, spec=spec: accepted(adapter, name, spec))
    negative_cases(adapter, specs)
    for arm in ("quartic", "membership", "quadratic", "quadratic_aa"):
        for status in ("complete", "censored"):
            case("legacy_" + arm + "_" + status, "legacy_integration",
                 lambda arm=arm, status=status: legacy_accepted(adapter, legacy, arm, status))
        for variant in ("delete_model14", "delete_leaf0", "corrupt_leaf0_multiplier",
                        "invalid_model0", "duplicate_projection"):
            case("legacy_" + arm + "_" + variant, "legacy_integration",
                 lambda arm=arm, variant=variant: legacy_rejected(adapter, legacy, arm, variant))
    case("forbidden_entry_points_never_called", "actual_execution_custody",
         lambda: need("zero_guard_sentinel_failures", not GUARD_CALLS, GUARD_CALLS))


class Tee:
    def __init__(self, original, captured):
        self.original, self.captured = original, captured

    def write(self, text):
        self.captured.write(text)
        return self.original.write(text)

    def flush(self):
        self.original.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    receipt = ROOT / args.receipt
    prior = json.loads(receipt.read_text()) if receipt.exists() else {"attempts": []}
    if len(prior["attempts"]) >= 4:
        raise RuntimeError("Fixed four-invocation budget already exhausted")
    before, started = hashes(), utc()
    source = (ROOT / SELF).read_text()
    out, err = io.StringIO(), io.StringIO()
    original_out, original_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = Tee(original_out, out), Tee(original_err, err)
    fatal = None
    try:
        def custody():
            need("cwd_matches_exact_authorization", Path.cwd() == ROOT)
            need("bytecode_disabled", sys.dont_write_bytecode is True)
            need("required_environment", os.environ.get("PYTHONDONTWRITEBYTECODE") == "1")
            for name, expected in FROZEN.items():
                need("frozen_hash_before_" + name, before[name] == expected)
        case("execution_preconditions", "actual_execution_custody", custody)
        if RECORDS[-1]["outcome"] != "holds":
            raise RuntimeError("Admission/source custody failed; target execution refused")
        run_suite()
    except BaseException as error:
        fatal = {"type": type(error).__name__, "message": str(error),
                 "traceback": traceback.format_exc()}
        traceback.print_exc()
    after = hashes()
    case("sources_unchanged_after_execution", "actual_execution_custody",
         lambda: need("all_source_hashes_unchanged", before == after))
    failures = [record["id"] for record in RECORDS if record["outcome"] != "holds"]
    returncode = 1 if failures or fatal else 0
    verdicts = {}
    for joint in JOINTS:
        joint_records = [record for record in RECORDS if record["joint"] == joint]
        verdicts[joint] = ("breaks" if any(record["outcome"] == "breaks" for record in joint_records)
                           else "holds" if joint_records and fatal is None else "inconclusive")
    print(json.dumps({"attempt": len(prior["attempts"]) + 1, "returncode": returncode,
                      "cases": len(RECORDS), "failures": failures, "verdicts": verdicts},
                     sort_keys=True))
    attempt = {
        "number": len(prior["attempts"]) + 1, "started_at": started, "finished_at": utc(),
        "argv": [sys.executable, "-B", *sys.argv], "cwd": str(Path.cwd()),
        "environment": {"PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE")},
        "python_version": sys.version, "python_executable": sys.executable,
        "source_hashes_before": before, "source_hashes_after": after,
        "harness_source_exact": source, "stdout": out.getvalue(), "stderr": err.getvalue(),
        "returncode": returncode, "fatal": fatal, "records": RECORDS,
        "oracle_results": ORACLES, "legacy_results": LEGACY,
        "guard_calls": GUARD_CALLS, "joint_verdicts": verdicts,
        "counts": {"cases": len(RECORDS), "failed_cases": len(failures),
                   "assertions": sum(len(record["assertions"]) for record in RECORDS)},
    }
    prior.update(schema="prime-prefix-independent-software-review/v1", task_id=TASK,
                 scientific_runs=0, benchmark_runs=0, solver_invocations=0,
                 performance_claim=False, attempt_limit=4,
                 oracle_scope="generic n<=5 and exact p5,s2 legacy n<=7 only; no n256 enumeration",
                 no_solver_guard="raising facade installed before encoding import; all forbidden search/refute entry points guarded",
                 runtime_request={"backend": "native_codex", "model": "gpt-6.1-sol",
                                  "reasoning_effort": "xhigh", "fork_turns": "none"},
                 runtime_observed={"task_name": "/root/prefix_adapter_reviewer",
                                   "model": None, "reasoning_effort": None,
                                   "provider_authenticated_identity": None,
                                   "opaque_session_uuid": None, "model_verified": False,
                                   "opus_execution": False},
                 exposed_preexecution_clocks=["2026-10-30 01:59:09 UTC",
                                               "2026-10-30 02:01:46 UTC"])
    prior["attempts"].append(attempt)
    receipt.write_text(json.dumps(prior, indent=2, sort_keys=True) + "\n")
    sys.stdout, sys.stderr = original_out, original_err
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
