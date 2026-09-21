# TASK-20260727-031 — adversarial notes

**Role:** Red Team, independent non-originating session
**Bound snapshot:** `a935f207a85f5d0a227b811cfbdde4393372aa1a`, parent `14deee8a`
**Branch/worktree:** `claude/ecdlp-batch006` @
`/Volumes/Volume/crypto-autoresearcher-worktrees/ecdlp-batch006`
**Companion record:** `red_team_report.yaml` in this directory

Nothing in this batch is a research result, a cryptanalytic result, an attack
improvement, a closure, or an impossibility claim. No hypothesis moves. No
measurement was taken.

---

## 0. Snapshot validation before interpreting anything

| Check | Command | Result |
|---|---|---|
| HEAD is the bound snapshot | `git rev-parse HEAD` | `a935f207…` |
| Parent is the plan commit | `git rev-parse HEAD^` | `14deee8a…` |
| Plan commit staged NO specification | `git show --stat 14deee8a` | 3 files: `repair_plan.md`, `GOAL-ECDLP-001.yaml`, `dispatch_queue.json` — neither spec |
| Repair commit changed exactly two spec lines | `git show a935f207` | `2 files changed, 2 insertions(+), 2 deletions(-)` for the specs, plus 4 new TASK-028 artifact files |
| Tree clean at entry | `git status --porcelain` | empty |

The commit-order claim is therefore true as a matter of git fact. Whether it is
*load-bearing* is section 2.

---

## 1. The same-act case, argued at full strength first

I was asked to argue the strongest case that this is `5de2db97` with better
paperwork before concluding otherwise. Here it is, and three of its seven limbs
survive.

**SA-1 — identical form.** Both edit committed artifacts in place under their
original ids and leave HEAD's text differing from the archived text with no
in-file marker. `CORR-20260727-007` defect_b describes the defect as records
standing "with no superseding record and no indication in either file that its
text was replaced." That sentence is presently true of
`experiments/EXP-STR-003/specification.yaml` at `a935f207`.

**SA-2 — size is not a principle.** Rule 4 has no *de minimis* clause. Two lines
versus 694 insertions is degree. A rule that yields to smallness yields to a
patient sequence of small edits. *Nothing in my verdict rests on the change
being small, and the Coordinator must not let it.*

**SA-3 — the correction does not exist (SURVIVES; this is objection OBJ-1).**
At the bound snapshot, `ledger/corrections/` contains CORR-001, CORR-002,
CORR-003 and nothing about this edit. Structurally that is the post-`5de2db97`
state exactly. The precedent is unflattering: `CORR-20260727-007` exists only
because an independent forensic validator (TASK-20260727-016, finding V-NEW-1,
severity HIGH) found the rewrite in git history a day later. "A correction is
coming" is what every uncorrected in-place edit looks like from the inside. And
the interruption risk is concrete, not theoretical — this campaign already
paused mid-batch at BATCH-006, needed `BUDGET-AMEND-20260727-004` to reach batch
8 at all, and BATCH-008's archive tasks *cannot be closed* under
`INT-BATCH007-T`.

**SA-4 — the plan is self-authored (SURVIVES).** The Coordinator wrote the plan,
approved it, and dispatched its execution. No AGENTS.md rule grants a Coordinator
authority to pre-authorize an immutability breach; rule 4 is not addressed to any
role. Had `5de2db97` been preceded by a one-line plan commit at 20:39, it would
satisfy this element in full. **Process-as-authority is the laundering
mechanism.** This is why the pre-committed plan is excluded from the load-bearing
set.

**SA-5 — worse on one axis (partly survives).** This edit destroys a hash
attestation that TASK-20260727-023 specifically established; `5de2db97` broke no
hash attestation, it only rewrote prose and numbers. Rebutted in part because the
attestation *as worded in EV-STR-003* is about two named commits and survives
(section 4), but the residual in OBJ-2 is real and unnamed anywhere in the batch.

