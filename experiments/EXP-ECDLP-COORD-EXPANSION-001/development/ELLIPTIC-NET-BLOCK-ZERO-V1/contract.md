# Experiment Contract: Elliptic-Net Block Zero V1

## Hypothesis

For the exact complete-addition locator

`h_Q(A_i,R_1,R_2,R_3,R_4)`,

dyadic products over canonical four-`R` blocks,

`G_C(i)=product_{r in C} h_Q(A_i,r)`,

may admit a low-state recurrence along `A_i=P0+iD`. If the recurrence is
constructible from target-independent block advice and shared across targets,
it could locate a zero block without explicitly storing or scanning all
`Theta(B^4)` suffix tuples.

## Null Hypotheses

1. Root and internal block products have linear complexity comparable to
   matched random sequences at the observed length.
2. Any short recurrence is target-specific or fails on held-out shifts.
3. Exact elliptic-net recurrences visible in positive controls do not survive
   products of independent locator factors.
4. Exact witness descent works only after `Theta(B^4 L)` locator evaluation
   and `Theta(B^4 L)` block-state materialization.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: prime-order subgroups `q=953,3919,15583`;
- coordinate `R` families: random-x, source-PRF-x, x-interval,
  rational-union;
- `B=|R|` and canonical multisets
  `C={r_1<=r_2<=r_3<=r_4}`;
- sequence length: `L=8B`, explicitly diagnostic and longer than the attack
  factor-base progression;
- `A` variants:
  exact public progression `P0+iD` and matched deterministic hash-to-curve
  points;
- targets:
  one progression-planted target and one deterministic held-out target,
  shared by both `A` variants;
- locator field: `F_p`;
- exact point path: complete Renes-Costello-Batina projective additions, with
  affine replay and locator zero-set checks;
- block tree: deterministic balanced binary tree over lexicographically
  ordered canonical four-tuples.

## Metrics

- complete-addition calls and locator evaluations;
- canonical leaf count, materialized tree nodes, field elements, and bytes;
- root zero indices and exact witness descent;
- Berlekamp-Massey order and normalized order at every tree level;
- recurrence residuals on the full sequence and a train/held-out split;
- exact polynomial sharing and cross-recurrence residuals across siblings;
- root recurrence sharing across targets and `A` variants;
- best fitted Somos-4 residual;
- true elliptic-divisibility-sequence, planted linear-recurrence, random,
  and products-of-low-order-sequences controls;
- wall time and peak RSS.

## Positive Controls

- a division-polynomial elliptic divisibility sequence satisfies the Ward
  recurrence and its induced Somos-4 identity exactly;
- a deterministic planted linear recurrence is recovered at no greater than
  its planted order and predicts held-out terms exactly;
- every reported block zero descends to a canonical tuple whose exact
  complete-addition sum equals the target;
- every locator zero agrees with affine point equality.

## Negative Controls

- a deterministic random field sequence;
- a pointwise product of independently planted low-order recurrence
  sequences;
- deterministic random `A` points matched in length and target;
- held-out targets not used to choose the progression or factor base.

## Recurrence Signal Criterion

A family is promoted only if all three curves satisfy all of:

- planted progression root Berlekamp-Massey order at most `2B`;
- normalized root order at most 80 percent of its matched random-`A` root;
- zero held-out residual for the trained root recurrence;
- an exact root annihilator shared across both targets;
- at least half of nontrivial sibling pairs share an exact annihilator;
- exact Somos-4 residual on the progression root;
- zero semantic or witness-descent mismatch.

Passing this gate authorizes a constructive implicit-state successor. It does
not establish sub-rho relation generation.

## Algorithm Promotion Criterion

An attack candidate additionally requires:

- target-independent construction of all reusable node operators in fewer
  than `B^2.5` field elements and operations;
- expected root specialization plus exact witness descent near `B`;
- total advice, workspace, memory traffic, relation yield, rank, and target
  descent satisfying the existing charged exponent inequality below `1/2`;
- replication on random prime-field curves beyond the toy schedule.

The explicit tree in this experiment is diagnostic and cannot pass this
criterion.

## Falsification Criteria

- Any semantic mismatch falsifies the implementation.
- Root order growing as `Theta(L)` with no advantage over random `A` is a
  scoped negative for linear-recurrence compression.
- Target-specific annihilators are a scoped negative for fixed-curve advice.
- Exact leaf recurrence with high-complexity products narrows the route to a
  genuinely nonlinear shared operator.
- Explicit `B^3` or `B^4` node state is not an index-calculus improvement.

## Reproduction Command

```bash
python3 src/elliptic_net_block_zero.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --length-multiplier 8
```
