---
id: KN-LIT-4449
type: literature
title: "Improving Attacks on Round-Reduced"
authors:
  - "Speck/ Using Deep Learning"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper has four main contributions.1 First, we calculate the predicted difference distribution of Speck32/64 with one specific input difference under the Markov assumption completely for up to eight rounds and verify that this yields a globally fairly good model of the difference distribution of Speck32/64. Secondly, we show that contrary to conventional wisdom, machine learning can produce very powerful cryptographic distinguishers: for instance, in a simple low-data, chosen plaintext attack on nine rounds of Speck, we present distinguishers based on deep residual neural networks that achieve a mean key rank roughly five times lower than an analogous classical distinguisher using the full difference distribution table.

## Key claims (as reported)
- Thirdly, we develop a highly selective key search policy based on a variant of Bayesian optimization which, together with our neural distinguishers, can be used to reduce the remaining security of 11-round Speck32/64 to roughly 38 bits.
- This is a significant improvement over previous literature.
- Lastly, we show that our neural distinguishers successfully use features of the ciphertext pair distribution that are invisible to all purely differential distinguishers even given unlimited data.
- While our attack is based on a known input difference taken from the literature, we also show that neural networks can be used to rapidly (within a matter of minutes on our machine) find good input differences without using prior human cryptanalysis.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940142 (1).pdf`
- `downloads/116940142.pdf`
