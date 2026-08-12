---
id: KN-LIT-5661
type: literature
title: "Optimal Security Proofs for PSS and other"
authors:
  - "Signature Schemes"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Probabilistic Signature Scheme (PSS) designed by Bellare and Rogaway is a signature scheme provably secure against chosen message attacks in the random oracle model, whose security can be tightly related to the security of RSA. We derive a new security proof for PSS in which a much shorter random salt is used to achieve the same security level, namely we show that log2 qsig bits suffice, where qsig is the number of signature queries made by the attacker.

## Key claims (as reported)
- When PSS is used with message recovery, a better bandwidth is obtained because longer messages can now be recovered.
- In this paper, we also introduce a new technique for proving that the security proof of a signature scheme is optimal.
- In particular, we show that the size of the random salt that we have obtained for PSS is optimal: if less than log 2 qsig bits are used, then PSS is still provably secure but it cannot have a tight security proof.
- Our technique applies to other signature schemes such as the Full Domain Hash scheme and Gennaro-Halevi-Rabin’s scheme, whose security proofs are shown to be optimal.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/coron (1).pdf`
- `downloads/coron (2).pdf`
- `downloads/coron.pdf`
