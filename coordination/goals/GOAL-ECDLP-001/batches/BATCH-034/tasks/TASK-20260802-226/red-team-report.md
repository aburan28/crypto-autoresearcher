# Independent Red Team report — TASK-20260802-226

## Verdict

**REVISE.** The repaired constant-excess producer bound has a sound core under
the standard encoding-oblivious generic-group model, but the committed package
does not state that model tightly enough and its complete-cost/Pareto artifact
contains binding errors. In particular:

1. equation (1) counts only `P` resident handle records, while the model also
   permits visible-string branching and separately charged non-handle advice;
   the proof never excludes advice derived from the random injection or counts
   all retained encoding-recognition state in `P`;
2. the retry rows do not distinguish rebuilding preprocessing on every attempt
   from reusing one table, despite §7 giving different formulas for the two;
3. `root_mass_output_G` declares `ecdlp_solver: false` but sets the ordinary
   ECDLP comparison to admissible and uses numeric zero where the comparison is
   `not_applicable`.

The first defect blocks the theorem as written. It is repairable by narrowing
and re-proving the model; it is not evidence against the familiar producer
bound in the ordinary generic model. The Pareto defects independently prevent
`PASS`. No experiment, implementation, research-state transition, support,
closure, novelty, SOTA, or breakthrough claim is authorized by this review.

## Snapshot and review boundary

This review used the Coordinator-committed producer snapshot
`79008962c5649785c9b0b60eb8f8a904c0e62890`, whose parent is
`14763e911251898fae4a3d825c97931fe6114bbd`. Read-only Git checks established
that the snapshot is reachable from `HEAD`, changes exactly the four TASK-224
producer artifacts plus the TASK-225 receipt, and that the working copies of
those five paths do not differ from the snapshot.

The reviewed hashes are:

- `repaired-producer-bound.md`:
  `5b0df7c295c77be92614db07511956d1162a8bdb115e401e01570a910c8f561f`
- `proof-obligations.yaml`:
  `18b0ad4fc479b93ce790104c579395e1b02248e867d4fb36806730bf7b6ac1b3`
- `pareto-frontier.yaml`:
  `4dce6196d955048b26a60dc110c16f9b9b81756132f0b24454b3025dc21550dc`
- `provenance.yaml`:
  `e35912850f874efb9d1c9829d82c549bdf89e1f36246b59841eee7081d960d0f`
- `snapshot_commit_receipt.json`:
  `90940d03bd81fcb97a7e3f81c396e453808789e5c69b4db982a17fa1b1f6ddce`

Unrelated pre-existing worktree changes were observed and left untouched.

## Independent reconstruction

### 1. RT-215-C1 and the exact uniform obstruction

Take the zero-operation producer `R=G`. It is correct precisely when
`alpha^d=1`. Since `alpha` is uniform in the cyclic group
`F_r^*` of order `N` and `d|N`, this event has exactly `d` members and
probability `d/N`. The producer has no informative collision except at the
single input collision `Q=G` when `alpha=1`; the other `d-1` successful inputs
do not create a producer collision.

A separate generic-DLP verifier can recover `alpha` using its own generic
operations, handles, comparisons, table, memory, and data movement, then accept
exactly when `R=alpha^d G`. Sound verification therefore does not imply a
producer collision. The producer/certificate lemma rejected by RT-215-C1
remains refuted, and TASK-224 correctly does not restore it.

For `d=N/2`, `R=G` has correctness `1/2` with constant producer work. Thus
constant correctness alone cannot imply rho work uniformly in `d`. This
obstruction is exact. A fixed correctness threshold strictly greater than
`1/2`, or constant excess over `d/N`, is a different statement.

### 2. Fixed transcript, adaptivity, raw strings, and table indices

Under the following standard restriction, TASK-224's coupling is sound:

- advice is chosen independently of both `alpha` and the random injection;
- every encoding or encoding-derived record retained from preprocessing and
  usable to recognize an online handle is counted in the preprocessing state;
