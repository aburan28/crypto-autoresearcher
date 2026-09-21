---
id: KN-LIT-d5baac
type: literature
title: "Post-quantum WireGuard"
authors:
  - "Andreas Hülsing"
  - "Kai-Chun Ning"
  - "Peter Schwabe"
  - "Florian Weber"
  - "Philip R. Zimmermann"
year: 2021
venue: "IEEE S&P"
identifiers:
  eprint: "iacr:2020/379"
  doi: "10.31224/5020"
  arxiv: null
  url: "https://eprint.iacr.org/2020/379"
tags: [classic-mceliece, code-based, implementation, protocol, wireguard, vpn, hybrid, deployment]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Post-quantum WireGuard**: a post-quantum variant of the WireGuard VPN
protocol, using code-based and other post-quantum primitives in place of the
original's elliptic-curve handshake.

## Key claims (as reported)
- WireGuard's handshake can be made post-quantum.
- A protocol-level design and analysis, not a primitive.

## Relevance to this program
The only protocol-level entry in this sweep, and the one that shows what the
rest is *for*. It is also where the ECDLP appears in this bibliography: the
protocol being replaced is elliptic-curve based, and the replacement exists
because of doubt about the long-term hardness of the discrete logarithm problem
under quantum attack.

That is the honest statement of this program's context — **the practical
consequence of ECDLP hardness is what protocols like this hinge on** — and it
should be recorded without inflating it. Nothing in this entry bears on the
mathematical question; it records the deployment stake.

Held with [[KN-LIT-4877]] (McTiny), the other protocol-integration entry, already
in the corpus.

## Not verified here
Citation verified against the IACR ePrint record for report 2020/379 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.31224/5020).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The protocol design, its security analysis, and its performance are NOT recorded
here. Which post-quantum primitives are used in which role is likewise not
recorded.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
