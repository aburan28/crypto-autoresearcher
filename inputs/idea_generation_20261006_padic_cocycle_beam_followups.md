# Prime-field ECDLP controlled mechanism follow-ups — 2026-10-06

## Intake status

- Source type: user-directed external follow-up experiments.
- Scope: classical ECDLP in prime-order subgroups of short-Weierstrass curves over prime fields.
- Exclusions: no Pollard-rho collision walk and no index-calculus relation collection.
- Evidence tier: deterministic toy experiments, external to this repository's contract and run-receipt system.
- Canonical status: none. This file allocates no IDEA, hypothesis, experiment, evidence, or decision identifier and changes no official research state.
- Bottom line: five earlier frozen successors failed their gates, then thirty-one structured addition, collision-sketch, validation-cost, representative-table, state-reuse, and data-flow measurements continued the path. Denominator clearing exposed an exact constructible rank-four numerator; a quotient/remainder rectangle represents the complete quadratic-character orbit with two singular corrections. Target translation recovers every toy log through a labelled square-root point collision, explicitly identifying the resulting decoder as signed, shifted baby-step/giant-step rather than a new method. Later first-success stopping, compact minimum-ticket representatives, and final-state fingerprints substantially reduced repeated toy construction/query or validation work, but remained square-root collision-table time-memory variants rather than establishing a new exponent. A public-target seed audit removed inherited harness-only target-scalar metadata and passed for one frozen derivation; an eight-salt robustness run remains queued.
- Import rule: treat these measurements as deduplication, control, and stop-rule priors until reproduced under a frozen repository experiment.

The originating code and JSON remain in a separate local repository. Reported provenance locators are:

| Artifact | SHA-256 or commit |
|---|---|
| p-adic decision-rule commit | `d27a568` |
| p-adic implementation commit | `4d06b69` |
| `padic_cocycle_lab.py` | `740dbe3078cbd246b5134944b5aee9073e241fd3541bc22467be4d39dfcabc95` |
| `tests/test_padic_cocycle_lab.py` | `1da80b4c43cb4ed51b1c8a6946dec24f138369011a11ef30616c996c65f59b8b` |
| `results/padic-cocycle.json` | `3c71a839f6e81f09a1903dc7aac94842a5137a78e05670b4d4b8a94db507502f` |
| beam decision-rule commit | `387b958` |
| beam implementation commit | `efbec7d` |
| `beam_exponent_lab.py` | `3e10208bd4f955f8432e51c364d96cadce9531ec77d42c4901ad0c69fde71719` |
| `tests/test_beam_exponent_lab.py` | `f4da6de0276fac21c181a2d2c821c2e5527487ae8123672104ad01f839aa3d3d` |
| `results/beam-exponent.json` | `b9a15961813afe9c8ee5d5830ab9876441d66661fafb8e2654d648faa9c79f7e` |
| sparse-defect decision-rule commits | `cd8939f`, `1249bb8` |
| sparse-defect implementation commit | `df744b2` |
| `translation_defect_lab.py` | `e7239dadc9380404326c66c710a1bc3de72937b6c0b05618251b7a2180c65f12` |
| `tests/test_translation_defect_lab.py` | `ceb2485aa64ad901604582254279f50268cb39958c6e804bd9a76217bfab39fb` |
| `results/sparse-translation-defect.json` | `7314973c8a820cf56f74b633719089074d8dcbbef625d69a621d9c5f3296d7c2` |
| block-Hankel decision-rule commit | `bc973a3` |
| block-Hankel implementation commit | `aa7c91c` |
| `block_hankel_lab.py` | `997bcce5994dda04e4bf775d1396487f55c2a5133364f551618138514a78c801` |
| `tests/test_block_hankel_lab.py` | `8e5b2f84a4a1d3c08b1e373a17c822f67f10eb64f51c98cffb95708ff788276f` |
| `results/block-hankel-state.json` | `6acd64cdf432c65c892969bb0d83158a02b2f99cb960b96bd5b1385a4058eb44` |
| generator-blind decision-rule commits | `d0bb017`, `50df5ab` |
| generator-blind implementation commit | `9be8ee9` |
| `generator_blind_lab.py` | `1b5f9d1b3766c940d504cf099f1420ab5f0b16c8142548be87dce7fe8fce5d74` |
| `tests/test_generator_blind_lab.py` | `9bcdb24e5c80a4725221368acc7d9176767532ab17318e44b12e5651f2be82d3` |
| `results/generator-blind-grammar.json` | `9134f6d0114ca22d4a40b6299250a9775c56f782ae70577bc4f153c4a780f835` |
| addition-kernel decision-rule commit | `d376c7d` |
| addition-kernel implementation commit | `a9fb5d0` |
| `addition_kernel_lab.py` | `eb141c6ed713e85f415a5f3b8b7b5f29fef490db722eb638b5dd15a62485ff86` |
| `tests/test_addition_kernel_lab.py` | `9586bbd995bb5f415b26998209740235cb2f4d766ffeb30e045ef6c014bb6776` |
| `results/addition-kernel-rank.json` | `c97d206dd03c60dd776fd8caca55ed6929213974253779e43bd5050a3f11ad6b` |
| rational-addition decision/layout commits | `2bbaa1d`, `b5ca515` |
| rational-addition implementation commit | `04c592b` |
| `rational_addition_lab.py` | `e4a54969b5b88481b88a96d1872a36f28a32cfac838cde511372a4a1f58fd824` |
| `tests/test_rational_addition_lab.py` | `cfbb3a28693a996e0111e65e6a133696ef038d5aba89874c62910fcf83f63131` |
| `results/rational-addition-structure.json` | `6f3a68202efcce5d2f2c8af03f31fa85245ce9f70c302a4ecf02a80b9802cd7c` |
| Gauss-expansion decision-rule commit | `faf037a` |
| Gauss-expansion implementation commit | `5fb2c97` |
| `gauss_expansion_lab.py` | `8fc4ea1c1ae78533df2a25d1d5e174c7d04d6fb503775a99ef6092f4244f71ab` |
| `tests/test_gauss_expansion_lab.py` | `9415147685f938a4192e5a4e0cce99b93b687ff829cad9c53f36ad6e833a0a12` |
| `results/gauss-character-expansion.json` | `ceac60648d389a6897941534e94a9dd197a34bff66b4bcab32f0984abd356b2c` |
| direct-factor decision-rule commit | `168b34b` |
| direct-factor implementation commit | `22510a9` |
| `four_factor_summation_lab.py` | `1792310cafadc56530387656ce3e808f264399996cebb0281b2cdf62c3c15eb3` |
| `tests/test_four_factor_summation_lab.py` | `6d7c33207ab575d1bc67f759ffb88862a802833be5cf5ac8ee65158cac178a6f` |
| `results/direct-four-factor-summation.json` | `0850b12efe96ab7c5c076ffdcea02f3227a6e517736a4c5b59f6da7ad2fdf6f1` |
| joint-transform decision-rule commit | `ccc20f0` |
| joint-transform implementation commit | `792206b` |
| `joint_transform_lab.py` | `497493d2753386956062d9ef4bd311ed58d3614bd89ca919c35830bac29d1713` |
| `tests/test_joint_transform_lab.py` | `cbe4007b5ace3fc8f6baf69000c67fe6268f1d0002eb42a14b08e6ad966857f8` |
| `results/joint-residue-scalar-transform.json` | `172eaa16734f46b303df5e9e488564eb739a44c0f199b56da510268e07a6a2fb` |
| full-coverage decision-rule commit | `3bcd12e` |
| full-coverage implementation commit | `9fd6f69` |
| `full_coverage_correction_lab.py` | `d291b00ba03122514b7f95b72351fb949ea27e89e66693984c9da2aba93c1222` |
| `tests/test_full_coverage_correction_lab.py` | `140b2d28a1a6aa1a64aeaa7736753cbd724d9849f147d6b6850a86761674f036` |
| `results/full-coverage-sparse-correction.json` | `8f29bd3e30e14aa03f7bfcca30477024af343b1a9aa41baf40abf8c992de5382` |
| translated-target decision-rule commit | `a4770aa` |
| translated-target implementation commit | `331c439` |
| `target_translation_lab.py` | `bc51cb42e2adad6da9c6d958d37e1f602283886c5e675b20f0d798451305f2ea` |
| `tests/test_target_translation_lab.py` | `eb40cc33b23e67a028e60782bdaed3841ff645d9038cad29e9e2ea8989b10fbc` |
| `results/target-translated-collision-decoder.json` | `9b52c7ef77f5b01806fcf68ca5cf820aa646528c43e1ef4351a83f5c5760e3ef` |
| streaming-resultant freeze/audit commits | `18f0d70`, `67a90f3` |
| streaming-resultant implementation/audit commits | `275c0ce`, `1b5991f` |
| `streaming_resultant_lab.py` | `612eb4613a4284cbc75bc6dc0b97616f2ea73f41c9517dab2ffe2ec54c313eb8` |
| `tests/test_streaming_resultant_lab.py` | `64385af442cca70c34d0e54813ab85138ce2f23c81fab201f3603dc92093ae01` |
| `results/streaming-resultant-decoder.json` | `281d5002a9dd7a6a3c8ba99e1d147ec5f7690b1d6ddb1a808f667562caf3d8b7` |
| hashed-moment freeze commit | `3a8699c` |
| hashed-moment implementation commit | `779cd75` |
| `hashed_moment_lab.py` | `e95429d25b20daf0fd77d2d7139d5378690c82b0a25002e6ddd9b331643a3386` |
| `tests/test_hashed_moment_lab.py` | `e79bc65a4db1335c60ff570b0ac0de3add1b28a3ead87d4b19b8928565e5b4c0` |
| `results/hashed-moment-sketch.json` | `49c2a83cc049821f3ccbdae47e05b8174d2e30c3a485456aec7a812349bb24ff` |
| capped-peeling freeze/implementation/result commits | `e5dda77`, `88c074e`, `59cb4e4` |
| `coupled_peeling_lab.py` | `80dc34403e803cc5f8bb63e34c5a66eac3d0da11d7a2ea04c1ab40781f7f16d3` |
| `tests/test_coupled_peeling_lab.py` | `b55f8d429401d6d8727eca415930deea312fc36a5be74acdc26aa88fc9ca2d82` |
| `results/coupled-peeling-seed-search.json` | `52d81064c6c5de40b2f5d52d828b65195d74769fa8aeb386c1ac1520bef2c25c` |
| singleton-scaling freeze/implementation/result commits | `1667b53`, `d54969f`, `2b64007` |
| `singleton_scaling_lab.py` | `8018ff29b9626d672e32e157fceb81dcd2d5e4b6cdc2dc5e12c82fe2e5f794c0` |
| `tests/test_singleton_scaling_lab.py` | `3e2ea8082a6e088b40e7593481ce406a1f3fe6f1db1a5015b19bbe96250db408` |
| `results/singleton-sketch-scaling.json` | `0342e27f86f03d37003d0e7650aca21310040fb6d7e5fd721fb6abfabc68ef6b` |
| sub-cap freeze/implementation/result commits | `a442759`, `95a2fed`, `58c35fc` |
| `subcap_sketch_lab.py` | `7674346450e535e4f5999f42372a5b9ae669c050a5baea3076bf42e601eb4ac2` |
| `tests/test_subcap_sketch_lab.py` | `39a8b6893c55f515f3c09e5468a2190dba480faf64fbc76955af0bc28b92301b` |
| `results/subcap-sequential-sketch.json` | `9ec7375d21cb082adf82cb9e4a2c95feaeee3d43ce626f2f6fb0862d2c076320` |
| x-quotient freeze/implementation/result commits | `18133d6`, `0deb150`, `a6255b1` |
| `x_quotient_sketch_lab.py` | `d59b1fe654819f4968c9ade0fd8978f8c013eb8409d4415add0830dea83eb80e` |
| `tests/test_x_quotient_sketch_lab.py` | `00309dfa9d1ee5e86a8e08ec782b6383183eac236ca99bbc644802f47613e4c7` |
| `results/x-quotient-sketch.json` | `d25bff18bce72b9ba43aa3613f17b01e5e0d5595b36e17b71c22275093266f92` |
| equal-work freeze/implementation/result commits | `a6255b1`, `2be24e9`, `6eb39c7` |
| `equal_work_schedule_lab.py` | `ccfc23e1e3329cc5278e3bee29c0b103384be6caf5e03dfd7edabe826847e4c2` |
| `tests/test_equal_work_schedule_lab.py` | `20fd487a2157e1a5e3f109a4f480768e99bdd1d6736d2d76e0a9990e52e46134` |
| `results/equal-work-quotient-schedule.json` | `f75bcb3f205843e606875b259a53cfe30ea75fb65ad8c24137b09267d223ed13` |
| validation-backed-pair freeze/implementation/result commits | `6eb39c7`, `fb2e013`, `f8493e7` |
| `validated_x_pair_lab.py` | `32b597a3343a920f6cf0b242488095c201c6a05d990518c75865f40635299984` |
| `tests/test_validated_x_pair_lab.py` | `8e506279366a4c209be51d973d62c38f937ed5a7e212b1ffb676ea819f3bf477` |
| `results/validation-backed-x-pair.json` | `ee5cf4d5e456bd14ee287e22e794689ec2c7e35a5f70fcd994626d8e30559547` |
| nonlinear-fingerprint freeze/implementation/result commits | `f8493e7`, `733b36d`, `d59cecf` |
| `nonlinear_x_pair_fingerprint_lab.py` | `15894d3ab72834c97a79141ca41604c6ef6ed01c8d29f4996dfad90928a249a4` |
| `tests/test_nonlinear_x_pair_fingerprint_lab.py` | `4f678481474e67233ef623201aaea24d2710eeec32fd98a063b9d3a316968094` |
| `results/nonlinear-x-pair-fingerprint.json` | `24b34eccec2bed770147b21293174775a5af31f470920199df6aa61e861bc6e4` |
| cheap-fingerprint freeze/implementation/result commits | `d59cecf`, `52dd84b`, `e0cad76` |
| `cheap_x_pair_fingerprint_lab.py` | `4fc68903521361893331d8c9563344f6e72184f9dc4d758c5a094cc9d1acc08d` |
| `tests/test_cheap_x_pair_fingerprint_lab.py` | `3f34c5099c6ae1e0550732e3e7467bba845319d334889dde75c119b0edd505ef` |
| `results/cheap-x-pair-fingerprint-frontier.json` | `9de0931006bd5b8ac3f2a572c377392185582ea23640d3af35aae0c2dae22972` |
| coefficient-family freeze/implementation/result commits | `e0cad76`, `58e921c`, `ae57de2` |
| `quadratic_fingerprint_family_lab.py` | `bd7eed4cb7c77af352ffa277807408688360ab1752d57ad38e1ac16b2db3b173` |
| `tests/test_quadratic_fingerprint_family_lab.py` | `fa168262b89d4d7f73fb0c27eb3b2d7e9cdc9d173ee8a00a6e6fdbca9ed53914` |
| `results/quadratic-fingerprint-coefficient-family.json` | `2aebbb9612a8387b7621af933df4a9bf97c29402bb1f94f7759c5588ccb0b2b3` |
| validation-path freeze/implementation/result commits | `ae57de2`, `a6543f3`, `ee20e7c` |
| `validation_scalar_paths_lab.py` | `d6538ae7677b65d48bdccf2043d9a4caf0b63608de4339fd3c0812a69ed02b05` |
| `tests/test_validation_scalar_paths_lab.py` | `7e11ac12f7ba1395131837c1f20271e9875f5528fa397a91a9b3bec3689596f4` |
| `results/validation-scalar-operation-paths.json` | `388d6027e73382cf6010c7c86e4f0088fd6bf02e9294d2cc5a3f69cdad3f13ed` |
| first-success freeze/implementation/result commits | `ee20e7c`, `cb68727`, `b02cc11` |
| `first_success_stopping_lab.py` | `a90bb4e575182a5477f85224a40f5e7a7b5f782eeb04319bf44a525a209ea6bb` |
| `tests/test_first_success_stopping_lab.py` | `016d4e9cb9d6abe96aca505361f315541f50efc7ab624749f454f7a3e503847a` |
| `results/first-success-sequential-stopping.json` | `2b8183bba1ed52fe599b5ed392c0f25010202911c3e93bf2aa144abb5120f252` |
| sacrificial-occupancy freeze/implementation/control-fix/result commits | `b02cc11`, `a9ab751`, `51316c7`, `819d83a` |
| `sacrificial_bucket_lab.py` | `5799d34bc640ec96a68da3fa4ee47bc9747de4eae81eeab36e0be9754e5e68dc` |
| `tests/test_sacrificial_bucket_lab.py` | `f58b09a33aaf6e2f6a02fde1c88407af1e28183914f2e82f542f55b8f8b48b50` |
| `results/sacrificial-bucket-occupancy-invalid-control-seed.json` | `a2feac33ec20bf15f4bf736760861687e2998d049e0aacdcb1234c97ceb07b7f` |
| `results/sacrificial-bucket-occupancy.json` | `638735702726ac9ac26c67a1d4fd0e9a3066b1b84dc79e3610ad02aa77ae0e39` |
| minimum-ticket freeze/implementation/result commits | `819d83a`, `a09ecd1`, `182076e` |
| `minimum_ticket_representative_lab.py` | `c7b093d55b55c71d7612f953305b9b28caf25e94da2436608381332bf00dbf0a` |
| `tests/test_minimum_ticket_representative_lab.py` | `844d5fa01556edaacc9335656ff9507c017d924c987fb6debec592025a34e9b0` |
| `results/minimum-ticket-representatives.json` | `7f42ce8a0ddf43fd2e7f72039e51c1feefe73f48219b0f9d91cf694ba371e4ec` |
| two-element freeze/implementation/result commits | `182076e`, `037946e`, `2870603` |
| `two_element_representative_lab.py` | `2c4ebd18750facd7a21cd97df06e754802a67961b6a103e0ba197cdf1484afbd` |
| `tests/test_two_element_representative_lab.py` | `ee622f8ec853b9d8701ae5bf7816582debe27a4725ee5e6a2663272183e35c18` |
| `results/two-element-representatives.json` | `8d38e3891937cce7daee731d25346a940e7298bafe332f8eba2f277a9904a1f8` |
| two-choice freeze/implementation/result commits | `2870603`, `1642256`, `3db1087` |
| `two_choice_cuckoo_lab.py` | `c0253165fe1fea2eb6fbb0f68bf8ceb423bc1da09260086a5aac4e95710f88a8` |
| `tests/test_two_choice_cuckoo_lab.py` | `3963092bd671b436c7822044c68b539a07b44c415efaa5f2447d5e263d4ab8c6` |
| `results/two-choice-cuckoo-representatives.json` | `2d5ac59174cb076d1a56191008f3b5ff14e137534cf2e51fd415f3115575fef9` |
| label-only freeze/implementation/result commits | `3db1087`, `db00d69`, `cd394d2` |
| `label_only_validation_lab.py` | `3979b7577df277453cde79d2049c243e92dcae18e84b7170e9494dcc1d0bda02` |
| `tests/test_label_only_validation_lab.py` | `2a5337cb88c7766349b93bbe8d6939a63ee824b7c2272e0f1dbdce8e85133ea7` |
| `results/label-only-validation-table.json` | `5011b6478bf2994582e5c95dfb9ab23523daccc22c1c3f42588d555e5d614e5a` |
| one-bit state freeze/implementation/result commits | `cd394d2`, `2eea9b4`, `40ab7ec` |
| `state_bit_fingerprint_lab.py` | `a654dd044e7b14d5ee3fbdb7abb667a28c115a29332fbb6383506af585dd74e0` |
| `tests/test_state_bit_fingerprint_lab.py` | `1d59812ae21d4bcbe595f9de91768a902af94814275cd0e9ebea8ea11679b158` |
| `results/state-bit-label-fingerprint.json` | `0baeee422cf471060f76c99221a37192352f45c5cf767f188fe9f3a280ffbf23` |
| two-bit state freeze/implementation/result commits | `40ab7ec`, `17b6009`, `80c8f6c` |
| `two_bit_state_fingerprint_lab.py` | `c977d949065d21d9fe2a8df8a92ed2ed4ee31ed53d93875a94b6cf5eae121298` |
| `tests/test_two_bit_state_fingerprint_lab.py` | `b5e96a4420cff917bd23d94b0d1c67bb8749484bdf6082ad01c9f453b8a7e50a` |
| `results/two-bit-state-fingerprint.json` | `dabb07c1af498637796bc640061225ea5dbad228744192d5f7155039de37ab78` |
| ternary reuse freeze/implementation/result commits | `80c8f6c`, `66c8938`, `5c6a66f` |
| `ternary_state_reuse_lab.py` | `a513b01645eb4042b3a9ed84279d9efda742acef6a60d77ca0fdac75074c62e0` |
| `tests/test_ternary_state_reuse_lab.py` | `92e824c725bebdbbb3ec8163c504edeaeb750dd06a69d4560d45caa682143bd8` |
| `results/ternary-state-reuse.json` | `cb14ba44b9f63690bee2894d46d29faa8e58081aefd192a9a47cf52175983b4b` |
| sentinel state freeze/implementation/result commits | `5c6a66f`, `50c7ce3`, `19ded37` |
| `sentinel_quaternary_state_lab.py` | `4dae069289443fddc881023e4a7f246f122295983c6a6bb628b7e117786496a4` |
| `tests/test_sentinel_quaternary_state_lab.py` | `e39e580ee6433dadce2554c9453fd265176fb01b3c75e74fc0fd802be4a3f318` |
| `results/sentinel-quaternary-state.json` | `bec2504a962752152a8996aee639c2cdc53049df0dab64515381a8a3fd7d6466` |
| decoy-first freeze/implementation/result commits | `19ded37`, `1068255`, `8ecdfe1` |
| `decoy_first_sentinel_lab.py` | `a81d760fcd6f30122b9471490b587632965bdf6fc65f28ea354a7e89ab855677` |
| `tests/test_decoy_first_sentinel_lab.py` | `5ed99769d48cd7fb4ac8dfa0cc482513d5f98a2995dba1124f56faf3a89a0142` |
| `results/decoy-first-sentinel.json` | `d67949d57d156131756e35b57830e40f62f02878c22274f3c57c93a9860649fc` |
| public-target seed-audit freeze/implementation/result commits | `8ecdfe1`, `e467418`, `ea1e699` |
| `public_target_seed_audit_lab.py` | `9c7c97e2bde3857ad8fb157385b01fefe952fb827a69ef44f2ccb8844a035719` |
| `tests/test_public_target_seed_audit_lab.py` | `12eb5df399d5e450d3895a7c7b11ce131db6bd8c61a8f1b7194feb3c1a24585e` |
| `results/public-target-seed-audit.json` | `fe0531d3c618d9a54d525b91daf2c7760d03fed2d9cb347d2d8acaf4ba56ff68` |
| public-seed salt-robustness freeze commit | `ea1e699` |

