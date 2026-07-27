# EXP-MLKEM-003 implementation notes

Executor task: `TASK-20260724-235`. Observations only.

## Harness

- Extended EXP-MLKEM-002 structure with `multiclass_generator.py`, `conformance_probe.c`, `decap_boundary_probe.c`, and `liboqs_probe.c`.
- wolfSSL static libraries reused from `/tmp/exp-mlkem-002/builds`; EXP-003 probes recompiled against those libraries.
- Second implementation: liboqs `0.12.0` (`f4b96220e4bd208895172acc4fedb5a191d9f5b1`).

## Anchor

- Named: `NIST_ACVP_ML-KEM_encapDecap_FIPS203_internalProjection_via_liboqs_in_tree`
- Grade: `strong`
- Retrieval attempts recorded in RUN-MLKEM-009 raw.json (NIST ACVP-Server URLs + liboqs in-tree internalProjection).

## Protocol deviations

See `execution-report.yaml` `protocol_deviations`.

Additional notes:

- Mutation cap `20000` applied per `(target, parameter_set, class)` as
  implied by the per-class stage stop rule; all G1/G2/G3 wolfSSL x86
  classes completed without capping.
- Helper `implementation/liboqs_probe.c` is the second-implementation
  adapter (not listed separately in `required_artifacts`).
- Known wolfSSL v5.9.1 NEON half-block silence (EV-MLKEM-005) was
  observed again on PREFIX-NEON and treated as the established defect,
  not as a new finding.

## Scope

No key recovery, oracle construction, exploitation path, disclosure, or
deployed-system interaction occurred. Library comparison logic was
not modified.
