# Endosweep Lean targets: independent semantic-fidelity review (2026-10-16)

## Purpose

A Lean proof that builds and passes the axiom audit is `machine_verified`, but
[`docs/formal-research-lane.md`](../../docs/formal-research-lane.md)
("Verification contract") keeps it `INCONCLUSIVE` until a separate reviewer
confirms *semantic fidelity*: that the Lean proposition says what the target
spec's `claim` says, with no vacuous statement, weakened quantifier, hidden
assumption or impossible premise. This directory records that review for the
49 endosweep targets in `formal/targets/endosweep-*.yaml` (files under
`formal/CryptoResearch/Endosweep/`), and the wording and statement fixes made
in response.

## Method

Three reviewers, R1, R2 and R3, each took a disjoint share of the targets.
None of them wrote the proofs. Each worked read-only against the checkout and
wrote one YAML file:

| Reviewer | Targets | Lean files |
|---|---|---|
| R1 ([`R1.yaml`](R1.yaml)) | 13 | Discriminant, NistCertificates, Koblitz, RMGoldenNorm |
| R2 ([`R2.yaml`](R2.yaml)) | 17 | XOnlyConjugate, LambdaCoordinates, BinaryGLS, Pippenger |
| R3 ([`R3.yaml`](R3.yaml)) | 19 | SubgroupIndex, ChainEigen, AlphaAdic, FrobeniusSplit, Blinding |

For every target the reviewer recorded five checks:

* **a. statement**: the Lean statement against the spec claim, clause by
  clause: objects, quantifiers, direction of the conclusion.
* **b. hypotheses**: every hypothesis is in the claim (none hidden), and
  the hypotheses are jointly satisfiable.
* **c. definitions**: every self-defined notion is the textbook one and
  matches the harness Python it stands for.
* **d. data**: every numeric constant matches the committed JSON.
* **e. scope**: the spec notes and the source README do not claim more than
  the theorem proves.

In support of these checks:

* **Satisfiability witnesses.** Each hypothesis set was discharged on a
  concrete instance in a scratch Lean file that imports the built modules.
  Examples: D = −15, −20, −8 for `isFundamental_of_primes`; GF(4) as a core
  `Lean.Grind.Field` for the λ-coordinate and GLS theorems; blinding.py's
  secp256k1 basis for `babai_unreduced_erases`. Closed `decide` statements
  need no witness.
* **Data spot-checks.** Lean constants were compared with nist.json,
  factorizations.jsonl, FIPS 186-4 Koblitz orders, xonly.json, msm.json
  (all 204 rows), subgroup.json, arkworks `curves.json`,
  chains.constants.json (all 22 rows) and alphaadic.json. Large primes were
  checked with PARI `isprime`, and B-571's cofactor by trial division below
  10^7. One-digit negative controls (`neg_nist.lean`, `neg_kob.lean`) fail in
  the kernel.
* **Numeric cross-checks against the harness Python.** Lean `#eval` and
  independent Python transcriptions were compared with quadorder.py,
  binary.py, lambdacoord.py, gls.py, msm.py, subgroup.py, alphaadic.py,
  frobenius.py, blinding.py and lattice.py on random and edge-case inputs.
* **Axioms.** `#print axioms` for every target returns only `propext`,
  `Classical.choice` and `Quot.sound`, or none. There is no `sorryAx`, no
  `ofReduceBool` and no `native_decide`.

The reviewers' small text evidence (`.lean`, `.py` and `.out` files, each
under 200 KB) is copied into [`evidence/R1`](evidence/R1),
[`evidence/R2`](evidence/R2) and [`evidence/R3`](evidence/R3). The comment
header of each YAML says what each file does. The files are kept as written,
so paths inside them point at the reviewers' scratch directory.
[`SHA256SUMS`](SHA256SUMS) covers the three YAML files.

## Results

