# J2 independent source/type fidelity review

Task: `TASK-20261030-2fb4bd`; archival owner: `TASK-20261030-92733b`; policy: `review-adversarial`.

**Scoped verdict: holds.** Each of the seven mathematical claims in the supplied `CLAIMS.md` matches its Lean declaration and actual fresh printed elaborated type. No unjustified mathematical hypothesis was added. The coefficient and probe orders are correct. Claims 1–3 are over arbitrary commutative rings; claims 4, 5 and 7 explicitly assume nontriviality; claim 6 is the concrete zero ring `ZMod 1`. These results establish the stated ring-expression claims. They do not establish executable Rust correctness, representation invariants, byte/fingerprint injectivity, or STARK security.

## Admission, independence and method

I read `ADMISSION.json` and `HANDOFF.json` first and confined all subsequent input reads to `/workspace/pr-integration/review-2681-inputs/J2`. The published input and reservation commits are recorded by admission as `77b2f0052d648f3753f788aa73e21fddc8d0f70b` and `fab6ed6e5b58ac68a60f7b3f756494714a4add5e`; I did not inspect Git to authenticate or reconstruct them. I read no sibling reports, other reviewers' messages, old reviewer reports/responses, producer repository, PR discussions, memories, or historical Git material. I did not follow the `J2-response.md` or other missing producer links. The older `native-40825630139` packet was not opened; its filenames and hashes occur in the administrative admission only. Historical status prose present in `CLAIMS.md` was not treated as a prior verdict or current execution status.

This was a fresh task session without parent-turn history. I used source reading, text search, JSON parsing and SHA-256 comparison. No subagents, scientific trials, solver runs, benchmarks, Lean commands, Rust tests, builds, network fetches, commits or official scientific transitions were performed. The actual observed native evidence was the supplied fresh hosted-execution packet, not a reviewer-run Lean execution.

The runtime amendment was conveyed in the task and admission/handoff; I did not open its external path. Requested policy/effort were `review-adversarial` / `xhigh`. The permitted native default-model fallback was used: `fallback_used: true`, `model_verified: false`. Serving provider/model, tier, context limit, output limit and effective reasoning effort are unverified. No Opus execution, CLI probe, opaque execution identifier or independently verified serving identity is claimed.

## Exact source binding and current machine evidence

All twelve mathematical/evidence files actually used have SHA-256 values matching their entries in `ADMISSION.json`. Complete actual input paths, hashes and read scopes, including the two administrative inputs, are in `attestation.json` and the appendix below.

The Rust file is bound to the supplied SHA-256 `3bfe1facc87a2e522ffb69984cee5c18db71d1a216e72e521a5c694142b0e223`; its claimed upstream commit/blob identity was not checked outside the view. I inspected its actual source, rather than relying solely on `source-exhibit.txt`: coefficient storage/constructor/evaluation at lines 176–204; the typed AIR at 206–220; fingerprint implementation/comment at 342–367; and the quadratic control at 954–970. I also inspected the module's assumptions/exclusions, imports, composition call site, transcript prefix and relevant test context. The exhibit agrees with those relevant source passages.

The fresh packet records hosted run `41109712394`, job `124248764439`, artifact `13004731447`, producer head `11d30c7a863816435b3098087c1264edc5bd54b2`, native/synthetic source commit `6170b8a9bd63e546eb68234e73a3ae89aaed4251`, and run interval 2026-10-30 18:46:24–19:12:14 UTC. These are inspected packet metadata, not executions or remote identities independently observed by this reviewer. Artifact metadata and binding agree on archive digest `ad53aa7463d5c44fc4ab3907cd3837dc82224f81e69d9de111acabab212f8082` and size 702537; archive bytes were not supplied or fetched, so that archive digest was not recomputed.

The current receipt's theorem SHA-256 is `3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d`, exactly matching the reviewed module. Target, toolchain and manifest digest bindings also match. The workspace binding additionally matches the supplied `lakefile.toml`. The toolchain is `leanprover/lean4:v4.35.0-rc1`; the receipt reports Lean commit `86c6347c75e39ec18c40e25ed2143b71a6e04a0a`; Mathlib is manifest-pinned at `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`. The `rev = "master"` input in the lakefile does not replace the exact manifest pin. Dependencies, verifier implementation, workflow and kernel executable were not available for independent examination within this view.

