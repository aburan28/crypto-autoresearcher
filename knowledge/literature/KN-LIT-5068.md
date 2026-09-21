---
id: KN-LIT-5068
type: literature
title: "NEON crypto"
authors:
  - "Daniel J. Bernstein"
  - "Peter Schwabe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, implementation, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NEON is a vector instruction set included in a large fraction of new ARM-based tablets and smartphones. This paper shows that NEON supports high-security cryptography at surprisingly high speeds; normally data arrives at lower speeds, giving the CPU time to handle tasks other than cryptography.

## Key claims (as reported)
- In particular, this paper explains how to use a single 800MHz Cortex A8 core to compute the existing NaCl suite of high-security cryptographic primitives at the following speeds: 5.60 cycles per byte (1.14 Gbps) to encrypt using a shared secret key, 2.30 cycles per byte (2.78 Gbps) to authenticate using a shared secret key, 527102 cycles (1517/second) to compute a shared secret key for a new public key, 650102 cycles (1230/second) to verify a signature, and 368212 cycles (2172/second) to sign a message.
- These speeds make no use of secret branches and no use of secret memory addresses.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/neoncrypto-20120320 (1).pdf`
- `downloads/neoncrypto-20120320.pdf`
