---
id: KN-LIT-f28b46
type: literature
title: "Revisiting nearest-neighbor-based information set decoding"
authors:
  - "Andre Esser"
year: 2022
venue: null
identifiers:
  eprint: "iacr:2022/1328"
  doi: "10.1007/978-3-031-47818-5_3"
  arxiv: null
  url: "https://eprint.iacr.org/2022/1328"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, nearest-neighbor, may-ozerov]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Revisits nearest-neighbour-based ISD — the May–Ozerov line ([[KN-LIT-5324]]) in
which the inner search for colliding vectors is treated as a nearest-neighbour
problem. Re-examination of an approach whose practical benefit had been argued
to be smaller than its asymptotic advantage suggests.

## Key claims (as reported)
- A re-analysis of nearest-neighbour ISD.
- Framed as revisiting, i.e. correcting or sharpening the existing understanding rather than introducing a new family.

## Relevance to this program
"Revisiting" papers are disproportionately valuable to this program because
they are where the **gap between asymptotic promise and concrete delivery** gets
measured. The May–Ozerov technique is the standard example of an ISD ingredient
whose asymptotic gain is hard to realise at real parameters.

That pattern — technique is correct, asymptotically better, and concretely
disappointing — is one the red-team role is specifically asked to test for in
this program's own proposals.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/1328 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-47818-5_3).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Whether the revision raises or lowers prior estimates of nearest-neighbour ISD's
usefulness is NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
