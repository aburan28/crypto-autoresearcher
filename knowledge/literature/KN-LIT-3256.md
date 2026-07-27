---
id: KN-LIT-3256
type: literature
title: "Cryptanalysis of SFLASH"
authors:
  - "Henri Gilbert"
  - "Marine Minier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, ecdsa, finite-field, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SFLASH [Spec] is a fast asymmetric signature scheme intended for low cost smart cards without cryptoprocessor. It belongs to the family of multivariate asymmetric schemes.

## Key claims (as reported)
- It was submitted to the call for cryptographic primitives organised by the European project NESSIE, and successfully passed the first phase of the NESSIE selection process in September 2001.
- In this paper, we present a cryptanalysis of SFLASH which allows an adversary provided with an SFLASH public key to derive a valid signature of any message.
- The complexity of the attack is equivalent to less than 238 computations of the public function used for signature verification.
- The attack does not appear to be applicable to the FLASH companion algorithm of SFLASH and to the modified (more conservative) version of SFLASH proposed in October 2001 to the NESSIE project by the authors of SFLASH in replacement of [Spec].

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/cryptanalysisofsflash_vf (1).pdf`
- `downloads/cryptanalysisofsflash_vf (2).pdf`
- `downloads/cryptanalysisofsflash_vf.pdf`
