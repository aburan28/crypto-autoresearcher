# Red-team report — GOAL-MCE-001 BATCH-001 framing

**Task:** TASK-20260803-08e883 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Question:** RQ-MCE-e65b3c · **Date:** 2026-08-03 · **Role:** red-team

**Inference provenance.** `requested_policy: review-adversarial` ·
`resolved_model_id: claude-opus-5` · `fallback_used: true` ·
`independent_session: true` (session), `independent_model: false`.
`review-adversarial` requires `xhigh` reasoning and an independent session; the
alias does not resolve under this Claude Code harness (CLAUDE.md, model policy
note), so the session model served it.

**THIS REVIEW IS NOT ADMISSIBLE TOWARD AN AGENTS.md RULE 13 CLOSURE QUORUM.**
Rule 13 requires pairwise-distinct `resolved_model_id`. This review and
`TASK-20260803-409c5e` both resolve to `claude-opus-5`. **No attestation may be
synthesized from this document**, and it may not be counted as one of the three
concurring judgements.

**Scope firewall on this document.** This report asserts nothing about Classic
McEliece's security in either direction. Where it discusses the reach of a
published attack it discusses *what this program's records say about what a
paper says*, and nothing more.

**Read scope actually used.** `AGENTS.md`, `CLAUDE.md`,
`docs/inventor-protocol.md`, `docs/target-result-profile.md`,
`docs/claims-and-verification.md`, `ledger/goals/GOAL-MCE-001/goal.yaml`,
`ledger/goals/GOAL-HQC-001.yaml`, `ledger/decisions/DEC-20260802-344883.yaml`,
`ledger/questions/RQ-MCE-e65b3c.yaml`, `knowledge/gathers/GATHER-20260803.md`,
`knowledge/open-problems/KN-OPEN-3f7a21.md`, `BATCH-001-OPENING.md` in full,
both producer packages at snapshot commits `6787c6e4` / `4d801d94` (recorded in
`archives/TASK-20260803-9fddc2/snapshot-receipt.json` and
`archives/TASK-20260803-f3beb0/snapshot-receipt.json`; working tree clean at
`398677d7`), and `knowledge/literature/` (169 files, measured).

---

## VERDICT

**PARTIALLY UPHELD, with one falsified framing claim, one contradicted ledger
citation, and one over-broad refusal. The batch is NOT a third consecutive
Coordinator overread of the GOAL-HAWK-001 / GOAL-HQC-001 shape — but it does
carry a fourth-shape error of the same family, and one of its two headline
framing sentences is falsified by its own producers' primary text.**

Broken out:

| Section | Verdict |
|---|---|
| §2 census — 169 / 137 / 32 / 0-read / 0 KN-TECH | **ALL FIVE NUMBERS CONFIRMED** by independent measurement (O-1). |
| §2 framing — "a broad unread corpus is more dangerous than a narrow one", applied to the 137 | **CHALLENGED (O-2).** The framing is inverted relative to its own numbers: the 137 are the best-provenanced McEliece entries in the corpus, not the worst. |
| §3 — KN-OPEN-3f7a21 used to discount pre-existing entries | **UPHELD (O-3).** Not a convenient argument. §3 says "unconfirmed", which is exactly what KN-OPEN-3f7a21 supports and no more. 31 of the 32 pre-existing entries cite `downloads/`. |
| §4 — refusal to characterise KN-LIT-7c4620 | **MOSTLY UPHELD, over-broad on one item (O-4).** One of the six "not established" items was already answered by a page the program had itself fetched. |
| §4 — "**The rate threshold is the whole question**" | **FALSIFIED (O-5).** This batch's own transcription shows the decisive restriction on `KN-LIT-4c8135` is a *family exclusion*, not a rate. This is the single most consequential defect in the opening. |
| §5 — "This goal **binds to** that convention" / goal.yaml "the convention GOAL-HQC-001 and GOAL-SDITH-001 **already bind to**" | **CONTRADICTED BY LEDGER (O-6).** `DEC-20260802-344883` D-6 states the convention **IS NOT ADOPTED** and that GOAL-SDITH-001 **must not bind to it**. |
| §5 — "the two live code-based goals" | **CHALLENGED (O-7).** `GOAL-SDITH-001.status: draft`, `current_batch_id: null`. |
| §7 — failure condition (confident characterisation the text does not support) | The batch is **closer to the dismissal-side error than the alarm-side error**, and the vehicle is §4's rate sentence, not the primary target (see O-5, and "Which error" below). |
| §8 §9 — SOURCES.md regression, 110 validation errors | **CONFIRMED** (spot-checked, O-8). |
| Duty 5 — producer scope firewall | **HELD.** No producer asserts anything about Classic McEliece's security, including by implication. One borderline juxtaposition (O-9). |
| Duty 6a — KN-LIT-4c8135 Goppa-exclusion omission | **VERIFIED. The producer is right.** |
| Duty 6b — `key-recovery` tag on distinguisher entries | **VERIFIED AND WORSE THAN REPORTED.** Prevalence is 4 of 4, not 2 of 2, and one of the four contradicts its own body. |

