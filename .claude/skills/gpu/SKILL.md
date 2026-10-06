---
name: gpu
description: "Inspect or improve CPU/CUDA arithmetic kernels, batched step throughput, GF(2) GPU updates, register/occupancy bottlenecks and GPU benchmark correctness. Use for kernel engineering and supplied GPU diagnostics. Use ops for cloud resources and run for existing arithmetic or step trials."
---

# GPU engineering

Read `harness/gpu/README.md` or `src/crypto_autoresearcher/gf2/gpu/README.md` for the selected kernel. Inspect `harness/gpu/mont256.h`, `rho_kernel.cu`, or `src/crypto_autoresearcher/gf2/gpu/tail_update.cu` as appropriate.

1. Identify the primitive, data layout, exact arithmetic domain, compiler/runtime and hardware. Do not confuse prime-field Montgomery kernels with ECC2K carryless arithmetic from another repo.
2. Preserve CPU/reference agreement, carry/reduction invariants, exceptional cases, coefficient bookkeeping, GPU synchronization and output checks. Validate arithmetic before timing.
3. Inspect memory traffic, arithmetic counts, register use, occupancy, launch geometry and batch sizes with the available profiler/source. Mark theoretical throughput assumptions explicitly.
4. Keep edits scoped to arithmetic or instrumentation. Test meaningful boundary cases and reference equivalence; retain a matched control for a performance change.
5. Use bench to report useful-step throughput and full accounting. Use ops for an authorized resource change; use run for existing benchmark processes. Never infer completion of a live campaign from kernel iterations.
6. Return the kernel diff, correctness evidence, bottleneck estimate and measured limits. An unavailable GPU is an infrastructure impediment, not negative algorithmic evidence.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
