# Experiment Contract: EXP-SGCP-EMBED-002, version 18

## Claim status

`HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.
The experiment is `review_required`; curve-family and canonical execution are
locked at zero generated V18 curve-family density rows and zero canonical runs.
Seventeen historical V1 development rows and one historical development run
manifest remain immutable non-V18 evidence.

## Hypothesis

At least one fixed coordinate predicate family, composed with the frozen
lexicographically least degree-two representative compiler, preserves
nonvacuous structured-embedding support across generated 5-8 bit curves and
improves the exact retained-support frontier over four hash-ranked x-fiber
controls at one same constrained-label cap fraction across strata.

This is a predicate-plus-compiler hypothesis. It is not an invariant of the
factor base or curve.

## Null hypothesis

On one complete valid exact matrix, no fixed coordinate-family and cap-fraction
pair simultaneously passes the full-cap persistence and matched-null advantage
rules below.

Missing rows, unresolved optimization, resource exhaustion, invalid controls,
or implementation and verifier failures are `INCONCLUSIVE`, not evidence for
the null.

## Mathematical object

For each accepted prime-order curve `E(F_p)` and even factor-base size `B`, a
predicate selects `B/2` two-point x-fibers. The factor base `F` contains both
signs above every selected x-coordinate.

The frozen compiler enumerates all degree-two multisets over `F`, groups them
by EC output, discards the identity output, and retains the lexicographically
least formal witness in every remaining output class. The complete
representative table, compiler identifier, and table digest are public.

Pairs of these representatives induce degree-four formal maxima. A maximum is
individually eligible exactly when EC evaluation is injective on its downward
closure. Two eligible maxima conflict exactly when evaluation on the union of
their downward closures is noninjective. For this fixed construction, a set of
maxima is admissible exactly when it is independent in that pair-conflict
graph. The verifier reconstructs individual rejections, first collisions,
eligible universe indices, and pair-conflict first collisions.

For an admissible selected set `S`, let `A4(S)` be the EC evaluations of its
degree-four maxima and define

```text
R(S) = |{P + Q : P,Q in A4(S), P <= Q}|.
```

The final join and `R(S)` are private audit data. The public partial operation
must contain no `A4 x A4` edge.

## Source interface

Every constrained coordinate label must have exactly one formal source in an
emitted public label-to-formal table. The verifier independently reconstructs
that table and its digest. The table is explicit fixed-row advice, and its
serialized bytes are charged inside the public model and each nested cap
receipt.

The legacy `source_recovery` boolean records sorted formal normalization only.
Version 18 interprets source recovery through
`source_recovery_via_public_table`; it does not treat normalization as an
inversion algorithm.

## Optimizer contract

For curve order `q`, use the deduplicated increasing caps

```text
floor(q/4), floor(q/2), floor(3q/4), q.
```

At every cap `C`, require `constrained_count(S) <= C` and use this exact
lexicographic objective:

1. maximize `R(S)`;
2. minimize constrained labels;
3. minimize public nonidentity edges;
4. maximize retained degree-four maxima;
5. choose the lexicographically least maximum list.

The per-cap producer node cap is `2,000,000`. The bound is the minimum of group
size, the global pair-output union, and the incumbent support plus a
conflict-clique-cover pair-capacity bound.

Every canonical cap cell must satisfy all of the following:

- `primary_exact=true`;
- `full_objective_exact=true`;
- lower bound equals upper bound;
- `absolute_gap=0`;
- no remaining or serialized live frontier;
- the frontier digest equals the SHA-256 digest of the empty JSON list;
- termination is `full_objective_proved`;
- deterministic verifier replay matches every objective and search field;
- a separately written depth-first primary proof finishes and matches the
  optimum.

Outside frozen B4, the primary optimum is independently proved while the
secondary constrained-count, public-edge, retained-maxima, and lexical fields
are replay-confirmed by a structurally similar verifier. The standalone frozen
B4 oracle independently proves all five fields. One unresolved primary or
secondary cell invalidates the entire 672-cell matrix. Gap-bearing cells remain
useful only as abstract optimizer controls.

## Curves and provenance

- q bit sizes: `5`, `6`, `7`, `8`
- curve seeds: `101`, `211`
- accepted model: `y^2 = x^3 + ax + b` over prime `p > 3`
- exact prime group order `q` with the requested bit length
- reject duplicate candidates, singular curves, wrong-bit or nonprime q,
  trace zero, anomalous trace one, `j=0`, and `j=1728`
- generator: least nonidentity affine point in canonical order
- frozen regression: `p=19,a=2,b=9,q=23,G=(0,3)`

The sampler is deterministic and generated, not statistically random. It must
record every draw and every applicable rejection reason. Duplicate draws are
retained explicitly and still record all mathematical reasons. Reason order is
`duplicate_candidate` first when applicable, followed by `singular`, or by
`wrong_q_bit_length`, `nonprime_group_order`, `trace_zero`,
`anomalous_trace_one`, `j_zero`, and `j_1728` in that order. The verifier
independently rederives the prime list,
hash-derived `(p,a,b)`, complete rejection transcript, accepted curve,
invariants, generator, and digest. The eight accepted `(p,a,b,q)` records must
be distinct across bit-seed pairs.

The frozen regression is implementation evidence only and is not a family
instance.

## Predicates

Every predicate selects exactly `B/2` admissible roots and includes both signs.

- `least_x_interval`: canonical integer x order.
- `mobius_interval`: `(u*x+v)/(x+w) mod p`, using the first nondegenerate
  domain-separated hash-derived map and deterministic pole removal.
- `two_mobius_union`: alternate through two independently derived Mobius
  rankings, skipping per-map poles and duplicate selected roots until full.
- `hash_x_null`: domain-separated SHA-256 ranking with exact replicate in
  `{0,1,2,3}`.

Coordinate rows require `null_replicate=null`. Hash-null rows require one exact
integer replicate in the frozen range. The verifier rederives every map,
nonce, determinant, ranking, pole list, alternating position, hash value,
selected root, root polynomial, point, sign pair, and selection digest.

## Canonical ordering and exact JSON types

All factor points are reduced affine coordinates sorted by `(x,y)`. Their
formal indices are zero-based, and every formal tuple is nondecreasing. When
formal degrees are mixed, shorter tuples precede longer tuples and integer
tuple lexicographic order breaks ties. EC points are ordered as identity first,
then affine `(x,y)`. Public point labels are exactly `O` for identity and
unsigned decimal `x:y` for affine points, without leading-zero variants.

Least-x ranks by integer `x`. A Mobius predicate ranks by `(score,x)` after
excluding poles. The two-map predicate alternates map 0 then map 1, preserving
each map order while skipping selected duplicates. Hash-null ranks by
`(64-character lowercase SHA-256 hex digest,x)`. The representative compiler
chooses the lexicographically least nondecreasing formal tuple for each
nonidentity EC output. These conventions are emitted as a public ordering
contract with digest
`8114bd7d1822578e3d1453126968964da213775c6f12f86c764413f737212359`.

V18 key sets and value types are closed throughout rows, documents, summaries,
family gates, nested integrity/accounting receipts, verification reports,
publication receipts, and publication results. JSON Boolean, integer, float,
string, list, object, and null roles are exact. In particular, `false` is not
integer zero, `-0.0` is not integer zero, and an equal-valued float is not an
integer receipt. Refreshed byte and document digests do not excuse a type
mismatch.

The V18 verifier accepts only the V18 document schema. V1-V17 schemas are
explicitly rejected without row verification. Each receipt contains an ordered
phase ledger from actual control flow. Aggregate row/cap phases carry expected,
completed, and failed unit counts and become independent checks only after all
registered units pass.

Path-based `verify_document` is the sole evidence-bearing API. Public direct
legacy-row and density-row verification entry points return invalid before any
curve, graph, replay, or proof helper. Internal row/document semantic helpers
also require the active process-local path permit; production-module test
wrappers cannot create that permit. Repository tests deliberately inject the
internal sentinel through test-file introspection, are non-evidence, and create
no exported permit factory. Every public path call creates fresh actual-work,
reservation, and registered-curve-cache state and restores any outer state on
return. Each state is bound to its creating thread, marked closed before the
prior context is restored, and protected against direct path-worker re-entry by
an invocation-local worker token. This isolates successive, concurrent, nested,
exceptional, copied-context cross-thread, and stale copied-context public-call
behavior. It is not a hostile same-process Python sandbox, and same-thread
internal monkeypatching or introspection remains out of scope. Public producer `generated_curve` and
`build_legacy_row` calls raise, and `build_density_row` admits only the exact
frozen p=19 B4 control before factor-base work.

The verifier opens the final input path component with no-follow and nonblocking
flags, requires a regular file, and rejects an initial `st_size` above 256 MiB
before allocation or reading. It fills one exact-size bytearray directly,
incrementally hashes those bytes, and requires stable file identity plus an
exact completed length. Before JSON object construction, an ASCII lexical
preflight rejects insignificant whitespace, more than 2,000,000
scalar/container/string tokens, nesting above depth 64, raw string tokens above
8 MiB, and scalar tokens above 1,024 bytes. The same buffer is then strictly
ASCII-decoded and cleared before standard JSON parsing with duplicate-key and
nonfinite-number rejection. Parent input path components may traverse symlinks;
the receipt states this policy. The parsed object graph is limited to 2,000,000
nodes, depth 64, and 8 MiB per string or key. Diagnostics are normalized to the
top level and limited to 256 items, 65,536 ASCII bytes total, and 2,048 bytes per
item. Reflected document digests are either exact lowercase SHA-256 values or
null. Reflected input-path metadata is limited to 4,096 ASCII bytes or replaced
by a bounded omission marker. The complete serialized verification report,
including its size receipt and hash, is limited to 8 MiB. Only B in
`{4,6,8}`, the exact frozen association or eight canonical `(bits,seed)`
associations, the source-owned frozen 100,000-node replay cap, the source-owned
canonical 2,000,000-node replay cap, and an exact primary-proof budget in
`0..5,000,000` are admitted.

The finite V18 output-path input domain is an exact `str`, a `pathlib.Path`, or
an `os.PathLike` whose `__fspath__` result is an exact `str`. Byte strings,
byte-valued path-like objects, string subclasses, null/unsupported objects,
empty strings, embedded NUL bytes, relative strings, terminal `/`, terminal
`/.`, explicit `..` components, and the distinct POSIX `//` anchor reject
before `Path` construction or absolute normalization. A `Path` object cannot
preserve a terminal separator or terminal `/.` erased by its own constructor,
so those raw classes are controlled with exact strings.

