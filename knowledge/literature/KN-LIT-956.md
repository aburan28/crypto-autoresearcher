---
id: KN-LIT-956
type: literature
title: "Beyond the Csiszár-Korner Bound: Best-Possible Wiretap Coding via Obfuscation"
authors:
  - "Yuval Ishai"
  - "Alexis Korb"
  - "Paul Lou"
  - "Amit Sahai"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/343"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/343"
tags: [mpc, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A wiretap coding scheme (Wyner, Bell Syst. 1975) enables Alice to reliably communicate a message m to an honest Bob by sending an encoding c over a noisy channel ChB, while at the same time hiding m from Eve who receives c over another noisy channel ChE.

## Key claims (as reported)
- Wiretap coding is clearly impossible when ChB is a degraded version of ChE, in the sense that the output of ChB can be simulated using only the output of ChE.
- A classic work of Csiszár and Korner (IEEE Trans.
- Theory, 1978) shows that the converse does not hold.
- This follows from their full characterization of the channel pairs (ChB, ChE) that enable information-theoretic wiretap coding.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070237 (1).pdf`
- `downloads/135070237.pdf`
