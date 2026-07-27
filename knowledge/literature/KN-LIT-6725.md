---
id: KN-LIT-6725
type: literature
title: "Snarky Signatures: Minimal Signatures of Knowledge from Simulation-Extractable SNARKs"
authors:
  - "Jens Groth"
  - "Mary Maller"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a pairing based simulation-extractable SNARK (SE-SNARK) that consists of only 3 group elements and has highly efficient verification. By formally linking SE-SNARKs to signatures of knowledge, we then obtain a succinct signature of knowledge consisting of only 3 group elements.

## Key claims (as reported)
- SE-SNARKs enable a prover to give a proof that they know a witness to an instance in a manner which is: (1) succinct - proofs are short and verifier computation is small; (2) zero-knowledge - proofs do not reveal the witness; (3) simulation-extractable - it is only possible to prove instances to which you know a witness, even when you have already seen a number of simulated proofs.
- We also prove that any pairing based signature of knowledge or SENIZK argument must have at least 3 group elements and 2 verification equations.
- Since our constructions match these lower bounds, we have the smallest size signature of knowledge and the smallest size SE-SNARK possible.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401344 (1).pdf`
- `downloads/10401344.pdf`
