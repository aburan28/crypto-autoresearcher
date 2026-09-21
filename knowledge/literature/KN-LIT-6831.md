---
id: KN-LIT-6831
type: literature
title: "Stronger Security and Constructions of Multi-Designated Verifier Signatures ? Ivan Damgård1 , Helene Haagh12"
authors:
  - "Anca Nitulescu"
  - "Claudio Orlandi"
  - "Sophia Yakoubov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Off-the-Record (OTR) messaging is a two-party message authentication protocol that also provides plausible deniability: there is no record that can later convince a third party what messages were actually sent. The challenge in group OTR, is to enable the sender to sign his messages so that group members can verify who sent a message (signatures should be unforgeable, even by group members).

## Key claims (as reported)
- Also, we want the off-the-record property: even if some verifiers are corrupt and collude, they should not be able to prove the authenticity of a message to any outsider.
- Finally, we need consistency, meaning that if any group member accepts a signature, then all of them do.
- To achieve these properties it is natural to consider Multi-Designated Verifier Signatures (MDVS).
- However, existing literature defines and builds only limited notions of MDVS, where (a) the off-the-record property (source hiding) only holds when all verifiers could conceivably collude, and (b) the consistency property is not considered.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550162 (1).pdf`
- `downloads/12550162.pdf`
