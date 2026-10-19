#set page(paper: "a4", margin: 18mm)
#set text(font: "Libertinus Serif", size: 9.4pt)
#set par(leading: 0.45em)
= Compact candidate: exponent 8191
EXP-ISOU-feb102 / GOAL-ISOU-f30a07
#parbreak()
Descriptive run report only: native outputs and recorded costs. No evidence-review decision or scientific promotion. One EXP/session report covers constructor RUN-ISOU-bdbf5d and the dependent verification nonstart RUN-ISOU-2b2372.
#image("flow.svg", width: 100%)
== Actual trial counts and results
Two phases were planned. One native constructor started and returned REJECTED at the Lucas–Lehmer gate; no certificate was emitted. The second adapter recorded NOT_STARTED because its construction/certificate gate was unmet. No native verification process ran. No candidate was substituted and no trial was repeated.
Constructor invocation: 2026-10-16 10:46:19 UTC; adapter terminal and conditional-verifier invocation: 10:46:20 UTC. The latter is an adapter timestamp, not a native verifier start.
#table(columns: (2fr, 1.4fr, 1.5fr), inset: 4pt, stroke: 0.4pt + luma(80%),
[Recorded quantity], [Constructor], [Native verification],
[Public native status], [REJECTED], [NOT_STARTED],
[Native resource status / exit], [FAIL / 1], [unavailable],
[Worker arithmetic record elapsed], [372 ms], [unavailable],
[Worker resource elapsed], [385 ms], [unavailable],
[OS real / user / system], [0.40 / 0.32 / 0.01 s], [unavailable],
[OS CPU sum, derived], [0.33 s], [unavailable],
[Sampled worker peak RSS], [2,932,736 bytes], [unavailable],
[Unavailable RSS samples], [0], [no process],
[Certificate], [not emitted], [no input certificate])
CPU sum is 0.32 + 0.01 seconds. Its scope is the public native constructor and waited descendants, excluding build, orchestration and all other trials. Both thin adapters exited0 to acknowledge observation delivery. Canonical cpu_seconds:null fields remain unchanged. One native observation has no between-run uncertainty estimate or performance ratio.
== Parameters, host and provenance
Candidate degree expression: $2^8191 - 1$. Intended source: exact registered SEC2 secp256k1 model, a=0, b=7, prime field and trusted p/n parameters fixed in the pinned source. No geometric map degree, point transport or compact certificate was admitted here. Native constructor error reports a nonzero Lucas–Lehmer terminal residue, retained in full in raw JSON; independent arithmetic review remains separate.
Native bounds were 1800s construct, 3600s verify and 8 GiB sampled worker RSS, 25ms sampling / 100ms monitor grace. They were retained unchanged. Shared Apple M4 Pro / Darwin arm64; detailed host and launch-load metadata are in both environment.json companions.
#parbreak()
#text(size: 8pt)[
Source commit: e82d80feaf82d3730576ccd9137911b336f9dab8; dirty=false.\
Executable SHA256: b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b\
Raw archive SHA256: 52301500bbeaa1d6bce211746657b6d66968cd4efd4c6fff6bbbb5ed5901c4f6
]
#parbreak()
The 14,903-byte archive seals34 original raw files, every per-file hash, full residue/error, both run trees, metadata collector and launcher/admission/timestamps. All14 declared release artifacts and34 raw hashes were checked. Frozen inputs and executable retained their hashes. Preparation controls remain94 passed,0 failed; no controls were rerun in this trial. Serving model/effort unexposed.
A flow diagram is used because only one native phase ran and no comparable completed measurement exists. Full commands, exact curve tuple, source/release bindings, missing data and render receipts are in report.md. The original rejection and nonstart records remain unchanged.
