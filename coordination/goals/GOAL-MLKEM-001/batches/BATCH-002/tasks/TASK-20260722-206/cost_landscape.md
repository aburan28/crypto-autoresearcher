# Corrected ML-KEM attack-cost landscape

Task `TASK-20260722-206` · literature cutoff/access date **2026-07-22**  
Inference: `research-sol-max` requested; `gpt-5.6-sol-xhigh`, `xhigh`,
fallback used, adapter `cursor-subagent-2026-07`.

## Result

There is no universal “ML-KEM security in bits” scalar. The defensible result is
a set of model-specific series:

* The corrected Ogilvie/Hou–Jiang structure-aware code-based-dual estimates are
  `C0` 121.9/173.0/237.4, `CC` 139.1/194.7/259.0, and `CN`
  134.5/188.7/254.1 for ML-KEM-512/768/1024 [S9]. The corresponding
  structure gains are only 0–0.8 bit. Ogilvie’s published 2–3-bit gaps and
  137.1/192.7/257.2 `CC` values are stale [S8,S9].
* Li–Zheng obtain slightly lower values in selected identically named columns,
  but use a disputed normal wrong-score tail approximation [S10]. Their table
  is a provisional estimate, not a validated replacement for Hou–Jiang.
* Progressive-primal, memory-routing, and provable-dual values use different
  models and remain separate. In particular, LaMS’s corrected 191/282/390
  values are not `CC` and its 22/31/41-bit gains are only against its corrected
  CRT comparator [S13].
* Published QRS Kyber costs improve a quantum Gaussian-sampling subroutine, but
  keep the pre-correction Pouly–Shen parameters [S21]. LaMS subsequently raises
  those classical comparators from 185/273/376 to 238/347/478 [S13]. No
  corrected QRS rerun existed at the cutoff.
* No inspected source reports a passive, reproducible standardized-parameter
  ML-KEM key recovery. The record consists of estimates, component tests, and
  scaled executions.

Throughout, “Kyber-512/768/1024” is mapped to ML-KEM only when the attacked
public-key MLWE instance has \(n=256\), \(q=3329\), module rank \(2/3/4\), and
CBD parameter \(\eta_1=3/2/2\) [S1,S2]. Protocol, oracle, or implementation
claims are outside this report.

## Cost-model firewall

| Label | What it counts | What it does not count |
|---|---|---|
| `C0` | Core-SVP abstraction: one idealized SVP call, lower-order exponent terms suppressed | circuits, memory, routing, physical time |
| `CC` | classical-circuit/list-decoding-classical estimate used by the dual estimators | memory-access cost |
| `CN` | classical nearest-neighbor/query count | gates, RAM traffic, routing |
| RAM gate count | source-defined progressive-BKZ plus final-search gates | dual `CC`; physical memory |
| Memory-routing | hardware-time estimate charging routing/sorting of sieve lists | `C0`, `CC`, `CN` |
| `GE19` | source-defined quantum circuit sieve estimate | a complete fault-tolerant ML-KEM machine |
| `QN` | quantum nearest-neighbor/query model | physical gates or time |
| `Q0` | quantum Core-SVP abstraction | physical gates or time |
| Provable-dual cost | PS24/QX25/LaMS sum of BKZ, sampling, and guessing | `C0`, `CC`, or `CN` |
| QRS cost | source-defined quantum operation/query estimate for Gaussian sampling in a dual attack | `QN`, `Q0`, `GE19`, or physical resources |
| Physical | qubits, error correction, clock assumptions, elapsed time | any estimator “bit” column |

Numbers in different rows of this firewall must not be subtracted, minimized
together, or supplemented by adding a “memory penalty.”

## Classical attacks

### Primal/uSVP and progressive BKZ

Xia et al. model progressive PnJ-BKZ followed by one Pump/SVP search. Their
optimized `Sop` strategy gives [S3]:

| RAM-model metric | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| \(\log_2\) gates, trivial `S0` | 142.6 | 205.5 | 277.7 |
| \(\log_2\) gates, optimized `Sop` | 141.4 | 204.3 | 276.5 |
| \(\log_2\) stored bits, `Sop` | 98.1 | 143.2 | 194.3 |

The optimized strategy saves 1.2 bits against the paper’s matched trivial
strategy. Its 4.6/4.6/4.4-bit reductions from the paper’s older gate estimates
do not transfer to another model. The authors execute their strategy on LWE
challenges of dimensions at most 90, not on ML-KEM.

