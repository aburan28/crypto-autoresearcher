# TASK-20260903-d3bef8 — amendment-005 authoring report

**Goal** GOAL-AES-002 · **Question** RQ-AES-002 · **Batch** BATCH-ae07ce ·
**Role** coordinator · **Authored** 2026-09-04

**Deliverable under report**
`coordination/goals/GOAL-AES-002/amendments/protocol-amendment-GOAL-AES-002-005.yaml`

**Claim ceiling of everything below: SPECIFICATION RESULT ONLY.** Nothing in this
report asserts, implies or depends on any property of AES at any round count, in
either direction. No margin, no cost figure, no speedup, no advantage and no
comparison against any published state of the art appears anywhere in it, so
RQ-AES-002's R5 same-sentence duty has nothing to attach to and is discharged
vacuously — recorded here rather than left for a reader to infer. Every symbolic
form used (one AEU-k, `(N/S_k + X/X_k)` AEU-k, N verification units, `2^(k-1)`,
`2^(k-m-1)`) is a charging form of the frozen cost model or a stipulated
parameter of an explicitly hypothetical construction; no N, X, D, G, M, m, t or
survivor count is given a value anywhere.

---

## 1. What was produced, and what it claims

Amendment 005 supplies two operative rule blocks — clauses **A5-0 … A5-5** for
CM-1 element (a)'s ADMISSIBLE CONVERSION ROUTE 3 bar, and clauses
**B5-0 … B5-4** for the element (c)/(f) separate-verification charge.

**The single design commitment**, applied to every gap: *remove the term that
failed to determine the answer from the operative test, rather than redefine
it.* Where a term could not be removed, it was replaced by a closed enumeration
or by a comparison of numbers the claimant is already required to declare.

- A-2's "independent" (a semantic predicate) is replaced by A5-3, a
  three-limb test on **what the attack performs and whether its cost is on the
  bill**, with A5-4 supplying a closed six-item enumeration of what the bar
  ranges over.
- B-1's "a FULL evaluation" (a predicate about a described operation) is
  replaced by B5-1, **an inequality between two declared numbers**: is the claim
  already charging at least one AEU-k per member of the set.
