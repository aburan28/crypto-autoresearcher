---
id: KN-OPEN-014
type: open_problem
title: What is the concrete quantum security of CSIDH, and how large must parameters be given the Kuperberg-sieve cost?
tags: [csidh, quantum-security, kuperberg, hidden-shift, parameter-sizing, class-group-action, post-quantum, open, adjacent]
confidence: reported
status: open
source_refs: [KN-LIT-069, KN-LIT-071]
added: 2026-07-23
superseded_by: null
---

## Statement
CSIDH's security against quantum attack reduces to the abelian hidden-shift
problem solved by Kuperberg's sieve (KN-LIT-071), which is subexponential
2^{O(sqrt(log p))} but with contested CONCRETE constants and memory/query
trade-offs. What is the true concrete quantum cost, and hence how large must the
CSIDH prime p be for a given security level -- CSIDH-512, -1024, or much larger?

## Current state (as reported)
The asymptotic subexponential bound is settled (KN-LIT-071), but concrete
estimates of the Kuperberg-sieve cost (including quantum memory, oracle-call cost
of evaluating the class-group action, and query counts) vary widely across
analyses, and successive works have argued CSIDH-512 offers much less quantum
security than first hoped -- pushing proposed parameters substantially larger and
slower. This is an ADJACENT (post-quantum) question, not the program's ECDLP
mission. Unlike SIDH, CSIDH was NOT broken in 2022 (no torsion images,
KN-TECH-027).

## Why it matters here
It is the quantum-cost-model analogue of the program's fully-charged cost
accounting: the security claim hinges on a precise cost model for a specific
algorithm over a group action, exactly the discipline the program applies to
ECDLP attacks. The class-group action and orientation structure are the program's
own objects (ISO-AR). Recorded to document the surviving commutative branch's open
sizing question; no program result is claimed.
