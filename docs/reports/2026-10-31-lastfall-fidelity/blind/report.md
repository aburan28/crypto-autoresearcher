# Blind derivation: last fall degree and finite degree profiles

Date: 2026-10-31. Reviewer task: T-1107. Base: `2b0cfe1401831c9493cfe047a515955f38d037b8`.

**Derived result.** Under the supplied assumptions, the last fall degree is the greatest first-membership degree among strict falls:

\[
d_F=\max\{d_f:f\in(F),\ d_f>\deg f\}.
\]

The equality holds for the actual spaces in the question. An exact finite profile can certify the fall thresholds within its covered degrees. Equating its largest observed fall with the global last fall degree additionally needs a justified upper bound or an equivalent completion certificate. The counterexamples below make that missing implication precise.

The mathematical statement alone was the scientific input. Producer code, target YAML, research notes, historical receipts, the review plan, and sibling reports were not read. This report is an independent derivation, not a review of the producer's Lean declaration or any actual measured matrix.

## 1. Definitions and elementary consequences

Let `k` be a field, `R=k[x_1,...,x_n]`, `I=(F)`, and let `V_i=V_{F,i}` be the smallest `k`-subspace containing every generator of degree at most `i` and closed under the multiplication rule in the task. Indices are nonnegative integers. The zero polynomial belongs to every `V_i`; it creates no positive strict fall under the usual zero-degree conventions and is handled separately below.

The following properties follow from the definition, rather than being extra assumptions:

1. **Containment:** `V_i` is contained in `I ∩ R_{≤i}`. That intersection is itself an admissible subspace in the definition of `V_i`.
2. **Monotonicity:** `V_i ⊆ V_j` for `i≤j`. The space `V_j` contains the required generators for `V_i` and is closed under every multiplication permitted at cap `i`.
3. **Exhaustion:** every `h∈I` belongs to some `V_i`. Write `h` as a finite sum `Σ a_j f_j`; any cap at least all `deg(a_j)+deg(f_j)` admits each product, hence their sum. This also works if the generating set is infinite, since an ideal representation uses finitely many generators.
4. Consequently every nonzero `h∈I` has a first membership index `d_h`, with `d_h≥deg h`; and `h∈V_i` holds exactly when `d_h≤i`.

The supplied finiteness of `d_F` supplies a global bound on falls. It is not needed merely to define each individual `d_h` for `h∈I`.

## 2. Independent proof of the equality

Write `d=d_F` and let

\[
S=\{d_h:h\in I,\ d_h>\deg h\}.
\]

The question assumes `S` is nonempty. For any strict fall `h`, the defining property of `d` gives

\[
d_h\leq \max(d,\deg h).
\]

If `d_h>d`, both `d` and `deg h` would be strictly less than `d_h`, contradicting that inequality. Therefore every member of `S` is at most `d`. A nonempty bounded subset of the nonnegative integers has a maximum; put `M=max S`. We have `M≤d`.

For an arbitrary nonzero `h∈I`, either `h` is a strict fall, in which case `d_h≤M`, or it is not, in which case `d_h≤deg h`. In either case

\[
d_h\leq\max(M,\deg h).
\]

Monotonicity gives `h∈V_{max(M,deg h)}`. The same membership holds for zero because every `V_i` is a vector space. Thus `M` satisfies the global defining property for `d_F`. Minimality gives `d≤M`. Combining the inequalities proves `d_F=M`.

**A second direct check of attainment.** The existence of a strict fall implies `d≥1`. Since `d-1` does not satisfy the global defining property, there is `h∈I` with `h∉V_{max(d-1,deg h)}`. This witness is nonzero. If `deg h≥d`, the defining membership at `d` would put it in that same space, a contradiction. Hence `deg h≤d-1`; we have `h∉V_{d-1}` and `h∈V_d`. Therefore `d_h=d>deg h`. This checks that the maximum is attained, not merely a supremum.

## 3. What an exact finite profile certifies

For an integer `i≥1`, define the quotient

\[
Q_i=\frac{V_i\cap R_{\leq i-1}}{V_{i-1}}.
\]

The denominator is a subspace of the numerator by containment and monotonicity. The following equivalence is exact:

\[
Q_i\neq0
\quad\Longleftrightarrow\quad
\exists h\in I:\ d_h=i>\deg h.
\]

Indeed, a nonzero quotient class has a representative of degree at most `i-1` lying in `V_i` but not `V_{i-1}`. Conversely every fall with first membership at `i` gives such a class.

Consequently a complete computation of these spaces through cap `B` determines all fall thresholds at most `B`. If any exist, it determines

\[
M_B=\max\{i\leq B:Q_i\neq0\}\leq d_F.
\]

This is a certified lower bound on `d_F`, conditional on exact identification of the computed spaces with `V_i`. It is not an upper bound. If there are no observed falls, the profile certifies only the absence of falls at indices at most `B`. In a no-fall system the literal maximum of the empty set is undefined; a convention such as returning zero must be stated.

