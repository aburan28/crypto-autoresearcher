# Sheriff: deep integrity audit of research results

The `sheriff` skill (`.claude/skills/sheriff/SKILL.md`) answers one question
about a result: **is it what it says it is?** It audits a claim, an experiment,
a paper, a benchmark row, a PR or everything at once, across
`crypto-autoresearcher`, `crypto` and `cryptanalysis`. It looks at every link
between the sentence and the bytes. That covers the execution-proof chain and
any STARK or zk verifier the claim leans on, Lean theorems, solve
certificates, cost accounting against the matched rho, statistics and
preregistration, provenance and replays, and every number in the prose.

This manual is the checklist. The skill is the procedure; `tools/sheriff.py`
is the deterministic half (sweep, canary, case check). Nothing here creates a
new evidence rule: each check cites the contract it enforces, and where this
file and `AGENTS.md` (or a sibling's `AGENTS.md`) disagree, they win.

## What a case is, and what it is not

A case is an **audit record**, like an `audit-runs` audit. It is not a
`validation_report`, it never satisfies a `review-adversarial` or
`review-breakthrough` routing rule on its own, and it changes no hypothesis,
experiment or goal status. The Coordinator may cite a case when it opens a
review round, and the case's findings are what it acts on. The sheriff repairs
nothing: a broken result gets a finding with what would fix it. It never gets
an edit to the record.

The sheriff is skeptical by construction. It assumes nothing was checked until
it sees the check, re-runs what it can, and states what it could not. **A
check that did not run is `not_covered`, never a pass.** A clean bill means
exactly the beats that passed, on exactly the commits recorded.

## Verdicts

Each claim in a case gets exactly one verdict:

| verdict | meaning |
| --- | --- |
| `upheld` | Every applicable beat passed, and the evidence is cited and on disk. |
| `upheld_scoped` | True as narrowed in `scoped_to`. Some beat was `not_covered` or the evidence supports only a narrower statement, but nothing failed. |
| `overclaimed` | The evidence supports a weaker statement (`scoped_to`). The wording, tier, scope or comparison goes past it. |
| `unsupported` | No admissible evidence: missing artifact, untraced number, uncited source, unverified answer. |
| `broken` | A check failed: wrong answer, failed certificate, `sorry`/axiom, a verifier that does not verify, a failed control that was ignored, a modified sealed record. |
| `not_covered` | The sheriff could not check it (toolchain absent, artifact off-disk), and says what would. |

Findings carry a severity:

- **`blocker`**: nothing may cite the claim until this is fixed.
- **`major`**: the claim must be narrowed or the missing evidence supplied.
- **`minor`**: worth fixing; it does not change the verdict.

`tools/sheriff.py check-case` enforces the vocabulary. It also refuses an
upheld verdict that has a failed or `not_covered` beat, a linked blocker, no
evidence on disk, or a canary that did not pass.

## Case layout

```text
research/sheriff/SHF-<YYYYMMDD>-<6hex>/     write-once
  sweep.json, sweep.md, sweep.svg           tools/sheriff.py sweep (deterministic)
  readers/<joint>.yaml                      one per independent reader (B9)
  scripts/                                  blind re-derivations, independent certificate checks
  findings.yaml                             composed verdicts (schema sheriff.case/v1)
  REPORT.md, report.typ, report.pdf         the report, with sweep.svg embedded
```

A second audit of the same target is a new case. Both stay.

## B0 Bind the case

- Fetch `origin/main` in every repository the target touches. Audit the
  published state unless the target is a branch or PR, and then audit its head.
  `sweep.json` records each repository's HEAD, branch, distance from
  `origin/main` and dirty paths. A dirty tree is audited only when the dirty
  state is itself the target.
- Never audit a result in the session that produced it. Independence is the
  point, as in `audit-runs`.
- Write down the target in one line, and the prior you hold before reading
  (what you expect to find broken, and why). The prior goes first in
  `REPORT.md`, so a reader can see whether the audit only confirmed it.

## B1 Claim inventory

Before checking anything, list **every claim in scope** in
`findings.yaml: claims`. A claim is any number, comparison, theorem, "verified",
"proved", "faster", "weak", "secure", "beats", "improves", or label of a result
class (advance, engineering, relabelling, accounting). Record it in the
producer's words with its location: `repo:path:line`, a PR number, or a ledger
id. Then list the artifacts it cites.

- A claim that cites nothing is already `unsupported`.
- Split compound claims. "Verified 3.2x end-to-end speedup over rho at n=83"
  is four claims: the answers were verified, the speedup is 3.2x, the
  comparison is end-to-end, and the baseline is a matched rho.
- Include claims made by omission. A table with no uncertainty column claims
  precision. A headline with no scope claims generality.

## B2 Execution proofs, STARKs and zk

Contracts: `docs/execution-proof-chain.md` and `docs/runbook-execution.md`.

1. **Does the claim say or imply proved execution?** Look for "execution
   verified", "proved", "STARK", "zk", "receipt", "verifiably computed" (sweep
   rule `zk.proof_language`). If it does, require a runbook `execution_proof`
   step whose units read `verified`, checked by a verifier pinned by sha256,
   with `dev_mode: false`, the pinned image id, the receipt's own digest, and a
   journal that binds the unit's raw-result bytes (`equals_artifact_sha256`).
   Re-run the pinned verifier on the receipt yourself when the tier is deep.
   Anything less makes the wording an overclaim.
   **As of 2026-10-16 every milestone of the execution-proof chain is open, so
   no result in these repositories is execution verified.** Replays, hashes,
   signatures and node-reported JSON are not execution proofs, and calling
   them that is a finding.
