# BATCH-020 successor FC0 host novelty screen

**Task:** `TASK-20260730-051`  
**Decision / evidence:** `DEC-20260730-017` / `EV-SSI-019`  
**Lane:** IDEA-20260729-001 / CSIDH-COLLIMATION-FC0-R2  
**Compute:** zero curve / isogeny / quantum-circuit  

## Verdict

`pin_status: no_admissible_pin`.

No screened successor host or explicit extension package exposes checkable
`Verify(x,k')` **and** FC0 `W/R/B/M_tail` lifetime hooks under the honesty
rule. Preferring a weak pin (Quist notebooks, classical CSIDH action, SQALE
estimator, paper prose, or an unwritten extension package) is refused.
`CollimationSieve@6f9188e4` remains `host_gap_certified` and is not patched.

Disposition retained: **`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`**.

## Candidates screened

| ID | Class | Pin eligibility | One-line reason |
|---|---|---|---|
| CAND-PEIKERT-PAPER-ONLY | Paper-only accounting (ePrint 2019/725) | **reject** | No executable Verify / lifetime APIs |
| CAND-QUIST-SIMULATOR | Quist thesis c-sieve + post-processing `@5445a082` | **reject** | Sieve sim + notebooks; no durable Verify / FC0 lifetimes |
| CAND-CSIDH-REF-VERIFY | `ioerror/csidh-reference-implementation@5e2508f8` | **reject** | Classical `csidh()` only; no FC0 W/R/B/M_tail |
| CAND-SQALE-CSEIVE-ESTIMATOR | SQALE `c-sieve-estimator.py@a95812f0` | **reject** | Cost estimator, not FC0 object host |
| CAND-INREPO-FC0-EXTENSION-PACKAGE | In-repo extension design from recovery_spec | **reject** | Spec-only anchors exist; no frozen host interfaces to pin |

Negative control (not a successor candidate): `CollimationSieve@6f9188e4`
(`host_gap_certified`, BATCH-019).

## What was checked (no execution)

- GitHub REST metadata and raw file headers for Quist, CSIDH reference, SQALE
  estimator; Peikert ePrint/author PDF as accounting surface.
- Cross-check against BATCH-012 `artifact_pin.yaml`, BATCH-013
  `recovery_spec.md`, BATCH-017 `lifetime_trace.yaml`, BATCH-019 host-gap
  certificate.
- No simulator runs, no curve/isogeny evaluation, no quantum-circuit compute.

## QM blockers

| Blocker | Status after this screen |
|---|---|
| QM-STOPPING | **open** (out of clearance scope; no τ / joint finiteness invented; BATCH-018 FAIL retained) |
| QM-MEMORY-MAP | **open** — still `open_host_gap_certified` relative to CollimationSieve; no successor pin advances it |
| QM-ERROR | **open** — Verify still absent; no `F_*` / `F_sim→F` instantiation |

ttm-v2 retained as finite ideal-choice observations only; **not** equated with
BATCH-014.

## What would be required next

1. Coordinator-authorized task to **freeze** an in-repo FC0 extension-package
   interface (Verify + W/R/B/M_tail signatures) under a declared write scope,
   citing recovery_spec classes, without inventing CollimationSieve APIs.
2. Later bounded implementation spike against that frozen package.
3. Optional lower-priority deep Quist notebook→API audit if adapting that host
   is preferred over a clean package.
4. QM-STOPPING remains a separate lane (Verify-relative τ + joint finiteness).

## Inventor-protocol honest accounting (§5)

- **Objects considered:** paper accounting surface; classical phase-vector
  simulator; notebook post-processing; classical CSIDH group-action API; SQALE
  cost estimator; recovery_spec / lifetime_trace checklist (spec-only).
- **dominated_by:** `n/a (no result claimed)` — this batch claims no asymptotic
  or security improvement; it certifies absence of an admissible pin.
- **sota_delta:** `0` (no complexity claim; host-pin search only).
- **Enumerated closures:** none claiming lane death. Pin-scoped host gap on
  CollimationSieve remains; successor-pin search fails eligibility, which is a
  search/instrumentation obstruction, not an FC0 mathematical impossibility.
- **Open for next session:** freeze and archive an explicit FC0 extension
  package interface; keep QM-STOPPING open until source-compatible τ exists.

## Inference

- Requested policy: `research-sol-max` (alias of research-deep family).
- Resolved model: Cursor Grok.
- `fallback_used: true` (authorized by
  `inference-amendment-TASK-20260730-051.yaml`).

## Non-claims

No numeric security, breakthrough, goal completion, QUERY_MEMORY clearance,
CollimationSieve API invention, τ invention, or BATCH-014 equivalence.
