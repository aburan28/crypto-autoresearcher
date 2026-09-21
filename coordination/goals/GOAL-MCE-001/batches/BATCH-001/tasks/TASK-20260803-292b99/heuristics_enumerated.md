# Heuristics enumerated — the 2026 subexponential line

**Task:** TASK-20260803-292b99 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`

---

## 0. The headline of this document

**`iacr:2026/1232`'s heuristics were NOT OBTAINED. Zero of them are enumerated
below, because zero were read.**

The paper's abstract (obtained) carries the word "heuristic" in the title and
the phrase "We make the conjecture that" in the complexity sentence, but it
**numbers, names, and states no heuristic**. Numbered heuristics, if the paper
has them, live in the body. The body was blocked by a Cloudflare bot-protection
challenge on the only host serving it (`source_access_log.yaml`, A02/A29, and
A03 for the archive path), and no aggregator has indexed the paper yet.

**Nothing is enumerated in their place.** This model's training data may contain
material about McEliece structural attacks; none of it appears here.
Reconstructing a numbered heuristic from memory and presenting it as
transcription is the specific fabrication AGENTS.md rule 9 forbids, and it is
the reason this task exists (the 137 KN-LIT entries filed 2026-08-03 are a map
built without reading). **A missing heuristic stays missing.**

What CAN be enumerated is the heuristic structure of the two papers whose full
text WAS obtained, one of which — `iacr:2024/1193`, *The syzygy distinguisher* —
is the object the primary target's abstract explicitly anchors its
subexponentiality to ("as the syzygy distinguisher of [R25]"). That is the
nearest available primary statement of the same claim shape, and it is
enumerated in §2 with its own numbering.

**Relay, never launder.** Each entry below records the source's own numbering,
its exact statement, whether the source offers evidence, and whether the source
itself flags the statement as unproven. Where the source hedges, the hedge is
reproduced.

---

## 1. `iacr:2026/1232` — Briaud, Lemoine, Randriambololona, Tillich

### 1.1 Status

| Field | Value |
|---|---|
| Heuristics obtained | **0** |
| Heuristics enumerated below | **0** |
| Reason | Body not retrieved; see `source_access_log.yaml` A02, A03, A04, A29 (403 `cf-mitigated: challenge`) and A05–A28 (no open-repository or aggregator copy) |
| Classification | `infrastructure_error`, NOT `negative_observation` (AGENTS.md rule 5) |

### 1.2 What the abstract does say about the epistemic status of its claims

These are the **only** hedging signals obtainable, transcribed VERBATIM:

- Title: **"A *Heuristic* Subexponential Attack on the McEliece Cryptosystem"** —
  the qualifier is in the title, not a footnote.
- Complexity sentence: **"We make the conjecture that this attack has a
  complexity which is of the same nature as the distinguisher, namely
  subexponential in the security parameter."**
- Distinguisher sentence: **"A byproduct of our approach is a new distinguisher
  for Goppa codes in even characteristic which is as the syzygy distinguisher of
  [R25] subexponential in the security parameter of the scheme."**

Read strictly, and strict reading is the whole job here:

- the **attack**'s complexity is presented as a **conjecture**, by comparison
  with the distinguisher — the abstract gives it no exponent and no formula;
- the **distinguisher**'s subexponentiality is asserted, and asserted *by
  reference* to `[R25]`;
- neither sentence exhibits an assumption, a numbered heuristic, or a
  probabilistic model.

**Whether the body numbers its heuristics is UNKNOWN.** The task instructed that
if the paper does not number them, the executor should number them and say so.
That instruction cannot be reached: the executor cannot tell whether the paper
numbers them, having not read it. **No executor numbering was invented.**

### 1.3 What a later heuristic-validation experiment would need, and does not have

The promotion gates in `/coordinate-research-goal` want a stated heuristic as
the object to test. For this paper that object **does not yet exist in this
program's hands**. The concrete unblocking actions, in order of cheapness:

1. Re-attempt `https://eprint.iacr.org/2026/1232.pdf` from a different network
   egress. The block is a Cloudflare bot challenge keyed on the requesting
   client/IP, not an authorization wall; the paper is licensed **CC BY**.
2. Wait for the HAL deposit. Three of four authors are Inria/ANSSI/Télécom Paris
   affiliated and HAL deposit is customary there; as of 2026-08-03 the deposit
   does not exist (A05, A06, A15, A27, A28).
