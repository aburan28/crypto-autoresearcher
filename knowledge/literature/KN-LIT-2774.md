---
id: KN-LIT-2774
type: literature
title: "Bootstrapping the Blockchain, with Applications"
authors:
  - "Juan A. Garay"
  - "Aggelos Kiayias"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Bitcoin backbone protocol [Eurocrypt 2015] extracts ba- sic properties of Bitcoin's underlying blockchain data structure, such as common pre x and chain quality, and shows how fundamental applications including consensus and a robust public transaction ledger can be built on top of them. The underlying assumptions are proofs of work (POWs), adversarial hashing power strictly less than 1/2 and no adversarial pre-computationor, alternatively, the existence of an unpredictable genesis block.

## Key claims (as reported)
- In this paper we rst show how to remove the latter assumption, presenting a bootstrapped Bitcoin-like blockchain protocol relying on POWs that builds genesis blocks from scratch in the presence of adversarial pre-computation.
- Importantly, the round complexity of the genesis block generation process is independent of the number of participants.
- Next, we consider applications of our construction, including a PKI generation protocol and a consensus protocol without trusted setup assuming an honest majority (in terms of computational power).
- Previous results in the same setting (unauthenticated parties, no trusted setup, POWs) required a round complexity linear in the number of participants.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770257 (1).pdf`
- `downloads/10770257 (2).pdf`
- `downloads/10770257 (3).pdf`
- `downloads/10770257 (4).pdf`
- `downloads/10770257.pdf`
