# ECDLP-IDEA-435 — Target-coefficient audit of the function-field lifting face

## Status and claim labels

- Class: `control`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `proposed_unapproved_pending_review`
- Cohort: `20260809-a`
- Evidence scale: audit of **existing** internal evidence (`EV-XEDN-*`); no new lifting experiment proposed
- Contract posture: `review_required` and unapproved
- Scale labels: the underlying data is `toy` (`p ∈ {7,13,19,31}`); every projection is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**. This record proposes a control on evidence this program already holds; its most likely outcome is a scoped negative that closes a lane.

## Falsifiable hypothesis

`KN-TECH-06bb4e` records that this program's xedni lane occupies a **fifth lifting
face** (F5: global, nontorsion, function-field `F_p(t)`) that Silverman's
characteristic-zero taxonomy (`KN-LIT-6935a1`) does not cover. In face F4b the
canonical-height obstruction is quantitative: `T̂ = mŜ` forces `ĥ(T̂) = m^2 ĥ(Ŝ)`, so
a Mordell–Weil relation that *carries the scalar* cannot be small.

This program has nonetheless reported, five times, Mordell–Weil relations with
`max |coeff| = 1` and **no observed coefficient growth** (`KN-FIND-003`, `004`, `005`,
`010`, `011`). Exactly one of the following is true:

- **H-A (escape):** face F5 genuinely evades the height obstruction, and infinity-norm-1
  relations exist that have a **nonzero coefficient on the target section**.
- **H-B (target-blindness):** every recovered infinity-norm-1 relation has coefficient
  **zero** on the target section. The relations are then facts about the surface's
  trivial/geometric Mordell–Weil part and carry no scalar, and F5 is closed by a
  *newly named* obstruction — target-blindness — which is F5's analogue of Masser
  independence rather than of the height bound.

**The audit:** recompute, for every relation already recorded in `EV-XEDN-*`, the
coefficient on the target section, and report the distribution. `H-B` predicts it is
identically zero.

## Mechanism-new operation

The operation is a **retrospective target-coefficient audit** of relations this
program has already found and recorded as `established`. It introduces no new
lifting construction, no new surface family, and no new search. Its novelty is
diagnostic: the existing findings report *coefficient magnitude* (`max |coeff| = 1`)
and *group-law verification*, which certify that the relation holds — but a relation
that holds and a relation that constrains `m` are different objects, and the corpus
records do not state which was measured.

This is the cheapest possible discriminator between "the program has found an escape
from a classical obstruction" and "the program has been measuring a trivial subgroup",
and it should be settled before any scaling work is contracted on that lane.

## Assumptions

1. The `EV-XEDN-*` evidence records retain, or permit recomputation of, the full
   relation vectors and the identity of the target section — not only the norm summary.
2. The target section is unambiguously identified in each surface family, i.e. the
   experiment distinguished a section playing the role of `T̂` from the sections
   playing the role of `Ŝ` and of auxiliary generators.
3. Group-law verification in the original runs certified relation validity, so the
   audit does not need to re-verify the relations themselves.
4. If the original design never *had* a distinguished target section, that is itself
   the finding: the lane measured Mordell–Weil structure of a surface family, not an
   ECDLP lift, and `H-B` is established by construction rather than by measurement.
5. All labels stay `toy`; `p <= 31` is far from any parameter of interest.

## Semantic fingerprint

`existing_xedni_evidence | function_field_lift_face | target_section_coefficient | height_obstruction_discriminator | lane_closure_or_escape`

Re-running the lift at larger `p`, changing the degree window, or densifying the
enumeration are **controls** and do not substitute for the coefficient audit; the
findings already show those do not change the norm.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — `KN-FIND-011`, full-enum densification recovers infinity-norm-1 free-x MW relations at `p=31`; the single most directly audited record.
2. `inputs/ledger_inventory.json` — `KN-FIND-010`, joint `deg x<=3` / `deg b=10` infinity-norm-1 relations at `p<=19` with `p=31` density-blocked.
3. `inputs/ledger_inventory.json` — `KN-FIND-003`, polarisation Gram rank is not Shioda rank; the lane's own precedent for measuring a different invariant than intended.
4. `inputs/ledger_inventory.json` — `KN-FIND-008`, rare-event gates are settled exactly by fibering, and exactness does not protect against formalisation error.
5. `inputs/ledger_inventory.json` — `ECDLP-IDEA-005`, height-compressing global lift, the active idea whose premise depends on this audit's outcome.

## Closest primary literature