3. Wait for aggregator indexing (OpenAlex count 0 at A07; OpenAIRE total 0 at
   A24; no Wayback capture at A21).

None of these is authorized by this task and none was performed beyond what the
log records.

---

## 2. `iacr:2024/1193` — *The syzygy distinguisher*, Randriambololona (KN-LIT-71d1a0)

**Full text obtained.** Source B01, sha256
`b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0`.
**Version caveat:** author's own copy, self-described *"(Eurocrypt 2025 version,
expanded, with supplementary material and errata)"*, dated 2025-05-02 on the
author's site; the ePrint record shows a later revision (2025-10-16, "last of 4
revisions"). **A later version may number things differently.** Everything below
is scoped to this sha256.

**Numbering is the paper's own.** The paper numbers exactly **one** Heuristic,
and separately labels **four** "Experimental fact"s which are empirical
statements it does not claim to have proved. Both classes are enumerated because
both are unproven inputs, and the paper distinguishes them by name.

### H1 — "Heuristic 1" (the paper's own number and label)

**Section:** 4, *"Regularity 2 and the small defect heuristic"*, under the
subheading *"The small defect heuristic"*, introduced VERBATIM by
**"Consequently, we postulate:"**

**Exact statement, as extracted:**

> **Heuristic 1.** Fix a field cardinality q, assume n is not too close to k in
> order to stay away from the counterexamples to the minimal resolution
> conjecture, and n < (k+1 choose 2) in order to ensure regularity 2. Then for
> random [n, k]_q-codes, with high probability:
>
> 1. if d > k + 1 − k(k+1)/n we expect β_{r−1,r} = 0 for r > k(k+1)/n.
> 2. if d⊥ > k(k+1)/n we expect β_{r−1,r} = ( k(k+1)/r − n ) (k−1 choose r−2)
>    for r < k(k+1)/n.

**[EXTRACTION-DAMAGED] on the displayed formulas in parts 1 and 2.** The
extraction returns unmapped `(cid:NN)` glyph tokens for the large binomial
delimiters, and the placement of `r` inside `k(k+1)/r − n` versus
`k(k+1)/n` is **not** reliably recoverable from the character stream. The
prose conditions ("Fix a field cardinality q", "n is not too close to k", "to
ensure regularity 2", "for random codes, with high probability") are clean. **The
formulas in parts 1 and 2 may not carry a claim in any deliverable.** Raw
extraction, unedited, for a reviewer with the rendered PDF:

```
Heuristic 1. Fix a field cardinality q, assume n is not too close to k in order
to stay away from the counterexamples to the minimal resolution conjecture, and
n < (cid:0)k+1 (cid:1) in order to ensure regularity 2. Then for random [n, k]q-codes, with
      2
high probability:
1. if d > k + 1 − k(k+1)          we expect βr−1,r = 0 for r > k(k+1)  .
                          n                                        n
2. if d⊥ > k(k+1)  we expect βr−1,r = (cid:16) k(k+1) − n (cid:17) (cid:0)k−1 (cid:1) for r < k(k+1) .
              n                                r              r−2                n
```

**Does the paper offer evidence?** Yes, explicitly and at length, and it also
states the limits of that evidence. VERBATIM:

> Unfortunately, even if the probability distribution of C is nice (say, uniform
> among codes of given [n, k]), it is not easy to control the distribution of
> φ_r, so we will not be able to give proofs. Moreover it could be that the
> iterative algebraic process in the construction of φ_r would lead to some
> unexpected constraints on its rank. And indeed, in this section we will identify
> some parameter ranges for which the defect cannot be small; but conversely, we
> will also give arguments that support the validity of this small defect
> heuristic at least under some proper conditions.

> A first argument in support of the heuristic is that it is unconditionally true
> when r = 2. Indeed, in this special case, [3] manages to give lower bounds,
> exponentially close to 1, on the probability that def(φ2) = 0.

> Another argument is the minimal resolution conjecture of [19]. […] However, two
> points require our attention:
> 1. This conjecture is now known to be false in general [11].
> 2. We work over a finite field, not an infinite one.

> Concerning point 1, we will argue that the conjecture is still "true enough"
> for our use. First, a nonzero defect might not be a problem in our Betti number
> estimates, as long as it remains small. Moreover, as noted in the introduction
> of [11], the conjecture has been proved for a large range of values of n and k.
> In fact, although [11] provides an infinity of counterexamples, these remain
> limited to very specific parameters, namely of the form n = k + O(√k). And
> indeed, perhaps the most valuable result for us is [17], which proves that the
> conjecture is true when n is large enough with respect to k.

Plus experimental support: the paper reports, VERBATIM, *"ticular β3,4 = 0
consistently in the random case confirms Heuristic 1 for these"* [sentence
fragmented by extraction — **[EXTRACTION-DAMAGED]**, cited only to record that
an experimental confirmation claim exists at that location], and Supplementary
Figure 14 with, VERBATIM: *"for random [56, 16]2-codes. For each pair (d, d⊥), a
few thousands of codes with these parameters were sampled uniformly (using
rejection sampling). The average value of def(φr) among these samples is
displayed, and also its 99% distri…"*

