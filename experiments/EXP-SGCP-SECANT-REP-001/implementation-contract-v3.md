# Implementation Contract V3

## Status

Status: `review_required`.

Source implementation, development children, registered seeds, canonical mode,
launch-plan design, and execution remain unauthorized.

## Single reconciled surface

`source-schema-v3.json` is the sole normative source-stage schema. It supersedes
the accounting and result-shape requirements of:

- `accounting-schema-v1.json`;
- `process-accounting-v2.json`;
- `result-schema-v2.json`.

Those files remain historical design inputs. V3 incorporates their mathematical
and measurement requirements only where explicitly present in the v3 schema.

The derivation is `derivation-manifest-v2.json` as narrowed by
`derivation-amendment-v3.json`. Controls and mutations remain the v1 manifests
plus their v2 amendments and `mutation-amendment-v3.json`.

## Current authority

The only currently emittable result variant is `development_control`.
The source constant is exactly:

```text
SOURCE_AUTHORITY = "CONTROLS_ONLY_ZERO_RUN_V3"
```

Before parsing any seed, chart, compiler, or matrix argument, every CLI rejects
an absent or unequal authority constant, any mode other than `controls`, and
any `maximum_runs` other than integer zero.

Canonical complete and canonical partial records are schema-defined for future
review, but current source must reject their construction and verification
unless a later hash-bound launch amendment changes the source and authority.

## Development claim boundary

Development output has exactly:

```text
claim_status = ["HYPOTHESIS","MODEL-BOUND","NOVELTY-UNVERIFIED"]
terminal.classification = "DEVELOPMENT_CONTROL_ONLY"
evidence_eligible = false
breakthrough_claim = false
ecdlp_solved = false
rho_comparison = "not_applicable"
matrix = absent
```

It must not use `TOY-EVIDENCE`, because implementation controls are not
experiment evidence.

## Failure and partial records

Curve and factor streams are tagged unions: `accepted` or `exhausted`.
Canonical matrices are tagged unions: `complete` with exactly 36 fixtures, or
`partial` with unique completed cells plus an exact missing-cell list.

Attempt-cap exhaustion, resource limits, process/publication failures, and
nonexact optimization produce `INCONCLUSIVE` partial records. Confirmed schema,
arithmetic, semantic, embedding, accounting, state, or verifier mismatches
produce `INVALID` partial records.

## Accounting

Every attempt contains the exact v3 fields:

```text
protocol_version, development_invocation_id, development_order, work, io,
integrity
```

in addition to identity, process, fresh-state, resource, storage, failure, and
observed/charged counters.

One closed work dictionary applies to every role; unused counters are zero.
One optimizer dictionary and one conservation block apply everywhere.

The root supervisor has its own identity, resource, I/O, storage, and observed
counter record. Aggregate totals include it under the v3 equations.

## Resource authority

Development per-child ceilings are frozen in v3. Canonical ceilings are null,
which makes canonical construction invalid. A future launch amendment must
supply nonnull ceilings and a new reviewed source hash.

## Next concrete action

Hash-bind v3 and obtain theory, accounting, and red-team review for source
implementation only.