All thirty-seven result payloads omit timing fields and reproduced byte-for-byte. The expanded external suite passed 148/148 tests. These are provenance statements, not repository run receipts. The sacrificial-occupancy invalid-control payload is intentionally retained: its duplicated second-control seed made the frozen reproduction gate fail before the corrected full rerun.

## H9 — p-adic section-defect cocycle cancellation

### Mechanism

For a public lift section `s:E(F_p)->E(Z/p^2)`, compute the formal-kernel coordinate

```
C(A,B) = t(s(A)+s(B)-s(A+B))/p mod p,
```

where `t=-x/y` is the formal parameter at the identity. The hypothesis was that signed two-point combinations might cancel the arbitrary section contribution that defeated the earlier one-point ordinary-curve lift quotient.

Four public sections were frozen. They shift the lifted x-coordinate by `p*d(x,y)` for `d=0`, `x`, `y`, and `x^2+3y+17`, then solve for the y correction modulo `p`.

Six constant-work formulas were frozen before execution:

1. `C(Q,P)`;
2. `C(Q,Q)`;
3. `C(Q,P)-C(Q,-P)`;
4. the signed parallelogram `C(Q,P)+C(-Q,-P)-C(Q,-P)-C(-Q,P)`;
5. `C(Q,Q)+C(2Q,2Q)`;
6. `C(Q+P,P)-C(Q,P)`.

