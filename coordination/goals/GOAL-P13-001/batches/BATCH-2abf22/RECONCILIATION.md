# BATCH-2abf22 — GOAL-P13-001 goal-head reconciliation

*(Directory name `BATCH-2abf22` is the minted batch ID. It, `TASK-20260810-5481f4`,
`DEC-20260810-205656` and `EV-WESO-d1a9d8` were all minted and `--check`ed free by
the orchestrating session before this task started. The Coordinator that executed
this batch has no shell, minted nothing, and used exactly those four identifiers.)*

## What this batch was asked to do

Execute steps 2 and 3 of the "Recommendation" in
`coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/SCOPE-DECISION.md` — the
dedicated reconciliation-and-repair action that the design gate explicitly
declined to perform itself, and that its own finding requires before any further
batch is opened against `GOAL-P13-001`.

Step 1 of that recommendation (verify durability in git) was **not** performed
here. The coordinator role has no `run_commands`, so the orchestrating session
discharged it and supplied its findings verbatim in
`ledger/handoffs/TASK-20260810-5481f4.yaml`. Every git fact used below is that
session's, at `origin/main = 3cc95d80ddec1c2fb401ef817e76045c6e1ace78`, and is
cited as such. **No record authored in this batch presents a git fact as its own
inspection.**

## The answer to step 1, and why it decided the shape of steps 2–3

The work is durable: the executor snapshot
`b7b3240b4266b85af1e0810831a66aa6e3300535`, the contract-freeze snapshot
`91b5428b1`, both review commits `49b4814c0`, and the commit that introduced all
four defective archive records `133f7d47b93b96ce0a3ffc3f4a38b92ae794fd68` are all
reachable from `origin/main` and pushed.

Therefore the branch that applies is **"author a proper superseding archive"**, not
"re-run the measurement". Redispatching NC2d-PROPER, NC2b-SLOPE or the
bibliographic subtask would duplicate already-executed, already
independently-reviewed science. Durability says nothing about correctness: the
seven defects are content defects and are untouched by reachability.

One refinement matters and is carried into every record: `TASK-20260804-7cb2d2`
**did** execute — its snapshot commit exists and names it in its subject — so its
defect is a missing receipt and a missing queue advance, *not* missing work. No
record here says that archive never happened.

## What was authored

| Path | Kind | Note |
| --- | --- | --- |
| `ledger/decisions/DEC-20260810-205656.yaml` | new | `decision: supersede`; supersedes `DEC-20260804-e19a65` |
| `ledger/evidence/EV-WESO-d1a9d8.yaml` | new | supersedes `EV-WESO-b6ceff` |
| `ledger/hypotheses/H-WESO-001.yaml` | append | one status_history entry, `transition: none`; refs appended |
| `ledger/goals/GOAL-P13-001.yaml` | targeted edits | checkpoints, head, budget accounting, `status: paused`, one `next_action` |
| `coordination/goals/GOAL-P13-001/batches/BATCH-2abf22/batch.yaml` | new | batch record |
| `coordination/goals/GOAL-P13-001/batches/BATCH-2abf22/RECONCILIATION.md` | new | this file |
| `coordination/goals/GOAL-P13-001/batches/BATCH-2abf22/tasks/TASK-20260810-5481f4/receipt.json` | new | task receipt |

Nothing outside that list was written. `DEC-20260804-e19a65.yaml`,
`EV-WESO-b6ceff.yaml`, `KN-FIND-4e7a92.md` and `KN-FIND-d1c853.md` are
byte-unmodified and were opened read-only.

## The seven defects and what was actually done about each

**D-1 — no receipts for BATCH-403f13's own archive tasks.** Refined (7cb2d2's
snapshot exists and names the task; what is missing is its receipt and queue
advance) and then recorded as unrepairable in place. Writing a receipt today for a
2026-08-04 commit would be back-dating a verification this Coordinator did not
perform, and `BATCH-403f13/archives/` is outside write scope. The authoritative
disposition of that batch is now `DEC-20260810-205656` plus `EV-WESO-d1a9d8`,
archived under `TASK-20260810-a291c2`.

**D-2 — `decision: support_scoped`, outside the template vocabulary.** Corrected by
replacement: this decision uses `supersede`, and its `decision_note` states why
`support`, `revise`, `weaken`/`reject_scoped` and `pause` were each rejected. The
out-of-vocabulary value was not a cosmetic slip — it encoded a "support, scoped"
claim the promotion gates forbid for this hypothesis, so fixing the vocabulary and
withdrawing the claim are one act. (The 2026-08-08 schema-supersession sweep did
**not** fix this: its v2 file still reads `support_scoped`.)

**D-3 — the narrated hypothesis transition was never applied.** The narration is
withdrawn as unsupported and the real entry is now written: one appended
`status_history` entry citing `DEC-20260810-205656`, `transition: none`, status
still `analyzed`. Nothing is reversed, because nothing had been applied.

