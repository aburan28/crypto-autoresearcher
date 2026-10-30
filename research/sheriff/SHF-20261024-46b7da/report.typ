#set document(title: "Sheriff case SHF-20261024-46b7da")
#set page(paper: "a4", margin: 1.75cm, numbering: "1")
#set text(size: 9.5pt)
#set par(justify: true)
#show heading.where(level: 1): set text(size: 15pt)
#show heading.where(level: 2): set text(size: 11pt)

= Sheriff case SHF-20261024-46b7da

Published-main validation snapshot, 24 October 2026. The authoritative
machine-readable verdicts are in `findings.yaml`; the full narrative and
limitations are in `REPORT.md`. This case changes no research status or
experiment record.

== Exact source scope

#table(columns: (auto, 1fr), stroke: 0.4pt, inset: 4pt,
  [*repository*], [*published commit*],
  [crypto-autoresearcher], [`4647b1d072ffaebbbb85127bdc60343bbd372ec4`],
  [crypto], [`172f84c7b0143ff5b4a26d6d21ffed3bf0f0cf3b`],
  [cryptanalysis], [`9d320ae7df3b8aa15d4497d6895f63644daa92d5`],
)

#figure(image("sweep.svg", width: 100%), caption: [Deterministic deep-sweep
signals. A scanner lead or a checker timeout is not a research verdict; see
`findings.yaml` for scoped adjudication.])

== Scoped verdicts

#table(columns: (auto, auto, 1fr), stroke: 0.35pt, inset: 3pt,
  [*ID*], [*verdict*], [*established scope*],
  [C1], [scoped], [84 / 84 pinned target declarations machine-verified; semantic fidelity pending],
  [C2], [scoped], [conditional BINSTD arithmetic ceiling, with satisfiable premises],
  [C3], [uncovered], [archived 40 / 40 EC execution not independently replayed],
  [C4], [scoped], [binary polynomial product identity only],
  [C5], [scoped], [3.2391 charged cold wall-time ratio, one host, two rank seeds],
  [C6], [scoped], [approximately 94-fold cold gap to matched rho on this host],
  [C7], [scoped], [tested degree-one STARK examples; general soundness open],
  [C8], [scoped], [14 receipt-source hashes; selected Lean builds only],
  [C9], [broken], [sheriff ecbench checker omits gzip expansion for archived sessions],
  [C10], [broken], [two configured cryptanalysis Lean gate scripts are absent],
  [C11], [broken], [formal checker timeout left an untracked Lean audit file],
  [C12], [scoped], [2,681 indexed factor-base archives verify with NumPy installed],
  [C13], [broken], [32 cited factor-base digests lack archive or declared debt],
  [C14], [broken], [four complete scratch pilots lack spec and host audit inputs],
  [C15], [broken], [13 interrupted sessions were counted as complete passes],
)

== Main limitations

The registry holds 2,753 experiment IDs and 3,726 run IDs in the auto
researcher, 636 crypto session paths (617 ecbench/v1), and 335 cryptanalysis experiment
directories. Only selected load-bearing joints received independent reading.
The 84 checked targets cite only five exact experiment IDs and five full run
IDs across their specs and 29 pinned source files; this is pointer coverage,
not proof of those runs.
The 617 ecbench/v1 directories have source-hashed integrity replays: 590
complete-status bound passes, 13 interrupted-status bound integrity passes
for retained records only, ten interrupted and unbound, and four missing
required source inputs. These counts do not replay timing and are not a
theorem-to-run coverage fraction. The n=83 stack omits
factor-base construction from both arms; a rank-stage planted control and
cross-host replay are missing. The STARK public closure accepts an
out-of-contract non-polynomial AIR, while the tested degree-one mutants reject.
Any checker infrastructure timeout remains a coverage gap, not a mathematical
counterexample. Pending PRs and public dashboard refresh are separate gates.
After this frozen snapshot, the PR replayed all four amended BINSTD cells:
160 deterministic targets and four archived hit-count pairs matched under
historical source commits and a separate exhaustive EC pair-sum oracle.
Original per-target traces and host timing remain unavailable.
