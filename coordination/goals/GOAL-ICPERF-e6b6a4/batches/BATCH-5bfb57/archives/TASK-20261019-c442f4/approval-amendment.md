# Prospective confound-control amendment

Experiment: `EXP-ICPERF-515ae3`. Approval task: `TASK-20261019-c442f4`.
The design-archived `review_required` specification and `prepare_packet.py` remain
byte-identical to content commit `04f95718c8bbb5c81db2f4004c0a0cdd337d661f`.
Before any approval archive or scientific call, ledger validation exposed two
missing required fields in the prospective `approved` specification:
`variable_ledger` and `prediction_provenance`. This amendment changes only
prospective approval bytes through `approval-preview/amend_confounds.py`.

The three fixed planted cells and their 600-second per-cell guards remain the
same. The decisive comparisons are absolute exact checks of custody, monitor
failure, polynomial roots, base membership, signs, lifts and full target
points. Timing, RSS, phase telemetry and stop caps are descriptive or censored.
No arm runtime, factor-base, yield or complete-cost comparison is authorized.
The arms differ jointly in base, target, encoding and equation shape, so their
cross-arm comparison is explicitly confounded. An A/A runtime control is absent;
no runtime difference is used for a decision. Prior 300-second results and
integration checks are disclosed as in-sample calibration data. A missing
certificate at the cap remains unresolved; a wrong accepted root invalidates
the instrument.

The exact preapproval probe on the amended prospective packet returned
`approvable: true` and `blockers: []`. The packet remains SHA-256
`578be8db07c3379438c7d2f7f818f1444efb7fdc7484b6c798bf0eec8134d396`.
The amended assessment is SHA-256
`6d9e62fca5b7745bb77abd7c119bde8ece2b5c90ab2fa385199423d6e2249766`.
The amended prospective hashes are specification
`3e24c2c1df6451f39388082a6b9594c6a6491f86c3075e1bf5878d6093792a30`,
trial plan `08f32f02a191dfd16f5342540716a327da73f5091528bac07cf5ee77cdb7cbc9`,
queue `9ac73b5884df9635a350367556a930d354dfa9622c701dec5f229e60d5e9ceb0`,
and executor handoff `bb0099b114e3fee96f93c54e3e1208d3934317780e1ec1624f37eee3758b72cc`.
The original false probe after installing canonical approved bytes was not an
approval; the canonical draft was restored from the pushed source before the
true probe, then the amended approved preview was installed byte-identically.

The repository-wide ledger validator still reports 163 inherited errors, with
none referencing this experiment, decision or handoffs. The required result
of this amendment is a committed and content-bound approval archive followed
by `newest_experiments.py` reporting `execution_state: ready`; it is not a
scientific result.
