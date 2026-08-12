---
id: KN-LIT-2093
type: literature
title: "A Leakage-Resilient Mode of Operation Krzysztof Pietrzak"
authors:
  - "CWI Amsterdam"
  - "The Netherlands"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A weak pseudorandom function (wPRF) is a cryptographic primitive similar to – but weaker than – a pseudorandom function: for wPRFs one only requires that the output is pseudorandom when queried on random inputs. We show that unlike “normal” PRFs, wPRFs are seedincompressible, in the sense that the output of a wPRF is pseudorandom even if a bounded amount of information about the key is leaked.

## Key claims (as reported)
- As an application of this result we construct a simple mode of operation which – when instantiated with any wPRF – gives a leakage-resilient stream-cipher.
- The implementation of such a cipher is secure against every side-channel attack, as long as the amount of information leaked per round is bounded, but overall can be arbitrary large.
- The construction is simpler than the previous one (Dziembowski-Pietrzak FOCS’08) as it only uses a single primitive (a wPRF) in a straight forward manner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790461 (1).pdf`
- `downloads/54790461 (2).pdf`
- `downloads/54790461 (3).pdf`
- `downloads/54790461 (4).pdf`
- `downloads/54790461.pdf`
