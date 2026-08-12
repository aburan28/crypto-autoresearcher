# Experiment Contract: first-norm semantics and exact rank caps v2

## Protocol status

`REVIEW_REQUIRED`. No execution result may be promoted until this version is
independently reviewed, repaired if necessary, hashed, and frozen in Git.

Version 2 preserves v1 and repairs the pure-squaring terminology, exact cell
matrix and cache policy, workload and traffic formulas, comparator boundaries,
cohort-span wording, deterministic-case semantics, and executable mutation
schedule.

## Hypothesis

On the frozen five-source RCB circuit, the componentwise norm tensor `h_Q`
has the exact degree-preserving formula, source-span representation, and
ambient-capped Hilbert TT rank bounds stated in `theory-v2.md`.

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

`execution-matrix-v2.json` is authoritative for the exact cell cross-product,
target-independent diagnostic cache, rank jobs, run partition, mandatory
counts, and resource projection. `mutation-manifest-v2.json` is authoritative
for control tensors, mutation transformations, execution cells, detectors,
and required rejection outcomes.

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

with the six coefficients from `theory-v2.md`. In the frozen trace-zero basis,
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

`mutation-manifest-v2.json` freezes six exact controls and 15 exact mutations
before source implementation. Its asymmetric control has independently
certified cut ranks `(1,2,3,4)`, so reversing the cut order cannot survive by
symmetry. Its quadratic norm control has ranks `(2,1,1,1)`. The dense SHA-256
control has preregistered ranks `(4,16,16,4)` over `F_947`.

Mutation `M07-RANK-FIELD-PROVENANCE` is a mandatory static provenance failure,
not a numeric rank test. An `F_p` matrix has the same rank after extension to
`F_p2`, so no valid numeric test could distinguish the wrong field label.

The exact flipped circuit mutation is gate 37,
`X3=X3-t0 -> X3=X3+t0`. All dynamic EC mutations use the frozen
`C08:random_unique:Q00` cell unless the mutation manifest names another cell.
Static mutations operate on in-memory record or source copies and never edit
the repository.

The mutation generator emits isolated mini-artifacts. The non-importing
verifier must reject each one with the frozen detector. The suite itself emits
strict `valid:true` only when all expected rejections occur. A surviving,
missing, post-hoc replaced, or unexecuted mutation invalidates the mutation
run.

## R6: parameters and analysis schedule

The complete mandatory schedule is `execution-matrix-v2.json`. Per curve it
contains exactly these ten semantic cells:

```text
random_unique: Q00,Q01,Q02,IDENTITY,PLANTED
x_interval: Q00,Q01,Q02
consecutive_scalar_control: Q00
rescaled random_unique: Q00
```

This is 54 unscaled registry-target cells and six rescaled cells. There are no
optional cells.

Each process constructs exactly three unscaled source-output tables per curve
and one rescaled `random_unique` table. A table is enumerated once, cached only
inside that process, reused across its declared target cells, charged as
`diagnostic_full_enumeration`, and discarded before the next curve. The cache
is not retained advice and cannot support a compiler claim.

The rank schedule is exact:

- all four `h` cuts for Q00 on all three registries plus identity and planted;
- only cut two of `h` for Q01 and Q02 on both primary registries;
- all four `g` cuts only for `random_unique:Q00`;
- all four cuts of `h^2,h^4,h^8` only for `random_unique:Q00`;
- all four rescaled `h` cuts for `random_unique:Q00`;
- all four cuts of each of six deterministic global controls.

This yields 264 EC rank jobs plus 24 control rank jobs per producer or
verifier path. Two tested-cohort span jobs per curve use only Q00,Q01,Q02 and
are reported as `tested_cohort_span_dimension`. The universal five-source
trace-zero bound comes from the symbolic coefficient formula, not from the
three-target sample.

Each curve also has three mandatory `D2+D3` comparator jobs, one per registry.
They measure `N2`, `N3`, operation counts, exact record widths, lookup traffic,
and certificate replay traffic. Across six curves this is 18 comparator jobs;
the candidate-addition upper bound is 7002.

The full `B^5` enumeration is `SANITY_ONLY`. No fitted exponent, slope, or
sub-rho extrapolation is allowed. Diagnostic powers check finite-size value
and rank semantics only.

For pure squaring states, define