**Does the paper flag it as unproven?** **Yes, unambiguously.** It is called a
Heuristic, it is introduced with "we postulate", and the paper states outright
"we will not be able to give proofs". The intro also says, VERBATIM: *"partially
relying on a natural heuristic: random codes are not expected to admit more
syzygies than those forced by these parameters. We do not have full proofs for
this fact, but we provide experimental evidence and partial theoretical
arguments that support it."*

**What depends on it.** Theorem 3 — the paper's complexity claim — is introduced
by the VERBATIM sentence **"Now, under Heuristic 1, we have:"**. The paper's
headline is conditional on H1, in the open.

**Where H1 is reported not to hold.** The paper states VERBATIM that for two of
the five parameter triples in its Example 2, the condition underlying its
Heuristic-1-based complexity estimate is **not** satisfied, and names a
fallback: *"but for (4608, 13, 96) and (6688, 13, 128) it is not (then, it would
still be possible to give a complexity estimate, using Lemma 5 instead of
Heuristic 1)."* It also reports, VERBATIM, at a later point: *"What happens? It
turns out the conditions in Heuristic 1 are not satisfied"*.

**This is the object a heuristic-validation experiment could test.** It is
stated, numbered, falsifiable, and comes with the paper's own experimental
protocol (sample random [n,k]_q codes, compute def(φ_r) / graded Betti numbers,
check the predicted vanishing). No such experiment is designed here — BATCH-001
designs none.

### EF1 — "Experimental fact 1"

> **Experimental fact 1.** Let C be a [n, k]_q-code of regularity 2, with minimum
> distance d = dmin(C) and dual minimum distance d⊥ = dmin(C⊥).
> 1. For all r ≥ d⊥ we have β_{r−2,r}(C) > 0. Moreover if d⊥ ≤ k(k+1)/n we have
>    β_{d⊥−2,d⊥}(C) ≥ A_{d⊥}(C⊥)/(q−1) (and there are numerous examples of C
>    where this inequality is an equality).
> 2. Dually, for all r ≤ k + 1 − d we have β_{r−1,r}(C) > 0. Moreover if
>    k + 1 − d ≥ k(k+1)/n […] there are numerous examples of C where this
>    inequality is an equality).