The verifier and producer CLI parsers retain `--output` as the exact
Python-decoded `str`; they do not construct `Path` first. Verifier `main`
preflights that string before input verification and passes the same string to
the writer. This preserves terminal `/` and terminal `/.` for rejection. It
does not preserve or classify raw argv bytes before Python, shell, or OS
decoding.

Calling `os.fspath` may execute arbitrary caller-provided `__fspath__` code
before the returned object can be classified. Side effects created by that
caller callback are outside the verifier-created no-destination guarantee. The
guarantee begins after `os.fspath` returns and applies to inert rejected inputs
and verifier-created filesystem effects. Controls demonstrate both a
string-valued callback with a caller side effect and a byte-valued callback
that creates its own candidate before rejection.

Ordinary internal `.` components and internal runs of separators are normalized
aliases. On the controlled POSIX runtime, any run of three or more leading
separators collapses to the ordinary `/` anchor; the controls cover the
three/four boundary and a larger representative. Admission then requires a
nonroot destination below the development root. Equivalent admitted spellings
name one destination; raw spelling preservation is not claimed. The descriptor
walker invokes the same raw grammar and independently enforces normalized root
containment before opening every root-relative parent no-follow from the
development root. Before writing, both the destination and deterministic
adjacent receipt name must be absent. Data and receipt publication remain
no-overwrite:
descriptor-relative exclusive rename or same-directory hard link where
supported, with a forced-`ENOTSUP` descriptor-relative `O_EXCL` fallback. The
real hard-link branch is controlled on a test-only hard-link-capable temporary
root because the mounted development root may not support links; this is branch
evidence, not a filesystem-support or durability claim.

