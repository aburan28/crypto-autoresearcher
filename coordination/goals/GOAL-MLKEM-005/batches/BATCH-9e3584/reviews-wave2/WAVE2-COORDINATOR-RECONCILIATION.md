# Wave-2 Coordinator reconciliation — BATCH-9e3584

Recorded 2026-08-12. Goal `GOAL-MLKEM-005`, batch `BATCH-9e3584`.
Ledger records written alongside this note: `ledger/evidence/EV-MLKEM-e45478.yaml`,
`ledger/decisions/DEC-20260812-15d3b2.yaml`.

**What this instrument is.** A batch-level narrative of a concurrency collision and of
the second independent review wave that ran into it. The binding acts are the two ledger
records above; this file is the account a later reader needs in order to overturn them.
**Claim tier stays TOY**: nothing in BATCH-9e3584 bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. AM-10 through AM-14 of
`DEC-20260808-05b684` and their binding carries are in force and are not re-litigated.
**AM-3 is not retired. BATCH-a44d08 is not rescored in any respect.** No producer outcome
row is adjudicated here.

---

## 0. Provenance of every fact below

This distinction is kept deliberately and for a specific reason: BATCH-cbe023 produced a
Coordinator claim about the git record that a Validator then proved false, and the
2026-08-11 adjudication was written to avoid repeating it. This note holds the same line.

**Read by me in this worktree, so mine to assert:** both wave-2 review reports in full;
`COORDINATOR-ADJUDICATION-20260811.md`; `dispatch_queue_continuation.json`;
`ledger/goals/GOAL-MLKEM-005.yaml`; `ledger/evidence/EV-MLKEM-9b8f7f.yaml`;
`templates/research-records.md`; `AGENTS.md`; `CLAUDE.md`; `agents/coordinator.md`;
`.gitignore`. I also directory-listed the whole `BATCH-9e3584` tree, which is where the
file counts in section 2 come from.

**Attributed to the dispatching (parent) session, which ran git plumbing:** the state of
`origin/claude/ml-kem-solution-ckdxmg` — its tip `86ac7f72e`, its archive commit
`5004932a9`, its contents, its five `completed` task states, and the fact that it is
pushed and not merged into `origin/main`; the fact that
`origin/claude/ml-kem-solution-ckdxmg` has **zero** files under `reviews-wave2/`; the
`allocate_id.py --check` results for the four fresh identifiers; and the relocation of
the two uncommitted review directories.

**Attributed to one or both wave-2 reviewers, who each ran git plumbing in their own
sessions:** the three-way commit split, the 30-for-30 content match, the D3 table, the
notarization chain in both directions, the archive-commit-message facts, and every
producer-artifact measurement.

**I hold no shell.** I ran no git command, no producer code and no probe, and I do not
narrate any of them into checks of my own.

---

## 1. What collided

The continuation queue in this worktree listed `TASK-20260809-3f1dc4` (validator) and
`TASK-20260809-444fe7` (red team) as `queued`, with a `queued_note` reading "NOT RUN" and
a batch `independence_note` stating that no producer had run and no review verdict
existed anywhere in the batch. Both cards were dispatched into fresh independent sessions
at `review-adversarial`. Both returned.

The wave-2 Validator then found, and the parent session independently confirmed with git
plumbing, that **the same two cards had already been executed on an unmerged branch**:

| on `origin/claude/ml-kem-solution-ckdxmg` | state |
| --- | --- |
| `.../reviews/TASK-20260809-3f1dc4/validation_report.yaml` | a **different** file, committed at `5004932a9` |
| `.../reviews/TASK-20260809-444fe7/red_team_report.md` + 21 probes | **different** files, same commit |
| `ledger/evidence/EV-MLKEM-9346bb.yaml` | exists there, not on `main` |
| `ledger/decisions/DEC-20260809-afe29b.yaml` | exists there, not on `main` — `decision: revise`, "R-OUT-1 STANDS", amends the instrument via AM-15/AM-16, claim tier toy |
| `knowledge/findings/KN-FIND-2a35aa.md` | exists there, not on `main` |
| its copy of the continuation queue | all five tasks `completed` |

