# Fixed-field and information-loss barriers with one premise-changing escape

## Epistemic boundary

This is a theory proposal, not an experiment, implementation, status transition,
closure result, or breakthrough claim. The fixed-field barrier and quotient
correction below are reconstructed from the authorized capsule. The proposed
escape is conditional on an open auxiliary-power recovery lemma and on a
strictly stronger input contract than ordinary ECDLP.

## Notation and cost model

Let \(E/\mathbb F_p\) be an elliptic curve and let
\(G=\langle P\rangle\subseteq E(\mathbb F_p)\) be cyclic of prime order \(N\).
The scalar convention is fixed throughout:

\[
Q=[x]P,\qquad x\in\mathbb F_N.
\]

The identity is \(O\). Scalar arithmetic is in \(\mathbb F_N\), while interval
representatives of scalars are in \(\{0,\ldots,N-1\}\).

Costs are reported separately as:

- online time: elliptic-curve group operations;
- memory: simultaneously stored group elements;
- preprocessing: group operations independent of the particular \(x\);
- data: secret-dependent auxiliary group elements and their bit length;
- queries: calls needed to obtain secret-dependent auxiliary data;
- verification: group operations needed to verify the recovered scalar.

Integer and field arithmetic polynomial in \(\log N\) is
\(N^{o(1)}\), but secret-dependent inputs are never hidden in that notation.
No cross-model comparison treats an unavailable auxiliary point as free.

## Lemma 1 — fixed-field trace and order invariance

