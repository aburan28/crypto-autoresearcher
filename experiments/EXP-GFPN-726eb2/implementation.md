# EXP-GFPN-726eb2 — implementation note

Executor note for TASK-20260920-d78326 (H-GFPN-ee4d45, GOAL-GFPN-380702,
approved by DEC-20260920-fe73de). The frozen contract
`experiments/EXP-GFPN-726eb2/specification.yaml` was not edited. This note
records what was implemented, every deviation from the approved protocol, every
failed or unfinished attempt, and observations only — no support/reject
judgement on the hypothesis.

Implementation commit: `c40a181afe7198c8dafab5cde4c2fcd2912c05e8` (branch
`claude/pollard-rho-speedup-hypotheses-yu8qwp`, tree clean apart from this
experiment's own artifacts, which are listed in each run's
`environment.json → git.dirty_paths`).

## 1. What the pipeline does

Scripts under `experiments/EXP-GFPN-726eb2/implementation/`:

| file | role |
| --- | --- |
| `run_wrapper.py` | Creates an immutable run directory (refuses to overwrite), records `command.txt`, `environment.json` (tool versions, git commit, dirty paths), captures `stdout.log`/`stderr.log`, wall time and peak RSS, writes `manifest.yaml` with `result.certificate.kind: none`. |
| `scurve_control.py` | Instrument control (contract control `scurve_control_curve`): regenerates the prior SCURVE certificate package value-for-value with independent code (own Montgomery ladder, own twisted-Edwards addition, own Hasse-interval count). |
| `gfpn_arith.py` | Pure-Python F_{p^5} = F_p[z]/(z^5-3) arithmetic, affine and Jacobian short-Weierstrass arithmetic, Tonelli–Shanks, Hasse-interval helpers, and an ECPP (Atkin–Morain) certificate verifier for PARI's `primecert` format. Calls no PARI code: this is the "independent re-verification" side. |
| `gfpn_audit.py` | The audit itself (one invocation per curve): source hashing and line citation, model derivation, SEA point counts (curve and quadratic twist), order certificate, n−1 factorization and embedding degree, CM discriminant, twist factorization / twist security, rigidity re-enumeration, figure provenance; writes `raw-result.json`, `audit-table.yaml`, `figure-provenance.yaml`, `certificates/`. |
| `check_run.py` | Completion-gate check: required artifacts, manifest fields, manifest/raw/audit-table agreement, factorization products, independent re-verification of every ECPP certificate in the package. |

External tools: PARI/GP 2.15.4 (`/usr/bin/gp`, with `pari-seadata`
0.20090618 installed by this task via apt), GMP-ECM 7.0.5 (apt `gmp-ecm`,
installed by this task), Python 3.11.15 with PyYAML. Sage is not used. A conda
Sage 10.9 was found at `/opt/conda-sage/envs/sage/bin/sage` (the dispatch note
said Sage was absent); it was not used and is recorded only as available.

## 2. Runs

| run | curve | status | wall (s) | peak RSS |
| --- | --- | --- | --- | --- |
| `RUN-GFPN-17ed52` | scurve_control (Ed448-Goldilocks / curve448) | completed_valid | 2.5 | 48 MB |
| `RUN-GFPN-b71f2f` | EcGFp5 | completed_valid | 814.6 | 465 MB |
| `RUN-GFPN-3bbef2` | EcMasFp5 | completed_valid | 213.8 | 243 MB |

`RUN-GFPN-81e5ca` was minted and confirmed free (`allocate_id.py --check`) as
the reserved fourth slot and was not used. Run identifiers were minted with
`python3 tools/allocate_id.py --next run --area GFPN` and each confirmed with
`--check`. The control run was executed and recorded before any GFPN
computation was started (contract control C-3 / stopping rule 3).

## 3. SCURVE control (RUN-GFPN-17ed52)

The repository's SCURVE lane contains no run directory with a certificate
(every `experiments/EXP-SCURVE-*/runs/` holds only `.gitkeep`; those contracts
are closed-form calibrators). The only executed SCURVE certificate package is
the Ed448-Goldilocks / curve448 base-point certificate
`coordination/goals/GOAL-SCURVE-15e805/batches/BATCH-0aef14/tasks/TASK-20260908-42e809/base-point-audit.yaml`
(sha256 `e4a0c12e…f5b174`), cited as `certificate_refs` by
`ledger/evidence/EV-SCURVE-e1ce7f.yaml`, with its inputs in
`raw-transcription.yaml` (sha256 `a918b8a1…98a675`). That package was used as
the control curve.

