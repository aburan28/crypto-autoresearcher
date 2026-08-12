---
id: KN-LIT-bb53c1
type: literature
title: "A non asymptotic analysis of information set decoding"
authors:
  - "Yann Hamdaoui"
  - "Nicolas Sendrier"
year: 2013
venue: null
identifiers:
  eprint: "iacr:2013/162"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2013/162"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, non-asymptotic, concrete-security, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **non-asymptotic** analysis of information set decoding: exact rather than
`O`-notation cost accounting for ISD, so that the numbers can be used for
parameter selection instead of only for comparing algorithm families.

## Key claims (as reported)
- Explicit non-asymptotic cost expressions for ISD.
- Aimed at parameter selection, where asymptotic exponents are not sufficient.

## Relevance to this program
Held as an early instance of a discipline this corpus values highly and this
program is bound by: **asymptotics do not select parameters; counted operations
do.** Finiasz–Sendrier ([[KN-LIT-6503]]) and later the Syndrome Decoding
Estimator ([[KN-LIT-6923]]) are the same tradition made systematic.

The direct analogue for this program is that a claimed ECDLP cost must be
expressed in a model where it can be counted and re-checked, not in an
asymptotic form that hides the constants a real attack pays.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2013/162 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The cost expressions and their agreement with experiment are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
