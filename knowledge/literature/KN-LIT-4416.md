---
id: KN-LIT-4416
type: literature
title: "Improved Linear Hull Attack on Round-Reduced Simon with Dynamic Key-guessing Techniques"
authors:
  - "Huaifeng Chen"
  - "Xiaoyun Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Simon is a lightweight block cipher family proposed by NSA in 2013. It has drawn many cryptanalysts’ attention and varieties of cryptanalysis results have been published, including differential, linear, impossible differential, integral cryptanalysis and so on.

## Key claims (as reported)
- In this paper, we give the improved linear attacks on all reduced versions of Simon with dynamic key-guessing technique, which was proposed to improve the differential attack on Simon recently.
- By establishing the boolean function of parity bit in the linear hull distinguisher and reducing the function according to the property of AND operation, we can guess different subkeys (or equivalent subkeys) for different situations, which decrease the number of key bits involved in the attack and decrease the time complexity in a further step.
- As a result, 23-round Simon32/64, 24-round Simon48/72, 25-round Simon48/96, 30-round Simon64/96, 31-round Simon64/128, 37-round Simon96/96, 38-round Simon96/144, 49-round Simon128/128, 51-round Simon128/192 and 53-round Simon128/256 can be attacked.
- As far as we know, our attacks on most reduced versions of Simon are the best compared with the previous cryptanalysis results.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830407 (1).pdf`
- `downloads/97830407.pdf`
