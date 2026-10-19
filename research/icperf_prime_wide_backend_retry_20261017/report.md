# Exact 63-bit prime-field backend engineering controls

**Task:** `TASK-20261017-68782f` in `BATCH-25c5e3`, replacing the separately archived scratch/precheck failure `TASK-20261017-6b60b8`. This is a bounded implementation and unit-control record. It changes no hypothesis, experiment or goal status and establishes no index-calculus runtime advantage.

## Inputs and method

The nine frozen files and their SHA-256 values are in `input_manifest.json`. The archived curve has `p = 9223372021248595841`. The direct executable was `/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage`, SHA-256 `b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1`, reporting SageMath 10.10.rc0. The exact launcher is `zsh -f research/icperf_prime_wide_backend_retry_20261017/command.txt`. `environment.json` records the starting `HEAD`, dirty worktree, scratch paths, executable, and sampled resources. `test-stdout.log` and `test-stderr.log` retain all process output, including unsuccessful attempts.

The backend parses archived polynomial coefficients and point coordinates as Python integers and emits candidate coordinates as decimal strings. It uses Sage GF(p), Gröbner bases and finite-field variety enumeration on bounded synthetic ideals. A unit ideal with basis element `1` is `certified_no_solution`; a positive-dimensional ideal is `unsupported`; other outcomes have distinct `ok`, `timeout`, `memory`, `crashed` and `invalid` labels. Empty rational-root output alone is not asserted inconsistent. The CLI writes its machine-readable result plus caller-supplied raw stdout/stderr paths. `independent_check.py` uses Sage elliptic-curve point addition and x-lifting without importing the backend polynomial evaluator.

The 21 archived three-arm systems were validated for exact coefficients, monomial powers and target coordinates. They were **parsed only**: `systems_solved = 0`. No natural or full-width planted polynomial ideal was sent to the solver.

```mermaid
flowchart LR
    A[21 archived public systems] --> B[Exact integer parse only]
    C[63-bit public curve and seeded vectors] --> D[Field and S3 controls]
    D --> E[Independent Sage point checks]
    F[Four synthetic ideals] --> G[GF(p) root interface]
    H[Small-prime m=2 system] --> G
    H --> I[Complete point enumeration]
    G --> I
```

## Attempts and observed controls

| Attempt | Scope reached | Outcome |
| --- | --- | --- |
| 1 | Resource-limit setup | macOS rejected `ulimit -v 8388608` with `setrlimit failed: invalid argument`; no Sage control began. |
| 2 | Supervisor setup | The sandbox denied psutil's process-list syscall. A later read-only diagnostic appended the raw traceback to `test-stderr.log`. No control output was observed. |
| 3 | Supervisor startup | A process-list race reported a Sage-launcher zombie. The supervisor terminated and reaped its child. No control output was observed. Its stdout marker repeats “attempt 2”; the machine validation records the separate event. |
| 4 | Parser, field, S3 | 21/21 systems parsed, 64/64 field identities, 16/16 valid S3 and 16/16 altered S3 checks passed. Parsing unrelated floating timing metadata in the coset scan raised `ValueError`; the four ideal and m=2 controls were not reached. The parser failure is an implementation/input-schema handling error, not solver evidence. |
| 5 | Supervisor startup | Another transient zombie in the process tree caused a fail-closed stop before control output. The child was reaped. |
| 6 | All specified controls | All controls below passed; child exit code 0. |

The final `validation.json` preserves attempt 4 and 5 in `prior_attempts`; `vectors.json` retains their available vectors. A bookkeeping field in `prior_attempts` mislabels attempt 5 as `implementation_error` because it inherited attempt 4's `ValueError`. Its nested `validation.classification = infrastructure_error` and `stop_reason = rss_monitor_unavailable:ZombieProcess` are the correct classification. The original field is retained so this correction remains auditable.

| Final control | Recorded observation |
| --- | --- |
| Archived-system exact parser | 21/21 parsed; 0 solved |
| GF(p) identities | 64/64 matched independent integer arithmetic |
| S3 valid triples | 16/16 matched independent Sage point sums |
| S3 altered triples | 16/16 rejected by the polynomial and geometric checks |
| Signed-root negative checks | 4/4 rejected: wrong sign, altered root, altered target, and a nonlifting member of the selected coset |
| One-root ideal | `ok`, exact root `(11, 13)` |
| Two-root ideal | `ok`, exact roots `(1, 7)` and `(2, 7)` |
| Inconsistent ideal | `certified_no_solution`, Gröbner basis contains `1` |
| Positive-dimensional ideal | `unsupported`, dimension 1 |
| Small-prime complete m=2 regression | 2 backend x-pairs equal 2 independently enumerated x-pairs; signed-point checks accepted both |

The final process-tree supervisor sampled RSS every 0.05 s and disk every 1 s, with an early RSS termination threshold of 6 GiB ahead of the frozen 8 GiB ceiling, an 8 GiB scratch ceiling, an 8 GiB continuing-free floor, and a 4-hour wall watchdog. It checked process-list visibility before launching Sage and terminated/reaped a child if monitoring failed. Observed peak process-tree RSS was 250,462,208 bytes, maximum scratch 943 bytes, and minimum SSD free space 543,246,139,392 bytes. The final supervised wall was 39.725 s. These are engineering resource observations, not comparative solver timings. macOS refused a hard virtual-memory `ulimit`, so the active enforcement was a sampled process-tree guard with a conservative 2 GiB margin; it does not prove an instantaneous OS-enforced RSS cap for later workloads. `environment.json` still contains the earlier generated `process_limit` string saying “8 GiB virtual address and post-control RSS checks”; that first clause is superseded by this paragraph and by its `supervisor` block. The raw environment field is retained for audit.

## Scope and remaining work

The four ideals and small-prime enumeration validate a narrow exact arithmetic/root interface. The CLI's timeout and memory classifications exist but were not triggered by these controls. This record does not admit a full-width solver panel. A later approved experiment must test planted m=2 positives under its 300 s, 8 GiB RSS and 64-primary-model per-call limits, then separately measure m=3..8, natural relation yield, observed degree, useful rank, linear algebra, target work, verification and matched rho with all setup charged. Any future cold-start or amortized improvement claim needs the required matched end-to-end evidence and independent review.
