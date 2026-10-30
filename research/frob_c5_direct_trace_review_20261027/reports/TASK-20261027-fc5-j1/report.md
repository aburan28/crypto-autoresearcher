# J1 source and claim fidelity: FROB C5 direct-trace successor

Reviewer task: `TASK-20261027-fc5-j1`; Conductor: `T-628`; date: 2026-10-27 UTC.

**Joint verdict: holds.** The pinned successor checker implements an actual repeated-q-power polynomial calculation, reproduces the three frozen trace matrices, and rejects the specified q=13 mutation under ordinary Python and `-O`. Its report correctly limits the result to replacement mathematical replay. It does not establish the original Sage process's loaded sources or historical C5 success. This report owns only `J1-source-and-claim-fidelity`; the coordinator must compose it with the separately sealed blind J2 report before closing the review round.

## Bound claim and isolation

The prospective plan is `research/frob_c5_direct_trace_review_20261027/review-plan.yaml`, committed at `dd4afa8950a12ec3aff5697c8a1ccd0bf4c0834a`. Producer inputs are the 14 files in `inputs.json`, whose producer revision is `ef1cf2979ef226378e0d0d9529c53fb6caedae52`. The claim is equality, on all 25 entries per cell, of the direct five-term trace with the polynomial `h(M)` of the separately source-bound q-power matrix, base-field image, rank/nullity 1/4, and rejection of the fixed q=13 mutation. This is source-informed review, not blind re-derivation.

I claimed T-628 explicitly at 2026-10-27T23:03:33.778333Z (attempt `455b8386-bba7-4dfd-a7d9-3b3e80a2d72a`, fencing epoch 1). No J2 report, directory contents, isolated statement, or coordinator machine receipt was opened. I received coordination-only messages that the machine packet existed; no sibling conclusions were provided. Workspace HEAD advanced during the coordinator's archival work; `raw/summary.json` records the observed HEAD. Every producer file was separately compared to its manifest and exact producer Git blob, so this report does not substitute the moving workspace HEAD for the frozen producer revision.

## Three review dimensions

| Claim/scope | Machine status | Fidelity | Review outcome |
|---|---|---|---|
| J1 successor trace computation, source binding, rank/image, fixed mutation and failure controls on the three frozen cells | passed | faithful_scoped | validated_scoped for J1 only |
| Prior exact q-power matrix receipt, checked through its own ordinary-Python replay | passed | faithful_scoped | validated_scoped as executable replay |
| Original Sage loaded-source custody and historical C5 success | not_verified | partial bridge; no promotion claimed by producer | inconclusive |
| Fresh Lean kernel/axiom verification of the adjacent quotient theorems | not_verified | not_reviewed as a fresh formal proof gate | inconclusive |

The overall prospective review still requires J2 and the coordinator's independence/composition gate. This report makes no official experiment, hypothesis, or goal transition.

## Observation: bindings and envelopes

`raw/input_hashes.json` verifies all 14 declared byte lengths and SHA-256 values against the worktree and the exact Git blobs at the producer commit. No mismatch occurred. The checker is `9673e46c0abf1548e2d27f5ae5b48f9c0cba445166b23d90ba90d3094e7eb720`; the prior matrix receipt is `22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005`; the direct replay is `4188f268e95ae37539153fe59281dd3f4e267d3cf38fd09afec4a3e24aea99cb`.

`raw/prior_source_bindings.json` separately checks the seven source hashes recorded by the earlier replay: its checker, fixtures, specification, archived Sage driver, archived core/lattice helpers, and archived independent checker. The earlier `recheck_matrix.py --check` produced `byte-exact C5 matrix receipt match`. Its `-O` invocation exited 1 with `C5 matrix validation requires Python assertions`; that is an intentional refusal because the older implementation uses assertions. The successor uses explicit exceptions and succeeds, with its controls still active, under `-O`.

Each frozen native output has exactly three logical lines: `RESULT_JSON_BEGIN`, the JSON payload, and `RESULT_JSON_END`. The successor checks its SHA-256 before parsing, then its cell, q, n and modulus. `raw/native_envelopes.json` preserves those fields, top-level keys and C5 flags. These outputs supply parameters and historical flags; they do not provide the reconstructed matrix. The matrix comes from the separately pinned prior receipt.

