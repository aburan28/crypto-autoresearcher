---
id: KN-LIT-3958
type: literature
title: "From Identification to Signatures via the Fiat-Shamir Transform: Minimizing Assumptions for Security and Forward-Security"
authors:
  - "Michel Abdalla"
  - "Jee Hea An"
  - "Mihir Bellare"
  - "Chanathip Namprempre"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Fiat-Shamir paradigm for transforming identification schemes into signature schemes has been popular since its introduction because it yields efficient signature schemes, and has been receiving renewed interest of late as the main tool in deriving forward-secure signature schemes. We find minimal (meaning necessary and sufficient) conditions on the identification scheme to ensure security of the signature scheme in the random oracle model, in both the usual and the forwardsecure cases.

## Key claims (as reported)
- Specifically we show that the signature scheme is secure (resp. forward-secure) against chosen-message attacks in the random oracle model if and only if the underlying identification scheme is secure (resp. forward-secure) against impersonation under passive (i.e.. eavesdropping only) attacks, and has its commitments drawn at random from a large space.
- An extension is proven incorporating a random seed into the Fiat-Shamir transform so that the commitment space assumption may be removed.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/main (2).pdf`
- `downloads/main (6).pdf`
- `downloads/main (7).pdf`
