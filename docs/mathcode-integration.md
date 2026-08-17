# MathCode: the formalization producer for the formal research lane

**Status:** wired; engine installed per machine, never vendored

[MathCode](https://math-ai-org.github.io/mathcode/) is a terminal agent with a
Lean 4 formalization engine attached: it turns a plain-language mathematical
statement into a Lean theorem and attempts the proof, with a persistent Lean
REPL, Mathlib lemma search over LSP, and parallel subgoal decomposition.

The formal lane (`docs/formal-research-lane.md`) already had a **verifier** —
`LeanWorker` runs `lake build` and the axiom audit and rejects forbidden
constructs — and no **producer**. Every task therefore returned
`missing theorem file` unless a human hand-wrote the Lean first. MathCode is
that missing half, and this document is how it attaches.

```text
claim (natural language)
      |
      v
MathCodeFormalizer          untrusted producer, runs OUTSIDE the workspace
      |  candidate .lean
      v
pre-stage scan              unfinished / smuggled candidates never enter formal/
      |
      v
LeanWorker                  lake build + AxiomAudit.lean   <-- the only machine evidence
      |
      v
semantic-fidelity review    independent; a proof that compiles may still be the wrong theorem
      |
      v
Coordinator                 the only thing that can promote any of this into claim state
```

## Install the engine

MathCode is a per-machine tool with its own Lean toolchain and Mathlib cache.
It is not a Python dependency and is deliberately not vendored here.

```sh
git clone https://github.com/math-ai-org/mathcode.git
cd mathcode
bash setup.sh          # bundles .local/elan, prepares .env from .env.example
codex auth login       # the default backend is the codex CLI
```

`setup.sh` installs a user-local `mathcode` launcher. Requirements per upstream:
macOS arm64 or Linux x86_64, `curl`, `shasum`/`sha256sum`, and enough disk for
the bundle plus Mathlib caches.

Then, from this repository:

```sh
autoresearch formal doctor
```

which reports the engine, its version, the resolved knobs, the Lean workspace
contract, and whether `lake` is on PATH — and exits non-zero while anything is
missing. It never guesses: an engine that does not report `--version` is
recorded as *not reported*, not as a version.

## Run one task

```sh
autoresearch formal formalize \
  --task-id TASK-20260817-a1b2c3 \
  --claim-id CL-ECDLP-0041 \
  --claim-file claim.txt \
  --theorem-name CryptoResearch.ECDLP.genericLowerBound \
  --theorem-file CryptoResearch/ECDLP/GenericLowerBound.lean \
  --hypothesis H-ECDLP-017 \
  --kind formalize_claim \
  --artifact-out experiments/EXP-.../formal/FP-ECDLP-00017.json
```

`--kind` selects one of the four frontier task kinds
(`formalize_claim`, `find_proof_gap`, `formal_counterexample`,
`proof_generalization`); each sends the engine a different instruction. Inspect
the exact text with `--print-prompt`, which exits without running anything.

Exit codes: `0` machine-verified (pending review), `1` a mathematical outcome
short of that — blocked, invalid, refuted — and `3` an engine failure, which is
**not** a result about the claim.

The command prints a `crypto.autoresearch.formal_proof.v1` artifact carrying a
`formalizer` provenance block: engine version, the MATHCODE_* knobs actually
used, the sha256 of the prompt and of the generated source, the attempt
directory, exit code, and wall-clock duration. Hashes that could not be computed
are `null`.

## Configuration

| variable | meaning | default |
| --- | --- | --- |
| `AUTORESEARCH_MATHCODE_BIN` | launcher to invoke | `mathcode` |
| `AUTORESEARCH_MATHCODE_EFFORT` | engine effort | `high` |
| `AUTORESEARCH_MATHCODE_TIMEOUT` | engine budget, seconds | `1800` |
| `AUTORESEARCH_FORMAL_ATTEMPT_ROOT` | where attempts are kept | `.formal-attempts` |
| `MATHCODE_*` | passed through to the engine | `LEAN_REPL`, `USE_LSP`, `AGENT_PROVE` on |

Any `MATHCODE_*` already exported wins over the default, so a session can turn
on tree proving (`MATHCODE_TREE_PROVE=1`) or multiple planners
(`MATHCODE_NUM_PLANNERS=3`) without editing code — and whatever it set is
recorded in the artifact.

MathCode picks its own inference backend (`MATHCODE_USE_OPENAI`,
`MATHCODE_USE_OPENROUTER`, `ANTHROPIC_API_KEY`, …). It is **not** resolved
through `orchestration/model-policies.yaml`: it is an external instrument, like
a solver, not a role in `roles.yaml`. Record which backend served an attempt in
the task receipt if it matters to the result.

## What the integration refuses to do

Three behaviours exist because of specific ways this could go wrong. All three
are enforced in code and covered in `tests/test_mathcode_formalizer.py`.

**The engine never runs inside the Lean workspace.** MathCode is an autonomous
coding agent that writes files where it is started, and `LeanWorker` scans
*every* `.lean` file under the workspace. One abandoned scratch file containing
`sorry` would mark every later task in that workspace `INVALID`. Each attempt
gets its own directory under `.formal-attempts/`, outside the workspace and
gitignored; only the single selected file is copied in. Attempt directories are
never reused — a retry becomes `TASK-….2` — because the artifacts of a failed
formalization are the record of what was tried.

**An unfinished proof is not a contract violation, and never reaches the
workspace.** A candidate whose only forbidden constructs are `sorry`/`admit` is
an *incomplete formalization*: it is held in the attempt directory, the unproved
sites are reported as `sorry:<line>`, and the outcome is
`formalization_blocked` — which is exactly the input `find_proof_gap` successors
consume. A candidate declaring a custom `axiom` or `unsafe` is a different
thing, an assumption the audit cannot see, and is reported `invalid`.

**An engine failure is never negative evidence.** A missing binary, a timeout,
an engine that exits non-zero or writes no Lean, or output that declares some
other theorem, all produce *no* `FormalProofResult` at all. They surface as
`INFRASTRUCTURE_FAILURE` with `claim_interpretation: inconclusive`, per AGENTS.md
rule 3. Nothing in this integration can turn "the tool broke" into "the claim is
false", and nothing in it writes Lean the engine did not produce.

## What a green run does and does not mean

`machine_verified` means: this file compiled against the pinned toolchain, the
axiom audit passed, and it contains no `sorry`, `admit`, custom `axiom`, or
`unsafe`. It does **not** mean the theorem is the claim.

The failure mode that matters is a model-authored statement that compiles and
means less than it appears to — a quantifier in the wrong order, a hypothesis
that is never satisfiable, a specialization that drops the hard case. The
generation prompt argues against it explicitly ("a statement that is true but
does not capture the claim is a failure of this task, not a partial success"),
but a prompt is not a guarantee, and the engine's incentive is to return
something that compiles.

So the artifact is emitted with `semantic_review: {required: true, status:
pending}`, and `verification_outcome_from_formal_result` reports a
mechanically successful proof as `INCONCLUSIVE` until an independent reviewer
confirms fidelity. The reviewer compares the Lean proposition against the
original claim and rejects vacuous statements, weakened quantifiers, hidden
assumptions, and claims proved only from impossible premises. Only then may the
Coordinator consider promotion, under the usual scoping and citation rules.

## Reproducibility and sandboxing

Anything intended as evidence should run with a pinned `lean-toolchain` and
`lake-manifest.json` in the workspace — both are hashed into the artifact's
`provenance` block — in a resource-bounded container. The engine needs network
access for its inference backend, so it cannot be run network-disabled; the
*verification* step can and should be, and it is the verification step that
produces the evidence.

Re-running a formalization is not expected to be byte-identical: the engine is a
language model. Reproducibility here binds the **verification**, not the
generation — the staged source, its hash, the toolchain, and the manifest are
what a later reviewer re-checks, and they are all in the artifact.
