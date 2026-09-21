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


# ---------------------------------------------------------------------------
# Post-execution facts, applied to the cards after they ran.
EXECUTED = {
    J1: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21, landed at 6f1902a44. VERDICT: BREAKS, narrowly, and not "
         "where the run's numbers are. `completed_valid` is NOT falsified -- every "
         "reported quantity reproduces from the raw records and no contract invalidation "
         "rule fires -- but the declaration is broader than the package establishes. The "
         "byte-identity control was reframed into a form with ZERO DETECTION POWER: "
         "run_cells.py computes one sha and passes the SAME VARIABLE as both "
         "system_sha256 and input_sha256, so 'a mismatch invalidates that cell' can never "
         "fire, and the manifest's assertion that byte identity holds is true only because "
         "the validator supplied the missing comparison itself (139 of 139 retained msolve "
         "files parsed and compared exactly). Declared code identity is broken for 4 of 11 "
         "modules with two .so files absent, made load-bearing by dirty: true."),
        ("the_duplicate_audit_was_computed_and_is_clean",
         "ZERO discordant pairs. 314 raw records over 270 distinct (instance, instrument) "
         "keys; 30 keys duplicated, accounting for all 44 extras; nothing disagrees on any "
         "reported value or per-degree profile. The disclosed workerB double-run splits "
         "into 9 F4 keys where BOTH records are unreached placeholders rather than "
         "measurements, and 10 Macaulay keys agreeing bit-for-bit -- so 'first completed "
         "record wins' never had to break a tie and is a no-op with respect to every "
         "reported value. This was the highest-value item on the joint precisely because "
         "an empty discordant list that was actually computed is a real result, and the "
         "package never computed it."),
        ("eight_further_defects_found_and_not_fixed",
         "D1 (high): declared code_sha256 broken for 4 of 11 modules against a dirty tree, "
         "so the instrument bytes that produced the run are not recoverable here. D3: the "
         "manifest records protocol_deviations [] and unexpected_observations [] while the "
         "run's own NOTES file lists seven deviations -- the manifest contradicts its own "
         "package. D7: one record shows 11.86 GB peak RSS against a stated 7 GB cap. Full "
         "list in findings.json."),
    ]),
    J2: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21, landed at fed1b8c21. VERDICT: BREAKS. THIS RUN DOES NOT "
         "EARN COMPLETION CRITERION 1. The contract's declared primary metric "
         "`D_macaulay_rank_statistic` was never computed: code/run_cells.py binds that "
         "metric NAME directly to the VALUE closure_D, so the raw records carry "
         "`D_macaulay_rank_statistic: 4` beside `closure_D: 4` -- a name collision that "
         "makes the substitution invisible to anyone reading the results table. And "
         "closure_D is F4-SIDE BY ITS OWN DEFINITION: closure_cert.py states the "
         "equivalence as 'G_D is a Groebner basis iff F4 completes with step degree <= D', "
         "so it is the solving degree of a truncated F4. THE HEADLINE IS THEREFORE AN "
         "AGREEMENT BETWEEN TWO F4-SIDE QUANTITIES, not a map between d_F4 and a Macaulay "
         "statistic. The substitution is disclosed nowhere."),
        ("the_prosecution_wins_but_not_on_the_ground_the_plan_led_with",
         "The defence is real and the red team credited it: msolve is an independently "
         "written F4 with the OPPOSITE field-equation convention, so 9 byte-identical "
         "agreements are a genuine falsifiable test of the closure's ARGUED "
         "truncated-Buchberger equivalence, and it could have failed. What kills it is "
         "that the headline and the conclusion are about different objects joined by no "
         "measurement, and that the input-versus-output point is a property of a function "
         "signature the run wrote -- ALREADY COMMITTED IN EV-DREG-008's OWN BOUNDARIES "
         "SEVEN WEEKS EARLIER ('Structural deficit_genuine is not theoretical d_reg'). "
         "Worse, GOAL-DREG-001's actual campaign quantity is d_reg as an OUTPUT "
         "(d_reg(null) = 7 at n = 12, analytic linear law c* = 0.23748), which this run "
         "never touches. So the run compared against the wrong DREG quantity."),
        ("unit_ideal_count_among_the_nine",
         "FIVE of 9 -- four at (15,5,3,3) and one at (17,3,3,6) with random B. On those "
         "five the closure decides by 1 in W_D; on the other four by a standard-monomial "
         "match. TWO DIFFERENT CERTIFICATES ARE REPORTED AS ONE FINDING, and the run's "
         "'35 of 43 unit-ideal' figure is over F4 traces rather than over the 9 that "
         "support the map. This number is the proves-too-much control's sharpest object "
         "and the package never computed it."),
        ("the_contract_is_at_fault_too",
         "The falsification criterion is UNSOUND, and that defect is the CONTRACT's, not "
         "the run's: its consequent conflates the degree at which a Macaulay matrix was "
         "BUILT with a degree the system ATTAINS. EV-DREG-008 computes a rank at frozen "
         "INPUT D = 6, which asserts no degree statistic of 6 and so cannot be in tension "
         "with d_F4 <= 4. Separating run defects from contract defects is why objections "
         "are classified on that axis."),
        ("the_fix_needs_zero_runs",
         "31 instances already carry BOTH the single-level rank/deficit and a d_F4 value -- "
         "3.4x the closure's 9 -- so naming one of the three readings in H-SEMBIN-112e2e "
         "and computing separation_D_minus_d_F4 from committed records produces the metric "
         "the contract actually declared, with no new measurement."),
        ("interpretation_limits_respected",
         "Checked hard in both directions: no Assumption-1 leakage. A red team that finds "
         "nothing where nothing is wrong is reporting, not failing."),
    ]),
    J3: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21, landed at ec3b333df. VERDICT: HOLDS. The headline "
         "reproduces EXACTLY and on ELEVEN instances rather than the producer's nine: "
         "closure_D - d_F4 = 0 on all 11 where both instruments were reached, under all "
         "four d_F4 conventions computed, so it is convention-independent on its support. "
         "closure_D reproduces on all 126 recorded instances (15 values, 111 nulls) and "
         "all 15 are exact rather than upper bounds. d_F4_naive agrees on all 45 where the "
         "producer publishes one, and an independent parse of every msolve log found zero "
         "field mismatches against the producer's trace parser."),
        ("one_definitional_divergence_localised_to_two_named_implementations",
         "The producer's d_F4_semaev deletes the trailing run of rounds that added NO NEW "
         "BASIS ELEMENT (new == 0). Semaev's stated exclusion, transcribed literally, "
         "deletes rounds that selected NO PAIRS ('No pairs to reduce', sel == 0). The two "
         "rounds the producer excludes -- and files under the name f4_empty_step_degrees "
         "[4, 5] -- SELECTED 34 AND 519 PAIRS and computed row echelon forms of 1915x2220 "
         "and 84267x84198 matrices. One instance reads 4 under the producer's rule and 5 "
         "under the literal one. It reaches no separation, because no n = 12 cell ever ran "
         "the closure."),
        ("tail_check_ii_is_untestable_and_that_is_the_finding",
         "Across 749 F4 rounds NOT ONE has sel == 0. msolve never emits a 'No pairs to "
         "reduce' step, so the F4 side of the contract's predicted coincidence is the EMPTY "
         "SET. The exclusion that Semaev's whole d_F4 definition turns on has nothing to "
         "act on in this engine -- which means the producer's new == 0 rule is doing ALL "
         "the exclusion work and it is not Semaev's rule. Reported as an engine property "
         "plus a coverage limit, never as evidence against the mechanism."),
        ("tail_check_i_answered_both_ways",
         "Raw: 11 of 11 hit. Like-for-like at degrees >= 2: ZERO of 11. The raw hit is "
         "SYSTEMATIC, because a closure profile always carries degree-1 pivots while an F4 "
         "run has no step at degree 0 or 1, so the two profiles are indexed on different "
         "things and only their supports are comparable. Reporting one number here would "
         "have been misleading in whichever direction it was chosen."),
        ("two_things_nobody_had_counted",
         "129 instance stems on disk against 126 ids in results.jsonl: THREE INSTANCES "
         "LEFT ARTIFACTS AND PRODUCED NO RECORD, and one really ran -- the B_random MATCHED "
         "NULL yields d_F4 = 4 from its retained log. Both the validator's enumeration and "
         "the run's own summary.json miss all three because both count from results.jsonl. "
         "Separately, four records carry a `rounds` array that is a strict prefix of the "
         "log on disk."),
        ("the_limit_on_achievable_blindness_disclosed",
         "The raw results.jsonl files EMBED the producer's per-instance derived scalars, so "
         "blindness to its NUMBERS was not achievable from this package. Blindness to its "
         "IMPLEMENTATION was, and was maintained: rederive.py deletes the producer's "
         "derived scalars programmatically before deriving and parses the raw engine logs "
         "itself. The d_F4 convention divergence is the evidence that it held -- an "
         "implementation that had peeked would not have disagreed."),
    ]),
    COMPOSE: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21, landed at 803f19231. TRANSITION: inconclusive. "
         "EV-SEMBIN-c6e9ad direction neutral, strength inconclusive, claim_tier toy, "
         "proof_status derivation. All seven priors scored: FIVE CONFIRMED, P-6 and P-7 "
         "REFUTED. Completion criterion 1 NOT MET on either branch. H-SEMBIN-112e2e does "
         "not move. Nothing promoted to knowledge, with a concrete reason."),
        ("the_asymmetry_is_the_finding",
         "Every prior about a DEFECT held; every prior about what the run ESTABLISHED fell. "
         "P-6 was flagged in the plan as THIS_IS_THE_PREDICTION_I_MOST_EXPECT_TO_LOSE with "
         "its escape clause written in advance, and the clause fired verbatim. The plan was "
         "committed at 43e99599f in a commit containing no reviewer output, which is the "
         "only thing that lets 'three reviewers concurred' be distinguished from 'three "
         "reviewers concurred with what the Coordinator already believed'."),
        ("why_inconclusive_rather_than_refine",
         "`refine` presupposes a measured comparison that needs sharpening. There is none to "
         "sharpen: the contract's declared primary metric was never computed as an output, "
         "so the instrument for the map has to be built first. `support` fails on unobserved "
         "strictness, `reject_scoped` on the bar forbidding one unreplicated empirical-only "
         "run, and replicate/expand because re-running the same instrument pair reproduces "
         "the same definitional gap at greater cost. P-7's three EXCLUSIONS all survive and "
         "are adopted even though its positive prediction was refuted."),
        ("the_hypothesis_does_not_move_on_a_ground_found_late",
         "H-SEMBIN-112e2e states that the predicted separation IS the excluded 'No pairs to "
         "reduce' tail -- and J-3 found that tail EMPTY in msolve across all 749 F4 rounds. "
         "So the hypothesis's own mechanism predicts separation 0 on this engine, and the "
         "observed 0 is CONSISTENT WITH it rather than against it. Unobserved strictness "
         "reads adverse and an unmeasured quantity reads neutral; the neutral reading wins. "
         "Coverage confirms no verdict was available anyway: exactly ONE non-degenerate "
         "separation-cell observation across the four cells where strictness is predicted."),
        ("its_own_overclaim_caught_mid_task_as_PD_5",
         "An earlier draft stated the declared metric was available at ZERO RUN COST on 31 "
         "instances. FALSE: the single-level sweep stops at D = 4, where every structured "
         "instance is far from determining (rank 4707 of 12951 columns, deficits 46-67), so "
         "obtaining it needs D >= 5 -- exactly where the memory caps bit. The error made the "
         "remedy look cheap and the completion criterion look nearer, which is precisely the "
         "bias this round existed to catch, and it also CORRECTS J-2's 'the fix needs zero "
         "runs' claim. Caught and disclosed by the composition itself rather than by audit."),
        ("nine_versus_eleven_reconciled",
         "Eleven rows carry both instruments: 9 distinct structured instances plus 1 "
         "known-false control and 1 identity repeat. 9 is adopted for the map claim and 11 "
         "for separation-bearing rows, with the reading stated wherever either is used. The "
         "producer is not wrong to say 9; it is wrong to put 9 in manifest.yaml and 11 in "
         "summary.json with no reconciling note."),
        ("one_reviewer_finding_corrected",
         "J-1 reversed the certificate bases; recomputation confirms J-2's split -- 5 "
         "unit-ideal deciding by 1 in W_D, 4 by standard-monomial match. J-1's joint verdict "
         "is untouched by the correction."),
    ]),
    LEDGER: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21 at commit 73f807a8137028e650b549f75d091a7f5e0842ff. "
         "EV-SEMBIN-c6e9ad and DEC-20260921-2c62d7 are official, with the analysis bound "
         "alongside. ZERO divergence from the composition's drafts, verified by diff and by "
         "recorded source and result hashes rather than asserted. validate_ledger.py names "
         "none of these records; the standing errors are other campaigns' run-manifest "
         "schema debt."),
        ("archive_binding", od([
            ("commit_sha", "d436b131c7d86df5d1037a193c80a5cd737ce155"),
            ("parent_sha", "73f807a8137028e650b549f75d091a7f5e0842ff"),
            ("commit_sha_note",
             "TWO COMMITS, and the binding names the second. The records were staged and "
             "committed at 73f807a81, whose message named all six record ids and OMITTED THE "
             "TASK ID -- against a card constraint requiring both, which research_dispatch.py "
             "enforces and which refused the render. 73f807a81 carries two ledger records and "
             "is pushed, so it was NOT amended: AGENTS.md forbids rewriting history over "
             "pushed records, and amending would have erased the evidence that a declared "
             "constraint was missed. d436b131c stages only the disclosure addendum and carries "
             "every identifier. The declared path_sha256 set is unchanged and still verifies, "
             "because content_first checks hashes against HEAD rather than against the named "
             "commit's tree, so the binding is exactly as strong as before. Full account: "
             "archives/TASK-20260921-bd5f2e/commit-message-addendum.md. Cost, stated plainly: "
             "the commit named here is not the commit that created the records it binds."),
            ("path_sha256", od([
                (f"{BASE}/archives/{LEDGER}/ledger-receipt.json",
                 "679e952becb07245de9b3b7ce20c8a37445a2892d8381b7b45b9c056644c5f32"),
                (f"ledger/evidence/{EVIDENCE}.yaml",
                 "bae577859c95303cbd4914c244b2cd8d13dc879837430e715583515d68e74c9d"),
                (f"ledger/decisions/{DECISION}.yaml",
                 "eda1fa6018a8740933d4fe5c0ccf2cd1164a6a42ccb549da73a711bb86143136"),
                (f"experiments/{EXP}/analysis.md",
                 "e134e8bc33ebd66f348f8c0c83965272a8df1abbf6b745b9997be56fed5f5d90"),
                (f"{BASE}/{COMPOSE}/scored-priors.json",
                 "1b68a2b2ae7d96bda80eac734c4f61867a64f9a75b5af21e1b33fe18d269cb88"),
                (f"{BASE}/{COMPOSE}/evidence-draft.yaml",
                 "bae577859c95303cbd4914c244b2cd8d13dc879837430e715583515d68e74c9d"),
                (f"{BASE}/{COMPOSE}/decision-draft.yaml",
                 "eda1fa6018a8740933d4fe5c0ccf2cd1164a6a42ccb549da73a711bb86143136"),
            ])),
            ("path_sha256_note",
             "SEVEN entries: the receipt, the two official ledger records, and the four "
             "artifacts the source task declared (the analysis, the scored priors, and both "
             "drafts). All computed from git blobs."),
            ("the_binding_CRYPTOGRAPHICALLY_confirms_the_zero_divergence_claim",
             "evidence-draft.yaml hashes to bae577859c95... and ledger/evidence/"
             "EV-SEMBIN-c6e9ad.yaml hashes to the SAME value; decision-draft.yaml and "
             "ledger/decisions/DEC-20260921-2c62d7.yaml likewise both hash to eda1fa601... "
             "So 'the official records are byte-identical to the composition's drafts' is not "
             "the archiving session's assertion about its own work -- it is two pairs of "
             "equal hashes in this binding, checkable by anyone against commit 73f807a81. "
             "That is a better guarantee than the receipt's prose and it is the reason to "
             "bind the drafts here rather than only the records."),
        ])),
        ("the_parent_sha_was_resolved_from_HEAD_this_time",
         "Recorded because the sibling archive TASK-20260921-064ae9 misfiled this exact "
         "field in this same batch, writing the tip of origin/main -- the commit it had just "
         "merged IN -- instead of its own parent. Here the declared value was produced by "
         "`git rev-parse HEAD` before staging and then checked against `git rev-parse HEAD^` "
         "after committing; the two agree. The earlier receipt is immutable and stays wrong, "
         "and the queue carries the correct value for it."),
    ]),
    SNAPSHOT: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21 at commit fbaaf6853be3cfb656b6fd4413d3fd26df41089b. Staged "
         "only its own receipt; all ten reviewer artifacts were already landed by "
         "producer_landing.py when each reviewer returned, and a following --check reported "
         "no unlanded output and nothing undeclared in any producer's write scope."),
        ("archive_binding", od([
            ("commit_sha", "fbaaf6853be3cfb656b6fd4413d3fd26df41089b"),
            ("parent_sha", "241313853c627dcc6cfbc5c50ad326c4ec3c9584"),
            ("path_sha256", od([
                (f"{BASE}/archives/{SNAPSHOT}/snapshot-receipt.json",
                 "d5691a7eeb426d36de1a658fe85f98398988b5ae37adf328a0710da7e9c103b5"),
                (f"{BASE}/{J1}/report.md",
                 "f1f8acb0d8544b8093df944407221af4d796cdfb83e0e3f0caad0670815dbee5"),
                (f"{BASE}/{J1}/findings.json",
                 "20fbc2eb9fb04190386d32dcccda1035462387ebb6b68c7651ae50ec39ac35c7"),
                (f"{BASE}/{J1}/attestation.yaml",
                 "06f39f860123a718c133a6a4cc7bbd06ada229e2df74dc63f19d6e7b30d8e67e"),
                (f"{BASE}/{J2}/report.md",
                 "fffb4ae252d8a0a2b4736753e96450204c3cdd2e366fd795449499be01eb115f"),
                (f"{BASE}/{J2}/objections.json",
                 "f3a3fc4a80ecb59b34de507d9c5bb2de261179f8f76d50904744637d700364fc"),
                (f"{BASE}/{J2}/attestation.yaml",
                 "aa25e64b42d9fa7b88198e0cea7f055bcbb8ad689d90f91db7141845cc32a862"),
                (f"{BASE}/{J3}/report.md",
                 "f1b10e63597d992bd18121ef36451f289838ee8410e634c63b26f951c51a935a"),
                (f"{BASE}/{J3}/rederived.json",
                 "e545eda29353734b8a50f592d9636957055d23221183387f2eecaf24cabbee15"),
                (f"{BASE}/{J3}/rederive.py",
                 "f4614f7e412ae5a7d1721b5b379e35722c40525d5c00266938f2718185f0c0ea"),
                (f"{BASE}/{J3}/attestation.yaml",
                 "b86afaf825167fffdfe8f32f8a1d344cac9b18a11527786a017441d1e0f24494"),
            ])),
            ("path_sha256_note",
             "ELEVEN entries: the receipt, whose hash it cannot contain itself, plus the ten "
             "declared artifacts of the three reviewers. All computed from git blobs."),
        ])),
        ("MY_ERROR_the_receipt_declares_the_WRONG_parent_sha", od([
            ("what",
             "The committed receipt records parent_sha 1d98cc5b2ac95bb1dd0f7aa0bca07ba0f80ff4e2. "
             "That is origin/main's tip, the commit that was MERGED in; it is not this "
             "archive's parent. The actual parent is "
             "241313853c627dcc6cfbc5c50ad326c4ec3c9584, the merge commit this session "
             "created. The value above in archive_binding is the correct one, verified with "
             "`git rev-parse <commit>^`."),
            ("how_it_happened",
             "I wrote the sha I had just fetched rather than resolving my own HEAD. The same "
             "shape of mistake as the fabricated commit_sha earlier in this session: reaching "
             "for a sha that was on screen instead of asking git which one the field means."),
            ("why_the_receipt_is_not_edited",
             "It is committed and immutable. Editing it to match would destroy the evidence "
             "that the archiving task got a binding field wrong, which is exactly the "
             "history a later reader needs. Disclosed here instead."),
            ("the_irony_is_load_bearing_and_is_recorded_as_such",
             "CORR-20260921-f5e9c4 -- written by this same session, minutes earlier, about "
             "this same goal -- records a defect whose whole substance was A QUEUE THAT HAD "
             "DRIFTED FROM ITS OWN RECEIPT, and proposes FG-4: a check comparing every "
             "completed archive's declared path_sha256 against the receipt committed inside "
             "it, failing the render on disagreement. I then produced a queue-versus-receipt "
             "divergence of my own within the same session, on a DIFFERENT field. Two "
             "conclusions follow and both are more useful than the embarrassment. First, "
             "FG-4 should cover parent_sha and commit_sha, not only path_sha256. Second, the "
             "defect class is not carelessness by one earlier session -- it is structural, "
             "because nothing mechanically compares the two records, and a session that has "
             "just finished writing about the hazard still walked into it."),
            ("what_is_NOT_affected",
             "No hash, no content claim, and no reviewer artifact. All eleven declared "
             "hashes verify. The render passes against the corrected parent, and the "
             "receipt's substantive content -- the ten hashes, the independence "
             "qualifications, the joint verdicts -- is unaffected."),
        ])),
        ("the_rederivation_hash_corroborates_the_blindness_claim",
         "rederived.json's committed blob hashes to e545eda2, exactly the value J-3 reported "
         "for the file it wrote BEFORE opening the producer's summary.json. So its "
         "attestation is about these exact bytes rather than an earlier draft. What a hash "
         "cannot establish is the ORDERING, which rests on the attestation -- and that is "
         "what an attestation is for."),
    ]),
}

for _task in tasks:
    _applied = EXECUTED.get(_task["id"])
    if not _applied:
        continue
    for _key, _value in _applied.items():
        if _key == "state":
            _task["state"] = _value
        elif _key == "archive_binding":
            _task["archive"]["commit_sha"] = _value["commit_sha"]
            _task["archive"]["parent_sha"] = _value["parent_sha"]
            _task["archive"]["path_sha256"] = _value["path_sha256"]
            _task["archive"]["path_sha256_note"] = _value["path_sha256_note"]
        else:
            _task[_key] = _value


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