**D-4 — the goal record was never advanced.** Corrected here: a `BATCH-403f13`
checkpoint (plus compact checkpoints for `BATCH-8e1671` and `BATCH-2abf22` so no
batch is silently omitted), `current_batch_id` → `BATCH-2abf22` with a
`dispatch_queue_path` that exists on disk, `batches_consumed` 3 → 4,
`batches_remaining` → `null` with its reason, `last_decision` advanced,
`status: paused`, and exactly one `next_action`. Prior text is preserved: the
superseded `next_action` is retained verbatim under a renamed key, and the prior
`status_note` and `dispatch_queue_path_note` are left unedited beside new dated
notes.

**D-5 — the shipped KN-FIND content matches neither its pre-registration nor the
cited run.** Resolved explicitly as **WITHDRAWN-PENDING** — see below.

**D-6 — no handoff records for any BATCH-403f13 task; an untraceable producer.**
Partly refined, partly permanent, corrected going forward. Refinement, from this
Coordinator's own read of `BATCH-403f13/dispatch_queue.json`: full inline `handoff`
envelopes **do** exist there for `7cb2d2`, `241b87`, `6519fa` and `bf4dce`, so
those tasks are authorized by a committed coordination record even though none was
persisted under `ledger/handoffs/`. The Validator and Red Team appear in that queue
only as `TBD-validator` / `TBD-red-team`. `TASK-20260804-eacb99`, which
`EV-WESO-b6ceff` names as its own producer, appears **nowhere** — and that cannot
be repaired now, because writing a handoff record today for a task claimed to have
run on 2026-08-04 would be a fabrication. It is recorded as a permanent provenance
gap and is one of the reasons that evidence record is superseded rather than
relied upon. Going forward, `EV-WESO-d1a9d8` is recorded by a task that has both a
committed handoff and a task card.

**D-7 — item (4) is genuinely open.** Recorded as open and made the goal's single
resume condition. Its one dispatch returned "Executor subagent returned empty
result"; under AGENTS.md core rule 5 that is an infrastructure outcome and **not**
evidence about Heuristic 1 in either direction. No inference of any kind is drawn
from it anywhere in this batch — including the convenient inference that would
have made closing the goal easier.

## The KN-FIND disposition, stated rather than left silent

`KN-FIND-4e7a92` and `KN-FIND-d1c853` are recorded **WITHDRAWN-PENDING**. Both
files remain in the corpus, unedited and undeleted — they are immutable and outside
every write scope in this batch. What changes is their *standing*: they may not be
cited as this programme's promoted knowledge, and no downstream record may treat
their formulas as carrying the `derivation` proof status they declare.

Four grounds, all checkable against committed artifacts:

1. **Content mismatch with a binding pre-registration.** `DEC-20260802-48c72c`
   fixed the promotable content in advance (the estimator lemma and pairing rule,
   `proof_status: derivation`, explicitly "NOT any c value"), and the same
   obligation is restated in `H-WESO-001.knowledge_promotion` and in
   `BATCH-403f13/dispatch_queue.json`'s `kn_find_requirement`. Neither shipped
   entry promotes that claim.
2. **Provenance not established.** Neither formula, nor the terms `phi(ell)`,
   `C_walk` or `N_pairs`, appears in either run's raw result or manifest, in the
   validation report, or in the red-team report — all of which describe an
   alpha-exponent p-scaling regression and a slope-recovery check. The entries name
   `EV-WESO-b6ceff` as their source evidence, and that record contains neither
   formula.
3. **Internal inconsistency with the artifact the entry itself cites.**
   `KN-FIND-4e7a92` defines `phi(ell) = ell − 1` as "the number of distinct roots
   of `Phi_ell` … in the supersingular case"; the red-team report it is downstream
   of records `entries = ell+1` for exactly this setting, confirmed against
   `raw-result.json`'s `n_distinct_roots = ell+1 or ell+2`.
4. **A restatement of Heuristic 1 that does not match the hypothesis record.**
   `KN-FIND-d1c853` treats `H_1` as a constant and `P_0` as `B_opt^{-1}`;
   `H-WESO-001` states Heuristic 1 as a smoothness probability `u^{-u(1+o(1))}`
   with `u = log(p/2)/(3 log B)`. Its offered cross-check cites an `EV-WESO-001`
   observation about the reproduction of five concrete (time, memory) pairs, which
   bears on the paper's cost table and not on a pairing rule.

**Grounds 3 and 4 are provenance and consistency findings, not mathematical
adjudications.** This batch does not rule either formula false; it records that
their stated basis contradicts the committed artifacts they rest on.

