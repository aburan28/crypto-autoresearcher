---
id: KN-LIT-6304
type: literature
title: "Rotatable Zero Knowledge Sets: Post Compromise Secure Auditable Dictionaries with application to Key Transparency"
authors:
  - "Brian Chen"
  - "Yevgeniy Dodis"
  - "Esha Ghosh"
  - "Eli Goldin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Key Transparency (KT) systems allow end-to-end encrypted service providers (messaging, calls, etc.) to maintain an auditable directory of their users’ public keys, producing proofs that all participants have a consistent view of those keys, and allowing each user to check updates to their own keys. KT has lately received a lot of attention, in particular its privacy preserving variants, which also ensure that users and auditors do not learn anything beyond what is necessary to use the service and keep the service provider accountable.

## Key claims (as reported)
- Abstractly, the problem of building such systems reduces to constructing so-called append-only Zero-Knowledge Sets (aZKS).
- Unfortunately, existing aZKS (and KT) solutions do not allow to adequately restore the privacy guarantees after a server compromise, a form of Post-Compromise Security (PCS), while maintaining the auditability properties.
- In this work we address this concern through the formalization of an extension of aZKS called Rotatable ZKS (RZKS).
- In addition to providing PCS, our notion of RZKS has several other attractive features, such as a stronger (extractable) soundness notion, and the ability for a communication party with out-ofdate data to efficiently “catch up” to the current epoch while ensuring that the server did not erase any of the past data.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910356 (1).pdf`
- `downloads/137910356.pdf`
