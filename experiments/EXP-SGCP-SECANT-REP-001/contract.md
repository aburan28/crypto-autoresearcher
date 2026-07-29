# Experiment Contract: Fixed-Chart Slope Representative Compiler V2

## Protocol status

Status: `HYPOTHESIS`, `MODEL-BOUND`, `NOVELTY-UNVERIFIED`.

Execution status: `review_required`.

Active resource budget: zero. Maximum runs: zero. No implementation or
execution is authorized.

## Hypothesis

For one preregistered cap fraction in `{1/2,3/4}`, fixed-chart canonical-residue
slope ordering strictly beats all 31 deterministic within-fiber hash controls
on both retained eight-term support and normalized pre-optimization conflict
density for at least two of three factor-base draws on at least two of three
generated curves, and the same fixture-level result holds in every
preregistered coordinate chart.

## Null hypothesis

The complete valid matrix does not meet that gate. The hash controls are a
finite descriptive benchmark, not exchangeable random samples and not a
calibrated significance test.

## Parameters

- Curve seeds: `731001`, `731002`, `731003`.
- Factor-base seeds per curve: `9101`, `9102`, `9103`.
- Field size: seven bits.
- Factor base: frozen sign-complete random-x set with `B=6`.
- Curves: ordinary prime-order short-Weierstrass curves over `F_p`, with
  `p>3`, trace not in `{0,1}`, and `j` not in `{0,1728}`.
- Caps: deduplicated increasing values
  `floor(q/4),floor(q/2),floor(3q/4),q`.
- Candidate charts: `u in {1,-1,2,3}`, reduced modulo `p`; a draw is invalid if
  these are not four distinct nonzero residues.
- Chart `u` maps
  `(x,y,a,b)` to `(u^2*x,u^3*y,u^4*a,u^6*b)` modulo `p`.
- No chart, factor base, cap, or control may be selected after results are
  observed.

Rejected curve draws are replaced by incrementing only the curve-search attempt
counter under the frozen seed derivation. Rejected factor-base draws are
replaced by incrementing only that factor-base attempt counter. Every attempt,
reason, and field/group operation is logged.

## Canonical source and witness encoding

Each factor base is sorted by canonical affine point tuple `(x,y)` with field
elements represented by their least integer residues in `[0,p)`. The resulting
zero-based position is the source label.

For each nonidentity `R` in `2F`, define the unordered multiset fiber

```text
W_R = {(i,j): 0 <= i <= j < B and P_i + P_j = R}.
```

Branching is exact:

1. `i<j` and `x_i!=x_j`: secant
   `lambda=(y_j-y_i)/(x_j-x_i) mod p`.
2. `i=j`: tangent
   `lambda=(3*x_i^2+a)/(2*y_i) mod p`.
3. `i<j` and `x_i=x_j`: inverse/vertical pair, hence identity; exclude from
   every nonidentity `W_R`.

Odd prime group order excludes rational two-torsion, so the tangent denominator
is nonzero. Store `lambda` as its canonical residue in `[0,p)`. The intercept
is diagnostic only:

```text
nu = y_i-lambda*x_i = -y_R-lambda*x_R mod p.
```

It supplies no independent within-fiber ordering. The candidate selects the
least `(lambda,i,j)`. Distinct valid witnesses for fixed nonidentity `R` should
have distinct slopes; a tie is nevertheless resolved by `(i,j)` and reported.

The candidate must be equivariant under two frozen source-label permutations:
reverse order and the SHA-256 order of canonical point bytes. Mapping selected
pairs back to affine points must reproduce the unpermuted selected-pair set.

## Hash controls

For control index `c in 0..30`, rank each witness with:

```text
SHA256(
  ASCII("EXP-SGCP-SECANT-REP-001|HASH-CONTROL|v2") || 0x00 ||
  U32BE(c) ||
  U32BE(width) ||
  FBE(p) || FBE(a) || FBE(b) ||
  FBE(x_R) || FBE(y_R) ||
  FBE(x_i) || FBE(y_i) ||
  FBE(x_j) || FBE(y_j)
)
```

Here `width=ceil(bit_length(p)/8)` and every `FBE` value is exactly `width`
unsigned big-endian bytes. Endpoints are first sorted by canonical affine point
tuple. The least `(digest,endpoint_1,endpoint_2)` wins. Digest ties are retained
as a diagnostic and resolved by endpoint tuples. Curve, factor-base, and fiber
identity are therefore bound through their complete canonical point content;
source-label permutations cannot change a control table.

Duplicate control tables and scores remain in the 31-control benchmark. Report
their multiplicities; never resample or deduplicate.

## Common and compiler-specific universes

The following are common across candidate and controls:

- curve and coordinate chart;
- factor-base points and source labels;
- semantic `2F` output points and all fibers `W_R`;
- the unordered slot universe of pairs of semantic `2F` output classes;
- cap values and optimizer algorithm.

The following are compiler-specific and must not be called identical:

- chosen degree-two formal representatives;
- flattened degree-four source multisets;
- duplicate collapses among flattened multisets;
- eligible degree-four formal vertices;
- constrained labels, public edges, conflict graph, and retained formal ideal.

