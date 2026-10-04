# Verification record

This file records which implementation checked each computational claim in
[`../theorem-dossier.md`](../theorem-dossier.md), and what it printed.

## Two implementations, no shared code

| step | implementation A (`code/`) | implementation B (`verify/indep_verify.py`) |
|---|---|---|
| field arithmetic | `gf2n.py` (Python), `s3count2.c` (C, PCLMUL) | separate Python `mulmod`, written independently |
| descended system | symbolic expansion of $S_3$ in `s3sys.s3_descent` | Möbius interpolation of $S_3$ evaluations at points of weight $\le2$, checked against direct evaluation at 200 random points |
| $S_3$ correctness | — | self-test: $S_3(x(P),x(Q),x(P+Q))=0$ on 10 random curve point pairs; nonzero on random triples |
| solution count | enumerate $X_1\in V$, solve the quadratic in $X_2$ (`s3count2.c`) | enumerate $s=X_1+X_2\in V$ with $\operatorname{Tr}s=\operatorname{Tr}\alpha$, use the half-trace form of Theorem 2.1, solve $X_1^2+sX_1=P$ |
| closure $W_D$ | M4RI dense echelon forms; degree-descending colex column order; chunked mutant products; skips products already in $M_D$ (`lfdclose2.c`) | Python integers; degree-ascending lexicographic order; incremental pivot dictionary; multiplies *every* low-degree pivot by every variable |

Two further checks were made:

- `lfdclose2.c` agrees with the unoptimized `lfdclose.c` (RREF, no skipping)
  on every instance where both were run.
- `s3count2.c` agrees with brute-force enumeration of $V\times V$ on 18
  even-$n$ instances ($n=8,10,12$). It also agrees with the Python counter on
  13 odd-$n$ instances, 4 of them satisfiable.

## The counterexample R35a, checked by implementation B

Instance R35a:
- $n=35$, $f=t^{35}+t^2+1$ (`800000005`), $a_2=0$, $a_6$=`2424e617c`, $z$=`573790dfc`;
- $V$ has a random basis of 18 elements, listed in `instances.json`.

```text
$ python3 indep_verify.py 35 800000005 0 2424e617c 573790dfc 4 1a6ea1c0e 1aa8b2310 1de85eb91 5a415c4c9 12ff7c0fd 41221b5a3 1d885bbad 2bea4256f 307ac5fee 62054fa82 4af2529cb ff7d5ec1 2fe339ecb 1d59a0626 615bf54e0 6cb4ac8b5 6e36b0754 6432ff219
selftest ok; xR on curve: True
descent ok: 361 monomials with nonzero K-coefficient; equations 35, vars 36
boolean solutions (ordered pairs): 0  [293.1s]
W4 dims [0, 1, 105, 3885, 61425] contains_one 0 rank 61425 cols 66712 [978.0s]
```

Implementation A reports the same instance as
`W4_dims 0 1 105 3885 61425 W4_one 0 iters 3 ncols 66712`. The dimensions of
$W_4\cap B_{\le d}$ agree exactly for every $d\le4$, and neither contains $1$.

**Upper bound, via Lemma 1.3.** Both restrictions $a_1=0$ and $a_1=1$
(variable index 0) are refuted at $W_4$ by both implementations:

```text
$ FIX=0=0 python3 indep_verify.py ... 4
restricted by {0: 0}: now 35 variables
W4 dims [1, 36, 631, 7176, 59057] contains_one 1 ...
$ FIX=0=1 python3 indep_verify.py ... 4
restricted by {0: 1}: now 35 variables
W4 dims [1, 36, 631, 7176, 59063] contains_one 1 ...
```

Implementation A prints `W4_dims 1 36 631 7176 59536 W4_one 1 iters 4` for
both branches. Both implementations stop as soon as $1$ appears, so the final
ranks differ; only the presence of $1$ matters. Hence $1\in W_5$ for R35a,
and its last fall degree is exactly 5.

