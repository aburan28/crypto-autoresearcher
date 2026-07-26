---
id: KN-LIT-6209
type: literature
title: "Relations between Constrained and Bounded Chosen Ciphertext Security for Key Encapsulation Mechanisms"
authors:
  - "Takahiro Matsuda⋆"
  - "Goichiro Hanaoka"
  - "Kanta Matsuura"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In CRYPTO 2007, Hofheinz and Kiltz formalized a security notion for key encapsulation mechanisms (KEMs), called constrained chosen ciphertext (CCCA) security, which is strictly weaker than ordinary chosen ciphertext (CCA) security, and showed a new composition paradigm for CCA secure hybrid encryption. Thus, CCCA security of a KEM turned out to be quite useful.

## Key claims (as reported)
- However, since the notion is relatively new and its definition is slightly complicated, relations among CCCA security and other security notions have not been clarified well.
- In this paper, in order to better understand CCCA security and the construction of CCCA secure KEMs, we study relations between CCCA and bounded CCA security, where the latter notion considers security against adversaries that make a-priori bounded number of decapsulation queries, and is also strictly weaker than CCA security.
- Specifically, we show that in most cases there are separations between these notions, while there is some unexpected implication from (a slightly stronger version of) CCCA security to a weak form of 1-bounded CCA security.
- We also revisit the construction of a KEM from a hash proof system (HPS) with computational security properties, and show that the HPS-based KEM, which was previously shown CCCA secure, is actually 1-bounded CCA secure as well.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930576 (1).pdf`
- `downloads/72930576 (2).pdf`
- `downloads/72930576 (3).pdf`
- `downloads/72930576.pdf`
