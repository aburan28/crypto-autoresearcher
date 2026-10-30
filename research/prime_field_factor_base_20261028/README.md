# Prime-field factor-base continuation

2026-10-28. **Implementation and software validation**, not a scientific run,
independent research review, novelty claim or performance measurement. Requested
scope: build the four follow-ups from the source survey and check them into Git.

## Delivered interfaces

1. `src/crypto_autoresearcher/index_calculus/relation_quality.py` supplies exact
   sparse affine elimination with original-row combination certificates,
   projective **affine** equation deduplication (including RHS), complete right
   kernels, target-combination identification and verified scalar recovery.
   Inconsistency is fatal and leaves the previously accepted system unchanged.
2. `cancel_outside(M,B,U,b)` eliminates outside-point columns before scoring
   information on the existing base. Every output equation carries weights on
   the partial rows. The gain is
   `rank([[M,0],[B,U]]) - rank(U) - rank(M)`. No outside logarithms are assumed.
   `rank_per_cost` uses exact counted integer costs; unmeasured/zero cost yields
   no rate. Rates with different units or accounting boundaries are incomparable.
3. `prym_completion.py` extends the historical Context with legitimate affine
   x=0 source/constraint points. Infinity, repeated interpolation coordinates,
   exceptional poles and nonsmooth residuals retain their checks. The curve,
   generator, factor base, source order and cubic construction are unchanged.
   The historical producer/checker source bytes are not edited.
4. The additive F1 `driver.py` and `reference.py` complete the prepared
   exterior-cube extractor with all three coordinate partitions, rational
   recovery, sign/subgroup checks, finite-resultant/point-sum oracle and an
   explicitly enumerative arity-four control. The operator dimension guard is
   checked before allocating matrices. All-equal and two-equal solutions are
   retained; unknown extraction is never treated as an empty set.

`check_prym.py` replays the complete finite branch stream using the historical
separate arithmetic lane and checks exact rows, status/digest totals, public
projection, affine rank and a complete kernel. It imports neither the new
collector nor producer arithmetic. This is a software cross-check, not a
separately staffed scientific review.

## Read-only retained-matrix diagnostics

Set `PYTHONPATH=src:.` from the repository root. A diagnostic input contains:

```json
{"modulus":7,"columns":2,"rows":[[1,1]],"rhs":[3],
 "targets":[[1,1],[1,0]],
 "partials":{"B":[[1,0],[0,1]],"U":[[1],[-1]],"rhs":[1,2]}}
```

```sh
python -m crypto_autoresearcher.index_calculus.quality_cli retained-matrix.json
```

The input rows must already have passed the applicable curve/witness verifier.
This command cannot establish that provenance. Identifiability means
`v*N=0` for a complete right kernel N; the returned row weights also certify
`v=sum(weights[i]*M[i])` and its value. It does not require full base rank.
`recover_target` handles `v*z=offset+target_coefficient*k`, rejects a zero
target coefficient and verifies the returned scalar against the public points.
It does not construct a cheap natural target decomposition by itself.

## Scientific entry points and admission

```sh
python research/prime_field_factor_base_20261028/run_prym.py \
  --inputs FROZEN_INPUTS --protocol NEW_FROZEN_PROTOCOL \
  --release COMMITTED_RELEASE --out FRESH_OUTPUT_DIRECTORY
python research/p256_factor_base_parallel_20261026/tracks/f1/driver.py \
  --inputs research/p256_factor_base_parallel_20261026/tracks/f1/inputs.json \
  --protocol NEW_FROZEN_PROTOCOL --release COMMITTED_RELEASE \
  --max-dimension 560 --out FRESH_OUTPUT_DIRECTORY
```

