# Falsification review — TASK-20260728-013

Adversarial review of the BATCH-003 producer packages committed at
`b978f883d5b2`. Companion to `red_team_report.yaml` in this directory; that
file is the authoritative record and this note shows the working.

Fresh session, no shared lineage with TASK-20260728-010, -011, -012 or any
BATCH-002 session. Model independence **not achieved and not claimed** — fifth
consecutive session on one self-reported `claude-opus-5` identity; the adapter
refuses `glm-5.2` because the zai binding's effort ceiling is `high` against a
policy requiring `xhigh`, and `$ZAI_API_KEY` is unset. Relayed from the queue,
not re-verified. Zero curve compute, zero web retrieval, read-only shell.

## 0. Snapshot verification (gate R7)

| check | result |
|---|---|
| `b978f883d5b2` reachable from HEAD `4f657aca` | yes |
| parent = `66692226` as receipted | yes |
| changed-path count | **5, exactly the five declared** |
| SHA-256 of all five, recomputed | **all five match the receipt** |

The changed-path check is the one main's `GOAL-ECDLP-001` BATCH-010 failed by
declaring 7 and committing 195. It passes here.

Not verified: `pushed_to_origin`, `ran_alone`, and the BATCH-002 artifacts the
producers cite as their baseline. Where I rely on a BATCH-002 figure I mark it
relayed.

## 1. Gate R2 — `KN-TECH-056`: **ADMIT**

**`TASK-20260728-014` commits 8 paths.** No queue amendment on this ground.

The claim I was asked to spot-check is that every quotation carries a locator
the author verified rather than relayed. I did not spot-check it — I checked
**all thirteen** cited lines (1, 11, 13, 19, 23, 25, 31, 33, 35, 37, 39, 41,
43) of `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` myself. Every quotation
matches its cited line verbatim. Two are worth naming because they are where a
relayed locator would have shown:

- The van Oorschot–Wiener interpolation sits in the **tail** of a
  ~950-character line 39 and is quoted correctly, including
  `√(N^3/w) = p^{1/2+o(1)}/w^{1/2}`.
- The unconditional tier's `at polynomial memory` qualifier — the one clause
  that could plausibly have been an unsourced addition — is genuinely sourced,
  to line 39's *"the classic p^{1/2+o(1)} algorithms with polynomial memory like
  [21]"*.

The Corollary 1.2 quotation elides only parenthetical problem
cross-references; the elision changes no content.

Other R2 checks: `KN-TECH-029` unmodified (last touched by `8bdb20c4`,
`knowledge/` clean); Heuristic 1 conditionality inline in front matter, body and
applicability limits; the superpolynomial `o(1)` and memory-equals-time carried
inline; no exponent asserted beyond what is sourced; scheme scope quoted,
attributed to the source, and marked not-to-be-widened.

Two **non-blocking** admit conditions:

- **AC1.** I checked the supersession convention rather than assuming it:
  `knowledge/` contains **7655** `superseded_by: null` and **zero** non-null.
  So the back-pointer is never filled, filling `KN-TECH-029`'s would be an edit
  to an immutable record, and the 8-path set is right and must not grow to 9.
  The cost is that a reader landing on `KN-TECH-029` learns nothing — which is
  exactly what the regenerated `knowledge/INDEX.md`, already in the 8-path set,
  must fix by rendering the `supersedes` edge in both directions.
- **AC2.** The front-matter `complexity` field re-transmits `F_p: Otilde(p^{1/4})`
  at `relayed_from_abstract`. The same producer's O5 shows that figure is not
  merely relayed but **contested across retrievals** — one of the two abstracts
  contains no `p^{1/4}` at all. The label is present and the body records the
  instability at length, so this does not block; append
  `contested across retrievals, see RC4` to that one field.

## 2. Lemma 4′(b) — the replacement argument is **SOUND**

I checked the argument, not merely that one exists.

