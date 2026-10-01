# REVIEW-SEMBIN-20260916-e0a0c1 — composition and ruling

**Task** `TASK-20260916-a8e5b5` · **Goal** `GOAL-SEMBIN-fcb7a2` · **Batch** `BATCH-e0a0c1`
**Round** `REVIEW-SEMBIN-20260916-e0a0c1` · **Opened by** `DEC-20260916-441cd5`
**Composed** 2026-09-21 · **Zero runs, zero measurements**
**This file is the text `TASK-20260916-d4fb62` commits as `DEC-20260916-87fc5c`.**

---

## 0. Bottom line, before the detail

1. **P-4 is refuted, three times over.** The prior the predecessor Coordinator said it
   would rather lose is the one it lost, and it lost it more comprehensively than the
   falsification condition anticipated: the upstream lemma does not deliver Lemma 4; the
   form P-4 named is *identical* to the form P-4 says the lemma does not license; and the
   statement P-4 asserts is licensed is **false**, with two independent witnesses and two
   independent implementations.
2. **Inertness holds.** Adjoining `S_fe` to the *fake* system changes `d'_F` by nothing.
   Confirmed by the Nagao reader exhaustively on its own witness, and independently by
   `tools/lemma4_inside_form.py` on its own witness and on 300 random multilinear pairs at
   `N = 3` with zero disagreements. Re-run in this task: 15/15 tests pass.
3. **So the campaign believed something wrong, in two layers, and this ruling names both
   without softening.** Layer one is a naming defect that has stood since 2026-09-16 and
   propagated into this task's own dispatch card. Layer two is a substantive belief —
   that the form the campaign depends on was unrefuted — which was true when recorded on
   2026-09-16, was refuted on 2026-09-21 at 14:06:43 UTC by the campaign's own tooling, and
   is already corrected in the ledger by `CORR-20260921-942a62` while the frozen contract's
   `S-5` still says "UNPROVEN" and needs an additive amendment. Section 4.
4. **There is now no placement of the field equations under which a universally quantified
   `d_F ≤ d'_F` survives at the contract's declared equality convention.** That is the
   headline finding of this round and it is stated at its narrowest supported scope in
   section 5.
5. **The escalation condition fired and is honoured.** The claim stays **un-promoted**; the
   goal stays **`active`** with an impediment recorded against the *claim*; nothing is
   softened to fit a servable review tier. Section 6.
6. **`EV-SEMBIN-1ca3c8` IS produced**, scoped narrowly to the counterexample certificate
   and explicitly **not** to the textual reads. Section 7 gives the reasoning and the
   drafted record.
7. **The independence gate is NOT satisfied and this ruling does not declare it satisfied.**
   Four of the six reported problems are checker limitations; two are genuine procedure
   deviations, one of them a defect in the plan itself. The checker is not loosened.
   Section 8.

---

## 1. Every joint, with its verdict

The plan declared five joints. **No joint went unowned.** Both owners filed all six declared
artifacts; both packages are hash-bound by `TASK-20260916-92128f` at
`4b7edadfbd42489f1a120157c1d29558fa992cce`.

| joint | owner | verdict | composed by this ruling |
|---|---|---|---|
| J-1 | `TASK-20260916-9da6e0` | **holds** | accepted, at **reduced evidential weight** — see 1.1 |
| J-2 | `TASK-20260916-9da6e0` | **holds** | accepted in full; independence here is unqualified |
| J-3 | `TASK-20260916-9da6e0` | **breaks** (reader token: `breaks_as_printed_holds_conditionally_on_usage_form`) | accepted; composed as **breaks** — see 1.3 |
| J-4 | `TASK-20260916-64a93b`, via card sub-joints J-4a/J-4b/J-4c | **breaks** | **owned and discharged** by the sub-joints — see 1.4 |
| J-5 | **both** readers, each on its own joints | **split: passes (Nagao half), FAILS (Semaev half)** | accepted as a split verdict, which is the correct outcome — see 1.5 |

### 1.1 J-1 — holds, and what that confirmation is now worth

The statement 2015/984 quotes as its "Lemma 3 ([11])" is **Lemma 2 of Nagao 2013/549**
(pymupdf 303–313; frozen md 685–708), matched on content. 2013/549 *has* its own Lemma 3
(pymupdf 471–478) and it is an unrelated weight-degree statement about monomials, so a
reader matching on number would have reported on the wrong statement. The restatement in
2015/984 is faithful in mathematical content, with three transcription defects (R-1 an
added and unproved reduction-to-zero ⟺ ideal-membership equivalence; R-2 an `M`-versus-`N`
index count; R-3 a symbol collision between Lemma 3's field-equation multipliers and Lemma
4's system generators).

**The card asks: if J-1's answer was available before the reader derived it, what is J-1's
confirmation worth?** Two leaks, not one, and the second is the Coordinator's own:

- The reader disclosed that `inputs/NAGAO-2013-549/errata-extraction-20260921.md` — which
  its card directed it to read — names Lemma 2, twice. It records the leak rather than
  claiming a blindness it did not have.
- **The answer was already in this program's committed ledger.** `GOAL-SEMBIN-fcb7a2`'s own
  completion-criterion-4 status line, citing `DEC-20260913-8d19e5`, reads: *"the Lemma 3
  statement 2015/984 declines to prove IS present and proved as 2013/549 Lemma 2."* The
  predecessor Coordinator wrote P-1 as a prediction about a question its own goal head had
  already answered. That is a larger qualification than the errata leak and nobody
  disclosed it, because the reader could not see the goal head and the plan's author did
  not look.

**Ruling.** The bare identification is **corroboration, not a test**. It should not be read
as evidence of Coordinator calibration and it is scored accordingly in section 2. What J-1
*did* produce at full weight, because no prior record contained it:

- the three transcription defects R-1/R-2/R-3, of which **R-1 is load-bearing** — it is the
  unproved equivalence the campaign inherits as `U-2`, and R-3 is the most plausible route
  by which Lemma 4 acquired its wrong placement;
- a **second independent anchor** into `[11]`: 2015/984's Lemma 5 is content-identical to
  2013/549's Lemma 9, also renumbered, also content-matched. Two independent citations into
  the same paper, both with shifted numbers, is a much stronger identification than one;
- the observation that 2015/984's Example 1 is internally inconsistent as printed.

### 1.2 J-2 — holds, unqualified

Lemma 2 is **proved** (pymupdf 314–414) and the proof is complete on its own terms once six
write-up defects are filled, none of which needs a new idea. The measure `ψ(G)` is
well-founded because a monomial order well-orders the monomials; the base case is not
stated but is present in effect (terminal tuples are `NUM(G) = 1` or `deg ψ(G) = D`); the
inductive step preserves membership in the representation set and strictly decreases the
measure, verified by executing the construction; and no hypothesis absent from the
statement is used. The graded order is *chosen inside the proof* and exists unconditionally
(grevlex), so it is load-bearing without being a hidden hypothesis.

Two items this ruling carries forward:

- **D-3 is false as printed** — claim 1) asserts `X_{I_1}^p | G_{I_i}` for the whole
  multiplier, and the reader exhibits a witness (`p = 2`, `G = (X + Y², Y + X²)`) where it
  fails. The repair is to weaken it to the leading term, which is what the rest of the
  proof uses. Recorded because a false claim in a published proof is a fact about the
  source, not a reader's opinion.
- The graded-order hypothesis is **invisible in the frozen markdown**: `paper_fulltext.md`
  721–734 renders it as a per-variable comparison that says nothing, so a reader confined
  to the frozen text would conclude the proof rests on an empty condition. This is a
  standing hazard for every future reader of that input package and is a next action.

Nothing leaked J-2. Its independence is the real thing the blind bought, exactly as the
plan predicted it would be.

### 1.3 J-3 — breaks

**Accepted, and this is the escalation trigger.** Lemma 2 does **not** support Lemma 4 as
printed, and Lemma 4 as printed is **false**.

The derivation from Lemma 2 necessarily puts multipliers on the field equations, so it
needs them as **members of the system whose `d_F` is claimed** — the reader's `(H3)` /
`U-3`. Lemma 4 as printed leaves the true side as `{f_1..f_M}` alone, so `(H3)` fails. What
the derivation actually delivers is

```
d_F({f_1..f_M} ∪ S_fe)  ≤  max_i deg(g_i f_i)        [UNREDUCED products]
```

and turning that into `≤ d'_F` needs a further hypothesis `(H4)` / **`U-4`**: the witness
realising `d'_F` must lose no total degree under reduction mod `S_fe`. **`U-4` is stated
nowhere in either paper**, does not follow from Definition 6 (which bounds only the
*reduced* product degree), and cannot be closed by Lemma 2 — Lemma 2's bound is relative to
`deg R`, and `deg R` is itself governed by the unreduced product degree, one step upstream.
`U-4` is the entire distance between what Lemma 2 gives and what Lemma 4 claims, and it is
this round's single most useful addition.

The reader's counterexample, independently constructed from the definitions **before** it
read `CORR-20260916-96f47d`:

> `p = 2`, `F_2[X, Y]`, `f_1 = X²Y`, `f_2 = XY + X`. Fake `d'_F = 2`. True `d_F = 3` with
> `S_fe` outside (both readings) and `d_F = 3` with `S_fe` inside under the equality
> reading. So `d_F = 3 > 2 = d'_F`.

The mechanism is that `f_1 = X²Y` is **not reduced** mod `S_fe`: the fake world sees `XY` of
degree 2, the true world sees degree 3.

**The reader's compound token is honest and I am composing it down deliberately.** It wrote
`breaks_as_printed_holds_conditionally_on_usage_form`. The conditional half is real and
valuable: 2015/984's *only* use of Lemma 4 — the proof of its Lemma 6 — puts the union on
the **true** side and absent from the fake side, the exact reverse of Lemma 4's printed
placement and the sound direction; 2013/549 never states Lemma 4 at all and states the
specific estimate over `n + N` equations, which makes the field equations members by
construction; and in both of those settings `U-4` is discharged by explicit bookkeeping
(`deg g_i ≤ 1`, generators already reduced) rather than by the fake definition. That is the
campaign's forward path and section 9 turns it into a next action. But the plan's J-3
question was whether the upstream statement supports Lemma 4 **in the form the campaign's
contract depends on**, and the answer to that question is no. The composed verdict is
**breaks**.

### 1.4 J-4 — owned, discharged by its sub-joints, verdict breaks

