# Prime-field ECDLP coordinate/orbit idea packet — 2026-10-05

## Intake status

- Source type: user-directed external idea intake.
- Scope: classical ECDLP in prime-order subgroups of short-Weierstrass curves over prime fields.
- Exclusions: no Pollard-rho walk and no index-calculus relation collection.
- Evidence tier: toy, external to this repository's contract/run-receipt system.
- Canonical status: none. This file allocates no IDEA, hypothesis, experiment, evidence, or decision identifier and changes no official research state.
- Bottom line: no general ECDLP break was found. The packet is useful as six explicit mechanisms, toy observations, and deduplication/control evidence.
- Import rule: the observations below are screening priors only until reproduced under a frozen repository experiment and reviewed under the repository contract.

The originating implementation and raw JSON were produced in a separate local repository. They were not copied into this repository by this intake. Source hashes reported by that repository were:

| Source artifact | SHA-256 |
|---|---|
| ecdlp_lab.py | e8df3a3997d64014dd83f719a2fe5b9c0e25d20ad62ef616470e721300129c62 |
| tests/test_ecdlp_lab.py | 23f760bf6daa66b2a194f8c2ca48d8f410234710ef382c529edf839331a60981 |
| results/baseline.json | c84ab1e00abe717e6eb0d035b4c1d45b9356c9b8516d898969867472ac0bf411 |
| results/spectral-controls.json | 7b0995b970d2b75ad4c1221aeab45df83fcb503554bf1f0b54dfa58217d29f1c |

A hash is only a provenance locator here. It is not a repository run receipt and does not make the absent artifact independently reproducible.

## Executive assessment

Six coordinate-specific alternatives were made concrete and tested. The successful toy procedures either used essentially one field element of advice per group element, enumerated the complete scalar orbit, or widened a binary tree. The mechanisms that were supposed to avoid those costs did not survive their controls.

| Label | Proposed mechanism | Toy observation | Intake disposition |
|---|---|---|---|
| H1 | Predict a low scalar digit from affine coordinates, then peel digits recursively | Held-out parity accuracy 47.7%–60.6%; unstable full-key recovery | Duplicate/control for ECDLP-IDEA-045; scoped negative |
| H2 | Interpolate the fixed-base log as a low-pole-order function on the curve | Exact fit first appeared with 83 coefficients for a group of order 83 | Known interpolation/advice family; scoped negative |
| H3 | Decode the unknown scalar as a cyclic shift of a sparse coordinate-orbit spectrum | About 15%–20% of all modes were needed; matched random signals were as good or better on all seven curves | Direct negative control for ECDLP-IDEA-110 and ECDLP-IDEA-048 |
| H4 | Rank the two inverse-doubling branches using lifted coordinate height or curve-equation carry | No consistent advantage over a scrambled-coordinate control at the larger toy orders | Binary-division prior art plus a distinct but weakened ranking variant |
| H5 | Compress scalar-orbit coordinate sequences with a short linear recurrence | Linear complexity was r or r−1 on every tested sequence and curve | Duplicate/control for H-ECDLP-92a375; scoped negative |
| H6 | Extend the p-adic lift-defect quotient from anomalous to ordinary curves | 96/96 recovery on each anomalous control; 0%–3.1% on ordinary curves | Known Smart case plus a failed ordinary-curve generalization |

No row above is promoted as a new canonical idea. H4's scoring rule is the narrowest distinct operation in the packet, but the experiment did not show a stable signal and the underlying binary-division tree is published prior art.

## Test objects

Every ordinary test group was the full prime-order group of the listed curve.

| Name | Curve over F_p | Generator | Prime order |
|---|---|---|---:|
| E101 | y² = x³ + 6x + 9 over F_101 | (0, 3) | 83 |
| E127 | y² = x³ + x + 7 over F_127 | (1, 3) | 109 |
| E149 | y² = x³ + 2x + 8 over F_149 | (2, 13) | 139 |
| E211 | y² = x³ + x + 1 over F_211 | (0, 1) | 223 |
| E283 | y² = x³ + 2x + 7 over F_283 | (0, 63) | 281 |
| E503 | y² = x³ + 3x + 8 over F_503 | (0, 189) | 499 |
| E907 | y² = x³ + x + 1 over F_907 | (0, 1) | 947 |

