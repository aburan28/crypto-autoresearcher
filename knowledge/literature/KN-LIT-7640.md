---
id: KN-LIT-7640
type: literature
title: "Ten Advances in Mathematics and Theoretical Computer Science (OpenAI, 2026) — full-text reading"
authors:
  - "OpenAI"
year: 2026
venue: 'OpenAI, collection of ten research papers, PDF dated 2026-08-01'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://cdn.openai.com/pdf/ten-proofs-oai.pdf
tags: [openai, astra, ai-for-mathematics, machine-discovered-proof, autonomous-research, closest-vector-problem, cvp, gapcvp, lattice, hardness-of-approximation, np-hardness, 3sat, pcp-free, syndrome-decoding, nearest-codeword, reed-solomon, post-quantum, sphere-packing, cohn-elkies, kabatianskii-levenshtein, coding-theory, non-sofic-groups, connes-rigidity, operator-algebras, arithmetic-circuit-complexity, permanent, parallel-repetition, quantum-games, ehrhart, ramsey, erdos-problems, extremal-graph-theory, barrier-result, premature-closure, methodology, primary-source, full-text-read]
confidence: reported
citation_verified: full_text
added: "2026-08-02"
superseded_by: null
---

## Status of this entry

Supersedes [[KN-LIT-7639]], which was written from web-search summaries when the
host was blocked by this session's egress policy. The PDF has since been
retrieved and read: `https://cdn.openai.com/pdf/ten-proofs-oai.pdf`, HTTP 200,
2 266 371 bytes, 249 pages, `sha256
64b900d5fae6fe22f2ae1b8e3b712d20055194a6c81cf343a2455e5898ac7dd6`. Text frozen
at `inputs/OPENAI-TEN-ADVANCES-2026/`.

**Three claims in KN-LIT-7639 did not survive contact with the document.** They
are corrected in "Corrections to KN-LIT-7639" below rather than quietly dropped,
because two of them were load-bearing for that entry's reading of the program's
own methodology.

PDF metadata as read: Title *Ten Advances in Mathematics and Theoretical Computer
Science*; Author *OpenAI*; Subject *"A collection of research papers by an
internal model at OpenAI"*; Creator *LaTeX with hyperref*; CreationDate
*2026-08-01*.

## What the document is

A 249-page collection of ten self-contained research papers, each a chapter with
its own abstract, references, and in two cases acknowledgments. The abstract
opens: *"We present a collection of results obtained by an internal OpenAI model,
spanning mathematics and theoretical computer science."*

That sentence is the **entire** methodological content of the document. There is
no preface, no methodology section, no discussion of how the model was used, no
compute or cost figure, and no statement of the human role. It is a mathematics
volume, not an announcement.

## The ten results (read from the primary text)

Chapter abstracts and introductions were read. **No proof was checked.**

1. **Sphere packing.** The exact exponential decay rate of the Cohn–Elkies linear
   program is *determined*: `lim LP_d^{1/d} = √e/(2π)`, proving the rate
   conjectured by Afkhami-Jeddi–Cohn–Hartman–de Laat–Tajdini. Hence
   `Δ_d ≤ 2^{−(α*+o(1))d}` with `α* = ½log₂(2π/e) = 0.6044…`, against the
   Kabatianskii–Levenshtein exponent `0.59905576…` [KL78]. The text states this
   is *"the first improvement since 1978 to the general sphere-packing
   exponent."* It also settles the Fourier sign-uncertainty problem
   asymptotically: `A₊(d)/√d, A₋(d)/√d → 1/π`.
   **This chapter is also a barrier result:** *"The matching lower bound shows
   that no Cohn–Elkies auxiliary function can improve this exponent."*
2. **Binary and spherical codes.** Classical upper bounds for fixed-distance
   binary and spherical codes improved by *exponential factors for all
   parameters*; the spherical construction independently recovers Chapter 1's
   packing exponent as a small-distance limit.
3. **Non-sofic groups.** An explicit non-sofic group is constructed, resolving
   whether every countable group admits finite permutation approximations. Uses
   property-(T) expanders and the binary Leavitt algebra.
4. **Connes's rigidity conjecture.** Infinitely many pairwise nonisomorphic
   property-(T) groups with the same group von Neumann algebra — disproving the
   conjecture and answering a related finite-to-one question of Popa.
5. **Arithmetic circuit complexity.** For the permanent: division-free circuits
   require `Ω(n² log log n)` gates; formulas require `Ω(n⁴/log n)` leaves.
6. **Quantum parallel repetition.** Exponential parallel repetition for *every*
   finite two-player entangled game, extending the classical principle beyond
   previously treated special classes.
7. **Closest vector problem.** `n^{1/400}`-factor hardness for Euclidean CVP —
   see the dedicated section below.
8. **Ehrhart's volume conjecture.** The sharp bound `(n+1)ⁿ/n!` in every
   dimension, for convex bodies whose barycenter is their only interior lattice
   point.
