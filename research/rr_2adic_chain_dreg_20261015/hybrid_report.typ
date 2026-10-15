#set page(paper: "a4", margin: 1.8cm)
#set text(size: 9.5pt)
#set par(justify: true)
#show heading: set block(above: 1.1em, below: 0.6em)

= Hybrid guessing of 1–2 unknowns in the six-point Riemann–Roch / 2-adic chain system

2026-10-15 (UTC) · follow-up to `REPORT.md` / `report.pdf` · experiment log (observations; no hypothesis status changed). Full log: `HYBRID_REPORT.md`; table `hybrid_runs.csv`; data `data/hybrid1/`.

== Setup
Circuit encoding, `mult` arm ($p = 268496897$, $S = {X : X^(2^k) = c}$), seed 1. We fix $g$ of the five unknowns: $g = 1$ fixes $c_1$; $g = 2$ fixes $c_1, c_0$ (so $C(x)$ is fully known). Guessed variables are substituted out. Three branches per $(k, g)$: *planted/true* (the guess equals the planted witness; the consistent branch), *planted/wrong*, and *random/wrong* (random $T$). Solver: msolve 0.10.1 F4, grevlex, 1 job, 1800 s limit; 15 GiB host. Code at commit 8ceaf173b3; run started 20261015T1626Z. A cell that does not complete at some $k$ is skipped for larger $k$. The $g = 0$ rows are from the earlier sweep.

#figure(image("hybrid_dmax_vs_k.svg", width: 100%),
  caption: [Left: max F4 degree vs $k$ for $g = 0, 1, 2$ (filled = complete; open triangle = lower bound from timeout or OOM). Right: wall time per specialised system. Run tags in `hybrid_runs.csv`.])

== Results (measured)
#table(columns: 7, inset: 4pt, stroke: 0.4pt,
  [*k*], [*g*], [*n*], [*stop*], [*max F4 deg*], [*wall / system*], [*peak RSS*],
  [3], [0], [14], [complete], [*5*], [0.2–0.4 s], [13 MB],
  [3], [1], [13], [complete], [*4*], [0.2 s], [13 MB],
  [3], [2], [12], [complete], [*3*], [0.2 s], [13 MB],
  [4], [0], [25], [OOM], [≥ 7], [≈ 1530 s], [13.6 GB],
  [4], [1], [24], [complete], [*5*], [1683–1711 s], [2.2 GB],
  [4], [2], [23], [complete], [*4*], [10.2–10.6 s], [94 MB],
  [5], [0], [36], [OOM], [≥ 6], [947 s], [13.6 GB],
  [5], [1], [35], [timeout], [≥ 5], [1800 s], [2.5 GB],
  [5], [2], [34], [timeout], [≥ 5], [1800 s], [5.1 GB],
)
*Controls:* every complete planted/true system returned exactly 1 solution; every complete planted/wrong and random/wrong system returned no solution (`[-1]`). Within each $(k, g)$ the three branches have the same max F4 degree and wall times within 2%, so rejecting a wrong guess costs as much as solving the right one. At $k = 5$ the runs were inside a degree-5 F4 step when they stopped ($g = 2$: $267807 times 285940$; $g = 1$: $164866 times 246582$).

== Derived
- Solving degree with $g = 2$: 3, 4, $>= 5$ for $k = 3, 4, 5$. With $g = 1$: 4, 5, $>= 5$. With $g = 0$: 5, $>= 7$. Each guessed unknown lowers the degree by 1 at $k = 3, 4$.
- At $k = 4$ the second guess cut the wall time by a factor of about 165 (≈ 1700 s → 10.4 s).
- A guess is an element of $F_p$. Exhaustive guessing multiplies the number of systems by $p^g$ ($2^(224 g)$ for P-224), against a per-relation budget of $approx 2^(27.8)$. Equivalently, a specialised family has an expected $|S|^6 \/ (720 p) dot p^(-g) approx 2^(-9.5 - 224 g)$ relations at the $N^(1\/3)$ parameters.

== Inference, limitations, next checks
*Inference:* guessing lowers the degree by a constant per guessed unknown but does not stop its growth in $k$ (with $g = 2$: 3 → 4 → $>= 5$). Guessing over $F_p$ cannot pay for itself in the relation search, because each guess divides the expected relation count by $p$. The degree evidence rests on complete runs at $k <= 4$ and lower bounds at $k = 5$; it is consistent with growth in $k$ but not a law. *Limitations:* one seed and one arm; only the coefficients of $C$ were guessed; timeouts are operational facts; 15 GiB host. *Next:* guess the remainder or quotient variables of the last squaring steps; rerun $k = 5$, $g = 2$ with a longer limit; restrict guesses to structured subsets, which needs its own relation-count model.
