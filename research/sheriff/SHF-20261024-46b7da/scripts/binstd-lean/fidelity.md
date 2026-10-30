# BINSTD B3 source-to-statement checks

Source revision: `4647b1d072ffaebbbb85127bdc60343bbd372ec4`.
Formal tree identity: `0dd2764cff0c0ec05c4938f12b334ec60376d9ff` on published main and preflight checkout. This note was written after first reading the source and theorem, before reading any root scratch notes or prior sheriff cases.

Prior: expect a valid conditional arithmetic theorem with possible prose broadening to empirical yield.

## a. Statement

The theorem quantifies over natural `targets`, `tauHits`, and `openHits`. Its conclusion is `4*tauHits < 5*openHits`, under `targets > 0`, `openHits = targets`, and `tauHits <= targets`. For positive open hits this is the exact rational inequality `tauHits/openHits < 5/4`. It proves no observed count.

## b. Hypotheses

The premises are jointly satisfiable: `targets=40`, `openHits=40`, `tauHits=40`. Lean checked this witness and the resulting `160 < 200`.

## c. Definitions

The theorem has no self-defined notions. `run.py` counts Boolean `m3_decomposes` hits over `target_count` targets for each arm, then divides both counts by the same target count. When open hits are positive, its `R_tau/R_open` is the count ratio. No Lean definition claims to formalize the EC runner.

## d. Data

The matrices contain four triples `(tau, open, targets)`: `(16,40,40)`, `(40,40,40)`, `(20,40,40)`, `(40,40,40)`. Their exact ratios are `2/5`, `1`, `1/2`, `1`; each is below `5/4`. Matrix digests match the run `raw-result.json` references. This checks recorded bytes and arithmetic, not independent execution.

## e. Scope

The finding explicitly limits itself to toy `n=17`, dimensions 8 and 9, two seeds, Stage 1, frozen `exhaustive_fb_sum_m3_stdlib_gf2`, and observed open saturation. It says Lean does not certify the runner or archived counts, retains `empirical_only`, and denies larger-field or attack claims.

## Secondary target

The `x17_factorization` theorem states exactly the product of the three archived bitmask polynomials in `(ZMod 2)[X]`. Independent carryless multiplication of `[3,313,471]` gives `131073 = (1<<17)|1`. The target notes correctly exclude irreducibility, Frobenius identification, and invariant-subspace classification.