The producer packages themselves are of high quality and I found no
transcription overreach in either. My objections are against the **Coordinator's
framing**, which is what this task was dispatched to attack.

---

## Duty 1 — the named precedent, attacked

`ledger/decisions/DEC-20260802-344883.yaml` (via
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/archives/TASK-20260802-a157ad/ledger-receipt.json`,
`corrections_carried_by_this_archive.process_finding`) records:

> "Second consecutive campaign in which a Coordinator 'the next_action is
> defective' claim was an overread caught by its own red team, after
> GOAL-HAWK-001 BATCH-001. The Coordinator named that precedent in the handoff
> and asked to be checked against it. The check worked; repeating the error
> after naming it is itself recorded."

`BATCH-001-OPENING.md` §3 names it a third time. I treated that as grounds for
more suspicion and went looking for the same error.

**Finding: the *literal* error did not recur.** This opening makes no "the prior
record is defective" claim at all. §3's three inherited hazards are each stated
at or below what the cited record supports (see O-3), and §5's eprint paragraph
correctly reproduces GOAL-HQC-001's D-4 retraction rather than re-making it —
the producer's independent measurement (`attack_transcription.md` §0, "PDF
endpoint returned HTTP 403 with `cf-mitigated: challenge`, twice") confirms the
opening's caution was correct.

**But the error family recurred in mirror image.** The GOAL-HAWK-001 /
GOAL-HQC-001 failure is: *a Coordinator asserts a status for a prior record that
the prior record does not carry.* §5 and `goal.yaml` do exactly that, in the
positive direction instead of the negative — asserting that a prior record
*supports* a binding it explicitly withholds. See **O-6**. That is the third
consecutive campaign in which a Coordinator claim about a prior record's status
is contradicted by that record, and this one is in a **committed ledger record**,
not merely an opening.

---

## Objections

### O-1 — §2's census: CONFIRMED, all five numbers. (No objection.)

Independently measured on the clean tree at `398677d7`:

| §2 claim | Measured | Verdict |
|---|---|---|
| 169 KN-LIT entries mentioning McEliece | `grep -ril mceliece knowledge/literature/` → **169** | CONFIRMED |
| 137 filed 2026-08-03 by GATHER-20260803 | commit `10dc665c` adds exactly **137** files under `knowledge/literature/`, all 137 McEliece-mentioning | CONFIRMED |
| 32 pre-existing | 169 − 137 = **32**; 31 `added: 2026-07-24`, 1 `added: 2026-07-27` | CONFIRMED |
| Of the 137, papers actually read: **0** | `citation_verified` across the 137: **118 `web`, 19 `false`, 0 `read`**. All 137 carry an explicit not-read statement (checked file-by-file, 0 missing). | CONFIRMED |
| 0 KN-TECH on ISD or code-based cryptanalysis | 82 KN-TECH files; **0** match `information set decoding|ISD|Prange|Stern|Goppa|syndrome decoding|code-based` | CONFIRMED |

Two sub-claims I attacked and could not break:

- §2's *"where the entry's description of an algorithm comes from general
  knowledge … it says 'recalled, not read from this source'"*. An exact-string
  grep returns only 2 files, which looks like a 6-vs-2 discrepancy against
  `GATHER-20260803.md` (which names Prange, Stern, Leon, Lee–Brickell,
  Niederreiter, McEliece 1978). It is **not** a discrepancy: the phrase is
  line-wrapped in four of them. All six named papers carry it —
  `KN-LIT-6a786b` (Prange), `KN-LIT-fb9047` (Stern), `KN-LIT-bbd0e9` (Leon),
  `KN-LIT-10be29` (Lee–Brickell), `KN-LIT-55b31e` (Niederreiter),
  `KN-LIT-141bac` (McEliece 1978). **CONFIRMED.**
- The 0-KN-TECH claim survives a wider net, with one near-miss worth recording:
  `KN-TECH-078` is *"Correlation and fast correlation attacks — linear
  cryptanalysis of stream ciphers as decoding"*, tagged `decoding, parity-check,
  ldpc`. It is not ISD and not code-based cryptanalysis, so §2's "0" stands as
  written, but a novelty screen keyed on `decoding` will surface it and a future
  KN-TECH on ISD should cite it rather than pretend the corpus was empty.

**Cheapest control that would falsify §2 if it were wrong:**
`git show --name-only 10dc665c | grep -c knowledge/literature` cross-checked
against `grep -ril mceliece knowledge/literature | wc -l` and a
`citation_verified` value histogram over the 137. Cost: three commands. I ran
them; the census holds.

---

### O-2 — §2's danger framing is inverted relative to its own numbers

**Objection.** §2 is titled *"Corpus census — broad, and unread"* and concludes
*"A broad unread corpus is more dangerous than a narrow one, because it returns
confident answers to novelty and dedup queries that it has no basis to answer."*
Read in context this attaches the danger label to the **137 new entries**. The
measurement says the opposite ordering.

**Citation it contradicts.** `knowledge/open-problems/KN-OPEN-3f7a21.md`:
7457 of 7666 entries carry `citation_verified: read` against an absent tree. I
re-measured on the current tree: **7459 of 7807** corpus-wide carry
`citation_verified: read`, and `downloads/` is still absent
(`git ls-files downloads` → 0; not in `.gitignore`). Of the **32 pre-existing**
McEliece entries, **31 cite a `downloads/` path** and 31 carry `read`.

So within the McEliece slice the provenance ranking is:

1. the **137** — every one `web` or `false`, every one carrying an explicit
   not-read statement, 118 verified against a primary index this session;
2. the **32** — 31 marked `read` against an artifact tree that has never
   existed.

The 137 are the **best**-provenanced McEliece entries in this corpus. §2's
framing invites the reader to treat them as the hazard. §3 does credit them
(*"that choice … happens to be the behaviour it argues for"*), so the opening is
not internally inconsistent — but the census section, which is the part a
downstream agent will grep, states the danger the wrong way round.

**Cheapest falsification control (the null-object control this batch never
ran).** Run the identical census against a scheme with no campaign attached —
`grep -ril "bike\|hqc\|sdith" knowledge/literature/` and histogram
`citation_verified` and `added`. If "broad and unread" is the corpus baseline
rather than a McEliece-specific hazard, §2 has reported a controlled null as a
finding (`docs/inventor-protocol.md` §3: "controls before belief"). My partial
run of this — 7459/7807 corpus-wide `read` against an absent tree — already
indicates the baseline is *worse* than the McEliece slice. Cost: two commands.

---

### O-3 — §3's use of KN-OPEN-3f7a21 is NOT a convenient argument. Objection withdrawn.

I went in expecting this to be the soft spot and it is not. §3 says only:

> "Any pre-2026-08-03 McEliece entry's `read` provenance is therefore
> **unconfirmed**."

`KN-OPEN-3f7a21` says, in its own words, *"The obvious reading — '7457 records
lie about having been read' — **is not supported**"*, and states the supported
conclusion as *"≈99.5% of the corpus is un-re-verifiable in place."*
"Unconfirmed" is precisely that and not one notch more. The opening does not use
the finding to *discount* prior work; it uses it to decline to *rely* on it,
which is the narrowest available move.

One residual, recorded not pressed: §3 asserts the 137's `web`/`false` choice
"was made independently of KN-OPEN-3f7a21". `GATHER-20260803.md` does not
mention `KN-OPEN-3f7a21` (grep count 0), which is consistent with the claim but
does not establish it — an agent can be aware of a record it does not cite. The
claim is about intent and is unverifiable from artifacts. It is also
inconsequential: the behaviour is right either way. **Cheapest control:** none
exists that is worth its cost; recommend the Coordinator downgrade the phrasing
to "the 137 use `web` or `false` and never `read`, which is the behaviour
KN-OPEN-3f7a21 argues for" and drop the intent claim.

---

### O-4 — §4's refusal is over-broad on one item, and the over-breadth is not caution

**Objection.** §4 lists among what is *"not established, by anything this program
holds"*: *"which code families and rates it reaches; **whether it touches binary
Goppa codes at all**"*.

That item was already answered by a page **this program had itself fetched on
2026-08-03**. `knowledge/literature/KN-LIT-7c4620.md` records:
*"Citation verified against the IACR ePrint record for report 2026/1232 (title
and author list checked) on 2026-08-03."* `knowledge/gathers/GATHER-20260803.md`
records: *"IACR ePrint: 75 of 75 requested records resolved. Title and author
list were compared against the bibliography for each."*

The page so fetched carries, per `attack_transcription.md` §1.1 (source A01,
sha256 `6e27530d…f1a6`), the ePrint keyword line verbatim:
`McEliece scheme, Algebraic cryptanalysis, Binary Goppa codes`, and the abstract
opening *"the McEliece cryptosystem based on binary Goppa codes"*.

So on 2026-08-03 the program held bytes answering "does it touch binary Goppa
codes at all" and the opening declared the question open. That is not epistemic
caution; it is a failure to use held evidence, produced by a sweep that verified
citations against abstract pages **without recording the two lines of scope text
those pages carry**.

**This is the answer to duty 3.** §4's refusal is appropriate for five of its six
items — validity, exponent, heuristic content, rate regime, bearing on Classic
McEliece parameters are all genuinely unestablished, and the producers confirm
it (`heuristics_enumerated.md` §1.1: heuristics obtained **0**;
`rate_regime_extraction.md` §1.1: rate condition **NONE STATED** in the obtained
text and body-level condition **UNKNOWN**). It is over-broad on the code-family
item. And it misses a distinction the producer had to supply: the paper's
complexity claim is a **conjecture** (*"We make the conjecture that this attack
has a complexity which is of the same nature as the distinguisher"*), and the
word "subexponential" attaches unhedged only to the **distinguisher byproduct**.
§4 says the title *"claims a heuristic subexponential attack"* — true of the
title, and the title is what the corpus entry relayed; but the abstract on the
same fetched page is weaker than the title, and nothing in the opening flags
that.

**Cheapest falsification control.** For every KN-LIT entry whose
`citation_verified: web` was obtained from an ePrint abstract page, record the
`Keywords:` line and the abstract verbatim in the entry body at verification
time. Zero extra network requests — the page is already being fetched. For the
retrospective check: re-fetch `https://eprint.iacr.org/2026/1232` (one request,
HTTP 200 confirmed twice today) and diff its keyword line against §4's
"not established" list.

