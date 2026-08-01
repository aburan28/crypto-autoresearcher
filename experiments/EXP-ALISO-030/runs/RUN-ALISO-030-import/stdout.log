# Experiment Contract: Exponent-Three Nilpotent Lift Consensus V10

Date: 2026-07-18

## Hypothesis

`HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND`: the target-separated projective
lift-consensus construction accepted in V8 extends from exponent two to the
registered ordinary exponent-three fixture. At each divided-orientation level,
the reconstructed matrix on `E[ell]` is nonzero, rank one, and square-zero; one
projective class maps to zero and the remaining `ell` classes yield one common
base-rational ascending kernel independently of identity, swap, and shear basis
changes.

No family, exact field-operation, performance, asymptotic, Kani, target-descent,
SCALLOP, ECDLP, novelty, deployment, or cryptographic-parameter claim is
permitted.

## Null hypothesis

The exponent-three fixture falsifies or narrows the implementation if any third
level fails exact projective consensus, if an under-divided orientation is
accepted, if target-free substitution cannot be reconstructed over the complete
two-step prefix, or if the withheld degree-27 path/composite does not match.

## Versioned evidence and negatives

- V1 through V7 remain preserved as `ISO-AR-NR-070` through
  `ISO-AR-NR-076`; none may be overwritten or promoted.
- V8 is accepted only for its exact degree-25 and degree-9 exponent-two
  fixtures. Its result/verification/postrun SHA-256 are
  `81dad6a33c976d9fe9145351b22d9b5be56d4efebb870ae034cf3bdc63aca0d7`,
  `72954743b53544eaf12b597c16125a79ee9c34cd02c6812d10b1ffc16500e8f3`,
  and `fe5ff8bc68e52203af9d7c872d7386f83141b05bcafc59fac848b548c6088503`.
  V8 must never be rerun or used as V10 output authority.
- V9 failed closed in its first development process at the producer-side
  constructor-semantics gate before any result was serialized. Its exact source
  hashes, command, and exception are preserved in
  `iso_ascending_prime_power_consensus_v9_development_failure.md`. V9 must not
  be edited, rerun, or promoted; V10 owns the diagnosis and repair.
- The older broad toy sweep is fixture-discovery evidence, not V10 acceptance
  authority. It recorded the `p=577` kernel ladder `x+197`, `x+255`, `x+41`
  and exact degree-27 composite, but V10 must reconstruct all arithmetic and
  verify the withheld path under its own split authority.

## Registered fixtures

V10 contains the two accepted V8 fixtures as regression controls and adds one
exponent-three fixture:

1. `F_1721`, `y^2=x^3+x+29`, order `1725`, trace `-3`, Frobenius
   discriminant `-6875=25^2*(-11)`, `ell=5`, exponent `2`, expected
   companion/measured degree sequences `[5,25]` and `[5,5]`.
2. `F_163`, `y^2=x^3+2x+2`, order `162`, trace `2`, Frobenius
   discriminant `-648=9^2*(-8)`, `ell=3`, exponent `2`, expected
   companion/measured degree sequences `[3,9]` and `[3,3]`.
3. `F_577`, `y^2=x^3+2x+1`, order `589`, trace `-11`, Frobenius
   discriminant `-2187=27^2*(-3)`, `ell=3`, exponent `3`, expected
   companion/measured degree sequences `[6,18,54]` and `[6,6,6]`.

The companion sequence is an upper bound computed in the non-saturated
`Z[pi]` model. The measured sequence is separately certified from full-order
torsion bases, full Weil-pairing order, and direct Frobenius action on each
current curve. V9 incorrectly identified the upper bounds with the measured
degrees for the exponent-three fixture; V10 keeps the two quantities distinct.

The verifier-owned fundamental discriminants are respectively `-11`, `-8`,
and `-3`. They and every class-polynomial/target-path object are instantiated
only after all three constructor outputs and pre-verifier map seals exist.

## Construction model

The constructor receives only source curve/Frobenius data, `ell`, exponent, and
registered field-degree authorities. It does not receive a target curve,
fundamental discriminant, secret edge/path, verifier callback, class polynomial,
or target `j`.

For step `r`, enumerate the `ell+1` projective classes of lifts in
`E_r[ell^(r+1)]`, project them to `E_r[ell]`, evaluate the original
Frobenius-imaginary orientation divided by `ell^r`, and re-derive all primitive
image/pairing/descent gates. Repeat under identity, swap, and both shear basis
transforms. A correct step requires:

- one nonzero rank-one square-zero `2x2` matrix over `F_ell`;
- exactly one zero projective image per transform;
- exactly `ell` accepted images per transform;
- one monic base-rational kernel polynomial shared by every accepted image and
  every transform;
- exact degree-`ell` quotient and full map seal;
- zero construction oracle calls and no target/secret-path use.

## Arbitrary-prefix substitution

Let the accepted steps be `phi_0,...,phi_(e-1)`. Define the final-step prefix

`Phi_prefix = phi_(e-2) o ... o phi_0`.

On the domain of `phi_(e-1)`, enumerate local degree-`ell` edges, remove the
accepted final-step kernel, and select the lexicographically first remaining
kernel. The target-free substitute is

