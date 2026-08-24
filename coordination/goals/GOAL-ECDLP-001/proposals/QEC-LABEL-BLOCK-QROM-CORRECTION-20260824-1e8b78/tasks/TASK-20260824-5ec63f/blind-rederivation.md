# Blind re-derivation for TASK-20260824-5ec63f

## Boundary and notation

This is an abstract derivation from the standalone handoff and blind statement only. It does not inspect or compare any implementation, snapshot, queue, review-plan, packet, producer artifact, sibling report, message, or earlier blind derivation. It owns no review joint and gives no whole-claim verdict.

Let the unchanged label be `l = (address, sign)` in a finite label set `Lambda`, let `D` be the computational-basis data domain, and let `A_l = A(l)` be the signed record loaded for label `l`. For each label, assume the specified transformation `T_l := T_{A_l}` is a permutation of `D`. All work registers start at zero.

## Direct-sum permutation and unitarity

On computational-basis states, the cleaned construction has action

`F(l,R) = (l,T_l(R))`.

It is injective: if `F(l,R) = F(l',R')`, the unchanged first component gives `l=l'`, and the injectivity of `T_l` then gives `R=R'`. It is surjective with inverse

`F^{-1}(l,R') = (l,T_l^{-1}(R'))`.

Thus `F` is a permutation of the disjoint union of label blocks. Its linear extension is a unitary,

`U = sum_{l in Lambda} |l><l| tensor T_l`.

The projectors `|l><l|` are mutually orthogonal, so there is no cross-label mixing even when two labels have equal payloads. Equivalently,

`U^dagger U = sum_l |l><l| tensor (T_l^dagger T_l) = I`.

The underlying `X`, `CX`, and `MCX` gates are computational-basis permutations and introduce no branch-dependent phase. Therefore, for arbitrary amplitudes,

`sum_{l,R} gamma_{l,R}|l,R> -> sum_{l,R} gamma_{l,R}|l,T_l(R)>`,

with every label, amplitude, and relative phase unchanged.

## One load, exactly one selected use, and inverse unload

Let `L` be the qROM load,

`L: |l,R,0_P,0_q> -> |l,R,A_l,0_q>`,

where `P` is the payload register and `q` is qROM-local scratch. Let `S` be the coherent selected-use circuit,

`S: |l,R,A_l,0_s> -> |l,T_l(R),A_l,0_s>`.

Inside `S`, an exception bit `e_l(R)` enables the exceptional mux when it is one and enables the generic core with the opposite polarity when it is zero. Hence the pathwise invocation counts are

`N_generic(l,R) = 1-e_l(R)`, `N_exceptional(l,R) = e_l(R)`,

so `N_generic + N_exceptional = 1` on every basis branch. Both controlled blocks may be present in the static circuit, but exactly one is active on a given basis branch. The complete clean action is

`L^dagger S L: |l,R,0_P,0_W> -> |l,T_l(R),0_P,0_W>`.

There is one forward load, one selected generic-core-or-exceptional-mux use, and one exact inverse unload. There is no loop over payload values and no second selected use.

The unload is exact because the label and payload remain unchanged while `S` runs. In the gate basis, reversing the forward qROM gate list applies `L^dagger`; all `X`, `CX`, and `MCX` gates are self-inverse. It maps `|l,A_l>` back to `|l,0_P>` after every payload-dependent work bit has been cleared. It does not depend on the final value of `R`.

## Equal-payload aliases

Payload equality is not label equality. If `A_l=A_l'`, the two direct-sum blocks remain `|l><l| tensor T_A` and `|l'><l'| tensor T_A`; neither projector is removed or applied twice.

For the positive alias control,

`alpha|2,0,R> + beta|3,1,R>`

maps to

`alpha|2,0,R+3A> + beta|3,1,R+3A>`.

For the mirror-negative alias control,

`alpha|2,1,R> + beta|3,0,R>`

maps to

`alpha|2,1,R-3A> + beta|3,0,R-3A>`.

Each branch receives exactly one signed translation. The address/sign labels and the coefficients `alpha` and `beta`, including their relative phase, are unchanged, and all work registers finish at zero. Canonicalizing the two labels to one representative would instead alter the label subsystem and would not implement this direct sum.

