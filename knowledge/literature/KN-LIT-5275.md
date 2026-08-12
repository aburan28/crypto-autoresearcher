---
id: KN-LIT-5275
type: literature
title: "Oblivious Pseudorandom Functions from Isogenies"
authors:
  - "Dan Boneh"
  - "Dmitry Kogan"
  - "Katharine Woo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, hash, isogeny, lattice, mpc, pqc, protocol, provable-security, quantum, rsa, sidh-csidh, supersingular, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An oblivious PRF, or OPRF, is a protocol between a client and a server, where the server has a key k for a secure pseudorandom function F , and the client has an input x for the function. At the end of the protocol the client learns F (k, x), and nothing else, and the server learns nothing.

## Key claims (as reported)
- An OPRF is verifiable if the client is convinced that the server has evaluated the PRF correctly with respect to a prior commitment to k.
- OPRFs and verifiable OPRFs have numerous applications, such as privateset-intersection protocols, password-based key-exchange protocols, and defense against denial-of-service attacks.
- Existing OPRF constructions use RSA-, Diffie-Hellman-, and lattice-type assumptions.
- The first two are not post-quantum secure.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491375 (1).pdf`
- `downloads/12491375.pdf`
