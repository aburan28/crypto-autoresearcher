# Manuscript alignment audit (CTRL-HZM-MANUSCRIPT-ALIGNMENT)

Executed as `RUN-HZM-001-a`. Full machine-readable output:
`experiments/EXP-HZM-001/runs/RUN-HZM-001-a/raw-result.json`.

## Source

`Mahalanobis, "A Guess and Determine Attack on the Elliptic Curve Discrete
Logarithm Problem", arXiv:2607.09814v1 (2026)`, retrieved live via HTTPS
during this run (`https://arxiv.org/pdf/2607.09814v1` and
`https://arxiv.org/html/2607.09814v1`), cached at
`experiments/EXP-HZM-001/runs/RUN-HZM-001-a/sources/` with SHA-256 recorded
in `raw-result.json`. `alignment_source: primary_manuscript_retrieved`
(network access succeeded; the snapshot-quote fallback was not needed).

## Notation recap (manuscript's own Section 1.1 "Notations")

The manuscript fixes `l` (ell) as the row-dimension of the left-kernel
matrix `K` (size `l x 2l`), and states explicitly: "We also assume that `l`
is an even integer throughout this paper and `2*l' = l`." So `l'` (post-
halving reduced dimension) is HALF of `l` (pre-halving full kernel
dimension) — these are two distinct, non-interchangeable symbols in the
manuscript's own notation.

## Anchor 1 — displayed success law `q` (Section 8, Conclusion)

> "Now to the question of the probability of success of the algorithm. At
> the end, the probability estimate is roughly"
>
> `1 - (1 - 1/p)^C(l'+d, d)`

Exact LaTeX source (from the arXiv HTML rendering, unambiguous on `l` vs
`l'`): `1-\left(1-\dfrac{1}{\mathtt{p}}\right)^{\binom{\ell^{\prime}+\mathtt{d}}{\mathtt{d}}}`.

**Base: `l'`** (post-halving reduced dimension). Consistent with Equation
(4) (`Lambda`, Section 6) and the Table 1 header, both of which also use
`C(l'+d, d)`.

## Anchor 2 — `H`, the hashtable/signature-count formula (Section 4.1)

> "...leading to the creation of the matrix A which is of size `(l'+d) x d`.
> Then the table A' is the hashtable and which is derived from A and has a
> maximum length of `C(l+d, d-1)`."

Exact LaTeX source of the second clause:
`\binom{\ell+\mathtt{d}}{\mathtt{d}-1}` — note the **unprimed** `\ell`,
confirmed directly from the arXiv HTML math markup (distinct from the
`\ell^{\prime}` used one clause earlier, in the same sentence, for matrix
A's row count).

**Base: `l`** (pre-halving full kernel dimension) `= 2*l'`.

## The mismatch

`specification.yaml`'s `preregistered_prediction.formula` pins:

```
M = binom(L+d, d)
H = binom(L+d, d-1) = M*d/(L+1)
```

i.e. it assumes `M` and `H` are the same manuscript quantity's two binomial
coefficients, sharing one base `L`. The algebraic identity
`binom(n,d)*d/(n-d+1) = binom(n,d-1)` (verified symbolically in
`raw-result.json.finding.identity_holds_when_bases_match: true`) is correct
**only when `M` and `H` share the base `n = L+d`**.

The manuscript's own displayed equations do not share a base:

- `M`/`q` (Anchors 1 and the Eq.-4/Table-1 cross-reference): base `l'`.
- `H` (Anchor 2, two sentences later in the *same* subsection 4.1): base
  `l = 2*l'`.

So the manuscript's own `H` is `C(2*l'+d, d-1)`, not `C(l'+d, d-1)` as the
specification's `H = M*d/(L+1)` identity requires if `L` is read as `l'`
(the value that makes `M` match the manuscript). This is a genuine,
primary-source-verified instance of exactly the concern raised in the
independent red-team review `RT-20260723-303`, objection `RT303-O3`
("no theorem, equation, page, or pseudocode anchors showing that q, M, and
H refer to the same outer restriction, defect choice, and stopping rule"),
which was raised against the *snapshot quote* before the manuscript itself
had been directly re-checked. This audit re-checks the manuscript directly
and confirms the same base-mismatch concern is real, not merely a snapshot-
transcription artifact.

## Stopping rule applied

`CTRL-HZM-MANUSCRIPT-ALIGNMENT`'s `pass_condition` ("q, M, and H are mapped
to one outer trial, one defect choice, and one stopping rule") **FAILS**.

Per `specification.yaml` `stopping_rules[0]`: *"Stop the experiment as
inconclusive_misalignment if CTRL-HZM-MANUSCRIPT-ALIGNMENT fails; a toy run
is never opened on unaligned formulas."*

**`RUN-HZM-001-b`** (formal 9-config x 3-seed toy enumeration grid) and
**`RUN-HZM-001-c`** (formal brute-force control subset + primary-gate
charged-cost ledger) were therefore **never opened**. No run record exists
for them; this is the pre-registered protocol behavior for this branch, not
a missing or incomplete run.

## Worked-example control (`CTRL-HZM-WORKED-EXAMPLE`) — checked for
completeness, not decisive here

The manuscript's only numeric content is Table 1 (Section 6): tabulated
success-probability *estimates* for `log2(p) in {40,...,60}`,
`d in {5,...,14}`. It gives no explicit `p`, curve, matrix `K`, chosen
index sets, resulting signature matrix, or an actual recovered zero minor
/ scalar `m` for any single instance; Section 7 (Implementation) states
plainly "we do not have much data to share." **No fully parameterized
worked example exists in the pinned manuscript.** Per the control's own
`pass_condition`, this alone would force "classify the experiment
inconclusive (success cannot be claimed)" — but it is moot here because
`CTRL-HZM-MANUSCRIPT-ALIGNMENT`'s failure already stops the experiment
first, per the specification's own stage ordering (Stage 1 before Stage 2).

## Experiment-level classification

**`inconclusive_misalignment`**, per `RT-20260723-303` and
`specification.yaml`'s `falsification_criterion(a)`. This is neither a
gate-survival result nor a falsification (non-sub-rho) result: the
manuscript-alignment premise fails before any cost or count comparison is
meaningful, so no claim is made about whether the route survives or fails
the sub-rho gate. Per `AGENTS.md` scoping rules, this closes only the
question of whether the *specification's pinned formula pair* (as written)
corresponds one-to-one to the manuscript's displayed equations — it does
not evaluate, support, or refute the manuscript's underlying algorithm,
its success-probability claim in isolation, or its H formula in isolation.
