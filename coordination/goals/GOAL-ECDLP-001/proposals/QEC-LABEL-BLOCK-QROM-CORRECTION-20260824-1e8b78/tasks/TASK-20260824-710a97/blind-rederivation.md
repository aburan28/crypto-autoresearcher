# Blind re-derivation: label-block qROM translation

## Scope and notation

This is an abstract derivation from the frozen statement. It does not inspect or compare any producer implementation or result. Let

- \(l=(a,s)\) be the unchanged address/sign label;
- \(R\) be the data register;
- \(A_l=A(l)\) be the selected qROM record;
- \(T_l=T_{A(l)}\) be the total signed translation selected by \(l\);
- \(Q,C,E,M,W\) be, respectively, qROM-record, comparison, exceptional-mask, mux/routing, and arithmetic work registers.

Every arithmetic body below is required to be a total reversible permutation on computational-basis states. Its generic and exceptional cases partition the relevant code-space inputs and implement the same total map \(T_l\) on their respective domains.

## 1. Basis permutation and unitary extension

Implement the qROM load as an XOR load

\[
L:\ |l\rangle|q\rangle_Q\longmapsto |l\rangle|q\oplus A_l\rangle_Q.
\]

For every fixed \(l\), \(L\) is a permutation, with \(L^{-1}=L\) for an XOR realization. Reversible comparison, mask computation, controlled generic arithmetic, controlled exceptional muxing, work cleanup, and the inverse load are also basis permutations. Their composition is therefore a basis permutation on the full register space, not merely on the clean-work subspace. A permutation matrix is unitary, so linear extension gives a unitary.

On the clean-work subspace, the required action is

\[
|l\rangle|R\rangle|0\rangle_{QCE MW}
\longmapsto
|l\rangle|T_l(R)\rangle|0\rangle_{QCE MW}.
\]

The label is never a target. Consequently the invariant label subspaces
\(\mathcal H_l=\operatorname{span}\{|l\rangle\}\otimes\mathcal H_R\)
are mutually orthogonal and preserved, and the induced clean-work unitary is

\[
U=\bigoplus_l T_l
 =\sum_l |l\rangle\!\langle l|\otimes T_{A(l)}.
\]

## 2. Exactly one load, use, and inverse unload

Within block \(l\), the sequence is:

1. Load exactly one record: \(Q:0\mapsto A_l\).
2. Reversibly compute comparison bits and a one-hot case selector \(e_l(R)\). The generic selector and the exceptional selectors form a disjoint, exhaustive partition, so their Hamming weight is exactly one on each enabled code-space input.
3. Apply the generic core when the generic selector is one, or the exceptional mux when exactly one exceptional selector is one. Because the selectors are disjoint, precisely one body is active. Its action is \(R\mapsto T_l(R)\).
4. Clear arithmetic and mux-routing work while the record and the required selectors remain live.
5. Clear the input-dependent comparison/exception information using the transported predicate described below.
6. Apply the exact inverse qROM load to the unchanged record: \(|l,A_l\rangle_Q\mapsto|l,0\rangle_Q\).

Thus there is one selected-record load, one active translation body, and one inverse unload. The inverse unload succeeds only because the exact same \(A_l\) remains live and unmodified throughout the use.

## 3. R-dependent exception-mask transport and cleanup

Let the pre-translation one-hot mask be

\[
\mu=e_l(R_{\rm in}),\qquad R_{\rm out}=T_l(R_{\rm in}).
\]

Naively rerunning the original comparison on \(R_{\rm out}\) need not clear \(\mu\), because the comparison was defined on the input. Since \(T_l\) is a permutation, the correct post-translation pullback predicate is well defined:

\[
\bar e_l(R_{\rm out})
=e_l(T_l^{-1}(R_{\rm out}))
=e_l(R_{\rm in})=\mu.
\]

After the selected body has finished and its local arithmetic work is zero, XOR-evaluating \(\bar e_l(R_{\rm out})\) into the stored mask sends \(\mu\mapsto\mu\oplus\bar e_l(R_{\rm out})=0\). Any scratch used to evaluate the pullback is then reversed. This is the required \(R\)-dependent mask transport: it transports the *meaning* of the input case predicate through \(T_l\), rather than assuming input and output predicates coincide.

An equivalent implementation may use a reversible case-transport map \(\tau_l\), but it must establish the identity
\(\tau_l(R_{\rm out},e_l(R_{\rm in}))=e_l(T_l^{-1}(R_{\rm out}))\)
on every code-space block and reverse all transport scratch. Merely recomputing \(e_l(R_{\rm out})\) is valid only in the special case that \(e_l\circ T_l=e_l\).

