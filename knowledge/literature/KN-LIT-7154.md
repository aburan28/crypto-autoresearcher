---
id: KN-LIT-7154
type: literature
title: "Tightly-Secure Authenticated Key Exchange"
authors:
  - "Christoph Bader"
  - "Dennis Hofheinz"
  - "Tibor Jager"
  - "Eike Kiltz"
  - "Yong Li"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first Authenticated Key Exchange (AKE) protocol whose security does not degrade with an increasing number of users or sessions. We describe a three-message protocol and prove security in an enhanced version of the classical Bellare-Rogaway security model.

## Key claims (as reported)
- Our construction is modular, it can be instantiated efficiently from standard assumptions (such as the SXDH or DLIN assumptions in pairingfriendly groups).
- For instance, we provide an SXDH-based protocol with only 14 group elements and 4 exponents communication complexity (plus some bookkeeping information).
- Along the way we develop new, stronger security definitions for digital signatures and key encapsulation mechanisms.
- For instance, we introduce a security model for digital signatures that provides existential unforgeability under chosen-message attacks in a multi-user setting with adaptive corruptions of secret keys.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90140632 (1).pdf`
- `downloads/90140632.pdf`
