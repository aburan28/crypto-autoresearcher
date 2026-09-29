# TASK-20260901-e045b8 — amendment-004 report

Worked classifications, rejected candidate rules, and the mandatory Gap B
proves-too-much demonstration for
`coordination/goals/GOAL-AES-002/amendments/protocol-amendment-GOAL-AES-002-004.yaml`.

- **goal** GOAL-AES-002 **question** RQ-AES-002 **batch** BATCH-241d37
- **role** coordinator **requested policy** `coordinator-orchestration-code`,
  reasoning effort `high`, `fallback_allowed: false`, `degraded_allowed: false`
- **model that actually answered** `claude-opus-5`, genuine self-report from this
  session's own runtime context ("You are powered by the model named Opus 5. The
  exact model ID is claude-opus-5."). Not copied from
  `orchestration/model-bindings.yaml`; this session cannot query its own backend,
  so the policy-to-model resolution is UNVERIFIED FROM INSIDE. No downgrade was
  taken and no fallback was used.
- **compute** ZERO. No benchmark, no sample, no run, no measurement of any kind.
  This session has no command-execution tool, so none was possible and none was
  attempted.
- **claim ceiling** SPECIFICATION ACT ONLY. Nothing here asserts anything about
  AES at any round count, states no margin, and makes no comparison against the
  published state of the art in either direction (SC-5, SC-6, SC-8).

---

## 0. What this task was asked to close, and what it deliberately did not touch

Two gaps, both established by the independent red team RT-20260901-1af5d9
against `protocol-amendment-GOAL-AES-002-003`:

- **Gap A** — objections[0] / `amendment_block_dispositions[0]`
  (`item_1_element_a_route_3`), MEDIUM, disposition **NEEDS REPAIR**: the word
  "independent" in Route 3's bar is undefined, and a fused T-table
  implementation is classifiable oppositely by two conforming readers.
- **Gap B** — objections[1] / `amendment_block_dispositions[1]`
  (`item_2_elements_c_f_joint`), MEDIUM: "genuinely distinct computational acts"
  is under-determined on its literal wording, and would classify the m=0
  definitional reference as unbundled — contradicting the same resolving text.
  The independent validator located the same edge case separately as
  **F-VAL4c225b-3** (LOW, "hybrid candidate-production pipelines").

Both reviews are **one draw from a correlated pair** under standing inference
basis 0137a051, so their agreement on Gap B is treated as two sessions, not two
models.

**Not touched, by instruction and by check.** `-003`'s
`item_3_element_d_two_axis_sublattice` (two-axis data sub-lattice) and
`item_4_elements_b_c_distinguisher_bridge` (separate distinguisher axis) were
attacked by the same red team and **HELD** (severity LOW with no verdict-level
split; and `concrete_reading_found: NONE`, INFORMATIONAL). No clause of
amendment 004 mentions, cites as governing, or alters either. `item_5` (the BC1
diligence supplement) is likewise untouched. `-003` itself was **not edited** —
amendment 004 is a separate file that supersedes three quoted sentence
fragments of `-003` and nothing else. `CM-1.yaml` was **not edited**.

