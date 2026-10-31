#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)
= n49 and n50 frontier terminal records

The n49 poly00 attempt retained an independently accepted degree-four certificate with codimension at least 32,291 and a fresh exact count of two solutions. Its degree-five producer reached its frozen watchdog after 21,621.6 seconds recorded by the wrapper. Nine durable checkpoints were published, but no degree-five certificate was produced.

The next original frontier input, n50 poly00, had zero solutions in a fresh exhaustive count. Its degree-three producer reported `W3_one 1` and wrote no seed certificate. The cascade stopped before degree four or degree five.

#image("diagram.svg", width: 100%)

The n49 run ID is `n49-poly00-D5-local-002`; its source record is `runs/n49-poly00-d5-local-terminal-002/manifest.json`. The n50 run ID is `fresh-n50-poly-00-D5-cascade01`; its source record is `runs/n50-poly00-cascade-local-terminal-001/manifest.json`. The latter archive includes the launch gate and fresh count transcript. The archived manifests hash every copied file.

These are two named-input outcomes. The n49 timeout is not a computed degree-five closure, and the n50 result has no degree-three certificate. Neither yields an LFD lower bound of six. The next original input is n50 poly01, subject to a separate frozen protocol and fresh admission.
