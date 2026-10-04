# independent_act_check.md — TASK-20260906-918585

My own working record for the independent review of the red team act pass
(TASK-20260906-dc4905) of BATCH-314308, on joints J1–J4 of
`coordination/goals/GOAL-SSI-001/batches/BATCH-314308/review_plan.yaml`.

**THIS FILE IS WEAKER THAN A RE-RUNNABLE SCRIPT AND I SAY SO.** This round's
product is an argument, not a computation. Almost nothing here has an exit code.
What this file buys instead is that a successor can re-check every J2 conclusion
against committed bytes without re-running anything: per act-finding, the key
path I opened, the words I found there, and my verdict. The three scratch
scripts I wrote (`proc.py`, `splice.py`, `quotes.py`) live **outside the
repository** and are not committed, so their results are re-derivable but not
re-runnable from any artifact of mine. That is CF-24's discharge for this round
and it is a lesser one.

**Citation prohibition, restated verbatim, lifted neither limb:**

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**.
> This task does not lift that prohibition. Only a committed Coordinator decision
> on independently reviewed evidence can lift it.

> In addition to the retained sentence, a row of any EXP-WESOVOW-001
> reconciliation is NOT citation-eligible when either (a) the two anchors disagree
> in the SIGN of the baseline comparison at that row, or (b) the smaller |margin|
> across the two anchors at that row is below that field size's anchor gap
> |Delta log2 T_full + Delta log2 M / 2|.

No crossover value, baseline-comparison sign, margin, speedup or PAPER_PAIRS
value or delta is stated anywhere in this file. Everything is named by locator.

---

## 0. Package binding I verified myself before reading anything of the producer's

| check | result |
| --- | --- |
| `sha256sum` of the three producer artifacts vs `archives/TASK-20260906-51fec3/snapshot_commit_receipt.json` `producer_artifact_sha256` | all three MATCH |
| `git show --name-status 1e161dd49fc1459c9c5c000db20f7a469acb2481` | exactly 4 paths, all `A`: the three producer artifacts + the snapshot receipt |
| parent of `1e161dd4` | `51c3d202acd7cd9ada7c1896cccdb5ffedaf2865` — matches the receipt's `parent_sha` |
| blob at commit vs blob in worktree, per producer artifact | identical for all three (`git rev-parse <sha>:<path>` == `git hash-object <path>`) |
| `git merge-base --is-ancestor 1e161dd4 HEAD` | YES; HEAD at review time `1178420e625b842024e2f7f2fae77c6981d69dc3` |
| `git status --porcelain` over `experiments/ inputs/ BATCH-752ef2 BATCH-79a0cb BATCH-60d6b9 BATCH-314308/tasks` | empty |

I did not take any of this from my launching prompt. The dispatch precondition
of my task card is satisfied: I am reviewing a committed, immutable package.

One receipt observation, recorded and **not** repaired: `commit_sha` in the
snapshot receipt is `null` by construction (the receipt is inside the commit it
describes) and points at `dispatch_queue.json` `tasks[TASK-20260906-51fec3].archive`
for the authoritative binding. That queue file at HEAD does not yet carry an
`archive` block for that task; the binding I actually verified is the
content binding (three digests) plus the commit's exact four-path scope, which
is the stronger of the two under CLAUDE.md "Archive receipts bind to CONTENT
first". Informational.

---

## 1. THE ATTESTED ORDERING — what I did and in what order

**I produced my own inert-object and twin-object results BEFORE opening
`tasks/TASK-20260906-dc4905/entailed_control_objects.yaml`.** Recorded as an
attestation, not a tool result, and it is weaker than a mechanically checkable
`blind_from` list. Nothing was forbidden to me at any time; this batch declares
no blind phase.

Order actually followed:

1. Read task card, queue handoff, `batch.yaml`, `review_plan.yaml`, AGENTS.md,
   CLAUDE.md, `agents/validator.md`.
2. Verified the snapshot binding (§0).
3. Read **only** `red_team_report.the_procedure_i_ran` — the seven steps S1–S7 —
   from the producer's report, to obtain the procedure I was to apply unchanged.
4. Read the redraft in full and the frozen `specification.yaml`.
5. **STAGE A** — applied S1–S7 myself to the INERT object and to the TWIN
   object. Recorded below at §2 and §3. *At this point I had not read the
   producer's `findings` list.*
6. Read the producer's `findings` (AF-1…AF-7).
7. **STAGE B** — my own twin-survival verdict for each AF. Recorded at §3.2.
   *Still before opening the producer's `entailed_control_objects.yaml`.*
8. Opened `entailed_control_objects.yaml` and compared. Divergences at §3.3.
9. J2 byte checks (§4), understatement search (§5), J1 classification (§6),
   J4 scope table (§7).

---

## 2. THE INERT OBJECT — my own result

Object: `coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/tasks/TASK-20260906-0fbf69/run_provenance_attestation.yaml`
(1349 lines). Predicate known FALSE for it: *"this record would bind a party,
foreclose an option, or mislead a reader of a green control about an amendment."*

