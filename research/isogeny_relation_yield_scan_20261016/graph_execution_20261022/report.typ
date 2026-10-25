#set page(paper: "us-letter", margin: 0.72in)
#set text(font: "Helvetica", size: 8.6pt)
#set heading(numbering: none)

= P29 graph-arm phased execution
Fixed public controls, 2026-10-22 PDT. Raw records: `bb8caa9722`; executable
receipt: `3813ea4635`. Conductor T-4750 / T-4753.

This report describes implementation-control observations. It makes no
discovery-stream yield or ECDLP cost inference.

== Exact tested pair
Source: $E / F_(320092037): y^2=x^3+105931039 x+284015384$,
prime order $320091991$, $G=(0,50656410)$. Vertex 8 after eight archived
degree-7 separable maps over the same field:
$y^2=x^3+218000848 x+38636553$,
transported $G=(148951155,154566416)$. The source `low_x` base and its
transported image have 256 x-orbits each; the fixed public targets use the
same scalar coefficients.

#figure(image("counts.svg", width: 100%), caption: [Exact source and vertex-8 ordered-count vectors. Both saved 128-target controls have five nonempty targets and 30 ordered triples; source and graph curves overlap exactly in this plot.])

== Recorded attempts and verification
Control 1 stopped before phases because checkout Python 3.13 lacked `psutil`.
Control 2 stopped at input verification because the first wrapper invocation
used positional arguments where flags were required. Both failure records
remain saved. Control 3 passed with eight fixed targets and zero triples.
Controls 4 (vertex 8) and 5 (source) passed with 128 targets each. Their C++
ordered-count vectors and complete Rust collector records are byte-identical.
Each Python replay independently found five useful targets, five verified
triples, and rank five. The binaries, commands, receipts, logs, and failed
attempts are retained in `graph_execution_20261022/`.

== Boundary and next action
The graph-specific runner preserves four phase receipts and requires frozen
admission in scientific mode. The fixed controls are outside discovery and
confirmation. Bind target roots, check-arm quotas, source hashes, admission
and output paths in a runnable Coordinator contract before scientific trials.
