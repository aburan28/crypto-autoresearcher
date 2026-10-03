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

On the 77 instances of `instances.json`:

| family | hypotheses hold | hypotheses fail |
|---|---|---|
| random $V$ (R) | 32 of 32 | 0 |
| trace-zero $V$ (T) | 6 of 6 | 0 |
| polynomial $V$, odd $n$ (P) | 14 | 23: (G2) fails, giving a second linear equation |
| polynomial $V$, $n=40$ (S) | 1 | 1: (G1) fails, since $\dim\operatorname{span}(V\!\cdot\!V)=n-1$ for even $n$ |

Where the proposition does not apply, $1\notin W_2$ was computed directly. On
all 77 instances the column "$W_2$ refutes" in `summary.md` is 0, so
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
