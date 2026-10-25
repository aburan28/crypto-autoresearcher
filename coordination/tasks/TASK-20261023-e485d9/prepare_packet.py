"""Prospective successor compiler: hashes and drafts only, no approval or runs."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
helper_path = ROOT / "coordination/tasks/TASK-20261023-3d7044/prepare_packet.py"
module_spec = importlib.util.spec_from_file_location("old_protocol_helpers", helper_path)
h = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(h)  # helper definitions only; never old main()
from tools.experiment_execution import GENERATED
from tools.research_dispatch import validate_queue

EXP="EXP-ICPERF-6c546e"; HYP="H-ICPERF-a2284c"; GOAL="GOAL-ICPERF-e6b6a4"
BATCH="BATCH-b2dce4"; DEC="DEC-20261023-6bcd2d"; REVIEW_DEC="DEC-20261023-122e32"
EXEC="TASK-20261023-b6cb1a"; SNAP="TASK-20261023-55a603"
REVIEW="TASK-20261023-6562b0"; LEDGER="TASK-20261023-e0567d"
RUN="RUN-ICPERF-d566af"; EV="EV-ICPERF-92c130"
HERE=Path(__file__).resolve().parent; PREVIEW=HERE/"preview"
SPEC=f"experiments/{EXP}/specification.yaml"; PLAN=f"experiments/{EXP}/trial-plan.json"
QUEUE=f"coordination/goals/{GOAL}/batches/{BATCH}/dispatch_queue.json"
RD=f"experiments/{EXP}/runs/{RUN}"
CONFIG="config/ic-target-balanced-benchmark.json"; ENV="config/ic-target-balanced-environment.json"
DRIVER="tools/ic_target_balanced_benchmark.py"
ARTIFACTS=["manifest.yaml","raw-result.json","instances.json","arms.jsonl","validation.json","balance-validation.json"]

def main():
    p=ROOT/SPEC
    if p.exists() and yaml.safe_load(p.read_text())["experiment"].get("approved_by"):
        raise SystemExit("Refusing to rewrite an approved successor")
    config=json.loads((ROOT/CONFIG).read_text())
    assert config["curve_seeds"]==[3,4,5] and config["bits"]==[12,14,16]
    assert config["solver_seeds"]==[0,1] and config["repetitions"]==3 and config["window"]==4
    assert config["m"]==2 and config["engine"]=="mitm" and config["factor_base"]=="small_x"
    assert config["accelerate"] is False and config["harvest"]=="off"
    assert config["execution_order"]=="cyclic_slots_with_reversed_orientation_per_solver_seed"
    assert config["worker_timeout_seconds"]==60 and config["bootstrap_replicates"]==5000 and config["bootstrap_seed"]==3065
    old=yaml.safe_load((ROOT/"experiments/EXP-ICPERF-3065f9/specification.yaml").read_text())["experiment"]
    spec=copy.deepcopy(old)
    spec.update(id=EXP,status="review_required",approved_by=None,frozen=False,execution_authorized=False,
                title="Held-out balanced-slot full-cost fixed-window IC target comparison",
                objective="Test complete-solve target-generator wall time on unseen curves with every treatment crossed through every execution slot.",
                designed_at="2026-10-23",supersedes_timing_design="EXP-ICPERF-3065f9; original records and native algorithm unchanged")
    sources=[DRIVER,"tools/ic_target_benchmark.py","src/crypto_autoresearcher/__init__.py"]
    sources += [str(x.relative_to(ROOT)) for x in sorted((ROOT/"src/crypto_autoresearcher/index_calculus").glob("*.py"))]
    source_hashes={x:h.sha(x) for x in sources}; inputs={x:h.sha(x) for x in (CONFIG,ENV)}
    spec["inputs"]["parameters"]=config
    spec["input_bindings"]={"source_closure":[{"path":x,"sha256":v} for x,v in source_hashes.items()],
                            "inputs":[{"path":x,"sha256":v} for x,v in inputs.items()]}
    spec["replication"].update(seeds={"curve":[3,4,5],"solver":[0,1],"target":[0]}, independent_instances=9,paired_cells=18,repetitions=3,arm_executions=162)
    spec["controls"] += ["For every exact bits/curve/solver-seed/arm, the three repetitions must occupy slots0,1,2 exactly once; solver seed1 reverses the orientation, yielding all6 permutations within each curve.","Worker environment equals committed environment lock and CPU affinity is [0] (the minimum locked allowed CPU). Preserve load before/after and pre/post process census; census is diagnostic, not proof of host-wide isolation.","Negative balance control: the old always-middle candidate schedule must fail the successor checker. Existing source tests cover this refusal; fresh reviewer independently exercises it on a scratch copy."]
    for factor in spec["variable_ledger"]["factors"]:
        if factor["name"]=="field_and_curve": factor["how"]="Fixed public generator, bits12/14/16 and unseen curve seeds3/4/5; paired arms share exact instance. No selection based on results."
        if factor["name"]=="execution_slot": factor.update(treatment="crossed",how="Within each exact curve/solver-seed, cyclic rotations across3 repetitions place every arm once in each slot. Solver seeds use opposite orientations, all6 permutations per curve. Frozen and checked, not random assignment.")
        if factor["name"]=="source_and_dependencies": factor["how"]="Hash-bound unchanged native/base worker sources plus successor driver; pre-run and every-worker environment digest must match committed lock, with actual Python/package/host/affinity metadata."
        if factor["name"]=="hardware_and_load": factor["how"]="Same locked host/environment and pinned CPU0 for all workers; pre/post load and process census recorded. Known concurrent scientific producers preclude a qualified timing conclusion; process census cannot establish global isolation."
    spec["variable_ledger"]["factors"] += [{"name":"cpu_affinity","treatment":"fixed","how":"Each worker pins to CPU0, the minimum allowed affinity in the committed environment lock; actual affinity checked."}]
    spec["preregistered_predictions"]=[{"id":"P-balanced-new-curves","quantity":"Complete-solve paired geometric speedup on held-out curve seeds3/4/5 with balanced execution slots","direction":"C-target success gate, unchanged from original prospective numerical gate","basis":"Original arithmetic mechanism and preliminary confounded timing observation; new curves have not been timed."}]
    spec["prediction_provenance"]=[{"prediction":"P-balanced-new-curves","first_recorded_in":SPEC,"written_at":"2026-10-23","data_seen":[{"path":"experiments/EXP-ICPERF-3065f9/runs/RUN-ICPERF-842b51/raw-result.json","measured":"Original bits12/14/16, curve seeds0/1/2, target-generator counters and full-solve timings. Candidate always middle-slot; no qualified causal wall-time claim."},{"path":"coordination/tasks/TASK-20261023-18b489/review_report.yaml","measured":"Independent original-grid integrity, confounded timing statistic and schedule obstruction."},{"path":"ledger/decisions/DEC-20261023-d70a08.yaml","measured":"Coordinator revised timing design; original evidence preliminary, no wall-time promotion."}],"sample_status":"out_of_sample","overlap":"New decisive scope is ONLY exact public curve seeds3/4/5; original seeds0/1/2 are seen calibration, excluded from all successor ratios/intervals. Bit sizes/algorithm are reused; this is a held-out-instance test informed by the original observation, not an independent discovery."}]
    spec["success_criterion"]=spec["success_criterion"].replace("P-target","P-balanced-new-curves")+" Additionally balance-validation must pass, the environment lock and CPU affinity must match, and no known concurrent scientific producer may contaminate timing. Load/census are reported limitations, not proof of global isolation."
    spec["falsification_criterion"]=spec["falsification_criterion"].replace("P-target","P-balanced-new-curves")
    spec["invalidation_rules"] += ["Any treatment missing an execution slot within an exact curve/solver-seed/arm group, changed orientation, environment/affinity mismatch or missing load invalidates the matched comparison."]
    spec["required_artifacts"]=[f"{RD}/{x}" for x in (*GENERATED,*ARTIFACTS)]
    spec["prior_independent_algebra"]={"report":"coordination/tasks/TASK-20261023-5301b1/review_report.yaml","scope":"Reuse unchanged native fixed-window identity and operation accounting; no new blinded algebra joint or theorem claimed."}
    spec["director_route"]={"status":"implementation","prior_compile_report":"coordination/tasks/TASK-20261023-675119/compile_report.yaml","limitation":"Original compile attempt failed real lint for absent session scope and unfinished nested-row metric mapping. This successor has no clean compiled runbook/card, so no LINT OK or mechanical tier is claimed. A fresh compile requires a separately published task."}
    h.write_yaml(ROOT/SPEC,{"experiment":spec})
    approved=copy.deepcopy(spec); approved.update(status="approved",approved_by=DEC,frozen=True,execution_authorized=True)
    h.write_yaml(PREVIEW/"specification.yaml",{"experiment":approved})
    trial=dict(id="balanced-heldout-full-grid",run_id=RUN,depends_on=[],argv=[".venv/bin/python",DRIVER,"run","--out","{run_dir}"],check_argv=[".venv/bin/python",DRIVER,"check","--run-dir","{run_dir}"],artifacts=ARTIFACTS,memory_mb=1024,watchdog_seconds=1200,watchdog_reason="Protect stuck parent/child group; retain incomplete observations without a scientific negative.",parameters=config,seed=3065)
    plan=dict(schema="crypto.autoresearch.trial_plan.v1",experiment_id=EXP,hypothesis_id=HYP,task_id=EXEC,approved_by=DEC,frozen=True,specification=SPEC,specification_sha256=h.sha(str((PREVIEW/"specification.yaml").relative_to(ROOT))),queue=QUEUE,source_sha256=source_hashes,input_sha256=inputs,trials=[trial])
    h.write_json(PREVIEW/"trial-plan.json",plan)
    draft=copy.deepcopy(plan); draft.update(frozen=False,approved_by=None,specification_sha256=h.sha(SPEC)); h.write_json(ROOT/PLAN,draft)
    runpaths=spec["required_artifacts"]
    producer=h.envelope(EXEC,"executor",SNAP,"Execute exactly the approved held-out balanced-slot IC comparison through the supervisor.","Whether matched complete solve time improves with slot balanced and environment locked.",[SPEC,PLAN,CONFIG,ENV],["No adaptive workload or extra curves; no competing known scientific producer.","Publish/fetch exact live claim and all bound source/config bytes before supervisor launch.","Retain all162 outcomes and both checker outputs; observations only."],runpaths,["Complete declared artifacts or preserve exact failure; publish raw results before a separate inspected run report."],h.policy("executor-implementation","medium"),runs=1)
    producer["execution"]=dict(mode="experiments",kind="run",experiment_id=EXP,trial_plan=PLAN,trial_plan_sha256=h.sha(str((PREVIEW/"trial-plan.json").relative_to(ROOT))),approved_by=DEC)
    reviewpaths=[f"coordination/tasks/{REVIEW}/review_report.yaml",f"coordination/tasks/{REVIEW}/derivation.md"]
    blindfrom=[f"{RD}/validation.json",f"{RD}/balance-validation.json",f"experiments/{EXP}/reports/","tools/ic_target_benchmark.py"]
    reviewplan=dict(claim_under_review="Any complete-solve wall-time advantage on the held-out balanced162-worker grid; no successor measurements exist yet.",coordinator_prior="Unchanged arithmetic should preserve targets and operation savings. Prior timings were confounded; balanced new curves may reduce, remove or reverse that observed wall-time contrast.",joints=[dict(joint="J-integrity: exact held-out grid, balanced slots, environment/affinity, target/relation/certificate matches and complete costs.",assigned_to=REVIEW,attack_plan="Inspect all raw rows and successor schedule/affinity code, verify source/config locks and certificates, mutate slot/target/row/config in scratch and require refusals. Reuse prior independent unchanged-base-worker audit by matching its source hash; do not read base analysis source protected from blind metric derivation.",breaking_artifact="Accepted confounded/tampered input or unreconciled full-cost/certificate/environment boundary."),dict(joint="J-inference: independently recomputed raw-only statistic/uncertainty and exact scoped conclusion.",assigned_to=REVIEW,attack_plan="Before producer summaries/source analysis, derive all54 ratios and clustered5000 seed3065 interval from raw only; check slot crossing and per-slot heterogeneity. Identical reference candidate must fail strict advantage. Assess host-load limitations without claiming process census proves isolation.",breaking_artifact="Mismatched statistic, accepted known-false advantage, hidden censoring or unsupported causal scope.")],blindness=dict(mutual=True,lifted_for=[]),proves_too_much=dict(objects=["Original always-middle candidate schedule.","Candidate times replaced by mean of references (strict advantage known false).","Wrong recovered k, target digest, missing row or environment/affinity record."],failure_signature="Balance/certificate/config changes refused; identical-time data cannot qualify.",assigned_to=REVIEW),blind_rederivation=dict(required=True,quantity="Paired geometric complete-solve speedup, A/A factor and curve-clustered stratified percentile interval, derived independently from the frozen definition and raw rows only.",parameters="Held-out bits12/14/16, seeds3/4/5, solver seeds0/1,3 repetitions,5000 resamples seed3065; no performance rerun.",blind_from=blindfrom,assigned_to=REVIEW),procedure_deviations=[])
    producer["review_plan"]=reviewplan
    reviewer=h.envelope(REVIEW,"reviewer",LEDGER,"Independently verify the held-out balanced-slot integrity and raw-only timing inference.","Whether any apparent gain survives slot/environment controls, independent certificates and raw metric rederivation.",[SPEC,PLAN,CONFIG,ENV,DRIVER,f"{RD}/raw-result.json",f"{RD}/arms.jsonl",f"{RD}/instances.json","coordination/tasks/TASK-20261023-5301b1/review_report.yaml","coordination/tasks/TASK-20261023-18b489/review_report.yaml"],["Fresh independent xhigh session; no inherited producer conversation.","Do not read any blind_from path, including base benchmark analysis source or producer validation summaries, at any time. Recompute raw statistics independently; use prior committed unchanged-worker audit for that dependency.","No science reruns. Offline arithmetic/certificate/scratch checker controls only.","Own exactly J-integrity and J-inference; attest exact sources, blind_from_respected and known-false controls."],reviewpaths,["Own independent raw calculation and actual refusal controls recorded; report both joint verdicts and limitations."],h.policy("review-adversarial","xhigh",True)); reviewer["review_plan"]=reviewplan
    sp=f"coordination/tasks/{SNAP}/snapshot_commit_receipt.json"
    snap=h.envelope(SNAP,"coordinator",SNAP,"Archive exact balanced raw receipts before independent review.","Immutable exact raw/supervisor/checker custody.",runpaths,["Run alone, exact paths/hashes/pushed bytes; no evidence transition."],[sp],["Exact snapshot receipt verifies against Git."],h.policy("coordinator-orchestration-code","high"))
    lp=f"coordination/tasks/{LEDGER}/ledger_commit_receipt.json"; dp=f"ledger/decisions/{REVIEW_DEC}.yaml"; ep=f"ledger/evidence/{EV}.yaml"; cp="claims/ic-target-balanced-6c546e.json"
    ledger=h.envelope(LEDGER,"coordinator",LEDGER,"Compose and archive independent successor review and scoped claim records.","Whether reviewed observations justify only the exact tested engineering conclusion.",reviewpaths,["Run alone; leave outcomes unwritten until review returns.","No frontier, measured bound, production-curve or asymptotic claim; required progress-fidelity and independence checks."],[lp,dp,ep,cp],["Exact review custody, independent review checks, claim schema and composed decision reconcile."],h.policy("coordinator-orchestration-code","high"))
    tasks=[h.task(producer,"Run balanced held-out IC target grid",[],[SPEC,PLAN,*sources,CONFIG,ENV],[f"{RD}/",f"experiments/{EXP}/reports/"],relevant=True),h.task(snap,"Archive balanced raw IC observations",[EXEC],runpaths,[f"coordination/tasks/{SNAP}/"],priority=100),h.task(reviewer,"Fresh balanced IC integrity/inference review",[EXEC,SNAP],reviewer["inputs"],[f"coordination/tasks/{REVIEW}/"]),h.task(ledger,"Archive balanced IC review composition",[REVIEW],reviewpaths,[f"coordination/tasks/{LEDGER}/",dp,ep,cp],priority=100)]
    tasks[1]["archive"]=dict(kind="snapshot",source_task_ids=[EXEC],commit_sha=None,parent_sha=None,path_sha256={},record_ids=[EXP,HYP,RUN,EXEC])
    tasks[-1]["archive"]=dict(kind="ledger",source_task_ids=[REVIEW],commit_sha=None,parent_sha=None,path_sha256={},record_ids=[EXP,HYP,REVIEW,REVIEW_DEC,EV])
    queue=dict(schema="crypto.autoresearch.dispatch_queue.v1",goal_id=GOAL,objective=spec["objective"],max_concurrent=1,tasks=tasks)
    validate_queue(queue); h.write_json(HERE/"execution-queue.json",queue); h.write_json(PREVIEW/"queue.json",queue)
    for item in (producer,snap,reviewer,ledger): h.write_yaml(PREVIEW/f"{item['id']}.yaml",{"handoff":item})
    approval=dict(id=DEC,decision="approve",context="Prospective held-out balanced successor under standing user authorization; approval only after exact preapproval passes.",target_ids=[EXP,HYP,EXEC],rationale=["Correct perfect candidate/middle-slot confounding on unseen curves; unchanged native algorithm and numerical thresholds.","Source and config are already pushed; exact draft/lane/approval publication and ordinary ready selector/live claim still required."],evidence_refs=["DEC-20261023-d70a08"],limitations=["Protocol approval is not evidence; host census diagnostic only; no frontier or bound."],next_actions=[f"Publish exact packet, require ready selector, claim {EXEC} before supervisor run."],knowledge_promotion=dict(promoted=[],not_warranted="Prospective protocol, no successor observations."),decided_by="coordinator",decided_at="2026-10-23")
    h.write_yaml(PREVIEW/f"{DEC}.yaml",{"coordinator_decision":approval})
    packet=dict(schema="crypto.autoresearch.preapproval_packet.v1",experiment_id=EXP,approval_decision_id=DEC,specification=SPEC,trial_plan=PLAN,queue=QUEUE,handoff=f"ledger/handoffs/{EXEC}.yaml",preview={"specification":str(PREVIEW/"specification.yaml"),"trial_plan":str(PREVIEW/"trial-plan.json"),"queue":str(PREVIEW/"queue.json"),"handoff":str(PREVIEW/f"{EXEC}.yaml")},source_ref="origin/codex/index-calculus-optimization",lane_id=BATCH,execution_route=dict(kind="implementation",reason="New balanced successor has no clean director-compiled runbook/card. Prior actual failed compile retained at coordination/tasks/TASK-20261023-675119/compile_report.yaml; implementation-tier route only, no nonexistent LINT OK."))
    h.write_json(HERE/"preapproval-packet.json",packet)
    print("Successor draft/preview compiled; queue structural validation passed. No approval or science.")

if __name__=="__main__": main()