**Named OPEN AND UNATTEMPTED (SC-9), recorded in the amendment as OU-1..OU-4:**
red-team objection 3 (element (d) mixed-kind *disclosure-content* gap) and
objection 4 (whether R7's matched random-permutation control must match the
distinguisher's data KIND, not merely its COUNT — **inherited from RQ-AES-002 R7
itself and out of any CM-1 amendment's scope**), plus the C2 design defects and
the still-unconfirmed S_k / X_k counts (O-CM1-4). None of these was tried,
screened, or found negative.

---

## 1. GAP A — the definition of "independent"

### 1.1 The candidate rule offered by the red team, TESTED and REJECTED

> "an operation is independent of the S-box route if and only if its cost is not
> already fully absorbed into a single memory access whose count is already being
> charged under Route 1."

Offered explicitly as a starting point, not a conclusion. I tested it against
the three implementations the task card names.

| implementation | what the candidate rule yields |
| --- | --- |
| fused T-table (one access = SubBytes + ShiftRows + partial MixColumns) | works as intended: the linear work IS absorbed into one charged access → not independent → admissible |
| **bitsliced** (S-box as a Boolean circuit) | **breaks**: there is NO memory access at all, so nothing is "absorbed into a single memory access whose count is already being charged under Route 1". On the plain wording every accompanying operation is independent → **INADMISSIBLE / UNADJUDICABLE** |
| **AES-NI** (`AESENC` as a register instruction) | **breaks the same way**: no memory access exists, so the antecedent has no referent → **INADMISSIBLE / UNADJUDICABLE** |

**Two independent reasons for rejection.**

1. **It does not terminate on two of the three implementations.** The rule's
   antecedent presupposes that Route 1's charge is a *memory-access* count. It is
   not. Under it, the most auditable implementation of all (bitsliced, no tables,
   no cache behaviour, fully data-independent) becomes inadmissible, which is a
   perverse outcome for a rule whose purpose is to stop implementation technique
   from moving a cost figure.
2. **It decides admissibility at the implementation level — the exact level CM-1
   already excluded.** CM-1's
   `element_a_unit.inadmissible_until_measured_stated_so_it_is_not_improvised`
   names all three by name: *"A T-table implementation, a bitsliced
   implementation and an AES-NI implementation do not agree on how many XORs or
   table accesses one encryption performs, so a conversion factor invented here
   would be a fabricated constant."* A rule keyed to memory accesses reintroduces
   into the *admissibility* test precisely the implementation dependence CM-1
   removed from the *charging* test.

The red team's **intent** — work already paid for is not charged twice and does
not void the route — is kept. What changes is the level at which the test is
applied.

### 1.2 The rule adopted (verbatim text in the amendment, clauses A-1..A-4)

- **A-1** N and X are counts of **specification-level operations the attack
  algorithm performs**, in the same sense in which S_k and X_k are
  specification-structure counts. Not instructions, accesses, lookups,
  registers, cache lines or gates. Classification and charged figure are
  **invariant under implementation technique**.
- **A-2** An operation is **independent** of the S-box route **iff the attack's
  own specification-level description requires its result**. (i) required →
  independent → inadmissible, *even if a particular implementation obtains it
  for free*; (ii) not required, arising only as a discarded by-product of how an
  implementation realises a charged S-box application → **not** independent, no
  inadmissibility, no extra charge. **The test is what the attack needs, never
  how it is computed.**
- **A-3** Two riders: (i) a fixed data-independent permutation of byte
  *positions* applied **by indexing alone** is not a ShiftRows *computation*;
  MixColumns never qualifies, since it forms bytewise linear combinations.
  (ii) a table access is within the S-box route **iff** it realises an S-box
  application already counted in N, at most one per access; every other table
  access is outside it. **O-CM1-3 remains open** and no table-access conversion
  is created.
- **A-4** Mandatory disclosure: the complete specification-level operation
  inventory, and the implementation technique, with the explicit statement that
  the latter does not affect the classification. Omission → INADMISSIBLE, figure
  is not evidence. (This adopts the red team's `required_controls[0]`.)

### 1.3 Worked classifications under the adopted rule

Every case below is stated with the classification the rule yields. A rule with
no worked classification is not admissible under this task's card, so these are
the admissibility evidence for clauses A-1..A-4.

**A-CASE-1 — the red team's headline counterexample: fused T-table attack that
computes rounds.** N T-table lookups (each performing SubBytes + ShiftRows +
partial MixColumns) plus X AddRoundKey byte-XORs, no other operation. The attack
uses a T-table *because it needs the round output*, i.e. its specification-level
description consumes the MixColumns result.
→ **A-2(i): independent → INADMISSIBLE under Route 3, recorded UNADJUDICABLE.**
Both of the red team's two readers are now forced to this same verdict; the
opposite-disposition split is closed, and closed in the **conservative**
direction (no figure is manufactured).

**A-CASE-2 — T-table used purely as an S-box realisation.** Same lookups, but
the attack extracts only the substituted byte and discards the fused linear
by-product; nothing downstream consumes ShiftRows or MixColumns output.
→ **A-2(ii) + A-3(ii): not independent → admissible under Routes 1+3, charged
(N/S_k + X/X_k) AEU-k.** This is the case the red team's Reader B had in mind,
and it is now reachable only when the by-product is genuinely discarded.

**A-CASE-3 — bitsliced attack.** N S-box applications realised as a Boolean
circuit, plus X AddRoundKey byte-XORs, nothing else consumed.
→ **A-1 + A-2(ii): admissible, (N/S_k + X/X_k) AEU-k.** *This is the case that
rejected the candidate rule*: there is no memory access to absorb anything into,
yet nothing independent of the S-box route occurred.

**A-CASE-4 — AES-NI attack using `AESENC` as a full round.** The attack consumes
the round output, hence MixColumns.
→ **A-2(i): INADMISSIBLE, UNADJUDICABLE.** Identical to the pre-amendment CM-1
verdict; Route 3 is not widened by a single case.

**A-CASE-5 — AES-NI `AESENCLAST` with a zero round key, used only to obtain
SubBytes outputs, the ShiftRows relabelling absorbed by reading output bytes at
permuted indices.** The ShiftRows step is applied by indexing alone, with no
bytewise arithmetic (**A-3(i)**); the instruction's zero-key XOR is a by-product
the attack does not consume (**A-2(ii)**).
→ **admissible, (N/S_k + X/X_k) AEU-k**, where X counts only the AddRoundKey
byte-XORs the *attack* requires. Note the asymmetry that makes this safe: an
unconsumed by-product contributes nothing to what the attack computes, so the
exemption buys no cryptanalytic capability.

**A-CASE-6 — table-driven attack that also consults a precomputed
difference-distribution table.** That second table access stands in no
correspondence to a charged S-box application.
→ **A-3(ii): outside the S-box route → INADMISSIBLE, UNADJUDICABLE.** Shows the
bar still bites, and that A-1 cannot be used to launder "2^t table accesses"
into "2^t S-box applications".

**Anti-laundering check performed.** The only way to reach the cheaper
classification under A-2(ii) is for the operation's result to be genuinely
unconsumed; the moment it is consumed, A-2(i) fires. So there is no reading in
which an attack gets real linear work for free. The residual attack surface is
*honest description*, not the rule — named in the amendment's `limitations` as
the place a red team should hit next.

---

## 2. GAP B — the narrower sense of "distinct"

### 2.1 Draft B-0, TESTED and REJECTED, recorded rather than deleted

> **Draft B-0.** "Two computational acts are DISTINCT IN KIND — the only sense of
> 'distinct' that triggers element (f)'s separate charge — if and only if the act
> that PRODUCES a candidate does not itself compute the quantity that the act of
> VERIFYING that candidate compares against the target ciphertext."

This is the natural first formalisation of the "distinct in kind, not in
procedural sequencing" reading both reviewers inferred. **It fails the
proves-too-much check.**

Apply it to the m=0 definitional reference. The producing act is "pick the next
key" — a counter increment. It does **not** compute E_K(P); the verifying act
does. B-0 therefore rules the reference's two acts distinct in kind, applies
element (f)'s separate charge to the reference, and charges it
2^(k-1) AEU-k **plus** 2^(k-1) verification units — roughly doubling CM-1's
`element_b_success_convention.the_charged_definitional_reference` figures
(2^127 / 2^191 / 2^255 AEU-k), which are definitional and which no amendment may
move. That is exactly the failure both reviewers independently predicted.

**Diagnosis.** B-0 drew the boundary between *choosing* and *computing*. The
boundary that matters is between **work already charged** and **work not yet
charged**. Clause B-1 draws it there.

### 2.2 The rule adopted (clauses B-1..B-4)

- **B-1** Element (f)'s separate N-verification-unit charge applies **iff the
  work already charged for producing the candidate set does not itself include,
  for each candidate in it, a FULL evaluation of AES-k on a target plaintext
  from the attack's own element (d) data under that candidate key.** Procedural
  separation is explicitly **not** the test. A partial evaluation — one round, a
  truncated computation, an algebraic or statistical constraint check, a table
  match — is not a full evaluation and does not bundle.
- **B-2** The charge is levied on the **survivors of the last production stage
  that does not include a full per-candidate evaluation**, never on candidates
  eliminated at or before it. "Bundled" carries element (d)
  `relation_to_R1`'s existing meaning — first pair per candidate, remaining
  pairs only for first-pair survivors (about one, on average) — which is
  element (b)'s same-convention-on-both-sides rule applied to the attack side.
  **No new charge is created and none is removed.**
- **B-3** Multi-stage pipelines are decomposed stage by stage; B-1 is applied
  once, at B-2's boundary. No escape by relabelling the final full-evaluation
  pass as "the candidate-generation mechanism"; no double-charging the same
  candidate set.
- **B-4** Mandatory disclosure of the stage decomposition and the survivor count
  at each boundary. Omission → INADMISSIBLE, number is not evidence.

### 2.3 THE PROVES-TOO-MUCH DEMONSTRATION (mandatory; it PASSES)

**Object.** The m=0 definitional reference: pick the next key K, encrypt a target
plaintext P under K, compare with the target ciphertext C, stop at first match.

**Apply clause B-1.** What is the work charged for producing each candidate? One
AEU-k. And one AEU-k is, by element (a)'s own definition, *"ONE FULL AES-k
ENCRYPTION OF ONE 128-BIT BLOCK AT THE FULL ROUND COUNT FOR THAT KEY SIZE ...
INCLUSIVE OF ONE KEY-SCHEDULE EXPANSION FOR A FRESH KEY"* — i.e. **a full
evaluation of AES-k on a target plaintext under that candidate key.**

Clause B-1's antecedent ("does NOT itself include ... a FULL evaluation") is
therefore **FALSE**.

**Result: element (f)'s separate charge DOES NOT APPLY; verification is
BUNDLED.** This is exactly the classification `-003`'s own resolving text gives
the reference, and exactly the classification the literal "genuinely distinct
computational acts" reading failed to give it. **The check passes.**

**Independent confirmation from a second direction.** Had the charge applied, the
reference's charged cost would be ~2× its definitional figure, contradicting
`element_b_success_convention.the_charged_definitional_reference`. Clause B-1
leaves those three figures precisely where CM-1 put them. Note also that the
*procedural* structure of the reference (two steps: pick, then encrypt-compare)
is unchanged under B-1 — B-1 simply refuses to look at it, which is the whole
point of the repair.

### 2.4 Worked classifications under the adopted rule

**B-CASE-1 — m=0 definitional reference.** → **BUNDLED**, no separate charge.
(§2.3.)

**B-CASE-2 — `-003`'s already-closed original case:** partial recovery of m bits,
residual ordinary exhaustive encrypt-and-compare over the remaining 2^(k-m),
stopping at first match. Production work per candidate is a full evaluation.
→ **BUNDLED**, no separate charge — **the same answer `-003` gave**, which
RT-20260901-1af5d9 confirmed closed. Amendment 004 does not disturb it.

**B-CASE-3 — the red team's guess-and-determine hybrid** (algebraic pre-filter
culls 2^(k-m) candidates to N survivors via partial algebraic constraint checks,
then an ordinary encrypt-and-compare on the survivors). The pre-filter performs
no full per-candidate AES-k evaluation.
→ **Charge APPLIES, and applies to the N survivors only.** Total = pre-filter
cost (charged under whichever element governs its own operation type: element
(a)'s routes as amended by clauses A-1..A-4, or UNADJUDICABLE where no route
applies) **+ N verification units**. The red team's Reader A and Reader B now
compute the same total; the additive-N_survivors split is closed. This also
closes validator finding F-VAL4c225b-3 on the same object.

**B-CASE-4 — sieving / meet-in-the-middle producing N candidates from table
matches.** No full per-candidate evaluation while producing the set.
→ **Charge APPLIES to N.** `-003`'s two named exemplars ("algebraic
elimination, sieving") are re-confirmed by B-1 rather than displaced by it.

**B-CASE-5 — two-stage filter:** enumerate 2^(k-m) candidates with a **one-round**
filter, then fully encrypt the survivors. A one-round evaluation is a partial
evaluation.
→ **Charge APPLIES, to the survivors of the one-round filter** (B-2's "last
stage that does not include a full per-candidate evaluation"). Determinate where
the literal `-003` wording was not. Note the error direction: partial never
bundles, so this rule charges *more* often, not less — against this campaign's
own interest, which is the only direction such a rule may point.

**B-CASE-6 — full encryption per candidate but comparison against only 64
ciphertext bits**, leaving survivors to confirm against a further pair.
→ **BUNDLED** for the first pair (production includes a full evaluation), with
the further-pair confirmation charged by **B-2**'s second sentence exactly as the
reference side is charged under element (d) `relation_to_R1`. No asymmetry
between the two sides is created; element (b) requires exactly that.

**B-CASE-7 — laundering attempt, checked deliberately.** A pipeline that
relabels its final encrypt-and-compare pass as "the candidate-generation
mechanism" in order to claim the whole pipeline is bundled.
→ **Blocked by B-3** (explicit prohibition) and by **B-2** (the boundary is the
last stage *without* a full per-candidate evaluation, wherever the submitter
puts the label), and made visible by **B-4**'s disclosure duty.

---

## 3. Completion gate, checked item by item

| gate item | status |
| --- | --- |
| Both gaps carry verbatim operative rule text | **YES** — `the_change.item_1_gap_a_definition_of_independent.resolving_text_verbatim` (clauses A-1..A-4) and `the_change.item_2_gap_b_the_bundling_test.resolving_text_verbatim` (clauses B-1..B-4) |
| Each rule tested against named implementations / attacks | **YES** — 6 worked cases for Gap A (fused T-table computing rounds; T-table as S-box only; bitsliced; AES-NI `AESENC`; AES-NI `AESENCLAST`; extra difference table), 7 for Gap B |
| Gap B proves-too-much demonstration present and passes | **YES** — §2.3; and the failed draft B-0 is recorded, not deleted (§2.1), as the card requires |
| `-003` unedited | **YES** — not opened for writing; amendment 004 is a separate file superseding three quoted fragments (SUP-A-1, SUP-A-2, SUP-B-1) |
| CM-1 unedited | **YES** — read only |
| objections 3 and 4 named OPEN AND UNATTEMPTED | **YES** — OU-1 and OU-2 in the amendment, with objection 4 explicitly recorded as inherited from RQ-AES-002 R7 and out of any CM-1 amendment's scope |

Write scope respected: exactly three files written, all inside the two declared
paths. Nothing was committed.

---

## 4. Limitations of this task itself, stated rather than left to be found

1. **NO CLOCK. SC-1's stamp duty is unsatisfiable by construction here.** This
   session's tool surface is file read, write, edit, content search, path glob
   and inter-agent messaging — no command execution. `start_utc`, `start_epoch`
   and `binding_stop_utc` are therefore null in `budget_stamps.jsonl` and in the
   amendment's budget block, with a declared surrogate (a fixed six-section plan,
   one stamp per boundary) bounding *work volume* rather than seconds. SC-10
   forbids inventing a timestamp; where SC-1 and SC-10 conflict, SC-10 governs.
   This is the **third observed recurrence** of `DEF-CM1-CLOCK`
   (BATCH-2b0fd1 → BATCH-286bcd → BATCH-241d37); the task is charged at its
   declared 900 s under C6, and the defect is against the instrumentation, not
   the producer. **A halt is infrastructure signal, never a negative
   mathematical result** — and no halt occurred.
2. **THE REQUIRED YAML PARSE CHECK COULD NOT BE RUN.** The task card asks for
   `python3 -c "import yaml;yaml.safe_load(open(PATH))"`. No command-execution
   tool exists in this session, so it was **not run**, and no claim is made that
   it passed. What was done instead, and all that was done: a structural
   inspection of every `key: value` line in the amendment for plain scalars
   containing `": "`, for flow sequences, for block-scalar indentation
   uniformity, and for reserved leading indicators — no defect found. **That is
   a manual inspection, not a parser.** An independent parse is owed by the
   archival task or by review.
3. **No SHA-256 could be computed** for any artifact, for the same reason; the
   amendment's `artifact_provenance` records `null` with the reason rather than a
   fabricated digest. The snapshot receipt of the archival task is the
   authoritative binding.
4. **The snapshot commit `69f52eba4bdbda468b8d51b77b12570c62f76062` was NOT
   independently verified** by this session (no git access). It is recorded as
   named by the dispatching Coordinator.
5. **The worked classifications are arguments, not measurements.** No
   implementation was written, compiled, instrumented, benchmarked or run, and
   no attack exists to which any classification has been applied.
6. **Read scope was not exhausted, and this is stated rather than implied.**
   Read in full: the task card, the handoff, RT-20260901-1af5d9's red-team
   report, `protocol-amendment-GOAL-AES-002-003`, `CM-1.yaml`. Read in part: the
   validation report (searched to F-VAL4c225b-3 and its per-artifact
   disposition). **Not opened in this session:** `RQ-AES-002.yaml`,
   `GOAL-AES-002.yaml`, `DEC-20260901-1fc2f5.yaml`, `-001`, `-002`,
   `AGENTS.md`, `docs/inventor-protocol.md`, `docs/claims-and-verification.md`,
   `templates/research-records.md`. R7 and R5 language relied on above is
   attributed to RT-20260901-1af5d9's own independent verbatim re-read and to
   `-003`'s committed text, not to a direct read here.
7. **Knowledge retrieval NOT ATTEMPTED** — no `search_knowledge` /
   `get_context` / `get_source` / `find_related` tool in this session's surface,
   the same gap CM-1 and `-003` disclose. No query is recorded as issued because
   none was. This licenses **no** absence, novelty, or non-novelty inference.
8. **These two resolving blocks are themselves unreviewed.** `-003`'s four blocks
   closed every first-round counterexample and were then broken by two new ones
   in the second round. The same may happen here. A defect found in clauses
   A-1..A-4 or B-1..B-4 is a specification result requiring a **further**
   superseding amendment, never an edit to amendment 004.
9. **AMAZON BEDROCK WAS NOT SELECTED, CONFIGURED, PROBED, CONTACTED OR USED** at
   any point, in any runtime, backend, endpoint, model identifier, fallback or
   probe (AGENTS.md rule 16; SC-11).

**R5 / SC-4 / SC-7.** This report states **no margin** and no result about AES at
any round count, so the anti-laundering same-sentence duty is discharged
vacuously and is recorded as such rather than left to be inferred. The symbolic
forms above — `(N/S_k + X/X_k) AEU-k`, `2^(k-1)`, `N verification units` — are
charging forms of the model, not margins; no N, X, m or survivor count is given a
value anywhere. `dominated_by`:
`unresolvable in this environment: no primary source reachable; every recalled frontier row is unverified-from-memory`.
