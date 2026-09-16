#!/usr/bin/env python3
"""Author BATCH-cbb416's dispatch queue -- the first batch on GOAL-SEMBIN-fcb7a2.

Kept beside the queue it wrote so a later reader can see the queue was generated
from one declaration rather than hand-edited into shape. It writes the file and
does not read it, so re-running it after the batch has moved would overwrite
recorded state -- one-shot authoring script; the queue is the record from here on.

THE SHAPE OF THIS BATCH IS SET BY ONE FACT: EXP-SEMBIN-4fa22c's own
proof_search_map carries an audit marked "REQUIRED BEFORE THE FIRST RUN and not
yet performed" -- the observation-collision search. So the batch is two producers
in series, not one: find out whether this program has already measured this
quantity, and only then measure it. A collision found after the compute is spent
is worth much less than the same collision found before, and the Coordinator's
own five-minute grep already turned up first-fall-degree machinery in four other
experiments, which is why this is a task and not a checkbox.
"""

import collections
import json
import pathlib

BATCH = "BATCH-cbb416"
GOAL = "GOAL-SEMBIN-fcb7a2"
BASE = f"coordination/goals/{GOAL}/batches/{BATCH}"
EXP = "experiments/EXP-SEMBIN-4fa22c"
AUDIT = f"{BASE}/collision-audit"
REVIEW = "coordination/review/sembin-20260916-cbb416"

OPEN = "TASK-20260916-141f76"
OPEN_SNAPSHOT = "TASK-20260916-007117"
COLLISION = "TASK-20260916-fc72a6"
AUDIT_SNAPSHOT = "TASK-20260916-81fa8c"
RULE = "TASK-20260916-ac0aea"
RULING_ARCHIVE = "TASK-20260916-9d98ef"
EXECUTE = "TASK-20260916-0c2802"
PRIOR = "TASK-20260916-1bb446"
PRIOR_ARCHIVE = "TASK-20260916-d5e431"
PRODUCER_SNAPSHOT = "TASK-20260916-8eb394"
REVIEW_INSTRUMENT = "TASK-20260916-90af14"
REVIEW_BLIND = "TASK-20260916-7be96a"
LEDGER = "TASK-20260916-6a2fcf"

DECISION = "DEC-20260916-59921c"
RULING = "DEC-20260916-b0e654"
AMENDMENT = "AMD-EXP-SEMBIN-4fa22c-20260916-collision"
ROUND = "REVIEW-SEMBIN-20260916-cbb416"
EVIDENCE = "EV-SEMBIN-29c44f"
CLOSING = "DEC-20260916-a0af84"

# The audit snapshot's own receipt hash, read back from its commit. A receipt
# cannot contain its own hash, so the queue carries it -- the one hash below that
# a reader must take from here rather than from the receipt itself.
RECEIPT_SHA = "c7b850aa0c61bb652d5b63856c4669ef828743badc0e63fca0077cb31b66f07e"
RULING_RECEIPT_SHA = "891420f789d63e3c8a503facd987cc175aa848975047678e96d56c0e7b25e8ba"

AMENDMENT_PATH = f"{EXP}/amendments/{AMENDMENT}.yaml"
# ADDENDUM **2**. Addendum 1 is another session's, and it landed on origin/main
# while this ruling was being written: it reassigns J3/J4 to the instrument
# reviewer so the blind re-deriver reads nothing under blind_from. Two sessions
# amended this batch's queue within the hour, which is the ordinary condition
# here, and the merge kept both. Addendum 2 extends `blind_from` over the
# collision audit; it does not touch addendum 1's assignment.
ADDENDUM_PATH = f"{REVIEW}/review-plan-addendum-2.yaml"

# ADDENDUM 3 exists because a task in ANOTHER LANE returned a sharp numeric
# prediction about the arm THIS batch's executor is measuring right now, and the
# prediction reverses the direction H-SEMBIN-a7e721 predicts. AGENTS.md "Review
# architecture" requires the Coordinator's prior to be recorded before any
# reviewer runs; here the harder constraint is that it be recorded before the
# MEASUREMENT, because a prior written after the number arrives is not a prior.
# Hence its own pair of cards below rather than a place on the closing card,
# which commits at batch close -- far too late to prove anything.
PRIOR_ADDENDUM_PATH = f"{REVIEW}/review-plan-addendum-3.yaml"


def od(pairs):
    return collections.OrderedDict(pairs)


open_artifacts = [
    f"ledger/decisions/{DECISION}.yaml",
    f"ledger/goals/{GOAL}/goal.yaml",
    f"ledger/goals/{GOAL}/checkpoints/{BATCH}.yaml",
    f"{BASE}/dispatch_queue.json",
    f"{BASE}/build_queue.py",
    f"{BASE}/opening-report.md",
    f"{REVIEW}/review-plan.yaml",
]

collision_artifacts = [
    f"{AUDIT}/report.md",
    f"{AUDIT}/searches.json",
    f"{AUDIT}/verdict.json",
]

# The review plan is committed and bound at d38386a31, so a change to who owns
# a joint travels as an addendum beside it (tools/check_review_independence.py
# composes plan + addenda), never as an edit to the plan. Both of these are
# Coordinator-written control-plane files the closing ledger archive binds.
REVIEW_ADDENDUM = f"{REVIEW}/review-plan-addendum-1.yaml"
BLIND_INSTANCE = f"{REVIEW}/blind-instance.yaml"
CLOSING_CHECKPOINT = f"ledger/goals/{GOAL}/checkpoints/{BATCH}-close.yaml"

# NO GOAL HEAD HERE, and the reason is a real constraint rather than an
# oversight: an artifact path is owned by exactly ONE task in a queue, and
# ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml is already owned by the OPEN card.
# research_dispatch.py refuses a second owner by name. So this ruling does not
# touch the head; the head is reranked at this batch's close, and the ruling is
# discoverable from the queue, the decision itself and the batch checkpoint.
#
# THE DECISION RECORD ITSELF IS OWNED BY THE ARCHIVE CARD, not by this one. That
# is not a preference either: research_dispatch.py requires a `ledger` archive to
# own an artifact under ledger/decisions/ AND refuses two owners for one path, so
# the two constraints together force the coordinator archive card to carry the
# decision. BATCH-e0a0c1 hit the identical pair of rules and resolved it the same
# way; the batch-closing card below has always been shaped like this.
ruling_artifacts = [
    AMENDMENT_PATH,
    ADDENDUM_PATH,
]

