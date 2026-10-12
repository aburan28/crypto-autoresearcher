# Fresh checks of three exploratory rare-prefix candidates

2026-10-12. Additive follow-up; original `higher-order-20261012` artifacts,
protocol and all results remain immutable. User authorization: explore rare
and higher-order patterns, run controlled studies and track them with PRs.
These are point-distribution observations, not a scientific-state change.

Discovery: all three of the 3,200 targeted-prefix score descriptors with
empirical right-tail fraction ≤.001 in the 98,304-G reference bank. The
threshold was a descriptive summary after sampling; it was not a primary
test. Explicit public G, exact standard curve, selected metric and original
score are locked in `config.json` with the selection-artifact checksum.
No cherry-picked candidate is omitted. This new protocol is committed and
pushed **before** its independent fresh public seed is sampled.

For each of the three fixed candidates, 4,096 independent paired windows
of 256 points, new uniformly random nonzero starting scalar per pair,
same scalar for the candidate H and a fresh uniformly random control G.
Candidates: P192 four-bit motif dispersion, P224 longest bit run, P224
bit-64 triple parity. New seed: solinas-rare-targets-20261012-fresh-v1.
6,291,456 measured coordinates, chunks of 32 pairs, three workers. Fixed
stopping after all 384 chunks, no significance-dependent enlargement.
Failures stop; identical-design/hash checks permit safe restart. Retain
all raw points, per-window scores, G and seeds, source, receipts and hashes.

Nine predeclared tests, a **separate** nominal 99.99% family (α=.0001,
Bonferroni α/test=.0001/9): one candidate-minus-random mean interval in the
selected score; one same-point u=2 candidate-minus-random mean interval;
one exact paired McNemar/binomial test of event rate score≥discovery score,
for each candidate. Means use paired Student approximations at independent
window level. Rare events use exact discordant-pair tests, not zero-variance
normal intervals. Report exact Clopper–Pearson bounds on each of the six
arm rates with .0001/6 correction, separately from the paired tests.

u=2 is the explicit isomorphism x→4x,y→8y,A→16A,B→64B, applied to the same
points. It is a coordinate diagnostic, not an independent curve sample.
Do not claim a combined 87-test 99.9% family: the original primary family
has α=.001 and this additional family α=.0001; a simple union bound across
families is nominal 99.89%, with approximate mean-interval coverage.

Verify every raw hash and coordinate equation, replay scores and u=2 scores,
check eight spread affine transitions/unit and selected start/generator
scalars with a separate Python affine oracle. This same-session check is
not independent scientific review. Report all means, event hits, intervals,
failures, limits and control outcomes, including zero-hit uncertainty.

A significant fresh effect would be a fixed-candidate coordinate/ordering
lead requiring an independent review and ordinary-prime matched construction;
it would not establish Solinas specificity or ECDLP resistance. Null means
or rare-event tests would bound only this window/population. Approximately
4,096 windows have little power for events at frequency 10^−5 or lower;
never call a zero hit evidence that the event is impossible. The original
selected prefix is not reused as fresh confirmation.
