# Prime-field ECDLP adaptive quadratic-character tree — 2026-10-06

## Intake status

- Source type: user-directed external idea iteration.
- Scope: classical fixed-base ECDLP in prime-order subgroups of short-Weierstrass curves over prime fields.
- Exclusions: no Pollard-rho collision walk and no index-calculus relation collection.
- Evidence tier: deterministic toy experiment, external to this repository's contract and run-receipt system.
- Canonical status: none. This file allocates no IDEA, hypothesis, experiment, evidence, or decision identifier and changes no official research state.
- Bottom line: the decoder recovered every toy target exactly, but only after exhaustive fixed-base preprocessing and linear advice. Matched random field subsets had the same decision-tree depths, so the predeclared EC-specificity rule passed on 0/7 curves.
- Import rule: treat the measurements as a deduplication and null-model prior until reproduced under a frozen repository experiment and reviewed under the repository contract.

The originating implementation and JSON were produced in a separate local repository at commit `916c991`. They were not copied into this repository. Reported SHA-256 provenance locators are:

| Source artifact | SHA-256 |
|---|---|
| `landmark_tree_lab.py` | `497121630755e53b369b69199ef5d64e4f863194d015b04fa535663d8d88c928` |
| `tests/test_landmark_tree_lab.py` | `1d44f2e22c68a5c35e04ef236b556bd20742d65fedbe8d7a10ea2d80f16ee029` |
| `results/adaptive-landmark-tree.json` | `e4aed60fb9db2c850cb4e2c21408de4b6d9a6cbfb28720bdd0423f8837ec42e8` |
| `results/adaptive-landmark-tree-quick.json` | `631a755764b8781f197dc1a5234b3a585d9f5661f79ff436a1e67462dd1b07cd` |
| `research/notebook/2026-10-06-adaptive-landmark-tree.md` | `02996327fe4e0c2513fddc84e46490fa32b006b66d5bbfc2c4161b67342162f1` |

A hash is only a provenance locator here. It is not a repository run receipt and does not make the absent artifact independently reproducible.

## Mechanism

Fix a generator `P` of odd prime order `r`. Quotient the nonidentity orbit by sign and define

```
X_P = { x([k]P) : 1 <= k <= (r-1)/2 }.
```

For every public constant `c in F_p`, define a ternary predicate

```
f_c(x) = chi(x-c) in {-1, 0, +1},
```

where `chi` is the quadratic character. During preprocessing, greedily choose the predicate minimizing the largest child of the current set; break ties by the sum of squared child sizes and then by `c`. Recursing produces a ternary tree whose leaves contain scalar representatives.

For an online target `Q`, evaluate the predicates on `x(Q)` until a leaf identifies the pair `{k,-k}`. Compute `[k]P` once and compare it and its point negation with `Q` to resolve the sign.

The hypothesis was not merely that a tree can encode a supplied log table. It was:

> EC x-coordinate sets are unusually separable by this public predicate family, so their mean and worst query depth improve on matched random field subsets.

That would be a representation-specific effect. The null experiment tests exactly that claim.

## Charged resource model

The compact online phase is not counted in isolation. Preprocessing:

1. enumerates the complete fixed-base orbit;
2. supplies every scalar label used at a leaf;
3. evaluates all `|X_P| * p` character-table cells;
4. performs all greedy builder lookups;
5. stores a tree with `Theta(r)` labeled nodes.

Online work consists of the reported character-query depth, one fixed-base scalar multiplication per nonidentity target, point negation, and comparisons. Thus this construction is an exact fixed-group decoder with exhaustive setup and linear advice, not a sub-rho total-cost algorithm.

## Predeclared test and stop rule

For each of seven ordinary prime-order toy curves, build the same greedy tree for 12 independently sampled subsets of `F_p`, each containing exactly `|X_P|` distinct elements.

The EC-specificity rule passes only if the EC tree has both:

- lower mean depth than every matched random subset; and
- lower maximum depth than every matched random subset,

on at least five of seven curves. Otherwise retire the claimed EC-specific signal.

The source encoded this rule before the full seven-curve run. An initial test run exposed a mismatch between stored ternary symbols and online evaluation. That implementation defect was corrected before the full experiment; exhaustive recovery tests then covered both signs.