Jaques instead charges physical routing/sorting in a two-dimensional memory
model [S4]:

| Memory-routing metric | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| sieve dimension | 375 | 586 | 829 |
| \(\log_2\) sieve cost | 145.7 | 216.5 | 273.6 |
| extrapolated \(\log_2\) full primal cost | 158.7 | 229.9 | 310.2 |
| increase over updated no-routing model | 14.3 | 22.6 | 30.6 |

The full values are extrapolations that hold every non-sieve term fixed. They
are not observed attack costs and not `CC`. The latest paper/code use routing
constant \(2^{-12.8}\); the pinned repository README still says
\(2^{-19.8}\), a documentation-version gap.

### Dual-sieve-FFT and score validity

The Guo–Johansson/MATZOV line uses many short dual vectors, guessing, and FFT
scoring. Ducas–Pulles show that treating those scores as independent can
contradict unconditional results or established heuristics; target norm is a
shared confounder, and wrong-candidate tails require conditional analysis
[S6]. Bashiri–Wiemers and the 2026 unified covariance work reinforce that
uncorrelated scores are not independent [S7]. Consequently, old MATZOV-style
tables are not accepted here as a corrected baseline.

Carrier et al. replace suspect modulus switching with generalized polar-code
lossy decoding and explicitly define all three classical models [S5]:

| Carrier model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 121.8 | 173.0 | 239.0 |
| `CC` | 139.5 | 195.1 | 259.7 |
| `CN` | 134.5 | 189.8 | 254.6 |

Their decoder distortion is benchmarked on 1,000 random words per selected
code, but that is a component test, not key recovery. `CC` omits memory.
Carrier also notes that idealized product-code nearest-neighbor costs can be
about 6 bits optimistic near sieve dimension 380.

Li–Zheng combine modulus switching and lossy coding [S10]:

| Li–Zheng model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 118.09 | 172.36 | 238.12 |
| `CC` | 139.20 | 194.02 | 259.40 |
| `CN` | 134.42 | 189.36 | 253.68 |

The minimizing intermediate modulus differs by row. FFT and decoding subcosts
drop, but short-vector sampling dominates the total. More importantly, the
search models wrong-guess scores as normal while acknowledging the disputed
tail problem. These are useful candidate estimates, not independently
validated tail probabilities.

### Corrected Ogilvie/Hou–Jiang baseline

Ogilvie’s paper reports the following structure-aware values [S8]:

| Stale paper table | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 118.8 | 170.2 | 234.8 |
| `CC` | 137.1 | 192.7 | 257.2 |
| `CN` | 132.2 | 186.9 | 252.4 |

They must not be used. Hou–Jiang identify two material implementation-lineage
issues [S9]:

1. Carrier’s base code wrote `2^100` (Python XOR) instead of `2**100`.
2. Ogilvie’s rotation code passed `nfft` instead of `beta1` to the
   probability integral.

Hou–Jiang state that Ogilvie confirmed the second issue. Ogilvie’s repository
then recorded commit `77efa315…`, “fix bug in probability calculation; better
R search.” The corrected table, at a 0.3 success-probability lower bound, is:

| Model | LWE 512/768/1024 | Isometric MLWE 512/768/1024 | Matched gaps |
|---|---|---|---|
| `C0` | 121.9 / 173.0 / 237.5 | 121.9 / 173.0 / 237.4 | 0.0 / 0.0 / 0.1 |
| `CC` | 139.3 / 194.7 / 259.6 | 139.1 / 194.7 / 259.0 | 0.2 / 0.0 / 0.6 |
| `CN` | 134.8 / 189.5 / 254.2 | 134.5 / 188.7 / 254.1 | 0.3 / 0.8 / 0.1 |

The corrected maximum structure gain is 0.8 bit, not 2–3 bits. The correction
fork’s raw output agrees after rounding, but contains repeated randomized
polar-code outputs without seeds. For example, its selected raw isometric `CC`
values are 139.1191, 194.7195, and 258.9961; earlier repeated entries in the
same logs differ. Raw decimal precision is therefore not reproducible
precision.

A label-aligned screening minimum over corrected Hou–Jiang and Li–Zheng is:

| Model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 118.09 [S10] | 172.36 [S10] | 237.4 [S9] |
| `CC` | 139.1 [S9] | 194.02 [S10] | 259.0 [S9] |
| `CN` | 134.42 [S10] | 188.7 [S9] | 253.68 [S10] |

