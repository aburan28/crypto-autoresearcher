# QM-ERROR advancement — F-union obligation ledger (BATCH-042 / TASK-20260730-139)

Bounded, zero-compute step under `DEC-20260730-039` / `EV-SSI-041` for
`IDEA-20260729-001` (CSIDH-COLLIMATION-FC0-R2). Executor records observations
only; no official status is changed here.

## The QM-ERROR question

QM-ERROR is the QUERY_MEMORY sub-blocker concerned with the **operational error
account** of the CSIDH collimation attack model. Its committed status is
`f_union_ledger_partial`, established in BATCH-025 (`TASK-20260730-071`): a
**one-directional** symbolic set-union inclusion

```
U = F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ F_tail ∪ F_verify ⊆ F
```

over the seven recovery-spec constituents, with a `Verify=true` success exit and
`F_sim maps_to_F = false` retained. What BATCH-025 recorded is that every named
constituent is a subset of the common failure event `F`. What it did **not**
record is the reverse direction, any probability composition, or a crypto
`Verify` body.

The bounded question for this batch: *can any obligation between
`f_union_ledger_partial` and an actual QM-ERROR error account be tightened from
committed in-repo structure, short of QUERY_MEMORY clearance, without inventing
probabilities, numeric error bounds, security bits, or τ?*

## F-union audit against committed citations

The lineage is committed and checkable:

- **BATCH-023** — channels wired; inclusion into `F` `checklist_only_not_justified`.
- **BATCH-024** (`path_justified_inclusions.yaml`) — each `F_*` given an
  executable scaffold failure path that halts without `Verify=true` and is
  `classified_as_common_F`; `path_justified_on_scaffold`.
- **BATCH-025** (`f_union_ledger.yaml`, `operational_error_composition.yaml`) —
  symbolic set-union `U ⊆ F` with membership rules R1–R5, `Verify=true` success
  exit, `F_sim ∉ U`, no probabilities, no crypto `Verify`.
- **recovery_spec** (`BATCH-013/TASK-20260730-017/recovery_spec.md`) — defines
  the common event `F`, the six-stage object schedule, the per-stage `F_*` maps,
  the unique `Verify=true` success exit, and the "error composition obligation"
  (which states only the *forward* inclusion and asks to identify dependency
  assumptions).

## Outcome: `f_union_tightened` (OBL-2a)

The tightening is the **reverse inclusion at spec-internal scope**, recorded for
the first time (see `f_union_obligation_ledger.yaml`, obligation `OBL-2a`).

recovery_spec §"State and final event" states verbatim: *"All exits are typed
either success (a true verification result) or a named failure constituent of
F."* Its §"Required stages and object schedule" binds each of the six stages to
exactly one constituent, and §"Verification event" makes `Verify=true` the only
success exit. Therefore, by the specification's own exit typing, **any exit that
is not the unique success exit is a member of a named `F_*`** — there is no
un-named residual failure class *within the spec's declared exit set*. This is
the reverse inclusion `F_spec ⊆ U`, which combined with the committed forward
inclusion `U ⊆ F` yields a **spec-internal set equality** `U = F_spec` over the
recovery-spec typed exit set.

This is a genuine, modest, checkable advance over BATCH-025 (which recorded only
`U ⊆ F`). Its value is twofold: it closes the specification-internal direction
definitionally, and — more importantly — it **isolates exactly what remains** by
forcing the host-level, probabilistic, and crypto-Verify obligations to be named
and honestly classified.

### What the tightening is NOT

- **Not** host-level exhaustiveness over the real `CollimationSieve@6f9188e4`
  exit space (`OBL-2b` = `not_supported`; BATCH-020 `no_admissible_pin`;
  `REV-E1`).
- **Not** a probability statement about `F` (`OBL-3`/`OBL-4` = `not_instantiated`;
  inventing probabilities is forbidden; `REV-E2`).
- **Not** a crypto `Verify` body (`OBL-5` = `not_supported`; no-crypto scaffold
  token only; `REV-E3`).
- **Not** QM-ERROR, QM-STOPPING, QM-MEMORY-MAP, or QUERY_MEMORY clearance.
- **Not** a CollimationSieve API invention, a τ, a security bit, a breakthrough,
  or a completion.

### Residual obligations and concrete revisit conditions

| Obligation | Status | Revisit |
|---|---|---|
| OBL-1 forward inclusion `U ⊆ F` | `wired_symbolic` (retained) | — |
| **OBL-2a reverse inclusion (spec-internal)** | **`tightened_from_committed_structure`** | — |
| OBL-2b reverse inclusion (host-level) | `not_supported` | REV-E1 |
| OBL-3 probability composition `Pr[F]` | `not_instantiated` | REV-E2 |
| OBL-4 numeric error bounds | `not_instantiated` | REV-E2 |
| OBL-5 crypto Verify body | `not_supported` | REV-E3 |
| OBL-6 CollimationSieve end-to-end | `not_supported` | REV-E1 |
| OBL-7 `F_sim` non-map retention | `wired_symbolic` (retained) | — |
| OBL-8 overlap/independence handling | `checklist_only` | REV-E2 |

- **REV-E1** — an admissible CollimationSieve pin (BATCH-020 `no_admissible_pin`
  lifted). Shared host gap with QM-STOPPING REV-1.
- **REV-E2** — a committed source assigning per-constituent error probabilities
  or a numeric error model (with the OBL-8 independence/bounding hypothesis
  stated and justified).
- **REV-E3** — a real cryptographic `Verify(x,k')` body.

## Retained controls and boundaries

- Disposition `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` retained.
- QM-STOPPING remains `FAIL`, lane `paused_pending_revisit`; **not reopened**
  (REV-1/REV-2 unmet).
- QM-MEMORY-MAP retained at `numeric_composition_operator_protocol_toy_partial`;
  not advanced.
- BATCH-020 `no_admissible_pin` retained; `CollimationSieve@6f9188e4` untouched;
  BATCH-022 scaffold unmodified; BATCH-014 not equated.
- Zero curve/isogeny/quantum-circuit compute; `EXP-SSI-001` not launched; toy
  peak-byte width lane not iterated; no fake-τ gate B.

```yaml
QM_ERROR_OUTCOME: f_union_tightened
tightened_obligation: OBL-2a
reverse_inclusion_scope: recovery_spec_internal_typed_exit_set_only
host_level_exhaustiveness: not_supported
qm_error_cleared: false
query_memory_cleared: false
qm_stopping_reopened: false
probability_composition: false
crypto_verify_body: false
tau_invented: false
is_relabel_only: false
disposition: FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED
```
