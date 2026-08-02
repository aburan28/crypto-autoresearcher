# CHECK (a) — Independent review of the OD-4 branching-bound attempt (TASK-20260801-806)

**Task** TASK-20260801-809 · **Goal** GOAL-AES-001 · **Batch** BATCH-004 · **Role** validator
**Artifact class** PROSE_REPORT · **Provenance** in-text block at §9 (Part B admits either form).
**Snapshot reviewed** `cc660597e3bcc616521bce443b9a17eafa4393c2`, parent `3e6b8b73`, receipt bound at `db4b321a`.

**VERDICT FOR CHECK (a): `passed`, with 1 medium and 5 low defects.**
This verdict is confined to check (a). It is never merged with, averaged against, or carried
across to check (b) in `od3_and_hole_ii_review.md`.

Everything below is TOY SCALE. Nothing here is crypto-scale evidence, nothing supports an
AES claim at any round count, and this report assigns no evidence strength and recommends no
promotion.

---

## 1. Evidence integrity

| check | result |
|---|---|
| `cc660597` reachable from HEAD | **YES** (`git merge-base --is-ancestor`) |
| parent is `3e6b8b73` as declared | **YES** |
| commit touches exactly the 9 declared paths, no more, no fewer | **YES** (set difference empty both ways) |
| 8 producer-artifact SHA-256 recomputed from `git show cc660597:<path>` | **8 of 8 MATCH** |
| receipt's own self-digest `ea8376…` | **UNVERIFIABLE — see D-809-1** |
| `git diff --name-status 613658c6 HEAD` | **all `A`, zero in-place modification** of any BATCH-001/002/003 artifact |

**D-809-1 (low, evidence-integrity annotation, NOT a producer defect).** The receipt asserts
its own digest as `ea8376949968…`. The committed bytes at `cc660597` hash to
`d58e80deaffb…`; at HEAD (after the `db4b321a` binding write) to `7ae1d254ae02…`. I attempted
three reconstructions of the claimed pre-commit byte-state (self-entry set to `null`, to `""`,
and to the asserted value) and none reproduces `ea8376…`. The receipt's own
`self_digest_note` concedes the construction is self-referential. The honest disposition is
that **this value cannot be verified by any party and should be recorded as `null` with a
note**, as `hash_status` does for the other fields, rather than asserted. Nothing turns on it:
all eight producer artifacts verify exactly. I record it because an asserted digest that no
one can check is precisely the shape AGENTS.md rule 9 exists to prevent.

---

## 2. The pre-screen, audited in BOTH directions

`prescreen_od4.json` is committed, carries `written_first: true`, a UTC freeze stamp
(2026-08-01T15:31:10Z), the git commit at write time and the dirty-tree state. **Six
candidates, six verdicts, none missing.**

### 2.1 Direction one — was any IN_SCOPE_VACUOUS candidate pursued?

**No.** I searched both `od4_branching_bound_report.md` and `od4_results.json` for
`CAND-806-A` and `CAND-806-E`. Every occurrence is a screen-table row, an explicit
"was not pursued" statement, or a forward-guidance instruction not to attempt them. **No
lemma, no derivation, no phase and no code path for either candidate exists in the package.**
Direction one: clean.

### 2.2 Direction two (the adversarial half) — was an in-scope candidate killed on an inflated constant?

This is the half that guards against premature closure (`docs/inventor-protocol.md`), and it
is the half a producer cannot perform on itself.

- **CAND-806-A** was killed at interface constant **30**, the measured forward diameter of
  the (λ,k) graph over GF(2^8), against a ceiling of ~7. I did **not** re-measure the 1020-node
  GF(2^8) diameter within budget (recorded as an unrun check, §8). I *did* independently
  recompute the GF(2^4) (λ,k) graph from my own edge rule and confirm the target matrix is
  **strongly connected on all 60 nodes** while the three nulls decompose into 60, 15 and 5
  components — the graph object the screen refers to exists and behaves as described. The
  kill margin claimed is 23 against a ceiling of 7; even a large error in the measured
  diameter would not bring it under 7. **I find no inflation.**