This is not yet a jointly reproduced lower envelope. Any claimed gain must
rerun the competing algorithms with one code revision, exact success target,
score-tail law, and memory convention.

### Provable dual, CRT switching, and LaMS

Pouly–Shen give a formal dual framework; Qu–Xu formally add modulus switching
and CRT recovery; LaMS fixes \(p=2\) and recovers the guessed secret
digit-by-digit [S11–S13]. LaMS also corrects an error-width substitution:
for CBD standard deviation \(\sigma\), the discrete-Gaussian width used by the
analysis must be \(\sigma_e=\sigma\sqrt{2\pi}\), not \(\sigma\).

| Source-defined provable-dual cost | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| corrected PS24 | 238 | 347 | 478 |
| corrected QX25 CRT | 213 | 313 | 431 |
| LaMS, \(p=2\) | 191 | 282 | 390 |
| LaMS gain over corrected QX25 | 22 | 31 | 41 |

These are complete source-formula estimates, but not `C0`, `CC`, or `CN`.
LaMS’s gains cannot be subtracted from Carrier or Hou–Jiang. Its repository
does not vendor or pin `lattice-estimator` and does not retain optimizer
outputs, so the publication table is not yet one-command reproducible.

### Hybrid decoding and batch-CVP

Fast Slicer implements Randomized-Slicer batch-CVP and exercises a full hybrid
pipeline on scaled Kyber-like CBD(3) LWE [S14]. The full text’s CBD boundary is
\(n=140\ldots170\), with speedup up to 3.4× over its matched primal
implementation. Other tested distributions reach up to 5× at dimensions no
greater than 210. There is no full ML-KEM estimate or solve. The artifact lives
on branch `ac_artifact`, not the default branch.

Coefficient isometries and rotated short vectors are prior art [S8,S9,S15].
Negacyclic rotations preserve the CBD laws and allow computational reuse, but
they create deterministic transforms, not fresh independent samples.
Wu–Xu’s principal example is NewHope512. For ML-KEM, the current numerical
structure effect is the corrected Hou–Jiang table.

### Algebraic and combinatorial attacks

Steiner’s Kyber-768 case study estimates BKW at 239 bits and reports
Arora–Ge/Gröbner figures of 1,588 bits (“lowest achievable”), 5,554 bits
(proven), and 4,717 bits (optimistic proven method) [S16]. Different columns
use different assumptions; none is a solve.

The 2026 dual-enhanced resultant method lowers its compared algebraic estimates
substantially [S17]:

| Algebraic estimate | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| compared Gröbner estimate | 1,584 | 1,588 | 2,014 |
| dual-enhanced resultant | 724 | 967 | 1,316 |

This narrows an algebraic gap but remains far above every lattice series in its
own operation model. The small checks validate formulas, not standardized key
recovery.

## Quantum attacks

### Quantum-augmented dual with QRACM

Albrecht–Shen speed up FFT-threshold search and score evaluation under
unit-cost quantum random access to an exponential classical vector list
(QRACM) [S18]. They explicitly warn that implementing such access has at least
linear total gate cost in the memory size even if depth is polylogarithmic.

The current revision’s quantum rows are:

| 2022/656 model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `GE19` | 139.5 | 191.9 | 252.0 |
| `QN` | 124.4 | 175.3 | 234.5 |
| `Q0` | 102.7 | 154.6 | 215.0 |
| augmented `QN` | 119.3 | 168.3 | 225.6 |
| augmented `Q0` | 99.7 | 150.0 | 208.4 |

Budroni–Mårtensson’s exact enumeration calculation re-estimates the same model
family [S19]:

| Enumeration-reestimated model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `GE19` | 139.1 | 190.6 | 251.0 |
| `QN` | 123.6 | 174.5 | 233.4 |
| `Q0` | 102.4 | 154.5 | 214.5 |
| augmented `QN` | 118.0 | 166.3 | 223.2 |
| augmented `Q0` | 98.4 | 148.0 | 206.2 |

Each row is a separate model. None includes QRACM construction or a
fault-tolerant architecture, and the underlying heuristic dual-score concerns
remain relevant.

### Quantum sieving

Heiser improves the asymptotic quantum hypercone-LSF sieve time from
\(2^{0.2653d+o(d)}\) to \(2^{0.2571d+o(d)}\) [S20]. The paper does not provide
an end-to-end ML-KEM-512/768/1024 cost. Substituting this exponent into `C0`,
`QN`, or a physical model without reoptimization is invalid.

### Quantum rejection sampling and the correction collision