| Rev. | Target | Theorem (`CryptoResearch.Endosweep.…`) | Verdict | Note |
|---|---|---|---|---|
| R1 | `endosweep-disc-fundamental-from-primes` | `Discriminant.isFundamental_of_primes` | PASS | Faithful; all three branches instantiated (D = −15, −20, −8). |
| R1 | `endosweep-disc-min-nonscalar-degree` | `Discriminant.minNonscalarDegree_isLeast` | PASS | Definitions are literally quadorder.py's; brute-force minimum agrees down to D = −2000. |
| R1 | `endosweep-disc-squarefree-part-bound` | `Discriminant.prod_mul_bound_le_of_eq_mul_sq` | PASS | Hypotheses exactly the claim's; stronger than needed (every factorisation). |
| R1 | `endosweep-nist-b571-bound` | `NistCertificates.B571.abs_DK_lower_bound` | PASS | Both hypotheses true (PARI, trial division); 2^164/2^162 are in `bound_values`; "composite" is PARI-only. |
| R1 | `endosweep-nist-exact-discriminants` | `NistCertificates.exact_discriminants` | PASS_WITH_NOTES | D_K construction was proved only in `factored_holds`, not stated in the named theorem. |
| R1 | `endosweep-nist-finding3-bounds` | `NistCertificates.finding3_bounds` | PASS | Faithful as disclosed; deg link via `exact_discriminants`. |
| R1 | `endosweep-nist-koblitz-discriminants` | `NistCertificates.koblitz_discriminants` | PASS | Unconditional; q = 2^m and t, f match nist.json. |
| R1 | `endosweep-koblitz-curve-certificates` | `Koblitz.koblitz_certificates` | PASS | n, h match FIPS 186-4; negative control fails in the kernel. |
| R1 | `endosweep-koblitz-delta-norm` | `Koblitz.norm_delta` | PASS | Faithful; N(τ − 1) = 3 − μ is the companion `norm_tau_sub_one`. |
| R1 | `endosweep-koblitz-lucas-norm` | `Koblitz.norm_one_sub_tau_pow` | PASS | Faithful for every μ. |
| R1 | `endosweep-koblitz-min-norm` | `Koblitz.min_norm_nonscalar` | PASS | Faithful. |
| R1 | `endosweep-koblitz-ztau-order` | `Koblitz.ztau_iso_order_neg_seven` | PASS | Faithful; "ring isomorphism" rests on visible Z-linearity of `toOmega`. |
| R1 | `endosweep-rm-golden-norm-2adic` | `RMGoldenNorm.norm_eq_four_pow_mul_odd` | PASS | Faithful; the induction bound n is instantiated at |a| + |b|. |
| R2 | `endosweep-xonly-conjugate-difference` | `XOnlyConjugate.xonly_difference_eq_conj` | PASS | Faithful; witness over Int. |
| R2 | `endosweep-xonly-conjugate-eigenvalue` | `XOnlyConjugate.conj_eigenvalue` | PASS | Faithful; second sentence is `eigen_conj_mod`. |
| R2 | `endosweep-xonly-odd-trace-needed` | `XOnlyConjugate.QuadOrder.trace_one_exists_iff_D_odd` | PASS_WITH_NOTES | Order-theoretic part faithful; the curve step "x((β−1)P) = x(β̄P) requires β + β̄ = 1" is informal and was not labelled so. |
| R2 | `endosweep-xonly-omega-norms` | `XOnlyConjugate.QuadOrder.omega_norms` | PASS | All four norms match xonly.json. |
| R2 | `endosweep-lambda-add` | `LambdaCoordinates.add_correct` | PASS | Operation-by-operation match with lambdacoord.py; 160/160 numeric. |
| R2 | `endosweep-lambda-curve-equation` | `LambdaCoordinates.curve_equation_iff` | PASS | Faithful. |
| R2 | `endosweep-lambda-dbl-add` | `LambdaCoordinates.dbl_add_correct` | PASS | Hypotheses are the code's raise/fallback conditions; 160/160 numeric. |
| R2 | `endosweep-lambda-dbl-alt` | `LambdaCoordinates.dbl_alt_eq_dbl_main` | PASS | Stronger than claimed (equality of triples). |
| R2 | `endosweep-lambda-dbl-theorem1` | `LambdaCoordinates.dbl_main_correct` | PASS | Faithful; no curve hypothesis, as claimed. |
| R2 | `endosweep-lambda-madd` | `LambdaCoordinates.madd_correct` | PASS | Faithful; `madd_eq_add` links it to `add`. |
| R2 | `endosweep-gls-psi-endomorphism` | `BinaryGLS.psi_add` | PASS | Faithful; other clauses are cited supporting theorems. |
| R2 | `endosweep-gls-psi-from-twist` | `BinaryGLS.psi_eq_conj_by_twist` | PASS_WITH_NOTES | Lean is correct; for gls.py's a = 0, m = 127 the twist conjugate is −ψ, so the spec's existence note was imprecise. |
| R2 | `endosweep-gls-psi-squared` | `BinaryGLS.psi_psi` | PASS | More general than claimed. |
| R2 | `endosweep-msm-bit-conservation` | `Pippenger.bit_conservation` | PASS | Trivial identity, as claimed. |
| R2 | `endosweep-msm-break-even` | `Pippenger.glv_wins_iff` | PASS | All 204 msm.json rows agree (0 mismatches). |
| R2 | `endosweep-msm-ideal-cstar` | `Pippenger.ideal_glv_wins_iff` | PASS_WITH_NOTES | "Exceeds" is strict only for D, C > 0 (not stated); "aggregation-only" is the model's term, not b·A/(c(c+1)). |
| R2 | `endosweep-msm-window-slots` | `Pippenger.window_slots` | PASS | Faithful; 2h/h scope explicit. |
| R3 | `endosweep-subgroup-index-gcd-minors` | `SubgroupIndex.index_eq_minorGcd` | PASS | Faithful general statement. |
| R3 | `endosweep-subgroup-ideal-index` | `SubgroupIndex.ideal_index_eq_elementIndex` | PASS | Lean = Python element_index on 36 random cases. |
| R3 | `endosweep-subgroup-cp6-782-certificate` | `SubgroupIndex.cp6_782_certificate` | PASS | All 17 conjuncts match the committed JSON. |
| R3 | `endosweep-subgroup-bls12-381-control` | `SubgroupIndex.bls12_381_control` | PASS | Faithful; one redundant conjunct. |
| R3 | `endosweep-chain-cp6-782-certificate` | `ChainEigen.cp6_782_chain_certificate` | PASS | All 18 rows match curves.json; signs re-derived. |
| R3 | `endosweep-chain-cryptopro-b-certificate` | `ChainEigen.cryptopro_b_chain_certificate` | PASS_WITH_NOTES | Arithmetic of 22 orderings faithful; the claim's "381 of 381 verified on points" quote suggested more. |
| R3 | `endosweep-chain-glv-basis` | `ChainEigen.glv_basis_spans_relation_lattice` | PASS | Faithful; both directions. |
| R3 | `endosweep-alphaadic-int-rule-1plus4w-cycle` | `AlphaAdic.cp6_782_int_rule_1plus4w_cycle` | PASS | Faithful; digit is the unique balanced representative. |
| R3 | `endosweep-alphaadic-int-rule-4plusw-cp6` | `AlphaAdic.cp6_782_int_rule_terminates` | PASS | Lean digit/step = alphaadic.py on 50 inputs. |
| R3 | `endosweep-alphaadic-int-rule-4plusw` | `AlphaAdic.cryptoProB_int_rule_terminates` | PASS | Faithful; disk data match alphaadic.json. |
| R3 | `endosweep-alphaadic-norm-decrease` | `AlphaAdic.norm_decrease` | PASS | Faithful square-root-free form. |
| R3 | `endosweep-alphaadic-termination-from-disk` | `AlphaAdic.terminates_of_disk` | PASS | Faithful; hypotheses discharged for two real rules. |
| R3 | `endosweep-frob-f4-trace` | `FrobeniusSplit.order_F4_eq` | PASS_WITH_NOTES | Claim needs three theorems; spec listed only `order_F4_eq`. |
| R3 | `endosweep-frob-lucas-double` | `FrobeniusSplit.order_double` | PASS | Faithful. |
| R3 | `endosweep-frob-q4-small-m` | `FrobeniusSplit.q4_small_m` | PASS | Faithful; m = 3 alone shows the bound is needed. |
| R3 | `endosweep-frob-q4-split` | `FrobeniusSplit.q4_split` | PASS_WITH_NOTES | Theorem faithful; spec first sentence and README Finding 4 headline were unqualified (false at m = 2, 3). |
| R3 | `endosweep-blinding-classical-erased` | `Blinding.babai_unreduced_erases` | PASS_WITH_NOTES | Faithful for `decompose_unreduced`; the 40 000 checks compare against lattice.py's `decompose`, not linked in Lean. |
| R3 | `endosweep-blinding-mod-n` | `Blinding.decompose_mod_erases` | PASS | Near-trivial; content is the code-shape premise, confirmed. |
| R3 | `endosweep-blinding-reconstruction` | `Blinding.blind_reconstructs` | PASS | Faithful for all r. |

