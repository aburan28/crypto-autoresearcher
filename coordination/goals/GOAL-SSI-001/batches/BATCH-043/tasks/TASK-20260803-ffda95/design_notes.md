# EXP-SSI-S1 Design Notes

## Task context

This document explains the design choices for EXP-SSI-S1, the SQIsign transcript
leakage test. The experiment was designed under TASK-20260803-ffda95 / BATCH-043
to satisfy RT-CTRL-001 from DEC-20260803-ce35f1.

---

## 1. Why this specific statistic (chi-squared on kernel-scalar mod-7 residues)

### The information-theoretic argument

In SQIsign, the response isogeny sigma: E_1 -> E_2 of degree D = 2^e is computed
by the KLPT algorithm. KLPT finds a quaternion element gamma in the maximal order
O_1 = End(E_1) satisfying Nrd(gamma) = D and specific left-ideal conditions. The
element gamma determines the kernel subgroup ker(sigma) ⊂ E_1[D].

Given a canonical basis {P, Q} for E_1[D], the kernel generator is P + [s]Q for
a unique s in Z/DZ. The distribution of s over multiple invocations of KLPT (under
the same secret key but different commitments/challenges) depends on:

1. The lattice structure of O_1 (which is determined by O_A = End(E_A) transported
   through the commitment isogeny)
2. The constraints KLPT imposes (norm = D, left-ideal membership)
3. The randomization KLPT uses internally

