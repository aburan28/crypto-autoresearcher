#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)
= Recovered n=42 degree-four certificates

Two interrupted original-panel attempts, `fresh-n42-rand-03` and `fresh-n42-rand-04`, retained complete 329 MB D4 certificate candidates but lacked terminal results. The closure producer was not rerun. The original independent checker accepted both certificates with codimension at least 22,065; a fresh pinned exhaustive counter found zero solutions for each. Thus each exact named Boolean presentation has last fall degree at least 5. The original producer exit codes remain unknown.

#table(columns: (1.8fr, 1fr, 1fr, 1fr), stroke: 0.4pt + gray,
  [Input], [Fresh count], [Checked D4 codim ≥], [LFD ≥],
  [`rand-03`], [0], [22,065], [5],
  [`rand-04`], [0], [22,065], [5])

#image("diagram.svg", width: 100%)

The original n=42 D4 panel now has 10/10 terminal attempts: seven accepted certificates and three producer contains-one outputs. Five certificates have the strict count gap needed for LFD ≥ 5. The two recovered certificate files, receipts, evidence archives and publication acknowledgements are in the public release `semaev-closure-certificates-20261029`. Every asset passed anonymous HTTPS and canonical S3 download/hash readback. Small raw transcripts and results are bound by `runs/n42-retained-recovery-001/manifest.json`; certificate binaries are in the release.
