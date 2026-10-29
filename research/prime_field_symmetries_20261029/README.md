# Prime-field factor bases, symmetry checks and the first C1 execution

29 October 2026. Three distinct evidence types: a new admitted fixed P-256
execution, exact diagnostics of retained Prym inputs, and new software prototypes.
No novelty, asymptotic improvement, complete attack-cost advantage or official
scientific status transition is asserted.

## New scientific execution

The unchanged seven-case F1 panel ran once through its existing admission,
after committing the instrument/analysis, freezing the prospective protocol,
uploading the real S3 checkpoint and committing an explicit root release.
The supervisor retained its owner, child PID, host, source/input/interpreter
locks, package versions, resource guards and complete stdout/stderr/raw journals.

| Fixed P-256 case | Symmetric states | Signed solutions | Complete finite oracle |
|---|---:|---:|---|
| Depth 3 constructed positive | 1 | 1 | matched |
| Depth 3 public generator | 0 | 0 | matched |
| Depth 4 constructed positive | 1 | 1 | matched |
| Depth 4 public generator | 0 | 0 | matched |

All five arity-four multiplicity partitions each returned one signed solution.
The nonseparable control and the corrupted-certificate control passed. The
historical name `corrupt-root-and-sign` actually removes the solution set;
this run does not claim additional native root/sign mutation controls.
All three triple-coordinate partitions were included; the nonzero states in
this native panel occur in the distinct-coordinate block. Separate native
positive queries for the two repeated-coordinate blocks remain a useful check.

The process exited 0, source unchanged, no timeout, seven cases complete and
zero unknown cases. The dimension guard remained 560. The exact P-256 curve,
generator, fibre terminals and public targets are the original
`p256_factor_base_parallel_20261026/tracks/f1/inputs.json`, not replacement
fixtures. A generator query with zero decompositions closes only that finite
base/query. The positives are constructed controls, not unknown DLP recoveries.

Native artifacts were committed first at `e925f22610577ceae34ff0e9cff59b3b40de277a`:
[raw run, receipts, analysis and export](../prime_field_c1_execution_20261029/runs/c1-fixed-panel-4f8ab9/).
Protocol canonical hash:
`da415e25dd20cae3d33abe90b1c6c9b6500063cfd7f7ad6dd78c97c49e7399d8`.
Source `6164ec00d419cbe43520fbdda19f85f6bbde44cf`; root-release commit
`9374c43ed538a91b62e3edc2b51d9f1ec1a6ccee`. Export verification with file
hashes passes with zero findings. Its two method cells share **one physical
execution** and one resource record; do not count them as two experiments or
sum shared object counts. The [run report](../prime_field_c1_execution_20261029/reports/c1-fixed-panel-4f8ab9/report.pdf)
contains the native observations separately from these prototypes.

Diagnostic process wall time was 321.665 seconds and peak process RSS
123,777,024 bytes. These are shared-host diagnostics, `wall_valid=false`, not
calibrated cost bounds or a matched performance comparison. Operator formation,
kernel elimination, extraction, lifting, signs and the separate oracle are
retained by stage. At depth 4 the recorded relation-operator CPU totals are
4.389/7.602 seconds for the positive/generator cases; no cache comparison was
run. FLINT internal elimination operation counts remain unavailable. Full cold
setup, misses, memory, validation and matched direct/MITM costs are still needed
before any scalable-improvement claim; no IC/rho claim is made here.

## A machine-readable base and symmetry catalog

[catalog.json](catalog.json) records two exact retained Prym bases, full EC1
curve identities, source/input hashes, signed ordered points, subgroup order,
known log-action constraints, closure/escaping witnesses and original-row
certificates. P-256 field/group parameters are decimal strings to preserve
integer precision. The catalog does not imply a broad curve census or a native
factory adapter for P-256. The crypto archive importer currently has its own
u64-width gates; its valid narrow-width comparisons are not silently widened.

On the retained p=4099, a=2 curves b=13,r=4021 and b=16,r=4111, the projected
matrices retain rank 13/15 and 9/15. Negation transports the old equations but
adds zero rank. This is exact retained-input analysis, with zero new curve,
target or collector draws. `catalog-initial.json` preserves the earlier
exploratory worktree output; `catalog.json` is the source-pinned version used
here. Their metadata differ; no scientific observations were discarded.

After publication, a clean-checkout checkpoint attempt exposed an empty-list
shell bug: filtering zero untracked files returned 1 under `pipefail`. The
state-hash loop now accepts clean or fully excluded lists while preserving
file-metadata failures and the real S3 gate. The regression fails on the old
function; seventeen affected checkpoint/relay tests pass after repair. This
bookkeeping fix follows the original C1 data snapshot. Reproduce C1 from its
pinned release/source; the old release correctly rejects changed source bytes.

