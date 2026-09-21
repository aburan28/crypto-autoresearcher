# Static Red-Team Pre-Run Audit

Verdict: `REVISE`

Audit scope: commit `b28b813` in `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy`. This is a static audit only; no experiment, harness execution, or broad search was performed. The wider factor-base family remains `OPEN`.

## Findings ordered by severity

### 1. High — promotion gate does not charge functional advice bytes or success-adjusted `S*T^2`

Answer to question 3: **No.** The implementation computes `advice_deep_bytes` and both `s_t_squared_over_q` and `s_t_squared_over_epsilon_q` in `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py:314-330`, but `promotion_decisions` ignores all of them. Its gate uses support ratio, the minimum of advice-entry ratio and online-operation ratio, and offline-operation ratio only (`verify_recursive_expansion.py:762-780`). The specification likewise says “advice entries or online group operations” (`specification.json:86`), while merely listing bytes and the diagnostic among metrics (`specification.json:48-61`). The self-test explicitly accepts the entry/operation gate (`verify_recursive_expansion.py:1071-1088`).

Required fix: make the promotion predicate charge a declared functional advice-byte metric, or explicitly use a success-adjusted `S*T^2` tradeoff with a frozen denominator/normalization; add a self-test that fails if entry count alone passes while bytes or success-adjusted cost fails.

### 2. High — hash chain is incomplete and not recomputed/enforced for generator/dependency inputs

Answer to question 2: **No, not fully.** The verifier hard-codes one recursive-generator source digest (`verify_recursive_expansion.py:28-32`) and reports it (`verify_recursive_expansion.py:937-940`), but does not hash the generator source at verification time, does not hash or enforce the imported dependency `coordinate_energy.py`, and does not compare submitted manifest/source/dependency hashes. The generator dynamically imports that dependency (`recursive_expansion.py:19-35`), whose commit-SHA-256 is `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71`; no corresponding dependency hash appears in the verifier. The verifier does perform exact reconstruction/replay (`verify_recursive_expansion.py:932-934`) and strict JSON parsing: duplicate keys reject at `:968-974`, non-finite constants reject at `:977-984`, and finite float comparison is enforced at `:106-109`.

Required fix: recompute hashes from the exact committed generator and dependency bytes, bind them to the input/run manifest, and reject mismatches; retain the duplicate-key and nonfinite parser checks.

### 3. Medium — unimplemented source-control promise and undisclosed `p == 3 mod 4` bias

Answer to question 4: **No.** `specification.json:17` promises a “Source control” in which shuffled component tags must not improve support or witness validity, but the checked-in generator/verifier paths only replay source metadata and arithmetic; no shuffle control is implemented in the frozen family/control loops (`recursive_expansion.py:374-403`, `:423-442`; verifier replay at `verify_recursive_expansion.py:839-863`).

The specification also does not disclose that field-prime construction forces `p == 3 mod 4`: the verifier adjusts the candidate with `(candidate - 3) % 4` at `verify_recursive_expansion.py:153-161`; the generator delegates to the energy module at `recursive_expansion.py:62-64`. This is material because the square-root path is therefore a restricted prime-field family, not an arbitrary generated prime-field family.

Required fix: either implement and instrument the shuffled-tag control or remove the promise; state the `p == 3 mod 4` selection rule and its implications in the specification/contract.

### 4. Low — CLI reproduction is incomplete as a frozen generator contract

Answer to question 1: **Partially, therefore No for exact reproduction.** `contract.md:48-56` gives the runner command and includes `--seed`, timeout, experiment directory, and nested generator invocation, but the generator itself requires `--bit-sizes`, `--seeds`, and `--m-values` (`recursive_expansion.py:538-545`). Those required generator arguments are absent from the nested CLI. The contract instead says “no parameter overrides” (`contract.md:48`), while the actual generator has no frozen defaults for those required arguments. The specification’s frozen inputs are present at `specification.json:29-37`, but they are not reproduced in the contract command.

