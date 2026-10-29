# J2 independent mathematical review

**Verdict: holds for the two scoped mathematical claims.** No arithmetic
counterexample was found. The archived-runner interpretation remains a separate
formal obligation. This report does not supply a fresh Lean build or kernel audit.

Producer: PR #2484 at exact commit
`976b82bf60afda5e3d31c0da2704604ea2f2e5a5`. Reviewer: J2, Conductor T-609.
Owned joint: `J2-blind-arithmetic-and-concrete-bridge`.

## Blind provenance

The first filesystem read was `../../blind-statements.json`. Before the seal,
the reviewer read only that mathematical input and its own script/output;
Conductor/tool metadata and parent messages about the claim and output location
contained no producer derivation. The blind stage did not inspect producer
files, receipts, PR text, git history, the review plan, input manifest, or sibling
reports. The calculation used Python 3.9.25 and its standard library, with
independently written carryless arithmetic and binary elimination.

The seal was written at **2026-10-27T22:07:34.000201+00:00**. Its five hashes
were subsequently rechecked unchanged. Artifacts:

- [Independent derivation](blind-derivation.md)
- [Exact calculation source](blind-calculate.py)
- [Raw JSON output](blind-output.json)
- [Commands and operational outcome record](blind-commands.txt)
- [Pre-unblinding seal](blind-seal.json)

The initial artifacts were mistakenly created at the worktree's `reports/J2/`;
the parent clarified the assigned nested directory and they were moved before
sealing. A patch attempted before the move completed failed to find its path;
after collecting that move's successful result, the patch and calculation
succeeded. No mathematical control failed unexpectedly. No sibling report was
read at any stage. After sealing, a broad producer-tree text search also exposed
matching lines from older BINSTD analyses and review records; these are fully
listed in the attestation and were not inputs to the blind derivation.

## Exact findings

| Object | Independent result | Method |
| --- | --- | --- |
| Factors 313 and 471 | Product is `1+X+...+X^16`; each is irreducible | Carryless convolution; Rabin criterion; all 30 monic trial divisors through degree 4 |
| Factors 3, 313, 471 | Product is `X^17+1`, mask 131073 | Exact polynomial multiplication |
| Canonical GF(2^17) Frobenius | Exact order 17; minimal polynomial `T^17+1` | Finite-field exponent law; root bound for linearized polynomials |
| Modulus 131081 | `X^17+X^3+1` is irreducible | Rabin criterion; all 510 monic trial divisors through degree 8 |
| Independently defined quotient Frobenius | Rank 17, exact order 17, minimal polynomial mask 131073 | Full 17 by 17 binary matrix arithmetic |
| Quotient orbits | `x` spans dimension 16; `x+1` spans dimension 17 | Exact 17-element orbit lists and elimination |
| Polynomial kernels | Dimensions 1,8,8, invariant and direct-sum rank 17 | Explicit kernel bases, matrix evaluations and elimination |
| Negative control `X^8+1` | Reducible; Frobenius rank 4, minpoly `T^4+T^3` | Both irreducibility checks reject; matrix computation |
| Negative control GF(2) | Frobenius order 1 and minpoly `T+1`, although `F^17=I` | Direct one-dimensional construction |

The canonical minimal-polynomial proof does not infer the answer merely from
order 17. An annihilating `q(T)` of degree `d<17` would give a nonzero
polynomial `sum c_i Z^(2^i)` of degree at most 65536 vanishing at all 131072
field elements. The field root bound excludes that. Since `T^17+1` annihilates
Frobenius, it is the minimal polynomial. The complete proof and every theorem
relied on are stated in the sealed derivation.

The explicit quotient matrix columns are
`[1,4,16,64,256,1024,4096,16384,65536,18,72,288,1152,4608,18432,73728,32786]`.
These are calculations for the independently defined quotient, not a replay or
formal verification of the archived runner.

## Comparison with the exact producer

The three primary Lean modules and both target YAML files were read using
`git show 976b82bf60afda5e3d31c0da2704604ea2f2e5a5:<path>`. All eight Git blob
IDs in `../../inputs.json` match that tree. The source polynomials have exactly
the blinded coefficients. The canonical field is literally `GaloisField 2 17`,
and the target is the `ZMod 2` linear-map minimal polynomial of its Frobenius.
Neither declaration substitutes an assumed conclusion or a conditional runner
statement for the advertised mathematical claim.

The producer irreducibility proof uses cyclotomic degree and the order of 2
modulo 17. The independent checks used explicit modular arithmetic and exhaustive
divisibility. The canonical proof uses Mathlib finite-field theorems; the blind
argument uses the elementary linearized-polynomial root bound. These provide
separate derivations of the advertised results.

