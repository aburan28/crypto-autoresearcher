#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt, font: "Libertinus Serif")
= n48 poly04 local degree-five attempt
The independent D4 checker accepted the seed (codimension at least *26,570*) and the fresh exact count found *0* solutions. The D5 quotient producer returned `projection_kills_one` with 42,791 working coordinates and relation rank 42,791. No D5 certificate was produced; this run establishes no LFD >= 6 bound or upper bound.

#image("flow.svg", width: 100%)

The run was admitted under a 24 GiB child cap and finished without timeout. Recorded stage durations: D4 check 483.919 s; exact count 18.167 s; D5 producer 971.336 s. Wall times are invalid for performance comparison on the shared host. Raw receipts and transcripts: `runs/n48-poly04-d5-local-terminal-001/manifest.json` (19 hash-pinned artifacts). Frozen protocol SHA-256: `49edc7d0db15afebf7e5703edf5099a352ae0de39b3973ebbdd760f02cd966e0`.
