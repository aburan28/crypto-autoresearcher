# Binding specialized agent rules

These rules were moved from `AGENTS.md` on 2026-10-25, with relative links adjusted for this directory, to keep the always-loaded instruction and skill wake budgets within their checked limits. `AGENTS.md` links to each section and explicitly keeps it binding. If wording conflicts, `AGENTS.md` wins.

## Name the obstruction

When substantial research, cryptanalysis, or audit work cannot meet a proof,
implementation, experiment, or validation requirement, **name the specific
problem**. Before repeating the same blocked approach or handing it off, create
or update `problems/<descriptive-slug>.md` using
[the problem template](../problems/TEMPLATE.md), add it to
[the problem index](../problems/README.md), and link it from the affected work.

- State exactly what is blocked, under which parameters and assumptions, and
  why that gap prevents the requested conclusion. Track major or recurring
  blockers, not every routine TODO.
- Separate observed evidence, suspected explanations, missing implementations,
  access/tool or assistance limits, resource limits, and proved mathematical
  obstructions. Cite artifacts or proofs with their exact scope; mark unknowns
  explicitly. A timeout or bounded failed search does not prove impossibility;
  failure to find an attack does not establish security.
- Say **what would unblock it**: the missing lemma, construction, verified map,
  measurement, implementation, access, or resource, with checkable acceptance
  criteria. Explain what satisfying those criteria would establish and what
  would remain unresolved. "More research" is not an exit condition.
- Give the next discriminating experiment or proof obligation, its controls
  and execution limits where relevant, and how each possible outcome changes
  the next action. Apply the existing experiment and budget rules.
- Reuse an existing problem record for the same obstruction, including a
  cross-repository link when appropriate. Update its evidence, next action,
  and index row in the PR that changes the situation; preserve frozen evidence.
  Resolve it only with linked evidence meeting its exit criteria. If another
  record replaces it, mark it superseded and link the successor.

Recording a problem keeps the original requirement visible; recording it alone
does not resolve that requirement. It
does not authorize abandoning requested work, weakening its acceptance criteria,
or promoting a claim. Completing the template or merging its PR does not solve
the underlying problem.

In this repository, link problem records to existing goal impediments and
inventor-protocol obstruction records. Problem status is not a goal or
hypothesis status; scientific transitions retain their existing authority.

## Research direction

For work explicitly pursuing an algorithmic-complexity claim, the target
profile is Wesolowski's `p^{1/3+o(1)}` supersingular isogeny result
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`;
`docs/target-result-profile.md`, checklist C1–C18; `KN-TECH-055`):
exponent first; numbered heuristics, each with random-model justification,
falsification condition and validation plan; single-responsibility lemmas;
external structural ingredients; validation at scale; honest cost and scope
(memory beside time, o(1) disclosed, a concrete cost table, affected-vs-safe
scope). The Coordinator checks the promotion gates of `agents/coordinator.md`
before an asymptotic claim moves toward `supported`. This profile qualifies
those claims; it is not an admission or success criterion for descriptive
observation and anomaly measurement.

The **inventor protocol** (`docs/inventor-protocol.md`; `KN-TECH-056`,
`KN-TECH-080`) binds the Idea Generator, Validator, Red Team and, for §8, the
Coordinator: premature closure fails like overclaiming; a closure needs a
named obstruction, recorded as a measured `obstruction` block with a
`resource_check`, an argument and forward guidance (a count of rejected
mechanisms is `unverified`); a signal is an artifact until run against a null
object of the same shape; deliverables claiming a comparative algorithmic
advance carry a checked `dominated_by` and a quantitative `sota_delta`.
Descriptive deliverables state their actual reference and uncertainty without
inventing a competitive claim. A proof-oriented proposal carries a
`proof_search_map` whose four cheap audits run before compute and before the
Coordinator approves implementation.

**Scheme construction** (signature, PKE, KEM, AKE proposals; scheme-security
claims) meets the six obligations of `docs/scheme-construction-contract.md`
and its YAML template: exact game, adversary model, oracles, assumptions,
correctly directed reductions, named missing lifts. Template completeness and
merge certify nothing.

## Cursor Cloud specific instructions

Use `/usr/local/bin/python3` (CPython 3.12.8, `.python-version`), never the
image's Ubuntu `/usr/bin/python3`: its builtin `_md5` fails
`tests/test_harness.py::test_md5_pin_mechanism_real_registry_is_distinct`.
Install the CI extras, not only `make install` (`.[agent,dev]`):
`python3 -m pip install -e ".[dev,agent,campaign-mcp,research-loop,gf2]"`.
`autoresearch` and `pytest` land in `~/.local/bin`, linked into
`/usr/local/bin`; `python3 -m pytest` and `python3 -m orchestration` work
either way. `autoresearch doctor` needs no API keys; `.env.example` variables
serve only token-spending commands. Dashboard:
`GITHUB_REPOSITORY=aburan28/crypto-autoresearcher python3 -m ui --host
127.0.0.1 --port 8787` (unset, source links come from `origin`, whose Cloud
Agent remote embeds a credential). `formal/setup.sh` (Lean) is not part of
this environment.

## Progress metrics (daily lab report)

`tools/progress_metrics.py` exports this repo's progress KPIs as JSONL for the lab-wide daily
report (`/Volumes/SSD990-2/progress-metrics`). It reads committed state at `origin/<default>` and
prints one sample per line (`metric, value, date, problem, unit, better, kind, label, source`).

- When a PR adds or changes a benchmark, leaderboard, result file or ledger source that carries a
  number worth tracking day over day, extend the exporter in the same PR. Keep metric ids stable;
  a renamed id is a new series.
- Never emit estimates. If a source is missing, emit nothing for it.
- `python3 tools/progress_metrics.py --since 2026-10-01` must run in under a minute, stdlib only,
  no builds, and never read the working tree.