**Total: 41 PASS, 8 PASS_WITH_NOTES, 0 FAIL (49 targets).**

No FAIL. Every PASS_WITH_NOTES concerns wording or the attribution of a claim
part to a theorem. None reports a wrong proof, a vacuous hypothesis or a data
mismatch. The minor notes on PASS entries are informational, and those the
specs could act on are applied below.

## Fixes applied in this PR

| Note (reviewer, target) | Change |
|---|---|
| R1 PASS_WITH_NOTES, `nist-exact-discriminants`: the D_K construction was not in the named theorem | `NistCertificates.exact_discriminants` now states two more conjuncts: the odd-exponent filter of the certificate equals `oddPrimes`, and `(D_K = −core ∧ D_K % 4 = 1) ∨ (D_K = −4·core ∧ −core % 4 ∈ {2, 3})` with `core = oddPrimes.prod`, as `nist.exact_discriminant` builds it. Both are taken from `factored_holds`, and the docstring is updated. The data blocks are generated, so the template `research/endosweep_nist_20261006/lean/NistCertificates.lean.in` carries the same edit. The generator, run against the pinned std-curves checkout (`77fe6e35…`), reproduces the committed `NistCertificates.lean` and `Koblitz.lean` byte for byte, both before and after the edit. The spec notes record the conjunct. |
| R1 minor, `nist-b571-bound` | The spec notes cite `B571.bound_values` for the 2^164 and 2^162 comparisons, and say that "C composite" comes from PARI, is not proved in Lean, and is not needed by the bound. |
| R1 minor, `koblitz-delta-norm` | The spec notes cite `Koblitz.norm_tau_sub_one` for N(τ − 1) = 3 − μ. |
| R1 minor, `rm-golden-norm-2adic` | The spec notes say that the induction bound n is instantiated at \|a\| + \|b\| (as `norm_eq_four_pow_mul_odd'` does). |
| R2 PASS_WITH_NOTES, `xonly-odd-trace-needed` | The spec notes and the xonly README Lean item 3 say that the step "x((β−1)P) = x(β̄P) requires β + β̄ = 1" rests on curve facts that are not formalised: x(P′) = x(P″) ⇒ P′ = ±P″, and the lift to β − 1 = ±β̄ in End(E). Lean proves only the order-theoretic part. |
| R2 PASS_WITH_NOTES, `gls-psi-from-twist` | The spec notes and the lambda README Lean section state the following. An s with s² + s = a + u always exists in F_{q⁴}. For a ∈ F₂ and odd m, s + s^q = a + u + (m−1)/2 mod 2. R2's `twist_check.py` confirms this for m = 1, 3, 5 only; m = 127 follows from the formula and was not run. So for gls.py's a = 0, m = 127, the twist conjugate is −ψ, and ψ = φπφ⁻¹ holds for a = 1. Both square to −1, so no result changes. The lambda README's results text does not itself state ψ = φπφ⁻¹ (only gls.py's docstring does), so no correction note was needed there. |
| R2 PASS_WITH_NOTES, `msm-ideal-cstar` | The spec claim and notes say that the break-even strictly exceeds the aggregation-only saving only for positive b, c, N and D or C > 0, and is at least that saving otherwise. They also say that "aggregation-only" means the model's (b/(2c))·2^c·R/N, not b·A/(c(c+1)). The msm README Lean section gets the same clarification. |
| R3 PASS_WITH_NOTES, `chain-cryptopro-b-certificate` | The "381 of 381 verified …" quotation in the claim is relabelled as harness context that the theorem does not certify. The theorem certifies the arithmetic of the 22 frozen orderings. |
| R3 PASS_WITH_NOTES, `frob-f4-trace` | The spec notes list the claim's three parts with `F4_trace`, `F4_trace_eq_neg_three_iff` and `order_F4_eq`. |
| R3 PASS_WITH_NOTES, `frob-q4-split` | The spec claim's first sentence is qualified to "every odd m ≥ 5 (every prime m in 67–199)", with the m = 2, 3 exceptions. A dated correction note follows the Finding 4 headline in `research/endosweep_frob_blinding_20261008/README.md`, and the original text is kept. |
| R3 PASS_WITH_NOTES, `blinding-classical-erased` | The spec notes say what the 40 000 checks compare: `decompose_unreduced(k + rn)` against lattice.py `decompose(k)`, which uses half-to-even rounding on k mod n. Lean does not link the two routines. They can differ only at exact half-integer ties, which are impossible here because each den_i divides n and n is odd. R3 found 0 mismatches in 8 000 samples. |

