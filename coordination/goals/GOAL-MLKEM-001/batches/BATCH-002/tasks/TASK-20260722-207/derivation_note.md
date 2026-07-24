# Carry-aware LaMS–isometry derivation

Task: `TASK-20260722-207`  
Scope: symbolic and literature analysis only; no empirical run or official state transition  
Inference: requested `research-sol-max`; resolved `gpt-5.6-sol-xhigh`;
reasoning effort `xhigh`; fallback used; adapter `cursor-subagent-2026-07`

## Result

The BATCH-001 gate resolves negatively for the proposed new-information
mechanism. A negacyclic target orbit can use one LaMS vector pool when the
guess/dual partition is fixed, but the orbit attacks permuted and signed secret
coordinates. After candidate alignment, every orbit score is exactly a
weighted rotated-vector Fourier score on the original target. This is the
adjoint form of Wu–Xu's rotated-vector construction and the same-A
preprocessing reuse formalized by Ogilvie and Hou–Jiang.

Signed \(p\)-adic digits do have a precise layer action. It requires a
coefficient wrap bit and a carry/borrow state. Entrywise modulus switching also
has a known sign cocycle. These terms prevent the naive claim that digit
updates commute with rotation, but they do not create samples or information.
They only change candidate labels and Fourier weights. No non-equivalent
statistic or uncharged amortization survives.

Unlike the two BATCH-001 reviews, this task recovered and checked the full
LaMS paper, ePrint 2026/1326, including equations (6)–(9), Algorithms 1–2,
Theorems 2–3, and Table 1. What remains unavailable is a proof that its
independent-uniform LWE assumptions and sample choices transfer unchanged to
the block-negacyclic matrix and fixed sample supply of one passive FIPS 203
key.

## 1. Exact LaMS layer from the primary source

Let the flattened LWE relation be

\[
 b=A_Gs_G+A_Ds_D+e\pmod q,
\]

where \(G\) is the guessed coordinate set, \(D\) is the dual coordinate set,
\(|G|=g\), and \(A=[A_G\mid A_D]\). LaMS uses canonical representatives in
\(\{0,\ldots,q-1\}\), fixes a prime \(p<q\), and writes

\[
s_G=\sum_{r=0}^{\ell-1}p^r d_r,\qquad
d_r\in\mathbb Z_p^g,\qquad
\ell=\lceil\log_p q\rceil.
\]

At layer \(i\), assume the lower digits are correct and define

\[
c_i=\sum_{r<i}p^r d_r,\qquad
t_i=\frac{s_G-c_i}{p^i},\qquad
B_i=p^iA_G\pmod q.
\]

The source's layer target is

\[
b_i=b-A_Gc_i
   =B_it_i+A_Ds_D+e\pmod q. \tag{1}
\]

Thus recovering \(d_i=t_i\bmod p\) is another modulo-\(p\) recovery problem.
Define the entrywise switch and residual

\[
\widehat B_i=\frac qp\left\lfloor\frac pqB_i\right\rfloor,\qquad
\Delta_i=B_i-\widehat B_i,
\]

and the rational \(q\)-ary lattice

\[
L_i=L_q([\widehat B_i\mid\Delta_i\mid A_D]). \tag{2}
\]

LaMS's proof-separation condition is expressed using
\(\lambda_1(L_i)\). The reusable random vectors are not sampled from
\(L_i^\perp\). They are

\[
Z=(z_1,\ldots,z_N),\qquad
z_r\leftarrow D_{L_q^\perp(A_D),qs}. \tag{3}
\]

For

\[
\alpha_i(z)=\sum_{v\in\mathbb Z_q^g}
 \exp\!\left(-\frac{2\pi\mathrm i}{q}\langle\Delta_i v,z\rangle\right),
\]

the empirical source score is

\[
G_{Z,i}(x)=
\Re\left[
\frac1N\sum_{z\in Z}
\alpha_i(z)\exp\!\left(\frac{2\pi\mathrm i}{q}\langle x,z\rangle\right)
\right]. \tag{4}
\]

