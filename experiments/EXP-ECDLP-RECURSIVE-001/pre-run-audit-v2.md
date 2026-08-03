# Fast Closure Audit: EXP-ECDLP-RECURSIVE-001 v2

## Verdict

**GO** for the frozen toy-evidence pre-run protocol only. The wider coordinate/factor-base family remains **OPEN**. No canonical experiment was run; `review_required` remains unchanged and `approved_by` remains `null`.

## Scope and exact identity

- Audited worktree: `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy`
- Commit: `90ff031be2f32b85f34d557d4c60d22b30e6af93`
- Worktree status: clean
- Canonical run artifacts under `experiments/EXP-ECDLP-RECURSIVE-001/runs/`: none

Exact SHA-256 hashes:

| Artifact | SHA-256 |
|---|---|
| `pre-run-audit-v1.md` | `8b6b3723f3198dcc607eb17b5937adab16f0305142a8ad67dd1fc484e3a933b7` |
| `revision-response-v2.md` | `4016fa253533f74bcedfa7c591071ad40b15c46817eae6baa120fe8378d82681` |
| `specification.json` | `811c5faf0a3057ebf298f940c218b0a26a861569d76165fa69515b7506ac6aff` |
| `contract.md` | `19ea43bab9ee6ae288e054e4262c287bc30d6a681b44297b1ed3546487af6e7e` |
| `src/recursive_expansion.py` | `c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d` |
| `src/verify_recursive_expansion.py` | `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552` |
| `tests/test_recursive_expansion.py` | `2f0a672afe3492f1d8342707bc0934a40cc5070e57b5591e4d7381aba51fbcef` |
| imported `EXP-ECDLP-ENERGY-001/src/coordinate_energy.py` | `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71` |

## Findings, severity ordered

### No blocking findings

1. **Closed — functional-byte gate and bypass self-test.** The verifier promotion predicate requires exact-support ratio `>= 0.8`, success-adjusted functional `S*T^2/(epsilon*q)` ratio `<= 0.8`, and offline-work ratio `<= 4.0`; promotion also requires at least three qualifying instances. The self-test mutates legacy entry/online ratios to appear favorable while the functional metric fails and requires rejection. This closes the v1 gate-bypass defect.

2. **Closed — runtime source/dependency hash chain.** The verifier recomputes both executable hashes, compares them with frozen constants, and rejects mismatches before replay. The generator emits the runtime source object, and the verifier enforces the submitted source object. The imported coordinate-arithmetic dependency is included in the frozen boundary.

3. **Closed — parser hardening.** Duplicate JSON keys and non-finite constants are explicitly rejected. The unit suite also covers Boolean/float substitution for exact integer fields.

4. **Closed — control/disclosure/commands.** The v2 text removes the unimplemented shuffled-tag promise, discloses the restricted seeded `p mod 4 = 3` field family and deterministic-square-root rationale, and gives complete generator arguments plus the verifier command.

5. **Boundary confirmed — support, witness, cost, replication.** Exact recursive supports are rebuilt; first split witnesses are separately recorded and arithmetically replayed; compiler, online, witness-recovery, diagnostic expansion, and rho costs are separated. The frozen schedule is three bit sizes, two seeds, `m={5,6,8}`, 256 targets, with promotion requiring three instances spanning two sizes and independent verification.

6. **Boundary confirmed — no overclaim.** The experiment is `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`; it does not establish relation independence, matrix rank, sparse linear algebra, individual-logarithm descent, asymptotic improvement, a faster-than-rho method, or deployment relevance. `review_required` and `approved_by: null` are appropriate before authorization.

## Fast verification

Command run, and only this suite was run:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Result: **8 tests passed**, exit code 0, in 0.796 seconds. No canonical generator, verifier run, validation command, or wider-family experiment was run.

## Required AGENTS handoff

## Handoff: v2 pre-run closure

### Claim or task
Independent fast audit confirms closure of all four v1 defects for the frozen recursive-expansion preflight.

### Status
OBSERVATION

### Assumptions
- The audit applies only to clean commit `90ff031` and the listed v2 artifacts.
- The normalized functional metric is an implementation-specific matched-control diagnostic.
- A future `GO` authorizes toy evidence collection only.

### Evidence so far
- All requested source and protocol hashes are recorded above.
- The repository fast unit suite passes 8/8.
- No canonical runs exist.
- The specification remains `review_required` with `approved_by: null`.

### Failure modes
- Small finite fields may favor the candidate.
- CPython deep-byte accounting is implementation-specific.
- Rank, target descent, and relation independence remain untested.
- The restricted `p mod 4 = 3` family is not representative evidence for the wider family.

### Next concrete action
After coordinator approval is explicitly recorded, run the exact two immutable commands in `contract.md`, preserving clean Git-state manifests; then perform independent result review before any promotion claim.

### Artifact paths
- `/Volumes/Volume/autolab/research/crypto_autoresearcher_exp_ecdlp_recursive_001_prerun_v2_audit_20260717.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/specification.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/recursive_expansion.py`
- `experiments/EXP-ECDLP-RECURSIVE-001/src/verify_recursive_expansion.py`

