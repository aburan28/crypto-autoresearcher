---
id: KN-LIT-3704
type: literature
title: "Equivalent Key Recovery Attacks against HMAC and NMAC with Whirlpool Reduced to 7 Rounds"
authors:
  - "Jian Guo"
  - "Yu Sasaki"
  - "Lei Wang"
  - "Meiqin Wang"
  - "Long Wen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A main contribution of this paper is an improved analysis against HMAC instantiating with reduced Whirlpool. It recovers equivalent keys, which are often denoted as Kin and Kout , of HMAC with 7-round Whirlpool, while the previous best attack can work only for 6 rounds.

## Key claims (as reported)
- Our approach is applying the meet-in-the-middle (MITM) attack on AES to recover MAC keys of Whirlpool.
- Several techniques are proposed to bypass different attack scenarios between a block cipher and a MAC, e.g., the chosen plaintext model of the MITM attacks on AES cannot be used for HMAC-Whirlpool.
- Besides, a larger state size and different key schedule designs of Whirlpool leave us a lot of room to study.
- As a result, equivalent keys of HMAC with 7-round Whirlpool are recovered with a complexity of (Data, Time, Memory) = (2481.7 , 2482.3 , 2481 ).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400173 (1).pdf`
- `downloads/85400173 (2).pdf`
- `downloads/85400173 (3).pdf`
- `downloads/85400173.pdf`
