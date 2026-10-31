# Terminal machine supplement — 2026-10-31

This adds the terminal evidence for the Lean machine and statement-fidelity joint of `TASK-20261031-43dc46`. The initial `review.md` and `review_attestation.yaml` remain frozen. No local Lean build or new hosted job was run.

## Result

The existing [Lean run 41191503149](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41191503149) completed **successfully**. Its `formal workspace (lake build + axiom audit)` job 124509229264 completed successfully and uploaded [artifact 13039453747](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41191503149/artifacts/13039453747), `formal-verification-receipts`. The artifact's named receipt, `lastfall-is-max-degree-fall.json`, reports `machine_verified`, `build_passed: true`, `axiom_audit_passed: true`, and `forbidden_constructs: []` for `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall`.

The named audit printed the elaborated type. It has exactly the explicit premises `(lastFallSet F).Nonempty` and `∃ f ∈ Ideal.span F, f.totalDegree < degreeFall F f`, and concludes `IsGreatest` for the set of attained fall degrees. The transitive axiom collector reported `[propext, Classical.choice, Quot.sound]`, the gate's three permitted standard axioms. The project-wide audit reported 795 theorems with standard axioms only. These observations supply the machine evidence pending in the initial report. Its independent, conditional statement-fidelity analysis and mathematical controls remain as written.

## Custody and source coverage

| Evidence | Value |
| --- | --- |
| Producer PR head / run `headSha` | `5c405f05539649cffb7f796ac586db65cdde1661` |
| CI checkout and receipt `source_commit` | `c8a52a45d8dc595be549f70722391e186d3b7f19`, GitHub's PR merge commit; its second parent is the producer head |
| Artifact ZIP size and SHA-256 | 823,553 bytes; `6f281222cb13fd52c19f2d8c1cdf68ec50600e352b1fda63190710928eed588f` |
| Named receipt SHA-256 | `a3cdc1a3ed20e7a5a9eec6c94a0db8884cb74de593abfde96520059fd051dca4` |
| Full formal-workspace job log SHA-256 | `5b8754edb5dd14fc07d83137da1299fdcf060b69e5a003dffd5a08f29e427947` |
| Target source SHA-256 | `1e7f005567847e46e4dc23a5649d29453a9d8b87b1a7fed1889f633c3d8b841b`, equal in receipt, workspace input inventory, and producer Git tree |
| Target spec SHA-256 | `de67d2e70c5da351f93f10505f6238450d4b7e9676c57e89c920fc4b354df085`, equal in receipt and producer Git tree |

I compared all receipt input hashes with the producer head: all 71 tracked workspace source/config inputs and all 10 verifier Python inputs match, with no mismatch. The remaining workspace input is generated `CryptoResearch.lean`; independently rendering the producer tree's 55 `CryptoResearch/` modules gives its receipt hash `6dd09ff7b0151850de06cf13d450af397887b1eebb3d9aec704aea86c2e6ee9d` and includes `CryptoResearch.FallDegree.LastFall`. The hosted job log explicitly records `Built CryptoResearch.FallDegree.LastFall` at line 600, starts the named target verification at line 1700, and lists its successful result at line 1853. Thus the PR merge checkout did not substitute different named source, spec, workspace, or verifier bytes for the reviewed producer head.

The verifier explicitly runs `lake build +CryptoResearch.FallDegree.LastFall` even if the project root omits the module, then runs the project audit and a transient named audit that confirms the declaration is a theorem, collects its transitive axioms, prints its elaborated type, and fails on any axiom outside the three allowed. The named receipt's `audit_log` contains `target axiom audit passed` and the printed type and axioms. The dependency-pin receipts before and after the proof checks are byte-identical and report clean installed source revisions matching the manifest, including Mathlib `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`.

The project audit enumerates theorem declarations under the `CryptoResearch` namespace; it is not a blanket audit of every external declaration. The named audit covers this exact declaration. Input inventory excludes `.git` and `.lake` infrastructure and includes the local Lean sources/configuration outside them. Dependency binaries and cached `.olean` files remain in Lean/Lake's normal trust boundary: the receipt explicitly says `binary_or_independent_kernel_recheck: false`. No `lean4checker --fresh` result is claimed. The run also marks semantic review pending; this supplement supplies machine evidence only and does not turn adjacent declarations or measured Macaulay profiles into reviewed claims.

## Reproducible references

- Full log: [formal-workspace job 124509229264](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41191503149/job/124509229264), especially lines 600, 1700–1701, 1853, 1873–1876, and 1918–1922. The exact selected lines and full-log hash are retained in `raw/terminal-20261031/machine-reconciliation.json`.
- Full receipt artifact: [artifact 13039453747](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41191503149/artifacts/13039453747), member `lastfall-is-max-degree-fall.json`. The extracted named receipt, dependency-pin receipts, terminal run metadata, and producer/CI merge reconciliation are retained under `raw/terminal-20261031/`.
- The downloaded ZIP hash equals the upload SHA-256 printed in job-log line 1918. The full ZIP and job log are referenced by their hosted URLs and hashes; the compact named evidence is kept in Git under this task's write scope.

**Updated machine status for this joint: passed.** Statement fidelity remains `faithful_scoped` for the conditional invariant theorem, with the exact assumptions and mathematical controls in the initial report. This does not change an official scientific ledger status.