If \(E\) and \(E'\) are isogenous over \(\mathbb F_p\), their Frobenius
characteristic polynomials agree. Hence their traces agree and

\[
\#E(\mathbb F_p)=p+1-t=\#E'(\mathbb F_p).
\]

Therefore movement within an \(\mathbb F_p\)-isogeny class cannot change the
rational group order.

## Lemma 2 — preservation of the order-\(N\) subgroup and embedding degree

Let \(\phi:E\rightarrow E'\) be an \(\mathbb F_p\)-defined isogeny with
\(\gcd(\deg\phi,N)=1\). Its restriction

\[
\phi|_G:G\longrightarrow \phi(G)
\]

has trivial kernel and is an isomorphism onto an order-\(N\) subgroup.

The embedding degree of this subgroup is

\[
k=\operatorname{ord}_N(p).
\]

It depends only on \(p\) and \(N\). Holding both fixed therefore holds \(k\)
fixed; an isogeny inside the same fixed-field class cannot manufacture a lower
MOV/Frey–Rück embedding degree.

## Lemma 3 — prime-field subfield limitation

The prime field \(\mathbb F_p\) has no proper subfield. Replacing one curve over
\(\mathbb F_p\) by an isogenous curve over the same field cannot create a
proper-prime-field subfield into which the ECDLP descends.

Lemmas 1–3 exclude only the named mechanism inside the frozen boundary. They do
not exclude field-changing reductions, order-changing correspondences,
extension-field constructions, or independently supplied side information.

## Lemma 4 — exact quotient cardinality

Suppose an ambient set has \(N M\) pairs and the stated equivalence relation
partitions it into classes of exactly \(M\) representatives. Then

\[
\left|(G\times[M])/{\sim}\right|=\frac{NM}{M}=N.
\]

It is not \(N/M\). Adding a redundant label and quotienting the redundancy
does not compress the original \(N\)-element state space.

A genuinely reduced state space of size \(N/M\) must instead discard,
identify, or externally resolve a multiplicity-\(M\) fiber.

## Lemma 5 — omitted fibers and success probability

Let a projection retain one effective state for each \(M\)-element fiber.
For a target whose fiber label is uniform conditional on the projected state,
an attempt accepting only one label succeeds with probability exactly \(1/M\).
More generally, if \(r\) labels are accepted, its success probability is
\(r/M\).

Thus a search over \(N/M\) projected states is not by itself a search over all
\(N\) original targets. A proof-backed recoverable label, a proved bias, or an
explicit search of the remaining fiber is required.

## Lemma 6 — per-attempt exponent

Define the asymptotic regime

\[
M=N^{\delta+o(1)},\qquad 0\leq\delta\leq1.
\]

Define \(\gamma\geq0\) by a multiplicative per-visited-state overhead of

\[
N^{\gamma+o(1)}
\]

in the same group-operation units as the baseline search.

Under the numbered random-mapping heuristic H-206-02, a collision search over
\(N/M\) effective states takes

\[
N^{\gamma+o(1)}\sqrt{N/M}
  =N^{\gamma+(1-\delta)/2+o(1)}
\]

operations per attempt.

## Lemma 7 — complete expected-cost assembly

Under H-206-01, retaining one unlabelled representative gives

\[
p_{\rm success}=M^{-1}=N^{-\delta+o(1)}.
\]

Therefore

\[
\begin{aligned}
T_{\rm expected}
  &=\frac{T_{\rm attempt}}{p_{\rm success}}\\
  &=N^{\gamma+(1-\delta)/2+o(1)}N^{\delta+o(1)}\\
  &=N^{\gamma+(1+\delta)/2+o(1)}.
\end{aligned}
\]

This reconstructs the reviewed exponent. For \(\gamma\geq0\), it is never
below \(1/2\); for \(\delta>0\) it is strictly worse than matched Pollard rho
unless the fiber loss is removed by additional structure.

## Barrier proposition

A fixed-\(\mathbb F_p\), prime-to-\(N\) isogeny cannot create the reviewed
anomalous, lower-embedding-degree, or prime-field-subfield weakness. A
cardinality-neutral relabelling cannot create an \(N/M\) search space. A lossy
projection that does create such a space but omits a uniform
multiplicity-\(M\) fiber has expected exponent
\(\gamma+(1+\delta)/2\), after inverse success probability is charged.

The proposition does not close isogeny transfer or ECDLP. It identifies the
premises that an escape must violate.

## Premise-changing candidate: auxiliary-power two-stage recovery

### Named premise violation

Ordinary ECDLP supplies only \((E,\mathbb F_p,N,P,Q)\). The candidate changes
that input contract by additionally supplying the secret-dependent group
element

\[
A=[x^d\bmod N]P
\]

for a public divisor \(d\mid N-1\). This provides algebraically correlated side
information rather than manufacturing a weakness by fixed-field isogeny or
silently dropping a fiber.

### Typed objects

Define the scalar power map

\[
f_d:\mathbb F_N^\*\longrightarrow\mathbb F_N^\*,\qquad z\mapsto z^d,
\]

and the encoding relative to \(P\),

\[
\operatorname{enc}_P:\mathbb F_N\longrightarrow G,\qquad z\mapsto[z]P.
\]

The auxiliary input is \(A=\operatorname{enc}_P(f_d(x))\). The map \(f_d\) is
a scalar-space map, not an efficiently available elliptic-curve endomorphism.
The supplied point \(A\) is therefore a genuine additional input.

If \(Q=O\), then \(x=0\) is detected immediately. The nontrivial analysis
assumes \(x\in\mathbb F_N^\*\).

### Exact image and fiber cardinalities

Because \(\mathbb F_N^\*\) is cyclic of order \(N-1\) and \(d\mid N-1\),

\[
|\ker f_d|=d,\qquad
|\operatorname{im} f_d|=(N-1)/d,
\]

and every nonempty fiber has exactly \(d\) elements.

The candidate uses both levels rather than discarding the fiber:

1. an image stage of cardinality exactly \((N-1)/d\);
2. a fiber stage of cardinality exactly \(d\).

The open auxiliary-power recovery lemma APR-206 asserts that the typed
relations supplied by \((P,Q,A,d)\) admit complete meet-in-the-middle searches
over those two domains with costs

\[
O\!\left(\sqrt{(N-1)/d}\right)
\quad\text{and}\quad
O(\sqrt d)
\]

group operations, respectively. This lemma is not proved by the capsule and
must receive an archived line-by-line proof before the candidate can support
any ECDLP claim.

### Per-attempt and total cost

Use deterministic table-based meet-in-the-middle stages, with stopping bounds

\[
m_I=\left\lceil\sqrt{(N-1)/d}\right\rceil,\qquad
m_F=\lceil\sqrt d\rceil.
\]

Conditional on APR-206, both domains are exhaustively covered, so the success
probability for a well-formed augmented input is \(1\), not \(1/d\). The second
stage explicitly pays for the entire \(d\)-element fiber.

Let

\[
d=N^{\delta+o(1)},\qquad 0<\delta<1.
\]

Then

\[
T_{\rm solve}
 =N^{(1-\delta)/2+o(1)}+N^{\delta/2+o(1)}
 =N^{\tau(\delta)+o(1)},
\]

where

\[
\tau(\delta)=
\max\left\{\frac{1-\delta}{2},\frac{\delta}{2}\right\}
=\frac12-\frac{\min(\delta,1-\delta)}2<\frac12.
\]

The memory exponent of the table implementation is also
\(\tau(\delta)\). At a valid divisor family with
\(d=N^{1/2+o(1)}\), both time and memory exponents are \(1/4\).

Verification of a proposed scalar \(x'\) checks

\[
Q=[x']P
\quad\text{and}\quad
A=[(x')^d\bmod N]P.
\]

This takes \(N^{o(1)}\) group operations and makes \(x'\) a succinct public
certificate.

### Preprocessing, data, and acquisition

Curve- and divisor-only preprocessing is required to remain
\(N^{o(1)}\). The two meet-in-the-middle tables are online work and are not
relabelled as free preprocessing.

The augmented input contains one secret-dependent group element \(A\), or
\(\Theta(\log N)\) encoded bits. Its exponent is zero, but its exact count and
secret dependence are material. If an oracle supplies it, the attack uses one
auxiliary-data query before solving.

Let obtaining \(A\) from an ordinary ECDLP instance cost
\(N^{a+o(1)}\) group-operation-equivalent units. End-to-end time is then

\[
N^{\max\{a,\tau(\delta)\}+o(1)}.
\]

Consequently, if \(a\geq1/2\), the candidate has no exponent advantage for
ordinary ECDLP. No amortization is claimed: \(A\) depends on the particular
secret \(x\), so a table for one target is not reusable for unrelated targets.

### Matched Pollard comparison and Pareto result

On the same augmented input, Pollard rho may ignore \(A\) and solve in expected
time \(N^{1/2+o(1)}\) with \(N^{o(1)}\) memory. Conditional APR-206 improves the
online time exponent by

\[
\Delta_{\rm time}
 =\tau(\delta)-\frac12
 =-\frac{\min(\delta,1-\delta)}2,
\]

which is \(-1/4\) at \(\delta=1/2\). It raises table memory from exponent \(0\)
to \(\tau(\delta)\). Neither row dominates the other across time and memory.

Against ordinary-input Pollard rho, the comparison is in a different data
domain. The candidate is not an ordinary-ECDLP reduction unless acquisition of
\(A\) is independently justified and charged below exponent \(1/2\).

After checking the authorized time, memory, preprocessing, data, and query
rows, the conditional augmented-input candidate has `dominated_by: null`.
This null is restricted to the augmented-input frontier and does not claim a
new ordinary-ECDLP state of the art.

## Numbered heuristics

### H-206-01 — uniform omitted-fiber label

Conditional on the projected state, the omitted label is uniform among \(M\)
labels.

Falsification: a proved or measured conditional distribution with
success probability asymptotically different from \(1/M\), after the
measurement is repeated against an identical-shape null.

### H-206-02 — random-mapping collision cost

A randomized projected walk behaves sufficiently like a random mapping on
\(N/M\) states that its collision cost is
\(N^{(1-\delta)/2+o(1)}\).

Falsification: a proved mixing obstruction or a controlled collision
distribution whose normalized stopping time does not approach the predicted
birthday scale.

Neither heuristic is needed by the proposed deterministic APR-206
meet-in-the-middle implementation; APR-206 instead remains an open proof
obligation.

## Pre-registered controls

1. **Cardinality-preserving null:** replace \(A=[x^d]P\) by an independent
   uniformly sampled group element while preserving its encoding and all table
   dimensions. Recovery above ordinary generic baseline must disappear.
2. **Fiber-label destruction:** permute auxiliary points across independent
   instances, preserving both marginals but breaking the relation
   \(A=[x^d]P\). Any retained signal is an artifact.
3. **Limit test:** as \(d\) grows, the predicted cost
   \(\sqrt{(N-1)/d}+\sqrt d\) is U-shaped and is minimized near
   \(d=\sqrt N\). Continued monotone improvement beyond that point reveals a
   missing fiber-stage cost.
4. **Inverse-success restoration:** if the \(d\)-element fiber stage is omitted
   and one root is guessed, success is \(1/d\); the attempt cost must be
   multiplied by \(d\).
5. **Orientation and type check:** every generated instance must satisfy
   \(Q=[x]P\) and \(A=[x^d\bmod N]P\). No expression may treat \(x^d\) as a
   point, multiply two unknown points, or reverse the scalar orientation.
6. **Matched-accounting control:** charge table construction, one
   secret-dependent auxiliary point, its acquisition query, verification, and
   any restarts in the same units used for the comparator.

## Exact scope

The fixed-field and information-loss barriers survive within their named
premises. The auxiliary-power candidate escapes only by changing the input
contract. It survives symbolic inverse-success and Pareto accounting
conditional on APR-206, but it is not yet a validated algorithm in this
record, does not reduce ordinary ECDLP without a cheap source of \(A\), and
does not justify a hypothesis-status change.
