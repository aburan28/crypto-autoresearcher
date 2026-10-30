# Classical ECDLP follow-up measurement report

The finite frozen follow-up is complete. It supplies scoped observations on a public-input decoder, projection entropy at larger toy orders and a local basis obstruction. It establishes no novel ECDLP solver, asymptotic improvement or advantage over a strong rho baseline.

- Experiment: `EXP-ECDLP-7c0b1e`; run: `RUN-ECDLP-0b7dd5`.
- Goal: `GOAL-ECDLP-0c7d6f`; hypothesis: `H-ECDLP-8dfef7`.
- Scope: classical algorithms only, without quantum computation or index-calculus relations. Same-session implementation and analysis; no independent scientific review.
- Question: do the pilot's projection gaps persist on fresh larger curves, do public terminal feature labels support a concrete ladder decoder, and what exact local basis statements survive an expanded audit?
- Workload: 24 fresh ordinary curves, subgroup orders 139–4,001 at 8/10/12 bits; 192 public targets, 90 kernels, 2,880 target cases, 144 projection rows and 504 basis rows. Six fifth-residue NAs are retained in each relevant module.
- Revision measured: `f0ac7434a55fba113e7f81d3e1c8c0f62e47bbc9`; C++20, `g++ (Debian 14.2.0-19) 14.2.0`, strict warnings and `-O2`. Exact arguments, source/binary digests and self-tests are in the [sealed raw result](../../runs/RUN-ECDLP-0b7dd5/raw-result.json) and [environment](../../runs/RUN-ECDLP-0b7dd5/environment.json).
- Frozen plan SHA-256: `deb151b22d39d8f42ca4eac8a58b0a5e8555b0c89c7a3caa5bdd8cc53221eeef`.
- Resources: four allocated CPU cores, five jobs, at most three simultaneous module workers plus driver. Builds and self-tests precede the worker pool; no nested module threads.
- Timing: started 2026-10-25 06:51:10.594266 UTC; command completed 06:53:12.390064 UTC (121.795798 s); output checking completed 06:53:15.309601 UTC (124.715335 s total supervisor envelope). All jobs exited successfully, with no watchdog censoring.
- Custody: all 348 declared run files remain sealed; raw files published in commit `d8853d45` before the archive receipt. The unchanged `GitRepositoryVerifier` validated 349 paths including the receipt at archive commit `3e6ca92887e07e4d9a1710eddd8c450e70fc86fa`.
- Public verification manifest SHA-256: `067fa27e5ba4835575cda9c04dca590459b21d436679a5ca7918a97de1f14390`. A separate Jacobian implementation and recompilation/replay verified the public instance witnesses. This is implementation diversity, not an independent scientific review session.
- Target custody: scalar labels/seeds were excluded from decoder and verifier inputs. Separation was source enforced, not formal OS isolation. The coordinator reveals the committed exact labels/seeds separately after sealing, for reproducibility.
- Uncertainty and limits: fresh toy curves only, three subgroup sizes, 99 null draws per measured family, shared curves/targets across configurations and no cost-matched rho comparison. No p-value, fitted asymptotic exponent or speed claim is computed.

[Report PDF](report.pdf) · [Complete observations](observations.md) · [Projection summary](data/projection-summary.json) · [Decoder summary](data/decoder-summary.json) · [Runtime extract](data/runtime-summary.json).

Charts are supplied as editable SVG and PDF pairs:

- [Projection entropy](figures/projection-entropy.svg) ([PDF](figures/projection-entropy.pdf)): equal-curve mean and complete range, not confidence intervals.
- [Decoder recovery](figures/decoder-recovery.svg) ([PDF](figures/decoder-recovery.pdf)): every tested feature/mode/beam, with candidate-budget reference ticks. Constant-mode pairs duplicate the same candidates; reference expectations for nonconstant features are not asserted.
- [Heldout calibration](figures/calibration.svg) ([PDF](figures/calibration.pdf)): empirical prediction loss and fitted-kernel diagnostics.
- [Actual execution timeline](figures/execution-timeline.svg) ([PDF](figures/execution-timeline.pdf)): exact stage intervals; very short intervals have visible vertical ticks.

Run `./build.sh` to rebuild all PDFs and SVGs with Python, NumPy and Matplotlib. The script reads descriptive summaries only; it runs no EC experiment. Each PDF remains below the canonical 64 KiB data-file threshold. Local rendering caches and inspection PNGs in `.inspection/` are not publication artifacts.

Visual inspection covered every page of the seven-page report and all four single-page figure PDFs. Embedded fonts replaced an initially malformed core-font rendering; table spacing was corrected where text met a footer. The final charts and pages have readable labels and no clipped text. Machine summaries retain all cells, including zero hits and NAs. This report records observations without promoting scientific statuses.

Post-seal reproducibility: [reveal record](target-reveal.json), [exact target scalars](data/target-truth.tsv), and [exact seed record](data/target-seeds.json) match the premeasurement commitments. [Archive check](archive-verification.json), [canonical artifact policy audit](artifact-policy-audit.json), [scoped record checks](new-record-schema-check.json), and [same-session mathematical check](theory-review.md) document their separate scopes.
