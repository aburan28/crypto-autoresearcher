---
id: KN-LIT-4854
type: literature
title: "Masking AES with d +"
authors:
  - "Ventzislav Nikov"
  - "Vincent Rijmen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, implementation, mpc, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking requires splitting sensitive variables into at least d + 1 shares to provide security against DPA attacks at order d. To this date, this minimal number has only been deployed in software implementations of cryptographic algorithms and in the linear parts of their hardware counterparts.

## Key claims (as reported)
- So far there is no hardware construction that achieves this lower bound if the function is nonlinear and the underlying logic gates can glitch.
- In this paper, we give practical implementations of the AES using d + 1 shares aiming at first- and second-order security even in the presence of glitches.
- To achieve this, we follow the conditions presented by Reparaz et al. at CRYPTO 2015 to allow hardware masking schemes, like Threshold Implementations, to provide theoretical higher-order security with d + 1 shares.
- The decrease in number of shares has a direct impact in the area requirements: our second-order DPA resistant core is the smallest in area so far, and its S-box is 50% smaller than the current smallest Threshold Implementation of the AES S-box with similar security and attacker model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130170 (1).pdf`
- `downloads/98130170.pdf`
