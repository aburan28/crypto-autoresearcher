# Static stopping-time and end-to-end cost audit

Task: `TASK-20260723-401`  
Goal: `GOAL-CRYPTO-001`  
Idea: `IDEA-20260723-002`  
Verdict: `INCONCLUSIVE_COST_CLAIM`

This is non-operational academic mathematics. No computation, implementation,
curve execution, real key, deployed system, or standardized cryptographic
curve was used. The audit reports no experimental outcome and makes no
breakthrough claim.

## 1. Audit result

The BATCH-003 cancellation is sound as a conditional statement:

\[
  M=\binom{r+d}{d},\qquad
  H=\binom{r+d}{d-1}=M\frac{d}{r+1},
\]

and, if the success probability of the same charged fixed-\(b\) trial obeys
\(q_b\leq N^{o(1)}M/N\), while a failed trial processes all \(H\) exact
penultimate signatures, then

\[
  \frac{H}{q_b}
  \geq N^{1-o(1)}\frac{d}{r+1}
  =N^{1-o(1)}
\]

for \(r=\Theta(\log N)\) and \(d\geq 1\). This is asymptotically worse than
Pollard rho and baby-step giant-step at exponent \(1/2\).

That premise does not align end to end with arXiv:2607.09814v1. The manuscript
uses \(M\) for a fixed-\(b\) completion probability but its public algorithm
loops over a different number \(B=\binom r d\) of \(b\)'s; it variously calls
both \(M\) and \(H\) the hashtable length; it gives no prefix law for first-
duplicate stopping; and it does not include rank, exact-collision,
index-union, scalar-orientation, or final-certificate failures in \(q_b\).
At \(d=1\), its own duplicate procedure has one table entry and therefore
cannot produce a duplicate despite the displayed \(q_b>0\). The exact
published expected cost is consequently unresolved, not sub-rho.

## 2. Source-aligned notation

