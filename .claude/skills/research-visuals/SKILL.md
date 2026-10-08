---
name: research-visuals
description: Produce evidence-linked diagrams, graphs, reports, and PDFs for substantive searches for new isogenies, curves, scalar rules, endomorphisms, and related ECDLP mechanisms.
---

# Research visuals and reports

Use this skill for a substantive literature, theory, code, or experiment search
for new isogenies, curves, scalar rules, endomorphisms, or related ECDLP ideas.
Read `AGENTS.md` first. This skill publishes derived communication artifacts;
it does not approve an experiment, launch a trial, promote a claim, or alter
the public `run` skill. The Coordinator assigns the report and graph paths in
a task's write scope before work is dispatched.

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
   such. Quantitative plots need units, sample sizes, uncertainty, and cited
   run IDs. Link the visual and its supporting records from the report.
3. Produce a PDF of the report with the visual included, using an available
   document tool such as Pandoc, Typst, or LaTeX. Keep source and PDF together
   and inspect legibility and citations. If rendering is blocked, preserve
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
