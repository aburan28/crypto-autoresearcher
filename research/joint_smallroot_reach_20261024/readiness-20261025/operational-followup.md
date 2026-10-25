# Follow-up operational checks

These checks followed the report snapshot. They add no scientific observation.

The direct Codex runtime is authenticated, but the following fixed public-prompt
readiness check exits 1 before emitting any JSON events:

```bash
timeout 50 codex exec --json --sandbox read-only --skip-git-repo-check \
  -c model_reasoning_effort=high 'Print exactly PROBE_OK and nothing else.'
```

Its stderr is retained in `codex-direct-readiness.stderr`. Initialization fails
with `Read-only file system (os error 30)`. No Coordinator task ran, no independent
runtime receipt was asserted, and no credentials or home directories were
rewritten. The empty stdout file is preserved. This is the concrete direct-runtime
impediment in addition to the API backend warnings in the main report.

After merging current main, local draft-tier lint also exposed two newly
inherited uncovered workflows, `lab-parity.yml` and `pext-n7-lean.yml`. Running
the repository's `draft_tier_gate.py --apply` adds `ready_for_review` events and
the existing nondraft job guard to those two files. The resulting checker reports
`0 PR workflows outside the draft tier gate`; merge hygiene passes. Their jobs
remain active on this ready PR and their original triggers and path filters
are retained. Required checks are not removed or waived. The original artifact
CI repair remains in place. Hosted checks must still complete on the final head.

Artifact policy selects PDFs above 64 KiB. The full 87,712-byte rendering was
retained unchanged in commit 3417ab1c4, before the artifact check identified it.
It is removed from the tip without rewriting history; the local copy is ignored.
Object-store credentials are absent, so no upload is asserted. The published
view is `report-compact.pdf`, made by `compact.py`: the complete source text and
vector artwork are retained, the display font changes to Nimbus Roman, and
structural PDF accessibility tags are omitted. Pixel hashes verify that the
container compression changes no pixels relative to that font variant.
`report.typ` and the original generator remain unchanged. To regenerate, run
`render.py` and then `compact.py` in a fresh copy of this directory. The
compact source, verification receipt and PDF are published under the size
threshold; no artifact-policy exception or threshold change is used.