`psi o Phi_prefix`,

not `psi o phi_0` unless `e=2`. The constructor report binds prefix length,
prefix degree, prefix source/codomain, all prefix step seals, accepted and
selected final kernels, selected edge seal, complete substitute seal, degree
and trace checks, and `target_or_class_polynomial_used_for_selection=false`.

Producer and standalone verifier independently reconstruct the complete prefix
from serialized kernel polynomials. A deliberately truncated-prefix control
must fail for the exponent-three fixture.

## Wrong-division controls

For every later step `r>0`, rerun lift enumeration using division power `r-1`.
V10 therefore requires one control on each exponent-two fixture and two controls
on the exponent-three fixture. Every such control must reconstruct:

- the exact zero `2x2` orientation matrix;
- `ell+1` zero images and zero accepted images under every basis transform;
- no surviving kernel polynomial;
- exact `ConsensusFailure: exact projective-lift consensus gate failed` before
  isogeny construction;
- zero target/oracle/secret-edge use.

The report is an ordered list keyed by correct and attempted division powers.
Missing, duplicated, reordered, or truncated controls reject.

## Withheld verifier

Only after construction is frozen, enumerate all rational length-`e`
degree-`ell` paths and select endpoints whose `j` is a root of the registered
Hilbert class polynomial. Require exactly one selected path, one exact commuting
transport per step, and exact composite rational-map agreement under exactly
one target automorphism. For the `D=-3` endpoint, enumerate all target
automorphisms; do not assume the generic two-automorphism case.

The target-free substitute must fail both the class-polynomial-root test and
the exact-map gate.

## Source and serialization custody

- Main executes only exact already-hashed constructor source bytes via
  `compile` plus `exec`; pathname loaders and bytecode-cache reads are forbidden.
- Fixed Sage seed `20260718` is initialized before any constructor arithmetic.
- Canonical/pretty JSON uses `allow_nan=false`. The standalone parser rejects
  duplicate keys, literal non-finite constants, and finite-token overflow before
  semantics, then recursively enforces finite values.
- Every digest has a canonical materialized preimage that the standalone
  verifier recomputes. Untouched JSON must need no type repair and no producer
  helper.
- Retained live maps are resealed after withheld verification. A verifier-side
  final-map replacement must change the fresh seal and reject.

## Semantic mutation controls

All V8 semantic mutations remain mandatory for every fixture:

1. identity orientation rows with stale nilpotent claims;
2. per-step target use;
3. per-step oracle use;
4. parent construction success false;
5. all field degrees changed consistently to one;
6. fabricated self-consistent preconditions;
7. degree-999 forged map seals with refreshed self-hashes;
8. altered verifier/path discriminants;
9. unbound substitution kernel;
10. valid-format wrong x-coordinate hash;
11. valid-format wrong transport hash.

V10 adds two exponent/prefix controls:

12. truncate the ordered wrong-division control list;
13. replace the complete-prefix substitution seal with a truncated-prefix seal.

All `13/13` must reject on all three fixtures. For exponent-two fixtures the
truncated-prefix mutation drops the sole prefix step; for exponent three it
uses only `phi_0` instead of `phi_1 o phi_0`.

## Metrics and logging

Record exact command, UTC timestamps, Git HEAD, initialized seed, Python/Sage
versions, frozen source hashes at start/end, companion and directly measured
torsion degrees, all projective/matrix evidence, ordered wrong-level controls,
prefix and map seals, withheld path/map facts, semantic mutation outcomes, wall
clock, and raw macOS RSS bytes. Exact low-level field operations remain `null`.

## Positive control

Both V8 fixtures must reproduce their accepted timing-free semantic facts under
the V10 schema. The `p=577` fixture must recover degree `27`, endpoint `j=0`, and
the three-step kernel ladder independently before verifier authority exists.

## Negative control

Every under-division control and the target-free complete-prefix substitute must
reject. The truncated-prefix mutation must demonstrate that a seal of a map with
the right final local edge but the wrong prefix cannot authorize success.

## Success criterion

All three registered cases pass construction, exact map reconstruction, delayed
verifier creation, withheld path/composite agreement, substitute rejection,
live post-verifier custody, and `13/13` semantic mutation rejection. Three fresh
development processes emit one timing-free semantic core and each untouched
artifact passes the standalone verifier. Independent prelaunch review must find
no P0/P1 before a canonical run is considered.

## Falsification criterion

Any failed gate narrows this implementation or fixture/model claim. It does not
rule out ascending-isogeny recovery generally. Preserve the failed V10 artifact
and repair only under V10; never overwrite or promote it.

## Proof and disproof tracks

Proof track: formalize the local multiplier-ring statement that the correctly
divided orientation is nonzero square-zero rank one at every level and that its
image is the conductor-ideal kernel.

Disproof track: search exponent-three/class-number-above-one fixtures for a
non-unique withheld path, a non-rank-one matrix, basis-dependent kernel output,
or a prefix substitution that accidentally reaches the target.

## Reproduction command

No V10 execution is authorized by this contract alone. After implementation,
exact source hashes, three fresh development runs, standalone verification,
adversarial controls, and independent prelaunch review must be supplied before
any one-shot canonical command is written.