The data path alone is never accepted evidence. A completion receipt binds a
random 256-bit publication identifier, exact destination basename,
development-root-relative destination path, payload byte count, payload
SHA-256, experiment, protocol, and its own canonical digest. A stale data or
receipt name blocks retry before new data is created. Concurrent attempts may
race, but only the identifier in the complete winning pair is accepted.

If an ordinary synchronous `Exception` escapes after receipt publication
begins, the writer snapshots and validates the terminal pair against the exact
expected identifier and payload. It returns accepted only for that exact pair
and records a reconciliation warning; a different, absent, partial, malformed,
or mismatched attempt preserves the failure. An observed direct-write
nonregular or wrong-size inode is fatal. Unavailable metadata or durability
checks may become warnings only when final exact pair validation succeeds.
`KeyboardInterrupt`, `SystemExit`, process termination, power loss, memory
exhaustion, and hostile same-process monkeypatching are outside this
reconciliation guarantee.

The production validator uses bounded descriptor snapshots. A standalone
test-only parser independently checks exact keys and types, canonical encoding,
self-digest, relative destination, publication identifier, payload size, and
payload digest without calling production `publication_status`. Neither
validator authenticates against a hostile same-user filesystem actor, and
their sequential data/receipt snapshots are not pair-atomic. A logical content
commit is not proof that every durability syscall succeeded; a future runner
must preserve warnings and use an immutable external artifact store.

