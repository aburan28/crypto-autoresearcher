#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Prime-field bases and verified symmetry actions
29 October 2026 · retained-input diagnostics and software prototypes

This report separates a new fixed P-256 execution, retained Prym matrices and
software-only strategies. No novelty, speedup or whole-attack cost is claimed.
The source-linked details and limitations are in README.md and literature.md.

#image("diagram.svg", width: 100%)

== What the retained data say
The two p=4099 Prym matrices retain rank13/15 and9/15. Their ordered base points,
curve identities and input hashes are in catalog.json. Negating old rows adds
zero rank. On these curves, a and b are nonzero: the diagonal point-map
conditions a(u⁴−1)=b(u⁶−1)=0 imply u²=1. Membership sign symmetry cannot be
silently treated as an extra curve automorphism. Fp Frobenius fixes rational
points; binary extension-field orbit folds do not transfer automatically.

#image("retained.svg", width: 95%)

== Three implemented routes
*Symmetry audit:* verify curve map, public-generator eigenvalue, signed base
action and group equations. Include zⱼ=sign·λ·zᵢ before scoring transported
rows. The returned original-row certificates include the target coefficient.
Incomplete closure keeps valid orbit edges but forbids dropping outside points.

*Public translation frame:* Fᵢ+[s]P has log zᵢ+s. Project a verified row by
subtracting s·Σcᵢ from its RHS, preserving the original unknowns. Zero and
signed-alias atoms remain flagged. Collection on translated frames is untested;
compare identical shifted sources before inferring any geometric advantage.

*Target-polynomial operators:* frozen S4 has target-x degree at most4, giving
M(t)=ΣtʲMⱼ with five coefficient operators. The prototype matches the original
matrix for every t in F19 and all three multiplicity blocks. Charge full setup,
query matrices and per-query elimination/recovery; no P-256 cache benchmark ran.

#pagebreak()
= First fixed C1 P-256 execution
One physical panel · original seven cases · seed2026102601 · dimension gate560

#image("native.svg", width: 100%)

Both constructed triple positives returned one symmetric state and one signed
solution. Both public-generator queries returned zero within their respective
fixed bases. The separate complete finite state/signed-set oracles matched.
All five arity-four multiplicity partitions returned one signed solution each;
nonseparable and corrupted-solution controls passed. The latter historical
case removes the solution set; it is not additional native root/sign coverage.
The triple repeated-coordinate blocks had no nonzero states in these four
queries; separate native repeated-coordinate positives remain useful.

The supervised process exited0, source unchanged, no timeout,7/7 cases complete
and0 unknown. Diagnostic wall321.665s and peak RSS123,777,024 bytes are shared-host
values, wall_valid=false. They are not calibrated bounds or performance evidence.
The finite oracle is charged validation work, separate from the solver.

== Execution and evidence
The instrument, analysis and original inputs were committed before the frozen
protocol, real S3 push/gate and explicit root release. Source commit:
#text(size: 8pt)[6164ec00d419cbe43520fbdda19f85f6bbde44cf].
Protocol hash:
#text(size: 8pt)[da415e25dd20cae3d33abe90b1c6c9b6500063cfd7f7ad6dd78c97c49e7399d8].
Native data snapshot:
#text(size: 8pt)[e925f22610577ceae34ff0e9cff59b3b40de277a].

The raw run, per-stage journals, PID/host/source receipts, analysis and validated
export are under prime_field_c1_execution_20261029/runs/c1-fixed-panel-4f8ab9.
Two method cells share one physical process; do not sum their counts/resources.
Model identity remains unverified and no independent claim review is asserted.

== Further iteration
Complete target replay now independently reconstructs all branches, ranks,
kernel syndromes, first recovery prefixes and row-combination certificates.
The eight proposed p=4099 natural targets remain ungenerated. B1's isolated
zero-completion panel and A1's natural partial-row panel remain unexecuted.
The next cache test needs a new prospective same-fibre many-target protocol
charging all construction, memory, elimination, lifting, signs and validation.

Checks:175 regression tests passed, nine existing optional-msolve skips;
four separate operator-family controls passed. Focused40-test results overlap
the regression count. C1 export verification has0 findings. Existing archive
and GLV notes already cover related folds and caches; Sage's official morphism
source and PKM2016 cost conditions are cited in literature.md. No scientific
status transition follows from this panel or these implementations.
