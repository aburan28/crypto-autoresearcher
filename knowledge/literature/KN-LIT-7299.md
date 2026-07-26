---
id: KN-LIT-7299
type: literature
title: "Two-Message, Oblivious Evaluation of Cryptographic Functionalities"
authors:
  - "Nico Döttling"
  - "Nils Fleischhacker"
  - "Johannes Krupp"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of two round oblivious evaluation of cryptographic functionalities. In this setting, one party P1 holds a private key sk for a provably secure instance of a cryptographic functionality F and the second party P2 wishes to evaluate Fsk on a value x.

## Key claims (as reported)
- Although it has been known for 22 years that general functionalities cannot be computed securely in the presence of malicious adversaries with only two rounds of communication, we show the existence of a round optimal protocol that obliviously evaluates cryptographic functionalities.
- Our protocol is provably secure against malicious receivers under standard assumptions and does not rely on heuristic (setup) assumptions.
- Our main technical contribution is a novel nonblack-box technique, which makes nonblack-box use of the security reduction of Fsk .
- Specifically, our proof of malicious receiver security uses the code of the reduction, which reduces the security of Fsk to some hard problem, in order to break that problem directly.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160604 (1).pdf`
- `downloads/98160604.pdf`
