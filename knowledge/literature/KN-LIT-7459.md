---
id: KN-LIT-7459
type: literature
title: "Verifiable Random Functions from Weaker Assumptions"
authors:
  - "Tibor Jager"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The construction of a verifiable random function (VRF) with large input space and full adaptive security from a static, non-interactive complexity assumption, like decisional Diffie-Hellman, has proven to be a challenging task. To date it is not even clear that such a VRF exists.

## Key claims (as reported)
- Most known constructions either allow only a small input space of polynomially-bounded size, or do not achieve full adaptive security under a static, non-interactive complexity assumption.
- The only known constructions without these restrictions are based on non-static, so-called “q-type” assumptions, which are parametrized by an integer q.
- Since q-type assumptions get stronger with larger q, it is desirable to have q as small as possible.
- In current constructions, q is either a polynomial (e.g., Hohenberger and Waters, Eurocrypt 2010) or at least linear (e.g., Boneh et al., CCS 2010) in the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90150119 (1).pdf`
- `downloads/90150119.pdf`