Two trace-one curves were used only as known-true controls for the p-adic mechanism:

| Name | Curve over F_p | Generator | Order |
|---|---|---|---:|
| A163 | y² = x³ + x + 4 over F_163 | (0, 2) | 163 |
| A367 | y² = x³ + x + 3 over F_367 | (2, 115) | 367 |

These sizes test implementation correctness and simple structural hypotheses. They support no direct extrapolation to cryptographic sizes.

## H1 — coordinate-residue digit peeling

Class: algorithm/control.

Claim under test: a public low-complexity function of the affine coordinates of [k]P predicts a low digit of k with enough out-of-sample advantage that repeated affine normalization recovers k in logarithmically many rounds.

Mechanism: train a small categorical predictor for parity using coordinate residues. Given its predicted bit b for a live point R, replace R by [2⁻¹](R − [b]P) and repeat. A genuine point-to-bit oracle would shrink the remaining scalar by one binary digit per round.

Required observables:

- held-out bit accuracy materially and stably above 1/2;
- complete-key recall on targets excluded from training;
- survival under new curves, generators, and coordinate encodings;
- total training/advice and recursive query cost below the square-root frontier.

Minimal discriminating test: freeze the feature family and split by scalar before fitting. Compare with balanced random labels and with a scalar-to-point relabeling that preserves feature marginals. Do not count a recursive step that re-enters a known-log training point as out-of-sample evidence.

Observation: best held-out parity accuracies across the seven curves ranged from 0.477 to 0.606. Complete-key recovery was normally zero. Two isolated full-key rates, 0.161 and 0.080, occurred because recursive peeling entered the large known-log training set; they were not evidence that the held-out bit predictor generalized.

Falsification boundary met: the coordinate features did not supply a stable target-independent scalar-bit oracle. This is a scoped result for the frozen feature/training family, not a theorem that every coordinate predicate is useless.

Repository deduplication:

- ECDLP-IDEA-045 already formalizes the stronger public algebraic hard-bit predicate plus affine hidden-number decoding. The present learner is a negative implementation control because it consumes scalar-labelled training data and does not meet IDEA-045's target-independent predicate requirement.
- The repository's representation-and-operation rule also warns that a lossy coordinate projection under full translation is either non-equivariant, branching, or hides the original scalar orientation.

External literature checked:

- Boneh and Shparlinski, On the Unpredictability of Bits of the Elliptic Curve Diffie-Hellman Scheme, DOI 10.1007/3-540-44647-8_12.
- Related elliptic hidden-number and hard-core-bit work is adjacent, but it does not supply the predictor tested here.

Disposition: preserve as a negative control; do not allocate a new idea ID.

## H2 — function-field log interpolant

Class: representation/control.

Claim under test: for a fixed generator P, the map (x([k]P), y([k]P)) ↦ k has a representation of pole order o(r), preferably below r^(1/2), in a Riemann–Roch basis 1, x, y, x², xy, and so on.

Mechanism: solve a linear interpolation system for the discrete-log table in a basis of rational functions on E. If the first exact representation used few coefficients and could be constructed without enumerating every log, online evaluation would be an unusual fixed-base DLP oracle.

Required observables:

- first exact pole order and coefficient count as a function of subgroup order r;
- setup queries, known logs, storage, and field operations;
- held-out exact recovery;
- comparison with arbitrary relabelings of the same point set.

Minimal discriminating test: on the order-83 curve, try increasing pole orders and require exact agreement on all 82 nonidentity points. Charge every supplied log and coefficient.

Observation: pole orders below 83 failed. Pole order 83, with 83 coefficients and 82 supplied nonidentity logs, recovered every target. The resulting object is an orbit-sized advice table written in polynomial form.

Falsification boundary met: no compression was observed on the tested curve. The successful evaluator does not improve total DLP cost because its construction consumes the answer table and its state is linear in the group order.

Repository deduplication and known results:

- IDEA-20261003-cd1903 is the repository's current algebraic-omega/interpolation formulation, including a degree-versus-agreement model and Lange–Winterhof as its nearest work.
- KR-RHO-ea34b8 records the correct accounting boundary for DLP with preprocessing.
- KR-RHO-13bf67 records the generic-group square-root lower bound; orbit-sized advice is a representation-specific preprocessing regime rather than a generic contradiction.

External literature checked:

