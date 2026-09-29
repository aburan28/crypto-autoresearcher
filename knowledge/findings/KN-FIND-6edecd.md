---
id: KN-FIND-6edecd
type: internal_finding
title: >-
  KN-FIND-a8990a's Theorem A ((Z/2)^{m-2} monodromy for the m-th Semaev
  summation cover) is independently corroborated by a separately-derived
  hypothesis, toy-scale execution, and dual independent review, closing
  most of a8990a's own disclosed "no independent review" risk; plus a
  genuinely new corollary — the standard cross-curve nearby-object null
  control for this cover is unsatisfiable by construction, for any
  companion object, because F_p has a unique quadratic extension
tags:
  - semaev-polynomial
  - summation-polynomial
  - monodromy
  - galois
  - index-calculus
  - ecdlp
  - prime-field
  - elliptic-curve
  - independent-review
  - toy-scale
  - control-design
confidence: derivation
confidence_note: >-
  Not a new theorem: KN-FIND-a8990a's Theorem A already proves the
  containment-and-equality claim unconditionally, in every characteristic.
  This entry records that a SEPARATE derivation (H-MONO-45183a, whose own
  source proposal IDEA-20260805-cf2d5a is dated 2026-08-05, two days
  BEFORE KN-FIND-a8990a was added on 2026-08-07 — genuinely independent
  authorship, not a later citation of a8990a) reaches the same conclusion,
  and that its toy-scale execution (EXP-MONO-12ce1c) received full
  independent Validator + Red Team review — the exact gap a8990a's own
  "Open, and honestly open" section names as "the single largest risk on
  the record." The control-design corollary (the unsatisfiable cross-curve
  null) IS newly established here, by both independent reviewers, and
  does not appear in a8990a.
evidence_level: independent_toy_verification_plus_new_control_design_corollary
internal_refs:
  - H-MONO-45183a
  - EXP-MONO-12ce1c
  - EV-MONO-efbd1c
  - DEC-20260830-0f8def
  - RQ-MONO-001
related_entries:
  - KN-FIND-a8990a   # the unconditional theorem this entry independently corroborates, not restates
  - KN-FIND-c41ea9   # the m=3 slice a8990a itself builds on
  - KN-OPEN-009      # the open problem this bears on; NOT closed by it
proof_status: derivation
proof_refs:
  - ledger/hypotheses/H-MONO-45183a.yaml
  - experiments/EXP-MONO-12ce1c/execution_report.yaml
  - experiments/EXP-MONO-12ce1c/reviews/validator/validation-report.yaml
  - experiments/EXP-MONO-12ce1c/reviews/red-team/red-team-report.yaml
claim_tier: toy
added: '2026-08-30'
superseded_by: null
---

## Why this entry exists, and precisely what it does and does not add

`KN-FIND-a8990a` (added 2026-08-07) already proves, unconditionally and in
every characteristic, that the m-th Semaev summation cover's monodromy is
exactly `(Z/2)^{m-2}` — Theorem A there is a complete derivation, not a
heuristic, and needs no independent verification to be *true*. What it
explicitly lacked, by its own honest disclosure, was **independent review**://
"The derivation and the code share an author and would share any conceptual
error. This is the single largest risk on the record."

This entry does not restate Theorem A. It records that this risk has now
been substantially, though not completely, addressed — by a route that
predates `a8990a` and was not designed with it in mind.

## The independent corroboration

`H-MONO-45183a`'s own derivation (Part A: containment in `(Z/2)^{m-2}`
via Kummer theory over a UFD, plus a separate equality heuristic HEUR-KUM-2
conditional on `S_m`'s irreducibility) traces to `IDEA-20260805-cf2d5a`,
dated **2026-08-05** — two days before `KN-FIND-a8990a` was added. The two
records reach the same containment conclusion by routes that differ in a
material way: `a8990a`'s Theorem A proves EQUALITY directly (transitivity
from the "signed sums generically avoid `E[2]`" argument), while
`H-MONO-45183a` leaves equality as an unproven heuristic and instead
measures it empirically (a genuine "realized distinct Frobenius
permutation count" census, G8). `EXP-MONO-12ce1c`'s execution and its
independent Validator + Red Team review (`EV-MONO-efbd1c`,
`DEC-20260830-0f8def`) found:

- G8 reaches `2^{m-2}` distinct realized permutations at both `m=4` and
  `m=5`, corroborating the equality claim empirically at these toy
  parameters — consistent with, and independent evidence for, `a8990a`'s
  own unconditional proof of the same fact.
- An exhaustive census of all 2,915,514 admissible triples at `p=103`
  (Red Team, third independent classifier) found zero exceptions to the
  containment claim — the strongest single confirmation this program has
  produced for any `m>=4` case of Theorem A, because it is not a sample.
- A dual-path cross-check (two independently-coded classifiers) agreed
  on 64,000 comparisons across two runs, with independently-measured
  ~89% power to detect a real violation via coefficient-corruption
  mutation testing.

**This closes most, not all, of `a8990a`'s disclosed review gap.** The
Red Team's own review resolved to the same model family (`claude-opus-5`)
as `a8990a`'s original producer; only the Validator's joint (resolved to
`claude-sonnet-5`) adds genuine model independence. `a8990a`'s own
"Open, and honestly open" section remains otherwise accurate: no Sage/Magma
reimplementation exists, and novelty against the external literature is
still unadjudicated.

## The genuinely new corollary: the standard nearby-object null is dead on arrival for this cover

Neither `a8990a` nor `H-MONO-45183a` states this. `EXP-MONO-12ce1c`'s
frozen contract required a "cross-curve" nearby-object null control
(points drawn from two different elliptic curves) to exhibit cycle types
OUTSIDE the `(Z/2)^{m-2}`-forced set, on the premise that "the sign-torsor
argument does not apply across two curves." It does not fail this way —
it cannot, for a reason both independent reviewers proved from the actual
code and then generalized:

`F_p` has a **unique** quadratic extension `F_{p^2}`. Every point this
family of constructions uses is defined via exactly one square root of an
`F_p`-element (`y = sqrt(f(x))`), placing it in `F_p` or in that same
`F_{p^2}`, REGARDLESS of which cubic `f` nominally belongs to. The
resulting signed-sum `x`-coordinate is a chord/tangent-formula rational
function of such points, hence itself lands in `F_p` or `F_{p^2}` — a
degree-1-or-2 element over `F_p`, never degree 3 or 4 — independent of
curve membership. The Red Team confirmed this is not specific to "a
different curve": substituting the companion object with a singular
cubic, an unrelated quartic, or a curve-free constant all produced only
the two Kummer-allowed cycle types.

**Consequence for future experiment design in this cover family:** a
genuinely discriminating nearby-object null needs a construction whose
roots are NOT chord-formula rational functions of individually-square-
rooted `F_p`-points — swapping the companion curve, as this contract and
presumably any naive design would do, cannot produce one. `a8990a`'s own
`positive_control_1`-analogue (random quartics, factored directly, no
signed-sum structure) remains a valid nearby object precisely because it
avoids this construction shape entirely.

## What this entry explicitly does not claim

No ECDLP, relation-rate, or cryptographic-scale claim, in either
direction. No closure of `KN-OPEN-009` (only the full-symmetric-monodromy
premise is addressed by either record; the imprimitivity half and the
relation-rate half are untouched). No claim that `a8990a`'s content is
wrong, incomplete, or in need of correction — it is not superseded by this
entry, only independently corroborated and extended with one control-design
corollary its own scope did not need to consider.
