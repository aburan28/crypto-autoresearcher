# SSI refinement duplication and knowledge audit

This is a design audit for `IDEA-20260806-9c2f80`, not an experiment result.
The prior BATCH-6c960d Validator and Red Team reports are the direct inputs;
their immutable hashes are recorded in `refinement_report.yaml`.

## Scope checked

- The current successor is `EXP-SSI-fe3f76`, superseding only
  `EXP-SSI-1d0f36`; both predecessors remain immutable.
- The exact source parameters are the two named paper instances:
  `5*2^248-1` and `27*2^500-1`. No finite toy prime is introduced by this
  repair. Toy diagnostics remain symbolic until a future task declares a
  separate exact toy instance.
- The existing SSI catalogue paths remain
  `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/{S1,S2,Q3}.md`.
- `tools/schema_supersession_registry.yaml` was not edited because a completed
  archive binds its bytes. The successor's `supersedes` field is the safe
  lineage mechanism for this additive repair.

## What is new in this refinement

The repair does not introduce a new cryptanalytic mechanism. It makes the
already-admitted named constructions mechanically reviewable: the query cost
is now a worst-case finite functional with explicit zero-success behavior;
the physical encodings are fixed; Construction B is mapped at every exact
sigma; shared index bytes are charged alongside the unique union fiber; and
the two former malformed/early-rejection nulls are replaced by valid records
that reach the final identity gate after the same semantic path.

## Non-duplication boundary

The following are not claimed to be novel or executed:

1. The generic advice frontier, known-endomorphism database, delta-screen
   reparameterization, and three-way pair accounting remain the mechanisms in
   the original proposal.
2. The exact primes are source parameters, not a new parameter set.
3. The finite sample sizes and tolerances are protocol controls, not measured
   distributions.
4. The successor is not an all-advice lower bound, a security estimate, or a
   sub-`p^(1/3)` result.

The only retained uncertainty is whether the typed constructions and semantic
controls can be implemented without violating their declared output and cost
contracts. That uncertainty must be reviewed independently before any freeze
or execution authorization.
