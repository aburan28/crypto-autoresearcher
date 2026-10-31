"""Independently authored fixed-contract software assertions for TASK-6b3c1b.

Only the four declared reviewer outputs are written. No producer harness or
outcome is loaded, and no curve entry point, reference or census is invoked.
Invocation attempts are append-only entries in the one receipt document.
"""
import argparse
import ast
import contextlib
import copy
import datetime
import hashlib
import importlib
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
AREA = "research/prime_sat_active_support_implementation_20261030"
META = "coordination/prime_sat_active_support_implementation_20261030"
TASK = "TASK-20261030-6b3c1b"
EXPECTED_TARGET = {
    AREA + "/active_refute.py": "b89d43a0d0c38591d1bba20895323b46b5eaa5082413af6512d2d797671908dc",
    AREA + "/engine_bridge.py": "974aa57c1b8d3a384cab344d78d40c956d0c6a5784e31a138c10b855494c1a50",
}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def polynomials(case):
    # Serialization-boundary conversion only. Invalid-input tests do not use it.
    return [{int(mask): coefficient for mask, coefficient in f.items()}
            for f in case["polynomials"]]


def independent_support(p, n, fs):
    active = [i for i in range(n)
              if any(c % p and (mask >> i) & 1 for f in fs for mask, c in f.items())]
    terms = [(mask, c) for f in fs for mask, c in f.items()]
    nonzero = [(mask, c) for mask, c in terms if c % p]
    counters = {"performed": True, "generators_scanned": len(fs),
                "input_terms_scanned": len(terms), "coefficient_mod_reductions": len(terms),
                "zero_coefficients_discarded": len(terms) - len(nonzero),
                "nonzero_terms_scanned": len(nonzero),
                "set_bit_visits": sum(sum((mask >> i) & 1 for i in range(n))
                                      for mask, _ in nonzero),
                "active_variable_count": len(active)}
    return active, counters


def independent_validation(fs):
    terms = sum(len(f) for f in fs)
    return {"generator_count": len(fs), "term_count": terms,
            "mask_type_range_checks": terms, "coefficient_type_checks": terms}


def independent_identity(p, fs, qs):
    if qs is None or len(qs) != len(fs):
        return False
    products = {}
    for f, q in zip(fs, qs):
        for a, ca in f.items():
            for b, cb in q.items():
                m = a | b
                products[m] = (products.get(m, 0) + ca * cb) % p
    return {m: c for m, c in products.items() if c} == {0: 1}


def independent_models(p, n, fs, domain=()):
    roots = []
    for bits in range(1 << n):
        valid = all(sum(c for m, c in f.items() if bits & m == m) % p == 0 for f in fs)
        permitted = all(any(((bits >> (abs(lit) - 1)) & 1) == (lit > 0)
                            for lit in clause) for clause in domain)
        if valid and permitted:
            roots.append(bits)
    return roots


def independent_restrict(p, fs, depth, prefix):
    residuals = []
    assigned_mask = (1 << depth) - 1
    for f in fs:
        result = {}
        for mask, c in f.items():
            if mask & assigned_mask & ~prefix:
                continue
            remaining = mask & ~assigned_mask
            result[remaining] = (result.get(remaining, 0) + c) % p
        residuals.append({m: c for m, c in result.items() if c})
    return residuals


class Watchdog(TimeoutError):
    pass


def alarm_handler(_signum, _frame):
    raise Watchdog("fixed software watchdog expired")


