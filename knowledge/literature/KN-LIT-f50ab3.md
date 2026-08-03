---
id: KN-LIT-f50ab3
type: literature
title: "Leaky McEliece: secret key recovery from highly erroneous side-channel information"
authors:
  - "Marcus Brinkmann"
  - "Chitchanok Chuengsatiansup"
  - "Alexander May"
  - "Julian Nowakowski"
  - "Yuval Yarom"
year: 2025
venue: "CHES"
identifiers:
  eprint: "iacr:2023/1536"
  doi: "10.46586/tches.v2025.i2.94-125"
  arxiv: null
  url: "https://eprint.iacr.org/2023/1536"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, key-recovery, erroneous-leakage, error-correction, lattice-techniques]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Leaky McEliece**: secret key recovery from **highly erroneous** side-channel
information — recovering the key even when the measured leakage is mostly
wrong. The interesting quantity is how much noise the recovery tolerates.

## Key claims (as reported)
- Key recovery succeeds from side-channel information with a high error rate.
- Robustness to measurement error is the contribution, not the measurement itself.

## Relevance to this program
The most important **defensive** result in this cluster, because it moves the
bar: it is not sufficient to make leakage noisy. The recovery algorithm absorbs
noise, so a countermeasure that merely degrades signal quality may not help at
all.

The general principle — **an adversary with an error-tolerant post-processing
step is far stronger than the raw measurement suggests** — is one this program
should apply when reasoning about any partial-information attack, including on
the curve side where noisy nonce leakage is the standing example.

Held with [[KN-LIT-55e037]], which treats the error-correction machinery as its
own subject.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/1536 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.46586/tches.v2025.i2.94-125).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The tolerable error rate, the recovery algorithm, and its cost are NOT recorded
here — and the tolerable error rate is the paper's key number.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
