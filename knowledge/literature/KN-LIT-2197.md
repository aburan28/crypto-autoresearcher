---
id: KN-LIT-2197
type: literature
title: "A preliminary version of this paper appears in Proceedings of the 13th Annual Conference on Computer and Communications Security, ACM, 2006. This is the full version"
authors:
  - "Mihir Bellare∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how to significantly speed-up the encryption portion of some public-key cryptosystems by the simple expedient of allowing a sender to maintain state that is re-used across different encryptions. In particular we present stateful versions of the DHIES and Kurosawa-Desmedt schemes that each use only 1 exponentiation to encrypt, as opposed to 2 and 3 respectively in the original schemes, yielding the fastest discrete-log based public-key encryption schemes known in the random-oracle and standard models respectively.

## Key claims (as reported)
- The schemes are proven to meet an appropriate extension of the standard definition of IND-CCA security that takes into account novel types of attacks possible in the stateful setting. ∗ Dept. of Computer Science & Engineering, University of California at San Diego, 9500 Gilman Drive, La Jolla, California 92093, USA.
- E-Mail: mihir@cs.ucsd.edu.
- URL: http://www-cse.ucsd.edu/users/mihir.
- Supported in part by NSF grant CNS-0524765 and a gift from Intel Corporation. † Dept. of Computer Science & Engineering, University of Washington, AC101 Paul G.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/bks.pdf`
