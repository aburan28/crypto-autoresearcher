---
id: KN-LIT-7194
type: literature
title: "Toward Practical Lattice-based Proof of Knowledge from Hint-MLWE Duhyeong Kim1[0000−0002−4766−3456] , Dongwon Lee2[0000−0002−2156−197X]"
authors:
  - "Jinyeong Seo"
  - "Yongsoo Song"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, provable-security, quantum, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the last decade, zero-knowledge proof of knowledge protocols have been extensively studied to achieve active security of various cryptographic protocols. However, the existing solutions simply seek zero-knowledge for both message and randomness, which is an overkill in many applications since protocols may remain secure even if some information about randomness is leaked to the adversary.

## Key claims (as reported)
- We develop this idea to improve the state-of-the-art proof of knowledge protocols for RLWE-based public-key encryption and BDLOP commitment schemes.
- In a nutshell, we present new proof of knowledge protocols without using noise flooding or rejection sampling which are provably secure under a computational hardness assumption, called Hint-MLWE.
- We also show an efficient reduction from Hint-MLWE to the standard MLWE assumption.
- Our approach enjoys the best of two worlds because it has no computational overhead from repetition (abort) and achieves a polynomial overhead between the honest and proven languages.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850481 (1).pdf`
- `downloads/140850481.pdf`
