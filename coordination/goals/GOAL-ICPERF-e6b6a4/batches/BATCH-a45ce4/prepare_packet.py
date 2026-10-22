"""Deterministically prepare prospective prime63 approval bytes, without launching trials."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
BATCH = Path(__file__).resolve().parent
PREVIEW = BATCH / "approval-preview"
EXP = "EXP-ICPERF-891f7f"
GOAL = "GOAL-ICPERF-e6b6a4"
DEC = "DEC-20261017-adc657"
TASK = "TASK-20261017-7ca6ac"
ARCHIVE = "TASK-20261017-7469b8"
REVIEW = "TASK-20261017-ecd082"
LEDGER_ARCHIVE = "TASK-20261017-1ce37e"
EVIDENCE = "EV-ICPERF-5427fe"
REVIEW_DECISION = "DEC-20261017-b0b0d7"
RUN = "RUN-ICPERF-7ed866"
TRIAL = "prime63-panel"
OWNER = "executor-prime63-science"
SPEC = f"experiments/{EXP}/specification.yaml"
PLAN = f"experiments/{EXP}/trial-plan.json"
QUEUE = f"coordination/goals/{GOAL}/batches/BATCH-a45ce4/dispatch_queue.json"
HANDOFF = f"ledger/handoffs/{TASK}.yaml"
RUN_DIR = f"experiments/{EXP}/runs/{RUN}"
RECEIPT = f"coordination/goals/{GOAL}/batches/BATCH-a45ce4/archives/{ARCHIVE}/snapshot-receipt.json"
REVIEW_PLAN = "coordination/review/icperf-prime63-retry-20261017/review-plan.yaml"
REVIEW_DIR = f"coordination/review/icperf-prime63-retry-20261017/{REVIEW}"
REVIEW_FILES = [f"{REVIEW_DIR}/report.md", f"{REVIEW_DIR}/attestation.yaml"]
LEDGER_RECEIPT = f"coordination/goals/{GOAL}/batches/BATCH-a45ce4/archives/{LEDGER_ARCHIVE}/ledger-receipt.json"
REVIEW_REPORT_DIR = f"experiments/{EXP}/reports/review-{REVIEW_DECISION}"
LEDGER_FILES = [f"ledger/evidence/{EVIDENCE}.yaml", f"ledger/decisions/{REVIEW_DECISION}.yaml",
                *[f"{REVIEW_REPORT_DIR}/{name}" for name in
                  ("report.md", "diagram.svg", "report.typ", "report.pdf")]]
GUARD = "research/icperf_prime63_checker_guard_20261017/guard.py"
GUARD_RECEIPT = f"coordination/goals/{GOAL}/batches/BATCH-800634/archives/TASK-20261017-0821e6/snapshot-receipt.json"
CORRECTED_RECEIPT = f"coordination/goals/{GOAL}/batches/BATCH-0f9c5a/archives/TASK-20261017-0298ad/snapshot-receipt.json"
DRIVER = "research/icperf_prime63_inflight_admission_20261017/driver.py"
RUNTIME_DRIVER = f"experiments/{EXP}/runtime_driver.py"
RUNTIME_MANIFEST = f"experiments/{EXP}/runtime-manifest.json"
SAGE = "/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    source_paths = [
        "research/icperf_prime63_inflight_admission_20261017/execute.py",
        DRIVER,
        RUNTIME_DRIVER,
        RUNTIME_MANIFEST,
        "research/icperf_prime63_inflight_admission_20261017/check.py",
        "research/icperf_prime63_inflight_admission_20261017/input_manifest.json",
        "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz",
        "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json",
        "research/icperf_prime63_pilot_launcher_20261017/input_replay.json",
        "research/icperf_prime63_pilot_launcher_20261017/verify_run.py",
        "research/icperf_prime_wide_backend_retry_20261017/backend.py",
        "research/icperf_prime_475_target_systems_20261017/systems.json.gz",
        GUARD,
    ]
    inputs = [
        "research/icperf_prime_coset_896_20261017/scan.json",
        "research/icperf_prime_475_controls_20261017/controls.json",
        GUARD_RECEIPT,
        CORRECTED_RECEIPT,
        "/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage",
    ]
    source_hashes = {path: sha(ROOT / path) for path in source_paths}
    input_hashes = {path: sha(ROOT / path) if not path.startswith("/") else sha(Path(path))
                    for path in inputs}

    spec = yaml.safe_load((ROOT / SPEC).read_text())
    body = spec["experiment"]
    assert body["status"] == "review_required" and body["approved_by"] is None
    body.update(status="approved", approved_by=DEC, execution_authorized=True,
                batch_id="BATCH-a45ce4")
    body["input_bindings"]["runtime_driver_py"]["sha256"] = source_hashes[RUNTIME_DRIVER]
    body["input_bindings"]["runtime_manifest_json"]["sha256"] = source_hashes[RUNTIME_MANIFEST]
    spec_preview = PREVIEW / "specification.yaml"
    spec_preview.write_text(yaml.safe_dump(spec, sort_keys=False, width=120))

    argv_tail = ["--plan", PLAN, "--owner", OWNER, "--epoch", "1",
                 "--trial-id", TRIAL, "--run-dir", "{run_dir}"]
    trial = {"id": TRIAL, "run_id": RUN, "depends_on": [],
             "argv": [SAGE, "-python", RUNTIME_DRIVER, *argv_tail],
             "check_argv": ["python3", GUARD, *argv_tail],
             "memory_mb": 8192, "watchdog_seconds": 14460,
             "watchdog_reason": "Bound the four-hour panel and checker for machine protection; a stop is censored or infrastructure, never a mathematical negative.",
             "artifacts": ["manifest.yaml", "raw-result.json", "raw.tar.gz"]}
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "frozen": True,
            "experiment_id": EXP, "goal_id": GOAL, "hypothesis_id": "H-ICPERF-05021b",
            "task_id": TASK, "approved_by": DEC, "specification": SPEC,
            "specification_sha256": sha(spec_preview), "queue": QUEUE,
            "source_sha256": source_hashes, "input_sha256": input_hashes,
            "trials": [trial]}
    plan_preview = PREVIEW / "trial-plan.json"
    save_json(plan_preview, plan)
    execution = {"mode": "experiments", "kind": "run", "experiment_id": EXP,
                 "trial_plan": PLAN, "trial_plan_sha256": sha(plan_preview),
                 "approved_by": DEC}

    generated = ["launch.json", "execution-receipt.json", "command.txt",
                 "environment.json", "stdout.log", "stderr.log",
                 "check.stdout.log", "check.stderr.log"]
    artifacts = [f"{RUN_DIR}/{name}" for name in
                 [*generated, *trial["artifacts"], "panel/receipt.json", "panel/raw.tar.gz"]]
    handoff = {"id": TASK, "from": "coordinator", "to": "executor",
               "role": "executor", "kind": "scientific_experiment",
               "recorded_at": "2026-10-17", "status": "assigned",
               "goal_id": GOAL, "batch_id": "BATCH-a45ce4",
               "objective": "Run exactly one 27-cell prime63 solver-to-certificate panel with six planted controls and 21 common-target natural cells at m=2..8.",
               "uncertainty_reduced": "Whether the three B=475 factor bases can produce independently checked full-point certificates within the frozen solver caps at 63-bit subgroup scale.",
               "inputs": [SPEC, PLAN, *source_paths, *inputs],
               "constraints": [
                   "Use the exact committed approved specification, one-trial plan and standard supervisor; do not bypass ordinary ready selection or the live published claim.",
                   "One process at a time; attempt six planted positives first, then the 21 fixed natural cells; enforce 300 seconds, 8 GiB RSS, 8 GiB scratch and four hours for the panel.",
                   "Preserve every per-cell raw request, response, stdout and stderr in the canonical tar and receipt; retain all censored, failed and unattempted cells.",
                   "Use the additive positive contradiction guard as check_argv. A checked satisfying planted witness contradicting a unit-ideal response invalidates the instrument.",
                   "Do not infer degree of regularity from input support or claim a complete index-calculus speedup from this bounded panel. Report observations only."
               ],
               "deliverables": artifacts, "artifact_paths": artifacts,
               "archived_by": ARCHIVE, "execution": execution,
               "inference": {"policy": "executor-implementation", "delivery": "interactive",
                             "fallback_allowed": False, "degraded_allowed": False},
               "budget": {"maximum_runs": 1, "maximum_workers": 1,
                          "watchdog_wall_clock_seconds": 14460,
                          "memory_gb": 8},
               "completion_gate": [
                   "All one-trial supervisor files and three top-level artifacts are present or explicitly missing in the execution receipt; the two fixed nested panel custody files are archived.",
                   "The independent checker replays raw tar bytes and every accepted root through exact polynomial, base, signed lift and full-target-point checks.",
                   "Every positive, natural and unattempted cell is counted once; no result is interpreted as total IC speedup or rho advantage without separately reviewed full-cost evidence."
               ],
               "read_scope": [SPEC, PLAN, QUEUE, *source_paths,
                              *(path for path in inputs if not path.startswith("/"))],
               "write_scope": [RUN_DIR],
               "dispatch_preconditions": [
                   "The prospective packet reports approvable true and the committed Coordinator decision approves this exact plan.",
                   "The approved branch is pushed, newest_experiments reports ready, and the one executor lane claim is live at owner and epoch 1."
               ]}
    handoff_preview = PREVIEW / "handoff.yaml"
    handoff_preview.write_text(yaml.safe_dump({"handoff": handoff}, sort_keys=False, width=120))

    executor_task = {"id": TASK, "title": "Run bounded prime63 27-cell panel",
                     "role": "executor", "priority": 96, "state": "queued",
                     "depends_on": [], "archived_by": ARCHIVE,
                     "artifact_paths": artifacts, "read_scope": handoff["read_scope"],
                     "write_scope": handoff["write_scope"], "review_required": True,
                     "handoff": handoff}
    archive_handoff = {"id": ARCHIVE, "from": "coordinator", "to": "coordinator",
                       "role": "coordinator", "kind": "archive", "recorded_at": "2026-10-17",
                       "status": "assigned", "goal_id": GOAL, "batch_id": "BATCH-a45ce4",
                       "objective": "Snapshot the exact one-trial raw and supervisor artifacts before independent review.",
                       "uncertainty_reduced": "Whether complete prime63 run output has durable content and commit custody.",
                       "inputs": artifacts, "constraints": ["Wait for the executor release; preserve every failed or censored artifact and commit only declared outputs before a separate receipt."],
                       "deliverables": [RECEIPT], "artifact_paths": [*artifacts, RECEIPT],
                       "archived_by": ARCHIVE,
                       "inference": {"policy": "coordinator-orchestration-code", "delivery": "interactive",
                                     "fallback_allowed": False, "degraded_allowed": False},
                       "budget": {"maximum_runs": 0},
                       "completion_gate": ["Content-at-commit hashes bind every declared run artifact and the receipt verifies before any review."],
                       "read_scope": [RUN_DIR],
                       "write_scope": [str(Path(RECEIPT).parent)]}
    archive_task = {"id": ARCHIVE, "title": "Archive prime63 panel raw trial",
                    "role": "coordinator", "priority": 95, "state": "queued",
                    "depends_on": [TASK], "archived_by": ARCHIVE,
                    "artifact_paths": [RECEIPT], "read_scope": [RUN_DIR],
                    "write_scope": [str(Path(RECEIPT).parent)],
                    "review_required": False, "handoff": archive_handoff,
                    "archive": {"kind": "snapshot", "binding_mode": "content_at_commit",
                                "source_task_ids": [TASK], "record_ids": [TASK, ARCHIVE],
                                "commit_sha": None, "parent_sha": None, "path_sha256": {}}}
    review_handoff = {"id": REVIEW, "from": "coordinator", "to": "validator",
                      "role": "validator", "kind": "independent_evidence_validation",
                      "recorded_at": "2026-10-17", "status": "assigned",
                      "goal_id": GOAL, "batch_id": "BATCH-a45ce4",
                      "objective": "Independently replay prime63 raw custody, planted controls, natural full-point certificates and measured scope before any interpretation.",
                      "uncertainty_reduced": "Whether the bounded observations and resource/censor classifications survive independent replay.",
                      "inputs": [REVIEW_PLAN, SPEC, PLAN, RECEIPT, *artifacts],
                      "constraints": [
                          "Read the committed review plan and run snapshot, then independently rederive each assigned quantity from statement and raw bytes.",
                          "Apply the forged unit-ideal planted response as a proves-too-much control; do not trust producer summaries or infer a full-cost ECDLP speedup.",
                          "Remain independent of the executor session and preserve any disagreement as a report, not a changed raw artifact."],
                      "deliverables": REVIEW_FILES, "artifact_paths": REVIEW_FILES,
                      "archived_by": LEDGER_ARCHIVE,
                      "review_plan": yaml.safe_load((ROOT / REVIEW_PLAN).read_text())["review_plan"],
                      "inference": {"policy": "review-adversarial", "delivery": "interactive",
                                    "fallback_allowed": False, "degraded_allowed": False,
                                    "independent_session_required": True},
                      "budget": {"maximum_runs": 0},
                      "completion_gate": ["Signed attestation and report separately assess every assigned joint, the null object and raw archive integrity."],
                      "read_scope": [REVIEW_PLAN, SPEC, PLAN, RECEIPT, RUN_DIR],
                      "write_scope": [REVIEW_DIR]}
    review_task = {"id": REVIEW, "title": "Blind replay prime63 panel evidence",
                   "role": "validator", "priority": 80, "state": "queued",
                   "depends_on": [TASK, ARCHIVE], "archived_by": LEDGER_ARCHIVE,
                   "artifact_paths": REVIEW_FILES, "read_scope": review_handoff["read_scope"],
                   "write_scope": [REVIEW_DIR], "review_required": False,
                   "review_plan_ref": REVIEW_PLAN,
                   "joints_assigned": ["R1", "R2", "R3", "R4", "R5", "proves_too_much_1"],
                   "handoff": review_handoff}
    ledger_handoff = {"id": LEDGER_ARCHIVE, "from": "coordinator", "to": "coordinator",
                      "role": "coordinator", "kind": "ledger_archive", "recorded_at": "2026-10-17",
                      "status": "assigned", "goal_id": GOAL, "batch_id": "BATCH-a45ce4",
                      "objective": "Archive independent review, scoped evidence, Coordinator decision and visual report after the panel.",
                      "uncertainty_reduced": "Which bounded feasibility statement survives validated run evidence and which full-cost obligations remain.",
                      "inputs": [RECEIPT, *REVIEW_FILES],
                      "constraints": ["Commit the run snapshot first, then independent review; never promote a full E2E claim from this bounded panel."],
                      "deliverables": [*LEDGER_FILES, LEDGER_RECEIPT],
                      "artifact_paths": [*REVIEW_FILES, *LEDGER_FILES, LEDGER_RECEIPT],
                      "archived_by": LEDGER_ARCHIVE,
                      "inference": {"policy": "coordinator-orchestration-code", "delivery": "interactive",
                                    "fallback_allowed": False, "degraded_allowed": False},
                      "budget": {"maximum_runs": 0},
                      "completion_gate": ["Independent review and every evidence/decision/report artifact are content-bound before a scientific transition."],
                      "read_scope": [RUN_DIR, RECEIPT, REVIEW_DIR],
                      "write_scope": ["ledger/evidence", "ledger/decisions", REVIEW_REPORT_DIR,
                                      str(Path(LEDGER_RECEIPT).parent)]}
    ledger_task = {"id": LEDGER_ARCHIVE, "title": "Archive prime63 independent evidence review",
                   "role": "coordinator", "priority": 75, "state": "queued",
                   "depends_on": [REVIEW], "archived_by": LEDGER_ARCHIVE,
                   "artifact_paths": [*LEDGER_FILES, LEDGER_RECEIPT],
                   "read_scope": [RUN_DIR, RECEIPT, REVIEW_DIR],
                   "write_scope": ledger_handoff["write_scope"],
                   "review_required": False, "handoff": ledger_handoff,
                   "archive": {"kind": "ledger", "binding_mode": "content_at_commit",
                               "source_task_ids": [REVIEW],
                               "record_ids": [REVIEW, LEDGER_ARCHIVE, EVIDENCE, REVIEW_DECISION],
                               "commit_sha": None, "parent_sha": None, "path_sha256": {}}}
    queue = {"schema": "crypto.autoresearch.dispatch_queue.v1", "goal_id": GOAL,
             "batch_id": "BATCH-a45ce4", "objective": handoff["objective"],
             "max_concurrent": 1, "max_concurrent_basis": "One 8-GiB bounded solver panel on this host",
             "tasks": [executor_task, archive_task, review_task, ledger_task]}
    queue_preview = PREVIEW / "dispatch_queue.json"
    save_json(queue_preview, queue)
    packet = {"schema": "crypto.autoresearch.preapproval_packet.v1",
              "experiment_id": EXP, "approval_decision_id": DEC,
              "specification": SPEC, "trial_plan": PLAN, "queue": QUEUE,
              "handoff": HANDOFF,
              "preview": {"specification": str(spec_preview),
                          "trial_plan": str(plan_preview),
                          "queue": str(queue_preview),
                          "handoff": str(handoff_preview)},
              "source_ref": "origin/codex/icperf-prime63-science-20261017",
              "lane_id": "BATCH-a45ce4",
              "execution_route": {"kind": "implementation",
                                  "reason": "The custom wide-field adapter and independent contradiction guard require executor implementation judgment; the runbook route is not linted."}}
    save_json(PREVIEW / "preapproval-packet.json", packet)
    print(json.dumps({"spec_sha256": sha(spec_preview), "plan_sha256": sha(plan_preview),
                      "queue_sha256": sha(queue_preview),
                      "handoff_sha256": sha(handoff_preview)}, indent=2))


if __name__ == "__main__":
    main()
