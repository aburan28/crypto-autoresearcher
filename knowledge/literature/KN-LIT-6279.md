---
id: KN-LIT-6279
type: literature
title: "Richer Efficiency/Security Trade-offs in 2PC"
authors:
  - "Vladimir Kolesnikov"
  - "Payman Mohassel"
  - "Ben Riva"
  - "Mike Rosulek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The dual-execution protocol of Mohassel & Franklin (PKC 2006) is a highly efficient (each party garbling only one circuit) 2PC protocol that achieves malicious security apart from leaking an arbitrary, adversarially-chosen predicate about the honest party’s input. We present two practical and orthogonal approaches to improve the security of the dual-execution technique.

## Key claims (as reported)
- First, we show how to greatly restrict the predicate that an adversary can learn in the protocol, to a natural notion of “only computation leaks”style leakage.
- Along the way, we identify a natural security property of garbled circuits called property-enforcing that may be of independent interest.
- Second, we address a complementary direction of reducing the probability that the leakage occurs.
- We propose a new dual-execution protocol — with a very light cheating-detection phase and each party garbling s + 1 circuits — in which a cheating party learns a bit with probability only 2−s .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90140230 (1).pdf`
- `downloads/90140230.pdf`
