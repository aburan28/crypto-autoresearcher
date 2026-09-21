# Red-team report — TASK-20260802-caddef

**Goal**: `GOAL-HQC-001` · **Batch**: `BATCH-002` · **Role**: red-team
**Question**: `RQ-HQC-001` · **Produced**: 2026-08-02
**Branch**: `claude/goal-target-hqc-launch-vndegi` · **Repo commit at start**: `e2f619f5` (clean tree)
**Objects reviewed**: the snapshot-committed producer artifacts at `a89e7542` and
`9baa7d87`, the three filed corpus entries, both BATCH-002 snapshot receipts, the
BATCH-002 opening, the four BATCH-002 commit messages, and `DEC-20260802-344883`
with both BATCH-001 reviews.

**I wrote none of what I am attacking.** No artifact, corpus entry, ledger record,
queue or status was modified by this task. My only write is this file.

## 0. Inference and admissibility

| field | value |
|---|---|
| `requested_policy` | `review-adversarial` |
| `resolved_model_id` | `claude-opus-5` |
| `fallback_used` | **true** — no policy alias in `orchestration/model-policies.yaml` resolves under this Claude Code harness; `.claude/agents/` frontmatter supports only Claude models, so every subagent runs `model: inherit` |
| `model_verified` | false — `python3 -m orchestration.adapter doctor --probe` was not run |
| `independent_session` | **true** |
| `independent_model` | **NO** |

**This is an independent SESSION, not an independent MODEL.** Every producer,
both reviews and the Coordinator in this batch run on the same backend. Nothing
in this report is admissible toward an `AGENTS.md` rule 13 closure quorum, and no
attestation may be synthesized from it. Claim-tier ceiling stays **toy**. This
report makes no security claim about HQC in either direction.

## 0.1 What I did independently

I did not accept any number in this batch. I re-acquired both primary sources
myself — a **fifth** independent fetch of the specification and a **third** of
RMRS — and re-derived every load-bearing figure from them.

