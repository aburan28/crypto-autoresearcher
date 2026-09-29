# The proves-too-much control

Task TASK-20260904-ed0e8f (red team), `review_plan.proves_too_much`, assigned
to this task. The ARGUMENT run unchanged against each object is
(D1)→(D3, H-TOP)→(D4, tensor kernel + Wilson exactness) of
`H-PFDR-4148b8`, whose conclusion is
`d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1` with
`fall_dim = m[C(s,a_0) − C(s,a_0+e)]`. Measurements are mine
(`r4_nearby_and_ptm.py`, `rt_meter.py`), p = 4099 unless stated.

| # | object (conclusion KNOWN false) | what the argument does, step by step | where it stops | closed form would give | measured | failure signature seen? |
|---|---|---|---|---|---|---|
| 1 | mixed-block linear map, m = 2, s = 3, all 6 digit variables shared (as executed) | (D1) applies (same ring B). (D3) is not invoked (no Semaev). (D4) requires `S~_top = ∏_k q_k(block k)`; the top form is a generic degree-4 form on all 6 variables, `top_terms = 15`, and is not a tensor product over any block split | **(D4), tensor-kernel step** | `d_ff = 5`, `fall_dim = 4` | **`d_ff = 6`, `fall_dim = 14`** (3 independent coefficient draws; package: 36/36 at 6) | **yes** — must be 6, is 6 |
| 2a | non-tensor top form `ell_1^3 ell_2 + ell_1 ell_2^3` + dense random sub-top, m = 2, s = 3 | (D1) applies. (D4)'s hypothesis fails: the block-1 × block-2 coefficient matrix of the top form has rank 2, so the multiplication map is `M_{ell_1^3}⊗M_{ell_2} + M_{ell_1}⊗M_{ell_2^3}`, whose kernel is not a sum of block kernels | **(D4), tensor-kernel step** | `d_ff = 5` | **`d_ff = 6`, `fall_dim = 14`** (3 reps) | **yes** — value in [5,6], not forced to 5 |
| 2b | non-tensor top form `ell_1^2 ell_2^2 + ell_1^3 ell_2` + dense random sub-top (my addition, the inconvenient variant) | same as 2a: rank-2 coefficient matrix, tensor step fails | **(D4)** — but the CONCLUSION for `d_ff` survives | `d_ff = 5`, `fall_dim = 4` | **`d_ff = 5`, `fall_dim = 2`** (3 reps) | **PARTIAL FAILURE.** `d_ff = 5` is reproduced where the argument does not apply; `fall_dim` is not |
| 3 | DIRECT presentation, m = 2, membership degree B = 4 = 2^s at s = 2; generators `f_1(x_1), f_2(x_2), S_3(x_1,x_2,x_R)` of degrees (4,4,4) in the ordinary ring `F_p[x_1,x_2]` | (D1) is unavailable: there is no squarefree quotient, so "top-form fall = graded annihilator in A" has no referent; the block algebra in which powers of a linear form have large annihilators is absent | **(D1), the change of algebra** | 5 (the digit value at s = 2) | **`d_ff = 6 = B + 2`, `fall_dim = 2`**; profile `(4;3,3,3,0) (5;6,6,6,0) (6;9,9,7,2)`; the fall at 6 is exactly the counting-forced one (9 rows into a 7-dimensional degree-6 space), and the semi-regular first-strictly-negative degree of `(1−z^4)^3/(1−z)^2` is also 6 | **yes** — must not be 5, is 6; reproduces `IDEA-20260808-afe4ce`'s "no early fall" |
| 4 | out-of-regime `s < 2^{m-1}`: m = 3, s = 3, n = 9 | (D3) gives a degree-12 top form `∏_k x_k^4`; substituting `x_k = ell_k` on 3 squarefree variables per block gives `ell_k^4 = 0`, so `S~_top` of degree 12 does not exist and δ = 12 is wrong | **(D3)→(D4) substitution: the claimed top form is zero** | δ = 12, `d_ff = 12` | generator degree **9** (matching `EXP-PFDR-cbdefb`'s "(3,2,3) generator degree 9"), single top monomial, **`d_ff = 10 = n+1`, `fall_dim = 9`** | **yes** — the argument declares itself out of scope, visibly (its δ is wrong by 3) |

## What the control found

* Objects 1, 3 and 4 kill the argument cleanly at the step the plan predicted,
  and the measured first falls (6, 6 = B+2, 10 with δ = 9) are all different
  from the closed form's value. **No sign that the argument reads the degree
  profile.**
* Object 2b is a real, if partial, survival, and its location is the finding:
  the argument's conclusion for `d_ff` re-emerges from a top form that is not a
  block tensor, because what produces `d_ff = δ + 1` is the existence of ANY
  degree-1 annihilator of the top form. Being a block tensor is sufficient, not
  necessary. The pair `(d_ff, fall_dim)` still separates (5,2) from (5,4), so
  the mechanism claim survives if it is carried by the pair; the record's
  falsification criterion F5 ("if the mixed-block object returns 5 the method
  cannot distinguish block structure from degree profile") is stated too
  strongly in the converse direction — an object returning 5 need not be a
  block object.
* Object 4 additionally supplies a number `EXP-PFDR-cbdefb` could not compute
  (it reported "no computable arm at D_max = 7" at (3,2,3), the generator
  degree being 9): at `D_max = 12` the cell has `d_ff = 10`, `fall_dim = 9`.
  Like the boundary cells, this is `n + 1` — degree exhaustion, not an early
  fall.