Each formula could use only public normalization by its values at `O` and `P`. No target labels were fitted.

### Predeclared gates

The arithmetic gate required zero failures of the abelian cocycle identity and commutativity over 128 deterministic triples per curve/section, plus exact recovery by the existing Smart trace-one positive control.

The mechanism gate required one fixed formula to give identical normalized predictions under all four sections and exact canonical logs on at least five of seven ordinary curves.

### Result

The arithmetic gate passed:

- zero cocycle or commutativity failures across nine curves and four sections;
- Smart's known anomalous quotient recovered 96/96 sampled logs on both A163 and A367.

The mechanism gate failed:

- every formula had **0/7** ordinary-curve support;
- no usable formula produced section-invariant predictions;
- best per-section canonical accuracy declined from at most 6.48% on the smallest curves to 0.53% at order 947, consistent with accidental field-sized matches.

This matches the expected obstruction. The formal kernel is the additive group of `F_p`, while the ordinary subgroup has prime order `r != p`; an additive homomorphism between these coprime-order groups is trivial. The anomalous case `r=p` is precisely where Smart's nontrivial linear observable exists.

Disposition: preserve the arithmetic/control harness and scoped negative. Do not expand the formula grammar unless a successor first explains how it evades both section coboundaries and the coprime-order obstruction. Allocate no canonical ID from this packet.

