---
id: KN-OPEN-025
type: open_problem
title: For which automorphism orders k can Galois symmetry accelerate the TNFS linear-algebra step, and what is the end-to-end gain?
tags: [number-field-sieve, tnfs, galois, automorphism, symmetry, linear-algebra, dlp, finite-field, extension-field, pairing, cost-model, open]
confidence: reported
status: open
source_refs: [KN-LIT-7643, KN-TECH-035, KN-OPEN-012]
added: 2026-08-01
superseded_by: null
---

## Statement

In the Tower Number Field Sieve — the best known algorithm for the DLP in `F_{p^n}`
with composite `n`, hence the algorithm that sets pairing-based security levels —
order-`k` Galois automorphisms have long been used to speed up **relation collection**
by a factor `k`. Using them in the **linear algebra** step was open beyond `k = 2`.

[[KN-LIT-7643]] (Al Aswad, Pierrot, Thomé) reports constructions for **`k = 6` and
`k = 12`**, with linear-algebra speedups of approximately `36` and `144` — the
quadratic factor `k²` previously attained only at `k = 2`. Two things remain open, and
the second is the one that matters for security estimation:

**(Q1) Generality.** Is there a construction for arbitrary `k`, or does the method
depend on specific structure of `F_{p^6}` and `F_{p^{12}}`? The paper closes two cases;
the abstract does not claim a general solution.

**(Q2) End-to-end effect.** Relation collection and linear algebra are the *two*
dominant TNFS steps. A `k²` speedup on one of them is not a `k²` speedup on TNFS.
**No end-to-end figure is stated in the source**, and none is derivable from what this
corpus holds. Until (Q2) is answered, no concrete security level should move.

## Why it matters

- **`n = 6, 12` is not a toy regime.** These are the embedding degrees of deployed
  pairing-friendly curves. Any real change to TNFS cost at those `n` propagates to
  concrete parameter recommendations — which is exactly why (Q2) must be answered before
  (Q1) is interesting.
- **Symmetry exploitation is a program-level theme.** The corpus already tracks
  automorphism and symmetry speedups on the *relation-collection* side of index calculus
  (`symmetry`, `weil-descent`, `glv-gls` threads). Acting on the **linear algebra** is
  the harder half, because the matrix structure has to survive the quotient. If the
  mechanism is general, it is a technique worth abstracting; if it is `F_{p^6}`- and
  `F_{p^{12}}`-specific, it is a pair of constructions.
- **Corpus gap.** A coverage audit on 2026-08-01 found **two** entries mentioning TNFS
  against 218 touching index calculus. This program's index-calculus expertise is
  concentrated on the elliptic-curve side, and the finite-field side that actually sets
  pairing parameters is under-covered.

## Current state (as reported)

- `k = 2`: known, quadratic factor 4.
- `k = 6, 12`: reported in [[KN-LIT-7643]], factors ≈36 and ≈144, **validated on small
  examples only**, with a SageMath implementation.
- Arbitrary `k`: no claim.
- End-to-end TNFS speedup at any `k`: **not stated anywhere this corpus holds.**
- Consequence for any concrete curve (BN, BLS12, BLS27, …): none established. Deriving
  one from a single-step speedup would be precisely the partial-cost error `AGENTS.md`
  rule 4 and [[KN-TECH-035]] forbid.

## What would resolve it

1. **Read [[KN-LIT-7643]]** and extract the end-to-end model: what fraction of TNFS
   wall-clock the linear algebra represents at the parameter sizes in question, and what
   the composed speedup is once relation collection is held fixed. This answers (Q2) and
   is the only step needed before the entry can inform any security estimate.
2. Determine from the construction whether `k = 6, 12` are special (e.g. via the tower
   structure of `F_{p^6}`, `F_{p^{12}}`) or instances of a general `k` method. Answers
   (Q1).
3. Only if (Q2) is material: revisit whether any pairing parameter recommendation in
   this program's ledger is affected. **No such revision is proposed now.**

## Not verified here

Every figure above is relayed from the [[KN-LIT-7643]] abstract retrieved 2026-08-01;
the paper was not read, the constructions were not checked, and the `36`/`144` factors
were not reproduced. **No claim is made that TNFS is faster end-to-end, that any
pairing-based parameter set is weakened, or that a general-`k` construction exists.**
**Does not bear on the ECDLP** — this is the finite-field DLP, not the elliptic-curve
one.