`fresh-native-41109712394/types-and-axioms.txt` is byte-for-byte identical to the decoded receipt `build_log`. It includes the successful project build and an explicit named-module build, ending with `Build completed successfully (1142 jobs)`. The module's seven full type blocks occur twice and are pairwise text-identical. I inspected the complete second set, log lines 618–1154, along with controls and axiom prints through 1170. The log says `Replayed`; I do not describe that as a forced re-elaboration of every dependency or a reviewer rerun. It is current source-bound successful hosted execution evidence.

The receipt's registered target is only `three_probe_extensionality` (claim 3), with `status: machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, no forbidden constructs and no infrastructure failure. It explicitly leaves semantic review pending. The other six declarations have successful module-build, full type-print and axiom-print evidence, not six additional separately registered target receipts. All seven axiom prints are present: claims 1–5 and 7 depend on `[propext]`; claim 6 on `[propext, Quot.sound]`. These are logical foundations reported by Lean, not added ring hypotheses. No custom axiom or assumed conclusion occurs in the supplied Lean source.

Both `#check_failure` controls show the specific expected inability to synthesize `Nontrivial (ZMod 1)` at Lean lines 99 and 103. Their surrounding successful build matters: the diagnostic is expected informational control output, not a failing build. The controls test rejection of these applications in the zero ring. They do not themselves prove a universal metatheorem about arbitrary changes to the source.

## Expression, tuple and quantifier checks

Write `E(a,b,c,x,y) = (a*x + b*y) + c`, and `Eabc(p,q)` for that expression at a designated pair. Lean line 13 uses this exact operand and addition order. Rust's nested `fr_add(fr_add(fr_mul(self.previous, previous), fr_mul(self.next, next)), self.constant)` has the corresponding structural order: `a = self.previous`, `b = self.next`, `c = self.constant`, `x = previous`, `y = next`. This establishes the syntactic modeling correspondence; it does not prove the imported helpers implement the ring operations.

The fresh prints expose `Prod R (Prod R R)` and `Prod.mk a (Prod.mk b c)`. Thus `(a,b,c)` means `(a,(b,c))`, in previous/next/constant order. Recovery first subtracts `E00` from `E10`, then from `E01`, then returns `E00`: its components are `(a,b,c)`, not `(c,a,b)` despite the Rust test computing the constant first. `Prod.fst`, `.2.1` and `.2.2` in extensionality select `a`, `b` and `c` correctly.

The generic printed types use arbitrary universe `u_2`, `{R : Type u_2}` and `[inst : CommRing R]`. There is no hidden universe restriction to a finite field, and no `Field`, primality, characteristic, finiteness, decidable equality, domain or nontriviality premise in claims 1–3. The concrete zero-ring declaration uses `ZMod 1 : Type 0` and its actual `ZMod.commRing 1` instance; unused section variables `{R}` and `[CommRing R]` are absent from its elaborated type.

All expanded subtraction, multiplication, zero and one instances in the type prints are derived from the displayed `CommRing` instance (or `ZMod.commRing 1`). In particular, the `CommRing.toRing`, `CommRing.toCommSemiring`, `CommSemiring.toSemiring`, ring/additive hierarchy projections, `instMulZeroClassOfSemiring`, `Zero.toOfNat0`, `One.toOfNat1`, `instHSub`, `instHMul`, and their displayed operation projections introduce no independent typeclass assumptions. Equality, inequality, products, `And` and `Not` are logical/type constructors, not hypotheses. The printed `Eq.{u_2+1}` universe annotation does not add a mathematical condition.

## Hypothesis-delta tables

In these tables, **implied** means explicitly required by the source mathematical claim or definition; **scoping** identifies universal variables, concrete witness choices or conditions inside the asserted conclusion; **unjustified** would identify a new restriction not supported by the source. No entry is unjustified. Every free declaration binder, instance, fixed coefficient/probe choice and side condition is accounted for below. Derived operation instances are accounted for in the preceding paragraph. Proof-local assumptions introduced while proving a negation are distinguished from exported premises.

### Supporting definition: `evaluate` (Lean 13)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Carrier for arbitrary ring expressions; no finite-field specialization | scoping |
| `[CommRing R]` | Exactly the common premise in `CLAIMS.md` 29 | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | Previous, next and constant coefficients respectively | scoping |
| `(x : R)`, `(y : R)` | Previous/next input values, arbitrary | scoping |
| Body `(a*x + b*y) + c`; standard ring operations | Exactly the source definition and the Rust expression structure | implied |

