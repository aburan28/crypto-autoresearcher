# PQC catalogue static review and protocol holds

This additive correction concerns the 100 unapproved proposals at
`c90520a94ee40dd760d57fe33cc6231ab03a6852`. It records 32 findings affecting 35
prospective experiment contracts. All 100 remain `review_required`,
`frozen: false`, `execution_authorized: false`, `evidence_eligible: false`,
and `approved_by: null`. No scientific trial or official hypothesis transition
is part of this correction.

The original 100 IDEA records, 100 hypothesis records, five drafting arrays,
manifest, session receipts, figures, PDF and empty artifact directories retain
their exact bytes. The unfrozen specifications for the 35 affected entries now
withdraw their procedure, accepted prediction model and verdict criteria from
execution consideration and add item-specific approval blockers. Their remaining
parameter, control and comparison fields are retained as unapproved design
material, not as validated alternatives. The original complete specifications
remain available at the commit above. [Original bindings](original-bindings.json)
identify every one of the 517 original changed paths by SHA-256 and distinguish
preserved bytes from mutable draft specifications and catalogue prose.

[Machine-readable findings](findings.json) bind every correction to catalogue
entry, IDEA, hypothesis and experiment identifiers. A finding classified as a
counterexample or formula error has the exact stated mathematical scope; a
design obligation remains unresolved. This record does not reject entire
research directions or establish security of any scheme. The unlisted 65 entries
retain the original implementation, preapproval, runbook and novelty blockers;
absence from this list is not scientific approval.

## Review and source limits

The review read all 100 canonical proposal/hypothesis/experiment contents, the
five drafting arrays, the generator, both session receipts and all six PDF pages.
The figures show proposal counts only; their data and canonical sources are
unchanged by these design qualifications, so no scientific result plot is
recomputed. The linked original `KN-LIT` records and recalled citations are not
being represented as a fresh full-text review of all external papers. Recalled
references remain pointers and cannot support a load-bearing claim until
retrieved and checked. The Coordinator must establish exact theorem domains,
source support, novelty and complete per-cell protocols before approval.

FIPS 204 specifies the ML-DSA public-key rounding, rejection gates and
SampleInBall byte use underlying entries 25, 28 and 35. See
[FIPS 204, Algorithms 6, 7, 29 and 35 (Power2Round)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf).
FIPS 205 specifies the WOTS checksum, address-domain rules and parameter table
underlying entries 81, 83, 84, 86 and 87. See
[FIPS 205, Algorithm 7, Table 2 and Section 11.2](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf).
The antichain, kernel, moment, support, ratio and memory arguments below are
arithmetic deductions under explicitly stated assumptions, not measured attacks.

## Required resolution before approval

For each affected entry, the Coordinator must reconcile the complete prospective
procedure, parameter cell map, controls, prediction, success/falsification
criteria and decision text against its finding. Preserve original proposal
history and label any revised hypothesis as a new correction or successor under
the repository contract. Bind actual launcher sources, input distributions,
units, per-cell counts, censors, uncertainty methods, artifact paths and runbook
before the existing preapproval gate can pass. No item here grants execution.

Finite failed searches bound only the tested procedure and scope. They cannot
establish infinite work, universal security, impossibility, or a global cost
ceiling. A model prediction remains modeled until an authorized protocol yields
admissible evidence. Source recall and count plots establish neither correctness
nor cryptanalytic utility.

The unresolved design work is tracked in the
[problem record](../../../problems/pqc-catalogue-protocol-contradictions.md).

## Findings by catalogue entry

### Entries 22: Even challenge kernels and invalid random-RHS null

For an even-weight challenge in the degree-n negacyclic ring modulo 2^b (the draft uses power-of-two n), the nonzero vector with every coefficient 2^(b-1) is in its multiplication kernel. Multiple even-weight challenges retain that common ambiguity on the unrestricted coefficient domain; a bounded-secret uniqueness result needs a separate argument. For power-of-two n, an odd-weight challenge is a unit modulo 2 and hence modulo 2^b; more generally this part of the argument requires explicit invertibility. For an invertible challenge every RHS is consistent, so random RHS is not an inconsistency control.

Affected experiments: `EXP-MLDSA-20961f`.

### Entries 23: Condition collision costs on actual accepted-mask equality

A capped attack does not establish infinite recovery cost. Distinct random messages are not guaranteed unique; repeated message and randomizer may intentionally repeat deterministic masks. Missing-key-prefix work must charge accepted-counter search. Under independent usable-pair probability p_same and an h-bit randomizer, the pair approximation is N(N-1)*p_same/2^(h+1), giving birthday scale proportional to sqrt(2^h/p_same), not sqrt(2^h)/p_same. The conditional p_same model must be derived or measured under the actual acceptance process.