- Silverman, [The Four Faces of Lifting for the Elliptic Curve Discrete Logarithm Problem](https://www.math.brown.edu/johsilve/), ECC 2007 (`KN-LIT-6935a1`) — supplies `ĥ(T̂) = m^2 ĥ(Ŝ)` and the Masser independence obstruction in explicit form, and is the source that makes the infinity-norm-1 observations look anomalous rather than encouraging.
- Masser, [Specializations of finitely generated subgroups of abelian varieties](https://doi.org/10.2307/2001769) — the independence obstruction whose function-field analogue is the candidate for face F5.
- Silverman, [Heights and the specialization map for families of abelian varieties](https://doi.org/10.1515/crll.1983.342.197) — the function-field specialization theorem governing the F5 setting.

No checked primary source records this for the program's own artifacts; the diagnostic
is `novelty-unverified` while the underlying theory is classical.

## Complete factor-base-to-target-descent path

This record proposes no descent path. It proposes the *precondition* for one:

1. Recover the full relation vectors and the target-section index from `EV-XEDN-*`.
2. Report the coefficient on the target section for every recorded relation.
3. If identically zero across all families and all `p`: write the scoped negative,
   name the obstruction (target-blindness), attach it to face F5 in `KN-TECH-06bb4e`,
   and re-evaluate `ECDLP-IDEA-005`.
4. If nonzero anywhere: freeze that instance, re-verify by group law, check whether the
   implied `m` is correct, and only then contract a scaling experiment with the height
   growth `ĥ(T̂) = m^2 ĥ(Ŝ)` as the pre-registered prediction to be falsified.

## Full rho/BSGS cost model

The audit itself is a re-read of stored artifacts at negligible time and peak-memory
cost, so it is not a competitor to rho or BSGS and claims no exponent. The baselines
still bound anything it could license: Pollard rho costs `N^(1/2+o(1))` time with
constant state, and BSGS costs `N^(1/2+o(1))` time and `N^(1/2+o(1))` memory. Any
successor experiment inherits the `ECDLP-IDEA-005` cost model:
with lift construction `N^a`, section search `N^c`, height/degree growth exponent
`N^h`, and relation verification `N^q`,

`lambda = max(a, c, h, q)` is the complete time exponent and
`mu = max(a_m, c_m, h)` is the complete peak-memory exponent, both stated against the
rho and BSGS baselines above.

The F4b obstruction is precisely the claim that `h` is not sub-`1/2`; F5's status on
that point is what the audit determines.

## Likely fatal obstruction

`H-B`. The prior strongly favours it: a relation of infinity-norm 1 that constrained
`m` would contradict the height growth in *any* face where a height/degree analogue
holds, and function-field elliptic surfaces do have a degree analogue of canonical
height. The expected result is therefore that the recovered relations lie in the
target-independent part of Mordell–Weil.

## Proof track

Prove that on the frozen surface families the infinity-norm-1 sublattice of
Mordell–Weil is contained in the target-annihilator sublattice, giving `H-B` as a
theorem rather than a measurement, and thereby closing face F5 for the bounded-degree
window without further runs.

## Disproof track

One group-law-verified relation with nonzero target coefficient, on a surface where
the target section was frozen before the search and the implied `m` is confirmed.

## Positive and negative controls

- Positive: construct a surface with a *known* dependent target section (plant the
  relation) and confirm the audit reports a nonzero target coefficient. Without this
  the audit cannot distinguish "always zero" from "never measured".
- Negative: a surface with a provably independent target section; audit must report zero.
- Advice control: any construction that used the scalar to place the target section is
  forbidden advice and must be flagged, not scored.

## Quantitative promotion and falsification gates

Remains proposed and unapproved. Promotion requires the planted-relation positive
control to pass first; an audit that cannot detect a planted nonzero coefficient is
uninformative by construction, which is the exact failure mode `KN-FIND-008` records.
`H-B` confirmed is a scoped negative and a lane closure, not a null result to be
filed and forgotten.

## Artifact plan

- Extraction of relation vectors and target-section indices from `EV-XEDN-*`: `ideas/artifacts/ECDLP-IDEA-435/relation_vector_extract.md`
- Planted-relation positive-control generator: `ideas/artifacts/ECDLP-IDEA-435/planted_control.py`
- Coefficient distribution report per family and per `p`: `ideas/artifacts/ECDLP-IDEA-435/target_coefficient_audit.md`
- Cost receipt: `ideas/artifacts/ECDLP-IDEA-435/cost_analysis.md`

All artifact paths are prospective; no experiment ran.

## Interpretation boundary

This is a control, not a candidate algorithm. Neither outcome is a break. `H-A` would
not be an ECDLP improvement — it would be a single toy-scale anomaly requiring
independent replication before any status change. `H-B` closes a lane and is the
useful, expected outcome.

## Exactly one next executable action

1. Determine from `EV-XEDN-*` whether a distinguished target section existed in the
   frozen experiment design at all. That single read decides whether this is a
   measurement (`H-A` vs `H-B` undetermined) or already a derivation (`H-B` by
   construction), and no computation is required to answer it.
