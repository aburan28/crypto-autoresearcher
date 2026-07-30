---
id: KN-LIT-2068
type: literature
title: "A Generic Construction of Tightly Secure Password-based Authenticated Key Exchange"
authors:
  - "Jiaxin Pan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pqc, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a generic construction of password-based authenticated key exchange (PAKE) from key encapsulation mechanisms (KEM). Assuming that the KEM is oneway secure against plaintextcheckable attacks (OW-PCA), we prove that our PAKE protocol is tightly secure in the Bellare-Pointcheval-Rogaway model (EUROCRYPT 2000).

## Key claims (as reported)
- Our tight security proofs require ideal ciphers and random oracles.
- The OW-PCA security is relatively weak and can be implemented tightly with the Diffie-Hellman assumption, which generalizes the work of Liu et al.
- (PKC 2023), and “almost” tightly with lattice-based assumptions, which tightens the security loss of the work of Beguinet et al.
- (ACNS 2023) and allows more efficient practical implementation with Kyber.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438390 (1).pdf`
- `downloads/14438390.pdf`
