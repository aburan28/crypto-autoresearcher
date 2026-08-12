# Experiment Contract: first-norm semantics and exact rank caps v1

## Protocol status

`REVIEW_REQUIRED`. No execution result may be promoted until this version is
independently reviewed, repaired if necessary, hashed, and frozen in Git.

## Hypothesis

On the frozen five-source RCB circuit, the componentwise norm tensor `h_Q`
has the exact degree-preserving formula, source-span representation, and
ambient-capped Hilbert TT rank bounds stated in `theory-v1.md`.

The toy run tests implementation semantics and exact finite-registry ranks. It
does not test an asymptotic rank exponent.

## Null hypothesis

At least one claimed identity, rank cap, source-span statement, field
declaration, or independent replay path fails on the frozen instances, or the
purported constructive route hides an uncharged `B`-dependent object or
shared producer/verifier implementation.

## R1: claim boundary

Passing this contract supports only these statements:

- the frozen implementation realizes the restricted first-norm theorem;
- toy exact ranks and source-span dimensions were measured correctly;
- the first norm is no longer the immediate rank-existence obstruction;
- a separate coefficient-space advice construction is justified.

It does not support:

- a subquadratic zero locator;
- a five-point decomposition algorithm;
- a relation-generation advantage;
- an index-calculus complexity claim;
- a single-instance or fixed-curve ECDLP improvement;
- an exponent below rho.

## R2: frozen objects

`instance-manifest-v1.json` is authoritative for:

- six tuples `(p,q,a,b,G,B)`;
- curve model, group order, trace, cofactor, and `j` invariant;
- three exact registry families per curve;
- three primary targets per curve selected by frozen SHA-256 labels;
- identity and planted targets as controls only;
- quadratic nonresidue, basis, trace, norm, and conjugation;
- mode order `(P1,P2,P3,P4,P5)`;
- left-associated addition tree;
- literal 40-gate RCB text and its SHA-256 digest;
- rank fields.

Primary cohorts are `random_unique` and `x_interval`. Every primary registry
must contain exactly `B` unique affine points and unique identifiers. The
`consecutive_scalar_control`, identity, planted target, repeated tuple indices,
and any duplicate-label mutation are controls and never primary evidence.

No object may be replaced after any tensor value or rank is observed. A change
requires `instance-manifest-v2.json`, `specification-v2.json`, a new review,
and preserved v1 history.

## R3: exact value paths

### Generator path

The producer must contain a literal local transcription of all 40 RCB gates,
use `b3=3b mod p`, and enumerate tuples in documented lexicographic order.
For each tuple and target it computes:

```text
S=(X:Y:Z)
e_X=Z_Q X-X_Q Z
e_Y=Z_Q Y-Y_Q Z
g_Q=e_X+omega e_Y
h_Q=g_Q conjugate(g_Q).
```

`F_p2` elements use an explicit pair representation in the frozen basis.

### Verifier path

The verifier must not import the generator, its RCB routine, its extension
arithmetic, its rank routine, or its tuple iterator. It must use:

- an independently transcribed RCB evaluator with different local structure;
- a mixed-radix or recursive tuple traversal, not the producer iterator;
- a separate `F_p2` implementation;
- column-oriented incremental exact elimination;
- an independently coded affine group law only for projective validity,
  equality, and zero-set replay.

Affine addition may never assign a nonzero RCB tensor value or a rank.

### Required norm equality

Both sides are computed independently:

```text
h_product = g_Q conjugate(g_Q)
h_quad    = e_X^2+t e_X e_Y+n e_Y^2.
```

The mismatch count must be zero. The verifier also evaluates

```text
h_source = c1 X^2+c2 XZ+c3 Z^2+c4 XY+c5 YZ+c6 Y^2
```

with the six coefficients from `theory-v1.md`. In the frozen trace-zero basis,
it must separately assert `c4=0`.

### Projective controls

Nonzero source and target rescaling factors are derived from frozen SHA-256
labels. The verifier checks:

- nonzero projective outputs and curve membership;
- affine equivalence of the output and independent group sum;
- zero-set invariance;
- predicted homogeneous scaling
  `mu^2 product_j(lambda_j^(2D_j))` for `h_Q`;
- exact rank invariance under the induced separable row/column scalings.

## R4: exact rank semantics

For an order-five tensor, cut `k` uses rows `(i1,...,ik)` and columns
`(i(k+1),...,i5)` in the manifest's mode order. The producer uses exact
row-oriented Gaussian elimination. The verifier uses an independently coded
column-basis algorithm.

- `g_Q` ranks are over `F_p2`.
- `h_Q` and `h_Q^e` ranks are over `F_p`.
- zero matrices have rank zero.
- raw direct-sum or Hadamard bond products are reported as raw dimensions,
  never as exact ranks.
- because `h_Q` is base-field valued, equality of its `F_p` and `F_p2` ranks
  is replayed on controls but never used to replace the declared base-field
  computation.

For degree vector `d=(d1,...,d5)`, set

```text
n_j=min(B,3d_j).
```

The recorded Hilbert cap at cut `k` is

```text
min(product(n_j,j<=k),product(n_j,j>k)).
```

The exact rank must not exceed it. A rank equal to `B^2` at a toy middle cut
is permitted and is not a route-stop result.

## R5: controls and mutations

The following deterministic tensors are required before EC evidence:

- separable `T(i1,...,i5)=product_j(i_j+1)`, rank one at every cut;
- synthetic `g=u(i1)+omega*v(i2)` with nonconstant `u,v`, whose norm has a
  checked rank above one at cut one;
