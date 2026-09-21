---
id: KN-LIT-1133
type: literature
title: "New record in the number of qubits for a quantum implementation of AES"
authors:
  - "Zhenqiang Li"
  - "Fei Gao"
  - "Sujuan Qin"
  - "Qiaoyan Wen"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/018"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/018"
tags: [cryptanalysis, pairing, pqc, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Optimizing the quantum circuit for implementing Advanced Encryption Standard (AES) is crucial for estimating the necessary resources in attacking AES by Grover algorithm. Previous studies have reduced the number of qubits required for the quantum circuits of AES128/-192/-256 from 984/1112/1336 to 270/334/398, which is close to the optimal value of 256/320/384.

## Key claims (as reported)
- It becomes a challenging task to further optimize them.
- Aiming at this task, we find a method about how the quantum circuit of AES S-box can be designed with the help of automation tool LIGHTER-R.
- Particularly, the multiplicative inversion in F28 , which is the main part of S-box, is converted into the multiplicative inversion (and multiplication) in F24 , then the latter can be implemented by LIGHTER-R because its search space is small enough.
- By this method, we construct the quantum circuits of S-box for mapping |a⟩|0⟩ to |a⟩|S(a)⟩ and |a⟩|b⟩ to |a⟩|b ⊕ S(a)⟩ with 20 qubits instead of 22 in the previous studies.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-018.pdf`
