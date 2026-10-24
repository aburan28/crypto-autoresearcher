# The three-repository lab contract

One contract for `aburan28/crypto`, `aburan28/crypto-autoresearcher` and
`aburan28/cryptanalysis` (the sibling `aburan28/crypto-lean` holds the Lean
library the proof gates call). Each repository still has its own `AGENTS.md`,
which is normative for work in that repository. This file is normative for the
things the three share: instruction precedence, the skill surface, object
storage, the validation vocabulary, curve identity, shared code, and the merge
flow. Where a repository's `AGENTS.md` states a stricter rule, the stricter rule
wins; where the two disagree on a shared convention, this file wins and the
repository file is corrected.

## 1. Repository roles

| repository | owns | does not own |
|:--|:--|:--|
| `crypto` | implementations, `ecbench`, IC measurements, the artifact-store tool and the curve registry build | research programme state, the lead atlas |
| `crypto-autoresearcher` | programme ledger, roles and dispatch, progress fidelity, the lead atlas, this contract | measured results, curve authorities |
| `cryptanalysis` | experiment protocols, the IC curve source of truth (`experiments/ic-candidate-catalog/curves.yaml`), independent checkers, factor-base archive | implementation benchmarks, programme state |
| `crypto-lean` | the shared CryptoLean library and proof gate invoked by `crypto` and `cryptanalysis` | experiment records |

## 2. Instruction surface

- **One normative file per repository**: `AGENTS.md`. `CLAUDE.md` and every other
  runtime file (`docs/claude-code-runtime.md`, `.cursor/*`, `.codex/*`) point at
  it and may restate only runtime mechanics. A second copy of a rule is a bug.
- No generated block may contain a rule. If a tool writes between markers, the
  block says where the rule lives; it does not hold the rule.
- One precedence sentence per repository, in `AGENTS.md`: "`.claude/agents` and
  generated runtime files carry tool surfaces only; `orchestration/roles.yaml`
  is authority for roles, and this file is authority for behaviour."
- A cited file that does not exist is removed from the instruction. Today
  `crypto` cites `.conductor/WORKFLOW.md`, which is absent.

## 3. Skills

- **One canonical body per skill per repository.** The other runtime surface
  carries a relative symlink or a pointer adapter, never a second real copy.
  Today `crypto` duplicates `ecbench-bounds` and `sheriff` as real files while
  its other twelve skills are symlinks; `cryptanalysis` exposes only two of its
  twelve skills under `.claude/skills/`.
- **The same skill name set on both surfaces**: `.agents/skills/<name>` and
  `.claude/skills/<name>` resolve to the same body for every `<name>` present.
  A Claude-only session must be able to discover every skill the repository
  defines.
- Names are kebab-case and describe the action (`run`, `review-evidence`,
  `design-experiment`), not the model or runtime.
- A skill whose procedure is owned by another repository is a pointer, and the
  pointer names the canonical path and commit. `sheriff` is canonical in
  `crypto-autoresearcher`; `curve identity` is canonical in this repository.
- A skill that changes a shared convention may not be edited on one side alone:
  the contract change lands here first.

## 4. Object storage

**One bucket: `s3://setec-astronomy-artifacts`, region `us-east-2`.**

| prefix | content | writer | reader |
|:--|:--|:--|:--|
| `store/sha256/<aa>/<hex>` | content-addressed data and blobs, write-once | `artifacts.py push`, `crypto store push`, `crax store push` | every repo, hash-checked |
| `reports/<repo>/<path>` | published reports, graphs, PDFs, plus `_manifests/<commit>.json` | the `reports-s3` workflow on `main`, or an owner sync | every agent |
| `ic/v1/isogeny-experiments/<run-id>` | resumable run state, head manifest written last | the run that owns the lock | the run that resumes it |

Rules:

