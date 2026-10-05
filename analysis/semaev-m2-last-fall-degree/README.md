# First and last fall degree of Semaev's descent systems over $\mathbb F_{2^n}$

**Status:** analysis directory. It contains pen-and-paper proofs and
computer-verified results on named instances. It promotes no ledger record and
closes no open problem; those are Coordinator decisions. Nothing here is a
cost claim about any ECDLP attack.

The main object is the Weil descent of Semaev's $S_3(x_1,x_2,z)=0$ with
$x_1,x_2$ in an $\mathbb F_2$-subspace $V\subset\mathbb F_{2^n}$ of dimension
$k=\lceil n/2\rceil$, together with field equations. This is Semaev's system
(5) for $m=t=2$ (ePrint 2015/310, §3). The chained system (5) for $m=t=3$ is
studied computationally: $S_3(u_1,x_1,x_2)=S_3(u_1,x_3,z)=0$, with $u_1$
free and $\dim V=\lceil n/3\rceil$. The statements and proofs are in
[`theorem-dossier.md`](theorem-dossier.md).

## Results

**Proved for all $n$ and all $V$:**

1. **Exact reformulation** (Thm 2.1). $S_3(X_1,X_2,z)=z^2(w^2+w+\ell_0\vartheta)$, where
   $w=X_1X_2/z+G(s^2)+G(a_6/z^2)$ and $G$ is an Artin–Schreier section such as the half-trace.
   - Hence $\operatorname{span}F=\{\operatorname{Tr}(\delta w):\operatorname{Tr}\delta=0\}+\mathbb F_2\ell_0$.
   - The affine-linear form $\ell_0=\operatorname{Tr}(S/z^2)$ always lies in the span of the equations.
2. **The first fall degree is 2 for every $n$** (Cor 2.2), under both the Caminata–Gorla and the Petit–Quisquater definitions.
   - The same holds for Semaev's whole chained system (5), for every $t\ge2$ (Cor 2.7). The last equation $S_3(u_{t-2},x_t,R_X)$ always yields the linear relation $\operatorname{Tr}(u_{t-2}+x_t)+\operatorname{Tr}(a_6/R_X^2)$. This contradicts the value 4 stated in the paper.
   - The degree-3 falls are explicit and independent of $n$ (Lemma 2.3): $\operatorname{Tr}(\lambda X_iw)$ for $\lambda\perp V$, plus $\operatorname{Tr}(sw)+\operatorname{Tr}(\alpha)\omega$.
   - The degree-3 identities $\omega a_j\equiv$ (quadratic) also hold.
   - On random subspaces these falls span the whole degree-$\le2$ part of $W_3$, of dimension exactly $3n$. This was checked on instances.
3. **General bounds on the last fall degree.**
   - Upper bound (Thm 2.5): every unsatisfiable instance is refuted inside the degree-$(k+2)$ Macaulay matrix, so $d_{\rm LFD}\le k+2$. For Semaev's whole chained system (5) with any $t\ge2$, the bound is $d_{\rm LFD}\le(t-1)k+t$ (Prop 3.7). That is $2k+3$ at $t=3$: each auxiliary element $u_j$ adds 1, not $n$.
   - Lower bound (Prop 2.6): $d_{\rm LFD}\ge3=d_{\rm ff}+1$ under two explicit, checkable genericity conditions. They hold on every random-subspace instance computed.
4. **Bridges** (Props 1.1, 1.2, 1.4; Lemma 1.3).
   - The Boolean closure $W_d$ equals the polynomial closure $V_{\tilde F,d}$ modulo field equations.
   - For unsatisfiable systems, the last fall degree equals the solving degree, which equals $\min\{d:1\in W_d\}$.
   - Every F4 run has $d_{F4}\ge d_{\rm LFD}$. The same holds for satisfiable systems whenever $\operatorname{codim}W_d>\#$solutions.
   - A branching lemma turns refutations of restricted systems into upper bounds.

**Computer-verified on named instances**
([`results/instances.json`](results/instances.json),
[`results/instances_t3.json`](results/instances_t3.json),
[`results/summary.md`](results/summary.md)):