So one producer snapshot now carries two complete, independent review waves, and on merge
will carry two evidence records and two Coordinator decisions.

### The mechanism, and it is two defects rather than one

**Primary: a reserved identifier in a shared mutable coordination record is a
single-writer resource handed to every worker that reads it.** `EV-MLKEM-9346bb` and
`DEC-20260809-afe29b` were minted **once**, correctly and randomly, on 2026-08-09, and
written into `TASK-20260809-60f9cc`'s `artifact_paths` and `archive.record_ids` because
`tools/research_dispatch.py` refuses to plan a ledger archive that owns no path under
`ledger/evidence/` and `ledger/decisions/`. From that moment they were not free
identifiers awaiting allocation — they were an **instruction**, and every branch
inheriting the queue inherited it. AGENTS.md rule 14's random tokens prevent two workers
from *independently minting* the same id. They do nothing about two workers *correctly
executing the same reservation*. That is a structural gap in the concurrency model, not a
mistake by either session.

**Compounding: `tools/allocate_id.py --check` answers from the working tree only.** It
reported both reserved identifiers **FREE** here, because the union it scans is this
worktree and it never consults other refs. The one mechanical guard a Coordinator would
reach for actively confirmed the wrong answer. The wave-2 Validator names both halves in
its finding F-7 and I adopt its account.

**What this is not.** Not a random-token collision, not a `max+1` allocation, not an
invented identifier, and not a failure of either wave-2 reviewer — both did exactly what
their cards required. Nor is it a defect of the concurrent branch: the wave-2 Validator
reports checking that branch's ledger archive and finding it **conforming on its own
terms**, its declared set of 27 paths equalling its commit's change set exactly, 0 extra
and 0 missing. Two correct executions of one instruction produced two correct records.

---

## 2. What I checked, and what I found

### 2.1 The reviews are genuinely independent of the other chain

This is the property that makes the second wave worth keeping, and it is fragile.

- The wave-2 Validator states it discovered the other chain **only at the end**, while
  re-checking its own dependency's ancestry, that its verification was complete before
  the discovery, and that **it did not open the other validation report** — it read only
  the blob's git metadata (commit, date, blob id, size). Its stated reason: "Two
  independent validations of one snapshot are worth more than one validation and a
  comparison, and the value of the second is exactly that it was formed without reference
  to the first."
- The wave-2 Red Team's report shows no awareness of the other chain at all.
- The parent session states it did not read the other branch's report bodies before these
  reviews ran.
- **I have not read them either**, and I have deliberately not compared the two waves.

### 2.2 The relocation, and the stale path declarations inside the reports

The parent session relocated the two uncommitted review directories, before any commit,
to fresh task slots:

| the reports internally declare | the bytes actually live at |
| --- | --- |
| `.../BATCH-9e3584/reviews/TASK-20260809-3f1dc4/validation_report.yaml` | `.../BATCH-9e3584/reviews-wave2/TASK-20260812-da8c3b/validation_report.yaml` |
| `.../BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md` + `probes/` | `.../BATCH-9e3584/reviews-wave2/TASK-20260812-aadafd/red_team_report.md` + `probes/` |

By my own directory listing, the wave-2 tree holds **30 paths**: one validation report,
one red-team report, and 28 probe files (7 probes × `{.py, .json, .stdout.log,
.stderr.log}`). The seven `.stderr.log` files are empty, and their emptiness is itself
the record that no probe wrote to stderr; the red team's report says so and they must be
committed rather than omitted.

**The reports' own text is not rewritten, and that is the point rather than an
oversight.** The validation report carries `id: VAL-20260809-3f1dc4`; both reports declare
`artifact_paths` under the old directories; both name the cards they executed. All of that
is **true** — a duplicate execution of a card is what happened. Editing it to make the
record tidier would erase the single most useful thing this batch teaches. AGENTS.md rule
4 forbids it anyway: an immutable review artifact is not edited, and a conflict inside one
is resolved by a new record under a new id.

