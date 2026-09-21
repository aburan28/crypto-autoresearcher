---
id: KN-LIT-2098
type: literature
title: "A Little Honesty Goes a Long Way: The Two-Tier"
authors:
  - "Aggelos Kiayias"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A fundamental result in secure multiparty computation (MPC) is that in order to achieve full security, it is necessary that a majority of the parties behave honestly. There are settings, however, where the condition of an honest majority might be overly restrictive, and there is a need to define and investigate other plausible adversarial models in order to circumvent the above impossibility.

## Key claims (as reported)
- To this end, we introduce the two-tier model for MPC, where some small subset of servers is guaranteed to be honest at the beginning of the computation (the first tier ), while the corruption state of the other servers (the second tier) is unknown.
- The two-tier model naturally arises in various settings, such as for example when a service provider wishes to utilize a large pre-existing set of servers, while being able to trust only a small fraction of them.
- The first tier is responsible for performing the secure computation while the second tier serves as a disguise: using novel anonymization techniques, servers in the first tier remain undetected to an adaptive adversary, preventing a targeted attack on these critical servers.
- Specifically, given n servers and assuming αn of them are corrupt at the onset (where α ∈ (0, 1)), we present an MPC protocol that can withstand an optimal amount of less than (1 − α)n/2 additional adaptive corruptions, provided the first tier is of size ω(log n).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90140134 (1).pdf`
- `downloads/90140134.pdf`