Before generic JSON traversal, V18 applies source-sized bounds to document and
row roots, registered parameters, the nested family gate, Mobius maps,
alternating positions, rejection reasons, root polynomials, formal witnesses,
edge/source tables, exact-empty frontiers, and per-cap byte receipts. Before
row semantics it validates complete key sets and exact types; row, nested, and
document digests; nested byte accounting; protocol, scope, and grid
association; the frozen static transcript; cap schedule; objective; masks;
source-owned node caps; and the reconstructed document summary/family gate. No
canonical curve derivation or reservation-dependent semantics occurs before
this authentication. V18 then reserves separate worst-case totals for
registered prime candidates, curve draws and hashes, predicate hashes, frozen,
semantic, and primary point enumerations, expansion cells, graph candidate
evaluations, eligible conflict checks, eligible pair-output cells, replay nodes,
independent primary nodes, both replay caches, both primary caches,
retained-model calls, and retained-model cells. Any over-limit reservation is
invalid and `INCONCLUSIVE`.

Rows are verified sequentially and stop at the first invalid row. Every raw
work charge must be an exact positive integer; Boolean, zero, negative, float,
and other amounts fail before counter mutation. Replay,
retained-model, and primary-proof exceptions preserve earlier cap receipts,
the trusted reservation, invocation-locally charged work already spent inside the
failing cap, the failed unit count, and `actual_work_complete=false`. Replay
and primary nodes are charged as explored and cache entries as inserted;
graph and expansion work is charged inside each executed loop, and
retained-model cells are charged as evaluated. Every completed row must exactly
report its reconstructed candidate evaluations, eligible-pair conflict checks,
eligible-squared pair-output cells, and degree 1, 2, 4, and 8 multiset expansion
cells. Every completed path must also exactly report the registered curve-cache
lookups/misses and the frozen, semantic, and primary point enumerations implied
by its authenticated row/cap grid. Only after all rows pass semantic curve and
factor-base reconstruction, the verifier derives exact completed totals for
registered prime candidates, curve draws, curve hashes, registered-curve point
enumerations, and predicate hashes from those verified public transcripts. The
canonical transcript expectations are respectively `480`, `112`, `336`, `218`,
and `4,218`; the frozen expectations are zero. Any one-unit suppression or
overcharge is invalid while the completed-work flag remains true. Interrupted
predicate reconstruction preserves partial work and sets
`actual_work_complete=false`, so completed equality is not claimed. Complete
actual work must also be dominated by the source-owned reservation or the
report is invalid. An otherwise successful report must match the exact V18
phase sequence, including completed provenance/predicate equality, with every
unit phase complete and passed. Ordinary authenticated semantic mismatches may
stop early with counters for the work actually executed. The
verifier source SHA-256 is frozen at module load for diagnostics only; it is
explicitly not executed-code attestation and is not reopened while building a
report.

## Canonical matrix

The exact order is:

```text
for bits in 5,6,7,8:
  for seed in 101,211:
    for B in 4,6,8:
      least_x_interval
      mobius_interval
      two_mobius_union
      hash_x_null replicate 0
      hash_x_null replicate 1
      hash_x_null replicate 2
      hash_x_null replicate 3
```

This is exactly 168 rows and 672 cap cells. Missing, extra, duplicate,
reordered, wrong-cap, wrong-node-budget, internally inconsistent, or
cross-seed-duplicate rows invalidate the document before interpretation.

