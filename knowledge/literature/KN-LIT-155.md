---
id: KN-LIT-155
type: literature
title: "Multi-trapdoor Commitments and their Applications to Proofs of Knowledge Secure under Concurrent Man-in-the-middle Attacks?"
authors:
  - "Rosario Gennaro"
year: 2003
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2003/214"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2003/214"
tags: [pairing, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of multi-trapdoor commitments which is a stronger form of trapdoor commitment schemes. We then construct two very efficient instantiations of multi-trapdoor commitment schemes, one based on the Strong RSA Assumption and the other on the Strong Diffie-Hellman Assumption.

## Key claims (as reported)
- The main application of our new notion is the construction of a compiler that takes any proof of knowledge and transforms it into one which is secure against a concurrent man-in-the-middle attack (in the common reference string model).
- When using our specific implementations, this compiler is very efficient (requires no more than four exponentiations) and maintains the round complexity of the original proof of knowledge.
- The main practical applications of our results are concurrently secure identification protocols.
- For these applications our results are the first simple and efficient solutions based on the Strong RSA or Diffie-Hellman Assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/concpok-proc (1).pdf`
- `downloads/concpok-proc (2).pdf`
- `downloads/concpok-proc.pdf`
