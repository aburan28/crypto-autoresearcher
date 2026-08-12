---
id: KN-LIT-5197
type: literature
title: "Non-interactive Zaps and New Techniques for NIZK"
authors:
  - "Jens Groth"
  - "Rafail Ostrovsky"
  - "Amit Sahai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2000, Dwork and Naor proved a very surprising result: that there exist “Zaps”, two-round witness-indistinguishable proofs in the plain model without a common reference string, where the Verifier asks a single question and the Prover sends back a single answer. This left open the following tantalizing question: does there exist a non-interactive witness indistinguishable proof, where the Prover sends a single message to the Verifier for some non-trivial NP-language?

## Key claims (as reported)
- In 2003, Barak, Ong and Vadhan answered this question affirmatively by derandomizing Dwork and Naor’s construction under a complexity theoretic assumption, namely that Hitting Set Generators against co-nondeterministic circuits exist.
- In this paper, we construct non-interactive Zaps for all NP-languages.
- We accomplish this by introducing new techniques for building NonInteractive Zero Knowledge (NIZK) Proof and Argument systems, which we believe to be of independent interest, and then modifying these to yield our main result.
- Our construction is based on the Decisional Linear Assumption, which can be seen as a bilinear group variant of the Decisional Diffie-Hellman Assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170094 (1).pdf`
- `downloads/41170094 (2).pdf`
- `downloads/41170094 (3).pdf`
- `downloads/41170094.pdf`