### 3.1 Which ranks are needed

Let `π_i` take the homogeneous part of total degree `i` of a polynomial in `V_i`. Then

\[
\dim Q_i=\dim V_i-\operatorname{rank}(\pi_i|_{V_i})-\dim V_{i-1}.
\]

Thus a rank profile can detect these local falls if it contains enough exact rank information to recover both the whole-space rank and the top-degree projection rank. A single total row rank per cap, or a raw increase in that rank, is not itself this quotient statistic. For example, `F={x}` has `dim V_i=i` for `i≥1`, yet it has no strict falls: all increases come from ordinary new multiples.

### 3.2 Bridges required for a measured profile

A claim about an actual finite matrix computation needs each of the following separately:

- **Algebra and input binding:** the matrix uses the specified field, variables, total-degree convention, full input generators, and the same cap convention as `V_i`.
- **Exact closure:** its row space equals `V_i`. Rows must include the effects of taking linear combinations that lower degree and then multiplying those newly available polynomials. A one-pass span of bounded generator multiples can be smaller.
- **Exact rank and membership:** ranks and the nonmembership needed to locate first membership must be justified over the stated field. Merely finding a polynomial at cap `i` proves `d_h≤i`, not `d_h=i`.
- **Local fall statistic:** recover the quotient above, or provide equivalent membership and nonmembership witnesses. Total ranks alone need an additional argument.
- **Cutoff completion:** justify the absence of all falls after `B` before identifying `M_B` with `d_F`.

An established bound `d_F≤B`, combined with the exact profile through `B` and the nonempty-fall assumption, is sufficient for the last item. An independently checked global invariant proving the defining property at `M_B` is also sufficient. Several consecutive degrees with no new falls do not supply such a certificate on their own.

No measured matrix, computation trace, field instance, or cutoff certificate was supplied to this blind reviewer. The application of these conditions to any particular existing measurement is therefore **inconclusive** in this report.

## 4. Exact controls

All control outcomes in this section are algebraically derived for every field. They are not sampled benchmark results.

### 4.1 Requested one-variable family

For `D≥2`, let `F_D={x^D,x^D+x}` in `k[x]`. Its ideal is `(x)`, since subtracting the generators gives `x` and both generators are divisible by `x`. The exact spaces are

\[
V_{F_D,i}=\begin{cases}
0,&i<D,\\
\operatorname{span}_k(x,x^2,\ldots,x^i),&i\geq D.
\end{cases}
\]

Below `D`, no generator is admitted. At cap `D`, their difference supplies `x`; the closure rule then supplies every `x^j` for `1≤j≤D`. At a larger cap the same argument supplies every positive-degree monomial up to that cap. Containment in `(x)∩R_{≤i}` gives the reverse inclusion.

Every nonzero `h∈(x)` consequently has

\[
d_h=\max(D,\deg h),\qquad d_{F_D}=D.
\]

The falls are exactly the nonzero polynomials of degree below `D`, and all have first membership `D`. In particular, `d_x=D`.

Replacing `D` by `D+1` proves `d_{F_{D+1}}=D+1`. The two systems have identical exact profiles through cap `D-1` (all zero), and their profiles first differ at cap `D`. These examples refute inference from a cutoff preceding the next fall. They do **not** have equal profiles through cap `D`; claiming that would be an indexing error.

### 4.2 Identical profiles with a visible early fall

Fix an observed cutoff `B≥2` and any integer `N>B`. In `k[x,y]`, set

\[
G_N=\{x^2,x^2+x,x^N,x^N+x\},\qquad
H_N=\{x^2,x^2+x,y^N,y^N+y\}.
\]

Both systems have four distinct generators and the same generator-degree multiset `{2,2,N,N}`. For every `i≤B`, neither degree-`N` pair is admitted, so the exact spaces coincide. More explicitly,

\[
V_{G_N,i}=\begin{cases}0&i<2,\\(x)\cap R_{\leq i}&i\geq2,\end{cases}
\]

and

\[
V_{H_N,i}=\begin{cases}
0&i<2,\\
(x)\cap R_{\leq i}&2\leq i<N,\\
(x,y)\cap R_{\leq i}&i\geq N.
\end{cases}
\]

The difference `x` is available at cap 2 in both systems. In `G_N` it generates every ideal element at cap `max(2,deg h)`; the higher generators add nothing. In `H_N`, the new difference `y` first becomes available at cap `N`, after which the closure rule generates every nonconstant monomial through the cap. Therefore

\[
d_{G_N}=2,\qquad d_{H_N}=N.
\]

Both profiles have an observed fall at 2 and no further falls through `B`, with exactly the same spaces, ranks, and local fall quotients throughout the observed range. Nevertheless their global last fall degrees differ, and `N` can be arbitrarily large relative to `B`. Equal generator degrees do not remove the ambiguity. This proves the unrestricted finite-profile inference false without depending on an initially empty profile.

