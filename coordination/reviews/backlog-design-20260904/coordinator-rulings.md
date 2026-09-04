# Coordinator rulings — backlog design, wave 1

Design-time rulings on questions the designing coordinators escalated rather
than deciding silently. Each was verified against the primary record before
ruling; none is a rubber stamp. These bind the approval decision that will
follow; they are not themselves approvals.

## R1. Question reassignment for the Shor-on-ECDLP cost assembly — CONFIRMED

`IDEA-20260815-1570fe` carries `question_id: RQ-QALG-457b41`. The designing
coordinator filed `H-ICEX-4b2e19` under `RQ-QRE-6dba8c` instead and disclosed
the move. Verified and confirmed:

- `RQ-QALG-457b41` has `curve_families: []`, `field_types: [module lattices
  over cyclotomic polynomial rings (Module-LWE, Module-SVP)]` and `bit_sizes:
  [ML-KEM-512, ML-KEM-768, ML-KEM-1024]`. Its constraints forbid a cost figure
  transferring in or out. An ECDLP quantum cost assembly cannot be filed there.
- `RQ-QRE-6dba8c` scope reads: "RSA-2048 factoring and 256-bit prime-field
  ECDLP under Shor's algorithm; surface-code fault tolerance". That is exactly
  this pipeline.

The immutable proposal is untouched and the mismatch is disclosed in the
hypothesis and the contract. Correct handling.

## R2. EXP-ICEX-b8c865 stays HARD-BLOCKED at approval — UPHELD

`RQ-QRE-6dba8c` constraint 1: "No pipeline output is recorded before at least
two primary resource-estimation papers are filed as KN-LIT entries with their
input tables extracted."

Verified against the four cited entries. Only `KN-LIT-099` qualifies (68 lines,
full simulation table). The other three do not, on their own testimony:

- `KN-LIT-1460`, `KN-LIT-1463`: "No abstract was extractable from the first two
  pages of the local PDF; contribution recorded from the title only."
- `KN-LIT-1882`: bulk-seeded 2026-07-24, "parsed heuristically and may be
  incomplete or mis-segmented; claims are relayed from the paper's abstract
  without independent verification."

`b8c865` produces a pipeline output, so constraint 1 binds. It stays blocked
until a second primary paper is filed with its input table extracted. The
coordinator also records that its dominant term is unevaluable regardless,
since KN-LIT-099 carries no error-correction layer and states no per-run
success probability — so unblocking the constraint alone would not make the
experiment runnable.

## R3. EXP-ICEX-640aef is NOT blocked by that constraint — RULED

The coordinator flagged this as a judgement call rather than deciding. Ruling:
constraint 1 governs a *pipeline output*. `640aef` records no pipeline output.
It reproduces one source's closed forms against that same source's own data
points, which constraint 2 contemplates as a distinct activity: "Reproduction
is scored against the paper's own inputs, and a reproduction gap is reported
with its magnitude rather than tuned away."

A reproduction that consumes exactly one paper cannot require two papers to be
filed. Constraint 1 does not bind it. `640aef` may proceed to approval on its
own merits.

Note its design is deliberately null: it predicts sensitivity to code distance,
cycle time, error rate, distillation and connectivity is EXACTLY ZERO, because
the closed forms contain none of those. The ranking is empty by construction.
That is a real result about what the source can and cannot support, not a
failed experiment, and the approval decision should read it that way.

## Corpus-integrity observation, not a ruling

All four entries above carry `citation_verified: read`, including the three
whose own body text says the contribution was taken from the title only or
relayed without verification. The flag and the body disagree. Records are
immutable so nothing is edited here, but `citation_verified: read` cannot be
relied on as evidence that a source was actually read, and any gate that tests
it is weaker than it appears. Worth a superseding correction and a check of
whatever else that flag gates.
