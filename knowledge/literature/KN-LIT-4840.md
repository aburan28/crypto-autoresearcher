---
id: KN-LIT-4840
type: literature
title: "Making RSA–PSS Provably Secure Against Non-Random Faults Gilles Barthe1 , François Dupressoir1 , Pierre-Alain Fouque2 , Benjamin Grégoire4"
authors:
  - "Mehdi Tibouchi"
  - "Jean-Christophe Zapalowicz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, factoring, finite-field, pairing, provable-security, rsa, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
RSA–CRT is the most widely used implementation for RSA signatures. However, deterministic and many probabilistic RSA signatures based on CRT are vulnerable to fault attacks.

## Key claims (as reported)
- Nevertheless, Coron and Mandal (Asiacrypt 2009) show that the randomized PSS padding protects RSA signatures against random faults.
- In contrast, Fouque et al.
- (CHES 2012) show that PSS padding does not protect against certain non-random faults that can be injected in widely used implementations based on the Montgomery modular multiplication.
- In this paper, we prove the security of an infective countermeasure against a large class of non-random faults; the proof extends Coron and Mandal’s result to a strong model where the adversary can choose the value of the faulty signatures modulo one of the prime factors of the RSA modulus.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310170 (1).pdf`
- `downloads/87310170 (2).pdf`
- `downloads/87310170 (3).pdf`
- `downloads/87310170.pdf`
