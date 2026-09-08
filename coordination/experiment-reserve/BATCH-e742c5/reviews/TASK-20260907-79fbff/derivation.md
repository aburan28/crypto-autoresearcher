# Blind Tate-character and full-cost derivation

Task: `TASK-20260907-79fbff`  
Owned joint verdict: **PASS / holds**  
Claim epoch: `49fee8136e284f8672b53eb48a0d7889645b3549`  
Review-plan commit: `baefa00db9140147c9cbf11e239310bd299c37d3`

This is a blind derivation from the frozen statement. It is not an inspection
of an implementation, an experiment, a timing result, or a whole-package
verdict.

## 1. Algebraic conditions

Let

\[
K=\mathbb F_{p^k},\qquad k=\operatorname{ord}_r(p),\qquad
e=\frac{p^k-1}{r}.
\]

The specification requires prime \(r\ne p\), \(r\mid\#E(\mathbb F_p)\),
\(v_r(\#E(\mathbb F_p))=1\), a nonzero point \(G\), and \([r]G=O\).
Because \(r\) is prime, \(G\) has exact order \(r\). The definition of \(k\)
gives \(r\mid p^k-1\), so \(K\) contains \(\mu_r\).

For a divisor representative \(D_T\) of the class of \(T\) whose support is
disjoint from the divisor of the Miller function, define the reduced Tate
pairing

\[
t_r(P,T)=f_{r,P}(D_T)^e\in\mu_r.
\]

The second argument is a class in \(E(K)/rE(K)\). Therefore \(T\) may have
arbitrary order; projecting it to \(E[r]\) is neither part of this definition
nor required. A raw zero or pole is not a pairing output. It means the chosen
divisor presentation is invalid and must be shifted or the candidate rejected,
as the frozen statement requires.

Fix an accepted \(T\) and define

\[
\chi_T:\langle G\rangle\longrightarrow\mu_r,qquad
\chi_T(P)=t_r(P,T).
\]

Bilinearity in the first argument gives, for every integer \(a\),

\[
\chi_T([a]G)=t_r([a]G,T)=t_r(G,T)^a=\chi_T(G)^a.
\]

Set \(g=\chi_T(G)\). The acceptance checks are \(g^r=1\) and \(g\ne1\).
Because \(r\) is prime, these imply \(\operatorname{ord}(g)=r\). The kernel of
\(\chi_T\) is then a proper subgroup of the order-\(r\) group \(\langle
G\rangle\), hence is trivial. Thus \(\chi_T\) is injective and, since both
domain and image have order \(r\), is an isomorphism onto \(\mu_r\).

The nontriviality check is load-bearing. If \(g=1\), all identities
\(\chi([a]G)=\chi(G)^a\) and \(g^r=1\) still hold, but every input has the same
output and no decoder can recover \(a\). The frozen `g!=1` and null control
correctly reject this proves-too-much object.

The final exponent is also load-bearing. A non-reduced Miller value is an
element of \(K^*\) representing a class modulo \((K^*)^r\); it is not generally
an element of \(\mu_r\). Exponentiation by \(e\) maps it to an \(r\)-th root
of unity. In the calibration parameters, \(|K^*|=103^6-1=1194052296528\)
and \(e=62844857712\). An abstract generator of \(K^*\) has the full ambient
order before reduction, while its \(e\)-th power has exact order 19.

The [official Sage documentation](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_point.html#sage.schemes.elliptic_curves.ell_point.EllipticCurvePoint_finite_field.tate_pairing)
was retrieved on 2026-09-07. It directly confirms the API contract used here:
the first point has order \(n\), the second point may have any order, the output
is an \(n\)-th root of unity, and Sage applies the reduction exponent after the
PARI non-reduced computation. Galbraith's directly retrieved
[pairing lecture notes](https://www.math.auckland.ac.nz/~sgal018/chuo-uni.pdf)
state the same domain, bilinearity, reduction, non-alternation, and the \(k>1\)
rational self-pairing fact. The conclusions above do not rest on an unchecked
citation: their proofs are written out here.

## 2. Base-field isotropy

Suppose \(k>1\) and both pairing arguments are rational over \(\mathbb F_p\).
Then \(r\nmid p-1\). Write

\[
p^k-1=(p-1)S,\qquad S=1+p+\cdots+p^{k-1}.
\]

Since \(r\mid p^k-1\) and \(\gcd(r,p-1)=1\), we have \(r\mid S\), and hence

\[
e=\frac{p^k-1}{r}=(p-1)\frac{S}{r}.
\]

A valid Miller evaluation on rational divisors lies in \(\mathbb F_p^*\).
Every \(z\in\mathbb F_p^*\) satisfies \(z^{p-1}=1\), so \(z^e=1\). In
particular, the reduced Tate value for base-field \(T=G\) is trivial when
\(k>1\). This proves the registered isotropy control without using Weil-pairing
alternation.

When \(k=1\), \(r\mid p-1\) and \(e=(p-1)/r\), which is generally not a
multiple of \(p-1\). The same argument therefore gives no self-pairing
triviality. The Tate pairing is not necessarily alternating, so the frozen
instruction correctly avoids assuming \(t_r(G,G)=1\) in that case. The Weil
identity \(e_r(G,G)=1\) is separate and follows from Weil alternation.

## 3. Explicit BSGS decoder

Let \(m=\lceil\sqrt r\rceil\). For a target \(Q=[a]G\) with the canonical
label \(0\le a<r\), put \(h=\chi_T(Q)=g^a\).

### Multiplicative decoder

1. Reject unless \(g^r=1\) and \(g\ne1\).
2. Store the exact canonical field elements \(B_j=g^j\) for
   \(0\le j<m\), retaining their indices.
3. Set \(\gamma=g^{-m}\). For \(i=0,1,\ldots,m\), compare
   \(Y_i=h\gamma^i\) with the baby table.
4. On an exact collision \(Y_i=B_j\), set
   \(c=(im+j)\bmod r\). Check both \(g^c=h\) and \([c]G=Q\). Return \(c\)
   only when both checks pass.
5. Return no-solution when the declared giant range is exhausted.

Completeness is elementary. Euclidean division gives

\[
a=i_0m+j_0,\quad i_0=\lfloor a/m\rfloor,\quad 0\le j_0<m.
\]

Since \(m^2\ge r\), \(i_0\le m-1\). Therefore
\(h\gamma^{i_0}=g^{j_0}\), and the collision appears within the declared
range. Baby values are distinct because \(m<r\) for every registered
\(r\ge17\) and \(g\) has order \(r\). Canonical reduction plus both exact
checks handles any redundant collision in the extra \(i=m\) iteration.

The table contains exactly \(m\) elements. Repeated multiplication uses
\(m-1\) multiplications to form \(g^0,\ldots,g^{m-1}\), one further
multiplication to obtain \(g^m\), and one inversion to obtain \(\gamma\).
A valid target is found using at most \(m\) lookups and \(m-1\) giant
multiplications. The frozen full exhaustion cap is \(m+1\) lookups and \(m\)
giant multiplications. If exponentiation or inversion is delegated to an opaque
library, the actual operation count is unavailable unless instrumented; the
CPU/wall/RSS measurement remains reportable.

### Additive decoder

1. Store \(B_j=[j]G\) for \(0\le j<m\).
2. Set \(S=[m]G\). For \(i=0,1,\ldots,m\), compare
   \(Y_i=Q-[i]S\) with the baby table.
3. On \(Y_i=B_j\), set \(c=(im+j)\bmod r\), check \([c]G=Q\), and return
   only on success. Otherwise return no-solution after exhaustion.

The same division of \(a\) proves completeness. Repeated addition uses
\(m-1\) additions for the table and one further addition to obtain \(S\).
A valid target is found in at most \(m\) lookups and \(m-1\) giant
additions/subtractions; full exhaustion uses at most \(m+1\) lookups and \(m\)
giant additions/subtractions.

These are matched \(O(\sqrt r)\)-time and \(O(\sqrt r)\)-memory decoders. The
field decoder is not free merely because the pairing transfers the discrete
logarithm from the curve group.

Each target certificate must retain the public input manifest, canonical
\(h\), \(m\), the exact table size, collision indices \((i,j)\), the exact
field/group collision equality, canonical candidate \(c\), \(g^c=h\), and
the final curve equality \([c]G=Q\). A no-solution certificate records complete
exhaustion. Fixture certificates additionally establish the exact orders of
\(G\) and \(g\), field irreducibility, T-attempt history, divisor handling, and
the final exponent.

## 4. Fully charged costs

For a fixture, seed, and q-query cold batch, the registered primary costs are

\[
\begin{aligned}
T_{\rm char}(q)={}&C_{\rm shared}+C_{\rm field}+C_{\rm searchT}+C_{\chi G}
+C_{\rm BSGS,field\ table}\\
&+\sum_{j=1}^q(C_{\chi Q_j}+C_{\rm field\ giants,j}
+C_{\rm curve\ verify,j}),\\
T_{\rm curve}(q)={}&C_{\rm shared}+C_{\rm BSGS,curve\ table}\\
&+\sum_{j=1}^q(C_{\rm curve\ giants,j}+C_{\rm curve\ verify,j}),\\
R_q={}&T_{\rm curve}(q)/T_{\rm char}(q).
\end{aligned}
\]

`Cshared` is the full deterministic curve enumeration, point counts,
factorizations, bin assignment, generator search, and input validation divided
equally over the eight selected fixtures. The identical allocation belongs in
both primary totals. A secondary difference may cancel it explicitly, but the
primary ratio may not silently remove it.

`Cfield` includes the ordered irreducible-polynomial search, rejected
candidates, certificate work, and construction. `CsearchT` includes every
sample, square-root attempt, rejected divisor/pole case, and the pairing/final
exponent needed to reject candidates. If the accepted pairing evaluation is
reported separately as `CchiG`, it is excluded from `CsearchT` exactly once;
all other accepted-T selection work remains. Each query charges its Miller
evaluation and final exponent (`CchiQ`), its field BSGS giant work, and final
curve verification. The curve arm charges its own table and giant work and the
same final verification.

Query generation and verifier-only exhaustive tables are shared experimental
scaffolding. They are charged to the run budget and reported separately, but
are not solver inputs and do not belong asymmetrically in either primary arm.
Setup is charged once per declared q batch, not once per timing repetition. If
one setup is physically reused across seeds or q values, its allocation must be
declared so that per-seed ratios neither omit nor multiply it.

The proves-too-much arithmetic mutation used

\[
T_{\rm curve}=10+20+64(2+1)=222
\]

and

\[
T_{\rm char}=10+30+20+10+20+64(1+2+1)=346.
\]

The full ratio is \(222/346=0.6416184971\). Omitting field construction, T
search, \(\chi(G)\), and the field decoder table/giants reduces the denominator
to \(10+64(1+1)=138\), producing \(222/138=1.6086956522\). The omission turns
a non-crossover into a registered positive, so the full charge is logically
necessary.

## 5. Finite-panel quantifiers

Let

\[
B=\{8,10\},\quad Z=\{1,2,3\!:\!6,7\!:\!12\},\quad
S=\{606223,606227\}.
\]

Let \(V\) mean all eight \((b,z)\) fixtures exist, the mandatory calibration
and exact controls are valid, both seeds and required q workloads are present,
all seven alternating blocks are reported, and no mandatory primary timing is
below 0.1 CPU second after 100 repetitions.

The positive branch is exactly

\[
V\ \land\ \exists z\in Z\ \forall b\in B\ \forall s\in S:
R_{64}(b,z,s)\ge1.20.
\]

The same bin must witness all four inequalities. Favorable b=8 and b=10 cells
in different bins do not combine into a witness.

The negative branch is exactly

\[
V\ \land\ \forall b\in B\ \forall z\in Z\ \forall s\in S:
R_{64}(b,z,s)\le1.
\]

All other complete patterns are inconclusive for the registered 20-percent
hypothesis. A missing fixture, failed mandatory calibration, or unresolved
timing makes \(V\) false and forbids both complete-panel branches. An exact
control failure makes the affected experiment invalid. The q=1 workload is
reported separately and cannot replace q=64. Equality belongs to the indicated
closed boundary: 1.20 qualifies positive and 1 qualifies negative.

## 6. Bounded checks

One `python3 -` process ran 21 fixed arithmetic or mock cases, with no
repository inputs and no Sage/pairing/fixture/timing execution. All 21 passed.
The script measured 0.00008454208727926016 seconds wall and
0.00008400000000000074 seconds CPU. Because the cases ran sequentially inside
that aggregate, every case was below the 10-second cap. Peak RSS was not
measured; one worker was used under the 2 GiB handoff limit.

The cases and exact observed values were:

| Case | Exact observation |
|---|---|
| BSGS r=17,a=0 | m=5,i=0,j=0; both group equations hold |
| BSGS r=17,a=16 | m=5,i=3,j=1; both group equations hold |
| BSGS r=19,a=18 | m=5,i=3,j=3; both group equations hold |
| BSGS r=251,a=250 | m=16,i=15,j=10; both group equations hold |
| target outside generated subgroup | ambient C38, g exponent 2, h exponent 1; no collision |
| trivial character | all sampled identities pass; nontriviality is false; ambiguous required |
| leaked label | public keys omit `label`; dishonest manifest adds it |
| final exponent | ambient order 1194052296528; exponent 62844857712; reduced order 19 |
| k>1 base-field exponent | p=103,r=19,k=6; exponent mod 102 is 0 |
| k=1 non-implication | p=103,r=17,k=1; exponent 6 mod 102 is 6 |
| omitted-cost mutation | full R=0.6416184971; omitted-cost R=1.6086956522 |
| common-bin positive | branch positive |
| crossed-bin ratios | branch inconclusive |
| all ratios <=1 | branch negative |
| one ratio 1.01 amid <=1 | branch inconclusive |
| one selected cell missing | branch inconclusive |
| calibration failed | branch inconclusive |
| timing below resolution | branch inconclusive |
| exact control failed | branch invalid |
| q=1 prefix | first q=64 target equals the q=1 target |
| flipped character value | index 11 changed from exponent 1 to 2 and exact comparison failed |

No frozen fixture search, calibration, scientific control, timing panel,
experiment run, producer source, sibling report, commit, push, release, ledger
edit, queue edit, or status change was performed.

## 7. Narrow conclusion

The owned mathematical joint holds. Conditional on a defined reduced Tate
pairing and an accepted \(g=\chi(G)\ne1\), the frozen statement gives an
injective character on \(\langle G\rangle\), a complete explicit field BSGS
decoder with a matched additive baseline, and a fully charged finite-panel
decision rule. This review establishes no fact about the unseen implementation
and no empirical crossover, novel character, generic ECDLP improvement, or
launch readiness.

The Coordinator should reconcile this derivation and its certificate list with
the separately owned executable review, then archive the two declared artifacts
through `TASK-20260907-c52fd1`.
