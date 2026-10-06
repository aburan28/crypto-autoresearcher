# Skills and tool routing

Use one primary skill for the requested action, with a subject profile only when
it adds useful context. Explicit experiment execution goes directly to `run`;
this guide, catalog checks and subject assessment are never launch preflights.

## Choose by action

| Request | Primary skill | Boundary |
| --- | --- | --- |
| Run an existing experiment, goal, task or command | `run` | Execute existing public synthetic trials; preserve named scope and built-in admission |
| Turn an idea into a frozen trial | `design-experiment` | Coordinator design/approval; no trial execution |
| Review results or a scientific conclusion | `review-evidence` | Independent claim-tier review; no automatic promotion |
| Show progress or unresolved work | `research-status` | Read-only record snapshot |
| Rank goals or continue coordination | `coordinate` | Existing Coordinator authority |
| Generate candidate research ideas | `propose-ideas` | Falsifiable proposals, not validated discoveries |
| Research literature and portfolio context | `deep-research` | Source-grounded inquiry and existing lifecycle |
| Ingest a source or distill validated findings | `curate-knowledge` | Preserve provenance and promotion requirements |
| Produce explanatory research diagrams/PDF | `research-visuals` | Derived communication, not scientific authority |
| Cross-lane context | `consolidate-lanes` | Independent pointer consolidation, not findings |
| Explicit inter-agent messaging | `agent-bus` | Pointers only; never approvals or work assignments |
| Improve a skill | `tune-skill` | Existing skill evaluation workflow |
| Choose a tool or locate a workflow | `route` | Read-only selection, no execution |
| Deliver code or handle a PR | `pr` | Scoped checks/publication; merge only if authorized |

## Choose by subject

| Subject | Profile | Representative implementation paths | Concrete output |
| --- | --- | --- | --- |
| Curve IDs, fields, traits, catalogs | `curve` | `tools/curve_identity.py`, `ui/curves.py` | Exact IDs, pins, sourced traits and unknowns |
| CM, conductors, GLV/GLS, Frobenius | `endo` | `harness/endosweep/`, `tools/isogeny_class_screen.py` | Map/lattice/cost evidence separated |
| Covers, lifts, descents, correspondences | `transfer` | Existing assessment template; explorer in pending PR #1909 | Typed maps, subgroup certificates and open obligations |
| Factor bases and independent relations | `ic` | `src/crypto_autoresearcher/index_calculus/`, `harness/rl_isogeny/` | Stage accounting and relation validity/rank |
| Gröbner, SAT, Macaulay, GF(2), elimination | `solver` | `groebner_compare/`, `harness/macaulay_fp/`, `src/crypto_autoresearcher/gf2/` | Input/adapter/certificate and bottleneck report |
| Performance claims and comparisons | `bench` | `harness/efficiency.py`, `groebner_compare/relation_metrics.py` | Matched cost table, uncertainty and limitations |
| CUDA/arithmetic/occupancy | `gpu` | `harness/gpu/`, `src/crypto_autoresearcher/gf2/gpu/` | Correctness evidence and scoped kernel change |
| Cloud jobs, runtime, storage, checkpoints | `ops` | `tools/gf2_runpod.py`, `scripts/rho_dp/`, `kb/`, runtime CLIs | Actual resource status, maintenance and checkpoint identity |
| PKE/KEM/signature/AKE obligations | `scheme` | `docs/scheme-construction-contract.md`, companion template | Game/algorithm/reduction obligation table |
| Lean proofs and verification receipts | `formal` | `formal/`, `orchestration/formal/cli.py` | Exact statement, build/axiom status and gaps |
| Dashboard, imports and static readers | `ui` | `ui/`, shared `ui/payloads.py` contract | Reader behavior, source pins, preview and tests |
| Branches, CI, review and PRs | `pr` | Merge-hygiene, immutability and landing tools | Reviewable scoped diff and observed PR state |

Profiles inspect supplied artifacts, support implementation and prepare bounded
synthetic work. They do not independently launch trials or create autonomous
production-target exploitation. A domain name in a request never changes the
primary action: “run the solver experiment” uses `run`; “review the solver
results” uses `review-evidence` with `solver` context.

## Examples

