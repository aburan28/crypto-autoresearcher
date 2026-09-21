---
id: KN-LIT-2277
type: literature
title: "A Universally Composable Framework for the Privacy of Email Ecosystems"
authors:
  - "Pyrros Chaidos"
  - "Olga Fourtounelli"
  - "Aggelos Kiayias"
  - "Thomas Zacharias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Email communication is amongst the most prominent online activities, and as such, can put sensitive information at risk. It is thus of high importance that internet email applications are designed in a privacy-aware manner and analyzed under a rigorous threat model.

## Key claims (as reported)
- The Snowden revelations (2013) suggest that such a model should feature a global adversary, in light of the observational tools available.
- Furthermore, the fact that protecting metadata can be of equal importance as protecting the communication context implies that end-to-end encryption may be necessary, but it is not sufficient.
- With this in mind, we utilize the Universal Composability framework [Canetti, 2001] to introduce an expressive cryptographic model for email “ecosystems” that can formally and precisely capture various well-known privacy notions (unobservability, anonymity, unlinkability, etc.), by parameterizing the amount of leakage an ideal-world adversary (simulator) obtains from the email functionality.
- Equipped with our framework, we present and analyze the security of two email constructions that follow different directions in terms of the efficiency vs. privacy tradeoff.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272313 (1).pdf`
- `downloads/11272313.pdf`
