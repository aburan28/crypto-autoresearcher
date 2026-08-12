# Independent Red-Team Review

## Handoff: Red-team ELLIPTIC-NET-BLOCK-ZERO-V1

### Claim or task

Determine whether `L=8B`, the controls, canonicalization, verifier, and cost
accounting justify a recurrence negative for exact block-zero location.

### Status

`NEGATIVE RESULT`, `REVISE INTERPRETATION`.

V1 supports a narrow negative for the frozen raw RCB-projective locator. It
does not support a representation-invariant negative for the canonical zero
set or elliptic-net methods.

### Assumptions

- toy curves `q in {953,3919,15583}`, one seed, `B in {5,8,10}`;
- identical four `R` slots and witness existence rather than ordered
  multiplicity;
- one fixed RCB addition order and raw projective gauge;
- short means homogeneous linear order at most `2B` or the fitted raw
  two-parameter Somos-4 form;
- reported bytes are logical packed payload, not resident memory.

### Evidence so far

- All 12 progression roots and matched random roots have BM order `L/2`.
- `L=8B` falsifies an observed-prefix recurrence of order at most `2B`, but
  does not prove asymptotic growth.
- The same-code deterministic verifier exactly reproduces the result.
- On the first random-x curve, all 24 permutations of tuple `(0,1,2,3)`
  produce one affine point sequence and one zero mask but 24 distinct raw
  locator-value sequences.

The locator is homogeneous of degree two in the projective RCB output.
Rescaling by nonzero `lambda_i` multiplies values by `lambda_i^2` without
changing zeros. Projective gauge can therefore manufacture or destroy a
scalar recurrence while preserving the cryptanalytic predicate.

### Failure modes

1. The raw recurrence negative is not projective-gauge invariant.
2. Rank-one EDS/Somos is a functional fitter control, not a matched
   translated rank-two-net control.
3. The verifier imports and reruns the producer rather than independently
   reconstructing canonical tuples, products, BM/Somos claims, and descents.
4. Equality of separately minimal BM polynomials is weaker than solving for
   a common bounded-order annihilator.
5. Canonical tuples preserve zero support, but not raw values or ordered
   multiplicity.
6. Packed tree bytes omit live multi-target state, Python overhead, memory
   traffic, and `Theta(N L^2)` recurrence-analysis work.
7. Three coupled size points and one seed do not support asymptotic language.

### Next concrete action

Run `GAUGE-INVARIANT-BLOCK-ZERO-V2`:

- evaluate all distinct tuple permutations and alternate parenthesizations;
- recover projective scales and verify affine points and zero masks;
- compare raw, intrinsic or scale-stripped, and randomly rescaled sequences;
- sweep `L in {8B,16B,32B}` and at least three curve seeds;
- solve a joint order-at-most-`2B` Toeplitz system across targets and
  siblings;
- independently reconstruct results without importing producer code;
- report shared build, target specialization, unique live field slots, deep
  bytes, memory traffic, and recurrence-analysis operations separately.

If recurrence classification changes under nonzero rescaling while the zero
set is fixed, retain V1 only as a representation-specific negative. If the
intrinsic sequence also has order above `2B` on the longer seeded sweep, the
negative becomes materially stronger.

### Artifact paths

- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/contract.md`
- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/raw-result.json`
- `development/ELLIPTIC-NET-BLOCK-ZERO-V1/verification.json`
- `src/elliptic_net_block_zero.py`
