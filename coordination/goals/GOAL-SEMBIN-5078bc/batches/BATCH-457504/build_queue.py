#!/usr/bin/env python3
"""Author BATCH-457504's dispatch queue -- the evidence review of RUN-SEMBIN-b6eb9f.

WHY THIS BATCH EXISTS. EXP-SEMBIN-c2c312 ran, produced a complete artifact set,
and has no evidence record and no decision. Its objective is
GOAL-SEMBIN-5078bc's FIRST completion criterion: state the map between Semaev's
d_F4 and GOAL-DREG-001's Macaulay-rank d_reg/D on identical instances, so that
campaign's degree-5/6 measurements can be read as bearing on Assumption 1 or
explicitly as not bearing on it. Either answer discharges the criterion; an
unstated map does not.

WHY IT IS A SECOND BATCH AND NOT MORE TASKS ON BATCH-9d649f. That batch is
drained -- 36 completed, 2 cancelled -- and it is a different round with its own
committed review plan. A new round gets a new batch and a new plan.

WHY THREE REVIEWERS. The round can move H-SEMBIN-112e2e and can discharge a
completion criterion, so AGENTS.md "Review architecture" applies: joints
enumerated, one owner each, blindness declared, proves-too-much filled with
structured objects, and a blind re-derivation of the load-bearing quantity. The
plan at coordination/review/sembin-20260921-457504/review-plan.yaml was committed
at 43e99599f, BEFORE this queue existed and before any reviewer ran.
"""

import collections
import json
import pathlib

od = collections.OrderedDict

GOAL = "GOAL-SEMBIN-5078bc"
BATCH = "BATCH-457504"
BASE = f"coordination/goals/{GOAL}/batches/{BATCH}"
REVIEW = "coordination/review/sembin-20260921-457504"
ROUND = "REVIEW-SEMBIN-20260921-457504"

EXP = "EXP-SEMBIN-c2c312"
RUN = "RUN-SEMBIN-b6eb9f"
HYP = "H-SEMBIN-112e2e"
RUNDIR = f"experiments/{EXP}/runs/{RUN}"

J1 = "TASK-20260921-f2d82f"        # validator: run validity and controls
J2 = "TASK-20260921-411a9d"        # red team: metric substitution + the map
J3 = "TASK-20260921-f1e5bd"        # validator: blind re-derivation
SNAPSHOT = "TASK-20260921-064ae9"  # archive the three reviewer packages
COMPOSE = "TASK-20260921-a9f304"   # coordinator: analysis + EV + DEC
LEDGER = "TASK-20260921-bd5f2e"    # ledger archive

EVIDENCE = "EV-SEMBIN-c6e9ad"
DECISION = "DEC-20260921-2c62d7"

# Every reviewer is blind to these. The first two are the other reviewers'
# directories; the third is the Coordinator's own recorded expectation, which is
# the one thing most likely to turn a review into an echo.
def blind_from(own: str) -> list[str]:
    others = [t for t in (J1, J2, J3) if t != own]
    return [f"{BASE}/{t}" for t in others] + [
        f"{REVIEW}/review-plan.yaml#coordinator_prior",
    ]


REVIEWER_INFERENCE = od([
    ("policy", "review-adversarial"),
    ("reasoning_effort", None),
    ("fallback_allowed", True),
    ("fallback_note",
     "No adapter backend is credentialed in this checkout, so the runtime-native "
     "binding permitted by core rule 16 is the only route. Declared up front. "
     "model_verified will be false throughout this round and every report says so."),
    ("degraded_allowed", False),
    ("independent_session_required", True),
])

BUDGET = od([
    ("wall_clock_seconds", 5400),
    ("memory_gb", 2),
    ("maximum_runs", 0),
])