These are launch syntax, **not commands executed in this change**. Existing
October 26 protocols do not authorize changed code. A new Coordinator protocol
and committed release must bind the full source/input dependency closure,
`source_commit`, `source_sha256`, `input_sha256`, exact `parameters`, canonical
`protocol_sha256`, `interpreter_sha256`, `execution_authorized` and the prior checkpoint receipt.
The shared admission helper checks committed bytes and invokes the existing
real S3 checkpoint gate; it has no skip flag. The new Prym paired parameters
are `{"arms":["historical_nonzero","completed_zero"]}`; F1 uses
`{"max_dimension":560}`. Admission refusals occur before output creation.
Normal native experiment ownership, resource supervision, export/review and
resume/archive obligations still apply; these library entry points do not
replace the lab's experiment supervisor or constitute an execution release.

The paired Prym launcher retains accepted witnesses as they arrive and explicit
failure records. It evaluates the candidate equations against the baseline
kernel. Direct collector calls remain restricted to marked p<=211 software
fixtures unless the admitted launcher supplies its capability. Its operation
vector is partial accounting, excluding the independent replay; no total S or
IC/rho comparison is supplied.

## Literature and source review

- Petit, Kosters, Messeng, *Algebraic approaches for the Elliptic Curve Discrete
  Logarithm Problem over prime fields* (PKC 2016), sections 2.4 and 3.1–3.5:
  <https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf>. Retrieved and
  read in this session. Composed low-degree membership maps are prior work;
  section 3.2 explicitly charges the relation solver and linear algebra. A
  short membership circuit supplies neither a cheap solver nor a rho advantage.
- Historical source pin `cdd2150922211f180ab3d8c3f3b248356c78f025`:
  `research/p256_factor_base_parallel_20261026/tracks/f1/{core,exterior}.py`,
  its derivation and first-pass symmetric S4 coefficients. Reused unchanged.
  The historical depth-four P-256 outcomes remain unknown.
- `research/prym_experiment_design_20261019/implementation/{relations,census,independent}.py`
  and `research/prym_factor_base_width_20261025/{collect_width,check_width}.py`:
  the source and constraint zero guards are the isolated change; independent
  row replay already handles the auxiliary image at x=0 as infinity.
- Latest survey pointer: <https://github.com/isogeny-labs/crypto-autoresearcher/issues/2414>.
  Its October 27 report path was not available on the inspected main checkout;
  issue-reported observations are not represented as locally reverified data.
- No `search_knowledge` connector was available. Repository files and GitHub
  search supplied retrieval; this is an evidence gap, not an absence/novelty proof.

## Validation and limits

`tests/test_relation_quality.py` checks identification against every solution of
small affine systems, verifies row certificates, cancellation rank identities,
inconsistency/shape rejection and public target recovery at deficient rank.
`tests/test_prime_field_continuation.py` compares the complete F1 signed sets
and algebraic states at depths 2–4 on a fixed **p=127 software fixture**, checks
all arity-four partitions, rejects corrupt/missing solutions and guards, and
replays a marked p=101 zero-completion stream with deliberate corruptions.
These tests are not the frozen P-256 or p=4099 panels.

The validation receipt records commands, versions, initial failures and final
outcomes. The first fixture choice lacked enough rational lifts at depth 2;
the software fixture was corrected before the final tests. Broader regressions
initially failed on omitted sparse-checkout fixtures; tracked fixtures were
materialized. No production source was changed to make those failures pass.

The p=4099 width claim, natural unknown-target descent cost and P-256 extractor
performance remain unmeasured. Dense exterior operators still have dimension
`C(2^depth,3)`, not polynomial size in depth; recovery inherits the prepared
p=3 mod 4 assumption and refuses other characteristics. This work makes no
asymptotic, whole-ECDLP, full-rank or speedup claim.

Canonical graph applicability: the historical F1 preparation diagram and
Prym run graphs remain unchanged because their recorded results are immutable.
`src/crypto_autoresearcher/index_calculus/README.md` receives an interface link.
No goal/hypothesis status, existing result, measured bound or IC/rho metric
changes. The new [diagram](diagram.svg) documents implemented data flow;
[report source](report.typ) and [PDF](report.pdf) describe this software delivery.
