---
id: KN-LIT-3291
type: literature
title: "Cryptanalytic Extraction of Neural Network Models"
authors:
  - "Nicholas Carlini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, mpc, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We argue that the machine learning problem of model extraction is actually a cryptanalytic problem in disguise, and should be studied as such. Given oracle access to a neural network, we introduce a differential attack that can efficiently steal the parameters of the remote model up to floating point precision.

## Key claims (as reported)
- Our attack relies on the fact that ReLU neural networks are piecewise linear functions, and thus queries at the critical points reveal information about the model parameters.
- We evaluate our attack on multiple neural network models and extract models that are 220 times more precise and require 100× fewer queries than prior work.
- For example, we extract a 100,000 parameter neural network trained on the MNIST digit recognition task with 221.5 queries in under an hour, such that the extracted model agrees with the oracle on all inputs up to a worst-case error of 2−25 , or a model with 4,000 parameters in 218.5 queries with worst-case error of 2−40.4 .
- Code is available at https://github.com/google-research/cryptanalytic-model-extraction.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171088 (1).pdf`
- `downloads/12171088.pdf`
