# Falsification review: IDEA-20260722-001

Task: `TASK-20260722-204`  
Goal/batch: `GOAL-MLKEM-001` / `BATCH-001`  
Reviewed snapshot: `f94da7203a708fd33fc0e7791f8247134d260143`

## Verdict

The ring identity at the base of the proposal is sound: in
\(R_q=\mathbb Z_q[X]/(X^n+1)\), multiplication by \(X^j\) is a signed
coefficient permutation, commutes with an MLWE matrix over the commutative
ring, and exactly preserves ML-KEM's iid symmetric centered-binomial public-key
secret and error distributions.

That identity does not support the proposed interpretation or cost claim. The
present novelty screen misses close covariance prior art, the random signed
permutation comparator is not a valid same-\(A\) MLWE control, effective
covariance rank is not a measure of distinguishing information, 30 seeds cannot
calibrate the required wrong-candidate tails, and the LaMS layer transition is
not defined under negacyclic signs and p-adic carries. A reduction in consumed
score vectors also does not imply a reduction in the dominant
BKZ-plus-sieving cost.

The candidate is therefore blocked as a novelty or fully charged two-bit
claim. It remains worth one cheaper exact algebraic falsification at \(n=8\);
passing that gate would justify only a calibrated toy scoring experiment.

## Snapshot and source integrity

The producer artifacts were read from the Coordinator-committed snapshot, not
accepted from working-tree-only state. Commit `f94da72` is reachable at `HEAD`
with parent `4fc43e8`. The committed hashes match the archive binding:

- `baseline_map.md`:
  `e09a9597316322f051124776e0c1418de38ac93c46dd0beeab1f9d9ba02a0f1f`
- `candidate_report.yaml`:
  `ddb15db841901c2c8b8ed23385db9486a8b6418322f11df4768f59234fd98217`
- `snapshot-receipt.json`:
  `ab88cf9cb83102c80fc1eea272a3efe1ae37592bb756d1ec4a374dd5c9cc4a6d`

The receipt's internal `commit_sha` is null by its self-reference-avoidance
design; the dispatch archive binds it to `f94da72`, and Git independently
verifies the parent, paths, and hashes.

Primary sources independently inspected included FIPS 203 and ePrints
2022/1661, 2026/279, 2023/1850, 2023/1238, 2026/1048, and 2026/1400. The LaMS
landing record and abstract for ePrint 2026/1326 were recovered, but its full
proof, parameter tables, and linked estimator code were not recoverable in this
review channel. That is a source-verification limit, not evidence that LaMS is
invalid.

## Fatal objections

### 1. The orbit mechanism is already represented by rotated-vector prior art

Let \(M(A)\) be the flattened block-negacyclic matrix and \(J_j\) the signed
orthogonal matrix for multiplication by \(X^j\). Ring commutativity gives

\[
J_jM(A)=M(A)J_j.
\]

For every score vector \(v\),

\[
\langle v,J_jb\rangle=\langle J_j^Tv,b\rangle.
\]

Thus evaluating one vector against a target orbit is the adjoint
representation of evaluating the corresponding rotated-vector orbit against
one target. Wu and Xu, ePrint 2022/1661, already construct \(n-1\) additional
equal-norm rotated short vectors from one reduced vector and use all of them in
the distinguisher. Ogilvie, ePrint 2026/279, already proves that coefficient
isometries produce same-\(A\) targets compatible with one expensive hybrid
preprocessing.

The exact LaMS-plus-GLS composition was not located. That narrow fact does not
make the orbit mechanism novel. At most, the candidate is an incremental
composition of known orbit generation, standard cyclic-correlation batching,
LaMS, and covariance-aware scoring.

The literature screen also omitted two directly relevant sources available
before the stated cutoff:

- Bashiri and Wiemers, ePrint 2023/1238 / JMC 2025, explicitly analyze
  covariance and refute score independence.
- Li and Zheng, ePrint 2026/1048, approved 2026-05-27, give covariance-based
  score prediction for the original, modulus-switched, and decoded dual
  attacks, including tail behavior.

