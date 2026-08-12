---
id: KN-LIT-5775
type: literature
title: "Plaintext-Dependent Decryption: A Formal Security Treatment of SSH-CTR"
authors:
  - "Kenneth G. Paterson⋆⋆"
  - "Gaven J. Watson⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a formal security analysis of SSH in counter mode in a security model that accurately captures the capabilities of real-world attackers, as well as security-relevant features of the SSH specifications and the OpenSSH implementation of SSH. Under reasonable assumptions on the block cipher and MAC algorithms used to construct the SSH Binary Packet Protocol (BPP), we are able to show that the SSH BPP meets a strong and appropriate notion of security: indistinguishability under buffered, stateful chosen-ciphertext attacks.

## Key claims (as reported)
- This result helps to bridge the gap between the existing security analysis of the SSH BPP by Bellare et al. and the recently discovered attacks against the SSH BPP by Albrecht et al. which partially invalidate that analysis.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320184 (1).pdf`
- `downloads/66320184 (2).pdf`
- `downloads/66320184 (3).pdf`
- `downloads/66320184.pdf`
