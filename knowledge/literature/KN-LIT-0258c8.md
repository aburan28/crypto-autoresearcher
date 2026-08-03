---
id: KN-LIT-0258c8
type: literature
title: "Decoding one out of many"
authors:
  - "Nicolas Sendrier"
year: 2011
venue: "PQCrypto"
identifiers:
  eprint: "iacr:2011/367"
  doi: "10.1007/978-3-642-25405-5_4"
  arxiv: null
  url: "https://eprint.iacr.org/2011/367"
tags: [isd, syndrome-decoding, code-based, mceliece, multi-target, dfr, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Decoding one out of many** (DOOM): if the attacker is content to decode *any
one* of `N` given syndromes rather than a specific one, the cost per instance
drops. The gain is roughly `sqrt(N)` in the standard setting, so an attacker
harvesting many ciphertexts pays substantially less per success than a
single-target analysis suggests.

## Key claims (as reported)
- Decoding one of `N` instances is cheaper per instance than decoding a designated one, by roughly a `sqrt(N)` factor.
- The consequence is a real reduction in the security level of schemes analysed only in the single-target model.

## Relevance to this program
The classical statement of the multi-target effect that [[KN-LIT-a85246]]
revisits at KEM level in 2026. Its importance to this program is that it is a
**gap between the security model and deployment that was invisible until
someone counted it** — the scheme was not broken, but its honest security level
was lower than advertised.

The ECDLP has the same structure (batch/multi-target discrete logarithm gives
roughly `sqrt(N)` per-target savings), so the accounting lesson transfers even
though the algorithms do not. Any evidence record in this program that claims a
per-instance cost must state whether it is single-target or amortised.

## Not verified here
Citation verified against the IACR ePrint record for report 2011/367 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-642-25405-5_4).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The exact gain formula and its conditions are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
