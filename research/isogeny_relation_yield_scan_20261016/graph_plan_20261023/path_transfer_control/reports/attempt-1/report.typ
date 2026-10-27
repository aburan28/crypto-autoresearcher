#set page(margin: 0.65in)
#set text(size: 9pt)
= P37 path-transfer adapter control

*Implementation-control observation only. This fixed-scalar path check is not relation-yield, rank, or unknown-log data, and it does not authorize a graph-study trial.*

== Scope and literature

The control maps one public source G,Q pair across 24 saved P37 edges, then checks it against the prepared endpoint and independently replays each edge with Sage. It uses a fixed known-scalar fixture and performs no discovery, confirmation, collector, solver, or rho trial.

Petit, Kosters, and Messeng (PKC 2016) study prime-field factor bases defined through rational maps, including an auxiliary-curve/isogeny construction. Their experiments are limited to small parameters and do not establish a practical advantage. This control measures only path transfer, one input to a future end-to-end cost account. [Primary source](https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf).

== Typed path and exact identities

Source `EC1P37Cp37sourceh7a9e23a954c5` has UID `urn:ec-record:1:sha256:7a9e23a954c5a7d9f76770b77e75d271ef53684802a5f9ce24deba36a3b39fc5` and model y²=x³+46677163888x+11713815639 over Fp, where p=81640512137 and prime subgroup order r=81640511861. Endpoint `EC1P37Cp37v0024h922b300022ce` has UID `urn:ec-record:1:sha256:922b300022ce5580d24d166a6bc7c01ce02a15c86443f84bc34308a653126029`. The saved route contains 24 degree-7 separable isogenies over Fp; its walk digest is `523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281` and kernel-chain digest is `a71ba84e6b95916bfc32c71a5e640a886e1f01dc235821b813d05bbeafa28604`. Since prime r differs from 7, each edge is injective on the order-r subgroup. The exact G,Q pair reached the prepared endpoint and the independent replay passed.

#figure(image("path-transfer.svg", width: 100%), caption: [Typed source-to-endpoint path and subgroup-transport control.])

== Recorded timings

One pass per distinct edge (n=24; no edge repetitions):

#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  [Quantity], [Total], [Per-edge median], [Per-edge range],
  [Map setup], [28.854436 s], [1.109505 s], [0.160616–2.554260 s],
  [Fast map of G,Q], [0.001641 s], [0.000028 s], [0.000023–0.000550 s],
  [Direct Sage validation], [8.440898 s], [0.316485 s], [0.044733–0.841402 s],
  [Runner process wall], [75.066430 s], [—], [one process],
  [Independent checker wall], [48.246685 s], [—], [one process],
)

#figure(image("edge-times.svg", width: 100%), caption: [Measured per-edge values; edges are distinct map instances, not replicate draws.])

The runner and checker process wall times include separate Sage startup. No uncertainty interval is reported because each edge was measured once. The verification phase is separate from the fast map time. These are path-transfer measurements only; no curve-level yield or ECDLP cost follows from them.

== Evidence and next check

Control status `completed`; independent check `pass` across 24 edges. Raw record `attempt-1/transfer.json`; commands and hashes `attempt-1/command.json`; full report data in `curve-identities.json`. Environment: macOS-26.6-arm64-arm-64bit-Mach-O; Sage 10.10.rc0.

The remaining task is to bind this measurement to each finalist in the frozen experiment protocol, then include transfer and setup alongside relation collection, linear algebra, individual logs, verification, and matched same-point rho. Coordinator admission and committed scientific target roots are not yet available.