---

### O-5 — §4's "The rate threshold is the whole question" is FALSIFIED by this batch's own primary text

**This is the most consequential objection in this report.**

**The claim.** `BATCH-001-OPENING.md` §4:

> "**The rate threshold is the whole question.** `KN-LIT-4c8135` is genuinely
> polynomial-time and genuinely confined to high rate. Classic McEliece's rate is
> a number this program has not transcribed. The distance between those two is
> what BATCH-001 exists to measure…"

and `ledger/questions/RQ-MCE-e65b3c.yaml`, constraints:

> "Rate-scoping is load-bearing, not decoration. KN-LIT-4c8135 is polynomial-time
> key recovery for HIGH-RATE random alternant codes; **the threshold is the
> practically decisive number** and no deliverable may state the headline without
> it."

**The record that contradicts it.** `TASK-20260803-292b99`,
`rate_regime_extraction.md` §3.3, quoting `arXiv:2304.14757` at sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`, VERBATIM and
flagged clean extraction:

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

with the paper's Table 1 restriction column reading *"(does not apply in the
particular case of Goppa codes)"* and §3.2 headed *"What is wrong with Goppa
codes?"*.

**Why this falsifies the framing, precisely.** §4 asserts a *characterisation*
("genuinely confined to high rate") and a *research programme* ("the rate
threshold is the whole question", "the distance between those two is what
BATCH-001 exists to measure") about a paper nobody in this program had read. The
paper states a three-conjunct restriction — family, field size, rate — and the
producer's judgement, which I endorse, is that the family conjunct is the sharp
one: `rate_regime_extraction.md` §6, *"the family exclusion alone is a sharper
and cheaper discriminator than any rate arithmetic."*

**And the same framing error propagated into the corpus.** `KN-LIT-4c8135`'s
"Relevance" section says the rate condition is what makes the result bounded:
*"Polynomial-time key recovery against a family adjacent to the one McEliece uses
would read as devastating with the rate condition dropped; with it stated, it is
a precise statement about a region of parameter space that deployed systems
avoid."* `KN-LIT-13a01d` repeats it: *"The high-rate scoping repeats the pattern
of [[KN-LIT-4c8135]]: real result, bounded regime, and **the bound is the
practically decisive part**."* Both were written 2026-08-03 without reading
either paper.

**Second instance, same shape.** §4's rate framing is also the wrong instrument
for `KN-LIT-71d1a0`. Its Theorem 3 is stated in the **dual** rate and says
VERBATIM *"However here we allow any R"* (`rate_regime_extraction.md` §2.2);
the numeric thresholds `R < 0.277` / `R < 0.141` are conditions on Heuristic 1's
**random-code null model** applied to a **shortened** code whose rate the paper
argues is `o(1)` by construction (§2.3). Reading them as primal-rate thresholds
for a McEliece code is, in the producer's words, "a category error." So for two
of the three papers examined, the measurement §4 declared to be "the whole
question" is either not the decisive one or not well-typed.

**Scope limit on my own objection.** I am not saying the rate is irrelevant, and
I am asserting nothing about what any of this implies for Classic McEliece. I am
saying that "the rate threshold is the whole question" is a *confident
characterisation of KN-LIT-4c8135's scope that the primary text does not
support*, and that `BATCH-001-OPENING.md` §7 defines exactly that as this
batch's failure condition.

**Cheapest falsification control.** One grep. With `arXiv:2304.14757` in hand:
`pdftotext … | grep -i -n -C2 "Goppa"` over the extracted text, and read Table 1's
restriction column. Cost: one command against an already-retrieved file. The
producer effectively ran it. The opening did not, because it had not retrieved
the file — but the *forward* control is that no future deliverable of this goal
may state a restriction as "the rate" until a `grep -i "does not apply\|does not
work" ` pass over the same text has been run and reported.