## Frozen family gate

All arithmetic is exact rational arithmetic.

### Full-cap persistence

For each coordinate family and bit stratum, take the exact median of the six
full-cap `retained_to_balanced_raw` ratios from two seeds and three B values.
The family passes persistence only if all four medians are at least `1/4`.

### Matched-null advantage

For every curve-B pair and cap fraction `1/2` or `3/4`, take the exact
arithmetic mean of the middle two of the four precommitted null supports.
Duplicate null selections and equal support values remain in the four-value
sample; there is no resampling or deduplication.

Subtract this null median and `max(1,ceil(q/20))` from coordinate support. A
bit stratum passes when the exact median of its six threshold margins is
nonnegative. A fixed family-cap pair passes when at least three bit strata pass
and at least 18 of all 24 unthresholded coordinate-minus-null-median
comparisons are positive.

The gate tests six preregistered family-cap pairs and reports all winners. One
same family and one same cap fraction must pass across strata; half-cap evidence
cannot be spliced with three-quarter-cap evidence.

The complete gate also emits the preregistered negative classification.
`COLLAPSE` applies exactly when every coordinate family has full-cap median
retention below `1/10` in at least three bit strata. A complete FAIL that does
not meet that condition is `WEAKEN_OR_REJECT`; a PASS has no negative outcome.

## Expansion and energy

For degrees `1`, `2`, `4`, and `8`, report exact support under degree-d
factor-base multisets.

`formal_multiset_collision_energy` squares output multiplicities when each
multiset is counted once. `ordered_tuple_additive_energy` first weights each
multiset by its multinomial number of orderings and then squares the resulting
output multiplicities. The verifier independently reconstructs both measures,
their witness totals, maxima, and histograms.

`balanced_raw_final_support` is the final pair support of the compiled balanced
A4 universe. `eight_fold_support` is the exact support of all degree-eight
factor-base multisets. Both denominators appear beside retention ratios.

## Accounting boundary

Version 18 retains the V3 accounting boundary and emits only independently
reconstructible combinatorial cells, including multiset evaluations,
representative and parent-pair counts, graph checks, pair-output cells,
optimizer nodes, bound calls, source-enforced optimizer and full-model cache
entry counts, selected maxima, public edges, source-table entries, and
final-pair cells. These are structural work, not CPU instructions,
allocator-memory bytes, field-operation totals, or a complete end-to-end cost.

Every cap creates a fresh model cache, so cap-local search receipts do not
depend on cap order. Public-model, private-audit, row-payload, and nested
per-cap canonical-JSON sizes are recomputed by the verifier. The nested sizes
overlap the row-level objects and are explicitly nonadditive.

Producer row and cap wall times are observational and checked only for finite,
nonnegative nesting. The producer makes no peak-memory claim. Any future
canonical execution must obtain generator and verifier wall time, peak RSS,
serialized output size, and memory traffic from the trusted external runner.
Verifier work must be reported as a separate role cost. V18 path receipts
record actual registered-curve cache behavior, prime candidates, curve and
predicate hashes, point enumerations, expansion cells, graph candidate
evaluations, eligible conflict checks, eligible pair-output cells, replay and
proof nodes, both replay caches, both primary caches, retained-model calls and
cells, plus whether an exception left those counters incomplete. The one-buffer
snapshot and lexical preflight bound source-copy amplification but do not claim
peak RSS, parser-object bytes, allocator retention, CPU, or wall time. Python
object overhead, process count, disk, I/O, and memory bandwidth remain outside
the in-process receipt and must be measured externally before execution.

This protocol cannot support a fixed-curve preprocessing crossover claim.

## Controls

1. Reproduce the frozen predecessor and inherited hash-bound controls.
2. Exact-compare pair-conflict independence with direct closure on every
   frozen B=4 subset.
3. Exact-compare both optimizers with exhaustive abstract fixtures, including
   density and lexical ties.
4. Force and verify a nonzero optimizer gap at node cap zero.
5. Independently recount all four expansion degrees and both energy measures.
6. Independently rederive generated curve and predicate provenance.
7. Exercise singular, trace-zero, anomalous, `j=0`, `j=1728`, duplicate, and
   multi-reason draw records, including duplicate-plus-mathematical reasons.
