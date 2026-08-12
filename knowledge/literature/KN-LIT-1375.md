---
id: KN-LIT-1375
type: literature
title: "Distinguishing Full-Round AES-256 in a Ciphertext-Only Setting via Hybrid Statistical Learning"
authors:
  - "Gopal Singh"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/862"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/862"
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of block ciphers such as AES-128, AES-192, and AES-256 relies on the assumption that their ciphertext outputs are computationally indistinguishable from random permutations. While distinguishers have been proposed for reduced-round variants or under nonstandard models such as known-key or chosen-key settings, no effective distinguisher has been demonstrated for the full-round AES ciphers in the standard secret-key model.

## Key claims (as reported)
- This work introduces FESLA (Feature Enhanced Statistical Learning Attack), a hybrid statistical learning framework that integrates outputs from a suite of classical statistical tests with machine learning and deep learning classifiers to construct ciphertext-only distinguishers for AES-128, AES-192, and AES-256.
- In contrast to existing approaches based on handcrafted or bitwise features, FESLA aggregates intermediate statistical metrics as features, enabling the capture of persistent structural biases in ciphertext distributions.
- Experimental evaluation across multiple datasets demonstrates consistent 100% classification accuracy using Support Vector Machines, Random Forests, Multi-Layer Perceptrons, Logistic Regression, and Naive Bayes classifiers.
- Generalization and robustness are confirmed through k-fold cross-validation, including on previously unseen ciphertext samples.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-862.pdf`
