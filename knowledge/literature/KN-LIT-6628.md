---
id: KN-LIT-6628
type: literature
title: "SiGamal: A supersingular isogeny-based PKE and its application to a PRF"
authors:
  - "Tomoki Moriya"
  - "Hiroshi Onuki"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, isogeny, pqc, protocol, quantum, rsa, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose two new supersingular isogeny-based public key encryptions: SiGamal and C-SiGamal. They were developed by giving an additional point of the order 2r to CSIDH.

## Key claims (as reported)
- SiGamal is similar to ElGamal encryption, while C-SiGamal is a compressed version of SiGamal.
- We prove that SiGamal and C-SiGamal are IND-CPA secure without using hash functions under a new assumption: the P-CSSDDH assumption.
- This assumption comes from the expectation that no efficient algorithm can distinguish between a random point and a point that is the image of a public point under a hidden isogeny.
- Next, we propose a Naor-Reingold type pseudo random function (PRF) based on SiGamal.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491168 (1).pdf`
- `downloads/12491168.pdf`
