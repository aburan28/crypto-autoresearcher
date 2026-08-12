from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# ---------------------------------------------------------------------------
# SOURCE OF TRUTH held independently of the produced artifacts. These are READ
# facts (frozen scaffold / prior committed records), NOT invented values.
# ---------------------------------------------------------------------------

# From BATCH-022 scaffold/lifetime_hooks.py::LifetimeRegistry.REQUIRED_HOOK_IDS.
CANONICAL_HOOK_IDS: List[str] = [
    "W_label", "R_label", "W_sieve", "R_sieve", "B_input", "B_attempt",
    "B_sieve", "accepted_transcript", "B_post", "B_recovery", "M_tail",
    "B_candidate",
]

# From BATCH-022 scaffold/state_machine.py::STAGE_LIVE_SETS (== BATCH-023 verbatim).
CANONICAL_STAGE_LIVE_SETS: Dict[str, List[str]] = {
    "preparation": ["B_input", "B_attempt", "W_label", "R_label"],
    "sieve_attempt": ["B_input", "B_attempt", "W_sieve", "R_sieve", "B_sieve"],
    "recovery": ["B_input", "B_attempt", "B_post", "B_recovery", "accepted_transcript"],
    "tail_verification": ["B_input", "B_attempt", "B_recovery", "M_tail", "B_candidate"],
}

# Only M_tail carries a width_decl parameter in birth_M_tail (symbolic-only).
CANONICAL_HOOKS_WITH_WIDTH_CHANNEL = frozenset({"M_tail"})

EXPECTED_OPERATOR_ID = "max_over_stages_of_sum_of_live_member_slot_widths"
EXPECTED_DISPOSITION = "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
EXPECTED_COLLIMATION_COMMIT = "6f9188e4eb5611bcfdf29a3e1ec3cd69a29a50e9"
EXPECTED_SCALE_LABEL = "host_integration_boundary_specification_no_scale"

# A numeric leaf is permitted ONLY under these structural keys. Anything else is
# an invented/out-of-protocol number (a real width, unit, peak, tau, or security
# figure smuggled in) and is rejected.
_ALLOWED_NUMERIC_LEAF_KEYS = frozenset({
    "count", "maximum_runs", "runs_attempted", "hooks_named_count",
    "required_hook_count", "implemented_method_count",
})

# Keys/ancestors that must NEVER carry a numeric leaf (must stay null/absent).
_FORBIDDEN_NUMERIC_KEY_SUBSTRINGS = (
    "width", "peak", "byte", "qubit", "tau", "security", "bit",
    "probability", "load",
)

# Flags that must never be True (allowlist-hardened per RT-20260730-129 OBJ-1:
# includes novel clearance-like keys, not just the historical denylist).
_FORBIDDEN_TRUE_KEYS = frozenset({
    "query_memory_cleared", "query_memory_clearance", "query_memory_solved",
    "clearance", "cleared", "pin_complete", "problem_closed",
    "breakthrough_claim", "completion_claim", "numeric_security_claim",
    "invent_tau", "tau_invented", "invents_tau", "invent_numeric_values",
    "invent_security_bits", "invent_probabilities", "cryptographic_scale",
    "gate_B_taken", "toy_peak_byte_lane_iterated", "batch022_scaffold_modified",
    "batch014_equated", "collimation_sieve_apis_invented", "reuses_toy_numeric",
    "is_numeric_instantiation", "measurement_performed", "advanced_this_batch",
    "is_closure_claim", "named_obstruction", "meets_inventor_protocol_s4",
    "source_available", "admissible_pin", "real_widths_sourced",
    "real_units_sourced", "real_peak_sourced",
})


def task_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_yaml(name: str) -> Dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML required")
    data = yaml.safe_load((task_dir() / name).read_text())
    if not isinstance(data, dict):
        raise ValueError(name)
    return data


def load_contract() -> Dict[str, Any]:
    return load_yaml("host_width_contract.yaml")["host_width_contract"]


def load_plan() -> Dict[str, Any]:
    return load_yaml("validation_falsification_plan.yaml")["validation_falsification_plan"]


