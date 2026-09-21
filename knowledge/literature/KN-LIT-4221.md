---
id: KN-LIT-4221
type: literature
title: "Highly Efficient GF (28 ) Inversion Circuit Based on Redundant GF Arithmetic and Its Application to AES Design"
authors:
  - "Rei Ueno"
  - "Naofumi Homma"
  - "Yukihiro Sugawara"
  - "Yasuyuki Nogami"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes a compact and efficient GF (28 ) inversion circuit design based on a combination of non-redundant and redundant Galois Field (GF) arithmetic. The proposed design utilizes redundant GF representations, called Polynomial Ring Representation (PRR) and Redundantly Represented Basis (RRB), to implement GF (28 ) inversion using a tower field GF ((24 )2 ).

## Key claims (as reported)
- In addition to the redundant representations, we introduce a specific normal basis that makes it possible to map the former components for the 16th and 17th powers of input onto logic gates in an efficient manner.
- The latter components for GF (24 ) inversion and GF (24 ) multiplication are then implemented by PRR and RRB, respectively.
- The flexibility of the redundant representations provides efficient mappings from/to the GF (28 ).
- This paper also evaluates the efficacy of the proposed circuit by means of gate counts and logic synthesis with a 65 nm CMOS standard cell library and comparisons with conventional circuits, including those with tower fields GF (((22 )2 )2 ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930061 (1).pdf`
- `downloads/92930061.pdf`
