---
id: KN-LIT-6135
type: literature
title: "Randomizable Proofs and Delegatable Anonymous Credentials Mira Belenkiy1 , Jan Camenisch2 , Melissa Chase3 , Markulf Kohlweiss4"
authors:
  - "Anna Lysyanskaya"
  - "Hovav Shacham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct an efficient delegatable anonymous credentials system. Users can anonymously and unlinkably obtain credentials from any authority, delegate their credentials to other users, and prove possession of a credential L levels away from a given authority.

## Key claims (as reported)
- The size of the proof (and time to compute it) is O(Lk), where k is the security parameter.
- The only other construction of delegatable anonymous credentials (Chase and Lysyanskaya, Crypto 2006) relies on general non-interactive proofs for NP-complete languages of size kΩ(2L ).
- We revise the entire approach to constructing anonymous credentials and identify randomizable zero-knowledge proof of knowledge systems as the key building block.
- We formally define the notion of randomizable non-interactive zero-knowledge proofs, and give the first instance of controlled rerandomization of non-interactive zero-knowledge proofs by a third-party.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770107 (1).pdf`
- `downloads/56770107 (2).pdf`
- `downloads/56770107 (3).pdf`
- `downloads/56770107.pdf`
