---
id: KN-LIT-4811
type: literature
title: "Lower Bounds in the Hardware Token Model"
authors:
  - "Shashank Agrawal"
  - "Prabhanjan Ananth"
  - "Vipul Goyal"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the complexity of secure computation in the tamperproof hardware token model. Our main focus is on non-interactive unconditional two-party computation using bit-OT tokens, but we also study computational security with stateless tokens that have more complex functionality.

## Key claims (as reported)
- Our results can be summarized as follows: – There exists a class of functions such that the number of bit-OT tokens required to securely implement them is at least the size of the sender’s input.
- The same applies for receiver’s input size (with a different class of functionalities). – Non-adaptive protocols in the hardware token model imply efficient (decomposable) randomized encodings.
- This can be interpreted as evidence to the impossibility of non-adaptive protocols for a large class of functions. – There exists a functionality for which there is no protocol in the stateless hardware token model accessing the tokens at most a constant number of times, even when the adversary is computationally bounded.
- En route to proving our results, we make interesting connections between the hardware token model and well studied notions such as OT hybrid model, randomized encodings and obfuscation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83490176 (1).pdf`
- `downloads/83490176 (2).pdf`
- `downloads/83490176 (3).pdf`
- `downloads/83490176.pdf`