9. **Multicolor Ramsey.** `R_k(3) ≥ (c k^{1/3}/log k)^k`, which with the classical
   factorial upper bound gives `R_k(3) = k^{Θ(k)}`; corollary — the Shannon
   capacity of graphs with independence number 2 is unbounded. Cites Erdős
   problem #183.
10. **Compactness and degeneracy.** Two counterexamples: a finite family `F` of
    connected bipartite graphs with `ex(n,F) = O(n^{4/3−1/48})` while
    `ex(n,F) = Ω(n^{4/3})` for each `F ∈ F`, disproving the Erdős–Simonovits
    compactness conjecture; and a connected bipartite 2-degenerate `H` with
    `ex(n,H) ≥ c·n^{3/2+ε}`, disproving a degeneracy conjecture of Erdős. Cites
    Erdős problems #146 and #180.

## Chapter 7 in detail — the only chapter adjacent to this program

**Main theorem.** A *deterministic polynomial-time many-one* reduction from 3SAT
to `GapCVP⁽²⁾_{n^{1/400}}`, where `n` is the rank of a lattice given by an
explicit square integer basis. Hence `GapCVP⁽²⁾_{n^{1/400}}` is NP-hard under
deterministic polynomial-time many-one reductions.

**Why the reduction is notable beyond the exponent.** The text is explicit: *"The
reduction uses no randomized step, gap-producing PCP, or Projection Games
Conjecture."* The route is
`3SAT → binary nearest codeword → Euclidean CVP`, the first arrow being the
technical contribution and the second the standard dimension-preserving
reduction. Assignments are encoded by Reed–Solomon power-sum constraints over a
characteristic-two field; soundness reconstructs separable root sets over a
rational function field from bounded power sums, and recovers clause assignments
through valuations.

**Companion factors.** `n^{1/200}` for binary nearest codeword and syndrome
decoding; `n^{1/(200p)}` for closest vector in every fixed rational `ℓ_p` norm,
`p ≥ 1` (`p = 2` recovering the main result). Parameters: `q = Θ(N²⁰⁰)`,
`n ≤ 40N⁴⁰¹` — *"large, but fixed-polynomial, output and bit complexity."*

**Prior state of the art, as the chapter states it.** Dinur–Kindler–Raz–Safra
[DKRS03] proved NP-hardness of Euclidean CVP within `n^{a/log log n}`. That factor
grows faster than every fixed power of `log n`, but **its exponent tends to
zero**, so it does not give hardness within `n^c` for any fixed `c > 0`. Fixed-
polynomial lattice inapproximability was previously available only *conditionally*
(Moshkovitz; Mukhopadhyay, on the Projection Games Conjecture). So the advance is
from "no fixed exponent, unconditionally" to `c = 1/400`.

**The barrier above it.** Aharonov–Regev [AR05]: `GapCVP⁽²⁾_{C√n} ∈ NP ∩ coNP`,
so NP-hardness at the square-root scale would imply `NP = coNP`. The chapter
states the resulting open problem plainly: determine the largest `c ∈ [1/400, 1/2)`
for which `GapCVP⁽²⁾_{n^c}` is NP-hard.

**On cryptographic relevance — the chapter's own words.** After surveying Ajtai,
GGH, Regev and NIST standardization, the text says: *"These cryptographic
applications rely on appropriate structured or average-case assumptions, rather
than directly on the worst-case NP-hardness of CVP."* This program's earlier
reading — that the result is a hardness statement and not an attack surface — is
therefore **the source's own position**, not an inference layered on top of it.

## Corrections to KN-LIT-7639

1. **"Astra" does not appear in the document — zero occurrences.** The document
   says only *"an internal OpenAI model."* The name Astra, the "next major model
   family" framing, and the GPT-6 gloss all come from the announcement and press
   coverage. Nothing in the primary source names or versions the model.
