# TASK-20260730-039 — Falsification and scope review of the CTRL-RT034-A mutation test

**Cited by path and task ID only.** No `RT-*` identifier is minted (INT-BATCH014-N;
`RT-20260729-036` is a dangling reference that must never be issued).

Reviewed snapshot: commit `1454d2bebe84d14b1c84a02ebe46598f064e497f`, the seven
mutation artifacts under
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/`.
Independent session. Model independence unavailable and not claimed
(INT-BATCH016-E); the resolved model is `claude-opus-5` with `fallback_used: true`.

No commit made. Nothing written outside this review directory. `harness/`
unmodified and unpatched. No ledger record touched. No research status changed.
No approval of EXP-STR-004 recommended, and BATCH-016 is not enlarged.

---

## 1. What the card got right, said first

I am obliged to state this before the objections, because an objection list read
without it will be mistaken for a verdict on the executor's work, which it is not.

- **The verbatim constraint held, and I checked it rather than believing it.**
  `verify_verbatim_copy()` byte-compares the copied region against
  `probe_driver.py` lines 416–441; re-executed in my own session it returns
  `byte_identical=True` with copied and source SHA-256 both
  `89ecfa9ac1a6705c83deacb0ee03e75818b93575d3ca97bac28ddf301c1fc3b0`. I also
  confirmed by `git diff e3cf9fdd HEAD -- .../probe_driver.py` (empty) that the
  cited source has not drifted, so comparing against the on-disk file is
  comparing against the committed text. This was the load-bearing constraint and
  it was honoured.
- **No interpretation was smuggled in.** `mutation_manifest.json` carries an
  explicit `no_interpretation_note`; `case_0_status` and
  `case_1_pre_stated_status` each disclaim result status on their face. A grep of
  all seven artifacts for *informative*, *rehabilit*, *vindicat*, *working
  control*, *confirms*, *validates*, *is phi-invariant* and *general* returns
  zero hits.
- **The snapshot commit changed exactly the seven declared producer paths**, with
  the receipt one commit later as INT-BATCH007-T predicts. The four-batch pattern
  of committing review artifacts one commit early did **not** recur, and no
  `EV-STR-006` or `DEC-20260730-032` draft exists in the tree.
- **I re-derived the instance and the case-2 rule independently.** p=2293, n=733,
  ζ₃=1303 with ζ₃³≡1, |F|=192 all distinct, F[0..5]=[1963,1094,1529,310,362,1621],
  forbidden orbit [1963,1094,1529], and x=1 is on-curve, not in F, not in that
  orbit — so `chosen_x=1, candidates_scanned=1` is correct under the stated rule.

The executor card is clean. My objections are to **the inference**, not to the
execution.

---

## 2. The strongest objection: "catches layout breaks" is false, and I ran the
## counterexamples

The natural successor reading is *"CTRL-4 catches layout breaks, is blind only to
ζ₃ validity, therefore rewrite rather than retire."* The first clause is false as
stated.

The checker refers to exactly one thing: the within-block identity
`F[3j+k] == ζ₃^k · F[3j] (mod p)`. It never touches the curve, never checks
distinctness, never checks orbit disjointness, never checks that the list came
from this instance, and never checks block-level ordering. **Anything that
preserves within-block alignment passes, however catastrophic.**

I loaded the *committed, byte-verbatim* checker out of `mutation_driver.py` by
file path (its `main()` is under an `__main__` guard, so import runs module level
only), fed it mutated copies of the committed builder's output, and ran it. The
diagnostic scripts live outside the repository, in the session scratchpad, and
are named in the YAML. **This is a red-team diagnostic. It is not a BATCH-016
measurement, not evidence, not a run, and mints no identifier.**

| # | Mutation (B=192 unless noted) | cond (i) | cond (ii) | joint |
|---|---|---|---|---|
| D-0 | none (baseline) | PASS | PASS | PASS |
| D-1 | block 0 → orbit of y=4, **off-curve** | PASS | PASS | **PASS — missed** |
| D-2 | **all 64 blocks fabricated**; only 78/192 entries on E | PASS | PASS | **PASS — missed** |
| D-3 | block 1 := block 0 (189/192 distinct) | PASS | PASS | **PASS — missed** |
| D-4 | blocks 0,1 swapped **whole** (same 6 indices as case 3) | PASS | PASS | **PASS — missed** |
| D-5 | block 0 := [0,0,0] | PASS | PASS | **PASS — missed** |
| D-6 | k=1↔k=2 swapped in **every** block | PASS | FAIL (128) | FAIL — caught |
| D-7 | F truncated to 189 | **FAIL** | PASS | FAIL — caught |
| D-8 | truncate to 189, refill one fresh valid orbit | PASS | PASS | **PASS — missed** |
| D-9 | G[1] := ζ₃²·F[0] (in-orbit, wrong power) | PASS | FAIL (1) | FAIL — caught |
| D-10b | **B=193**, F[192] := 1 (unrelated on-curve x) | PASS | PASS | **PASS — missed** |
| D-10c | **B=193**, F[192] := 0 (not a point) | PASS | PASS | **PASS — missed** |
| D-11 | foreign-instance FB | — | — | **not run**, reported as not run (seed 2 gives p=2953, a different prime; I did not weaken the rule to force a number) |

Three observations carry the argument.

**D-2 is the strongest single fact in this review.** CTRL-4 reports PASS on a
factor base in which 114 of 192 entries are not x-coordinates of any point of the
curve. A "control" on a factor base that passes a 59 %-non-point list is not
controlling the factor base; it is controlling a multiplicative pattern among
integers mod p.

**D-4 is decisive against the generalisation.** It permutes exactly the six
elements that case (3) permutes, and it PASSES. Two mutations of the same
descriptive class ("reordering the first two blocks") with opposite outcomes means
the descriptive class is the wrong unit of generalisation. Note carefully: D-4 is
a *correct* non-detection — a whole-block swap does not break the block-circulant
φ-shift — so it is a demarcation, not a defect. That is precisely why it is
useful: it locates the boundary, which the batch's mutation set never does.

**D-10 shows the hole is inside the frozen contract, not outside it.** B=193 is a
contract cell that the BATCH-015 probe actually ran. There, index 192 lies in no
complete block and is checked by nothing. The checker's own
`tail_indices_not_in_a_complete_block` field records the hole; nothing acts on it.
(Labelled clearly: B=193 is outside BATCH-016's B=192 scope and this is offered as
a diagnostic, not a batch measurement.)

---

## 3. The strongest case that the mutations are too easy

Case (2)'s replacement rule **explicitly excludes every value in
{ζ₃ᵗ·F[0]}**. Given that exclusion, `G[1] ≠ ζ₃·G[0]` is a *theorem about the
constructed input*, and a condition-(ii) FAIL follows by inspection of six lines
of Python. Case (3) is the same up to a 1/p accident: after interleaving,
H[1]=F[3], and H[1]==ζ₃·H[0] would require the independently seeded F[3] to
coincide with ζ₃·F[0] — probability ≈1/2293 per position, four positions.

Both outcomes were **derivable at queue-authoring time from the source the queue
author had in hand.** A mutation that directly violates the exact identity being
checked is close to a tautology in the opposite direction, and a FAIL on it
carries little more information than the PASS it replaces.

**But it does carry *some*, and I will not argue that away.** A checker whose
inner loop never executed — an empty `range(len(F)//3)`, an early return, a
`failing` list rebuilt and discarded, an inverted PASS/FAIL polarity — would have
passed case (1) for a second, duller reason, and BATCH-015's finding would have
had an alternative explanation. That alternative is now excluded on this instance
at this B. **One genuine bit, and it was worth the milliseconds.** It is one bit,
and it does not scale into "is a control".

Dissent against my own objection, recorded: a tautological mutation is the
*correct first* mutation for an assertion that has never been mutated at all —
you check that the needle moves before asking what it is sensitive to. The queue's
choice was reasonable as a first exercise. My objection is to the inference, not
to the choice.

---

## 4. Case 0 as a null object

Case 0 excludes an *always-FAIL* harness — a driver that corrupted its input on
every path, mis-bound ζ₃ everywhere, or inverted polarity. It does **not** exclude
the mode that actually threatens this batch.

A broken mutation harness that still passes case 0 looks like this: suppose
`build_case_input()` silently returned the mutated list for cases 2 and 3 and the
**unmutated** list for case 1. Case 0 passes, cases 2 and 3 fail, case 1 passes —
**an outcome pattern byte-identical to the observed one**, and case 0 could not
have told anyone.

Is that mode present? **No, and I checked rather than assuming.** I read
`build_case_input()` and independently re-derived case 1: building F with z=5 and
checking with z=5 does yield JOINT=PASS, and the reason is visible in
`harness/endomorphism_la.py` lines 96–113 — the builder constructs orbits under
whatever z it is handed, so the checker re-verifies the constructor's own
arithmetic. The mode is absent. The point stands that the offered null object
could not have excluded it.

**The adequate null object for a mutation harness is a positive control on the
mutation channel**: one mutation known-detectable by an argument independent of
the checker under test, and one known-*un*detectable that must PASS, both
pre-stated. My D-6 (must FAIL, 128 failing pairs) and D-4 (must PASS, harmless)
are that pair and cost microseconds.

---

## 5. Verdict on condition (i)

**It is not dead code, and "dead, full stop" would be a false statement that must
not be written.** D-7 fired it on my first attempt: truncate F to 189 and
condition (i) reports FAIL while condition (ii) reports PASS. The comparison is
live and it discriminates.

The correct narrow verdict is that condition (i) is a length check which

1. **no reachable path of the as-committed builder can fail at B=192 on this
   instance** — `_build_phi_invariant_factor_base` fills `xs` until `len(xs) ≥ B`
   then returns `xs[:B]`, so the only failure mode is exhausting the `50B+1000`
   seed budget, against which BATCH-015 measured a 76× margin; and
2. **no mutation in this batch's set was constructed to violate** — all four
   mutated inputs preserve length by design, which is why (i) reported PASS five
   times out of five.

So the BATCH-015 finding stands unchanged and is **not** extended to "dead, full
stop". It is a constructor identity *in practice at these parameters*, retaining
power against length-changing corruption (D-7) and against supply exhaustion at
larger B or on a poorer instance. D-8 shows how trivially it is evaded: any
corruption that restores length walks straight past it.

And condition (i) *hides* the B=193 tail hole rather than catching it: `len(F)==193`
passes, while index 192 is checked by nothing (D-10b, D-10c).

---

## 6. Claim-ceiling audit — item by item

I audited N-1 through N-7, the case-0 and case-1 prohibitions, the no-RUN-id and
no-`experiments/`-write rules, and the "ledger does not validate" rule, against
all seven committed artifacts.

**No claim-ceiling breach is present in any committed BATCH-016 artifact at
`1454d2be`.** In particular, and because the card pre-registers these two as
prohibited, I checked them specifically:

- **Case (1) is not recorded as a new result.** `case_1_pre_stated_status` states
  verbatim that the outcome is pre-stated and that its reproduction is not
  recorded as a new result, a discovery, a replication or evidence about
  φ-invariance. `stdout.log` line 30 lists case 1 only as a *contributing case to
  the pre-registered consequence*, which is the mechanically correct use of it.
  **No breach.**
- **Case 0 is not recorded as a result.** `stdout.log` lines 13 and 21 both label
  it "instrument sanity check, not a result". **No breach.**

The breach risk is **downstream**. These are the exact sentences a successor is
likely to write that would breach the ceiling, and each should be flagged
BLOCKING if it appears:

1. *"CTRL-4 detects layout breaks and is blind only to ζ₃."* — **false as stated**;
   refuted by D-1, D-2, D-3, D-5, D-8, D-10b, D-10c.
2. *"The mutation test shows CTRL-4 is a working control."* — it shows the checker
   is not always-PASS on this instance at this B.
3. *"Cases 2 and 3 confirm the factor base is φ-invariant / that CTRL-4 is
   informative about φ-invariance."* — breaches N-3 and the queue's own
   `what_a_FAIL_on_cases_2_and_3_does_NOT_license`.
4. *"Case 1 reproduced the BATCH-015 finding" / "BATCH-016 replicated the bogus-ζ₃
   pass."* — breaches N-2. The permitted sentence is that case (1) was executed
   with a pre-stated outcome so that all cases passed through one checker in one
   package.
5. *"The baseline passed, confirming the factor base is well-formed."* — case 0 is
   an instrument gate, not evidence about F.
6. *"Condition (i) is dead."* — false; see D-7.
7. *"R-9 has been discharged" / "the independence limitation is now mitigated."* —
   the queue itself says an exercise is not a repair, and §7 shows the exercise
   did not reach the failure mode R-9 exists to cover.
8. Any sentence attaching a **number** — α, rank, cost, supply, crossover — to
   anything in BATCH-016. Nothing numeric was computed except PASS/FAIL booleans,
   four failing-pair identities, and one scan count.

---

## 7. Did R-9 actually work? Did determinisation bind?

**R-9: partially — at the execution layer only, and not at the layer that matters
most.**

R-9's premise is that mutation evidence is model-independent in a way that
cross-reading is not. That premise is **correct for execution**: arithmetic mod
2293 does not care which model wrote the driver, and the byte-verbatim constraint
plus the in-process determinism repeat make the execution layer genuinely
mechanical. I re-executed it and got the same answer, so the mechanical half is
real and I credit it.

But **a mutation test has two layers, and only one was mechanised.** The
*selection* of mutations is a modelling act. Here, one program — with the checker
source in front of it — chose the mutations, wrote the expectations, wrote the
prohibitions, and pre-wrote the reading the outcomes would license ("REWRITE, if
the checker detects layout breaks…"). The correlated blind spot R-9 exists to
defend against survived intact at the selection layer. The proof that it survived
is that a single adversarial session found **eight missed mutations in about ten
minutes**, one of which passes a 59 %-non-point factor base.

**R-9 is a real mitigation that was applied to the wrong half of the problem.**
What would make it bind is a *mutation-completeness rule* (CTRL-RT039-A): one
mutation per property the control's own text claims to protect; at least one
pre-stated-PASS row so the boundary is recorded rather than assumed; and at least
one row authored by a session that did not author the queue or the assertion. The
third is available on this harness **today, at zero model diversity** — it is
exactly what this card just did — and it is the cheapest of the three.

**Determinisation: yes against post-hoc selection, no against pre-hoc selection.**
I reproduced `chosen_x=1`, `candidates_scanned=1`, the forbidden orbit
[1094,1529,1963] and the fixed permutation *from the queue text alone* and got
identical values, so no outcome could have been obtained by choosing an input
after seeing a result. That protection is real and it held. It is orthogonal to
§3: fixing an input in advance does not make its outcome informative if the
outcome was derivable from the checker source in advance, and the same program
held both. **Determinisation converts "could have been fished" into "was fixed in
advance"; it does not convert "deducible" into "measured".**

---

## 8. Pareto honesty

**`dominated_by`: inapplicable — and this is not an unchecked null.** BATCH-016
produces no (time, memory, data) point for any algorithm. It computes no relation,
no closure, no rank, no solve and no cost quantity; it evaluates PASS/FAIL
booleans of an assertion over lists of field elements. There is nothing to place
on a frontier and nothing that could dominate it. Writing `dominated_by: null`
would imply an undominated algorithmic point exists — a fabrication under AGENTS
rule 5 — so the field carries this sentence instead.

**`sota_delta`: zero on every axis, quantitatively.** For the instance this batch
touches (n = 733): Pollard rho at an expected √(πn/4) = 24.0 group operations with
O(1) memory; BSGS at 2√n = 54 operations with √n = 27 stored entries; exhaustive
search at 733 operations. Closest specialised baseline: Gaudry/Semaev-style index
calculus over this same factor base — also not run; **not one relation was
collected**. Time delta 0, memory delta 0, data delta 0 against all four.

Against `docs/target-result-profile.md`: **not target-class, and not close.** A1
asks for mechanisms moving an asymptotic exponent on a central hard problem under
explicit numbered heuristics, validated at cryptographic scale. This batch
measures six lines of Python on a 12-bit prime. Its value is entirely
instrumental — but that value is real, because without it every past and future
"CTRL-4 PASSES" is uninterpretable.

---

## 9. Recommended disposition: REWRITE **and demote**

**RETIRE is wrong** because the checker is demonstrably not inert: D-6, D-7 and
D-9, together with cases (2) and (3), show it discriminates within-block
misalignment and length. An assertion with non-zero power against a future
refactor is worth ten lines.

**RETAIN-AS-IS is wrong** because the pre-registered consequence has already fired
on the BATCH-015 record, and because condition (ii) is blind to on-curve
membership, distinctness, orbit disjointness, provenance, and the B=193 tail.

So **REWRITE** — and the demotion is the load-bearing half. The rewritten
assertion must be labelled an **input-integrity regression assertion, not a
control**, and no record may cite it as evidence about φ-invariance, because
clause (e) remains a constructor identity no matter how many clauses surround it.

### CTRL-4′ — factor-base input-integrity assertion (freezable as written)

Precondition: B mod 3 = 0, else report NOT_APPLICABLE and invoke clause (h).

- **(a)** `pow(ζ₃,3,p)==1` **and** ζ₃ ∉ {0,1}. *The axis the old assertion missed entirely.*
- **(b)** `len(F)==B`.
- **(c)** `len(set(F))==B` — distinctness.
- **(d)** `E.lift_x(x) is not None` for every x∈F — on-curve membership.
- **(e)** For all 0≤j<B/3, k∈{1,2}: `F[3j+k]==pow(ζ₃,k,p)*F[3j]%p`, and `F[3j]≠0`.
  **Labelled in the contract text as a constructor identity that verifies the
  builder's own arithmetic and nothing about the mathematics.**
- **(f)** Orbit leaders pairwise orbit-disjoint: for j≠j′, `F[3j′] ∉ {F[3j], ζ₃F[3j], ζ₃²F[3j]}`. O(B) with one set.
- **(g)** **Provenance**: record sha256(p,a,b,derived_seed,B,ζ₃) beside
  `factor_base_sha256`, and assert that rebuilding F from the recorded instance
  reproduces F byte-identically.
- **(h)** **Tail**: when B mod 3 ≠ 0, indices in [3⌊B/3⌋, B) are asserted under
  (c), (d), (g) and the tail indices are recorded explicitly rather than silently
  skipped.

Every clause reports separately, with failing sets as **named sets, never counts
alone** (PRED-ID-STR). Clauses (d), (f), (g) execute **outside** any window whose
`wall_seconds` the contract reports — clause (d) costs B modular square roots per
cell, the same order as building the factor base, and per KN-LIT-7593 an
invariant's own cost must be charged before it is called free.

### Pre-stated mutation test CTRL-4′ must pass before freezing

Must FAIL, with the named clause firing:
M1 ζ₃:=5 → (a) *[old assertion PASSES]* · M2 case-2 replacement → (e) at (0,1) ·
M3 case-3 interleave → (e) at (0,1),(0,2),(1,1),(1,2) · M4 block 0 := orbit of
off-curve y=4 → (d) *[old PASSES]* · M5 block 1 := block 0 → (c),(f) *[old
PASSES]* · M6 block 0 := [0,0,0] → (c),(e) *[old PASSES]* · M7 wholly fabricated
FB → (d),(g) *[old PASSES]* · M8 truncate to 189 → (b) · M9 at B=193, F[192]:=0 →
(d),(h) *[old PASSES]*.

Must PASS, and **this row is mandatory**:
M10 blocks 0,1 swapped whole → all clauses PASS, pre-stated, with the recorded
reason that a whole-block permutation does not break the block-circulant φ-shift.
*A mutation set with no pre-stated-PASS row documents no boundary.*

At least M4–M7 and M10 must be re-derived by a session that did not author the
successor contract.

### The strongest case **against** my own recommendation

- **F-RT1 (cheapest, zero compute).** If `derivation_note.md` shows the exactness
  argument needs *only* within-block alignment — no on-curve, distinctness,
  orbit-disjointness or provenance property — then clauses (c),(d),(f),(g) protect
  nothing, REWRITE collapses to relabelling, and **RETIRE becomes correct**. I did
  not read the derivation note in full; my claim that it needs those properties is
  asserted from CTRL-4's own contract text ("this is the hypothesis the derivation
  note's exactness rests on") and is **not verified against the derivation
  itself**. That is a real gap in this review and I name it.
- **F-RT2, and I flag it against myself.** The committed builder *already* enforces
  distinctness and on-curve membership internally. So my mutations reach states
  the current single call path cannot reach, and clauses (c),(d),(f),(g) may
  themselves be constructor identities on every reachable path. My counter is that
  a control exists to catch a *future* bug, not the current constructor, and that
  a control which can only restate its constructor is exactly what BATCH-015
  condemned. But if the Coordinator holds that a control must be justified against
  reachable states only, **RETIRE follows and I would not contest it.**
- **F-RT3.** If clause (d)'s B `lift_x` calls perturb a reported timing and cannot
  be moved out of the window, (d) must be dropped or sampled — and dropped, the
  rewrite loses most of its added power.

---

## 10. Premature closure, both directions

**Over-reading is the live risk**, and §2 and §6 are the answer.

**Premature retirement is also live, and I decline it.** "The checker is a
constructor identity, therefore retire it" would discard an assertion with
demonstrated discriminating power on the strength of a fatigue argument about a
search that found blind spots. Blind spots are grounds for widening an assertion,
not for deleting it. Per `docs/inventor-protocol.md` §4, a closure needs a named
obstruction, an argument, and forward guidance; *"CTRL-4 detects nothing"* is not
an obstruction, it is a false statement, and I decline to write it.

**And the honest middle, which I am obliged to state because it is true.** For the
one job the checker was actually wired to do inside the BATCH-015 probe — confirm
that the builder laid its returned list out in aligned blocks of three — the
checker is adequate, and cases (2), (3), D-6 and D-9 confirm it. **The six lines
are not buggy.** My objection is that the job they do is strictly smaller than the
word "control" in the frozen contract promises, and that the gap is where a
successor will overclaim.

---

## 11. Narrowest supported statement

At commit `1454d2be`, on CURVE-J12S1 (p=2293, n=733, ζ₃=1303) at B=192, on one
host with one realisation each and a passing determinism repeat, the CTRL-4
assertion as byte-verbatim copied from `probe_driver.py` lines 416–441 reported
JOINT PASS on the unmutated baseline and on both bogus-ζ₃ inputs (pre-stated, not
a new result), and JOINT FAIL via condition (ii) on the single-element replacement
at (j,k)=(0,1) and on the two-block interleaving at (0,1),(0,2),(1,1),(1,2).
Condition (i) reported PASS in all five cases because all five inputs preserve
length by construction. **That is the whole of what was measured.** It establishes
that the checker is not vacuously always-PASS and that it discriminates
within-block misalignment on this instance at this B. It establishes **no general
layout-detection capability**, and a red-team diagnostic at the same commit
exhibits eight mutations the same checker misses.

## 12. Next concrete action

At TASK-20260730-040, record the disposition as **REWRITE AND DEMOTE**, carry
CTRL-4′ clauses (a)–(h) and the M1–M10 mutation test verbatim into the
successor-contract obligation, and record **CTRL-RT039-A** (the
mutation-completeness rule) as a rationale amending R-9 in the same decision —
zero compute, no new card, no enlargement of this batch, no approval of
EXP-STR-004.

## 13. Bounded-card disclosure — what I did not reach

- I did **not** read `experiments/EXP-STR-004/derivation_note.md` in full, so
  F-RT1 is stated as a falsifier and not as a finding.
- I did **not** audit the concurrent TASK-20260730-038 validation report: it is
  not committed, and reviewing a working-tree-only artifact as durable evidence is
  refused by my role contract.
- I did **not** re-verify the dispatcher's post-commit verifier acceptance of
  `1454d2be`; I verified the commit's path set by `git` and stopped there.
- My D-11 provenance mutation was **not run as designed** (seed 2 yields p=2953, a
  different prime) and is reported as not run rather than weakened into a number.
