# Source-grounded continuation: active-variable PC and certified specialization

2026-10-30. Design note only: no implementation, solver invocation, benchmark, experiment result, novelty claim or scientific status change. Motivated by DEC-20261030-0c834c requiring a strategy/accounting change before another comparison.

## Observed implementation boundary

engine._residuals restricts all original polynomials at a prefix, then _try_prefix passes the original ring object to legacy.refute. encoding imports that refute from core. BoolRing.restrict removes assigned variables from every surviving monomial. core.refute initializes a new basis/queue on each call and recursively multiplies accepted rows by every i in range(ring.n), including assigned or otherwise absent variables. The current cache records attempted prefix keys, not residuals or certified bases. No claim is made about other repository implementations.

## Candidate A: active-variable search

For each restricted generator list G, take the union of its monomial supports as active set A. Restrict multiplication rules to x_i for i in A, preserving original bit labels or using an explicit bijective compact mapping with checked certificate lifting. Constants and zero polynomials need explicit handling. A full-leaf nonzero constant already gives a checked inverse certificate; no active variable is needed.

Mathematical obligation: in the Boolean quotient, specializing all variables outside A to0 is a ring homomorphism fixing every G_i. Any identity1=sum q_i*G_i maps to1=sum pi(q_i)*G_i without increasing degree. A degree-D PC derivation maps line by line: addition/scaling remain valid, multiplication by active x_i remains valid, and multiplication by an inactive variable maps to0. Hence existence of a degree-D refutation does not require the absent variables. This is a proposed proof argument to independently check, not a proof of completeness or equal behavior of the current selected-echelon algorithm.

The degree-D Boolean monomial universe changes from sum_(j=0)^D binomial(n,j) to sum_(j=0)^D binomial(|A|,j), with binomial terms beyond the variable count zero. This is a combinatorial search-space bound, not measured matrix size, runtime or total-cost gain. Certificates must still be independently checked against the exact original-prefix residual list. Capped selected-echelon behavior may change; UNKNOWN stays UNKNOWN and no inference of non-refutability is allowed. Full projected model sets and the original complete fallback/reference must remain checked.

## Candidate B: persistent certified parent rows

If a parent row r=sum q_i*G_i has a child substitution sigma, retain sigma(r)=sum sigma(q_i)*sigma(G_i). Degrees do not increase under Boolean assignment. These sound inherited rows may seed a child basis; specialization can destroy pivots, create dependencies or yield0, so echelon form is not blindly reused. Add all child original generators and charge re-elimination and proof-multiplier specialization. Backtracking uses immutable or explicitly reversible state; a row is never transferred to a sibling without valid common-ancestor derivation. Record whether proof search is still bounded by row degree, multiplier degree, or both.

A parent basis is not assumed complete, and warm-start row ordering may change capped outcomes. Reusing rows can cost more than rebuilding because certificate multipliers, copying, dedup and retained memory grow. Charge these, including discarded rows and failed searches; no free warm starts or preprocessed parent rows.

## Candidate C: callback bookkeeping

Track contiguous-prefix changes and newly eligible unattempted keys from assignment/backtrack events rather than rescan all prefix depths on every has_clause call. This addresses duplicate-prefix and prefix-scan work only. It does not itself reduce distinct PC searches. Fixed assignments, nonchronological backtracking, queued clauses and full-assignment versus genuine partial triggers require explicit controls.

## Prospective comparison requirements

Freeze a separate contract before any trials. Preserve model-only and original partial-prefix arms; isolate active variables, parent-row reuse and callback bookkeeping in separate arms before combining. Keep all four encodings, exact identity checks, complete projected sets, controls/A/A and the charged complementary-point baseline. Fix comparable per-arm limits and disclose whether equal row caps mean different work. Record preprocessing, restriction, row generation/elimination, certificate creation/checking, multiplier storage/copies, reconstruction, peak memory and I/O. Historical tiny cells are calibration; a new held-out inventory must be chosen prospectively. A general speedup/regularity reduction remains unproved even if a local implementation gain is eventually measured.

## Source bindings
- research/prime_sat_prefix_search_20261030/engine.py SHA256 ad46f7109f25f7c2f6794be7d3a1f42f19571f98953e7e6b9fe0234cad1ef2ee
- research/prime_sat_five_tests_20261029/core.py SHA256 c67fc44404b282ac963f1021a4b6197ebbb4a8bf382c70a2576db45172065a4f
- research/prime_sat_followup_20261029/encoding.py SHA256 2b18f50238db633eb91ac33a36660c52620e81c5f6fa1c9c78d40c261e99041f
