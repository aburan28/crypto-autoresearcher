# EXP-SGCP-EMBED-002 source self-review v5

## Task

Check whether the no-run V5 source and controls close the exact verifier
totality, version routing, standalone semantic oracle, and family-gate boundary
findings in `pre-run-red-team-v4.md` without widening the mathematical claim or
consuming a curve-row/run budget.

## Status

`OBSERVATION`; underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

## Checks

- The producer emits only schema/protocol V5 and still rejects both CLI modes.
- The verifier accepts only exact V5 schema and rejects V1-V4 before row
  verification.
- Check lists are route-specific; unsupported inputs do not claim graph,
  optimizer, gate, or accounting checks.
- Files, JSON shape, strings/keys, B values, optimizer node caps, and verifier
  primary budgets have explicit ceilings.
- Row envelope checks run before graph reconstruction. Semantic eligibility and
  upper index/mask bounds run before replay or cap-loop indexed access.
- Row, document-value, and file entrypoints catch remaining implementation
  exceptions and serialize invalid receipts.
- The four V4 red-team crash cases return equal deterministic invalid receipts
  on repeated calls and perform zero primary-proof nodes.
- A V5 body relabeled as any V1-V4 schema is rejected with zero row reports.
- Malformed JSON, duplicate keys, nonobject roots, malformed schema types, and
  invalid verifier budgets fail closed.
- Every scalar leaf in the frozen row is replaced by a wrong JSON scalar type;
  all substitutions are rejected by the exact-type pass.
- A standalone frozen-B4 oracle does not call producer or verifier EC, graph,
  ideal, retained-model, support, or optimizer helpers. It reconstructs the
  factor base, candidate and conflict counts, and every five-field cap winner.
- Hand-derived gate fixtures hit 17/18, 18/24, two/three-strata, median-tie,
  duplicate-null, cross-cap, all-fail, and COLLAPSE boundaries. Producer and
  verifier outputs match exactly.
- Hypothesis and specification records validate, and `ledger.json` exactly
  matches the generated experiment index.

## Failure modes still open

1. The 1 GiB and 10,000,000-node verifier ceilings are parsing boundaries, not
   approved execution resources. A future plan must choose smaller enforceable
   role budgets or justify these ceilings independently.
2. A final exception boundary converts an unexpected valid-input verifier bug
   into an invalid receipt. That is correctly `INCONCLUSIVE`, but the exception
   must still be investigated before interpreting any future matrix.
3. The standalone oracle is complete only for frozen p=19, B=4, least-x. It
   challenges shared finite semantics but does not validate generated-curve or
   Mobius/hash-null derivation independently at every canonical row.
4. Producer and verifier family-gate implementations remain structurally
   similar. Hand-derived expected counts cover the registered threshold edges
   but not every possible complete-matrix configuration.
5. Canonical exact search feasibility, cache memory, traffic, full artifact
   size, generator/verifier role cost, and process isolation remain unmeasured.
6. No relation generation, relation rank, target descent, fixed-curve
   preprocessing crossover, rho comparison, exponent, or ECDLP claim exists.

## Next action

Commit the exact V5 snapshot, then request fresh read-only theory, accounting,
and red-team `GO` or `REVISE` decisions. Keep `maximum_runs=0`; do not design a
launch plan unless all three reviews explicitly authorize that separate step.

## Artifact paths

- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v5.json`
- `experiments/EXP-SGCP-EMBED-002/revision-response-v5.md`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v5.md`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
