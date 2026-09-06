---
id: KN-LIT-3f24a6
type: literature
title: "Expander properties of superspecial digraphs"
authors:
  - "Krijn Reijnders"
  - "Thomas Decru"
year: 2026
venue: "CRYPTO 2026 (presentation slides); paper at Cryptology ePrint Archive 2026/500"
identifiers:
  eprint: "iacr:2026/500"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/500"
tags: [isogeny, superspecial, isogeny-graph, digraph, expander, ramanujan, spectral-gap, dimension-2, richelot, jacobian, genus-2, random-walk, slides, isogeny-based-cryptography, elliptic-curve]
confidence: unverified
citation_verified: false
added: "2026-09-06"
superseded_by: null
---

> **PROVENANCE — READ THIS BEFORE CITING. The paper was NOT read.** What was read is
> a **CRYPTO 2026 presentation slide deck**,
> `/Volumes/SSD990/downloads/207_slides.pdf` (5,366,514 bytes,
> `sha256:22d1606ee83576b19e824881594a503dec162b54bc5ba1f029819a22deec6841`), whose
> title slide names Krijn Reijnders, "joint work with Thomas Decru", CRYPTO 2026, and
> points at `https://eprint.iacr.org/2026/500`.
>
> Slide decks extract badly: the deck uses incremental builds, so `pdftotext` returns
> the same fragment repeatedly and drops most mathematical content. This entry
> therefore records **only what was legible**, which is very little. It is filed as a
> **pointer so a future agent can find the paper**, not as a summary of it —
> `knowledge/SEEDING.md`'s honest floor. `citation_verified: false` and
> `confidence: unverified` are deliberate and must not be raised without reading
> `iacr:2026/500` itself.

## What the deck appears to claim

Fragmentary, and each item below should be re-checked against the paper:

- The object is the **superspecial `(ℓ, ℓ)`-isogeny digraph** `G_{2,p}(ℓ)` — a
  numbered definition ("Definition 11") in the deck — i.e. the dimension-2 analogue of
  the supersingular `ℓ`-isogeny graph, on superspecial principally polarized abelian
  surfaces / genus-2 Jacobians rather than elliptic curves.
- The deck steps through dimensions 1, 2, 3, contrasting elliptic curves
  (`E : y² = x³ + ax + b`) with genus-2 curves and addition **on the Jacobian
  `J_C`, explicitly not on the curve**.
- Eigenvalues of the digraph are computed and the word **"Ramanujan"** appears as a
  conclusion, so the result is a spectral-gap / expansion statement about these
  digraphs. Whether the claim is that they *are* Ramanujan, are Ramanujan only in
  certain cases, or fail to be, **could not be determined from the extracted text.**
- A theorem represents `ζ*` acting on `J[ℓ]` as a matrix `M ∈ GL_4(F_ℓ)`.

## Why this is worth a pointer

Expansion of isogeny graphs is the mixing assumption underneath random-walk arguments
in isogeny-based cryptography, and this program has several live isogeny lanes
(`GOAL-SSI-001`, `GOAL-SSIQ-001`, `GOAL-QALG-001`, and the isogeny-class machinery in
`harness/isogeny_class.py` and `harness/rl_isogeny`). A CRYPTO 2026 result on the
spectral behaviour of the **dimension-2** graph bears directly on whether
walk-mixing intuitions carried over from the elliptic case are safe in higher
dimension. That is a question this program is exposed to and has not audited.

## Required before use

Fetch and read `iacr:2026/500`. Until then this entry supports nothing: it may not
back a `novelty_status`, a coordinator decision, or a heuristic's
`supporting_results` (`AGENTS.md` rule 9). In particular, do **not** cite it for the
direction of the Ramanujan claim — the deck's own conclusion on that point was not
legible in extraction, and guessing it is precisely the failure this entry's
provenance block exists to prevent.
