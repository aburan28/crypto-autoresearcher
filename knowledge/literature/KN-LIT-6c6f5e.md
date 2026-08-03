---
id: KN-LIT-6c6f5e
type: literature
title: "Verified non-recursive calculation of Beneš networks applied to Classic McEliece"
authors:
  - "Wrenna Robson"
  - "Samuel Kelly"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/107"
  doi: "10.46586/tches.v2026.i3.306-333"
  arxiv: null
  url: "https://eprint.iacr.org/2026/107"
tags: [classic-mceliece, code-based, implementation, formal-verification, benes-network, permutation, proof-assistant]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Verified non-recursive calculation of Beneš networks** applied to Classic
McEliece. Beneš networks realise an arbitrary permutation as a fixed network of
conditional swaps, which is how Classic McEliece applies its secret permutation
in constant time. The standard construction is recursive; this gives a
non-recursive calculation with a machine-checked correctness proof.

## Key claims (as reported)
- A non-recursive method for computing Beneš network control bits.
- **Verified** — the correctness argument is machine-checked, not prose.

## Relevance to this program
The current end of a line that begins with Bernstein's control-bit formulas
([[KN-LIT-6dcb5b]]) and runs through the Classic McEliece formal-methods work
([[KN-LIT-3f2ee6]]). What makes it worth holding is the **claim tier**:
a machine-checked proof is the strongest basis available, above a derivation and
far above empirical validation.

`docs/claims-and-verification.md` defines exactly that ladder for this program's
own findings — `certificate`, `derivation`, `empirical_only` — and this is a
published example of a community deliberately climbing it for a component
where correctness is security-critical and hard to test.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2026/107 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.46586/tches.v2026.i3.306-333).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The proof assistant used, the exact statement verified, and the performance of
the non-recursive method are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
