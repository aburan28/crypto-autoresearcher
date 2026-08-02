---
id: KN-LIT-7640
type: literature
title: Ten Advances in Mathematics and Theoretical Computer Science
authors: [OpenAI]
year: 2026
venue: >-
  OpenAI technical report; 249-page collection. Read from the PDF recorded in
  inputs/OAI-TEN-PROOFS-2026/source_record.yaml (SRC-OAI-TEN-PROOFS-2026).
  Unlike SRC-P13-WESOLOWSKI-2026, the artifact is NOT frozen in-repo, so no
  later session can re-read the source these summaries were taken from.
identifiers:
  eprint: null
  doi: null
  url: https://cdn.openai.com/pdf/ten-proofs-oai.pdf
tags: [mathematics, theoretical-computer-science, proof-architecture, theorem-search, certificate, counterexample, invariant, potential-method, reduction, methodology, agentic-harness, cross-domain]
confidence: reported
citation_verified: read
source_record: SRC-OAI-TEN-PROOFS-2026
added: "2026-08-01"
supersedes: KN-LIT-7639
superseded_by: null
---

## Contribution

The report collects ten papers attributed to an internal OpenAI model. It
reports advances in sphere packing, coding theory, group theory, operator
algebras, arithmetic circuit complexity, quantum information, lattice
hardness, convex geometry, Ramsey theory, and extremal graph theory. This entry
preserves those as ten separate external claims and extracts their proof
architectures for retrieval. It does not treat the claims as independently
verified and does not import any of their mathematical conclusions into ECDLP.

## The ten reported results

1. **Cohn-Elkies sphere-packing linear program.** Reports the exact
   high-dimensional exponential rate of the program and matching asymptotics
   for two Fourier sign-uncertainty constants. The proof pairs a universal
   obstruction with an explicit asymptotically matching witness.
2. **Binary and spherical codes.** Reports strict exponential improvements to
   the optimized MRRW and Kabatianskii-Levenshtein bounds. The classical scalar
   construction is embedded as the boundary of a larger moving-subspace
   hierarchy, whose successive levels are claimed to improve strictly; a
   separate small-angle limit recovers the sphere-packing exponent.
3. **Non-sofic group.** Reports that the unit group of the binary Leavitt
   algebra is non-sofic. The proof first isolates a general expander-matching
   criterion, then constructs a concrete property-(T) realization and derives
   a contradiction from a subgroup that would have to be LEF.
4. **Connes rigidity conjecture.** Reports infinitely many pairwise
   nonisomorphic property-(T) groups with the same group von Neumann algebra.
   The construction exploits information forgotten by the observable: distinct
   compact group laws share the same measured action, while an intrinsic group
   invariant distinguishes their dual semidirect products.
5. **Permanent circuit and formula lower bounds.** Reports an
   `Omega(n^2 log log n)` division-free circuit lower bound and
   `Omega(n^4/log n)` formula lower bounds. The arguments construct
   problem-specific complexity measures, specialize the permanent to make the
   measure large, pack disjoint variable blocks so charges add, and explicitly
   prove ceilings and determinant counterexamples for the methods.
6. **Quantum parallel repetition.** Reports exponential decay for every finite
   two-player entangled game with value below one. The new lemma is designed to
   remain useful after exponentially rare postselection: a randomly selected
   reveal increment is charged to a telescoping operator-entropy budget rather
   than to the inverse probability of the conditioning event.
7. **Closest vector problem.** Reports deterministic 3SAT hardness for
   `n^(1/400)`-approximate Euclidean CVP. The proof factors through binary
   nearest codeword, separates completeness from soundness, proves an
   independent algebraic reconstruction lemma, and charges the exponent loss
   through the final dimension-preserving lattice lift.
8. **Ehrhart volume conjecture.** Reports the sharp `(n+1)^n/n!` volume bound.
   The body is moved into a representation where lattice points form a
   holomorphic monomial basis and the unique-interior-point hypothesis becomes
   the exact statement `H_1 = C`; lower and upper slopes of one convex potential
   then sandwich the desired quantity.
9. **Multicolor Ramsey numbers.** Reports a superexponential lower bound and
   hence `R_k(3) = k^Theta(k)`. The recursion preserves a deliberately stronger
   invariant - every color graph is properly `(j+1)`-colorable - because the
   target invariant of triangle-freeness alone is too weak to compose.
