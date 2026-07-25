# Labs

Six runnable, dependency-free Python labs (`python3 >= 3.10`, standard
library only). Each lab is the executable companion of one or more course
modules; each verifies itself with assertions before printing a demo, so a
clean run is also a proof that the mathematics in the modules does what it
claims on real numbers.

| Lab | Run | Companion module(s) | Builds |
| --- | --- | --- | --- |
| `lab01_arithmetic.py` | `python3 lab01_arithmetic.py` | 01, 04 | xgcd, inverses, CRT, Legendre, Tonelli–Shanks |
| `lab02_finite_fields.py` | `python3 lab02_finite_fields.py` | 05 | `Fp`, `Fp2` with Frobenius, norms, square roots |
| `lab03_elliptic_curves.py` | `python3 lab03_elliptic_curves.py` | 06, 07 | group law, scalar mult, counting, orders, twists |
| `lab04_ecdlp.py` | `python3 lab04_ecdlp.py` | 07 | brute force / BSGS / Pollard rho, √n scaling demo (~30 s) |
| `lab05_isogenies.py` | `python3 lab05_isogenies.py` | 09 | Vélu's formulas (deg 2 and odd), duals, verification |
| `lab06_ss_graph.py` | `python3 lab06_ss_graph.py` | 10, 11 | the supersingular 2-isogeny graph for p = 83, 431, 1013 |

Recommended order: 01 → 02 → 03 → 04 → 05 → 06 (later labs import
earlier ones — run them from this directory).

`lab06_ss_graph.py --export` regenerates
`../interactive/ssgraph_data.js`, the dataset behind the isogeny-graph
tab of the interactive playground (the playground also embeds a copy
inline so it works as a single file).

Every lab ends with `EXERCISE` comments: small modifications that turn
the demo into an experiment. Do them — the difference between reading
Vélu's formulas and watching your own implementation fail until the
representative set is right is the course.
