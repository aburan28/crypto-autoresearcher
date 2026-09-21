---
id: KN-LIT-5602
type: literature
title: "On the Unpredictability of Bits of the Elliptic Curve Diffie–Hellman Scheme"
authors:
  - "Dan Boneh"
  - "Igor E. Shparlinski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, finite-field, lattice, pairing, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let E/Fp be an elliptic curve, and G ∈ E/Fp . Define the Diffie–Hellman function as DHE,G (aG, bG) = abG.

## Key claims (as reported)
- We show that if there is an efficient algorithm for predicting the LSB of the x or y coordinate of abG given hE, G, aG, bGi for a certain family of elliptic curves, then there is an algorithm for computing the Diffie–Hellman function on all curves in this family.
- This seems stronger than the best analogous results for the Diffie–Hellman function in F∗p .
- Boneh and Venkatesan showed that in F∗p computing approximately (log p)1/2 of the bits of the Diffie–Hellman secret is as hard as computing the entire secret.
- Our results show that just predicting one bit of the Elliptic Curve Diffie–Hellman secret in a family of curves is as hard as computing the entire secret.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390200 (1).pdf`
- `downloads/21390200 (2).pdf`
- `downloads/21390200.pdf`
