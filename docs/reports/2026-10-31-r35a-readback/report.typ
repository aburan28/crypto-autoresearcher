#set page(paper: "a4", margin: 1.7cm)
#set text(font: "DejaVu Sans", size: 10pt)
#set heading(numbering: none)

= R35a publication readback and certificate replay

2026-10-31 UTC. Read-only audit of the named R35a Boolean closure certificate. The public release's listed assets, tracked receipt, decompressed certificate, and every receipted evidence member matched their recorded SHA-256 values. A one-byte receipt mutation was rejected under optimized Python.

#image("custody.svg", width: 100%)

_Figure 1._ Green boxes show the independently rechecked custody and degree-4 certificate predicates. The dashed box lists separate obligations for an exact global last fall degree. Source: `readback.json`, `replay/replay.json`, the tracked R35a receipt, and the dated verification correction.

== Pinned checker result

The pinned checker source SHA-256 is `13d926240a99de4b3eede374932fe245d62e7de65102a4fdf2cccfb0e4463877`. It ran on the SHA-matched 44,830,496-byte certificate under a 12 GiB virtual-memory limit, with 39,855,042,560 bytes available at admission and a 16 GiB system reserve. It completed in 23.166 seconds, exited zero, and produced empty stderr. All 13 substantive stdout lines match the historical receipt after timing annotations are removed.

The checker verified that the dual map is onto, annihilates all 35 input equations, sends 1 to a nonzero vector, and has a kernel closed under every variable multiplication on degree at most 3. Thus `1 ∉ W₄` and `codim W₄ ≥ 5,287` for R35a. This is a lower bound: the dual certificate does not show that its kernel equals `W₄`.

== Claim boundary and next gate

The historical receipt itself records `d_ref_exact: null` and `d_ref_lower_bound: 5`. The dated correction explains why its certificate cannot establish the producer's exact dimension. The verification record separately describes an unsatisfiability count and two restricted degree-4 refutations for an upper bound at degree 5. Those steps, and the Boolean-to-polynomial closure bridge, are the next independent checks before an exact `d_F` value can be promoted.

The full source paths, release name, reproduction commands, hashes, negative control, and machine-readable replay are in the adjacent `README.md`, `readback.json`, and `replay/` files. This report introduces no performance measurement or dashboard value.
