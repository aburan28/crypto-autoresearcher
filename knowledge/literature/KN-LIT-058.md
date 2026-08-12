---
id: KN-LIT-058
type: literature
title: Trapdoors for Hard Lattices and New Cryptographic Constructions (GPV)
authors: [Gentry Craig, Peikert Chris, Vaikuntanathan Vinod]
year: 2008
venue: STOC 2008, pp. 197-206
identifiers:
  eprint: iacr:2007/432
  doi: 10.1145/1374376.1374407
  url: https://eprint.iacr.org/2007/432
tags: [gpv, lattice-trapdoor, preimage-sampleable, hash-and-sign, signature, ibe, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces preimage-sampleable (trapdoor) functions from lattices, assuming
worst-case lattice hardness. These yield "hash-and-sign" digital signatures
(secure in the random-oracle model) and identity-based encryption -- the GPV
framework. Discrete Gaussian sampling with a short trapdoor basis is the core
tool.

## Key claims (as reported)
- Preimage-sampleable trapdoor functions => ROM-secure hash-and-sign signatures
  and IBE from lattice assumptions.
- Simpler/faster trapdoors followed: Micciancio-Peikert, "Trapdoors for Lattices:
  Simpler, Tighter, Faster, Smaller," EUROCRYPT 2012, LNCS 7237:700-718
  (doi:10.1007/978-3-642-29011-4_41, iacr:2011/501) -- the gadget "G-trapdoor."

## Relevance to this program
POST-QUANTUM construction, ADJACENT to the ECDLP mission. Recorded as context: GPV
hash-and-sign is one of the two dominant lattice signature paradigms (the other is
Fiat-Shamir-with-aborts, KN-LIT-059) and underlies Falcon (KN-LIT-057). Unrelated
to discrete-log hardness; recorded to map the lattice-signature design space that
succeeds ECDSA.

## Not verified here
Full paper not read; the GPV framework relayed from the abstract (hence
confidence: reported). Fields (incl. Micciancio-Peikert) confirmed against ACM DL /
Springer / IACR records via search, not by fetching the primary pages.
