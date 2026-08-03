---
id: KN-LIT-e800e6
type: literature
title: "A key-recovery side-channel attack on Classic McEliece implementations"
authors:
  - "Qian Guo"
  - "Andreas Johansson"
  - "Thomas Johansson"
year: 2022
venue: "CHES"
identifiers:
  eprint: "iacr:2022/514"
  doi: "10.46586/tches.v2022.i4.800-827"
  arxiv: null
  url: "https://doi.org/10.46586/tches.v2022.i4.800-827"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, key-recovery, reference-implementation, practical]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A key-recovery side-channel attack on **Classic McEliece implementations** —
CHES 2022, one of the earlier full key-recovery results against the
specification's own implementations and a reference point for the cluster that
followed.

## Key claims (as reported)
- Full secret key recovery from side-channel measurements.
- Targets actual implementations of the submission, not a model of them.

## Relevance to this program
Attacking the **shipped implementation** rather than an abstraction is what
makes a physical-security result actionable, and it is why this paper anchors
the cluster.

The parallel obligation in this program is that experiments run the artifact
that is actually declared and archived — which is what the dispatcher's
post-commit verifier checks by binding archive receipts to content hashes.
A result about code that is not the code in the archive is not evidence about
the archive.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/514 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.46586/tches.v2022.i4.800-827).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Trace requirements, target platform and success rate are NOT recorded here.
Note: the corpus entry [[KN-LIT-6621]] surfaced in an automated fragment match
against this title but is an unrelated paper on static-power leakage; separated
by hand during dedup.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
