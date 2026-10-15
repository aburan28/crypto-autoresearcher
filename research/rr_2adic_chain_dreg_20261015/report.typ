#set page(paper: "a4", margin: 1.8cm)
#set text(size: 9.5pt)
#set par(justify: true)
#show heading: set block(above: 1.1em, below: 0.6em)

= Solving degree vs chain depth $k$: six-point Riemann–Roch decompositions over a 2-adic chain factor base

2026-10-15 (UTC) · study `research/rr_2adic_chain_dreg_20261015/` · experiment log (observations; no hypothesis status changed). Labels: *measured*, *derived*, *literature*, *inference*. Full log: `REPORT.md`.

== Question
P-224 has $p-1 = 2^96 (2^128-1)$, P-192 has $p+1 = 2^64 (2^128-1)$. A factor base $S$ with $|S| = 2^k$ x-values has a membership test that is a chain of $k$ squarings. A six-point relation is $f = A(x) + y C(x)$, $deg A <= 3$, $C$ monic quadratic, $f(-T)=0$ (5 unknowns), with all six roots of $q = (E C^2 - A^2)/(x - x_T)$ in $S$. An $N^(1\/3)$ ECDLP needs $|S| approx N^(1\/6)$ ($k approx 37$ for P-224) and each system decided in $approx N^(1\/6)\/720 approx 2^(27.8)$ operations. We measure how the Gröbner solving degree grows with $k$. *Literature:* Petit–Kosters–Messeng, PKC 2016 (doi 10.1007/978-3-662-49387-8_1) is the direct precedent.

== Setup
- *Arms:* `mult`, $p = 268496897$ ($2^12 | p-1$), $S = {X : X^(2^k) = c}$ (P-224 shape); `dickson`, $p = 268562431$ ($2^12 | p+1$), $S = {X : D_(2^k)(X) = c}$ with chain $x |-> x^2 - 2$ (P-192 shape, no auxiliary curve).
- *Encodings:* *direct*, 5 unknowns, equations are the coefficients of $"chain"^k(X) mod q - c$ (input degree 6 at $k=3$, 22 at $k=4$); *circuit*, $R_(i+1) = R_i^2 - Q_i q$ with remainder, quotient and $q$-coefficient variables, all equations of degree $<= 2$, $n = 11k - 19$ variables, $n+1$ equations.
- *Instances:* *planted* (positive control; witness checked against every equation) and *random* $T$ (expected relations $<< 1$).
- *Solver:* msolve 0.10.1, F4, grevlex, 1 thread; Xeon 2.1 GHz, 15 GiB. Metric: max F4 step degree (the solving degree when complete; a lower bound when stopped).
- *Phases:* 1 (05:18Z, $k = 3$–$4$, 3 seeds, 600 s, 3 jobs); 2 (06:35Z, circuit $k=4$, 1 job, 2400 s); 3 (08:29Z, circuit $k = 5$–$7$, mult planted seed 1, 1 job, 2400 s). Code: `build_systems.py` unchanged since commit 6dee0662f2; driver fd0db54170.

#figure(image("dmax_vs_k.svg", width: 100%),
  caption: [Left: max F4 degree vs $k$ for all 55 runs (filled = complete, open triangle = lower bound from timeout or OOM). Right: columns of the largest F4 matrix per degree, circuit/mult/planted seed 1 (k=3 phase 1, k=4 phase 2, k=5–7 phase 3). Run tags in `runs.csv`, `matrix_by_degree.csv`.])

== Results (measured)
#table(columns: 7, inset: 4pt, stroke: 0.4pt,
  [*k*], [*encoding*], [*n*], [*runs*], [*stop*], [*max F4 deg*], [*largest matrix*],
  [3], [circuit], [14], [12], [complete, ≤ 0.4 s], [*5*], [3748 × 3275],
  [3], [direct], [5], [12], [complete, ≈ 0.2 s], [*8*], [—],
  [4], [direct], [5], [12], [timeout 600 s], [≥ 24], [5652 × 49785],
  [4], [circuit], [25], [12 (ph. 1)], [OOM, 3 jobs], [≥ 7], [165551 × 195969],
  [4], [circuit], [25], [4 (ph. 2)], [OOM, 1 job, 13.6 GB], [≥ 7], [647230 × 655761],
  [5], [circuit], [36], [1], [OOM, 947 s], [≥ 6], [851697 × 1274254],
  [6], [circuit], [47], [1], [OOM, 636 s], [≥ 6], [2223917 × 4142298],
  [7], [circuit], [58], [1], [OOM, 333 s], [≥ 6 (step started)], [170233 × 363442],
)
*Controls (measured):* every complete planted run returned exactly 1 solution; every complete random run returned no solution over the closure (`[-1]`); every planted instance passed the witness assertion. Both arms behaved identically at $k=3$ and $k=4$.

== Derived
- The circuit encoding lowers the solving degree at $k=3$ from 8 to 5. At $k=4$ the direct input degree is 22, matching the earlier toy's "22". The circuit's input degree is 2, but its solving degree is $>= 7$.
- Degree-5 matrix width (columns): 3275, 39040, 144749, 253573, 363442 for $k = 3..7$.
- At P-224 size ($k = 37$, $n = 388$), the dense Macaulay width $binom(n+D, D)$ is $2^(36.1)$, $2^(42.2)$, $2^(48.0)$ for $D = 5, 6, 7$. Each exceeds the $approx 2^(27.8)$ per-system budget.

== Inference, limitations, next checks
*Inference:* no measurement shows the solving degree staying near 2–3, which the $N^(1\/6)$-per-relation target needs. The values (complete $D=5$ at $k=3$; $D >= 7$ at $k=4$) are consistent with growth in $k$. They do not establish a growth law, because no run with $k >= 4$ completed. *Limitations:* one solver and one order; a 15 GiB memory cap; only the $2^k$ part of $p plus.minus 1$; toy $p approx 2^28$; timeouts and OOM kills are operational facts, not refutations. *Next:* finish $k = 4, 5$ on a host with ≥ 64 GB; hybrid guessing of 1–2 unknowns; encodings with fewer variables (eliminate $Q_i$); a Petit–Kosters–Messeng Semaev-chain baseline with the same $S$.