**[EXTRACTION-DAMAGED]** on the displayed inequalities (same `(cid:NN)` and
fraction-flattening problem). Prose is clean.
**Evidence offered:** empirical — it is labelled "Experimental fact", and the
paper points to Supplementary Figures 11–14. **Flagged unproven:** yes, by its
label. Verified in worked examples the paper gives (e.g. VERBATIM: *"As d, d⊥ ≥
7, Experimental fact 1 is trivially verified"* for the binary Golay code).

### EF2 — "Experimental fact 2"

> **Experimental fact 2.** Conversely, for a random code C among codes of given
> parameters [n, k, d, d⊥]_q, the probability that def(φ_r) = 0 tends quickly to
> 1 as r ≪ min( k(k+1)/n , k + 1 − d ) and as r ≫ max( ⌊k(k+1)/n⌋ , k + 1 − d ).

**[EXTRACTION-DAMAGED]** — the two displayed bounds are heavily interleaved in
the extraction and the min/max association above is a **reconstruction from
extraction order**. Do not quote the bounds.
**Evidence offered:** empirical.
**Flagged unproven:** yes, and the paper additionally records a **failure case**,
VERBATIM: *"On the other hand, Experimental fact 2 is not verified, but this only
illustrates the fact that the Golay code is certainly not representative of
random codes. Indeed it has a lot of algebraic structure, which explains it
admitting special syzygies."*

### EF3 — "Experimental fact 3"

> **Experimental fact 3.** Let C be a dual alternant code. Then for all s we have
> rmax(C_s) ≥ rmax(C) − s.    (102)

Clean extraction. **Evidence offered:** empirical.
**Flagged unproven:** yes, and the paper explicitly reports counterexamples,
VERBATIM: *"It would be tempting to conjecture that (102) holds for all codes,
but it turns out that one can find counterexamples. However, these
counterexamples are quite rare. So maybe an interesting problem instead should
be to give criteria for (102) to hold."*

### EF4 — "Experimental fact 4"

> **Experimental fact 4.** Let T = Alt⊥ or Gop_{irr,⊥} be a type of codes, namely,
> either dual alternant codes, or dual Goppa codes with irreducible Goppa
> polynomial. Let q be a field cardinality, and t ≥ 3 an integer.
> 1. For all m large enough, rmax(C) = r*_{T,q,t}   (103)
>    is the same for generic proper C ∈ T_{q,m,q^m,t}, i.e. it generically does
>    not depend on m nor on the choice of C, but only on T, q, t.
> 2. For all m, for all n ≤ q^m, for generic proper C ∈ T_{q,m,n,t}, and for all
>    s ≤ r* − 2, if r* − s > max( (k−s)(k−s+1)/(n−s) , … )

**[EXTRACTION-DAMAGED]** on part 2, which is truncated mid-expression in the
extraction. Part 1 is clean.
**Evidence offered:** empirical.
**Flagged unproven:** yes by label, and the paper adds a scope caveat VERBATIM:
*"(for Goppa codes the author only tested the irreducible case, but the result is
likely to generalize)"*.

### Count for `iacr:2024/1193`

**1 numbered Heuristic + 4 numbered Experimental facts = 5 unproven inputs, all
numbered by the paper itself.** The executor invented no numbering.

---

## 3. `arXiv:2304.14757` — Bardet, Mora, Tillich (KN-LIT-4c8135)

