# Independent runtime control protocol, 2026-10-24

Engineering admission only. No named NIST/ANSI order is executed by this control
program. The unchanged static binaries are bound by summary.json. The Alpine
3.20.10 x86 kernel is bound by the existing kernel-receipt.json. A new static
32-bit init launches one child per fresh QEMU VM, without disks or networking.

Fixed limits: one emulated CPU, 256 MiB VM RAM, child address space 128 MiB,
30 CPU seconds, 30 second guest alarm and 90 second host watchdog. Child runs
as uid/gid 65534. Inputs belong to root and are read-only to the child; only
RAM-backed /tmp is writable. The host shares no filesystem with the guest.
Host timings include boot and emulation and cannot estimate 1997 runtime.

Controls in order: the existing 69 arithmetic vectors (345 exact comparisons),
normal prover inputs 101, 65537, 15, 341, CM-only 101, empty-catalog CM-only
101, missing-catalog CM-only 101, and the nine fixed checker fixtures from
checker_controls_v2.py. Expected labels and checker acceptance are fixed there.
Empty-catalog misclassification and missing-catalog crash are deliberate
failure controls, not admission success for mathematical results. All nine
checker fixtures repeat because the kernel/runtime changed.

Require the init ABI 4/4/4, exactly one guest begin/completion and child-exit
marker, QEMU's controlled exit 33 and no timeout. Arithmetic output is checked
against Python exact arithmetic. Positive checker fixtures require every
reported step to succeed and complete sentinel input. Negative fixtures must
fail that admission predicate. This predicate is only a bounded engineering
control, not an independent general certificate verifier. A mismatch, crash
or timeout retains all bytes and stops admission; no named-order launch follows.

Each attempt uses a new output directory. Preserve source, command, input and
initramfs hashes, raw serial output and stderr, child status, limits and host
elapsed time. Missing completion means indeterminate, never composite.

No canonical mathematical graph changes: this controls a runtime. The new
runtime diagram/report will cite all attempts and the existing source report.
