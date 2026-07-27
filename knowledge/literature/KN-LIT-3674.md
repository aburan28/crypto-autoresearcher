---
id: KN-LIT-3674
type: literature
title: "EnCounter: On Breaking the Nonce Barrier in Differential Fault Analysis with a Case-Study on PAEQ"
authors:
  - "Dhiman Saha"
  - "Dipanwita Roy Chowdhury"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work exploits internal differentials within a cipher in the context of Differential Fault Analysis (DFA). This in turn overcomes the nonce barrier which acts as a natural counter-measure against DFA.

## Key claims (as reported)
- We introduce the concept of internal differential fault analysis which requires only one faulty ciphertext.
- In particular, the analysis is applicable to parallelizable ciphers that use the counter-mode.
- As a proof of concept we develop an internal differential fault attack called EnCounter on PAEQ which is an AES based parallelizable authenticated cipher presently in the second round of on-going CAESAR competition.
- The attack is able to uniquely retrieve the key of three versions of full-round PAEQ of key-sizes 64, 80 and 128 bits with complexities of about 216 , 216 and 250 respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130159 (1).pdf`
- `downloads/98130159.pdf`
