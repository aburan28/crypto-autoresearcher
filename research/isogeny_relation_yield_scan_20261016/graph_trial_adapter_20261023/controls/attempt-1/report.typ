#set page(paper: "a4", margin: 20mm)
#set text(font: "Helvetica", size: 10pt)
= Graph trial adapter implementation control

2026-10-22. P29 vertex 0, fixed public roots, eight target coefficients per arm.
The native `low_x`, graph transported, and coordinate transported arms each
completed the phased wrapper and independent checker. Both transported outputs
matched native targetwise triples, ordered counts, and rank metrics. Each arm
recorded zero useful targets and zero rank increments in this small control.

#image("control_flow.svg", width: 100%)

The first two attempts failed for missing Python dependencies. The successful
isolated environment used psutil 7.2.2 and sympy 1.14.0. Exact commands,
digests, raw outputs, logs and receipts are in the sibling control directories.
These controls check adapter plumbing and transport conservation. Scientific
admission, graph-wide relation yield, and complete ECDLP timing remain open.
