# ML-KEM cryptanalysis baseline map

Task: `TASK-20260722-201`  
Research question: `RQ-MLKEM-001`  
Public-information cutoff and access date for every URL below: **2026-07-22**

## Scope and reading rules

This map covers the standardized ML-KEM parameter sets and public attack
literature available by the cutoff. “Kyber-512/768/1024” in attack papers is
mapped to ML-KEM-512/768/1024 only where the attacked MLWE parameters are the
same. Kyber and final ML-KEM are not byte-for-byte protocols; claims involving
the Fujisaki–Okamoto transform, rejection behavior, malformed ciphertexts, or
code paths must be rechecked against FIPS 203.

An estimated exponent is not an observed attack. Exponents from Core-SVP
(`C0`), classical-circuit (`CC`), classical-query/nearest-neighbor (`CN`),
quantum-query, RAM, and physical-resource models are not interchangeable.
Every comparison below therefore retains its source model and charges, at
minimum, sample acquisition, lattice reduction/sieving, guessing, FFT or
decoding, memory, success amplification, and candidate verification when the
source exposes them. No public work reviewed here reports a verified
cryptographic-scale key recovery for any standardized ML-KEM parameter set.

## Standardized target

FIPS 203 fixes \(R_q=\mathbb Z_q[X]/(X^{256}+1)\), \(q=3329\), and module rank
\(k\in\{2,3,4\}\). The public-key relation is Module-LWE; ciphertext
compression also creates Module-LWR-like information. The table is from FIPS
203 [S1].

| Set | NIST category | \(k\) | \(\eta_1\) | \(\eta_2\) | \((d_u,d_v)\) | honest decapsulation-failure rate |
|---|---:|---:|---:|---:|---:|---:|
| ML-KEM-512 | 1 | 2 | 3 | 2 | (10,4) | \(2^{-138.8}\) |
| ML-KEM-768 | 3 | 3 | 2 | 2 | (10,4) | \(2^{-164.8}\) |
| ML-KEM-1024 | 5 | 4 | 2 | 2 | (11,5) | \(2^{-174.8}\) |

The Kyber design document’s historical Core-SVP anchors were 112/102,
178/161, and 241/218 classical/quantum bits for 512/768/1024 [S2]. The
round-three document separately credited ciphertext rounding with raising the
512 classical anchor from 112 to 118 bits under an additional weak-LWR
interpretation. These are design-time indicators, not current full attack
costs and not NIST category thresholds. Later papers commonly compare detailed
nearest-neighbor estimates with category reference costs 143/207/272 bits;
that is another metric, not a contradiction.

## Core algorithmic cryptanalysis (no leakage or decryption oracle)

### 1. Primal/uSVP lattice attacks

**Mechanism.** Embed the MLWE equations, secret, and error into a \(q\)-ary
lattice, reduce with BKZ/progressive BKZ, and solve a unique-SVP or BDD
instance. The expensive terms are basis construction, BKZ tours, the SVP
oracle (enumeration or sieving), rerandomization/success amplification, memory,
and final secret verification. Generic methodology and the estimator lineage
are given by Albrecht–Player–Scott [S3]; G6K is an implementation baseline
[S4].

**Current status.**

* Strategy search and improved Pump-and-Jump simulation reduce Kyber estimates
  by 3.4–4.6 bits relative to the documentation, and by only 1.1–1.3 bits
  relative to the paper’s matched refined two-step estimator [S5]. This is a
  strategy/cost refinement, not a new asymptotic attack.
* A model that explicitly routes/sorts sieve memory estimates full primal
  costs of 158.7, 229.9, and 310.2 bits at sieve dimensions 375, 586, and 829
  for 512/768/1024 [S6]. The paper labels these extrapolations and assumes the
  rest of the attack is unchanged. The result illustrates that omitting memory
  can move estimates by 14.3/22.6/30.6 bits relative to its updated
  no-routing-cost model; it must not be mixed with `C0` or `CC`.
* No primal paper supplies a standardized-parameter solve. Simulator agreement
  or a lower optimized block size is evidence about an estimator, not key
  recovery.

**Baseline conclusion.** Primal remains a required matched control. Any
candidate must beat a current progressive-BKZ/two-step implementation and a
full cost model, not merely the old 112/178/241 Core-SVP anchors.

