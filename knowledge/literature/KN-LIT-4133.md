---
id: KN-LIT-4133
type: literature
title: "Group Encryption"
authors:
  - "Aggelos Kiayias"
  - "Yiannis Tsiounis"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present group encryption, a new cryptographic primitive which is the encryption analogue of a group signature. It possesses similar verifiability, security and privacy properties, but whereas a group signature is useful whenever we need to conceal the source (signer) within a group of legitimate users, a group encryption is useful whenever we need to conceal a recipient (decryptor) within a group of legitimate receivers.

## Key claims (as reported)
- We introduce and model the new primitive and present sufficient as well as necessary conditions for its generic implementation.
- We then develop an efficient novel number theoretic construction for group encryption of discrete logarithms whose complexity is independent of the group size.
- As part of achieving this we construct a new public-key encryption for discrete logarithms that satisfies CCA2-key-privacy and CCA2-security in the standard model (this gives the first Pailler-based system with the above two properties proven in the standard model).
- Applications of group encryption include settings where a user wishes to hide her preferred trusted third party or even impose a hidden hierarchy of trusted parties while being required to assure well-formed ciphertexts, as well as oblivious storage settings where the set of retrievers need to be verifiable but the storage distribution should be oblivious to the server.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330179 (1).pdf`
- `downloads/48330179 (2).pdf`
- `downloads/48330179 (3).pdf`
- `downloads/48330179.pdf`
