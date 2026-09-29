#!/usr/bin/env python3
"""Control 2 of the TASK-20260928-4d6266 design report (control_targets: held-file mutation).

Mutates the six held EXP-AUXIN-7e2e3d files and its implementation/ directory
(including a new file under implementation/typed/) in a SCRATCH CLONE under
$TMPDIR, never in the research worktree, and evaluates the rules the design
report lists against draft EXP-AUXIN-bafa2e. expected_by_design: every one
unaffected (F-CUSTODY.independence); any affected rule is a break.

Usage (from the repository root): python3 <this file> <ref>
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

DRAFT = ("coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"
         "TASK-20260928-4d6266/draft-contract.yaml")
DRAFT_SHA256 = "667cf21e1a0680eaa5eb862164835a0074c109f2254f5ac6f52428327ba27bbd"
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
CAE584_QUEUE = "coordination/design/BATCH-cae584/dispatch_queue.json"
SUCCESSOR_TYPED = "experiments/EXP-AUXIN-bafa2e/implementation/typed/"


def run(args, cwd, check=True):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{args}: {p.returncode} {p.stderr[-2000:]}")
    return p


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def manifest_refuses(porcelain: str, contract_path: str) -> list[str]:
    """F-CUSTODY.manifest: refuse iff dirty_summary lists a path under the
    successor's implementation/typed/ or this contract file."""
    hits = []
    for line in porcelain.splitlines():
        path = line[3:].strip().strip('"')
        if path.startswith(SUCCESSOR_TYPED) or path == contract_path:
            hits.append(line)
    return hits


def t0388_fires(porcelain: str) -> list[str]:
    """Stated T-0388, read literally: launch with a dirty implementation/typed/
    (R5: the successor's) or a dirty amendment path. No F-READ rule rewrites
    'amendment path', so an amendments/ path of any experiment is read as written."""
    hits = []
    for line in porcelain.splitlines():
        path = line[3:].strip().strip('"')
        if path.startswith(SUCCESSOR_TYPED) or "/amendments/" in path:
            hits.append(line)
    return hits


def dispatch_verifies(clone: Path, tmp: Path, tag: str) -> dict:
    out = tmp / f"plan-{tag}.json"
    rep = tmp / f"plan-{tag}.md"
    p = run([sys.executable, "tools/research_dispatch.py", CAE584_QUEUE, "--output", str(out),
             "--report", str(rep), "--claims", "off"], cwd=clone, check=False)
    return {"exit": p.returncode, "stderr_tail": p.stderr.strip()[-600:]}


