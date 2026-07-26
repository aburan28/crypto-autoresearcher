---
id: KN-LIT-3865
type: literature
title: "Feasibility and Infeasibility of Secure Computation with Malicious PUFs"
authors:
  - "Dana Dachman-Soled"
  - "Nils Fleischhacker"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A recent line of work has explored the use of physically uncloneable functions (PUFs) for secure computation, with the goals of (1) achieving universal composability without (additional) setup, and/or (2) obtaining unconditional security (i.e., avoiding complexity-theoretic assumptions). Initial work assumed that all PUFs, even those created by an attacker, are honestly generated.

## Key claims (as reported)
- Subsequently, researchers have investigated models in which an adversary can create malicious PUFs with arbitrary behavior.
- Researchers have considered both malicious PUFs that might be stateful, as well as malicious PUFs that can have arbitrary behavior but are guaranteed to be stateless.
- We settle the main open questions regarding secure computation in the malicious-PUF model: – We prove that unconditionally secure oblivious transfer is impossible, even in the stand-alone setting, if the adversary can construct (malicious) stateful PUFs. – We show that universally composable two-party computation is possible if the attacker is limited to creating (malicious) stateless PUFs.
- Our protocols are simple and efficient, and do not require any cryptographic assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160282 (1).pdf`
- `downloads/86160282 (2).pdf`
- `downloads/86160282 (3).pdf`
- `downloads/86160282 (4).pdf`
- `downloads/86160282 (5).pdf`
- `downloads/86160282 (6).pdf`
- (+1 more duplicate copies)