- A session **never** uploads, overwrites or deletes under `reports/`; the
  workflow is the only writer there. An agent may list, copy down and presign,
  and verifies a download against the materialized SHA-256 before citing it.
- `store/` is write-once. An agent never deletes a remote object; superseding
  writes a new digest. `gc` prunes the local cache only.
- Credentials are `ARTIFACTS_AWS_ACCESS_KEY_ID` / `ARTIFACTS_AWS_SECRET_ACCESS_KEY`
  with `ARTIFACTS_AWS_REGION=us-east-2`. Readers need `s3:GetObject` and
  `s3:ListBucket`; writers add `s3:PutObject`. Workflows prefer these secrets
  and fall back to `AWS_ACCESS_KEY_ID`.
- Manifests are the authority: `.artifacts.json` (`artifacts.manifest/v1`) per
  data directory, `reports/<repo>/_manifests/<commit>.json` per report push.
- **Legacy buckets are read-only**: `s3://crypto-autoresearcher/**`,
  `ecc2k130-*`, `ecc2k130-status-*`, `aburan28-n83-tier1-*`, `cairn-swarm-*`.
  No new object is written to them. `crypto`'s `store/config.json` still points
  at the first of these and must move to `setec-astronomy-artifacts/store`.
- A bucket is not a place to avoid a review: an object is evidence only through
  the manifest and the validation record that cite it.

## 5. Validation

Shared vocabulary, one meaning per word:

- **Claim tier**: `toy` (≤32 bits), `medium` (≤96), `crypto` (>96). A tier is a
  scale statement, never a licence for a broader claim.
- **Row status**: `validated`, `pre-gate`, `unvalidated`, `failed`. Only
  `validated` may appear as a result; `pre-gate` is historical and frozen.
- **`VALIDATION.json`**: one schema, `validation/v1`, with `claim_tier`,
  `status`, `certificate` (kind + digest + verifier), `reference` (matched rho:
  same point, same envelope, the 0 / 0.1 / 1 GAE band), and `inputs` (curve UID,
  code commit, seed). A file without those keys is not a validation record.
- **Certificate kinds**: `none` (pure measurement), `replay` (independent
  re-execution reproduces answers and counters), `proof` (Lean, axiom-checked),
  `solver` (checked witness). A failed certificate makes the run
  `invalid_measurement`, never negative evidence.
- **Independence**: a verifier does not import the producer's code path; a
  review plan names, per load-bearing joint, one owner and one attack.
- **Required checks** (rulesets, not conventions): `crypto` — `gate`, `size`,
  and `validation-gate`; `crypto-autoresearcher` — `progress-fidelity` and
  `ledger-and-harness`; `cryptanalysis` — `analysis` and `ic-bench`. A required
  check is never skipped, re-run to green, or bypassed. Admin bypass stays off.
- A non-required check queued 24 h without starting does not block a merge, if
  every executed check on the head passed; a required check never qualifies.

## 6. Curve identity

Three layers, never conflated:

1. **Identity** — `curve_uid = urn:ec-record:1:sha256:<hex>` over the canonical
   `{"field": …, "curve": …}` record, computed by the byte-identical
   `tools/curve_identity.py`. This is the join key across repositories. A hash
   proves metadata identity, never mathematical equivalence.
2. **Compact alias** — `EC1N<n>C<tag>h<12hex>` (binary),
   `EC1P<bits>C<tag>h<12hex>` (prime), `EC1Q<p>D<n>C<tag>h<12hex>` (extension).
   Display and filename use; never the only join key.
3. **Display slug** — `ICV1:…` in `crypto`, and the IC names
   (`N53`, `IC1…fb<B>…`, `…W<12hex>R<n>`) in `cryptanalysis`. Presentation only.

Source of truth: `cryptanalysis:experiments/ic-candidate-catalog/curves.yaml`,
mirrored byte-for-byte to `crypto/docs/curves/ic/curves.yaml`, from which
`crypto` builds `docs/curves/registry.json` and `traits.json`;
`crypto-autoresearcher` reads that export at a pinned commit and never computes
curve facts. Register a curve in the PR that first names it; a retired name in
new text fails `curve-names`.

