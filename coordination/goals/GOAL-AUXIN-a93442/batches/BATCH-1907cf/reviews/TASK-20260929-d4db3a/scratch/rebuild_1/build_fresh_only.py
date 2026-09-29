#!/usr/bin/env python3
"""Build EXP-AUXIN-92dccc draft-contract.yaml: fresh meta + protocol_normative, zero transclusion."""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import yaml

ROOT = Path('/workspace')
DESIGN = Path(__file__).resolve().parent
TYPED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"
NARROW = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml"
GATED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
FRESH = Path('/workspace/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/reviews/TASK-20260929-d4db3a/scratch/rebuild_1/fresh-text.yaml')
OUT = Path('/workspace/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/reviews/TASK-20260929-d4db3a/scratch/rebuild_1/draft-contract.yaml')


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def deep_merge(base: dict, overlay: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def walk_strings(obj, fn):
    if isinstance(obj, dict):
        return {k: walk_strings(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk_strings(x, fn) for x in obj]
    if isinstance(obj, str):
        return fn(obj)
    return obj


def rewrite_protocol_text(s: str) -> str:
    s = s.replace("experiments/EXP-AUXIN-7e2e3d/implementation/", "experiments/EXP-AUXIN-92dccc/implementation/")
    # Remap bare implementation/typed/ only when not already under 92dccc
    s = re.sub(
        r"(?<![\w/])implementation/typed/",
        "experiments/EXP-AUXIN-92dccc/implementation/typed/",
        s,
    )
    s = re.sub(
        r"(experiments/EXP-AUXIN-92dccc/)+",
        "experiments/EXP-AUXIN-92dccc/",
        s,
    )
    s = re.sub(
        r"Launch with a dirty implementation/typed/ or dirty amendment path, or on implementation bytes",
        "Launch with a dirty implementation tree under experiments/EXP-AUXIN-92dccc/implementation/typed/, or on implementation bytes that differ from the implementation snapshot",
        s,
    )
    s = re.sub(
        r"Launch with a dirty experiments/EXP-AUXIN-92dccc/implementation/typed/ or dirty amendment path, or on implementation bytes",
        "Launch with a dirty implementation tree under experiments/EXP-AUXIN-92dccc/implementation/typed/, or on implementation bytes that differ from the implementation snapshot",
        s,
    )
    s = re.sub(
        r"Any edit of this file, of specification\.yaml, of AMD-20260916-bands\.yaml or of AMD-20260923-d1d10\.yaml after approval",
        "Any edit of this contract file after approval",
        s,
    )
    s = re.sub(r"[Gg]overning-text hash(?:es)? mismatch", "successor_contract_sha256 mismatch", s)
    s = re.sub(r"successor_contract_sha256(?:es)?", "successor_contract_sha256", s)
    s = re.sub(r"governing_text_table", "protocol_normative section index", s)
    s = re.sub(r"four governing layers?", "this contract file alone", s)
    s = re.sub(r"four-layer stack", "single-contract custody model", s)
    s = re.sub(r"all four governing layers?", "this contract file", s)
    s = re.sub(r"Pre-registration of every cut-off rests on the sha256 binding of all four governing layers before any value is seen \(change\.D8_custody and custody_additions below\), not on the index\.", "Pre-registration of every cut-off rests on successor_contract_sha256 binding at launch, not on the index.", s)
    s = re.sub(
        r"completeness_claims_over_four_layers:.*",
        "completeness_claims_over_four_layers: After this contract, no field claims a complete threshold index across external layers; the index is non-normative per F-INDEX.",
        s,
    )
    s = re.sub(r"the held text", "this contract's stated rule", s)
    s = re.sub(r"\bheld text\b", "prior-record wording", s, flags=re.I)
    s = re.sub(r"amendment\.<path>", "successor contract path (provenance only)", s)
    s = re.sub(
        r"licenses a later amendment revision route",
        "does not apply; F-REV is the only revision route",
        s,
    )
    return s


def extract_protocol(amendment: dict) -> dict:
    a = amendment.get("amendment", amendment)
    keys = [
        "definitions",
        "change",
        "conventions",
        "tools_and_admission",
        "stages",
        "controls",
        "controls_distinctness",
        "what_the_controls_exercise",
        "null_arm",
        "preregistered_prediction",
        "metrics",
        "budget",
        "stopping_rules",
        "invalidation_rules",
        "required_artifacts",
        "success_criterion",
        "falsification_criterion",
        "interpretation_limits",
        "proof_search_map",
    ]
    return {k: a[k] for k in keys if k in a}


def patch_protocol(protocol: dict) -> None:
    """Surgical fixes for EJ6/EJ8 surfaces after bulk rewrite."""
    d8 = (protocol.get("change") or {}).get("D8_custody")
    if isinstance(d8, dict):
        d8["trial_plan"] = (
            "trial-plan.json under experiments/EXP-AUXIN-92dccc/implementation/typed/ "
            "records successor_contract_sha256 only. The run recomputes it at launch "
            "and at every stage boundary; mismatch is evidence-integrity failure."
        )
        d8["manifest"] = (
            "manifest.yaml records dirty_summary, launch commit, implementation snapshot "
            "task and commit, successor_contract_sha256, tool versions, third-party "
            "distributions and the inference block. Launch is refused if dirty_summary "
            "lists this contract file or any path under "
            "experiments/EXP-AUXIN-92dccc/implementation/typed/."
        )
        for key in ("import_rule", "implementation_snapshot_and_launch_comparison", "snapshot"):
            if key in d8 and isinstance(d8[key], str):
                d8[key] = rewrite_protocol_text(d8[key])
    d10 = (protocol.get("change") or {}).get("D10_additivity")
    if isinstance(d10, dict) and "rule" in d10:
        d10["rule"] = (
            "This contract is never rewritten in place. Any change is a new successor "
            "contract under a new EXP id per F-REV. The run uses NEW modules under "
            "experiments/EXP-AUXIN-92dccc/implementation/typed/ and edits no "
            "implementation file of any other experiment."
        )
    ta = protocol.get("tools_and_admission") or {}
    gate = ta.get("admission_gate")
    if isinstance(gate, str):
        gate = rewrite_protocol_text(gate)
        gate = gate.replace(
            "(7) The four successor_contract_sha256 match trial-plan.json.",
            "(7) successor_contract_sha256 in trial-plan.json matches this contract file at launch.",
        )
        gate = gate.replace(
            "(7) The four governing-text hashes match trial-plan.json.",
            "(7) successor_contract_sha256 in trial-plan.json matches this contract file at launch.",
        )
        ta["admission_gate"] = gate
    if isinstance(protocol.get("required_artifacts"), list):
        protocol["required_artifacts"] = [
            rewrite_protocol_text(x)
            .replace("governing-text hashes", "successor_contract_sha256")
            .replace("four governing-text hashes", "successor_contract_sha256")
            if isinstance(x, str)
            else x
            for x in protocol["required_artifacts"]
        ]
    for overlay in protocol.get("corrective_overlays") or []:
        if not isinstance(overlay, dict):
            continue
        ti = overlay.get("threshold_index") or {}
        if "completeness_claims_over_four_layers" in ti:
            ti["completeness_claims_over_four_layers"] = (
                "No governing field of this contract claims a complete threshold index; "
                "F-INDEX makes the index non-normative."
            )
        if "status_of_the_index" in ti and isinstance(ti["status_of_the_index"], str):
            ti["status_of_the_index"] = rewrite_protocol_text(ti["status_of_the_index"])
    fcm = protocol.get("falsification_condition_mapping") or {}
    if fcm:
        protocol["falsification_condition_mapping"] = walk_strings(
            fcm,
            lambda t: t.replace("the held text", "this contract's stated rule")
            if isinstance(t, str)
            else t,
        )
    ta = protocol.get("tools_and_admission") or {}
    if isinstance(ta.get("absence_rule"), str):
        ta["provisioning_precondition"] = ta["absence_rule"]


def build_execution_admission() -> dict:
    return {
        "currently_admitted": False,
        "requirements": [
            "Verified snapshot archive of EXP-AUXIN-92dccc contract file and H-AUXIN-6db354 binding on a published branch or PR; archive names this experiment id only.",
            "Implementation under experiments/EXP-AUXIN-92dccc/implementation/typed/ with two independent arithmetic paths that do not share factorization code.",
            "trial-plan.json naming successor_contract_sha256 and Stage artifact paths.",
            "Fresh Executor claim via tools/goal_lanes.py before launch.",
        ],
        "explicitly_not_required": [
            "Verified snapshot archive of EXP-AUXIN-7e2e3d approval chain.",
            "Clean or dirty status of any EXP-AUXIN-7e2e3d amendment file.",
            "Predecessor governing-text hashes of the held four-layer stack.",
        ],
    }


def build_falsification_mapping(narrow: dict, gated: dict) -> dict:
    n = narrow.get("amendment", narrow)
    g = gated.get("amendment", gated)
    mapping = n.get("corrective", {}).get("falsification_condition_mapping", {})
    fc6 = n.get("corrective", {}).get("falsification_condition_mapping_fc6")
    if fc6 is None:
        fc6 = g.get("corrective", {}).get("falsification_condition_mapping_fc6")
    return {"FC1_to_FC5": mapping, "FC6": fc6}


def collect_self_reference_phrases(text: str) -> set[str]:
    patterns = [
        r"\bthis contract\b",
        r"\bthis file\b",
        r"\bthis experiment\b",
        r"\bthis specification\b",
        r"\bthis protocol\b",
        r"\bthis frozen contract\b",
        r"\bthe frozen contract\b",
        r"\bthis amendment\b",
        r"\bthese controls\b",
        r"\bthis text\b",
    ]
    found = set()
    low = text.lower()
    for p in patterns:
        if re.search(p, low, re.I):
            found.add(re.search(p, text, re.I).group(0).lower())
    return found


def build_self_reference_table(contract_yaml: str) -> list[dict]:
    phrases = sorted(collect_self_reference_phrases(contract_yaml))
    table = []
    for ph in phrases:
        rule = "R1"
        if ph in ("this amendment",):
            rule = "R1"
        table.append({"phrase": ph, "rule_id": rule, "closed": True})
    table.append(
        {
            "phrase": "_closure_",
            "rule_id": "R4",
            "text": "Every self-referential phrase in protocol_normative and fresh fields appears above with exactly one rule. Unlisted phrase is a draft defect.",
        }
    )
    return table


def main() -> None:
    fresh = load_yaml(FRESH)["fresh"]
    typed = load_yaml(TYPED)
    narrow = load_yaml(NARROW)
    gated = load_yaml(GATED)

    protocol = extract_protocol(typed)
    protocol = walk_strings(protocol, rewrite_protocol_text)
    patch_protocol(protocol)

    # Narrow + gated corrective overlays (fresh text_kind)
    for src in (narrow, gated):
        a = src.get("amendment", src)
        corr = a.get("corrective")
        if corr:
            protocol.setdefault("corrective_overlays", []).append(
                walk_strings(corr, rewrite_protocol_text)
            )
    patch_protocol(protocol)

    protocol["execution_admission"] = build_execution_admission()
    protocol["falsification_condition_mapping"] = walk_strings(
        build_falsification_mapping(narrow, gated),
        lambda t: t.replace("the held text", "this contract's stated rule")
        if isinstance(t, str)
        else t,
    )
    patch_protocol(protocol)
    ch = protocol.get("change") or {}
    if isinstance(ch.get("D8_custody"), dict):
        ch["D8_custody"]["trial_plan"] = (
            "trial-plan.json under experiments/EXP-AUXIN-92dccc/implementation/typed/ "
            "records successor_contract_sha256 only. The run recomputes it at launch "
            "and at every stage boundary; mismatch is evidence-integrity failure."
        )
    protocol["text_kind"] = "fresh"
    protocol["semantic_lineage"] = {
        "note": "Normative content restated from held amendments as fresh text in this file only. Not transcluded. Not read from held paths at run time.",
        "provenance_only_sources": [
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
        ],
    }

    # Ensure stop/escalate tension resolved in stopping_rules list
    if isinstance(protocol.get("stopping_rules"), list):
        protocol["stopping_rules"] = [
            rewrite_protocol_text(x) if isinstance(x, str) else x for x in protocol["stopping_rules"]
        ]
        protocol["stopping_rules"].append(
            "Outcome hierarchy: evidence-integrity stops and admission failures precede instrument falsification outcomes (N1, N2, N3, N4). There is no stop-and-escalate on deployed-row exponents. After Stage C passes, null-arm and deployed rows run to completion unless a validity rule fires."
        )

    successor = {
        "successor_contract": {
            "fresh": fresh,
            "protocol_normative": protocol,
            "transcluded": {"entries": []},
            "additions_read_together": {"text_kind": "fresh", "groups": []},
            "leaf_map": {"text_kind": "fresh", "note": "Empty. No transcluded leaves.", "rows": []},
        }
    }

    body = yaml.dump(successor, sort_keys=False, allow_unicode=True, width=1000)
    phrases_table = build_self_reference_table(body)
    successor["successor_contract"]["self_reference_table"] = {
        "text_kind": "fresh",
        "order_matches_F_READ": True,
        "rows": phrases_table,
    }
    body = yaml.dump(successor, sort_keys=False, allow_unicode=True, width=1000)
    OUT.write_text(
        "# GENERATED by build_fresh_only.py — status draft, approved_by null.\n"
        "# Zero transclusion. Do not edit by hand; edit fresh-text.yaml or builder.\n"
        + body
    )
    print("wrote", OUT, "sha256", hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