### 2. Dual, dual-sieve-FFT, and provable dual attacks

**Mechanism.** Find many short vectors in a dual \(q\)-ary lattice, evaluate a
non-uniformity score on the LWE target, and optionally enumerate secret
coordinates with an FFT. Costs include short-vector sampling, decoding or
modulus switching, the number of score trials, FFT tables, false-positive
filtering, memory, and verification.

**Credible line and cautions.**

* Guo–Johansson introduced the two-step/many-short-vector FFT line [S7].
  MATZOV added modulus switching and aggressive cost estimates [S8].
* Ducas–Pulles proved that the independent-score heuristic used in that line
  contradicts unconditional results or established heuristics in relevant
  regimes and experimentally overestimates success [S9]. Their 2026 journal
  version supplies more accurate correct/wrong score predictions, but does not
  turn every earlier parameter table into a validated attack.
* Carrier–Meyer-Hilfiger–Shen–Tillich replace the suspect modulus-switching
  step with generalized polar-code lossy source coding and experimentally
  validate the distortion component [S10]. In their matched nearest-neighbor
  model the classical costs are 139.5, 195.1, and 259.7 bits, respectively
  (3.5/11.9/12.3 below the 143/207/272 reference costs). These are estimates,
  with exponential lattice reduction and substantial memory, not executions.
* Li–Zheng combine modulus switching with lossy source coding [S11]. Their best
  total costs by model are approximately:

  | Set | `C0` | `CC` | `CN` |
  |---|---:|---:|---:|
  | 512 | 118.09 | 139.20 | 134.42 |
  | 768 | 172.36 | 194.02 | 189.36 |
  | 1024 | 238.12 | 259.40 | 253.68 |

  The gains over lossy-source-coding alone are modest in total cost, although
  FFT and decoding subcosts fall by 1–7 bits; short-vector sampling remains the
  bottleneck. Their `CC` model omits memory-access cost.
* Pouly–Shen give a simplified, non-asymptotic provable dual framework [S12].
  Qu–Xu add provable modulus switching and CRT reconstruction [S13]. LaMS
  replaces several CRT primes by one small prime and p-adic digit recovery,
  reducing its corrected CRT comparator by 22/31/41 bits for
  512/768/1024 [S14]. Those deltas are **not** reductions from the best
  Carrier/Ogilvie total cost and do not establish a new overall ML-KEM
  baseline.

**Baseline conclusion.** The matched classical dual baseline is the minimum
fully charged result among Carrier, Li–Zheng, and the structure-aware result
below, under the *same* cost model. Any use of MATZOV-style scores must pass the
Ducas–Pulles covariance/false-positive checks.

### 3. Hybrid guessing, decoding, and batch-CVP

**Mechanism.** Guess or enumerate a secret subvector, reduce the remaining
dimension, and solve many BDD/CVP instances with shared preprocessing.
Meet-in-the-middle saves time by using exponential memory; batch-CVP saves
preprocessing only if target generation and rerandomization are fully charged.

* Fast Slicer implements Randomized-Slicer batch-CVP and reports up to a
  five-fold speedup over primal on scaled LWE dimensions 160–210, including
  centered-binomial distributions [S15]. It does not beat the best full-scale
  ML-KEM estimate or solve a standardized instance.
* For ML-KEM’s non-sparse centered-binomial secrets, ordinary primal hybrid
  guessing is much less favorable than for sparse FHE secrets. A toy speedup
  cannot be extrapolated through the BKZ exponent without a calibrated scaling
  law.

**Baseline conclusion.** A valid hybrid comparison must use identical target
success probability, BKZ output quality, number of targets, rerandomizations,
memory, and verification. “One preprocessing for many targets” is not itself
an attack gain if target scores are highly correlated.

### 4. Module/ring-structure exploitation

**Established structure.** In \(X^{256}+1\), multiplication by monomials gives
negacyclic signed coefficient permutations. These coefficient isometries
preserve ML-KEM’s product centered-binomial secret/error distributions.

* Wang et al. rotate each short dual vector into \(n-1\) further vectors and
  heuristically use their near-orthogonality [S16]. Their example is
  NewHope512; it does not establish a material ML-KEM reduction.
