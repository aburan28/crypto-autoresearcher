---
id: KN-FIND-617d78
type: internal_finding
title: "The K-rational fibre of a quasi-subfield relaxation is capped by the degree of one difference polynomial: N_K(X^{p^{n'}} - lambda) <= max(d^{q+1}, p^{n'-r}), hence beta > 1/2 for every completely splitting L with n' < n not dividing n — derivation tier, attacked at six joints by three independent sessions and not broken"
tags: [qsp, quasi-subfield, quasi-subfield-polynomial, ecdlp, index-calculus, factor-base, frobenius, difference-polynomial, twisted-iterates, beta-quality, complete-splitting, degree-bound, ecc2k-130, characteristic-two, odd-characteristic, negative-result, derivation-tier, scoped, review-breakthrough, blind-rederivation, proves-too-much]
confidence: derivation_attacked_at_six_named_joints_by_three_independent_sessions_and_not_broken_plus_exhaustive_certificate_bearing_enumeration_at_toy_n_and_exact_counts_at_n_131
evidence_level: derivation_plus_exhaustive_enumeration_toy_scale_plus_exact_counts_at_the_131_bit_target_field
source_refs: [KN-LIT-0a321c, KN-LIT-4fe9d2, KN-LIT-096, KN-OPEN-ac409f, KN-TECH-54c38e]
internal_refs: [EV-QSP-a6aa4b, DEC-20260917-793ae2, DEC-20260917-ea9dd2, EXP-QSP-33b442, H-QSP-645a07, H-QSP-5540d7, RQ-QSP-f9bbdb, TASK-20260917-43701b]
internal_refs_note: "internal_refs carries ONLY ids tools/validate_ledger.py can resolve, which is ctx.ids (the six LEDGER_DIRS at validate_ledger.py:160 plus experiments) and ctx.knowledge. Five further records this finding rests on are NOT resolvable there and are listed under unregistered_refs instead; every one of them is cited in the body with what it contributes. Populating a machine-checked pointer field with ids the field cannot hold buys nothing and costs a red error per id."
unregistered_refs:
  - id: CORR-20260917-8b80cc
    why_unregistered: "ledger/corrections/ is not in LEDGER_DIRS (validate_ledger.py:160), so no CORR-* is ever registered as a record."
    contributes: "the validity gate for the run set; the ratification of AMD-20260917-001 with the scope limit that leaves 10 of 65 complete splitters on I2 alone; the five disclosed S0 schema errors; and the 'at least four splitters at equality' inference this round corrected to three."
  - id: CORR-20260916-8d0b81
    why_unregistered: "same: corrections are not a registered record type."
    contributes: "the F_p-coefficient slice of (A), verified by a Coordinator session BEFORE the experiment was designed, and the inversion of RQ-QSP-f9bbdb's premise (4)."
  - id: TASK-20260917-34b637
    why_unregistered: "no handoff card exists: the three reviewers were dispatched from the joint assignments in TASK-20260917-43701b's review_plan rather than from their own cards. The absence is accurate history and is NOT repaired by writing cards after the fact."
    contributes: "J1/J3/J5; the p != 2 sweep; the 65-row recomputation from (n, n', d) alone; the exactly-three equality count; the 546-versus-732 certificate accounting."
  - id: TASK-20260917-52b4e6
    why_unregistered: "same as above."
    contributes: "J2/J4/J6 and the proves-too-much control; the (q+1) | n degeneracy criterion; fault injection; 36 independent n = 131 determinations; the kappa direction finding."
  - id: TASK-20260917-5fa7d5
    why_unregistered: "same as above."
    contributes: "the blind re-derivation of the n = 131 quantity and its null model."
unregistered_refs_note: "Their durable pointers are PATHS, not ids: the three reviewer reports are in review_refs and proof_refs above, and both CORR records are at ledger/corrections/<id>.yaml. That a finding cannot machine-reference a correction record is a gap in the validator rather than in this entry — corrections are exactly what a finding should be able to cite — and it is routed as a tooling item in DEC-20260917-ea9dd2 NA-E3."
proof_status: derivation
proof_refs:
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j6_kappa_out.txt
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/scratch/j2_structural.py
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/out/j3_scope_witness.txt
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/out/j5_census_enum.txt
  - experiments/EXP-QSP-33b442/analysis.md