Added assumptions: **none**. There is no separate `#check evaluate`; the definition was read directly and every printed theorem occurrence supplies this same `R`/ring instance.

### Claim 1: `recover_coefficients` (Lean 16–20; native log 618–688)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Arbitrary carrier, not restricted to a particular field | scoping |
| `[CommRing R]` | The common ring premise of claim 1 | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | All coefficient triples, universally bound | scoping |
| Fixed inputs `(1,0)`, `(0,1)`, `(0,0)` | Exactly the recovery evaluations in claim 1 | scoping |
| Ordered tuple `(E10-E00, E01-E00, E00) = (a,(b,c))` | Exactly the asserted conclusion; subtraction comes from the ring | implied |
| Additional equality/inequality or nonzero premise | None in source or elaborated declaration | scoping: absent |

Added assumptions: **none**. Simplification yields `E00=c`, `E10=a+c`, `E01=b+c`; additive cancellation needs no division or field assumption.

### Claim 2: `coefficients_eq_of_probes` (Lean 22–35; native log 689–761)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Both expressions live in one arbitrary carrier | scoping |
| `[CommRing R]` | The stated common ring premise | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | Arbitrary first coefficients | scoping |
| `(a' : R)`, `(b' : R)`, `(c' : R)` | Arbitrary second coefficients in the same ring | scoping |
| `h00 : Eabc(0,0) = Ea'b'c'(0,0)` | First of exactly the three source probe equalities | implied |
| `h10 : Eabc(1,0) = Ea'b'c'(1,0)` | Second designated probe equality | implied |
| `h01 : Eabc(0,1) = Ea'b'c'(0,1)` | Third designated probe equality | implied |
| Fixed pairs `(0,0)`, `(1,0)`, `(0,1)`; conclusion `(a,(b,c))=(a',(b',c'))` | Correct probe and coefficient order; curried implications in the print express the three supplied hypotheses | scoping |
| Additional field/nontriviality/characteristic/finite premise | None | scoping: absent |

Added assumptions: **none**. The proof recovers each triple from the same probe data. It does not assume coefficient equality as a premise.

### Claim 3: `three_probe_extensionality` (Lean 38–48; native log 762–832)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Arbitrary ring carrier | scoping |
| `[CommRing R]` | Exactly the common ring premise and registered target claim | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | Universally quantified first coefficients | scoping |
| `(a' : R)`, `(b' : R)`, `(c' : R)` | Universally quantified second coefficients | scoping |
| `h00 : Eabc(0,0) = Ea'b'c'(0,0)` | Exactly the first source premise | implied |
| `h10 : Eabc(1,0) = Ea'b'c'(1,0)` | Exactly the second source premise | implied |
| `h01 : Eabc(0,1) = Ea'b'c'(0,1)` | Exactly the third source premise | implied |
| `∀ (x : R) (y : R), Eabc(x,y)=Ea'b'c'(x,y)` | Universal conclusion over all pairs, not only the sampled pairs | scoping |
| Fixed probe order; extra side conditions | `(0,0),(1,0),(0,1)` as in source; no extra conditions | scoping |

Added assumptions: **none**. Coefficient equality is obtained from claim 2, then substituted. The function equality is pointwise and is not a theorem about Rust object identity or byte strings.

### Claim 4: `multiplication_not_affine` (Lean 51–58; native log 833–842)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Arbitrary carrier | scoping |
| `[CommRing R]` | The stated ring premise | implied |
| `[Nontrivial R]` | Explicitly required by claim 4; used as `0 ≠ 1` | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | Every coefficient triple | scoping |
| `¬ (∀ (x : R) (y : R), Eabc(x,y)=x*y)` | Exact global nonagreement; the quantified agreement is inside the negation | scoping |
| Proof-only pairs `(0,0),(1,0),(0,1),(1,1)` | Used internally; not an exported extra premise or the statement of a finite-point result | scoping |
| Local `h` introduced by `intro h` | Temporary assumption of the negand to derive contradiction; not an assumed conclusion exported in the theorem | scoping |

Added assumptions: **none**. Nontriviality is necessary, as claim 6 shows. This declaration alone does not specify four obstruction points in its conclusion.

