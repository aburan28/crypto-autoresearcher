# Fold of the 201 changed paths into the lead atlas (proposed diffs; nothing applied; review stamp untouched)

Generated 2026-10-24 by the fold agents of the lead-discovery workflow (sonnet), from the paths listed by `python3 tools/lead_atlas.py --delta` at crypto-autoresearcher ab0609ebee, crypto 5cb553810e, cryptanalysis c5aa7b39b, ecc-challenges df8cd52. Each row names the record read, the lead it advances (or NONE / new), and the proposed row edit. Six new mechanisms were found; they are proposed lead rows for the Coordinator, not filed.


---

## Group: car-decisions

# Fold of changed paths into the ECDLP lead atlas: group `car-decisions`

Reviewer output for the lead-atlas skill, "changed since review", step 2. **Proposed diffs only**: no atlas row, `coverage.tsv`, repository file or hypothesis/experiment/goal status was edited. Written under `scratchpad/audit/` only.

## 0. Scope, conventions and caveats

- **Count.** The task text says 54 files; `atlas/delta.txt` lists **57** decision paths for this group (39 `DEC-20261018-*`, 2 `DEC-20261019-*`, 2 `DEC-20261022-*`, 11 `DEC-20261023-*`, 3 `DEC-20261024-*`; `grep -c 'ledger/decisions/' delta.txt` = 57). All 57 were folded. The path list is `audit/car-decisions-paths.txt` (extracted from delta.txt) and the table below.
- **Observation vs interpretation.** Table cells quote what a record says or what a file/receipt shows ("Observation"); statements beginning "Interpretation (conditional)" are mine and conditional. A timeout, an interrupted attempt, an `invalid_output` receipt or an inadmissible run set is not evidence for or against any lead; the records say so themselves and this fold keeps that reading.
- **Method.** Each record was read by its summary fields (decision, scope, rationale, scoped claim, limitations, next_actions, knowledge_promotion), not by raw logs. Targets were resolved through `ledger/.index/{experiments,hypotheses,proposals}.jsonl` and `coverage.tsv`. `python3 tools/lead_atlas.py --match` was run **twice per record** (query A = decision label plus target titles; query B = the scientific claim of the first target hypothesis, or the decision scope when there is none) and a **third, topical** time for the 36 worksheet/campaign records, because for custody records the first two queries mostly match process vocabulary. Raw top-5 hits are in the appendix. Lead mapping for custody records therefore comes from the existing `coverage.tsv` rows of the original hypotheses, and the appendix shows where `--match` agrees or disagrees.
- **Action codes.** `advances_lead` = the record bears on a lead (a custody record with no row edit of its own is still coded here, with "subsumed by C-nn"); `decides_lead` = the record is a deciding record for a closure or opening in a lead; `new_mechanism` = none in this group; `not_ecdlp` = administrative record with no mechanism content and no lead (only `f952c0`, a lane-closure receipt; the campaign itself is GOAL-ECDLP-001). DEC ids are not rows of `coverage.tsv`, so no coverage row is owed for the decisions themselves.
- **Edit labels.** `S-nn` = substantive diff in section 2.1-2.12; `C-nn` = consolidated campaign evidence entry in section 2.13. `last_reviewed` is left to the folding step.
- **`prior_art.lead` check.** The nine ideas named by these records (IDEA-20261023-f15270, IDEA-20261017-3f46a5, IDEA-20261024-b58e07, IDEA-20261009-93b29f, IDEA-20260803-ff7415, -20260805-a9a95d, -20260805-90df50, -20260831-d29a71, -20260904-a1b81b) carry no `prior_art.lead` field; the rule starts at IDEA-20261025, so this is not a defect.


## 1. Summary

**Tally (57 paths):** 54 `advances_lead`, 2 `decides_lead`, 1 `not_ecdlp`.

**Eleven records of the CZLIFT review round are the substantive fold** (`039ddf, 147f9f, 26a6de, 2e7447, 36b4f0, 488023, 66af3b, 6931ab, 9de83a, fdc4af, 23d64d`), all prime-field transfer/lift work (p-adic canonical sections, global lifts, xedni). They replace the "review pending" / "evidence records not filed" wording in three lead rows (`LEAD-TRF-global-lift-small-height`, `LEAD-TRF-anomalous-padic-lift`, `LEAD-TRF-padic-canonical-section`) and show that statements in two of them are wider than the deciding records:

1. `LEAD-TRF-global-lift-small-height`: `best_measured` says small points reduce like uniform points and xedni dependence was never seen within relation bound 6. Observation: DEC-20261023-26a6de (uniform-reduction clause contradicted as stated), -6931ab ("reduce uniformly" contradicted) and -488023 (1 relation in 3200 trials, with a certificate) say otherwise; DEC-20261023-fdc4af returned the Q(2^(1/3)) run set as inadmissible, so the E(K) clause has no basis. The closure basis becomes conditional JKSST (CORR-20261024-63d682: status proven -> heuristic) plus a derivation-tier fixed-rank counting obstruction conditional on T1-T4 (S-08). No record flips `closed_known`.
2. `LEAD-TRF-padic-canonical-section`: the closure holds for homomorphic sections and the formal logarithm (derivation, DEC-20261023-36b4f0) but the sentence "any non-homomorphic section recovers d only at the random 1/p rate" and the foreclosed phrase "p-adic digits of the torsion section" are not carried: DEC-20261023-2e7447 and DEC-20261024-23d64d leave coordinate/digit encodings of s_tor open and rank an exponent-targeting successor (KN-OPEN-d3a6f0) next. **One disposition change is proposed (conditional): `closed_obstructed` -> `open_next_step`** (S-01).
3. `LEAD-TRF-anomalous-padic-lift`: "review pending" is replaced by DEC-20261023-147f9f (support, toy, scoped, known theory) and the 10^4..10^5 replication in DEC-20261023-9de83a (S-07).

**Prime-field relevance.** The only item in this group that could bear on a prime-field exponent is KN-OPEN-d3a6f0 (maximal Fourier mass of p-adic digit characters of the torsion section against the n^(-1/4) Fourier-learning breakeven, for E/F_p with a point of prime order n). Observation: the program's only measurement (EV-CZLIFT-764f54, preliminary, 42 power-bearing records of 72, n <= 613) excludes a single-pair correlation above a per-record floor and cannot test the title claim. Interpretation (conditional): the existing lead closes more than that evidence; this fold does not say that digits leak.

**Other substantive records.** `a7a0fd/5b9240/ebf1dc` (Semaev s4_expr defect: matched legacy/repaired rerun, exposure note on `LEAD-ICE-curve-presentation-invariance`, no effect claimed); `9aec2b` (PFDR bb0d26: unreviewed O-NULL observation, next_action update, S-03); `e5f45c` (SNFS-G: zero valid runs, S-04); `273b2d` (ICPERF m=8 k11 design, coverage row, S-05); `19c53b` (extension-field compounding-clause re-scope, S-06); `992998/e29f4c` (PEXT n=7 GHS cover genus floor, S-11).

**The 39 `DEC-20261018-*` campaign records (minus `273b2d`, `a7a0fd`) are custody/process records with zero science** (`knowledge_promotion.not_warranted` on every one). Twelve leads own the toy worksheets they touch (none of the twelve cites any of these experiments today). Proposal: one consolidated evidence entry per lead pointing at `DEC-20261018-8e211e` and `reports/ideas_execution_20261018/native-campaign-closeout/actual-native-inventory.json` (C-01..C-12), no `best_measured` change.

**Cross-cutting flags for the atlas reviewer** (details in sections 2 and 4):
- **KR-IC-cd159a dependency.** DEC-20261024-23d64d records the frontier row as overstated (CORR-20261024-63d682: claim narrowed, status heuristic, "lift to characteristic zero" and "canonical lift for ECDLP" not foreclosed by JKSST); the superseding row is not committed. Eight leads list KR-IC-cd159a. Text/dependency notes are proposed for the three whose obstruction text leans on it (S-08, S-09, S-10); none is a basis for a flip.
- **SEMAEV is not an ECC area** in `orchestration/research-priority.yaml`, so `--coverage` never lists `H-SEMAEV-94dab2` (nor H-MTIC-001, H-FIB-001, H-DTREE-8636a3, the experiments it audits). Five records touched by this group have no coverage row (four listed by `--coverage` as unmapped, plus `H-SEMAEV-94dab2`, which `--coverage` cannot see); they are listed in section 4.
- **Coverage fit is weak for some worksheet hypotheses** (section 4).


## 2. Proposed diffs by lead

All blocks are proposals against rows under `knowledge/leads/ecdlp/<family>/`. `evidence` paths are repo-relative and were checked to exist; ids in `ledger_refs` were checked against `ledger/` (see the verification line at the end of section 2).


### 2.1 S-01 `LEAD-TRF-padic-canonical-section` (transfer; today `closed_obstructed`): from DEC-20261023-36b4f0, -039ddf, -2e7447, -9de83a, DEC-20261024-23d64d; the reopen itself is decided by -2e7447 and DEC-20261024-23d64d

**Observation.** The row's `obstruction.statement` (kind `theorem`) says: the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills; "any non-homomorphic section recovers d only at the random 1/p rate"; "Toy runs ... met the frozen criteria; the only failure (naive F_p^* section) is a size effect". `best_measured` ends "evidence records not filed". `forecloses` includes "p-adic digits of the torsion section". The review round has now filed EV-CZLIFT-ad28f5 (supported, derivation, replicated), EV-CZLIFT-f2a401 (reject_scoped, strong), EV-CZLIFT-764f54 (refine, preliminary), EV-CZLIFT-e9a7cf (refine). Their limits, quoted: "One readout (identity); planted discrete-log oracles pass it. No claim that the non-torsion sections carry no information about d" (-36b4f0); "The 1/p clauses carry no evidence ... likelihood ratio of 0.85" (-9de83a); the naive section's excess sits exactly on g^d mod p^2 < p (-039ddf); "Whether any coordinate or digit encoding of s_tor carries d" is `not_established` and "Coordinate and digit encodings of s_tor must be excluded [from any RQ closure] while KN-OPEN-d3a6f0 is open" (-23d64d).

**Interpretation (conditional).** The closure is wider than the evidence in two places: the 1/p sentence (measured only for three named sections, identity readout, toy, detection floor 4.2x-5.2x of 1/p; no power at 10^4..10^5) and the digit phrase (the theorem addresses the formal logarithm and homomorphic sections, not nonlinear digit characters). The first is a text narrowing; the second changes what the lead can claim to have closed. This is not a statement that digits leak.

```yaml
# LEAD-TRF-padic-canonical-section
disposition: open_next_step          # was closed_obstructed  (see section 3)
obstruction:                          # kept, but scoped to what is decided
  kind: theorem
  statement: >-
    SCOPE OF THE CLOSURE (derivation tier, EV-CZLIFT-ad28f5; a checkable argument, not
    machine-verified): for p >= 5, prime n != p and any good-reduction Z_p-lift, the prime-to-p
    torsion section is the unique homomorphic section of reduction over <P>, costs at most
    2(bits(n)+bits(p^k))+1 complete additions, and the Smart formal-logarithm functional vanishes
    identically on it (DEC-20261023-36b4f0). NOT carried: "any non-homomorphic section recovers d
    only at the random 1/p rate". Measured only for three named sections with the identity readout
    (toy, p <= 600, detection floor 4.2x-5.2x of 1/p); the 1/p tests at 10^4 <= p <= 10^5 have no
    power (DEC-20261023-9de83a); the naive integral section on F_p^* exceeds 1/p exactly where
    g^d mod p^2 < p (DEC-20261023-039ddf, z = 7.65, 9.14; H-CZLIFT-d37231 rejected as posed);
    CORR-20261023-6e10a2 rewrites RQ-CZLIFT-b9f765 decision_target (a). NOT closed: coordinate and
    digit encodings of s_tor (DEC-20261024-23d64d; KN-OPEN-d3a6f0).
  revisit_when: (unchanged) + "the exponent-targeting successor below reports Phi_i(n)"
next_action:
  step: >-
    Exponent-targeting successor on KN-OPEN-d3a6f0 (DEC-20261023-2e7447 NA-4; ranked in
    DEC-20261024-23d64d N-3(1), behind the zero-run control C1 of its N-2): measure the growth
    exponent of Phi_i(n), the maximal Fourier mass of p-adic digit-character functions (i = 1..4,
    coordinates x and y, full-range sums) of the prime-to-p torsion section s_tor, against n^(-1/2)
    (uniform-random model) and the n^(-1/4) Fourier-learning breakeven, for n up to about 10^4..10^5,
    with a symmetry-matched null and per-record detection floors; with the NA-6 Weil-type
    derivation task for the i >= 1 digit sums through the KN-TECH-080 gate.
  discriminates: >-
    Phi_i(n) >= n^(-1/4+delta) for some i with a locatable heavy coefficient would be an exponent-level
    candidate, after the polynomial degree of coefficient location in 1/tau is checked
    (KN-OPEN-d3a6f0 Q3); Phi_i(n) at the sqrt(ln(pn)/n) random scale plus a Weil-type bound closes
    digit encodings of s_tor and restores the closed state for the whole lead.
best_measured: >-
  derivation tier: s_tor unique homomorphic section, Smart functional vanishes (EV-CZLIFT-ad28f5,
  supported, replicated; identity readout, 0 exceptions in 1116 pairs, p <= 600, and 576/576 pairs at
  10^4 <= p <= 10^5, same-code); G_m calibration: naive section excess confined to g^d mod p^2 < p
  (EV-CZLIFT-f2a401); digit-character spectrum (EV-CZLIFT-764f54, preliminary): no single
  (additive character, character of Z/n) correlation >= rho_min 0.28-0.98 on 42 power-bearing records
  (53 <= p <= 571, 47 <= n <= 613); 30 of 72 records blind (n <= 41)
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-36b4f0.yaml,
   note: "H-CZLIFT-6d4ed1 supported (derivation, replicated); H2 'computable canonical section = full break' answered negatively or circular"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-039ddf.yaml,
   note: "G_m calibration; naive section rejected as posed, excess exactly on g^d mod p^2 < p; Teichmuller and Hensel clauses held"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-2e7447.yaml,
   note: "digit-character spectrum H-CZLIFT-fba874 approved->analyzed, preliminary; 30/72 records blind; title claim untested"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-9de83a.yaml,
   note: "replication at 10^4..10^5 (toy): exact identities hold, 1/p clauses uninformative"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261024-23d64d.yaml,
   note: "CZLIFT synthesis: RQ cannot close while digit encodings of s_tor are open; ranks the Fourier-mass successor"}
- {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-d3a6f0.md,
   note: "Q1 growth exponent, Q2 Weil-type bound for digit i >= 1, Q3 Fourier-learning consequence"}
ledger_refs:   # append
- DEC-20261023-36b4f0
- DEC-20261023-039ddf
- DEC-20261023-2e7447
- DEC-20261023-9de83a
- DEC-20261024-23d64d
- EV-CZLIFT-ad28f5
- EV-CZLIFT-f2a401
- EV-CZLIFT-764f54
- EV-CZLIFT-e9a7cf
- CORR-20261023-6e10a2
related: [LEAD-EXO-padic-jet-canonical-lift, LEAD-EXO-coordinate-statistic-leakage, LEAD-EXO-hnp-advice-leakage]
```

**Owner choice (one owner).** `--match` on KN-OPEN-d3a6f0's own phrasing returns `LEAD-TRF-padic-canonical-section` first (14) on the Fourier-mass wording, then `LEAD-EXO-padic-jet-canonical-lift` (10); on the "hidden number problem / Fourier learning" wording `LEAD-EXO-hnp-advice-leakage` ranks first (16) and `LEAD-TRF-padic-canonical-section` second (15). The padic-jet row's obstruction is about additive/linear readouts ("every additive order-l image is zero", "digit linearity at chance", jet oracles GGM-simulable) and a Teichmuller contrast; it does not address nonlinear digit characters of s_tor, so it keeps its closure and gains only a `related` note (S-12). `LEAD-EXO-coordinate-statistic-leakage` names a digit-character family (IDEA-20260921-1ec106) whose object is a bounded digit character of the coordinate's integer lift, a different object from the p-adic digits of a Hensel/torsion section; its `next_action.discriminates` says a random-level result "leav[es] only unnatural (unbounded-degree) statistics", and KN-OPEN-d3a6f0 Q2 states that for i >= 1 the digit function "degree grows with p". `LEAD-EXO-hnp-advice-leakage` is the downstream converter (blocked until "a statistic with a measured nonzero log-bit advantage exists"). Both get `related` notes only.


### 2.2 S-02 `LEAD-ICE-curve-presentation-invariance` (ic-engine; `open_next_step`): exposure note, from DEC-20261018-a7a0fd, DEC-20261019-5b9240, DEC-20261019-ebf1dc

**Observation.** H-SEMAEV-94dab2 (approved by -a7a0fd) states that the legacy `s4_expr` dropped x3 and "changed the recorded outputs of the archived S4-consuming runs", exposed runs being EXP-MTIC-001, EXP-FIB-001 and RUN-ICINV-e0cd8f-m3class (audit `docs/reports/2026-10-18-semaev-s4-factor-base-audit.md`, which reports archived `s4_support` 227 against 439 repaired on two p = 4001 curves and lists RUN-ICINV-geom-* as not affected). The lead lists `EV-ICINV-8afb64` in `ledger_refs`; that evidence cites RUN-ICINV-e0cd8f-m3class, treats m = 3 as the decisive families and records "m=4 support and singular locus computed as required secondaries". The lead's evidence entry EV-ICINV-343679 rests on geom runs (not affected). Receipts under `experiments/EXP-SEMAEV-93d5cc/runs/`: 6 of 7 `output_validated` (returncode 0, check 0); RUN-SEMAEV-500a81 has no receipt (interrupted, -5b9240); RUN-SEMAEV-980e8c under EXP-SEMAEV-88c46c has no receipt; `experiments/EXP-SEMAEV-6e9dcf/runs/` is empty. No evidence record and no review exist. `LEAD-RHO-dp-multitarget-precomputation` lists `MTIC` only under `areas`; none of its evidence entries or refs names EXP-MTIC-001 or H-MTIC-001, so **no edit** there (grep of all 147 rows for EXP-MTIC-001/EXP-FIB-001/ICINV-e0cd8f/s4_expr/H-FIB-001/EV-STR-001/EV-IC-001 finds nothing else).

**Interpretation (conditional).** Exposure only: the m = 4 secondary columns behind EV-ICINV-8afb64 were computed with the defective expression; the matched rerun that measures the effect has produced receipts but no reviewed result, and one cell (mtic-010b) is unmeasured. No effect on the lead is claimed.

```yaml
# LEAD-ICE-curve-presentation-invariance
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/hypotheses/H-SEMAEV-94dab2.yaml,
   note: "INTEGRITY EXPOSURE, no effect claimed: EV-ICINV-8afb64's m=4 secondary columns (RUN-ICINV-e0cd8f-m3class) used the x3-dropping legacy s4_expr (audit 2026-10-18). Matched legacy/repaired rerun EXP-SEMAEV-93d5cc approved by DEC-20261018-a7a0fd: 6 of 7 receipts output_validated, mtic-010b cell unmeasured after two interrupted attempts (DEC-20261019-5b9240, -ebf1dc), no evidence record, no review. m=3 S_3 families are not S4-dependent."}
ledger_refs:   # append
- H-SEMAEV-94dab2
- EXP-SEMAEV-93d5cc
- DEC-20261018-a7a0fd
# coverage.tsv (new row): H-SEMAEV-94dab2  LEAD-ICE-curve-presentation-invariance
```


### 2.3 S-03 `LEAD-ICP-coincidence-harvest-structured-base` (ic-prime; `open_next_step`): from DEC-20261022-9aec2b

**Observation.** The row's `next_action.step` says "run the scheduled log-GAP validation EXP-PFDR-bb0d26 in the same instrument". The five frozen trials have run (receipts `output_validated`, `scientific_conclusion: null`) and the decision records producer values as OBSERVATIONS: outcome `O-NULL`, headline `SUPPORT_SCOPED`, 44 powered cells of 45 (cell b20-r3-n4096 invalid: 46 of 50 curves ok after 4 degenerate jobs), largest |kappa-1| = 0.0414 (b28-r1-n256, CI [1.0100, 1.0743]), largest |z| = 3.13 (b24-r1-n2048), smallest planted kappa 1.2885, calibration mean -0.268 / sd 0.974, 0 failed_infrastructure, replication trial ran zero jobs because no cell was flagged. "MOVES NO HYPOTHESIS STATUS"; independent review (NA-1) pending. **Interpretation (conditional):** consistent with the lead's existing kappa-near-1 reading at 20-28 bits, toy only ("a null does not exclude label structure for sets that are not log-GAPs"). No disposition change.

```yaml
# LEAD-ICP-coincidence-harvest-structured-base
next_action:
  step: >-
    Run the break-even growth ladder (IDEA-20261018-a0830c): measure kappa_rel for the best FAM-1
    geometry at 3+ rungs from 16 to 32 bits with planted positive controls, and require growth of
    2^(8 delta*) per rung. The log-GAP validation EXP-PFDR-bb0d26 has run (five trials,
    DEC-20261022-9aec2b: observation recorded, UNREVIEWED; independent review NA-1 pending, H-PFDR-727bfc
    still approved); fold its review outcome into the ladder instrument.
best_measured: >-
  (existing text) ; EXP-PFDR-bb0d26 (UNREVIEWED producer observation, DEC-20261022-9aec2b): O-NULL, 44
  powered cells of 45, max |kappa-1| 0.0414 at 20-28 bits, planted kappa >= 1.2885
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261022-9aec2b.yaml,
   note: "EXP-PFDR-bb0d26 five runs recorded as observations (O-NULL, no flagged cell, 1 invalid cell); review pending"}
ledger_refs:   # append
- DEC-20261022-9aec2b
- EXP-PFDR-bb0d26
```


### 2.4 S-04 SNFS-G contracts (DEC-20261022-e5f45c): evidence notes on the leads the four hypotheses map to

**Observation.** Four SNFS-G contracts approved by DEC-20261017-0b1593 have **zero valid runs**: five receipts, none a valid run record (EXP-ECDLP-84af7b attempt A `infrastructure_error`, `cargo` missing; attempt B `invalid_output` kept under the alias RUN-ECDLP-d12308; EXP-ECDLP-8cc60d, -4c6a09, -ad27ad `invalid_output`, flat `manifest.yaml` refused by the run schema). The decision "asserts nothing about H-ECDLP-2f1033, H-ECDLP-281dd6, H-ECDLP-4da36f, H-ECDLP-986bab". `coverage.tsv` maps 2f1033 and 4da36f to `LEAD-EXO-global-lift-height`, 281dd6 to `LEAD-TRF-prime-field-isogeny-to-weak`, 986bab to `LEAD-ICP-algebraic-membership-factor-base`. None of the three leads cites them today. **Interpretation (conditional):** the number-field (cyclotomic / Solinas) arm of the height-compressing-lift lead is untested, not negative.

```yaml
# LEAD-EXO-global-lift-height  (2f1033 cyclotomic lift with complete splitting, 4da36f Solinas number fields)
next_action:
  step: (existing function-field step) + >-
    SNFS-G number-field arm: implement the versioned manifest transport (DEC-20261022-e5f45c NA-1) for
    EXP-ECDLP-84af7b and EXP-ECDLP-4c6a09 so they yield a valid run record; no result exists yet.
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261022-e5f45c.yaml,
   note: "SNFS-G contracts H-ECDLP-2f1033/4da36f: zero valid runs (infrastructure_error, invalid_output on run schema); impediment IMP-SNFSG-MANIFEST-20261022; asserts nothing about the hypotheses"}
ledger_refs: [DEC-20261022-e5f45c, H-ECDLP-2f1033, H-ECDLP-4da36f, EXP-ECDLP-84af7b, EXP-ECDLP-4c6a09]

# LEAD-TRF-prime-field-isogeny-to-weak and LEAD-ICP-algebraic-membership-factor-base: evidence note only
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261022-e5f45c.yaml,
   note: "SNFS-G contract (H-ECDLP-281dd6 / H-ECDLP-986bab) has no valid run; impediment IMP-SNFSG-MANIFEST-20261022; no metric exists"}
```

Mapping caveat: for H-ECDLP-281dd6 ("Mersenne embedding degree k(l) = ord_l(2)/gcd(ord_l(2), c)") `--match` ranks `LEAD-TRF-mov-small-embedding-degree` (13) and `LEAD-TRF-curve-parameter-transfer-audits` (11) above `LEAD-TRF-prime-field-isogeny-to-weak` (10); see section 4.


### 2.5 S-05 `LEAD-ICP-full-width-arity-grid` (ic-prime; `open_blocked`): from DEC-20261018-273b2d

**Observation.** The row's `next_action` ends "same for the k11 ordinary-binary matched bases", and its `ledger_refs` already contain IDEA-20261017-3f46a5 (the bounded k11 solver-to-certificate idea). -273b2d (decision `revise`) specifies H-ICPERF-3982eb and the successor EXP-ICPERF-554db4 for the certified ordinary-binary GF(2^61) curve (subgroup order 576460752557211763, m = 8): gamma = b^(1/4) = x([r]P_source) = 70364449406991 bound, sorted eight signed summand points, U/S/U schedule; experiment `review_required`, `approved_by` null, `execution_authorized` false; `experiments/EXP-ICPERF-554db4/` has no `runs/`. It states the v1 planted controls each hit the 300 s wall cap and all 64 natural calls were gated (EV-ICPERF-54ac6b, DEC-20261017-3b87bf: "do not support a zero-yield or performance verdict"), and that a no-solver blind replay must clear `problems/icperf-k11-gamma-admission-unbound.md`. **No result, no disposition change.**

```yaml
# LEAD-ICP-full-width-arity-grid
next_action:
  step: (existing 63-bit panel step) ; k11 ordinary-binary arm: >-
    EXP-ICPERF-554db4 (DEC-20261018-273b2d): zero-scientific-run sorted-input and launcher implementation
    (TASK-20261018-da71bd), blind gamma schedule derivation sealed before predecessor manifests are opened,
    then exact preapproval (approvable true) before any solver call.
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261018-273b2d.yaml,
   note: "k11 ordinary-binary m=8 successor design EXP-ICPERF-554db4 (review_required, no runs); v1 censored receipts are not a zero-yield verdict"}
ledger_refs: [DEC-20261018-273b2d, H-ICPERF-3982eb, EXP-ICPERF-554db4]
# coverage.tsv (new row): H-ICPERF-3982eb  LEAD-ICP-full-width-arity-grid
```
Alternative coverage target: `LEAD-ICP-icperf-binary-pdp-solver` (top hit of query A, score 11) because the sorted-summand presentation is a solver-input question; the parent idea's existing mapping points at `full-width-arity-grid`, which I follow.


### 2.6 S-06 `LEAD-ICE-semaev-cover-monodromy` (ic-engine; `closed_obstructed`): from DEC-20261023-19c53b

**Observation.** -19c53b is a portfolio act ("no trials", "Nothing here is evidence ... about compounding, about relation rates, or about any exponent"). It routes IDEA-20260803-ff7415 (the 2^(n-1) per-fibre compounding clause over F_{q^n}) to a re-scope, IDEA-20261023-f15270, under GOAL-PATH-001 BATCH-7ca353. ff7415 and four siblings plus H-MONO-663fb4 are already mapped to this lead; its `revisit_when` names "a factor-base statistic answering KN-OPEN-62c870 Q1/Q3". The compounding clause is Q3 and is a yield-counting question, distinct from `LEAD-ICE-semaev-yield-model-coset-typing` (the m! factor in the binary yield model, coset-typed bases). Scope: F_{q^n}; "no prime-field statement follows". IDEA-20261023-f15270 is unmapped. No disposition change.

```yaml
# LEAD-ICE-semaev-cover-monodromy
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-19c53b.yaml,
   note: "KN-OPEN-62c870 Q3 (2^(n-1) compounding over F_{q^n}) routed to IDEA-20261023-f15270; ranking only, extension-field scope, no evidence"}
ledger_refs: [DEC-20261023-19c53b, IDEA-20260803-ff7415, IDEA-20261023-f15270]
# coverage.tsv (new row): IDEA-20261023-f15270  LEAD-ICE-semaev-cover-monodromy
```


### 2.7 S-07 `LEAD-TRF-anomalous-padic-lift` (transfer; `closed_known`): from DEC-20261023-147f9f, -9de83a, -66af3b

**Observation.** The row's obstruction ends "re-derived the canonical-lift degeneracy (CZLIFT runs, review pending)". The review is decided: -147f9f supports H-CZLIFT-889c9d at toy tier in the scope of EV-CZLIFT-712fe4 (29 class-number-one CM anomalous curves, 7 <= p <= 1373, precision p^8; flag and j-distance rule agree on 14,616/14,616 rows; Smart's ratio recovers d on 2,052/2,052 rows per seed when v_p(Delta j) < 2e) and frames it as "known theory, calibrated (novelty: none; prior art Belding 2007 section 7)". -9de83a (refine) repeats it at 10^4 <= p <= 10^5 (p <= 97813): 4608/4608 rows agree, Smart's ratio = d on 1152/1152 pert_p rows. -66af3b returned the run set of EXP-CZLIFT-7c8d73 (level-1 Serre-Tate splitting, H-CZLIFT-d3dc4b) as inadmissible; no evidence exists for that construction. **No disposition change.**

```yaml
# LEAD-TRF-anomalous-padic-lift
obstruction.statement: replace the last sentence with >-
  The program reproduced it (Smart certificate p = 771853 in EXP-IT-001) and re-derived the canonical-lift
  degeneracy: v_p(z([p]P^)) >= 2 agrees with the j-distance rule v_p(Delta j) >= 2e on 14,616/14,616 rows
  (DEC-20261023-147f9f, support, toy, scoped, replicated, framed as known theory: Belding 2007 s7,
  KN-FIND-3c7e19) and on 4608/4608 rows at 10^4 <= p <= 10^5 (DEC-20261023-9de83a). The level-1
  Serre-Tate splitting construction (H-CZLIFT-d3dc4b) has no admissible run (DEC-20261023-66af3b); nothing
  is asserted about it.
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-147f9f.yaml,
   note: "H-CZLIFT-889c9d supported (toy, scoped): canonical-lift degeneracy of Smart's attack calibrated against known theory"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-9de83a.yaml,
   note: "replication at 10^4..10^5; exact identities hold; 1/p clauses uninformative"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-66af3b.yaml,
   note: "EXP-CZLIFT-7c8d73 run set inadmissible; H-CZLIFT-d3dc4b review paused, no evidence"}
ledger_refs:   # append
- DEC-20261023-147f9f
- DEC-20261023-9de83a
- DEC-20261023-66af3b
- EV-CZLIFT-712fe4
- EV-CZLIFT-e9a7cf
- CORR-20261023-9f2176
```


### 2.8 S-08 `LEAD-TRF-global-lift-small-height` (transfer; `closed_known`): from DEC-20261023-26a6de, -488023, -6931ab, -fdc4af, DEC-20261024-23d64d

**Observation.** Today's text: `best_measured` "toy: small points reduce like uniform points; xedni dependence never seen within relation bound 6 (planted dependence detected)"; obstruction "the program re-measured uniform reduction of small points on rank 0-11 curves and over Q(2^{1/3}) (CZLIFT, review pending)"; scope "lifts to E(Q) and E(K) for bounded-degree K". Deciding records, quoted: -26a6de "C2 uniform reduction contradicted as stated" (1.0330/1.0333 against uniform-null upper edges 1.0023/1.0041, 0 of 200 reps reach it; "the obstruction survives as a counting obstruction at fixed rank (D7), carried by C1, not by uniformity"; C5 twists / E(K) untested); -6931ab "'reduce uniformly / no structure' is contradicted as stated"; -488023 "1 relation in 3200 trials (3.1e-4, CI [7.9e-6, 1.7e-3])" with an explicit tangent instance as certificate, so "exactly 0 per seed" is false; -fdc4af "ruled inadmissible" for EXP-CZLIFT-8c50ea (the Q(2^{1/3}) run); -23d64d: KR-IC-cd159a "Overstated; corrected by CORR-20261024-63d682" (JKSST Theorem 4.1 is conditional on Lang's lower-bound conjecture and Lemma 4.1's assumption, with constants vacuous at small p).

**Interpretation (conditional).** The lead's measured clauses are contradicted or unsupported by its own deciding records; the closure survives only as a conditional literature result plus a derivation-tier counting obstruction conditional on T1-T4 beyond toy scale. **Does `closed_known` still fit?** README: `closed_known` = "a literature result the program reproduced; nothing new in scope". The literature basis is now conditional and the program's own measurements add scope-relevant findings that are not the literature result. No record decides a different disposition, so no flip is proposed; the reviewer should re-read the disposition when the superseding KR row (a new row via /curate-knowledge, per CORR-20261024-63d682) is committed.

```yaml
# LEAD-TRF-global-lift-small-height
obstruction:
  kind: literature          # unchanged; basis restated
  statement: >-
    JKSST (2000) Theorem 4.1 (conditional on Lang's lower-bound conjecture for the canonical height and
    Lemma 4.1's assumption; asymptotic; constants vacuous at small p, dependence frequent at small
    discriminants; CORR-20261024-63d682 K1): a xedni round succeeds with probability < C0/p. Program
    derivation (DEC-20261023-26a6de D6/D7, derivation tier, EV-CZLIFT-376eee; conditional on transfer
    assumptions T1-T4 beyond toy scale): at fixed rank, any spread of small points saves at most a factor
    2 ln 2 in N (0.327 at r = 2 to 0.093 at r = 7 in log log H_half); kernel vectors have canonical height
    >= 2 log p - c_E. Toy observations (eight-curve ladder, naive height <= 3e5, p = 103..20011): the
    (log H)^{r/2} count law is supported; "uniform reduction" is contradicted as stated (DEC-26a6de,
    -6931ab); 1 xedni-type relation in 3200 trials at bound 6 (DEC-488023, certificate). Scope: E(Q) only
    as measured; E(K) is UNMEASURED (EXP-CZLIFT-8c50ea run set inadmissible, DEC-fdc4af; C5 untested).
  revisit_when: (existing) + >-
    a pre-registered structured-null replication on disjoint curves and primes (DEC-20261023-26a6de
    next_actions), the numbered-heuristic successor from /propose-ideas RQ-CZLIFT-b9f765, or a valid E(K)
    run set (TASK-20261023-f97b36)
best_measured: >-
  toy (EV-CZLIFT-376eee, replicated; EV-CZLIFT-ee9b23, preliminary): (log H)^{r/2} count law supported;
  reduction is structured, not uniform (coverage ratio 1.033 vs uniform upper band 1.002-1.004); 1
  xedni-type dependence in 3200 trials (3.1e-4) at relation bound 6
evidence:      # append
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-26a6de.yaml, note: "H-CZLIFT-9a32e9 weakened: C1 supported, C2 contradicted as stated, counting obstruction D7 survives (derivation, conditional)"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-488023.yaml, note: "H-CZLIFT-cb95b8 weakened: 1 relation in 3200 trials, certificate; JKSST Thm 4.1 conditional"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-6931ab.yaml, note: "H-CZLIFT-27a184 weakened: rank-record curves; 'reduce uniformly' contradicted"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-fdc4af.yaml, note: "EXP-CZLIFT-8c50ea (E(K), K = Q(2^{1/3})) run set inadmissible; no E(K) evidence"}
- {repo: crypto-autoresearcher, path: ledger/corrections/CORR-20261024-63d682.yaml, note: "KR-IC-cd159a overstated: status proven -> heuristic; superseding row pending"}
ledger_refs:   # append
- DEC-20261023-26a6de
- DEC-20261023-488023
- DEC-20261023-6931ab
- DEC-20261023-fdc4af
- DEC-20261024-23d64d
- EV-CZLIFT-376eee
- EV-CZLIFT-ee9b23
- EV-CZLIFT-b6fe48
- CORR-20261024-63d682
- CORR-20261024-a7e0af
```


### 2.9 S-09 `LEAD-ICP-char0-lifting-xedni-smoothness` (ic-prime; `closed_known`) and 2.10 S-10 `LEAD-TRF-cm-canonical-lift-heights` (transfer; `closed_obstructed`): KR-IC-cd159a dependency notes only

**Observation.** S-09's obstruction (kind `literature`) says JKSST "show xedni does not beat rho". CORR-20261024-63d682 (K1, K2, K4; via DEC-20261024-23d64d) narrows the frontier row: conditional, asymptotic, status heuristic; "lift to characteristic zero" and "canonical lift for ECDLP" are not foreclosed by JKSST. -488023 observed 1 dependence in 3200 trials. S-10's obstruction (kind `cost_model`) rests on the Hilbert/ring-class polynomial degree h(D) ~ p^{1/2} and, for small |D|, on "the height-coverage obstruction of LEAD-TRF-global-lift-small-height ... unchanged"; its `forecloses` lists "canonical lift for ECDLP". The cost-model half is independent of JKSST; the small-|D| half inherits S-08. The superseding KR row is not committed, so these are text notes, not flips.

```yaml
# LEAD-ICP-char0-lifting-xedni-smoothness  (S-09) obstruction.statement, first sentence:
  JKSST (2000) show, under Lang's lower-bound conjecture and Lemma 4.1's assumption (Theorem 4.1;
  asymptotic, vacuous at small p; CORR-20261024-63d682), that a xedni round succeeds with probability
  below C0/p, and the logs span rank(E(Q)) unknowns ... ; the program's bounded-relation count found 1
  dependence in 3200 trials at relation bound 6 (DEC-20261023-488023).
ledger_refs: += [DEC-20261023-488023, CORR-20261024-63d682]

# LEAD-TRF-cm-canonical-lift-heights  (S-10) obstruction.statement, append:
  (Dependency: for small |D| the height-coverage half rests on LEAD-TRF-global-lift-small-height, whose basis is
  conditional per DEC-20261023-26a6de and CORR-20261024-63d682; the h(D) ~ p^{1/2} cost-model half is
  independent of JKSST.)
ledger_refs: += [DEC-20261024-23d64d]
```
Not edited: `ICP-xedni-function-field-sections` and `TRF-function-field-xedni-lift` (exact closed-form alpha = 3 proofs, independent of JKSST), `EXO-padic-jet-canonical-lift` (proof), `TRF-padic-canonical-section` (S-01). `EXO-global-lift-height` says the Q-lift variant "is already closed_known by KR-IC-cd159a" in `next_action.discriminates`: append "(KR row under correction, CORR-20261024-63d682)".


### 2.11 S-11 PEXT (DEC-20261024-992998, -e29f4c): `LEAD-TRF-small-genus-cover-general` (transfer; `closed_obstructed`)

**Observation.** EXP-PEXT-212d5c is approved (six trials) to measure the GHS cover genus floor at n = 7 in odd characteristic with a characteristic-2 control, porting the program's own n = 3 / n = 5 census tool (`research/ghs_cover_census_n5_20261013/cover_census_n.rs` in repo `crypto`, vendored with sha256 in the specification) and regressing against it (n = 3 at q = 3, 5, 7; n = 5 at q = 3, "floors 33 / 33 / 25 / 5 attained"). Hypothesis H-PEXT-d536a1: span dimensions are the degrees of divisors of x^7-1 over F_2 ({1,3,4,6,7}), genus 7 reached by split 2-torsion. `experiments/EXP-PEXT-212d5c/runs/` is empty. The nearest row is `LEAD-TRF-small-genus-cover-general`: Riemann-Hurwitz census g = 1 - 2^m + 2^{m-2}R of 2-torsion Kummer covers of E/F_{q^3} (only the JV configuration reaches g <= 3) and floors 9 / 49 / 41 at k = 6 / 10 / 14. The sibling n = 5 census README is cited by no lead (the row cites `research/cover_descent_genus_floor_20261015/`). `--match` on the idea's own wording ("GHS cover genus floor at n = 7 odd characteristic 2-torsion type compositum genus census") returns `LEAD-TRF-odd-char-descent-smith-quartic` (14, n = 3), `LEAD-ICP-gfp5-odd-char-cover` (10, n = 5, `open_blocked` on a source freeze) and `LEAD-TRF-jv-sieve-fp6-weak-class` (10), and `LEAD-TRF-small-genus-cover-general` is outside the top 6 (vocabulary gap: "floor" against "small-genus"); on the mechanism wording ("smallest genus of the 2-torsion Kummer cover compositum of the conjugate double covers of the x-line over F_{q^n}, Riemann-Hurwitz census") it ranks first (14). That is a retrieval gap worth telling the atlas maintainers; the choice of owner here is by reading the row. **Not a new mechanism:** the object (smallest genus of the (Z/2)^m compositum over F_q-structures) is the existing lead's; the new content is the n = 7 case and the governing invariant (cyclic submodules of F_2[x]/(x^n-1), "Lemma M"), both unmeasured until the trials run. No disposition change. Extension-field scope (not prime-field ECDLP).

```yaml
# LEAD-TRF-small-genus-cover-general
obstruction.revisit_when: (existing) + "the n = 7 floor table of EXP-PEXT-212d5c (odd characteristic) disagrees with the n = 3/5 pattern"
evidence:      # append
- {repo: crypto, path: research/ghs_cover_census_n5_20261013/README.md,
   note: "n = 3 (larger q) and n = 5 GHS cover genus census; baseline for the n = 7 extension"}
- {repo: crypto-autoresearcher, path: experiments/EXP-PEXT-212d5c/specification.yaml,
   note: "approved (DEC-20261024-992998), six trials, no run yet: n = 7 odd-characteristic genus floor with characteristic-2 control"}
ledger_refs: [DEC-20261024-992998, DEC-20261024-e29f4c, H-PEXT-d536a1, EXP-PEXT-212d5c, IDEA-20261024-b58e07, GOAL-PEXT-4a1d6b, RQ-PEXT-7c3e91]
# LEAD-ICP-gfp5-odd-char-cover: related += LEAD-TRF-small-genus-cover-general; note that its next step (odd-characteristic cover genus for EcGFp5/EcMasFp5) is the n = 5 case of the same census
# coverage.tsv (new rows): H-PEXT-d536a1  LEAD-TRF-small-genus-cover-general ;  IDEA-20261024-b58e07  LEAD-TRF-small-genus-cover-general
```


### 2.12 S-12 `related` notes (no other change)

- `LEAD-EXO-padic-jet-canonical-lift`: `related += LEAD-TRF-padic-canonical-section`; evidence note citing DEC-20261023-36b4f0 (uniqueness of the homomorphic section supports "prime-to-p torsion lifts uniquely"). Its closure covers additive/linear readouts; nonlinear digit characters of s_tor are owned by S-01.
- `LEAD-EXO-coordinate-statistic-leakage`: `related += LEAD-TRF-padic-canonical-section` (digit-character function of a lifted coordinate, different object and unbounded degree).
- `LEAD-EXO-hnp-advice-leakage`: `related += LEAD-TRF-padic-canonical-section` (KN-OPEN-d3a6f0 Q3 is the Fourier-learning conversion that lead prices once an advantage is measured).


### 2.13 Consolidated campaign entries C-01..C-12 (carrier record: `DEC-20261018-8e211e`)

**Observation.** The 2026-10-18 campaign executed 18 conditional-audit worksheet scopes plus one adjacent instrument: 41 native attempts, 32 `output_validated`, 7 `invalid_output`, 2 `infrastructure_error` (`actual-native-inventory.json`). Every campaign decision carries `knowledge_promotion.not_warranted`; the inventory says "Audit18 membership remains conditional" and "scientific_promotion" false. None of the twelve leads below cites any of these experiments or the report directory today (grep of the 147 rows). **Proposal:** one evidence entry per lead and one `ledger_refs` addition list; no `best_measured`, `obstruction` or `disposition` change; no per-custody-record `ledger_refs` (they add no information beyond this entry).

Common entry shape (path checked to exist):
```yaml
evidence:      # append, once per lead
- repo: crypto-autoresearcher
  path: reports/ideas_execution_20261018/native-campaign-closeout/actual-native-inventory.json
  note: <per-lead note below>
ledger_refs: += [DEC-20261018-8e211e, <the EXP ids listed>]
```

**C-01 `LEAD-ICP-algebraic-membership-factor-base`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-bfbe6f, EXP-ECDLP-4bb0ef, EXP-ECDLP-3521b9`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-bfbe6f -> EXP-ECDLP-4bb0ef (1 output_validated; runs RUN-ECDLP-25c448). Non-validated attempts retained: EXP-ECDLP-bfbe6f/RUN-ECDLP-8f5190 invalid_output; EXP-ECDLP-3521b9/RUN-ECDLP-03ccb4 infrastructure_error. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-02 `LEAD-EXO-coordinate-statistic-leakage`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-5f4f14, EXP-ECDLP-087aea, EXP-ECDLP-3c166b, EXP-ECDLP-11c54d, EXP-ECDLP-20ac31, EXP-ECDLP-5d6ec1`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-5f4f14 -> EXP-ECDLP-087aea (1 output_validated; runs RUN-ECDLP-42ded6) ; EXP-ECDLP-3c166b -> EXP-ECDLP-11c54d (1 output_validated; runs RUN-ECDLP-d9188a) ; EXP-ECDLP-20ac31 -> EXP-ECDLP-5d6ec1 (1 output_validated; runs RUN-ECDLP-6671fe). Non-validated attempts retained: EXP-ECDLP-5f4f14/RUN-ECDLP-42444c invalid_output; EXP-ECDLP-3c166b/RUN-ECDLP-4a3ca0 invalid_output; EXP-ECDLP-20ac31/RUN-ECDLP-08e0d9 invalid_output. 8e211e preserves, unreviewed: square-bias prediction strict miss (EXP-ECDLP-20ac31) and chord-slope fibres unscored (EXP-ECDLP-5f4f14). knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-03 `LEAD-EXO-global-lift-height`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-f34097, EXP-ECDLP-ee406e`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-f34097 -> EXP-ECDLP-ee406e (1 output_validated; runs RUN-ECDLP-4110e6). Non-validated attempts retained: EXP-ECDLP-f34097/RUN-ECDLP-62ec3d invalid_output. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-04 `LEAD-EXO-elliptic-net-eds`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-903c48, EXP-ECDLP-5c8854`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-903c48 -> EXP-ECDLP-5c8854 (1 output_validated; runs RUN-ECDLP-67ed93). Non-validated attempts retained: EXP-ECDLP-903c48/RUN-ECDLP-4616a2 invalid_output. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-05 `LEAD-EXO-curve-model-representation`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-080496`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-080496 (2 output_validated; runs RUN-ECDLP-9f8c2f, RUN-ECDLP-e6d65d). Non-validated attempts retained: none. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-06 `LEAD-EXO-invertible-hint-subset`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-4a3f03, EXP-ECDLP-6491b4, EXP-ECDLP-daee4d, EXP-ECDLP-324080`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-4a3f03 (2 output_validated; runs RUN-ECDLP-030f1f, RUN-ECDLP-4b5355) ; EXP-ECDLP-6491b4 (2 output_validated; runs RUN-ECDLP-e63c06, RUN-ECDLP-46551e) ; EXP-ECDLP-daee4d -> EXP-ECDLP-324080 (2 output_validated; runs RUN-ECDLP-0f1a90, RUN-ECDLP-5e5d13). Non-validated attempts retained: none. adjacent staged instrument EXP-ECDLP-324080 is separate from the conditional audit-18 mapping; its checker is vocabulary/file-presence only (legacy labels S0-FREEZE-OK, O-EXCESS). knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-07 `LEAD-EXO-lossy-object-propagation`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-5a293e`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-5a293e (2 output_validated; runs RUN-ECDLP-113f49, RUN-ECDLP-8c3ce8). Non-validated attempts retained: none. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-08 `LEAD-EXO-four-list-ktree-join`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-65f903, EXP-ECDLP-911c16, EXP-ECDLP-95f69f, EXP-ECDLP-c0c520`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-65f903 (2 output_validated; runs RUN-ECDLP-782cda, RUN-ECDLP-c7395e) ; EXP-ECDLP-911c16 (2 output_validated; runs RUN-ECDLP-5febcb, RUN-ECDLP-cfbd49) ; EXP-ECDLP-95f69f -> EXP-ECDLP-c0c520 (2 output_validated; runs RUN-ECDLP-36eff6, RUN-ECDLP-f5bde2). Non-validated attempts retained: EXP-ECDLP-95f69f/RUN-ECDLP-f67842 infrastructure_error. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-09 `LEAD-ICP-icperf-binary-pdp-solver`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-c9110e, EXP-ECDLP-53b1c3, EXP-ECDLP-efafc0, EXP-ECDLP-524b38, EXP-ECDLP-615fcf`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-c9110e -> EXP-ECDLP-53b1c3 (2 output_validated; runs RUN-ECDLP-ef9a36, RUN-ECDLP-449da5) ; EXP-ECDLP-efafc0 -> EXP-ECDLP-524b38 (2 output_validated; runs RUN-ECDLP-762d8c, RUN-ECDLP-b80f30). Non-validated attempts retained: EXP-ECDLP-615fcf/RUN-ECDLP-7f3a18 invalid_output. 8e211e preserves, unreviewed: chord-sign prediction false for the original EXP-ECDLP-efafc0. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-10 `LEAD-ICP-prime-ic-constant-engineering`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-d68ac9, EXP-ECDLP-c64491`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-d68ac9 -> EXP-ECDLP-c64491 (2 output_validated; runs RUN-ECDLP-40541f, RUN-ECDLP-fce7f4). Non-validated attempts retained: none. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-11 `LEAD-EXO-padic-jet-canonical-lift`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-f7310e, EXP-ECDLP-417a94`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-f7310e -> EXP-ECDLP-417a94 (2 output_validated; runs RUN-ECDLP-40d618, RUN-ECDLP-e3586e). Non-validated attempts retained: none. knowledge_promotion.not_warranted; no hypothesis or goal status moved.

**C-12 `LEAD-RHO-dp-multitarget-precomputation`**  
`ledger_refs += DEC-20261018-8e211e, EXP-ECDLP-c9c5a4, EXP-ECDLP-30277c, EXP-ECDLP-3365b4`  
> Toy finite-worksheet native reproductions (deterministic calibration, all unreviewed): EXP-ECDLP-c9c5a4 -> EXP-ECDLP-30277c (2 output_validated; runs RUN-ECDLP-7727d1, RUN-ECDLP-2d3b31). Non-validated attempts retained: none. 8e211e preserves, unreviewed: c9 definition gap and the descriptive two-convention arm (EXP-ECDLP-c9c5a4 / 3365b4). knowledge_promotion.not_warranted; no hypothesis or goal status moved.


## 3. Proposed disposition changes (only with a named deciding record)

| lead | from | to | deciding records | basis |
|:--|:--|:--|:--|:--|
| `LEAD-TRF-padic-canonical-section` | `closed_obstructed` | `open_next_step` | `DEC-20261023-2e7447` (H-CZLIFT-fba874 approved -> analyzed; KN-OPEN-d3a6f0 promoted) with `DEC-20261024-23d64d` (digit encodings of s_tor must stay excluded from any RQ closure while KN-OPEN-d3a6f0 is open; ranks the exponent-targeting successor, N-3(1)) | Observation: the row's `forecloses` includes "p-adic digits of the torsion section", while its theorem covers the formal logarithm and homomorphic sections; the only measurement of digit-character correlation is preliminary with 30 of 72 records blind. Interpretation (conditional): the closure is wider than the evidence for that sub-mechanism. Alternative the reviewer may prefer: keep the row `closed_obstructed` with `forecloses` narrowed and file the digit-character item as one new lead; I recommend reopening the existing row because no other row's obstruction covers nonlinear digit characters of s_tor (read: `EXO-padic-jet-canonical-lift`, `EXO-coordinate-statistic-leakage`, `EXO-hnp-advice-leakage`; see S-01) and the lead-atlas skill (step 2) puts a near-duplicate in the existing row. |

No other flip is proposed. Flagged, not flipped: `LEAD-TRF-global-lift-small-height` (`closed_known`: basis now conditional, S-08) and `LEAD-ICP-char0-lifting-xedni-smoothness` (`closed_known`: JKSST conditional, S-09), both pending the superseding KR-IC-cd159a row.

**New mechanisms: none in this group.** The digit-character Fourier-mass item (KN-OPEN-d3a6f0) is owned by an existing row (S-01); PEXT n = 7 is the existing cover-genus-floor object at a new n (S-11); the compounding clause is KN-OPEN-62c870 Q3 (S-06).


## 4. Coverage and retrieval observations

Proposed `coverage.tsv` rows (keep the file sorted):

| record | proposed lead | note |
|:--|:--|:--|
| `H-ICPERF-3982eb` | `LEAD-ICP-full-width-arity-grid` | listed unmapped by `--coverage`; parent IDEA-20261017-3f46a5 already maps there (alt: `LEAD-ICP-icperf-binary-pdp-solver`) |
| `H-PEXT-d536a1` | `LEAD-TRF-small-genus-cover-general` | listed unmapped; S-11 |
| `IDEA-20261024-b58e07` | `LEAD-TRF-small-genus-cover-general` | listed unmapped; S-11 |
| `IDEA-20261023-f15270` | `LEAD-ICE-semaev-cover-monodromy` | listed unmapped; re-scope of IDEA-20260803-ff7415, which maps there; S-06 |
| `H-SEMAEV-94dab2` | `LEAD-ICE-curve-presentation-invariance` | **not listed by `--coverage`**: area SEMAEV (like MTIC, FIB, DTREE) is absent from `ecc_areas` in `orchestration/research-priority.yaml` although the records belong to GOAL-ECDLP-001 / RQ-ECDLP-002; S-02 |

The other 21 `IDEA-20261018-*`, `IDEA-20261022-*`, `IDEA-20261024-*` and `H-PEXT/H-ICPERF` unmapped ids in `atlas/coverage.txt` belong to other groups and are not decided here.

Weak or unsupported coverage fits seen while reading the targets (observation, for the reviewer; none changed here):
- `H-ECDLP-281dd6` (Mersenne embedding degree identity) is mapped to `LEAD-TRF-prime-field-isogeny-to-weak`; `--match` on its statement ranks `LEAD-TRF-mov-small-embedding-degree` (13) and `LEAD-TRF-curve-parameter-transfer-audits` (11) above it (10).
- `H-ECDLP-242aa4` ("Degree-2 translation count") and `H-ECDLP-db6960` ("Chord-and-tangent check of one triple over F_17") are mapped to `LEAD-ICP-icperf-binary-pdp-solver` (a binary point-decomposition solver lead); the topical `--match` on their wording returns `LEAD-ICB-frobenius-search-symmetry`, `LEAD-ICB-oakley-quintic-tower` and `KR-IC-5765d2` and not that lead (appendix, records 15d481/1a5209/60f8de/975dd7/f3fac7).
- For `H-ECDLP-af796a` and `H-ECDLP-753879` (stage-0 instruments) the topical `--match` ranks `LEAD-TRF-cm-canonical-lift-heights` ahead of the mapped `EXO-global-lift-height` / `EXO-elliptic-net-eds` (lexical overlap on "canonical height" / "section").
- Retrieval gap: the PEXT idea's own wording does not retrieve `LEAD-TRF-small-genus-cover-general` (S-11).

**Verification line.** Every `evidence` path used in sections 2.1-2.13 and every id added to `ledger_refs` was checked for existence by `audit/verify_refs.py` (output reproduced in the last section of this file).


## 5. Per-path table (57 rows)

Columns: path, action, lead(s), reasoning (Observation first; "Interpretation (conditional)" where mine), proposed row edit. `ecdlp=false` only for `f952c0`.

| # | path | action | lead(s) | reasoning | proposed row edit |
|:--|:--|:--|:--|:--|:--|
| 1 | `ledger/decisions/DEC-20261018-083171.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base`<br>`LEAD-EXO-coordinate-statistic-leakage` | **Custody: approves 4 metadata-compatible reproductions of toy finite worksheets (3521b9, 087aea, 11c54d, 5d6ec1); no science.** decision=approve; EXP-ECDLP-3521b9 (of bfbe6f), 087aea (of 5f4f14), 11c54d (of 3c166b), 5d6ec1 (of 20ac31); scope: "no original scientific artifact or interpretation/status is changed"; knowledge_promotion.not_warranted. Lead mapping is via coverage.tsv of the original hypotheses (H-ECDLP-cba67a, 8c879e, 85fe43, 18c7f7); lexical --match on the record text is low-signal (see appendix). | subsumed by C-01, C-02 (no separate edit) |
| 2 | `ledger/decisions/DEC-20261018-0a2a22.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds` | **Custody: prepares additive three-output metadata adapters for stage-0 instruments f34097 and 903c48 (ee406e, 5c8854); unapproved preparation.** EXP-ECDLP-ee406e (of f34097, H-ECDLP-af796a, already in LEAD-EXO-global-lift-height ledger_refs) and 5c8854 (of 903c48, H-ECDLP-753879, in LEAD-EXO-elliptic-net-eds ledger_refs). "fresh_experiments: unapproved preparation only"; old science untouched. | subsumed by C-03, C-04 (no separate edit) |
| 3 | `ledger/decisions/DEC-20261018-0e1ce7.yaml` | `advances_lead` | `LEAD-EXO-four-list-ktree-join`<br>`LEAD-ICP-icperf-binary-pdp-solver`<br>`LEAD-ICP-prime-ic-constant-engineering`<br>`LEAD-EXO-padic-jet-canonical-lift`<br>`LEAD-RHO-dp-multitarget-precomputation`<br>`LEAD-EXO-invertible-hint-subset` | **Custody: preserves the failed 95f69f route-A invocation (env prefix error) and prepares direct-argv successors for 7 worksheets.** Observation: the first 95f69f native attempt failed before the science because the Coordinator prefixed env/GIT_CONFIG to a helper that compares real argv (rationale[0]); the failed source stays failed (RUN-ECDLP-f67842 infrastructure_error in the 8e211e inventory). Successors: c0c520 (of 95f69f), 615fcf (of c9110e), c64491 (of d68ac9), 524b38 (of efafc0), 417a94 (of f7310e), 30277c (of 3365b4), 324080 (adjacent x-rank). "Metadata/protocol failures are not mathematical negatives" (knowledge_promotion). | subsumed by C-08, C-09, C-10, C-11, C-12, C-06 (no separate edit) |
| 4 | `ledger/decisions/DEC-20261018-15d481.yaml` | `advances_lead` | `LEAD-ICP-icperf-binary-pdp-solver` | **Custody: approves fresh metadata-only successor EXP-ECDLP-53b1c3 of the invalid 615fcf (outer Git-only runtime env).** Original 615 native partial (13 files, manifest absent, second primary unlaunched) "remains immutable; no partial arithmetic is relabeled native success". 53b1c3 is a replay of the unchanged "Degree-2 translation count" worksheet (H-ECDLP-242aa4). | subsumed by C-09 (no separate edit) |
| 5 | `ledger/decisions/DEC-20261018-16581f.yaml` | `advances_lead` | `LEAD-RHO-dp-multitarget-precomputation` | **Custody: completes 11 finite-worksheet implementations and prepares a review_required c9 successor (3365b4) for the clipping-convention conflict.** EXP-ECDLP-3365b4 "Two explicit clipping conventions for the frozen finite cover worksheet" (H-ECDLP-3db46b). "c9 has a real definition conflict"; successor is review_required/unapproved; original contract untouched. "not actual worksheet evidence or a generic ECDLP conclusion". | subsumed by C-12 (no separate edit) |
| 6 | `ledger/decisions/DEC-20261018-1a5209.yaml` | `advances_lead` | `LEAD-ICP-icperf-binary-pdp-solver` | **Custody: declares outer-supervisor Git metadata control (core.preloadIndex=false) for untouched approved slots after 615 route-A Git status 128.** Observation: 615 route A driver0/checker1 failed Git status 128 after arithmetic; 13 real files preserved, manifest absent, route B never launched. Host-metadata control only; "supplies no native run success, second primary measurement ... or attack claim". | subsumed by C-09 (no separate edit) |
| 7 | `ledger/decisions/DEC-20261018-273b2d.yaml` | `advances_lead` | `LEAD-ICP-full-width-arity-grid` | **ICPERF m=8 GF(2^61) sorted-summand design (H-ICPERF-3982eb, EXP-ICPERF-554db4) revised to review_required; no run; unmapped H gets a coverage row.** decision=revise (GOAL-ICPERF-e6b6a4). Observations: v1 planted controls each reached the 300 s wall cap and all 64 natural calls were gated (EV-ICPERF-54ac6b, DEC-20261017-3b87bf: censored, "do not support a zero-yield or performance verdict"); successor binds gamma = b^(1/4) = x([r]P_source) = 70364449406991, sorts the eight signed summand points, U/S/U schedule; experiment review_required, execution_authorized false, no runs/ directory. Parent IDEA-20261017-3f46a5 is already in coverage.tsv -> LEAD-ICP-full-width-arity-grid, whose next_action names "the k11 ordinary-binary matched bases". --match query A ranks LEAD-ICP-icperf-binary-pdp-solver first and full-width-arity-grid is the one that already owns the parent idea; I follow the parent mapping and list the alternative. H-ICPERF-3982eb is currently unmapped (coverage.txt). | S-05: evidence + ledger_refs (H-ICPERF-3982eb, EXP-ICPERF-554db4, DEC-20261018-273b2d) on LEAD-ICP-full-width-arity-grid; next_action k11 clause points at EXP-ICPERF-554db4; coverage row H-ICPERF-3982eb -> LEAD-ICP-full-width-arity-grid |
| 8 | `ledger/decisions/DEC-20261018-28b2dd.yaml` | `advances_lead` | `LEAD-EXO-four-list-ktree-join` | **Custody: raw-archive receipt for EXP-ECDLP-c0c520 (reproduction of 95f69f); both primary routes output_validated.** Both separate primary-route receipts output_validated, driver/checker 0; snapshot a8bd3f44 passed native queue and Git hash verification. "Operational raw custody only, not independent scientific evidence interpretation." | subsumed by C-08 (no separate edit) |
| 9 | `ledger/decisions/DEC-20261018-30223e.yaml` | `advances_lead` | `LEAD-EXO-padic-jet-canonical-lift` | **Custody: raw-archive receipt for EXP-ECDLP-417a94 (reproduction of f7310e "Trivial-direction cancellation on two points"); output_validated.** Both primary-route receipts output_validated, snapshot 65db23d0. Operational custody only; no interpretation. | subsumed by C-11 (no separate edit) |
| 10 | `ledger/decisions/DEC-20261018-3fd5b1.yaml` | `advances_lead` | `LEAD-RHO-dp-multitarget-precomputation` | **Custody: raw-archive receipt for EXP-ECDLP-30277c (reproduction of 3365b4, c9 cover worksheet); output_validated.** Both primary-route receipts output_validated, snapshot 4b00d91d. Operational custody only. | subsumed by C-12 (no separate edit) |
| 11 | `ledger/decisions/DEC-20261018-43f3b8.yaml` | `advances_lead` | `LEAD-EXO-invertible-hint-subset` | **Custody: authorizes metadata/staging implementation for the adjacent x-rank instrument (EXP-ECDLP-daee4d / 324080); not an audit member.** Existing queue invalid and old manifest top-level only; "explicit adjacent 19th candidate is not authenticated audit 18 member". Implementation authorization and static defect review "are not measurement or conclusions". | subsumed by C-06 (no separate edit) |
| 12 | `ledger/decisions/DEC-20261018-50225a.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base`<br>`LEAD-EXO-coordinate-statistic-leakage` | **Custody: opens the lane BATCH-7ddcd6 for four additive successors of worksheets whose manifests the supervisor rejected.** decision=open_batch; four actual original driver/checker processes exited 0 but native output was invalid_output (rationale). Successors 3521b9, 087aea, 11c54d, 5d6ec1 stay review_required until native preapproval is approvable. Administrative. | subsumed by C-01, C-02 (no separate edit) |
| 13 | `ledger/decisions/DEC-20261018-59a33a.yaml` | `advances_lead` | `LEAD-EXO-curve-model-representation`<br>`LEAD-EXO-invertible-hint-subset`<br>`LEAD-EXO-lossy-object-propagation`<br>`LEAD-EXO-four-list-ktree-join`<br>`LEAD-ICP-icperf-binary-pdp-solver`<br>`LEAD-RHO-dp-multitarget-precomputation`<br>`LEAD-ICP-prime-ic-constant-engineering`<br>`LEAD-EXO-padic-jet-canonical-lift` | **Custody: authorizes role-separated implementation of 12 finite worksheets (080496, 4a3f03, 6491b4, 5a293e, 65f903, 911c16, 95f69f, c9110e, efafc0, c9c5a4, d68ac9, f7310e).** Twelve unexecuted worksheets with frozen approved specs and no implementation; "Implementation authorization does not complete scientific trials, prove claims, score predictions or authenticate the conditional historical eighteen-contract inventory." | subsumed by C-05, C-06, C-07, C-08, C-09, C-12, C-10, C-11 (no separate edit) |
| 14 | `ledger/decisions/DEC-20261018-5ef9a3.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base` | **Custody: zero-run preservation of partial native files of the failed 3521b9 attempt (RUN-ECDLP-03ccb4).** The native terminal void-source proposal refused duplicate ownership of retained partial files; a zero-run producer adopts them. "Administrative preservation after pre-driver failure provides no scientific result." | subsumed by C-01 (no separate edit) |
| 15 | `ledger/decisions/DEC-20261018-5faa6d.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds` | **Custody: terminal-snapshot preservation of stage-0 runs of f34097/903c48 (driver/checker 0, native invalid_output).** Targets are TASK ids only; the experiments are read from evidence_refs (experiments/EXP-ECDLP-f34097/runs/RUN-ECDLP-62ec3d, EXP-ECDLP-903c48/runs/RUN-ECDLP-4616a2). Observation: "native status invalid_output because code/environment/inputs/timing/result ... are absent". --match returns "no lead or known result shares vocabulary" (appendix) because the text has no mechanism words. | subsumed by C-03, C-04 (no separate edit) |
| 16 | `ledger/decisions/DEC-20261018-60f8de.yaml` | `advances_lead` | `LEAD-ICP-icperf-binary-pdp-solver` | **Custody: prepares fresh outer metadata successor (53b1c3) after the preserved 615 Git-status failure.** "No native success or second primary is inferred from partial arithmetic." Same direct child argv and 1 GiB limit; explicit outer Git environment declared prospectively under DEC-20261018-1a5209. | subsumed by C-09 (no separate edit) |
| 17 | `ledger/decisions/DEC-20261018-66f069.yaml` | `advances_lead` | `LEAD-ICP-prime-ic-constant-engineering` | **Custody: raw-archive receipt for EXP-ECDLP-c64491 (reproduction of d68ac9 "Window pair-sum counts"); output_validated.** Both primary-route receipts output_validated, snapshot ba096eec. Operational custody only. | subsumed by C-10 (no separate edit) |
| 18 | `ledger/decisions/DEC-20261018-6b8340.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base`<br>`LEAD-EXO-coordinate-statistic-leakage` | **Custody + observation: 4 fresh native reproductions output_validated; raw results equal the original outputs byte for byte.** EXP-ECDLP-4bb0ef (S3 worksheet replay), 3521b9, 087aea, 11c54d, 5d6ec1. Observation: "each new raw-result.json and preserved legacy-manifest.yaml equals the corresponding original actual output byte for byte"; "exact deterministic reproduction only"; "Repeated deterministic calibration is not independent" evidence. No status or interpretation change. | subsumed by C-01, C-02 (no separate edit) |
| 19 | `ledger/decisions/DEC-20261018-7ad1ee.yaml` | `advances_lead` | `LEAD-EXO-four-list-ktree-join` | **Custody: raw-archive receipt for EXP-ECDLP-65f903 ("exponent band contains 1/5, 64^2 below 64^3"); both routes output_validated.** Snapshot 9951ca2a. Operational custody only; native acceptance is not a theorem or independent review. | subsumed by C-08 (no separate edit) |
| 20 | `ledger/decisions/DEC-20261018-7c6c84.yaml` | `advances_lead` | `LEAD-EXO-invertible-hint-subset` | **Custody: raw-archive receipt for EXP-ECDLP-4a3f03 ("Orbit factors and the anomalous trace"); output_validated.** Snapshot e798e465. Operational custody only. | subsumed by C-06 (no separate edit) |
| 21 | `ledger/decisions/DEC-20261018-7cf349.yaml` | `advances_lead` | `LEAD-EXO-lossy-object-propagation` | **Custody: raw-archive receipt for EXP-ECDLP-5a293e ("Negation invariance of two x-line maps over F_17"); output_validated.** Snapshot 1bfc925f. Operational custody only. | subsumed by C-07 (no separate edit) |
| 22 | `ledger/decisions/DEC-20261018-7ee3c1.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base`<br>`LEAD-EXO-coordinate-statistic-leakage` | **Custody: amends dispatch queue so original executor tasks cover supervisor-generated artifacts (bfbe6f, 5f4f14, 3c166b, 20ac31).** "The supervisor refused before any scientific trial because original executor artifact_paths omitted GENERATED files." Artifact-custody repair; "no scientific evidence". | subsumed by C-01, C-02 (no separate edit) |
| 23 | `ledger/decisions/DEC-20261018-808baa.yaml` | `advances_lead` | `LEAD-EXO-four-list-ktree-join` | **Custody: raw-archive receipt for EXP-ECDLP-911c16 ("theta coefficient leaves a positive cross-energy remainder"); output_validated.** Snapshot 22be797d. Operational custody only. | subsumed by C-08 (no separate edit) |
| 24 | `ledger/decisions/DEC-20261018-8e211e.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base`<br>`LEAD-EXO-coordinate-statistic-leakage`<br>`LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds`<br>`LEAD-EXO-curve-model-representation`<br>`LEAD-EXO-invertible-hint-subset`<br>`LEAD-EXO-lossy-object-propagation`<br>`LEAD-EXO-four-list-ktree-join`<br>`LEAD-ICP-icperf-binary-pdp-solver`<br>`LEAD-ICP-prime-ic-constant-engineering`<br>`LEAD-EXO-padic-jet-canonical-lift`<br>`LEAD-RHO-dp-multitarget-precomputation` | **Closeout inventory of 41 native attempts (32 output_validated, 7 invalid_output, 2 infrastructure_error); carrier of consolidated entries C-01..C-12.** Observation (reports/ideas_execution_20261018/native-campaign-closeout/actual-native-inventory.json): 41 attempts = 6 legacy metadata reproductions + 24 finite primary RUNs + 2 dependent adjacent stages (+ failed/invalid originals). rationale[1] preserves, unreviewed: square-bias strict miss (EXP-20ac31), slope unscored (5f4f14), chord-sign prediction false (efafc0), c9 definition gap/descriptive arm (c9c5a4/3365b4). "Audit18 membership remains conditional"; no independent arithmetic certificate for the adjacent checker. This is the single record each C-nn entry cites. | consolidated evidence entries C-01..C-12 (section 2.8); ledger_refs += DEC-20261018-8e211e |
| 25 | `ledger/decisions/DEC-20261018-975dd7.yaml` | `advances_lead` | `LEAD-ICP-icperf-binary-pdp-solver` | **Custody: raw-archive receipt for EXP-ECDLP-53b1c3 (successor of the invalid 615fcf); both routes output_validated.** Snapshot 02ae6179. Operational custody only. | subsumed by C-09 (no separate edit) |
| 26 | `ledger/decisions/DEC-20261018-a7a0fd.yaml` | `advances_lead` | `LEAD-ICE-curve-presentation-invariance` | **Approves matched legacy/repaired s4_expr rerun EXP-SEMAEV-93d5cc (7 trials); integrity exposure of S4-consuming runs incl. ICINV m4 columns; no effect claimed.** Protocol approval (H-SEMAEV-94dab2 specified->approved, pre-run): "Approval is not evidence". Context: harness/semaev.py s4_expr dropped x3 before 2026-08-13; exposed runs EXP-MTIC-001, EXP-FIB-001, RUN-ICINV-e0cd8f-m3class (docs/reports/2026-10-18-semaev-s4-factor-base-audit.md). LEAD-ICE-curve-presentation-invariance lists EV-ICINV-8afb64 in ledger_refs (decisive m=3 families; "m=4 support and singular locus computed as required secondaries", line 104), and that evidence cites RUN-ICINV-e0cd8f-m3class; its evidence entry EV-ICINV-343679 rests on RUN-ICINV-geom-* runs that the audit lists as NOT affected, and EV-ICINV-6b6264 reports S_3 supports from the s0/s1 attempts (audit: failed_infrastructure, no results). RUN-SEMAEV receipts in experiments/EXP-SEMAEV-93d5cc/runs: 6 of 7 output_validated (0/0), RUN-SEMAEV-500a81 has no receipt. No evidence record, no review. Area SEMAEV is not in ecc_areas, so --coverage never listed H-SEMAEV-94dab2. | S-02: exposure note + ledger_refs on LEAD-ICE-curve-presentation-invariance; coverage row H-SEMAEV-94dab2 -> LEAD-ICE-curve-presentation-invariance |
| 27 | `ledger/decisions/DEC-20261018-ae74db.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds` | **Custody + observation: native metadata reproductions ee406e and 5c8854 output_validated (driver/checker 0, 13-file outputs).** Timing differences between separate processes are not suppressed. "Operational reproduction and repeated in-sample calibration are not independent confirmation, mathematical falsification, attack progress, scientific status or proof." | subsumed by C-03, C-04 (no separate edit) |
| 28 | `ledger/decisions/DEC-20261018-b3861f.yaml` | `advances_lead` | `LEAD-RHO-dp-multitarget-precomputation` | **Custody: prepares explicit c9 descriptive successor (3365b4) with both min(D,tau) and min(D+1,tau) arms.** "The original c9 contract has a genuine cutoff-definition conflict"; runtime prediction_match scoped to original-compatible clipD; clipDplus1 descriptive. Source preparation "not measurement, scientific interpretation, proof or ECDLP progress". | subsumed by C-12 (no separate edit) |
| 29 | `ledger/decisions/DEC-20261018-c4352a.yaml` | `advances_lead` | `LEAD-EXO-four-list-ktree-join`<br>`LEAD-ICP-icperf-binary-pdp-solver`<br>`LEAD-ICP-prime-ic-constant-engineering`<br>`LEAD-EXO-padic-jet-canonical-lift`<br>`LEAD-RHO-dp-multitarget-precomputation`<br>`LEAD-EXO-invertible-hint-subset` | **Custody: approves 7 pushed-source native protocols (c0c520, 615fcf, 524b38, c64491, 417a94, 30277c, 324080).** All seven native prospective checks approvable:true, blockers []. "Metadata protocol approval does not establish independent mathematical verification, original hypothesis support/falsification, authenticated historical18membership". | subsumed by C-08, C-09, C-10, C-11, C-12, C-06 (no separate edit) |
| 30 | `ledger/decisions/DEC-20261018-c63577.yaml` | `advances_lead` | `LEAD-EXO-invertible-hint-subset` | **Custody: raw-archive receipt for EXP-ECDLP-6491b4 ("Three cells of the query-bounded success bound"); output_validated.** Snapshot 19a39d88. Operational custody only. | subsumed by C-06 (no separate edit) |
| 31 | `ledger/decisions/DEC-20261018-ca4056.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds` | **Custody: approves the two three-output metadata reproductions (ee406e, 5c8854); historical readings stay in-sample.** Adapter "passed 23 synthetic controls without executing a real frozen fixture". "makes no mathematical, section-cost, net-information, ECDLP attack, goal or hypothesis transition". | subsumed by C-03, C-04 (no separate edit) |
| 32 | `ledger/decisions/DEC-20261018-d763f3.yaml` | `advances_lead` | `LEAD-RHO-dp-multitarget-precomputation` | **Custody: approves the c9 two-convention descriptive successor (3365b4); known values explicitly in-sample.** Original c9 contract/status unchanged; "not an execution, scientific validation/falsification of original c9, generic graph constant, mathematical proof or ECDLP result". | subsumed by C-12 (no separate edit) |
| 33 | `ledger/decisions/DEC-20261018-d8801f.yaml` | `advances_lead` | `LEAD-EXO-invertible-hint-subset` | **Custody: raw-archive receipt for the adjacent staged x-rank instrument EXP-ECDLP-324080; two dependent stages output_validated.** Old checker is vocabulary/file-presence validation only (inventory: labels S0-FREEZE-OK, O-EXCESS; no independent arithmetic certificate). Snapshot d268c8a6. | subsumed by C-06 (no separate edit) |
| 34 | `ledger/decisions/DEC-20261018-ea671a.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-EXO-elliptic-net-eds` | **Custody: appends 16 supervisor provenance/log paths to the f34097/903c48 queue cards so native admission can proceed.** "Administrative readiness and an anticipated schema defect are not mathematical evidence, execution success or hypothesis/goal transitions." | subsumed by C-03, C-04 (no separate edit) |
| 35 | `ledger/decisions/DEC-20261018-f3fac7.yaml` | `advances_lead` | `LEAD-ICP-icperf-binary-pdp-solver` | **Custody: raw-archive receipt for EXP-ECDLP-524b38 (reproduction of efafc0 "Chord-and-tangent check of one triple over F_17"); output_validated.** Snapshot 7fdfc7db. The 8e211e closeout preserves "chord sign prediction false" for the original (unreviewed observation). | subsumed by C-09 (no separate edit) |
| 36 | `ledger/decisions/DEC-20261018-f4c865.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base` | **Custody: additive metadata replacement 4bb0ef after 3521b9 infrastructure_error (Git threaded lstat memory); process-local preloadIndex=false.** Observation: first successor failed before the scientific driver; read-only diagnostic shows core.preloadIndex=false succeeds under the same 256 MiB limit. "Infrastructure repair and deterministic metadata calibration make no mathematical hypothesis, goal, speedup or attack claim." | subsumed by C-01 (no separate edit) |
| 37 | `ledger/decisions/DEC-20261018-f952c0.yaml` | `not_ecdlp` | - | **Administrative: closes 7 finished campaign lanes and publishes the report-archive receipt; no mechanism content, no lead row affected.** targets are BATCH ids only; "Administrative lane lifecycle and exact postcommit receipt only. Goal stays active; ... scientific statuses unchanged." Coded not_ecdlp in the sense "no coverage row / no lead edit"; the campaign itself is GOAL-ECDLP-001. | none |
| 38 | `ledger/decisions/DEC-20261018-f9e8d5.yaml` | `advances_lead` | `LEAD-ICP-algebraic-membership-factor-base` | **Custody: approves EXP-ECDLP-4bb0ef, a deterministic metadata-only S3 engineering replay (preload-index prefix, 256 MiB).** Predecessor infrastructure_error stays immutable; 8 actual native files preserved by a zero-run producer. "not mathematical evidence or measured attack improvements". | subsumed by C-01 (no separate edit) |
| 39 | `ledger/decisions/DEC-20261018-fd0a18.yaml` | `advances_lead` | `LEAD-EXO-curve-model-representation` | **Custody: raw-archive receipt for EXP-ECDLP-080496 ("Rational points and the coordinate cycle on the Hesse cubic over F_97"); output_validated.** Snapshot 47ad70ed. Operational custody only. | subsumed by C-05 (no separate edit) |
| 40 | `ledger/decisions/DEC-20261019-5b9240.yaml` | `advances_lead` | `LEAD-ICE-curve-presentation-invariance` | **Records the interrupted mtic-010b attempt (RUN-SEMAEV-500a81) as non-evidence and approves one-trial successor EXP-SEMAEV-88c46c.** Amendment AMD-EXP-SEMAEV-93d5cc-20261019-mtic010b-successor; "The interruption is infrastructure; the cell is unmeasured, not negative." RUN-SEMAEV-980e8c under EXP-SEMAEV-88c46c has no receipt in the tree. Not evidence. | S-02 (same exposure note); no separate edit |
| 41 | `ledger/decisions/DEC-20261019-ebf1dc.yaml` | `advances_lead` | `LEAD-ICE-curve-presentation-invariance` | **Records the second interrupted attempt (RUN-SEMAEV-980e8c) and approves successor EXP-SEMAEV-6e9dcf for the mtic-010b cell.** "The interruption is infrastructure; the cell is unmeasured, not negative." experiments/EXP-SEMAEV-6e9dcf/runs/ exists and is empty. Not evidence; a repeat made visible as a repeat. | S-02 (same exposure note); no separate edit |
| 42 | `ledger/decisions/DEC-20261022-9aec2b.yaml` | `advances_lead` | `LEAD-ICP-coincidence-harvest-structured-base` | **Records 5 runs of EXP-PFDR-bb0d26 (log-GAP dual sum-product probe, toy) as UNREVIEWED observations: O-NULL headline, no flagged cell; review pending.** Observation (producer values, quoted from the decision): outcome O-NULL, headline SUPPORT_SCOPED, 44 powered cells of 45 (b20-r3-n4096 invalid: 46/50 curves ok after 4 degenerate jobs), largest /kappa-1/ = 0.0414 (b28-r1-n256, CI [1.0100, 1.0743]), largest /z/ = 3.13 (b24-r1-n2048), smallest planted kappa 1.2885 (plant z >= 21.9), calibration mean -0.268 sd 0.974, failed_infrastructure 0, replication trial ran zero jobs (no flagged cell). H-PFDR-727bfc stays approved; criteria readings are "observations of producer-computed values", inference belongs to the independent review round (NA-1, pending). Interpretation (conditional): consistent with the lead's kappa-near-1 reading at 20-28 bits; toy only, a null does not exclude other labelings. | S-03: next_action no longer lists bb0d26 as scheduled; best_measured gets an UNREVIEWED-labelled clause; ledger_refs += DEC-20261022-9aec2b, EXP-PFDR-bb0d26 |
| 43 | `ledger/decisions/DEC-20261022-e5f45c.yaml` | `advances_lead` | `LEAD-EXO-global-lift-height`<br>`LEAD-TRF-prime-field-isogeny-to-weak`<br>`LEAD-ICP-algebraic-membership-factor-base` | **SNFS-G (Mersenne/Solinas special-form prime) contracts: zero valid runs; impediment IMP-SNFSG-MANIFEST-20261022; custody reconciliation of RUN-ECDLP-18d26b; no evidence.** revise. Observation: five receipts for four approved trials, none a valid run record (EXP-ECDLP-84af7b attempt A infrastructure_error: cargo missing; attempt B invalid_output, alias RUN-ECDLP-d12308; EXP-ECDLP-8cc60d, 4c6a09, ad27ad invalid_output: flat manifest.yaml refused by run schema). "No metric value of any SNFS-G hypothesis exists"; "asserts nothing about H-ECDLP-2f1033, H-ECDLP-281dd6, H-ECDLP-4da36f, H-ECDLP-986bab". Route: versioned manifest transport (NA-1), fresh run ids. Coverage maps H-ECDLP-2f1033/4da36f -> EXO-global-lift-height, 281dd6 -> TRF-prime-field-isogeny-to-weak, 986bab -> ICP-algebraic-membership-factor-base; the 281dd6 mapping is weak (see coverage notes). A timeout/format refusal is not evidence. | S-04: evidence note (no-valid-run status) on the three mapped leads; EXO-global-lift-height next_action gains the NA-1 transport step; no best_measured number added |
| 44 | `ledger/decisions/DEC-20261023-039ddf.yaml` | `advances_lead` | `LEAD-TRF-padic-canonical-section` | **reject_scoped on H-CZLIFT-d37231 (F_p^* section calibration): naive integral section exceeds 1/p exactly where g^d mod p^2 < p; Teichmuller/Hensel held.** Observations: Teichmuller section homomorphic on every sampled pair, functional vanishes; random-Hensel ratio = d on 3 of 3200 pairs vs 5.39 expected; naive section = d on 13 and 20 of 1600 pairs (z 7.65, 9.14), exactly on pairs with g^d mod p^2 < p (Eisenstein logarithmic property); naive section homomorphic iff x*y < p. Scope toy (80 primes < 2000), smallest primitive root, F_p^* only. Red team: "no elliptic analogue" breaks (integral multiples of a small global point recover d exactly; review-side, two curves). Interpretation (conditional): this is the size effect the lead already names, so the lead's "only failure ... is a size effect" is consistent, but "any non-homomorphic section recovers d only at the random 1/p rate" is not carried by it. KN-FIND-c71e5d promoted. | S-01: obstruction.statement rewrite, best_measured replace, evidence + ledger_refs on LEAD-TRF-padic-canonical-section (with 36b4f0, 2e7447, 9de83a, 23d64d) |
| 45 | `ledger/decisions/DEC-20261023-147f9f.yaml` | `advances_lead` | `LEAD-TRF-anomalous-padic-lift` | **support (toy, scoped) for H-CZLIFT-889c9d: Serre-Tate canonical-lift degeneracy of Smart on anomalous CM curves; framed as known theory (Belding 2007 s7).** Observation: degeneracy flag v_p(z([p]P^)) >= 2 agrees with the j-distance rule v_p(Delta j) >= 2e on 14,616/14,616 rows (29 class-number-one CM anomalous curves, 7 <= p <= 1373, precision p^8); Smart ratio recovered d on 2,052/2,052 rows per seed when v_p(Delta j) < 2e; on degenerate lifts next-digit successes consistent with the random-section null (matching null 1/(p+1)); j = 0 threshold only pinned to (3, 6]. "novelty: none". Replaces the lead's "review pending". KN-FIND-3c7e19. | S-07: replace "review pending" in LEAD-TRF-anomalous-padic-lift obstruction.statement; evidence + ledger_refs; no disposition change |
| 46 | `ledger/decisions/DEC-20261023-19c53b.yaml` | `advances_lead` | `LEAD-ICE-semaev-cover-monodromy` | **Portfolio ranking: routes IDEA-20260803-ff7415 (2^(n-1) compounding clause over F_{q^n}) to a re-scope IDEA-20261023-f15270; extension-field, no evidence.** decision=approve, mode portfolio, "no trials"; opens BATCH-7ca353 under GOAL-PATH-001; "Nothing here is evidence. It asserts nothing about compounding, about relation rates, or about any exponent." ff7415 and its siblings (a9a95d, 90df50, d29a71, a1b81b, H-MONO-663fb4) are mapped to LEAD-ICE-semaev-cover-monodromy, whose revisit_when names KN-OPEN-62c870 Q1/Q3; the compounding clause is Q3 (a yield-counting question), distinct from LEAD-ICE-semaev-yield-model-coset-typing (m! factor, binary). Scope: F_{q^n}; "no prime-field statement follows". IDEA-20261023-f15270 is unmapped in coverage.txt; no prior_art.lead field (rule starts 20261025). | S-06: ledger_refs += DEC-20261023-19c53b, IDEA-20260803-ff7415, IDEA-20261023-f15270; evidence note; coverage row IDEA-20261023-f15270 -> LEAD-ICE-semaev-cover-monodromy |
| 47 | `ledger/decisions/DEC-20261023-26a6de.yaml` | `advances_lead` | `LEAD-TRF-global-lift-small-height` | **weaken H-CZLIFT-9a32e9: (log H)^{r/2} count law supported, "uniform reduction" contradicted as stated; obstruction survives as fixed-rank counting (derivation, conditional).** Observations (eight-curve ladder, naive height <= 3e5, p = 103..20011, toy): coverage ratio 1.0330/1.0333 vs uniform-null upper band edges 1.0023/1.0041 (0 of 200 reps reach it); frozen criterion met but uninformative (any point set gives ratio <= min(x,1)/(1-e^-x)); kernel vectors have height >= 2 log p - c_E (D2); pigeonhole: spread saves at most 2 ln 2 in N (0.327 at r=2 to 0.093 at r=7 in log log H_half). C4 "exponential height" is not a measurement; C5 twists/E(K) untested. Interpretation (conditional): the lead's best_measured "small points reduce like uniform points" is not carried; the closure rests on D7 (derivation, conditional on T1-T4 beyond toy scale per DEC-20261024-23d64d and CORR-20261024-63d682 K1) plus conditional JKSST. | S-08: rewrite obstruction.statement, replace best_measured, evidence + ledger_refs on LEAD-TRF-global-lift-small-height; flag closed_known fit |
| 48 | `ledger/decisions/DEC-20261023-2e7447.yaml` | `decides_lead` | `LEAD-TRF-padic-canonical-section` | **refine H-CZLIFT-fba874 (digit-character spectrum of s_tor): approved->analyzed, preliminary; 30 of 72 records blind; title claim untested; KN-OPEN-d3a6f0 promoted.** Observation (EV-CZLIFT-764f54): on the 42 power-bearing records (33 CM-canonical, 9 random curves; 53 <= p <= 571, 47 <= n <= 613) no single-digit function a_i of x or y of s_tor([k]P), i = 0..4, has half-range correlation >= rho_min = sqrt((ln((p-1)n)+12)/h) (0.28-0.98, median 0.50) with any single (additive character, character of Z/n); the 30 records with n <= 41 carry no information; the instrument cannot test digit 0, chirp, inverse or Legendre-bit leaks; the shuffled control is contaminated (probability of its zero about 0.47). KN-OPEN-d3a6f0: growth of the maximal Fourier mass Phi_i(n) of digit characters against n^(-1/2) and the n^(-1/4) Fourier-learning breakeven; no Weil-type bound known for i >= 1. Interpretation (conditional): the lead forecloses "p-adic digits of the torsion section" with a theorem that addresses the formal logarithm and homomorphic sections only; the digit-character claim is open at the program's own preliminary strength. This is the only exponent-relevant open item in the group (prime field E/F_p, point of prime order n). | S-01 (same lead): next_action from DEC-20261024-23d64d N-3(1); disposition_change closed_obstructed -> open_next_step (conditional) |
| 49 | `ledger/decisions/DEC-20261023-36b4f0.yaml` | `advances_lead` | `LEAD-TRF-padic-canonical-section` | **support H-CZLIFT-6d4ed1 (derivation, replicated): prime-to-p torsion section is the unique homomorphic section, Smart functional vanishes; H2 "full break" answered negatively.** Scope: torsion-section, cost, vanishing and tau-identity clauses at derivation tier (uniform in p >= 5, n != p, any good-reduction lift); identity-readout rate at toy tier, detection floor 4.2x-5.2x of 1/p; instruments agree on 0 exceptions in 1116 pairs (p <= 600). Limitations: "One readout (identity); planted discrete-log oracles pass it. No claim that the non-torsion sections carry no information about d"; the arm comparison is confounded and powerless. It confirms (derivation, not machine-verified) the homomorphic-section/formal-log half of the lead's obstruction that stays closed; it moves no disposition (the reopen is decided by 2e7447 and 23d64d). KN-FIND-7e2b94. | S-01 (same lead): obstruction restated at derivation tier and narrowed; evidence + ledger_refs |
| 50 | `ledger/decisions/DEC-20261023-488023.yaml` | `advances_lead` | `LEAD-TRF-global-lift-small-height` | **weaken H-CZLIFT-cb95b8: "no xedni-type relation within bound 6" is false (1 relation in 3200 trials, certificate); rarity reading consistent.** Observation (EV-CZLIFT-ee9b23, certificate): 1 relation in 3200 trials (3.1e-4, CI [7.9e-6, 1.7e-3]) for the 8 primes, r in {2,3}, y != 0 sampler, symmetric lifts, bound 6; counterexample certificate = explicit tangent instance on Y^2 = X^3 - 1728X - 27423. JKSST Theorem 4.1 is conditional and vacuous at p <= 12809; JKSST empirical law expects 0.855, observed 1. Strength preliminary. Contradicts the lead's best_measured clause "xedni dependence never seen within relation bound 6". | S-08 (same lead): best_measured replaced; evidence + ledger_refs; also text note on LEAD-ICP-char0-lifting-xedni-smoothness (S-09) |
| 51 | `ledger/decisions/DEC-20261023-66af3b.yaml` | `advances_lead` | `LEAD-TRF-anomalous-padic-lift` | **pause: run set of EXP-CZLIFT-7c8d73 (level-1 Serre-Tate splitting, H-CZLIFT-d3dc4b) ruled inadmissible; no evidence, no status moved.** Frozen control C1 fails as written, checker evaluates neither C1 nor a non-vacuous C2, load-bearing quantity is not the specified quantity on 18 of 29 curves (J3); "a superseding contract is required, not a replication". "Under AGENTS.md core rule 5 they say nothing against H-CZLIFT-d3dc4b." Only a note on the lead: the splitting construction has no admissible run. | S-07 (note in obstruction.statement); no separate edit |
| 52 | `ledger/decisions/DEC-20261023-6931ab.yaml` | `advances_lead` | `LEAD-TRF-global-lift-small-height` | **weaken H-CZLIFT-27a184 (rank-record curves): S1 count holds as observation, interpretation unsupported, "reduce uniformly" contradicted; scope three reduced models.** EV-CZLIFT-b6fe48: S3/S4 "cannot fail" (instrument ceiling min(x,1)/(1-e^-x)), S2 met with uninformative upper side; generalisation to rank-record curves contradicted by Elkies-Watkins rows. Scope: three named reduced minimal models, H <= 3e5, p = 103..20011, toy. "Not support ... not reject_scoped ... not inconclusive". | S-08 (same lead): evidence + ledger_refs |
| 53 | `ledger/decisions/DEC-20261023-9de83a.yaml` | `advances_lead` | `LEAD-TRF-padic-canonical-section`<br>`LEAD-TRF-anomalous-padic-lift` | **refine H-CZLIFT-bd2017: exact canonical-lift/torsion identities hold at 10^4 <= p <= 10^5 (toy, p <= 97813); the 1/p clauses carry no evidence.** Observation (EV-CZLIFT-e9a7cf): j-distance rule 0 disagreements in 4608 rows (164 cells); Smart ratio = d on 1152/1152 pert_p rows; five torsion rates and tau identity 576/576 pairs (same-code); non-canonical recoveries 0 of 3456 anomalous-degenerate rows and 0 of 576 per torsion section; 95% one-sided bounds 8.7e-4 and 5.2e-3 per row "do not test the 1/p rate" (likelihood ratio 0.85). Tier is toy (spec label "medium" is a mislabel). | S-01 and S-07: evidence + ledger_refs; narrows "random 1/p rate" wording |
| 54 | `ledger/decisions/DEC-20261023-fdc4af.yaml` | `advances_lead` | `LEAD-TRF-global-lift-small-height` | **pause: run set of EXP-CZLIFT-8c50ea (small points of E(K), K = Q(2^{1/3})) ruled inadmissible; E(K) claim has no evidence.** Enumerated set is not the frozen box; sealed blind count disagrees (37a1: 33/15 vs 27/15 main, 39/17 vs 27/15 replication); replication not an independent instance; two metric definitions differ. No result of the returned run set is used. Consequence for the lead: its statement that the program re-measured uniform reduction "over Q(2^{1/3})" has no admissible basis. | S-08 (same lead): scope clause on E(K); no separate edit |
| 55 | `ledger/decisions/DEC-20261024-23d64d.yaml` | `decides_lead` | `LEAD-TRF-padic-canonical-section`<br>`LEAD-TRF-global-lift-small-height` | **Synthesis of the 10-record CZLIFT round: RQ-CZLIFT-b9f765 cannot close (digit encodings of s_tor open, E(K) untested); KR-IC-cd159a overstated; ranks the digit-character successor.** status_transitions empty. h2_established_at_toy_tier.not_established: "Whether any coordinate or digit encoding of s_tor carries d"; rq_closure.missing includes "Coordinate and digit encodings of s_tor must be excluded while KN-OPEN-d3a6f0 is open"; N-3(1): "Exponent-targeting successor on KN-OPEN-d3a6f0 ... n to about 10^4..10^5, symmetry-matched null, per-record floors" (behind the zero-run control C1, N-2). canonical_graphs_checked: KR-IC-cd159a "Overstated; corrected by CORR-20261024-63d682" (claim narrowed, status proven -> heuristic, "lift to characteristic zero" and "canonical lift for ECDLP" not foreclosed by JKSST; superseding row not yet committed). Ten CORR records: RQ decision_target (a) A1-A5 rewritten (CORR-20261023-6e10a2). | S-01 (digit successor as next_action; disposition_change), S-08 (obstruction basis), S-09/S-10 (KR dependency notes on ICP-char0-lifting-xedni-smoothness, TRF-cm-canonical-lift-heights) |
| 56 | `ledger/decisions/DEC-20261024-992998.yaml` | `advances_lead` | `LEAD-TRF-small-genus-cover-general` | **Approves EXP-PEXT-212d5c (GHS cover genus floor at n=7, odd characteristic; 6 trials); no runs yet; extension-field cover census.** Extends the program's own n=3/n=5 GHS cover censuses (research/ghs_cover_census_n5_20261013 in repo crypto, vendored by the spec) to n=7; mechanism: smallest genus of the (Z/2)^m compositum of the n conjugate double covers, g = 2^{m-2}(r-4)+1; hypothesis H-PEXT-d536a1 says span dimensions are degrees of divisors of x^7-1 over F_2 ({1,3,4,6,7}). "Asserts nothing about any floor, spectrum or mechanism". experiments/EXP-PEXT-212d5c/runs/ exists and is empty. Nearest leads: TRF-small-genus-cover-general (closed_obstructed, Riemann-Hurwitz census of Kummer/GHS covers, F_{q^3} and k = 6,10,14), ICP-gfp5-odd-char-cover (n=5, open_blocked), TRF-odd-char-descent-smith-quartic (n=3). Not a new mechanism: same cover-genus-floor object at a new n. IDEA-20261024-b58e07 predates the prior_art.lead rule. | S-11: ledger_refs + evidence on LEAD-TRF-small-genus-cover-general; related note on LEAD-ICP-gfp5-odd-char-cover; coverage rows H-PEXT-d536a1, IDEA-20261024-b58e07 -> LEAD-TRF-small-genus-cover-general |
| 57 | `ledger/decisions/DEC-20261024-e29f4c.yaml` | `advances_lead` | `LEAD-TRF-small-genus-cover-general` | **Opens GOAL-PEXT-4a1d6b / RQ-PEXT-7c3e91, records IDEA-20261024-b58e07 as first target, adds area PEXT to the ECC set; no evidence.** Approves no experiment; "n = 7 is the decision-changing next case ... at n = 3 and 5 that leaves only {1, n-1, n}, so the two censuses cannot separate" the 2-torsion-type reading from the x^n-1 factorisation reading (Lemma M of the sibling n = 5 study). Goal administration plus a research-priority edit; the PEXT area is now in ecc_areas so --coverage will list its records. | S-11 (same edit set as 992998) |

## Appendix A. Raw `lead_atlas.py --match` top hits for every record

Environment: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` set as in the task. Query A = decision label + target titles; query B = scientific claim of the first target hypothesis (or the decision scope); query C (topical, campaign records only) = mechanism wording of the mapped leads. Top 5 lines per query, columns: score, id, disposition, title. A low score is not novelty (the tool says so) and for custody records the A/B hits mostly reflect process vocabulary; the table in section 5 states which lead was chosen and why.


### DEC-20261018-083171

**A** `approve Metadata-compatible deterministic reproduction of EXP-ECDLP-bfbe6f; Metadata-compatible deterministic reproduction of EXP-ECDLP-5f4f14; Metadata-compatible deterministic reproduction of EXP-ECDLP-3c166b; Metadata-compatible deterministic reproduction of EXP-ECDLP-20ac31`
```
    2  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
    1  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41 ; chord slope fibres under translation, x-count gap of two curves, square bias of four-term x-product, coordinate statistic of points`
```
   24  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   18  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   16  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

### DEC-20261018-0a2a22

**A** `prepare two additive three output metadata reproductions Native metadata reproduction of the unchanged three-output EXP-ECDLP-f34097 instrument; Native metadata reproduction of the unchanged three-output EXP-ECDLP-903c48 instrument`
```
    5  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    4  KR-RHO-cd86f5                                known_result       r-adding walks and the walk constant
    4  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
```
**B** `On the preregistered constant Weierstrass surface y^2 = x^3 + x + 30 over F_31, with planted degree-0 section (x, y) = (2, 3), the known-generator oracle recovers coefficient vector (2, 0, 3, 0) at m…`
```
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
```
**C** `stage-0 instrument planted degree-0 section canonical height of lift over F_31 ; elliptic net rank-1 zeros stage-0 instrument y^2 = x^3 + 2 over F_11 net information`
```
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   13  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   12  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
```

### DEC-20261018-0e1ce7

**A** `preserve actual invocation failure and prepare additive direct argv successors Direct native invocation reproduction of EXP-ECDLP-95f69f; Direct native invocation reproduction of EXP-ECDLP-c9110e; Direct native invocation reproduction of EXP-ECDLP-d68ac9; Direct native invocation reproduction of EXP-ECDLP-efafc0`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    4  KR-RHO-cd86f5                                known_result       r-adding walks and the walk constant
    4  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
```
**B** `Let low(x) = x mod 4. For every pair of residues (u, v) in 0..3, the set of low((a+b) mod 17) over a, b in 0..16 with low(a)=u and low(b)=v has size 2. There are 136 pairs (a, b) where this value dif…`
```
    8  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, 
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
    6  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    5  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```
**C** `Wagner k-tree four-list join exponent band cross-energy remainder branching of 2-bit reduction addition modulo 17 ; degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet ; window pair-sum counts constant engineering prime-field index calculus`
```
   20  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
   17  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   16  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

### DEC-20261018-15d481

**A** `approve Direct native invocation reproduction of EXP-ECDLP-615fcf`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    2  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
```
**B** `On the curve y^2 = x^3 + 8x^2 + 2x over the field with 11 elements there are 12 rational points, counting the identity. For each of the three points S among (0,0), (1,0) and (2,0), exactly four trans…`
```
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   11  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
```
**C** `degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet`
```
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
```

### DEC-20261018-16581f

**A** `complete existing finite worksheet implementations and prepare explicit c9 successor Two explicit clipping conventions for the frozen finite cover worksheet`
```
    7  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgrou
    6  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    6  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into th
    5  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    5  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit an
```
**B** `On the path of 8 points whose successor is the next index, stopping at the last point, the depth-4 covers of the stored points 3 and 5 have sizes 4 and 5. Their intersection has size 3 and their unio…`
```
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    7  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```
**C** `cover counts and band products clipping conventions distinguished points multitarget finite cover`
```
   17  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    8  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    7  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    7  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
```

### DEC-20261018-1a5209

**A** `declare outer supervisor git metadata control for untouched approved slots Direct native invocation reproduction of EXP-ECDLP-c9110e`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
```
**B** `On the curve y^2 = x^3 + 8x^2 + 2x over the field with 11 elements there are 12 rational points, counting the identity. For each of the three points S among (0,0), (1,0) and (2,0), exactly four trans…`
```
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   11  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
```
**C** `degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet`
```
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
```

### DEC-20261018-273b2d

**A** `revise Bounded k11 solver-to-certificate viability on matched binary bases; Canonical summand order and gamma-bound binary m8 solver feasibility; Gamma-bound blind schedule and sorted-summand binary m8 positive gate`
```
   11  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the IC
   11  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    9  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    9  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    9  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
```
**B** `On certified GF(2^61), r=576460752557211763, both frozen B=316 k11 m=8 bases yield checked solver models for their separate positive controls and at least one certified natural projected relation ove…`
```
   13  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   10  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
    9  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    8  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
```

### DEC-20261018-28b2dd

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-95f69f`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `Let low(x) = x mod 4. For every pair of residues (u, v) in 0..3, the set of low((a+b) mod 17) over a, b in 0..16 with low(a)=u and low(b)=v has size 2. There are 136 pairs (a, b) where this value dif…`
```
    8  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, 
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
    6  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    5  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```
**C** `Wagner k-tree four-list join exponent band cross-energy remainder branching of 2-bit reduction addition modulo 17`
```
   18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
    7  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    5  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)
```

### DEC-20261018-30223e

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-f7310e`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `Over the integers, with a equal to 1 and b equal to 1, the point (2, 1) has curve defect 10 and identity gap 30. The point (4, 2) has curve defect 65 and identity gap 195. Each gap equals three times…`
```
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    6  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    5  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    5  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
```
**C** `trivial-direction cancellation on two points dual-number jets prime-to-p lift`
```
   18  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    9  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    8  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    7  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
```

### DEC-20261018-3fd5b1

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-3365b4`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `On the path of 8 points whose successor is the next index, stopping at the last point, the depth-4 covers of the stored points 3 and 5 have sizes 4 and 5. Their intersection has size 3 and their unio…`
```
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    7  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```
**C** `cover counts and band products clipping conventions distinguished points multitarget finite cover`
```
   17  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    8  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    7  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    7  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
```

### DEC-20261018-43f3b8

**A** `authorize adjacent staged metadata implementation only Stage 0 freeze of N-window / weight rule / null seed; Stage 1 x-rank overlap excess on two ordinary toys with`
```
    8  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by 
    7  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    6  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    6  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself
    6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
```
**B** `SETTING (IDEA-20261007-1a61b9). For an ordinary short-Weierstrass curve over F_p with a prime-order subgroup of size N in (2^10, 2^12), skipping y^2=x^3+x+1, let t=floor(log2(N)/4) and let W be the n…`
```
    8  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    8  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    8  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weaknes
    7  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
    6  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```
**C** `invertible hint subset orbit factors anomalous trace query-bounded success bound x-rank overlap`
```
   14  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

### DEC-20261018-50225a

**A** `open batch Metadata-compatible deterministic reproduction of EXP-ECDLP-bfbe6f; Metadata-compatible deterministic reproduction of EXP-ECDLP-5f4f14; Metadata-compatible deterministic reproduction of EXP-ECDLP-3c166b; Metadata-compatible deterministic reproduction of EXP-ECDLP-20ac31`
```
    6  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    6  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
    4  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
    4  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    2  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41 ; chord slope fibres under translation, x-count gap of two curves, square bias of four-term x-product, coordinate statistic of points`
```
   24  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   18  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   16  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

### DEC-20261018-59a33a

**A** `authorize role separated finite worksheet implementation Rational points and the coordinate cycle on the Hesse cubic over F_97; Orbit factors and the anomalous trace; Negation invariance of two x-line maps over F_17; Three cells of the query-bounded success bound`
```
   10  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    9  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
    8  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```
**B** `Let C be x^3 + y^3 + z^3 = 3*27*xyz over F_97. It has 117 projective rational points. O = (1 : 96 : 0) lies on C. The map sigma(x : y : z) = (y : z : x) sends C to itself, satisfies sigma^3 = id, and…`
```
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    8  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
```
**C** `rational points and the coordinate cycle on the Hesse cubic over F_97 curve model representation ; invertible hint subset orbit factors anomalous trace query-bounded success bound x-rank overlap ; negation invariance of two x-line maps over F_17 lossy object propagation`
```
   19  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
   14  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   12  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
   12  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
```

### DEC-20261018-5ef9a3

**A** `authorize zero run partial output preservation Metadata-compatible deterministic reproduction of EXP-ECDLP-bfbe6f`
```
    6  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    5  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    5  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
    4  KR-RHO-38be82                                known_result       Tag tracing and table-driven step shortcuts
    4  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41`
```
   20  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   11  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic,
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

### DEC-20261018-5faa6d

**A** `authorize terminal snapshot preservation`
```
no lead or known result shares vocabulary with this idea; a low score is not novelty: read ATLAS.md by family
```
**B** `authorize terminal snapshot preservation`
```
no lead or known result shares vocabulary with this idea; a low score is not novelty: read ATLAS.md by family
```

### DEC-20261018-60f8de

**A** `prepare fresh metadata successor after preserved git status failure Direct native invocation reproduction of EXP-ECDLP-615fcf`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
```
**B** `On the curve y^2 = x^3 + 8x^2 + 2x over the field with 11 elements there are 12 rational points, counting the identity. For each of the three points S among (0,0), (1,0) and (2,0), exactly four trans…`
```
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   11  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
```
**C** `degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet`
```
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
```

### DEC-20261018-66f069

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-d68ac9`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `On y^2 = x^3 + x + 3 over the field of 151 elements, the point (1, 55) lies on the curve and 167 times that point is the identity. The integer 167 is prime. Thirteen squared is 169, which is above 15…`
```
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
    9  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    9  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    9  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic
    8  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```
**C** `window pair-sum counts constant engineering prime-field index calculus`
```
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   11  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
   11  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   10  LEAD-ICP-extension-field-embedding           closed_obstructed  Embedding E(F_p) into E(F_{p^n}) to buy a subfield factor base
```

### DEC-20261018-6b8340

**A** `record completed metadata reproductions and operational archives Metadata-compatible S3 worksheet reproduction with bounded Git metadata threading; Metadata-compatible deterministic reproduction of EXP-ECDLP-5f4f14; Metadata-compatible deterministic reproduction of EXP-ECDLP-3c166b; Metadata-compatible deterministic reproduction of EXP-ECDLP-20ac31`
```
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    4  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    4  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircas
    4  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41 ; chord slope fibres under translation, x-count gap of two curves, square bias of four-term x-product, coordinate statistic of points`
```
   24  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   18  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   16  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

### DEC-20261018-7ad1ee

**A** `record actual raw archive and operational task completion The exponent band contains 1/5, and 64 squared is below 64 cubed`
```
    8  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    6  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    4  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
```
**B** `Cross-multiplication gives 1/6 < 1/5 because 5 < 6, and 1/5 < 1/4 because 4 < 5. The witness 1/5 lies in the half-open interval from 1/6 to 1/4. For n = 64, n^2 = 4096 and n^3 = 262144, so n^2 < n^3.…`
```
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
    4  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbi
    4  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself
    4  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    4  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
```
**C** `Wagner k-tree four-list join exponent band cross-energy remainder branching of 2-bit reduction addition modulo 17`
```
   18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
    7  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    5  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)
```

### DEC-20261018-7c6c84

**A** `record actual raw archive and operational task completion Orbit factors and the anomalous trace`
```
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbi
```
**B** `The curve y squared equals x cubed plus 5 over the field of 7 elements has 7 points, so its trace is 1. The six nonzero points fall into 2 orbits of size 3 under multiplication of the x-coordinate by…`
```
   13  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
    9  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    9  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    8  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircas
```
**C** `invertible hint subset orbit factors anomalous trace query-bounded success bound x-rank overlap`
```
   14  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

### DEC-20261018-7cf349

**A** `record actual raw archive and operational task completion Negation invariance of two x-line maps over F_17`
```
    6  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    5  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
```
**B** `The curve has 17 affine points. For every such point (x, y), the point (x, -y) is also on the curve and has the same x-coordinate. The same holds after sending x to x+1. Exactly 16 affine points have…`
```
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   10  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    8  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```
**C** `negation invariance of two x-line maps over F_17 lossy object propagation`
```
   16  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
    6  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    5  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    5  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
```

### DEC-20261018-7ee3c1

**A** `amend dispatch queue Twelve S_3 residues on y^2 = x^3 + x + 2 over F_41; Chord-slope fibres under translation by one generator on one F_53 curve; Lower-half x-count gap of two curves over F_29; Square bias of one four-term x-product on y^2 = x^3 + 6x + 2`
```
   10  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    8  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    8  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    6  KR-IC-e2d81b                                 known_result       ecGFp5 and degree-5 extension curves: published estimates
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41 ; chord slope fibres under translation, x-count gap of two curves, square bias of four-term x-product, coordinate statistic of points`
```
   24  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   18  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   16  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

### DEC-20261018-808baa

**A** `record actual raw archive and operational task completion Which theta coefficient leaves a positive cross-energy remainder`
```
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    4  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
    3  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
```
**B** `Let L = M/(2b) be the coefficient of |A|^4 in the nonzero cross-energy lower bound, for b > 0 and M > 0. For theta^2 = 1/(16b) the off-spectrum coefficient is M/(16b), and its ratio to L is 1/8. Subt…`
```
    7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    4  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    3  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
```
**C** `Wagner k-tree four-list join exponent band cross-energy remainder branching of 2-bit reduction addition modulo 17`
```
   18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
    7  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    5  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)
```

### DEC-20261018-8e211e

**A** `archive descriptive actual native execution closeout Twelve S_3 residues on y^2 = x^3 + x + 2 over F_41; Chord-slope fibres under translation by one generator on one F_53 curve; Lower-half x-count gap of two curves over F_29; Square bias of one four-term x-product on y^2 = x^3 + 6x + 2`
```
   10  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    8  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    8  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    8  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41 ; chord slope fibres under translation, x-count gap of two curves, square bias of four-term x-product, coordinate statistic of points ; stage-0 instrument planted degree-0 section canonical height of lift over F_31`
```
   24  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   19  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   18  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   16  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

### DEC-20261018-975dd7

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-615fcf`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `On the curve y^2 = x^3 + 8x^2 + 2x over the field with 11 elements there are 12 rational points, counting the identity. For each of the three points S among (0,0), (1,0) and (2,0), exactly four trans…`
```
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   11  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
```
**C** `degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet`
```
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
```

### DEC-20261018-a7a0fd

**A** `approve The legacy (x3-dropping) s4_expr changed the recorded outputs of the archived S4-consuming runs; a matched rer; Matched legacy/repaired s4_expr rerun of every archived S4-consuming run (EXP-MTIC-001, EXP-FIB-001, RUN-ICINV; PER-RUN IMMUNITY AUDIT of the 21 archived runs of EXP-MTIC-001 and EXP-FIB-001 against the confirmed harness/s`
```
    8  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    7  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition
    5  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
```
**B** `THE DEFECT (established, not hypothesized). Before 2026-08-13, harness/semaev.py built the right-hand S3 of the S4 resultant with a sequential .subs({x1: x3, x2: x4, x3: t}), so x3 was renamed twice…`
```
    4  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, 
    4  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    3  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    3  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    3  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
```

### DEC-20261018-ae74db

**A** `record two additional native metadata reproductions and six scope implementation resolution Native metadata reproduction of the unchanged three-output EXP-ECDLP-f34097 instrument; Native metadata reproduction of the unchanged three-output EXP-ECDLP-903c48 instrument`
```
    6  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    4  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    4  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    4  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks)
```
**B** `On the preregistered constant Weierstrass surface y^2 = x^3 + x + 30 over F_31, with planted degree-0 section (x, y) = (2, 3), the known-generator oracle recovers coefficient vector (2, 0, 3, 0) at m…`
```
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
```
**C** `stage-0 instrument planted degree-0 section canonical height of lift over F_31 ; elliptic net rank-1 zeros stage-0 instrument y^2 = x^3 + 2 over F_11 net information`
```
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   13  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   12  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
```

### DEC-20261018-b3861f

**A** `prepare explicit c9 descriptive successor and correct unapproved metadata binding Two explicit clipping conventions for the frozen finite cover worksheet; Cover counts and band products`
```
    7  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgrou
    6  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    6  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into th
    5  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    5  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
```
**B** `On the path of 8 points whose successor is the next index, stopping at the last point, the depth-4 covers of the stored points 3 and 5 have sizes 4 and 5. Their intersection has size 3 and their unio…`
```
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    7  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```
**C** `cover counts and band products clipping conventions distinguished points multitarget finite cover`
```
   17  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    8  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    7  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    7  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
```

### DEC-20261018-c4352a

**A** `approve Direct native invocation reproduction of EXP-ECDLP-95f69f; Direct native invocation reproduction of EXP-ECDLP-c9110e; Direct native invocation reproduction of EXP-ECDLP-d68ac9; Direct native invocation reproduction of EXP-ECDLP-efafc0`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    2  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
```
**B** `Let low(x) = x mod 4. For every pair of residues (u, v) in 0..3, the set of low((a+b) mod 17) over a, b in 0..16 with low(a)=u and low(b)=v has size 2. There are 136 pairs (a, b) where this value dif…`
```
    8  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, 
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
    6  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    5  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```
**C** `Wagner k-tree four-list join exponent band cross-energy remainder branching of 2-bit reduction addition modulo 17 ; degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet ; window pair-sum counts constant engineering prime-field index calculus`
```
   20  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
   17  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   16  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

### DEC-20261018-c63577

**A** `record actual raw archive and operational task completion Three cells of the query-bounded success bound`
```
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    4  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `For n = 101, the rational (P*T + T*T + 1)/n is 1/101 when P = T = 0, is 101/101 when P = 0 and T = 10, and is 16/101 when P = 2 and T = 3. A claimed success probability of 1 at P = T = 0 is strictly…`
```
    8  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    6  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    5  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
```
**C** `invertible hint subset orbit factors anomalous trace query-bounded success bound x-rank overlap`
```
   14  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

### DEC-20261018-ca4056

**A** `approve Native metadata reproduction of the unchanged three-output EXP-ECDLP-f34097 instrument; Native metadata reproduction of the unchanged three-output EXP-ECDLP-903c48 instrument`
```
    5  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, 
    3  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables
    3  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
```
**B** `On the preregistered constant Weierstrass surface y^2 = x^3 + x + 30 over F_31, with planted degree-0 section (x, y) = (2, 3), the known-generator oracle recovers coefficient vector (2, 0, 3, 0) at m…`
```
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
```
**C** `stage-0 instrument planted degree-0 section canonical height of lift over F_31 ; elliptic net rank-1 zeros stage-0 instrument y^2 = x^3 + 2 over F_11 net information`
```
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   13  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   12  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
```

### DEC-20261018-d763f3

**A** `approve Two explicit clipping conventions for the frozen finite cover worksheet`
```
    7  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgrou
    6  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    6  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into th
    5  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    5  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
```
**B** `On the path of 8 points whose successor is the next index, stopping at the last point, the depth-4 covers of the stored points 3 and 5 have sizes 4 and 5. Their intersection has size 3 and their unio…`
```
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    7  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```
**C** `cover counts and band products clipping conventions distinguished points multitarget finite cover`
```
   17  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    8  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    7  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    7  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
```

### DEC-20261018-d8801f

**A** `record actual raw archive and operational task completion Native staged metadata reproduction of the unchanged adjacent x-rank instrument`
```
    6  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `SETTING (IDEA-20261007-1a61b9). For an ordinary short-Weierstrass curve over F_p with a prime-order subgroup of size N in (2^10, 2^12), skipping y^2=x^3+x+1, let t=floor(log2(N)/4) and let W be the n…`
```
    8  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    8  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    8  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weaknes
    7  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
    6  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```
**C** `invertible hint subset orbit factors anomalous trace query-bounded success bound x-rank overlap`
```
   14  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

### DEC-20261018-ea671a

**A** `amend administrative artifact path coverage Stage-0 instrument: planted degree-0 section on y^2 = x^3 + x + 30 over F_31; Stage-0 instrument: rank-1 net zeros for (1, 5) on y^2 = x^3 + 2 over F_11`
```
    8  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables
    5  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    4  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    4  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
```
**B** `On the preregistered constant Weierstrass surface y^2 = x^3 + x + 30 over F_31, with planted degree-0 section (x, y) = (2, 3), the known-generator oracle recovers coefficient vector (2, 0, 3, 0) at m…`
```
   12  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
```
**C** `stage-0 instrument planted degree-0 section canonical height of lift over F_31 ; elliptic net rank-1 zeros stage-0 instrument y^2 = x^3 + 2 over F_11 net information`
```
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   13  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   12  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
```

### DEC-20261018-f3fac7

**A** `record actual raw archive and operational task completion Direct native invocation reproduction of EXP-ECDLP-efafc0`
```
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chaine
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    3  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    3  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```
**B** `The three points (0, 1), (4, 1), and (13, 16) lie on y^2 = x^3 + x + 1 over F_17 and are collinear. The chord-and-tangent sum of (0, 1) and (4, 1) is (13, 1), the negation of (13, 16). The triple (0,…`
```
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    7  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    5  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
```
**C** `degree-2 translation count chord-and-tangent check of one triple over F_17 point decomposition worksheet`
```
   13  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
```

### DEC-20261018-f4c865

**A** `prepare additive metadata replacement and preserve failure Metadata-compatible S3 worksheet reproduction with bounded Git metadata threading; Metadata-compatible deterministic reproduction of EXP-ECDLP-bfbe6f`
```
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    4  KR-RHO-cd86f5                                known_result       r-adding walks and the walk constant
    4  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircas
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41`
```
   20  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   11  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic,
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

### DEC-20261018-f952c0

**A** `publish verified report archive receipt and close only this campaigns finished coordination lanes`
```
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    4  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by 
    4  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
    3  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
```
**B** `Administrative lane lifecycle and exact postcommit receipt only. Goal stays active; other sessions and scientific statuses unchanged.`
```
    5  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130
    4  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    4  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by 
```

### DEC-20261018-f9e8d5

**A** `approve Metadata-compatible S3 worksheet reproduction with bounded Git metadata threading`
```
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    4  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircas
    4  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    3  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
```
**B** `On y^2 = x^3 + x + 2 over F_41, S_3 from KN-TECH-002 vanishes at each of the six chord sums of (0, 17), (1, 2), (3, 14), and (5, 3), and the six values at third coordinate 7 are 13, 33, 35, 11, 28, a…`
```
    7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    5  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
```
**C** `S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41`
```
   20  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   11  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic,
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

### DEC-20261018-fd0a18

**A** `record actual raw archive and operational task completion Rational points and the coordinate cycle on the Hesse cubic over F_97`
```
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    5  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    5  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    5  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
```
**B** `Let C be x^3 + y^3 + z^3 = 3*27*xyz over F_97. It has 117 projective rational points. O = (1 : 96 : 0) lies on C. The map sigma(x : y : z) = (y : z : x) sends C to itself, satisfies sigma^3 = id, and…`
```
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    8  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
```
**C** `rational points and the coordinate cycle on the Hesse cubic over F_97 curve model representation`
```
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    8  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
```

### DEC-20261019-5b9240

**A** `approve The legacy (x3-dropping) s4_expr changed the recorded outputs of the archived S4-consuming runs; a matched rer; Matched legacy/repaired s4_expr rerun of every archived S4-consuming run (EXP-MTIC-001, EXP-FIB-001, RUN-ICINV; One-trial successor of EXP-SEMAEV-93d5cc for its interrupted mtic-010b cell (matched legacy/repaired s4_expr r`
```
    7  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    4  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    2  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    2  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
```
**B** `THE DEFECT (established, not hypothesized). Before 2026-08-13, harness/semaev.py built the right-hand S3 of the S4 resultant with a sequential .subs({x1: x3, x2: x4, x3: t}), so x3 was renamed twice…`
```
    4  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, 
    4  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    3  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    3  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    3  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
```

### DEC-20261019-ebf1dc

**A** `approve The legacy (x3-dropping) s4_expr changed the recorded outputs of the archived S4-consuming runs; a matched rer; Matched legacy/repaired s4_expr rerun of every archived S4-consuming run (EXP-MTIC-001, EXP-FIB-001, RUN-ICINV; Second one-trial successor for the mtic-010b cell of EXP-SEMAEV-93d5cc (after EXP-SEMAEV-88c46c was interrupte; One-trial successor of EXP-SEMAEV-93d5cc for its interrupted mtic-010b cell `
```
    7  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    5  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation
    4  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    3  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbi
```
**B** `THE DEFECT (established, not hypothesized). Before 2026-08-13, harness/semaev.py built the right-hand S3 of the S4 resultant with a sequential .subs({x1: x3, x2: x4, x3: t}), so x3 was renamed twice…`
```
    4  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, 
    4  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    3  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    3  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    3  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
```

### DEC-20261022-9aec2b

**A** `record observations and dispatch review Dual sum-product probe at toy scale: the x-label sets of rank-r log-GAP bases {c_1 P_1 + ... + c_r P_r} on gen; Heuristic validation of H1 of IDEA-20261017-078074, the dual sum-product probe, at toy scale: exact nontrivial`
```
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
    8  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
    7  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by 
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    6  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
```
**B** `Let E/F_p be a generated prime-order ordinary curve, N = #E(F_p), f(x) = x^3 + ax + b, and L = {x in F_p : f(x) a nonzero square} the label universe (the R1 x-labels of the points of E other than O,…`
```
    7  LEAD-EXO-torsor-deck-period                  closed_obstructed  Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent
    6  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    6  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
```

### DEC-20261022-e5f45c

**A** `revise Cyclotomic lift with complete splitting: trace-relation yield ratio R(H), covering exponent gamma and rank gai; Mersenne embedding degree: exact identity k(l) = ord_l(2)/gcd(ord_l(2), c) on a toy census against matched ran; Solinas number fields: rank gain, minimal new-point height and covering exponent of E over K_f = Q[t]/(f) for ; Rotation-class factor base over Mersenne primes: closure ratio and decomposit`
```
   25  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
   17  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit an
   15  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   15  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```
**B** `Let p = 2^c - 1 be a Mersenne prime with c prime, so ord_p(2) = c, p = 1 mod c, and p splits completely in Q(zeta_c) and in every subfield K of degree d | c - 1. Let E/Q have rank 0, good reduction a…`
```
   12  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   11  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130
   11  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircas
   10  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    9  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
```
**C** `stage-0 instrument planted degree-0 section canonical height of lift over F_31 ; S_3 residues algebraic membership factor base twelve residues on elliptic curve over F_41`
```
   20  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree m
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
   12  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```

### DEC-20261023-039ddf

**A** `reject scoped On F_p^* the Teichmuller section is the unique homomorphic section, log_p vanishes on it, and non-canonical se; Multiplicative-group calibration: Teichmuller, naive and Hensel sections of Z_p^* -> F_p^* under log_p(s(x)^{p`
```
   14  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   10  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    6  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    5  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
```
**B** `For 40 primes 50 < p < 2000 with generator g and precision 4: the Teichmuller section is a homomorphism on every sampled pair and the functional log_p(s(x)^{p-1}) vanishes on it identically, so its S…`
```
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, 
    6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, L
    5  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
```

### DEC-20261023-147f9f

**A** `support On an anomalous CM curve, Smart's formal-logarithm attack is killed exactly by the Serre-Tate canonical lift o; On every class-number-one CM anomalous curve with p <= 1500, read v_p(z([p]P^)) and Smart's ratio over four cu`
```
   23  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   22  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   17  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   11  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
   10  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
```
**B** `Let E/F_p be ordinary with #E(F_p) = p and End(E) the maximal order of a class-number-one field, so its Serre-Tate canonical lift E_can/Z_p is the explicit integral CM model. For a lift E^/Z_p of E a…`
```
   23  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   15  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   12  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic
   10  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    9  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
```

### DEC-20261023-19c53b

**A** `approve Decide KN-FIND-c41ea9's own untaken clause - is the 2^(n-1) split-compounding over F_{q^n} an exponent lever, ; Is the "2^(n-1) compounding" clause over F_{q^n} a yield lever or a bookkeeping factor? Derivation-first re-sc; SCOPE: prime fields F_p with p in [100, 3000]; E(F_p) as a finite abelian group; factor bases FB that are symm; The relation-rate half of KN-OPEN-009 is not a monodromy question at all: an`
```
   15  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   14  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic,
   14  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   14  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   13  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```
**B** `KN-FIND-c41ea9 CLOSES WITH A CLAUSE IT FLAGS AND DOES NOT DECIDE, AND THE CLAUSE IS THE ONLY EXPONENT-MOVING STATEMENT ANYWHERE IN THE ECDLP CORPUS: "A per-fibre factor of 2 applied once per summatio…`
```
    8  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    8  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    8  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    7  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    7  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
```

### DEC-20261023-26a6de

**A** `weaken Small rational points on E/Q (and on E(K) for a quadratic K) grow like (log H)^{r/2}, reduce to E(F_p) like un; Census of rational points of naive height <= 10^5 (3 x 10^5 on the replication) on the rank-0..7 minimal-condu`
```
   15  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   15  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    8  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    7  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
```
**B** `For E/Q of rank r the number N_E(H) of rational points of naive height H(x) <= H grows like c_E (log H)^{r/2} (the slope of log N_E against log log H lies within 1 of r/2 on the ladder of ranks 0..7…`
```
   20  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
   11  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    8  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    7  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
```

### DEC-20261023-2e7447

**A** `refine Character spectrum of digits 0..4 of x and y of the torsion section s_tor([k]P), half-range k <= (n-1)/2, on C; No p-adic digit of the torsion section's coordinates, on the canonical curve lift or on an arbitrary lift, cor`
```
   28  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   20  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   12  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   12  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```
**B** `Let E/F_p have a prime-order subgroup <P>, n != p, and let s_tor be the torsion section on a lift E^/Z_p (the CM canonical model or an arbitrary integer lift). For every digit function f(k) = a_i(x(s…`
```
   16  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   16  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    9  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
```

### DEC-20261023-36b4f0

**A** `support The canonical point section of E(Q_p) -> E(F_p) on a non-anomalous curve exists, is the prime-to-p torsion sec; Compute the prime-to-p torsion section explicitly on CM-canonical and arbitrary lifts, verify it is canonical,`
```
   25  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   18  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   14  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    7  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```
**B** `Let E/F_p be ordinary with a subgroup <P> of prime order n != p, and E^/Z_p ANY lift of E (the Serre-Tate canonical CM model or an arbitrary integer lift). Reduction E^(Q_p)[n] -> E(F_p)[n] is a grou…`
```
   23  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   15  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   11  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit an
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   10  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgrou
```

### DEC-20261023-488023

**A** `weaken Xedni lifts of two or three random points are never dependent within a relation bound of 6, while a planted de; Lift r in {2, 3} random points of random curves at 8 primes to symmetric integer representatives, fit the curv`
```
   27  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   20  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
   17  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   16  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   13  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```
**B** `For p in {101, 211, 401, 809, 1601, 3203, 6421, 12809}, random y^2 = x^3 + a x + b over F_p, and r in {2, 3} random points lifted to symmetric integer representatives with the Weierstrass model fitte…`
```
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
    7  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presenta
    7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    6  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
```

### DEC-20261023-66af3b

**A** `pause Serre-Tate level-1 splitting by explicit construction: log_F / exp_F series, p-torsion lift built and verified; The level-1 Serre-Tate splitting of an anomalous lift is exactly the j-distance rule, witnessed by an explicit`
```
   12  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   12  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   11  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    7  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```
**B** `On the 29 anomalous CM curves (p <= 1500) and the four lift classes of EXP-CZLIFT-17b7eb, with lambda = log_F(z([p]P^)) computed from the formal-group series at precision 6: v_p(lambda) >= 2 if and o…`
```
   11  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   11  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    7  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
```

### DEC-20261023-6931ab

**A** `weaken On retrieved rank-record curves (rank >= 8 and >= 9) small rational points stay rare and reduce uniformly, so ; Rank ladder extended with retrieved rank-record curves (Grunewald-Zimmert rank >= 8, Brumer-Kramer rank >= 9)`
```
   14  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   14  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy co
    9  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    7  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```
**B** `With the Grunewald-Zimmert (rank >= 8) and Brumer-Kramer (rank >= 9) curves retrieved from Dujella's rank-history pages and the lane-1 rank-7 curve as overlap: N_E(10^5) on the two record curves is b…`
```
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    7  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    7  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    6  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
```

### DEC-20261023-9de83a

**A** `refine The canonical-lift rule and the torsion-section identities hold unchanged for p between 10^4 and 10^5; Medium-scale replication of the canonical-lift rule and the torsion-section identities, 10^4 <= p <= 10^5; Replicate the canonical-lift and torsion-section measurements at p near 10^4 to 10^5`
```
    4  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
    3  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, 
    3  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    2  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    1  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
```
**B** `On 24 class-number-one CM anomalous curves and 16 CM-canonical plus 8 random-lift non-anomalous curves sampled with 10^4 <= p <= 10^5: rule_agreement = 1 and nondegenerate_success_rate = 1 for Smart'…`
```
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   10  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
```

### DEC-20261023-fdc4af

**A** `pause Small points of E(K), K = Q(2^{1/3}), on the rank-0..5 ladder: cubic gain over E(Q) and coverage of E(F_p) at ; Over K = Q(2^{1/3}) the small points of E(K) exceed those of E(Q) by a bounded factor and reduce to E(F_p) lik`
```
   13  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy co
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    9  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic,
    9  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    8  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
```
**B** `For the six ladder curves of rank 0..5 and K-points x = alpha/d^2 with alpha in Z[theta], coordinates up to 32 and d <= 4: N_K(H) is at least N_Q(H) and at most 4 N_Q(H) at the top height on every cu…`
```
    9  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
    6  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-s
    6  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    5  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
```

### DEC-20261024-23d64d

**A** `synthesize The canonical point section of E(Q_p) -> E(F_p) on a non-anomalous curve exists, is the prime-to-p torsion sec; Small rational points on E/Q (and on E(K) for a quadratic K) grow like (log H)^{r/2}, reduce to E(F_p) like un; Lift r in {2, 3} random points of random curves at 8 primes to symmetric integer representatives, fit the curv; Rank ladder extended with retrieved rank-record curves (Grunewald-Zimmert`
```
   28  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   25  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   20  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   20  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-
   18  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
```
**B** `Let E/F_p be ordinary with a subgroup <P> of prime order n != p, and E^/Z_p ANY lift of E (the Serre-Tate canonical CM model or an arbitrary integer lift). Reduction E^(Q_p)[n] -> E(F_p)[n] is a grou…`
```
   23  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   15  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   11  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit an
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of in
   10  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgrou
```

### DEC-20261024-992998

**A** `approve GHS cover genus floor at n = 7: does the factorisation of x^7 - 1 over F_2 (ord_7(2) = 3), with the 2-torsion ; GHS cover genus floor at n = 7 in odd characteristic: the span dimensions are the degrees of divisors of x^7 -; GHS cover genus floor at n = 7 (odd characteristic, with a characteristic-2 control): regression of the n = 3`
```
   14  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   10  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into th
```
**B** `For E/F_{q^7}, q odd, and the (2,...,2) compositum of the 7 conjugate double covers of the x-line (g = 2^(m-2)(r-4)+1), m is in {1, 3, 4, 6, 7}; split 2-torsion can reach g = 7 (the Lemma D0 bound) v…`
```
    7  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    7  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic
    6  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
    6  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    5  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```

### DEC-20261024-e29f4c

**A** `approve GHS cover genus floor at n = 7: does the factorisation of x^7 - 1 over F_2 (ord_7(2) = 3), with the 2-torsion`
```
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   10  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into th
    8  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
```
**B** `For E/F_{q^7}, q odd, and the (2,...,2) compositum of the 7 conjugate double covers of the x-line (g = 2^(m-2)(r-4)+1), m is in {1, 3, 4, 6, 7}; split 2-torsion can reach g = 7 (the Lemma D0 bound) v…`
```
    7  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    7  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic
    6  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients 
    6  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    5  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```
## Appendix B. Reference verification (audit/verify_refs.py)

```
id tokens checked: 157 missing: []
evidence paths checked: 21 missing: []
   experiments/EXP-PEXT-212d5c/specification.yaml
   knowledge/open-problems/KN-OPEN-d3a6f0.md
   ledger/corrections/CORR-20261024-63d682.yaml
   ledger/decisions/DEC-20261018-273b2d.yaml
   ledger/decisions/DEC-20261022-9aec2b.yaml
   ledger/decisions/DEC-20261022-e5f45c.yaml
   ledger/decisions/DEC-20261023-039ddf.yaml
   ledger/decisions/DEC-20261023-147f9f.yaml
   ledger/decisions/DEC-20261023-19c53b.yaml
   ledger/decisions/DEC-20261023-26a6de.yaml
   ledger/decisions/DEC-20261023-2e7447.yaml
   ledger/decisions/DEC-20261023-36b4f0.yaml
   ledger/decisions/DEC-20261023-488023.yaml
   ledger/decisions/DEC-20261023-66af3b.yaml
   ledger/decisions/DEC-20261023-6931ab.yaml
   ledger/decisions/DEC-20261023-9de83a.yaml
   ledger/decisions/DEC-20261023-fdc4af.yaml
   ledger/decisions/DEC-20261024-23d64d.yaml
   ledger/hypotheses/H-SEMAEV-94dab2.yaml
   reports/ideas_execution_20261018/native-campaign-closeout/actual-native-inventory.json
   research/ghs_cover_census_n5_20261013/README.md
```

---

## Group: car-evidence-hypotheses

# Fold: car-evidence-hypotheses (changed-since-review, step 2)

Reviewer output for the lead-atlas skill. Read-only: no repository file was edited; every edit below is a PROPOSED DIFF to an atlas row (or to `coverage.tsv`). No hypothesis, experiment or goal status change is proposed.

- Repository root: `/Volumes/SSD990-2/crypto-autoresearcher`. Atlas rows: `knowledge/leads/ecdlp/<family>/LEAD-*.yaml`. Paths came from `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/delta.txt` lines 71-91 (21 paths: 8 evidence, 10 H-CZLIFT, H-ICPERF-3982eb, H-PEXT-d536a1, H-SEMAEV-94dab2).
- Method: each record read by summary fields (direction/direction_note/strength/inference/obstruction/resource_check for EV; title/statement/mechanism/status/status_history for H; the DEC records they cite for next_actions and status_transitions). No raw run logs opened. `python3 tools/lead_atlas.py --match` run with two phrasings per record group (raw top-5 hits in section 4) plus 12 extra phrasings for the "new mechanism" check (section 5). Raw JSON: `scratchpad/audit/matches.json`, `scratchpad/audit/matches_extra.json`.
- Status provenance: the CZLIFT evidence round (EV-CZLIFT-712fe4, -ad28f5, -376eee, -764f54, -ee9b23, -f2a401, -e9a7cf, -b6fe48; DEC-20261023-147f9f, -36b4f0, -26a6de, -2e7447, -488023, -039ddf, -9de83a, -6931ab, -66af3b, -fdc4af) is in git commit 87bdd8316f ("archive(TASK-20261023-4d7449) ..."), which `git branch -r --contains` lists under origin/main (via origin/HEAD). The status notes say a transition is official only after the post-commit verifier accepts that commit; I did not run the verifier, so every note below that cites a status should be read "as recorded in the hypothesis file".
- Convention: "Observed" = what the record states with its scope; "Reading" = my interpretation, conditional. A record's own tier and scope are carried into every proposed note (all CZLIFT evidence is `claim_tier: toy`, prime fields below 2^17).

## 1. Result in one paragraph

All 21 paths advance or pin an existing lead; none is a new mechanism and none is `not_ecdlp`. No proposed edit changes a lead's disposition. The 18 CZLIFT paths (8 evidence, 10 hypotheses) are the filed evidence and status moves that three TRF rows still describe as "review pending" / "evidence records not filed" (`LEAD-TRF-global-lift-small-height`, `LEAD-TRF-anomalous-padic-lift`, `LEAD-TRF-padic-canonical-section`); the xedni sibling `LEAD-ICP-char0-lifting-xedni-smoothness` gets one cross-reference. Three existing atlas statements are contradicted by the filed evidence and need correction: (i) `LEAD-TRF-global-lift-small-height.best_measured` says small points "reduce like uniform points" and xedni dependence "never seen within relation bound 6" - EV-CZLIFT-376eee measures a non-uniform excess (coverage median 1.033 vs uniform null 1.002) and EV-CZLIFT-ee9b23 records one dependence in 3200 trials; (ii) the same row's obstruction text says the program re-measured reduction "over Q(2^{1/3})" - the run set for that claim was ruled inadmissible (DEC-20261023-fdc4af, H-CZLIFT-89e169 has no evidence); (iii) `LEAD-TRF-padic-canonical-section.obstruction` states the 1/p rate of non-homomorphic sections under `kind: theorem` - EV-CZLIFT-ad28f5 proves only the homomorphic-section statement (Hom(Z/n, E^(pZ_p)) = 0, n != p) and labels the 1/p statement a numbered heuristic measured on three named sections at toy scale. Coverage gaps found: H-ICPERF-3982eb and H-PEXT-d536a1 are unmapped; H-SEMAEV-94dab2 has no row at all (area SEMAEV is not in `ecc_areas`, so `--coverage` cannot see it).

## 2. Per-path table

Edit ids (D-...) refer to the consolidated diffs in section 3. "cov" = current `coverage.tsv` row. EV records have no coverage row (the file tracks H-* and IDEA-* only).

| # | path | record, status, direction | ECDLP | action | lead | edit | reasoning |
|:--|:--|:--|:--|:--|:--|:--|:--|
| 1 | ledger/evidence/EV-CZLIFT-376eee.yaml | EV for H-CZLIFT-9a32e9; weakens; strength replicated; toy; DEC-20261023-26a6de | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-1,3,4,5,6 | Observed: eight-curve ladder (ranks 0..7), H <= 3e5, p = 103..20011; N_E(H) / Neron-Lang count in [0.963, 1.309]; coverage median 1.0330 and 1.0333 on two runs against uniform null 1.0017; 97 and 123 frozen cells with paired-uniform tail < 1e-6; ker(red_p) has no vector of canonical height below 2 log p - c_E (none below 2 log p + 0.91 observed). Record derives (D6, D7) that the extra spread costs at most a factor 2 ln 2 in points needed, so half coverage of E(F_p) needs >= N_p/2 distinct global points at fixed rank (Omega(p) vs O(sqrt p)); exponential-height clause (C4) not measured, conditional on T1-T4; twists/E(K) (C5) untested. Reading: the lead's "reduce like uniform points" is superseded; the closed_known disposition is supported by an additional measured/derived counting bound, not weakened. |
| 2 | ledger/evidence/EV-CZLIFT-712fe4.yaml | EV for H-CZLIFT-889c9d; supports; replicated; toy; DEC-20261023-147f9f (via status_history) | yes | advances_lead | LEAD-TRF-anomalous-padic-lift | D-ANOM-1,2,3 | Observed: 29 class-number-one CM anomalous curves, 7 <= p <= 1373, precision p^8; degeneracy flag v_p(z([p]P^)) >= 2 agrees with j-distance rule v_p(Delta j) >= 2e on 14,616/14,616 rows (+12,778/12,778 red-team fibre lifts); Smart ratio recovers d on 2,052/2,052 rows per seed when v_p(Delta j) < 2e; on degenerate lifts next-digit successes 93 and 87 of 5,256 vs 86.84 expected under 1/(p+1). The record states the rule follows from Serre-Tate/Kummer theory (prior art Belding 2007 sec 7) and "closes no lane". Reading: replaces "review pending" in the lead; confirms the closed_known reproduction and the "random (non-canonical) lift" caveat. |
| 3 | ledger/evidence/EV-CZLIFT-764f54.yaml | EV for H-CZLIFT-fba874; supports (narrow); preliminary; toy; DEC-20261023-2e7447 | yes | advances_lead | LEAD-TRF-padic-canonical-section | D-SEC-3,4 | Observed: 42 power-bearing records (33 CM-canonical, 9 naive-lift), 53 <= p <= 571, 47 <= n <= 613; single-digit functions a_i(x or y of s_tor([k]P)), i = 0..4; no pair (t, j) reaches tau >= rho_min (0.28-0.98, median 0.50); 30 records with n <= 41 exclude nothing; digit 0 carries k up to sign so the title claim is non-discriminating. The record states no obstruction is asserted and "no record may cite it as the reason this lane is closed". Reading: a toy exclusion of one gross leak class; belongs in best_measured with its scope, and the lead's closure must not lean on it. |
| 4 | ledger/evidence/EV-CZLIFT-ad28f5.yaml | EV for H-CZLIFT-6d4ed1; supports in scope; replicated; toy; proof_status derivation; DEC-20261023-36b4f0 | yes | decides_lead | LEAD-TRF-padic-canonical-section | D-SEC-1,2,3,4,5 | Observed: derivation uniform in p >= 5, n prime != p: unique homomorphic section is s_tor, cost <= 2(bits(n)+bits(p^k))+1 additions, Smart functional vanishes on it, Smart ratio of any section = tau-ratio; v_p = k on 1116/1116 pairs; identity-readout rate for hensel_random/naive/Teichmuller consistent with 1/p, 4-sigma floor 4.2x-5.2x of 1/p; 1/p is stated as heuristic H-1, validated only on 71 curves, 2 lifts, 2 sections. Also not supported: "canonical curve lift contributes nothing" (false on canonical j = 0 lifts) and "recovering d needs tau(dP)/tau(P) = d". Decides: closed_obstructed (theorem) stands, scoped to the homomorphic-section statement (from closed_obstructed to closed_obstructed; no change). This is the filed evidence the row said was missing ("no hypothesis has evidential standing"). |
| 5 | ledger/evidence/EV-CZLIFT-b6fe48.yaml | EV for H-CZLIFT-27a184; weakens; preliminary; toy; DEC-20261023-6931ab | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-1,3,5,6 | Observed: reduced minimal models of Grunewald-Zimmert and Brumer-Kramer 1977 records have 5 / 215 points at H = 1e5 and 11 / 311 at 3e5 vs 1155 / 1559 for the rank-7 curve 382623908456a1; counts order by discriminant, not rank; N_E(1e5) spans 3..1155 over 5 translations of the rank-7 curve; Elkies-Watkins rank 8..11 rows have 665..1027 points at 1e5. Record states the global-lift lane "is not closed for rank-record curves by this run, only for the two 1977 models" and that the rank-independent counting bound of EV-CZLIFT-376eee is neither strengthened nor weakened. Reading: add as a scope-limiting measurement; do not let "record rank curves have few small points" be cited as a rank or c_E obstruction. |
| 6 | ledger/evidence/EV-CZLIFT-e9a7cf.yaml | EV for H-CZLIFT-bd2017; supports (exact clauses); replicated; toy; proof_status empirical_only; DEC-20261023-9de83a | yes | advances_lead | LEAD-TRF-padic-canonical-section (secondary LEAD-TRF-anomalous-padic-lift) | D-SEC-2,3,4,6; D-ANOM-1,2,3 | Observed: p in [10007, 97813] (< 2^17); anomalous arm 41 curves, j-distance rule 4,608 rows, Smart recovers d on 1,152/1,152 pert_p rows; torsion arm 48 odd-order curves, rates/identity on 576 pairs (same-code evidence only); non-canonical recoveries 0/3,456 (anomalous-degenerate) and 0/576 per torsion section, one-sided 95% bounds 8.66e-4 and 5.19e-3, "do not test the 1/p rate". resource_check: exact-hit instrument is silent on tau-ratios biased toward d, "the hypothesis of a hidden-number or lattice attack"; successor in DEC-20261023-9de83a: record r and d per row, residue tests. Reading: replication at larger toy p, not a new regime; the leakage measurement is the one open item for this lead and is the natural `revisit_when` hook. |
| 7 | ledger/evidence/EV-CZLIFT-ee9b23.yaml | EV for H-CZLIFT-cb95b8; weakens; preliminary; toy; proof_status certificate (adverse clause); DEC-20261023-488023, CORR-20261023-4ffd7e | yes | advances_lead | LEAD-TRF-global-lift-small-height (secondary LEAD-ICP-char0-lifting-xedni-smoothness) | D-GLS-1,3,5; D-XED-1,2 | Observed: p in {101..12809}, r in {2,3}, y != 0 sampler, zero-freedom fit, relation bound 6: 1 dependent trial in 3200 (3.1e-4, exact 95% CI [7.9e-6, 1.74e-3]); the one relation is 2 P~1 + P~2 = O at p = 101 (RUN-CZLIFT-c3f8a8, trial 61, Y^2 = X^3 - 1728 X - 27423), a relation that already holds mod p; planted control 48/48; of 1261 bounded mod-p relations the lift preserved 1. Prediction "exactly 0" is false on seed 20261009. Record notes the JKSST attribution in the hypothesis mechanism is incorrect and bound 6 is below the attacker scale p^(1/r). Reading: "xedni dependence never seen within relation bound 6" must be corrected to the observed 1/3200; the dependence is geometric (tangent), not a lift-specific event, so it is not a `revisit_when` trigger for the xedni rows. |
| 8 | ledger/evidence/EV-CZLIFT-f2a401.yaml | EV for H-CZLIFT-d37231; contradicts as posed; strength strong; toy; DEC-20261023-039ddf | yes | advances_lead | LEAD-TRF-padic-canonical-section | D-SEC-1,3,4 | Observed: F_p^* only; 80 seeded primes 50 < p < 2000; Teichmuller section homomorphic and log_p vanishes on every pair (3200/3200); random-Hensel ratio = d on 3 of 3200 (5.39 expected); naive section ratio = d on 13 and 20 of 1600 (z = 7.65, 9.14), exactly on pairs with g^d mod p^2 < p (24/24), band p <= g^d < p^2 never (0/34); naive homomorphic exactly when x*y < p. Record: the excess is the archimedean no-carry region, solvable by an O(log p) integer logarithm, "no evidence of p-adic leakage or about any elliptic curve". Reading: this is the evidence behind the existing sentence "the only failure (naive F_p^* section) is a size effect for g^d < p"; the sentence is correct and gains a citation. |
| 9 | ledger/hypotheses/H-CZLIFT-27a184.yaml | status weakened (DEC-20261023-6931ab, EV-CZLIFT-b6fe48); cov LEAD-TRF-global-lift-small-height | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-3 | Observed: S1 (record-curve counts below rank 7) holds as an observation in the reduced minimal models; "reduce uniformly", the c_E parenthetical and the generalisation to rank-record curves are not supported (finite-H count is not an isomorphism invariant; counts order by discriminant). Reading: already in the row's `ledger_refs`; add the decision and evidence ids so the row cites the status it now has. |
| 10 | ledger/hypotheses/H-CZLIFT-6d4ed1.yaml | status supported, scoped (DEC-20261023-36b4f0, EV-CZLIFT-ad28f5); cov LEAD-TRF-padic-canonical-section | yes | decides_lead | LEAD-TRF-padic-canonical-section | D-SEC-2 | The row's own evidence entry for this file reads "canonical section = prime-to-p torsion section, gives nothing to the formal log"; that is the statement now `supported` in scope (torsion-section, cost, vanishing and tau-identity clauses by derivation; identity-readout rate at toy tier). Mechanism sentences "canonical curve lift contributes nothing" and "a section recovering d would need tau(dP)/tau(P) = d" are recorded as NOT supported (EV-CZLIFT-ad28f5 B-6, B-7). Deciding record for the lead: DEC-20261023-36b4f0 / EV-CZLIFT-ad28f5; closed_obstructed -> closed_obstructed, evidence note updated. |
| 11 | ledger/hypotheses/H-CZLIFT-889c9d.yaml | status supported, toy (DEC-20261023-147f9f, EV-CZLIFT-712fe4); cov LEAD-TRF-anomalous-padic-lift | yes | advances_lead | LEAD-TRF-anomalous-padic-lift | D-ANOM-2 | Statement (j-distance rule: Smart's precision-p^2 residue degenerates exactly when v_p(j(E^) - j_can) >= 2e) is the reproduced canonical-lift degeneracy the row cites as "review pending". Scoped form supported at toy tier; the p-torsion splitting is a known theorem (Serre-Tate). Row is already in `ledger_refs`; add status and decision. |
| 12 | ledger/hypotheses/H-CZLIFT-89e169.yaml | status approved, no evidence; run set inadmissible (DEC-20261023-fdc4af, VAL-20261022-833f7f); cov LEAD-TRF-global-lift-small-height | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-3,4 | Observed: the status_history note says validation failed on instrument defects (enumeration drops genuine K-points with ramified-prime denominators, caps d through its height; coverage median is the upper middle value; bounds cannot fail on the excess side) and RUN-CZLIFT-e7147a, RUN-CZLIFT-d6996f are inadmissible; evidence review paused. Reading: the row's claim of a re-measurement "over Q(2^{1/3})" has no admissible support and must be removed; E(K) remains unmeasured by this program. A superseding contract is the stated unblock; the atlas should say so (impediment, not an obstruction). |
| 13 | ledger/hypotheses/H-CZLIFT-9a32e9.yaml | status weakened (DEC-20261023-26a6de, EV-CZLIFT-376eee); cov LEAD-TRF-global-lift-small-height | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-2 | The row's evidence entry for this file reads "small rational points grow like (log H)^{r/2} and reduce uniformly". Clause-level readings in the status note: C1 growth law supported; C2 uniform reduction contradicted as stated; C3 consistent but derived from C1; C4 (exponential height) unmeasured, conditional on T1-T4; C5 (twists/E(K)) untested. Edit the evidence note accordingly. |
| 14 | ledger/hypotheses/H-CZLIFT-bd2017.yaml | status analyzed (DEC-20261023-9de83a, EV-CZLIFT-e9a7cf); cov LEAD-TRF-padic-canonical-section | yes | advances_lead | LEAD-TRF-padic-canonical-section (secondary LEAD-TRF-anomalous-padic-lift) | D-SEC-3,4,6; D-ANOM-3 | Exact clauses replicate at p to 97813; the tier clause ("moving the claim tier from toy to medium") is not met because p < 2^17 is toy tier; the 1/p clauses are inconclusive. Hypothesis covers both arms, so it also belongs under the anomalous row's refs. |
| 15 | ledger/hypotheses/H-CZLIFT-cb95b8.yaml | status weakened (DEC-20261023-488023, EV-CZLIFT-ee9b23, CORR-20261023-4ffd7e); cov LEAD-TRF-global-lift-small-height | yes | advances_lead | LEAD-TRF-global-lift-small-height | D-GLS-3,5 | Prediction "exactly 0 on 1600 valid trials per seed" false on seed 20261009; status attaches to the statement as tested (CORR-20261023-4ffd7e). Row already cites the hypothesis; add decision/evidence/correction ids and fix best_measured. |
| 16 | ledger/hypotheses/H-CZLIFT-d37231.yaml | status rejected, scoped "as posed; smallest primitive root" (DEC-20261023-039ddf, EV-CZLIFT-f2a401); cov LEAD-TRF-padic-canonical-section | yes | advances_lead | LEAD-TRF-padic-canonical-section | D-SEC-3 | The refuted parts are the naive-section clauses (random-model prediction); the mechanism Hom(Z/(p-1), Z_p) = 0 is not contradicted (EV-CZLIFT-f2a401 direction_note). Not a lead-level reversal: the existing sentence about the F_p^* size effect is what this decision confirms. |
| 17 | ledger/hypotheses/H-CZLIFT-d3dc4b.yaml | status approved, no evidence; run set inadmissible (DEC-20261023-66af3b, VAL-20261022-a38921); cov LEAD-TRF-anomalous-padic-lift | yes | advances_lead | LEAD-TRF-anomalous-padic-lift | D-ANOM-4 | Observed: validation failed (log_F = exp_F = z mod z^7: the 2A/5 z^5 term is missing on 18 of 29 curves; control C1 fails as written on two split lifts; checker not independent); RUN-CZLIFT-ac0be5, RUN-CZLIFT-8cd006 inadmissible. Reading: explicit p-torsion-lift construction has no admissible measurement; the valuation-based flag in EV-CZLIFT-712fe4 is the measured substitute. Row cites the hypothesis; add the decision as a caveat so it is not read as measured. |
| 18 | ledger/hypotheses/H-CZLIFT-fba874.yaml | status analyzed (DEC-20261023-2e7447, EV-CZLIFT-764f54); cov LEAD-TRF-padic-canonical-section | yes | advances_lead | LEAD-TRF-padic-canonical-section | D-SEC-3,4 | Decision refine: evidence preliminary, toy, covers only the single-pair statement on the 42 power-bearing records; not supported/weakened/rejected; decision_impact.on_positive (closing the canonical-section clause at the character level) not invoked. Reading: the row must not claim character-level closure. |
| 19 | ledger/hypotheses/H-ICPERF-3982eb.yaml | status specified (approved_by null); idea IDEA-20261017-3f46a5; EXP-ICPERF-554db4 specified, approved_by null; cov UNMAPPED | yes | advances_lead | LEAD-ICP-full-width-arity-grid | D-FW-1,2,3 | Observed: sorting the eight 11-bit coordinate summands (stable ties, all seven partial sums re-chained) of the m = 8, B = 316 chained S3 circuit on certified GF(2^61) (r = 576460752557211763); test = two separately planted positive controls, 1200 s, one thread, 8 GiB sampled RSS, 6 planted calls, 0 natural calls. The record says "instrument hypothesis, not an index-calculus cost claim". Source idea IDEA-20261017-3f46a5 is already mapped to this lead; the lead's own evidence EV-ICPERF-54ac6b records the k11 planted calls as wall-censored. No new mechanism: the nearest closed row LEAD-ICB-decomposition-encoding-and-sat scopes S_m symmetrisation as an encoding constant (H-BINSTD-770ec3). |
| 20 | ledger/hypotheses/H-PEXT-d536a1.yaml | status approved (pre-run, DEC-20261024-992998); EXP-PEXT-212d5c; source IDEA-20261024-b58e07 (unmapped); cov UNMAPPED | yes | advances_lead | LEAD-TRF-small-genus-cover-general | D-GEN-1,2,3 | Observed: derived (not yet measured) n = 7 odd-characteristic GHS floors: span dimension m in {1, 3, 4, 6, 7}; genus 7 only for split 2-torsion via (m, r) = (3, 7); E(K)[2] = Z/2 gives g >= 161; #E(K) = 2 mod 4 gives >= 193; odd order with j not in F_q gives >= 193; plus characteristic-2 histogram at N = 7l. `novelty_status: unverified`: KN-LIT-bf1772 (abstract only) reports a d = 7 classification, so the census may be an independent check. The existing row covers F_{q^3} and k = 6, 10, 14; k = 7 and the n = 5/n = 4 census directories in the crypto repo are not cited by any lead. Reading: same lead, new extension degree; the closed_obstructed (proof) scope does not yet reach k = 7 and should say so until the experiment is reviewed. The top --match hit `LEAD-TRF-odd-char-descent-smith-quartic` (open_blocked) is a different object: genus-3 descent over F_{q^3} followed by Smith's isogeny to a plane quartic and Diem's attack, not a genus-floor census at n = 7; `LEAD-ICP-gfp5-odd-char-cover` (n = 5, blocked on a source freeze) is the nearest sibling and could cite the n = 7 floors as a cross-reference. |
| 21 | ledger/hypotheses/H-SEMAEV-94dab2.yaml | status approved (DEC-20261018-a7a0fd); EXP-SEMAEV-93d5cc (+88c46c, 6e9dcf); goal GOAL-ECDLP-001; no coverage row | yes | advances_lead | LEAD-EXO-methodology-instruments (cross-refs LEAD-ICE-curve-presentation-invariance, LEAD-RHO-dp-multitarget-precomputation) | D-METH-1,2,3,4 | Observed: before 2026-08-13 `harness/semaev.py` s4_expr dropped x3 (degree 16, 227 terms vs exact S4 degree 12, 439 terms for y^2 = x^3 + 2x + 3); exposed archived runs: MTIC-007/008/010/010b, FIB-004/005 (feeding FIB-006C, -007 ratio, -008 gate), RUN-ICINV-e0cd8f-m3class m4 stage. Hypothesis measures effect size with a matched legacy-vs-repaired rerun; "not asserted that any conclusion moves"; runs exist under experiments/EXP-SEMAEV-93d5cc/runs but no evidence record or decision on outcome is filed. Source note: "remediation measurement, not a new mechanism". The only lead citing an exposed run is `LEAD-ICE-curve-presentation-invariance` (EV-ICINV-8afb64); that EV has 0 mentions of m4/s4, and H-SEMAEV P2 predicts the CLASS-VARYING verdict is unchanged (a prediction). No lead cites EXP-MTIC-001, EXP-FIB-001 or KN-OPEN-5b3a08 by id; `LEAD-RHO-dp-multitarget-precomputation` lists area MTIC (the multi-target crossover K* experiment family that H-MTIC-001 belongs to) but its evidence entries and `ledger_refs` do not cite MTIC runs, and its obstruction rests on crypto-repo controls (equal-advice audit, N83 precomputed-rho control). Reading: the MTIC-007/008/010/010b outputs are exposed to the defect and their effect size is unmeasured; whether the rho-vs-IC multi-target margin in that row depends on them cannot be settled from the row's citations. |

## 3. Consolidated proposed diffs (atlas rows only)

Every block lists what to add or replace in the named YAML row. Nothing is applied. `last_reviewed` stays at the reviewer's stamp date. `ledger_refs` entries must exist under `ledger/`; knowledge ids go into `evidence` paths.

### LEAD-TRF-global-lift-small-height (closed_known, unchanged)

```yaml
# D-GLS-1  evidence: add
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-376eee.yaml,
   note: "toy: ranks 0..7, H<=3e5, p=103..20011. Count follows Neron-Lang (ratio 0.963-1.309); reductions NOT independent-uniform (coverage median 1.033 vs uniform null 1.002; kernel of reduction has no vector below canonical height 2 log p - c_E); pigeonhole caps the excess at a factor 2 ln 2, so half coverage needs >= N_p/2 distinct global points at fixed rank (Omega(p) vs O(sqrt p))"}
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-b6fe48.yaml,
   note: "1977 record models (GZ rank>=8, BK rank>=9) carry 5/215 points at H=1e5 vs 1155 for a rank-7 curve; counts order by discriminant, not rank; EW rank 8..11 rows carry 665..1027; lane not closed for rank-record curves by this run"}
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-ee9b23.yaml,
   note: "xedni random pairs r=2,3, bound 6: 1 dependent in 3200 (p=101 tangent relation, already a mod-p relation); planted control 48/48; JKSST attribution in H-CZLIFT-cb95b8 incorrect"}
# D-GLS-2  evidence[2] (ledger/hypotheses/H-CZLIFT-9a32e9.yaml) note: replace
#   "small rational points grow like (log H)^{r/2} and reduce uniformly"
# with
#   "growth law supported; uniform-reduction clause contradicted as stated (status weakened 2026-10-23, EV-CZLIFT-376eee); exponential-height and twist/E(K) clauses unmeasured"
# D-GLS-3  ledger_refs: add
[EV-CZLIFT-376eee, EV-CZLIFT-b6fe48, EV-CZLIFT-ee9b23, DEC-20261023-26a6de, DEC-20261023-6931ab, DEC-20261023-488023, DEC-20261023-fdc4af, CORR-20261023-4ffd7e, RQ-CZLIFT-b9f765]
# D-GLS-4  obstruction.statement: replace the clause
#   "the program re-measured uniform reduction of small points on rank 0-11 curves and over Q(2^{1/3}) (CZLIFT, review pending)"
# with
#   "the program measured the small-point census on a rank 0..7 ladder and two 1977 record models at H <= 3e5 (EV-CZLIFT-376eee, EV-CZLIFT-b6fe48): reduction is not independent-uniform (kernel height floor) but the excess is capped at a factor 2 ln 2, so half coverage needs >= N_p/2 distinct global points at fixed rank; the exponential-height form is conditional (T1-T4) and unmeasured; E(K) and twists are unmeasured (the Q(2^{1/3}) run set was ruled inadmissible, DEC-20261023-fdc4af)"
# D-GLS-5  best_measured: replace with
"toy: N_E(H) within [0.963, 1.309] of the Neron-Lang count (ranks 1..7); coverage median 1.033 vs uniform null 1.002; 1 dependence in 3200 random-pair xedni lifts at relation bound 6 (p=101, tangent relation); planted dependence detected 48/48"
# D-GLS-6  revisit_when: append
"... or a lift family of rank >= r*(p) = 2 log p / log(2 log p) (record: about 60 at p = 2^256; record rank 29 recalled) that reduces to the prescribed target curve, or a method that finds short vectors of ker(red_p) or the target coset without discrete logs (CVP form; EV-CZLIFT-376eee resource_check)"
# D-GLS-7  forecloses: add
["closest vector problem in the kernel lattice of reduction", "kernel height floor", "rank versus discriminant ladder of record curves"]
# D-GLS-8  related: add [LEAD-ICP-char0-lifting-xedni-smoothness, LEAD-EXO-global-lift-height]
```

### LEAD-TRF-anomalous-padic-lift (closed_known, unchanged)

```yaml
# D-ANOM-1  evidence: add
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-712fe4.yaml,
   note: "toy: 29 CM anomalous curves p<=1373: j-distance degeneracy rule 14,616/14,616 rows; Smart recovers d 2,052/2,052 per seed off the canonical class; degenerate-lift next digit 93 and 87 of 5,256 vs 86.84 expected"}
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-e9a7cf.yaml,
   note: "toy: 41 CM anomalous curves p to 97,813: rule 4,608/4,608 rows; 0/3,456 non-canonical next-digit successes (95% bound 8.7e-4); does not test the 1/p rate"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-147f9f.yaml,
   note: "H-CZLIFT-889c9d supported, scoped, toy"}
# D-ANOM-1b evidence[2] (DEC-20261009-44c288) note: replace "evidence round not yet filed" with "evidence round filed: EV-CZLIFT-712fe4, EV-CZLIFT-e9a7cf"
# D-ANOM-2  obstruction.statement: replace "(CZLIFT runs, review pending)" with
"(EV-CZLIFT-712fe4, EV-CZLIFT-e9a7cf: the degeneracy rule v_p(z([p]P^)) >= 2 iff v_p(j - j_can) >= 2e is a known theorem (Serre-Tate; Belding 2007 sec 7) measured at toy scale; on a split lift the homomorphic sections mod p^2 form a torsor under Hom(E(F_p), F_p), so a section with rate 1/p + eps has DL advantage eps)"
# D-ANOM-3  ledger_refs: add
[EV-CZLIFT-712fe4, EV-CZLIFT-e9a7cf, H-CZLIFT-bd2017, DEC-20261023-147f9f, DEC-20261023-9de83a, DEC-20261023-66af3b]
# D-ANOM-4  caveat on H-CZLIFT-d3dc4b (no change to ledger_refs membership): add to evidence note of DEC-20261009-44c288 or as new entry
"explicit p-torsion-lift series instrument: run set inadmissible (DEC-20261023-66af3b, VAL-20261022-a38921); no measurement"
# best_measured: append "; j-distance rule 14,616/14,616 (p<=1373) and 4,608/4,608 (p to 97,813)"
```

### LEAD-TRF-padic-canonical-section (closed_obstructed, unchanged; wording narrowed)

```yaml
# D-SEC-1  obstruction.statement: replace
#   "... any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E."
# with
"Theorem scope (EV-CZLIFT-ad28f5; p >= 5, n prime, n != p, any good-reduction Z_p-lift): Hom(Z/n, E^(pZ_p)) = 0, so the unique homomorphic section over <P> is the n-torsion section s_tor (<= 2(bits(n)+bits(p^k))+1 additions), the Smart functional vanishes on it, and for any other section the Smart ratio equals z(tau_Q)/z(tau_P) with tau = s - s_tor. Not proved: that a non-homomorphic computable section recovers d only at rate 1/p; this is heuristic H-1, measured for the hensel_random, naive and Teichmuller sections (identity readout, toy, detection floor 4.2x-5.2x of 1/p; EV-CZLIFT-ad28f5, EV-CZLIFT-e9a7cf). On F_p^* the only excess is the no-carry region g^d mod p^2 < p (EV-CZLIFT-f2a401)."
# D-SEC-2  evidence[H-CZLIFT-6d4ed1] note: append "; supported in scope 2026-10-23 (DEC-20261023-36b4f0); mechanism sentences 'canonical lift contributes nothing' and 'recovering d needs tau(dP)/tau(P)=d' not supported (B-6, B-7)"
#          evidence[GOAL-CZLIFT-1516d5] note: replace "'no hypothesis has evidential standing'" with "6d4ed1 supported; fba874, bd2017 analyzed; d37231 rejected as posed; 889c9d supported (2026-10-23)"
# D-SEC-3  evidence: add EV-CZLIFT-ad28f5, EV-CZLIFT-f2a401, EV-CZLIFT-764f54, EV-CZLIFT-e9a7cf (notes as in the table rows 3, 4, 6, 8)
# D-SEC-4  best_measured: replace "...evidence records not filed" with
"toy: v_p(z([n]s_tor)) = k on 1116/1116 pairs; identity readout consistent with 1/p, excess above 4.2x-5.2x excluded (p<=600) and 0/576 per torsion section to p=97,813 (95% bound 5.2e-3); torsion-digit single-pair statistic below rho_min=0.28-0.98 on 42 records (n 47..613); naive F_p^* section succeeds exactly on g^d mod p^2 < p (24/24)"
# D-SEC-5  ledger_refs: add
[EV-CZLIFT-ad28f5, EV-CZLIFT-f2a401, EV-CZLIFT-764f54, EV-CZLIFT-e9a7cf, DEC-20261023-36b4f0, DEC-20261023-039ddf, DEC-20261023-2e7447, DEC-20261023-9de83a]
# D-SEC-6  revisit_when: append
"... or the leakage successor named in DEC-20261023-9de83a next_action (1) (record r and d per row; (r - d) mod p uniformity, chi-square of r against d, near-miss fraction |r - d|_p < p/100, structured-d stratum, CM non-canonical torsion arm, 84 anomalous primes in [1e4, 1e5]) finds structure; the exact-hit instrument is silent on tau-ratios biased toward d (EV-CZLIFT-e9a7cf resource_check)"
# related: add [LEAD-EXO-padic-jet-canonical-lift, LEAD-TRF-anomalous-padic-lift, LEAD-EXO-dl-character-sum-pseudorandom]
# forecloses: add ["torsion section digit character", "Fermat quotient p-adic logarithm on F_p^*", "homomorphic section torsor mod p^2"]
```


### LEAD-ICP-char0-lifting-xedni-smoothness (closed_known, unchanged)

```yaml
# D-XED-1  evidence: add
- {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-ee9b23.yaml,
   note: "random-pair xedni lifts p=101..12809, bound 6: 1/3200 dependent (tangent relation, holds mod p already); bounded mod-p relations preserved 1 of 1261; not a prescribed-pair certified dependence"}
# D-XED-2  ledger_refs: add [H-CZLIFT-cb95b8, EV-CZLIFT-ee9b23, DEC-20261023-488023, CORR-20261023-4ffd7e]
#          best_measured: append "; random-pair bounded search 1/3200 (EV-CZLIFT-ee9b23)"
```
`revisit_when` of this row requires a certified exact dependent lift found by the frozen bounded search with costs charged; the single hit above is a geometric mod-p relation and does not meet it.

### LEAD-EXO-padic-jet-canonical-lift / LEAD-EXO-global-lift-height (cross-references only)

```yaml
# LEAD-EXO-padic-jet-canonical-lift: related += [LEAD-TRF-padic-canonical-section]; ledger_refs += [EV-CZLIFT-ad28f5]
#   (both rows rest on vanishing of the formal logarithm on prime-to-p torsion; the two lead rows overlap and currently do not reference each other)
# LEAD-EXO-global-lift-height: related += [LEAD-TRF-global-lift-small-height]; evidence += EV-CZLIFT-376eee
#   (Q-lift counting bound; the record does not evaluate the rank threshold r*(p) for elliptic surfaces over F_p(t), so no change to next_action)
```

### LEAD-ICP-full-width-arity-grid (open_blocked, unchanged)

```yaml
# D-FW-1  ledger_refs: add [H-ICPERF-3982eb]
# D-FW-2  evidence: add
- {repo: crypto-autoresearcher, path: experiments/EXP-ICPERF-554db4/specification.yaml,
   note: "k11 ordinary-binary arm design: canonical (sorted) summand order of the m=8 B=316 chained S3 circuit vs unsorted, two separately planted controls, 1200 s / 1 thread / 8 GiB RSS, 0 natural calls; specified, approved_by null; instrument hypothesis, no cost claim (H-ICPERF-3982eb)"}
# D-FW-3  next_action.step: append after "same for the k11 ordinary-binary matched bases":
"; the k11 arm is specified as sorted-vs-unsorted planted-control calls (H-ICPERF-3982eb, EXP-ICPERF-554db4) and decides only whether the planted calls clear a 1200 s cap"
# related: add [LEAD-ICB-decomposition-encoding-and-sat]   forecloses: add ["canonical summand ordering of the m=8 chained S3 circuit"]
# coverage.tsv: H-ICPERF-3982eb<TAB>LEAD-ICP-full-width-arity-grid
```

### LEAD-TRF-small-genus-cover-general (closed_obstructed, unchanged; scope note)

```yaml
# D-GEN-1  ledger_refs: add [H-PEXT-d536a1, DEC-20261024-992998, DEC-20261024-e29f4c]
# D-GEN-2  evidence: add
- {repo: crypto-autoresearcher, path: ledger/hypotheses/H-PEXT-d536a1.yaml,
   note: "design-stage, nothing measured (approved pre-run, EXP-PEXT-212d5c): derived n=7 odd-char floors: m in {1,3,4,6,7}; g=7 only for split 2-torsion via (m,r)=(3,7); 161 (E(K)[2]=Z/2), 193 (#E(K)=2 mod 4), 193 (odd order, j not in F_q); char-2 arm at N=7l; novelty unverified vs KN-LIT-bf1772"}
# D-GEN-3  obstruction.statement: append "Scope does not yet include k = 7 or k = 4, 5: n = 7 floors are derived in H-PEXT-d536a1 and unmeasured until EXP-PEXT-212d5c is reviewed; census directories research/ghs_cover_census_n5_20261013 and research/ghs_cover_census_n4_20261024 (crypto) are not cited by this row and were not read in this audit."
# coverage.tsv: H-PEXT-d536a1<TAB>LEAD-TRF-small-genus-cover-general ; IDEA-20261024-b58e07<TAB>LEAD-TRF-small-genus-cover-general
# related: add [LEAD-TRF-ghs-binary-composite]   (char-2 arm at N = 7l reproduces KR-IC-791cb7 magic numbers)
```

### LEAD-EXO-methodology-instruments (open_next_step, unchanged) and LEAD-ICE-curve-presentation-invariance

```yaml
# D-METH-1  LEAD-EXO-methodology-instruments.ledger_refs: add [H-SEMAEV-94dab2, DEC-20261018-a7a0fd, DEC-20261023-fdc4af, DEC-20261023-66af3b]
# D-METH-2  LEAD-EXO-methodology-instruments.evidence: add
- {repo: crypto-autoresearcher, path: ledger/hypotheses/H-SEMAEV-94dab2.yaml,
   note: "record integrity: shared harness/semaev.py s4_expr dropped x3 before 2026-08-13; exposed runs MTIC-007/008/010/010b, FIB-004/005, ICINV-e0cd8f m3class m4 stage; matched legacy-vs-repaired rerun designed (EXP-SEMAEV-93d5cc), effect size unmeasured, no evidence record filed"}
- {repo: crypto-autoresearcher, path: ledger/decisions/DEC-20261023-fdc4af.yaml,
   note: "independent validation ruled two CZLIFT run sets inadmissible on instrument defects (also DEC-20261023-66af3b): examples of validation catching a defective instrument"}
# D-METH-4  LEAD-RHO-dp-multitarget-precomputation (area MTIC): ledger_refs += [H-SEMAEV-94dab2]; add evidence note:
"MTIC-family outputs (EXP-MTIC-001 runs 007/008/010/010b, K* crossover) were produced with the legacy s4_expr; effect size unmeasured (H-SEMAEV-94dab2); this row's cited controls are crypto-repo benchmarks, not MTIC runs"
# D-METH-3  LEAD-ICE-curve-presentation-invariance.evidence[EV-ICINV-8afb64]: append note
"run archived legacy-defect s4_support (227 in 274 of 276 m4 records, docs/reports/2026-10-18-semaev-s4-factor-base-audit.md); this EV does not cite m4; H-SEMAEV-94dab2 P2 predicts the CLASS-VARYING verdict is unchanged (prediction, not a result)"
#          ledger_refs: add [H-SEMAEV-94dab2]
# coverage.tsv: H-SEMAEV-94dab2<TAB>LEAD-EXO-methodology-instruments
```

## 3b. Disposition changes proposed

One confirmation entry, no change of value:

| lead | from | to | deciding record | reason |
|:--|:--|:--|:--|:--|
| LEAD-TRF-padic-canonical-section | closed_obstructed | closed_obstructed | DEC-20261023-36b4f0 (evidence EV-CZLIFT-ad28f5, hypothesis H-CZLIFT-6d4ed1 supported in scope) | First filed evidence for a closure whose row says "no hypothesis has evidential standing"; the proof-kind obstruction stands for the homomorphic-section statement (Hom(Z/n, E^(pZ_p)) = 0, n != p), and the 1/p statement for other sections is narrowed to a measured heuristic (D-SEC-1). |

Nothing else changes disposition. Two rows carry wording that goes beyond what the filed evidence supports; I propose narrowing the wording, not the disposition:

- `LEAD-TRF-padic-canonical-section` keeps `closed_obstructed` / `kind: theorem` for the proved scope (homomorphic sections, n != p). The 1/p statement for non-homomorphic sections is a measured/heuristic claim (EV-CZLIFT-ad28f5 H-1). README rule 1 says a null is not an obstruction; if the Coordinator adopts the leakage successor of DEC-20261023-9de83a next_action (1), the row would carry a runnable discriminating step and an `open_next_step` reading becomes available. I do not propose that change now because that contract is "not approved here".
- `LEAD-TRF-global-lift-small-height` keeps `closed_known`; the obstruction now rests on literature plus a fixed-rank counting bound that the record derives under assumptions T1-T4 and measures only at toy scale.

## 4. Raw `--match` top hits (score, id, disposition, title)

Env set to the three sibling checkouts. Top 5 lines of each call, unedited. Records sharing a group were matched with the same two phrasings (the CZLIFT EV and its hypothesis describe one mechanism).

### 4a. Per record group

#### G_GLOBAL (EV-CZLIFT-376eee, H-CZLIFT-9a32e9)

- phrasing: `small rational points reduce mod p uniformly coverage height lattice ball counting obstruction global lift`

```
   24  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   19  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   11  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   11  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
```

- phrasing: `xedni calculus Mordell-Weil rank lift height (log H)^{r/2} half coverage of E(F_p)`

```
   32  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   21  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   19  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   19  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   15  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
```

#### G_RANKREC (EV-CZLIFT-b6fe48, H-CZLIFT-27a184)

- phrasing: `rank record curves small rational points Elkies Watkins high rank lift global`

```
   31  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   14  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
   10  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    9  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
```

- phrasing: `Grunewald-Zimmert Brumer-Kramer record rank curve naive height count lift`

```
   13  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   10  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    8  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    6  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    5  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```

#### G_XEDNI (EV-CZLIFT-ee9b23, H-CZLIFT-cb95b8)

- phrasing: `xedni lift random points dependence relation bound Jacobson Koblitz Silverman Stein Teske`

```
   21  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   18  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   16  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   14  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```

- phrasing: `lifted points rational dependence rank deficiency Weierstrass fit mod p relation`

```
   17  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   11  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   11  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    9  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
```

#### G_NF (H-CZLIFT-89e169)

- phrasing: `number field lift Q(2^{1/3}) E(K) small points reduce at split primes`

```
   22  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   15  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   12  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    9  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
```

- phrasing: `SNFS number field lift elliptic curve cyclotomic rank points reduction`

```
   29  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   17  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   11  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   10  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```

#### G_ANOM (EV-CZLIFT-712fe4, H-CZLIFT-889c9d)

- phrasing: `Smart attack canonical lift degeneracy j-distance rule anomalous CM curve Serre-Tate split p-torsion`

```
   27  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   22  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   17  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   11  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
   10  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
```

- phrasing: `anomalous curve p-adic formal logarithm lift next digit precision p^3 random section`

```
   22  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   21  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   21  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   11  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    8  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
```

#### G_SPLIT (H-CZLIFT-d3dc4b)

- phrasing: `level-1 Serre-Tate splitting anomalous lift p-torsion lift explicit construction formal group exponential`

```
   15  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   13  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    7  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
    7  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
```

- phrasing: `split extension p-torsion E[p] mu_p canonical lift q p-th power`

```
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    7  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
```

#### G_SECT (EV-CZLIFT-ad28f5, H-CZLIFT-6d4ed1)

- phrasing: `canonical section prime-to-p torsion section formal logarithm vanishes non-anomalous curve`

```
   27  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   22  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    9  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    6  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
```

- phrasing: `Smart ratio tau non-canonical offset Hom(Z/n, Z_p)=0 Hensel lift section`

```
   17  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   12  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    7  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    6  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
```

#### G_DIGIT (EV-CZLIFT-764f54, H-CZLIFT-fba874)

- phrasing: `p-adic digits of torsion section coordinates character correlation discrete logarithm`

```
   25  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   12  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    9  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    9  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    8  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

- phrasing: `torsion section digit function additive character Fourier bias formal logarithm vanishes on torsion`

```
   16  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   15  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   15  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    7  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    7  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
```

#### G_LARGEP (EV-CZLIFT-e9a7cf, H-CZLIFT-bd2017)

- phrasing: `canonical lift rule torsion section identities large p 10^5 Smart anomalous replicate`

```
   19  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   17  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   17  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   12  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
```

- phrasing: `leakage partial bits hidden number lattice Smart ratio tau-ratio bias section`

```
   12  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    8  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    6  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    6  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    6  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
```

#### G_GM (EV-CZLIFT-f2a401, H-CZLIFT-d37231)

- phrasing: `multiplicative group Teichmuller section Fermat quotient p-adic logarithm discrete log F_p^*`

```
   19  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   13  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   11  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
   10  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
```

- phrasing: `naive integer section carry no-carry region small integer lift index calculus homomorphic`

```
   19  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   15  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   13  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   11  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
```

#### ICPERF (H-ICPERF-3982eb)

- phrasing: `canonical summand order sorted symmetry breaking binary index calculus SAT solver m8 GF(2^61)`

```
   15  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   14  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   13  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
```

- phrasing: `binary curve decomposition Boolean SAT planted relation summand ordering commutativity`

```
   13  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   12  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   11  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   11  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   11  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
```

#### PEXT (H-PEXT-d536a1)

- phrasing: `GHS cover genus floor odd characteristic n=7 span dimension 2-torsion Weil descent`

```
   24  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   23  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   18  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   17  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   13  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
```

- phrasing: `Weil descent extension degree 7 magic number divisor x^7-1 genus compositum double covers`

```
   22  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   19  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   17  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   15  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   14  KR-IC-e2d81b                                 known_result       ecGFp5 and degree-5 extension curves: published estimates
```

#### SEMAEV (H-SEMAEV-94dab2)

- phrasing: `Semaev summation polynomial S4 resultant defect s4_expr legacy matched rerun`

```
   17  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   10  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    9  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

- phrasing: `Semaev S4 summation polynomial harness bug x3 dropping archived runs recorded conclusions`

```
   14  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   10  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    9  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

### 4b. Extra phrasings used for the new-mechanism check (section 5) and for locating a home for H-SEMAEV-94dab2 / H-PEXT-d536a1

#### X_GROWRANK

- phrasing: `lift family with Mordell-Weil rank growing like log p over log log p reducing to a prescribed target curve`

```
   12  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
   12  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   10  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   10  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    9  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```

- phrasing: `kernel height floor counting bound Omega(p) enumeration distinct global points half of E(F_p)`

```
   13  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    6  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```

#### X_CVP

- phrasing: `closest vector problem coset of kernel lattice of reduction map Mordell-Weil lattice lifting target point`

```
   12  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
   10  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   10  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    8  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    8  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

#### X_TORSOR

- phrasing: `homomorphic sections mod p^2 torsor Hom(E(F_p),F_p) section d-homogeneity discrete log oracle`

```
   13  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
```

#### X_ONEBIT

- phrasing: `one-bit invariant E(Z/p^2) split recognizes canonical lift class without j_can Satoh`

```
   15  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    9  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    7  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
```

#### X_SEM_MTIC

- phrasing: `multi-target index calculus crossover K* amortized factor base logarithm table toy prime-field curves`

```
   23  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   22  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   18  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   18  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   17  LEAD-ICP-extension-field-embedding           closed_obstructed  Embedding E(F_p) into E(F_{p^n}) to buy a subfield factor base
```

- phrasing: `Semaev fiber geometric invariant per-target decomposition cost prime field m=3 factor base`

```
   18  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   18  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   17  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   17  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   17  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
```

#### X_SEM_S4

- phrasing: `S4 summation polynomial repaired resultant exact S4 degree 12 support 439 terms`

```
   13  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   13  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   13  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   10  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   10  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
```

- phrasing: `audit defect semaev.py recorded outputs rerun`

```
    6  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    6  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    6  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    6  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

#### X_PEXT

- phrasing: `cover census n=7 minimum genus per 2-torsion type`

```
   10  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
    8  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
    8  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    7  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    7  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
```

- phrasing: `odd-characteristic GHS cover genus floor 193 161 non-split 2-torsion`

```
   12  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   12  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
   10  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
```

#### X_ICPERF

- phrasing: `sorted summand order symmetry breaking SAT m8 k11 planted positive control wall-censored`

```
   12  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    7  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    7  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    6  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    6  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
```

#### X_LEAK

- phrasing: `leakage partial bits hidden number lattice Smart ratio tau-ratio bias section`

```
   12  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    8  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    6  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    6  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    6  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
```

#### X_SEM_METH (H-SEMAEV-94dab2, methodology home)

- phrasing: `shared harness defect record integrity instrument calibration matched rerun legacy versus repaired archived runs`

```
    9  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    6  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    6  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
```

## 5. Candidate mechanisms from resource_check readings: new_mechanism check

None of the following is filed as a new lead; each was matched with two or more phrasings (raw hits in section 4b).

| reading (source) | best hit (quoted) | why it is not a separate mechanism |
|:--|:--|:--|
| Lift family with rank >= r*(p) = 2 log p / log(2 log p) (EV-CZLIFT-376eee resource_check 1; routed to idea-generator by DEC-20261023-26a6de) | `12 LEAD-TRF-global-lift-small-height closed_known` / `12 LEAD-ICP-char0-lifting-xedni-smoothness` | The row's `revisit_when` already names "a lift family with rank growing like log p and provably small regulator"; the record supplies the threshold formula. Sharpen D-GLS-6. |
| CVP in the coset of ker(red_p) (EV-CZLIFT-376eee resource_check 2) | `10 LEAD-TRF-function-field-xedni-lift closed_obstructed`; `12 LEAD-TRF-one-point-self-pairing` for the CVP phrasing (unrelated mechanism) | Requires Lambda_p and the target coset, which the record says needs discrete logs (KN-LIT-7593 pattern); it is a reformulation of global lifting, covered by the same row. Add to `forecloses` (D-GLS-7). |
| Homomorphic sections mod p^2 are a torsor under Hom(E(F_p), F_p); a section with rate 1/p + eps has DL advantage eps (EV-CZLIFT-712fe4 resource_check 2) | `13 LEAD-STR-class-group-ecdlp-bridge open_next_step` (different object: Cl(O) vectorization) | The record calls it a reduction with no attack and a measurement method, "not filed as an idea". Recorded in D-ANOM-2. |
| One-bit invariant "E^(Z/p^2) split" recognises the canonical class mod p^2 in O(log p) (EV-CZLIFT-712fe4 resource_check 1) | `15 LEAD-TRF-cm-canonical-lift-heights closed_obstructed` | Recognition of a given lift's class, not construction of the canonical lift (that row's obstruction is the class-polynomial degree h(D) ~ p^{1/2}); the record says the pointer to Satoh-type point counting is recalled and "no ECDLP resource". Not proposed as an edit. |
| Bits of d in the Smart tau-ratio, residue tests (EV-CZLIFT-e9a7cf resource_check; DEC-20261023-9de83a) | `12 LEAD-EXO-hnp-advice-leakage open_blocked`; `8 LEAD-EXO-coordinate-statistic-leakage open_next_step` | Same family as the hidden-number conversion rows, applied to the p-adic section output; the natural home is `revisit_when` of LEAD-TRF-padic-canonical-section (D-SEC-6). That row's blocked_by note says no statistic with measured nonzero log-bit advantage exists; this measurement would test one more. The `digit-character` item in LEAD-EXO-coordinate-statistic-leakage (IDEA-20260921-1ec106) concerns Thue-Morse/Rudin-Shapiro signs of the coordinate's integer lift, a different digit expansion from the p-adic digits of EV-CZLIFT-764f54. |
| Sorted-summand order as symmetry breaking in the m = 8 SAT circuit (H-ICPERF-3982eb) | `12 LEAD-ICB-frobenius-search-symmetry closed_obstructed` (Frobenius symmetry, not summand permutation); `7 LEAD-ICP-icperf-binary-pdp-solver` | Instrument hypothesis on the existing k11 planted controls, listed under the full-width-grid row; S_m symmetrisation is already an encoding constant in LEAD-ICB-decomposition-encoding-and-sat. |

`new_mechanisms` = none.

## 6. Checks on coverage and ideas

- `coverage.tsv` current state: H-CZLIFT-27a184, -89e169, -9a32e9, -cb95b8 -> LEAD-TRF-global-lift-small-height; -6d4ed1, -bd2017, -d37231, -fba874 -> LEAD-TRF-padic-canonical-section; -889c9d, -d3dc4b -> LEAD-TRF-anomalous-padic-lift. H-ICPERF-3982eb and H-PEXT-d536a1 appear in `--coverage` as unmapped. H-SEMAEV-94dab2 does not appear in `coverage.tsv` and is not in the unmapped list: `ecdlp_records()` selects by area prefix from `orchestration/research-priority.yaml: ecc_areas`. Observed by loading that file: `ecc_areas` has 42 entries; ICPERF and PEXT are in it, SEMAEV, MTIC, FIB and CZLIFT are not. H-MTIC-001 (area MTIC) and H-FIB-001 (area FIB) are the originals exposed to the s4_expr defect and are likewise invisible to `--coverage`; the H-CZLIFT rows in `coverage.tsv` are hand-added rows for an area the tool does not select. The record's goal is GOAL-ECDLP-001, so it is an ECDLP record the coverage tool cannot see.
- IDEA `prior_art.lead`: IDEA-20261017-3f46a5 (source of H-ICPERF-3982eb) has `prior_art.lead` unset, `frontier_map: knowledge/frontiers/ecdlp`; IDEA-20261024-b58e07 (source of H-PEXT-d536a1) has `prior_art.lead` unset. Rule 4 of the README applies from IDEA-20261025 on, so neither is a violation. H-CZLIFT-* and H-SEMAEV-94dab2 have no source IDEA of this kind (H-SEMAEV source note: "No IDEA record exists"); other CZLIFT ideas (IDEA-20261009-*) are already in the rows' `ledger_refs`.
- `--check` currently reports two errors in an unrelated row (`LEAD-RHO-pool-class-quotient`: ecc-challenges paths missing); not touched by this group.

## 7. Limits of this review

- Evidence records were read through their summary fields; per-clause numbers above are quoted from those fields. I did not recompute any measurement or open run logs.
- Numbers for p ranges, curve counts and thresholds are each record's own scope (all `claim_tier: toy`). Nothing here supports a statement about cryptographic sizes.
- H-PEXT-d536a1 and H-ICPERF-3982eb are pre-run designs: their rows only record that the experiments exist and what they will decide. H-SEMAEV-94dab2 runs exist but no evidence or decision on their outcome is filed; I did not open them.
- The research directories `ghs_cover_census_n5_20261013` and `ghs_cover_census_n4_20261024` were listed, not read.

---

## Group: car-proposals-a

# Fold of group `car-proposals-a` into the ECDLP lead atlas (proposed diffs only)

Reviewer: lead-atlas "changed since review", step 2. No repository file was edited, created, added or committed; this file and the two raw match logs `match_raw_carA.txt` / `match_extra_carA.txt` (inlined below) are the only writes from this fold, all under the scratchpad `audit/` directory.

## 0. Scope, conventions, discrepancies

- **Paths.** `delta.txt` lines 92-109 list **18** files `ledger/proposals/IDEA-20261018-*.yaml` (1aff90 1bc873 2c37f5 2d21b9 49fdf7 4c28fc 670088 6c1c6e 88041d ac3694 b32287 b4bc61 b90b0c c0b13a c4adb6 e0857e e3bcff e7a860). The task text says 19; the task's own id list and `delta.txt` both name 18. All 18 were folded. If a 19th file exists it is not in the delta.
- **Method per path.** Read the proposal by summary fields (title, claim, mechanism, prior_art, citations); `lead_atlas.py --match` with two phrasings (raw top-5 hits inlined in Appendix A; extra queries in Appendix B); read the top lead rows with `showlead.py`; then checked sibling-repo records the idea or the lead points at (read-only, `scratchpad/crypto-main`, `cryptanalysis-main`).
- **Labels.** `OBS` = observed in a named file. `INT` = interpretation, conditional. A proposal is a plan, not a measurement; nothing here treats an idea's claim as a result.
- **`prior_art.lead`.** Absent on all 18 (their `prior_art` keys are `frontier_map, rows_checked, nearest, searched`). README rule 4 starts at IDEA-20261025, so this is not a violation. Each `searched.note` says the frontier map "was not rendered or matched in this logging pass"; Appendix A is that match. All `rows_checked` KR ids exist in `KRMAP.md`.
- **Coverage.** `lead_atlas.py --coverage` reports all 18 as `unmapped` (2049/2078 mapped). Section 4 gives the 18 `coverage.tsv` lines.
- **Ledger index.** `grep` of `ledger/.index/{proposals,hypotheses,experiments}.jsonl` finds each id only in `proposals.jsonl`; no hypothesis, experiment, decision, evidence, goal or knowledge file references any of the 18 ids. So no row is `decides_lead` and `disposition_changes` is empty: a proposal cannot decide a disposition.
- **Later crypto records.** Several crypto directories cited below (for example `dreg_closure_m4l6_20261018`, `k_conversion_20261018`, `sparse_la_timing_20261018`, `ic_improve_20261014/01-d4-2lp`) are not in `delta.txt` (the crypto delta is 16 `benchmarks/`, `docs/`, `problems/` files). They are read here only to state what an idea's premise looks like against the checkout; I do not fold them. Many are cited by no lead yet (list in section 5).
- **No status changes proposed.** Only atlas row edits and `coverage.tsv` lines.

## 1. Summary table (one row per path)

Action key: `adv` = advances_lead, `new` = new_mechanism. All 18 are ECDLP (index calculus, Weil descent, rho baselines or their instruments).

| # | path (ledger/proposals/) | ECDLP | action | lead | one-line reasoning (OBS then INT) |
|--:|:--|:-:|:-:|:--|:--|
| 1 | IDEA-20261018-1aff90.yaml | yes | adv | LEAD-ICE-descent-closure-degree-at-scale | OBS idea = GF(2) block Wiedemann consistency test for the (4,6) degree-5 memory case, XL bound only, priority low; lead next_action already says "or a sparse closure". `dreg_closure_m4l6_20261018` measured (4,6) at degree 4 with 25.8 GB. INT the remaining memory-blocked cell is C1 (3,7); XL bound sits 2-3 degrees above closure so it cannot decide C1. |
| 2 | IDEA-20261018-1bc873.yaml | yes | adv | LEAD-ICB-orbit-linear-algebra (secondary LEAD-ICP-prime-ic-constant-engineering) | OBS review corrected the "unreachable" premise (sparse-cado PR #1874, PR #2162); `sparse_la_timing_20261018` null on the E(F_{29^4}) ladder, `ic_linalg_pipeline_20261019` same S on a 32-bit prime curve. INT largely carried out below the lead's `revisit_when` scale; the 2LP regime where LA is material has no sparse measurement. |
| 3 | IDEA-20261018-2c37f5.yaml | yes | new | LEAD-ICP-fp4-gaudry-d4-ladder (proposed) | OBS idea and review say the stacked D4+2LP arm was never run; `crypto:research/ic_improve_20261014/01-d4-2lp/README.md` ran it: whole 1.025 [1.016, 1.037] REGRESSES, re-measured 1.0264 in `ic_improve_20261015/04-d4-2lp-fix` (which reports a no-large-prime first-dependency stop at 0.9792 [0.9725, 0.9855]). No lead is built on the E(F_{p^4}) Gaudry ladder. INT conflict reported, interpretation conditional. |
| 4 | IDEA-20261018-2d21b9.yaml | yes | adv | LEAD-EXO-ml-learned-models | OBS lead mechanism includes learned solver branching; best_measured is a worse learned WDSat policy. Desk dossier LEAD-08 (crypto) cites Caminata-Gorla: order cannot change solving degree on refuted targets; effect is stage-only. |
| 5 | IDEA-20261018-49fdf7.yaml | yes | adv | LEAD-ICE-generic-oracle-arity-cost-floor | OBS lead obstruction already cites CHW 2026/384 and DKM 2025/783, scope "oracles that do not read curve coordinates"; the row-to-model-class mapping table is not produced. Dossier LEAD-12 could not read the EC theorem of 2026/384. INT idea's claim is broader than the lead's scope. |
| 6 | IDEA-20261018-4c28fc.yaml | yes | adv | LEAD-ICP-retained-setup-online (secondary LEAD-RHO-dp-multitarget-precomputation) | OBS lead `revisit_when` is exactly an equal-bytes IC row vs BL rho; `equal_advice_wide_20261018/README.md`: instrument built, n=73/83 session frozen and not run. The N83 time/RSS-matched control already exists (PR #1987). |
| 7 | IDEA-20261018-670088.yaml | yes | new | LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp (proposed) | OBS the genus-3 hyperelliptic 2LP pipeline after cubic GHS has 4 crypto records (exponent 1.300; `ghs3_vs_rho_20261023`: 1 of 7 sizes "IC below the strong rho", 6 unresolved, crossover interval uninformative) and no lead; the only neighbour is the blocked plane-quartic/Smith branch. Round-4 baseline already includes block Wiedemann (2,1). |
| 8 | IDEA-20261018-6c1c6e.yaml | yes | adv | LEAD-ICB-prime-degree-algebraic-decomposition | OBS lead holds the m=4 price rows; FGHR arm has no owner (cofactor-torsion lead routes it to "engine family"). Faugere-Svartz half collides lexically with closed LEAD-ICB-frobenius-search-symmetry (whose obstruction is about the Frobenius group). INT FGHR applicability to subspace-base binary systems unverified. |
| 9 | IDEA-20261018-88041d.yaml | yes | adv | LEAD-ICE-descent-closure-degree-at-scale | OBS (4,6) premise superseded: `dreg_closure_m4l6_20261018/RESULTS.md` A1 refuted at degree 4 on 2 unsat draws (N=54, 25.8 GB); C1 (3,7) capped at 169 GB (projection 217 GB). Lead already cites it; add ledger_ref. Prime-degree lead's `blocked_by` "(4,6) exceeded 3 GB" no longer describes (4,6). |
| 10 | IDEA-20261018-ac3694.yaml | yes | adv | LEAD-ICE-charged-toy-ic-exponent-vs-rho | OBS dependency note; lead `blocked_by` already names the EXP-ICEX-153c34 backend; `experiments.jsonl`: EXP-ICEX-153c34 status approved. ledger_refs only. |
| 11 | IDEA-20261018-b32287.yaml | yes | adv | LEAD-ICE-chained-semaev-dreg-vs-semiregular (secondary LEAD-TRF-teske-secret-isogeny-trapdoor) | OBS four lanes; DREG C1 and the ECTD panel are already the two leads' `next_action`s. H-STR-002, H-DTREE-001, H-IC-001 are absent from `coverage.tsv` and not flagged by `--coverage`. No relabel proposed. |
| 12 | IDEA-20261018-b4bc61.yaml | yes | adv | LEAD-ICE-hybrid-guess-determine-l7 | OBS lead forecloses "crossbred on descent cells"; idea's "only m=2" premise is narrower than `e2e_panel.txt` (it has m=3, n=9). Desk dossier LEAD-07 predicts its own kill at (4,6); unverified desk model. |
| 13 | IDEA-20261018-b90b0c.yaml | yes | adv | LEAD-EXO-methodology-instruments (+ ledger_ref on LEAD-ICE-boolean-f4-f5-f6-engines) | OBS s4_expr half: KN-OPEN-5b3a08 audit update 2026-10-18 (fix on main, 21 runs exposed, impact unmeasured); the matched rerun is already approved and partly run as EXP-SEMAEV-93d5cc (trials 1-6 output_validated; outcomes not read). Mismatch half: cause isolated 2026-10-20 (BMI2 path) and already in the F4 lead's evidence. The `--match` hits were lexical misses. |
| 14 | IDEA-20261018-c0b13a.yaml | yes | adv | LEAD-ICE-descent-closure-degree-at-scale | OBS lead cites KR-IC-fbdb61; dossier LEAD-05 states closure = F4 = last fall = D_solve on the m=2 Solovyev family, which weakens the "cheaper instrument" premise (conditional). `fall_degree_bounds_20261008` (first fall degree) is cited by no lead. |
| 15 | IDEA-20261018-c4adb6.yaml | yes | adv | LEAD-ICE-linearization-excess-fb-prior | OBS same fitted rule D = 2 + [e<-3.5] + [e<-8.5] (MAE 0.06, 656 bases). Collision flagged with LEAD-ICB-factor-base-subspace-choice forecloses "geometric progression subspace beats random subspace": different matching basis (matched size vs matched dim(V.V)); not adjudicated. |
| 16 | IDEA-20261018-e0857e.yaml | yes | adv | LEAD-ICP-digit-presentation-solving-degree | OBS no lead text names PKM or the Kummer tower; coverage maps H-ECDLP-60de36 (the PKM heuristic) here. Records: m=4 D = 6,7,7,>=8 (N=8..20); m=3 N=21/24 inconclusive by wall, then memory (99.6 GiB), then the native `--max-dense` cap (~317 GB). Tension with closed LEAD-ICP-algebraic-membership-factor-base noted. |
| 17 | IDEA-20261018-e3bcff.yaml | yes | adv | LEAD-ICE-boolean-f4-f5-f6-engines | OBS `f4_gf2.rs`/`f4_gpu.rs` exist in cryptanalysis, not in crypto; the 426 s -> 5.7 s RTX 5090 figure was not located in cryptanalysis (quoted from the review). Lead is closed_dominated; its `revisit_when` is not met by a stage speedup. |
| 18 | IDEA-20261018-e7a860.yaml | yes | adv | LEAD-ICB-prime-degree-algebraic-decomposition | OBS K already measured: `k_conversion_20261018/README.md` K = 3.96-16.77 (median 4.48, n=83 step); the idea's flip condition log2 K < -7.6 is not met per that record. Lead cites it; its `next_action` text still lists K as to-do. ledger_ref + text update. |

Tallies: advances_lead 16, new_mechanism 2, decides_lead 0, not_ecdlp 0.

## 2. Per-record detail

Each record: OBS (with paths), INT (conditional), `--match` (best hit, why/why not the same), proposed row edit and `coverage.tsv` line. Paths are relative to the named repository root: `car` = `/Volumes/SSD990-2/crypto-autoresearcher`, `crypto` = `scratchpad/crypto-main`, `cryptanalysis` = `scratchpad/cryptanalysis-main`.

### 2.1 IDEA-20261018-1aff90 (area BINSTD, class algorithm, priority low)

- **OBS (idea).** A GF(2) block Wiedemann (Coppersmith) consistency test on the sparse Macaulay matrix would decide, for (4,6) at degree 5, solvability "using memory at least 10x below dense" (about 70 GB dense), and gives the plain-XL degree "as an upper bound". The idea's own `dominated_by`: "Dominated by the large-memory run of the degree cells if a node can be had; a fallback."
- **OBS (lead).** `car:knowledge/leads/ecdlp/ic-engine/LEAD-ICE-descent-closure-degree-at-scale.yaml` (open_blocked): `next_action.step` = run the frozen C1 cell "on a host with >= 250 GB RAM (or a sparse closure)"; `best_measured` already lists "closure degree 4 through (m,l) = (4,6), N = 54" and "(3,7) degree-5 closure capped at 169 GB"; it also states XL needs 5-7 where closure needs 3-4.
- **OBS (crypto).** `crypto:research/dreg_closure_m4l6_20261018/RESULTS.md`: A1 (m=4, n=15, l=6, N=54, S=-9) refuted at degree 4 on 2 unsatisfiable draws, satisfiable control not refuted, 25.8 GB measured against a 44 GB projection; C1 (m=3, n=19, l=7, degree 5) exhausted 169 GB of a 184 GB cap (projection 217 GB), "inconclusive".
- **`--match`.** Top hits `LEAD-ICB-orbit-linear-algebra` (15, 16): lexical on "Wiedemann"; not the same mechanism: that lead is the Frobenius-folded relation matrix over Z/r (`koblitz_sparse_la.rs`), this is a Macaulay consistency decision over GF(2). Next: `LEAD-ICE-chained-semaev-dreg-vs-semiregular`, `KR-IC-f5c584`, `KR-IC-fbdb61`.
- **INT.** The (4,6)-at-degree-5 memory case in the idea is not the cell the lead is now blocked on; the blocked cell is C1. A consistency test returns the plain-XL degree, which the lead's data put 2-3 degrees above the closure degree, so it would bound, not measure, C1.
- **Proposed edit** to `LEAD-ICE-descent-closure-degree-at-scale`: `ledger_refs += IDEA-20261018-1aff90`; in `next_action.step` replace "(or a sparse closure)" with "(or a sparse closure; IDEA-20261018-1aff90 proposes a GF(2) block Wiedemann consistency test that returns only a plain-XL upper bound, own priority low, own dominated_by the large-memory run)". No disposition change.
- **coverage.tsv:** `IDEA-20261018-1aff90	LEAD-ICE-descent-closure-degree-at-scale`

### 2.2 IDEA-20261018-1bc873 (area BINSTD, class tooling, priority high)

- **OBS (idea).** Wire existing block Wiedemann/Lanczos with CADO-style filtering into `ic.pipeline`; measure the relation matrix (density, weights, post-filter dimension) and a counted-cost crossover; premise: `ic.pipeline` offers only dense or structured Gauss (`linalg.rs:250-279`, test `:379` rejects "wiedemann"). Regimes named: E(F_{p^4}) (LA 0.495 of the exponent, 0.420 with large primes) and genus-3 (local q^1.52).
- **OBS (review).** `crypto:research/ic_leads_review_20261018/README.md` section 3.3 carries two corrections: `sparse-cado` (PR #1874) already on main; PR #2162 wires `wiedemann`, `lanczos`, `filter+lanczos`, `filter+wiedemann`.
- **OBS (crypto).** `research/sparse_la_timing_20261018/README.md`: "Null or negative result"; sparse arms cost the same as baseline on one E(F_{29^4}) k=4 workload, 1.398x on the other, 1.206x in total; LA-scaling curve 5.72x at 128 columns falling to 1.030x at 4,096; cause named as the full-rank completion rule; "Genus 3 is not measured... not reachable from `ic.pipeline`". `research/ic_linalg_pipeline_20261019/README.md` (32-bit prime curve, |F| = 1,024..16,384): identical S (ops ratio 1.0000), sparse-cado `row_ops` 1.50-1.53x dense, LA wall cado/dense 0.72 (N=1,024) down to 0.25 (N=8,192), pair-table set-up 84% (8,192) / 89% (16,384) of dense wall time. I did not confirm that density, weight distribution and post-filter dimension are tabulated.
- **OBS (lead).** `LEAD-ICB-orbit-linear-algebra` (exhausted_at_scale): LA 0.0-2.7% of S in Tables A-C; CADO filter 10.40x on the phase at 262,144 columns; `revisit_when` = "Factor bases of 10^6+ columns or a large-prime arm that makes linear algebra a material share of S." Its evidence already cites `benchmarks/20261019-ic-linalg-pipeline-sparse-cado`. `crypto:research/ic_improve_20261014/01-d4-2lp/README.md` reports the D4 arm's LA share "under 10^-7".
- **`--match`.** `LEAD-ICB-orbit-linear-algebra` is the top hit in both phrasings (25, 28): same mechanism family (sparse filter + block Wiedemann/Lanczos on the relation matrix). Secondary host for the prime-curve measurement: `LEAD-ICP-prime-ic-constant-engineering` (forecloses "NFS-style relation filtering for the ECDLP matrix").
- **INT.** The idea's measurement was largely made at sizes far below the lead's `revisit_when` scale and returned null for S. The regime named by `revisit_when` (a large-prime arm with material LA share) has no sparse-LA measurement in these records: sparse_la_timing used the D4 ladder (LA share tiny) and genus 3 was unreachable.
- **Proposed edit** to `LEAD-ICB-orbit-linear-algebra`: `ledger_refs += IDEA-20261018-1bc873`; `evidence +=` `{repo: crypto, path: research/sparse_la_timing_20261018/README.md, note: sparse arms null end to end on E(F_{29^4}) ladder (1.206x total); genus 3 not reachable from ic.pipeline}` and `{repo: crypto, path: research/ic_linalg_pipeline_20261019/README.md, note: 32-bit prime curve N=1,024-16,384 identical S, cado row_ops 1.50-1.53x dense, LA wall 0.25-0.72x descriptive}`; `best_measured +=` "in ic.pipeline: same S; cado/dense row_ops 1.50-1.53 (prime, |F| <= 16,384)". Disposition unchanged. Secondary: `LEAD-ICP-prime-ic-constant-engineering` `evidence += research/ic_linalg_pipeline_20261019/README.md`.
- **coverage.tsv:** `IDEA-20261018-1bc873	LEAD-ICB-orbit-linear-algebra`

### 2.3 IDEA-20261018-2c37f5 (area ICPERF, class composition, priority high) -> NEW MECHANISM

- **OBS (idea).** Stacking D4 symmetry (18.2x [16.4, 20.8] whole-solve constant) with double large primes (LA exponent 0.495 -> 0.420 [0.405, 0.440]) gives end-to-end cold S below the D4-only arm "at the largest measured sizes with a lower fitted exponent"; mechanism text: "Measured separately and never run together." The review (`crypto:research/ic_leads_review_20261018/README.md` sections 2.2, 3.4) says the same.
- **OBS (conflict).** `crypto:research/ic_improve_20261014/01-d4-2lp/README.md` (IC improvement round, 2026-10-14, protocol frozen before data) ran D4 + 2LP stacked: tuned D4+2LP / D4 whole-cost pooled paired ratio **1.025 [1.016, 1.037] REGRESSES**; exponent difference **+0.0055 [+0.0036, +0.0078] REGRESSES**; relation phase 1.025 REGRESSES; LA phase 0.827 [0.802, 0.853] ADVANCES; "the D4 LA share is under 10^-7"; Gaudry-alpha variant 2.355 [2.043, 2.702]; fitted handover at #E ~ 2^128.9 which the record calls "an extrapolation, not a measurement... indicative only"; 24 held-out curves, p = 101..1301; controls: A/A null identical on 24/24, positive control `d4-half` 2.033 inside the pre-registered [1.6, 2.5]. `research/sparse_la_timing_20261018/README.md`: no sparse arm lowers end-to-end S on this ladder. `crypto:research/ic_improve_20261015/04-d4-2lp-fix/README.md` (round 2 item 04, 2026-10-15) re-measured the 2LP arm at 1.0264 [1.0179, 1.0362] REGRESSES (27 held-out curves, p = 101..1601) and states "The regression is fixed by removing the large primes, not by better large primes": its `d4-ed` arm (first-dependency stop, no large primes) is 0.9792 [0.9725, 0.9855] ADVANCES at the constant level with the exponent MATCHES, and its adaptive-alpha arm `d4-adapt` MATCHES `d4` at every measured size (frozen rule leaves plain D4 at #E ~ 2^116.5, "an extrapolation, not a measurement"). `crypto:research/fp4_d4_ladder_20261023/` holds `PROTOCOL.md`, `cards/` and `specs/`, with no `sessions/` directory and no results file; the receipt `cards/CARD-fp4-d4-ladder-20261023-b3.receipt.json` reads `status: stopped at command 2`: `ecbench run ... SPEC-B.json --out .../sessions/B3` exited 143 after 1,842.755 s ("interrupted by signal 15 while waiting for /tmp/crypto-bench.lock"), `outputs: {}`. Cards A/B are unreported.
- **OBS (atlas).** `grep` of every lead yaml for `gaudry_quartic`, `fp4-ladder`, `ic_improve_20261014`, `d4_symmetrised` matches only `LEAD-ICP-residual-partial-relations` (one benchmark path `benchmarks/20261014-ic-next10-01-fp4-ladder`, used as an analogue in its `best_measured` and `discriminates`).
- **`--match`.** Phrasing 1 best hit `KR-IC-a4dd54` ("Hyperelliptic index calculus and the genus threshold", 9): a literature row, not an experiment on this ladder. `LEAD-ICB-large-prime-variants` (binary/Koblitz subspace bases) and `LEAD-ICP-residual-partial-relations` (prime-field m=2 pair-table engine) are 2LP leads in other settings. Extra queries (Appendix B): `KR-IC-46d822` (Gaudry, n fixed), `LEAD-ICP-gfp5-symmetrized-gaudry` (n=5, deployed EcGFp5, symmetrisation at H-GFPN-*) - same family of tricks, different n and curve family, and not the D4 toy ladder. No lead is built on the E(F_{p^4}) Gaudry ladder (7 crypto directories: `ic_next10_20261014/01-fp4-ladder`, `ic_improve_20261014/01-d4-2lp`, `gaudry_quartic_d4_*`, `sparse_la_timing_20261018`, `fp4_d4_ladder_20261023`, ...).
- **INT (conditional).** The idea's claim is stated as a prediction ("below the D4-only arm... lower fitted exponent"); the recorded held-out comparison went the other way at the measured sizes, with a handover that the record itself labels indicative. Whether a stacked arm helps would depend on the LA share becoming material, which the records place far above the measured sizes (handover 2^128.9 in item 01; 2^116.5 for the adaptive rule in item 04, both labelled extrapolations). Item 04's argument that any large-prime scheme needs at least the first-dependency stop's trials is the record's own, and is not re-derived here. This is a coverage gap: a ladder row would give the toy-ladder results a home. Alternative if the curator prefers not to add a row: append the 01-d4-2lp result to `best_measured` of `LEAD-ICP-residual-partial-relations`, but that lead's `next_action` is about the prime m=2 engine.
- **Proposed new row** `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-fp4-gaudry-d4-ladder.yaml` (draft, section 3.1). **coverage.tsv:** `IDEA-20261018-2c37f5	LEAD-ICP-fp4-gaudry-d4-ladder`. Also `LEAD-ICP-residual-partial-relations`: `related += LEAD-ICP-fp4-gaudry-d4-ladder`.

### 2.4 IDEA-20261018-2d21b9 (area DREG, class algorithm, priority low)

- **OBS (idea).** Learned monomial/variable ordering (HATSolver, arXiv 2512.14722) lowers counted cost of msolve/F4 on Semaev and PKM cells by >= 2x on >= half of held-out cells; the idea notes "the M7/M9 predictors there are null beyond size".
- **OBS (lead).** `LEAD-EXO-ml-learned-models` (open_next_step): mechanism lists "a solver branching policy"; `best_measured`: learned WDSat branching policy 16,097 conflicts vs paper default 3,092 on 8 heldout targets (worse); forecloses "learned SAT branching for point decomposition".
- **OBS (crypto, desk).** `crypto:research/pdp_literature_leads_20261022/leads/LEAD-08.md` (the dossier labels parts "unverified desk check"): variable order cannot change F4's solving degree on refuted/unique-solution targets (Caminata-Gorla arXiv 2112.05579 Thm 3.1, Cor 3.3, "read-at-source"); WDSat node count within +0.8% of 2^{3l}/3! at l = 6-7 (thesis Table 7.6); effect confined to F4 word-XOR cost where hand rules give 2-4.91x at stage level with S unchanged; kill rule requires >= 20% over the median random order on held-out cells. It also quotes ml-cryptanalysis `closure-degree-predictor` null (LODP 0 of 8). Not cited by any lead.
- **`--match`.** Phrasing 1 top hit `LEAD-ICP-digit-presentation-solving-degree` (14) is lexical on Semaev/PKM/msolve; `LEAD-ICE-boolean-f4-f5-f6-engines` (closed_dominated) is engine engineering, not learned ordering. `LEAD-EXO-ml-learned-models` ranks 2 in phrasing 2 and is the mechanism match.
- **Proposed edit** to `LEAD-EXO-ml-learned-models`: `ledger_refs += IDEA-20261018-2d21b9`; `evidence += {repo: crypto, path: research/pdp_literature_leads_20261022/leads/LEAD-08.md, note: desk dossier - variable order cannot change F4 solving degree on refuted targets (Caminata-Gorla); WDSat nodes within +0.8% of 2^(3l)/3!; effect stage-only}`; `forecloses += "learned monomial or variable ordering for F4/msolve on Semaev systems"`. `next_action` unchanged.
- **coverage.tsv:** `IDEA-20261018-2d21b9	LEAD-EXO-ml-learned-models`

### 2.5 IDEA-20261018-49fdf7 (area ICPERF, class control, priority medium)

- **OBS (idea).** Tabulate every pair-table, k-sum and 6-sum row (ECC2K-130, n = 85, 89 rungs) against DKM (ePrint 2025/783) and structured GGM (ePrint 2026/384); claims "an EC index calculus must exploit structure in at least a 1/sqrt(q) fraction of points to beat rho" and that the tabulation "finds none that violates them".
- **OBS (lead).** `LEAD-ICE-generic-oracle-arity-cost-floor` (closed_obstructed) obstruction statement already contains "in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically"; `revisit_when` names an oracle that reads coordinates (see `LEAD-ICE-descent-closure-degree-at-scale`).
- **OBS (crypto, desk).** `research/pdp_literature_leads_20261022/leads/LEAD-12.md` / README table: verdict "unverifiable-from-here for the one statement it most wants (the elliptic-curve theorem of ePrint 2026/384 could not be read)"; 14-row classification delivered; "none of CGK, Shoup, DKM or SGGM constrains an oracle that reads coordinates".
- **`--match`.** Top hits are weak (best 6, `LEAD-ICP-coincidence-harvest-structured-base`; phrasing 2 `KR-IC-a4dd54` 16, `KR-RHO-13bf67` 16, `LEAD-ICE-generic-oracle-arity-cost-floor` 16): the generic-oracle floor lead is the mechanism match.
- **INT.** The mapping table is the unperformed deliverable. The idea's EC statement is broader than the lead's stated scope; a note on the lead should stay inside that scope and carry the dossier's "EC theorem unread" caveat.
- **Proposed edit** to `LEAD-ICE-generic-oracle-arity-cost-floor`: `ledger_refs += IDEA-20261018-49fdf7`; `evidence += {repo: crypto, path: research/pdp_literature_leads_20261022/leads/LEAD-12.md, note: desk theory gate; EC theorem of 2026/384 not read; bounds do not constrain coordinate-reading oracles}`; `next_action` stays absent (closed). No disposition change.
- **coverage.tsv:** `IDEA-20261018-49fdf7	LEAD-ICE-generic-oracle-arity-cost-floor`

### 2.6 IDEA-20261018-4c28fc (area ICPERF, class control, priority high)

- **OBS (idea).** Co-measure Bernstein-Lange preprocessing rho and compact-orbit IC at equal advice at n = 73, 83, one resource envelope, record log2(S*T^2) - log2(r/|Aut|); claim BL > 10x faster online (the n=83 50-100x figure is called "not measured").
- **OBS (lead).** `LEAD-ICP-retained-setup-online` (closed_dominated): `revisit_when` = "An IC online row that beats BL preprocessing rho at equal advice bytes and equal setup"; obstruction already: BL 53-317x faster online at n = 41/53/61, precomputed rho wins every N83 matched pair. `LEAD-RHO-dp-multitarget-precomputation` (closed_known) carries the same incumbent.
- **OBS (review/crypto).** `ic_leads_review_20261018/README.md` section 2.1 correction: the time- and RSS-matched N83 control exists on main (PR #1987); the open form is equal-bytes, one process group, co-measured. `crypto:research/equal_advice_wide_20261018/README.md`: "instrument built and checked; the n = 73 / n = 83 session is frozen and NOT run"; instrument check at n = 61 narrow vs wide "identical counters on 24/24 rows".
- **`--match`.** Phrasing 2 puts `KR-RHO-ea34b8` (13), `LEAD-RHO-dp-multitarget-precomputation` (11), `LEAD-RHO-lhw-preprocessing-frontier` (11), `LEAD-ICP-retained-setup-online` (10) on top. `lhw-preprocessing-frontier` is the low-Hamming-weight DLP class, a different scheme; `retained-setup-online` is the lead whose `revisit_when` the idea would test.
- **Proposed edit** to `LEAD-ICP-retained-setup-online`: `ledger_refs += IDEA-20261018-4c28fc`; `evidence += {repo: crypto, path: research/equal_advice_wide_20261018/README.md, note: equal-bytes co-measured instrument built; n = 73/83 session frozen, not run}`. Secondary `LEAD-RHO-dp-multitarget-precomputation`: `ledger_refs += IDEA-20261018-4c28fc`. No disposition change.
- **coverage.tsv:** `IDEA-20261018-4c28fc	LEAD-ICP-retained-setup-online`

### 2.7 IDEA-20261018-670088 (area ICPERF, class algorithm, priority medium) -> NEW MECHANISM

- **OBS (idea).** Add block Wiedemann with filtering to the genus-3 double-large-prime pipeline after cubic GHS; claims it lowers the local LA exponent below q^1.52, moves the whole-solve exponent "from 1.368 toward the 4/3 target" and removes the memory block at 2^23.
- **OBS (crypto).** `research/ic_next10_20261014/07-cubic-ghs-genus3/README.md`: hyperelliptic branch (m=3, r=5) "POSITIVE under the frozen decision rule, at toy scale, with a qualification on the crossover"; 24/24 correct; IC-2LP exponent 1.300 [1.292, 1.308] all sizes, 1.377 [1.363, 1.392] over q = 2^11..2^15; against the rho model IC-2LP is still 1.62x more expensive at q = 2^15 and 2.29x against ideal negation rho; plane-quartic (Diem) branch "BLOCKED". `research/ghs3_vs_rho_20261023/TABLES.md` (protocol frozen 2026-10-23; scope: `E0/F_{q^3}`, `#E0 = 0 mod 4`, a cubic GHS cover by a genus-3 hyperelliptic curve; "Not prime-order curves"): 21 instances, log2 q = 14..20; per-size decision "IC below the strong rho" at log2 q = 16 only (geomean IC/R_ideal 0.701), "unresolved" at 14, 15, 17, 18, 19, 20 (geomeans 1.157, 1.150, 1.516, 1.423, 0.970, 1.274); per-curve IC/R_ideal from 0.524 to 2.394; OLS slope of log2(IC/R_ideal) on log2 q 0.0339 [-0.0465, 0.1050] per bit, root at log2 q = 11.46 [-35.59, 60.37]; with M_ell = 9 M_q the max IC/R_ideal per size is 3.321-12.418. The record's baseline arm is `w:lpsgebw2@cx+C1C2` with "structured Gaussian elimination, block Wiedemann (2, 1)" already included. `research/sparse_la_timing_20261018/README.md`: genus 3 "not reachable from `ic.pipeline`"; needs a genus-3 curve kind in ecbench or the relation-matrix registry wired into the example.
- **OBS (atlas).** `LEAD-TRF-odd-char-descent-smith-quartic` (open_blocked): mechanism = genus-3 hyperelliptic descent then Smith's isogeny to a plane quartic and Diem q^{4/3}; `next_action` = implement Smith's Props. 2 and 4; `best_measured` = toy plane-quartic correctness only; `blocked_by` = Smith construction not implemented. Its `forecloses` contains "genus 3 Weil descent in odd characteristic".
- **`--match`.** Phrasing 1: `LEAD-ICB-orbit-linear-algebra` 16, `LEAD-ICB-large-prime-variants` 14, `LEAD-ICP-residual-partial-relations` 13, `KR-IC-a4dd54` 11; phrasing 2: `LEAD-TRF-odd-char-descent-smith-quartic` 8; extra (Appendix B): `KR-IC-a4dd54` 34, `LEAD-TRF-odd-char-descent-smith-quartic` 17, `KR-IC-5ea2f8` 16, `LEAD-TRF-cover-catalog-jacobian-transfer` 11. The first three are LA/2LP leads in other settings (Koblitz relation matrix, binary subspace, prime m=2). The Smith lead is the nearest by phrase.
- **INT (conditional).** The Smith lead owns the plane-quartic branch (blocked, no measurement); the hyperelliptic genus-3 2LP branch has its own measured exponent, rho comparison and LA question and no row. The idea's "sparse LA is the missing stage" premise is partly in the baseline already (block Wiedemann (2,1)); whether the baseline includes CADO-style filtering is not stated in the protocol text I read. The `ghs3_vs_rho` record resolves no crossover (one size below rho, six unresolved). Alternative if the curator prefers no new row: widen `LEAD-TRF-odd-char-descent-smith-quartic` (title, `best_measured`, evidence) to cover the hyperelliptic branch.
- **Proposed new row** `knowledge/leads/ecdlp/transfer/LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp.yaml` (draft, section 3.2). **coverage.tsv:** `IDEA-20261018-670088	LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp`. Also `LEAD-TRF-odd-char-descent-smith-quartic`: `related += LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp`.

### 2.8 IDEA-20261018-6c1c6e (area DREG, class composition, priority medium)

- **OBS (idea).** "If the degree-5 row survives", FGHR 2-torsion symmetrisation lowers counted cost of the m=4 system by >= 30x ("30-416x, about 5-8.7 bits" measured elsewhere), moving the ECC2K-130 optimistic row "from +10.32 to between about +1.6 and +5.4 bits over rho"; Faugere-Svartz character blocks "never run". The mechanism text says only measured factors are stacked "after K is converted".
- **OBS (lead).** `LEAD-ICB-prime-degree-algebraic-decomposition` (open_blocked) holds the price rows (+7.6 before K, +9.78 at median K) and cites `research/k_conversion_20261018/README.md`, whose converted gaps are +9.78 (degree 4) and +12.48 (degree 5). The idea's +10.32 is the unconverted degree-5 row. Arithmetic only: 12.48 minus 5..8.7 bits = +3.8..+7.5 bits; this is a calculation, not a measurement.
- **OBS (other leads).** `LEAD-ICB-frobenius-search-symmetry` (closed_obstructed): mechanism lists "Faugere-Svartz character blocks in F4"; obstruction concerns the absolute Frobenius ("an equivariance between conjugate target instances, not a per-instance search symmetry"), equivariant elimination "2-3x against gf2_elim", "does not apply to the production pipeline systems (regresses 0.29-0.59x there)". `LEAD-ICB-cofactor-torsion-quotients` (closed_obstructed): "FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family)"; its 2-torsion census adds 0 relations. `LEAD-ICE-boolean-f4-f5-f6-engines` does not mention FGHR. `crypto:research/d4_symmetrised_s5_20261015/README.md` ran FGHR-coordinate D4 weighted Macaulay on E(F_{p^4}) (odd characteristic): C_w about 1.41e9, 844-863x below plain S4 (per the review table); the setting differs from the binary subspace-base system.
- **`--match`.** `KR-IC-5ea2f8` 12 and `LEAD-ICP-digit-presentation-solving-degree` 12 (lexical on "Weil descent"), `LEAD-TRF-ghs-binary-composite` 12; phrasing 2: `LEAD-ICB-prime-degree-algebraic-decomposition` 14, `LEAD-ICE-hybrid-guess-determine-l7` 14. The m=4 ECC2K-130 price row lives in the prime-degree lead.
- **INT.** The FGHR arm has no owning row; two closed leads point at "engine family" or mention Faugere-Svartz. The Faugere-Svartz sub-claim ("never run") sits next to a closed lead whose measured equivariant pass is that family, but whose obstruction is the Frobenius group, not 2-torsion translation; applicability of FGHR to the binary subspace-base systems is unverified. Reconciling the two is a curator question.
- **Proposed edit** to `LEAD-ICB-prime-degree-algebraic-decomposition`: `ledger_refs += IDEA-20261018-6c1c6e`; append to `next_action.step`: "Conditional second step: only if the degree-5 row survives C1 / l >= 7, run an FGHR 2-torsion arm on the same m=4 cells (first check FGHR applicability to subspace-base systems; convert K first)"; `related += LEAD-ICB-frobenius-search-symmetry, LEAD-ICB-cofactor-torsion-quotients`. No disposition change.
- **coverage.tsv:** `IDEA-20261018-6c1c6e	LEAD-ICB-prime-degree-algebraic-decomposition`

### 2.9 IDEA-20261018-88041d (area DREG, class measurement, priority high)

- **OBS (idea).** At (m,l) = (4,6) the solving degree "stays at 5", and slope cells m=3 l=8, m=4 l=7 rise by at most one per step; "Only memory is missing: (4,6) at degree 5 needs about 70 GB dense (N=40)". Competing reading "degree follows l" priced at about +112 bits.
- **OBS (crypto).** `research/dreg_closure_m4l6_20261018/RESULTS.md` (see 2.1): (4,6) at N=54 refuted at degree 4 on 2 unsatisfiable draws (25.8 GB), "m.l >= 21" refuted "as the explanation of the degree-5 step; l = 7 survives"; "Consequence for the ECC2K-130 m = 4 note: None yet"; C1 capped; "A2, B1, B2, C2: not run". `research/pdp_literature_leads_20261022/leads/LEAD-07.md` (desk): "the card's '70 GB at degree 5' is the N = 40 figure... (4,6) at n = 10 is 191 GB dense".
- **OBS (lead).** `LEAD-ICE-descent-closure-degree-at-scale` already cites the m4l6 RESULTS and its `next_action` covers C1 on >= 250 GB, A2/B1/B2 and (4,7); the m=3 l=8 stretch cell E8 is in `LEAD-ICE-hybrid-guess-determine-l7.next_action`. `LEAD-ICB-prime-degree-algebraic-decomposition.next_action.blocked_by` still reads "(4,5), (4,6), (13,4) and (13,5) exceeded the 3 GB cap".
- **`--match`.** Best `LEAD-ICP-digit-presentation-solving-degree` 25 / `LEAD-ICB-prime-degree-algebraic-decomposition` 24 / `KR-IC-fbdb61` 23 / `LEAD-ICE-descent-closure-degree-at-scale` 19 in phrasing 1 (lexical on "Weil descent degree cells"); phrasing 2 puts `LEAD-ICE-descent-closure-degree-at-scale` first (15), the mechanism match.
- **INT.** The idea's (4,6) premise is superseded by a record the lead cites; the cells still open are C1, (3,8), (4,7). The "+112 bits if degree follows l" competing reading is the lead's `discriminates` ">= 6" outcome.
- **Proposed edit.** `LEAD-ICE-descent-closure-degree-at-scale`: `ledger_refs += IDEA-20261018-88041d` (no other change). `LEAD-ICB-prime-degree-algebraic-decomposition`: in `next_action.blocked_by` replace "(4,5), (4,6), ... exceeded the 3 GB cap" with a statement that (4,6) was measured at N=54 with 25.8 GB (`research/dreg_closure_m4l6_20261018`) and C1 / (4,7) remain memory-blocked.
- **coverage.tsv:** `IDEA-20261018-88041d	LEAD-ICE-descent-closure-degree-at-scale`

### 2.10 IDEA-20261018-ac3694 (area ICEX, class tooling, priority medium)

- **OBS.** Self-described "DEPENDENCY NOTE, NOT A NEW EXPERIMENT": building the approved non-enumerative membership oracle EXP-ICEX-153c34 is the prerequisite named by DEC-20261001-9e675e. `ledger/.index/experiments.jsonl`: EXP-ICEX-153c34, hypothesis H-ICEX-6ca21f, status approved. `LEAD-ICE-charged-toy-ic-exponent-vs-rho` (open_blocked) `next_action` is "Build the EXP-ICEX-153c34 backend (G1 membership, O5 oracle, S/G/X/V counters, admission-refusing driver) and pass S0 gates G0-1..G0-6"; `blocked_by` "EXP-ICEX-153c34 backend unbuilt; dispatch gated on the C-7 host-load gate". Its `ledger_refs` do not list EXP-ICEX-153c34 or H-ICEX-6ca21f.
- **`--match`.** Top `LEAD-ICE-generic-oracle-arity-cost-floor` 6 (phrasing 1), `KR-RHO-825bca` 6 (phrasing 2): weak lexical hits; the charged-toy lead is where the experiment id lives (5 in phrasing 1).
- **Proposed edit** to `LEAD-ICE-charged-toy-ic-exponent-vs-rho`: `ledger_refs += IDEA-20261018-ac3694, EXP-ICEX-153c34, H-ICEX-6ca21f`. Nothing else.
- **coverage.tsv:** `IDEA-20261018-ac3694	LEAD-ICE-charged-toy-ic-exponent-vs-rho`

### 2.11 IDEA-20261018-b32287 (area ECDLP, class control, priority medium)

- **OBS (idea).** Fills infrastructure/artifact gaps in four lanes: DREG C1 (n=15, D=6; 11.7-12.2 GiB observed against an 8 GiB cap; needs >= 16 GiB), ECTD arity-3 panel ("17 of 20 arms lost to infrastructure"), H-STR-002 (missing artifacts), H-DTREE-001 (infeasible design). Explicitly "fills gaps without rewriting the original decisions"; `prior_art.nearest` = KN-OPEN-5b3a08.
- **OBS (leads).** `LEAD-ICE-chained-semaev-dreg-vs-semiregular` `next_action`: "Re-run item C1 (n = 15, D = 6, seeds as frozen) with a streaming native Macaulay builder under the lane's memory floor"; `best_measured`: "n = 15 D = 6 runs failed at 11.7-12.2 GiB". `LEAD-TRF-teske-secret-isogeny-trapdoor` `next_action`: re-run the approved 20-arm panel EXP-ECTD-0cf008, "every trial of run-20261016T0409Z died with psutil_import_missing". The counts differ ("every trial" vs "17 of 20 arms"); I did not open the run data to reconcile them.
- **OBS (coverage).** `grep` of `coverage.tsv` for `H-STR-002`, `H-DTREE-001`, `H-IC-001` returns nothing, and `--coverage` does not list them as unmapped, so the tool does not classify them as ECDLP records. They are index-calculus records by their own mechanism text (H-DTREE-001: "Standard prime-field index calculus (KN-TECH-003) decomposes each target directly...", area DTREE, question RQ-ECDLP-002). Reported, not fixed.
- **`--match`.** Weak (4 at most): phrasing 1 `LEAD-ICE-decomposition-probability-audit` 3, `LEAD-ICP-isogeny-transported-relation-yield` 3; phrasing 2 `LEAD-EXO-cryptoscale-candidate-screen` 4, `LEAD-STR-endo-scalar-action-generic` 4. Neither covers the DREG lane; the two real homes were found by id grep (`H-DREG-*` -> chained-semaev lead in `coverage.tsv`; `H-ECTD-*` -> teske lead).
- **INT.** The two `next_action`s that this idea would unblock are already the leads' own; the idea adds a resource floor (>= 16 GiB). The "relabel infrastructure negatives" part of the review (section 3.2) would be a record-status action; none is proposed here.
- **Proposed edits.** `LEAD-ICE-chained-semaev-dreg-vs-semiregular`: `ledger_refs += IDEA-20261018-b32287`; append to `next_action.step` "(host >= 16 GiB per IDEA-20261018-b32287; recorded peak 11.7-12.2 GiB)". `LEAD-TRF-teske-secret-isogeny-trapdoor`: `ledger_refs += IDEA-20261018-b32287`.
- **coverage.tsv:** `IDEA-20261018-b32287	LEAD-ICE-chained-semaev-dreg-vs-semiregular`

### 2.12 IDEA-20261018-b4bc61 (area DREG, class composition, priority medium)

- **OBS (idea).** Crossbred (Joux-Vitse; ePrint 2024/992, preprocessing ePrint 2026/360) on the Weil-descended PDP cells vs F4 and WDSat; premise "tried only on the m=2 toy oracle at n=7, 9".
- **OBS (lead).** `LEAD-ICE-hybrid-guess-determine-l7` (open_next_step) mechanism: "Crossbred was tried only at m = 2 and 3 with n = 7 or 9"; `forecloses` includes "crossbred on descent cells"; evidence includes `research/crossbred_20260920/e2e_panel.txt`; `known_results: None`. `crypto:research/crossbred_20260920/e2e_panel.txt` has rows at (m=3, n=9): crossbred 11.7 relations/s vs enumerate 19,696.3 relations/s (about 1,700x), and a closing line "Relation collection stays Theta(2^n) with any oracle polynomial in the factor base; this prices the constant, not the exponent." `crypto:research/pdp_literature_leads_20261022/leads/LEAD-07.md` (desk, "unverified desk check"): "constant-factor candidate, lowest rung", expects its own kill `k > l` to fire at (4,6); notes crossbred preprocessing 8.8x wider than guess-then-F4 on the m=3 residual.
- **`--match`.** Phrasing 1: `KR-IC-e847d1` 11 (the literature row), `LEAD-ICP-icperf-binary-pdp-solver` 11, `LEAD-ICE-hybrid-guess-determine-l7` 9, `LEAD-ICE-sat-xor-pdp-oracle` 9. Phrasing 2: `KR-IC-e847d1` 24, `LEAD-ICE-hybrid-guess-determine-l7` 14. The hybrid lead is the only lead naming crossbred on descent cells; solver-choice leads (`icperf-binary-pdp-solver`, `sat-xor-pdp-oracle`) are about SAT vs Groebner.
- **INT.** The idea's "only m=2" premise is narrower than the recorded panel (m=3, n=9 present). Whether crossbred beats F4/WDSat at the descent cells remains unmeasured; the dossier prediction is a desk model that the repository's F4 (degree 4 where semi-regular reads 7-8) may contradict, as the dossier says.
- **Proposed edit** to `LEAD-ICE-hybrid-guess-determine-l7`: `ledger_refs += IDEA-20261018-b4bc61`; `known_results += KR-IC-e847d1`; `evidence += {repo: crypto, path: research/pdp_literature_leads_20261022/leads/LEAD-07.md, note: desk dossier; crossbred expected to hit its k > l kill at (4,6); unverified}`. No `next_action` change.
- **coverage.tsv:** `IDEA-20261018-b4bc61	LEAD-ICE-hybrid-guess-determine-l7`

### 2.13 IDEA-20261018-b90b0c (area ICPERF, class control, priority high)

- **OBS (idea).** (a) Re-run the 21 archived runs touched by the `harness/semaev.py` `s4_expr` bug and whole-curve factor-base sampling under fixed code; (b) root-cause the 48 of 168 inherited-F4 replay mismatches. `prior_art.nearest` = KN-OPEN-5b3a08 (relation "same").
- **OBS (s4_expr half).** `car:knowledge/open-problems/KN-OPEN-5b3a08.md` (itself in `delta.txt`, folded by another group), section "Audit update, 2026-10-18": repair is in `harness/semaev.py` on main (CORR-20260813-d9f0fa); `s4_expr` now vanishes exactly on the x-tuples with sign sums = O, 0 mismatches over 6561 and 1296 tuples; "The 21 MTIC/FIB runs are confirmed to have recorded commits that lack the repair. One more experiment is affected... RUN-ICINV-e0cd8f-m3class"; "Their numerical impact is still unmeasured; matched reruns remain required"; status left open pending a Coordinator decision (`coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`). `car:ledger/decisions/DEC-20261005-a67fea.yaml` approved EXP-DTREE-b93a15 / H-DTREE-8636a3 ("per-run immunity audit of the 21 archived runs"); `experiments.jsonl` lists EXP-DTREE-b93a15 as approved. A second, later decision in this delta, `car:ledger/decisions/DEC-20261018-a7a0fd.yaml` (decision `approve`, 2026-10-18, targets include H-SEMAEV-94dab2, EXP-SEMAEV-93d5cc, EXP-DTREE-b93a15, CORR-20260813-d9f0fa; seen only as an observation, another group folds it), approves a one-factor matched rerun ("The arms differ in one function bound by sha256; the archived programs, instances, seeds and caps are fixed"); `experiments.jsonl`: EXP-SEMAEV-93d5cc, status approved, title "Matched legacy/repaired s4_expr rerun of every archived S4-consuming run (EXP-MTIC-001, EXP-FIB-001, RUN-ICINV-e0cd8f-m3class)...". `DEC-20261019-5b9240` and `DEC-20261019-ebf1dc` (also in this delta) record "Trials 1-6 are output_validated" and that trial 7 (mtic-010b) was lost to container restarts and moved to successors EXP-SEMAEV-88c46c and EXP-SEMAEV-6e9dcf ("the cell is unmeasured, not negative"). I did not read the trial outcomes. `coverage.tsv` has no row for H-SEMAEV-94dab2 and `--coverage` does not list it.
- **OBS (mismatch half).** `crypto:research/validation_sweep_20261019/D-known-issues/item1_cross_isa_20261020/RESULT.md`: "Cause isolated: the x86-64-only BMI2 word-wise ('eager') rewrite in `inherited_f4.rs` charges a different word-XOR count than the portable bit-scatter path, and the method identity does not record which path ran"; table: 48 differing on x86 default builds (rustc 1.97 and 1.93.1), 0 on aarch64-under-qemu, 0 with BMI2 branch off (one-line patch); recommendation "not applied". `LEAD-ICE-boolean-f4-f5-f6-engines` already lists that file in `evidence`.
- **`--match`.** The hits are lexical misses: phrasing 1 best `LEAD-ICP-gfp5-rho-reference-audit` 11 then `KR-IC-f3da82` 9; phrasing 2 best `LEAD-ICB-factor-base-subspace-choice` 7, `LEAD-ICE-semaev-cover-monodromy` 7; Appendix B: `LEAD-ICP-gfp5-rho-reference-audit` 5 (harness-audit phrasing) and `KR-IC-f3da82` 9 (replay-mismatch phrasing). No lead owns "harness/record-integrity audit of index-calculus runs"; the closest atlas row by mechanism text is `LEAD-EXO-methodology-instruments` ("record integrity").
- **INT.** Half (b) appears answered by the cited record (conditional on its single recorded session and one x86 host, as it states). Half (a), the matched rerun of the 21 archived runs, is the subject of the approved and partly executed EXP-SEMAEV-93d5cc / H-SEMAEV-94dab2 (and the earlier-approved EXP-DTREE-b93a15 audit); its outcome is not read here. The idea therefore duplicates existing ledger work on half (a). Neither half changes a lead's disposition.
- **Proposed edits.** `LEAD-EXO-methodology-instruments`: `ledger_refs += IDEA-20261018-b90b0c, H-DTREE-8636a3, EXP-DTREE-b93a15, DEC-20261005-a67fea, H-SEMAEV-94dab2, EXP-SEMAEV-93d5cc` (and `DEC-20261018-a7a0fd` once its own group folds it); `evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-5b3a08.md, note: s4_expr fixed on main; 21 MTIC/FIB runs exposed; numeric impact unmeasured as of 2026-10-18; matched rerun approved as EXP-SEMAEV-93d5cc}`. `LEAD-ICE-boolean-f4-f5-f6-engines`: `ledger_refs += IDEA-20261018-b90b0c`; note on its inherited-F4 evidence: the 48 mismatches are the BMI2-path charge difference (RESULT.md), so inherited-F4 `solver_ops` is path-dependent across ISAs.
- **coverage.tsv:** `IDEA-20261018-b90b0c	LEAD-EXO-methodology-instruments`

### 2.14 IDEA-20261018-c0b13a (area DREG, class measurement, priority medium)

- **OBS (idea).** The last fall degree (Huang-Kosters-Yang-Yeo arXiv 1505.02532) computed for the descended systems upper-bounds the dense-closure solving degree within one degree on >= 90% of cells "at a fraction of the memory".
- **OBS (lead/KR).** `LEAD-ICE-descent-closure-degree-at-scale` lists `KR-IC-fbdb61` ("last fall degree... bounded independently of the extension degree under stated conditions"). `crypto:research/pdp_literature_leads_20261022/leads/LEAD-05.md` lines 123 and 163-164 (dossier verdict for LEAD-05 is "unverifiable-from-here"): last fall degree "by mutant closure on exactly Solovyev's family (m = 2...)"; "the paper reports last fall degree = D_solve on every instance. So closure = F4 = last fall = D_solve, XL above." `crypto:research/fall_degree_bounds_20261008/RESULTS.md` concerns first fall degree d_F at m=2 (E1, E1b, E2 only; "E3, E4 and E5 have not run"). Neither research dir is cited by any lead.
- **`--match`.** `KR-IC-fbdb61` 18/28, then `LEAD-ICE-descent-closure-degree-at-scale` 14/19, `LEAD-ICP-digit-presentation-solving-degree` 14/15 (lexical on "fall degree").
- **INT (conditional).** If the closure degree coincides with the last fall degree on the cells where both are computed (the dossier's reading on the m=2 family), a separate last-fall-degree computation would add a pre-screen only if it is cheaper in memory than the closure; that memory comparison is the idea's actual content and is unmeasured.
- **Proposed edits.** `LEAD-ICE-descent-closure-degree-at-scale`: `ledger_refs += IDEA-20261018-c0b13a`; `evidence += {repo: crypto, path: research/pdp_literature_leads_20261022/leads/LEAD-05.md, note: desk; closure = F4 = last fall degree = D_solve on m=2 Solovyev family; cheaper-instrument premise untested at m>=3}`. `LEAD-ICE-first-fall-degree-assumptions`: `evidence += {repo: crypto, path: research/fall_degree_bounds_20261008/RESULTS.md, note: E1/E1b/E2 at m=2: trace relation proved, Semaev d_F one below semi-regular, gap constant 1 at n<=18}`.
- **coverage.tsv:** `IDEA-20261018-c0b13a	LEAD-ICE-descent-closure-degree-at-scale`

### 2.15 IDEA-20261018-c4adb6 (area KIC, class composition, priority low, goal_ids empty)

- **OBS (idea).** Use the cryptanalysis fitted rule D = 2 + [e < -3.5] + [e < -8.5] (MAE 0.06 over 656 bases) and the "geometric-progression bases are 15-40x cheaper per query" finding as a prior in `fb-search`; first run the ready `fpn_decomposable` config (about 10 CPU-minutes) to turn the null M7/M9 result into a citable one.
- **OBS (lead).** `LEAD-ICE-linearization-excess-fb-prior` (open_unexamined; `ledger_refs: None`): same rule and same MAE, `next_action` = rank equal-size subspaces by e on the m=3/m=4 cells and compare closure degree and charged cost per query against a random-subspace control. `cryptanalysis:experiments/pdp-degree-heuristics/README.md` (exists): "seven factor-base families at matched size", "geometric progressions are optimal" for e at prime n.
- **OBS (collision).** `LEAD-ICB-factor-base-subspace-choice` (exhausted_at_scale) forecloses "geometric progression subspace beats random subspace"; its obstruction: "geometric-progression vs random at matched dim(V.V) weakened and replicated (EV-BINSTD-78ca0d, EV-BINSTD-b176df)". The comparison bases differ as stated in the two files: matched factor-base size (cryptanalysis README) vs matched dim(V.V) (lead). I do not adjudicate which claim holds.
- **OBS (ML).** `LEAD-EXO-ml-learned-models` and dossier LEAD-08 record the null M7/M9 predictors (`ml-cryptanalysis` is not a sibling checkout in this task; those figures are second-hand).
- **`--match`.** Phrasing 1 top `LEAD-ICE-linearization-excess-fb-prior` 11 (the mechanism match); phrasing 2 `LEAD-ICB-cofactor-torsion-quotients` 15 and `LEAD-ICB-quasi-subfield-polynomials` 15 (lexical on "predictor... prunes"), then `LEAD-ICE-linearization-excess-fb-prior` 14.
- **Proposed edit** to `LEAD-ICE-linearization-excess-fb-prior`: `ledger_refs += IDEA-20261018-c4adb6`; `related += LEAD-EXO-ml-learned-models`; add to `mechanism` or a note "the fb-search prior form is proposed by IDEA-20261018-c4adb6; its geometric-progression claim is compared at matched size, whereas LEAD-ICB-factor-base-subspace-choice's null is at matched dim(V.V)". Disposition stays open_unexamined.
- **coverage.tsv:** `IDEA-20261018-c4adb6	LEAD-ICE-linearization-excess-fb-prior`

### 2.16 IDEA-20261018-e0857e (area DREG, class measurement, priority high)

- **OBS (idea).** At m=3 the msolve degree is >= 8 at N=21 and >= 9 at N=24 ("about one degree per eight unknowns, as at m=4 over N=12-20"), so the PKM tower has no plateau; a plateau (D <= 7 at N=21) "would keep the m=3 prime-field exponent question open". Request: 256-512 GB host.
- **OBS (atlas).** `grep -il 'PKM\|pkm_'` over all lead yamls: no match; `tower|Kummer` matches only `LEAD-EXO-curve-model-representation`, `LEAD-ICB-oakley-quintic-tower`, `LEAD-ICP-algebraic-membership-factor-base`, `LEAD-TRF-pairing-target-field-recost`, `LEAD-TRF-small-genus-cover-general` (none of them the PKM tower). `coverage.tsv` line 414: `H-ECDLP-60de36 (mechanism: "PKM (PKC 2016) heuristic: a factor base with a low-degree, many-variable description..."; status rejected_scoped) -> LEAD-ICP-digit-presentation-solving-degree`. `LEAD-ICP-algebraic-membership-factor-base` (closed_obstructed): theorem that a target-independent algebraic locus of degree d yields O(d) points so a size-B base has description degree >= B/3, scope "prime-order E/F_p, any base of size B", `revisit_when` KN-OPEN-020. `LEAD-ICE-prime-field-semaev-solving-degree` (closed_known) `revisit_when`: a bounded-degree-independent-of-p base "produces a measured solving degree that stays flat across >= 3 field sizes".
- **OBS (records, quoted readings).** `crypto:research/ic_next10_20261014/03-pkm-degree/README.md`: m=4 line "D = 6, 7, 7, >= 8 at N = 8, 12, 16, 20" (msolve completes three productive degree-8 rounds, then the 5 GB cap; the README reads this as H0 "growth resumes" and flags "the D >= 8 is msolve's, on the raw presentation"); m=3 at N=18, 21, 24 "stopped by the 45-minute wall inside the second degree-7 step"; kill test "can be evaluated neither way". `research/pkm_m3_n21_msolve_20261018/RESULTS.md`: three N >= 21 runs stopped at their wall inside degree 7 (N=21: 15,458 s/15.3 GB and 7,728 s/8.9 GB; N=24: 8,328 s/13.0 GB), "inconclusive"; Amendment A1 (`-t 16`, 99.6 GiB used of a 108.8 GB cap): "Degree 7 ran out of pairs without the unit ideal. msolve then selected 398,409 degree-8 pairs and exited 139"; reading "inconclusive (memory stop, no productive degree-8 round... Not H0 and not a plateau reading)". `research/pkm_lead1_m3n21_20261016/RESULTS.md` + `research/large_memory_runs_20261018/EXPERIMENT_LOG.md` (native `f4_fp_tower`, 124 GB host): both N=21 targets stopped at the first degree-8 step by `--max-dense` (B' demand 7.93e10 entries, about 317 GB at 4 bytes, about 460 GB at the 1.45 ratio); "every degree-7 pair reduced without refuting... no productive degree-8 reduction... No verdict". `research/pdp_literature_leads_20261022/leads/LEAD-14.md` (desk): "closed-by-theorem" for multi-homogeneous block bounds on digit/Kummer-tower systems; formal values 7, 9, 11, 13 exceed the measured 6, 6, 7, 7 at m=3, N=9-18.
- **`--match`.** Original two phrasings: phrasing 1 `LEAD-ICE-prime-field-semaev-solving-degree` 11 and `LEAD-ICP-digit-presentation-solving-degree` 11; phrasing 2 `LEAD-ICP-digit-presentation-solving-degree` 15, `LEAD-ICE-chained-semaev-dreg-vs-semiregular` 13, `LEAD-ICE-prime-field-semaev-solving-degree` 13. Appendix B PKM phrasings: `KR-IC-5931ee` 14 / 11 (literature row), `LEAD-ICP-digit-presentation-solving-degree` 12 / 12, `LEAD-ICB-prime-degree-algebraic-decomposition` 11 / 11 (binary prime-degree, not F_p), `LEAD-ICB-quasi-subfield-polynomials` 10 / 10, `LEAD-EXO-curve-model-representation` 9 (Kummer = curve model, not the PKM tower). The digit-presentation lead is the nearest in mechanism (F_p analogue of Weil descent, solving degree vs number of unknowns).
- **INT (conditional).** No lead text records the PKM tower measurements. The coverage file places the PKM heuristic in the digit-presentation lead, so that is the host. The idea's claim (D >= 8 at N=21, >= 9 at N=24) is unmeasured in every record above; the records move the host requirement up (about 317-460 GB for the native cell; msolve exceeded 99.6 GiB). Tension to record, not resolve: a closed lead (algebraic-membership theorem, single-variable locus degree) coexists with an open exponent-deciding measurement on a many-variable presentation; the lead texts do not state whether the theorem covers the tower presentation. No disposition change proposed.
- **Proposed edit** to `LEAD-ICP-digit-presentation-solving-degree`: `ledger_refs += IDEA-20261018-e0857e, H-ECDLP-60de36`; `evidence +=` four entries ({crypto, research/ic_next10_20261014/03-pkm-degree/README.md, m=4 D = 6,7,7,>=8 at N=8,12,16,20; m=3 N=18-24 inconclusive}, {crypto, research/pkm_m3_n21_msolve_20261018/RESULTS.md, N=21/24 msolve inconclusive by wall then memory}, {crypto, research/pkm_lead1_m3n21_20261016/RESULTS.md, native N=21 stopped by --max-dense at first degree-8 step; no verdict}, {crypto, research/pdp_literature_leads_20261022/leads/LEAD-14.md, desk: block bounds do not apply}); `best_measured +=` "PKM tower (Kummer, F_p): m=4 D = 6,7,7,>=8 at N=8,12,16,20 (README reading); m=3 N=21/24 no verdict (wall/memory)"; `next_action.step` add a parallel arm "PKM tower m=3 N=21 degree-8 step on a host above the recorded ~317-460 GB native demand (IDEA-20261018-e0857e asks 256-512 GB)". Secondary: `LEAD-ICE-prime-field-semaev-solving-degree.related += LEAD-ICP-digit-presentation-solving-degree` only if the curator accepts the PKM tower as that lead's `revisit_when` instance.
- **coverage.tsv:** `IDEA-20261018-e0857e	LEAD-ICP-digit-presentation-solving-degree`

### 2.17 IDEA-20261018-e3bcff (area ICPERF, class tooling, priority medium)

- **OBS (idea).** Port `cryptanalysis` `f4_gf2` / `f4_gpu` into `crypto`, run on a device; claims >= 10x over `gf2_elim` ("25-75x on degree-6 matrices in cryptanalysis: 426 s to 5.7 s on an RTX 5090"); "whether it moves end-to-end S is measured, not assumed".
- **OBS (checkouts).** `cryptanalysis:suite/src/cryptanalysis/f4_gf2.rs` and `f4_gpu.rs` exist; `crypto:src/cryptanalysis/` has `gf2_elim.rs`, `f4_fp.rs`, `inherited_f4.rs`, ... and no `f4_gf2`/`f4_gpu` (grep of `crypto-main/src` finds none). The 426 s -> 5.7 s RTX 5090 timing was **not located** in a primary file of the cryptanalysis checkout (`grep -rIl f4_gpu` and a search for 426 with 5.7/GPU/5090 found nothing); it appears as a quotation in `crypto:research/ic_leads_review_20261018/README.md` section 2.4 and in the idea.
- **OBS (lead).** `LEAD-ICE-boolean-f4-f5-f6-engines` (closed_dominated, dominated by `LEAD-ICE-rootfind-pairtable-oracle`): "Engine speedups of 1.4x-2.3x (cryptanalysis)... are real, but priced F4 is far above both the pair table and rho"; `forecloses` includes "GPU RREF Groebner decomposition"; `revisit_when`: a descended cell where the pair table is infeasible (m >= 4 at large n) and the algebraic degree stays bounded, "or a priced engine beats the MITM floor slope on >= 3 cells". Obstruction numbers: inherited F4 22x-33x strong rho at K13, pair table 17x-22x cheaper than F4.
- **`--match`.** `LEAD-ICE-boolean-f4-f5-f6-engines` 7 / 7 (both phrasings), then `LEAD-RHO-ecc2k130-gpu-fpga-throughput` 7 and `LEAD-RHO-prime-gpu-rho` 7 (GPU rho kernels, a different object).
- **INT.** A stage-level speedup is a constant; the lead's dominance statement combines a constant ratio at n13 with a slope comparison. The `revisit_when` conditions are not met by the idea as stated. The measurement the idea proposes (does it move end-to-end S) is not in the lead.
- **Proposed edit.** `ledger_refs += IDEA-20261018-e3bcff`; `evidence += {repo: cryptanalysis, path: suite/src/cryptanalysis/f4_gpu.rs, note: GPU RREF kernel present; 426 s -> 5.7 s RTX 5090 timing quoted by the review, source not located; not ported to crypto}`. No disposition change.
- **coverage.tsv:** `IDEA-20261018-e3bcff	LEAD-ICE-boolean-f4-f5-f6-engines`

### 2.18 IDEA-20261018-e7a860 (area ICPERF, class measurement, priority high)

- **OBS (idea).** Measure K, ecbench group operations (GAE) per Macaulay column touch in the m=4 oracle; the sign of the ECC2K-130 m=4 rows (+7.6 to +10.32 bits) "flips only if log2 K < -7.6 (resp. -10.32); K above 1 widens the gap".
- **OBS (crypto).** `research/k_conversion_20261018/README.md`: K = (Ir per column touch)/(Ir per rho step) by Callgrind; "K (rho steps per column touch) is 4.0 to 15.6 with the n = 83 step (pooled m = 4 median 4.48, range 3.96 to 16.77)", 82.91 at 17,902 columns (degree 4, N=26); converted gaps +9.78 / +12.48 at the median, +9.61..+11.69 / +12.31..+14.39 across the range; "No conversion measured here brings either row below rho"; limits: n=131 rho unsupported (group order exceeds u128), degree-3 cells for the m=4 numbers, degree 4 only at N=26 (two draws). The record's K is in Ir ratio (simulated instructions), where the idea asks for GAE; the direction ("K above 1 raises the priced rows") matches the idea's stated prediction.
- **OBS (lead).** `LEAD-ICB-prime-degree-algebraic-decomposition` `evidence` already cites `research/k_conversion_20261018/README.md` and `best_measured` quotes "+9.78 at median K 4.48 [3.96, 16.77]"; its `next_action.step` still says "plus the conversion K (rho steps per column touch) on the same host" and `blocked_by` says "no 131-bit rho walk exists to measure K at n = 131 (IDEA-20261015-c6f017)".
- **`--match`.** `LEAD-ICB-prime-degree-algebraic-decomposition` 9 (phrasing 1); phrasing 2 `KR-RHO-1c2928` 13 / `LEAD-RHO-native-step-cost` 12 (the rho-step side of the conversion, a different object).
- **INT.** The idea's primary measurement is in the checkout; its flip condition (log2 K < -7.6) is not met by the recorded range (log2 K from +1.99 to +4.07). What is open per the record: K at degree 4 for N >= 34 and the n=131 wide rho step.
- **Proposed edit** to `LEAD-ICB-prime-degree-algebraic-decomposition`: `ledger_refs += IDEA-20261018-e7a860`; in `next_action.step` replace "plus the conversion K (rho steps per column touch) on the same host" with "K already measured at the n=83 step (3.96-16.77; research/k_conversion_20261018); open: K at degree 4 for N >= 34 and the n=131 wide rho step". Disposition unchanged.
- **coverage.tsv:** `IDEA-20261018-e7a860	LEAD-ICB-prime-degree-algebraic-decomposition`

## 3. Draft new lead rows (proposed; the curator decides)

### 3.1 `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-fp4-gaudry-d4-ladder.yaml`

```yaml
id: LEAD-ICP-fp4-gaudry-d4-ladder
family: ic-prime
title: Gaudry k = 4 decomposition on the E(F_{p^4}) toy ladder - D4 symmetrisation, double large primes and sparse linear algebra stacked end to end
mechanism: >-
  On E over F_{p^4} (Gaudry, n = 4) the Weil-descended decomposition with D4 symmetrisation
  is the program's proven-exponent regime. Question: do the measured stage gains (D4 constant,
  double-large-prime LA exponent, sparse LA) stack into a lower end-to-end cold S than the
  D4-only arm, and where does the fitted S cross negation rho. Toy ladder only; not a prime-order target.
disposition: open_next_step   # proposed
next_action:
  step: >-
    Run to completion the frozen research/fp4_d4_ladder_20261023 protocol (cheaper D4 solver end to
    end at p = 101, 181, 269, 397 against the ladder's ic-d4 arm and rho-neg; the b3 card receipt
    shows ecbench run stopped by signal 15 while waiting for the bench lock, no sessions in the
    checkout). Add a first-dependency-stop arm (ic_improve_20261015/04) to the same ladder; add a
    2LP or sparse-LA arm only at sizes where the measured LA share of the D4 arm is material.
  discriminates: >-
    An end-to-end S below the old C4 baseline with the interval excluding 1 is a stage improvement
    carried into S (exponent unchanged); an LA share still under 1e-7 keeps both LP and sparse-LA
    arms at the measured regression/null.
best_measured: >-
  tuned D4+2LP / D4 whole cost 1.025 [1.016, 1.037] REGRESSES, exponent difference +0.0055
  [+0.0036, +0.0078], LA phase 0.827 [0.802, 0.853] ADVANCES, D4 LA share under 1e-7, fitted handover
  at #E ~ 2^128.9 (indicative only), 24 held-out curves p = 101..1301; first-dependency stop without
  large primes (d4-ed) / d4 = 0.9792 [0.9725, 0.9855] ADVANCES (constant; exponent MATCHES), 27 held-out
  curves p = 101..1601; sparse LA arms 1.206x total (null) on E(F_{29^4}) k = 4 workloads
evidence:
  - {repo: crypto, path: research/ic_improve_20261014/01-d4-2lp/README.md, note: stacked D4 + 2LP regresses at the measured sizes; controls passed}
  - {repo: crypto, path: research/ic_improve_20261015/04-d4-2lp-fix/README.md, note: 2LP re-measured 1.0264 REGRESSES; first-dependency stop without large primes 0.9792 ADVANCES at constant level}
  - {repo: crypto, path: research/sparse_la_timing_20261018/README.md, note: four sparse relation matrices null end to end on the E(F_29^4) ladder}
  - {repo: crypto, path: research/ic_next10_20261014/01-fp4-ladder/README.md, note: ladder; D4 18.2x whole solve; plain 2LP 2.31x costlier}
  - {repo: crypto, path: research/fp4_d4_ladder_20261023/PROTOCOL.md, note: cheaper D4 solver end-to-end protocol frozen; card b3 receipt stopped at command 2, no sessions in the checkout}
  - {repo: crypto, path: benchmarks/20261014-ic-next10-01-fp4-ladder, note: ladder benchmark}
ledger_refs: [IDEA-20261018-2c37f5, GOAL-ICPERF-e6b6a4]
known_results: [KR-IC-46d822, KR-IC-a4dd54]
related: [LEAD-ICP-residual-partial-relations, LEAD-ICB-large-prime-variants, LEAD-ICB-orbit-linear-algebra, LEAD-ICP-gfp5-symmetrized-gaudry, LEAD-ICP-extension-field-embedding]
forecloses: [stack D4 symmetry with double large primes on E(F_p^4), sparse linear algebra for the E(F_p^4) ladder, Gaudry k = 4 toy ladder end to end]
areas: [ICPERF]
last_reviewed: 2026-10-24
```

### 3.2 `knowledge/leads/ecdlp/transfer/LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp.yaml`

```yaml
id: LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp
family: transfer
title: Cubic GHS transfer of E0(F_{q^3}) to a genus-3 hyperelliptic Jacobian and double-large-prime index calculus there (structured class, not prime order)
mechanism: >-
  For E0 over F_{q^3} with #E0 = 0 mod 4 and a cubic GHS cover by a genus-3 hyperelliptic curve over F_q,
  run genus-3 index calculus with double large primes (theory q^{4/3} vs rho q^{3/2}). The plane-quartic
  (Smith/Diem) branch is a separate lead.
disposition: open_next_step   # proposed
next_action:
  step: >-
    Narrow ghs3_vs_rho_20261023 where its per-size decision is "unresolved" (6 of 7 sizes) with more
    curves per size, and time a sparse-cado relation matrix inside the genus-3 pipeline once a genus-3
    curve kind exists in ecbench (or the relation-matrix registry is wired into the example); report
    LA exponent and whole-solve exponent against round 4's block Wiedemann (2,1) baseline.
  discriminates: >-
    A root of the IC/R_ideal fit with an interval inside the measured range fixes a crossover for this
    class; an interval still spanning the range leaves the comparison unresolved; a sparse arm that
    lowers the local LA exponent below q^1.52 identifies the next lever.
best_measured: >-
  IC-2LP exponent 1.300 [1.292, 1.308] (all sizes), 1.377 [1.363, 1.392] (q = 2^11..2^15); 1.62x rho model
  and 2.29x ideal negation rho at q = 2^15 (ic_next10 item 7); ghs3_vs_rho_20261023: IC/R_ideal per curve
  0.524-2.394, one of seven sizes below the strong rho, OLS slope 0.0339 [-0.0465, 0.1050] per bit
evidence:
  - {repo: crypto, path: research/ic_next10_20261014/07-cubic-ghs-genus3/README.md, note: hyperelliptic branch positive at toy scale; plane-quartic branch blocked}
  - {repo: crypto, path: research/ic_improve4_20261015/README.md, note: round 4 relation-phase tuning of the genus-3 2LP pipeline}
  - {repo: crypto, path: research/ghs3_vs_rho_20261023/TABLES.md, note: per-size decisions vs strong rho, 6 of 7 unresolved}
  - {repo: crypto, path: research/sparse_la_timing_20261018/README.md, note: genus 3 not reachable from ic.pipeline}
ledger_refs: [IDEA-20261018-670088, GOAL-ICPERF-e6b6a4]
known_results: [KR-IC-a4dd54, KR-IC-5ea2f8]
related: [LEAD-TRF-odd-char-descent-smith-quartic, LEAD-TRF-small-genus-cover-general, LEAD-ICB-orbit-linear-algebra, LEAD-ICB-large-prime-variants]
forecloses: [genus-3 index calculus after cubic GHS, double large primes on a genus-3 hyperelliptic Jacobian, sparse linear algebra for genus 3 past q = 2^23]
areas: [ICPERF]
last_reviewed: 2026-10-24
```

## 4. Proposed `coverage.tsv` lines (append, keep file sorted by id)

```
IDEA-20261018-1aff90	LEAD-ICE-descent-closure-degree-at-scale
IDEA-20261018-1bc873	LEAD-ICB-orbit-linear-algebra
IDEA-20261018-2c37f5	LEAD-ICP-fp4-gaudry-d4-ladder
IDEA-20261018-2d21b9	LEAD-EXO-ml-learned-models
IDEA-20261018-49fdf7	LEAD-ICE-generic-oracle-arity-cost-floor
IDEA-20261018-4c28fc	LEAD-ICP-retained-setup-online
IDEA-20261018-670088	LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp
IDEA-20261018-6c1c6e	LEAD-ICB-prime-degree-algebraic-decomposition
IDEA-20261018-88041d	LEAD-ICE-descent-closure-degree-at-scale
IDEA-20261018-ac3694	LEAD-ICE-charged-toy-ic-exponent-vs-rho
IDEA-20261018-b32287	LEAD-ICE-chained-semaev-dreg-vs-semiregular
IDEA-20261018-b4bc61	LEAD-ICE-hybrid-guess-determine-l7
IDEA-20261018-b90b0c	LEAD-EXO-methodology-instruments
IDEA-20261018-c0b13a	LEAD-ICE-descent-closure-degree-at-scale
IDEA-20261018-c4adb6	LEAD-ICE-linearization-excess-fb-prior
IDEA-20261018-e0857e	LEAD-ICP-digit-presentation-solving-degree
IDEA-20261018-e3bcff	LEAD-ICE-boolean-f4-f5-f6-engines
IDEA-20261018-e7a860	LEAD-ICB-prime-degree-algebraic-decomposition
```

(In the current `coverage.tsv` the existing `IDEA-20261018-*` lines are at lines 2713-2727 with other suffixes; the 18 above interleave by id.) The two new ids must exist as lead files before `--check` passes.

## 5. Cross-cutting observations (for the curator)

1. **Stale or contradicted idea premises (OBS, with the record that contradicts):**
   - 2c37f5 "stacked D4+2LP never run" vs `crypto:research/ic_improve_20261014/01-d4-2lp/README.md` (REGRESSES) and `ic_improve_20261015/04-d4-2lp-fix/README.md` (re-measured; no-large-prime variant ADVANCES at the constant level).
   - 88041d "(4,6) is the missing memory-bound cell" vs `crypto:research/dreg_closure_m4l6_20261018/RESULTS.md` (A1 refuted at degree 4).
   - e7a860 "K is unmeasured" vs `crypto:research/k_conversion_20261018/README.md` (K = 3.96-16.77).
   - 1bc873 "sparse engine unreachable from ic.pipeline" vs review corrections (PR #1874, #2162) and `sparse_la_timing_20261018`, `ic_linalg_pipeline_20261019`.
   - b90b0c (b) "48 mismatches unexplained" vs `item1_cross_isa_20261020/RESULT.md` (cause isolated); (a) "no audit" vs approved EXP-DTREE-b93a15 and EXP-SEMAEV-93d5cc (trials 1-6 output_validated per DEC-20261019-5b9240; outcomes not read here).
   - b4bc61 "crossbred only at m=2" vs `e2e_panel.txt` (also m=3, n=9); 670088 "sparse LA missing from the genus-3 pipeline" vs `ghs3_vs_rho_20261023/PROTOCOL.md` (baseline includes block Wiedemann (2,1)).
   - 6c1c6e "Faugere-Svartz never run" vs `LEAD-ICB-frobenius-search-symmetry` measured equivariant pass (different symmetry group: Frobenius vs 2-torsion).
2. **Crypto records read here that no lead cites** (the curator may want rows or evidence entries; they are not in this group's delta): `ic_improve_20261014/01-d4-2lp`, `ic_improve_20261015/04-d4-2lp-fix`, `sparse_la_timing_20261018`, `ic_linalg_pipeline_20261019` (the benchmark dir is cited, not the research dir), `equal_advice_wide_20261018`, `ghs3_vs_rho_20261023`, `ic_next10_20261014/07-cubic-ghs-genus3`, `ic_improve4_20261015`, `fp4_d4_ladder_20261023`, `pkm_m3_n21_msolve_20261018`, `pkm_lead1_m3n21_20261016`, `large_memory_runs_20261018`, `ic_next10_20261014/03-pkm-degree`, `fall_degree_bounds_20261008`, `pdp_literature_leads_20261022`.
3. **Coverage gaps.** `coverage.tsv` has no row for `H-DTREE-001`, `H-STR-002`, `H-IC-001`, `H-DTREE-8636a3` and `--coverage` does not list them; they appear to be classified non-ECDLP by the tool although `H-DTREE-001` and `H-DTREE-8636a3` carry question `RQ-ECDLP-002` and index-calculus mechanism text. The `PKM` mechanism has no lead text of its own (only a coverage mapping through H-ECDLP-60de36).
4. **Two lead-text statements that look out of date against the checkout** (conditional): `LEAD-ICB-prime-degree-algebraic-decomposition.next_action` (K as to-do; "(4,6)... exceeded the 3 GB cap"); `LEAD-ICE-hybrid-guess-determine-l7` has `known_results: None` while its mechanism cites crossbred (KR-IC-e847d1).
5. **Match quality.** Criterion used: the chosen lead was not the highest-scoring `LEAD-` row (KR rows ignored) in either of the two phrasings of Appendix A. By that criterion 6 of the 16 records with an existing chosen lead missed by rank: 1aff90, 2d21b9, 4c28fc, ac3694, b32287, b90b0c (for 4c28fc the chosen lead was fifth in phrasing 2; for ac3694 fifth in phrasing 1 and absent in phrasing 2; for 2d21b9 second in phrasing 2; for 1aff90, b32287 and b90b0c it is absent from both top-5 lists). For the two new-mechanism records (2c37f5, 670088) no existing lead was chosen. The mechanism lead was found by reading lead texts or by id grep, not by rank, so `--match` should be read alongside the row text.

## Appendix A. Raw `lead_atlas.py --match` top-5 hits, two phrasings per record

Command per line: `LEAD_ATLAS_CRYPTO=... LEAD_ATLAS_CRYPTANALYSIS=... LEAD_ATLAS_ECC_CHALLENGES=... python3 tools/lead_atlas.py --match "<phrase>" --limit 5` from `/Volumes/SSD990-2/crypto-autoresearcher`. Columns: token-overlap score, id, disposition (or `known_result`), title (truncated by the tool). Verbatim output, headers added.

```text
### 1aff90 phrasing1: GF(2) block Wiedemann Coppersmith consistency test Macaulay matrix memory-light XL degree bound
   15  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   10  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    7  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    7  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
### 1aff90 phrasing2: sparse Krylov linear algebra over GF(2) dense memory 70 GB degree cell
   16  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   12  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    6  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    6  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
### 1bc873 phrasing1: block Wiedemann Lanczos filtering ic.pipeline relation matrix density weight post-filter dimension
   25  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   15  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    7  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    6  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
### 1bc873 phrasing2: sparse linear algebra engine unreachable structured Gauss crossover measured relation matrix
   28  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   11  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
### 2c37f5 phrasing1: stacked D4 symmetry double large primes E(F_p^4) end to end
    9  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    9  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    8  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
### 2c37f5 phrasing2: double large prime relation phase 2LP crossover extension field p^4 symmetry stacking
   14  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
   13  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
   12  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
### 2d21b9 phrasing1: learned Groebner monomial ordering HATSolver Semaev PKM systems msolve F4
   14  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   12  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
   11  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
   10  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
### 2d21b9 phrasing2: machine learning variable ordering Groebner basis counted cost held-out cells
   12  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
   10  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
   10  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
### 49fdf7 phrasing1: structured GGM non-adaptive time-space bound pair-table k-sum Dinur Keller Marmor
    6  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    5  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    5  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
    4  LEAD-ICB-koblitz-setup-phase-cost            open_next_step     Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sits
    4  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
### 49fdf7 phrasing2: generic group model lower bound index calculus decomposition probability sqrt advice
   16  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   16  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
   16  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   14  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
### 4c28fc phrasing1: Bernstein-Lange preprocessing rho equal advice index calculus co-measured n=73 n=83
   16  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   12  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   12  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
### 4c28fc phrasing2: preprocessing rho vs compact-orbit IC online time S T^2 equal advice
   13  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
   11  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
   11  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   10  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
### 670088 phrasing1: genus-3 cubic GHS sparse linear algebra double large prime q^1.52
   16  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   14  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
   13  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   11  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   10  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
### 670088 phrasing2: genus 3 whole-solve exponent 4/3 memory block ladder block Wiedemann filtering
   13  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   10  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    8  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
    6  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    6  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
### 6c1c6e phrasing1: FGHR 2-torsion symmetrisation Faugere-Svartz character blocks Weil descent m=4 system
   12  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   12  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   12  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   10  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   10  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
### 6c1c6e phrasing2: equivariant F4 symmetrised Groebner ECC2K-130 descent degree 5 optimistic row
   14  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   14  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
   13  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   12  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   11  KR-IC-0d2021                                 known_result       Modern Gröbner-basis complexity refinements
### 88041d phrasing1: large-memory run Weil descent degree cells (4,6) solving degree Semaev system ECC2K-130
   25  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   24  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   23  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   19  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   18  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
### 88041d phrasing2: MutantXL closure degree follows l slope cells m=3 l=8 m=4 l=7 70 GB
   15  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   13  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
   10  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    8  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
### ac3694 phrasing1: non-enumerative membership oracle EXP-ICEX-153c34 enumerative membership bottleneck
    6  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    6  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    6  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    5  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
### ac3694 phrasing2: membership oracle backend instrumented counters admission driver non-frozen smoke curves
    6  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    6  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    6  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    4  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
### b32287 phrasing1: DREG C1 ECTD arity-3 panel H-STR-002 H-DTREE-001 infrastructure gaps failed_infrastructure
    3  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    3  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    1  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    1  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
### b32287 phrasing2: common phi shift no-append ablation missing artifacts infeasible design inconclusive
    4  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm
    4  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    3  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    3  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply
    2  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
### b4bc61 phrasing1: Crossbred Weil-descended Semaev PDP cells F4 WDSat
   11  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
   11  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    9  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    9  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    8  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
### b4bc61 phrasing2: Joux-Vitse crossbred overdetermined Boolean systems improved preprocessing descent cells
   24  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
   14  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
   11  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    9  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    8  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
### b90b0c phrasing1: s4_expr bug audit inherited F4 replay mismatches host-dependent counted cost
   11  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    9  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    6  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
### b90b0c phrasing2: semaev.py s4_expr whole-curve factor-base sampling archived runs rerun fixed code
    7  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    7  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    6  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
### c0b13a phrasing1: last fall degree order-independent refutation instrument degree cells
   18  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   14  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   14  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   12  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   10  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
### c0b13a phrasing2: Huang Kosters Yang Yeo last fall degree bound solving degree dense closure
   28  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   19  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   16  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   15  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
### c4adb6 phrasing1: fitted degree rule geometric-progression bases factor-base prior fb-search
   11  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    8  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    7  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
### c4adb6 phrasing2: learned predictor solving degree from factor base prunes search M7 M9 null
   15  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   15  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   15  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   14  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
   13  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
### e0857e phrasing1: PKM tower degree m=3 N=21 N=24 m=4 N=24 msolve prime-field line plateau
   11  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   11  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    7  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    7  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
### e0857e phrasing2: polynomial system degree one per eight unknowns no plateau prime-field exponent 256 GB host
   15  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   13  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   11  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   10  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
### e3bcff phrasing1: port f4_gf2 f4_gpu cryptanalysis into crypto GPU device Boolean F4
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    7  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
    7  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
    6  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
### e3bcff phrasing2: GF(2) elimination RREF gf2_elim device 25-75x RTX 5090 degree-6 matrices
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    4  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    3  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    3  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    2  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
### e7a860 phrasing1: K column touch to group operation conversion m=4 oracle ECC2K-130 rows
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    7  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    7  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    7  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    6  KR-RHO-18cc42                                known_result       ECC2K-130: expected work and 2009–2010 implementation rates
### e7a860 phrasing2: Macaulay column touch GAE conversion field multiplications instrumented counters rho constant
   13  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   12  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    9  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    9  KR-RHO-cd86f5                                known_result       r-adding walks and the walk constant
    9  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
```

## Appendix B. Extra `--match` queries (PKM tower, cubic-GHS genus 3, E(F_p^4) ladder, harness audit)

Run to settle the lead choice for e0857e, 670088, 2c37f5 and b90b0c; same command and columns.

```text
### e0857e extra1: PKM Kummer tower msolve degree plateau prime field Petit Kosters Messeng
   14  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   11  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   10  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    9  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
### e0857e extra2: Kummer tower prime field tower of extensions degree growth
   12  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   11  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   10  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    9  KR-IC-49c882                                 known_result       Quasi-subfield polynomials
### 670088 extra1: cubic GHS genus 3 hyperelliptic double large prime Jacobian index calculus q^1.3
   34  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   19  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
   18  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
   17  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   17  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
### 670088 extra2: E(F_{q^3}) cubic GHS cover genus-3 hyperelliptic relation collection rho crossover
   16  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   11  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
   10  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
   10  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    9  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
### 2c37f5 extra1: Gaudry E(F_{p^4}) k=4 ladder D4 symmetry quartic decomposition
   12  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
   12  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   10  LEAD-ICP-gfp5-symmetrized-gaudry             open_next_step     Symmetrization-aware Gaudry/Diem decomposition on EcGFp5/EcMasFp5 (n = 5) using rational 2-torsion ((Z/2)^4 x| S_5) and side dichotomy
   10  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    9  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
### 2c37f5 extra2: extension field F_{p^4} Gaudry decomposition toy ladder cost per decomposition
   15  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
   13  KR-IC-081a58                                 known_result       Joux–Vitse n−1 decomposition and oracle-assisted static DH
   11  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
   11  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
### b90b0c extra1: harness bug audit archived runs superseding repair evidence integrity
    5  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    3  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    3  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
    1  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    1  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
### b90b0c extra2: replay mismatch inherited F4 BMI2 host dependent counted cost
    9  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    6  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    6  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
```

---

## Group: car-proposals-b

# Lead-atlas fold: group car-proposals-b (proposed diffs only)

Reviewer: lead-atlas "changed since review", step 2. Repository root of the paths: `/Volumes/SSD990-2/crypto-autoresearcher`.
Delta list read from `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/delta.txt` lines 110-128: 19 paths, 10 records
(`IDEA-20261022-{727676,727d2e,e5b3a4}`, `IDEA-20261023-f15270`, `IDEA-20261024-{3c71a9,5f08bd,7be1c6,a29e53,b58e07,d84f20}`; nine have a `.notes.md`, f15270 has none).

Nothing in this file edits a row. Every "proposed edit" is text for the atlas owner to apply or reject. No hypothesis, experiment or goal status change is proposed.
Labels: **Obs** = read in a file this session (path given); **Interp** = reading of the observation, conditional.

## 1. Result in brief

| item | count / value |
|:--|:--|
| paths folded | 19 (10 `.yaml`, 9 `.notes.md`) |
| records that are ECDLP-lane (question/goal/frontier map ECDLP) | 10 of 10; one of them (727d2e) states in its own text "NOT ECDLP" |
| `advances_lead` | 3 records (5 paths): 727d2e, e5b3a4, f15270 (+ their notes) |
| `new_mechanism` | 7 records (14 paths): 727676 (proposed new lead N1) and six PEXT ideas (proposed new lead N2) |
| `decides_lead` | 0 (no record in this group is a decision record that closes or reopens a lead's deciding hypothesis) |
| `not_ecdlp` (coverage `NONE`) | 0 |
| disposition changes proposed | 0 |
| records carrying `prior_art.lead` | 0 of 10 (grep of every `.yaml` for `lead:` / `new_lead_reason:` under `prior_art` is empty; expected, rule 4 starts at IDEA-20261025) |
| all 10 records in `coverage.tsv` | no (all 10 are in `/private/tmp/.../atlas/coverage.txt` as unmapped; `grep` of `knowledge/leads/ecdlp/coverage.tsv` finds none) |

### Two coverage gaps this group exposes (observations first)

**N1. The PKM tower oracle line has no lead row.**
- Obs: `grep -rn -i "pkm|prime_tower|prime-kummer|prime-isogeny|factor-base-encyclopedia|Amadori|Messeng|ic_framework|f4_fp_tower|pkm_tower" knowledge/leads/ecdlp/*/*.yaml` returns nothing.
- Obs: the crypto clone holds 14 directories `research/pkm_*` (dickson_torus, isogeny_tower_ecbench, isogeny_tower_p192, lead1_m3n21, m3_n21_msolve, supersingular_aux, tower_ecbench, tower_pilot, tower_round2 to round7) and `research/notes/index-calculus/RESEARCH_PKM_TOWER_ORACLE.md`; the engine is `src/cryptanalysis/f4_fp_tower.rs`.
- Obs: in the ledger the line appears as H-ECDLP-60de36 (coverage.tsv maps it to LEAD-ICP-digit-presentation-solving-degree), IDEA-20261009-f24f8a (same lead), IDEA-20261018-e0857e and IDEA-20261018-2d21b9 (unmapped in coverage.txt; outside this group's path list), EXP-ECDLP-f49f75, EXP-ECDLP-20a588, and this group's IDEA-20261022-727676 (unmapped).
- Interp: it is the program's only prime-field algebraic decomposition-oracle line (RESEARCH_PKM_TOWER_ORACLE.md section 0 calls PKM "the one algebraic mechanism for prime-field curves") and it is the line closest to the user's stated focus. Proposed: one new row N1, section 5.

**N2. Prime-degree extension descent (GOAL-PEXT-4a1d6b) has no lead row.**
- Obs: GOAL-PEXT-4a1d6b and RQ-PEXT-7c3e91 were opened 2026-10-24 (DEC-20261024-e29f4c, `kind: goal_opening`); EXP-PEXT-212d5c is approved (DEC-20261024-992998) and `experiments/EXP-PEXT-212d5c/runs/` holds only `.gitkeep`, so there are no results.
- Obs: DEC-20261024-e29f4c context says "no existing goal owns it" and lists the n=3 and n=5 results as living in the sibling repository (`research/ghs_cubic_cover_census_20261012`, `research/ghs_cover_census_n5_20261013`); no lead row cites either directory (grep empty).
- Obs: the nearest closed row, LEAD-TRF-small-genus-cover-general, is `closed_obstructed` with scope "Kummer/GHS covers of the x-line in odd characteristic" (F_{q^3}; k = 6, 10, 14). The PEXT work is open and has an approved experiment.
- Interp: filing open PEXT work under a closed row would contradict that row's disposition, and no deciding record exists to reopen it. Proposed: one new open row N2 that lists the closed row in `related`, section 5. Relevance caveat: the PEXT line studies E over F_{q^n} (n prime), states "no attack, no speedup, no cost" in its goal claim_boundary, and does not touch prime-field E(F_p).

## 2. Table (one row per path)

Columns: ECDLP? = lane test; action in {advances_lead, new_mechanism}. `(new)` = lead proposed in section 5.

| # | path | ECDLP? | action | lead | reasoning | proposed row edit |
|--:|:--|:--|:--|:--|:--|:--|
| 1 | ledger/proposals/IDEA-20261022-727676.yaml | yes (RQ-ECDLP-002, GOAL-ECDLP-001, frontier_map ecdlp) | new_mechanism | (new) LEAD-ICP-pkm-tower-algebraic-oracle | **Obs:** status proposed, class measurement, header "Nothing here is [measured]". Proposes adding per-step digests and a multiply-add split by row outcome to `StepTrace` of `f4_fp_tower`, then running m=3 N=15, m=3 N=18, m=4 N=12 (two committed targets each) to report Z (multiply-adds on rows that reduce to zero), U_time (symbolic-preprocessing share) and the Amdahl bound 1/(1-U); owner prediction Z < 0.05, "falsified at >= 0.25"; optional arm B seeds F4 with the target-independent chain links. Its prior_art lists KR-IC-f3da82 as `special_case` ("replay known") and says no exponent moves. No `prior_art.lead`. 5 `--match` phrasings (hits in section 7): top lead hits LEAD-ICE-boolean-f4-f5-f6-engines (8, closed_dominated), LEAD-ICE-prime-field-semaev-solving-degree (5, closed_known), and with tower wording LEAD-ICP-algebraic-membership-factor-base (29, closed_obstructed). **Interp:** the replay lever is a constant-factor item on an engine no lead describes. The Boolean row's scope is binary Weil-descended S_3, n <= 31, with "learn/apply trace reuse"; the prime-field solving-degree row's scope is interval/random/subgroup bases (EV-SDEG-4a1c3d). Neither records a tower presentation. Conditional: if the reviewer reads the theorem of LEAD-ICP-algebraic-membership-factor-base (size-B algebraic base needs description degree >= B/3) as covering a lifted tower presentation (one auxiliary variable per level, RESEARCH_PKM_TOWER_ORACLE.md section 0), the PKM material is evidence for that row instead; the row text names neither tower nor auxiliary variables, so the scope question is open. | Add new row N1 (section 5). Coverage line: `IDEA-20261022-727676<TAB>LEAD-ICP-pkm-tower-algebraic-oracle`. |
| 2 | ledger/proposals/IDEA-20261022-727676.notes.md | yes | new_mechanism | (new) LEAD-ICP-pkm-tower-algebraic-oracle | **Obs:** notes section 1 reports two places where the brief and the repo disagree. (i) For `f4_fp` (not `f4_fp_tower`) `docs/ic/GROEBNER_F4F5F6_AUDIT_20261010.md` lines 264-268 say symbolic preprocessing and sparse pair-row reduction are the larger part and dense residue elimination "a small share" (text checked in the crypto clone); so the symbolic share in `f4_fp_tower` is unmeasured and the draft gives no point prediction for U_time. (ii) RESEARCH_PKM_TOWER_ORACLE.md section 11 already records identical D, width and step count across targets, so structure identity is a precondition for replay, not a payoff. Section 6 arm B borrows a reuse ceiling from IDEA-20260829-fa8235 and says "NOT checked for F4 over R". Section 9: no code run, nothing measured. **Interp:** same classification as row 1; the notes add scope limits, not evidence. | none beyond row 1 |
| 3 | ledger/proposals/IDEA-20261022-727d2e.yaml | yes by lane (RQ-ECDLP-002, GOAL-ECDLP-001); the record says "NOT ECDLP" | advances_lead | LEAD-STR-curve-generation-provenance-seeds | **Obs:** proposes a calibrated census of radix (class E) and lattice (class L) representations of p, r, p-1, p+1, t for deployed curves, with analytic and sampled nulls, planted FGHT-style controls and a power curve over g1 bits; positive controls Curve25519, Ed448, P-192, P-521, BN, BLS12-381. Text: "Audits companion F_p^* and F_{p^2}^* DLP risk and hidden-structure detection, NOT ECDLP", and "Not ECDLP ... cannot move the baseline"; `sota_delta: none`. Lineage `extends: IDEA-20261009-2abd32` (coverage.tsv maps 2abd32 to LEAD-TRF-mov-small-embedding-degree). Notes section 2 names `research/nist_trapdoor_slot_program_20261011` (slot S2, the prime) as the covered neighbour; that directory and `research/safecurves_trapdoor_slots_20261017` exist in the crypto clone and no lead row cites either (grep empty). 2 `--match` phrasings: top hits LEAD-RHO-cheon-deployed-applicability (10), LEAD-ICB-quasi-subfield-polynomials (9), LEAD-ICP-construction-normal-form (9); none is a prime-structure screen. **Interp:** the nearest row by mechanism is the hidden-weak-class / provenance screen family: LEAD-STR-curve-generation-provenance-seeds lists the public screens run so far (CM field, class number, conductor, embedding degree, twist factors, odd isogenies <= 10,000, ANSI gates, 21 features) and none screens p, r, p+-1 for a polynomial form. Its `revisit_when` ("a new publicly testable weak class of density at least 2^-30 is named") is not met by this record, which names no class. If the reviewer reads the self-declared "NOT ECDLP" strictly, the alternative is coverage `NONE`; the lineage alternative is LEAD-TRF-mov-small-embedding-degree (2abd32's row). | `LEAD-STR-curve-generation-provenance-seeds`: add `IDEA-20261022-727d2e` to `ledger_refs`; add evidence `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261022-727d2e.yaml, note: "proposed integer-structure census of deployed p, r, p+-1, t with planted controls and detectability edge; self-declared not ECDLP; zero runs"}`; add evidence `{repo: crypto, path: research/nist_trapdoor_slot_program_20261011/README.md, note: "slot S2 (the prime) pending matched-rho only; the idea fills the polynomial-form gap"}`. No disposition, obstruction or best_measured change. Coverage line `IDEA-20261022-727d2e<TAB>LEAD-STR-curve-generation-provenance-seeds`. |
| 4 | ledger/proposals/IDEA-20261022-727d2e.notes.md | yes by lane | advances_lead | LEAD-STR-curve-generation-provenance-seeds | **Obs:** notes section 2 reads four neighbours: SNFS-B4 limb (b) (one prime, Murphy-E vs CADO), the slot program's census.md (executed) and PROTOCOL section 8 (S2: only E2, matched rho, pending), `p192_cm_norm_sieve.rs` (norms in Z[pi], another object), `fght_snfs.rs` (degree 2 only, bits <= 64, degree 3 returns false). Section 1 says the brief's paths live in the crypto repo, not in crypto-autoresearcher. Sections 3-4 give the two classes and note the FGHT hidden prime is `p = Res(f, g1*x - g0)` with g1 > 1, so class E sees only g1 = 1. No [measured] value. **Interp:** same as row 3; the notes support the claim that the S2 gap is polynomial form of p, not a rho control. | none beyond row 3 |
| 5 | ledger/proposals/IDEA-20261022-e5b3a4.yaml | yes (RQ-ECDLP-002, GOAL-ECDLP-001) | advances_lead | LEAD-TRF-pairing-target-field-recost (also ledger_refs on LEAD-TRF-mov-small-embedding-degree) | **Obs:** proposes a table of model-priced rows for MOV/Frey-Rueck transfer followed by (S)exTNFS for BN-254, BN-462, BLS12-381, BLS12-446, KSS16, KSS18, BLS24 beside matched rho under AGENTS.md 5a (w in {0, 0.1, 1} GAE per unpriced operation), a refusal rule for undefined rows (k > k_cap), and k* from primary tables; predictions: BN-254 transfer < rho, BLS12-381 within 2^+-4 of rho, P-256/secp256k1 refused. `extends: IDEA-20261009-2abd32`, `also_extends: EXP-ECDLP-6dacdb deployed-table.md`; `related_not_superseded` includes IDEA-20260815-bf1328 and IDEA-20260815-0676d4, which coverage.tsv maps to LEAD-TRF-pairing-target-field-recost. Memory uncharged in the models. No run. 2 `--match` phrasings: top hits LEAD-TRF-mov-small-embedding-degree (29, 23), LEAD-TRF-prime-field-isogeny-to-weak (20), LEAD-TRF-pairing-target-field-recost (10). **Interp:** the record prices the same post-MOV target-field cost the recost row targets, from published models rather than a charged run; the recost row's `best_measured` is "none: 33 EXP-PAIR contracts, zero runs" and this adds a proposal, not a measurement. The MOV row (closed_known) is unaffected: its obstruction already says the target-field cost is a separate lead. | `LEAD-TRF-pairing-target-field-recost`: add `IDEA-20261022-e5b3a4` to `ledger_refs`; add evidence `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261022-e5b3a4.yaml, note: "proposed model-priced BN/BLS/KSS rows beside matched rho in the 5a band; refusal rule for k > k_cap; memory uncharged; zero runs"}`. `LEAD-TRF-mov-small-embedding-degree`: add `IDEA-20261022-e5b3a4` to `ledger_refs` only. `best_measured` stays "none". Coverage line `IDEA-20261022-e5b3a4<TAB>LEAD-TRF-pairing-target-field-recost`. |
| 6 | ledger/proposals/IDEA-20261022-e5b3a4.notes.md | yes | advances_lead | LEAD-TRF-pairing-target-field-recost | **Obs:** notes section 4 argues S_T(w)/S_rho(w) = (C/N) w/(1 + w c_native) increases in w, so "transfer < rho" is the only rankable outcome and everything else is "unresolved". Section 3 gives matched rho 2^125.5 (BN-254) and 2^125.95 (BLS12-381) and a rough consistency check against KN-LIT-24b9c7 / KR-RHO-825bca. Section 1: supersession of B4 is left to the Coordinator; B4 limb (b) not carried. Sections not read are listed as "Not read" (Equation [2], kappa/A/B meaning, operation unit). **Interp:** the unit of a model operation is unread, so the w = 1 conservatism (H3) is unverified; this is the record's own stated risk. | none beyond row 5 |
| 7 | ledger/proposals/IDEA-20261023-f15270.yaml | yes (RQ-MONO-001, GOAL-PATH-001, frontier_map ecdlp) | advances_lead | LEAD-ICE-semaev-cover-monodromy | **Obs:** `supersedes_by_reference: IDEA-20260803-ff7415` (coverage.tsv maps ff7415 to LEAD-ICE-semaev-cover-monodromy); routed by DEC-20261023-19c53b (ff7415 to be designed only through f15270 once the snapshot archive verifies). Zero runs, no code. Claim [D, derived, "NOT independently re-derived"]: reading Y (relation rate beyond 1/n!) is false for every n >= 2, B and finite abelian group because rate = coverage <= min(1, C(B+n-1,n)/N); the 2^(n-1) appears only in universe-size bookkeeping that cancels, and as the ratio between the exact count and a Chebotarev quasirandom proxy (G = (Z/2)^{m-2} regular). Reading C (cost) "is not decided by this record". Anchors KN-OPEN-62c870 Q3, KN-FIND-007, KN-FIND-4f0d84, KN-FIND-bdcd60; derivations in `docs/reports/2026-10-23-idea-f15270-rescope/report.md`. The lead's `revisit_when` names "a factor-base statistic answering KN-OPEN-62c870 Q1/Q3". 2 `--match` phrasings: top lead hits LEAD-ICP-gfp5-oa-sdhp-jv (11), LEAD-ICE-semaev-yield-model-coset-typing (10), LEAD-ICE-semaev-cover-monodromy (15, second phrasing). **Interp:** the record is a proposal toward Q3, not a decision; if its derivation survives review it would be evidence for the lead's closure at F_{q^n}, but nothing here moves the lead from `closed_obstructed`. The lead's obstruction is stated for E/F_p, p > 3; this record extends the scope to F_{q^n}. Statement (1) is field-independent and so also bears on prime-field relation-rate claims. | `LEAD-ICE-semaev-cover-monodromy`: add to `ledger_refs` `IDEA-20261023-f15270`, `IDEA-20260803-ff7415`, `DEC-20261023-19c53b`; add evidence `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261023-f15270.yaml, note: "derivation-first re-scope onto KN-OPEN-62c870 Q3: the 2^(n-1) clause derived (not measured) to be bookkeeping / proxy, not a yield lever; scope F_{q^n}; zero runs"}`. Optionally `LEAD-ICE-semaev-yield-model-coset-typing`: add `IDEA-20261023-f15270` to `ledger_refs` (KN-FIND-007 conservation is evidence there too). No disposition change. Coverage line `IDEA-20261023-f15270<TAB>LEAD-ICE-semaev-cover-monodromy`. |
| 8 | ledger/proposals/IDEA-20261024-3c71a9.yaml | yes by lane (RQ-PEXT-7c3e91, GOAL-PEXT-4a1d6b; frontier_map ecdlp) | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** claim "derived after reading the sibling q = 3 data; the q = 1 mod 4 branch and n = 7 are out-of-sample": at n = 5, \|E(K)[4]\| = 8 on every genus-5 curve at q = 3 mod 4, and 4 on exactly one twist of each pair at q = 1 mod 4. The sibling README (`research/ghs_cover_census_n5_20261013/README.md`, read) records genus 5 only with #E(K)[4] = 8 (20 of 60, 0 of 21) at q = 3, and "for reasons the census does not explain" for class minima by v_2. Prediction panels and a falsifier are written (a genus-5 curve at q = 3 mod 4 with \|E(K)[4]\| != 8). Nearest rows cited: KR-IC-5ea2f8 (adjacent), KN-LIT-bf1772 (abstract only). No `prior_art.lead`. 2 `--match`: top hits LEAD-TRF-odd-char-descent-smith-quartic (24, 10), LEAD-TRF-ghs-binary-composite (18), LEAD-TRF-small-genus-cover-general (11). **Interp:** the best hit's mechanism is descent onto genus 3 then Smith's isogeny and Diem q^{4/3}; this record is about which curves can sit on a genus-n floor family at prime n, with no cost and no genus <= 3 target. LEAD-TRF-small-genus-cover-general is closed on F_{q^3} and k = 6, 10, 14 and cites no 2-adic or norm-character statement. | Contributes to new row N2 (section 5); `ledger_refs` += `IDEA-20261024-3c71a9`. Coverage line `IDEA-20261024-3c71a9<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 9 | ledger/proposals/IDEA-20261024-3c71a9.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** hand derivation (label "not evidence"): squares in K are norms; N(sigma^i x - sigma^k x) = c_{k-i}, c_{-j} = -c_j; the three resolvent differences give a table by (eps, u, s) with \|E(K)[4]\| in {4, 8, 16}; the kappa constant between Jacobian roots and c*theta_i is "recalled, to be fixed at design". The q = 3 consistency check is a necessary-condition match, stated as "not a test". **Interp:** the one external dependency (kappa) is unverified, so the table's twist orientation is open until design. | none beyond row 8 |
| 10 | ledger/proposals/IDEA-20261024-5f08bd.yaml | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** claim: single-orbit floor 2^(n-3-e(n))(n-4) + 1 for prime n >= 5, with e(n) the largest number of nontrivial n-th roots of unity killed by one weight-4 polynomial; Newton lemma in characteristic 2 (p_1 = p_3 = 0 forces a repeated root) gives e(n) = 0 whenever 3 lies in <2> mod n; predictions e(5) = e(11) = e(13) = e(19) = ... = 0, e(7) = 3, e(31) = 5 (stated as conjecture); Hess genus 2^t - 2^(t-s1) - 2^(t-s2) + 1 equals n at Mersenne primes n = 2^t - 1, whereas the odd floor at n = 31 is about 2^23 * 27. It cites `odd_char_descent_genus3_20261014/REPORT.md` (minimum genus 5, 7, 1793, 9217 at n = 5, 7, 11, 13) and KN-LIT-f64d86; its prior_art cites KR-IC-791cb7 as adjacent. Notes say the weight-4 generator is "absent in Artin-Schreier form"; whether a Hess family at n = 31 has useful density "is not claimed". 2 `--match`: top hits LEAD-TRF-same-field-genus-g-embedding (13), LEAD-TRF-odd-char-descent-smith-quartic (15), KR-IC-791cb7 (15). **Interp:** the char-2 contrast touches LEAD-TRF-small-genus-cover-general's `revisit_when` branch "Hess Artin-Schreier analogue ... in odd characteristic" only as a derivation about why the Kummer compositum cannot reproduce it; it constructs nothing. | Contributes to N2; `ledger_refs` += `IDEA-20261024-5f08bd`. Coverage line `IDEA-20261024-5f08bd<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 11 | ledger/proposals/IDEA-20261024-5f08bd.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** notes derive g = 2^(m-2)(n-4) + 1 with m = n - 1 - \|Z(S)\|; baseline checks n = 5 (g = 5), 7 (S = {0,2,3,4}, g = 7), 11 (1793), 13 (9217) against the sibling table; e(n) > 0 iff four distinct elements of mu_n sum to 0 in F_{2^o}; Poisson-mean estimates for n = 17, 23, 31, 47, 73 are flagged "estimates; the exhaustive table decides". Lean `decide` on submodule dimensions of F_2[x]/(x^7 - 1) planned (dimensions 7, 6, 4, 4, 3, 3, 1, 0). **Interp:** n = 31 and n = 73 statements are expectations, not derived results. | none beyond row 10 |
| 12 | ledger/proposals/IDEA-20261024-7be1c6.yaml | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** claim (a) exact: classes with E(K)[2] = (Z/2)^2 number N_split(t) = sum over orders O containing Z[(pi-1)/2] of h(O), positive iff 4 divides #E, and these are the non-floor vertices of the K-rational 2-isogeny volcanoes; (b) heuristic: hits per class ~ lambda_n q^(n/2 - 3), falling like q^(-1/2) at n = 5 and tending to 1 at n = 7; (c) competing shape-bias explanation tied to 3c71a9. Sibling README (read, lines 174-176 and ~196) gives class minima by v_2 at q = 3 taking the values 5, 17, 25, 33, 97, and none of 9 sampled split curves (31 models) reaching genus 5 at q = 5. Citations Schoof, Kohel, Sutherland, Jao-Miller-Venkatesan are `recalled`. Notes: "Not done here: the walk ... No cost is claimed." 2 `--match`: top hits KR-IC-791cb7 (22), LEAD-TRF-jv-sieve-fp6-weak-class (19, 18), LEAD-ICP-gfp5-odd-char-cover (18). **Interp:** LEAD-TRF-jv-sieve-fp6-weak-class carries "the isogeny walk into the class" for the genus-3 weak class on F_{p^6}; this record counts reachability of a genus-n floor curve inside a class at prime n and prices nothing. Same family, different object; listed in N2's `related`. | Contributes to N2; `ledger_refs` += `IDEA-20261024-7be1c6`. Coverage line `IDEA-20261024-7be1c6<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 13 | ledger/proposals/IDEA-20261024-7be1c6.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** notes section (a) argues E(K)[2] = E[2] iff (pi-1)/2 is an endomorphism, so 4 divides #E(K) and the depth of the 2-volcano is at least 1 ("to be checked at design"); section (b) estimates hits per class 4.5 / 3.8 / 3.0 / 2.8 at q = 5 / 7 / 11 / 13 as "rough" and reports 1.3 per class at q = 3 (15 classes with 4 dividing #E, 20 genus-5 curves); section (c) restates the v_2 = 2 contrast. **Interp:** the q = 3 figure is below the fitted-constant range, which the notes use to justify fitting lambda_n on q >= 5. | none beyond row 12 |
| 14 | ledger/proposals/IDEA-20261024-a29e53.yaml | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor; related LEAD-ICB-ecc2k130-jacobian-carrier | **Obs:** claim: Jac(C) for a genus-n curve C/F_q is isogenous to W = Res E iff N_i(C) = q^i + 1 for i < n and N_n = Q + 1 - n t (Tate); at n = 3 Torelli plus Serre's twist gives, for every t with T^6 - tT^3 + Q irreducible, a genus-3 curve in the class of t or -t, so classes with #E(K) odd or 2 mod 4 (GHS cover floors 13 / 5) would still hold genus-3 Jacobians; "existence is not descent" (an explicit isogeny of controlled degree is needed; Tian 2023, KN-LIT-b4a89c, abstract only). Naive-independence density e(n) = (-n^2 + 11n - 12)/4 gives 1.5, 3, 4.5, 4, -3 at n = 2, 3, 5, 7, 11. Notes: for n = 5 "the exponent is stated and not tested". 2 `--match`: top hits KR-IC-791cb7 (18, 21), LEAD-TRF-ghs-binary-composite (18), LEAD-TRF-odd-char-descent-smith-quartic (16), LEAD-ICB-ecc2k130-jacobian-carrier (15). **Interp:** LEAD-ICB-ecc2k130-jacobian-carrier states the same object in characteristic 2 (a Jacobian isogenous to the Weil-restriction factor, Torelli rarity heuristic, n = 5 and 7 toy ladder); this record adds the full-W form at odd q and a closed-form density exponent. If the n = 3 existence claim holds, it would bear on the scope of LEAD-TRF-small-genus-cover-general, whose closure is about 2-torsion Kummer covers, not about Jacobians in the class. | Contributes to N2 (`ledger_refs` += `IDEA-20261024-a29e53`). Cross-row: `LEAD-ICB-ecc2k130-jacobian-carrier` `related` += `LEAD-TRF-prime-degree-ghs-genus-floor` with note "a29e53 e(n) crosses zero near n = 9.8; compare the lead's codimension heuristic". Coverage line `IDEA-20261024-a29e53<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 15 | ledger/proposals/IDEA-20261024-a29e53.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** notes state Torelli is dominant only at n = 3 (dim M_3 = dim A_3); at n = 4 the image is a hypersurface and at n = 5 codimension 3 in A_5, so "no such argument exists"; the density exponent is "naive; the classes of Res E have special structure (L is a function of T^n) which can correlate the coefficients". Enumeration plan: genus 2 with q <= 11, genus 3 hyperelliptic q <= 7 (4.0e7 forms), plane quartics q = 2, 3, 4 exhaustive and q = 5 sampled. Outcomes: 100 percent of {t, -t} pairs would show the cover floor is a property of the (2,...,2) construction. **Interp:** every extrapolation to n = 5, 7 rests on the unverified independence heuristic. | none beyond row 14 |
| 16 | ledger/proposals/IDEA-20261024-b58e07.yaml | yes by lane (`proposed_by: coordinator`, transcribes the user-named first-batch target of 2026-10-24) | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** claims (coordinator's prior, "each is proved or refuted at design"): n = 7 spectrum m in {1, 3, 4, 6, 7} (divisors of x^7 - 1 over F_2); split 2-torsion reaches g = 7 only via (m, r) = (3, 7); odd order with j not in F_q has floor 193. H-PEXT-d536a1 (approved, proposal_id b58e07) and EXP-PEXT-212d5c (approved by DEC-20261024-992998; six trials; `runs/` empty) are its design. citations: sibling README `research/ghs_cover_census_n5_20261013/README.md` (n = 5 floors 33 / 33 / 25 / 5, and the n = 3 class minima 13 / 5 / 3 restated there; read in the crypto clone; the n = 3 census directory `ghs_cubic_cover_census_20261012` exists and was not opened). KN-LIT-bf1772 (Iijima-Momose-Chao, d in {2,3,5,7}) is abstract only; KR-IC-5ea2f8 cites it. 2 `--match`: top hits LEAD-TRF-odd-char-descent-smith-quartic (14, 21), LEAD-ICP-gfp5-odd-char-cover (10), LEAD-TRF-small-genus-cover-general (8). **Interp:** this is the lead-defining record for N2. Closed-known risk: if KN-LIT-bf1772's full text already classifies the d = 5 and d = 7 cases, the n = 7 table could be reproduction; the record calls its novelty `unverified` and the KN entry has never been read past the abstract. | Defines N2 (section 5). `ledger_refs` += `IDEA-20261024-b58e07`, `H-PEXT-d536a1`, `GOAL-PEXT-4a1d6b`, `RQ-PEXT-7c3e91`, `DEC-20261024-e29f4c`, `DEC-20261024-992998`, `EXP-PEXT-212d5c`. Coverage line `IDEA-20261024-b58e07<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 17 | ledger/proposals/IDEA-20261024-b58e07.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** header "Coordinator's prior, not derivations". Notes: Lemma M makes m the degree of a divisor of x^n - 1; n = 7 is the first prime with ord_n(2) < n - 1; S = {0,2,3,4} or {0,1,2,4} gives the [7,3,4] simplex code with r = 7, m = 3, g = 7; odd-order floor 193 from orbits 3 + 7 (r = 10, m = 7), "Unproved". Scan cost (Q^3 - Q)/(q^3 - q): about 4.4e8 at q = 3, 4e12 at q = 5, so q >= 5 needs a constructive enumeration. Cross-characteristic pointer to KR-IC-791cb7 is "recalled, not checked". **Interp:** the q = 5 arm depends on a construction the notes do not yet give. | none beyond row 16 |
| 18 | ledger/proposals/IDEA-20261024-d84f20.yaml | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor; revisit-link LEAD-TRF-small-genus-cover-general | **Obs:** claim: K-rational degree-2 functions f_T are indexed by E(K)/2E(K); the branch set B_T is an E[2]-torsor with Frobenius cycle type fixed by E[2]/(F-1)E[2]; for T != 0 the genera are in {1, (n-1)2^n + 1} (4-cycle) and {1, 2^(n-2)(n-2) + 1, 2^(n-1)(n-1) + 1, (n-1)2^n + 1} ((2,2)); smallest T != 0 genus 3, 25, 161 at n = 3, 5, 7; expected to tie the x-line floor at n = 3 only via Momose-Chao "Type 2" (slides not read, "to be checked"). Sibling README states "Not established: degree-2 maps other than x" (quoted in the record). 2 `--match`: top hits LEAD-ICP-gfp5-odd-char-cover (10), LEAD-TRF-small-genus-cover-general (10), LEAD-ICE-semaev-cover-monodromy (9, 11), LEAD-EXO-torsor-deck-period (11). **Interp:** LEAD-TRF-small-genus-cover-general names "a non-Kummer cover family (Hess Artin-Schreier analogue, non-x-line function)" in `revisit_when`; non-x-line degree-2 functions are the second half of that clause. This record targets that condition and does not reopen the row: a T != 0 genus below the x-line floor in the planned panel is what would meet it, and the record predicts none for n >= 5. | Contributes to N2 (`ledger_refs` += `IDEA-20261024-d84f20`). Cross-row: `LEAD-TRF-small-genus-cover-general` `related` += `LEAD-TRF-prime-degree-ghs-genus-floor`, `ledger_refs` += `IDEA-20261024-d84f20`, with the note "proposal targets revisit_when (non-x-line degree-2 functions); does not reopen; a T != 0 floor below the x-line floor would meet it". Disposition unchanged. Coverage line `IDEA-20261024-d84f20<TAB>LEAD-TRF-prime-degree-ghs-genus-floor`. |
| 19 | ledger/proposals/IDEA-20261024-d84f20.notes.md | yes by lane | new_mechanism | (new) LEAD-TRF-prime-degree-ghs-genus-floor | **Obs:** notes derive the torsor Frobenius type (odd #E(K): only T = 0, type (1,3); Z/2: 4-cycle at T != 0; (Z/2)^2: (2,2) at T != 0), and note the module for the shared-orbit case is over F_2[x]/((x^n - 1)^2), "not semisimple; first place the program meets" such a module. n = 3 Type 2 identification is "to be checked". Extended tool needs K-stable 4-sets generated directly; cost about q^(2n) points for n = 3 (q <= 13: 4.8e6) and q = 3 only at n = 5. **Interp:** the non-semisimple case is outside Lemma M's semisimple setting, so N2's n = 7 spectrum claim does not carry over to T != 0 without new work. | none beyond row 18 |

## 3. Why the classifications are not the other options

- Not `decides_lead`: no record here is a decision that closes or reopens a lead's deciding hypothesis. DEC-20261024-992998 (approves EXP-PEXT-212d5c) and DEC-20261024-e29f4c (opens GOAL-PEXT-4a1d6b) are decisions but decide no lead row, because no PEXT lead exists; DEC-20261024-992998 moves H-PEXT-d536a1 from specified to approved, which is outside atlas scope. DEC-20261023-19c53b routes ff7415 to f15270 and, by its own text, "moves no hypothesis, idea or goal status".
- Not `not_ecdlp`: all ten records sit under ECDLP-lane questions or goals and use the ECDLP frontier map. The strongest `NONE` candidate is 727d2e (its text says "NOT ECDLP"); its parent B4 (2abd32) is mapped to a lead, so a `NONE` row would split the lineage.
- Zero runs anywhere in the group: every claim above is a proposal or a derivation. No outcome in this file is a measurement from these records.

## 4. Proposed edits to existing rows (consolidated; none applied)

1. `knowledge/leads/ecdlp/structure/LEAD-STR-curve-generation-provenance-seeds.yaml` (from IDEA-20261022-727d2e)
   - `ledger_refs` += `IDEA-20261022-727d2e`
   - `evidence` += `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261022-727d2e.yaml, note: "proposed integer-structure census of deployed p, r, p+-1, t with planted controls and detectability edge; self-declared not ECDLP; zero runs"}`
   - `evidence` += `{repo: crypto, path: research/nist_trapdoor_slot_program_20261011/README.md, note: "slot S2 (the prime): only matched rho (E2) pending; polynomial form of p unexamined"}` (no lead cites this directory today)
   - disposition `exhausted_at_scale`, obstruction, `revisit_when`, `best_measured`: unchanged.
2. `knowledge/leads/ecdlp/transfer/LEAD-TRF-pairing-target-field-recost.yaml` (from IDEA-20261022-e5b3a4)
   - `ledger_refs` += `IDEA-20261022-e5b3a4`
   - `evidence` += `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261022-e5b3a4.yaml, note: "proposed model-priced BN/BLS/KSS rows beside matched rho in the 5a band; refusal rule for k > k_cap; memory uncharged; zero runs"}`
   - `best_measured` stays `none: 33 EXP-PAIR contracts, zero runs`; `next_action` unchanged (its calibration step is the precondition for trusting the kappa fit the proposal relies on, H1 of e5b3a4).
3. `knowledge/leads/ecdlp/transfer/LEAD-TRF-mov-small-embedding-degree.yaml` (from IDEA-20261022-e5b3a4)
   - `ledger_refs` += `IDEA-20261022-e5b3a4` only.
4. `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-semaev-cover-monodromy.yaml` (from IDEA-20261023-f15270)
   - `ledger_refs` += `IDEA-20261023-f15270`, `IDEA-20260803-ff7415`, `DEC-20261023-19c53b`
   - `evidence` += `{repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261023-f15270.yaml, note: "derivation-first re-scope onto KN-OPEN-62c870 Q3: the 2^(n-1) clause derived (not measured) to be bookkeeping / proxy, not a yield lever; scope F_{q^n}; zero runs"}`
   - disposition `closed_obstructed` unchanged; `revisit_when` unchanged (this record does not break KN-FIND-4f0d84 or KN-FIND-bdcd60 and reports no factor-base statistic).
5. `knowledge/leads/ecdlp/ic-engine/LEAD-ICE-semaev-yield-model-coset-typing.yaml` (optional, from IDEA-20261023-f15270): `ledger_refs` += `IDEA-20261023-f15270` (KN-FIND-007 conservation is already cited there as evidence).
6. `knowledge/leads/ecdlp/transfer/LEAD-TRF-small-genus-cover-general.yaml` (from IDEA-20261024-d84f20, cross-link only)
   - `related` += `LEAD-TRF-prime-degree-ghs-genus-floor` (once N2 exists)
   - `ledger_refs` += `IDEA-20261024-d84f20`
   - append to the text of `obstruction.revisit_when` or as a YAML comment: "IDEA-20261024-d84f20 targets the non-x-line-function branch (degree-2 functions f_T, T in E(K)/2E(K)); proposal only, does not reopen; a T != 0 genus below the x-line floor would meet it."
   - disposition `closed_obstructed`: unchanged.
7. `knowledge/leads/ecdlp/ic-binary/LEAD-ICB-ecc2k130-jacobian-carrier.yaml` (from IDEA-20261024-a29e53, cross-link only): `related` += `LEAD-TRF-prime-degree-ghs-genus-floor`; no other change.

No edit is proposed to LEAD-ICP-gfp5-odd-char-cover: GOAL-PEXT-4a1d6b `scope_boundary.not_owned` excludes GOAL-GFPN-380702 and says a general n = 5 floor "may be cited there by that goal's Coordinator".

## 5. Proposed new rows

### N1. `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-pkm-tower-algebraic-oracle.yaml`

```yaml
id: LEAD-ICP-pkm-tower-algebraic-oracle
family: ic-prime
title: >-
  Petit-Kosters-Messeng tower factor bases (Kummer, Dickson/torus, 2-isogeny chain) as an algebraic
  decomposition oracle on prime-field curves: solving degree in the tower length, and per-target cost
mechanism: >-
  Factor base F = {P : x(P) in V}, V = {x : L(x) = 0}, L = L_t o ... o L_1 a composition of low-degree
  maps whose preimage tree splits completely over F_p; one auxiliary variable per level keeps every
  membership equation low degree, so the Semaev S_{m+1} system is a one-generator system over a
  2^N-point quotient, N = m*t about log2 r (RESEARCH_PKM_TOWER_ORACLE.md section 0). The question is
  whether the F4 / msolve solving degree stays bounded in N, which would make the oracle algebraic
  rather than a table.
disposition: open_next_step        # proposed; no deciding record exists for this row
next_action:
  step: >-
    Run IDEA-20261022-727676 on the committed cells (m=3 N=15, m=3 N=18, m=4 N=12, two targets each):
    instrument f4_fp_tower, report Z (multiply-adds on zero-reducing rows), U_time (symbolic share) and
    1/(1-U). Separate and blocked on host memory: the exponent question at m=3 N=21-27
    (IDEA-20261018-e0857e asks for a 256-512 GB host; round 7 reached 96 percent of a 14 GB cap at N=18).
  discriminates: >-
    Z >= 0.25 or U_time >= 0.25 with per-step pivot-lead Jaccard >= 0.999 makes a replay prototype a
    separate record (constant factor only, per the record); Z < 0.05 and U_time < 0.05 closes the replay
    lever at these cells with numbers. Neither outcome bears on whether D grows in N.
best_measured: >-
  F4 solving degree D reads 6, 6, 7, 7 over m=3 N=9-18 and 7 at m=4 N=12 and N=16 (RESEARCH_PKM_TOWER_ORACLE.md
  header, rounds 3 and 7); "whether it grows linearly in N is not decided". End to end in ecbench, the Kummer
  tower base costs 29-141x rho (negation map) on five curves of 20-28 bits, slope 0.26 +- 0.28 bits of S_IC/S_rho
  per bit of r (pkm_tower_ecbench_20261013); the isogeny tower base costs 1.00-1.33x the plain base of equal
  size with its auxiliary-curve search charged, IC arms 18-136x rho (pkm_isogeny_tower_ecbench_20261015). m=3
  N=21 msolve: all three N>=21 runs stopped at their wall inside degree 7, "inconclusive, null result"
  (pkm_m3_n21_msolve_20261018); a wall stop is not evidence about D.
evidence:
  - {repo: crypto, path: research/notes/index-calculus/RESEARCH_PKM_TOWER_ORACLE.md, note: "design, pilot and rounds 2-7; D table; engine f4_fp_tower"}
  - {repo: crypto, path: research/pkm_tower_round7_20261006/README.md, note: "m=3 N=18 D=7 both targets, confirmed by capped re-runs; 96 percent of 14 GB"}
  - {repo: crypto, path: research/pkm_tower_ecbench_20261013/README.md, note: "Kummer tower IC 29-141x rho, 896 runs verified"}
  - {repo: crypto, path: research/pkm_isogeny_tower_ecbench_20261015/README.md, note: "isogeny tower with search charged, 1.00-1.33x plain base"}
  - {repo: crypto, path: research/pkm_m3_n21_msolve_20261018/README.md, note: "N>=21 stopped at walls inside degree 7: inconclusive null"}
  - {repo: crypto-autoresearcher, path: ledger/proposals/IDEA-20261022-727676.yaml, note: "proposed replay-lever diagnostic; zero runs"}
ledger_refs: [IDEA-20261022-727676]   # merge with the sibling records listed in section 6
known_results: [KR-IC-f3da82, KR-IC-0d2021, KR-IC-5931ee]
related: [LEAD-ICP-algebraic-membership-factor-base, LEAD-ICE-prime-field-semaev-solving-degree,
          LEAD-ICP-digit-presentation-solving-degree, LEAD-ICE-boolean-f4-f5-f6-engines,
          LEAD-ICP-prime-ic-constant-engineering]
forecloses:
  - PKM tower factor base
  - Petit-Kosters-Messeng prime-field index calculus
  - algebraic decomposition oracle for prime-field curves
  - Kummer tower solving degree
  - 2-isogeny chain factor base
  - F4 trace replay on tower systems
areas: [ECDLP]
last_reviewed: 2026-10-24
```

Open question for the row author (conditional, not decided here): LEAD-ICP-algebraic-membership-factor-base is `closed_obstructed` by a theorem about the description degree of a size-B algebraic base in x and lists "multiplicative subgroup factor base x^B = 1" among its `forecloses`. The Kummer tower base is a multiplicative subgroup of order 2^t presented with auxiliary variables. Whether that theorem reaches the lifted presentation is not stated in the row; if it does, the PKM evidence belongs there and N1 reduces to an evidence addition.

### N2. `knowledge/leads/ecdlp/transfer/LEAD-TRF-prime-degree-ghs-genus-floor.yaml`

```yaml
id: LEAD-TRF-prime-degree-ghs-genus-floor
family: transfer
title: >-
  Prime-degree extension descent: what governs the minimum genus of GHS-type covers of E/F_{q^n}
  (n prime) by 2-torsion type, 2-adic type, isogeny class and characteristic
mechanism: >-
  The (2,...,2) compositum of the n conjugate double covers of the x-line has genus
  g = 2^(m-2)(r-4) + 1, where m is the F_2-dimension of the span of the sigma-orbit indicators of the branch set
  (the degree of a divisor of x^n - 1 over F_2, "Lemma M" of the sibling censuses) and r the size of the union.
  The program asks which algebraic quantity sets the floor at prime n (ord_n(2), 4-term relations among
  n-th roots of unity, the norm-character law for |E(K)[4]|, volcano reachability, degree-2 functions beyond x,
  Jacobians in the isogeny class of Res E), and where odd characteristic separates from Hess's characteristic-2
  families. Structural; the goal states no attack, no speedup, no cost.
disposition: open_next_step        # proposed; GOAL-PEXT-4a1d6b active, EXP-PEXT-212d5c approved, runs/ empty
next_action:
  step: >-
    Run the six frozen trials of EXP-PEXT-212d5c (regression RUN-PEXT-fccfb9, construct RUN-PEXT-056770,
    char2 RUN-PEXT-708f11, census RUN-PEXT-3fd19f, lean RUN-PEXT-af1b2a, analyze RUN-PEXT-422517), then the
    IDEA-20261024-3c71a9 panel (|E(K)[4]| by q mod 4, n=5, q=3..13) and the IDEA-20261024-d84f20 T != 0 extension.
  discriminates: >-
    The record's predictions, not results: n=7 spectrum m in {1,3,4,6,7}; floor 7 for split 2-torsion only via
    (m,r)=(3,7); floor 193 for odd order with j not in F_q. A genus-5 curve at q = 3 mod 4 with |E(K)[4]| != 8
    refutes the norm-character bookkeeping of 3c71a9; a T != 0 genus below the x-line floor meets the
    revisit_when of LEAD-TRF-small-genus-cover-general.
best_measured: >-
  n=5 derived floors 33 (odd) / 33 (2 mod 4) / 25 (E(K)[2]=Z/2, 4 | #E) / 5 (split), attained at q=3 (exhaustive,
  488 curves, 0 violations); n=3 class minima 13 / 5 / 3 for #E(K) odd / 2 mod 4 / 0 mod 4
  (research/ghs_cover_census_n5_20261013/README.md). No n=7 value: EXP-PEXT-212d5c has no runs.
evidence:
  - {repo: crypto, path: research/ghs_cover_census_n5_20261013/README.md, note: "n=3 at larger q and n=5 census; Lemma M, D0, E; floors 33/33/25/5; 20 of 81 split curves reach genus 5 at q=3, none of 31 models at q=5"}
  - {repo: crypto, path: research/ghs_cubic_cover_census_20261012/README.md, note: "merged n=3 census cited by the n=5 README (not opened in this fold)"}
  - {repo: crypto, path: research/odd_char_descent_genus3_20261014/REPORT.md, note: "minimum genus by exact period n: 5, 7, 1793, 9217 at n=5,7,11,13 (as cited by 5f08bd)"}
  - {repo: crypto-autoresearcher, path: ledger/goals/GOAL-PEXT-4a1d6b/goal.yaml, note: "goal, scope_boundary excludes GFPN, ECDLP2M; claim_boundary: toy fields, no attack or cost"}
  - {repo: crypto-autoresearcher, path: experiments/EXP-PEXT-212d5c/specification.yaml, note: "approved, six trials, runs/ empty"}
ledger_refs: [GOAL-PEXT-4a1d6b, RQ-PEXT-7c3e91, H-PEXT-d536a1, EXP-PEXT-212d5c, DEC-20261024-e29f4c,
              DEC-20261024-992998, IDEA-20261024-b58e07, IDEA-20261024-3c71a9, IDEA-20261024-5f08bd,
              IDEA-20261024-7be1c6, IDEA-20261024-a29e53, IDEA-20261024-d84f20]
known_results: [KR-IC-5ea2f8, KR-IC-a4dd54, KR-IC-791cb7]
related: [LEAD-TRF-small-genus-cover-general, LEAD-TRF-odd-char-descent-smith-quartic,
          LEAD-ICP-gfp5-odd-char-cover, LEAD-TRF-jv-sieve-fp6-weak-class,
          LEAD-ICB-ecc2k130-jacobian-carrier, LEAD-TRF-ghs-binary-composite]
forecloses:
  - GHS cover genus floor at prime extension degree
  - odd characteristic Weil descent minimum genus n=7
  - Hess analogue in odd characteristic
  - degree-2 functions beyond x for GHS covers
  - Jacobian isogenous to Weil restriction
areas: [PEXT]
last_reviewed: 2026-10-24
```

Closed-known risk for N2 (conditional): KN-LIT-bf1772 (Iijima-Momose-Chao, ePrint 2015/805, classification for d in {2,3,5,7}) is in the knowledge base as abstract-only and is cited by KR-IC-5ea2f8 and KR-IC-e2d81b. If its full text already contains the n=5 and n=7 genus tables, parts of N2 would be reproduction and the disposition would move toward `closed_known` on a KR row, which only a read of the paper (or a decision record) can establish. The ideas themselves mark novelty `unverified`.

Relevance note (observation): N2 concerns E over F_{q^n}, n prime, q odd or 2. Its goal text excludes work on deployed curves and on prime-field E(F_p).

## 6. coverage.tsv lines (proposed) and cross-group notes

```text
IDEA-20261022-727676	LEAD-ICP-pkm-tower-algebraic-oracle
IDEA-20261022-727d2e	LEAD-STR-curve-generation-provenance-seeds
IDEA-20261022-e5b3a4	LEAD-TRF-pairing-target-field-recost
IDEA-20261023-f15270	LEAD-ICE-semaev-cover-monodromy
IDEA-20261024-3c71a9	LEAD-TRF-prime-degree-ghs-genus-floor
IDEA-20261024-5f08bd	LEAD-TRF-prime-degree-ghs-genus-floor
IDEA-20261024-7be1c6	LEAD-TRF-prime-degree-ghs-genus-floor
IDEA-20261024-a29e53	LEAD-TRF-prime-degree-ghs-genus-floor
IDEA-20261024-b58e07	LEAD-TRF-prime-degree-ghs-genus-floor
IDEA-20261024-d84f20	LEAD-TRF-prime-degree-ghs-genus-floor
```

Cross-group notes for the merge (observations only; no edits proposed here):
- Other PKM records outside this group: IDEA-20261018-e0857e and IDEA-20261018-2d21b9 (unmapped in coverage.txt; outside this group's path list), H-ECDLP-60de36 and IDEA-20261009-f24f8a (mapped to LEAD-ICP-digit-presentation-solving-degree), EXP-ECDLP-f49f75, EXP-ECDLP-20a588. If another fold group proposes its own PKM row, use one id (`LEAD-ICP-pkm-tower-algebraic-oracle`).
- The mapping of H-ECDLP-60de36 ("chain-encoded isogeny factor base versus dense encoding") to the digit-presentation row is as found in coverage.tsv; LEAD-ICP-digit-presentation-solving-degree lists only H-PFDR-* refs and no PKM evidence.
- No PEXT record has a `prior_art.lead`; N2 should be named in the PEXT ideas' `prior_art.lead` only if a future edit adds the field.

## 7. Raw `--match` output (every record; command `python3 tools/lead_atlas.py --match "<phrase>"`, first 8 lines each)

Environment: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` set as in the task. Score is lexical token overlap, so it shows shared vocabulary, not equality of mechanism. Phrasings 1-2 are the two required; 727676 has three more (tower wording) because the first two missed the nearest lead row.

### IDEA-20261022-727676

```text
## 727676 match 1: F4 trace replay target-independent PKM tower Groebner
   18  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    8  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    5  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    5  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    5  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    4  KR-IC-0d2021                                 known_result       Modern Gröbner-basis complexity refinements
    4  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves

## 727676 match 2: symbolic preprocessing share multiply-adds Kummer tower F4 Amdahl replay Joux-Vitse
   10  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    8  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    6  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
    6  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class
    5  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
    5  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier
    5  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class

## 727676 extra match 3: Petit Kosters Messeng 2-isogeny chain factor base tower oracle prime field solving degree
   22  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   21  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   18  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) po
   18  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   14  KR-IC-49c882                                 known_result       Quasi-subfield polynomials
   14  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
   14  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   13  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems

## 727676 extra match 4: algebraic decomposition oracle Kummer tower F4 solving degree growth in N sparse engine
   20  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   16  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   14  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   14  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   12  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   12  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   10  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
## 727676 extra match 5: multiplicative subgroup factor base Kummer tower auxiliary variable per level low-degree membership
   29  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   15  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) po
   13  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   11  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   11  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   10  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)

```

### IDEA-20261022-727d2e

```text
## 727d2e match 1: hidden SNFS prime detection lattice radix census deployed curve primes
   10  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply
    7  KR-IC-9e610d                                 known_result       Survey consensus (2016)
    7  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    6  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) po
    6  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    6  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    6  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)

## 727d2e match 2: special form prime Solinas polynomial representation FGHT trapdoor detectability
    9  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    9  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    8  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    7  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
    7  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class
    6  KR-IC-49c882                                 known_result       Quasi-subfield polynomials
    6  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    6  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) po

```

### IDEA-20261022-e5b3a4

```text
## e5b3a4 match 1: pairing transfer MOV embedding degree TNFS BN BLS cost model matched rho
   29  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
   20  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
   19  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
   15  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   14  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
   13  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   13  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   12  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk

## e5b3a4 match 2: model-priced pairing transfer reference rows exTNFS embedding degree k* Frey-Ruck
   23  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
   16  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
   15  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   15  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
   14  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
   10  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
   10  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged
    8  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk

```

### IDEA-20261023-f15270

```text
## f15270 match 1: Gaudry Diem decomposition F_{q^n} compounding 2^(n-1) sign classes yield 1/n!
   19  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
   11  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
   10  KR-IC-081a58                                 known_result       Joux–Vitse n−1 decomposition and oracle-assisted static DH
   10  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    9  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
    9  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    7  KR-IC-64659b                                 known_result       Diem: rigorous subexponential ECDLP for suitable n
    7  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base

## f15270 match 2: summation polynomial extension field relation rate conservation count factor base coverage cap
   17  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   16  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   16  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
   16  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   14  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)

```

### IDEA-20261024-3c71a9

```text
## 3c71a9 match 1: GHS Weil descent odd characteristic genus n cover 4-torsion norm character
   24  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   23  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   18  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   17  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   11  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
   10  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   10  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery

## 3c71a9 match 2: Weil restriction elliptic curve F_{q^n} prime n 2-torsion branch quadruple genus floor
   12  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
   12  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
    9  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    9  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    8  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    8  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite

```

### IDEA-20261024-5f08bd

```text
## 5f08bd match 1: GHS cover genus floor prime n cyclotomic 4-term relation roots of unity characteristic 2 Mersenne
   13  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   12  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   11  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
   11  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    9  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold

## 5f08bd match 2: Hess genus Weil descent n = 7 Mersenne cyclic module x^n-1 span dimension
   15  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   15  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   13  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   13  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   12  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    8  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    8  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks

```

### IDEA-20261024-7be1c6

```text
## 7be1c6 match 1: isogeny walk volcano 2-isogeny reach floor cover GHS genus odd prime n
   22  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   19  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
   18  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   17  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   14  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   12  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite

## 7be1c6 match 2: isogeny class split 2-torsion curves per class hits per class Weil descent cover
   22  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   19  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   18  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   18  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
   16  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   13  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   13  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
   12  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class

```

### IDEA-20261024-a29e53

```text
## a29e53 match 1: genus-n Jacobian isogeny class Weil restriction Torelli L-polynomial Tian genus 3
   18  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   18  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   16  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   15  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   15  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
   14  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
   12  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
   12  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops

## a29e53 match 2: which isogeny classes of Res E contain a Jacobian of a curve of genus 3 existence not descent
   21  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   17  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   17  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   16  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   12  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   12  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
   11  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    9  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation

```

### IDEA-20261024-b58e07

```text
## b58e07 match 1: GHS cover genus floor n = 7 odd characteristic x^7-1 span
   14  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    9  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
    8  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
    8  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    7  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)

## b58e07 match 2: Weil descent minimum genus (2,...,2) compositum odd characteristic F_{q^7} census
   21  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   13  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   12  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    8  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    8  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    8  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks

```

### IDEA-20261024-d84f20

```text
## d84f20 match 1: degree-2 functions beyond x branch types E(K)/2E(K) GHS cover genus census
   11  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
   10  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
    8  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
    8  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack

## d84f20 match 2: Weil descent odd characteristic cover branch set Frobenius cycle type torsor 2-torsion type
   17  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   16  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   12  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   11  LEAD-EXO-torsor-deck-period                  closed_obstructed  Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent
   11  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   10  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    9  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    8  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)

```

## 8. Not done, limits

- No file in any repository was edited; no `lead_atlas.py --stamp` or `--check` was run (both belong to the review owner after merging the diffs).
- Mathematical content of the PEXT and f15270 records was not re-derived. Only figures they cite from the sibling README `research/ghs_cover_census_n5_20261013/README.md` were checked against that README (n=5 floors, 20 of 60 and 0 of 21 with |E(K)[4]| = 8 / 4 at q = 3, genus 25 at q = 5, none of 31 models reaching genus 5 at q = 5). The n=3 census README, KN-LIT-bf1772 beyond its abstract, the Momose-Chao slides and Hess/Menezes-Teske sources were not opened.
- The PKM figures in N1 come from the headers and READMEs named there; per-run logs and `runs/*.jsonl` were not opened.
- A `--match` miss or a grep-empty result is a statement about token overlap in the lead rows, not evidence that no related work exists elsewhere in the repositories.
- Dispositions proposed for N1 and N2 (`open_next_step`) are proposals to the row author; no decision record in this group decides them.

---

## Group: car-knowledge-problems

# Fold: car-knowledge-problems (31 changed paths) into the ECDLP lead atlas, as proposed diffs

Read-only review. No file in any repository was edited, created, staged or committed; this file and its scratch inputs live under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/audit/`. Observation and interpretation are separated; interpretation is conditional. A timeout, censor or infrastructure stop is not evidence. Hypothesis, experiment and goal statuses are quoted from the ledger, never proposed.

Group: `car-knowledge-problems`. Repository root: `/Volumes/SSD990-2/crypto-autoresearcher`. Paths: 3 findings, 9 open-problem records, 19 `problems/*.md` records (delta.txt lines 129-147).

## Summary

Tally of row actions: advances_lead = 23, new_mechanism = 2, not_ecdlp = 3, unclear = 3. Disposition changes proposed: none (every closure/open label stays; scope notes only). Proposed new lead rows: 2. Coverage remaps: 1.

Entries that reference the two proposed new rows (`related +=`, `forecloses -=`, the coverage remap, the `H-TRA-4344b7` move) pass `check_leads` only with the new rows present; each such row states its dependency under 'Dependency on a new row'. The diffs do not depend on application order (no two rows rewrite the same text).

Edits were checked in memory against the atlas with `lead_atlas.check_leads` (ledger refs resolve by basename under `ledger/`, evidence paths exist, `related` ids exist, `forecloses` >= 3, known results exist): baseline 0 errors, after applying every proposed edit 0 errors, new errors 0. Each reword's old text was matched against the live lead (0 mismatches).

### Findings that change what a lead says (factual, not interpretive)

1. `LEAD-TRF-teske-secret-isogeny-trapdoor` says every trial of run-20261016T0409Z failed (`psutil_import_missing`; evidence note 'all trials infrastructure_error'). `experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/data.json` records 3 output_validated, 11 psutil_import_missing, 2 rss_sampling_failure, 4 waiting_on_dependencies (row `ectd-arity3-panel-infrastructure-loss`).
2. `LEAD-TRF-padic-canonical-section` states 'any non-homomorphic section recovers d only at the random 1/p rate' under `kind: theorem`; `KN-FIND-7e2b94` records that universal as false (planted sections) and the toy rate as measured only for three sections; `best_measured` still says 'evidence records not filed' although EV-CZLIFT-ad28f5, -f2a401, -764f54 are filed (rows KN-FIND-7e2b94, KN-FIND-c71e5d).
3. `LEAD-TRF-anomalous-padic-lift` says 'review pending' for the CZLIFT canonical-lift re-derivation; that review is filed (DEC-20261023-147f9f). `LEAD-TRF-global-lift-small-height` carries the same words for H-CZLIFT-9a32e9-type records, which belong to another fold group and are not touched here.
4. The legacy register notes (reconciliation of 2026-10-18) state that no saturation theorem is on record (KN-OPEN-004), that no commutator-collapse proof is committed (KN-OPEN-008), that the cited DEC-20260722-003..006 do not bear on the problems (premise check, KN-OPEN-004/005/006/007/008/009/010), and that H-TRA-001's decision was not located (KN-OPEN-010). Files on disk: `research/THM_BKKMV1.md` (box saturation proved for m <= 5), `research/THM_COMMUTATOR_KERNEL1.md` (commutator collapse for the translation/negation quiver), `research/THM_JETBARRIER1.md`, `research/THM_INCBARRIER1.md`; hypotheses at `ledger/H-*.yaml` (not `ledger/hypotheses/`); root-level decisions `ledger/DEC-20260722-002..006.yaml` (H-TTN-001, H-BKKMV-001/H-BKK-001, H-JETB-001/H-JET-001, H-NCP-001, H-INCB-001/H-INC-001) and `ledger/DEC-20260718-003/-005/-007/-008/-009/-011.yaml`. **ID collision:** `ledger/DEC-20260722-001..005.yaml` and `ledger/decisions/DEC-20260722-001..005.yaml` are different records with the same ids (verified for -002, -003, -004, -005); the notes' premise check read only `ledger/decisions/`. `lead_atlas.ledger_ids()` resolves by basename and cannot tell them apart, so proposed evidence entries cite explicit paths and the ids are kept out of `ledger_refs` where they are ambiguous.
5. `H-TRA-4344b7` (transfer-operator hypothesis) sits in `LEAD-RHO-r-adding-walk-mixing.ledger_refs`; that lead's mechanism (rho walk constant) does not match it. Proposed: move to a new lead.
6. `LEAD-ICE-first-fall-degree-assumptions.next_action` asks to fix the `fall_profile` defect and re-run; both are done on replay (archived 70/10 -> corrected 68/12) and a Lean-checked finite counterexample exists, review pending.
7. `LEAD-STR-curve-generation-provenance-seeds` infers density >= 2^-30 from screens of 21 named classes; the 1997-draft acceptance space is >= 69 full-prime and >= 99 near-prime certified seed positions, so the 21 are a retrospective subset.

### Conditional folds the reviewer should confirm (alternative: new row)

- KN-OPEN-004 (BKK) and KN-OPEN-007 (tensor-train) into `LEAD-ICE-prime-field-semaev-solving-degree` (solver alternatives for the same dense composed-resultant object).
- KN-OPEN-008 (quiver word search) into `LEAD-RHO-generic-sqrt-lower-bound` (conditional on the cost layer, an open gap in the theorem note).
- KN-OPEN-006 and `str002` (designed supports / phi-orbit bases) into `LEAD-ICB-orbit-linear-algebra` (a binary-family lead; Table B prime rows give the prime LA share).
- `dtree-slope-grid-design-infeasible` into `LEAD-ICP-residual-partial-relations` (medium-base descent is a per-target variant of the large-prime idea; the lexical score is low).

## Table

| # | path | ECDLP | action | lead | reasoning |
|--:|:--|:--:|:--|:--|:--|
| 1 | `knowledge/findings/KN-FIND-3c7e19.md` | yes | advances_lead | LEAD-TRF-anomalous-padic-lift | Smart degeneracy on the canonical lift is the known Serre-Tate/Kummer theorem; closes the lead's 'review pending' via DEC-20261023-147f9f. Instrument calibration, no new attack. |
| 2 | `knowledge/findings/KN-FIND-7e2b94.md` | yes | advances_lead | LEAD-TRF-padic-canonical-section | s_tor is the unique homomorphic section and Smart vanishes on it (derivation); the universal '1/p for every other section' clause is false (planted sections). Split the lead's obstruction. |
| 3 | `knowledge/findings/KN-FIND-c71e5d.md` | yes | advances_lead | LEAD-TRF-padic-canonical-section | F_p^* calibration: naive section succeeds exactly when g^d mod p^2 < p, so a 1/p null is wrong for structured sections. Replaces 'size effect' in the lead; notes a Siegel-finite elliptic analogue. |
| 4 | `knowledge/open-problems/KN-OPEN-004.md` | yes | advances_lead | LEAD-ICE-prime-field-semaev-solving-degree | BKK/mixed volume of sectioned Semaev: MV = box Bezout (theorem m<=5, measured m=6); fold into the Semaev solving-degree lead. Register note omits THM_BKKMV1 and root DEC-20260722-003. |
| 5 | `knowledge/open-problems/KN-OPEN-005.md` | yes | advances_lead | LEAD-EXO-augmented-oracle-ggm | Jet/net/incidence GGM-simulability: THM_JETBARRIER1 (simulation theorem; maximality C2 open) and THM_INCBARRIER1/2 back the lead; register stays open. Evidence and scope note. |
| 6 | `knowledge/open-problems/KN-OPEN-006.md` | yes | advances_lead | LEAD-ICB-orbit-linear-algebra | Designed AP supports: measured displacement rank ~ B (H-STR-001 rejected_scoped); LA is <= 0.4% of S in prime Table B rows, so structured LA cannot move S at measured scale. Extend orbit-LA lead. |
| 7 | `knowledge/open-problems/KN-OPEN-007.md` | yes | advances_lead | LEAD-ICE-prime-field-semaev-solving-degree | Tensor-train bond ranks of the Semaev resultant tree equal the exact Sylvester count (m<=6); exponent -> 2 if it persists. Fold with BKK into the Semaev solving-degree lead. |
| 8 | `knowledge/open-problems/KN-OPEN-008.md` | yes | advances_lead | LEAD-RHO-generic-sqrt-lower-bound | Quiver word search: a commutator-collapse theorem is committed (THM_COMMUTATOR_KERNEL1, DEC-20260722-005); the register note says none exists. Fold into the generic lower-bound lead. |
| 9 | `knowledge/open-problems/KN-OPEN-009.md` | yes | advances_lead | LEAD-ICE-semaev-cover-monodromy | Monodromy of the Semaev cover: chain KN-OPEN-009 -> -8a7432 -> -62c870 (live); the 2026-10-18 'not on record' note predates KN-FIND-bdcd60 and DEC-20261022-a0f165. Evidence cross-reference only. |
| 10 | `knowledge/open-problems/KN-OPEN-010.md` | yes | new_mechanism | NEW: LEAD-EXO-koopman-transfer-operator | Koopman/transfer operator of translation-by-P: barrier shown only for negation-symmetric x-cells; H-TRA-4344b7 is misfiled under rho walk mixing. New lead; move the ref. |
| 11 | `knowledge/open-problems/KN-OPEN-5b3a08.md` | yes | advances_lead | LEAD-ICE-decomposition-probability-audit | Harness defects: s4_expr bug reached 21 MTIC/FIB runs and ICINV m4 columns (matched reruns in progress); full_curve default may confound cofactor effects. Caveats only; no lead clause affected. |
| 12 | `knowledge/open-problems/KN-OPEN-d3a6f0.md` | yes | new_mechanism | NEW: LEAD-TRF-torsion-section-digit-fourier | Fourier mass of p-adic digit characters (i>=1) of s_tor vs the n^(-1/4) Fourier-learning breakeven lies outside the formal-log closure. New open lead; narrow padic-canonical-section. |
| 13 | `problems/README.md` | no | not_ecdlp | none | Index of obstruction records; no mechanism of its own. Lead-level content is folded in the per-problem rows. No atlas edit. |
| 14 | `problems/dreg-c1-memory-cap-exhausted.md` | yes | advances_lead | LEAD-ICE-chained-semaev-dreg-vs-semiregular | GOAL-DREG-001 item C1 (n=15, D=6): 0 of 6 runs completed; prepare phase 11.73/12.22 GiB vs 8 GiB cap; floor raised to 16 GiB (DEC-20261005-8d23bb), retry carded, no output. Not a d_reg result. |
| 15 | `problems/dtree-slope-grid-design-infeasible.md` | yes | advances_lead | LEAD-ICP-residual-partial-relations | EXP-DTREE-001 (depth-2 medium-base descent): slope grid design_infeasible (0/18 cells), C2 inconclusive. Conditional fold under the large-prime lead; results are not evidence. |
| 16 | `problems/ectd-arity3-panel-infrastructure-loss.md` | yes | advances_lead | LEAD-TRF-teske-secret-isogeny-trapdoor | EXP-ECTD-0cf008: 3 of 20 arms validated, 17 lost to infrastructure. The Teske lead says 'all trials infrastructure_error'; data.json shows otherwise. Correct the lead. |
| 17 | `problems/finite-worksheet-direct-invocation.md` | yes | unclear | none | Native-admission infrastructure for toy finite worksheets (resolved for six routes). Maps via H-ECDLP-7bd5f5/-242aa4 to two leads that do not cite them; no row field changes. |
| 18 | `problems/formal-target-semantic-fidelity-unreviewed.md` | yes | advances_lead | LEAD-EXO-methodology-instruments | Lean build/axiom success of 83-84 targets is not claim fidelity; independent semantic review pending (Semaev degree-two is the worked counterexample). Methodology-lead evidence entry. |
| 19 | `problems/frob-c5-factor-kernel-and-model-bridge.md` | yes | advances_lead | LEAD-ICB-frobenius-orbit-factor-base | Lean proofs of the C5 factor-kernel decomposition (q=11,13,19; n=5) support the lead's X^n-1 lattice statement; code bridge, source custody, review open. Evidence note only. |
| 20 | `problems/full-ledger-validation-errors.md` | yes | advances_lead | LEAD-EXO-methodology-instruments | validate_ledger.py exits 1 on main (162 unsuppressed errors, 49 paths); includes the RUN-FROB-91ee9c-7119f2 source-custody gap. Methodology evidence entry plus a custody note on the Frobenius lead. |
| 21 | `problems/full-width-ic-arity-grid-unmeasured.md` | yes | advances_lead | LEAD-ICP-full-width-arity-grid | Full-width arity grid still unmeasured; adds the Koblitz size-coordinate correction and the 2026-10-19 m=2 diagnostic (three 600 s censors) to the lead. |
| 22 | `problems/icperf-prime63-m2-output-contract-mismatch.md` | yes | advances_lead | LEAD-ICP-full-width-arity-grid | Prime63 m=2 diagnostic: plan and launcher disagree on outputs, so supervisor records invalid_output though the checker passes; three 600 s censors stand. Edit shared with full-width row. |
| 23 | `problems/icperf-prime63-monitor-and-positive-controls.md` | yes | advances_lead | LEAD-ICP-full-width-arity-grid | Prime63 panel: RSS monitor lost on first natural cell, six planted positives censored at 300 s; m=2 diagnostic adds three 600 s censors. Refresh best_measured via the full-width edit. |
| 24 | `problems/isogeny-graph-wide-relation-solver.md` | yes | advances_lead | LEAD-STR-class-representative-ic-selection | Graph-wide P29/P37 study: transport replayed on all 2,304 edges and 128 public targets; still no admitted run or complete solve. Updates the lead's 'blocked on collector and transport' note. |
| 25 | `problems/legacy-adapter-output-preservation.md` | no | not_ecdlp | none | Native-execution adapter source bindings (PR 2397): scratch deletion on I/O error and inconsistent-timing acceptance in legacy adapters. Pure repo infrastructure; no lead field. |
| 26 | `problems/legacy-trial-manifest-schema.md` | yes | unclear | none | Stage-0 worksheet drivers lacked canonical run fields (resolved for six native routes). Maps via H-ECDLP-cba67a/-8c879e/-85fe43/-18c7f7 to two leads that do not cite them; no row field changes. |
| 27 | `problems/nist-seed-selection-rule-unexplained.md` | yes | advances_lead | LEAD-STR-curve-generation-provenance-seeds | 1997-draft acceptance space is >= 69 full-prime (>= 99 near-prime) seed positions; the lead's 'exhausted' screens cover 21 named classes only. Scope note and revisit condition; disposition unchanged. |
| 28 | `problems/pages-workflow-disabled-live-snapshot-stale.md` | no | not_ecdlp | none | GitHub Pages workflow disabled; public dashboard snapshot stale (Oct 11). Publication infrastructure; no ECDLP content and no lead field. |
| 29 | `problems/semaev-degree-two-fall-nonzero-bridge.md` | yes | advances_lead | LEAD-ICE-first-fall-degree-assumptions | fall_profile defect fixed on replay (archived 70/10 -> corrected 68/12); a Lean-checked finite counterexample exists at n=4; review pending. Rewrite next_action; leave open_blocked. |
| 30 | `problems/staged-xrank-independent-arithmetic-verification.md` | yes | unclear | none | EXP-ECDLP-daee4d (x-rank vs low-Hamming scalars) has only label/file-presence checks. Maps to invertible-hint-subset via H-ECDLP-b093c1, which the lead does not cite; no row change. |
| 31 | `problems/str002-support-verdict-missing-artifacts.md` | yes | advances_lead | LEAD-ICB-orbit-linear-algebra | H-STR-002 (phi-orbit base -> O(1) displacement rank) weakened on artifact/ablation/cost grounds, not rejected; no mechanism test exists. Refs on the orbit-LA lead (shared with KN-OPEN-006). |

## Per-path detail

### 1. `knowledge/findings/KN-FIND-3c7e19.md`

- **Action:** `advances_lead`; **lead:** LEAD-TRF-anomalous-padic-lift (currently `closed_known`); **record id:** KN-FIND-3c7e19; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `FIND-3c7e19-a`; `FIND-3c7e19-b`
- **Observation:**
  - KN-FIND-3c7e19 (confidence established, proof_status derivation) states that Smart's precision-p^2 attack degenerates exactly on the canonical-lift class mod p^2 and says of itself: 'This is known theory. It is not a discovery of this program' (prior art Belding 2007, arXiv:math/0703906, section 7).
  - Two code-independent instruments (point-arithmetic flag, j-distance rule) agree on 14,616/14,616 frozen rows (RUN-CZLIFT-041d05, RUN-CZLIFT-6709c9) and 12,778/12,778 red-team full-fiber lifts, on 29 class-number-one CM anomalous curves with 7 <= p <= 1373. Smart recovered d on 2,052/2,052 non-degenerate rows per seed.
  - Degenerate next digit: pooled counts 93 and 87 against 86.84 (z = +0.68, +0.02); null depends on the metric definition (CORR-20261023-9f2176). Per-cell exception: j = 0 with A = 0 mod p^2, mu_6 equivariance, counterexample p = 7, y^2 = x^3 + 5.
  - The finding's own limits: 'No new obstruction and no new attack'; power 0.05 against a single-section 1/sqrt(p) leak at p > 500; j = 0 threshold 2e = 6 pinned only to (3, 6]; nothing about non-anomalous, non-CM, ramified lifts or cryptographic sizes.
  - Current lead text (LEAD-TRF-anomalous-padic-lift): 're-derived the canonical-lift degeneracy (CZLIFT runs, review pending)'; evidence note on DEC-20261009-44c288 reads 'evidence round not yet filed'.
  - DEC-20261023-147f9f (evidence_review, decision support): H-CZLIFT-889c9d approved -> supported at toy tier, scoped to EV-CZLIFT-712fe4; 'It closes no lane ... Authorizes no attack.'
- **Interpretation (conditional):**
  - The review the lead calls pending is filed (EV-CZLIFT-712fe4, DEC-20261023-147f9f); the lead's wording is stale. Disposition closed_known is unchanged: the record reproduces a literature theorem.
  - The agreement calibrates instruments against a known theorem (the decision says so); read as conditional support for the instruments' trustworthiness, not as independent evidence for the theorem or as any ECDLP leverage.
- **Proposed diff:**

```
EDIT LEAD-TRF-anomalous-padic-lift
  ledger_refs += ["EV-CZLIFT-712fe4", "DEC-20261023-147f9f", "CORR-20261023-9f2176", "EXP-CZLIFT-17b7eb"]
  related += ["LEAD-TRF-padic-canonical-section"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/findings/KN-FIND-3c7e19.md, note: "Canonical-lift degeneracy of Smart = Serre-Tate/Kummer theorem (Belding 2007 s.7); two instruments agree 14,616/14,616 rows, 29 CM anomalous curves p <= 1373 (toy)"}
  evidence += {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-712fe4.yaml, note: "Evidence for H-CZLIFT-889c9d (supported at toy tier, DEC-20261023-147f9f); calibrates instruments, adds no attack"}
  reword obstruction.statement:
    - "(CZLIFT runs, review pending)"
    + "(EXP-CZLIFT-17b7eb: the degeneracy is the Serre-Tate/Kummer theorem, prior art Belding 2007 s.7; two code-independent instruments agree on 14,616/14,616 rows of 29 class-number-one CM anomalous curves, p <= 1373, and Smart recovers d on 2,052/2,052 non-degenerate rows per seed; EV-CZLIFT-712fe4, DEC-20261023-147f9f; toy tier, instrument calibration, no new attack)"
  reword evidence[DEC-20261009-44c288].note:
    - "CZLIFT trials output_validated; evidence round not yet filed"
    + "CZLIFT trials output_validated; evidence round filed as EV-CZLIFT-712fe4 / DEC-20261023-147f9f"

```

### 2. `knowledge/findings/KN-FIND-7e2b94.md`

- **Action:** `advances_lead`; **lead:** LEAD-TRF-padic-canonical-section (currently `closed_obstructed`); **record id:** KN-FIND-7e2b94; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `FIND-7e2b94-a`; `FIND-7e2b94-b`
- **Observation:**
  - KN-FIND-7e2b94 (derivation tier, uniform in p >= 5, n != p, any Z_p-lift with good reduction): s_tor is the unique homomorphic ([c]-equivariant) section of reduction over <P>; commutes with every Z_p-endomorphism preserving <P>; computable in at most 2(bits(n)+bits(p^k))+1 complete additions at precision k; z([n]s_tor) vanishes identically; s_tor carries the DL relation isomorphically into E(Q_p)[n], 'no easier'.
  - The clause 'a computable canonical section would be a full break' is false under every constraining reading of 'canonical' and circular under the remaining one (a section whose Smart residue recovers d is a DL oracle by definition).
  - Toy measurement (RUN-CZLIFT-dab752, RUN-CZLIFT-5b2581; 50 <= p <= 600, 11 <= n <= 613, k = 4, 36 curves per seed, seeds 20261009/20261010): Hensel-random, naive-integer and Teichmuller sections show no identity-readout excess meeting the 4-sigma threshold; detection floor 4.2x to 5.2x of 1/p; uniform p^-1/2 leak excluded with power >= 0.989; planted leaking section detected at rate 1; independent exhaustive control 0.97x to 1.06x of a same-shape null on 71 curves.
  - Explicit non-claims in the finding: NOT 'every non-canonical section recovers d only at 1/p: false (planted sections)'; planted oracles f(x) = n - x or x^2 mod n pass the identity readout while recovering d on 99-100% of pairs; the 1/p reference assumes H-1, validated at toy scale only.
  - DEC-20261023-36b4f0 (support): H-CZLIFT-6d4ed1 approved -> supported in the scope of EV-CZLIFT-ad28f5; RQ-CZLIFT-b9f765 not closed; 'Correction records pending (N-2 to N-4)' on mechanism wording.
  - Lead text today: obstruction kind 'theorem' with 'any non-homomorphic section recovers d only at the random 1/p rate'; best_measured ends 'evidence records not filed'.
- **Interpretation (conditional):**
  - The lead's second clause is stated as a theorem but the finding records it as unproved (and false as a universal) and measured only for three natural sections at toy scale. Read conditionally: the theorem-grade part is the derivation about s_tor; the 1/p rate is a toy measurement with a stated detection floor.
  - 'evidence records not filed' is stale: EV-CZLIFT-ad28f5, EV-CZLIFT-f2a401, EV-CZLIFT-764f54 and DEC-20261023-36b4f0, -039ddf, -2e7447 are filed.
  - Disposition: closed_obstructed can stand for the formal-logarithm / homomorphic-section channel and the identity readout of the three sections; it should not be read to cover other readouts of s_tor (see KN-OPEN-d3a6f0 row).
- **Proposed diff:**

```
EDIT LEAD-TRF-padic-canonical-section
  ledger_refs += ["EV-CZLIFT-ad28f5", "DEC-20261023-36b4f0", "EXP-CZLIFT-ae0a13", "RQ-CZLIFT-b9f765"]
  related += ["LEAD-TRF-torsion-section-digit-fourier"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/findings/KN-FIND-7e2b94.md, note: "s_tor unique homomorphic section, Smart functional vanishes (derivation, p >= 5, n != p); universal 1/p clause false (planted sections); three sections at random rate, toy, floor 4.2-5.2x"}
  evidence += {repo: crypto-autoresearcher, path: ledger/evidence/EV-CZLIFT-ad28f5.yaml, note: "Evidence for H-CZLIFT-6d4ed1 (supported, DEC-20261023-36b4f0); two mechanism sentences excluded (B-6, B-7)"}
  set obstruction.kind:
    + "proof"
  set obstruction.statement:
    + "SPLIT into (A) derivation and (B) toy measurement. (A) KN-FIND-7e2b94, lemmas D1-D6, uniform in p >= 5, n != p, any Z_p-lift: the prime-to-p torsion section s_tor is the unique homomorphic ([c]-equivariant) section of reduction over <P>; z([n] s_tor) vanishes identically so the Smart functional reads nothing from it; it costs at most 2(bits(n)+bits(p^k))+1 complete additions and carries the DL relation isomorphically into E(Q_p)[n]; the clause 'a computable canonical section is a full break' is false under every constraining reading of 'canonical' and circular under the other. (B) toy only (50 <= p <= 600, 11 <= n <= 613, k = 4, seeds 20261009/20261010): the identity readout 'Smart ratio = d mod p' of the Hensel-random, naive-integer and Teichmuller sections shows no excess meeting the 4-sigma threshold, with detection floor 4.2x-5.2x of 1/p. NOT ESTABLISHED: that every non-homomorphic section recovers d only at rate 1/p (planted sections f(x) = n - x, x^2 mod n pass the identity readout while recovering d); the naive F_p^* section succeeds exactly when g^d mod p^2 < p, so the null depends on the section and generator (KN-FIND-c71e5d). Scope of closure: formal-logarithm / homomorphic-section channel and the identity readout; other readouts of s_tor (digit characters, i >= 1) are LEAD-TRF-torsion-section-digit-fourier."
  set best_measured:
    + "toy: EV-CZLIFT-ad28f5 (replicated; torsion canonicity, homomorphism, degeneracy and tau-identity on 1116/1116 pairs, blind re-derivation 1116/1116); identity-readout rates at the random level for three sections with 4.2x-5.2x detection floor; planted leaking section detected at rate 1 (frozen z +172 to +292); EV-CZLIFT-f2a401 and EV-CZLIFT-764f54 filed (see rows KN-FIND-c71e5d, KN-OPEN-d3a6f0)"

```
- **Dependency on a new row:** The `related += LEAD-TRF-torsion-section-digit-fourier` entry and the last sentence of the new obstruction text depend on adopting the new lead row proposed in the KN-OPEN-d3a6f0 row; if that row is rejected, drop both (the rest is independent). obstruction.kind 'proof' (was 'theorem') because the finding labels part (A) a derivation.

### 3. `knowledge/findings/KN-FIND-c71e5d.md`

- **Action:** `advances_lead`; **lead:** LEAD-TRF-padic-canonical-section (currently `closed_obstructed`); **record id:** KN-FIND-c71e5d; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `FIND-c71e5d-a`; `FIND-c71e5d-b`
- **Observation:**
  - KN-FIND-c71e5d (derivation, toy, two seeds): Teichmuller section: homomorphic and log_p vanishes on 3200/3200 pairs, ratio never defined. Naive integer section: success iff g^d mod p^2 < p (Eisenstein logarithmic property of the Fermat quotient), reproduced on 3200/3200 archived rows by two independent implementations. Pooled naive successes 33 against 5.39 at mean 1/p (ratio 6.13, 95% CI 4.22-8.61) but 33 against 29.19 under the exact null (1.13, CI 0.78-1.59); random-digit Hensel 3 against 5.39 (0.56, CI 0.12-1.63).
  - Use clause: a contract that scores a non-canonical section against 1/p must first compute the exact null for that section and generator; under the smallest primitive root the frozen 4-sigma test falsifies a 1/p prediction with probability about 0.94 per seed (red-team simulation).
  - Limits stated by the finding: G_m only; 'no discrete-log leverage'; a review-side computation (RT-20261023-2411b8, not a run record) shows an elliptic analogue: the integral section on a small-coefficient global model recovers d exactly at integral multiples of the global lift (37a1 short model 1420/1420 at d = 2..6; y^2 = x^3 + 17 287/287 at d = 2); the set is Siegel-finite (recalled) and does not grow with p; it depends on the Weierstrass model and lift convention.
  - DEC-20261023-039ddf (reject_scoped): H-CZLIFT-d37231 approved -> rejected at toy tier, scoped to naive-section success and homomorphism-rate clauses as posed; does not touch Hom(Z/(p-1), Z_p) = 0, says nothing about elliptic curves, does not close RQ-CZLIFT-b9f765.
  - Lead text today: 'the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one'.
- **Interpretation (conditional):**
  - The finding turns the lead's qualitative 'size effect' into an exact rule; the lead's explanation stands and becomes checkable. It also supplies the matching-null discipline that the lead's 'random 1/p rate' clause lacks (see KN-FIND-7e2b94 row).
  - The exact rule is carried into the lead by the replacement obstruction text proposed in the KN-FIND-7e2b94 row; this row adds only refs, evidence and cross-references, so the two rows do not depend on application order.
  - The review-side elliptic analogue (integral multiples of a small global point recovered exactly, finitely many by Siegel) is consistent with LEAD-TRF-global-lift-small-height's height obstruction (covering a residue needs large height) rather than a counter-example to it; it is not a measured run result, so only a cross-reference is proposed.
- **Proposed diff:**

```
EDIT LEAD-TRF-padic-canonical-section
  ledger_refs += ["EV-CZLIFT-f2a401", "DEC-20261023-039ddf", "EXP-CZLIFT-bdae69", "H-CZLIFT-d37231"]
  related += ["LEAD-TRF-global-lift-small-height"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/findings/KN-FIND-c71e5d.md, note: "F_p^* calibration: Teichmuller kills log_p; naive section succeeds iff g^d mod p^2 < p (3200/3200 rows, two implementations); 1/p null wrong for structured sections; toy"}
  evidence += {repo: crypto-autoresearcher, path: experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/redteam_report.yaml, note: "RT-20261023-2411b8: review-side elliptic analogue on small-coefficient global models (37a1 1420/1420, y^2=x^3+17 287/287), Siegel-finite; not a run record"}

EDIT LEAD-TRF-global-lift-small-height
  related += ["LEAD-TRF-padic-canonical-section"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/findings/KN-FIND-c71e5d.md, note: "Limits section: review-side elliptic analogue, integral multiples of a small global point recovered exactly on small-coefficient models, Siegel-finite, does not grow with p (not a run record)"}

```

### 4. `knowledge/open-problems/KN-OPEN-004.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-prime-field-semaev-solving-degree (currently `closed_known`); **record id:** KN-OPEN-004; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-004-a`; `OPEN-004-b`; `OPEN-004-c`
- **Observation:**
  - Register question: are the Newton polytopes of the target-sectioned Semaev family proper subpolytopes of the degree box (MV < Bezout) or saturated (MV = Bezout); reconciliation note (2026-10-18) states results are toy-scale scoped negatives (m <= 5, p <= 1009), 'no saturation theorem is on record', and that H-BKK-001 / H-BKKMV-001 were not found under ledger/hypotheses/.
  - On disk: ledger/H-BKK-001.yaml (status rejected_scoped, DEC-20260718-005), ledger/H-BKKMV-001.yaml (status supported, DEC-20260718-011). EV-BKK-001 (contradicts, replicated): rho_m = MV/(n! D^n) = 1 exactly in 54/54 instances (MV 8, 384, 98304 at m = 3, 4, 5); sparse route more expensive than dense where measured (op ratios 1.384 at m = 3, 5.537 at m = 4). EV-BKKMV-001 (neutral, replicated): MV_m = (m-1)! 2^((m-1)(m-2)); BKK cross-check 21/21 Semaev cells; unsectioned supports are not box-saturated (13 < 27, 439 < 625, 54777 < 59049). EV-BKKMV-002: MV_6 = 125,829,120 on 6/6 instances at p in {1000003, 1000033}; hull = box on 30/30 sections (28/30 full 1,419,857 cells).
  - research/THM_BKKMV1.md (2026-07-18): sectioned box-saturation PROVED for m <= 5 (hence MV law a theorem for m <= 5); all-m is CONJECTURE C1, reduced to the interior-fiber non-cancellation Lemma-G. research/THM_BKKMV2.md (2026-07-24): Theorem B (b-extremal grade never cancels) PROVED conditional on (T_m), unconditional for m <= 5.
  - ID collision: ledger/DEC-20260722-003.yaml (root; targets H-BKKMV-001, H-BKK-001; 'EXP-BKKMV-002 m = 6 MV certificate + THM_BKKMV1') and ledger/decisions/DEC-20260722-003.yaml (GOAL-MLKEM-001) share one id. The note's premise check read the second; the first is the BKK decision.
  - No lead names BKK, mixed volume or Newton polytopes (grep of knowledge/leads/ecdlp). LEAD-ICE-prime-field-semaev-solving-degree already lists 'an eliminant or subresultant route' in its mechanism; its --match score 17 on the third phrasing (second to LEAD-ICP-digit-presentation-solving-degree 18, which is a base-B digit presentation, a different object).
- **Interpretation (conditional):**
  - Folding rather than a new lead (per advisor review of this fold): sparse elimination is another solver for the same dense composed-resultant object; if C1 holds, MV equals the dense multigraded Bezout number for every m, so the support-aware driver equals the dense driver and no exponent changes. Conditional on C1; proved only to m = 5, measured at m = 6.
  - Open cell worth a revisit_when: a level m >= 6 whose sectioned support is a proper subpolytope (refutes C1), or the unsectioned object, whose supports are measurably not box-saturated but whose MV was not computed.
- **Proposed diff:**

```
EDIT LEAD-ICE-prime-field-semaev-solving-degree
  ledger_refs += ["H-BKK-001", "H-BKKMV-001", "EV-BKK-001", "EV-BKKMV-001", "EV-BKKMV-002", "DEC-20260718-005", "DEC-20260718-011"]
  areas += ["BKK", "BKKMV"]
  forecloses += ["mixed volume sparse elimination of Semaev summation systems", "Newton polytope saturation of the Semaev family", "BKK bound below Bezout for summation polynomials"]
  evidence += {repo: crypto-autoresearcher, path: research/THM_BKKMV1.md, note: "Sectioned box-saturation PROVED for m <= 5 (MV_m = (m-1)! 2^((m-1)(m-2)) = box Bezout); all-m is conjecture C1 reduced to Lemma-G"}
  evidence += {repo: crypto-autoresearcher, path: research/THM_BKKMV2.md, note: "Theorem B (b-extremal non-cancellation) conditional on (T_m); bottom-fiber law; m = 4 covering case (0 of 125 fibers uncovered)"}
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-BKK-001.yaml, note: "Newton polytope = full box at m = 3, 4, 5 (54/54); sparse route 1.384x (m=3) and 5.537x (m=4) dense ops"}
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-BKKMV-002.yaml, note: "MV_6 = 125,829,120 on 6/6 instances, hull = box on 30/30 sections, p ~ 2^20"}
  evidence += {repo: crypto-autoresearcher, path: ledger/DEC-20260722-003.yaml, note: "Root-level legacy decision for H-BKKMV-001/H-BKK-001 (same id as ledger/decisions/DEC-20260722-003.yaml, a GOAL-MLKEM-001 record)"}
  append to obstruction.statement:
    + "Support-aware elimination: sectioned box saturation (so MV_m = (m-1)! 2^((m-1)(m-2)) = box Bezout) is proved for m <= 5 (THM_BKKMV1), measured for m = 6 on 6/6 instances (EV-BKKMV-002, p ~ 2^20), with the sparse route costing 1.384x / 5.537x the dense operations at m = 3 / 4 (EV-BKK-001); the all-m statement is conjecture C1 (Lemma-G open)."
  append to obstruction.revisit_when:
    + "A level m >= 6 at which the sectioned support is a proper subpolytope of the degree box (refutes C1), or an MV computation for the unsectioned object, whose supports are not box-saturated at m = 3, 4, 5."
  set mechanism (append):
    + "Support-aware (BKK / mixed-volume) elimination is the sparse variant of the same eliminant route: for the target-sectioned S_m the Newton polytope is the full degree box, so MV equals the dense multigraded Bezout number."

```

### 5. `knowledge/open-problems/KN-OPEN-005.md`

- **Action:** `advances_lead`; **lead:** LEAD-EXO-augmented-oracle-ggm (currently `closed_obstructed`); **record id:** KN-OPEN-005; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-005-a`; `OPEN-005-b`
- **Observation:**
  - Register question: is each non-generic representation (jets, elliptic nets, incidence) GGM-simulable with O(1) overhead; reconciliation note (2026-10-18): register stays open; DEC-20260804-4f37d5 = PARTIALLY_ADDRESSED ('technically open'); the owed KN-FIND (pending_kn_find_oracle_obstruction) was never made; claims DEC-20260722-004/-005/-006 do not bear on it.
  - On disk: ledger/DEC-20260722-004.yaml (root; H-JETB-001/H-JET-001 supported; 'THM_JETBARRIER1 theory note: simulation theorem for the jet-augmented generic group') and ledger/DEC-20260722-006.yaml (root; H-INCB-001/H-INC-001 supported; 'THM_INCBARRIER1 ... EC-chord richness ceiling'); ledger/decisions/DEC-20260722-004 and -005 are GOAL-ECDLP-001 BATCH-002 task records (supersede, expand) and ledger/decisions/ has no -006, which is what the note's premise check read; the root-level files share the ids.
  - research/THM_JETBARRIER1.md: T4 PROVED (every jet query in J(E, FB, r) simulable from public data with zero group-oracle overhead; Shoup bound lifts verbatim); T6 PROVED (boundary sharp: adding coordinate data of composite non-public elements collapses genericity); C2 (maximality of the simulable class) and G2 (Weil-restriction/descent scope) OPEN. research/THM_INCBARRIER1.md and THM_INCBARRIER2.md: chord-richness identities and phase diagram PROVED in the uniform-x model; fixed/adversarial-F certification at B = p^alpha, alpha <= 1/2 an OPEN GAP in THM1 (energy certificate and norm-ladder in THM2).
  - LEAD-EXO-augmented-oracle-ggm (closed_obstructed, kind theorem) already lists the jet, incidence, endomorphism, halving oracles and revisit_when 'a publicly computable oracle that is NOT GGM-simulable is exhibited'.
- **Interpretation (conditional):**
  - The lead's closure is per analysed oracle class (its own scope line: 'oracles, not resources'); the register question is the classification statement, which THM_JETBARRIER1 states as open (C2). Both readings are compatible: no row disposition change, add the theorem notes as evidence and make the scope explicit.
- **Proposed diff:**

```
EDIT LEAD-EXO-augmented-oracle-ggm
  ledger_refs += ["H-JETB-001", "H-INCB-001", "H-INC-001", "EV-INCB-001", "EV-JETB-001", "DEC-20260804-4f37d5"]
  related += ["LEAD-EXO-padic-jet-canonical-lift", "LEAD-EXO-elliptic-net-eds"]
  evidence += {repo: crypto-autoresearcher, path: research/THM_JETBARRIER1.md, note: "T4 PROVED: jet queries simulable with zero group-oracle overhead; T6 boundary sharp; C2 (maximality of the simulable class) and G2 (descent scope) OPEN"}
  evidence += {repo: crypto-autoresearcher, path: research/THM_INCBARRIER1.md, note: "EC-chord richness identities and uniform-x phase diagram PROVED; adversarial-F certification open (G1)"}
  evidence += {repo: crypto-autoresearcher, path: research/THM_INCBARRIER2.md, note: "Chord-profile identity, energy certificate, norm-ladder; exact cross-cancellation barrier"}
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-005.md, note: "Register entry for the general GGM-simulability question; stays open (DEC-20260804-4f37d5 PARTIALLY_ADDRESSED)"}
  evidence += {repo: crypto-autoresearcher, path: ledger/DEC-20260722-004.yaml, note: "Root-level legacy decision (H-JETB-001/H-JET-001 supported; THM_JETBARRIER1); same id as a GOAL-ECDLP-001 BATCH-002 record under ledger/decisions/"}
  evidence += {repo: crypto-autoresearcher, path: ledger/DEC-20260722-006.yaml, note: "Root-level legacy decision (H-INCB-001/H-INC-001 supported; THM_INCBARRIER1); no ledger/decisions/ counterpart"}
  append to obstruction.statement:
    + "Scope: each analysed oracle class; the classification question (is every public non-generic representation simulable) is open as THM_JETBARRIER1 conjecture C2 and register entry KN-OPEN-005, and is what revisit_when names."

```

### 6. `knowledge/open-problems/KN-OPEN-006.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICB-orbit-linear-algebra (currently `exhausted_at_scale`); **record id:** KN-OPEN-006; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-006-a`; `OPEN-006-b`
- **Observation:**
  - Register question: AP relation supports give O(1) displacement rank; does a superfast structured solve beat Wiedemann net of the AP hit-probability penalty. Note (2026-10-18): H-STR-002 weakened; EV-STR-001 (AP, contradicts, preliminary, n <= 4139).
  - On disk: ledger/H-STR-001.yaml status rejected_scoped (DEC-20260718-003): displacement rank grows linearly in B (alpha/B 0.56-0.77, generic maximum in 32/35 instances, identical to random baseline); AP relation-stage penalty 17.5x to 4128.6x against a 1.5x gate; AP tuples cover 3.3% to 13.2% of the group.
  - H-STR-002 (phi-orbit base, block-circulant): DEC-20260727-009 reports alpha = (27, 52, 197, 386) for the phi-invariant arm and (27, 52, 199, 387) for a random base at B = (27, 55, 204, 397) under the same shift/collection/no-append convention (scoped; mechanism not rejected); EV-STR-004 28/28 runs valid but 'No H-STR-002 mechanism test'.
  - docs/ic/LEADERBOARD.md (crypto, 'Phases, as a share of S'): linear algebra is 0.0%-0.4% of S in all eight Table B prime rows (log2 r 9.7-23.4) and 0.0%-2.7% over Tables A-C, the number LEAD-ICB-orbit-linear-algebra quotes.
  - Best --match: LEAD-ICB-orbit-linear-algebra 21 and 27 on the two phrasings (mechanism there: F_r[Z/n]-module structure of the Frobenius-folded matrix, binary Koblitz).
- **Interpretation (conditional):**
  - Conditional on the LA-share numbers, any LA-stage speed-up is bounded by <=0.4% of S at the measured prime sizes; the register's asymptotic question (larger B, where LA share may grow) is not decided, and the lead's revisit_when (10^6+ columns or a large-prime arm) already names that regime.
  - The mechanism (designed supports / phi-equivariant prime-field bases) differs from the lead's Frobenius-fold in setting but is the same cost argument; propose extending the lead's scope and forecloses rather than a new row.
- **Proposed diff:**

```
EDIT LEAD-ICB-orbit-linear-algebra
  ledger_refs += ["H-STR-001", "H-STR-002", "EV-STR-001", "EV-STR-004", "DEC-20260718-003", "DEC-20260727-009"]
  forecloses += ["arithmetic progression supports for low displacement rank", "Toeplitz or Hankel relation matrix by designed supports", "phi-orbit block-circulant relation matrix on j = 0 prime fields"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-006.md, note: "Register entry: designed (AP) supports -> displacement rank; prime fields"}
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-STR-001.yaml, note: "AP supports: displacement rank alpha ~ B (0.56-0.77 B), AP penalty 17.5x-4128.6x (H-STR-001 rejected_scoped, DEC-20260718-003)"}
  evidence += {repo: crypto-autoresearcher, path: problems/str002-support-verdict-missing-artifacts.md, note: "phi-invariant base alpha (27,52,197,386) vs random (27,52,199,387): scoped ablation; H-STR-002 weakened, not rejected"}
  append to obstruction.statement:
    + "Prime-field structured-support variants (arithmetic-progression supports; phi-orbit bases on j = 0) fall under the same phase argument: LA is 0.0%-0.4% of S in the eight Table B prime rows (log2 r 9.7-23.4); measured displacement rank grows like B for AP supports (EV-STR-001) and shows no phi-invariance gain under the shift convention (DEC-20260727-009 R2)."

```

### 7. `knowledge/open-problems/KN-OPEN-007.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-prime-field-semaev-solving-degree (currently `closed_known`); **record id:** KN-OPEN-007; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-007-a`; `OPEN-007-b`
- **Observation:**
  - Register question: do bond tensors of the recursive Semaev resultant tree have low rank, with recall-0.99 bond rank growing at exponent < 1 in the per-variable degree d = 2^(m-2); note (2026-10-18): toy scoped negative (m <= 6, p <= 1009), EV-TTN-001 weakens, EV-TTN-002 strengthens (m = 6 only), H-TTN-806b84 proposed.
  - EV-TTN-001 (weakens, preliminary): exact F_p bond ranks 3, 6, 15 at m = 3, 4, 5, identical in all 27 cells, field-size independent (beta = 0.000000), where full rank would be 3, 25, 81; chi_needed(recall >= 0.99) = chi_full in every cell (recall at chi_full - 1 is 0.0000 at m = 4); fitted exponent alpha = 1.160964 against the gate alpha < 1 (not crossed); ranks match the Sylvester multiset count C(2^(m-3)+2, 2).
  - EV-TTN-002 (strengthens, preliminary): chi(6) = 45 on the mechanism bond (rank <= 45 by construction, = 45 certified in 9/9 cells); on the balanced growth-family split at m = 6 the measured rank is 68 (not the face-value 45 and not the naive multiset count 70: one universal degree-4 syzygy). Statuses: ledger/H-TTN-001.yaml rejected_scoped (DEC-20260718-008), root DEC-20260722-002 supported_scoped (m = 6 certificate).
  - ledger/hypotheses/H-TTN-806b84.yaml (proposed): exact construction cost of the lossless chi(m)-term factorization against the dense composed resultant at m <= 6, counted in field operations, 'no exponent claim'.
  - No lead names tensor networks or bond rank; H-ECDLP-0fd4b9 (mapped to LEAD-EXO-lossy-object-propagation) merely cites KN-OPEN-007.
- **Interpretation (conditional):**
  - The measured low ranks are exact counts, not truncatable slack: recall collapses below chi_full. If the Sylvester count persists the growth exponent in d tends to 2 (EV-TTN-001's own extrapolation, untested for m >= 7). Conditional reading: contraction-based counting is not cheaper than dense at m <= 6.
  - The one open cell is a cost (not exponent) comparison: H-TTN-806b84. Record it as a revisit_when rather than a new lead (per advisor review of this fold); a proof of a border-rank lower bound is not on record.
- **Proposed diff:**

```
EDIT LEAD-ICE-prime-field-semaev-solving-degree
  ledger_refs += ["H-TTN-001", "H-TTN-806b84", "EV-TTN-001", "EV-TTN-002", "DEC-20260718-008"]
  areas += ["TTN"]
  forecloses += ["tensor train contraction of the Semaev resultant tree", "bond rank of Semaev summation polynomial tensors", "low rank factorization of the composed resultant"]
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-TTN-001.yaml, note: "Bond ranks 3, 6, 15 (m = 3..5, 27/27 cells) = C(2^(m-3)+2, 2); recall collapses below chi_full; alpha = 1.16 vs gate < 1"}
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-TTN-002.yaml, note: "chi(6) = 45 certified on mechanism bond; balanced split rank 68 (one universal syzygy)"}
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-007.md, note: "Register entry: tensor-train bond rank of the Semaev resultant tree"}
  evidence += {repo: crypto-autoresearcher, path: ledger/DEC-20260722-002.yaml, note: "Root-level legacy decision: H-TTN-001 supported_scoped, chi(6) = 45 certificate; same id as a GOAL-ECDLP-001 BATCH-001 record under ledger/decisions/"}
  append to obstruction.statement:
    + "Tensor-network contraction of the resultant tree: bond ranks equal the exact Sylvester multiset count (3, 6, 15, 45 at m = 3..6; 68 on the m = 6 balanced split), recall >= 0.99 needs chi_full, and the fitted exponent is 1.16 against the gate < 1 (toy, p <= 1009, m <= 6); if the count persists the exponent tends to 2."
  append to obstruction.revisit_when:
    + "m >= 7 bond ranks that fall below the Sylvester count with exponent < 1, or H-TTN-806b84 (exact construction-cost crossover of the lossless factorization against the dense resultant at m <= 6)."

```

### 8. `knowledge/open-problems/KN-OPEN-008.md`

- **Action:** `advances_lead`; **lead:** LEAD-RHO-generic-sqrt-lower-bound (currently `closed_obstructed`); **record id:** KN-OPEN-008; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-008-a`; `OPEN-008-b`
- **Observation:**
  - Register question: does a noncommutative word search find target-reaching relations the commutative subset-sum quotient misses; note (2026-10-18): scoped negative (word degree <= 6, p in {101, 431}); 'A proof of commutator collapse would close this by theorem; none is committed.'
  - research/THM_COMMUTATOR_KERNEL1.md (2026-07-18; check script 12/12 instances, 0 mismatches): PROVED (Theorems 1-2) for the single-vertex translation/negation quiver of a prime-field cyclic group that the evaluation kernel is the normal closure of the commutators, the forced dihedral torsion and the commutative subset-sum lattice, so every word relation descends to a signed-subset-sum relation of no larger l1 weight at any word degree, B and n; Proposition 1: the unqualified 'kernel = commutator ideal' is false (nu^2 - 1); Corollary 2 reproduces EV-NCP-001's strict inclusion (p = 431, B = 4: 350/439 vs 437/439). CONJECTURE 1: Frobenius-augmented quivers over extension fields. OPEN GAPS: multi-vertex isogeny-graph groupoids; the search-cost layer.
  - ledger/DEC-20260722-005.yaml (root; H-NCP-001 'supported'; refs the theorem note and EV-NCP-001): 'closed for prime fields by theorem'. ledger/decisions/DEC-20260722-005.yaml is a different (GOAL-ECDLP-001 BATCH-002) record under the same id. ledger/H-NCP-001.yaml status rejected_scoped (DEC-20260718-009). EV-NCP-001 (contradicts, replicated): 12/12 instances; NC cost per relation tracks n; 94,472 shadow replays, 0 value-set violations.
  - ledger/hypotheses/H-NCP-4cc527.yaml (proposed) restates the argument: the arrow group generated by translations and negation is virtually abelian, so word evaluation factors through the abelianization. No lead names quivers or path algebras (grep); best --match scores are <= 7 (LEAD-EXO-elliptic-net-eds, LEAD-RHO-generic-sqrt-lower-bound among them).
- **Interpretation (conditional):**
  - For the tested quiver every reachable word value is a signed subset sum, so the search is a generic-group algorithm and LEAD-RHO-generic-sqrt-lower-bound (Shoup/Nechaev) applies; this is conditional on the cost layer, which the theorem note lists as an open gap.
  - The register note's 'none is committed' is contradicted by the files above; what remains open is scope beyond the tested quiver (non-affine correspondences, isogeny groupoids, Frobenius-augmented quivers), not the translation/negation case.
- **Proposed diff:**

```
EDIT LEAD-RHO-generic-sqrt-lower-bound
  ledger_refs += ["H-NCP-001", "H-NCP-4cc527", "EV-NCP-001", "DEC-20260718-009"]
  areas += ["NCP"]
  forecloses += ["noncommutative path algebra word search for ECDLP relations", "quiver of translations and negation as relation source", "commutator collapse of word relations"]
  evidence += {repo: crypto-autoresearcher, path: research/THM_COMMUTATOR_KERNEL1.md, note: "PROVED: every word relation of the prime-field translation/negation quiver descends to a signed-subset-sum relation of no larger l1 weight; Frobenius-augmented and isogeny-groupoid cases open"}
  evidence += {repo: crypto-autoresearcher, path: ledger/DEC-20260722-005.yaml, note: "Root-level legacy decision recording the theorem (same id as a GOAL-ECDLP-001 BATCH-002 record under ledger/decisions/)"}
  evidence += {repo: crypto-autoresearcher, path: ledger/EV-NCP-001.yaml, note: "12/12 instances: NC cost per relation tracks n; value-set inclusion S_nc in S_comm, 0 violations of 94,472 replays (contradicts, replicated)"}
  append to obstruction.statement:
    + "Noncommutative word search over translations and negation is a generic algorithm: every reachable word value is a signed subset sum (THM_COMMUTATOR_KERNEL1, any word degree, B, n; prime-field cyclic group). Not covered: multi-vertex isogeny-graph groupoids, Frobenius-augmented quivers over extension fields (conjecture), and the search-cost layer."

```

### 9. `knowledge/open-problems/KN-OPEN-009.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-semaev-cover-monodromy (currently `closed_obstructed`); **record id:** KN-OPEN-009; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-009-a`; `OPEN-009-b`
- **Observation:**
  - KN-OPEN-009 front matter: superseded_by KN-OPEN-8a7432; KN-OPEN-8a7432 status open, superseded_by KN-OPEN-62c870; KN-OPEN-62c870 status open, superseded_by null, added 2026-10-22.
  - Reconciliation note (2026-10-18): a CLOSED disposition (DEC-20260804-4f37d5, monodromy C_2^{m-2}) and a later supersession reopening m >= 4 coexist; 'treat KN-OPEN-8a7432 as the live entry'; the ordered-base derivations are 'single-reviewer leads not re-derived by any committed record'.
  - LEAD-ICE-semaev-cover-monodromy (closed_obstructed, kind proof) cites KN-FIND-bdcd60 ('two blind re-derivations'), KN-FIND-4f0d84, GOAL-MONO-001 completed under DEC-20261022-a0f165 and KN-OPEN-62c870 as the live entry; --match score 34 on the first phrasing, next hit 11.
- **Interpretation (conditional):**
  - The note's reading is stale relative to files dated after it (KN-FIND-bdcd60, DEC-20261022-a0f165); the lead is already current. No disposition change; add the superseded register entries so a search from KN-OPEN-009 reaches the lead.
- **Proposed diff:**

```
EDIT LEAD-ICE-semaev-cover-monodromy
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-009.md, note: "Original register entry; superseded KN-OPEN-009 -> KN-OPEN-8a7432 -> KN-OPEN-62c870 (live); 2026-10-18 note predates KN-FIND-bdcd60 and DEC-20261022-a0f165"}

```

### 10. `knowledge/open-problems/KN-OPEN-010.md`

- **Action:** `new_mechanism`; **lead:** NEW: LEAD-EXO-koopman-transfer-operator; **record id:** KN-OPEN-010; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-010-a`; `OPEN-010-b`
- **Observation:**
  - Register question: can the leading spectrum of a coarse-grained transfer operator of the translation-by-P walk localize k below sqrt(n) total cost, or does character orthogonality force L = O(1). Note (2026-10-18): EV-TRA-001 weakens, C = 128 is not a full-resolution test, H-TRA-4344b7 proposed, 'no separate decision' located for H-TRA-001.
  - On disk: ledger/H-TRA-001.yaml status rejected_scoped (DEC-20260718-007: L = O(1), growth exponent 0.0195). EV-TRA-001: L_eff means 1.667 / 1.555 / 1.778 against chance floors 1.385 / 1.304 / 1.579 at p = 211 / 1009 / 4099 (S = n^(1/4)); positive control (C = n recovers k) 18/18; random-permutation negative control 50 hits vs 50.35 chance; all 54 exact coarse operators exactly reversible (detailed-balance residual 2.5e-17, max |Im lambda| 3.7e-16).
  - EV-TRA-001 unresolved confounds: 'non-negation-symmetric partitions and multi-mode estimators untested; reversibility obstruction is measured (and symmetry-argued) for x-cells, not proved for all partitions'. H-TRA-4344b7 (proposed) Part A: exact C x C operators on (x-interval, sign of y) cells and one non-symmetric family; Part B (conditional): L growth above 0.0195 (its own prior: 0.10).
  - No lead names transfer operators or Koopman spectra. The only lead holding H-TRA-4344b7 is LEAD-RHO-r-adding-walk-mixing (mechanism: rho iteration-function walk constant), a different object.
- **Interpretation (conditional):**
  - Best hit not the same mechanism: --match top hits are LEAD-RHO-lhw-polymem-collision-walks (11) and LEAD-EXO-dl-character-sum-pseudorandom (10) on the first phrasing; the first is a weight-w collision walk, the second an additive-character bias of DL on factor bases; neither estimates a spectrum of a coarse-grained walk operator to localize k.
  - Observation vs reading: the reversibility/real-spectrum result is a property of the partition tested; whether the barrier is partition-general or specific to the +/- fold is the discriminating cell (Part A is exact linear algebra at toy n). A conditional reading is that phases appearing with L flat would be a more general barrier statement than the one committed.
- **Proposed diff:**

```
(new row; full YAML in section 'Proposed new rows')

EDIT LEAD-RHO-r-adding-walk-mixing
  ledger_refs -= ["H-TRA-4344b7"]
  areas -= ["TRA"]

```
- **Dependency on a new row:** Removing H-TRA-4344b7 and area TRA from LEAD-RHO-r-adding-walk-mixing depends on adopting the new row LEAD-EXO-koopman-transfer-operator, which takes them over; if the new row is rejected, leave that lead unchanged.

### 11. `knowledge/open-problems/KN-OPEN-5b3a08.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-decomposition-probability-audit (currently `open_next_step`); **record id:** KN-OPEN-5b3a08; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-5b3a08-a`; `OPEN-5b3a08-b`
- **Observation:**
  - Q1 (code): pre-repair s4_expr (non-simultaneous subs) drops x3; repaired in harness/semaev.py (CORR-20260813-d9f0fa); docs/reports/2026-10-18-semaev-s4-factor-base-audit.md: repaired s4_expr vanishes exactly on +-P1+-P2+-P3+-P4 = O over all 6561 tuples (F_13) and 1296 (F_11); legacy construction fails 2353/6561 and 648/1296.
  - Q1 (exposure, audit table): EXP-MTIC-001 11 runs and EXP-FIB-001 10 runs recorded commits lacking the repair; a third consumer is RUN-ICINV-e0cd8f-m3class whose archived m4 columns (s4_support 227 in 274 of 276 records) differ from 439 recomputed on two sample curves at p = 4001; its m3 columns use s3_expr and are unaffected; RUN-ICINV-geom-* and EXP-DTREE-001 (local semaev_fix.py) are listed as not affected.
  - Matched reruns: DEC-20261018-a7a0fd approves EXP-SEMAEV-93d5cc (7 trials); DEC-20261019-5b9240 and DEC-20261019-ebf1dc record trials 1-6 output_validated and move the 7th cell (mtic-010b) to successors EXP-SEMAEV-88c46c then EXP-SEMAEV-6e9dcf after two worker restarts. H-SEMAEV-94dab2 remains approved in ledger/hypotheses (not characterized further here).
  - Q2: build_factor_base default scope=full_curve draws from E(F_p), not <P>; scope='target_subgroup' now exists; no archived caller opts in. EV-DTREE-2e8f6a measured P(m=3,B) = 0.0, 0.32, 0.0 at 16/20/24 bits (0/50, 16/50, 0/50) against HEUR-001's (B/N)^2 point predictions 0.047, 0.000239, 0.003; cofactors 2280, 196, 31512.
  - Lead usage check (grep of knowledge/leads/ecdlp): no lead cites EXP-MTIC-001, EXP-FIB-001 or the m4 columns; LEAD-ICE-curve-presentation-invariance and LEAD-STR-isogeny-class-generic-invariance list EV-ICINV-8afb64 (the m3class run) in ledger_refs, and their stated clauses are S_3 / length-2 yield / generic rho.
- **Interpretation (conditional):**
  - No lead field depends on the affected s4_support columns, so no obstruction or best_measured is invalidated by Q1; the numerical effect on the 21 runs and the m4 columns remains unmeasured/unreviewed. A caveat on the ICINV evidence entries avoids a later reader citing the m4 columns.
  - Q2 bears on LEAD-ICE-decomposition-probability-audit: its next_action (BATCH-79a580, exact count vectors c_D against a size-matched random base) should state the factor-base scope per fixture; whether cofactor size drives the EXP-DTREE-001 pattern is not isolated by any run (the experiment designed to isolate it hit design_infeasible).
- **Proposed diff:**

```
EDIT LEAD-ICE-decomposition-probability-audit
  ledger_refs += ["CORR-20260813-d9f0fa", "DEC-20261018-a7a0fd", "EV-DTREE-2e8f6a"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-5b3a08.md, note: "Shared-harness caveats: Q1 s4_expr defect (repaired; effect on MTIC/FIB/ICINV-m4 runs unmeasured), Q2 full_curve factor-base scope vs cofactor"}
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-18-semaev-s4-factor-base-audit.md, note: "Audit: repaired s4_expr exact on 6561 + 1296 tuples; exposure table; target_subgroup scope added; no caller opts in"}
  append to next_action.step:
    + "State build_factor_base scope (full_curve default vs target_subgroup, KN-OPEN-5b3a08 Q2) for every fixture, and use the repaired s4_expr (CORR-20260813-d9f0fa) for any m >= 3 chain."

EDIT LEAD-ICE-curve-presentation-invariance
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-18-semaev-s4-factor-base-audit.md, note: "Caveat for EV-ICINV-8afb64: RUN-ICINV-e0cd8f-m3class m4 columns (s4_support) used the pre-repair s4_expr; its m3 columns and RUN-ICINV-geom-* are unaffected; matched reruns EXP-SEMAEV-93d5cc pending review"}

EDIT LEAD-STR-isogeny-class-generic-invariance
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-18-semaev-s4-factor-base-audit.md, note: "Caveat only: EV-ICINV-8afb64 (in ledger_refs) comes from RUN-ICINV-e0cd8f-m3class, whose m4 columns used the pre-repair s4_expr; this lead's generic rho/BSGS clauses do not use them"}

```

### 12. `knowledge/open-problems/KN-OPEN-d3a6f0.md`

- **Action:** `new_mechanism`; **lead:** NEW: LEAD-TRF-torsion-section-digit-fourier; **record id:** KN-OPEN-d3a6f0; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `OPEN-d3a6f0-a`; `OPEN-d3a6f0-b`
- **Observation:**
  - KN-OPEN-d3a6f0 (status OPEN, added 2026-10-23): Q1 growth exponent of Phi_i(n) = max_t max_j |(1/n) sum_k e(t a_i(c(s_tor([k]P)))/p) e(-jk/n)| for i = 1..4 (uniform-random model predicts about sqrt(ln(pn)/n), exponent -1/2); Q2 Weil-type bound (digit 0: O(sqrt p) subgroup-sum cancellation, Lange-Shparlinski via Farashahi-Shparlinski arXiv:1005.4771 Lemma 5, reported; i >= 1: 'No bound is known'); Q3 consequence: s_tor is a computable homomorphism so g has exact shift-query access, a heavy coefficient tau gives chi_j(d) from about tau^-2 queries, breakeven about tau* = n^(-1/4) up to polylog (RT-20261023-dcb217 order-of-magnitude estimate).
  - DEC-20261023-2e7447 (refine): EV-CZLIFT-764f54 supports a narrow statement at preliminary strength, toy tier: on 42 power-bearing records (33 CM-canonical class-number-one models, 9 random curves, 53 <= p <= 571, 47 <= n <= 613, precision 5) no single-digit function a_i(x or y of s_tor([k]P)), i = 0..4, has half-range normalised correlation tau >= rho_min in [0.28, 0.98] (median 0.50); the 30 records with n <= 41 carry no information; H-CZLIFT-fba874 approved -> analyzed; successor work NA-4 (measurement) and NA-6 (Weil-type bound).
  - The record states why the formal-log closure does not answer it: KN-TECH-73630e covers group-theoretic invariants only, 's_tor is a group isomorphism onto its image, and the formal logarithm vanishes on torsion, so any gain must come from the encoding'; it sharpens KN-OPEN-3417fc (invertible coordinate functional).
  - Lead mapping: coverage.tsv maps H-CZLIFT-fba874 to LEAD-TRF-padic-canonical-section (closed_obstructed), whose forecloses includes 'p-adic digits of the torsion section' and whose theorem-kind obstruction is the formal-log / homomorphic-section argument. The 'digit-character family' in LEAD-EXO-coordinate-statistic-leakage's next_action (IDEA-20260921-1ec106) is the Thue-Morse / Rudin-Shapiro signs of the integer lift of an x-coordinate, not p-adic digits of lifts.
- **Interpretation (conditional):**
  - Best hit not the same mechanism: LEAD-TRF-padic-canonical-section (14 and 8 on the two phrasings) is closed for the linear (formal-log) readout and the identity readout of three sections; the Fourier-level readout of digits i >= 1 of s_tor is explicitly outside both (the record says so) and is an open runnable question with named next actions. LEAD-EXO-hnp-advice-leakage (6) is blocked on having a measured statistic; LEAD-EXO-dl-character-sum-pseudorandom (7) concerns DL characters on factor bases.
  - A closed_obstructed row that contains an open, runnable sub-question conflicts with README rule 1; the narrower, lower-loss edit is to split: keep the closure scoped to the linear channel and open a sibling lead whose next_action is NA-4. The a-priori model (exponent -1/2, far below -1/4) makes a negative outcome the likely reading, which is why the question is cheap to decide definitively at toy scale rather than closed by assertion.
  - The toy floor (tau >= 0.28-0.98) is about 50 bits of correlation from the attack regime by the red team's estimate; it says nothing about the exponent.
- **Proposed diff:**

```
(new row; full YAML in section 'Proposed new rows')

EDIT LEAD-TRF-padic-canonical-section
  ledger_refs += ["EV-CZLIFT-764f54", "DEC-20261023-2e7447", "EXP-CZLIFT-1a3453"]
  related += ["LEAD-TRF-torsion-section-digit-fourier"]
  forecloses += ["formal logarithm readout of the torsion section", "homomorphic section other than the torsion section"]
  forecloses -= ["p-adic digits of the torsion section"]
  evidence += {repo: crypto-autoresearcher, path: knowledge/open-problems/KN-OPEN-d3a6f0.md, note: "Digit-character Fourier mass of s_tor (i >= 1) is OPEN: split to LEAD-TRF-torsion-section-digit-fourier"}

```
- **Dependency on a new row:** Every entry on LEAD-TRF-padic-canonical-section in this row (related +=, forecloses -= 'p-adic digits of the torsion section', the coverage remap) depends on adopting the new row LEAD-TRF-torsion-section-digit-fourier; if the new row is rejected, keep that phrase in forecloses and drop the related entry. The refs and evidence entries are independent.
- **coverage.tsv:** remap `H-CZLIFT-fba874` from `LEAD-TRF-padic-canonical-section` to `LEAD-TRF-torsion-section-digit-fourier`.

### 13. `problems/README.md`

- **Action:** `not_ecdlp`; **lead:** none; **record id:** problems/README.md; **ECDLP record:** no (coverage row NONE)
- **Observation:**
  - problems/README.md is the index of named blockers ('This index does not assert that all repository obstructions are recorded'). Rows relevant to ECDLP leads point to files folded individually below (e.g. semaev-degree-two..., full-width-ic-arity-grid..., ectd-arity3...). The index also lists records outside this group (FROB C8 recheck, BINSTD n=17 Lean bridge) that are not in the delta for this group.
- **Interpretation (conditional):**
  - Coverage row: none (not an H-* or IDEA-* record). No lead field is derived from the index itself.
- **Proposed diff:** none of its own.

### 14. `problems/dreg-c1-memory-cap-exhausted.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-chained-semaev-dreg-vs-semiregular (currently `open_next_step`); **record id:** problems/dreg-c1-memory-cap-exhausted.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `dreg-c1`
- **Observation:**
  - All six required (seed, arm) runs ended failed_infrastructure / resource_exhaustion before the rank kernel ran; prepare-phase peak 11.73 GiB (semaev arm) and 12.22 GiB (null arm) at seed 2026 against a lane contract of memory_gb 8 (+46.6% and +52.75%). Independent validator VAL-20260828-001 passed on all five joints.
  - DEC-20261005-8d23bb raised the floor from 8 to 16 GiB and carded the retry as TASK-20261005-821d86; 'As of origin/main f279a4918c no run output for it is committed.' Whether 16 GiB covers the unmeasured rank phase is stated as unknown.
  - Lead today: next_action 'Re-run item C1 (n = 15, D = 6, seeds as frozen) with a streaming native Macaulay builder (IDEA-20260828-770aa4) under the lane's memory floor'; best_measured ends 'n = 15 D = 6 runs failed at 11.7-12.2 GiB'. --match score 30 on the lead (next hit 14).
- **Interpretation (conditional):**
  - The lead already states the situation; the edit makes the floor change and the 'no result' status explicit. A resource stop is not a d_reg measurement (the problem record and AGENTS.md rule 5 say so). Disposition open_next_step unchanged.
- **Proposed diff:**

```
EDIT LEAD-ICE-chained-semaev-dreg-vs-semiregular
  ledger_refs += ["DEC-20261005-8d23bb", "DEC-20260828-653923"]
  evidence += {repo: crypto-autoresearcher, path: problems/dreg-c1-memory-cap-exhausted.md, note: "C1 stopped on its memory cap: 0/6 runs completed_valid, prepare peak 11.73/12.22 GiB vs 8 GiB; floor now 16 GiB (DEC-20261005-8d23bb), retry TASK-20261005-821d86 carded, no output committed; not a d_reg measurement"}
  reword next_action.step:
    - "under the lane's memory floor"
    + "under the lane's memory floor (raised 8 -> 16 GiB by DEC-20261005-8d23bb; TASK-20261005-821d86 carded, no run output committed at origin/main f279a4918c; coverage of the unmeasured rank phase by 16 GiB unknown)"
  reword best_measured:
    - "n = 15 D = 6 runs failed at 11.7-12.2 GiB"
    + "n = 15 D = 6: all 6 (seed, arm) runs failed_infrastructure before the rank kernel (prepare peak 11.73 / 12.22 GiB vs 8 GiB cap); no n = 15 rank exists"

```

### 15. `problems/dtree-slope-grid-design-infeasible.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICP-residual-partial-relations (currently `open_next_step`); **record id:** problems/dtree-slope-grid-design-infeasible.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `dtree-a`; `dtree-b`; `dtree-c`
- **Observation:**
  - RUN-DTREE-001/002: 0 qualifying cells among 18 (curve, B') values; subgroups n = 23, 19, 31 on the 8/10/12-bit curves, and the grid needs n >= 80 (necessary and sufficient given B' >= 8: 56/0.7); EV-DTREE-b47c19 classifies it 'design_infeasible', 'no result on HEUR-001 at all'.
  - EV-DTREE-2e8f6a (inconclusive): P(m=3,B) = 0.0 (0/50), 0.32 (16/50), 0.0 (0/50) at 16/20/24 bits so the single-level baseline C1 is undefined at two sizes; 16-bit depth-2 found 38 stage-1 decompositions in 5 of 8 configs and every stage-2 attempt failed (stage2_found = 0 in all 5; the record's own totals, 59 in one sentence and per-config counts 6+4+45+9+45 in another, disagree); 20-bit depth-2 failed the validity prefix (n1 = 3-4 of 50 planned, 1500 s cumulative cap); every defined C2 exceeded C1 (20-bit), recorded as 'resource_exhaustion (recorded, not evidence)'. H-DTREE-001 status inconclusive (DEC-20260809-91d4c7). The experiment used its own semaev_fix.py, so the s4_expr defect does not apply to it.
  - Mechanism (H-DTREE-001): decompose Q + [t]P over an enlarged medium base F_med (B_med in {2B, 4B, 8B, 16B}, arity m' in {2, 3}) and then each medium element over F; the hypothesis calls it 'the ECDLP analogue of the NFS descent tree and of large-prime variants in extension-field index calculus'.
  - No lead names descent trees or medium bases (grep 'DTREE', 'medium base'); best --match on the three phrasings: KR-IC-5931ee (27), LEAD-ICB-cofactor-torsion-quotients (22), LEAD-ICP-coppersmith-smallroot-semaev (20), LEAD-ICP-residual-partial-relations is the closest mechanism by content (large-prime variation) though it scores low lexically.
- **Interpretation (conditional):**
  - Conditional fold, with a caveat the reviewer should check: LEAD-ICP-residual-partial-relations is about crediting residual x-coordinates as partial relations during table building, while the depth-2 tree decomposes each target through a medium base (a descent step). They share the large-prime/descent idea and the 'does an enlarged base pay for its second stage' accounting; if the reviewer judges them distinct, the alternative is a new ic-prime row. Neither run family is evidence (resource-exhausted or design-infeasible), so no best_measured or disposition changes.
  - The record's open discriminators are cheap to state: a seed-policy amendment (n >= 80) or successor, and a matched full_curve versus target_subgroup arm (now possible via KN-OPEN-5b3a08).
- **Proposed diff:**

```
EDIT LEAD-ICP-residual-partial-relations
  ledger_refs += ["H-DTREE-001", "EV-DTREE-b47c19", "EV-DTREE-2e8f6a", "EXP-DTREE-001"]
  areas += ["DTREE"]
  forecloses += ["depth-2 descent tree through a medium factor base", "enlarged medium base two-stage decomposition for prime-field ECDLP"]
  evidence += {repo: crypto-autoresearcher, path: problems/dtree-slope-grid-design-infeasible.md, note: "Depth-2 medium-base descent tree: C1 slope grid design_infeasible (0/18 cells, n = 19-31); not a result; successor needs n >= 80 and matched full_curve/target_subgroup arms"}
  evidence += {repo: crypto-autoresearcher, path: ledger/evidence/EV-DTREE-2e8f6a.yaml, note: "C2 inconclusive: baseline undefined at 16/24 bits, 20-bit validity prefix failed (resource_exhaustion); recorded, not evidence"}
  set mechanism (append):
    + "A depth-2 descent tree through an enlarged medium base F_med (decompose the target over F_med, then each medium element over F) is the per-target variant of the same large-prime idea; H-DTREE-001 is inconclusive (design_infeasible slope grid, resource-exhausted depth-2 runs)."

```

### 16. `problems/ectd-arity3-panel-infrastructure-loss.md`

- **Action:** `advances_lead`; **lead:** LEAD-TRF-teske-secret-isogeny-trapdoor (currently `open_next_step`); **record id:** problems/ectd-arity3-panel-infrastructure-loss.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `ectd-a`
- **Observation:**
  - Problem record: only 3 arms have output_validated receipts (P37-floor-u2-native, P29-E2-native, P29-E3-native); 11 arms infrastructure_error ModuleNotFoundError psutil, 2 arms 'cannot read resident memory for process', 4 u2-transport arms waiting_on_dependencies; failed attempts neither overwritten nor imputed; recovery amendment is a draft (experiments/EXP-ECTD-0cf008/amendments/recovery-20261016-draft.json, 17-arm additive plan).
  - Directly verified in experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/data.json: status counts {output_validated: 3, infrastructure_error/psutil_import_missing: 11, infrastructure_error/rss_sampling_failure: 2, waiting_on_dependencies: 4} across 20 trials.
  - LEAD-TRF-teske-secret-isogeny-trapdoor today: next_action 'every trial of run-20261016T0409Z died with psutil_import_missing' and an evidence note '20-arm panel: all trials infrastructure_error' (both for the same data.json). LEAD-ICP-isogeny-transported-relation-yield already says 'Finish the 17 missing arms' and cites problems/prime-field-arity3-relation-oracle.md ('3 of 20 arms valid').
  - problems/isogeny-graph-wide-relation-solver.md reports the two valid E2/E3 arms as RUN-ECTD-c769f1 (2,204/32,768 useful targets) and RUN-ECTD-f395a9 (2,191/32,768) with 99.75% intervals [0.063148, 0.071545] and [0.062762, 0.071136], 'this secondary result has not received an evidence review'; the E1 primary and both E2/E3 random arms ended in infrastructure errors.
- **Interpretation (conditional):**
  - The Teske lead's two statements are contradicted by the file it cites; the 3 valid arms give no native/random or crater/floor comparison, so best_measured is unchanged and the discriminating panel remains open (17 arms). Edits are factual corrections plus a cross-reference.
- **Proposed diff:**

```
EDIT LEAD-TRF-teske-secret-isogeny-trapdoor
  ledger_refs += ["EXP-ECTD-0cf008"]
  evidence += {repo: crypto-autoresearcher, path: problems/ectd-arity3-panel-infrastructure-loss.md, note: "3 of 20 arms output_validated; 17 lost to infrastructure (11 psutil, 2 RSS sampling, 4 waiting_on_dependencies); recovery amendment drafted, not approved"}
  reword next_action.step:
    - "every trial of run-20261016T0409Z died with psutil_import_missing"
    + "of the 20 trials of run-20261016T0409Z 3 are output_validated (P37-floor-u2-native, P29-E2-native, P29-E3-native), 11 died with psutil_import_missing, 2 with rss_sampling_failure and 4 u2-transport arms wait on dependencies; finish the 17 missing arms after the Coordinator-approved additive recovery amendment with a runtime preflight"
  reword evidence[experiments/EXP-ECTD-0cf008/reports/run-20261016T0409Z/data.json].note:
    - "20-arm panel: all trials infrastructure_error"
    + "20-arm panel: 3 output_validated, 17 infrastructure/dependency losses; no native/random or crater/floor comparison"

EDIT LEAD-ICP-isogeny-transported-relation-yield
  evidence += {repo: crypto-autoresearcher, path: problems/ectd-arity3-panel-infrastructure-loss.md, note: "Specific record for the 17 lost arms of EXP-ECTD-0cf008 (opened 2026-10-18); blocked_by file problems/prime-field-arity3-relation-oracle.md covers the Coordinator backend limit"}

```

### 17. `problems/finite-worksheet-direct-invocation.md`

- **Action:** `unclear`; **lead:** none; **record id:** problems/finite-worksheet-direct-invocation.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `finite-worksheet`
- **Observation:**
  - Original RUN-ECDLP-f67842 receipt: infrastructure_error, return 1, no checker invocation; stderr 'current invocation differs from the actual supervisor command'. Six metadata-only successors in BATCH-e7e584 preserve all scientific source/config/spec hashes and use direct argv. EXP-ECDLP-c0c520 has two actual output_validated primary-route receipts; EXP-ECDLP-615fcf retained a distinct native invalid_output (final checker Git status refused: 'unable to create threaded lstat'), 13 real files preserved; DEC-20261018-1a5209 declares the Git-only variables on the outer supervisor environment; EXP-ECDLP-53b1c3 is a fresh review_required successor.
  - Mapping through coverage.tsv: EXP-ECDLP-c0c520 -> H-ECDLP-7bd5f5 -> LEAD-EXO-four-list-ktree-join; EXP-ECDLP-615fcf/-53b1c3 -> H-ECDLP-242aa4 -> LEAD-ICP-icperf-binary-pdp-solver. Neither lead cites those hypotheses or experiments (grep of knowledge/leads/ecdlp).
- **Interpretation (conditional):**
  - Execution-integrity record for fixed toy worksheets (record states 'not a mathematical negative'); it changes no mechanism, obstruction, evidence or next_action of any lead. Marked unclear rather than not_ecdlp because the experiments are ECDLP-area and are mapped to leads.
- **Proposed diff:** none of its own.

### 18. `problems/formal-target-semantic-fidelity-unreviewed.md`

- **Action:** `advances_lead`; **lead:** LEAD-EXO-methodology-instruments (currently `open_next_step`); **record id:** problems/formal-target-semantic-fidelity-unreviewed.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `formal-target`
- **Observation:**
  - At main d513b75 all 83 target specs have theorem files and the main workspace (652 theorems, standard axioms only) builds; at main 969e051 there are 84 targets (656 theorems); full per-target machine check at 1c572eb: all 84 receipts passed. The record states these establish 'kernel acceptance and the declared theorem names' existence', not scientific claim fidelity; semantic review per claim is open.
  - Concrete gap: the batch-five target is conditional on three large factors being prime and does not prove trace identity, End(E) = O_K or field/order primality; its README nevertheless states End(E) = O_K. Known counterexample to the shortcut 'it compiles, so the claim holds': the Semaev degree-two trace theorem versus the nonzero-target first-fall interpretation (problems/semaev-degree-two-fall-nonzero-bridge.md).
  - LEAD-EXO-methodology-instruments (open_next_step) covers 'findings-promotion gate and ... record integrity' and decides 'whether other leads' negatives and positives are trustworthy'; the two leads that cite Lean (batched-inversion, automorphism-class-walks) cite correctness proofs of rho components, not cryptanalytic claim targets.
- **Interpretation (conditional):**
  - Cross-cutting evidence-quality statement; no obstruction in any lead rests on the unreviewed cryptanalytic targets (grep of formal/ in leads: only LEAD-ICE-first-fall-degree-assumptions and two rho leads). Evidence entry on the methodology lead only.
- **Proposed diff:**

```
EDIT LEAD-EXO-methodology-instruments
  forecloses += ["Lean target compiles therefore the experimental claim is proved"]
  evidence += {repo: crypto-autoresearcher, path: problems/formal-target-semantic-fidelity-unreviewed.md, note: "Lean build and axiom audit of 83-84 targets is machine verification, not semantic sign-off; claim-to-theorem coverage and independent review open"}

```

### 19. `problems/frob-c5-factor-kernel-and-model-bridge.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICB-frobenius-orbit-factor-base (currently `closed_obstructed`); **record id:** problems/frob-c5-factor-kernel-and-model-bridge.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `frob-c5-a`
- **Observation:**
  - Proved in Lean (all with standard axioms; independent semantic review pending): X^5 - 1 factorizations for the three canonical degree-five fields (q=11 four linear, q=13 one quartic, q=19 two quadratics), irreducibility, direct sum of non-trivial factor kernels = trace kernel of dimension four; exact 5x5 q-power matrices in the three archived quotient bases (75 entries); factor-kernel sums on those matrices; the full q-power endomorphism equals the matrix; quotient-level fifth-power and fixed-line controls; characteristic-five negative control (X^5 - 1 not squarefree over ZMod 5).
  - Open per the record: check the historical Sage field construction and kernel paths against the proved model, original execution-source custody, modulus irreducibility at the formal field level, independent semantic and code review; C8 and the experiment success gate are separate. Executable evidence (core-object replay, source-bound matrix replay) is stated to be 'not a Lean refinement proof of the historical code'.
  - LEAD-ICB-frobenius-orbit-factor-base (closed_obstructed, kind proof) states 'the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q' and already lists H-FROB-d93575 in ledger_refs (the EXP-FROB-91ee9c hypothesis).
- **Interpretation (conditional):**
  - The Lean results give formal support, at n = 5 for three fields, to the factorization-lattice statement the lead's proof obligation uses; the historical-run verdict (C5) is not promoted. No obstruction or disposition change; add the report and target as evidence with the open bridge stated.
- **Proposed diff:**

```
EDIT LEAD-ICB-frobenius-orbit-factor-base
  ledger_refs += ["EXP-FROB-91ee9c"]
  evidence += {repo: crypto-autoresearcher, path: problems/frob-c5-factor-kernel-and-model-bridge.md, note: "C5 factor kernels proved in Lean for q = 11, 13, 19 (n = 5), exact quotient matrices, full map, controls; historical Sage bridge, source custody and semantic review open"}
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-22-frob-c5-factor-kernels/REPORT.md, note: "Factor-kernel proof report with exact-source receipts"}

```

### 20. `problems/full-ledger-validation-errors.md`

- **Action:** `advances_lead`; **lead:** LEAD-EXO-methodology-instruments (currently `open_next_step`); **record id:** problems/full-ledger-validation-errors.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `full-ledger`
- **Observation:**
  - tools/validate_ledger.py exits 1 on main e20013a with 162 unsuppressed error lines in 49 paths (1,210 grandfathered errors suppressed; 543 advisories): 66 prior-art metadata, 32 review/handoff fields, 28 citation provenance, 19 run-manifest schema, 7 broken references, 5 zero-compute-stage artifacts, 5 experiment-spec fields. 'These are mechanical failures requiring record-by-record review, not 162 established false scientific conclusions.'
  - ECDLP-specific items: RUN-QSP-33b442-S0 is a hand-derivation Stage 0 filed in the run namespace (declares no program ran; the validator requires command capture, environment, stdout, stderr, raw result). RUN-FROB-91ee9c-7119f2: pre-run code.head_commit does not contain the archived implementation.py; hash-matched artifacts reproduce the archived checker byte for byte but 'cannot identify the implementation bytes that produced the original outputs'; its tuple_sum_reverifications check three of six curves (the rest skipped for size).
  - LEAD-ICB-quasi-subfield-polynomials cites EV-QSP-2c78d3, which belongs to EXP-QSP-70b731 (not EXP-QSP-33b442). LEAD-ICB-frobenius-orbit-factor-base cites H-FROB-d93575 (EXP-FROB-91ee9c).
- **Interpretation (conditional):**
  - The general count is methodology-lead material (record integrity). The one lead-specific consequence is a custody caveat on any statement resting on the frozen RUN-FROB-91ee9c-7119f2 verdicts; the lead's obstruction cites other hypotheses (H-FROB-6774fb, DEC-20260923-e6cd5d), so no obstruction change. No QSP lead field depends on RUN-QSP-33b442-S0.
- **Proposed diff:**

```
EDIT LEAD-EXO-methodology-instruments
  forecloses += ["clean ledger integrity gate for the whole corpus"]
  evidence += {repo: crypto-autoresearcher, path: problems/full-ledger-validation-errors.md, note: "Full-corpus validator: 162 unsuppressed errors in 49 paths on audited main; mechanical, not scientific conclusions; clean-gate claim unsupported"}

EDIT LEAD-ICB-frobenius-orbit-factor-base
  evidence += {repo: crypto-autoresearcher, path: problems/full-ledger-validation-errors.md, note: "Custody caveat: RUN-FROB-91ee9c-7119f2 pre-run commit lacks the archived implementation.py; archived checker replays byte for byte but original code bytes unidentified"}

```

### 21. `problems/full-width-ic-arity-grid-unmeasured.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICP-full-width-arity-grid (currently `open_blocked`); **record id:** problems/full-width-ic-arity-grid-unmeasured.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `fullwidth-a`
- **Observation:**
  - Record status investigating; kind implementation gap, resource limit, missing measurement; 'No mathematical obstruction is claimed'. Prime complete-solve arity ladder stops at 32 bits and m = 7 (compact numpy path); Koblitz N53 is a 53-bit field with a 45-bit prime subgroup; exact screening of the two standard binary Koblitz curves at field degrees 50-63 finds no prime subgroup of order at least 2^50.
  - Prepared inputs (not measurements): certified 50/53/63-bit prime fixtures; 380-point and 475-point (seed 20261027) 63-bit coset bases with m = 2..8 chained-S3 systems; equal-size random/small-x controls; ordinary-binary GF(2^61) fixture with 249/265/267/316-column bases and XCNF inputs; sorted 64-bit collision store. Exact signed-multiset ceilings: 0.323848% of uniform targets at m = 7 and 31.048916% at m = 8 on the 380-point base; 0.004432 (m = 7) and 0.299713 (m = 8) at B = 267 on the binary base.
  - Runs: 2026-10-18 RUN-ICPERF-7ed866 attempted 7 of 27 cells (6 planted positives hit 300 s caps; first natural cell rss_monitor_unavailable_for_live_child; 20 unattempted); 2026-10-19 RUN-ICPERF-eb0d88 (three-cell m = 2 diagnostic): three timeout_censored at 600 s, supervisor invalid_output (missing top-level manifest.yaml / raw-result.json). Structural obstruction record: problems/binary-subfield-base-has-no-large-prime-component.md.
  - Lead today: open_blocked, blocked_by this file; best_measured 'prime complete-solve arity ladder stops at 32 bits and m = 7; 63-bit second run: six time-censored planted controls, one monitor-error cell'; evidence lists this file and the monitor problem but not the output-contract or binary-subfield records. --match score 28.
- **Interpretation (conditional):**
  - blocked_by remains accurate. The lead's best_measured omits the later diagnostic; censored and invalid-output cells are not evidence about the formulations (timeout is not an obstruction). The title's 'Koblitz orbit at 50-63-bit subgroups' needs the size-coordinate correction.
- **Proposed diff:**

```
EDIT LEAD-ICP-full-width-arity-grid
  ledger_refs += ["DEC-20261018-eb6e00", "DEC-20261017-8ae5ea", "EXP-ICPERF-515ae3", "EXP-ICPERF-891f7f"]
  evidence += {repo: crypto-autoresearcher, path: problems/icperf-prime63-m2-output-contract-mismatch.md, note: "m=2 diagnostic: checker integrity_pass but supervisor invalid_output (plan requires top-level manifest.yaml / raw-result.json, launcher writes diagnostic/receipt.json); three 600 s censors"}
  evidence += {repo: crypto-autoresearcher, path: problems/binary-subfield-base-has-no-large-prime-component.md, note: "Structural obstruction: a direct proper-subfield x base has zero large-prime component on a descended binary curve under the stated prime-order bound"}
  evidence += {repo: crypto-autoresearcher, path: experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/diagnostic/receipt.json, note: "Three fixed prime63 m=2 positives timeout_censored at 600 s: coset ended in Groebner work, random and small-x in root enumeration"}
  reword best_measured:
    - "63-bit second run: six time-censored planted controls, one monitor-error cell"
    + "63-bit second run (RUN-ICPERF-7ed866): six planted controls censored at 300 s, one monitor-error cell, 20 natural cells unattempted; m = 2 diagnostic (RUN-ICPERF-eb0d88, 2026-10-19): three planted positives censored at 600 s (coset: Groebner; random, small-x: root enumeration), supervisor invalid_output; no relation yield, rank or cost measured"
  append to mechanism:
    + "Size coordinate: Koblitz N53 is a 53-bit field with a 45-bit prime subgroup; the two standard binary Koblitz curves have no prime subgroup of order >= 2^50 at field degrees 50-63, so Koblitz cells in this grid are not 50-63-bit subgroup rows."

```

### 22. `problems/icperf-prime63-m2-output-contract-mismatch.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICP-full-width-arity-grid (currently `open_blocked`); **record id:** problems/icperf-prime63-m2-output-contract-mismatch.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `icperf-m2-a`
- **Observation:**
  - p = 9223372021248595841, r = 9223372018953067627, one 475-point base per arm (coset, random, small-x), m = 2, separately planted targets. Receipt: returncode 0, check_returncode 0, status invalid_output, detail 'missing/empty required artifact: manifest.yaml'; run directory also lacks raw-result.json. Checker output: integrity_pass, positive_censored 3, positive_verified 0; diagnostic receipt: three timeout_censored calls (600.148, 600.072, 600.059 s) and a correctly injected monitor-null fault. Frozen plan SHA-256 08f32f02...; launcher SHA-256 4cba7cfb....
  - Record: 'It does not explain or erase the three separately recorded 600-second solver censors'; unblock requires a fresh-ID successor with one hash-bound required-output schema and a standard-supervisor no-science fixture; 'A censored solver result must stay censored even when its artifact contract passes.'
- **Interpretation (conditional):**
  - Infrastructure defect on a prospective trial; read conditionally, the censors are bounded observations (no certificate in 600 s) and not evidence of unsatisfiability (planted satisfying inputs exist). Edit is the evidence entry already proposed in the full-width row; no separate row change.
- **Proposed diff:** none of its own. Carried by Row 21 (full-width-ic-arity-grid-unmeasured): evidence entries problems/icperf-prime63-m2-output-contract-mismatch.md and experiments/EXP-ICPERF-515ae3/runs/RUN-ICPERF-eb0d88/diagnostic/receipt.json, ledger_refs DEC-20261018-eb6e00 and EXP-ICPERF-515ae3, and the best_measured rewrite on LEAD-ICP-full-width-arity-grid.

### 23. `problems/icperf-prime63-monitor-and-positive-controls.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICP-full-width-arity-grid (currently `open_blocked`); **record id:** problems/icperf-prime63-monitor-and-positive-controls.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `icperf-mon-a`
- **Observation:**
  - Receipt RUN-ICPERF-7ed866: status invalid_output, check_returncode 1; six planted positives (coset/random/small-x at m = 2 and m = 8) timeout_censored; natural-coset-m2 infrastructure_monitor_error rss_monitor_unavailable_for_live_child after 2.268 s; 20 natural cells unattempted. 'These are two distinct gaps: monitor reliability and bounded solver feasibility.'
  - Later three-cell diagnostic: all three m = 2 positives censored at 600 s with distinct last phases (Groebner for coset; root enumeration for random and small-x), traces 'bounded observations, not a validated comparative solver result'. Suspected explanations (transient child exit / zombie race; expensive Groebner work) are labeled unverified.
  - --match top hits for this record are LEAD-ICP-icperf-binary-pdp-solver (5) and LEAD-EXO-methodology-instruments (4), both weak; the lead that cites this file in evidence is LEAD-ICP-full-width-arity-grid.
- **Interpretation (conditional):**
  - No new lead field beyond the full-width edit (best_measured text, evidence of the m=2 receipt). The planted controls' archived satisfying inputs mean the timeouts are not unsatisfiability claims.
- **Proposed diff:** none of its own. Carried by Row 21 (full-width-ic-arity-grid-unmeasured): the best_measured rewrite on LEAD-ICP-full-width-arity-grid (this record is already an evidence entry of that lead, with blocked_by pointing at the arity-grid problem) and ledger_refs EXP-ICPERF-891f7f, DEC-20261018-eb6e00.

### 24. `problems/isogeny-graph-wide-relation-solver.md`

- **Action:** `advances_lead`; **lead:** LEAD-STR-class-representative-ic-selection (currently `open_next_step`); **record id:** problems/isogeny-graph-wide-relation-solver.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `isograph-a`
- **Observation:**
  - 2,304 checked degree-7 edges and 2,306 vertices. Source-base transport independently replayed through all 2,048 P29 and 256 P37 edges; targetwise ordered-count equality passed on 128 fixed public control targets at P29 index 8 and P37 indices 4, 24, 256. Missing: equality on the committed discovery stream, a frozen admitted collector schedule, and a complete index-calculus solve with matched-cost pipeline. Candidate schedule: 8,206 discovery arms, 322 check vertices, schedule SHA-256 8de2d731...; 'not approved or executed'.
  - Prior same-conductor observations (from EXP-ECTD-0cf008): P29-E2 RUN-ECTD-c769f1 2,204/32,768 useful targets, rank prefixes 37/143/256/256; P29-E3 RUN-ECTD-f395a9 2,191/32,768, prefixes 45/140/256/256; 99.75% intervals [0.063148, 0.071545] and [0.062762, 0.071136]; independent ordered-count and group-law checks passed; 'this secondary result has not received an evidence review'.
  - Lead today: evidence note 'graph-wide relation yield over 2,304 degree-7 edges blocked on collector and transport'; next_action is the three-arm ecbench study at 24-32 bits.
- **Interpretation (conditional):**
  - Transport is no longer a blocker per the record; the blocker is admission plus a complete solve pipeline. The E2/E3 useful-target fractions are unreviewed same-conductor observations and are not a floor/crater comparison, so best_measured is unchanged.
- **Proposed diff:**

```
EDIT LEAD-STR-class-representative-ic-selection
  ledger_refs += ["EXP-ECTD-0cf008"]
  reword evidence[problems/isogeny-graph-wide-relation-solver.md].note:
    - "graph-wide relation yield over 2,304 degree-7 edges blocked on collector and transport"
    + "graph-wide yield over 2,304 degree-7 edges: transport replayed on all 2,048 P29 + 256 P37 edges and on 128 public control targets; blocked on the committed discovery-stream equality, an admitted collector schedule (8,206-arm candidate, unapproved) and a complete same-point solve; P29-E2/E3 useful fractions 2,204 and 2,191 of 32,768 are unreviewed"

```

### 25. `problems/legacy-adapter-output-preservation.md`

- **Action:** `not_ecdlp`; **lead:** none; **record id:** problems/legacy-adapter-output-preservation.md; **ECDLP record:** no (coverage row NONE)
- **`--match` phrasings run (raw top hits in Appendix A):** `legacy-adapter`
- **Observation:**
  - Status investigating; kind implementation gap. Synthetic controls reproduce deletion of an extra binary file and acceptance of negative wall time / reversed timestamps in the original two-output adapter; corrected prospective versions pass 48 tests and 29 subtests but have no execution authorization under the existing plans. 'No historical result is reclassified on that basis.' --match top hits are weak (LEAD-RHO-native-step-cost 2).
- **Interpretation (conditional):**
  - Coverage row: none. Not about any ECDLP mechanism; no lead cites the adapters or plans.
- **Proposed diff:** none of its own.

### 26. `problems/legacy-trial-manifest-schema.md`

- **Action:** `unclear`; **lead:** none; **record id:** problems/legacy-trial-manifest-schema.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `legacy-trial-manifest`
- **Observation:**
  - Four frozen stage-0 worksheet drivers (EXP-ECDLP-bfbe6f, -5f4f14, -3c166b, -20ac31) write run_id and metrics but omit canonical run fields, so successful original processes cannot yield output_validated receipts; RUN-ECDLP-8f5190 has driver/checker exits 0 but native invalid_output. Resolved for native metadata reproduction of six named worksheet scopes via new source-bound adapters; 'no failure of a mathematical hypothesis ... follows from a manifest defect'.
  - Coverage mapping: H-ECDLP-cba67a -> LEAD-ICP-algebraic-membership-factor-base; H-ECDLP-8c879e, -85fe43, -18c7f7 -> LEAD-EXO-coordinate-statistic-leakage. Neither lead cites those hypotheses or experiments.
- **Interpretation (conditional):**
  - Infrastructure record about fixed toy censuses (finite worksheets); no lead field changes. Marked unclear with the mapping stated.
- **Proposed diff:** none of its own.

### 27. `problems/nist-seed-selection-rule-unexplained.md`

- **Action:** `advances_lead`; **lead:** LEAD-STR-curve-generation-provenance-seeds (currently `exhausted_at_scale`); **record id:** problems/nist-seed-selection-rule-unexplained.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `nist-seed-a`
- **Observation:**
  - Problem (status open, unknown cause): historical acceptance rule for eleven named omitted candidates is unexplained; original generator code, state and run log unavailable. Source-bound replay of the November 1997 draft's listed checks finds 69 certified full-prime-order seed positions (10 published, 59 unpublished); the corrected l_max = 255 near-prime replay raises the observed lower bound to 99 (10 published, 89 unpublished) with independent point certificates, and 10,083 further positions are censored so a full near-prime count is not possible. 'The 69 are eligible positions under the listed text, not a count of actual program visits.'
  - Tests against fixed rules: a field-fixed minimum-order threshold accepting all published same-field controls also accepts seven of eleven omissions (not a complete selector conditional on visitation); extended Atkin information gives 20 earlier, 3 later, 2 tied omitted cutoffs (weakens the former 24/25 ordering). ECPP V3.4.1 source acquired; no linkage to the original generator established. The record states a rule or log is still needed 'or an independently predictive attack-relevant property'; neither condition 'rules out a separate hidden mathematical route'.
  - Lead today (exhausted_at_scale): 'Every public weak-class screen run on all 21 published and omitted classes found no anomaly and no rule separating them ... a hidden weak class would need density at least about 2^-30 among prime-order curves'; revisit_when covers recovered generator logs or a new publicly testable class.
  - This problem record lists no weak-class screen (CM field, class number, conductor, embedding degree, twists, isogenies) of the additional draft-eligible positions beyond the 21 classes.
- **Interpretation (conditional):**
  - The 2^-30 density inference is conditional on the 21 classes being representative of the candidates the program visited; the problem record shows they are a retrospective subset of a larger draft-eligible set. Read conditionally, the closure stands for the 21 named classes; extending the existing screens to the certified draft-eligible positions is a bounded, cheap extension and the revisit_when should say so. No deciding record, so exhausted_at_scale is not changed.
- **Proposed diff:**

```
EDIT LEAD-STR-curve-generation-provenance-seeds
  evidence += {repo: crypto-autoresearcher, path: research/nist_seed_1997_acceptance_20261024/report.md, note: "Draft acceptance-space replay: 69 certified full-prime-order seed positions (10 published, 59 unpublished) meet the November 1997 draft's listed checks"}
  evidence += {repo: crypto-autoresearcher, path: research/nist_seed_1997_nearprime_20261024/report.md, note: "Near-prime extension at l_max = 255: 99 certified positions (10 published, 89 unpublished); 10,083 censored"}
  evidence += {repo: crypto-autoresearcher, path: research/nist_seed_1997_order_threshold_20261024/report.md, note: "Field-fixed minimum-order threshold also admits seven of eleven omissions"}
  append to obstruction.statement:
    + "Cohort scope: the screens cover the 21 named classes (10 published, 11 named omissions); the November 1997 X9.62 draft's listed checks admit at least 69 certified full-prime-order and at least 99 near-prime seed positions (10 published, 89 unpublished; 10,083 more censored), so the 21 are a retrospective subset (problems/nist-seed-selection-rule-unexplained.md); that record lists no weak-class screen of the other positions."
  append to obstruction.revisit_when:
    + "Weak-class screens (CM field, class number, conductor, embedding degree, twist factors, odd-degree isogenies) are extended to the draft-eligible cohort of at least 99 certified positions."

```

### 28. `problems/pages-workflow-disabled-live-snapshot-stale.md`

- **Action:** `not_ecdlp`; **lead:** none; **record id:** problems/pages-workflow-disabled-live-snapshot-stale.md; **ECDLP record:** no (coverage row NONE)
- **`--match` phrasings run (raw top hits in Appendix A):** `pages-workflow`
- **Observation:**
  - Status open; kind deployment configuration and publication-state gap. Workflow reported disabled_manually; public data/meta.json names a 2026-10-11 commit; local build passes (55,318 files, 27,585 records); owner answered 'Re-enable and publish after all checks pass'. --match hits are noise (single score-1 hit).
- **Interpretation (conditional):**
  - Coverage row: none.
- **Proposed diff:** none of its own.

### 29. `problems/semaev-degree-two-fall-nonzero-bridge.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICE-first-fall-degree-assumptions (currently `open_blocked`); **record id:** problems/semaev-degree-two-fall-nonzero-bridge.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `semaev-deg2-a`
- **Observation:**
  - Uniform claim 'descended Semaev S_3 has a nontrivial first fall at degree two' is not proved by its Lean theorem (DegreeTwoFall.lean proves Artin-Schreier normalization and trace annihilation of quadratic coefficients for nonzero target abscissa; no nonzero quotient class). Historical fall_profile builds monomial multiples as {mm | m for mm in f}, which does not cancel duplicates over F_2.
  - Corrected replay (docs/reports/2026-10-22-semaev-first-fall-replay): archived counts 70 degree-two / 10 degree-three reproduced byte for byte; with XOR cancellation and independent binary ranks the same 80 systems give 68 / 12; two draws (n, n', s, x_R) = (5,3,4,8) and (5,3,8,8) move from degree two to three; 12 of 200 null grades change; 7 corrected degree-three draws have x_R != 0.
  - Finite explanation at n = 4, n' = 4, s = 1, x_R = 1: the trace residual u0+u3+w0+w3 is already the fourth linear generator; dim V1 = 1, dim(V2 ∩ R<=1) = 1 so new_falls(2) = 0; dim V2 = 11, dim V3 = 53, dim(V3 ∩ R<=2) = 12 so new_falls(3) = 1. Lean-checked (finite certificate, 256-assignment equation bridge, row-space ranks, filtration, 23-row explicit witness with separating functional); a second implementation reproduces ranks and witness. Independent human semantic review, generic rank semantics and the additive claim correction remain open; PR #2504 proposes a dated correction.
  - Lead today: open_blocked, next_action 'Discharge or refute the nonzero-residual bridge ... in Lean ... and fix fall_profile's representation defect before re-running the FFD_SEMAEV_MEASUREMENT1 table'; discriminates: 'a counterexample restricts it to the trace identity, removing the last uniform premise of the FFD route'; blocked_by this file. --match 20 (next hit 18 is KR-IC-f5c584).
- **Interpretation (conditional):**
  - Both parts of the lead's next_action have been executed for a finite toy Boolean model (defect fixed and table re-run; counterexample exhibited and Lean-checked). Because semantic review is pending and the record keeps the claim open, this is recorded as a non-deciding advance: the lead's step text should be rewritten and the remaining obligation stated. Nothing here speaks to cryptographic-scale solving degree. The disposition stays open_blocked: the record keeps the claim open pending review, and no deciding record exists; it is a candidate to move once review lands, not proposed here.
- **Proposed diff:**

```
EDIT LEAD-ICE-first-fall-degree-assumptions
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-22-semaev-first-fall-replay/report.md, note: "Corrected Boolean replay: archived 70/10 -> 68/12 degree-two/three first falls on 80 draws; defect in fall_profile; 12 of 200 null grades change"}
  evidence += {repo: crypto-autoresearcher, path: docs/reports/2026-10-23-semaev-concrete-witness/report.md, note: "Lean-checked 23-row witness at n = 4, n' = 4, s = 1, x_R = 1: new_falls(2) = 0, new_falls(3) = 1"}
  evidence += {repo: crypto-autoresearcher, path: formal/targets/semaev-s3-degree2-fall-witness.yaml, note: "Frozen formal target for the degree-two fall witness (claim wording pending additive correction)"}
  reword next_action.step:
    - "Discharge or refute the nonzero-residual bridge for the S_3 degree-two cancellation in Lean (formal/targets/semaev-s3-degree2-fall-witness.yaml), and fix fall_profile's representation defect before re-running the FFD_SEMAEV_MEASUREMENT1 table."
    + "Obtain independent semantic-fidelity review of the finite model and proof chain (fall_profile defect fixed on replay: 68/12 corrected vs 70/10 archived; Lean-checked counterexample at n = 4, n' = 4, s = 1, x_R = 1), then record an additive correction to the uniform first-fall-2 wording; a qualified positive theorem needs hypotheses excluding the seven nonzero-target degree-three exceptions; a generic symbolic S_3 descent is a separate theorem."

```

### 30. `problems/staged-xrank-independent-arithmetic-verification.md`

- **Action:** `unclear`; **lead:** none; **record id:** problems/staged-xrank-independent-arithmetic-verification.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `staged-xrank`
- **Observation:**
  - Checker accepts stage 0 from an outcome label plus freeze-file existence and stage 1 from a permitted O-* label plus census/control-table presence; it does not recompute point counts, subgroup selection, scalar/ranking sets, overlap arithmetic, null controls or thresholds. The run source sets B_scalar_recover directly to W_aff before computing its positive-control overlap and computes excess against len(W)/N while ranking affine negation classes; normalization needs independent review.
  - EXP-ECDLP-daee4d spec header: 'ZERO RUNS in this design packet', hypothesis H-ECDLP-b093c1; coverage.tsv maps H-ECDLP-b093c1 -> LEAD-EXO-invertible-hint-subset, whose ledger_refs and evidence do not cite it. --match top hits: LEAD-RHO-lhw-polymem-collision-walks (10), LEAD-RHO-lhw-modular-filter-price (9), LEAD-EXO-lossy-object-propagation (6).
- **Interpretation (conditional):**
  - No lead currently depends on the instrument's outputs; an evidence-validity caveat would apply only if a lead cited the Stage 0-1 results. The coverage mapping to the invertible-hint lead is the program's; the LHW leads are the other plausible home. Marked unclear.
- **Proposed diff:** none of its own.

### 31. `problems/str002-support-verdict-missing-artifacts.md`

- **Action:** `advances_lead`; **lead:** LEAD-ICB-orbit-linear-algebra (currently `exhausted_at_scale`); **record id:** problems/str002-support-verdict-missing-artifacts.md; **ECDLP record:** yes
- **`--match` phrasings run (raw top hits in Appendix A):** `STR002-a`; `STR002-b`; `str002-b`
- **Observation:**
  - DEC-20260727-009 withdrew 'supported' on three grounds: R1 artifact defects (EV-STR-002 run_ids [], no run record for B = 55, 204, 397; committed main() raises IndexError when B mod 3 != 0; rand_alpha 53, 200, 387 re-measure as 54, 201, 382; records rewritten in place after archival), R2/R4 an independently reproduced comparison (alpha (27, 52, 197, 386) phi-invariant vs (27, 52, 199, 387) random base at B = (27, 55, 204, 397), same shift/collection/no-append convention), R3 missing complete-cost evidence (rank deficiencies (4, 6, 30, 67); no archived baseline). 'Evidence-integrity failure, not a mathematical one'; the general mechanism is not rejected.
  - Later work: EXP-STR-004 / EV-STR-004 (DEC-20260730-014, inconclusive): 28/28 runs completed_valid, 654/654 certificates pass, instrument_verdict mixed, direction neutral, 'No H-STR-002 mechanism test'; open confounds UC-1, UC-2.
  - Best --match: LEAD-ICB-orbit-linear-algebra (27 on the second phrasing; 21 for KN-OPEN-006), then LEAD-ICB-frobenius-orbit-factor-base (10-15). Lead scope today is binary Koblitz Frobenius folds; its obstruction quotes LA at 0.0-2.7% of S in Tables A-C (prime Table B rows 0.0-0.4%).
- **Interpretation (conditional):**
  - The mechanism-level question (does a phi-invariant base give O(1) displacement rank in general) is untested; the lead's LA-share argument bounds its payoff at measured sizes. Add the refs so a search from H-STR-002 reaches the lead; statuses of H-STR-002 are the Coordinator's and are not touched here.
- **Proposed diff:**

```
EDIT LEAD-ICB-orbit-linear-algebra
  ledger_refs += ["EV-STR-002", "EV-STR-003", "DEC-20260730-014"]

```

## Proposed new rows (full YAML)

Both rows pass `lead_atlas.check_leads` in the in-memory test above (family code, required fields, `forecloses` >= 3, existing evidence paths, resolvable ledger refs and known results).

### `knowledge/leads/ecdlp/transfer/LEAD-TRF-torsion-section-digit-fourier.yaml`

```yaml
id: LEAD-TRF-torsion-section-digit-fourier
family: transfer
title: Fourier mass of p-adic digit characters (i >= 1) of the prime-to-p torsion section and the n^(-1/4)
  Fourier-learning breakeven
mechanism: 's_tor : <P> -> E(Z_p)[n] is a computable homomorphism, so g(k) = e(t * a_i(c(s_tor([k]P)))/p)
  has exact shift-query access: g(d + r) is read from s_tor(Q + [r]P). A heavy Fourier coefficient tau
  = Phi_i(n) of g would give chi_j(d) from about tau^-2 queries (hidden-number / Fourier-learning lineage)
  against rho at sqrt(pi n/4) group operations; the breakeven is about tau* = n^(-1/4) up to polylog factors
  (order-of-magnitude estimate, RT-20261023-dcb217). Digit 0 is covered by subgroup-sum bounds (O(sqrt
  p) cancellation); for i >= 1 no bound is known. The formal-logarithm closure of LEAD-TRF-padic-canonical-section
  does not address this nonlinear readout.'
disposition: open_next_step
next_action:
  step: 'KN-OPEN-d3a6f0 Q1 / DEC-20261023-2e7447 NA-4: measure the growth exponent of Phi_i(n) for i =
    1..4 over CM-canonical and arbitrary lifts up to n of about 10^4 to 10^5 (toy tier), with a symmetry-matched
    null (negation classes; mu_6 orbits at D = -3), j = 0 dropped from the spike count, planted-leak power
    curves and several lifts per curve; in parallel the Weil-type bound of NA-6 (Q2).'
  discriminates: A measured exponent consistent with -1/2 for each i = 1..4 up to the stated n resolves
    the question negatively at that scope; a replicated Phi_i(n) >= n^(-1/4 + delta) with a locatable
    heavy coefficient and a charged end-to-end cost below rho and BSGS would be an exponent-level signal
    needing independent replication and a red team; the polynomial degree of the coefficient-location
    step in 1/tau must be checked before any exponent is claimed.
best_measured: 'EV-CZLIFT-764f54 (preliminary, toy): no single-digit function a_i(x or y of s_tor([k]P)),
  i = 0..4, with half-range normalised correlation tau >= rho_min in [0.28, 0.98] on 42 power-bearing
  records (47 <= n <= 613, p <= 571, one generator per record); spectra white at that floor; the 30 records
  with n <= 41 carry no information; not evidence about the exponent.'
evidence:
- repo: crypto-autoresearcher
  path: knowledge/open-problems/KN-OPEN-d3a6f0.md
  note: The question, resolution criteria, and why it is not already answered
- repo: crypto-autoresearcher
  path: ledger/evidence/EV-CZLIFT-764f54.yaml
  note: Half-range single-pair correlation floor on 42 toy records (supports narrowly, preliminary)
- repo: crypto-autoresearcher
  path: ledger/decisions/DEC-20261023-2e7447.yaml
  note: 'Refine: H-CZLIFT-fba874 approved -> analyzed; successor work NA-4 (measurement), NA-6 (Weil-type
    bound)'
- repo: crypto-autoresearcher
  path: knowledge/findings/KN-FIND-7e2b94.md
  note: s_tor is the unique homomorphic section; Smart functional vanishes on it (derivation)
ledger_refs:
- H-CZLIFT-fba874
- EV-CZLIFT-764f54
- DEC-20261023-2e7447
- EXP-CZLIFT-1a3453
- RQ-CZLIFT-b9f765
- GOAL-CZLIFT-1516d5
known_results:
- KR-IC-cd159a
related:
- LEAD-TRF-padic-canonical-section
- LEAD-EXO-hnp-advice-leakage
- LEAD-EXO-coordinate-statistic-leakage
- LEAD-EXO-dl-character-sum-pseudorandom
forecloses:
- p-adic digit characters of the torsion section
- Fourier learning of digits of the torsion section
- hidden number problem from torsion-section digits
- Weil-type bound for p-adic digit sums of the torsion section
- n^(-1/4) Fourier-learning breakeven for digit characters
areas:
- CZLIFT
last_reviewed: '2026-10-24'
```

### `knowledge/leads/ecdlp/exotic/LEAD-EXO-koopman-transfer-operator.yaml`

```yaml
id: LEAD-EXO-koopman-transfer-operator
family: exotic
title: 'Coarse-grained transfer (Koopman) operator of the translation-by-P walk: spectral localization
  of k'
mechanism: 'Push the translation-by-P walk onto a cell partition to get a C x C Markov operator, estimate
  its leading spectrum from S = o(sqrt n) trajectory samples, and map eigenvalue phases to a k-interval.
  Translation is measure-preserving, so the Koopman operator is unitary with characters as eigenfunctions
  and the phases are the logarithm data: at full resolution (C ~ n) the spectrum recovers k circularly;
  at C << n coarse-graining may mix exactly that phase (L = O(1) by character orthogonality). Measured
  only for negation-symmetric x-interval cells, where the fold makes the coarse chain reversible with
  a real spectrum.'
disposition: open_next_step
next_action:
  step: 'H-TRA-4344b7 Part A: build the exact C x C operators by group enumeration (no sampling) at the
    EXP-TRA-001 toy orders on cells (x-interval, sign of y) and on one deliberately non-negation-symmetric
    interval family, and compare detailed-balance residual and max |Im lambda| with the 2.5e-17 / 3.7e-16
    floors of the x-interval cells; Part B only if phases appear: fitted exponent of L(S, C) against the
    0.0195 measured for x-cells.'
  discriminates: 'Reversibility and a real spectrum persisting on fold-breaking partitions would make
    the committed barrier partition-general (character orthogonality rather than the +/- fold); phases
    appearing with L flat at O(1) is a stronger barrier statement than the one committed; L growing with
    n on the non-symmetric family (the hypothesis''s own prior: 0.10) would be a sub-birthday localization
    signal needing a charged-cost comparison.'
best_measured: 'EXP-TRA-001 (toy, p = 211 / 1009 / 4099): L_eff means 1.667 / 1.555 / 1.778 against chance
  floors 1.385 / 1.304 / 1.579, growth exponent 0.0195, hits at chance; all 54 exact coarse operators
  reversible (detailed-balance residual 2.5e-17, max |Im lambda| 3.7e-16); positive control (C = n recovers
  k) 18/18; negative control 50 hits vs 50.35 chance.'
evidence:
- repo: crypto-autoresearcher
  path: knowledge/open-problems/KN-OPEN-010.md
  note: 'Register entry: transfer-operator localization of k'
- repo: crypto-autoresearcher
  path: ledger/EV-TRA-001.yaml
  note: 'EXP-TRA-001: L = O(1), exact reversibility for negation-symmetric x-interval cells (weakens,
    preliminary)'
- repo: crypto-autoresearcher
  path: ledger/H-TRA-001.yaml
  note: Hypothesis rejected_scoped (DEC-20260718-007)
- repo: crypto-autoresearcher
  path: ledger/hypotheses/H-TRA-4344b7.yaml
  note: 'Proposed: is reversibility a property of the partition or of the walk (Part A exact, Part B long
    shot)'
ledger_refs:
- H-TRA-001
- H-TRA-4344b7
- EV-TRA-001
- DEC-20260718-007
- EXP-TRA-001
known_results:
- KR-RHO-13bf67
related:
- LEAD-EXO-augmented-oracle-ggm
- LEAD-RHO-r-adding-walk-mixing
forecloses:
- Koopman operator of the translation walk
- transfer operator spectrum localizes the discrete log
- coarse-grained eigenvalue phase of translation by P
- spectral discrete log from sub-birthday trajectory samples
areas:
- TRA
last_reviewed: '2026-10-24'
```

Coverage remap: `H-CZLIFT-fba874` `LEAD-TRF-padic-canonical-section` -> `LEAD-TRF-torsion-section-digit-fourier`. `H-TRA-4344b7` is not in coverage.tsv (area TRA is not an ECC area); it moves only in `ledger_refs`.

## Not proposed

- No disposition change. The two 'split' rows keep `closed_obstructed` on the narrowed scope and open a sibling; no deciding record changes a lead's label.
- No hypothesis, experiment, goal or problem status change. Quoted statuses: H-CZLIFT-889c9d/-6d4ed1 supported, H-CZLIFT-d37231 rejected (scoped), H-CZLIFT-fba874 analyzed (DEC-20261023-147f9f, -36b4f0, -039ddf, -2e7447); H-BKK-001/H-TTN-001/H-NCP-001/H-TRA-001/H-STR-001 rejected_scoped; H-BKKMV-001 supported; H-STR-002 weakened; H-SEMAEV-94dab2 approved.
- Not read in full (summaries only, per instructions): `problems/nist-seed-selection-rule-unexplained.md` (62 KB), `problems/full-width-ic-arity-grid-unmeasured.md` (47 KB), `problems/isogeny-graph-wide-relation-solver.md` (26 KB), `problems/README.md` (index rows only), the long evidence middles of `legacy-*`/`finite-worksheet-*`.

## Appendix A: raw `lead_atlas.py --match` top hits

Command per phrasing: `LEAD_ATLAS_CRYPTO=... LEAD_ATLAS_CRYPTANALYSIS=... LEAD_ATLAS_ECC_CHALLENGES=... python3 tools/lead_atlas.py --match "<phrase>"` from `/Volumes/SSD990-2/crypto-autoresearcher`; first 8 lines shown (score, id, disposition, title).

```
### FIND-3c7e19-a :: --match "Smart anomalous attack canonical lift Serre-Tate mod p^2 degenerate"
   22  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   22  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   17  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    9  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    7  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    6  KR-RHO-5b1c0a                                known_result       Representation techniques do not beat rho over F_{p^2}

### FIND-3c7e19-b :: --match "Kummer class vanishes canonical lift anomalous curve formal group next digit random section null"
   19  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
   16  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
   16  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   14  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   13  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   10  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class

### FIND-7e2b94-a :: --match "canonical torsion section E(Q_p) to E(F_p) Smart functional vanishes non-anomalous"
   20  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   12  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    6  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    4  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    4  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    3  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail

### FIND-7e2b94-b :: --match "prime-to-p torsion section formal group lift Hensel section identity readout random rate"
   19  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   17  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    8  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    8  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
    7  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    6  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law

### FIND-c71e5d-a :: --match "Fermat quotient Teichmuller naive integer section multiplicative group Smart-style recovery"
    7  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
    7  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    6  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    6  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    5  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
    5  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms

### FIND-c71e5d-b :: --match "global lift integral section small coefficient model Siegel recovers d exactly integral multiples"
   14  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    9  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    8  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    7  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    7  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    6  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    6  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant

### OPEN-004-a :: --match "BKK mixed volume Newton polytope Semaev sparse resultant elimination prime field"
   12  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    9  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    9  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    8  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    8  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    7  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130

### OPEN-004-b :: --match "Newton saturation support-aware elimination Semaev summation polynomial dense resultant"
   18  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   11  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
   10  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    9  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
    8  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho

### OPEN-005-a :: --match "generic group model simulable jets elliptic nets incidence representation sub-birthday"
   16  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
   10  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
   10  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    9  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
    9  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    7  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

### OPEN-005-b :: --match "dual number first jet oracle GGM simulation O(1) overhead"
    7  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    7  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    6  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    6  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    5  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption

### OPEN-006-a :: --match "displacement rank structured linear algebra arithmetic progression relation supports Wiedemann"
   21  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   12  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    8  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    8  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    7  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    7  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    6  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)

### OPEN-006-b :: --match "Toeplitz Hankel relation matrix structured solve designed supports index calculus"
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   12  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    9  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    8  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed

### OPEN-007-a :: --match "tensor train bond rank Semaev resultant tree low rank factorization"
    8  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    8  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    7  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    7  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    7  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    6  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    6  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases

### OPEN-007-b :: --match "tensor network contraction counting solutions border rank resultant intermediate"
    4  LEAD-ICB-free-relations-self-collision       exhausted_at_scale Free relations from self-collisions in the pair-root table (no-probe relations)
    4  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    3  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    3  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    3  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    3  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    3  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    3  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection

### OPEN-004-c :: --match "Semaev eliminant subresultant composed resultant Bezout degree prime field"
   18  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   17  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   14  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   11  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   11  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   10  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   10  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials

### OPEN-008-a :: --match "noncommutative path algebra quiver word relations commutator collapse Groebner"
    6  LEAD-ICB-free-relations-self-collision       exhausted_at_scale Free relations from self-collisions in the pair-root table (no-probe relations)
    6  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    5  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    5  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    5  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    4  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    4  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
    4  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system

### OPEN-008-b :: --match "word search non-abelianizable relation translations negation arrows birthday"
    7  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    6  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
    6  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    5  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles

### OPEN-009-a :: --match "monodromy group Semaev summation cover full symmetric wreath exceptional curves Chebotarev"
   34  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   11  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    9  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    9  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
    9  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    8  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null

### OPEN-009-b :: --match "Frobenius cycle type census relation rate imprimitive resolvent CM curves"
   18  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    8  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    8  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    6  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    6  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    6  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    6  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source

### OPEN-010-a :: --match "transfer operator Koopman coarse-grained translation walk spectrum localize discrete log"
   11  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    9  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    8  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    8  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    8  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class

### OPEN-010-b :: --match "character orthogonality spectral eigenvalue phase interval sub-birthday trajectory samples"
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
    4  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    3  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    3  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    3  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    3  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
    3  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    3  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class

### OPEN-5b3a08-a :: --match "harness semaev s4_expr variable collision bug shared harness"
    6  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    6  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    6  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    6  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    6  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
    6  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks

### OPEN-5b3a08-b :: --match "build_factor_base whole curve target subgroup sampling cofactor decomposition probability"
   22  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   19  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   17  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base

### OPEN-d3a6f0-a :: --match "Fourier mass p-adic digit characters torsion section Fourier learning hidden number breakeven"
   14  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   10  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    6  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    6  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    6  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    5  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    5  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks

### OPEN-d3a6f0-b :: --match "character sum bound digit function torsion section Weil-type exponent n^(-1/4) heavy coefficient"
    8  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    8  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    8  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    7  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    6  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    6  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves

### STR002-a :: --match "phi-orbit factor base block-circulant relation matrix displacement rank j=0 endomorphism prime field"
   17  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   16  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   15  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   13  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
   13  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base

### STR002-b :: --match "endomorphism-invariant factor base equivariant relation matrix structured linear algebra GLV"
   27  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   12  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
   11  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   11  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves

### dtree-a :: --match "depth-2 descent tree decomposition cost slope grid prime field index calculus cofactor factor base"
   27  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   22  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   22  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   20  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   20  LEAD-ICP-extension-field-embedding           closed_obstructed  Embedding E(F_p) into E(F_{p^n}) to buy a subfield factor base
   20  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   19  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   19  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571

### dtree-b :: --match "two-level descent decomposition exact enumeration slope fit non-saturated cells heuristic (B/N)^2"
   10  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    9  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    8  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    8  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    8  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    8  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    7  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools

### dtree-c :: --match "medium base enlarged factor base two-stage descent first-stage decomposition large prime variant NFS descent tree"
   20  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   16  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   15  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   15  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   13  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   13  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base

### finite-worksheet :: --match "finite worksheet helper rejects env-prefixed native command direct invocation ECDLP toy curve"
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    7  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
    6  KR-IC-64659b                                 known_result       Diem: rigorous subexponential ECDLP for suitable n
    6  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    6  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    6  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    6  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves

### legacy-trial-manifest :: --match "legacy stage-0 ECDLP trial manifest canonical run fields native admission worksheet"
   10  KR-IC-64659b                                 known_result       Diem: rigorous subexponential ECDLP for suitable n
    7  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    6  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    6  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
    6  KR-RHO-33f837                                known_result       Prime-field ECDLP records
    6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    5  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks

### legacy-adapter :: --match "legacy adapter output preservation timing validation scratch deletion"
    2  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    1  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs

### staged-xrank :: --match "staged x-rank overlap low Hamming weight scalar set independent arithmetic verification"
   10  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    9  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups
    6  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
    5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner)
    5  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    5  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)

### pages-workflow :: --match "Pages workflow disabled live dashboard snapshot stale"
    1  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base

### full-ledger :: --match "full ledger validation integrity errors archived records"
    4  KR-RHO-38be82                                known_result       Tag tracing and table-driven step shortcuts
    4  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
    4  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves
    3  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
    3  LEAD-RHO-kangaroo-interval                   closed_dominated   Kangaroo / lambda (van Oorschot-Wiener, Gaudry-Schost) as a full-group ECDLP solver
    3  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
    2  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
    2  KR-RHO-33f837                                known_result       Prime-field ECDLP records

### formal-target :: --match "Lean formal target semantic fidelity claim 83 targets"
    7  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    6  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    5  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    5  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
    4  LEAD-EXO-torsor-deck-period                  closed_obstructed  Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent
    4  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    4  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation
    4  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves

### dreg-c1 :: --match "degree of regularity Macaulay rank n=15 D=6 semi-regular null memory cap"
   30  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   14  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   12  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    9  KR-IC-0d2021                                 known_result       Modern Gröbner-basis complexity refinements
    9  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    8  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    7  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    7  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks

### frob-c5-a :: --match "Frobenius trace kernel factor kernel X^5-1 finite field degree five Lean quotient matrices"
   12  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   12  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
   11  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   11  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
   11  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    9  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    9  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130

### semaev-deg2-a :: --match "Semaev S_3 degree-two first fall trace cancellation nonzero residual Boolean rank"
   20  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
   18  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   14  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
   14  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    9  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems

### isograph-a :: --match "graph-wide isogeny relation yield degree-7 edges transport factor base collector complete solve"
   26  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   17  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   17  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   16  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   14  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   13  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
   13  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving

### nist-seed-a :: --match "NIST seed skipped candidates selection rule unexplained curve generation"
   24  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
   10  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
    4  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    4  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    4  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    4  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    4  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    4  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)

### ectd-a :: --match "arity-3 relation yield panel conductor native random factor bases crater floor"
   37  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   19  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   17  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   13  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
   12  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   11  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   11  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   11  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness

### icperf-m2-a :: --match "prime63 m=2 diagnostic output contract supervisor invalid_output censored"
    1  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)

### icperf-mon-a :: --match "prime63 panel RSS monitor planted positive controls censored solver feasibility"
    5  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    4  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    4  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    3  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    3  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    3  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    2  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)

### fullwidth-a :: --match "full-width complete solve index calculus arity grid 63-bit subgroup"
   28  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   11  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   10  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    9  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
    9  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300

### str002-b :: --match "H-STR-002 phi-orbit factor base displacement rank weakened artifact ablation"
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   10  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   10  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    9  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    9  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
```

---

## Group: crypto

# fold-crypto: the `crypto` group folded into the ECDLP lead atlas (proposed diffs only)

Reviewer step: lead-atlas skill, "changed since review", step 2. Output is a set of PROPOSED atlas row edits. No row, no `coverage.tsv`, no `REVIEW_STATE.json` and no repository file was edited. Written only under `scratchpad/audit/`.

## 0. Scope, method, limits

- Group `crypto`, repository root `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main` (HEAD `5cb553810e`). The reviewed commit pinned in `knowledge/leads/ecdlp/REVIEW_STATE.json` is `da3a1b5d53323a4fb14ed761ca269e84b6018089`.
- The 16 paths are exactly the `crypto:` block of `scratchpad/atlas/delta.txt`: `benchmarks/README.md`, `docs/bounds/FRONTIER.md`, `docs/ic/LEADERBOARD.md`, `problems/README.md` and 12 `problems/*.md` records.
- To separate what changed from what the leads already hold, I used read-only `git diff da3a1b5d HEAD -- <path>` on the three large files and the modified problem records. `benchmarks/README.md` has 29 insertions and 0 deletions (26 new table rows, 2 prose lines, 1 blank). `docs/ic/LEADERBOARD.md` changes 13 validation cells and one registry hash. `docs/bounds/FRONTIER.md` is a generated file rebuilt under "procedure 2" (commits `e064d7d49e`, `71004838b7`).
- None of the 16 paths is a ledger record. No `H-`, `EV-`, `DEC-`, `IDEA-`, `EXP-` or `GOAL-` id occurs in any of the 12 problem files, in the added lines of `benchmarks/README.md`, or in the diffs of `LEADERBOARD.md` and `FRONTIER.md`. Consequences: no `coverage.tsv` row is implied, the "IDEA-2026101x/2x `prior_art.lead`" check does not apply to this group, and no `ledger_refs` addition is proposed anywhere below.
- `lead_atlas.py --match` was run with at least two phrasings for every record that could be ECDLP (four for prime61, three for p61 and eccp131, added after the first two phrasings did not surface the lead I judged closest). The raw top-5 lines are embedded in section 6. Where my chosen lead is outside the top 5 I say so and give the reason.
- Every proposed evidence path was checked to exist at crypto-main HEAD (`ls`/`-e`), because `--check` fails on missing paths.
- I read records by their summary (problem record, study README, benchmark table row). I did not open raw logs or session files. Numbers below are quoted from the file named next to them. A timeout, `UNKNOWN`, capped stream or gate failure is reported as such and is not used as evidence.
- Observation and interpretation are separated: "Observed" is quoted from the file; "Reading" is mine and conditional.

## 1. Result in one table (16 paths)

| # | path | ECDLP | action | lead (primary) | one line |
|--:|:--|:--|:--|:--|:--|
| 1 | `benchmarks/README.md` | yes | advances_lead | many, see 2.1 (26 rows) | 26 new rows: IC engineering rounds R06 to R12 and rule v6 to v8, a matched-rho v8 row, negative micro-lever explorations, rootfinding, factor-base, PS-3 oracle, safecurves slots, N83 prebuilt base |
| 2 | `docs/bounds/FRONTIER.md` | yes | advances_lead | LEAD-ICP-generic-table-decomposition (+4 RHO leads, RHO-matched-rho-calibration) | procedure-2 rebuild: v1 bounds kept as historical, v2 bounds ranked; cited bound ids and the IC alpha interval drift |
| 3 | `docs/ic/LEADERBOARD.md` | yes | advances_lead | LEAD-ICP-prime-ic-constant-engineering | Table B 13 of 13 rows now "validated"; Table C and Table A unchanged in status |
| 4 | `problems/README.md` | no | not_ecdlp | none | index only; every ECDLP row it adds is folded under its own problem file |
| 5 | `problems/certicom-binary-gpu-rho-integration.md` | yes | advances_lead | LEAD-RHO-prime-gpu-rho | three dated CPU/CUDA-port studies for ECCp-131 and ECC2-131; no GPU result |
| 6 | `problems/ecbench-claim-n13-replay-accounting-version-drift.md` | yes | advances_lead | LEAD-ICE-boolean-f4-f5-f6-engines | inherited-F4 counted work depends on lazy vs eager specialisation accounting; ic-f4-m3 differs 1.12x to 1.30x |
| 7 | `problems/eccp131-full-parameter-index-calculus.md` | yes | advances_lead | LEAD-ICP-generic-table-decomposition | exact 131-bit prime curve: 2-point and 3-point small-x probes, zero natural relations, rank 0, support bounds 2^-103.19 and 2^-88.19 |
| 8 | `problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md` | yes | advances_lead | LEAD-ICP-gfp5-oa-sdhp-jv | trial constant measured, Edwards 2-torsion route end to end; fills the lead's `best_measured: None` |
| 9 | `problems/n83-prebuilt-base-quality-m2-m4.md` | yes | advances_lead | LEAD-ICB-factor-base-subspace-choice | n = 83 retained-base comparison at m = 2..4 is unmeasured; this is the experiment the lead's `revisit_when` names |
| 10 | `problems/nist-extension-twist-composite-cofactors.md` | yes | advances_lead | LEAD-STR-curve-generation-provenance-seeds | 8 of 9 degree-2 extension-twist orders fully factored; one 444-bit P-256 residual unsplit |
| 11 | `problems/nist-factorization-raw-archive-publication.md` | no | not_ecdlp | none | storage-access limit for the factorization archives |
| 12 | `problems/p61-registered-root-terminal-closure.md` | yes (census infrastructure) | unclear | (LEAD-EXO-ml-learned-models, evidence only) | census substrate gap resolved; no ECDLP measurement |
| 13 | `problems/prime61-horizontal-class-memory.md` | yes | advances_lead | LEAD-ICP-isogeny-transported-relation-yield | 61-bit horizontal class: 614.4M capped target trials, zero relations or solves; coverage still uncertified |
| 14 | `problems/rho-worker-tier1-host-access.md` | yes | advances_lead | LEAD-RHO-batched-inversion-shared-pm | secp256k1 serial vs batch worker: every aggregate `unknown_gate_failed`; diagnostic 5.110 not admitted |
| 15 | `problems/rootfinding-complete-cost-calibration.md` | yes | advances_lead | LEAD-ICE-rootfind-pairtable-oracle | 2026-10-19 conditional pair-cell addition only; blocker unchanged |
| 16 | `problems/sqisign-statistical-root-gate.md` | no | not_ecdlp | none | SQISign unit-test assertion in a release suite |

Tally over the 16 paths: `advances_lead` 12 (rows 1, 2, 3, 5, 6, 7, 8, 9, 10, 13, 14, 15), `unclear` 1 (row 12), `not_ecdlp` 3 (rows 4, 11, 16). No path is `new_mechanism` or `decides_lead`. The structured output lists more than 16 rows because `benchmarks/README.md` is split into one row per new benchmark entry (26) and `FRONTIER.md` and `LEADERBOARD.md` are split by the lead they touch.

Why no `decides_lead` and no disposition change: every disposition in the atlas that these records touch is either `open_*` with a next step that these records only partly execute, or a closure whose `revisit_when` condition is not met by anything in these 16 paths. The two `blocked_by` problem files that matter here (`certicom-binary-gpu-rho-integration.md`, `rootfinding-complete-cost-calibration.md`) are still `open` (status line of each file), so `LEAD-RHO-prime-gpu-rho` and `LEAD-ICE-rootfind-pairtable-oracle` stay `open_blocked`. Details per row below.

## 2. Per-path reasoning

### 2.1 `benchmarks/README.md` (26 new rows)

Observed in the diff: 26 rows added to the admitted-results table, none removed, plus the sentence "The retained adjacent-K screen (`N83_FINEGRID_UNADMITTED_20261021.md`) is preserved separately pending validation admission" (that file holds the quarantined `20261016-n83-finegrid` row: N83 root11, K1102 to 1120, 21 fresh processes on one exposed target, "candidate remains unpromoted"). No existing lead cites `benchmarks/README.md`, any of the 26 slugs, or the quarantined `n83-finegrid` / `n83_e2e_finegrid` entry (grep over `knowledge/leads/ecdlp` is empty), so the quarantine changes no lead text; the leads cite the `research/` directories behind some of them.

`--match` (embedded in section 6) for the IC-engineering rows returned `LEAD-ICB-koblitz-rho-reference` 21, `LEAD-ICB-koblitz-setup-phase-cost` 17, `LEAD-ICB-generic-table-oracle` 16, `LEAD-ICB-retained-setup-online` 16, `LEAD-RHO-matched-rho-calibration` 16 as top 5, so the Koblitz IC leads cover these rows.

**(a) Koblitz IC engineering rounds and rule runs** (leads `LEAD-ICB-koblitz-setup-phase-cost` primary, `LEAD-ICB-koblitz-rho-reference` for the rho side). All on Emerald Rapids, 4 cores, isolated CPU 2; cold = `ic price --single-target`; ratios v_prev / v_new at 2^44.3 / 2^44.5 / 2^47.2 with 95% intervals as printed in the row.

| slug | observed (quoted) | status of the row's own classification |
|:--|:--|:--|
| `20261016-ic-r10-main-head` | v3 to main (becomes baseline v4): 1.017 [0.990, 1.045], 1.034 [1.012, 1.055], 1.007 [0.992, 1.022] | "credited to main", engineering |
| `20261016-ic-r06-scan-key` | v4 to v5: 1.197 [1.167, 1.228], 1.220 [1.197, 1.243], 1.241 [1.223, 1.260]; collection 1.26 to 1.30x | accepted baseline v5, engineering |
| `20261016-ic-r08-scan-fold` | v5 to v6: 1.326 [1.297, 1.356], 1.354 [1.316, 1.392], 1.398 [1.370, 1.425]; collection 1.47 to 1.53x | accepted baseline v6, engineering |
| `20261016-ic-r11-build-streams` | v6 to v7: 1.134 [1.107, 1.162], 1.124 [1.100, 1.148], 1.071 [1.049, 1.093]; build phase 1.50 to 1.51x | accepted baseline v7, engineering |
| `20261017-ic-r12-admitted-prefetch` | v7 to v8: 1.055 [1.036, 1.075], 1.055 [1.038, 1.072], 1.063 [1.053, 1.073]; with R06, R08, R11 "1.90 to 1.98x over v4" | accepted baseline v8, engineering |
| `20261016-ic-rule-v6` | cold IC/rho 3.78 to 12.06x (7.90 / 7.40 / 12.06 at the three large sizes); rule v3 was 5.23 to 20.97x; online IC 14.2 to 36.4x faster | accounting, "distance to rho about 40% smaller" |
| `20261016-ic-rule-v7` | cold 3.43 to 11.51x; online 14.1 to 37.0x faster | accounting |
| `20261019-ic-matched-rho-v8` | rho with batched GFNI signed-Frobenius canonicalisation ("matched") vs the v7 rho as control, same binary: cold IC/rho 4.67 [4.34, 5.07], 5.70, 7.07, 11.75, 10.65, 18.07 [15.98, 20.58] at log2 r 36.6 to 47.2; control 3.59 to 11.56; matched/control 1.30 to 1.58; rho online 1.42 to 1.62x faster; slope of ln(cold ratio) on ln r 0.168 [0.128, 0.208] matched, 0.141 control, 0.176 at v3; "no advance" | engineering (rho kernel) and accounting (larger distance) |
| `20261017-ic-scan-stages-v8` | scan 16.2 / 16.8 / 17.6 ns per summand (v3: 35.2 / 34.8 / 36.4); scan is 97 to 99% of collection; collection is 56 to 82% of cold | diagnostic |
| `20261017-ic-a14-prefetch-size-gate` | cold v8/gate 0.992 [0.964, 1.022] at 2^27.8, 0.961 [0.854, 1.083] at 2^38.0, 1.011 [0.978, 1.046] at 2^44.3 | "no gain, no round declared" |
| `20261017-ic-a15-filter-slots` | 0.958 [0.911, 1.007], 0.964 [0.935, 0.993], 0.983 [0.967, 1.000] | "negative" |
| `20261017-ic-a16-huge-pages` | filter alone 1.017 / 0.981 / 1.046 [1.026, 1.067]; every array 0.970 / 0.979 / 1.012 | exploration, no round |
| `20261017-ic-a17-filter-huge-pages` | 1.047 [0.999, 1.098], 0.976 [0.944, 1.009], 1.051 [1.029, 1.075] | exploration, no round (needs each lower end above 1.03) |
| `20261017-ic-a18-wider-base` | factor base 320 to 400 / 470 orbits at 2^47.2: 1.020 [1.002, 1.037], 1.023 [0.994, 1.054]; collection -27%, build x2.28 for x2.17 stored pairs | exploration, recipe change, no round |
| `20261017-ic-a19-filter-pages-build-parts` | 1.067 [1.010, 1.126], 1.014 [0.978, 1.051], 1.054 [1.012, 1.097] | exploration, no round |
| `20261017-ic-a20-build-line-streams` | "no visible gain": build 119 / 114 ms vs 128 / 108 (2^44.3), 238 / 220 vs 231 / 229 (2^47.2) | smoke, not pursued |

Observation on units and numbering (needs the reviewer's eye before any `best_measured` is overwritten). The existing lead `LEAD-ICB-koblitz-setup-phase-cost` quotes "rule v4 (2026-10-24 ...)": `research/ic_tool_program/rule/v4/README.md` says "Ran 2026-10-24", a paired recipe test (recipe v4/v3, rho at the canonical step). The benchmark rows "rule v6/v7/v8" ran 2026-10-16 to 2026-10-19 and are numbered by the IC binary baseline (v6 = v4 + R06 + R08, v7 = + R11, v8 = + R12). They are different series with different units: the lead's 9.9x to 43.5x gap is rho priced at the canonical step in counted units, the v6 to v8 figures are wall-time cold ratios with both arms timed in one process (the row says the section 5a band therefore "gives one figure"). Do not replace one with the other; append the v8 row with its unit. `docs/ic/LEADERBOARD.md` Table A header still reads "re-run at baseline v3" with the 5.23x to 21x values, so the board has not absorbed v6 to v8.

Reading (conditional). The v8 matched-rho numbers are 0.86x to 0.93x of the v3 published ratios at each size (4.67/5.23, 5.70/6.12, 7.07/7.66, 11.75/13.24, 10.65/12.03, 18.07/20.97). In the same wall-time units the log-log slope of the cold ratio is 0.168 [0.128, 0.208], the same sign and size as the counted-unit slope 0.165 [0.117, 0.213] already recorded in `LEAD-ICB-frobenius-orbit-factor-base`. If that slope persists beyond log2 r = 47.2 the distance to rho would keep growing; the data here reach only log2 r = 47.21 ("no curve of log2 r >= 50 runnable"). The v8 README states that the control rho is not admissible as a reference at four of six sizes (1.05, 1.20, 1.04, 1.03 of the strong walk's time per step) and that why this differs from v7 (0.57 to 0.78) "was not established"; the matched rho is admissible at 6 of 6 (0.57 to 0.82). `research/ic_tool_program/rule/v8/` contains no `VALIDATION.json`.

Proposed edits:

- `LEAD-ICB-koblitz-setup-phase-cost`: add `evidence` {crypto, `research/ic_tool_program/rule/v8/README.md`, "rule v8: matched-rho cold IC/rho 4.67 to 18.07x at log2 r 36.6 to 47.2, wall time, one process; no advance"}; {crypto, `research/ic_tool_program/rounds/R12-admitted-prefetch`, "baseline v8: R06+R08+R11+R12 1.90 to 1.98x cold over v4"}; {crypto, `benchmarks/20261017-ic-scan-stages-v8`, "scan 16 to 18 ns/summand, 97 to 99% of collection"}; {crypto, `benchmarks/20261017-ic-a15-filter-slots`, "A14 to A20 micro-levers: no round (A15 negative)"} (path form `benchmarks/<slug>` directory; verified). Append to `best_measured`: "Baseline v8 (R06+R08+R11+R12) is 1.90 to 1.98x faster cold than v4 at 2^44.3 to 2^47.2; rule v8 vs matched rho (wall time, same process): 4.67x (log2 r 36.6) to 18.07x (47.2) [15.98, 20.58]; A14 to A20 stage explorations moved no size past the 1.03 acceptance bar." Leave `disposition: open_next_step`. Suggested wording change to `next_action.step` (reviewer's call): the "re-run the rule-v4 paired panel" baseline binary would now be baseline v8.
- `LEAD-ICB-koblitz-rho-reference`: append to `best_measured` "Rule v8 (2026-10-19), six Table A curves, same process: matched rho (batched GFNI signed-Frobenius canonicalisation) is admissible against the strong fixture at 6/6 sizes (0.57 to 0.82 of its time per step); control rho admissible at 2/6; cold IC/rho 4.67 to 18.07x (control 3.59 to 11.56x); not validated (no `VALIDATION.json`)". Add `evidence` {crypto, `benchmarks/20261019-ic-matched-rho-v8`, ...}. `next_action.step` first clause ("run the strong rho fixture and ParallelRho on the same Table A targets in the same process") is executed in wall-time terms by v8's reference check; what remains is pricing at the canonical step with the section 5a band and producing a replay certificate and `VALIDATION.json`, then the 131-bit signed-Frobenius walk. Disposition unchanged (`strongest_available` is still unresolved by the gate).
- `LEAD-ICB-generic-table-oracle` (closed_obstructed, theorem): add `evidence` {crypto, `benchmarks/20261019-ic-matched-rho-v8`, "ln(IC/rho) slope 0.168 [0.128, 0.208] wall time"}. The obstruction statement already reads "ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r" in counted units; the new slope is consistent with it. No disposition change.

**(b) Other Koblitz and binary rows**

| slug | observed | lead | proposed edit |
|:--|:--|:--|:--|
| `20261022-strong-rho-batchinv` | `Gf2::batch_inv_clmul` over fixed-width `as_chunks::<4>()`: Callgrind 707.2 to 679.7 instructions per step at n = 53 (-3.9%, 1.040x), 706.5 to 679.0 at n = 41; outputs identical at n = 41, 53, 61, scalars independently verified. Native ns/step "not established": 1.117x at n53 rests on baseline drift (other readings 1.039 to 1.058x, inside the 7.0% A/A spread); a 16-round independent rerun read 0.989x; 1.076x at n61 inside the 14.4% A/A spread; counted GAE identical at weights 0, 0.1, 1 | `LEAD-RHO-native-step-cost` (top-5 hit, score 23) | `evidence` {crypto, `benchmarks/20261022-strong-rho-batchinv`}, {crypto, `research/rho_batchinv_20261022/README.md`}; append to `best_measured` "batch_inv_clmul fixed-width chunks: -3.9% Ir/step at n53 (instruction count only; native time not established, A/A spread 7.0%)". The lead's own 1,196 to 718 Ir figure is a different series (n not stated in the lead); do not combine. |
| `20261017-two-sylow-fp64` | `two_sylow_search` halving search on branch-free `Fp64` (PR #2034): ratios 0.98 to 1.02 and 1.02 to 1.08 (controls also read high); positive control 0.44, negative control within 4.5%; "neutral within resolution" | none: action `not_ecdlp` (an arithmetic-backend timing of a 2-Sylow halving search). It is a side control for the Fp64 branch-free PR that `LEAD-RHO-native-step-cost` already cites (`research/fp64_branchfree_20261016/README.md`). | no row edit proposed; if the reviewer wants the control recorded, `evidence` {crypto, `benchmarks/20261017-two-sylow-fp64`, "branch-free Fp64 neutral on the latency-bound two_sylow halving search"} on that lead. |
| `20261019-adaptive-pair-cells` | 1,237 positive-dimensional fixed-grid certificates; adaptive dimension-65 cells; original all-roots problem unresolved; external comparison not run | `LEAD-ICE-rootfind-pairtable-oracle` (top-5 for the 'Semaev root finding' phrasing, score 10) | see 2.15 |
| `20261017-rootfinding-paper-synthesis` | "Native coordinates 58,176 to 45,427; subsequent search UNKNOWN; no qualified speedup"; no new measurement | same | evidence only; the UNKNOWN is a bounded search outcome, not a result |
| `20261017-rootfinding-native-followup` | internal variables 58,176 to 45,427 (count only); changed bounded norm search UNKNOWN, 0 verified witnesses, no exact count, 61.794 s supervising wall; source-symmetry restoration passed 34,816 tiny assignments | same | evidence only |
| `20261018-factor-base-shape-leads` | On the degree-13 fixture `icv1-f2m13-t181-515ee569`: two 15-column trace-zero geometric-progression bases support 226 and 214 nonidentity target-subgroup points vs 144 for the 16-column coordinate base; fresh probes 15/128 and 17/128 verified decompositions vs 4/128; solving degree stays 3; changed bases increase successful F4 work; four primary degree-31 bases have zero supported nonidentity subgroup targets (study README) | `LEAD-ICB-factor-base-subspace-choice` (exhausted_at_scale). Top hits for the 'factor base shape' phrasing were `LEAD-ICB-nonlinear-frob-stable-bases` 19 and `LEAD-ICB-frobenius-orbit-factor-base` 16; I chose subspace-choice because its mechanism is the choice of V at fixed dimension and its `revisit_when` is the effect growing with n at n >= 31 | `evidence` {crypto, `research/factor_base_shape_leads_20261018/README.md`}, {crypto, `benchmarks/20261018-factor-base-shape-leads`}; note: "n = 13 finite-fixture yield difference for trace-zero GP bases; n = 31 bases tested had zero supported targets, so the revisit condition (null-controlled effect growing with n >= 31) remains untested". Disposition unchanged. |
| `20261019-factor-base-designs-ek1` | prime-field slope close-out: kappa = delta log2(field_ops) / delta b against the (m-1) break-even; every measured series with >= 3 cells is cost-unfavourable at the measured sizes, A0 at m = 4 inconclusive (2 cells). E-K1 Koblitz analogue, n in {11, 23}, m in {2, 3}: 306 rows, 250/250 completed traces replayed, 14/14 series with >= 3 cells kappa-unfavourable, S at m = 3 inconclusive (2 cells), 22 no-plant placeholders. A11 not measured. "No pipeline S or speedup" | prime close-out: `LEAD-ICP-coincidence-harvest-structured-base` (it uses the same break-even/kappa instrument: "kappa in [0.889, 1.103] ... kappa_rel 0.998"); E-K1: `LEAD-ICB-factor-base-subspace-choice`. Neither lead cites `research/factor_base_designs_20261015`. | `evidence` {crypto, `research/factor_base_designs_20261015/README.md`, "prime-field kappa close-out and E-K1: all series with >= 3 cells kappa-unfavourable at measured sizes; stage diagnostics only"}. I did not compare this row's kappa definition with EXP-PFDR-ca5e01's; verify before quoting numbers in `best_measured`. |
| `20261016-n83-prebuilt-factor-base` | three fresh native builds of a retained signed-Frobenius degree-83 panel (54 objects, 83,328,324 compressed bytes): build 59.518, 74.022, 169.555 s (max/min 2.85); replay 54/54 PASS each; "no speed ratio or admitted end-to-end IC improvement" | `LEAD-ICB-factor-base-subspace-choice` (with 2.9); related `LEAD-ICB-retained-setup-online` (closed_dominated, which remains true: this row reports no online comparison) | `evidence` {crypto, `benchmarks/20261016-n83-prebuilt-factor-base`}. |
| `20261018-pdp-ps3-bitsliced` | bit-sliced group-law oracle, 64/256/512 lanes, per target at l = 11 on two separate CPU hosts: baseline/arm 23.8x / 60.6x / 62.5x (host A) and 17.5x / 41.5x / 50.3x (host B); bs512/scalar 0.935x and 1.117x; 4-thread isolation requirement blocked; exact root-set and digest checks pass; "no end-to-end or ECC2K-130 claim" | `LEAD-ICB-generic-table-oracle` (closed_obstructed; constant-factor engineering of an enumeration oracle, which that lead says remains valid baseline work). Top-5 for the 'bit-sliced group-law' phrasing were `LEAD-ICE-rootfind-pairtable-oracle` 15, `LEAD-ICE-gpu-rootfind-oracle` 12, `LEAD-ICB-generic-table-oracle` 11; related `LEAD-ICE-sat-xor-pdp-oracle` | `evidence` {crypto, `benchmarks/20261018-pdp-ps3-bitsliced`, "constant-factor speed-up of the brute-force PDP oracle at l = 11; no end-to-end claim"}. The obstruction (Shoup / Corrigan-Gibbs-Kogan) is untouched by a constant. |
| `20261017-safecurves-trapdoor-slots` | sextic-twist census: weak non-quadratic sibling classes at rho work 2^28 (secp192k1), 2^55.5 (secp224k1), 2^65.5 (secp256k1); toy grind finds a strong published/twist pair with a weak sibling after 2 to 3 scanned primes at 48 and 96 bits, 40 scans at 128 bits; 256-bit probe stopped after 12 scans with seven orbits uncertifiable. "No deployed-curve weakness beyond the named census rows ... no key recovery" | `LEAD-STR-safecurves-parameter-audit` (closed_known; twist security). Related `LEAD-STR-curve-generation-provenance-seeds`. Top hits were `LEAD-TRF-teske-trapdoor-fp6-weak-class` 17 and `LEAD-TRF-teske-secret-isogeny-trapdoor` 13: not chosen, because this row is a count of grinding candidates among sextic twists of j = 0 curves, with no secret isogeny. | `evidence` {crypto, `benchmarks/20261017-safecurves-trapdoor-slots`, "sextic-twist weak-sibling census and toy grind counts; twist-level, no deployed-curve ECDLP bearing"}. `revisit_when` of both leads is not met: the weakness lives on a sibling twist, not on the published group. |

### 2.2 `docs/bounds/FRONTIER.md`

Observed. Generated by `ecbench frontier build`; header now "Frontier `ECFR1hbd02e945e867` (procedure 2), built from 94 bound(s)" (was `ECFR1h8b45b672c283`, 46 bounds). Commit messages: `e064d7d49e` "refit records under fit v2 and rebuild the frontier (procedure 2)"; `71004838b7` "keep every published v1 record, add fit-v2 twins" (46 v1 records kept byte for byte, 48 v2 bounds ranked, v1 listed as "historical: fit version 1, kept as published and re-derivable"). Procedure 2 differences visible in the file: dominance on `ops` and `memory`, read on shared curves; "clearly better" means disjoint 95% intervals; dominance must also hold at 0, 0.1 and 1 GAE per unpriced operation with the flip price printed; a frontier entry needs >= 4 sizes and the full curve set (a `--tier` fit is listed but not ranked); new columns for the ops tail (max/median, top run). Domains: Koblitz toy, Koblitz medium, prime toy. No prime medium tier exists.

`--match` ("measured bounds frontier ops memory rho bsgs kangaroo prime toy tier dominance"): `KR-RHO-cd0049` 24, `LEAD-RHO-matched-rho-calibration` 17, `KR-RHO-1c2928` 14, `LEAD-ICP-gfp5-rho-reference-audit` 11, `LEAD-RHO-cheon-toy-reproduction` 11. Seven leads already cite this file (`LEAD-RHO-bsgs-family-memory`, `-matched-rho-calibration`, `-automorphism-class-walks`, `-generic-sqrt-lower-bound`, `-kangaroo-interval`, `-negation-map-fruitless-cycles`, `LEAD-ICP-generic-table-decomposition`). The edit is therefore drift repair plus one changed interval, not a new lead.

**Edit 2.2a: IC exponent interval (prime toy tier, 4 shared sizes log2 r 17.7, 19.1, 21.2, 24.0, 96 runs).**

| arm | v1 (historical) | v2 (ranked) |
|:--|:--|:--|
| `ic.pipeline` prime-abscissa:size=32, `mitm:negation_folded=1`, `targets=walk`: ops 22.686 x floor [11.421, 40.107], tail 6.8x / 4%, memory unknown | `ECBND1hbab6d6dc37fc` alpha 0.841 [0.500, 1.024] | `ECBND1h93b7a9d5c187` alpha 0.841 [0.646, 0.953] |
| same, `oracle=subtract`: ops 1258.230 [395.647, 2482.904], tail 9.7x / 5% | `ECBND1h9d3beb6852c6` alpha 1.005 [0.786, 1.099] | `ECBND1h9879c0aa348f` alpha 1.005 [0.880, 1.077] |
| for comparison, same four sizes: `rho.negation` | `ECBND1h7b69b9787056` | `ECBND1h9896c8176a62` ops 1.466 [1.278, 1.653], alpha 0.454 [0.388, 0.593] |
| `bsgs.negation`, same four sizes | `ECBND1he0aea8671f10` | `ECBND1h04456c09d990` ops 1.160 [1.068, 1.248], alpha 0.460 [0.408, 0.495] |

(v1 to v2 pairing: confirmed from the committed twin files in `docs/bounds/records/` (`<name>.json` and `<name>-v2.json`, `bound_id` read from each) for `prime-ic-mitm`, `prime-ic-subtract`, `prime-rho-neg`; the `bsgs.negation` four-size row `ECBND1he0aea8671f10` cited by a KR row is matched by identical ops interval to `session-prime-toy-reference-e1-candidate-v2.json`, because the challenge incumbent has no same-name twin.) The two ic.pipeline rows are listed "no" (dominated); every dominated-by line for them says "memory unknown on one side and left out ... holds across the pricing band". The ic.pipeline alpha is a four-size toy-tier fit with memory unrecorded; the file treats four sizes as the threshold for a frontier entry, so four is the minimum, not a margin.

Reading (conditional): on the four shared sizes the v2 ic.pipeline interval [0.646, 0.953] and the v2 rho.negation interval [0.388, 0.593] do not overlap, and the subtract arm's [0.880, 1.077] is consistent with the exponent about 1 that `LEAD-ICP-generic-table-decomposition` records for exhaustive IC (0.99 at m = 2, 1.01 at m = 3). Nothing here is a charged exponent for the whole pipeline (GOAL-ICEX-001 still needs the backend named in `LEAD-ICE-charged-toy-ic-exponent-vs-rho`).

Proposed edits:

- `LEAD-ICP-generic-table-decomposition` (closed_obstructed): in `best_measured` replace "FRONTIER fitted exponent 0.841 [0.500, 1.024] for folded mitm m = 2" with "FRONTIER fit v2 (prime toy, 4 sizes) fitted exponent 0.841 [0.646, 0.953] for folded mitm m = 2 (`ECBND1h93b7a9d5c187`; v1 `ECBND1hbab6d6dc37fc` kept as historical), subtract arm 1.005 [0.880, 1.077]". No change to the obstruction or `revisit_when`.
- `LEAD-ICE-charged-toy-ic-exponent-vs-rho` (open_blocked): append the same interval pair to `best_measured` ("no IC arm has a fitted exponent below rho's" is consistent with it); keep `blocked_by`.
- `LEAD-RHO-matched-rho-calibration` (open_next_step): `best_measured` "prime toy rho.negation 1.453 x floor with alpha 0.398 [0.308, 0.476]" becomes "... alpha 0.398 [0.315, 0.475] (fit v2, `ECBND1h67e22de83dca`, 6 sizes log2 r 15.7 to 25.3)"; the sentence "no prime medium-tier bound exists" is still true of this file (medium domain is Koblitz only). `next_action` unchanged.

**Edit 2.2b: bound-id and frontier-id drift in leads (ids that still re-derive but are no longer ranked).** Pairings below are read from the twin files (`<name>.json` to `<name>-v2.json`, `bound_id` of each), not inferred.

| lead | cites | status at HEAD | v2 id (twin file) |
|:--|:--|:--|:--|
| `LEAD-RHO-automorphism-class-walks` | `ECBND1h05a2ea918f3c` (`rho.signed_frobenius_strong` 1.089 [0.927, 1.261], Koblitz medium) | historical v1 | `ECBND1hcf69c27b4978` (`pair-claw-koblitz-rho-strong-v2.json`; ranked, ops leader of the medium domain; alpha 0.451 [0.399, 0.503]; memory 0.008 / sqrt r; uncharged 0.271 / sqrt r; tail 2.7x / 2%) |
| `LEAD-RHO-bsgs-family-memory` | `ECBND1he8163c29cc39` (`bsgs.negation` 1.100 [0.978, 1.225], prime toy, 6 sizes) | historical v1 | `ECBND1h9d01a5c2ae56` (`calibration-prime-bsgs-neg-v2.json`; ranked, "frontier: yes") |
| `LEAD-RHO-kangaroo-interval` | `ECBND1hb4b4be548e88` (`kangaroo.vow` 2.203 [1.803, 2.527]) | historical v1 | `ECBND1h2e9e2024d8f3` (`calibration-prime-kangaroo-v2.json`; ranked, dominated) |
| `LEAD-RHO-negation-map-fruitless-cycles` | `ECBND1ha6fbf0c678d0` (`rho.negation` 1.453 [1.184, 1.772]) | historical v1 | `ECBND1h67e22de83dca` (`calibration-prime-rho-neg-v2.json`; ranked, "frontier: yes") |
| `LEAD-RHO-generic-sqrt-lower-bound` | quotes "bsgs.negation 0.529 [0.485, 0.596], prime toy" with no id | the same bound as `ECBND1he8163c29cc39` | v2 interval is 0.529 [0.486, 0.595]; the sentence "all generic arms fit alpha <= 0.53" still holds for every generic arm printed in the v2 file (largest point estimate 0.529) |
| six leads (`-matched-rho-calibration`, `-automorphism-class-walks`, `-generic-sqrt-lower-bound`, `-kangaroo-interval`, `-negation-map-fruitless-cycles`, `-bsgs-family-memory`) | evidence note "sealed frontier `ECFR1h8b45b672c283`: ops x floor sqrt(pi/2A), memory, alpha per method" | superseded by `ECFR1hbd02e945e867` (procedure 2, 94 bounds) | note text becomes "frontier `ECFR1hbd02e945e867` (procedure 2; fit-v2 bounds ranked, v1 historical)" |
| KR rows (note only, not edited): `KR-RHO-1c2928` cites `ECBND1h05a2ea918f3c`, `ECBND1hbc8602528f48`, `ECBND1hc2936a598d20`; `KR-RHO-cd0049` cites `ECBND1he0aea8671f10`, `ECBND1he8163c29cc39`, `ECBND1h7b69b9787056`; both also cite `ECFR1h8b45b672c283` | | all historical v1 | `ECBND1hcf69c27b4978`; `ECBND1h9684d410eb0d` (`session-koblitz-toy-reference-e1-candidate-v2.json`, by interval); `ECBND1h9ca30b59bfc6` (`calibration-koblitz-toy-rho-frob-v2.json`); `ECBND1h04456c09d990` (`session-prime-toy-reference-e1-candidate-v2.json`, by interval); `ECBND1h9d01a5c2ae56`; `ECBND1h9896c8176a62` (`prime-rho-neg-v2.json`). The KR sentence "no row improves on both ops and memory" was written under the v1 rule and is not re-evaluated here. |

Proposed edit: replace the id in each lead's `best_measured` with the v2 id and add "(v1 id kept as historical)"; replace the frontier id in the six evidence notes. Values do not change, except the generic-sqrt-lower-bound interval (0.485, 0.596 to 0.486, 0.595) and the `matched-rho-calibration` interval in 2.2a.

**Edit 2.2c: observed ranking changes, no lead edit needed.** Koblitz toy: the former ops and memory leader (`ECBND1hc2936a598d20`, `rho.signed_frobenius` 3.306, 3 sizes, one tier) is now "listed, not ranked"; the domain line reads "Ops: no leader named, the intervals do not separate". Koblitz medium: `claw.pair_table` base_scale=1.06, table_scale=0.03125 (ops 35.596 [28.645, 42.831], memory 0.004 / sqrt r, alpha 0.483 [0.379, 0.559]) is now "frontier: yes" as memory leader (`ECBND1h782964654934`), whereas the v1 listing had it dominated; the other `claw.pair_table` row (base_scale=4, table_scale=1: ops 2.390, memory 0.142, alpha 0.467 [0.426, 0.497]) is dominated by `rho.signed_frobenius_strong` "over 6 shared sizes; holds across the pricing band". Adding `memory` as an axis changes which rows are on the frontier; it does not change a measured value. Optional `evidence` note on `LEAD-ICB-generic-table-oracle`: "FRONTIER procedure 2: claw.pair_table trades 35.6x floor ops for 0.004 sqrt(r) memory; dominated on ops by strong rho at every table scale".

### 2.3 `docs/ic/LEADERBOARD.md`

Observed (git diff): the 13 Table B rows change from "unvalidated (pre-gate)" to "validated"; every S_IC, S_ref and x-reference value is unchanged (e.g. `icv1-fp24-t1577-77336155` 13.5x, `icv1-f2m27-t12543-569dca8b` 38.2x); `docs/curves/registry.json` sha256 changes (584d070fbec7e21f to 595b71600e1f471a). Commit `a8d8e3cd38` "Validate the 13 Table B rows through the gate; Table C fails" adds `docs/ic/runs/VALIDATION.json` and `research/ic_validation_gate_20261024/`. Table A (`re-run at baseline v3`, 5.23x to 21x) and Table C (3.62x to 14.9x) rows are still "unvalidated (pre-gate)".

From `research/ic_validation_gate_20261024/README.md` (summary): Table B 13/13 rows pass R1 to R4 (1,257 runs identical on independent replay; 1,578/1,578 negative controls rejected; 52 headline numbers recompute to 1e-9); IC/rho at the section 5a weights 0 / 0.1 / 1 is 4.66 to 16.30x for the eight prime rows (range computed by me from the README's per-row columns; extended-band minimum 4.05x at fp12) and 4.05 to 54.76x over all 13 rows; "validation says the numbers are what the archive says and the reference is fair, not that IC approaches rho". Table C 0/9 rows pass (R4: targets not archived; the rho reference is another study's batch walk; no band available). The study README's status line says the manifest is "staged", while the commit above installs it; the board at HEAD shows "validated", so the README status line predates the install.

`--match` ("IC leaderboard S_IC over S_rho validated gate prime field rows"): `LEAD-RHO-matched-rho-calibration` 12, `KR-IC-9e610d` 10, `KR-RHO-cd0049` 10, `LEAD-ICB-quasi-subfield-polynomials` 10, `LEAD-ICP-full-width-arity-grid` 10. The file is cited by 14 leads; the three whose text changes are below.

Proposed edits:

- `LEAD-ICP-prime-ic-constant-engineering` (open_next_step): `next_action.step` currently starts "Put the eight Table B prime rows through the validation gate (replay certificate, validator report, matched rho with the section 5a band, VALIDATION.json), then run the unimplemented two-level target batching ...". The first clause is done for the 8 prime rows (and the 5 random-binary rows). Proposed step: "Run the unimplemented two-level target batching (1024 targets in lock-step so the R <- R + G inverse is amortised) as a paired ecbench arm against the folded/walked m = 2 recipe at fp20 to fp28; Table B rows are validated (`research/ic_validation_gate_20261024`)". Add `evidence` {crypto, `research/ic_validation_gate_20261024/README.md`, "Table B 13/13 pass R1 to R4; prime rows IC/rho 4.66 to 16.30x over the 5a band, extended-band minimum 4.05x"} and {crypto, `docs/ic/runs/VALIDATION.json`, "admits the 13 Table B slugs"}. Disposition stays `open_next_step`.
- `LEAD-ICP-generic-table-decomposition`: in `best_measured` change "Table B prime ladder, unvalidated (pre-gate)" to "Table B prime ladder, validated (gate 2026-10-24); 5.47x (log2 r 11.9) to 13.5x (23.4) on the board, 4.05x to 16.30x across the 5a and extended bands".
- `LEAD-ICB-multi-target-and-portfolio` (closed_obstructed): its `best_measured` is Table C "3.62x (n41) to 14.9x (n19) above batch rho (reference from a different session)". Add: "Table C failed the validation gate 2026-10-24 (0/9 rows; R4: targets not archived, rho reference is another study's batch walk)" and `evidence` {crypto, `research/ic_validation_gate_20261024/README.md`}. This confirms the lead's own caveat; the obstruction is a theorem and is unaffected.
- `LEAD-ICB-generic-table-oracle`: Table A/B binary rows: no value change; add the same evidence path for the 5 random-binary Table B rows now validated.
- `LEAD-ICE-rootfind-pairtable-oracle`: `best_measured` "... prime Table B 5.47x-13.5x rho at 9.7-23.4 bits" gains "(validated, gate 2026-10-24)". Found by `grep -rnE "Table B|pre-gate|unvalidated" knowledge/leads/ecdlp`. Lines that carry a validation status and need the edit: `LEAD-ICP-prime-ic-constant-engineering` `next_action` (line 15, above) and its evidence note ("all Table B rows unvalidated (pre-gate)": the 13 Table B rows become validated, Table A and Table C stay pre-gate), `LEAD-ICP-generic-table-decomposition` `best_measured` and its evidence note ("Table B prime rows fp10..fp24, all unvalidated (pre-gate)"), and the `LEAD-ICE-rootfind-pairtable-oracle` quote above. Lines that mention Table B without a validation claim and need no edit: phase-share mentions in `LEAD-ICE-relation-graph-rank-large-prime`, `LEAD-ICE-gpu-rootfind-oracle`, `LEAD-ICP-prime-ic-constant-engineering` (mechanism text), and the gap-widens mentions in `LEAD-ICP-generic-table-decomposition`.

### 2.4 `problems/README.md` (index)

Observed: +7 index rows (NIST extension-twist, NIST archive publication, rho worker, SQISign gate, N83 prebuilt base, p61 terminal closure, claim-n13) and two edited rows (k5 Joux-Vitse: adds the Edwards-route figures; rootfinding: adds "2026-10-19 conditional pair-cell evidence added"), each pointing to a file folded below. It carries no mechanism of its own. Action `not_ecdlp` (index). No `--match` is meaningful for an index; each target file was matched on its own.

### 2.5 `problems/certicom-binary-gpu-rho-integration.md` (modified)

Observed. Status `partial`. Host-verified native arithmetic for exact ECCp-131 and ECC2-131 (256 field-vector sets and 16 scalar vectors per curve, point identities, four subgroup checks); CUDA device replay not run (the AWS GPU job "was rejected before instance creation because the AWS GPU vCPU quota is zero"). Lines added since the reviewed commit: 2026-10-22 single-core CPU baseline for the three 131-bit targets (batched-inversion walks, ECC2-131 8.50 M and ECCp-131 1.23 M steps/s, `research/certicom131_rho_ic_bench_20261022/`); 2026-10-23 parity study (ECCp-131 AVX-512 walk 15.06 M and ECC2-131 bitsliced walk 11.46 M steps/s against 10.3 M for the ECC2K-130 client, one isolated session, all gates passing, `research/certicom131_rho_parity_20261023/`); 2026-10-23 CUDA port (kernels compile for sm_80 to sm_90, retargeted sm_120; "`walk_cuda` has not run on a GPU", `research/certicom131_cuda_port_20261023/`). The record states the host and CPU results are not GPU results.

`--match` top lead: `LEAD-RHO-prime-gpu-rho` 19 (second phrasing 21, tied with `LEAD-RHO-ecc2k130-gpu-fpga-throughput` 21). The lead already lists this problem as its blocker.

Decision: advances_lead `LEAD-RHO-prime-gpu-rho`. Proposed edits: add `evidence` {crypto, `research/certicom131_rho_ic_bench_20261022/README.md`}, {crypto, `research/certicom131_rho_parity_20261023/README.md`}, {crypto, `research/certicom131_cuda_port_20261023/README.md`, "CUDA port compiles; no device run"}; append to `best_measured`: "Certicom 131-bit CPU baselines (single core, descriptive, not GPU): ECCp-131 AVX-512 15.06 M steps/s, ECC2-131 bitsliced 11.46 M steps/s; no CUDA device result". `next_action` unchanged (the record's own next step is `gpu/certicom131/test_cuda.cu` on an approved CUDA 13.x RTX PRO 6000 runner). Disposition stays `open_blocked`. Also `LEAD-RHO-native-step-cost`: append the same two CPU step rates to `best_measured` (descriptive). ECC2-131 is a random binary curve (the record: "Random binary curves cannot inherit a Koblitz Frobenius quotient"), so these walks do not execute `LEAD-ICB-koblitz-rho-reference`'s "131-bit signed-Frobenius walk" for ECC2K-130.

### 2.6 `problems/ecbench-claim-n13-replay-accounting-version-drift.md` (new)

Observed. Replay of `research/ecbench_rootfind_engine_20261012/sessions/claim-n13` (96 problems, all in the `ic-f4-m2` / `ic-f4-m3` arms; the 72 rho rows reproduce) fails on current main because the session was recorded at `2245b75` (Apple M4 Pro, non-BMI2 host, inherited-F4 specialisation charged lazily) and main charges it eagerly on every host. BMI2 and portable paths agree on main (byte-identical `solver.ops`, counters and phase natives on 224 records). A temporary lazy build reproduces the recorded `solver.ops` on all 32 `ic-f4-m2` rows; `ic-f4-m3` still differs: recorded 8,412,139, lazy 9,399,398, eager 10,914,662 (ratios to recorded 1.117 and 1.298, arithmetic mine). Seq 58 `cost.total_gae` 741.09 recorded vs 1,433.5 replayed (measured vs pinned pricing, separate). Status `open`; next step: replay with the `2245b75` binary, then an owner decision on the accounting identity plus a method-identity field.

`--match`: `KR-IC-f3da82` (F4 trace reuse) 9, then `LEAD-ICE-hybrid-guess-determine-l7` 5; neither is the same mechanism. The lead that already cites the same issue is `LEAD-ICE-boolean-f4-f5-f6-engines` (closed_dominated; its evidence includes `research/validation_sweep_20261019/D-known-issues/` and `.../item1_cross_isa_20261020/RESULT.md`, the problem record's other affected-work item), found by research-directory lookup, not by `--match` (not in either top 5).

Decision: advances_lead `LEAD-ICE-boolean-f4-f5-f6-engines`, evidence only. Edit: add `evidence` {crypto, `problems/ecbench-claim-n13-replay-accounting-version-drift.md`, "inherited-F4 counted work is accounting-version dependent: n13 ic-f4-m3 recorded 8.41 M vs lazy 9.40 M vs eager 10.91 M ops; ic-f4-m2 lazy reproduces the record"}. Reading (conditional): the lead's "priced inherited F4 about 22x-33x strong rho at n13" is a ratio built on one accounting definition; the record gives a change of at most 1.30x in the F4 op count between the two definitions on the arm where they differ, which does not change the direction of "dominated by the pair table" but does mean the quoted band is not definition-independent. I did not open the sessions to confirm which one produced the 22x-33x figure. No disposition change; `revisit_when` untouched.

### 2.7 `problems/eccp131-full-parameter-index-calculus.md` (modified; 2 lines added)

Observed. Exact Certicom ECCp-131 (prime n = `0x048E1D43F293469E317F7ED728F6B8E6F1`, cofactor 1). Bounded exact-curve probes by `ic prime --curve eccp-131`: two-point B512 seed 131 gives 262,144 distinct pair-sum abscissae (matches an independent PARI/GP enumeration), 8/8 planted controls pass, 128 natural setup candidates give zero relations and rank 0, 128 target-descent candidates give zero relations; stage matrix of 20 processes at B256 / B512 / B1024 all zero natural relations, rank 0; three-point B128, two seeds, paired two-point controls, zero natural rows, rank 0 in all four processes; the 2026-10-22 x86 baseline (25 runs, B256 to B1024 two-point and B128 three-point) reproduces zero relations and rank 0. Support bounds stated in the record: two-point `2B^2/(n-1)` = 2^-103.1875 per uniform candidate at the CLI cap B = 8192 (at least 2^116.188 candidate trials for B+1 rows if every hit were independent); three-point `8B^3/(n-1)` = 2^-88.1875 at B = 8192 (2^101.188 trials). The record: "a coverage bound for this factor base and two-sum oracle, not a lower bound for all index-calculus methods"; `ca-ic prime --curve eccp-131` in `cryptanalysis` "still executes its relation pipeline on a generated smaller curve" (for that group's fold). No scalar for the published Q.

`--match` (three phrasings, section 6): top hits `KR-IC-5931ee` 27, `LEAD-ICP-isogeny-transported-relation-yield` 24 / 22, `LEAD-ICE-decomposition-probability-audit` 20, `LEAD-ICP-full-width-arity-grid` 17, `LEAD-ICB-factor-base-subspace-choice` 16. No lead cites ECCp-131 index calculus. The lead I propose, `LEAD-ICP-generic-table-decomposition`, is in none of the top 5; reason: its obstruction ("any decomposition oracle that enumerates or table-looks-up factor-base elements ... T >~ sqrt(N)", arity 2 to 7, measured at 12 to 32 bits) and its `revisit_when` ("a non-generic decomposition oracle ... per-attempt cost T_dec << p^{1/4} at arity m = 4, or a decomposition test sub-linear in |F|") describe exactly what the record's next step asks for ("an exact-curve relation oracle whose measured independent-row rate escapes the 8B^3 support limit"). Closest top-5 hit, `LEAD-ICP-isogeny-transported-relation-yield` (open_blocked), concerns transported bases across volcano levels and is not the same mechanism. `LEAD-ICP-full-width-arity-grid` (open_blocked, 50 to 63-bit grid) is the neighbour for width.

Decision: advances_lead `LEAD-ICP-generic-table-decomposition`; related `LEAD-ICP-full-width-arity-grid`, `LEAD-ICP-algebraic-membership-factor-base` (conservation law: mean yield of any size-B base is `binomial(B+m-1, m)/N`; the record's `2B^2/(n-1)` and `8B^3/(n-1)` bounds are the same kind of count at n about 2^131, reading conditional on the signed-point convention matching). Proposed edits: add `evidence` {crypto, `problems/eccp131-full-parameter-index-calculus.md`}, {crypto, `research/eccp131_bsgs_ic_20261020/REPORT.md`}, {crypto, `research/eccp131_bsgs_ic_20261020/reports/run-20261022T0523Z/REPORT.md`}; append to `best_measured`: "exact ECCp-131 (131-bit prime order): two-point (B256 to B1024) and three-point (B128) small-x probes, zero natural relations and rank 0 in every bounded process; per-candidate support bounds 2^-103.19 (two-point) and 2^-88.19 (three-point) at B = 8192; scale reached, not a cost"; append to `forecloses`: "ECCp-131 exact-curve small-x two-point or three-point relations". Disposition unchanged; the record explicitly does not claim an obstruction beyond the method-specific support bound.

### 2.8 `problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md` (modified)

Observed (record last updated 2026-10-20). Joux-Vitse (n-1)-decomposition on E(F_{q^5}): complete DLPs at p = 11 (three seeds) and p = 31 with every relation re-added and every trial's decompositions equal to an independent meet-in-the-middle oracle, IC/rho about 4e7 to 7e7 (plain route); trial-cost ladder p = 11 to 241; trial constant C'' = 1.104e10 F_p multiplications on the current engine ("flat in q"); counting-bound rate `16*C(|F|+3,4)/#E`; Problem text: about 24q trials per relation, q/2 relations needed, cost about `12 q^2 C_trial` against rho about `0.89 q^{5/2} c_add`, ratio `sqrt(q*/q)` with q* about 2^55. Edwards 2-torsion route end to end with F4 trace replay (2026-10-20): replay cuts the four-point test 1.74 to 1.77x (5.85e7 to 3.3e7), below the 3 to 10x RESEARCH_K5 section 5 priced; five complete verified DLPs at log2 n = 22.8 to 28.7 cost 1.2e6 to 5.8e6 times rho (4.1e5 to 1.9e6 with rho's unpriced walk work at 1 GAE); a sixth stopped at its cap at >= 1.5e7; extrapolated parity n about 2^227 (was 2^233). The study README adds: Edwards test 3.3e7 replayed against 7.5e9 plain. The record: "No lower bound on C_trial is proved"; "does not establish that no k = 5 route reaches parity".

Units. `MODEL.md` (`research/joux_vitse_n1_20261015/`) gives q* about 2^55.3 (a base-field size, group about 2^276) using the paper's c-tilde = 3e9, kappa = 24, c_add about 190; the "n about 2^227 / 2^233" figures are group orders for the Edwards route. A reviewer's arithmetic check (not a record statement): the same formula with the measured C'' = 1.104e10 gives q* of order 2^59, not 2^55; I did not rerun the study's computation, so confirm against MODEL.md's measured table before quoting a q* in a lead.

`--match` ("Joux-Vitse decomposition ..."): `LEAD-ICP-gfp5-rho-reference-audit` 15, `LEAD-ICE-rootfind-pairtable-oracle` 14, `LEAD-ICP-gfp5-oa-sdhp-jv` 14; second phrasing: `KR-IC-081a58` ("Joux-Vitse n-1 decomposition and oracle-assisted static DH") 20, `KR-IC-f3da82` 19, `KR-IC-955fd6` ("Symmetries and torsion speed up point decomposition") 12, `LEAD-ICP-gfp5-oa-sdhp-jv` 11.

Decision: advances_lead `LEAD-ICP-gfp5-oa-sdhp-jv` (open_next_step; `best_measured: None`; `next_action`: "Freeze the JV/Granger sources, measure C_pdp4 at toy p' and project to p = 2^64 (H-GFPN-3366ea), and file the JV (n-1) full-ECDLP closure arithmetic (goal criterion C5)"). The record supplies the toy-p' trial-cost measurement and the closed-form projection, but cites neither H-GFPN-3366ea nor criterion C5, so the projection to p = 2^64 and the closure arithmetic are not shown as done. Proposed edits: add `evidence` {crypto, `problems/k5-joux-vitse-trial-cost-and-fpk-ecbench.md`}, {crypto, `research/joux_vitse_n1_20261015/README.md`}, {crypto, `research/joux_vitse_n1_20261015/MODEL.md`}; set `best_measured` to "k = 5 (n-1)-decomposition trial constant C'' = 1.104e10 F_p mults (p = 11 to 241); complete DLPs IC/rho about 4e7 to 7e7 (plain, p = 11, 31) and 1.2e6 to 5.8e6 (2-torsion Edwards with F4 trace replay, log2 n 22.8 to 28.7, five verified, one capped at >= 1.5e7); extrapolated parity q* about 2^55 (paper constants; group about 2^276) or n about 2^227 (Edwards + replay); extrapolation on measured constants, not a measurement at those sizes"; leave `disposition: open_next_step` and trim the first clause of `next_action` only after a reviewer confirms the p = 2^64 projection is filed. Related: `LEAD-ICP-gfp5-symmetrized-gaudry` (its next step H-GFPN-6cc6aa measures a degree-4 Macaulay rank of the 2-torsion quotient): the Edwards 2-torsion model is a measured 2-torsion lever on the test cost (7.5e9 to 3.3e7 including replay), add as `evidence` there.

### 2.9 `problems/n83-prebuilt-base-quality-m2-m4.md` (new)

Observed (opened 2026-10-16, status `open`). Problem: no matched natural-relation, useful-rank and complete-pipeline measurement exists for a prebuilt base at m = 2, 3, 4 on `icv1-f2m83-tm6151469093347-debefd74` (81-bit subgroup). Tested primary bases: 64 / 256 / 600 signed-Frobenius columns (10,624 / 42,496 / 99,600 points); structured dimension-12 closure 2,001 columns / 332,166 points; explicit-orbit comparator 2,048 columns / 339,968 points. Sweep: 1,728 dependent two-summand fixed-point probes, zero relations; bounded m = 3 attempt did not finish a query; the five-summand search reached a conflict cap. Support screen (model-specific): full-smooth hit probability of a uniform nonidentity target at K = 600: m = 4 at most 1.695987e-6, m = 3 6.810989e-11, m = 2 2.051462e-15; 22,945,941,707 materialized root states at K = 16,627 where the m = 4 counting ceiling becomes vacuous. Next step: a full-width m = 4 retained-base adapter (source-to-orbit, group lift, rank), then a paired run of the two bases.

`--match`: `LEAD-ICB-frobenius-orbit-factor-base` 19, `LEAD-ICP-isogeny-transported-relation-yield` 16, `KR-IC-b0fcda` 14, `LEAD-ICB-factor-base-subspace-choice` 13, `LEAD-ICB-nonlinear-frob-stable-bases` 13; second phrasing: `LEAD-ICB-frobenius-orbit-factor-base` 16, `LEAD-ICB-nonlinear-frob-stable-bases` 14, `LEAD-ICP-retained-setup-online` 13, `LEAD-EXO-dl-character-sum-pseudorandom` 12, `LEAD-ICB-cofactor-torsion-quotients` 12 (subspace-choice is not in that top 5). I chose `LEAD-ICB-factor-base-subspace-choice` (exhausted_at_scale) over the top hit because `LEAD-ICB-frobenius-orbit-factor-base`'s obstruction is the proof that the orbit gain is exactly n, which this record does not contest; this record compares retained bases at fixed size, which is the subspace-choice mechanism, and its `revisit_when` ("a property of V that predicts N_var or yield with a null-controlled effect that grows with n at n >= 31") is the condition an n = 83 paired m = 4 run would test.

Decision: advances_lead `LEAD-ICB-factor-base-subspace-choice`, evidence plus a pointer; related `LEAD-ICB-kic-golden-base-exact-decomp` (co-designed binary bases). Edits: add `evidence` {crypto, `problems/n83-prebuilt-base-quality-m2-m4.md`, "n = 83 retained-base comparison at m = 2..4 unmeasured; the paired m = 4 run is the first n >= 31 test of this lead's revisit condition"}, {crypto, `research/n83_prebuilt_factor_base_20261016/REVIEW.md`}, {crypto, `research/koblitz_n83_factor_base_sweep_20261008/SUPPORT_MOMENTS.md`}. Disposition unchanged (nothing measured at n = 83 yet).

### 2.10 `problems/nist-extension-twist-composite-cofactors.md` (new)

Observed (status `open`, last updated 2026-10-23). Target: orders N = (p-1)^2 + t^2 of the degree-2 extension twist of the NIST curves. R02: eight of nine distinct targets completely factored, all nine final partitions pass native PARI certificate replay and exact product verification (Lean `ProductIdentities.lean` over `Nat`); one explicit composite 444-bit residual (P-256 block 876) remains; the former 327-bit P-224 block-5736 and 364-bit published P-224 residuals are prime-certified. Limits: P-1/P+1 plus 100 allocated ECM curves at B1=11,000,000 per lineage (P-256 lineage attempted 92, stage 2 on 91, exit 124); NFS exit 137 in polynomial search; R03 duplicate-search restore failure; R04 exit 137 with no new factor; R05 3,600 s local run ended exit 139 (segfault), 3,164,757 raw-relation lines kept, a patched binary reproduces exit 139 vs 0 on a small input; FactorDB returns no additional factors (2026-10-23); R06 1,800 s continuation had two workers running at the record's last observation, final status pending. The record: these failures "are inconclusive, not negative mathematical results"; "No smallest-prime-factor lower bound follows".

`--match`: `LEAD-STR-curve-generation-provenance-seeds` 9 and 14, `LEAD-TRF-curve-parameter-transfer-audits` 6 and 14, `LEAD-STR-safecurves-parameter-audit` 9. No lead cites `research/nist_skipped_curve_dissection_20261021`.

Decision: advances_lead `LEAD-STR-curve-generation-provenance-seeds` (exhausted_at_scale), evidence only; its listed screens already include "twist factors". The unsplit residual keeps this one screen (degree-2 extension twist) incomplete, and an incomplete factorization is not a weak-class finding and not an obstruction. Edit: add `evidence` {crypto, `problems/nist-extension-twist-composite-cofactors.md`, "degree-2 extension-twist orders of the nine skipped/published NIST targets: 8 of 9 completely factored and certified; P-256 block-876 444-bit residual unsplit after ECM/NFS attempts (inconclusive); no weak-class bearing observed"} and {crypto, `research/nist_skipped_curve_dissection_20261021/factorization/README.md`}. `revisit_when` not met.

### 2.11 `problems/nist-factorization-raw-archive-publication.md` (new)

Observed. Access/tool limit: the R02 and R05 NFS raw archives exceed GitHub's 100 MB file limit, and the runtime has no configured AWS identity for `s3://crypto-autoresearcher/store`; deterministic local archive, byte count and SHA-256 are preserved in the R02 and R05 manifests; results, prime certificates, Lean proofs and a compact P-256 checkpoint are committed. `--match` best: `LEAD-ICB-free-relations-self-collision` 6 (lexical overlap on "relations"), then `LEAD-ICP-residual-partial-relations` 6; neither is the same subject. Decision: not_ecdlp (storage access). It is only the durability gap behind the evidence cited at 2.10; no lead edit.

### 2.12 `problems/p61-registered-root-terminal-closure.md` (new)

Observed (status `resolved`, 2026-10-23, Conductor T-4942). Census of `p61-i0025` over p = 2^61-1 (fundamental discriminant -8726545188371316595, unconditionally certified class number 358,094,304, per `problems/p61-full-isogeny-class-census.md`): the terminal range [19890496, 19894128) could not close because the degree-13 closure compared the generic canonical representative with the registered root model coefficient by coefficient although both are F_p-isomorphic. Successor source `3b66e5cae94ab709f2ba2169e181eb0d3ac1c9e2` closed all 18 lanes, 65,376 nodes, 18 closures, `next_x=19894128`; release-library suite 4,081 passed / 0 failed / 114 ignored on the source head and 4,479 / 0 / 119 on rebased main. The record: global uniqueness, complete adjacency, endpoint resolution and hardness-model training "remain separate obligations".

`--match` (three phrasings): `LEAD-STR-isogeny-transport-preprocessing` 12, `LEAD-STR-p192-class-cm-relations` 12, `LEAD-TRF-jv-sieve-fp6-weak-class` 11, `LEAD-TRF-prime-field-isogeny-to-weak` 11; third phrasing ("learning corpus hardness predictor isogeny class vertices training table"): `LEAD-EXO-ml-learned-models` 18 (top), then `LEAD-STR-isogeny-transport-preprocessing` 16. None of these is the mechanism of this record (an enumeration capability bug); the best hit I can quote is `LEAD-EXO-ml-learned-models` 18, "Machine learning / neural and RL approaches to ECDLP and its subroutines", whose evidence includes `research/ec_hardness_predictor_20261010/README.md` (it names milestone M7), and the census problem record says the census does not complete "a diverse-field training corpus, or the M7 geometry-specificity validation".

Decision: `unclear`. No ECDLP measurement; it is census infrastructure whose stated downstream use is a hardness-model corpus. If the reviewer wants it recorded, the least-claiming edit is an `evidence` entry on `LEAD-EXO-ml-learned-models`: {crypto, `problems/p61-registered-root-terminal-closure.md`, "p61-i0025 census substrate (358,094,304 vertices) complete; uniqueness/adjacency and corpus use open; no ECDLP result"}. No disposition effect.

### 2.13 `problems/prime61-horizontal-class-memory.md` (modified; 62 lines added)

Observed (status `open`, last updated 2026-10-18). Curve `y^2 = x^3 + (p-3)x + 111`, p = 2^61-1, prime order 2,305,843,010,818,082,053, discriminant -6649310858224389603 fundamental (conductor 1, no vertical base-field edges). Old walker: 240 bytes per Node and 152 per Edge give 26,719,514,040 bytes before heap against a 17,179,869,184-byte limit (this applies to the retained-node/edge backend). One class has certified order 68,162,026, so the class has at least that many vertices; the design note derives at least 545,296,208 from genus vectors (conditional on replay C1) and PARI's conditional h agrees. Disk-backed worker: pilot 250 curves, 480 verified maps, 768 capped streams; continuation (2026-10-18): 1,344 discovered curves, 256 expanded sources, 3,840 verified maps, 512 measured curves, 6,144 committed streams, 614,400,000 target trials, zero relations or solves. Study README (`research/prime61_isogeny_20261016/`): "a null relation-stage result, not a measured improvement"; the factor base is three inverse pairs; every stream reached its cap. Designed envelope (not run): enumeration 716 core-hours and 562 GB; measurement 217,361 core-hours (about 283 days on 32 vCPUs); total about 234,936 core-hours. Not established (the record): exhaustive reachability, a certified full class count, any full-class ranking, a cost gain, or impossibility of enumeration.

`--match` (three phrasings): first two: `LEAD-TRF-jv-sieve-fp6-weak-class` 17, `LEAD-STR-p192-class-cm-relations` 15, `KR-IC-791cb7` 14, `LEAD-STR-isogeny-walk-weak-neighbour` 22, `LEAD-TRF-prime-field-isogeny-to-weak` 17; third ("map target to isogenous curves relation stage factor base inverse pairs transported instance horizontal edges"): `LEAD-ICP-isogeny-transported-relation-yield` 16 (top lead), `LEAD-STR-class-representative-ic-selection` 13; fourth ("choose isogenous curve class member cheapest index calculus relation yield per vertex"): `LEAD-STR-class-representative-ic-selection` 20, `LEAD-ICP-isogeny-transported-relation-yield` 16. Not `new_mechanism`: the mechanism (run a relation stage on isogeny-transported instances and compare yield across class members) is the one those two leads hold; this record extends it to horizontal class members at 61 bits.

Decision: advances_lead `LEAD-ICP-isogeny-transported-relation-yield` (open_blocked; `blocked_by` `problems/prime-field-arity3-relation-oracle.md`, not touched by this record); related `LEAD-STR-class-representative-ic-selection`. Edits: add `evidence` {crypto, `problems/prime61-horizontal-class-memory.md`}, {crypto, `research/prime61_isogeny_20261016/README.md`}, {crypto, `research/prime61_disk_continue_20261018/README.md`}; append to `best_measured`: "61-bit horizontal class (p = 2^61-1, prime order, conductor 1): 512 measured curves, 6,144 capped streams, 614,400,000 target trials with three inverse pairs, zero relations or solves; bounded null at the scale reached, class coverage not certified". A capped null is not an obstruction, so the disposition stays `open_blocked`. Also `LEAD-STR-isogeny-walk-weak-neighbour` and `LEAD-TRF-prime-field-isogeny-to-weak` (closed on class-invariant weaknesses) are unaffected: the 61-bit panel measures a non-invariant quantity (relation yield) and finds none in its bounded streams.

### 2.14 `problems/rho-worker-tier1-host-access.md` (new)

Observed (status `open`, last updated 2026-10-19). secp256k1 serial and opt-in batch rho worker paths replay the same frozen walk outputs (rebased suite 4,396 passed; local 32-Q replay 64/64 arms, 32/32 exact-output pairs). Five RunPod attempts, each aggregate `unknown_gate_failed` (A/A outside [0.90, 1.11] in attempts 1 and 2; thread or `runc` host-affinity in 3 to 5). Physical-host `m5zn.metal` r5 panel: independent audit of all 768 arms and 384 pairs shows no invalid arms or pairs; one of 256 A/A controls read 1.123159 above the 1.11 limit, aggregate `unknown_gate_failed`; comparison-only diagnostic median Q-cluster ratio 5.110, diagnostic 95% interval [5.041, 5.165]; "serial routing remains the default until a prospective gate passes". Open: a separate dedicated host (AWS quota), then a 768-arm, 384-pair panel on 32 fresh Q points with a qualified 95% lower bound above 1.05.

`--match`: first phrasing `KR-RHO-0528e7` 14, `KR-RHO-46c2c6` 14, `LEAD-ICB-multi-target-and-portfolio` 13, `LEAD-RHO-automorphism-class-walks` 13, `LEAD-STR-automorphism-quotient-rho` 13; second phrasing `LEAD-RHO-batched-inversion-shared-pm` 10, `LEAD-RHO-pool-class-quotient` 10, `KR-RHO-cb1c58` ("Simultaneous (batched) inversion") 9. Chosen: `LEAD-RHO-batched-inversion-shared-pm` (closed_known), because the compared arms are serial vs batched affine steps; `LEAD-RHO-native-step-cost` (admitted CPU timing) is the neighbour but is in neither top 5.

Decision: advances_lead `LEAD-RHO-batched-inversion-shared-pm`, evidence only. Edit: add `evidence` {crypto, `problems/rho-worker-tier1-host-access.md`, "secp256k1 serial vs batch worker: exact replay passes; aggregate unknown_gate_failed (5 hosted attempts, physical-host r5 1/256 A/A at 1.123 > 1.11); diagnostic 5.11x not admitted; serial stays default"}, {crypto, `experiments/rho-worker-phase-profile-20261017/README.md`}. No `best_measured` change (the 5.11 figure is not admitted). `revisit_when` ("an inversion-free step cheaper than 1I/n + 3M per walk") untouched.

### 2.15 `problems/rootfinding-complete-cost-calibration.md` (modified; 8 lines added)

Observed. Added section "2026-10-19 generalized all-roots conditional-cell follow-up" and the status text "open; 2026-10-19 conditional pair-cell evidence added". Quoted: the cycle "proves exact fixed-sum pair recovery and adaptive empty affine cells of dimension 65 on GF(2^83), d18. These are conditional first-S3 components. They do not resolve the full 339-coordinate hard root set, its 2^101 outer (p,s) grid, all requested field families, or the matched full all-roots F4/F5/F6 performance gate. No speed ratio is inferred from cells or timeouts." The next experiment is a draft union/residual card (`backlog/XP-20261019-adaptive-pair-cell-union/README.md`, not queued); native component tests pass; legacy sparse Python-suite validation incomplete. The older exit criteria (serialize and price native work, L2 isolation, independent host) are unchanged and still open.

`--match` first phrasing: `LEAD-ICP-prime-ic-constant-engineering` 17, `LEAD-ICB-generic-table-oracle` 11, `LEAD-ICB-koblitz-rho-reference` 10, `LEAD-ICE-rootfind-pairtable-oracle` 10, `LEAD-ICB-koblitz-setup-phase-cost` 9; second phrasing: `KR-IC-791cb7` 6, `KR-IC-f3da82` 6, `LEAD-ICB-generic-table-oracle` 6, `LEAD-TRF-miller-cocycle-nonhom-transfer` 5, `KR-IC-0d2021` 4 (no rootfinding lead in that top 5). Chosen: `LEAD-ICE-rootfind-pairtable-oracle` (open_blocked; this file is its `blocked_by` and is already in its evidence list, together with `problems/generalized-rootfinding-all-roots-8x.md`).

Decision: advances_lead `LEAD-ICE-rootfind-pairtable-oracle`. Edits: add `evidence` {crypto, `research/autolab_cycle_20261019_v3/REPORT.md`, "exact fixed-sum pair recovery and adaptive empty affine cells (dim 65, GF(2^83), d18); conditional components, no speed ratio"}, {crypto, `benchmarks/20261019-adaptive-pair-cells`}, {crypto, `backlog/XP-20261019-adaptive-pair-cell-union/README.md`, "draft completeness card, not queued"}; `blocked_by` text and `next_action` unchanged (pricing of native primitives and L2 replay are still the gate). Related: `LEAD-ICE-boolean-f4-f5-f6-engines` (closed_dominated): its `revisit_when` names a descended cell where the pair table is infeasible; this record does not claim such a cell is measured. The three rootfinding benchmark rows (2.1b) fold into the same lead; their UNKNOWN search outcomes are bounded and not evidence.

### 2.16 `problems/sqisign-statistical-root-gate.md` (new)

Observed (status `investigating`, last updated 2026-10-16). The serial full suite at source `3ce9694` completed 4161 passed / 1 failed / 117 ignored, exit 101; the SQISign test drew a random signing instance over a 37-vertex graph, verified 4000 tampered messages and required an acceptance rate strictly between 1/(37*4) and 4/37; 27 of 4000 were accepted (0.00675, below 1/148). One bounded whole-module retake passed 14/0/0. Cause unknown; the failing run did not retain its random seed. `--match` best: `LEAD-EXO-methodology-instruments` 8 ("Program methodology: instrument calibration, nulls, findings promotion"), then `LEAD-ICE-semaev-cover-monodromy` 6; not the same subject: that lead is about ECDLP screening instruments, this is a unit test of a signature-scheme implementation inside a release gate. Decision: not_ecdlp; no lead edit.

## 3. Index: which leads receive edits

| lead | sections | kind of edit |
|:--|:--|:--|
| `LEAD-ICB-koblitz-setup-phase-cost` | 2.1a | evidence x4, `best_measured` append, optional `next_action` baseline wording |
| `LEAD-ICB-koblitz-rho-reference` | 2.1a | evidence, `best_measured` append, `next_action` partly executed |
| `LEAD-ICB-generic-table-oracle` | 2.1a, 2.1b, 2.2c, 2.3 | evidence only |
| `LEAD-RHO-native-step-cost` | 2.1b, 2.5 | evidence, `best_measured` append (descriptive) |
| `LEAD-ICP-prime-ic-constant-engineering` | 2.3 | `next_action.step` first clause done; evidence |
| `LEAD-ICP-generic-table-decomposition` | 2.2a, 2.3, 2.7 | `best_measured` edits (interval v2, "validated"), evidence, `forecloses` |
| `LEAD-ICE-charged-toy-ic-exponent-vs-rho` | 2.2a | `best_measured` append |
| `LEAD-ICB-multi-target-and-portfolio` | 2.3 | `best_measured` note (Table C failed gate), evidence |
| `LEAD-RHO-automorphism-class-walks`, `-bsgs-family-memory`, `-kangaroo-interval`, `-negation-map-fruitless-cycles` | 2.2b | bound-id and frontier-id update (values unchanged) |
| `LEAD-RHO-matched-rho-calibration` | 2.2a, 2.2b | `best_measured` alpha interval v2; frontier id in evidence note |
| `LEAD-RHO-generic-sqrt-lower-bound` | 2.2b | `best_measured` interval 0.486, 0.595; frontier id in evidence note |
| `LEAD-RHO-prime-gpu-rho` | 2.5 | evidence x3, `best_measured` append |
| `LEAD-RHO-batched-inversion-shared-pm` | 2.14 | evidence only |
| `LEAD-ICE-boolean-f4-f5-f6-engines` | 2.6 | evidence only |
| `LEAD-ICP-gfp5-oa-sdhp-jv` | 2.8 | `best_measured` set (was None), evidence |
| `LEAD-ICP-gfp5-symmetrized-gaudry` | 2.8 | evidence only |
| `LEAD-ICB-factor-base-subspace-choice` | 2.1b, 2.9 | evidence, pointer to the revisit condition |
| `LEAD-ICP-coincidence-harvest-structured-base` | 2.1b | evidence (kappa close-out; verify definition first) |
| `LEAD-ICE-rootfind-pairtable-oracle` | 2.1b, 2.3, 2.15 | evidence; `best_measured` "validated" tag on the Table B quote |
| `LEAD-ICP-isogeny-transported-relation-yield` | 2.13 | evidence, `best_measured` append |
| `LEAD-STR-curve-generation-provenance-seeds` | 2.10, 2.1b | evidence only |
| `LEAD-STR-safecurves-parameter-audit` | 2.1b | evidence only |
| `LEAD-EXO-ml-learned-models` | 2.12 | optional evidence (row is `unclear`) |

`ledger_refs`, `known_results`, `dominated_by`, `coverage.tsv` and every `disposition`: no change proposed.

## 4. Disposition changes: none

No record in these 16 paths decides a disposition. For each lead that has a closure, the stated `revisit_when` is not met by anything folded here: `LEAD-ICP-generic-table-decomposition` (needs a non-generic oracle; the ECCp-131 probes are generic small-x oracles with zero yield), `LEAD-ICB-generic-table-oracle` and `LEAD-ICB-multi-target-and-portfolio` (theorems; the new IC rounds are constant-factor), `LEAD-ICB-factor-base-subspace-choice` (n >= 31 test not yet run), `LEAD-STR-curve-generation-provenance-seeds` (no new weak class), `LEAD-ICE-boolean-f4-f5-f6-engines` (no priced engine beats the pair-table floor on a new cell). For the open leads, the two problem files that block `LEAD-RHO-prime-gpu-rho` and `LEAD-ICE-rootfind-pairtable-oracle` are still `open`. The only next-action text that is partly executed is `LEAD-ICP-prime-ic-constant-engineering` (validation of the Table B prime rows, 2.3), `LEAD-ICB-koblitz-rho-reference` (same-process stronger-rho comparison, 2.1a) and `LEAD-ICP-gfp5-oa-sdhp-jv` (toy trial-cost measurement and closed-form projection, 2.8); each keeps its disposition because the remaining part of its step is unexecuted. No hypothesis, experiment or goal status change is proposed anywhere.

## 5. Flags for the reviewer

1. Numbering and units: "rule v4" in `LEAD-ICB-koblitz-setup-phase-cost` (ran 2026-10-24, counted-unit recipe test) is not the baseline-v4 rule of the 2026-10-16 to 2026-10-19 series; the v6 to v8 figures are wall-time with both arms in one process (2.1a). `LEADERBOARD.md` Table A still reads baseline v3.
2. Rule v8: the control rho is not admissible at 4 of 6 sizes and the reason it differs from v7 is recorded as "not established"; the 1.30 to 1.58x matched/control ratio therefore compares against a control whose own speed moved between sessions.
3. `FRONTIER.md`: only ids and one interval changed; values in `best_measured` are unchanged. The KR rows `KR-RHO-1c2928` and `KR-RHO-cd0049` hold v1 ids (left alone, noted in 2.2b).
4. Table B validation: `research/ic_validation_gate_20261024/README.md` still says "staged" while `docs/ic/runs/VALIDATION.json` exists at HEAD and the board shows "validated"; the gate result does not narrow the distance to rho.
5. k5 Joux-Vitse: the title figure q* about 2^55 uses MODEL.md's paper constant c-tilde = 3e9; with the measured C'' = 1.104e10 the same formula gives about 2^59 (my arithmetic, not rerun).
6. prime61: the zero-relation result is a capped null with three inverse pairs; it is not an obstruction and must not be written as one.
7. Pending in a source record: the nist-extension-twist R06 continuation had no final status in the record; FactorDB-negative and timeout outcomes are inconclusive by the record's own wording.
8. `ca-ic prime --curve eccp-131` (cryptanalysis) still runs on a generated smaller curve, per the ECCp-131 record; that belongs to the cryptanalysis group's fold.
9. Not in this group's delta but referenced by these records and not read: `problems/p61-full-isogeny-class-census.md`, `problems/ecbench-gpu-matched-workload-contract.md`, `problems/prime-field-arity3-relation-oracle.md`, `problems/generalized-rootfinding-all-roots-8x.md`.

## 6. Raw `--match` output

Commands were run from `/Volumes/SSD990-2/crypto-autoresearcher` with `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` set as specified. Each block shows the phrasing and the top 5 lines (score, id, disposition or `known_result`, title, truncated). `[tag]` is the record: benchmarks = `benchmarks/README.md`; frontier = `FRONTIER.md`; leaderboard = `LEADERBOARD.md`; certicom, n13, eccp131, k5, n83, nistext, nistarch, p61, prime61, rhoworker, rootfind, sqisign = the problem files of the same name.

```text
### [benchmarks] --match "IC single-target cold time baseline pair table scan prefetch build compared with matched rho Koblitz"
   21  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisati
   17  LEAD-ICB-koblitz-setup-phase-cost            open_next_step     Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sit
   16  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
   16  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged pr
   16  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
### [benchmarks] --match "index calculus engineering round accepted baseline cold speedup versus Pollard rho distance"
   16  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   15  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
   13  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   13  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
### [benchmarks] --match "strong signed-Frobenius rho batched inversion clmul walk instructions per step"
   23  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; bea
   23  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   22  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisati
   16  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   15  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
### [benchmarks] --match "isogeny volcano level effect ECDLP cost census rho BSGS IC"
   27  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   14  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
   13  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
   12  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; bea
   12  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, invers
### [benchmarks] --match "N83 prebuilt retained signed-Frobenius factor base build replay"
   14  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a p
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion tr
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, bey
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa 
### [benchmarks] --match "sextic twist weak sibling class safecurves trapdoor census"
   17  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class
   13  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-inv
   12  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   11  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
   11  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q
### [benchmarks] --match "adaptive pair cells rootfinding all-roots exact binary fixed-sum"
    9  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa 
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    6  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    6  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
    5  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m sy
### [benchmarks] --match "factor base shape slope kappa prime field Koblitz analogue solver-stage"
   19  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative
   16  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, bey
   16  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extensio
   16  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bas
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
### [benchmarks] --match "bit-sliced group-law oracle point decomposition lanes"
   15  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   11  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
   11  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
### [benchmarks] --match "two-Sylow halving search Fp64 branch-free"
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    6  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    4  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    4  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
    4  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curve
### [benchmarks] --match "Semaev root finding native long-XOR affine cone count"
   10  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    9  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    8  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC 
    6  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Pet
    6  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
### [frontier] --match "measured bounds frontier ops memory rho bsgs kangaroo prime toy tier dominance"
   24  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sq
   17  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   14  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; bea
   11  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, invers
   11  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
### [frontier] --match "claw pair table Koblitz medium tier bound ic.pipeline exponent alpha fit"
   15  LEAD-ICB-koblitz-setup-phase-cost            open_next_step     Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sit
   13  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
   13  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table
   12  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged pr
   11  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)
### [leaderboard] --match "IC leaderboard S_IC over S_rho validated gate prime field rows"
   12  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   10  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   10  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sq
   10  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extensio
   10  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bas
### [leaderboard] --match "registry curves leaderboard regenerated validation gate Table B"
   10  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sq
    6  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    6  LEAD-ICB-free-relations-self-collision       exhausted_at_scale Free relations from self-collisions in the pair-root table (no-probe relations)
    6  LEAD-ICB-koblitz-setup-phase-cost            open_next_step     Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sit
    6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a p
### [certicom] --match "Certicom ECCp-131 ECC2-131 GPU rho worker distinguished points CUDA"
   21  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
   19  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
   15  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   12  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
   11  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
### [certicom] --match "binary challenge curves GPU Pollard rho persistent worker bitsliced walk steps per second"
   25  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   21  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
   21  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
   16  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; bea
   16  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
### [n13] --match "inherited F4 specialisation accounting eager lazy replay ecbench claim-n13"
    9  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    5  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    4  KR-IC-0d2021                                 known_result       Modern Gröbner-basis complexity refinements
    3  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    2  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m sy
### [n13] --match "ecbench inherited-F4 arms counted work method identity replay drift"
    4  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    3  LEAD-RHO-kangaroo-interval                   closed_dominated   Kangaroo / lambda (van Oorschot-Wiener, Gaudry-Schost) as a full-group ECDLP solver
    2  KR-RHO-18cc42                                known_result       ECC2K-130: expected work and 2009–2010 implementation rates
    2  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; bea
    2  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sq
### [eccp131] --match "ECCp-131 exact curve index calculus two-point three-point small-x relation rank zero"
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift cert
   15  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number
   14  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
### [eccp131] --match "prime field index calculus relation oracle support bound factor base abscissae 131-bit"
   27  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   24  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   19  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils
   17  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bas
   17  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift cert
### [k5] --match "Joux-Vitse decomposition E(F_p^5) trial cost Groebner rho parity crossover"
   15  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, invers
   14  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   14  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 +
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   11  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
### [k5] --match "extension field curve n-1 decomposition 2-torsion Edwards F4 trace replay"
   20  KR-IC-081a58                                 known_result       Joux–Vitse n−1 decomposition and oracle-assisted static DH
   19  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
   12  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
   11  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 +
### [n83] --match "N83 prebuilt factor base quality m=2 m=3 m=4 Koblitz relation rank"
   19  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, bey
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   14  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   13  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace ran
   13  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative
### [n83] --match "signed-Frobenius orbit factor base structured closure dimension 12 retained base comparison"
   16  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, bey
   14  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative
   13  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a p
   12  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion tr
### [nistext] --match "extension twist composite cofactor factorization NIST P-256 order degree-2 NFS ECM"
    9  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
    9  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    6  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion tr
    6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed
### [nistext] --match "NIST curve twist group order factorization skipped curves seed provenance"
   14  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
   14  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed
   12  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
### [nistarch] --match "NIST factorization raw archive NFS relations publication store"
    6  LEAD-ICB-free-relations-self-collision       exhausted_at_scale Free relations from self-collisions in the pair-root table (no-probe relations)
    6  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    6  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
    5  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    4  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
### [nistarch] --match "large evidence archive publication curve order factorization"
    8  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    8  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    5  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    5  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    5  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
### [p61] --match "p61 isogeny class census registered root terminal closure vertices"
   12  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
   12  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
   11  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   11  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
### [p61] --match "isogeny class graph 2^61-1 horizontal class adjacency uniqueness census"
   12  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
   12  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
   11  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   11  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
### [prime61] --match "prime61 exhaustive horizontal isogeny class walk relations solves"
   17  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   15  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
   14  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
   14  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent
   13  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
### [prime61] --match "isogeny walk class group action prime-degree kernel edges weak neighbour 61-bit"
   23  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
   22  LEAD-STR-isogeny-walk-weak-neighbour         closed_known       Walk or construct isogenies from a deployed curve to find a weak neighbour
   22  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   19  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   17  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent
### [rhoworker] --match "secp256k1 rho worker batch serial walk speedup physical host A/A"
   14  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor
   14  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
   13  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
   13  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   13  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
### [rhoworker] --match "batched inversion walk worker default routing fresh targets paired interval"
   10  LEAD-RHO-batched-inversion-shared-pm         closed_known       Batched affine steps: Montgomery simultaneous inversion and the free x(P-Q) beside x(P+Q)
   10  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
    9  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
    9  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    7  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisati
### [rootfind] --match "root-finding pipeline complete cost calibration pair table lanes native pricing"
   17  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table
   11  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
   10  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisati
   10  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    9  LEAD-ICB-koblitz-setup-phase-cost            open_next_step     Cutting the reusable set-up of the one-target Koblitz pipeline (Table A), where 98.5-99.7% of S sit
### [rootfind] --match "generalized all-roots conditional pair cell union residual F4 F5 F6 GF(2^83)"
    6  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeratio
    5  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-
    4  KR-IC-0d2021                                 known_result       Modern Gröbner-basis complexity refinements
### [sqisign] --match "SQISign statistical root gate test failure acceptance rate"
    8  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
    6  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a p
    4  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    3  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
### [sqisign] --match "isogeny signature scheme validation suite assertion"
    6  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Te
    6  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    6  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport t
    6  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
    6  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
### [prime61] --match "map target to isogenous curves relation stage factor base inverse pairs transported instance horizontal edges"
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   13  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, bey
   13  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposabili
   13  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
### [prime61] --match "choose isogenous curve class member cheapest index calculus relation yield per vertex"
   20  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift cert
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
### [p61] --match "learning corpus hardness predictor isogeny class vertices training table"
   18  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
   16  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
   12  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
   11  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the 
   11  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent
### [eccp131] --match "relation oracle escaping small-x support limit conservation yield binomial coverage factor base size"
   22  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   20  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposabili
   18  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   17  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   16  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace ran
```

---

## Group: cryptanalysis-ecc

# Fold: group cryptanalysis-ecc (proposed atlas diffs, no repository edited)

Reviewer step: lead-atlas skill, "changed since review", step 2. Date 2026-10-24.
Scope: 32 cryptanalysis paths + 3 ecc-challenges paths from `scratchpad/atlas/delta.txt` = **35 paths**.
Nothing was edited, staged or committed in any repository. All writes are under `scratchpad/audit/`.

## 0. Conventions and provenance

- **NO-OP** (in `proposed_row_edit`): the path changes nothing the atlas records. It is listed under the lead that already covers its parent directory so the parent can filter it out.
- **outside delta**: a file I read that is not in the changed list, only to price a claim a changed path makes. Marked each time.
- Observation = something I read or computed from a file, with its path. Interpretation = conditional, marked "reading:".
- Repos and pins: cryptanalysis checkout `scratchpad/cryptanalysis-main`, HEAD `c5aa7b39b` (pin `9760a763`). ecc-challenges `/Volumes/SSD990-2/ecc-challenges`, branch `main`, HEAD `df8cd52` (pin `3a71596`, which is an ancestor of HEAD; `git diff 3a71596 HEAD -- docs/` touches exactly the 3 listed docs).
- IDEA `prior_art.lead` check: **N/A**, this group has no IDEA-* paths. No path in this group is a ledger record, so **no `coverage.tsv` row is needed**.
- `python3 tools/lead_atlas.py --check --strict-paths` (with the three LEAD_ATLAS_* env vars) printed 2 errors in 147 leads, both in `LEAD-RHO-pool-class-quotient` (evidence[4], evidence[5]); see D3.
- Moved-file check: `git diff --name-status 9760a763 HEAD` in cryptanalysis lists 1,372 deleted paths (`audit/cryptanalysis_deleted_paths.txt`). A Python scan of all 147 lead files found **0** of them referenced. All 22 `repo: cryptanalysis` evidence entries either resolve in the checkout or carry a `ref: c273e621` branch pin (4 entries; those 4 do not resolve on main, as the pin states).
- Path convention: every path below and in the structured return is prefixed `cryptanalysis:` or `ecc-challenges:` because `problems/README.md` and others exist in several repos.
- Disposition changes proposed: **none**. New mechanisms: **none**.

## 1. Table (one row per path)

All 15 `.artifacts.json` manifests (R11, R12, R20-R32) come from one commit, `5569ba6e3` 2026-10-24 "Move tracked data blobs to S3 so CI checkouts stop filling the disk": in `git diff --name-status` each is `A` (manifest + `.gitignore`) next to `D` of the raw file (report.pdf, png, checkpoints, logs). `docs/artifacts.md` (R10) says the store "moves bytes and checks them; it makes no claim about what the bytes mean".

| # | Path (repo: cryptanalysis unless noted) | ECDLP | Action | Lead | Reasoning |
|---|---|---|---|---|---|
| R01 | cryptanalysis:docs/CRAX.md | no | not_ecdlp | none | Modified (about +215/-17, commit 915fe6aba "Document bounded ECDLP and cubic graph CLI checks"). Observation: CLI bridge documentation. It lists `crax ecdlp-nist`, `crax ic` or `crax icx` with `solve-prime`, `solve-prime-file`, `solve-cubic`, `prime-route-generate`, `cubic-graph`, `cubic-route-generate`, `crax store` (S3 push/verify/pull), and AES/hash/MAC commands. It gives explicit-target input limits (p in 5..1,000,000; n in 3..4,000,000; cubic characteristic 7..101) and states these are "operational input limits, not estimates of cryptographic-curve solve cost". Examples return verified scalars 190 (p=271) and 5 (F11 cubic fixture). No mechanism, cost model or ECDLP-size measurement is introduced. Reading: plumbing for existing sibling tools; no lead's mechanism, obstruction or next_action is affected. `--match` x2 (appendix A.crax): best hit score 14, `LEAD-TRF-odd-char-descent-smith-quartic`, lexical overlap only ("prime", "route", "isogeny"), mechanism unrelated. |
| R02 | cryptanalysis:docs/CRAX_AES_BRIDGE_ACCEPTANCE_20261024.json | no | not_ecdlp | none | Added. AES CLI parity receipt (help list, S-box row parity, binary SHA-256s). AES, not ECDLP. |
| R03 | cryptanalysis:docs/CRAX_AES_HOLDOUT.md | no | not_ecdlp | none | Added. AES differential/linear held-out corpus procedure. Not ECDLP. |
| R04 | cryptanalysis:docs/CRAX_AES_HOLDOUT_S3_ACCEPTANCE_20261023.json | no | not_ecdlp | none | Added. AES holdout S3 acceptance receipt. Not ECDLP. |
| R05 | cryptanalysis:docs/CRAX_AES_OBSERVED_BRIDGE_ACCEPTANCE_20261024.json | no | not_ecdlp | none | Added. AES observed-statistics CLI parity (`direct_equals_crax: true`). Not ECDLP. |
| R06 | cryptanalysis:docs/CRAX_HASH_AUTO_REPLAY_ACCEPTANCE_20261024.json | no | not_ecdlp | none | Added. Hash-auto witness replay (30 algorithms, 30 pairs replayed, 9 full-digest-equal per its `counts`). Not ECDLP. |
| R07 | cryptanalysis:docs/CRAX_HASH_BRIDGE_S3_ACCEPTANCE_20261023.json | no | not_ecdlp | none | Added. Hash bridge S3 acceptance. Not ECDLP. |
| R08 | cryptanalysis:docs/CRAX_HASH_STREAM_S3_ACCEPTANCE_20261023.json | no | not_ecdlp | none | Added. Streamed-hash S3 acceptance. Not ECDLP. |
| R09 | cryptanalysis:docs/CRAX_PRIME_ROUTE_S3_ACCEPTANCE_20261024.json | no (ECDLP-adjacent infra) | not_ecdlp | none | Added (b0a3f802a). Observation: schema `crax.prime-route-s3-acceptance/v1`; `crax store` pushes input.json (95 B) and routes.json (4,103 B), remote byte check, fresh-cache pull; then `crax --json ic solve-prime-file` returns scalar "190", `verified: true`, `edges_verified: 2`, route id IW1E11h1h1a619f4ab250; `objects_after: 0` after cleanup. Scalar 190 equals the CRAX.md p=271 example (the receipt does not print p). Reading: storage round-trip of a public target and a certified 2-edge isogeny route; no relation-yield, cost or scaling datum. It does **not** touch the blocker of `LEAD-ICP-isogeny-transported-relation-yield` (`blocked_by: problems/prime-field-arity3-relation-oracle.md`, 17 of 20 EXP-ECTD-0cf008 arms missing): that blocker is arity-3 relation yield at ell=8209/131101, a different object. `--match` x2 (A.crax): top hits lexical only. |
| R10 | cryptanalysis:docs/artifacts.md | no | not_ecdlp | none | Added (b1cba0342). Artifact-store policy (1,372 files, 4,032.9 MB of 4,682.5 MB tracked would move). Explains R11, R12, R20-R32. |
| R11 | cryptanalysis:docs/ecdlp-surfaces/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration. Manifest for report.pdf (182,485 B) and transfer.png (152,208 B) of docs/ecdlp-surfaces. Lead's evidence cites `ecdlp_surfaces_n83` REPORT.md and crypto PROTOCOL.md, not these binaries. `--match` (A.surfaces): rank 1-2 = this lead (scores 9, 12). |
| R12 | cryptanalysis:docs/papers/ecc2k130-blackwell/.artifacts.json | yes | advances_lead | LEAD-RHO-ecc2k130-gpu-fpga-throughput | NO-OP: pointer migration of paper.pdf. `--match` (A.ecc2k130): rank 1 = this lead (scores 31, 23). Flag F3 (outside delta): the atlas never cites docs/papers/ecc2k130-blackwell/. |
| R13 | cryptanalysis:docs/sixclass-20261024/assessment.md | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added (86702f8db, A/B/A drift control). See D1/D2 and section 3. Observation: six-class walk on registered `glv-j0-26`: orbit of 6 = {1, lambda, lambda^2, -1, -lambda, -lambda^2} images; canonical rep = min rotated x then min(y, p-y); jumps twisted by u(t)^-1 so the class-keyed jump is equivariant; native C opt-in solver. Original paired run: default oriented GLV rho 0.016382582 s vs six-class 0.020590401 s (1.257x), 20/20 planted logs solved. A/B/A run: default arms 0.012935407 s and 0.012907277 s, six-class 0.023595841 s (1.826x of the mean default), identical A/A group-op counts. Assessment itself says the two algorithms use different unit counters, solves are ms-scale, "No confidence interval or production speed claim", and the cited 126.96-bit / >=0.3909 success figure is conditional on the source submission's H1 mixing and cost model (kappa 1.05 -> 1.02, inversion batch 2^16). Reading: this is the known automorphism-orbit walk (KR-RHO-0528e7: sqrt(6) for j=0), not a new mechanism; no step-count shortfall against the sqrt(6) ceiling is measured, so neither lead's `revisit_when` is triggered. `--match` x4 (A.sixclass): LEAD-RHO-automorphism-class-walks (score 13-18) and LEAD-STR-automorphism-quotient-rho (score 47 on the "orbit-choice mixing / fruitless cycles / GLV-split" phrasing; its `forecloses` lists exactly those). |
| R14 | cryptanalysis:docs/sixclass-20261024/paired-glv-j0-26-aba.json | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added. Raw rows (schema ca.sixclass.paired.v2, 20 targets, seeds 19..38). Computed by me from the rows: totals default-before 0.012935407 s, default-after 0.012907277 s, six-class 0.023595841 s; six-class time is below the mean of the two default arms on 1 of 20 targets (index 1, seed 20, ratio 0.82); per-target ratio range 0.82-5.84, median 1.78; per-target A/A drift up to 24.3%; sums: 78,476 default group ops, 46,882 class visits, 2,922 DPs, 196 escapes. Reading: at ms scale the A/A pair brackets only within-run drift; see F1 for a between-receipt discrepancy. Evidence entry in D1. |
| R15 | cryptanalysis:docs/sixclass-20261024/paired-glv-j0-26.json | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added (4c3be2941). Original raw totals, schema v1: default 0.016382582 s, six-class 0.020590401 s, `default_group_ops` 110,581, class visits 46,882, DPs 2,922, escapes 196. Same six-class counters as R14 but a different `default_group_ops` (110,581 vs 78,476): F1. Cited by D1 as the original receipt, not as a measurement of equal rank to R14. |
| R16 | cryptanalysis:docs/sixclass-20261024/routing-telemetry-2trials.json | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added (c9f9cba20). Seeds 19 and 20: per-twist visit counts (134,127,134,132,149,144 and 277,301,279,269,301,312) and 12 twist/route-parity cells, each row summing exactly to class visits (820 and 1,739). Seed 19 candidate slower, seed 20 faster. Exploratory, no CI. |
| R17 | cryptanalysis:docs/sixclass-20261024/routing-telemetry-2trials.md | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added. Protocol and caveats: "retrospective exploratory evidence, not a held-out H1 test"; counts are correlated walk visits and "cannot establish class uniformity, route independence, collision CDF, full-work cost". Binary SHA-256 and parent revision 1f6aa21795ba pinned. |
| R18 | cryptanalysis:problems/README.md | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Modified: +1 index row (sixclass-secp-throughput-unmeasured, status Open). Index pointer only; the problem record is R19. |
| R19 | cryptanalysis:problems/sixclass-secp-throughput-unmeasured.md | yes | advances_lead | LEAD-STR-automorphism-quotient-rho | Added (c9f9cba20), status `open`. Names the gap: 64-bit toy C solver and BigUint Rust worker only; no fixed-limb production worker, no matched secp256k1 measurement. Records "Suspected explanation" (extra canonicalization, DP management and short-cycle work may outweigh a quotient gain on this curve) as suspected, not shown, and "What this evidence does not establish": the toy loss does not refute a secp256k1 gain; the source estimate does not establish one here. Next discriminating step: fixed-limb worker vs default on the registered 26- to 44-bit GLV ladder with A/A controls. D1 (obstruction unchanged) and D2 (this is a native-step-cost question). |
| R20 | cryptanalysis:research/binary_genus2_cover_20261014/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of report.pdf. REPORT.md evidence path (cited by the lead) still resolves. `--match` (A.genus2_cover): ranks 1-2 are TRF-cover-catalog (22) and this lead (13/14). See F4 (outside delta). |
| R21 | cryptanalysis:research/binary_genus2_cover_20261014/figures/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of counts.png. |
| R22 | cryptanalysis:research/binary_genus2_cover_20261014/runs/run-20261014T1442Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of root-library-tests.log (351,237 B). |
| R23 | cryptanalysis:research/binary_genus2_speed_20261014/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of report.pdf. `--match` (A.genus2_speed): top hits ICB-decomposition-encoding-and-sat (9), TRF-cover-catalog (9), then ICB-koblitz-rho-reference (23) on the rho-cost phrasing; lexical. REPORT.md (cited by lead) unchanged. |
| R24 | cryptanalysis:research/binary_genus2_speed_20261014/reports/run-20261014T1901Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of one report.pdf. |
| R25 | cryptanalysis:research/binary_genus2_speed_20261014/reports/run-20261014T2034Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of one report.pdf. |
| R26 | cryptanalysis:research/binary_genus2_speed_20261014/reports/run-20261014T2148Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of one report.pdf. |
| R27 | cryptanalysis:research/binary_genus2_speed_20261014/reports/run-20261014T2250Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of one report.pdf (257,053 B, sha256 baefd37e...). |
| R28 | cryptanalysis:research/binary_genus2_speed_20261014/runs/run-20261014T1901Z/campaign/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of 13 files (checkpoint JSONs, progress.jsonl, worker.log). |
| R29 | cryptanalysis:research/binary_genus2_speed_20261014/runs/run-20261014T2034Z/campaign/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of 23 files (checkpoint JSONs, progress.jsonl, worker.log). |
| R30 | cryptanalysis:research/binary_genus2_speed_20261014/runs/run-20261014T2148Z/campaign/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of 26 files (checkpoint JSONs, progress.jsonl, worker.log). |
| R31 | cryptanalysis:research/binary_genus2_speed_20261014/runs/run-20261014T2250Z/campaign/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP, with one optional pointer (D5). Moves 28 files: a0-0 elliptic and image_inverse checkpoints, a1-0..a1-7 elliptic/image_inverse/jacobian checkpoints, progress.jsonl and worker.log. Only a0-0 exists for a=0, consistent with REPORT.md ("no a=0 recovery", censored counters). |
| R32 | cryptanalysis:research/ecdlp_surfaces_n83_20261012/reports/run-20261012T0331Z/.artifacts.json | yes | advances_lead | LEAD-TRF-same-field-genus-g-embedding | NO-OP: pointer migration of destinations.png and report.pdf. Lead's evidence cites this run's REPORT.md, which still resolves. `--match` (A.surfaces) rank 1 = this lead (score 9). |
| R33 | ecc-challenges:docs/admission-and-capacity.md | no | not_ecdlp | none | Modified (752b49c "Allow unlimited active API keys with account upload quota"). Observation: account limit changes from "three active keys" to any number of keys with a combined 15 GiB/day upload limit, key creation at most once per minute; per-key 5 GiB/day, 8 active runs, 64 lifetime run IDs unchanged. Reading: contributor admission policy for the distributed-rho platform; no walk, cost or result. `--match` x2 (A.admission): no relevant lead (top lexical hit score 9, LEAD-RHO-prime-gpu-rho). |
| R34 | ecc-challenges:docs/multicurve-storage.md | yes | advances_lead | LEAD-RHO-pool-class-quotient | Modified (commits 469b4b5 2026-10-20, 556ebf7 2026-10-22; in the pin..HEAD diff). Observation: new "Walk versions" section: walk 2 = SHA-256 partition on points, defined for every curve; walks 3 and 4 for ECC2-131 and ECCp-131; walk 4 (`...-negmap-v4`) walks classes {P,-P}, stores the canonical point, negates a and b with the point, "ideal birthday model predicts sqrt(pi*n/4) steps; cycle handling adds work whose cost must be measured"; 2-cycles and anchor cycles leave through a 33rd (escape) jump. "ECC2-131 and ECCp-131 register new runs under walk 4 by default (`DEFAULT_WALKS`)". Confirmed in code: `src/ecc_challenges/multicurve/codec.py:40-41` `FAST_WALK_CAMPAIGNS = ("ecc2-131","eccp-131")`, `DEFAULT_WALKS = {campaign: WALK_V4 ...}` (outside delta). Reading: the lead's mechanism ("plain rho on all 23 non-ECC2K-130 campaigns") and evidence[0] note ("v2 walk has no automorphism quotient") are now partly stale for those 2 campaigns. Whether walk 4 runs in the live pool is not established here: `verification/rho131-nine-curve-20261023/README.md` (outside delta) says the live catalog snapshot still pins worker digest sha256:a347a784... and no new image has been advertised. D3. |
| R35 | ecc-challenges:docs/running-a-worker.md | yes | advances_lead | LEAD-RHO-pool-class-quotient | Modified (one table row changed, one added). Observation: `ECC_LANES` default for ECC2-131/ECCp-131 (walk 4) GPU 4096, CPU 32 x threads (others: GPU 64, CPU 4 x threads); new `ECC_STEPS_PER_ROUND` default 256, and 4096 for the walk-4 curves. Reading: deployment parameters corroborating R34; minor evidence entry only (D3). |

## 2. Proposed diffs (atlas rows; nothing applied)

### D1. `knowledge/leads/ecdlp/structure/LEAD-STR-automorphism-quotient-rho.yaml` (disposition stays `closed_known`)

```yaml
evidence:
+ - {repo: cryptanalysis, path: docs/sixclass-20261024/assessment.md,
+    note: "six-class (j=0 order-6 orbit, unit-twisted jumps) GLV rho, native C toy on glv-j0-26: 20/20 planted logs recovered; wall time 1.826x of default GLV rho in the A/B/A receipt (with A/A control) and 1.257x in the earlier v1 receipt (default-arm counter disagrees between receipts, see F1), ms-scale, different unit counters, no CI; cited 126.96-bit figure conditional on source H1 mixing/cost model, not tested"}
+ - {repo: cryptanalysis, path: docs/sixclass-20261024/paired-glv-j0-26-aba.json,
+    note: "raw A/B/A rows; six-class below the mean default time on 1 of 20 targets; per-target ratio 0.82-5.84, median 1.78"}
+ - {repo: cryptanalysis, path: docs/sixclass-20261024/routing-telemetry-2trials.md,
+    note: "two-target twist/route-parity counters reconcile to class visits; exploratory, not an H1 test"}
+ - {repo: cryptanalysis, path: problems/sixclass-secp-throughput-unmeasured.md,
+    note: "open: fixed-limb worker + trail replay + matched 26-44 bit ladder needed before any secp256k1 statement"}
related:
+ - LEAD-RHO-automorphism-class-walks
+ - LEAD-RHO-native-step-cost
forecloses:
+ - six-class GLV rho (Curve Smash)
+ - unit-twisted equivariant jump class walk on j=0
+ - canonical orbit representative min rotated x then min(y, p-y)
```

Unchanged on purpose:
- `best_measured`: the six-class numbers are wall time on a 26-bit toy with different counters, not a step-count ratio to the sqrt(6) ceiling.
- `ledger_refs`: no six-class ledger record exists. The only ledger hits for "six-class" are `H-ECDLP-2a4935` / `EXP-ECDLP-25be5c` ("six-class certificate-verdict table"), an unrelated use of the name; do **not** add them.
- `revisit_when` ("per-step cost kappa below 1 group operation ... for a group larger than Aut"): not triggered. The group is Aut(6); the assessment's kappa (1.05 -> 1.02) is an accounting constant of the external cost model whose definition is not in these paths, so whether it is the lead's kappa is not established.

`LEAD-RHO-automorphism-class-walks.yaml`: add `related: [LEAD-STR-automorphism-quotient-rho]` and `forecloses: + six-class GLV rho orbit walk`. No evidence duplication.

### D2. `knowledge/leads/ecdlp/generic/LEAD-RHO-native-step-cost.yaml` (stays `open_next_step`)

```yaml
evidence:
+ - {repo: cryptanalysis, path: docs/sixclass-20261024/assessment.md,
+    note: "prime j=0 six-class step (canonicalisation + DP management + short-cycle escape) priced only as toy wall time (1.257x / 1.826x of default GLV rho at 26 bits); 'Next checks' asks for a matched field-operation and memory meter"}
related:
+ - LEAD-STR-automorphism-quotient-rho
next_action.step:  append "; the prime j=0 analogue is the fixed-limb six-class worker vs default GLV rho on the registered 26- to 44-bit ladder with A/A controls (cryptanalysis problems/sixclass-secp-throughput-unmeasured.md, 'Next discriminating step')"
```

Reading: the six-class open obligation (priced cost of canonicalisation and escapes per step) is the same measurement type as this lead's Koblitz canonicaliser step; this is the closest `open_next_step` lead in the atlas (the other candidates, D1's two leads, are `closed_known`). No `discriminates` change proposed.

### D3. `knowledge/leads/ecdlp/generic/LEAD-RHO-pool-class-quotient.yaml` (stays `open_next_step`)

```yaml
mechanism:   replace "on all 23 non-ECC2K-130 campaigns" with
             "on the campaigns other than ECC2-131 and ECCp-131 (which register walk-4 negation-class runs by default on ecc-challenges main)"
evidence[0]: note -> "Walk versions section: walk 2 (plain points) for every curve; walks 3/4 only for ECC2-131/ECCp-131, walk 4 = {P,-P} classes, default for those two (codec.py FAST_WALK_CAMPAIGNS/DEFAULT_WALKS); cycle-handling cost 'must be measured'"
evidence[4], evidence[5]: add  ref: 1f49962  # branch claude/ecdlp-leads-analysis-l7f87y (origin); not on main
             (precedent: LEAD-RHO-native-step-cost uses `ref:`)
evidence:
+ - {repo: ecc-challenges, path: src/ecc_challenges/multicurve/codec.py, note: "DEFAULT_WALKS: ecc2-131, eccp-131 -> WALK_V4"}
+ - {repo: ecc-challenges, path: benchmarks/rho131/results/toy-negation-gain.json,
+    note: "walk 4 vs walk 3 through the production fast engine, toy group order 16,782,391, 300 trials/walk: 3820 +/- 116 vs 4798 +/- 142 steps, ratio 1.256 (ideal 1.414); README: does not establish the gain on the 131-bit curves"}
+ - {repo: ecc-challenges, path: docs/running-a-worker.md, note: "walk-4 worker defaults: lanes 4096 (GPU) / 32 x threads (CPU), 4096 steps per round vs 64 / 4 x threads / 256 elsewhere"}
best_measured: append "; walk 4 (fast engine on main, a different implementation from B3): 3820/4798 = 0.796 of walk 3's steps, 1 toy curve (order 16,782,391), 300 trials, README ratio 1.26 +/- ~0.05"
next_action.step -> "ECC2-131/ECCp-131: walk 4 is the code default on main; still to measure: the trap / cycle-escape rate and steps-per-solve at production DP density on the 131-bit curves (README: not measured), CUDA and Metal paths (a hosted macOS x86_64 Apple-Paravirtual job reported an off-curve ECCp-131 walk-4 state; PR #57 repair pending per the rho131-nine-curve README), and whether the live catalog pins a walk-4 image. Other campaigns: PR #56 generic-engine variant (1f49962, not on main) as before; Frobenius class walk for ECC2K-163/238/358 remains design only."
```

`--check --strict-paths` confirms evidence[4] (`verification/negation-walk-20261024/README.md`) and evidence[5] (`docs/negation-walk.md`) do not exist on main; `git ls-tree 1f49962` shows both exist in that commit, which `git merge-base --is-ancestor 1f49962 HEAD` says is not an ancestor of main (`git branch -a --contains` -> `remotes/origin/claude/ecdlp-leads-analysis-l7f87y`). Disposition stays open because the production-density trap rate and live deployment are not shown by any file read.

The benchmark JSON and `codec.py` are outside the delta; they were read to price the doc's "must be measured" sentence.

### D4. Optional, outside delta: `LEAD-TRF-cover-catalog-jacobian-transfer.yaml` (stays `open_blocked`)

```yaml
evidence:
+ - {repo: cryptanalysis, path: research/binary_genus2_cover_20261014/REPORT.md,
+    note: "family-specific executable degree-3 pullback C_a -> E_a over GF(2^83) with explicit inverse; REPORT states it does not implement a norm on arbitrary Jacobian classes, so the blocker problems/binary-cover-arbitrary-jacobian-norm-missing.md is unchanged"}
```

Reading, conditional: REPORT.md line 227 says the crypto cover-catalog explanation "is updated to link this additional family"; whether the n=83 curves are among the lead's 160 binary cubic pullbacks is not established by these paths.

### D5. Optional pointer: `LEAD-TRF-same-field-genus-g-embedding.yaml`

```yaml
evidence:
+ - {repo: cryptanalysis, path: research/binary_genus2_speed_20261014/runs/run-20261014T2250Z/campaign/.artifacts.json,
+    note: "raw a0/a1 checkpoints and progress log are now in the artifact store (sha256 manifest); run `python3 tools/artifacts/artifacts.py pull` before reading (docs/artifacts.md)"}
```

No other change. The obstruction (Tate multiplicativity, DEC-20260902-4c82fd) and `best_measured` are untouched; REPORT.md (unchanged by the delta) still gives Q_7: 1,160.138869297 s native J(C) vs 9.268307496 s elliptic at 10,442,347 steps, a=0 outstanding.

## 3. Flags found while reading (outside the changed paths unless stated)

- **F1 (in delta, R14 vs R15).** Same 20 targets (seed 19+i), same six-class counters (46,882 visits, 2,922 DPs, 196 escapes), but `default_group_ops` is 110,581 in the v1 receipt and 78,476 in the v2 A/B/A receipt, and default time totals differ (0.016382582 s vs about 0.01292 s, ratio 1.268). The assessment does not explain either difference. Reading, conditional: the default solver or its counter may have changed between receipts; until explained, any ratio of six-class visits to default group ops depends on which receipt is used (I computed none). Between the two receipts the six-class total rose 14.6% (0.020590 s to 0.023596 s) while the default total fell 21.1% (0.016383 s to 0.012921 s mean of the two arms).
- **F2.** `LEAD-RHO-pool-class-quotient` evidence[4]/[5] point at an unmerged branch (D3).
- **F3.** The atlas has no mention of `docs/papers/ecc2k130-blackwell/` (grep of the lead files for "blackwell": 0). Its README (rev 2, 2026-10-01; unchanged by the delta, only paper.pdf moved) reports a Frobenius-walk 17.625650 B iterations/s (+2.7734% paired, DP32) and a table-walk 22.100934 B updates/s that the README calls an arithmetic ceiling because the cycle rule admits Frobenius-relation cycles. `LEAD-RHO-ecc2k130-gpu-fpga-throughput` has `best_measured` 15.884 B updates/s (sigma-table). Whether these share a device and workload is not established. Reviewer to reconcile or cite the manuscript.
- **F4.** n=83 genus-2 cover vs the cover-catalog lead (D4).
- **F5.** Six-class evidence in other repos that no delta group lists, so the atlas would still have no pointer to it: crypto `docs/cryptanalysis/six-class-rho.md` and `src/bin/six_class_*.rs`; crypto-autoresearcher `harness/evidence/sixclass-*`, `harness/fixtures/sixclass_h1_matrix.json` (five H1 clauses, all distributional ones open per R13) and `docs/curvesmash-verification.md`. Also `grep` of the three ledger index files for "sixclass" returns no six-class rho record, so there is nothing for `ledger_refs`/`coverage.tsv`.
- **F7 (tooling note).** One `git log -S` run in ecc-challenges printed `unable to open loose object e1e43f18...: Interrupted system call`. R34 commit ids were re-confirmed with `git log --oneline 3a71596..HEAD -- docs/multicurve-storage.md docs/running-a-worker.md docs/admission-and-capacity.md` (469b4b5, 556ebf7, bddbc1b, 752b49c in range); no content here depends on the corrupt object.
- **F6.** The rho131-nine-curve README (ecc-challenges, outside delta) records a hosted macOS x86_64 Apple-Paravirtual Metal failure (off-curve ECCp-131 walk-4 state, jobs 120789662742 and 120796467229) with the repair on PR #57 pending; relevant to D3's "test the CUDA/Metal path" step.

## 4. Return summary

- n_paths 35; ECDLP-content rows that advance a lead with an edit: R13-R19 (D1/D2), R34-R35 (D3). NO-OP pointer rows: R11, R12, R20-R32 (15). not_ecdlp: R01-R10, R33 (11).
- decides_lead: none (no DEC record in this group; the one problem record R19 is status `open`). new_mechanism: none.

## Appendix A. Raw `--match` output (top 5 per query; env: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES set to the scratchpad checkouts)

### A.sixclass
```
#### [sixclass] --match "six-class GLV rho orbit walk equivariant twisted jump canonical class j=0"
   14  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   13  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
   13  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   13  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels

#### [sixclass] --match "automorphism class walk short cycle escape distinguished points secp256k1 throughput fixed-limb"
   17  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
   15  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
   12  LEAD-STR-isogeny-walk-weak-neighbour         closed_known       Walk or construct isogenies from a deployed curve to find a weak neighbour
   11  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor
   11  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

#### [sixclass_extra] --match "orbit-choice mixing fruitless cycles at |Aut| greater than 2 GLV-split rho walk on j=0 curves"
   47  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
   20  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
   14  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   13  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   12  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves

#### [sixclass_extra] --match "canonicalisation per-step cost wall time slower than default GLV rho toy glv-j0-26"
   15  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   13  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   13  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   13  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   12  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)

#### [sixclass] --match "six-class GLV rho automorphism orbit canonical class walk" (default limit 8, first run)
   18  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   15  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor
   15  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
   14  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
   13  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
   13  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   12  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels

```

### A.genus2_cover
```
#### [genus2_cover] --match "binary genus-2 cover degree-3 E over GF(2^83) pullback Jacobian transfer"
   22  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
   13  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   12  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
    7  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)

#### [genus2_cover] --match "same-field genus-g embedding Jacobian index calculus cost Koblitz n=83"
   15  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
   14  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

```

### A.genus2_speed
```
#### [genus2_speed] --match "binary genus-two Jacobian full-subgroup solve elliptic versus image inverse a=0 a=1 census"
    9  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    9  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
    7  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    7  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    7  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite

#### [genus2_speed] --match "Jacobian rho step cost versus elliptic rho matched equal steps GF(2^83) Koblitz"
   23  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   17  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   16  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   15  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
   14  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0

```

### A.surfaces
```
#### [surfaces_n83] --match "quartic model product surface representation n=83 Koblitz pair correctness"
    9  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    8  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    8  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    6  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation

#### [surfaces_n83] --match "quadric pencil surface transfer destinations ECDLP surfaces"
   12  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    6  KR-IC-64659b                                 known_result       Diem: rigorous subexponential ECDLP for suitable n
    6  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    6  KR-RHO-2480c6                                known_result       Binary-curve ECDLP records (FPGA)
    6  KR-RHO-33f837                                known_result       Prime-field ECDLP records

```

### A.ecc2k130
```
#### [ecc2k130_blackwell] --match "ECC2K-130 Blackwell GPU bitsliced rho throughput iterations per second"
   31  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
   17  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   13  KR-RHO-18cc42                                known_result       ECC2K-130: expected work and 2009–2010 implementation rates
   13  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
   10  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk

#### [ecc2k130_blackwell] --match "ECC2K-130 CUDA kernel Frobenius sigma walk updates per second per watt"
   23  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
   21  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps
   12  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
   10  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   10  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk

```

### A.crax
```
#### [crax_prime_route] --match "explicit target prime-field index calculus isogeny route certified route store bridge"
   14  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   14  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC

#### [crax_prime_route] --match "crax CLI bridge solve-prime route generate content-addressed store acceptance receipt"
    4  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    3  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    3  KR-RHO-7d93f6                                known_result       Time–space bounds for many collisions and DP memory
    3  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm
    3  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself

```

### A.multicurve
```
#### [multicurve_storage] --match "negation map walk canonical class distinguished point namespace ECC2-131 ECCp-131 sqrt(pi n/4)"
   23  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
   19  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)
   16  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
   15  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   13  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation

#### [multicurve_storage] --match "distributed rho campaign walk version cycle escape fruitless 2-cycle DP verification trail start"
   18  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
   16  KR-RHO-fb88e6                                known_result       Negation map: sqrt(2) gain and fruitless cycles
   13  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
   12  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   11  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes

```

### A.worker
```
#### [running_a_worker] --match "worker lanes steps per round GPU rho 131-bit walk checkpoint batch"
   19  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   16  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
   15  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   15  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
   13  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

#### [running_a_worker] --match "distributed rho contributor worker CPU GPU Metal CUDA throughput"
   20  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
   16  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
   13  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)
   10  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points

```

### A.admission
```
#### [admission] --match "API key upload quota admission control distributed rho campaign contributors"
    9  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
    7  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    6  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation

#### [admission] --match "rate limit backlog distinguished point batch upload checkpoint"
   12  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
   10  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    7  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves

```

