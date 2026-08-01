---
id: KN-LIT-3857
type: literature
title: "Fault Sensitivity Analysis Yang Li1 , Kazuo Sakiyama1 , Shigeto Gomisawa1 , Toshinori Fukunaga2"
authors:
  - "Junko Takahashi"
  - "Kazuo Ohta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes a new fault-based attack called the Fault Sensitivity Analysis (FSA) attack, which unlike most existing fault-based analyses including Differential Fault Analysis (DFA) does not use values of faulty ciphertexts. Fault sensitivity means the critical condition when a faulty output begins to exhibit some detectable characteristics, e.g., the clock frequency when fault operation begins to occur.

## Key claims (as reported)
- We explain that the fault sensitivity exhibits sensitive-data dependency and can be used to retrieve the secret key.
- This paper presents two practical FSA attacks against two AES hardware implementations on SASEBOR, PPRM1-AES and WDDL-AES.
- Different from previous work, we show that WDDL-AES is not perfectly secure against setup-time violation attacks.
- We also discuss a masking technique as a potential countermeasure against the proposed fault-based attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250310 (1).pdf`
- `downloads/62250310 (2).pdf`
- `downloads/62250310 (3).pdf`
- `downloads/62250310.pdf`