2. **What does the proof cover?** Check whether the guest computes the
   observations or only post-processes numbers the host supplied. Check whether
   host hints, external solver output and GPU returns are verified inside the
   guest. Check whether the guest enforces the operation count it reports. Check
   that every trial is covered, failed controls, misses, caps and zero-hit cells
   included. Check that seeds come from the prescribed derivation, so a
   contributor cannot pick favorable draws. A proof of post-processing proves
   post-processing.
3. **Does the verifier verify?** For any in-house prover or verifier (for
   example `crypto:src/zk/`), read the verify function line by line. It must
   check:
   - every constraint (boundary, transition, and composition against the trace
     at each query point);
   - the out-of-domain sample;
   - every FRI layer and the final polynomial's degree;
   - every Merkle path.
   The Fiat–Shamir transcript must absorb the statement, the public inputs and
   every commitment before each challenge (the "frozen heart" class). The
   low-degree extension must actually be applied. The security level must come
   from a stated formula, proven or conjectured, with the query count, blow-up,
   grinding and field size.

   A value the verifier reads and discards (`let _ = val;`, sweep rule
   `zk.discarded_value`) is a constraint it does not enforce.
4. **Mutation controls.** Each of these must be rejected:
   - one tampered trace value, re-committed;
   - a wrong public input;
   - a wrong AIR;
   - a valid proof of a different statement;
   - a truncated FRI;
   - a reordered or duplicated query.

   Write the controls if none exist (in the case's `scripts/`, never in the
   producer's tree). A verifier with no negative test (`zk.no_negative_test`) is
   unverified. One that accepts a mutant is `broken`.
5. **Trust assumptions stated**: the backend's security target (RISC Zero
   v3.0.6 is about 96-bit conjectured, never "128-bit"), recursion, any trusted
   setup (Groth16) and who ran it, and dev-mode settings (`RISC0_DEV_MODE`,
   `dev_mode: true` receipts, sweep rule `zk.dev_mode_receipt`).

## B3 Lean and formal proofs

Contracts:

- `docs/formal-research-lane.md` ("Verification contract");
- `crypto:AGENTS.md`, "Lean": no `sorry`, `admit`, `sorryAx`, custom axioms or
  native evaluation, and no arithmetic certificate passed off as the theorem;
- `cryptanalysis:AGENTS.md`, "Lean proofs";
- the method of `research/endosweep_lean_review_20261016/README.md`.

1. **Build from clean, pinned.**
   - Use the project's `lean-toolchain` and `lake-manifest.json`.
   - Run `lake exe cache get && lake build`, then the project's axiom audit
     (`lake env lean AxiomAudit.lean`, or `#print axioms` per theorem), then
     `lean4checker --fresh` where the project configures it.
   - The standalone `crypto:research/n83_*` files run `lean X.lean`, and the
     output is diffed against the committed `proof_check.log`.
   - cryptanalysis runs `tools/lean/proof-gate.sh` and
     `tools/lean/selftest/run.sh`.
   - crypto-autoresearcher runs `./formal/setup.sh`,
     `tools/rebuild_formal_root.py --workspace formal`, `lake build`, then
     `tools/verify_formal_targets.py`.
   - No Lean in the container makes the beat `not_covered`, with the setup
     command as the way to enable it.
