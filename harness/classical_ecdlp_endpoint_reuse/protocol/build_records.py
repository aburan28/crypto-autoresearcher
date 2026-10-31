#!/usr/bin/env python3
"""Prepare new review-required records outside the canonical checkout.

No execution approval, live claim, lane, archive receipt, run, empirical result
or scientific transition is asserted. The reserved approval/run IDs are names
for a future exact-byte admission packet, not generated approval/run records.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
PREFIX = "harness/classical_ecdlp_endpoint_reuse"
PROBLEM = "problems/classical-ecdlp-endpoint-reuse-isolated-runner-unavailable.md"

def write(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError("Refusing to overwrite generated record: " + str(target))
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    return target

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def problem_text(ids):
    return f'''# Endpoint reuse has no source-bound isolated execution route

- **Status:** `open`
- **Kind:** access/tool limit; implementation/deployment gap
- **Affected work:** [{ids['experiment']}](../experiments/{ids['experiment']}/specification.yaml), [{ids['goal']}](../ledger/goals/{ids['goal']}/goal.yaml), [{ids['capacity_task']}](../ledger/handoffs/{ids['capacity_task']}.yaml)
- **Next action owner:** Coordinator, {ids['capacity_task']}
- **Last updated:** 2026-10-26

## Problem

We cannot yet dispatch the new source-pinned classical endpoint-reuse measurement because this session has no demonstrated generic isolated runner that executes the new code and returns verifiable host and artifact receipts.

The planned study has 64 fresh ordinary, non-anomalous prime-field curves with j distinct from 0 and 1728, 16 each at 12/14/16/18 subgroup bits. Two independent target/setup replicates and 64 targets per cell give 8,192 public target IDs, tested by six complete solver arms. The method retains failed Bernstein–Lange endpoints only after a scalar passes its public point equation, under one fixed known-plus-pending endpoint arena. The original acceptance criterion remains complete source/input-bound execution, all outcomes and independent public witness/trace checks, followed by the registered full setup-plus-solve counter comparison. A draft or a problem record does not satisfy it.

## Evidence and uncertainty

- **Observed:** [capacity observations](../{PREFIX}/execution/evidence/observations.json) at crypto source commit `ac14190f1ab825f0ab1760a093c43bdac8be5e61` report no generic isolab/taskq/spotlab tool exposed in this session and no configured AWS outbound identity. Normal `aws`, `kubectl` and `boto3` entry points were absent. This is session evidence, not a statement that the owner has no such capacity elsewhere.
- **Observed:** the [main Actions bridge](../{PREFIX}/execution/evidence/main-workflow.yml) accepts a main-branch ecbench specification and uses a fixed deployed image. [HARNESS.md](../{PREFIX}/execution/evidence/HARNESS.md) says caller `source_revision` is provenance; it does not cause arbitrary new candidate source or shell code to execute.
- **Observed:** the feature bridge at `fae82d3325e05d0a608b4ea47712cd38cec90c10` is not on the inspected main. [Run 40118925100 job data](../{PREFIX}/execution/evidence/run-40118925100-jobs.json) shows contracts succeeded while build and experiment jobs were skipped. That run is not evidence of a successful custom-image measurement.
- **Observed:** the ordinary GitHub Actions variables read returned HTTP 403, `Resource not accessible by integration`; configuration values were not obtained. The denied read was neither retried nor bypassed.
- **Derived or proved:** a fixed-image specification runner cannot supply a measurement of this new source merely because the request names its commit. A generic node label or CPU request alone does not establish observed L2/tier-B isolation.
- **Suspected explanation:** the remaining gap is connection/deployment access or an undeployed generic worker. Which authorized path is available is not yet established.
- **Missing capability:** a working authorized generic isolated submission route, a real code-only worker image/binary identity, normal authorized public-input/output transport and readback, and observed execution/isolation receipts. Source and protocol fields that depend on those observations remain unbound.
- **What this evidence does not establish:** no scientific batch was attempted; there are no endpoint-reuse measurements, speedups or algorithm failures. It does not refute endpoint reuse, establish runtime isolation, prove the absence of all remote resources, or justify changing the scientific sample or success criterion.

## What would unblock it

- [ ] Identify an authorized exposed generic isolab connection or normal AWS/Kubernetes submission identity; a non-scientific readiness check must establish the actual supported request/worker contract.
- [ ] Build and publish the code-only worker image from an exact source commit, record its actual OCI digest and native binary SHA-256, and verify the measured worker reports those identities. Protocol/public-input data are supplied later by hash, avoiding an image/protocol/input hash cycle.
- [ ] Demonstrate authorized durable public-input transport and output retrieval with actual length/SHA-256 readback; retain all raw streams, the unified export and failures under the repository's canonical artifact policy.
- [ ] Record actual isolated allocation/host facts and per-child isolation blockers. A timed secondary comparison remains invalid without observed L2/tier-B or better; choosing counted metrics does not waive the isolated-placement rule in `docs/experiment-protocol.md` section 4.
- [ ] Complete the source/runtime/preflight bindings and honest inference provenance, freeze and publish the protocol before affected draws, then obtain genuine exact-byte preapproval, committed Coordinator approval, ordinary selector readiness and a real published executor claim. Warnings about unconfigured external API backends do not establish failure of the current interactive Codex session.

These conditions are necessary for this planned measurement route, not proof of a gain. Public witness checks, full counter/memory accounting, the A/A control, complete sampling and later independent scientific interpretation remain obligations.

## Next discriminating step

- **Action or proof obligation:** {ids['capacity_task']} binds one source-capable isolated worker and demonstrates its non-scientific readiness and artifact readback with the actual image/identity; it does not launch this study.
- **Inputs and controls:** the pinned workflow/HARNESS/job evidence above, the prospective source/protocol package, and a readiness control that distinguishes the deployed fixed image from the new candidate worker. Keep API authorization failures distinct from backend process failures.
- **Execution limits and stop condition:** read/configuration checks and a fixed software readiness control only. No scientific target draw or solver cohort, no credential substitution, no changed infrastructure permissions and no campaign spending cap. Stop on a concrete unsupported/unauthorized route and retain its exact result.
- **Outcomes and next actions:** demonstrated source-bound execution and readback allow final admission work; a fixed-image-only or denied route keeps this task impeded and motivates another already-authorized route; ambiguous metadata requires a more discriminating readiness receipt. None of these outcomes changes a mathematical hypothesis.
- **Recheck trigger:** an authorized generic runner/identity becomes available, the owner identifies its existing endpoint, a real image build is available, or the connector/runtime capability set changes.

## Resolution and history

Unresolved. On 2026-10-26 the exact capacity observations and source hashes were retained while implementation, independent public verification and prospective design continued. No source-isolation certificate, experiment approval, run, archive completion or scientific verdict is manufactured by this record. Future updates append actual evidence and preserve this original acceptance criterion.
'''

def build(ids, protocol):
    exp, goal, rq, hyp = (ids[k] for k in ("experiment", "goal", "question", "hypothesis"))
    task = ids["capacity_task"]
    next_action = ("Coordinator: complete " + task + " by binding one source-pinned isolated worker and actual host/artifact-readback receipts for " + exp + "; keep the experiment review_required until final source/protocol/runtime bindings and genuine preapproval permit approval.")
    impediment = {"id": "endpoint-reuse-source-capable-isolated-runner", "raised": "2026-10-26",
                  "condition": "No demonstrated generic isolated source-capable runner and complete source/input/image/preflight bindings for the new study.",
                  "what_is_blocked": "Scientific dispatch and timed/counter performance qualification for " + exp + ", not the research goal.",
                  "clears_when": "Actual source-bound isolated execution/host/artifact readiness plus final frozen protocol and native preapproval are recorded.",
                  "recheck": "On supplied generic-runner connection/identity, real image build or changed runtime capabilities; see " + PROBLEM,
                  "asserts_nothing_about": "Correctness, usefulness, asymptotic cost or empirical performance of the mathematical endpoint-reuse family."}
    goal_doc = {"research_goal": {"id": goal, "title": "Classical verified endpoint reuse at matched finite memory and complete costs",
        "objective": "Implement and test a complete actual-EC Bernstein-Lange endpoint-reuse solver, then compare registered setup-plus-solve counter and memory costs with matched working references.",
        "question_ids": [rq], "status": "active", "owner": "coordinator",
        "completion_criteria": ["The fixed 64-curve, two-replicate,64-target six-arm study has actual complete execution records, all outcomes, retained raw data and a checked unified export.",
                                "All returned scalar/endpoint claims and causal cap/promotion boundaries are independently checked; incomplete or censored outcomes remain visible.",
                                "Registered full-cost, nested-prefix, A/A and memory observations are reported with scope/uncertainty; no improvement is required merely to complete the finite measurement."],
        "pause_conditions": [], "campaign_budget": {"maximum_batches": None, "total_wall_clock_seconds": None, "max_concurrent": 1},
        "next_action": next_action, "next_action_role": "coordinator", "impediments": [impediment], "open_batches": [],
        "predecessor_goal_id": "GOAL-ECDLP-8be063", "previous_finite_goal_preserved": True,
        "claim_scope": "Complete working classical solver and finite measured counter/memory increments; novelty of the generic family and a new asymptotic exponent are not asserted."}}
    question = {"research_question": {"id": rq, "title": "Can verified endpoint reuse reduce actual EC solver work at a fixed endpoint arena?",
        "scope": {"curve_families": ["fresh ordinary non-anomalous j!=0,1728 prime-field curves"], "field_types": ["prime"], "bit_sizes": [12, 14, 16, 18], "methods": [a["id"] for a in protocol["arms"]]},
        "motivation": "The completed 48-curve validation established working named references and exposed a poor prefix candidate. The next bounded implementation step tests an existing endpoint-reuse family on actual EC arithmetic with verification and honest finite capacity/cost accounting.",
        "decision_target": "Credit checked working correctness and any qualified finite group-invocation improvement; otherwise retain all costs and identify the next revision or scale test without a novelty gate.",
        "constraints": ["Classical algorithms only; no quantum or index calculus.", "Keep prior generic/UF/reselection data and atlas pointers; new EC monotoneappend scope is distinct.", "No scalar labels supplied to solver/verifier; no method retuning after confirmation."],
        "status": "active", "owner": "coordinator"}}
    hypothesis = {"hypothesis": {"id": hyp, "question_id": rq, "statement": protocol["hypotheses"][0]["statement"],
        "mechanism": protocol["hypotheses"][0]["mechanism"], "status": "specified", "proposed_by": "coordinator",
        "assumptions": ["Certified public prime-field curve, prime subgroup order/base and valid public subgroup targets.", "Native BL walk/endpoint identities are preserved by the source-bound adapter.", "Only publicly verified target scalars certify staged endpoint coefficients."],
        "proof_search_map": {"not_applicable_reason": "A finite implementation/cost study; no theorem, new asymptotic bound or universal closure is claimed."},
        "asymptotic_claim": None, "predictions": [{"metric": "counters.group_additions at m64, complete setup+target deltas", "direction": "lower", "minimum_effect": "See C-growth-filled/P-work in the prospective protocol; passing controls and a pointwise clusterCI wholly below1 within the finite registered scope."}],
        "test_boundary": {"instances": "64 new curves,2 target/setup replicates,64 uniform replacement targets each", "parameters": {"subgroup_bits": [12,14,16,18], "C": "4*C0 requested chains and arena slots", "reuse_prefixes": [1,8,16,32,64]}, "implementation": PREFIX},
        "falsification_conditions": ["A wrong public witness, premature endpoint promotion or arena overflow refutes the affected implementation.", "Failure to reduce registered group-invocation costs characterizes only this frozen method/regime; censoring or missing infrastructure is not a mathematical refutation."],
        "interpretation_limits": ["Known endpoint-reuse family; prior Kuhn2001/generic growth/selection work is retained.", "No runtime saving inferred from EC group counts; full other native counters and peakRSS remain separate.", "No asymptotic fit or cryptographic-scale transfer claimed."]}}
    spec = {"experiment": {"id": exp, "goal_id": goal, "hypothesis_id": hyp, "version": 1,
        "title": "Actual EC verified endpoint reuse under one capped working arena",
        "status": "review_required", "approved_by": None, "frozen": False, "execution_authorized": False,
        "objective": protocol["question"], "controls": protocol["controls"], "independent_variables": protocol["variable_ledger"]["independent"],
        "metrics": protocol["metrics"], "replication": {"independent_curves": 64, "seeds_per_curve": 2, "targets_per_seed": 64},
        "budget": {"policy": "advisory", "maximum_runs": 1, "maximum_workers": 2, "maximum_active_cpus": 4, "memory_gb": 12},
        "stopping_rules": [r["rule"] for r in protocol["stopping_rules"]], "invalidation_rules": protocol["invalidation_rules"],
        "success_criterion": "Complete checked observations are the first milestone; a primary finite group-invocation improvement additionally requires C-growth-filled/P-work at m64 with all declared controls and no success-only panel.",
        "falsification_criterion": "Invalid public equations/cap/causal traces reject the affected implementation; a non-improving finite paired cost is retained without claiming the family exhausted; infrastructure censoring makes no mathematical assertion.",
        "decision_impact": {"on_positive": "Credit working correctness and any separately qualified measured counter improvement at the tested scope, then design independent scale/reuse follow-up.", "on_negative": "Preserve all correct answers, failures, growth and complete costs; investigate the observed bottleneck or next registered implementation change without a universal closure."},
        "variable_ledger": protocol["variable_ledger"], "prediction_provenance": [{"prediction": "P-work", **protocol["hypotheses"][0]["predictions"][0]["provenance"]}],
        "required_artifacts": ["All native per child JSONL/event streams with exact hashes", "Actual worker/process/host/isolation/rusage and source/binary/image receipts", "Independent public scalar/endpoint/causal coverage report", "Unified experiment.export/v1, analysis, flow table, report/graph/PDF"],
        "execution_plan": {"protocol_hashes": [], "source_sha256": {}, "input_sha256": {}, "binding_status": "Draft: actual committed source/binary/runtime/input pins are completed before freeze/admission."},
        "input_bindings": {}, "readiness_problem": PROBLEM,
        "standing_user_authorization": "User authorizes classical algorithm research, experiments and continuation; standing AGENTS authorization covers complete runnable designs, not fabricated readiness."}}
    decision = {"coordinator_decision": {"id": ids["design_decision"], "context": "Continue the user's classical working-solver/baseline program with an actualEC fixed-arena monotone endpoint-reuse study; no scientific measurements have been started.",
        "decision": "revise", "target_ids": [goal, rq, hyp, exp],
        "rationale": ["The narrowly scoped actualEC verified-growth implementation is distinct from previously executed generic UF/reselection studies, while the broader family is existing prior work.", "The scientific cohort, costs, comparisons, controls and analysis are explicit, but the source-capable isolated route and remaining observed bindings are not complete.", "Keep the goal active and contract review_required; do not approve, manufacture a claim, draw confirmation targets, or substitute local measurement for the required isolated route."],
        "evidence_refs": [PREFIX + "/mechanism-review/audit.json", PREFIX + "/execution/evidence/observations.json", "experiments/EXP-ECDLP-9f7772/reports/run-20261025T1930Z/observations.md", PROBLEM],
        "limitations": ["Prospective design and source/interface checks only; no new endpoint-reuse outcomes, L2 qualification or independent scientific review.", "Configured external API doctor warnings do not establish interactive Codex failure. Unknown interactive backend/model provenance remains unknown; no model_verified or fallback attestation is manufactured."],
        "next_actions": [next_action], "knowledge_promotion": {"promoted": [], "not_warranted": "Prospective design and an access/deployment gap do not supply a new replicated scientific finding."},
        "decided_by": "coordinator", "decided_at": "2026-10-26"}}
    capacity = {"handoff": {"id": task, "from": "coordinator", "to": "coordinator", "role": "coordinator",
        "objective": "Bind one actual source-capable isolated worker and its input/output readback route for the new endpoint-reuse study; do not run the scientific cohort.",
        "uncertainty_reduced": "Which already-authorized connection/image/identity can actually execute the pinned source and return observed isolation/artifact receipts.",
        "inputs": [PROBLEM, PREFIX + "/execution/evidence/observations.json", "experiments/" + exp + "/protocol.json"],
        "constraints": ["No scientific target draw or measurement launch.", "No credential substitution, unsupported request fields, permission widening, fake image builds, isolation labels or retrospective approval.", "A fixed deployed ecbench image does not execute a new candidate merely because source_revision names it."],
        "deliverables": ["A source/image/binary-bound readiness result with exact supported submission contract and observed host/artifact readback, or a retained exact refusal."],
        "artifact_paths": [PREFIX + "/execution/route-readiness.json"], "archived_by": ids["design_archive_task"],
        "inference": {"policy": "coordinator-orchestration-code", "reasoning_effort": "high", "fallback_allowed": False, "degraded_allowed": False, "independent_session_required": False, "delivery": "interactive"},
        "budget": {"maximum_runs": 0, "reason": "Readiness/design integration only; no scientific trial."},
        "completion_gate": ["Exact source-bound worker execution capability and normal authorized artifact readback established, or exact bounded inability recorded.", "Unknown model/runtime/isolation fields remain unknown; no readiness or approval inferred."],
        "return_format": "JSON observations and exact source/hash-linked pointers; no mathematical verdict.",
        "prospective_only": True}}
    executor = {"handoff": {"id": ids["executor_task"], "from": "coordinator", "to": "executor", "role": "executor",
        "objective": "After real admission only, execute exactly the frozen128cell/sixarm complete study, retaining all outcomes and actual receipts.",
        "uncertainty_reduced": "ActualEC correctness, certified endpoint growth/cap behavior and complete counter/memory comparisons at the fixed scope.",
        "inputs": ["experiments/" + exp + "/protocol.json", "experiments/" + exp + "/trial-plan.json", PREFIX + "/cohort/public/publication-handoff.json"],
        "constraints": ["This handoff is prospective and not dispatchable while the experiment is review_required.", "Require committed source/input pins, exact genuine preapproval, Coordinator approval, selector readiness and actual published claim before any measurement.", "Never change sample/seeds/caps/accounting or retry errors until they pass; report every failed/censored case.", "Only publish observations; scientific promotion or qualification needs its separate evidence/review decision."],
        "deliverables": ["Exact raw runs and per child execution receipts, independent witness/trace checks, unified export, registered analysis, flow table and observation report/graph/PDF."],
        "artifact_paths": ["experiments/" + exp + "/runs/" + ids["reserved_run"] + "/manifest.yaml", "experiments/" + exp + "/export.json"],
        "archived_by": ids["archive_task"],
        "inference": {"policy": "executor-implementation", "reasoning_effort": "high", "fallback_allowed": False, "degraded_allowed": False, "independent_session_required": False, "delivery": "interactive"},
        "budget": {"maximum_runs": 1, "memory_gb": 12},
        "completion_gate": ["Frozen declared coverage or retained exact operational failure; no fabricated missing rows.", "Native checker and independent public witness/causal checks pass for any claimed complete panel; clocks valid only with observed qualification.", "Raw records and unified export pass actual hash/coverage checks before analysis/interpretation."],
        "return_format": "Exact counts/statuses/artifact paths and missing capabilities; no official hypothesis verdict.", "prospective_only": True}}
    def archive_handoff(ident, objective, inputs):
        receipt = "coordination/goals/" + goal + "/batches/" + ids["batch"] + "/archives/" + ident + "/snapshot-receipt.json"
        return {"handoff": {"id": ident, "from": "coordinator", "to": "coordinator", "role": "coordinator",
                "objective": objective, "uncertainty_reduced": "Exact immutable source/output custody only.",
                "inputs": inputs, "constraints": ["Isolated actual archive with exact declared paths and hashes; no fabricated commit receipt or scientific transition."],
                "deliverables": [receipt], "artifact_paths": [receipt],
                "completion_gate": ["The actual source/output snapshot and its real Git receipt verify against the unchanged repository verifier."],
                "budget": {"maximum_runs": 0}, "prospective_only": True}}
    design_archive = archive_handoff(ids["design_archive_task"], "Archive a future bound runtime-readiness result and its exact source/route identity.",
                                     [PREFIX + "/execution/route-readiness.json"])
    run_archive = archive_handoff(ids["archive_task"], "Archive exact future scientific outputs, export and all incomplete/failed outcomes before any scientific interpretation.",
                                  ["experiments/" + exp + "/runs/" + ids["reserved_run"] + "/", "experiments/" + exp + "/export.json"])
    return goal_doc, question, hypothesis, spec, decision, capacity, executor, design_archive, run_archive

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--protocol", type=Path, required=True)
    p.add_argument("--ids", type=Path, default=HERE / "ids.json")
    args = p.parse_args()
    ids = json.loads(args.ids.read_text())
    docs = build(ids, json.loads(args.protocol.read_text()))
    paths = [("ledger/goals/" + ids["goal"] + "/goal.yaml", docs[0]),
             ("ledger/questions/" + ids["question"] + ".yaml", docs[1]),
             ("ledger/hypotheses/" + ids["hypothesis"] + ".yaml", docs[2]),
             ("experiments/" + ids["experiment"] + "/specification.yaml", docs[3]),
             ("ledger/decisions/" + ids["design_decision"] + ".yaml", docs[4]),
             ("ledger/handoffs/" + ids["capacity_task"] + ".yaml", docs[5]),
             ("ledger/handoffs/" + ids["executor_task"] + ".yaml", docs[6]),
             ("ledger/handoffs/" + ids["design_archive_task"] + ".yaml", docs[7]),
             ("ledger/handoffs/" + ids["archive_task"] + ".yaml", docs[8])]
    for path, value in paths:
        write(args.out, path, value)
    problem = args.out / PROBLEM
    problem.parent.mkdir(parents=True, exist_ok=True)
    problem.write_text(problem_text(ids))
    row = "| [Endpoint reuse has no source-bound isolated execution route](classical-ecdlp-endpoint-reuse-isolated-runner-unavailable.md) | open | " + ids["experiment"] + ": dispatch of the new actual-EC six-arm capped-reuse study; no measurements yet | An authorized generic source-pinned isolated worker, actual image/host identities, durable artifact readback and final admission |\n"
    (args.out / "problems-index-row.txt").write_text(row)
    patch = "*** Begin Patch\n*** Update File: /workspace/classical-ecdlp-validation-ready/problems/README.md\n@@\n | Problem | Status | What it blocks | What would unblock it |\n | --- | --- | --- | --- |\n+" + row.rstrip() + "\n*** End Patch\n"
    (args.out / "problems-index.patch").write_text(patch)
    known = {}
    for name in ("analysis.py", "seed_rules.py", "build_protocol.py", "build_records.py", "check_records.py", "export_bundle.py"):
        known[PREFIX + "/protocol/" + name] = sha(HERE / name)
    write(args.out, PREFIX + "/protocol/actual-source-pins.json", {"schema": "classical.ecdlp.endpoint-reuse.known-source-pins.v1", "known_file_sha256": known,
        "source_commit": None, "binary_sha256": None, "image_digest": None, "input_hashes": {}, "protocol_frozen": False,
        "scope": "Exact current design-source bytes only, not a published source/binary/runtime/input certificate."})
    write(args.out, PREFIX + "/protocol/readiness.json", {"schema": "classical.ecdlp.endpoint-reuse.design-readiness.v1", "experiment_id": ids["experiment"],
        "state": "review_required", "science_parameters_fixed": True, "protocol_frozen": False, "approval_granted": False, "scientific_measurements_started": False,
        "reserved_approval_id_is_not_an_approval": ids["reserved_approval_decision"], "reserved_run_id_is_not_a_run": ids["reserved_run"],
        "remaining_observations_or_integrations": ["Actual published source/code-only image/binary identities", "Source-capable isolated runner identity/placement/artifact readback", "Measured separate preflight cost before confirmation", "Final source/runtime pins, honest interactive inference provenance and official exact-byte preapproval", "Postfreeze public nonce/cohort input hashes/private commitments", "Frozen unified-export/analysis/independent-verification integration"],
        "problem": PROBLEM})

if __name__ == "__main__":
    main()
