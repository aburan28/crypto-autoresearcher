---
id: KN-LIT-2111
type: literature
title: "A Method for Making Password-Based Key Exchange Resilient to Server Compromise?"
authors:
  - "Craig Gentry"
  - "Philip MacKenzie"
  - "Zulfikar Ramzan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper considers the problem of password-authenticated key exchange (PAKE) in a client-server setting, where the server authenticates using a stored password file, and it is desirable to maintain some degree of security even if the server is compromised. A PAKE scheme is said to be resilient to server compromise if an adversary who compromises the server must at least perform an offline dictionary attack to gain any advantage in impersonating a client.

## Key claims (as reported)
- (Of course, offline dictionary attacks should be infeasible in the absence of server compromise.) One can see that this is the best security possible, since by definition the password file has enough information to allow one to play the role of the server, and thus to verify passwords in an offline dictionary attack.
- While some previous PAKE schemes have been proven resilient to server compromise, there was no known general technique to take an arbitrary PAKE scheme and make it provably resilient to server compromise.
- This paper presents a practical technique for doing so which requires essentially one extra round of communication and one signature computation/verification.
- We prove security in the universal composability framework by (1) defining a new functionality for PAKE with resilience to server compromise, (2) specifying a protocol combining this technique with a (basic) PAKE functionality, and (3) proving (in the random oracle model) that this protocol securely realizes the new functionality.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170140 (1).pdf`
- `downloads/41170140 (2).pdf`
- `downloads/41170140 (3).pdf`
- `downloads/41170140.pdf`
