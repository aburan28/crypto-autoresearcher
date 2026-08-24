# Arm-A successor repair design

This package is a new immutable successor to `EXP-ECDLP-e8ef62`. The prior
package and its fresh `TASK-20260809-f6873c` NO-GO report remain unchanged.
This task creates no implementation, run, or empirical evidence.

## Closure map for the fresh review

| Finding | Concrete repair |
|---|---|
| `REV-f6873c-01` exact paired sign-permutation gate | v5 defines exact reduced rational `r_i=W_FULL_i/W_CONTROL_i`, `d_i=log(r_i)` for sign/order only, the lower 18th of 36 exact Walsh geometric means as the effect estimator, exact tie/zero rules, integer doubled midranks, `T2`, bit-ordered `k=0..255` sign vectors, inclusive two-sided tail, exact `p_numerator/256`, and the equivalent integer gate `p_numerator <= 6` for both FULL/NEG and FULL/BASE. `comparison.json` must emit and the validator must recompute the complete 256-row table. |
| `REV-f6873c-02` incomplete baseline certificate fixture | v5 freezes the coefficient-group equation `R(a,b)=(a+37b) mod 101`, the initial residue, all three before/after transition residues, and every expected negation coefficient/residue transform. The fixture explicitly rejects curve-point inference and accepts only exact coefficient-group outputs. |
| `REV-f6873c-NB-01` calibration attempt prose | v5 states the inclusive attempt index interval `[0,255]`, its count of 256, and terminal failure after index 255. |

The successor remains finite toy-scale and carries no exponent or
cryptographic-scale claim. The next gate is the exact snapshot followed by a
fresh independent `review-adversarial` session.
