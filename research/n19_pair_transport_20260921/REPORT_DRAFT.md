# Native orbit-canonical pair lookup: finite N19 result

The primary x-only orbit-canonical implementation completed all fixed targets with exact recovered witnesses and used 0.750927 times the expanded table's cold native-process wall time on the preregistered statistic. That is 24.9073% less time, or a 1.33169-fold speedup. The descriptive stratified bootstrap95% interval for the ratio is[0.655143,0.864423]. Independent review is still required before Coordinator acceptance; this draft makes no official status transition.

The comparison fixes K1/F2^19, modulus z^19+z^5+z^2+z+1, prime subgroup order262543, and the previously accepted152point affine-orbit base. Both methods represent exactly the same pair-sum set and exact-three-point relation. The experiment contains eight fixed public target cases, four decomposable and four nondecomposable, with six fresh technical repetitions per arm. All six arm orders occur for each target. The 144 measurements are technical repetitions on eight targets, not144independent target samples.

| Native implementation | Table keys | Anchor pair additions | Median process wall | Median CPU | Median peak RSS |
|---|---:|---:|---:|---:|---:|
| Expanded pair table|11097|11628|9.7260ms|6.0745ms|2818048bytes|
| Full-point canonicalization|293|380|7.3718ms|4.3805ms|1851392bytes|
| Normal-coordinate x-only canonicalization|293|380|7.4814ms|3.7560ms|1867776bytes|

The table reports marginal medians over48processes perarm. They do not define the primary ratio: the frozen rule first takes six-repeat medians for each case/arm and then the median of eight paired case ratios. Full-point canonicalization has a descriptive paired ratio0.784478versus expanded. X-only versus full-point has paired ratio0.949354and interval[0.805296,1.092471], so this panel does not establish x-only as faster than full-point. X-only was selected as the primary candidate before any timing was seen.

Seven of the eight primary case ratios are belowone; one is1.039978. The finding is a finite average over this declared balancedpanel, not a guarantee for every target or a uniform-population estimate. The same public cases were used in the preceding SAT pilot; this is not fresh target holdout replication.

The gain comes mainly from construction. The expanded table's median internal build is2.854396ms; x-only is0.601959ms, plus0.041667msnormal-basis and nibble-map preparation. Median query/transport/replay is0.034479msfor expanded and0.036980msfor x-only. These separate stage medians are not additive and cannot substitute for wholeprocess wall. Fullpoint query/transport median is0.096834ms. Direct polynomial squaring performs inverse transport in this implementation; no post-result optimization was applied.

The expanded comparator remains a compact inline key-to-pair-index map: an8bytekey and4bytevalue. Canonical rows use an8bytekey and48bytevalue carrying normalized points/metadata. Logical key/value payload is133164versus16408bytes, an8.116-fold reduction. This excludes map buckets, node allocation, vector/runtime storage and allocator overhead. Measured x-only median processRSS is about66.3% of expanded; it is not an8.116-fold RSS reduction.

The native controls check all524288field elements for normal-conversion roundtrip and Frobenius rotation,4457fieldproducts,4096groupbatches and full tablewitness correctness. Both293key tables agree with the11097point expanded pair sumset across all262543subgroup points. All6909target orbits agree on6189exact3successes and720absences, including first-hit thirdpoint indices, with153separate infinity/base-point queries. All152basepoint exceptions succeed; infinity doesnot. Wrongshift,wrongsign,key/summismatch,offcurve input andnoninvariantbase controls reject their forgedcertificates. A separately written Python checker passed beforebenchmark admission.

Whole primary wall is direct native Popen launch through event-driven process-exit notification and sole wait4 reap. It includes native startup, input, base construction/validation, fresh normal conversion whereused, table construction, query, exact witness recovery, verification and output. There is no Python worker inside this boundary. It is therefore not directly comparable with the preceding pilot's48.5msPython-wrapped native median. No old timing is subtracted.

The measurement loop uses kqueue NOTE_EXIT rather than periodic millisecond polling. All144workers completed withoutfault,censor,watchdog,memorycap or fast-exit registration-race recovery. None lasted long enough for a50mssampledfootprint measurement; sampledfootprint remainsunavailable, while wait4peakRSS ispresent for everyworker. No OScacheflush, thermal/backgroundload invariance or portableenvironment isclaimed.

All144native worker intervals sum to1.2059595s; their entire supervisor phase took4.104262292s including source/input checks,parentvalidation,hashes andarchives. Native-control supervisorwall6.314426791s andindependent-checker supervisorwall50.473086041s arevalidation costs, not perquerytimings. Compilation andreviewerwork areseparate. Supervisor/childCPUandRSSscopesoverlapandarenotadded.

This result concerns cold single-query point decomposition on one finite base and host. It does not remeasure fullindexcalculus orPollardrho, alter the previous3.29×IC/rhogap, proveanexponentchange, or establish larger-fieldperformance. Shrinkingthetabledoesnotremoveper-targetcanonicalization costs. A next experiment must test a larger finiteparameter andrepresentativebase with construction/memory/query costs andexactwitnesscontrols before integration into afullICclaim.

Provenance: internal RUN-KIC-278e3e, scientificsnapshotc7f01acd95478bcbb4cf3c799f8b251d019d89c9, approvalDEC-20260921-70dcf4. This draft is local. PublicGitHubpublication remainsawaiting explicitapproval after automatic review rejected thepush; nopublicexporthasoccurred.
