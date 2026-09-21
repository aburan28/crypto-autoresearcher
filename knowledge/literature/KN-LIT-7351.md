---
id: KN-LIT-7351
type: literature
title: "Unconditionally Secure and Universally Composable Commitments from Physical Assumptions"
authors:
  - "Ivan Damgård"
  - "Alessandra Scafuro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a constant-round unconditional black-box compiler that transforms any ideal (i.e., statistically-hiding and statisticallybinding) straight-line extractable commitment scheme, into an extractable and equivocal commitment scheme, therefore yielding to UC-security [9]. We exemplify the usefulness of our compiler by providing two (constantround) instantiations of ideal straight-line extractable commitment based on (malicious) PUFs [36] and stateless tamper-proof hardware tokens [26], therefore achieving the first unconditionally UC-secure commitment with malicious PUFs and stateless tokens, respectively.

## Key claims (as reported)
- Our constructions are secure for adversaries creating arbitrarily malicious stateful PUFs/tokens.
- Previous results with malicious PUFs used either computational assumptions to achieve UC-secure commitments or were unconditionally secure but only in the indistinguishability sense [36].
- Similarly, with stateless tokens, UC-secure commitments are known only under computational assumptions [13,24,15], while the (not UC) unconditional commitment scheme of [23] is secure only in a weaker model in which the adversary is not allowed to create stateful tokens.
- Besides allowing us to prove feasibility of unconditional UC-security with (malicious) PUFs and stateless tokens, our compiler can be instantiated with any ideal straight-line extractable commitment scheme, thus allowing the use of various setup assumptions which may better fit the application or the technology available.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700102 (1).pdf`
- `downloads/82700102 (2).pdf`
- `downloads/82700102 (3).pdf`
- `downloads/82700102.pdf`
