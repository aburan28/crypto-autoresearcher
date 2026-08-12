---
id: KN-LIT-076
type: literature
title: On the Security of Supersingular Isogeny Cryptosystems (GPST adaptive attack)
authors: [Galbraith Steven D., Petit Christophe, Shani Barak, Ti Yan Bo]
year: 2016
venue: ASIACRYPT 2016, LNCS 10031, pp. 63-91
identifiers:
  eprint: iacr:2016/859
  doi: 10.1007/978-3-662-53887-6_3
  url: https://eprint.iacr.org/2016/859
tags: [gpst, sidh, adaptive-attack, static-key, torsion-points, endomorphism-ring, cryptanalysis, isogeny, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The GPST active/adaptive attack: recovers a STATIC SIDH secret key by sending
malformed torsion points and observing whether key exchange succeeds, using
partial knowledge of shared keys to reconstruct the full key. Hence static-key
SIDH needs a countermeasure (Fujisaki-Okamoto transform / ephemeral keys).

## Key claims (as reported)
- Also argues that the security of all such schemes ultimately depends on the
  difficulty of computing the ENDOMORPHISM RING of a supersingular curve
  (KN-LIT-074) -- and develops foundational analysis of the isogeny problem when
  auxiliary torsion information is available.
- The active attack is preventable only via a relatively expensive countermeasure.

## Relevance to this program
Maps the security landscape of the isogeny problem and shows how revealed /
manipulated torsion-point data enables key recovery -- directly on-theme for how
auxiliary information changes cryptanalytic complexity (KN-OPEN-015). An early
warning (2016) that the torsion images SIDH publishes are dangerous, six years
before the full break. Adjacent to the ECDLP mission.

## Not verified here
Full paper not read; the adaptive attack and endomorphism-ring observation relayed
from the abstract (hence confidence: reported). Fields confirmed against IACR
ePrint 2016/859 and the Springer DOI via search, not by fetching the primary
pages.