**SA-6 — the program already had a non-overwriting mechanism and used it on this
very file family.** `experiments/EXP-IC-002/amendments/v1_to_v2.yaml`, committed
at `e0db8ef7` roughly a day before this batch, states:

> `specification.yaml` version 1 is **PRESERVED UNCHANGED**. This amendment
> supersedes the named fields; it does not overwrite them. […] Where the two
> disagree, this record governs.

`git log -- experiments/EXP-IC-002/specification.yaml` confirms it: the file was
touched at `6e6fd28e` (birth) and `a935f207` (this repair) and nowhere else — the
"amend to v2" commit did not touch it. So the repository's established practice
for changing a frozen spec is *preserve and supersede*. Repair-in-place inverts
it. Partly rebutted, because an amendment sidecar cannot fix a **parse** failure
(it registers no id), but decisive for the fourth mechanism in section 3.

**SA-7 — proportionality, never priced (SURVIVES; OBJ-4).** The repair clears
5 of 990 non-grandfathered errors — 0.5 %. The validator still exits 1 at 985.
No gate was unblocked, because no gate can be gated on a validator failing at
990. Eleven other specifications remain unparseable and grandfathered in
`tools/validate_ledger_baseline.txt`:

```
EXP-DREG-001  EXP-DREG-002  EXP-EQJ-001  EXP-FB-001   EXP-FB3-001  EXP-ICI-001
EXP-REP-001   EXP-REP-002   EXP-SIG-001  EXP-SIG-004  EXP-SIG-005
```

The true claim is "these two experiments now register," not "the ledger now
validates," and the batch never draws the comparison.

---

## 2. Verdict: the disanalogy holds, on one element, and it is not the one led with

**HOLDS NARROWLY.**

The load-bearing element is **not** the pre-committed plan, not the two-line
bound, and not "snapshot before review." It is:

> **The pre-edit objects had no valid parse at all, so no assertion could
> change — and that is provable mechanically, by a stranger, from the commit
> alone.**

`5de2db97` took records that **parsed** and asserted "the structured solve is
NOT cheaper at B=27" and "16/20-bit instances were too slow to generate," and
made them assert measurements at B = 204 and B = 397 and "H-STR-002 is
confirmed." `a935f207` took two files that asserted **nothing** — they were not
records, they were corrupt files — and made them assert exactly the character
sequences a human already read on those lines. Rule 4 protects results and
claims. There was no claim to protect and none moved. That is a difference in
kind.

### The one command that decides the whole question

```
git cat-file blob <pre-edit-blob> | python3 -c "import sys,yaml; yaml.safe_load(sys.stdin)"
```

- against `5de2db97`'s pre-edit `EV-STR-002` / `DEC-20260726-006` blobs → **succeeds**
  (they were records; rewriting them changed assertions)
- against `1c6f10b7` and `8987eb01` → **raises `yaml.ScannerError`**
  (they were not records)

One command, no trust in the actor, no reference to any plan.

### What stops the next in-place edit from being laundered