Affected experiments: `EXP-MLDSA-b675fd`.

### Entries 25: Sign bytes do not bound the entire challenge image

FIPS 204 Algorithm 29 consumes the first eight bytes for signs and subsequent bytes for positions. Truncating only sign bytes leaves C(256,39) possible supports, whose base-2 logarithm is about 153.7603. A 16-to-32-bit full-image claim requires a different, fully specified seed truncation map. Uniform seed sampling does not imply uniform challenge-image sampling; exact forgery probability requires the induced distribution.

Affected experiments: `EXP-MLDSA-eed16d`.

### Entries 27: Fresh shares retain joint dependence on the secret

Re-randomizing shares preserves their combined secret even when each individual share is uniform. It is not a secret-independent higher-order null. Define a null with independently generated secrets or a specified joint leakage law and verify the claimed independence.

Affected experiments: `EXP-MLDSA-0d773e`.

### Entries 28: Rounded public keys and zero-matrix non-identifiability

ML-DSA publishes rho and t1 after Power2Round with d=13, not the full t. Zero A slots therefore do not directly reveal exact s2 slots from the stated public key. At A=0 the public key is independent of s1, so original-secret recovery by linear algebra is impossible without additional information. Distinguish original-secret identification, equivalent signing capability, and partial information; specify the actual public observation before building hints.

Affected experiments: `EXP-MLDSA-1e2b4d`.

### Entries 30: One faulty transcript gives a fixed-target match

Matching one fixed h-bit randomizer among N independent honest transcripts has probability 1-(1-2^-h)^N. Its constant-success scale is 2^h, not 2^(h/2). Birthday or two-set collision costs require multiple variable targets and an explicitly charged pair model.

Affected experiments: `EXP-MLDSA-0a3ffb`.

### Entries 35: Removing one rejection condition does not remove all gates

A narrower mask can eliminate the z-bound rejection only under its explicit parameter inequality. Low-bit, c*t0 and hint-weight rejection checks remain. Record and analyze each gate and the final accepted-signature law; do not assume every attempt is accepted.

Affected experiments: `EXP-MLDSA-7a6410`.

### Entries 36: Structured covert payloads can be publicly distinguishable

A fixed all-zero k-bit payload forces a public challenge prefix that occurs with probability 2^-k under the honest model. Secret-key knowledge is unnecessary for this distinguisher. Any indistinguishability claim needs an explicit randomized/encrypted payload distribution, receiver protocol, and stated adversarial scope; bounded tests are not a universal proof.

Affected experiments: `EXP-MLDSA-e492e6`.

### Entries 38, 49: Recompute the CRT structure at each ring degree

Complete linear splitting of x^n+1 over F_q requires 2n dividing q-1 in the stated power-of-two cases. Thus n=256,q=257 does not provide 256 base-field slots. Conversely n=64,q=3329 is fully split into 64 linear factors, not 32 quadratic factors copied from n=256. Freeze a valid per-cell CRT map. Entry 49 also needs a separate exact-constraint path for zero hint noise instead of division by a zero standard deviation.

Affected experiments: `EXP-MLDSA-4d3948`, `EXP-MLKEM-0a97f8`.

### Entries 42, 70: Orbit controls must remain in the actual attack lattice

Rotation invariance of a homogeneous module lattice does not establish invariance of a target embedding or its projected block. A coordinate-permuted vector explicitly outside the lattice cannot be inserted as an ordinary sieve control. Specify the exact lattice and projection, certify membership of every injected vector, and test rejected nonmembers separately from valid algorithm comparisons.

Affected experiments: `EXP-MLKEM-e08b88`, `EXP-QLWE-ccd305`.

### Entries 50: Repeated noisy alarms need not multiply the entire search cost

Under the proposed model of deterministic true failure, independent false alarms of probability epsilon, and at most k extra queries per first alarm, the expected query multiplier over F/p base candidates is at most 1+k*(p+(1-p)*epsilon). At p=2^-14, epsilon=0.01, k=6 this is about 1.06036, while the false-confirmed/true ratio is at most (1-p)*epsilon^(k+1)/p. This valid confirmation strategy contradicts the proposed universal hundred-fold lower bound. It is a conditional accounting counterexample, not a measured end-to-end attack cost.

Affected experiments: `EXP-MLKEM-3559f0`.

### Entries 56: Parallel efficiency acts on work, not linearly on an exponent

For serial work T=2^a, t workers and efficiency E, elapsed work units are T/(tE), with logarithm a-log2(t)-log2(E). Aggregate processor work is T/E. Dividing the exponent a by E is not either quantity. Define elapsed, aggregate, and memory units separately.

