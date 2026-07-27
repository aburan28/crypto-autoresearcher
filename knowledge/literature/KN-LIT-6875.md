---
id: KN-LIT-6875
type: literature
title: "Successfully Attacking Masked AES Hardware Implementations"
authors:
  - "Stefan Mangard"
  - "Norbert Pramstaller"
  - "Elisabeth Oswald"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
During the last years, several masking schemes for AES have been proposed to secure hardware implementations against DPA attacks. In order to investigate the effectiveness of these countermeasures in practice, we have designed and manufactured an ASIC.

## Key claims (as reported)
- The chip features an unmasked and two masked AES-128 encryption engines that can be attacked independently.
- In addition to conventional DPA attacks on the output of registers, we have also mounted attacks on the output of logic gates.
- Based on simulations and physical measurements we show that the unmasked and masked implementations leak side-channel information due to glitches at the output of logic gates.
- It turns out that masking the AES S-Boxes does not prevent DPA attacks, if glitches occur in the circuit.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/012 (1).pdf`
- `downloads/012 (2).pdf`
- `downloads/012 (3).pdf`
- `downloads/012.pdf`