* Ogilvie proves that coefficient-isometry-derived MLWE instances can share
  expensive hybrid preprocessing and uses rotations to improve the hit
  probability [S17]. Her structure-aware dual-hybrid estimates are:

  | Set | `C0` | `CC` | `CN` | reduction from her matched unstructured-LWE comparator |
  |---|---:|---:|---:|---:|
  | 512 | 118.8 | 137.1 | 132.2 | 3.0 / 2.4 / 2.3 bits |
  | 768 | 170.2 | 192.7 | 186.9 | 2.8 / 2.4 / 2.9 bits |
  | 1024 | 234.8 | 257.2 | 252.4 | 4.2 / 2.5 / 2.2 bits |

  The gain is concrete and exponential-time; it is not a polynomial break.
* Hou–Jiang independently apply ring rotations to hybrid decoding [S18]. Their
  major 4–13-bit effects concern sparse Ring-LWE/FHE. Their own corrected Kyber
  comparison reports only 0–0.8 bit, while Ogilvie’s later table reports the
  larger values above. This version/code sensitivity is a reproduction
  requirement, not evidence that the effects add.
* NoMod treats modular wraps as robust-regression outliers and amplifies
  reduced samples by negacyclic rotations [S19]. Its recovered instances use
  binary/sparse or reduced test settings, not all standard ML-KEM dimensions
  and centered-binomial distributions with a full attack cost. It is
  hypothesis-generating only.

**Deduplication consequence.** “Use rotations,” “reuse preprocessing over
isometries,” “save reduced vectors,” or “apply robust regression after
reduction” is prior art. A new candidate must identify a non-overlapping source
of information or a rigorously cheaper charged subroutine.

### 5. Combinatorial and algebraic attacks

**BKW/combinatorial.** BKW variants eliminate blocks by combining many LWE
samples. The standardized public key exposes a fixed, sample-limited MLWE
instance; ring rotations are correlated transforms, not fresh independent
samples. Under the reviewed parameterizations, BKW is not competitive with
primal/dual reduction [S3]. Secret enumeration already appears inside the
hybrid and dual baselines and must charge its time-memory tradeoff.

**Arora–Ge/Gröbner/resultants.**

* Steiner proves complexity bounds for Arora–Ge polynomial systems and
  analyzes Kyber-768; even optimistic estimates remain far above lattice
  attacks [S20].
* Wang et al. first reduce dimension with dual vectors, then build
  error-distribution-aware polynomials and solve by resultants [S21]. Their
  estimates are 724/967/1316 bits for 512/768/1024, improving the compared
  Gröbner estimates 1584/1588/2014 by 860/621/698 bits but remaining far above
  both NIST reference costs and lattice attacks. The small-scale checks
  validate parts of the probability model, not cryptographic-scale solving.

**Baseline conclusion.** Algebraic work has narrowed an academic gap but is
not a competitive attack baseline. A claim based only on a large improvement
over a thousand-bit Gröbner comparator is not a material ML-KEM improvement.

## Oracle-dependent algorithmic attacks

These attacks are cryptanalytic algorithms, but their oracle is not provided
by the ideal FIPS 203 interface. They are therefore outside passive core
MLWE hardness and must state how the oracle is instantiated.

* Natural honest failures occur with the FIPS 203 rates in the first table.
  Merely waiting for one costs about the reciprocal probability before any
  failure-boosting, key recovery, or verification work.
* Multitarget failure boosting gives theoretical failure-attack estimates for
  Kyber and explicitly discusses why real execution can remain impractical
  [S22]. It does not provide a standard decapsulation failure bit to a remote
  adversary.
* The 2026 adaptive-LDPC attack recovers ML-KEM-768 in 2,950 queries at a
  stipulated 95%-accurate decryption-failure oracle, 1.35 times its Shannon
  lower bound [S23]. That is a strong result **conditional on leakage**; it is
  not a core algorithmic break and cannot be compared in “bits” with a
  no-oracle lattice attack without charging oracle construction and traces.

## Implementation leakage (separate from core cryptanalysis)

* KyberSlash exploits secret-dependent division timing in affected
  implementations; demonstrated key recovery takes minutes to hours on the
  tested ARM platforms, and the vulnerable code was patched [S24].