Ling–Yan–Zhao replace the classical lattice-Gaussian sampling factor
\(1/\Delta\) with QRS scaling \(1/\sqrt{\Delta_R}\) [S21]. At fixed
Pouly–Shen parameters they publish:

| Source-defined QRS comparison | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| no-switching comparator | 185 | 273 | 376 |
| no-switching QRS | 176 | 269 | 363 |
| switching comparator, explicitly indicative | 141 | 202 | 279 |
| switching QRS, explicitly indicative | 141 | 201 | 261 |

Those absolute values are not a current baseline. LaMS, published later in the
cutoff window, identifies the Gaussian-width error and reports corrected
classical comparators 238/347/478 and 213/313/431 [S13]. No paper reruns QRS
under that correction. This does not falsify the QRS theorem; it means its
9/4/13-bit fixed-parameter deltas and absolute tables need recomputation and
global reoptimization.

Chevignard–Schrottenloher–Shen independently obtain a quadratic sampling
speedup [S22]. One dual variant retains qRAM; the second has higher time but
polynomial online classical/quantum memory, excluding Gaussian-sampler
preprocessing. They intentionally give no concrete Kyber table because their
analysis lacks the modulus switching needed for competitive costs.

### Physical resources

Doriguello et al. compile arithmetic, non-asymptotic Grover search, QRAM,
surface-code/error-correction, and architecture assumptions [S23]. For
dimension 400, under optimistic \(10^{-5}\) circuit noise, 100 ns code cycles,
and 1 µs reaction time, spherical-LSF GaussSieve requires approximately
\(10^{13}\) physical qubits and \(10^{31}\) years. Bucket-brigade QRAM
dominates qubits.

This is a dimension-400 SVP case study, not a full ML-KEM attack and not a
lower bound. It cannot be converted into `QN`, `Q0`, or “physical ML-KEM
security bits.” No end-to-end physical-resource estimate for all three
standardized parameter sets was found.

## Estimates, executions, and solves

| Evidence kind | What was found |
|---|---|
| Estimates | every cryptographic-scale numeric table above |
| Component tests | Carrier polar decoding; covariance/score prediction; sieve simulators |
| Toy/scaled executions | PSSearch LWE challenges up to dimension 90; Fast Slicer CBD(3) dimensions 140–170; Wu–Xu/NewHope and other non-ML-KEM demonstrations |
| Standardized passive ML-KEM solve | **none** |
| Physical quantum execution | **none** |

Timeouts, unavailable code, or failed reproduction would be infrastructure
outcomes, not negative mathematical evidence.

## Reproducibility ledger

