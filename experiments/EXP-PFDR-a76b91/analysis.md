# Analysis — EXP-PFDR-a76b91 (Coordinator evidence review, 2026-09-07)

## Observation

Four runs, one container launch each, all supervisor status `completed`, payload
exit code 0, under the pinned image
`sha256:1c633a1d80264a1ff31824a06a5b8ea8566e6277bd7af4fa5db6dd993d4ec4de`
(Ubuntu 22.04.5 base, CPython 3.10.12 payload) with the enforced boundary
`--memory 8589934592 --memory-swap 8589934592 --cpus=1` (8 GiB RAM, swap
disabled, 1 CPU) and a 900 s wall limit per run.

Per-run terminal statuses (canonical manifests):

| Run | Group | Terminal status | result.valid | invalid_reason |
|---|---|---|---|---|
| RUN-PFDR-20260907-587a55 | 1 | `completed_inconclusive` | false | `unresolved_native_definition_interface; dependent certificates unavailable` |
| RUN-PFDR-20260907-2b0b0f | 2 | `completed_valid` | true | null |
| RUN-PFDR-20260907-d934ea | 3 | `completed_inconclusive` | false | `unresolved_native_definition_interface; dependent certificates unavailable` |
| RUN-PFDR-20260907-f0b0d7 | 4 | `completed_valid` | true | null |

Per-fixture statuses, verbatim from the raw results and canonical manifests
(identical in both):

- native-q3: `unmeasured` — reason: "Definition 1.3 grades slots using deg(fi) in B; Example 4.4 includes w^q=0 in B without explicit zero-slot grading or top-before-quotient convention." (d_ff, d_lf, sd_bounds all null)
- native-q5: `unmeasured` — same reason (d_ff, d_lf, sd_bounds all null)
- boolean-q3: `incompatible` — reason: "Boolean quotient signature differs from ordinary ring; no interface proof; ordinary certificate reuse rejected."
- boolean-q5: `incompatible` — same reason
- universal-equality: `inconclusive` — reason: "No certified native witness; control predictions cannot be substituted." (certified_witness null)
- supplied-gap-one: `inconclusive` — same reason (certified_witness null)
- uniform-gap: `rejected_inference` — reason: "A finite table cannot refute existence of an unspecified uniform constant; no asymptotic conclusion."
- rational-target: `inadmissible` — reason: "Exact enumeration of the declared rational-target fiber." (admissible false, rational_y [])

Checker output, verbatim and identical in all four runs:

```json
{"passed": true, "checked_fixture_count": 2, "independent_session": false, "method": "separate checker implementation; same Executor session; not independent research validation"}
```

`incorrectly_accepted_claims` is 0 in all four raw results and all four
canonical manifests.

Resource figures (payload, from the canonical manifests):

| Run | CPU seconds | Peak RSS (bytes) | Supervisor wall (s) | Charged wall (s) |
|---|---|---|---|---|
| RUN-PFDR-20260907-587a55 | 0.002025790999999999 | 15659008 | 51.48167070897762 | 600.005249042 |
| RUN-PFDR-20260907-2b0b0f | 0.002190418999999999 | 15773696 | 51.505960208014585 | 0.0031323750000069595 |
| RUN-PFDR-20260907-d934ea | 0.0016839599999999982 | 15777792 | 49.356666999985464 | 0.0026856249999980264 |
| RUN-PFDR-20260907-f0b0d7 | 0.0017282499999999971 | 15581184 | 53.45993820799049 | 0.002060457999959908 |

Total charged wall: 600.0131275 s against the 3600 s cap (the 600.0 s setup
charge is carried by group 1 per the predecessor convention; groups 2–4 are
charged 0.0 s). Total supervisor wall 205.80423612496816 s; container startup
dominates, and the payload arithmetic itself ran in milliseconds. Both the
per-run 900 s cap and the 3600 s total cap were respected. No rerun, no
protocol deviation, no censored run.

