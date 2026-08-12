# Balanced-Primary Same-Instance Backend Admission Audit

Date: 2026-07-24

## Claim

The checkout contains Kani/theta machinery, but it does not currently contain
a same-instance Kani/theta or BMSS-normalization backend wired to the accepted
reverse degree-13 balanced-primary fixture over `F_390391`.

## Status

`NEGATIVE RESULT / ADMISSION AUDIT / MISSING SAME-INSTANCE BACKEND / NOT-A-BREAK`

## Evidence

Producer:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_same_instance_backend_admission_audit.py
```

Verifier:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_same_instance_backend_admission_audit_verify.py
```

Result:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_same_instance_backend_admission_audit_result.json
```

Verifier result:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_same_instance_backend_admission_audit_verify.json
```

Producer payload:

```text
eca6851f9d948ce443d245614c033292254ea6277f2be098f4fc28f5b41791d3
```

Verifier payload:

```text
cb5ac6c1ca170c69f0574e9637f2dbcadb47217871e1a765402f314951a9b494
```

The verifier passed with zero errors.

## Audit Result

- candidate Kani/theta/BMSS/normalization scripts scanned: `80`;
- vendored theta backend present: `true`;
- same-instance reverse degree-13 backend available: `false`;
- same-instance candidates: `[]`.

Closest reusable candidate:

```text
experiments/ecdlp_isogeny/iso_balanced_kani_recovery.sage.py
```

It uses the vendored theta backend and exposes a fixture dictionary, but its
registered fixtures are:

```text
p43_degree7
p43_degree7_balanced_kani
p43_degree7_non_one_auxiliary
p43_degree7_non_one_auxiliary_balanced_kani
p619_degree15_composite
p619_degree15_composite_balanced_kani
```

It does not mention the reverse degree-13 fixture markers:

```text
390391, F_390391, degree13_reverse, degree13_reverse_nonunique,
iso_balanced_primary_degree13_reverse_nonunique_recovery,
346159, 305173, 76765, 66879
```

## Interpretation

The same-decoder branch-redundancy result cannot yet be promoted into a
same-instance Kani/theta runtime comparison. The needed components are
nearby, but the current repository state has no accepted executable that
consumes the reverse degree-13 balanced-primary fixture and emits a compact
Kani/theta or BMSS-normalized recovery result.

## Boundary

This is a lexical admission audit, not a proof that adaptation is impossible.
It says only that the current checkout lacks a ready same-instance backend.
It is not a SCALLOP attack, PEARL-SCALLOP attack, ECDLP break, or
isogeny-complexity improvement.

## Next Concrete Action

Adapt `iso_balanced_kani_recovery.sage.py` to a new `p390391_degree13_reverse`
fixture, or build a verifier-protected BMSS-normalization comparison. The
first acceptance gate is public construction without reading the withheld
degree-13 map, followed by post-freeze endpoint/kernel verification.
