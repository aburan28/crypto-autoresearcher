#set page(paper: "a4", margin: (x: 18mm, y: 17mm))
#set text(font: "Helvetica Neue", size: 9.5pt)
#set par(leading: 0.64em)

= Orbit-canonical bases: complete IC integration gate

2026-10-17 UTC. This is a design memo for Coordinator review, not an approved experiment or a performance claim. Its source report is `docs/reports/2026-10-17-orbit-ic-integration-design.md`.

#image("2026-10-17-orbit-ic-integration-design.svg", width: 100%)

== Accepted inputs and inference limit

The reviewed N53 Koblitz complete IC comparator, `RUN-KIC-a15078`, has 3.0809126245 s median cold IC wall and 3.2945816805 paired IC/strengthened-rho median. Its signed Frobenius-orbit base has 75 columns. Internal setup and query medians are 0.7615440415 s and 1.844755585 s; query is nested inside collection, so those figures are not additive.

The separate reviewed N23/K16 point-decomposition receipt, `RUN-KIC-ba86d9`, found orbit-canonical normal-x / expanded-table whole-job paired median 0.6468878314 for 512 queries, with fixed-panel interval [0.6384838473, 0.6562119807]. N19/K4 at 512 queries was near parity, ratio 1.0031933978. N23 had a cheaper table build and slightly costlier queries. These N23 and N53 ratios belong to different curves, bases, workloads and panels and cannot be multiplied.

The next measurement must therefore use the accepted N53 base and the same unseen target panel in both IC arms. It isolates representation first; a selected elite base is a subsequent target-blind comparison.

#pagebreak()

== Proposed gated protocol

#table(
  columns: (0.6fr, 2.1fr, 3.6fr),
  inset: 5pt,
  [Gate], [Question], [Required control and stop],
  [A], [N53 compatibility], [Rebuild the same 75-column point set. Compare exact pair-sum support, deterministic witnesses, signs, infinity, repeated points, torsion and subgroup cases against the expanded table. Independently replay every admitted witness. Stop before timing on any mismatch.],
  [B], [Same-base complete IC], [Freeze disjoint public-known-answer points and seeds. Run baseline IC, canonical-table IC and strengthened rho in fresh serial processes with balanced order. Charge base/table build, all relation attempts, useful rank, linear algebra, target extraction, certificates, verification, I/O, CPU, wall and peak RSS. Preserve censored and invalid jobs.],
  [C], [Target-blind elite base], [Select candidates on training targets, commit recipes and failed candidates before the holdout. Match realized base size and representation. Measure distinct useful relations, duplicate rows, rank growth and complete cold and genuinely amortized costs on unseen same-point targets.],
)

The Coordinator must freeze sample count, exact panel derivation, arm order, resource envelope, censor rules, raw artifact paths, and inference before any run. Gate A is the cheap semantic falsifier. Gate B is the first proposed full-cost measurement. Gate C separates base choice from table representation. A new complete-cost advantage requires a machine-readable `claims/*.json` record passing `tools.progress_fidelity`, an independent review, and the paired matched-rho gap beside it.

The cold cost includes candidate-base selection, base and table builds, relation search, useful rank and linear algebra, target extraction, certificates, verification and I/O. A many-target cost may charge reusable work once only when reuse is real and the number of targets is stated.

== Larger grid and next act

The 50–63-bit prime/Koblitz/ordinary-binary, `m=2..8` grid remains open. Each row needs a size-matched current and target-blind base, structural controls, complete IC cost and matched rho. Direct `S_8` handles seven summands plus a target; eight summands need direct `S_9` or a chain such as `S_3`. Measure construction, monomial support, degree, solver resources, relation yield, rank and complete cost before transferring any structural signal. Timeout is censored.

The immediate Coordinator act is to freeze Gates A and B as one bounded N53 experiment. Gate C gets a separate holdout whose values remain undisclosed during base selection. No canonical frontier graph changes now: these pages connect accepted finite receipts to an unrun gate.

The configured Coordinator inference backend was unavailable at the 2026-10-17 check. `problems/prime-field-arity3-relation-oracle.md` now records the shared access limit and the exact exit condition for this ICPERF continuation. This is separate from the scientific uncertainty in Gates A–C.

Internal evidence: `research/cold_arm_composition_ic_20260921/REPORT.md`; `research/pair_reuse_20260922/REPORT.md`; `ledger/decisions/DEC-20260921-6648da.md`; `ledger/decisions/DEC-20260922-38ca94.md`; baseline grid `docs/reports/2026-10-16-elite-factor-base-baseline.md`.