Affected experiments: `EXP-MLKEM-19e5b7`.

### Entries 60: CBD(2) moments and matched-variance controls

CBD(2) has variance 1, fourth moment 5/2, and excess kurtosis -1/2. Uniform integers from -2 through 2 have variance 2. A matched-variance uniform or discrete-Gaussian control needs an explicitly normalized integer law and its actual moments, rather than reusing unmatched labels or assuming the Gaussian parameter equals realized variance.

Affected experiments: `EXP-MLKEM-62fa28`.

### Entries 64: A finite log-lattice computation is not automatically exact CVP

There is no uniform probability distribution on an unbounded real span. Specify a bounded sampling window or quotient domain. A 200-bit numerical log basis and integer enumeration need certified approximation-error bounds and a comparison margin before they establish exact CVP in the real log lattice. Otherwise label the outcome numerical and keep theorem-domain and exactness questions unresolved.

Affected experiments: `EXP-QLWE-65244f`.

### Entries 65: Planted-relative norms do not certify approximation factors

Because lambda_1 is at most the planted vector norm, output_norm/planted_norm is a lower bound on output_norm/lambda_1, not a certified upper approximation factor. Report the planted-relative ratio separately or supply a certified lower bound on lambda_1. A claim at dimension 256 also requires a theorem actually covering the tested lower dimensions before those cases can falsify it.

Affected experiments: `EXP-QLWE-386499`.

### Entries 66: Module and embedding dimensions need a valid cell map

Dimensions 50 and 70 with module rank 4 do not give integer ring degrees. Specify admissible ring degree/rank and the resulting embedding dimension per cell before execution; do not silently round or drop cells.

Affected experiments: `EXP-QLWE-2fdcf6`.

### Entries 68: The stated dense quantum-state cell exceeds the memory contract

The n=8,q=17 complex128 state alone needs 17^8*16 = 111612119056 bytes, exceeding the 32-GiB memory bound before temporary arrays. The claim that every cell is at most 41^4 amplitudes is false. Resolve the cell/memory contradiction prospectively; a sparse or compressed algorithm requires its own representation and fidelity contract.

Affected experiments: `EXP-QLWE-0221a8`.

### Entries 73: Average and worst-case quantifiers do not supply a numerical radius

An average-case versus worst-case distinction alone proves no quantitative radius separation. Small-dimensional numerical oracle tests cannot establish a general worst-case impossibility theorem. State the actual modeled threshold and retain the missing reduction or bound as an obligation.

Affected experiments: `EXP-QLWE-912f22`.

### Entries 79: Use the correct time-memory slope direction

For slope s=d(log T)/d(log M), the derivative of log(M*T) is 1+s. A prediction s<=-2 contradicts wording that requires s>=-2. Reconcile the direction and limit conclusions to the prespecified interval; a finite interval does not bound all possible memory regimes.

Affected experiments: `EXP-MLKEM-b702be`.

### Entries 81, 83: WOTS checksum antichain and minimum reachable chain index

For base-w message digits b, checksum C=sum(w-1-b_i). If a different b' dominates b componentwise then C'<C, so the full message-plus-checksum encoding cannot also dominate componentwise. The full encoding is an antichain. Identical encodings caused by a message-digest collision are a separate case. For several disclosed chain values, the minimum index per chain determines forward reachability, not the maximum. Entry 83 also uses h=8,d=3 with nonintegral layer height and d=2 makes layer 0 and layer d-2 identical; its comparison grid needs correction.

Affected experiments: `EXP-SLHDSA-9d3ed1`, `EXP-SLHDSA-e9b016`.

### Entries 84: Address headroom and reachable-domain coverage

Repeated use of the same logical ADRS is not an encoding collision: exhibit distinct logical addresses with identical encoded bytes. Key generation builds the top XMSS root; a finite signature sample does not enumerate every reachable tree address. FIPS 205 Table 2 gives bottom-tree widths 63 bits for 128f and 64 bits for 256f in the 8-byte field, so their headrooms are 1 and 0 bits rather than at least 8. Zero headroom within the field capacity does not itself imply a vulnerability. Freeze the reachable-domain enumeration and validate any claimed cross-type collision on the complete retained type byte.

Affected experiments: `EXP-SLHDSA-8ada4e`.

### Entries 85: One million trials cannot resolve a 64-bit collision probability

Outputs of 8 and 12 bytes mean 64 and 96 bits. One million independent attempts at probability 2^-64 have expected hits about 5.42e-14. Zero hits cannot estimate that probability within a factor of two or support a collision-slope fit; its one-sided 95% binomial upper bound is about 2.996e-6. Report the bounded mutation coverage and a valid interval. Changing output truncation would require an explicitly revised prospective protocol.