This is fatal to a novelty claim, not to the possibility of a small engineering
or estimator refinement.

### 2. The random signed permutation control breaks the relation

The proposal requires the true negacyclic orbit to retain one projected bit
more gain than size-matched random signed permutations. This comparator is not
a matched MLWE attack.

An arbitrary signed permutation \(P\) generally does not commute with the
flattened matrix:

\[
PM(A)\ne M(A)P.
\]

Consequently, from \(b=M(A)s+e\), it does not follow that
\(Pb=M(A)Ps+Pe\). Applying \(P\) jointly to \(A\) restores a relation but
changes the matrix and destroys the same-\(A\) preprocessing premise. A
true-orbit advantage over an invalid transform mainly detects the known
commuting symmetry; it cannot measure additional information or generic
batching gain.

Every proposed \(P\) should first undergo an exact commutator test. A
noncommuting \(P\) can be retained only as an intentionally broken negative
control. Matched controls are:

1. valid monomial rotations with correct versus shuffled candidate alignment;
2. an equal-norm pool of independently sampled short vectors;
3. ablations that hold the vector pool fixed and separately enable rotation,
   covariance weighting, convolution, and LaMS.

### 3. Effective covariance rank is not the relevant attack statistic

The proposed

\[
r_{\rm eff}=\frac{(\operatorname{tr}\Sigma)^2}
                  {\operatorname{tr}(\Sigma^2)}
\]

describes eigenvalue spread. It does not measure separation between correct
and wrong candidates. Under a linear Gaussian model with common covariance,
the relevant squared separation is

\[
(\mu_1-\mu_0)^T\Sigma^{-1}(\mu_1-\mu_0).
\]

GLS weights proportional to \(\Sigma^{-1}\mathbf 1\) are justified only after
showing that the signal is a common mean in the \(\mathbf 1\) direction.
Orbit scores need not have that mean orientation, correct and wrong
covariances need not agree, and the FFT maximum over candidates is nonlinear.
A high effective rank can coexist with no usable separation; a low effective
rank can contain the entire signal direction.

The sample plan is also internally inadequate. With 30 seeds split into
training and held-out sets, a centered training covariance has rank at most
\(n_{\rm train}-1\). A feature set of up to 32 orbit scores is therefore
singular if all 30 seeds are used for training and more underdetermined after a
real holdout. Orbit-subset search over the same small sample adds severe
selection bias. Matrix inversion, subset choice, and the reported effective
rank would be unstable without a predeclared subset, shrinkage, condition
diagnostics, and key-and-vector-pool holdout.

This is fatal to the current rank gate and fourfold-vector interpretation. It
does not preclude a regularized likelihood score tested on genuinely held-out
keys and vector pools.

### 4. Thirty seeds cannot validate the wrong-candidate tail

The attack must reject exponentially many wrong candidates, not merely
separate 30 correct and 30 uniformly chosen wrong examples. The operational
false-positive probability is the tail after:

- reuse of one target and one short-vector pool;
- dependence across orbit scores;
- dependence among related candidate guesses;
- maximum over FFT candidates;
- data-driven orbit-subset selection;
- repetition across p-adic layers and retries.

Ducas-Pulles show that target norm is a confounder and that the old
independence heuristic underestimates important tails. Bashiri-Wiemers compute
nonzero covariance and further explain why uncorrelated is not independent.
Li-Zheng 2026/1048 extend covariance and tail prediction to LWE dual variants.
The orbit fixes the target norm exactly while sharing the complete target,
which removes no obligation to model the remaining deterministic dependence.

Thirty seeds can reveal a gross failure but cannot resolve a cryptographic
tail. An exhaustive wrong-candidate distribution at a smaller dimension,
followed by an analytic or validated rare-event model, is required. A binomial
confidence interval over 30 arbitrary wrong guesses is not a substitute.

### 5. LaMS composition and full source recovery are unspecified

The candidate does not state:

- the small prime \(p\);
- the p-adic digit convention for centered negative coefficients;
- the exact orbit score at a layer;
- the transformed candidate-coordinate map;
- the target update after a recovered digit;
- how a wrong early digit propagates into later layers;
- the final reconstruction and residual certificate.