### Claim 5: `two_probes_insufficient` (Lean 74–78; native log 843–1004)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Any carrier | scoping |
| `[CommRing R]` | The common ring premise | implied |
| `[Nontrivial R]` | Explicitly required by claim 5; needed for the final inequality | implied |
| First fixed triple `(0,0,0)` | Exactly the zero transition witness in claim 5 | scoping |
| Second fixed triple `(0,1,0)` | Exactly the next-coordinate transition witness in claim 5 | scoping |
| Agreement at `(0,0)` and `(1,0)` | The first two conjuncts, asserted conclusions, not assumed hypotheses | scoping |
| Disagreement at `(0,1)` | The final conjunct is `Ne`, not equality or an omitted third premise | scoping |
| Free coefficients, arbitrary input pairs, additional premises | None; these witnesses and pairs are concrete | scoping: absent |

Added assumptions: **none**. The result reduces to `0=0 ∧ 0=0 ∧ 0≠1`. It concerns omission of the designated third probe, not a blanket theorem that every possible two-point probe scheme fails.

### Claim 6: `zero_ring_product_control` (Lean 81–83; native log 1005–1040)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Fixed carrier `ZMod 1 : Type 0` | Exactly the zero-ring specialization in claim 6 | scoping |
| Concrete `ZMod.commRing 1` and all derived operation instances | Supplied by the actual standard ring instance, not a custom assumed ring | implied |
| `(x : ZMod 1)`, `(y : ZMod 1)` | Every pair in this concrete ring | scoping |
| Fixed coefficients `(0,0,0)` | Exactly the zero affine transition | scoping |
| Conclusion `E(0,0,0,x,y)=x*y` | Global agreement in this ring; no finite-probe restriction | implied |
| Generic `{R}`, generic `[CommRing R]`, `[Nontrivial (ZMod 1)]`, prime-modulus premise | All absent from the actual printed type | scoping: absent |

Added assumptions: **none**. `Subsingleton.elim` proves the equation because this ring has one element. That is a real inhabited boundary model, not a proof from impossible nontriviality assumptions.

### Claim 7: `multiplication_not_affine_on_four_probes` (Lean 61–71; native log 1041–1154)

| Binder, instance or fixed data | Source comparison | Mark |
|---|---|---|
| Universe `u`; `{R : Type u}` | Arbitrary carrier | scoping |
| `[CommRing R]` | The stated common ring premise | implied |
| `[Nontrivial R]` | Explicit in claim 7; excludes the countermodel of claim 6 | implied |
| `(a : R)`, `(b : R)`, `(c : R)` | Every coefficient triple | scoping |
| First negated conjunct `Eabc(0,0)=0*0` | Exactly the first finite-point agreement | scoping |
| Second negated conjunct `Eabc(1,0)=1*0` | Exactly the second finite-point agreement | scoping |
| Third negated conjunct `Eabc(0,1)=0*1` | Exactly the third finite-point agreement | scoping |
| Fourth negated conjunct `Eabc(1,1)=1*1` | Exactly the fourth finite-point agreement | scoping |
| Outer `Not (And P00 (And P10 (And P01 P11)))` | Negates the conjunction at those four pairs; does not substitute an all-input quantifier or assume one failed equality | implied |
| Proof-local `h`, projections `h.1`, `h.2.1`, `h.2.2.1`, `h.2.2.2` | Temporary assumed conjunction for contradiction, in the correct order | scoping |

Added assumptions: **none**. The first three conjuncts force `c=a=b=0`; the fourth forces `0=1`, contradicted by nontriviality. The universal quantification over coefficients matches the Rust comment, whereas the concrete Rust test constructs only the candidate recovered from multiplication's first three values.

## Satisfiability and per-claim disposition

Claims 1–3 have no empty-model trick: they apply also to the zero ring. For claims 2–3 the probe premises are simultaneously satisfiable by identical coefficient triples in any commutative ring. Claims 4, 5 and 7 have ordinary models such as the integers; their `Nontrivial` premise is consistent and does not exclude characteristic two or finite rings. With `0≠1`, the four pairs remain the intended four distinct pairs. Claim 6 supplies an inhabited subsingleton ring with no contradictory premise. No declaration quantifies over a vacant coefficient set or assumes the intended conclusion.