Not acted on (informational, no spec change needed): R1's optional
standalone restatement of `finding3_bounds` with `minNonscalarDegree`, and
R1's note on the "ring isomorphism" wording for `ztau_iso_order_neg_seven`.
Also R2's note that "b mod c" quantisation is loose for `msm-window-slots`,
R3's redundant conjunct in `bls12_381_control`, and R3's optional rewording
of `q4_small_m`. The informal "ψ = φ∘π∘φ⁻¹" sentence in the docstring of
`harness/endosweep/gls.py` (lines 8–10) is the R2 point above; the harness
code is left unchanged in this PR.

## Status

* **Machine-verified locally.** All 13 Endosweep Lean files compile with
  `lean -o` in dependency order (exit 0, no errors), on Lean 4.35.0-rc1.
  Ten use core Lean only. AlphaAdic, ChainEigen and SubgroupIndex import
  `Mathlib.Tactic.Ring` from the existing local dependency build; Mathlib was
  neither downloaded nor built. The reviewers' axiom audit is clean. The one Lean file this PR
  changes, `NistCertificates.lean`, was recompiled after `Discriminant.lean`,
  and `#print axioms exact_discriminants` gives `propext`,
  `Classical.choice` and `Quot.sound`. No `sorry`, `admit`, `axiom`,
  `unsafe` or `native_decide`.
* **Semantic review: PASS** (41 PASS, 8 PASS_WITH_NOTES, 0 FAIL). Every note
  is addressed above.
* **No promotion.** Ledger and claim promotion is reserved to the
  Coordinator and was NOT done here. Nothing under `ledger/` or `knowledge/`
  is changed.
* **CI.** The formal-workspace CI gate had not run on `main` when this was
  written (GitHub Actions idle since 2026-10-12). The local build is the
  only build evidence so far.