Certificates: every manifest's `result.certificate` is
`{kind: none, verified: null, verifier: null}`. No run claims a solve or a
relation, so no `verified: true` certificate is required. The group-4
`certificates.json` additionally carries a `quantifier` block
(`finite_certificate_implies_no_uniform_constant: false`,
`finite_table_would_only_bound_supplied_constants: true`, with a written
argument) and a `domain` block (exact enumeration of the F_19 fiber at x = 9:
rhs 2, roots []). The quantifier block is a logical argument about quantifier
order, not a discrete_log certificate; it does not change the manifest's
certificate kind.

Artifact-form note: the four archived `command.txt` files contain the
payload command line as a JSON-encoded string (the adapter's `write()`
helper encoded every object), not verbatim. The exact payload command is
recorded verbatim in each manifest's `run.code.command`, and the host-side
launch command with its enforced boundary is recorded in each
supervisor-receipt.json. This is a recording-format defect of the archived
artifacts; it was fixed for future runs by commit e0756e31f (branch-only at
review time; it also makes the adapter persist schema-validation failures).
It does not affect the receipts' validity.

## Comparison

The pre-registered prediction (specification.yaml `preregistered_prediction`)
has two components:

1. Native degree triples: q=3 (d_ff, d_lf, sd) = (3, 5, 5); q=5 (3, 9, 9).
2. Invalid acceptances = 0.

Component 2 is MEASURED at the tested scope and equals 0: 8 of 8 fixture
records, checker-verified in all four groups (checker `passed: true`,
`checked_fixture_count: 2` per group, identical verbatim output in every run).

Component 1 is UNMEASURED: groups 1 and 3 stopped at the unresolved
Definition 1.3 / Example 4.4 zero-slot grading interface, exactly as the
frozen protocol prescribes for an unresolved interface (group 1 procedure:
"If that interface is unresolved, record unmeasured"; stopping rule 2: "Stop
arithmetic on an unresolved native-definition interface; metadata fixtures may
still complete"). No d_ff, d_lf, or sd value was produced for either q. The
prediction is therefore neither confirmed nor refuted by this experiment; the
source values remain control predictions, never observations.

The two components are not conflated: the measured zero is a statement about
the instrument's acceptance decisions on the eight tested fixtures; the
unmeasured component is a statement about the absence of a well-posed native
grading, not about the degree values.

## Inference

The runs establish, at the tested scope only:

- The container-executed audit pipeline (supervisor + adapter + frozen driver)
  completed all four bounded groups under the enforced 8 GiB / 1 CPU / 900 s
  boundary with no infrastructure failure, no rerun, and no protocol
  deviation.
- The instrument's acceptance logic behaved as designed on the tested surface:
  the altered Boolean signatures were rejected as incompatible without an
  interface proof; the finite-table-to-uniform-constant inference was rejected
  by quantifier order; the F_19 rational-target fiber was enumerated and found
  inadmissible (no y with y^2 = 9^3 + 2*9 + 15 = 2 in F_19); and no invalid
  claim was accepted among the eight fixtures.

The runs do NOT establish:

- Any mathematical degree value (first fall, last fall, or solving degree) for
  either native system; none was produced.
- Anything about the pre-registered degree triples (3,5,5) and (3,9,9); those
  remain source control predictions.
- Anything beyond the eight toy fixtures: no prime-digit transfer, no
  asymptotic inference, no statement about elliptic curves or the ECDLP.

## Limitation

- The native Definition 1.3 / Example 4.4 zero-slot grading interface remains
  unresolved; groups 1 and 3 are unmeasured by design, and no degree estimate
  was substituted.
- Single experiment, single seed (0), zero independent instances; the eight
  fixtures are deterministic toy objects, not a sample.
- Toy scale throughout (q in {3, 5}; the F_19 enumeration is a declared
  control, not a scale claim).
- The payload interpreter is container CPython 3.10.12; the host interpreter
  is not the payload interpreter.
- The checker is a separate implementation but from the same Executor session
  (`independent_session: false` per the manifests' own note); it is not
  independent research validation.
- The archived command.txt files are JSON-encoded (recoverable; the verbatim
  command is in the manifests and receipts). The post-archive adapter fix
  e0756e31f exists on the branch, not yet on main, so the branch's
  adapter.py diverges from the frozen hash block once that commit is
  carried; no run receipt was altered by it.
