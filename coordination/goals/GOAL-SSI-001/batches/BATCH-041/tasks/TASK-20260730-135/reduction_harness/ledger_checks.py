"""BATCH-041 host-independence reduction harness checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

TASK_DIR = Path(__file__).resolve().parents[1]
ILLICIT_CLEARANCE_KEYS = {
    "query_memory_cleared",
    "qm_stopping_cleared",
    "qm_memory_map_cleared",
    "cleared",
    "breakthrough",
    "completion",
    "pin_complete",
    "numeric_security_bits",
    "security_bits",
}
FORBIDDEN_TRUE_PATHS = [
    ("reduction_exists", True),
    ("dependence_essential_scoped", True),
    ("named_obstruction", True),
    ("meets_inventor_protocol_s4", True),
    ("is_closure_claim", True),
    ("ninth_unverified_rerecord", True),
    ("tau_invented", True),
    ("joint_finiteness_established", True),
]


def _load(name: str) -> Any:
    return yaml.safe_load((TASK_DIR / name).read_text())


def load_criteria():
    return _load("falsifiable_criteria.yaml")


def load_ledger():
    return _load("reduction_ledger.yaml")


def load_classification():
    return _load("classification.yaml")


def load_memory_map():
    return _load("memory_map_status.yaml")


def load_reduction_md() -> str:
    return (TASK_DIR / "host_independence_reduction.md").read_text()


def check_criteria_pre_registered(c=None) -> dict:
    c = c or load_criteria()
    fc = c["falsifiable_criteria"]
    problems = []
    if not fc.get("registered_before_claim"):
        problems.append("registered_before_claim must be true")
    outcomes = fc.get("outcomes") or {}
    for key in ("reduction_exists", "dependence_essential_scoped", "neither_pause"):
        if key not in outcomes:
            problems.append(f"missing outcome {key}")
        else:
            if not outcomes[key].get("requires_all"):
                problems.append(f"{key}.requires_all empty")
            if not outcomes[key].get("falsified_if"):
                problems.append(f"{key}.falsified_if empty")
    return {"passed": not problems, "problems": problems}


def check_ledger_outcome(led=None) -> dict:
    led = led or load_ledger()
    rl = led["reduction_ledger"]
    problems = []
    if rl.get("outcome") != "neither_pause":
        problems.append(f"expected neither_pause, got {rl.get('outcome')}")
    if rl.get("reduction_exists") is not False:
        problems.append("reduction_exists must be false")
    if rl.get("dependence_essential_scoped") is not False:
        problems.append("dependence_essential_scoped must be false")
    if rl.get("named_obstruction") is not False:
        problems.append("named_obstruction must be false")
    if rl.get("ninth_unverified_rerecord") is not False:
        problems.append("ninth_unverified_rerecord must be false")
    if rl.get("qm_stopping_lane") != "paused_pending_revisit":
        problems.append("qm_stopping_lane must be paused_pending_revisit")
    revs = rl.get("revisit_conditions") or []
    if len(revs) < 2:
        problems.append("need >=2 revisit conditions")
    ids = {r.get("id") for r in revs}
    if not {"REV-1", "REV-2"} <= ids:
        problems.append("REV-1 and REV-2 required")
    props = rl.get("candidate_properties_audited") or []
    if len(props) < 5:
        problems.append("need >=5 audited candidate properties")
    if any(p.get("discharges_outcome_R") for p in props):
        problems.append("no Prop may discharge OUTCOME-R in neither_pause")
    return {"passed": not problems, "problems": problems}


def check_md_machine_block(md: str | None = None) -> dict:
    md = md if md is not None else load_reduction_md()
    problems = []
    m = re.search(r"```yaml\n(.*?)```", md, re.S)
    if not m:
        return {"passed": False, "problems": ["missing machine-readable yaml block"]}
    block = yaml.safe_load(m.group(1))
    expected = {
        "REDUCTION_OUTCOME": "neither_pause",
        "reduction_exists": False,
        "dependence_essential_scoped": False,
        "named_obstruction": False,
        "ninth_unverified_rerecord": False,
        "qm_stopping_lane": "paused_pending_revisit",
        "tau_invented": False,
    }
    for k, v in expected.items():
        if block.get(k) != v:
            problems.append(f"md block {k}={block.get(k)!r} expected {v!r}")
    return {"passed": not problems, "problems": problems}


def check_classification(cl=None) -> dict:
    cl = cl or load_classification()
    c = cl["classification"]
    problems = []
    if c.get("disposition") != "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED":
        problems.append("disposition mismatch")
    if c.get("control_result") != "FAIL":
        problems.append("control_result must be FAIL")
    hir = c.get("host_independence_reduction") or {}
    if hir.get("outcome") != "neither_pause":
        problems.append("classification outcome mismatch")
    if c.get("cryptographic_scale") is not False:
        problems.append("cryptographic_scale must be false")
    if c.get("execution_package", {}).get("curve_isogeny_quantum_circuit_compute") is not False:
        problems.append("compute must be false")
    qm = c.get("qm_statuses") or {}
    if qm.get("QM_MEMORY_MAP") != "numeric_composition_operator_protocol_toy_partial":
        problems.append("MEMORY-MAP must be retained")
    if "FAIL" not in str(qm.get("QM_STOPPING", "")):
        problems.append("QM_STOPPING must retain FAIL")
    return {"passed": not problems, "problems": problems}


def check_memory_map(mm=None) -> dict:
    mm = mm or load_memory_map()
    m = mm["memory_map_status"]
    problems = []
    if m["qm_memory_map"].get("advanced_this_batch") is not False:
        problems.append("MEMORY-MAP must not advance")
    if m["qm_stopping"].get("lane_status") != "paused_pending_revisit":
        problems.append("lane_status mismatch")
    if m["qm_stopping"].get("ninth_unverified_rerecord") is not False:
        problems.append("ninth unverified forbidden")
    if m["query_memory"].get("cleared") is not False:
        problems.append("query_memory cleared illicit")
    if m.get("batch020_pin_status_retained") != "no_admissible_pin":
        problems.append("BATCH-020 pin status not retained")
    if m.get("collimation_sieve_apis_invented") is not False:
        problems.append("API invention flag")
    if m.get("gate_B_taken") is not False:
        problems.append("fake-τ gate B taken")
    return {"passed": not problems, "problems": problems}


def _walk_illicit(obj: Any, path: str = "") -> list[str]:
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            lk = str(k).lower()
            if lk in ILLICIT_CLEARANCE_KEYS and v is True:
                hits.append(p)
            if lk in {"clearance", "query_memory_cleared"} and v is True:
                hits.append(p)
            hits.extend(_walk_illicit(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(_walk_illicit(v, f"{path}[{i}]"))
    return hits


def check_no_illicit_clearance() -> dict:
    blobs = [
        load_ledger(),
        load_classification(),
        load_memory_map(),
        load_criteria(),
    ]
    hits = []
    for b in blobs:
        hits.extend(_walk_illicit(b))
    # allow explicit false clearance fields; only True is illicit
    return {"passed": not hits, "hits": hits}


def check_no_invented_closure_flags(led=None) -> dict:
    led = led or load_ledger()
    rl = led["reduction_ledger"]
    problems = []
    for key, bad in FORBIDDEN_TRUE_PATHS:
        if rl.get(key) is bad:
            problems.append(f"reduction_ledger.{key} must not be {bad}")
    return {"passed": not problems, "problems": problems}


def _repo_root() -> Path:
    # TASK_DIR = .../coordination/goals/GOAL-*/batches/BATCH-*/tasks/TASK-*
    for cand in [TASK_DIR, *TASK_DIR.parents]:
        if (cand / "AGENTS.md").exists() and (cand / "ledger").is_dir():
            return cand
    raise RuntimeError(f"repo root not found from {TASK_DIR}")


def check_citations_exist(led=None) -> dict:
    led = led or load_ledger()
    root = _repo_root()
    missing = []
    for prop in led["reduction_ledger"].get("candidate_properties_audited") or []:
        for cite in prop.get("citations") or []:
            path = cite.split("#", 1)[0]
            if not (root / path).exists():
                missing.append(cite)
    return {"passed": not missing, "missing": missing}


def run_all_checks() -> dict:
    return {
        "criteria_pre_registered": check_criteria_pre_registered(),
        "ledger_outcome": check_ledger_outcome(),
        "md_machine_block": check_md_machine_block(),
        "classification": check_classification(),
        "memory_map": check_memory_map(),
        "no_illicit_clearance": check_no_illicit_clearance(),
        "no_invented_closure_flags": check_no_invented_closure_flags(),
        "citations_exist": check_citations_exist(),
    }
