---
id: KN-LIT-6399
type: literature
title: "Secret External Encodings Do not Prevent"
authors:
  - "Transient Fault Analysis"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Contrarily to Kerckhoffs’ principle, many applications of today’s cryptography still adopt the security by obscurity paradigm. Furthermore, in order to rely on its proven or empirical security, some realizations are based on a given well known and widely used cryptographic algorithm.

## Key claims (as reported)
- In particular, a possible design would obfuscate a standard block cipher E by surrounding it with two secret external encodings P1 and P2 (one-to-one mappings), leading to the proprietary algorithm E’ = P2 ◦ E ◦ P1 .
- A claimed advantage of this approach is that, since inputs and outputs of the underlying function E are not known by a potential attacker, such a construction is usually believed to inherently prevent any kind of transient fault analysis that may apply on the core function E.
- In this paper, we show that this latter argument is not true, by exhibiting a key recovery attack which applies to the whole class of externally encoded DES or Triple-DES.
- Moreover, our attack remains applicable even in the presence of the classical counter-measure against fault attacks which consists in executing the algorithm twice and returning an output only if both results are identical.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270181 (1).pdf`
- `downloads/47270181 (2).pdf`
- `downloads/47270181 (3).pdf`
- `downloads/47270181.pdf`
