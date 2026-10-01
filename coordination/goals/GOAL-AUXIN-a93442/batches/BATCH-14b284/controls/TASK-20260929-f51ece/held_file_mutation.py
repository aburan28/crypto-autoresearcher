#!/usr/bin/env python3
"""Control 2 of TASK-20260929-1abb8c design-report control_targets: held-file mutation.

Mutates EXP-AUXIN-7e2e3d specification/amendments (and adds a held implementation
probe) in a SCRATCH CLONE under $TMPDIR. Evaluates whether any listed draft rule
outcome depends on held-file bytes. expected_by_design: unaffected.

Usage: python3 <this file> <ref>
Writes one JSON result to stdout.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

DRAFT = (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/design/"
    "TASK-20260929-1abb8c/draft-contract.yaml"
)
DRAFT_SHA256 = "608c46c02a59c8f4ba5871e6d32643c58e2b351302b98fd54f866d2bac679b8c"
HELD = [
    "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
]
IMPL_EXISTING = "experiments/EXP-AUXIN-7e2e3d/implementation/driver.py"
IMPL_NEW_TYPED = "experiments/EXP-AUXIN-7e2e3d/implementation/typed/control_probe.py"
SUCCESSOR_TYPED = "experiments/EXP-AUXIN-55c6c0/implementation/typed/"
CONTRACT_FILE_HINT = DRAFT  # relative path of the contract under review


def run(args, cwd, check=True):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args}: {p.returncode} {p.stderr[-2000:]}")
    return p


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def porcelain_paths(porcelain: str) -> list[str]:
    out = []
    for line in porcelain.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.append(path)
    return out


def manifest_refuses(porcelain: str, contract_path: str) -> list[str]:
    """F-CUSTODY.manifest_rule: refuse iff dirty lists contract_file or implementation_tree."""
    hits = []
    for line in porcelain.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith(SUCCESSOR_TYPED) or path == contract_path:
            hits.append(line)
    return hits


def dirty_amendment_held_fires(porcelain: str) -> list[str]:
    """Would a literal 'dirty amendment path' reading of held amendments fire?"""
    hits = []
    for line in porcelain.splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.startswith("experiments/EXP-AUXIN-7e2e3d/amendments/"):
            hits.append(line)
    return hits


def evaluate_rules(doc: dict, porcelain: str, draft_sha: str) -> dict:
    fresh = doc["fresh"]
    custody = fresh["custody"]
    pn = doc["protocol_normative"]
    adm = pn["execution_admission"]

    # Independence claim text
    independence = custody.get("independence", "")
    independence_claims_no_held = "EXP-AUXIN-7e2e3d" in independence and "No gate" in independence

    # Manifest: held dirtiness must NOT refuse
    manifest_hits = manifest_refuses(porcelain, CONTRACT_FILE_HINT)
    held_dirty = dirty_amendment_held_fires(porcelain)

    # Invalidation scan: any rule text that still refuses on held dirty/amendment?
    inv = pn.get("invalidation_rules", [])
    inv_texts = [str(x) for x in inv]
    inv_mentions_held_dirty = [
        t for t in inv_texts
        if ("dirty" in t.lower() and "7e2e3d" in t)
        or ("dirty amendment" in t.lower())
        or ("amendments/" in t and "7e2e3d" in t)
    ]
    inv_dirty_successor_only = [
        t for t in inv_texts
        if "dirty" in t.lower() and "EXP-AUXIN-55c6c0" in t
    ]

    # Execution admission
    reqs = [str(x) for x in adm.get("requirements", [])]
    not_req = [str(x) for x in adm.get("explicitly_not_required", [])]
    req_names_held = [r for r in reqs if "7e2e3d" in r or "H-AUXIN-66e6fd" in r]
    not_req_covers_held = any("7e2e3d" in x for x in not_req)

    # Trial plan / D8
    d8 = pn["change"].get("D8_custody", {})
    trial = str(d8.get("trial_plan", ""))
    trial_binds_held = "7e2e3d" in trial
    trial_binds_successor_hash = "successor_contract_sha256" in trial or "successor_contract_sha256" in str(
        custody.get("trial_plan_rule", "")
    )

    # Outcomes that CHANGE because held files are dirty (contrary to independence)
    affected = []
    if manifest_hits:
        # only affected if hits are held paths — successor hits would be expected
        held_manifest = [h for h in manifest_hits if "7e2e3d" in h]
        if held_manifest:
            affected.append({"rule": "F-CUSTODY.manifest_rule", "detail": "refuses on held dirty", "hits": held_manifest})
    if inv_mentions_held_dirty:
        affected.append({"rule": "invalidation_rules", "detail": "mentions held dirty/amendment", "texts": inv_mentions_held_dirty})
    if req_names_held:
        affected.append({"rule": "execution_admission.requirements", "detail": "names held experiment", "texts": req_names_held})
    if trial_binds_held:
        affected.append({"rule": "D8_custody.trial_plan", "detail": "binds held path", "text": trial[:300]})

    # Self-check: synthetic dirty under successor typed MUST refuse under manifest
    synthetic_porcelain = porcelain + f"\n M {SUCCESSOR_TYPED}probe.py\n"
    synth_hits = manifest_refuses(synthetic_porcelain, CONTRACT_FILE_HINT)
    self_test_successor_dirty_refused = any(SUCCESSOR_TYPED in h for h in synth_hits)

    return {
        "independence_claims_no_held": independence_claims_no_held,
        "held_dirty_lines_present": bool(held_dirty),
        "held_dirty_line_count_omitted": True,  # outcome discipline
        "manifest_refuses_held": False if not any("7e2e3d" in h for h in manifest_hits) else True,
        "manifest_hits_held": [h for h in manifest_hits if "7e2e3d" in h],
        "invalidation_mentions_held_dirty": inv_mentions_held_dirty,
        "invalidation_dirty_successor_present": bool(inv_dirty_successor_only),
        "execution_admission_requires_held": req_names_held,
        "execution_admission_explicitly_not_required_covers_held": not_req_covers_held,
        "trial_plan_binds_held": trial_binds_held,
        "trial_plan_binds_successor_hash": trial_binds_successor_hash,
        "draft_sha256_unchanged": draft_sha == DRAFT_SHA256,
        "affected": affected,
        "self_test_successor_dirty_refused": self_test_successor_dirty_refused,
    }


def main() -> int:
    ref = sys.argv[1]
    repo = Path.cwd()
    if sha((repo / DRAFT).read_bytes()) != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch"}))
        return 2
    doc = yaml.safe_load((repo / DRAFT).read_text(encoding="utf-8"))["successor_contract"]
    if doc["transcluded"]["entries"]:
        print(json.dumps({"label": "NOT_RUN", "reason": "expected zero transclusion entries"}))
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="heldmut-14b284-", dir=os.environ.get("TMPDIR")))
    clone = tmp / "clone"
    run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(clone)], cwd=tmp)
    run([
        "git", "sparse-checkout", "set", "--no-cone",
        "/experiments/EXP-AUXIN-7e2e3d/",
        "/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/design/",
        "/tools/",
    ], cwd=clone)
    run(["git", "checkout", "--quiet", ref], cwd=clone)
    run(["git", "config", "user.email", "control@scratch.invalid"], cwd=clone)
    run(["git", "config", "user.name", "held-file-mutation control"], cwd=clone)
    ident = run(["git", "rev-parse", "HEAD"], cwd=clone).stdout.strip()

    baseline_porcelain = run(["git", "status", "--porcelain=v1"], cwd=clone).stdout
    baseline_sha = sha((clone / DRAFT).read_bytes())

    for rel in HELD:
        p = clone / rel
        if p.exists():
            with open(p, "ab") as fh:
                fh.write(b"\n# held-file mutation control (scratch clone only)\n")
    impl = clone / IMPL_EXISTING
    if impl.exists():
        with open(impl, "ab") as fh:
            fh.write(b"\n# held-file mutation control\n")
    (clone / IMPL_NEW_TYPED).parent.mkdir(parents=True, exist_ok=True)
    (clone / IMPL_NEW_TYPED).write_text("# held-file mutation control probe\n", encoding="utf-8")

    porcelain = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=clone).stdout
    mutated_paths = porcelain_paths(porcelain)
    # Confirm mutations are under held tree only
    non_held = [p for p in mutated_paths if not p.startswith("experiments/EXP-AUXIN-7e2e3d/")]
    draft_after = sha((clone / DRAFT).read_bytes())

    eval_result = evaluate_rules(doc, porcelain, draft_after)
    eval_result["scratch_tmp"] = str(tmp)
    eval_result["clone_ref"] = ident
    eval_result["baseline_porcelain_empty"] = baseline_porcelain.strip() == ""
    eval_result["baseline_draft_sha256"] = baseline_sha
    eval_result["mutations_visible_in_scratch"] = bool(mutated_paths)
    eval_result["non_held_mutations"] = non_held

    affected = eval_result["affected"]
    if not eval_result["self_test_successor_dirty_refused"]:
        label = "FAIL"
        affected.append({"rule": "self_test", "detail": "successor dirty did not refuse under manifest_rule"})
    elif non_held:
        label = "FAIL"
        affected.append({"rule": "scratch_isolation", "detail": "non-held paths mutated", "paths": non_held})
    elif affected:
        label = "FAIL"
    else:
        label = "PASS"

    out = {
        "control": "held-file mutation",
        "label": label,
        "draft_sha256": DRAFT_SHA256,
        "expected_by_design": "unaffected",
        "evaluation": eval_result,
        "affected": affected,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