| Cell | Native SHA-256 |
|---|---|
| FROB-SPLIT-q11n5 | d9f74a8480e3bfc032693caaa56a19eb91f9aceb2e91a73a9c8de326984ca562 |
| FROB-NOLATTICE-q13n5 | 4791dba1f91156343044120a012ec45b762ac9c0280547b1ad9ee2a94ef04751 |
| FROB-EQDEG-q19n5 | 0f0c8ee95024d572c230511dd4f6d83dcf140f0bf5f7e1543c62f18e33763b4a |

The digest pins authenticate equality to selected archived bytes, not the identity of a historical executing process. The native data are read more than once by the checker; this is not an immutable-snapshot security mechanism against concurrent adversarial edits. The pinned values and review replay are appropriate to this fixed mathematical fixture scope.

## Comparison: directness and exact arithmetic

`direct_trace_matrix` constructs columns from the constant-first power basis `(1,x,x²,x³,x⁴)`. For each vector it adds the current residue exactly five times, replacing the term by its q-th power after each addition. The final extra powering is unused and does not add a sixth term. `product_mod` convolves coefficient vectors, then reduces from highest degree downward against the monic polynomial. The reduction cancels each leading coefficient modulo q. `power_mod` is binary exponentiation with exact Python integers and modular reduction; no floating-point arithmetic is used.

The direct function has no matrix argument and does not call `mat_product` or `mat_geometric_sum`. The review replaced both helpers with functions that raise immediately, then successfully constructed the q=13 direct trace. The separately executed matrix path sums `I,M,M²,M³,M⁴`; equality uses full nested-list equality and therefore tests all 25 entries. This removes the historical same-matrix tautology.

| q | Frozen modulus | Nonzero trace row | Rank/nullity |
|---:|---|---|---|
| 11 | x^5 + 2*x^4 + 1 | [5,9,4,3,5] | 1/4 |
| 13 | x^5 + 8*x^4 + 1 | [5,5,12,8,1] | 1/4 |
| 19 | x^5 + 3*x^4 + 1 | [5,16,9,11,5] | 1/4 |

All other rows are exactly zero. Both ordinary and optimized replay outputs are byte-for-byte equal to the frozen `replay.json`. Independently of the elimination implementation, the displayed matrices have rank exactly one because their only nonzero row has first entry 5, which is nonzero in all three prime fields. The monic degree-five quotient has the five displayed basis elements, so rank-nullity gives nullity four. Their image equals the constant line: it is contained there, and the image of 1 is the nonzero scalar 5. The raw trace itself is not an idempotent projector; dividing it by 5 gives the projection when the usual trace identities hold.

The direct and prior q-power reconstruction paths use separately written implementations of familiar convolution, long division and binary exponentiation, but these are related algorithms with shared mathematical inputs. My inspection and replay are source-informed and do not replace J2's independently derived arithmetic.

## Controls and a deliberate boundary counterexample

`review_checks.py` executes 13 checks under each of ordinary Python 3.9.25 and `-O`. Exact exceptions and accepted boundary cases are in `raw/controls-normal.stdout.txt` and `raw/controls-optimized.stdout.txt`; every subprocess command, return code, stdout and stderr is retained.

The rejection checks cover: q=13 entry (1,1) changed 2→3; a bad native digest; changed replay parameters; wrong matrix shape; out-of-range entry; malformed native start marker; an extra native line; changed native q; changed native nullity; and a changed top-level prior-replay digest. Tests beneath the hash layer deliberately recompute a fixture digest in a temporary `/var/tmp` tree, so they exercise the parser/semantic guard without pretending to bypass the production hash pin. The specified q=13 mutation raises `ValueError: direct trace differs from h(M): FROB-NOLATTICE-q13n5` in both modes.

**Trace equality alone does not identify M.** I substituted `M²` for the q=13 matrix at the internal `check_cell` boundary. This different matrix was accepted. Since `M^5=I`, multiplication by 2 permutes exponents modulo 5, so `h(M²)=h(M)`. The exact alternate matrix is in the control output. Thus the trace predicate is many-to-one; a report claiming it proves every q-power matrix entry would be incorrect. The actual producer expressly relies on the separately source-bound prior matrix replay, whose exact bytes and regeneration passed here. The top-level checker rejects changed replay bytes before reaching this internal test. The M² result is a necessary limitation of the predicate, not a counterexample to the pinned successor claim.

