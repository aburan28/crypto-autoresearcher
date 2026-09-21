---
id: KN-LIT-4247
type: literature
title: "Hosting Services on an Untrusted Cloud"
authors:
  - "Dan Boneh"
  - "Divya Gupta"
  - "Ilya Mironov"
  - "Amit Sahai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a scenario where a service provider has created a software service S and desires to outsource the execution of this service to an untrusted cloud. The software service contains secrets that the provider would like to keep hidden from the cloud.

## Key claims (as reported)
- For example, the software might contain a secret database, and the service could allow users to make queries to different slices of this database depending on the user’s identity.
- This setting presents significant challenges not present in previous works on outsourcing or secure computation.
- Because secrets in the software itself must be protected against an adversary that has full control over the cloud that is executing this software, our notion implies indistinguishability obfuscation.
- Furthermore, we seek to protect knowledge of the software S to the maximum extent possible even if the cloud can collude with several corrupted users.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560246 (1).pdf`
- `downloads/90560246.pdf`
