---
id: KN-LIT-3791
type: literature
title: "Fast constant-time"
authors:
  - "Daniel J. Bernstein"
  - "Bo-Yin Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, finite-field, implementation, lattice, pairing, pqc, provable-security, rsa, side-channel, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces streamlined constant-time variants of Euclid’s algorithm, both for polynomial inputs and for integer inputs. As concrete applications, this paper saves time in (1) modular inversion for Curve25519, which was previously believed to be handled much more efficiently by Fermat’s method, and (2) key generation for the ntruhrss701 and sntrup4591761 lattice-based cryptosystems.

## Key claims (as reported)
- (Abstract too short to separate claims; see Contribution.)

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/safegcd-20190413.pdf`
