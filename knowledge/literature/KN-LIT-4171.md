---
id: KN-LIT-4171
type: literature
title: "Hash-Function based PRFs: AMAC and its Multi-User Security"
authors:
  - "Mihir Bellare"
  - "Daniel J. Bernstein"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
AMAC is a simple and fast candidate construction of a PRF from an MD-style hash function which applies the keyed hash function and then a cheap, un-keyed output transform such as truncation. Spurred by its use in the widely-deployed Ed25519 signature scheme, this paper investigates the provable PRF security of AMAC to deliver the following three-fold message: (1) First, we prove PRF security of AMAC.

## Key claims (as reported)
- (2) Second, we show that AMAC has a quite unique and attractive feature, namely that its multi-user security is essentially as good as its single-user security and in particular superior in some settings to that of competitors.
- (3) Third, it is technically interesting, its security and analysis intrinsically linked to security of the compression function in the presence of leakage.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650182 (1).pdf`
- `downloads/96650182.pdf`
