# Red-Team Review: TYPED-TT-TARGET-COMMON-BASIS-PREFLIGHT-V1

## Verdict

Accept as a narrow target-sharing observation. Do not promote it to a fixed-curve attack or ECDLP improvement.

## Objections and responses

1. **Only two targets were tested.** Correct. The equal cut-3 row rank may disappear for larger target batches. A batch-size sweep is required.

2. **The experiment enumerates both target tensors.** Correct. The result measures shared linear-algebra geometry, not a compiler. Source construction and all rank operations are charged diagnostic costs.

3. **Row-union rank alone does not provide a TT factorization.** Correct. A reusable prefix row space must be connected to exact cores, normalization, target specialization, and witness-bearing locator semantics.

4. **The column side grows.** This is the main limiting observation. A target-independent prefix basis may still leave a target-specific suffix operator whose storage or online application dominates.

5. **The chosen targets are not a random batch.** They are the first relation target and first held-out target, selected for reproducibility and direct relation/descent relevance. Fresh random and larger held-out batches are needed before generalizing.

6. **No relation matrix or individual-log path was evaluated.** Correct. The experiment stops at tensor rank geometry and makes no cryptanalytic claim.

## Required follow-up

Test target batch sizes 1, 2, 4, and 8 on fresh curve/factor-base seeds. Construct the shared prefix basis explicitly, charge its fixed-curve storage and bandwidth, and compare target-specialized application against independent exact factorization and the optimized rho baseline.
