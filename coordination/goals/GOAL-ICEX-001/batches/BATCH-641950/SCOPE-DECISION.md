# BATCH-641950 scope decision — GOAL-ICEX-001 — **PAUSE (batch not opened)**

Candidate: `ledger/proposals/IDEA-20260803-fa9839.yaml` — the arity-threshold charged
cost model — routed here by `ledger/decisions/DEC-20260805-bb162b.yaml`.

**Disposition: PAUSE. BATCH-641950 is NOT opened.** No producer, review, or archive task
is dispatched. No `batch.yaml`, no `dispatch_queue.json`, no task card, and no
`ledger/handoffs/TASK-20260806-*.yaml` is written. This file is the whole of the batch.

**This is a sequencing pause, not a merit decline and not a closure.** The routed
proposal is live, is being pursued right now by another batch, and its algebra
reproduces under independent re-derivation (§5). What this record decides is that
**GOAL-ICEX-001 is not the goal that may execute it today**, and it names the exact
committed artifacts whose arrival makes it eligible (§7).

---

## 0. The single fact that reframes the question

**The brief states that nobody has picked the proposal up. Against working-tree state
that is false.** A live batch is already executing it:

- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/dispatch_queue.json` —
  five tasks, `max_concurrent: 3`, objective naming `IDEA-20260803-fa9839` explicitly.
- `ledger/hypotheses/H-ICEX-9e54c2.yaml` — `status: specified`,
  `question_id: RQ-ICEX-001`, `source_proposal_id: IDEA-20260803-fa9839`,
  `specified_at: '2026-08-06'`, `specified_under_task: TASK-20260806-cd81c5`.
- `experiments/EXP-ICEX-146ff5/specification.yaml` — `status: approved`,
  `approved_under_task: TASK-20260806-cd81c5`, `frozen_at: '2026-08-06'`.

The brief is right in one strict sense and it is the sense that matters for durability:
**none of this is committed.** The contract says so in its own words:

> `approved_at_precision:` "... It ran no git command, made no commit, and every
> commit_sha, parent_sha and path_sha256 associated with this freeze is null. NOTHING
> HERE IS DURABLE OR OFFICIAL until TASK-20260806-fb85f5 commits it and the dispatcher's
> post-commit verifier accepts that commit."

`BATCH-9c41dd` has no `archives/` directory. `TASK-20260806-fb85f5` (snapshot),
`TASK-20260806-7e7ce3` (independent red team), and `TASK-20260806-636e61` (ledger
archive) have all produced nothing. So the state is: **an approved, unreviewed,
uncommitted contract, three preconditions open, in another goal's live batch.**

And the second of those preconditions is addressed to me by name:

> `execution_authorization: granted: false` … **P2 GOAL BINDING UNRESOLVED.**
> "…routed it to GOAL-ICEX-001, whose next_action reads 'NO ICEX MEASUREMENT
> AUTHORIZED' and defers 'until charged SDEG/MONO/RELN measurement packages exist'.
> That deferral is on MEASUREMENT and this contract performs none, but the reading is
> GOAL-ICEX-001's Coordinator's to make on its own record, preserving its own single
> next action. THIS FILE DOES NOT MAKE IT AND DOES NOT PRE-EMPT IT."

§1 answers P2. §2–§4 explain why answering it does not license a batch today.

---

## 1. Question 1 — is a zero-compute closed-form derivation a "measurement"?

Argued both ways, then concluded. The prohibition, quoted **verbatim** from
`ledger/goals/GOAL-ICEX-001.yaml` `next_action`:

> "UNCHANGED IN SUBSTANCE - remain non-executing until charged SDEG/MONO/RELN
> measurement packages exist; optionally tighten RT023-O1/O2 at seal. NO ICEX
> MEASUREMENT AUTHORIZED (DEC-20260731-015 / EV-ICEX-001). ONE MANDATORY READ IS ADDED:
> BEFORE CONSUMING ANY MONO FEED, READ DEC-20260802-a51c82."

And **verbatim** from `ledger/evidence/EV-ICEX-001.yaml` `inference`:

> "Adopt PASS for the review-only ICEX exponent protocol design. **Do not authorize
> implementation or measurement until charged SDEG/MONO/RELN measurement packages exist
> and a separate Coordinator ledger authorization is issued.**"

**The case that a derivation is NOT covered.** The capitalised clause names
*measurement*, and the stated precondition is the existence of *measurement packages* —
inputs a measurement consumes. `EXP-ICEX-146ff5` consumes none of them: its
`admission_and_ceiling` states "THIS EXPERIMENT MEASURES NOTHING ABOUT ECDLP. It solves
no discrete logarithm, constructs no oracle, runs no summation-polynomial solve, and
touches no elliptic curve." Its `certificate.kind` is `none` because nothing is claimed.
Its enumerations are over `Z/N` for the null control only. A prohibition conditioned on
the arrival of inputs that a given piece of work does not use is not naturally read as
barring that work, and reading it so risks the premature-closure failure mode
`docs/inventor-protocol.md` §4 treats as symmetric with overclaiming. `EV-ICEX-001`'s
own boundary — "Protocol-design PASS only" — attaches the deferral to *that* frozen
measurement protocol, not to every thought about the question.

**The case that it IS covered, which I find stronger.** Three grounds.

1. **The operative clause is not the one about measurement.** The sentence opens
   "remain **non-executing**", and only then adds "NO ICEX MEASUREMENT AUTHORIZED" as a
   citation-bearing restatement. "Non-executing" is a statement about the goal's
   dispatch status, not about a category of work. A batch with a producer, a validator,
   and two archive tasks consuming wall-clock budget is execution on any reading.
2. **`EV-ICEX-001` forbids "implementation **or** measurement", conjoined with a
   *second*, independent precondition** — "and a separate Coordinator ledger
   authorization is issued." That authorization has never been issued. It is a ledger
   act. This task may not write to `ledger/decisions/`, `ledger/goals/`, or any
   hypothesis or evidence record, so I cannot issue it here, and a `SCOPE-DECISION.md`
   is a coordination artifact that cannot substitute for it. The precondition is unmet
   and remains unmet whatever "measurement" means.
3. **The deliverable is the deferred comparison.** The contract's declared satellite
   output is a `D_reg_max` table telling `GOAL-SDEG-001`, `GOAL-DREG-001` and
   `GOAL-SIG-001` what their deferred measurements would have to read. That is the
   substance of the aggregation this goal defers, reached by model instead of by
   measurement. It does not *meet* the completion criterion (a free `D_trial` cannot
   produce a confidence interval, so no CI can exclude 1/2), but it is close enough to
   the deferred object that treating the word "measurement" as the whole of the
   prohibition would be reading the gate narrowly in order to get through it.

**Conclusion.** On its words the prohibition covers this batch — not via "measurement",
but via "remain non-executing" and via `EV-ICEX-001`'s unmet requirement of a separate
Coordinator ledger authorization. **Recorded answer to P2: the measurement deferral does
not by itself bar a zero-compute derivation, and I do not read it as doing so; but the
non-execution clause and the missing separate ledger authorization do bar
GOAL-ICEX-001 from opening an execution batch today.** Per the instruction I received
and per `agents/coordinator.md`, I do not reinterpret a prohibition to enable work.

---

## 2. Question 2 — has a pause condition fired?

`pause_conditions` as committed:

1. "User requests pause." — **NOT fired.** No user request is on this record.
2. "Prerequisites remain without auditable next action beyond campaign budget." —
   **FIRED.** See below.
3. "Archive verification fails." — **NOT fired.** No archive was attempted by this task;
   nothing was staged, committed, or verified. This condition is untouched, not passed.

**Limb (a): the prerequisites plainly remain.** No charged SDEG/MONO/RELN measurement
package exists. `GOAL-MONO-001` is the sharpest case: `DEC-20260802-a51c82` `N-2`
records "The campaign budget is exhausted: maximum_batches is 3 and BATCH-003 is the
third. GOAL-MONO-001 moves to paused… Resuming requires a fresh budget grant."

**Limb (b): is the routed proposal an auditable next action that does not need them?**
No — not for *this goal, today*. Four independent grounds, each checkable:

- **(b1) The contract is uncommitted.** `AGENTS.md` "Durable research commits" requires a
  snapshot commit of the exact contract *before* an independent agent reviews it, and
  the contract itself binds execution to "the COMMITTED BLOB at the TASK-20260806-fb85f5
  snapshot commit, never the working-tree file." That commit does not exist. Executing
  against a working-tree contract is an evidence-integrity failure, not a result.
- **(b2) P1 is undischarged and is not mine to discharge.** `EXP-ICEX-146ff5` requires
  "P1 INDEPENDENT RED-TEAM PASS. TASK-20260806-7e7ce3 reviews this contract in an
  independent session." That task exists, is queued under `BATCH-9c41dd` at
  `review-adversarial`/`xhigh`/`independent_session_required: true`, and has not run.
  The batch I was offered has a *validator*, not a red team, and substituting a
  different review type for a named precondition on a contract another batch owns is
  not a discharge.
- **(b3) Write scopes cannot be made disjoint.** Any producer executing this contract
  must write `experiments/EXP-ICEX-146ff5/runs/**` and `results/`. `BATCH-9c41dd`'s live
  `TASK-20260806-cd81c5` declares `write_scope: experiments/EXP-ICEX-146ff5/`. `AGENTS.md`
  dynamic dispatch: "Each dispatched task owns non-overlapping repository-relative
  `write_scope` paths." I cannot satisfy that requirement and the brief's own
  disjoint-write-scope constraint simultaneously.
- **(b4) The goal record would be left inconsistent.** `GOAL-ICEX-001` carries
  `current_batch_id: BATCH-001` and `dispatch_queue_path` pointing at BATCH-001, and I
  may not edit it. Opening BATCH-641950 leaves an unreferenced second active batch
  beside an unchanged `next_action` that still says "remain non-executing" — the exact
  structural inconsistency `DEC-20260805-bb162b` gave as disqualifying for
  `GOAL-ECDLP-001`. Applying it to that goal and not to this one would be
  special pleading.

There **is** an auditable next action for the *lane* — finish `BATCH-9c41dd`. There is
no auditable next action for **this goal** that does not need its prerequisites or
another goal's uncommitted, unreviewed artifacts. Condition 2 fires on that reading, and
the reading is stated so a reviewer can disagree with it precisely.

---

## 3. What a batch would actually have produced today

Recorded so the pause is checkable rather than asserted. The producer slot
(`TASK-20260806-50d12c`, "zero compute") admits exactly two fillings, and both fail:

- **Fill it with the derivation.** It already exists, in the working tree, as
  `H-ICEX-9e54c2` + `EXP-ICEX-146ff5` + `BATCH-9c41dd/tasks/TASK-20260806-cd81c5/design_report.md`.
  A second producer would either duplicate them or fork them, and a fork of an
  uncommitted contract under a second goal is the identifier-and-archive hazard
  `CLAUDE.md` "Concurrency" exists to prevent.
- **Fill it with the run.** Blocked by (b1), (b2), (b3) above, and by
  `execution_authorization.granted: false`.

A third, reduced filling — "emit a corrected model note" — was considered and rejected:
every component of it is already committed. The corrected optimizer, `T*`, the threshold
`d < (m−3)/4` and the `2/(n(n+1))` identity are in `DEC-20260805-bb162b.limitations`;
defects D2/D3/D4 are in `CORR-20260805-4b91ca`; the `B`-dependence audit and the
coupon-collector correction are in `ideas/catalogue-20260805/A1-index-calculus.md`
A1-2 and A1-8. Restating four committed records in a fifth place is curation, and
curation into `knowledge/` requires a promotion this decision cannot warrant (no
evidence record, no run, no `replicated`/`strong` evidence).

---

## 4. Standing prohibitions, carried verbatim

Binding on anything that cites this file.

From `ledger/goals/GOAL-ICEX-001.yaml` `next_action`:

> "remain non-executing until charged SDEG/MONO/RELN measurement packages exist … NO
> ICEX MEASUREMENT AUTHORIZED (DEC-20260731-015 / EV-ICEX-001). ONE MANDATORY READ IS
> ADDED: BEFORE CONSUMING ANY MONO FEED, READ DEC-20260802-a51c82. … Do NOT use
> chebotarev_S2_split * (W_eff/p)^2: on the factor-base locus the m=3 summation fibre
> splits with probability EXACTLY 1, not freq_split, so the correction factor is
> (1 - 1/W_eff)/freq_split -> 2*(1 - 1/W_eff). USE THE FORMULA, NOT THE NUMBER - the 1.5
> measured at W_eff=4 is not the limit, which is 2. The factor is constant at fixed m and
> fixed W_eff and moves no exponent HERE, but a per-fibre factor of 2 compounds as
> 2^{n-1} in a Gaudry/Diem-style decomposition over F_{q^n} with n growing, where it
> would."

From `ledger/decisions/DEC-20260802-a51c82.yaml`
`the_icex_feed_supersession.scope_that_must_travel_with_it`:

> "IT IS NOT UNCONDITIONALLY CONSTANT. Applied once per summation fibre in a
> Gaudry/Diem-style decomposition over F_{q^n} with n growing, a per-fibre factor of 2
> compounds as 2^{n-1} = q^{Theta(1)} and DOES move an exponent. Any ICEX statement
> quoting 'moves no exponent' must carry this scope."

From `ledger/evidence/EV-ICEX-001.yaml`:

> "Do not authorize implementation or measurement until charged SDEG/MONO/RELN
> measurement packages exist and a separate Coordinator ledger authorization is issued."
> … "Protocol-design PASS only; toy claim tier; protocol PASS ≠ measurement ≠ crypto-scale
> IC-beats-rho."

From `ledger/proposals/IDEA-20260803-fa9839.yaml` `interpretation_limits`, adopted
unchanged as the ceiling for any successor:

> "THIS CANNOT ESTABLISH THAT PRIME-FIELD INDEX CALCULUS FAILS, AND IT CANNOT ESTABLISH
> THAT IT SUCCEEDS." … "'No admissible D_trial within this model' must NEVER be written
> as 'm <= 3 is impossible'."

**Claim ceiling for this record: `toy`.** Pollard rho at `c_rho·sqrt(N)` remains the
ECDLP baseline; `sota_delta` is zero on every axis. No breakthrough, closure, novelty,
completion, or hardness claim is made or authorized. `KN-OPEN-001` stays open in both
directions. No hypothesis status moves. All four asymptotic promotion gates in
`agents/coordinator.md` remain OPEN and none is attempted. AGENTS.md rule 13's closure
quorum is neither claimed nor claimable here.

---

## 5. What I verified, so the pause is not mistaken for doubt about the lane

Recorded because `AGENTS.md` rule 9 forbids steering away from a plausible lead, and a
pause that hides a positive check would do exactly that.

**The frozen contract's design-time algebra reproduces under my independent
re-derivation.** With `omega = 2` and the three declared constraints — balance
`(m−omega−1)/(2·omega)`, trial-count admissibility `omega/(m−1)`, and the
one-relation-per-target kink `(m−2)/(2m)` applicable where `d > (omega−1)/m` and
`m > 2·omega` — I obtain `sup W(m,2)` = EMPTY, EMPTY, 1/4, 3/10, 1/3, 1/3, 2/7, 1/4,
2/9, 1/5, 2/11 at `m = 2…12`. That matches `H-ICEX-9e54c2` `predictions[winning_window_shape]`
and `GATE-A` arm `A5` exactly. I also reproduce `CTRL-DEGENERATE` arm D2's
pre-registered raw flip at `m = 8`: at `D = N` the total exponent is `4/(m+1)`, and
`4/(m+1) < 1/2` iff `m > 7`.

**This is a check on arithmetic and on nothing else.** It is not evidence about ECDLP,
not a run, not a validation of the *charge*, and confers no strength on any row. The
contract's own `replication_honesty_note` says it best: "THIS IS A DERIVATION, NOT A
MEASUREMENT, AND ITS REPRODUCIBILITY IS NOT EVIDENCE OF ITS CORRECTNESS." It is recorded
here for one purpose: so that the pause reads as sequencing, and so that the reviewer of
`BATCH-9c41dd` knows the design-time rationals survived one independent re-derivation
before `GATE-A` ever runs.

**Two defects that survive into the frozen contract and should reach
`TASK-20260806-7e7ce3`.** Neither is a ground for this pause; both are recorded so they
are not lost.

- **`D_trial` is treated as independent of `B`.** The stationarity behind `GATE-A` arms
  A3/A4 differentiates `m!·N·D/B^(m−1) + c_LA·B^omega` holding `D` fixed. Catalogue entry
  A1-2 records that meet-in-the-middle supplies a *universal achievable*
  `D_trial = B^{⌈m/2⌉}`, a function of `B`, and that at `m = 9` the two accounts diverge
  qualitatively. The contract's quantifier order ("FOR EVERY family of factor bases of
  size `B(N)`, IF `D_trial = N^d`…") makes the window a statement about arithmetic and
  so does not *falsify* it, but no arm of `GATE-A` exercises a `B`-dependent `D`, and a
  window boundary is being read off a stationary point that a `B`-dependent oracle does
  not sit on.
- **Relations needed is not `B`.** `C_rel` charges `T_r = B/mu`. A1-8 records the
  coupon-collector floor `Θ((B/m)·ln B)`. I re-derived the consequence: the
  relation-search term gains a `ln B/m` factor, `B*` moves by a polylog factor, and the
  window boundary — an exponent comparison — is **unchanged**. This is a
  **log-cofactor correction only** and is explicitly non-target-class under
  `docs/target-result-profile.md`. It belongs in the contract's honesty column, not in
  its exponents.

---

## 6. Rule-9 record

**Evidence cited.** `ledger/goals/GOAL-ICEX-001.yaml` (`next_action`, `pause_conditions`,
`completion_criteria`, `current_batch_id`, `campaign_budget`);
`ledger/evidence/EV-ICEX-001.yaml`; `ledger/decisions/DEC-20260731-015.yaml`;
`ledger/decisions/DEC-20260802-a51c82.yaml`; `ledger/decisions/DEC-20260805-bb162b.yaml`;
`ledger/corrections/CORR-20260805-4b91ca.yaml`; `ledger/corrections/CORR-20260806-3ac71e.yaml`;
`ledger/proposals/IDEA-20260803-fa9839.yaml`; `ledger/proposals/IDEA-20260803-ff7415.yaml`;
`ledger/questions/RQ-ICEX-001.yaml`; `ledger/questions/RQ-ECDLP-002.yaml`;
`ledger/hypotheses/H-ICEX-9e54c2.yaml`; `experiments/EXP-ICEX-146ff5/specification.yaml`;
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/dispatch_queue.json`;
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-156658/SCOPE-DECISION.md`;
`knowledge/findings/KN-FIND-007.md`; `knowledge/findings/KN-FIND-c41ea9.md`;
`knowledge/open-problems/KN-OPEN-001.md`; `knowledge/open-problems/KN-OPEN-020.md`;
`ideas/catalogue-20260805/A1-index-calculus.md` (A1-1, A1-2, A1-3, A1-8, A1-13),
`SCREENING.md`, `CALIBRATION.md`.

**Budget consumed.** Zero against `total_wall_clock_seconds: 43200`. No Executor,
Validator, or Red Team session dispatched. `max_concurrent: 1` is not approached. The
`maximum_batches: null` amendment of 2026-08-02 is **not** consumed, **not** invoked, and
**not** relied on by this record; removing a batch cap creates no obligation to spend one.

**Test boundary.** Scoped to *whether GOAL-ICEX-001 opens BATCH-641950 on 2026-08-06*.
It decides nothing about the arity-threshold model's correctness (§5 finds its
design-time algebra reproduces), nothing about `KN-OPEN-001`, nothing about whether
prime-field index calculus can beat rho, nothing about `BATCH-9c41dd`'s merits or its
`GOAL-ECDLP-001` binding, and nothing about any deployed curve.

**Ranking against the alternatives not chosen.**

1. **(chosen) PAUSE, answer P2 on the record, name the resume trigger.** Costs nothing,
   loses nothing — the work is proceeding under `BATCH-9c41dd` — supplies P2's answer
   which was blocking, and refuses to execute an uncommitted, unreviewed contract.
2. **Open BATCH-641950 to execute `EXP-ICEX-146ff5`.** Ranked second, and it is a real
   loss to decline: the deadlock is six goals deep and this is its declared exit.
   Rejected on §2 (b1)–(b4): the contract is uncommitted, its own P1 independent
   red-team precondition is undischarged and owned by another live batch, its write
   scope is already held, and this goal's record cannot be made to reference a second
   batch.
3. **Open a reduced "model repair note" batch.** Ranked third. Rejected on §3: every
   component is already committed across `DEC-20260805-bb162b`, `CORR-20260805-4b91ca`,
   and catalogue entries A1-2/A1-8. Restating committed records is not research and
   consumes an immutable batch identifier to do it.
4. **Decline on merit / declare the lane exhausted.** Ranked last and rejected outright.
   `docs/inventor-protocol.md` §4 treats premature closure as symmetric with
   overclaiming; §5 records that the algebra reproduces; nothing here supports closure of
   anything. Note also that `ideas/catalogue-20260805/SCREENING.md`'s 0/102 survival
   rate **may not** be cited against this lane: `CALIBRATION.md` records that the lens
   calibration control **did not run**, that its reported verdict is **retracted**, and
   that "0/102 still may not be cited as a finding about the catalogue."

**Remaining uncertainty.**

- Whether the `GATE-B` re-partition of `CORR-20260805-4b91ca` D4 is a legitimate
  pre-observation protocol decision or a relaxation. The contract declares it, argues it,
  and routes it to `TASK-20260806-7e7ce3` to adjudicate. **I do not adjudicate it here**
  and this record must not be cited as approving it.
- Whether `HEUR-AT-4` — that the conservation count already contains the sign
  multiplicity, so `DEC-20260802-a51c82`'s `2(1−1/W_eff)` must not be applied on top —
  is right. `CTRL-PARAM` is the control that can refute it. Separately unresolved:
  `IDEA-20260803-ff7415` (`status: proposed`, `question_id: RQ-MONO-001`,
  `class: measurement`) exists to decide whether the `2^{n−1}` compounding is a real
  lever or a double count, and its owning goal `GOAL-MONO-001` is paused at exhausted
  budget. `CORR-20260805-4b91ca` D1's repair names it as a blocking dependency.
- Whether the `B`-independence of `D_trial` (§5) invalidates any window row.
- Whether `GOAL-ECDLP-001` may carry an `RQ-ICEX-001` hypothesis and experiment at all,
  given `DEC-20260805-bb162b`'s finding that it does not list that question, and whether
  `EXP-ICEX-146ff5` satisfies that decline's revisit condition R-D. That is P3, it is
  `BATCH-9c41dd`'s ledger decision to make (`DEC-20260806-8f7e4f`), and this record
  neither answers nor pre-empts it.
- Whether any primary source for the extension-field exponent is obtainable from any
  environment this program can reach. I searched: `inputs/` holds no such source, and no
  `knowledge/` record carries the exponent with a transcribed excerpt. The only
  in-repository statement is the agent-written secondary note the contract itself
  disqualifies. `GATE-B` should be expected to stay UNRUN indefinitely.

**Concrete successor / revisit condition.** See §7. This pause names one.

---

## 7. Resume action — concrete, and owned

**GOAL-ICEX-001 becomes eligible to open a batch on this lane when ALL of the following
are true against committed state, and not before:**

- **R-1.** `BATCH-9c41dd`'s snapshot archive `TASK-20260806-fb85f5` has committed
  `ledger/hypotheses/H-ICEX-9e54c2.yaml` and `experiments/EXP-ICEX-146ff5/specification.yaml`,
  and the dispatcher's post-commit verifier has accepted that commit.
- **R-2.** The independent red-team pass `TASK-20260806-7e7ce3` has returned, discharging
  precondition **P1**, with an explicit verdict on (i) the `GATE-B` re-partition of D4,
  (ii) whether every `GATE-A` arm and every control is capable of failing, and (iii) the
  omitted cost terms — to which the two in §5 (`B`-dependent `D_trial`; the
  `Θ((B/m)·ln B)` coupon-collector floor) should be added.
- **R-3.** `BATCH-9c41dd`'s ledger archive `TASK-20260806-636e61` has committed
  `DEC-20260806-8f7e4f` and `EV-ICEX-2be32e`, adjudicating **P3** — whether the extended
  contract satisfies `DEC-20260805-bb162b`'s revisit condition R-D and which goal owns
  the `RQ-ICEX-001` binding.
- **R-4.** A session with write access to `ledger/goals/GOAL-ICEX-001.yaml` and
  `ledger/decisions/` issues the **separate Coordinator ledger authorization**
  `EV-ICEX-001` requires, amending `next_action` from "remain non-executing" to a single
  bounded next action naming the committed contract. **This task cannot do it** — it may
  not edit the goal record or write a decision record — and a `SCOPE-DECISION.md` is not
  a substitute. §1's answer to P2 is the input to that authorization, not the
  authorization itself.

**If R-2 returns adverse**, the resume action is the repair the red team names, applied
by one versioned `protocol_amendment` that is itself snapshot-committed and
independently re-reviewed — never in flight, per the contract's own P1.

**Independently of R-1…R-4**, and requiring none of them: `IDEA-20260803-ff7415` remains
the cheapest way to retire the largest open scope question attached to this goal's
mandatory read. It is `proposed` and unadjudicated under `RQ-MONO-001`, and
`GOAL-MONO-001` needs a fresh budget grant to take it. That routing is `GOAL-PATH-001`'s
(`GOAL-ICEX-001.parent_goal_id`), not mine.

---

## 8. Identifier and archival hygiene

**Unconsumed identifiers.** The following four were pre-allocated to BATCH-641950 and are
**consumed by no record**. No `TASK-*` handoff, task card, dispatch-queue entry, archive
receipt, or artifact of any kind exists for any of them, and none is referenced anywhere
in this repository:

`TASK-20260806-50d12c`, `TASK-20260806-458d93`, `TASK-20260806-ad6c1d`,
`TASK-20260806-cb9ec1`.

Per `AGENTS.md` rule 14 identifiers are never reused. A future GOAL-ICEX-001 batch should
mint its own with `python3 tools/allocate_id.py --next task --date <YYYYMMDD>` and
`--check` before use rather than adopting these — they were drawn against a
BATCH-641950 execution intent that this record declines. `BATCH-641950` itself is
consumed by this file alone and by no queue.

**No queue and no handoffs were written.** Writing them would assert an authorization
this record does not give.

**Records untouched.** `ledger/goals/GOAL-ICEX-001.yaml` is not edited: it keeps
`current_batch_id: BATCH-001`, keeps its `dispatch_queue_path`, keeps `status: active`,
and keeps its single `next_action` unchanged. No hypothesis, evidence, decision,
correction, proposal, experiment, or knowledge record is created or modified by this
task. `H-ICEX-9e54c2` stays `specified`; `EXP-ICEX-146ff5` stays `approved` with
`execution_authorization.granted: false`.

**Archival ownership of this file.** This is a coordination record, not evidence. It
carries no archive receipt and asserts no commit, sha, hash, or review verdict. No git
command was run by this session. Its promotion to `ledger/decisions/DEC-20260806-<tok>.yaml`
— token minted by `tools/allocate_id.py` and `--check`ed, which this session cannot do
(no shell) and must not fabricate — is owed to the next ledger archive of GOAL-ICEX-001
or its parent. Until then this decision is durable as a reviewable coordination artifact
and is **not** an official ledger transition.

**Branch note.** `AGENTS.md` requires fetching `origin/main` and merging it into open
branches before an archival commit. This session has no shell and ran no
`git fetch`/`merge`; no base commit is recorded and none is claimed. Since no commit is
made by this task, no sync obligation is discharged or asserted.

---

## 9. Discrepancies between the dispatching brief and the committed records

Recorded because the record wins.

1. **"Nobody has picked it up."** Contradicted by working-tree state: `H-ICEX-9e54c2`,
   `EXP-ICEX-146ff5`, and live `BATCH-9c41dd` (§0). Correct in the narrow sense that
   none of it is committed.
2. **A1-8 numbers.** The brief cites "9.0× at m=4, B=2^52". Committed `A1-8` states "At
   `B ≈ 2^42` and `m = 4` that is a factor `≈ 7`." Both satisfy `ln B/m`
   (42·ln2/4 = 7.28; 52·ln2/4 = 9.01), but `2^52` is not the committed parameter point.
   The record's value stands.
3. **"A1-8, which the dispatching session independently verified."** No committed
   artifact records that verification. `SCREENING.md` places A1-8 in the `REPAIRABLE`
   tier with its own repair, including "fix the rank `B−1` off-by-one", and records
   slice A1 at 0/13 `PASS`. I re-derived the log-cofactor consequence myself and affirm
   it on that basis, labelled as my own derivation (§5).
4. **"A1-1/A1-2/A1-3/A1-8 raise four more [defects]."** Overstated. Only **A1-2** and
   **A1-8** are audits of `fa9839`. **A1-3** *repairs* one of its stated confounders in
   its favour (arguing descent is identically zero). **A1-1** answers `HEUR-AT-3`'s
   forward question and is a successor claim, not a defect. Separately, `SCREENING.md`
   §5 Mode 3 records **A1-13**'s headline claim as **false under its own model**, which
   the brief does not mention.
5. **`D_trial` described as "the per-trial descent cost".** In `IDEA-20260803-fa9839`
   `D_trial` is the per-trial *decomposition-decision* cost; descent is a separate,
   explicitly omitted stage (`confounders[0]`). The distinction is load-bearing —
   `EXP-ICEX-146ff5` charges them separately as `C_rel` and `C_desc`, and A1-3 is
   entirely about the descent stage.
6. **"untouched for ~5 days."** `GOAL-ICEX-001.updated_at` is `2026-07-31T12:35:00-07:00`
   — six days. Related record-hygiene observation, reported not fixed: the goal's
   `next_action` and `campaign_budget` both carry 2026-08-02 amendments while
   `updated_at` still reads 2026-07-31.
7. **Confirmed, no discrepancy:** the `maximum_batches` removal is recorded verbatim in
   the goal as an explicit user direction of 2026-08-02 and is not a Coordinator
   self-grant; `DEC-20260805-bb162b` is a routing decline that found the core algebra
   correct; `CORR-20260805-4b91ca` records D1–D4 against `fa9839`; the
   `DEC-20260802-a51c82` mandatory read does bind the `N = q^n, m = n` family the
   baseline gate uses.

---

```yaml
coordinator_decision:
  id: DEC-20260806-PENDING          # ledger/decisions/DEC-20260806-<tok>.yaml, owed to the
                                    # next ledger archive of GOAL-ICEX-001 or GOAL-PATH-001.
                                    # NOT minted here: this session has no shell, cannot run
                                    # tools/allocate_id.py --check, and will not fabricate an
                                    # identifier (AGENTS.md rules 9 and 14).
  recorded_at: '2026-08-06'
  decided_by: coordinator
  goal_id: GOAL-ICEX-001
  question_id: RQ-ICEX-001
  subject: IDEA-20260803-fa9839
  proposed_batch_id: BATCH-641950
  decision: pause
  disposition: pause_batch_not_opened_sequencing_behind_BATCH-9c41dd
  pause_condition_fired: >-
    "Prerequisites remain without auditable next action beyond campaign budget."
    Limb (a) holds - no charged SDEG/MONO/RELN measurement package exists and
    GOAL-MONO-001 is paused at exhausted budget (DEC-20260802-a51c82 N-2). Limb (b)
    holds for THIS GOAL - the one candidate action, executing EXP-ICEX-146ff5, is
    blocked because the contract is uncommitted, its own P1 independent red-team
    precondition is undischarged and owned by live BATCH-9c41dd, its write scope is
    already held by that batch, and this task may not edit the goal record to
    reference a second batch.
  pause_conditions_not_fired:
  - '"User requests pause." - no user request is on this record.'
  - >-
    '"Archive verification fails." - no archive was attempted; nothing was staged,
    committed or verified. Untouched, not passed.'
  rationale: >-
    Sequencing pause, not a merit decline and not a closure. On its words the goal's
    prohibition covers this batch - not via "measurement", which does not naturally
    cover a zero-compute derivation, but via the operative clause "remain
    non-executing" and via EV-ICEX-001's unmet second precondition, "a separate
    Coordinator ledger authorization is issued", which this task cannot issue.
    Independently, the routed proposal HAS been picked up: BATCH-9c41dd under
    GOAL-ECDLP-001 specified H-ICEX-9e54c2 and approved EXP-ICEX-146ff5 on 2026-08-06,
    with execution_authorization.granted false and three open preconditions, of which
    P2 is addressed to this Coordinator by name. P2 is answered on this record. No
    batch may execute that contract today because it is uncommitted, its independent
    red-team pass has not run, and its write scope is held by a live batch. The
    contract's design-time window rationals were independently re-derived here and
    reproduce exactly - recorded so this pause is not read as doubt about the lane.
  evidence_refs:
  - ledger/goals/GOAL-ICEX-001.yaml
  - ledger/evidence/EV-ICEX-001.yaml
  - ledger/decisions/DEC-20260731-015.yaml
  - ledger/decisions/DEC-20260802-a51c82.yaml
  - ledger/decisions/DEC-20260805-bb162b.yaml
  - ledger/corrections/CORR-20260805-4b91ca.yaml
  - ledger/proposals/IDEA-20260803-fa9839.yaml
  - ledger/proposals/IDEA-20260803-ff7415.yaml
  - ledger/hypotheses/H-ICEX-9e54c2.yaml
  - experiments/EXP-ICEX-146ff5/specification.yaml
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/dispatch_queue.json
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-156658/SCOPE-DECISION.md
  - knowledge/findings/KN-FIND-007.md
  - knowledge/open-problems/KN-OPEN-001.md
  - ideas/catalogue-20260805/A1-index-calculus.md
  - ideas/catalogue-20260805/SCREENING.md
  - ideas/catalogue-20260805/CALIBRATION.md
  status_changes: []
  hypothesis_status_changes: []
  experiment_approvals: []
  goal_status_change: none
  claim_ceiling: toy
  knowledge_promotion:
    promoted: []
    not_warranted: >-
      No experiment ran, no run record exists, and no evidence record was produced. A
      sequencing pause is neither support nor reject_scoped and rests on no
      replicated or strong evidence, so it promotes no KN-FIND. The two contract
      defects recorded in section 5 are review findings routed to
      TASK-20260806-7e7ce3, not corpus entries; they become promotable only if a run
      adjudicates them.
  dominated_by: >-
    Not applicable as an attack - no algorithm is proposed and no Pareto point is
    claimed. Written explicitly rather than left null.
  sota_delta: >-
    Zero on every ECDLP cost axis. Pollard rho at c_rho*sqrt(N) remains the baseline;
    no attack, no measurement, no exponent moved, no deployed system affected.
  next_actions:
  - >-
    DO NOT open BATCH-641950. GOAL-ICEX-001 remains active and non-executing under its
    own unchanged next_action, at current_batch_id BATCH-001, with zero budget
    consumed and its single next action preserved.
  - >-
    ANSWER TO EXP-ICEX-146ff5 PRECONDITION P2, RECORDED: GOAL-ICEX-001's deferral is
    on MEASUREMENT and does not by itself bar a zero-compute derivation. It is
    nevertheless barred today by the separate "remain non-executing" clause and by
    EV-ICEX-001's requirement of a separate Coordinator ledger authorization, which
    does not exist and which this task cannot issue.
  - >-
    LET BATCH-9c41dd FINISH. Its snapshot archive TASK-20260806-fb85f5, independent
    red-team pass TASK-20260806-7e7ce3, and ledger archive TASK-20260806-636e61 are
    the auditable next actions on this lane, and they are not this goal's to run.
  - >-
    CARRY TWO ADDITIONAL DEFECTS TO TASK-20260806-7e7ce3 - (i) D_trial is charged
    independent of B while catalogue entry A1-2 supplies a universal achievable
    D_trial = B^ceil(m/2) that is a function of B, and no GATE-A arm exercises a
    B-dependent D; (ii) C_rel charges B relations while A1-8's coupon-collector floor
    is Theta((B/m)*ln B) - a LOG-COFACTOR correction that does NOT move the window
    boundary and must never be presented as exponent movement.
  - >-
    RESUME CONDITION R-1..R-4 (section 7): committed snapshot of the contract;
    discharged P1 red-team pass; committed DEC-20260806-8f7e4f / EV-ICEX-2be32e
    adjudicating P3 and R-D; and a separate Coordinator ledger authorization amending
    GOAL-ICEX-001.next_action to one bounded action naming the committed contract.
  - >-
    Promote this decision to ledger/decisions/DEC-20260806-<tok>.yaml at the next
    ledger archive of GOAL-ICEX-001 or GOAL-PATH-001, minting the token with
    tools/allocate_id.py and --check. Until then it is a coordination record and not
    an official transition.
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; per-role policy selection under this runtime
      is process-level. Recorded, never silently substituted (AGENTS.md rule 11).
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session; no
      `python3 -m orchestration.adapter doctor --probe` was run.
    independent_session: false
```
