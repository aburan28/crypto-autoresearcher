# Supplied-paper triage — TASK-20260723-215

Cutoff and access date: **2026-07-23**. Inference:
`research-sol-max` requested; `gpt-5.6-sol-xhigh` resolved at `xhigh`;
fallback used; adapter `cursor-subagent-2026-07`. This is literature triage
only and changes no official state.

## Result

All 69 supplied identifiers were resolved against their primary IACR ePrint
records. Bare identifiers were interpreted as 2026 entries; explicitly supplied
2023, 2024, and 2025 years were preserved. The screen found:

- **2 direct, potentially claim-changing papers:** 2026/1022 on convolutional
  correlation and DFR/failure attacks, and 2026/1465 on lattice-sieve reduction
  probabilities. Their bounded theorem/cost reviews are already assigned to
  sibling tasks `TASK-20260723-213` and `TASK-20260723-214`.
- **6 adjacent-methodology papers:** 2026/026, 2026/1462, 2026/1467,
  2026/1468, 2026/1448, and 2026/155. None by itself changes an ML-KEM claim.
- **1 pedagogical paper:** 2026/1098. Its stated purpose is an accessible
  introduction; no new security analysis was identified.
- **60 irrelevant papers:** unrelated primitives or constructions that merely
  use terms such as lattice, LWE, noise, post-quantum, or polynomial without
  supplying an ML-KEM attack or deployment result.

The classification `direct` means “directly targets a current ML-KEM claim and
needs a discriminating follow-up,” not “the claim has already survived review.”
Query counts, traces, local sieve probabilities, DFRs, and security-bit
estimates remain non-interchangeable.

## Claim-changing gates already in flight

### 2026/1022 — Thorns in Polynomial Convolution

The primary record was revised on 2026-07-19. The abstract directly challenges
coefficient-independence assumptions in structured-lattice DFR analysis and
connects large-deviation “thorns” to failure attacks. The decisive issue is not
whether convolution creates correlation—it does—but whether the paper's
Gaussian model and norm analysis map to FIPS 203's exact centered-binomial
inputs, compression, coefficient threshold, and implicit-rejection interface.

`TASK-20260723-213` is bounded to 2,400 seconds, 4 GiB, and one run. A positive
outcome requires an exact-distribution bridge that changes a named honest-DFR
or fully charged conditional-oracle metric. A Gaussian-only or assumed-oracle
result leaves passive MLWE and the ideal FIPS interface unchanged.

### 2026/1465 — On Reduction Probability Models in Lattice Sieving

The primary record was approved on 2026-07-21. Its reported 1.5x–8x
pair-reduction probability advantages are directly relevant to the sieve
subroutine, but a local constant is not automatically a security-bit reduction.

`TASK-20260723-214` is bounded to 2,400 seconds, 4 GiB, and one run. It must
separate a constant from an exponent and bridge any effect through list size,
iterations, memory/routing, BKZ, final search, and global reoptimization under
one named cost model. Without that bridge, the BATCH-002 ML-KEM cost rows do not
change.

## Required special cases

- **2026/155** was already reviewed in BATCH-002, including independent review
  and red-team challenge. It gives MLWE/IP-M-EDCP reductions and equivalences
  but no efficient structured-EDCP solver, standardized solve, or improved
  ML-KEM attack cost.
- **2026/1098** is pedagogical unless it contains new analysis. Its abstract
  explicitly presents an undergraduate/early-graduate introduction to
  ML-KEM, ML-DSA, FN-DSA, lattices, LWE, and LLL; no original attack, estimator,
  DFR, or implementation claim was identified.
- **2026/1022 and 2026/1465** are not re-adjudicated here; their full-text
  implications are owned by the two sibling tasks above.

## Adjacent-methodology screen

- **2026/026:** the URG randomness-dependency framework could be adapted to
  masked ML-KEM or Keccak hardware, but its proof and FPGA validation are
  AES-only.
