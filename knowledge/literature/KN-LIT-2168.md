---
id: KN-LIT-2168
type: literature
title: "A Note on Non-Interactive Zero-Knowledge from CDH"
authors:
  - "Geoffroy Couteau"
  - "Abhishek Jain"
  - "Zhengzhong Jin"
  - "Willy Quach"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We build non-interactive zero-knowledge (NIZK) and ZAP arguments for all NP where soundness holds for infinitely-many security parameters, and against uniform adversaries, assuming the subexponential hardness of the Computational Diffie-Hellman (CDH) assumption. We additionally prove the existence of NIZK arguments with these same properties assuming the polynomial hardness of both CDH and the Learning Parity with Noise (LPN) assumption.

## Key claims (as reported)
- In both cases, the CDH assumption does not require a group equipped with a pairing.
- Infinitely-often uniform security is a standard byproduct of commonly used non-black-box techniques that build on disjunction arguments on the (in)security of some primitive.
- In the course of proving our results, we develop a new variant of this non-black-box technique that yields improved guarantees: we obtain explicit constructions (previous works generally only obtained existential results) where security holds for a relatively dense set of security parameters (as opposed to an arbitrary infinite set of security parameters).
- We demonstrate that our technique can have applications beyond our main results.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850426 (1).pdf`
- `downloads/140850426.pdf`
