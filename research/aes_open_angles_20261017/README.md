# AES research assessment and experiment ideas

Start with [REPORT.md](REPORT.md) or [the PDF](report.pdf). The source receipt
is [sources.json](sources.json); nine advisory, falsifiable follow-ups are in
[hypotheses.json](hypotheses.json). These do not create official ledger records
or change GOAL-AES-001/002/003 priorities or execution permissions.

The [native adapter](../../experiments/aes-distinguisher-lab-20261017/README.md)
links the implemented companion binary, frozen suite and measured observations.
The remaining `crypto` integration is tracked in
[the access problem](../../problems/aes-lab-conductor-and-campaign-admission.md).

The editable report source is Markdown plus `research-map.svg`. `report.typ`
contains the rendered Pandoc fragment with page/font settings. To render that
source, run `typst compile report.typ report.pdf` in this directory. The current
PDF used Pandoc 3.9 and Typst 0.15.0. All four pages, including the taxonomy
table and the implemented/proposed diagram, were visually inspected. The
machine-readable sources distinguish full-text/selected-section reads from
abstract-only reads; no exhaustive novelty audit or full published attack
reproduction is claimed.
