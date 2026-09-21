---
id: KN-LIT-7089
type: literature
title: "The Wonderful World of Global Random Oracles Jan Camenisch1 , Manu Drijvers1,2 , Tommaso Gagliardoni1"
authors:
  - "Anja Lehmann"
  - "Gregory Neven"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The random-oracle model by Bellare and Rogaway (CCS’93) is an indispensable tool for the security analysis of practical cryptographic protocols. However, the traditional random-oracle model fails to guarantee security when a protocol is composed with arbitrary protocols that use the same random oracle.

## Key claims (as reported)
- Canetti, Jain, and Scafuro (CCS’14) put forth a global but non-programmable random oracle in the Generalized UC framework and showed that some basic cryptographic primitives with composable security can be efficiently realized in their model.
- Because their random-oracle functionality is non-programmable, there are many practical protocols that have no hope of being proved secure using it.
- In this paper, we study alternative definitions of a global random oracle and, perhaps surprisingly, show that these allow one to prove GUCsecure existing, very practical realizations of a number of essential cryptographic primitives including public-key encryption, non-committing encryption, commitments, Schnorr signatures, and hash-and-invert signatures.
- Some of our results hold generically for any suitable scheme proven secure in the traditional ROM, some hold for specific constructions only.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822321 (1).pdf`
- `downloads/10822321.pdf`