- **2026/1462:** demonstrates that an HQC timing fix can leave power leakage and
  that masking may need hiding. ML-KEM has no HQC fixed-weight support sampler,
  so the reported calls/traces do not transfer.
- **2026/1467:** presents a migration-readiness score and reports
  ML-KEM-768/X25519MLKEM768 timings. These are deployment measurements, not
  cryptanalytic evidence, and the paper says external predictive validation is
  future work. The stated replication-package URL returned HTTP 404 when
  checked; that is a reproducibility/infrastructure observation, not evidence
  against the measurements.
- **2026/1468:** FEbA's treatment of dependent asymmetric XOR leakage could
  matter for ML-KEM masking operations, but no ML-KEM target or recovery is
  reported.
- **2026/1448:** MILP recovery from bounded-secret fault equations is a
  potentially reusable backend, but the equations and fault reductions are
  specific to randomized ML-DSA signing.
- **2026/155:** mathematically adjacent as above, but already covered and
  missing a solver.

## Exhaustive item log

The revision column reproduces the current primary-record history label at the
cutoff.

| # | ePrint | Current title | Revision | Class | Reason |
|---:|---|---|---|---|---|
| 1 | 2026/1443 | SENTRA:Privacy-Preserving Training in Outsourced Cloud Environments | 2026-07-23 revised | irrelevant | TEE/MPC machine-learning training, not ML-KEM. |
| 2 | 2026/1244 | Resource Estimation of the Distributed Quantum Algorithm for the Elliptic Curve Logarithm Problem | 2026-07-22, last of 6 | irrelevant | Distributed Shor resources for ECDLP, not MLWE. |
| 3 | 2026/1340 | Generalized Batched Decomposition Key-Switching for CKKS | 2026-07-22 revised | irrelevant | CKKS functional noise and key switching do not transfer to ML-KEM DFR. |
| 4 | 2025/2338 | OHMG: One hot modular garbling | 2026-07-22, last of 2 | irrelevant | Garbling with elliptic-curve arithmetic. |
| 5 | 2025/1824 | Coppercloud: Blind Server-Supported RSA Signatures | 2026-07-22, last of 6 | irrelevant | RSA blind signatures. |
| 6 | 2025/1907 | Introducing GRAFHEN: GRoup-bAsed Fully Homomorphic Encryption without Noise | 2026-07-22, last of 4 | irrelevant | Group-rewriting FHE, not a lattice KEM. |
| 7 | 2026/089 | The Billion Dollar Merkle Tree | 2026-07-22 revised | irrelevant | Merkle-tree binding and extractability. |
| 8 | 2026/829 | Beyond Binary: crosscorrelation of Cubic, Quartic and Quintic Character Sequences | 2026-07-22, last of 3 | irrelevant | Character-sequence correlation, not MLWE noise. |
| 9 | 2026/760 | A Simple Batched Threshold Encryption Scheme | 2026-07-22, last of 2 | irrelevant | Pairing-based threshold encryption. |
| 10 | 2026/090 | On the Impossibility of Round-Optimal Pairing-Free Blind Signatures in the ROM | 2026-07-21, last of 2 | irrelevant | Generic-group blind-signature lower bound. |
| 11 | 2025/1871 | A Unified Approach to Quantum Key Leasing with a Classical Lessor | 2026-07-21, last of 2 | irrelevant | Uses LWE as an assumption but gives no attack. |
| 12 | 2026/1453 | Celer: A Lookup Argument for Large-Scale Queries | 2026-07-21, last of 2 | irrelevant | Proof-system lookup argument. |
| 13 | 2026/026 | A General Randomness Recycling Framework for First-Order Masking with Application to AES | 2026-07-21 revised | adjacent methodology | Generic masking method; proved/measured only for AES. |
| 14 | 2026/1459 | Hybrid hash function based on the DLP and SIS problems | 2026-07-21 revised | irrelevant | SIS hash parameters do not attack MLWE. |
| 15 | 2024/1008 | Multi-round Dependency Identification: Theoretical Construction and Automatic Search of Impossible Boomerang Distinguishers | 2026-07-21, last of 8 | irrelevant | Symmetric-cipher boomerang analysis. |
| 16 | 2023/1258 | Flexway O-Sort: Enclave-Friendly and Optimal Oblivious Sorting | 2026-07-20, last of 3 | irrelevant | Oblivious sorting. |
| 17 | 2026/1402 | On Extending Integral Distinguishers | 2026-07-20, last of 2 | irrelevant | Symmetric-cipher integral cryptanalysis. |
| 18 | 2024/2086 | How To Think About End-To-End Encryption and AI: Training, Processing, Disclosure, and Consent | 2026-07-20, last of 5 | irrelevant | General E2EE/AI analysis, not ML-KEM integration. |
| 19 | 2026/1074 | Cryptocurrency-Backed Trustless Anonymous Tokens and Their Applications | 2026-07-20 revised | irrelevant | Blockchain anonymous tokens. |
| 20 | 2026/355 | Forget-IT: Optimal Good-Case Latency For Information-Theoretic BFT | 2026-07-20 revised | irrelevant | Byzantine consensus. |
| 21 | 2026/872 | Privacy Coins Under Viewing Key Compromise | 2026-07-20, last of 8 | irrelevant | Privacy-coin viewing keys. |
| 22 | 2025/2085 | Strong Pseudorandom Functions in AC^0[2] in the Bounded-Query Setting | 2026-07-20, last of 2 | irrelevant | Circuit-complexity PRFs. |
| 23 | 2026/491 | SoK: Private Transformer-Based Model Inference | 2026-07-20, last of 4 | irrelevant | PPML systems survey. |
| 24 | 2026/1389 | SC-DT: Scalable Constant Round Secure Comparison and its Application to Privacy Decision Tree Evaluation | 2026-07-20 revised | irrelevant | MPC comparison and PDTE. |
| 25 | 2026/1475 | Partial Derandomization for Leakage-Resilient Shamir's Secret Sharing over Composite Order Fields | 2026-07-22 approved | irrelevant | Shamir evaluation-place theorem, no ML-KEM implementation. |
| 26 | 2026/1474 | Mu-qt-PEGASIS: Interactive Aggregate Signatures from Effective Isogenies in the Programmable Random-Oracle Model | 2026-07-22 approved | irrelevant | Isogeny aggregate signatures. |
| 27 | 2025/1528 | Trustless Delegation of Vector Commitment Construction in Resource-Constrained Settings | 2026-07-19 revised | irrelevant | Delegated vector commitments and folding SNARKs. |
| 28 | 2026/1098 | A gentle introduction to lattice-based cryptography | 2026-07-19, last of 3 | background/pedagogy | Directly discusses ML-KEM but is explicitly expository; no new analysis found. |
| 29 | 2026/1022 | Thorns in Polynomial Convolution: Correlation, Large Deviations, and Applications | 2026-07-19 revised | direct claim-changing candidate | Could alter DFR/oracle analysis; exact FIPS bridge is delegated. |
| 30 | 2026/1473 | An Exact Four-Wise Framework for Boomerang Cryptanalysis | 2026-07-22 approved | irrelevant | Symmetric-cipher boomerang framework. |
| 31 | 2026/1472 | Vordr: Verifiable, Scalable and Anonymous Remote Attestation for Confidential Virtual Machines | 2026-07-22 approved | irrelevant | CVM attestation, not ML-KEM leakage. |
| 32 | 2026/1471 | Efficient Single-Round Obfuscation of Search and Result Patterns in Searchable Encryption | 2026-07-22 approved | irrelevant | Searchable encryption and DP/PIR. |
| 33 | 2026/488 | SoK: Offline Finding Protocols for Lightweight Location Tracking | 2026-07-18 revised | irrelevant | Bluetooth tracking protocols. |
| 34 | 2026/1470 | A Complexity-Theoretic Approach to Proofs of Space | 2026-07-22 approved | irrelevant | Proofs of space. |
| 35 | 2026/1469 | MULTILINEAR POLYNOMIALS VIA TREE-BASED CIRCUIT AND THE SUMCHECK PROTOCOL | 2026-07-23, last of 3 | irrelevant | Sumcheck optimization, not lattice reduction. |
| 36 | 2026/1468 | Side-Channel Attacks Revisited - an Optimization Problem Perspective: Bootstrapping and Space Reduction | 2026-07-22 approved | adjacent methodology | Generic XOR leakage method; no ML-KEM target. |
| 37 | 2026/1467 | Quantum-Safe Cryptography: A Migration Framework for Legacy Systems Toward NIST PQC Standards with the Crypto-Agility Readiness Score | 2026-07-21 approved | adjacent methodology | ML-KEM migration metrics and timings, not security evidence. |
| 38 | 2025/1665 | Threshold Public-Key Encryption: Definitions, Relations, and CPA-to-CCA Transforms | 2026-07-17, last of 3 | irrelevant | Threshold-PKE notions, not ML-KEM's transform. |
| 39 | 2026/1466 | Scalable High-Throughput FPGA Architecture for SMAC Message Authentication Code | 2026-07-21 approved | irrelevant | AES-round MAC hardware. |
| 40 | 2026/1465 | On Reduction Probability Models in Lattice Sieving | 2026-07-21 approved | direct claim-changing candidate | Could alter sieve constants/costs; full bridge is delegated. |
| 41 | 2026/1464 | Optimal Distributed Monotone-Policy Encryption for DNFs and More from Lattices | 2026-07-21 approved | irrelevant | Uses decomposed LWE for a construction; no attack. |
| 42 | 2026/1463 | Shortening Bounds for Reed-Solomon MCA | 2026-07-21 approved | irrelevant | Reed-Solomon code bounds. |
| 43 | 2026/1148 | Pushing the boundaries of group-based aggregation with zero-evading generators of low additive complexity | 2026-07-17, last of 11 | irrelevant | Group-commitment aggregation. |
| 44 | 2026/1462 | Power Reveals Timing Conceals - Side-Channel Attacks and Hiding Countermeasures for HQC's Fixed-Weight Vector Sampling | 2026-07-21 approved | adjacent methodology | Implementation lesson is adjacent; HQC sampler and metrics do not transfer. |
| 45 | 2026/1461 | The m=n+1 Boundary of EME: A Splicing Distinguisher for the Unrefreshed EME-Core Extension and Its Linear-Map Generalization | 2026-07-21 approved | irrelevant | Wide-block-cipher distinguisher. |
| 46 | 2026/1460 | A Practical Key-Recovery Attack on GRAFHEN | 2026-07-21 approved | irrelevant | Group-rewriting FHE attack. |
| 47 | 2026/1458 | A High-Speed Hardware Accelerator for QR-UOV Signature Scheme | 2026-07-21 approved | irrelevant | Multivariate-signature hardware. |
| 48 | 2026/369 | Constant-Size Issuer Hiding for BBS Credentials via Randomizable Keys | 2026-07-17, last of 4 | irrelevant | Pairing-based credentials. |
| 49 | 2026/1457 | Identity-Based Encryption from Isogenies | 2026-07-21 approved | irrelevant | Isogeny IBE. |
| 50 | 2024/1893 | Bitsliced Jasmin Implementation of the Mayo Signature Scheme | 2026-07-17, last of 2 | irrelevant | Multivariate-signature implementation. |
| 51 | 2026/1456 | QuantumScouter: Reinforcement Learning-Based Optimization of Variational Quantum Circuits for Differential Cryptanalysis | 2026-07-20 approved | irrelevant | Quantum distinguishers for SPECK/SIMON. |
| 52 | 2026/1438 | Vela and Carina: Fast Pairing-Based Multilinear Polynomial Commitments from Reciprocal Polynomials | 2026-07-16 revised | irrelevant | Pairing-based commitments. |
| 53 | 2026/1455 | Trout++: Robust Asynchronous Two-Round ECDSA for Arbitrary Thresholds | 2026-07-20 approved | irrelevant | Threshold ECDSA. |
| 54 | 2026/1454 | Batched Attribute-Based Encryption from Bilinear Pairings | 2026-07-20 approved | irrelevant | Pairing-based ABE. |
| 55 | 2026/451 | Oblivious Single Access Machines are Concretely Efficient | 2026-07-16, last of 3 | irrelevant | ORAM/OSAM systems work. |
| 56 | 2026/811 | Low-Depth Bootstrapping for Matrix-Native FHE | 2026-07-16 revised | irrelevant | FHE bootstrapping, not ML-KEM DFR. |
| 57 | 2026/068 | Practical Amortized Bootstrapping for NTRU-Based FHE | 2026-07-16, last of 2 | irrelevant | NTRU-FHE performance; no new MLWE attack. |
| 58 | 2025/2253 | Efficient Privacy-Preserving Blueprints for Threshold Comparison | 2026-07-16 revised | irrelevant | Cryptocurrency escrow proofs. |
| 59 | 2026/1452 | Labeled Multi-Key Batched IBE | 2026-07-20 approved | irrelevant | Batched IBE. |
| 60 | 2026/1451 | Lightweight Hardware Accelerator for the UOV Signature Scheme with Oil Space Blinding | 2026-07-20 approved | irrelevant | UOV hardware and blinding. |
| 61 | 2026/617 | Scaling of Memory and Bandwidth Requirements of Post-Quantum Signatures with Message Size | 2026-07-16 revised | irrelevant | PQ-signature/X.509 migration, not KEM integration. |
| 62 | 2026/155 | Module Learning With Errors and Structured Extrapolated Dihedral Cosets | 2026-07-16, last of 2 | adjacent methodology | Already reviewed; equivalence only, no solver. |
| 63 | 2026/1450 | Optimizing Polynomial Multiplication and Fixed-Weight Sampling for HQC on ARM Cortex-M4 | 2026-07-20 approved | irrelevant | HQC-specific arithmetic and sampler. |
| 64 | 2025/628 | Improving the Masked Division for the FALCON Signature | 2026-07-16, last of 2 | irrelevant | Falcon-specific masked division. |
| 65 | 2026/835 | Fault Injection Attacks Against zkSTARKs | 2026-07-16 revised | irrelevant | Faults against proof-system provers. |
| 66 | 2026/1449 | ANSA-IBKEM: Practical Quantum-Safe Identity-Based Key Encapsulation via Annular NTRU Trapdoors and Standardized PQC Arithmetic Reuse | 2026-07-20 approved | irrelevant | Different NTRU/BCH KEM; its DFR cannot transfer to FIPS 203. |
| 67 | 2026/1448 | Improving Skipping Fault Correction Attacks on Randomized Dilithium via MILP | 2026-07-20 approved | adjacent methodology | Potentially reusable MILP backend, but ML-DSA-specific fault equations. |
| 68 | 2026/1447 | Faster NTRU-based Bootstrapping with Extended and Sorting-based Techniques | 2026-07-20 approved | irrelevant | NTRU-FHE performance optimization. |
| 69 | 2026/1446 | Quantum Circuit Optimization with LLMs under a Structured Guideline | 2026-07-20 approved | irrelevant | Symmetric-cipher circuit generation, not a lattice attack circuit. |

## Priority rationale

The only high-information items are already isolated into the cheapest valid
discriminators. Test 2026/1022 first because an exact-distribution check can
quickly separate an honest-FIPS DFR correction from a Gaussian or
conditional-oracle result without implementing an attack. Review 2026/1465
next because converting a local reduction probability into an end-to-end
security estimate requires a wider and more expensive sieve-cost bridge.
No additional follow-up is warranted from this supplied set unless a concrete
ML-KEM backend is shown to instantiate the exact XOR, randomness-reuse, HQC
sampling, or ML-DSA fault equations in the adjacent papers.