- **CAND-806-E** was killed on *two* grounds: no exhibitable upper bound on n, and a lower
  bound of 30. A candidate with no exhibitable upper bound is correctly screened out under a
  threshold test; that is not an inflated constant, it is an absent one, and the screen says
  so rather than inventing a number.
- **The four PURSUE candidates all carry n = 1 and survive both interface-to-round
  conversions.** I checked this is substantively true and not a label: §4's derivation
  (LEM-806-1…4 and the Assembly) genuinely concludes from a **single** interface. I re-derived
  it; **no step of it iterates over interfaces, traverses the (λ,k) graph, or uses group
  growth.** The screen's own claim — that the machine which produced the bound is not the
  (λ,k) machine — is *correct*, and I verified it by working the proof, not by reading it.

**Both directions reported. The screen was applied honestly and was not used as an excuse to
decline work: 4 of 6 candidates were pursued and the two killed are the two that provably
iterate.**

---

## 3. Is a bound stated? Yes — and I worked it lemma by lemma

I re-implemented GF(2^8) and GF(2^4)/GF(2^2) arithmetic, RREF, subspace enumeration, minors,
and the branching computation **from scratch**, taking no code and no constant from
`od4_branching.py`. Scripts under my scratchpad; numbers below are mine.

### 3.1 Lemma-by-lemma

| lemma | its one job | my independent finding |
|---|---|---|
| **LEM-806-1** ShiftRows index bookkeeping | i ↦ (j+i) mod 4 is a bijection for each j | **HOLDS.** Trivially true; I used the same index map in my from-definition brute force and it reproduced the closed form. |
| **LEM-806-2** perturbation set = ∏_i proj_i(K) = F^S | identify the reachable set | **HOLDS**, *conditional on an unnumbered hypothesis — see U-809-1 below.* proj_i(K) is an F-subspace of F, hence 0 or F; the four coordinates come from four distinct words (LEM-806-1) so they are perturbed independently. |
| **LEM-806-3** B = q^(s − dim(W_S∩K)) | turn the set into a count | **HOLDS.** \|π(W_S)\| = \|W_S\|/\|W_S∩K\| = q^(dim W_S − dim(W_S∩K)), and dim W_S = s because M is invertible. Verified by brute force below. |
| **LEM-806-4** dim(W_S∩F^S) = max(0, 2s−4) | bound the exponent's negative term | **HOLDS, recomputed over GF(2^8) for all 16 subsets S.** My table: s=0→0, s=1→0 (all 4 S), s=2→0 (all 6 S), s=3→2 (all 4 S), s=4→4. Exactly max(0, 2s−4). |

Supporting recomputations over GF(2^8), M = circulant(02,03,01,01) mod 0x11B:
- **all 16 entries nonzero: TRUE** (PRED-1 holds, independently of `verify_derivation.py`);
- **MDS: TRUE — 69 minors of all sizes computed, 0 singular** (PRED-2 holds).
  *Prose defect D-809-2 (low):* the report says "all 69 **proper** minors plus the
  determinant". There are **68 proper minors plus the determinant = 69 total**. An off-by-one
  in prose only; the computation is right.

### 3.2 The Assembly

I performed the minimisation my own way, using only `dim(W_S∩K) ≤ min(dim(W_S∩F^S), dim K)`
(valid because K ⊆ F^S by the definition of S) and `dim K ≤ 3` (dim K = 4 is the excluded
constant π):

| s | dim(W_S∩F^S) | admissible dim K | min exponent |
|---|---|---|---|
| 1 | 0 | 1 | **1** |
| 2 | 0 | 1,2 | 2 |
| 3 | 2 | 1,2,3 | **1** |
| 4 | 4 | 1,2,3 | **1** |

**Minimum exponent = 1 ⇒ B ≥ q^1 = 256.** My computation, my arithmetic. **The bound
FOLLOWS.**

Note the s = 4 row is the one that needs care: `dim(W_S∩F^S) = 4` there, which alone would
give exponent 0. The bound survives only because `dim K ≤ 3`. The report's Assembly table gets
this right; a reader skimming LEM-806-4 alone would not. Worth naming for the red team but not
a defect.