```text
j_star(B)=max(0,ceil(log_4(B/9216))).
```

This is the first pure-squaring state whose Hilbert ceiling can reach `B`. A
`j_star-1,j_star` bracket is defined only when `j_star>0`. It is not a
chain-wide statement. A successor must freeze an actual addition chain and
check every accumulator exponent `e_s` against

```text
rho2(h^e_s)<=min(B^2,9216*e_s^2),
e_s>=ceil(sqrt(B/9216)) at loss of the strict sub-B certificate.
```

## R7: accounting and resource gates

Every record separates producer, verifier, control, mutation, certificate,
and comparator ledgers. Base-field counters distinguish addition/subtraction,
multiplication, squaring, inversion, comparison, and modular reduction.
Extension-field counters distinguish addition/subtraction, multiplication,
squaring, inversion, conjugation, comparison, and reduction, and also report
their expanded base-field operations. RCB gates, residual formation, both norm
paths, power formation, elimination, certificate digesting, and replay have
separate buckets.

Traffic buckets separately record source-table construction, cache reads and
writes, target residuals, norm paths, powers, each rank job, certificates,
mutation artifacts, and verifier replay. Advice, preprocessing, and online
specialization remain empty or `not_executed` in this semantic run; the
`B^5` cache cannot be reclassified as advice.

The cases are deterministic, so `success_probability` is `not_applicable`.
The run reports exact valid/invalid, witness, and no-hit counts by frozen
cohort. It also reports whether generator, modulus, curve, registry, and target
are fixed, plus all special modulus, curve, registry, and extension structure.

For `N=B^5` entries:

```text
canonical_Fp_bytes = ceil(log2(p)/8)
canonical_K_bytes  = 2*canonical_Fp_bytes
g_value_bytes      = N*canonical_K_bytes
h_value_bytes      = N*canonical_Fp_bytes
```

The implementation may stream or reuse storage, but both logical traffic and
peak live state are measured. Python object overhead is captured by peak RSS
and never substituted for canonical storage. Peak RSS uses
`resource.getrusage(RUSAGE_SELF).ru_maxrss`; Darwin values are bytes and Linux
values are KiB multiplied by 1024. The raw platform value, platform name,
normalization rule, and normalized bytes are all emitted. Wall time uses
`time.perf_counter_ns`.

For an unfolding, orient the smaller dimension as `r` rows and the larger as
`c` columns. The frozen worst-case exact-elimination ledger is

```text
normalization multiplications <= c*r*(r+1)/2
elimination subtractions       <= c*r*(r-1)/2
inversions                     <= r
logical coefficient traffic   <= 3*c*r*(r+1)/2 words.
```

The execution matrix expands these formulas to 159007996 base-field rank
normalization multiplications, 14725568 extension-field rank normalization
multiplications, and 565377396 base-field-word-equivalent rank traffic per
baseline path, including controls. Dynamic counters must not exceed the frozen
upper bounds and exact observed counts are still emitted.

For a dense five-core TT with bonds `(r1,r2,r3,r4)`, the declared base-field
word count is

```text
B*(r1+r1*r2+r2*r3+r3*r4+r4).
```

At the first-norm theorem caps this is `3542508*B` words. The common Hilbert
coefficient ceiling has `127401984` entries. Neither object is materialized in
v2. The `9216 by 13824` and all larger coefficient matrices are prohibited
under the 2 GB gate because exact elimination needs additional workspace.

The frozen per-path totals are:

```text
source tuple evaluations = 615868
RCB calls               = 2463472
residual/norm cells     = 1539670
power squarings         = 461901
rank jobs               = 288
tested-cohort spans     = 12
D2+D3 comparator jobs   = 18.
```

The projected peak RSS is at most 512 MiB because curves are processed
sequentially and the largest source table has 100000 tuples. The hard limit
remains 2 GiB. The target is at most 3600 seconds for each baseline producer
or verifier and 12 aggregate CPU hours. A mandatory timeout or resource
refusal makes that run invalid; completed cells remain scoped diagnostics but
cannot satisfy the all-cases criterion.

### Comparator boundary

The semantic run does not execute a performance comparator. Its analysis must
still display the following normalized boundaries:

