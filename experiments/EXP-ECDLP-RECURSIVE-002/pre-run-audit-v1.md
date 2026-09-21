# EXP-ECDLP-RECURSIVE-002 independent pre-run red-team audit

**Verdict: REVISE. Do not approve or launch the frozen 31+31-null experiment from commit `96fcc1b`.**

This is a pre-run protocol verdict, not evidence for or against the mathematical hypothesis. No canonical evidence execution was performed. All target-repository references below are relative to `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy` at immutable commit `96fcc1b339844f0a0cadf8a5dcd1cda9c6d058dd`.

## Scope and provenance

- Audited: contract, specification, hypothesis, research question, candidate checklist, implementation note, generator, independent verifier, experiment tests, predecessor result red-team/evidence/decision, and generic harness runner/CLI semantics.
- Target worktree remained tracked-clean at the audited commit before and after review. Ignored AppleDouble sidecars were present but did not alter the tracked source or source hashes.
- Frozen source hashes independently matched:

| File | SHA-256 |
|---|---|
| `experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py` | `f2c0a9456758931c3c46651e2482330e05b76b6efb7253995c3b712572a3dc4f` |
| `experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py` | `0900818b0c4609d15d22b0ccb10645b77f804b520e0676eb0e37c016a4ba3197` |
| `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py` | `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552` |
| `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py` | `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d` |
| `experiments/EXP-ECDLP-ENERGY-001/src/coordinate_energy.py` | `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71` |

Severity scale: `S0` blocks approval; `S1` can produce a false promotion or materially misleading cost claim; `S2` limits inference or durability but does not overturn the reduced arithmetic checks.

## Risk list

### S0-1 — The canonical execution is not bound to the audited protocol

The specification is still `review_required` with `approved_by: null`, and the contract intentionally withholds the exact harness command and immutable run IDs (`experiments/EXP-ECDLP-RECURSIVE-002/specification.json:3`, `:83`; `experiments/EXP-ECDLP-RECURSIVE-002/contract.md:49-60`). That is a correct prohibition today, but it means this commit is not executable as a frozen canonical protocol and cannot receive `GO`.

The verifier hard-codes the intended data configuration (`experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py:57-69`, `:331-353`), while the generator accepts arbitrary CLI values (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:637-658`). The generic runner neither checks the command against that configuration nor requires a verifier pass; any command returning exact JSON `valid=true` becomes `completed_valid` (`src/crypto_autoresearcher/runner.py:150-185`).

The hash-control claim is also stronger than the mechanism. The verifier binds the generator, prior independent verifier, and two arithmetic sources, but not its own source (`experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py:48-53`, `:80-92`, `:423-426`). Its own hash appears only in prose (`experiments/EXP-ECDLP-RECURSIVE-002/implementation.md:15-23`). The runner records whichever clean `HEAD` is current, but does not require the audited commit or an approved successor commit; dirty execution can also be explicitly enabled (`src/crypto_autoresearcher/runner.py:59-63`, `:131-135`; `src/crypto_autoresearcher/cli.py:55-64`).

**Failure mode:** a clean later commit can alter the verifier, harness, command, or interpretation while preserving the three generator-side hashes, and the wrapper can still record a valid run.

**Required repair:** freeze both exact commands, run IDs, input path/hash linkage, timeout, metadata parameters, and allowed commits; prohibit `--allow-dirty`; externally bind the verifier, runner, specification, and contract hashes; require the second run to verify the exact SHA-256 of the first run's `raw-result.json` before any evidence record can be valid.

### S0-2 — The harness does not enforce the declared budgets or required run graph

The specification declares two runs, 900 seconds per run, 2 GiB, four CPU-hours, and an independent verifier artifact (`experiments/EXP-ECDLP-RECURSIVE-002/specification.json:5-9`, `:72-89`). The runner reads approval state but does not consume `maximum_runs`, `maximum_memory_gb`, `total_cpu_hours`, stopping rules, invalidation rules, or required artifacts (`src/crypto_autoresearcher/runner.py:104-139`). Its timeout is only the caller-supplied value (`src/crypto_autoresearcher/runner.py:150-159`), and RSS is measured after execution but never enforced (`src/crypto_autoresearcher/runner.py:227-253`).

An isolated synthetic reconstruction at this commit declared zero wall time, zero CPU, zero memory, and `maximum_runs=1`; the runner accepted two distinct runs and marked both `completed_valid`. This is a harness-semantics counterexample, not a canonical experiment run.

**Required repair:** enforce run count, timeout, memory, and cumulative CPU in the runner or a dedicated canonical launcher; reject commands not matching the frozen argv; make generator-to-verifier linkage and verifier success a validity condition rather than a prose-required artifact.

### S1-1 — The positive control can fail without blocking promotion

The contract and specification require scalar progression to compress four-term support and lose eight-term coverage (`experiments/EXP-ECDLP-RECURSIVE-002/contract.md:33-39`; `experiments/EXP-ECDLP-RECURSIVE-002/specification.json:14-17`). The generator computes `positive_control_passed` (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:500-524`) and reports an all-controls summary (`:612-615`), but family promotion depends only on candidate pass counts/spans (`:566-583`) and `valid` is unconditional (`:584-588`). A failed positive control can therefore coexist with `preflight_gate_passed=true`.

