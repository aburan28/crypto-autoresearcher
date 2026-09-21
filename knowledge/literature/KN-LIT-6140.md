---
id: KN-LIT-6140
type: literature
title: "Range Extension for Weak PRFs; The Good, the Bad, and the Ugly"
authors:
  - "Krzysztof Pietrzak"
  - "Johan Sjödin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate a general class of (black-box) constructions for range extension of weak pseudorandom functions: a construction based on m independent functions F1 , . . . , Fm is given by a set of strings over {1, . . . , m}∗ , where for example {h2i, h1, 2i} corresponds to the function X 7→ [F2 (X), F2 (F1 (X))]. All efficient constructions for range expansion of weak pseudorandom functions that we are aware of are of this form.

## Key claims (as reported)
- We completely classify such constructions as good, bad or ugly, where the good constructions are those whose security can be proven via a blackbox reduction, the bad constructions are those whose insecurity can be proven via a black-box reduction, and the ugly constructions are those which are neither good nor bad.
- Our classification shows that the range expansion from [10] is optimal, in the sense that it achieves the best possible expansion (2m − 1 when using m keys).
- Along the way we show that for weak quasirandom functions (i.e. in the information theoretic setting), all constructions which are not bad – in particular all the ugly ones – are secure.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150517 (1).pdf`
- `downloads/45150517 (2).pdf`
- `downloads/45150517 (3).pdf`
- `downloads/45150517.pdf`
