---
id: KN-LIT-6dcb5b
type: literature
title: "Verified fast formulas for control bits for permutation networks"
authors:
  - "Daniel J. Bernstein"
year: 2020
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://cr.yp.to/papers.html#controlbits"
tags: [classic-mceliece, code-based, implementation, formal-verification, permutation-network, control-bits, constant-time]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Verified fast formulas for control bits for permutation networks** — computing
the control bits that make a Beneš-style network realise a given permutation,
with a machine-checked correctness proof and fast formulas rather than the
recursive construction.

## Key claims (as reported)
- Fast formulas for permutation-network control bits.
- **Verified** — correctness is machine-checked.

## Relevance to this program
The origin of the verified-permutation thread that [[KN-LIT-6c6f5e]] continues
six years later. The reason this component attracts formal verification is
worth stating: it is **security-critical, easy to get subtly wrong, and its
bugs are invisible to testing** — a wrong permutation still produces
well-formed output.

This program's own tooling has the same profile in places, which is why
`docs/claims-and-verification.md` prefers re-verified certificates to passing
tests wherever a certificate is available.

**Does not bear on the ECDLP.**

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — not found in IACR ePrint or Crossref
during this sweep; the cr.yp.to URL is transcribed from the bibliography and was
not resolved. The formulas, the verification tool, and the performance claims
are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
