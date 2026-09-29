# REVIEW-ICPERF-20260915-a33cda — joint R6 — TASK-20260915-abf147

Independent re-derivation (pre-registered, not blind — see §7) of the reduced
Gröbner basis of the Weil-descent instance `n15l5-1-S` with field equations
over GF(2), plus the proves-too-much (perturbed-system) control.

Governing documents read: `review-plan-r6.yaml`, `review-plan-r6-addendum-1.yaml`,
`agents/validator.md`, `AGENTS.md`, `CLAUDE.md`. This report covers **R6 only**;
`whole_claim_verdict` is null by construction.

Validator role contract note: this task is a blind re-derivation joint, not a
validation of a producer receipt, so the `validation_report` block in
`attestation.yaml` records my own derivation's artifacts and recomputations and
leaves producer-receipt fields (`run_ids`) empty. `VAL-20260916-abf147-R6` is
bound to the task token because `tools/allocate_id.py` mints no `VAL` type.

## 1. The four values

Instance: `n15l5-1-S` (n = 15, l = 5, m−1 = 3; INFO file: modulus bits
`1010110000000001`, planted x-coordinates `11010-00000-11010`). Ideal: the 42
shipped polynomials in 42 variables (15 `x`, 27 `e`) together with `v^2 + v`
for every variable, over GF(2).

| # | quantity | value | how obtained |
|---|----------|-------|--------------|
| 1 | cardinality of the reduced Gröbner basis | **43** | Macaulay2 1.22 `groebnerBasis(I, Strategy => "F4")`, GRevLex, Magma variable order (run 1); minimality + reducedness re-checked in my own Python (`check.run1.json`) |
| 2 | maximal total degree in the basis | **2** | same; degree histogram {1: 40, 2: 3} |
| 3 | unit ideal? | **no** (proper ideal) | 1 ∉ basis; the basis has 3 GF(2)-zeros |
| 4 | quotient dimension over GF(2) | **3** | M2 `degree` of the F4 basis = 3; **independently** brute force over all 2^15 x-assignments (e-variables determined by their defining equations) gives exactly 3 GF(2)-solutions; my own Buchberger over the basis gives standard monomials {1, xb3, xc3} |

Monomial order used for the pre-registered value: **GRevLex** (Macaulay2
`GRevLex => {1,…,1}`, `MonomialSize => 32`, `Position => Up`) on the 42
variables in the Magma file's generator order
`x_1_0..x_1_4, x_2_0..x_2_4, x_3_0..x_3_4, e_1_0..e_1_4, e_2_0..e_2_8, e_3_0..e_3_12`
(renamed `xa0..xc4, ea0..ec12` for engine-safe identifiers).

Pre-registered at **2026-09-16T08:42:41Z** in `PREREGISTERED-VALUES.json`
(sha256 `1c6008b4…571645`), the moment run 1 returned, before any other
repository file was opened. Engine input sha256
`d7672055eebf569499094ab194e46dd0fa15526d4017927bb1bed2fdce6f89d7`; re-emitting
from the current conversion module reproduces that hash byte-for-byte, so the
parse-and-emit path did not change after pre-registration (the module's own
hash did change: checker and own-Buchberger code were appended afterwards).

### The basis itself (run 1, verbatim in `artifacts/runs/run1-m2-grevlex-unperturbed.stdout.txt`)

40 linear elements pin every variable in terms of `xb3` and `xc3` — all 27
e-variables are constants (`ec12, …, ea0` = 0 except `eb0 = eb2 = eb6 = 1`),
`xa0 + xb3 + xc3`, `xa1 + xb3 + xc3`, `xa3 + xb3 + xc3`, `xb0 + xb3`, `xb1 + xb3`,
`xc0 + xc3`, `xc1 + xc3`, and `xa2 = xa4 = xb2 = xb4 = xc2 = xc4 = 0` — plus three
elements in the free pair: `xc3^2 + xc3`, `xb3^2 + xb3`, and
`xb3*xc3 + xb3 + xc3 + 1 = (xb3 + 1)(xc3 + 1)`. The zero set is
`(xb3, xc3) ∈ {(1,0), (0,1), (1,1)}`: three points, which are the planted
solution `(x1, x2, x3) = (11010, 00000, 11010)` and its two permutations under
swapping the three x-blocks (the system is symmetric in them).

