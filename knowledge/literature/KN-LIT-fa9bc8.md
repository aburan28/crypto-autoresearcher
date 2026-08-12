---
id: KN-LIT-fa9bc8
type: literature
title: "Analysis of information set decoding for a sub-linear error weight"
authors:
  - "Rodolfo Canto Torres"
  - "Nicolas Sendrier"
year: 2016
venue: "PQCrypto"
identifiers:
  eprint: null
  doi: "10.1007/978-3-319-29360-8_10"
  arxiv: null
  url: "https://hal.inria.fr/hal-01244886v1/document"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, asymptotics, sublinear-weight, prange]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Analyses ISD in the **sub-linear error weight** regime — where the number of
errors grows more slowly than the code length, which is the regime Goppa-code
McEliece actually lives in (`t ≈ n / log n`), as opposed to the constant-rate
regime most asymptotic analyses assume.

## Key claims (as reported)
- In the sub-linear weight regime, the asymptotic advantage of advanced ISD variants over Prange's original algorithm largely disappears.
- The analysis is asymptotic and specific to sub-linear `t`.

## Relevance to this program
One of the most consequential entries in this sweep, and the reason it is worth
holding the older ISD literature at all. It says that in **the regime McEliece
actually uses**, fifty years of ISD refinement asymptotically collapses back
toward Prange.

The general form of that lesson is directly binding on this program: an
algorithmic advantage measured in one asymptotic regime **may vanish in the
regime the cryptosystem occupies**, so a speedup must be demonstrated at the
parameters in question, not at the parameters where the analysis is convenient.
This is rule 4 with a published counterexample attached.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-319-29360-8_10).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The precise statement of the collapse, and whether it holds concretely as well
as asymptotically, are NOT recorded here — the concrete gains at real parameters
are real and measurable ([[KN-LIT-6923]]) even where the asymptotics converge.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