8. Reject illegal replicate bindings and mutations to Mobius nonce, ordering
   contract, objective order, representative table, source table, exactness,
   structural work, and bytes after refreshing enclosing digests.
9. Reject scalar-material additions and extra nested transcript fields under
   the closed schema.
10. Reject Boolean/integer/float aliases in optimizer, graph, axiom, ratio,
    mask, node-cap, wall-time, byte-receipt, summary, and document fields.
11. Verify one frozen V18 document and reject an empty canonical document.
12. Reject missing, extra, duplicate, reordered, wrong-cap, wrong-node-cap,
    inconsistent-curve, and cross-seed-duplicate canonical matrices.
13. Exact-match producer and independent family gates on a synthetic complete
    168-row matrix; both must reject every independently mutated exactness,
    bound, gap, frontier, digest, and termination field.
14. Compare the complete five-field density objective and lexical witness tie
    against both the prior verifier-assisted oracle and a standalone frozen
    B=4 implementation that independently rebuilds EC addition, factor-base
    fibers, representative compilation, ideals, graph conflicts, model costs,
    final support, and every cap winner.
15. Require deterministic invalid receipts for truncated cap schedules,
    out-of-range selected formals, duplicate selected formals, negative caps,
    malformed JSON, nonobject roots, duplicate keys, and out-of-range verifier
    budgets.
16. Relabel a valid V18 body with every V1-V17 schema and require explicit legacy
    rejection with zero row checks and no V18 mathematical check claims.
17. Replace the input path after its snapshot is read and require the receipt
    hash and parsed document to remain bound to the original bytes. Reject
    directories and symlinks before JSON parsing.
18. Reject huge curve bits, nonregistered transcripts, wrong source-owned
    replay caps, repeated invalid frozen rows, and aggregate replay overbudget
    before curve, row, replay, or proof semantics.
19. Compare the complete standalone frozen-B4 factor-base, representative,
    rejection, conflict, graph, selected-mask, formal-family, constrained-label,
    public-edge, source-table, digest, axiom, and cap-winner transcripts.
20. Use hand-derived gate fixtures for the discriminating null multiset
    `[8,8,10,12]`, strict `1/10` collapse inequality, 17 versus 18 positive
    comparisons, two versus three passing strata, fixed-cap anti-splicing,
    every-family COLLAPSE, and noncollapse classification.
21. Compare the standalone oracle's complete candidate and eligible lists,
    including every recursive degree-two parent pair, directly with the
    verifier reconstruction.
22. Keep generated controls at curve-provenance and factor-base scope only;
    construct no generated V18 curve-family density row. Separately construct
    exactly three transient noncanonical frozen legacy semantic rows at
    B=4,6,8, record their digests, and distinguish them from the sole frozen-B4
    density-row/document control.
23. Reject FIFOs without blocking, reject an initially oversized sparse file
    before the first read, reject a final-component symlink, and confirm the
    disclosed parent-component symlink behavior.
24. At a temporarily small exact input ceiling, confirm that one pre-sized
    buffer is used, the exact-ceiling file succeeds, and the first over-ceiling
    byte is rejected before reading. Require the byte buffer to be cleared before
    JSON object construction and reject lexical node, depth, string, scalar,
    whitespace, and non-ASCII amplification before calling the standard parser.
25. Patch frozen and registered curve helpers, replay, and primary proof and
    require zero calls for a bad row digest, wrong objective, nonempty frontier,
    oversized mask, and oversized B-derived public transcript.
26. Inject replay and primary-proof failures on the second cap and after
    nonzero work inside the failing function. Preserve the reservation, all
    observed prior/failing-cap counters, failed unit count, normalized top-level
    error, and `actual_work_complete=false`.
27. Amplify malformed keys and reflected digest values past source ceilings.
    Require bounded count, total bytes, item bytes, and complete serialized
    report size including its integrity fields.
28. Accept exact `1/4` full-cap persistence and reject exact `999/4000` in one
    stratum; freeze the verifier source digest at module load and prove report
    construction does not reopen the source path.
29. Disable both public direct-verification APIs before curve, graph, replay, or
    proof work; reject public generated-curve and legacy-row construction and
    every non-frozen public density-row association before factor-base work;
    require path-based verification for evidence.
30. Reject one-over map, alternating-position, reason, polynomial, formal,
    edge/source-table, frontier, byte-receipt, parameter, summary, and nested
    family-gate containers before generic traversal or mathematical work.
