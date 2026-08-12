## Handoff: SGCP V8 exact-commit red-team review

### Claim or task

Adversarially test whether exact commit
`a1719f7d910d3cc454911a55ceb8b30d833a0b2d` is ready for design of a
separate hash-complete launch plan.

### Status

`NEGATIVE RESULT`; decision `REVISE` before launch-plan design. This grants no
execution authority. `maximum_runs=0` remains binding, with no generated row,
matrix, runner, plan, or run authorized.

### Assumptions

- Exact committed scoped blobs were reviewed read-only.
- Arbitrary caller-supplied `Path` values and direct Python imports are part of
  the adversarial API model.
- Logged tests were inspected but not rerun.
- Frozen B4 and external-resource claim boundaries remain unchanged.

### Evidence so far

Findings:

1. `HIGH`: unbounded caller-controlled path metadata defeats the total bounded-
   report guarantee. A budget-invalid call reaches report construction before
   opening the path. The report reflects the full `str(path.absolute())` as
   `input_path`; size fallbacks retain that field, and the final ceiling check
   can raise. A printable path longer than the report ceiling therefore yields
   an uncaught exception without requiring a filesystem object.
2. `MEDIUM`: the zero-generated-row producer boundary is CLI-only. Direct
   importers can call generated-curve helpers and `build_density_row`, bypassing
   the refusal in `main`. This cannot create valid V8 evidence by itself, but a
   future launcher must not inherit the capability while budget is zero.
3. `LOW`: aggregate phase closure is recorded but not independently enforced as
   a final validity invariant. No input-driven false-pass was found, but an
   omitted future phase update could leave an incomplete phase with
   `valid=true`.
4. `LOW`: V8 producer diagnostics still contain `version-7` wording.

No concrete false-pass was found for exact types, closed nested shapes,
digest/summary/gate ordering, counter suppression, legacy verifier entry
points, or public direct density-row verification.

### Failure modes

- Caller path metadata can make an invalid-budget verifier call raise instead
  of returning a deterministic bounded invalid receipt.
- Import-level producer construction remains possible under a zero budget.
- Phase validity depends on each call site updating the ledger correctly.
- B6/B8 have independent primary proof plus replay-confirmed secondary fields,
  not a standalone all-five-field oracle.
- Structural reservations are not CPU, runtime, peak RSS, parser/allocator
  memory, output cost, disk/I/O, cache traffic, or memory bandwidth.

### Next concrete action

Prepare one no-run repair that bounds, hashes, or omits reflected `input_path`;
gates every generated-curve/density-row construction entry point; makes phase
closure a final validity invariant; fixes stale provenance strings; and adds
non-generating falsification tests. Then request fresh exact-commit review.

### Artifact paths

- `git:a1719f7d910d3cc454911a55ceb8b30d833a0b2d`
- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v8.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`

