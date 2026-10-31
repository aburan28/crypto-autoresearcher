#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)
= n50 poly01 cascade terminal record

The next original n50 input, `fresh-n50-poly-01-D5-cascade01`, had zero solutions in a fresh exhaustive count. Its degree-three producer recorded `M3_one 1` and `W3_one 1`, wrote no seed certificate, and the frozen cascade stopped. Degrees four and five were not attempted; this one named-input run supplies no new LFD lower bound.

#image("diagram.svg", width: 100%)

The terminal record, counter and producer transcripts, launch gate, and file hashes are in `runs/n50-poly01-cascade-local-terminal-001/`. Admission sampled 37,482,303,488 available bytes against a 19,327,352,832-byte requirement and held both campaign locks. The producer used one thread, a 16 GiB cap, 60,000-row chunks, and a 21,600-second command watchdog. No comparable timing metric or population inference is reported.
