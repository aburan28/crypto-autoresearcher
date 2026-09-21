---
id: KN-LIT-5560
type: literature
title: "On The Round Complexity of Secure Quantum Computation"
authors:
  - "James Bartusek⋆"
  - "Andrea Coladangelo⋆⋆"
  - "Dakshita Khurana⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first constant-round protocols for secure quantum computation in the two-party (2PQC) and multi-party (MPQC) settings with security against malicious adversaries. Our protocols are in the common random string (CRS) model. – Assuming two-message oblivious transfer (OT), we obtain (i) threemessage 2PQC, and (ii) five-round MPQC with only three rounds of online (input-dependent) communication; such OT is known from quantum-hard Learning with Errors (QLWE). – Assuming sub-exponential hardness of QLWE, we obtain (i) threeround 2PQC with two online rounds and (ii) four-round MPQC with two online rounds. – When only one (out of two) parties receives output, we achieve minimal interaction (two messages) from two-message OT; classically, such protocols are known as non-interactive secure computation (NISC), and our result constitutes the first maliciously-secure quantum NISC.

## Key claims (as reported)
- Additionally assuming reusable malicious designated-verifier NIZK arguments for NP (MDV-NIZKs), we give the first MDV-NIZK for QMA that only requires one copy of the quantum witness.
- Finally, we perform a preliminary investigation into two-round secure quantum computation where each party must obtain output.
- On the negative side, we identify a broad class of simulation strategies that suffice for classical two-round secure computation that are unlikely to work in the quantum setting.
- Next, as a proof-of-concept, we show that tworound secure quantum computation exists with respect to a quantum oracle.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826122 (1).pdf`
- `downloads/12826122.pdf`