**The report's own flagged discrepancy is real and correctly disclosed:** `od4_results.json`
phase P3 reports `min_over_all_S = 1` (i.e. B = q^0 = 1) because that phase admits dim K = 4.
The report flags this in §4.2 rather than letting a reader discover it. That is correct conduct.

### 3.3 Tightness at L = 8, 16, 24 — verified

| K | dim K | L | S | dim(W_S∩K) | exponent | B |
|---|---|---|---|---|---|---|
| span(e₀) | 1 | 8 | {0} | 0 | 1 | **256** |
| W_S∩F^S for S={0,1,2} | 2 | 16 | {0,1,2} | 2 | 1 | **256** |
| span(e₀,e₁,e₂) | 3 | 24 | {0,1,2} | 2 | 1 | **256** |

All three recomputed over GF(2^8) by me. **The tightness claims hold.** Stronger than
"witnessed": since the Assembly proves min exponent = 1 over *all* admissible (S, dim K) and
these witnesses attain it, B ≥ q is the exact minimum, not merely a bound with three
examples. The report understates this.

### 3.4 Independent brute-force cross-checks

- **GF(2^4), all 78 899 proper nonzero subspaces enumerated by me (+2 trivial = 78 901, exactly
  the producer's count):** B histogram `{16: 4377, 256: 70303, 4096: 4219}`, **min B = 16 = q**,
  per-dim minima (d=1,2,3) = **16, 16, 16**. Reproduces the producer's §4.4 row exactly.
- **GF(2^2), all 527 proper nonzero subspaces (+2 = 529, exactly the producer's count):**
  min B = **4 = q**. **Not MDS: 24 of 69 minors vanish** — the producer's "16 vanishing 2×2 and
  8 vanishing 3×3" sums to exactly 24. Confirmed.
- **From-definition brute force** (no structural shortcut: all four input words perturbed
  independently over K, real ShiftRows index map, real MixColumns, distinct π-images counted)
  over GF(2^2): agreement with the closed form on every kernel completed before my budget stop.
  The full 442-kernel pass did **not** finish inside my 1400 s; recorded as an unrun check (§8),
  **not** as agreement I did not obtain.
- GF(2^8) from-definition brute force is 256^4 ≈ 4.3·10⁹ evaluations per output word. Infeasible
  here; the producer records the same limitation as R806-5.

**Conclusion on §4: Proposition 806-1 FOLLOWS. Corollary 806-2 (L + Y ≤ 24) FOLLOWS**
immediately from B ≥ 2⁸ together with B ≤ \|X\| = 2^(32−L).

### 3.5 The §6.2 obstruction and the "no increasing f(L,n)" argument — verified with one caveat

For a GF(2)-linear functional φ depending on ≥ 2 bytes, I confirm proj_i(K) = F for every i:
writing φ(v) = Σ φ_t(v_t), coordinate i can be driven to any value iff some φ_t ≠ 0 with t ≠ i,
which holds for every i exactly when φ depends on ≥ 2 bytes. Hence the perturbation set is F⁴,
its M-image is F⁴, and B = \|X\| = 2 at L = 31. **The obstruction is correct.**

**D-809-3 (low, overstatement).** "No lower bound of the shape B ≥ f(L,n) with f **increasing**
in L can exist" is proved only for *strictly* increasing f. A weakly-increasing f capped at 2
is not excluded by B ≤ 2^(32−L) — it is merely vacuous. The substantive claim (no useful bound
growing with L) is right; the universal phrasing is one notch stronger than the argument.

---

## 4. F-2 RULING — is Proposition 806-1 a result about OD-4 at all?

**Ruling: the producer's framing is HONEST, the scoping is CORRECT, and if anything the
producer's "answered NO" is under-explained rather than over-claimed. I find no
class-inflation defect. I do find one scoping imprecision, D-809-4.**

Reasoning, from what I re-derived rather than read:

1. **It is genuinely not the OD-4 machine.** OD-4 asked whether PROP-701-I's *group-growth*
   argument converts into a quantitative inequality. I worked every step of §4 and **no step
   uses the group-growth argument, the (λ,k) graph, transitivity of invariance, or more than
   one interface.** It is coordinate-support and minor algebra at a single interface. The
   producer says exactly this, in the statement rather than in a footnote (§4 preamble,
   R806-1, R806-2, §5.5(v)).
2. **Two distinct questions are answered NO, and both answers are earned.**
   (i) *Does the Step-1/2/3 machinery force a B–L–n inequality?* NO, with a named and
   re-derivable breaking step (§5 below).
   (ii) *Can any bound of OD-4's hoped-for shape exist?* NO, by the B ≤ 2^(32−L) ceiling,
   which I verified (modulo D-809-3's phrasing).
   Answering the posed question NO **while** returning a positive result on a smaller class by a
   different method is the honest shape of this outcome, not a bait-and-switch.
3. **The smaller class is declared everywhere it matters.** R806-1 states the bound "must never
   be quoted as a bound for OD-4's class". §5.5 lists four things "not reached at all" with the
   reason for each. The commit message itself leads with "FOR A STRICTLY SMALLER CLASS THAN
   OD-4's". I could find no place in the package where the F-linear bound is quoted as an OD-4
   bound.
4. **The bound is not a qualitative statement dressed as a cost inequality** — the handoff's
   named target defect. It is an *exact closed form* whose minimum I recomputed. If anything the
   opposite risk is present:

**D-809-4 (medium, scoping/framing).** The dispatch card asked for a bound on B "**for a given
entropy loss**". Proposition 806-1's bound is **independent of L**. There is therefore **no
trade-off between L and B** in the proposition — it is not a cost inequality in the card's
sense at all. Corollary 806-2 restores a trade-off shape (L + Y ≤ 24) but does so by
substituting a *different* quantity (yield Y) and is an immediate rearrangement of
`B ≥ 2⁸` with the trivial ceiling `B ≤ 2^(32−L)`; its content beyond "B ≥ 256" is arithmetic,
not new mathematics. The producer is transparent about this in §12(1) (re-pose OD-4 in Y). But
**the package's exponent-relevant yield should be recorded by the Coordinator as: an exact
one-interface branching formula for a strictly linear subclass, plus a proof that OD-4's
hoped-for inequality shape cannot exist — and NOT as "a cost inequality was obtained".**
I raise this to medium because it is the sentence most likely to be mis-transcribed into a
downstream evidence record.

---

## 5. The named breaking step — re-derived independently

The producer names the break as **the first sentence of Step 2**: Step 1 *consumes* equality of
π-values but under B > 1 *emits* only B-confinement, so the induction fails at its first step.

**I re-derived this and I agree the named step is the RIGHT step.** The argument is a type
argument and it is checkable without computation: PROP-701-I's induction is closed precisely
because its conclusion type equals its hypothesis type. Under branching, hypothesis type is
`π(a) = π(b)` and conclusion type is `π(u), π(u+v) ∈ R_j(x)` with `|R_j(x)| ≤ B`. For every
B ≥ 2 the second is strictly weaker than the first, so the feedback edge of the induction does
not typecheck. The break is at interface 1, before any traversal. **Correct, and correctly
located as the *first* failure rather than the most visible one.**

The two "further, independent failures" are also right and are worth having on the record:
- **Step 2's union**: under branching R_j(x) varies with x, so the union is over *different*
  confining sets. Correct.
- **Step 3's group closure**: B-confinement is reflexive and symmetric but **not transitive**;
  no equivalence, hence no group, hence no span. Correct, and this is the deepest of the three
  — it is why no amount of care at Step 2 rescues the machinery.

**Closure standard (§4 of the inventor protocol): MET, not the fatigue standard.** There is a
named obstruction (type instability of the induction), an argument for it (the three
independent failures), and forward guidance that is *specific and falsifiable* (§3.3's three
routes, of which route 2 — a bounded-index subgroup statement — is stated as a genuine open
question rather than as a plan). This is a clean, argued negative and I record it as a
**complete and valuable outcome**.

---

## 6. F-3 — MY OWN PER-GATE ASSESSMENT, AND THE REVIEW HALF OF GATE (4)

The producer asserts **no** gate satisfied and requests **no** promotion. I concur with that
posture. My independent per-gate finding differs from the producer's self-assessment in two
places, both named.

### Gate (1) — proof decomposition and per-attempt × inverse-success bookkeeping
**MET FOR THE PROPOSITION; DEGENERATE FOR THE COST MODEL.**
LEM-806-1…4 are genuinely single-responsibility — I worked each in isolation and each does
exactly one job — and the Assembly is a correct finite minimisation over a table I recomputed.
§5.1 does name an attempt, a per-attempt cost (C_node·N(n)) and a success probability, and
does multiply them, in both a frontier form and a single-guess form. **But** the column
actually tabulated is the frontier column, where p = 1 **by construction**, so the
inverse-success factor is 1 and the bookkeeping does no work in the number that is used. It is
present and honest; it is not load-bearing. Gate (1) stands for §4; it is formally satisfied
but substantively empty for §5.

### Gate (2) — every conditional dependence numbered, each paired with a validation experiment
**NOT MET.** I agree with the producer that HEUR-806-3 (baseline) and HEUR-806-4 (four-word
independence) carry **no** schedulable validation experiment, and both are load-bearing for any
barrier reading. HEUR-806-1 and HEUR-806-2 do carry concrete, falsifiable, dispatchable
experiments and are good specimens.

**And I found an UNNUMBERED conditional dependence, which the handoff names as the
highest-value defect available in this check:**

> **U-809-1 (medium) — Proposition 806-1 silently inherits PROP-701-I's full "for EVERY state
> s" quantifier, and this dependence is numbered nowhere and appears in none of R806-1…7.**
> LEM-806-2's step "the four coordinates are perturbed by **four independent elements of K**"
> is valid only because each input word ranges over its *entire* coset w_t + K, which is
> exactly hypothesis (H2)'s unrestricted quantifier. If the object is required to propagate
> only on a structured subset of states — D-705-5 hole (ii), the very hypothesis
> TASK-20260801-807 measured in the *same batch* — the reachable perturbation set is a proper
> subset of F^S, W_S shrinks, and **B ≥ q does not follow**. §5.5's "not reached at all" list
> names layer-dependence, non-linearity, GF(2)-linearity and multi-word objects, but **not the
> state quantifier.** This is not a numbering formality: it is the one hypothesis the batch's
> other producer independently demonstrated to be restrictable, and 807's measurement that
> 12.5 % of admissible configurations collapse the sweep to reach 1 is direct evidence that the
> restriction bites on exactly the freedom LEM-806-2 consumes.
> **Severity medium**, not high, because the object class in §2 does state "for every state s"
> in the hypothesis, so the dependence is present in the definition; the defect is that it is
> never carried into the heuristics or the limitations, where a reader looks for it.

### Gate (3) — concrete cost table
**NOT MET.** Present and creditable: memory alongside time (§5.3 and the 2³⁴-byte machine
ceiling), an explicit time–memory trade-off (MITM at 2^(16n) memory, which the producer itself
notes *destroys* the barrier reading at n = 7), parallelization, a hidden-overhead disclosure
naming the 2⁷² relation-table cost for general π, six optimistic/pessimistic assumptions each
flagged **with its direction**, and an affected-vs-safe scope statement. That is a good cost
table by this campaign's standards. It is nevertheless **not met**, on the producer's own two
grounds, which I confirm independently: the central column's J = 2³² is **measured at six
witness kernels, not established as a minimum** (my own GF(2^4) exhaustive pass reads per-word
min B = q at every dimension, consistent with — but not evidence for — the analogue's q³ joint
minimum), and no alternative baseline is costed (HEUR-806-3). Additionally: **peak RSS was not
measured** (`/usr/bin/time` absent) and is correctly reported as not measured rather than
estimated — that is the right conduct, and it also means every memory figure in §5.3 is
**modelled**.

### Gate (4) — independent review + red team
**NOT SATISFIED. The review half is performed by this report; the red-team half is
outstanding (TASK-20260801-810 has not run).** Recording this precisely, as the completion
gate requires:

- Gate (4) is satisfied by **this review together with the TASK-20260801-810 red team, and by
  nothing TASK-20260801-806 did.** The producer correctly claimed nothing here.
- **The review half itself is weakened and I state it against my own interest:** under
  inference-amendment `0137a051`, this session supplies independence in **SESSION** and **NOT
  in MODEL**. My agreement with the producer is **correlated confirmation, not independent
  confirmation**, and nothing in this report may be counted toward a goal-closure quorum.

**WHICH GATES STAND, PLAINLY: gate (1) stands for the proposition only and is degenerate for
the cost model; gate (2) does NOT stand and now has an unnumbered dependence (U-809-1) against
it; gate (3) does NOT stand; gate (4) is half-performed. No gate package stands, and no
promotion is supportable on this material.** That is a finding about the package's readiness,
not a criticism of it: the producer said the same and asked for nothing.

---

## 7. F-4 — CONTROLS: verifying the producer's self-caught defect, AND BUILDING THE SIBLING NULL NOBODY BUILT

### 7.1 The producer's self-caught defect — VERIFIED

Claim: CTRL-NULL-1 (a 2×2 zero block) isolates "M has no zero block", **not** "all entries of
M are nonzero", so MDS is not load-bearing and the operative property is *no proper nonempty S
has W_S ⊆ F^S*.

I rebuilt all four controls over GF(2^4) and re-ran the **exhaustive** minimisation (all 78 899
proper nonzero subspaces) on each, from my own arithmetic:

| control | invertible | all entries ≠ 0 | violates P | zero block | **my min B** |
|---|---|---|---|---|---|
| target circ(02,03,01,01) | yes | yes | no | no | **16 = q** |
| CTRL-NULL-1 (2×2 zero block) | yes | no | S ∈ {{0,1},{2,3}} | yes | **1** |
| CTRL-NULL-2 (exactly one zero entry) | yes | no | **no** | no | **16 = q** |

**Confirmed on every count.** CTRL-NULL-2 negates "all entries nonzero" and the bound
**survives**, so "all entries nonzero" is not what CTRL-NULL-1 isolates. PRED-8 was
pre-registered and held in the *inconvenient* direction. **The producer's self-diagnosis is
correct and is the honest reading.**

I add a structural observation the producer does not make: with all entries of M nonzero, every
column has full support, so `W_S ⊆ F^S` is **impossible** for proper S. **"All entries nonzero"
therefore *implies* P outright** — which is exactly why negating it via one zero entry cannot
break the bound, and is the mechanism behind PRED-8's inconvenient outcome.

### 7.2 The sibling null nobody built — MY OWN, and it changes the attribution

A producer catching its own defect does not mean the **replacement** property is isolated.
V-804-1 was found by building the null nobody built, so I built it.

**The replacement property P and the producer's stated isolation "M has no zero block" are not
the same property.** "No zero block" is a *two-sided* decomposability condition (M block-
diagonal: both M[Sᶜ][S] = 0 and M[S][Sᶜ] = 0). P is *one-sided* (some S with every column in S
supported on S). P is strictly weaker. **No control in the package separates them**, because
CTRL-NULL-1 violates both at once — which is the exact shape of the V-804-1 defect, one level
down.

So I constructed two matrices over GF(2^4) that violate **P alone** while satisfying "no zero
block", and ran the same exhaustive minimisation:

| my control | invertible | violates P at | has zero block | **my min B** | per-dim minima |
|---|---|---|---|---|---|
| **VALIDATOR-SIB-1** = [[2,3,1,1],[0,2,3,1],[0,1,2,3],[0,1,1,2]] (column 0 supported on {0}) | yes | S = {0} | **NO** | **1** | 1, 16, 16 |
| **VALIDATOR-SIB-2** = [[2,3,1,1],[1,2,3,1],[0,0,2,3],[0,0,1,2]] (columns {0,1} supported on {0,1}) | yes | S = {0,1} | **NO** | **1** | 16, 1, 16 |

**Finding.** Both are invertible, both are **not** block-decomposable, both violate P alone, and
**both destroy the bound (min B = 1)**. Therefore:

1. **The producer's replacement property P IS the operative one, and it is now genuinely
   isolated** — by a null the producer did not build. This *strengthens* Proposition 806-1's
   attribution.
2. **But the producer's own stated isolation is itself still one notch over-strong.**
   CTRL-NULL-1 does **not** isolate "M has no zero block" either: my siblings break the bound
   with no zero block present. "No zero block" is *sufficient* to break it, not *necessary*.
   The property that is necessary and sufficient, among the four I tested, is **P**. §7's final
   paragraph names P correctly; §7's table and the sentence "it isolates the strictly stronger
   property *M has no zero block*" do not, and the commit message repeats the latter.
   **D-809-5 (low): the report's control-attribution sentence over-attributes by one notch
   relative to its own concluding sentence, and the package contains no control that
   discriminates the two.** This is the same failure class as V-804-1, at reduced severity,
   found by the method that found V-804-1.
3. **None of this touches AES's M**, which has all entries nonzero and therefore satisfies P
   unconditionally. Proposition 806-1 is unaffected.

**Null-decay check (`docs/inventor-protocol.md` §3).** The controls here are of the right shape:
the statistic (min B) does what it *should* under negation — it collapses to 1 exactly when the
named property is destroyed and stays at q otherwise, across four producer controls and two of
mine, over exhaustive enumerations rather than samples. There is no "quantity that fails to
decay" tell in check (a).

---

## 8. F-8 — did a falsified pre-registration propagate into a surviving conclusion?

**PRED-11** predicted J < B⁴ at the minimising kernels; measured J = B⁴ = 2³². I traced every
downstream use. §5.2 and §5.3 use J = 2³² as a **MEASURED** value — that is, they use the
*falsifying measurement itself*, correctly labelled "MEASURED at those kernels only; not an
exhaustive minimum". **No conclusion rests on the falsified prediction.** I note the direction
of the error: the falsification moved the number *upward*, i.e. in the direction that flatters
a barrier reading — and the producer flags precisely this as OPT-5, "PESSIMISTIC (favours the
barrier reading), and therefore the one to attack", and declares gate (3) unmet on it. That is
the correct handling of an inconvenient-in-one's-own-favour result. **Clean.**

---

## 9. Provenance, stand-down, supersession, literature

- **Provenance (my own digests).** `od4_results.json` carries a first-class `inference` block
  (policy/requested_policy `executor-implementation`, resolved `claude-opus-5`, `fallback_used:
  true`, `model_verified: false`, standing basis `0137a051`) and a 4-entry
  `artifact_provenance` list. **I recomputed all three non-self-referential digests: all
  MATCH.** The self-entry is self-referential and unverifiable (same pathology as D-809-1).
  `od4_branching.py` carries a comment-block stanza (class SOURCE_CODE). The report takes the
  pointer form, equally compliant under Part B. **No gap found for TASK-20260801-806.**
- **Stand-down: CLEAN.** Every occurrence of "mutation-control", "escape enumeration",
  "GATE-601-A" or "reject_scoped" in this task's artifacts is a **negative declaration of
  non-performance** or a scope statement. No instrument work of any kind was performed.
- **Supersession: CLEAN.** All files new; nothing superseded; PROP-701-I and Proposition 801-1
  stand exactly as written.
- **Literature.** The package makes **one** recollection (MDS matrices standard in wide-trail
  designs), marked `unverified-from-memory` with LOW recall confidence and load-bearing
  nowhere; M's MDS property is recomputed, and I recomputed it again. **Every literature
  statement in MY report would likewise be unverified-from-memory; I make none.** No primary
  source is reachable in this environment and novelty is unresolvable here.
- **Analogue discipline: CLEAN.** §4.4 leads with "These are ANALOGUES. Their readings are NOT
  evidence about GF(2^8) and are certainly not evidence about AES." §0 and §5.5(v) repeat it.
  No transfer to GF(2^8) or AES is asserted without an argument; where transfer is claimed
  (HEUR-806-1) it is numbered as a heuristic, not asserted.

## 10. Checks I did NOT run — named, so that no unrun check reads as a check that found nothing

1. **GF(2^8) (λ,k) graph diameter (claimed 30).** Not re-measured; 1020 nodes was outside my
   remaining budget. The CAND-806-A kill margin (23 against a ceiling of 7) is large enough that
   I do not regard this as material, but I did not verify the number.
2. **The full 442-kernel GF(2^2) from-definition brute force.** Started, did not finish inside
   my 1400 s stop. Partial agreement only; I claim no more.
3. **GF(2^8) from-definition brute force.** Infeasible (≈4.3·10⁹ evaluations per output word).
4. **The joint-branching computation J(K).** I verified per-word B independently; I did **not**
   independently recompute the joint J at the six GF(2^8) witnesses. Gate (3) fails on this
   quantity anyway, on the producer's own statement.
5. **§2.5(2)'s dimension claim** in the 807 package (invariance only on an M-image of
   dimension 1 + |J|) — see check (b); asserted as a derivation, not re-executed by me.

---

## 11. Defects — check (a)

| id | severity | statement |
|---|---|---|
| **U-809-1** | **medium** | Proposition 806-1 silently inherits the unrestricted "for every state s" quantifier via LEM-806-2; unnumbered, absent from R806-1…7, and demonstrably restrictable by this batch's own TASK-20260801-807. Gate (2) fails on it. |
| **D-809-4** | **medium** | The proposition is L-*independent* and so is not a cost inequality in the card's sense; Corollary 806-2's trade-off is arithmetic on B ≥ 2⁸. Must not be transcribed downstream as "a cost inequality was obtained". |
| **D-809-5** | low | CTRL-NULL-1 does not isolate "M has no zero block" either; my VALIDATOR-SIB-1/-2 break the bound with no zero block. The report's own concluding sentence (property P) is right; its table sentence over-attributes. |
| **D-809-1** | low | Snapshot receipt asserts a self-digest that no party can verify and that I could not reproduce under three reconstructions. Not a producer defect. |
| **D-809-2** | low | "69 proper minors plus the determinant" — 68 proper + det = 69 total. Prose only. |
| **D-809-3** | low | "No f increasing in L can exist" proved only for strictly increasing f. |

**No high-severity defect found in check (a).**

---

## 12. Verdict, check (a)

**`passed`.**

Meaning, precisely and no more: the OD-4 package is **admissible evidence** — its artifacts are
present and hash-verified, its pre-screen is honest in both directions, **Proposition 806-1
FOLLOWS** by my own independent re-derivation and exhaustive recomputation, its tightness claims
hold, its named breaking step is the right step, its negative outcome meets the section-4
closure standard, and its self-reported falsification propagated into nothing.

It is **not** a speedup, **not** a cost inequality in the sense the card asked for (D-809-4),
**not** a result about OD-4's class (R806-1, which the producer states and I confirm), and
**not** promotable: gates (2) and (3) do not stand and gate (4) is half-performed. This
verdict assigns no evidence strength and recommends no promotion — those are the Coordinator's
transition in TASK-20260801-811.

---

## 13. Validator inference block

```yaml
inference:
  policy: validator-independent
  requested_policy: validator-independent
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml routes this role to a GPT-5.6-family alias that
    Claude Code cannot resolve; the harness resolved to the inherited Claude model.
  model_verified: false
  model_verified_reason: "python3 -m orchestration.adapter doctor --probe was not run."
  degraded_allowed: false
  independent_session: true
  independence_scope: >-
    SESSION ONLY, NOT MODEL. Under inference-amendment 0137a051, this review shares a model
    family with both producers, with the TASK-20260801-810 red team and with the Coordinator.
    Its agreement with them is CORRELATED confirmation, not independent confirmation.
    NOTHING IN THIS REPORT MAY BE COUNTED TOWARD A GOAL-CLOSURE QUORUM.
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  covering_manifest: validation_report.yaml
```
