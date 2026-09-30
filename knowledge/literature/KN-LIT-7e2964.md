---
id: KN-LIT-7e2964
type: literature
title: "Non-uniform Cracks in the Concrete: The Power of Free Precomputation"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: 2013
venue: "ASIACRYPT 2013, LNCS 8270, pp. 321-340; ePrint 2012/318"
identifiers:
  eprint: "iacr:2012/318"
  arxiv: null
  doi: "10.1007/978-3-642-42045-0_17"
  url: null
tags: [pollard-rho, precomputation, non-uniform, security-definitions, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Shows that, with unlimited free precomputation, high-probability attack algorithms exist against NIST P-256 (and AES-128, DSA-3072, RSA-3072) far below 2^128 "time". This breaks the standard definition of 2^b security without any practical threat. Motivates the S-T trade-off lower bounds of Corrigan-Gibbs-Kogan.

## Key claims (as reported)

- Existential P-256 attack well below 2^128 online time (exact exponents not re-extracted).

## Relevance to this program

Free-precomputation attacks break the naive reading of concrete security bounds (including ECDLP with l^{1/3}-time online after l^{2/3} precomputation). Context for any precomputation-rho claim and for Corrigan-Gibbs–Kogan's lower bound.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-5230 (bulk stub or misattributed entry; see that file's `superseded_by`).
