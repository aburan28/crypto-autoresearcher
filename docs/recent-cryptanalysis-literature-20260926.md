# Recent ECC and post-quantum cryptanalysis: June–September 2026

Snapshot: 2026-09-26 (America/Los_Angeles). Source-date window: approximately
2026-06-26 through 2026-09-26. This is a targeted, deduplicated selection of
20 primary-source papers with relevance to the program's ECC and PQC lanes,
not a claim to enumerate every new cryptography preprint. The ePrint landing
pages (or arXiv abstracts for the two arXiv-only entries) and dates were read;
full papers, code and measurements were not checked during this pass. Claims in
KN-LIT entries remain *reported*, even when the paper says it verified them.

The corpus already covers major work from this interval: the HAWK dimension
reduction and practical toy key recovery (KN-LIT-7592 and KN-LIT-970963),
supersingular isogeny p^(1/3+o(1)) results (KN-LIT-7563 and
KN-LIT-6fb205), and the initial McEliece distinguisher
(KN-LIT-7baf07). These were not duplicated. The later ePrint 2026/1630
revision adds a heuristic equivalent-key recovery claim and is recorded as a
superseding entry (KN-LIT-b97b9f).

| ePrint received / arXiv submitted, or revision | Area | Result type | Corpus record | Primary source |
|---|---|---|---|---|
| 2026-09-22 | isogeny | implementation speedup | [KN-LIT-cc9e69](../knowledge/literature/KN-LIT-cc9e69.md) | [2026/2153](https://eprint.iacr.org/2026/2153) |
| 2026-09-22 | multivariate | implementation attack | [KN-LIT-81c4b3](../knowledge/literature/KN-LIT-81c4b3.md) | [2026/2154](https://eprint.iacr.org/2026/2154) |
| 2026-09-21 | lattice | side-channel attack | [KN-LIT-5228f3](../knowledge/literature/KN-LIT-5228f3.md) | [2026/2137](https://eprint.iacr.org/2026/2137) |
| 2026-09-20 | lattice | theoretical attack speedup | [KN-LIT-016039](../knowledge/literature/KN-LIT-016039.md) | [2026/2117](https://eprint.iacr.org/2026/2117) |
| 2026-09-20 | lattice | side-channel attack | [KN-LIT-7909ee](../knowledge/literature/KN-LIT-7909ee.md) | [2026/2124](https://eprint.iacr.org/2026/2124) |
| 2026-09-18 | lattice | asymptotic attack speedup | [KN-LIT-d5f69c](../knowledge/literature/KN-LIT-d5f69c.md) | [2026/2084](https://eprint.iacr.org/2026/2084) |
| 2026-09-18 | lattice | side-channel attack speedup | [KN-LIT-d053a1](../knowledge/literature/KN-LIT-d053a1.md) | [2026/2091](https://eprint.iacr.org/2026/2091) |
| 2026-09-15 | lattice | fault attack and implementation speedup | [KN-LIT-46aae8](../knowledge/literature/KN-LIT-46aae8.md) | [2026/2046](https://eprint.iacr.org/2026/2046) |
| 2026-09-08 | elliptic-curve | quantum resource estimate | [KN-LIT-766b4e](../knowledge/literature/KN-LIT-766b4e.md) | [2026/1916](https://eprint.iacr.org/2026/1916) |
| 2026-09-08 | multivariate | forgery attack | [KN-LIT-f0a590](../knowledge/literature/KN-LIT-f0a590.md) | [2026/1927](https://eprint.iacr.org/2026/1927) |
| 2026-09-07 | lattice | side-channel attack | [KN-LIT-c42d33](../knowledge/literature/KN-LIT-c42d33.md) | [2026/1904](https://eprint.iacr.org/2026/1904) |
| 2026-09-06 | elliptic-curve | arithmetic speedup | [KN-LIT-b901b9](../knowledge/literature/KN-LIT-b901b9.md) | [2026/1902](https://eprint.iacr.org/2026/1902) |
| 2026-08-27 | code | structural attack update | [KN-LIT-b97b9f](../knowledge/literature/KN-LIT-b97b9f.md) | [2026/1630](https://eprint.iacr.org/2026/1630) |
| 2026-08-17 | isogeny | implementation speedup | [KN-LIT-112bad](../knowledge/literature/KN-LIT-112bad.md) | [2026/1713](https://eprint.iacr.org/2026/1713) |
| 2026-08-17 | lattice | claim audit | [KN-LIT-a2a423](../knowledge/literature/KN-LIT-a2a423.md) | [2026/1714](https://eprint.iacr.org/2026/1714) |
| 2026-08-17 | isogeny | quantum attack resource estimate | [KN-LIT-a25516](../knowledge/literature/KN-LIT-a25516.md) | [2026/1707](https://eprint.iacr.org/2026/1707) |
| 2026-08-15 | lattice | refutation | [KN-LIT-3b271a](../knowledge/literature/KN-LIT-3b271a.md) | [2026/1693](https://eprint.iacr.org/2026/1693) |
| 2026-08-13 | lattice | implementation attack | [KN-LIT-3b006a](../knowledge/literature/KN-LIT-3b006a.md) | [2026/1682](https://eprint.iacr.org/2026/1682) |
| 2026-07-27 | code | structural attack | [KN-LIT-c5966a](../knowledge/literature/KN-LIT-c5966a.md) | [2607.25027](https://arxiv.org/abs/2607.25027) |
| 2026-07-15 | elliptic-curve | quantum circuit resource estimate | [KN-LIT-68585e](../knowledge/literature/KN-LIT-68585e.md) | [2607.13816](https://arxiv.org/abs/2607.13816) |

## What changes our research agenda

1. **Current-parameter implementation failures.** SNOVA's six affected
   odd-characteristic alternatives (KN-LIT-81c4b3), Falcon physical
   attacks (KN-LIT-7909ee, KN-LIT-46aae8), ML-DSA
   leakage (KN-LIT-c42d33, KN-LIT-d053a1), and ML-KEM
   implementation defects (KN-LIT-5228f3, KN-LIT-3b006a)
   offer concrete reproduction targets. Record exact build, key reuse, traces,
   signatures, queries, verified successes, preprocessing and full cost. None
   implies a mathematical break of ML-KEM/ML-DSA/FN-DSA generally.
2. **Structural attacks and estimates.** Frobenius-UOV (KN-LIT-f0a590)
   has a heuristic forgery estimate well below its stated security levels.
   The McEliece August revision separates proven distinguishing from heuristic
   key recovery. The GRS weight-two attack (KN-LIT-c5966a) is a
   *different code family* from Classic McEliece. The LWE projection result
   (KN-LIT-016039) improves a particular provable dual baseline;
   the exact polynomial-space SVP result (KN-LIT-d5f69c) uses a
   different cost model than standard ML-KEM core-SVP estimates.
3. **ECC and isogeny implementation comparisons.** The MSM result
   (KN-LIT-b901b9) is a batched arithmetic speedup, not a rho-step or
   asymptotic ECDLP improvement. SQIsign SIMD (KN-LIT-112bad) and
   bounded-integer quaternion arithmetic (KN-LIT-cc9e69) have
   different baselines and cost metrics. Measure them on matched parameters
   before combining speedup ratios.
4. **Quantum ECDLP resource accounting.** The 835-logical-qubit construction
   (KN-LIT-68585e) trades space for gate count. The 25.7-day,
   19,397-physical-qubit secp256k1 estimate (KN-LIT-766b4e)
   assumes a specific fault-tolerant trapped-ion architecture. These estimates
   are not observed 256-bit solves. Keep quantum attack costs separate from
   classical Pollard rho and index calculus, and compare logical circuits
   under the same hardware assumptions.
5. **Disputed quantum lattice claim.** Simon's DCP proposal is already
   KN-LIT-e204ab. Guo–Yang (KN-LIT-a2a423) expose a remaining partition
   condition and Gupte–Ragavan–Zhandry (KN-LIT-3b271a) prove a
   no-go for the proposed algorithm. Do not propagate the original
   polynomial-time claim into lattice security estimates.

For each candidate, first attempt an exact-parameter, same-game replication
and a cost receipt. A smaller-parameter demonstration, a projected gate
count, a hardware-specific fault, and a public-key-only cryptanalytic break
are distinct outcomes. All 20 entries record the boundary individually.
