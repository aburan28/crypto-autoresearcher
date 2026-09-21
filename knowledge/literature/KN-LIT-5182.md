---
id: KN-LIT-5182
type: literature
title: "Non-interactive Distributional Indistinguishability (NIDI) and Non-Malleable Commitments"
authors:
  - "Dakshita Khurana"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce non-interactive distributionally indistinguishable arguments (NIDI) to address a significant weakness of NIWI proofs: namely, the lack of meaningful secrecy when proving statements about NP languages with unique witnesses. NIDI arguments allow a prover P to send a single message to verifier V, from which V obtains a sample d from a (secret) distribution D, together with a proof of membership of d in an NP language L.

## Key claims (as reported)
- The soundness guarantee is that if the sample d obtained by the verifier V is not in L, then V outputs ⊥.
- The privacy guarantee is that secrets about the distribution remain hidden: for every pair of (sufficiently) hardto-distinguish distributions D0 and D1 with support in NP language L, a NIDI that outputs samples from D0 with proofs of membership in L is indistinguishable from one that outputs samples from D1 with proofs of membership in L. – We build NIDI arguments for superpolynomially hard-to-distinguish distributions, assuming sub-exponential indistinguishability obfuscation and sub-exponentially secure (variants of) one-way functions. – We demonstrate preliminary applications of NIDI and of our techniques to obtaining the first (relaxed) non-interactive constructions in the plain model, from well-founded assumptions, of: • Commit-and-prove that provably hides the committed message • CCA-secure commitments against non-uniform adversaries.
- The commit phase of our commitment schemes consists of a single message from the committer to the receiver, followed by a randomized output by the receiver (that need not be returned to the committer).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960292 (1).pdf`
- `downloads/126960292.pdf`
