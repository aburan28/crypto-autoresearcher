# DEC-20261025-1046c6 metadata completion — 2026-10-27

Coordinator integrity checkpoint on `codex/dec1046-knowledge-promotion-20261027`,
base `b5258367c37cad94c750bc3102fa043698e198a8`. This correction adds only `knowledge_promotion` to a new,
hash-bound schema replacement. Every original decision field and the original
file bytes are preserved. No fresh decision, review, run, execution admission,
scientific finding or goal/hypothesis transition is asserted.

## Source reading and exact bindings

Coordinator (/root/coordinator) read these committed sources on 2026-10-27:

| Source at the base commit | SHA256 |
| --- | --- |
| `ledger/decisions/DEC-20261025-1046c6.yaml` | `53aa6ff5986fba2f38d00f5c3939195f3660c6333800192c68ddb8f025cbf2fa` |
| `experiments/EXP-ECDLP-381959/reports/run-20261025T1906Z/HEADER.md` | `59fe3ba18a687cfe9a93bec1b816031072d6a1c3f42d68ae339f11460550745d` |
| `experiments/EXP-ECDLP-381959/reports/run-20261025T1906Z/data/failed-attempt.json` | `9b55a8e8176245770ed62f1a51efc2501afb42423bdb2e9d3c838ddf6f7b8817` |

The original decision says `scientific_effect: none` and
`hypothesis_status_changed: false`. The report describes a compiler-stopped
attempt, not a solver comparison. Its machine-readable companion records
`infrastructure_error`, zero measurement jobs dispatched and zero solver
observation rows. These source statements support `promoted: []` and the
scoped reason for no knowledge promotion. This is source reading, not a replay
or independent scientific validation; no external theorem is needed or cited.
Missing verification-stage artifacts stay missing. The failed-run manifest's
separate schema/custody errors remain outside this correction.

- Original SHA256: `53aa6ff5986fba2f38d00f5c3939195f3660c6333800192c68ddb8f025cbf2fa`.
- Replacement: `ledger/corrections/schema-supersessions/20261027/DEC-20261025-1046c6.v2.yaml`.
- Replacement SHA256: `31467b0c3b77aa1466b3c8ee830f2c30467d5b55339155605fcf1674fc46a005`.
- Native route: `tools/schema_supersession_registry.yaml`, `kind: ledger`,
  same decision ID; both original and replacement are pinned.

## Scope, gates and checkpoint

The exact three-path Conductor check returned `allow` before writing. This
checkpoint owns only the replacement, its registry append and this note; it
claims no scientific lane. The linked repository impediment remains
`problems/full-ledger-validation-errors.md`.

Unmodified full-tree `python3 tools/validate_ledger.py` exits 1 with 100
unsuppressed errors on the named base (the four-proposal PR is not merged
there). The required differential is deletion of exactly the original's
`missing required field 'knowledge_promotion'` error, with no added error.
The validator and its baseline are unchanged. Native schema/cross-reference,
semantic-preservation, source-hash and merge-hygiene checks are publication
gates; pending results must not be represented as a clean whole-ledger gate.

## Verification results

- Full-tree validator: 100 to 99 unsuppressed errors; both runs exit 1.
  Exactly the named knowledge-promotion error disappeared, none appeared,
  and all other error lines retain their order.
- Before log SHA256: `febff59a2f906ad49d647cfddb125441f46d2b33f641c23bd9cff14f93293382`.
- After log SHA256: `d2553272a09a14a3aed2c3f075ddcb04a9d964e4d5de696cf840b196131aa3bb`.
- Native original record check: one expected error. Replacement schema,
  both hash bindings and decision cross-reference checks: zero scoped errors.
- Removing only `knowledge_promotion` makes the replacement semantically
  equal to the original. Original bytes and the pre-existing registry byte
  prefix match HEAD; the three provenance sources also match HEAD.
- `python3 tools/check_merge_hygiene.py --base origin/main`: PASS for the
  current unstaged branch view. Its parseability sweep reports zero candidate
  record paths, because both new files are untracked and the tracked change
  is the tools registry. The new replacement and registry parse separately;
  the publishing control plane must rerun hygiene with all three paths included.
- Native hygiene `check_markers` and `check_parses(report_stale=False)` were
  also called with the exact three-path list, including both untracked files:
  PASS, no marker or parse error.
- `git diff --check`: PASS. The baseline and validator are unchanged.

Next action — Coordinator/control plane: verify the one-error full-tree
reduction and exact three-path diff, then publish this metadata correction
through normal PR/CI gates after the existing publication sequencing permits.
Coordinate the shared registry append with PR #2609's separate routing fix;
do not duplicate its repair or infer a scientific conclusion from either.

Policy: `coordinator-orchestration-code/high`, existing available binding
`openai-gpt61:gpt-6.1-sol/high`; no execution or reviewer model substitution.
No canonical scientific graph changes: decision metadata only.
