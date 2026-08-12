---
id: KN-LIT-4547
type: literature
title: "Investigating SRAM PUFs"
authors:
  - "Pol Van Aubel"
  - "Daniel J. Bernstein"
  - "Ruben Niederhagen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Physically unclonable functions (PUFs) provide data that can be used for cryptographic purposes: on the one hand randomness for the initialization of random-number generators; on the other hand individual fingerprints for unique identification of specific hardware components. However, today’s off-the-shelf personal computers advertise randomness and individual fingerprints only in the form of additional or dedicated hardware.

## Key claims (as reported)
- This paper introduces a new set of tools to investigate whether intrinsic PUFs can be found in PC components that are not advertised as containing PUFs.
- In particular, this paper investigates AMD64 CPU registers as potential PUF sources in the operatingsystem kernel, the bootloader, and the system BIOS; investigates the CPU cache in the early boot stages; and investigates shared memory on Nvidia GPUs.
- This investigation found non-random non-fingerprinting behavior in several components but revealed usable PUFs in Nvidia GPUs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/cpupuf-20150729.pdf`