One thing I checked by reading, which neither reviewer could check about itself: **as
declared, `TASK-20260809-60f9cc` cannot commit this wave.** Its `artifact_paths` list four
paths and its `source_task_ids` are `[TASK-20260809-3f1dc4, TASK-20260809-444fe7]`, whose
`artifact_paths` point at two files that do not exist in this worktree. Its expected
binding set would therefore name two absent paths and omit all 30 present ones —
reproducing defect D3 exactly. Independently, that task id is already `completed` against
`5004932a9` on the other branch, so running it here would be a *third* instance of the
same collision.

### 2.3 One stray file, checked and benign

`.../tasks/TASK-20260809-311784/__pycache__/measure_nullfam.cpython-311.pyc` exists
untracked inside a producer task directory — a by-product of the red team importing the
producer's committed module verbatim for its `n_fire` replication. `.gitignore` line 1 is
`__pycache__/`, which I read, so it is not a staging hazard. Recorded because it sits
inside a directory whose 28-file committed content is load-bearing, and a reader who finds
it should know it was checked rather than missed.

### 2.4 Both reviews confirmed the Coordinator's git claims, and the Red Team refined them

Both review cards required the reviewers to verify the 2026-08-11 adjudication's git
account **themselves** rather than accept it. Both did, in separate sessions, and both
report every checkable claim **true**: the three-way commit split (`1aa7db53` 2 paths,
`c034ef38` 28 paths, `502d15a0` 3 paths), the 30-for-30 content match — verified by both
against the blobs **at the declared commits** as well as the working tree, a stronger test
than the one claimed — and every row of the D3 table.

The Red Team **narrowed** the recorded defect in the Coordinator's favour, and this is the
part a later reader most needs:

1. **For both archive tasks, the receipt's own `path_sha256` set equals its commit's
   change set exactly.** So D3 is a defect of the **queue's** `artifact_paths`, not of the
   **receipts**. The adjudication's phrase "nine of the 28 declared producer artifact
   paths do not exist" is true of the queue and false of the receipt — and keeping the two
   apart matters, because a reader who bins the receipt as unreliable loses the only
   correct declaration of what was committed.
2. **Two of the adjudication's three UNKNOWNs resolve, both in its favour.** Both archive
   commit messages do contain their task id and `GOAL-MLKEM-005`, and both do record the
   base commit checked — in the commit message, as "Base checked: origin/main
   `3d5dd80a…`". The only surviving failure is the change-set equality test; the only
   surviving UNKNOWN is push/PR state.

### 2.5 What the wave measured that the batch did not contain

Recorded in full in `EV-MLKEM-e45478`; the headline items are:

- **Validator `passed`**, with seven findings, none of which moves a number, a threshold
  or a verdict. Material: **F-1**, the lead report's "a factor of 6 to 31" is **false at
  its lower end** — the true range is **4.87× to 31.03×**, and the value that breaks it,
  `0.486626`, is the exact number the frozen pre-registration works out as its own REL-2
  worked example. **F-2**, an **undeclared across-cell aggregation rule** (`G_REL_PASS`
  collapses across lattices and cells with an ANY rule) that selects an outcome row; the
  defect is the non-disclosure, since the reported outcome is correct under the frozen
  text's own "majority" language, and `X_null` passes under all three rules anyway.
- **Validator O-2: `G-VAR` is EVADABLE.** `X_null + 1e-9·A[0,0]/q` is *admitted* by G-VAR
  while passing REL1 10/10 and REL2 19/19. G-VAR as frozen is necessary but not
  sufficient.
- **Red Team RT-R1: a BUILT nearby family flips G-VAR from 38/38 to 0/38.** Changing one
  thing — `m_i[0] = q+i` — makes the determinant vary with the basis index, and both
  `rdet` and `X_null` are then admitted while still reading zero entries of `A`. **The
  proposed G-VAR repair is conditional on the frozen family.** The missing separator is
  named: dispersion *on the fibre of the family over the observable's own arguments*.