**Required repair:** a failed positive control must make the run invalid or force `preflight_gate_passed=false`; add an adversarial test that forces the control false and proves promotion is impossible.

### S1-2 — Four aggregate shuffles do not remove support-order dependence

The predecessor red team required shuffled and order-independent controls plus first-witness distributions (`experiments/EXP-ECDLP-RECURSIVE-001/result-red-team.md:41-43`, `:57-60`). The successor samples four deterministic shuffles and gates the ratio of the maximum to minimum **aggregate mean** over targets (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:204-265`, `:289-297`). It does not retain per-target scan-cost vectors, gate target-level instability, or compute an order-independent expectation. Large target-specific swings can cancel in the aggregate.

On one reduced frozen-curve reconstruction (`p=4051`, `q=4093`, `B=8`), the four-shuffle medians were encouraging: they were within `0.54%` to `1.53%` of the exact uniform-permutation expectation for the five non-control bases, with aggregate order-variation ratios `1.009` to `1.036`. This is a useful reduced control, but it is not present in the protocol and does not establish robustness over all scheduled rows.

**Required repair:** for each target, count the number `k` of successful four-support partials among `S=|4A|`; use the exact uniform-permutation first-hit expectation `(S+1)/(k+1)` for `k>0` and `S` for `k=0`, retain the per-target distribution, and gate sampled-vs-exact agreement. Keep the four preregistered shuffles as a secondary implementation check.

### S1-3 — The offline and memory model omits material work

The promotion gate charges candidate offline **group operations** against random-x (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:362-382`). The inherited `Ops` object counts curve additions/doublings and their modeled fields only (`experiments/EXP-ECDLP-ENERGY-001/src/coordinate_energy.py:18-24`, `:48-85`). It does not charge Legendre/square-root modular exponentiations in `point_for_x` (`:153-178`), coordinate-map arithmetic, or the modular inversions used by the rational-union map (`:331-360`).

The defect is observable at `p=4051`, `B=8`: random-x, x-interval, square-map, and rational-union each report the same `88` factor-base group operations and `284` field multiplications, while their recorded square-root tests differ (`7`, `6`, `13`, `4`) and rational-union map inversions remain uncounted. The hard-coded `64` bytes per lookup is likewise an undocumented traffic model (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:293-296`). CPython deep-size fields are implementation-specific, as the implementation note concedes (`experiments/EXP-ECDLP-RECURSIVE-002/implementation.md:13`).

The result document stores digests and summaries rather than the claimed factor-base/advice artifact itself (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:270-298`), which conflicts with `experiments/EXP-ECDLP-RECURSIVE-002/implementation.md:7`; reconstruction remains possible, but the durability claim must be corrected.

**Required repair:** count square-root/Legendre work and map inversions in an explicit field/bit-operation model, report per-family wall time, retain lookup counts separately from a labeled traffic assumption, enforce peak RSS, and either retain the functional artifact or say clearly that it is reconstructible rather than stored.

### S2-1 — The null and family-level language is stronger than the finite design

