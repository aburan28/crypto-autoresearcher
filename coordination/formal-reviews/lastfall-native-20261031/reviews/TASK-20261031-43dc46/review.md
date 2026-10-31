# Last fall degree: Lean machine and statement fidelity joint

Review task: `TASK-20261031-43dc46`. This report examines the pinned producer head `5c405f05539649cffb7f796ac586db65cdde1661`, the published handoff at `adb26ef1295b2d97d6b8328875670c866e602377`, and the named target `THM-FALLDEG-INVARIANTS1-THM-2-8`. No sibling review or historical T-1105/T-1106/T-1107 verdict was read while forming this result.

## Result

The source theorem's declared type faithfully states the target's **conditional identification of the last fall degree**. It quantifies over a field `k`, a polynomial-variable type `σ`, and a generating set `F`; assumes `(lastFallSet F).Nonempty` and an actual fall `∃ f ∈ Ideal.span F, f.totalDegree < degreeFall F f`; and concludes that `lastFallDegree F` is an attained greatest element of the fall-degree set. The arbitrary variable type is a harmless generalization of a finite variable set for this order-theoretic theorem. The proof uses the explicit finiteness assumption to ensure each ideal element enters some `V F d`, so `Nat.sInf` is applied only to nonempty degree sets where it matters.

Machine status is **pending** until the existing hosted exact-head run `41191503149` finishes its formal-workspace job and publishes the per-target audit receipt. The completed `kernel-controls` job validates the harness controls, not this declaration. No local Lean build was started: this host did not have the required 16 GiB free-memory reserve. The verdict for this joint is therefore **inconclusive pending the exact named-declaration and transitive axiom audit**, with statement fidelity assessed as `faithful_scoped` from source/type comparison. This is not a whole-claim or other-joint verdict.

## Bound inputs and interpretation

| Item | Binding |
| --- | --- |
| Handoff | `adb26ef1295b2d97d6b8328875670c866e602377:coordination/formal-reviews/lastfall-native-20261031/handoffs/TASK-20261031-43dc46.yaml`, SHA-256 `e0673e46e2d499d7a0d2b29f0303c2aa3de7283eb2c8d7a0411886e83d0ede64` |
| Lean source | `5c405f05539649cffb7f796ac586db65cdde1661:formal/CryptoResearch/FallDegree/LastFall.lean`, SHA-256 `1e7f005567847e46e4dc23a5649d29453a9d8b87b1a7fed1889f633c3d8b841b` |
| Target | `5c405f05539649cffb7f796ac586db65cdde1661:formal/targets/lastfall-is-max-degree-fall.yaml`, SHA-256 `de67d2e70c5da351f93f10505f6238450d4b7e9676c57e89c920fc4b354df085` |
| Named declaration | `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall` |
| Lean and dependency pins | `leanprover/lean4:v4.35.0-rc1`; Mathlib manifest revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a` |
| Hosted run | [Run 41191503149](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41191503149), exact head `5c405f05539649cffb7f796ac586db65cdde1661` |

The target's `V_{F,i}` is a smallest vector subspace closed under products fitting the degree budget. Lean defines it as `sInf` of submodules with those two properties. The predicate `f.totalDegree + g.totalDegree ≤ i` exactly guards multiplication even when `f.totalDegree > i`; a truncated natural subtraction would not. The source proves the defining inclusion and closure lemmas, then bounds `V F i` by polynomials of degree at most `i`, establishing `degreeFall F f ≥ f.totalDegree` for members.

The theorem's conclusion is `IsGreatest {d | ∃ f ∈ Ideal.span F, degreeFall F f = d ∧ f.totalDegree < d} (lastFallDegree F)`. This gives both attainment and the global upper bound. The proof first bounds every fall degree by `d_F`. Its nonempty, bounded fall set has a maximum in `ℕ`. It then shows every ideal member lies in the appropriate `V` at that maximum and invokes the minimum property of `d_F`. This matches both directions of the target claim. No premise equates a one-pass Macaulay matrix with `V`, and no finite profile is promoted to a global maximum by this declaration.

## False-case and boundary controls

**Remove `hfall`:** choose `F = ∅`. Then `Ideal.span F = {0}` and `V F i = {0}` for every `i`: the zero submodule satisfies both defining conditions and is the infimum. Thus `lastFallSet F = ℕ`, `lastFallDegree F = 0`, and `(lastFallSet F).Nonempty` holds. The set of fall degrees is empty because its only eligible ideal element is zero, `degreeFall F 0 = totalDegree 0 = 0`. Hence the conclusion `IsGreatest ∅ 0` is false. This is a mathematical countermodel to the nearby claim with the fall hypothesis removed; it was **not** run through Lean on this host. It shows `hfall` is a load-bearing premise and rules out a vacuous greatest-element proof.

**Empty-set `sInf` boundary:** `degreeFall` as a total definition is zero if an arbitrary nonideal polynomial never enters any `V F d`. The theorem only uses `degreeFall` on ideal elements, and `hfin` constructs an entry degree for every such element. The proof's `hne` records this fact before applying `Nat.sInf_mem`.

**Mathematical positive witness:** over a one-variable polynomial ring over any field, take `F = {x², x²+x}`. At degree 1 no generator is admitted, so `V F 1 = 0`. At degree 2 both generators are admitted and their difference gives `x ∈ V F 2`; hence `degreeFall F x = 2 > totalDegree x = 1`. Also `(F) = (x)`. For any nonzero `f = xq` of degree `m`, the polynomial degree law gives `m = 1 + deg q`, so closure from `x ∈ V F 2` puts `f` in `V F (max 2 m)`; zero belongs to every submodule. Thus `2 ∈ lastFallSet F`. This independently derives simultaneous satisfiability of `hfin` and `hfall` mathematically. It is not a Lean-checked witness in this review.

## Machine evidence and scope

At the recorded check, hosted run `41191503149` was `in_progress` on the exact producer head. Its `kernel-controls` job completed successfully, including real Lean setup and harness positive/negative tests. The `formal workspace (lake build + axiom audit)` job was still building; named target verification and receipt upload had not completed. The workflow's source has a `lake build` step followed by `python3 tools/verify_formal_targets.py --artifact-dir formal-receipts` and dependency-pin checks. That design would cover the target if the job completes and its receipt identifies the named declaration; the workflow text and generic controls alone do not establish that it did.

The statement comparison here is from committed source syntax and the target text. An elaborated-type printout, `#print axioms`, transitive audit result, and optional independent kernel recheck are not yet available in this review. The adjacent representation-degree declarations in the module were read to understand source context but were not assigned to this joint as separate claims.

## Obligations for closure

1. Reconcile run `41191503149` to a terminal status and retain its exact-head formal-workspace log and `formal-verification-receipts` artifact.
2. Confirm the target receipt names `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall`, records successful source/module coverage, and contains a passing transitive axiom audit with no unapproved axioms, holes, or native-evaluation bypass.
3. If the larger review requires machine-checked nonvacuity, formalize or verify the positive witness above. The present report supplies a mathematical derivation only.

No scientific ledger status is changed by this joint report.