- preprocessing oracle responses that remain observable online are included
  in the fixed symbolic state; and
- the random injection is then lazily coupled to the fixed symbolic token
  sequence.

Fixing algorithm coins and fresh symbolic encoding tokens first makes every
raw-string branch, hash result, table index, output index, and later oracle-call
schedule fixed independently of `alpha`. Before a distinct formal-label pair
evaluates equally, each online group label remains `a+bX`; disclosed scalar
multiplication is affine because the disclosed scalar is fixed in that
transcript. Outside scalar collisions, the evaluated distinct scalars receive
an ordered sample of distinct random tokens, so the real and symbolic
transcripts have the same marginal distribution. Adaptivity and arbitrary
visible-string branches do not by themselves add an exceptional event.

This does **not** establish the broader statement currently written. Section 3
allows separately charged non-handle advice but says such advice creates no
collision roots; §4 then fixes advice and tokens without requiring their
independence. If preprocessing may derive a lookup structure, fingerprint set,
or inverse-encoding advice from previously observed random encodings, fixing
that state conditions the future token distribution. A challenge handle that
matches a preprocessed-but-not-counted encoding can select a different branch
without appearing in `C_PO`.

The theorem therefore needs one of two explicit repairs:

1. sample the random injection after encoding-oblivious advice and define `P`
   to include every retained encoding/equality-recognition record; or
2. retain the broader preprocessing model but add total preprocessing oracle
   labels and encoding-derived state to the event/cost bound, with a new
   conditioning argument.

Merely charging a large advice structure in `C_pre` can preserve a final work
lower bound by a case split, but it does not make equation (1), which contains
no advice term, true.

### 3. `P`, `q_g`, `n=q_g+1`, and collision boundaries

With `P` interpreted as the number of distinct retained preprocessing handles
or equality-recognition records, including `G`, the declared boundary is
correct:

- `L_0=X` accounts for the supplied challenge `Q` exactly once;
- each of `q_g` online oracle calls creates at most one new handle;
- an oracle-created output is already one of those slots; and
- an output selected from preprocessing is already one of the `P` records.

Thus `n=q_g+1`. Preprocessing/preprocessing collisions are
challenge-independent and need not enter the alpha-root union. Every relevant
preprocessing/online pair contributes at most one root, as does every
nonidentical online/online affine pair. Hence

`|C_PO| <= Pn` and `|C_OO| <= binom(n,2)`

are conservative. Counting inaccessible resident pairs can only enlarge the
upper bound. Online construction of a constant table does not escape: its
oracle calls are in `q_g`, its results are online labels, and its accesses and
storage must be charged. Free challenge-independent handles are excluded by
ordinary input; if supplied as advice, their construction and storage must be
charged and their records included in `P`.

The unresolved point is the meaning of *resident handle record*. Discarding an
API object while retaining its raw encoding, exact fingerprint, or a lookup
structure that recognizes it cannot reduce `P` for purposes of the root bound.
TASK-224 must say this explicitly. It must also state whether discarded
preprocessing oracle tokens are integrated out or counted; fixing them in
`tau` while omitting their retained consequences from `P` is not sufficient.

### 4. Selected output agreement and the exact union

For a fixed valid symbolic transcript, one output handle is selected. Its
formal label is affine, `h(X)=a+bX`, and

`T_out={x in F_r^*: h(x)=x^d}`.

Because `2<=d<r`, `a+bX-X^d` is a nonzero degree-`d` polynomial, so
`|T_out|<=d`. For `h=1`, equivalently output `G`, equality is attained because
`d|N`. Using this single selected set is correct; unioning all handles' target
sets would charge outputs not selected by the fixed transcript.

Once the transcript coupling is valid, every success lies in

`C_PO union C_OO union T_out`.

Collision roots cover every real branch that can diverge from the no-collision
symbolic branch, and target roots cover correctness outside collisions. Set
union before the sum bound handles every overlap. Injective encodings create no
additional raw-string coincidence. The excluded arbitrary-string-output case
needs the stated unused-encoding guess term, with the implicit edge condition
`m<M`.

