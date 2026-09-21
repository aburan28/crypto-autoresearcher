from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# --- Canonical protocol constants (protocol_spec.md FC0-PEAKBYTE-TOY-PROTOCOL-R1)
# These are the SOURCE OF TRUTH the harness holds independently of the ledger,
# so a ledger that disagrees (invented / out-of-protocol values) is rejected.
# Toy unit weights in protocol_slot_bytes. NOT real widths, NOT security bits.
CANONICAL_SLOT_WIDTHS: Dict[str, int] = {"W": 8, "R": 4, "B": 2, "M": 16, "T": 1}

# Verbatim from BATCH-023 peak_live_set_accounting.yaml -> stage_live_sets.
CANONICAL_STAGE_MEMBERSHIP: Dict[str, List[str]] = {
    "preparation": ["B_input", "B_attempt", "W_label", "R_label"],
    "sieve_attempt": ["B_input", "B_attempt", "W_sieve", "R_sieve", "B_sieve"],
    "recovery": ["B_input", "B_attempt", "B_post", "B_recovery", "accepted_transcript"],
    "tail_verification": ["B_input", "B_attempt", "B_recovery", "M_tail", "B_candidate"],
}

# Explicit enumeration (protocol_spec.md §2); no fuzzy prefix guessing.
CANONICAL_SLOT_CLASS_MAP: Dict[str, str] = {
    "B_input": "B", "B_attempt": "B", "B_sieve": "B", "B_post": "B",
    "B_recovery": "B", "B_candidate": "B",
    "W_label": "W", "W_sieve": "W",
    "R_label": "R", "R_sieve": "R",
    "M_tail": "M",
    "accepted_transcript": "T",
}

EXPECTED_BOUND_UNITS = "protocol_slot_bytes"
EXPECTED_OPERATOR_ID = "max_over_stages_of_sum_of_live_member_slot_widths"
EXPECTED_STATUS_AFTER = "numeric_composition_operator_protocol_toy_partial"
EXPECTED_PRIOR_STATUS = "composition_aggregation_schema_partial"
EXPECTED_DISPOSITION = "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED"
EXPECTED_SCALE_LABEL = "protocol_toy_scaffold_scale"

BATCH023_RELPATH = (
    "coordination/goals/GOAL-SSI-001/batches/BATCH-023/tasks/"
    "TASK-20260730-063/peak_live_set_accounting.yaml"
)

# Numeric leaves are permitted ONLY with this provenance. Anything else is an
# invented / out-of-protocol number and is rejected.
_ALLOWED_NUMERIC_LEAF_KEYS = frozenset({"maximum_runs", "runs_attempted"})
_ALLOWED_NUMERIC_PARENT_KEYS = frozenset({"slot_width_table", "stage_byte_loads"})
_ALLOWED_VALUE_PARENTS = frozenset({"peak_byte_bound", "mistaken_sum_across_stages"})

