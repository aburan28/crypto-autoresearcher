---
id: KN-LIT-63f33d
type: literature
title: "The Enormous Theorem, formalized (Axiom Math) -- agent-swarm Lean formalization of the Classification of Finite Simple Groups; lessons for the formal research lane"
authors:
  - "Axiom Math (core: Dean Cureton, Vasily Ilin, Bhavik Mehta, Niels Voss; ~30 further contributors; advisors Richard Lyons, Dan Nakano, Ron Solomon)"
year: 2026
venue: "Axiom Math research blog post; proof site cfsg.axiommath.ai; repository github.com/AxiomMath/CFSG"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://axiommath.ai/research/the-enormous-theorem-formalized/"
tags: [lean, mathlib, formalization, formal-verification, agent-swarm, ai-prover, statement-fidelity, conditional-results, certificates, proof-map, errata, cfsg, finite-simple-groups, group-theory, workflow]
confidence: reported
citation_verified: read
added: "2026-10-29"
superseded_by: null
---

## Contribution (as reported; nothing below was re-checked here)

A blog post reporting what it calls the first complete computer-checked proof
of the Classification of Finite Simple Groups (CFSG) in Lean on top of
Mathlib. The theorem says every finite simple group is cyclic of prime order,
alternating of degree at least 5, in one of 16 Lie-type families, or one of
the 26 sporadic groups. They formalized the first-generation proof, not the
second-generation one, which is still incomplete.

Figures from the post, read 2026-10-29 and not verified (we did not clone
or build `AxiomMath/CFSG`):

- About 43.1 million lines of Lean produced in 24 days. The Slack channel
  opened 2026-10-01 and the first agent swarm started 2026-10-02.
- About 1.2 million lines reused from the Qiuzhen-CFSG project, plus earlier
  Lean work listed in the repository's ThirdParty README.
- A "proof map" built from the literature split the work into 108 milestones
  and about 380 tasks. Dependency graph: https://cfsg.axiommath.ai/proof-map.
- Swarms of dozens of "AxiomProver" agents ran on a changing mix of models.
  Lead agents decomposed arguments and reviewed the statements being
  formalized. Worker agents searched for existing results or wrote proofs.
  Agents claimed milestones as GitHub issues, reported in Slack, and could
  hand prerequisites to other agents.
- Infrastructure shared cached build results across workers and ran
  independent checks in parallel. Expensive finite computations were moved
  into separately checkable certificates, which the post says made
  verification faster "by orders of magnitude".
- The post gives no Lean or Mathlib version and no compute or dollar cost.

## Mathematical by-products (reported)

- The post lists 34 places where the formalization deviated from the
  published record, mostly typos, table errors and dropped hypotheses. The
  list is at https://cfsg.axiommath.ai/errata.
- A quasithin lemma (Aschbacher-Smith) states an equality that fails for
  SL_2(5). The fix weakens it to an inequality and reorganizes the cases.
- Agents found counterexamples to a closure claim in Walter's 1986 memoir
  behind the Unbalanced Group Theorem. Example: in PSL_2(49), the field
  involution's centralizer is PGL_2(7), whose component PSL_2(7) is outside
  the claimed family. Working with Lyons and Solomon, they wrote a
  replacement proof using Solomon's 1976 maximal 2-components, including a
  new "Preservation of simple tops" theorem (Thm 2.3). Paper:
  https://hexagonmath.org/2610.00575?version=1. Its Remark 9.5 gives a
  shorter route that avoids Thm 2.3.

## Trust model they state

- Lean checks the deductions. People check that the top-level statement and
  definitions mean the intended classification.
- Lean will verify a result proved under an extra assumption. Reviewers
  therefore compared every proved statement with its target and checked
  that any added assumption follows from the original hypotheses. The
  formalization counts as complete only when no unjustified assumption is
  left.

## Relevance to this program

This is a report of method, not an ECDLP result, so it changes no lead and
no frontier row. It gives outside, very large-scale support for rules this
program already enforces, plus three practices we do not yet apply
systematically.

Already in our contract (`formal/README.md`,
`docs/formal-research-lane.md`):

- A Lean build is not a claim. An independent semantic-fidelity review must
  confirm the proposition matches the human claim and is not vacuous or
  weakened by hidden hypotheses. This matches their reviewers comparing
  each statement with its target.
- We reject `sorry`, `admit`, custom `axiom` and `unsafe`, and audit the
  exact theorem's axioms (`AxiomAudit.lean`).
- Our replay certificates follow the same pattern as their finite-computation
  certificates: the search is expensive, the check is cheap and independent.

Candidate adoptions. These are proposals and need a Coordinator decision:

1. **Hypothesis-delta check in fidelity review.** For every formal theorem
   offered as evidence, list each hypothesis the formal statement has that
   the human claim lacks, and give for each one either a proof that it
   follows from the claim's hypotheses or a scoping note. Their failure mode,
   conditional results that type-check, is exactly what an axiom audit
   cannot see.
2. **Proof map before formalizing.** Before work on a multi-lemma target
   starts, write down its dependency DAG of milestones. Their early
   milestones hid large unproved prerequisites, and they deleted tens of
   thousands of lines and split milestones into smaller pieces. This is
   cheap to copy as a `formal/targets/` field.
3. **Errata from formalization.** When a formalization attempt finds that a
   cited paper's lemma is false or missing a hypothesis, record it as a
   finding with its counterexample. Here that means a `KN-OPEN`, or a note
   superseding the relevant `KN-LIT`, so the defect is not lost when the
   attempt directory is abandoned. Their SL_2(5) and PSL_2(49) examples show
   that small explicit counterexamples are the usual output.

Limits:

- Everything above comes from one blog post by the team that did the work.
- Line counts measure machine-generated output, not difficulty, and are not
  comparable to Mathlib's hand-written lines.
- We have not checked the repository's axiom footprint, its top-level
  statement, or that it builds.