- Lange and Winterhof, Polynomial Interpolation of the Elliptic Curve and XTR Discrete Logarithm, DOI 10.1007/3-540-45655-4_16.
- Corrigan-Gibbs and Kogan, The Discrete-Logarithm Problem with Preprocessing, ePrint 2017/1113.

Disposition: known/duplicate family and a useful advice-size control; do not allocate a new idea ID.

## H3 — sparse spectral phase decoder

Class: algorithm/control.

Claim under test: the coordinate-orbit signal

    s[k] = exp(2π i x([k]P) / p)

has an elliptic-curve-specific sparse Fourier representation that permits recovery of the unknown cyclic shift from a short exact target window using sublinear support.

Mechanism: enumerate the known fixed-base orbit, compute its spectrum, retain its largest modes, reconstruct an approximation, and identify the target shift from the values at Q, Q+P, and subsequent points. This first checks whether a sparse spectral channel exists; it does not credit full-orbit enumeration as a fast algorithm.

Baseline observation: retaining roughly one quarter of all modes produced 100% accuracy on six curves and 98.8% on the order-499 curve. With approximately sqrt(r) modes, accuracy declined from 0.805 at order 83 to 0.130 at order 947. Peak single-mode energy was only a few percent.

Predetermined null-model rule: at the first tested point reaching at least 95% recovery, the EC signal's retained-mode fraction had to be lower than every one of five shuffled-coordinate replicates and every one of five independent random-field-phase replicates on at least five of seven curves.

Null-model result:

| Curve | Order | EC mode fraction | Shuffled median | Random-phase median | Beat every control? |
|---|---:|---:|---:|---:|---|
| E101 | 83 | 0.1566 | 0.1566 | 0.1566 | no |
| E127 | 109 | 0.1560 | 0.2018 | 0.2018 | no |
| E149 | 139 | 0.1511 | 0.1511 | 0.1511 | no |
| E211 | 223 | 0.2018 | 0.1525 | 0.1525 | no |
| E283 | 281 | 0.1530 | 0.1530 | 0.1530 | no |
| E503 | 499 | 0.2004 | 0.1503 | 0.2004 | no |
| E907 | 947 | 0.1510 | 0.1510 | 0.1510 | no |

Supporting curves: 0/7, versus the required 5/7.

Interpretation: a short window of a generic random cyclic signal acts as a fingerprint. Keeping approximately 15%–20% of its largest modes was enough on this coarse grid to match the window, and the EC signal had no special advantage. The toy decoder worked because it used exhaustive setup plus generic random-signal fingerprinting.

Repository deduplication:

- ECDLP-IDEA-048 already states the stronger significant-Fourier coefficient mechanism with sublinear query access and explicitly rejects a dense DFT or materialized orbit table.
- ECDLP-IDEA-110 is the closest semantic match. Its disproof track calls for exhaustive spectra, matched random functions, and random scalar relabeling; its falsification rule says a gain that survives random relabeling is an artifact. This packet supplies a smaller external version of exactly that control.
- ECDLP-IDEA-101 and other transform records cover related Fourier/Heisenberg basis changes, but H3 needs no additional merge target beyond 048 and 110.

External literature checked:

- Ahmadi and Shparlinski, Exponential Sums over Points of Elliptic Curves, arXiv:1302.4210.
- Lange and Shparlinski, Certain exponential sums and random walks on elliptic curves, DOI 10.4153/CJM-2005-015-8.

Disposition: preserve the 0/7 null result as external screening evidence for 048/110; do not allocate a new idea ID.

## H4 — integer-lift/carry-ranked binary descent

Class: algorithm/measurement.

Claim under test: in the two-way inverse-doubling tree

    R' = [2⁻¹](R − [b]P),  b in {0,1},

the branch consistent with the next scalar bit has a public integer-lift signature: smaller centered-coordinate height or smaller carry in the lifted curve equation. A beam search ranked by that signature would keep the correct path with width r^theta for theta below 1/2.

Mechanism: expand both bit choices, score each child using only its public affine coordinates and fixed integer representatives, and retain the best W children. Compare height and carry rankings with a deterministic scrambled-coordinate score of the same shape.

Required observables:

- recovery versus beam width W and subgroup order;
- improvement over the scrambled control on held-out curves and generators;
- measured growth exponent of the smallest W needed for fixed recovery;
- complete work including all expanded branches.

