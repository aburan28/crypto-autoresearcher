---
id: KN-LIT-4520
type: literature
title: "Instantiability of RSA-OAEP under Chosen-Plaintext Attack"
authors:
  - "Eike Kiltz"
  - "Adam O’Neill"
  - "Adam Smith"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the widely deployed RSA-OAEP encryption scheme of Bellare and Rogaway (Eurocrypt 1994), which combines RSA with two rounds of an underlying Feistel network whose hash (i.e., round) functions are modeled as random oracles, meets indistinguishability under chosen-plaintext attack (IND-CPA) in the standard model based on simple, non-interactive, and noninterdependent assumptions on RSA and the hash functions. To prove this, we first give a result on a more general notion called “padding-based” encryption, saying that such a scheme is IND-CPA if (1) its underlying padding transform satisfies a “fooling” condition against small-range distinguishers on a class of high-entropy input distributions, and (2) its trapdoor permutation is sufficiently lossy as defined by Peikert and Waters (STOC 2008).

## Key claims (as reported)
- We then show that the first round of OAEP satifies condition (1) if its hash function is t-wise independent for appopriate t and that RSA satisfies condition (2) under the Φ-Hiding Assumption of Cachin et al.
- This appears to be the first non-trivial positive result about the instantiability of RSA-OAEP.
- In particular, it increases our confidence that chosenplaintext attacks are unlikely to be found against the scheme.
- In contrast, RSA-OAEP’s predecessor in PKCS #1 v1.5 was shown to be vulnerable to such attacks by Coron et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230294 (1).pdf`
- `downloads/62230294 (2).pdf`
- `downloads/62230294 (3).pdf`
- `downloads/62230294.pdf`
