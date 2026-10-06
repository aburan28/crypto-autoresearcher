#!/usr/bin/env python3
"""EJ5: fresh replacements keep non-held run-time clauses; NC drops one manifest item."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
WRITE = Path(__file__).resolve().parent
DESIGN = (
    ROOT
    / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/design/TASK-20260929-1abb8c"
)
DRAFT = DESIGN / "draft-contract.yaml"
TYPED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"

# Non-hash manifest items that must survive in F-CUSTODY.manifest_rule
MANIFEST_ITEMS = [
    "dirty_summary",
    "launch commit",
    "implementation snapshot",
    "successor_contract_sha256",
    "tool versions",
    "third-party",
    "inference",
]


def walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk_strings(x)
    elif isinstance(obj, str):
        yield obj


def main() -> None:
    draft = yaml.safe_load(DRAFT.read_text())
    sc = draft["successor_contract"]
    fresh = sc["fresh"]
    pn = sc["protocol_normative"]
    typed = yaml.safe_load(TYPED.read_text())
    ta = typed.get("amendment", typed)
    typed_d8 = ((ta.get("change") or {}).get("D8_custody")) or {}

    custody = fresh.get("custody") or {}
    write = fresh.get("write_scope") or {}
    rev = fresh.get("revision_rule") or {}
    admission = pn.get("execution_admission") or {}
    d8 = ((pn.get("change") or {}).get("D8_custody")) or {}
    d10 = ((pn.get("change") or {}).get("D10_additivity")) or {}
    inv = pn.get("invalidation_rules") or []

    manifest_rule = custody.get("manifest_rule") or ""
    trial_plan_rule = custody.get("trial_plan_rule") or ""
    independence = custody.get("independence") or ""

    manifest_survival = {
        item: bool(re.search(re.escape(item), manifest_rule, re.I))
        for item in MANIFEST_ITEMS
    }
    # launch commit / implementation snapshot phrasing variants
    if not manifest_survival["launch commit"]:
        manifest_survival["launch commit"] = bool(
            re.search(r"launch commit", manifest_rule, re.I)
        )
    if not manifest_survival["implementation snapshot"]:
        manifest_survival["implementation snapshot"] = bool(
            re.search(r"implementation snapshot", manifest_rule, re.I)
        )
    if not manifest_survival["third-party"]:
        manifest_survival["third-party"] = bool(
            re.search(r"third.party", manifest_rule, re.I)
        )
    if not manifest_survival["inference"]:
        manifest_survival["inference"] = bool(
            re.search(r"inference", manifest_rule, re.I)
        )
    if not manifest_survival["tool versions"]:
        manifest_survival["tool versions"] = bool(
            re.search(r"tool versions", manifest_rule, re.I)
        )

    checks = {
        "manifest_non_hash_items": manifest_survival,
        "all_manifest_items_present": all(manifest_survival.values()),
        "trial_plan_recomputes_sha256": bool(
            re.search(r"recomput", trial_plan_rule, re.I)
            and re.search(r"successor_contract_sha256", trial_plan_rule)
        ),
        "dirty_refusal_scoped": bool(
            re.search(r"contract_file|implementation_tree", manifest_rule, re.I)
            and re.search(r"refuse", manifest_rule, re.I)
        ),
        "write_scope_confined_to_55c6c0": "EXP-AUXIN-55c6c0" in str(
            write.get("paths")
        ),
        "write_new_modules_no_edit_others": bool(
            re.search(r"new modules|edits no", write.get("implementation_modules", ""), re.I)
        ),
        "F_REV_only_revision": bool(
            re.search(r"only revision", rev.get("text", ""), re.I)
        ),
        "D10_cites_F_REV": bool(
            re.search(r"F-REV", str(d10.get("rule", "")))
        ),
        "admission_lists_explicitly_not_required": bool(
            admission.get("explicitly_not_required")
        ),
        "admission_not_currently_admitted": admission.get("currently_admitted") is False,
        "independence_stated": bool(
            re.search(r"No gate|does not depend|never opened", independence, re.I)
        ),
        "typed_d8_keys_in_proto": sorted(
            set(typed_d8.keys()) & set(d8.keys())
        ),
        "typed_d8_keys_missing": sorted(set(typed_d8.keys()) - set(d8.keys())),
    }

    # Invalidation substance survival (timeout / field-prime class)
    inv_blob = "\n".join(x for x in inv if isinstance(x, str)).lower()
    inv_survival = {
        "timeout_or_wall": bool(re.search(r"timeout|wall.clock|budget", inv_blob)),
        "field_or_prime": bool(re.search(r"field|prime|curve|pin", inv_blob)),
        "no_spec_yaml_stands": not bool(
            re.search(
                r"all experiment\.invalidation_rules of specification\.yaml stand",
                inv_blob,
            )
        ),
        "count": len(inv),
    }

    # D8 module / trial_plan sentences
    d8_checks = {
        "trial_plan_present": "trial_plan" in d8,
        "manifest_present": "manifest" in d8,
        "successor_hash_in_trial_plan": bool(
            re.search(r"successor_contract_sha256", str(d8.get("trial_plan", "")))
        ),
    }

    # Negative control: remove one non-hash manifest item from scratch copy
    scratch = copy.deepcopy(draft)
    sc2 = scratch["successor_contract"]
    mr = sc2["fresh"]["custody"]["manifest_rule"]
    # Drop "tool versions" phrase
    mr_nc = re.sub(r",?\s*tool versions", "", mr, count=1, flags=re.I)
    assert mr_nc != mr, "NC edit failed to change manifest_rule"
    sc2["fresh"]["custody"]["manifest_rule"] = mr_nc
    nc_survival = {
        item: bool(re.search(re.escape(item), mr_nc, re.I))
        for item in MANIFEST_ITEMS
    }
    # retarget tool versions check
    nc_survival["tool versions"] = bool(re.search(r"tool versions", mr_nc, re.I))
    nc_detected = nc_survival["tool versions"] is False and all(
        (k == "tool versions") or v for k, v in nc_survival.items()
    )
    # Broader: detected if tool versions missing while others present
    nc_detected = (not nc_survival["tool versions"]) and sum(
        1 for k, v in nc_survival.items() if k != "tool versions" and v
    ) >= 5

    # Scan for dropped D10 module sentences vs typed
    typed_d10 = ((ta.get("change") or {}).get("D10_additivity")) or {}
    d10_note = {
        "typed_keys": sorted(typed_d10.keys()) if isinstance(typed_d10, dict) else [],
        "proto_keys": sorted(d10.keys()) if isinstance(d10, dict) else [],
        "proto_rule_prefix": str(d10.get("rule", ""))[:240],
    }

    result = {
        "replacement_surfaces_checked": [
            "F-CUSTODY",
            "F-WRITE",
            "F-REV",
            "execution_admission",
            "invalidation_rules",
            "D8_custody",
            "D10_additivity",
        ],
        "checks": checks,
        "invalidation_survival": inv_survival,
        "d8_checks": d8_checks,
        "d10_note": d10_note,
        "negative_control": {
            "id": "NC-EJ5-drop-tool-versions",
            "edit": "remove 'tool versions' from scratch F-CUSTODY.manifest_rule",
            "nc_survival": nc_survival,
            "detected": nc_detected,
        },
        "verdict_inputs": {
            "all_manifest_items_present": checks["all_manifest_items_present"],
            "trial_plan_and_dirty_ok": checks["trial_plan_recomputes_sha256"]
            and checks["dirty_refusal_scoped"],
            "write_and_rev_ok": checks["write_scope_confined_to_55c6c0"]
            and checks["F_REV_only_revision"]
            and checks["D10_cites_F_REV"],
            "admission_ok": checks["admission_lists_explicitly_not_required"]
            and checks["admission_not_currently_admitted"],
            "typed_d8_keys_complete": len(checks["typed_d8_keys_missing"]) == 0,
            "no_spec_stands_pointer": inv_survival["no_spec_yaml_stands"],
            "nc_detected": nc_detected,
        },
    }

    out = WRITE / "ej5_replacement_check.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps(result["verdict_inputs"], indent=2))
    print("manifest", manifest_survival)
    print("wrote", out)


if __name__ == "__main__":
    main()