The checker reports that `TASK-20260916-64a93b` does not claim `J-4`. It claims `J-4a`,
`J-4b` and `J-4c`, **because its task card decomposed the joint that way** — the
decomposition is the dispatcher's, not the reader's (see the card's `handoff.questions`).
The three sub-joints jointly answer the plan's J-4 question verbatim and answer more of it
than the parent question asked. **J-4 is owned and discharged.** It is not unowned and it
is not dropped. The schema gap and the plan-versus-card divergence are adjudicated in
section 8 (problem iv).

- **J-4a — answered, with a recorded ambiguity the reader was instructed not to resolve by
  choosing.** The campaign consumes Semaev's §4.5 first-fall-degree result — the number 4 —
  and consumes it **through** Nagao's Propositions 2 and 5, not directly. And: **no record
  of this campaign cites 2015/310 at all.** Not `H-SEMBIN-a7e721`'s citations block, not
  `EXP-SEMBIN-4fa22c`'s; the experiment's `dependencies` name only the Nagao fulltext. The
  consumed statement exists in this campaign's records **only as unanchored prose inside a
  `mechanism` field**, with no section, equation, page or line anchor and no provenance
  marking. Within §4.5 the paraphrase does not pick between a system-level "proved to be 4"
  (:97) and the body's explicitly partial "at least `t − 2` of the equations" (:598-599),
  which are materially different claims.

  **I rule this a defect in the campaign's own records, not merely an observation.** A
  citation that cannot be checked without redoing this task's work is not a citation. It is
  fixed by the additive amendment in section 9 and not by editing the frozen contract.

  The reader also records that `H-SEMBIN-a7e721`'s LINK 1 calls Semaev's quantity the
  *fake* first fall degree, which is right about Semaev's **computation** and wrong about
  Semaev's **definition** — Nagao says so in terms (`NAGAO-2015-984` :452-459, "He uses the
  true definition of first fall degree"). LINK 1 therefore understates the paper in one
  direction while correctly identifying what the argument computes. Carried as a
  next action; it does not move the hypothesis.

- **J-4b — answered.** What is **proved**: the **fake** first fall degree of the
  **non-terminal** links is at most 4, by a single **uniform** witness (the variable `x₁`),
  with the strongest available quantifier order — for all `n`, all `V`, all `B`, all
  non-terminal links, one fixed object exhibits the fall. For one such link taken alone the
  value is **exactly** 4, a lower bound the reader supplied and the paper did not argue.
  What is **not** proved: the terminal equation (experimental, and Semaev says so); the
  field-level-to-descended-system transfer (true, but it is Nagao's Lemma 5, not stated in
  2015/310); the fake→true conversion (absent — it is Nagao's Lemma 4, the object this
  round just refuted); and `d_ff → d_F4` (a declared assumption the paper itself calls "not
  generally correct").

- **J-4c — breaks.** Three separable components, and a consumer relies on a different side
  of each. **GAP-1 QUANTITY** (heaviest): the statement is about the true degree and about
  `d_F4`; the argument delivers the fake degree of a subset of the equations, and the two
  conversions that separate them are in neither paper. **GAP-2 COVERAGE** (sharpest,
  because exact): system (5) has `t − 1` equations and the argument reaches `t − 2`, so one
  — the terminal link — is uncovered at every `t`, and at `t = 2` the count is **zero**
  while Assumption 1's range `2 ≤ t ≤ m` **includes** `t = 2`. **GAP-3 QUANTIFIER**:
  universal statements on typical-instance evidence at `n ≤ 21` (one cell at 40), `m ≤ 6`,
  against a FIPS conclusion drawn at `n = 409, 571` and `m = 11, 12` — disclosed in the
  body as "very likely", not carried into the introduction or the abstract.

  The reader also records one thing that **is not** a gap although it looks like one:
  Semaev's exhibition survives affine coset shifts, because squaring over `F₂` is
  `F₂`-affine on coordinates. Recorded here because it bears on the reach of the argument
  and because suppressing a finding that cuts against the campaign's own mechanism would be
  the exact failure this round exists to prevent.

### 1.5 J-5 — split, and the split is the correct outcome

The plan assigned J-5 to **both** readers, each running the control on its own joints. The
two halves therefore ran different arguments against different objects and reached opposite
outcomes. That is not an inconsistency; a proves-too-much control is a control on an
*argument*, and there were two arguments.

- **J-5 (Nagao half) — CONTROL PASSES.** Run against the known-false outside form, the
  reader's J-3 derivation does **not** go through, and it fails at exactly step 6 — the one
  step that uses the field equations as members, which is the same step whose absence makes
  the outside form false. A derivation that survived, or that broke somewhere else, would
  have told us the derivation was wrong. It broke in the right place.
  - **Second control finding, which also bites.** Under the printed `>=` reading of
    condition (1), the inside form goes through **without Lemma 3 at all**. An argument that
    succeeds without its stated main ingredient is the other kind of proving-too-much. This
    independently corroborates `EXP-SEMBIN-4fa22c`'s declared equality convention, reached
    from the upstream lemma's necessity rather than from Assumption 1's degeneracy — a
    different route to the same convention than the contract took, which is worth more than
    agreement reached the same way twice.

- **J-5 (Semaev half) — CONTROL FAILS.** The paper supplies its own known-false object at
  §4.5.1 (:1054-1058): *"the maximal degree (regularity degree) generally exceeds 4 when
  `k > ⌈n/m⌉` though the first fall degree is still 4."* On that same family, measured by
  the same author with the same instrument, the argument's **premise holds** and its
  **conclusion is false** — he says both. And the argument runs there unchanged, because
  `k` appears nowhere in it. Verified mechanically over two fields, every `k = 1..n`, random
  subspaces, the mixed shape of system (5), and coset shifts; the underlying reason is the
  single fact `deg_{F2}(x^a) = popcount(a)`, a property of the Frobenius in which `dim V`
  does not appear.

  **What this establishes, at its narrowest.** Assumption 1 is **not refuted** — its
  hypothesis `k = ⌈n/m⌉` excludes the regime and it is stated correctly. What is
  established is that the **justification** offered for Assumption 1 does not distinguish
  the regime where it is believed from the regime where the author reports it false:
  everything offered in support of `d_F4 ≤ 4` at `k = ⌈n/m⌉` would equally support it at
  `k = ⌈n/m⌉ + 1`, where the paper says it is wrong. Nothing here measures `d_F4` at any
  `k`; the falsity at `k > ⌈n/m⌉` is the paper's own report, taken at face value.

  The contrast control matters and is why this is a finding rather than a generic complaint
  about upper-bound arguments: run against the terminal equation `S₃(x₁,x₂,z)`, where the
  multiplier `x₁` gives no fall, the argument **correctly refuses** and Semaev flags the
  refusal. So it has a working discriminator along the equation-type axis and **none** along
  the `dim V` axis.

---

## 2. Every prior, scored

Machine-readable in `scored-priors.json`. A refuted prior is recorded here **at least as
prominently** as a confirmed one, and the two most informative entries — P-4 and P-5 — are
refutations.

### P-4 — **REFUTED.** The load-bearing one, and the one the predecessor said it would rather lose.

P-4 claimed that 2013/549's Lemma 2 licenses `d_F ≤ d'_F` **in the INSIDE form**, which P-4
defined parenthetically as *"`d'_F` taken of `{f_1..f_M} ∪ S_fe`, which is how 2015/984's
Lemma 4 is written"*, and does **not** license the outside form the program's counterexample
already falsifies.

It fails on three independent grounds, any one of which is sufficient:

1. **J-3 breaks.** Lemma 2 does not license Lemma 4 in the printed form. The derivation
   needs `U-3` (field equations as members of the true system) and `U-4` (unreduced product
   degrees bounded by `d'_F`); Lemma 2 supplies neither, and neither is stated in either
   paper. This is precisely P-4's declared falsification condition — *"the proof is
   incomplete, the statement is weaker than the consumer needs"* — met.
2. **The distinction P-4 draws does not exist.** `S_fe` on the *fake* side is inert.
   Therefore `d'_F({f} ∪ S_fe) = d'_F({f})`, and P-4's "INSIDE form" is literally the same
   statement as the "outside form" P-4 says the lemma does not license and that the program
   had already falsified. **P-4 asserts that the upstream lemma both licenses and does not
   license one statement.** It is not merely false; as written it is incoherent. This is
   P-4's third falsification condition — *"the inside/outside distinction turns out not to
   be the operative gap"* — met, in the strongest available form.
3. **The statement P-4 says is licensed is FALSE.** Two independent witnesses
   (`X²Y, XY + X` at `N = 2`; `X₁X₂ + X₃, X₁X₃ + X₂` at `N = 3`) from two independent
   implementations, with a 23.5% violation rate on 400 random multilinear pairs at `N = 3`.

This is the most valuable outcome the batch could produce, it is exactly the outcome the
plan named as most valuable, and it is recorded as such.

### P-5 — **REFUTED in the specific sense it named**; its genus was right.

P-5 claimed the gap in Semaev 2015/310 is that *"the argument bounds the quantity at a fixed
or typical instance while the statement quantifies over all instances."* The reader finds
the opposite about the argument: its quantifier order is the **strongest available**, a
single uniform witness good for all `n`, all `V`, all `B`, all non-terminal links —
"**not** a per-instance witness dressed up as a uniform one" (B-2). The gap is real but is
of a different shape: **quantity** (fake vs true; `d_ff` vs `d_F4`) and **coverage**
(`t − 2` of `t − 1` equations). A quantifier slide does exist, but in the **experimental
support for Assumption 1**, which is not the argument P-5 was about.

The plan recorded P-5 at low confidence and called it "close to a guess about a genre of
gap". The genre was right — statement stronger than argument — and the mechanism was wrong.
Scored **refuted**, because the plan wrote "in the specific sense that", and a prior scored
on its genus rather than its stated content is a prior that cannot be lost.

### P-2 — **REFUTED (mechanism)**, on a ground neither the plan nor the reader stated.

P-2 claimed the Lemma 3 / Lemma 2 numbering mismatch has a mundane explanation: the served
PDF is the second of two revisions whose note records deleting the content of §4, and
"deleting content plausibly renumbered the lemmas". **It cannot have, for a §2 statement,
and the served text shows the author did not renumber at all.**

- Lemma 2 is in **§2** (pymupdf 303). The deletion was of **§4** content (pymupdf 35). A
  later deletion cannot shift an earlier statement's number.
- The served text's numbering runs Lemma 1…9, then **Lemma 11, 12, 13** — a hole at 10.
  Verified directly by this task against
  `inputs/NAGAO-2013-549/paper_fulltext.pymupdf.txt` (lines 262, 303, 471, 536, 554, 590,
  646, 689, 710, 813, 829, 867). A paper that leaves a hole at 10 after deleting content
  did not renumber; it left gaps. So no statement shifted, and Lemma 2 was Lemma 2 in the
  first revision too.

**This is a Coordinator inference from two reader-established facts plus one direct check of
a frozen file, not a reader verdict.** It is recorded as such and is checkable by anyone.
What caused 2015/984 to write "Lemma 3" is **not** thereby determined, and this ruling does
not claim it is: a plain miscitation remains open, and the first revision is not served.

P-2's embedded sub-prediction — that the reader would be **unable** to check the first
revision and would report that limit rather than paper over it — is **confirmed**. The
reader declined to reason about a version it could not open and recorded it as a
cannot-determine.

### P-6 — **CONFIRMED in its consequent, REFUTED in its stated mechanism.**

The consequent happened: both reads reported "could not determine" items on formulas that
matter (Nagao CND-1..3; Semaev CND-1..6). The **mechanism** P-6 gave did not. P-6 attributed
this to the 2013/549 extraction being materially worse; the Nagao reader reports the
opposite — *"Nothing in Lemma 2's statement or proof was undeterminable. The `pymupdf`
extraction is intact throughout that passage."* It routed around the defect using the
errata's clean companion and direct PDF reads, and the cannot-determines that remained are
about **authorial intent** (is the printed `>=` a lost prime glyph?) and about the **other**
paper.

**And P-6's stated mechanism is refuted in a way that matters more than the score.** The
reader settled the open extraction question `CORR-20260916-96f47d` left in
`residual_uncertainty`: the `>=` in Definitions 5 and 6, and the bare `d_F` where Definition
6 should print `d'_F`, **are in the PDF**. They are not extraction artifacts. The question is
now about Nagao's intent, which is not recoverable from this text. That is a genuine
narrowing of a recorded residual and is a next action.

The deeper extraction problem was found at a different place than P-6 predicted, and is
worse: the frozen markdown of 2013/549 destroys the **graded monomial order hypothesis**
that Lemma 2's proof depends on, at lines 721–734, leaving a condition that reads as
vacuous. A reader confined to the frozen text would conclude the proof rests on nothing.

### P-1 — **CONFIRMED, and it was not a live prediction.**

Confirmed on the merits: the match is 2013/549's Lemma 2. But the answer was in this
program's committed ledger before the plan was written (`GOAL-SEMBIN-fcb7a2` criterion-4
status line, citing `DEC-20260913-8d19e5`), and it was additionally in an in-scope
program-authored errata the reader's own card told it to read. Scored `confirmed` with
`was_a_live_prediction: false`, so that a later reader measuring this program's calibration
does not count it.

### P-3 — **CONFIRMED.**

`local polynomial` names the ambient ring `F_p[X_1..X_N]` with `N = d·n'`, not an extra
restriction, and 2015/984 dropped **no** hypothesis when restating the lemma. The reader
lists Lemma 2's complete hypothesis set and locality appears as the ring, exactly as P-3
predicted. Recorded with its context intact: P-3 was written down **because the
Coordinator's first reading had been the opposite** and it had refuted itself within
minutes. The confirmation is worth having and the honest reading of it is that the
predecessor's *second* reading was right, not that its instincts were.

One qualification the reader adds and P-3 did not anticipate: the restatement carries an
**addition** rather than a subtraction — R-1, the unproved reduction-to-zero ⟺
ideal-membership equivalence, inherited by the campaign as `U-2`. P-3 asked whether anything
was dropped and the answer is no; nobody asked whether anything was added.

### Calibration summary

| | |
|---|---|
| confirmed | P-1 (not live), P-3, P-6 (consequent only) |
| refuted | **P-2**, **P-4**, **P-5**, P-6 (mechanism) |
| untested | none |

Three of six refuted, including the one declared load-bearing, and one of the three
"confirmed" was not a prediction at all. **The round overturned the Coordinator more than it
confirmed it, which is the outcome the plan said it wanted and is recorded without
softening.** The plan's central methodological choice — write the prior first, bar the
reader from it — is vindicated for the second time in this campaign.

---

## 3. Inertness: the ruling

**Inertness holds. I rule it established at the scope stated below.**

The claim: adjoining `S_fe` to the **fake** system leaves `d'_F` unchanged. Every member
`X_j^p − X_j` given its own multiplier `h_j` contributes `h_j(X_j^p − X_j) ≡ 0 mod S_fe`,
identically, for every `h_j`. Definition 6 states all three of its conditions mod `S_fe`, so
such a member contributes `deg = −∞` to condition (1) and nothing to conditions (2) and (3).
All three conditions are unchanged and so is the minimum over witnesses.

Three independent supports:

1. **A derivation**, one line, from Definition 6 as printed. It needs no computation and is
   checkable by reading.
2. **The Nagao reader**, exhaustively on its own witness under **both** readings of condition
   (1) (`recheck.out` 92–102), in a session that never read `tools/lemma4_inside_form.py`.
3. **`tools/lemma4_inside_form.py`**, an implementation written from the definitions in an
   earlier session which that reader never read and which does not reference its arithmetic:
   equal on its own witness, and on **300 random multilinear pairs at `N = 3` with zero
   disagreements** (`TestTheFakeSidePlacementIsInert`). Structurally, `first_fall_degree`
   drops generators that reduce to zero, which is inertness realised in code rather than
   asserted.

**Re-verified by this task**: `python3 tools/test_lemma4_inside_form.py` → 15 tests, OK;
`python3 tools/lemma4_inside_form.py` → refutation reproduces, fast eliminator and literal
enumeration agree 80/80, 94/400 random multilinear pairs violate the inside form (23.5%).

**This is a blind re-derivation, and I am citing it as one.** Two implementations, written
without sight of each other, computing the same quantities from the same printed
definitions, agreeing on two witnesses and on inertness. Per AGENTS.md "Review architecture",
agreement is then evidence **about the quantity** rather than about either implementation —
which is what validation, recomputing from the producer's own artifacts, structurally cannot
buy. It composes nothing and rules on nothing; the composition is this document's job.

**Scope.** `p = 2`, `N ≤ 3`, `F_2`, Definition 6 as printed under both readings of condition
(1). It asserts nothing about `p ≥ 3` and nothing about descended summation-polynomial
systems at `n ∈ [7,12]`.

---

## 4. What the campaign believed that was wrong, and for how long

The card asks me not to soften this. I will not. There are **two** wrong beliefs, they are
different in kind, and only one of them was ever correct when it was written.

### 4.1 WRONG-1 — the naming defect. Standing 2026-09-16 → this ruling, five days, and it reached this task's own card.

Four committed documents locate Lemma 4's inside/outside distinction on the **fake** side:

| document | what it says | status |
|---|---|---|
| `read-plan.yaml` P-4 | "the INSIDE form (`d'_F` taken of `{f_1..f_M} ∪ S_fe`…)" versus "the outside form" | **void as a distinction** |
| `BATCH-e0a0c1` opening report | "Lemma 4's **literal** form — with the field equations *outside* the fake system — is **false**" | **misdescribes Lemma 4 as printed** |
| `checkpoints/BATCH-e0a0c1.yaml` | "Lemma 4's LITERAL form — field equations OUTSIDE the fake system — is FALSE" | same |
| this task's own dispatch card | repeats the fake-side framing | same |

Lemma 4 as printed puts `S_fe` **inside** the fake system and **outside** the true one. The
three documents that say "outside the fake system" describe a placement Lemma 4 does not
have; and because the fake side is inert, the "inside" and "outside" forms those documents
distinguish are **one statement**, already falsified on 2026-09-16 by the counterexample
`CORR-20260916-96f47d` records.

So for five days this campaign ran a lane whose central question — *does the upstream lemma
support the inside form and not the outside one?* — could not have a "yes" answer, because
the two forms it named were the same statement and one of them was known false. The reader
caught it. The round's design caught it: this is what a proves-too-much control is for.

**What this cost.** Less than it might have. The lane was still worth running — it produced
J-3, `U-4`, the `U-1..U-7` inheritance list, the extraction hazard, and the whole Semaev
read, none of which depended on the naming. But it means the plan's P-4 was unfalsifiable in
one direction and incoherent in the other, and a prior that cannot be confirmed is only half
a prior.

**What was NOT wrong.** `CORR-20260916-96f47d` drew the distinction on the **true** side and
drew it correctly: *"Lemma 4 puts `d_F` on `{f_1..f_M}` with the field equations OUTSIDE the
**left-hand** system"*, and its "with the field equations INSIDE" clause exhibits a true-side
fall. The goal head's ranked item (2) and `tools/lemma4_inside_form.py` inherit that correct
framing. **The drift is in the documents that restated the correction, not in the correction.**
That is worth recording precisely, because the cheap and wrong lesson here would be "the
2026-09-16 correction was sloppy", and it was not.

### 4.2 WRONG-2 — the substantive belief. Recorded 2026-09-16, refuted 2026-09-21 14:06:43 UTC, ledger corrected the same day; the frozen contract still carries it.

`CORR-20260916-96f47d` recorded: *"the INSIDE form the paper actually uses holds in every
instance checked and is not proven in general here."* `EXP-SEMBIN-4fa22c`'s success
criterion **S-5** froze that into the contract: *"Lemma 4's inside form, which is UNPROVEN
and whose literal form is verified false."*

Both were **accurate when written**. Neither is accurate now:

- `tools/lemma4_inside_form.py`, committed at `c55103916` on **2026-09-21 14:06:43 UTC**,
  refutes the true-side inside form with `f_1 = X₁X₂ + X₃`, `f_2 = X₁X₃ + X₂` over `F_2` at
  `N = 3`: `d'_F = 2`, `d_F = 3`.
- The Nagao reader's witness `X²Y, XY + X` refutes it again, independently, and also kills
  the outside form, under the equality reading — so a **single** object refutes **both**
  true-side placements.
- `CORR-20260921-942a62` records the refutation in the ledger, as `recovered_finding`, the
  same day.

So the ledger is already corrected. **The frozen contract is not, and cannot be**: S-5 is
immutable and says "UNPROVEN" where the honest word is now "REFUTED as a universal
statement". That is repaired by an additive amendment, never an edit (section 9, NA-1).

### 4.3 The composite, stated plainly

**There is no placement of the field equations under which a universally quantified
`d_F ≤ d'_F` is unrefuted, at the contract's declared equality convention.**

| placement | status | refuted by |
|---|---|---|
| `S_fe` outside the true system (= Lemma 4 as printed, by inertness) | **FALSE** | `CORR-20260916-96f47d`'s witness; the reader's witness; `tools/lemma4_inside_form.py` |
| `S_fe` inside the true system (the form the campaign depends on) | **FALSE** | `tools/lemma4_inside_form.py`'s witness; the reader's witness |
| `S_fe` inside or outside the fake system | **not a distinction** | inertness |

The campaign's recorded residual — *the outside form is refuted, the inside form is the one
we depend on and it is unrefuted* — is dead in both halves. This is a bookkeeping error found
by the program's own reviewer, it is cheap, and concealing it would not be.

**The one honest caveat, stated because a refutation silent about the reading under which its
target is true is not honest about its own scope.** Under the literal `>=` printed in
2015/984, the inside form **holds** — and holds emptily, for reasons having nothing to do
with any upstream lemma (Koszul padding makes condition (1) free). The contract declares the
equality reading, 2013/549's own Definition 1 prints equality, and the Nagao reader reached
the same convention by a third route: if Lemma 4 genuinely rests on Lemma 3, the reading
cannot be `>=`, because under `>=` the derivation succeeds without Lemma 3. Three independent
routes to one convention is as close to settled as this text allows, and it is still a
**declared interpretation of an ambiguous source**, not a fact about Nagao's intent.

---

## 5. What this round establishes, at its narrowest supported scope

Stated so that the strength and the scope are both exact, because the escalation makes them
the only things carrying the finding.

**ESTABLISHED (mathematics, machine-checkable):**

> The statement "for all finite generator sets `F ⊂ F_2[X_1..X_N]`, `d_F ≤ d'_F`" — Lemma 4
> of Nagao ePrint 2015/984 — is **FALSE**, under the equality reading of condition (1) of
> Definitions 5 and 6, under **every** placement of `S_fe` in either system. Witnesses:
> `f_1 = X²Y`, `f_2 = XY + X` over `F_2[X,Y]`; and `f_1 = X₁X₂ + X₃`, `f_2 = X₁X₃ + X₂` over
> `F_2[X_1,X_2,X_3]`. The failure is not pathological: 94 of 400 random multilinear pairs at
> `N = 3` violate it (23.5%, seed 20260916).

**ESTABLISHED (mathematics, one-line derivation, thrice checked):** adjoining `S_fe` to the
fake system leaves `d'_F` unchanged, so Lemma 4's printed form and the form this program had
already falsified are the same statement.

**ESTABLISHED (textual, by an independent reader, on frozen hash-verified sources):**
2015/984's "Lemma 3 ([11])" is 2013/549's Lemma 2; Lemma 2 is proved and its induction is
well-founded, with six write-up defects of which one (D-3) is false as printed and
repairable; the derivation from Lemma 2 to Lemma 4 requires the unstated hypothesis `U-4`;
2015/984's only application of Lemma 4 uses the sound placement; Semaev 2015/310's §4.5
argument proves the fake degree of the non-terminal links by a uniform witness and reaches
neither the true degree nor `d_F4`; and that argument survives the paper's own known-false
object at `k > ⌈n/m⌉`.

**NOT ESTABLISHED, and not claimed:**

- **Nothing about Nagao's Proposition 5.** It may hold by another route. `DC-1` is untouched.
- **Nothing about Semaev's Assumption 1**, which is correctly stated and is not refuted by
  its justification's `k`-blindness.
- **Nothing about descended summation-polynomial systems at `n ∈ [7,12]`**, the objects
  `EXP-SEMBIN-4fa22c` measures. A counterexample refutes a universally quantified statement
  and says nothing about a typical instance, still less about a structured family.
- **Nothing about `p ≥ 3`.** Every witness is over `F_2`.
- **Nothing about `d_F4` at any `k`.** No task in this round measured it.
- **Nothing about the first revision of 2013/549**, which is not served and was not
  fetchable.
- **Nothing about any elliptic curve, any deployed parameter set, or the security of
  anything.**
- **Nothing that moves `H-SEMBIN-a7e721` or `EXP-SEMBIN-4fa22c`.** No status changes in this
  ruling on the strength of a read of external sources; section 6.

**The transfer assumption, stated because it is the one a later reader will want.** From
"the universal statement is false" to "the campaign's inference is broken" requires that the
EQS4 instances be among the violating instances. **That is not established and this ruling
does not assume it.** What is established is that the inference can no longer be discharged
by *citing Lemma 4 as a theorem*; it must be discharged **instance by instance**, which is
exactly what both papers do in their own applications (`U-4` via `deg g_i ≤ 1` and reduced
generators). Section 9, NA-1 turns that into a protocol requirement.

---

## 6. The escalation, and the claim/campaign disposition

**The escalation condition has fired.** `TASK-20260916-9da6e0` found the upstream lemma
insufficient for the form the campaign's contract depends on (J-3 breaks), and found the
statement itself false.

**The CLAIM — that a published subexponential ECDLP bound rests on an unsupported lemma —
stays UN-PROMOTED.** Under AGENTS.md core rule 12 that claim is a contradiction of
established evidence and requires `review-breakthrough` at `max`, which is `degradable:
false` and **cannot be served in this environment** (`orchestration.adapter doctor --probe`
has no credentialed backend; `model_verified: false` throughout this round). I do **not**
substitute `validator` or `review-adversarial` to get it moving. That is the silent
downgrade the policy layer forbids, and the temptation is real precisely because two
`review-adversarial` reports are sitting in front of me saying what I would want a
breakthrough tier to say.

**Nothing in the finding is softened to fit a servable tier.** Section 5 states it at full
strength. What is withheld is *promotion*, not *content*.

**The CAMPAIGN stays `active`.** `paused` and `blocked` are not permitted `GOAL-*` statuses
and `tools/validate_ledger.py` refuses both by name. **An unservable review tier is an
impediment and is categorically NOT negative mathematical evidence** (core rule 5; CLAUDE.md
rule 10, item 2).

### Goal-head impediment entry — text for `TASK-20260916-d4fb62` to apply additively

This ruling writes only its two declared files. The following is the text the ledger archive
appends to `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`'s `impediments` list. It is additive;
it touches no existing entry, no `open_batches` entry, `current_batch_id`, or
`dispatch_queue_path`, and `BATCH-cbb416`'s checkpoint keeps the operative `next_action`.

```yaml
    - id: IMP-SEMBIN-FCB7A2-LEMMA4-TIER
      raised: '2026-09-21'
      recorded_under: DEC-20260916-87fc5c
      condition: >-
        pause_conditions item 4: review-breakthrough at max cannot be served by any
        reachable backend for a claim-changing round.
      what_is_blocked: >-
        THE CLAIM, NEVER THE GOAL AND NEVER THIS BATCH. Specifically: promoting to a
        program conclusion the claim that Nagao 2015/984's Proposition 5 -- and the
        subexponential bound of its Theorem 1 -- rest on an unsupported lemma. The
        underlying mathematical finding is NOT blocked and is recorded at full strength
        in DEC-20260916-87fc5c and EV-SEMBIN-1ca3c8: the universally quantified
        d_F <= d'_F is false over F_2 at N <= 3 under the declared equality convention,
        in every placement of S_fe. What is blocked is the step from that to a statement
        about a published complexity claim, which is a contradiction of established
        evidence under core rule 12.
      clears_when: >-
        `python3 -m orchestration.adapter doctor --probe` resolves a backend that serves
        review-breakthrough at max effort, AND an independent session at that tier
        reviews the claim and its cost model. Two backends resolving would additionally
        restore the goal closure quorum; one suffices for this impediment.
      recheck: >-
        python3 -m orchestration.adapter doctor --probe ;
        python3 -m orchestration.adapter resolve --role validator-breakthrough
      asserts_nothing_about: >-
        THE SCIENCE. An unservable review tier is an infrastructure fact. It is not
        evidence for or against Lemma 4, Proposition 5, Assumption 1, or any degree.
        It does not weaken the refutation and does not license restating it more
        cautiously than section 5 of the ruling states it.
```

### What would be needed to promote the claim later, concretely enough to act on

A session with a second backend can execute all of this from committed artifacts:

1. **Resolve the tier.** `python3 -m orchestration.adapter doctor --probe`, then
   `resolve --role validator-breakthrough` and `--role red-team-breakthrough`. Both must
   report a resolved model at `reasoning_effort: max` with `model_verified: true`. If only
   one backend resolves, the tier is served but the closure quorum stays suspended; that is
   sufficient for this impediment and not for closing the goal.
2. **Write the review plan first**, per AGENTS.md "Review architecture", before either
   reviewer runs, with the Coordinator's prior recorded. Joints, each with exactly one owner:
   - **JB-1** — is the counterexample arithmetic correct? Blind re-derivation from the
     statement of `d_F`/`d'_F` and the two polynomial pairs alone, `blind_from:
     [tools/lemma4_inside_form.py, tools/test_lemma4_inside_form.py,
     .../read-nagao-2013-549/recheck.py]`. This is a third implementation, not a re-run.
   - **JB-2** — is the equality reading of condition (1) the right one? The claim is void
     under `>=`, and the whole finding hangs on this. Attack it by trying to make the `>=`
     reading non-degenerate.
   - **JB-3** — does the refutation reach Proposition 5 at all? The gap in section 5's
     transfer assumption is the load-bearing step and is where I expect a breakthrough
     reviewer to push back hardest.
   - **JB-4** — red team on the cost model and the scope statement: what does refuting
     Lemma 4 cost Theorem 1's `O(n^{8w+1})`, and what does it not cost?
   - **JB-5** — proves-too-much: run the refutation argument against a lemma of this shape
     that is known **true** (for instance, the sound placement 2015/984's Lemma 6 proof
     actually uses, with `U-4` discharged). If the refutation also "refutes" that, it is
     wrong somewhere.
3. **Fill `proves_too_much.objects` in the structured field**, not in prose. This round's
   plan did not, and section 8 records that as a deviation.
4. **Then, and only then**, a Coordinator decision may promote. Until every one of those is
   in a committed artifact, the claim stays where this ruling leaves it.

---

## 7. `EV-SEMBIN-1ca3c8`: produced, and why

**Ruling: YES, this round produces `EV-SEMBIN-1ca3c8`** — scoped to the counterexample
certificate and **not** to the textual reads. The identifier was reserved, not promised, and
the plan left the decision to this ruling. Here is the reasoning, including the case against.

**The case against, taken seriously.** These are reads of external sources, not observations
of a research object. No run exists. Both readers explicitly disclaim being evidence about
any research object. The campaign's own precedent — the 2026-09-16 blind read that overturned
the Coordinator — was recorded as a correction plus a decision, with **no** evidence record,
and that was right: a reading of a text is a reading of a text.

**Why it is nonetheless produced.** Because this round did not only produce readings. It
produced a **counterexample certificate**: two explicit polynomial pairs over `F_2` whose
degrees are computable by exact finite arithmetic in milliseconds, reproduced by two
implementations written without sight of each other, pinned by 15 tests, and re-verified in
this task. That object is not a reader's opinion about a text. It is checkable by anyone,
forever, without trusting any agent in this program. And `agents/coordinator.md`
responsibility 12 routes exactly this object through an evidence record: the strongest
checkable refutation artifact is *"recorded as `proof_status`/`proof_refs` on the evidence
record and archived before the decision that relies on it."* The amendment in section 9
relies on it. So an evidence record is the contract's own answer, not an upgrade.

**The split is what makes both answers right.** The machine-checkable part becomes evidence;
the textual part is cited by the decision directly, at committed paths with recorded hashes.
A reading and a certificate are different kinds of thing and this round produced one of each.

### Drafted `EV-SEMBIN-1ca3c8` — for `TASK-20260916-d4fb62` to write to `ledger/evidence/EV-SEMBIN-1ca3c8.yaml`

```yaml
evidence:
  id: EV-SEMBIN-1ca3c8
  hypothesis_id: null
  hypothesis_id_note: >-
    NULL AND DELIBERATELY SO. H-SEMBIN-a7e721 predicts a measurable separation between
    shifted and unshifted descents; this record measures no such thing and cannot move it.
    Attaching it to that hypothesis would misfile a statement about a published lemma as
    a statement about EQS4.
  experiment_ids: []
  experiment_ids_note: >-
    EMPTY. EXP-SEMBIN-4fa22c CONSUMES the refuted lemma as a declared dependency; it did
    not produce this evidence and has taken no run. The relation is recorded by the
    additive amendment AMD-EXP-SEMBIN-4fa22c-20260921-lemma4, not by claiming the
    experiment as a source.
  run_ids: []
  run_ids_note: >-
    EMPTY, AND THIS RECORD IS NOT A MEASUREMENT. Zero runs were performed under
    TASK-20260916-9da6e0, TASK-20260916-64a93b or TASK-20260916-a8e5b5. What backs this
    record is exact finite arithmetic over F_2 in two independent implementations, which
    is a derivation carried out by machine, not a sampled observation.
  type: theoretical
  direction: contradicts
  strength: replicated
  strength_basis: >-
    Two witnesses that are genuinely different objects (X^2 Y and XY + X in two variables,
    not multilinear; X_1X_2 + X_3 and X_1X_3 + X_2 in three variables, multilinear), each
    computed by two implementations written without sight of each other, one by a blind
    reader in an independent session and one by the Coordinator from the printed
    definitions in an earlier session. Each implementation additionally carries its own
    internal oracle: lemma4_inside_form.py cross-checks its eliminator against literal
    cofactor enumeration (80/80 agreement) and the reader certifies its >=-reading lower
    bounds by two ring homomorphisms rather than by search. Not `strong`, because every
    witness is at p = 2 and N <= 3 and nothing has been checked at p >= 3.
  claim_tier: toy
  claim_tier_note: >-
    TOY, and that is the honest label for N <= 3 over F_2. It is not a weakness of the
    refutation -- a counterexample to a universally quantified statement is complete at any
    scale -- but it IS the exact reason this record asserts nothing about EQS4 at
    n in [7,12] or about any deployed parameter.
  certificate_refs: []
  proof_status: certificate
  proof_refs:
    - tools/lemma4_inside_form.py
    - tools/test_lemma4_inside_form.py
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/recheck.py
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/recheck.out
  observations:
    - >-
      Lemma 4 of Nagao ePrint 2015/984, read as the universally quantified statement
      d_F <= d'_F under the equality reading of condition (1) of Definitions 5 and 6, is
      FALSE over F_2, under EVERY placement of S_fe in either system.
    - >-
      Witness A (blind reader, TASK-20260916-9da6e0): f_1 = X^2 Y, f_2 = XY + X over
      F_2[X,Y]. d'_F = 2; d_F = 3 with S_fe outside the true system under both readings;
      d_F = 3 with S_fe inside the true system under the equality reading.
    - >-
      Witness B (tools/lemma4_inside_form.py, written independently and earlier):
      f_1 = X_1X_2 + X_3, f_2 = X_1X_3 + X_2 over F_2[X_1,X_2,X_3]. d'_F = 2, d_F = 3,
      refuting both true-side placements.
    - >-
      The two witnesses are different objects: witness A has two variables and is not
      multilinear; witness B has three and is. Pinned so they cannot silently collapse.
    - >-
      INERTNESS: adjoining S_fe to the FAKE system leaves d'_F unchanged, because every
      h_j(X_j^p - X_j) is 0 mod S_fe and Definition 6 states all three conditions mod
      S_fe. Verified exhaustively on witness A under both readings, and on 300 random
      multilinear pairs at N = 3 with zero disagreements. Consequence: Lemma 4 as printed
      and the form CORR-20260916-96f47d already falsified are THE SAME STATEMENT.
    - >-
      The failure is not pathological: 94 of 400 random multilinear pairs at N = 3 violate
      the inequality (23.5%, seed 20260916).
    - >-
      SCOPE NOTE, recorded because a refutation silent about the reading under which its
      target is true is not honest about its own scope: under the literal ">=" printed in
      2015/984 the inequality HOLDS and is empty, both quantities collapsing to
      1 + (least degree of a nonzero ideal element). The equality reading is
      EXP-SEMBIN-4fa22c's declared convention, is what 2013/549's Definition 1 prints,
      and is independently required by TASK-20260916-9da6e0's finding that under ">=" the
      derivation succeeds without Lemma 3 at all.
  inference: >-
    An inference of the form "d'_F was measured at v, therefore d_F <= v" may no longer be
    discharged by citing Lemma 4 as a theorem. It must be discharged INSTANCE BY INSTANCE,
    by exhibiting that the realising fake witness's UNREDUCED product degrees do not exceed
    d'_F -- hypothesis U-4 of TASK-20260916-9da6e0, stated in neither paper. Both papers do
    discharge it in their own applications, by explicit bookkeeping (deg g_i <= 1 and
    already-reduced generators), which is why their uses are unaffected by this record and
    a consumer transcribing the lemma literally is not.
  boundaries:
    - p = 2 only. Nothing is checked at p >= 3, where Proposition 2's bound is 3p+1.
    - N <= 3 variables. Nothing is checked at the N of any descended system.
    - >-
      The equality reading of condition (1). Under the printed ">=" the statement holds
      and is empty.
    - >-
      This record asserts NOTHING about Nagao's Proposition 5, which may hold by another
      route, and NOTHING about Semaev's Assumption 1, which is correctly stated.
    - >-
      It asserts nothing about descended summation-polynomial systems at n in [7,12], and
      nothing about any elliptic curve or deployed parameter set.
    - >-
      It does not license promoting the claim that a published subexponential bound rests
      on an unsupported lemma. That claim needs review-breakthrough at max under core rule
      12 and is blocked by IMP-SEMBIN-FCB7A2-LEMMA4-TIER.
  unresolved_confounds:
    - >-
      Whether the ">=" printed at NAGAO-2015-984 :401 and :439, and the bare d_F in
      Definition 6's conditions, are authorial or typesetting. TASK-20260916-9da6e0
      establishes they are IN THE PDF and not extraction artifacts -- narrowing
      CORR-20260916-96f47d's residual_uncertainty -- but authorial intent is not
      recoverable from this text.
    - >-
      Whether the EQS4 instances EXP-SEMBIN-4fa22c will measure are among the violating
      instances. Not established, not assumed, and the reason this record changes no
      experiment or hypothesis status.
  obstruction:
    statement: >-
      The fake first fall degree does not bound the true one. d'_F is computed after
      reduction mod S_fe and therefore cannot see the degree a generator or a product
      carries before reduction; a generator that is not reduced mod S_fe presents a
      strictly smaller object to the fake computation than to the true one, and the
      inequality d_F <= d'_F fails by exactly that difference.
    quantity: >-
      d_F - d'_F on {f_1, f_2} u S_fe over F_2, under the equality reading of condition
      (1), taken over random multilinear pairs at N = 3.
    value: >-
      +1 degree on both exhibited witnesses (d_F = 3, d'_F = 2). Violation frequency
      94/400 = 23.5% on random multilinear pairs at N = 3 (seed 20260916); binomial 95%
      interval approximately [19.5%, 28.0%]. Zero pairs in 400 had d_F < d'_F. Exact
      finite arithmetic, so the per-instance values carry no measurement error; the
      frequency is a sample statistic and its interval is stated as one.
    measured_by:
      - tools/lemma4_inside_form.py (survey_random_multilinear_pairs, trials=400, seed=20260916)
      - tools/test_lemma4_inside_form.py
      - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/recheck.py
    scope: >-
      F_2, N <= 3, multilinear pairs plus one non-multilinear two-variable witness,
      equality reading of condition (1), S_fe present as generators of the true system.
      Claimed nowhere else -- in particular not at p >= 3, not at the N of a descended
      system, and not on structured summation-polynomial systems.
    resource_check:
      examined: true
      reading: >-
        YES, AND IT IS THE MORE USEFUL HALF OF THIS RECORD. The obstruction is a
        reduced-versus-unreduced degree gap, and the same gap is the HYPOTHESIS of the
        forward path: since d_F - d'_F is exactly the degree lost to reduction, an
        instrument that RECORDS the unreduced product degrees of its realising witness
        discharges U-4 directly and recovers the inference the lemma can no longer carry
        as a theorem. That is how both papers already do it (deg g_i <= 1 on reduced
        generators), and it converts a broken citation into a measurable per-instance
        obligation. Independently, the 23.5% violation rate is itself a quantity worth
        having: it makes "how often does the fake degree mislead" a measurable property
        of a family rather than a yes/no question about a lemma, which is a better-posed
        question than the one this round started with.
      spawned_ids: []
      spawned_ids_note: >-
        EMPTY AT THIS RECORD'S WRITING, and the resource reading above is routed as
        next action NA-1 of DEC-20260916-87fc5c (the U-4 bookkeeping requirement in
        AMD-EXP-SEMBIN-4fa22c-20260921-lemma4) rather than as a new proposal. A resource
        candidate enters the ranking on its merits and changes no status by existing.
  reviewed_by: coordinator
  reviewed_by_note: >-
    Composed at TASK-20260916-a8e5b5 from two independent review-adversarial sessions on
    disjoint joints, plus a Coordinator cross-check by an implementation neither reader
    read. NOT reviewed at review-breakthrough: that tier cannot be served here, which is
    why this record stops at the mathematics and the CLAIM about a published complexity
    bound stays un-promoted (IMP-SEMBIN-FCB7A2-LEMMA4-TIER).
  citations:
    - ref: NAGAO-2015-984 (IACR ePrint 2015/984)
      provenance: retrieved
      claim: Definitions 5 and 6, Lemmas 3, 4, 5 and 6, and the only application of Lemma 4.
      verified_by: TASK-20260916-9da6e0 and TASK-20260916-64a93b, both of which read the frozen text and the PDF.
    - ref: NAGAO-2013-549 (IACR ePrint 2013/549, second revision)
      provenance: retrieved
      claim: Lemma 2 and its proof; the definition of `local polynomial`; the revision note.
      verified_by: TASK-20260916-9da6e0, which read the pymupdf companion in full and the PDF spans for the disputed passages.
    - ref: CORR-20260916-96f47d
      provenance: internal
      claim: the program's first counterexample, to the outside form, and the residual this record closes.
      verified_by: coordinator, TASK-20260916-a8e5b5.
    - ref: CORR-20260921-942a62
      provenance: internal
      claim: the recovered_finding that the inside form is false, and the provenance of witness B.
      verified_by: coordinator, TASK-20260916-a8e5b5.
```

---

## 8. The independence checker's six problems, adjudicated

Reproduced exactly as the tool reports them, against the round as filed. **I do not loosen
the checker**, and the dispatching session was right not to: a gate satisfied by weakening
the instrument that reports on it is worth less than a gate that fails honestly.

### (i), (ii) — J-1 and J-2 verdicts are nested mappings. **CHECKER LIMITATION.**

`TASK-20260916-9da6e0` filed `J-1: {verdict: holds, answer: …, confidence: 0.98}` and
`J-2: {verdict: holds, answer: …}`. The bare token the checker wants is **present**, as the
`verdict` key; the attestation carries strictly more than the schema expects — the answer,
and in J-1's case a numeric confidence. Rejecting a report for being more informative is a
schema defect, not a procedure failure. Recommendation in 8.7.

### (iii) — J-3's verdict is nested **and** its token is compound. **CHECKER LIMITATION**, with a composition ruling.

The token is `breaks_as_printed_holds_conditionally_on_usage_form`. The plan prescribed no
verdict vocabulary — the three-token vocabulary is the checker's — and the compound token is
information-preserving and honest: the joint genuinely breaks on one object and holds
conditionally on another. **This ruling composes it to `breaks`** for the reason given in
1.3: the plan's question was about the form the contract depends on. The reader was right to
refuse to collapse it and the Coordinator is the right place for the collapse to happen,
which is what "the Coordinator composes" means.

### (iv) — `TASK-20260916-64a93b` does not claim joint `J-4`. **BOTH: checker limitation as to schema, and a genuine procedure deviation as to the plan.**

- **Schema.** A sub-joint decomposition legitimately discharges a parent joint when the
  sub-joints jointly answer the parent's question and every one is owned by the parent's
  assigned owner. All three conditions hold. `J-4` is **not** unowned.
- **Procedure.** The plan declared `J-4` as **one** joint. The **task card** decomposed it
  into `J-4a/b/c` (see its `handoff.questions`). **That divergence is the dispatcher's, not
  the reader's**, it happened after the plan was committed, and it was not recorded anywhere
  until this ruling. It is benign and improving — the decomposition is better than the
  plan's single question and produced the J-4a records finding that the plan would not have
  asked for. It is still a departure from a committed plan, and AGENTS.md is explicit that
  departures go in `procedure_deviations` *even when they are right*: "acting before a report
  returns, reassigning a joint mid-round, or dropping a control may all be right in the
  moment; none of them is self-documenting." **Recorded as PD-1.**

### (v) — Joint `J-5` is assigned to both readers. **GENUINE PROCEDURE DEVIATION.**

The review-architecture rule is one owner per joint. The plan wrote `owner: both readers,
each on its own joints` — which the checker then parsed as a literal owner id, producing the
confusing "…which filed no `review_attestation`". The parse is an artifact; the underlying
problem is real.

**And the plan's substantive choice was right.** A proves-too-much control is a control on an
*argument*; the two readers had different arguments and were mutually blind, so no single
owner could have run the control on both. The rule as literally written cannot express that.
**What the plan should have done is declare two joints, `J-5a` (Nagao) and `J-5b` (Semaev),
each with exactly one owner.** It did not, and the cost is visible: the round produced two
opposite J-5 outcomes under one identifier, and only a composition can tell them apart.
**Recorded as PD-2.** The outcome remains the split verdict of 1.5; the deviation is in how
the joint was declared, not in how it was run.

### (vi) — `proves_too_much.objects` is empty in the plan. **GENUINE PROCEDURE DEVIATION, and the most serious of the four.**

AGENTS.md requires the control to name "objects for which the conclusion is KNOWN FALSE and
the signature a correct argument must show on them." The plan named one object — the
program's own exhaustive counterexample, for J-3 — **in J-5's `attack_plan` prose**, and for
J-4 it said only "a parameter regime where the conclusion is known or believed false", which
names no object at all. The structured field the contract and the checker read is **empty**.

**The consequence was real and is visible in the round.** The Semaev reader had to find its
own known-false object, and found an excellent one — §4.5.1's `k > ⌈n/m⌉` remark, where the
paper reports its own conclusion failing. That is skill, and it is not compliance. A control
whose object is chosen by the reviewer being controlled is a weaker control than one whose
object was fixed before the reviewer ran, and the plan is where it should have been fixed.

**This is a defect in the predecessor Coordinator's plan**, not in either reader's work, and
I record it as such rather than letting the round's good outcome absorb it. **Recorded as
PD-3.**

### 8.7 The gate, reported honestly

> **The completion gate "the independence checker raises no problem against the round" is
> NOT SATISFIED. This ruling records it as not-yet-satisfied and does not declare otherwise.**

Four of the six problems — (i), (ii), (iii), (iv-schema) — would be closed by a checker fix
that strictly **adds** expressiveness and weakens no check. Two — (v) and (vi) — would
**remain**, and they would remain permanently, because they are properties of a plan that is
committed and immutable. That is the right end state: a standing, machine-visible record
that this round's plan double-owned a joint and left a required control field unfilled. A
green check would erase exactly the information worth keeping.

**Recommended checker change, specified but NOT applied** (it is outside this task's write
scope and the card forbids resolving the gate this way):

1. **Accept a mapping verdict** whose `verdict` key holds a token.
   *Test:* `{verdict: holds, answer: "..."}` passes; `{answer: "..."}` with no `verdict` key
   still **fails**; a mapping whose `verdict` value is itself a mapping still **fails**.
2. **Accept a compound token** whose leading word is `breaks|holds|inconclusive`, **only**
   when the report also carries a `verdict_scope` (or per-object verdicts).
   *Test:* `breaks_as_printed_holds_conditionally_on_usage_form` with a `verdict_scope`
   passes; the same token without one still **fails**; `unclear_but_probably_fine` still
   **fails** whatever else is present.
3. **Accept sub-joints as discharging a parent** when every claimed sub-joint id is the
   parent id plus a single suffix character **and** the claimant is the parent's assigned
   owner. *Test:* `J-4a/b/c` by the owner of `J-4` discharges `J-4`; `J-9a` does **not**
   discharge `J-4`; `J-4a` claimed by a task that is not `J-4`'s owner does **not** discharge
   it.
4. **Accept a multi-owner joint only when it declares per-owner objects** — e.g.
   `per_owner_object: true` — and every named owner attests separately with its own control
   object. *Test:* a joint with two owners and `per_owner_object: true`, with both
   attestations present, passes; the same joint without the declaration still **fails**; with
   the declaration but only one attestation, still **fails**.
5. **Leave `proves_too_much.objects` strictly as it is.** It is not a schema gap. An empty
   required control field is the thing the check exists to find, and it found it.
6. Fix the owner-parsing so a prose `owner` string is reported as *"owner field is prose, not
   an owner id"* rather than as a missing attestation. Cosmetic, but the current message sent
   this adjudication looking for a third reader that never existed.

### 8.8 `procedure_deviations` — for `DEC-20260916-87fc5c`

```yaml
procedure_deviations:
  - id: PD-1
    what: >-
      The plan declared J-4 as ONE joint; TASK-20260916-64a93b's task card decomposed it
      into J-4a/J-4b/J-4c and the reader answered the sub-joints. The decomposition is the
      DISPATCHER'S, made after the plan was committed, and was recorded nowhere until this
      ruling.
    who: the dispatching Coordinator session, not the reader.
    benign: >-
      YES, and improving. The decomposition is better than the plan's single question and
      produced the J-4a finding -- that no record of this campaign cites 2015/310 at all --
      which the parent question would not have asked for.
    recorded_because: >-
      A departure from a committed plan is recorded even when it is right. A protocol that
      is silently deviated from is worth less than one never declared, because it still
      reads as rigorous.
    effect_on_the_round: >-
      None adverse. J-4 is composed as owned and discharged; it is not unowned.
  - id: PD-2
    what: >-
      Joint J-5 was assigned to BOTH readers ("owner: both readers, each on its own
      joints"), against the one-owner-per-joint rule of AGENTS.md "Review architecture".
    who: the plan, REVIEW-SEMBIN-20260916-e0a0c1, written before either reader ran.
    why_the_substance_was_right: >-
      A proves-too-much control is a control on an ARGUMENT. The two readers had different
      arguments and were mutually blind, so one owner could not have run it on both.
    what_should_have_been_done: >-
      Declared TWO joints, J-5a (Nagao) and J-5b (Semaev), each with exactly one owner.
    effect_on_the_round: >-
      The round produced two OPPOSITE J-5 outcomes under one identifier -- passes on the
      Nagao half, FAILS on the Semaev half. Only a composition can tell them apart, which
      is a cost the declaration should not have imposed.
    not_repairable: >-
      The plan is committed and immutable. tools/check_review_independence.py will report
      this against this round permanently, and that is the correct outcome.
  - id: PD-3
    what: >-
      `proves_too_much.objects` is EMPTY in the plan. The J-3 object was named in J-5's
      attack_plan PROSE; the J-4 object was not named at all ("a parameter regime where the
      conclusion is known or believed false" names no object).
    who: the plan, REVIEW-SEMBIN-20260916-e0a0c1.
    severity: the most serious of the three. A required control field was left unfilled.
    consequence_observed: >-
      TASK-20260916-64a93b had to FIND its own known-false object and found an excellent one
      (Semaev's own k > ceil(n/m) remark at :1054-1058). That is skill, not compliance. A
      control whose object is chosen by the reviewer being controlled is weaker than one
      fixed before the reviewer ran.
    effect_on_the_round: >-
      The J-5 findings stand -- both objects are genuinely known-false objects and both
      controls were genuinely run. What is weakened is the GUARANTEE, not the result.
    successor_obligation: >-
      Any successor plan under this goal fills proves_too_much.objects in the structured
      field before dispatch. Recorded as next action NA-5.
  - id: PD-4
    what: >-
      TASK-20260916-9da6e0 disclosed three contacts that qualify its blindness: the J-1
      answer leaked from an in-scope program-authored errata it was DIRECTED to read; it
      read CORR-20260916-96f47d only AFTER constructing its own counterexample; and it ran
      `ls -la` on the sibling's directory at the end of its task, seeing five file names,
      sizes and mtimes without opening any file.
    who: the reader, disclosed by the reader, in full, unprompted.
    ruling_on_each:
      errata_leak: >-
        COSTS J-1 ITS STATUS AS A TEST. The bare identification is corroboration. J-2, J-3
        and J-5 are untouched -- the errata says nothing about whether Lemma 2 is proved or
        whether it delivers Lemma 4. And a second, UNDISCLOSED leak is larger: the answer
        was already in the goal head, citing DEC-20260913-8d19e5. Ruling in section 1.1.
      correction_read_after: >-
        COSTS NOTHING, and the ordering is what makes it cost nothing. The reader's witness
        is a DIFFERENT object from the recorded one and is stronger (it kills the inside
        form under the equality reading, which the recorded one does not). Where the two
        agree, that is ONE independent confirmation and not two, exactly as the reader
        says.
      sibling_ls: >-
        COSTS NOTHING. File names, sizes and mtimes carry no verdict, the names are the
        card's prescribed deliverable set and are predictable without looking, and no file
        was opened. The disclosure is worth more than the contact cost: an attestation that
        is merely almost true is the failure this document exists to prevent, and this
        reader corrected an earlier draft of its own attestation rather than leave a
        sentence standing that contact had made untrue.
    is_this_a_blindness_breach: >-
      NO. No blind_from path was opened by either reader. These are qualifications on what
      the blind was WORTH, disclosed by the agent that incurred them, which is the behaviour
      the contract wants.
  - id: PD-5
    what: >-
      TASK-20260916-64a93b disclosed a boundary case: two files inside its granted read
      scope (EXP-SEMBIN-4fa22c/specification.yaml and H-SEMBIN-a7e721.yaml) QUOTE prior
      campaign findings, including CORR-20260916-96f47d's quantifier correction. It read
      those quotations because they are inside files it was told to read, and opened no
      referenced file.
    ruling: >-
      COSTS NOTHING MATERIAL, and the disclosure is correct. No finding in that report
      depends on the quotations: J-4b's degree results and the J-5 control come from the
      frozen Semaev text and from its own recheck.py. But it is a real defect in how the
      read scope was drawn -- a scope that admits a file which quotes the answers is not the
      blind it claims to be -- and a successor plan should either exclude such files or
      declare what they leak. Recorded as part of NA-5.
  - id: PD-6
    what: >-
      The completion gate requires the independence checker to raise no problem. It raises
      six. This ruling adjudicates each and reports the gate NOT SATISFIED.
    ruling: >-
      The gate is not satisfied and is not declared satisfied. Four problems are checker
      limitations with a specified fix and its tests (section 8.7); two are the genuine
      deviations PD-2 and PD-3 and will stand against this round permanently, because the
      plan is immutable. The checker was NOT loosened to reach the gate.
```

---

## 9. Decision, and what follows

```yaml
coordinator_decision:
  id: DEC-20260916-87fc5c
  recorded_at: '2026-09-21'
  recorded_by: coordinator
  goal_id: GOAL-SEMBIN-fcb7a2
  batch_id: BATCH-e0a0c1
  round_id: REVIEW-SEMBIN-20260916-e0a0c1
  composed_at_task: TASK-20260916-a8e5b5
  archived_by: TASK-20260916-d4fb62
  context: >-
    Two independent, mutually blind review-adversarial source reads on disjoint joints
    returned. BOTH BROKE THEIR JOINTS. The Nagao reader finds that 2013/549's Lemma 2 --
    correctly identified as the statement 2015/984 cites as its "Lemma 3 ([11])" -- is
    proved, but does NOT deliver 2015/984's Lemma 4, which is FALSE as printed, with a
    counterexample. It additionally finds the INSIDE/OUTSIDE distinction this campaign
    drew on the FAKE side to be INERT, so Lemma 4 as printed and the form this program had
    already falsified are the same statement. The Semaev reader finds a three-component
    gap between statement and argument in 2015/310 and reports its proves-too-much control
    FAILING: the paper supplies its own known-false object and the argument runs there
    unchanged. A Coordinator cross-check by an independent implementation neither reader
    read confirms inertness and reproduces the reader's witness.
  decision: synthesize
  target_ids:
    - GOAL-SEMBIN-fcb7a2
    - BATCH-e0a0c1
    - REVIEW-SEMBIN-20260916-e0a0c1
    - EXP-SEMBIN-4fa22c
    - EV-SEMBIN-1ca3c8
  rationale:
    - >-
      P-4 REFUTED, three times over: the upstream lemma does not deliver Lemma 4; the
      distinction P-4 drew does not exist; and the statement P-4 says is licensed is false.
      This is the prior the predecessor Coordinator recorded as the one it would rather
      lose, and it is recorded here at least as prominently as the confirmations.
    - >-
      P-2 and P-5 also REFUTED; P-1 and P-3 confirmed, with P-1 marked NOT A LIVE
      PREDICTION because its answer was in this program's own committed goal head; P-6
      confirmed in its consequent and refuted in its mechanism. Three of six refuted. Full
      scoring at the ruling's section 2 and in scored-priors.json.
    - >-
      There is no placement of the field equations under which a universally quantified
      d_F <= d'_F survives at the contract's declared equality convention. The campaign's
      recorded residual is dead in both halves, and the bookkeeping error is named rather
      than absorbed (ruling section 4).
    - >-
      The escalation condition fired. The CLAIM that a published subexponential ECDLP
      bound rests on an unsupported lemma needs review-breakthrough at max under core rule
      12; that tier is undegradable and unservable here. The finding is recorded at full
      strength and narrowest scope; the claim is not promoted; the goal stays ACTIVE with
      IMP-SEMBIN-FCB7A2-LEMMA4-TIER recorded against the CLAIM.
    - >-
      No status transition rests on a read of an external source. H-SEMBIN-a7e721 and
      EXP-SEMBIN-4fa22c are unmoved; no completion criterion is discharged; criterion 4
      remains the only one met, by DEC-20260913-8d19e5.
  evidence_refs:
    - EV-SEMBIN-1ca3c8
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/report.md
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/attestation.yaml
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/statement-map.json
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/recheck.out
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-nagao-2013-549/reextract.md
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-semaev-2015-310/report.md
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-semaev-2015-310/attestation.yaml
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-semaev-2015-310/statement-map.json
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-semaev-2015-310/recheck.out
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/read-semaev-2015-310/reextract.md
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/archives/TASK-20260916-92128f/snapshot-receipt.json
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/ruling/composition.md
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/ruling/scored-priors.json
    - tools/lemma4_inside_form.py
    - tools/test_lemma4_inside_form.py
    - CORR-20260916-96f47d
    - CORR-20260921-942a62
  evidence_binding: >-
    All twelve reader artifacts are hash-bound by TASK-20260916-92128f at commit
    4b7edadfbd42489f1a120157c1d29558fa992cce under binding_mode content_first, which
    verifies the declared hashes against HEAD and so catches an in-place edit to a filed
    report. This decision cites bytes a later reader can verify, not a Coordinator's
    recollection of them.
  limitations:
    - >-
      THE CLAIM IS NOT PROMOTED. Nothing here asserts as a program conclusion that Nagao's
      Proposition 5, or the bound of his Theorem 1, is unsupported. That step needs
      review-breakthrough at max and is blocked.
    - >-
      Every witness is at p = 2 with N <= 3. Nothing is established at p >= 3 or at the
      variable counts of any descended system.
    - >-
      The refutation is void under the literal ">=" reading printed in 2015/984, under
      which the inequality holds and is empty. The equality reading is a DECLARED
      interpretation of an ambiguous source, supported by three independent routes and
      settled by none.
    - >-
      Whether the EQS4 instances EXP-SEMBIN-4fa22c will measure are among the violating
      instances is NOT established and is not assumed.
    - >-
      The Semaev J-5 control establishes that the JUSTIFICATION for Assumption 1 does not
      distinguish the regime where it is believed from the regime the author reports it
      false. Assumption 1 itself is correctly stated and is NOT refuted. Nothing in this
      round measures d_F4 at any k.
    - >-
      Both reads are of frozen external texts by agents at review-adversarial with
      model_verified: false. The mathematics is independently checkable; the textual
      findings rest on two careful readings and are cited as such.
    - >-
      J-1's confirmation is corroboration, not a test: its answer was available to the
      reader in an in-scope errata AND was already recorded in this goal's own head.
    - >-
      The independence gate is NOT satisfied. Six problems stand, adjudicated at the
      ruling's section 8; two are genuine deviations of the round from its plan and will
      stand permanently.
  knowledge_promotion:
    warranted: true
    entry_id: KN-FIND-936151
    id_minted_by: >-
      python3 tools/allocate_id.py --check KN-FIND-936151 -- well-formed and free across
      the union (25700 identifier-bearing paths scanned, 0 occurrences). allocate_id.py
      --next has no `kn-find` type, so the token was drawn at random with secrets.token_hex
      and confirmed with --check, which is the same discipline and the same guarantee.
    title: >-
      The fake first fall degree does not bound the true one: Nagao 2015/984's Lemma 4 is
      false as a universal statement over F_2, in every placement of the field equations
    why_warranted_despite_the_decision_not_being_support_or_reject_scoped: >-
      The coordinator contract triggers a KN-FIND on `support` or `reject_scoped` backed by
      replicated/strong evidence. This decision is `synthesize`, so the trigger does not
      fire -- and the promotion is warranted anyway, for a reason the trigger does not
      cover: the finding is REUSABLE OUTSIDE THIS CAMPAIGN and is the kind of thing a later
      agent would otherwise re-derive or, worse, not know to check. Every campaign in this
      program that consumes a first-fall-degree bound consumes d_F <= d'_F somewhere, and
      GOAL-DREG-001, GOAL-RELN-001, GOAL-ICEX-001 and GOAL-SEMBIN-5078bc all touch these
      quantities. The honest record is that the rule did not require this and the
      Coordinator judged it warranted on the merits; that judgement is recorded here so it
      can be disagreed with.
    must_carry:
      - The two witnesses in full, so the entry is self-contained and checkable.
      - The inertness result, which is why the naming in older records is unsafe to reuse.
      - >-
        The ">=" scope note. An entry that omits the reading under which its target is TRUE
        would be a worse pointer than none.
      - >-
        The U-4 bookkeeping route, because the entry's forward value is that the inference
        is RECOVERABLE per instance, not that a lemma is dead.
      - >-
        An explicit statement that it asserts nothing about Proposition 5, about
        Assumption 1, or about any curve.
    committed_with: >-
      The same ledger archive as this decision, TASK-20260916-d4fb62, together with a
      regenerated knowledge/INDEX.md. knowledge/INDEX.md is gitignored and rebuilt on
      demand, so "regenerated" means the build is run and shown to succeed, not that the
      file is staged.
  next_actions:
    - id: NA-1
      rank: 1
      action: >-
        Write AMD-EXP-SEMBIN-4fa22c-20260921-lemma4, an ADDITIVE amendment at
        experiments/EXP-SEMBIN-4fa22c/amendments/, in the form of the existing
        AMD-EXP-SEMBIN-4fa22c-20260916-collision. It must: (a) record that S-5's phrase
        "Lemma 4's inside form, which is UNPROVEN" is now, at the contract's own declared
        equality convention, REFUTED as a universal statement, citing EV-SEMBIN-1ca3c8 --
        WITHOUT editing the frozen contract, whose text is immutable and historically
        accurate for 2026-09-16; (b) ADD a reporting requirement discharging U-4 per
        instance: for every reported d'_F, the run records the UNREDUCED total degree of
        each product g_i f_i of the realising fake witness, and states whether
        max_i deg(g_i f_i) <= d'_F holds at that instance. Only where it holds may the
        report state the d_F <= d'_F consequence, and it then states it as discharged by
        that bookkeeping rather than by Lemma 4; (c) ADD the missing 2015/310 citation
        anchor -- section, line range and provenance -- that J-4a found absent from every
        record of this campaign, and record the LINK 1 characterisation qualification
        (Semaev states the result under the TRUE definition and calls it "proved", while
        his argument computes the fake bound); (d) record that control C-6 is now known to
        be STRUCTURALLY UNINFORMATIVE for the quantity this contract measures: C-6 compares
        the field equations placed inside the generating set against Boolean reduction
        alone, and inertness makes those identical for d'_F, so C-6 can only ever report
        agreement. The control is not removed -- removing it would be a rewrite -- and its
        verdict is to be reported as structurally forced rather than as a passed check.
      why_first: >-
        It is the only action that changes what the campaign's next run must do, it costs
        no compute, and the contract currently instructs an executor to lean on a statement
        that is false.
      authority: >-
        An additive amendment under a new id, per AGENTS.md core rule 4 and the contract's
        own what_changed_at_approval. It removes, weakens and reinterprets nothing.
    - id: NA-2
      rank: 2
      action: >-
        Fix the frozen-extraction hazard in inputs/NAGAO-2013-549. TASK-20260916-9da6e0
        reports that paper_fulltext.md lines 721-734 destroy the GRADED MONOMIAL ORDER
        hypothesis that Lemma 2's proof depends on, rendering it as a per-variable
        comparison that says nothing, so a reader confined to the frozen text concludes the
        proof rests on an empty condition. The clean pymupdf companion
        (paper_fulltext.pymupdf.txt, sha256 087d38...) already exists beside it. Extend
        errata-extraction-20260921.md to name this specific passage and the correct reading.
        The frozen markdown and its sha256 sidecar are NOT edited.
      why: >-
        It is a mechanical fact about a frozen file, not a judgement, and it affects every
        future reader of that input package -- including any successor read dispatched
        under NA-4.
    - id: NA-3
      rank: 3
      action: >-
        Record, as a correction or in the closing checkpoint, the NAMING DEFECT of ruling
        section 4.1: four committed documents (the read plan's P-4, this batch's
        opening-report.md, its checkpoint, and TASK-20260916-a8e5b5's own dispatch card)
        locate the inside/outside distinction on the FAKE side, where it is inert. None is
        edited; all are immutable. The correction records that CORR-20260916-96f47d drew
        the distinction on the TRUE side and drew it CORRECTLY, so the drift is in the
        documents that restated it, and that every future record in this campaign states
        which SIDE a placement is on.
      why: >-
        The defect propagated from the read plan into a dispatch card five days later. A
        naming convention nobody corrected is a naming convention that will propagate again.
    - id: NA-4
      rank: 4
      action: >-
        Rank, but do NOT yet dispatch, a successor read on the one question this round
        opened and could not close: does Nagao's own application chain actually discharge
        U-4 at the instances Proposition 5 covers? TASK-20260916-9da6e0 reports that
        2015/984's Lemma 6 proof and 2013/549's own estimate both discharge it by explicit
        bookkeeping (deg g_i <= 1 on already-reduced generators), but neither reader was
        asked whether Proposition 5's EQS4 instances inherit that bookkeeping -- EQS4 is
        reached through Definition 8 and footnote 6's omitted proof, which is exactly where
        the chain is thinnest. A `yes` would restore the campaign's inference at those
        instances without needing Lemma 4 at all, which is the most valuable single answer
        now available.
      why_not_dispatched_here: >-
        This task writes two files and dispatches nothing. It is ranked so the next
        coordinating session has it, and it is ranked BELOW NA-1 because the amendment
        changes what an executor does and this read changes what a claim can say.
    - id: NA-5
      rank: 5
      action: >-
        Carry PD-2, PD-3 and PD-5 into the successor review plan as requirements: one owner
        per joint with the proves-too-much control split per argument (J-5a/J-5b); every
        known-false object named in the STRUCTURED proves_too_much.objects field before
        dispatch, with the signature a correct argument must show on it; and a read scope
        that either excludes files quoting the round's own answers or declares what they
        leak.
      why: >-
        All three are cheap before a round and unrepairable after it. This round paid for
        each of them.
    - id: NA-6
      rank: 6
      action: >-
        Publish a bus message to `coordinator` and the SEMBIN lanes pointing at
        DEC-20260916-87fc5c, EV-SEMBIN-1ca3c8 and KN-FIND-936151, so the sessions working
        GOAL-SEMBIN-5078bc, GOAL-DREG-001, GOAL-RELN-001 and GOAL-ICEX-001 learn that
        d_F <= d'_F may no longer be cited as a theorem. A POINTER, never a permission and
        never evidence: cite the ids and let each session read the records.
      why: >-
        Four other goals consume first-fall-degree quantities and none of them can see this
        lane. The bus is a feed, not a notification, so this is filed for whoever reads it
        next rather than delivered.
  what_this_decision_does_not_do:
    - Change H-SEMBIN-a7e721's status. It predicts a measurable separation; this round measured none.
    - Change EXP-SEMBIN-4fa22c's status. It remains `approved`, unrun, and now amended additively.
    - Edit the frozen contract, the read plan, the opening report, the checkpoint, or either reader's package. All are immutable.
    - Discharge any completion criterion. Criterion 4 remains the only one met, by DEC-20260913-8d19e5.
    - Promote the claim. IMP-SEMBIN-FCB7A2-LEMMA4-TIER stands until review-breakthrough at max can be served.
    - Assert anything about Proposition 5, Assumption 1, any value of d_F4, any elliptic curve, or the security of any deployed parameter set.
    - Close BATCH-e0a0c1's lane as the campaign's current one. current_batch_id still names BATCH-cbb416 and that checkpoint keeps the operative next_action.
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-opus-5
    model_provenance: self-reported by the runtime
    model_verified: false
    model_verified_note: >-
      `python3 -m orchestration.adapter doctor --probe` has no credentialed backend in this
      checkout, so the resolved identifier is unverified configuration and not an
      established fact. Recorded as NOT OBTAINED rather than as met.
    fallback_allowed: true
    fallback_used: true
    fallback_reason: >-
      No adapter backend is credentialed in this checkout, so the runtime-native binding
      permitted by core rule 16 is the only route. Declared up front in the task card, not
      discovered afterwards.
    degraded_allowed: false
    degraded_requirements: [model_verified]
    independent_session_required: false
    bedrock_prohibition_observed: >-
      No provider, backend, endpoint, or model identifier containing `bedrock` was selected
      or contacted.
    reasoning_effort: high
    reasoning_effort_source: policy default for coordinator-orchestration-code
```

---

## 10. Completion gate, reported against itself

| gate item | status |
|---|---|
| every prior P-1..P-6 is scored | **MET.** Section 2 and `scored-priors.json`; none untested; three refuted, recorded at least as prominently as the confirmations; P-4 called out first. |
| every joint J-1..J-5 named with a verdict or an explicit "unowned" | **MET.** Section 1. No joint unowned. J-4 discharged by its card sub-joints; J-5 composed as a split verdict. |
| the checker's six problems each adjudicated, gate reported honestly | **ADJUDICATED; GATE NOT SATISFIED.** Section 8. Four checker limitations, two genuine deviations, checker not loosened, fix specified with tests but not applied. |
| no status transition rests on a read of an external source alone | **MET.** No hypothesis, experiment or goal criterion moved. `EV-SEMBIN-1ca3c8` rests on machine-checkable arithmetic reproduced by two independent implementations, not on a read; the textual findings are cited by the decision and carry no transition. |
| nothing written outside the write scope | **MET.** Two files under `.../BATCH-e0a0c1/ruling/`. No `git add`, `git commit` or `git push` was run. Verified with `git status --porcelain`. |

**Zero runs.** The only executions were re-verifications of in-scope artifacts —
`python3 tools/test_lemma4_inside_form.py` (15 tests, OK), `python3 tools/lemma4_inside_form.py`,
`python3 tools/check_review_independence.py`, `python3 tools/allocate_id.py --check`, and a
`grep` over the frozen `paper_fulltext.pymupdf.txt` for the P-2 numbering check. Each is exact
finite arithmetic or a read of a committed file; none samples, times, or measures a property
of any research object.