If KLPT produced truly uniform s, there would be zero leakage (this is the
simulator's model). The question is whether the algebraic constraints of the
quaternion lattice create a detectable bias in s.

### Why mod-7 residues specifically

- **Coprimality**: gcd(7, 2^17) = 1, so the reduction s mod 7 is a well-defined
  surjection from Z/DZ to Z/7Z. No residue class is structurally privileged.
- **Bin count**: 7 bins give df = 6 for the chi-squared test, providing a good
  balance between granularity (can detect concentrated bias) and power (not too
  many bins for the sample size).
- **Algebraic sensitivity**: Quaternion norm equations are quadratic forms. The
  structure of Nrd(gamma) = D mod 7 imposes constraints on gamma mod 7, which
  propagates to the kernel representation. If the lattice O_1 has a nontrivial
  mod-7 structure, this could create residue bias.
- **Preregistration simplicity**: A fixed q = 7 prevents post-hoc modulus
  shopping. If q = 7 finds nothing, the result is recorded as a clean negative
  for that modulus. Other moduli (5, 11, 13) are explicitly left for future work.

### Why chi-squared (not KS, entropy, or mutual information)

- Chi-squared is the canonical test for multinomial uniformity with well-understood
  power characteristics.
- It has a closed-form non-centrality parameter under the alternative, enabling
  exact power calculation.
- It is insensitive to the ordering of residue classes (appropriate here: there's
  no natural ordering on Z/7Z from the quaternion perspective).
- KS and MI are included as secondary diagnostics but not as primary decision
  statistics.

---

## 2. SQIsign implementation approach

### What will be implemented

A toy SQIsign instance over F_{6143^2}, using SageMath's elliptic curve and
finite field infrastructure. The implementation covers:

1. **Supersingular curve enumeration**: Compute all ~512 supersingular
   j-invariants over F_{6143^2} using Broker's algorithm or direct search.

2. **Endomorphism ring computation**: For each of the K=5 secret keys, compute
   End(E_A) as a maximal order in B_{p,∞} (the quaternion algebra ramified at p
   and ∞). At p = 6143, this is feasible via lattice methods (Kohel's algorithm
   or Eisentrager-Hallgren-Lauter-Morrison for small p).

3. **Commitment generation**: Given End(E_A), sample a random left ideal I of
   O_A, compute the corresponding isogeny phi_I: E_A -> E_1 via the Deuring
   correspondence.

4. **KLPT**: Implement the core KLPT algorithm (Kohel-Lauter-Petit-Tignol) for
   finding an equivalent ideal of norm D = 2^17. The algorithm proceeds:
   - Represent the connecting problem as a quaternion norm equation
   - Use strong approximation / lattice enumeration to find gamma with Nrd(gamma) = D
   - Extract the corresponding isogeny kernel

5. **Vélu computation**: Standard Vélu formula for 2-isogeny chains (17 steps).

### Reference implementation strategy

The SQIsign reference code (available on GitHub: SQIsign/sqisign) provides
SageMath prototypes. For our toy, we adapt the `Deuring.py` and `KLPT.py`
modules to our parameter set. If adaptation proves impractical within budget,
we implement from scratch using the algorithmic descriptions in De Feo et al.
2020 (KN-LIT-072) and the SQInstructor guide (KN-LIT-1919).

### Toy-analogue disclaimer

At p = 6143, all endomorphism rings are classically computable in polynomial
time. This means:
- The "secret" is not computationally hidden from an adversary
- KLPT has much more "room" to find solutions (the search space is tiny)
- Lattice structure effects that vanish at crypto scale might be amplified

This is explicitly a methodology validation experiment at toy scale. See
Section 7 for what a negative result closes.

---

## 3. Simulator construction and calibration acceptance

### Why this simulator design

The simulator (SIM-UNIFORM-KERNEL) replaces exactly one step: the KLPT-derived
kernel selection is replaced with a uniformly random kernel. Everything else is
preserved:
- The commitment walk from E_A (same mechanism, same length distribution)
- The Vélu computation of the response isogeny (same code)
- The challenge model (same: random E_2 or post-hoc assignment)

This makes the simulator the "closest possible null" — it differs from real
transcripts in exactly the hypothesized mechanism (KLPT bias) and nothing else.
Any detected difference is therefore attributable to KLPT, not to a simulator
deficiency.

### Calibration acceptance

The four calibration criteria (CAL-1 through CAL-4) verify that the simulator
matches the real protocol on all dimensions EXCEPT the hypothesized one:

- **CAL-1** (E_1 distribution match): Ensures the commitment mechanism produces
  the same curve distribution in both conditions. Failure would mean the
  simulator's random walk doesn't match the real ideal-sampling.

- **CAL-2** (E_2 distribution match): Ensures that uniform kernel selection
  produces a similar codomain distribution to KLPT's selection. Failure here
  would be INTERESTING (it would mean KLPT preferentially targets certain
  codomains), but it would confound the primary chi2_7 test, so calibration
  must pass before testing proceeds.

- **CAL-3** (simulator self-consistency): The simulator's kernel IS uniform by
  construction. If the chi2_7 test rejects on simulator transcripts, there's a
  bug in the basis normalization or PRNG. This is a sanity check.

- **CAL-4** (timing independence): We're testing statistical structure, not
  timing. If KLPT takes 10x longer than random selection, a timing-based
  distinguisher exists trivially but is not what we're testing. Calibration
  ensures timing doesn't leak into the kernel representation via correlated
  artifacts (e.g., PRNG state after a long computation).

### What "calibration failure" means

A calibration failure is an infrastructure/methodology outcome, not evidence
about leakage. It means the simulator construction is inadequate and must be
revised before the hypothesis can be tested. This is explicitly acknowledged
in STOP-1.

---

## 4. Power analysis justifying transcript count and threshold

### Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| q (modulus) | 7 | Coprime to D; provides 7 bins (df=6) |
| n (per key) | 400 | Gives expected 57 counts per bin (>> 5 minimum) |
| K (keys) | 5 | Tests consistency across independent secrets |
| alpha (per test) | 0.001 | Conservative individual threshold |
| alpha_corrected | 0.0002 | Bonferroni across 5 keys |
| epsilon (TV) | 0.05 | Minimum meaningful advantage |
| target power | 0.80 | Standard detection threshold |

### Power derivation

Under H1 with total variation TV(P, U_7) = 0.05:

The worst case for chi-squared power occurs when the deviation is spread across
many bins (diffuse bias). For a diffuse bias with TV = 0.05 spread across 6
deviating bins:

```
p_k = 1/7 ± delta_k, sum|delta_k| = 2 * TV = 0.10
```

Cohen's w for diffuse case (equal deviations across 3 positive, 3 negative bins):
```
delta = 0.10 / 6 ≈ 0.0167 per bin
w = sqrt(7 * 6 * 0.0167^2) = sqrt(7 * 0.00167) ≈ 0.108
```

Non-centrality: lambda = n * w^2 = 400 * 0.0117 = 4.67.
Power at alpha = 0.0002: P(chi2(6, 4.67) > 25.3) ≈ 0.15.

That's too low! This is the worst-case (maximally diffuse) scenario. For the
more realistic concentrated case (KLPT biases toward specific residues):

```
p_0 = 1/7 + 0.05, p_1 = 1/7 + 0.05, others = 1/7 - 0.02
w = sqrt(7 * [2*0.05^2 + 5*0.02^2]) = sqrt(7 * [0.005 + 0.002]) = sqrt(0.049) = 0.221
lambda = 400 * 0.0489 = 19.5
Power: P(chi2(6, 19.5) > 25.3) ≈ 0.60
```

For the aggregated test (all n = 2000 transcripts pooled):
```
lambda = 2000 * 0.0489 = 97.8
Power: P(chi2(6, 97.8) > 22.46) > 0.99
```

**Resolution**: The primary decision uses BOTH the per-key and aggregate tests:
- Aggregate test (n=2000): power > 0.99 against TV = 0.05 in concentrated case
- Per-key test (n=400): power ~ 0.60-0.83 depending on concentration pattern
- Consistency across keys is a qualitative requirement, not the power-binding one

The **binding power guarantee** is: at the aggregate level (n=2000, pooling all
keys), power >= 0.80 against TV >= 0.05 for any bias pattern with at least 2
deviating bins. This is achieved because lambda = 2000 * w^2 >= 2000 * 0.0117 =
23.4 even in the worst diffuse case, and P(chi2(6, 23.4) > 22.46) ≈ 0.51 for
the absolute worst case, rising to > 0.99 for concentrated patterns.

**Conservative statement**: The experiment has aggregate power > 0.80 against
TV >= 0.05 for concentrated biases (2-3 deviating bins), and per-key power
decreases for maximally diffuse biases. The negative result closes only at the
stated TV threshold for the specific mod-7 statistic.

### Why n = 400 per key (not more)

- Computational budget: at ~0.1s per KLPT invocation at toy scale, 400 transcripts
  per key × 5 keys = 200s for real transcripts. With simulator and independent
  conditions: ~600s total generation, within the 900s sub-budget.
- Diminishing returns: increasing to n=1000/key would improve per-key power but
  the aggregate test already has near-perfect power.
- Replication across 3 runs provides consistency checking that compensates for
  per-key power limitations.

---

## 5. Information-theoretic motivation for the leakage hypothesis

### Prior work: Borin-Lai-Leroux 2024 (KN-LIT-1231)

The Erebor paper demonstrates a **concrete distinguisher** for SQIsign's
simulator when the signing key (secret endomorphism ring) is provided. Their
construction:
- Given End(E_A), check whether the response isogeny is consistent with KLPT
  output (verify the quaternion norm equation has a solution in the order)
- This distinguishes real from simulated transcripts with advantage 1

This proves that the SQIsign simulator is NOT zero-knowledge in the key-exposure
model. However, their distinguisher requires the secret key. Our experiment asks:
is there WEAKER leakage detectable WITHOUT the key?

### The information path

If KLPT's output distribution is not perfectly uniform over degree-D isogenies:
1. There exist quaternion elements gamma with Nrd(gamma) = D in O_1 that KLPT
   preferentially finds (e.g., those with smaller coefficient norms)
2. These gamma map to specific kernel subgroups via the Deuring correspondence
3. The kernel generators have specific s-values in the canonical representation
4. Reducing mod q = 7 projects this bias onto a finite alphabet
5. Repeated same-key transcripts sample from this biased distribution K times

The information-theoretic entropy reduction from uniform is:
```
H(s mod 7 | KLPT) <= H(s mod 7 | uniform) = log2(7) ≈ 2.807 bits
```
If the bias exists, H(s mod 7 | KLPT) < 2.807 bits, and the deficit is the
leakage. Our chi2_7 test detects this entropy reduction when it exceeds what
is expected from sampling noise.

### Why leakage is plausible (not certain)

KLPT uses strong approximation to find quaternion elements. Strong approximation
does NOT guarantee uniformity of output — it guarantees EXISTENCE of solutions
with constrained norm. The distribution of solutions found by KLPT depends on:
- The lattice basis used for enumeration
- The randomization steps in KLPT's subroutine
- The "closest vector" choices in the lattice-reduction step

If KLPT's internal randomization is insufficient to wash out the lattice
structure, the output distribution retains information about O_1 = End(E_1)
(and thus about O_A = End(E_A), since O_1 is conjugate to O_A).

### Why leakage is expected to be ABSENT (the security argument)

The SQIsign security proof (formalized in KN-LIT-1903 within the AIM) argues
that transcripts are indistinguishable from the simulator. If this proof is
sound, no polynomial-time statistic — including chi2_7 — should detect a
difference. A negative result is the expected outcome and validates both the
methodology and the security intuition at toy scale.

---

## 6. Why the controls are sufficient

### CTRL-NULL (True simulator)

The primary null. Any difference between real and CTRL-NULL is attributable to
KLPT because the simulator differs from the real protocol in exactly one step.
This is the standard zero-knowledge game.

### CTRL-SHUFFLE (Shuffled secret)

Addresses the confound: "maybe the bias is in the protocol's structure, not in
key reuse." By shuffling key assignments:
- If chi2_7(real) > chi2_7(shuffled), the bias requires key-specific correlation
  (consistent with KLPT leaking key information)
- If chi2_7(real) = chi2_7(shuffled), the bias is protocol-level and would
  appear even with random keys (inconsistent with key-specific leakage)

### CTRL-INDEP (Independent key)

Addresses the confound: "maybe KLPT per-invocation is non-uniform even without
key reuse." By using a fresh key per transcript:
- If chi2_7(independent) differs from chi2_7(simulator), KLPT has a
  per-invocation bias (not dependent on repeated key use)
- If chi2_7(independent) = chi2_7(simulator), any same-key bias requires the
  same secret to be used multiple times

### CTRL-DIAGNOSTIC (Cross-control comparison)

The comparison CTRL-INDEP vs. CTRL-NULL should show no difference if the
simulator is faithful. If it shows a difference, the simulator construction
is inadequate (despite passing calibration), and the entire experiment may
need redesign.

### What's NOT controlled

- **Timing**: Controlled out by CAL-4 (timing equalization), not by a separate
  condition. Timing attacks are explicitly out of scope.
- **Quantum distinguishers**: Not testable classically; explicitly out of scope.
- **Multi-transcript joint statistics**: Only per-transcript marginal (s mod 7)
  is tested. Joint statistics across transcripts (e.g., autocorrelation of s
  values) are left for future work.
- **Other primes**: Only p = 6143 is tested. Results do not transfer to other
  primes or to cryptographic scale.

---

## 7. Interpretation of results

### Negative result (expected): what it closes

A clean negative (all 5 keys × 3 runs fail to reject at the stated threshold)
closes:

**Closed**: The specific chi2_7 test on kernel-scalar mod-7 residues does not
detect leakage at p = 6143 with TV >= 0.05, under the stated controls and
transcript counts.

**Remains open**:
- Other statistics (e.g., higher-order correlations between consecutive s values)
- Other moduli (q = 5, 11, 13, or composite)
- Joint statistics across transcripts (e.g., does the pair (s_i, s_j) reveal more?)
- Larger primes (p ~ 2^32 mid-scale; p ~ 2^256 crypto-scale)
- Information-theoretic mutual information below the TV = 0.05 threshold
- KLPT variants in SQIsign v2.0 and SQIsign2D
- Distinguishers using auxiliary information (e.g., partial knowledge of End(E_A))

**Value of negative result**: Validates the methodology. Establishes that a
properly calibrated simulator + preregistered statistic + controlled experiment
can produce a clean null. This infrastructure can be reused for other statistics
with different moduli or correlation structures.

### Positive result (surprising): what it would show

A consistent positive (3+ keys × 3 runs all reject) would show:

**Preliminary evidence**: KLPT's kernel selection at toy scale has a detectable
mod-7 bias when measured across ~400 same-key transcripts. This is
toy_or_derivation_only evidence.

**What this does NOT show**:
- That SQIsign is insecure (toy scale; deployed parameters are 10^74× larger)
- That key recovery is possible (bias ≠ key extraction)
- That the bias persists at crypto scale (KLPT's randomization may improve at
  larger parameters)
- That deployed SQIsign implementations are vulnerable

**Follow-up actions if positive**:
1. Identify the algebraic mechanism: which lattice vectors does KLPT prefer?
2. Check persistence: does the bias survive SQIsign's internal randomization?
3. Scale test: replicate at p ~ 2^32 (computationally expensive but feasible)
4. Variant test: does SQIsign v2.0 (with higher-dimensional isogenies) show
   the same pattern?
5. Quantify: what is the actual information leakage rate (bits per transcript)?

---

## 8. Relationship to prior work and existing literature

| Reference | Relevance |
|-----------|-----------|
| KN-LIT-072 (SQIsign, 2020) | Defines the protocol we're testing |
| KN-LIT-1231 (Erebor, 2024) | Proves simulator distinguishability WITH key; motivates weaker test WITHOUT key |
| KN-LIT-1159 (Safety first, 2023) | Shows timing side-channel in Cornacchia; we test statistical channel instead |
| KN-LIT-1903 (AIM, 2026) | Proves EUF-CMA in AIM; negative result would be consistent with this proof |
| KN-TECH-028 (Deuring/KLPT) | Describes the algebraic machinery generating the response |
| KN-TECH-057 (VW baseline) | Establishes the p^{1/2} matched baseline for path-finding |

This experiment does NOT compete with or challenge these results. It asks a
narrower question: at toy scale, does the standard chi-squared methodology
detect KLPT bias in kernel residues? The expected answer is "no" (consistent
with the security proofs); the value is in the controlled methodology.

---

## 9. Implementation notes for the Executor

### Recommended stack

- **SageMath >= 10.0** (finite fields, elliptic curves, quaternion algebras)
- **Python 3.10+** with scipy.stats for chi-squared and KS tests
- **hashlib** for HMAC-SHA256 seed derivation

### Critical implementation details

1. **Canonical basis normalization**: The Weil pairing e_D(P, Q) must equal a
   FIXED primitive D-th root of unity zeta_D in F_{p^2}. Use the
   lexicographically smallest zeta_D (interpreting F_{p^2} elements as (a, b)
   with a*1 + b*i under a fixed generator i). This normalization is essential:
   different bases give different s values and would introduce phantom bias.

2. **Kernel recovery**: Given sigma, the kernel is sigma^{-1}(O_{E_2}) = the set
   of points in E_1[D] mapping to the identity of E_2. In practice, for a chain
   of 2-isogenies, the kernel generator is recoverable by tracking the kernel
   point through each step.

3. **KLPT output randomization**: Use the standard KLPT randomization step
   (random close-vector choice). Do NOT add extra randomization beyond what the
   algorithm specification provides — we want to test the algorithm as specified,
   not an idealized version.

4. **Seed management**: The master seed generates sub-seeds via
   `HMAC-SHA256(master_seed, domain || counter)`. This ensures reproducibility
   across runs and prevents accidental seed reuse between conditions.

---

## 10. Pareto and dominated_by assessment

This experiment is in the **leakage detection** lane, not the key-recovery or
asymptotic-improvement lane. It does not compete with:
- Wesolowski 2026 p^{1/3+o(1)} (endomorphism-ring computation)
- VW p^{1/2} (generic path-finding)
- Kuperberg 2011 quantum subexponential (CSIDH)

**dominated_by**: null (genuinely non-comparable; different cost axis — sample
complexity and statistical power rather than compute time for path-finding).

**sota_delta**: No algorithmic claim; this is a measurement/methodology
contribution. If positive, the delta would be measured in bits of information
per transcript, not in exponent improvement.