certificate_refs:
  - experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S3/certificates/
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/out/roots_lambda_132.txt
review_refs:
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/report.md
added: '2026-09-17'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: `toy` for the candidate mass, with exact counts at a 131-bit
field declared separately — exactly as `EV-QSP-a6aa4b` declares them.** This
entry may not claim more than that evidence record's scoped claim, and it does
not. Read the four paragraphs below before using anything further down.

**Nothing here touches any deployed curve.** No curve, no group and no point
was constructed anywhere in `EXP-QSP-33b442` or in any review artifact cited
here. **No attack exponent moves.** rho on ECC2K-130 stands at `2^60.9`
([[KN-LIT-096]]), untouched.

**The general statement is a DERIVATION, not an enumeration.** The bound is
claimed for every `p`, `n`, `n'` and every non-degenerate `lambda`. That
generality rests on a three-line argument which **three independent sessions
attacked at six named joints and did not break** — not on the numbers. The
numbers could only have refuted it, and did not, across roughly 340 000
candidates from two implementations with no shared lineage. Where measurement
stops is stated in §5 and is not negotiable.

**`RQ-QSP-f9bbdb` decision target (a) — an existence result at `n' = 33` — is
answered NEGATIVELY ON THE 732 ENUMERATED CANDIDATES AND ON NOTHING ELSE.** A
complete splitter there would need `N = 2^33`; the largest observed is 132.

**This entry does not promote the closure reading.** `H-QSP-5540d7` (E) —
"no quasi-subfield factor base beats generic algorithms" — is **not** part of
this finding. Its stated reason was refuted in the same review round and the
open question it leaves is [[KN-OPEN-ac409f]]. What is promoted here is the
unconditional bound and its corollary, and nothing else.

## 1. The finding

Let `K = F_{p^n}`, let `lambda` in `K[X]` have degree `d >= 1`, set
`L = X^{p^{n'}} - lambda(X)`, and write `n = q n' + r` with `0 <= r < n'`. Let
`N_K(L)` be the number of **distinct** roots of `L` in `K` — the size of the
factor base the quasi-subfield relaxation of [[KN-LIT-0a321c]] §3.1 proposes.
Define the twisted iterates `Lambda_1 = lambda`,
`Lambda_{k+1} = Lambda_k^{(n')} o lambda`, where `f^{(k)}` raises every
coefficient of `f` to the `p^k`-th power.

> **(A) The twisted injection bound.** Every `K`-root of `L` is a root of the
> single **difference polynomial**
> `D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}}`, and therefore
>
> ```
>     N_K(L)  <=  deg D  <=  max(d^{q+1}, p^{n'-r})        whenever D != 0.
> ```

> **(B) The beta corollary.** If `n'` does not divide `n`, `r >= 1`, and `L`
> splits completely in `K` as a set (`N_K(L) = p^{n'}`), then `n' < n` and,
> with `l = log_p d` and `beta := l n / n'^2`,
>
> ```
>     (q+1) l  >=  n'        and        beta  >=  n / (n + n' - r)  >  1/2.
> ```

The mechanism in one sentence: run the chain identity of [[KN-LIT-0a321c]]
Appendix A.2 **one step further than the paper does**, to `k = q + 1`, where the
identity `(q+1) n' = n + (n' - r)` lets `x^{p^n} = x` collapse the left-hand side
to `x^{p^{n'-r}}` — which is *tiny* exactly when `r` is close to `n'`, the regime
the paper itself identified as the attacker's best case. Then compare degrees.
The additions to the published argument are the coefficient twist (so `lambda`
may have coefficients in `K`, not only in `F_p`) and that one extra step.

**Why it matters.** Lemma 4.1 of [[KN-LIT-0a321c]] gives `q l + r >= n'`, whose
strength *degrades* as `n mod n'` shrinks; §5 of that paper asks whether the
`n mod n'` term can be removed and observes that removing it would show the
approach cannot beat generic algorithms. (B) is that removal — by a
complementary bound rather than by sharpening Lemma 4.1. The two are
incomparable ((A) is stronger iff `l < r`) and combine to
`q l + min(l, r) >= n'`.

