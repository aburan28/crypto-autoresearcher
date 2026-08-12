---
id: KN-LIT-6818
type: literature
title: "Strengthening the Known-Key Security Notion for Block Ciphers"
authors:
  - "Benoît Cogliati"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We reconsider the formalization of known-key attacks against ideal primitive-based block ciphers. This was previously tackled by Andreeva, Bogdanov, and Mennink (FSE 2013), who introduced the notion of known-key indifferentiability.

## Key claims (as reported)
- Our starting point is the observation, previously made by Cogliati and Seurin (EUROCRYPT 2015), that this notion, which considers only a single known key available to the attacker, is too weak in some settings to fully capture what one might expect from a block cipher informally deemed resistant to known-key attacks.
- Hence, we introduce a stronger variant of known-key indifferentiability, where the adversary is given multiple known keys to “play” with, the informal goal being that the block cipher construction must behave as an independent random permutation for each of these known keys.
- Our main result is that the 9-round iterated Even-Mansour construction (with the trivial key-schedule, i.e., the same round key xored between permutations) achieves our new “multiple” known-keys indifferentiability notion, which contrasts with the previous result of Andreeva et al. that one single round is sufficient when only a single known key is considered.
- We also show that the 3-round iterated Even-Mansour construction achieves the weaker notion of multiple known-keys sequential indifferentiability, which implies in particular that it is correlation intractable with respect to relations involving any (polynomial) number of known keys.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830470 (1).pdf`
- `downloads/97830470.pdf`