31. Authenticate nested hashes/accounting and reconstruct summary/family gate
    before reservation or semantics.
32. Assert the exact frozen actual-work vector and reservation mapping, then
    under-reserve an otherwise valid path and require invalidation by the
    actual-work dominance phase.
33. Inject failures into the frozen, semantic, and primary point-enumeration
    calls and require each invocation to be charged before failure.
34. Inject a failure after the second graph-candidate, eligible-conflict,
    expansion, and eligible-pair-output charge. Preserve the exact partial
    counter, failed graph/expansion unit, and `actual_work_complete=false`.
35. Suppress one otherwise successful primary-proof phase update and require
    final phase-closure invalidation.
36. Supply an over-report-ceiling caller path with an invalid verifier budget
    and require a bounded invalid receipt rather than an exception.
37. Suppress each graph-candidate, eligible-conflict, eligible-pair-output, and
    expansion charge on an otherwise completed row, then overcharge one
    candidate evaluation; require exact-delta mismatch invalidation while
    preserving `actual_work_complete=true`.
38. Reconstruct all 168 public curve/factor-base transcripts without building a
    density row and require exact canonical provenance/predicate totals
    `480/112/336/218/4218`. Undercharge and overcharge each dimension by one and
    require exact mismatch while completed work remains true; inject a predicate
    interruption and require its partial charge with completed work false.
39. Call every internal legacy-row, density-row, document-value, test-wrapper,
    registered-curve, path-worker, and path-worker-body semantic entry point
    without the active permit/token and require rejection before mathematical
    work.
40. Pass Boolean, zero, negative, float, string, and null work-charge amounts;
    require exact-type rejection and no counter mutation.
41. Overlap two frozen path verifications at the first graph-candidate charge
    and nest one complete verification inside another factor-base
    reconstruction. Require each receipt to equal the serial baseline and no
    active state after return.
42. Inject an escaping public-worker exception and require the inner state to
    be closed and the exact outer context restored. During an authenticated
    callback, reject direct path-worker re-entry, copied-context use from
    another thread, and later same-thread use of the copied closed state.
43. Publish one data/receipt pair and use a standalone parser sharing no
    production status implementation to validate its exact canonical encoding,
    self-digest, root-relative destination, publication identifier, and payload
    binding. Preserve both paths on retry, preserve a race-created orphan,
    reject an output parent symlink, and reject later payload mismatch.
44. Force unsupported-publication direct writes and interrupt first the data
    write and then the completion-receipt write. Classify the first as an
    unaccepted orphan and the second as an unaccepted invalid receipt; prove
    neither terminal path can be overwritten.
45. After complete destination publication, inject directory-fsync failure and
    actual `os.link` success followed by temporary-cleanup failure. Require a
    normal accepted return with structured warnings and a matching receipt.
46. Remove the data while preserving a valid receipt, then retry the identical
    payload. Require preflight failure before replacement data is created.
47. Race two random publication identifiers at one destination. Require one
    accepted exact attempt, one no-overwrite failure, and production plus
    standalone attribution only to the winning identifier.
48. Inject an ordinary synchronous exception immediately after receipt commit
    through exclusive rename, actual hard link, and forced direct `O_EXCL`
    publication. Require exact-attempt reconciliation and a structured warning.
49. Make a direct receipt write return after writing one byte too few. Require
    the observed inode-size mismatch to fail closed and both validators to
    classify the terminal pair as unaccepted.
50. Apply the finite raw-path grammar across verifier and producer CLI parsing,
    verifier preflight ordering, the public writer, receipt-path, status,
    standalone status, and private descriptor walker. Require terminal `/` and
    terminal `/.` to survive CLI parsing and verifier `main` to reject them
    before input verification or writing. Admit exact
    absolute strings, `pathlib.Path`, custom exact-string `os.PathLike`, internal
    dot and repeated-separator aliases, and representatives with three, four,
    and seven leading separators. Reject exact leading `//`, explicit `..`,
    relative in-root and escaping strings, terminal `/`, terminal `/.`, the
    development root, ordinary outside paths, empty and NUL-bearing strings,
    direct bytes, byte-valued path-like objects, string subclasses, and null
    objects before normalization. Require every inert rejected class to create
    no verifier destination. Separately exercise side-effecting string-valued
    and byte-valued `__fspath__` callbacks to delimit caller-created effects
    before return-value validation. Publish through the combined raw alias and
    require production and standalone attribution through every admitted
    spelling. Separately
    require production writer/status and descriptor traversal to reject a
    symlinked parent; the standalone parser remains outside the
    filesystem-race claim.
