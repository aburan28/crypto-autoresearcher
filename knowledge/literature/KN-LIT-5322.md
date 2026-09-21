---
id: KN-LIT-5322
type: literature
title: "On Composable Security for Digital Signatures"
authors:
  - "Christian Badertscher"
  - "Ueli Maurer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Instead of modeling all aspects of a DSS in a monolithic ideal functionality, our approach characterizes a DSS as a construction of a repository for authentically reading values written by a certain party from certain assumed repositories, e.g., for transmitting verification key and signature values. This approach resolves several technical complications of previous simulation-based approaches, captures the security of signature schemes in an abstract way, and allows for modular proofs.

## Key claims (as reported)
- We show that our definition is equivalent to existential unforgeability.
- We then model two example applications: (1) the certification of values via a signature from a specific entity, which with public keys as values is the core functionality of public-key infrastructures, and (2) the authentication of a session between a client and a server with the help of a digitally signed assertion from an identity provider.
- Single-sign-on mechanisms such as SAML rely on the soundness of the latter approach.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770209 (1).pdf`
- `downloads/10770209 (2).pdf`
- `downloads/10770209 (3).pdf`
- `downloads/10770209 (4).pdf`
- `downloads/10770209.pdf`
