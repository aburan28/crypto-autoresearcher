---
id: KN-LIT-1222
type: literature
title: "ECPM Cryptanalysis Resource Estimation Dedy Septono Catur Putranto1,2[0000−0002−1246−7877] , Rini Wisnu Wardhani3[0000−0003−0565−6458]"
authors:
  - "Jaehan Cho"
  - "Howon Kim"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1767"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1767"
tags: [cryptanalysis, curve-arithmetic, dlp, ecdlp, elliptic-curve, finite-field, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Elliptic Curve Point Multiplication (ECPM) is a key component of the Elliptic Curve Cryptography (ECC) hierarchy protocol. However, the specific estimation of resources required for this process remains underexplored despite its significance in the cryptanalysis of ECC algorithms, particularly binary ECC in GF (2m ).

## Key claims (as reported)
- Given the extensive use of ECC algorithms in various security protocols and devices, it is essential to conduct this examination to gain valuable insights into its cryptanalysis, specifically in terms of providing precise resource estimations, which serve as a solid basis for further investigation in solving the Elliptic Curve Discrete Logarithm Problem.
- Expanding on several significant prior research, in this work, we refer to as ECPM cryptanalysis, we estimate quantum resources, including qubits, gates, and circuit depth, by integrating point addition (PA) and point-doubling (PD) into the ECPM scheme, culminating in a Shor’s algorithm-based binary ECC cryptanalysis circuit.
- Focusing on optimizing depth, we elaborate on and implement the most efficient PD circuit and incorporate optimized Karatsuba multiplication and FLT-based inversion algorithms for PA and PD operations.
- Compared to the latest PA-only circuits, our preliminary results showcase significant resource optimization for various ECPM implementations, including single-step ECPM, ECPM with combined or selective PA/PD utilization, and total−step ECPM (2n PD +2 PA).

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1767.pdf`
