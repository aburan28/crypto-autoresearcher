---
id: KN-LIT-6624
type: literature
title: "Sieve-in-the-Middle: Improved MITM Attacks"
authors:
  - "Anne Canteaut"
  - "Marı́a Naya-Plasencia"
  - "Bastien Vayssière"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a new generic technique, named sievein-the-middle, which improves meet-in-the-middle attacks in the sense that it provides an attack on a higher number of rounds. Instead of selecting the key candidates by searching for a collision in an intermediate state which can be computed forwards and backwards, we look for the existence of valid transitions through some middle sbox.

## Key claims (as reported)
- Combining this technique with short bicliques allows to freely add one or two more rounds with the same time complexity.
- Moreover, when the key size of the cipher is larger than its block size, we show how to build the bicliques by an improved technique which does not require any additional data (on the contrary to previous biclique attacks).
- These techniques apply to PRESENT, DES, PRINCE and AES, improving the previously known results on these four ciphers.
- In particular, our attack on PRINCE applies to 8 rounds (out of 12), instead of 6 in the previous cryptanalyses.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420191 (1).pdf`
- `downloads/80420191 (2).pdf`
- `downloads/80420191 (3).pdf`
- `downloads/80420191.pdf`