Because the plan is not load-bearing, a *process*-gated rule ("we planned it
first, so it's clean") licenses exactly the laundering the task worried about —
and would immediately expose the eleven other broken specs. The boundary has to
be **content**-gated and reader-checkable. Proposed for `CORR-20260727-004`:

| Gate | Requirement | Met by this repair? |
|---|---|---|
| **L1** | Pre-edit blob has **no valid parse** under the schema it claims — a corrupt file, not a record. Anything that parses is a reissue-under-new-id, **full stop**. | **YES** (verified, both) |
| **L2** | An **inverse transform** of the post-edit blob reproduces the pre-edit blob byte-for-byte over the whole file, exhibited as a re-runnable script. | **In fact yes; not archived** |
| **L3** | Pre-edit bytes preserved as a **live file in HEAD**, not only in history. | **NO** |
| **L4** | The superseding correction lands **in the same commit** as the edit, or the edit does not land. | **NO** (OBJ-1) |
| **L5** | No field any downstream immutable record quotes changes value. | **YES** |

L1 is the knife: it can never extend to a `5de2db97`-shaped case, because those
files parse. L4 closes the "promised correction" gap that SA-3 exposes.

---

## 3. Mechanism comparison — was repair-in-place the only option?

| # | Mechanism | Clears 5 errors? | Frozen blob live at HEAD? | Rule-4 exposure | Stability | Considered by the plan? |
|---|---|---|---|---|---|---|
| M1 | **Repair in place** (chosen) | 5/5 | **no** (history only) | yes | stable | yes, chosen |
| M2 | Reissue under a new EXP id | 0/5 — the three cross-refs name `EXP-STR-003` in immutable records, and the unparseable file stays in the glob | yes | none | stable | yes, rejected correctly |
| M3a | Repaired sidecar at a **non-globbed** filename | **0/5** — validator globs `experiments/*/specification.yaml` **only** (`validate_ledger.py:461-462`) | yes | none | stable | yes, rejected correctly |
| M3b | Repaired copy at another `experiments/<dir>/specification.yaml` carrying `id: EXP-STR-003` | 3/5 (registers the id; the two `invalid YAML` lines persist) | yes | none | **unstable** — becomes `duplicate ID` the moment the original is ever repaired; two sources of truth | yes, rejected on those grounds |
| **M4** | **M1 + the frozen ORIGINAL preserved as a live non-globbed companion** | **5/5** | **YES** | yes, but **discharged by artifact** | stable — the companion is never parsed, so it can never collide | **NO — this is the gap** |
| M5 | Relax `check_experiment` to tolerate the parse failure | 5/5 | yes | none | — | no; **reject**: changes the instrument to clear a defect in the object, and masks the eleven other broken specs |
| M6 | Baseline the five errors | 5/5 suppressed | yes | none | — | forbidden; the baseline is prune-only by construction (`validate_ledger.py:472-477`) and its header says lines may only ever be removed |
| M7 | Do nothing; record an integrity note | 0/5 | yes | **none** | stable | **no — never weighed.** Defensible on SA-7 grounds; fails because it leaves three *correct* immutable records permanently flagged as broken by a defect elsewhere |

### The fourth mechanism, concretely

**M4 = repair in place **plus** preserve the original bytes as a live sibling.**
Commit blob `1c6f10b7…` verbatim to
`experiments/EXP-STR-003/specification.v1-frozen-1c6f10b7.yaml`, and `8987eb01…`
to `experiments/EXP-IC-002/specification.v1-frozen-8987eb01.yaml`.

Why it is safe, checked not assumed:

- `tools/validate_ledger.py:461-462` globs `experiments/*/specification.yaml`
  **exactly**. A companion under any other filename is never opened, never
  parsed, registers no id, and therefore *cannot ever produce the `duplicate ID`
  instability the plan rightly feared for M3b*.
- Grepping `tools/`, `harness/`, and `orchestration/` for `specification.yaml`
  returns the validator and two fixture lines in
  `tools/test_research_dispatch.py`. **Nothing else in the repository reads
  experiment specifications.** Blast radius of the addition: zero.
- It is **additive**. It modifies no committed file and deletes nothing. Adding
  bytes that are already permanently attested is not an immutability breach; it
  is the discharge of one.

Why the plan missed it: §2.3 evaluated *sidecar-as-registration* — a repaired
copy the validator would read — and rejected it on three correct grounds. It
never evaluated *sidecar-as-preservation*. The very property that makes a sidecar
useless as a repair (the validator ignores it) makes it ideal as a preservation.
And it restores the shape the repository already uses for frozen specs
(`amendments/v1_to_v2.yaml`, SA-6).

**It is still available.** M4 requires no revert and no re-edit — only two added
files under `TASK-20260727-032`, which means widening that task's `write_scope`
by exactly two experiment paths. That is the Coordinator's call.

*Fallback if M4 is judged scope creep:* `CORR-20260727-004` must at minimum
record a **SHA-256** of each pre-edit file beside the git blob ids. Every hash in
this batch is a git-internal SHA-1; a content hash makes retrieval verifiable
independently of git and of this repository. **Recompute and archive it — do not
copy it from any review report.**

---

## 4. Does the blob change damage the F1 result? No.

I re-derived every clause of `EV-STR-003.provenance.freeze_evidence`
independently at the bound snapshot rather than accepting the Executor's report:

| Clause | Independent check | Result |
|---|---|---|
| Blob at the freeze commit | `git rev-parse 92268c9e:experiments/EXP-STR-003/specification.yaml` | `1c6f10b7…` ✔ |
| Blob at the run-package commit | `git rev-parse c79e3a8d:…` | `1c6f10b7…` ✔ (so the diff between them is empty) |
| Parent relation | `git rev-parse c79e3a8d^` | `92268c9e…` ✔ |
| Freeze commit added exactly one path | `git show --name-only 92268c9e` | one path, that spec ✔ |
| 20 runs attest the freeze commit | `grep -h "commit:" runs/*/manifest.yaml \| sort \| uniq -c` | `20  commit: 92268c9e…`, one distinct value ✔ |
| Run packages unmodified | `git status --porcelain experiments/EXP-STR-003/runs experiments/EXP-STR-003/results` | empty ✔ |
| Original blobs retrievable | `git cat-file blob 1c6f10b7… / 8987eb01…` | both succeed ✔ |

**Every clause is a statement about *named commits*, not about HEAD.** Not one is
falsified. The pre-registration ordering that makes F1 evidential — criteria
frozen at `92268c9e` *before* execution at `c79e3a8d`, runs attesting `92268c9e`
with `dirty: false` — is a property of commit order that no later edit can touch.
`DEC-20260727-009` quotes no HEAD blob and depends on no HEAD byte-identity.

**What does not survive:** HEAD byte-identity with the attested freeze, and the
property that the frozen contract had never been edited after freezing.

**The one residual harm, which nobody in this batch names (OBJ-2).**
`ledger/evidence/EV-STR-003.yaml:134` lists

```
  proof_refs:
    - experiments/EXP-STR-003/specification.yaml
```

as a **bare path with no commit pin**. A reader resolving that proof_ref at HEAD
now gets blob `5e0dadf7`, not the `1c6f10b7` the evidence was written against.
The difference is one inserted quote pair, so no criterion, threshold, or
prediction moved and the reader is not *misled* — but they are not *told*, and an
immutable evidence record should not require its reader to know that. The
information to resolve correctly is present two lines above
(`contract_freeze_commit`, `contract_blob`); nothing instructs the reader to use
it. `CORR-20260727-004` must state the rule — *resolve at `92268c9e`, not at
HEAD* — and M4 closes it entirely.

---

## 5. "Semantic preservation is unprovable mechanically" — the plan over-concedes

`repair_plan.md` §5 says no tool can certify same-semantics here and substitutes
an eye-verifiable diff plus two reviews. **That is wrong in the safe direction,
and it should be corrected rather than accepted.**

What is genuinely unavailable is a *parsed-tree diff*. What **is** available — and
is strictly stronger for a pure-delimiter change — is an **inverse-transform
byte-identity proof**: delete the inserted delimiters from the post-edit blob and
require the pre-edit blob back, byte for byte, across the whole file.

Scratch probe (labelled below; **not evidence**):

```
EXP-STR-003
  BEFORE yaml.safe_load raises: ScannerError while scanning a block scalar
  AFTER parses OK, id = EXP-STR-003
  line counts: 924 924    differing 1-based lines: [407]
  inverse-transform(after_line) == before_line : True
  FULL-FILE inverse transform == before bytes  : True
  parsed value == original post-key text       : True
EXP-IC-002
  BEFORE yaml.safe_load raises: ScannerError while scanning a block scalar
  AFTER parses OK, id = EXP-IC-002
  line counts: 512 512    differing 1-based lines: [213]
  inverse-transform(after_line) == before_line : True
  FULL-FILE inverse transform == before bytes  : True
  parsed value == original post-key text       : True
```

Combine that with two further facts and the argument is **complete**, not papered
over:

1. The pre-edit blob has **no valid parse at all**, so there is no second reading
   the repair could have chosen wrongly. (A YAML-fluent reader might ask whether
   `p_dec_counting_bound: |` was *meant* as a block scalar — it cannot have been:
   `|S| / N.` has content after the indicator, which is unparseable in every
   reading. There is exactly one candidate intent and the repair encodes it.)
2. Neither changed line contains a single-quote character, so the single-quoted
   form needs no escaping and the parsed string is the original character
   sequence exactly — which the probe confirms.

**So the answer to "is a two-line eye-verifiable diff plus two reviews an
adequate substitute?" is: the check is not missing, so nothing is being
substituted for.** The two reviews are doing a different and necessary job — they
check the **choice** of repair (quoting rather than rewording, `version` left at
1, `frozen`/`frozen_on` not added to EXP-IC-002 where they are absent), which is a
judgement call and correctly reviewed.

Recommendation: `EV-SPEC-001` should archive the inverse-transform check as a
re-runnable script with captured output and rest `proof_status: derivation` on
that, rather than on eye-verification. I am **not** asking for a certificate
claim; `derivation` remains the right tier.

---

## 6. Blast radius — correctly scoped, no sixth consequence found

I diffed the two **committed** validator captures directly rather than trusting
the summary. The diff is the header count line plus **five deletions and zero
additions**:

```
1c1
< FAIL: 990 new validation error(s):        > FAIL: 985 new validation error(s):
57d56  < experiments/EXP-IC-002/specification.yaml: invalid YAML: while scanning a block scalar
60d58  < experiments/EXP-STR-003/specification.yaml: invalid YAML: while scanning a block scalar
982d979 < ledger/evidence/EV-STR-003.yaml: evidence references unknown experiment 'EXP-STR-003'
985,986d981 < ledger/decisions/DEC-20260727-008.yaml: decision references unknown target 'EXP-IC-002'
             < ledger/decisions/DEC-20260727-009.yaml: decision references unknown target 'EXP-STR-003'
```

Additional checks I ran that the batch did not:

- **Could any tool, run, or record have silently consumed an unparseable spec?**
  **No, and none could have.** `tools/validate_ledger.py` is the only program in
  the repository that opens `experiments/*/specification.yaml`. The 20 runs were
  driven by `experiments/EXP-STR-003/driver/ablation_driver.py` from CLI
  arguments, and `grep -l "specification" experiments/EXP-STR-003/runs/*/manifest.yaml`
  returns **0**.
- **Duplicate mapping keys** in the now-parseable documents — a real new risk,
  since `yaml.safe_load` silently drops duplicates and the parsed content becomes
  authoritative for the first time: **none in either file.**
- **Type coercion** (boolean/null keys, Norway-problem values, unintended
  floats): **no coerced keys**; `frozen_on` parses as a date, benign.
- **Approval fields**: both parse to `status: approved` with non-null
  `success_criterion`, `falsification_criterion`, `approved_by`; `version: 1` in
  both; `frozen: true` / `frozen_on: 2026-07-27` for EXP-STR-003; `frozen`
  **absent** in EXP-IC-002 and correctly **not added**.
- **One adjacent inconsistency, pre-existing (OBJ-6)**: the repaired EXP-IC-002
  parses to `version: 1` while `amendments/v1_to_v2.yaml` declares
  `version_to: 2`. That is by design and the validator does not check it — but
  now that the document registers, a future consumer reading
  `experiment.version` will read 1 and miss the amendment. One sentence in
  `DEC-20260727-003` fixes it.

**The standing limitation this exposes (OBJ-7, not caused by this batch, not used
to attack F1):** the frozen contract was never *machine-bound* to the execution.
Nothing ever verified that the driver implemented the frozen protocol; the
pre-registration guarantee behind F1 is commit order plus human transcription.
That was equally true at `92268c9e`. "20 runs executed against a spec no tool
could parse" is a symptom of that general property, not of this defect. Record
it; do not act on it here.

---

## 7. Framing and scope

Confirmed, and I checked rather than assumed: nothing here is a research result.
`ledger/goals/GOAL-ECDLP-001.yaml` states it directly — *"BATCH-008 IS NOT
RESEARCH."* No measurement, no run, no certificate, no solve, no relation, no
attack improvement, no closure, no impossibility claim, no exponent movement.
`H-STR-002` and `H-IC-001` stay `weakened`.

Three framing risks to guard:

1. **`EV-SPEC-001` carries `hypothesis_id: H-STR-002`.** An evidence record bound
   to a hypothesis it does not bear on *will* be miscited later. The plan's own
   guards — `direction: neutral`, `claim_tier: toy`, `run_ids: []`,
   `proof_status: derivation`, boundaries stating it moves neither hypothesis —
   are all necessary, plus one explicit sentence that it bears on the **contract
   artifact**, not on the mechanism.
2. **`DEC-20260727-003.knowledge_promotion` must be `not_warranted`** with a
   reason. A YAML quoting repair must never enter `knowledge/` as a finding.
3. **Do not phrase "990 → 985" as validator improvement without the
   denominator** (OBJ-4). This is the same class of error as quoting per-attempt
   cost without the inverse success probability: a true number that overstates
   what was bought.

And one procedural correction: **the "snapshot before review" element of the
disanalogy is not dispatcher-verified** (OBJ-3). `BATCH-008/dispatch_queue.json`
carries `commit_sha: null` for all eight tasks, by design, because
`INT-BATCH007-T` / `INT-BATCH008-C` make archive-task verification unreachable
repository-wide. I verified `a935f207` by hand against every property the verifier
*would* check — reachable from HEAD, expected parent, exactly the declared paths,
recorded hashes preserved, task and record ids named — but that is my check, not
the dispatcher's. `DEC-20260727-003` must say so and must not fabricate a receipt.

---

## 8. Probe disclosure and repository hygiene

- Every computational probe in this report ran in the **session scratchpad
  outside the repository**. Blobs were extracted with `git cat-file blob` into
  scratch and analysed there. **These results are NOT evidence and must not be
  cited by any record.** They must be re-derived and archived under
  `TASK-20260727-032` (required control RC-3).
- I state this explicitly because an earlier session in this campaign drove a
  decision from an unarchived scratchpad probe that then failed to reproduce.
- **No file inside the worktree was created, modified, or deleted by any probe.**
  Bash was used read-only (git queries and file reads). No commit was made. No
  status was changed. No evidence, decision, or correction record was created.
  `git status --porcelain` was empty at entry, and the only paths this task
  writes are the two deliverables under its assigned `write_scope`.

---

## 9. Single next concrete action

Run `TASK-20260727-032` and, **in the same commit as `CORR-20260727-004`**, land:

1. the two frozen-original companion files
   (`experiments/EXP-STR-003/specification.v1-frozen-1c6f10b7.yaml` byte-identical
   to blob `1c6f10b7…`, and
   `experiments/EXP-IC-002/specification.v1-frozen-8987eb01.yaml` byte-identical
   to blob `8987eb01…`);
2. the archived, re-runnable inverse-transform check with its output;

and have `CORR-20260727-004` state the **L1–L5 precedent boundary** and pin
`EV-STR-003`'s specification `proof_ref` to commit `92268c9e`.

This requires the Coordinator to widen `TASK-20260727-032`'s `write_scope` by
exactly those two experiment paths. That is the Coordinator's decision, not this
report's.
