---
id: KN-LIT-f51628
type: literature
title: "Sieving method for SDP with the zero window: an improvement in low memory environments"
authors:
  - "Naoki Yoshiguchi"
  - "Yusuke Aikawa"
  - "Tsuyoshi Takagi"
year: 2024
venue: "IWSEC"
identifiers:
  eprint: null
  doi: "10.1007/978-981-97-7737-2_9"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-981-97-7737-2_9"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, sieving, memory-constrained, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A sieving method for the syndrome decoding problem (SDP) using a **zero
window** — a block of syndrome coordinates constrained to zero, in the tradition
of Stern's and Dumer's windows — presented as an improvement specifically in
**low-memory environments**.

## Key claims (as reported)
- An SDP sieving method built around a zero window.
- The claimed advantage is in low-memory settings, not in the unconstrained-memory optimum.

## Relevance to this program
Memory is the axis on which advanced ISD variants have repeatedly been shown to
be less impressive than their time exponents suggest — the same critique that
`KN-TECH-044` (charging for memory) records on the lattice side, and the point
of Li–Wang ([[KN-LIT-5677ae]]) for Classic McEliece specifically.

Held as an instance of the general rule this program applies to its own cost
claims: **an algorithm's exponent is not its cost until memory and memory
access are priced.**

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-981-97-7737-2_9).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The memory regime in which the improvement holds, and the size of the gain, are
NOT recorded here. Springer link from the bibliography was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
