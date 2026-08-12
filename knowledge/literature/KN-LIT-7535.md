---
id: KN-LIT-7535
type: literature
title: "Your Rails Cannot Hide From Localized EM: How Dual-Rail Logic Fails on FPGAs"
authors:
  - "Vincent Immler"
  - "Robert Specht"
  - "Florian Unterstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mov-fr, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protecting cryptographic implementations against side-channel attacks is a must to prevent leakage of processed secrets. As a celllevel countermeasure, so called DPA-resistant logic styles have been proposed to prevent a data-dependent power consumption.

## Key claims (as reported)
- As most of the DPA-resistant logic is based on dual-rails, properly implementing them is a challenging task on FPGAs which is due to their fixed architecture and missing freedom in the design tools.
- While previous works show a significant security gain when using such logic on FPGAs, we demonstrate this only holds for power-analysis.
- In contrast, our attack using high-resolution electromagnetic analysis is able to exploit local characteristics of the placement and routing such that only a marginal security gain remains, therefore creating a severe threat.
- To further analyze the properties of both attack and implementation, we develop a custom placer to improve the default placement of the analyzed AES S-box.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529127 (1).pdf`
- `downloads/10529127.pdf`