For every compiler report the slot count, distinct flattened formal-multiset
count, semantic four-sum support, duplicate-collapse histogram, eligible vertex
count, conflict-edge count, and normalized conflict density
`2E/(V*(V-1))` with exact rational numerator/denominator. The optimizer receives
the compiler-specific formal universe.

## Optimizer contract

Use the exact `EXP-SGCP-EMBED-002` objective at each cap:

1. maximize retained eight-term support `R(S)`;
2. minimize constrained labels;
3. minimize public nonidentity edges;
4. maximize retained degree-four maxima;
5. choose the lexicographically least maximum list.

Every compiler/cap run starts in a fresh process with empty replay cache,
primary cache, incumbent, and frontier. It records an input digest, complete
objective, lower and upper bounds, absolute gap, node counts, cache insertions,
and an empty-frontier digest. A result is complete only with
`full_objective_exact=true`, equal bounds, zero gap, and independent replay.
Branch order is fixed before implementation and cannot depend on compiler type.

## Nonvacuity gates

Each fixture/chart must have:

- at least eight nonsingleton fibers;
- total choice entropy
  `sum_R log2(|W_R|)` at least eight bits, reported as the exact product
  `prod_R |W_R| >= 256` rather than a floating approximation;
- candidate/formal-lex Hamming distance at least
  `max(4,ceil(nonsingleton_count/5))`;
- at least 16 distinct hash-control tables;
- at least eight distinct complete control objective vectors across the two
  decision caps.

Failure of any item is `SCOPED_NEGATIVE_VACUOUS`, not `INCONCLUSIVE`.

## Finite rank and decision rule

At one cap, the candidate wins a metric only if it is strictly better than all
31 controls. Ties fail. This is finite rank `1/32`; it is not called a
percentile or p-value.

A fixture/chart passes a cap only when:

- candidate retained eight-term support is strictly greater than every control;
- candidate normalized pre-optimization conflict density is strictly lower
  than every control;
- all semantic, embedding, witness, and optimizer checks pass.

One fixture passes a cap only when all four charts pass that same cap. The
experiment is `PASS_PROMOTE` only when one same cap fraction in `{1/2,3/4}`
passes for at least two factor-base seeds on at least two curve seeds.

Complete valid outcomes are exhaustive:

- `PASS_PROMOTE`: the full gate above passes.
- `SCOPED_NEGATIVE_MECHANISM`: support rank passes the replication gate but
  conflict-density rank does not.
- `SCOPED_NEGATIVE_CHART`: chart `u=1` passes the replication gate but at least
  one other chart does not.
- `SCOPED_NEGATIVE_VACUOUS`: a nonvacuity gate fails.
- `SCOPED_NEGATIVE_NO_SIGNAL`: the complete matrix is valid but none of the
  preceding cases applies.
- `INCONCLUSIVE`: optimizer/resource/infrastructure failure, malformed or
  partial matrix, or independent-verifier disagreement.

## Controls

1. Regression control: replay the exact registered `EXP-SGCP-EMBED-001` fixture
   and its frozen objective receipt before new results.
2. Synthetic optimizer positive control: a frozen abstract two-fiber conflict
   graph with four representative tables, one uniquely optimal table, and an
   exhaustive oracle must be solved exactly by producer and verifier.
3. Invariant negative control: all fibers singleton, so every compiler must
   produce byte-identical tables and objective vectors.
4. Exhaustive tiny control: enumerate every representative table on one frozen
   multiplicity-rich toy fixture and reproduce the full exact score
   distribution.
5. Coordinate controls: all four `u` charts above, with no best-chart
   selection.
6. Source-label controls: reverse and hash-ranked permutations.

The exact fixtures, bytes, digests, and expected control receipts must be frozen
in a reviewed implementation contract before execution.

## Accounting

Report shared curve/factor-base generation separately from every compiler,
optimizer, and verifier role. Charge:

- field and EC operations, branches, comparisons, sort keys, hashes, and hash
  input bytes;
- pair enumeration, table lookup/insert, deduplication, graph cells, final-pair
  cells, optimizer nodes, bounds, cache inserts, and failed attempts;
- canonical artifact bytes, retained advice bytes, temporary bytes, logical
  reads/writes, disk bytes and I/O calls;
- isolated role CPU time, wall time, peak RSS, and artifact storage;
- all independent-verifier work in a separate ledger.

These are local structural costs. No attack-cost claim follows.

## Interpretation boundary

The chord/tangent formulas, collinear-triple geometry, decomposition fibers,
coordinate factor bases, and additive-energy concepts are established. The
apparently unreported element is only the use of a fixed-chart least-slope
section of each pair-sum fiber to optimize a recursive structured-generic
embedding. Novelty remains unverified.

A pass would be a toy coordinate-specific structured-embedding signal. It
would not establish relation generation, matrix rank, individual logarithms,
index calculus, an exponent improvement, or a Pollard-rho break.

## Next concrete action

Obtain fresh independent theory and red-team review of v2 and complete the
remaining citation-chain search before implementation design.
