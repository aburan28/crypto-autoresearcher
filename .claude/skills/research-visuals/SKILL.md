---
name: research-visuals
description: Produce evidence-linked diagrams, graphs, reports, and PDFs for every experiment run, every evidence review, and every substantive search for new isogenies, curves, scalar rules, endomorphisms, and related ECDLP mechanisms.
---

# Research visuals and reports

Use this skill at three points (AGENTS.md "Visual research record"):

- **every experiment run**: the `run` skill finishes each experiment it ran
  with a descriptive run report ("Every experiment run" below);
- **every evidence review**: the review that records a `DEC-*` decision
  leaves a decision report and refreshes the canonical graphs it changes
  ("Every evidence review" below);
- **every substantive search round**: a literature, theory, code, or
  experiment search for new isogenies, curves, scalar rules, endomorphisms, or
  related ECDLP ideas ("Deliverables for each search round" below).

Read `AGENTS.md` first. This skill publishes derived communication artifacts;
it does not approve an experiment, launch a trial, promote a claim, or turn
`run` into a review. Report paths for runs and reviews are fixed below; for a
search round the Coordinator assigns the report and graph paths in a task's
write scope before work is dispatched.

## Every experiment run

Each `run` session leaves one report per experiment it ran, covering every run
directory it wrote for that experiment: completed, failed, and timed-out
trials alike. A launch refused before any run directory exists gets no report;
`run` reports the impediment as before.

- **Where.** A fresh, write-once directory
  `experiments/<EXP-ID>/reports/run-<YYYYMMDDTHHMMZ>/` (UTC time the session's
  first trial for that experiment started). Never write into a run directory:
  runners seal theirs (`manifest.sha256`, expected/missing/extra file lists),
  and an added file reads as an unlisted extra. Never edit an earlier report;
  a later session writes its own. An experiment whose own runner already
  writes a report into its run directory keeps that report, and this one
  links to it.
- **What the report says.** Experiment, hypothesis and goal IDs; the run
  IDs and their paths; code commit and dirty state; exact command,
  parameters, seeds and controls; trials requested, completed, failed and
  timed out, with each failure's recorded reason; wall and CPU time and the
  host; the measured values with units, sample sizes and the spread or
  uncertainty the runner recorded; the controls' outcomes and certificate
  status; missing data stated as missing. Label every number measured or
  derived (a ratio or mean computed from recorded values) and show how a
  derived one was computed.
- **Observations only.** No verdict, support or weaken language, significance
  or priority: those belong to the evidence review. Say so in the report's
  first paragraph. A failed process is an operational fact, not a mathematical
  refutation.
- **Graph.** At least one quantitative graph of the run's recorded data
  (per-trial values, arms side by side, a quantity against a parameter, or
  progress over time) with units, sample size, uncertainty where recorded,
  and run IDs in the caption. Plot recorded values only: no new computation,
  sampling, or reruns. A run with fewer than two comparable values gets a
  diagram of what ran (arms, controls, pipeline, where it stopped) instead,
  and the report says why. Keep the script or data that draws each graph
  beside its SVG.
- **PDF.** `report.pdf` from the report source with the graph embedded
  ("Rendering" below), inspected before it is committed.
- **Publish after the run records.** The run records are committed and
  pushed first, as `run` already does, so no report delays them; then commit
  the report directory on the same branch, push, and name it in the session's
  final summary. Keep it proportionate: minutes per experiment, not a study.

## Every evidence review

The review that records a `DEC-*` decision (`/review-evidence`, or the review
step of `coordinate`) leaves a decision report beside the experiment's earlier
reports, in `experiments/<EXP-ID>/reports/review-<DEC-ID>/`, archived in the
same ledger commit as the evidence and decision records.

- State the decision, evidence strength, claim tier, and the exact scoped
  claim, with the `EV-*`, `DEC-*`, `RUN-*` and `TASK-*` IDs they rest on.
  Keep Observation, Comparison, Inference, and Limitation separate, as
  `analysis.md` does, and list the next actions.
- Graph the quantities the decision rests on: measured values with units,
  sample sizes and uncertainty against the declared prediction, threshold, or
  control, with run IDs cited. Adverse decisions graph the obstruction they
  record (its measured value and scope).
