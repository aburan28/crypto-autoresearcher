---
id: KN-LIT-b2191d
type: literature
title: "Decoding linear codes with high error rate and its impact for LPN security"
authors:
  - "Leif Both"
  - "Alexander May"
year: 2018
venue: "PQCrypto"
identifiers:
  eprint: "iacr:2017/1139"
  doi: "10.1007/978-3-319-79063-3_2"
  arxiv: null
  url: "https://eprint.iacr.org/2017/1139"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, lpn, high-error-rate, bjmm]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Decoding linear codes at **high error rate**, with consequences for **LPN
security**. The standard ISD analysis targets the low-weight regime relevant to
McEliece; the high-error regime is the one that matters for Learning Parity with
Noise, and the algorithms that win there differ.

## Key claims (as reported)
- Improved decoding in the high-error-rate regime.
- Consequences drawn for LPN parameter security, not only for code-based encryption.

## Relevance to this program
Held for the **regime-dependence** point. The same problem — decode a linear
code — has a different best algorithm depending on the error weight, and an
algorithm optimal in one regime can be irrelevant in the other.

That is a direct warning against a failure mode this program can commit: taking
a solver benchmarked in one parameter regime and quoting its performance in
another. Every evidence record here is scoped to the parameters actually
tested (rule 4), and this paper is a concrete illustration of why that scoping
is not a formality.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2017/1139 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-319-79063-3_2).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The improved complexity and the LPN parameter consequences are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
