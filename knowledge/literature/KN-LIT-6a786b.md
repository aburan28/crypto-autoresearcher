---
id: KN-LIT-6a786b
type: literature
title: "The use of information sets in decoding cyclic codes"
authors:
  - "Eugene Prange"
year: 1962
venue: "IRE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/tit.1962.1057777"
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, prange, foundational, cyclic-codes]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Prange's information-set decoding**, the origin of the entire family. To
decode, pick `k` coordinates at random, hope they contain no errors, invert the
generator matrix restricted to them, and check the resulting candidate; repeat
until the guess is right. Published for cyclic codes in 1962 — sixteen years
before McEliece's cryptosystem existed.

## Key claims (as reported)
- Information sets can be used to decode cyclic codes by repeated random selection and re-encoding.
- The method is generic: it uses no structure of the code beyond a generator matrix.

## Relevance to this program
The most load-bearing single entry of this sweep, for one reason.
**Prange's algorithm remains, asymptotically, close to the best known attack in
the regime McEliece actually uses** ([[KN-LIT-fa9bc8]]). Sixty years and the
whole of this bibliography's first section — Lee–Brickell, Leon, Stern, Dumer,
Canteaut–Chabaud, MMT, BJMM, May–Ozerov, sieving, quantum variants — bought a
modest constant in the exponent.

This program cites that record for calibration in both directions, and the
symmetry matters. It is the standing argument against accepting an
exponent-moving claim cheaply, since sustained expert attack on a central
problem usually does not produce one. It is equally the argument against
`premature closure` (`docs/inventor-protocol.md`): a target that has absorbed
sixty years of attention is not thereby proven safe, and declining to search
because a problem looks saturated is treated here as a failure mode symmetric
with overclaiming.

It is also worth recording that the attack predates the cryptosystem. Generic
methods developed with no adversarial intent set the security level of a scheme
designed later — the direct precedent for this program holding material with no
current ECDLP framing.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/tit.1962.1057777).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Contents unread; no online copy listed. The description of the algorithm is the
standard textbook account and is **recalled, not read from this source**. The
claim that Prange remains competitive at McEliece parameters is relayed from
[[KN-LIT-fa9bc8]] and has not been re-derived here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
