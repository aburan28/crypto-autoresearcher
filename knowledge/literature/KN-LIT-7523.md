---
id: KN-LIT-7523
type: literature
title: "Witness Encryption from Instance Independent Assumptions"
authors:
  - "Craig Gentry"
  - "Allison Lewko"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Witness encryption was proposed by Garg, Gentry, Sahai, and Waters as a means to encrypt to an instance, x, of an NP language and produce a ciphertext. In such a system, any decryptor that knows of a witness w that x is in the language can decrypt the ciphertext and learn the message.

## Key claims (as reported)
- In addition to proposing the concept, their work provided a candidate for a witness encryption scheme built using multilinear encodings.
- However, one significant limitation of the work is that the candidate had no proof of security (other than essentially assuming the scheme secure).
- In this work we provide a proof framework for proving witness encryption schemes secure under instance independent assumptions.
- At the highest level we introduce the abstraction of positional witness encryption which allows a proof reduction of a witness encryption scheme via a sequence of 2n hybrid experiments where n is the witness length of the NP-statement.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160226 (1).pdf`
- `downloads/86160226 (2).pdf`
- `downloads/86160226 (3).pdf`
- `downloads/86160226 (4).pdf`
- `downloads/86160226 (5).pdf`
- `downloads/86160226.pdf`
