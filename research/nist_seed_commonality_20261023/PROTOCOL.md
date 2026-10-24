# Bounded commonality search: 21 NIST/ANSI prime-field seed blocks

Frozen 2026-10-23 UTC before computing this round's features. The labels and
earlier studies are already known, so this is an exploratory, retrospective
comparison, not a blinded historical test or an experiment on attack cost.

## Question and inputs

Under the stipulated hypothesis that the 1997–98 program evaluated every
reported qualifying block, is there a simple shared arithmetic trait among the
eleven passed-over curves that is absent from the ten published curves?

Read only `research/nist_seed_skipped_curves_20261016/assessed.json` (eleven
seed-level classes) and `traits.json` in that directory (ten published
controls), with SHA-256 digests recorded by the analyzer. One P-224 seed with
two isomorphic signs is one class. Exact identities are the stored EC1 UIDs.

## Fixed feature family

For every row recompute `t = p + 1 - n`, `Delta = t^2 - 4p`, and the twist order
`p + 1 + t` from the archived integers; stop on a mismatch. Trial divide
`abs(Delta)` by every odd prime at most 10,000, retaining the exact valuation
where present. The mathematical focus is whether the Frobenius order has a
small conductor divisor: for odd prime `ell`, `v_ell(f_pi) =
floor(v_ell(Delta)/2)` in the ordinary case. This is a class invariant, not
the unknown representative endomorphism-ring conductor `f_E` or an attack.

The prelisted derived features are: existence and number of odd square-prime
divisors, smallest such divisor (10,001 sentinel if none), sum of
`floor(v_ell(Delta)/2) * log2(ell)` over the bound, maximum valuation, and
indicators for each of `ell = 3,5,7,11,13,17,19,23,29,31` dividing the local
conductor. Controls are normalized absolute trace, signed normalized trace,
the 2-adic valuations of `n-1` and `n+1`, the count of certified twist primes
at most 10,000, and coefficient `b` bit weight (using the smaller of `b` and
`-b` weights only for P-224, where the signs are isomorphic). These
controls overlap earlier explorations; they are included to calibrate this
round's feature search and must not be relabeled as new discoveries.

For each feature record all 21 values and the published-versus-passed-over
pair score within the four fields with both labels (8 published and 11
passed-over; 25 pairs). A pair scores 1 if the published value is smaller,
0 if larger, and 1/2 for a tie. For each feature compute the exact two-sided
tail under all 4,480 within-field label reallocations preserving each field's
published count. Then compute the family-wise minimum-p calibration on those
same allocations. This calibration is only an exploratory diagnostic: actual
labels were selected by a historical process and are not exchangeable draws.

## Outcomes and stopping

A perfect split in this fixed feature family is a candidate rule only. An
advantage on the exact prime-order subgroup would still require a mechanism,
correctness evidence, a matched published-curve control, and complete costs.
A partial association is a lead, never a historical attribution. If no feature
splits the labels, the conclusion is limited to this bounded family. Stop after
the specified 21 rows and 4,480 allocations; no adaptive feature additions to
this round. Retain script, exact JSON output, chart source, vector chart,
Markdown report, and inspected PDF in this directory.
