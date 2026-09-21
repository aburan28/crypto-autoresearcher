---
id: KN-LIT-1630
type: literature
title: "ECCFROG522PP: An Enhanced 522 bit Weierstrass"
authors:
  - "Elliptic Curve"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2604.21261"
  url: "https://arxiv.org/abs/2604.21261"
tags: [complexity-theory, curve-arithmetic, elliptic-curve, prime-field, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents ECCFROG522PP, a 522 bit elliptic curve over a prime field in short Weierstrass form, designed around a simple principle: every critical parameter should be publicly reproducible from a fixed seed by a deterministic procedure. Many deployed systems still rely on NIST P 256 and secp256k1, which sit near the 128 bit classical security level.

## Key claims (as reported)
- At higher security levels, practitioners usually consider NIST P 521, Curve448, and Brainpool P512.
- ECCFROG522PP is intended for the same general classical security range as P 521 while emphasizing transparency, verifiability, and auditability rather than speed.
- The curve parameters are derived from a fixed public seed through a BLAKE3 based pipeline with published indices.
- The resulting curve has prime order, cofactor one, a deterministically validated base point, a quadratic twist with a large proven prime factor, a published embedding degree lower bound, and basic sanity checks against small embedding degree reductions and low bound CM anomalies.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2604.21261v1 (1).pdf`
- `downloads/2604.21261v1.pdf`