**`n' < n` is derived, not assumed, and needs two conjuncts.** (i) Cardinality:
`N_K(L)` counts distinct roots *in* `K`, so `N_K(L) <= |K| = p^n`, and the
antecedent `N_K(L) = p^{n'}` forces `n' <= n`. (ii) Non-divisibility: `n' = n`
divides `n`, which (B) excludes by hypothesis. **Cardinality alone is not
enough**: at `n' = n` with `lambda = X`, `L = X^{p^n} - X` splits completely,
`q = 1`, `r = 0`, and `n/(n + n' - r) = 1/2` *exactly*, so the strict inequality
fails at equality. `H-QSP-5540d7` stated neither conjunct; `H-QSP-645a07`
states both.

## 2. What was measured, and by whom

| arm | scope | result |
|---|---|---|
| Producer, `EXP-QSP-33b442` (p = 2) | 1260 exhaustive toy + 1200 seeded K-coefficient + 42 244 sweep + 732 at n = 131 = **45 436** | **0** candidates with `N > max(d^{q+1}, p^{n'-r})` |
| Independent reviewer `TASK-20260917-34b637`, written against the **statement** at arbitrary `p`, never opening the producer's implementation | **291 997** deduplicated (machine roll-up 292 105) at `p` in {2,3,5,7} + 2400 odd-`p` K-coefficient draws | **0** violations; 0 with `deg D` above the bound; 0 where the `K`-root set of `L` fails to divide `D`; largest `N`/bound anywhere exactly **1.0** |
| Red team `TASK-20260917-52b4e6` | 331 664 `lambda` searched for `D = 0` outside the claimed shape; 1 324 468 characteristic-`p` compositions searched for a counterexample to `f o g = Y^m ⇒ g = cY^e + b` | **0** found in each |
| Complete splitters, recomputed from `(n, n', d)` **alone** with exact rationals, trusting no instrument | all **65** archived rows | 0 disagreements on any column; `min(beta − exact) = 0` exactly; `min(beta − conservative) = 7/32` |

**The bound is attained, and now at odd characteristic too.** Ratio exactly 1 at
`(7,3)` by `X^2+X` and `X^2+X+1` (`N = 8`) and at `(7,4)` by `X^4+X^2+X`
(`N = 16`) at `p = 2`; and — new in the review round, where nothing in the
experiment touches `p != 2` — at `(p,n,n') = (3,8,3)` with `d = 2`
(`N = 8 = max(8,3)`) and `(5,5,3)` with `d = 2` (`N = 5 = max(4,5)`). **Exactly
three** `p = 2` splitters attain equality, which corrects the execution report's
"two" and overturns `CORR-20260917-8b80cc`'s inference of "at least four".

**(A) does visible exclusion work, not only passive satisfaction.** At `(7,4)`
with `d = 3` the bound is `max(9,2) = 9 < 16 = 2^{n'}`, so (A) **forbids** a
complete splitter there — and none is observed, while three of the 356
near-complete rows sit strictly below the exact corollary and fail to be `F2`
events only because they are not complete splitters.

## 3. At the target field, on two lineages with no shared code

Over `K = F_2[z]/(z^131 + z^13 + z^2 + z + 1)` — the ECC2K-130 field of
`RQ-QSP-f9bbdb` — for every non-linearized `lambda` in `F_2[X]` of exact degree
3..7 (244 per cell) at `n'` in {33, 44, 66}:

- **max `N` = 132** at `n' = 33`, histogram `{0:62, 1:118, 2:60, 132:4}`,
  four attaining `lambda` each with Frobenius orbit sizes `[1, 131]`;
  **max `N` = 2** at `n' = 44` and at `n' = 66`.
- A complete splitter at those cells would need `2^33` / `2^44` / `2^66`. The
  shortfall at `n' = 33` is **`log2(132) = 7.04` bits against 33, a factor of
  `2^25.96`**.