The refutation is right: with `y = h(u) = (b(u), i(u))`, the colliding endpoint
`g(y)` is the walk endpoint from `E_{b(u)}`, hence a *function* of the side bit.
Independence is the wrong word, and a conclusion reached through a false step is
unproven until someone supplies a valid one.

The replacement — condition on `(β,β')`, get `(1±o(1))/n_V` identically for all
four configurations, let Bayes return the prior — is **valid, and is a different
argument rather than a restatement**. Uniformity across conditionings makes the
posterior equal the prior without needing independence. Three checks:

1. **The L² input.** With `‖e‖₂ ≤ poly(d)·ℓ^{-d/2}` at `d = (1+ε)log_ℓ p`,
   `|⟨e_β,e_{β'}⟩| ≤ polylog·p^{-(1+ε)} = o(1/n_V)`, since `p^ε` beats polylog
   for fixed `ε > 0`. Holds.
2. **The diagonal, where I expected it to break.** At `β = β'` both walks start
   from the *same* curve, so Cauchy–Schwarz is unavailable and the quantity is
   `Σ_v μ_β(v)² = 1/n_V + ‖e_β‖₂²`. The same Ramanujan bound gives
   `‖e‖₂² = o(1/n_V)`, so the diagonal obeys the same `(1±o(1))/n_V`. **The
   uniformity claim survives the case with the most reason to fail.**
3. **The prior is 1/2** under the PRF model provided `u ≠ u'`, and `u = u'`
   would force `y = y'`. The side condition is correctly discharged.

The threshold table is also right, including the row that matters: at
`ρ = p^{-δ}` one gets `T = Θ(p^{1/2+δ}/√w)`, explicitly `w`-dependent, so
memory-independence falls exactly when `ρ` is polynomially small.
`ρ = 1/2 - o(1)` clears it with polynomial margin.

**So the memory-independence conclusion of the BATCH-002 erratum STANDS** — on
the argument supplied in `-011` and re-derived here, not on the erratum's own.

Two things the discharge does not say about its own repair:

- **O6 (the one that changes a label).** The replacement consumes the **L²**
  bound — the same substitution the discharge's own O1 shows is *not licensed by
  H1′ as numbered*. So memory-independence now rests on a statement absent from
  the numbered heuristic inventory, while RC8's `blocks` field reads `Nothing`.
  RC8 is a **precondition of the conclusion this discharge preserves**, not a
  cosmetic restatement.
- **O7.** Trail heads are handled by assertion (`uniform start`), not
  derivation. A 1/L fraction cannot move `ρ` off `Θ(1)`, so nonfatal — but it is
  the one step I could not verify from what is written, and it belongs in RC10.

I independently re-derived O1's counterexample (TV `p^{-1/4}`, collision
probability `Θ(p^{-1/2})`, inflation `Θ(p^{1/2})`) — **correct**. And O2's
arithmetic: `√S·‖e‖₂ = polylog·p^{-1/4-ε/2}` must be `o(p^{-1/2})`, needing
`ε > 1/2` — **correct**, and no exponent moves since `d` stays `Θ(log p)`.

D1: re-derived, `C = Θ(p^{1+2ε})` against `M = Θ(p^{1+ε})`, so `C = ω(M)`.
Confirmed — and I endorse the discharge's *self-downgrade* of it to bookkeeping.
A review that demotes its predecessor's headline disagreement and then names the
item nobody had checked as the real load-bearing one is behaving correctly.

## 3. S1 and the two derived rejections — all three hold

**S1 holds** as a conditional transfer lemma, and the one-for-one claim is real.
`X = B^{1/2}p^{β/2}` gives `X² = B·p^β`; at the choice making `B = p^{o(1)}` and
`u^u = p^{o(1)}` simultaneously, per-attempt × inverse-success `= p^{β+o(1)}`,
reproducing the headline at `β = 1/3`. I looked for a second channel and found
none: the inverse-success factor depends on `β` only through `u` and moves
*favourably* as `β` falls; the modular-polynomial cost `B^{O(1)}` is
`β`-independent; there is no additive `p^{Ω(1)}` term to dominate a smaller
table. The screen is decisive rather than a list, as claimed.

