---
id: KN-LIT-4110
type: literature
title: "Get Your Hands Off My Laptop: Physical Side-Channel Key-Extraction Attacks on PCs"
authors:
  - "Daniel Genkin"
  - "Itamar Pipman"
  - "Eran Tromer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, quantum, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We demonstrate physical side-channel attacks on a popular software implementation of RSA and ElGamal, running on laptop computers. Our attacks use novel side channels, based on the observation that the “ground” electric potential, in many computers, fluctuates in a computation-dependent way.

## Key claims (as reported)
- An attacker can measure this signal by touching exposed metal on the computer’s chassis with a plain wire, or even with a bare hand.
- The signal can also be measured at the remote end of Ethernet, VGA or USB cables.
- Through suitable cryptanalysis and signal processing, we have extracted 4096-bit RSA keys and 3072-bit ElGamal keys from laptops, via each of these channels, as well as via power analysis and electromagnetic probing.
- Despite the GHz-scale clock rate of the laptops and numerous noise sources, the full attacks require a few seconds of measurements using Medium Frequency signals (around 2 MHz), or one hour using Low Frequency signals (up to 40 kHz).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310202 (1).pdf`
- `downloads/87310202 (2).pdf`
- `downloads/87310202 (3).pdf`
- `downloads/87310202.pdf`