This cleanup does not require saving an \(n\)-bit copy of \(R_{\rm in}\) if the pullback predicate is evaluated reversibly in place or streamed from \(R_{\rm out}\) and \(A_l\) with sublinear scratch. Materializing \(T_l^{-1}(R_{\rm out})\) in a separate \(n\)-bit register would create the hidden register addressed in Section 7.

## 4. Equal-payload aliases and phase preservation

The direct-sum control is the label projector \(|l\rangle\!\langle l|\), not a loop over distinct payload values. If \(A(l_1)=A(l_2)=A\) with \(l_1\ne l_2\), then

\[
\alpha|l_1,R\rangle+\beta|l_2,R\rangle
\longmapsto
\alpha|l_1,T_A(R)\rangle+\beta|l_2,T_A(R)\rangle.
\]

Each branch lies in exactly one label block, so equality of payloads changes neither the number of active blocks per branch nor the translation multiplicity. It therefore cannot cause a second translation.

For the positive alias control, the abstract action is exactly

\[
\alpha|2,0,R\rangle+\beta|3,1,R\rangle
\longmapsto
\alpha|2,0,R+3A\rangle+\beta|3,1,R+3A\rangle.
\]

For the mirror-negative control, it is exactly

\[
\alpha|2,1,R\rangle+\beta|3,0,R\rangle
\longmapsto
\alpha|2,1,R-3A\rangle+\beta|3,0,R-3A\rangle.
\]

In both cases labels are unchanged, exactly one signed translation acts per branch, and all work ends at zero. X, CX, and MCX are permutation matrices with unit entries, so they introduce no branch-dependent phase. Linearity therefore preserves \(\alpha\), \(\beta\), and their relative phase.

A payload-row iterator that emits one translation for every label row matching a payload fails this control: an alias branch matches multiple equal-payload rows and is translated multiple times. The label-block direct sum avoids that failure because each basis label activates one and only one projector.

## 5. Exact liveness intervals

Use the following ordered boundaries:

- \(t_0\): clean entry;
- \(t_1\): qROM record loaded;
- \(t_2\): comparisons and exception mask computed;
- \(t_3\): mux/routing selectors prepared;
- \(t_4\): selected translation completed and arithmetic-local work reversed;
- \(t_5\): mux/routing work reversed;
- \(t_6\): pullback comparison completed and stored comparison/exception mask cleared;
- \(t_7\): pullback scratch reversed;
- \(t_8\): inverse qROM unload completed.

With half-open intervals, the required work is live as follows:

| Work | Exact live interval | Width |
|---|---:|---:|
| qROM record \(Q\) | \([t_1,t_8)\) | \(q(n,w)\) |
| original comparison \(C\) | \([t_2,t_6)\) | \(c(n,w)\) |
| exceptional mask \(E\) | \([t_2,t_6)\) | \(e(n,w)\) |
| mux/routing \(M\) | \([t_3,t_5)\) | \(m(n,w)\) |
| arithmetic-local \(W\) | \([t_3,t_4)\) | \(a_b(n,w)\), where \(b\) is the uniquely active generic or exceptional body |
| pullback cleanup scratch \(P\) | \([t_5,t_7)\) | \(p(n,w)\) |

The dependency order is essential: arithmetic-local work clears before its selector; mux work clears while routing selectors remain available; the input-dependent selector clears only after the output-dependent pullback is available; pullback scratch clears before the qROM record is unloaded; and the record unloads last. At \(t_8\), \(Q=C=E=M=W=P=0\).

## 6. Symbolic gate, primitive, and ancilla accounting

For gate kind \(g\in\{X,CX,MCX_k\}\), define:

- \(Q_g(n,w)\): gates in the forward qROM load;
- \(C_{j,g,\sigma}(n,w)\): gates for comparison \(j\) with control-polarity word \(\sigma\); summing over every \(\sigma\) records all polarities;
- \(S_g,E_g,M_g,P_g\): selector, exception-mask, mux/routing, and pullback-cleanup gates;
- \(G_g\) and \(X_g\): gates in the controlled generic and controlled exceptional circuit bodies;
- \(H_g\): any remaining declared reversible housekeeping.

The exact static circuit count, once those component counts are supplied, is

\[
N_g
=2Q_g
+\sum_j\sum_{\sigma} C_{j,g,\sigma}
+S_g+E_g+M_g+P_g+G_g+X_g+H_g
+272\,\mathbf 1[g=MCX_{18}].
\]

The factor \(2Q_g\) is exact because the unload is the exact inverse and has the same gate multiset. The fixed layer contributes exactly 272 MCX operations with 18 controls, or an explicitly proved equivalent whose expansion must replace that term without double counting. The remaining MCX count is the arity-indexed family \(N_{MCX_k}\) for \(k\ne18\), plus all nonfixed 18-control terms already named above. Control-polarity X gates are counted in the corresponding \(C_{j,X,\sigma}\), so negative controls cannot be silently omitted.

