# Coordinator portfolio ruling opening BATCH-27c132

Recorded 2026-08-14. Goal `GOAL-MLKEM-005`, discharging
`DEC-20260814-b0a095`'s single `next_action` (the close of `BATCH-a5b13c`).

**What this instrument is.** A pre-dispatch portfolio ruling, matching the
discipline `DEC-20260813-9c7353` itself modeled and that `DEC-20260814-b0a095`
required explicitly: "THE NEXT COORDINATOR SESSION OPENING A BATCH ON
RQ-MLKEM-001 MUST MAKE AN EXPLICIT, REASONED PORTFOLIO CHOICE -- NOT
DEFAULTED." It writes no ledger record, changes no hypothesis status, and
commits nothing (this session holds no shell). Its consequence, if any, is the
dispatch queue and task card opened alongside it in this same directory, which
become durable only through a separate, later Coordinator-archived commit that
the post-commit verifier accepts.

## 0. Provenance of the facts used

**Read directly by me in this session (read-only, no shell):**
`ledger/decisions/DEC-20260814-b0a095.yaml`; `ledger/goals/GOAL-MLKEM-005.yaml`
(`research_goal` header and `completion_criteria` sections); `ledger/questions/RQ-MLKEM-001.yaml`;
`experiments/EXP-MLKEM-bfdb63/specification.yaml` (full text); `ledger/hypotheses/H-MLKEM-232843.yaml`;
`ledger/hypotheses/H-MLKEM-34e22e.yaml`; `ledger/hypotheses/H-MLKEM-dc51f5.yaml` (found by grep,
not named in the brief); `experiments/EXP-MLKEM-6715e6/specification.yaml` header fields;
`docs/task-lifecycle.md`; `docs/dynamic-subagent-dispatch.md`; `docs/target-result-profile.md`
(Part A, A1-A2); `.claude/agents/idea-generator.md`; `.claude/skills/propose-ideas/SKILL.md`;
and `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a5b13c/dispatch_queue.json` /
`tasks/TASK-20260814-d13724/task_card.md` for the rigor precedent this batch matches.

**Not verified by me:** whether any other in-flight worktree is concurrently opening a
conflicting batch on `RQ-MLKEM-001`; the two-scope `--check` status of `TASK-20260814-ac35d8`
(stated as already confirmed in my brief; I did not re-run `allocate_id.py` myself, holding no
shell).

## 1. Correction to the brief's own premise: EXP-MLKEM-bfdb63 is not a specification for option (ii)

The task that opened this session characterized `EXP-MLKEM-bfdb63` as targeting
"exactly the goal's own primary best-of-M/Beta-law objective." Having now read the
full spec, **this is not correct**, and the correction is load-bearing for the
portfolio choice below, so it is recorded first rather than folded silently into
the ruling.