Affected experiments: `EXP-SLHDSA-e67a2b`.

### Entries 86: Shared public seeds do not erase hash address domains

The full function domain includes the public seed, address type, chain and index, and hash role. Sharing a public seed alone does not place all chain values into one common target function. Partition targets by the complete tweak domain and independently verify candidate relations under the actual function before using a multi-target cost model.

Affected experiments: `EXP-SLHDSA-8f310d`.

### Entries 87: Interior skips differ from valid chain-prefix truncation

If an interior iteration is skipped while the address counter advances, the next hash uses a different domain; the result need not equal a valid earlier chain value. A prefix-truncation fault is a different model. Specify fault position and counter behavior and verify the resulting chain index before applying the lower-index recovery argument.

Affected experiments: `EXP-SLHDSA-a6c6d8`.

### Entries 89: The stated second-preimage ratio has the wrong threshold

Under the draft's own expressions the MD/sponge ratio is 2^(c-n)/blocks. At c=32,n=24 and blocks=64 it is 4, not at most 1/16; at blocks=8 it is 32. The crossover is n>c-log2(blocks), not n>c/2. Charge expandable-message preparation and compare the best available generic direct attack. Truncated SHAKE is not itself the block-cipher permutation required for a Davies-Meyer construction; define the concrete compression function.

Affected experiments: `EXP-SLHDSA-5c7662`.

### Entries 90: Cache detection needs valid dimensions and trusted initialization

h=9,d=4 has nonintegral layer height. The top-L cache size is a geometric sum and is zero at L=0, unlike the stated largest-term expression. Detection also needs trusted cache initialization and defined misses; storing the first faulty value cannot detect that first use. Freeze valid cells and the trusted-cache fault model.

Affected experiments: `EXP-SLHDSA-37c329`.

### Entries 91: A proof upper bound is not an exact attack frequency

Security-proof upper-bound terms are not exact conditional probabilities for an arbitrary selected forger. A measured frequency below a bound does not justify deleting the bound term. Define the reduction/extraction event and its inequality direction before interpreting the empirical comparison.

Affected experiments: `EXP-SLHDSA-316fdd`.

### Entries 92: Changing an exact weight can destroy importance-sampling support

A nominal law supported on exact weight w and a proposal supported only on higher exact weights are disjoint. Then the nominal measure is not absolutely continuous with respect to the proposal, and likelihood-ratio importance sampling cannot estimate the nominal expectation. Require positive proposal mass everywhere on nominal support, exact normalized P/Q weights, a justified range or tail bound, and separate pilot/evaluation data before claiming finite confidence intervals.

Affected experiments: `EXP-HQC-f546f2`.

### Entries 94: Permuting whole key labels preserves a DFR-tail statistic

Relabeling whole keys leaves the multiset of per-key failure rates and its p99/median ratio unchanged. It is not a null for key-dependent heterogeneity. Specify a valid outcome-level exchangeability or conditional null and retain dependence on the corrected importance-sampling support contract.

Affected experiments: `EXP-HQC-b6e6db`.

### Entries 96: ISD algorithm and preprocessing grids omit named comparisons

The variable ledger lists Stern and MMT but the claim includes Dumer; its 2^10 and 2^18 levels omit the 2^14 A/A cell. An eight-bit gap does not resolve a crossover within one doubling without a specified interpolation model. Reconcile the algorithm set, A/A cell and comparison resolution before approval.

Affected experiments: `EXP-HQC-c048de`.

### Entries 98: The circuit-depth comparison names an absent cell

C2 requires depth 2^64 while the independent levels list only 2^40 and 2^96. Reconcile the prospective comparison and full cell map before approval.

Affected experiments: `EXP-HQC-afc485`.

### Entries 100: Calibration verdict and algorithm scope disagree

The contract lists Stern and BJMM while its claim covers Prange, Stern, Dumer and BJMM. A negative offset exceeding five bits cannot be described as calibration within three bits. Reconcile the algorithm scope and positive/negative decision text before approval.

Affected experiments: `EXP-HQC-465cc3`.

## Deterministic regression evidence

`python3 docs/reviews/pr2404/test_counterexamples.py -v` checks 19 fixed
arithmetic regression cases. They include exhaustive small encoding/kernel
fixtures and exact rational calculations. They do not implement the proposed
cryptanalytic experiments, run solvers, sample attack trials, or estimate attack
performance. The suite passing establishes only these finite arithmetic checks;
the written general arguments and unresolved design obligations have their own
scope.
