# SSI v13 duplication and knowledge audit

## Scope

This is a Coordinator design audit for `TASK-20260809-f13a83`. It does not
claim a literature result, a cryptanalytic result, or a completed review. The
v13 successor is intentionally additive: v12 and the v11 Red Team report are
immutable inputs and remain reviewable at their original paths.

## Why a successor is justified

The v12 snapshot was structurally useful but left concrete contract-level
questions open: the specification registry rows did not repeat all fields in
the input registry, local-record widths and preimages were not all field-level,
the NULL shortened frame length was implicit, terminal codes were symbolic,
the source quantifier was prose-level, event byte populations were incomplete,
and the total-byte equation omitted hash-input and signature populations. The
v13 changes address those exact questions; they do not broaden the SSI claim.

## Duplication decision

No new external mechanism is proposed. The v13 experiment reuses the same
design lane and predecessor proposal only as provenance. The repair is a
schema successor, not a re-run of the v12 producer and not a second claim of
the v11/v12 work. The contract repeats its own active rules and copies the
input manifests into the new experiment directory so a later snapshot has one
declared review boundary.

## Knowledge boundary

No new paper, theorem, source citation, route-success claim, or novelty claim
is introduced. The audit relies on the already archived v11 Red Team objections
and v12 producer artifacts. Any later assertion that this SSI lane has been
tried, ruled out, or improved must cite the relevant immutable experiment,
review, evidence, and decision records and must pass the repository knowledge
retrieval policy.

## Required later falsification checks

1. Parse all YAML/JSON and compare the specification registry entry map with
   `FRAME-REGISTRY-v7.yaml`, including key sets, order, widths, and null policy.
2. Recompute every declared local width and digest offset, including the
   172-byte saturation row, 385-byte C-pair row, 196-byte event, and 34-byte
   buffer.
3. Mutate NULL payload length 4090 versus shortened length 4058 and require
   exactly one accepted serialization.
4. Mutate source path/tree/bytes, attempt-to-owner schedule, terminal code,
   event population, HNF quotient, replay draw, control row, and incumbent
   scope; each mutation must reject.
5. Keep all materialization, provider availability, independent review, and
   execution gates closed until those checks and the required reviews exist.

The expected status after authoring is therefore `review_required`, not
`frozen`, `approved`, `running`, `analyzed`, or `supported`.