| Claim / declaration | Current machine-evidence status | Fidelity to exact Rust source and source claim | Scoped J2 outcome |
|---|---|---|---|
| 1 / `recover_coefficients` | Fresh bound module build; complete matching type print; `[propext]`; no separate target receipt | Exact `CLAIMS.md` recovery identity. Matches the previous/next/constant recovery order in the Rust control and underlies the first-three-values comment. Ring-level only. | **holds**, no added assumption |
| 2 / `coefficients_eq_of_probes` | Fresh bound module build; complete matching type print; `[propext]`; no separate target receipt | Exact uniqueness claim for the three listed probes. Makes the coefficient-determination content of Rust 342–347 precise. Does not identify raw BigUint structs without refinement/canonicality. | **holds**, no added assumption |
| 3 / `three_probe_extensionality` | Fresh bound module/type/axiom evidence plus named target `machine_verified` and target axiom audit; `[propext]` | Exact registered claim and pointwise meaning of the Rust first-three-values statement, generalized from the intended scalar field to all commutative rings. No field or nontriviality silently added. | **holds**, no added assumption |
| 4 / `multiplication_not_affine` | Fresh bound module build; complete matching type print; `[propext]`; first zero-ring rejection control present | Exact global claim 4; a consequence of the finite obstruction described in Rust 954–970. Its exported statement does not itself locate finite obstruction points. | **holds** for stated global scope, no added assumption |
| 5 / `two_probes_insufficient` | Fresh bound module build; complete matching type print; `[propext]`; no separate target receipt | Exact declared boundary control for omission of `(0,1)`. Supports the determination boundary; no claim that the Rust file contains this exact test or that arbitrary two points are covered. | **holds** for the explicit witnesses and pairs, no added assumption |
| 6 / `zero_ring_product_control` | Fresh bound module build; complete concrete type print; `[propext, Quot.sound]`; used by both rejection controls | Exact zero-ring claim. This is a proof boundary countermodel, not an assertion that Rust's scalar field is the zero ring. | **holds**, no added assumption |
| 7 / `multiplication_not_affine_on_four_probes` | Fresh bound module build; complete matching type print and `[propext]`; second zero-ring rejection control present; no separate target receipt | Exact four-conjunct mathematical claim and universal content of the Rust comment/test. Faithfully separates finite obstruction from claim 4's global statement. | **holds**, no added assumption |

No row promotes a successful build to a semantic fidelity result. Fidelity above comes from comparing the statements, source expressions, argument order and actual printed types. Machine evidence is reported in its own column.

## Separate unproved bridges and exclusions

These are not secretly inserted hypotheses in the seven theorems. They remain necessary obligations for broader claims about the implementation or protocol, and their absence limits this review's verdict. Relevant helper implementations are imported in the Rust file but absent from this view; I did not follow them outside it.

| ID / category | Separate unproved obligation |
|---|---|
| I1 / implementation | Show that `scalar_modulus()` denotes the intended nonzero prime modulus and formally instantiate the Rust scalar-value model as a commutative ring/nontrivial ring. The seven declarations do not instantiate BLS12-381. |
| I2 / implementation | Prove the imported `fr_add`, `fr_mul` and `fr_sub` on BigUint implement the corresponding quotient-ring operations on all relevant inputs. Reading their call order does not prove their semantics. |
| I3 / implementation | Prove `AffineTransition::new` performs the claimed canonical reductions and that `evaluate` refines Lean `evaluate` for all stored coefficients and input representatives. Ring coefficient equality alone is not raw BigUint equality. |
| I4 / implementation | Establish compiler/runtime execution correctness, totality/resource behavior and the actual Rust test execution. This review ran neither Rust nor Lean and does not validate historical test claims. |
| R1 / representation | Prove the private-field/constructor/API invariant covers every reachable transition representation, including internal construction and all allowed mutation/creation paths. Source inspection observes the typed API but is not a verified representation invariant. |
| R2 / representation | Prove a formal polynomial degree bound and the connection from the typed expression to an `MvPolynomial` representation. The source restricts the expression syntax to affine form; none of the seven statements is a total-degree theorem. Over finite fields, a high-degree polynomial expression can also denote an affine function, so no blanket extensional exclusion of every high-degree expression follows. |
| E1 / encoding | Prove correctness/canonicality/injectivity of `reduced_bytes` on the modeled field values. That implementation is absent from this view. |
| E2 / encoding | Prove the evaluation order, lengths and concatenation framing make the encoded ordered probe vector unambiguous. Equality of three field values is not equality/injectivity of arbitrary serialized bytes. |
| E3 / fingerprint | Prove the full Rust `air_fingerprint` refines the modeled vector and has the claimed distinguishing property after encoding. The implementation emits a domain tag and five evaluations (three designated plus `AIR_PROBES = 2` fixed public pairs); the Lean claims neither model these bytes nor the two additional generated pairs. `air_fingerprint` itself returns bytes, not a proven collision-free hash. |
| E4 / statement encoding | Prove the full `statement_transcript` encoding binds parameters, boundary constraints and transition bytes as intended, including canonicality and serialization. Transition extensionality is not injectivity of the entire serialized AIR/statement. |
| S1 / security | Establish Merkle/hash commitment correctness and the appropriate collision/security assumptions. No cryptographic hash injectivity or collision-resistance theorem appears here. |
| S2 / security | Establish Fiat–Shamir sampling, challenge distribution, domain separation and transcript sequencing properties, and any random-oracle assumptions. Deterministic probe recovery alone does not provide them. |
| S3 / security | Prove complete AIR satisfaction, composition polynomial properties and correspondence between trace constraints and the actual prover/verifier. The affine expression identity is only one algebraic component. |
| S4 / security | Prove composition/ALI/DEEP/FRI soundness and a quantitative security bound with all required assumptions. The Rust module explicitly disclaims a proven soundness bound/security level. |
| S5 / security | Prove any zero-knowledge claim; the supplied Rust module expressly says it is not zero-knowledge. These seven expression theorems do not change that. |
| H1 / historical validation | Validate historical runs, timings, benchmarks and other experimental conclusions separately. The present fresh Lean packet establishes its limited formal execution evidence, not those historical claims. |

