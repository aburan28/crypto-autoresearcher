# Frontier checkpoint disk admission

The general lab worker currently declares 10 GiB ephemeral storage. The n47 random00 input has 48 Boolean variables, 213053 seed columns, 1925357 output columns, and 187583 working coordinates. `runtime/frontier-checkpoint-disk-envelope-001.json` records exact conservative byte arithmetic from the committed serializers. These are derived sizes, not measurements.

Two maximum snapshots plus the uncompressed seed occupy 10429731008 bytes, leaving 307687232 bytes before runtime overhead. The conservative certificate bound is 45161173824 bytes and cannot be admitted under 10 GiB. A small fixture or successful matrix restore does not resolve this bound.

Next implementation: bind the disk allowance to the worker request; account for runtime files and restore/download staging; preserve a verified phase 2 checkpoint before export; calculate exact certificate size from its relation rank and refuse/defer export if it will not fit. Any refusal retains state and remains inconclusive for LFD. Qualify the allow/refuse boundaries before frontier use. Do not enlarge a Kubernetes limit through an unsupported tool parameter or let an unchecked output trigger eviction.

Exit: checked arithmetic and actual runtime admission, qualified durable phase 2 export refusal, then a frozen frontier attempt with exact original input and independent final checker.

## Implementation boundary discovered in source

The existing producer saves a phase-2 checkpoint immediately before export, so its publication hook can preserve the completed state and refuse an oversized export. However, restoring a phase-2 checkpoint skips the save/hook path and proceeds directly to export. The worker must apply the same exact output-size admission before launching a restored phase-2 child. Qualify both paths; testing only the publication hook is insufficient.

Retain the native binary unchanged if possible. A wrapper can bind policy to the frozen request and protocol, use verified checkpoint metadata to compute output bytes, account for actual work-directory files plus declared overhead, and emit an explicit deferred-export result after verified publication. A deferred export establishes no lower bound until a final certificate is independently accepted. Existing local case000 checkpoint23 is a small phase-2 fixture suitable for both allow and refuse boundary controls. This guard is not implemented or qualified yet.

## Export guard controls, 2026-10-30

The request-bound export guard passes all 20 frozen local software controls
(ten fresh, ten restored). See
[report](../analysis/semaev-degree-five-quotient-lift/reports/export-guard-001/report.md).
Fresh refusal preserves a verified published phase-2 checkpoint; restored
refusal prevents native launch. Exact-capacity and one-byte-short arithmetic
use the common prelaunch path, as frozen. All 169 raw file hashes verify; the
twenty-row export validates with zero findings.

This closes local guard qualification only. End-to-end frontier worker
integration, startup accounting of seed plus two snapshots plus runtime and
reserve, and cloud qualification remain open. No frontier job was launched
by these controls and no new mathematical lower bound was obtained.

## Integrated worker ready for a bounded frontier attempt

Nine real-cloud worker controls passed across distinct source and restore
pods, with original checker acceptance and exact reference output for all
completed fixtures. See [report](../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-worker-cloud-002/report.md).
The retained n47 request uses streamed seed decoding, event checkpoints,
startup accounting, and exact export admission; its native binary is unchanged.
After the two-snapshot-plus-seed allowance, 256 MiB reserve, measured bundle
files (6,685,871 bytes) and archive (2,521,934 bytes), the declared 10 GiB
capacity has 30,043,971 bytes left before small request/protocol files. This
is arithmetic, not observed frontier disk use. The worker must admit actual
filesystem and cgroup state at runtime; an export deferral remains inconclusive.
