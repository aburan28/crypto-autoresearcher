#set page(paper:"a4",margin:16mm)
#set text(size:9.2pt)

= Complete finite sampler support

#text("Observations only, 2026-10-18. EXP-ECDLP-00e491 completed both frozen trials; native statuses are output_validated. Built-in checks are not independent scientific review. Interpretation, relevance and usefulness calls remain with the owner.")

#image("support.svg",width:100%)

#text("d=3: 8 patterns, 8 Q-irreducible, 5 exact-prime eligible, 5 original-screen eligible; d=7: 24 patterns, 20 Q-irreducible, 10 exact-prime eligible, 10 original-screen eligible; d=8: 560 patterns, 489 Q-irreducible, 240 exact-prime eligible, 237 original-screen eligible; d=12: 2640 patterns, 2308 Q-irreducible, 858 exact-prime eligible, 837 original-screen eligible. These are exhaustive counts for the specified monic, constant +/-1, weight-three/five coefficient supports, k=4..12 and prime minimum 4096. Full QQ factorizations and all 29,088 prime records are retained.")

#text("What is worth inspecting: 3 degree-eight and 21 degree-twelve exact-prime-eligible, Q-irreducible patterns remain unresolved by the original modular irreducibility screen. Across all coefficient patterns, the corresponding Q-irreducible but unresolved counts are 7 and 80. A missing screen witness is not relabeled Q-reducible.")

#text("Both prime screens agree on all 29,088 eligible/ineligible value decisions. Every original positive irreducibility witness agrees with exact Q irreducibility. These agreements and unresolved cases are separate columns, not a uniformity or anomaly significance test.")

#text("Example unresolved eligible degree-eight pattern, coefficients low to high: [1, 0, -1, 0, -1, 0, -1, 0, 1]; first exact eligible k=7. All 24 eligible unresolved patterns and their exact factors are in observations.json. The source trial uses Sage 10.7 with proof-enabled primality; source-screen and exact classifications remain distinct.")

#text("Source RUN-ECDLP-ee0d23. Reproducible commands, seeds, hashes, execution-start commit, environment, child CPU and memory are in the sealed native records. No earlier G3 result or protocol was changed.")


#pagebreak()

= Fresh seeds with inputs held fixed

#text("Seven fixed inputs, twelve fresh search-seed strings each: 84 fresh jobs, plus eleven legacy-seed controls and seven identical-seed replays. No field, curve or auxiliary-prime list is regenerated when a search seed changes. All 102 prescribed jobs completed.")

#image("variation.svg",width:100%)

#text("input 1 (d=3): final D range 10..10; input 2 (d=3): final D range 2..2; input 3 (d=3): final D range 20..20; input 4 (d=3): final D range 0..0; input 5 (d=7): final D range 0..0; input 6 (d=8): final D range 0..0; input 7 (d=12): final D range 0..0. All endpoints match within each input's twelve fresh jobs, including ordinary zero-count cases. Intermediate-rung spread is retained: input 1: W=3000 D=4..6; input 3: W=3000 D=10..14.")

#text("Selection was fixed before launch: four exact archived inputs previously seen under seeds 1/3, plus the minimum canonical-JSON input key among archived seed-1 random_g cases at each degree 7,8,12. These seven conditional cases are not a random sample of all curves or fields. Distinct seed labels do not prove statistical independence.")

#text("The plot shows the median and observed min/max of twelve counts at each recorded rung. The shaded ranges are not confidence intervals; no population variance, significance label or fitted scaling exponent is supplied. Point/residue counts do not identify full point sets.")

#text("Original checkpoints occur before testing candidate W. Final after-search snapshots are saved separately. Across all 102 jobs, residue-count differences between those last two boundaries were {\"0\": 102} (difference: job count). The boundary distinction is retained even when counts happen to match.")

#text("Source RUN-ECDLP-6bd7b4. Every unique discovered point, checkpoint and shell event is retained in the indexed instrument.tar.gz bundle, with no eight-point cap. Rejected candidates are not individually logged.")


#pagebreak()

= Prefixes, controls and provenance

#text("Each input has 66 pairwise comparisons among twelve fresh jobs. These pairs reuse the same twelve jobs; they are not 66 independent samples. Point-key prefixes use coordinates, exclude event work counters and include the whole shorter list when fewer than eight points were found.")

#image("prefixes.svg",width:100%)

#text("input 1: 66 same-prefix pairs, 32 of those with different D paths, 0 different full point-set pairs; input 2: 66 same-prefix pairs, 0 of those with different D paths, 0 different full point-set pairs; input 3: 31 same-prefix pairs, 23 of those with different D paths, 0 different full point-set pairs; input 4: 66 same-prefix pairs, 0 of those with different D paths, 0 different full point-set pairs; input 5: 66 same-prefix pairs, 0 of those with different D paths, 0 different full point-set pairs; input 6: 66 same-prefix pairs, 0 of those with different D paths, 0 different full point-set pairs; input 7: 66 same-prefix pairs, 0 of those with different D paths, 0 different full point-set pairs. Full per-input trajectories and pair counts are in observations.json; all zero-difference/control behavior is retained beside differences.")

#text("All eleven legacy controls reproduce every comparable original rung field. All seven identical-seed replays have byte-identical event streams. The separate checker verified all 480 discovered point events by exact Fraction arithmetic on the curve and recomputed residues; it also replayed all support records. No independent scientific review is claimed.")

#text("Producer timing (completed operations, not performance comparisons): support wall 14.762 s, child CPU 14.710 s, child peak RSS 245747712 bytes; panel wall 61.306 s, child CPU 61.392 s, child peak RSS 54910976 bytes. Checker time is separate from those producer metrics. Exact host/platform and launch provenance are preserved in native manifests.")

#text("All requested sampler follow-ups in this protocol are complete: larger-degree finite support, fixed-input interface, fresh seeds, legacy controls, identical-seed replay, uncapped traces and separate observation views. New questions to inspect are the structure of unresolved modular-screen cases and how discovery order changes while final counts agree. These are proposed follow-ups, not additional measurements or verdicts.")

#text("Raw records were published before this report. Certificate kind remains none; hypothesis/goal scientific conclusions and historical observations remain unchanged. Local coverage() retains a hardcoded publication_verified:false field; actual publication is evidenced by Git commits/hashes and the separate archive receipt, never inferred from that placeholder.")
