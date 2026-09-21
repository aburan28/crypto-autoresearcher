---
id: KN-LIT-4195
type: literature
title: "Hierarchical Identity Based Encryption with Polynomially Many Levels"
authors:
  - "Craig Gentry (Stanford & IBM)"
  - "Shai Halevi (IBM)"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first hierarchical identity based encryption (HIBE) system that has full security for more than a constant number of levels. In all prior HIBE systems in the literature, the security reductions suffered from exponential degradation in the depth of the hierarchy, so these systems were only proven fully secure for identity hierarchies of constant depth.

## Key claims (as reported)
- (For deep hierarchies, previous work could only prove the weaker notion of selective-ID security.) In contrast, we offer a tight proof of security, regardless of the number of levels; hence our system is secure for polynomially many levels.
- Our result can very roughly be viewed as an application of Boyen’s framework for constructing HIBE systems from exponent-inversion IBE systems to a (dramatically souped-up) version of Gentry’s IBE system, which has a tight reduction.
- In more detail, we first describe a generic transformation from “identity based broadcast encryption with key randomization” (KR-IBBE) to a HIBE, and then construct KR-IBBE by modifying a recent construction of IBBE of Gentry and Waters, which is itself an extension of Gentry’s IBE system.
- Our hardness assumption is similar to that underlying Gentry’s IBE system.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54440436 (1).pdf`
- `downloads/54440436 (2).pdf`
- `downloads/54440436 (3).pdf`
- `downloads/54440436.pdf`