I also changed the historical `T_equals_hM` flag to false in a deliberately rehashed temporary native fixture. `check_cell` still computed and accepted the direct equality, and returned the false flag as metadata. This is consistent with the producer's historical boundary: the old flag is not the proof of the new calculation. The production hash pin prevents this fixture from replacing the frozen output.

## Assumptions, source fidelity and historical boundary

The arithmetic assumes the exact three prime moduli q=11,13,19, monic degree-five polynomials and constant-first basis. Primality and `5 != 0` hold for these parameters. The code is a fixed-fixture checker, not an unrestricted validator for arbitrary q, dimensions, JSON schemas or negative exponents. Reducible quotient rings still admit the q-power endomorphism and the computed five-term sum; identifying that sum with the conventional extension-field trace requires the field assumptions. The prior executable replay independently checked modulus irreducibility by its finite-field criterion and the degree-five q-power condition. This review replayed that executable evidence. It does not provide a Lean irreducibility theorem or a canonical field isomorphism.

I inspected `QuotientFrobeniusMap.lean`, `QuotientKernelTransport.lean` and their targets. Their stated objects are `AdjoinRoot` quotient algebras over `ZMod q`, with power-basis representations and transported matrix controls. Their comments and target notes expressly exclude modulus irreducibility and historical execution custody. No fresh Lean build, axiom audit or native theorem verification was run, as this task prohibited heavy Lean work. Those modules are contextual source-fidelity inputs, not new machine-verified proof claims in this packet.

The specification's C5 paragraph explicitly calls for direct repeated q-th powering, comparison with the independent matrix polynomial, and additional factor-kernel/direct-sum/fixed-line checks. The archived `implementation.py` function `c5_trace_identity` instead builds `T` as a sum of powers of M and compares it with another construction of the same sum. The archived `command.txt` invokes relative `implementation.py`; that driver prepends its directory and `work/` to `sys.path` before importing core and lattice. The run manifest explicitly says its hashes describe final post-bugfix content. These records do not authenticate the originally loaded bytes. The successor repairs the missing direct mathematical comparison on the archived parameters only. It cannot retroactively establish historical C5, C8, full experiment success, performance, ECDLP cost, or a historical Sage refinement.

## Sources and method boundary

The bound repository sources above are primary evidence; `review_attestation.yaml` enumerates every substantive actual read, including sources read only for hashes and the selected historical source excerpts. I consulted the official [Python optimization documentation](https://docs.python.org/3/using/cmdline.html#cmdoption-O) for the assertion-removal behavior and the official [Sage finite-field trace documentation](https://doc.sagemath.org/html/en/reference/finite_rings/sage/rings/finite_rings/element_base.html#sage.rings.finite_rings.element_base.FinitePolyExtElement.trace) for its sum-of-conjugates definition. These documentation reads clarify methods; they do not authenticate this historical Sage invocation. No novelty claim is made.

All repository writes are confined to this J1 directory. Temporary malformed fixtures were created and removed under `/var/tmp`. No scientific trial, Sage process, Lean build, EKS job, PR, commit, sibling read, or official status transition was performed. No performance graph changes follow from this review. The coordinator owns composition, archival publication, and any update to the existing problem record. The historical obstruction remains the one already recorded in `problems/frob-c5-factor-kernel-and-model-bridge.md`.

## Reproduce and retain

Run from the review worktree, with a fresh output directory inside J1 or scratch:

```sh
python3 -B research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j1/review_checks.py --root . --out /var/tmp/frob-c5-j1-reproduction
```

`raw/commands.json` gives the exact commands used here. The initial wrapper invocation used `--out research/frob_c5_direct_trace_review_20261027/reports/TASK-20261027-fc5-j1/raw`. `raw/input_hashes.json`, `raw/prior_source_bindings.json`, both direct JSON replays and all control logs support the verdict. `SHA256SUMS` seals the report, attestation, checker and raw artifacts. The seal is an integrity manifest, not a cryptographic identity signature. After sealing, no sibling or coordinator machine artifact will be read by this reviewer.
