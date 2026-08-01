---
id: KN-LIT-3029
type: literature
title: "Composition of Zero-Knowledge Proofs with Efficient Provers?"
authors:
  - "Eleanor Birrell"
  - "Salil Vadhan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the composability of different forms of zero-knowledge proofs when the honest prover strategy is restricted to be polynomial time (given an appropriate auxiliary input). When restricted to efficient provers, the original Goldwasser–Micali– Rackoff (GMR) definition of zero knowledge (STOC ‘85), here called plain zero knowledge, is closed under a constant number of sequential compositions (on the same input).

## Key claims (as reported)
- This contrasts with the case of unbounded provers, where Goldreich and Krawczyk (ICALP ‘90, SICOMP ‘96) exhibited a protocol that is zero knowledge under the GMR definition, but for which the sequential composition of 2 copies is not zero knowledge.
- If we relax the GMR definition to only require that the simulation is indistinguishable from the verifier’s view by uniform polynomialtime distinguishers, with no auxiliary input beyond the statement being proven, then again zero knowledge is not closed under sequential composition of 2 copies.
- We show that auxiliary-input zero knowledge with efficient provers is not closed under parallel composition of 2 copies under the assumption that there is a secure key agreement protocol (in which it is easy to recognize valid transcripts).
- Feige and Shamir (STOC ‘90) gave similar results under the seemingly incomparable assumptions that (a) the discrete logarithm problem is hard, or (b) UP 6⊆ BPP and one-way functions exist.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59780568 (1).pdf`
- `downloads/59780568 (2).pdf`
- `downloads/59780568 (3).pdf`
- `downloads/59780568.pdf`
