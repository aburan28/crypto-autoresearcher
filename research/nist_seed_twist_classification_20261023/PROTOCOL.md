# Frozen classification of rational twist forms

**Frozen:** 2026-10-23 UTC, before computing this study's per-curve output. This is a deterministic mathematical audit, not a historical-program replay or an attack-cost experiment.

## Inputs and exact scope

Read eleven seed-level omitted classes from `research/nist_seed_skipped_curves_20261016/assessed.json` (SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`) and ten published controls from its `traits.json` (SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`). Deduplicate isomorphic P-224 coefficient signs using the eleven assessed rows. Cross-bind each exact curve UID to the 21-row twist analysis `research/nist_seed_twist_embedding_20261023/analysis.json`, whose SHA-256 is recorded by the launcher at run time.

## Checks and proof boundary

For every exact prime field `p` and short-Weierstrass coefficients `a,b`, check `p>3`, `a=-3 mod p`, `b!=0 mod p`, `4a^3+27b^2!=0 mod p`, and compute `j=1728*4a^3/(4a^3+27b^2) mod p`. Require `j!=0` and `j!=1728`. Compute `n_twist=2p+2-n`, require it to equal the independently archived twist order, and require 21 unique curve UIDs. Stop on any mismatch; preserve complete output in a new write-once run directory.

The mathematical claim under test is conditional on the standard classification theorem: in characteristic above 3, `j` outside `{0,1728}` gives geometric automorphism group `{+1,-1}`; over a finite field of odd order, its rational forms consist of the original class and exactly one nonsquare quadratic-twist class. Record the theorem and its scope separately from the arithmetic check. The earlier complete twist-order factorizations and embedding-degree results are referenced, not reproduced by this audit.

If all checks pass, this closes only the possibility of an unenumerated quartic or sextic *twist form* of these 21 geometric curves. It does not establish implementation safety, reject an unknown weakness, or prove why the historical curves were selected. If a check fails, retain the exact mismatch and do not infer a twist-classification conclusion.
