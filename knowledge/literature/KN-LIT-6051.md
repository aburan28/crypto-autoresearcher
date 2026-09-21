---
id: KN-LIT-6051
type: literature
title: "Pushing the Limits of SHA-3 Hardware Implementations to Fit on RFID"
authors:
  - "Peter Pessl"
  - "Michael Hutter"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, signature, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
There exists a broad range of RFID protocols in literature that propose hash functions as cryptographic primitives. Since Keccak has been selected as the winner of the NIST SHA-3 competition in 2012, there is the question of how far we can push the limits of Keccak to fulfill the stringent requirements of passive low-cost RFID.

## Key claims (as reported)
- In this paper, we address this question by presenting a hardware implementation of Keccak that aims for lowest power and lowest area.
- Our smallest (fullstate) design requires only 2 927 GEs (for designs with external memory available) and 5 522 GEs (total size including memory).
- It has a power consumption of 12.5 μW at 1 MHz on a low leakage 130 nm CMOS process technology.
- As a result, we provide a design that needs 40 % less resources than related work.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860174 (1).pdf`
- `downloads/80860174 (2).pdf`
- `downloads/80860174 (3).pdf`
- `downloads/80860174.pdf`
