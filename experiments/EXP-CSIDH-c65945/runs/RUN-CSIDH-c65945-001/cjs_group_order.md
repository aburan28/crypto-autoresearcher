# Group order N' actually supplied to the DCP/dihedral-HSP instance by the CJS reduction

Required artifact per specification.yaml required_artifacts[3]: "An explicit
statement of the group order N' actually supplied to the DCP/dihedral-HSP
instance by the CJS reduction (KN-LIT-071), with a citation, distinguished
from the raw class number itself if the two differ (e.g. because the class
group is not cyclic, or a subgroup or quotient is used)."

## Source

Childs, Jao, Soukharev, "Constructing elliptic curve isogenies in quantum
subexponential time" (Journal of Mathematical Cryptology 8(1):1-29, 2014;
arXiv:1012.4019v3). Retrieved live via `curl` this run (HTTP 200,
`https://arxiv.org/pdf/1012.4019`); see `command.txt`.

## What the CJS reduction actually supplies

**Section 5 ("A quantum algorithm for constructing isogenies"), p.9**: CJS
reduce the isogeny/group-action-inversion problem to the **abelian hidden
shift problem** directly on `A = Cl(O_Δ)` (the ideal class group itself),
via functions `f_0, f_1 : Cl(O_Δ) → Ell_{q,n}(O_Δ)` (Lemma 5.1, p.9). This is
an ABELIAN hidden shift problem on the class group `Cl(O_Δ)` itself, not
already-embedded in a dihedral group at this step of CJS's own presentation.

**Algorithm 3 ("Isogeny construction"), p.11**: decomposes
`Cl(O_Δ) = <[b_1]> ⊕ ... ⊕ <[b_k]>` (a direct sum of cyclic groups of orders
`n_j`), then "solves the hidden shift problem defined by functions
`f_0, f_1 : Z_{n_1} x ... x Z_{n_k} -> Ell_{q,n}(O_Δ)`".

**For CSIDH-512 specifically**: CSI-FiSh (Section 3, p.7-8, and Section 2.1
p.4: "In what follows we will assume that the class group Cl(O) is cyclic")
establishes that `Cl(O)` for CSIDH-512's actual discriminant is CYCLIC of
order N (the exact value verified in `class_group_order.md`). With `k=1` in
CJS's Algorithm 3 decomposition, the abelian hidden shift problem CJS reduces
to is on the single cyclic group `Z_N`.

**Equivalence to a dihedral-HSP/DCP instance of order 2N**: Kuperberg 2005
("A Subexponential-Time Quantum Algorithm for the Dihedral Hidden Subgroup
Problem"), **Section 6, Proposition 6.1, p.6**: "If A is an abelian group,
the hidden shift and hidden reflection problems in A are equivalent to the
hidden reflection problem in D_A" — where (same section, "Generalized
dihedral groups...") `D_A` is defined as the generalized dihedral group
`C_2 ⋉ exp(A)`, of order `2|A|`.

## N' (this contract's own notation)

For CSIDH-512, `A = Cl(O) ≅ Z_N` (cyclic, single factor), so the equivalent
dihedral-HSP/DCP instance CJS's reduction (composed with Kuperberg's
Proposition 6.1 equivalence) supplies has group order:

```
N' = N = 254652442229484275177030186010639202161620514305486423592570860975597611726191
```

i.e. **N' equals the raw class number N exactly** — they do NOT differ here,
because Cl(O) is cyclic (not merely abelian with multiple invariant factors,
which would instead have required CJS's `k>1` multi-factor decomposition and
a per-factor hidden-shift/dihedral-HSP instance of smaller order for each
`n_j`). This is stated explicitly and cited, per the specification's own
instruction to distinguish N' from the raw class number "if the two differ
(e.g. because the class group is not cyclic...)" — here they do not differ,
and the reason they do not is recorded.

The dihedral group itself (as fed to Kuperberg's sieve or to Simon's
zero-noise DCP construction, both of which operate on a dihedral group of
order `2N` per their own stated problem formulations — see
`applicability_audit.md`) therefore has order `2N' = 2N`, an even integer of
bit length 259, consistent with Simon 2026's own DCP problem statement
(p.2: "2N ≈ 2^{n+1} is the size of the dihedral group").

## Scope note

This artifact states what group order the CJS reduction supplies; it does
NOT compute or compare any concrete time/query cost (out of scope per
H-CSIDH-3eaede.interpretation_limits and this task's own constraints), and it
does NOT verify CJS's own Theorem 2.1 / GRH-heuristic runtime claims (out of
scope, unrelated to this contract's premise-(i) applicability question).
