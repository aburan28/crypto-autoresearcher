# EXP-017 — Weil-restricted ABELIAN SURFACE summation polynomial (H14)

**Round** 9  **Role** Experiment-Engineer  **Timestamp** 2026-05-31
All numbers below are read back from `round009_exp017_abelian_surface_result.json`
produced by the final clean run (rc=0). No value in this file is hand-entered.

**Artifacts**
- `round009_exp017_abelian_surface.sage` (self-contained, parses+runs under Sage 10.9)
- `round009_exp017_abelian_surface.log`
- `round009_exp017_abelian_surface_result.json`
- `round009_exp017_abelian_surface_result.md` (this file)
- loaded gate: `round007_exp012_localization_gate.sage` -> `meter_gated`, `meter_local`, `build_*`

## VERDICT: `failed` — H14 CLOSED as a bankable NEGATIVE

`RESTRICTED THEOREM (empirical, toy p<=509, m in {2,3})` / `NEGATIVE RESULT`:
For the SCALAR Weil restriction A = Res_{F_{p^2}/F_p}(E) realized by splitting the
Semaev relation over the F_p-basis {1, w}, the A-summation polynomial has the SAME
per-variable degree as the elliptic-curve Semaev relation for the same number of
variables (S_2: 1=1, S_3: 2=2). The Weil split is an F_p-LINEAR isomorphism on the
coefficient space; it re-packs total degree across the doubled coordinates but cannot
lower the per-variable degree of the underlying F_q relation. **Semaev per-variable
degree is a restriction invariant** (the algebraic shadow of "Semaev degree is an
isogeny invariant", since the norm/Verschiebung structure relating A and E is an
isogeny). No D_reg advantage exists, so the H14 "slower-than-4^(m-1) surface summation
degree" conjecture is FALSE for the scalar-restriction realization.

A gate-meaningful early fall DID occur at m=3 (d_ff=5 < D_reg=11) — but it is the KNOWN
POS-C Weil-S_3 phenomenon reproduced on the 6-variable surface system, NOT a new
prime-field positive: with EQUAL degree it confers no D_reg advantage.

## 1. Meter self-validation (MANDATORY — inline) — PASS

| control | meter | d_ff | D_reg | fires | gate_passes | gate_meaningful | expected | ok |
|---|---|---|---|---|---|---|---|---|
| POS-A (3 cubics, shared quad, seed 101) | meter_local | 4 | 7 | True | n/a | n/a | fire d_ff=4<7 | YES |
| NEG-1 (generic quadrics, seed 11) | meter_local | None | 4 | False | n/a | n/a | quiet | YES |
| NEG-2 (generic cubics, seed 22) | meter_local | None | 7 | False | n/a | n/a | quiet | YES |
| e-ring m=3 Semaev | meter_gated | 3 | 7 | True | False | **False** | FAIL gate (artifact) | YES |
| POS-C Weil S_3 / F_{p^2} | meter_gated | 4 | 9 | True | True | **True** | PASS gate | YES |

`meter_self_validated = True`, checks = {posA_ok, neg_ok, ering_fails_gate_ok,
posC_passes_gate_ok} all True. (POS-A/NEG built inline in a 3-variable ring with the
round005 seeds; the gate module's own 4-variable build_POS_A reports D_reg=None beyond
the probe bound and the round005 control builders crash on a closed log handle — both
traps avoided, see code comments.)

## 2. Weil-restriction construction + auto-descent (n | prime-field target) — CONFIRMED

A = Res_{F_{p^2}/F_p}(E), A(F_p) ≅ E(F_q), q=p^2; |A(F_p)| = |E(F_p)|·|T(A)|, T(A) the
trace-zero (twist) factor, |T(A)| = |E(F_q)|/|E(F_p)|. E has F_p-coefficients so it
descends to E/F_p; descent prime n = largest prime factor of Np=|E(F_p)|. DLP transport:
PUBLIC Q=k·P in E(F_p) (k HIDDEN from solver), embed into A(F_p)=E(F_q), solve order-n
DLP in the surface (additive-group discrete_log, fallback order-n BSGS), verify ONLY
against the PUBLIC relation Q == k_rec·P (k never read for the success test).

| p | a | b | Np=\|E(F_p)\| | Nq=\|A(F_p)\| | \|T(A)\| | n | n\|Np | n\|Nq | n\|T(A) | dlp_ok (vs public pt) |
|---|---|---|---|---|---|---|---|---|---|---|
| 31  | 1 | 3   | 41  | 943    | 23  | 41  | True | True | False | **True** |
| 61  | 1 | 9   | 73  | 3723   | 51  | 73  | True | True | False | **True** |
| 127 | 1 | 42  | 139 | 16263  | 117 | 139 | True | True | False | **True** |
| 251 | 1 | 243 | 283 | 62543  | 221 | 283 | True | True | False | **True** |
| 509 | 1 | 104 | 523 | 259931 | 497 | 523 | True | True | False | **True** |

F_q min polynomials: p=31 x^2+29x+3; p=61 x^2+60x+2; p=127 x^2+126x+3;
p=251 x^2+242x+6; p=509 x^2+508x+2.