## H10 — scalar-balanced inverse-doubling beam exponent

### Mechanism

The earlier fixed-width beam percentages did not answer whether the correct branch survives in sub-square-root width. This follow-up measured the first power-of-two width reaching 90% recovery for the already frozen height and lifted-carry rankings.

The protocol used:

- every nonidentity target;
- generators `[u]P` for `u in {1,2,3,5}`;
- widths through the complete binary frontier;
- the original deterministic random score;
- a matched permutation of each coordinate score table over nonzero scalar indices;
- complete accounting of equivalent inverse-two multiplications, subtractions, score evaluations, and final candidate verifications.

The frozen primary statistic was equal-weight macro accuracy across scalar bit-length buckets. Width scaling was fit as `W_90=r^alpha` with 2,000 deterministic curve-level bootstrap replicates.

### Predeclared gate

Height or carry could advance only if:

1. the one-sided 99% upper bound on `alpha` was below `1/2`; and
2. its `W_90` was strictly below both its matched score permutation and the random control for every generator on at least five of seven curves.

### Result

| score | primary W90 exponent | one-sided 99% upper bound | curves beating both controls on every generator |
|---|---:|---:|---:|
| height | 0.730762 | 0.974538 | 0/7 |
| carry | 0.621314 | 1.379280 | 0/7 |
| random control | 0.417010 | 1.588964 | n/a |
| permuted height | 0.588414 | 1.342833 | n/a |
| permuted carry | 0.687135 | 1.657458 | n/a |

Both candidates failed both gates. Generator sensitivity was large: within one curve, the first tested `W_90` often varied by a factor of four or eight.

A post-run methodology audit found that equal bucket weighting still gives easy tiny-scalar buckets disproportionate influence. The frozen primary decision was retained. A stricter, non-rescuing largest-bit-length-only diagnostic increased the height and carry exponent estimates to 0.970037 and 0.938425, with upper bounds 1.161027 and 1.279711. This strengthens the negative.

Complete toy orbit tables accelerated the measurement simulator, but were not credited as an attack resource. The scalar-state simulator was tested against the original group-operation solver.

Disposition: retire the frozen height and carry rankings. A successor needs a generator-invariant branch statistic and a predicted sub-square-root survival exponent before another beam sweep. Allocate no canonical ID from this packet.

## H11 — sparse translation-defect equation

### Mechanism and obstruction

For `f` in the Riemann--Roch space `L(mO)`, the frozen proposal sought

```
f(Q+P) - f(Q) = 1
```

outside an explicitly stored exception set. The residual
`g(Q)=f(Q+P)-f(Q)-1` has poles only at `O` and `-P`, with total pole degree at
most `2m`. It is not identically zero on an ordinary order-`r` cycle: summing
over `r` translations would imply `r=0` in `F_p`, but `r != p`. Thus at most
`2m` affine edges agree.

The two edges touching `O` are mandatory exceptions. With the constant
coefficient removed because it cancels under translation, there are `d=m-1`
useful coefficients and

```
e >= max(2, r-2m),
d+e >= ceil(r/2).
```

This is an undercharged linear lower bound before storing exception locations
or correction values. It is scoped to the explicit-exception representation;
it is not a general ECDLP lower bound or a novelty claim.

### Frozen audit and result

The audit used all seven ordinary toy curves, generators `[u]P` for
`u in {1,2,3,5}`, pole orders `2,3,4,8,16,32`, fixed deterministic consensus
samples, permuted-point controls, random-label-difference controls, and a
planted one-defect positive control. The rule and exact secondary comparison
were committed before implementation.

| curve | order | optimized lower bound on `d+e` | bound / `sqrt(r)` | generators beating both controls |
|---|---:|---:|---:|---:|
| E101 | 83 | 42 | 4.610 | 2/4 |
| E127 | 109 | 55 | 5.268 | 2/4 |
| E149 | 139 | 70 | 5.937 | 1/4 |
| E211 | 223 | 112 | 7.500 | 3/4 |
| E283 | 281 | 141 | 8.411 | 2/4 |
| E503 | 499 | 250 | 11.192 | 1/4 |
| E907 | 947 | 474 | 15.403 | 2/4 |

Every arithmetic and planted-defect audit passed. Every EC witness respected
the `2m` divisor ceiling and every required complete system was inconsistent.
No curve beat both matched controls on all four generators, so the empirical
gate scored **0/7**. The timing-free JSON reproduced byte-for-byte.

Disposition: retire the explicit sparse-exception representation. A successor
must derive a compact dense correction rule and an online evaluator before
examining scalar-labelled data. Allocate no canonical ID from this packet.

## H12 — block-Hankel shared state and index inversion

### Mechanism and obstruction

The frozen channel family was `x`, `y`, `x^2`, `xy`, `chi(x)`, and
`chi(x-1)`. If a `d`-dimensional autonomous linear state obeys
`z_(k+1)=A z_k`, Cayley--Hamilton makes every linear output satisfy a
recurrence of degree at most `d`. Therefore the joint state dimension is at
least the maximum scalar-channel complexity. Conversely, any period-`r` vector
sequence has an `r`-state cyclic realization.

The protocol measured Berlekamp--Massey complexity on two periods for all seven
curves and generators `[u]P`, `u in {1,2,3,5}`. Two shared scalar-position
permutations preserved full observable tuples; two independent per-channel
permutations preserved every marginal. A synthetic three-state generator was
the positive control. State-to-index lookup entries and bits were charged
separately.

### Result

The positive control measured complexity three. On all 28 curve/generator
pairs, `x`, `x^2`, and both character channels had complexity exactly `r`,
while `y` and `xy` had `r-1`. Hence the minimum joint autonomous linear-state
dimension was exactly `r`, from 83 through 947. Both control families also had
exact dimension `r` everywhere, so strict control support was **0/7**.

