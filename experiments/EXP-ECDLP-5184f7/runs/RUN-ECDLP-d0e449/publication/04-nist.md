P-192 and P-224 show practically similar normalized generic rho work to matched random-field controls in this fixed small-subgroup experiment.

| Prime | S/R work ratio | Marginal 99.9% interval | Matched pairs / R fields |
| --- | --- | --- | --- |
| P-192 | 0.983358 | [0.917418, 1.058089] | 116 / 89 |
| P-224 | 0.987524 | [0.926093, 1.052021] | 126 / 91 |

The study uses the actual 192/224-bit prime fields, but complete recovery is limited to 16–20-bit prime-order subgroups. It does not measure full cryptographic-subgroup ECDLP resistance. All 468 large-subgroup trials and both standard-curve anchors censor at the frozen 4,096-call cap; that null outcome supplies no extra-resistance claim.

Source, sampling, matching, stopping and analysis froze at `6b0d33cf3d0fed77cff7520fd18801afa0eaf53b`. There are 512 uniform curve models per fixed prime, 144 independent size-matched random fields and 144 independent size-and-mod-12-matched fields per case, four models per control field: 576 random fields and 3,328 unconditional main models in total. Prior Solinas observations stay separate.

500,000 whole-control-field bootstrap replicates provide approximate marginal 99.9% intervals; reserved three-family 99.9667% primary intervals also lie in the frozen [1/1.2, 1.2] similarity band. Matching is held fixed. Repeated targets and seeds are not counted as independent fields. Curve population rates have conservative binomial-model intervals. Timing intervals cover control-field variation conditional on a fixed S median; they exclude S systematic timing error.

Validation: all 39,570 scheduled jobs completed, zero main small-subgroup rho censors, 400 exact sham/replay/transport comparisons passed, all returned scalars and collision equations verified, all 2,972 BSGS setup/search counts exact, and all 8,700 arithmetic observations output-equal. An additional report check validates all 264 actual isomorphic endpoint jobs and 1,807 complete group/curve identity rows. Both tiny-group BSGS controls complete.

The report explains coordinate reduction, subgroup order, unit rank versus elliptic rank, and the missing lifting/relation steps. Exact PARI calculations give chosen lift degrees 3 and 7, signatures (1,1) and (1,3), unit ranks 1 and 3, discriminants −23 and −816631, and explicit principal prime ideals with residue field F_p. Elliptic Mordell-Weil rank is unmeasured in this run. These lift fields do not determine a curve endomorphism ring.

Retained anomalies: optional SEA data were installed during point counting after four existing order/factor/primality records matched exactly; no samples or frozen programs changed, and mixed preparation timings are not security comparisons. P-192 inversion backend labels execute identical builtin code yet their median timing ratio is 5.61; the cause is unmeasured, all observations are retained, and primary operation-count results use no timing data. Initial engineering failures and their corrections are also retained.

Review entry points: `experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449/report/report.md`, visually inspected four-page `report/report.pdf`, `analysis/summary.json`, `manifest.json`, frozen `contract.json` and `source/`, raw phase outputs, and artifact hashes. No independent scientific review, sealed bound or research-state promotion is claimed.

Base: `run/solinas-prime-resistance-20261011`. Head: `run/nist-prime-resistance-20261011`. Ready for review; merge commits only after CI passes.
