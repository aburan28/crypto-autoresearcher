# Source-bound November 1997 acceptance replay

**Frozen before calculation, 2026-10-24 UTC.** Question: among the already
certified prime-order seed candidates in six recovered prime-field streams,
how many pass every explicit numerical and seed-to-coefficient requirement of
the 17 November 1997 X9.62 draft, without the later retrospective order-width
restriction or a presumption that only one square-root sign may be chosen?

Input is the 17 November 1997 draft PDF at `/private/tmp/x962-11-17-97.pdf`,
SHA-256 `0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e`.
Relevant sections are F.1.1--2, F.2.1--2, F.3.1--3; PDF pages 61--65.
Archived input records are `research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json`
and `research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`.
The former supplies the six complete prime-order seed lists and published
ordinals; the latter supplies 82 branch-bound order and point certificates.
The analysis script binds their SHA-256 digests at execution.

For every certified root branch, independently recompute the draft's SHA-1
integer `r`, verify `r*b^2 = (-3)^3 (mod p)`, nonsingularity, prime full order,
Hasse membership, `n > 2^160`, `n != p`, MOV for B=20, and the retained
subgroup-point certificate flags. The already certified prime order gives
cofactor one and near-primality for any `lmax >= 1`; the full point certificate
is inherited, not re-executed. Collapse two qualifying branches at one seed
ordinal to one seed-level possibility. Compare exact ordinals to the published
ones and the retrospective screen's eleven omissions, seventeen order-width
rejections and thirty-one opposite-root-only cases.

Controls: all ten published curves must pass; the eleven named omissions must
pass; all 82 prior branch certificates must be accounted for exactly; altering
one seed bit must change the computed `r` for every branch. Any failed check
invalidates this replay. A passing replay establishes numerical eligibility
under the draft's listed checks, conditional on this exact reconstructed seed
stream and certified prime-order candidate census. It does not establish that
the original program visited a candidate, used these exact discretionary
parameters, or preferred any branch. No new point counting is planned.

Output: write-once `analysis.json`, reproducible script, a report, diagram
source and SVG, and an inspected PDF. Do not modify inherited records.