Observation at W = 32:

| Order | Height ranking | Carry ranking | Scrambled control |
|---:|---:|---:|---:|
| 83 | 1.000 | 1.000 | 1.000 |
| 109 | 1.000 | 1.000 | 0.843 |
| 139 | 1.000 | 1.000 | 0.920 |
| 223 | 0.712 | 0.577 | 0.284 |
| 281 | 0.689 | 0.911 | 0.225 |
| 499 | 0.406 | 0.566 | 0.627 |
| 947 | 0.473 | 0.367 | 0.452 |

The high rates at the smallest orders largely reflect the broad beam and early termination in a small binary tree. At orders 499 and 947 the coordinate scores did not consistently beat the scrambled control. The worst-case tree remains exponential.

Falsification boundary met: the tested height/carry scores did not show a stable coordinate-specific ranking advantage. This does not prove that every possible branch invariant fails.

Repository and external prior art:

- ECDLP-IDEA-034 is adjacent but not identical: it proposes a simultaneous p/N Hasse-gap carry lattice. The present experiment ranks branches using a single-child integer lift and supplies no two-modulus lattice.
- ECDLP-IDEA-005 is the broader global-lift/height neighbor.
- Verkhovsky and Polyakov, Binary Division Attack for Elliptic Curve Discrete Logarithm Problem, DOI 10.14738/tnc.24.293, already publishes the binary-division tree and states exponential worst-case complexity. The height/carry beam score is the distinct variant tested here.

Disposition: preserve as a weakened pre-ID variant and external negative measurement; a new canonical proposal would require a new invariant with a pre-run scaling argument.

## H5 — coordinate-recurrence compression

Class: representation/control.

Claim under test: scalar-orbit sequences derived from public coordinates have a short constant-coefficient linear recurrence whose companion state can be inverted to the scalar index in less than square-root total work.

Mechanism: apply Berlekamp–Massey to the periodic sequences x([k]P), y([k]P), the quadratic character of x([k]P), and the low bit of x([k]P). A short recurrence would be only the first gate; a complete algorithm would also need a sub-square-root state-index decoder.

Observation: on every tested curve the measured linear complexity was r or r−1 for all four sequence families. For the x-coordinate sequence specifically, L/r = 1.000 on all seven curves.

Falsification boundary met: none of the frozen rational/coordinate predicates compressed. The result is curve- and predicate-scoped and does not establish a universal lower bound.

Repository deduplication:

- H-ECDLP-92a375 already freezes the full recurrence-state question, including random balanced-word controls, collision fibres, and the explicit warning that recurrence fitting is only a measurement primitive.
- IDEA-20260904-d84512 and the repository's elliptic-net/orbit records cover neighboring interpolation and recurrence formulations.

External literature checked:

- Mérai and Winterhof, On the linear complexity profile of some sequences derived from elliptic curves, arXiv:1509.06909.

Disposition: direct duplicate/control for H-ECDLP-92a375; do not allocate a new idea ID.

## H6 — generalized p-adic lift-defect quotient

Class: mechanism/control.

Claim under test: Smart's p-adic lift functional for trace-one curves might extend to ordinary non-anomalous prime-order curves when deterministic noncanonical lifts are used. Lift E and its points modulo p², multiply the lifts by the subgroup order, map the resulting kernel points with the formal parameter −x/y, and take the target/generator ratio.

Mechanism: on an anomalous curve of order p, the formal-group quotient is scalar-linear and reveals the log. The proposed extension asked whether a deterministic section defect accidentally preserves enough of that linearity when the subgroup order n is prime but n ≠ p.

Required observables:

- exact recovery on trace-one positive controls;
- ordinary-curve recovery compared with the 1/p chance scale;
- refusal or explicit treatment of noninvertible denominators and exceptional lifts;
- survival across independently generated ordinary curves.

Observation:

- A163: 96/96 sampled logs recovered exactly.
- A367: 96/96 sampled logs recovered exactly.
- Ordinary curves: recovery accuracy ranged from 0.000 to 0.031.

Falsification boundary met: the implementation detected the known anomalous signal and the same quotient was noise on the tested ordinary curves. The successful branch is Smart's attack, not a new result.

Repository deduplication and known results:

