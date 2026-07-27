---
id: KN-LIT-7574
type: literature
title: "BIKE: Bit Flipping Key Encapsulation (round-4 submission specification)"
authors: [Aragon Nicolas, Barreto Paulo S. L. M., Bettaieb Slim, Bidoux Loic, Blazy Olivier, Deneuville Jean-Christophe, Gaborit Philippe, Gueron Shay, Guneysu Tim, Aguilar Melchor Carlos, Misoczki Rafael, Persichetti Edoardo, Sendrier Nicolas, Tillich Jean-Pierre, Vasseur Valentin, Zemor Gilles]
year: 2022
venue: NIST PQC Standardization Process, round-4 submission (BIKE spec v5.0, 2022-10-04)
identifiers:
  eprint: null
  doi: null
  url: https://bikesuite.org/files/v5.0/BIKE_Spec.2022.10.04.1.pdf
tags: [code-based, bike, qc-mdpc, kem, decoding-failure, bit-flipping, pqc, specification]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
A quasi-cyclic MDPC KEM: the public key is a single quasi-cyclic block, which
collapses key sizes from ~10^6 bytes (KN-LIT-7573) to ~10^3, at the cost of an
iterative bit-flipping decoder that fails with nonzero probability. The
specification defines the BGF (Black-Gray-Flip) decoder and the decoding failure
rate (DFR) analysis per block size.

## Key claims (as reported)
- Quasi-cyclic structure yields kilobyte-scale keys while keeping a
  syndrome-decoding security argument.
- IND-CCA security requires the DFR to be driven below the security level,
  because decoding failures leak the key (KN-LIT-2085); the specification's DFR
  argument is extrapolated, not proven, for the CCA parameter sets.

## Relevance to this program
BIKE is the cleanest case in the corpus of a scheme whose security depends on a
*rate* that cannot be measured directly at deployment parameters -- the DFR is
far below anything simulable, so the claim rests on an extrapolation model. That
is precisely the pattern KN-TECH-052 (fitting and extrapolating cost exponents
from bounded experiments) exists to police, and it is the subject of
KN-OPEN-022. It is also the code-based counterpart to KN-TECH-048's
decryption-failure attacks on lattice KEMs.

## Not verified here
Specification PDF not fetched. Title, version/date (v5.0, 2022-10-04), URL, and
the principal-submitter list were confirmed via search against the project site
and secondary summaries; the author ordering here follows a secondary listing
and may not match the specification's title page. The DFR and decoder claims are
relayed from secondary summaries, not read from the specification.