# Flags that must never be True.
_FORBIDDEN_TRUE_KEYS = frozenset({
    "query_memory_cleared", "query_memory_clearance", "clearance", "pin_complete",
    "breakthrough_claim", "completion_claim", "numeric_security_claim",
    "invent_tau", "tau_invented", "invent_numeric_values", "invent_security_bits",
    "invent_probabilities", "cryptographic_scale", "gate_B_taken",
    "controlled_null_fatigue", "batch022_scaffold_modified",
    "collimation_sieve_apis_invented", "batch014_equated",
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


def load_ledger() -> Dict[str, Any]:
    return load_yaml("instantiation_ledger.yaml")["instantiation_ledger"]


# --- Protocol recomputation --------------------------------------------------

def compute_expected(
    widths: Optional[Dict[str, int]] = None,
    membership: Optional[Dict[str, List[str]]] = None,
    class_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    widths = widths or CANONICAL_SLOT_WIDTHS
    membership = membership or CANONICAL_STAGE_MEMBERSHIP
    class_map = class_map or CANONICAL_SLOT_CLASS_MAP
    loads: Dict[str, int] = {}
    for stage, members in membership.items():
        loads[stage] = sum(widths[class_map[m]] for m in members)
    peak_stage = max(loads, key=lambda s: loads[s])
    return {
        "stage_byte_loads": loads,
        "peak_byte_bound": loads[peak_stage],
        "peak_stage": peak_stage,
        "mistaken_sum": sum(loads.values()),
    }


# --- Checks (each accepts an optional ledger dict for mutation testing) -------

def check_composition_numerics(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    led = led if led is not None else load_ledger()
    problems: List[str] = []

    op = led.get("composition_operator", {})
    if op.get("id") != EXPECTED_OPERATOR_ID:
        problems.append("composition_operator.id mismatch")
    if op.get("bound_units") != EXPECTED_BOUND_UNITS:
        problems.append("composition_operator.bound_units mismatch")
    if op.get("invented") is not False:
        problems.append("composition_operator.invented not False")

    widths = led.get("slot_width_table", {})
    if widths != CANONICAL_SLOT_WIDTHS:
        problems.append("slot_width_table does not match canonical protocol widths")

    class_map = led.get("slot_class_map", {})
    if class_map != CANONICAL_SLOT_CLASS_MAP:
        problems.append("slot_class_map does not match canonical protocol map")

    membership = led.get("stage_membership", {})
    if membership != CANONICAL_STAGE_MEMBERSHIP:
        problems.append("stage_membership does not match BATCH-023 verbatim membership")

    # Recompute from the ledger's OWN declared widths/membership/map, but only if
    # they are structurally usable; guard against unknown members/classes.
    exp = None
    try:
        exp = compute_expected(widths, membership, class_map)
    except (KeyError, TypeError):
        problems.append("out-of-protocol member or slot class prevents recomputation")

    if exp is not None:
        if led.get("stage_byte_loads") != exp["stage_byte_loads"]:
            problems.append("stage_byte_loads disagree with recomputation")
        pbb = led.get("peak_byte_bound", {})
        if pbb.get("value") != exp["peak_byte_bound"]:
            problems.append("peak_byte_bound.value disagrees with recomputation")
        if pbb.get("peak_stage") != exp["peak_stage"]:
            problems.append("peak_byte_bound.peak_stage disagrees with recomputation")
        if pbb.get("units") != EXPECTED_BOUND_UNITS:
            problems.append("peak_byte_bound.units mismatch")
        msum = led.get("mistaken_sum_across_stages", {})
        if msum.get("value") != exp["mistaken_sum"]:
            problems.append("mistaken_sum_across_stages.value disagrees with recomputation")
        if msum.get("rejected_as_peak") is not True:
            problems.append("mistaken_sum not rejected_as_peak")
        if not (isinstance(msum.get("value"), int) and msum.get("value") > exp["peak_byte_bound"]):
            problems.append("mistaken sum not strictly greater than peak")

    return {"passed": not problems, "problems": problems,
            "recomputed": exp if exp else {}}


def check_key_sets(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """slot_width_table and stage_byte_loads must carry EXACTLY the protocol keys.

    Prevents an invented numeric being smuggled under an allowed container key.
    """
    led = led if led is not None else load_ledger()
    problems: List[str] = []
    if set(led.get("slot_width_table", {}).keys()) != set(CANONICAL_SLOT_WIDTHS.keys()):
        problems.append("slot_width_table has unexpected/missing keys")
    if set(led.get("stage_byte_loads", {}).keys()) != set(CANONICAL_STAGE_MEMBERSHIP.keys()):
        problems.append("stage_byte_loads has unexpected/missing keys")
    return {"passed": not problems, "problems": problems}


def _walk_numeric(node: Any, chain: List[str], hits: List[Dict[str, Any]]) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        leaf = chain[-1] if chain else None
        parent = chain[-2] if len(chain) >= 2 else None
        allowed = (
            leaf in _ALLOWED_NUMERIC_LEAF_KEYS
            or parent in _ALLOWED_NUMERIC_PARENT_KEYS
            or (leaf == "value" and parent in _ALLOWED_VALUE_PARENTS)
        )
        if not allowed:
            hits.append({"path": ".".join(chain), "key": leaf, "value": node})
        return
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_numeric(v, chain + [str(k)], hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_numeric(v, chain + [f"[{i}]"], hits)


def check_no_invented_numerics(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    led = led if led is not None else load_ledger()
    hits: List[Dict[str, Any]] = []
    _walk_numeric(led, [], hits)
    return {"passed": not hits, "hits": hits}


def _walk_forbidden_true(node: Any, chain: List[str], hits: List[Dict[str, Any]]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k in _FORBIDDEN_TRUE_KEYS and v is True:
                hits.append({"path": ".".join(chain + [str(k)]), "key": k})
            _walk_forbidden_true(v, chain + [str(k)], hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_forbidden_true(v, chain + [f"[{i}]"], hits)


def check_no_illicit_clearance(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    led = led if led is not None else load_ledger()
    hits: List[Dict[str, Any]] = []
    _walk_forbidden_true(led, [], hits)
    problems: List[str] = []
    if led.get("query_memory_clearance") is not False:
        problems.append("query_memory_clearance must be False")
    if led.get("cryptographic_scale") is not False:
        problems.append("cryptographic_scale must be False")
    if led.get("scale_label") != EXPECTED_SCALE_LABEL:
        problems.append("scale_label must be protocol_toy_scaffold_scale")
    summ = led.get("summary", {})
    if summ.get("disposition") != EXPECTED_DISPOSITION:
        problems.append("disposition must remain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED")
    if summ.get("query_memory_cleared") is not False:
        problems.append("summary.query_memory_cleared must be False")
    return {"passed": not hits and not problems, "forbidden_true_hits": hits,
            "problems": problems}


def check_gate_and_status(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    led = led if led is not None else load_ledger()
    problems: List[str] = []
    if led.get("gate_chosen") != "A":
        problems.append("gate_chosen must be A")
    if led.get("gate_B_taken") is not False:
        problems.append("gate_B_taken must be False (exactly one gate)")
    if led.get("controlled_null_fatigue") is not False:
        problems.append("controlled_null_fatigue must be False for a non-null instantiation")
    summ = led.get("summary", {})
    if summ.get("instantiation_status") != EXPECTED_STATUS_AFTER:
        problems.append("summary.instantiation_status mismatch")
    if summ.get("prior_status") != EXPECTED_PRIOR_STATUS:
        problems.append("summary.prior_status mismatch")
    if summ.get("has_nonnull_protocol_derived_numeric") is not True:
        problems.append("summary.has_nonnull_protocol_derived_numeric must be True")
    ni = led.get("numeric_instantiation", {})
    for k in ("composition_operator_instantiated", "bound_units_instantiated",
              "numeric_width_instantiated", "peak_byte_accounting_instantiated"):
        if ni.get(k) is not True:
            problems.append(f"numeric_instantiation.{k} must be True")
    return {"passed": not problems, "problems": problems}


def check_qm_stopping_retained(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    led = led if led is not None else load_ledger()
    problems: List[str] = []
    nc = led.get("qm_stopping_negative_control", {})
    if nc.get("control_result") != "FAIL":
        problems.append("qm_stopping control_result must remain FAIL")
    if nc.get("tau_invented") is not False:
        problems.append("tau must not be invented (gate A)")
    if nc.get("joint_finiteness_established") is not False:
        problems.append("joint finiteness must not be claimed (gate A)")
    if led.get("summary", {}).get("control_result") != "FAIL":
        problems.append("summary.control_result must remain FAIL")
    lr = led.get("lineage_retained", {})
    if lr.get("batch020_pin_status") != "no_admissible_pin":
        problems.append("BATCH-020 no_admissible_pin must be retained")
    if lr.get("qm_error_status") != "f_union_ledger_partial":
        problems.append("QM-ERROR f_union_ledger_partial must be retained")
    return {"passed": not problems, "problems": problems}


def _find_repo_file(relpath: str) -> Optional[Path]:
    for ancestor in [task_dir(), *task_dir().parents]:
        candidate = ancestor / relpath
        if candidate.exists():
            return candidate
    return None


def check_cross_batch023(led: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Best-effort: confirm the ledger membership equals BATCH-023 on disk."""
    led = led if led is not None else load_ledger()
    src = _find_repo_file(BATCH023_RELPATH)
    if src is None:
        return {"passed": True, "found": False, "note": "BATCH-023 file not located; skipped"}
    data = yaml.safe_load(src.read_text())["peak_live_set_accounting"]["stage_live_sets"]
    disk = {stage: list(v["members"]) for stage, v in data.items()}
    matches = disk == CANONICAL_STAGE_MEMBERSHIP == led.get("stage_membership")
    return {"passed": matches, "found": True, "membership_matches": matches}


# --- Sibling status files ----------------------------------------------------

def check_memory_map_status() -> Dict[str, Any]:
    qm = load_yaml("memory_map_status.yaml")["memory_map_status"]["qm_memory_map"]
    passed = (
        qm.get("prior_status") == EXPECTED_PRIOR_STATUS
        and qm.get("status_after_batch") == EXPECTED_STATUS_AFTER
        and qm.get("clearance") is False
        and qm.get("query_memory_cleared") is False
        and qm.get("cryptographic_scale") is False
    )
    return {"passed": passed, "status_after_batch": qm.get("status_after_batch")}


def check_classification() -> Dict[str, Any]:
    data = load_yaml("classification.yaml")["classification"]
    passed = (
        data.get("disposition") == EXPECTED_DISPOSITION
        and data.get("control_result") == "FAIL"
        and data.get("gate_chosen") == "A"
        and data.get("cryptographic_scale") is False
        and data.get("non_extrapolation") is True
        and data.get("qm_statuses", {}).get("QM_MEMORY_MAP") == EXPECTED_STATUS_AFTER
        and data.get("qm_statuses", {}).get("QM_STOPPING") == "remains_open_FAIL"
    )
    return {"passed": passed, "disposition": data.get("disposition")}


def check_mutation_status() -> Dict[str, Any]:
    data = load_yaml("mutation_status.yaml")["mutation_status"]
    passed = (
        data["QM_MEMORY_MAP"]["status_after_batch"] == EXPECTED_STATUS_AFTER
        and data["QM_STOPPING"]["control_result"] == "FAIL"
        and data["QUERY_MEMORY"]["cleared"] is False
        and data["batch020_pin_status_retained"] == "no_admissible_pin"
    )
    return {"passed": passed}


def run_all_checks() -> Dict[str, Any]:
    return {
        "composition_numerics": check_composition_numerics(),
        "key_sets": check_key_sets(),
        "no_invented_numerics": check_no_invented_numerics(),
        "no_illicit_clearance": check_no_illicit_clearance(),
        "gate_and_status": check_gate_and_status(),
        "qm_stopping_retained": check_qm_stopping_retained(),
        "cross_batch023": check_cross_batch023(),
        "memory_map_status": check_memory_map_status(),
        "classification": check_classification(),
        "mutation_status": check_mutation_status(),
    }
