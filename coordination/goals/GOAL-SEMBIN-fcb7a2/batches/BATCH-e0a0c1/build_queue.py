#!/usr/bin/env python3
"""Author BATCH-e0a0c1's dispatch queue -- the SECOND, ZERO-COMPUTE lane on
GOAL-SEMBIN-fcb7a2, opened while BATCH-cbb416 holds the machine.

WHY THIS LANE EXISTS AND WHY IT IS SEPARATE. The goal head ranks a zero-compute
read of Nagao 2013/549 and Semaev 2015/310 as item (2), and says in terms that it
"needs no compute and competes with the batch for nothing, so it may run
concurrently in a separate lane rather than waiting behind it". BATCH-cbb416 has
max_concurrent 1 because its executing task is a degree-by-degree GF(2) rank
computation with a 10 GB watchdog; two readers of frozen PDF text cost that
nothing. Putting them in cbb416 would have forced them behind its executor for
no reason, and raising that batch's concurrency to let them in would have put
readers in the same slot pool as the measurement.

WHAT IS AT STAKE, since a "read two papers" batch can look like make-work. The
instrument EXP-SEMBIN-4fa22c builds measures the FAKE first fall degree d'_F.
Every inference from it to anything of Nagao's runs through 2015/984's Lemma 4,
d_F <= d'_F, which that paper ASSERTS WITHOUT PROOF and derives from its Lemma 3,
which it attributes to [11] = 2013/549 and declines to prove ("Proof of this
Lemma is complicated and not constructive"). The program has already verified by
exhaustive search over F_2 that the LITERAL form of Lemma 4, field equations
outside, is FALSE. So the campaign's central inference rests on a lemma whose
only proof sits in a paper nobody in this program had opened before 2026-09-13,
in a form nobody has checked against the statement that consumes it. This lane
reads it. The answer cannot change DC-1 and cannot refute Proposition 5; it
changes how conditional a confirmation would be, which the contract records as a
dependency rather than a footnote.

One-shot authoring script. It writes the queue and does not read it, so
re-running it after the batch moves would overwrite recorded state -- unless the
state is declared in EXECUTED/REVISIONS below, which is exactly why that table
exists (BATCH-cbb416's lesson, carried forward).
"""

import collections
import json
import pathlib

BATCH = "BATCH-e0a0c1"
GOAL = "GOAL-SEMBIN-fcb7a2"
BASE = f"coordination/goals/{GOAL}/batches/{BATCH}"
REVIEW = "coordination/review/sembin-20260916-e0a0c1"
NAGAO_DIR = f"{BASE}/read-nagao-2013-549"
SEMAEV_DIR = f"{BASE}/read-semaev-2015-310"
RULING_DIR = f"{BASE}/ruling"

OPEN = "TASK-20260916-7ecd0f"
OPEN_SNAPSHOT = "TASK-20260916-b88c5a"
READ_NAGAO = "TASK-20260916-9da6e0"
READ_SEMAEV = "TASK-20260916-64a93b"
READS_SNAPSHOT = "TASK-20260916-92128f"
RULING = "TASK-20260916-a8e5b5"
LEDGER = "TASK-20260916-d4fb62"

DECISION = "DEC-20260916-441cd5"
CLOSING = "DEC-20260916-87fc5c"
ROUND = "REVIEW-SEMBIN-20260916-e0a0c1"
EVIDENCE = "EV-SEMBIN-1ca3c8"

NAGAO_TEXT = "inputs/NAGAO-2013-549/paper_fulltext.md"
NAGAO_PDF = "inputs/NAGAO-2013-549/eprint-2013-549.pdf"
SEMAEV_TEXT = "inputs/SEMAEV-2015-310/paper_fulltext.md"
SEMAEV_PDF = "inputs/SEMAEV-2015-310/eprint-2015-310.pdf"
CONSUMER = "inputs/NAGAO-2015-984/paper_fulltext.md"


def od(pairs):
    return collections.OrderedDict(pairs)


open_artifacts = [
    f"ledger/decisions/{DECISION}.yaml",
    f"ledger/goals/{GOAL}/goal.yaml",
    f"ledger/goals/{GOAL}/checkpoints/{BATCH}.yaml",
    f"{BASE}/dispatch_queue.json",
    f"{BASE}/build_queue.py",
    f"{BASE}/opening-report.md",
    f"{REVIEW}/read-plan.yaml",
]

# goal.yaml is declared here AND by TASK-20260916-141f76 in BATCH-cbb416's queue.
# That is not double ownership: ownership is checked within a queue, and each
# lane binds the head's bytes AT ITS OWN COMMIT under content_at_commit, so two
# lanes' bindings of a file both of them append to cannot contradict each other.
# Before CORR-20260915-654160 this was impossible and the earlier of two lanes
# had to disown the file.
GOAL_HEAD_SHARED_NOTE = (
    f"ledger/goals/{GOAL}/goal.yaml is declared by BOTH open lanes on this goal and is the only "
    "file they share. This lane APPENDS an open_batches entry, one next_action prefix paragraph "
    "and one amendment_history entry, and rewrites nothing: BATCH-cbb416 keeps current_batch_id, "
    "dispatch_queue_path and its own entry untouched. Each lane binds the head at its own commit "
    "under content_at_commit, which is what makes concurrent appends verifiable "
    "(docs/concurrent-goal-lanes.md, CORR-20260915-654160)."
)

# WIDENED after CORR-20260921-942a62. Both cards originally declared three files
# apiece and both readers filed far more -- seventeen and twelve -- because a
# reader that checks its own claim writes a recheck, and a reader that distrusts a
# frozen extraction re-extracts the PDF. All of it was lost with the machine,
# INCLUDING the recheck that carried the counterexample to Lemma 4's inside form,
# which was the single most valuable thing either read produced.
#
# tools/producer_landing.py commits the DECLARED set and nothing else, on purpose.
# So an undeclared artifact is an unlanded artifact, and the declaration has to
# anticipate what a reader legitimately produces rather than record the minimum.
# These names are therefore REQUIRED OUTPUT PATHS in the cards below, not a guess
# at what might appear: a reader that has nothing to put in recheck.py writes the
# file saying so, which is a cheaper convention than a per-file negotiation.
#
# `--check` still sweeps each write_scope for anything undeclared, so a reader
# that files beyond even this set is visible before the turn ends.
nagao_artifacts = [
    f"{NAGAO_DIR}/report.md",
    f"{NAGAO_DIR}/statement-map.json",
    f"{NAGAO_DIR}/attestation.yaml",
    f"{NAGAO_DIR}/recheck.py",
    f"{NAGAO_DIR}/recheck.out",
    f"{NAGAO_DIR}/reextract.md",
]

semaev_artifacts = [
    f"{SEMAEV_DIR}/report.md",
    f"{SEMAEV_DIR}/statement-map.json",
    f"{SEMAEV_DIR}/attestation.yaml",
    f"{SEMAEV_DIR}/recheck.py",
    f"{SEMAEV_DIR}/recheck.out",
    f"{SEMAEV_DIR}/reextract.md",
]

