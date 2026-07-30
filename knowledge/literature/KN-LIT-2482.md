---
id: KN-LIT-2482
type: literature
title: "An Efficient Strong Asymmetric PAKE Compiler Instantiable from Group Actions"
authors:
  - "Ian McQuoid"
  - "Jiayu Xu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, dlp, factoring, isogeny, pairing, pqc, protocol, provable-security, quantum, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Password-authenticated key exchange (PAKE) is a class of protocols enabling two parties to convert a shared (possibly low-entropy) password into a high-entropy joint session key. Strong asymmetric PAKE (saPAKE), an extension that models the client-server setting where servers may store a client’s password for repeated authentication, was the subject of standardization efforts by the IETF in 2019–20.

## Key claims (as reported)
- In this work, we present the most computationally efficient saPAKE protocol so far: a compiler from PAKE to saPAKE which costs only 2 messages and 7 group exponentiations in total (3 for client and 4 for server) when instantiated with suitable underlying PAKE protocols.
- In addition to being efficient, our saPAKE protocol is conceptually simple and achieves the strongest notion of universally composable (UC) security.
- In addition to classical assumptions and classical PAKE, we may instantiate our PAKE-to-saPAKE compiler with cryptographic group actions, such as the isogeny-based CSIDH, and post-quantum PAKE.
- This yields the first saPAKE protocol from post-quantum assumptions as all previous constructions rely on cryptographic assumptions weak to Shor’s algorithm.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438324 (1).pdf`
- `downloads/14438324.pdf`
