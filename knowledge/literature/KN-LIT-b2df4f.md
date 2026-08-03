---
id: KN-LIT-b2df4f
type: literature
title: "Multiparallel MMT: faster ISD algorithm solving high-dimensional syndrome decoding problem"
authors:
  - "Shintaro Narisada"
  - "Kazuhide Fukushima"
  - "Shinsaku Kiyomoto"
year: 2023
venue: "IEICE Transactions on Fundamentals of Electronics, Communications and Computer Sciences"
identifiers:
  eprint: null
  doi: "10.1587/transfun.2022cip0023"
  arxiv: null
  url: "https://www.jstage.jst.go.jp/article/transfun/advpub/0/advpub_2022CIP0023/_pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, mmt, parallel, implementation, record]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **multiparallel implementation of MMT** ([[KN-LIT-3368]]) aimed at solving
high-dimensional syndrome decoding instances — engineering rather than a new
algorithm, in the line that produced the McEliece-1284 and McEliece-1409 records
([[KN-LIT-4875]], [[KN-LIT-1302]]).

## Key claims (as reported)
- A faster MMT-based syndrome decoding solver through parallelisation.
- Targeted at high-dimensional instances, i.e. at pushing the record frontier rather than at asymptotic improvement.

## Relevance to this program
This is the corpus's clearest example of the **record-attempt genre**, which
this program itself practices: take a known algorithm, engineer it hard, and
solve the largest instance you can. Two disciplines from that genre are binding
here — the solved instance is a certificate that can be checked independently
(`docs/claims-and-verification.md`), and the result is scoped to the dimension
actually solved, never extrapolated to parameters that were not attempted.

**Does not bear on the ECDLP**, though the record-attempt discipline is
identical for discrete-log challenge instances.

## Not verified here
citation verified against the Crossref record (DOI 10.1587/transfun.2022cip0023).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The dimensions reached, the hardware used, and the speedup over serial MMT are
NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