- **Red Team RT-R3: the "neither direction" refusal OVER-CLOSES.** Only the PASS side was
  shown vacuous; the gate's **refusal side is untested in either direction** and its
  false-refusal rate has never been measured. Premature closure is a failure mode
  symmetric with overclaiming.
- **Red Team RT-B1: `n_fire` replicated 8×** — 28, 37, 36, 32, 32, 29, 28, 35, mean
  **32.12 ± 3.60** — so the single reported 35 does not survive replication as stated. The
  *substantive* verdict does: no replicate comes within seven steps of the pre-registered
  PASS threshold. The Validator reached the same place independently with its own
  differently-seeded family.
- **Red Team RT-C1a / RT-C1b: two AM-14 observations reduce to controlled nulls.** The
  "4 of 10 ratios below 1" is the null expectation to two decimals (3.98 of 10); the
  "degenerate regime" is a property of the `S = 8, E = 4` design, under which the C2
  positive control tested only 6 of 10 targets.
- **Against the Red Team's own thesis:** Section C2's refusal of the "over-sensitive"
  reading is **corroborated** by the centered ladder it ran, which the producer had
  deliberately deferred.

**Infrastructure, recorded as infrastructure:** `fpylll` was **ABSENT in both sessions**,
so `lam1n` and `hkz` were **not** independently re-derived, and neither were the 48
reductions or the L7/L8 replication. That is a limit on this wave's coverage and is
**never** evidence against any of those quantities.

**Inference provenance, both sessions:** requested `review-adversarial`, resolved
`claude-opus-5`, `model_verified: false` (no adapter probe receipt is obtainable from
inside a subagent). Independence is **procedural and never model-level**; **AGENTS.md rule
12 is UNMET AND UNWAIVED**. Two review waves is two procedural samples of one model, not
two models.

---

## 3. What I ruled

Full text in `DEC-20260812-15d3b2`. In summary:

1. **The collision is a coordination failure, not an evidence failure.** Every byte is
   intact; both reviews ran to completion inside budget; the producer snapshot is
   content-verified by two more independent sessions. AGENTS.md distinguishes the dispatch
   queue from evidence, and that distinction decides this the same way it decided the
   2026-08-11 adjudication.
2. **This branch is ADDITIVE-ONLY. It adds files and modifies none.** In particular it
   does **not** touch `ledger/goals/GOAL-MLKEM-005.yaml`, which the concurrent branch's
   archive already edits. I considered editing it and refused; the cost — that the
   committed goal record will not name this wave until the merger applies the carried
   next action — is stated in the decision rather than hidden, and is smaller than an
   unresolvable conflict in the record that steers the campaign. It also does not touch
   `dispatch_queue_continuation.json` (the other branch rewrote it), does not run
   `tools/shard_goal.py`, and does not write or regenerate `knowledge/INDEX.md`.
3. **Nothing here rescores, supersedes, endorses or contradicts `EV-MLKEM-9346bb`,
   `DEC-20260809-afe29b` or `KN-FIND-2a35aa`.** They are not on `main`, I have not read
   them, and they are deliberately absent from this chain's `evidence_refs`: a record I
   have not read is not evidence for anything I decide. They are named throughout as
   objects to be **reconciled**, which is a different thing.
4. **`TASK-20260809-60f9cc` must never run on this branch**, on two independent grounds
   (already `completed` elsewhere; declared binding set unusable here). The wave-2 archive
   is a new task under a newly minted handoff id, owning exactly the 30 wave-2 paths plus
   the two ledger records, this note, and its own receipt.
5. **The comparison of the two waves is a new Coordinator decision under a new id, made
   after the merge by a session that has read both.** It supersedes by reference and edits
   nothing. It is the single most informative thing anyone can do with these two chains,
   and it is deliberately not attempted here — a Coordinator who has read only one wave
   cannot make it, and a wave 2 formed with reference to wave 1 would not have been worth
   comparing.
