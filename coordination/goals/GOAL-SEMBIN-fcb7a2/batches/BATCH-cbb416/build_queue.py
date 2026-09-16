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
EXECUTE = "TASK-20260916-0c2802"
PRODUCER_SNAPSHOT = "TASK-20260916-8eb394"
REVIEW_INSTRUMENT = "TASK-20260916-90af14"
REVIEW_CONTROLS = "TASK-20260916-7be96a"
LEDGER = "TASK-20260916-6a2fcf"

DECISION = "DEC-20260916-59921c"
ROUND = "REVIEW-SEMBIN-20260916-cbb416"
EVIDENCE = "EV-SEMBIN-29c44f"
CLOSING = "DEC-20260916-a0af84"


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
    ("priority", 88),
    ("review_required", True),
    ("depends_on", [COLLISION]),
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
    ]),
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
     "Snapshot-archive BATCH-cbb416's producers -- the collision audit and whatever the execution "
     "produced -- before any independent review reads them"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 70),
    ("review_required", False),
    ("depends_on", [COLLISION, EXECUTE]),
    ("read_scope", [BASE, EXP, "ledger"]),
    ("write_scope", [f"{BASE}/archives/{PRODUCER_SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{PRODUCER_SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [COLLISION, EXECUTE]),
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
        ("inputs", collision_artifacts + [f"{EXP}/code/", f"{EXP}/runs/"]),
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
def reviewer(task_id, title, joints, objective, questions, extra_constraints=()):
    """One reviewer card. Two of these split REVIEW-SEMBIN-20260916-cbb416's five joints.

    Split by WHAT THEY ATTACK rather than by convenience: one owns the object and the
    instrument (is this the system the contract names, does the code compute d'_F),
    the other owns the controls and the blind re-derivation (do the nulls
    discriminate, is an absence being written up as a fact). A reviewer told only to
    "review this" converges on whatever is most legible, so their agreement would
    measure shared taste rather than coverage.
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
        ("read_scope", [
            f"{EXP}/",
            f"{REVIEW}/review-plan.yaml",
            AUDIT,
            "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
            "ledger/decisions/DEC-20260916-88ac73.yaml",
            "ledger/corrections/CORR-20260916-96f47d.yaml",
            "coordination/review/sembin-20260916-propquant",
            "inputs/NAGAO-2015-984",
            "templates/research-records.md",
        ]),
        ("write_scope", [f"{REVIEW}/{task_id}/"]),
        ("artifact_paths", [
            f"{REVIEW}/{task_id}/report.md",
            f"{REVIEW}/{task_id}/attestation.yaml",
        ]),
        ("review_plan_ref", f"{REVIEW}/review-plan.yaml"),
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
                f"{EXP}/specification.yaml -- the frozen contract. Binding.",
                f"{AUDIT}/verdict.json -- the pre-compute collision audit.",
            ]),
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
                "`did_not_read` list, what you re-derived, what you took on trust, what you could "
                "not verify and what it would cost to, and your inference provenance",
            ]),
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
            ]),
            ("dispatch_preconditions", [
                f"{PRODUCER_SNAPSHOT} has a verified snapshot receipt, so you read committed "
                "producer artifacts rather than a working tree",
            ]),
        ])),
    ])


tasks.append(reviewer(
    REVIEW_INSTRUMENT,
    "Review J1, J2 and J5 of REVIEW-SEMBIN-20260916-cbb416: is the measured object the coset-shifted "
    "EQS4 descent the contract names, does the code compute d'_F rather than something near it, and "
    "does the run state its own blindness to the true degree",
    ["J1", "J2", "J5"],
    "Attack the object and the instrument. Establish independently whether the systems measured are "
    "the ones EXP-SEMBIN-4fa22c specifies, whether the integer it reports is the quantity the "
    "contract defines, and whether the report states in words that it cannot refute Proposition 5.",
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
    ],
    extra_constraints=(
        "The proves-too-much control is YOURS (review plan, proves_too_much): run the argument "
        "against a system with a PLANTED fall at degree 3, where its conclusion is known false. The "
        "instrument must find that fall at 3. And against a Koszul-only system, where it must find "
        "no non-trivial fall at all.",
    ),
))

tasks.append(reviewer(
    REVIEW_CONTROLS,
    "Review J3 and J4 of REVIEW-SEMBIN-20260916-cbb416 and perform the blind re-derivation: do the "
    "null objects actually discriminate, is any absence being written up as a fact, and does an "
    "independent computation of d'_F agree",
    ["J3", "J4"],
    "Attack the controls and the accounting, and independently derive d'_F and M-2 at the smallest "
    "completed instance. Establish whether a reported separation is a fact about the summation "
    "polynomial or about the shape of a degree-3 Boolean system, and whether every censored arm, "
    "watchdog kill and wall figure is reported as what it is.",
    [
        "Are the ten draws per null arm ten DISTINCT seeded draws? Regenerate two from their "
        "recorded seeds -- do they reproduce?",
        "Does A-NULL-SHUFFLED preserve the exact global monomial multiset of A-SHIFTED? Count it; do "
        "not trust the label.",
        "Did the run stay within maximum_runs 4? A fifth pass over the n-series is the shape of "
        "re-rolling nulls until they cooperate and would void C-2 entirely.",
        "S-6: are the nulls reported BEFORE any target value is interpreted, or is the headline "
        "first and the control a later section? The Coordinator expects the ordering to be where "
        "this breaks.",
        "For every arm with no fall found: does the record say `> d_max_reached` rather than 'no "
        "fall', and does NO downstream sentence treat it as a measured value (SR-1)?",
        "Is every watchdog kill or infrastructure failure recorded as `failed_infrastructure` and "
        "cited nowhere as evidence about Nagao (SR-5)?",
        "Read the recorded poll interval. Does any reported wall RATIO involve two measurements that "
        "both finish inside it (CORR-20260916-33068f measured a 51x inflation from exactly this)?",
        "C-5: is the series shown, or is monotonicity asserted? A non-monotone series is an "
        "INSTRUMENT signal first (F-4) -- was it rationalised as a fact about the systems?",
    ],
    extra_constraints=(
        "THE BLIND RE-DERIVATION IS YOURS, AND ITS PROCEDURE IS MANDATORY AND ORDERED. Before you "
        "open ANY file under experiments/EXP-SEMBIN-4fa22c/code/, experiments/EXP-SEMBIN-4fa22c/"
        "runs/, this batch's archives, or your sibling's directory, derive d'_F and M-2 at the "
        "smallest completed instance from the contract's definitions and the instance description "
        "alone, and write them with your method, exact command and input hash to "
        "PREREGISTERED-VALUES.json in your write scope. WRITE-ONCE: no edits, not even to fix a "
        "typo -- append a second file. Only then read the rest. This ordering is what makes your "
        "number evidence regardless of what you encounter afterwards, and it is required because "
        "the last blind assignment in this repository was leaked by the very document written to "
        "protect it (CORR-20260916-292e53).",
        "Disclose any exposure you encounter, with WHEN, measured against your pre-registration. "
        "Exposure after it costs the joint nothing; exposure before it means your number is "
        "reported as informed rather than independent. Disclosing is the behaviour that preserves "
        "the joint's value -- it is not a failure.",
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
    ("depends_on", [REVIEW_INSTRUMENT, REVIEW_CONTROLS]),
    ("read_scope", [BASE, REVIEW, EXP, "ledger"]),
    ("write_scope", [
        f"{BASE}/archives/{LEDGER}",
        f"ledger/evidence/{EVIDENCE}.yaml",
        f"ledger/decisions/{CLOSING}.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        f"{EXP}/specification.yaml",
        f"ledger/goals/{GOAL}/checkpoints/",
    ]),
    ("artifact_paths", [
        f"{BASE}/archives/{LEDGER}/ledger-receipt.json",
        f"ledger/evidence/{EVIDENCE}.yaml",
        f"ledger/decisions/{CLOSING}.yaml",
    ]),
    ("archive", od([
        ("kind", "ledger"),
        ("source_task_ids", [REVIEW_INSTRUMENT, REVIEW_CONTROLS]),
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
            f"{REVIEW}/{REVIEW_INSTRUMENT}/", f"{REVIEW}/{REVIEW_CONTROLS}/",
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
            f"the {BATCH} goal checkpoint",
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
    ("max_concurrent", 1),
    ("max_concurrent_basis",
     "Machine headroom, not a research budget. 4 CPUs and ~15 GB RAM, and the executing task is a "
     "degree-by-degree GF(2) rank computation with a 10 GB resident-set watchdog. The two producers "
     "are in series by dependency anyway, so 1 costs this batch nothing and protects the "
     "measurement: BATCH-51e2aa in the ICPERF campaign recorded a Macaulay2 phase driving the load "
     "average to 4.55 and had to split a review joint out to keep a timing clean."),
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
    ]),
    ("tasks_state_revisions", []),
    ("tasks", tasks),
])

path = pathlib.Path(BASE) / "dispatch_queue.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(queue, indent=1) + "\n")
print(f"wrote {path} with {len(tasks)} tasks")