Required fix: include the exact generator arguments, including `--bit-sizes 12 14 16 --seeds 1473001 1473002 --m-values 5 6 8 --targets 256 --rho-trials 4 --occupancy-lambda 0.5`, or replace the nested command with the repository’s canonical frozen runner invocation.

## Question 5 — remaining coherence

Answer: **Mostly coherent, with the above qualifications.** Exact sign modes and canonicalization are explicit in the contract (`contract.md:16-18`, `:36`) and implemented by raw-size doubling plus canonical-point selection (`recursive_expansion.py:130-152`). Online search stops at the first witness per target (`recursive_expansion.py:254-270`), records the first witness (`:280-285`), and independently verifies it (`:278-279`). Diagnostic full expansion has separate counters from compiler/online work (`recursive_expansion.py:231-237`, `:316-318`), and the contract separates those phases (`contract.md:22-28`). Two seeds across three sizes yield six independent instances (`specification.json:30-37`, `:65-68`), with promotion requiring at least three instances (`recursive_expansion.py:480-501`). Rank and target descent are explicitly out of scope (`contract.md:26-27`; `handoff.md:13-16`).

The remaining concern is interpretation: the promotion gate’s actual semantics do not match the declared bytes/success-adjusted metrics, and the source-control and field-family disclosures are incomplete. Thus these coherent components do not justify `GO` until the required fixes are applied.

## Exact commit and SHA-256 evidence

- Commit: `b28b813` (`feat: add recursive expansion compiler preflight`)
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`: `2e4a9b91b4937169d21c49550c92fbfcc05be895772db188287b77a7a3a08b58`
- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`: `a51a6419bfacbcb7171b26c919781c79007ec55337aa7ab4505b1c2369ee4828`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`: `f17cb9d63eca4473d0b3ab15563a233f3252449a7d599bf1f468577a64b54275`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`: `6107a381d654affb8a28dde80794a71bce9f9d088ee35a899f5477d836bfb0e0`
- Imported dependency `experiments/EXP-ECDLP-ENERGY-001/src/coordinate_energy.py`: `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71`

## Narrow claim boundary

At most, this commit defines a toy-evidence, heuristic, model-bound preflight for recursive support expansion and split compilation on a restricted generated ordinary prime-order curve family. It does not establish a faster-than-rho method, a rank-bearing relation system, target descent, a deployed-curve result, or a general factor-base-family result. The wider family remains `OPEN`.

## Handoff: Static red-team pre-run audit

### Claim or task
Determine whether the frozen recursive expansion preflight is ready for execution under its declared controls, accounting, and verifier boundary.

### Status
REVISE

### Assumptions
- The audit is limited to commit `b28b813` and exact file:line evidence.
- No experiment, harness execution, or broad search was performed.
- A promotion signal remains a preflight signal, not an ECDLP break.

### Evidence so far
- Duplicate-key and nonfinite JSON parsing are enforced by `verify_recursive_expansion.py:968-984`.
- Exact arithmetic reconstruction and first-witness replay are enforced by `verify_recursive_expansion.py:932-934` and `recursive_expansion.py:254-285`.
- The promotion predicate omits advice bytes and both success-adjusted `S*T^2` fields (`verify_recursive_expansion.py:762-780`; `recursive_expansion.py:314-330`).
- Generator/dependency hash recomputation and dependency binding are absent; only a hard-coded recursive source digest is reported (`verify_recursive_expansion.py:28-32`, `:937-940`).

### Failure modes
- Entry-count reduction can pass despite larger functional advice bytes.
- A changed imported dependency can remain outside the verifier’s hash boundary.
- The promised shuffled-tag control is absent.
- The field-prime rule restricts the family to `p == 3 mod 4` without specification disclosure.
- The contract command omits required generator CLI arguments.

### Next concrete action
Revise the contract, specification, generator, and verifier so the exact CLI, hash chain, source control, `p == 3 mod 4` disclosure, and functional promotion metric are frozen and self-tested; then request a fresh static audit before any run.

### Artifact paths
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`
- `research/crypto_autoresearcher_exp_ecdlp_recursive_001_prerun_audit_20260717.md`