---

### O-6 — §5's convention binding is contradicted by a committed ledger decision

**The claim.** `BATCH-001-OPENING.md` §5:

> "This goal **binds to that convention and does not derive a competing one.**
> `RQ-MCE-e65b3c` states it as a constraint."

`ledger/questions/RQ-MCE-e65b3c.yaml`, constraints:

> "Bind to the costing convention produced under GOAL-HQC-001
> TASK-20260802-0100a5; do NOT derive a competing one."

`ledger/goals/GOAL-MCE-001/goal.yaml` (lines 16–18), stronger still:

> "…baseline at those parameters under the costing convention GOAL-HQC-001 and
> GOAL-SDITH-001 **already bind to**."

and (lines 32–33): "…this record binds to their ISD costing convention rather
than opening a competing one."

**The record that contradicts it.** `ledger/decisions/DEC-20260802-344883.yaml`,
D-6, VERBATIM:

> "ISD-FC-2026 **IS NOT ADOPTED**. The proposed convention is admitted as a
> reviewed working document only. Adoption is conditional on resolving the red
> team's O6 and O7… It is a usable draft, not a binding convention, and
> **GOAL-SDITH-001 must not bind to it in its current state**."

corroborated by
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/archives/TASK-20260802-a157ad/ledger-receipt.json`,
`what_this_archive_makes_durable_and_what_it_does_not.durable[2]`: *"That a
proposed ISD costing convention exists and is **explicitly NOT adopted**."*

**The objection.** GOAL-MCE-001 is the third code-based goal in the same class as
GOAL-SDITH-001. A ledger decision naming a sibling goal and forbidding it to bind
to this artifact "in its current state" is on point. Three defects follow:

1. `goal.yaml`'s "already bind to" is **false as written**. GOAL-HQC-001 did not
   adopt it (D-6). GOAL-SDITH-001 is `status: draft`, `current_batch_id: null`
   and binds to nothing (O-7). Neither goal binds to it.
2. §5's hedge is aimed at the wrong axis. It hedges *finality* — "Whether
   `TASK-20260802-0100a5`'s output is final is **not asserted here**" — while
   the ledger's objection is to *adoption*, and adoption is stated flatly in a
   decision record, not buried in the artifact. §5 says "this Coordinator has not
   read that convention artifact"; it did not need to. It needed
   `DEC-20260802-344883` D-6, one grep from the goal record it *did* read
   ("GOAL-HQC-001's record shows BATCH-001 closed and the campaign now at
   BATCH-003").
3. The operational consequence is real and it distorted this batch's shape. §5
   uses the binding to justify stopping the second producer at parameters:
   *"That is why BATCH-001's second producer transcribes Classic McEliece's
   parameters and stops there."* The justification rests on a binding that does
   not exist. See the batch-shape answer below for what that deferral cost.

**Cheapest falsification control.** `grep -n "0100a5\|ISD-FC-2026\|NOT ADOPTED"
ledger/decisions/DEC-20260802-344883.yaml`. One command. This should be a
standing pre-open check: **before any goal record asserts that a sibling goal
binds to an artifact, grep that sibling's terminal decision record for the
artifact's adoption verdict.**

---

### O-7 — "the two live code-based goals" overstates GOAL-SDITH-001

**Objection.** §5 opens: *"`GOAL-HQC-001` and `GOAL-SDITH-001` are both code-based
and both need a memory-charged ISD cost."* under the heading *"Coordination with
the two live code-based goals"*.

**Citation.** `ledger/goals/GOAL-SDITH-001.yaml`: `status: draft`,
`current_batch_id: null`. A `draft` goal with no batch is not live and has no
convention needs to coordinate with. This is minor on its own, but it inflates
the coordination pressure that O-6's non-existent binding was invoked to relieve.

**Cheapest control.** `grep -m3 "status:\|current_batch_id" ledger/goals/GOAL-SDITH-001.yaml`.

---

### O-8 — §§8 and 9 confirmed. (No objection.)

Not in my required set but cheap and falsifiable, so checked:

- §9: `python3 tools/validate_ledger.py` → `FAIL: 110 new validation error(s)`,
  all under `ledger/evidence/` and `ledger/decisions/`. **CONFIRMED at 110.**
  (I did not independently re-check the `origin/main` scratch-worktree
  comparison; the branch-side number is confirmed.)
- §8: `knowledge/SOURCES.md` line 19 reads
  `| Per-URL retrieval attempts | 0 |`, and
  `inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json` top-level keys are
  `baseline_hashes, command, completed_at, current_codedualattack_head, cwd,
  origin_main_commit, schema, sources, started_at, task_id, working_head,
  working_tree_status` — **no `attempts` key**. **CONFIRMED.**

---

### O-9 — one borderline juxtaposition in `standardization_status.md`, and one uncited assertion

**Objection (minor, but it is the only firewall-adjacent line in the batch).**
`TASK-20260803-f3aece/standardization_status.md` §3.1 item 2:

> "**No mceliece348864 variant is in the ISO standard.** … This is significant for
> GOAL-MCE-001: the phrase *"the standardized parameter sets"* excludes 348864,
> which is exactly the set carrying the lowest claimed category **and the subject
> of both attack-claim notes on the designers' NIST page**."

Two problems. (a) "both attack-claim notes on the designers' NIST page" is an
assertion about content that is **not transcribed anywhere in this task's
package** — `nist.html` is quoted only for *"In 2025, NIST delayed McEliece
standardization"*. Under AGENTS.md rule 10 the assertion has no artifact behind
it. (b) Placing "excluded from ISO", "lowest claimed category" and "subject of
attack-claim notes" in one sentence flagged "significant for GOAL-MCE-001" is the
closest anything in this batch comes to an implication about a parameter set's
standing. It stops short — nothing is asserted — but it is exactly the shape the
firewall is meant to prevent.

**Verdict on duty 5 overall: the firewall HELD.** I grepped both producer
packages for first-person security predicates (`is secure`, `remains secure`,
`does not threaten`, `is threatened`, `unaffected`, `we conclude`, `therefore
Classic McEliece`). Every hit is either a verbatim quotation attributed to a
source, or an explicit prohibition the producer wrote against itself
(`corpus_provenance_upgrade.md` §1.4: *"Any statement that the attack does or
does not threaten Classic McEliece"* — listed under "What must NOT be written").
`attack_transcription.md` §1.3 handles the single most tempting sentence in the
batch — the authors' own note that their attack *"does not break Classic McEliece
parameters"* — by transcribing it, attributing it, recording that the referenced
paragraph was not read, and explicitly refusing to use it as licence to dismiss
the paper. That is correct handling and it is the hardest case.

**Cheapest control for O-9.** Either transcribe the two notes from
`https://classic.mceliece.org/nist.html` (already fetched, sha256 in
`source_access_log.yaml`) verbatim, or delete the clause. One or the other, not
neither.

