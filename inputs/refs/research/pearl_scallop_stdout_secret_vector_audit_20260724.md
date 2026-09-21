# PEARL-SCALLOP Stdout Secret-Vector Audit

Date: 2026-07-24

## Handoff: reference implementation logging hazard

### Claim or task

Audit the public PEARL-SCALLOP Sage reference example for public-orientation or
branch-selector leakage relevant to the passive SCALLOP attack search.

### Status

`OBSERVATION / IMPLEMENTATION-LEAKAGE-HAZARD / NOT-A-PROTOCOL-BREAK`

### Assumptions

- Sources audited:
  `https://raw.githubusercontent.com/biasse/SCALLOP-params/main/implementation-sage/pearl-scallop.sage`.
  `https://raw.githubusercontent.com/biasse/SCALLOP-params/main/cpp-optimised-implementation/main.cpp`.
  `https://raw.githubusercontent.com/biasse/SCALLOP-params/main/cpp-optimised-implementation/scallop.hpp`.
- Local downloaded source hashes:
  `4fc0820d447123b6b50c8c8135fe0844b29502fbe77884f1ad4ac26c0dca539e`.
  `2c55f67cd4918b9be0a891dd773bf81ba5c440982ec0d5f0353f4f98147ef52e`.
  `b8566b25f31cff4c959f6c2eac66c2662ce0cff23c655bb9c208b8ee37f333fd`.
- The audit concerns the public reference/example execution path, not a
  deployed service or protocol specification.

### Evidence

Audit artifacts:

```text
experiments/ecdlp_isogeny/iso_pearl_scallop_stdout_secret_vector_audit.py
experiments/ecdlp_isogeny/iso_pearl_scallop_stdout_secret_vector_audit_result.json
```

Hashes:

```text
script: 2ab0b5e9f6dddc64ae1d09823335fb73e4abcbf9796ab2359cb60b2ace2daf54
result: 1fc3ad7f7e586865fb081bef6fa12e02590b09dea822ca6337636a8fd0862a22
```

The audited Sage source defines `GroupAction(E, K1, K2, vec, ells)`.  Inside
the main loop it prints:

```text
line 312: print("\\n\\nVector currently looks like:")
line 313: print(vec)
```

The sample `__main__` path samples secret action vectors and passes them into
`GroupAction`:

```text
line 367: alice = [randint(-3, 3) for _ in range(dim)]
line 368: bob = [randint(-3, 3) for _ in range(dim)]
line 370: E_A, P_A, Q_A = GroupAction(E, P, Q, alice.copy(), ells)
line 372: E_B, P_B, Q_B = GroupAction(E, P, Q, bob.copy(), ells)
```

The audited C++ implementation has the same example-path pattern:

```text
scallop.hpp line 14:  void printVector(std::vector<int> const &vec) {
scallop.hpp line 151:         printVector(es);
main.cpp line 227:    std::vector<int> es_A = GenSecret(dim, 3);
main.cpp line 228:    std::vector<int> es_B = GenSecret(dim, 3);
main.cpp line 236:    ProjA PK_A = GroupAction(P_A, Q_A, Qm_A, A, es_A);
main.cpp line 238:    ProjA PK_B = GroupAction(P_B, Q_B, Qm_B, A, es_B);
main.cpp line 241:    auto SS_A = GroupAction(P_B, Q_B, Qm_B, PK_B, es_A);
main.cpp line 244:    auto SS_B = GroupAction(P_A, Q_A, Qm_A, PK_A, es_B);
```

### Interpretation

The strongest valid statement is:

> The public PEARL-SCALLOP Sage and C++ examples print sampled `GroupAction`
> action vectors to stdout in sample public-key-generation and shared-secret
> paths.  Any use that treats this stdout as public or logs it durably leaks
> the sample action vector.

This is a real implementation hygiene issue for the audited reference/example
source.  It is not a passive mathematical attack on PEARL-SCALLOP, and it does
not change the protocol-level SCALLOP security analysis.

### Failure modes

- The code may be intended only as an interactive demonstration.
- A production implementation may remove or suppress stdout logs.
- The issue leaks the sampled action vector only in executions that preserve
  this logging behavior.
- This does not provide a new isogeny-complexity algorithm, a general
  SCALLOP break, or an ECDLP consequence.

### Next concrete action

Patch or upstream-report the reference implementations by removing or guarding
`print(vec)` and `printVector(es)`.

### Artifact paths

- `experiments/ecdlp_isogeny/iso_pearl_scallop_stdout_secret_vector_audit.py`
- `experiments/ecdlp_isogeny/iso_pearl_scallop_stdout_secret_vector_audit_result.json`
