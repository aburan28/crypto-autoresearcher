---
id: KN-LIT-5053
type: literature
title: "Mutual Information Analysis A Generic Side-Channel Distinguisher"
authors:
  - "Benedikt Gierlichs"
  - "Lejla Batina"
  - "Pim Tuyls"
  - "Bart Preneel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a generic information-theoretic distinguisher for differential side-channel analysis. Our model of side-channel leakage is a refinement of the one given by Standaert et al.

## Key claims (as reported)
- An embedded device containing a secret key is modeled as a black box with a leakage function whose output is captured by an adversary through the noisy measurement of a physical observable.
- Although quite general, the model and the distinguisher are practical and allow us to develop a new differential side-channel attack.
- More precisely, we build a distinguisher that uses the value of the Mutual Information between the observed measurements and a hypothetical leakage to rank key guesses.
- The attack is effective without any knowledge about the particular dependencies between measurements and leakage as well as between leakage and processed data, which makes it a universal tool.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540423 (1).pdf`
- `downloads/51540423 (2).pdf`
- `downloads/51540423 (3).pdf`
- `downloads/51540423.pdf`
