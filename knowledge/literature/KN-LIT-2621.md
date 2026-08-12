---
id: KN-LIT-2621
type: literature
title: "Attribute-Based Signatures for Circuits from Bilinear Map"
authors:
  - "Yusuke Sakai"
  - "Nuttapong Attrapadung"
  - "Goichiro Hanaoka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In attribute-based signatures, each signer receives a signing key from the authority, which is associated with the signer’s attribute, and using the signing key, the signer can issue a signature on any message under a predicate, if his attribute satisfies the predicate. One of the ultimate goals in this area is to support a wide class of predicates, such as the class of arbitrary circuits, with practical efficiency from a simple assumption, since these three aspects determine the usefulness of the scheme.

## Key claims (as reported)
- We present an attribute-based signature scheme which allows us to use an arbitrary circuit as the predicate with practical efficiency from the symmetric external Diffie-Hellman assumption.
- We achieve this by combining the efficiency of Groth-Sahai proofs, which allow us to prove algebraic equations efficiently, and the expressiveness of GrothOstrovsky-Sahai proofs, which allow us to prove any NP relation via circuit satisfiability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140208 (1).pdf`
- `downloads/96140208 (2).pdf`
- `downloads/96140208 (3).pdf`
- `downloads/96140208 (4).pdf`
- `downloads/96140208.pdf`