10. **Compactness and degeneracy counterexamples.** Reports counterexamples to
    two extremal graph conjectures. The compactness construction exploits the
    quantifier order by combining a family-level upper bound with a separate
    dense witness for every individual forbidden graph; the degeneracy
    construction uses an entropy potential that would increase at every layer
    of a forbidden embedding.

## Cross-paper proof architectures

The report is most useful to this harness as a portfolio of search transforms,
not as a list of domain facts:

- **Embed the baseline as a boundary.** Enlarge a known variational or
  certificate family so the previous best result is an exact parameter slice,
  then prove a strict inward perturbation or monotone hierarchy.
- **Search for observation collisions.** Identify what an invariant, functor,
  certificate, or measurement forgets; construct distinct underlying objects
  with the same observable; then use an intrinsic invariant to prove they
  really differ.
- **Strengthen the invariant before recursing.** Preserve more than the final
  goal requires when that stronger state is what makes composition possible.
- **Replace unstable local bounds with a telescoping potential.** Randomize the
  location of one difficult increment and charge it to an additive global
  budget, especially when conditioning or rare events otherwise introduce an
  inverse-probability loss.
- **Specialize, measure, and pack.** Invent a target-specific measure, construct
  a specialization where it is large, and pack disjoint blocks only after
  proving their charges add without double counting.
- **Change representation so the hypothesis becomes exact.** Prefer a model in
  which the input assumption is an equality, dimension statement, or vanishing
  condition, and prove the claim by a two-sided sandwich in that model.
- **Audit quantifier order.** Rewrite every conjecture and proposed closure with
  explicit quantifiers; look for witness families that satisfy each local
  demand while defeating the claimed uniform selection.
- **State a method ceiling and a nearby-object control.** Prove what the method
  cannot establish, and run it on a close object where the desired conclusion
  is false. This prevents an elegant certificate from being mistaken for a
  general-purpose engine.

These patterns are operationalized in `KN-TECH-080` and
`docs/inventor-protocol.md` section 8.

## What this entry does not carry over from KN-LIT-7639

`KN-LIT-7639` recorded the *announcement*; this entry records the *PDF*. They
are different sources, so supersession is scoped, not total. This intake read
the technical collection and nothing else, and therefore does **not** upgrade
any of the following announcement-level claims, which remain only in
`KN-LIT-7639` at its `citation_verified: false` status:

- attribution of the results to an internal model named "Astra", and the
  "no progress for at least a decade" framing of the ten problems;
- the Lean 4 / `mathlib` formalization of every result and the existence,
  contents, or compilation of the reported `openai/ten-proofs` repository;
- the approximately $2,000 discovery-token cost figure and its rate basis;
- the volunteered negative base rate ("other major problems were attempted
  without success; no Millennium Prize problems"), which is the item of most
  methodological value to this program and is still second-hand;
- the Erdos problem numbers (183, 146, 180) attached to items 9 and 10.

Cite those from `KN-LIT-7639` with its sourcing warning attached, not from
here. The reverse also holds: where the two entries describe the same result
differently, this entry governs, because `KN-LIT-7639`'s statements were
relayed from search summaries.

## Relevance to this program

The source does not discuss generic prime-field ECDLP and supplies no ECDLP
algorithm, relation generator, descent, cost path, or verifier receipt. Its
relevance is methodological: it expands the harness's proof-search repertoire
beyond smoothness, meet-in-the-middle, and rerandomization, and supplies
concrete adversarial checks for identifiability, strictness, quantifiers, and
method limits.

## Not verified here

The PDF was read in full and visually inspected, but none of the ten proofs was
independently re-derived line by line, no reference was separately checked
against its primary publication, and no computation was reproduced. The
proper content status is therefore `reported`. In particular, the report's
claims of resolving or disproving longstanding conjectures must not be cited as
established results on the strength of this intake alone.

The intake is also not reproducible from this repository. The PDF was supplied
as a conversation attachment and is not committed, so the sha256 in
`SRC-OAI-TEN-PROOFS-2026` cannot be recomputed here and the summaries above
cannot be re-checked against the source without re-acquiring the artifact. The
comparison is `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, where the frozen
text makes exactly that check possible. Any later use of this entry that needs
the source text should re-acquire the PDF, verify the recorded hash, and freeze
the extracted text before relying on a specific statement.