**S1 — enactability gate: NO.** I ran a mechanical scan (my `proc.py`,
outside the repository) over every string of the flattened document, looking for
an operation word (`replace|add|remove|amend|supersede`) co-occurring with a file
path and a locator token. **Exactly one candidate** came back:
`runs[1].summary_verdict_statement`, matched on `add` inside "first-**add**
commit" and on "clause" inside "the dirty_summary **clause**". I read it in full
and **rejected** it: it is a provenance verdict about two run manifests, not an
operation on an artifact at a locator. Corroborating bytes:
`record_class: provenance_attestation_from_committed_artifacts_and_git_history_only`;
`what_this_record_is_not[0]` = "NOT an adjudication of either run's evidential
status". No replacement text, no target line range, no splice, no version
transition.

→ Gate not tripped. Under the procedure as written, S2–S4 return nothing.

**UNGATED CROSS-CHECK — mine, and stronger than the procedure requires.**
The obvious attack on this result is that *all* the specificity sits in one
binary reading of S1. So I ran the S3 machinery anyway, with the gate removed.
Six normative-verb-bearing strings out of 1349 lines:

| key path | verb |
| --- | --- |
| `citation_prohibition.discharging_cf_9_lifts_nothing` | may not |
| `runs[1].limbs[1].the_named_residual.what_would_close_the_residual` | is forbidden |
| `runs[1].what_would_change_this_verdict` | requires |
| `limitations_of_this_attestation[1]` | must |
| `limitations_of_this_attestation[4]` | must |
| `limitations_of_this_attestation[5]` | requires |

I read all six. **None** imposes a requirement on any party by force of this
record: they state a standing prohibition, the conditions under which a *future*
attestation would upgrade, and reader caveats. S3's own test — "name the SUBJECT
the text addresses, and separately the party who would in practice have to
comply" — has no subject in any of the six.

**S4:** the record introduces no invariant, pointer or requirement on an external
artifact. Candidate foreclosure considered and rejected at the bytes: recording
RUN-WESOVOW-001's provenance UNATTESTABLE does not foreclose citing that run —
`what_this_record_is_not[0]` and the closing statement say the opposite in terms.

**S5:** axis A4 asks what a reader of a green parse control would wrongly
conclude **about an amendment**. The inert object has no amendment and no parse
control over an amended document. Nothing to return.

**MY INERT RESULT: 0 act-findings, at any severity.** The procedure does not fire
on an object for which the predicate is known false — and it still does not fire
when its gate is removed, which is a stronger statement than the producer needed
to make and which I obtained independently.

---

## 3. THE TWIN OBJECT — my own result

Object: `coordination/goals/GOAL-SSI-001/batches/BATCH-752ef2/tasks/TASK-20260905-28c89d/protocol_amendment_draft.yaml`.
Predicate known FALSE for it: *"this is a live proposed act."*

### 3.1 STAGE A — S1–S4 applied de novo (before I read the pass's findings)

**S1: PARTIAL.** The twin declares the same operations on the same external
artifact at the same locators; its clause_1 has no applicable text (established
at three candidate columns by three sessions), so the gate fails for clause_1 and
trips for clauses 2–4, which do splice and parse.

**The mechanical comparison I ran myself** (`yaml.safe_load` of each clause's
`replacement_text_in_full`, then key-by-key string equality):

| clause / key | twin vs redraft |
| --- | --- |
| `clause_1` whole text | DIFFERS — **whitespace only**, 8 continuation lines two columns deeper |
| `clause_2` whole text | **BYTE-IDENTICAL** (2157 chars both) |
| `clause_3.what_the_five_pairs_are` | DIFFERS (blind-phase sentence deleted) |
| `clause_3.what_C1_is_and_why_its_test_is_two_sided` | IDENTICAL |
| `clause_3.serialization_requirement` ("THE OPERATIVE CLAUSE") | **IDENTICAL** |
| `clause_3.deviation_sign_note` | **IDENTICAL** |
| `clause_3.tolerance_statement_note` | NEW IN REDRAFT |
| `clause_4.requirement` (the reachability requirement) | **IDENTICAL** |
| `clause_4.why_it_is_required` | DIFFERS (RT-9(b): hypothetical) |
| `clause_4.licensing` | DIFFERS (RT-4 provisos carried in) |
| `clause_4.licensing_provisos_are_operative` | NEW IN REDRAFT |
| `clause_4.fuller_statement` | NEW IN REDRAFT |
| `clause_4.relation_to_the_standing_citation_prohibition` | IDENTICAL |

**My prediction, written before I read the pass's findings:** any act-finding
anchored at `clause_2` (any key), `clause_3.serialization_requirement`,
`clause_3.deviation_sign_note`, `clause_4.requirement` or
`clause_4.relation_to_the_standing_citation_prohibition` **survives verbatim on
the twin and is a CLASS finding.** Findings anchored at
`clause_3.tolerance_statement_note`, `clause_4.licensing_provisos_are_operative`,
`clause_4.fuller_statement`, `amendment.splice_procedure`, `amendment.supersedes`,
`amendment.controls`, `amendment.changes_from_the_superseded_draft`,
`amendment.reserved_to_the_enacting_decision`, `amendment.gating_reproduction`
are INSTANCE findings: those blocks do not exist in the twin.

