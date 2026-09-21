# Repaired producer-output generic bound

## 1. Scope and result

Let \(r\ge 5\) be prime, \(N=r-1\), and let
\[
D=\mathbb F_r^\*,\qquad \alpha\mathrel{\leftarrow}D,\qquad Q=\alpha G.
\]
Fix a declared divisor \(d\mid N\) with \(2\le d<N\). The producer receives only the ordinary input handles for \(G\) and \(Q\), and its target is
\[
f_d(\alpha)G=\alpha^dG.
\]
The producer must return an oracle-issued handle. It receives no handle for \(\alpha^dG\).

The repaired result is piecewise. For a producer with success probability \(s\), define the excess over the affine fixed-output root mass by
\[
\delta=s-\frac dN.
\]

For a producer capped at \(q_g\) generic operations, with \(P\) resident challenge-independent handle records including the public handle \(G\), put \(n=q_g+1\). Then
\[
s\le
\frac{\left|
 C_{\rm PO}\cup C_{\rm OO}\cup T_{\rm out}
\right|}{N}
\le
\min\!\left\{
1,\frac{Pn+\binom n2+d}{N}
\right\}.
\tag{1}
\]

Consequently, whenever \(\delta>0\),
\[
Pn+\binom n2\ge N\delta.
\tag{2}
\]
If \(s\) is bounded below by a positive constant and \(d/N\le s-c\) for a constant \(c>0\), fully charged single-instance producer work is \(\Omega(\sqrt N)\).

This does not give a uniform rho lower bound over every allowed \(d\). For \(d=N/2\), the producer returning \(G\) has correctness \(1/2\) and constant work. Thus the unconditional statement “constant producer correctness implies rho work” is refuted. The repaired theorem depends on constant excess correctness above \(d/N\), or in particular on \(d=o(N)\) and constant correctness.

This is an unverified theorem candidate with an exact obstruction to its uniform extension. It is not a novelty, first, SOTA, support, closure, or breakthrough claim.

## 2. Mandatory RT-215-C1 control

Consider the producer
\[
\mathcal P_0(G,Q): R\gets G.
\]
It performs no online group operation. Its only challenge-dependent handle is the supplied \(Q\); it creates no informative producer collision. Its output is correct exactly on
\[
\{\alpha\in D:\alpha^d=1\},
\]
which has cardinality \(\gcd(d,N)=d\), since \(d\mid N\).

Now give a separate verifier its own ordinary generic-group budget. The verifier deterministically recovers \(\alpha\), for example by exhaustive search or generic baby-step/giant-step, and accepts exactly when
\[
R=\alpha^dG.
\]
For \(R=G\), it therefore accepts exactly when \(\alpha^d=1\). The verifier is perfectly sound, but all handles, equalities, collisions, table accesses, memory, and generic operations used to recover \(\alpha\) belong to the verifier.

This control invalidates the earlier producer-only certificate/collision lemma: a sound acceptance can arise from verifier computation even though the producer transcript contains no informative collision. On accepted roots other than \(\alpha=1\), the producer’s handles \(G\) and \(Q\) are distinct. Arbitrary certificate contents cannot move verifier-created labels or work across the producer/verifier boundary. No narrowed version of that false certificate lemma is used below.

For \(d=N/2\), \(\mathcal P_0\) has constant correctness \(d/N=1/2\) and \(O(1)\) producer work. This is the exact obstruction to a \(d\)-uniform producer rho bound.

## 3. Generic model and charged resources

The group is represented by a uniformly random injection
\[
\xi:\mathbb F_r\hookrightarrow\mathcal E,
\qquad |\mathcal E|=M\ge r.
\]
Opaque encodings \(\xi(z)\) are visible as strings. The interface permits:

- equality of issued handles;
- group addition and inversion;
- multiplication by a disclosed scalar;
- inspection, comparison, hashing, or branching on visible encoding strings.

It supplies no pairing, endomorphism, correspondence, extension-field oracle, nonlinear map, verifier oracle, or certificate oracle.

Preprocessing occurs before \(\alpha\) is sampled and is independent of the challenge. At the start of an online attempt:

- \(P\) is the number of distinct resident challenge-independent oracle-handle records, including the public \(G\);
- \(C_{\rm pre}\) is their charged construction and storage-initialization work;
- in the ordinary unit-cost model, \(C_{\rm pre}\ge P-1\), because only \(G\) is supplied without construction;
- any non-handle advice words are separately included in \(C_{\rm pre}\), peak memory, and data movement, but do not create collision roots.

The online producer accounting records:

