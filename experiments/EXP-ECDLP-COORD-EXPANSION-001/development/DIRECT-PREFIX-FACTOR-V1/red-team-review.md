# Independent Red-Team Review

## Handoff: Independent red-team of DIRECT-PREFIX-FACTOR-V1

### Claim or task

Audit whether the evidence justifies an exact 48/24-coordinate direct factor
theorem with four-scalar target specialization and honest attack accounting.

### Status

`OBSERVATION`, with a valid algebraic proof sketch. The artifact does not
independently certify the full `RESTRICTED THEOREM` or accounting gate.

### Assumptions

- five inputs and cuts 2/3;
- smooth short-Weierstrass curves over `F_p`, `p>3`;
- frozen left-associated 40-gate RCB circuit;
- canonical affine projective lifts;
- raw RCB projective gauge;
- materialized suffix tables and `B=Theta(q^0.2)`.

### Evidence so far

- Artifact hashes match source commit `f4cec496`.
- The quotient is a free `F_p[Y,Z]` module with basis `{1,X,X^2}` because
  the cubic is monic in `X`. Its degree-`d` piece has dimension `3d`, giving
  48 and 24 for degrees 16 and 8.
- The four-component target identity is algebraically correct.
- All 2,223,216 shared-implementation comparisons agree.
- A separate spot audit of the 12 planted tuples found nonzero projective
  outputs and agreement with affine summation, but this is not enforced by
  the official result.

### Failure modes

1. The verifier imports and reruns the producer; it is deterministic replay,
   not an independent polynomial, RCB, rank, or locator verifier.
2. Zero-set checks can pass vacuously because witness counts and planted
   indices are not recorded or enforced.
3. The one symbolic/numerical RCB control omits infinity, doubling, inverse
   pairs, repeated points, and independent affine addition.
4. Advice construction avoids the tensor, but exhaustive validation
   enumerates all `A B^4` pairs and retains two flattened full-surface arrays.
5. Polynomial operations, compiler/validation timing, specialization
   additions, reads/writes, traffic, prefix storage, deep bytes, and live
   field slots are absent.
6. Full sampled `U/V` ranks are narrower than intrinsic predicate rank,
   relation rank, or descent. The small cut-2 `U` side is row-capped.
7. Rescaled projective targets and infinity are untested.
8. Payload and work exponents are distinct resources.
9. Vectors are computed and hashed, not emitted as reusable artifacts.

### Next concrete action

Run `GAUGE-INVARIANT-DIRECT-FACTOR-V2` with:

- an independently implemented RCB and CAS normal form;
- recorded planted hits, affine sums, witness counts, and nonzero-projective
  checks;
- infinity, doubling, inverse-pair, repeated-point, rescaled-target, and
  mutation controls;
- left-associated, suffix-first, alternate-parenthesized, permuted, and
  randomly rescaled representations;
- streamed validation digests;
- separate compiler, specialization, validation, memory, and traffic
  accounting;
- at least three seeds per size.

Falsify representation-invariant rank if affine sums and zero masks agree but
ranks or factor dimensions differ.

### Artifact paths

- `development/DIRECT-PREFIX-FACTOR-V1/contract.md`
- `development/DIRECT-PREFIX-FACTOR-V1/raw-result.json`
- `development/DIRECT-PREFIX-FACTOR-V1/verification.json`
- `src/direct_prefix_factor.py`
- `src/verify_direct_prefix_factor.py`