At this head, `implementation/gf2.py:13` pins the same modulus;
`Field.mul` uses carryless multiplication/reduction, `Field.sqr` calls
`mul(a,a)`, and `make_field(17)` picks that pin. In `implementation/run.py`,
`_frobenius_cols` at line 351 squares the polynomial-basis vectors,
`ker_p_phi` at line 414 evaluates the factor polynomial on this map and takes
its binary nullspace, and `build_tau_closed_from_factors` at line 420 joins
selected kernels and checks dimension and stability. This source correspondence
is consistent with the independent matrix, but was not executed or formally
certified by J2.

The source `admissible-phi-dims.json` records `{0,1,8,9,16,17}`. Abstractly,
the squarefree minimal/characteristic polynomial and the distinct simple
components of dimensions 1,8,8 give exactly eight invariant subspaces, with
dimensions `0,1,8,8,9,9,16,17`; the set of dimensions is the archived set.
Completeness uses the Chinese-remainder/primary-decomposition theorem: every
invariant submodule is the sum of its intersections with the three pairwise
nonisomorphic simple components, and each intersection is zero or the full
component. This mathematical consequence is stronger than the two named
producer declarations and is not attributed to those declarations as a Lean
classification proof.

## Missing bridges, individually

1. **Concrete encoded object.** Define the runner's 17-bit values as elements of
   `F2[X]/(X^17+X^3+1)` and prove coefficient order, canonical representatives,
   and bitwise addition agree with the formal representation.
2. **Concrete field.** Formalize irreducibility of that degree-17 modulus and
   establish the quotient's field structure, cardinality, and dimension. The
   independently checked arithmetic here is not a Lean proof of that bridge.
3. **Executable arithmetic.** Prove the runner's `clmul`, `pmod`, `Field.mul`
   and `Field.sqr` implement the corresponding quotient operations for the
   intended inputs, and bind the run's source/version and modulus to them.
4. **Canonical transport.** Construct a field/F2-algebra equivalence from the
   formal concrete quotient to `GaloisField 2 17`; prove it intertwines square
   maps, and transport order/minimal polynomial. Abstract finite-field
   uniqueness supplies existence mathematically; it does not certify Python.
5. **Linear representation.** Prove `_frobenius_cols`, vector application and
   polynomial evaluation represent the transported endomorphism in the actual
   bit basis. An explicit normal-basis/cyclic-module equivalence is one route;
   the independent `x+1` orbit is a concrete candidate, not a producer theorem.
6. **Complete classification.** Formalize squarefreeness, coprime primary
   decomposition, simplicity and multiplicity one; show both directions of
   the correspondence between invariant subspaces and sums of those components.
   Derive exactly the dimension set, including existence and exclusion.
7. **Constructor and predicate refinement.** Prove the runner's nullspace,
   rank, polynomial-kernel and saturation code returns the stated subspaces;
   relate its selected factor subsets and membership/stability checks to the
   classification. The constructor selects the first matching subset and
   does not enumerate every subspace. In particular its structured loop omits
   the empty subset, so its API should not be described as a complete constructor
   for every admissible dimension without separately handling dimension zero.
8. **Archived-output binding.** Connect the exact executed runner, parameters,
   generated bases and serialized dimension table to the proved constructions.
   Structural theorems alone do not authenticate historical execution or the
   relation-yield counts.

The reviewed producer modules explicitly disclaim runner binding, classification,
and yield certification. The existing problem record
`problems/binstd-frobenius-invariant-dimension-lean-bridge.md` already names these
formalization gaps. They limit downstream use; they do not break the two scoped
canonical statements. `YieldCeiling.lean`, the only other BINSTD module in the
exact tree, contains conditional count arithmetic and supplies none of these
structural bridges.

## Verification and procedural limits

| Claim | J2 mathematical verdict | J2 semantic fidelity | J2 fresh Lean machine status |
| --- | --- | --- | --- |
| `factor8_irreducible_pair` | holds | faithful_scoped | not_verified |
| `canonicalFrobenius_order_and_minpoly` | holds | faithful_scoped | not_verified |
| Full concrete runner/classification certification | inconclusive as formal certification | partial | not_verified |

The legacy receipts were read after sealing. They claim successful builds and
audits but identify source commits `30a97e57...` and `4cd570dc...`, not the
reviewed head, and do not contain a complete current workspace binding. J2 does
not authenticate those executions or replace the coordinator's fresh named-module
machine gate. No heavy Lake build, benchmark, experiment, empirical replay,
scientific status transition, or security/performance inference was performed.

The current plan uses Conductor IDs `T-608` and `T-609`; the exact-head
`check_review_independence.py` accepts `TASK-*` IDs and expects additional
blind-phase fields. Its legacy union-of-reads check also needs the supported
phased-release declarations to distinguish permitted post-seal reads. J2 reports
the actual ID and actual phases rather than rewriting the historical plan or
omitting reads. The coordinator owns that protocol reconciliation and any
round-level independence check; J2 does not inspect sibling reports to run it.

Technical-literature/context reading was intentionally deferred until the blind
seal as the task required. Afterwards the reviewer read the exact producer
source, target statements, bridge problem, review workflow and repository
contract. The finite-algebra argument is self-contained; no novelty claim or
external literature-coverage claim is made.
