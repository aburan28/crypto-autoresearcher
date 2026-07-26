---
id: KN-LIT-6577
type: literature
title: "Short Chosen-Prefix Collisions for MD5 and the Creation of a Rogue CA Certificate"
authors:
  - "Marc Stevens"
  - "Alexander Sotirov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, hash, mov-fr, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a refined chosen-prefix collision construction for MD5 that allowed creation of a rogue Certification Authority (CA) certificate, based on a collision with a regular end-user website certificate provided by a commercial CA. Compared to the previous construction from Eurocrypt 2007, this paper describes a more flexible family of differential paths and a new variable birthdaying search space.

## Key claims (as reported)
- Combined with a time-memory trade-off, these improvements lead to just three pairs of near-collision blocks to generate the collision, enabling construction of RSA moduli that are sufficiently short to be accepted by current CAs.
- The entire construction is fast enough to allow for adequate prediction of certificate serial number and validity period: it can be made to require about 249 MD5 compression function calls.
- Finally, we improve the complexity of identical-prefix collisions for MD5 to about 216 MD5 compression function calls and use it to derive a practical single-block chosen-prefix collision construction of which an example is given.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770054 (1).pdf`
- `downloads/56770054 (2).pdf`
- `downloads/56770054 (3).pdf`
- `downloads/56770054.pdf`
