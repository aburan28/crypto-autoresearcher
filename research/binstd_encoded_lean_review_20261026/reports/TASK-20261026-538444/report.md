# J1 review: exact BINSTD encoded theorem and verification workflow

**Task:** `TASK-20261026-538444`  
**Producer revision:** `6409590d9bf26201956095e87f36f25d346cba68`  
**Frozen review plan:** `cab536aaa7ddc70016acfaff741b5478b3261dc1`  
**Joint verdict:** **holds for J1's narrow encoded theorem and workflow attribution.** This is not a verdict on polynomial irreducibility or the full formal workspace gate.

## Freeze and method

I read my handoff, `inputs.json`, and the committed review plan before producer content. The reserved `reviewer-binstd-j1` claim had task ID `TASK-20261026-538444`, epoch 1, this worktree, and only this report directory as write scope. I created no second claim. The review plan in this worktree has the same SHA-256 as the object at `cab536a` (`10893fba438f1a133637167d72342184afec9a2d026a7b03ac6a2a0c83779353`), and that commit is an ancestor of this checkout.

All eight `inputs.json` files were read from the **Git tree at the producer revision**. Their SHA-256 and Git blob IDs match the frozen list; see `source-hashes.log`. Supplemental exact-revision source hashes are in `supplemental-source-hashes.log`. The direct Lean input in `/tmp` retained the frozen source SHA-256 before and after checks (`lean-inputs.log`, `lean-inputs-post-hashes.log`). I did not read the sibling review, blind statements, or any sibling messages. Source and method reads are enumerated in `review_attestation.yaml`.

## Machine evidence

| Check | Result | Raw evidence |
| --- | --- | --- |
| Pinned direct compile of `EncodedDivisors.lean` with Lean 4.35.0-rc1, `-j 1` | **passed**, exit 0; peak RSS 587,824 KiB | `direct-lean-retry.result.json`, `.stdout`, `.stderr`, `lean-version.log` |
| Exact elaborated types of all seven named theorems | **passed**; the combined theorem has exactly the eight conjuncts in `inputs.json` and target YAML | `AuditTypes.stdout`, `AuditTypes.result.json` |
| Seven `#print axioms` results | **passed**; six report only `propext`, and `archived_trial_counts` reports no axioms | `Audit.stdout`, `Audit.result.json` |
| Nearby false control `noSmallMonicDivisor 131073 = true := by decide` | **expected rejection**, exit 1; Lean says `decide` proved the proposition false | `FalseControl.stdout`, `FalseControl.result.json` |
| Source-guided enumeration of every candidate and reduction step | **passed** for the five exact masks; no fuel exhaustion | `source_guided_structural_check.py`, `source-guided-reduction-rows.json`, `source-guided-summary.json` |
| Full Mathlib/Lake workspace and target verifier | **not_verified** in this review; no heavy build launched while another owner's Lean work held the host slot | Workflow analysis below; archived receipt itself sets `full_lake_workspace_build: false` |

The first direct compile attempt used a 2 GiB **virtual address space** limit. Lean aborted before processing the file because it could not create a thread (exit 134, 16,492 KiB peak RSS). I retained `direct-lean.result.json` and logs. Retrying with one Lean worker thread and a 16 MiB thread stack succeeded; its observed resident memory, and those of the type, axiom, and negative-control runs, stayed below the 2 GiB task budget. The failed resource-limit attempt is not evidence against the theorem.

The source-guided replay is a second implementation of the *read source*, not the plan's blind re-derivation. It finds:

| Mask | Encoded degree | Monic candidates | Actual tests before `List.all` stops | Predicate | Maximum XOR reductions | Fuel exhaustion |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 131081 | 17 | 510 | 510 | true | 14 | 0 |
| 313 | 8 | 30 | 30 | true | 6 | 0 |
| 471 | 8 | 30 | 30 | true | 6 | 0 |
| 131073 | 17 | 510 available | 2 | false, first zero divisor 3 | 17 over full candidate set | 0 |
| 257 | 8 | 30 available | 2 | false, first zero divisor 3 | 8 over full candidate set | 0 |

For a positive mask of encoded degree `n`, `List.range (n / 2)` gives degrees 1 through `⌊n/2⌋`. For each degree `d`, `2^d + lower` with `0 ≤ lower < 2^d` lists every monic bitmask of that degree once. The counts are `2+4+⋯+256=510` at degree 17 and `2+4+8+16=30` at degree 8. The count function is a formula; it does not itself measure short-circuited execution. Because each positive theorem evaluates the entire `all` to `true`, every one of its listed candidates must have passed. For the negative controls, execution stops at mask 3 after candidate masks 2 and 3.

