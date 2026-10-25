#set document(title: "Sheriff case SHF-20261023-7b9227")
#set page(paper: "a4", margin: 1.8cm, numbering: "1")
#set text(size: 9.5pt)
#set par(justify: true)
#show heading.where(level: 1): set text(size: 16pt)
#show heading.where(level: 2): set text(size: 12pt)

= Sheriff case SHF-20261023-7b9227

This case ran `all` at the deep tier on 2026-10-23. It sweeps the three
repositories on `origin/main` and adds five independent readers on the claims
that carried weight among what merged since SHF-20261017-e4d7f6. It is an
audit record: it changes no research state and repairs nothing. The verdicts
are in `findings.yaml`, which passes `check-case`. The full text is in
`REPORT.md`.

*Result: of 16 claims, 2 are upheld, 10 are upheld with a narrower scope, 3 are
overclaimed and 1 is broken. There is no blocker.* The goal closure (GOAL-MONO-001)
holds: its mathematics survived a blind re-derivation and an exhaustive
falsification search. The broken claim is that `validate` guards main: it
fails on every main run.

#figure(image("verdicts.svg", width: 100%), caption: [Verdicts on the 16 audited claims, by area (findings.yaml).])

== Scope

#table(columns: 3, stroke: 0.4pt, inset: 4pt,
  [*repository*], [*commit*], [*how*],
  [crypto-autoresearcher], [`e9b91d62a9` origin/main], [in place],
  [crypto], [`6ed792e86` origin/main], [sparse partial clone; `ecbench` rebuilt],
  [cryptanalysis], [`6dfc25d` origin/main], [sparse partial clone],
)

- The canary passed (15/15, no false positives). The instrument includes the
  I1 fixes, so sparse coverage now reports as partial: 413 leads are
  `not_covered`.
- Independence: this session's own \#2330 and the earlier cases are excluded.
  The STARK fix `999d4eefc` and \#2326 were written by other sessions and are
  in scope.
- About 4.4 GB of disk was free, so only the Mathlib-free Lean modules could
  be built.

*Prior* (`prior.md`, written before the sweep):
- the STARK fix would hold, with risk in the AIR identifier — confirmed, minor;
- the ledger would have grown — it shrank, 157 → 141;
- CI would still be off — partly on, and red;
- new strong wording — confirmed;
- the cryptanalysis K-N residues would still be open — mostly fixed.

== Verdicts

#table(columns: 3, stroke: 0.4pt, inset: 3pt,
  [*id*], [*claim*], [*verdict and basis*],
  [C1], [KN-FIND-bdcd60 monodromy and Frobenius rule], [upheld_scoped: blind re-derivation; orders 2/24/192/1920/23040; 0 violations in 2.1 M fibres; m≥4 for primitivity],
  [C2], ["established; three derivations agree"], [*overclaimed*: one derivation, one blind (answer-shaped card), one guided; one model family],
  [C3], [GOAL-MONO-001 completed], [upheld_scoped: criterion (c) instrument no-go; question open],
  [C4], [STARK statement binding; forgeries rejected], [upheld_scoped: every old mutant rejected, no panics, 41/41 tests; new-design attacks not run],
  [C5], [stark_v2 soundness text], [upheld],
  [C6], [ecbench `records_bound` (E1-R)], [upheld_scoped: correct; nothing consumes it],
  [C7], [21 new formal/ Lean modules], [upheld_scoped: no holes; constants re-derive; 6 Mathlib-free modules built here, 30 theorems standard axioms, mutants fail; 15 never built by CI],
  [C8], ["the certificate proves C5"], [*overclaimed*: two C5 steps are Sage checks, not Lean],
  [C9], [n=83 closure 6.44 / 7.66 / 7.41], [upheld_scoped: re-derived blind; 174/174 answers; gain is fewer unknowns, not cheaper relations],
  [C10], [n=83 engineering chain], [upheld_scoped: wall time on four CPUs; sub-2% effects not separable from layout],
  [C11], [n=83 row: gap 3.9242, band not computable], [*overclaimed*: [3.16, 5.22], host-dependent; band computable, unranked],
  [C12], [\#944 fixes K-N1..4, R1-R], [upheld_scoped: K-N1 partly (no group-op counts)],
  [C13], [`validate` guards main], [*broken*: fails on every main run; 141 ledger errors],
  [C14], [runbook sessions audited], [upheld_scoped: 2 unaudited; both audited clean here],
  [C15], [crypto \#2066 L-N1, L-N7], [upheld: the cited CI jobs re-read, all green],
  [C16], [fb-archive index], [upheld_scoped: 2,681 archives, 0 problems],
)

== Major findings (no blocker)

- *MN-3:* the MONO confidence wording overstates the independence of the
  review round. The mathematics stands.
- *LN-1:* the FROB C5 report says Lean "proves C5". Two of its steps are
  checked in Sage, where they hold.
- *N83-1:* each relation costs one generic table solve, so the closure's gain
  comes from 600 → 16 unknowns. As K′ → 0 the method becomes the ledger's own
  BSGS on the quotient, which is not IC. The fix is to add a known-log arm.
- *CI-1:* `validate` is red on every main run, so it cannot flag new defects.
- *CI-2:* `lean-verification` is still disabled, so CI has built none of the
  21 new Lean modules.

There are 18 minor findings; they are listed in `REPORT.md` and
`findings.yaml`.

== Sweep

#figure(image("sweep.svg", width: 100%), caption: [Deterministic sweep leads by beat (sweep.json).])

== Not covered

- *The 15 Mathlib-dependent Lean modules:* need about 6 GB of disk, or
  `lean-verification` re-enabled.
- *The STARK attacks on the new design:* AIR-identifier collision and
  oversized statements.
- *The 413 sparse-coverage leads, `refs.py`, `curve-names`,
  `ecbench bound check`, and the 497 ecbench sessions outside the sparse set:* need full
  checkouts.
- *Literature dominance for KN-FIND-bdcd60.*

== What this case does not establish

- That KN-FIND-bdcd60 is new or bears on relation rates.
- That n=83 IC beats rho: it is 3.92× above matched rho, and the two are
  unranked across the GAE band.
- That the 15 Mathlib-dependent modules build.
- Anything about this session's own \#2330.
- Any execution proof.

*Readers* (paths under `/tmp/...` in the reader files refer to the staging copy mirrored under `scripts/readers/`):
- validator-breakthrough: MONO, blind re-derivation;
- red-team-breakthrough (claude-fable-5-1): MONO, scope and decision logic;
- validator: STARK;
- validator: Lean;
- red-team: n=83.