### 5. Capped and expected-work algebra

Subject to the repaired preprocessing-state restriction, the algebra checks:

`Pn+binom(n,2) >= N*delta`, where `delta=s-d/N>0`.

The inequality

`Pn+binom(n,2) <= (3/4)(P+n)^2`

is loose but valid. It gives

`P+n >= sqrt(4N*delta/3)`

and, because `W_att >= P+q_g-1=P+n-2`, the capped bound

`W_att >= sqrt(4N*delta/3)-2`.

For expected total single-instance work `mu`, truncating at
`L=ceil(2mu/delta)` loses at most `delta/2` success by Markov. On untruncated
paths, `P<=L+1`, `q_g<=L`, and `n<=L+1`. Applying the capped bound yields

`mu >= (delta/2)(sqrt(delta*N/3)-2)`.

The constants and Markov loss are correct for `mu>0`; the zero-work degenerate
case needs a harmless separate sentence. For constant positive excess, heavy
tails do not evade `Omega(sqrt(N))`. For shrinking excess, equation (18) gives
the weaker `Omega(sqrt(N)*delta^(3/2))` behavior and must not be advertised as
a uniform rho lower bound.

### 6. Retries, detectability, reused preprocessing, and multiple instances

Equation (16) is a correct renewal identity only for iid attempt pairs
`(work, success)` and detectable success. Detection is not free: a producer-only
work row may condition on a separate verifier, but an end-to-end row must add
that verifier's queries, memory, and data.

Equation (17) correctly distinguishes a table constructed once:

`C_pre + E[W_online,att]/s_att`.

The Pareto rows do not consistently use that distinction. If
`P=Theta(N^p)`, online work is `Theta(N^x)`, and
`s=Theta(N^-beta)`, then a table built once and reused across iid detectable
online attempts has exponent

`max(p, beta+x)`,

not `beta+max(p,x)`. If the table is rebuilt with fresh preprocessing coins on
every attempt, the latter expression can be correct, but that assumption and
the repeated construction/data movement must be stated.

For `B=Theta(N^b)` independent challenges sharing one table, the analogous
one-time construction expression is

`Theta(N^max(p-b,0)) + Theta(N^(beta+x))`,

with exponent `max(max(p-b,0), beta+x)`. The committed amortized row instead
divides the construction term by success as well. It therefore conflicts with
§7's own equation (17).

Repeating randomized attempts on one fixed `alpha` is not iid merely because
success is `s` after averaging over uniform `alpha`; one needs a per-instance
success statement or must integrate `1/s(alpha)`. Drawing fresh challenges
renews the instance distribution but changes the task and cannot be called a
single-instance retry. The `root_mass_output_G` phrase `Theta(N/d) across fresh
independently verified challenges` is therefore not a cost for solving one
challenge, and its unspecified verifier cost can be rho-scale.

Peak memory and resident data remain at least `P` under reuse and are never
divided by `B`. TASK-224 gets that part right. Dynamic updates based on prior
independent challenges are conditionally independent of a fresh challenge but
belong to the shared construction/state and must be charged over the declared
amortization population.

## Fatal theorem defect as written

### RT-226-F1 — encoding-dependent preprocessing state is outside the root union

**Affected claims:** repaired-producer-bound.md equations (1), (12), and (13),
§4's alpha-independent coupling, and proof obligations PO-224-05, PO-224-06,
PO-224-08, PO-224-12, PO-224-14, PO-224-16, and PO-224-18.

**Mutation.** Before `alpha` is sampled, query encodings of a set `S` of known
constant multiples of `G`, retain an exact encoding-to-scalar recognition
structure, and discard whatever the artifact chooses not to call a resident
handle. Online, inspect `Q`'s raw string. If it is recognized as `cG`, issue
`c^dG`; otherwise output `G`.