Algorithm 2 evaluates

\[
G_{Z,i}(b_i-\widehat B_i a),\qquad a\in\mathbb Z_p^g, \tag{5}
\]

and returns its maximizer. Algorithm 1 then updates

\[
c_{i+1}=c_i+p^i\widehat d_i. \tag{6}
\]

The unchanged \(A_D\) in (3), not equality among the \(L_i\), is why the paper
can reuse one literal list \(Z\) across all layers. The source additionally
shows equal determinants
\(\det L_i=p^{-g}q^{m-n}\) under its rank assumptions, but equal determinant
does not make the lattices equal.

For reference, the source gives

\[
T_{\rm total}=T_{\rm BKZ}
+N\,T_{\rm MCMC}(L_q^\perp(A_D),qs)
+\operatorname{poly}(m,n)\ell(N+p^g). \tag{7}
\]

With \(p=2\), Table 1 reports 191, 282, and 390 bits for
Kyber-512/768/1024. Those figures are 22, 31, and 41 bits below the paper's
corrected Qu–Xu comparator, not below Carrier, Li–Zheng, or the corrected
isometry-aware dual hybrid. They are not established in the same cost model as
the latter rows.

## 2. MLWE orbit and partitions

For

\[
R_q=\mathbb Z_q[X]/(X^n+1),\qquad
\mathbf b=\mathbf A\mathbf s+\mathbf e,
\]

let \(J_j\) be multiplication by \(X^j\) on each output polynomial and \(S_j\)
the corresponding action on each secret polynomial. Both are orthogonal signed
permutation matrices. The flattened block-negacyclic matrix satisfies

\[
J_j\bar A=\bar A S_j. \tag{8}
\]

Consequently

\[
J_j\bar b=\bar A(S_j\bar s)+J_j\bar e. \tag{9}
\]

The i.i.d. symmetric centered-binomial secret and error laws of ML-KEM are
preserved exactly. The orbit is nevertheless deterministic:

\[
I(s;b,\{J_jb\}_j\mid A)=I(s;b\mid A). \tag{10}
\]

There are two partition conventions, and they must not be conflated.

### Fixed partition

Keep the same coordinate selectors \(G,D\) after applying \(J_j\). Equation
(9) is

\[
J_jb=A_G(S_js)_G+A_D(S_js)_D+J_je.
\]

The literal matrices \(A_G,A_D\), each \(B_i,\widehat B_i,\Delta_i,L_i\),
and the list \(Z\) in (3) are unchanged. Pool validity is exact. In general,
however, \((S_js)_G\) comes from the original coordinate set
\(S_j^{-1}G\), so different orbit elements do not provide repeated
observations of one common digit vector. They provide coverage of different
signed/permuted coordinates. This is precisely the same-A isometry reuse
mechanism already used in hybrid attacks.

### Candidate-aligned partition

To make all orbit labels refer to one original coordinate set, move the
partition to

\[
G_j=S_j^{-1}G,\qquad D_j=S_j^{-1}D.
\]

The selected matrix blocks then change. If
\(z\in L_q^\perp(A_D)\), equation (8) sends it to an equal-norm vector
\(J_j^Tz\) in the dual lattice associated with \(D_j\). Therefore a rotated
pool is valid, but one unchanged literal pool is not justified unless \(G,D\)
are orbit-stable.

An orbit-stable choice is a union of whole polynomial blocks. In that case
there are signed permutations \(S_{j,G},S_{j,D}\) such that

\[
J_jA_G=A_GS_{j,G},\qquad
J_jA_D=A_DS_{j,D}. \tag{11}
\]

Then \(J_j^TZ\) has the same discrete-Gaussian law in
\(L_q^\perp(A_D)\). This establishes vector validity, but still does not
establish digitwise commutation.

## 3. Signed \(p\)-adic digits: exact wrap-and-carry action

