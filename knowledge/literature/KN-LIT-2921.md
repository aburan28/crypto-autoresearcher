---
id: KN-LIT-2921
type: literature
title: "Client-Server Concurrent Zero Knowledge with"
authors:
  - "Constant Rounds"
  - "Guaranteed Complexity"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The traditional setting for concurrent zero knowledge considers a server that proves a statement in zero-knowledge to multiple clients in multiple concurrent sessions, where the server’s actions in a session are independent of all other sessions. Persiano and Visconti [ICALP 05] show how keeping a limited amount of global state across sessions allows the server to significantly reduce the overall complexity while retaining the ability to interact concurrently with an unbounded number of clients.

## Key claims (as reported)
- Specifically, they show a protocol that has only slightly super-constant number of rounds; however the communication complexity in each session of their protocol depends on the number of other sessions and has no a-priori bound.
- This has the drawback that the client has no way to know in advance the amount of resources required for completing a session of the protocol up to the moment where the session is completed.
- We show a protocol that does not have this drawback.
- Specifically, in our protocol the client obtains a bound on the communication complexity of each session at the start of the session.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160225 (1).pdf`
- `downloads/86160225 (2).pdf`
- `downloads/86160225 (3).pdf`
- `downloads/86160225 (4).pdf`
- `downloads/86160225 (5).pdf`
- `downloads/86160225 (6).pdf`
- (+1 more duplicate copies)