**My own de novo twin findings:** the same class-level ones (clause_2 incorporates
a law by reference into a coordination directory; clause_3/clause_4 make the one
existing implementation non-conforming), plus one instance finding the redraft
does not have — the twin's clause_1 is not applicable, so an enacting decision
acting on it would have no applicable text for its primary target.

### 3.2 STAGE B — my own survival verdict per AF (still before opening the producer's file)

| AF | my verdict | the twin bytes I checked myself |
| --- | --- | --- |
| AF-1 version transition | **SURVIVES → CLASS** | twin `version_to: 2`; twin line 444 carries "Version becomes 2 and every record produced before enactment stays scoped to version 1." verbatim; twin `enactment.what_would_be_required` carries "moves EXP-WESOVOW-001 to version 2"; twin has **no** `splice_procedure` block and no clause `operation` names spec line 3 |
| AF-2 prerequisite names a ledger archive | **DOES NOT SURVIVE → INSTANCE** | twin line 575 names `TASK-20260905-6fcd2c`, whose receipt `kind` is `snapshot`; the redraft names `TASK-20260906-9f3e2a`, whose receipt `kind` is `ledger`, `binding_mode: content_first`; BATCH-60d6b9 has exactly one `archives/` directory |
| AF-3 only source of law is an unopened pointer | **SURVIVES → CLASS** | clause_2 byte-identical, clause_1 identical modulo indentation |
| AF-4 unmeetable requirement + unsubjected prohibition | **SURVIVES IN PART → MIXED** | `clause_4.requirement` and `clause_3.deviation_sign_note` IDENTICAL (class), **but** AF-4's third quoted anchor `clause_4.licensing_provisos_are_operative` is NEW IN THE REDRAFT (instance) |
| AF-5 prerequisite list omits the companion | **SURVIVES IN PART** | twin's list has 3 items and also omits it; redraft added a 4th and still did not add this one |
| AF-6 `binding_effect` forecloses the control-is-wrong branch | **SURVIVES → CLASS** | clause_2 byte-identical |
| AF-7 operation line miscounts C1's keys | **SURVIVES + instance aggravation** | twin `clause_3.operation` reads "add two keys alongside the existing four" and is also wrong — its clause_3 adds ONE top-level key, `anchor_semantics` |

My tally: 5 class, 1 instance (AF-2), AF-7 class miscount with instance
aggravation. Strictly smaller than and differently classed from the redraft's
set, which is what the plan's failure signature requires of a non-vacuous twin.

### 3.3 Where my results differ from the producer's `entailed_control_objects.yaml`

Opened after the above. **Six of seven survival rows agree exactly**, including
the two I regarded as decisive (AF-2 non-survival; AF-1 survival-with-live/inert
asymmetry). The producer additionally ran the known-false-attribution object, the
green-control reader object and the positive control, which I re-checked rather
than re-ran (§7).

**DIVERGENCE 1 — AF-4's class label is too broad (mine, informational).** The
producer labels AF-4 flatly `CLASS FINDING` with no
`what_is_nevertheless_instance_level` field (it supplies that field for AF-1,
AF-5 and AF-7). Its cited evidence is accurate as far as it goes. But one of
AF-4's own four quoted anchors — `clause_4.licensing_provisos_are_operative`,
"The two conditions stated in capitals above … are CONDITIONS ON THE LICENCE and
not commentary" — **does not exist in the twin at all**. The "conditions on the
licence" limb of AF-4 is therefore instance-level. The direction of the error is
conservative: the pass under-attributes to the instance rather than attributing a
class property to an instance, which is the direction the failure signature calls
a break. Smaller repair: a successor record adds a
`what_is_nevertheless_instance_level` line to that row. **Not repaired by me.**

**DIVERGENCE 2 — my ungated cross-check on the inert object is additional, not
contradictory.** The producer names `discharges: CF-9` as the near-miss where a
looser gate would have fired, and says S1's gate is where its specificity is
purchased. I agree, and I add the result it did not obtain: with the gate
*removed*, S2–S4 still return nothing on the inert object (§2). That strengthens
its claim by a route it did not take.

---

## 4. J2 — every act-finding checked against the redraft's own bytes

Method: I resolved each quoted string to its named key path in
`BATCH-60d6b9/tasks/TASK-20260906-ee372e/protocol_amendment_redraft.yaml` by
`yaml.safe_load` in a scratch script outside the repository, whitespace-normalised
both sides, and tested containment. **23 of 23 quoted strings resolve and are
present at the key path named. Zero key-path breaks. Zero misquotations.**