| User wording | Primary | Supporting profile |
| --- | --- | --- |
| “Run EXP-… on its existing inputs” | `run` | Load only that launcher's relevant subject sources |
| “Design a paired genus-two transfer test” | `design-experiment` | `transfer` |
| “Check whether these GLV timings are fair” | `bench` | `endo` |
| “Audit subgroup preservation in this supplied map” | `transfer` | `curve` if identity metadata needs repair |
| “Why is this Macaulay matrix elimination failing?” | `solver` | `ic` if relation semantics matter |
| “Make the GPU multiply faster” | `gpu` | `bench`; existing benchmark execution remains `run` |
| “Check the RunPod job and saved checkpoint” | `ops` | No automatic scientific launch |
| “Formalize this stated lemma” | `formal` | Frozen formal task execution remains `run` |
| “Does this recipient-lift construction meet IND-CCA?” | `scheme` | `formal` only for a supplied proof obligation |
| “Add sourced curve traits to the dashboard” | `ui` | `curve` |
| “Ingest these papers into KN” | `curate-knowledge` | No new literature-ingestion skill required |
| “Merge this PR if review and checks pass” | `pr` | Inspect the authorized exact head revision |

## Catalog commands

```sh
python3 tools/skill_catalog.py list
python3 tools/skill_catalog.py route --intent run --topic solver
python3 tools/skill_catalog.py route --intent review --topic transfer
python3 tools/skill_catalog.py check
python3 tools/skill_catalog.py drift
```

These commands read files only and never execute catalog entries. `route` uses
explicit intent/topic values; it is not an autonomous planner or natural-language
classifier. `check` validates canonical/adaptor metadata, owner mappings, console
declarations and current source-path presence. `drift` reports uncataloged Python
or shell CLI markers for maintenance. Neither proves runtime readiness or complete
coverage of arbitrary executable code. `check --snapshot-only` validates metadata
in a partial checkout and explicitly does not assert local source availability.

## Audit and coverage

The source inventory is pinned to main commit
`3575cc2705c200ffc0c0163c82548ab3335585ce`, with the existing `transfer` skill
from PR #1908 reused in this change. On that main snapshot Claude exposed 12
skills and `.agents/skills/` exposed only three. This change adds 12 short subject
and maintenance skills and adapters for nine previously unexposed lifecycle skills.
Including transfer, both surfaces expose 25 canonical names.

`docs/skill-tool-inventory.json` records 381 selected source paths (including the
pending explorer reference and this catalog utility): tool and module entrypoints, libraries, native
kernel sources, shell scripts and formal sources. 92 entries have source-read
inspection; the remainder have path-inventory inspection. Six installed console
entrypoint declarations are recorded separately. These are declarations and
tracked sources, not proof that a binary is installed or runnable here.

Maintained roots audited: tools, src, orchestration, scripts, harness,
groebner_compare, kb, formal and ui, plus the skill/plugin discovery surfaces.
Archived experiments, inputs, outputs, third-party code, test fixtures and
generated digests are not promoted into one skill per historical executable.
Contract-specific harness programs remain with `run`; old repair scripts remain
historical maintenance references and are not generalized into destructive recipes.

The repo contains source for endosweep, prime-field IC, Boolean/GF(2) diagnostics,
GPU step/kernel measurements, Lean integration, KB, dashboard and cloud wrappers.
It does not contain the full ECC2K-130 solver binary referenced by the external
autolab runbook. Rust binaries in `crypto`/`cryptanalysis` require those checkouts;
this audit does not claim to inspect or install them. The transfer explorer is
pending PR #1909 and remains optional until actually present in a checkout.

No scientific trial was launched, novelty or speedup declared, or ledger state
changed by this audit. Existing `run`, `coordinate` and review/archive contracts
retain authority. New skills live in `.claude/skills/`; `.agents/skills/` contains
thin adapters with the same names and canonical pointers. They are repository
skills available to those hosts after the branch is checked out, not a personal
Skills-page installation.

Two concrete workflow defects were corrected: coordinate's lifecycle reference
pointed at a nonexistent local `references/` directory, and design-experiment's
blanket rejection of null fields contradicted advisory/unlimited budget policy.
The fixes preserve the existing scientific-contract completeness requirement.

Validation: all 25 canonical skills pass skill-creator structural checks, and
the focused routing suite passes. A fresh read-only forward-test correctly routed
eight recurring requests while reporting missing artifacts in the partial audit
checkout. It also identified the RunPod wrapper's lack of a named-job status
command; ops now states that limitation explicitly. Validation checks metadata,
routing and source interfaces, not scientific claims or live infrastructure.

## Maintain the map

When adding a reusable workflow, update its canonical description, host adapter,
`docs/skill-catalog.json`, and the relevant inventory rows together. Include exact
source/console interfaces, availability and execution/authority boundaries. Run
the focused catalog tests and `check`; inspect `drift` after new CLI sources land.
Keep descriptions sufficient to trigger the skill without loading its body.
Reuse lifecycle skills instead of duplicating them under a shorter alias.