| Object | Fixed-curve work | Online/query work | Storage and traffic |
|---|---:|---:|---:|
| This diagnostic | `Theta(B^5)` per source table | not a compiler | every tuple and cache byte charged |
| `D2+D3` table | `Theta(B^2+B*N2)`, at most `Theta(B^3)` | at most `N2`, hence at most `B^2` lookups | retain `N2+N3` records plus replay data |
| Pollard rho/VOW | no hidden preprocessing | `C_rho*sqrt(q/|Aut|)=Theta(B^2.5)` total group work | parallel total work, distinguished-point records, communication, and replay charged |

Here `N2` and `N3` are the measured distinct two- and three-sum counts for the
same registry. This run reports their values, record byte widths, lookup
traffic, replay, and usable negation or endomorphism quotient `|Aut|`. A later
end-to-end successor must measure VOW total work, communication, and memory.
No wall-clock-only comparison is valid.

Tier B requires fixed advice, preprocessing workspace, operations, and traffic
each `o(B^3)`, with per-target work, traffic, and peak state each `o(B^2)`.
Tier C requires retained bytes, preprocessing, relation generation, linear
algebra, target descent, and verification each `o(B^2.5)` in its own unit under
one success distribution. Units are never added into one score.

Hard limits:

- 2 GB peak RSS per process;
- 3600 seconds per run;
- 12 aggregate CPU hours;
- six harness runs;
- no undeclared network or external computer algebra service.

Crossing a resource gate preserves a resource refusal. It is not evidence of
high mathematical rank.

## R8: interpretation firewall

Every artifact must contain `interpretation=SANITY_ONLY`,
`breakthrough_claim=false`, `compiler_constructed=false`, and
`success_probability=not_applicable`. The run may report the restricted
theorem as independently replayed toy semantics. It may not report a universal
target-family dimension from three targets, a chain-wide power frontier from
pure squares, retained advice from the `B^5` cache, or a performance result
from the non-executed rho formula.

Passing authorizes one new reviewed coefficient-space construction contract.
It does not approve that successor's implementation, execution, or claim.

## Positive control

All six tensors in `mutation-manifest-v2.json` must have their preregistered
exact cut profiles. The synthetic quadratic norm must demonstrate rank above
one, and the asymmetric profile must bind all four cut labels. Planted and
identity targets must pass their exact semantic checks.

## Negative control

The full-rank dense tensor and all 15 frozen mutations must exercise high-rank,
provenance, accounting, schedule, and interpretation failures. The
consecutive-scalar registry tests sensitivity to overt additive structure and
is never merged into primary evidence.

## Success criterion

Success requires all of the following:

- zero independent RCB, norm, source-span, tuple-order, zero-set, and
  projective-rescaling mismatches;
- every exact `h_Q` rank at or below its finite-registry Hilbert cap;
- all deterministic controls pass;
- all 15 mutation classes are detected or statically rejected;
- all 60 semantic cells, 288 rank jobs, 12 tested-cohort spans, 18 comparator
  jobs, and four harness partitions are present with no optional or silently
  censored cell;
- complete operation, traffic, storage, RSS, timing, and provenance records;
- `success_probability` is exactly `not_applicable`, while deterministic
  witness and no-hit counts are complete;
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
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/generate_tt_norm_rank.py --mode baseline --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json --execution-matrix experiments/EXP-ECDLP-TT-NORM-RANK-001/execution-matrix-v2.json --mutation-manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/mutation-manifest-v2.json
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py --mode baseline --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json --execution-matrix experiments/EXP-ECDLP-TT-NORM-RANK-001/execution-matrix-v2.json --mutation-manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/mutation-manifest-v2.json --raw-result <immutable-baseline-run-path>/raw-result.json
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/generate_tt_norm_rank.py --mode mutations --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json --execution-matrix experiments/EXP-ECDLP-TT-NORM-RANK-001/execution-matrix-v2.json --mutation-manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/mutation-manifest-v2.json
PYTHONDONTWRITEBYTECODE=1 python3 experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py --mode mutations --manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/instance-manifest-v1.json --execution-matrix experiments/EXP-ECDLP-TT-NORM-RANK-001/execution-matrix-v2.json --mutation-manifest experiments/EXP-ECDLP-TT-NORM-RANK-001/mutation-manifest-v2.json --raw-result <immutable-mutation-run-path>/raw-result.json
```

Canonical harness commands and exact hashes are added only to an approved
`specification.json`; they may not be guessed into this review record.