### Order sensitivity: checked, and the values are order-independent for this instance

Argument. The three solutions are affinely independent (their `(xb3, xc3)`
projections are three distinct points of GF(2)^2, not on an affine line), so the
affine-linear forms vanishing on them form a space of dimension exactly
42 − 2 = 40, and the 40 linear basis elements above are a basis of it. The
quotient has dimension 3 (brute force, engine-independent). In **any** monomial
order the reduced basis therefore contains 40 linear elements whose leading
variables are 40 distinct variables, the two remaining variables `u, v` give
standard monomials `{1, u, v}` (the only 3-element order ideal not divisible by
the 40 leading variables and by `u^2, v^2`, which are leading terms of the
field equations), and the leading ideal's minimal generators are those 40
variables plus `u^2, v^2, uv`: 43 elements, every non-leading term standard,
hence total degree ≤ 2. So (1) = 43 and (2) = 2 in every order; only which pair
`(u, v)` is free depends on the order.

Empirical confirmation with my own Buchberger (Python, `own-gb` subcommand,
started from the verified grevlex basis — not an engine run):

| order | variable order | cardinality | max degree | free pair | file |
|-------|----------------|-------------|------------|-----------|------|
| grevlex | Magma | 43 | 2 | (xb3, xc3) — reproduces the engine basis exactly as a set | `owngb.unperturbed.grevlex-magma.json` |
| lex | Magma | 43 | 2 | (xb3, xc3) | `owngb.unperturbed.lex-magma.json` |
| grevlex | reversed | 43 | 2 | (xa0, xb0) | `owngb.unperturbed.grevlex-reversed.json` |
| lex | e-variables first | 43 | 2 | (xb3, xc3) | `owngb.unperturbed.lex-efirst.json` |

Each of those bases passes my minimality/reducedness check, the Buchberger
criterion, vanishes on the 3 solutions, and reduces all 42 inputs to zero.
The engine-level order check (run 4, F4 with reversed variables) was censored
at the 9 GiB resident-set bound and is reported as such in §3.

## 2. Route (mine, end to end)

Files read for the derivation, all under `inputs/TRIMOSKA-ECICB-2024/upstream/`:

- `benchmarks/INFOn15l5-1-S.dimacs` — parameters, modulus, planted solution.
- `benchmarks/Xn15l5-1-S.anf` — WDSAT XOR-AND form; **primary parse**.
- `benchmarks/n15l5-1-S.in` — Magma `BooleanPolynomialRing` form; **second, independent parse** used as a cross-check.
- `README.md`, `Weil_descent.sage` — the generator, read to pin the ANF semantics (permitted by the plan).
- `inputs/TRIMOSKA-WDSAT-2024/upstream/README.md` — the ANF format definition.

The CNF-XOR `.dimacs` was not used (it introduces 460 auxiliary Tseitin
variables and is not the polynomial system).

ANF semantics I used (from the WDSAT README and the generator's
`get_ANF_output_X/E`): a line `x <terms> 0` is an XOR clause that must be true;
`T` is the constant 1; `.d v1 … vd` is a degree-d monomial; the polynomial that
must vanish is `sum(terms) + 1` with `T` counting as 1. Variables 1–15 are the
x-bits in Magma order, 16–42 the e-bits. This mapping was **checked, not
assumed**: the two encodings parse to the same 42 polynomials, in the same order
(`inspect.unperturbed.json`: `anf_and_magma_identical_in_order: true`).

