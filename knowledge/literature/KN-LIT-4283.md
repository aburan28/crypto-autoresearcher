---
id: KN-LIT-4283
type: literature
title: "How to Fool an Unbounded Adversary with a Short Key"
authors:
  - "Alexander Russell"
  - "Hong Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the symmetric encryption problem which manifests when two parties must securely transmit a message m with a short shared secret key. As we permit arbitrarily powerful adversaries, any encryption scheme must leak information about m—the mutual information between m and its ciphertext cannot be zero.

## Key claims (as reported)
- Despite this, we present a family of encryption schemes which guarantee that for any message space in {0, 1}n with minimum entropy n − ` and for any Boolean function h : {0, 1}n → {0, 1}, no adversary can predict h(m) from the ciphertext of m with more than 1/nω(1) advantage; this is achieved with keys of length `+ω(log n).
- In general, keys of length `+s yield a bound of 2−Θ(s) on the advantage.
- These encryption schemes rely on no unproven assumptions and can be implemented efficiently.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/encryption-euro-final (1).pdf`
- `downloads/encryption-euro-final (2).pdf`
- `downloads/encryption-euro-final.pdf`
