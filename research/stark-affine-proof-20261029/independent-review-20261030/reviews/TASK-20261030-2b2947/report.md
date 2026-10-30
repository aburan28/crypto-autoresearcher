**J3 native evidence and proof-boundary review — TASK-20261030-2b2947**

**Verdict: inconclusive for the complete verification boundary.** The bounded hosted native checks hold: the current seven-declaration module was built, all seven actual types and axiom prints are present, and both expected nontriviality rejections occur for the intended reason. No hidden assumed conclusion, hole or nonstandard axiom was found in the admitted target. Clean installed dependency revisions and an independent kernel/binary recheck are not established; those requirements remain inconclusive.

This is an independent J3 report, not a whole-claim vote or official scientific transition. The admitted view is /workspace/pr-integration/review-2681-inputs/J3, published input commit 77b2f0052d648f3753f788aa73e21fddc8d0f70b, with published claim/reservation commit fab6ed6e5b58ac68a60f7b3f756494714a4add5e. No sibling or historical review reports/responses, out-of-view producer source, or Git history were inspected. Older native/verifier files and the full Rust file were hashed only. The admitted claim and Rust source exhibit were read; links to review responses were not followed.

| Dimension | Finding |
| --- | --- |
| Machine status | Passed for the seven declarations through the fresh hosted source-module build and actual type/axiom output, under ordinary Lean/Lake dependency-binary trust. The single registered target separately reports machine_verified. |
| Fidelity implication | faithful_scoped for the seven elaborated abstract propositions against their matching numbered CLAIMS.md statements. Broader implementation and security fidelity are not established. |
| J3 review outcome | inconclusive for the complete installed-dependency and independent recheck boundary; native type/axiom/control subchecks hold. No mathematical refutation is reported. |

**Exact input bindings.** All 36 admitted mathematical input SHA-256 values match, as do the two administrative file hashes. They were rechecked before output. The fresh receipt's source/spec/toolchain/manifest fields match the admitted files, and all ten recorded verifier hashes match fresh-verifier/. In particular fresh targets.py is 6e78dcc6ae2a7ce32dfbe017d2a14c524b23665a45bb860398483f5579149c8d; the different historical targets.py was not substituted.

| Input | SHA-256 |
| --- | --- |
| AffineTransition.lean | 3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d |
| stark-affine-probes.yaml | 9407079fce149571b3e34d6088c13a587e0fccd5bfe624e4060b81911b2f5daf |
| lean-toolchain | 5699bbbd7db4601365371c8b0c9bf463d07d747b5f4d8aedabce9eb067dfc150 |
| lake-manifest.json | 3adfcdc058cb9fe8556812d1b6cb76b75d3e1295f705f8e08296e2a28dc3a4dc |
| lakefile.toml | ff38d76dfa30f8e499a3d7870fc510bcea8d9da4fd4f19f315fba90b3ce5c788 |
| Fresh receipt | 5e61fbaa874085ecb5e77e551ae1c9783e003e75c1560f9bad92d873ba63e4a1 |

The toolchain is leanprover/lean4:v4.35.0-rc1. Hosted evidence reports Lean commit 86c6347c75e39ec18c40e25ed2143b71a6e04a0a and Lake 5.0.0-src+86c6347. All nine dependencies are pinned to exact Git revisions, including Mathlib 7fa22735254ddf7e11f119250a9f2d0352bc7c3a; the attestation retains every dependency pin and source/verifier hash. The moving master requirement in lakefile.toml does not replace the exact manifest pin.

The receipt records 69 workspace hashes. Four workspace entries are supplied here: the target source and three configuration/pin files. All four match. The remaining 65 contents, including project audit/root sources, cannot be independently compared with this minimal view. I did not run a full-workspace receipt validator and claim a complete consistency pass.

**Hosted execution linkage.** I independently retrieved only the same pinned [run 41109712394](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41109712394), job 124248764439, and artifact 13004731447 through GitHub tools. GitHub reports run success and successful relevant checkout, build, formal-target and upload steps. The execution head is producer 11d30c7a863816435b3098087c1264edc5bd54b2. The checkout log records synthetic commit 6170b8a9bd63e546eb68234e73a3ae89aaed4251 and the message “Merge 11d30c7a863816435b3098087c1264edc5bd54b2 into b9e9c8c606bdb406a4805ad61259bf3c4bcaaa26”, agreeing with binding.json and the receipt. No Git parent-object/history traversal occurred. The present PR-head value embedded in the run API response was not confused with the historical execution head.