| system | $n$ | $V$ (and $z$) | last fall degree $d_{\rm LFD}$ of the unsatisfiable instances |
|---|---|---|---|
| $m=t=2$ | 17, 19 | polynomial | **3** (10 of 10) |
| $m=t=2$ | 21 | polynomial | 3 (2 instances), 4 (2 instances) |
| $m=t=2$ | 23–35, 41, 43 | polynomial | **4** (25 of 25) |
| $m=t=2$ | 40, Semaev's cell | polynomial, uniform $z$ | **4** (2 of 2), matching his $d_{F4}=4$ |
| $m=t=2$ | 11, 13 | random | **3** (6 of 6) |
| $m=t=2$ | 15–33 | random | **4** (29 of 29; plus 2 of 2 with uniform $z$ at $n=33$) |
| $m=t=2$ | 33 | random $\subset\ker\operatorname{Tr}$ | **≥ 5** (2 of 2) |
| $m=t=2$ | 35 | random | **= 5** on R35a (via branching); **≥ 5** on 4 of 4, including 2 with uniform $z$ |
| $m=t=2$ | 35, satisfiable | random | **≥ 5** (2 of 2, by Prop 1.4: $\operatorname{codim}W_4=5287\gg$ #solutions) |
| $m=t=2$ | 37, 39 | random | **≥ 5** (4 of 4) |
| $m=t=2$ | 45 | polynomial (Semaev's default) | **≥ 5** (P45a, 1 of 1) |
| $m=t=3$ (chained, $u_1$ free) | 17 | random, polynomial | ≤ 4 (4 of 4) |
| $m=t=3$ (chained, $u_1$ free) | 19, 21 | polynomial | ≤ 4 (4 of 4) |
| $m=t=3$ (chained, $u_1$ free) | 19, 21 | random | **≥ 5** (4 of 4; C19a: $5\le d_{\rm LFD}\le17$) |

At $m=2$ the last fall degree rises $3\to4\to5$ along Semaev's diagonal
$k=\lceil n/2\rceil$, while the first fall degree stays at 2. At these
instances this settles the gap between the first fall degree and the solving
degree that `KN-OPEN-d218ec` and `KN-OPEN-3c8f51` leave open.

**Consequence: Semaev's Assumption 1 is false as stated** (Corollaries 3.4
and 3.6). The assumption says $d_{F4}\le4$ for every $2\le t\le m<n$,
$k=\lceil n/m\rceil$ and every $k$-dimensional subspace $V$. The explicit
counterexamples are:

- $(n,m,t,k)=(35,2,2,18)$, instance R35a;
- $(45,2,2,23)$, instance P45a. This uses Semaev's own default polynomial
  subspace $\langle1,t,\dots,t^{22}\rangle$, so the failure is not an artifact
  of choosing a random subspace;
- $(19,3,3,7)$, instance C19a, and $(21,3,3,7)$, instances C21a and C21b.
  This is the chained system with an auxiliary variable, inside the $n$-range
  of Semaev's own experimental tables.

Every F4 run on any of these instances reaches total degree at least 5. The
non-refutations of R35a and C19a were reproduced exactly by an implementation
that shares no code with the first. [`results/verification.md`](results/verification.md)
records which instances were reproduced that way.

**Consistency with the published data.** Semaev's cells use his default
polynomial subspace.
- Our polynomial-$V$ instances are refuted at degree 4 at $n=40$, in his
  $m=t=2$ cell with uniform $z$, and at $n=41$ and $n=43$.
- Our $m=t=3$ instances are refuted at degree 4 at $n=17$ for both
  subspaces, as in his tables. At $n=19$ and $n=21$, all four polynomial-$V$
  instances are refuted at degree 4, as in his Table 2. All four random-$V$
  instances are not refuted at degree 4.
- Kosters reported step degree 5 on a *satisfiable* $n=45$, $m=t=2$ system
  (KN-LIT-e77232). Our polynomial-$V$ instance at the same $n$, P45a, is
  *unsatisfiable* and also has $1\notin W_4$. That entry suggests, as its own
  inference, that solvable instances climb to 5 while unsolvable ones stop
  at 4. P45a is a counterexample to that reading at $n=45$. So is every
  random-$V$ counterexample here.

## What this does not show

- **Growth beyond the named instances.** That the last fall degree tends to
  infinity with $n$ is consistent with every computation here, and a
  semi-regular model gives roughly linear growth (dossier §4). It is not
  proved. The proved general bounds are $d_{\rm ff}=2$,
  $3\le d_{\rm LFD}$ (generic), $d_{\rm LFD}\le k+2$ at $t=2$, and
  $d_{\rm LFD}\le(t-1)k+t$ for system (5).
- **Polynomial subspaces.** Semaev's default polynomial subspace has $2n-1$
  extra degree-3 falls. At $m=2$ it is refuted at degree 4 up to $n=43$, and
  first fails at $n=45$. At $n\ge41$ only one instance per $n$ was computed,
  so this places the step near $n=45$ without showing that every instance
  beyond it needs degree 5.
- **The asymptotic regime.** Semaev's complexity uses $m\approx\sqrt{n/\ln n}$
  and states that it survives if the regularity degree is
  $o(\sqrt{n/\log n})$ (KN-LIT-e77232). The counterexamples falsify
  "$d_{F4}\le4$" at $m=2$ and $m=3$. They do not measure the growth rate in
  the regime $m\to\infty$.
- **ECDLP cost.** At $m=2$, root-finding costs $2^k$ and Pollard rho dominates.
  Nothing here changes the cost of any attack.

## Reproducing

All code is in [`code/`](code/) and [`verify/`](verify/). Build the M4RI
library (<https://github.com/malb/m4ri>), then:

```sh
cd code
gcc -O3 -march=native -mpclmul -msse4.1 -o s3count2 s3count2.c
gcc -O3 -march=native -mpclmul -msse4.1 -o s3c3count s3c3count.c
gcc -O3 -march=native -fopenmp -o lfdclose2 lfdclose2.c -I$M4RI/include -L$M4RI/lib -lm4ri -lm
python3 tabulate.py                # m = 2: regenerates every instance and closure outcome
                                   # (--maxN 40 skips the D = 4 closures at n >= 41, ~30 min each)
python3 restrict.py inst/rand_curve_13_n35/n35_l18_rand_curve_13_0.sys b0.sys 0=0 && ./lfdclose2 4 < b0.sys   # R35a, a_1 = 0
python3 restrict.py inst/rand_curve_13_n35/n35_l18_rand_curve_13_0.sys b1.sys 0=1 && ./lfdclose2 4 < b1.sys   # R35a, a_1 = 1
./run_t3_batch.sh rand 31 2 4 17:6 19:7    # m = t = 3 (then: python3 collect_t3.py)
python3 gen3.py 13 5 1 77 rand unsat c3tiny && python3 ../verify/check_prop37.py c3tiny/c3_n13_k5_rand_77_0.sys 13 5   # Prop 3.7(b)
```

The independent verifiers recompute everything from the curve parameters with
a different descent (Möbius interpolation of $S_3$ evaluations, checked against
direct evaluation), a different solution enumeration and a different closure
(Python integers, different monomial order):

```sh
cd verify
python3 indep_verify.py 35 800000005 0 2424e617c 573790dfc 4 <18 basis words>   # R35a: contains_one 0
FIX=0=0 NOCOUNT=1 python3 indep_verify.py ... 4                                  # R35a branch: contains_one 1
python3 indep_verify_t3.py 19 80027 1 1926 79a26 4 e632 61ca0 32488 12079 5788e 589e 11c0a   # C19a: contains_one 0
python3 falls_check.py <instance params>                                        # Lemma 2.3 / Observation 2.4
python3 g1g2_check.py ../results/instances.json                                 # Prop 2.6 hypotheses
```

[`results/verification.md`](results/verification.md) records which
implementation checked which claim, with its output.