- B-2's "the last production stage that does not include a full per-candidate
  evaluation" is replaced by B5-3, which **names the sets** the test applies to
  and takes the maximising one once. B5-2 individuates a stage boundary
  operationally (RC-3's own words) and then states that **no charge depends on
  it**.

**What the amendment does not claim.** It makes no determinacy claim and no
reader-agreement claim for its own text, because none has been measured. The
frozen panel has been classified against -004 and against superseded -003; it
has **not** been classified against this text. Two amendments have now claimed
closure and been ruled open by an independent review or a Coordinator decision;
this one states its closures as arguments by their author and names the
measurement that would test them as unrun.

---

## 2. The four load-bearing validator findings, each addressed or declined

### (a) The SPEC-10 disagreement — ADDRESSED, and resolved in a way a blind reader can reach

The independent validator, reading only clauses B-1 to B-4 and hashing its
verdicts before opening `relation_to_what_003_already_closed`, recorded
`SEPARATE_CHARGE_APPLIES` on the partial-key-recovery-with-exhaustive-residual
shape. -004's committed text says `BUNDLED`. That is a reader disagreeing with
an author on one of the two items RC-6 designated pass-capable — the event RC-6
exists to detect.

Amendment 005 does **not** adjudicate between the two readings. It removes the
distinction they disagreed about. The validator's own diagnosis is that -004
"treats the residual search as production work" while B-2 levies the charge on
the survivors of the last production stage, and that "the clauses are not
reconciled in the text". Clause B5-1 states in its own operative words that the
test is *not* whether work is called production or verification; it is the
number on the bill per member of a set, and clause B5-3 says which set. On the
shape at issue the residual set is charged one AEU-k per member, so it bundles,
and CM-1 element (c)'s partial-key-recovery clause — untouched — charges the
residual search in full.

**Stated against this record's interest, in the amendment and here:** this
resolution lands on -004's author's answer and not on the blind reader's, and
this author is the same model family as -004's. Three counterweights are
recorded rather than assumed: the route to the answer is a declared number
rather than a prose assertion; clause B5-3 *excludes* a charge -004's B-2 would
have levied (a reduction, disclosed as such); and **the claim that a blind
reader will now agree is not made.** If a blind reader of B5-1 and B5-3 records
SEPARATE on this shape, the repair has failed the way the two before it failed,
and that is a finding to record, not to argue away.

### (b) The m=0 control is degenerate for this clause — ADDRESSED with four B-block controls, three of them non-degenerate for the boundary clauses

PVF-2 established that at m=0 there is one production stage, so B-2 never binds
and the control cannot reach the clause the SPEC-10 disagreement turns on.
Re-running it alone would have been a band that cannot fire. Six controls were
run on paper; each carries a **non-degeneracy argument naming a nearby wrong
rule that the same object would detect**:

| id | clause under test | object | outcome | the nearby wrong rule it detects |
|---|---|---|---|---|
| PT-1 | B5-1 | m=0 definitional reference | BUNDLED; definitional figures unmoved | a strict `> 1 AEU-k` threshold — the reference sits **exactly on** the threshold, so it fires and roughly doubles a definitional figure (draft B-0's failure) |
| PT-2 | B5-3 (and B5-1 through it) | two-phase attack at m > 0, boundary **active** | BUNDLED for the residual set; residual charged in full under element (c) | (i) -004's B-2 first limb, which adds a verification term on top of element (c)'s residual charge; (ii) a rule treating the residual as free |
| PT-3 | B5-1 | early-aborted per-candidate evaluation on a candidate-key pool | separate charge applies | a rule keyed to the specification sentence, which yields BUNDLED and drops the whole verification term |
| PT-4 | B5-2 + B5-3 | reference plus a trivial bookkeeping filter (boundary now exists) | BUNDLED; figure unmoved | a rule charging at every boundary, which doubles a definitional figure |
| PT-A1 | A5-3, A5-4 | the pullback pair (RC-1) | **verdict invariant**: both forms barred | -004's own text, under which the two forms receive different verdicts |
| PT-A2 | A5-4 | attack whose whole cipher-structural inventory is counted | bar does not fire; Route 3 not emptied | the literal reading of A-2's iff over an undefined "bytewise operation" (DEF-004-1), under which Route 3 admits nothing |

PT-1 is retained but its limit is restated, not inherited: it remains inactive
for the boundary clauses, exactly as PVF-2 established, and PT-2 and PT-4 exist
because of it. **PT-2 is the m > 0 instance the validator's forward guidance
asked for**, with a stated stage decomposition and the boundary live.

PT-A1 also closes the asymmetry DEC-20260901-d264ea named as structural: -004
ran a proves-too-much control for B-1 and none anywhere on A-1..A-4, and two of
its three A-block breaks were in that block. RC-1 is that missing control and it
is run here.

**One draft was killed by a control during authoring and is recorded rather than
deleted** (`rejected_drafts` DRAFT-B-LASTBOUNDARY): a rule levying the charge on
the survivor set at the last stage boundary proves too much on the m=0
reference, because the final comparison itself strictly decreases the candidate
count. That is the control doing its job on this text, not on a predecessor's.

### (c) Measured gain and its inflation — NO GAIN IS CLAIMED, so nothing is double-counted

The amendment claims no determinacy gain, for -004 or for itself. The one
measurement that exists is one reader's classification, and the amendment
records all three of the bounds that reader put on it — 2 of 12 forced T-004
cells decided by clauses quoting the item verbatim; 7 of 20 cells per text
NOT_ENGAGED under both texts, leaving 13 informative; "forced" a single reader's
judgement and a proxy for agreement, not agreement — plus the reader-correlation
bound, without summing them into a net figure and without asserting that -004's
count transfers to this text.

### (d) Not measured, not negative — CARRIED FORWARD AS OPEN AND UNATTEMPTED

Each of the following is recorded in the amendment's `open_and_unattempted`
block in exactly these terms — **not tried, not screened, not negative**:

- **On-the-fly tables** (OU-005-2). Neither verdict table says anything about
  them; no on-the-fly construction exists in this campaign's committed records.
  A5-4 names "a table access" without regard to when the table is built, and the
  amendment states in terms that this is **not** a claim the shape is handled.
- **The second null column** against an empty rule text, CM-1 alone (OU-005-3).
- **The -005 column** — the frozen panel classified against this text
  (OU-005-4).
- **Inter-reader agreement**, on any text (OU-005-5). One reader cannot measure
  it; this task is one author with no reader at all.

Also carried: DEF-CM1-A (OU-005-1), DEF-PANEL-4 (OU-005-8), OBJ-5 and the -004
half of OBJ-6 (OU-005-6), -004's OU-1/OU-2/OU-3/OU-4 (OU-005-7), and the
DEF-CM1-CLOCK ruling owed as OI-3 (OU-005-9).

---

## 3. Repair-by-relocation: the audit, clause by clause

The named enemy is a resolving clause that removes an ambiguous word and
introduces a new undetermined one elsewhere. **Every clause in 005 carries a
`relocation_argument` as a required field**, and each names the panel shapes it
is addressed to. The shape of the argument is the same throughout: *what new
term does this clause introduce, and is it closed, a number, or already-tested
committed text?*

| clause | new term introduced | why it cannot relocate |
|---|---|---|
| A5-0 | none (clause identifiers only) | an ordering over two names; A5-1 makes the routing unconditional, so the phrase "could be read to differ" is not load-bearing |
| A5-1 | none | membership in a two-item list quoted from A-3, closed by "and no others" |
| A5-2 | three byte origins | each referent fixed in committed text (element (d); N and X; A-3(i) itself); recursion terminates on a finite specification; unlisted origins route to A5-3, which is total |
| A5-3 | "the attack performs, at the level A-1 fixes" | **not new** — A-1's own term, the one A-block clause both independent reviews record as holding. The extensional escape and the materiality escape are each foreclosed by name |
| A5-4 | a closed six-item enumeration | five FIPS-197 maps plus "table access" (already operative in A-3(ii)); its one extensional sentence quantifies over **five fixed maps**, never over algorithms computing the attack's function |
| A5-5 | none (disclosure) | requires counts over A5-4's closed list; element (f) already individuates precomputation |
| B5-0 | none | identifiers; preservation-by-quotation of unchanged committed words |
| B5-1 | none | an inequality between two declared numbers; four candidate relocation sites are foreclosed in the clause text by name |
| B5-2 | "stage boundary" defined by a strict decrease in declared counts | and then **no charge depends on it** — an ambiguity cannot relocate into a term that no longer decides anything |
| B5-3 | "verifying test", "candidate-key set", "the maximising set" | operation kind + effect, with the aborted-evaluation sub-question settled in the clause; a member property element (c) already requires; a maximum over a finite enumerated family |
| B5-4 | none (disclosure) | replaces a binary judgement field with three declared quantities |

**Two residuals are named as live attack surfaces and are not claimed closed**,
because claiming them closed is what the two previous amendments did:

1. **A5-3 presupposes an honest specification-level description.** This is -004's
   own limitation L4, carried forward. A5-5's per-kind inventory makes a
   description auditable; it does not make it self-verifying. A red team should
   attack here again.
2. **B5-3's boundary between "evaluates part of AES-k under the candidate key on
   element (d) data" and "computes some other function of the candidate."** A
   claimant able to present a partial cipher evaluation as pure algebra would
   remove a set from those B5-1 tests, in the direction of a smaller total.

---

## 4. Changes of reading relative to -004, in both directions

-004 declared of itself that it was not a widening of Route 3. **005 makes a
less comfortable disclosure: it changes readings both ways, and both ways are
listed in the record.**

Narrowings (against the claimant): a Route 3 claim whose attack computes a
cipher-structural constant for itself, even once at specification time, is
barred — this is the price of RC-1 invariance, and its ground is -003's own
committed sentence forbidding a materiality threshold under Route 3; a run-time-only
operation inventory is inadmissible under A5-5; B-4's binary field alone is
inadmissible under B5-4; a charged cost below one AEU-k per member of a verified
candidate-key set carries element (f)'s charge whatever the specification says.

**The one reduction in charge (toward the claimant):** element (f)'s separate
charge is not applied to sets of *partial*-key values, because CM-1 element (c)
already charges a partial-key-recovery attack its own cost plus the residual
exhaustive search, and levying element (f) on the partial-key guess set as well
charges the same "the key is not yet recovered" fact twice under two elements —
which -004's own clause B-3 prohibition is written against. This is disclosed as
a reduction, not dressed as a clarification, and a reviewer should test whether
it opens a laundering route. The check run here is PT-2, and it is an argument,
not a measurement.

---

## 5. The frozen panel: used as a constraint, never fitted to

- The panel (`…/tasks/TASK-20260903-59e9b9/panel-spec.yaml`, sha256
  `e9fe9f91…0ee29b` as declared in this task's dispatch and independently
  recomputed by TASK-20260903-373afa) was **not edited and no edit is proposed**.
  This session did not recompute the digest and does not claim to have — it has
  no command-execution tool.
- **The operative text contains no worked example, no panel item, no attack name
  and no verdict.** This is the one structural difference from -003 and -004,
  and it is deliberate: the blind classifier of the -005 column reads exactly the
  two `resolving_text_verbatim` blocks plus CM-1, so an operative text carrying
  its author's classifications would destroy the third column before it is run.
- The panel's published T-004 verdicts are cited in exactly one place — PT-A1's
  non-degeneracy argument — and only to establish that a control band can fire.
- Where the text plainly changes the reading of a shape the panel contains, the
  change is recorded in `changes_of_reading_relative_to_004` **as this author's
  own reading**, not as a prediction of what a blind reader will record.
- A `reader_warning` binds any future classifier: `closure_arguments`,
  `controls_run`, `limitations` and `changes_of_reading_relative_to_004` are the
  analogue of the worked examples the panel's blindness obligation forbids
  reading before verdicts.

---

## 6. Required controls: incorporated, with one declared deviation

- **RC-1** (specification-rewriting invariance) — incorporated and run as PT-A1
  against A5-3/A5-4. Pass criterion as written is **met**: the verdict is
  invariant under the pullback rewriting.
- **RC-2** (precedence sentence; A-3(i)'s antecedent extended to element (d)
  input bytes) — both limbs adopted, as A5-0/A5-1 and A5-2. RC-2's *first*
  option was taken; why, and what it costs, is recorded.
- **RC-3** (bind "full evaluation" to charged expected cost; individuate a stage
  operationally; re-run the m=0 check) — incorporated as B5-1, B5-2 and PT-1.
  **Declared deviation by strengthening:** RC-3 treats the stage as an input to
  the charge; B5-2 individuates it exactly as RC-3 specifies and B5-3 then
  removes the charge's dependence on it. A reviewer who prefers RC-3's literal
  form should say so — nothing is hidden behind the control's name.
- **RC-6** — open for this text, discharged by nothing yet. This record's only
  contribution to it is structural and negative (no worked examples), so the
  third column can be run blind.

---

## 7. Constraint discharge

| constraint | discharge |
|---|---|
| Compute | **ZERO, and known rather than unmeasured.** This session's tool surface is file read/write/edit, content search, path glob and inter-agent messaging; there is no command-execution tool, so no benchmark, sample, run or measurement of any kind could have been or was performed. `maximum_runs: 1` declared, **0 runs used**. |
| Network / web retrieval | **ZERO.** No web retrieval, no network request, no external lookup. Every input is a file at a declared path in this repository. |
| Knowledge retrieval | **NOT PERFORMED** — no `search_knowledge` / `get_context` / `get_source` / `find_related` tool on this surface. No query is recorded as issued because none was. This licenses **no** absence, novelty or non-novelty inference. |
| Margin statements | **NONE.** R5 discharged vacuously and recorded as such. `dominated_by: unresolvable in this environment; no primary source reachable; every recalled frontier row is unverified-from-memory` — the same statement -004, the panel and the verdict tables each record about themselves. |
| Assertions about AES | **NONE**, at any round count, in either direction. |
| Immutability | **No committed record was edited.** CM-1, all four prior amendments, the frozen panel, the verdict tables, the red-team report, the decisions and the goal record were opened read-only. Corrections are new records. |
| Write scope | **Exactly two files**, both inside scope: the amendment and this report. No ledger record, no queue file, no panel file, nothing outside scope. |
| Commit | **NOTHING WAS COMMITTED.** No git command was run — none could be. |
| Amazon Bedrock | **Not selected, not configured, not probed, not contacted, not used** in any runtime, backend, endpoint, model identifier, fallback or probe. |

**One completion-gate item is checked by structural review only, and that is
stated rather than implied.** The gate requires both deliverables to be strict
parseable YAML/Markdown with no duplicate keys. This session has no
command-execution tool, so it could **not** run `yaml.safe_load` or any parser
over the amendment. What was done instead: the file was re-read in full after
writing; the block-scalar indentation, the sequence/mapping boundaries and the
top-level and per-item key sets were inspected by hand, and one real defect found
this way was fixed (a mapping key emitted at the indentation of a sequence's
items under `superseded_clauses`, which would have failed to parse). **Parse
verification is therefore OWED to the archival task and to the batch validator**,
and no claim is made here that a parser has accepted these bytes.

**Budget.** Declared 1600 s wall clock / 2 GB / 1 run; 0 runs used; compute 0 s.
Every clock field is **null and not invented**: no clock is readable from this
session. This is DEF-CM1-CLOCK's **fourth observed recurrence**, now across four
batches (BATCH-2b0fd1 → BATCH-286bcd → BATCH-241d37 → BATCH-ae07ce). The task is
charged at its declaration under the C6 charged-at-declaration fallback, the
defect is recorded against the campaign's instrumentation and not against the
producer, and no ruling is made here — that is OI-3, owed to a Coordinator
decision. No halt occurred and no declared work was dropped; that is **not** a
claim that the 1600 s declaration was respected, which was not observable from
inside.

---

## 8. Inference provenance

| field | value |
|---|---|
| requested policy | `coordinator-orchestration-code` |
| requested reasoning effort | `null` in the handoff (= policy default, which is `high` under this runtime per the CLAUDE.md policy table) |
| **effort cap disclosure** | **No cap is claimed to have been applied and none is claimed not to have been.** This session cannot read back the effort actually in force; the value is UNVERIFIED FROM INSIDE. Stated positively: no downgrade was requested by this session, none was accepted, and nothing was delegated to a cheaper policy (DEC-20260903-16bfc2). |
| fallback_allowed / degraded_allowed | `false` / `false`; **fallback_used: false** |
| resolved model (self-reported) | `claude-opus-5`, from this session's own runtime context. Not copied from `orchestration/model-bindings.yaml` and not offered as live confirmation that the committed binding was honoured — this session cannot query its own backend, so the resolution is UNVERIFIED FROM INSIDE, the same disclosure CM-1, -003, -004, the panel and the verdict tables each make about themselves. |
| independent session required | `false` in the handoff, correctly — this is an authoring task. Its reviews of record are the batch's validator and red-team tasks. |

**Model-independence divergence from the batch plan — material, and it weakens
this record.** BATCH-ae07ce's `model_independence_note` and DEC-20260903-7548c0
both record that this batch's coordinator tasks would run on `fireworks/glm-5p3`,
a different family, expressly to repair BATCH-241d37's model independence of
zero. **This task did not run on that model.** It resolved to `claude-opus-5` —
the same model that authored -003 and -004, the same model that authored
RT-20260901-3ad5d2 whose four objections this text answers, the same model that
froze the panel, and the same model that produced the verdict tables. The
cross-family independence this batch claimed is not realised here either, and no
later record may read this amendment's agreement with -004 on any point as
corroboration. It is the strongest reason to treat §2(a)'s resolution with
suspicion, which is why the amendment states that suspicion itself.

---

## 9. What a reviewer should attack first

1. **A5-3's precomputation limb** (§4, PT-A1). It is the largest change in the
   record and the one that buys RC-1 invariance. If a one-time
   specification-time cipher-structural operation should *not* bar the route,
   this clause is wrong and PT-A1's pass is bought at too high a price.
2. **B5-3's restriction to candidate-KEY sets** (§4). It is the only reduction
   in charge in the record. Test whether it opens a laundering route that
   element (c) does not close.
3. **B5-3's "evaluates part of AES-k" boundary** (§3, residual 2). This is where
   a description can still move a classification.
4. **The SPEC-10 resolution** (§2(a)). It agrees with an author of the same model
   family as this author. The unrun -005 column is what would test it.

## 10. Status

The amendment is **uncommitted and therefore not yet durable**. It becomes part
of the frozen cost model as amended only once an isolated snapshot archive
commits these bytes, the post-commit verifier accepts the receipt, and the branch
is pushed with a PR against `main` naming the record. This task did not commit
and was forbidden to. It closes no objection, changes no status, approves
nothing and promotes nothing: those are Coordinator decisions resting on
committed records, and this is not one.