The ZIP was downloaded and parsed entirely in memory. Its 702,537 bytes have SHA-256 ad53aa7463d5c44fc4ab3907cd3837dc82224f81e69d9de111acabab212f8082, agreeing with GitHub metadata and the upload log. Only stark-affine-probes.json was opened: its 81,897 bytes exactly match the admitted fresh receipt. The admitted types-and-axioms.txt is exactly receipt.build_log, SHA-256 b21d123c8bddfd838339520f86e0f2d0806621d5716212461376688b27402fe1.

Hosted log line 693 records “Built CryptoResearch.Stark.AffineTransition (2.8s)”. Its full type/control/axiom block at lines 694–1245, after timestamp removal, occurs exactly in the receipt (SHA-256 019ff2d9cacc37d63a6865f4d11362ebc036760c904def013db949943f1d2392). The two receipt copies are project and explicit-module replay output, not two independent kernel reruns.

The hosted commands include lake build and then python3 tools/verify_formal_targets.py --artifact-dir formal-receipts. The bound LeanWorker.verify source calls lake build +CryptoResearch.Stark.AffineTransition after project-build success, including during same-invocation reuse. The receipt contains that explicit module replay and successful 1,142-job completion. The outer hosted log does not echo this internally captured argv separately; invocation is supported by the bound worker code and resulting receipt, not an invented command transcript.

These are actual hosted execution observations beyond self-consistent JSON. They retain trust in GitHub, its runner/workflow, the reported Lean executable and the imported binary environment. Neither JSON nor hashes alone authenticate execution, and this review is not a cryptographic attestation of every machine action.

~~~mermaid
flowchart LR
  A["Admitted source/spec/pin hashes"] --> B["Hosted source module built"]
  B --> C["Seven types and axiom prints; two expected failures"]
  D["Exact GitHub artifact ZIP"] --> E["Admitted receipt bytes match"]
  C --> F["Bounded native checks hold"]
  E --> F
  F --> G["Installed dependency cleanliness and independent recheck inconclusive"]
~~~

**Seven actual types and axiom prints.** All names below are in CryptoResearch.Stark.AffineTransition. Generic types explicitly quantify R : Type u and use genuine Mathlib ring structure.

| Declaration | Actual interface | Type / axiom source lines | Actual transitive axioms |
| --- | --- | --- | --- |
| recover_coefficients | CommRing R; every a,b,c; designated recovery tuple equals (a,(b,c)). | 87 / 107 | propext |
| coefficients_eq_of_probes | CommRing R; six coefficients; three designated probe equalities imply coefficient-tuple equality. | 88 / 108 | propext |
| three_probe_extensionality | Same three premises; evaluation equality for every x,y : R; no nontriviality or field premise. | 89 / 109 | propext |
| multiplication_not_affine | CommRing R; Nontrivial R; every coefficient triple; negates agreement with multiplication everywhere. | 90 / 110 | propext |
| two_probes_insufficient | CommRing R; Nontrivial R; fixed triples (0,0,0) and (0,1,0); equality at two probes and inequality at (0,1). | 91 / 111 | propext |
| zero_ring_product_control | Every x,y : ZMod 1; zero affine evaluation equals x*y. | 92 / 112 | propext, Quot.sound |
| multiplication_not_affine_on_four_probes | CommRing R; Nontrivial R; every coefficient triple; negates the four-point conjunction. | 93 / 113 | propext |

For each of these seven declarations the hypothesis-delta table against its matching numbered CLAIMS.md statement is empty. All binders, fixed coefficients and Nontrivial conditions are stated there; no extra Fact, field, characteristic, denominator condition or conclusion-bearing instance appears. Assumptions introduced inside proofs of negations are discharged by contradiction, not exported assumed conclusions.