Let \(N\) be an abstract prime subgroup order and
\(n=\lceil\log_2N\rceil\). The 2026 manuscript writes \(p\) for \(N\). Its
original kernel matrix has dimension \(\ell=\Theta(n)\), with
\(\ell=2\ell'\). Write

\[
  r=\ell'=\Theta(n).
\]

This \(r\) is the quantity called \(L\) in the BATCH-003 package. After the
one-step restriction, the matrix \(\mathcal K'\) is \(r\times 2r\).

The exact combinatorial quantities are:

| Symbol | Manuscript loop/event | Count |
|---|---|---:|
| \(A\) | possible first restrictions \(a\) | \(\binom{2r}{r}\), though Algorithm 1 samples one |
| \(B\) | fixed-part choices \(b\subseteq[r]\), \(|b|=r-d\) | \(\binom r d\) |
| \(M\) | \(d\)-column completions after one \(b\) is fixed | \(\binom{r+d}{d}\) |
| \(H\) | \((d-1)\)-row penultimate subsets for that \(b\) | \(\binom{r+d}{d-1}\) |

The identity

\[
  H=M\frac{d}{r+1}
\]

is exact. It does not identify \(B\) with \(M\).

Equation (4) of Section 6 uses the single-completion estimate

\[
  \alpha
  =\frac{N-2r+1}{N(N-r+1)}
  =\frac{1+o(1)}{N}
\]

and displays, for a fixed part,

\[
  q_b^{\mathrm{exist}}
  =1-(1-\alpha)^M.
\]

The simplified BATCH-003 formula replaces \(\alpha\) by \(1/N\), which does
not alter an \(N\)-exponent. The material issue is not that simplification;
it is whether \(q_b^{\mathrm{exist}}\) is the success probability of the
public duplicate-and-certificate procedure.

## 3. Exact \(a/b/M/H\) loop map

### First restriction \(a\)

Algorithm 1 lines 4--8 select \(r\) columns from the dense half of the
\(2r\times4r\) input kernel, transpose the submatrix, and reduce it to an
anti-diagonal \(r\times2r\) matrix. One \(a\) is sampled per invocation.

The source does not define:

- a complete retry law over \(a\);
- whether all \(a\)'s may reuse one target-bearing kernel \(\mathcal K\);
- when sampled points and the evaluation matrix must be rebuilt; or
- how failed \(a\), rank, and pivot events enter the stated probability.

A fixed \(\mathcal K\) can in principle be reused within one target, but every
new restriction and row reduction remains charged.

### Fixed-part loop \(b\)

Algorithm 1 lines 11--14 generate all subsets of \([r]\) of size \(r-d\).
The exact count is

\[
  B=\binom r{r-d}=\binom r d.
\]

For each \(b\), the algorithm extracts an \(r\times(r-d)\) matrix and computes
its left kernel \(T\). The claimed \(\dim T=d\) requires rank \(r-d\); a rank
failure is a charged branch, not a successful trial.

Section 5 prose instead says there are \(\binom{r+d}{d}\) such subsets. That
quantity is \(M\), the number of completions available after \(b\) has been
fixed. Section 5.2 correctly gives the full combinatorial shape

\[
  B\,H
  =\binom r d\binom{r+d}{d-1}
\]

before polynomial kernel and normalization costs.

### Signature matrix and inner table

For a fixed \(b\), the complement has \(r+d\) columns. Algorithm 1 creates a
signature matrix with \(r+d\) rows and \(d\) columns. The manuscript treats
\(r\) structured signatures as cheap and computes \(d\) signatures by row
reduction. “Free” here can only mean reduced arithmetic: generating,
indexing, reading, or regenerating those rows still incurs memory traffic.

The `create-intersection-signature` procedure enumerates every
\((d-1)\)-subset of the \(r+d\) rows. Hence its endpoint count is

\[
  H=\binom{r+d}{d-1}.
\]

Each entry requires at least:

1. retaining the subset's combinatorial provenance;
2. checking rank of a \((d-1)\times d\) matrix;
3. computing its exact right kernel;
4. normalizing by its first nonzero coordinate;
5. looking up a hash; and
6. resolving a hash collision by exact vector equality.

Section 4.1 and Algorithm 1 use this \(H\)-entry table. Section 8 instead calls
the hashtable length \(M=\binom{r+d}{d}\). These are unequal except at special
parameters and represent different objects.

### Postprocessing and certificate

Algorithm 2 receives two \((d-1)\)-subsets with equal penultimate vectors. A
complete accepted branch must:

1. require exact vector equality, not finite-hash equality;
2. require the union of the two index sets to have cardinality exactly \(d\);
3. map structured and dense indices back to \(\mathcal K'\) and \(\mathcal K\);
4. reverify the resulting maximal zero minor;
5. retain and reconstruct all public sampled-point coefficients;
6. obtain a relation with nonzero target coefficient modulo \(N\);
7. orient the scalar equation; and
8. verify the final public group equality.

Equation (4) prices none of the failure probabilities in this chain.
Theorem 5 also warns that its duplicate-to-zero-minor statement may be wrong,
so the existence event counted by \(M\) cannot simply be declared identical
to a valid public certificate.

## 4. Stopping-time audit

The pseudocode constructs the full inner dictionary and then searches it.
Section 4.1 separately says the implementation may stop at the first
duplicate. Those are different stopping processes.

For a full failed fixed-\(b\) trial, all \(H\) entries must be processed to
certify absence of a duplicate. For a successful trial, a first duplicate may
occur earlier. Endpoint values \(q_b\) and \(H\) do not determine its expected
position. A valid early-stop analysis needs either:

- an occupancy bound for every processed prefix; or
- an equivalent stopping-time theorem tied to the actual enumeration order.

Neither appears in the manuscript.

There is still a useful conditional cancellation. Suppose each completion
event has probability at most \(N^{o(1)}/N\), every public success is contained
in one of those events, and failed fixed-\(b\) trials cost \(\Omega(H)\). For
any \(t\) processed \(b\)'s, a union bound gives

\[
  \Pr[\text{success among the first }t\text{ }b\text{'s}]
  \leq N^{o(1)}\frac{tM}{N}.
\]

Thus adding \(B\) outer choices cannot be treated as a free probability
multiplier: the \(B\) work cancels the at-most-\(B\) completion mass. In the
low-success regime the conditional expected charge remains

\[
  \Omega\!\left(\frac{NH}{M}\right)
  =\Omega\!\left(\frac{Nd}{r+1}\right)
  =N^{1-o(1)}.
\]

This derivation is a conditional implication, not a source-verified expected
cost. It requires the missing event and stopping alignment. When
\(M=\Omega(N)\), full-table work already has
\(H=\Omega(Nd/(r+1))\), but a lower bound for an optimally early-stopped
successful table still needs the missing prefix theorem.

## 5. The \(d=1\) boundary

At the admitted smallest defect,

\[
  B=r,\qquad M=r+1,\qquad H=1.
\]

The sole penultimate subset is the empty set. Its \(0\times1\) right kernel
has a normalized generator, but the table contains only one entry. Two
distinct entries cannot repeat, so the stated duplicate search cannot return
a witness. In contrast, Equation (4) gives

\[
  q_b^{\mathrm{exist}}=1-(1-\alpha)^{r+1}>0.
\]

This is a direct event mismatch. A special \(d=1\) branch might inspect zero
signatures or test the \(r+1\) completions directly, but no such branch is in
Algorithm 1. Adding it would require a separate proof and charges for every
extension test, equality check, provenance record, orientation check, and
certificate. The value \(H=1\) cannot price that unstated process.

## 6. Rank, orientation, and exactness failures

The end-to-end success probability must include all of the following:

| Stage | Required condition | Charged failure |
|---|---|---|
| Evaluation matrix | expected rank and kernel dimension | rebuild or reject the stratum |
| Restriction \(a\) | sufficient rank and anti-diagonal pivots | another restriction/reduction |
| Fixed part \(b\) | rank \(r-d\), hence \(\dim T=d\) | next \(b\) |
| Hyperplane signature | handled nonzero normalization, or a proved zero-signature branch | next branch or semantic failure |
| Penultimate matrix | rank \(d-1\) | general-position branch |
| Duplicate | exact normalized vectors agree | hash-collision resolution |
| Index union | cardinality exactly \(d\) | continue searching |
| Zero minor | exact determinant/rank verification | reject candidate |
| Source relation | coefficients reconstruct correctly | reject candidate |
| Orientation | target coefficient is nonzero modulo \(N\) | resample or continue |
| Certificate | final public group equality holds | reject candidate |

These conditions can only lower public success relative to an existence count.
That observation does not repair formula alignment: an unquantified lower
success probability makes cost no better, but it prevents an exact expected
cost claim.

## 7. Preprocessing and full work ledger

Curve-only symbolic preparation can be separated if it contains neither the
target nor sampled target multiples. Monomial ordering, evaluation formulas,
and basis conventions have \(n^{O(1)}\) bit cost and may be reused.

For one target, the following are not free:

- generating \(O(n)\) sampled public multiples involving both public points;
- constructing and reducing the evaluation matrix;
- computing and storing \(\mathcal K\) with coefficient provenance;
- every \(a\) extraction, transpose, rank check, and anti-diagonal reduction;
- every \(d\) choice tried;
- all \(B\) fixed-part kernels until stopping;
- all generated or read signature rows;
- every processed inner subset, kernel, normalization, hash lookup, exact
  equality check, and provenance record;
- sorting, I/O, recomputation, or extra passes used instead of an in-RAM table;
- all failed rank, union, orientation, and certificate branches; and
- exact reconstruction and final verification.

The setup and final verification are polynomial in \(n\), so they have
\(N\)-exponent zero. They do not erase an exponent-one search. Conversely,
the target-bearing evaluation matrix cannot be amortized across unrelated
targets. A fixed \(\mathcal K\) may be reused across restrictions for one
target, but that does not make the restriction and search loops free.

This is a direct-relation route, so omitting factor-base relation collection,
factor-log linear algebra, and descent is appropriate. It must still include
the entire relation-to-oriented-scalar certificate path.

## 8. Bit memory and traffic

The signature matrix itself occupies

\[
  O((r+d)d\,n)
\]

bits when field elements have \(\Theta(n)\)-bit representation.

An exact in-RAM table retaining normalized \(d\)-coordinate vectors and subset
provenance has the shape

\[
  O\!\left(
    H\left(dn+\log_2H+\text{metadata}\right)
  \right)
\]

bits. A hash-only representation replaces \(dn\) by a hash width \(\lambda\),
but exact Las Vegas acceptance then requires retained vectors or charged
recomputation for collision resolution.

For fixed \(d\), \(M,H,B\) are polynomial in \(n\), so peak table memory has
\(N\)-exponent zero while the conditional retry work has exponent one. If
modeled constant success requires \(M=\Omega(N)\), then \(d=\Theta(r)\) and

\[
  H=\Theta(N)
\]

up to constant or subpolynomial factors. Hash and provenance records then
have near-linearly many logarithmic-width entries. Retaining exact vectors
costs \(O(Nn^2)\) bits at this scale.

The manuscript does not prove that exact duplicate recovery can be streamed
with polynomial live memory and unchanged work. External sorting, multiple
passes, recomputation, and I/O merely move the charge. Parallelism similarly
changes wall clock, not aggregate processors, memory traffic, or total work.

## 9. Charged exponents

All entries below are symbolic; no timing or run occurred.

| Component | Work exponent in \(N\) | Bit-memory exponent in \(N\) | Status |
|---|---:|---:|---|
| Curve-only preparation | \(0\) | \(0\) | polynomial in \(n\) |
| Target setup per rebuild | \(0\) | \(0\) | polynomial in \(n\) |
| Fixed-\(d\), one \(b\) | \(0\) | \(0\) | polynomial in \(n\) |
| Aligned \(q/M/H\) expected work | \(1-o(1)\) | parameter-dependent | conditional only |
| Constant-success full \(H\) table | \(1-o(1)\) | \(1-o(1)\) | conditional endpoint |
| Exact published end-to-end algorithm | unknown | unknown | formula/stopping mismatch |
| Pollard rho | \(1/2+o(1)\) | \(0\) serial | matched generic baseline |
| BSGS | \(1/2+o(1)\) | \(1/2+o(1)\) | generic time-memory baseline |

Field operations, group operations, and memory accesses each have
polynomial-\(n\) bit costs in this abstract family. Their conversion to bit
operations does not close an exponent gap between one and one half.

## 10. Baseline comparison

### Pollard rho

The matched reference is \(N^{1/2+o(1)}\) expected group operations with
small serial memory; distinguished-point parallelism reduces wall clock
without making aggregate work free. This follows the program's
`KN-TECH-001`, `KN-LIT-008`, and `KN-LIT-012` baseline.

Under the additional alignment premise, the signature route costs
\(N^{1-o(1)}\), so it is asymptotically worse. Without that premise, the
correct label is “cost unresolved,” not “better than rho.”

### Baby-step giant-step

BSGS uses \(N^{1/2+o(1)}\) group operations and
\(N^{1/2+o(1)}\) stored group elements. Fixed defect may use less peak memory,
but conditionally requires near-linear expected work. The modeled
constant-success exact-table branch has near-linear entries. Neither branch
improves the BSGS time-memory frontier.

### Exact specialized baselines

The 2018 Problem L paper states that its multiple-Gaussian-elimination method
has whole-algorithm success

\[
  0.6\frac{(\log N)^2}{N}
\]

per polynomial-time pass. Its own formula therefore gives
\(N^{1-o(1)}\) expected work. It is a specialized near-linear baseline, not a
sub-rho one.

The 2023/2025 zero-minor manuscript states per-kernel costs
\(O(r^5)\) for two deviations, \(O(r^7)\) for three deviations, and
\(O(r^{2s+1})\) for \(s\) deviations. It supplies no large-\(N\) theorem for
the number of kernels and no matched prime-field success law. Its complete
expected exponent is therefore unknown; small binary-field tables are not an
asymptotic baseline.

The closest exact specialized comparator is the 2026 method itself:

\[
  B=\binom r d
  \quad\text{outer fixed parts},\qquad
  H=\binom{r+d}{d-1}
  \quad\text{inner entries per fixed part}.
\]

Its probability equation counts \(M=\binom{r+d}{d}\) completions for one
fixed part. Because the manuscript does not bind these quantities to one
complete stopping and certificate process, it supplies no verified
end-to-end exponent. If the missing alignment is supplied, the conditional
exponent is one and the route does not beat rho, BSGS, or its 2018
specialized predecessor in exponent.

## 11. Verdict and falsification boundary

The verdict is `INCONCLUSIVE_COST_CLAIM`.

This does not mean that a sub-rho mechanism was observed. It means the
manuscript's \(q/M/H\) formulas do not describe one fully specified public
stopping process, so the exact algorithm cannot inherit the otherwise-valid
near-linear cancellation without an additional proof. The strongest
supported statement is:

> If the completion occupancy bound applies to every charged fixed-\(b\)
> trial and its prefixes, and if exact duplicate recovery plus all rank,
> index, orientation, and certificate conditions are included in the same
> success event, then expected work is
> \(\Omega(Nd/(r+1))=N^{1-o(1)}\), with no asymptotic advantage over rho or
> BSGS.

Failure to prove that alignment leaves only this cost attribution
inconclusive. A semantic failure would reject only the affected
defect/signature interface. Neither outcome is a lower bound against other
nonlinear zero-minor locators, coordinate-sensitive representations, or
ECDLP algorithms.

## Sources

- Ayan Mahalanobis, “A Guess and Determine Attack on the Elliptic Curve
  Discrete Logarithm Problem,” arXiv:2607.09814v1 (2026), especially Sections
  4.1, 5, 5.2, 6, 8 and Algorithms 1--3:
  <https://arxiv.org/html/2607.09814v1>.
- Ayan Mahalanobis and Vivek Mallick, “A Las Vegas algorithm to solve the
  elliptic curve discrete logarithm problem,” IACR ePrint 2018/134,
  INDOCRYPT 2018: <https://eprint.iacr.org/2018/134>.
- Ansari Abdullah and Ayan Mahalanobis, “Minors solve the elliptic curve
  discrete logarithm problem,” arXiv:2310.04132v1 (2023):
  <https://arxiv.org/html/2310.04132v1>.