| item | my result |
|---|---|
| `hqc_specifications_2025_08_22.pdf` | 876 126 B, sha256 `174186cb…5406d` — **byte-identical** to the recorded value |
| `arxiv.org/pdf/2005.10741` | 525 223 B, sha256 `cbb7dbd6…f5446` — **byte-identical** |
| Prop 6.1.3 implementation | calibrated against an **external** published table (RMRS Table 4's `DFR from 4.2.1` column: I compute −7.845/−11.808/−13.896 against published −7.84/−11.81/−13.90) |
| Prop 6.1.4 implementation | reproduces SPEC Table 11: I compute −10.7927/−14.1384/−11.3212 against published −10.79/−14.14/−11.30 |
| Theorem 6.1, `p_i` from 6.1.4 | 2⁻¹³²·⁸⁵⁶ / 2⁻¹⁹³·⁸⁷⁸ / 2⁻²⁶⁰·⁵¹² |
| Theorem 6.1, `p_i` from 6.1.3 | 2⁻¹²²·²⁴⁷ / 2⁻¹⁸⁵·⁹¹⁶ / 2⁻²⁴³·⁷¹⁸ |
| A19 gap | **10.609 / 7.962 / 16.794 bits** — the producer's 10.61/7.96/16.79 **VERIFIED** |
| A16 null-object measurement | cap active **219/289** and **354/481**; effect **0.3746** and **0.290** bits — the producer's 219/289, 354/481, 0.3744, 0.2898 **VERIFIED** |
| `tools/validate_ledger.py` | **67** error lines, **0** naming HQC or the three new entry ids — the batch's claim **VERIFIED** |

---

# 1. Verdict

**PROCEED TO THE LEDGER ARCHIVE, WITH FOUR CORRECTIONS THAT MUST LAND IN THE
DECISION AND THE CORRECTION RECORD.**

The batch's measured work is the strongest this campaign has produced. Every
headline number I could test reproduced, including two the producer derived and
nobody had checked (the A19 gaps and the A16 cap). The RS-S3 correction survives
a fifth independent fetch on all three routes, and I found a **fourth**. The
merge resolution is byte-exact and I withdraw any objection to it.

The defects are concentrated in one place: **the valuation of A19, and the
Coordinator's escalation of it into a campaign retarget.** The bit-counts are
right; what they measure is not what the batch says it measures. And the same
defect has already been frozen into an immutable corpus entry.

Ranked objections follow. Where a duty found nothing I say so plainly, and the
objections I could not support are **withdrawn, not softened** (§4).

---

# 2. Objections, ranked by severity

## O1 — HIGH — A19's 16.79 bits is real arithmetic and is **not value**: the specification settles A19 against itself, on three internal witnesses, and resolving it moves no published number

**Target**: `a17_characterization.md` §0.1 item 5, §6.1, §6.4 item 2;
`a17_sensitivity.yaml` derivation step 10; the `TASK-20260802-a4f56a`
receipt's `retarget_recommendation`; commit `9baa7d87`'s message
(*"A19 is reported larger and cheaper … and exceeds the bound's own conservatism
budget"*).

**The arithmetic is correct.** I reproduced 10.609 / 7.962 / 16.794 bits from my
own copy of the PDF, with my Prop 6.1.3 implementation calibrated against RMRS's
own published `DFR from 4.2.1` column so the reader does not have to take my
formula on trust. That part of the producer's work is sound and is now
independently confirmed.

**But the specification decides A19, and the batch had every ingredient and did
not run the check.** Three witnesses, all inside the document the producer
downloaded:

1. **Table 5 (p.29) — decisive.** The specification's own published DFR targets
   are `< 2⁻¹²⁸ / 2⁻¹⁹² / 2⁻²⁵⁶`. Evaluating Theorem 6.1 both ways:

   | set | `p_i` from **6.1.4** | `p_i` from **6.1.3** | Table 5 target |
   |---|---|---|---|
   | HQC-1 | 2⁻¹³²·⁸⁶ — **clears by 4.86** | 2⁻¹²²·²⁵ — **MISSES by 5.75** | < 2⁻¹²⁸ |
   | HQC-3 | 2⁻¹⁹³·⁸⁸ — **clears by 1.88** | 2⁻¹⁸⁵·⁹² — **MISSES by 6.08** | < 2⁻¹⁹² |
   | HQC-5 | 2⁻²⁶⁰·⁵¹ — **clears by 4.51** | 2⁻²⁴³·⁷² — **MISSES by 12.28** | < 2⁻²⁵⁶ |

   The 6.1.3 reading fails the document's own tabulated claim at **all three**
   levels; the 6.1.4 reading clears at all three. A specification does not
   publish a DFR column its own theorem contradicts three times.

2. **Table 11's printed values are 6.1.4's, numerically.** −10.79/−14.14/−11.30
   against my 6.1.4 −10.793/−14.138/−11.321 and my 6.1.3 −10.129/−13.670/−10.761.
   The column header (*"DFR from 6.1.4"*) is right and the caption (*"the formula
   from proposition 6.1.3"*) is wrong — decidable from the numbers, not from the
   words.

3. **The specification's own Changelog, p.3, entry 2020/10/01**, verbatim:
   *"We have improved the theoretical lower bound for the Reed-Muller decoder
   which permits to lower our theoretical bound for the DFR and improve our
   parameters."* The improved bound is what the parameters were set with. This is
   documentary, it is on page 3 of the PDF, and no BATCH-002 artifact cites it.

**What follows, and it is the objection.** A19 is a **stale cross-reference of
exactly the same family as the printed `49`** — a sentence the document failed to
update when its own analysis moved on. Resolving it correctly leaves every
published HQC number where it is. Therefore:

- **"Larger than A17" is a category error.** A17, if it fails toward positive
  association, would move the *published claim*. A19, resolved correctly, moves
  *nothing*; its 16.79 bits is the size of the error a **reader** makes by
  following the literal cross-reference. Comparing the two on a bit-count ranks
  a documentation defect above a load-bearing assumption.
- **"Exceeds the bound's own conservatism budget of 2.72/4.25/5.40 bits" is
  void.** That budget (step 9) measures how much a *dependence amplification of
  the true DFR* must exceed before the published number stops being an upper
  bound. A19 is not an amplification of anything; it is a choice of which upper
  bound to quote. The two quantities are not commensurable and the comparison
  should be struck.
- **The producer's own §3.7 already says this** — *"under R2 either choice keeps
  the theorem TRUE (both are upper bounds on `q`), so R-p is an ambiguity of
  tightness, not of validity"* — and §6.1/§6.4 then rank it above A17 anyway. The
  document contradicts itself, and the receipt and commit message propagated the
  louder half.

**What survives.** Resolving A19 *is* worth doing, cheaply, for exactly one
reason the batch never states: a downstream re-derivation that follows Theorem
6.1's literal text manufactures a false finding that HQC misses its DFR target at
**all three** security levels — the identical trap the `49` set at one level. That
is hygiene of the same class as `CORR-20260802-3ae664`, not a research target,
and it is worth **zero** bits of movement in HQC's published claim.

**Cheapest resolving control.** Zero-network, already run in this report:
evaluate Theorem 6.1 at both readings and compare against Table 5's three
targets. Thirty seconds. It decides A19 outright and I have run it.

---

## O2 — HIGH — a second RS-S3 has already been frozen into the immutable corpus: `KN-LIT-b9e1a8` relays the `6.1.3` cross-reference and flags the inconsistency **without deriving which reading the document forces**

**Target**: `knowledge/literature/KN-LIT-b9e1a8.md`, *Key claims* → "Concatenated
DFR (Theorem 6.1…)" and *Published-text inconsistencies* item 3.

The entry relays Theorem 6.1 verbatim including *"`p_i` is defined as in
proposition 6.1.3"*, and item 3 records that *"Table 11's column header names
Prop. 6.1.4 while its caption names Prop. 6.1.3, and Theorem 6.1's own text names
Prop. 6.1.3"*. It stops there.

**That is the exact failure mode BATCH-002 exists to correct.** Item 1 of the same
section does the right thing for RS-S3: it prints the anomalous value, then gives
three derivations that force the correct one. Item 3 does the first half and not
the second — it records that the printed cross-references disagree without
deriving which one the rest of the document forces, which is verbatim what the
Coordinator faulted BATCH-001 for on the `49` (`correction_report.md` §2.5:
*"What BATCH-001 did omit is the arithmetic — it recorded that the two printed
values disagree without deriving which one the rest of the document forces"*).

**Cost of the omission.** A reader following the entry's relay takes `p_i` from
Prop 6.1.3 and concludes HQC misses its published DFR target by 5.75 / 6.08 /
12.28 bits at NIST-1/3/5. The `49` trap was 46 bits at one level; this one is
5.8–12.3 bits at **three**. It sits on the same lane, in an entry marked
`citation_verified: read`, and the entry is now immutable.

**The mitigation the entry does provide** — flagging the three-way inconsistency —
is real and is why this is not the worst possible version of the defect. It is
also exactly the mitigation BATCH-001 provided for the `49` (anomaly X6), which
this program judged insufficient.

**Cheapest resolving control.** Free and zero-network. `CORR-20260802-3ae664`
(or a sibling `CORR`) supersedes `KN-LIT-b9e1a8` item 3 with one sentence:
*"Table 11's printed values match Prop 6.1.4 numerically, and Theorem 6.1
evaluated with Prop 6.1.3's `p_i` fails Table 5's own DFR targets at all three
levels; the document's numbers are Prop 6.1.4's."* No entry is edited — the
correction supersedes, as the `49` correction does.

---

## O3 — MEDIUM-HIGH — *"A17 is implied by A5"* is true only on the space where A17 is not in question, and the producer's own §2.1 says so

**Target**: `a17_characterization.md` §0.1 item 3, §3.4 (R4), §5.4;
`a17_sensitivity.yaml` `null_object_check.correction_to_the_inherited_framing`;
the `a4f56a` receipt's `null_control_fired_partially`; commit `9baa7d87`'s
*"A17 is IMPLIED by A5 applied to disjoint blocks"*.

The implication is **space-dependent**, and the producer establishes both halves
and then reports only one:

- **On space (M)** — `ẽ ∼ Bernoulli(p⋆)^{⊗n₁n₂}` — A5 does imply A17. The blocks
  are disjoint, `F_j` is a function of `ẽ^{(j)}`, functions of disjoint blocks of
  independent coordinates are independent. Correct, and trivial: on (M) A17 was
  never in question.
- **On space (T)** — where A17 is actually asserted (§2.2 states it on (T)) — the
  producer's own §2.1 says *"the coordinates of `ẽ` on (T) are demonstrably **not**
  independent"*, citing the sources' own under-dispersion (γ ≈ 0.61–0.74). A5 read
  as the literal proposition is therefore **false on (T)**, and an implication
  from a false antecedent discharges nothing.
- Read the way the source actually intends and hedges it — A5 as a *modelling
  substitution* whose products *"can only be upper bounds"* — A5 does **not**
  imply A17, because the validity of a substitution is functional-specific. The
  producer says precisely this in §5.5 (A5's evidence covers two functionals,
  A17 consumes a third).

So the flat headline *"A17 is not a second, independent assumption"* holds only
under a reading of A5 on which A5 is itself false, and fails under the reading the
source supports. Under the latter, BATCH-001's *"second, independent use"* framing
is defensible and should not be recorded as corrected.

**Why this matters operationally.** The instruction that follows it — §6.4 item 4,
*"the logical question is already answered (A5 ⟹ A17) and pursuing it would
rediscover A5"* — would steer BATCH-003 away from a question that is not in fact
answered. That is the shape `AGENTS.md` §"Research-direction integrity" exists to
catch, and I do **not** allege it was deliberate: the producer supplies the
refutation itself, three sections earlier.

**Cheapest resolving control.** Free: the decision records the implication with
its quantifier — *"A5 ⟹ A17 on space (M) only; on space (T), where A17 is stated,
A5 as a literal proposition is false and the implication is vacuous"* — and does
**not** record BATCH-001's O10 framing as corrected.

---

## O4 — MEDIUM — *"settled by reading, not measuring"* is wrong about the mechanism, is refuted by two prior sessions that read the same sentences, and points at a source the search explicitly excluded

**Target**: `a17_characterization.md` §6.1 (*"settled by reading the source and the
reference implementation"*), §0.1 item 5; the `a4f56a` receipt
(*"settled BY READING rather than by measuring"*); commit `9baa7d87`.

Three problems, in ascending order:

1. **It is not settled by reading.** Reading gives three inconsistent
   cross-references and no resolution — which is exactly the state BATCH-001 left
   it in. What settles it is *arithmetic on already-published numbers* (O1's three
   witnesses). "Reading" and "computing from published tables" are different acts,
   and conflating them is what let two prior sessions read the sentences and leave
   the question open.
2. **The task card's own question answers itself.** BATCH-001 *did* find A19 — it
   is recorded as assumption `A19` and anomaly `X3` in
   `dfr_model_transcription.md`, verbatim and correctly. It did not settle it
   because reading does not settle it.
3. **The named settling source is outside the searched scope.** §6.1 proposes
   *"reading the source and the reference implementation"*, while
   `proof_search_log.md` §8 lists *"the HQC reference/optimised implementation and
   its comments"* among the artifacts **not** searched. A recommendation whose
   discharge route is an unsearched artifact is a promise, not a finding —
   especially when the free internal route (O1) was available and unrun.

**Cheapest resolving control.** The decision restates A19's resolution route as
*"exact arithmetic on SPEC Tables 5 and 11 plus the p.3 Changelog"*, not *"reading
the reference implementation"*, and records that the reference implementation
remains unread.

---

## O5 — MEDIUM — *"I did not and cannot establish the document's edit history"* is falsified by the document's own three-page Changelog, which is on page 2 of the PDF that was downloaded

**Target**: `correction_report.md` §2.6 (*"Status of this paragraph: a hypothesis
supported by a numeral coincidence and a shared lineage… I did not and cannot
establish the document's edit history"*), §4.3, DEV-3; `filing_report.yaml`
DEV-3 and `what_this_task_does_not_establish`.

The specification carries a **Changelog on printed pages 2–4**, dated by revision.
It is not the full edit history, but it directly bears on both provenance
hypotheses the report files as unestablishable:

- **2020/10/01**: *"We have updated the sizes of the decoded messages for the
  concatenated RMRS code to the targeted security levels (i.e. 128 and 192 rather
  than 256) for level 1 and 3 which improves the decoding capacity of the RMRS
  code and improves our parameters."* — this is precisely the move from RMRS
  Figure 6's `k = 32` at all levels to `k ∈ {16, 24, 32}`, i.e. **documentary
  support for X6's second half being a stale RMRS-era sentence** (§4.3's
  hypothesis).
- **2020/10/01**, second bullet: the improved Reed-Muller bound — O1 witness 3.
- **2025/08/22**: *"…fixing several typographical errors"*, a revision that did
  not fix this one.

`cannot` is the strongest word in the sentence and it is wrong: two pages of the
same PDF were available and unread. The correct status is *"the changelog records
the k-dimension change consistent with this hypothesis and says nothing about the
RS-S3 minimum distance"* — which is stronger evidence than the numeral
coincidence and still short of proof.

I stress that this cuts **in the batch's favour**: it strengthens the stale-value
account rather than weakening it. It is filed as an objection because an
overstated impossibility is a defect in either direction, and because
`CORR-20260802-3ae664` will inherit the sentence.

**Cheapest resolving control.** Free: the `CORR` cites SPEC Changelog p.3
(2020/10/01) beside the numeral coincidence, and replaces *"cannot establish"*
with *"the published changelog records a related parameter change and does not
mention the RS-S3 minimum distance"*.

---

## O6 — MEDIUM — the *"complete location inventory"* is not complete: SPEC pp.1–5 are absent from it

**Target**: `proof_search_log.md` §0 (*"records the **complete location inventory
of both documents**"*), §3 (*"every listed section is accounted for below"*), §8.

`proof_search_log.md` §3's SPEC inventory begins at *"1 Introduction | 6"*. Pages
1–5 — the title/submitters page, a **three-page Changelog**, and the Contents — are
not listed, marked `n/a`, or otherwise accounted for. The Changelog is prose, is
about the DFR model's history (O5), and is exactly the kind of location a `T3`
acknowledgment could sit in.

**The negative nevertheless survives**, and I say so rather than inflating this.
The §4.1 keyword sweeps were whole-document — the log itself reports hits on pages
3 and 5 for `assum` and `concatenat` — so those pages were swept even though they
are not inventoried. **I read all three Changelog pages myself and found no T1,
T2, T3 or T4 item.** The defect is in the completeness claim, not in the search.

**Cheapest resolving control.** Free: the evidence record states the inventory
covers pp.6–51 of SPEC and that pp.1–5 were covered by sweep only, and notes the
Changelog's independent relevance (O5, O1).

---

## O7 — MEDIUM — the snapshot split amendment narrowed `source_task_ids` but left both handoff blocks describing a joint two-producer snapshot

**Target**: `dispatch_queue.json`, `TASK-20260802-a4f56a.handoff.objective`
(*"Commit the exact terminal artifacts of **both producers**, including the three
newly filed corpus entries, in one commit"*) and `.inputs`; the same `.inputs` on
`TASK-20260802-35472f`.

The `amendments` block correctly narrows `source_task_ids` to `[15971b]` and adds
`35472f` for `63b16a`, and the `archive` blocks are correct and verify. But
neither handoff was updated: `a4f56a`'s objective still claims it commits both
producers *and the three corpus entries*, which its commit (`9baa7d87`, four
files, no `knowledge/` path) does not. Both tasks' `inputs` still list both
producers.

A queue is a coordination record, not evidence — but this one is inside the ledger
archive's `write_scope` and will be committed. A future reader comparing
`a4f56a`'s stated objective against its receipt finds a contradiction that is
purely editorial.

**On the split itself: no objection** — see §3, duty 6(a).

**Cheapest resolving control.** Free, in the ledger archive's own commit: amend
both handoff `objective`/`inputs` strings to match the archives, recorded as a
second amendment entry rather than a silent edit.

---

## O8 — LOW — the reversal receipt misidentifies one of the three records it retracts

**Target**: `TASK-20260802-35472f/snapshot-receipt.json`
`finding_that_reverses_two_prior_records.what_this_falsifies`, and commit
`a89e7542`'s message: *"BATCH-002-OPENING section 3, **this batch's opening commit
message**, and BATCH-001 red-team objection O1 all blamed the TRANSCRIPTION."*

I read commit `206c0019`'s message in full. It says *"correct RS-S3 minimum
distance 49 → 59 — Reed-Solomon is MDS so `d = n−k+1 = 59`, and the transcribed
delta=29 gives `2·29+1 = 59` independently"*. It attributes the error to **nobody**.
BATCH-002-OPENING §3 and BATCH-001 O1 do blame the transcription; the opening
commit message does not.

Over-attributing a fault to oneself is the benign direction, but a retraction that
is itself inaccurate is now permanent in a commit message, and a later reader
auditing the reversal will find one of its three cited records does not say what
it is said to say.

**Cheapest resolving control.** Free: the decision records the reversal against
the two records that actually carry the attribution.

---

## O9 — LOW — `KN-LIT-b9e1a8`'s *"Not verified here"* undercounts its own program-generated claims

**Target**: `knowledge/literature/KN-LIT-b9e1a8.md`, *Not verified here*, first
bullet: *"No claim in this entry has been re-derived, recomputed, or measured by
this program, **with one exception** stated as such: the three arithmetic
derivations of RS-S3's minimum distance…"*

The entry contains at least two further claims that are this program's inferences,
not the source's relays, and neither is covered by the stated exception:

- *"The i.i.d.-across-inner-blocks assumption that makes this a binomial tail is
  implicit in the formula and is not stated in prose"* — an assertion about what
  the source does **not** contain.
- *"The §3.4.1 sentence therefore holds only for HQC-5"* — an inference from
  §3.4.2, Table 3 and Table 5.

**Both are true.** I verified the first by whole-document sweep (`i.i.d.`,
`identically`, `correlat*` = 0 in the 51-page specification) and the second
against §3.4.1, §3.4.2, Table 3 and Table 5 in my own copy. The defect is the
entry's self-description in an immutable record, at `confidence: reported`, whose
definition is *"the source states it; you are relaying it"*.

**Cheapest resolving control.** Free: the decision records that the entry carries
three program-derived claims, all checked, and that its "one exception" wording
undercounts them.

---

## O10 — LOW — `proof_search_log.md` §8's not-covered list omits SPEC reference `[24]`, cited for the very construction A17 is about

**Target**: `proof_search_log.md` §8 (bounds on the negative), §6.3 (*"the citation
chain is two links long and both links are exhausted"*).

§8 names `[1]` Aguilar-Melchor et al. 2018 and *"the wider concatenated-coding
literature"*, but not SPEC `[24]` = **Lin & Costello, *Error Control Coding*,
2004**, which §3.4.2 cites twice for the Reed-Solomon construction and the field
polynomial. That textbook is the canonical home of the memoryless-inner-channel
concatenated-code error analysis the producer's own route (d) anticipates.

**The obstruction claim nevertheless survives, and I strengthened it.** I checked
SPEC's citations page by page across the whole DFR region: p.32 carries `[4]`
(RMRS) once, and **pp.33–39 carry no citation at all**. The producer's log does not
report performing this check for SPEC (it performs the exhaustive version only for
RMRS's two-item bibliography). So the DFR chain does terminate as claimed, and now
on a directly verified basis.

**Cheapest resolving control.** Free: §8's list, as restated in the evidence
record, names `[24]` explicitly.

---

# 3. The six named duties, answered — including where I found nothing

## Duty 1 — the replacement account of the printed `49`

**Route 1, shortening/MDS: SOUND.** From my own fetch, SPEC §3.4.2 p.17 verbatim:
*"obtained by subtracting 209 from the parameters n **and** k of the code RS-1,
… and by subtracting 165 from the parameters n and k of the code RS-3"*. The
arithmetic checks on all three rows (255−165 = 90, 197−165 = 32), so `n − k = 58`
is invariant. That is **shortening**, not puncturing; shortened MDS codes remain
MDS, so `d = n − k + 1 = 59`. The specification also asserts the preservation
itself (*"shortening the Reed-Solomon code does not affect its error correcting
capacity"*) and states the relation internally (`n − k = 2δ`, `d_min = 2δ + 1`), so
no external MDS theory is imported. **Yes, the spec really subtracts 165 from both
n and k, and yes, the construction preserves minimum distance.**

**Route 2, δ = 29: SOUND.** Table 3 p.18, read from my own extraction: RS-3 δ = 29
and **RS-S3 δ = 29**. `2·29 + 1 = 59`. Siblings check: δ = 15 → 31 ✓ printed 31;
δ = 16 → 33 ✓ printed 33. **δ = 29 is Table 3's value for this code.**

**Route 3, deg g₃ = 58: SOUND.** SPEC pp.18–19 print `g₃(x)` in full; its highest
term is `+ x⁵⁸`. `58 = 90 − 32 = 2δ`. Sibling generators end at `x³⁰` and `x³²`,
matching `n − k` on both. **g₃ really has degree 58.**

**The printed `49` is real.** My extraction of p.18 returns
`• RS-S3[90 = 255 −165, 32 = 197 −165, 49].` at a fifth independent fetch of a
byte-identical PDF. The BATCH-002 replacement account is **confirmed** and the
BATCH-001/BATCH-002-OPENING attribution to the transcription is **confirmed
false**.

**The uncomfortable possibility — is HQC's published DFR itself computed with 49?
NO, and Table 11/Table 5 are consistent with 59.** This is the question the batch
did not ask, and the answer clears the specification:

| | δ_e = 29 (d = 59) | δ_e = 24 (d = 49) | Table 5's claim |
|---|---|---|---|
| HQC-5, Theorem 6.1 | **2⁻²⁶⁰·⁶⁰** | 2⁻²⁰⁹·⁸⁴ | < 2⁻²⁵⁶ |

Only `d_e = 59` produces a Theorem 6.1 value consistent with the DFR the
specification publishes for HQC-5; `49` misses it by 46 bits. **Table 5 is
therefore a fourth, independent, internal route to 59** — and, more importantly,
it is evidence that the specification's own security claim was computed with
δ_e = 29. This is **not** a defect in the specification's security claim; it is an
isolated stale printed parameter. The typo/stale-value account stands, and the
batch may state it more strongly than it did.

**Note on the stale-value hypothesis.** RMRS Figure 6, read from my own fetch:
`[80, 32, 49]`, `[76, 32, 45]`, `[78, 32, 47]` — all MDS, and `49 = 80 − 32 + 1`
is correct there. Combined with the Changelog (O5), the hypothesis is materially
better supported than the batch records. It remains a hypothesis.

## Duty 2 — the filing decision and what entered the corpus

**Provenance levels: HONEST and EARNED.** I re-acquired both full-text sources at
the recorded sha256 and checked entry claims against my own copies:
`KN-LIT-b9e1a8` and `KN-LIT-1c9474` at `read` are correct under
`knowledge/SEEDING.md`'s definition (*"you fetched the actual paper (PDF/abstract)
and the claims in this entry reflect its real content"*); `KN-LIT-4c1133` at `web`
is the conservative and correct call, and the entry documents that the choice was
deliberate. No upgrade to `KN-LIT-2141` was filed; I confirmed that file is
untouched by this batch's commits.

**Laundering: NONE FOUND.** I sampled the entries hard against the primary text and
every hedged claim retains its hedge: *"simplifying assumption"*, *"working
assumption"*, *"can only be upper bounds"*, *"no exact formula"*, *"the
approximation is less precise"*, *"a **small proportion** of HQC bits do behave as
i.i.d Bernoulli variables"* — all verified verbatim in my own extractions.

**Spot checks that passed** (each verified against my own fetch): Table 5's nine
parameter values and three DFR targets; Table 11's six values; RMRS Table 4's
fifteen values; RMRS Figure 6's three external codes; Table 12's
1.00015/1.00047/1.00101; §6.2.3's four-term prose on p.45; §3.4.1's *"dimension 32
over F256"*; the 23-author list in submission order; the claim that *"Guo–Johansson's
A New Decryption Failure Attack Against HQC (ASIACRYPT 2020) is absent from its
reference list"* — I checked all four reference pages: Guo and Johansson appear as
co-authors of `[20]` (the TCHES rejection-sampling timing attack) and `[21]`
(Ring-LPN), and the decryption-failure-attack paper is indeed absent. The entry's
wording is precise and correct.

**A second uncorrected defect: YES — see O2.** It is the A19 cross-reference,
relayed with the inconsistency flagged and the resolution underived. This is the
answer to the duty's question and it is the reason O2 is ranked HIGH.

**The `KN-OPEN-3f7a21` pattern: NOT repeated.** The three new entries do carry
`read`/`web` with nothing retained, but unlike the 7 457 legacy entries they cite
no phantom `downloads/` path; each records a URL, byte count and sha256, and the
re-acquisition path is real — **I exercised it myself and both hashes matched**.
That is the good version of the pattern, and it is the pattern `KN-OPEN-3f7a21`
Q2 proposes as a candidate repair. One forward note, not an objection: if Q2's
repair introduces a new provenance level, these three will need re-marking like
every other.

**Was one batch of delay justified?** Yes on the evidence now available: the
delay is what produced the reversal of the attribution (a finding that could not
have been made by filing on schedule) and the third derivation route. It did not,
however, catch O2 — so the delay bought less than a full audit.

## Duty 3 — the A17 negative

**The negative SURVIVES, and I strengthened it with a control the producer did not
run.** The concern that the token search would miss the assumption under different
vocabulary is the right concern; I tested it. Sweeping both documents for the
vocabulary a coding theorist would actually use:

| token | SPEC | RMRS |
|---|---|---|
| `memoryless` | **0** | **0** |
| `exchangeab*` | **0** | **0** |
| `disjoint` | **0** | **0** |
| `mutually` | **0** | **0** |
| `jointly` | **0** | **0** |
| `pairwise` | **0** | **0** |
| `outer` | **0** | **0** |
| `erroneous` | **0** | **0** |

and I reproduced the producer's own sweeps **exactly**: SPEC `Proof` ×4 (pp.33,
35, 36, 40), `Remark` 0, `Lemma` ×3 (pp.44, 45×2), `Appendix` **0**, `independen`
×16 on the same seven pages, `bounded distance` 0; RMRS `Proof` ×4 (pp.4, 5, 9,
10), `Remark` ×2 (both p.12, both before Theorem 4.3), `Appendix` **0**, `i.i.d`
×1 (p.12, Remark 4.2). **"Zero appendices" is true in both documents.**

**Cited external work**: I checked SPEC's citations across the DFR region
directly — p.32 carries `[4]` once, **pp.33–39 carry none** — which the producer's
log does not report doing for SPEC. RMRS's two-item bibliography is exhausted as
reported. The chain terminates.

**Figures, tables, captions**: SPEC Fig. 4 and RMRS Fig. 5 are the only artifacts
at the right conceptual place; the producer's §5.4 disqualification of them (wrong
parameters, wrong depth, first-moment quantity) is sound and I add nothing.

**Locations it did not check**: the Changelog (O6) — which I read, finding nothing;
`[24]` Lin & Costello (O10); and the artifacts §8 correctly lists as out of scope
(reference implementation, NIST archives, earlier revisions, `[1]`, the general
literature). **An earlier HQC version** is correctly excluded as a separate
document, and the in-document Changelog is the nearest available substitute.

**Load-bearing claim: HOLDS.** Theorem 6.1 is terminal — I confirmed nothing after
p.39 recomputes the concatenated DFR — and the handoff's warning case (an
assumption superseded by Theorem 6.1) genuinely applies to A9/A10 and not to A17.
I independently reproduced the A16 measurement that gives the null control its
discriminating power (219/289, 354/481, 0.375/0.290 bits). The null-object work is
the best-executed part of this batch.

## Duty 4 — the retarget recommendation

**The numbers: VERIFIED.** 10.609 / 7.962 / 16.794 bits, from my own PDF, with the
Prop 6.1.3 implementation calibrated against an external published table. The
conservatism budget 2.72/4.25/5.40 also checks (Table 11's 0.17/0.25/0.18 × m for
m = 16/17/30). **No fabrication, no arithmetic error.**

**The reasoning: FAILS — see O1, O3, O4.** In summary:

- *"settled by reading"* — wrong mechanism, and refuted by two prior sessions that
  read the same sentences (O4). The document settles it by **arithmetic**.
- *"larger than A17"* — a category error: A19 resolved correctly moves **no**
  published number, while A17 could move the published claim (O1).
- *"exceeds the conservatism budget"* — incommensurable quantities (O1).
- *"cheaper" confused with "more valuable"* — **yes, demonstrably.** Cheap is
  right; valuable is not established and, once A19 is resolved (O1), is zero.

**The null-control finding that A17 is implied by A5: PARTIALLY FALSE — O3.** It
holds on space (M), where A17 was never in question, and is vacuous on space (T),
where A17 is stated and where the producer's own §2.1 declares A5's antecedent
false. So BATCH-001's red team is **not** shown to have mischaracterized A17, and
the producer has **not** manufactured a reason to abandon the target — it has
supplied a real observation and over-generalized it by one quantifier.

**What the producer actually recommended, and what the Coordinator forwarded.**
§6.4's **first** recommendation is *"Retarget from 'A17' to `μ_{δ_e+1}`"* — a
sharpening **within** the same lane, keeping the target. Its second is *"Resolve
A19 first"* — a **re-sequencing**. The `a4f56a` receipt and commit `9baa7d87`
compress these into *"RETARGETING AWAY from A17, which is the target
`DEC-20260802-344883` named"*, dropping the primary recommendation and elevating
the secondary one into a campaign redirection. **That is a Coordinator overread of
its own producer**, and it is the one this red team was convened to find.

**Recommended disposition.** Keep `DEC-20260802-344883`'s A17 lane, renamed to
`μ_{δ_e+1}` on space (T) per the producer's own first recommendation. Handle A19
as a documentation correction in the same `CORR` family as the `49`, resolved by
O1's control, **not** as a research target and **not** as a reason to move the
campaign.

## Duty 5 — premature closure and scope inflation

**Nothing found, and I looked in the specific places named.**

- **A17 is not treated as settled in either direction.** `a17_sensitivity.yaml`'s
  verdict is `UNDETERMINED_WITHOUT_MEASUREMENT_OR_PROOF`, and both mechanisms are
  derived with their signs shown. The one closure-shaped statement (§6.4 item 4)
  carries a named obstruction, an argument and forward guidance, so it meets
  `docs/inventor-protocol.md` §4's standard even though its quantifier is wrong
  (O3).
- **"Undetermined" is used to justify the next step, not to stop.**
  `verdict.is_this_a_good_outcome` says an honest undetermined *"is what would
  justify a later measurement or a later proof"*; §7 supplies four proof routes,
  each with its own ceiling named, including route (d) whose ceiling is stated
  before it is proposed. This is the correct use.
- **No claim exceeds the toy tier.** `claim_tier: toy` and `certificate.kind:
  none` appear in the sensitivity file; every producer artifact and both receipts
  restate it.
- **Filing is nowhere described as progress on HQC's security.** I checked all
  four BATCH-002 commit messages (`206c0019`, `7f8a78d4`, `a89e7542`, `b39e81d7`,
  `e2f619f5`) and both receipts. Every one carries an explicit disclaimer; the
  `a4f56a` receipt's `what_this_snapshot_does_not_establish` is the strongest
  version of it. The `a89e7542` message's most assertive line —
  *"A FINDING THAT REVERSES TWO PRIOR RECORDS"* — is about this program's own
  records, not about HQC, and it is true.
- **No HQC security claim** appears in any filed corpus entry, in either
  direction. The 50.7-bit figure is correctly kept out of all three entries.

The only closure-adjacent item worth a line, and it is **not** an objection: the
producer's *"undetermined"* rests on the correct structural argument (a
`(δ_e+1)`-way joint moment is not determined by second-moment data), and it names
the exact quantity that would determine it. That is the honest form.

## Duty 6 — the Coordinator's process decisions

### (a) The mid-batch snapshot split — **LEGITIMATE**, with O7 as the only defect

I looked for convenience and did not find it.

- **The cited authority says what the amendment says.**
  `docs/task-lifecycle.md` §7a: *"After **a producer** reaches a terminal outcome,
  the Coordinator runs its isolated snapshot archive task before any dependent
  review."* Singular. It binds the freeze to a producer going terminal, not to the
  slowest sibling.
- **The precedent supports this case *a fortiori*, not merely by analogy.**
  BATCH-001's red team ruled the `TASK-20260802-1f2e40` split *"a design
  correction found by running the design, correctly recorded on both tasks,
  operationally verified. No objection."* BATCH-002's case is **stronger**: this
  split also prevented three live `knowledge/literature/` entries and a rebuilt
  `INDEX.md` — state other tooling reads — from sitting uncommitted in a shared
  worktree while another agent ran. That is a new and better reason, not a
  borrowed one.
- **The operative facts verify.** `a89e7542` has parent `7f8a78d4` and changes
  exactly its 7 declared paths; `9baa7d87` has parent `b39e81d7` and changes
  exactly its 4. The two declared path sets are disjoint. Both reviews
  (`32250e`, `caddef`) depend on **both** snapshots, so no reviewer reads an
  unfrozen artifact — I confirmed this in `dispatch_queue.json`.

**Objection O7 stands** on the un-updated handoff text, which is the split's only
loose end.

### (b) Framing bias — **not toward defending A17; plausibly toward producing a competitor**

The handoff did hand the executor a pre-formed conclusion (BATCH-002-OPENING §4:
*"A17 is the highest-value surface BATCH-001 found"*) and it was in the executor's
`read_scope`.

*Against anchoring toward A17*: the executor did not accept it. It corrected the
inherited framing against its own convenience (§5.4), reported the null control
firing partially, and recommended moving off the target. The handoff explicitly
authorized that (*"Be willing to conclude A17 is NOT the best target and name a
better one"*), which is good design and I credit it.

*The bias that is present, and it is the mirror image*: a duty that explicitly
rewards *"nam[ing] a better one"* creates an incentive to produce a competitor,
and the competitor produced is the weakest analysis in the batch (O1, O4). The
producer found a real 16.79-bit arithmetic gap and did not run the free check that
would have shown the gap is not value. **The framing did not bias the analysis
toward A17; it plausibly biased the search toward finding a headline replacement.**

I do not allege bad faith, and the producer's own §3.7 contains the refutation —
which is the signature of over-reach under a reward, not of steering.

### (c) The merge resolution — **VERIFIED BYTE-EXACT. NO OBJECTION. WITHDRAWN.**

I checked this from Git rather than from the commit message, because the card
correctly flags it as HIGH severity if false. It is true:

| record | `main` (669e7368) | branch commit | verdict |
|---|---|---|---|
| `ledger/goals/GOAL-HQC-001.yaml` | blob `d4dcb845`, sha256 `73ebb5bf…` | `47a684f2`: blob `d4dcb845`, sha256 `73ebb5bf…` | **byte-identical** |
| `…/BATCH-001/dispatch_queue.json` | blob `abee2032`, sha256 `819068f2…` | `3ec55418`: blob `abee2032`, sha256 `819068f2…` | **byte-identical** |

Both blob OIDs are equal, not merely the contents. `47a684f2` and `3ec55418` are
both ancestors of `HEAD`. And `git log b6e6503e..669e7368` restricted to
`ledger/goals/GOAL-HQC-001.yaml` and `coordination/goals/GOAL-HQC-001/` returns
**exactly one** commit: `6290e316`, the PR #113 squash. **No other lane's record
was touched, and resolving to HEAD discarded nothing.** The merge commit
`5108d798` also correctly records why rebasing was forbidden.

---

# 4. Objections I could not support — withdrawn, not softened

- **The merge resolution.** Withdrawn outright: verified byte-exact from Git
  (duty 6(c)).
- **The correction resting on one route rather than two** (the queue's own duty 1
  hypothesis, inherited from the opening commit). Withdrawn: the MDS route
  applies, on the specification's own stated definitions, and I verified the
  shortening arithmetic on all three rows. The correction rests on **three**
  internal routes, and I add a fourth (Table 5).
- **Provenance laundering in the filed entries.** Withdrawn: I sampled hard
  against the primary text and every hedge is intact.
- **A17 not being load-bearing / superseded by Theorem 6.1.** Withdrawn: Theorem
  6.1 is terminal and I confirmed it.
- **Experiment design smuggled into the A17 task.** Withdrawn: `a17_sensitivity.yaml`
  step 8 evaluates a symbolic formula at the specification's own three published
  parameter sets and selects nothing; there is no trial count, seed, success
  criterion or stopping rule anywhere in the three deliverables, and
  `note_on_step_8` pre-declares the fallback disposition. No design under another
  name.
- **The split being convenience** (duty 6(a)). Withdrawn; only the editorial O7
  remains.
- **Any scope inflation or claim-tier breach** (duty 5). Nothing found in the
  producer artifacts, the receipts, or any of the five commit messages.

---

# 5. Required controls, in the order they should be run

| # | control | cost | resolves |
|---|---|---|---|
| C1 | Evaluate Theorem 6.1 at both `p_i` readings and compare against Table 5's three targets | zero-network, ~30 s; **already run in §0.1/O1** | O1, O2, O4 |
| C2 | Supersede `KN-LIT-b9e1a8` item 3 with the one-sentence A19 resolution, via `CORR` | free | O2 |
| C3 | Restate `A5 ⟹ A17` with its space quantifier in the decision; do **not** record BATCH-001 O10 as corrected | free | O3 |
| C4 | Cite SPEC Changelog p.3 (2020/10/01) beside the numeral coincidence; replace *"cannot establish"* | free | O5 |
| C5 | State the inventory's true coverage (SPEC pp.6–51 inventoried, pp.1–5 swept only) and add `[24]` to §8's not-covered list | free | O6, O10 |
| C6 | Amend both handoff `objective`/`inputs` strings to match the archives, as a recorded second amendment | free | O7 |
| C7 | Correct the reversal's list of retracted records; count `KN-LIT-b9e1a8`'s program-derived claims correctly | free | O8, O9 |

Every control is zero-network and zero-compute. None requires a decoding trial,
a measurement, or a new experiment.

---

# 6. Narrowest supported statement

> The published HQC specification at sha256 `174186cb…` prints `49` as RS-S3's
> minimum distance on p.18. Four independent witnesses internal to that same
> document — its own `n−k = 2δ` / `d_min = 2δ+1` definitions applied to a verified
> shortening, Table 3's `δ = 29`, the printed `deg g₃ = 58`, and the fact that only
> `δ_e = 29` yields a Theorem 6.1 value consistent with Table 5's published
> `< 2⁻²⁵⁶` — force `d_e = 59`. `TASK-20260802-6344ed` transcribed the source
> faithfully. Neither the specification nor arXiv:2005.10741 proves, weakens, or
> acknowledges the i.i.d.-across-inner-blocks assumption (A17); the citation chain
> from SPEC Theorem 6.1 to RMRS Theorem 4.3 terminates without a proof, and that
> negative survives a vocabulary-robustness control this session added. Assumption
> A19 is a stale cross-reference of the same family as the printed `49`: the
> specification's own Table 5, Table 11 and p.3 Changelog force the Prop 6.1.4
> reading, so resolving it moves no published HQC number.
>
> **None of this is a statement about HQC's security in either direction.** No
> measurement was taken and no decoding trial was run by this program.

# 7. Next concrete action

**Run C1's comparison into the ledger archive and file A19 as a documentation
correction in the same family as the `49`, then keep `DEC-20260802-344883`'s A17
lane open under the producer's own preferred name `μ_{δ_e+1}` on space (T).** Do
not redirect the campaign to A19: it is cheap, it is worth doing, and once done it
moves nothing.

---

```yaml
red_team_report:
  id: RT-20260802-caddef
  task_id: TASK-20260802-caddef
  claim_under_review: >-
    BATCH-002's replacement account of the printed 49, the filing of three KN-LIT
    entries, the A17 characterization, and the recommendation to retarget the
    campaign from A17 to A19.
  verdict: PROCEED_WITH_REQUIRED_CORRECTIONS
  objections:
    - {id: O1, severity: HIGH,        summary: "A19's 16.79 bits is arithmetically right and is not value; SPEC Table 5, Table 11 and the p.3 Changelog force the 6.1.4 reading, so resolving A19 moves no published number."}
    - {id: O2, severity: HIGH,        summary: "A second RS-S3 is already frozen in the corpus: KN-LIT-b9e1a8 flags the 6.1.3/6.1.4 inconsistency without deriving the resolution; the trap is 5.8-12.3 bits at all three levels."}
    - {id: O3, severity: MEDIUM_HIGH, summary: "'A17 is implied by A5' holds only on space (M); on space (T) the producer's own section 2.1 declares A5's antecedent false, so the implication is vacuous and BATCH-001's O10 framing is not refuted."}
    - {id: O4, severity: MEDIUM,      summary: "'Settled by reading, not measuring' is the wrong mechanism, is refuted by two prior sessions that read the same sentences, and names the unsearched reference implementation as its route."}
    - {id: O5, severity: MEDIUM,      summary: "'Cannot establish the edit history' is falsified by the specification's own three-page Changelog on pp.2-4, which corroborates both provenance hypotheses."}
    - {id: O6, severity: MEDIUM,      summary: "The 'complete location inventory' omits SPEC pp.1-5 including the Changelog; the sweeps covered them and the negative survives, but the completeness claim is false."}
    - {id: O7, severity: MEDIUM,      summary: "The split amendment narrowed source_task_ids but left both handoff objective/inputs blocks describing a joint two-producer snapshot."}
    - {id: O8, severity: LOW,         summary: "The reversal receipt and commit a89e7542 name the BATCH-002 opening commit message among records that blamed the transcription; it does not."}
    - {id: O9, severity: LOW,         summary: "KN-LIT-b9e1a8's 'one exception' undercounts its program-derived claims; there are at least three."}
    - {id: O10, severity: LOW,        summary: "proof_search_log section 8 omits SPEC reference [24] (Lin and Costello) from the not-covered list."}
  required_controls: [C1, C2, C3, C4, C5, C6, C7]
  counterexample_or_mutation: >-
    Evaluate Theorem 6.1 with p_i from Prop 6.1.3 at all three published parameter
    sets and compare against SPEC Table 5. It misses the published DFR target at
    every level (by 5.75 / 6.08 / 12.28 bits), while the 6.1.4 reading clears at
    every level. The document therefore disambiguates A19 against itself, and the
    16.79-bit 'value' is the size of a reader's error, not of a defect in HQC.
  baseline_comparison: >-
    NOT APPLICABLE and stated rather than left blank. BATCH-002 makes no algorithmic
    claim, so there is no Pollard-rho, BSGS or specialized-ISD baseline to compare
    against. dominated_by is undefined here rather than null. The only comparison
    made is between two internal analytic bounds of the same specification, and it
    is checked in O1.
  heuristic_challenges:
    - "A17's two probability spaces are separated correctly and this is the batch's best work; but the A5 => A17 implication is reported without its space quantifier (O3)."
    - "The sensitivity's first-order coefficient K is correctly labelled a scale and not a bound, and the producer says so itself; no objection."
    - "The gamma extraction rests on a Gaussian interpolation of four published quantiles and is labelled as such; no objection."
  cost_model_challenges:
    - "The conservatism budget (2.72/4.25/5.40 bits) is correctly derived but is compared against a quantity it cannot be compared with (O1)."
    - "'Cheaper' is used as a proxy for 'more valuable' in the retarget recommendation, and once A19 is resolved its value is zero bits of movement (O1)."
  reduction_and_scope_challenges:
    - "No scope inflation found. Every artifact and every commit message keeps the claim tier at toy and makes no HQC security claim in either direction."
    - "The A17 negative is properly bounded to two documents at two hashes, and I strengthened it with a vocabulary-robustness control the producer did not run."
  proof_architecture_challenges:
    - "Lemma L1 (exchangeability by cyclic symmetry) and Lemma L2 (the inner failure event is increasing) are both correct as argued; no objection."
    - "Jordan inclusion-exclusion reduction to the joint moments uses no independence and is correct; the reduction of the sensitivity to mu_m at the published depth reproduces (leading-term shares 0.999006/0.999880/0.999245)."
  narrowest_supported_statement: see section 6
  next_concrete_action: >-
    Run C1 into the ledger archive, file A19 as a documentation correction in the
    same CORR family as the printed 49, and keep DEC-20260802-344883's A17 lane
    open under the producer's own preferred name mu_{delta_e+1} on space (T).
    Do not redirect the campaign to A19.
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    fallback_used: true
    model_verified: false
    independent_session: true
    independent_model: false
    closure_quorum_admissibility: NOT_ADMISSIBLE
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-002/reviews/TASK-20260802-caddef/red_team_report.md
```
