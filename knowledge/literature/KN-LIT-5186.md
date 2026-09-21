---
id: KN-LIT-5186
type: literature
title: "Non-Interactive Multiparty Computation"
authors:
  - "Without Correlated Randomness"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of non-interactive multiparty computation (NI-MPC) where a group of completely asynchronous parties can evaluate a function over their joint inputs by sending a single message to an evaluator who computes the output. Previously, the only general solutions to this problem that resisted collusions between the evaluator and a set of parties were based on multi-input functional encryption and required the use of complex correlated randomness setup.

## Key claims (as reported)
- In this work, we present a new solution for NI-MPC against arbitrary collusions using a public-key infrastructure (PKI) setup supplemented with a common random string.
- A PKI is, in fact, the minimal setup that one can hope for in this model in order to achieve a meaningful “best possible” notion of security, namely, that an adversary that corrupts the evaluator and an arbitrary set of parties only learns the residual function obtained by restricting the function to the inputs of the uncorrupted parties.
- Our solution is based on indistinguishability obfuscation and DDH both with sub-exponential security.
- We extend this main result to the case of general interaction patterns, providing the above best possible security that is achievable for the given interaction.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240203 (1).pdf`
- `downloads/106240203.pdf`
