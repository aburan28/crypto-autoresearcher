---
id: KN-LIT-2944
type: literature
title: "Collision Attacks on Up to 5 Rounds of SHA-3 Using Generalized Internal Differentials"
authors:
  - "Itai Dinur"
  - "Orr Dunkelman"
  - "Adi Shamir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
On October 2-nd 2012 NIST announced its selection of the Keccak scheme as the new SHA-3 hash standard. In this paper we present the first published collision finding attacks on reduced-round versions of Keccak-384 and Keccak-512, providing actual collisions for 3-round versions, and describing an attack which is 245 times faster than birthday attacks for 4-round Keccak-384.

## Key claims (as reported)
- For Keccak-256, we increase the number of rounds which can be attacked to 5.
- All these results are based on a generalized internal differential attack (introduced by Peyrin at Crypto 2010), and use it to map a large number of Keccak inputs into a relatively small subset of possible outputs with a surprisingly large probability.
- In such a squeeze attack it is easier to find random collisions in the reduced target subset by a standard birthday argument.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240206 (1).pdf`
- `downloads/84240206 (2).pdf`
- `downloads/84240206 (3).pdf`
- `downloads/84240206.pdf`
