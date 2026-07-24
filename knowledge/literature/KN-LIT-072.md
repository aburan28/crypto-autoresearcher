---
id: KN-LIT-072
type: literature
title: SQIsign - Compact Post-Quantum Signatures from Quaternions and Isogenies
authors: [De Feo Luca, Kohel David, Leroux Antonin, Petit Christophe, Wesolowski Benjamin]
year: 2020
venue: ASIACRYPT 2020, LNCS 12491, pp. 64-93
identifiers:
  eprint: iacr:2020/1240
  doi: 10.1007/978-3-030-64837-4_3
  url: https://eprint.iacr.org/2020/1240
tags: [sqisign, signature, deuring, endomorphism-ring, quaternion, fiat-shamir, isogeny, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A compact isogeny-based signature (Short Quaternion and Isogeny Signature) from a
one-round, high-soundness identification protocol on supersingular isogeny graphs,
made non-interactive via Fiat-Shamir. Security rests on the Deuring correspondence
(KN-LIT-075) and on computing endomorphism rings; a central tool is a new
algorithm to find an isogeny path connecting two supersingular curves of known
endomorphism rings.

## Key claims (as reported)
- At NIST-1: ~204-byte signatures, 64-byte public keys, 16-byte secret keys --
  an order of magnitude smaller (signature + public key) than other PQ candidates
  at the time; reference timings ~0.6 s keygen, ~2.5 s sign, ~50 ms verify.
- NOT affected by the 2022 SIDH torsion-image break (reveals no torsion images) --
  it is a leading survivor and an active NIST additional-signatures candidate.

## Relevance to this program
SQIsign's hardness and construction sit directly on endomorphism rings and the
Deuring correspondence between supersingular curves and quaternion maximal orders
-- the algebraic endomorphism-structure machinery the program studies (CM,
orientation, RQ-ISO-001, ISO-AR). Adjacent to the ECDLP mission. Illustrates the
design principle (post-SIDH-break) of NOT revealing torsion images (KN-OPEN-015).

## Not verified here
Full paper not read; the scheme and sizes relayed from the abstract (hence
confidence: reported; parameters have evolved in later SQIsign versions). Fields
confirmed against IACR ePrint 2020/1240 and the Springer DOI via search, not by
fetching the primary pages.