Static gate count and active semantic multiplicity are distinct. A reversible circuit may contain both controlled branch bodies, so both \(G_g\) and \(X_g\) occur in the netlist count. On a basis branch, however, the one-hot selector makes the active translation-body multiplicity exactly

\[
I_{\rm generic}(l,R)+I_{\rm exceptional}(l,R)=1.
\]

Primitive invocation accounting is therefore: one forward qROM load, one inverse unload, one comparison/selector computation with exact cleanup, one mask transport/cleanup, and exactly one active generic core or exceptional mux per enabled label block.

For ancillae, let superscripts \(c,d\) denote clean and dirty widths. Under the displayed schedule and an explicitly proved reuse of the generic and exceptional body workspace, define

\[
b^c=\max(a_G^c,a_X^c,a_{18}^c),\qquad
b^d=\max(a_G^d,a_X^d,a_{18}^d).
\]

Then the exact peak for disjoint concurrently-live work pools is

\[
A_{\rm clean}^{\rm peak}
=\max\{q^c,\ q^c+c^c+e^c,\ q^c+c^c+e^c+m^c+b^c,\ q^c+c^c+e^c+p^c\},
\]

\[
A_{\rm dirty}^{\rm peak}
=\max\{q^d,\ q^d+c^d+e^d,\ q^d+c^d+e^d+m^d+b^d,\ q^d+c^d+e^d+p^d\}.
\]

If mux work survives into pullback cleanup, add \(m^{c,d}\) to the last term. If work pools alias, an alias/restoration proof may reduce the sum; without such a proof the disjoint-pool formula is the admissible count. Treating MCX as a primitive gives \(a_{18}^c=a_{18}^d=0\); decomposing it requires the decomposition's ancilla width and gate expansion to be inserted explicitly.

The frozen statement provides the fixed 272-operation layer and the structural multiplicities, but it does not provide the component functions above. No further numeric X, CX, remaining-MCX, or absolute ancilla coefficient follows from the blind data alone.

## 7. Scalable peak width and the hidden-register condition

Let the declared persistent state have width

\[
B(n,w)=3n+\lambda(w)+O(\log n),
\]

and let \(A_{\rm extra}^{\rm peak}(n,w)\) be the physical extra width obtained from the clean peak above plus any dirty registers that are not borrowed from, and restored to, the declared persistent state. Then

\[
W_{\rm peak}(n,w)=B(n,w)+A_{\rm extra}^{\rm peak}(n,w).
\]

The leading form \(3n+O(\log n)\) is preserved exactly under these conditions:

1. \(w=O(\log n)\) and every simultaneously live extra pool in the max formula is \(O(w+\log n)\); or any wider pool is provably an alias of one of the three already-counted \(n\)-bit lanes and is restored before that lane is needed again.
2. The selected record \(Q\) is either \(O(w+\log n)\), already included in the three-lane baseline, or streamed/aliased reversibly. A separately allocated \(q(n,w)=\Theta(n)\) qROM record is an additional hidden \(n\)-bit register.
3. The pullback predicate \(e_l(T_l^{-1}(R_{\rm out}))\) is evaluated in place or with \(O(w+\log n)\) scratch. Saving \(R_{\rm in}\), or materializing a separate \(T_l^{-1}(R_{\rm out})\), uses another \(n\)-bit register.
4. Generic and exceptional body workspaces are time-multiplexed only with a proved restoration/alias schedule; otherwise both allocations must be counted.

Equivalently, no hidden linear-width register appears iff every extra \(\Theta(n)\) live object is injectively assigned to an already-counted persistent lane with compatible liveness and restoration. If any independent extra pool has width \(\gamma n+o(n)\) for \(\gamma>0\), the leading coefficient becomes at least \(3+\gamma\). The abstract statement does not specify \(q,c,e,m,a_b,p\) or the baseline alias map, so it establishes this condition but does not establish that a concrete construction meets it.

## 8. Known-false reasoning controls

- Payload-row iteration fails the equal-payload controls by applying a translation once per matching row rather than once per label block.
- A no-op backend fails every block with nonidentity \(T_l\).
- A procedure that chooses one classical label does not define the coherent direct sum on a label superposition. A fixed reversible circuit controlled by quantum label bits does.
- Omitting the inverse unload leaves \(Q=A_l\) correlated with the label and violates final cleanup.
- Canonicalizing distinct labels with equal payload is noninjective unless the discarded label is retained; it changes labels or destroys coherence.
- A partial generic or exceptional arithmetic body is not a total permutation implementing \(T_l\) on every code-space block and therefore fails at least one block.

These controls delimit the abstract derivation only. They are not observations about any implementation.