2. **Holes and trusted-base escapes** (sweep rules `lean.*`, comment-, string-
   and name-literal-aware):
   - `sorry`, `admit` and custom `axiom` are blockers. `skipKernelTC` is a
     blocker too.
   - `native_decide`, `ofReduceBool`/`trustCompiler` and
     `implemented_by`/`extern` put the compiler in the trusted base; so does
     `unsafe`.
   - `#exit` hides everything after it.
   - Metaprogramming in a proof file can add or alter declarations, so a
     reader confirms it does not.
   - A text scan cannot see a `sorryAx` reached through an import; only the
     axiom audit can.
3. **Axioms of every cited theorem.** Run `#print axioms <name>` for each
   theorem a claim cites, not only the project-wide audit. The allowed set is
   `propext`, `Classical.choice` and `Quot.sound`.

   Coverage gaps to check:
   - crypto-autoresearcher's `#audit_project` audits only `CryptoResearch.*`.
   - A theorem in another namespace, or in a file outside the lake workspace
     (`lean.unpinned`, `research/*.lean`), is unaudited.
   - Several crypto projects have no audit at all (`lean.no_axiom_audit`).
4. **Statement fidelity**, which only a reader can check. It is the most
   important Lean check: a theorem that builds can still say something other
   than the claim. Apply the five endosweep checks:
   - **a, statement:** clause by clause against the claim, covering objects,
     quantifiers and the direction of the implication.
   - **b, hypotheses:** none hidden, and jointly satisfiable. Discharge them on
     a concrete witness, or the theorem may be vacuous.
   - **c, definitions:** every self-defined notion is the textbook one and
     matches the Python or Rust it stands for. Differential-test with `#eval`
     against the harness on random and edge inputs.
   - **d, data:** constants match the committed JSON.
   - **e, scope:** the README, paper or evidence record claims no more than
     the theorem proves.

   Usual traps:
   - truncated ℕ subtraction, `x / 0 = 0` and floor `Nat.sqrt`;
   - coercions between ℕ, ℤ and `ZMod n`;
   - `Finset.range n` off by one;
   - `<` against `≤`, and `∃` against `∀`;
   - `Fintype.card` of the wrong type;
   - a conclusion of `True` (`lean.vacuous`);
   - contradictory hypotheses;
   - a closed `decide` over a bound cited as the general theorem;
   - a toy-parameter theorem cited at cryptographic size.
5. **Proves-too-much control.** Change one digit of a constant, or drop a
   hypothesis, and the proof must fail (`neg_nist.lean`-style negative
   controls).
6. **Pinning.** The cited commit's Lean source states what the claim quotes,
   and receipts bind the source hash. A `machine_verified` receipt stays
   `semantic_review: pending` until the formal lane reviews it, and this screen
   does not substitute for that review.

## B4 Certificates and verified answers

Contracts:

- `docs/claims-and-verification.md`;
- `crypto:AGENTS.md` §2 ("a row without a verified answer is not a result")
  and §8;
- `cryptanalysis:AGENTS.md`, "Measurement rows and accounting".

1. **Re-verify solves independently.** Check `[k]P = Q` for every cited solve
   and a random sample of the rest. Use arithmetic you write, or a library that
   shares no code with the producer (PARI/GP, Sage, plain Python), and say
   which. Producer-side `verified: true` is a claim, not a check.
2. **Instance identity.** Check each of the following:
   - the curve coefficients;
   - the field, and the reduction polynomial for a binary field;
   - the point is on the curve;
   - the group order `r` is prime, by an independent test or a Pratt
     certificate;
   - the cofactor;
   - `[r]P = O`;
   - `Q` lies in `<P>`.

   Named curves must match the standard (`tools/curve_identity.py`,
   `crypto:scripts/curve_id.py`). Never infer identity from the field degree.
3. **Target independence.** The solver must never see `k`. Planted targets must
   come from a seed or derivation the solver cannot read; check its argv, env,
   logs and code path. The `k = planted` check belongs to the verifier, not the
   solver. A solve on a target the solver could derive is void.
