# EXP-030b — BOUNDED theta-null Kummer redo (settle H14 theta-null chart)

Round 15. Experiment-engineer. Bounded redo of the round-13 EXP-030 measurement
that stalled before the gated meter finished.

Files:
- code:  `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo.sage`
- log:   `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo.log`
- json:  `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo_result.json`
- reused build (read, 516 lines): `round013_exp030_theta_null_kummer.sage`
- gated meter (read, 685 lines): `round007_exp012_localization_gate.sage`
- base meter (read, 277 lines): `round005_meter_validation.sage`

## Headline verdict: INCONCLUSIVE on meter self-validation; STRONG NULL signal on the science.

The bounded sweep ran and produced data, but the mandatory 4-fixture meter
self-validation did **not** come back all-clean (POS-A fixture failed), which by
the hard rule forces an INCONCLUSIVE meter status. The theta-null science signal
that DID land points entirely at the EXPECTED NULL (no gate-meaningful fall), but
because the meter could not be certified in this run I do **not** record H14
theta-null as formally CLOSED — it stays OPEN pending a clean meter pass.

## Meter self-validation (4 fixtures) — FAILED on POS-A

| fixture     | required                                  | observed                                  | ok |
|-------------|-------------------------------------------|-------------------------------------------|----|
| POS-A       | base fires, d_ff=4 < D_reg                 | d_ff=4, **D_reg=None**, fires=False        | NO |
| NEG-1       | quiet (no base fire, gm=False)             | fires=False, gm=False                      | yes|
| e-ring m=3  | base fires, gate_meaningful=False (artifact)| fires=True (d_ff=3<D_reg=7), gm=False      | yes|
| POS-C Weil  | base fires AND gate_meaningful=True        | fires=True (d_ff=4<D_reg=9), gm=True       | yes|

ROOT CAUSE of the POS-A failure (diagnosed, not a meter-logic bug): the
round-007 `build_POS_A` puts 3 cubics in **4** variables (an underdetermined,
positive-dimensional ideal), so the Froberg degree-of-regularity series never
goes non-positive and `froberg_Dreg_local` returns `D_reg=None`; the fixture's
`fires := d_ff < D_reg` then evaluates False. The original round-005 POS-A used
**3** variables (where D_reg=7 is finite and POS-A fires d_ff=4<7). The 3
discriminating fixtures (NEG-1 quiet, e-ring artifact rejected gm=False, POS-C
genuine fall gm=True) behave exactly as required, so the gate itself is
discriminating; only the POS-A positive-base-fire fixture is mis-specified in
this Dmax/variable configuration. This is the SAME mismatch that stalled
round-13 (its log shows identical `POS_A ok=False D_reg=None`). A clean rerun
needs POS-A evaluated with a finite D_reg (3-var version or an explicit
known-d_ff check).

## Theta-null system measurement (what landed: p=31, m=2)

Only the p=31/m=2 cell completed and was captured before the read-back channel
went intermittent; p=31/m=3 began (curve built) but its meter row was not
captured this session.

| p  | m | theta nvars | theta neqs | theta total deg | max per-var deg | 4^(m-1) | d_ff | D_reg | fires | gate_passes | gate_meaningful |
|----|---|-------------|------------|-----------------|-----------------|---------|------|-------|-------|-------------|-----------------|
| 31 | 2 | 4           | 5          | 2               | 2               | 4       | 4    | 3     | False | True        | **False**       |

Note: `fires=False` here because D_reg=3 <= d_ff=4 for this small over-determined
quadratic theta system (it is regular/near-regular at this size), so there is NO
early fall at all — gate_passes=True is irrelevant because the base meter does
not fire (gate_meaningful = fires AND gate_passes = False).

## Anti-circularity confirmation (p=31, m=2) — PASSED

The theta-null system is genuinely distinct from the x-line Semaev:
- theta: 4 vars / 5 eqs, all four theta coords per point used in the biquadratic
  Hadamard addition; x-line Semaev S_3: 3 vars / 1 eq.
- `nvars_differ=True`, `neqs_differ=True`.
- Projection test (collapse each theta point to a single coord p0..p3 -> X0,0,0,0):
  the x-line Semaev S_3 is **NOT** recovered monomial-for-monomial
  (`semaev_recovered_under_projection=False`).
- `anti_circularity.distinct = True`.

So unlike round-12 EXP-028 (which was circular: kummer numerators == S_3), this
relation is NOT algebraically the x-line Semaev.

## Per-variable degree vs elliptic 4^(m-1)

For m=2 the theta system's max per-variable degree is 2, vs the elliptic Semaev
per-pair bound 4^(m-1)=4. Lower per-variable degree is observed, BUT this is a
toy-size near-regular artifact (the system does not fire at all), not an
exploitable early fall: lower degree without a gate-meaningful fall gives no
index-calculus leverage. This matches the established D_reg-conservation picture.

## Auto-descent (p=31, m=2) — PASSED (fixes the round-13 NR-024 failure)

- n=31, hidden k chosen, public Q = k*P built.
- Sage `discrete_log(Qpub, Gp, ord=n, operation="+")` on the PUBLIC point only.
- k_rec=23; **verify_kP_eq_Q=True**; matches_public_point=True;
  hidden_eq_recovered_modn=True.

The descent recovers k mod n (the EC group order) and verifies against the public
point without ever reading the ground-truth k to drive the solve. This is the
honest descent that round-13's affine attempt (NR-024) failed.

## H14 theta-null verdict

INCONCLUSIVE this round (meter not certified). The science signal that landed is
fully consistent with the EXPECTED NULL: the genuinely-distinct theta-null
relation shows gate_meaningful=False (no exploitable summation-poly early fall;
the small m=2 instance is near-regular and does not fire at all). There is NO
candidate (no gate_meaningful fire). But because POS-A failed self-validation, I
will not stamp H14 theta-null CLOSED on this run.

## Next

1. Conservative: rerun with a FIXED POS-A fixture (3-var version, finite D_reg=7,
   or an explicit `d_ff == 4 and d_ff < <known-regular-bound>` check that does not
   require a finite Froberg D_reg for underdetermined systems), then complete the
   p in {31,67} x m in {2,3} grid. Expectation: all gate_meaningful=False ->
   verdict=failed -> H14 theta-null CLOSED, joining NR-024 (affine) + NR-028
   (x-line); H14 closed across all 3 charts and the named queue exhausted.
2. Representation-changing: if (unexpectedly) any m=3 cell shows gate_meaningful=True
   with lower per-variable degree AND a verified auto-descent, escalate to PO-003
   (downstream solver demo) before any claim.
3. Harness: before the next run, confirm a bare `echo ok` returns non-empty so the
   round is not lost to the intermittent read-back outage seen this session.