## R-dependent exception-mask transport and cleanup

The exception predicate is evaluated on the input data: `e = e_l(R_in)`. A reversible input comparator first computes the predicate into temporary comparison work, copies the one-bit result to a persistent exception mask `E`, and reverses the comparator before `R` changes. The mask then controls the mutually exclusive generic and exceptional paths.

After the selected transformation, `R_out=T_l(R_in)`. Re-running the input predicate naively on `R_out` need not reproduce `e`; that would generally fail to clear `E`. The correct output-side predicate is the transported predicate

`e_l^out(R_out) := e_l(T_l^{-1}(R_out))`.

On a reachable output, `e_l^out(R_out)=e_l(R_in)=e`. A reversible output-side comparator computes `e_l^out(R_out)` into a temporary bit, XORs that bit into `E`, and uncomputes its own comparison work. Thus `E -> e xor e = 0` without changing `R_out`. This is a predicate transport, not an execution of `T_l^{-1}` followed by a second execution of `T_l`: the output-side predicate must be evaluated directly or by an equivalent streaming/in-place reversible circuit.

The effective controls derived from `E`, the label, and the payload are uncomputed while those inputs are still live. Generic arithmetic scratch and exceptional-mux scratch must each be returned to zero by their selected reversible block. Only then is the transported exception mask cleared, and only after that is `L^dagger` applied. Missing this order would leave some work correlated with `l` or `R`.

## Exact liveness schedule

The following half-open intervals refer to the stage boundaries shown. A register listed as live contains nonzero or logically required information; internal scratch is zero outside its interval.

| Stage interval | Operation | Live work after/beside the operation |
| --- | --- | --- |
| `[0,1)` | qROM forward load | qROM internal scratch only during the load |
| `[1,2)` | input predicate compute-copy-uncompute | payload `P`; input comparison scratch during this interval; exception mask `E` becomes live |
| `[2,3)` | prepare effective controls | `P`, `E`, effective-control/mux selector work |
| `[3,4)` | selected translation | `P`, `E`, effective controls; generic arithmetic work only on `e=0`, exceptional mux/arithmetic work only on `e=1`; the 272-operation 18-control layer is scheduled here |
| `[4,5)` | uncompute effective controls | `P`, `E`; selector work returns to zero |
| `[5,6)` | output-predicate transport and XOR cleanup | `P`, `E`, output comparison scratch; output scratch and then `E` return to zero |
| `[6,7)` | exact inverse qROM unload | `P` and qROM internal scratch only during unload; both return to zero |

Equivalently, the payload is live from completion of the forward load through the start of inverse unload; qROM-local scratch is live only in `[0,1)` and `[6,7)`; comparison scratch is live only in `[1,2)` and `[5,6)`; the exception mask is live from its copy in `[1,2)` until its XOR cleanup in `[5,6)`; selector/mux-control work is live in `[2,5)`; and path-specific arithmetic or exceptional-mux scratch is live only in `[3,4)`.

## Symbolic gate accounting

For a component `J`, define the fully expanded gate vector

`g_J(n,w) = (x_J, cx_J, {m_{J,k}}_{k>=2})`,

where `m_{J,k}` counts `k`-control `MCX` operations. The components are:

- `Q`: one forward qROM load; its exact inverse has the same vector because it is the reversed list of self-inverse gates.
- `C_in`: the full input-predicate compute-copy-uncompute sequence.
- `S_ctl`: effective-control preparation and cleanup.
- `G`: the statically present controlled generic core.
- `E_mux`: the statically present controlled exceptional mux.
- `C_out`: the full transported-output-predicate compute-XOR-uncompute sequence.
- `H_18`: the fixed layer `(0,0,{m_18=272, m_k=0 for k!=18})`.

The static circuit vector is therefore exactly

`g_total = 2 g_Q + g_C_in + g_S_ctl + g_G + g_E_mux + g_C_out + g_H_18`.

In particular,

`N_MCX(k) = 2m_Q,k + m_C_in,k + m_S_ctl,k + m_G,k + m_E_mux,k + m_C_out,k + 272*[k=18]`.