6. **Knowledge promotion is scheduled, not declined.** The decision is `revise` so the
   gate does not fire; the most promotable finding (RT-R1) is one probe nobody else has
   run; and a corpus entry from the same snapshot already exists on the other branch. The
   merger's superseding decision promotes once, correctly, with the index regenerated in
   the same archive commit.
7. **The goal is not paused, closed or completed.** Its `pause_conditions` are
   INFRASTRUCTURE-ONLY plus a user request. A duplicate execution, an uncommitted artifact
   set and a queue that must be superseded are none of them.

**The single next action carried for the merger to apply:** reconcile the two chains
first, then re-score G-VAR on the fibre family before any successor spends compute on
candidate observables — with the false-refusal control and an `fpylll`-equipped L7/L8
replication pre-registered behind it and structurally gated so they cannot displace it.
Full text in `DEC-20260812-15d3b2.goal_next_action_to_apply`.

---

## 4. What a later Coordinator would need to overturn me

Stated concretely, because a ruling that cannot be overturned is not a ruling.

**To overturn the additive-only disposition** — i.e. to conclude this branch should have
edited the goal record: show that the merge cost is lower than I judged (e.g. that the
concurrent branch's edit to `GOAL-MLKEM-005.yaml` is confined to fields this chain would
not touch), and show that carrying the next action inside a decision record measurably
lost something. My reasoning is in `DEC-20260812-15d3b2.branch_disposition` in full,
including the cost I accepted.

**To overturn the "coordination failure, not evidence failure" ruling:** show that
something about the collision touched the *bytes* — that a wave-2 report rests on
artifacts other than the committed snapshot `c034ef38`, that the relocation altered any
content, or that the relocation touched a path the concurrent branch occupies. The parent
session reports checking the last of these and finding **zero** files under
`reviews-wave2/` on that branch. If any of those turns out false, this ruling falls and
the correct instrument is a superseding record, not an edit.

**To overturn the admission of this wave as evidence:** the Validator names in its own
report what would change its verdict — a demonstration that the HKZ profile as computed
does not reproduce (which it could not test, `fpylll` absent); a second reviewer finding
that F-2's across-cell aggregation changes an outcome row under the frozen text's own
language; or a Coordinator determination that the two-chain situation makes this report's
path uncommittable, in which case the instrument is a superseding record under a new id
and **never** an edit to either report. I add one: if the merger's side-by-side reading
shows that a wave-2 finding was already established, or already refuted, by wave 1, then
`EV-MLKEM-e45478` is narrowed by a superseding record and not by a correction to it.

**To overturn RT-R1, which is the wave's most consequential finding:** run
`probe_gvar_family.py` and show that F1 does not differ from F0 in exactly one respect, or
that its 0-of-38 result does not reproduce. It costs 0.24 s. The Red Team named that
could-not-fail arrangement in the probe's own docstring before running it and asserted
against it in the probe's output; a successor should check the assertion rather than take
it.

**To overturn the scheduling of knowledge promotion:** show that RT-R1 or O-2 is
reproduced by a party independent of the reviewer that built it, or that the merger's
reconciliation has happened and a promotion is now owed. Either makes the promotion
appropriate, and the fibre re-score named in the carried next action is precisely the
experiment that would supply the first.

**What cannot be overturned by argument, only by measurement:** the claim tier. It stays
**TOY**. Nothing in this batch, in either wave, bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model, and no number here may be
transported to `beta = 606`, `d = 1420`, or any other parameter set by extrapolation, by
analogy, or by any other route.

---

## 5. Status of everything named here

**UNCOMMITTED.** This note, `EV-MLKEM-e45478`, `DEC-20260812-15d3b2` and all 30 wave-2
review artifacts sit uncommitted as written — **PD-4 in its sharpest recorded form**,
since a *different* review set is already committed at the paths these were originally
declared at. None of it is durable or official until the wave-2 ledger archive commits it,
the post-commit verifier accepts it, and the branch is pushed with an open PR against
`main` naming every new record. **Run the verifier before the push, not after**: that is
the recorded single lesson of this goal's own archive defects, and it has now been paid
for four times.
