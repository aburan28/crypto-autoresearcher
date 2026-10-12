# Analysis EXP-CERTBIN-66e167

## Observation

Stages 0–2 of EXP-CERTBIN-66e167 completed as three `completed_valid` runs, each with an `output_validated` receipt and check stdout `{"check": "pass"}`.

Stage 0 (`RUN-CERTBIN-59cf3d`) re-measured the n=19 E_0 cell: group order 523492, prime subgroup order r=130873, kernel identities on G and 3G both true, and C_eff=1145. The birthday expectation frozen before Stage 1 is E = 1145×1144/(2×130873) = 5.004393572394611. SHA-256 of `stage0/preregistered-predictions.json` is `183f6de905a4a529626965916b240a5fd31f3872fe16688e6305c07380ba525b`, matching the sidecar.

Stage 1 (`RUN-CERTBIN-a30c5b`) counted informative colliding pairs on seeds 2026100311 and 2026100312 at k=2 and k=3. The four ratios of those counts over E are 3.397014993739885, 0.999122056982319, 7.593327633065625, and 1.3987708797752467. Heaviest fibers are 3, 2, 4, and 2. The Z/rZ control (4 colliding pairs) has ratio 4/E = 0.7992976455858553. The same freeze hash is recorded. The archived label is O-MIXED. `in_band` is false, `tail_ok` is true, `zr_ok` is true, and `exponent_read` is false. r^0.05 = 1.8023639941375367.

Stage 2 (`RUN-CERTBIN-b5fa6e`) reports the n=17 nearby object with `kernel_ok` true, `n17_r_is_prime` false, and `pooled_with_n19` false. Its n=19 label copy is O-MIXED. The freeze hash is unchanged.

Each manifest records `certificate.kind: none` and `verified: true`, with the note that the run is an instrument observation and not a discrete-log or key-recovery claim. `code.dirty` is true. The four implementation SHA-256 values in the Stage-1 manifest match the blob hashes of those files at `4501e83555229e04edc588742623d3f2b4e2cd39`. The dirty summary is uncommitted Stage run artifacts.

A Stage-1 replay from a copy under `/tmp/review-certbin-66e167`, with the run directory `/tmp/review-certbin-66e167-run`, again emitted label O-MIXED. `check.py` exited 0. The repository `runs/` tree gained no new files.

## Comparison

The English labels are uniform quantifiers over every n=19 (seed, k) cell.

O-BIRTHDAY requires every ratio in [1/2, 2]. The two k=2 ratios are 3.397014993739885 and 7.593327633065625, both above 2. O-BIRTHDAY does not fire. The two k=3 ratios, 0.999122056982319 and 1.3987708797752467, do lie in the band, which is why a reading that looked only at k=3 would be false.

O-DELTA-N19 requires every ratio to be at least r^0.05 and the Z/rZ ratio to lie in [1/2, 2]. The Z/rZ ratio 0.7992976455858553 is inside the band, and the k=2 ratios exceed 1.8023639941375367, but both k=3 ratios are below that threshold. O-DELTA-N19 does not fire.

O-ARTIFACT does not fire: the Stage-0 order and kernel checks pass, Z/rZ is in band, and the freeze hash is the same on Stages 0, 1, and 2. O-IMPEDIMENT does not fire: all three receipts are `output_validated`.

The remaining frozen sentence is O-MIXED. HEUR-1’s uniform claim, that every new (seed, k) ratio lies in [1/2, 2], fails on this seed set. The exponent falsifier, which needs every cell, does not.

n=17 is not a row of that comparison. `pooled_with_n19` is false.

## Inference

The uniform HEUR-1 band is weakened on this package. The decision is `weaken`, direction `weakens`, strength `preliminary`, claim tier `toy`, proof status `empirical_only`. This is not `support`, not `reject_scoped`, and not an exponent move. The two k=2 excesses are a k-specific collision excess: the k=3 ratios stay below r^0.05, so the cells do not show a uniform delta.

## Limitation

The observation is one toy cell: n=19, r=130873, m=3, k in {2, 3}, seeds 2026100311 and 2026100312, with Z/rZ seed 2026100313. It does not transfer to m=83 or to n≥131. No discrete logarithm was recovered. Full-cost S is unset. Predecessor seeds 2026100301/02/03 are not in this package. A preliminary empirical weaken of a toy band is not a replicated or strong `reject_scoped`. Amazon Bedrock was not used. No Magma, Sage, or AUXIN path was used.
