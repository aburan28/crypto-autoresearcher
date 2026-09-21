---
id: KN-LIT-3832
type: literature
title: "Faster discrete logarithms on"
authors:
  - "Christof Paar"
  - "Peter Schwabe"
  - "Ralf Zimmermann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, dlp, ecdlp, elliptic-curve, hyperelliptic, implementation, mov-fr, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper accelerates FPGA computations of discrete logarithms on elliptic curves over binary fields. As an illustration, this paper reports successful completion of an attack against the SECG standard curve sect113r2, a binary elliptic curve that was not removed from the standard until 2010 and was not disabled in OpenSSL until June 2015.

## Key claims (as reported)
- This is a new size record for ECDL computations, using a prime order very slightly larger than the previous record holder.
- More importantly, this paper uses FPGAs much more efficiently, saving a factor close to 3/2 in the size of each high-speed ECDL core and allowing 3 cores to be squeezed into a low-cost Spartan-6 FPGA.
- The paper also covers much larger curves over 127-bit fields.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/sect113r2-20160414.pdf`
