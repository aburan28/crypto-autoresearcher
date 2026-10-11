#set page(margin: 0.65in)
#set text(size: 10pt)
#set par(leading: 0.62em)
#show heading.where(level: 1): set text(size: 17pt, weight: "bold")
#show heading.where(level: 2): set text(size: 12pt, weight: "bold")

= Observation-only run report: EXP-CSIDH-999626

*Scope.* This report records the outputs of the frozen Stage 0–1 successor. It is observation-only: it assigns no evidence strength, promotes no claim, and changes no hypothesis or experiment status.

== Identity and runtime

Experiment \`EXP-CSIDH-999626\`; hypothesis \`H-CSIDH-73e6ab\`; goal \`GOAL-CSIDH-001\`; task \`TASK-20261011-883597\`; plan SHA-256 \`e4336c1437525dbc02b53a3680ab13336a084a41fefae8686cca47c47dc454f8\`; executor authority commit \`e66fddc083cc28726282956d28de1ec7eb7ecea2\`; owner/epoch \`executor-csidh-999626/1\`. Receipts record Linux, Python 3.11.17, and runtime-lock SHA \`2e527af61020a126a4d55a2be57e7874d7633cc46e80e5e79cb723e8a60c2edd\`.

The outer launch used the narrow worktree and Git-metadata mounts plus a read-only PyYAML mount. The exact command is retained in \`report.md\`.

== Trials

#table(
  columns: (1fr, 1.25fr, 1.1fr, 1.5fr),
  inset: 5pt,
  stroke: 0.4pt,
  [*Trial*], [*Run*], [*Start UTC*], [*Return/check, status*],
  [\`stage0-memcap-freeze\`], [\`RUN-CSIDH-8a996d\`], [19:31:48.379], [0/0, output validated],
  [\`stage1-memcap-census\`], [\`RUN-CSIDH-fc6b43\`], [19:31:52.888], [0/0, output validated],
)

The supervisor requested two trials and validated both. It reported zero remaining trials, zero dependency waits, and zero reconciliation items. No timeout or crash was recorded.

== Frozen controls and recorded values

The run used $p=419$, $"disc"=-419$, $n=4$, both enumeration routes, $M=2$ and $M_"free"=4$, $G in {1,2}$, the blind-control instrument, and the forced-$N=1$ control. Stage 0 recorded \`S0-FREEZE-OK\`; Stage 1 recorded \`O-SEPARATES\`, with $N_A=N_B=9$ and reconstruction true.

#figure(
  image("graph.svg", width: 100%),
  caption: [Recorded deterministic ratios ($n=1$ per bar) from \`RUN-CSIDH-8a996d\` and \`RUN-CSIDH-fc6b43\`. Values are copied from stage artifacts; no new samples or uncertainty estimate was added.],
)

The main ratios were 2.0 at both G levels; the blind ratios and forced-$N=1$ control were 1.0. No spread, CPU-time measurement, per-stage wall-time measurement, random seed, or statistical uncertainty was recorded, so those fields remain missing.

== Artifact pointers

The exact receipts, raw results, manifests, checker logs, and stage artifacts are in the two run directories named above. The editable graph data are in \`graph-data.json\`; the narrative and exact outer command are in \`report.md\`. This report does not generalize the deterministic ratios beyond the frozen tested scope.
