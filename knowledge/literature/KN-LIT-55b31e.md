---
id: KN-LIT-55b31e
type: literature
title: "Knapsack-type cryptosystems and algebraic coding theory"
authors:
  - "Harald Niederreiter"
year: 1986
venue: "Problems of Control and Information Theory"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [code-based, niederreiter, foundational, knapsack, dual-construction]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Niederreiter's construction**: knapsack-type cryptosystems from algebraic
coding theory. Where McEliece encrypts by adding errors to a codeword,
Niederreiter encrypts by computing the syndrome of a low-weight error vector —
the dual formulation, with the same underlying trapdoor.

## Key claims (as reported)
- A knapsack-style public-key cryptosystem built on algebraic codes.
- Equivalent security to McEliece when instantiated with the same code family, with smaller ciphertexts.

## Relevance to this program
The dual construction, and the shape Classic McEliece's KEM actually takes —
which is why this entry matters rather than being a historical footnote.

The methodological point is that a **reformulation of the same mathematics can
have materially better engineering properties** (smaller ciphertexts here) while
being security-equivalent. Looking for such reformulations is cheap and
sometimes decisive, and it is a move `docs/inventor-protocol.md` explicitly
asks proposals to consider before reaching for new mathematics.

The original GRS instantiation was broken by Sidelnikov–Shestakov
([[KN-LIT-19cf36]]); the construction survives with Goppa codes.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — not found in ePrint or Crossref during
this sweep, and no online copy is listed. The security-equivalence and
ciphertext-size claims are the standard textbook account and are **recalled,
not read from this source**.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
