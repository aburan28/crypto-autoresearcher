---
id: KN-FIND-0cbdf6
type: internal_finding
title: The twisted injection bound caps the K-rational fibre of a quasi-subfield polynomial at max(d^{q+1}, p^{n'-r}), so every complete splitter with n' not dividing n has n' < n and beta > 1/2 (derivation tier; 0 violations in ~340000 candidates at p in {2,3,5,7}; max N = 132 against 2^33 at n = 131)
tags: [qsp, quasi-subfield, ecc2k-130, ecdlp, index-calculus, factor-base, frobenius, finite-fields, root-counting, beta, scoped-negative, derivation, blind-rederivation, gf2, characteristic-two]
confidence: established
evidence_level: derivation_plus_exhaustive_enumeration
source_refs: [EV-QSP-a6aa4b, DEC-20260917-793ae2, DEC-20260917-6b9a63, EXP-QSP-33b442]
internal_refs:
  - EV-QSP-a6aa4b
  - DEC-20260917-793ae2
  - DEC-20260917-6b9a63
  - EXP-QSP-33b442
  - H-QSP-3fe0ab
  - H-QSP-5540d7
  - RQ-QSP-f9bbdb
  - TASK-20260917-43701b
  - KN-TECH-54c38e
proof_status: derivation
proof_refs:
  - experiments/EXP-QSP-33b442/analysis.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-34b637/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6/report.md
  - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/report.md
  - ledger/evidence/EV-QSP-a6aa4b.yaml
review_chain_note: >-
  The three reviewer tasks of the claim-changing round opened by
  TASK-20260917-43701b are task directories, not ledger records, so they are
  cited by path in proof_refs rather than in internal_refs:
  validator-breakthrough TASK-20260917-34b637 (joints J1/J3/J5),
  red-team-breakthrough TASK-20260917-52b4e6 (J2/J4/J6 and the required
  proves-too-much control), and the blind re-derivation TASK-20260917-5fa7d5.
added: '2026-09-17'
superseded_by: null
---

## Finding

Let `K = F_{p^n}`, let `lambda` in `K[X]` have degree `d >= 1`, write
`L = X^{p^{n'}} - lambda(X)` and `n = q n' + r` with `0 <= r < n'`, and let
`N_K(L)` be the number of DISTINCT roots of `L` in `K`. Define the twisted
iterates `Lambda_1 = lambda`, `Lambda_{k+1} = Lambda_k^{(n')} o lambda` (degree
`d^{k+1}`), where `f^{(k)}` raises every coefficient of `f` to the `p^k`-th
power. Then every `K`-root of `L` is a root of the difference polynomial
`D(Y) := Lambda_{q+1}(Y) - Y^{p^{n'-r}}`, and

```
    N_K(L)  <=  deg D  <=  max(d^{q+1}, p^{n'-r})        whenever D != 0.
```

**Corollary (the beta bound).** Suppose `n'` does not divide `n` (equivalently
`r >= 1`) and `L` splits completely in `K` as a set, `N_K(L) = p^{n'}`. Then
first `n' < n` — by TWO conjuncts and not one: (i) `N_K(L) <= |K| = p^n` gives
`n' <= n`, and (ii) `n' = n` divides `n`, contradicting the hypothesis, so
`n' != n`. Then `d^{q+1} >= p^{n'}`, i.e. `(q+1) l >= n'` with `l = log_p d`,
and since `(q+1) n' = n + n' - r`,

```
    beta  :=  l n / n'^2   >=   n / (n + n' - r)   >   1/2.
```

Cardinality alone is NOT enough for the first step: `n' = n` with `lambda = X`
gives `L = X^{p^n} - X`, a complete splitting with `q = 1`, `r = 0` and
`n/(n + n' - r) = 1/2` exactly, so the strict inequality fails at equality.
That object is excluded by the non-divisibility hypothesis and by nothing else.

**Degenerate branch.** `D = 0` forces `d = p^j` with `j(q+1) = n' - r` and
`lambda = c X^{p^j} + b`, so `L = M^{p^j}` with `M = X^{p^{n'-j}} - c'X - b'`
and `N_K(L) = N_K(M) <= deg M = p^{n'-j} < p^{n'}`: a degenerate `L` never
splits completely as a set. The bound there follows from `deg M` alone. (`c' =
c^{p^{-j}}` requires `K` FINITE, not merely a field. For `b != 0`, `M` is an
affine TRINOMIAL whose root set is a coset of an additive subgroup and is
covered by neither Appendix C.2 of `KN-LIT-0a321c` nor Proposition 6 of
`KN-LIT-4fe9d2`, both of which are the multiplicative family `X^{q^{n'}} -
X^a`; `H-QSP-5540d7` described the whole family as an affine binomial of
subfield or multiplicative type citing both, and that description is wrong for
`b != 0`.)

**Vacuity.** `r` enters the derivation in exactly one place, the exponent of
`Y^{p^{n'-r}}`. At `r = 0` that exponent is `n'`, so the MAX form is `>= deg L`
and says nothing — subfield polynomials are untouched, which is the
proves-too-much control. The `N <= deg D` form is NOT automatically vacuous at
`r = 0`: when `d^{q+1} = p^{n'}` leading terms can cancel and `deg D < deg L`.

### What was measured

- **0 violations of the bound, anywhere.** 45436 producer candidates
  (1260 exhaustive `F_2` toy + 1200 seeded `K`-coefficient + 42244
  complete-splitting sweep + 732 at `n = 131`), plus 291997 + 2400 candidates
  from an independent reviewer implementation written in dense `F_p[X]`
  against the STATEMENT at `p` in {2,3,5,7} — roughly 294400 independent ones.
  Also 0 candidates with `deg D` above the bound, 0 where the `K`-root set of
  `L` fails to divide `D`, 0 `lambda` with `D = 0` outside the claimed shape in
  331664 searched, and 0 counterexamples to the composition-equals-monomial
  step in 1324468 characteristic-`p` compositions.
- **0 complete splitters below either corollary.** All 65 complete splitters
  found in the sweep — (7,3): 36, (7,4): 3, (31,5): 24, (31,6): 2 — recomputed
  from `(n, n', d)` alone with exact rationals: `min(beta - exact) = 0`
  exactly, `min(beta - conservative) = 7/32` exactly.
- **The bound is TIGHT, and not only at `p = 2`.** The largest ratio
  `N / bound` observed anywhere is exactly **1**, attained at `(n, n') = (7,3)`
  by `lambda = X^2 + X` and `X^2 + X + 1` (`N = 8`) and at `(7,4)` by
  `X^4 + X^2 + X` (`N = 16`); and at ODD characteristic by `(p,n,n') = (3,8,3)`
  with `d = 2` (`N = 8 = max(8,3)`) and `(5,5,3)` with `d = 2`
  (`N = 5 = max(4,5)`). Exactly three of the 65 complete splitters attain
  equality in the corollary.
- **At `n = 131`, the target field of `RQ-QSP-f9bbdb`.** Over
  `F_2[z]/(z^131 + z^13 + z^2 + z + 1)`, for every non-linearized `F_2`-
  coefficient `lambda` of exact degree 3..7 (244 per cell) the largest
  `N_K(L)` is **132**, attained at `n' = 33` by exactly **4 of 244**
  candidates (`X^7+X^2`, `X^7+X^5+1`, `X^7+X^6+X^3+X^2`,
  `X^7+X^6+X^5+X^4+X^3+X+1`, each with orbit sizes `[1, 131]` and slack 0),
  with histogram `{0:62, 1:118, 2:60, 132:4}`; `max N = 2` at `n' = 44` and at
  `n' = 66`, histogram `{0:62, 1:122, 2:60}` each. A complete splitter at
  `n' = 33` would need `2^33`, so the **shortfall is a factor of 2^25.96**
  (`log2(132) = 7.04` bits against 33).
- **That target-scale maximum was independently RE-DERIVED BLIND**
  (`TASK-20260917-5fa7d5`, `blind_from_respected: true`; two repository files
  read, no git command run, no sibling path listed). It derived the
  candidate-set size 244 for itself and returned the same maximum, the same
  four attaining `lambda`, the same histogram and the same orbit sizes — by a
  method that never materialises `L` (the composition-lemma instrument now
  recorded as `KN-TECH-54c38e`; degree `2^33` never built, all 244 cells in
  about 6 seconds), re-implemented a second time in sympy `GF(2)` arithmetic
  with 0 mismatches. Blind re-derivation is not replication: it cannot
  reproduce a wrong-but-self-consistent implementation, which is the failure
  mode replication cannot see.
- **The proves-too-much control's declared failure signature is ABSENT on both
  known-false families.** `n' | n`: the bound is vacuous on all 3422 triples
  with `n' | n`, `n <= 32`, `d <= 29`, and the vacuity is STRUCTURAL; of the
  288 candidates where the derivation is non-vacuous at `r = 0`, not one splits
  completely. The linearized family of Theorem 1: 1032 `F_2`-linearized
  complete splitters at `n <= 40`, enumerated by Proposition 2 of
  `KN-LIT-4fe9d2` ALONE with no instrument of the experiment — 0 violations of
  the corollary, and **0 objects with `3/4 <= beta <` the corollary's bound**,
  which is the object that would satisfy Theorem 1 and refute it.
- **Forced fixtures returned their forced values exactly**: subfield
  `(12,6,X) = 64` with the bound VACUOUS, Type 2 at `n = 7` `= 8` with the
  bound ATTAINED, Type 2 at `n = 31` `= 32768`, Theorem 1 equality
  `X^4+X^2+X` over `F_8` `= 4` with the bound ATTAINED.

### Relation to the published bounds

Lemma 4.1 of `KN-LIT-0a321c` (`q l + r >= n'`) and this bound
(`(q+1) l >= n'` for complete splitting) are INCOMPARABLE — this one is
stronger iff `l < r` — and combine to `q l + min(l, r) >= n'`. Theorem 1 of
`KN-LIT-4fe9d2` (`beta >= 3/4`) is for linearized `lambda` at any `n'`; this
corollary is for ANY `lambda` with `n' < n` and `n'` not dividing `n`. Section 5
of `KN-LIT-0a321c` asks whether Lemma 4.1 is tight; this is the removal of its
`n mod n'` term by a complementary bound, not a sharpening of Lemma 4.1.

## Significance

- A **derivation-tier structural bound on factor-base size** that the program
  can reuse without re-running anything: for the quasi-subfield shape
  `{x in K : x^{p^{n'}} = lambda(x)}` with `n'` not dividing `n`, the
  `K`-rational fibre is capped by `deg D`, and the cap was exactly attained in
  four characteristics, so it is not loose.
- **It answers `RQ-QSP-f9bbdb` decision target (a) — an existence result at
  `n' = 33` — NEGATIVELY on the 732 enumerated candidates and on nothing
  else**, and it constrains every untested `lambda` at those cells by
  derivation rather than by list.
- **Design constraint for successors, and this is the reusable half.** Read the
  other way round, `deg D` is a DESIGN VARIABLE: the cap is small precisely
  because `D` has degree at most `max(d^{q+1}, p^{n'-r})`, so any construction
  that legitimately raises `deg D` raises the ceiling with it. A correspondence
  shape proposed as a successor (`IDEA-20260916-a17f43`) must be shown to RAISE
  `deg D`, **not** to find a luckier `lambda` — 0 of roughly 340000 `lambda`
  across two implementations and four characteristics exceeded the cap. The
  target to beat at `n = 131`, `n' = 33` is 132 against `2^33`.
- **The cap is also a computational asset**, not only a cost: it converts an
  intractable degree-`2^33` object into a degree-2401 one, which is the only
  reason an exact census at a 131-bit field was affordable. That instrument is
  `KN-TECH-54c38e` and is cited here rather than re-derived.

## What this finding does NOT claim

Stated separately and at length because the record it is promoted from was
weakened for claiming more than this.

- **It does not claim the closure.** The conditional reading that no
  quasi-subfield factor base of this shape beats generic algorithms is NOT part
  of this finding. That claim lives at `H-QSP-542cfa` at status `specified`,
  and the reason it is not here is that its stated reason was refuted: a
  cheap solver is excluded only by a LOWER bound on the solver exponent
  `kappa`, and both frozen sources give `4.876` as an UPPER bound (Proposition 7
  of `KN-LIT-4fe9d2`, "currently majored by 4.876"; Lemma 3.1 of
  `KN-LIT-0a321c`, a big-O). The exclusion needs `kappa >= (n-1)/n`, which is
  `130/131 = 0.9923664` at `n = 131` — a margin of 0.76% over the cost model's
  own assumption `kappa >= 1`, tending to zero, not a factor of five.
- **It establishes no lower bound on `kappa`** and asserts nothing about
  solver hardness. That gap is `KN-OPEN-ac409f`.
- **It establishes nothing about any deployed curve and moves no attack
  exponent.** No curve, group or point was constructed anywhere in
  `EXP-QSP-33b442`. **rho on ECC2K-130 stands at 2^60.9 iterations**
  (`KN-LIT-096`), untouched.
- **It does not close the quasi-subfield line, and that line must not be
  reported as closed.** Four survivors stand: `n' | n` (Diem's subfield family;
  at `n = 131` only `n'` in {1, 131}); correspondence shapes of conjugate
  degree `>= 2` (`IDEA-20260916-a17f43`); factor bases that are not root sets
  of a single `X^{p^{n'}} - lambda`; and RATIONAL `lambda`, since the
  rational-`lambda` extension is WITHDRAWN AS STATED, its pole bookkeeping
  never having been written out.
- **The observations do not prove the general statement.** They could only have
  refuted it. `(A)` and `(B)` for all `p, n, n'` and `lambda` rest on the
  DERIVATION, which three independent sessions attacked at six named joints and
  did not break; they do not prove that all parameterizations fail, that all
  related representations fail, that no undiscovered structure exists, or that
  no future algorithm exploits the mechanism.

## Boundaries

Copied from `EV-QSP-a6aa4b` `boundaries`; a finding never claims more than its
evidence record's scoped claim.

- **720 of the 732 census rows at `n = 131` (98.4%) are single-instrument.**
  Only the injection counter ran there, and its only check is a root
  re-verifier that can falsify a LISTED root and **cannot detect a MISSED
  one** — and a missed root lowers `N`, which is the direction that makes the
  bound look satisfied. The 62 candidates per cell with `N = 0` carry no
  verification at all. Twelve affine rows now carry an independent
  linear-algebra determination that agrees exactly, and the blind
  re-derivation establishes the `n' = 33` cell's maximum, argmax, histogram and
  orbit structure by a disjoint method — it is not a per-row second instrument
  and it computed nothing at `n' = 44` or `n' = 66`.
- **10 of the 65 complete splitters rest on instrument I2 alone**, all at
  `(n, n', d) = (31, 5, 8)` with `deg D = 2^21`, excluded from the third
  instrument by the ratified amendment `AMD-20260917-001`. Reported as "10 of
  65 complete splitters" and never as "14 of the 356 near-complete candidates"
  without that qualification.
- **The degeneracy control is vacuous by construction.** `n' - r = (q+1)n' - n`
  identically, so degeneracy requires `(q+1) | n`, and every one of the 111
  declared cells has `n` prime with `2 <= n' < n`. The instrument returned
  False on 45436 candidates and **could not have returned anything else**.
  (The degenerate branch is nevertheless independently confirmed OUTSIDE the
  contract: 26 constructed instances and 164 full-`K` degenerate `lambda`, all
  attaining `N = p^{n'-j}` exactly and none splitting completely.)
- **`p != 2` evidence is a REVIEW artifact, not a run of the experiment.**
  Every numerical cell of `EXP-QSP-33b442` is `p = 2`; the odd-characteristic
  evidence exists only at `p` in {3,5,7}, `n <= 13` (`p = 3`) and `n <= 11`
  (`p = 5,7`), `n' <= 8`, degree 2..4, plus 2400 odd-`p` `K`-coefficient draws,
  from `TASK-20260917-34b637`. **The transfer from `p = 2` to general `p` is by
  the derivation and never by measurement.**
- **No independent replication invocation was spent** (PD-6). What stands in
  its place is a determinism cross-check on the same binary and host over
  54.9% of the sweep, plus the structural fact that Stages 0-3 and every
  control are exhaustive and seed-free, plus the one blind re-derivation.
  Those are not the same thing as replication and are not described as such.
- **`K`-coefficient `lambda` at `n = 131` are entirely untouched**, and degree
  there is capped at 7: the census is a measure-zero slice of `F_{2^131}[X]`,
  certifying 244 DISTINCT `lambda` examined at three `n'` — 732 rows, 732
  distinct `L`, 244 distinct `lambda` — not "732 named polynomials".
- **The empirical headline of the experiment was corrected** and only the
  corrected form may be repeated: "732 exact counts at `n = 131`, **546** of
  them certificate-bearing, under **two** independent determinations at Stage 1
  over a shared primitive base and **one** instrument at `n = 131`." The frozen
  contract's own success sentence claimed 732 certificate-bearing counts, 34%
  more than exist.
- **Claim tier `toy`**, per `EV-QSP-a6aa4b`: that is where the candidate mass
  is (`n <= 31`, `p = 2`). It is not a statement that nothing at cryptographic
  scale was computed — the 732 exact counts are in the 131-bit ECC2K-130 field
  — but no curve claim attaches, because no curve was constructed.
- **Infrastructure is not evidence**: an aborted stage, the absent
  Groebner/resultant and sub-quadratic `GF(2)[X]` engines, two hung fault
  injections and one unfinished boundary sweep are infrastructure outcomes
  under AGENTS.md rule 5, and none of them bears on the bound.
