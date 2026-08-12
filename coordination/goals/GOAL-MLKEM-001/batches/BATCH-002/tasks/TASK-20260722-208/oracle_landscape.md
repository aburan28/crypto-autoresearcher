# ML-KEM oracle and implementation-assisted attack landscape

Task: `TASK-20260722-208`
Research cutoff and URL access date: **2026-07-22**
Scope: defensive primary-source synthesis; no official state transition

## Bottom line

The reviewed record supports three different conclusions that must not be
merged:

1. **Passive core MLWE.** No reviewed source demonstrates a passive
   standardized-parameter ML-KEM key recovery. This task found no reason to
   revise the BATCH-001 passive-hardness boundary.
2. **Conditional oracle algorithms.** Adaptive LDPC and soft-information
   methods materially reduce the number of *oracle calls*. The strongest
   simple figure is 2,950 calls for ML-KEM-768 at a stipulated 95%-accurate
   one-bit DF oracle. It is not an end-to-end cost until construction,
   profiling, repeated traces, adaptivity, device access, and post-processing
   are charged.
3. **Implementation leakage.** Timing, DMP/cache, DVFS, power, EM, faults,
   masking composition, and comparison bugs have produced laboratory key
   recoveries on named targets. These results concern implementations, not the
   hardness of MLWE, and transfer only to final FIPS 203 code that reproduces
   the required channel.

The canonical machine-readable details, including complete cost fields and
defensive proposal records, are in `oracle_surface_report.yaml`.

## FIPS 203 boundary

FIPS 203 standardizes all three sets: ML-KEM-512, ML-KEM-768, and
ML-KEM-1024. Its honest decapsulation-failure rates are respectively
\(2^{-138.8}\), \(2^{-164.8}\), and \(2^{-174.8}\).

`ML-KEM.Decaps_internal` decrypts, derives re-encryption randomness,
re-encrypts, compares the complete ciphertext, and substitutes \(J(z\|c)\) on
mismatch. Both paths return a 256-bit value. Therefore:

- an honest failure probability is not a public failure oracle;
- a caller must acquire a leakage, fault, logic, or protocol-confirmation
  channel to distinguish the paths;
- K-PKE is only an internal component and is not an approved stand-alone PKE.

Final ML-KEM is derived from round-three Kyber but differs in the FO/KDF
derivation, randomness handling, shared-secret length, input checks, and
key-generation domain separation. Round-three Kyber already used implicit
rejection; final FIPS 203 changes the exact derivation rather than replacing an
explicit failure return. Source: [FIPS 203](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf),
accessed 2026-07-22.

## Material-result map

Each entry below names the oracle model, affected class, evidence level,
charged cost, patch state, final-standard transfer limit, primary source, and
the cheapest defensive gate. “Trace” means a physical or
microarchitectural measurement; it is not interchangeable with “oracle call.”

### Standard and conditional algorithmic oracles

#### ORS-001 — Ideal FIPS 203 interface

- **Oracle model:** none; only a 256-bit shared secret is returned.
- **Affected class:** every conforming FIPS 203 implementation.
- **Evidence:** standard specification.
- **Cost:** no oracle, profile, trace, or bypass exists in the ideal
  interface.
- **Patch status:** normative final standard; NIST also publishes a potential
  errata spreadsheet.
- **Transfer limit:** this is final-standard behavior, but it says nothing
  about timing, power, EM, cache, or fault silence.
- **Primary source:** [FIPS 203](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf),
  accessed 2026-07-22.
- **Cheapest gate:** byte-wise malformed-ciphertext differential testing
  against a scalar Algorithm-18 oracle.

#### ORS-002 — Multitarget failure boosting

- **Oracle model:** visible honest decryption success/failure bit.
- **Affected class:** round-three Kyber distributions with many static
  targets.
- **Evidence:** theoretical estimate, not execution.
- **Cost:** the principal tables allow \(2^{64}\) queries per target and up to
  \(2^{64}\) targets and consider maximum depth \(2^{96}\). Online
  decapsulation, precomputation, follow-up failures, finite message spaces,
  and target storage are separate costs; the source does not classify a Kyber
  parameter set as broken by its developed attack under the stated constraints.
- **Patch status:** design analysis, not a single code bug.
- **Transfer limit:** arithmetic distributions are close, but FIPS 203 does
  not export the assumed failure bit or supply an exponential target pool.
