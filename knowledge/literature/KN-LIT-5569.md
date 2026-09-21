---
id: KN-LIT-5569
type: literature
title: "On the Security of Dynamic Group Signatures: Preventing Signature Hijacking Yusuke Sakai1? , Jacob C. N. Schuldt2?? , Keita Emura3? ? ?"
authors:
  - "Goichiro Hanaoka"
  - "Kazuo Ohta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We identify a potential weakness in the standard security model for dynamic group signatures which appears to have been overlooked previously. More specifically, we highlight that even if a scheme provably meets the security requirements of the model, a malicious group member can potentially claim ownership of a group signature produced by an honest group member by forging a proof of ownership.

## Key claims (as reported)
- This property leads to a number of vulnerabilities in scenarios in which dynamic group signatures are likely to be used.
- We furthermore show that the currently most efficient dynamic group signature scheme does not provide protection against this type of malicious behavior.
- To address this, we introduce the notion of opening soundness for group signatures which essentially requires that it is infeasible to produce a proof of ownership of a valid group signature for any user except the original signer.
- We then show a relatively simple modification of the scheme by Groth (ASIACRYPT 2007, full version) which allows us to prove opening soundness for the modified scheme without introducing any additional assumptions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930715 (1).pdf`
- `downloads/72930715 (2).pdf`
- `downloads/72930715 (3).pdf`
- `downloads/72930715.pdf`
