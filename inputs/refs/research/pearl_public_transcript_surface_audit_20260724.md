# PEARL-SCALLOP Public Transcript Surface Audit

## Claim or task

Audit the already-downloaded public PEARL-SCALLOP Sage and C++ example
sources for stdout features that could support the passive Bockstein/marked
torsion attack route.

## Status

`NEGATIVE RESULT / PASSIVE-TRANSCRIPT-SURFACE-AUDIT / IMPLEMENTATION-LEAKS-ONLY / NOT-A-PROTOCOL-BREAK`

## Result

The active example stdout surface contains two implementation hazards:

- sampled `GroupAction` action vectors are printed;
- example shared-secret j-invariants are printed.

The active stdout surface does not print pairings, BiDLP coefficients, kernel
generators, eigenvalue matrices, isomorphism constants, marked torsion images,
or a Bockstein/divided-orientation transcript.  Those missing objects are the
kind of same-launch data needed to promote the passive PEARL route into a
SCALLOP protocol attack.

## Evidence

Producer:

```bash
python3 -B experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit.py
```

Verifier:

```bash
python3 -B experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit_verify.py
```

Both passed.  The verifier reports no active pairing/kernel/matrix output and
no passive Bockstein or marked-torsion transcript.

Artifact hashes:

- `experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit.py`
  `c7e4932945af2bfcca79309018d387413da3c750332fb3d60f9664d42b606368`
- `experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit_result.json`
  `4d3a64e2cd9ee3c37f19ac462a946049072a421a6897c6722ebc2c65bf55e7c8`
- `experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit_verify.py`
  `2e96c824c0f48ff0de4115bc72b36dda4756ae7d56b7ec83381d6812d7bfda19`
- `experiments/ecdlp_isogeny/iso_pearl_public_transcript_surface_audit_verify.json`
  `a8a720d3a3b5c3d3a8bb717c0a7e022a7c056cb17405812e38c943fa19421fc6`

Audited public-source hashes:

- Sage source `/private/tmp/pearl-scallop.sage`
  `4fc0820d447123b6b50c8c8135fe0844b29502fbe77884f1ad4ac26c0dca539e`
- C++ main `/private/tmp/pearl-main.cpp`
  `2c55f67cd4918b9be0a891dd773bf81ba5c440982ec0d5f0353f4f98147ef52e`
- C++ header `/private/tmp/pearl-scallop.hpp`
  `b8566b25f31cff4c959f6c2eac66c2662ce0cff23c655bb9c208b8ee37f333fd`

## Claim Boundaries

This is a static audit of three local public example-source files.  It does
not analyze every downstream fork or production integration.

The action-vector and shared-secret stdout behavior is an implementation
hazard if logs are public or durable.  It is not a protocol-level
PEARL-SCALLOP break, not a general isogeny-complexity improvement, and not an
ECDLP consequence.

## Next Concrete Action

Search for a non-stdout transcript or verification API that returns marked
torsion images, pairings, normalized kernels, or divided-orientation data.  If
none exists, keep the passive PEARL route closed and pivot away from this line.