**C2's rejection holds.** `D_K ≥ D_1/K` is correct (compose `ψ∘φ`, apply
minimality; it survives the cyclicity worry since factoring out a non-cyclic
part only lowers degree), and `Θ(K²)·B·D_K ≥ Θ(K)·B·D_1` raises the exponent to
`1/3+δ`. I also tested the *sharing* evasion the artifact lists as its own
falsification condition: building one enlarged list from `E^{(p)}` does not
escape, because the union of radius-`X` neighbourhoods of `T_K` sits inside a
radius-`K·X` neighbourhood of size `Θ((KX)²)` — the same `K²X²`. Robust, and
correctly scoped to compose-with-a-small-isogeny families.

**C4's degeneration holds.** For `E` with a model over `F_p`, `E^{(p)} = E`, the
minimal isogeny has degree 1, and the endomorphism returned is `π ∈ Z[π]`, known
a priori. It is a genuine structural explanation of the source's own line-35
CSIDH line, correctly flagged as very likely folklore, with the twist control
named. The repaired transfer is screened `UNLIKELY` on an estimate labelled
unverified three times.

**S3** re-derives correctly (`p/|W| + |W|^{1/2}`, minimum `p^{1/3}` at
`|W| = p^{2/3}`; both checkpoints reproduce, including `p^{1/4}` for
`F_p`-rational input). Its escape from the L1 ceiling is real and, if anything,
undersold: `p^{1/3}(log p)^{O(1)}` dominates `p^{1/3+o(1)}` with superpolynomial
`o(1)` at every realisable `p`.

### C3's blocker labelling — holds in prose, **not in the greppable field**

The label *does* hold where the blocker is described (`to this screener's
knowledge`, `THIS BELIEF IS NOT VERIFIED HERE`, and the note that the web was
not searched for this candidate). But the field a reader greps is
`screen_verdict`, and it reads `LIVE_BUT_BLOCKED_ON_A_KNOWN_HARD_SUBPROBLEM` —
the token `KNOWN_HARD` asserts a literature fact the artifact elsewhere disclaims
(**O9**).

**And yes, something downstream leans on it.** `recommendation.rationale` demotes
C3 below C1 because its test has *"a likely negative answer"*, and
`new_attack_mechanism_justification` repeats it. The **flag is robust** —
C3 can at best *tie* the conditional tier and a tie is not a detection — but the
**ranking is not**: strike that clause and C1-over-C3 rests only on retrieval
size, while C3 is the only candidate escaping the L1 ceiling.

### O8 — the sharpest objection, and the cheapest control

The screen invokes Eichler/Hurwitz class-number sums for **C4** and never turns
the same machinery on **C1**, where it points *against* the candidate. Sketch,
zero compute: compose a degree-`m` isogeny `E → E^{(p)}` with the dual of
Frobenius to get an endomorphism of degree `mp`; requiring the count of pairs
`(E, α)` with `deg α ≤ N` to cover all `Θ(p)` supersingular curves gives
`N ~ p^{4/3}`, i.e. `β ~ 1/3`. **On the counting heuristic, `β = 1/3` is
essentially tight** — C1's own falsification condition 1, arriving from the
artifact's own toolkit rather than from an unobtained reference [4].

I do **not** conclude C1 is dead: this is a counting heuristic on a *minimised*
structured quantity, precisely the random-model-transfer failure mode that cuts
both ways. It is a reason to run the sum (RC11) before repeating a retrieval
that has now failed twice. Note that O8 and O9 push the same direction: the
C1-over-C3 ordering is supported by an unrun count disfavouring C1 and an
unverified recollection disfavouring C3.

**O11**, available only to a reviewer reading both packages: S3 charges
`p^{1+o(1)}/|W|` to *reject-sample* into `W`. A mechanism that **steers** does
not pay that — and the sibling task's own RC4 retrieval quotes Delfs–Galbraith
offering exactly that alternative (a DFS through all short paths from `E0`). The
producers ran concurrently, so neither could see it.

