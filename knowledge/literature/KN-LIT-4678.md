---
id: KN-LIT-4678
type: literature
title: "Leakage-Flexible CCA-secure Public-Key Encryption: Simple Construction and Free of Pairing"
authors:
  - "Baodong Qin"
  - "Shengli Liu"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In AsiaCrypt 2013, Qin and Liu proposed a new approach to CCA-security of Public-Key Encryption (PKE) in the presence of bounded key-leakage, from any universal hash proof system (due to Cramer and Shoup) and any one-time lossy filter (a simplified version of lossy algebraic filters, due to Hofheinz). They presented two instantiations under the DDH and DCR assumptions, which result in leakage rate (defined as the ratio of leakage amount to the secret-key length) of 1/2 − o(1).

## Key claims (as reported)
- In this paper, we extend their work to broader assumptions and to flexible leakage rate, more specifically to leakage rate of 1 − o(1). – We introduce the Refined Subgroup Indistinguishability (RSI) assumption, which is a subclass of subgroup indistinguishability assumptions, including many standard number-theoretical assumptions, like the quadratic residuosity assumption, the decisional composite residuosity assumption and the subgroup decision assumption over a group of known order defined by Boneh et al. – We show that universal hash proof (UHP) system and one-time lossy filter (OT-LF) can be simply and efficiently constructed from the RSI assumption.
- Applying Qin and Liu’s paradigm gives simple and efficient PKE schemes under the RSI assumption. – With the RSI assumption over a specific group (free of pairing), public parameters of UHP and OT-LF can be chosen in a flexible way, resulting in a leakage-flexible CCA-secure PKE scheme.
- More specifically, we get the first CCA-secure PKE with leakage rate of 1 − o(1) without pairing.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830144 (1).pdf`
- `downloads/83830144 (2).pdf`
- `downloads/83830144 (3).pdf`
- `downloads/83830144 (4).pdf`
- `downloads/83830144 (5).pdf`
- `downloads/83830144.pdf`
