---
id: KN-LIT-fd27c2
type: literature
title: "Analysis and Optimization of Cryptographically Generated Addresses"
authors:
  - "Joppe W. Bos"
  - "Onur Özen"
  - "Jean-Pierre Hubaux"
year: null
venue: "manuscript (EPFL/ENAC preprint)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [cga, addresses, networking, privacy, hash, optimization]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Studies cryptographically generated addresses (CGA) for IPv6: how hosts
generate self-certifying addresses without a trusted authority, the attack
models that arise in practice, and optimization of the CGA computation
("modifier" search). Combines an address-ownership analysis with concrete
optimized implementations of the hash-based address generation.

## Key claims (as reported)
- Re-investigates attack models for CGA-like self-certifying addresses.
- Provides analysis of the CGA binding and an optimized CGA implementation.

## Relevance
- Hash-based address generation is a source of "birthday-like" computational
  effort; relevant as a comparative constant for the cost of hash-based
  constructions used in the program's commitment/hashing contexts, not the
  ECDLP core this program studies.

## Not verified here
- Entry generated during the 2026-08-07 sweep from the local first pages;
  full security analysis marking of the CGA paper not verified beyond the
  opened sections.