51. Recompute the non-self-referential review-surface entry inventory from
    exact paths, exact flat-directory selectors, the static experiment rule,
    and four exact historical-development paths. Reject control-bearing or
    non-ASCII selected paths, require regular nonexecutable `100644 blob`
    entries, and hash sorted NUL-delimited mode/type/path records. Require the
    exact entry count and digest, all entries present, no predicted commit or
    tree, exact-commit/tree reviewer checks, zero generated V18 curve-family
    density rows, zero canonical runs, explicit preservation of 17 historical
    V1 development rows and one historical development run manifest, and zero
    launch-plan or execution authority.
52. Re-sign a receipt with a different valid random identifier and confirm
    ordinary unkeyed status accepts it while exact-attempt reconciliation
    rejects it. Re-sign a wrong relative path and weak Boolean byte count and
    require both production and standalone validators to reject them.

## Positive criterion

After a separately approved canonical launch, all controls, 168 rows, and 672
cap cells must be valid and exact. At least one fixed family-cap pair must pass
both full-cap persistence and matched-null advantage exactly as frozen above.

This would be a toy coordinate-structure signal authorizing a larger compiler
and curve-family replication. It would not authorize an ECDLP claim.

## Falsification and narrowing

On one complete valid exact matrix, failure of every fixed family-cap pair
weakens or rejects this exact predicate-plus-compiler hypothesis. If every
family has full-cap median retention below `1/10` in at least three strata,
record the narrower `COLLAPSE` negative.

An axiom failure, provenance mismatch, optimizer disagreement, mismatched
control, malformed type, scalar-material leak, resource exhaustion, or
incomplete matrix invalidates the evidence and yields `INCONCLUSIVE`. Those
events do not falsify the mathematical hypothesis.

Neither result closes coordinate-specific SGGM embeddings in general. The next
positive question would be whether another representative compiler, formal
quotient, model transformation, or source-recoverable non-tree operation
changes the measured collision geometry.

## Budgets and stopping

Version 1 consumed 17 of 18 historical development curve rows and left one
historical development run manifest. Version 18 preserves those exact
historical artifacts, creates zero generated V18 curve-family density rows and
zero canonical runs, and authorizes no additional curve-family row. Unit,
abstract graph,
generated-curve provenance, generated factor-base, one frozen p=19 B4
density-row/document control, and exactly three transient noncanonical frozen
legacy semantic rows at B=4,6,8 are allowed. A generated curve-family density
row is not allowed.

Canonical budget remains:

```text
maximum_runs = 0
wall_clock_seconds_per_run = 0
total_cpu_hours = 0
maximum_memory_gb = 0
```

Fresh independent theory, accounting, and red-team GO on one committed V18
snapshot is necessary but not sufficient to launch. A separate hash-complete
execution plan and coordinator approval must follow before any budget change.

`review-surface-manifest-v18.json` binds review scope without predicting or
self-hashing a commit. Its finite entry rules and NUL-delimited
mode/type/path digest cover the static SGCP record tree, four exact historical
development artifacts, the constitution, normative repository documents,
ledgers, harness schemas and core, repository tests, and inherited SGCP
controls. The exact reviewed Git commit and tree bind the bytes. Each reviewer
must independently verify HEAD, parent, tree, detached cleanliness, inventory
presence, zero generated V18 curve-family density rows, zero canonical runs,
and the disclosed historical V1 evidence.

## Claim boundary

No exponent, relation yield, matrix rank, factor-base logarithm, individual
descent, preprocessing crossover, memory-bandwidth advantage, rho improvement,
deployment relevance, or prime-field ECDLP result is in scope. Fixed B values
are finite stress probes, not an `n^(1/5)` schedule.

## Reproduction command

No canonical reproduction command exists while `maximum_runs` is zero. The
current producer refuses both development family rows and canonical execution;
only unit, generated-factor-base, one frozen-fixture B4 density control, and
the disclosed transient B4/B6/B8 legacy semantic controls are authorized for
V18 preflight.
