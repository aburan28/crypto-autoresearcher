# TASK-20260916-a93a2a producer report (idea-generator)

> Placement note (Coordinator session, 2026-09-16): the idea-generator's
> attempt to write this file was refused by the runtime's subagent tool guard
> ("Subagents should return findings as text, not write report files"), so
> the producer returned the report verbatim in its hand-back message and the
> Coordinator placed it here unchanged before archiving (TASK-20260916-f405cb).
> The deviation is the producer's, disclosed by it; the content below is the
> producer's text.

Question: RQ-QSP-f9bbdb. Deliverables: four proposals under ledger/proposals/ and this report. No compute was run; no status changed; nothing outside the write scope was edited.

## Proposals filed
- IDEA-20260916-3f7a1c | measurement | Item (i) without a degree-2^33 gcd: injection x -> x^{2^32} into roots of H(Y) = Y^2 + lambda^{o4}(Y), degree d^4 <= 2401; exact per-candidate certificate; brute-force cross-check at n' in {11, 22}; null/linearized/proves-too-much controls | unverified | low/low | high
- IDEA-20260916-5c9d6e | mechanism | General bound N_K(L) <= d^{q+1} + p^{n'-r} for any lambda in F_{p^n}[X], r >= 1; beta >= n/(n+n'-r) > 1/2; beta >= 131/132 at 131 = -1 mod n'; incomparable with Lemma 4.1; tight on Theorem 1 equality and Type 2 (n = 7); vacuous at r = 0; Section 5 generalisations priced; closure block with resource_check | unverified | low/low | high
- IDEA-20260916-b84e2d | measurement | Item (ii): D_S, cost, relaxation slack of the chain at n <= 41 vs paper M(E), Rojas, enumeration floor, Weil-descent control; (4,3) cell only under pre-flight | unverified | high/medium | low
- IDEA-20260916-a17f43 | representation | Successor object V_R with conjugate-degree 2; room iff r <= q; admissible a listed; m^2-variable fractional Weil restriction; m-homogeneous Bezout 2^38.6 vs 2^31.3 budget at (33, 4); mixed-volume audit and toy census predicted to close it | unverified | medium/low | medium

All four cite RQ-QSP-f9bbdb and table rows by (n', d, m, orbits); each carries the object-frame pair, trichotomy placement, lossy-projection test against the named Sigma, KN-OPEN-020 class, proof_search_map, numbered heuristics with validation routes, target_complexity, dominated_by (checked against the rho row), sota_delta, estimated_cost.

## Recommended first test
IDEA-20260916-3f7a1c Stages 0-3: hand-check the reduction at n = 4; exhaustive fixture at n = 11, n' = 6 (brute gcd at degree 64 vs H-count for all 252 lambda of degree 2..7); the n = 131, n' = 33 exact count for all <= 248 candidates (minutes, KB); brute-force cross-check at n' in {11, 22}. Cheapest valid discriminator: decides item (i) entirely, decides whether the derivation behind 5c9d6e and a17f43 is right, and every outcome is informative (a candidate with > d^4 roots refutes the derivation and reinstates the 2^33 design; agreement closes the F_2 shape at n' in {33,44,66} with certificates and voids row (33, d, 4): attempts 29.6 -> >= 90.6).

## Honest accounting (inventor-protocol section 5)
- Objects considered: (1) K-rational fibre of the QSP relaxation K[X]/(L) under Sigma = {sigma^{n'}, lambda} -- priced at <= d^{q+1} + p^{n'-r}; (2) the relaxation ideal (S) contains (T) under Sigma = {phi} -- its branching (slack) is item (ii)'s quantity; (3) the fractional Weil restriction (x, sigma^a x, ...) with a degree-2 link -- passes the lossy-projection test (discards the closing condition), room iff r <= q. Rejected without a record: endomorphism-defined factor bases (subgroups of E(K), order <= 4 or >= l since |E(K)| = 4l), multiplicative subgroups (already in the note), n' | n (impossible at prime n).
- dominated_by: every proposal n/a as an ECDLP result; rho at 2^60.9 dominates every table row and the proposals make the open rows void rather than cheaper. As bounds/instruments: per record (Theorem 1 and Lemma 4.1 on their own slices; the degree-2^33 gcd on derivation-independence only).
- sota_delta: zero on every ECDLP cost axis. If the derivation survives review: admissible beta at n' not dividing n moves from "unbounded below except Lemma 4.1" to >= n/(n+n'-r) > 1/2 -- the "cannot beat generic algorithms" conclusion Section 5 of KN-LIT-0a321c anticipated from removing the n mod n' term. RQ premise (4) inverted.
- Closures with mechanism: polynomial-lambda QSP factor bases at n' not dividing n; obstruction = Bezout number of two low-degree curves in the (x, x^{p^r}) plane; quantity N_K(L) <= d^{q+1} + p^{n'-r}; scope every p, n, n' with n' not dividing n; resource_check examined: conjugate-degree d_1 >= 2 has room iff (q+1) log_p d_1 >= r -> IDEA-20260916-a17f43. All unverified until the hand check and toy fixtures run.
- Open directions: the successor shape's two audits; K-coefficient c, e (needs a construction); whether the rank-metric/subspace-code literature named in KN-LIT-4fe9d2 section 4.5 already has the injection bound; pole bookkeeping for rational lambda.

## Discrepancy found in an input (not edited; outside write scope)
analysis/qsp-ecc2k130/qsp_ecc2k130.py cost_cell encodes log2_ME = m(m-1)(1+log2 d), i.e. M(E) = 2^{m(m-1)} d^{m(m-1)}. Appendix A.1 of the frozen paper reads M(E) = prod_{k=1}^m lambda_k, lambda_k = d^{k-1} 2^{m-1}, i.e. 2^{m(m-1)} d^{m(m-1)/2}. At (m,d) = (4,3): 2^21.5 (paper) vs 2^31.0 (note). Under the paper's formula table.md row (33,3,4,131) floor would be max(29.6+21.5, 53.9) = 53.9 not 60.6; (33,3,4,1) stays 68.0. Changes no conclusion (3f7a1c voids the row) but should be adjudicated against the PDF (the extraction splits the exponent across lines). Recorded in b84e2d claim (B) and a citation note of 3f7a1c.

## Inputs
Every card input read in full (the Euler-Petit extraction in two pages); no input could not be read. Also read: AGENTS.md, KN-OPEN-020, IDEA-20260806-c5d183, IDEA-20260901-863e36, IDEA-20260916-71ab94, IDEA-20260913-9ba7fc.

## Novelty check performed
Corpus grep (quasi-subfield | Huang-Kosters | Euler-Petit) over ledger/, knowledge/, analysis/, coordination/: only the frozen-paper records, the analysis note, this task's cards, and SEMBIN/PFDR records citing the CRYPTO 2015 last-fall-degree paper; no prior QSP factor-base proposal. Web: two searches (no post-2022 QSP follow-up; no iterate-degree root bound found) and the McGuire-Mueller arXiv 1905.11755 abstract (linearized trinomials only). Honest label for all four: unverified.

## ID allocation
No shell tool in the producer session; tools/allocate_id.py could not be run there. Tokens chosen at random without scanning state; checked by Glob/Grep. (Coordinator: `--check` run on all four ids after filing; each occurs exactly once across 25,357 identifier-bearing paths.)

## Lane note
No goal dispatch queue exists for RQ-QSP-f9bbdb (GOAL-ECDLP2M-001 is draft); no lane claim applied.
