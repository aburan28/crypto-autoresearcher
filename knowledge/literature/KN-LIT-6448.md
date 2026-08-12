---
id: KN-LIT-6448
type: literature
title: "Secure Multiparty Computation from Threshold Encryption based on Class Groups"
authors:
  - "Lennart Braun"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, factoring, fhe, lattice, mpc, number-theory, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first actively-secure threshold version of the cryptosystem based on class groups from the so-called CL framework (Castagnos and Laguillaumie, 2015). We show how to use our threshold scheme to achieve general universally composable (UC) secure multiparty computation (MPC) with only transparent set-up, i.e., with no secret trapdoors involved.

## Key claims (as reported)
- On the way to our goal, we design new zero-knowledge (ZK) protocols with constant communication complexity for proving multiplicative relations between encrypted values.
- This allows us to use the ZK proofs to achieve MPC with active security with only a constant factor overhead.
- Finally, we adapt our protocol for the so called “You-Only-Speak-Once” (YOSO) setting, which is a very promising recent approach for performing MPC over a blockchain.
- This is possible because our key generation protocol is simpler and requires significantly less interaction compared to previous approaches: in particular, our new key generation protocol allows the adversary to bias the public key, but we show that this has no impact on the security of the resulting cryptosystem.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850104 (1).pdf`
- `downloads/140850104.pdf`
