---
id: KN-LIT-33d2bd
type: literature
title: "Cryptanalysis of the Niederreiter public key scheme based on GRS subcodes"
authors:
  - "Christian Wieschebrink"
year: 2010
venue: "PQCrypto"
identifiers:
  eprint: null
  doi: "10.1007/978-3-642-12929-2_5"
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, niederreiter, grs-codes, subcodes, variant-break]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Cryptanalysis of the **Niederreiter scheme based on GRS subcodes** — a variant
that hoped to repair the GRS-based construction, broken by Sidelnikov–Shestakov
([[KN-LIT-19cf36]]), by publishing only a subcode.

## Key claims (as reported)
- The GRS-subcode repair does not restore security.

## Relevance to this program
An instance of the **failed-repair** genre, which is worth holding for its own
sake. After a family is broken, the natural response is a modification that
blocks the specific attack; the modification then usually falls to a variation
of the same idea.

This program's decision records are required to name a concrete successor or
revisit condition when a path is deprioritised (rule 9). The failed-repair
pattern is why that requirement is not merely bureaucratic: "we patched the
break" is not a successor unless the patch is tested against the attack's
generalisation, not just its instance.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-642-12929-2_5).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The attack's mechanism and cost are NOT recorded here. No online copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
