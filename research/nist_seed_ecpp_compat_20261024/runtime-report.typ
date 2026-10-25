#set page(paper: "a4", margin: 19mm)
#set text(font: "Helvetica", size: 9.5pt)
#set par(leading: 0.58em)
#set heading(numbering: none)
= Recovered ECPP: independent runtime controls
2026-10-24 · Engineering observations · Named curve orders executed: *0*

The fixed ECPP V3.4.1 32-bit binaries now execute in fresh offline QEMU VMs.
The report records bounded compatibility and failure controls. It identifies
no common omitted-curve property or historical acceptance rule.

== Recorded results
#table(columns: (1fr, 2.2fr, 1fr), inset: 6pt,
  [Check], [Actual scope], [Recorded result],
  [Arithmetic], [69 vectors, 1–521 bits; 5 exact comparisons each], [345 pass],
  [Prover], [4 normal inputs; CM-only 101; empty/missing catalog], [7 expected behaviors],
  [Checker], [5 positive and 4 negative fixtures], [9 expected outcomes],
  [Binding], [9 saved checker cases + 7 injected failures], [16 pass],
  [Framing], [17 saved serial transcripts + 9 corruptions], [26 pass],
  [Named cohort], [11 omitted + 10 published exact UIDs/orders pinned], [0 executed],
)
Binding and framing reuse saved outputs. These counts are not independent
curve samples. The arithmetic-only bring-up qemu-v2 and full controls qemu-v3
use the same 69 fixed vectors.

#figure(image("runtime.svg", width: 100%, height: 105mm, fit: "contain"), caption: [Solid nodes record completed engineering controls. Dashed nodes remain unresolved. Source: runtime.dot; records: attempts/qemu-v3, admission-v1 and framing-v1.])

#pagebreak()
== What the failure controls show
Original full catalog: prime 101 is accepted. N−1/N+1 disabled and only the
discriminant catalog deliberately emptied: prime 101 is labeled composite,
after two exhaustion messages and a retry. Missing catalog: child exit 139.
These controls repeat the prior Docker observations in an independent runtime.
They do not show failure on any omitted curve order.

The legacy checker exits zero on all nine fixtures, including rejected and
malformed inputs. Strict admission therefore binds root, complete grammar,
sentinel, chain order/divisibility, theorem route and checker step count, while
guest framing checks completion, ABI and watchdog/process status.

*The binding reader is not an independent general mathematical verifier.*
Earlier order/primality certificates and the affine CM-only 101 check remain
separate evidence. The original source-certif2 is an expected rejection;
its separately preserved current-reader variant is an expected acceptance.

== Workload and runtime
QEMU 11.0.2 on macOS arm64; pinned Alpine 3.20.10 Linux x86 kernel. Fresh
one-CPU VM; 256 MiB RAM; no host disks or network. Root-owned read-only inputs;
legacy child uid/gid 65534. Child address-space limit 128 MiB, CPU/guest alarm
30 seconds, host watchdog 90 seconds. Actual peak memory and guest CPU
consumption were not measured. These limits are not consumption measurements.

#figure(image("runtime-times.svg", width: 100%), caption: [17 VM host elapsed measurements, one per case. Includes emulation and boot; no historical runtime or speed advantage is inferred. Data: attempts/qemu-v3/COMPLETE.json.])

#pagebreak()
== Reproducibility and source identity
Exact commands, input hashes, raw serial, stderr, statuses and host elapsed
time are retained in each attempt. Controls ran in the private artifact
directory during a Conductor outage; completed records were copied unchanged
after scope acquisition recovered. RUNTIME_LOCATION.json binds that location.
The earlier qemu-v1 handle disappeared before any recorded compiler/guest
result; its observed empty output is retained without inventing an exit reason.

Commands: qemu_controls.py --attempt qemu-v2 --arithmetic-only;
qemu_controls.py --attempt qemu-v3; admission_controls.py; framing_controls.py.

runtime-bindings.json inventories original data and executable content hashes.
runtime-payloads retains four exact executables in canonical gzip form; all
four content digests round-trip. The kernel official bundle checksum matched.

#set text(size: 8pt)
Kernel SHA-256:
#raw("ce1f6dad86646efaa980fed238c7ed7e4189fd90c30f99a3788df9c9429cc5c9")

ECPP package SHA-256:
#raw("0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f")
#set text(size: 9.5pt)

The earlier source report documents a 1996 thesis citation to this package
filename. It does not authenticate the mirrored bytes as a 1996 capture or
establish use by the original generator.

== Remaining work and interpretation boundary
The full 21-order cohort is pinned. Its substantive replay still needs the
complete frozen execution contract, trial plan, committed Coordinator approval
and handoff. The configured Coordinator backend probe reports its API key
unset and the backend unusable. No model substitution or approval is asserted.
COHORT_PROTOCOL_DRAFT.md records inputs, fixed configuration, censoring and
remaining execution work. It is not an approved protocol.

If a later run separates the eleven omissions, it first establishes behavior
of this artifact and configuration. Independent replay, wider prediction and
original-caller provenance are separate requirements. ECPP uses auxiliary
curves over the integer n being proven prime, distinct from the cryptographic
curve over F_p. Historical use and any ECDLP advantage remain unestablished.

Evidence: attempts/qemu-v3/COMPLETE.json; attempts/admission-v1/COMPLETE.json;
attempts/framing-v1/COMPLETE.json; runtime-summary.json; cohort-inputs.json;
runtime-bindings.json; prior nist_seed_ecpp_source_20261024/report.md.
The canonical admission diagram was refreshed. Prior report/PDF remain the
historical partial snapshot. No mathematical frontier graph changed.
