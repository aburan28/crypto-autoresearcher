---
id: KN-LIT-3739
type: literature
title: "Expressive Key-Policy Attribute-Based Encryption with Constant-Size Ciphertexts"
authors:
  - "Nuttapong Attrapadung"
  - "Benoı̂t Libert"
  - "Elie de Panafieu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Attribute-based encryption (ABE), as introduced by Sahai and Waters, allows for fine-grained access control on encrypted data. In its key-policy flavor, the primitive enables senders to encrypt messages under a set of attributes and private keys are associated with access structures that specify which ciphertexts the key holder will be allowed to decrypt.

## Key claims (as reported)
- In most ABE systems, the ciphertext size grows linearly with the number of ciphertext attributes and the only known exceptions only support restricted forms of threshold access policies.
- This paper proposes the first key-policy attribute-based encryption (KPABE) schemes allowing for non-monotonic access structures (i.e., that may contain negated attributes) and with constant ciphertext size.
- Towards achieving this goal, we first show that a certain class of identitybased broadcast encryption schemes generically yields monotonic KPABE systems in the selective set model.
- We then describe a new efficient identity-based revocation mechanism that, when combined with a particular instantiation of our general monotonic construction, gives rise to the first truly expressive KP-ABE realization with constant-size ciphertexts.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710093 (1).pdf`
- `downloads/65710093 (2).pdf`
- `downloads/65710093 (3).pdf`
- `downloads/65710093.pdf`