## 4. Sourcing (gate R4)

Honestly recorded, with one word to fix. No `F_p` confidence label was upgraded;
failed fetches are recorded as failures with verbatim error strings; the Haifa
PDF was opened, identified as a 2013 student slide deck, and **discarded rather
than cited**; a search-engine summary was refused as not-the-paper; a fetch
summariser's `O(p^{1/4})` *inference* was identified as such and not adopted.
That is the discipline this campaign was in debt over, applied correctly — and
applied by a session that had a finding *contradicting* the artifact it was
reviewing and still changed no label.

**O10.** RC4's finding says *the published* descent is one long walk. What was
retrieved was ar5iv's rendering of arXiv 1310.7789 — and the **same report's O5**
shows the arXiv and DCC objects differ enough that their abstracts disagree on
whether `p^{1/4}` appears at all. Sound for the arXiv version, unverified for the
published one. One word.

**O5 scoping.** Correctly scoped, and **no label needs to drop**:
`relayed_from_abstract` is still accurate. But *relayed* and *contested* are
different defects, and O5 establishes the second. Add
`contested_across_retrievals` alongside the existing label wherever the `F_p`
figure is quoted. I explicitly do **not** recommend downgrading the `F_p`
ranking — the direction of the discrepancy is unknown and the likeliest
explanation (an arXiv version difference) is itself unverified. Absence of a
stable source is not evidence the figure is wrong.

## 5. `new_attack_mechanism_detected` — my own verdict: **false**

Reached independently, and I do not disagree with the three prior sessions.
Reasoning that does not reuse theirs: C2 and C4 are rejected on the exponent by
derivations I re-derived myself; C1 cannot beat anything until an ingredient
exists that this program failed to locate, and O8 gives a positive reason to
expect it does not; C3 at best *ties* the conditional tier by its own floor
lemma. A tie is not a detection. Separately, the discharge's only preserved
conclusion is memory-independence — a theorem that a resource does not help is a
negative result about attacks, not an attack.

Neither package overclaims. No conditional written as unconditional; no
per-attempt cost quoted as total expected cost anywhere in either artifact.
**No BATCH-003 output can satisfy a GOAL-SSI-001 completion criterion.**

## 6. What I did not reach inside 420 s

- **The most important limitation:** I did not read the BATCH-002 artifacts.
  My checks of Lemma 4′(b), D1, O1 and O2 were made against the **discharge's
  restatement** of those steps. If the discharge misquoted the erratum, my
  agreement with it would not catch that.
- Erratum sections 2.5–2.7, 4, 7; Lemma 5′, Lemma 7′; the MITM `p^{2/3}` floor.
- O8's Eichler/Hurwitz sum to completion — a sketch and a direction only; RC11
  exists to do it properly.
- Any web retrieval. I confirmed neither the RC4 quotations nor the RC5
  failures independently; I assessed only whether they are honestly recorded.
- `mechanism_hunt_note.md` and `independent_check_note.md` in full — S1/S2/S3
  were checked against the YAML statements plus my own re-derivation, so a
  defect living only in a companion note's algebra would not be caught.
- `[35]`, the reductions under Corollary 1.2. **No session in this program has
  verified them**; C1's cascades-for-free claim is inherited, not checked.
- No adapter probe; the model-independence refusal is relayed from the queue.

## 7. Next concrete action

`TASK-20260728-014` commits **8 paths**, and while staging should ensure the
regenerated `knowledge/INDEX.md` renders the `supersedes` edge in both
directions (AC1). The highest-value research action after that is **RC11** —
run O8's count on paper before re-attempting the reference [4] retrieval. If it
lands at `1/3`, S1 converts from a lever into a barrier capping the whole
architecture at `p^{1/3+o(1)}`, which the screen itself calls the valuable
outcome.

Nothing in this review is a cryptanalytic result.
