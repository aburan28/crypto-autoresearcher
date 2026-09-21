---
id: KN-LIT-3643
type: literature
title: "Efficient Universal Padding Techniques for Multiplicative Trapdoor One-way Permutation"
authors:
  - "Yuichi Komano"
  - "Kazuo Ohta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Coron et al. proposed the ES-based scheme PSS-ES which realizes an encryption scheme and a signature scheme with a unique padding technique and key pair. The security of PSS-ES as an encryption scheme is based on the partial-domain one-wayness of the encryption permutation.

## Key claims (as reported)
- In this paper, we propose new ES schemes OAEP-ES, OAEP++-ES, and REACT-ES, and prove their security under the assumption of only the one-wayness of encryption permutation.
- OAEP-ES, OAEP++-ES, and REACT-ES suit practical implementation because they use the same padding technique for encryption and for signature, and their security proof guarantees that we can prepare one key pair to realize encryption and signature in the same way as PSS-ES.
- Since one-wayness is a weaker assumption than partial-domain one-wayness, the proposed schemes offer tighter security than PSS-ES.
- Hence, we conclude that OAEP-ES, OAEP++-ES, and REACT-ES are more effective than PSS-ES.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290365 (1).pdf`
- `downloads/27290365 (2).pdf`
- `downloads/27290365.pdf`