Negacyclic rotations include sign changes. P-adic expansion is not equivariant
under coefficientwise sign without carries or borrows. For the cheapest
concrete mutation, take \(q=3329\), \(p=2\), and a centered secret coefficient
\(-1\). Its residue is 3328, whose binary digit path is not the digitwise
signed path of \(+1\). A carry-aware map may exist after conditioning on all
earlier recovered digits, but it must be derived and tested at every layer.

The proposed one-layer experiment cannot establish that the layer update
commutes with isometry, that all orbit candidates remain aligned, or that the
complete secret is recovered after early-layer errors and retries. It can only
falsify a necessary local scoring property.

This is a missing proof and representation test, not an impossibility result.

### 6. The full-cost claim does not follow from score or vector counts

A fourfold decrease in vectors consumed by a score is not automatically a
fourfold decrease in attack time:

- one BKZ-plus-sieve execution already emits a large list;
- list production and reduction parameters may not change when fewer entries
  are consumed;
- ePrint 2026/1400 reports that short-vector sampling dominates even after
  reducing FFT and decoding subcosts by several bits;
- convolution batches raw cyclic correlations, but modulus switching,
  decoding, candidate maximization, p-adic updates, retries, and verification
  remain;
- at \(n=32\) or a selected orbit of size at most 32, a transform may be slower
  than an optimized direct correlation;
- covariance training and subset search are per-model or per-key costs that
  have not been assigned.

The total must be recomputed as a sum of costs and only then converted to
\(\log_2\), with all attack parameters reoptimized. Subtracting two bits from
a local term is invalid when another term dominates.

The requested model is also ambiguous. Ogilvie's reported `CC` model is not a
memory-routing or physical-resource model. Counting bytes moved and peak RSS
for the candidate does not make those costs comparable to `CC` unless the same
architecture and routing conversion is applied to every baseline. Conversely,
dropping memory traffic violates the proposal's own "fully charged" language.

Finally, the snapshot provides no absolute ordinary-LaMS `CC` costs, no
concrete \(p\), no layer/partition parameters, and no executable estimator for
the claimed lower-of-two threshold. The two-bit claim is therefore not
currently testable, much less supported.

## Uncertainties, not impossibility findings

- A correctly regularized likelihood score may extract useful computational
  discrimination from orbit-generated vectors after covariance and tail
  correction.
- A carry-aware p-adic candidate map may make every LaMS target update
  equivariant under negacyclic signs; the current snapshot neither derives nor
  refutes such a map.
- Convolution exactly batches raw cyclic correlations, but the fraction of
  complete modulus-switching, decoding, threshold, and verification work it
  can amortize is unknown.
- Per-key covariance and a predeclared orbit subset may or may not remain
  stable from \(n\in\{32,64\}\) to \(n=256\). Toy success cannot resolve this.
- Incomplete recovery of the full LaMS paper and estimator prevents an
  independent absolute-cost comparison. This is a verification limit, not
  negative evidence about LaMS.

## Sample accounting and oracle boundary

The passive public-key object provides one fixed MLWE key relation. For module
rank \(k\), this is \(k\) ring equations or \(kn\) flattened coefficient
equations. The \(n\) target rotations are deterministic invertible transforms
of those equations. They are not fresh samples and cannot be credited as
additional independent public data.

Separate synthetic keys are legitimate experimental replicates for estimating
average behavior, but they are not samples available while attacking one key.
Covariance training across keys also requires evidence that the learned model
transfers to a new \(A\) and independently generated short-vector pool.

The candidate correctly excludes decapsulation, failure, timing, power, hint,
plaintext-checking, and trace oracles. Any use of such information would move
the result outside this review. Public parsing and expansion of \(A\) from its
seed must still be charged.

## Baseline comparison

Pollard-rho and baby-step/giant-step are generic-group discrete-log algorithms.
They are not applicable to MLWE and must not be presented as ML-KEM baselines.
The generic cryptanalytic control here is a matched progressive-BKZ primal
attack.

The relevant specialized figures, retained in their source models, are:

