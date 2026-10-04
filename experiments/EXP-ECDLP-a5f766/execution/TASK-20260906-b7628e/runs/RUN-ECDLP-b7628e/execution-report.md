# Execution report: infrastructure failure

EXP-ECDLP-a5f766 / TASK-20260906-b7628e / RUN-ECDLP-b7628e.
Terminal state: failed_infrastructure. Exactly one command invocation; no retry.

The process failed on macOS at source/run_audit.py:38 while installing
the 2 GiB address-space ceiling:
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
raised ValueError: current limit exceeds maximum limit. The directory had
been created exclusively, but scientific stages and normal artifact writing
had not begun. Zero of 96 rows, zero point counts, zero rejection checks,
and zero certificate evaluations executed.

These partial artifacts were constructed after failure by the Executor under
the same declared write scope with Coordinator confirmation. stderr.log is the
exact observed traceback; empty data files and NOT_EXECUTED fields preserve
absence of measurements. Outer exec_command wall time was 1.18865425 seconds;
CPU, RSS and stage times were not captured and remain null. Sources are frozen
and unchanged. No hypothesis comparison, mathematical negative, or proof
outcome is asserted. The completion gate did not pass.

A separate read-only post-failure probe reported RLIMIT_AS soft/hard values
9223372036854775807; this does not resolve why the attempted Darwin limit
assignment failed. A future additive implementation should use a portable
resident-memory watchdog or a supported platform memory limit, preserving the
2 GiB machine-protection intent, and test that operational mechanism before
a new separately authorized immutable scientific run. No such retry or source
repair was performed here.

Executor assessment: protocol incomplete; no scientific measurements; data
quality unavailable; implementation/infrastructure repair and a fresh governed
run required. Independent validation and Coordinator snapshot remain pending.
