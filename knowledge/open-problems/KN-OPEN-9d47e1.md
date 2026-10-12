---
id: KN-OPEN-9d47e1
type: open_problem
title: >-
  Does any currently retrievable source supply (a) an effective
  Theorem-2.4-type moment bound, or (b) the classical geometric properties
  of "Family L" (R^1 of the Legendre family), for the EXP-CRYPTO-6505c6
  elliptic-addition-pullback transfer target?
tags: [ecdlp, elliptic-curves, trace-functions, sheaf-theory, legendre-family,
  quantitative-sheaf-theory, effectiveness, moment-bound, open,
  literature-gap, exp-crypto-6505c6]
confidence: reported
status: open
source_refs:
  - EV-CRYPTO-4a91d7
  - DEC-20260928-2f8c6b
  - EXP-CRYPTO-6505c6
  - H-CRYPTO-fde1f1
  - ledger/handoffs/TASK-20260928-14fdee.yaml
added: 2026-09-28
superseded_by: null
---

## The precise unknown

`EXP-CRYPTO-6505c6` audits whether an addition-pullback correlation complex
built from two fixed sheaf families ("Family K": the quadratic Kummer sheaf;
"Family L": R^1 of the Legendre family `v^2 = z(z-1)(z-u)`) admits an
effective, uniform all-extension fourth-moment bound, using
`arXiv:2511.09459v1` (Fouvry-Kowalski-Michel-Sawin, "Bilinear forms with
trace functions") as its sole cited primary source for the required
stratification theorem (Theorem 2.4).

Two disclosed prerequisites are missing **from that specific source**,
confirmed convergently by two independent reads — the original literature
digest chain (`coordination/design/BATCH-aa0d38/audits/TASK-20260913-0d9fe6/source-digest.md`)
and a later, genuinely blind re-derivation (`TASK-20260928-b9a4de`, which
fetched the paper directly and reported back without opening the audit
bundle, the digest, or the earlier corroborating handoff):

1. **Theorem 2.4's implicit constant is non-effective.** It depends on
   `(d, c(M))` but no explicit formula, algorithm, or citable effective bound
   is given anywhere in the paper. Remark 1.2 explicitly disclaims
   polynomial/effective dependence for this paper's own method, contrasting
   it unfavorably against a cited prior work ("[21]" in the paper's own
   numbering) that does achieve polynomial dependence.
2. **Family L does not appear anywhere in the paper**, under any name or
   notation — confirmed by an exhaustive full-text search (57 pages,
   ~126,000 characters), including a specific check of the paper's own
   dedicated worked-examples section (Section 9, covering hypergeometric,
   Kloosterman-type, orthogonal-monodromy and finite-monodromy sheaves, but
   never a Legendre-family construction).

## Why this is an open problem, not a closed negative

Per `docs/claims-and-verification.md`'s refutation-artifact discipline and
`specification.falsification_criterion` ("absence of proof cannot refute the
main target"), neither finding is a counterexample to `H-CRYPTO-fde1f1`'s
transfer-target claim — it is an obstruction to using **this one cited
source** to supply the two missing prerequisites. The audit bundle's own
"Launch gate and next steps" section (`audit-report.md`) already names the
concrete successor: an independent derivation, or a different and more
foundational source, for each gap.

## The precisely statable question

- **Q1.** Does any published or citable source give an EXPLICIT, computable
  effective bound (as a function of `d` and `c(M)`, or an analogous
  complexity invariant) for a Theorem-2.4-shaped stratification/moment
  conclusion — either directly for `arXiv:2511.09459`'s own construction, or
  for a comparable "gallant sheaf" moment estimate that could substitute for
  it? The paper's own Remark 1.2 names a specific prior work ("[21]") that
  achieves polynomial dependence for a related but not identical estimate —
  is that work's method applicable here, and if so, at what concrete
  exponent?
- **Q2.** What is family L's rank, monodromy group, purity weight, and
  Artin/Swan conductor behavior at its declared boundary `{0, 1, infinity}`,
  from a source that actually defines and treats it (rather than a source
  that never mentions it)? Candidate sources not yet checked by this program:
  standard references on the Legendre family's associated local systems
  (e.g. Katz-style treatments of hypergeometric/Legendre sheaves), or an
  independent from-scratch derivation using only classical elliptic-curve
  cohomology.
- **Q3.** Separately, does `arXiv:2511.09459`'s bare `L_chi` notation (found
  by both reads, matching exactly) extend anywhere in the citable literature
  to the specific properties `specification.families.K` requires (rank 1,
  purity weight 0, ramification at `{0, infinity}`, quadratic-norm
  compatibility across extensions) — this is a smaller gap than Q2 (the
  object is at least named) but is still an open O01 obligation for family K
  in the audit's own panel.

## Concrete successor action

Per `DEC-20260928-2f8c6b` next_actions: rank a literature-search or
independent-derivation task against Q1 and Q2 (Q3 is the lower-cost
sub-question and can be folded into the same pass) ahead of any further
formalization pass on `EXP-CRYPTO-6505c6`'s remaining 110+ OPEN cells, since
Q1/Q2 gate the majority of that panel (`open-obligations.yaml`
`GAP-O06-EFFECTIVENESS`, 14 cells directly plus 28 further O07/O08 cells;
`GAP-O01-L` and its downstream O02-O04/O07/O09 chain). This entry performs no
repair and promotes no resolution: it exists so the next agent that
encounters this gap does not have to rediscover it from the audit bundle's
20 files.

## Provenance

Both convergent reads are recorded in `EV-CRYPTO-4a91d7`'s observations. The
audit bundle's own internal tallies (obligation/chart status counts,
cross-checked directly against `open-obligations.yaml`'s independent
grouping) were re-verified by the Coordinator in this review round and found
consistent; no defect was found in the bundle itself. Confidence is
`reported` because the two convergent reads are LLM-mediated fetch-and-read
sessions of a single-versioned primary source, not a human mathematician's
independent verification of the surrounding proof.
