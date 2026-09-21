---
id: KN-LIT-fbc2c8
type: literature
title: "Breaking Goppa-based McEliece with hints"
authors:
  - "Elena Kirshanova"
  - "Alexander May"
year: 2022
venue: "SCN 2022; Information and Computation 2023"
identifiers:
  eprint: "iacr:2022/525"
  doi: "10.1016/j.ic.2023.105045"
  arxiv: null
  url: "https://eprint.iacr.org/2022/525"
tags: [code-based, mceliece, structural-attack, key-recovery, goppa, partial-information, hints, side-channel-theory]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Breaking Goppa-based McEliece with hints**: given partial information about
the secret Goppa key, how much is enough to recover the rest? The earlier title
— "Decoding McEliece with a hint: secret Goppa key parts reveal everything" —
states the answer more bluntly.

## Key claims (as reported)
- Partial knowledge of secret Goppa key components enables full key recovery.
- The quantity of leakage required is small enough that the earlier title describes it as revealing everything.

## Relevance to this program
The theoretical bridge to the entire side-channel section of this bibliography.
Physical attacks recover *fragments*; this paper says what a fragment is worth,
and its answer is: **more than one would guess.**

The general form matters to this program: a secret with algebraic structure
degrades **non-gracefully**. Recovering a small fraction can collapse the rest,
because the structure that makes the trapdoor work also constrains the unknown
parts. Any proposal here that introduces a structured secret must consider its
partial-leakage behaviour, not only its full-secrecy hardness.

Held with [[KN-LIT-8285cb]] (ISD with hints), which asks the same question on
the decoding side.

**Does not bear on the ECDLP directly**, but the partial-information question
is live there too — the hidden number problem and biased-nonce attacks are the
curve-side analogue, and the corpus holds those separately.

## Not verified here
Citation verified against the IACR ePrint record for report 2022/525 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1016/j.ic.2023.105045).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

How much leakage is required, of which key components, and the recovery cost
are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
