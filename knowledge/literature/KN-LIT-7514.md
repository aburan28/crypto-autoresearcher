---
id: KN-LIT-7514
type: literature
title: "Who watches the watchmen? : Utilizing Performance Monitors for Compromising keys of RSA on Intel Platforms"
authors:
  - "Sarani Bhattacharya"
  - "Debdeep Mukhopadhyay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Asymmetric-key cryptographic algorithms when implemented on systems with branch predictors, are subjected to side-channel attacks exploiting the deterministic branch predictor behavior due to their keydependent input sequences. We show that branch predictors can also leak information through the hardware performance monitors which are accessible by an adversary at the user-privilege level.

## Key claims (as reported)
- This paper presents an iterative attack which target the key-bits of 1024 bit RSA, where in offline phase, the system’s underlying branch predictor is approximated by a theoretical predictor in literature.
- Subsimulations are performed to classify the message-space into distinct partitions based on the event branch misprediction and the target key bit value.
- In online phase, we ascertain the secret key bit using branch mispredictions obtained from the hardware performance monitors which reflect the behavior of the underlying predictor hardware.
- We theoretically prove that the probability of success is equivalent to the accurate modelling of the theoretical predictor to the underlying system predictor.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930241 (1).pdf`
- `downloads/92930241.pdf`