---

## Duty 4 — the batch shape, answered concretely

**Is §1's KN-TECH-080 exact-bottleneck justification sound, or a rationalisation
for deferring the hard work?**

**Sound in principle, but it under-delivered, and a cheaper decisive test
existed. Three of them, in fact.** I name them concretely as required.

`docs/inventor-protocol.md` §8 does require establishing the exact bottleneck and
reproducing the baseline before expensive experiments, and `KN-LIT-f1073f`
(Panny, brute force) is a real cautionary instance in this exact literature. I
do not object to "read before you solve". I object that the batch spent two
executor tasks to obtain what one already-fetched page and one already-read table
would have given, and that the *baseline half* of §1's own justification was
never touched.

**Cheaper decisive test #1 — the page the program had already fetched (zero
marginal cost).** `GATHER-20260803.md` records *"IACR ePrint: 75 of 75 requested
records resolved"*, and `KN-LIT-7c4620` records its citation verified against
`https://eprint.iacr.org/2026/1232` on 2026-08-03. That fetch already returned
the abstract, the keyword line, and the authors' `Note:` field. Recording them
verbatim at that moment — **no additional network request** — would have
delivered the code family (binary Goppa), the field condition (even
characteristic), the conjecture-versus-theorem status of the complexity claim,
the absence of any stated rate condition, and the authors' revision note. That is
substantially everything `TASK-20260803-292b99` returned for the primary target
(`attack_transcription.md` §§1.1–1.5), obtained days of budget earlier. The
batch's shape is defensible; the *sweep's* shape was not, and §1 does not notice.