def main() -> int:
    ref = sys.argv[1]
    repo = Path.cwd()
    if sha((repo / DRAFT).read_bytes()) != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch"}))
        return 2
    doc = yaml.safe_load((repo / DRAFT).read_text(encoding="utf-8"))["successor_contract"]
    sources = doc["transcluded"]["sources"]
    source_commit = doc["transcluded"]["source_commit"]

    tmp = Path(tempfile.mkdtemp(prefix="heldmut-", dir=os.environ.get("TMPDIR")))
    clone = tmp / "clone"
    run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(clone)], cwd=tmp)
    run(["git", "sparse-checkout", "set", "--no-cone", "/experiments/EXP-AUXIN-7e2e3d/",
         "/coordination/design/BATCH-cae584/", "/tools/",
         "/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"], cwd=clone)
    run(["git", "checkout", "--quiet", ref], cwd=clone)
    run(["git", "config", "user.email", "control@scratch.invalid"], cwd=clone)
    run(["git", "config", "user.name", "held-file-mutation control"], cwd=clone)
    ident = run(["git", "rev-parse", "HEAD"], cwd=clone).stdout.strip()

    baseline = {
        "ref": ident,
        "porcelain": run(["git", "status", "--porcelain=v1"], cwd=clone).stdout,
        "dispatch_cae584": dispatch_verifies(clone, tmp, "baseline"),
        "draft_sha256": sha((clone / DRAFT).read_bytes()),
    }

    # --- mutate (working tree) --------------------------------------------
    for rel in HELD + [IMPL_EXISTING]:
        with open(clone / rel, "ab") as fh:
            fh.write(b"\n# held-file mutation control (scratch clone only)\n")
    (clone / IMPL_NEW_TYPED).parent.mkdir(parents=True, exist_ok=True)
    (clone / IMPL_NEW_TYPED).write_text("# held-file mutation control probe\n", encoding="utf-8")
    porcelain = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=clone).stdout

    wt = {}
    blob = {}
    for layer, s in sources.items():
        wt[layer] = sha((clone / s["path"]).read_bytes())
        blob[layer] = sha(run(["git", "show", f"{source_commit}:{s['path']}"], cwd=clone).stdout.encode())
    span_check = {
        "source_blobs_at_source_commit_equal_declared": {l: blob[l] == sources[l]["blob_sha256"] for l in sources},
        "working_tree_differs_from_declared_after_mutation": {l: wt[l] != sources[l]["blob_sha256"] for l in sources},
        "reading": ("F-CUSTODY.span_check recomputes every span from `git show <source_commit>:<source_path>`. "
                    "Those blobs are unchanged by the mutation while the working-tree files differ, so the "
                    "span check outcome is unaffected and a working-tree reader would have seen the change."),
    }
    contract_sha_after = sha((clone / DRAFT).read_bytes())
    refusals = manifest_refuses(porcelain, DRAFT)
    neg_line = f"?? {SUCCESSOR_TYPED}probe.py"
    t0388 = t0388_fires(porcelain)

    # --- commit the mutation, then ask the dispatcher about T-0457's archive
    run(["git", "add", "-A", "experiments/EXP-AUXIN-7e2e3d/"], cwd=clone)
    run(["git", "commit", "--quiet", "-m", "scratch: held-file mutation control"], cwd=clone)
    committed = {"dispatch_cae584": dispatch_verifies(clone, tmp, "mutated")}

    evaluations = [
        {"rule": "F-CUSTODY.trial_plan and admission_item_7",
         "affected": contract_sha_after != baseline["draft_sha256"],
         "evidence": "sha256 of the contract file before and after mutation",
         "reading": "successor_contract_sha256 hashes this contract file only."},
        {"rule": "F-CUSTODY.span_check", "affected": not all(span_check["source_blobs_at_source_commit_equal_declared"].values()),
         "evidence": "span_check block"},
        {"rule": "F-CUSTODY.manifest (dirty_summary refusal)", "affected": bool(refusals),
         "evidence": {"refusing_lines": refusals,
                      "negative_control_line_refuses": bool(manifest_refuses(neg_line, DRAFT))}},
        {"rule": "F-CUSTODY.invalidation", "affected": contract_sha_after != baseline["draft_sha256"],
         "reading": "fires only on an edit of this contract file after approval."},
        {"rule": "T-0373 (typed stopping_rules item 12) under R3", "affected": False,
         "reading": "Governing-text hash resolves under R3 to successor_contract_sha256 (this file). The "
                    "forbidden-module half reads T-0143 under R5, which forbids every EXP-AUXIN-7e2e3d module "
                    "and is not changed by held bytes."},
        {"rule": "T-0395 (typed required_artifacts item 4) under R3", "affected": False,
         "reading": "manifest item list; 'governing-text hashes' is successor_contract_sha256 under R3."},
        {"rule": "T-0388 (typed invalidation_rules item 12)", "affected": bool(t0388),
         "evidence": {"lines_that_make_it_fire": t0388},
         "reading": ("Stated entry: 'Launch with a dirty implementation/typed/ or dirty amendment path ... - "
                     "invalid_measurement of the package.' R5 rewrites the implementation/typed/ half to the "
                     "successor; no F-READ rule (R1-R9) rewrites 'amendment path', and it is not in "
                     "self_reference_table. Read as written, a dirty held amendment file at launch makes the "
                     "successor's package invalid_measurement. That contradicts F-CUSTODY.manifest ('refuses "
                     "nothing') and F-CUSTODY.independence. F-PREC reserved_topics would let F-CUSTODY decide, and "
                     "says such a finding is still a draft defect.")},
        {"rule": "T-0378 (typed invalidation_rules item 1)", "affected": False,
         "reading": "'All experiment.invalidation_rules of specification.yaml stand.' R4 (typed, another file) "
                    "or R7 either way names text, not bytes; the v1 items are stated as T-0529 to T-0535."},
        {"rule": "other stated typed invalidation items (1-9, 11, 13-15)", "affected": False,
         "reading": "None names a held file, hash or git status; item 13 reads implementation/typed/ under R5."},
        {"rule": "v1 invalidation items 1-6", "affected": False,
         "reading": "No held-file reference."},
        {"rule": "T-0535 (v1 invalidation_rules item 7) under R2", "affected": False,
         "reading": "'Overwriting this specification' fires only on this contract under R2. Observation outside "
                    "the declared run_against: 'or a prior run receipt' is unscoped and could read a receipt "
                    "under experiments/EXP-AUXIN-7e2e3d/runs/; not mutated here."},
        {"rule": "T-0461 (v1 launch gate item 2) under R2", "affected": False,
         "reading": "'this frozen contract' is this file under R2."},
        {"rule": "T-0457 (v1 execution_admission item 1)",
         "affected": (committed["dispatch_cae584"]["exit"] != 0) != (baseline["dispatch_cae584"]["exit"] != 0),
         "dependence_on_held_bytes_demonstrated": (
             "content hash mismatch" in baseline["dispatch_cae584"]["stderr_tail"]
             or "content hash mismatch" in committed["dispatch_cae584"]["stderr_tail"]),
         "evidence": {"baseline": baseline["dispatch_cae584"], "after_committed_mutation": committed["dispatch_cae584"]},
         "reading": ("Stated entry requires a 'Verified snapshot archive of H-AUXIN-66e6fd, EXP-AUXIN-7e2e3d, "
                     "DEC-20260913-515d80, TASK-20260913-e347cb'. R6 makes the DEC and TASK references provenance "
                     "only; no rule makes the H and EXP ids provenance only. The queued archive with exactly those "
                     "record_ids, TASK-20260913-d428ec in BATCH-cae584, is content_first over the held "
                     "implementation files, so whether it verifies is a function of held bytes at HEAD. At the "
                     "baseline ref it ALREADY fails (a later held commit changed a bound implementation file), so "
                     "the mutation does not change the outcome and 'affected' is false in this test. The "
                     "dependence itself is demonstrated by the dispatcher's content-hash refusal, which "
                     "F-CUSTODY.independence says no admission item has. Whether another archive (the "
                     "commit-bound opening snapshot of BATCH-cae584) satisfies the item is a reading for the "
                     "review round; the draft names none.")},
        {"rule": "T-0458 (v1 execution_admission item 2) under R5", "affected": False,
         "reading": "Path remapped to experiments/EXP-AUXIN-bafa2e/implementation/."},
        {"rule": "T-0143, T-0144, T-0146, T-0602 under R5", "affected": False,
         "reading": "Every experiments/EXP-AUXIN-7e2e3d/implementation/ path is remapped; T-0144 compares the "
                    "successor's typed/ files with the successor's snapshot. The new held typed/control_probe.py "
                    "is outside every remapped path."},
        {"rule": "T-0566 under R8", "affected": False,
         "reading": "'READ FROM specification.yaml frozen_curve_list' reads the stated entries R7 gives for that "
                    "field, not the file."},
    ]
    affected = [e["rule"] for e in evaluations if e.get("affected")]
    dependent = [e["rule"] for e in evaluations if e.get("dependence_on_held_bytes_demonstrated")]
    self_test_ok = bool(manifest_refuses(neg_line, DRAFT)) and all(
        span_check["working_tree_differs_from_declared_after_mutation"].values())
    label = "NOT_RUN" if not self_test_ok else ("FAIL" if affected or dependent else "PASS")
    result = {
        "control": "held-file mutation",
        "design_report": ("coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"
                          "TASK-20260928-4d6266/design-report.yaml control_targets.controls[1]"),
        "object": {"path": DRAFT, "sha256": DRAFT_SHA256},
        "label": label,
        "affected_rules": affected,
        "held_byte_dependence_without_outcome_change": dependent,
        "scratch": {"clone_ref": ident, "location": "TMPDIR scratch clone (git clone --shared, sparse); "
                    "the research worktree was not modified"},
        "mutations": HELD + [IMPL_EXISTING, IMPL_NEW_TYPED],
        "baseline": baseline,
        "porcelain_after_mutation": porcelain,
        "span_check": span_check,
        "committed_mutation": committed,
        "evaluations": evaluations,
        "self_test": {"manifest_predicate_refuses_successor_typed_line": bool(manifest_refuses(neg_line, DRAFT)),
                      "mutation_visible_in_working_tree": all(
                          span_check["working_tree_differs_from_declared_after_mutation"].values())},
        "limits": ("Rule evaluations other than the manifest, span check, contract hash, T-0388 predicate and "
                   "T-0457 dispatcher check are Coordinator readings of the rule text under F-READ, not "
                   "executions; no protocol run exists to execute them."),
    }
    json.dump(result, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