A generic state-to-index table needs `r` entries (581 to 9,470 bits on the toy
ladder), and the hypothesis supplied no sub-square-root decoder. The state gate,
control gate, and independent index-decoder gate all failed. The timing-free
JSON reproduced byte-for-byte.

Disposition: retire the frozen autonomous linear-state model. A successor must
preregister a nonlinear state representation and a direct target-to-index
algorithm with complete advice accounting. Allocate no canonical ID from this
packet.

## H13 — generator-blind coordinate-bit grammar

### Frozen model and controls

The model used a fixed 172-term grammar: centered `x,y`, six public interval
tests, quadratic characters of eight low-degree functions, two character
ratios, all pairwise products, and an intercept. A ridge linear classifier was
trained leave-one-curve-out with no curve identifier, generator multiplier, or
fitted field constant. A point-invariant public hash split scalar-training from
scalar-held-out points.

Each fold trained on generators `[u]P`, `u in {1,2,3,5}`, then evaluated the
fully unseen curve under all four generator relabelings. Thirty-two balanced
random-label and 32 scalar-permutation refits used the same feature matrices,
class weights, coefficient budget, and supplied-label count. The frozen gate
required every generator's one-sided 99% lower advantage to reach 0.05 and its
accuracy to exceed every matched refit, on at least five of seven curves.

### Result

Across all 28 unseen curve/generator evaluations, accuracy ranged from 27.8% to
58.8%. Every 99% lower advantage was negative; the best was -5.1% on the
largest curve. No EC accuracy beat all 64 matched refits, so support was
**0/7**. The fits consumed 824--1,340 known base logs per fold and stored 172
float64 coefficients. Recursive peeling was neither authorized nor run. The
timing-free JSON reproduced byte-for-byte.

Disposition: retire the frozen grammar without feature tuning. A successor
needs a mathematical generator-covariance mechanism derived before another
labelled sweep. Allocate no canonical ID from this packet.

## H14 — baby/giant addition-kernel separation rank

The scalar orbit was reshaped as `k=a+m*b`, `m=floor(sqrt(r))`, and analyzed as
a two-variable addition kernel. Raw `x` matrices had full finite-field row rank.
Complex phase matrices needed 78%--93% of row rank for 99% energy, overlapping
shuffled and random-field controls. At rank `ceil(r^(1/4))`, median separable
Fourier-query error increased from 0.489 to 0.689 and top-16 mode recall fell
from 0.688 to 0.281 over the ladder. All full-rank reconstruction controls
passed. This measurement motivated exact displacement structure rather than a
stop.

## H15 — exact rational-addition factor and displacement

For affine `A=(u,v)`, `B=(s,t)`, direct rearrangement of the addition law gives

```
(s-u)^2*x(A+B) = a(u+s)+2b-2vt+u*s^2+u^2*s.
```

All 28 curve/generator cases verified exact denominator-cleared rank four and
rank-one second Cauchy displacement. Raw output, inverse-square denominator,
and first displacement remained full rank. Both output-control families made
the cleared matrix full rank again. The constructible four-factor storage
fraction fell from 0.844 to 0.258 along the ladder. This is an exact positive
algebraic structure, not an ECDLP solution or novelty claim.

## H16 — Gauss expansion on the rank-four numerator

The quadratic character cancels the square denominator, and its nonzero
additive Fourier coefficients all had magnitude `sqrt(p)` exactly to recorded
precision. At `ceil(sqrt(p))` modes, retained energy fell from 11.0% to 3.4%,
median matrix error was 0.946--0.985, and median rectangle-spectrum error was
0.905--0.969. Deterministic truncation reached 90% sign accuracy near `p/2`
modes; matrix error below 0.25 used the full `p-1` budget. Random-mode and
balanced-function control distributions are retained in full. The next
experiment is direct summation of individual bilinear phase terms from H15's
four factors.

## H17 — direct four-factor phase summation

Direct cells, full-feature aggregation, residue/DFT batching, and a four-factor
Hadamard construction agreed exactly on 28 elliptic and 56 permuted-feature
cases. Full feature tuples never collided. Phase 99%-energy rank fractions had
the same median, `0.857143`, for elliptic inputs and controls; rank-capped tensor
recompression had median matrix error `0.815288` versus `0.807678` for controls.
The exact residue histogram still visited every cell once, but when all
additive modes were requested its modeled work ratio fell from 0.384 to 0.052
over the curve ladder.

## H18 — joint residue/scalar-frequency transform

A mixed-sign 2D transform exactly reconstructed every sampled `(t,q)` phase
and the complete all-`q` quadratic-character spectrum. Its joint support used a
median 96% of cells, dense state expanded from 93 to 895 entries per cell, and
dense 2D work was 1.91--1.96 times the repeated one-dimensional route. The
singular-free step-one rectangle covered only 21.7% down to 6.4% of scalar
sums, motivating a different layout rather than a denser transform.

## H19 — full-coverage sparse singular correction

The masked quotient/remainder layout covered every scalar exactly once. Across
all 28 curve/generator cases, the rank-four character formula held away from
exactly two cells: one doubling at scalar 2 and one inverse pair at scalar 0.
Adding those two explicit corrections reconstructed the full character orbit
and its DFT exactly. Correction relative L2 fell from 0.158 to 0.046 across the
ladder. This is an exact positive algebraic representation, not yet a fast
nonlinear evaluator.

## H20 — target-translated collision decoder

Translating the giant side by `Q=[k]G` makes a same/inverse point collision emit
`k=+/-a-o-m*j`. Every one of 9,096 nonidentity targets was recovered with
`floor(sqrt(r))` baby points and `ceil(r/m)` translated giant points; the
full-coverage mask guaranteed one inverse collision. Permuting the giant
points' scalar labels reduced median recovery to 11.1%, declining to roughly
6% on the largest curve. All 420 sampled translated rank-four/correction
systems were exact. This positive decoder is the standard signed, shifted
baby-step/giant-step meet-in-the-middle mechanism and is retained as a control,
not claimed as novel.

## H21 — streaming resultant decoder

