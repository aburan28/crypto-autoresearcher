# R3 — H-TOP provenance, the ALPF-011 citation, the CAS substitution, and
# H-TOP at m = 4

Task TASK-20260904-ed0e8f (red team), joint R3. Numbers from `r3_results.json`
and `r3b_results.json` (`r3_htop_m4.py`, `r3b_htop_m4.py`). Result of the
joint: **breaks (citation) / holds (CAS) / gap closed at m = 4**.

---

## 1. The ALPF-011 citation is mislabelled — confirmed, decisively

`H-PFDR-4148b8` (D3) and HEUR-001's `random_model_justification` say: *"At
m = 3 the archived EXP-ALPF-011 profile (total degree 12, per-variable degree
4) forces the single monomial x_1^4 x_2^4 x_3^4 with nonzero coefficient"*,
citing `[4, 4, 4, 12]` from
`experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep_result.md`.

Opened. Section 2 of that file, column header: *"Leading-form degree profile is
the homogeneous top-form degrees actually fed to the meter"*, one row per
(curve, bits, |FB|, representation). The decisive datum is that the entry
**tracks |FB|**:

| rep | |FB| = 4 | |FB| = 5 |
|---|---|---|
| (A) x-ring baseline | `[4, 4, 4, 12]` | `[5, 5, 5, 12]` |

A per-variable profile of `S_4` cannot change when the factor base grows. The
list is the degree list of the meter's four **generators** — three factor-base
membership polynomials of degree |FB| and `S_4` of total degree 12. The
executor's observation `A-ARCHIVED-PROFILE-CITATION` is **confirmed**; the
archive supports "total degree 12" and nothing about per-variable degrees.

Consequence for HEUR-001. The *inference* is valid given its premise (in three
variables, `(4,4,4)` is the unique exponent vector of total degree 12 with
every exponent ≤ 4), but the premise was not in the cited source. After this
review, HEUR-001's m = 3 support rests **entirely on the package's own symbolic
run** `RUN-PFDR-5726af-htop`, which is sound and which I reproduce below. The
hypothesis record's `supporting_results` entry with
`verified_by: coordinator … (file not reopened)` should be superseded by an
annotation recording (a) that the archived list is a generator-degree list and
(b) that the symbolic check now carries the claim. Records are immutable, so
this is a superseding annotation, never an edit.

## 2. The CAS substitution (D-HTOP-CAS): no objection

The contract's `inputs.symbolic_S4` names no CAS; it names the construction
(`Res_T(S_3(x_1,x_2,T), S_3(x_3,x_R,T))` from a from-scratch `S_3`, `x_R`
symbolic, not the harness `s4_expr`). sympy's resultant over `Z[a,b,x_R]` is
exact integer algebra with no floating point and no termination heuristic, so
the substitution changes nothing in substance. I reproduced the m = 3 result
with my own sympy code and a different extraction route (specialise
`x_k = c_k t`, read the leading `t`-coefficient): total degree 12,
coefficient of `x_1^4x_2^4x_3^4` **= 1** for three independent random
`(a, b, x_R)`. The handoff's "missing Sage is failed_infrastructure" clause
concerns stages that REQUIRE Sage; this one does not. **No objection.**

## 3. H-TOP at m = 4 — the package's declared gap, now closed

`stage0-htop.md` §2.2 records "m = 4 (S_5) was not attempted". Since HEUR-001
is quantified over all m ≥ 2, m = 4 was the first unchecked case of a
load-bearing heuristic. It is cheap to settle:

`S_5` has per-variable degree `2^3 = 8`, so the only exponent vector of total
degree 32 with all exponents ≤ 8 is `(8,8,8,8)`. Hence H-TOP at m = 4 reduces
to "the total degree in (x_1..x_4) is 32 and the coefficient of
`x_1^8x_2^8x_3^8x_4^8` is a nonzero constant". Both are read off the
one-variable specialisation `x_k = c_k t` of
`S_5 = Res_T(S_3(x_1,x_2,T), S_4(x_3,x_4,x_R,T))`.

| run | deg_t | coefficient of x_1^8x_2^8x_3^8x_4^8 |
|---|---|---|
| 6 random (a, b, x_R), pairwise-distinct c | 32 in all 6 | **1** in all 6 |
| a, b numeric, **x_R symbolic** | 32 | **1**, and the leading coefficient has no free symbols |
| x_R numeric, **a, b symbolic** | 32 | **1**, no free symbols |
| m = 3 positive control (same code path) | 12 | **1** (3 random parameter sets) |

So H-TOP holds at m = 4 with `c = 1`, constant in (a, b, x_R) — it cannot
vanish on any locus. **Caveats, stated plainly:** (i) I use the raw resultant,
as the package did; if the true `S_5` is the resultant divided by an extraneous
factor, the constant could differ (the *single-monomial* conclusion would not,
since a factor of the top form is still a monomial); (ii) the per-variable
degree bound `≤ 8` is the classical fact about summation polynomials, checked
here only at one non-degenerate specialisation (deg 8 in `x_1`); (iii) m ≥ 5
remains unchecked.

**Degeneracy caution for anyone repeating this.** Specialisations with
`c_1 = c_2` (or `x_3 = x_4`) kill the leading `T`-coefficient `(x_1-x_2)^2`
(resp. `(x_3-x_4)^2`) and drop the resultant's degree — my first attempt hit
this (deg_t = 24 with `c = [5,5,7,9]`, and degree 4 with `x_3 = x_4 = 3`).
Those are degeneracies of the SPECIALISATION, not of H-TOP; both runs are
archived in `r3_results.json` so the sequence is not hidden.

## 4. Is the top form a single monomial for every m? Still open

Checked: m = 2 (by hand and here), m = 3 (package and here), m = 4 (here).
The general statement — "the resultant recursion multiplies leading
coefficients, so the top term of the resultant is the product of the top
terms" — is a *generic* statement about resultants, and the degenerate
specialisations above are exactly cases where genericity fails; the argument
therefore needs the non-vanishing of the leading `T`-coefficients of both
factors, which is `(x_1-x_2)^2 ≠ 0` and, at the next level, the leading
`T`-coefficient of `S_m`. That is plausible and not proved in the record.
**H-TOP at m ≥ 5 remains a symbolic obligation**, as the hypothesis itself
says.