| Artifact | Pinned revision | Material note |
|---|---|---|
| Hou–Jiang correction fork | [`7cce6a5`](https://github.com/identitymapping/CodedDualAttack/tree/7cce6a5572420004da31be58f26954cedfc885d0) | corrected raw outputs; random seeds absent |
| Ogilvie source | [`77efa31`](https://github.com/TabOg/CodedDualAttack/commit/77efa3150a2c19809b5499e504bf7c2eab374935) | probability bug fix and better \(R\) search |
| Carrier source | [`9c1367f`](https://github.com/kevin-carrier/CodedDualAttack/tree/9c1367f85d26038244bc83c025d84c0b7006f2ee) | code-based dual baseline |
| LaMS | [`f784884`](https://github.com/latticewalker/LaMS/tree/f7848842d8573ef3e6b6b90acc909afdf700e4d1) | no vendored estimator or saved outputs |
| PSSearch | [`4b3da61`](https://github.com/Summwer/pro-pnj-bkz/tree/4b3da615943371ff72603dd9351326b69d94508e) | progressive strategy code |
| Two-step estimator | [`a1129fa`](https://github.com/Summwer/lwe-estimator-with-pnjbkz/tree/a1129fac4416b64fa6f4c8122739b5dc89a7b8c5) | output/code lineage |
| Memory-routing estimator | [`d197843`](https://github.com/sam-jaques/sieve-memory-estimates/tree/d197843ddb406102ba101f426ea5a59e8a8a306f) | README constant is stale relative to code |
| Fast Slicer artifact | [`bd72687`](https://github.com/ElenaKirshanova/g6k_hybrid/tree/bd72687b2ebbaff16fb692259f83b327bbcd9586) | `ac_artifact` branch, not default |
| `lattice-estimator` audit pin | [`3e48ef4`](https://github.com/malb/lattice-estimator/tree/3e48ef421ec256afddb3e7d2249a77eab6e9ba12) | audit choice; LaMS does not declare this pin |
| base sieve-cost code | [`a4d3a53`](https://github.com/jschanck/eprint-2019-1161/tree/a4d3a53fe1f428fe3b4402bd63ee164ba6cc571c) | ancestor of later cost implementations |

Additional gaps:

* Li–Zheng 2026/1048 and 2026/1400 expose no pinned estimator revision in the
  inspected primary records.
* LaMS hard-codes corrected PS24 totals but searches QX25/LaMS, so one command
  does not regenerate every comparator independently.
* Exact CBD distributions are sometimes replaced by Gaussian surrogates.
  Cross-paper comparison requires matching or bounding that approximation.
* No corrected post-LaMS QRS table or physical ML-KEM circuit exists in the
  inspected record.

## Primary sources

All URLs were accessed 2026-07-22.

* **[S1]** NIST, FIPS 203. <https://doi.org/10.6028/NIST.FIPS.203>
* **[S2]** Avanzi et al., *CRYSTALS-Kyber Specification v3.02*.
  <https://pq-crystals.org/kyber/data/kyber-specification-round3.pdf>
* **[S3]** Xia et al., *Refined Strategy for Solving LWE in Two-step Mode*.
  <https://eprint.iacr.org/2022/1343>
* **[S4]** Jaques, *Memory Adds No Cost to Lattice Sieving for Computers in 3
  or More Spatial Dimensions*. <https://eprint.iacr.org/2024/080>
* **[S5]** Carrier et al., *Assessing the Impact of a Variant of MATZOV’s Dual
  Attack on Kyber*. <https://eprint.iacr.org/2022/1750>
* **[S6]** Ducas–Pulles, *Accurate Score Prediction for Dual-Sieve Attacks*.
  <https://doi.org/10.1007/s00145-025-09560-7>
* **[S7]** Li–Zheng, *Unified Dual Attack Analyses*.
  <https://eprint.iacr.org/2026/1048>
* **[S8]** Ogilvie, *On the Concrete Hardness Gap Between MLWE and LWE*.
  <https://eprint.iacr.org/2026/279>
* **[S9]** Hou–Jiang, *Careful with the Ring*.
  <https://eprint.iacr.org/2026/366>
* **[S10]** Li–Zheng, *What Happens When Integrating Modulus Switching and
  Lossy Source Coding*. <https://eprint.iacr.org/2026/1400>
* **[S11]** Pouly–Shen, *Provable Dual Attacks on Learning with Errors*.
  <https://eprint.iacr.org/2023/1508>
* **[S12]** Qu–Xu, *On the Provable Dual Attack for LWE by Modulus
  Switching*. <https://eprint.iacr.org/2025/859>
* **[S13]** Wang et al., *LaMS*. <https://eprint.iacr.org/2026/1326>
* **[S14]** Karenin et al., *Fast Slicer for Batch-CVP*.
  <https://eprint.iacr.org/2025/1910>
* **[S15]** Wu–Xu, *Enhancing the Dual Attack against MLWE*.
  <https://eprint.iacr.org/2022/1661>
* **[S16]** Steiner, *The Complexity of Algebraic Algorithms for LWE*.
  <https://eprint.iacr.org/2024/313>
* **[S17]** Wang et al., *Too Far Behind? Narrowing the Gap with a
  Dual-Enhanced Two-Stage Algebraic Algorithm for LWE*.
  <https://eprint.iacr.org/2026/688>
* **[S18]** Albrecht–Shen, *Quantum Augmented Dual Attack*.
  <https://eprint.iacr.org/2022/656>
* **[S19]** Budroni–Mårtensson, *Improved Estimation of Key Enumeration with
  Applications to Solving LWE*. <https://eprint.iacr.org/2023/139>
* **[S20]** Heiser, *Improved Quantum Hypercone Locality Sensitive Filtering
  in Lattice Sieving*. <https://eprint.iacr.org/2021/1295>
* **[S21]** Ling–Yan–Zhao, *Improved Dual Attack and Trapdoor Sampling via
  Quantum Rejection Sampling*. <https://eprint.iacr.org/2026/979>
* **[S22]** Chevignard–Schrottenloher–Shen, *Quantum Algorithm for Discrete
  Gaussian Sampling*. <https://eprint.iacr.org/2026/984>
* **[S23]** Doriguello et al., *On the Practicality of Quantum Sieving
  Algorithms for the Shortest Vector Problem*.
  <https://eprint.iacr.org/2024/1692>