# The ruling task DRAFTS; the ledger archive WRITES THE OFFICIAL DECISION and
# commits it. That split is not a style choice: research_dispatch.py requires a
# ledger archive to own an exact artifact under ledger/decisions/
# (`_validate_ledger_archive`), because a decision that is authored by one task
# and committed by another has a window in which it exists and is not official.
# Same shape as BATCH-cbb416's TASK-20260916-6a2fcf.
ruling_artifacts = [
    f"{RULING_DIR}/composition.md",
    f"{RULING_DIR}/scored-priors.json",
]

ledger_artifacts = [
    f"{BASE}/archives/{LEDGER}/ledger-receipt.json",
    f"ledger/decisions/{CLOSING}.yaml",
]

# The blind_from list every reader in this round is held to. It names the
# Coordinator's own documents, because those are where the expected answers are.
BLIND_FROM = [
    f"{REVIEW}/read-plan.yaml",
    f"ledger/decisions/{DECISION}.yaml",
    f"{BASE}/opening-report.md",
    f"ledger/goals/{GOAL}/checkpoints/{BATCH}.yaml",
    "the sibling reader's task directory in this batch",
]

READER_INFERENCE = od([
    ("policy", "review-adversarial"),
    ("reasoning_effort", None),
    ("fallback_allowed", True),
    ("fallback_note",
     "TRUE and declared up front. No adapter backend is credentialed in this checkout, so the "
     "runtime-native binding permitted by core rule 16 is the only route; `false` would be a claim "
     "every dispatch here breaks (DEC-20260916-7b2235, DEC-20260916-bec4b8)."),
    ("degraded_allowed", False),
    ("degraded_requirements_expected", [
        "model_verified false: `doctor --probe` has no usable backend here, so the resolved "
        "identifier is self-reported and is unverified configuration.",
    ]),
    ("independent_session_required", True),
    ("independent_session_note",
     "review-adversarial requires it, and this round needs it for a second reason: the value of a "
     "read that overturns the Coordinator comes entirely from the reader not having been told what "
     "the Coordinator expects. CORR-20260916-96f47d is this campaign's precedent -- that read "
     "overturned the Coordinator's reading of Proposition 5 and the campaign's objective changed."),
])

