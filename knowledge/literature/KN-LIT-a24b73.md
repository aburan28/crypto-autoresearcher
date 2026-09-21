---
id: KN-LIT-a24b73
type: literature
title: "Triple Cryptanalysis of Isogeny-Based VRFs from Asiacrypt 2025"
authors:
  - "Yi-Fu Lai"
  - "Yu Yu"
  - "Xiaogang Zhou"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1623"
identifiers:
  eprint: iacr:2026/1623
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1623"
tags: [vrf, isogeny, cgl, radical-isogenies, cryptanalysis, unique-provability]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Presents a two-stage attack on the Levin–Pedersen verifiable random function
(VRF) from Asiacrypt 2025, which uses a CGL-analog hash function built from
radical isogenies and an R1CS proof binding the secret radical-CGL walk applied
to a public curve and to a message-dependent curve. Stage one exploits an
unspecified representation of the public key (j-invariant vs two coefficients)
to produce two distinct VRF outputs under the same public key and message,
breaking unique provability. Stage two exploits the coefficient representation
to recover the VRF secret key (256-bit) with 1536 queries in about 30 minutes.

## Key claims (as reported)
- The representation mismatch breaks unique-provability: two outputs under same
  key and message.
- Full key recovery: 1536 queries, ~30 min, on the concrete Asiacrypt-2025 VRF
  parameters.
- Lessons for isogeny-based VRF design: radical-isogeny walks + R1CS are not
  enough; the representation gap is the real attack surface.

## Relevance
- Not directly ECDLP-exponent, but an empirical result for isogeny-based
  constructions (CGL-family) that the corpus tracks. It shows that
  "radical-isogeny walks + NIZK proof of same secret" carries subtle
  representation pitfalls, which a future design in the isogeny area must
  avoid. Low value for ECDLP exponent claims; moderate for isogeny-based
  crypto novelty checks.

## Not verified here
- The 1536-query / 30-minute cost claimed in abstract not independently
  measured here. Implementation artifacts not examined.