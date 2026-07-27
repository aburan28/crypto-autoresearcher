# Independent falsification review of BATCH-002

Task `TASK-20260722-211`  
Machine-readable verdict: `red_team_report.yaml` (`RT-20260723-001`)  
Role: independent Red Team; no official state change

## Scope and evidence basis

This review asks whether the committed BATCH-002 synthesis overstates novelty,
cost comparability, oracle realism, or experiment readiness. It does not decide
the goal, hypothesis, evidence, or experiment state.

The reviewed producer snapshot is commit
`f4425f5ac689eef52e406363ca8d12795fa6e801`, with parent
`62151b25c7b5ffb2fbe28081efa1bb2c2b525dcc`. It contains the six declared
producer files from `TASK-20260722-206`, `TASK-20260722-207`, and
`TASK-20260722-208`. Their SHA-256 values match
`archives/TASK-20260722-209/snapshot-receipt.json`, and the commit is reachable
from the current history. The receipt's own `commit_sha` is null because of its
self-reference convention; the commit subject and Git parent bind the snapshot
to `TASK-20260722-209`. This is a provenance blemish to preserve, not a reason
to discard the six hash-matched producer artifacts. Uncommitted dispatch and
review files were not treated as research evidence.

The review preserves four boundaries:

1. absence from the inspected corpus is not an impossibility theorem;
2. estimates, simulations, physical traces, oracle calls, and verified solves
   are different evidence and cost classes;
3. a defect in one version and backend does not transfer to ML-KEM generally;
4. an infrastructure or reproduction failure would not be negative
   mathematical evidence.

## Verdict

The verdict is **scoped repairs required**. Three claims fail as stated, five
questions remain unresolved because the available sources or protocols do not
settle them, and five narrower negative conclusions survive.

The following parts of the producer synthesis remain credible within the
inspected-source boundary:

- the cost-model firewall and the corrected Ogilvie/Hou--Jiang table;
- the FIPS 203 ideal-interface boundary and Algorithm 18 implicit rejection;
- the requirement to charge oracle construction, profiling, traces,
  adaptivity, device access, protocol confirmation, and post-processing;
- the named version/backend scopes of the two wolfSSL comparison defects;
- the finding that no inspected source supplies a verified passive
  standardized-parameter ML-KEM key recovery.

The following stronger claims do not survive:

- the Fourier adjoint identity alone closes every possible computational
  saving from the LaMS-isometry representation;
- one category label cleanly separates abstract oracle algorithms from
  physical implementations;
- the proposed end-to-end byte/lane mutation suite necessarily detects every
  represented incomplete comparison.

None of these defects is evidence that passive MLWE is weak.

## Material source checks

The material records were checked on 2026-07-23. No later revision than the
producer cutoff was visible for the listed ePrint records. That is a freshness
check for named records, not proof that the literature search was exhaustive.
Most producer citations retain access dates but not paper-PDF hashes or a
screened-query log, so exact reconstruction after a future preprint revision
is not guaranteed.

- [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) still specifies all
  three ML-KEM parameter sets and publishes a potential-errata sheet. The
  currently identified zeta-array clarification and Algorithm 15 comment
  correction do not change Algorithm 18 implicit rejection or the reported
  failure rates.