Thus the fixed layer contributes exactly 272 18-control `MCX` operations; any additional 18-control operations from named components remain visible in their symbolic terms. The qROM invocation count is exactly two: one load and one inverse unload. The logical selected-use count is exactly one per basis branch, as shown above.

All comparison control polarities must be expanded. If `I_J` is the number of maximal negative-polarity conjugation intervals in the chosen schedule for component `J`, then

`N_X = 2x_Q + x_C_in + x_S_ctl + x_G + x_E_mux + x_C_out + 2 sum_J I_J`,

`N_CX = 2cx_Q + cx_C_in + cx_S_ctl + cx_G + cx_E_mux + cx_C_out`.

With no sharing of adjacent polarity conjugations, `I_J` equals the sum, over every controlled gate in `J`, of its number of negative control literals. With sharing, it counts the actual maximal intervals, which prevents negative controls from being silently omitted or double-counted. The total high-level primitive count in the declared basis is

`N_primitive = N_X + N_CX + sum_{k>=2} N_MCX(k)`.

The two qROM calls are already expanded in `2g_Q` and must not be added again to `N_primitive`. The statement supplies no component vectors beyond `H_18`, so the formulas above are the exact symbolic totals; unstated numeric totals cannot be derived without an additional scientific input.

## Symbolic ancilla accounting and the hidden-register condition

Let the widths, all functions of `(n,w)`, be:

- `p`: payload register;
- `q_c,q_d`: clean/dirty qROM-local scratch peak;
- `c_in,c_out` and `d_in,d_out`: clean/dirty input/output comparison scratch peaks, including their temporary predicate bits;
- `b=1`: persistent exception mask;
- `u_c,u_d`: clean/dirty effective-control work;
- `a_G,c`, `a_G,d`: clean/dirty generic arithmetic scratch;
- `a_E,c`, `a_E,d`: clean/dirty exceptional arithmetic scratch;
- `m_E,c`, `m_E,d`: clean/dirty exceptional-mux scratch;
- `h_c,h_d`: clean/dirty scratch for the chosen realization of the 272-operation layer.

For the schedule above, the additional clean-ancilla peak is the maximum of

`p+q_c`, `p+b+c_in`, `p+b+u_c`,

`p+b+u_c+max(a_G,c, a_E,c+m_E,c)+h_c`,

`p+b+c_out`, and `p+q_c` for unload. The additional dirty-ancilla peak is the corresponding maximum of

`q_d`, `d_in`, `u_d`,

`u_d+max(a_G,d, a_E,d+m_E,d)+h_d`,

`d_out`, and `q_d`.

If forward and inverse qROM have different scratch realizations, replace the repeated `q_c,q_d` entries by their separate load/unload widths. The exact total-qubit peak is obtained stagewise by adding clean and dirty live widths after accounting for legal register reuse; independently maximizing clean and dirty widths and then summing can overestimate if their peaks occur at different stages.

Suppose the advertised base allocation consists of three counted `n`-bit banks plus logarithmic label/control storage. The leading width is `3n+O(log n)` if and only if the maximum live width not colorable into those three banks is `O(log n)` for the chosen `w=w(n)`. Concretely, every `Theta(n)` payload, arithmetic candidate, or mux candidate must reuse one of the three counted banks rather than coexist as a fourth bank; the qROM unload must reuse the original payload register; and the output-side exception predicate must be computable in place or by streaming with only `O(log n)` extra work.

In particular, retaining a copy of `R_in` solely to erase the R-dependent exception mask creates a hidden `n`-bit register and violates the condition. So does an unaccounted `Theta(n)` payload register or simultaneous generic and exceptional `Theta(n)` candidates. A sufficient scalable regime is that every unallocated width in the stage table is `O(w+log n)` with `w=O(log n)`, or that any larger width is explicitly assigned to and reused within the three counted banks. The abstract statement does not establish that a concrete implementation satisfies this register-coloring condition; it establishes the condition itself.

## Scope

The result is limited to the abstract direct-sum construction, its coherent alias behavior, reversible cleanup, symbolic resource identities, and the stated width condition. It is not an implementation validation or a scientific state decision.