**Full text obtained.** Source C02, sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`.
**Coverage is PARTIAL and clearly labelled as such**: this is secondary target 2
and it was enumerated by grep over the extracted text, not by a full read. The
list below is the set of numbered unproven inputs the grep surfaced; **it is not
certified complete.**

The paper's own summary of its epistemic position, VERBATIM:

> By using certain heuristics that we confirmed experimentally we are able to
> prove that the Gröbner basis computation takes polynomial time and give a
> complete algebraic explanation of each step of the computation.

Note the construction the transcription must preserve: "**By using certain
heuristics** … **we are able to prove**". The polynomial-time claim is
conditional on heuristics; the paper says so in the same sentence.

### A1 — "Conjecture 18" (paper's number)

> **Conjecture 18.** Let A_r(x, y) be a random alternant code over F_q, such that
> r ≥ q + 1 and (A_r(x,y)^⊥)^{*2} is not the full code. Let C := (Sh_i(A_r(x,y)))^⊥
> and D := Sh_i( (A_r(x,y)^⊥)^{*2} ), for an arbitrary position i. Then, we expect
> that Cond(C, D) = A_{r−1}(x… )

**[EXTRACTION-DAMAGED]** — the conclusion is truncated mid-expression and the
superscript/star-product markup is flattened. **The conclusion of Conjecture 18
is NOT transcribed and may not be quoted.**
**Evidence offered:** yes, experimental, VERBATIM: *"However, if x and y are
sampled at random, we never met a case in our experiments where equality does not
hold. This leads us to state the following conjecture."*
**Flagged unproven:** yes — it is called a Conjecture, and the paper reports its
own counterexamples, VERBATIM: *"It is however possible to build artificial
examples where equality does not hold. Notably, we also found that the subfamily
of Goppa codes does not meet this property either."*

### A2 — "Heuristic 23" (paper's number) — the Goppa carve-out

Introduced by the section VERBATIM: *"3.2. What is wrong with Goppa codes?
Before moving to the second part of the attack, we make a short digression on how
the arguments explained so far (do not) apply to the Goppa case. The discussion
below does not represent a proof that computing a filtration is impossible for
Goppa codes, but rather an intuition about what hampers it. Goppa codes behave
differently from random alternant codes and provide counterexamples to Heuristic
18. The latter should be replaced by"*

> **Heuristic 23.** Let G(x, Γ) := A_r(x, y) be a random Goppa code of degree r,
> with r ≥ q − 1 and (G(x,Γ)^⊥)^{*2} being different from the full code. Choose an
> arbitrary code position i and let C := (Sh_i(G(x,Γ)))^⊥ and D := Sh_i(
> (A_r(x,y)^⊥)^{*2} ) […] with high probability,

**[EXTRACTION-DAMAGED]** — conclusion truncated. Not transcribed.
**Note a discrepancy the extraction surfaces and this transcription does not
resolve:** the surrounding prose refers to "**Heuristic** 18" while the numbered
statement retrieved at that number is labelled "**Conjecture** 18". Either the
paper is inconsistent, or the extraction dropped a duplicate label, or the
version served differs. **Recorded as an open discrepancy, not repaired.**
**Flagged unproven:** yes; explicitly *"does not represent a proof"*.

### A3 — "Assumption 28 (Random alternant code)"

> **Assumption 28 (Random alternant code).** We assume that A_3(x, y) is in
> standard form, and that its dimension satisfies k = n − rm = n − 3m.

Clean extraction. Introduced VERBATIM by *"These results lead us to make the
following assumptions, given for the case r = 3 of interest, that will be
satisfied for a random alternant code."*

### A4 — "Assumption 29 (High rate regime)"

> **Assumption 29 (High rate regime).** If q ≥ 3, we assume that
> Rank(S) = Rank(S′) = (3m choose 2) − m ≤ k.

**[EXTRACTION-DAMAGED]** on the binomial: the extraction renders it as a
detached `3m / 2` stack inside `(cid:16)…(cid:17)` delimiters and the reading
"(3m choose 2)" is a **reconstruction**. Do not quote the formula.

### A5 — "Assumption 30 (High rate regime)"

> **Assumption 30 (High rate regime).** If q = 2, we assume that
> Rank(S) = Rank(S′) = (3m choose 2) − 3m ≤ k.

**[EXTRACTION-DAMAGED]** — same reconstruction caveat. Preceded VERBATIM by
*"Note that for q = 2, the rank is smaller:"*.

### A6 — an unnumbered heuristic step, numbered HERE BY THE EXECUTOR

The paper contains at least one heuristic step it does not number. **The label
`A6` is the executor's, not the paper's, and is flagged as such per the task's
instruction.** VERBATIM: *"This step is heuristic, and verified experimentally:
the resulting system…"* (sentence truncated by the extraction —
**[EXTRACTION-DAMAGED]**; recorded only to establish that an unnumbered
heuristic step exists at that location).

The paper also relays a heuristic it attributes to prior work, VERBATIM:
*"However, in the high rate regime, [FGO`13] proposed an algebraic heuristic
explaining why there is a tighter upper bound. This heuristic was confirmed by
…"*. **Attributed to [FGO`13], not to this paper.** Not enumerated as one of this
paper's own.

### Count for `arXiv:2304.14757`

**5 numbered unproven inputs numbered by the paper (Conjecture 18, Heuristic 23,
Assumptions 28, 29, 30) + at least 1 unnumbered heuristic step numbered here by
the executor (A6). NOT CERTIFIED COMPLETE** — enumeration was by targeted search,
not a full read.

---

## 4. `iacr:2025/531` (KN-LIT-7ee1a9)

**Heuristics: NOT OBTAINED.** Abstract only (D03); full text blocked by a
proof-of-work bot interstitial at `inria.hal.science` (D01, D02), not
circumvented. The abstract states no heuristic and no assumption. **Nothing is
enumerated.**

---

## 5. Totals

| Source | Full text | Heuristics/assumptions numbered by the source | Numbered by the executor | Enumeration certified complete |
|---|---|---|---|---|
| `iacr:2026/1232` (KN-LIT-7c4620) — **PRIMARY** | **no** | **0 obtained** | **0** | n/a — nothing read |
| `iacr:2024/1193` (KN-LIT-71d1a0) | yes | 5 (Heuristic 1; Experimental facts 1–4) | 0 | yes for numbered items in this version |
| `arXiv:2304.14757` (KN-LIT-4c8135) | yes | 5 (Conjecture 18; Heuristic 23; Assumptions 28–30) | 1 (`A6`) | **no** — targeted search only |
| `iacr:2025/531` (KN-LIT-7ee1a9) | no | **0 obtained** | 0 | n/a — nothing read |

**The primary target's heuristic count is not zero. It is UNKNOWN.** Those are
different statements and this document does not let them merge.