If the recognition structure is classified as separately charged non-handle
advice rather than contributing `|S|` to `P`, success gains `|S|/N` roots while
equation (1) gains no corresponding `P*n` term. A full inverse-encoding table
makes the contradiction immediate: success is one with one online scalar
multiplication, although construction/storage are linear. The large
`C_pre` means this does not beat rho work, but it does falsify the stated
probability inequality.

If every such retained encoding-derived record is, as intended, counted in
`P`, the mutation does not falsify the theorem. The package must resolve that
classification rather than relying on an unstated interpretation. Until it
does, the fixed-token coupling and the list of `PROVED` obligations are too
broad.

## Repairable presentation and accounting defects

### RT-226-R1 — retry formulas omit preprocessing-reuse regimes

**Affected claims:** repaired-producer-bound.md §7 as instantiated by
`pareto-frontier.yaml`; PO-224-17, PO-224-18, and PO-224-20; rows
`collision_table_tradeoff_single`, `collision_full_table_single`, and
`collision_table_tradeoff_amortized`.

Split each row into `rebuild_each_attempt` and `reuse_once` regimes. Use
`(C_pre+online)/s` only in the former. In the latter use
`C_pre+online/s`, with a conditional-success premise for the fixed table.

### RT-226-R2 — fresh challenges are not single-instance retries

**Affected claims:** `root_mass_output_G.expected_work_expression`, its
`single_instance: true` scope, and PO-224-17.

Delete the `Theta(N/d)` phrase or move it to a separately labeled sampling
row. Add the verifier's full cost if `independently verified` remains.

### RT-226-R3 — an explicit non-solver cannot have an admissible ECDLP SOTA row

**Affected claims:** `root_mass_output_G.sota_delta`, PO-224-20, and
PO-224-21's package-level accounting claim.

The row says `ecdlp_solver: false`; therefore set
`comparison_admissible: false` and all three ordinary SOTA improvements to
`not_applicable`. Its raw producer-task resource differences may remain under
a clearly non-SOTA field. Numeric zero means no exponent improvement for an
admissible comparison; it does not mean the comparison is undefined.

The positive-excess producer rows likewise are not complete ECDLP algorithms
unless downstream Cheon work, output verification, and inverse success are
included. Their safe treatment is `not_applicable` at row level, with the
package-level ordinary-ECDLP claimed improvement remaining exactly zero.

### RT-226-R4 — boundary constraints are not achieved frontier points

**Affected claims:** every collision row's exact `time_exponent`,
`expected_work_expression`, and `dominated_by` interpretation; PO-224-20.

The theorem supplies necessary collision constraints, not constructions
attaining every `(p,x,beta,kappa)` point. Label these rows as lower-bound
profiles or cite an actual algorithm and include its complete cost. Dominance
among hypothetical boundary profiles is only a formal comparison, not an
algorithmic Pareto frontier. The existing `global_frontier_claimed: false`
statement is appropriately cautious but does not cure exact-looking row
fields.

### RT-226-R5 — parameter ranges and access fields need closure

State `0<=kappa<=1-beta<=1` for the polynomial excess regimes represented by
the table, and provide a separate vacuous/small-excess row if needed. Replace
phrases such as `at most the charged online-work exponent` with a numeric bound
or `not_determined`; it is not a complete data/access exponent.

## Pareto row-by-row audit

