"""BATCH-042 QM-ERROR F-union obligation ledger harness checks.

Adversarial guards for the claimed outcome ``f_union_tightened``. The harness
must FAIL on: illicit clearance, invented probabilities / numeric error bounds /
security bits / τ, relabel-only overclaim, host-level exhaustiveness smuggling,
QM-STOPPING reopen, MEMORY-MAP advance, gate-B, CollimationSieve API invention,
and disposition drift.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

TASK_DIR = Path(__file__).resolve().parents[1]

ALLOWED_STATUSES = {
    "wired_symbolic",
    "checklist_only",
    "not_instantiated",
    "not_supported",
    "deferred",
    "tightened_from_committed_structure",
}

# Keys that must never be True anywhere in the package.
ILLICIT_CLEARANCE_KEYS = {
    "query_memory_cleared",
    "qm_error_cleared",
    "qm_stopping_cleared",
    "qm_memory_map_cleared",
    "qm_stopping_reopened",
    "reopened_this_batch",
    "cleared",
    "clearance",
    "breakthrough",
    "completion",
    "pin_complete",
    "not_pin_complete",  # only a label; must remain a list entry, never a True flag
    "numeric_security_bits",
    "security_bits",
    "tau_invented",
    "joint_finiteness_established",
    "probabilities_invented",
    "numeric_error_bounds_invented",
    "security_bits_invented",
    "gate_b_taken",
    "collimation_sieve_apis_invented",
    "batch014_equated",
    "batch022_scaffold_modified",
    "toy_peak_byte_lane_iterated",
    "exp_ssi_001_launched",
    "is_relabel_only",
    "probability_assigned",
    "probability_composition",
    "crypto_verify_body",
    "crypto_body",
    "host_level_exhaustiveness_cleared",
    "is_closure_claim",
    "qm_stopping_reopened_this_batch",
}

# Numeric-invention detector: these key fragments must not carry a real number.
NUMERIC_INVENTION_FRAGMENTS = ("probabilit", "epsilon", "security_bit", "pr_f", "tau_value")


def _load(name: str) -> Any:
    return yaml.safe_load((TASK_DIR / name).read_text())


def load_ledger():
    return _load("f_union_obligation_ledger.yaml")


def load_criteria():
    return _load("falsifiable_criteria.yaml")


def load_classification():
    return _load("classification.yaml")


def load_memory_map():
    return _load("memory_map_status.yaml")


def load_md() -> str:
    return (TASK_DIR / "qm_error_advancement.md").read_text()


# --------------------------------------------------------------------------
# Positive structural checks
# --------------------------------------------------------------------------
def check_criteria_pre_registered(c=None) -> dict:
    c = c or load_criteria()
    fc = c["falsifiable_criteria"]
    problems = []
    if not fc.get("registered_before_claim"):
        problems.append("registered_before_claim must be true")
    outcomes = fc.get("outcomes") or {}
    for key in ("f_union_tightened", "qm_error_pause_revisit", "pin_seeking_without_api_invention"):
        if key not in outcomes:
            problems.append(f"missing outcome {key}")
            continue
        if not outcomes[key].get("requires_all"):
            problems.append(f"{key}.requires_all empty")
        if not outcomes[key].get("falsified_if"):
            problems.append(f"{key}.falsified_if empty")
    if fc.get("selected_outcome") != "f_union_tightened":
        problems.append("selected_outcome must be f_union_tightened")
    return {"passed": not problems, "problems": problems}


def check_obligation_ledger(led=None) -> dict:
    led = led or load_ledger()
    ob = led["f_union_obligation_ledger"]
    problems = []
    if ob.get("outcome") != "f_union_tightened":
        problems.append(f"expected f_union_tightened, got {ob.get('outcome')}")
    obligations = ob.get("obligations") or []
    if len(obligations) < 7:
        problems.append("need >=7 obligations decomposing the gap")
    tightened = []
    for o in obligations:
        st = o.get("status")
        if st not in ALLOWED_STATUSES:
            problems.append(f"{o.get('id')} status {st!r} not in allowed vocabulary")
        if not o.get("citations"):
            problems.append(f"{o.get('id')} has no citations")
        if o.get("probability_assigned") is True:
            problems.append(f"{o.get('id')} assigns a probability")
        if st == "tightened_from_committed_structure" and o.get("tightened_this_batch") is True:
            tightened.append(o.get("id"))
        if st in {"not_supported", "not_instantiated"} and not o.get("revisit_ref"):
            problems.append(f"{o.get('id')} blocked but has no revisit_ref")
    declared = ob.get("tightened_this_batch") or []
    if len(tightened) != 1:
        problems.append(f"exactly one obligation must be tightened this batch, found {tightened}")
    if sorted(declared) != sorted(tightened):
        problems.append(f"declared tightened_this_batch {declared} != actual {tightened}")
    # revisit conditions concrete and unmet
    revs = ob.get("revisit_conditions") or []
    ids = {r.get("id") for r in revs}
    if not {"REV-E1", "REV-E2", "REV-E3"} <= ids:
        problems.append("REV-E1/REV-E2/REV-E3 required as concrete revisit conditions")
    if any(r.get("currently_met") is True for r in revs):
        problems.append("no revisit condition may already be met")
    # summary honesty
    summ = ob.get("summary") or {}
    for key in ("qm_error_cleared", "query_memory_cleared", "qm_stopping_cleared",
                "qm_stopping_reopened", "probabilities_invented", "tau_invented"):
        if summ.get(key) is True:
            problems.append(f"summary.{key} must not be true")
    return {"passed": not problems, "problems": problems}


def check_md_machine_block(md: str | None = None) -> dict:
    md = md if md is not None else load_md()
    problems = []
    blocks = re.findall(r"```yaml\n(.*?)```", md, re.S)
    if not blocks:
        return {"passed": False, "problems": ["missing machine-readable yaml block"]}
    block = yaml.safe_load(blocks[-1])
    expected = {
        "QM_ERROR_OUTCOME": "f_union_tightened",
        "tightened_obligation": "OBL-2a",
        "host_level_exhaustiveness": "not_supported",
        "qm_error_cleared": False,
        "query_memory_cleared": False,
        "qm_stopping_reopened": False,
        "probability_composition": False,
        "crypto_verify_body": False,
        "tau_invented": False,
        "is_relabel_only": False,
        "disposition": "FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED",
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
    if c.get("cryptographic_scale") is not False:
        problems.append("cryptographic_scale must be false")
    if c.get("execution_package", {}).get("curve_isogeny_quantum_circuit_compute") is not False:
        problems.append("compute must be false")
    qm = c.get("qm_statuses") or {}
    if qm.get("QM_MEMORY_MAP") != "numeric_composition_operator_protocol_toy_partial":
        problems.append("MEMORY-MAP must be retained")
    if "FAIL" not in str(qm.get("QM_STOPPING", "")):
        problems.append("QM_STOPPING must retain FAIL")
    if qm.get("QUERY_MEMORY") != "unreconciled":
        problems.append("QUERY_MEMORY must remain unreconciled")
    adv = c.get("qm_error_advancement") or {}
    if adv.get("outcome") != "f_union_tightened":
        problems.append("classification qm_error outcome mismatch")
    if adv.get("qm_error_cleared") is not False:
        problems.append("qm_error_cleared must be false")
    if adv.get("host_level_exhaustiveness") not in (None, "not_supported"):
        problems.append("host_level_exhaustiveness must be not_supported")
    if adv.get("is_relabel_only") is not False:
        problems.append("is_relabel_only must be false")
    return {"passed": not problems, "problems": problems}


def check_memory_map(mm=None) -> dict:
    mm = mm or load_memory_map()
    m = mm["memory_map_status"]
    problems = []
    if m["qm_memory_map"].get("advanced_this_batch") is not False:
        problems.append("MEMORY-MAP must not advance")
    if m["qm_stopping"].get("lane_status") != "paused_pending_revisit":
        problems.append("QM-STOPPING lane must remain paused_pending_revisit")
    if m["qm_stopping"].get("reopened_this_batch") is not False:
        problems.append("QM-STOPPING must not be reopened")
    if m["qm_stopping"].get("ninth_unverified_rerecord") is not False:
        problems.append("ninth unverified forbidden")
    if m["qm_error"].get("cleared") is not False:
        problems.append("qm_error cleared illicit")
    if m["qm_error"].get("host_level_exhaustiveness") not in (None, "not_supported"):
        problems.append("qm_error host_level_exhaustiveness must be not_supported")
    if m["query_memory"].get("cleared") is not False:
        problems.append("query_memory cleared illicit")
    if m.get("batch020_pin_status_retained") != "no_admissible_pin":
        problems.append("BATCH-020 pin status not retained")
    if m.get("collimation_sieve_apis_invented") is not False:
        problems.append("API invention flag")
    if m.get("gate_B_taken") is not False:
        problems.append("fake-τ gate B taken")
    if m.get("toy_peak_byte_lane_iterated") is not False:
        problems.append("toy peak-byte lane iterated")
    if m.get("exp_ssi_001_launched") is not False:
        problems.append("EXP-SSI-001 launched")
    return {"passed": not problems, "problems": problems}


def check_not_relabel_only(led=None, cl=None) -> dict:
    led = led or load_ledger()
    cl = cl or load_classification()
    ob = led["f_union_obligation_ledger"]
    problems = []
    if ob.get("prior_status", {}).get("reverse_inclusion_recorded") is not False:
        problems.append("prior reverse_inclusion_recorded must be false (else no new content)")
    obl2a = next((o for o in ob.get("obligations", []) if o.get("id") == "OBL-2a"), None)
    if obl2a is None:
        problems.append("OBL-2a missing")
    else:
        if not obl2a.get("derivation"):
            problems.append("OBL-2a needs a derivation (checkable new content)")
        if not obl2a.get("scope"):
            problems.append("OBL-2a needs an explicit scope")
        if not obl2a.get("what_this_is_not"):
            problems.append("OBL-2a must state what it is NOT")
    if cl["classification"].get("qm_error_advancement", {}).get("is_relabel_only") is not False:
        problems.append("classification is_relabel_only must be false")
    return {"passed": not problems, "problems": problems}


def check_no_host_level_exhaustiveness_claim(led=None) -> dict:
    led = led or load_ledger()
    ob = led["f_union_obligation_ledger"]
    problems = []
    obl2b = next((o for o in ob.get("obligations", []) if o.get("id") == "OBL-2b"), None)
    if obl2b is None:
        problems.append("OBL-2b (host-level exhaustiveness) must be present and blocked")
    elif obl2b.get("status") != "not_supported":
        problems.append(f"OBL-2b must be not_supported, got {obl2b.get('status')}")
    # OBL-2a scope must be spec-internal only
    obl2a = next((o for o in ob.get("obligations", []) if o.get("id") == "OBL-2a"), None)
    if obl2a and "host" in str(obl2a.get("scope", "")).lower():
        problems.append("OBL-2a scope must not be host-level")
    return {"passed": not problems, "problems": problems}


def _walk(obj: Any, path: str = ""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else str(k)
            yield p, str(k), v
            yield from _walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def _all_blobs() -> list[Any]:
    return [load_ledger(), load_classification(), load_memory_map(), load_criteria()]


def check_no_illicit_clearance(blobs=None) -> dict:
    blobs = blobs if blobs is not None else _all_blobs()
    hits = []
    for b in blobs:
        for p, key, val in _walk(b):
            lk = key.lower()
            if lk in ILLICIT_CLEARANCE_KEYS and val is True:
                hits.append(p)
    return {"passed": not hits, "hits": hits}


def check_no_invented_numerics(blobs=None) -> dict:
    blobs = blobs if blobs is not None else _all_blobs()
    hits = []
    for b in blobs:
        for p, key, val in _walk(b):
            lk = key.lower()
            if any(frag in lk for frag in NUMERIC_INVENTION_FRAGMENTS):
                if isinstance(val, bool):
                    continue
                if isinstance(val, (int, float)):
                    hits.append(f"{p}={val}")
    return {"passed": not hits, "hits": hits}


def _repo_root() -> Path:
    for cand in [TASK_DIR, *TASK_DIR.parents]:
        if (cand / "AGENTS.md").exists() and (cand / "ledger").is_dir():
            return cand
    raise RuntimeError(f"repo root not found from {TASK_DIR}")


def check_citations_exist(led=None) -> dict:
    led = led or load_ledger()
    root = _repo_root()
    missing = []
    for o in led["f_union_obligation_ledger"].get("obligations") or []:
        for cite in o.get("citations") or []:
            path = cite.split("#", 1)[0]
            if not (root / path).exists():
                missing.append(cite)
    return {"passed": not missing, "missing": missing}


def run_all_checks() -> dict:
    return {
        "criteria_pre_registered": check_criteria_pre_registered(),
        "obligation_ledger": check_obligation_ledger(),
        "md_machine_block": check_md_machine_block(),
        "classification": check_classification(),
        "memory_map": check_memory_map(),
        "not_relabel_only": check_not_relabel_only(),
        "no_host_level_exhaustiveness_claim": check_no_host_level_exhaustiveness_claim(),
        "no_illicit_clearance": check_no_illicit_clearance(),
        "no_invented_numerics": check_no_invented_numerics(),
        "citations_exist": check_citations_exist(),
    }
