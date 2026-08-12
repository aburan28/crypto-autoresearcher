---
id: KN-LIT-4417
type: literature
title: "Improved Linear Sieving Techniques with Applications to Step-Reduced LED-64"
authors:
  - "Itai Dinur"
  - "Orr Dunkelman"
  - "Nathan Keller"
  - "Adi Shamir"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present advanced meet-in-the-middle (MITM) attacks against the lightweight block cipher LED-64, improving the best known attacks on several step-reduced variants of the cipher in both single-key and related-key models. In particular, we present a knownplaintext attack on 2-step LED-64 with complexity of 248 and a relatedkey attack on 3-step LED-64 with complexity of 249 .

## Key claims (as reported)
- In both cases, the previously known attacks have complexity of 260 , i.e., only 16 times faster than exhaustive key search.
- While our attacks are applied to the specific scheme of LED-64, they contain several general methodological contributions: First, we present the linear key sieve technique, which allows to exploit linear dependencies between key bits to obtain filtering conditions in MITM attacks on block ciphers.
- While similar ideas have been previously used in the domain of hash functions, this is the first time that such a technique is applied in block cipher cryptanalysis.
- As a second contribution, we demonstrate for the first time that a splice-and-cut attack (which so far seemed to be an inherently chosen-plaintext technique) can be used in the knownplaintext model, with data complexity which is significantly below the code-book size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400119 (1).pdf`
- `downloads/85400119 (2).pdf`
- `downloads/85400119 (3).pdf`
- `downloads/85400119.pdf`
