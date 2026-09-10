# Execution mode

Use this for unqualified run/continue requests and named experimental execution.
It narrows the work selection in `lifecycle.md`; it does not waive any lifecycle
approval, dispatch, claim, isolation, archival, publication or review gate.
Read repository `docs/experiment-execution.md` for the process adapter contract.

1. Resolve/preflight the checkout and retain the named EXP/GOAL/TASK scope.
   Resume the recorded lane and unfinished work rather than generating ideas.
2. Select existing work with `python3 tools/newest_experiments.py --limit 3 --json`.
   Add `--goal <ID>` or repeat `--experiment <ID>` when scoped. This is a page,
   not a session-completion threshold. Retain ECC-first/newest-first priority.
3. Use `--include-blocked --limit 0 --json` to expose unmet prerequisites and
   incomplete legacy attempts. Check actual claims before launching anything.
   An empty runnable queue does not authorize ideation or invention of tasks.
4. For ready work, arrange the existing committed handoff, dispatcher checks and
   published claim. A fresh executor receives only runtime-core, its role
   contract, exact specification/handoff and referenced source paths.
5. Missing code/plan: dispatch scoped preparation/implementation for that exact
   experiment. Its completion condition names the executable it unblocks.
   Resolve contract fields through Coordinator approval without asking the user
   again. Preserve frozen protocols and explicit zero-run prerequisites.
6. For a compatible frozen trial plan, the executor invokes
   `tools/experiment_execution.py run --plan <path> --owner <owner> --epoch <epoch>`.
   This continues eligible trials without model calls. It is not a standalone
   portfolio daemon and cannot acquire authority or publish on its own.
7. Inspect artifacts, classify failures, release the actual claim outcome, and
   perform the Coordinator-only snapshot archive and verification before
   independent review. Publish the package and PR through the existing lifecycle.
   No executor interprets observations as support, rejection or closure.
8. Continue with the next eligible existing experiment. Independent review and
   scientific state decisions use their proper sessions and gates; they must
   not serialize unrelated already-authorized execution. A dependency requiring
   review still waits for review. Do not reopen a terminal goal.

Preparation cannot become a proposal-only loop. Do not create new goals, intake
new ideas, perform portfolio-wide literature/closure discussions, or rewrite
research policy in this mode. A necessary repair must name its blocked existing
experiment and executable unblock condition. If nothing can proceed, report
specific impediments and a durable next action; do not busy-loop unchanged checks.

Report measured trial coverage, workers/owners, failures and prerequisites,
archive/publication state, and the one recorded next action. Ideas, documents,
commits and passing unit tests are not experimental results. Directory existence
is neither completion nor permission to rerun. A negative measurement is not a
reason to retry, and an infrastructure failure is not a mathematical refutation.

A checkpoint resumes this same mode and scope. Stop at an explicitly requested
named-task boundary, user stop, genuine unresolved impediment, or session end;
never promise that a chat session continues work in the background.
