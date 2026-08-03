---
id: KN-LIT-b9d3e0
type: literature
title: "How to backdoor (Classic) McEliece and how to guard against backdoors"
authors:
  - "Tobias Hemmert"
  - "Alexander May"
  - "Johannes Mittmann"
  - "Carl Richard Theodor Schneider"
year: 2022
venue: "PQCrypto"
identifiers:
  eprint: "iacr:2022/362"
  doi: "10.1007/978-3-031-17234-2_2"
  arxiv: null
  url: "https://eprint.iacr.org/2022/362"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, backdoor, subversion, key-generation, countermeasure]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**How to backdoor (Classic) McEliece and how to guard against backdoors** — both
halves: a construction for a subverted key generator whose output looks
legitimate, and defences against it.

## Key claims (as reported)
- Classic McEliece key generation can be backdoored so that outputs appear legitimate.
- Countermeasures are given alongside the attack.

## Relevance to this program
The attack-and-defence pairing is the feature worth recording. A subversion
paper that stops at the construction leaves the field worse off; carrying the
guard makes it actionable.

`docs/inventor-protocol.md`'s closure standard asks the same of this program's
deliverables — a result is not finished at the point where it is interesting,
but at the point where its consequences are stated. And rule 9 requires a
deprioritisation to name a successor or revisit condition, for the same reason.

Held with [[KN-LIT-c4974d]], the multi-user follow-up.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/362 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-17234-2_2).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The backdoor construction, its undetectability properties, and the strength of
the proposed guards are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
