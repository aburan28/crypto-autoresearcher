# PKM m=3 grid under an F4 solver (msolve): successor plan (DRAFT)

Status: **planned and blocked: `msolve` is not installed in the environment that drafted
this, so nothing can run yet.** Tracking PR. No Coordinator approval, no hypothesis change.

Follows DEC-20261015-a08389 (H-ECDLP-60de36 rejected_scoped: p <= 23 bits, m in {2,3}, Singular
std/slimgb + fglm). That decision's `next_actions` names this step; the problem note
`problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md` stays open.

## Question
Does the negative result (chain-encoded factor base no cheaper than dense and random-set
encodings of the same set) survive an F4 solver with regularity degrees reported?

## Needed before approval
- msolve available on the runner (`-t 1`), version recorded.
- A new experiment id and frozen specification (committed experiments are not edited; this
  links to EXP-ECDLP-f49f75).
- Same frozen toy grid, positive control, dense and random-set controls, paired design.
- Scope any verdict to the grid and solver; per the decision, no further P-256 work on this
  route until a solver beats the controls.