An injective `F_(p^2)` point encoding supports a streaming characteristic
product, derivative, and label numerator. Their quotient at a root recovers the
giant label without a point-equality table. After a cross-ring audit added every
integer lift `g0+j*p<r`, all 9,096 targets still recovered with zero derivative
or subfield failures. The decoder used a 12-field-element working set and
10,636,080 total factor updates. It emitted 936 extra lifts, including 344
validated high-label roots. This is a constant-memory, linear-work
reformulation of the collision control, not an exponent improvement.

## H22 — hashed moment sketches

Exact singleton and two-item `F_(p^2)` moment buckets replaced pair streaming
with sketch inserts and baby probes. One full-size capacity-two sketch recovered
92.6% overall; two recovered 99.7% and missed 27 targets. Their median storage
was 146 and 292 field elements, versus 60 coordinate elements for the full H20
point table. The only configuration below that table size recovered 3.6%.
Complete recovery therefore did not accompany a storage reduction in the frozen
sweep; coupled peeling and seed search remain queued.

## H23 — capped coupled peeling and seed search

Four-element count/point-sum/label-sum cells were fitted under H20's exact
point-coordinate cap. Sequential degree-one sketches recovered all 9,096
targets by the 16-seed prefix; degree two recovered 9,093 there and all targets
by 64. Degree three still missed 10 at 256. All 27 H22 full-x2 misses recovered
by four degree-one/two seeds. Every initial and compacted storage invariant
passed. This is a repeated-hash time-memory variant of the H20 collision
decoder, not a new exponent.

## H24 — larger-order seed-success scaling

Six independently point-counted prime-order curves of order 2,083--63,799 and
12,288 sampled targets measured 59.64%, 83.45%, 97.45%, 99.935%, and 100%
recovery at 1, 2, 4, 8, and 16 seeds. One-seed recovery slope was +0.0020 per
order doubling. Exact ideal one-seed occupancy was 59.47%, close in aggregate,
while a strict per-row random-control gate held on only 9/24 rows.

## H25 — sub-cap sequential sketches

On 3,072 larger-curve targets, fixed memory fractions traded additional passes
for recovery. Full and three-quarter cap were complete by 16 seeds, half by 64,
and one-third by 256. Quarter cap recovered 3,065/3,072 at 256 seeds. All five
fractions exceeded 99%, every aggregate observed-minus-occupancy-prediction
residual was below 0.013, and no cap invariant failed.

## H26 — negation-quotient x sketches

A three-element x singleton improved early recovery but ended behind the point
baseline. A four-element x/x-square moment bucket verified the exact EC
inverse-pair identity `k=-(g1+g2)/2 mod r`: 171/171 true pair decodes validated
with zero failures. It recovered 3,069/3,072 targets, all seven point-baseline
misses, and used half the baby probes. The sequential point/x-pair union covered
all 3,072 targets at quarter-cap peak memory, but uses twice the passes.

## H27 — equal-work point/x schedules

Point-only, verified x-pair-only, and half/half alternating schedules were
compared at equal total pass budgets `2,8,32,128,512`. All three first reached
3,072/3,072 at 512 passes. Alternating failed both frozen gates, while x-pair-
only was tied or highest at every earlier prefix and used half the point-only
baby probes. Complementarity remained measurable but did not lower the first
complete-recovery threshold at fixed pass count.

## H28 — validation-backed three-element x pairs

Removing the x-square certificate allowed three-element count/x-sum/label-sum
cells. Every count-two candidate was publicly validated. The pair arm was never
worse than its singleton baseline and reached 3,072/3,072 by 256 seeds,
recovering all 13 singleton misses. At that prefix, 13,849 count-two tests
contained 318 genuine same-x tests and 13,531 false sum collisions. Complete
lifts emitted 27,748 pair candidates: 319 accepted and 27,429 rejected. The
result is a validation-for-storage trade, not a free decoder.

## H29 — seed-keyed nonlinear x-pair fingerprint

Replacing `f(x)=x` with `f_c(x)=x+c*x^2` preserved complete recovery and all
318 genuine pair passes. Rejected pair validations fell from 27,429 to 3,910.
False singleton passes limited the net scalar-validation reduction to 13.02%,
from 163,310 to 142,046. The nonlinear arm charged 396,623,872 fingerprint
field multiplications, so the frozen result is a multi-resource trade rather
than an unconditional speedup.

## H30 — one-multiplication fingerprint frontier

Fixed `x^2` and `x+x^2` fingerprints halved H29's fingerprint multiplication
count and retained 3,072/3,072 recovery plus all genuine pair passes. They used
142,142 and 142,078 scalar validations versus 142,046 for the keyed control.
Because both exceeded the keyed count, the strict frozen frontier gate failed;
the closest gap was 32 validations.

## H31 — frozen quadratic coefficient family

The complete preregistered family `f_d(x)=x^2+d*x`,
`d in {-2,-1,1,2}`, retained every coefficient result. All arms reached
3,072/3,072 and preserved 318 genuine pair passes. Final scalar-validation
counts were 142,174, 142,078, 142,078, and 141,975 in coefficient order. Thus
`d=2` passed the family gate with 103 fewer validations than `d=1` and 71 fewer
than H29's keyed arm, but charged 198,311,936 more additions than `d=1`.

## H32 — exact validation scalar paths

Every candidate's right-to-left scalar path was partitioned into addend
doublings, identity shortcuts, inverse cancellations, equal-point doublings,
and generic additions. All endpoint and partition checks passed. `d=2` used
1,151 fewer inversion-bearing operations at 256 seeds but 87 more at the
four-seed prefix, so the frozen every-prefix gate failed. This is exact
operation accounting for the originating implementation, not a universal
scalar-multiplication cost model.

## H33 — first-success sequential stopping

The H32 construction was rerun with target-level and within-seed stopping at
the first publicly validated candidate. Both coefficient arms exactly
reproduced every recovery row. At 256 seeds, `x^2+2x` used 4,456,462 inserts,
4,191,667 probes, 4,969 validations, and 88,190 inversion-bearing operations:
3.46%--4.46% of the prior full-scan charges. Average construction was 12.21
seeds per target. The `d=2` every-prefix comparison with `d=1` still failed at
four seeds, so the nonmonotone coefficient outcome is retained.

## H34 — sacrificial-bucket occupancy

A public nonuniform map routed most translated points to one heavy bucket while
holding the remaining buckets near expected load one. The corrected uniform
arm reproduced H33 exactly. Useful-singleton opportunity rose from 4.33% to
11.50%, close to its 11.57% prediction. Recovery was 648 versus 252 at one
seed and 1,884 versus 882 at four; complete recovery moved from 256 to 64
seeds. Final inserts/probes fell 59.56%/62.52% and average seeds fell from
12.21 to 4.70.

