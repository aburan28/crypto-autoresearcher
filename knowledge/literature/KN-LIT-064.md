---
id: KN-LIT-064
type: literature
title: SIKE - Supersingular Isogeny Key Encapsulation (NIST PQC submission, broken 2022)
authors: [Azarderakhsh Reza, Campagna Matthew, Costello Craig, De Feo Luca, Hess Basil, Jalali Amir, Jao David, Koziel Brian, LaMacchia Brian, Longa Patrick, Naehrig Michael, Renes Joost, Soukharev Vladimir, Urbanik David]
year: 2022
venue: NIST PQC standardization submission (Round 4 spec, 2022-09-15)
identifiers:
  eprint: null
  doi: null
  url: https://csrc.nist.gov/csrc/media/Projects/post-quantum-cryptography/documents/round-4/submissions/SIKE-spec.pdf
tags: [sike, sidh, kem, nist, cryptanalysis, broken, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
SIKE is a CCA-secure key-encapsulation mechanism built on SIDH (KN-LIT-062) via a
Fujisaki-Okamoto-style transform. It reached NIST PQC Round 3 as an alternate
candidate and advanced to Round 4.

## Key claims (as reported)
- Small keys/ciphertexts; the most compact NIST PQC KEM candidate.
- BROKEN in July/August 2022 by Castryck-Decru (KN-LIT-065) and follow-ups: a
  classical key-recovery attack via Kani's glue-and-split and the SIDH
  torsion-point images; reported single-core times ~1 hour (SIKEp434) to ~21
  hours (SIKEp751), so ALL parameter sets fall. NIST subsequently dropped it.
- The break is specific to the SIDH torsion-image structure; CGL, CSIDH, and
  SQIsign are unaffected.

## Relevance to this program
A concrete, high-profile instance of auxiliary torsion-point data turning a
conjectured-hard problem into a polynomial-time break via higher-dimensional
isogenies (KN-TECH-026) -- the isogeny-transfer / cover-attack phenomena adjacent
to the ECDLP program, and a cautionary case for reasoning about torsion /
endomorphism-ring leakage.

## Not verified here
Submission not read; scheme status and break timings relayed from the NIST CSRC
page and the break papers (hence confidence: reported). Author roster is the
core submission team (the full team includes further contributors). No DOI (NIST
submission). Fields confirmed against NIST CSRC via search, not by fetching the
primary page.
