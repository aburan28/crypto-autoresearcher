---
id: KN-LIT-5044
type: literature
title: "Multipurpose Identity-Based Signcryption A Swiss Army Knife for Identity-Based Cryptography Xavier Boyen"
authors:
  - "Palo Alto"
  - "California — crypto@boyen.org"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, lattice, pairing, protocol, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Identity-Based (IB) cryptography is a rapidly emerging approach to public-key cryptography that does not require principals to pre-compute key pairs and obtain certificates for their public keys— instead, public keys can be arbitrary identifiers such as email addresses, while private keys are derived at any time by a trusted private key generator upon request by the designated principals. Despite the flurry of recent results on IB encryption and signature, some questions regarding the security and efficiency of practicing IB encryption (IBE) and signature (IBS) as a joint IB signature/encryption (IBSE) scheme with a common set of parameters and keys, remain unanswered.

## Key claims (as reported)
- We first propose a stringent security model for IBSE schemes.
- We require the usual strong security properties of: (for confidentiality) indistinguishability against adaptive chosen-ciphertext attacks, and (for nonrepudiation) existential unforgeability against chosen-message insider attacks.
- In addition, to ensure as strong as possible ciphertext armoring, we also ask (for anonymity) that authorship not be transmitted in the clear, and (for unlinkability) that it remain unverifiable by anyone except (for authentication) by the legitimate recipient alone.
- We then present an efficient IBSE construction, based on bilinear pairings, that satisfies all these security requirements, and yet is as compact as pairing-based IBE and IBS in isolation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290382 (1).pdf`
- `downloads/27290382 (2).pdf`
- `downloads/27290382.pdf`
