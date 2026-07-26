---
id: KN-LIT-4721
type: literature
title: "Lightweight Coprocessor for Koblitz Curves: 283-bit ECC Including Scalar Conversion with only 4300 Gates"
authors:
  - "Sujoy Sinha Roy"
  - "Kimmo Järvinen"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, elliptic-curve, implementation, side-channel, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a lightweight coprocessor for 16-bit microcontrollers that implements high security elliptic curve cryptography. It uses a 283-bit Koblitz curve and offers 140-bit security.

## Key claims (as reported)
- Koblitz curves offer fast point multiplications if the scalars are given as specific τ -adic expansions, which results in a need for conversions between integers and τ -adic expansions.
- We propose the first lightweight variant of the conversion algorithm and, by using it, introduce the first lightweight implementation of Koblitz curves that includes the scalar conversion.
- We also include countermeasures against side-channel attacks making the coprocessor the first lightweight coprocessor for Koblitz curves that includes a set of countermeasures against timing attacks, SPA, DPA and safe-error fault attacks.
- When the coprocessor is synthesized for 130 nm CMOS, it has an area of only 4,323 GE.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930100 (1).pdf`
- `downloads/92930100.pdf`
