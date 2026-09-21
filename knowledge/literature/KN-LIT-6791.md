---
id: KN-LIT-6791
type: literature
title: "State Machine Replication under Changing"
authors:
  - "Network Conditions"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protocols for state machine replication (SMR) are typically designed for synchronous or asynchronous networks, with a lower corruption threshold in the latter case. Recent network-agnostic protocols are secure when run in either a synchronous or an asynchronous network.

## Key claims (as reported)
- We propose two new constructions of network-agnostic SMR protocols that improve on existing protocols in terms of either the adversarial model or communication complexity: 1. an adaptively secure protocol with optimal corruption thresholds and quadratic amortized communication complexity per transaction; 2. a statically secure protocol with near-optimal corruption thresholds and linear amortized communication complexity per transaction.
- We further explore SMR protocols run in a network that may change between synchronous and asynchronous arbitrarily often; parties can be uncorrupted (as in the proactive model), and the protocol should remain secure as long as the appropriate corruption thresholds are maintained.
- We show that purely asynchronous proactive secret sharing is impossible without some form of synchronization between the parties, ruling out a natural approach to proactively secure network-agnostic SMR protocols.
- Motivated by this negative result, we consider a model where the adversary is limited in the total number of parties it can corrupt over the duration of the protocol and show, in this setting, that our SMR protocols remain secure even under arbitrarily changing network conditions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910204 (1).pdf`
- `downloads/137910204.pdf`