- `TASK-20260917-5fa7d5` re-derived this **blind** — from the statement of the
  quantity and the parameters alone, having read exactly two repository files,
  run no git command and listed no sibling path — deriving the candidate-set
  size 244 for itself and returning **the same maximum, the same argmax, the
  same histogram and the same orbit sizes**. Its method never materialises `L`
  (`33·4 = 132 = 131 + 1`, so two gcds against a degree-2401 object suffice);
  that instrument is abstracted as [[KN-TECH-54c38e]].
  Under the interpretation rule fixed **before** the round, agreement is
  evidence about the *quantity*, and it is the only evidence at `n = 131` that
  does not pass through the producer's single instrument.

## 4. The controls, including the one that came out against the Coordinator

- **Proves-too-much, both declared known-false families, signature ABSENT on
  each.** FAMILY 1 (`n' | n`, Diem's subfield family, where the conclusion is
  known false): the bound is vacuous on all 3422 triples with `n <= 32`,
  `d <= 29`, and the vacuity is **structural** — `r` enters (A) in exactly one
  place, the exponent of `Y^{p^{n'-r}}`, which at `r = 0` *is* `deg L`. 141
  objects at `r = 0` split completely and the derivation is vacuous on every
  one; of the 288 where it is non-vacuous at `r = 0`, **not one** splits
  completely. FAMILY 2 (the linearized family of Theorem 1 of
  [[KN-LIT-4fe9d2]], `beta >= 3/4` already known): 1032 linearized complete
  splitters at `n <= 40` enumerated by Proposition 2 **alone**, with no
  instrument of the experiment — 0 violations of (B), and **0 objects with
  `3/4 <= beta <` (B)'s bound**, which is precisely the object that would
  satisfy Theorem 1 and refute (B).
- **Forced fixtures on their forced values**: `(64, 8, 32768, 4)` exactly.
- **Fault injection, which overturned the Coordinator's recorded prior in the
  record's favour.** The prior held that a single injected fault leaving the
  agreement matrix clean would show the matrix measures shared code. The
  antecedent does not hold: corrupting `clmul`, which all three instruments
  reach, changed **87 of 120** counts and took the matrix from `(0,0,0)` to
  `(75,73,43)`; single-instrument faults localise (`(92,0,92)` and `(17,17,0)`);
  three faults *designed* to evade the field-polynomial self-check were caught by
  an internal algebraic assertion; and a semantically identical rewrite of
  Euclid as negative control changed nothing. `M2 = 0` is a **measured
  property**, not an artifact of shared code.
- **The null model removes an anomaly instead of explaining it.** Non-`F_2`
  roots arrive only in orbits of size 131, so the expected number of
  orbit-carrying `lambda` is `244/131 = 1.86` against **4 observed**, Poisson
  `P[>=4] = 0.12`; after the involution `lambda(X) -> lambda(X+1)+1`, which
  pairs (132, 251) and (161, 204), there are 2 independent events against 0.93
  expected, `P[>=2] = 0.24`. **The four maximizers are the generic outcome, not
  a signal.** Any later claim treating those four as algebraically distinguished
  lacks evidence, and the producer's `unexpected_observation` about them
  requires no explanation.

## 5. Boundaries — these travel with the finding, not as a footnote

1. **The degeneracy control is VACUOUS BY CONSTRUCTION across all 111 cells.**
   Degeneracy requires `(q+1) | n` (because `n' - r = (q+1)n' - n` identically),
   and every declared cell has `n` prime with `2 <= n' < n`. The instrument
   returned `False` on 45 436 candidates **and could not have returned anything
   else**, so a declared *blocking* control was never exercised inside the
   contract. What supplies the missing measurement is outside it: 26 constructed
   degenerate instances at 26 `(n, n')` pairs plus 164 full-`K` degenerate
   `lambda`, every one attaining `N = p^{n'-j}` exactly and none splitting
   completely. *(The superseded and incorrect reason — that every cell has
   `n' - r` in {1,2} — is false on 56 of the 95 Stage-2 cells and must not be
   repeated.)*
