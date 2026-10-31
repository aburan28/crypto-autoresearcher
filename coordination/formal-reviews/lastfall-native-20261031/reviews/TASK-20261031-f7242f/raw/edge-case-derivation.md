# Source correspondence checks, independently derived

All calculations take place in k[x] for an arbitrary field k. V_i means the least k-subspace containing generators of degree at most i and closed under products whose resulting degree budget is at most i, as in Caminata-Gorla Definition 1.5 (printed page 6). No computer algebra or Lean run was performed.

## General two-inequality check

For any finite polynomial representation f = sum_j q_j F_j, choose i at least every deg(q_j F_j). Each F_j lies in V_i and the closure rule admits multiplication by q_j; hence f lies in V_i and d_f exists. If d_F is finite, the definition gives f in V_{max(d_F,deg f)}. For any fall d_f>deg f, d_F<d_f would imply max(d_F,deg f)<d_f, impossible by minimality of d_f. Thus each fall degree is at most d_F. A nonempty set of natural fall degrees bounded by d_F has a maximum mu. For any f in the ideal, either d_f>deg f, so d_f<=mu and f lies in V_{max(mu,deg f)}, or d_f=deg f, and the same membership follows by monotonicity of V_i. Thus d_F<=mu. These give equality. This proof does not require F finite once d_F is explicitly assumed finite.

## Empty F

The ideal is {0}; every V_i is {0}. Under the target's natural-number degree convention, d_0=deg(0)=0, so there is no fall and d_F=0. The fall premise is false. The source calls F a finite polynomial system and does not explicitly discuss the empty system; its Theorem 2.8 is conditional and makes no assertion of a maximum for an empty fall set.

## F={x}

The ideal is (x). Every nonzero f=xq has deg f=deg q+1. The generator x is present at degree 1 and closure admits q at budget deg f, so f lies in V_{deg f}. Hence d_f=deg f, there is no fall, and d_F=0. The fall premise is false, consistent with the source's Lemma 2.7 (printed page 9).

## Actual fall: F={x^2, x^2+x}

There are no generators of degree below 2, so V_0=V_1={0}. At degree 2, both generators enter, and their difference is x; hence x lies in V_2 but not V_1, giving d_x=2>deg x=1. Conversely every f in the ideal (x) with deg f>=2 is xq with deg q=deg f-1. Since x is in V_2, closure gives xq in V_{deg f}; the degree-1 element x is in V_2. Therefore d_F<=2. The fall in x forces d_F>=2, so d_F=2 and the maximum fall degree is 2. The argument works in every characteristic because (x^2+x)-x^2=x.

## Wording check

The printed proof of Theorem 2.8 (page 9) begins its first inequality with f in F, but the displayed supremum and theorem range over f in (F). The derivation above uses f in (F); this appears to be a local wording slip in the proof, not a different quantified theorem. The source's finiteness of d_F is stated immediately after Definition 1.5 (page 6) as a consequence of a Groebner basis; the target makes finiteness an explicit hypothesis.