**Cheaper decisive test #2 — the family grep (one command, and it is the sharp
discriminator).** With `arXiv:2304.14757` in hand, `grep -i "does not work\|does
not apply" ` over the extracted text returns the Goppa exclusion immediately.
This is cheaper than any rate arithmetic and, per `rate_regime_extraction.md` §6,
sharper. §4 designed the batch around the rate comparison instead. See O-5.

**Cheaper decisive test #3 — the ISD baseline table the batch READ AND DECLINED
TO TRANSCRIBE.** This is the concrete miss. `parameter_sets.md` §3:

> "SEC's Table 1 (Esser–Bellini estimator output, **three memory models per set**)
> **was read** and is available at `mceliece-security-20221023.pdf` p.10. It is
> **not** transcribed into this document: it is attack-cost estimation, outside
> this task's transcription scope…"

GOAL-MCE-001's second completion criterion (`goal.yaml` lines 84–86) wants a
memory-charged ISD cost "with hidden overhead, memory access, and time-memory
tradeoffs accounted". The designers' own estimator output at three memory models,
for all five sizes, **was in the executor's hands, extraction-clean, at zero
marginal retrieval cost**, and was deferred. The stated reason chains back to
O-6: the batch is waiting on a costing convention that `DEC-20260802-344883` D-6
says was never adopted. **Transcribing a published table is not adopting a
convention.** It is the baseline side of the comparison, and having it in the
corpus is a precondition for ever charging it under any convention.

**Concrete recommendation for BATCH-002, in cost order:**

1. Transcribe SEC Table 1 verbatim, three memory models × five parameter sets,
   with per-cell extraction-damage markers. One already-retrieved PDF, no
   convention adopted, no assessment made. This is the `KN-LIT-f1073f` discipline
   §1 invokes and it is the cheapest unbought item in the goal.
2. Run the corpus tag audit forced by duty 6b (below) — 137 entries, one script.
3. Only then re-attempt the `iacr:2026/1232` body, per
   `heuristics_enumerated.md` §1.3's three ranked unblocking routes.

**On the "cheapest brute-force baseline" in the `KN-LIT-f1073f` sense:** none is
available yet and I do not claim one is. No attack cost has been stated by this
program, so there is nothing to compare a brute-force baseline against.
Recommendation #1 is the prerequisite that makes that comparison possible.

---

## Duty 3 — which error is this batch closer to?

**Closer to the dismissal-side error, and the vehicle is §4's rate sentence, not
the primary target.**

`BATCH-001-OPENING.md` §7 names the two symmetric failures: reporting the paper
as a threat it may not be, and *"dismissing it as irrelevant on a rate argument
nobody transcribed"*. The opening then, in §4, states as established: *"The rate
threshold is the whole question. `KN-LIT-4c8135` is genuinely polynomial-time and
genuinely confined to high rate."* — a rate argument nobody had transcribed,
applied to a paper nobody had read, which the batch's own producer then showed
carries an explicit family exclusion that the rate framing does not capture
(O-5).

Two mitigations, both real, which is why my verdict is "closer to" and not
"committed":