2. **10 of the 65 complete splitters rest on instrument I2 alone**, all at
   `(31, 5, d = 8)` with `deg D = 2 097 152`, excluded from I3 by the ratified
   `AMD-20260917-001`. They are the only 10 of 65 with a single non-null
   instrument. Report this figure as "10 of 65 complete splitters" and **never**
   as "14 of the 356 near-complete candidates" without it. Mitigations that
   reduce but do not remove the exposure: the surviving instrument is the C
   helper `gf2rc`, the one implementation sharing nothing with `qspcore`; their
   `beta` margin of 2.834 is the largest in the table; and I2 ran on all 42 244
   candidates, so the cap cannot have *hidden* a splitter.
3. **720 of the 732 census rows at `n = 131` are single-instrument (98.4 %).**
   Only I3 ran there, checked by a re-verifier that can falsify a listed root and
   **cannot detect a missing one** — and a missed root lowers `N`, which is the
   direction that makes `N <= bound` hold. The 62 rows per cell with `N = 0`
   carry no root verification at all. Twelve affine rows now carry an
   independent linear-algebra determination that agrees exactly; the blind
   re-derivation covers the `n' = 33` cell's *aggregate* quantities and computed
   nothing at `n' = 44` or `n' = 66`.
4. **The census certifies 244 distinct `lambda` examined at three `n'`, not "732
   named polynomials"**, and it is a measure-zero slice: `K`-coefficient
   `lambda` at `n = 131` are **entirely untouched**, and degree is capped at 7.
5. **"Three agreeing instruments" is two, and at `n = 131` it is one.** I1, I2,
   I3 and the root re-verifier all bottom out on the same `clmul`, `deg`,
   `polymod` and `square`; I1 has no primitive of its own. The corrected headline
   is: *"732 exact counts at `n = 131`, 546 of them certificate-bearing, under
   two independent determinations at Stage 1 over a shared primitive base and one
   instrument at `n = 131`."* The frozen contract's own pre-registered sentence
   said "732 certificate-bearing", overstating by **186 rows** (732 claimed
   against 546 that exist).
6. **`p != 2` evidence exists only barely and is a REVIEW artifact**: `p` in
   {3,5,7}, `n <= 13` (p = 3) and `n <= 11` (p = 5,7), `n' <= 8`, degree 2..4.
   Every numerical cell of `EXP-QSP-33b442` is `p = 2`. **The transfer from
   `p = 2` to general `p` is by the derivation and never by measurement.**
7. **No independent replication invocation was spent (PD-6).** What stands in
   its place is structural rather than procedural — Stages 0–3 and every control
   are exhaustive and seed-free, hence deterministic by construction — plus one
   blind re-derivation. They are not the same thing as replication and are not
   reported as such.
8. **Five ledger-schema errors on `RUN-QSP-33b442-S0`** (a stage that ran no
   program) remain standing disclosed debt; none falls on a
   measurement-bearing run (`CORR-20260917-8b80cc`).

## 6. What this forecloses, and what it does not

**Foreclosed, on the tested scope**: looking for a *luckier* `lambda`. The cap
is exactly attained — ratio 1.000 at `(7,3)` at `p = 2` and at `(3,8,3)` and
`(5,5,3)` at odd `p` — so it is not loose, and **0 of roughly 340 000 `lambda`
across two implementations and four characteristics exceeded it**. Any successor
construction must be shown to **raise `deg D`**, not to search harder inside the
same shape. The number to beat at `n = 131`, `n' = 33` is **132 against `2^33`**
(`DEC-20260917-ea9dd2`, design constraint on `IDEA-20260916-a17f43`).

**Not foreclosed — four survivors stand and the QSP line is NOT closed:**

