---
id: KN-LIT-4521
type: literature
title: "Instantiating Random Oracles via UCEs"
authors:
  - "Mihir Bellare"
  - "Viet Tung Hoang"
  - "Sriram Keelveedhi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper provides a (standard-model) notion of security for (keyed) hash functions, called UCE, that we show enables instantiation of random oracles (ROs) in a fairly broad and systematic way. Goals and schemes we consider include deterministic PKE; message-locked encryption; hardcore functions; point-function obfuscation; OAEP; encryption secure for key-dependent messages; encryption secure under relatedkey attack; proofs of storage; and adaptively-secure garbled circuits with short tokens.

## Key claims (as reported)
- We can take existing, natural and efficient ROM schemes and show that the instantiated scheme resulting from replacing the RO with a UCE function is secure in the standard model.
- In several cases this results in the first standard-model schemes for these goals.
- The definition of UCE-security itself is quite simple, asking that outputs of the function look random given some “leakage,” even if the adversary knows the key, as long as the leakage does not permit the adversary to compute the inputs.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420296 (1).pdf`
- `downloads/80420296 (2).pdf`
- `downloads/80420296 (3).pdf`
- `downloads/80420296.pdf`
