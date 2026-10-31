# LastFall review integration, 2026-10-31

The three independent reports support the conditional mathematical identity
`d_F = max{d_f : d_f > deg f}` at the level of source interpretation and a
separate derivation. They also locate a concrete claim boundary: an exact
finite rank profile supplies falls in its observed degrees, while identifying
its largest observed fall with the global `d_F` requires an independent upper
bound or completion certificate. This packet does not claim a completed formal
validation or validate an actual Macaulay measurement.

## Bound inputs and independent reports

- Reviewed producer tree: `199f3aaaa6d37d2fce59f4d8c8fe8d2eb8b50672`.
  The precommitted plan was pushed at `2b0cfe1401831c9493cfe047a515955f38d037b8`.
- [Source report](source/report.md), committed by T-1105, checks Caminata–Gorla
  Definition 1.5 and Theorem 2.8 against the target and records a paper proof
  typo and the essential degree-fall hypothesis. Its diagram and inspected
  [PDF](source/report.pdf) are retained.
- [Lean report](lean/report.md), committed by T-1106, checks the declaration,
  guards, historical receipt input hashes and mathematical controls. Its
  static fidelity verdict is `faithful_scoped`; its owned-joint outcome is
  `inconclusive` pending a fresh pinned build and transitive axiom audit.
- [Blind report](blind/report.md), committed by T-1107, derives the equality
  from definitions alone and gives explicit finite-profile controls. Its
  [profile diagram](blind/profile-control.svg) and inspected [PDF](blind/report.pdf)
  are retained. It read no producer theorem, target, receipt, note or sibling
  report before publishing.

The report branches were integrated by exact scoped cherry-picks after merging
current `main` at `0c9dddeb6aaf1c36ac6cdb41c293233f9709b6fe`. The
reviewed LastFall source and target blobs were unchanged across those trees.

| Dimension | Finding | Next gate |
| --- | --- | --- |
| Source correspondence | Conditional theorem and explicit hypotheses match the paper in the checked scope. | Keep no-fall and finiteness branches explicit. |
| Lean semantic fidelity | Static statement and model inspection support the conditional invariant claim. | Fresh isolated pinned module build, named declaration and transitive axiom audit. |
| Measurement inference | The unrestricted finite-prefix inference breaks; two systems can have the same observed profile and different later `d_F`. | Bind each concrete rank run to the iterated closure `V_i`, then prove a cutoff/completion condition. |
| Independent review gate | `check_review_independence.py` fails on seven task-ID schema errors, retained in [independence_gate.txt](independence_gate.txt). | Correct identity binding through a prospective schema-compatible review round; preserve these original reports and chronology. |

The blind control uses `G_N={x²,x²+x,x^N,x^N+x}` and
`H_N={x²,x²+x,y^N,y^N+y}`, with `N>B≥2`. Their exact `V_i` agree for every
`i≤B`, including a visible degree-2 fall, yet `d_(G_N)=2` and `d_(H_N)=N`.
The argument is mathematical, not an execution receipt. The same review shows
that a one-pass Macaulay row span can be smaller than `V_i`: the row-space
bridge must refer to the paper's repeated reduction and multiplication
closure, rather than an unqualified one-pass matrix.

## Procedure and claim limits

The frozen plan assigned Conductor IDs `T-1105` through `T-1107`.
The repository checker requires `TASK-*` IDs for both plan owners and
attestations. The exact checker invocation returned exit 1 with seven identity
errors and no other reported independence errors. This administrative mistake
was discovered after reviewer work began; editing the prior in place would
obscure chronology. The original plan and reports remain intact, and no
`validated_scoped` combined outcome is assigned.

The historical hosted receipt reports `machine_verified`, but the static
hash comparison does not authenticate its execution. Resource admission on
this host prevented a fresh Lean gate: other Rust and Clippy builds owned the
build slot and root-disk free space fell to roughly 4 GiB during review.
No Lean build, experiment, or cloud job was launched by this review.

The blind report's empty-fall example and alternate attainment proof use
`deg(0)=0`, or equivalently exclude zero from strict fall witnesses. If one
instead assigns `deg(0)=-∞` and counts zero, then zero has appearance index
zero and is a formal index-0 fall. The main maximum argument and all positive
degree controls remain valid; its alternate proof should start with `d_F>0`,
and `{x}` should be described as having no **nonzero** strict fall. This
convention is explicit here rather than silently altering the blind report.

The source reviewer also found that the producer note's adjacent Theorem 2.9
restatement omitted the paper's fall-existence condition. A subsequent scoped
documentation correction restores it and narrows the target note and
measurement bridge to the finite-profile evidence actually available. The
formal Theorem 2.8 declaration and its hypotheses are unchanged. A later
comment-only correction to `LastFall.lean` removes its residual finite-profile
overclaim and fixes two closure explanations; no declaration or proof term is
edited. The original reviewer reports and input bindings still refer to the
pre-correction producer tree.

The report PDFs and SVGs are explanatory diagrams, not benchmark plots. No
measured performance figure or public dashboard value changes as a result of
this theorem review.

The remaining obligations are tracked in the
[finite-profile completeness problem](../../../problems/lastfall-finite-profile-completeness.md)
and the [review identity problem](../../../problems/lastfall-review-task-id-schema.md).
