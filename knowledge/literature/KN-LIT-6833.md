---
id: KN-LIT-6833
type: literature
title: "Stronger security bounds for Wegman-Carter-Shoup authenticators"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Shoup proved that various message-authentication codes of the form p (n, m) 7→ h(m) + f (n) are secure against all attacks that see at most 1/ authenticated messages. Here m is a message; n is a nonce chosen from a public group G; f is a secret uniform random permutation of G; h is a secret random function; and  is a differential probability associated with h.

## Key claims (as reported)
- Shoup’s result implies that if AES is secure then various state-of-the-art message-authentication codes of the form (n, m) 7→ h(m) + p AESk (n) are p secure up to 1/ authenticated messages.
- Unfortunately, 1/ is only about 250 for some state-of-the-art systems, so Shoup’s result provides no guarantees for long-term keys.
- This paper proves that security of the same systems is retained √ up to √ #G authenticated messages.
- In a typical state-of-the-art system, #G is 264 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/securitywcs-20050227.pdf`
