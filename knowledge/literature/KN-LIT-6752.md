---
id: KN-LIT-6752
type: literature
title: "Some thoughts on security after ten years of qmail 1.0"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The qmail software package is a widely used Internet-mail transfer agent that has been covered by a security guarantee since 1997. In this paper, the qmail author reviews the history and security-relevant architecture of qmail; articulates partitioning standards that qmail fails to meet; analyzes the engineering that has allowed qmail to survive this failure; and draws various conclusions regarding the future of secure programming.

## Key claims (as reported)
- Internet at the time; see, e.g., [4].
- Here’s what I wrote in the qmail documentation in December 1995: Every few months CERT announces Yet Another Security Hole In Sendmail—something that lets local or even remote users take complete control of the machine.
- I’m sure there are many more holes waiting to be discovered; Sendmail’s design means that any minor bug in 41000 lines of code is a major security risk.
- Other popular mailers, such as Smail, and even mailing-list managers, such as Majordomo, seem just as bad.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/qmailsec-20071101.pdf`