- \(q_g\): all online generic-oracle calls; at most \(q_g\) new handles can be issued;
- \(q_{\rm eq}\): explicit handle or encoding equality tests not already charged in \(q_g\);
- \(q_{\rm raw}\): raw-string inspections, hashes, and comparisons;
- \(q_{\rm branch}\): formal control-flow decisions;
- \(A_{\rm move}\): record reads, writes, table probes, and other data movement;
- \(S_{\rm peak}\): peak resident words.

One-attempt charged work is
\[
W_{\rm att}
 =C_{\rm pre}+q_g+q_{\rm eq}+q_{\rm raw}
  +q_{\rm branch}+A_{\rm move}.
\tag{3}
\]
In particular, \(W_{\rm att}\ge (P-1)+q_g\) and \(S_{\rm peak}\ge P\).

The \(q_g+1\) online-label boundary is exact as a worst-case boundary: \(L_0=X\) is the supplied challenge handle \(Q\), and each of the \(q_g\) oracle calls can issue at most one further label \(L_j\). Thus there are at most
\[
n=q_g+1
\]
online label slots. A final output produced by an oracle call is already one of those slots and is not counted again. An output equal to \(G\) or another preprocessing handle is already among the \(P\) records.

The theorem requires the output to be an issued handle. If arbitrary strings were allowed, after \(m\) distinct issued encodings and conditional on the target scalar not already being issued, \(g\) adaptive non-issued guesses would add at most
\[
\frac{g}{M-m}
\tag{4}
\]
to success. That extension is not part of theorem (1).

Single-instance preprocessing is fully charged. If one preprocessing table is reused for \(B\) mutually independent challenges, only the construction term may be reported as \(C_{\rm pre}/B\); peak memory \(P\), resident data \(P\), online work, and accesses are not divided by \(B\). Such a row is amortized multi-instance work, not ordinary single-instance work.

## 4. Fixed symbolic transcript, including raw encodings

Fix all producer coins, preprocessing coins, a sequence of distinct random strings from \(\mathcal E\), and the deterministic responses that the producer makes to those strings. This fixed object is denoted \(\tau\). It is sampled independently of \(\alpha\).

The symbolic oracle assigns a fresh pre-sampled encoding string to each new formal-label class and reuses a string only for a formally identical label. Raw strings are therefore concrete inside \(\tau\). Every comparison of their bits, hash, table probe, equality branch, and subsequent oracle-call schedule is fixed before any value of \(\alpha\) is substituted.

Each preprocessing handle has a constant formal label
\[
K_i(X)=c_i,\qquad 1\le i\le P.
\]
The online input has \(L_0(X)=X\). Before an informative collision, induction on oracle calls gives
\[
L_j(X)=a_j+b_jX.
\]
Addition, inversion, and multiplication by a disclosed scalar preserve this affine form. Branching does not alter closure because the branch is already fixed by \(\tau\).

For a particular \(\alpha\), the real and symbolic transcripts can diverge only if two formally distinct labels evaluate to the same scalar. Outside those root events, all evaluated scalars represented by distinct formal classes are distinct. Their encodings under a uniformly random injection are a uniformly random ordered tuple without replacement, exactly matching the symbolic token distribution.

Hence, for every fixed \(\tau\), every \(\alpha\) outside the collision union follows the same schedule and raw-bit branches. This coupling does not condition on an \(\alpha\)-dependent branch. Averaging the per-\(\tau\) bound over the independently sampled coins and encoding tokens proves the randomized bound.

Because \(\xi\) is injective and symbolic encodings are sampled without replacement, distinct formal labels cannot suffer a raw-string coincidence outside a scalar collision. Thus the raw-encoding exceptional set is
\[
E_{\rm raw}(\tau)=\varnothing.
\]
A non-injective encoding model would require a separate birthday term and is outside this theorem.

## 5. Exact root sets and one union

Remove all identically equal formal-label pairs before defining root sets.

For each preprocessing/online pair with \(K_i\not\equiv L_j\), define
\[
C^{\rm PO}_{i,j}
 =\{x\in D:K_i(x)=L_j(x)\}.
\]
The exact preprocessing/online collision set is
\[
C_{\rm PO}
 =\bigcup_{\substack{1\le i\le P,\ 0\le j<n\\
                     K_i\not\equiv L_j}}
   C^{\rm PO}_{i,j}.
\tag{5}
\]

For each unordered pair of online labels with \(L_j\not\equiv L_k\), define
\[
C^{\rm OO}_{j,k}
 =\{x\in D:L_j(x)=L_k(x)\},
\]
and
\[
C_{\rm OO}
 =\bigcup_{\substack{0\le j<k<n\\L_j\not\equiv L_k}}
   C^{\rm OO}_{j,k}.
\tag{6}
\]