- Refresh every canonical graph the decision changes ("Keep graphs current
  without changing the evidence" below) in the same change; list the graphs
  checked and left unchanged.
- Build and inspect the PDF. The subagent that writes the records may lack a
  shell; then the session renders the graphs and PDF before the ledger
  archive commit.

## Rendering

Use an installed renderer: Typst, Pandoc with a PDF engine, or LaTeX. Where
none is installed (a Claude Code cloud container has none), install Typst as a
Python wheel in a scratch virtualenv outside the repository; it is the same
compiler that built this repository's Typst reports:

```sh
python3 -m venv /tmp/report-venv
/tmp/report-venv/bin/pip install -q typst matplotlib
/tmp/report-venv/bin/python -c "import typst; typst.compile('report.typ', output='report.pdf')"
```

Write the report source in Typst when Typst renders it (Markdown needs
Pandoc). Draw graphs as SVG with matplotlib, Graphviz, or hand-written SVG,
and embed the SVG in the PDF. Then open the PDF and read every page: check
that it opens, that the graph is legible and labeled, and that run IDs and
citations are present. Never commit a PDF you have not inspected, and never
present an older PDF as current. If no renderer can be installed, commit the
complete source and graphs, and state the exact blocker in the report and the
session summary.

## Deliverables for each search round

1. Write a dated Markdown report in the assigned `research/` study directory
   or `docs/reports/`. State the question, search scope, methods, exact curve
   and subgroup identities, sources and evidence/run IDs, positive and
   negative results, contradictions, limitations, and next checks. Label each
   statement as proposed, derived, independently verified, or measured. For
   isogenies include endpoint IDs, degree, map/kernel and subgroup transport
   status; for scalar rules include domain, preconditions, formula, and an
   independent check or counterexample.
2. Add at least one explanatory diagram with editable source and a vector
   rendering such as SVG, plus a quantitative graph when there are data to
   compare. Label isogeny vertices by full curve identity,
   their edges by degree/direction, and unknown or conjectural edges as
   such. For an ordinary volcano diagram, label every vertex with
   `(D_K, f_pi, f_E)`, using `null` when `f_E` is not certified, and label
   every edge with degree, separability, field of definition, and
   `horizontal | ascending | descending | unresolved`. Draw
   characteristic-power Frobenius or Koblitz `tau` as an endomorphism action,
   not as a separable volcano edge. Quantitative plots need units, sample sizes, uncertainty, and cited
   run IDs. Link the visual and its supporting records from the report.
3. Produce a PDF of the report with the visual included, using an available
   document tool such as Pandoc, Typst, or LaTeX ("Rendering" above). Keep
   source and PDF together and inspect legibility and citations. If rendering is blocked, preserve
   complete source and report the precise blocker; never reuse an older PDF
   as though it includes the latest finding.

## Keep graphs current without changing the evidence

- Before editing, find all affected graph sources and rendered forms in the
  study directory, `knowledge/frontiers/ecdlp/`, and related reports. Treat
  evidence, ledger decisions, and knowledge records as authoritative; graphs
  and PDFs are derived views. Update affected graph source and rendering in
  the same scoped change after the supporting record exists. Never mutate an
  immutable run receipt or historical report to make a graph appear current.
- Distinguish proposed, literature-reported, independently checked, and
  measured items visually. An isogeny class sketch does not prove a map;
  similarly a scalar identity tested on toy curves is not a universal rule.
  Do not infer exact curve identity from field degree or a short alias.
- If no graphable finding survives, record the negative or inconclusive result
  and list the graphs checked. Still provide the search report, diagram, and
  PDF. Change a canonical graph only when its supported content or coverage
  changes.
- Have the Coordinator archive the new derived artifacts through the normal
  task and commit process. Any shared graph needs an exclusive write scope;
  concurrent workers supply evidence and proposed edits to the Coordinator.
  Review the graph against cited evidence, inspect the PDF, and include all
  affected forms in the same publication change.

## Reports in S3

Once a report is on `main`, `.github/workflows/reports-s3.yml` copies it to
`s3://crypto-autoresearcher/reports/crypto-autoresearcher/<repository path>`
with a per-push manifest (`docs/reports-s3.md`). It takes everything under
`experiments/*/reports/` and `docs/reports/` and every PDF under `research/`,
so keep reports at those paths. Sessions never upload to S3.