4. **Relations, decompositions, rank.** Recheck relation sums, decompositions
   and linear-algebra rank independently (GF(2) rank, basis membership,
   Macaulay identities).
5. **Absence claims.** "No solution", "no decomposition" and "no weak curve"
   need a certificate (a refutation identity, or proved exhaustive coverage).
   Otherwise they are scoped to the bounded search: a timeout or a zero-hit
   count proves no absence.
6. A certificate checks a solution. It says nothing about the search
   procedure, operation count, distribution or rarity (B2).

## B5 Cost accounting and comparisons

Contracts:

- "Every improvement is a success" (in `AGENTS.md`, `crypto:AGENTS.md` §1–§6
  and §8);
- §5a, which prices unpriced native work at 0, 0.1 and 1 GAE;
- `docs/progress-fidelity.md`;
- `docs/bounds-and-frontiers.md`;
- `crypto:docs/bounds/README.md`.

1. **Class.** Is the change an advance, engineering, relabelling or accounting?
   Diff the pipeline against the baseline. If only the counting changed, it is
   not an improvement, whatever the table says.
2. **Baseline.**
   - It must be the current frozen index-calculus baseline for that curve and
     size, not a stale or weakened one.
   - Rho must solve the same target in the same counted unit. `S` is
     `total/√n`, and the gap to matched rho is reported as distance remaining.
3. **Unpriced work.** List every arm's unpriced counters and price them at 0,
   0.1 and 1 GAE (`ecbench band --weights 0,0.1,1 --ranks`). Two arms rank only
   where the order holds across the whole band.
4. **Phases.**
   - Every phase must be present: setup, factor base, relation collection,
     linear algebra, descent or recovery, and verification.
   - A missing phase makes the total unknown, not zero.
   - Amortization names the number of targets, and cold-start and amortized
     costs are reported separately.
5. **Scope.**
   - A stage diagnostic is not an end-to-end result.
   - Local speedups never multiply.
   - A toy result is not a general one.
   - An exponent needs at least 4 sizes with disjoint α intervals.
   - Wall time is never a bound.
6. **Machinery.**
   - `ecbench bound check` recomputes every `ECBND1h` seal, and
     `ecbench frontier build ... --check` and `ecbench challenge check` run on
     every record.
   - `ecbench claim check` fails closed without an independent receipt from a
     different host class, L2 isolation on both arms, and verified answers.
   - Every speedup has a `claims/*.json` that passes
     `python3 -m tools.progress_fidelity validate`. That validator checks
     declared paths as strings, so open the artifacts.
7. **Hardware.** An empty `gpu.devices` must be labelled CPU-only. Emulation
   must be distinguished from physical hardware. Isolation and the resource
   envelope must match on both arms.

## B6 Statistics, controls and preregistration

Contracts:

- core rules 2–8 of `AGENTS.md`;
- "A failed or non-estimable preregistered A/A or negative-control gate";
- `crypto:` `controlled-experiment` skill;
- `crypto:AGENTS.md` §10.

1. **Preregistration is provable from git.** The protocol or specification
   commit must be an ancestor of the first raw-output commit, and dated before
   it. A protocol edited after data arrived
   (`git log --follow -- <spec>`) is a finding. So is a specification carrying
   an outcome (`check_outcome_not_prewritten`), or one with no
   `decision_impact`.
2. **Stopping and exclusions.** Check that N equals the planned N. Look for
   interim peeks in journals and intermediate commits. Exclusion rules must be
   declared beforehand. Every failure, timeout and OOM row must still be
   present.
3. **Forking paths.** Count every sibling arm, variant, metric, seed batch,
   branch and session on the same question: ledger records, ecbench sessions,
   autolab tournaments. A headline that is the best of k is reported as best of
   k, with a correction for multiplicity, or disclosed.
4. **Controls.**
   - The A/A gate passed. If it failed, inference is withheld, with no post-hoc
     margin and no conditional follow-up.
   - The negative control comes from the right null population.
   - A positive control on the same code path shows the detector can see the
     effect.
   - Every arm uses the same instrument.