Every polynomial difference in (5) or (6) is a nonzero affine polynomial. Each constituent set therefore contains at most one member of \(D\). If
\[
m_{\rm PO}
 =\#\{(i,j):K_i\not\equiv L_j\},
\quad
m_{\rm OO}
 =\#\{\{j,k\}:L_j\not\equiv L_k\},
\]
then
\[
m_{\rm PO}\le Pn,
\qquad
m_{\rm OO}\le\binom n2.
\tag{7}
\]

For every handle \(H\) issued in \(\tau\), with formal affine label
\(h(X)=a+bX\), define its target-agreement set
\[
T_H=\{x\in D:h(x)=x^d\}.
\tag{8}
\]
This defines the required agreement set for every allowed output handle. Because the fixed transcript selects one handle \(H_{\rm out}(\tau)\), the agreement set relevant to that transcript is
\[
T_{\rm out}=T_{H_{\rm out}(\tau)}.
\tag{9}
\]
Using the union of all \(T_H\) in the success bound would count output alternatives that the fixed transcript did not select.

Since \(2\le d<r-1<r\), the polynomial
\[
a+bX-X^d
\]
is nonzero and has degree \(d\). Therefore
\[
|T_H|\le d
\tag{10}
\]
for every allowed issued output. For \(H=G\), equality holds:
\[
T_G=\{x\in D:x^d=1\},
\qquad |T_G|=d.
\tag{11}
\]

The single exact bad/success-covering union for transcript \(\tau\) is
\[
U_\tau
 =C_{\rm PO}\cup C_{\rm OO}\cup
  T_{\rm out}\cup E_{\rm raw}.
\tag{12}
\]
This is a set union. A root belonging to multiple collision pairs, or to both a collision set and \(T_{\rm out}\), is counted once in \(|U_\tau|\). Only after forming (12) do we use the conservative cardinality bound
\[
|U_\tau|
 \le
 \min\!\left\{
 N,\,
 m_{\rm PO}+m_{\rm OO}+d
 \right\}
 \le
 \min\!\left\{
 N,\,
 Pn+\binom n2+d
 \right\}.
\tag{13}
\]
This justifies, and improves on, the looser expression
\(P(q_g+1)+(q_g+1)^2\). The \(q_g+1\) term is never silently replaced by \(q_g\).

## 6. Producer correctness theorem

Fix \(\tau\). If \(\alpha\notin C_{\rm PO}\cup C_{\rm OO}\), the real execution is coupled to the fixed symbolic execution, including all raw-string branches. The producer returns the fixed issued handle \(H_{\rm out}(\tau)\). It is correct only if
\[
\alpha\in T_{\rm out}.
\]
If \(\alpha\) lies in a collision set, the real execution may diverge and may succeed, so all collision roots are conservatively counted.

Thus the real success set is a subset of \(U_\tau\), and
\[
\Pr_\alpha[\operatorname{success}\mid\tau]
 \le \frac{|U_\tau|}{N}.
\]
Averaging over \(\tau\) proves (1).

Writing \(\delta=s-d/N\), inequality (1) gives (2):
\[
Pn+\binom n2\ge N\delta
\]
whenever \(\delta>0\). Since
\[
Pn+\binom n2
 \le \frac34(P+n)^2,
\]
we obtain
\[
P+n\ge \sqrt{\frac{4N\delta}{3}}.
\tag{14}
\]
Using \(n=q_g+1\) and fully charging construction,
\[
W_{\rm att}
 \ge P+q_g-1
 =P+n-2
 \ge
 \sqrt{\frac{4N\delta}{3}}-2.
\tag{15}
\]

For constant \(s\) and constant \(\delta>0\), this is
\(\Omega(\sqrt N)\). In particular it applies when \(d=o(N)\) and producer correctness is constant.

When \(\delta\le0\), this route intentionally gives no collision lower bound. The \(R=G\) control realizes success \(d/N\), showing that this loss is necessary rather than a proof artifact.

## 7. Expected work, retries, memory, and data

The capped theorem immediately gives the required retry accounting. For independent, identically distributed attempts with detectable success probability \(s_{\rm att}>0\), where every attempt includes its allocated preprocessing charge,
\[
\mathbb E[W_{\rm to\ success}]
 =
 \mathbb E[W_{\rm att}]\,
 s_{\rm att}^{-1}.
\tag{16}
\]
If preprocessing is constructed once and reused, the correct expression is instead
\[
C_{\rm pre}
 +\mathbb E[W_{\rm online,att}]\,s_{\rm att}^{-1}.
\tag{17}
\]
That is an explicitly amortized/reused-preprocessing regime. Repeating against the same fixed challenge is not justified merely from success averaged over random \(\alpha\); the attempts must renew the relevant randomness and success must be detectable.

