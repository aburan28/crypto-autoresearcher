---
name: sheriff
description: "Wildly deep integrity audit of research results across crypto-autoresearcher, crypto and cryptanalysis: execution proofs and STARK/zk verifiers, Lean theorems (holes, axioms, statement fidelity), solve certificates, cost accounting against matched rho, statistics and preregistration, provenance and replays, and every number in papers. Use for /sheriff, 'is this result real', before a claim, paper or benchmark row lands, after a claimed breakthrough, or on a schedule. Writes write-once cases; never repairs or changes research state."
---

# Sheriff

Is the result what it says it is? The sheriff checks every link from the
sentence to the bytes, and assumes nothing was checked until it sees the check.
The beat-by-beat checklist is [`docs/sheriff.md`](../../../docs/sheriff.md):
read the beats your target reaches before you start. `tools/sheriff.py` is the
deterministic half.

A case is an audit record, like `audit-runs`. It is never a
`validation_report`, never satisfies a `review-adversarial` or
`review-breakthrough` gate by itself, and changes no status. It repairs
nothing: a broken result gets a finding saying what would fix it, never an
edit. The Coordinator decides what follows.

## Arguments

`/sheriff <target> [deep]`. The target is one of:

- `all`;
- an `EXP-*` or `RUN-*` id;
- a path, or `crypto:<path>` / `cryptanalysis:<path>`;
- a PR number (check out its head first);
- a sentence quoting the claim, which you locate first.

`deep` adds the slow and toolchain-dependent checkers: the Lean builds and
axiom audits, the ledger validator, merge hygiene, ecbench replays and bound
checks, and the zk tests. Use `deep` for anything that will be cited.

## Steps

0. **Bind.**
   - Fetch `origin/main` in every repository the target touches. Audit the
     published state, or the PR head when the target is a PR.
   - Refuse when this session produced the result.
   - Write your prior, what you expect to be broken and why, before reading.
1. **Sweep.** Run
   `python3 tools/sheriff.py sweep --target <target> [--deep]`. It does four
   things:
   - It runs the canary (planted defects that must be caught, look-alikes that
     must not be).
   - It scans Lean, zk verifiers, receipts, proof language, strong words and
     paper numbers in all three repositories.
   - It runs every existing checker it can, and records `not_covered` for the
     rest.
   - It writes `research/sheriff/SHF-*/sweep.{json,md,svg}`.

   If the canary failed, stop: report the instrument failure and uphold
   nothing. Install what `--deep` needs where you can (`./formal/setup.sh`,
   `cargo build --release --bin ecbench`). What stays uninstalled is
   `not_covered`.
2. **Claim inventory (B1).** List every claim in scope in the producer's
   words, with location and cited artifacts. Split compound claims, and count
   claims made by omission. A claim that cites nothing is already
   `unsupported`.
3. **Work the beats** that apply to each claim (`docs/sheriff.md`):
   - **B2:** execution proofs, and STARK/zk verifiers with mutation controls;
   - **B3:** Lean builds, axioms per cited theorem, statement fidelity and the
     proves-too-much control;
   - **B4:** independent certificate re-verification and target independence;
   - **B5:** class, baseline, matched rho, 0/0.1/1 GAE pricing, phases and
     bounds;
   - **B6:** preregistration from git chronology, stopping, forking paths,
     controls and uncertainty;
   - **B7:** commits, immutability, archive hashes, replays and citations;
   - **B8:** number tracing, words against tier, PDF currency and derived
     views.

   Every sweep lead is either confirmed (a finding with evidence) or dismissed
   (one line saying why). A lead you did not look at is `not_covered` for its
   claim.
4. **Independent readers (B9).** Give each load-bearing joint to exactly one
   reader, with blindness declared:
   - `validator`: certificates, controls, receipts, Lean fidelity and verifier
     soundness, given the matching checklist;
   - `red-team`: interpretation and cost model;
   - `validator-breakthrough` and `red-team-breakthrough` at `max` for any
     `review-breakthrough`-class claim, never degraded.

   Each reader does one blind re-derivation of a load-bearing quantity from
   the statement and parameters alone, and runs a proves-too-much control. Each
   writes `readers/<joint>.yaml`. Write your own re-derivations and independent
   checks under the case's `scripts/`, never in the producer's tree.
5. **Compose.**
   - Write `findings.yaml` (`sheriff.case/v1`): claims with verdicts, per-beat
     states, evidence and linked findings, and each finding's severity, what
     is wrong and what would fix it.
   - Run `python3 tools/sheriff.py check-case <case>` and fix the case until it
     passes. Never bend a verdict to satisfy the checker.
6. **Report.**
   - `REPORT.md`:
     - the prior;
     - the verdict table;
     - blockers first;
     - per-beat results;
     - what was `not_covered` and the command that would cover it;
     - what the case does not establish.
   - Render `report.pdf` with `sweep.svg` embedded (`research-visuals`,
     "Rendering") and read every page.
   - A recurring or blocking obstruction gets a `problems/` record.
7. **Publish.** Commit only the case directory (and any problem records) on
   this session's branch, push, and open or refresh the PR.
8. **Receipt.**
   `python3 tools/session_receipt.py --skill sheriff --role validator
   --outcome <reviewed|no_change|impeded> --created <SHF id>`.

## Verdicts

| verdict | when |
| --- | --- |
| `upheld` | Every applicable beat passed; the evidence is cited and on disk. |
| `upheld_scoped` | Nothing failed, but only the narrower `scoped_to` statement is supported, or a beat was `not_covered`. |
| `overclaimed` | The evidence supports a weaker statement (`scoped_to`) than the one made. |
| `unsupported` | No admissible evidence for it. |
| `broken` | A check failed: a wrong answer, a failed certificate, a hole or axiom, a verifier that accepts a mutant, an ignored failed control, a modified sealed record. |
| `not_covered` | Could not be checked here; name what would check it. |

Severity: a `blocker` means nothing may cite the claim until it is fixed; a
`major` means narrow the claim or supply the evidence; a `minor` does not change
the verdict.

## Rules

- **`not_covered` is never a pass.** A missing toolchain, an off-disk artifact
  or an unread lead is reported as such, never as clean.
- **Re-run, don't read.** A recorded `verified: true`, a green CI badge, a
  hash, or a reviewer's sign-off is a claim about a check. Repeat the check
  when you can, and say when you could not.
- **Replays, hashes, signatures and attestations are not execution proofs.**
  As of 2026-10-16 the milestones of `docs/execution-proof-chain.md` are open,
  so "execution verified" applies to nothing here yet.
- **A Lean build proves the Lean statement under its axioms, nothing more.**
  Statement fidelity is a reader's check, and the formal lane's
  `semantic_review` stays pending after this screen.
- **Narrow, don't round up.** Report the strongest statement the evidence
  carries (`upheld_scoped`, `overclaimed`), not a pass or fail on the
  producer's wording.
- **Every improvement is a success, honestly sized.** Report each result's
  verified delta over the current baseline, and its gap to matched rho as
  distance remaining. Relabelling and accounting are not improvements.
- Case directories are write-once; a re-audit is a new `SHF-*`. Scripts write
  only under the case directory. Never edit an audited artifact, run a
  scientific trial, or change research state.
- A bounded search, a timeout or a zero-hit count proves no absence. An
  impediment is never negative evidence.