- The error lands on the **secondary** target (`KN-LIT-4c8135`), not the primary
  one. §4's treatment of `KN-LIT-7c4620` itself is disciplined to the point of
  over-caution (O-4), and the producers held that discipline throughout.
- The producer **caught it**, without being told to, and refused to complete the
  comparison the opening asked for (`rate_regime_extraction.md` §6: *"Computing a
  distance from a missing left-hand side and a second-hand right-hand side would
  produce a number with the appearance of a measurement and the content of a
  guess."*). The batch's review layer worked.

So: the batch did not fail §7's test, but the opening set it up to. The framing
sentence that would have driven BATCH-002 into a rate comparison should be
retracted before it does.

---

## Duty 6 — the two producer findings, verified

### 6a — the `KN-LIT-4c8135` Goppa-exclusion omission: **VERIFIED, and it is worse than "an omission"**

The producer's claim (`corpus_provenance_upgrade.md` §3.2): *"The original entry
recorded the high-rate scoping and did **not** record the Goppa exclusion."*

**Verified against `knowledge/literature/KN-LIT-4c8135.md`.** The word "Goppa"
appears exactly once in the entry, in the *opposite* direction: *"Alternant codes
are the family containing Goppa codes; the result is confined to the **high-rate**
regime, and that scoping is the whole content of its practical reading."* The
entry's "Key claims" list has three bullets, none mentioning a family exclusion:
*"The attack is **rate-scoped** — it does not claim to break alternant or Goppa
codes at arbitrary rate."*

So the entry does not merely omit the exclusion. It (a) names Goppa codes only to
establish *containment*, positioning the result as adjacent to McEliece; (b)
states the rate scoping is "the whole content of its practical reading"; and (c)
in its "Relevance" section, teaches the entry as the program's standard for
scope honesty — *"The best example in this sweep of a result that is genuinely
strong and genuinely bounded, and of how much the boundary carries"* — while
having the boundary wrong.

Against the verbatim primary text at sha256 `ebbd94ac…c564b8`
(`rate_regime_extraction.md` §3.3): *"Interestingly our attack does not work at
all when the alternant code has the additional structure of being a Goppa code."*
Table 1: *"(does not apply in the particular case of Goppa codes)"*. §3.2:
*"What is wrong with Goppa codes?"* … *"Goppa codes behave differently from
random alternant codes and provide counterexamples to Heuristic 18."*

**This is a material defect in an entry the sweep wrote on 2026-08-03**, it was
propagated into `KN-LIT-13a01d` (*"the bound is the practically decisive part"*),
into `BATCH-001-OPENING.md` §4, and into `RQ-MCE-e65b3c`'s binding constraints.
The producer's proposed superseding correction is correct in substance and
correct in form (superseding body addition, not a silent edit, per
`knowledge/SEEDING.md`). **I endorse filing it**, and I add that the correction
must also reach `RQ-MCE-e65b3c`'s constraint text and `BATCH-001-OPENING.md` §4
by superseding record — the defect is not contained in one KN-LIT entry.

**Cheapest control:** `grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md`
→ 1, and read the one hit. Cost: one command.

### 6b — the `key-recovery` tag on distinguisher-only entries: **VERIFIED, and the real prevalence is 4 of 4, not 2 of 2**

The producer reported the defect on `KN-LIT-71d1a0` and `KN-LIT-7ee1a9`, and
explicitly declined to extrapolate from a two-of-two sample
(`corpus_provenance_upgrade.md` §6: *"That is a two-of-two sample and **not** an
estimate of the rate across the sweep; the proper response is a check, not an
extrapolation."*). That restraint was correct. **I ran the check the producer
called for.**

**Measurement, over all 137 entries filed 2026-08-03 (commit `10dc665c`):**

| Quantity | Count |
|---|---:|
| entries tagged `key-recovery` | 36 |
| entries tagged `distinguisher` | 4 |
| entries tagged **both** | **4** |
| entries tagged `distinguisher` **without** `key-recovery` | **0** |
| entries whose **title** contains "distinguish" | 4 — and all 4 are tagged `key-recovery` |

The four:

| Entry | Title | Tags include |
|---|---|---|
| `KN-LIT-13a01d` | A distinguisher for high rate McEliece cryptosystems | `key-recovery`, `distinguisher` |
| `KN-LIT-71d1a0` | The syzygy distinguisher | `key-recovery`, `distinguisher` |
| `KN-LIT-7ee1a9` | Understanding the new distinguisher of alternant codes at degree 2 | `key-recovery`, `distinguisher` |
| `KN-LIT-e37d4c` | A note on the Goppa code distinguishing problem | `key-recovery`, `distinguisher` |

**Prevalence: 4 of 4.** Every distinguisher-tagged entry in the sweep also
carries `key-recovery`, and not one entry in the corpus's McEliece slice is
tagged as distinguisher-only. This is not a two-instance coincidence; it is a
systematic property of how the sweep tagged, and it is a defect at exactly the
grep level `RQ-MCE-e65b3c` relies on.

**And one of the four contradicts its own body.** `KN-LIT-13a01d` is tagged
`key-recovery` while its Contribution section says, verbatim:

> "**It does not recover keys; it distinguishes**, in the high-rate regime"

and its Relevance section says:

> "Report a distinguisher as a distinguisher — this program's claim tiers
> (`docs/claims-and-verification.md`) forbid promoting it to a break."

**`KN-LIT-13a01d` is the entry `RQ-MCE-e65b3c` names as the anchor of its own
binding constraint**: *"Distinguisher is not break. **KN-LIT-13a01d
distinguishes and does not recover keys**; docs/claims-and-verification.md
forbids promoting one to the other."* The research question's canonical example
of the rule is itself a grep-level violation of the rule.

**Boundary on my measurement, stated so it is not over-read.** This is a
tag-versus-title-and-body check over the 137 entries filed 2026-08-03. It does
**not** cover the 32 pre-existing McEliece entries, does not cover the ~7,670
non-McEliece entries, and cannot find a distinguisher-only paper whose title and
body never say "distinguish". The correct claim is: **within the distinguisher
population this sweep identified, the mis-tag rate is 4/4**, and the sweep
produced zero correctly-tagged distinguisher-only entries.

**Cheapest falsification control, and the one I recommend be dispatched:** the
script I ran, extended corpus-wide — parse `tags:` from every
`knowledge/literature/*.md`, select entries carrying `key-recovery`, and flag any
whose title or body matches `distinguish` without an explicit key-recovery claim.
Runtime seconds, no network. Route it as a `/curate-knowledge` task, not as a
silent edit: corrections supersede.

---

## Required controls, consolidated

| # | Control | Cost | Answers |
|---|---|---|---|
| C1 | Null census: identical grep + `citation_verified` histogram for a scheme with no campaign; compare to the 7459/7807 corpus-wide `read`-against-absent-tree baseline | 2 commands | O-2 — is "broad and unread" a McEliece hazard or the corpus baseline? |
| C2 | `grep -n "0100a5\|ISD-FC-2026\|NOT ADOPTED" ledger/decisions/DEC-20260802-344883.yaml` before any goal asserts a sibling binding | 1 command | O-6 |
| C3 | `grep -i "does not work\|does not apply\|does not hold" ` over every retrieved attack paper before stating its restriction as a rate | 1 command/paper | O-5 |
| C4 | Record the ePrint `Keywords:` line and abstract verbatim at citation-verification time, for every `citation_verified: web` upgrade | 0 network cost | O-4 |
| C5 | Corpus-wide `key-recovery`-vs-`distinguisher` tag audit, routed to `/curate-knowledge` | seconds | 6b |
| C6 | Transcribe SEC Table 1 (three memory models × five sets) verbatim from the already-retrieved `mceliece-security-20221023.pdf` p.10 | 0 network cost | batch shape / goal completion criterion 2 |
| C7 | Transcribe or delete the "both attack-claim notes on the designers' NIST page" clause | minutes | O-9 |

---

## Scope limits of this report

- I reviewed the **Coordinator-committed snapshots** (`6787c6e4`, `4d801d94`,
  receipts recorded at `398677d7`), plus committed ledger and knowledge records.
  I read no working-tree-only artifact as durable evidence; the tree was clean.
- I **wrote nothing** outside
  `coordination/goals/GOAL-MCE-001/batches/BATCH-001/reviews/TASK-20260803-08e883/`.
  No producer artifact, ledger record, or knowledge entry was modified. No
  commit was made.
- I **verified no source independently** and re-fetched nothing. Every quotation
  of primary text in this report is quoted **from the producers' transcriptions**
  and is scoped to the sha256 those transcriptions record. I did not re-acquire
  `arXiv:2304.14757` or `iacr:2024/1193`; independent re-acquisition is
  `TASK-20260803-409c5e`'s deliverable and my O-5 and 6a findings are
  **conditional on the validator confirming those extractions**.
- **This report asserts nothing about Classic McEliece's security in either
  direction**, and nothing here should be read as a statement about the reach of
  any attack against it. My objections are about what this program's records
  claim, not about cryptography.
- I did not evaluate the two producers' source access logs line by line, did not
  re-run the `origin/main` scratch-worktree comparison behind §9, and did not
  audit the 32 pre-existing entries' content beyond their provenance fields.
- **Not admissible toward an AGENTS.md rule 13 quorum.** See the inference block
  at the head of this document.

---

## ONE NEXT CONCRETE ACTION

**Dispatch a single Coordinator correction task that supersedes the rate framing
in three places at once, before BATCH-002 designs anything on top of it:**
retract *"The rate threshold is the whole question"* from `BATCH-001-OPENING.md`
§4 and *"the threshold is the practically decisive number"* from
`RQ-MCE-e65b3c`'s constraints by superseding record, file the producer's
`KN-LIT-4c8135` Goppa-exclusion correction, and in the same task correct
`ledger/goals/GOAL-MCE-001/goal.yaml`'s *"the costing convention GOAL-HQC-001 and
GOAL-SDITH-001 already bind to"* to match `DEC-20260802-344883` D-6
(*"ISD-FC-2026 IS NOT ADOPTED"*). All three are the same defect — a framing
asserted ahead of the record that would have checked it — and correcting them
separately lets the next batch inherit whichever one is fixed last.