`symmetry.py` separates four obligations: a valid curve map, a verified subgroup
eigenvalue, a known signed base action, and the information left after that
action. For the restricted map `(x,y)->(u²x,u³y)`, substituting the curve equation
requires `a(u⁴-1)=b(u⁶-1)=0`. On these generic curves both coefficients are
nonzero, so `u²=1`. Membership sign symmetry alone supplies no additional
curve automorphism. Frobenius is the identity on rational Fp points; binary
extension-field orbit compression cannot be imported by analogy.

If `phi(F_i)=sign_i F_j` and `phi=[lambda]` on the subgroup, the known equation
is `z_j=sign_i*lambda*z_i`. Once these equations are present, a transported
relation differs from lambda times its seed only by known constraints. The
auditor verifies public point equations and original-row weights, including
the transformed target coefficient. Toy cubic/quartic controls detect a
naive apparent rank increase that disappears after including these constraints.
An incomplete orbit still supplies valid known edges, but an escaping row
cannot silently lose its outside points.

The library expects a certified cyclic subgroup context from its caller. Its
r-torsion and point-action checks are not an independent full curve-order
certificate or a discrete-log membership oracle. The catalog preserves the
original fixture/validation provenance rather than upgrading an assertion.

## Implemented strategies and their next tests

**Public translation frames.** The points `F_i+[s]P` have logs `z_i+s` on the
original unknowns. A verified row `sum c_i(F_i+[s]P)=bP+tQ` projects to
`sum c_i F_i=(b-s*sum c_i)P+tQ`. The implementation verifies both point equations,
keeps target coefficients and flags zero/signed-alias atoms. It introduces no
new log columns. This is an affine frame, not a new subgroup endomorphism.
Before testing a collector, freeze public shifts and independent targets and
compare identically shifted source queries on the original base. Otherwise
additional source coverage could be mistaken for a geometric improvement.
No translated-source collector experiment has run.

**Reusable target-polynomial operators.** The frozen S4 coefficient expressions
have target-x degree at most four. For a fixed fibre, linearity gives
`M(t)=M_0+t M_1+...+t^4 M_4`. The prototype explicitly constructs all five
coefficient operators and evaluates query matrices by Horner's rule. It keeps
the dimension gate and does not remove kernel elimination, character extraction,
factoring, lifting or sign checks. Tests compare the exact matrix with the old
constructor for every target value in F19, across all three multiplicity blocks.
No P-256 cache or amortized-cost measurement has run. The next prospective test
must charge all setup operators/memory and compare cold and reused complete
queries with the same outputs and targets. This is operator-template reuse,
not a new generic curve symmetry or asymptotic result.

**Complete target replay.** `check_targets.py` reconstructs every target branch
through the historical separate Census/arithmetic lane. Its geometric source
is Q, while public-anchor projection stays bound to the original P schedule.
It compares exact rows/statuses/digests, dense affine rank and kernel syndrome,
first recovery prefixes, original-row weights, coincidence flags and `[k]P=Q`.
The scientific target launcher now requires this checker in its source lock and
calls it before publishing a case result. Software controls include public-hash
and known-generator targets, changed labels, removed rows, false prefixes,
bad anchors, counters and certificates. This second code path is not a staffed
independent scientific review. The eight proposed p=4099 natural targets remain
ungenerated; their prospective input/ownership/release bindings are next.

The isolated B1 Prym comparison and A1 natural partial-row panel also remain
unexecuted. The original [four-track plan](../prime_field_leads_20261028/PLAN.md)
stays open; C1 completion does not close the other questions. None of the new
symmetry interfaces enlarges B1's fixed base or changes its cubic law.

## Validation and sources

[Regression log](validation/regression-tests.txt): 175 passed, nine existing
optional-msolve skips. [Operator-family controls](validation/operator-family-tests.txt):
four passed. [Focused checks](validation/focused-tests.txt): 40 passed, overlapping
the regression suite. No prototype test is presented as a new P-256 experiment.
The C1 preparation retains its initial administrative failures and corrected
outcomes; in particular a root-added PID-record indentation error was caught
before commitment/execution. Final package tests passed before release.

See [literature.md](literature.md) for immutable source pointers, retrieved
official documentation and limits. The relevant primary PKM paper was read;
its relation-solver/linear-algebra cost boundary is preserved. Closely related
archive, orbit-folding, torsion and template strategies already exist in the
org. This work makes no absence-of-prior-work or novelty claim.

Historical Prym, F1 preparation and prior retained-diagnostics graphs stay
unchanged. New observations are graphed in this study and the fresh C1 report,
with their raw inputs linked. The diagram, renderer and inspected PDF are
derived communication artifacts. No ledger hypothesis/status is promoted.