The first full payload is preserved separately because the harness duplicated
the second shuffled-control seed offset. Attack outcomes were unchanged, but
the frozen reproduction gate failed. The corrected code expanded the baseline
test to both controls, passed 101 tests, and reproduced byte-for-byte. This is
an externally preserved harness failure, not evidence to discard an
unfavorable control.

## H35 — minimum-ticket representatives

Each bucket retained the minimum-ticket x coordinate, its multiplicity, and
label sum in the same three stored elements. Exact x comparison made the
representative publicly queryable. Observed distinct-x retention was 30.80%,
matching the 30.82% prediction. Recovery rose from 648 to 1,577 at one seed
and from 1,884 to 2,896 at four; completion moved from 64 to 16 seeds. At
complete recovery, examinations/probes fell 58.17%/66.14%, average seeds fell
from 4.70 to 1.95, and false fingerprint passes plus fingerprint field
arithmetic disappeared.

## H36 — two-element packed representatives

Dropping multiplicity and retaining only selected x plus one label expanded
the cell count under the same quarter-H20 peak allocation. Equal-ticket
arrivals kept the existing label; complete lifts and both signs recovered all
13 former pair-path successes as singleton validations. Observed retention
rose to 42.63%, close to its 42.59% prediction. Recovery was 2,084/3,072 after
one seed and complete by eight rather than 16. Examinations/probes fell another
23.97%/35.52%, while validations and inversion-bearing operations rose
0.56%/0.58%; the regression is retained as part of the cost frontier.

## H37 — two-choice cuckoo representatives

Two candidate cells and deterministic augmenting-path placement raised
retention from 42.63% to 47.98%, near the 48.79% cell-capacity upper bound.
Recovery improved at one, two, and four seeds, and complete-recovery
examinations fell 5.92%. However, both one- and two-choice arms first completed
at eight seeds, so the strict primary gate failed. Bucket reads increased
76.22%; construction used 4.33 million edge visits and 4.07 million occupied-
cell displacement attempts. This is a mixed time-memory-lookup trade, not a
new ECDLP algorithm or exponent.

## H38 — label-only validation table

One-field label cells plus a charged two-bit construction-state map increased
representative retention to 58.86%. The two-pass selected-x-to-label transition
completed all 3,072 targets by six seeds rather than H36's eight. Removing the
x certificate made every emitted label require public scalar validation:
two-pass examinations rose 60.98%, validations rose 64.58-fold, and
inversion-bearing validation operations rose 69.87-fold. The mixed result is
retained; it motivates state fingerprints rather than a speed claim.

## H39 — one-bit final-state fingerprint

Reusing the already charged two-bit state map for empty/final-zero/final-one
states preserved H38 recovery, occupancy, construction, and storage exactly.
The bit rejected 48.96% of occupied queries. Label emissions fell 48.96%,
scalar validations 49.23%, and inversion-bearing operations 49.25%. All frozen
gates passed, but the decoder remains the same validation-backed signed
collision table.

## H40 — two-bit fingerprint with a three-bit state map

A wider state map encoded four final ticket classes but reduced the number of
label cells under the same peak cap. It cut validations and inversion-bearing
operations 43.08% and 43.12% relative to H39 and still completed all targets
at seed 6. It trailed H39 by 46, 19, and 2 recoveries at prefixes 1, 2, and 4,
so the frozen early-recovery and primary gates failed. Insertions rose 1.98%
and probes 7.65% by completion.

## H41 — ordered ternary construction-state reuse

H41 kept H39's table size and used all three nonempty two-bit state values as
final fingerprints. A descending-ticket, duplicate-grouped second pass made
reuse of the selected-x state unambiguous. Recovery, insertions, probes, and
persistent layout matched H39 exactly; validations fell 32.10% and
inversion-bearing operations 32.23%. The payload explicitly charges 2.75
million merge comparisons, transient sort records, and 17.04% more
construction cell reads. Every safety and primary gate passed.

## H42 — sentinel-empty quaternary state

An absent label sentinel moved emptiness out of the state map, freeing all four
two-bit codes for ticket fingerprints at H39's exact cell count. Recovery and
layout again matched H39. Label emissions fell 47.64%, validations 48.09%, and
inversion-bearing operations 48.25%; all sentinel and ordering safety counters
were zero. Reading the sentinel first forced a cell read on every query, so
combined query cell-plus-state reads rose about 25.3%. The result is a
multi-resource frontier, not an unconditional speedup.

## H43 — decoy-first sentinel lookup

Empty slots received deterministic `position mod 4` state decoys and queries
tested state before the label sentinel. Occupied behavior, recovery, controls,
emissions, validations, and scalar paths were identical to H42. Decoys rejected
48,132/64,262 empty probes before a cell read; final cell reads fell 73.76% to
56,328 and combined query reads were 271,007, 7.01% below H39. Logical and
packed decoy initialization remain charged. This optimizes lookup constants
inside the same square-root collision decoder.

## H44 — public target-point seed audit

The inherited seed helper mixed the harness's known target scalar into each
deterministic hash instance. H44 retained H43 as an exact reference but removed
`target_scalar` from public construction, seed, and lookup signatures. Hash
parameters were derived from canonical public curve, generator, target-point,
degree, and seed-index data. Metadata-invariance tests passed and the attack-
side scalar-read counter stayed zero.

The public arm recovered 2,535, 2,987, 3,054, 3,070, and 3,072 targets at
prefixes 1, 2, 3, 4, and 6, passing every frozen gate. Relative to H43 it used
1.28% more seeds, 6.00% more probes, 3.66% more validations, and 4.39% more
inversion-bearing operations. Combined query reads remained 1.76% below H39.
This establishes one frozen public deterministic instance, not seed-family
robustness or a new ECDLP exponent.

## Remaining preregistered cards, not results

The active continuation has one next proposal. It has no result and is not a canonical candidate:

- an eight-salt public seed-robustness ensemble that preserves H44's data-flow
  audit and measures recovery/work variation without choosing a salt after
  inspection (H45, frozen in `ea1e699`).

They are included here only to prevent parameter-tuning regressions and to identify possible future mechanism gates. Nothing in this packet is a breakthrough or promotion.
