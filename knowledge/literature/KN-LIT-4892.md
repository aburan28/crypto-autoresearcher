---
id: KN-LIT-4892
type: literature
title: "Memory-Demanding Password Scrambling"
authors:
  - "Christian Forler"
  - "Stefan Lucks"
  - "Jakob Wenzel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Most of the common password scramblers hinder passwordguessing attacks by “key stretching”, e.g., by iterating a cryptographic hash function many times. With the increasing availability of cheap and massively parallel off-the-shelf hardware, iterating a hash function becomes less and less useful.

## Key claims (as reported)
- To defend against attacks based on such hardware, one can exploit their limitations regarding to the amount of fast memory for each single core.
- The first password scrambler taking this into account was scrypt.
- In this paper we mount a cache-timing attack on scrypt by exploiting its password-dependent memory-access pattern.
- Furthermore, we show that it is possible to apply an efficient password filter for scrypt based on a malicious garbage collector.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730252 (1).pdf`
- `downloads/88730252 (2).pdf`
- `downloads/88730252 (3).pdf`
- `downloads/88730252.pdf`