tasks = []

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", OPEN),
    ("title",
     "Open BATCH-cbb416 on GOAL-SEMBIN-fcb7a2: rank the approved EXP-SEMBIN-4fa22c behind its own "
     "unperformed pre-compute audit, and record the batch control plane"),
    ("role", "coordinator"),
    ("state", "completed"),
    ("priority", 95),
    ("review_required", False),
    ("depends_on", []),
    ("read_scope", [
        f"ledger/goals/{GOAL}/goal.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        f"{EXP}/specification.yaml",
        "ledger/decisions/DEC-20260916-6ce039.yaml",
        "ledger/decisions/DEC-20260916-88ac73.yaml",
        "ledger/corrections/CORR-20260916-402547.yaml",
        "ledger/corrections/CORR-20260916-96f47d.yaml",
        "coordination/review/sembin-20260916-propquant",
        "docs/concurrent-goal-lanes.md",
        "docs/inventor-protocol.md",
    ]),
    ("write_scope", [
        BASE,
        REVIEW,
        f"ledger/decisions/{DECISION}.yaml",
        f"ledger/goals/{GOAL}/goal.yaml",
        f"ledger/goals/{GOAL}/checkpoints/",
    ]),
    ("artifact_paths", open_artifacts),
    ("handoff", od([
        ("objective",
         "Turn the approved-but-never-dispatched EXP-SEMBIN-4fa22c into a batch whose first "
         "producer is the audit its own contract requires before any measurement."),
        ("uncertainty_reduced",
         "none; this is a ranking and control-plane act. It measures nothing and asserts nothing "
         "about Nagao."),
        ("inputs", [
            f"ledger/goals/{GOAL}/goal.yaml (next_action rank 1: dispatch the first SEMBIN batch)",
            f"{EXP}/specification.yaml (approved at v1 by DEC-20260916-6ce039)",
            "ledger/hypotheses/H-SEMBIN-a7e721.yaml (approved)",
            "ledger/corrections/CORR-20260916-402547.yaml (authoring is not progress against a "
            "completion criterion; only run or read evidence is)",
        ]),
        ("constraints", [
            "Zero runs.",
            "Never edit the frozen EXP-SEMBIN-4fa22c specification or H-SEMBIN-a7e721. A change to "
            "either is an additive amendment under a new id.",
            "The goal head is edited additively inside this batch's own archive; another session "
            "may be working this goal without telling this one.",
        ]),
        ("deliverables", [f"{DECISION}", f"{BATCH} checkpoint", "dispatch_queue.json",
                          "opening-report.md",
                          f"{ROUND} review plan, written before any reviewer is dispatched"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note",
             "TRUE and declared up front rather than amended after the work runs. No adapter "
             "backend is credentialed in this checkout, so the runtime-native binding permitted by "
             "core rule 16 is the only route and `false` would be a claim every dispatch breaks "
             "(DEC-20260916-7b2235, DEC-20260916-bec4b8). "
             "tools/research_dispatch.py `inference_advisories` now reports this at render time; "
             "this card is written so it has nothing to report."),
            ("degraded_allowed", False),
            ("degraded_requirements_expected", [
                "model_verified false: `doctor --probe` needs a usable backend and none is usable "
                "here, so the resolved identifier is self-reported and is unverified configuration.",
            ]),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 3600),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "the opening decision is committed",
            "the queue renders with all gates passing and no inference advisory",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", OPEN_SNAPSHOT),
    ("title", "Snapshot-archive BATCH-cbb416's control plane before either producer reads it"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 94),
    ("review_required", False),
    ("depends_on", [OPEN]),
    ("read_scope", [BASE, REVIEW, EXP, "ledger"]),
    ("write_scope", [f"{BASE}/archives/{OPEN_SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{OPEN_SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [OPEN]),
        ("record_ids", [DECISION, GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit from the outset. The goal head is reranked at every checkpoint and the "
         "contract will advance from `approved` to `running` to `completed`, so under content_first "
         "each of those legitimate moves would report this archive as corrupt -- the failure "
         "CORR-20260915-654160 records. Binding the bytes in this archive's own commit asks the "
         "question a snapshot actually makes."),
        ("receipt_note",
         "Both producers depend on this archive so that each reads a committed, pushed contract "
         "rather than a working tree."),
    ])),
    ("handoff", od([
        ("objective", "Commit the exact control plane both producers will read."),
        ("uncertainty_reduced", "none; durability before dispatch"),
        ("inputs", open_artifacts),
        ("constraints", [
            "stage only declared paths",
            "commit message names the task id and every record id",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As OPEN's card: declared up front, not amended after the fact."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 600),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", ["post-commit receipt verified by research_dispatch.py"]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", COLLISION),
    ("title",
     "Perform EXP-SEMBIN-4fa22c's observation-collision audit: has this program already measured a "
     "first fall degree -- true or fake -- for summation-polynomial descents, and does an existing "
     "validated Macaulay implementation already answer part of this contract?"),
    ("role", "executor"),
    ("state", "queued"),
    ("priority", 90),
    ("review_required", False),
    ("review_required_note",
     "FALSE, and the reason is not that this task is unimportant. `review_required` reserves an "
     "independent reviewer for a task whose RESULT could change a claim; this task produces a search "
     "log and a recommendation, and changes no claim about any curve. The act that can change "
     "something is the COORDINATOR RULING on its verdict, which is a committed decision and is "
     "subject to the ordinary decision-record discipline -- including the research-direction "
     "integrity rule, which is the one that matters here: if this audit recommends stopping or "
     "reframing, the ruling must name the evidence, the test boundary, the remaining uncertainty and "
     "a concrete successor or revisit condition. An audit that quietly steers the campaign away from "
     "a lead is exactly what that rule forbids, and the ruling is where it is checkable."),
    ("depends_on", [OPEN_SNAPSHOT]),
    ("read_scope", [
        f"{EXP}/specification.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "knowledge/",
        "ledger/",
        "experiments/",
        "inputs/NAGAO-2015-984",
        "AGENTS.md",
        "docs/inventor-protocol.md",
    ]),
    ("write_scope", [AUDIT]),
    ("artifact_paths", collision_artifacts),
    ("handoff", od([
        ("objective",
         "Establish, BEFORE any compute is spent on EXP-SEMBIN-4fa22c, whether its planned "
         "measurement duplicates or contradicts a measurement this program already holds -- and "
         "whether an existing validated implementation already computes part of it. This is the "
         "contract's own proof_search_map audit, whose status field says REQUIRED BEFORE THE FIRST "
         "RUN and not yet performed."),
        ("uncertainty_reduced",
         "Whether the planned run is novel, a replication, or already contradicted. Any of the "
         "three is a useful answer and the third is the most valuable."),
        ("inputs", [
            f"{EXP}/specification.yaml proof_search_map.observation_collision_search",
            "The Coordinator's own opening grep, which is a STARTING POINT AND NOT A RESULT: "
            "`rg -il 'first.fall.degree|first_fall_degree|d._F'` over knowledge/, ledger/ and "
            "experiments/ returned, among others, experiments/EXP-ECTD-9e4248/driver/reused/"
            "macaulay.py, experiments/EXP-SIG-007/src/ic_first_fall_fast.py, EXP-ALPF-006's "
            "round004_exp005_validated_firstfall.{sage,log,result.md}, EXP-ALPF-012's "
            "round006_exp011_binary_fppr.sage, EXP-PFGB-d630f6 and EXP-ECTD-abb8be's "
            "specifications, EXP-SEMBIN-db9bc3's code, and knowledge techniques KN-TECH-004, "
            "KN-TECH-011, KN-TECH-071, KN-TECH-b18366, KN-TECH-1cd4bb. Go past this list; it was "
            "one regex.",
            "inputs/NAGAO-2015-984/paper_fulltext.md for what quantity is actually being sought.",
        ]),
        ("constraints", [
            "ZERO RUNS AND ZERO MEASUREMENTS. You do not implement the experiment, you do not "
            "compute a first fall degree, and you do not run any algebra engine. If you find "
            "yourself measuring, the task has gone wrong.",
            "THE RETRIEVAL INDEX IS NOT AVAILABLE IN THIS CHECKOUT. kb/ has no .venv, no .env and "
            "no Qdrant reachable at the configured URL, so `search_knowledge` cannot be called and "
            "must not be reported as if it were. Search the repository directly instead, and record "
            "the index's unavailability as a limit on your recall. AGENTS.md is explicit that "
            "absence of a search result is not evidence something was not tried, and that recall is "
            "a FLOOR -- your report states a floor, never a clean bill of novelty.",
            "RECORD EVERY QUERY YOU RAN, including the ones that returned nothing, in searches.json "
            "with its exact form and its hit list. A search whose queries are not recorded cannot be "
            "extended by the next reader, which is most of the value of doing it.",
            "DISTINGUISH THE QUANTITY FROM ITS NAME. Several hits will use `first fall degree` for a "
            "DIFFERENT object -- a different field, a different descent, a different ring, or the "
            "true degree where this contract measures the fake one. A collision requires the same "
            "quantity on a comparable object, and near-misses are reported as near-misses with the "
            "difference named.",
            "DO NOT DECIDE WHETHER THE RUN PROCEEDS. You report; the Coordinator rules. Recommend, "
            "with reasons, and mark the recommendation as a recommendation.",
            "Cite with provenance (templates/research-records.md). A file you opened and read is "
            "`internal`; a paper you recall but did not open is `recalled` and is a pointer, never "
            "support.",
        ]),
        ("deliverables", [
            "report.md -- what exists, what it measured, on what object, and how close it is to "
            "this contract's quantity. One section per candidate, with the difference named for "
            "every near-miss.",
            "searches.json -- every query, its exact form, its hit count and its hits, including "
            "empty results; plus an explicit record that the kb index was unavailable and what that "
            "costs the recall claim.",
            "verdict.json -- machine-readable: {collision: none|replication|contradiction|partial, "
            "candidates: [...], reusable_implementations: [...], recommendation: proceed|reframe|"
            "stop, recall_floor_note: ...}. Every field is a recommendation, not a ruling.",
        ]),
        ("specific_questions_to_answer", [
            "Q1. Has any experiment in this program measured a first fall degree for a SUMMATION "
            "POLYNOMIAL Weil descent? If so: which quantity (true or fake), which field, which m "
            "and n, shifted or unshifted, and what value?",
            "Q2. EXP-ECTD-9e4248/driver/reused/macaulay.py -- what does it compute, is it validated "
            "by a run record, and would it compute this contract's M-1 and M-3 unchanged? The "
            "contract forbids importing EXP-ICPERF's converter and says nothing about this file; if "
            "it is a validated Macaulay-matrix rank instrument, that is a Coordinator ruling worth "
            "having before an executor writes a third one.",
            "Q3. EXP-SIG-007/src/ic_first_fall_fast.py -- same three questions.",
            "Q4. Does any record already assert a value for d_F or d'_F at EQS2 or EQS4 instances of "
            "Nagao's family, including inside DEC-20260913-8d19e5's lineage or EXP-SEMBIN-db9bc3?",
            "Q5. Does any existing measurement CONTRADICT H-SEMBIN-a7e721's prediction that d'_F > 4 "
            "at the shifted instances? A contradiction found here is worth more than the run.",
            "Q6. Is there a prior measurement of the TRIVIAL Koszul fall degree (this contract's "
            "M-2) anywhere, under any name?",
        ]),
        ("artifact_paths", collision_artifacts),
        ("inference", od([
            ("policy", "executor-implementation"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note",
             "TRUE, declared up front. No adapter backend is credentialed here "
             "(DEC-20260916-7b2235); the runtime-native binding is the only route."),
            ("degraded_allowed", False),
            ("degraded_requirements_expected", [
                "model_verified false: no backend is probeable in this checkout.",
            ]),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 5400),
            ("memory_gb", 2),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "report.md, searches.json and verdict.json all exist under the write scope",
            "searches.json records every query including empty ones, and records the kb index as "
            "unavailable",
            "every one of Q1-Q6 has an answer or an explicit `could not determine, because ...`",
            "no measurement was performed and no file outside the write scope was modified",
        ]),
        ("dispatch_preconditions", [
            f"{OPEN_SNAPSHOT} has a verified snapshot receipt, so the contract this audit reads is "
            "committed and pushed rather than a working tree",
        ]),
    ])),
]))

# ---------------------------------------------------------------------------
# THREE CARDS ADDED 2026-09-16 AFTER THE AUDIT RETURNED, and the reason they
# were not in the queue at opening is worth recording rather than hiding: the
# opening queue assigned the audit's artifacts to PRODUCER_SNAPSHOT, which also
# owns the execution. That is a defect. It makes the audit's deliverables
# uncommittable until the run they are supposed to gate has already happened,
# so the Coordinator ruling would have cited an uncommitted working tree and
# the reviewers would have read the audit out of the same commit as the run it
# preceded. Split here: the audit gets its own snapshot, the ruling gets its own
# card and its own ledger commit, and PRODUCER_SNAPSHOT is retargeted to the
# execution alone. Recorded in tasks_state_revisions, additively; no existing
# card's history is rewritten.
tasks.append(od([
    ("id", AUDIT_SNAPSHOT),
    ("title",
     "Snapshot-archive the collision audit exactly as produced, before any ruling cites it and "
     "before any reviewer reads it"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 89),
    ("review_required", False),
    ("depends_on", [COLLISION]),
    ("read_scope", [AUDIT, BASE]),
    ("write_scope", [f"{BASE}/archives/{AUDIT_SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{AUDIT_SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [COLLISION]),
        ("record_ids", ["EXP-SEMBIN-4fa22c", GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit, consistently with every archive in this batch. The audit's three "
         "files are write-once and are not expected to move, but the batch's other archives bind "
         "this queue and the goal head, which do move, and a batch with two binding modes is a "
         "batch whose reader has to work out which rule applies where."),
        ("receipt_note",
         "The receipt must disclose one thing plainly: THE COORDINATOR READ THESE THREE FILES "
         "BEFORE THIS COMMIT EXISTED. They arrived as an uncommitted working tree, the Coordinator "
         "read the verdict to decide what to do next, and only then were they staged. That is the "
         "ordinary shape of a producer returning into a shared worktree, and the honest mitigation "
         "is the receipt's own hashes plus the fact that the audit made no write after it reported "
         "-- not a claim that custody was unbroken. An independent reviewer reads them from this "
         "commit, which is the custody that matters for the review round."),
    ])),
    ("handoff", od([
        ("objective", "Make the audit durable and citable, and bind its bytes."),
        ("uncertainty_reduced", "none; durability"),
        ("inputs", collision_artifacts),
        ("constraints", [
            "STAGE ONLY THE THREE DECLARED AUDIT PATHS AND THIS RECEIPT. `git add -A` here would "
            "sweep in a concurrent lane's in-flight ledger edits -- BATCH-e0a0c1 opened on this "
            "same goal while the audit was running and its own executor flagged the hazard in its "
            "completion gate.",
            "Never edit an audit artifact while staging it.",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 600),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", ["post-commit receipt verified by research_dispatch.py"]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", RULE),
    ("title",
     "Rule on the collision audit's verdict: what the partial collision changes, whether another "
     "campaign's Macaulay code may be imported, and which of the audit's two reframings bind"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 88),
    ("review_required", False),
    ("depends_on", [AUDIT_SNAPSHOT]),
    ("read_scope", [AUDIT, EXP, REVIEW, "ledger", "experiments/EXP-DREG-001",
                    "experiments/EXP-SIG-007", "experiments/EXP-ECTD-9e4248",
                    "experiments/EXP-ALPF-012", "src/semaev_tree.py"]),
    ("write_scope", [
        f"{EXP}/amendments/",
        REVIEW,
    ]),
    ("write_scope_note",
     f"{EXP}/amendments/ and NOT {EXP}/specification.yaml. The contract is frozen at version 1 and "
     "says so in its own what_changed_at_approval; a ruling that needs the protocol to change "
     "writes an additive amendment under a new id."),
    ("artifact_paths", ruling_artifacts),
    ("handoff", od([
        ("objective",
         "Convert the audit's recommendations into a committed ruling, so that the execution card "
         "is unblocked by a decision a later reader can audit rather than by a task merely having "
         "finished."),
        ("uncertainty_reduced",
         "none about the mathematics. It resolves three OPEN QUESTIONS OF PERMISSION the contract "
         "left silent: may another campaign's Macaulay implementation be imported, does the "
         "unshifted arm report as a replication, and does the known-answer fixture set grow."),
        ("inputs", collision_artifacts + [
            f"{EXP}/specification.yaml dependencies and proof_search_map",
            f"{REVIEW}/review-plan.yaml",
        ]),
        ("constraints", [
            "THE RULING MAY NOT UNDERSTATE THE AUDIT IN THE DIRECTION THAT KEEPS THE RUN ALIVE, "
            "and may not overstate it in the direction that kills the run. Both are steering. Name "
            "the evidence, the test boundary, the remaining uncertainty, and a revisit condition "
            "for anything declined.",
            "DO NOT RESTATE ANY MEASURED DEGREE. The audit deliberately disclosed one scoped "
            "relation between prior unshifted values and this contract's threshold, recorded under "
            "values_disclosed_deliberately in verdict.json with the paths that hold the integers. "
            "Cite it by pointer. A document written to protect a blind assignment has already "
            "leaked the value it protected once in this repository (CORR-20260916-292e53) and the "
            "cheap way not to repeat that is to name paths, never numbers.",
            "The goal head is edited ADDITIVELY. A second lane (BATCH-e0a0c1) is working this same "
            "goal and has already amended the head.",
        ]),
        ("deliverables", [
            f"{RULING} -- the ruling, with the reuse permission stated explicitly either way",
            f"{AMENDMENT} -- whatever the ruling makes binding, additively",
            f"{ADDENDUM_PATH} -- the review plan's blind_from list extended to cover the audit, "
            "because the blind re-derivation of J4 must not be anchored by it",
        ]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 3600),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "the ruling answers Q2 and Q3's permission question in words that an executor can act "
            "on without asking again",
            "every declined recommendation carries a revisit condition",
            "no measured degree appears anywhere in the ruling or its amendment",
        ]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", RULING_ARCHIVE),
    ("title", "Ledger-archive the collision ruling, its protocol amendment and the review-plan "
              "addendum"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 87),
    ("review_required", False),
    ("depends_on", [RULE]),
    ("read_scope", ["ledger", EXP, REVIEW, BASE, AUDIT]),
    ("write_scope", [
        f"{BASE}/archives/{RULING_ARCHIVE}",
        f"ledger/decisions/{RULING}.yaml",
    ]),
    ("artifact_paths", [
        f"{BASE}/archives/{RULING_ARCHIVE}/ledger-receipt.json",
        f"ledger/decisions/{RULING}.yaml",
    ]),
    ("archive", od([
        ("kind", "ledger"),
        ("source_task_ids", [RULE]),
        ("record_ids", [RULING, AMENDMENT, "EXP-SEMBIN-4fa22c", GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit: the goal head moves again at this batch's close, which content_first "
         "would report as corruption of this archive."),
        ("ledger_kind_note",
         "kind `ledger` with no EV-* record, which research_dispatch.py permits and "
         "CORR-20260822-7e98b5 HD-1 records the reason for: a ledger archive's whole content can BE "
         "the decision -- here a protocol amendment and a permission ruling. It promotes nothing "
         "and moves no hypothesis."),
    ])),
    ("handoff", od([
        ("objective",
         "Write the ruling as a decision record and commit it with the amendment and addendum the "
         "RULE card produced."),
        ("uncertainty_reduced", "none; durability before the execution reads the ruling"),
        ("inputs", ruling_artifacts + [f"{AUDIT}/verdict.json"]),
        ("constraints", [
            "stage only declared paths; the concurrent lane's edits are not this commit's",
            "commit message names the task id and every record id",
        ]),
        ("deliverables", ["ledger-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 900),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", ["post-commit receipt verified by research_dispatch.py"]),
    ])),
]))

# ---------------------------------------------------------------------------
# THE TWO CARDS BELOW RACE THE EXECUTOR, AND THAT IS THE POINT.
#
# TASK-20260916-64a93b -- a blind source read in the OTHER lane on this goal
# (BATCH-e0a0c1) -- returned while EXECUTE was already running, carrying an exact
# computation over F_2 that predicts d'_F(A-SHIFTED) <= 4 with NON-ZERO shifts.
# H-SEMBIN-a7e721's mechanism predicts the shifted arm rises. Those cannot both
# be right, and which one the measurement lands on is only interesting if the
# prediction is on record BEFORE the measurement.
#
# `depends_on` is EMPTY and cannot be otherwise: the input is a task in a
# different queue, and depends_on names tasks in this one. That is a real
# limitation of a per-batch queue and it is recorded here rather than papered
# over with a fake dependency. The prose below and the addendum itself name the
# cross-lane source.
tasks.append(od([
    ("id", PRIOR),
    ("title",
     "Record the Coordinator's pre-measurement prior for the shifted arm, reversed by a blind read "
     "in the other lane, BEFORE the running executor produces a number"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 89),
    ("priority_note",
     "ABOVE the ruling cards despite being authored after them. Priority here is urgency, not "
     "importance: this card's value decays to zero the moment EXECUTE writes its first artifact, "
     "and every other queued card's value does not decay at all."),
    ("review_required", False),
    ("depends_on", []),
    ("depends_on_note",
     "Empty, and not because this card has no input. Its input is TASK-20260916-64a93b in "
     "BATCH-e0a0c1's queue; depends_on can only name tasks in THIS queue, so the cross-lane "
     "dependency is recorded in prose and in the addendum's own provenance block. Do not read the "
     "empty list as independence."),
    ("read_scope", [
        f"coordination/goals/{GOAL}/batches/BATCH-e0a0c1/read-semaev-2015-310",
        REVIEW,
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "ledger/corrections/CORR-20260916-96f47d.yaml",
        f"{EXP}/specification.yaml",
    ]),
    ("write_scope", [REVIEW]),
    ("artifact_paths", [PRIOR_ADDENDUM_PATH]),
    ("handoff", od([
        ("objective",
         "Put a falsifiable numeric prediction, and what each possible outcome would mean, on the "
         "record while the outcome is still unknown."),
        ("uncertainty_reduced",
         "NONE about the mathematics -- this card measures nothing. What it removes is the "
         "possibility of narrating any measured value as expected after the fact."),
        ("inputs", [
            f"coordination/goals/{GOAL}/batches/BATCH-e0a0c1/read-semaev-2015-310/report.md",
            f"coordination/goals/{GOAL}/batches/BATCH-e0a0c1/read-semaev-2015-310/attestation.yaml",
            f"coordination/goals/{GOAL}/batches/BATCH-e0a0c1/read-semaev-2015-310/recheck.json",
            "ledger/hypotheses/H-SEMBIN-a7e721.yaml mechanism, the premise now predicted false",
        ]),
        ("constraints", [
            "THE PREDICTION IS COMMITTED BEFORE ANY ARTIFACT EXISTS UNDER "
            f"{EXP}/code OR {EXP}/runs, and the commit is the proof. Do not assert "
            "pre-registration in prose; make it checkable with git ls-tree.",
            "DO NOT TELL THE RUNNING EXECUTOR. Its declared read_scope excludes this directory and "
            "it was not informed. Telling a measurer the expected answer destroys the measurement, "
            "and this program has already leaked a protected value once (CORR-20260916-292e53).",
            "EVERY OUTCOME GETS ITS READING IN ADVANCE, including the one that refutes the prior "
            "and the one where the run is censored. An outcome table written after the fact is a "
            "narration.",
            "A PRIOR IS NOT EVIDENCE and does not amend the frozen contract. It cannot move a "
            "hypothesis, cannot relax the amendment, and cannot reassign a joint.",
        ]),
        ("deliverables", [
            f"{PRIOR_ADDENDUM_PATH} -- the prior, its mechanism, its falsification table, its scope "
            "limits, and the additive obligations it puts on J1 and J2",
        ]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 1800),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "the prediction is a number with a direction, not a hedge",
            "every outcome including refutation and censoring has a pre-recorded reading",
            f"the addendum is committed at a tree where {EXP}/runs does not exist",
            "the addendum adds no joint reassignment and lifts no blindness",
        ]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", PRIOR_ARCHIVE),
    ("title", "Snapshot-archive the pre-measurement prior immediately, so the tree proves it "
              "preceded the measurement"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 89),
    ("review_required", False),
    ("depends_on", [PRIOR]),
    ("read_scope", [REVIEW, BASE]),
    ("write_scope", [
        f"{BASE}/archives/{PRIOR_ARCHIVE}",
    ]),
    ("artifact_paths", [
        f"{BASE}/archives/{PRIOR_ARCHIVE}/snapshot-receipt.json",
    ]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [PRIOR]),
        ("record_ids", [ROUND, "EXP-SEMBIN-4fa22c", GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit, for a reason specific to this archive: its whole purpose is to pin a "
         "tree state that LATER COMMITS WILL CHANGE -- the executor is writing into "
         f"{EXP} as this commits. content_first at HEAD would report the archive as corrupt within "
         "the hour, which is exactly the defect CORR-20260915-654160 records."),
        ("what_this_archive_asserts",
         "ONE thing, and it is a fact about the tree rather than about the mathematics: at this "
         f"commit, {PRIOR_ADDENDUM_PATH} exists and no artifact exists under {EXP}/code or "
         f"{EXP}/runs. A later reader confirms it with `git ls-tree -r <commit> -- {EXP}` and does "
         "not have to trust the receipt's prose."),
    ])),
    ("handoff", od([
        ("objective",
         "Commit the prior now. Not at batch close, not with the reader package, not after the "
         "measurement -- now, because the commit timestamp relative to the run artifacts IS the "
         "evidence that this was a prediction."),
        ("uncertainty_reduced", "none; durability, and specifically durability with a provable order"),
        ("inputs", [PRIOR_ADDENDUM_PATH]),
        ("constraints", [
            "stage ONLY the declared paths. Two other lanes are writing into this worktree and the "
            "executor's output must NOT be swept into this commit -- doing so would destroy the "
            "very ordering this archive exists to establish.",
            f"verify and record in the receipt that {EXP}/code and {EXP}/runs are absent from the "
            "committed tree",
            "commit message names the task id and the cross-lane read that caused it",
        ]),
        ("deliverables", ["snapshot-receipt.json, with the absence check recorded"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 900),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            f"the receipt records the checked absence of {EXP}/runs at the commit",
        ]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", EXECUTE),
    ("title",
     "Execute EXP-SEMBIN-4fa22c: implement the summation-polynomial descent with its coset shifts, "
     "measure d'_F per arm per n against the matched unshifted pair and both null objects, and "
     "report the instrument's blindness to the true degree as a success criterion"),
    ("role", "executor"),
    ("state", "blocked"),
    ("blocked_reason",
     "Deliberately NOT `queued`. This card is unblocked by a COORDINATOR RULING on "
     f"{COLLISION}'s verdict, not merely by that task completing: a collision may reframe this run "
     "as a replication, may hand it an existing validated instrument to use instead of writing a "
     "third one (Q2, Q3), or may contradict the prediction outright and make the run unnecessary. "
     "Dispatching this the moment the audit returns would waste the audit. The ruling is a "
     "committed decision that moves this card to `queued` and records what it changed."),
    ("role_note",
     "Executor, not validator: this card builds an instrument and records observations. It does not "
     "interpret them, and the review round that will is a separate batch."),
    ("priority", 86),
    ("review_required", True),
    ("depends_on", [COLLISION, RULING_ARCHIVE]),
    ("depends_on_note",
     "BOTH, and the second is the point of the first. This card was written `blocked` on a "
     f"COORDINATOR RULING rather than on {COLLISION} finishing, and the dependency on "
     f"{RULING_ARCHIVE} is what makes that mechanical: the ruling has to be COMMITTED before this "
     "runs, not merely decided in a session that will not survive."),
    ("read_scope", [
        f"{EXP}/specification.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "ledger/decisions/DEC-20260916-88ac73.yaml",
        "ledger/decisions/DEC-20260916-6ce039.yaml",
        "ledger/corrections/CORR-20260916-96f47d.yaml",
        "ledger/corrections/CORR-20260916-33068f.yaml",
        "coordination/review/sembin-20260916-propquant",
        AUDIT,
        "inputs/NAGAO-2015-984",
        "templates/research-records.md",
        "docs/claims-and-verification.md",
        # Added when the card was unblocked. The ruling that unblocked it is
        # binding beside the frozen contract, and its A-1 grants READ access to
        # named files; a read scope is closed, so a file not listed here is a
        # file the executor cannot open however the ruling reads.
        f"ledger/decisions/{RULING}.yaml",
        AMENDMENT_PATH,
        "experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py",
        "experiments/EXP-ECTD-9e4248/driver/reused/mvpoly.py",
        "experiments/EXP-SIG-007/src/ic_first_fall_fast.py",
        "experiments/EXP-ALPF-012/source/round006_exp011_binary_fppr.sage",
        "src/semaev_tree.py",
    ]),
    ("read_scope_note",
     "WIDENED AT UNBLOCK, 2026-09-16T12:05Z, and not before: the card was written `blocked` on a "
     f"ruling that did not yet exist, so its opening read scope could not name {RULING} or "
     f"{AMENDMENT}. The ruling's A-1 permits reading the five reference files listed last and "
     "using macaulay.rank_mod_p as a TEST ORACLE under A-4 -- never in the measurement path -- "
     "and A-2, A-3 and A-4 bind the builder, the unshifted arm's report and the C-3 fixture set. "
     "An executor that can see only the frozen contract cannot honour any of them, and the "
     "amendment's own A-1 requires the run manifest to record which of these files were read."),
    ("write_scope", [f"{EXP}/code/", f"{EXP}/runs/"]),
    ("write_scope_note",
     "Exactly the contract's own write_scope_when_dispatched. The run id is allocated by the "
     "executor with tools/allocate_id.py --next run and confirmed with --check before use."),
    ("artifact_paths", [
        f"{EXP}/code/CODE_SHA256.json",
        f"{EXP}/runs/INDEX.json",
    ]),
    ("artifact_paths_note",
     "TWO FIXED PATHS THAT BETWEEN THEM NAME EVERYTHING ELSE, because the run id does not exist "
     f"until this task allocates it and so no path under {EXP}/runs/RUN-.../ can be declared here. "
     "CODE_SHA256.json enumerates every code file that ran with its hash; runs/INDEX.json is a "
     "one-object file naming the allocated run directory and listing the artifacts it contains. The "
     "indirection is deliberate: a card that guesses run paths is a card that gets amended. "
     "BATCH-a33cda paid for the alternative -- its executor card named epoch 1's paths, epoch 2 "
     "produced seven more, and the archive had to be additively amended mid-batch "
     "(TASK-20260915-7da7f1 receipt-scope-note.json). The contract's required_artifacts remains the "
     "binding statement of WHAT must exist; these two paths are how the archive FINDS it."),
    ("handoff", od([
        ("objective",
         "Produce the measured d'_F table of EXP-SEMBIN-4fa22c with its controls. You do NOT "
         "conclude anything about Nagao's Proposition 5, and the contract's S-1 makes that explicit: "
         "a measured d'_F > 4 is CONSISTENT with d_F <= 4 because Lemma 4 runs d_F <= d'_F, and this "
         "instrument is structurally blind to the X^2 -> X falls that make d_F small. Your report "
         "says so in those words."),
        ("uncertainty_reduced",
         "The value of d'_F at the coset-shifted EQS4 instances, and whether it separates from the "
         "matched unshifted pair and from two null objects of the same shape."),
        ("inputs", [
            f"{EXP}/specification.yaml -- the frozen contract. Its declared_conventions, arms, "
            "metrics M-1..M-5, controls C-1..C-6, success criteria S-1..S-7, stopping rules "
            "SR-1..SR-5 and required_artifacts are binding and are not yours to reinterpret.",
            "coordination/review/sembin-20260916-propquant/coordinator-recheck.py -- the C-3 "
            "known-answer fixture's hand algebra, already verified.",
            f"{AUDIT}/verdict.json -- the collision audit, and any Coordinator ruling on it.",
            f"{AMENDMENT_PATH} -- the ruling's additive protocol amendment, BINDING beside the "
            "frozen contract: A-1 (reuse as reference and test oracle only, with every read "
            "recorded in the run manifest), A-2 (one builder for both arms, A-UNSHIFTED at "
            "v = 0), A-3 (the unshifted arm reports as a replication with a changed instrument), "
            "A-4 (the GF(2) rank kernel is checked against an independent computation before any "
            "Nagao instance is measured, inheriting SR-3), and R-2 declined.",
            f"ledger/decisions/{RULING}.yaml -- the committed ruling that unblocked this card.",
        ]),
        ("constraints", [
            "CONTROLS BEFORE BELIEF, AND IN THAT ORDER. C-3's known-answer fixture runs FIRST and "
            "SR-3 stops the whole run if it fails -- measuring an unknown with an instrument that "
            "fails a known is worthless. C-2's null arms are reported BEFORE any target value is "
            "interpreted (S-6).",
            "THE SHIFTS ARE PART OF THE INSTANCE (DC-3). A descent without them is EQS2 and may not "
            "be reported against Proposition 5. Record every v_i explicitly as a field element.",
            "IMPORT NOTHING from EXP-ICPERF's converter (contract dependencies). If the collision "
            "audit identified an existing validated Macaulay instrument and a Coordinator ruling "
            "permits it, that permission is in the ruling and nowhere else.",
            "NO WALL-TIME RATIO between two measurements that both finish inside the resident-set "
            "poll interval, and record the interval beside every wall figure (M-5). "
            "CORR-20260916-33068f measured a 51x inflation from exactly this in another campaign.",
            "RESIDENT-SET watchdog, NEVER RLIMIT_AS. An RLIMIT_AS cap aborts algebra engines that "
            "reserve far more address space than they touch; this program has already paid for that "
            "mistake once.",
            "A CENSORED OBSERVATION IS NOT A VALUE AND IS NOT A NEGATIVE RESULT. If no fall is "
            "found within budget, M-1 is `> d_max_reached` (SR-1). Never 'no fall exists'.",
            "A watchdog kill or infrastructure failure is `failed_infrastructure` and is never "
            "negative mathematical evidence (SR-5, core rule 5).",
            "If the tree is dirty when you run, record the per-file sha256 of every code file that "
            "ran -- a recorded commit that does not contain the bytes that ran recovers nothing "
            "(CORR-20260916-33068f D-2).",
            "WRITE ONLY INSIDE YOUR WRITE SCOPE, and never edit an already-committed artifact. Two "
            "concurrent sessions have now done that in this repository within a day "
            "(CORR-20260916-5166fe, CORR-20260916-2e9bc3); a correction supersedes by adding a file, "
            "never by editing one.",
        ]),
        ("deliverables", [
            "the implementation under experiments/EXP-SEMBIN-4fa22c/code/ with a CODE_SHA256.json "
            "enumerating every code file that ran, with its hash",
            "a run directory with a manifest carrying every field of the contract's "
            "required_artifacts",
            "experiments/EXP-SEMBIN-4fa22c/runs/INDEX.json -- the run id you allocated and the "
            "artifacts inside it. This is how the producer snapshot finds a directory whose name "
            "did not exist when its card was written; without it the archive has to guess.",
            "the full Macaulay rank series M-3 as machine-readable rows, from which M-1 is "
            "re-derivable WITHOUT re-running the algebra",
            "M-1, M-2, M-4, M-5 per arm per n with censoring flags",
            "the C-3 fixture verdicts, the C-4 order-sensitivity comparison, the C-6 "
            "both-placements comparison",
            "a per-criterion verdict table for S-1..S-7",
        ]),
        ("inference", od([
            ("policy", "executor-implementation"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note",
             "TRUE, declared up front, matching the contract's own inference block "
             "(DEC-20260916-7b2235)."),
            ("degraded_allowed", False),
            ("degraded_requirements_expected", [
                "model_verified false: no backend is probeable in this checkout.",
            ]),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 43200),
            ("wall_clock_seconds_note",
             "The contract's total. Per arm per n is 1800 s (SR-1)."),
            ("memory_gb", 10),
            ("memory_note", "RESIDENT SET, not address space."),
            ("maximum_runs", 4),
        ])),
        ("completion_gate", [
            "C-3's known-answer fixture has a recorded verdict, and if it failed the run stopped "
            "there (SR-3)",
            "C-2's null arms are reported before any target interpretation (S-6)",
            "every S-1..S-7 criterion carries PASS or FAIL with its evidence",
            "M-1 is re-derivable from the recorded M-3 series without re-running the algebra",
            "the report states, in words, that this instrument cannot refute Proposition 5 (S-1)",
            "runs/INDEX.json names the allocated run directory and every artifact in it",
        ]),
        ("dispatch_preconditions", [
            f"{COLLISION} has a completed receipt AND a committed Coordinator ruling on its verdict "
            "that moves this card from `blocked` to `queued`",
        ]),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", PRODUCER_SNAPSHOT),
    ("title",
     "Snapshot-archive whatever the execution produced, before any independent review reads it"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 70),
    ("review_required", False),
    ("depends_on", [EXECUTE]),
    ("retargeted_note",
     f"OPENED owning both producers; retargeted 2026-09-16 to {EXECUTE} alone once the audit "
     f"returned, because the audit's artifacts had to be committed before the ruling that reads "
     f"them and this archive cannot run until the execution it also owned has happened. The audit "
     f"is now archived by {AUDIT_SNAPSHOT}. See tasks_state_revisions."),
    ("read_scope", [BASE, EXP, "ledger"]),
    ("write_scope", [f"{BASE}/archives/{PRODUCER_SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{PRODUCER_SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [EXECUTE]),
        ("record_ids", ["EXP-SEMBIN-4fa22c", "H-SEMBIN-a7e721", GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit: the contract advances to `completed` after this archive and the goal "
         "head is reranked, both of which content_first would report as corruption."),
        ("receipt_note",
         "This archive is what an independent review round reads. It stages the run directory the "
         "executor allocated, whose paths cannot be predeclared in the executor's card -- the "
         "receipt records what was actually staged with its hashes, which is the binding statement."),
    ])),
    ("handoff", od([
        ("objective",
         "Commit the exact producer artifacts an independent review will read, and record what was "
         "staged with its hashes."),
        ("uncertainty_reduced", "none; durability before review"),
        ("inputs", [f"{EXP}/code/", f"{EXP}/runs/"]),
        ("constraints", [
            "stage only declared paths, and enumerate the run directory as actually produced",
            "commit message names the task id and every record id",
            "never edit a producer's artifact while staging it -- supersede outside its directory "
            "if something is wrong (CORR-20260916-2e9bc3)",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 1800),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", ["post-commit receipt verified by research_dispatch.py"]),
    ])),
]))

# ---------------------------------------------------------------------------
REVIEWER_READ_SCOPE = [
    f"{EXP}/",
    f"{REVIEW}/review-plan.yaml",
    REVIEW_ADDENDUM,
    AUDIT,
    "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
    "ledger/decisions/DEC-20260916-88ac73.yaml",
    "ledger/corrections/CORR-20260916-96f47d.yaml",
    "coordination/review/sembin-20260916-propquant",
    "inputs/NAGAO-2015-984",
    "templates/research-records.md",
]


def reviewer(task_id, title, joints, objective, questions, extra_constraints=(), *,
             read_scope=REVIEWER_READ_SCOPE, read_scope_note=None, extra_inputs=(),
             extra_artifacts=(), extra_deliverables=(), extra_gate=(), extra_preconditions=()):
    """One reviewer card. Two of these make up REVIEW-SEMBIN-20260916-cbb416's round.

    Split the way ICPERF's BATCH-a33cda split its round, and for the reason that
    batch learned: one reviewer owns every joint that requires READING THE RUN
    (the object, the instrument, the controls, the accounting), the other owns
    ONLY the blind re-derivation and reads nothing under the plan's `blind_from`.
    The first draft of this queue put J3/J4 and the blind re-derivation on one
    card; since J3/J4 cannot be checked without opening
    experiments/EXP-SEMBIN-4fa22c/runs/ and tools/check_review_independence.py
    reports ANY attested read under `blind_from` as a leak, that card's own
    completion gate could not be passed by an honest reviewer. A reviewer told
    only to "review this" converges on whatever is most legible, so the joints
    are still enumerated and owned one by one.
    """
    return od([
        ("id", task_id),
        ("title", title),
        ("role", "validator"),
        ("state", "queued"),
        ("priority", 60),
        ("review_required", False),
        ("depends_on", [EXECUTE, PRODUCER_SNAPSHOT]),
        ("depends_on_note",
         "BOTH, and each for its own reason. On EXECUTE because this card reviews that execution and "
         "the dependency is what records the reviewer as its independent successor. On "
         "PRODUCER_SNAPSHOT because a reviewer must read committed, pushed artifacts rather than a "
         "working tree -- if the tree can still move underneath a review, custody is exactly what "
         "breaks, which BATCH-a33cda's R5 verdict recorded from experience."),
        ("read_scope", list(read_scope)),
    ] + ([("read_scope_note", read_scope_note)] if read_scope_note else []) + [
        ("write_scope", [f"{REVIEW}/{task_id}/"]),
        ("artifact_paths", [
            f"{REVIEW}/{task_id}/report.md",
            f"{REVIEW}/{task_id}/attestation.yaml",
        ] + list(extra_artifacts)),
        ("review_plan_ref", f"{REVIEW}/review-plan.yaml"),
        ("review_plan_addendum", [REVIEW_ADDENDUM]),
        ("joints_owned", joints),
        ("handoff", od([
            ("objective", objective),
            ("uncertainty_reduced",
             "Whether the joints assigned to you hold. NOT whether the claim as a whole holds -- "
             "you are blinded from your sibling's joints by construction, so a whole-claim verdict "
             "from you would be an opinion formed from a fraction of the evidence. The Coordinator "
             "composes."),
            ("inputs", [
                f"{REVIEW}/review-plan.yaml -- your joints, their worked attack plans, and where "
                "the Coordinator thinks each one breaks. The Coordinator's priors are recorded "
                "there BEFORE you ran; overturning one is among the most informative things you "
                "can return.",
                f"{REVIEW_ADDENDUM} -- ADDITIVE companion to the plan, written before any reviewer "
                "ran: reassigns J3 and J4 so that the blind re-deriver reads nothing under "
                "blind_from. The plan and this addendum together are the round's declaration.",
                f"{EXP}/specification.yaml -- the frozen contract. Binding.",
            ] + list(extra_inputs)),
            ("constraints", [
                f"DO NOT READ your sibling reviewer's directory under {REVIEW}/. Record it in a "
                "`did_not_read` list in your attestation.",
                "RE-DERIVE, DO NOT RE-RUN. Where the plan asks you to check a quantity, compute it "
                "your own way from the contract's definitions. Recomputing from the producer's own "
                "artifacts reproduces a wrong-but-self-consistent implementation faithfully, which "
                "is exactly the failure this round cannot otherwise see.",
                "WRITE ONLY INSIDE YOUR WRITE SCOPE, and never modify a producer's committed "
                "artifact. Two concurrent sessions did that in this repository within one day "
                "(CORR-20260916-5166fe, CORR-20260916-2e9bc3) and one of them was corrected for "
                "editing a reviewer's own filed report. A finding supersedes by adding a file.",
                "DO NOT COMMIT. The Coordinator archives.",
                "YOU MAY NOT CERTIFY A REFUTATION OF PROPOSITION 5 whatever the run measured "
                "(DC-1). The instrument is structurally blind to the X^2 -> X falls that make d_F "
                "small. A report phrased as a refutation is an S-1 FAILURE of the run, and saying "
                "so is your job.",
                "A verdict of `breaks` on a joint is a normal and valuable outcome. So is "
                "`cannot determine`, with what it would take stated.",
                "Record `requested_policy`, `resolved_model_id`, `fallback_used` with its reason, "
                "and `model_verified` in your attestation. See the plan's inference.model_note: "
                "the binding here is declared, not discovered.",
            ] + list(extra_constraints)),
            ("questions", questions),
            ("deliverables", [
                "report.md -- one section per joint you own, each with a verdict "
                "(holds | breaks | cannot determine), the evidence, and what you re-derived versus "
                "took on trust",
                "attestation.yaml -- per-joint verdicts, `read_sibling_reports: false`, a "
                "`did_not_read` list, a `sources_read` list, what you re-derived, what you took on "
                "trust, what you could not verify and what it would cost to, and your inference "
                "provenance",
            ] + list(extra_deliverables)),
            ("inference", od([
                ("policy", "review-adversarial"),
                ("reasoning_effort", "xhigh"),
                ("fallback_allowed", True),
                ("fallback_note",
                 "TRUE, declared in the review plan before the round rather than amended after a "
                 "reviewer returns -- which is what BATCH-a33cda had to do "
                 "(DEC-20260916-7b2235). No adapter backend is credentialed here."),
                ("degraded_allowed", False),
                ("degraded_requirements_expected", [
                    "model_verified false: no backend is probeable in this checkout.",
                ]),
                ("independent_session_required", True),
            ])),
            ("budget", od([
                ("wall_clock_seconds", 10800),
                ("memory_gb", 4),
                ("maximum_runs", 0),
                ("maximum_runs_note",
                 "Zero SCIENTIFIC runs. Re-deriving a quantity and running the known-answer "
                 "fixtures is review work, not a run of the experiment, and is expected."),
            ])),
            ("completion_gate", [
                "every joint you own carries a verdict with its evidence",
                "attestation.yaml records read_sibling_reports false and a did_not_read list",
                "tools/check_review_independence.py raises no problem against this task",
            ] + list(extra_gate)),
            ("dispatch_preconditions", [
                f"{PRODUCER_SNAPSHOT} has a verified snapshot receipt, so you read committed "
                "producer artifacts rather than a working tree",
                f"{REVIEW_ADDENDUM} is committed and pushed, so the joint assignment you are "
                "handed is the one the round declares",
            ] + list(extra_preconditions)),
        ])),
    ])


tasks.append(reviewer(
    REVIEW_INSTRUMENT,
    "Review J1-J5 of REVIEW-SEMBIN-20260916-cbb416: is the measured object the coset-shifted EQS4 "
    "descent the contract names, does the code compute d'_F rather than something near it, do the "
    "null objects actually discriminate, is any absence being written up as a fact, and does the run "
    "state its own blindness to the true degree",
    ["J1", "J2", "J3", "J4", "J5"],
    "Attack the object, the instrument, the controls and the accounting -- every joint that requires "
    "reading the run. Establish independently whether the systems measured are the ones "
    "EXP-SEMBIN-4fa22c specifies, whether the integer it reports is the quantity the contract "
    "defines, whether a reported separation is a fact about the summation polynomial or about the "
    "shape of a degree-3 Boolean system, whether every censored arm, watchdog kill and wall figure "
    "is reported as what it is, and whether the report states in words that it cannot refute "
    "Proposition 5. The blind re-derivation is NOT yours: your sibling derives d'_F and M-2 without "
    "opening the run, which is why you may.",
    [
        "Recompute the descent for the smallest n from Nagao's definitions rather than from the "
        "executor's code, and compare against the recorded M-4 hash. Do the two arms differ in "
        "EXACTLY the recorded shifts?",
        "Is every recorded v_i non-zero as a field element in the recorded basis of V (DC-3)? Is the "
        "curve non-Koblitz?",
        "Re-run C-3's fixtures yourself: fake quantity 2 for f1 = X1X2 + X3, f2 = X1 + X2, and true "
        "first fall 3 for the same pair with the field equations OUTSIDE. Does the instrument agree?",
        "Add a generator pair whose only fall is the trivial Koszul syzygy. Does M-1 stay put while "
        "M-2 moves? This is where the Coordinator expects the instrument to be wrong.",
        "Does the equality form of condition (1) -- all products at the same degree d, combination "
        "strictly below d -- match what the code implements, or is there an off-by-one?",
        "C-6: can the run demonstrate WHICH field-equation placement it computed? An instrument that "
        "cannot show this may not be cited on Lemma 4 in either form.",
        "S-1 and S-5: find the sentence. Both consequences for every measured value, and a "
        "confirmation direction carrying its dependence on Lemma 4's unproven inside form?",
        "J3. Are the ten draws per null arm ten DISTINCT seeded draws? Regenerate two from their "
        "recorded seeds -- do they reproduce?",
        "J3. Does A-NULL-SHUFFLED preserve the exact global monomial multiset of A-SHIFTED? Count "
        "it; do not trust the label.",
        "J3. Did the run stay within maximum_runs 4? A fifth pass over the n-series is the shape of "
        "re-rolling nulls until they cooperate and would void C-2 entirely.",
        "J3. S-6: are the nulls reported BEFORE any target value is interpreted, or is the headline "
        "first and the control a later section? The Coordinator expects the ordering to be where "
        "this breaks.",
        "J4. For every arm with no fall found: does the record say `> d_max_reached` rather than "
        "'no fall', and does NO downstream sentence treat it as a measured value (SR-1)?",
        "J4. Is every watchdog kill or infrastructure failure recorded as `failed_infrastructure` "
        "and cited nowhere as evidence about Nagao (SR-5)?",
        "J4. Read the recorded poll interval. Does any reported wall RATIO involve two measurements "
        "that both finish inside it (CORR-20260916-33068f measured a 51x inflation from exactly "
        "this)?",
        "J4. C-5: is the series shown, or is monotonicity asserted? A non-monotone series is an "
        "INSTRUMENT signal first (F-4) -- was it rationalised as a fact about the systems?",
    ],
    extra_constraints=(
        "The proves-too-much control is YOURS (review plan, proves_too_much): run the argument "
        "against a system with a PLANTED fall at degree 3, where its conclusion is known false. The "
        "instrument must find that fall at 3. And against a Koszul-only system, where it must find "
        "no non-trivial fall at all.",
        f"NEVER QUOTE A MEASURED d'_F OR M-2 VALUE outside your own directory -- not in a bus "
        f"message, not in a commit message, not in a note. Your sibling {REVIEW_BLIND} derives "
        "those integers blind, and the plan's blind_from_note makes this a standing obligation on "
        "every document in the campaign.",
    ),
    extra_inputs=(f"{AUDIT}/verdict.json -- the pre-compute collision audit.",),
))

tasks.append(reviewer(
    REVIEW_BLIND,
    "Blind re-derivation for REVIEW-SEMBIN-20260916-cbb416: derive d'_F and M-2 at the smallest "
    "completed A-SHIFTED instance from the contract's definitions and the instance description alone, "
    "pre-register them write-once, and only then compare",
    ["blind_rederivation"],
    "Independently derive d'_F for the A-SHIFTED arm and M-2 (the trivial-Koszul ceiling) at the "
    "smallest n the run completed, from Nagao's definitions, the contract's declared_conventions and "
    "the instance description the Coordinator hands you -- never from the producer's code or run. "
    "Agreement between two implementations sharing no code is evidence about the quantity; "
    "disagreement localises to one of two named implementations. Recomputing from the producer's "
    "artifacts would reproduce a wrong-but-self-consistent implementation faithfully, which is the "
    "one failure this round cannot otherwise see.",
    [
        "From the instance description alone: what is d'_F at the smallest completed n under the "
        "contract's equality-form convention on condition (1), with the field equations placed as "
        "declared_conventions places them?",
        "What is M-2, the degree at which the trivial Koszul syzygies alone first produce a fall, "
        "at the same instance?",
        "Does your derivation route share ANY code with anything under "
        "experiments/EXP-SEMBIN-4fa22c/? It must not, and your report says how you know.",
        "You do NOT compare against the run; your deliverable is the pre-registered pair and the "
        "route that produced it. The Coordinator compares at composition and reports agreement or "
        "disagreement beside your timestamp.",
    ],
    extra_constraints=(
        "THE BLIND RE-DERIVATION IS YOURS, AND ITS PROCEDURE IS MANDATORY AND ORDERED. Before you "
        "open anything beyond your declared read scope, derive d'_F and M-2 at the smallest "
        "completed instance from the contract's definitions and blind-instance.yaml alone, and "
        "write them with your method, exact command and input hash to PREREGISTERED-VALUES.json in "
        "your write scope. WRITE-ONCE: no edits, not even to fix a typo -- append a second file. "
        "This ordering is what makes your number evidence regardless of what you encounter "
        "afterwards, and it is required because the last blind assignment in this repository was "
        "leaked by the very document written to protect it (CORR-20260916-292e53).",
        "BLIND, AS A MATTER OF PATHS: do not open experiments/EXP-SEMBIN-4fa22c/code/, "
        "experiments/EXP-SEMBIN-4fa22c/runs/, this batch's archives/, or your sibling's directory "
        "-- the plan's blind_from -- at ANY point, before or after pre-registration. "
        "tools/check_review_independence.py reports an attested read under blind_from as a failed "
        "re-derivation and has no after-registration exception; that is why J3 and J4, which "
        "cannot be checked without opening the run, are your sibling's and not yours. List every "
        "path you did read in attestation.yaml `sources_read` and set `blind_from_respected: true` "
        "only if it is true.",
        "Disclose any exposure you encounter, with WHEN, measured against your pre-registration. "
        "Exposure after it costs the joint nothing; exposure before it means your number is "
        "reported as informed rather than independent. Disclosing is the behaviour that preserves "
        "the joint's value -- it is not a failure.",
        "The comparison against the producer's value happens at composition, by the Coordinator, "
        "who reads the run and you do not. Disagreement is a finding, not a failure: do not "
        "resolve it by adopting theirs.",
    ),
    read_scope=[
        f"{REVIEW}/review-plan.yaml",
        REVIEW_ADDENDUM,
        BLIND_INSTANCE,
        f"{EXP}/specification.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "inputs/NAGAO-2015-984",
        "templates/research-records.md",
    ],
    read_scope_note=(
        "DELIBERATELY NARROW AND DISJOINT FROM THE PLAN'S blind_from. This card's whole value is "
        "that it reads the contract and the instance description and NOT the producer's "
        "implementation or run, so the read scope excludes experiments/EXP-SEMBIN-4fa22c/code/ and "
        "runs/ entirely, this batch's archives/, the collision audit, and the other reviewer's "
        "directory. The instance description it needs -- which the contract records in the run's "
        f"inputs block, under runs/ -- is extracted by the Coordinator to {BLIND_INSTANCE} before "
        "dispatch, with no measured value in it (see dispatch_preconditions). ICPERF's BATCH-a33cda "
        "gave its re-deriver the same shape of scope for the same reason."),
    extra_inputs=(
        f"{BLIND_INSTANCE} -- the smallest completed n, the curve, the basis of V and every coset "
        "shift v_i as field elements, and the contract conventions needed to build the A-SHIFTED "
        "system, copied by the Coordinator from the run's recorded inputs block WITHOUT any "
        "measured value. This is the only thing about the run you are told.",
    ),
    extra_artifacts=(f"{REVIEW}/{REVIEW_BLIND}/PREREGISTERED-VALUES.json",),
    extra_deliverables=(
        "PREREGISTERED-VALUES.json -- d'_F and M-2 with UTC timestamp, method, exact command and "
        "sha256 of your input, WRITE-ONCE, written before any other read. Declared here and in "
        "artifact_paths so the ledger archive hash-binds it: an unbound pre-registration is a "
        "pre-registration whose bytes may drift, which is the hole ICPERF's AP-AMD-1 closed after "
        "research_dispatch.py refused an archive over it.",
    ),
    extra_gate=(
        "PREREGISTERED-VALUES.json exists, carries both integers with method and input hash, and "
        "its recorded timestamp precedes every other read the attestation declares",
        "attestation.yaml `sources_read` intersects none of the plan's blind_from, and "
        "`blind_from_respected` is explicitly true",
    ),
    extra_preconditions=(
        f"The Coordinator has written {BLIND_INSTANCE} from the run's recorded inputs block -- the "
        "smallest completed n, the curve's defining polynomial and coefficients, the basis of V and "
        "every v_i as field elements, and nothing else -- and has re-grepped that file AND the tree "
        "as it then stands for any d'_F, M-1 or M-2 figure, as the plan's blind_from_note requires. "
        "Omitting exactly that re-grep is what caused CORR-20260916-292e53.",
        "No document written as part of this dispatch quotes a measured value; the run record is "
        "cited by path only.",
    ),
))


# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", LEDGER),
    ("title",
     "Ledger-archive the composition of REVIEW-SEMBIN-20260916-cbb416: the evidence record, the "
     "closing decision, whatever hypothesis and experiment status the reviews support, and the "
     "BATCH-cbb416 goal checkpoint"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 50),
    ("review_required", False),
    ("depends_on", [REVIEW_INSTRUMENT, REVIEW_BLIND]),
    ("read_scope", [BASE, REVIEW, EXP, "ledger"]),
    ("write_scope", [
        f"{BASE}/archives/{LEDGER}",
        f"ledger/evidence/{EVIDENCE}.yaml",
        f"ledger/decisions/{CLOSING}.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        f"{EXP}/specification.yaml",
        f"ledger/goals/{GOAL}/checkpoints/",
        REVIEW_ADDENDUM,
        BLIND_INSTANCE,
    ]),
    ("artifact_paths", [
        f"{BASE}/archives/{LEDGER}/ledger-receipt.json",
        f"ledger/evidence/{EVIDENCE}.yaml",
        f"ledger/decisions/{CLOSING}.yaml",
        CLOSING_CHECKPOINT,
        REVIEW_ADDENDUM,
        BLIND_INSTANCE,
    ]),
    ("artifact_paths_note",
     "EVERY PATH THIS ARCHIVE WILL HASH-BIND IS DECLARED HERE, because research_dispatch.py "
     "requires a completed archive's path_sha256 to equal exactly its own artifact_paths plus its "
     "sources' -- a path bound at close time that no card declares is refused as outside the commit "
     "scope, which is what blocked ICPERF's TASK-20260915-efa91b until AP-AMD-1. The checkpoint is "
     f"a NEW shard, {CLOSING_CHECKPOINT}: the opening shard {BATCH}.yaml is write-once and already "
     "committed at d38386a31, so the close cannot be written into it (precedent: "
     "BATCH-ef31ab-close-20260808.yaml). The plan addendum and the blind-instance extract are "
     "Coordinator-written control-plane files of this round that no earlier archive can own, so "
     "this one does; both sit in write_scope for that reason and are not authored by this task."),
    ("archive", od([
        ("kind", "ledger"),
        ("source_task_ids", [REVIEW_INSTRUMENT, REVIEW_BLIND]),
        ("record_ids", [EVIDENCE, CLOSING, "H-SEMBIN-a7e721", "EXP-SEMBIN-4fa22c", GOAL, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit: the goal head is reranked after this archive and the hypothesis may "
         "move again in a later batch, both of which content_first would report as corruption."),
    ])),
    ("handoff", od([
        ("objective",
         "Compose the two reviewers' joint verdicts into one evidence record and one decision, and "
         "commit them with whatever status transitions they actually support."),
        ("uncertainty_reduced",
         "none; this is composition and durability. The uncertainty was reduced by the producers "
         "and tested by the reviewers."),
        ("inputs", [
            f"{REVIEW}/review-plan.yaml -- the joints, the owners, and the Coordinator's priors as "
            "recorded before the round",
            f"{REVIEW_ADDENDUM} -- the J3/J4 reassignment, written before any reviewer ran",
            f"{REVIEW}/{REVIEW_INSTRUMENT}/", f"{REVIEW}/{REVIEW_BLIND}/",
            f"{REVIEW}/{REVIEW_BLIND}/PREREGISTERED-VALUES.json -- compare against the run record's "
            "value HERE, at composition, and report agreement or disagreement with the "
            "pre-registration timestamp beside it",
        ]),
        ("constraints", [
            "COMPOSE, DO NOT AVERAGE. Name every joint, its owner, its verdict and its evidence. A "
            "break on one joint is not outvoted by holds on the others; the plan's "
            "`what_a_break_on_each_joint_costs` states what each one does to the claim.",
            "REPORT EVERY OVERTURNED PRIOR AS SUCH. The plan records four Coordinator priors before "
            "the round, including an expectation that the shuffled null will NOT separate. A review "
            "that overturns one is among the most informative results available and must not be "
            "smoothed into agreement.",
            "A CLAIM PRESENTED AS CONTRADICTING PROPOSITION 5 NEEDS `review-breakthrough` AT MAX, "
            "which is undegradable and cannot be served here. If the evidence points that way, the "
            "claim stays UN-PROMOTED and the campaign stays ACTIVE with a recorded impediment -- "
            "never a substituted cheaper tier, and never a downgraded claim to keep things moving.",
            "AUTHORING AND APPROVING RECORDS IS NOT PROGRESS AGAINST A COMPLETION CRITERION. "
            "CORR-20260916-402547 corrected exactly that error on this goal. Only the run or read "
            "evidence this batch produced can move a criterion, and the decision states which "
            "criteria moved and which did not.",
            "Never edit a producer's or reviewer's committed artifact. Supersede outside its "
            "directory (CORR-20260916-2e9bc3).",
            "Fill `knowledge_promotion` or state why not warranted.",
        ]),
        ("deliverables", [
            f"{EVIDENCE} -- the evidence record, scoped to the tested curves, parameters, arms and "
            "budget, with the instrument's blindness to d_F stated in the scope rather than a "
            "footnote",
            f"{CLOSING} -- the closing decision, its composition of the joints, every overturned "
            "prior, the criteria that moved, and the ranked next action",
            f"{CLOSING_CHECKPOINT} -- the {BATCH} closing checkpoint, as a new write-once shard "
            f"beside the opening one; {BATCH}.yaml is never edited",
            "ledger-receipt.json",
        ]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As every card in this batch: declared up front."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 5400),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "tools/check_review_independence.py raises no problem against the round",
            "every joint in the review plan is named in the decision with its verdict",
        ]),
    ])),
]))


# ---------------------------------------------------------------------------
# POST-EXECUTION FACTS, APPLIED HERE RATHER THAN HAND-EDITED INTO THE JSON.
#
# A generated queue that is amended by hand after every task drifts from its
# generator, and the next regeneration silently discards the execution history.
# BATCH-a33cda carried that hazard and recorded it. So outcomes, archive
# bindings and state revisions live in this table and are APPLIED to the cards
# below, which makes `python3 build_queue.py` idempotent: re-running it
# reproduces the queue including everything that has happened to it.
EXECUTED = {
    OPEN: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16. DEC-20260916-59921c recorded (with the required `decision` field "
         "added before commit, having been caught by validate_ledger.py), the eight-card queue "
         "built, REVIEW-SEMBIN-20260916-cbb416 written before any reviewer was dispatched, the "
         "BATCH-cbb416 checkpoint shard written, and the goal head reranked -- including "
         "CORR-20260916-da9ab9's repair of IMP-SEMBIN-FCB7A2-DESCENT's recheck, which still "
         "pointed at the fabricated run identifier RUN-SEMBIN-8eda8e and at a queue path that has "
         "never existed. Zero runs, zero measurements, no status moved."),
    ]),
    OPEN_SNAPSHOT: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16 at commit d38386a31b6f3356efc3a4de02d53c968204cc91. Staged exactly "
         "the seven declared source artifacts plus its own receipt; the two corrections and the "
         "schema supersession this session also produced were committed separately in 711e5c89b "
         "ahead of the archive so this commit changes exactly its declared set."),
        ("archive_binding", od([
            ("commit_sha", "d38386a31b6f3356efc3a4de02d53c968204cc91"),
            ("parent_sha", "711e5c89b05ea9397a875497e0cd81a64be5fa1a"),
            # Keyed off open_artifacts so the binding cannot name a path the
            # opening task does not declare -- the defect that made
            # BATCH-a33cda's last archive fail to render until its source card
            # was amended.
            ("path_sha256", od([
                # The archive's OWN artifact, which research_dispatch.py requires
                # a completed archive to bind alongside its sources. The receipt
                # cannot carry this value -- a file cannot contain its own hash --
                # so the queue carries it. This is the one hash a reader must take
                # from here rather than from the receipt.
                (f"{BASE}/archives/{OPEN_SNAPSHOT}/snapshot-receipt.json",
                 "86621e13aff90ef8052493b0252b5fb5bfde04027b9021c1fc1b85911da65ba2"),
            ] + list(zip(open_artifacts, [
                "55562b21ee55ddf23e0b5dbc0d2a47195e12736a42cc41d5e44cd57d51469be5",
                "a0bbe535759bc16e2811216bbd78dca501b7926b5e704768b3fe4da85fea25c2",
                "4f781242d82fb12905fdc3bb0e59efb27e8d762a61d1a37b12748ca190544be1",
                "3918592dda834b22c59b0a7d34dfd809ca7c48ac1550ef7231654909014413db",
                "e7ac2d4d91554c6ac3ef125d99f5a9abdfce7970220dae88e0c3e8b9fedfb49d",
                "f03181611c63b1220d5ec89353491d28763413530cf671074c1d5bc55cfbe8bc",
                "c8552620f672cf12556a53e1a35adfa6f398b16807aca6bff673e672069aa362",
            ], strict=True)))),
            ("path_sha256_note",
             "SEVEN ENTRIES, INCLUDING THIS QUEUE AND ITS GENERATOR, which BATCH-a33cda's "
             "equivalent archive could not bind and had to disown under also_staged_sha256. That "
             "batch's own note (`what_content_at_commit_would_additionally_allow`) recorded why the "
             "obstacle was specific to content_first and predicted that a batch declaring "
             "binding_mode content_at_commit from the outset could bind its queue at its own "
             "snapshot commit. This is that batch. The hashes are the bytes AT d38386a31, and both "
             "files have legitimately changed since -- this table is the change. Under "
             "content_at_commit that is verification working, not drift; under content_first it "
             "would read as corruption. EXPECT every LATER archive in this batch to bind a "
             "DIFFERENT snapshot of these same two files."),
        ])),
    ]),
    COLLISION: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16, zero runs and zero measurements, 63 recorded queries over 76,056 "
         "files with four empty results, all six questions answered. Verdict `partial`, "
         "recommendation `proceed`, both marked as recommendations rather than rulings. THE FINDING "
         "THAT MATTERED WAS NOT THE VERDICT: the audit established by reading the code that this "
         "program's shared descent builder cannot construct a shifted instance at all -- "
         "src/semaev_tree.py contains no coset, shift, v_i or offset, and its subspace passes "
         "through the origin -- so every Semaev descent the program has ever built is v = 0, which "
         "is EQS2 in Nagao's own words. The headline arm's novelty therefore rests on a checkable "
         "absence in code rather than on a failure to find a record, which is a much stronger thing "
         "to have, and the control arm turns out to be substantially pre-measured, which is where "
         "the `partial` comes from. The kb retrieval index could not be called (six probes) so "
         "recall is stated as a FLOOR. Ruled on by " + RULING + "."),
    ]),
    AUDIT_SNAPSHOT: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16 at commit 4af041050299e91c0e354effe242bcb7bff545ad. Staged exactly "
         "the three declared audit artifacts plus its own receipt, path by path -- a second lane's "
         "readers were in flight in the same worktree and `git add -A` would have swept them in. "
         "The receipt discloses that the Coordinator read the audit before this commit existed, "
         "which is how a producer returns into a shared worktree, and records that no commit in "
         "that window touched collision-audit/."),
        ("archive_binding", od([
            ("commit_sha", "4af041050299e91c0e354effe242bcb7bff545ad"),
            ("parent_sha", "2324bef46905952710c532f3350c2f6a7fbbd8c8"),
            ("path_sha256", od([
                (f"{BASE}/archives/{AUDIT_SNAPSHOT}/snapshot-receipt.json", RECEIPT_SHA),
            ] + list(zip(collision_artifacts, [
                "bd51ae401f5b018220ac58c3ad5224dec8467d7d3f66c58297100dc88d63556a",
                "66128266e7f42807f42a2c200da293d095f3c274349efc9ce85abe44c42d7b0d",
                "96dd4741f0c0d55a528a4659176fc6678017dc45f72183f4eda6574342353de9",
            ], strict=True)))),
            ("path_sha256_note",
             "Four entries: the three audit artifacts and this archive's own receipt, which "
             "research_dispatch.py requires a completed archive to bind and which the receipt "
             "cannot carry itself."),
        ])),
    ]),
    RULE: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16. " + RULING + " accepts the `partial` verdict as the audit read it "
         "and lets the run proceed; " + AMENDMENT + " makes four things binding additively (A-1 "
         "reuse as reference and test oracle but never in the measurement path, A-2 one builder for "
         "both arms with the control at v = 0, A-3 the unshifted arm reported as a replication with "
         "a changed instrument, A-4 the GF(2) rank kernel checked before it is trusted) and declines "
         "R-2's fixture with a revisit condition; addendum 2 puts the audit and the paths holding "
         "prior integers under the blind re-deriver's blind_from. One audit finding was CORRECTED: "
         "macaulay.rank_mod_p does not degenerate at p = 2, which changes the ruling's reasons and "
         "not its outcome. No measured degree appears in any of the three files."),
    ]),
    RULING_ARCHIVE: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16 at commit 323f22645cfc5d9b89132c25e4fab8eceff32c9e. Three declared "
         "records plus its own receipt, staged path by path with two other lanes in flight in the "
         "same worktree. The receipt also records a defect found while writing the ruling and "
         "deliberately NOT fixed inside an archive commit: this round's review plan declares its "
         "joints as id/name/owner where templates/research-records.md and "
         "tools/check_review_independence.py use joint/assigned_to, so the checker cannot see the "
         "plan's ownership and both reviewer cards' completion gate is unpassable as written. It "
         "bites only when the first reviewer attests, which cannot happen until the execution has "
         "run and been snapshotted."),
        ("archive_binding", od([
            ("commit_sha", "323f22645cfc5d9b89132c25e4fab8eceff32c9e"),
            ("parent_sha", "9bcbd0112a2c1788119475841c16d2a898afd2ee"),
            ("path_sha256", od([
                (f"{BASE}/archives/{RULING_ARCHIVE}/ledger-receipt.json", RULING_RECEIPT_SHA),
                (f"ledger/decisions/{RULING}.yaml",
                 "d3aa82ddd08f8165e98edb4ab39a9ed34b34f9fd82de564d07040a5ae6abe24d"),
                (AMENDMENT_PATH,
                 "a49aa124e169bb1f4ddbe1265928914fee24a640b458f044452038db70a6777e"),
                (ADDENDUM_PATH,
                 "3029f17625ed86cda575599a7c7c4e935985bf2aca4ffb32a8c6d64ad8e815d9"),
            ])),
        ])),
    ]),
    EXECUTE: od([
        ("state", "queued"),
        ("unblocked_by",
         RULING + ", committed at 323f22645 and archived by " + RULING_ARCHIVE + ". The card was "
         "written `blocked` on a ruling rather than on the audit finishing, and this is that "
         "ruling. The executor reads the amendment as binding alongside the frozen contract."),
    ]),
    PRIOR: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16T12:10Z. Authored REVIEW-SEMBIN-20260916-cbb416-ADD3, which records "
         "the reversed prior d'_F(A-SHIFTED) <= 4 at m = 3 with its mechanism, a four-row outcome "
         "table covering refutation and censoring, five scope limits, and additive obligations on "
         "J1 and J2 that reassign nothing. TWO SELF-CORRECTIONS DURING THE WORK, both disclosed in "
         "the artifact rather than smoothed away. First, the draft was FLAT -- a top-level "
         "`extends:` with no `review_plan_addendum:` wrapper -- which parses, validates, and is "
         "SILENTLY IGNORED by compose_plan()'s `_addendum_of`, the worst of the three outcomes "
         "because it reads as a protection that is not in force. Second, the draft header claimed "
         f"{EXP}/code was absent; the executor began implementing between drafting and committing, "
         "so the claim was true when written and false ten minutes later. Narrowed to the claim "
         "that is true -- the prior precedes the MEASUREMENT, not the implementation."),
    ]),
    PRIOR_ARCHIVE: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16 at commit c15dc4318. The archive's substantive content is an "
         "ORDERING CHECK rather than a hash comparison: at that commit the only paths under "
         f"{EXP} are specification.yaml and the collision amendment -- no runs/, no code/ -- so the "
         "tree itself witnesses that the prediction preceded the measurement. Two independent "
         "checks recorded (committed tree via git ls-tree, working tree via ls). Staged path by "
         "path with three lanes writing into the worktree, because sweeping the executor's "
         "untracked code/ into this commit would have destroyed the ordering the archive exists to "
         "establish."),
        ("archive_binding", od([
            ("commit_sha", "c15dc43183f770205c41592e2a5cc691f4a7dd1e"),
            ("commit_sha_note",
             "READ BACK FROM GIT, not typed. The first value written here was a full hash extended "
             "from the abbreviation by hand and it was wrong past the 9th character; "
             "research_dispatch.py refused the queue with `requires archive.commit_sha to resolve "
             "to a commit`, which is the check doing exactly its job. Confirm with "
             "`git log -1 --format=%H` on the commit whose subject names TASK-20260916-d5e431."),
            ("parent_sha", "a98f3334060f82c2c5383a72e6007209472d12d5"),
            ("path_sha256", od([
                (f"{BASE}/archives/{PRIOR_ARCHIVE}/snapshot-receipt.json",
                 "ad4696bfc8c9ef7c8d27887cbbadcdea5aeac86d3c5b91899eedb64b6037e70e"),
                (PRIOR_ADDENDUM_PATH,
                 "1cb56e37d48f77c65cea003f87a24f55660181f4177a4b2edc0257a08d5f381b"),
            ])),
        ])),
    ]),
}

