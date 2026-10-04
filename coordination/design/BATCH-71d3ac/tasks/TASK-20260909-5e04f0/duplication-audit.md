# Duplication and Pareto audit — `TASK-20260909-5e04f0`

## Scope of this audit

This record compares only the **draft's actual deliverable**: a finite symbolic
tree grammar with bounded window variables, threshold classification, and
synthetic controls.  It does not compare a cryptanalytic method because this
task defines none.

## Candidate relationship to the originating idea

`IDEA-20260808-486ae2` motivates a windowed-tree point-decomposition direction.
The draft preserves that provenance while narrowing the current work to a
pre-cryptanalytic accounting interface.  It has not selected a point model,
curve, factor base, equation system, lattice construction, root method, or
attack schedule.

## Nearby topics and evidence status

| Topic | Possible relationship | Evidence inspected in this task | Status |
| --- | --- | --- | --- |
| Semaev summation-polynomial methods | A later tree may seek to encode a relation system associated with this topic. | None. The topic is recalled only. | Unverified; no known/adaptation claim. |
| Jochemsz--May multivariate small-root analyses | A later bounded-variable design may seek a small-root analysis. | None. The topic is recalled only. | Unverified; no known/adaptation claim. |
| Existing repository ECDLP proposals | May contain overlapping tree, factor-base, relation, or cost ideas. | No repository-wide semantic comparison was performed by this task. | Inconclusive. |
| Generic symbolic tree evaluators | May already use equivalent bookkeeping. | No source or code comparison was performed. | Inconclusive. |

## Dominance and state-of-the-art status

`dominated_by: inconclusive`

No time, memory, data, query, success-probability, or asymptotic quantity is
defined by this draft.  Therefore no Pareto comparison against Pollard rho,
index-calculus methods, relation-generation approaches, or any other baseline
is meaningful.  The absence of a comparison is not evidence that the draft is
novel or competitive.

`sota_delta: not_applicable_to_the_current_symbolic_contract`

## Non-duplication requirement for any later promotion

A later Coordinator decision may not infer non-duplication from this document.
Before promoting an ECDLP-facing extension, it must retain:

1. a source-bound description of the exact extension and its claimed
   mathematical interface;
2. primary or otherwise admissible evidence for each claimed related method;
3. a repository-wide semantic comparison keyed to equations, variables,
   controls, cost quantities, and claimed scope;
4. an explicit `dominated_by` and quantitative `sota_delta` across every
   relevant time, memory, and data/query row; and
5. independent review of the comparison.

Until then, the only defensible status is that this draft is an unreviewed
symbolic accounting design with duplicate status **inconclusive**.