`auto_descent_confirmed = True` across all 5 toy sizes (2^5..2^9). KEY POINT: n | Np and
n | Nq ALWAYS; n | T(A) is FALSE for every chosen curve here (n is the LARGE prime
factor of Np and the twist order |T(A)| is coprime to it). That is the CORRECT and
stronger statement — the surface carries the prime-field target subgroup DIRECTLY
(inside the E(F_p) factor of A), so the DLP transports faithfully even though the
descent prime does NOT live in T(A). This is precisely the auto-descent NR-016 lacked
(there the target was forced into the wrong subgroup); here the target IS the
prime-field E(F_p) subgroup sitting inside A. (Note: the original H14 framing expected
n | |T(A)|; the experiment shows the faithful descent runs through the E(F_p) factor
instead, which is strictly better for a prime-field attack.)

## 3. A-summation degree vs elliptic-curve Semaev (the decisive H14 test) — NO ADVANTAGE

Construction builds the m-variable Semaev S_m over F_q and splits it into F_p real/imag
parts (the A-summation rows). `m` = number of Semaev variables. Reference:
deg_var S_2 = 1; deg_var S_n = 2^{n-2} (n>=3). Apples-to-apples = per-variable degree of
the SAME relation.

| m | relation | EC per-var | 4^(k-1) slogan (k=m-1) | A sum per-var | A sum total | A sys total | nFp vars | strictly lower? | EQUAL to EC? |
|---|---|---|---|---|---|---|---|---|---|
| 2 | S_2 | 1 | 1 | **1** | 1 | 2 | 4 | No | **Yes** |
| 3 | S_3 | 2 | 4 | **2** | 4 | 4 | 6 | No | **Yes** |

`A_degree_strictly_lower_any = False`. The A-summation per-variable degree EXACTLY
EQUALS the elliptic-curve Semaev per-variable degree for both S_2 and S_3.

## 4. Gated meter on the A decomposition system

| m | nFp vars | n eqs | d_ff | D_reg | fires | gate_passes | gate_meaningful |
|---|---|---|---|---|---|---|---|
| 2 | 4 | 4 | None | 3 | False | False | **False** |
| 3 | 6 | 6 | 5 | 11 | True | True | **True** |

`gate_meaningful_fire = True` (from m=3). m=3 gate_detail @D=5: nrows_full=236,
rank_full=196, ker_full=40, koszul_full=36, nontriv_full=4, n_sum_rows=12, nontriv_fb=0,
involves_sum_shrink=True, involves_sum_direct=True — the firing non-Koszul syzygy
genuinely touches the S_3 summation rows. This is the SAME mechanism as POS-C (the Weil
restriction of S_3 over F_{p^2} has a genuine summation-touching early fall), now
reproduced on the full 6-variable doubled surface system. IT IS NOT A NEW POSITIVE: it
arrives with EQUAL per-variable degree (section 3), so it gives no D_reg advantage over
plain prime-field Semaev.

## 5. What is ruled out / what is NOT

RULED OUT (scoped: toy p<=509, m in {2,3}, scalar Weil restriction via {1,w} split):
- The H14 degree-advantage mechanism for the SCALAR Weil restriction. The A-summation
  polynomial does NOT have lower per-variable degree than the EC Semaev polynomial; it
  is the SAME relation re-expressed over F_p. No D_reg gain.
- Therefore the (real, confirmed) faithful auto-descent buys NOTHING: the algebra it
  descends to has identical complexity to plain prime-field Semaev (Yokoyama 2020 closes
  naive IC there).

NOT RULED OUT:
- A GENUINELY 2-dimensional surface addition law (Kummer-surface / theta / Mumford
  coordinates from A's OWN group law) rather than the F_q-Semaev pullback. Only a
  summation relation that does NOT factor through the F_q x-line Semaev could escape
  restriction-degree-invariance. EXP-017 tested the pullback; it did not test an
  intrinsic surface relation.
- Higher m (m>=4) in the surface setting — untested here (EXP-015 closed prime-field
  x-ring m=4 separately).
- Non-scalar restrictions / restriction relative to a degree>2 extension.

## 6. Near-theorem extracted

`HEURISTIC -> RESTRICTED THEOREM (toy-confirmed)`: Semaev per-variable degree is
invariant under the scalar Weil restriction realized by an F_p-linear basis split. The
split acts as an F_p-linear isomorphism on coefficients; it cannot lower the per-variable
degree of any single underlying F_q variable's image. This is the algebraic shadow of
"Semaev degree is an isogeny invariant" (the norm/Verschiebung map relating A and E is an
isogeny).

## 7. Next structure to test (next three pushes)

1. REPRESENTATION-CHANGING / highest value (EXP-018): build the decomposition relation
   from A's INTRINSIC group law in Kummer/theta/Mumford coordinates (a degree-2 divisor
   on the surface), NOT by pulling back the F_q x-line Semaev. Measure its per-var degree
   and run the gate with sumpoly_indices = the intrinsic-relation rows. Only a relation
   that does NOT factor through the F_q Semaev can break the invariance shown here.
2. CONSERVATIVE: re-run EXP-017's degree+gate measurement on S_4 over F_{p^2} (m=4, 8 F_p
   vars) to confirm restriction-degree-invariance persists at the next Semaev level
   (extends this NEGATIVE to m=4 in the surface setting).
3. HIGH-RISK: T(A) is itself an elliptic curve / twist over F_p; build a factor base +
   native Semaev on T(A)/F_p and combine with the confirmed n|Np auto-descent to test
   whether the twist's distinct j-invariant (the one un-probed degree of freedom) yields
   any degree or rank structure absent in plain E(F_p) (expected null by the same
   invariance, but worth a bankable check).
