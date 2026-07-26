---
id: KN-LIT-590
type: literature
title: "Cache-Attacks on the ARM TrustZone implementations of AES-256 and AES-256-GCM via GPU-based analysis"
authors:
  - "Ben Lapid"
  - "Avishai Wool"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/621"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/621"
tags: [cryptanalysis, mov-fr, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The ARM TrustZone is a security extension which is used in recent Samsung flagship smartphones to create a Trusted Execution Environment (TEE) called a Secure World, which runs secure processes (Trustlets). The Samsung TEE includes cryptographic key storage and functions inside the Keymaster trustlet.

## Key claims (as reported)
- The secret key used by the Keymaster trustlet is derived by a hardware device and is inaccessible to the Android OS.
- However, the ARM32 AES implementation used by the Keymaster is vulnerable to side channel cache-attacks.
- The Keymaster trustlet uses AES-256 in GCM mode, which makes mounting a cache attack against this target much harder.
- In this paper we show that it is possible to perform a successful cache attack against this AES implementation, in AES256/GCM mode, using widely available hardware.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-621.pdf`