1. `n' | n` (Diem's subfield family; at `n = 131`, only `n'` in {1, 131}).
2. Correspondence shapes of conjugate degree `>= 2` (`IDEA-20260916-a17f43`).
3. Factor bases that are **not** root sets of a single `X^{p^{n'}} - lambda`.
4. **Rational `lambda`**, since the rational extension (D)(ii) of
   `H-QSP-5540d7` is recorded **withdrawn as stated** — its pole bookkeeping was
   never written out.

**Reopened by**, in order of where it would most plausibly live: a single
certified `lambda` with `N_K(L) > max(d^{q+1}, p^{n'-r})` and a re-verified root
list at `p` outside {2,3,5,7}; at degree above 7 at `n = 131`; or among
`K`-coefficient `lambda` at `n = 131`, which nothing has touched. That remains
**the most valuable outcome this line can produce**.

## 7. The obstruction, read as a resource

The same bookkeeping that caps the fibre makes it **exhaustively enumerable and
certifiable at a field where the object itself cannot be written down**: `deg L`
at `n' = 33` is `2^33`, and the blind re-derivation counted all 244 cells in
about six seconds by composing `lambda` four times and taking two gcds, never
materialising `L`. An upper bound that converts an intractable object into a
degree-2401 one is a **computational resource**, and it is why an exact census
at a 131-bit field was affordable at all ([[KN-TECH-54c38e]]).

A third reading was sought and **not** found, recorded as a null so nobody
re-runs the search: no theory was identified that takes *"kappa is bounded above
by 4.876 and nowhere below"* as an asset. The honest reading is that it is a gap
in the literature ([[KN-OPEN-ac409f]]).

## 8. Provenance

The `F_p`-coefficient slice of (A) — where the twists are trivial and
`Lambda_{q+1}` is just `lambda` composed `q+1` times — was verified by a
Coordinator session in `CORR-20260916-8d0b81` **before the experiment was
designed**, together with the inversion of `RQ-QSP-f9bbdb`'s premise (4) (that
`131 = -1 mod n'` is the attacker's best case; it is the worst). That slice is
the part of the derivation with the longest independent history in this program.

Produced by `EXP-QSP-33b442` under a protocol frozen and approved before any run
(`DEC-20260917-73c49a`), validity-gated by `CORR-20260917-8b80cc`, and reviewed
by the claim-changing round opened by `TASK-20260917-43701b`: six joints, each
owned by exactly one reviewer, with a pre-recorded Coordinator prior that
declared its own contamination. `TASK-20260917-34b637`
(validator-breakthrough, J1/J3/J5) and `TASK-20260917-52b4e6`
(red-team-breakthrough, J2/J4/J6 and the proves-too-much control) ran at
`review-breakthrough` / `max` in independent sessions; `TASK-20260917-5fa7d5`
supplied the blind re-derivation. Verdicts as returned: **J1 holds, J2 holds, J3
holds with the required `n' < n` narrowing, J4 holds, J5 breaks, J6 breaks** —
J5 and J6 against the *headline* and the *closure reading*, and **no refutation
artifact of any tier was produced against (A) or (B)**.

Composed into `EV-QSP-a6aa4b` (direction `weakens`, strength `strong`,
proof_status `derivation`) and decided by `DEC-20260917-793ae2`
(decision: `weaken`, on the record as written). That decision **deferred** this
finding on the explicit ground that a finding may not claim more than its
evidence record's scoped claim while the scoped claim sat inside a hypothesis
whose (E) was refuted and whose (B) lacked the `n' < n` clause.
`DEC-20260917-ea9dd2` supersedes `H-QSP-5540d7` with `H-QSP-645a07`, which
removes that obstruction, and promotes this entry.

The composition's declared independence was machine-checked:
`tools/check_review_independence.py` **passed** — "3 reports, every joint owned
and attested, blindness respected, controls declared"
(`ledger/archives/TASK-20260917-c706bb.yaml`).

One procedural exposure is disclosed rather than absorbed, and the pass above
does **not** cover it, because it bears on
what the round's independence means: the **orchestrating session** committed
reviewer artifacts to the shared branch while `blindness.mutual` was `true` and
`lifted_for` empty (`PROC-1`, `TASK-20260917-619c31`). No reviewer was at fault
— the validator disclosed exactly what it saw and states every verdict was fixed
by its own computation beforehand, the red team declares
`read_sibling_reports: false`, and the blind re-deriver ran no git command — but
blindness is now a property of three reviewers' **restraint** rather than of the
round's **setup**, which is the weaker guarantee. The independence check
inspects the *returned artifacts*; the ordering of commits *during* the round is
not something it can see, so the pass and the deviation are both true and
neither retires the other.
