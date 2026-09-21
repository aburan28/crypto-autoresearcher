---
id: KN-LIT-651
type: literature
title: "Two-Message Statistically Sender-Private OT from LWE ?"
authors:
  - "Zvika Brakerski"
  - "Nico Döttling"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/530"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/530"
tags: [fhe, lattice, mpc, pqc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a two-message oblivious transfer (OT) protocol without setup that guarantees statistical privacy for the sender even against malicious receivers. Receiver privacy is game based and relies on the hardness of learning with errors (LWE).

## Key claims (as reported)
- This flavor of OT has been a central building block for minimizing the round complexity of witness indistinguishable and zero knowledge proof systems, non-malleable commitment schemes and multi-party computation protocols, as well as for achieving circuit privacy for homomorphic encryption in the malicious setting.
- Prior to this work, all candidates in the literature from standard assumptions relied on number theoretic assumptions and were thus insecure in the post-quantum setting.
- This work provides the first (presumed) post-quantum secure candidate and thus allows to instantiate the aforementioned applications in a post-quantum secure manner.
- Technically, we rely on the transference principle: Either a lattice or its dual must have short vectors.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239245 (1).pdf`
- `downloads/11239245.pdf`
