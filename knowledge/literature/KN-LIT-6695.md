---
id: KN-LIT-6695
type: literature
title: "Single-Server Private Information Retrieval with Sublinear Amortized Time"
authors:
  - "Henry Corrigan-Gibbs"
  - "Alexandra Henzinger"
  - "Dmitry Kogan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct new private-information-retrieval protocols in the single-server setting. Our schemes allow a client to privately fetch a sequence of database records from a server, while the server answers each query in average time sublinear in the database size.

## Key claims (as reported)
- Specifically, we introduce the first single-server private-information-retrieval schemes that have sublinear amortized server time, require sublinear additional storage, and allow the client to make her queries adaptively.
- Our protocols rely only on standard cryptographic assumptions (decision DiffieHellman, quadratic residuosity, learning with errors, etc.).
- They work by having the client first fetch a small “hint” about the database contents from the server.
- Generating this hint requires server time linear in the database size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760032 (1).pdf`
- `downloads/132760032.pdf`
