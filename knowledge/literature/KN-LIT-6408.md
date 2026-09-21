---
id: KN-LIT-6408
type: literature
title: "Secure and Efficient Asynchronous Broadcast Protocols"
authors:
  - "Christian Cachin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Reliable broadcast protocols are a fundamental building block for implementing replication in fault-tolerant distributed systems. This paper addresses secure service replication in an asynchronous environment with a static set of servers, where a malicious adversary may corrupt up to a threshold of servers and controls the network.

## Key claims (as reported)
- We develop a formal model using concepts from modern cryptography, present modular definitions for several broadcast problems, including reliable, atomic, and secure causal broadcast, and present protocols implementing them.
- Reliable broadcast is a basic primitive, also known as the Byzantine generals problem, providing agreement on a delivered message.
- Atomic broadcast imposes additionally a total order on all delivered messages.
- We present a randomized atomic broadcast protocol based on a new, efficient multi-valued asynchronous Byzantine agreement primitive with an external validity condition.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390524 (1).pdf`
- `downloads/21390524 (2).pdf`
- `downloads/21390524.pdf`
- `downloads/ckps.pdf`
