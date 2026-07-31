---
id: KN-LIT-2787
type: literature
title: "Break-glass Encryption"
authors:
  - "Alessandra Scafuro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
“Break-glass” is a term used in IT healthcare systems to denote an emergency access to private information without having the credentials to do so. In this paper we introduce the concept of break-glass encryption for cloud storage, where the security of the ciphertexts – stored on a cloud– can be violated exactly once, for emergency circumstances, in a way that is detectable and without relying on a trusted party.

## Key claims (as reported)
- Detectability is the crucial property here: if a cloud breaks glass without permission from the legitimate user, the latter should detect it and have a proof of such violation.
- However, if the break-glass procedure is invoked by the legitimate user, then semantic security must still hold and the cloud will learn nothing.
- Distinguishing that a break-glass is requested by the legitimate party is also challenging in absence of secrets.
- In this paper, we provide a formalization of break-glass encryption and a secure instantiation using hardware tokens.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420235 (1).pdf`
- `downloads/114420235.pdf`