* Power, electromagnetic, cache/microarchitectural, fault, masking, and
  plaintext/decryption-check leakage can instantiate hints or the oracle used
  by [S23]. These are implementation findings. They say neither that MLWE is
  easy nor that a constant-time, appropriately protected FIPS 203
  implementation exposes the same channel.
* Any proposal using exact coefficients, signs, Hamming weights, PC/DF bits, or
  decapsulation timing is a side-information attack and must charge trace
  collection, profiling, noise, adaptivity, chosen ciphertexts, device access,
  and countermeasure bypass.

## Classical/quantum boundary

* Classical estimates are dominated by exponential lattice reduction,
  short-vector sampling, score evaluation/decoding, and often exponential
  memory. The lowest exponent depends strongly on whether memory access is
  charged [S6].
* Quantum lattice sieving improves idealized asymptotic exponents; quantum
  hypercone LSF reports \(2^{0.2571d+o(d)}\) [S25]. This does not include a
  fault-tolerant machine.
* Quantum-augmented dual attacks use amplitude estimation/quantum search and
  assume unit-cost quantum random access to classical memory (QRACM) [S26].
  Reported Kyber improvements are conditional on that memory oracle.
* A physical-resource analysis of Grover-aided sieving finds essentially no
  speedup at dimension about 400 under its optimistic hardware assumptions,
  estimating about \(10^{13}\) physical qubits and \(10^{31}\) years [S27].
  This is a model result, not a lower bound.
* The 2026 structured-EDCP work gives reductions/equivalences for MLWE but no
  efficient stEDCP solver or ML-KEM key recovery [S28].
* Luo’s arXiv:2605.17412 claims a polynomial quantum break [S29], but the
  proposed ML-KEM output is a generator of the determinant ideal of an
  embedding whose determinant is unchanged when the target \(t=As+e\) (and
  hence the secret) changes. A value independent of \(s\) cannot certify or
  recover \(s\). The claim is therefore excluded from the credible baseline;
  no security conclusion here relies on it.

## Parameter-level synthesis

| Set | Best credible public direction at cutoff | What is established | What is not established |
|---|---|---|---|
| ML-KEM-512 | structure-aware code-based dual hybrid [S10,S17] | estimated `CC` 137.1 in [S17], with a 2.4-bit matched structure gain | executable key recovery; agreement across memory-inclusive models |
| ML-KEM-768 | structure-aware code-based dual hybrid [S10,S17] | estimated `CC` 192.7 in [S17], with a 2.4-bit matched structure gain | executable key recovery; a passive use of the 2,950-query DF result |
| ML-KEM-1024 | structure-aware code-based dual hybrid [S10,S17] | estimated `CC` 257.2 in [S17], with a 2.5-bit matched structure gain | executable key recovery; realistic quantum advantage |

The table names a direction, not a universal scalar winner. Under memory-aware
or quantum models a different row of the underlying comparisons can dominate.
As of the cutoff, the literature supports small, model-dependent concrete
refinements—not a credible asymptotic or practical break of standardized
ML-KEM.

## Primary sources

All were accessed 2026-07-22.

* **[S1]** NIST, *Module-Lattice-Based Key-Encapsulation Mechanism Standard*,
  FIPS 203 (2024). <https://doi.org/10.6028/NIST.FIPS.203>
* **[S2]** Avanzi et al., *CRYSTALS-Kyber Algorithm Specifications and
  Supporting Documentation, version 3.02*.
  <https://pq-crystals.org/kyber/data/kyber-specification-round3.pdf>
* **[S3]** Albrecht, Player, Scott, *On the Concrete Hardness of Learning with
  Errors*. <https://eprint.iacr.org/2015/046>
* **[S4]** Albrecht et al., *The General Sieve Kernel and New Records in
  Lattice Reduction*. <https://eprint.iacr.org/2019/089>
* **[S5]** Xia et al., *Refined Strategy for Solving LWE in Two-step Mode*.
  <https://eprint.iacr.org/2022/1343>
* **[S6]** Jaques, *Memory Adds No Cost to Lattice Sieving for
  Computers in 3 or More Spatial Dimensions*.
  <https://eprint.iacr.org/2024/080>
* **[S7]** Guo, Johansson, *Faster Dual Lattice Attacks for Solving LWE with
  Applications to CRYSTALS*.
  <https://doi.org/10.1007/978-3-030-92068-5_2>
