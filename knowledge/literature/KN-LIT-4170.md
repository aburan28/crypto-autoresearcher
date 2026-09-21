---
id: KN-LIT-4170
type: literature
title: "Hash Proof Systems over Lattices Revisited"
authors:
  - "Fabrice Benhamouda"
  - "Olivier Blazy]"
  - "Léo Ducas["
  - "Willy Quach"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, pairing, protocol, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Hash Proof Systems or Smooth Projective Hash Functions (SPHFs) are a form of implicit arguments introduced by Cramer and Shoup at Eurocrypt’02. They have found many applications since then, in particular for authenticated key exchange or honest-verifier zero-knowledge proofs.

## Key claims (as reported)
- While they are relatively well understood in group settings, they seem painful to construct directly in the lattice setting.
- Only one construction of an SPHF over lattices has been proposed in the standard model, by Katz and Vaikuntanathan at Asiacrypt’09.
- But this construction has an important drawback: it only works for an adhoc language of ciphertexts.
- Concretely, the corresponding decryption procedure needs to be tweaked, now requiring q many trapdoor inversion attempts, where q is the modulus of the underlying Learning With Errors (LWE) problem.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770185 (1).pdf`
- `downloads/10770185 (2).pdf`
- `downloads/10770185 (3).pdf`
- `downloads/10770185 (4).pdf`
- `downloads/10770185.pdf`