| Row | `dominated_by` audit | SOTA audit | Result |
|---|---|---|---|
| `pollard_rho_ordinary_single` | `null` is defensible; no listed row solves the same task with all resources no worse. | Admissible ordinary baseline with zero deltas. | PASS |
| `collision_low_preprocessing_single` | Conditional Pollard dominance at constant success, `kappa=1`, `p>0` is correct as a formal profile. | Producer target is not a complete ECDLP solver; row-level ordinary SOTA comparison needs Cheon/verification or `not_applicable`. | REVISE |
| `collision_table_tradeoff_single` | `null` is defensible only as a formal resource profile because fewer online queries trade for larger time/memory/data. | Exact retry time overcharges reused preprocessing; complete ECDLP path absent. | REVISE |
| `collision_full_table_single` | `null` is defensible only because the online-query axis is strictly smaller; this is not an achieved frontier point. | Reused-preprocessing exponent and complete ECDLP path are missing. | REVISE |
| `collision_table_tradeoff_amortized` | `null` is defensible because no same-scope local row is supplied. | `not_applicable` ordinary single-instance deltas are correct, but the construction term is incorrectly divided by success. | REVISE |
| `root_mass_output_G` | `null` is correct for its strictly weaker bounded-correctness producer task. | `comparison_admissible: true` contradicts `ecdlp_solver: false`; three zeros must be `not_applicable`. | REVISE |

Every row lists all other local rows in `dominance_checked_against`, so there is
no unchecked `dominated_by: null`. The defects are task admissibility,
attainability, and retry accounting, not an omitted row name.

## Prior-art and scope audit

The artifacts correctly treat Cheon's auxiliary-input algorithm and generic
nonlinear-target hardness as binding prior art. They make no novelty, first,
positive SOTA, support, closure, or breakthrough claim. The ordinary input
does not supply `alpha^dG`; Cheon's cost therefore cannot be substituted for
producer acquisition. Conversely, a producer row alone is not an ordinary
ECDLP solver until the downstream Cheon computation and verification are
included.

The narrow surviving result concerns uniform nonzero `alpha`, prime-order
randomly encoded generic groups, affine generic operations, oracle-issued
outputs, encoding-oblivious advice, and fully charged single-instance state.
Pairings, endomorphisms, correspondences, nonlinear maps, extension-field
oracles, alpha-dependent advice, quantum algorithms, coordinate structure,
and multi-instance amortization outside the declared `B` population remain
open and unaffected.

## Observations that survive

- RT-215-C1 decisively separates producer correctness from verifier soundness.
- `d=N/2`, output `G`, constant work, and correctness `1/2` is exact.
- Affine closure and the raw-token fixed-transcript argument are sound after
  the preprocessing-state restriction is made explicit.
- `n=q_g+1`, `P*n+binom(n,2)`, the selected `T_out`, and the degree-`d` root
  bound are correct and conservative in that restricted model.
- Constant excess over `d/N` forces capped and expected single-instance
  producer work `Omega(sqrt(N))`; shrinking excess does not.
- Peak memory/resident data are at least `P`, and they do not amortize away.
- No ordinary-ECDLP improvement, novelty, closure, support, or breakthrough is
  established.

## Cheapest decisive falsification route

Run the proof-only **encoding-state erasure mutation RT-226-C1** described in
RT-226-F1. No code or experiment is needed. Ask whether an exact recognition
record for a preprocessed encoding still contributes to `P` after the producer
discards the handle object. If the answer is no, choose more than three such
records outside the `d` roots, branch on `Q`, and equation (1) is false. If the
answer is yes, serialize that rule, require encoding-oblivious external advice,
and rerun the fixed-transcript proof with every retained record counted.

Independently, the cheapest package-level rejection is a three-field schema
check on `root_mass_output_G`: `ecdlp_solver: false` requires
`comparison_admissible: false` and `not_applicable` deltas. That check alone
already rules out `PASS`, even if the theorem-model repair succeeds.

## Next concrete action

Issue one producer repair task, not an experiment. It should:

1. define advice relative to the random injection and broaden `P` to every
   retained equality-recognition record, or add a separate advice/state term;
2. redo PO-224-05, PO-224-06, PO-224-08, PO-224-12, PO-224-14, PO-224-16, and
   PO-224-18 under that definition;
3. split rebuild-versus-reuse retry rows and correct their exponents;
4. mark all non-ECDLP-solver row comparisons `not_applicable`; and
5. retain the narrow constant-excess conclusion and exact `d=N/2` obstruction.

The Coordinator alone may interpret or change official research state.
