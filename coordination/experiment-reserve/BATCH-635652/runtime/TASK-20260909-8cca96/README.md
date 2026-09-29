# Native group-OOM integration correction

This source package implements TASK-20260909-8cca96 under DEC-20260909-201769. It is not authorized for live Docker, cgroup, privilege, migration, pressure, or scientific execution.

The source changes address NF-01 through NF-05: production serialization joins host parsing; memory delegation is disabled before supervisor return; generated nonce and identity are verified before payload copy/start or ownership-dependent cleanup; supervisor membership is read back; and enumeration errors fail closed. The original source and failed producer records remain immutable.

The fixed suite preserves 81 original case registrations and adds 18 regression controls. Its Docker and cgroup observations are injected. Five bounded current-user POSIX fixtures exercise pipes, barriers, draining, signalling, and reaping. No command contacts Docker.

The intended changes to old test expectations are explicit: inspection refusal no longer removes an unverified container; fake cgroup writes model kernel delegation semantics; and positive host reports are produced by the actual serializer from a supervisor outcome instead of a fabricated schema string. Historical attempt counts are not carried into current accounting.

Each invocation uses a unique temporary attempt directory, pre-reserved source hashes and copied source bytes, redirected streams, and full inner and outer tool custody. The canonical receipt is created only after all intended attempts terminate. Observed memory data is not a hard kernel-enforcement claim.

The protocol binding lists all 57 frozen inputs, the exact current code hashes, and all 99 registered cases. The final execution report and receipt will state actual results. Fresh independent complete source review is required before any operational handoff.