I also rebuilt the amended document myself, in memory, with my own splice code
(not by importing the producer's control), bottom-up under the redraft's own
`splice_procedure`.

| finding | key path(s) I opened | what I found there | verdict |
| --- | --- | --- | --- |
| **AF-1** | `amendment.version_to`, `.version_note`, `.blast_radius.frozen_artifacts[0].effect`, `.enactment.what_would_be_required`, `.splice_procedure.{clause_1,clause_2,clause_3_and_clause_4}.operation` | all present verbatim. Spec line 3 reads `  version: 1`. No clause `operation` names line 3. **My own splice gives `experiment.version == 1` in the amended document**, and the amended `experiment` key set is identical to the frozen one. Corroborated, not derived, by the committed `structural_diff_frozen_vs_fully_amended` (5 differences, none `.experiment.version`) | **CONFIRMED at the bytes.** Follows from the text alone. The party addressed is nobody, which is the defect |
| **AF-2** | `amendment.enactment.prerequisites_before_such_a_decision[1]` | reads "the snapshot archive of this package (TASK-20260906-9f3e2a)". `BATCH-60d6b9/archives/TASK-20260906-9f3e2a/ledger_commit_receipt.json` carries `"kind": "ledger"`, `"binding_mode": "content_first"`; that is BATCH-60d6b9's only `archives/` entry | **CONFIRMED at the bytes**, and I checked the receipt myself rather than through the report. The mislabel follows from the text; the *consequence* needs the enacting decision, which the pass states |
| **AF-3** | `clause_1.replacement_text_in_full`; `clause_2.replacement_text_in_full` key `incorporated_by_reference` | both quotes present verbatim. **My own splice** lists `model_definition.vow_charging_law` keys as `[status_in_this_contract, incorporated_by_reference, invariants_that_any_incorporated_law_must_satisfy, binding_effect, notation_note]` — **no charging law and no closed form is stated there**; clause_1's "stated once … and nowhere else" is true only transitively | **CONFIRMED at the bytes.** I did not open BATCH-2e6130 either — it is outside my read_scope, so I confirm the *structure* and not the pointer's target |
| **AF-4** | `clause_4.replacement_text_in_full` keys `requirement` and `licensing_provisos_are_operative`; `clause_3…deviation_sign_note`; `blast_radius.frozen_artifacts[3].effect`; `scope.budget` | all present verbatim. `cost_model.py:302` **read as text** emits `"paper_pair": {"log2time": pt, "log2memory": pm}` — keys naming only a time and a memory, no relation, no unit, no locator, no status. The narrowing the pass discloses is real: `BATCH-752ef2/tasks/TASK-20260905-28c89d/category_and_licensing_analysis.yaml:226-227` **does** record per-field statuses (I read the lines; I do not restate the statuses) | **CONFIRMED at the bytes.** The disclosed self-correction is accurate and checkable, which is the strongest single honesty signal in the package. Subject analysis on `deviation_sign_note` is correct: the sentence is an unsubjected passive |
| **AF-5** | `reviewer_notes.known_weaknesses_of_this_draft[1]`; `cf_10_raw_path_placement.answer`; `enactment.prerequisites_before_such_a_decision` | quotes present verbatim; the four prerequisites do **not** include the companion record's existence | **CONFIRMED at the bytes.** Follows from the text alone: a ruling on placement and the companion existing are different things |
| **AF-6** | `clause_2.replacement_text_in_full` key `binding_effect` | present verbatim | **CONFIRMED at the bytes.** The foreclosure of the control-is-wrong branch follows from the sentence; the pass correctly declines to assert the sentence is wrong |
| **AF-7** | `clause_3.operation`; `clause_3.changed_from_the_superseded_draft`; `changes_from_the_superseded_draft.items[6]` | quotes present verbatim. **My own splice**: frozen `controls[0]` has 4 keys; amended `controls[0]` has **6** — `anchor_semantics` (5 sub-keys) from clause_3 and `anchor_reachability` (6 sub-keys) from clause_4. The operation line's arithmetic (4+3, then +1) predicts 8 | **CONFIRMED at the bytes.** But see §6: I classify this as integrity-wearing-an-act-header, not as an act on the contract |
| **A4-1** | control report `defect_found_in_this_control_during_its_own_development` | the recorded near-miss is real and is the same shape as the candidate | CONFIRMED |
| **A4-2** | — | this is AF-1 seen through the control; not an independent finding | CONFIRMED as a restatement of AF-1 |
| **A4-3** | frozen `experiment.metrics` | **I parsed the frozen file myself: `metrics[4]` IS a single-key mapping** (`['per (p, w, overhead c)']`) and `metrics[5]` is too; the frozen file already satisfies P2 and P3 | CONFIRMED, and independently reproduced rather than taken from CF-27 |
| **A4-4** | `reviewer_notes…[3]` | self-disclosure, and the pass classifies it as one and rates it informational | CONFIRMED |

**Overstatement search: none found.** No finding claims an effect the text does
not carry; every finding that needs a further decision names it (AF-2's
consequence, AF-4's two standing conditions).

**DEC-20260906-408595 PD-9 discharge:** the pass filed
`clause_text_confirmation_against_the_file` confirming all four clause texts at
the file; I confirmed clause_1 (and the other three) against the file myself by
`sed` and by splice. PD-9's standing gap is closed on the pass's half and on
mine; it remains owed by the enacting decision.

---

## 5. THE UNDERSTATEMENT HALF — one act the redraft's text plainly effects that the pass did not report

**FINDING U-1, severity medium.**
**Key path: `amendment.proposed_replacement.clause_4.replacement_text_in_full`, key `licensing`.**

What the bytes say there, verbatim:

> An `off_curve` status **LICENSES** two things and no more. FIRST, reporting the
> anchor as the source's stated lower bound for that field size, CITED BY LOCATOR
> AND CARRYING ITS RELATION AND ITS UNIT — a bare number is not licensed. SECOND,
> comparing this model's attained value against it and reporting the signed
> difference, PROVIDED THE REACHABILITY STATUS IS REPORTED IN THE SAME BREATH AS
> THE DIFFERENCE — a signed difference emitted without its status is not licensed.
> It also licenses C1's instrument-sanity verdict, read alongside that status. An
> `off_curve` status **FORECLOSES** treating the anchor as an admissible
> (T_full, M) input to this model at that field size, **and forecloses citing any
> row derived from it as a cost, a speedup or a crossover of this model.** A
> `reachable` status licenses using the anchor as a model point at that field
> size, and licenses NOTHING about the field sizes where the status is `off_curve`.

**What I checked, mechanically:**

* `amendment.what_this_changes` — 9 items. Regex `licen|foreclos`, case-insensitive: **zero hits.** Items [6] and [7] report only the *implementation* limbs ("Implementations become required to serialize…", "…to record, per field size…").
* `amendment.blast_radius` (whole block, JSON-serialised) — contains **neither** the substring `forecloses` **nor** `licens`. The closest item, `controls_whose_meaning_changes[3]`, says the object "this pair is an admissible (T_full, M) input to this cost model" *gains a contract-level place to be recorded* — a place to record, not a foreclosure.
* The producer's report — the words "licence"/"licensing" appear only in connection with the two **provisos**; the FORECLOSURE limb appears in no finding, and axis A3's negative sweep enumerates four categories of foreclosure it did not find, none of which covers this one.
* Whole-repository grep for `forecloses citing any row derived`: **two hits, both amendment drafts.** No committed report, decision, evidence record or knowledge entry names it.

**Why it is an act and not a reading.** On enactment this becomes contract text.
The amended contract would, for the first time, **grant a licence** and **impose a
foreclosure** on how model output may be cited, keyed on a per-field reachability
status. Both are clause effects. Under the pass's **own** S2 rule — "A clause
effect outside the claimed set is a finding" — and on its **own** foreclosure axis
A3, this should have been returned. It was not.

**What I do NOT claim.** I do **not** claim clause_4 lifts, narrows or widens the
standing citation prohibition — `clause_4.relation_to_the_standing_citation_prohibition`
says it does not and I do not contradict a committed record. I do **not** settle
RT-4's licensing question, which is reserved. I state only that the licence and
the foreclosure are effects of the clause text and are absent from the record's
own declared effect set and from the pass.

**Class or instance, by my own discipline:** the twin's `clause_4.licensing`
carries the same foreclosure sentence and the twin's `what_this_changes` also
omits it. **U-1 SURVIVES ON THE TWIN and is a CLASS finding**, inherited from the
lineage; its live-ness is instance-level for exactly the enactability reason
AF-1 and AF-3 turn on.

**Smaller repair, RECOMMENDATION and not a ruling:** the enacting decision names
clause_4's licence and its foreclosure limb explicitly among the effects it
enacts. A successor record — never an edit of the immutable redraft — may add
the item to `what_this_changes`.

**Entailment honesty about U-1.** My launching prompt and my task card told me to
read clause_3 and clause_4 in full and to read `blast_radius`,
`what_this_changes` and `scope` against them. The **method** was handed to me and
I disclose it. The specific gap is mine, is anchored at one key path, and is
decidable by a successor in two commands.

### Understatement candidates I pursued and **rejected**

* **`what_this_changes[8]` / `blast_radius.committed_records_whose_reading_changes[0]`** — that on enactment CF-1 becomes dischargeable and EV-SSI-5d954c observations 1 and 2 "become historical rather than live", i.e. an amendment changing how an immutable evidence record reads. **Rejected as a defect.** `blast_radius.statement` carries an explicit theory for this class ("None of their bytes change… What changes is the contract version they must henceforth be read against"), and I checked the two observations at `ledger/evidence/EV-SSI-5d954c.yaml`: observation 1 is a statement about what the frozen file still carries and observation 2 about the joint unsatisfiability, both of which clause_1 does discharge. So the claimed reading change **does** follow from a clause, unlike AF-1's version claim. It is also already touched by OP-4 of the BATCH-79a0cb report. Recorded because the review plan named it as its item (3) and would otherwise read this silence as a coverage gap: **I looked, and there is no defect here.**
* **clause_1's "This metrics list names reported quantities and their units and states no law"** — an assertion about the whole metrics list, of which [0..4] and [6] are untouched. **Rejected:** I read all seven metrics entries at the frozen file; none of the other six states a law or a closed form. The sentence is true of the amended list.
* **clause_1's "…and nowhere else"** — **Rejected:** `model_definition.quantities` (spec:58–70) states laws for log2X, w, log2Psi, log2M, u, log2P0 and log2Tfull but **not** for T(w); C3 and C4 state *properties* of T(w), which clause_2 itself treats as invariants rather than as statements of the law. No contradiction.
* **`amendment.scope.budget`** — asserts the budget is unchanged and no clause touches `experiment.budget`. Consistent.

**Where I looked, exactly:** `proposed_replacement.clause_3` and `.clause_4` in
full, key by key; `amendment.blast_radius` (all five sub-blocks);
`amendment.what_this_changes` (9 items) and `.what_this_does_not_change` (12
items); `amendment.scope` (5 keys); `amendment.enactment` (4 sub-keys);
`amendment.reserved_to_the_enacting_decision`; `amendment.cf_10_raw_path_placement`;
`amendment.controls`; `amendment.target`; `amendment.splice_procedure`;
`amendment.reviewer_notes`; and the frozen `specification.yaml` at lines 30–60,
58–107 and 133–160.

---

## 6. J1 — my classification of every result

Buckets: **(a)** act · **(b)** integrity wearing an act header · **(c)**
restatement of a numbered record · **(d)** draft self-disclosure read back.

| result | pass's own label | **my** classification | note |
| --- | --- | --- | --- |
| AF-1 | ACT (A1) | **(a)** | claimed effect on the target with no clause effecting it; the integrity round had the diff and did not draw the act consequence |
| AF-2 | ACT (A2) | **(a)**, process-level | about the record's operative guidance to the enacting act, not about contract text |
| AF-3 | ACT (A1) | **(a)** with (d) adjacency | `reviewer_notes[0]` confesses the pointer's weakness; the act-framing and the three-rounds-of-scope observation are new |
| AF-4 | ACT extending a DRAFT SELF-DISCLOSURE | **(a)+(d)**, as labelled | correct and honestly labelled |
| AF-5 | ACT (A2) | **(a)**, process-level | overlap with `batch.yaml` disclosed by the pass itself |
| AF-6 | ACT (A3) | **(a)** | new; adjacency to RT-6 named rather than borrowed |
| AF-7 | ACT (A1) | **(b)** with a real act consequence | **my one classification disagreement.** The `operation` line never becomes contract text and the amendment applies correctly regardless; the effect on `specification.yaml` is nil. Its consequence — a verifier checking the line's arithmetic would expect 8 keys and find 6 — is real and downstream. Severity `low` is honest; the axis label is not |
| A4-1 | ACT (A4) | **(a)** | the campaign has an actually-occurred instance of the failure |
| A4-2 | ACT (A4) | **(a)**, but = AF-1 on a second axis | not an independent result |
| A4-3 | ACT (A4) | **(a)/(c)** | rests on CF-27, which `batch.yaml` named to the producer — **but** the pass reproduced it from its own parse and so did I |
| A4-4 | DRAFT SELF-DISCLOSURE | **(d)**, as labelled | correctly rated informational |

**Act-finding count per axis, my classification:** A1 = 2 (AF-1, AF-3);
A2 = 3 (AF-4's subject analysis on the text; AF-2 and AF-5 at process level);
A3 = 2 (AF-4, AF-6); A4 = 1 genuinely independent (A4-1), plus A4-2 duplicating
AF-1, A4-3 and A4-4.

**NO UNCOVERED AXIS.** No axis rests entirely on buckets (b), (c) or (d).
A4 is the thinnest: of its four results, one duplicates AF-1, one is (d), and one
leans on a carried-forward item — leaving A4-1 as its single independent act
result. That is coverage, not vacuity, and I report the thinness rather than
letting the count of four stand unqualified. The Coordinator's prior predicted at
0.5 that A4 would be the weakest axis; on my reading it is the weakest, **and it
is still covered**.

**THE STEER CHECK.** `batch.yaml` `key_paths_named_to_the_producer` lists nine
key paths. AF-1's load-bearing blocks (`amendment.version_to`, `.version_note`,
`.splice_procedure`) and AF-7's (`amendment.changes_from_the_superseded_draft`)
are **not** among the nine. **The pass was not steered.**

One accuracy defect in the pass's own steer claim, severity low: its
`is_my_finding_set_entailed_by_its_own_construction.by_my_launching_prompt` says
"AF-1, AF-2 and AF-7 rest on blocks the nine-path key-path list does not name."
**AF-2's sole key path is `amendment.enactment.prerequisites_before_such_a_decision[1]`,
and the list names "amendment.enactment (including prerequisites_before_such_a_decision)"
explicitly.** AF-2's *content* came from outside the list — from two archive
receipts the list does not name — but its *block* is named. The pass overstates
its own unsteeredness by one finding. Smaller repair: one word in a successor
record. **Not repaired by me.**

---

## 7. J3 — the other two sources of entailment, and the other three control objects

**By the prompt.** The producer's receipt discloses ten verbatim statements from
its launching prompt. The load-bearing one is *"That round returned zero blocking
findings and it is committed"* — a statement about how a previous agent concluded,
received before it looked. The producer names it as the contamination it cannot
unlearn. The prompt named **no** suspected defect, **no** expected finding count
and **no** weakest key path, and the producer records that it did not open
`review_plan.yaml`. On the evidence available to me the separation held: the
Coordinator's prior element (5) — that the procedure would fire on the inert
object — is **overturned**, and its element (2) — that the pass would return the
draft's own confession about non-conforming implementations — is only partly
realised, because AF-4 extends the confession with a predicate analysis rather
than reading it back.

**By the campaign record.** No finding is a relabelled RT-, F- or V-number. I
tested this rather than accepting it: I grepped `version_to|version_from|Version
becomes|experiment.version` across the BATCH-79a0cb red-team report, the
BATCH-60d6b9 validation report, EV-SSI-804e09 and DEC-20260906-408595 — **the
version field appears in none of them**, so AF-1 is genuinely new. AF-2's key
path is touched by V-3 only as a completeness point about the change enumeration,
which I read; the content is new. AF-6's adjacency to RT-6 and AF-7's to V-3 are
named by the pass rather than borrowed.

**The known-false attribution object (c).** I re-checked all three at the file
rather than through the report: C4 at `specification.yaml:148-149` versus
clause_2's second invariant — the qualifier "before the declared overhead
multiplier" is in the clause and absent from C4, and
`reserved_to_the_enacting_decision.items[0]` says the draft "CARRIED THE TEXT
UNCHANGED AND DECIDED NOTHING" (RT-6 **unresolved**); clause_3's
`what_the_five_pairs_are` carries "AN ENACTING COORDINATOR SHOULD CONFIRM THE
LOCATOR AGAINST THE FILE BEFORE ENACTMENT" word for word and nothing extends it
to the characterization (RT-9(a) **unresolved**); `gating_reproduction` reports a
verdict and a witness and does not adopt the bare word "unsatisfiable" (RT-12
**neither adopted nor rejected**). The pass reports all three UNRESOLVED. **No
break.**

**The green-control reader object (d).** The pass enumerated eight candidates and
reports **four killed by checking against committed artifacts** — including the
two the review plan itself pre-identified as breaks if raised. I verified the
kill for "the control's pass is entailed by its construction" independently: I did
not need to re-run the selftest because the redraft's own
`controls[0].negative_objects_it_was_exercised_on` declares five objects of which
four must FAIL, and the frozen file's `metrics` list (7 items, item 5 a single-key
mapping) shows why only P4 discriminates — which I parsed myself. **No break.**
The 4-of-8 kill rate is the single best evidence in the package that the candidate
list was not entailed.

**The positive control (e).** The procedure fires on the redraft: 7 act findings
plus 4 green-control over-readings. **Not silent.**

**Is the finding set entailed?** The producer answers "YES, PARTLY" and shows its
work per source. My independent test agrees, with the one accuracy defect at §6
and the one class/instance divergence at §3.3. **The pass anticipated the
class/instance separation by itself and labelled every survivor.** Under the
review plan's own terms that overturns the Coordinator's recorded prior element
(5) and is a better outcome than confirming it. I state it plainly.

**Is my round entirely re-confirmation?** No — and I record the ratio honestly.
Re-confirmations: 23 quote checks, the amended-document version, the amended
`controls[0]` key count, `metrics[4]`'s shape, the two archive receipt kinds, the
twin's clause-level identity table, the adapter resolution. Genuinely new to the
campaign record: **U-1** (§5), the ungated inert-object cross-check (§2), the
AF-4 class/instance divergence (§3.3), the AF-2/nine-key-paths accuracy defect
(§6), and the two control-plane observations at §8. My agreement with any RT-,
F- or V-number is **not** independent of the reports I was given, and blindness
was lifted for me by name.

---

## 8. J4 — item by item

| item | verdict | what I checked |
| --- | --- | --- |
| (i) approved or enacted anything? | **CARRIED** | The report's own header lines 5–9 state EXP-WESOVOW-001 is UNAMENDED at version 1 and the redraft remains `status: draft`, `in_force: false`, `approved_by: null`; limitations[2] repeats it. I confirmed the three redraft fields are as committed and that `git status` over `experiments/` is empty. `narrowest_supported_statement` says "I approve nothing, I enact nothing" |
| (ii) settled any of the five reserved items? | **CARRIED** | `material_for_the_five_reserved_items_ALL_LABELLED_RECOMMENDATIONS` opens "I SETTLE NONE OF THESE". CF-10: recommendation only; the `travels with` authority limb is expressly left. F-7: the pass checked the qualifier is in the same sentence and asked for no change. F-2/F-3/CF-22: it read the R3 warrant sentence and **declined to evaluate the antecedent**, stating that a check would require a governed baseline-comparison sign. RT-6/RT-9(a)/RT-12: all three reported UNRESOLVED and re-checked at the file. **RT-4: it says in terms "THAT IS THE CARRYING, AND CARRYING IS NOT SETTLING"** and offers no recommendation on the licensing question. I looked specifically for a recommendation phrased as a ruling: `required_controls` is a template field of `agents/red-team.md`, not a self-chosen word, and every entry inside it is tagged RECOMMENDATION |
| (iii) lifted, narrowed or widened either prohibition limb; stated a governed sign, crossover, margin or speedup? | **CARRIED** | Scanned all three artifacts for decimals `\d+\.\d+`: **zero matches.** Digit runs ≥3 are identifiers, line numbers, dates, digest fragments and the budget. Every occurrence of `P=512`, `w=2^80` and "crossover value" is inside the restated prohibition sentence itself. The one place it could have fired — the R3 warrant antecedent `A > 0`, which **is** the governed sign — is named and **not evaluated**. Its one symbolic check is an identity between two quoted committed expressions with nothing instantiated |
| (iv) executed `cost_model.py`? | **CARRIED** | The receipt says read-as-text only, four ranges, never executed with or without `WESOVOW_RAW_PATH`, and discloses a redaction filter over the PAPER_PAIRS range. I read `:302`, `:239` and `:288-289` as text myself and confirm the blast-radius locators are accurate; **I did not execute it either** |
| (v) edited a frozen or immutable artifact? | **CARRIED** | `git status --porcelain` over `experiments/`, `inputs/`, BATCH-752ef2, BATCH-79a0cb, BATCH-60d6b9 and the producer's task directory: **empty**. The commit `1e161dd4` added exactly four paths |
| (vi) asserted a committed immutable record is wrong? | **CARRIED** | limitations[8] leaves the stronger claim UN-PROMOTED and names IMP-1; `the_stop_condition_did_not_fire` records that the pass did **not** conclude the underlying defect fails to reproduce |

### Two control-plane observations, neither a defect of the producer

**CP-1 (informational).** `review_plan.yaml` J1 and `batch.yaml`
`entailed_control_analysis.what_would_make_this_producers_output_vacuous` both
say the redraft's `reviewer_notes.known_weaknesses_of_this_draft` "names **four**
weaknesses". The file names **five** (items [0]–[4]); the producer counts five
and is right. A control-plane count wrong against the bytes. Reported as a
divergence of the control plane, per the plan's own instruction, and **not
repaired.**

**CP-2 (informational, and it bears on J4).** The producer escalated an
inference-provenance divergence rather than absorbing it:
`batch.yaml` `inference_environment.resolvable_backends: local only` — expressly
labelled an ASSUMPTION carried from IMP-1 — against an adapter resolution naming
`anthropic:claude-opus-5`. **I reproduced its factual basis myself**:
`python3 -m orchestration.adapter resolve --role red-team --independent-session`
returns `review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)` at exit 0,
and the same command without the flag returns the policy's independence error.
Escalating rather than absorbing is the **correct** behaviour and I record J4 as
carried on it.

Two things I add, both mine:

1. **The divergence does not clear IMP-1 and must not be read as doing so.**
   `adapter resolve` reads the committed binding target for a policy; it contacts
   nothing and says nothing about servability. IMP-1's `clears_when` requires *a
   probe reporting at least two distinct resolvable backends*. So this is a
   documentation/assumption-labelling question, not evidence that a second
   backend resolves. **IMP-1 stands, un-downgraded; the CLAIM stays
   UN-PROMOTED; GOAL-SSI-001 stays `active`.**
2. **No committed record disposes of this escalation as of HEAD `1178420e6`.**
   `DEC-20260906-408595`'s `inference_provenance_ruling` addresses the *earlier*
   divergence (adapter resolution vs runtime self-report, escalated by CF-9) and
   was committed before this batch opened; it does not reach this one, and for
   this producer the adapter resolution and the self-report **agree**. My
   launching prompt told me the dispatching session "has since acted on" the
   escalation. **I could not verify that from committed state and I do not
   record it as done**; a message is a pointer, never a record. The disposition
   belongs in `DEC-20260906-f709b2` or a correction record, and IMP-1's named
   recheck `python3 -m orchestration.adapter doctor --probe` has been run by
   nobody in this batch. Recorded OUTSTANDING, never as passed.

---

## 9. The stop condition did not fire for me either

I did **not** conclude that the underlying defect fails to reproduce. I did not
investigate whether `specification.yaml:39-40` and control C4 are jointly
unsatisfiable off the degenerate slice — it is not my joint, I derived nothing
about it, and I state no value, no sign and no field size. I confirm only the
structural fact that the two blocks are in one scope: both are keys under the
single top-level `experiment:` mapping of the frozen file. Nothing here
contradicts EV-SSI-2aaf6f, nothing requires `review-breakthrough`, and the round
does not halt on that object.

## 10. What I did not accept from the reports I was given

* From the **producer's report**: no quotation. All 23 were resolved at the redraft's own key paths by me. Its twin-survival table: re-derived independently before I opened it, and I diverge on AF-4. Its A4-3 (`metrics[4]` is a single-key mapping): re-parsed from the frozen file. Its entailment self-analysis: tested, and one claim in it is inaccurate (§6).
* From the **BATCH-60d6b9 validation report**: I used `structural_diff_frozen_vs_fully_amended` only as corroboration; the amended document and the `version == 1` result are from my own splice, and the amended `controls[0]` key count is from my own splice.
* From the **BATCH-79a0cb red-team report**: I read it and located OP-4, which is why I rejected the EV-SSI-5d954c candidate as new. I re-derived the `cost_model.py:302` serialization shape myself rather than inheriting it.
* From **`batch.yaml` and `review_plan.yaml`**: I checked the "four weaknesses" count against the file and found five (CP-1), and I checked the nine-key-path steer list against each finding's anchors myself.
* From my **launching prompt**: I did not accept the snapshot commit, its parent or its four-path scope — I verified all three. I did not accept that the escalated inference question had been acted on — I looked and found no committed disposition (CP-2).