tasks = []

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", OPEN),
    ("title",
     "Open BATCH-e0a0c1: the zero-compute source read the goal head ranks second, as its own lane "
     "rather than behind BATCH-cbb416's executor"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 96),
    ("review_required", False),
    ("depends_on", []),
    ("read_scope", ["ledger", "inputs", "coordination/goals/" + GOAL, "experiments"]),
    ("write_scope", [BASE, REVIEW, f"ledger/decisions/{DECISION}.yaml",
                     f"ledger/goals/{GOAL}/checkpoints/{BATCH}.yaml",
                     f"ledger/goals/{GOAL}/goal.yaml"]),
    ("artifact_paths", open_artifacts),
    ("artifact_paths_note", GOAL_HEAD_SHARED_NOTE),
    ("handoff", od([
        ("objective",
         "Open a second, disjoint lane on GOAL-SEMBIN-fcb7a2 for ranked item (2), with the "
         "Coordinator's prior on all five joints recorded BEFORE either reader is dispatched."),
        ("uncertainty_reduced",
         "none; this is a ranking and control-plane act. It reads two papers only far enough to "
         "form a falsifiable prior, and asserts nothing about either."),
        ("inputs", [
            f"ledger/goals/{GOAL}/goal.yaml (next_action item (2), and its note that this item may "
            "run concurrently in a separate lane)",
            "experiments/EXP-SEMBIN-4fa22c/specification.yaml (records Lemma 4 as a dependency)",
            "ledger/corrections/CORR-20260916-96f47d.yaml (the precedent: a blind read of this "
            "paper family overturned the Coordinator)",
            "ledger/corrections/CORR-20260916-292e53.yaml (the precedent for how a protective "
            "document leaks what it protects)",
            NAGAO_TEXT,
            CONSUMER,
        ]),
        ("constraints", [
            "Zero runs, zero measurements.",
            "Record the prior BEFORE dispatching either reader, including the predictions the "
            "Coordinator's own checking already refuted. A prior listing only surviving beliefs "
            "overstates the Coordinator's calibration.",
            "Edit the goal head ADDITIVELY and inside this lane's archive only. BATCH-cbb416 is "
            "open on the same goal and its checkpoint owns the operative next_action.",
            "Never edit the frozen inputs, their sha256 sidecars, EXP-SEMBIN-4fa22c or "
            "H-SEMBIN-a7e721.",
        ]),
        ("deliverables", [DECISION, f"{BATCH} checkpoint", "dispatch_queue.json",
                          "opening-report.md",
                          f"{ROUND} read plan with the prior, written before any reader runs"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note",
             "TRUE and declared up front rather than amended after the work runs, for the reason "
             "recorded on every card in BATCH-cbb416."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 3600),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "the opening decision is committed",
            "the read plan records a prior for every joint, and predates both readers",
            "the queue renders with all gates passing and no inference advisory",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", OPEN_SNAPSHOT),
    ("title", "Snapshot-archive BATCH-e0a0c1's control plane before either reader reads it"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 95),
    ("review_required", False),
    ("depends_on", [OPEN]),
    ("read_scope", [BASE, REVIEW, "ledger"]),
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
         "content_at_commit from the outset, as BATCH-cbb416 did. It is what lets this archive bind "
         "the QUEUE AND ITS GENERATOR at its own commit rather than disowning them, since both "
         "necessarily change after it (CORR-20260915-654160, and BATCH-a33cda's forward pointer "
         "which cbb416 discharged)."),
        ("receipt_note",
         "Both readers depend on this archive so that the read plan they are blind FROM is "
         "committed and immutable before they run. A blind_from list that could still be edited "
         "afterwards is not a declared blindness."),
    ])),
    ("handoff", od([
        ("objective", "Commit the control plane, including the prior, before any reader runs."),
        ("uncertainty_reduced", "none; durability before dispatch"),
        ("inputs", open_artifacts),
        ("constraints", [
            "stage only declared paths",
            "commit message names the task id and every record id",
            "runs alone",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As OPEN's card."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 1800),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "the read plan is committed and its bytes are hash-bound",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", READ_NAGAO),
    ("title",
     "BLIND READ, joints J-1/J-2/J-3: does Nagao 2013/549 actually contain and prove the lemma "
     "2015/984 cites as its Lemma 3, and does it support Lemma 4 in the INSIDE form the campaign "
     "depends on?"),
    ("role", "validator"),
    ("state", "queued"),
    ("priority", 90),
    ("review_required", False),
    ("review_required_note",
     "FALSE, and the reason is structural rather than an exemption. This card IS the independent "
     "review: role validator, review-adversarial, independent session, blind from the Coordinator's "
     "prior and from its sibling. Setting it true would demand a reviewer of the reviewer, which "
     "buys nothing here and would leave the round with no owner for its actual joints. What "
     "composes it is the Coordinator ruling at " + RULING + ", which is a separate card with its "
     "own ledger archive, and the sibling read is a second independent session on a disjoint "
     "joint. Same disposition, same reasoning, as the collision audit in BATCH-cbb416."),
    ("depends_on", [OPEN_SNAPSHOT]),
    ("read_scope", [
        NAGAO_TEXT, NAGAO_PDF, "inputs/NAGAO-2013-549",
        CONSUMER, "inputs/NAGAO-2015-984",
        "experiments/EXP-SEMBIN-4fa22c/specification.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "ledger/corrections/CORR-20260916-96f47d.yaml",
        "AGENTS.md", "agents/validator.md", "templates/research-records.md",
        "docs/inventor-protocol.md",
        NAGAO_DIR,
    ]),
    ("read_scope_note",
     "DELIBERATELY NARROW ON ONE SIDE AND WIDE ON THE OTHER. Both papers are fully in scope, "
     "including the PDFs and the extraction script -- the 2013/549 extraction is materially worse "
     "than the 2015/984 one and its own frozen note says to read the PDF alongside it, so a reader "
     "confined to the markdown would be confined to mangled formulas. What is OUT of scope is every "
     "document in which the Coordinator has written down what it expects: see blind_from."),
    ("write_scope", [NAGAO_DIR]),
    ("artifact_paths", nagao_artifacts),
    ("handoff", od([
        ("objective",
         "Establish what the upstream source actually says and proves, and whether it carries "
         "2015/984's Lemma 4 in the form EXP-SEMBIN-4fa22c depends on."),
        ("uncertainty_reduced",
         "How conditional a d'_F measurement's bearing on Nagao's d_F statements really is. The "
         "contract records Lemma 4 as a dependency; nobody has checked its provenance."),
        ("inputs", [
            f"{CONSUMER} -- Lemma 3 as quoted at :461-507, Lemma 4 at :510-515, Example 1 at "
            ":495-505, and the sentence declining to reproduce the proof at :507",
            f"{NAGAO_TEXT} plus {NAGAO_PDF}",
            "inputs/NAGAO-2013-549/extract_text.py -- re-runnable with different LAParams",
            "experiments/EXP-SEMBIN-4fa22c/specification.yaml -- what the campaign consumes",
        ]),
        ("constraints", [
            "ZERO RUNS AND ZERO MEASUREMENTS. maximum_runs is 0. This is a read.",
            "A small hand-check of an algebraic step, written into your own task directory and "
            "labelled a recheck rather than a measurement, is PERMITTED and encouraged -- the "
            "precedent is coordination/review/sembin-20260916-propquant/coordinator-recheck.py.",
            "MATCH STATEMENTS ON CONTENT, NEVER ON NUMBER. The upstream paper has its own Lemma 3 "
            "and it may not be the one 2015/984 means. Enumerate the numbered statements and match "
            "the CONTENT of the quoted lemma.",
            "The served 2013/549 PDF is the LAST OF TWO REVISIONS and its abstract note records "
            "that a lemma of the first version was FALSE and a section deleted. The first revision "
            "is NOT in inputs/ and is not fetchable here; say so where it matters instead of "
            "reasoning about a version you cannot see.",
            "Report an honest 'cannot determine, because the extraction destroys this formula and "
            "re-extraction also failed' rather than a confident reading of mangled text. The "
            "extraction is known bad in Sections 2-3.",
            "You may NOT read the files in blind_from. Attest to what you read.",
            "Do not rule on what the campaign should do. You report; the Coordinator rules.",
            "Cite with provenance (templates/research-records.md): a paper you OPENED is "
            "`retrieved`; one you recall is `recalled`, a pointer and never support.",
        ]),
        ("questions", [
            "J-1: Which numbered statement in 2013/549 is the one 2015/984 quotes as its Lemma 3? "
            "Give its number, its exact statement, every hypothesis it carries, and every "
            "definition it depends on. Is 2015/984's restatement faithful, weaker or stronger?",
            "J-2: Is that statement PROVED in 2013/549, and is the proof complete on its own "
            "terms? If it runs by induction, is the measure well-founded, is there a base case, "
            "does the inductive step preserve the degree bound, and does it use a hypothesis the "
            "statement does not carry?",
            "J-3: Does it support 2015/984's Lemma 4 (d_F <= d'_F) in the INSIDE form -- d'_F taken "
            "of {f_1..f_M} UNION S_fe, which is how Lemma 4 is written? Derive Lemma 4 from it "
            "step by step, or show where the derivation fails. Name every upstream hypothesis the "
            "derivation consumes, because the campaign must record those as its own dependencies.",
            "J-5 (PROVES-TOO-MUCH, REQUIRED): this program has verified by exhaustive "
            "two-polynomial search over F_2 that the OUTSIDE form of Lemma 4 -- field equations "
            "outside the fake system -- is FALSE. Run your J-3 derivation against that object. If "
            "it also goes through with S_fe outside, YOUR DERIVATION IS WRONG SOMEWHERE, and "
            "locating that is worth more than the derivation. Report the outcome either way.",
        ]),
        ("deliverables", [
            "report.md -- one section per joint, with the answer, the evidence by file and line, "
            "and what you could not determine and why. Include your inference provenance: "
            "requested_policy review-adversarial, the model identifier your session self-reports, "
            "fallback_used true with its reason, model_verified false.",
            "statement-map.json -- machine-readable: every numbered statement in 2013/549 with its "
            "line range and a one-line content summary; which one matches the quoted Lemma 3 and "
            "with what confidence; the hypotheses each carries; and a `could_not_determine` list.",
            "attestation.yaml -- what you read (exact paths), that you did not read blind_from, "
            "your verdict per joint, and the J-5 control's outcome.",
            "recheck.py + recheck.out -- an EXECUTABLE check of whatever claim in your "
            "report carries the most weight, and its captured output. If your finding is a "
            "counterexample, this is the file that makes it survive you: the last reader to "
            "run this card produced one and it was lost with the machine "
            "(CORR-20260921-942a62), and the Coordinator had to rebuild it from scratch. "
            "If nothing in your report is mechanically checkable, write both files saying "
            "so and why -- an empty required file is a cheaper convention than a "
            "negotiation.",
            "reextract.md -- if you re-extract the PDF because you distrust the frozen "
            "markdown, the result and what differed. READ inputs/NAGAO-2013-549/"
            "errata-extraction-20260921.md FIRST: that package orphans 63 of its 73 large "
            "operators, so Lemma 2's GRADED monomial-order hypothesis reads as a vacuous "
            "per-variable one in paper_fulltext.md, and paper_fulltext.pymupdf.txt beside "
            "it is intact. If the errata answers your extraction question, record that "
            "here instead of re-doing it.",
        ]),
        ("artifact_paths_note",
         "SIX files, all inside " + NAGAO_DIR + ". Create nothing outside it and check with "
         "`git status --porcelain` before reporting done. Every one of the six is REQUIRED: "
         "the Coordinator lands exactly the declared set on your return "
         "(tools/producer_landing.py), so a file you produce and do not declare is a file "
         "that is not committed, and an undeclared artifact is what was lost last time."),
        ("blindness", od([
            ("blind_from", BLIND_FROM),
            ("why",
             "The Coordinator has recorded, in the read plan, its expected answer to J-1 through "
             "J-4 -- including the exact upstream lemma number it believes is the match. A reader "
             "who reads that file is confirming rather than checking. The declared limit of this "
             "blind is stated in the plan and repeated here: the J-1 answer is a lemma number in a "
             "public paper, derivable in minutes by grep, so blindness buys real independence on "
             "J-2 and J-3 and much less on J-1."),
            ("sibling", READ_SEMAEV),
            ("sibling_rule",
             "Do not read the sibling's task directory. Your joints and its joints are disjoint by "
             "construction."),
        ])),
        ("inference", READER_INFERENCE),
        ("budget", od([
            ("wall_clock_seconds", 7200),
            ("memory_gb", 2),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "all SIX declared artifacts exist under the write scope -- the Coordinator lands "
            "exactly the declared set, so an undeclared file is an uncommitted file",
            "J-1, J-2, J-3 and the J-5 control each have an answer or an explicit "
            "'cannot determine, because ...'",
            "the attestation names every path read and asserts blind_from was respected",
            "git status --porcelain shows nothing outside the write scope",
            "no measurement was performed",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", READ_SEMAEV),
    ("title",
     "BLIND READ, joint J-4: what does Semaev 2015/310's ARGUMENT deliver, as against what his "
     "STATEMENT claims?"),
    ("role", "validator"),
    ("state", "queued"),
    ("priority", 89),
    ("review_required", False),
    ("review_required_note", "As " + READ_NAGAO + "'s card: this IS the independent review."),
    ("depends_on", [OPEN_SNAPSHOT]),
    ("read_scope", [
        SEMAEV_TEXT, SEMAEV_PDF, "inputs/SEMAEV-2015-310",
        CONSUMER, "inputs/NAGAO-2015-984",
        "experiments/EXP-SEMBIN-4fa22c/specification.yaml",
        "ledger/hypotheses/H-SEMBIN-a7e721.yaml",
        "AGENTS.md", "agents/validator.md", "templates/research-records.md",
        "docs/inventor-protocol.md",
        SEMAEV_DIR,
    ]),
    ("write_scope", [SEMAEV_DIR]),
    ("artifact_paths", semaev_artifacts),
    ("handoff", od([
        ("objective",
         "Separate what Semaev's argument establishes from what his statement asserts, for the "
         "statement this campaign consumes."),
        ("uncertainty_reduced",
         "Whether the campaign's second recorded residual is a gap between statement and argument, "
         "and if so, of what shape: quantifier order, a heuristic step, or experiments offered in "
         "support of a general claim."),
        ("inputs", [
            f"{SEMAEV_TEXT} plus {SEMAEV_PDF} and inputs/SEMAEV-2015-310/tables.yaml",
            "inputs/SEMAEV-2015-310/source_record.yaml -- which statement the program recorded as "
            "the one it consumes",
            f"{CONSUMER} -- for how the neighbouring literature uses the same quantities",
        ]),
        ("constraints", [
            "ZERO RUNS AND ZERO MEASUREMENTS. maximum_runs is 0.",
            "A small labelled hand-check in your own task directory is permitted.",
            "IDENTIFY THE CONSUMED STATEMENT FIRST, and say how you identified it. If the "
            "program's own records are ambiguous about which statement it depends on, that "
            "ambiguity is itself a finding worth reporting -- do not resolve it by choosing.",
            "Attend to QUANTIFIER ORDER specifically: 'for all instances there is a bound' and "
            "'for a typical instance there is a bound' are different claims and the difference is "
            "what this joint exists to find. The same distinction is what the last read of this "
            "paper family turned on (CORR-20260916-96f47d).",
            "Distinguish what is PROVED, what is argued heuristically, and what is supported only "
            "by the paper's own experiments. Report the strongest claim the argument supports.",
            "You may NOT read the files in blind_from, or your sibling's task directory.",
            "Do not rule on what the campaign should do.",
            "Cite with provenance.",
        ]),
        ("questions", [
            "J-4a: Which statement of 2015/310 does this program consume, and how did you "
            "determine that?",
            "J-4b: What does the argument for it actually establish? Quantifier order, hypotheses, "
            "and any step asserted rather than proved.",
            "J-4c: Is there a gap between statement and argument? If so, name it precisely and say "
            "which side a consumer must rely on.",
            "J-5 (PROVES-TOO-MUCH, REQUIRED): apply the argument to a parameter regime or object "
            "where its conclusion is known or strongly believed FALSE, and report whether it still "
            "runs. An argument that survives its own known-false object has an error nobody has "
            "located yet. If you cannot construct such an object, say so and say why.",
        ]),
        ("deliverables", [
            "report.md -- one section per sub-joint plus the control, evidence by file and line, "
            "what you could not determine, and your inference provenance.",
            "statement-map.json -- the numbered statements you examined with line ranges, which is "
            "the consumed one, what is proved versus argued versus experimental, and a "
            "`could_not_determine` list.",
            "attestation.yaml -- paths read, blind_from respected, verdict per sub-joint, control "
            "outcome.",
            "recheck.py + recheck.out -- an EXECUTABLE check of whichever claim in your report "
            "carries the most weight, and its captured output. The last reader to run this card "
            "produced rechecks and they were lost with the machine (CORR-20260921-942a62); a "
            "finding that exists only as prose does not survive its session. If nothing in your "
            "report is mechanically checkable, write both files saying so and why.",
            "reextract.md -- if you re-extract the PDF because you distrust the frozen markdown, "
            "the result and what differed. inputs/NAGAO-2013-549/errata-extraction-20260921.md "
            "records a CONFIRMED case of this in the sibling package: 63 of 73 large operators "
            "detached from their operands, so a graded hypothesis reads as a vacuous one. "
            "SEMAEV-2015-310 was audited and shows no operator detachment, but it does show "
            "line-splitting, so check any formula you rely on against the PDF and record the "
            "outcome here either way.",
        ]),
        ("blindness", od([
            ("blind_from", BLIND_FROM),
            ("why",
             "The Coordinator's prediction for this joint is recorded in the read plan at LOW "
             "confidence and is close to a guess about a genre of gap. That is exactly the kind of "
             "prior a reader would anchor on if shown it."),
            ("sibling", READ_NAGAO),
            ("sibling_rule", "Do not read the sibling's task directory."),
        ])),
        ("inference", READER_INFERENCE),
        ("budget", od([
            ("wall_clock_seconds", 7200),
            ("memory_gb", 2),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "all SIX declared artifacts exist under the write scope -- the Coordinator lands "
            "exactly the declared set, so an undeclared file is an uncommitted file",
            "every sub-joint and the J-5 control has an answer or an explicit "
            "'cannot determine, because ...'",
            "the attestation names every path read and asserts blind_from was respected",
            "git status --porcelain shows nothing outside the write scope",
            "no measurement was performed",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", READS_SNAPSHOT),
    ("title", "Snapshot-archive both reader packages before the Coordinator composes them"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 80),
    ("review_required", False),
    ("depends_on", [READ_NAGAO, READ_SEMAEV]),
    ("read_scope", [NAGAO_DIR, SEMAEV_DIR, BASE]),
    ("write_scope", [f"{BASE}/archives/{READS_SNAPSHOT}"]),
    ("artifact_paths", [f"{BASE}/archives/{READS_SNAPSHOT}/snapshot-receipt.json"]),
    ("archive", od([
        ("kind", "snapshot"),
        ("source_task_ids", [READ_NAGAO, READ_SEMAEV]),
        ("record_ids", [ROUND, BATCH]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_first"),
        ("binding_mode_note",
         "content_first HERE, unlike the opening archive, and the difference is the point. A "
         "reader's filed report is IMMUTABLE: it must read identically at HEAD forever, and if it "
         "does not, something edited a producer's artifact after filing. This campaign's sibling "
         "has had that happen TWICE (CORR-20260916-5166fe, CORR-20260916-2e9bc3), both times by a "
         "concurrent session fixing something in place. content_first is the mode that catches it; "
         "content_at_commit would not."),
        ("receipt_note",
         "Records both readers' attestations and whether either declares a blindness breach. A "
         "breach does not invalidate the read -- it changes what the read is evidence of, and the "
         "composition must say so."),
    ])),
    ("handoff", od([
        ("objective", "Fix both reports in an immutable commit before the Coordinator reads them "
                      "together."),
        ("uncertainty_reduced", "none; evidence integrity before composition"),
        ("inputs", nagao_artifacts + semaev_artifacts),
        ("constraints", [
            "NEVER edit a reader's filed artifact. If one is wrong, the correction is a new record "
            "under a new id in a Coordinator-owned path -- the disposition CORR-20260916-2e9bc3 "
            "records after the alternative was tried.",
            "stage only declared paths; runs alone",
            "commit message names the task id and every record id",
        ]),
        ("deliverables", ["snapshot-receipt.json"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As OPEN's card."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 1800),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "both attestations are committed unedited",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", RULING),
    ("title",
     "Compose " + ROUND + ": score every prior, name every joint's verdict, and rule on what the "
     "campaign's Lemma 4 dependency now costs"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 70),
    ("review_required", False),
    ("depends_on", [READS_SNAPSHOT]),
    ("read_scope", [NAGAO_DIR, SEMAEV_DIR, BASE, REVIEW, "ledger", "inputs", "experiments"]),
    ("write_scope", [RULING_DIR]),
    ("artifact_paths", ruling_artifacts),
    ("handoff", od([
        ("objective",
         "Turn two independent reads into one committed ruling about how conditional a d'_F "
         "measurement's bearing on Nagao's d_F statements is."),
        ("uncertainty_reduced",
         "Whether EXP-SEMBIN-4fa22c's recorded Lemma 4 dependency is supported upstream, and at "
         "what strength; and whether the Semaev residual is a statement-argument gap."),
        ("inputs", nagao_artifacts + semaev_artifacts + [f"{REVIEW}/read-plan.yaml"]),
        ("constraints", [
            "Zero runs.",
            "SCORE EVERY PREDICTION P-1..P-6 as confirmed, refuted or untested, and record a "
            "refuted prior at least as prominently as a confirmed one. P-4 is the one the "
            "Coordinator said it would rather lose.",
            "Name EVERY joint with its verdict. A joint no reader owned is reported as unowned, "
            "not quietly dropped.",
            "If either reader declares a blindness breach, record it in procedure_deviations and "
            "say what the read is then evidence of.",
            "Do NOT change H-SEMBIN-a7e721's status, EXP-SEMBIN-4fa22c's status, or any goal "
            "criterion on the strength of a read of external sources. Whether this round produces "
            f"{EVIDENCE} at all is this ruling's decision to make and to justify.",
            "If the reads bear on EXP-SEMBIN-4fa22c's dependency record, the change is an ADDITIVE "
            "amendment under a new id, never an edit to the frozen contract.",
            "The goal head edit is additive and stays inside this lane; BATCH-cbb416's checkpoint "
            "owns the operative next_action.",
        ]),
        ("deliverables", [
            "composition.md -- the ruling in full: every joint named with its verdict, every "
            f"prior scored, and the text that {LEDGER} commits as {CLOSING}",
            "scored-priors.json -- machine-readable P-1..P-6 with confirmed | refuted | untested "
            "and the evidence for each, so a later reader can measure this Coordinator's "
            "calibration without re-reading the prose",
        ]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As OPEN's card."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
            ("escalation_condition",
             "IF EITHER READER FINDS THE UPSTREAM LEMMA UNPROVED OR INSUFFICIENT FOR THE INSIDE "
             "FORM, the resulting claim -- that a published subexponential ECDLP bound rests on an "
             "unsupported lemma -- is a contradiction of established evidence in the sense of core "
             "rule 12 and requires review-breakthrough at max, which is UNDEGRADABLE and CANNOT BE "
             "SERVED in this environment. The ruling then records the finding at its narrowest "
             "supported scope and leaves the CLAIM un-promoted while the campaign stays active. "
             "That is a limit on the claim, never on the campaign, and never a reason to soften the "
             "finding so a servable tier will carry it."),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 5400),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "every prior P-1..P-6 is scored",
            "every joint J-1..J-5 is named with a verdict or an explicit 'unowned'",
            "tools/check_review_independence.py raises no problem against the round",
            "no status transition rests on a read of an external source alone",
        ]),
        ("runs_launched", 0),
    ])),
]))

# ---------------------------------------------------------------------------
tasks.append(od([
    ("id", LEDGER),
    ("title", "Ledger-archive the ruling and close this lane"),
    ("role", "coordinator"),
    ("state", "queued"),
    ("priority", 60),
    ("review_required", False),
    ("depends_on", [RULING]),
    ("read_scope", [RULING_DIR, BASE, REVIEW, "ledger"]),
    ("write_scope", [f"{BASE}/archives/{LEDGER}", f"ledger/decisions/{CLOSING}.yaml",
                     f"ledger/goals/{GOAL}/checkpoints/", f"ledger/goals/{GOAL}/goal.yaml"]),
    ("artifact_paths", ledger_artifacts),
    ("archive", od([
        ("kind", "ledger"),
        ("source_task_ids", [RULING]),
        ("record_ids", [CLOSING, BATCH, GOAL]),
        ("commit_sha", None),
        ("parent_sha", None),
        ("path_sha256", {}),
        ("binding_mode", "content_at_commit"),
        ("binding_mode_note",
         "content_at_commit: this archive stages the goal head, which every later checkpoint "
         "reranks. Binding it at HEAD would report this archive corrupt at the next rerank."),
    ])),
    ("handoff", od([
        ("objective",
         f"Write {CLOSING} from the composition and make it official in one isolated commit."),
        ("uncertainty_reduced", "none; durability"),
        ("inputs", ruling_artifacts + [f"{REVIEW}/read-plan.yaml"]),
        ("constraints", [
            "stage only declared paths; runs alone",
            "commit message names the task id and every record id",
            "fetch origin/main and MERGE it before committing; never rebase pushed records",
            "The decision's content is the composition's, not a fresh judgement: this card "
            "COMMITS a ruling that was already reasoned and reviewable, and a divergence between "
            f"{CLOSING} and composition.md is a defect rather than a refinement.",
            "The closing checkpoint shard is write-once and additive; the goal head edit is "
            "additive and must not touch BATCH-cbb416's fields.",
        ]),
        ("deliverables", ["ledger-receipt.json", f"{CLOSING}", f"{BATCH}.closing.yaml checkpoint",
                          "an additive goal-head rerank recording this lane's outcome"]),
        ("inference", od([
            ("policy", "coordinator-orchestration-code"),
            ("reasoning_effort", None),
            ("fallback_allowed", True),
            ("fallback_note", "As OPEN's card."),
            ("degraded_allowed", False),
            ("independent_session_required", False),
        ])),
        ("budget", od([
            ("wall_clock_seconds", 1800),
            ("memory_gb", 1),
            ("maximum_runs", 0),
        ])),
        ("completion_gate", [
            "post-commit receipt verified by research_dispatch.py",
            "validate_ledger.py adds no new error on the paths this commit stages",
        ]),
        ("runs_launched", 0),
    ])),
]))


# ---------------------------------------------------------------------------
# Post-execution facts, applied to the cards. See BATCH-cbb416's builder for why
# this table exists rather than hand edits to the generated JSON.
EXECUTED = {
    OPEN_SNAPSHOT: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16 at commit 84f25affa595e433b34fc8d774fbaf5dda5701a8. Staged exactly "
         "the seven declared source artifacts, its own receipt, and the lane side file; nothing "
         "else. The concurrently running collision audit of BATCH-cbb416 was writing into its own "
         "untracked directory at the time and was deliberately NOT staged -- a producer's artifacts "
         "are committed by the archive that owns them, and staging a running producer's partial "
         "output would bind bytes it has not finished writing."),
        ("archive_binding", od([
            ("commit_sha", "84f25affa595e433b34fc8d774fbaf5dda5701a8"),
            ("parent_sha", "de6c804682fe138a63e4c9cb4d2c224c4c42430d"),
            ("path_sha256", od([
                # The archive's own artifact first. A receipt cannot contain its
                # own hash, so this is the one value a reader takes from the
                # queue rather than from the receipt.
                (f"{BASE}/archives/{OPEN_SNAPSHOT}/snapshot-receipt.json",
                 "46cda209dcfa01756f7b76704318b2e3cf42a53fa0e8fee0938b384213afba86"),
            ] + list(zip(open_artifacts, [
                "f063851780a5423aacad539156397cc62710cb87774cb30d1735fd34e8c0e509",
                "b8e3fdbf22c22100f7afc9d28c7ed5c48341adf6adc10905a85bde09e74f5920",
                "8605c51728bb35f957fe12f50f43afe8fddaf9a94dbb6106c443da0d802e8776",
                "fe433b8e666729343d3e779728d9697036d902ca60f0d52b0fbdead20f17ea37",
                "5bc45d68e23b0421b919fba598b0b83d416089813bc7df77daa72c8fb19c8a90",
                "450207237b2462eb2b14a8da31d6c2ea11f54080aeb415bc22263f2926a27eeb",
                "3e3c6555e8078f647e1935b29f045b0a5ded596f57a97202c798500641181c62",
            ], strict=True)))),
            ("path_sha256_note",
             "EIGHT entries: the receipt plus the seven sources, INCLUDING THE GOAL HEAD, THIS "
             "QUEUE AND ITS GENERATOR. All three legitimately change after this commit -- the head "
             "at every rerank and whenever the other open lane appends, the queue and generator as "
             "this table records what has executed. Under content_at_commit that is verification "
             "working; under content_first each of those moves would report this archive corrupt "
             "(CORR-20260915-654160)."),
        ])),
    ]),
    OPEN: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-16. The prior was formed by the Coordinator opening both Nagao papers "
         "directly for about twenty minutes and is recorded at REVIEW-SEMBIN-20260916-e0a0c1 with "
         "six predictions, confidences, and falsification conditions -- including P-3, which the "
         "Coordinator's own checking REFUTED while forming it (the first reading was that "
         "2015/984 had dropped a locality hypothesis; the definition at NAGAO-2013-549 "
         "paper_fulltext.md :180 shows `local polynomial` names the ambient ring). Zero runs."),
    ]),
    READ_NAGAO: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21 at epoch 2, re-dispatched after the first attempt's package was "
         "destroyed uncommitted with the machine (CORR-20260921-942a62). Six declared artifacts "
         "filed and landed at c31504e97 the moment the reader returned. Zero runs, zero "
         "measurements. J-1 holds and the match is 2013/549's LEMMA 2, not its Lemma 3 -- "
         "matching on number would have found an unrelated statement about deg(wd(m)), which is "
         "exactly the failure the card's match-on-content constraint anticipated. J-2 holds: "
         "Lemma 2 is proved and its induction is well-founded under a graded order. J-3 BREAKS -- "
         "the derivation requires the field equations as MEMBERS of the true system, which Lemma 4 "
         "does not supply, and the reader filed a second counterexample (f_1 = X^2 Y, "
         "f_2 = XY + X over F_2[X,Y]: d'_F = 2, d_F = 3). The J-5 proves-too-much control PASSES. "
         "The reader additionally reports that this batch's INSIDE-versus-OUTSIDE distinction is "
         "INERT on the fake side, which if it stands means the campaign's recorded residual was "
         "drawn in the wrong place; the Coordinator reproduced both that claim and the "
         "counterexample in tools/lemma4_inside_form.py, which the reader never read, and pinned "
         "them in tools/test_lemma4_inside_form.py. Ruling at TASK-20260916-a8e5b5."),
        ("disclosed_independence_qualifications",
         "The reader's own attestation, not a Coordinator finding: the J-1 answer LEAKED from an "
         "in-scope, program-authored document -- inputs/NAGAO-2013-549/errata-extraction-20260921.md "
         "names Lemma 2, and the card directed the reader to read it first. The reader derived the "
         "match independently by enumerating statements and matching content, and recorded the leak "
         "rather than claiming a blindness it did not have. J-1 is therefore corroboration; the "
         "blind bought its real value on J-2 and J-3. It also read CORR-20260916-96f47d only after "
         "building its counterexample, and saw the sibling directory's file names via `ls` without "
         "opening any file in it. Both disclosed."),
    ]),
    READ_SEMAEV: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21 at epoch 2, re-dispatched for the same reason as its sibling. Six "
         "declared artifacts filed and landed at c0a107514. Zero runs, zero measurements. J-4a "
         "answered WITH A RECORDED AMBIGUITY the card told it not to resolve by choosing: the "
         "campaign consumes Semaev's 4.5 first-fall-degree result through Nagao's Propositions 2 "
         "and 5, and NO record of this campaign cites 2015/310 directly at all -- the statement "
         "exists only as unanchored prose in a `mechanism` field. J-4b: the argument proves the "
         "FAKE degree of the NON-TERMINAL links only, by a uniform witness, which the reader is "
         "careful to call a genuine strength of quantifier order rather than dress up. J-4c BREAKS "
         "in three separable components -- quantity, coverage (t-2 of t-1 equations, so one is "
         "uncovered at every t and the count is zero at t = 2, which Assumption 1's range "
         "includes), and quantifier. The J-5 proves-too-much control FAILS: the paper supplies its "
         "own known-false object at 4.5.1 and the argument runs there unchanged because k appears "
         "nowhere in it. Ruling at TASK-20260916-a8e5b5."),
    ]),
    READS_SNAPSHOT: od([
        ("state", "completed"),
        ("outcome",
         "Completed 2026-09-21 at commit 4b7edadfbd42489f1a120157c1d29558fa992cce. Staged exactly "
         "its own receipt and nothing else, because the twelve source artifacts were already "
         "committed by tools/producer_landing.py when each reader returned. That inverts the "
         "historical order deliberately and is the CORR-20260921-942a62 remedy: the gap between "
         "production and archival is what destroyed this round's first attempt. content_first "
         "verifies the declared hashes at HEAD rather than against a changed-path set, so the "
         "binding is unaffected by the inversion."),
        ("archive_binding", od([
            ("commit_sha", "4b7edadfbd42489f1a120157c1d29558fa992cce"),
            ("parent_sha", "d67aa9e61cb675f6dc67196b7a01bb17ac634e17"),
            ("path_sha256", od([
                # The receipt's own hash, which it cannot contain itself.
                (f"{BASE}/archives/{READS_SNAPSHOT}/snapshot-receipt.json",
                 "e8db5c325c32af4908a2121873aaa4720967f8a8564e30e884f9c06912182864"),
            ] + list(zip(nagao_artifacts, [
                "9a90c0a338ff8debedad4f89308f21d8668c7b9fb4a716733a5cff87ce6f5317",
                "3b5b93f7541011df6c6260bcd2b6c527c78177b030953587cd42db14e313b2cc",
                "d167a49b867b1c9c4272f9c952370bb892e6688deeca8606cc0c0d6557175921",
                "5398d1745bbc01c8a2db337c19ca585b9ca6571f64f80a025cceee653b6e55ee",
                "e8fa485a1bd917ed8f51f1dba0889be1a4a9096cc9422501a4655e403209204c",
                "56aa696d494ef6f66871879504a8c9370be7118d4f4ea0922f5f6002a8ce794d",
            ], strict=True)) + list(zip(semaev_artifacts, [
                "d6ac3d96ff8604a246550d002fb9976580d7f751275e20f0ea7b7c903ce534ac",
                "f78faf3849c6f1ebe56f89243a63c403856726937c63b81108e5fd8a9dfc771b",
                "3d1a92cf56ed986ddca02f3a9687c1b20b773801b6de4563fda1ef9e290e5707",
                "bfc84f94e164ad7ecf266549aa73208029a8272a65a11ecd082fee23cf085bba",
                "b83a413e042adee1a5f41d2aeb3d9ca63542822dd51c44d206d8c2458b02e116",
                "2e1443502d229e8b41f8691388d8711a5d975b64019f6ca33b82ac20673714ea",
            ], strict=True)))),
            ("path_sha256_note",
             "THIRTEEN entries: the receipt plus twelve reader artifacts, six per reader. Six and "
             "not three because the cards were widened after the first attempt produced six and "
             "lost the three it had not declared. Unlike the opening archive, nothing bound here "
             "is allowed to change: a filed report is immutable, which is why this archive binds "
             "content_first and that one binds content_at_commit."),
        ])),
    ]),
}

REVISIONS = [
    od([
        ("at", "2026-09-16T11:40:00Z"),
        ("task_id", OPEN),
        ("from_state", "queued"),
        ("to_state", "completed"),
        ("reason",
         "Recorded as a transition rather than written `completed` from the start, which is what "
         "BATCH-cbb416's opening card did and had to disclose afterwards: that card read "
         "`completed` while three of its declared artifacts did not exist. This one is marked "
         "completed only now, with all seven present and committed at 84f25affa."),
    ]),
    od([
        ("at", "2026-09-16T11:42:00Z"),
        ("task_id", OPEN_SNAPSHOT),
        ("from_state", "queued"),
        ("to_state", "completed"),
        ("reason",
         "Snapshot archive executed at 84f25affa under binding_mode content_at_commit, binding "
         "eight paths. Both readers are now unblocked and the read plan they are blind FROM is a "
         "fixed, hash-bound object."),
    ]),
    od([
        ("at", "2026-09-21T14:30:00Z"),
        ("task_id", f"{READ_NAGAO}, {READ_SEMAEV}"),
        ("from_state", "queued"),
        ("to_state", "queued"),
        ("what_changed",
         "artifact_paths widened from three files to six on each card, with the two new "
         "deliverables (recheck.py + recheck.out, reextract.md) stated as REQUIRED and the "
         "completion gate updated from 'all three' to 'all SIX'."),
        ("reason",
         "BOTH CARDS ALREADY RAN ONCE AND THEIR OUTPUT WAS LOST (CORR-20260921-942a62). They are "
         "queued here because the queue edits recording their execution were lost along with the "
         "artifacts, not because they were never dispatched. This revision is the one thing that "
         "attempt teaches which can be fixed before the next: each card declared three files and "
         "each reader filed far more -- seventeen and twelve -- including the recheck that carried "
         "the counterexample to Lemma 4's inside form, which was the most valuable single artifact "
         "either read produced. tools/producer_landing.py commits the DECLARED set and nothing "
         "else, by design, so under the new mechanism those extras would STILL have been lost. "
         "Declaring them is what closes that."),
        ("what_this_revision_does_not_do",
         "It does not change either card's objective, joints, questions, blindness, budget or "
         "inference, and it does not touch the read plan. The scientific content of the round is "
         "unchanged and its prior is still the one recorded before any reader ran, so the "
         "re-dispatch inherits the round's independence in full. It also does not pretend the "
         "first attempt did not happen: the correction records it, and no artifact from it is "
         "cited anywhere."),
        ("cost_stated_plainly",
         "A reader with nothing mechanically checkable now has to write two files saying so. That "
         "is a real if small tax on every future run of these cards, accepted because the "
         "alternative -- negotiating the declared set per reader, after the fact -- is what "
         "produced an undeclared-artifact dispatch error on the first attempt and a total loss on "
         "the second."),
    ]),
    od([
        ("at", "2026-09-21T15:40:00Z"),
        ("task_id", READS_SNAPSHOT),
        ("from_state", "queued"),
        ("to_state", "completed"),
        ("what_changed",
         "Both reads and their snapshot archive recorded as executed in EXECUTED, with the "
         "archive's commit, parent and thirteen path hashes bound."),
        ("reason",
         "The widened cards ran at epoch 2 and both filed all six declared artifacts. Each set was "
         "landed by tools/producer_landing.py at the moment its reader returned -- c31504e97 and "
         "c0a107514 -- so for the first time in this round the output was in the repository before "
         "anything could take the machine away. The re-claim used the "
         "`--supersedes-lost-completion` path added to tools/goal_lanes.py, which refuses unless "
         "the declared artifacts are verifiably absent, so the epoch-1 completions could not have "
         "been overwritten by mistake."),
        ("the_ordering_inversion_this_records",
         "The archive commit stages only its receipt, because the artifacts it binds were already "
         "committed. Every previous archive in this batch created the files it bound. That change "
         "is deliberate and is the correction's remedy, but it has a cost worth stating where a "
         "later reader will meet it: the archive commit is no longer where you learn when an "
         "artifact first existed, and a reader reconstructing the timeline must read the landing "
         "commit instead. The receipt says so in its own "
         "`the_source_artifacts_were_ALREADY_COMMITTED_when_this_archive_ran` block."),
        ("what_this_revision_does_not_do",
         "It records no verdict. Both readers broke their joints -- J-3 on the derivation, J-4c on "
         "the statement-versus-argument gap -- and the Semaev reader's proves-too-much control "
         "FAILED, which is the strongest single result of the round. None of that is a program "
         "conclusion until TASK-20260916-a8e5b5 composes the joints and a ledger archive commits "
         "the decision. In particular the reader's report that this batch's inside-versus-outside "
         "residual was drawn on the inert side is a claim the Coordinator has reproduced "
         "arithmetically and has NOT yet ruled on."),
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
     "Read the two frozen sources the campaign's central inference actually rests on. "
     "EXP-SEMBIN-4fa22c measures the FAKE first fall degree d'_F; every step from there to a "
     "statement of Nagao's runs through 2015/984's Lemma 4 (d_F <= d'_F), which that paper asserts "
     "WITHOUT PROOF, derives from its Lemma 3, attributes to [11] = 2013/549, and declines to "
     "prove. The program has separately verified by exhaustive search over F_2 that Lemma 4's "
     "LITERAL form with the field equations OUTSIDE is FALSE. So this lane asks whether the "
     "upstream source contains and proves what the consumer says it does, in the form the consumer "
     "needs -- and, in parallel, what Semaev 2015/310's argument delivers as against what his "
     "statement claims. Neither answer can change DC-1 or refute Proposition 5. Both change how "
     "conditional a confirmation is, which the contract records as a dependency."),
    ("max_concurrent", 2),
    ("max_concurrent_basis",
     "TWO, because the two producers here are readers of frozen PDF text with maximum_runs 0 and "
     "no engine between them, and their joints are disjoint by construction. This is machine "
     "headroom, not a research budget: the same machine is concurrently running BATCH-cbb416, "
     "whose max_concurrent is 1 because ITS producer is a degree-by-degree GF(2) rank computation "
     "with a 10 GB watchdog. Two readers alongside it cost that measurement nothing, which is the "
     "whole reason this is a separate lane rather than two more cards in that batch."),
    ("notes", [
        od([
            ("at", "2026-09-16T11:10:00Z"),
            ("kind", "why_this_lane_is_not_make_work"),
            ("text",
             "An unlimited ECC budget is the strongest invitation to make-work this program has, so "
             "the ranking is stated rather than assumed. This is ranked item (2) of the goal head, "
             "which says in terms that it needs no compute and competes with the batch for nothing "
             "and may therefore run concurrently in a separate lane. It is ranked ahead of doing "
             "nothing on a concrete ground: EXP-SEMBIN-4fa22c is approved and about to spend "
             "compute measuring a quantity whose only route to any claim of Nagao's is a lemma "
             "with no proof in the consuming paper and no reader in this program. Learning that "
             "the upstream proof is absent or insufficient is cheaper before the run than after, "
             "and the run's own contract cannot discover it."),
        ]),
        od([
            ("at", "2026-09-16T11:10:00Z"),
            ("kind", "the_prior_is_recorded_first_and_here_is_why"),
            ("text",
             "This campaign has one precedent for exactly this shape of task and it is decisive: on "
             "2026-09-16 a blind read of Nagao 2015/984's Proposition 5 OVERTURNED the "
             "Coordinator's reading, and the goal's objective changed as a result "
             "(CORR-20260916-96f47d, DEC-20260916-88ac73). It was informative because the "
             "Coordinator's expectation was written down first and the reader could not see it. "
             "The prior for this round is at coordination/review/sembin-20260916-e0a0c1/"
             "read-plan.yaml, both readers are blind from it, and one of its six predictions is "
             "recorded specifically because the Coordinator's own checking refuted it."),
        ]),
        od([
            ("at", "2026-09-16T11:10:00Z"),
            ("kind", "what_this_lane_cannot_reach"),
            ("text",
             "It cannot refute Proposition 5, cannot promote or weaken H-SEMBIN-a7e721 (no "
             "measurement exists), and cannot discharge a completion criterion by itself -- all "
             "four of this goal's criteria need a committed decision on run or read evidence, and "
             "a report is not a decision. It also cannot decide anything about the FIRST revision "
             "of 2013/549, which is not served and not in inputs/. AND IF A READER FINDS THE "
             "UPSTREAM LEMMA UNPROVED, the resulting claim needs review-breakthrough at max, "
             "which is undegradable and unservable here: the finding is recorded at its narrowest "
             "scope and the CLAIM stays un-promoted while the campaign stays active."),
        ]),
        od([
            ("at", "2026-09-16T11:10:00Z"),
            ("kind", "two_binding_modes_on_purpose"),
            ("text",
             "The opening archive binds content_at_commit and the reader archive binds "
             "content_first, and the difference is not an oversight. The control plane contains the "
             "goal head and this queue, which legitimately change after the archive; a reader's "
             "filed report never does. content_first is what catches an in-place edit to a filed "
             "artifact, which the sibling campaign has suffered twice (CORR-20260916-5166fe, "
             "CORR-20260916-2e9bc3). Choose the mode by asking what the archive is protecting."),
        ]),
        od([
            ("at", "2026-09-16T11:10:00Z"),
            ("kind", "concurrency"),
            ("text",
             "SECOND OPEN LANE on GOAL-SEMBIN-fcb7a2. BATCH-cbb416 is open and holds the operative "
             "next_action in its own checkpoint; this lane touches none of its paths and edits the "
             "goal head only additively inside its own archives "
             "(docs/concurrent-goal-lanes.md). Check `tools/goal_lanes.py lanes "
             "GOAL-SEMBIN-fcb7a2` after a fetch rather than assuming this session knows who else "
             "is here."),
        ]),
    ]),
    ("tasks_state_revisions", REVISIONS),
    ("tasks", tasks),
])

# Resolve against the REPOSITORY ROOT, never the caller's cwd. `BASE` is a
# repository-relative path, and `mkdir(parents=True)` made a wrong cwd silently
# succeed: run from inside the batch directory this wrote a nested
# BATCH-e0a0c1/coordination/goals/.../dispatch_queue.json, reported success, and
# left the real queue untouched -- so a widened declaration looked applied and
# was not. A builder that cannot find its own repository must fail, not guess.
def _repository_root() -> pathlib.Path:
    for candidate in [pathlib.Path(__file__).resolve(),
                      *pathlib.Path(__file__).resolve().parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / ".git").exists():
            return candidate
    raise SystemExit("cannot locate the repository root above this build script")


path = _repository_root() / BASE / "dispatch_queue.json"
if not path.parent.is_dir():
    raise SystemExit(f"{path.parent} does not exist; refusing to create a queue "
                     f"directory from a path that may be wrong")
path.write_text(json.dumps(queue, indent=1) + "\n")
print(f"wrote {path.relative_to(_repository_root())} with {len(tasks)} tasks")
