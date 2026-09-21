# Source implementation authorization v1

## State transition

`EXP-ECDLP-TT-SOURCE-COMPILER-001` moves from `review_required` to `approved`
for source implementation on protocol v5.

This transition does not authorize a baseline or mutation run. Execution
requires a separate post-implementation gate after source hashes, dependency
closure, focused tests, resource preflight, implementation accounting review,
and implementation red-team review are frozen.

## Transition audit

The canonical status fields were changed only after both v5 closeout reviews
returned `GO`. The source matrix binding was then propagated into the withheld
full matrix and all six bound SHA-256 values were recomputed:

- source manifest: `524110579d7334dccf46a7d9c1231710956ba04bc001754983ebaab5a8777a52`;
- source execution matrix: `daaa47eb48d1e5e661b27d7561bb61b276743deb3b32bf1a94d27287d3f2cd40`;
- target manifest: `082a0f3201c0fd9a1ec3e22e1a38825c21965d1640b130b19b44904b995468b7`;
- control manifest: `305bfd7ab3f413a2035017346998beb24b7098fb4593b8ebb59640e94fb66c79`;
- mutation manifest: `f92c56557a1cffb4fd84738bcf6c14dcb070e344b261f4def8f69435c91946ae`;
- accounting model: `6ab8f97341f8aa8affc9ccabef22d222c143bc24a4fa282e4bfeb7fdc613f9d3`.

The experiment specification intentionally has no `execution_plan`. The
repository runner therefore rejects experiment execution in this intermediate
state even though the schema-valid status is `approved`.

## Rationale

- `theory-review-v2.md`: `GO` for the unchanged exact TT and first-norm
  identities.
- `accounting-review-v1.md`: v4 arithmetic and binding `GO`.
- `red-team-v3.md`: v4 `REVISE` for one count-scope ambiguity.
- `accounting-review-v2.md`: v5 phase-equation and hash `GO`.
- `red-team-v4.md`: v5 source-implementation `GO`.

## Approved implementation boundary

- Build the target-blind source compiler and source verifier as disjoint
  transitive closures.
- Build target specialization and target verification as separate post-advice
  processes.
- Implement the isolated staging, closed IR, filesystem/environment/source
  audits, exact backend attestation, componentwise ledgers, controls, and 29
  mutations exactly as frozen.
- Run focused unit and development preflights only. Do not register experiment
  evidence or claim success before the pre-run implementation gate.

## Next concrete action

Commit the protocol-only tree, then implement the source compiler and
independent source verifier in disjoint file scopes.
