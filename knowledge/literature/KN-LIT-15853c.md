---
id: KN-LIT-15853c
type: literature
title: "Key-recovery side-channel attack on the Berlekamp-Massey decoding algorithm in the Classic McEliece KEM"
authors:
  - "Andrei Alexei"
  - "Marios Omar Choudary"
  - "Vlad-Florin Dragoi"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/2043"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2043"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, key-recovery, berlekamp-massey, decoding]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A key-recovery side-channel attack on the **Berlekamp–Massey** step of Classic
McEliece decapsulation. Berlekamp–Massey computes the error-locator polynomial
during Goppa decoding; its control flow and operand values depend on the secret.

## Key claims (as reported)
- Leakage from the Berlekamp–Massey routine enables secret key recovery.
- Targets a specific decoding subroutine rather than the implementation as a whole.

## Relevance to this program
Illustrates how this attack literature works: pick **one subroutine**, model
what its leakage reveals, and build the recovery from there. Over time the
cluster covers the whole decapsulation path — polynomial loading
([[KN-LIT-6e1eb5]]), syndrome computation ([[KN-LIT-7d6c98]]), permutation
([[KN-LIT-886c90]]), and here the error locator.

That decomposition-and-coverage strategy is a research-design pattern this
program can use directly: to attack a pipeline, enumerate its stages and audit
each, rather than treating the pipeline as a single object.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/2043 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The leakage model, trace requirements and target platform are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