**Positive control R33a** ($n=33$, random $V$). Implementation B reports 0
solutions and `W4 dims [1, 34, 595, 6579, 52484] contains_one 1`;
implementation A reports `W4_one 1 iters 4`.

## Every exact last fall degree with $n\le29$ (`verify/b_sweep.py`)

There are 61 instances in `instances.json` with $n\le29$, all with an exact
refutation degree $d\in\{3,4\}$. For each one, implementation B was run at
$D=d-1$ and $D=d$ and compared with implementation A. Four checks were made:
- the same Boolean solution count (0);
- $1\notin W_{d-1}$;
- the same dimensions of $W_{d-1}\cap B_{\le e}$ for every $e$ (both closures
  run to completion there);
- $1\in W_d$.

```text
$ python3 verify/b_sweep.py results/instances.json 29
R11a   n=11 d=3 B_count=0 B_W2=[0, 1, 22] A_W2=[0, 1, 22] B_one(W2)=0 B_one(W3)=1 AGREE
...
T29b   n=29 d=4 B_count=0 B_W3=[0, 0, 56, 1708] A_W3=[0, 0, 56, 1708] B_one(W3)=0 B_one(W4)=1 AGREE
done; disagreements: 0
```

All 61 agree. The full output is in [`b_sweep_n11-29.txt`](b_sweep_n11-29.txt).
Implementation B is pure Python, so it was not run on every larger instance.
Instances with $n\ge31$ that are not named in a section of this file were
computed by implementation A only.

## Lemma 2.3 and Observation 2.4 (`verify/falls_check.py`)

On R23a, R23b, R25a, R25b, R27a and R27b, each line prints:

```text
W3 contains 1: 0; dim(W3 cap B<=2) = 3n; explicit span dim = 3n;
falls in W3: True; r_j in M3: True; explicit span == W3 low part: True
```

The script also asserts the identity $S=z^2(w^2+w+\ell_0)$ of Theorem 2.1(a)
before doing anything else. For the polynomial basis (P23a), the explicit falls
are in $W_3$, but $\dim(W_3\cap B_{\le2})=114=5n-1>3n$: the extra falls are
specific to the polynomial basis.

## Satisfiable instance Q35a (Theorem 3.3), checked by implementation B

```text
$ python3 indep_verify.py 35 800000005 0 291215786 1a90965f6 4 <18 basis words of Q35a>
selftest ok; xR on curve: True
descent ok: 361 monomials with nonzero K-coefficient; equations 35, vars 36
boolean solutions (ordered pairs): 6  [288.0s]
W4 dims [0, 1, 105, 3885, 61425] contains_one 0 rank 61425 cols 66712 [1154.6s]
```

Implementation A agrees on the solution count (6) and on the closure,
`W4_dims 0 1 105 3885 61425`. So $\operatorname{codim}W_4=66712-61425=5287>6$,
and Proposition 1.4 applies.

## Agreement with this program's earlier engine

`EV-CERTBIN-091c56` was produced by the native backend of
`crypto_autoresearcher.gf2`, a third implementation. It reports this degree-4
Macaulay profile for the $m=2$ polynomial-basis system at $n=19$, $l=10$:

```text
dims_by_deg [0, 1-2, 110-112, 1246, 3711]
```

Here `dims_by_deg[d]` is the dimension of $M_4\cap B_{\le d}$.
`code/lfdclose2.c` gives exactly these values on the four P19 instances:
`[0,1,111,1246,3711]`, `[0,2,112,1246,3711]` (twice) and `[0,2,110,1246,3711]`.
That record used a different curve and different targets on the same field and
subspace, so the agreement is on the instance-independent part of the profile.

## Proposition 2.6 hypotheses (`verify/g1g2_check.py`)

On the 93 instances of `instances.json`:

| family | hypotheses hold | hypotheses fail |
|---|---|---|
| random $V$ (R) | 41 of 41 | 0 |
| random $V$, uniform $z$ (U) | 4 of 4 | 0 |
| trace-zero $V$ (T) | 6 of 6 | 0 |
| polynomial $V$, odd $n$ (P) | 15 | 25: (G2) fails, giving a second linear equation |
| polynomial $V$, $n=40$ (S) | 1 | 1: (G1) fails, since $\dim\operatorname{span}(V\!\cdot\!V)=n-1$ for even $n$ |