**Operationalisation of "match prior certificate bytes (or hash)"** (protocol
deviation D-1, see §7): the prior package is a prose YAML dossier, which no
independent implementation can reproduce byte-for-byte. The control therefore
(a) re-verifies both files' sha256 against the values observed in the tree
(hash match) and (b) regenerates every numeric certificate value in the M1
(curve448), M3 (edwards448) and M2 (falsifier) rows from the transcribed RFC
inputs with code written for this experiment, comparing value-for-value
against the hash-pinned bytes. Result: hash match true; 18/18 values identical
(on-curve residues, l·B = O, Hasse endpoints, h·l, multiple count, the
order-4 / order-2l positive controls, and M2's l·B = (0, p−1) with 2l·B = O).
`scurve_control_certificate_match: true`. Reproduced again from the recorded
command into a scratch directory after the GFPN runs: identical rows.

## 4. GFPN audit — how each primary metric was decided

**Model.** EcGFp5: the frozen paper states the double-odd equation
y² = x(x² + 2x + 263z) over GF(p)[z]/(z⁵ − 3) (`paper_fulltext.md` line 65;
field at lines 46–50) and its own change of variable to short Weierstrass
(A = (3b − a²)/3, B = a(2a² − 9b)/27). The audit derives A = 263z − 4/3,
B = 16/27 − 526z/3 from that and cross-checks the Hermez note's restated
Weierstrass constants (`note_fulltext.md` lines 123–126): identical.
EcMasFp5: y² = x³ + 3x + 8z⁴ (`note_fulltext.md` line 222).

**Point count (`sea_method_id`).** PARI/GP `ellcard` (SEA with seadata) over
F_{p^5}: 9.4–9.8 s per curve. The quadratic twist (twist by d = z + 2, a
non-square) is counted independently as well; N + N' = 2q + 2 holds for both
curves. Note on infrastructure: the dispatch session's probe that did not
finish in 15 minutes ran without `pari-seadata`; with the modular polynomials
installed the same `ellcard` finishes in about 10 s. That earlier non-finish
is an infrastructure fact, not a property of the curves.

**Order certificate (`regenerated_not_copied` control).** The candidate
integer is the SEA count (regenerated), never the note's integer. The
certificate is independent of PARI's SEA: (i) n proven prime by PARI
`primecert` (ECPP), re-verified by `gfpn_arith.verify_ecpp` (own modular EC
arithmetic; checks m = N+1−t, s | m, q > (N^{1/4}+1)², non-singularity,
[m]P = O, [s]P ≠ O down a chain ending in a q ≤ 2⁶⁴ proved by deterministic
Miller–Rabin); the verifier rejects corrupted chains (tested). (ii) A
deterministic point P (smallest x ∈ F_p with a square RHS; for EcGFp5 P := 2Q
to land in the odd part) with [n]P = O computed by the pure-Python Jacobian
arithmetic. (iii) For EcGFp5, the rational 2-torsion point (X = 2/3, the
double-odd (0,0)) is a root of the cubic and the remaining quadratic
x² + 2x + 263z is irreducible (its discriminant is a non-square), so 2 | #E
and #E ≢ 0 mod 4. (iv) Exactly one multiple of h·n lies in the Hasse interval
[q+1−⌊2√q⌋, q+1+⌊2√q⌋], hence #E = h·n. The certified order equals the SEA
count for both curves, and equals the self-reported integer for both curves.
Because the SEA count finished, the dispatch session's question — whether a
Hasse-interval certificate alone would satisfy `regenerated_not_copied` — did
not have to be decided: the integer is regenerated by SEA and then
independently certified. (Had SEA not finished, the certificate would still
have been a proof, but its candidate integer would have originated in the
note; that case did not arise and is not claimed.)

**Cofactor.** 2 (EcGFp5) and 1 (EcMasFp5), from the certified order.

**Embedding degree.** n − 1 factored: trial division to 10⁶, then GMP-ECM
factor hints (background jobs launched by this task; logs copied into each
run's `certificates/ecm/`) re-verified by exact division, Pollard rho for
pieces < 2⁹⁰, and a primality proof for every prime factor (deterministic
Miller–Rabin below 3.3·10²⁴, else ECPP re-verified independently). Both
factorizations are complete; e = ord_n(q) is computed exactly from them.
EcGFp5: n−1 = 2⁵·5·163·769·1059871·p33·p51 (the paper's stated factorization,
regenerated, not copied), e = (n−1)/5, 317 bits. EcMasFp5:
n−1 = 2·337·571·5519·363285325079·p27·p50, e = n−1, 320 bits.

**CM discriminant.** t = q+1−N, D = t² − 4q. |D| is 322 bits for both curves.
Both |D| factor completely (EcMasFp5: 4691·335249·65480383697·p27·p51;
EcGFp5: 2²·3·41·p313 where p313 is a proven prime — the ECM job on it was
stopped after 1085 curves once the primality proof existed), so the squarefree
part and fundamental discriminant are exact: 322 bits for both (conductor 1
for EcMasFp5, 2 for EcGFp5). EcMasFp5's self-reported D integer reproduces
exactly; its stated "323 bits" does not equal the integer's binary length
(322; the hex string has 81 digits with leading nibble 3). Recorded as an
observation with a plausible explanation (sign character counted); not
adjudicated here. The EcGFp5 paper states no discriminant.

**Twist.** N' = 2q+2−N agrees with the independent SEA count of the twist.
Factorizations complete with primality proofs. EcMasFp5: N' = p116 · p205
(the note's two factors reproduce as integers; regenerated by ECM, run 207 at
B1 = 10⁶). Twist security = log₂√(π·ℓ'/4) = 0.5·log₂ℓ' + 0.5·log₂(π/4) =
101.9321 bits, |Δ| = 0.0021 from the self-reported 101.93 (tolerance 0.01).
The curve-side figure 159.83 recomputes as 159.8257 (same formula).
Twist embedding degree (ℓ'−1)/15 (201 bits) reproduces. EcGFp5:
N' = 2·3·13·379·3347303·3852461398139·p242, twist security 120.66 bits, twist
embedding degree (ℓ'−1)/2 (241 bits); the paper states no twist figures, so
these rows have no self-report to compare against.

**Rigidity.** The published searches are re-enumerated in the published
order with PARI `ellsea(E, tors)` early abort, whose zero return is a proof
that a small prime coprime to `tors` divides #E (semantics verified
empirically on F_{p²} before use and documented in PARI's function
description). EcMasFp5 (`find_ec_over_gfp5`, A from 0, c = 1..49, i = 1..4,
prime order): 620 candidates examined in 194 s; 398 excluded by early abort,
221 by a full count that is composite; the first prime-order curve is
candidate #620 = (A=3, c=8, i=4), the published one. EcGFp5 (c = 1, 2, …;
i = 1..4; +cz^i then −cz^i; order 2n with n prime; Pornin's quadratic-residue
pre-filter applied as published): 2097 candidates, first hit #2097 = the published b = 263z; details in §6.

**Figure provenance.** `figure-provenance.yaml` per run. `field_security_142`
is tagged **asserted** on EcGFp5 (derived inside the paper from a cost model
of Gaudry's attack with "very optimistic assumptions" language; lines
131–149) and **inherited** on EcMasFp5 ("we inherit by default its security…
approximately achieves a 142-bit security level", line 257).
`twist_security_101_93` is tagged **computed** and recomputed (101.9321).
Other self-reported figures (159.83, D "323 bits", e = n−1, (nt−1)/15,
e = (n−1)/5, the n−1 factorization, orders) are tagged and compared in the
same table. Attack cost is not recomputed (scientific boundary).

## 5. Failed, unfinished and stopped attempts (all recorded, none discarded)

- Development dry-runs (not run records; in the session scratchpad): the
  first control dry-run mismatched two values because of two bugs in my own
  code (RFC 7748 `a24 = (A−2)/4` convention; Hasse lower endpoint
  `p+1−⌊2√p⌋`), fixed before the official control run. My first ECPP
  verifier failed on a genuine certificate because of a missing factor in the
  projective addition formula (X3 = H·A); fixed and re-tested with two
  corrupted-certificate negative controls before use.
- A first SEA probe launch failed immediately: `/usr/bin/time` is not
  installed (infrastructure); relaunched without it.
- A gp probe hung after finishing because gp waited on stdin when not
  detached; killed and rerun with `</dev/null` (infrastructure; no result
  lost — all official runs use `stdin=DEVNULL`).
- An accidental `pkill -f` matched the executing shell itself (exit 144); no
  run or artifact was affected; the intended ECM process was then stopped by
  pid.
- ECM job on the EcGFp5 discriminant cofactor stopped by the executor after
  1085 curves with no factor, because the cofactor had been proven prime
  (`ecm_gf_D.stopped` in the copied logs states this).
- The dispatch session's 15-minute non-finishing `ellcard` probe is explained
  by the absent `pari-seadata` package (installed here).

## 6. EcGFp5 run (RUN-GFPN-b71f2f) — filled from the official run

`RUN-GFPN-b71f2f`: completed_valid, wall 814.6 s, peak RSS 465 MB, CPU 810.9 s.
SEA 9.79 s (curve) / 9.75 s (twist); #E = 2n with n the paper's 319-bit prime
(SEA count equals the self-reported 2n; independent certificate agrees).
Embedding degree e = (n−1)/5, 317 bits (paper: "(n − 1)/5, a 317-bit
integer"); n−1 factorization identical to the paper's, regenerated. |D| = 322
bits, fundamental discriminant 322 bits (conductor 2). Twist order
2·3·13·379·3347303·3852461398139·p242, twist security 120.66 bits, twist
embedding degree (ℓ'−1)/2, 241 bits — no self-report exists for these.
Rigidity: 2097 candidates examined in 794 s (2096 predecessors of the
published b = 263z): 1552 rejected by Pornin's own quadratic-residue
pre-filter (b or a² − 4b a square), 445 rejected by `ellsea(E, 2)` early abort
(an odd small prime divides #E), 99 counted in full with #E/2 composite; the
first curve with #E = 2·prime is candidate #2097 = (c = 263, i = 1, sign +),
i.e. the published b = 263z. `figure_security_142` tagged **asserted** with
the model-derivation lines cited.

## 7. Protocol deviations

- **D-1 (control match definition).** "Re-run must match prior certificate
  bytes (or hash)" is operationalised as hash re-verification of the prior
  package plus value-for-value regeneration of all numeric certificate
  entries by independent code (18 values), because the prior package is a
  prose dossier, not a machine-regenerable byte stream. No amendment was
  filed; the Coordinator/Validator may judge whether this reading satisfies
  the control.
- **D-2 (SCURVE tooling reuse).** The contract says to reuse SCURVE
  certificate schemas and verification wrappers. The SCURVE lane has no
  reusable wrapper code in the repository (its executed certificate is a
  hand-authored YAML dossier), so the wrapper was written here, keeping the
  SCURVE package's certificate shape (on-curve, non-identity, l·B = O,
  Hasse-interval uniqueness, positive/negative controls) as the schema of
  `order-certificate.json`. Sage is not installed for the harness pipeline;
  PARI/GP is used directly, as the contract's "Sage-PARI" wording allows.
- **D-3 (factor hints from outside the run).** GMP-ECM ran as background
  jobs started by this task before/while the official runs executed; the
  runs consume those logs as hints only, copy them into `certificates/ecm/`,
  and re-establish every factor by exact division plus a primality proof, so
  each run's factorization certificate is self-contained.
- **D-4 (rigidity watchdog).** A 14 400 s wall-clock watchdog is set on each
  rigidity sweep as machine protection (wall clock is advisory in the
  contract). It was not reached.
- Observation outside write scope: `inputs/PORNIN-2022-274-ECGFP5/source_record.yaml`
  says "modulus z^5 − 2" in its headline; the frozen paper text and the
  Hermez note both say z⁵ − 3, which the audit uses. Reported, not edited.

## 8. Reproduction

Each run's `command.txt` holds the exact wrapper command; `trial-plan.json`
lists them with the implementation files' sha256. Everything is deterministic
(no seeds; the point search is by smallest x; PARI's internal randomness in
`primecert` only affects which valid certificate is emitted, and every
emitted certificate is stored and re-verified). `check_run.py <run-dir>`
re-verifies each package including all ECPP certificates.
