#!/usr/bin/env python3
"""Write the exact-byte approval previews of EXP-PEXT-212d5c and the preapproval packet.

Run from the repository root: python3 coordination/goals/GOAL-PEXT-4a1d6b/batches/BATCH-21339c/approval-preview/prepare_packet.py [source_ref]
Writes, beside this script: specification.yaml (draft + freeze_fills), trial-plan.json, dispatch_queue.json,
handoff.yaml (executor), handoffs/TASK-20261024-5ab5b8.yaml (archive), lane.json (lane to open), preapproval-packet.json.
Nothing canonical is written; the committing session copies these to their canonical paths only after the probe
reports approvable true on pushed bytes. Re-run after any change to the draft or the implementation.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import yaml

ROOT = os.getcwd()
HERE = os.path.relpath(os.path.dirname(os.path.abspath(__file__)), ROOT)
EXP = "EXP-PEXT-212d5c"
GOAL = "GOAL-PEXT-4a1d6b"
BATCH = "BATCH-21339c"
DEC = "DEC-20261024-992998"
OBS_DEC = "DEC-20261024-e97526"
EXEC_TASK = "TASK-20261024-672126"
ARCH_TASK = "TASK-20261024-5ab5b8"
H = "H-PEXT-d536a1"
IMPL = f"experiments/{EXP}/implementation"
PLAN = f"experiments/{EXP}/trial-plan.json"
SPEC = f"experiments/{EXP}/specification.yaml"
QUEUE = f"coordination/goals/{GOAL}/batches/{BATCH}/dispatch_queue.json"
HANDOFF = f"ledger/handoffs/{EXEC_TASK}.yaml"
GENERATED = ("launch.json", "execution-receipt.json", "command.txt", "environment.json", "stdout.log", "stderr.log",
             "check.stdout.log", "check.stderr.log")
WD_REASON = "Machine protection only; expiry is failed_infrastructure for the unfinished trial, never a metric value."
TRIALS = [
    # id, run, stage, artifacts, deps, memory_mb, watchdog_s
    ("regression", "RUN-PEXT-fccfb9", "regression", ["regression.json", "R-n3-q3.jsonl", "R-n3-q5.jsonl", "R-n3-q7.jsonl", "R-n5-q3.jsonl"], [], 2048, 3600),
    ("construct", "RUN-PEXT-056770", "construct", ["construct-q3.jsonl", "construct-q5.jsonl", "construct-q7.jsonl"], ["regression"], 2048, 3600),
    ("char2", "RUN-PEXT-708f11", "char2", ["char2.jsonl"], ["regression"], 2048, 7200),
    ("census", "RUN-PEXT-3fd19f", "census", ["census-n7-q3.jsonl", "census-progress.log"], ["regression"], 4096, 172800),
    ("lean", "RUN-PEXT-af1b2a", "lean", ["lean.json", "lean-build.log"], [], 4096, 3600),
    ("analyze", "RUN-PEXT-422517", "analyze", ["analysis.json", "floor-table.md"], ["regression", "construct", "char2", "census"], 2048, 1800),
]


def sha(path: str) -> str:
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write(name: str, data: bytes) -> str:
    p = os.path.join(HERE, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)
    return p


def sources() -> dict:
    out = {}
    for root, dirs, files in os.walk(os.path.join(ROOT, IMPL)):
        dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", ".lake"))
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(root, name), ROOT)
            out[rel] = sha(rel)
    return dict(sorted(out.items()))


def approved_spec() -> bytes:
    text = open(os.path.join(ROOT, SPEC)).read()
    head, rest = text.split("  status: review_required\n", 1)
    assert "  frozen: false\n" in rest
    rest = rest.replace("  frozen: false\n", "  frozen: true\n", 1)
    rest = rest.replace("  approved_by: null\n  approval_decision: null\n  execution_authorized: false\n",
                        f"  approved_by: {DEC}\n  approval_decision: {DEC}\n  execution_authorized: true\n"
                        "  approval_basis: >-\n    AGENTS.md 'Standing user authorization' (user, 2026-09-06); approval bounded by execution: "
                        "tools/experiment_preapproval.py approvable true on pushed bytes, goal approved-unrun capacity checked.\n"
                        f"  execution_scope: >-\n    The six trials of {PLAN} and nothing else, in dependency order, through the "
                        "frozen argv; no other q, n, stratum or seed.\n", 1)
    start = rest.index("  status_note: >-\n")
    end = rest.index("  objective: >-\n")
    rest = rest[:start] + (f"  status_note: >-\n    Frozen at version 1 and approved by {DEC} under AGENTS.md standing "
                           "authorization after the preapproval probe reported approvable true on pushed bytes.\n") + rest[end:]
    return (head + "  status: approved\n" + rest).encode()


def main() -> None:
    source_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/claude/prime-degree-extension-campaign"
    spec_bytes = approved_spec()
    p_spec = write("specification.yaml", spec_bytes)
    src = sources()
    inputs = {k: v for k, v in src.items() if "/fixtures/" in k}
    trials = []
    for tid, rid, stage, arts, deps, mem, wd in TRIALS:
        t = {"id": tid, "run_id": rid, "stage": stage,
             "argv": ["python3", f"{IMPL}/run.py", "trial", "--run-dir", "{run_dir}", "--run-id", rid, "--trial-id", tid, "--plan", PLAN],
             "check_argv": ["python3", f"{IMPL}/check.py", "{run_dir}", PLAN, tid],
             "artifacts": ["manifest.yaml", "raw-result.json", *arts], "depends_on": deps,
             "memory_mb": mem, "watchdog_seconds": wd, "watchdog_reason": WD_REASON}
        if stage == "analyze":
            t["inputs_from"] = {"regression": "RUN-PEXT-fccfb9", "construct": "RUN-PEXT-056770", "char2": "RUN-PEXT-708f11",
                                "census": "RUN-PEXT-3fd19f", "lean": "RUN-PEXT-af1b2a"}
        trials.append(t)
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "experiment_id": EXP, "frozen": True, "approved_by": DEC,
            "specification": SPEC, "specification_sha256": sha_bytes(spec_bytes), "task_id": EXEC_TASK, "queue": QUEUE,
            "source_sha256": src, "input_sha256": inputs,
            "defaults": {"threads": 4, "strata_k": 24, "seed": 20261012, "construct_q": [3, 5, 7], "char2_l": [1, 2, 3]},
            "trials": trials}
    plan_bytes = (json.dumps(plan, indent=1, sort_keys=True) + "\n").encode()
    p_plan = write("trial-plan.json", plan_bytes)
    binding = {"mode": "experiments", "kind": "run", "experiment_id": EXP, "trial_plan": PLAN,
               "trial_plan_sha256": sha_bytes(plan_bytes), "approved_by": DEC}
    run_paths = [f"experiments/{EXP}/runs/{t['run_id']}/{n}" for t in trials for n in (*GENERATED, *t["artifacts"])]
    constraints = [
        "EX-1: launch only the frozen argv of the trial plan through tools/experiment_execution.py with a published live claim on lane BATCH-21339c.",
        "EX-2: do not edit the specification, hypothesis, trial plan or any file under implementation/; protocol changes only as amendments.",
        "EX-3: a timeout, crash, memory kill or watchdog expiry is failed_infrastructure, never a metric value and never a refutation.",
        "EX-4: no interpretation; record metrics. Never overwrite a run directory; run no seventh trial.",
        "EX-5: dependency order; regression first, and nothing after a failed regression is read as evidence.",
        "EX-6: toy fields only; no deployed or standardized curve, key, logarithm or cost.",
        "EX-7: the census uses 4 threads; run it alone on the host (machine headroom, not a research budget).",
    ]
    gate = ["six run directories exist, each with check.py exit 0 recorded in check.stdout.log or a recorded terminal class in its manifest",
            "every declared artifact present",
            "run and report directories committed and pushed on the session branch; the run report follows the research-visuals skill (graph SVG and report.pdf)",
            "no byte of the specification, hypothesis, trial plan or implementation/ changed"]
    exec_handoff = {"handoff": {
        "id": EXEC_TASK, "from": "coordinator", "to": "executor", "role": "executor", "recorded_at": "2026-10-24",
        "opened_by_decision": DEC, "experiment_id": EXP, "hypothesis_id": H, "question_id": "RQ-PEXT-7c3e91", "goal_id": GOAL,
        "lane": BATCH,
        "objective": (f"Execute the frozen trial plan of {EXP}: regression as RUN-PEXT-fccfb9, construct as RUN-PEXT-056770, char2 as "
                      "RUN-PEXT-708f11, census as RUN-PEXT-3fd19f, lean as RUN-PEXT-af1b2a, analyze as RUN-PEXT-422517, each validated by "
                      "check.py; record the primary metrics as observations and write the run report."),
        "uncertainty_reduced": ("Predictions P1 to P7 and heuristic H1 of H-PEXT-d536a1: the n = 7 span spectrum, the split floor 7 and "
                                "its route (3, 7), the non-split floors 161 / 193 / 193 / 577, the characteristic-2 divisor rule. Toy fields only."),
        "inputs": [SPEC, PLAN, f"{IMPL}/", f"ledger/hypotheses/{H}.yaml", f"ledger/decisions/{DEC}.yaml"],
        "constraints": [{"id": c.split(":")[0], "text": c.split(": ", 1)[1]} for c in constraints],
        "deliverables": [f"experiments/{EXP}/runs/<RUN-ID>/ for the six planned runs",
                         f"experiments/{EXP}/reports/run-<YYYYMMDDTHHMMZ>/ (run report, SVG graph, report.pdf; no verdict)"],
        "artifact_paths": run_paths,
        "write_scope": [f"experiments/{EXP}/runs/", f"experiments/{EXP}/reports/"],
        "archived_by": ARCH_TASK, "depends_on": [],
        "dispatch_preconditions": [
            "draft, implementation and previews committed and pushed; preapproval probe approvable true on the pushed bytes",
            f"{DEC} committed with specification_sha256 and trial_plan_sha256 equal to the committed files",
            f"python3 tools/newest_experiments.py --experiment {EXP} --json reports execution_state ready",
            f"lane {BATCH} open and claimed with tools/goal_lanes.py"],
        "review_required": False, "review_note": "independent review (blind recount C7) is opened by /review-evidence after the ledger archive",
        "execution": binding,
        "inference": {"policy": "executor-implementation", "reasoning_effort": None, "fallback_allowed": False,
                      "degraded_allowed": False, "independent_session_required": False, "delivery": "interactive"},
        "budget": {"wall_clock_seconds": sum(t[6] for t in TRIALS), "wall_clock_seconds_note": "sum of the per-trial watchdogs; advisory, machine protection only",
                   "memory_gb": 4, "maximum_runs": 6, "maximum_workers": 4},
        "completion_gate": gate,
        "return_format": "run ids, checker verdicts, analysis.json headline, valid, predictions outcomes and floor_table verbatim",
        "handoff_record": HANDOFF, "state": "queued"}}
    exec_bytes = yaml.safe_dump(exec_handoff, sort_keys=False, width=120).encode()
    p_handoff = write("handoff.yaml", exec_bytes)
    arch_handoff = {"handoff": {
        "id": ARCH_TASK, "from": "coordinator", "to": "coordinator", "role": "coordinator", "recorded_at": "2026-10-24",
        "opened_by_decision": DEC, "experiment_id": EXP, "goal_id": GOAL, "lane": BATCH,
        "objective": f"Ledger-archive the six {EXP} run records with the observation decision {OBS_DEC} (moves no hypothesis status) and the goal checkpoint.",
        "inputs": [f"experiments/{EXP}/runs/", SPEC, f"ledger/hypotheses/{H}.yaml", f"ledger/goals/{GOAL}/goal.yaml"],
        "constraints": ["Stage exactly the run artifacts, the observation decision, the goal checkpoint shard and the goal head's own next_action line.",
                        "A criterion met is an observation; status moves only after independent review (/review-evidence, blind recount C7).",
                        "No trial is launched from this task."],
        "deliverables": [f"ledger/decisions/{OBS_DEC}.yaml", f"ledger/goals/{GOAL}/checkpoints/{BATCH}-{OBS_DEC}.yaml",
                         f"coordination/goals/{GOAL}/batches/{BATCH}/archives/{ARCH_TASK}/ledger-receipt.json"],
        "budget": {"wall_clock_seconds": 1800, "memory_gb": 2, "maximum_runs": 0},
        "completion_gate": ["six run directories with output-validated receipts or explicit infrastructure records",
                            "the observation decision committed and bound in the queue archive block",
                            "path_sha256 in the receipt covers every declared path"],
        "inference": {"policy": "coordinator-orchestration-code", "reasoning_effort": None, "fallback_allowed": False,
                      "degraded_allowed": False, "independent_session_required": False, "delivery": "interactive"},
        "state": "queued"}}
    arch_bytes = yaml.safe_dump(arch_handoff, sort_keys=False, width=120).encode()
    write(f"handoffs/{ARCH_TASK}.yaml", arch_bytes)
    eh = exec_handoff["handoff"]
    queue = {"schema": "crypto.autoresearch.dispatch_queue.v1", "goal_id": GOAL, "batch_id": BATCH,
             "objective": f"Run the frozen n = 7 GHS cover genus floor contract {EXP} ({H}, RQ-PEXT-7c3e91) over its six trials and archive its run records; approval {DEC}.",
             "max_concurrent": 1, "max_concurrent_basis": "machine headroom: the census uses 4 threads on a 4-core host; one task at a time. Not a research budget.",
             "tasks": [
                 {"id": EXEC_TASK, "title": f"Execute {EXP}: six trials (implementation tier)", "role": "executor", "state": "queued",
                  "priority": 85, "review_required": False, "depends_on": [],
                  "read_scope": [SPEC, PLAN, f"{IMPL}/", f"ledger/hypotheses/{H}.yaml", f"ledger/decisions/{DEC}.yaml"],
                  "write_scope": eh["write_scope"], "artifact_paths": run_paths,
                  "handoff": {"record": HANDOFF, "objective": eh["objective"], "uncertainty_reduced": eh["uncertainty_reduced"],
                              "inputs": eh["inputs"], "constraints": constraints, "deliverables": eh["deliverables"],
                              "completion_gate": gate, "budget": eh["budget"], "inference": eh["inference"], "execution": binding},
                  "archived_by": ARCH_TASK},
                 {"id": ARCH_TASK, "title": f"Ledger archive of the six {EXP} run records with the observation decision", "role": "coordinator",
                  "state": "queued", "priority": 80, "review_required": False, "depends_on": [EXEC_TASK],
                  "read_scope": [f"experiments/{EXP}/", "ledger/", f"coordination/goals/{GOAL}/batches/{BATCH}/"],
                  "write_scope": [f"ledger/decisions/{OBS_DEC}.yaml", f"ledger/goals/{GOAL}/checkpoints/{BATCH}-{OBS_DEC}.yaml",
                                  f"ledger/goals/{GOAL}/goal.yaml", f"coordination/goals/{GOAL}/batches/{BATCH}/archives/{ARCH_TASK}/",
                                  f"experiments/{EXP}/runs/"],
                  "artifact_paths": [f"ledger/decisions/{OBS_DEC}.yaml", f"ledger/goals/{GOAL}/checkpoints/{BATCH}-{OBS_DEC}.yaml",
                                     f"coordination/goals/{GOAL}/batches/{BATCH}/archives/{ARCH_TASK}/ledger-receipt.json"],
                  "handoff": {"record": f"ledger/handoffs/{ARCH_TASK}.yaml", "objective": arch_handoff["handoff"]["objective"],
                              "uncertainty_reduced": "Completeness and hash binding of the six run packages; criteria met recorded as observations.",
                              "inputs": arch_handoff["handoff"]["inputs"], "constraints": arch_handoff["handoff"]["constraints"],
                              "deliverables": arch_handoff["handoff"]["deliverables"], "completion_gate": arch_handoff["handoff"]["completion_gate"],
                              "budget": arch_handoff["handoff"]["budget"], "inference": arch_handoff["handoff"]["inference"]},
                  "archive": {"kind": "ledger", "binding_mode": "content_at_commit", "source_task_ids": [EXEC_TASK],
                              "commit_sha": None, "parent_sha": None, "path_sha256": {},
                              "record_ids": [OBS_DEC] + [t[1] for t in TRIALS]},
                  "archived_by": ARCH_TASK}],
             "notes": [{"at": "2026-10-24T00:00:00Z", "kind": "design_written",
                        "text": f"Preview of the final queue for {EXP}, written by the design lane; canonical only after the preapproval probe is approvable on pushed bytes and {DEC} is recorded."}]}
    queue_bytes = (json.dumps(queue, indent=1) + "\n").encode()
    p_queue = write("dispatch_queue.json", queue_bytes)
    lane = {"batch_id": BATCH, "branch": source_ref.split("/", 1)[1], "concurrent_open_lanes_at_open": [],
            "dispatch_queue_path": QUEUE,
            "goal_head_policy": "This lane edits ledger/goals/<GOAL>/goal.yaml only inside its own ledger archive and only additively (open_batches entry, checkpoint pointer, its own next_action line); it never rewrites another lane's entries, and it writes its checkpoint as a write-once shard under ledger/goals/<GOAL>/checkpoints/.",
            "goal_id": GOAL, "objective": f"Freeze, approve and run {EXP} (n = 7 GHS cover genus floor)", "opened_at": None,
            "opened_by": "coordinator", "opening_decision_id": DEC, "schema": "crypto.autoresearch.goal_lane.v1", "session": None,
            "write_scope": [f"coordination/goals/{GOAL}/batches/{BATCH}/"]}
    write("lane.json", (json.dumps(lane, indent=2, sort_keys=True) + "\n").encode())
    packet = {"schema": "crypto.autoresearch.preapproval_packet.v1", "experiment_id": EXP, "approval_decision_id": DEC,
              "specification": SPEC, "trial_plan": PLAN, "queue": QUEUE, "handoff": HANDOFF,
              "preview": {"specification": p_spec, "trial_plan": p_plan, "queue": p_queue, "handoff": p_handoff},
              "source_ref": source_ref, "lane_id": BATCH,
              "execution_route": {"kind": "implementation",
                                  "reason": "No runbook: experiment-director (compile mode) could not be dispatched from the design lane; the executor runs the frozen argv at the implementation tier."}}
    write("preapproval-packet.json", (json.dumps(packet, indent=2, sort_keys=True) + "\n").encode())
    print(json.dumps({"specification_sha256": sha_bytes(spec_bytes), "trial_plan_sha256": sha_bytes(plan_bytes),
                      "queue_sha256": sha_bytes(queue_bytes), "handoff_sha256": sha_bytes(exec_bytes)}, indent=1))


if __name__ == "__main__":
    main()