Why not simply supersede them with correct entries: `knowledge/findings/` and
`knowledge/INDEX.md` are outside both BATCH-2abf22 write scopes, and
`/curate-knowledge` requires the entry and the regenerated index in the *same*
ledger archive commit. Writing outside the declared scope would be a
scope-expanding commit. So the scheduled KN-FIND is re-declared as a binding
deliverable of the next `GOAL-P13-001` ledger archive, with its content unchanged
from `DEC-20260802-48c72c`.

The count, stated exactly: **four** consecutive archives have now failed to ship
the scheduled entry, and the causes are not identical. BATCH-002's, BATCH-003's and
BATCH-2abf22's archive cards omitted `knowledge/findings/` and
`knowledge/INDEX.md` from write scope — the same scoping defect three times.
BATCH-403f13's card *did* carry both paths and *did* ship two entries; its failure
is the content, which is worse and is what the WITHDRAWN-PENDING verdict addresses.

## The terminal status, and why `paused` rather than `closed_at_budget`

**`paused`.**

`closed_at_budget` would name a cause that did not occur. `maximum_batches` is
`null` — the cap of 4 was removed on the user's explicit direction of 2026-08-02
and is recorded as *superseded, not consumed* — so there is no batch cap to
exhaust. On wall clock, the goal's authorized total is 21600 s and the executed
measurement runs consume of the order of 1230 s of it (396 s + 791.751 s +
42.0 s), under six per cent. The actual causes of stopping are a **method ceiling**
on the c-calibration lane (recorded by `DEC-20260802-48c72c`: `gamma = exponent(M)
− 1`, `M` at most schoolbook, residual width dominated by the unimplemented L4) and
an **unmet infrastructure capability** for the one substantive open item. `paused`
also correctly signals that exactly one named, frozen, ready protocol remains.

`completed` is barred by the goal's own `closure_requirements` while completion
criterion 1 is unmet, and `DEC-20260802-48c72c` assessed criterion 1 as unmet *and*
unreachable by this method within the remaining budget. The suspension of the
three-model closure quorum does not change that: it lifts a procedural gate, not
the substantive requirement that a declared criterion was actually met. **No
attestation was obtained and none is recorded; no `completion_quorum` block is
written.**

Criterion 2 is **not** asserted met either. It requires a Coordinator evidence
record, decision and hypothesis-status update committed through a *verified* ledger
archive; the archive carrying this transition is unverified at the time of writing.

CLAUDE.md rule 8's prohibition on understating a goal is not engaged: criterion 1
is genuinely unmet on the numbers, so there is no met criterion being hidden behind
a weaker status.

## What was refused

- **No hypothesis promotion.** `H-WESO-001` stays `analyzed`. Gates 1–4 are
  unsatisfied by committed artifacts and gate 4 is unsatisfiable in this harness.
  Retiring a label at one ell range narrows a qualification; it is not evidence for
  an asymptotic claim.
- **No inference from the item-(4) infrastructure failure**, in either direction.
- **No new number.** Every value in `EV-WESO-d1a9d8` is restated from a committed
  artifact and attributed to it. This Coordinator recomputed nothing.
- **No c-table, bracket or margin update.** All eight mandatory attachments and all
  twelve standing prohibitions of `DEC-20260802-48c72c` remain in force; SP-10 in
  particular is *not* lifted by NC2d-PROPER.
- **No forward pointers** written into the superseded records: that corpus-wide
  policy is unsettled, so the reference direction is new-cites-old only.
- **No edit to any `adjudicated_positions` text** in `H-WESO-001`. The scoped
  retirement lives in the new decision and evidence records; older position text is
  retained verbatim.
- **No narrated experiment-status transition that this decision cannot apply.**
  `EXP-P13-NC2d` and `EXP-P13-NC2b` are `analyzed` in substance, but their frozen
  `specification.yaml` files read `status: approved`, are outside write scope, and
  must not be edited after their snapshot. Writing "approved → analyzed" into the
  decision while leaving those files untouched would reproduce defect D-3 in the
  act of correcting it, so the decision records `transition: none` and names the
  discrepancy instead. The same latent discrepancy already exists from
  `DEC-20260802-48c72c` for `EXP-PEC-49c773`; it is recorded, not repaired —
  repairing it would mean editing a frozen contract.
- **No commit.** This role writes files only.

## What makes this official

Nothing here is official until `TASK-20260810-a291c2` commits the declared paths,
records a real `commit_sha`, `parent_sha` and non-empty `path_sha256` map, pushes
the branch, and opens or refreshes a PR against `main` naming
`DEC-20260810-205656`, `EV-WESO-d1a9d8`, `H-WESO-001`, `GOAL-P13-001`,
`TASK-20260810-5481f4` and `TASK-20260810-a291c2`. Until then this is a
working-tree artifact and `GOAL-P13-001` is, as a matter of committed fact,
whatever `main` says it is.
