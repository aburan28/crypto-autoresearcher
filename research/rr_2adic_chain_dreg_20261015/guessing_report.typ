#set page(paper: "a4", margin: 1.7cm)
#set text(size: 9.3pt)
#set par(justify: true)
#show heading: set block(above: 1.0em, below: 0.55em)

= Guessing remainders and sign patterns in the six-point Riemann–Roch / 2-adic chain system

2026-10-15/16 (UTC) · follow-up to `REPORT.md` and `HYBRID_REPORT.md` · experiment log (observations; no hypothesis status changed). Full log: `GUESSING_REPORT.md`; table `guessing_runs.csv` (67 msolve runs, `mult` arm, $p = 268496897$, seed 1).

== Strategies
- *Remainder coefficients.* Fix $g$ coefficients of the last chain remainders $R_L = X^(2^(L+1)) mod q$. $g = 6$ fixes $R_L$; $g = 12$ fixes $R_L$ and $R_(L-1)$. The guess space is $p^g$.
- *One-level sign split.* On each root of $q$, $X^(2^(k-1)) = plus.minus s$ with $s^2 = c$. Guess $m = \#{+}$ (7 options). Then $q = q_+ q_-$, with $q_(plus.minus) | X^(2^(k-1)) minus.plus s$ and each factor checked by a depth-$(k-1)$ chain.
- *Two-level sign split.* $X^(2^(k-2))$ is one of the four fourth roots $y_j$ of $c$. Guess a composition $(m_0, ..., m_3)$ of 6 ($<= 84$ options; 68 at $k = 4$). The factors $f_j | X^(2^(k-2)) - y_j$ are nested inside the one-level split, so every equation stays quadratic.
Solver: msolve 0.10.1 F4, one job at a time, 1200–1800 s per system; 8.6 GB `ulimit` after the container restarts. Planted instances check a witness for the true guess.

#figure(image("guessing_compare.svg", width: 100%),
  caption: [Max F4 degree (left) and wall time (right) per specialised system, by strategy. Filled = complete; open triangle = stopped (timeout or memory), a lower bound. Includes the earlier no-guess and C-coefficient rows. Tags in `guessing_runs.csv`.])

== Results (measured): max F4 degree
#table(columns: 5, inset: 3.5pt, stroke: 0.4pt,
  [*strategy*], [*guess space*], [*k = 4*], [*k = 5*], [*k = 6*],
  [none], [—], [≥ 7 (memory)], [≥ 6 (memory)], [≥ 6 (memory)],
  [C coeffs $g = 1$ / $2$], [$p$ / $p^2$], [5 (≈1700 s) / 4 (≈10 s)], [≥ 5 / ≥ 5 (timeout)], [skipped],
  [remainder $g = 1$], [$p$], [5 (5–7 s)], [not run], [not run],
  [remainder $g = 2$], [$p^2$], [4 (0.2 s)], [≥ 5 (memory)], [skipped],
  [remainder $g = 6$], [$p^6$], [true 4, wrong 2], [true 4, wrong 3], [true 4, wrong 3],
  [remainder $g = 12$], [$p^12$], [n/a], [true 4, wrong 2], [true 4, wrong 2],
  [one-level split], [7], [true ≥ 7; wrong 5–≥ 7], [≥ 5 / ≥ 6 (memory)], [skipped],
  [two-level split], [≤ 84], [true *6* (1190 s); wrong 6–≥ 6], [all ≥ 6 (memory)], [skipped],
)
*Controls:* every complete correct-guess system returned 1 solution; every complete wrong-guess or random-$T$ system returned none. Planted and random instances cost the same for a given guess shape (e.g. two-level $(1,2,1,2)$ at $k = 4$: 1189.975 s vs 1189.979 s). At $k = 4$ the systems have 25 variables with no guess, 20–32 with a one-level split, 34–37 with a two-level split and 19 with remainder $g = 6$.

== Derived
- With a whole remainder guessed, the degree is flat at 4 for $k = 4, 5, 6$, because $q$ must divide the known degree-10 polynomial $R_L^2 - c$. The guess space is $p^6 = 2^1344$ at P-224 size, against a per-relation budget of $approx 2^(27.8)$. Each fixed coefficient also divides the expected relation count by $p$.
- Guessing 1–2 remainder coefficients behaves like guessing C coefficients (degree 5 or 4 at $k = 4$, no completion at $k = 5$), but is much faster at $k = 4$.
- Sign splits are cheap guesses but do not lower the degree. The one-level true branch stays at $>= 7$. The two-level true branch completes at 6 at $k = 4$ (unguessed: $>= 7$); at $k = 5$ every two-level system ran out of memory at degree 6. Over all 68 compositions, one $k = 4$ instance would cost an estimated $10^4$–$10^5$ s; this is extrapolated, not measured.

== Inference, limitations, next checks
*Inference:* on these systems, the guesses that flatten the solving degree have a guess space that is a power of $p$. Bounded sign-pattern guesses leave the degree at or near the unguessed values and hit the same memory wall at $k = 5$. None shows a bounded way to keep the degree near 2–3. The evidence is complete runs at $k <= 4$ ($k <= 6$ for whole-remainder guesses) and lower bounds elsewhere. *Limitations:* one seed and one arm; representative compositions only; time and memory caps; two container restarts interrupted two runs, which were discarded. *Next:* multi-level splits combined with remainder guesses on the small factors; a ≥ 64 GB host for $k = 5$ true branches; how the number of compositions and the per-system cost combine as the number of split levels approaches $k$, where it becomes exhaustive search.
