# Red-Team Review: TYPED-TT-SOURCE-AWARE-SKELETON-PREFLIGHT-V1

## Verdict

Accept as a strong but scoped toy representation result. Do not promote it to a fixed-curve cryptanalytic attack.

## Objections and responses

1. **The exact rank budget is imported from a prior enumerative oracle.** Correct. The constructor is favorable because it knows when to stop. An adaptive rank-discovery rule must be tested and charged.

2. **The prefix order succeeds because the tensors are generic at these toy sizes.** Correct. The first rank-many prefixes happened to span the needed row space. Fresh curves, factor bases, and adversarial order controls are required.

3. **Full validation still evaluates every tensor entry.** Correct and explicitly separated. Validation proves exactness; it is not construction cost. The receipt must not quote the construction ratio as an end-to-end attack ratio.

4. **The construction uses a direct affine oracle, not the actual RCB circuit.** Correct. A circuit-native implementation must prove that the same selected fibers and basis operations can be obtained from the projective addition-law circuit with complete field-operation accounting.

5. **The target-specialization saving is a constant-factor cut-3 matrix saving.** Correct. It may be overwhelmed by relation density, sparse linear algebra, target descent, or persistent advice. No exponent claim follows.

6. **No relation witnesses are recovered by the skeleton itself.** Correct. The current result only reconstructs locator values; relation rank and individual-log correctness remain untested.

## Required follow-up

Run fresh-seed adaptive rank discovery, retain the exact skeleton as a reusable operator, and integrate it with the typed relation/descent verifier. Report fixed-curve offline operations, retained advice, memory bandwidth, supported targets, success probability, relation rank, and online work alongside a matched rho baseline.