REVISIONS = [
    od([
        ("at", "2026-09-16T10:30:00Z"),
        ("task_id", OPEN),
        ("from_state", "completed"),
        ("to_state", "completed"),
        ("reason",
         "Not a state change. The card was already `completed` when the queue was first written, "
         "which was accurate only in the sense that the opening act had run -- three of its seven "
         "declared artifacts (the checkpoint shard, the opening report, and the goal head edit) did "
         "not yet exist, and its completion gate required the decision to be COMMITTED, which it "
         "was not. All seven now exist and are committed at d38386a31. Recorded rather than "
         "smoothed: a card marked completed ahead of its own completion gate is exactly the kind of "
         "state a later reader cannot distinguish from a card that passed it."),
    ]),
    od([
        ("at", "2026-09-16T10:32:00Z"),
        ("task_id", OPEN_SNAPSHOT),
        ("from_state", "queued"),
        ("to_state", "completed"),
        ("reason",
         "Snapshot archive executed at d38386a31 under binding_mode content_at_commit, binding all "
         "seven declared source artifacts including this queue and its generator. Receipt at "
         f"{BASE}/archives/{OPEN_SNAPSHOT}/snapshot-receipt.json, which records the origin/main "
         "merge (c68e9d4c9, 24 commits, clean, never rebased), the validator outcome scoped to the "
         "paths this commit stages, and the two errors that were this session's and are now closed."),
    ]),
    od([
        ("at", "2026-09-16T11:20:00Z"),
        ("task_id", COLLISION),
        ("from_state", "queued"),
        ("to_state", "completed"),
        ("reason",
         "The audit returned. Its outcome is in the card; the ruling on it is " + RULING + ". Lane "
         f"claim released as `completed` at {BASE}/claims/{COLLISION}.1.release.json."),
    ]),
    od([
        ("at", "2026-09-16T11:22:00Z"),
        ("task_id", PRODUCER_SNAPSHOT),
        ("from_state", "queued"),
        ("to_state", "queued"),
        ("reason",
         "NOT A STATE CHANGE, A RETARGET, and it repairs a defect the opening queue shipped with. "
         f"{PRODUCER_SNAPSHOT} owned both producers' artifacts, so the audit's three files could "
         "not be committed until the execution they exist to gate had already run -- the ruling "
         "would have cited an uncommitted working tree, and the reviewers would have read the audit "
         "out of the same commit as the run it preceded. Its source_task_ids are now "
         f"[{EXECUTE}] and the audit is archived by {AUDIT_SNAPSHOT}. Nothing was rewritten: three "
         "cards were added and one archive's source list narrowed, both visible here."),
    ]),
    od([
        ("at", "2026-09-16T12:05:00Z"),
        ("task_id", EXECUTE),
        ("from_state", "blocked"),
        ("to_state", "queued"),
        ("reason",
         "The ruling exists and is committed: " + RULING + " at 323f22645, archived by "
         + RULING_ARCHIVE + ". The card's blocked_reason asked for a committed Coordinator ruling on "
         "the audit's verdict and not merely for the audit to finish; it got one, which accepted "
         "`partial`, granted a bounded reuse permission, and added four binding clauses in "
         + AMENDMENT + "."),
    ]),
    od([
        ("at", "2026-09-16T11:24:00Z"),
        ("task_id", AUDIT_SNAPSHOT + ", " + RULE + ", " + RULING_ARCHIVE),
        ("from_state", "absent"),
        ("to_state", "queued"),
        ("reason",
         "Three cards added after the audit returned, taking the batch from eight to eleven. Why "
         "they were not there at opening: the opening queue treated the Coordinator ruling as an "
         "act that would simply happen between two cards, which is precisely the shape of an "
         "approval that leaves no trace. The ruling now has a card, a write scope, a completion "
         "gate and a ledger commit, and the execution card's blocked_reason -- which already said "
         "it was gated on a ruling rather than on the audit finishing -- is now mechanically true "
         "rather than aspirational."),
    ]),
]