The percentile direction and tie handling are implemented correctly (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:301-311`, `:339-361`). Independent checks gave the expected range `1/32` to `1`, and a tied midrank example returned `0.6` in both directions. With 31 nulls, however, a no-tie support threshold of `>=0.95` resolves to rank `31/32 = 0.96875`, and a no-tie frontier threshold of `>=0.90` resolves to `29/32 = 0.90625`; exact rank and tie counts should be reported.

For a prime-order, sign-complete group, nonzero scalar sign classes `{+/-kG}` are in bijection with affine x-fibers. Random-scalar and filtered random-x therefore sample the same set-level null distribution; random-x remains valuable as a construction-cost control, but these are not two distinct structural null models. The wording “both null distributions” should say “two independently seeded samples of the same point-set null, one through the coordinate constructor.”

The literal family aggregation is correctly coded as at least six passes with all three sizes and seeds represented (`experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:566-583`). It still permits three arbitrarily severe reversals, has no family-selection adjustment across three candidate families, and does not establish a stable effect on all clean curves. The contract's statement that a null result “distinguishes random variation” is too strong (`experiments/EXP-ECDLP-RECURSIVE-002/contract.md:45-47`).

**Required repair:** retain raw ranks/ties and all nine effect rows; label the gate an exploratory finite-null screen; report a pooled/exchangeability analysis as secondary; and narrow both success and failure language to the exact six-of-nine criterion.

### S2-2 — Nine curves are not nine independently selected field moduli

Independent reconstruction of the frozen schedule produced clean, prime-order, monotone curves, but only five field primes. All three 12-bit curves use `p=4051`; two 14-bit curves use `p=15739`; two 16-bit curves use `p=62743`. The specification calls these nine independent instances (`experiments/EXP-ECDLP-RECURSIVE-002/specification.json:68-70`). They are nine distinct curves, not nine independent field choices.

**Required repair:** either require distinct field primes per seed at each size or state the exact design as nine curves over five fields and avoid treating field-level replication as nine independent observations.

### S2-3 — Existing tests establish agreement, not all semantic gates

The three experiment tests cover deterministic reduced execution, verifier self-test, and reduced generator/verifier round trip (`tests/test_null_calibrated_coverage.py:51-185`). The verifier mutation suite checks exact-document rejection (`experiments/EXP-ECDLP-RECURSIVE-002/src/verify_null_calibrated_coverage.py:483-510`). Neither suite permanently tests brute-force support cardinalities, percentile endpoint/tie ranks, 6-of-9 aggregation edges, global seed uniqueness, positive-control gating, budget enforcement, or actual curve-search rejection paths.

The frozen curve schedule exercised composite-order rejection 136 times and trace-zero rejection once, but did not exercise anomalous trace-one, singular, or special-j rejection. A reduced alternate seed did exercise trace-one and singular rejection. Because coefficients are sampled from `1..p-1`, `j=0` and `j=1728` are structurally excluded; the explicit special-j branch is effectively redundant for this generator.

**Required repair:** add permanent semantic-oracle tests for each listed gate, including injected trace-one/special-j candidates and the synthetic zero-budget/multiple-run harness counterexample.

## Controls that survived red-team reconstruction

- **Curve policy:** all nine scheduled curves independently recomputed to prime order, cofactor one, trace outside `{0,1}`, non-special j, `p mod 4 = 3`, and strictly increasing `q` per seed. The `(p,q,trace)` rows were `(4051,4093,-41)`, `(15767,15881,-113)`, `(62743,62467,277)`; `(4051,4057,-5)`, `(15739,15919,-179)`, `(62743,62969,-225)`; `(4051,4003,49)`, `(15739,15541,199)`, `(62791,62983,-191)`.
- **Seed uniqueness:** every frozen curve has 66 unique base seeds (31+31 nulls, three candidates, one control); all 594 labels were globally collision-free. On the first frozen curve, each null family also produced 31 distinct point-set digests.
- **Construction matching:** on reduced checks, all six base families matched the independent verifier constructor exactly, including full factor-base dictionaries and digests.
- **Exact support:** independent unordered-multiset enumeration matched generated `|4A|` and `|8A|`. At the first frozen 12-bit curve with `B=8`, `(four,eight)` was random `(225,1957)`, random-x `(225,1945)`, x-interval `(225,1945)`, square-map `(225,1881)`, rational-union `(225,1867)`, and scalar progression `(33,65)`.
- **Reduced execution:** the repository's three experiment tests passed. A separate one-seed, three-size, 4+4-null, 32-target, two-order-seed round trip completed in about `3.86 s` for the generator and `3.88 s` for the verifier and passed clean-curve, positive-control, rho, and exact reconstruction checks. This was explicitly nonfrozen and is not hypothesis evidence.
- **Rho and claim boundary:** rho is excluded from promotion and labeled arithmetic scale only (`experiments/EXP-ECDLP-RECURSIVE-002/contract.md:21`, `:30-31`). Rank, relation independence, sparse linear algebra, factor-base logarithms, descent, exponent fitting, and deployment are explicitly unmeasured and unclaimable (`experiments/EXP-ECDLP-RECURSIVE-002/hypothesis.json:15-19`; `experiments/EXP-ECDLP-RECURSIVE-002/src/null_calibrated_coverage.py:628-632`). No current source claim outruns those boundaries.

## Overclaim corrections

1. Replace “the verifier/source boundary is SHA-256 bound” with: “the verifier binds the generator, prior verifier, and two arithmetic sources; the current verifier hash is externally recorded but not self-enforced.”
2. Replace “support-order confounds are removed” or “order-robust” with: “median aggregate work over four preregistered deterministic shuffles, pending an exact order-independent per-target control.”
3. Replace “two structural null distributions” with: “two independently seeded samples of the same sign-complete point-set null, with random-x additionally matching coordinate-construction cost.”
4. Replace “a null result distinguishes random variation” with: “no tested family met the finite-null gate under this schedule; the cause remains unresolved.”
5. Replace “nine independent instances” with: “nine distinct curves over five field primes.”
6. Replace any unqualified “offline work/frontier efficiency” with: “group-operation-normalized toy diagnostic with uncharged square-root/map arithmetic and implementation-specific byte estimates.”
7. A successful family may be described only as passing on at least six of nine scheduled toy curves with all size and seed labels represented. It is not evidence of rank, descent, an exponent improvement, a faster-than-rho algorithm, or deployment relevance.

## Required controls before a new GO review

1. Freeze exact generator and verifier harness argv, immutable run IDs, approved commit(s), metadata, timeout, and first-result SHA linkage; externally bind verifier/runner/specification/contract hashes.
2. Enforce `maximum_runs`, timeout, memory, total CPU, clean-tree policy, command equality, and required generator-to-verifier run graph.
3. Make positive-control success mandatory for validity and promotion.
4. Add exact per-target uniform-order first-hit expectation/distribution and gate sampled-vs-exact agreement.
5. Complete factor-base field/bit-operation accounting, map inversion accounting, lookup model labeling, and memory enforcement.
6. Add permanent semantic-oracle tests for exact supports, percentile ranks/ties, seed uniqueness, curve rejection, family aggregation, positive-control failure, and harness budgets.
7. Amend field-replication and finite-null language, or regenerate a versioned schedule with distinct field primes. Any source/config change requires new hashes and a fresh pre-run audit.

## Next falsification tests

- **Cleanest provenance counterexample:** in a temporary clone, commit a verifier-only mutation while preserving generator/dependency hashes; the current runner has no audited-commit or verifier-self-hash gate. The repaired launcher must reject it.
- **Cleanest control counterexample:** force scalar progression's control predicate false while making six synthetic candidate rows pass. The repaired family gate must remain false and the run must be invalid.
- **Order counterexample:** search reduced rows where four aggregate shuffles satisfy `<=1.25` but a target-level sampled/exact ratio or exact first-hit tail is large; this directly attacks the current aggregate cancellation loophole.
- **Cost counterexample:** construct rational-union bases with many failed map/x trials but matched subgroup tests. If the current 4x group-operation gate passes while charged field/bit work does not, narrow or replace the gate.
- **Replication counterexample:** repeat the same contract on distinct field primes. If the family signal disappears, narrow the result to the original five-field schedule.
- **Later cryptanalytic gates:** only after a valid additive-geometry signal, measure relation independence/rank, linear algebra, factor-base logarithms, individual target descent, and a wider size sweep before any exponent or rho comparison.

## Handoff: repair EXP-ECDLP-RECURSIVE-002 before execution

### Claim or task

Repair the frozen protocol so that a canonical run is bound to the audited code/configuration, enforced by the harness, and incapable of promotion when controls, order robustness, or honest resource accounting fail.

### Status

HYPOTHESIS

### Assumptions

- This audit covers commit `96fcc1b339844f0a0cadf8a5dcd1cda9c6d058dd` only.
- Reduced reconstructions are correctness controls, not evidence for the candidate family.
- The 31+31-null canonical schedule has not been executed.

### Evidence so far

- Core curve arithmetic, seed uniqueness, factor-base reconstruction, exact support sizes, percentile direction/ties, and reduced generator/verifier agreement survived independent checks.
- Two S0 protocol/harness blockers and three S1 promotion/accounting risks remain.
- The predecessor's rank/descent/exponent boundary is preserved correctly.

### Failure modes

- Arbitrary or altered clean commands can be recorded as valid without exact config or verifier enforcement.
- Declared run, timeout, memory, and CPU budgets are not enforced.
- A failed positive control can coexist with promotion.
- Four aggregate shuffles can hide target-level order sensitivity.
- Uncharged square-root/map work can create a false offline-cost pass.

### Next concrete action

Create a versioned protocol amendment implementing Required Controls 1-6, freeze its exact canonical commands and hashes, run only the reduced semantic test suite, and request a fresh independent pre-run audit before approval.

### Artifact paths

- `/Volumes/Volume/autolab/research/prototypes/exp_ecdlp_recursive_002_pre_run_audit.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-RECURSIVE-002/`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-RECURSIVE-001/result-red-team.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/src/crypto_autoresearcher/runner.py`

## Pre-run verdict

**REVISE — canonical execution remains prohibited.**

The arithmetic and reduced reconstruction layer is strong enough to preserve. The protocol is not yet safe to run canonically because execution/provenance and budgets are not enforced, the positive control is nonbinding, the order metric is only four-shuffle aggregate, and the offline cost gate omits material arithmetic. A fresh `GO` is appropriate only after the required controls are implemented, source/config hashes are refrozen, and the repaired reduced tests pass under another independent pre-run review.