5. **Uncertainty.**
   - The design is paired, with matched seeds and targets.
   - The CI method is stated, for example the paired bootstrap.
   - A tier-1 speedup needs a 95% CI lower bound above 1.
   - The effect is compared against the frozen margin.
   - N is adequate, with a power check (`2/(N+1) < α/m` where it applies).
6. Recompute the headline statistic from the raw rows yourself (B9's blind
   re-derivation).

## B7 Provenance, integrity and reproducibility

Contracts: "Artifact policy" and "Durable research commits" in `AGENTS.md`,
`crypto:AGENTS.md` §12, and `cryptanalysis:AGENTS.md`, "Measurement rows and
accounting".

1. **Code binding.** The run manifest's commit must exist, and
   `code.dirty: false` must hold. Sources must be pinned
   (`tools/check_run_source_provenance.py`). A binary's hash must match a build
   from that commit, or say why it cannot.
2. **Immutability.**
   - Run directories are never modified after creation
     (`tools/check_run_immutability.py`, `git log --follow`).
   - A sealed ecbench session is never resealed in a later commit. Its seals are
     unkeyed hashes, so git history and an other-host replay are the only
     witnesses against a full reseal.
   - The fb-archive is append-only (`cryptanalysis:experiments/fb-archive/`).
3. **Archive receipts.** Recompute `path_sha256` (`tools/research_dispatch.py`
   archive verification). A content mismatch is fatal.
4. **Replay.**
   - `tools/runbook.py audit`: nonce-sampled, never with `--nonce`.
   - `ecbench verify --replay N`, on another host for independent receipts.
   - cryptanalysis `public-point-replay` and `independent-replay`.

   Replays bound fabrication; they are not proofs.
5. **Independence.** An independent receipt comes from a different host or
   environment class. A reviewer did not produce the result: compare session
   and model ids in the receipts.
6. **Citations.**
   - Provenance must be `recalled`, `retrieved`, `kb` or `internal`.
   - A `recalled` reference is never support.
   - A self-referential `proof_refs` is a defect (`docs/falsification-program.md`,
     D6).
   - A bus message is never evidence.
7. **Repository health.**
   - `tools/validate_ledger.py`, which is relative to its baseline;
   - `tools/check_merge_hygiene.py --absolute`;
   - `tools/runbook.py pending-audits`;
   - `cryptanalysis:experiments/fb-archive/fbarchive.py verify` and `refs.py
     check`.

## B8 Prose, papers and numbers

Contracts: "Papers" in each repository's `AGENTS.md` (every number cites a
committed artifact, and a stage diagnostic is never a speedup), and the
`report-evidence` skill.

1. **Every number traces.**
   - The sweep lists each number in each paper that appears in none of the
     artifacts the paper cites, whether exactly, truncated or rounded
     (`paper.untraced_number`). A paper that cites no artifact at all is
     `paper.no_cited_artifacts`.
   - A reader traces each one, or records it as `unsupported`.
   - Do the same by hand for README tables, `benchmarks/README.md` rows and PR
     bodies.
   - Regenerate each figure from its data script and compare.
2. **Words against tier.** `prose.strong_claim` leads list "proves", "verified",
   "beats rho", "breakthrough", "secure", "weak curve", "speedup" and the like.
   Each one either has the artifact that earns it or is an overclaim.

   Watch for ambiguity: "verified execution" in an ecbench report means a
   verified answer, not an execution proof. Check caveat loss (D7): a limitation
   in the evidence record must not be missing from the abstract.
3. **Build.** `make -C papers/<paper> check` must pass. The committed PDF must
   be newer than the last change to any number or figure it cites; compare the
   commit dates. The paper README names its novelty audit and the measurements
   still owed.
4. **Derived views regenerate.** Leaderboards, dashboards and frontier tables
   pass their `--check` builders, for example
   `crypto:scripts/build_ic_leaderboard.py --check` and `ecbench frontier build
   ... --check`.

## B9 Independent readers

Follow "Review architecture" in `AGENTS.md`:

- Record the prior first.
- Give each load-bearing joint to exactly one reader, with a worked attack
  plan.
- Declare blindness, and lift it only deliberately.
- Run a proves-too-much control on an object whose conclusion is known false.
- Do a blind re-derivation of each load-bearing quantity, from the statement
  and parameters alone. Replicating from the producer's artifacts is not one.

