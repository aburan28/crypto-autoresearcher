# Independent runtime admission for recovered ECPP V3.4.1

2026-10-24. This is an engineering observation report. No named NIST/ANSI
curve order has been executed in this round, and no common omitted-curve
property or historical acceptance rule is asserted.

## What completed

The unchanged 32-bit prover, checker and arithmetic binaries now execute in
fresh offline QEMU VMs without Docker. The pinned Alpine 3.20.10 Linux x86
kernel boots a small custom static init. Each legacy child runs as uid/gid
65534 with read-only inputs, RAM-backed temporary output, no disks/network,
one emulated CPU and fixed memory/time limits. QEMU 11.0.2 runs on the existing
macOS arm64 host. The original source/data bodies remain unchanged.

| Recorded check | Actual scope | Outcome |
| --- | --- | --- |
| Arithmetic | 69 fixed vectors, 1–521 bits; 5 exact Python comparisons each | 345 comparisons pass |
| Prover | 4 normal prime/composite inputs; CM-only 101; empty/missing catalog controls | All 7 expected behaviors reproduced |
| Checker | 5 positive and 4 negative fixed fixtures | All 9 expected admission outcomes reproduced |
| Certificate binding | 9 saved checker cases and 7 injected binding/process failures | All 16 checks pass |
| Guest framing | 17 saved serial transcripts and 9 corrupted framing/error cases | All 26 checks pass |
| Named curve cohort | 11 omitted + 10 published exact UIDs/orders pinned | 0 executed |

The counts overlap deliberately: binding and framing controls reuse saved
transcripts; these are not independent curve samples or extra primality tests.
`qemu-v2` was an arithmetic-only bring-up. `qemu-v3` repeats those same vectors
as the first stage of the complete runtime-control sequence.

## Two observed failure behaviors

With the original full catalog, prime 101 is accepted. With N−1/N+1 disabled
and only the discriminant catalog deliberately emptied, the same prime is
labeled composite after two “No next D” messages and a retry. With the catalog
missing, the child crashes with exit 139. These modified-data controls reproduce
previous Docker observations in an independent runtime. They establish a
specific software failure path; they do not show that the original catalog
fails on any of the eleven omitted orders.

The legacy checker returns exit zero for every one of the nine fixtures,
including rejected or malformed inputs. Exit zero is therefore insufficient
for admission. A separate strict reader now binds the requested integer, full
certificate grammar, complete final sentinel, recursive chain order/divisibility,
theorem route and exact checker step count. It rejects wrong roots, missing or
duplicated steps, appended certificates, incomplete input and process errors.
The guest framing checks independently reject absent begin/exit/completion
markers, duplicate transcripts, a wrong ABI and host/guest watchdog failures.

`certificate_admission.py` is a format/binding check around the legacy checker.
It is **not an independent general mathematical certificate verifier**. Earlier
independent order/primality evidence and the affine check for CM-only 101 remain
separate. In particular, the original source-certif2 is an expected rejection;
the separately prepared current-reader variant is an expected acceptance.

## Commands, identity and retained data

- `python3 qemu_controls.py --attempt qemu-v2 --arithmetic-only`
- `python3 qemu_controls.py --attempt qemu-v3`
- `python3 admission_controls.py`
- `python3 framing_controls.py`

QEMU controls ran in the chat's private artifact directory while Conductor
was unavailable, using byte-identical copies of the fixed source, binaries,
fixtures and data. `RUNTIME_LOCATION.json` identifies that directory. Exact
commands and paths remain in each started.json; completed raw records were
copied unchanged into this study after scope acquisition recovered. The
repository attempt `qemu-v1` lost its session handle before any recorded
compiler/guest result; its empty-directory/no-executable observation is retained
without fabricating an exit reason or treating it as mathematical evidence.

`runtime-bindings.json` binds all original data files, the kernel receipt and
four executable content hashes. `runtime-payloads/*.gz` now durably retain the
exact executed binaries, including the new init. They were compacted with
`tools/artifact_store.py`; all four content digests round-trip correctly.
The kernel bundle's official checksum matched before boot. The kernel digest
is `ce1f6dad86646efaa980fed238c7ed7e4189fd90c30f99a3788df9c9429cc5c9`.
The ECPP package digest remains
`0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f`.

Evidence: [complete VM records](attempts/qemu-v3/COMPLETE.json),
[binding records](attempts/admission-v1/COMPLETE.json),
[framing records](attempts/framing-v1/COMPLETE.json),
[runtime summary](runtime-summary.json),
[full prospective cohort](cohort-inputs.json).
These are internal retrieved artifacts from this session. The acquired
period-source provenance is documented in the earlier
[source report](../nist_seed_ecpp_source_20261024/report.md), including the
1996 thesis citation to the package filename. That citation does not prove
these exact mirrored bytes existed in 1996 or were used by Reiter.

## Limits and next discriminator

This removes the Docker runtime obstacle for the bounded engineering controls.
The original generator/caller remains absent. A substantive full-cohort run
still requires the complete frozen execution contract, executable trial plan,
committed Coordinator approval and handoff under repository rules. The
configured Coordinator backend probe reports its API key unset and the backend
unusable; no model substitution or scientific approval has been invented.
No credential is recorded. The [prospective draft](COHORT_PROTOCOL_DRAFT.md)
states the complete input cohort, fixed primary configuration, censoring rules
and remaining execution work. It is not an approved protocol.

The historical question remains conditional on actual visitation of the eleven
seed windows. A later split would first identify behavior of this artifact and
configuration. Historical use would require original-caller provenance or
independent predictive evidence. An ECDLP advantage would require a separate
mechanism and cost analysis. ECPP's auxiliary curves over the candidate integer
n are distinct from the original cryptographic curve over F_p.

The runtime diagram is [runtime.dot](runtime.dot) / [runtime.svg](runtime.svg).
The [elapsed-time SVG](runtime-times.svg) plots the 17 recorded VM host times
from qemu-v3; one measurement per case, including boot and emulation, with no
estimate of 1997 runtime. Actual guest CPU consumption and peak memory were not
measured; configured limits are not presented as consumption. The canonical
admission.dot/SVG was updated to these completed controls. The original report
and PDF are retained as the earlier partial-admission snapshot. No mathematical
frontier, isogeny or endomorphism graph changes from this engineering evidence.
