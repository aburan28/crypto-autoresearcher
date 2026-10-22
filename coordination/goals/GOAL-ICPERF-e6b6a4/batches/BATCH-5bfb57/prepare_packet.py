"""Prepare exact prospective prime63 m=2 approval bytes; never run a solver.

This writes only approval-preview files. Canonical records are installed only
after the read-only preapproval probe reports approvable true.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
BATCH = Path(__file__).resolve().parent
PREVIEW = BATCH / "approval-preview"
GOAL = "GOAL-ICPERF-e6b6a4"
BID = "BATCH-5bfb57"
EXP = "EXP-ICPERF-515ae3"
RUN = "RUN-ICPERF-eb0d88"
DEC = "DEC-20261019-133820"
REVIEW_DEC = "DEC-20261019-4a1d67"
EVIDENCE = "EV-ICPERF-01ad47"
EXEC = "TASK-20261019-904fbf"
SNAPSHOT = "TASK-20261019-2c3c6a"
VALIDATOR = "TASK-20261019-eb3177"
RED_TEAM = "TASK-20261019-de7d9a"
LEDGER = "TASK-20261019-b3799d"
TRIAL = "prime63-m2-three-arm-diagnostic"
OWNER = "executor-prime63-m2-science"
SPEC = f"experiments/{EXP}/specification.yaml"
PLAN = f"experiments/{EXP}/trial-plan.json"
QUEUE = f"coordination/goals/{GOAL}/batches/{BID}/dispatch_queue.json"
HANDOFF = f"ledger/handoffs/{EXEC}.yaml"
REVIEW_PLAN = "coordination/review/icperf-prime63-m2-20261019/review-plan.yaml"
RUN_DIR = f"experiments/{EXP}/runs/{RUN}"
SNAP_RECEIPT = f"coordination/goals/{GOAL}/batches/{BID}/archives/{SNAPSHOT}/snapshot-receipt.json"
LEDGER_RECEIPT = f"coordination/goals/{GOAL}/batches/{BID}/archives/{LEDGER}/ledger-receipt.json"
VALIDATOR_DIR = f"coordination/review/icperf-prime63-m2-20261019/{VALIDATOR}"
RED_TEAM_DIR = f"coordination/review/icperf-prime63-m2-20261019/{RED_TEAM}"
REVIEW_REPORT = f"experiments/{EXP}/reports/review-{REVIEW_DEC}"
LAUNCHER = "research/icperf_prime63_m2_diagnostic_integration_20261018/execute.py"
CHECKER = "research/icperf_prime63_m2_diagnostic_integration_20261018/check.py"
MANIFEST = "research/icperf_prime63_m2_diagnostic_integration_20261018/input_manifest.json"
PUBLIC = "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz"
WITNESSES = "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json"
SYSTEMS = "research/icperf_prime_475_target_systems_20261017/systems.json.gz"
SAGE = "/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage"
SOURCE_REF = "origin/codex/icperf-prime63-m2-protocol-20261019"


def digest(path: str | Path) -> str:
    p = Path(path)
    return hashlib.sha256((p if p.is_absolute() else ROOT / p).read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, width=110))


def handoff(task: str, role: str, kind: str, objective: str, inputs: list[str],
            artifacts: list[str], read: list[str], write: list[str], archive: str,
            constraints: list[str], gates: list[str], policy: str,
            dependencies: list[str] | None = None) -> dict:
    return {
        "id": task, "from": "coordinator", "to": role, "role": role,
        "kind": kind, "recorded_at": "2026-10-19", "status": "assigned",
        "goal_id": GOAL, "batch_id": BID, "objective": objective,
        "uncertainty_reduced": objective, "inputs": inputs,
        "constraints": constraints, "deliverables": artifacts,
        "artifact_paths": artifacts, "archived_by": archive,
        "inference": {"policy": policy, "delivery": "interactive",
                      "fallback_allowed": False, "degraded_allowed": False},
        "budget": {"maximum_runs": 1 if role == "executor" else 0,
                   **({"maximum_workers": 1, "watchdog_wall_clock_seconds": 2160,
                       "memory_gb": 8} if role == "executor" else {})},
        "completion_gate": gates, "read_scope": read, "write_scope": write,
        "depends_on": dependencies or [],
    }


def task(card: dict, title: str, priority: int, dependencies: list[str],
         review_required: bool = False, archive_binding: dict | None = None) -> dict:
    out = {"id": card["id"], "title": title, "role": card["role"],
           "priority": priority, "state": "queued", "depends_on": dependencies,
           "archived_by": card["archived_by"],
           "artifact_paths": card["artifact_paths"],
           "read_scope": card["read_scope"], "write_scope": card["write_scope"],
           "review_required": review_required, "handoff": card}
    if archive_binding is not None:
        out["archive"] = archive_binding
    return out


def main() -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / MANIFEST).read_text())
    sources = dict(manifest["source_sha256"])
    sources[MANIFEST] = digest(MANIFEST)
    assert all(digest(path) == value for path, value in sources.items())
    inputs = {path: digest(path) for path in [PUBLIC, WITNESSES, SYSTEMS, SAGE]}
    assert inputs[SAGE] == "b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1"

    spec = yaml.safe_load((ROOT / SPEC).read_text())
    body = spec["experiment"]
    assert body["status"] == "review_required" and body["approved_by"] is None
    body.update(status="approved", approved_by=DEC,
                execution_authorized=True, frozen=True)
    spec_preview = PREVIEW / "specification.yaml"
    write_yaml(spec_preview, spec)

    args = ["--plan", PLAN, "--owner", OWNER, "--epoch", "1",
            "--trial-id", TRIAL, "--run-dir", "{run_dir}"]
    trial = {"id": TRIAL, "run_id": RUN, "depends_on": [],
             "argv": [SAGE, "-python", LAUNCHER, *args, "--run-approved"],
             "check_argv": ["python3", CHECKER, *args],
             "memory_mb": 8192, "watchdog_seconds": 2160,
             "watchdog_reason": "Bound a 2100-second three-cell panel plus supervisor and independent checker; a stop is censored or infrastructure.",
             "artifacts": ["manifest.yaml", "raw-result.json"]}
    plan = {"schema": "crypto.autoresearch.trial_plan.v1", "frozen": True,
            "experiment_id": EXP, "goal_id": GOAL,
            "hypothesis_id": "H-ICPERF-05021b", "task_id": EXEC,
            "approved_by": DEC, "specification": SPEC,
            "specification_sha256": digest(spec_preview), "queue": QUEUE,
            "source_sha256": sources, "input_sha256": inputs,
            "trials": [trial]}
    plan_preview = PREVIEW / "trial-plan.json"
    write_json(plan_preview, plan)
    execution = {"mode": "experiments", "kind": "run",
                 "experiment_id": EXP, "trial_plan": PLAN,
                 "trial_plan_sha256": digest(plan_preview), "approved_by": DEC}

    generated = ["launch.json", "execution-receipt.json", "command.txt",
                 "environment.json", "stdout.log", "stderr.log",
                 "check.stdout.log", "check.stderr.log"]
    run_artifacts = [f"{RUN_DIR}/{name}" for name in [*generated, *trial["artifacts"]]]
    run_artifacts += [f"{RUN_DIR}/diagnostic/receipt.json",
                      f"{RUN_DIR}/diagnostic/raw.tar.gz"]
    source_inputs = list(dict.fromkeys([SPEC, PLAN, QUEUE, REVIEW_PLAN,
                                        *sources, *inputs]))
    source_reads = [path for path in source_inputs if not path.startswith("/")]
    exec_card = handoff(
        EXEC, "executor", "scientific_experiment",
        "Run exactly the fixed three planted prime63 m=2 positives after the monitor-null control.",
        source_inputs, run_artifacts, source_reads, [RUN_DIR], SNAPSHOT,
        ["Use only the approved committed plan, standard supervisor, live goal-lane claim and exact ready selector.",
         "One worker; 600 seconds per positive, 2100 seconds total, sampled 8 GiB tree RSS and 8 GiB scratch.",
         "Preserve raw request, phase trace, stdout, stderr and any response; record censors and unattempted cells.",
         "Report observations only; do not rank bases or claim total ECDLP cost."],
        ["All supervisor files and diagnostic raw tar/receipt exist or missing artifacts are explicitly classified.",
         "Independent checker accepts every reported ok root by exact full-point replay.",
         "Every scheduled cell is counted once, including early-stop unattempted cells."],
        "executor-implementation")
    exec_card["execution"] = execution
    exec_card["dispatch_preconditions"] = [
        "Exact packet approvable true, committed approval decision and archive, pushed source branch, ready selector, and live published owner/epoch claim."]
    handoff_preview = PREVIEW / "handoff.yaml"
    write_yaml(handoff_preview, {"handoff": exec_card})

    archive_card = handoff(
        SNAPSHOT, "coordinator", "archive",
        "Bind the complete raw and supervisor run output before independent review.",
        run_artifacts, [SNAP_RECEIPT], [RUN_DIR],
        [f"coordination/goals/{GOAL}/batches/{BID}/archives/{SNAPSHOT}"], SNAPSHOT,
        ["Wait for executor release; commit only declared run outputs, retain failures and censors."],
        ["Exact path hashes, commit parent, source task and record IDs verify before reviewers read output."],
        "coordinator-orchestration-code", [EXEC])
    review = yaml.safe_load((ROOT / REVIEW_PLAN).read_text())["review_plan"]
    validator_files = [f"{VALIDATOR_DIR}/report.md", f"{VALIDATOR_DIR}/attestation.yaml"]
    red_files = [f"{RED_TEAM_DIR}/report.md", f"{RED_TEAM_DIR}/attestation.yaml"]
    validator_card = handoff(
        VALIDATOR, "validator", "independent_evidence_validation",
        "Blindly rederive exact planted identities and validate raw custody and full-point certificates.",
        [REVIEW_PLAN, SPEC, PLAN, SNAP_RECEIPT, *run_artifacts], validator_files,
        [REVIEW_PLAN, SPEC, PLAN, SNAP_RECEIPT, RUN_DIR], [VALIDATOR_DIR], LEDGER,
        ["Use a separate review-adversarial xhigh session; do not read producer interpretation or red-team report before sealing.",
         "Attack R1 and R2 and the proves-too-much control from the prewritten plan."],
        ["Sealed report and attestation cover R1, R2, blind rederivation and the contradiction control."],
        "review-adversarial", [EXEC, SNAPSHOT])
    validator_card["review_plan"] = review
    validator_card["inference"]["independent_session_required"] = True
    red_card = handoff(
        RED_TEAM, "red-team", "independent_cost_model_challenge",
        "Challenge monitor censors and any factor-base or complete-cost inference from separate planted targets.",
        [REVIEW_PLAN, SPEC, PLAN, SNAP_RECEIPT, *run_artifacts], red_files,
        [REVIEW_PLAN, SPEC, PLAN, SNAP_RECEIPT, RUN_DIR], [RED_TEAM_DIR], LEDGER,
        ["Use a separate review-adversarial xhigh session; do not read producer interpretation or validator report before sealing.",
         "Attack R3 and R4 using the raw snapshot and null full-cost ledger."],
        ["Sealed report and attestation cover R3, R4 and every material missing E2E term."],
        "review-adversarial", [EXEC, SNAPSHOT])
    red_card["review_plan"] = review
    red_card["inference"]["independent_session_required"] = True
    ledger_files = [f"ledger/evidence/{EVIDENCE}.yaml",
                    f"ledger/decisions/{REVIEW_DEC}.yaml",
                    *[f"{REVIEW_REPORT}/{name}" for name in
                      ("report.md", "diagram.svg", "report.typ", "report.pdf")]]
    ledger_card = handoff(
        LEDGER, "coordinator", "ledger_archive",
        "Archive both sealed reviews, scoped evidence, decision and visual research report.",
        [SNAP_RECEIPT, *validator_files, *red_files],
        [*ledger_files, LEDGER_RECEIPT],
        [SNAP_RECEIPT, VALIDATOR_DIR, RED_TEAM_DIR],
        ["ledger/evidence", "ledger/decisions", REVIEW_REPORT,
         f"coordination/goals/{GOAL}/batches/{BID}/archives/{LEDGER}"], LEDGER,
        ["Compare reviews only after both reports are sealed; preserve disagreements and procedure deviations.",
         "Do not promote a complete-cost or base-ranking claim from planted systems."],
        ["Content-bound evidence, decision, reviewer reports and visual artifacts precede any official scientific transition."],
        "coordinator-orchestration-code", [VALIDATOR, RED_TEAM])
    for card in (archive_card, validator_card, red_card, ledger_card):
        write_yaml(PREVIEW / "handoffs" / f"{card['id']}.yaml", {"handoff": card})
    queue = {"schema": "crypto.autoresearch.dispatch_queue.v1",
             "goal_id": GOAL, "batch_id": BID,
             "objective": exec_card["objective"], "max_concurrent": 1,
             "max_concurrent_basis": "One bounded Sage worker and independent sequential review",
             "tasks": [
                 task(exec_card, "Run prime63 planted m2 diagnostic", 96, [], True),
                 task(archive_card, "Archive diagnostic raw output", 95, [EXEC],
                      archive_binding={"kind": "snapshot", "binding_mode": "content_at_commit",
                                       "source_task_ids": [EXEC], "record_ids": [EXEC, SNAPSHOT],
                                       "commit_sha": None, "parent_sha": None,
                                       "path_sha256": {}}),
                 task(validator_card, "Blind replay of raw and point certificates", 84, [EXEC, SNAPSHOT]),
                 task(red_card, "Independent censor and cost-model challenge", 83, [EXEC, SNAPSHOT]),
                 task(ledger_card, "Archive independent review and scoped decision", 75,
                      [VALIDATOR, RED_TEAM], archive_binding={
                          "kind": "ledger", "binding_mode": "content_at_commit",
                          "source_task_ids": [VALIDATOR, RED_TEAM],
                          "record_ids": [VALIDATOR, RED_TEAM, LEDGER, EVIDENCE, REVIEW_DEC],
                          "commit_sha": None, "parent_sha": None, "path_sha256": {}}),
             ]}
    for reviewer, joints in [(queue["tasks"][2], ["R1", "R2", "proves_too_much_1"]),
                             (queue["tasks"][3], ["R3", "R4"])]:
        reviewer["review_plan_ref"] = REVIEW_PLAN
        reviewer["joints_assigned"] = joints
    queue_preview = PREVIEW / "dispatch_queue.json"
    write_json(queue_preview, queue)
    packet = {"schema": "crypto.autoresearch.preapproval_packet.v1",
              "experiment_id": EXP, "approval_decision_id": DEC,
              "specification": SPEC, "trial_plan": PLAN,
              "queue": QUEUE, "handoff": HANDOFF,
              "preview": {"specification": str(spec_preview.relative_to(ROOT)),
                          "trial_plan": str(plan_preview.relative_to(ROOT)),
                          "queue": str(queue_preview.relative_to(ROOT)),
                          "handoff": str(handoff_preview.relative_to(ROOT))},
              "source_ref": SOURCE_REF, "lane_id": BID,
              "execution_route": {"kind": "implementation",
                                  "reason": "The custom Sage monitor and raw-custody integration require executor implementation judgment; no linted runbook exists."}}
    write_json(PREVIEW / "preapproval-packet.json", packet)
    write_json(PREVIEW / "prospective-hashes.json", {
        name: digest(path) for name, path in
        [("specification", spec_preview), ("trial_plan", plan_preview),
         ("queue", queue_preview), ("handoff", handoff_preview)]})


if __name__ == "__main__":
    main()