2. **"Lean" and "mathlib" do not appear in the document — zero occurrences.**
   There is no formalization, no certificate, and no verification section. The
   44 apparent `Lean` matches in the text layer are all inside `Boolean`, and
   both `formaliz*` hits are ordinary mathematical usage ("we formalize this
   observation by induction"). **KN-LIT-7639's central methodological reading —
   that this is `docs/claims-and-verification.md`'s certificate-first design
   executed externally — rests entirely on the announcement page and the
   reported `openai/ten-proofs` repository, neither of which this program has
   been able to open.** The Lean claim may well be true; it is simply not
   evidenced by the source that has been read, and must not be cited to this
   document.
3. **The sphere-packing result was mischaracterized.** KN-LIT-7639 relayed "new
   upper bounds approaching the Cohn–Elkies threshold." The actual result
   *determines the LP's exact asymptotic rate* and proves a matching lower bound
   showing **no Cohn–Elkies auxiliary function can do better**. It is a
   determination plus a barrier, not an approach to a threshold. (KN-LIT-7639's
   marked guess that the "1978" reference is Kabatianskii–Levenshtein is
   confirmed: the chapter cites [KL78, Lev79] by name.)

Also newly visible, and absent from KN-LIT-7639: **the Connes result has
independent concurrent competition.** Chapter 4's acknowledgments state that
during manuscript preparation the authors learned of *"independent and concurrent
work by Shuoxing Zhou also establishing a counterexample to Connes's rigidity
conjecture, developed in part with the assistance of GPT-5.6 Sol."* One of the
ten was reached separately, by a named human, also with model assistance.

## Relevance to this program

**No result touches the ECDLP.** No elliptic curves, no discrete logarithms, no
isogenies, no index calculus. Recorded as methodological literature plus one
adjacent hardness datum.

1. **The CVP chapter is background, not an opening.** It raises a worst-case
   NP-hardness exponent; it breaks nothing, and the chapter itself says the
   deployed lattice schemes rest on structured/average-case assumptions rather
   than on worst-case CVP hardness. Its only corpus contact is the leakage-model
   lattice/HNP lane ([[KN-OPEN-011]], [[KN-OPEN-018]]). Recorded explicitly so a
   future ideation pass does not read "lattice cryptography" in a headline as an
   attack surface.
2. **Two chapters are shaped exactly like `docs/target-result-profile.md` asks.**
   Both move an exponent on a central problem against a stated prior best, and
   both are honest about the ceiling: Chapter 1 improves the general packing
   exponent for the first time since 1978 *and proves its own method cannot go
   further*; Chapter 7 states its `[1/400, 1/2)` gap and names the `NP = coNP`
   barrier that closes the top. That pairing — an exponent moved, and the
   barrier above it named in the same breath — is the `sota_delta` /
   `dominated_by` honesty `docs/inventor-protocol.md` and [[KN-TECH-056]]
   require, and these chapters are usable as *shape* exemplars alongside the
   Wesolowski exemplar (`inputs/P13-WESOLOWSKI-2026/`).
3. **Chapter 1 is a worked example of the closure [[KN-OPEN-019]] asks for.** That
   entry's complaint is that this program's saturation claims are statements
   about its search rather than about the problem. Chapter 1 shows the other
   thing being done: a *method* is characterized exactly, and the matching lower
   bound proves the method's exponent cannot be improved by any admissible
   function. That is a closure over a technique, argued rather than tallied —
   the form [[KN-TECH-056]] component 7 demands. Worth reading directly by
   anyone attempting a real closure argument here.
4. **The premature-closure evidence strengthens.** Ten problems static for a
   decade or more, several far longer, were not saturated. This is a second
   independent data point alongside [[KN-LIT-7594]], now from a different lab and
   a different domain.
5. **The cost comparison in KN-LIT-7639 must be dropped, not merely caveated.**
   The ≈$2,000 figure appears **nowhere in this document**. It is an
   announcement-page claim. Do not quote it against [[KN-LIT-7594]]'s ≈$100k per
   result, and do not attribute it to this source.
6. **Named humans are in the loop, visibly.** Two chapters carry acknowledgments
   thanking named mathematicians for comments and careful readings (Ch. 3: Henry
   Bradford, Michael Chapman, Alon Dogon, Francesco Fournier-Facio; Ch. 4: Sorin
   Popa, François Charles, Cyril Houdayer). Whatever the division of labour, the
   manuscripts went through human mathematical review before publication.

## Not verified here

- **No proof in this collection has been checked by this program**, and no
  theorem statement has been independently confirmed. Every mathematical claim
  above is `reported` — relayed from chapter abstracts and introductions.
- **The attribution itself is untested.** That these results were "obtained by an
  internal OpenAI model" is a one-sentence claim by the publishing party, with no
  supporting methodology, transcript, or protocol in the document. Nothing here
  lets this program assess what the model did versus what its human collaborators
  did.
- **Not peer-reviewed.** This is a self-published PDF, not a refereed venue, and
  as of this entry no chapter is known to have been accepted anywhere.
- **The announcement page was not retrieved** (HTTP 403 from the origin's bot
  protection, after egress was opened — a different failure from the earlier
  policy block). Everything sourced only to it — the Astra name, the Lean
  certificates, the ≈$2,000 cost, the credit statement, the Leiden declaration
  reference, and the quoted remarks by @polynoamial — remains **unverified**, and
  is retained in [[KN-LIT-7639]] under that entry's own sourcing warning.
- **The `openai/ten-proofs` Lean repository was not retrieved**; the GitHub layer
  enforces this session's repository allowlist. Its existence and contents are
  unverified.
- Formulas quoted above are transcribed from a mechanical PDF text extraction in
  which mathematical display is reflowed and lossy. They were read back against
  context and are believed right, but **re-check any formula against the PDF
  before relying on it** (see the extraction caveat in
  `inputs/OPENAI-TEN-ADVANCES-2026/`).