- KR-RHO-53c89f records p-adic anomalous-curve attacks as special-curve transfers, not general ECDLP algorithms.
- H-ECDLP-f1e714 is the repository's richer non-anomalous p-adic digit/defect spectral measurement with anomalous calibration.
- H-ECDLP-6a9479 and EXP-ECDLP-a26bde record the exact formal-group digit identity for explicit global lifts, the quadratic height price, and the point where the anomalous case breaks.
- ECDLP-IDEA-004 and ECDLP-IDEA-436 cover adjacent prime-to-p jet and canonical-torsion-lift coordinate questions.

External literature checked:

- Smart, The Discrete Logarithm Problem on Elliptic Curves of Trace One, Journal of Cryptology 12 (1999), 193–196.
- Jacobson, Koblitz, Silverman, Stein, and Teske, Analysis of the Xedni Calculus Attack, DOI 10.1023/A:1008312401197.

Disposition: known positive control plus a failed ordinary-curve generalization; do not allocate a new idea ID.

## Consolidated baseline observations

The table uses the first approximately sqrt(r)-mode spectral cell and the approximately r/4 cell from the baseline run. Beam columns use width 32. BM x/r is the x-coordinate sequence's linear complexity divided by the group order.

| Order | H1 bit | H1 full key | H3 sqrt modes | H3 about r/4 | H4 height | H4 carry | H4 random | H5 BM x/r | H6 ordinary |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 83 | 0.606 | 0.000 | 0.805 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.024 |
| 109 | 0.477 | 0.000 | 0.796 | 1.000 | 1.000 | 1.000 | 0.843 | 1.000 | 0.031 |
| 139 | 0.482 | 0.161 | 0.739 | 1.000 | 1.000 | 1.000 | 0.920 | 1.000 | 0.031 |
| 223 | 0.539 | 0.000 | 0.505 | 1.000 | 0.712 | 0.577 | 0.284 | 1.000 | 0.000 |
| 281 | 0.482 | 0.080 | 0.496 | 1.000 | 0.689 | 0.911 | 0.225 | 1.000 | 0.010 |
| 499 | 0.535 | 0.000 | 0.283 | 0.988 | 0.406 | 0.566 | 0.627 | 1.000 | 0.000 |
| 947 | 0.530 | 0.000 | 0.130 | 1.000 | 0.473 | 0.367 | 0.452 | 1.000 | 0.000 |

H2 is omitted from the table because it was run only as the exact order-83 interpolation gate: first exact fit at 83 coefficients after supplying all 82 nonidentity logs.

## Prior-art screen and repository positioning

The known-results map was read before import. Rows most directly bearing on this packet were:

- KR-RHO-13bf67: a sub-square-root method must exploit the representation rather than only generic group operations.
- KR-RHO-ea34b8: fixed-group preprocessing and online work must be charged together.
- KR-RHO-53c89f: anomalous and small-embedding-degree attacks are special-curve checks.
- KR-IC-cd159a: characteristic-zero/global-lift ECDLP approaches inherit the xedni obstruction.
- KR-IC-9e610d: no known general prime-field ECDLP attack beats rho.

The repository corpus search also found the internal records named in each section. Therefore none of the six mechanisms is represented here as a genuinely new unscreened algorithm.

The literature search was targeted rather than exhaustive. It checked the nearest primary sources listed above and Semaev's summation-polynomial work only to maintain the exclusion boundary. Absence of another source is not evidence of novelty.

## Suggested repository follow-up

1. Treat H3's 0/7 matched-null result as an external screening prior for ECDLP-IDEA-110. If the Coordinator wants admissible evidence, reproduce it under a frozen contract with the larger curve/size schedule already specified by IDEA-110.
2. Treat H4 as the only narrowly distinct operation in the packet. Do not allocate it unless a new, target-independent branch invariant predicts a beam-width exponent below 1/2 before tuning.
3. Use H1, H2, H5, and H6 as regression controls when testing future coordinate representations:
   - labelled training must not masquerade as a public bit oracle;
   - orbit-sized interpolation must be reported as advice;
   - a Fourier shift solver must beat matched random signals;
   - a recurrence must include the state-index inversion cost;
   - every p-adic proposal must separate the anomalous n = p mechanism from ordinary n ≠ p curves.
4. Do not infer a general closure from these toy failures. Each negative closes only the exact frozen representation, observable, and test boundary above.