* **[S8]** MATZOV, *Report on the Security of LWE: Improved Dual Lattice
  Attack*, version 2. <https://doi.org/10.5281/zenodo.6493704>
* **[S9]** Ducas, Pulles, *Accurate Score Prediction for Dual-Sieve Attacks*.
  <https://doi.org/10.1007/s00145-025-09560-7>
* **[S10]** Carrier, Meyer-Hilfiger, Shen, Tillich, *Assessing the Impact of a
  Variant of MATZOV's Dual Attack on Kyber*.
  <https://eprint.iacr.org/2022/1750>
* **[S11]** Li, Zheng, *What Happens When Integrating Modulus Switching and
  Lossy Source Coding*. <https://eprint.iacr.org/2026/1400>
* **[S12]** Pouly, Shen, *Provable Dual Attacks on Learning with Errors*.
  <https://eprint.iacr.org/2023/1508>
* **[S13]** Qu, Xu, *On the Provable Dual Attack for LWE by Modulus
  Switching*. <https://eprint.iacr.org/2025/859>
* **[S14]** Wang et al., *LaMS: A p-adic Layered Modulus Switching for
  Provable Dual Attacks on LWE*. <https://eprint.iacr.org/2026/1326>
* **[S15]** Karenin et al., *Fast Slicer for Batch-CVP: Making Lattice
  Hybrid Attacks Practical*. <https://eprint.iacr.org/2025/1910>
* **[S16]** Wang et al., *Enhancing the Dual Attack against MLWE: Constructing
  More Short Vectors Using Its Algebraic Structure*.
  <https://eprint.iacr.org/2022/1661>
* **[S17]** Ogilvie, *On the Concrete Hardness Gap Between MLWE and LWE*.
  <https://eprint.iacr.org/2026/279>
* **[S18]** Hou, Jiang, *Careful with the Ring: Enhanced Hybrid Decoding
  Attacks against Module/Ring-LWE*. <https://eprint.iacr.org/2026/366>
* **[S19]** Bassotto et al., *NoMod: A Non-modular Attack on Module Learning
  With Errors*. <https://arxiv.org/abs/2510.02162>
* **[S20]** Steiner, *The Complexity of Algebraic Algorithms for LWE*.
  <https://eprint.iacr.org/2024/313>
* **[S21]** Wang et al., *Too Far Behind? Narrowing the Gap with a
  Dual-Enhanced Two-Stage Algebraic Algorithm for LWE*.
  <https://eprint.iacr.org/2026/688>
* **[S22]** D'Anvers, Batsleer, *Multitarget Decryption Failure Attacks and
  Their Application to Saber and Kyber*.
  <https://eprint.iacr.org/2021/193>
* **[S23]** Guo, Nabokov, Johansson, *Unlocking the True Potential of Decryption Failure
  Oracles: A Hybrid Adaptive-LDPC Attack on ML-KEM Using Imperfect Oracles*.
  <https://eprint.iacr.org/2026/070>
* **[S24]** Bernstein et al., *KyberSlash: Exploiting Secret-Dependent
  Division Timings in Kyber Implementations*.
  <https://eprint.iacr.org/2024/1049>
* **[S25]** Heiser, *Improved Quantum Hypercone Locality
  Sensitive Filtering in Lattice Sieving*.
  <https://eprint.iacr.org/2021/1295>
* **[S26]** Albrecht, Shen, *Quantum Augmented Dual Attack*.
  <https://eprint.iacr.org/2022/656>
* **[S27]** Doriguello et al., *On the Practicality of Quantum Sieving
  Algorithms for the Shortest Vector Problem*.
  <https://eprint.iacr.org/2024/1692>
* **[S28]** Wen, Zheng, *Module Learning With Errors and Structured
  Extrapolated Dihedral Cosets*. <https://eprint.iacr.org/2026/155>
* **[S29]** Luo, *Module Lattice Security (Part IV): Probabilistic Polynomial
  Quantum Attack on Module-LWE over 2-Power Cyclotomics*.
  <https://arxiv.org/abs/2605.17412>

## Archival provenance

This producer artifact is bound to snapshot task `TASK-20260722-202`.