- [LaMS, ePrint 2026/1326](https://eprint.iacr.org/2026/1326), revision
  2026-07-01, supports the layered target, reuse of a fixed
  \(L_q^\perp(A_D)\) sample pool, weighted score, and the claimed 22/31/41-bit
  improvements over its corrected Qu--Xu comparator. Its theorem is stated
  for uniform unstructured LWE assumptions; it does not prove that the
  layer-wise rank, shortest-vector, independence, and sample conditions hold
  for one block-negacyclic FIPS public key.
- [Hou--Jiang, ePrint 2026/366](https://eprint.iacr.org/2026/366), revision
  2026-03-17, supports the corrected structure-aware rows:
  `C0` 121.9/173.0/237.4, `CC` 139.1/194.7/259.0, and
  `CN` 134.5/188.7/254.1, under the source's success-probability lower bound
  0.3. It also supports the Python-XOR and Ogilvie probability-code
  corrections. These are model-specific estimates, not solves.
- [Li--Zheng, ePrint 2026/1400](https://eprint.iacr.org/2026/1400), approved
  2026-07-12, supports its model-labelled values and modest total gain. The
  paper argues that its normal wrong-score model is conservative at Carrier's
  optimal Kyber parameters while acknowledging heavier wrong-score tails. It
  does not establish conservativeness at every newly selected MS-LSC optimum,
  so the producer was right to keep those minima provisional, although its
  summary should preserve the source's narrower safety argument.
- [Unified Dual Attack Analyses, ePrint
  2026/1048](https://eprint.iacr.org/2026/1048), approved 2026-05-27, supports
  covariance-aware correct-score modelling and an extension of incorrect-score
  tail analysis. It does not independently validate the parameter minima in
  ePrint 2026/1400.
- [Adaptive-LDPC, ePrint
  2026/070](https://eprint.iacr.org/2026/070), approved 2026-01-20, supports
  the 2,950-query ML-KEM-768 result only for a stipulated 95%-accurate oracle.
  Its Apple-M1 evidence is different: 73 of 100 trials ended within Hamming
  distance four, with 6,047.84 average key-recovery measurements over those
  selected successes. It must not be relabelled as unconditional exact-key
  recovery.
- [Quantum rejection sampling, ePrint
  2026/979](https://eprint.iacr.org/2026/979), last revised 2026-05-26,
  supports the quadratic sampler mechanism and the published 9/4/13-bit
  same-parameter deltas. It predates LaMS's corrected Kyber parameterization;
  no checked source gives a corrected and globally reoptimized QRS table.
- [Predicting Module-Lattice Reduction, ePrint
  2025/1904](https://eprint.iacr.org/2025/1904), revision 2026-02-02, states
  that power-of-two cyclotomics satisfy
  \(\lvert\Delta_K\rvert=d^d\) and incur a \(d-1+o(1)\) blocksize loss.
  ML-KEM is therefore the equality boundary, not an instance of the strict
  \(\lvert\Delta_K\rvert<d^d\) speedup condition.
- [CVE-2026-10097](https://nvd.nist.gov/vuln/detail/CVE-2026-10097) supports
  the 1,536-of-1,568-byte AVX2 comparison, wolfSSL 5.7.0--5.9.1 scope,
  output-confirmation precondition, and vendor/CNA-reported roughly 350-query,
  roughly 98% PoC. [PR
  10430](https://github.com/wolfSSL/wolfssl/pull/10430) confirms the final
  32-byte omission, but also fixes AVX2 5-bit decompression. A release-level
  differential is therefore not a clean one-variable comparison.
- [CVE-2026-6330](https://nvd.nist.gov/vuln/detail/CVE-2026-6330) supports the
  half-input ARM64 NEON comparison and wolfSSL 5.7.4--5.9.1 scope, but gives no
  key-recovery query count. [PR
  10192](https://github.com/wolfSSL/wolfssl/pull/10192) folds the upper
  comparison half into the scalar result and adds a tamper/FO-rejection test.
  It is direct prior engineering art for the defensive proposal, and the
  multi-fix PR is not a clean experimental contrast.

## Fatal objections to claims as written

Here “fatal” means fatal to the named synthesis claim, not fatal to every
underlying observation or research direction.

### 1. The score identity does not prove computational equivalence

Equation 25 in the derivation is a valid adjoint Fourier identity, and the
mutual-information identity correctly shows that target orbits are not fresh
samples. Those facts close the proposed information-amplification story and
the naive digit-commutation story. They do not prove that every implementation
of the weighted orbit score has the same operation count, memory traffic, or
preprocessing cost as the closest Wu--Xu/Ogilvie/Hou--Jiang baseline.

The candidate-dependent weights and rotated vectors may share transforms or
other common subexpressions. The producer gives neither a cost-preserving
reduction for all restricted implementations nor matched operation DAGs that
show the weights eliminate every reuse opportunity. Its optional
\(n\leq16\) identity check would test transcription, not this complexity
question.

The narrow negative survives: if total cost is \(S+U\), only \(S\) falls by
four, and \(U\) or new overhead is positive, a full fourfold/two-bit total
reduction is impossible. What remains open is a smaller or differently
structured computational saving.

**Cheapest decisive gate:** freeze one layer, one orbit-stable partition, and
one candidate batch. Construct symbolic operation DAGs for ordinary LaMS,
Wu--Xu rotated-vector reuse, and weighted orbit evaluation. After
common-subexpression elimination, charge vector generation, \(\alpha_i\)
weights, transforms, candidate phases, memory reads, and target updates. Stop
if the orbit DAG has no strictly smaller charged term.

### 2. The oracle taxonomy collapses two independent axes

The producer's single `category` field mixes an algorithm's required access
model with the evidence used to instantiate that access:

- ORS-006 is labelled a conditional algorithmic oracle but reports a physical
  Cortex-M4 full-key recovery;
- ORS-004 combines an iid 95% simulation and a bursty Apple-M1 near-key
  experiment in one row;
- ORS-005 and ORS-009 instantiate PC/DF oracles physically but are labelled
  implementation leakage.

The row-level metrics and caveats can survive. Category-level ranking and
promotion cannot, because an abstract query count and a physical measurement
campaign can appear to be the same evidence class.

**Cheapest decisive gate:** replace the category with two orthogonal fields:
`backend_access_model` and `oracle_instantiation_evidence`. Record query,
trace, profiling, adaptivity, device, exact-key, and protocol-confirmation
fields separately before reranking any row.

### 3. The defensive mutation proposal cannot guarantee complete detection

One end-to-end mutation per byte or SIMD lane is not a complete test of the
comparison primitive. A mutation can change decryption and trigger rejection
through bytes that are still compared even when another byte is ignored.
Scalar and optimized paths may also share the same defect. For
CVE-2026-10097, comparing wolfSSL 5.9.1 with 5.9.2 is additionally confounded
by PR 10430's decompression fix. PR 10192 already contains an FO-tamper
regression, so the proposal's novelty is a coverage extension rather than the
regression concept itself.

The engineering direction remains useful, but the universal-detection
prediction and current positive-control design fail.

**Cheapest decisive gate:** invoke each comparison primitive directly on
equal-length buffers that differ by exactly one bit at every position. Force
and attest AVX2/NEON dispatch, bracket the exact comparison-fix commits, and
use a separately checked scalar oracle. Only after the vulnerable primitive is
detected should one equal-length Algorithm-18 mutation test integration.

## Unresolved source and protocol limits

These issues are not falsifications. They mark claims that the available
record cannot yet settle.

1. **Literature completeness and reproducibility.** Access dates and repository
   commits help, but most paper PDFs lack retained hashes and no search log
   establishes completeness. The only supportable wording is “no checked
   source at the cutoff.”  
   **Gate:** retain PDF SHA-256, ePrint revision, repository commit, search
   strings, and the screened-result list for each claim-moving source.

2. **Li--Zheng minima.** Correct-score expectation checks do not validate the
   family-wise maximum wrong-candidate tail at every minimizing tuple. The
   values remain provisional, not false.  
   **Gate:** at every reported optimum and one frozen success target, compare
   the normal model, conditional Ducas--Pulles/unified-covariance model, and
   Monte Carlo maximum-wrong-score quantiles. Reject a minimum if its normal
   tail is not conservative.

3. **LaMS transfer from LWE to one FIPS key.** Multiplication by \(p^i\)
   preserves the block-negacyclic structure of the flattened public matrix.
   The source's unstructured-LWE rank and lattice heuristics therefore do not
   automatically transfer, and one public key fixes the available samples.  
   **Gate:** prove, or explicitly mark as assumptions, the layer-wise rank,
   determinant/shortest-vector, independence, and sample-count conditions for
   the actual FIPS matrix and passive sample set before more orbit work.

4. **CVE exploitation metrics.** The comparison bugs, affected ranges, and
   patches are well supported. The roughly 350-query/98% figures for
   CVE-2026-10097 are vendor/CNA-reported, and no independent PoC was inspected.
   A remote attack also needs behavior that confirms genuine versus rejection
   keys.  
   **Gate:** reproduce only the primitive omission and one laboratory
   valid-versus-rejection confirmation before considering query-count
   replication.

5. **IDEA-20260722-003 readiness.** The factor-two prediction has no frozen
   protected backend, trace corpus, acquisition count, key/device split,
   decoder versions, success target, or stopping rule. It is falsifiable in
   principle but is not an approved bounded experiment.  
   **Gate:** use one existing time-ordered trace corpus with disjoint keys to
   freeze calibration and replay adapters. Stop before new acquisition if
   held-out calibration or block-bootstrap prediction already misses by more
   than twofold.

## Scoped negatives that survive

1. No checked source supplies an independently verifiable passive full-key
   recovery for ML-KEM-512, ML-KEM-768, or ML-KEM-1024. This is a statement
   about the inspected corpus and cutoff only.
2. Negacyclic target orbits are deterministic transforms, not fresh samples.
   Signed canonical digits need wrap/carry state, and switching adds a public
   cocycle. This does not exclude restricted-algorithm or implementation
   savings.
3. A fourfold reduction of only one cost term cannot yield a fourfold total
   reduction when unaffected cost or overhead is positive. This rejects the
   current vector-only two-bit path, not every reuse factor or end-to-end
   algorithm.
4. FIPS 203 exports no DF/PC bit. A 2,950-call iid-oracle simulation and a
   protocol requiring valid-versus-rejection confirmation are neither passive
   attacks nor ideal-interface attacks.
5. CVE-2026-10097 and CVE-2026-6330 concern named wolfSSL versions and optimized
   backends fixed in 5.9.2. They do not transfer to all libraries, protocols,
   or patched deployments.

## Baselines and end-to-end cost

Pollard rho and BSGS are not relevant comparators for passive ML-KEM key
recovery: the target is MLWE, not generic discrete logarithm in a cyclic group.
The relevant specialized baselines are primal and dual lattice attacks under
explicit cost models.

No fatal cross-model subtraction was found in the producer's cost report. The
corrected structure-aware reference remains:

- `C0`: 121.9/173.0/237.4;
- `CC`: 139.1/194.7/259.0;
- `CN`: 134.5/188.7/254.1.

These model labels are not interchangeable. Li--Zheng minima remain
provisional pending tail validation; RAM, routing, QN/Q0/GE19, source-defined
provable-dual, and physical-resource values remain separate series. There is
still no jointly reproduced lower envelope with one success probability,
score law, CBD treatment, memory convention, and code revision.

For the structure question, the closest comparator is Wu--Xu rotated-vector
reuse plus Ogilvie/Hou--Jiang same-\(A\) hybrid reuse in one operation model.
LaMS's 191/282/390 values may be compared only inside its corrected
QX25/LaMS source family unless a common model is constructed.

For conditional oracles, the comparator is a channel-capacity bound and a
matched PC/DF backend under the same oracle distribution, followed by explicit
trace, profile, and protocol costs. For implementation bugs, the comparator is
FIPS Algorithm 18's scalar behavior against exact vulnerable and fixed
optimized primitives on named commits.

## Survivors and their cheapest gates

- **Corrected Ogilvie/Hou--Jiang family — model-specific estimate.** Seed-fixed
  rerun of all three rows at success lower bound 0.3, with all comparisons
  normalized to the same success target.
- **Li--Zheng MS-LSC — provisional estimate.** Family-wise wrong-tail test at
  every reported optimum before accepting any lower-envelope entry.
- **LaMS p-adic layering — conditional unstructured-LWE mechanism.** Prove or
  declare the structured-matrix and passive sample-cap assumptions before
  spending on orbit experiments.
- **QRS Gaussian sampling — theorem-level mechanism with a stale Kyber table.**
  Apply the LaMS Gaussian-width correction to the fixed published parameters
  and reproduce the comparator before global reoptimization.
- **Adaptive-LDPC backend — conditional oracle algorithm.** Replay time-ordered
  M1 outputs with block resampling and require unconditional exact-key success,
  not Hamming-distance-at-most-four on selected trials.
- **IDEA-20260722-002 — repaired engineering control only.** Run the direct
  one-bit comparison-primitive mutation with forced backend attestation.
- **IDEA-20260722-003 — conditional measurement proposal, not experiment
  ready.** Run a frozen existing-trace preflight on held-out keys and stop
  before physical acquisition if calibration or trace-to-key prediction misses
  by more than twofold.

## Narrow conclusion and next gate

Within the committed BATCH-002 source set, there is no verified passive
standardized-parameter ML-KEM key recovery. Corrected structure-aware
code-based-dual gains are at most 0.8 bit in their source model. The current
fourfold vector-only LaMS-isometry route cannot produce a two-bit end-to-end
gain with positive unaffected cost, and deterministic target orbits add no
Shannon information. The supplied identity does not, however, prove that every
restricted implementation has identical computational cost.

Conditional PC/DF algorithms, physical leakage, and named logic bugs must
remain separate from passive MLWE and from protocol attacks lacking a
confirmation channel. The two wolfSSL defects are credible within their named
version/backend scopes. The first defensive proposal needs a primitive-level
positive control; the second needs a frozen-trace preflight.

The cheapest next action is to repair `IDEA-20260722-002`: run exhaustive
one-bit direct-comparison mutations on exact pre-fix and post-fix AVX2 and NEON
commits with forced backend attestation, then run one equal-length Algorithm-18
integration mutation. Stop if either vulnerable primitive is not detected.
This recommendation is a falsification gate, not an approval, experiment
result, passive attack claim, or official state transition.
