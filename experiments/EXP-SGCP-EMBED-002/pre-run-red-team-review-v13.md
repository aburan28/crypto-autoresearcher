## Findings

1. **High — A failed call can still leave an accepted publication.** The receipt-commit syscall and the helper’s commit-state return are not exception-atomic. After successful `renameatx_np`, hard link, or direct receipt write, an asynchronous Python exception can occur before the helper returns; the exception is re-raised even though the final receipt exists ([verifier lines 7136–7159](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7136), [7181–7205](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7181), [7314–7325](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7314), [7559–7564](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7559)). `publication_status` can then return `accepted` ([lines 7521–7528](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7521)), contradicting the no-post-commit-failure claim ([contract lines 233–240](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:233), [protocol amendment line 12](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v13.json:12)).

   A second deterministic sequence exists because receipt names and content have no attempt identifier ([lines 7328–7330](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7328), [7383–7396](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7383)): after an earlier receipt remains but its data is lost or removed, retrying the identical payload creates new data, fails on the stale receipt’s `EEXIST`, yet the old receipt validates the new data. Concurrent same-destination calls also permit one failed call while another accepted pair becomes visible.

   Minimum repair: bind a unique attempt/publication ID into the receipt; preflight both names; and on every exception during or after receipt publication reconcile the observed pair against the exact expected attempt before returning. Narrow any absolute exception guarantee that cannot cover asynchronous exceptions.

2. **High — Direct public writer calls can escape the development root.** `output_path` normalizes and checks containment ([lines 7061–7072](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7061)), but `write_json_exclusive` does not call it ([lines 7536–7544](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7536)). `_open_output_parent` uses lexical `relative_to` and passes every component—including `..`—to descriptor-relative `os.open` ([lines 7075–7105](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7075)). Thus a direct call with `DEVELOPMENT_ROOT / ".." / "escaped.json"` publishes outside the claimed root. `publication_status` subsequently rejects or raises on that normalized path, despite the writer returning accepted. This violates the output-boundary claim ([contract lines 225–231](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:225)).

   Minimum repair: call `output_path` inside every public writer/status entry point and defensively reject empty, `.`, and `..` descriptor-walk components.

3. **Medium — Forced `O_EXCL` can return accepted after detecting an incomplete inode.** `_confirm_regular_size` raises both for metadata failure and for a definite nonregular/wrong-size result, but both are converted to warnings ([lines 7190–7205](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7190)). The outer writer then marks the publication accepted without validating the final pair ([lines 7550–7584](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7550)). A receipt-size mismatch can therefore produce `accepted: true` while `publication_status` classifies the same pair invalid or mismatched.

   Minimum repair: treat an observed type/size mismatch as unaccepted, distinguish it from an unavailable metadata check, and verify the exact final data/receipt pair before constructing an accepted result.

4. **Medium — Publication coverage is overstated.** The claimed hard-link-success cleanup control replaces `_publish_no_replace` with code that creates and copies into a new `O_EXCL` file; it never calls `os.link` ([test lines 4479–4501](/tmp/sgcp-v13-review-e44edde/tests/test_sgcp_embed_family.py:4479)). The claimed “independent” receipt validation calls the production `publication_status` implementation itself ([test lines 4262–4271](/tmp/sgcp-v13-review-e44edde/tests/test_sgcp_embed_family.py:4262)), despite stronger wording in the contract ([lines 518–529](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:518)).

   Minimum repair: exercise the actual `os.link` branch and add a standalone receipt parser/digest/payload checker sharing no publication-status implementation.

5. **Low — One preserved review-provenance path is wrong.** The provenance record names `pre-run-red-team-review-v12.md` ([line 35](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/independent-review-provenance-v12.json:35)), but the committed artifact is [pre-run-red-team-v12.md](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/pre-run-red-team-v12.md:1). Its recorded hash does match the latter bytes.

   Minimum repair: correct the provenance filename through a new immutable correction record.

## Confirmed checks

- Detached `HEAD` is exactly `e44edde4231604abd76e481b7b4ed90359e42d09`, with sole parent `4386d9722468fde9d963e1bc7e39fca7935463cb`; the worktree remained clean.
- All nine hashes in [development-test-log-v13.md lines 18–28](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/development-test-log-v13.md:18) match the committed blobs.
- Independent arithmetic reproduced `480/112/336/218/4218`.
- Static counts confirm 168 canonical rows, 672 cap cells, 75 focused test methods, 219 repository test methods, and 15 scoped records. Test pass/failure statements remain historical and were not rerun.
- `maximum_runs=0` is explicit ([specification lines 202–209](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:202)); the ledger has `runs: []`, `review_required`, version 13 ([ledger lines 126–132](/tmp/sgcp-v13-review-e44edde/ledger.json:126)).
- No V13 density-row, canonical-matrix, runner, plan, or run artifact is committed. Historical V1 development artifacts are accurately preserved. The only constructed density control is frozen B=4; the three transient legacy controls are exactly B=4,6,8 ([test lines 685–712](/tmp/sgcp-v13-review-e44edde/tests/test_sgcp_embed_family.py:685)).
- V1–V12 schemas route to rejection before semantic row verification ([verifier lines 6970–7012](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6970)). Producer schema/protocol emission is V13, and public generated/legacy construction remains gated ([producer lines 404–410](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:404), [1315–1329](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1315)).
- After normalizing only V12/V13 labels, the entire producer and the verifier’s mathematical core hash identically to the required parent. The curve grid, predicates, compiler, caps, objective, gates, and claim boundary are unchanged.
- No ordinary verification-state reuse bypass was found inside the stated non-hostile-Python boundary. Fresh state, owner-thread checking, closure, token restoration, and worker re-entry guards are structurally sound.
- The receipt is forgeable and transferable by a hostile same-user actor: it is unkeyed, binds only the basename rather than the parent identity, and receipt/data snapshots are sequential rather than pair-atomic. The documents accurately exclude such authentication and TOCTOU protection ([contract lines 241–246](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:241)). An accepted receipt also proves publication integrity only—not verification-report semantics, crash atomicity, or durability.

## Handoff

```yaml
handoff:
  id: TASK-20260724-013
  from: coordinator
  to: executor
  objective: repair V13 publication attribution, exception reconciliation, path containment, direct-write acceptance, and publication-control independence without changing the mathematical protocol
  inputs:
    - git:e44edde4231604abd76e481b7b4ed90359e42d09
    - parent:4386d9722468fde9d963e1bc7e39fca7935463cb
    - severity-ordered findings in this red-team review
  constraints:
    - preserve immutable V13 evidence and create a new successor record
    - preserve the exact curve grid, predicates, compiler, objective, and gates
    - maximum_runs remains 0
    - create no generated density rows, matrix, runner, launch plan, or run artifacts
    - retain no-overwrite and descriptor-relative no-follow semantics
  deliverables:
    - attempt-bound receipt protocol with stale-receipt and concurrent-retry controls
    - exception reconciliation for every receipt-publication branch
    - mandatory path normalization and dot-component rejection in public writers
    - fail-closed handling of observed direct-write inode mismatch
    - actual hard-link control and standalone receipt validator
    - immutable correction for the V12 provenance filename
    - refreshed exact hashes, protocol response, self-review, log, handoff, and ledgers
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: 0
  completion_gate:
    - no failed call can be reconciled as accepted for a different or stale attempt
    - no public writer call can escape the development root
    - accepted return and publication_status agree for every terminal branch
    - all post-commit guarantees are accurately scoped
    - fresh exact-commit theory, accounting, and red-team review
```

REVISE before launch-plan design