The single YAML target registers only three_probe_extensionality. Its named audit requires theorem status (thmInfo) and uses Lean.collectAxioms with the standard allow-list propext, Classical.choice, Quot.sound. It reports a 757-theorem project audit and a passing named-target audit. This does not create seven registered-target receipts. The six companions are covered instead by the actual shared source-module build and their own type and transitive axiom prints. The project theorem count is not semantic fidelity or complete-source coverage of every adjacent file.

**Controls and forbidden constructs.** The admitted target contains none of sorry, admit, custom axiom, unsafe, native_decide, implemented_by, extern, run_tac or run_cmd. The receipt's forbidden list is empty. Actual axiom prints contain no sorryAx, custom axiom or native-evaluation exception. The worker scan skips hidden directories and symlinks; it does not certify every hidden/dependency source. This target is a visible regular source importing only Mathlib.Algebra.Ring.Basic and Mathlib.Data.ZMod.Basic.

The missing-probe theorem proves equality at (0,0) and (1,0), but inequality at (0,1), for the specified transitions in every nontrivial commutative ring. It witnesses omission of that designated third probe; it does not claim every arbitrary pair of probes is insufficient. The ZMod 1 control proves global agreement with multiplication and is a countermodel to either obstruction without nontriviality.

Both native #check_failure applications reject the current obstructions at ZMod 1. Source lines 99 and 103 each report “failed to synthesize instance of type class Nontrivial (ZMod 1)”. These are expected elaboration failures inside a successful build, not infrastructure failures. The checked countermodel shows the weakened statements are false; the failed applications show the current theorems cannot be instantiated there. No newly mutated theorem with its binder removed was built by this reviewer.

**Uncovered boundaries.** The job restores formal/.lake/packages from cache and downloads 8,915 cached Mathlib files. No installed-package HEAD/dirty-tree check was found in the admitted receipt or inspected log. Project checkout clean:true does not establish cleanliness of later-restored dependencies. Exact installed revisions/cleanliness are not_verified and inconclusive even though manifest hashes match.

The action explicitly sets leanchecker:false, lean4checker:false and nanoda:false. No independent kernel/binary checker or reviewer-local Lean run occurred. Standard Lean/Lake import trust remains. Pre/post input hashes and same-invocation reuse checks do not exclude transient edits or authenticate filesystem immutability. Complete comparison of the other 65 workspace sources is also inconclusive under the admitted-view restriction.

No Rust execution/refinement, byte/hash injectivity, AIR satisfaction, total-degree formalization, STARK/DEEP/FRI soundness, zero knowledge, security level, historical benchmark or performance claim is certified. The finite four-probe theorem states its exact expression-level obstruction; global nonagreement alone would not identify those four points. Whole-claim source fidelity and the other review joints require composition after archive.

**Procedure and runtime.** I applied the repository review-evidence formal-review skill and its Lean reference. The handoff's stricter immutable-view, no-history/no-build and two-output limits governed this session. Relevant primary references were the admitted claim/source/exhibit and verifier code. No novelty claim or out-of-view literature survey was made. No scientific trial, solver, benchmark, package installation, local heavy Lean build, git mutation, sibling contact, message to another person or official state change occurred. No PDF file was produced because this task permits only report.md and attestation.json; packet composition/archive belongs to TASK-20261030-92733b.

The prospective amendment authorizes the bounded native default-model fallback. Requested policy is review-adversarial, effort xhigh, and parent history none. This session began with its administrative task, without producer history. Actual serving model, inference provider, tier, context/output ceilings and effective effort are unauthenticated: model_verified:false and fallback_used:true, with degraded requirements explicit in the attestation. No Opus execution, opaque model/session UUID, CLI inference probe or independent kernel recheck is claimed.

A later administrative notice reported a brief workspace restart. My visible review context remained available, but the functions.exec auxiliary metadata store was unavailable afterward. The final metadata was reconstructed from the already recorded tool observations and original admitted files; admitted inputs were rehashed before writing. One output-preparation functions.exec call had a JavaScript SyntaxError before any shell command or file write; it was corrected without altering the evidence.

To close the uncovered execution boundary, obtain actual clean installed revision evidence for all manifest dependencies and retain actual independent rechecker output if claiming that assurance. This report infers neither.
