---
id: KN-LIT-082ca9
type: literature
title: "The giant footprint is the smallest: low-footprint decryption of Classic McEliece"
authors:
  - "Cong Liu"
  - "Naoto Yanai"
  - "Naohisa Nishida"
  - "Akira Maruko"
year: 2025
venue: "CSP"
identifiers:
  eprint: null
  doi: "10.1109/csp66295.2025.00011"
  arxiv: null
  url: "https://ieeexplore.ieee.org/abstract/document/11141920"
tags: [classic-mceliece, code-based, implementation, memory-constrained, decryption, embedded, low-footprint]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**"The giant footprint is the smallest"** — low-footprint decryption for Classic
McEliece, addressing the memory cost that is the scheme's principal deployment
obstacle. The bibliography records a companion IEICE version under the title
"Giant footprint sharing".

## Key claims (as reported)
- Classic McEliece decryption can be implemented with substantially reduced memory footprint.

## Relevance to this program
Classic McEliece's design accepted a very large key in exchange for a
conservative security argument ([[KN-LIT-19cf36]] and the variant breaks explain
why). This literature is the sustained effort to make that trade survivable in
practice.

Held as a worked example of **paying a known cost deliberately and then
engineering around it** — a pattern this program can apply when a
methodologically sound approach is expensive: the cost is a research problem,
not automatically a disqualification.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1109/csp66295.2025.00011).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The footprint achieved and the platform are NOT recorded here. The companion
IEICE paper listed in the bibliography is not separately recorded in this corpus.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
