---
id: KN-LIT-7518
type: literature
title: "Wild McEliece"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christiane Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hyperelliptic, pairing, pqc, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The original McEliece cryptosystem uses length-n codes over F2 with dimension ≥ n − mt efficiently correcting t errors where 2m ≥ n. This paper presents a generalized cryptosystem that uses length-n codes over small finite fields Fq with dimension ≥ n − m(q − 1)t efficiently correcting bqt/2c errors where q m ≥ n.

## Key claims (as reported)
- Previously proposed cryptosystems with the same length and dimension corrected only b(q − 1)t/2c errors for q ≥ 3.
- This paper also presents list-decoding algorithms that efficiently correct even more errors for the same codes over Fq .
- Finally, this paper shows that the increase from b(q − 1)t/2c errors to more than bqt/2c errors allows considerably smaller keys to achieve the same security level against all known attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/wild-20101007.pdf`
