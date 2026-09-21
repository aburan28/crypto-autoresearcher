---
id: KN-TECH-048
type: technique
title: Decryption-failure attacks and failure boosting
tags: [decryption-failure, failure-boosting, failure-oracle, cca, kem, lwe, lwr, ring-lwe, module-lwe, ml-kem, query-budget, multi-target, lattice]
confidence: reported
complexity: adversary effort is the cost of finding a failing ciphertext (failure rate times boosting gain) times the number of failures needed; for conservatively parameterised NIST candidates the required query count is reported above practical limits
applicability: IND-CCA lattice KEMs with nonzero decryption failure probability; requires an oracle that reveals decryption success or failure
source_refs: [KN-LIT-119, KN-LIT-118, KN-LIT-080, KN-LIT-055, KN-TECH-022]
added: 2026-07-24
superseded_by: null
---

## Method
Lattice KEMs have a small but nonzero probability that decryption fails. Each
failure leaks information about the secret, because a failing ciphertext is
evidence that the noise term correlated with the secret in a particular
direction. The attack has three stages (KN-LIT-119):

1. **Failure boosting.** Do not wait for a random failure; search offline for
   ciphertexts whose failure probability is elevated, trading precomputation for
   a higher effective failure rate.
2. **Obtain failures.** The minimal effort depends on the adversary model -- the
   paper analyses a quantum adversary, a multi-target adversary, and one limited
   in oracle queries.
3. **Exploit them.** Quantify the information each failing ciphertext carries and
   accumulate it; KN-LIT-118 provides the machinery for folding that information
   into a lattice attack as hints (KN-TECH-047).

## What the result actually says
Schemes with relatively high failure rates lose significant security. For the
NIST candidates assessed, the required number of oracle queries is **above
practical limits**, because of those schemes' conservative parameter choices.
That negative conclusion is the operative one for anything targeting deployed
ML-KEM.

This is the chain that gives failure-rate work its security meaning, and it is
the missing link for the repository's ML-KEM line. EXP-MLKEM-001 examined
failure-probability *modelling* -- exact marginals against a pinned estimator --
and closed at `supported_within_toy_boundary` without transferring to FIPS 203
rates. The rule this entry fixes: **a revised failure rate is not an attack.**
To become one it must be carried through boosting gain, an adversary model, a
query budget, and an information-accumulation argument, and for conservative
parameters the published analysis says the query budget is where it dies.

## Applicability limits
The attack needs a failure oracle, so it is a CCA-setting result and does not
apply to ephemeral or CPA usage. Analyses are per-scheme, depending on the exact
noise distribution, compression, and failure rate; a bound for one parameter set
does not transfer. Multi-target and quantum variants change the arithmetic and
must be stated. Later refinements in this line (directional failures,
multi-ciphertext accumulation) are not covered by this entry.

## Verified vs reported
Failure boosting, the three adversary models, the information-quantification
step, and the explicit statement that NIST candidates' query requirements exceed
practical limits are reported from KN-LIT-119's abstract; nothing was
reproduced. The connection to the repository's own ML-KEM experiment and the
"a revised failure rate is not an attack" rule are this program's reasoning,
consistent with but not stated by the source.
