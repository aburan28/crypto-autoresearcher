# EXP-PFDR-cbdefb — Stage 0 (zero compute): the transfer dictionary, the two non-transferring steps, the null formula and the formal analogue constant on the ladder

Task TASK-20260903-6745ea (Executor). Contract `specification.yaml` (status
`approved`, `approved_by: coordinator`, approval commit `c5742969`,
DEC-20260903-93862f). This note is written BEFORE any official run. It restates
material already derived in IDEA-20260903-d52480 and H-PFDR-c88f14 (claim (A),
(B1), (B2), (C)) in the form the contract's Stage 0 asks for; nothing here is a
new derivation and nothing here is evidence about any hypothesis. Observations
only; no status is touched.

## 1. The dictionary (descent of arXiv:2103.07282  <->  digit presentation of IDEA-20260830-84cdb7)

| descent side (as retrieved by IDEA-20260903-d52480, abstract / ar5iv level) | digit side (IDEA-20260830-84cdb7, this contract) |
|---|---|
| ground field k = F_{q^n}, subfield k' = F_q | prime field F_p, no proper subfield |
| m original variables x_1..x_m | m unknowns x_1..x_m (x-coordinates of the summands) |
| descended coordinates X_{ij}, j = 0..n-1, via the k'-linear isomorphism k = k'^n | digit variables a_{k,i}, i = 0..s-1, via x_k = sum_i a_{k,i} d^i (a bijection of SETS [0, d^s) -> [0, d)^s, not additive: carries) |
| field equations X_{ij}^q - X_{ij} included in F'_1 | membership equations prod_{j<d} (a_{k,i} - j); at d = 2 they are the ring quotient a(a - 1) = 0 |
| q (subfield size) | d (digit base) |
| n (extension degree) | s (digits per unknown) |
| F over k, deg F = d_F; F'_1 = Weil descent of F plus field equations | S~ = S_{m+1}(ell_1, ..., ell_m, x_R) reduced in B = F_p[a]/(a(a - 1)), ell_k = sum_i 2^i a_{k,i} |
| Theorem 1.1: max(d_{F_1}, q deg F) = max(d_{F'_1}, q deg F) | no analogue asserted |
| Theorem 2.6: F reducible for k  =>  d_{F'_1} <= max((q - 1) m + 1, q deg F) | the FORMAL analogue max((d - 1) m + 1, d deg S) is a number with no theorem behind it (section 3) |
| Lemma 2.1: f_i^q == f_{i+1} (mod Q-bar) for f = sum a_{ij} x_{ij} in S_1 (Frobenius = cyclic shift of the coordinate index) | NO ANALOGUE (section 2, B1) |

## 2. The two non-transferring steps

**B1 — the Frobenius shift.** Lemma 2.1 is the step that lets a relation found
in one descended coordinate block propagate to all n blocks at no degree cost;
it holds because tau: x -> x^q is a k'-linear automorphism of k that permutes
the descended coordinates up to the field equations. Over F_p the only
Frobenius is x -> x^p, which is the identity on F_p: it fixes every digit
value in [0, d) and permutes no digit position (Aut(F_p) is trivial), and the
digit map is not additive, so x -> x^p induces nothing on (a_{k,0}, ...,
a_{k,s-1}). The lemma has no analogue; the propagation it buys is absent.

**B2 — the reducibility hypothesis.** Theorem 2.6 requires F to be "reducible
for k", a condition expressed through k'-linear structure on k. The base-d
expansion is not k'-linear for any subfield because F_p has none. The
hypothesis is unavailable, so Theorem 2.6 does not apply even formally.

Consequence (claim (A) of H-PFDR-c88f14, restated): no version of the
bounded-last-fall theorem transfers to the digit presentation, neither with
the same constant nor with a different one. The last fall degree must be
MEASURED; that is Stages 1-4 of this contract.

Proof-body caveat, carried forward verbatim from the source record: the
theorem statements above were retrieved by the proposing session from the
abstract page and the ar5iv HTML; the proof bodies were not read there and
this session has no web access, so it could not re-read them either. This is
why the F_2 Weil-descent known-answer fixture of `inputs.known_answer_fixtures
(ii)` cannot be exhibited here with a conformance argument to Theorem 2.6's
hypotheses (the executor cannot establish "reducible for k" from the retrieved
statement alone) and the contract's sanctioned substitute, the PLANTED-FALL
fixture, is the known answer; see `stage1-closure-convention.md` section 4.

## 3. The null formula and the formal analogue constant on the ladder

Null formula (contract `inputs.null_formula`, IDEA-20260830-84cdb7 convention):
`D_null(m, d, s) = ceil((m s (d - 1) + 2 m) / 2)`; at m = 2, d = 2 this is
`s + 2`. The sibling EXP-PFDR-5726af scores against
`floor((m s + m e) / 2) + 1 = s + 3` (its own contract's convention, e = 2);
it is listed beside the frozen one and is NOT used for scoring here (the
frozen band of this contract is `s + 2 + c`, c in {0, 1, 2}).

Formal analogue constant: `max((d - 1) m + 1, d * deg S)` with deg S the total
degree of S_{m+1}. At m = 2, deg S_3 = 4 = 2m, so the constant is
`max(3, 8) = 8 = 4m` (the contract's "4m"). At m = 3, deg S_4 = 12 = m 2^{m-1}
(IDEA-20260903-e1e38b's correction of 84cdb7's "2m"); the contract's formula
"4m = 12" uses the 2m reading, the corrected reading gives max(4, 24) = 24.
Both are tabulated; neither is a theorem (section 2).

| m | s | D_null = ceil((ms + 2m)/2) (frozen) | s + 3 (5726af convention, reference) | null band s + 2 + {0,1,2} | analogue constant (2m reading / m 2^{m-1} reading) | separable on this ladder? |
|---|---|---|---|---|---|---|
| 2 | 1 | 3 | 4 | 3..5 | 8 / 8 | no (band below 8) |
| 2 | 2 | 4 | 5 | 4..6 | 8 / 8 | no |
| 2 | 3 | 5 | 6 | 5..7 | 8 / 8 | no |
| 2 | 4 | 6 | 7 | 6..8 | 8 / 8 | no (band reaches 8) |
| 2 | 5 | 7 | 8 | 7..9 | 8 / 8 | no (band straddles 8) |
| 2 | 6 | 8 | 9 | 8..10 | 8 / 8 | excluded cell (2, 2, 6, 8) by name |
| 3 | 2 | 6 | 8 | 6..8 | 12 / 24 | no |
| 3 | 3 | 8 | 9 | 8..10 | 12 / 24 | no |

Reading: on the ladder s <= 5 at m = 2 the semi-regular null runs from 3 to 7
and the analogue constant is 8; with the band {0, 1, 2} the null's own last
fall is expected between s + 2 and s + 4 and reaches 8 already at s = 4..5. So
the ladder CANNOT test "d_lf <= 4m"; it tests slope 0 against slope 1 in s at
resolution 0.25 with four to five points (H-PFDR-c88f14 claim (C)). A flat
d_lf at s <= 5 is a slope statement, never a bound in s.

Also recorded: D_max = 7 of this contract is BELOW the frozen null band's upper
edge at s = 4 (8) and s = 5 (9), so null-arm cells at the top of the ladder
may be right-censored by construction; the censoring flag and its treatment
are frozen in `stage1-closure-convention.md` section 3.

## 4. Inputs read from the two sibling packages (read-only, after their snapshot archives)

- EXP-PFDR-5726af (`analysis.md`, `runs/RUN-PFDR-5726af-m2-s{2,3,4,5}/raw-result.json`):
  graded-rank first fall (per-layer meter convention, D_max = D_null + 1) on
  the Semaev arm at p = 4099, curve seeds 1101..1103, target seeds 1, 2:
  d_ff = 5, 5, 6, 6 at s = 2, 3, 4, 5 on every draw (fall_dim 4, 4, 10, 10);
  NULL-1 (support-matched) d_ff = 5, 6, 7, 8 = s + 3 on every seed; H-TOP at
  m = 3 passed (`gate_m3_secondary_open: true`), so Stage 3 of this contract is
  gated open. These are the CTRL-DFF-AGREEMENT reference values.
- EXP-PFDR-fd901a (`analysis.md`): rank-drop rate at p = 4099 on the Semaev
  arm 0/40, exact 95 percent CI [0, 0.0881]; this is the small-p artifact
  budget the contract names under `inputs.artifact_budget`.

## 5. The frozen prediction, restated read-only (never adjusted)

- d_ff = 5, 5, 6, 6 at s = 2..5 (slope 1/2; IDEA-20260903-e1e38b D5).
- d_lf on NULL-1 and NULL-2 = s + 2 + c, c in {0, 1, 2}.
- Semaev d_lf slope: prior 0.6 that the 95 percent interval contains 1 and
  excludes 0.5 (Outcome I on d_lf) giving the joint label OUTCOME II with the
  d_ff slope 1/2 strictly below; 0.05 Outcome III (interval contains 0 and
  excludes 0.25 over four consecutive uncensored cells); 0.1 unresolved.
- NULL-3 d_ff minus Semaev d_ff = 0 at every cell.
- Joint-label rule (P5 of H-PFDR-c88f14): OUTCOME II iff the d_ff interval
  lies strictly below the d_lf point estimate and excludes 1 while the d_lf
  interval contains 1 and excludes 0.5.