- **Primary source:** [D'Anvers–Batsleer, ePrint
  2021/193](https://eprint.iacr.org/2021/193), accessed 2026-07-22.
- **Cheapest gate:** locally instrument boosted failure rates and compare them
  with the estimator without exposing the instrumentation as an API.

#### ORS-003 — Error-tolerant inequality recovery

- **Oracle model:** a signed decryption-error inequality with an estimated
  correctness probability.
- **Affected class:** Kyber512 fault or leakage sources that produce the
  paper's inequality form.
- **Evidence:** simulation plus fault-induced demonstration.
- **Cost:** about 5,500 filtered or 9,000 unfiltered correct inequalities,
  calibration of reliability, thousands of device interactions, belief
  propagation, and lattice reduction.
- **Patch status:** the backend remains usable wherever matching inequalities
  leak.
- **Transfer limit:** ML-KEM-512 arithmetic transfers; the inequality source
  does not come from FIPS 203.
- **Primary source:** [Hermelink et al., ePrint
  2023/098](https://eprint.iacr.org/2023/098), accessed 2026-07-22.
- **Cheapest gate:** reproduce recovery thresholds on held-out synthetic
  inequalities across a swept error rate.

#### ORS-004 — Adaptive-LDPC DF attack

- **Oracle model:** one-bit DF oracle with stated accuracy.
- **Affected class:** ML-KEM-512/768 implementations permitting balanced
  multi-coefficient chosen queries.
- **Evidence:** full-key simulation plus physical Apple-M1
  near-key/partial-correction experiment.
- **Cost:** 2,400 and 2,950 calls for ML-KEM-512/768 at 95% accuracy. The M1
  experiment additionally used eviction sets, 1,000 calibration measurements,
  about 6,047.84 key-recovery traces on its 73/100 trials ending within Hamming
  distance four, and about 25 minutes including calibration.
- **Patch status:** disabling the DMP or restricting work to non-DMP cores
  removes the concrete GoFetch oracle.
- **Transfer limit:** the algorithm directly parameterizes ML-KEM, but the
  2,950 figure assumes a memoryless 95% oracle; measured M1 errors include
  bursts and platform calibration.
- **Primary source:** [Guo–Nabokov–Johansson, ePrint
  2026/070](https://eprint.iacr.org/2026/070), accessed 2026-07-22.
- **Cheapest gate:** replay measured outputs with block resampling and compare
  against the independent-bit simulation.

#### ORS-005 — Generic FO plaintext checking

- **Oracle model:** binary PCO derived from re-encryption/hash leakage.
- **Affected class:** FO-transformed KEM implementations with distinguishable
  reference messages.
- **Evidence:** physical EM/power oracle construction.
- **Cost:** classifier templates or points of interest, one or more traces per
  adaptive chosen ciphertext, and thousands of calls for early binary
  backends.
- **Patch status:** no universal patch; the complete decapsulation path,
  including symmetric primitives, must be protected.
- **Transfer limit:** final ML-KEM retains decrypt/hash/re-encrypt/compare, but
  exact KDF inputs, hash code, masks, and hardware differ.
- **Primary sources:** [ePrint 2019/948](https://eprint.iacr.org/2019/948) and
  [ePrint 2021/849](https://eprint.iacr.org/2021/849), accessed 2026-07-22.
- **Cheapest gate:** two-message held-out leakage classification over complete
  final-FIPS decapsulation.

#### ORS-006 — Parallel PC oracle

- **Oracle model:** \(2^P\)-class or \(P\)-bit parallel PCO.
- **Affected class:** tested unprotected or lightly shuffled pqm4 Kyber768 on
  Cortex-M4.
- **Evidence:** physical full-key recovery.
- **Cost:** binary baseline 1,776 target queries; P=10 gives 232 with a clone
  device but requires five traces for each of 1,024 classes (5,120 template
  traces). Without a clone, the demonstrated
  P=4/five-template setting totals 613 target queries.
- **Patch status:** shuffling was bypassed; masking was recommended but not
  proved sufficient.
- **Transfer limit:** coefficient logic transfers, while templates, final code,
  masking, and cross-device portability do not automatically transfer.
- **Primary source:** [Rajendran et al., ePrint
  2022/931](https://eprint.iacr.org/2022/931), accessed 2026-07-22.
- **Cheapest gate:** run only the held-out class classifier and account
  separately for clone and no-clone templates.

#### ORS-007 — Soft-analytic noisy PCO

- **Oracle model:** posterior distribution over parallel message classes.
- **Affected class:** ML-KEM implementations with weak but calibratable
  re-encryption leakage.
- **Evidence:** simulation and open-source solver, not universal physical
  recovery.
- **Cost:** for ML-KEM-1024 at eight positions in parallel, 1,529.6 queries at
  \(\alpha=0.5\), 944.64 at 0.7, and 706.56 at 0.9. Physical traces can greatly
  exceed oracle queries; profiling and posterior computation are charged.
- **Patch status:** attack backend, not a patch-specific bug.
- **Transfer limit:** directly parameterized for ML-KEM, but abstract
  \(\alpha\)/noise does not establish a concrete masked device distribution.
- **Primary source:** [Hermelink–Mårtensson–Tran, ePrint
  2025/1496](https://eprint.iacr.org/2025/1496), accessed 2026-07-22.
- **Cheapest gate:** replace synthetic likelihoods with held-out device traces
  and reject the model if calibration fails.

#### ORS-008 — SPRT noise handling

- **Oracle model:** repeated PCO scores with sequential likelihood stopping.
- **Affected class:** noisy, repeatable ML-KEM PCOs.
- **Evidence:** simulation.
- **Cost:** two-to-threefold fewer repeated calls than fixed majority or
  likelihood tests in the evaluated settings, in exchange for strictly online
  stopping and stationary calibrated distributions.
- **Patch status:** statistical wrapper, not a code patch.
- **Transfer limit:** algorithm-agnostic; it does not create the underlying
  leakage or survive unmodeled drift automatically.
- **Primary source:** [Poilbout–Roche–Imbert, ePrint
  2025/2045](https://eprint.iacr.org/2025/2045), accessed 2026-07-22.
- **Cheapest gate:** replay time-ordered traces with drift and compare SPRT at
  matched decision error.

### Masking and FO composition

#### ORS-009 — Masked comparison leakage

- **Oracle model:** DF bit from horizontal or vertical masked-comparison
  distributions.
- **Affected class:** the tested higher-order masked polynomial comparison.
- **Evidence:** simulations and physical oracle tests on multiple devices.
- **Cost:** a horizontal oracle can use one trace per call; a no-profile
  vertical example uses about 7,000 chosen-ciphertext traces. Higher masking
  order does not remove the tested horizontal reuse.
- **Patch status:** affected comparison requires redesign or validation in a
  stronger physical model.
- **Transfer limit:** final FIPS comparison is security-critical, but the
  leakage is not universal to every masked comparison.
- **Primary sources:** [ePrint 2024/060](https://eprint.iacr.org/2024/060) and
  [ePrint 2021/104](https://eprint.iacr.org/2021/104), accessed 2026-07-22.
- **Cheapest gate:** one-trace horizontal classification with fresh masks and
  a held-out device.

#### ORS-010 — Masked Keccak PCO

- **Oracle model:** soft PCO from masked Keccak re-encryption leakage.
- **Affected class:** tested DOM, PINI, and TI Cortex-M4 software.
- **Evidence:** physical profiled oracle plus modeled exploitation.
- **Cost:** profiles and principal-subspace templates; the strongest reported
  seven-share DOM case reaches 90% accuracy from 104 Keccak-round leakages,
  corresponding to about 50 ML-KEM executions.
- **Patch status:** no universal software patch; secure microcontrollers and
  parallel coprocessors are proposed directions.
- **Transfer limit:** Keccak remains in final ML-KEM, but call structure,
  platform, implementation, and profile portability remain conditional.
- **Primary source:** [Balon et al., ePrint
  2026/777](https://eprint.iacr.org/2026/777), accessed 2026-07-22.
- **Cheapest gate:** reproduce only the two-message classifier at two and seven
  shares on held-out traces.

#### ORS-020 — Multiple-ciphertext attack on first-order masking

- **Oracle model:** aggregated chosen-ciphertext masked leakage score.
- **Affected class:** modeled Bronchain-style first-order masked Kyber.
- **Evidence:** simulation/illustration on a specific implementation, not a
  universal physical result.
- **Cost:** 75,000 traces at SNR 0.67 for 95% reported full-key success, plus
  leakage-model calibration and multiple chosen ciphertexts.
- **Patch status:** no universal patch or physical validation claim.
- **Transfer limit:** masked K-PKE arithmetic is relevant, but the result is
  tied to one pre-standard-branded design and noise model.
- **Primary source:** [Soulami–Connan–Duquesne, ePrint
  2026/528](https://eprint.iacr.org/2026/528), accessed 2026-07-22.
- **Cheapest gate:** test whether the simulated score calibration survives a
  small real-trace campaign with fresh masks.

### Timing and microarchitecture

#### ORS-011 — KyberSlash

- **Oracle model:** variable-latency division timing, directly or as a PCO.
- **Affected class:** code/compiler/CPU combinations emitting
  secret-dependent variable-latency divisions.
- **Evidence:** physical full-key recovery.
- **Cost:** KyberSlash1 recovered Kyber512 on Raspberry Pi 2 in 2-4 hours;
  KyberSlash2 recovered Kyber768 on Cortex-M4 in about four minutes and 6,144
  decapsulations. Both demonstrations report 10/10 success.
- **Patch status:** official reference commits `dda29cc` (2023-12-01) and
  `272125f` (2023-12-30) replaced the divisions; third-party status remains
  version-specific.
- **Transfer limit:** arithmetic can recur in ML-KEM code, but the flaw is not
  mandated by FIPS 203 and patched backends are outside the demonstrated class.
- **Primary source:** [KyberSlash, ePrint
  2024/1049](https://eprint.iacr.org/2024/1049), accessed 2026-07-22.
- **Cheapest gate:** taint every generated instruction and run timing tests
  across compiler, flags, and backend.

#### ORS-012 — Power leakage after timing remediation

- **Oracle model:** simple-power classification of the multiplication-based
  timing-safe arithmetic.
- **Affected class:** tested patched standard and shuffled Cortex-M4 code.
- **Evidence:** physical full-key recovery.
- **Cost:** about 30 seconds standard and three hours shuffled, 100% reported
  success; source upper bounds are five queries per coefficient for ML-KEM-512
  and four for 768/1024.
- **Patch status:** the timing bug remains correctly patched; the power channel
  needs separate remediation.
- **Transfer limit:** explicitly framed as ML-KEM but demonstrated on one
  Cortex-M4 implementation and acquisition setup.
- **Primary source:** [Berzati et al., ePrint
  2024/2051](https://eprint.iacr.org/2024/2051), accessed 2026-07-22.
- **Cheapest gate:** require both timing and fixed-versus-random power
  regression for any arithmetic patch.

#### ORS-013 — GoFetch

- **Oracle model:** DMP-induced cache hit/miss revealing a decrypted
  pointer-like value.
- **Affected class:** tested constant-time Kyber512 reference code on Apple M1
  performance cores.
- **Evidence:** physical full-key recovery.
- **Cost:** co-location, high-resolution timer, standard and compound eviction
  sets, eight ciphertexts and 32 measurements for each of 392 recoverable
  coefficients, 59 minutes online, and 286 minutes of lattice reduction.
- **Patch status:** DIT disables DMP on tested M3 but not M1/M2; DOIT disables
  the Intel counterpart; non-DMP-core scheduling is another mitigation.
- **Transfer limit:** final ML-KEM has similar secret-dependent data, but the
  result is microarchitecture-, process-placement-, timer-, and code-specific.
- **Primary source:** [GoFetch, USENIX Security
  2024](https://www.usenix.org/conference/usenixsecurity24/presentation/chen-boru),
  accessed 2026-07-22.
- **Cheapest gate:** test only the two-class pointer predicate with DMP
  mitigation on/off.

#### ORS-014 — DVFS/Hertz leakage

- **Oracle model:** frequency hint for low-Hamming-weight NTT states.
- **Affected class:** tested NTT implementations and a simplified CPA Kyber
  variant without compression.
- **Evidence:** measured leakage plus estimator projection, not final-ML-KEM
  recovery.
- **Cost:** 425,984/851,968/1,277,952 oracle calls for ranks 2/3/4; a call can
  itself repeat decryption over a 100-second interval and collect 100,000
  frequency points.
- **Patch status:** platform/DVFS policy, not a universal algorithm patch.
- **Transfer limit:** NTT transfers, while omitted compression, CPA scope, and
  lack of full FIPS decapsulation do not.
- **Primary source:** [Yu et al., ePrint
  2024/070](https://eprint.iacr.org/2024/070), accessed 2026-07-22.
- **Cheapest gate:** compare the low-weight distinguisher with DVFS enabled
  versus fixed-frequency operation.

### Power, EM, and physical leakage without a one-bit oracle

#### ORS-015 — Adaptive EM magnification

- **Oracle model:** high-bandwidth inverse-NTT or message-recovery leakage.
- **Affected class:** tested Kyber reference and pqm4 builds on STM32F407.
- **Evidence:** physical full-key recovery.
- **Cost:** four traces for reference code and 8-960 for pqm4, with the compiler
  optimization controlling the range; chosen ciphertexts, close EM access, and
  alignment remain charged.
- **Patch status:** no universal patch.
- **Transfer limit:** arithmetic is related, but final FIPS code, compiler,
  masks, and platform require reproduction.
- **Primary source:** [Xu et al., ePrint
  2020/912](https://eprint.iacr.org/2020/912), accessed 2026-07-22.
- **Cheapest gate:** fixed-versus-random EM tests over the supported compiler
  matrix.

#### ORS-016 — Barrett-reduction clustering

- **Oracle model:** fine-grained modular-reduction leakage revealing multiple
  secret values.
- **Affected class:** tested reference and pqm4 m4 Kyber decapsulation on
  Cortex-M4.
- **Evidence:** physical full-key recovery.
- **Cost:** 6/6/8 chosen ciphertexts for reference-style
  Kyber512/768/1024 and 6/9/12 for pqm4 m4, plus high-resolution traces,
  leakage modeling, and clustering.
- **Patch status:** no universal patch verified.
- **Transfer limit:** Barrett reduction is common but its instruction schedule
  and leakage are not mandated by FIPS 203.
- **Primary source:** [Sim et al., ePrint
  2021/874](https://eprint.iacr.org/2021/874), accessed 2026-07-22.
- **Cheapest gate:** isolate the production reduction routine and test held-out
  cluster separation.

#### ORS-017 — Known-ciphertext CPA

- **Oracle model:** Hamming-weight power scores during pointwise
  multiplication; no PC/DF oracle.
- **Affected class:** tested unprotected pqm4 Kyber512 on STM32F3 Cortex-M4.
- **Evidence:** physical full-key recovery.
- **Cost:** 200 known-ciphertext traces, alignment, leakage model, and
  correlation; reported success exceeds 99%.
- **Patch status:** implementation-specific power protection required.
- **Transfer limit:** multiplication remains, but the trace count does not
  transfer across code, devices, or protections.
- **Primary source:** [Karlov–Linard de Guertechin, ePrint
  2021/1311](https://eprint.iacr.org/2021/1311), accessed 2026-07-22.
- **Cheapest gate:** held-out CPA rank-versus-trace curve on production code.

#### ORS-018 — Blind power analysis

- **Oracle model:** Hamming-weight likelihood without ciphertext knowledge.
- **Affected class:** tested reference pqm4 Kyber on Cortex-M4.
- **Evidence:** simulated full key plus physical recovery of 20 selected
  coefficients.
- **Cost:** simulations need 820 traces for a perfect classifier or 7,805 at
  95% accuracy; physical selected coefficients require about 35-5,000 traces.
- **Patch status:** no universal patch.
- **Transfer limit:** the arithmetic target transfers; full-key physical
  recovery and protected final-FIPS transfer were not shown.
- **Primary source:** [Ravi et al., ePrint
  2024/169](https://eprint.iacr.org/2024/169), accessed 2026-07-22.
- **Cheapest gate:** hold ciphertexts out entirely and test correct-coefficient
  rank on a predeclared subset.

#### ORS-019 — Profiling-device-free SASCA

- **Oracle model:** soft INTT posterior learned by NTT-to-INTT domain
  adaptation.
- **Affected class:** tested ML-KEM implementation on Atmel SAM4S.
- **Evidence:** physical full-key recovery.
- **Cost:** 100 controlled NTT profiling traces and 6.6 INTT attack traces on
  average, plus adversarial domain adaptation and SASCA. This removes a
  matching clone, not profiling or device access.
- **Patch status:** no universal patch.
- **Transfer limit:** directly targets ML-KEM, but operation similarity,
  acquisition, code, and protection are target-specific.
- **Primary source:** [Wang, ePrint
  2026/981](https://eprint.iacr.org/2026/981), accessed 2026-07-22.
- **Cheapest gate:** test NTT-to-INTT posterior calibration on held-out keys
  before full decoding.

### Fault attacks

#### ORS-021 — Fault-enabled FO inequalities

- **Oracle model:** effective/ineffective fault or FO-failure inequality.
- **Affected class:** Kyber implementations without complete decapsulation
  fault coverage.
- **Evidence:** simulations plus Cortex-M4 clock-glitch demonstrations.
- **Cost:** a foundational example reports 6,500 faulty decapsulations for
  Kyber512; device profiling, fault-window search, repeated faults, and
  statistical solving are additional.
- **Patch status:** protection must cover full dataflow, not only duplicate the
  final comparison.
- **Transfer limit:** final ML-KEM retains re-encryption, but fault physics and
  observability are implementation-specific.
- **Primary sources:** [ePrint 2021/064](https://eprint.iacr.org/2021/064) and
  [ePrint 2021/1222](https://eprint.iacr.org/2021/1222), accessed 2026-07-22.
- **Cheapest gate:** software-fault every decapsulation stage and verify
  redundant detection before physical work.

#### ORS-022 — Roulette

- **Oracle model:** noisy inequality from randomized useful fault hits.
- **Affected class:** tested masked Kyber on Cortex-M4 and related
  re-encryption targets.
- **Evidence:** physical full-key recovery with ChipWhisperer clock glitches.
- **Cost:** fewer than 10,000 inequalities, tolerance for about 25% incorrect
  inequalities, roughly one-minute solving, and thousands of faulted
  decapsulations. Masking randomness can increase useful hit probability.
- **Patch status:** countermeasures are proposed, but no universal library
  status is established.
- **Transfer limit:** related stages remain in masked ML-KEM; exact masks,
  fault physics, and coverage require reproduction.
- **Primary source:** [Delvaux, ePrint
  2021/1622](https://eprint.iacr.org/2021/1622), accessed 2026-07-22.
- **Cheapest gate:** simulate set-to-zero and skip faults outside the protected
  comparison.

#### ORS-023 — Carry Your Fault

- **Oracle model:** soft leakage from A2B carry-chain fault propagation.
- **Affected class:** masked LWE KEMs selecting the affected A2B conversion.
- **Evidence:** simulation and physical EM-fault validation on first-order
  STM32 code.
- **Cost:** targeted EM fault profiling, repeated faulty decapsulation, and
  belief propagation; the abstract does not state a verified trace count.
- **Patch status:** conversion requires fault-aware redesign or redundancy.
- **Transfer limit:** A2B is an implementation choice, not a FIPS 203
  requirement.
- **Primary source:** [Kundu et al., ePrint
  2023/1674](https://eprint.iacr.org/2023/1674), accessed 2026-07-22.
- **Cheapest gate:** software-fault every carry stage and test redundant A2B
  detection.

#### ORS-024 — Seed-pointer corruption

- **Oracle model:** direct deterministic corruption of polynomial-sampling
  state, not a PC/DF oracle.
- **Affected class:** implementations with an unprotected single seed-pointer
  flow.
- **Evidence:** physical full-key/message recovery on STM32H7 with laser
  injection.
- **Cost:** precision laser access and pointer/timing profiling; the primary
  abstract reports success up to 100% but not a verified attempt count.
- **Patch status:** countermeasures proposed; vendor-wide patch status not
  verified.
- **Transfer limit:** directly concerns final-standard sampling code, but the
  pointer coding style is not specified by FIPS 203.
- **Primary source:** [Valsaraj et al., ePrint
  2025/2009](https://eprint.iacr.org/2025/2009), accessed 2026-07-22.
- **Cheapest gate:** dataflow audit plus software corruption of pointer, length,
  and sampler state.

### Deterministic implementation bugs

#### ORS-025 — CVE-2026-10097

- **Oracle model:** deterministic PCO from an incomplete re-encryption
  comparison and a valid-versus-rejection output confirmation.
- **Affected class:** wolfSSL 5.7.0-5.9.1 ML-KEM-1024 x64 AVX2.
- **Evidence:** vendor/CNA advisory with reported full-key PoC.
- **Cost:** only 1,536 of 1,568 bytes were compared. The PoC reports about 350
  chosen ciphertexts and about 98% success; no timing or trace profiling is
  required, but a static key and output confirmation are.
- **Patch status:** fixed in wolfSSL 5.9.2, PR 10430.
- **Transfer limit:** direct violation of final FIPS 203 complete comparison;
  only the named versions/backend are implicated.
- **Primary sources:** [NVD CVE-2026-10097](https://nvd.nist.gov/vuln/detail/CVE-2026-10097)
  and [wolfSSL 5.9.2 release](https://github.com/wolfSSL/wolfssl/releases/tag/v5.9.2-stable),
  accessed 2026-07-22.
- **Cheapest gate:** mutate each final 32-byte position and compare vulnerable,
  scalar, and patched outputs.

#### ORS-026 — CVE-2026-6330

- **Oracle model:** deterministic partial comparison; acceptance confirmation
  is still required for a PCO.
- **Affected class:** wolfSSL 5.7.4-5.9.1 ML-KEM ARM64 NEON.
- **Evidence:** vendor/CNA advisory.
- **Cost:** only half of the input was compared. No end-to-end key-recovery
  query count is reported, so the CVE-2026-10097 figure is not transferred.
- **Patch status:** fixed in wolfSSL 5.9.2, PR 10192.
- **Transfer limit:** direct final-standard semantic violation, confined to the
  named versions/backend.
- **Primary sources:** [NVD CVE-2026-6330](https://nvd.nist.gov/vuln/detail/CVE-2026-6330)
  and [wolfSSL 5.9.2 release](https://github.com/wolfSSL/wolfssl/releases/tag/v5.9.2-stable),
  accessed 2026-07-22.
- **Cheapest gate:** mutate every ciphertext SIMD lane across scalar and NEON
  backends.

## Cost accounting rules

The following conversions are invalid unless explicitly justified:

- one oracle query = one physical trace;
- one chosen ciphertext = one trace;
- oracle accuracy = independent identically distributed bit errors;
- “no clone device” = no profiling;
- masking order = physical security order;
- constant instruction flow = constant power or microarchitectural behavior;
- valid-ciphertext KAT success = correct FO rejection;
- a local subcost reduction = an end-to-end attack reduction.

Every defensive evaluation should report, separately:

1. target decapsulation calls and distinct ciphertexts;
2. physical measurements per call and failed/repeated acquisitions;
3. profiling traces, keys, devices, and portability;
4. online adaptivity and timer/co-location requirements;
5. fault setup, successful-fault yield, and filtering;
6. countermeasure and bypass path;
7. offline BP, templates, domain adaptation, lattice reduction, memory, and
   verification;
8. exact-key success with confidence intervals, rather than near-key distance
   alone.

## Defensive research ranking

Two schema-complete proposals are recorded in `oracle_surface_report.yaml`.

`IDEA-20260722-002`, the cross-backend negative-ciphertext conformance matrix,
ranks first. It has deterministic vulnerable positive controls, directly covers
the two 2026 comparison CVEs, needs no physical acquisition, and can fail
cheaply if either vulnerable control is missed.

`IDEA-20260722-003`, the end-to-end soft-oracle leakage budget, has greater
potential to improve protected-device risk estimates. It is more expensive
because it requires disjoint profiling and attack keys, physical traces,
calibration, burst-aware replay, and multiple attack backends.

**Test first:** `IDEA-20260722-002`. Byte-and-lane mutation is the cheapest
valid discriminator: vulnerable releases must disagree with the scalar FIPS
oracle, while patched backends must agree. Passing would address deterministic
comparison omissions only; it would not establish side-channel or fault
resistance.

## Scope and evidence limits

- The paper and advisory metrics above are reported results, not new runs.
- Simulation is not relabeled as physical evidence.
- Near-key or partial-key evidence is not relabeled as exact full-key recovery.
- A failed reproduction, crash, timeout, or unavailable target is not negative
  mathematical evidence.
- No result changes an official hypothesis, experiment, evidence, or goal
  status.
- This report provides classification and defensive gates, not operational
  exploitation instructions for deployed systems.
