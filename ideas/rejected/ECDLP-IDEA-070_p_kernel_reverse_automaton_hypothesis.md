# ECDLP-IDEA-070 — p-kernel reverse automaton

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_merged`
- Evidence scale: `toy` recurrence analysis only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with ideas `006/011/027`
- Breakthrough claim: **none**; a finite automaton for an elliptic sequence is not an ECDLP break.

## Falsifiable hypothesis

Some public coordinate or elliptic-net observable `a_n` of `[n]P` has a minimal
base-`p` kernel of `N^(alpha+o(1))` states with `alpha<1/2` and a bounded-ambiguity reverse
transducer. From the observable at `Q=[x]P`, the transducer recovers the digits/state path
of `x`, or factor-base source states sufficient for calibration and target descent, with
complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation was a **small exact p-kernel plus reversible scalar transducer**.
Semantic review found this is the same hidden-shift/state-compression object as elliptic-
net annihilators (`006`), scalar-orbit refinement (`011`), and bounded-defect automata
(`027`). Automatic-sequence terminology does not remove the missing small-state and
orientation theorem.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N` and `Q=[x]P`.
2. The observable is computable from a point without knowing its scalar.
3. Its p-kernel is exact, target independent, and constructible without enumerating `N` terms.
4. Reverse ambiguity and accepting-state labels are bounded below square-root scale.
5. Automaton discovery, states, transitions, residual candidates, verification, and memory are charged.
6. No scalar-indexed training table, post-hoc state merge, or hidden orientation is permitted.
7. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`scalar_indexed_elliptic_observable | exact_p_kernel | small_DFAO | reversible_state_path | scalar_or_source_recovery`

Collision fingerprint: `elliptic_net_state_compression | scalar_orbit_quotient | finite_defect_automaton | missing_orientation`. It is not mechanism-new.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, the failed held-out recurrence/state-polynomial control.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, the exact one-transition recurrence with failed two-transition compression.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, which closes tested public feature decoders for factor-log state.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, the finite-state/solver compilation control for five-term membership.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H679`, the closest fixed-curve five-term advice/state lane.

## Closest primary literature

- Christol, Kamae, Mendes France, and Rauzy, [Suites algébriques, automates et substitutions](https://doi.org/10.24033/bsmf.1926), relates algebraic power series and automatic sequences but gives no elliptic scalar inverse.
- Derksen, [A Skolem–Mahler–Lech theorem in positive characteristic](https://doi.org/10.1007/s00222-006-0031-0), supplies automatic zero-set structure, not a small reversible ECDLP automaton.
- Stange, [Elliptic nets and elliptic curves](https://arxiv.org/abs/0710.1316), proves exact elliptic-net recurrences and makes the collision with idea `006` explicit.

No checked source proves sub-square-root state complexity or target-to-index inversion.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, the point-computable observable, digit convention, and automaton grammar.
2. Generate exhaustive tiny scalar sequences only for truth, not as advice.
3. Prove the exact p-kernel and construct the automaton from algebraic identities.
4. Label reverse transitions with point/source witnesses and verify all scalar paths.
5. Calibrate any factor-base state labels from verified relations.
6. Evaluate the observable on randomized `Q+[t]P`.
7. Reverse all compatible paths, subtract `t`, and retain every scalar candidate.
8. Verify candidates until `[x]P=Q` or exhaust the complete list.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let automaton construction/state exponent be `alpha`,
reverse branching exponent `rho_a`, evaluation exponent `kappa`, calibration exponent
`c`, and memory exponent `mu`. Then `lambda=max(alpha,rho_a,kappa,c,mu)`, including
transition labels and verification. For `N approximately p`, base-`p` has essentially one
digit; any apparent digit compression that stores `N` outgoing labels is charged as
`alpha=1`.

## Likely fatal obstruction

A generic prime-period elliptic observable can require `Omega(N)` states. Elliptic-net
recurrences predict values without locating the hidden shift, and reversing a periodic
automaton can leave `N` scalar paths. With `N` close to `p`, the digit expansion supplies
no deep recursion. A public accepting-state orientation is itself the DLP dictionary.

## Proof track

Prove a sub-square-root exact p-kernel constructed without enumeration, a bounded-ambiguity
reverse map, and full calibration/verification costs below rho.

## Disproof track

Prove minimal state count or reverse ambiguity `Omega(sqrt(N))`, show the state labels
encode the scalar dictionary, or reduce the object to the occupied elliptic-net/orbit lane.

## Positive and negative controls

- Positive automata control: an algebraic sequence with a known small p-kernel and reversible generator.
- Positive elliptic control: exhaustive tiny elliptic-net recurrence verification.
- Negative random-period control: matched random sequences of period `N`.
- Mechanism control: Berlekamp–Massey/elliptic-net prediction without hidden-shift recovery.
- Leakage control: forbid scalar-indexed transition tables and post-hoc state minimization on targets.

## Quantitative promotion and falsification gates

No active gate exists because this proposal is merged/rejected. A genuinely new successor
would require a proof that both state count and reverse ambiguity have upper 95% exponent
at most `0.20`, zero scalar misses, and full `lambda,mu<=0.45`. State or ambiguity lower
95% exponent at least `0.50`, or an orientation dictionary, falsifies it.

## Artifact plan

- Collision report: `ideas/artifacts/ECDLP-IDEA-070/ledger_collision.md`
- Possible state proof: `ideas/artifacts/ECDLP-IDEA-070/p_kernel_theorem.md`
- Verifier: `ideas/artifacts/ECDLP-IDEA-070/verify_automaton.py`
- Retain observables, kernel states, transitions, reverse paths, candidates, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected hypothesis is toy, heuristic, model-bound, and novelty-unverified. A short
recurrence or automaton is neither scalar inversion nor a breakthrough.

## Exactly one next executable action

1. If reopened, first prove in `ideas/artifacts/ECDLP-IDEA-070/p_kernel_theorem.md` a small exact kernel and reverse map not covered by ideas `006/011`; otherwise execute nothing.
