---
id: KN-LIT-2919
type: literature
title: "Classical vs Quantum Random Oracles"
authors:
  - "Takashi Yamakawa"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study relationship between security of cryptographic schemes in the random oracle model (ROM) and quantum random oracle model (QROM). First, we introduce a notion of a proof of quantum access to a random oracle (PoQRO), which is a protocol to prove the capability to quantumly access a random oracle to a classical verifier.

## Key claims (as reported)
- We observe that a proof of quantumness recently proposed by Brakerski et al.
- (TQC ’20) can be seen as a PoQRO.
- We also give a construction of a publicly verifiable PoQRO relative to a classical oracle.
- Based on them, we construct digital signature and public key encryption schemes that are secure in the ROM but insecure in the QROM.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960137 (1).pdf`
- `downloads/126960137.pdf`