## 7. Shared code and documents

These are byte-identical in every repository that has them, and a change lands
in the owner first:

| file | owner |
|:--|:--|
| `tools/curve_identity.py` | `crypto-autoresearcher` |
| `tools/task_card.py` | `crypto-autoresearcher` |
| `tools/artifacts/artifacts.py` | `crypto` |
| `docs/curve-identities.md` | `crypto-autoresearcher` |
| `docs/lab-contract.md` (this file) | `crypto-autoresearcher` |
| `validation/v1` JSON schema | `crypto` |

A parity check compares the digests and fails a PR that lets them drift. Forking
a copy is not a fix: extend the owner or make the dependency explicit.

## 8. Merge flow

- Open ready for review (`draft=false`), enable auto-merge immediately
  (`gh pr merge <n> --auto --merge`), then continue through the PR: fix what the
  change breaks, check in about 50 minutes then about four hours, stop after
  three quiet checks. Stacked PRs cannot auto-merge until retargeted to `main`.
- **Merge commits only** in all three repositories; a squash orphans archive
  receipts. A new commit resets the head's checks.
- Never bypass branch protection, required review or a required check; never
  skip, disable or re-run a check to go green; never force-push a shared branch.
- Conflicts in frozen evidence, ledger rows, claims or factor bases are reported
  to the owner, never resolved by picking a side.
- Records are immutable: correct by superseding, never by rewriting; archive
  receipts bind content first (`path_sha256`), commit reachability second.

## 9. Divergence today (2026-10-24)

| area | `crypto` | `crypto-autoresearcher` | `cryptanalysis` |
|:--|:--|:--|:--|
| instruction | three concatenated documents; `CLAUDE.md` duplicates rules | single contract + pointer `CLAUDE.md` (model) | single contract; `CLAUDE.md` additive |
| skills | `.agents` canonical, 2 real duplicates, 12 symlinks | `.claude` canonical, `.agents` adapters | `.agents` canonical, 2 of 12 symlinked |
| store | `.artifacts` → setec, `store/` → `crypto-autoresearcher` | setec | delegates to `crypto store` |
| blobstore doc | setec | still says `crypto-autoresearcher/blobs`, `us-west-2` | n/a |
| validation | `VALIDATION.json` gate; no ruleset for it | progress-fidelity ruleset | no ruleset; workflow gates |
| curve source | registry built from `curves.yaml` mirror | consumes a pinned export | owns `curves.yaml` |
| Lean | local gate | none | local gate |
| `crypto-lean` | not named as a dependency | not named | not named |

## 10. Migration

1. **This change**: publish this contract; fix `crypto/store/config.json` and the
   stale blobstore paragraph; de-duplicate `crypto`'s two real skill copies;
   expose all `cryptanalysis` skills to Claude.
2. **Surface parity**: a `check_skills_parity.py` per repository fails a missing
   symlink or a duplicated body; fix the `crypto` `AGENTS.md` three-document
   concatenation and the absent `.conductor/WORKFLOW.md` reference.
3. **Validation**: commit the `validation/v1` JSON schema, convert the existing
   `VALIDATION.json` instance, and add the missing required checks to the two
   rulesets (`crypto: validation-gate`; `cryptanalysis: analysis`, `ic-bench`).
4. **Storage**: move the last writer off `s3://crypto-autoresearcher/**`; declare
   the legacy buckets read-only in every `AGENTS.md`; add a report-retention
   note for `cryptanalysis`.
5. **Curves**: a cross-repo registry parity check (source → mirror → built
   registry), run on every PR that touches any of the three files.
6. **Shared code**: add the digest lock and the parity job named in section 7,
   including the `crypto-lean` proof gate as a named dependency.