class Suite:
    def __init__(self, receipt, path, record, contract, bindings):
        self.receipt, self.path, self.record = receipt, path, record
        self.contract, self.bindings = contract, bindings
        self.record.update(assertions=[], cold_cases=[], invalid_controls=[], source_controls=[],
                           direct_controls=[], native_slots=[], native_instances=0)

    def persist(self):
        self.path.write_text(json.dumps(self.receipt, sort_keys=True, separators=(",", ":")) + "\n")

    def check(self, name, condition, details=None):
        self.record["assertions"].append({"name": name, "holds": bool(condition), "details": details})
        if not condition:
            raise AssertionError(name + (": " + str(details) if details is not None else ""))

    def rejected(self, name, function):
        try:
            function()
        except (ValueError, TypeError, AssertionError) as error:
            outcome = {"name": name, "rejected": True,
                       "exception_type": type(error).__name__, "message": str(error)}
        else:
            outcome = {"name": name, "rejected": False}
        self.check(name, outcome["rejected"], outcome)
        return outcome

    def source_checks(self):
        for item in self.bindings["sources"]:
            self.check("source_binding/" + item["path"],
                       digest(ROOT / item["path"]) == item["sha256"])
        for relative, expected in EXPECTED_TARGET.items():
            self.check("target_binding/" + relative, digest(ROOT / relative) == expected)
        raw = ast.parse((ROOT / "research/prime_sat_five_tests_20261029/core.py").read_text())
        candidate = ast.parse((ROOT / (AREA + "/active_refute.py")).read_text())
        rf = next(n for n in raw.body if isinstance(n, ast.FunctionDef) and n.name == "refute")
        kf = next(n for n in candidate.body if isinstance(n, ast.FunctionDef) and n.name == "_kernel")
        expected = copy.deepcopy(rf.body)
        replacements = 0
        for node in ast.walk(ast.Module(body=expected, type_ignores=[])):
            if (isinstance(node, ast.For) and isinstance(node.target, ast.Name)
                    and node.target.id == "i" and ast.dump(node.iter) ==
                    ast.dump(ast.parse("range(ring.n)", mode="eval").body)):
                node.iter = ast.Name(id="active_indices", ctx=ast.Load())
                replacements += 1
        self.check("source_fidelity/one_loop_seam", replacements == 1)
        self.check("source_fidelity/raw_core_body_match", ast.dump(ast.Module(body=expected, type_ignores=[])) ==
                   ast.dump(ast.Module(body=kf.body, type_ignores=[])))
        self.check("source_fidelity/kernel_signature", [a.arg for a in kf.args.args] ==
                   ["ring", "generators", "degree_cap", "row_cap", "active_indices"])
        dispatch = next(n for n in candidate.body if isinstance(n, ast.FunctionDef) and n.name == "checked_refute")
        kernel_calls = [n for n in ast.walk(dispatch) if isinstance(n, ast.Call) and
                        isinstance(n.func, ast.Name) and n.func.id == "_kernel"]
        self.check("source_fidelity/unchanged_generators_passed", len(kernel_calls) == 1 and
                   [ast.dump(a) for a in kernel_calls[0].args] ==
                   [ast.dump(ast.Name(id=v, ctx=ast.Load())) for v in
                    ("ring", "generators", "degree_cap", "row_cap", "indices")])
        self.record["source_controls"].append({"kernel_ast": "raw core body with exactly the active loop seam"})

    def imports(self):
        sys.path.insert(0, str(ROOT / AREA))
        sys.path.insert(0, str(ROOT / "research/prime_sat_prefix_search_20261030"))
        self.active = importlib.import_module("active_refute")
        self.bridge = importlib.import_module("engine_bridge")
        self.engine = importlib.import_module("engine")
        self.checker = load("research/prime_sat_prefix_search_20261030/check.py", "independent_frozen_check")
        self.core = load("research/prime_sat_five_tests_20261029/core.py", "independent_raw_core")
        self.legacy = self.engine.legacy
        self.adapter = self.engine.adapter
        self.cover = load("research/prime_sat_costbridge_controls_20261029/prefix_cover.py", "independent_frozen_cover")
        self.record["software_environment"] = self.engine.environment()
        native = Path(importlib.util.find_spec("pysolvers").origin)
        self.record["software_environment"]["native_path"] = str(native)
        expected = self.bindings["software_environment"]
        self.check("environment/python_executable", sys.executable == self.contract["execution"]["python"])
        self.check("environment/python_sat", importlib.metadata.version("python-sat") == expected["python_sat"])
        self.check("environment/native_hash", digest(native) == expected["native_sha256"])

    def diagnostics(self, details, mode, p, n, fs, index=None):
        support, setup = independent_support(p, n, fs)
        wanted = {"mode": mode, "input_validation": independent_validation(fs),
                  "active_indices": support if mode == "active_support" else None,
                  "support_setup": setup if mode == "active_support" else {"performed": False}}
        if index is not None:
            wanted["call_index"] = index
        self.check("setup/exact_diagnostics/" + mode, details == wanted, {"actual": details, "expected": wanted})

    def cold(self):
        fixed = self.contract["fixed_cold_cases"]
        self.check("cold/exact_14", len(fixed) == 14)
        named_counts = {"empty_n0": (0, 0), "empty_rows": (2, 2),
                        "early_constant_later_support": (1, 1), "zero_row_cap": (1, 1),
                        "gapped_active_order": (5, 4), "gapped_exact_cap": (5, 4),
                        "all_active_order": (4, 4), "mod_p_zero_support": (2, 2),
                        "all_zero_mod_p": (2, 2), "degree_zero_rejection": (2, 2),
                        "characteristic_two": (2, 2)}
        expected_cert = {"early_constant_later_support": [{0: 3}, {}],
                         "gapped_active_order": [{2: 1}, {0: 4}, {}],
                         "gapped_exact_cap": [{2: 1}, {0: 4}, {}],
                         "all_active_order": [{1: 1}, {0: 4}, {}],
                         "mod_p_zero_support": [{0: 1}, {0: 4}],
                         "characteristic_two": [{0: 1}, {0: 1}]}
        refuted = {"early_constant_later_support", "gapped_active_order", "gapped_exact_cap",
                   "all_active_order", "duplicate_generator", "mod_p_zero_support", "characteristic_two"}
        self.results = {}
        for case in fixed:
            name, p, n = case["id"], case["p"], case["n"]
            fs = polynomials(case)
            untouched = copy.deepcopy(fs)
            support, _ = independent_support(p, n, fs)
            self.check("cold/" + name + "/independent_support", support == case["expected_support"])
            raw = self.core.refute(self.core.BoolRing(n, p), fs, case["degree_cap"], case["row_cap"])
            outputs, diagnostics = {}, {}
            for mode in self.contract["native_modes"]:
                detail = {}
                result = self.active.checked_refute(mode, self.core.BoolRing(n, p), fs,
                                                    case["degree_cap"], case["row_cap"], diagnostics=detail)
                self.diagnostics(detail, mode, p, n, fs)
                outputs[mode], diagnostics[mode] = result, detail
                self.check("cold/" + name + "/result_schema/" + mode, set(result) == set(raw))
                if result["status"] == "refuted":
                    self.check("cold/" + name + "/own_identity/" + mode,
                               independent_identity(p, fs, result["certificate"]))
                    self.check("cold/" + name + "/raw_checker/" + mode,
                               self.core.check_refutation(p, n, fs, result["certificate"]))
                    accepted, _ = self.legacy.certificate_check(p, fs, result["certificate"])
                    self.check("cold/" + name + "/encoding_checker/" + mode, accepted)
                else:
                    self.check("cold/" + name + "/no_certificate/" + mode, result["certificate"] is None)
            base, active = outputs["baseline"], outputs["active_support"]
            self.check("cold/" + name + "/baseline_raw_full_equality", base == raw)
            public = self.active.refute_active(self.core.BoolRing(n, p), fs, case["degree_cap"], case["row_cap"])
            self.check("cold/" + name + "/public_active_api", public == active)
            self.check("cold/" + name + "/input_preserved", fs == untouched)
            expected_status = "refuted" if name in refuted else "unknown"
            self.check("cold/" + name + "/active_status", active["status"] == expected_status)
            self.check("cold/" + name + "/baseline_status", base["status"] ==
                       ("unknown" if name == "gapped_exact_cap" else expected_status))
            if name in named_counts:
                self.check("cold/" + name + "/fixed_attempt_counts",
                           (base["attempted_rows"], active["attempted_rows"]) == named_counts[name])
            if name in expected_cert:
                self.check("cold/" + name + "/ordered_certificate", active["certificate"] == expected_cert[name])
            if base["status"] == "refuted":
                self.check("cold/" + name + "/one_way_success", active["status"] == "refuted" and
                           active["certificate"] == base["certificate"] and
                           active["attempted_rows"] <= base["attempted_rows"])
            if name in ("zero_row_cap", "gapped_exact_cap"):
                self.check("cold/" + name + "/baseline_cap", base["resource_capped"] and
                           base["status"] == "unknown" and not base["closure_complete"])
            if name == "gapped_exact_cap":
                self.check("cold/exact_cap/active_success", not active["resource_capped"])
            if name == "all_active_order":
                self.check("cold/all_active/complete_result_equality", active == base)
                self.check("cold/all_active/additional_setup", diagnostics["active_support"]["support_setup"]["performed"])
            roots = independent_models(p, n, fs)
            if active["status"] == "refuted":
                self.check("cold/" + name + "/refutation_has_no_roots", roots == [])
            if name == "free_inactive_models":
                self.check("cold/free_inactive_models/exact_free_extensions", roots == [0, 1, 4, 5])
            row = {"id": name, "input": case, "independent_support": support,
                   "independent_models": roots, "raw_core": raw, "outputs": outputs, "diagnostics": diagnostics}
            self.record["cold_cases"].append(row)
            self.results[name] = row
        # Exactly one reversed active-order mutation, held outside the target API.
        case = next(c for c in fixed if c["id"] == "all_active_order")
        fs = polynomials(case)
        mutant = self.active._kernel(self.core.BoolRing(2, 5), fs, 2, 64, [1, 0])
        self.check("source_control/reversed_order_changes_certificate", mutant["certificate"] != expected_cert["all_active_order"])
        rejection = self.rejected("source_control/reversed_order_equality_rejects",
                                  lambda: self._assert_equal(mutant["certificate"], expected_cert["all_active_order"]))
        self.record["source_controls"].append({"name": "reversed_active_order", "mutant": mutant, "control": rejection})
        above = next(c for c in fixed if c["id"] == "above_cap_support")
        bad_support = independent_support(above["p"], above["n"],
                                         [f for f in polynomials(above) if all(m.bit_count() <= 1 for m in f)])[0]
        rejection = self.rejected("source_control/omitted_above_cap_support_rejected",
                                  lambda: self._assert_equal(bad_support, above["expected_support"]))
        self.record["source_controls"].append({"name": "bad_support", "bad_support": bad_support, "control": rejection})

    @staticmethod
    def _assert_equal(left, right):
        assert left == right, (left, right)

    def invalid(self):
        cases = []
        for key, normal in (("n", 2), ("p", 5), ("degree", 2), ("rows", 8)):
            for bad in (True, float(normal)):
                cases.append((key + "/" + type(bad).__name__, {key: bad}))
        for key, value in (("n", -1), ("p", 1), ("degree", -1), ("rows", -1)):
            cases.append((key + "/range", {key: value}))
        cases.extend((name, {"fs": value}) for name, value in [
            ("negative_mask", [{-1: 1}]), ("out_of_range_mask", [{4: 1}]),
            ("bool_mask", [{True: 1}]), ("float_mask", [{1.0: 1}]),
            ("string_mask", [{"1": 1}]), ("aliased_masks", [{1: 1, "1": 2}]),
            ("bool_coefficient", [{1: True}]), ("float_coefficient", [{1: 1.0}]),
            ("nonmapping_generator", [None]), ("nonsequence_generators", {1: 1}),
            ("late_malformed_after_constant", [{0: 1}, {4: 1}]),
            ("late_nonmapping_after_constant", [{0: 1}, None])])
        for name, changed in cases:
            config = {"n": 2, "p": 5, "degree": 2, "rows": 8, "fs": [{1: 1}]}
            config.update(changed)
            for mode in self.contract["native_modes"]:
                result = self.rejected("invalid/" + name + "/" + mode,
                    lambda c=config, m=mode: self.active.checked_refute(m, SimpleNamespace(n=c["n"], p=c["p"]),
                                                                       c["fs"], c["degree"], c["rows"]))
                self.record["invalid_controls"].append(result)
        self.record["invalid_controls"].append(self.rejected("invalid/unknown_mode_dispatch", lambda:
            self.active.checked_refute("other", self.core.BoolRing(2, 5), [], 0)))
        self.record["invalid_controls"].append(self.rejected("invalid/unknown_mode_bridge", lambda:
            self.bridge._private_engine("other")))

    def private_instances(self):
        self.shared_before = {k: id(v) for k, v in vars(self.legacy).items()}
        self.engine_before = {k: id(v) for k, v in vars(self.engine).items()}
        self.modules_before = {k: id(sys.modules[k]) for k in ("core", "encoding", "engine")}
        engines = []
        case = self.results["all_active_order"]["input"]
        for mode in ("baseline", "active_support", "baseline", "active_support"):
            private, sidecar, guard = self.bridge._private_engine(mode)
            self.check("private/fresh_module", all(private is not old for old in engines))
            self.check("private/shallow_namespace", all(getattr(private.legacy, k) is v
                       for k, v in vars(self.legacy).items() if k != "refute"))
            self.check("private/only_refute_overridden", set(vars(private.legacy)) == set(vars(self.legacy)) and
                       private.legacy.refute is not self.legacy.refute)
            for name, method in vars(self.engine.PrefixPropagator).items():
                if callable(method) and hasattr(method, "__code__"):
                    other = getattr(private.PrefixPropagator, name)
                    self.check("private/callback_body/" + name, other.__code__.co_code == method.__code__.co_code and
                               other.__code__.co_consts == method.__code__.co_consts and
                               other.__globals__ is vars(private))
            engines.append(private)
            result = private.legacy.refute(self.core.BoolRing(2, 5), polynomials(case), 2, 64)
            self.check("private/alternating_modes_result", result == self.results["all_active_order"]["raw_core"])
            self.check("private/isolated_sidecar", len(sidecar["calls"]) == 1)
            self.diagnostics(sidecar["calls"][0], mode, 5, 2, polynomials(case), 0)
            guard()
        self.shared_unchanged()
        self.record["source_controls"].append({"name": "four_alternating_private_instances", "holds": True})

    def shared_unchanged(self):
        self.check("private/shared_encoding_identity", self.shared_before == {k: id(v) for k, v in vars(self.legacy).items()})
        self.check("private/shared_engine_identity", self.engine_before == {k: id(v) for k, v in vars(self.engine).items()})
        self.check("private/no_sys_modules_replacement", self.modules_before ==
                   {k: id(sys.modules[k]) for k in self.modules_before})

    def direct(self):
        for mode in self.contract["native_modes"]:
            private, sidecar, guard = self.bridge._private_engine(mode)
            limits = dict(self.contract["native_limits"])
            prop = private.PrefixPropagator(self.legacy.CountedRing(3, 5), [{1: 1}], 1, limits,
                                             "partial_prefix", [0, 1, 3])
            prop.on_assignment(-1, fixed=True)
            prop.on_new_level()
            prop.on_assignment(2)
            prop.on_new_level()
            prop.on_assignment(-3)
            prop.on_backtrack(1)
            self.check("direct/backtrack_above_level/" + mode, set(prop.assignments) == {0, 1})
            prop.on_backtrack(0)
            self.check("direct/fixed_survives/" + mode, prop.assignments == {0: (0, 0, True)})
            # Model-only ensures no implicit theory action confounds pending-state control.
            empty = private.PrefixPropagator(self.legacy.CountedRing(2, 5), [{0: 1}], 2, limits,
                                              "model_only", [0, 1, 2])
            self.check("direct/no_pending_is_false/" + mode, empty.has_clause() is False)
            self.record["direct_controls"].append(self.rejected("direct/no_pending_delivery/" + mode, empty.add_clause))
            self.record["direct_controls"].append(self.rejected("direct/no_unproved_rejection/" + mode, lambda: empty._reject(0)))
            self.check("direct/invalid_model_actual_proof/" + mode, empty.check_model([-1, -2]) is False and
                       bool(empty.learned) and bool(empty.pending))
            proof = empty.learned[0]
            self.check("direct/real_empty_clause/" + mode, proof["depth"] == 0 and proof["clause"] == [] and empty.has_clause())
            self.check("direct/empty_clause_delivery/" + mode, empty.add_clause() == [])
            self.check("direct/empty_consumed/" + mode, empty.has_clause() is False)
            disabled = dict(limits, pc_calls=0)
            leaf = private.PrefixPropagator(self.legacy.CountedRing(2, 5), [{3: 1, 0: 4}], 2, disabled,
                                             "partial_prefix", [0, 1, 2])
            leaf.on_assignment(-1)
            self.check("direct/zero_pc_no_partial/" + mode, leaf.has_clause() is False)
            before = len(sidecar["calls"])
            self.check("direct/zero_pc_rejects_via_fallback/" + mode, leaf.check_model([-1, -2]) is False)
            item = leaf.learned[0]
            self.check("direct/checked_leaf_fallback/" + mode, item["trigger"] == "leaf_fallback" and
                       item["depth"] == 2 and leaf.events["pc_calls"] == 0 and
                       leaf.events["leaf_fallbacks"] == leaf.events["leaf_inverse_calls"] == 1 and
                       len(sidecar["calls"]) == before and
                       independent_identity(5, independent_restrict(5, [{3: 1, 0: 4}], 2, 0), item["certificate"]))
            accepted = self.adapter.verify_transcript(5, 2, 2, [{3: 1, 0: 4}], [], leaf.snapshot())
            self.check("direct/fallback_adapter_accepts/" + mode, accepted["valid"] and accepted["declared_status"] == "censored")
            self.record["direct_controls"].append({"mode": mode, "backtracking": True,
                                                   "empty_proof": proof, "fallback_proof": item})
            guard()
        supplied = {"status": "censored", "models": [], "learned": [
            {"depth": 0, "prefix": 0, "clause": [], "certificate": [{0: 1}]}]}
        checked = self.adapter.verify_transcript(5, 2, 2, [{0: 1}], [], supplied)
        self.check("direct/closed_censored_stays_censored", checked["cover_complete"] and
                   checked["declared_status"] == "censored" and not checked["projected_model_set_complete"])
        mutations = {"corrupt_multiplier": copy.deepcopy(supplied), "malformed_prefix": copy.deepcopy(supplied),
                     "invalid_model": {"status": "censored", "models": [0], "learned": []},
                     "missing_cover_complete": {"status": "complete", "models": [], "learned": []}}
        mutations["corrupt_multiplier"]["learned"][0]["certificate"] = [{0: 2}]
        mutations["malformed_prefix"]["learned"][0]["clause"] = [1]
        for name, answer in mutations.items():
            self.record["direct_controls"].append(self.rejected("direct/adapter_rejects/" + name, lambda a=answer:
                self.adapter.verify_transcript(5, 2, 2, [{0: 1}], [], a)))
        self.shared_unchanged()

    def reconcile_sidecar(self, answer, family, mode):
        fs = polynomials(family)
        details = answer[self.bridge.SIDECAR]
        self.check("native/sidecar_mode", details["mode"] == mode)
        self.check("native/sidecar_pc_call_count", len(details["calls"]) == len(answer["attempts"]) ==
                   answer["costs"]["search_events"]["pc_calls"])
        for i, (detail, attempt) in enumerate(zip(details["calls"], answer["attempts"])):
            residuals = independent_restrict(family["p"], fs, attempt["depth"], attempt["prefix"])
            self.diagnostics(detail, mode, family["p"], family["n"], residuals, i)

    def native(self):
        families = self.contract["fixed_native_families"]
        limits = dict(self.contract["native_limits"])
        self.check("native/fixed_inventory", len(families) == 4 and
                   self.contract["native_modes"] == ["baseline", "active_support"] and
                   self.contract["native_strategies"] == ["model_only", "partial_prefix", "partial_prefix_aa"])
        old_snapshot_fields = set(self.engine.PrefixPropagator(self.legacy.CountedRing(2, 5), [], 2, limits,
                                                              "model_only", [0, 1, 2]).snapshot())
        for family in families:
            fs = polynomials(family)
            for mode in self.contract["native_modes"]:
                for strategy in self.contract["native_strategies"]:
                    slot = {"id": "/".join((family["id"], mode, strategy)), "family": family,
                            "mode": mode, "strategy": strategy, "limits": limits,
                            "started_at": utc(), "status": "started", "checkpoints": []}
                    self.record["native_slots"].append(slot)
                    self.record["native_instances"] += 1
                    self.check("native/per_suite_limit", self.record["native_instances"] <= 24)
                    prior = sum(a.get("native_instances", 0) for a in self.receipt["attempts"][:-1])
                    self.check("native/actor_limit", prior + self.record["native_instances"] <= 96)
                    self.persist()
                    remaining = max(0.001, 180 - (time.monotonic() - self.started_mono))
                    signal.setitimer(signal.ITIMER_REAL, min(5, remaining))
                    try:
                        answer = self.bridge.solve(self.legacy.CountedRing(family["n"], family["p"]), fs,
                            copy.deepcopy(family["domain"]), family["projected_bits"], limits,
                            strategy, family["prefix_depths"], lambda snap: slot["checkpoints"].append(copy.deepcopy(snap)),
                            refuter_mode=mode)
                        slot["answer"] = answer
                        signal.setitimer(signal.ITIMER_REAL, max(0.001, 180 - (time.monotonic() - self.started_mono)))
                        checked = self.adapter.verify_transcript(family["p"], family["n"], family["projected_bits"],
                            fs, family["domain"], answer, aux_bound=family["aux_bound"])
                        slot["check"] = checked
                        self.check("native/" + slot["id"] + "/complete_expected_projection", checked["valid"] and
                                   checked["projected_model_set_complete"] and checked["projected_models"] == family["expected_models"])
                        # Independent enumeration occurs only after the search returns.
                        roots = independent_models(family["p"], family["n"], fs, family["domain"])
                        projections = sorted({x & ((1 << family["projected_bits"]) - 1) for x in roots})
                        slot["independent_models"], slot["independent_projections"] = roots, projections
                        self.check("native/" + slot["id"] + "/own_tiny_models", projections == family["expected_models"] and
                                   all(x in roots for x in answer["models"]))
                        prefixes = [(item["depth"], item["prefix"]) for item in answer["learned"]]
                        prefixes += [(family["projected_bits"], x & ((1 << family["projected_bits"]) - 1))
                                     for x in answer["models"]]
                        cover = self.cover.verify_cover(family["n"], prefixes,
                                                       projected_bits=family["projected_bits"], aux_bound=family["aux_bound"])
                        slot["direct_coverage_check"] = cover
                        self.check("native/" + slot["id"] + "/coverage", cover["covered"])
                        for item in answer["learned"]:
                            residuals = independent_restrict(family["p"], fs, item["depth"], item["prefix"])
                            self.check("native/" + slot["id"] + "/own_identity",
                                       independent_identity(family["p"], residuals, item["certificate"]))
                        self.checker.counters_check(answer, family["n"], limits)
                        self.check("native/" + slot["id"] + "/old_counters", True)
                        self.reconcile_sidecar(answer, family, mode)
                        self.check("native/" + slot["id"] + "/old_schema", set(answer) ==
                                   old_snapshot_fields | {"environment", self.bridge.SIDECAR})
                        for snap in slot["checkpoints"]:
                            self.check("native/checkpoint_old_fields", set(snap) in
                                       (old_snapshot_fields | {self.bridge.SIDECAR},
                                        old_snapshot_fields | {"environment", self.bridge.SIDECAR}))
                            self.reconcile_sidecar(snap, family, mode)
                        if family["id"] == "positive" and strategy != "model_only":
                            self.check("native/" + slot["id"] + "/actual_partial_conflict", any(
                                item["trigger"] == "partial" and item["depth"] == 1 and item["prefix"] == 0 and
                                item["assigned_count"] < family["n"] for item in answer["learned"]))
                        if family["id"] == "negative":
                            self.check("native/" + slot["id"] + "/no_false_depth1_conflict", not any(
                                item["depth"] == 1 for item in answer["learned"]))
                        if family["id"] == "empty":
                            self.check("native/" + slot["id"] + "/actual_empty_clause", any(
                                item["depth"] == 0 and item["clause"] == [] for item in answer["learned"]))
                        if family["id"] == "fiber":
                            self.check("native/" + slot["id"] + "/projected_witness_and_aux_range", len(answer["models"]) == 1 and
                                       answer["models"][0] & 1 == 0 and answer["models"][0] >> 1 < 3)
                        self.shared_unchanged()
                        slot["status"] = "passed"
                    except BaseException as error:
                        slot.update(status="failed", exception_type=type(error).__name__, message=str(error))
                        raise
                    finally:
                        slot["ended_at"] = utc()
                        self.persist()
        self.check("native/exact_24_executed", self.record["native_instances"] == 24 and
                   len(self.record["native_slots"]) == 24 and all(s["status"] == "passed" for s in self.record["native_slots"]))

    def run(self):
        self.started_mono = time.monotonic()
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.setitimer(signal.ITIMER_REAL, 180)
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
        self.source_checks()
        self.imports()
        self.cold()
        self.invalid()
        self.private_instances()
        self.direct()
        self.native()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    path = Path(args.receipt)
    allowed = ROOT / AREA / TASK / "independent-results.json"
    if path.resolve() != allowed:
        raise SystemExit("receipt outside fixed write scope")
    contract = json.loads((ROOT / META / "software-contract.json").read_text())
    bindings = json.loads((ROOT / META / "source-inputs.json").read_text())
    receipt = json.loads(path.read_text()) if path.exists() else {
        "schema": "prime-active-support-independent-software-results/v1", "task_id": TASK,
        "scope": "fixed software fidelity only", "attempts": []}
    if len(receipt["attempts"]) >= 4:
        raise SystemExit("fixed four-attempt ceiling reached")
    if any(a.get("frozen_target_defect", False) for a in receipt["attempts"]):
        raise SystemExit("retained frozen target defect forbids further execution")
    paths = [item["path"] for item in bindings["sources"]] + list(EXPECTED_TARGET)
    paths += [META + "/" + name for name in ("software-contract.json", "source-inputs.json", "review-plan.yaml", "inference-amendment.yaml")]
    record = {"attempt": len(receipt["attempts"]) + 1, "started_at": utc(),
              "argv": [sys.executable, "-B", *sys.argv], "cwd": os.getcwd(),
              "environment": {"PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE")},
              "limits": {"suite_watchdog_seconds": 180, "native_slot_watchdog_seconds": 5,
                         "memory_bytes": 2 * 1024**3, "maximum_native_instances": 24,
                         "maximum_actor_native_instances": 96, "maximum_actor_attempts": 4},
              "before_sha256": {p: digest(ROOT / p) for p in paths},
              "new_source_text": {p: (ROOT / p).read_text() for p in EXPECTED_TARGET},
              "harness_source_text": Path(__file__).read_text(),
              "harness_sha256": digest(Path(__file__)), "scientific_runs": 0, "curve_invocations": 0,
              "benchmarks": 0, "historical_replays": 0, "status": "started"}
    receipt["attempts"].append(record)
    suite = Suite(receipt, path, record, contract, bindings)
    suite.persist()
    output, errors = io.StringIO(), io.StringIO()
    returncode = 1
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            suite.run()
            print("All fixed independent software assertions passed; 14 cold fixtures and 24 native slots.")
        returncode = 0
        record["status"] = "passed"
    except BaseException as error:
        traceback.print_exc(file=errors)
        record.update(status="failed", exception_type=type(error).__name__, message=str(error),
                      timeout=isinstance(error, Watchdog))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        record.update(ended_at=utc(), returncode=returncode, stdout=output.getvalue(), stderr=errors.getvalue(),
                      after_sha256={p: digest(ROOT / p) for p in paths})
        record["all_bound_sources_unchanged"] = record["before_sha256"] == record["after_sha256"]
        suite.persist()
    sys.stdout.write(output.getvalue())
    sys.stderr.write(errors.getvalue())
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