Where the proposition does not apply, $1\notin W_2$ was computed directly. On
all 93 instances the column "$W_2$ refutes" in `summary.md` is 0, so
$d_{\rm LFD}\ge3$ holds everywhere.

## The chained $m=t=3$ counterexample C19a (`verify/indep_verify_t3.py`)

Instance C19a:
- $n=19$, $f=t^{19}+t^5+t^2+t+1$ (`80027`), $a_2=1$, $a_6$=`1926`, $z$=`79a26`;
- $V=\langle$`e632 61ca0 32488 12079 5788e 589e 11c0a`$\rangle$;
- $N=n+3k=40$ variables and 38 equations of degree $\le3$.

```text
$ python3 indep_verify_t3.py 19 80027 1 1926 79a26 4 e632 61ca0 32488 12079 5788e 589e 11c0a
selftest ok
descent ok: equations 38, vars 40, max degree 3
boolean solutions: 0  [9.3s]
W4 dims [0, 2, 272, 7000, 92838] contains_one 0 rank 92838 cols 102091 [999.6s]
```

Implementation A (`code/gen3.py`, `code/s3c3count.c`, `code/lfdclose2.c`)
reports `W4_dims 0 2 272 7000 92838 W4_one 0 iters 8` and 0 solutions. Here is
how the two implementations differ:

- **Solution count.** Implementation B enumerates $(X_1,X_2)\in V^2$, solves
  for $u_1$, then for $X_3$. Implementation A enumerates $X_3$, then $u_1$,
  then $(X_1,X_2)$.
- **Validation of A.** `s3c3count.c` agrees with exhaustive enumeration over
  all $(u_1,X_1,X_2,X_3)$ on 12 instances with $n\le8$. `gen3.py` agrees with
  direct evaluation of both $S_3$ equations at 300 random points.

## Proposition 3.7, step (b) (`verify/check_prop37.py`)

The instance is `gen3.py 13 5 1 77 rand unsat c3tiny`: $n=13$, $k=5$,
random $V$, $t=3$, unsatisfiable, with 28 variables. For each of the $2^{10}$
assignments of the coordinates of $x_2$ and $x_3$, the script restricts the
system and runs `lfdclose2` at $D=1,2,3$:

```text
$ python3 ../verify/check_prop37.py c3tiny/c3_n13_k5_rand_77_0.sys 13 5
assignments 1024; max degree of restricted systems 2; least D with 1 in W_D: {2: 416, 1: 608}
```

Every restriction has degree $\le2$ and is refuted at $W_2$. The proposition
needs only $W_3$.

## Polynomial $V$ at $n=41,43,45$ (P41a, P43a, P45a)

Their degree-4 closures were run in a batch before these instances were added
to `tabulate.py`. To tie the batch to the table, `gen2.py` regenerated each
instance from its seed. All three files are byte-identical to the batch files
(`cmp`). The degree-4 outcomes were imported from the batch logs, with a
`provenance` field in `instances.json`, and `tabulate.py` computed $D=2,3$:

| instance | $W_2$ | $W_3$ | $W_4$ |
|---|---|---|---|
| P41a | $(0,2,122)$, no 1 | $(0,2,204,6328)$, no 1 | contains 1 (3 rounds) |
| P43a | $(0,2,128)$, no 1 | $(0,2,214,6980)$, no 1 | contains 1 (4 rounds) |
| P45a | $(0,1,90)$, no 1 | $(0,1,224,8465)$, no 1 | $(0,1,224,8950,166705)$, no 1 (3 rounds, 179447 columns) |

Implementation A's solution count is 0 for all three. On these instances,
$\dim W_3\cap B_{\le2}=5n-1$, the polynomial-basis count of Observation 2.4.
P45a's $W_4$ adds no further quadratic.
