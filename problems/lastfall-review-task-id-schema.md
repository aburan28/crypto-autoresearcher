# LastFall review identities do not satisfy the repository independence checker

- **Status:** `open`
- **Kind:** access/tool limit and audit procedure gap
- **Affected work:** [frozen plan](../docs/reports/2026-10-31-lastfall-fidelity/review_plan.yaml), [checker output](../docs/reports/2026-10-31-lastfall-fidelity/independence_gate.txt), [PR #2824](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2824)
- **Next action owner:** Coordinator and independent reviewers
- **Last updated:** 2026-10-31

## Problem

The LastFall review's combined independence gate fails because its precommitted plan and three attestations use Conductor task IDs `T-1105`, `T-1106`, and `T-1107`, while `tools/check_review_independence.py` accepts only repository `TASK-*` IDs. This prevents a `validated_scoped` review verdict even though the three reports exist.

## Evidence and uncertainty

- **Observed:** The [retained checker run](../docs/reports/2026-10-31-lastfall-fidelity/independence_gate.txt) exits nonzero with seven identity-schema errors. The plan was pushed before reviewer work; all three reviewer reports and attestations were published under the declared Conductor identities.
- **Derived or proved:** The checker result is a procedural failure, not a counterexample to the conditional theorem. The original chronological record cannot truthfully be rewritten as if native `TASK-*` IDs had been assigned before review.
- **Suspected explanation:** The two task systems use incompatible identifiers. Whether a prospective additive mapping can satisfy the existing checker without weakening its precommitment rule is unknown.
- **Missing capability:** A schema-compatible prospective review plan and attestations, or a reviewed checker extension that binds Conductor IDs to immutable native task identities while preserving the original timing and blindness evidence.
- **What this evidence does not establish:** It neither proves reviewer independence under the repository gate nor shows that the reports' mathematical findings are false.

## What would unblock it

- [ ] Preserve the original frozen plan, attestations, commits, and failed checker output byte for byte.
- [ ] Run a prospective schema-compatible review round with native `TASK-*` IDs and an exact source/role binding, or land a reviewed additive identity mapping with a checker negative control for changed task owners.
- [ ] Pass `tools/check_review_independence.py` on the new exact record without discarding its original failure or lifting blind scope retroactively.

These conditions would establish the review procedure gate for the named LastFall claim. A fresh pinned Lean build and axiom audit remain separate requirements.

## Next discriminating step

- **Action or proof obligation:** Inspect the checker schema and the repository's native task creation path, then precommit a new plan or identity bridge before any new reviewer acts.
- **Inputs and controls:** Use the original plan, three attestations, checker failure, and a mutated-owner control. Keep source, Lean, and blind reviewers in separate declared scopes.
- **Execution limits and stop condition:** No experiment or heavyweight build is needed. Stop if the proposed mapping would relabel a prior role or erase the original failed gate.
- **Outcomes and next actions:** A valid prospective round can be composed after its independent reports; a rejected mapping leaves the current verdict inconclusive and calls for a fresh round.
- **Recheck trigger:** A native task plan or checker change with explicit negative controls.

## Resolution and history

- 2026-10-31: Opened from the seven-error independence check. Unresolved.