`EXP-MLKEM-bfdb63.experiment.goal_id` is `GOAL-MLKEM-001`, not `GOAL-MLKEM-005`.
Its `hypothesis_id` is `H-MLKEM-6d9364`, a hypothesis about the **negacyclic
adjoint identity / orbit-amortisation mechanism** (`IDEA-20260722-001`'s
successor): whether the 2n coordinate rotations of a ring element's dual vector
let an attacker amortise a score-evaluation cost across the whole orbit, tested
by an exact operation-DAG accounting instrument (op-count ratios, a matched
unstructured null, a CYC-FFT positive control, and — only if the estimator is
reachable — a score-evaluation-share ceiling `f_score`). This is a **ring/algebraic-
structure exploitation mechanism** (RQ-MLKEM-001's own scope lists "module and ring
structure exploitation" as a distinct method from "primal and dual lattice
attacks"), entirely disjoint from GOAL-MLKEM-005's tracked object (a shared
BKZ-reduced basis and the per-target ratio `R = ||pi_{d-beta}(e)||^2 / ||e||^2` of
a CBD error vector under best-of-M ciphertext selection). Nothing in
`EXP-MLKEM-bfdb63` measures a block-size bound under best-of-M selection, a
census of M, or a Beta-law tail on a projected error norm. Its own text is
explicit that it would run **only under a successor goal to GOAL-MLKEM-001**
(`approval_requirements`: "A successor goal record exists; GOAL-MLKEM-001 is
closed at budget and authorizes nothing"), and `outcomes.no_execution_authorization`
states plainly this is presently "a `review_required` draft. No run, no
observation, no evidence, no inference" with no goal it could currently be
authorized under.

This is **not a repairable gap** in an otherwise-relevant contract. There is no
edit that turns an orbit-amortisation op-count instrument into a best-of-M
ciphertext-selection / Beta-law measurement; they are different mechanisms
answering different questions, sharing only `RQ-MLKEM-001` as a parent and the
coincidence that both happen to sit in `review_required` limbo. Authorizing
`EXP-MLKEM-bfdb63` as-is, even if perfectly executed, would **not advance any
of GOAL-MLKEM-005's own C1-C5** and would misuse a goal-scoped batch to revive
a different, closed goal's orphaned draft without the successor-goal act its
own `approval_requirements` demand. I therefore **do not authorize, freeze, or
recommend repairing `EXP-MLKEM-bfdb63` in this batch**. Whether a
`GOAL-MLKEM-006`-shaped successor to the closed `GOAL-MLKEM-001` orbit-
amortisation lane is ever opened is a separate, future portfolio question this
ruling does not decide and does not foreclose.

## 2. A second correction, found in the same pass: option (ii) has no ready instrument either

Grepping `ledger/hypotheses/*.yaml` for the actual C1/C3 vocabulary
(`best-of-M`, `Beta law`, `projected-error-norm`, `dbeta`) returns four files:
`H-MLKEM-11aabf` (just moved to `analyzed`, its own `interpretation_limits`
stating it "does not and cannot advance" C1/C3), `H-MLKEM-232843` and
`H-MLKEM-34e22e` (both explicitly self-scoped as unrelated — see section 3
below), and one hypothesis **not named anywhere in the brief or in
`DEC-20260814-b0a095`'s enumeration of "three idle hypotheses": `H-MLKEM-dc51f5`**.

`H-MLKEM-dc51f5` (`goal_id: GOAL-MLKEM-005`, `status: proposed`, never
dispatched — its own paired experiment draft `EXP-MLKEM-6715e6` is likewise
`status: review_required`, `frozen: false`, `execution_authorized: false`,
`goal_id: GOAL-MLKEM-005`, zero runs archived) is closer to this goal's own
object than anything else idle in the ledger, but it is still **not the C1/C3
tracked object**: it screens whether **multi-target key recovery by selecting
among N independently keyed sessions on realised secret norm** (primal uSVP)
can beat single-target attack, a key-side selection mechanism. Its own
`interpretation_limits` state: "GOAL-MLKEM-005's C2 is PARTIALLY served: the
measured arms are real measurements with a named removed object ... but they
measure the SELECTION claim, not the cost balance." Nothing in it touches a
shared reduced basis, a ciphertext-side projected-error ratio, or a Beta-law
tail check on real BKZ-reduced bases with real CBD errors — the actual C1 and
C3 objects. I record this as a genuine, adjacent finding (worth a future
session's attention) but **it does not change the ruling below**: no
hypothesis currently in the ledger, proposed or otherwise, targets
GOAL-MLKEM-005's C1/C3 tracked object directly.

**Consequence:** option (ii), while correctly identified by `DEC-20260814-b0a095`
as "the actual reason GOAL-MLKEM-005 exists," is **not cheap-and-ready** in the
way the brief's premise about `EXP-MLKEM-bfdb63` suggested. There is nothing to
authorize. The correct first act toward option (ii) is `/propose-ideas`, not
`/design-experiment`.

## 3. Re-confirming option (iii): H-MLKEM-232843 and H-MLKEM-34e22e

Re-read in full this session. Both carry, verbatim, an `interpretation_limits`
clause stating they do "not touch and does not contradict GOAL-MLKEM-005's
proven convexity ceiling G <= log2 M" and are explicitly "unrelated to best-of-M
ciphertext selection against a shared reduced basis" (232843: implementation-
level decapsulation-key field integrity, a `GOAL-MLKEM-002`-adjacent defect-
detection instrument; 34e22e: per-key-generation sampler-budget defect
detection, a third, distinct defect-mechanism class from the same lineage).
Both are `status: proposed`, both are real, well-specified, falsifiable control-
tier hypotheses under `RQ-MLKEM-001`'s "decryption-failure and side-information
amplification" / general defect-detection scope — but neither is closer to
GOAL-MLKEM-005's own tracked object than `H-MLKEM-dc51f5` is, and both were
already correctly ruled topically orthogonal when `BATCH-a5b13c` was opened.
**That reasoning still holds; nothing found this session changes it.**

## 4. The ruling

**Chosen: option (ii), redirect RQ-MLKEM-001 capacity toward GOAL-MLKEM-005's
own untouched C1-C3 completion criteria — via a fresh `/propose-ideas` pass,
not a `/design-experiment` pass, because no live idea or hypothesis currently
targets that object.** Not option (i). Not option (iii). Reasoned explicitly
below, weighing all three against this goal's own declared standard rather than
against ease of drafting.

**Why not (iii).** Confirmed in section 3: both `H-MLKEM-232843` and
`H-MLKEM-34e22e` are self-scoped, on their own text, as not bearing on this
goal's tracked object at all. Advancing either would produce a third and fourth
well-executed control-tier finding in a lineage (implementation-defect
detection) this goal did not exist to run, while its own declared reason for
existing sits untouched. Real work, wrong goal.

**Why not (i).** Real, cheap, and licensed: a reformulated-M2 or instrument-
extension follow-up on `H-MLKEM-11aabf` would reuse the same pinned,
already-controlled `tools/sage_free_estimator` harness, and both of
`BATCH-a5b13c`'s independent reviews converged on concrete forward guidance for
it. But `H-MLKEM-11aabf`'s own `interpretation_limits`, restated three times now
across `DEC-20260814-b0a095` and this ruling, say plainly it "does not and
cannot advance" GOAL-MLKEM-005's C1/C3. Choosing (i) would extend a
`MEDIUM`-tier, already-`analyzed` ciphertext-noise-modelling lane for a further
batch while the goal's own `stop_rule` ("The goal MUST close as `completed` as
soon as C1-C3 are met, even with work remaining... a campaign that has its
answer and keeps spending is a budget failure, not diligence") sits against a
completion criterion that roughly twenty batches across this goal's history —
the `hkz`/HKZ-independence instrument-calibration lineage, the ciphertext-noise-
modelling lineage now closing on `H-MLKEM-11aabf`, and the untouched control-
tier hypotheses of option (iii) — have never once addressed. `docs/target-
result-profile.md` A1's exponent-first bias does not itself discriminate among
(i)/(ii)/(iii): GOAL-MLKEM-005's own `ceiling_known_in_advance` proves, in
advance, that *no* lane of this goal can move an exponent (`dbeta/beta ~
0.29*sqrt((1-rho)*ln M/beta)`, `G <= log2 M` unconditionally) — so the
exponent-first bias operates at the *cross-goal* portfolio level (favoring other
goals in this program over more constant-cofactor work here), not as a
tiebreaker within GOAL-MLKEM-005. What does discriminate within this goal is
its own declared standard: the stop rule exists precisely so a campaign with an
answerable, bounded question does not drift into adjacent, always-productive,
never-decisive lanes. Choosing (i) again — cheap, known-good instrument, real
forward guidance from two reviews — is exactly the kind of choice this goal's
own unbounded-budget design warns against defaulting to: momentum toward the
easiest next increment, not the reasoned choice DEC-20260814-b0a095 required.
AGENTS.md rule 9 forbids "deliberately abandon[ing]... or steer[ing] away from
a plausible high-value lead," and repeatedly reaching for the cheap, adjacent,
already-productive lane over the goal's own declared object — while not
malicious — is the same failure shape from the other direction: it is how a
goal's actual question goes unanswered for twenty batches without anyone ever
deciding not to answer it.

**Why (ii), stated affirmatively.** GOAL-MLKEM-005 exists to answer C1 (a
numeric best-of-M `dbeta` bound under a named cost model), C2 (a census of M),
and C3 (the projected-error-norm/Beta-law measurement on real BKZ-reduced bases
with real CBD errors), and its `stop_rule` requires the campaign to close the
moment those are answered, "even with work remaining." Zero batches have yet
targeted them directly. C2 in particular is the cheapest possible next
foothold — it is a literature/deployment-specification census ("M = 1 in every
standardised mode we could source" satisfies it in full), not a measurement
requiring lattice reduction — and a determined M value is a *direct input* to
C1's own bound ("attainable by best-of-M selection at the M established in
C2"). C3 is the heavier lift (it needs real BKZ-reduced bases with real CBD
errors, which this program's `hkz`/HKZ-independence lineage has already built
and validated `fpylll`/BKZ infrastructure for elsewhere in this same goal,
lowering its marginal cost relative to building that infrastructure from
scratch). Because no hypothesis in the ledger currently targets this object,
the correct dispatch is ideation, not design: `/propose-ideas` on
`RQ-MLKEM-001`, explicitly scoped to C1-C3, informed by (but not derailed by)
the adjacent `H-MLKEM-dc51f5`/`EXP-MLKEM-6715e6` draft and by the now-corrected
understanding that `EXP-MLKEM-bfdb63` belongs to a different goal entirely.

## 5. What this ruling does not do

It does not close, pause, or complete `GOAL-MLKEM-005`. It does not change any
hypothesis status — `H-MLKEM-dc51f5`, `H-MLKEM-232843`, and `H-MLKEM-34e22e`
remain `proposed`, exactly as `DEC-20260814-b0a095` left them. It does not
edit, freeze, repair, or authorize `EXP-MLKEM-bfdb63` or `EXP-MLKEM-6715e6` —
both remain exactly as committed; any repair or freezing of either is a
separate, future Coordinator-approval-gated act on its own frozen path, not
enacted here. It does not decide whether a `GOAL-MLKEM-001`-successor goal is
ever opened for the orbit-amortisation lane `EXP-MLKEM-bfdb63` belongs to. It
does not pre-select which idea, if any, returned by `TASK-20260814-ac35d8`
becomes a hypothesis — that is a separate, later Coordinator act once ideas
exist to evaluate. It carries forward unchanged every binding-carry item
`DEC-20260814-b0a095` and its predecessors already fixed (claim tier discipline,
the M2 corrected citable wording, the M0=M1 forced-identity finding, AGENTS.md
rule 12 unmet/unwaived, `knowledge/INDEX.md` never written or staged).

## 6. Identifiers

`TASK-20260814-ac35d8` is used exactly as supplied, for the idea-generator
task opening this batch. **No further identifier is needed to open this
batch.** The follow-on snapshot-archive task (per `.claude/skills/propose-
ideas/SKILL.md` step 5, committing the returned `IDEA-*` proposal(s) before
they are treated as filed) and the `IDEA-YYYYMMDD-NNN` identifier(s) for
whatever proposals `TASK-20260814-ac35d8` actually returns cannot be sized or
minted yet — the count of proposals is unknown until ideation runs — and are
recorded as a declared gap in `dispatch_queue.json` (`G-1`), to be minted via
`tools/allocate_id.py --next task --check` and `--next idea --check`
respectively once ideation completes, matching this goal's own established
`declared_gaps` convention (e.g. `BATCH-a5b13c` `G-6`).