Conversion code: `artifacts/parse_instance.py` (parser for both encodings,
brute-force counter, M2/Singular emitters with optional perturbation,
reduced-basis checker, own Buchberger). Runner: `artifacts/run_bounded.py`
(wall-clock bound + **resident-set** bound polled from `/proc`, summed over the
child's session; no `RLIMIT_AS`).

Input structure observed: 5 linear + 9 quadratic + 13 cubic e-defining
equations (`e_j + f_j(x)`), and 15 quadratic descent equations in the
e-variables only; 6 of the 42 polynomials carry a constant term.

## 3. Engine invocations (6 of the plan's `maximum_runs: 6`)

Host: 4 CPUs, 15 GB RAM. M2's F4 is multi-threaded here (CPU > wall is expected).
All bounds are wall-clock plus **resident-set** (polled), never address space.

| run | engine / strategy / order | system | load₁ at start | outcome | wall s | CPU s | peak RSS | record |
|-----|---------------------------|--------|----------------|---------|--------|-------|----------|--------|
| 1 | M2 1.22 F4, GRevLex, Magma vars | unperturbed | 0.03 (host check ~10 min earlier; runner reading lost) | **completed** | ≈58 (shell timing) | F4 45.76 (engine-reported) | **not measured** — runner bug, see note | `run1-….run.MANUAL-NOTE.json`, stdout verbatim |
| 2 | M2 F4, GRevLex, Magma vars | P1: `+ xa0` on eq #28 | 0.91 | **killed_rss** at 8 GiB | 83.4 | 294.7 | 8.34 GiB polled / `ru_maxrss` 8.96 GB | `run2-….run.json` |
| 3 | M2 F4, GRevLex, Magma vars | P2: eq #42 deleted | 1.45 | **completed** | 36.9 | 111.6 | 7.72 GiB polled / `ru_maxrss` 8.48 GB | `run3-….run.json` |
| 4 | M2 F4, GRevLex, **reversed** vars | unperturbed | 1.14 | **killed_rss** at 9 GiB | 73.1 | 236.1 | 9.19 GiB polled / `ru_maxrss` 9.86 GB | `run4-….run.json` |
| 5 | Singular 4.3.2 `std`, `dp`, Magma vars, `option(redSB)` | unperturbed | 1.66 | **killed_wall_clock** at 600 s | 600.2 | 600.1 (1 thread) | 1.17 GiB | `run5-….run.json` |
| 6 | M2 `Strategy => "MGB"`, GRevLex, Magma vars | P1 | 0.47 | **killed_wall_clock** at 600 s | 600.4 | 600.5 (1 thread) | 8.17 GiB | `run6-….run.json` |

Runs 2, 4, 5, 6 are **infrastructure outcomes** (core rule 5): they are
observations about engines on this host under my bounds, not values and not
evidence about the mathematics. The RSS bound was 8 GiB for runs 1–2 and 9 GiB
for runs 3–6 (raised inside the 10 GB task budget after run 2, with ~10 GB
available on the host).

Run 1 note: the first version of `run_bounded.py` reaped the child with
`Popen.poll()` and then crashed on `wait4`, after the engine had exited
normally and its stdout/stderr were fully captured. No resource record exists
for run 1; peak RSS is reported as **not measured**, not estimated. Run 3 (same
engine and order on 41 of the 42 polynomials) is the nearest measured
reference; run 1 completed under an 8 GiB polled bound. Re-measuring would
cost one more ~1-minute invocation, which the plan's run cap did not leave.

## 4. Independent verification of the printed bases (no engine trusted)

For runs 1 and 3, `parse_instance.py check-output` re-parsed the printed
elements and established, in Python:

- minimality and reducedness under the stated order (no leading term divides another; no term of any element lies in another element's leading-term ideal);
- Buchberger's criterion (all S-polynomials of non-coprime pairs reduce to zero);
- the basis vanishes on every brute-force GF(2) solution of the (possibly perturbed) input system, so ⟨GB⟩ ⊆ I + FE (I + FE is radical with all zeros in GF(2)^42);
- every input polynomial reduces to zero modulo GB ∪ {v²+v}, so I + FE ⊆ ⟨GB⟩.

Hence in both cases the printed set **is** the reduced Gröbner basis of
I + FE, independently of what the engine did internally
(`check.run1.json`, `check.run3.json`: `ideal_equality_established: true`).
For run 1 the M2 default engine, re-run on the F4 output inside the same
script, also returned the identical set (`DEFAULT_GB_EQUALS_F4_AS_SET true`).

## 5. Proves-too-much control: the perturbed system

Both perturbations were predicted by brute force **before** any engine saw them
(`inspect.perturbed-P1-add.json`, `inspect.perturbed-P2-del.json`).

| | unperturbed | **P2**: delete equation #42 (last descent equation) | **P1**: add monomial `xa0` (= x_1_0) to equation #28 (first descent equation) |
|---|---|---|---|
| emitted input sha256 | `d7672055…` | `f04dd7a0…` | `fca2cdb0…` (F4), `44d56914…` (MGB) |
| brute-force GF(2) solutions (my code, before engine) | 3 | **9** | **1** (planted solution no longer satisfies it) |
| engine run | run 1 completed | run 3 completed | runs 2 (F4) and 6 (MGB) **censored** |
| (1) cardinality | 43 | **62** | 42 — by argument, not by engine: one GF(2) point + radicality ⇒ I + FE is the maximal ideal of that point, whose reduced basis in every order is `{v_i + s_i}` |
| (2) max degree | 2 | 2 | 1 — same argument |
| (3) unit ideal | no | no | no |
| (4) quotient dim | 3 | **9** (M2 `degree` 9 = brute force 9) | 1 |
| independent verification of printed basis | yes (§4) | yes (§4; degree histogram {1: 35, 2: 27}, 135 S-pairs checked) | n/a — no engine basis to check |

**Control verdict: discriminates.** On the identical route (my parse → my
emission → M2 F4 GRevLex, Magma order), deleting one equation changed the
cardinality from 43 to 62 and the quotient dimension from 3 to 9, exactly as
brute force predicted. The pipeline reads what it claims to read. The
"add one monomial" variant discriminated at the brute-force stage (3 → 1
solutions) and in the emitted engine input (one line differs), but its engine
run did not finish under my bounds with either mathicgb strategy; its basis is
known by argument (42 linear elements), not by an engine, and I report it as
such.

## 6. R6 verdict

**holds** — for the quantity as stated in `review-plan-r6.yaml`, my own route
yields cardinality 43, maximal degree 2, proper ideal, quotient dimension 3
under GRevLex (and 43 / 2 in every monomial order, by the §1 argument and four
computed orders), with the printed basis verified independently of the engine
and the perturbed control discriminating.

What this is worth is for the Coordinator to weigh, with §7 in hand: the
unperturbed numbers were **pre-registered but not blind**. The quotient
dimension (value 4) was not exposed to me anywhere and is the one value here
that was derived with no prior at all; it is also the value settled by a route
(brute force) that uses no Gröbner engine.

## 7. Blindness: disclosure and timeline

- **Exposure, before derivation.** `coordination/review/icperf-20260915-a33cda/review-plan-r6-addendum-1.yaml`, which the dispatch brief instructed me to read in full first, quotes in its `leak_sites_found` block `gb_size: 43`, `result: proper ideal` and the summary line `gb_size = 43 / maxdeg = 2`. I read it at approximately **08:29Z on 2026-09-16**, at task start, before opening any instance file. This exposed values (1), (2) and (3). It did not expose value (4). By the addendum's own weighting this makes the unperturbed derivation *informed rather than independent*, and the perturbed control carries the joint. The addendum designed to protect the blind is itself a leak site; I record that as forward guidance in §8.
- **No `blind_from` path was read**, in either the original list or the addendum's extension. In particular I did **not** open `inputs/TRIMOSKA-ECICB-2024/source_record.yaml` (I listed `upstream/` and `upstream/benchmarks/` only and never listed or read the directory above them), nor `experiments/EXP-ICPERF-e21835/specification.yaml`, nor the sibling reviewer's directory, nor `review-plan.yaml`, nor `review-plan-addendum-1.yaml` (the round's main addendum, not named in my documents; I left it unread), nor the dispatch queue. So `blind_from_respected: true` is literally true as to paths, and the exposure above is disclosed separately.
- **Pre-registration** at 08:42:41Z, immediately after run 1 returned. Everything in §1 was fixed before I read `templates/research-records.md` (attestation format) and `tools/check_review_independence.py` (field names), the only non-instance files opened after the derivation.
- Values were **not** looked up anywhere after pre-registration either; the perturbed values exist in no repository file.

## 8. Findings the assignment did not ask for

1. **The Magma `.in` file carries a literal `0 +` leading term in 9 of its 15 descent equations** (generator printing artifact). It must be read as the zero polynomial; the ANF form has no such artifact. A converter that mis-tokenised `0` (as a variable, or as the constant 1) would produce a different system — a place where two implementations could disagree.
2. **The ANF and Magma encodings are identical** as ordered lists of 42 polynomials under the WDSAT semantics; the three-equation-block variable numbering (x first, then e) matches the Magma generator order exactly.
3. **The `S` instance's solution set is degenerate**: all three solutions have two equal x-coordinates (`11010`) and the third equal to `0`, i.e. `x(P_2) = 0` is the curve's 2-torsion point and `P_1 = ±P_3`. Whether such planted solutions are representative of point-decomposition instances is a question for the executor's scope statement, not for this joint.
4. **Macaulay2 F4's resident memory on this 42-variable system is 8–10 GB** and is sensitive to variable order and to one-monomial perturbations: Magma order fits under 8 GiB, reversed order exceeds 9 GiB, and adding a single x-monomial to one descent equation exceeds 8 GiB within 83 s. A memory bound for this instance family must therefore be measured per variable order, not per system size. Singular `std` used only 1.2 GiB but did not finish in 600 s single-threaded.
5. **The perturbed system with one solution (P1) is much harder for both mathicgb strategies than the original with three.** Difficulty is evidently governed by the structure of the descent equations (e-only in the original) rather than by the number of solutions.
6. **Order-independence of (1) and (2) is provable for this instance** (§1); any engine, in any order, must return 43 elements of degree ≤ 2 or be wrong.
7. **The addendum is itself a leak site** (§7). Forward guidance to the program: a mitigation document for a blind must describe leak sites by path only, never by quoting the protected value.
8. My runner's first version lost run 1's resource record (§3); fixed before run 2 and disclosed rather than backfilled.

## 9. Limitations

- The unperturbed values are pre-registered, not blind (§7).
- No cross-engine confirmation of the unperturbed basis was obtained: Singular did not finish in 600 s. It would cost a longer wall bound (unknown; >10 min single-threaded) or `slimgb`, and one more run beyond the plan's cap. The engine-independent verification in §4 makes the cross-engine check inessential for correctness of the printed basis.
- The engine-level order-sensitivity run (reversed variables) was censored; order independence rests on the §1 argument and my own Buchberger over the verified basis.
- Run 1's peak RSS was not measured.
- P1's basis is known by argument, not engine; its engine runs were censored at 8 GiB RSS (F4) and 600 s (MGB).
- All statements are about `n15l5-1-S` with the field equations, over GF(2), on this host. Nothing here transfers to other instances, orders on other instances, or any claim about index-calculus performance.

## 10. Artifacts (all under this task directory)

- `PREREGISTERED-VALUES.json` — write-once, 08:42:41Z.
- `artifacts/parse_instance.py`, `artifacts/run_bounded.py` — my conversion code and runner.
- `artifacts/inspect.unperturbed.json`, `inspect.perturbed-P1-add.json`, `inspect.perturbed-P2-del.json` — parses, encoding comparison, brute force (with full solutions).
- `artifacts/n15l5-1-S.*.m2`, `n15l5-1-S.unperturbed.dp.sing` — emitted engine inputs (unperturbed, reversed order, P1 F4, P1 MGB, P2, Singular).
- `artifacts/runs/*.stdout.txt`, `*.stderr.txt` — verbatim engine output; `*.run.json` — bounded-run records (runs 2–6); `run1-….run.MANUAL-NOTE.json` — labelled reconstruction for run 1.
- `artifacts/check.run1.json`, `check.run3.json` — independent verification of the printed bases.
- `artifacts/owngb.unperturbed.*.json` — own Buchberger in four orders, with elements.
