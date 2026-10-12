The existing ML solver selector had no elliptic-curve input or relation
evaluator. This adds a bounded EC summation-polynomial bridge, exact signed-point
verification, modular relation rank and target-identifiability checks, with
field-based splits and public-feature allowlists.

The standalone task retains write-once logs, inputs, JSON checkpoints, costs,
controls and source/artifact hashes. A retrospective audit identifies repeated
curves in the earlier number-field data. A source-linked report, editable diagram,
figures and inspected PDF explain the theory and proposed confirmation design.

Validation: 13 mathematical/leakage tests passed; 96 quick and 768 standard
solver jobs completed; both complete artifact replays passed. On 48 standard
test targets, the same relation pool supplies a per-target rank sum of 56 and
11 newly identified logs; post-hoc shared-curve accounting gives joint rank sum
39 and 13 new logs. Seven other target logs are initially known. BSGS recovers
all targets. The learned selectors did not beat the best fixed training action
on this run. These are tiny-group software pilots, with no security inference,
sealed bound or official hypothesis transition.

Tracking: ready PR intended from `feat/ec-relation-ml-20261011` into
`run/nist-prime-resistance-20261011`, after that earlier branch is published.
Publication status is recorded separately; no PR number is assigned locally.