The dimensions for the illustration `B=4,N=6` are derived from these formulas: `(x)∩R_{≤i}` has dimension `i(i+1)/2`, and `(x,y)∩R_{≤i}` has dimension `(i+1)(i+2)/2-1`. See [the diagram](profile-control.svg).

### 4.3 A later fall can exceed the maximum generator degree

Let `K={x^2,xy-1}` in `k[x,y]`. At cap 2, `V_2=span{x^2,xy-1}`, which contains no nonzero polynomial of degree below 2. At cap 3, permitted products give

\[
y x^2-x(xy-1)=x.
\]

Once `x` is present, closure permits `xy`, so subtracting `xy-1` gives `1`. Thus `V_3=R_{≤3}`, and at every larger cap `V_i=R_{≤i}`. We have `d_1=3` and `d_K=3`, although every generator has degree 2. A rule that simply stops at the maximum generator degree fails this control.

### 4.4 One-pass Macaulay rows need not equal the defined closure

For `F_D` at cap `D`, a one-pass matrix containing only monomial multiples of the original generators with product degree at most `D` has row span

\[
\operatorname{span}\{x^D,x^D+x\}=\operatorname{span}\{x^D,x\}.
\]

For `D≥3`, that has dimension 2, whereas the true `V_D` has dimension `D`. The newly produced `x` must be multiplied within the same cap to get the missing powers. This is an exact counterexample to the unqualified identification of that one-pass row span with `V_D`.

The system `K` also exhibits the same issue at cap 3: the one-pass span of `x^2,x^3,x^2y,xy-1,x^2y-x,xy^2-y` contains `x` but not `1`. Its only row with a constant term also carries `xy`, which no other row can cancel. The actual `V_3` contains `1` by the additional closure step above.

### 4.5 Empty-fall boundary

For `F={x}`, every nonzero ideal element has `d_h=deg h`; there are no strict falls, and the global defining property holds already at `d=0`. Thus the nonempty-fall hypothesis is needed if the conclusion is literally a greatest element of the fall set. A maximum with an explicit default of zero is a different formulation.

## 5. Verdicts and next obligation

| Reviewed claim | Verdict | Supporting argument |
| --- | --- | --- |
| Finite `d_F` and at least one strict fall imply `d_F` is the greatest `d_h` of a strict fall | holds | Section 2, including attainment |
| Exact spaces through `B` identify the fall thresholds at most `B` | holds | Quotient criterion in Section 3 |
| Largest observed fall through an arbitrary finite cutoff equals `d_F` | breaks | `G_N,H_N` in Section 4.2 |
| Stopping at the maximum generator degree always suffices | breaks | `K={x^2,xy-1}` in Section 4.3 |
| One-pass bounded generator multiples always span `V_i` | breaks | Sections 4.4 and 4.1 |
| A particular existing measured profile establishes the global value | inconclusive | Its matrix-to-space and cutoff certificates were not supplied to this blind task |

The next concrete obligation for a measured result is to supply exact space/rank evidence and the claimed cutoff certificate for the same input system. The coordinator can compare those artifacts to the checklist in Section 3.2 without changing this independent mathematical verdict.

## 6. Scope, independence, and archival record

The scientific input was only the mathematical statement and example systems in the task. Operational instructions read were the review-evidence skill and its Lean-review reference; repository delivery and cloud-runtime skills, the networking reference, and the research-visuals skill; and `AGENTS.md` from the existing repository's `HEAD`. That `AGENTS.md` read included general historical examples unrelated to this theorem; none of the forbidden mathematical sources was opened. Git metadata and command help were consulted to create the isolated worktree and claim the task. No memory files, external mathematical sources, producer source files, producer reports, prior receipts, the review plan, or sibling reports were read.

The worktree uses a sparse checkout containing only root `AGENTS.md` and this report directory. It is based on the precommitted plan revision solely as an archival parent; the plan content was not read. Initially fetched `origin/main` was `199f3aaaa6d37d2fce59f4d8c8fe8d2eb8b50672`, an ancestor of this base. The pre-archive fetch observed an advance to `0c9dddeb6aaf1c36ac6cdb41c293233f9709b6fe`. The task's explicit base pin was retained; the coordinator will integrate this scoped report into its current branch. Conductor T-1107 was claimed at epoch 1; `conductor check` allowed this write scope. A later attempt to repeat `task claim` returned `task already claimed`; it did not renew the existing lease or create a second task.

No Lean build or theorem-source review was performed in this blind task. No scientific experiment, benchmark, or statistical measurement was run. The controls are exact algebraic derivations. The local visual is a derived view of Section 4.2 and is not a performance chart. No canonical graph was read or changed because this task's blind and write scopes restrict it to its own directory. The coordinator owns any shared graph reconciliation and the final review packet.

Companion files: [attestation](review_attestation.yaml), [diagram source/rendering](profile-control.svg), [PDF source](report.typ), and [rendered report](report.pdf).
