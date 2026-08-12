---
id: KN-LIT-2572
type: literature
title: "Arithmetic Operators for Pairing-Based Cryptography"
authors:
  - "Jean-Luc Beuchat"
  - "Nicolas Brisebarre"
  - "Jérémie Detrey"
  - "Eiji Okamoto"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, extension-field, finite-field, implementation, pairing, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since their introduction in constructive cryptographic applications, pairings over (hyper)elliptic curves are at the heart of an ever increasing number of protocols. Software implementations being rather slow, the study of hardware architectures became an active research area.

## Key claims (as reported)
- In this paper, we first study an accelerator for the ηT pairing over F3 [x]/(x97 + x12 + 2).
- Our architecture is based on a unified arithmetic operator which performs addition, multiplication, and cubing over F397 .
- This design methodology allows us to design a compact coprocessor (1888 slices on a Virtex-II Pro 4 FPGA) which compares favorably with other solutions described in the open literature.
- We then describe ways to extend our approach to any characteristic and any extension field.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270239 (1).pdf`
- `downloads/47270239 (2).pdf`
- `downloads/47270239 (3).pdf`
- `downloads/47270239.pdf`
