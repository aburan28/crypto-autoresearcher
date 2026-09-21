---
id: KN-LIT-3817
type: literature
title: "Fast, Compact, and Expressive Attribute-Based Encryption"
authors:
  - "Junichi Tomida"
  - "Yuto Kawahara"
  - "Ryo Nishimaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Attribute-based encryption (ABE) is an advanced cryptographic tool and useful to build various types of access control systems. Toward the goal of making ABE more practical, we propose key-policy (KP) and ciphertext-policy (CP) ABE schemes, which first support unbounded sizes of attribute sets and policies with negation and multi-use of attributes, allow fast decryption, and are adaptively secure under a standard assumption, simultaneously.

## Key claims (as reported)
- Our schemes are more expressive than previous schemes and efficient enough.
- To achieve the adaptive security along with the other properties, we refine the technique introduced by Kowalczyk and Wee (Eurocrypt’19) so that we can apply the technique more expressive ABE schemes.
- Furthermore, we also present a new proof technique that allows us to remove redundant elements used in their ABE schemes.
- We implement our schemes in 128-bit security level and present their benchmarks for an ordinary personal computer and smartphones.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110144 (1).pdf`
- `downloads/12110144.pdf`