# ---------------------------------------------------------------------------
# Generic recursive scanners.
# ---------------------------------------------------------------------------

def _walk_numeric(node: Any, chain: List[str], hits: List[Dict[str, Any]]) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        leaf = chain[-1] if chain else None
        # index tokens like "[0]" are transparent to key allow/deny decisions.
        keychain = [c for c in chain if not (c.startswith("[") and c.endswith("]"))]
        real_leaf = keychain[-1] if keychain else None
        allowed = real_leaf in _ALLOWED_NUMERIC_LEAF_KEYS
        forbidden = any(
            sub in c.lower() for c in keychain for sub in _FORBIDDEN_NUMERIC_KEY_SUBSTRINGS
        )
        if forbidden or not allowed:
            hits.append({"path": ".".join(chain), "key": real_leaf, "value": node})
        return
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_numeric(v, chain + [str(k)], hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_numeric(v, chain + [f"[{i}]"], hits)


def _walk_forbidden_true(node: Any, chain: List[str], hits: List[Dict[str, Any]]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k in _FORBIDDEN_TRUE_KEYS and v is True:
                hits.append({"path": ".".join(chain + [str(k)]), "key": k})
            _walk_forbidden_true(v, chain + [str(k)], hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_forbidden_true(v, chain + [f"[{i}]"], hits)


# ---------------------------------------------------------------------------
# Contract checks (each accepts an optional dict for mutation testing).
# ---------------------------------------------------------------------------

def check_contract_fields_present(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = c if c is not None else load_contract()
    problems: List[str] = []

    hooks = c.get("width_emission_hooks", [])
    ids = [h.get("hook_id") for h in hooks]
    if sorted(ids) != sorted(CANONICAL_HOOK_IDS):
        problems.append("width_emission_hooks must name exactly the 12 frozen hook ids")

    for h in hooks:
        for field in ("hook_id", "object_class", "live_in_stages",
                      "birth_signature_ref", "real_per_slot_width"):
            if field not in h:
                problems.append(f"hook {h.get('hook_id')} missing field {field}")
        rpw = h.get("real_per_slot_width", {})
        for field in ("value", "units", "sourced_from"):
            if field not in rpw:
                problems.append(f"hook {h.get('hook_id')} real_per_slot_width missing {field}")

    op = c.get("composition_operator", {})
    if op.get("id") != EXPECTED_OPERATOR_ID:
        problems.append("composition_operator.id mismatch")
    if op.get("invented") is not False:
        problems.append("composition_operator.invented must be False")
    if "consumes" not in op:
        problems.append("composition_operator.consumes missing")
    if "bound_units" not in op:
        problems.append("composition_operator.bound_units field missing (must be present, null)")
    if "peak" not in op:
        problems.append("composition_operator.peak field missing")

    if "host" not in c:
        problems.append("host block missing")
    return {"passed": not problems, "problems": problems}


def check_hook_width_channels(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Only M_tail may declare a width channel; matches the frozen scaffold."""
    c = c if c is not None else load_contract()
    problems: List[str] = []
    for h in c.get("width_emission_hooks", []):
        hid = h.get("hook_id")
        has_channel = bool(h.get("width_emission_point_exists_in_scaffold"))
        should = hid in CANONICAL_HOOKS_WITH_WIDTH_CHANNEL
        if has_channel != should:
            problems.append(
                f"hook {hid} width_emission_point_exists_in_scaffold={has_channel} "
                f"but scaffold says {should}")
        if hid == "M_tail" and h.get("scaffold_width_declaration_param") != "width_decl":
            problems.append("M_tail must declare scaffold_width_declaration_param: width_decl")
        if hid != "M_tail" and h.get("scaffold_width_declaration_param") is not None:
            problems.append(f"hook {hid} must have scaffold_width_declaration_param: null")
    return {"passed": not problems, "problems": problems}


def check_all_real_widths_null(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Every REAL width/unit/peak must be null and sources unavailable."""
    c = c if c is not None else load_contract()
    problems: List[str] = []
    for h in c.get("width_emission_hooks", []):
        rpw = h.get("real_per_slot_width", {})
        if rpw.get("value") is not None:
            problems.append(f"hook {h.get('hook_id')} real width value must be null")
        if rpw.get("units") is not None:
            problems.append(f"hook {h.get('hook_id')} real width units must be null")
        if rpw.get("source_available") is not False:
            problems.append(f"hook {h.get('hook_id')} source_available must be False")
    op = c.get("composition_operator", {})
    if op.get("bound_units") is not None:
        problems.append("operator.bound_units must be null (unsourced)")
    peak = op.get("peak", {})
    if peak.get("value") is not None:
        problems.append("operator.peak.value must be null (no numeric peak)")
    if peak.get("units") is not None:
        problems.append("operator.peak.units must be null")
    uv = c.get("unsourced_values_null", {})
    for k in ("all_real_per_slot_widths_null", "all_real_units_null",
              "real_peak_null", "tau_null", "security_bits_null"):
        if uv.get(k) is not True:
            problems.append(f"unsourced_values_null.{k} must be True")
    return {"passed": not problems, "problems": problems}


def check_no_invented_numerics(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = c if c is not None else load_contract()
    hits: List[Dict[str, Any]] = []
    _walk_numeric(c, [], hits)
    return {"passed": not hits, "hits": hits}


def check_pin_untouched(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = c if c is not None else load_contract()
    problems: List[str] = []
    host = c.get("host", {})
    if host.get("commit") != EXPECTED_COLLIMATION_COMMIT:
        problems.append("host.commit must be the frozen CollimationSieve pin")
    if host.get("apis_invented") is not False:
        problems.append("host.apis_invented must be False")
    if host.get("admissible_pin") is not False:
        problems.append("host.admissible_pin must be False (no_admissible_pin)")
    if host.get("batch020_pin_status") != "no_admissible_pin":
        problems.append("host.batch020_pin_status must be no_admissible_pin")
    if c.get("collimation_sieve_apis_invented") is not False:
        problems.append("collimation_sieve_apis_invented must be False")
    if c.get("batch022_scaffold_modified") is not False:
        problems.append("batch022_scaffold_modified must be False")
    return {"passed": not problems, "problems": problems}


def check_stage_membership_matches_scaffold(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = c if c is not None else load_contract()
    disk = {s: list(v) for s, v in c.get("stage_live_sets", {}).items()}
    matches = disk == CANONICAL_STAGE_LIVE_SETS
    return {"passed": matches, "membership_matches": matches}


def check_no_illicit_clearance(c: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = c if c is not None else load_contract()
    hits: List[Dict[str, Any]] = []
    _walk_forbidden_true(c, [], hits)
    problems: List[str] = []
    if c.get("query_memory_clearance") is not False:
        problems.append("query_memory_clearance must be False")
    if c.get("cryptographic_scale") is not False:
        problems.append("cryptographic_scale must be False")
    if c.get("scale_label") != EXPECTED_SCALE_LABEL:
        problems.append("scale_label mismatch")
    if c.get("disposition") != EXPECTED_DISPOSITION:
        problems.append("disposition must remain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED")
    return {"passed": not hits and not problems,
            "forbidden_true_hits": hits, "problems": problems}


# ---------------------------------------------------------------------------
# Validation/falsification plan checks.
# ---------------------------------------------------------------------------

def check_validation_plan(p: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = p if p is not None else load_plan()
    problems: List[str] = []
    if p.get("registered_before_measurement") is not True:
        problems.append("plan must be registered_before_measurement: True")
    if p.get("measurement_performed") is not False:
        problems.append("measurement_performed must be False (zero compute)")
    proc = p.get("validation_procedure", {})
    steps = proc.get("steps", [])
    if not isinstance(steps, list) or len(steps) < 1:
        problems.append("validation_procedure.steps must be a non-empty list")
    fcs = p.get("falsification_conditions", [])
    if not isinstance(fcs, list) or len(fcs) < 1:
        problems.append("at least one falsification_condition required")
    for fc in fcs if isinstance(fcs, list) else []:
        if not fc.get("condition") or not fc.get("falsifies"):
            problems.append(f"falsification condition {fc.get('id')} missing condition/falsifies")
    if "controls_before_belief" not in p or "null_object" not in p.get("controls_before_belief", {}):
        problems.append("controls_before_belief.null_object required (inventor-protocol §3)")
    return {"passed": not problems, "problems": problems}


# ---------------------------------------------------------------------------
# Sibling status-file checks.
# ---------------------------------------------------------------------------

def check_memory_map_status() -> Dict[str, Any]:
    m = load_yaml("memory_map_status.yaml")["memory_map_status"]
    qm = m.get("qm_memory_map", {})
    st = m.get("qm_stopping", {})
    passed = (
        qm.get("status_after_batch") == "numeric_composition_operator_protocol_toy_partial"
        and qm.get("advanced_this_batch") is False
        and qm.get("clearance") is False
        and qm.get("query_memory_cleared") is False
        and qm.get("cryptographic_scale") is False
        and st.get("control_result") == "FAIL"
        and st.get("obstruction_analysis_status") == "unverified"
        and st.get("tau_invented") is False
        and st.get("joint_finiteness_established") is False
        and m.get("batch020_pin_status_retained") == "no_admissible_pin"
        and m.get("qm_error", {}).get("status") == "f_union_ledger_partial"
        and "BATCH-039" in st.get("fail_retained_from", [])
        and "BATCH-018" in st.get("fail_retained_from", [])
    )
    return {"passed": passed}


def check_classification() -> Dict[str, Any]:
    d = load_yaml("classification.yaml")["classification"]
    obs = d.get("qm_stopping_obstruction", {})
    passed = (
        d.get("disposition") == EXPECTED_DISPOSITION
        and d.get("control_result") == "FAIL"
        and d.get("cryptographic_scale") is False
        and d.get("non_extrapolation") is True
        and d.get("qm_statuses", {}).get("QM_MEMORY_MAP")
            == "numeric_composition_operator_protocol_toy_partial"
        and d.get("qm_statuses", {}).get("QM_STOPPING") == "remains_open_FAIL"
        and obs.get("status") == "unverified"
        and obs.get("is_closure_claim") is False
        and obs.get("meets_inventor_protocol_s4") is False
        and d.get("inference", {}).get("model_verified") is False
    )
    return {"passed": passed}


def check_obstruction_analysis(text: Optional[str] = None) -> Dict[str, Any]:
    """The .md must carry the §4 sections and an honest machine-readable status."""
    if text is None:
        text = (task_dir() / "stopping_obstruction_analysis.md").read_text()
    problems: List[str] = []
    if "OBSTRUCTION_ANALYSIS_STATUS: unverified" not in text:
        problems.append("obstruction analysis must record status unverified")
    for token in ("named_obstruction: false", "meets_inventor_protocol_s4: false",
                  "is_closure_claim: false", "qm_stopping_control_result: FAIL"):
        if token not in text:
            problems.append(f"missing honest marker: {token}")
    # §4 structure: candidate obstruction, argument, forward guidance.
    for heading in ("Candidate obstruction", "Forward guidance", "fatigue"):
        if heading.lower() not in text.lower():
            problems.append(f"missing §4 element: {heading}")
    # Must NOT smuggle a closure/clearance in prose.
    for bad in ("QM-STOPPING CLEARED", "obstruction proven", "closure achieved"):
        if bad.lower() in text.lower():
            problems.append(f"illicit closure/clearance phrase: {bad}")
    return {"passed": not problems, "problems": problems}


def run_all_checks() -> Dict[str, Any]:
    return {
        "contract_fields_present": check_contract_fields_present(),
        "hook_width_channels": check_hook_width_channels(),
        "all_real_widths_null": check_all_real_widths_null(),
        "no_invented_numerics": check_no_invented_numerics(),
        "pin_untouched": check_pin_untouched(),
        "stage_membership_matches_scaffold": check_stage_membership_matches_scaffold(),
        "no_illicit_clearance": check_no_illicit_clearance(),
        "validation_plan": check_validation_plan(),
        "memory_map_status": check_memory_map_status(),
        "classification": check_classification(),
        "obstruction_analysis": check_obstruction_analysis(),
    }
