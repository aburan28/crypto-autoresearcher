---
id: KN-LIT-55e037
type: literature
title: "Optimizing key recovery in Classic McEliece: advanced error correction for noisy side-channel measurements"
authors:
  - "Nicolas Vallet"
  - "Pierre-Louis Cayrel"
  - "Brice Colombier"
  - "Vlad-Florin Dragoi"
  - "Vincent Grosso"
year: 2025
venue: "IACR Communications in Cryptology"
identifiers:
  eprint: "iacr:2025/802"
  doi: "10.62056/ahmpgyl7s"
  arxiv: null
  url: "https://eprint.iacr.org/2025/802"
tags: [classic-mceliece, code-based, implementation, side-channel, error-correction, key-recovery, noisy-data]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Optimising key recovery in Classic McEliece by applying **advanced error
correction to noisy side-channel measurements** — treating the leaked data as a
noisy channel and decoding it, rather than demanding clean measurements.

## Key claims (as reported)
- Error-correction techniques improve key recovery from noisy side-channel data.

## Relevance to this program
The recursion here is worth stating: **coding theory is used to attack a
code-based cryptosystem**, by decoding the side-channel measurement rather than
the ciphertext. The attacker's error-correction problem is a different instance
of the same mathematics the defender is using.

Held with [[KN-LIT-f50ab3]] (Leaky McEliece) as the noise-tolerance pair, and as
a reminder that a technique's role — attack or defence — is a matter of where it
is pointed, not of what it is.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/802 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.62056/ahmpgyl7s).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The error-correction methods used and the improvement obtained are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