The explicit exclusions in `CLAIMS.md` 57–71 agree with this boundary. A broad end-to-end implementation/security conclusion would remain **inconclusive** on these inputs. The seven stated mathematical claims and their source/type fidelity receive **holds**. No official task-state promotion, experiment result or scientific transition is authorized or performed by this report.

## Actual input manifest

Paths below are relative to the admitted J2 source view. A hash of the entire file identifies the file; it does not assert that every unrelated Rust function or every dependency named in a receipt was semantically reviewed. Detailed read scopes are in the JSON attestation.

| Path | SHA-256 |
|---|---|
| `ADMISSION.json` | `e1db70041f7207605246c86e782c25d7b4dda1dd03891c4d994d26942a391424` |
| `HANDOFF.json` | `da840087172d85804e93abb9ff32c96dafb2db44f20b370e1a7a28ac08a17982` |
| `formal/CryptoResearch/Stark/AffineTransition.lean` | `3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d` |
| `formal/targets/stark-affine-probes.yaml` | `9407079fce149571b3e34d6088c13a587e0fccd5bfe624e4060b81911b2f5daf` |
| `formal/lean-toolchain` | `5699bbbd7db4601365371c8b0c9bf463d07d747b5f4d8aedabce9eb067dfc150` |
| `formal/lake-manifest.json` | `3adfcdc058cb9fe8556812d1b6cb76b75d3e1295f705f8e08296e2a28dc3a4dc` |
| `formal/lakefile.toml` | `ff38d76dfa30f8e499a3d7870fc510bcea8d9da4fd4f19f315fba90b3ce5c788` |
| `research/stark-affine-proof-20261029/CLAIMS.md` | `277a0e46061cb74b274c5e7310f6810f04d256d1fb93a13cf8dd79832f077f42` |
| `research/stark-affine-proof-20261029/source-exhibit.txt` | `7e368a9a65cb839501831fddd4918c664d7fa595c295b290acdb2ef9e2134195` |
| `rust-stark_v2-8ce2800f.rs` | `3bfe1facc87a2e522ffb69984cee5c18db71d1a216e72e521a5c694142b0e223` |
| `fresh-native-41109712394/binding.json` | `04b70b07f8e1778263d292a257f04058ff7330598221c4848dfebef1b0241d91` |
| `fresh-native-41109712394/artifact.json` | `b1d0922d9286e80e0d68fa325238d8d4bb018959b2af567b721f734701a05087` |
| `fresh-native-41109712394/stark-affine-probes.json` | `5e61fbaa874085ecb5e77e551ae1c9783e003e75c1560f9bad92d873ba63e4a1` |
| `fresh-native-41109712394/types-and-axioms.txt` | `b21d123c8bddfd838339520f86e0f2d0806621d5716212461376688b27402fe1` |