The constant-correctness result also covers algorithms specified only by expected charged work. Let \(T\) be total charged single-instance work, \(\mu=\mathbb E[T]\), and \(s=\Pr[\operatorname{success}]\). Assume
\[
\delta=s-\frac dN>0.
\]
Abort an execution after
\[
L=\left\lceil\frac{2\mu}{\delta}\right\rceil
\]
charged steps. Markov’s inequality shows that aborting loses at most
\(\delta/2\) success probability. On every surviving transcript,
\(P\le L+1\), \(q_g\le L\), and \(n\le L+1\). Applying (1) to the truncated producer gives
\[
\frac{\delta}{2}
 \le \frac{3(L+1)^2}{2N}.
\]
Therefore
\[
\mu
 \ge
 \frac{\delta}{2}
 \left(\sqrt{\frac{\delta N}{3}}-2\right).
\tag{18}
\]
For constant excess \(\delta\), expected single-instance producer work is
\(\Omega(\sqrt N)\). Heavy-tailed scheduling therefore does not evade the repaired constant-excess theorem.

No positive memory exponent follows: Pollard rho uses \(N^{o(1)}\) memory. Preprocessing gives the explicit bound \(S_{\rm peak}\ge P\). Every generic call, equality, raw branch, table probe, and data movement remains in (3). Counting all \(Pn\) possible preprocessing/online root pairs is conservative even if the producer reads only a subset; inaccessible pairs can only make the true collision set smaller.

For \(B\) independent challenges sharing one table,
\[
\mathbb E[W_{\rm amortized\ per\ challenge}]
 =
 \frac{C_{\rm pre}}B+\mathbb E[W_{\rm online}],
\tag{19}
\]
while memory and resident data remain at least \(P\). This is not an ordinary single-instance row.

## 8. Verifier separation

A verifier has its own parameters
\[
P_v,\ q_{g,v},\ q_{{\rm eq},v},
A_{{\rm move},v},\ S_{{\rm peak},v},\ s_v.
\]
A perfectly sound verifier may recover \(\alpha\) by generic baby-step/giant-step using \(\Theta(\sqrt N)\) generic work, memory, and table data, then compare \(R\) with \(\alpha^dG\). Alternatively it may use an exhaustive method with a different verifier-only cost profile.

None of these verifier labels or collisions appears in \(P\), \(q_g\), \(C_{\rm PO}\), or \(C_{\rm OO}\). A statement about
\[
W_{\rm producer}+W_{\rm verifier}
\]
is a combined-work statement and cannot replace theorem (1), which is producer-only. No certificate-soundness conclusion is inferred.

## 9. Pareto and prior-art boundary

For exponents \(P=\Theta(N^p)\), \(q_g+1=\Theta(N^x)\), and
\[
Ns-d=\Theta(N^\kappa),
\]
the collision constraint is
\[
\max\{p+x,2x\}\ge\kappa.
\]
Its boundary is piecewise:
\[
x=
\begin{cases}
\kappa/2,&0\le p\le\kappa/2,\\
\kappa-p,&\kappa/2<p<\kappa,\\
0,&p\ge\kappa.
\end{cases}
\]
Fully charged single-instance time includes \(N^p\), so preprocessing above the square-root balance does not improve ordinary single-instance time. It can reduce online queries only by increasing construction, memory, and resident data. Multi-instance amortization is a different scope.

Cheon’s auxiliary-input algorithm assumes that \(\alpha^dG\) is already supplied and is therefore not a producer for the ordinary input considered here. Generic nonlinear-target hardness and target-assumption classifications are also prior art:

- https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf
- https://www.iacr.org/archive/asiacrypt2008/53500495/53500495.pdf
- https://eprint.iacr.org/2007/360.pdf
- https://eprint.iacr.org/2017/343.pdf
- https://static.aminer.org/pdf/PDF/000/314/734/variations_of_diffie_hellman_problem.pdf

The ordinary-ECDLP claimed SOTA deltas in time, memory, and data/query exponent are all zero. No global frontier is claimed.

## 10. Outcome

The producer route is repaired only as a constant-excess theorem:

- exact producer success is bounded by the union of producer collision roots and the selected output’s nonlinear agreement roots;
- constant correctness above the unavoidable \(d/N\) root mass forces rho-scale expected single-instance producer work;
- constant correctness alone does not do so uniformly in \(d\);
- \(d=N/2\), \(R=G\) is the exact constant-work, constant-correctness obstruction;
- verifier or certificate work remains separate.

Official research status is unchanged.
