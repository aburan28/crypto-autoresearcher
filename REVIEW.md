# Review instructions

Contract for automated pull-request review of this repository. It is the single
source of truth for both review paths: Anthropic's managed Code Review service
reads this file directly, and the `claude-pr-review` GitHub Actions job is a
thin bootstrap that reads it too. Change review behavior here, not in the
workflow.

This repository is a reproducible ECDLP research program, not a product. Its
output is a body of records whose value is entirely their integrity, so review
record integrity first and code second. The rules cited below live in
`AGENTS.md` (binding contract), `docs/claims-and-verification.md`, and
`docs/evidence-and-reproducibility.md`.

## The reviewer has no authority

Post findings; change nothing. Do not approve, do not request changes, do not
edit a file, do not push a commit, and never state that a hypothesis,
experiment, or evidence record has changed status. Only the Coordinator changes
official research state (`AGENTS.md`, "Roles").

This reviewer is **not** the program's Reviewer, Validator, or Red Team role.
Those are independent research tasks defined in `orchestration/roles.yaml`, run
against committed artifacts under a Coordinator handoff. This one reads a diff
and has no standing in the research record. Never write a finding that implies
otherwise, and never suggest that merging the PR settles a research question.

## What Important (🔴) means here

Reserve 🔴 for defects in the *record*, plus ordinary breaking bugs in code.
The eight below are the ones that matter most, roughly in order:

1. **Mutating an immutable record.** Rule 4: corrections supersede, never
   overwrite. CI mechanically blocks this only for `experiments/**/runs/**`, so
   an edit or deletion of an existing `ledger/**` record or `knowledge/**`
   entry passes CI and is yours to catch. Check the diff status, not the
   content: any `M` or `D` on a record that already exists on the base branch
   is a finding. Adding a new superseding record is correct and not a finding.
2. **Claim exceeding its tier.** `validate_ledger.py` checks the `claim_tier`
   *field* against run parameters; it cannot read prose. Flag any analysis,
   synthesis, README, knowledge entry, or PR description whose language omits
   the tested parameters, evidence scope, or transfer assumptions. Also flag
   any universal impossibility
   claim ("X cannot beat Y"), which no tier permits.
3. **Fabrication risk.** Rule 9. Any timing, count, speedup, solving degree,
   or citation that does not trace to a committed artifact is a finding. The
   bar is a run ID, record ID, or repository path the reader can open. Prose
   that describes a run, command, or output with no corresponding file in the
   diff or the tree is the single worst failure mode in this repository —
   treat an unresolvable number as Important, not as a nit.
4. **Infrastructure failure presented as mathematical evidence.** Rule 5. A
   timeout, crash, OOM, or `failed_infrastructure` run cited to weaken or
   reject a hypothesis. A failed certificate is `invalid_measurement`, never a
   `negative_observation`.
5. **Certificate discipline.** `docs/claims-and-verification.md`. CI checks
   that `certificate.verified` is `true`; it cannot tell whether the verifier
   was genuinely independent. Flag a certificate whose verification path runs
   through the solver's own state, or that lacks `verifier` /
   `verifier_commit`.
6. **State transition without authority or basis.** A changed hypothesis or
   experiment `status:` with no accompanying decision record, a decision whose
   rationale is not supported by the evidence it cites, or an adverse
   transition (`weaken`, `reject_scoped`, `rejected`) with no refutation
   artifact and no honest `proof_status: empirical_only` declaration.
7. **Conclusion without citation.** Rule 10: every conclusion names the
   EXP/RUN/EV IDs that support it. Cross-refs are checked mechanically only
   for records; markdown prose is not.
8. **Provenance loss in a run manifest.** A missing or contradictory
   `requested_policy` / `canonical_policy` / `backend` / `model_verified`, a
   silent substitution without `fallback_used` and a reason, or an unrecorded
   entry in `degraded_requirements`.

For code under `tools/`, `harness/`, `orchestration/`, and `src/`, apply the
normal bar: 🔴 for logic errors, broken edge cases, and regressions that would
corrupt or silently weaken a check. A validator that stops catching what it
claims to catch is an integrity failure, not a style issue.

## Nit (🟡)

Style, naming, wording, and structure. Report at most five per review; if you
found more, give the count in the summary instead of posting them. Newly
introduced `CLAUDE.md` violations are nits unless they fall under one of the
eight above.

## Do not report

- Anything `.github/workflows/validate.yml` already enforces: ledger schema and
  required fields, record cross-references, the numeric `claim_tier` ceiling,
  run companion artifacts, `experiments/**/runs/**` immutability, knowledge
  index freshness, runtime-binding drift, dispatch-queue validity, and pytest.
  If one of those would fail, CI says so; repeating it wastes the author's
  attention. Reasoning that CI *cannot* reach is exactly your job.
- Missing test coverage for research records. Records are data, not code.
- The volume or verbosity of research prose, and the writing style of
  `research_directions_*.md`.
- Anything under `tools/*_baseline.txt`, `tools/legacy_*.yaml`, or a generated
  index — those are regenerated, not hand-edited.

## Verification bar

State only what you checked. A behavioral claim needs a `file:line` citation,
not an inference from a name. Before reporting a record as mutated, confirm it
exists on the base branch. Before reporting a number as unsupported, search the
repository for the ID or path that would support it. When a finding rests on
something you could not verify, say so in the finding or drop it — an
unverified assertion in a review of *this* repository is the same failure the
repository exists to prevent.

## Re-review convergence

After the first review of a PR, post Important findings only. Do not re-raise a
finding the author addressed, and do not open new nit threads on a branch that
is converging.

## Summary shape

Open the summary with a one-line tally by category, for example
`2 record-integrity, 1 code, 3 nits`. Lead with "No integrity issues" when the
diff is clean on the eight checks above, even if nits follow. Then list the
findings by severity, and close with anything you deliberately did not check.