tasks: list[od] = []

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", J1),
    ("title", "J-1: is RUN-SEMBIN-b6eb9f valid, and are its four controls satisfied as SPECIFIED?"),
    ("role", "validator"),
    ("state", "queued"),
    ("priority", 80),
    ("review_required", False),
    ("depends_on", []),
    ("read_scope", [f"experiments/{EXP}", f"{REVIEW}/review-plan.yaml", "ledger", "templates"]),
    ("write_scope", [f"{BASE}/{J1}"]),
    ("artifact_paths", [f"{BASE}/{J1}/report.md", f"{BASE}/{J1}/findings.json",
                        f"{BASE}/{J1}/attestation.yaml"]),
    ("archived_by", SNAPSHOT),
    ("handoff", od([
        ("objective",
         "Establish whether the run is valid as its own contract defines validity, and "
         "whether each declared control was satisfied as written rather than as later "
         "reframed. Report on J-1 only."),
        ("uncertainty_reduced",
         "whether anything downstream of this run may be interpreted at all"),
        ("inputs", [f"{RUNDIR}/manifest.yaml", f"experiments/{EXP}/specification.yaml",
                    f"{RUNDIR}/workerA/cells/results.jsonl",
                    f"{RUNDIR}/workerB/cells/results.jsonl",
                    f"{RUNDIR}/workerC/cells/results.jsonl",
                    f"{RUNDIR}/heavy/cells/results.jsonl",
                    f"{RUNDIR}/heavy_closure/cells/results.jsonl",
                    f"{REVIEW}/review-plan.yaml"]),
        ("constraints", [
            "Work from the RAW records. The summary is a convenience, not the datum.",
            "THE HIGHEST-VALUE ITEM ON THIS JOINT is the duplicate-record audit. The run "
            "discloses that two processes (pids 9160 and 9336) both appended to "
            "workerB/cells/results.jsonl and that summarize.py resolves duplicates by "
            "'first completed record wins'. Find every duplicated (instance, instrument) "
            "pair and report whether ANY pair is DISCORDANT -- different d_F4, different "
            "closure_D, different per-degree profile. 'First wins' is safe if and only if "
            "no pair disagrees, and nothing in the package states whether any did. A "
            "discordant pair would mean the instrument is nondeterministic, which the "
            "contract's own instrument-identity control says voids the comparison.",
            "BYTE IDENTITY: the contract requires that both instruments' recorded input "
            "hashes be COMPARED. The manifest instead records them 'equal by "
            "construction'. Determine whether any per-record comparison exists in the raw "
            "data. If equality is only asserted, state concretely how it could fail "
            "silently -- that is what the control is for.",
            "The baseline control at (13,4,4,4) rests on ONE instance with "
            "closure_measured = 1. Say plainly how much of the calibration rests on a "
            "single instance, without deciding whether that invalidates anything.",
            "Check the three invalidation rules other than the matched-null one: the "
            "structural shape check (n(t-1) equations in n(t-2)+kt variables of degree 3), "
            "known-false returning 2 from BOTH instruments, and both invalid inputs "
            "rejected by the generator.",
            "Check the arithmetic: the report claims 126 instances recorded, 314 raw "
            "records, 44 duplicates resolved. Say whether those three numbers are "
            "mutually consistent and, if not, what the true counts are.",
            "AN INFRASTRUCTURE OUTCOME IS NOT A RESULT. Unreached and memory-capped cells "
            "say nothing about any degree (AGENTS.md rule 5). Verify they are recorded as "
            "resource facts and never folded into a measurement.",
            "Report on J-1 ONLY. You cannot see the other joints and a whole-claim verdict "
            "from you would be an opinion formed from a fraction of the evidence.",
            "You are BLIND to the other two reviewers' directories and to the review "
            "plan's coordinator_prior block. Do not read them; attest to what you read.",
        ]),
        ("deliverables", [
            "report.md -- findings, each tied to the raw file and record it rests on",
            "findings.json -- machine-readable: per control, verdict in "
            "{satisfied_as_specified, satisfied_differently, not_satisfied, unevaluable}; "
            "plus the duplicate audit as an explicit list of discordant pairs (possibly "
            "empty) and the instance-count reconciliation",
            "attestation.yaml -- joints_owned [J-1], exactly what you read, what you did "
            "not read, resolved model, model_verified false, and any independence "
            "qualification you must disclose",
        ]),
        ("inference", REVIEWER_INFERENCE),
        ("budget", BUDGET),
        ("completion_gate", [
            "every one of the four contract controls given one of the four verdicts",
            "the duplicate audit reports an explicit discordant-pair list, even if empty",
            "a single overall validity verdict for the run, with its reason",
            "no interpretation of what the measured degrees MEAN -- that is J-2's and the "
            "composition's, not yours",
        ]),
        ("blind_from", blind_from(J1)),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", J2),
    ("title", "J-2: was the contract's quantity measured, and was the map measured or argued?"),
    ("role", "red-team"),
    ("state", "queued"),
    ("priority", 80),
    ("review_required", False),
    ("depends_on", []),
    ("read_scope", [f"experiments/{EXP}", f"{REVIEW}/review-plan.yaml", "ledger",
                    "inputs/SEMAEV-2015-310", "knowledge", "templates"]),
    ("write_scope", [f"{BASE}/{J2}"]),
    ("artifact_paths", [f"{BASE}/{J2}/report.md", f"{BASE}/{J2}/objections.json",
                        f"{BASE}/{J2}/attestation.yaml"]),
    ("archived_by", SNAPSHOT),
    ("handoff", od([
        ("objective",
         "Try to falsify the run's central claim: that it has settled the map between the "
         "two degree statistics. Report on J-2 and on the proves-too-much control."),
        ("uncertainty_reduced",
         "whether this run discharges GOAL-SEMBIN-5078bc's first completion criterion or "
         "only appears to"),
        ("inputs", [f"experiments/{EXP}/specification.yaml", f"{RUNDIR}/task-report.md",
                    f"{RUNDIR}/manifest.yaml", f"{RUNDIR}/results-table.json",
                    f"{RUNDIR}/summary.json",
                    f"{RUNDIR}/NOTES-deviations-and-limitations.md",
                    f"{REVIEW}/review-plan.yaml",
                    "ledger/hypotheses/H-SEMBIN-112e2e.yaml",
                    f"ledger/goals/{GOAL}.yaml"]),
        ("constraints", [
            "START WITH THE METRIC. The contract's metrics.primary names "
            "`D_macaulay_rank_statistic` and `separation_D_minus_d_F4`. The report "
            "presents `closure_D` and `closure_D - d_F4`. Establish whether closure_D is "
            "the contract's D, a different quantity, or a third thing; and whether the "
            "substitution is disclosed anywhere as a deviation. The run states its seven "
            "deviations are 'all for cost, none for content'.",
            "THEN ATTACK THE CENTRAL CLAIM, which is that DREG's statistic is not the "
            "quantity Assumption 1 bounds because its degree is an INPUT while d_F4 is an "
            "OUTPUT. Is that established BY THE MEASUREMENT, or is it a definitional "
            "remark that needed no experiment? Build the strongest case that the run did "
            "NOT settle the map.",
            "THEN BUILD THE OPPOSITE CASE as strongly: what, if anything, does measuring "
            "both instruments on byte-identical systems add that the definitional remark "
            "alone does not? Report both cases and say which is stronger and why. A "
            "red team that only prosecutes is not measuring the claim.",
            "THE FALSIFICATION CRITERION. The contract says 'D - d_F4 = 0 on every "
            "measured instance including the off-diagonal cells refutes the hypothesis in "
            "the direction that matters most: the two statistics would then be the same "
            "quantity here, and GOAL-DREG-001's degree-5/6 measurements WOULD be in "
            "tension with Assumption 1.' Under the D actually measured, does that "
            "inference go through? State whether the criterion is sound, and if not, "
            "exactly where it conflates two quantities.",
            "RUN THE PROVES-TOO-MUCH CONTROL. It is assigned to you and its four objects "
            "are declared in the plan with the signature a correct argument must show on "
            "each. You MUST compute one number: OF THE 9 INSTANCES SUPPORTING THE MAP, HOW "
            "MANY ARE UNSATISFIABLE (unit ideal, quotient dimension 0)? The run reports 35 "
            "of 43 completed traces are unit-ideal, where any two degree statistics agree "
            "for reasons unrelated to the map. If most or all of the 9 are unit-ideal, the "
            "identity is asserted mainly where agreement is forced.",
            "CHECK FOR LEAKAGE IN BOTH DIRECTIONS. The contract's interpretation_limits "
            "forbid this run bearing on Assumption 1 at all. Does the report respect that, "
            "or does it drift into supporting or undermining it?",
            "Do not re-run the experiment and do not launch any measurement. maximum_runs "
            "is 0. Exact finite recomputation from committed records is fine.",
            "You are BLIND to the other two reviewers' directories and to the plan's "
            "coordinator_prior block.",
        ]),
        ("deliverables", [
            "report.md -- the metric finding, both cases on the central claim with a "
            "verdict on which is stronger, the falsification-criterion analysis, and the "
            "proves-too-much control with its four objects answered",
            "objections.json -- machine-readable: each objection with severity in "
            "{fatal, material, minor}, what would resolve it, and whether it is a defect "
            "of the RUN or of the CONTRACT; plus the unit-ideal count among the 9",
            "attestation.yaml -- joints_owned [J-2], what you read and did not read, "
            "resolved model, model_verified false, independence qualifications",
        ]),
        ("inference", REVIEWER_INFERENCE),
        ("budget", BUDGET),
        ("completion_gate", [
            "a verdict on whether the contract's declared primary metric was measured",
            "both the prosecution and the defence of the central claim, with a reasoned "
            "choice between them",
            "the unit-ideal count among the 9 map-supporting instances, computed",
            "all four proves-too-much objects answered against their declared signatures",
            "every objection classified as a defect of the run or of the contract",
        ]),
        ("blind_from", blind_from(J2)),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", J3),
    ("title", "J-3: blind re-derivation of d_F4, closure_D and the separation from raw records"),
    ("role", "validator"),
    ("state", "queued"),
    ("priority", 80),
    ("review_required", False),
    ("depends_on", []),
    ("read_scope", [f"experiments/{EXP}/specification.yaml", f"{RUNDIR}/workerA",
                    f"{RUNDIR}/workerB", f"{RUNDIR}/workerC", f"{RUNDIR}/heavy",
                    f"{RUNDIR}/heavy_closure", "inputs/SEMAEV-2015-310",
                    f"{REVIEW}/review-plan.yaml"]),
    ("write_scope", [f"{BASE}/{J3}"]),
    ("artifact_paths", [f"{BASE}/{J3}/report.md", f"{BASE}/{J3}/rederived.json",
                        f"{BASE}/{J3}/rederive.py", f"{BASE}/{J3}/attestation.yaml"]),
    ("archived_by", SNAPSHOT),
    ("handoff", od([
        ("objective",
         "Recompute d_F4, closure_D and their separation per instance from the raw "
         "records and the definitions alone, then and only then compare against the "
         "producer's numbers."),
        ("uncertainty_reduced",
         "whether the headline separation is a property of the systems or of one "
         "implementation"),
        ("inputs", [f"experiments/{EXP}/specification.yaml",
                    f"{RUNDIR}/workerA/cells/results.jsonl",
                    f"{RUNDIR}/workerB/cells/results.jsonl",
                    f"{RUNDIR}/workerC/cells/results.jsonl",
                    f"{RUNDIR}/heavy/cells/results.jsonl",
                    f"{RUNDIR}/heavy_closure/cells/results.jsonl",
                    "inputs/SEMAEV-2015-310/paper_fulltext.md"]),
        ("constraints", [
            "THIS IS A RE-DERIVATION, NOT A REPLICATION. Write your own implementation "
            "from the DEFINITIONS. Recomputing from the producer's summarizer would "
            "reproduce a wrong-but-self-consistent implementation faithfully, which is "
            "exactly the failure validation cannot see.",
            "DO NOT READ, at any point: summary.json, task-report.md, results-table.json, "
            "code/summarize.py, NOTES-deviations-and-limitations.md, or the `result` and "
            "`controls` blocks of manifest.yaml. They are your blind_from set. Compare "
            "against summary.json ONLY at the very end, after rederived.json is written, "
            "and say in your report that you did so in that order.",
            "d_F4 is Semaev's: the maximal total degree of a polynomial occurring before "
            "F4 terminates, WITH the trailing 'No pairs to reduce' steps excluded. The "
            "exclusion is the whole subtlety -- compute and report BOTH the naive maximum "
            "and the Semaev-excluded value, per instance, so the effect of the exclusion "
            "is visible rather than buried.",
            "closure_D is the smallest degree cap at which the degree-capped Boolean "
            "closure is already a Groebner basis. Take it from the per-degree closure "
            "profiles.",
            "REPORT THE TWO TAIL CHECKS THE CONTRACT ASKS FOR AND THE PACKAGE DOES NOT "
            "CLEARLY ANSWER. (i) Every instance where the two statistics AGREE but the "
            "per-degree PROFILES differ -- the contract calls numerical agreement for "
            "different reasons 'the dangerous case', and it is the fibre the objective "
            "says created the ambiguity. (ii) The degrees at which F4 reported no pairs "
            "against the degrees at which the Macaulay block gained rank -- the contract's "
            "predicted mechanism for a separation that did not appear.",
            "Report per instance, not in aggregate. An average would hide the cell that "
            "matters, which the contract's own tail_checks say explicitly.",
            "If you cannot recompute a quantity for some instance, say so and say why. A "
            "gap reported is worth more than a number guessed.",
            "You are BLIND to the other two reviewers' directories and to the plan's "
            "coordinator_prior block.",
        ]),
        ("deliverables", [
            "rederive.py -- your own implementation, runnable, reading only raw records",
            "rederived.json -- per instance: naive d_F4, Semaev-excluded d_F4, closure_D, "
            "separation, and the two tail checks",
            "report.md -- your numbers, then the comparison against the producer's, in "
            "that order, with every disagreement localised to a named instance",
            "attestation.yaml -- joints_owned [J-3], your blind_from list and confirmation "
            "you did not read it before writing rederived.json, resolved model, "
            "model_verified false",
        ]),
        ("inference", REVIEWER_INFERENCE),
        ("budget", BUDGET),
        ("completion_gate", [
            "rederived.json written BEFORE summary.json was opened, and the report says so",
            "both the naive and the Semaev-excluded d_F4 reported per instance",
            "both tail checks answered, per instance",
            "every disagreement with the producer localised to a named instance and "
            "attributed to one of two named implementations",
        ]),
        ("blind_from", blind_from(J3)),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", SNAPSHOT),
    ("title", "Snapshot-archive the three reviewer packages before composition reads them"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 70),
    ("review_required", False),
    ("depends_on", [J1, J2, J3]),
    ("read_scope", [f"{BASE}/{J1}", f"{BASE}/{J2}", f"{BASE}/{J3}",
                    f"{BASE}/archives/{SNAPSHOT}"]),
    ("write_scope", [f"{BASE}/archives/{SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [J1, J2, J3]),
        ("record_ids", [ROUND, EXP, RUN]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_first"),
        ("binding_mode_note",
         "content_first: a filed review report is immutable and nothing reranks it, so "
         "binding the declared hashes at HEAD is the stricter choice and catches an "
         "in-place edit to a report after it was filed. Note for future archives in this "
         "goal: content_first must NEVER be used for a shared append-only file such as "
         "tools/run_supersession_registry.yaml -- that is the defect CORR-20260921-f5e9c4 "
         "repairs in BATCH-9d649f, which left this goal undispatchable."),
    ])),
    ("handoff", od([
        ("objective",
         "Commit the three reviewer packages exactly as filed, so the composition reads "
         "hash-bound bytes rather than working-tree state."),
        ("uncertainty_reduced", "none; durability and reviewability"),
        ("inputs", [f"{BASE}/{J1}", f"{BASE}/{J2}", f"{BASE}/{J3}"]),
        ("constraints", [
            "stage only declared paths; runs alone",
            "commit message names the task id and every record id",
            "fetch origin/main and MERGE it before committing; never rebase pushed records",
            "If the reviewer packages were already landed by tools/producer_landing.py, "
            "stage only this receipt and say so in it, as TASK-20260916-92128f's receipt "
            "does. That is the expected state under the CORR-20260921-942a62 remedy.",
            "Record any independence qualification a reviewer disclosed in its "
            "attestation. An undisclosed sibling read discovered later is far worse than "
            "one written down here.",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "executor-mechanical"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As the reviewers' cards."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([("wall_clock_seconds", 900), ("memory_gb", 1), ("maximum_runs", 0)])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "every reviewer's disclosed independence qualification recorded in the receipt",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", COMPOSE),
    ("title", "Compose the round: score every prior, write analysis, evidence and decision"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 65),
    ("review_required", False),
    ("depends_on", [SNAPSHOT]),
    ("read_scope", [f"{BASE}", REVIEW, f"experiments/{EXP}", "ledger", "knowledge",
                    "templates", "docs"]),
    ("write_scope", [f"experiments/{EXP}/analysis.md", f"{BASE}/{COMPOSE}"]),
    ("artifact_paths", [f"experiments/{EXP}/analysis.md",
                        f"{BASE}/{COMPOSE}/scored-priors.json",
                        f"{BASE}/{COMPOSE}/evidence-draft.yaml",
                        f"{BASE}/{COMPOSE}/decision-draft.yaml"]),
    ("why_this_task_drafts_rather_than_writes_the_ledger_records",
     "research_dispatch.py requires a LEDGER ARCHIVE to own an exact artifact under "
     "ledger/decisions/, and it is right to: a decision authored by one task and "
     "committed by another has a window in which it exists and is not official. So this "
     "task drafts both records inside its own directory and TASK-20260921-bd5f2e writes "
     "and commits the official ones. Same split as GOAL-SEMBIN-fcb7a2's "
     "TASK-20260916-a8e5b5 / TASK-20260916-d4fb62 pair, where it worked."),
    ("archived_by", LEDGER),
    ("handoff", od([
        ("objective",
         "Compose three blinded reviews into one official reading of RUN-SEMBIN-b6eb9f, "
         "and state whether GOAL-SEMBIN-5078bc's first completion criterion is met."),
        ("uncertainty_reduced",
         "whether GOAL-DREG-001's degree-5/6 Macaulay measurements bear on Semaev's "
         "Assumption 1"),
        ("inputs", [f"{BASE}/{J1}/report.md", f"{BASE}/{J2}/report.md",
                    f"{BASE}/{J3}/report.md", f"{BASE}/{J1}/findings.json",
                    f"{BASE}/{J2}/objections.json", f"{BASE}/{J3}/rederived.json",
                    f"{REVIEW}/review-plan.yaml", f"experiments/{EXP}/specification.yaml",
                    f"{RUNDIR}/manifest.yaml", f"ledger/goals/{GOAL}.yaml",
                    f"ledger/hypotheses/{HYP}.yaml"]),
        ("constraints", [
            "SCORE EVERY ONE OF THE SEVEN PRIORS in the plan as confirmed / refuted / "
            "untested, and record the refutations AT LEAST AS PROMINENTLY as the "
            "confirmations. The plan names P-6 as the one the Coordinator most expected "
            "to lose; if it lost, say so first.",
            "analysis.md is separated STRICTLY into Observation / Comparison / Inference / "
            "Limitation. An inference in the observation section is the defect this "
            "separation exists to prevent.",
            "claim_tier is CAPPED AT toy and may not exceed it. The contract declares tier "
            "toy, n <= 21, N <= 60, no correspondence; the paper's conclusion needs "
            "n = 409 and 571. No transfer to cryptographic n may be claimed or implied.",
            "The evidence record is scoped to COMMENSURABILITY ONLY. The contract's "
            "interpretation_limits forbid this run bearing on Assumption 1 or Assumption 2 "
            "or any deployed curve, in either direction, and the evidence record must not "
            "quietly exceed that.",
            "If the direction is `weakens` or `contradicts`, fill the `obstruction` block "
            "-- the quantity, its measured value with units and error bars, the runs it is "
            "read from, and the scope those runs cover -- and then fill its "
            "`resource_check`, which asks which theory takes that measurement as its "
            "HYPOTHESIS rather than its refutation. A null resource_check blocks the "
            "decision; `examined: true` recording that none was found is complete.",
            "Choose exactly ONE transition: replicate | expand | refine | support | "
            "weaken | reject_scoped | inconclusive. `pause` is not available -- goals are "
            "never paused and this program removed it. `support` requires that the "
            "hypothesis's PREDICTED STRICTNESS was observed; it was not. `reject_scoped` "
            "requires a checkable refutation artifact or replicated empirical evidence, "
            "never one unreplicated empirical-only run.",
            "STATE EXPLICITLY whether GOAL-SEMBIN-5078bc's completion criterion 1 is met, "
            "on which of its two branches, and why. The criterion accepts either 'bearing "
            "on Assumption 1' or 'explicitly not bearing on it'; an UNSTATED map does not "
            "satisfy it. Do not claim the criterion met if J-2 found the map argued rather "
            "than measured.",
            "Fill knowledge_promotion. If nothing is promoted, give one concrete line of "
            "why, never 'n/a'.",
            "Update H-SEMBIN-112e2e's status, or state explicitly and with reasons that it "
            "does not move. Its predicted strictness was not observed and the quantity it "
            "named may never have been measured; both bear on this.",
            "Any departure from the review plan goes in `procedure_deviations` on the "
            "decision rather than being quietly absorbed.",
            "This task WRITES; it does not commit. TASK-20260921-bd5f2e owns the commit.",
        ]),
        ("deliverables", ["analysis.md", "scored-priors.json",
                          f"evidence-draft.yaml (becomes {EVIDENCE})",
                          f"decision-draft.yaml (becomes {DECISION})",
                          f"the {HYP} status change stated in the decision draft, for the "
                          "ledger archive to apply"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As the reviewers' cards."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([("wall_clock_seconds", 5400), ("memory_gb", 2), ("maximum_runs", 0)])),
        ("completion_gate", [
            "all seven priors scored, refutations recorded at least as prominently",
            "analysis.md strictly separated into the four sections",
            "exactly one transition chosen, with claim_tier at or below toy",
            "an explicit verdict on completion criterion 1 and its branch",
            "knowledge_promotion filled, with a concrete line if nothing is promoted",
            "no git command run",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", LEDGER),
    ("title", "Ledger-archive the evidence record, decision and analysis"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 60),
    ("review_required", False),
    ("depends_on", [COMPOSE]),
    ("read_scope", [f"{BASE}", REVIEW, f"experiments/{EXP}", "ledger", "templates"]),
    ("write_scope", [f"{BASE}/archives/{LEDGER}",
                     f"ledger/evidence/{EVIDENCE}.yaml",
                     f"ledger/decisions/{DECISION}.yaml",
                     f"ledger/hypotheses/{HYP}.yaml"]),
    ("artifact_paths", [f"{BASE}/archives/{LEDGER}/ledger-receipt.json",
                        f"ledger/evidence/{EVIDENCE}.yaml",
                        f"ledger/decisions/{DECISION}.yaml"]),
    ("archive", od([
        ("kind", "ledger"),
        ("source_task_ids", [COMPOSE]),
        ("record_ids", [DECISION, EVIDENCE, ROUND, EXP, HYP, GOAL]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_first"),
        ("binding_mode_note",
         "content_first: every path this archive binds is write-once -- an evidence "
         "record, a decision, an analysis -- so binding at HEAD is the stricter choice. "
         "It does NOT stage the goal head, which is what would have required "
         "content_at_commit."),
    ])),
    ("handoff", od([
        ("objective",
         f"Write {EVIDENCE} and {DECISION} from the composition's drafts and make them "
         "official in one isolated commit."),
        ("uncertainty_reduced", "none; durability"),
        ("inputs", [f"{BASE}/{COMPOSE}/evidence-draft.yaml",
                    f"{BASE}/{COMPOSE}/decision-draft.yaml",
                    f"{BASE}/{COMPOSE}/scored-priors.json",
                    f"experiments/{EXP}/analysis.md",
                    f"{REVIEW}/review-plan.yaml",
                    "templates/research-records.md"]),
        ("constraints", [
            "stage only declared paths; runs alone",
            "commit message names the task id and every record id",
            "fetch origin/main and MERGE it before committing; never rebase pushed records",
            "validate_ledger.py must add no NEW error on the paths this commit stages. "
            "Capture a baseline BEFORE staging so a pre-existing error is not mistaken "
            "for one of yours.",
            "THE RECORDS' CONTENT IS THE COMPOSITION'S, NOT A FRESH JUDGEMENT. A "
            "divergence between the drafts and what you commit is a DEFECT, not a "
            "refinement. If a draft violates a schema in templates/research-records.md, "
            "fix exactly that and disclose each fix in the receipt under a "
            "`divergences_from_the_draft` block. Never silently.",
            f"Apply the {HYP} status change the decision states, or leave the hypothesis "
            "untouched if the decision says it does not move. Do not decide this "
            "yourself: only the composition's decision may change a hypothesis status, "
            "and you are applying it, not making it.",
        ]),
        ("deliverables", ["ledger-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As the reviewers' cards."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([("wall_clock_seconds", 1800), ("memory_gb", 1), ("maximum_runs", 0)])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "validate_ledger.py adds no new error on the staged paths",
        ]),
        ("runs_launched", 0),
    ])),
]))


queue = od([
    ("schema", "crypto.autoresearch.dispatch_queue.v1"),
    ("goal_id", GOAL),
    ("batch_id", BATCH),
    ("objective",
     "Evidence review of RUN-SEMBIN-b6eb9f (EXP-SEMBIN-c2c312): state the map between "
     "Semaev's d_F4 and GOAL-DREG-001's Macaulay-rank d_reg/D on byte-identical "
     "chained-S_3 Boolean instances, and say whether that campaign's degree-5/6 "
     "measurements bear on Assumption 1 or explicitly do not. This is "
     "GOAL-SEMBIN-5078bc's first completion criterion; either answer discharges it and "
     "an unstated map does not. Zero runs: every card carries maximum_runs 0, and the "
     "measurement being reviewed is already committed."),
    ("max_concurrent", 3),
    ("max_concurrent_basis",
     "Three, because the three reviewers are mutually blind and concurrent is the "
     "correct shape for them: nothing one learns may reach another. They are "
     "zero-compute readers of committed records at 2 GB each, which this host carries. "
     "The later tasks are strictly sequential by dependency."),
    ("notes", [
        od([
            ("at", "2026-09-21T19:10:00Z"),
            ("kind", "review_plan"),
            ("text",
             f"The round is {ROUND} and its plan is {REVIEW}/review-plan.yaml, committed "
             "at 43e99599f -- BEFORE this queue existed and before any reviewer ran. The "
             "plan carries seven Coordinator priors, three joints with exactly one owner "
             "each, four STRUCTURED proves-too-much objects, and an eight-entry "
             "blind_from. Reviewers are blind to each other and to the prior block."),
        ]),
        od([
            ("at", "2026-09-21T19:10:00Z"),
            ("kind", "why_this_is_ranked_work_and_not_make_work"),
            ("text",
             "RUN-SEMBIN-b6eb9f completed with a full artifact set and has no evidence "
             "record and no decision, so its measurement is an observation that no "
             "reader can cite. Its objective is this goal's FIRST completion criterion. "
             "An unlimited ECC budget does not license make-work, and this is ranked "
             "ahead of doing nothing because a committed run without an evidence record "
             "is the cheapest unconverted value the goal holds."),
        ]),
        od([
            ("at", "2026-09-21T19:10:00Z"),
            ("kind", "this_goal_was_undispatchable_when_this_batch_opened"),
            ("text",
             "BATCH-9d649f's queue -- the path this goal's head still names in "
             "dispatch_queue_path -- would not render: TASK-20260913-525e13 bound the "
             "shared append-only tools/run_supersession_registry.yaml under "
             "content_first, so every unrelated ICPERF or QSP append reported the "
             "archive corrupt, and a dispatch error is fatal to a whole render. The "
             "declared hash had also drifted away from the archive's own committed "
             "receipt. Repaired and recorded in CORR-20260921-f5e9c4 before this batch "
             "was built. Any archive in this batch that binds a shared or generated file "
             "must use content_at_commit."),
        ]),
    ]),
    ("tasks", tasks),
])

root = pathlib.Path(__file__).resolve().parents[5]
out = root / BASE / "dispatch_queue.json"
if not out.parent.is_dir():
    raise SystemExit(f"refusing to write: {out.parent} does not exist")
out.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(root)} with {len(tasks)} tasks")