## Results

All 2,274 nonidentity targets were recovered exactly. The EC-specificity rule passed on 0/7 curves, versus 5/7 required.

| Curve | Order | Sign classes | EC mean depth | EC max | Random mean range | Random max range | Supports hypothesis |
|---|---:|---:|---:|---:|---:|---:|:---:|
| E101 | 83 | 41 | 4.243902 | 6 | 4.219512–4.268293 | 5–5 | no |
| E127 | 109 | 54 | 4.518519 | 5 | 4.518519–4.518519 | 5–5 | no |
| E149 | 139 | 69 | 4.884058 | 6 | 4.826087–4.942029 | 6–6 | no |
| E211 | 223 | 111 | 5.486486 | 6 | 5.486486–5.486486 | 6–6 | no |
| E283 | 281 | 140 | 5.778571 | 7 | 5.778571–5.792857 | 7–7 | no |
| E503 | 499 | 249 | 6.542169 | 8 | 6.526104–6.542169 | 8–8 | no |
| E907 | 947 | 473 | 7.486258 | 9 | 7.477801–7.492600 | 8–9 | no |

The checked test suite contained 10 passing tests in total, four for this experiment and six inherited baseline tests. This is external execution information, not a repository validation receipt.

## Interpretation and falsification boundary

The online tree is shallow and exact, but the measured property is not elliptic: uniformly random field subsets are just as separable by the shifted-character predicates. The most economical interpretation is a generic Paley-character/set-separation effect wrapped around a complete ECDLP codebook.

This experiment falsifies only the frozen claim that EC x-coordinate sets receive a query-depth advantage from the greedy family `chi(x-c)` at these toy sizes. It does not prove that every character family, adaptive predicate, or coordinate representation is useless. It does establish that future variants must not credit shallow online depth while hiding full-orbit construction or scalar-labeled leaves.

## Prior-art and repository screen

A targeted search found adjacent work but not this exact greedy tree:

- Henry Corrigan-Gibbs and Dmitry Kogan, [The Discrete-Logarithm Problem with Preprocessing](https://eprint.iacr.org/2017/1113), EUROCRYPT 2018, gives the generic preprocessing lower-bound framework. The reported relation is `S T^2 = Omega(epsilon N)` up to logarithmic factors.
- Lior Rotem and Gil Segev, [A Fully-Constructive Discrete-Logarithm Preprocessing Algorithm with an Optimal Time-Space Tradeoff](https://doi.org/10.4230/LIPIcs.ITC.2022.12), ITC 2022, gives a constructive generic preprocessing tradeoff. It reinforces that a fast online phase with group-specific advice is not itself an ECDLP advance.
- Yu Tsumura, [The number of points on an elliptic curve with square x-coordinates](https://arxiv.org/abs/0912.5501), studies the quadratic character of x-coordinates for a special prime-field family via a degree-two isogeny. It is not an adaptive log-recovery tree.
- Nigel Smart, [A note on the x-coordinate of points on an elliptic curve in characteristic two](https://research-information.bris.ac.uk/en/publications/a-note-on-the-x-coordinate-of-points-on-an-elliptic-curve-in-char/), studies an x-coordinate condition in characteristic two, not this prime-field predicate family.

Repository search found the existing generic preprocessing record `KR-RHO-ea34b8`, the public coordinate-predicate/hard-bit lane around `ECDLP-IDEA-045`, and broader structured-coordinate-predicate work. None was identified as a verbatim adaptive `chi(x-c)` log-table tree. Absence from a targeted search is not proof of novelty, and the matched-null failure removes any reason to promote a novelty claim.

This mechanism is distinct in operation from Pollard rho and index calculus, but its exhaustive fixed-base codebook places it squarely in the already charged preprocessing/advice regime.

## Intake disposition

- Preserve as a scoped negative and a deterministic control for coordinate-separating proposals.
- Do not allocate a new canonical idea ID on the strength of this packet.
- Do not describe the logarithmic-looking online depth as a total-cost improvement.
- Reproduce internally only if a later candidate needs this exact null control.
- A successor should be admitted only if it specifies how its tree, labels, and predicates are generated without a full orbit or linear advice, and predeclares a comparison with matched random subsets.
