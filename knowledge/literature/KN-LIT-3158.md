---
id: KN-LIT-3158
type: literature
title: "Controlling Access to an Oblivious Database using Stateful Anonymous Credentials"
authors:
  - "Scott Coull"
  - "Matthew Green"
  - "Susan Hohenberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mpc, pairing, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we consider the task of allowing a content provider to enforce complex access control policies on oblivious protocols conducted with anonymous users. As our primary application, we show how to construct privacy-preserving databases by combining oblivious transfer with an augmented anonymous credential system.

## Key claims (as reported)
- This permits a database operator to restrict which items each user may access, without learning anything about users’ identities or item choices.
- This strong privacy guarantee holds even when users are assigned different access control policies and are allowed to adaptively make many queries.
- To do so, we show how to augment existing anonymous credential systems so that, in addition to certifying a user’s attributes, they also store state about the user’s database access history.
- Our construction supports a wide range of access control policies, including efficient and private realizations of the Brewer-Nash (Chinese Wall) and Bell-LaPadula (Multilevel Security) policies, which are used for financial and defense applications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430506 (1).pdf`
- `downloads/54430506 (2).pdf`
- `downloads/54430506 (3).pdf`
- `downloads/54430506.pdf`
