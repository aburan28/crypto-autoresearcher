---
id: KN-LIT-3395
type: literature
title: "Designated-verifier pseudorandom generators, and their applications"
authors:
  - "Geoffroy Couteau"
  - "Dennis Hofheinz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, fhe, lattice, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a generic construction of non-interactive zeroknowledge (NIZK) schemes. Our construction is a refinement of Dwork and Naor’s (FOCS 2000) implementation of the hidden bits model using verifiable pseudorandom generators (VPRGs).

## Key claims (as reported)
- Our refinement simplifies their construction and relaxes the necessary assumptions considerably.
- As a result of this conceptual improvement, we obtain interesting new instantiations: – A designated-verifier NIZK (with unbounded soundness) based on the computational Diffie-Hellman (CDH) problem.
- If a pairing is available, this NIZK becomes publicly verifiable.
- This constitutes the first fully secure CDH-based designated-verifier NIZKs (and more generally, the first fully secure designated-verifier NIZK from a nongeneric assumption which does not already imply publicly-verifiable NIZKs), and it answers an open problem recently raised by Kim and Wu (CRYPTO 2018). – A NIZK based on the learning with errors (LWE) assumption, and assuming a non-interactive witness-indistinguishable (NIWI) proof system for bounded distance decoding (BDD).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760195 (1).pdf`
- `downloads/114760195.pdf`