| Attack | ML-KEM-512 `CC` | ML-KEM-768 `CC` | ML-KEM-1024 `CC` | Relevance |
|---|---:|---:|---:|---|
| Ogilvie IsometricDualHybrid | 137.1 | 192.7 | 257.2 | Closest same-\(A\) isometry/preprocessing baseline |
| Carrier code-based dual hybrid | 139.5 | 195.1 | 259.7 | Corrected score/decoding baseline |
| Li-Zheng MS+LSC | 139.20 | 194.02 | 259.40 | Closest modulus-switching composition; sampling dominates |

Wu-Xu 2022 is the closest mechanism comparator for obtaining \(n\) score
vectors from one reduced vector. Its near-orthogonality/independence cost
analysis cannot be imported without the later covariance and tail corrections.

Ogilvie's 2.4/2.4/2.5-bit `CC` gains already consume the main isometry benefit.
The candidate must show a non-overlapping gain against the optimized
isometric baseline, not add Wu-Xu, Ogilvie, and LaMS deltas. It must also
reoptimize the baseline with the same success target, public-key sample cap,
reduction and sieve implementation, list size, false-positive rule, memory
semantics, and final verification. Core-SVP, `CC`, `CN`, memory-routing,
quantum, and physical-resource numbers are not interchangeable.

## Required discriminating controls

1. **Exact carry-and-layer gate.** At \(n\in\{8,16\}\), use exact integer
   arithmetic, an explicit \(p\), and secrets containing \(-1,0,+1\). Verify
   every scalar orbit score against convolution, every target update and carry,
   complete reconstruction, and the final residual.
2. **Commutator-labelled controls.** Check \(PM-MP\) exactly for every
   permutation. Treat noncommuting transforms only as broken negatives. Use
   valid aligned/shuffled isometries and independent equal-norm short vectors
   as matched controls.
3. **Frozen statistical model.** Freeze orbit subset, covariance estimator,
   shrinkage, and threshold on training keys and vector pools. Hold out both
   keys and independently generated pools. Report covariance condition number,
   weight stability, and sensitivity to regularization.
4. **Exhaustive null at tiny dimension.** Enumerate all wrong candidates,
   including the maximum and selection procedure, and compare the complete
   tail with Ducas-Pulles, Bashiri-Wiemers, and Li-Zheng 2026/1048 models.
5. **Sample ledger.** Record exactly \(kn\) public coefficient equations per
   attacked key and label all orbit targets as deterministic transforms.
6. **Composition ablation.** Test rotation-only, covariance-only, LaMS-only,
   convolution-only, and full composition under identical inputs.
7. **One full-cost implementation.** Reoptimize primal, Carrier/Li-Zheng,
   Ogilvie, ordinary LaMS, and the candidate together. Charge reduction,
   sieving, list production, transforms, training, subset search, layers,
   retries, memory in one declared model, candidate verification, and final
   reconstruction.

## Cheapest counterexample and next action

Do not begin with the proposed \(n=32\) covariance fit.

Use \(n=8\), \(q=3329\), \(p=2\), one exact short vector, and a secret
containing \(-1\). Enumerate all eight monomial rotations and all p-adic
layers. Check:

1. \(J_jM=MJ_j\);
2. direct and convolution score equality;
3. carry-aware candidate alignment after every target update;
4. complete secret reconstruction and residual verification;
5. nonzero commutator for one fixed arbitrary random signed permutation.

Any score, carry, update, or reconstruction mismatch rejects the current
composition; a commuting random permutation invalidates the chosen mutation
and requires another draw. Passing proves only algebraic consistency and earns
the exhaustive-null/calibrated-score test. It does not establish novelty,
scaling, or a cost gain.

## Narrowest supported conclusion

The committed snapshot supports an exact ring symmetry and a cheap
falsification question. It does not support a new orbit attack, independent
samples, a fourfold useful-vector reduction, covariance-calibrated false
positives, complete LaMS source recovery, or a two-bit standardized-parameter
improvement. Failure of the exact toy gate would reject only this
representation and composition; it would not rule out all covariance-aware or
isometry-aware MLWE attacks.