The issue is canonical reduction modulo \(q\). Let \(S\) be any signed
permutation and let \(x,y\in\{0,\ldots,q-1\}^g\) satisfy

\[
y=[Sx]_q.
\]

There is a unique wrap vector \(\omega_S(x)\in\{0,1\}^g\) such that

\[
y=Sx+q\omega_S(x). \tag{12}
\]

For a positive row of \(S\), the corresponding wrap bit is zero. For a
negative row selecting \(x_k\), it is \(1\) exactly when \(x_k\ne0\).
This zero branch matters: \([-0]_q=0\), not \(q\).

Write

\[
x=c_i+p^it_i,\qquad
c_i=x\bmod p^i,\quad 0\le c_i<p^i.
\]

Define

\[
c_i'=(Sc_i+q\omega)\bmod p^i,\qquad
\kappa_i=\frac{Sc_i+q\omega-c_i'}{p^i}. \tag{13}
\]

Substitution into (12) gives the exact quotient invariant

\[
y=c_i'+p^i(St_i+\kappa_i),\qquad
t_i'=St_i+\kappa_i. \tag{14}
\]

Hence the next digit transforms as

\[
d_i'=t_i'\bmod p=(Sd_i+\kappa_i)\bmod p, \tag{15}
\]

and the prefix update remains

\[
c_{i+1}'=c_i'+p^id_i'. \tag{16}
\]

Equations (12)–(16) are the carry-aware multi-layer invariant. It is local in
the augmented state \((c_i,\omega,\kappa_i)\), not in \(d_i\) alone. The wrap
bit depends on whether the full canonical coefficient is zero. Therefore no
function of only the current digit can align a negative orbit coordinate.

The same fact can be written as ordinary base-\(p\) borrowing. If
\(q=\sum_rq_rp^r\), \(x=\sum_rd_rp^r\), and a negative output has wrap
bit \(\omega\), set \(\beta_0=0\) and solve

\[
q_r\omega-d_r-\beta_r=d_r'-p\beta_{r+1},
\qquad d_r'\in\{0,\ldots,p-1\}. \tag{17}
\]

Thus

\[
d_r'=(q_r\omega-d_r-\beta_r)\bmod p. \tag{18}
\]

For \(q=3329,p=2\), treating \(-1\) as digitwise negation fails:
the canonical residue \(3328\) and \(1\) are related by the complete borrow
chain (17), while zero follows the separate \(\omega=0\) branch.

Balanced signed digits do not remove this issue for the source algorithm.
LaMS's theorem and reconstruction use canonical \(\mathbb Z_p\) digits.
Replacing them by a redundant or balanced digit set would require a new
candidate space, uniqueness rule, score proof, and cost analysis. In
particular, base \(2\) has no nonredundant symmetric digit set.

## 4. Carry-aware target update

Assume the orbit-stable condition (11), and apply the preceding equations to
the guessed block. The transformed layer target is

\[
b_i'=Jb-A_Gc_i'. \tag{19}
\]

Using \(J A_G=A_GS_G\) and
\(S_Gc_i+q\omega-c_i'=p^i\kappa_i\),

\[
\begin{aligned}
b_i'
 &=J(b-A_Gc_i)+A_G(S_Gc_i-c_i')\\
 &=Jb_i+B_i\kappa_i\pmod q. \tag{20}
\end{aligned}
\]

Together with \(t_i'=S_Gt_i+\kappa_i\), equation (20) yields

\[
b_i'=B_it_i'+A_D(S_Ds_D)+Je\pmod q. \tag{21}
\]

So each correctly updated orbit state is a valid LaMS layer. It is not,
however, the naive rotation \(Jb_i\). If a lower digit is wrong, then \(c_i'\),
\(\kappa_i\), \(b_i'\), and all later labels are wrong. The LaMS union bound
assumes correct preceding layers; an orbit score supplies no recovery from
that branch error.

## 5. Modulus-switching sign cocycle

Even with an orbit-stable partition, entrywise modulus switching does not
commute with signs. For a canonical scalar \(x\in\{0,\ldots,q-1\}\), let

\[
\mathcal R_p(x)=\frac qp\left\lfloor\frac{px}{q}\right\rfloor,\qquad
\Delta_p(x)=x-\mathcal R_p(x).
\]

For \(x\ne0\), \(px/q\) is nonintegral because \(p\) and \(q\) are distinct
primes, and direct calculation gives

\[
\mathcal R_p(q-x)=q-\frac qp-\mathcal R_p(x),\qquad
\Delta_p(q-x)=\frac qp-\Delta_p(x). \tag{22}
\]

At \(x=0\), both switched value and residual are zero. Equation (22) is a
known, entrywise affine correction determined by the public matrix; it is not
secret information.

Suppose \(JB_i=B_iS_G\) and define the public rounding cocycle

\[
C_i=J\widehat B_i-\widehat B_iS_G,\qquad
C_i\equiv\Delta_iS_G-J\Delta_i\pmod q. \tag{23}
\]

For a candidate \(a\in\mathbb Z_p^g\), align it by

\[
a'=(S_Ga+\kappa_i)\bmod p.
\]

Let

\[
x_i(a)=b_i-\widehat B_i a,\qquad
x_i'(a')=b_i'-\widehat B_i a'.
\]

Since \(p\widehat B_i\) is an integer multiple of \(q\), equations (20) and
(23) give

\[
x_i'(a')=Jx_i(a)+\Delta_i\kappa_i+C_i a\pmod q. \tag{24}
\]

The pair \((\kappa_i,C_i)\) is the exact obstruction to strict layer
equivariance. A candidate-aligned orbit score therefore cannot be treated as
another identically distributed copy of the original candidate score. Any
common-mean GLS assumption would first have to include these phases.

## 6. Exact score identity

The obstruction (24) does not produce a new source of information. Apply
(4) directly. For any row signed permutation \(J\), any public/candidate shift
\(u\), and any layer,

\[
\begin{aligned}
G_{Z,i}(Jb-u)
 =\Re\frac1N\sum_{z\in Z}
 &\alpha_i(z)
 \exp\!\left(-\frac{2\pi\mathrm i}{q}\langle u,z\rangle\right)\\
 &{}\cdot
 \exp\!\left(\frac{2\pi\mathrm i}{q}\langle b,J^Tz\rangle\right).
\end{aligned} \tag{25}
\]

For a LaMS candidate,

\[
u=A_Gc_i'+\widehat B_i a'. \tag{26}
\]

Equation (25) is exact: it expresses the target-orbit score as a score on the
single original target \(b\), using the equal-norm vectors \(J^Tz\) and
attached complex weights

\[
w_{i,J,a',z}=
\alpha_i(z)
\exp\!\left(
-\frac{2\pi\mathrm i}{q}
\langle A_Gc_i'+\widehat B_i a',z\rangle
\right). \tag{27}
\]

Thus:

1. the raw LaMS score is a weighted Fourier score, not merely an unweighted
   cosine sum;
2. rotating the target is exactly adjoint to rotating its score vectors while
   retaining the attached weights;
3. carry and rounding corrections change (27), not the target information;
4. under the fixed partition, the original \(z\)'s remain valid because
   \(A_D\) is unchanged;
5. under candidate-aligned partitions, \(J^Tz\) is valid for the corresponding
   rotated dual lattice, and for orbit-stable partitions it remains in the
   same dual lattice.

Wu–Xu already derive equal-norm rotated short vectors and use their orbit in a
dual distinguisher. Ogilvie and Hou–Jiang already exploit the adjoint same-A
target view for hybrid preprocessing and coverage. Equation (25) is the
LaMS-weighted instance of those mechanisms. It is not a new sample-amplification
identity.

An arbitrary signed permutation is not a matched orbit control. It generally
fails \(JA=AS\), so it breaks the same-\(A\) MLWE relation. Such a transform
can serve only as a deliberately broken commutator negative, not as a
comparator measuring a ring-specific attack gain.

The modulus-switching cocycle means that (25) need not equal an independently
recomputed *ordinary* LaMS score for the original partition with all labels
discarded. That difference is not a surviving invariant: the exact weights
(27) retain it completely. Dropping the weights would define a different,
unproved statistic; retaining them gives rotated-vector relabeling.

## 7. Covariance and false positives

The orbit-score vector is a deterministic function of one \(b\), one public
matrix, and one vector pool. A large participation ratio

\[
\frac{(\operatorname{tr}\Sigma)^2}{\operatorname{tr}(\Sigma^2)}
\]

does not imply useful separation. Under a common-covariance Gaussian model,
the relevant linear quantity would instead be

\[
(\mu_{\rm correct}-\mu_{\rm wrong})^T
\Sigma^{-1}
(\mu_{\rm correct}-\mu_{\rm wrong}), \tag{28}
\]

and even (28) does not establish the maximum-score tail over candidates,
layers, orbit choices, and retries.

Covariance-based score prediction is itself prior art: ePrint 2026/1048 covers
original, modulus-switched, and decoded dual attacks and extends wrong-score
tail modeling. Ducas–Pulles additionally show why the target norm and shared
target invalidate simple independence. Equations (24) and (27) also show that
the correct mean direction need not be the all-ones direction required by the
BATCH-001 GLS proposal.

## 8. Cost consequence

Let the baseline total cost be \(S+U\), where only \(S\) is affected by an
orbit optimization, let \(f\) be its reduction factor, and let \(H\ge0\) be
new overhead. A two-bit total improvement requires

\[
\frac Sf+U+H\le\frac{S+U}{4}. \tag{29}
\]

At \(f=4\), equation (29) cannot hold for positive \(U\) or \(H\). More
importantly, the orbit identity does not reduce the cost of producing the
LaMS list (3). It only reuses or relabels that list. Li–Zheng 2026/1400
independently reports that short-vector sampling remains the dominant term
when FFT and decoding subcosts are reduced.

The corrected Hou–Jiang isometric `CC` values are 139.1, 194.7, and 259.0
bits. Li–Zheng reports 139.20, 194.02, and 259.40 in its `CC` model. LaMS
reports 191, 282, and 390 bits in a different provable-dual estimate. These
figures cannot be subtracted across models, but they supply no present path
to an additional two-bit gain below the matched lower envelope.

## 9. Broader structured-MLWE screen

The other requested mechanisms do not produce a survivor:

- Module-BKZ's asymptotic subexponential improvement requires
  \(|\Delta_K|<d^d\). For ML-KEM's power-of-two cyclotomic field,
  ePrint 2025/1904 instead predicts a \(d-1+o(1)\) blocksize loss for equal
  slope. EPrint 2025/2195 finds a possible finite-tour convergence effect,
  but no pinned full ML-KEM cost below matched BKZ.
- Subfield, subring, trace, evaluation, and Ring-BKW attacks require favorable
  projected errors, NTRU norm structure, small evaluation roots, or samples
  restricted to multiplicative cosets of subrings. One passive ML-KEM key
  supplies no such sample distribution, and rotations are not fresh samples.
- Fast Slicer gives measured factor-\(\le5\) gains over primal at scaled LWE
  dimensions 160–210, including centered binomial errors, but supplies no
  new ring mechanism or standardized-parameter scaling certificate.
- The 2026 dual-enhanced resultant attack reduces algebraic estimates to
  724/967/1316 bits for Kyber-512/768/1024. This is a major improvement over
  its Gröbner comparators but remains noncompetitive with lattice attacks.
- NoMod already combines robust regression, saved reduced vectors, and
  automorphism amplification. Its reported Kyber-like results concern
  binary/sparse or reduced instances, not full standardized dense
  centered-binomial keys with matched attack costs.
- EPrint 2026/1400 already composes modulus switching and lossy coding;
  its total Kyber gain is modest. EPrint 2026/1048 already supplies the
  covariance analysis omitted by BATCH-001.
- The claimed polynomial quantum attack in arXiv:2605.17412 outputs a
  generator of a determinant ideal derived from a module basis. The output is
  unchanged as \(b=As+e\) and \(s\) vary with \(A\) fixed, and the checked
  source gives no map from that invariant to the MLWE secret. It is therefore
  not a credible key-recovery mechanism as written.

## 10. Narrow conclusion and optional check

The exact conclusion is scoped to the BATCH-001 composition:

- fixed-partition LaMS pool reuse is valid;
- digit alignment requires the wrap/carry recurrence (12)–(18);
- layer targets satisfy (20), not naive commutation;
- entrywise switching contributes the public cocycle (22)–(24);
- the complete score satisfies the weighted rotated-vector identity (25);
- no independent samples, non-equivalent statistic, or two-bit cost path is
  derived.

This does not declare all future p-adic, isometry-aware, or covariance-aware
MLWE attacks impossible.

If implementation assurance is desired, an exact \(n\in\{8,16\}\), \(p=2\)
check can enumerate signs, zero/nonzero wrap branches, all layers, and all
orbit elements. It should stop on the first mismatch in (13), (20), (22),
(24), (25), or the final residual. A bound of two core-hours, 1 GiB, and 64
instances is ample. Passing would verify transcription only; the symbolic
identity has already removed the proposed attack mechanism, so no empirical
research proposal is retained.

## Primary references

1. Wang, Wang, Zheng, Zhao, *LaMS*, IACR ePrint 2026/1326,
   <https://eprint.iacr.org/2026/1326>.
2. Qu, Xu, *On the Provable Dual Attack for LWE by Modulus Switching*,
   IACR ePrint 2025/859, <https://eprint.iacr.org/2025/859>.
3. Wu, Xu, *Enhancing the Dual Attack against MLWE*, IACR ePrint 2022/1661,
   <https://eprint.iacr.org/2022/1661>.
4. Ogilvie, *On the Concrete Hardness Gap Between MLWE and LWE*,
   IACR ePrint 2026/279, <https://eprint.iacr.org/2026/279>.
5. Hou, Jiang, *Careful with the Ring*, IACR ePrint 2026/366,
   <https://eprint.iacr.org/2026/366>.
6. Li, Zheng, *Unified Dual Attack Analyses*, IACR ePrint 2026/1048,
   <https://eprint.iacr.org/2026/1048>.
7. Li, Zheng, *What Happens When integrating Modulus Switching and Lossy
   Source Coding*, IACR ePrint 2026/1400,
   <https://eprint.iacr.org/2026/1400>.
8. Ducas, Engelberts, de Perthuis, *Predicting Module-Lattice Reduction*,
   IACR ePrint 2025/1904, <https://eprint.iacr.org/2025/1904>.
9. de Perthuis, Trenkić, *Refined Modelling of the Primal Attack, and
   Variants Against Module-Learning With Errors*, IACR ePrint 2025/2195,
   <https://eprint.iacr.org/2025/2195>.
10. Karenin, Kirshanova, May, Nowakowski, *Fast Slicer for Batch-CVP*,
    IACR ePrint 2025/1910, <https://eprint.iacr.org/2025/1910>.
11. Wang et al., *Too Far Behind?*, IACR ePrint 2026/688,
    <https://eprint.iacr.org/2026/688>.
12. Bassotto, Franch, Krček, Picek, *NoMod*, arXiv:2510.02162,
    <https://arxiv.org/abs/2510.02162>.
13. Stange, *Algebraic aspects of solving Ring-LWE*, IACR ePrint 2019/183,
    <https://eprint.iacr.org/2019/183>.
