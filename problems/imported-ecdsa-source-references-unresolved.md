# Two imported ECDSA source references lack source custody

- **Status:** `open`
- **Kind:** missing source provenance and source availability
- **Affected work:** imported `candidate226_github_grind_fork` and `candidate233_hmr_clean_route` references under `inputs/refs/research/ecdsafail_record_20260715/artifacts/`
- **Next action owner:** original archive/source owner, unassigned
- **Last updated:** 2026-10-27

## Problem

The checkout records two exact external Git commits without their repository
URLs or source trees, so this checkout cannot supply an independently
rebuildable source archive for either imported reference.

## Evidence and uncertainty

- **Observed:** original mode-160000 entries name commits
  `86c3bfcb2f18d4cc41f824aa46b612771b98b416` and
  `e2e5c758e7f5bb5f1cfd661a166d41bec26ae8ac`. Neither has a `.gitmodules`
  mapping. Their exact paths and OIDs are preserved in
  [the custody record](../docs/ci-repair-orphan-gitlink-20261027/original-references.json)
  and the directory-local `SOURCE_REFERENCE.json` files.
- **Derived or proved:** these pointers identify requested commits; they do
  not supply a source tree or establish source availability or execution.
- **Suspected explanation:** unknown. No claim is made about whether an
  original private clone or archive still exists.
- **Missing capability:** original repository identity/access or a complete
  hash-bound source archive.
- **What this evidence does not establish:** public commit search returned
  zero matches, which does not show the private/local originals are lost.
  Existing research observations are neither promoted nor refuted by this
  metadata repair.

## What would unblock it

- [ ] Recover each original repository and exact commit, or a complete source
  archive bound to that original reference.
- [ ] Retain independently checkable source/dependency hashes and verify them
  against any original frozen input commitments before using the archive.

This would restore source custody. Existing experiment, review and correctness
requirements would still govern any execution or scientific conclusion.

## Next discriminating step

- **Action:** locate the two original clones or archives and record their
  repository identity and exact commit/source hashes.
- **Inputs and controls:** the unchanged two OIDs and original reference paths;
  reject a different revision or incomplete source export.
- **Execution limits and stop condition:** source inspection and hash checks
  only; stop and preserve a mismatch rather than substituting another source.
- **Outcomes:** a matching archive restores custody; an absent or mismatched
  archive leaves this record open; an access failure remains an access limit.
- **Recheck trigger:** original repository/clone/archive becomes available.

## Resolution and history

Unresolved. The 2026-10-27 checkout repair converts unusable submodule entries
to explicit source references while preserving their exact identities. It
does not reconstruct or validate the missing external source.
