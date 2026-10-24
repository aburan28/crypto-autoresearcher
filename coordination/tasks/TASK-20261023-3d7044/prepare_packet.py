"""Compile prospective approval bytes; never approve, publish, or run science.

Call only while the canonical experiment is review_required. After the source
and canonical draft are published, the generated packet can be passed to the
repository's read-only experiment_preapproval.py. Approval copies must retain
the exact prospective digests printed by that tool.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.experiment_execution import GENERATED
from tools.research_dispatch import validate_queue

EXP = "EXP-ICPERF-3065f9"
HYP = "H-ICPERF-a2284c"
GOAL = "GOAL-ICPERF-e6b6a4"
BATCH = "BATCH-64029f"
DEC = "DEC-20261023-958d32"
EXEC = "TASK-20261023-361f2c"
SNAP = "TASK-20261023-6fb4b3"
REVIEW = "TASK-20261023-18b489"
BLIND = "TASK-20261023-5301b1"
LEDGER = "TASK-20261023-174f6f"
RUN = "RUN-ICPERF-842b51"
REVIEW_DEC = "DEC-20261023-d70a08"
EVIDENCE = "EV-ICPERF-9bf9d7"
DIRECTOR = "TASK-20261023-675119"
DIRECTOR_SNAP = "TASK-20261023-c5d261"
HERE = Path(__file__).resolve().parent
SPEC = f"experiments/{EXP}/specification.yaml"
PLAN = f"experiments/{EXP}/trial-plan.json"
QUEUE = f"coordination/goals/{GOAL}/batches/{BATCH}/dispatch_queue.json"
RUN_DIR = f"experiments/{EXP}/runs/{RUN}"
ARTIFACTS = ["manifest.yaml", "raw-result.json", "instances.json", "arms.jsonl", "validation.json"]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_yaml(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))


def policy(name, effort, independent=False):
    return dict(policy=name, reasoning_effort=effort, fallback_allowed=False,
                degraded_allowed=False, independent_session_required=independent,
                delivery="interactive", runtime_native=True,
                binding_note="Use the session's explicitly resolved runtime-native binding; no vendor substitution or API probe is implied.")


def envelope(task_id, role, archive, objective, uncertainty, inputs, constraints,
             artifacts, gate, inference, *, runs=0):
    return {"id": task_id, "role": role, "from": "coordinator", "to": role,
            "objective": objective, "uncertainty_reduced": uncertainty,
            "inputs": inputs, "constraints": constraints, "deliverables": artifacts,
            "artifact_paths": artifacts, "archived_by": archive,
            "inference": inference,
            "budget": {"memory_gb": 2, "wall_clock_seconds": 3600, "maximum_runs": runs},
            "completion_gate": gate}


def task(handoff, title, depends, read, write, *, relevant=False, priority=90):
    return dict(id=handoff["id"], title=title, role=handoff["role"], state="queued",
                priority=priority, review_required=relevant, depends_on=depends,
                read_scope=read, write_scope=write, artifact_paths=handoff["artifact_paths"],
                archived_by=handoff["archived_by"], handoff=handoff)


def main():
    current = ROOT / SPEC
    if current.exists():
        prior = yaml.safe_load(current.read_text())["experiment"]
        if prior.get("approved_by") or prior.get("status") not in ("review_required", "draft"):
            raise SystemExit("Refusing to rewrite an approved or executed protocol")
    sources = ["tools/ic_target_benchmark.py", "src/crypto_autoresearcher/__init__.py"]
    sources += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "src/crypto_autoresearcher/index_calculus").glob("*.py"))]
    if (ROOT / "tools/ic_target_analysis.py").exists():
        sources.append("tools/ic_target_analysis.py")
    missing = [p for p in sources if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("Missing prospective sources: " + ", ".join(missing))
    source_hashes = {p: sha(p) for p in sources}
    inputs = {"config/ic-target-benchmark.json": sha("config/ic-target-benchmark.json")}
    parameters = json.loads((ROOT / "config/ic-target-benchmark.json").read_text())
    expected = dict(bits=[12, 14, 16], curve_seeds=[0, 1, 2], solver_seeds=[0, 1],
                    repetitions=3, m=2, factor_base="small_x", engine="mitm",
                    accelerate=False, harvest="off", window=4,
                    arms=["reference_a", "fixed_window", "reference_b"],
                    worker_timeout_seconds=60, bootstrap_replicates=5000, bootstrap_seed=3065)
    if any(parameters.get(k) != v for k, v in expected.items()):
        raise SystemExit("Workload differs from the prospective frozen design")
    hypothesis = dict(
        id=HYP, question_id="RQ-ICPERF-94c86e", status="specified", proposed_by="coordinator",
        statement="A fixed-window repeated-base generator for aP+bQ can reduce complete native toy-IC solve time on the fixed public workload after charging setup and final verification.",
        mechanism="Cache digit multiples of the same P and Q; retain identical seeded a,b targets so decomposition, relation ordering and elimination are unchanged.",
        assumptions=["Prime-order public toy curves generated by the bound package.", "The scalar ranges and group law are unchanged.", "No amortization across independent solves; each candidate builds and pays for its own table."],
        proof_search_map={"not_applicable_reason": "Empirical implementation comparison; algebraic correctness is independently checked, but no new theorem, attack bound or asymptotic claim is proposed."},
        asymptotic_claim=None,
        predictions=[dict(id="P-target", metric="complete_solve_seconds", direction="lower", minimum_effect="C-target gate in the prospective frozen experiment; no measured effect exists yet.")],
        test_boundary=dict(instances="9 public generated prime-order toy curves; 18 curve/solver-seed cells", parameters=expected, implementation=sources, budget={"maximum_workers": 1, "maximum_memory_gb": 1}),
        falsification_conditions=["A valid complete paired workload has geometric speedup <= 1.", "Any same-seed target or relation differs, or independent recovery verification fails (implementation correctness failure, not mathematical impossibility)."],
        interpretation_limits=["Only 12-, 14- and 16-bit prime-field curves, m=2, small_x, mitm, no vector acceleration, harvest off.", "No production-curve, Pollard-rho, exponent, frontier or measured-bound claim.", "Wall time is a machine observation and not a cryptanalytic work bound."])
    write_yaml(ROOT / f"ledger/hypotheses/{HYP}.yaml", {"hypothesis": hypothesis})
    factors = [
        ("field_and_curve", "randomized", "Fixed generator with bits 12,14,16 crossed with seeds 0,1,2; paired arms use the identical full curve and public P,Q."),
        ("target_sampling", "fixed", "Public target seed 0; identical solver seeds 0,1, random a,b distribution, and target_label default for every paired arm."),
        ("factor_base", "fixed", "small_x and package default_fb_size(N,2), built inside every timed solve; bind full point-list digest."),
        ("decomposition_and_elimination", "fixed", "m=2, mitm, scalar accelerate=false, default table arity, min_fill elimination, harvest=off; unchanged bound sources."),
        ("source_and_dependencies", "fixed", "One hash-bound source closure, interpreter and dependency environment for all arms, recorded in the receipt."),
        ("execution_slot", "randomized", "Three repetitions; prescribed alternating arm order by enumerated grid index parity; each arm in a fresh process, no concurrent workers."),
        ("censoring", "fixed", "Per-worker 60-second process watchdog and package default attempt limit 50*N for all arms; preserve every timeout/failure, continue the grid."),
        ("hardware_and_load", "measured", "Record host, Python/dependencies, load and per-process ru_maxrss; no competing scientific producers during the timed grid."),
        ("measurement_boundary", "fixed", "Timer surrounds complete solve entry through return, including setup, misses, LA, recovery and solver verification; fixture generation, process startup, trace hashing and separate checker are reported harness overhead.")]
    spec = dict(
        id=EXP, hypothesis_id=HYP, goal_id=GOAL, version=1,
        title="Matched full-cost fixed-window target generation for native toy prime-field IC",
        designed_at="2026-10-23", status="review_required", approved_by=None, frozen=False, execution_authorized=False,
        objective=hypothesis["statement"],
        inputs=dict(parameters=expected, target_seed=0, baseline="Reference E.add(E.mul(a,P),E.mul(b,Q)) from the same bound solver", candidate="target_engine=fixed_window, target_window=4, charged per-solve cache"),
        input_bindings={"workload": {"path": "config/ic-target-benchmark.json", "sha256": inputs["config/ic-target-benchmark.json"]}, "source_closure": [{"path": p, "sha256": h} for p, h in source_hashes.items()]},
        controls=["Same public input, factor-base point digest, RNG stream, target digest, relation digest, attempts/rank/LA counts and verified k across all three paired arms.", "A/A duplicate reference_a vs reference_b differs only in execution slot, setting timing noise.", "Checker-owned affine arithmetic regenerates seeded targets and verifies every recovered logarithm.", "Driver/checker known-false controls exercise a wrong logarithm and duplicated-reference strict-speedup rejection.", "Full reviewer must actually exercise tampered target/config digests and a missing worker row against a scratch copy, retaining the checker refusals; these are planned review controls, not claimed existing unit-test coverage.", "Supervisor separately rejects changed bound source/config bytes before launch; this is admission coverage and not a driver timing measurement."],
        independent_variables=[{"name": "target_generator", "levels": ["reference", "fixed_window_w4"]}],
        metrics={"primary": [{"name": "complete_solve_seconds", "unit": "seconds", "kind": "measured", "boundary": "External perf_counter_ns around entire solve_index_calculus call; includes final solver verification."}], "secondary": ["CPU seconds at the identical boundary (measured, not added to wall time).", "Full curve group operations and target/setup group operations (distinct measured counts).", "Attempts, successful relations, rank, LA multiply-adds, S3 solves and table entries (distinct measured counts).", "Per-worker peak_rss_bytes and target-table payload bytes (distinct measured/storage quantities; payload is not Python RSS).", "Driver harness_seconds includes fixture generation, process startup and trace hashing, and ends before the independent checker; supervisor/checker timings and logs record checks separately. Do not merge overlapping boundaries.", "Failures/timeouts/invalid records, with reason and stderr.", "Matched rho and Bernstein-Lange gaps: unmeasured, no estimate in this optimization contract."]},
        preregistered_predictions=[{"id": "P-target", "quantity": "Complete-solve geometric paired speedup after per-solve setup", "direction": "greater than 1, subject to the C-target gate", "basis": "Proposed elimination of repeated scalar doublings; no pilot performance data were consulted."}],
        scale_relevance={"tier": "toy", "justification": hypothesis["interpretation_limits"][0], "correspondence": None},
        replication={"seeds": {"curve": [0, 1, 2], "solver": [0, 1], "target": [0]}, "independent_instances": 9, "paired_cells": 18, "repetitions": 3, "arm_executions": 162},
        budget={"enforcement": "advisory", "maximum_memory_gb": 1, "maximum_workers": 1, "maximum_runs": 1},
        stopping_rules=["Execute all54 cell-repetitions and all3 arms (162 workers), regardless of observed timings or censored outcomes; no parameter tuning or successful-only reruns.", "Each worker stops on verified recovery, package default attempt limit 50*N or 60-second process watchdog; preserve that reason.", "Supervisor watchdog1200 seconds protects a stuck parent/child process group. An interrupted incomplete grid is retained and cannot qualify; a successor run requires an additive contract and new run ID."],
        invalidation_rules=["Any missing/duplicate grid row, mismatched config/source/instance/FB/target/relation digest, deterministic paired count, recovered k or independent certificate invalidates the comparison.", "Any failure, timeout or incomplete grid precludes a qualified speedup; retain all artifacts as observations.", "A second scientific producer running during wall-time collection or an uncontrolled primary-metric factor makes wall-time inference inconclusive; operation counts remain separately observable."],
        analysis={"paired_ratio": "For each of54 cell-repetitions, r=((reference_a.seconds+reference_b.seconds)/2)/fixed_window.seconds.", "point_estimate": "exp(mean(log(r))) across all54 pairs; only if all162 are complete and valid.", "aa_factor": "max(exp(mean(log(reference_a/reference_b))), its reciprocal) across the same54 pairs.", "interval": "5000 deterministic percentile bootstrap resamples, seed3065; stratify by bits and sample3 curve groups with replacement within each bit stratum, retaining both solver seeds and all3 repetitions for each selected curve. Report 2.5% and97.5% empirical percentiles.", "failure_policy": "No success-only summary. Incomplete/censored/invalid records suppress the qualified ratio and interval; counts and raw times still reported.", "units": "Wall, CPU, group ops, S3 solves and LA ops are never summed."},
        success_criterion="C-target / P-target: all162 workers are valid with matched deterministic invariants and independent certificates; geometric paired speedup > max(1.05, C-aa aa_factor), and the stratified clustered bootstrap lower95% endpoint > 1. Independent review is required before any performance claim.",
        falsification_criterion="C-target / P-target: a complete valid workload has geometric paired speedup <= 1; an arithmetic or deterministic-invariant mismatch separately falsifies correctness of this implementation. A crash or timeout is operational signal, not evidence against the mathematical mechanism. Values between the falsification and success gates are inconclusive.",
        decision_impact={"on_positive": "After independent review, expose and document the measured optional generator at this exact toy scope and record its delta; do not change historical defaults or official frontiers.", "on_negative": "Retain the reference default, preserve the regression/correctness evidence, and inspect the measured setup/collection breakdown before designing a successor.", "on_inconclusive": "Preserve all observations and the unchanged default; commission a new fixed workload only if its controls resolve the recorded uncertainty."},
        variable_ledger={"independent": [{"name": "target_generator", "levels": ["reference", "fixed_window_w4"]}], "factors": [{"name": n, "treatment": t, "how": how} for n, t, how in factors], "comparisons": [{"id": "C-target", "arms": ["reference_a+reference_b", "fixed_window"], "differs_in": ["target_generator"], "design": "one_factor"}, {"id": "C-aa", "arms": ["reference_a", "reference_b"], "differs_in": ["execution_slot"], "design": "aa"}], "crosses_map": False},
        prediction_provenance=[{"prediction": "P-target", "first_recorded_in": f"ledger/hypotheses/{HYP}.yaml", "written_at": "2026-10-23", "data_seen": [], "sample_status": "out_of_sample", "overlap": "No performance pilot or trial for this candidate/grid was consulted; arithmetic correctness tests are not performance observations."}],
        required_artifacts=[f"{RUN_DIR}/{x}" for x in [*GENERATED, *ARTIFACTS]],
        required_reports="After immutable run publication, a write-once reports/run-YYYYMMDDTHHMMZ directory with source, graph/SVG and inspected PDF under research-visuals. Reports are observations until independently reviewed.",
        execution_proof={"status": "unavailable", "limitation": "Hash-bound supervisor/checker receipts and certificates do not establish zkVM execution verification; no guest or execution-proof claim."},
        assigned_to="executor")
    write_yaml(ROOT / SPEC, {"experiment": spec})
    preview = HERE / "preview"
    approved = copy.deepcopy(spec)
    approved.update(status="approved", approved_by=DEC, frozen=True, execution_authorized=True)
    write_yaml(preview / "specification.yaml", {"experiment": approved})
    trial = dict(id="fixed-full-grid", run_id=RUN, depends_on=[],
                 argv=[".venv/bin/python", "tools/ic_target_benchmark.py", "run", "--out", "{run_dir}"],
                 check_argv=[".venv/bin/python", "tools/ic_target_benchmark.py", "check", "--run-dir", "{run_dir}"],
                 artifacts=ARTIFACTS, memory_mb=1024, watchdog_seconds=1200,
                 watchdog_reason="Stop a stuck parent or child process group; preserve incomplete observations, never infer a scientific negative.",
                 parameters=expected, seed=3065)
    plan = dict(schema="crypto.autoresearch.trial_plan.v1", experiment_id=EXP, hypothesis_id=HYP,
                task_id=EXEC, approved_by=DEC, frozen=True, specification=SPEC,
                specification_sha256=sha(str((preview / "specification.yaml").relative_to(ROOT))),
                queue=QUEUE, source_sha256=source_hashes, input_sha256=inputs, trials=[trial])
    write_json(preview / "trial-plan.json", plan)
    draft_plan = copy.deepcopy(plan)
    draft_plan.update(frozen=False, approved_by=None, specification_sha256=sha(SPEC))
    write_json(ROOT / PLAN, draft_plan)
    binding = dict(mode="experiments", kind="run", experiment_id=EXP, trial_plan=PLAN,
                   trial_plan_sha256=sha(str((preview / "trial-plan.json").relative_to(ROOT))), approved_by=DEC)
    run_paths = [f"{RUN_DIR}/{name}" for name in [*GENERATED, *ARTIFACTS]]
    producer = envelope(EXEC, "executor", SNAP, "Execute exactly the approved paired toy-IC grid through the supervisor.", "Whether full solve wall time changes with identical targets/relations after charged setup.", [SPEC, PLAN, "config/ic-target-benchmark.json"], ["Launch only after committed approval, ready selector, clean bound sources and published live claim.", "No concurrent scientific producer, no adaptive workload or selective retries.", "Retain every failure and complete the frozen grid; do not promote a claim."], run_paths, ["All declared supervisor/trial artifacts and checker output exist or exact operational failure is retained.", "Commit/push raw observations before a separate write-once run report."], policy("executor-implementation", "medium"), runs=1)
    producer["execution"] = binding
    def review_paths(t):
        return [f"coordination/tasks/{t}/review_report.yaml", f"coordination/tasks/{t}/derivation.md"]
    blind_handoff = envelope(BLIND, "reviewer", LEDGER, "Blindly rederive fixed-window equivalence and reference target-generation operation accounting from the statement and public parameters alone.", "Whether the proposed cache changes the sampled group element or disguises a local count as a full solve gain.", [SPEC, "config/ic-target-benchmark.json", "src/crypto_autoresearcher/index_calculus/curve.py", f"{RUN_DIR}/instances.json"], ["Fresh independent xhigh session; do not inherit producer conversation.", "Do not read producer targets.py, benchmark/analysis code, run raw outputs, measured reports, sibling review or commit messages giving results.", "Own J-algebra only; write the derivation before any later deliberate unblinding (none is authorized by this task)."], review_paths(BLIND), ["Derive the radix-window group identity and reference group-add formula for bounded nonnegative a,b from the statement and bound baseline group law.", "State boundary controls a=0, b=0, partial final window, infinity, and incorrect digit shifts; list sources actually read and blind_from_respected."], policy("review-adversarial", "xhigh", True))
    reviewer = envelope(REVIEW, "reviewer", LEDGER, "Independently audit complete-cost accounting, matched workload, raw certificates and speedup interpretation.", "Whether any apparent performance result survives independent arithmetic, raw metric recomputation and known-false controls.", [SPEC, PLAN, f"{RUN_DIR}/", *sources, "config/ic-target-benchmark.json"], ["Fresh independent xhigh session, no sibling report reads.", "Recompute metrics from raw data; no trial reruns under this zero-run review task.", "Own J-integrity and J-inference only; test rejection of duplicate-A/A speedup, tampered scalar/digest and missing worker records.", "State measured-vs-derived boundaries, RSS/payload distinction, censoring, confidence and tested scope."], review_paths(REVIEW), ["Review report declares review_attestation with sources_read and each owned joint verdict.", "Independent code/affine-certificate and metric calculations reconcile or concrete breaking artifacts are retained."], policy("review-adversarial", "xhigh", True))
    protected = ["src/crypto_autoresearcher/index_calculus/targets.py", "tools/ic_target_benchmark.py", "tools/ic_target_analysis.py", f"{RUN_DIR}/raw-result.json", f"{RUN_DIR}/arms.jsonl", f"{RUN_DIR}/validation.json", f"experiments/{EXP}/reports/", f"coordination/tasks/{REVIEW}/"]
    review_plan = dict(claim_under_review="Any proposed complete-solve speedup and correctness of the fixed-window target generator, at the frozen toy workload only; no numerical result exists at plan creation.", coordinator_prior="The group identity should preserve targets; setup may erase gains in small/short solves, so a positive full-cost result is uncertain before measurements.", joints=[dict(joint="J-algebra: fixed-window digits preserve aP+bQ and independently derived reference target group-operation formula.", assigned_to=BLIND, attack_plan="Derive the digit expansion independently, including zero scalars and final partial window; construct a wrong shifted-digit implementation that must fail.", breaking_artifact="A concrete scalar/point counterexample or a missing precondition."), dict(joint="J-integrity: paired inputs, targets, relations, recovery certificates and complete costs remain comparable.", assigned_to=REVIEW, attack_plan="Audit timer and all162 raw workers; independently regenerate seeded target stream and certify kP==Q; mutate k/digests/remove a row and require refusal.", breaking_artifact="A tampered record accepted or a genuine row whose independent certificate/digest/cost boundary does not reconcile."), dict(joint="J-inference: declared full-cost statistic and uncertainty support only the exact tested scope.", assigned_to=REVIEW, attack_plan="Recompute all54 paired ratios and clustered stratified bootstrap from raw times; replace candidate with identical reference data and require the strict improvement gate to fail.", breaking_artifact="A differing recomputed statistic, accepted known-false performance control, omitted censoring or expanded scope.")], blindness=dict(mutual=True, lifted_for=[]), proves_too_much=dict(objects=["Identical reference timings substituted as candidate (known to have no strict speedup).", "A known-wrong k+1 or shifted digit, corrupted target digest, and an incomplete grid."], failure_signature="No qualified speedup for identical timings; invalid certificates/digests and incomplete grids are refused.", assigned_to=REVIEW), blind_rederivation=dict(required=True, quantity="Algebraic group element and exact reference E.add call count for nonnegative a,b, including zero scalars and the final point sum; derive from the frozen group algorithm statement independently.", parameters="Same public p,a,b,N,P,Q and seeded a,b range as frozen specification; window4.", blind_from=protected, assigned_to=BLIND), procedure_deviations=[])
    producer["review_plan"] = review_plan
    reviewer["review_plan"] = review_plan
    blind_handoff["review_plan"] = review_plan
    snap_path = f"coordination/tasks/{SNAP}/snapshot_commit_receipt.json"
    snap = envelope(SNAP, "coordinator", SNAP, "Archive exact raw run observations before independent review.", "Whether reviewers receive immutable hash-bound worker and supervisor evidence.", run_paths, ["Run alone, fetch main, stage exact declared raw paths only.", "Verify published commit/parent/path hashes and leave scientific state unchanged."], [snap_path], ["Snapshot receipt verifies exact run paths and published bytes."], policy("coordinator-orchestration-code", "high"))
    ledger_path = f"coordination/tasks/{LEDGER}/ledger_commit_receipt.json"
    decision_path = f"ledger/decisions/{REVIEW_DEC}.yaml"
    evidence_path = f"ledger/evidence/{EVIDENCE}.yaml"
    claim_path = "claims/ic-target-fixed-window-3065f9.json"
    ledger = envelope(LEDGER, "coordinator", LEDGER, "Archive both independent reports and separately composed scientific records, without expanding scope.", "Whether a proposed result has completed both independent joints and durable custody.", review_paths(BLIND) + review_paths(REVIEW), ["Run alone; no producer or reviewer writes during archive.", "No official frontier or measured bound from wall time; no promotion with missing independent reviews.", "Write evidence, claim and composition decision only after both reviews; leave outcomes unwritten prospectively."], [ledger_path, decision_path, evidence_path, claim_path], ["Both reviews archived exactly; check_review_independence accepts declared sources and joint ownership.", "Claim record passes progress-fidelity and cites exact artifacts; no further official transition without its separately declared archive scope."], policy("coordinator-orchestration-code", "high"))
    tasks = [task(producer, "Run fixed paired target-generation grid", [], [SPEC, PLAN, *sources, "config/ic-target-benchmark.json"], [f"{RUN_DIR}/", f"experiments/{EXP}/reports/"], relevant=True), task(snap, "Snapshot raw IC target benchmark", [EXEC], run_paths, [f"coordination/tasks/{SNAP}/"], priority=100), task(blind_handoff, "Blind fixed-window algebra/count derivation", [EXEC, SNAP], blind_handoff["inputs"], [f"coordination/tasks/{BLIND}/"]), task(reviewer, "Independent full-cost IC benchmark audit", [EXEC, SNAP], reviewer["inputs"], [f"coordination/tasks/{REVIEW}/"]), task(ledger, "Archive independent IC benchmark review", [BLIND, REVIEW], ledger["inputs"], [f"coordination/tasks/{LEDGER}/", decision_path, evidence_path, claim_path], priority=100)]
    tasks[1]["archive"] = dict(kind="snapshot", source_task_ids=[EXEC], commit_sha=None, parent_sha=None, path_sha256={}, record_ids=[EXP, HYP, RUN, EXEC])
    tasks[-1]["archive"] = dict(kind="ledger", source_task_ids=[BLIND, REVIEW], commit_sha=None, parent_sha=None, path_sha256={}, record_ids=[EXP, HYP, BLIND, REVIEW, REVIEW_DEC, EVIDENCE])
    queue = dict(schema="crypto.autoresearch.dispatch_queue.v1", goal_id=GOAL, objective=spec["objective"], max_concurrent=2, tasks=tasks)
    validate_queue(queue)
    write_json(HERE / "execution-queue.json", queue)
    write_json(preview / "queue.json", queue)
    for h in (producer, snap, blind_handoff, reviewer, ledger):
        write_yaml(preview / f"{h['id']}.yaml", {"handoff": h})
    director_paths = [f"coordination/tasks/{DIRECTOR}/compile_report.yaml", f"coordination/tasks/{DIRECTOR}/runbook_lint.txt", f"coordination/tasks/{DIRECTOR}/task_card_lint.txt"]
    director_inputs = [SPEC, PLAN, str((preview / "specification.yaml").relative_to(ROOT)), str((preview / "trial-plan.json").relative_to(ROOT)), "tools/ic_target_benchmark.py", "config/ic-target-benchmark.json", "templates/runbook.yaml", "agents/experiment-director.md", "docs/runbook-execution.md"]
    director = envelope(DIRECTOR, "executor", DIRECTOR_SNAP, "Compile-mode experiment-director attempt for the exact prospective IC workload; run only lint, never science.", "Whether an exact judgment-free runbook/task card can be compiled before approval, or which specification field prevents clean lint.", director_inputs, ["Act as experiment-director in compile mode under director-runbook/high; no scientific trial, dispatch, API call or approval.", "Do not change canonical specification, trial plan, sources or any scientific criterion.", "Create temporary candidate runbook/card under the task directory, run actual lint commands and retain their verbatim outputs; remove unapproved candidates if clean lint cannot be obtained.", "Always produce the three declared artifacts. compile_report.yaml names candidate source text and exact source hashes if both lint commands pass, otherwise records exact specification_error and a failed/unavailable lint command without inventing LINT OK or CARD OK.", "Root may only adopt a clean candidate after exact canonical archive ownership and Coordinator approval are separately bound; do not publish a runbook or select mechanical tier from an incomplete candidate."], director_paths, ["Actual runbook lint and task-card lint command outputs are retained, including failures; report exact non-executing compile status.", "No runbook is committed unless clean lint can be established; implementation route remains available with recorded reason."], policy("director-runbook", "high"))
    dsnap_path = f"coordination/tasks/{DIRECTOR_SNAP}/snapshot_commit_receipt.json"
    dsnap = envelope(DIRECTOR_SNAP, "coordinator", DIRECTOR_SNAP, "Archive the director's exact compile/lint receipts without executing the prospective experiment.", "Whether the runbook route has real lint evidence or a named specification impediment.", director_paths, ["Run alone; exact declared paths, hashes and pushed bytes only.", "A failed compile receipt changes no scientific status and does not authorize a mechanical executor."], [dsnap_path], ["Published receipt verifies the exact compile report and verbatim lint outputs."], policy("coordinator-orchestration-code", "high"))
    director_tasks = [task(director, "Compile prospective IC mechanical runbook", [], director_inputs, [f"coordination/tasks/{DIRECTOR}/"]), task(dsnap, "Archive IC director compilation receipts", [DIRECTOR], director_paths, [f"coordination/tasks/{DIRECTOR_SNAP}/"], priority=100)]
    director_tasks[1]["archive"] = dict(kind="snapshot", source_task_ids=[DIRECTOR], commit_sha=None, parent_sha=None, path_sha256={}, record_ids=[EXP, DIRECTOR])
    director_queue = dict(schema="crypto.autoresearch.dispatch_queue.v1", goal_id=GOAL, objective="Prospective non-executing runbook compilation for fixed IC workload", max_concurrent=1, tasks=director_tasks)
    validate_queue(director_queue)
    write_json(HERE / "director-queue.json", director_queue)
    write_yaml(preview / f"{DIRECTOR}.yaml", {"handoff": director})
    write_yaml(preview / f"{DIRECTOR_SNAP}.yaml", {"handoff": dsnap})
    approval = dict(id=DEC, context="Prospective exact full-cost fixed-window IC implementation comparison under AGENTS standing user authorization (2026-09-06); not evidence or acceptance of any speedup.", decision="approve", target_ids=[EXP, HYP, EXEC], rationale=["User requested using the harness to speed up index calculus.", "Approval is prospective only after experiment_preapproval reports approvable:true for these exact bytes; source and inputs must be committed/pushed, lane lawful, then ordinary selector ready and live claim published."], evidence_refs=[], limitations=hypothesis["interpretation_limits"], next_actions=[f"Publish exact approved packet and handoffs; require newest_experiments.py --experiment {EXP} --json execution_state ready before claiming {EXEC}."], knowledge_promotion=dict(promoted=[], not_warranted="Protocol approval creates no measured evidence."), decided_by="coordinator", decided_at="2026-10-23")
    write_yaml(preview / f"{DEC}.yaml", {"coordinator_decision": approval})
    packet = dict(schema="crypto.autoresearch.preapproval_packet.v1", experiment_id=EXP, approval_decision_id=DEC, specification=SPEC, trial_plan=PLAN, queue=QUEUE, handoff=f"ledger/handoffs/{EXEC}.yaml", preview={"specification": str(preview / "specification.yaml"), "trial_plan": str(preview / "trial-plan.json"), "queue": str(preview / "queue.json"), "handoff": str(preview / f"{EXEC}.yaml")}, source_ref="origin/codex/index-calculus-optimization", lane_id=BATCH, execution_route=dict(kind="implementation", reason="The newly implemented isolated-worker driver/checker needs implementation-tier inspection and has no independently compiled LINT OK runbook/task-card receipt. No runbook is committed or mechanical executor claimed."))
    write_json(HERE / "preapproval-packet.json", packet)
    print("Drafts and prospective packet compiled; dispatcher structural validation passed. Nothing approved or run.")


if __name__ == "__main__":
    main()