| joint | reader |
| --- | --- |
| B4 certificates, B6 controls and statistics, B7 receipts and replays | `validator` |
| B5 interpretation, cost model, cheapest falsification | `red-team` |
| B3 statement fidelity (one reader per Lean project cited) | `validator`, given the B3 checklist (`formal` for proof work) |
| B2 verifier soundness and mutation controls | `validator`, given the B2 checklist |
| Any `review-breakthrough` claim (a break or speedup on a real curve, a goal closure, a contradiction of validated evidence) | `validator-breakthrough` and `red-team-breakthrough` at `max`, never degraded |

Each reader writes `readers/<joint>.yaml`, containing `joint`, `reader`
(role and model), `sources_read`, `blind_from`, `checks` (each with its
command, output path and result), `findings` and `suggested_verdicts`.
Readers report; the session composes. A reader that produced the result
refuses.

## B10 Verdict, report and hand-off

`findings.yaml`:

```yaml
sheriff_case:
  schema: sheriff.case/v1
  id: SHF-20261016-abc123
  target: cryptanalysis:papers/x            # illustrative values throughout
  prior: "expect untraced table numbers; no Lean"
  readers:
    - {role: validator, model: <id>, joint: B4+B6+B7, report: readers/receipts.yaml}
  claims:
    - id: C1
      text: "3.2x end-to-end improvement over the frozen IC baseline at n=83"
      location: cryptanalysis:papers/x/main.tex:212
      verdict: upheld_scoped
      scoped_to: "3.2x cold online S at n=83 on one host class; no other-host replay"
      beats: {B4: pass, B5: pass, B6: pass, B7: not_covered, B8: pass}
      evidence: [cryptanalysis:experiments/.../summary.json]
      findings: [F2]
  findings:
    - id: F2
      beat: B7
      severity: major
      claim_ids: [C1]
      what: "independent receipt is from the same env_class_id"
      evidence: [cryptanalysis:experiments/.../receipt.json]
      fix: "replay on a host of another class: ecbench verify --replay 24"
```

Then:

1. `python3 tools/sheriff.py check-case <case>` must pass.
2. Write `REPORT.md` and render `report.pdf` with `sweep.svg` embedded
   (`research-visuals`, "Rendering"), and read every page.
3. A recurring or blocking obstruction gets a `problems/` record ("Name the
   obstruction").
4. Commit only the case directory (and problem records) on the session's
   branch, then push and open a PR.
5. Write the session receipt.
6. The Coordinator decides what follows.

## What the deterministic sweep cannot see

The sweep is a lead generator and a floor, not the audit. Its known limits:

- **Lean:** the scan is textual. It cannot see holes reached through imports,
  and it does not build anything. The build and axiom checkers do, when Lean is
  installed (`--deep`).
- **zk:** the verifier scan reads Rust only and is heuristic. A verifier can
  discard a value in ways the regex does not match.
- **Numbers:** finding a number in a cited artifact is weak evidence, because
  short integers recur by coincidence. Not finding it is a strong lead. Units,
  percentages and derived ratios are not matched.
- **Strong words:** this is a lead list. It has no notion of who is speaking:
  quoting a paper's claim is not making it.
- **Checkers:** each inherits its own limits. For example `validate_ledger` is
  relative to a baseline of legacy errors.
- **Sparse checkouts:** a checker that reads a file left out of a sparse
  checkout fails for that reason alone, so the sweep annotates such a failure.
  Confirm it on a full checkout before reporting it.

The canary (`tools/sheriff.py canary`) is the sweep's positive control. It
plants each defect class above in a scratch repository, with look-alikes that
must not be flagged:

- a `sorry` in a comment or a string;
- a name literal ``` ``Lean.ofReduceBool ```;
- a `let _ = log(...)` call;
- a number that occurs only in an uncited file.

It fails on any miss or any false positive. A sweep records its canary, and
`check-case` refuses to uphold anything when the canary failed.

## When to call the sheriff

- Before a paper, a benchmark row, a `claims/*.json` or an "improvement" PR
  lands, so a claim never merges unaudited.
- Before `/review-evidence` on a claimed improvement, and always after any
  `review-breakthrough`-class claim.
- On a schedule over everything (`/loop 24h /sheriff all`, or a scheduled task
  that starts a fresh session with `/sheriff all`), with `--deep` where the
  toolchains are installed.
- Whenever someone asks whether a result is real.
