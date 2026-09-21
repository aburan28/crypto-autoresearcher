---
id: KN-LIT-070
type: literature
title: Hard Homogeneous Spaces / Public-Key Cryptosystem Based on Isogenies (Couveignes; Rostovtsev-Stolbunov)
authors: [Couveignes Jean-Marc, Rostovtsev Alexander, Stolbunov Anton]
year: 2006
venue: IACR ePrint 2006/291 (Couveignes, ~1997); IACR ePrint 2006/145 (Rostovtsev-Stolbunov)
identifiers:
  eprint: iacr:2006/291
  doi: null
  url: https://eprint.iacr.org/2006/291
tags: [hard-homogeneous-space, group-action, ordinary-curve, isogeny, class-group, key-exchange, csidh-precursor, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
The two independent origins of commutative isogeny group-action key exchange,
which CSIDH (KN-LIT-069) later instantiates:
- **Couveignes, "Hard Homogeneous Spaces"** (ePrint 2006/291, written ~1997):
  abstracts a "hard homogeneous space" (a torsor under an abelian group where the
  action is easy but vectorization/inversion is hard) and ports Diffie-Hellman to
  it.
- **Rostovtsev-Stolbunov** (ePrint 2006/145): a concrete public-key cryptosystem
  from isogenies between ORDINARY elliptic curves, via CM and the ideal class
  group action.

## Key claims (as reported)
- The class-group-action-on-curves structure is the theoretical backbone of the
  commutative-isogeny branch.
- Both are ePrint reports with no peer-reviewed DOI; Couveignes was originally a
  rejected 1997 Crypto submission posted in 2006.

## Relevance to this program
The foundational group-action / HHS framework behind CSIDH and the ordinary-curve
isogeny key exchange. Its ordinary-curve class-group action and CM / volcano
structure are directly relevant to the program's volcano-orientation work
(RQ-ISO-001, ISO-AR). Adjacent to the ECDLP mission (CM / class-group machinery).

## Not verified here
Full papers not read; the HHS abstraction and the ordinary-curve scheme relayed
from the abstracts (the framework is textbook-level in isogeny cryptography, hence
confidence: established). Fields for both ePrint 2006/291 and 2006/145 confirmed
via search, not by fetching the primary pages.
