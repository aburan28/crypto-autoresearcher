---
id: KN-LIT-f1073f
type: literature
title: "On breaking McEliece keys using brute force"
authors:
  - "Lorenz Panny"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/632"
  doi: "10.1007/978-3-032-22698-3_9"
  arxiv: null
  url: "https://eprint.iacr.org/2025/632"
tags: [code-based, mceliece, structural-attack, key-recovery, brute-force, key-space, goppa, concrete-security]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
On breaking McEliece keys by **brute force** — counting how large the effective
Goppa key space actually is, as opposed to how large the parameter description
suggests. Equivalent keys (Gibson, [[KN-LIT-3663ee]]) and symmetries reduce the
count.

## Key claims (as reported)
- An analysis of the true cost of brute-force key search against McEliece.

## Relevance to this program
The **baseline-reproduction** check, done for real. Section 8 of
`docs/inventor-protocol.md` (`KN-TECH-080`) requires a proof-oriented proposal
to establish the exact bottleneck and reproduce the trivial baseline before
anything expensive is approved — because the embarrassing outcome is a
sophisticated attack that fails to beat brute force honestly counted.

A 2025 paper still finding this question worth asking about a 1978 system is
good evidence the check is not pedantry.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/632 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-032-22698-3_9).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The counted key-space size and the resulting brute-force cost are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