- all-zero tensor, rank zero;
- one-spike tensor, rank one at every cut;
- SHA-256-seeded dense pseudorandom tensor, checked against a second rank path.

The mutation suite must detect and reject every applicable mutation:

1. `b3=b` instead of `3b`;
2. one flipped RCB addition or subtraction gate;
3. incomplete affine addition used as the producer;
4. projective output `(0,0,0)` accepted as a point;
5. `omega^p=omega` instead of `-omega`;
6. `g^2` substituted for `g*conjugate(g)`;
7. extension-field rank reported in place of required base-field rank;
8. raw Hadamard bond products reported as exact ranks;
9. reversed or shifted cut ordering;
10. target chosen after rank observation;
11. duplicate primary labels or points;
12. producer math imported by the verifier;
13. full enumeration omitted from operation accounting;
14. canonical bytes or peak RSS omitted;
15. a toy fixed-power result labeled asymptotic.

Mutations 10, 12, and 15 may be static protocol-lint failures rather than
numeric runs. The report must distinguish static from dynamic detection.

## R6: parameters and analysis schedule

- Curves: `C08,C10,C12,C14,C15,C17`.
- Registry sizes: `B={3,4,5,7,8,10}`.
- Primary registry families: `random_unique,x_interval`.
- Structured control: `consecutive_scalar_control`.
- Primary targets: three preselected targets per curve.
- Control targets: identity and one planted five-term sum.
- Diagnostic powers: `e={1,2,4,8}`.
- Cuts: `k={1,2,3,4}`.

The full `B^5` enumeration is `SANITY_ONLY`. No fitted exponent, slope, or
sub-rho extrapolation is allowed. Power ranks are reported to validate exact
power semantics and finite-size behavior only. The chain-wide frontier is the
paper formula

```text
j_star(B)=max(0,ceil(log_4(B/9216))).
```

and requires a separate scalable implicit experiment.

## R7: accounting and resource gates

Every record reports separately:

- offline base-field additions, multiplications, inversions, and comparisons;
- retained advice in field words and canonical bytes;
- preprocessing logical reads/writes and canonical-byte traffic;
- online target-specialization operations, reads/writes, and live state;
- full-enumeration tuple and gate counts;
- rank-elimination operations;
- wall-clock time and peak RSS;
- number and type of supported targets;
- success probability and observed success count;
- whether the generator, field modulus, curve, factor base, and target are
  fixed or variable;
- any special curve, modulus, registry, or extension structure.

For `N=B^5` entries:

```text
canonical_Fp_bytes = ceil(log2(p)/8)
canonical_K_bytes  = 2*canonical_Fp_bytes
g_value_bytes      = N*canonical_K_bytes
h_value_bytes      = N*canonical_Fp_bytes
```

The implementation may stream or reuse storage, but both logical traffic and
peak live state are measured. Python object overhead is captured by peak RSS
and never substituted for canonical storage.

For a dense five-core TT with bonds `(r1,r2,r3,r4)`, the declared base-field
word count is

```text
B*(r1+r1*r2+r2*r3+r3*r4+r4).
```

At the first-norm theorem caps this is `3542508*B` words. The common Hilbert
coefficient ceiling has `127401984` entries. Neither object is materialized in
v1. The `9216 by 13824` and all larger coefficient matrices are prohibited
under the 2 GB gate because exact elimination needs additional workspace.

Hard limits:

- 2 GB peak RSS per process;
- 3600 seconds per run;
- 12 aggregate CPU hours;
- six harness runs;
- no undeclared network or external computer algebra service.

Crossing a resource gate preserves a resource refusal. It is not evidence of
high mathematical rank.

## Positive control

The separable, zero, one-spike, and planted-target cases must have their
preregistered semantic and rank behavior. The synthetic quadratic norm must
demonstrate that the rank routines do not collapse every norm tensor to rank
one.

## Negative control

The dense pseudorandom tensor and listed mutations must exercise high-rank and
failure paths. The consecutive-scalar registry tests sensitivity to overt
additive structure and is never merged into primary evidence.

## Success criterion

Success requires all of the following:

- zero independent RCB, norm, source-span, tuple-order, zero-set, and
  projective-rescaling mismatches;
- every exact `h_Q` rank at or below its finite-registry Hilbert cap;
- all deterministic controls pass;
- all 15 mutation classes are detected or statically rejected;
- complete operation, traffic, storage, RSS, timing, and provenance records;
- generator and verifier emit strict JSON with exact `valid:true` only after
  all local gates pass.

Passing authorizes only a successor coefficient-space advice-construction
experiment.

## Falsification criterion

A reproducible independent semantic mismatch or Hilbert-cap violation rejects
the corresponding restricted implementation claim. A source tensor outside
the declared span rejects the six-source construction. Hidden `B^5`
construction or omitted advice costs rejects the compiler interpretation.

These do not falsify the theorem by themselves:

- toy middle-rank saturation;
- failure to allocate a prohibited dense matrix;
- large but constant source ranks;
- failure of a later power stage;
- absence of a five-term witness for a uniform target.

## Reproduction command

After review, implementation, protocol hashing, and Git freeze, the planned
direct commands are:

```bash
cd /Volumes/Volume/crypto-autoresearcher-worktrees/outer-translator-001
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/generate_tt_norm_rank.py --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json --raw-result <immutable-run-path>/raw-result.json
```

Canonical harness commands and exact hashes are added only to an approved
`specification.json`; they may not be guessed into this review record.