for _task in tasks:
    _applied = EXECUTED.get(_task["id"])
    if not _applied:
        continue
    _binding = _applied.get("archive_binding")
    if _binding is not None:
        for _field, _value in _binding.items():
            _task["archive"][_field] = _value
    for _field, _value in _applied.items():
        if _field == "archive_binding":
            continue
        _task[_field] = _value


# ---------------------------------------------------------------------------
queue = od([
    ("schema", "crypto.autoresearch.dispatch_queue.v1"),
    ("goal_id", GOAL),
    ("batch_id", BATCH),
    ("objective",
     "Get the first RUN OR READ EVIDENCE onto GOAL-SEMBIN-fcb7a2, which is the only kind of "
     "evidence any of its four completion criteria accepts. Three of the four are unmet and cannot "
     "be met without run records that do not exist (CORR-20260916-402547); the fourth was met by a "
     "read. EXP-SEMBIN-4fa22c is approved and has never been dispatched, and its own "
     "proof_search_map carries an audit marked REQUIRED BEFORE THE FIRST RUN and not yet performed. "
     "So this batch is that audit and then that run, in series, with the second gated on a "
     "Coordinator ruling about the first rather than on its mere completion."),
    ("max_concurrent", 2),
    ("max_concurrent_basis",
     "Machine headroom, not a research budget. 4 CPUs and ~15 GB RAM, and the executing task is a "
     "degree-by-degree GF(2) rank computation with a 10 GB resident-set watchdog. "
     "RAISED 1 -> 2 AT 2026-09-16T12:05Z, and the constraint the original 1 was protecting is "
     "UNCHANGED: at most ONE COMPUTE PRODUCER runs at a time. What the original number conflated "
     "was compute contention with queue slots. The card that needed the second slot "
     "(TASK-20260916-1bb446) carries maximum_runs 0 and memory_gb 1 and writes one YAML file, so it "
     "consumes no headroom and cannot contend with a rank computation -- while blocking it would "
     "have cost the campaign a pre-measurement prior, whose value expires the moment the "
     "measurement lands. A LATER READER MUST NOT USE THIS 2 TO DISPATCH TWO ALGEBRA RUNS: the "
     "reviewers are compute-capable and if two of them ever become Ready together, the cap comes "
     "back to 1. BATCH-51e2aa in the ICPERF campaign recorded a Macaulay2 phase driving the load "
     "average to 4.55 and had to split a review joint out to keep a timing clean, which is the cost "
     "this basis exists to avoid."),
    ("notes", [
        od([
            ("at", "2026-09-16T09:30:00Z"),
            ("kind", "batch_record"),
            ("text",
             "This queue IS the batch record; there is no batch.yaml, matching both batches of the "
             f"ICPERF campaign. The opening decision is {DECISION} and the human-readable account "
             "is opening-report.md beside this file."),
        ]),
        od([
            ("at", "2026-09-16T09:30:00Z"),
            ("kind", "why_the_audit_is_a_task_and_not_a_checkbox"),
            ("text",
             "One regex over knowledge/, ledger/ and experiments/ found first-fall-degree machinery "
             "in at least six other places, including a `driver/reused/macaulay.py` in "
             "EXP-ECTD-9e4248 and an `ic_first_fall_fast.py` in EXP-SIG-007. If either is a "
             "validated Macaulay-rank instrument, an executor writing a third one from scratch is "
             "waste, and if any of them already measured this quantity on a comparable object the "
             "planned run is a replication that should be framed as one. Both of those are cheaper "
             "to learn before the compute than after, which is the entire point of section 8's "
             "observation-collision audit."),
        ]),
        od([
            ("at", "2026-09-16T09:30:00Z"),
            ("kind", "what_this_batch_cannot_reach"),
            ("text",
             "Nothing here can refute Proposition 5, and the contract's S-1 makes that a success "
             "criterion rather than a caveat so that no run discovers it after the compute is "
             "spent. The reachable target is the PROPOSITION'S JUSTIFICATION at specific instances "
             "(DC-1, DEC-20260916-88ac73). A result presented as contradicting Proposition 5 would "
             "need `review-breakthrough` at max, which is undegradable and CANNOT BE SERVED in this "
             "environment -- so such a claim would stay un-promoted while the campaign stays "
             "active. That is a limit on the claim, never on the campaign."),
        ]),
        od([
            ("at", "2026-09-16T09:30:00Z"),
            ("kind", "concurrency"),
            ("text",
             "GOAL-SEMBIN-fcb7a2 has had no lane file until this batch. Another session may open "
             "one at any time without this one being told, which is the ordinary condition here: "
             "check `tools/goal_lanes.py lanes GOAL-SEMBIN-fcb7a2` after a fetch rather than "
             "assuming. Every task here writes inside its own directory and the goal head is "
             "edited additively inside this batch's archive, so a second lane collides with "
             "nothing but the head (docs/concurrent-goal-lanes.md)."),
        ]),
        od([
            ("at", "2026-09-16T09:30:00Z"),
            ("kind", "inference_declared_up_front"),
            ("text",
             "Every card here sets fallback_allowed TRUE with a stated reason, rather than "
             "inheriting `false` from AGENTS.md's template and being amended after the work runs. "
             "That template default is right for the contract and wrong for this machine, which "
             "holds no API credentials at all; BATCH-a33cda needed three separate amendments to "
             "learn it (DEC-20260916-7b2235, DEC-20260916-bec4b8). "
             "tools/research_dispatch.py `inference_advisories` reports the mismatch at render "
             "time; this queue is written so it has nothing to say."),
        ]),
        od([
            ("at", "2026-09-16T11:05:00Z"),
            ("kind", "review_round_restructured_before_any_reviewer_ran"),
            ("text",
             "Three defects in the reviewer and ledger cards, found by review of the queue as "
             "committed at d38386a31 and repaired before either producer had returned, let alone "
             f"a reviewer. (1) {REVIEW_BLIND} was told to write PREREGISTERED-VALUES.json but did "
             "not declare it in artifact_paths, so the ledger archive could not have hash-bound "
             "the one file that fixes the order of the blind derivation -- ICPERF's AP-AMD-1 hole "
             f"exactly. (2) {REVIEW_BLIND} owned J3/J4, which cannot be checked without opening "
             "experiments/EXP-SEMBIN-4fa22c/runs/, AND the blind re-derivation whose blind_from "
             "includes runs/; tools/check_review_independence.py flags any attested read under "
             "blind_from with no after-registration exception, so that card's own completion gate "
             f"could not be met honestly. J3 and J4 move to {REVIEW_INSTRUMENT} by "
             f"{REVIEW_ADDENDUM}; {REVIEW_BLIND} keeps only the blind re-derivation with a read "
             "scope disjoint from blind_from, and the instance description it needs is extracted "
             f"by the Coordinator to {BLIND_INSTANCE} before dispatch. (3) {LEDGER} listed the "
             "batch checkpoint as a deliverable but not in artifact_paths, so binding it at close "
             "would have failed the commit-scope check; the close is now a declared new shard, "
             f"{CLOSING_CHECKPOINT}, since the opening shard is write-once. The review plan itself "
             "is not edited: its blind_rederivation owner, blind_from and pre-registration path "
             "were already right, and the joint reassignment is the addendum's to make."),
        ]),
    ]),
    ("tasks_state_revisions", REVISIONS),
    ("tasks", tasks),
])

path = pathlib.Path(BASE) / "dispatch_queue.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(queue, indent=1) + "\n")
print(f"wrote {path} with {len(tasks)} tasks")
