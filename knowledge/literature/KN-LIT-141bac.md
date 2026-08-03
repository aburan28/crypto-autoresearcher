---
id: KN-LIT-141bac
type: literature
title: "A public-key cryptosystem based on algebraic coding theory"
authors:
  - "Robert J. McEliece"
year: 1978
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://ipnpr.jpl.nasa.gov/progress_report2/42-44/44N.PDF"
tags: [code-based, mceliece, foundational, goppa, original, public-key-cryptography]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**The original McEliece cryptosystem** (DSN Progress Report, 1978). Encrypt by
encoding a message with a scrambled, permuted generator matrix of a binary Goppa
code and adding a random error vector of weight `t`; decrypt by undoing the
scrambling and running the Goppa decoder. The public key is the disguised
generator matrix; the secret is the Goppa structure.

Published the same year as RSA, and never broken.

## Key claims (as reported)
- A public-key cryptosystem whose security rests on the hardness of decoding a general linear code, plus the indistinguishability of disguised Goppa codes from random ones.
- Binary Goppa codes are the proposed instantiation — the choice that has survived, where every more structured alternative has not.

## Relevance to this program
The origin of everything else in this sweep, and the single most useful
calibration point this corpus holds for `docs/target-result-profile.md`.

**Forty-eight years, one hundred and sixty-two papers in this bibliography
alone, and the original proposal stands** — with larger parameters
([[KN-LIT-7c6f53]]) and with a CCA transform ([[KN-LIT-ae8a1e]]) it did not have,
but with its central assumptions intact. Every attempt to improve it structurally
was broken; the conservative original was not.

This program cites that record in both directions, and both matter equally.
Against overclaiming: sustained expert attack on a central hard problem rarely
produces an exponent-moving result, so a proposal claiming one cheaply warrants
proportionate scrutiny. Against premature closure: forty-eight years of survival
is not proof of security, and 2026 still produced a claimed heuristic
subexponential attack ([[KN-LIT-7c4620]]). `docs/inventor-protocol.md` treats
declining to search because a target looks saturated as a failure mode symmetric
with overclaiming, and this bibliography is the evidence for that symmetry.

**Does not bear on the ECDLP mathematically.** It bears on the program's taste:
this is what a durable result on a central hard problem looks like from the
inside — a modest, honest, conservatively parameterised construction that made
no claim it could not keep.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — the DSN Progress Report is not
indexed in IACR ePrint or Crossref, and the NASA IPN Progress Report URL is
transcribed from the bibliography and was not resolved during this sweep. The
description of the construction is the standard textbook account and is
**recalled, not read from this source**. Notably, the original paper was **not
previously held in this corpus** despite thirty-two entries mentioning McEliece.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
