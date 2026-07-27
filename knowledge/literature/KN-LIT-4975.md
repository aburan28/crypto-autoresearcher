---
id: KN-LIT-4975
type: literature
title: "Multi-Client Functional Encryption for Linear Functions in the Standard Model from LWE"
authors:
  - "Benoît Libert"
  - "Radu Ţiţiu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-client functional encryption (MCFE) allows ` clients to encrypt ciphertexts (Ct,1 , Ct,2 , . . . , Ct,` ) under some label. Each client can encrypt his own data Xi for a label t using a private encryption key eki issued by a trusted authority in such a way that, as long as all Ct,i share the same label t, an evaluator endowed with a functional key dkf can evaluate f (X1 , X2 , . . . , X` ) without learning anything else on the underlying plaintexts Xi .

## Key claims (as reported)
- Functional decryption keys can be derived by the central authority using the master secret key.
- Under the Decision DiffieHellman assumption, Chotard et al.
- (Asiacrypt 2018) recently described an adaptively secure MCFE scheme for the evaluation of linear functions over the integers.
- They also gave a decentralized variant (DMCFE) of their scheme which does not rely on a centralized authority, but rather allows encryptors to issue functional secret keys in a distributed manner.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210228 (1).pdf`
- `downloads/119210228.pdf`
