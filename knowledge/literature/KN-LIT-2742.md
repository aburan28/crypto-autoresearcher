---
id: KN-LIT-2742
type: literature
title: "Blind Schnorr Signatures and Signed ElGamal Encryption in the Algebraic Group Model"
authors:
  - "Georg Fuchsbauer"
  - "Antoine Plouviez"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, hash, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Schnorr blind signing protocol allows blind issuing of Schnorr signatures, one of the most widely used signatures. Despite its practical relevance, its security analysis is unsatisfactory.

## Key claims (as reported)
- The only known security proof is informal and in the combination of the generic group model (GGM) and the random oracle model (ROM) assuming that the “ROS problem” is hard.
- The situation is similar for (Schnorr-)signed ElGamal encryption, a simple CCA2-secure variant of ElGamal.
- We analyze the security of these schemes in the algebraic group model (AGM), an idealized model closer to the standard model than the GGM.
- We first prove tight security of Schnorr signatures from the discrete logarithm assumption (DL) in the AGM+ROM.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105250 (1).pdf`
- `downloads/12105250.pdf`