At each nonterminal XOR step the aligned divisor cancels the leading bit, so the encoded degree strictly decreases. Starting at degree `n`, there can be at most `n - degree(d) + 1 ≤ n` such steps before the remainder is zero or has degree below `d`. The source supplies `n + 1` fuel. The raw replay also confirms no exhaustion on any enumerated exact candidate. This reasoning covers the finite bitmask loop; it is not a Lean proof of polynomial remainder correctness.

## Fidelity and claim boundary

`EncodedDivisors.lean:23-38` defines natural-number XOR-and-shift reduction, the exhaustive lower-mask loop, and a separate count formula. Lines 43-87 prove the three positive Boolean equalities, counts, two zero-remainder witnesses, two negative Boolean equalities, and their combined theorem. The elaborated combined type matches `formal/targets/binstd-encoded-divisors.yaml:25-31` and the theorem type frozen in `inputs.json`. `research/binstd_end_to_end_20261026/evidence.json:16-17,143-147` names the same field mask, factor masks, and counts. The producer report consistently calls the Lean result an encoded certificate (`REPORT.md:50-63,115-118`).

`Factorization.lean:24-29` defines `factor1`, `factor8a`, and `factor8b` in `(ZMod 2)[X]` and proves their product is `X^17+1`. Their displayed coefficient exponents correspond arithmetically to masks 3, 313, and 471. The reviewed Lean source contains no function sending a natural-number mask to a polynomial, no theorem identifying `remFuel` with Euclidean polynomial remainder, and no theorem deriving polynomial irreducibility from the encoded Boolean predicate. The factorization file itself explicitly disclaims factor irreducibility and the Frobenius representation (`Factorization.lean:13-15`). The encoded theorem therefore supports its source-defined finite claim only. A Lean irreducibility or normal-basis claim remains **not_verified** by these artifacts.

## Workflow attribution

The archived control receipt binds the frozen source, archived evidence, and generator hashes; it reports direct compile exit 0 and seven allowed axiom lines (`lean-encoded-controls-validation.json:6-11,12-50`). The generator actually invokes `elan run leanprover/lean4:v4.35.0-rc1 lean` on the source and then on an appended axiom-query copy (`check_lean_controls.py:54-85`). It does **not** call Lake or the formal target verifier, and it records `full_lake_workspace_build: false` (`check_lean_controls.py:106-108`). The independent direct replay here confirms the named declaration and seven axiom results but does not turn that receipt into a workspace verification receipt. The receipt is a consistency record; it is not, by itself, execution authentication.

At the frozen revision, the intended full gate is separate. `.github/scripts/ci_scope.py:69-82` marks changes under `formal/` as workspace inputs. `.github/workflows/lean-verification.yml:139-256` restores Mathlib, runs `lake build`, and invokes `tools/verify_formal_targets.py`. That script loads the exact target spec and dispatches `formal verify` for a present theorem file (`tools/verify_formal_targets.py:99-136`). The CLI checks toolchain and manifest pins, snapshots local source and verifier files, and invokes `LeanWorker` (`orchestration/formal/cli.py:206-293`). The worker builds the root and named module, scans forbidden constructs, runs project `AxiomAudit.lean`, and audits the requested name as a theorem with only standard axioms (`orchestration/formal/lean_worker.py:121-201`). Root regeneration imports the module (`orchestration/formal/workspace.py:30-66`). This is a static workflow trace. I did not run that full gate and did not inspect any hosted job result, so its status for the producer revision remains **not_verified**.

## Separated findings

| Subject | Machine status | Semantic fidelity | Review outcome |
| --- | --- | --- | --- |
| Exact combined **encoded Boolean** theorem, frozen standalone source | **passed** by pinned direct Lean; seven axiom outputs checked | **faithful_scoped** to source-defined masks, loop, and target claim | J1 **holds**; whole-certificate outcome remains **inconclusive** until the full gate and blind reviewer are reconciled |
| Archived direct control receipt | **passed** on independent direct replay of its source and axiom outputs | **faithful_scoped** to a direct Init-based module check | **validated_scoped** as a direct-check record only |
| Full formal target/workspace gate | **not_verified** in this lane | Target routing and verifier code reviewed statically | **inconclusive** |
| Polynomial irreducibility or Frobenius/normal-basis identification | **not_verified** by this theorem | **partial**: matching displayed masks, missing checked bridges | **inconclusive**; no such theorem should be inferred |

There is no counterexample to the **stated encoded theorem** in this review. The remaining actions are to run the frozen full workspace gate when the host slot is free, reconcile the separate blind finite-arithmetic review, and supply explicit Lean bridges before promoting the encoded result to an irreducibility or Frobenius claim. These are Coordinator decisions; this lane changes no official status.
