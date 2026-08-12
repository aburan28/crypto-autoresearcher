---
id: KN-LIT-7317
type: literature
title: "Two-Round Oblivious Linear Evaluation from Learning with Errors"
authors:
  - "Pedro Branco"
  - "Nico Döttling"
  - "Paulo Mateus"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, lattice, mpc, pairing, pqc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious Linear Evaluation (OLE) is the arithmetic analogue of the well-know oblivious transfer primitive. It allows a sender, holding an affine function f (x) = a + bx over a finite field or ring, to let a receiver learn f (w) for a w of the receiver’s choice.

## Key claims (as reported)
- In terms of security, the sender remains oblivious of the receiver’s input w, whereas the receiver learns nothing beyond f (w) about f .
- In recent years, OLE has emerged as an essential building block to construct efficient, reusable and maliciously-secure two-party computation.
- In this work, we present efficient two-round protocols for OLE over large fields based on the Learning with Errors (LWE) assumption, providing a full arithmetic generalization of the oblivious transfer protocol of Peikert, Vaikuntanathan and Waters (CRYPTO 2008).
- At the technical core of our work is a novel extraction technique which allows to determine if a non-trivial multiple of some vector is close to a q-ary lattice.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770139 (1).pdf`
- `downloads/131770139.pdf`
