---
id: KN-LIT-c0a19f
type: literature
title: "Modeling bit flipping decoding based on nonorthogonal check sums with application to iterative decoding attack of McEliece cryptosystem"
authors:
  - "Marc P. C. Fossorier"
  - "Kazukuni Kobara"
  - "Hideki Imai"
year: 2007
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/tit.2006.887515"
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, bit-flipping, iterative-decoding, ldpc, attack-modelling]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Models **bit-flipping decoding with non-orthogonal check sums**, and applies it
as an iterative decoding attack on McEliece. Bit-flipping is the standard
LDPC/MDPC decoder; the analysis addresses the case where the parity checks are
not orthogonal, which is what happens when the checks come from an attacker's
construction rather than a designed code.

## Key claims (as reported)
- A model of bit-flipping decoding under non-orthogonal check sums.
- An iterative decoding attack on McEliece follows from the model.

## Relevance to this program
Held for the **decoder-as-attack** framing: a decoding algorithm designed for
error correction becomes an attack when pointed at a cryptographic instance.
The same duality that makes [[KN-LIT-bbd0e9]] (Leon) a cryptanalytic tool.

Also the theoretical ancestor of the decoding-failure-rate analysis that
dominates BIKE's security argument today — where the *failure* probability of
an iterative decoder, not its success, is the security-relevant quantity. Held
as an example of a security property that lives in the tail of a distribution
rather than in a worst-case bound, which is a shape this program should expect
in its own measurements.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/tit.2006.887515).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The model's accuracy and the attack's effectiveness against McEliece parameters
are NOT recorded here. No online copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
