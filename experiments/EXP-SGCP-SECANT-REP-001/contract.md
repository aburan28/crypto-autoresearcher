# Experiment Contract: Fixed-Chart Slope Representative Compiler V6

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
- `q` is exactly the odd prime cardinality `#E(F_p)` of the generated curve.
  It is not the field modulus, a subgroup estimate, or a constrained-label
  count.
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

The inherited optimizer and generation reference is exact commit
`c02d31eb67e4e24f0866ba0a045e72dbe74a3844`:

- `EXP-SGCP-EMBED-002/contract.md` SHA-256
  `b93084cf19634533210fd0c48fd7ea2f84f9b718b9320f5d390b363f403df2fe`;
- producer SHA-256
  `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8`;
- verifier SHA-256
  `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199`.

V6 does not authorize reuse of those CLIs. A future implementation contract
must reproduce their curve/factor-base derivation byte for byte or freeze a
complete replacement derivation and differential receipt. Until then, sampling
and implementation remain unauthorized.

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

Define the complete factor-base digest as

```text
FB_DIGEST = SHA256(
  ASCII("EXP-SGCP-SECANT-REP-001|FACTOR-BASE|v6") || 0x00 ||
  FBE(p) || FBE(a) || FBE(b) ||
  FBE(x_0) || FBE(y_0) || ... || FBE(x_(B-1)) || FBE(y_(B-1))
).
```

The points use canonical source-label order and the same fixed `FBE` width
defined below.

For control index `c in 0..30`, rank each witness with:

```text
SHA256(
  ASCII("EXP-SGCP-SECANT-REP-001|HASH-CONTROL|v6") || 0x00 ||
  U32BE(c) ||
  U32BE(width) ||
  FB_DIGEST ||
  FBE(p) || FBE(a) || FBE(b) ||
  FBE(x_R) || FBE(y_R) ||
  FBE(x_i) || FBE(y_i) ||
  FBE(x_j) || FBE(y_j)
)
```

Here `width=ceil(bit_length(p)/8)` and every `FBE` value is exactly `width`
unsigned big-endian bytes. Endpoints are first sorted by canonical affine point
tuple. The least `(digest,endpoint_1,endpoint_2)` wins. Digest ties are retained
as a diagnostic and resolved by endpoint tuples. Curve, complete factor-base,
and fiber identity are therefore bound through canonical point content;
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

- at least two eligible vertices for the candidate and every control at both
  decision caps, so every registered conflict density has nonzero denominator;
- at least eight nonsingleton fibers;
- total choice entropy
  `sum_R log2(|W_R|)` at least eight bits, reported as the exact product
  `prod_R |W_R| >= 256` rather than a floating approximation;
- candidate/formal-lex Hamming distance at least
  `max(4,ceil(nonsingleton_count/5))`;
- at least 16 distinct hash-control tables;
- at least eight distinct complete control objective vectors.

Formal-lex selects the least canonical source-label pair `(i,j)` in every
nonsingleton `W_R`. Hamming distance is the number of nonsingleton fibers where
the candidate and formal-lex choose different unordered affine endpoint
multisets.

For one control, its complete objective vector is the canonical JSON array

```text
[
  [R_half, constrained_half, public_edges_half, retained_d4_half, maxima_half],
  [R_three_quarter, constrained_three_quarter,
   public_edges_three_quarter, retained_d4_three_quarter,
   maxima_three_quarter]
]
```

using the exact five objective fields at `floor(q/2)` and `floor(3q/4)`.
Distinct vectors mean distinct canonical JSON bytes; controls are not pooled by
cap.

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

For cap `c`, chart `u`, curve seed `s`, and factor-base seed `f`, write
`SUP(c,u,s,f)` for strict support rank `1/32` and `CON(c,u,s,f)` for strict
conflict-density rank `1/32`; define `BOTH=SUP and CON` on one cell.

Define `REPL(X,c,U)` to mean that there exists a set of at least two curve seeds
such that, for each selected curve, at least two factor-base seeds satisfy
`X(c,u,s,f)` for every `u` in chart set `U`. Thus all quantifiers use the same
cap and the required factor-base seeds may differ by curve.

Apply this ordered decision tree exactly once:

1. `INVALID`: malformed output or a schema, arithmetic, semantic, embedding,
   accounting, or independent-verification mismatch is confirmed. This is not
   evidence against the mathematical hypothesis.
2. `INCONCLUSIVE`: the matrix is partial or a resource, optimizer, process,
   publication, or infrastructure failure prevents a complete valid result.
3. `SCOPED_NEGATIVE_VACUOUS`: any registered nonvacuity gate fails.
4. `PASS_PROMOTE`: for one `c` in `{1/2,3/4}`,
   `REPL(BOTH,c,{1,-1,2,3})` holds.
5. `SCOPED_NEGATIVE_CHART`: for one `c`, `REPL(BOTH,c,{1})` holds, but step 4
   does not.
6. `SCOPED_NEGATIVE_MECHANISM`: for one `c`,
   `REPL(SUP,c,{1,-1,2,3})` holds but step 4 does not.
7. `SCOPED_NEGATIVE_NO_SIGNAL`: the complete valid matrix reaches none of the
   prior outcomes.

Steps are precedence-ordered and select exactly one terminal outcome.

## Controls

1. Regression control: replay the exact registered `EXP-SGCP-EMBED-001` fixture
   and its frozen objective receipt before new results.
2. Synthetic representative positive control: a frozen abstract two-fiber
   fixture assigns canonical slope labels so least-slope selection produces the
   one uniquely optimal representative table. Candidate and 31 control tables,
   complete expected objective vectors, and the exhaustive oracle distribution
   must be frozen before source implementation. The producer must derive the
   known-winning table through the candidate rule, not receive it as an input.
3. Invariant negative control: all fibers singleton, so every compiler must
   produce byte-identical tables and objective vectors.
4. Exhaustive tiny control: enumerate every representative table on one frozen
   multiplicity-rich toy fixture and reproduce the full exact score
   distribution.
5. Coordinate controls: all four preregistered `u` chart encodings above, with
   no best-chart selection. For each chart, hash the canonical transformed
   curve, sorted factor base, source labels, and complete `W_R` fibers. Report
   distinct fixture digests and their multiplicities. In particular, do not
   describe `u=-1` as an independent perturbation when its induced fixture
   digest duplicates another chart.
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

Obtain fresh independent theory and red-team review of v6 before implementation
design. The bounded citation search is complete; broader search gaps continue
to block a novelty claim, not properly scoped design work.
