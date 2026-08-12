## Handoff: EXP-SGCP-EMBED-002 V14 theory review

### Claim or task

Independent pre-launch review of exact commit `371790de7418aee8b1f56b7fa872f91bbec43899`, parent `bc11b2dca2a216bab0c28ec93ed168ab271fa77e`.

The checkout was clean at detached HEAD: no tracked, staged, or untracked changes. No experiment, repository test, generator, validator, or runner was executed; no V14 density row or artifact was generated.

### Status

**GO** — scoped Theory GO only for a later, separate, non-executable, hash-complete launch-plan design.

This does not authorize that design yet, execution, a budget increase, generation of a V14 row, or promotion of the hypothesis. Fresh accounting and red-team GOs and a Coordinator decision remain required. `maximum_runs=0`.

### Assumptions

- Historical test results in `development-test-log-v14.md:31-115` are treated as committed records, not independently rerun evidence.
- Publication guarantees assume the documented controlled workspace without a hostile same-user filesystem actor.
- The operation vector is a deterministic expectation for a completed canonical matrix, not evidence that such a matrix was generated.
- Only the Coordinator may change official hypothesis or experiment state.

### Evidence so far

- **Mathematical invariance:** The parent diff changes schema/protocol labels and the publication protocol, but not the curve grid, coordinate predicates, representative compiler, optimizer, family gate, or objective. The frozen definitions remain at `specification.json:5-24,52-95`, `contract.md:30-110`, and `src/sgcp_embed_family.py:25-55,1311-1324,1790-1885`. The V14 amendment explicitly preserves the mathematical protocol at `protocol-amendment-v14.json:21-25`.

- **Exact operation vector:** Independent static reconstruction gives:

  - Prime candidates: `2 × (16 + 32 + 64 + 128) = 480`.
  - Draws: `12 + 49 + 4 + 15 + 11 + 8 + 3 + 10 = 112`.
  - Curve hashes: `3 × 112 = 336`.
  - Registered-curve point enumerations: `2 × 109 = 218`.
  - Predicate hashes: `207 + 138 + 246 + 303 + 663 + 519 + 1287 + 855 = 4218`.

  These agree with `contract.md:298-299,517`, `development-test-log-v14.md:75-77`, and `protocol-amendment-v14.json:18`. No repository implementation or expected-value fixture was invoked for this calculation.

- **Schema routing:** V14 is the sole current schema; V1–V13 are enumerated as legacy and rejected before row verification. See `src/verify_sgcp_embed_family.py:30-50,6971-7018` and the all-legacy control at `tests/test_sgcp_embed_family.py:3749-3791`.

- **Publication-ID semantics:** V14 performs destination/receipt preflight, binds the receipt to a fresh publication identifier and exact payload, and reconciles ordinary synchronous exceptions only against that exact attempt. See `src/verify_sgcp_embed_family.py:7062-7114,7354-7410,7441-7584,7637-7745`.

- **Claim boundaries are explicit:** The receipt is controlled-workspace integrity evidence, unkeyed, based on sequential rather than pair-atomic snapshots, and not a durability certificate. `BaseException`, process death, power loss, memory exhaustion, and hostile mutation are excluded. See `revision-response-v14.md:52-67`, `protocol-amendment-v14.json:27-35`, and `development-test-log-v14.md:123-128`.

- **Committed-byte hashes:** All nine hashes in `development-test-log-v14.md:19-29` match blobs read directly from exact commit `371790de7418aee8b1f56b7fa872f91bbec43899`.

| Artifact | Verified SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `8a98e94a08ad62e35630dbc6bbc36db236f66c705113f18c197a70d39ddeefbe` |
| `src/verify_sgcp_embed_family.py` | `9aa3bef0de41a01ebf0f5bf608605292ab7117eeecca288a1c056aca50a51e2f` |
| `tests/test_sgcp_embed_family.py` | `9c61fa2bb8c9ec3a09d5b9f35a378c7c529f8568d1bf8cce4245b95db95e3170` |
| `hypothesis.json` | `d8f4df40406d85381aa7c588fa6cc7877f6c88425beb5b662224b0febdbdae83` |
| `specification.json` | `ebb0735d7a1770c4c1049a201e46813247d2f983b03e258da7c297e631f121b2` |
| `contract.md` | `ef6903daf5d98ac45bdb2bd6ed8d4348816b706b7ba67f904fbfea60d673992a` |
| `protocol-amendment-v14.json` | `365b337c9fb9c43c315de00f3ba3fbdb4aafba11de69bfd439b748100ece59f9` |
| `revision-response-v14.md` | `921758f2abf4e06e4173a1fcb29fd8d5957d3b1a3e0bfc9a63d98d2d02fb9afc` |
| `source-self-review-v14.md` | `3e4d37b4db7369b129feff73545689943dd30c3df443f7eb7597baa1ceec684f` |

- **No launch authority or V14 output:** `ledger.json:126-132` has no runs; `specification.json:208-215,350` retains `maximum_runs=0` and `approved_by: null`; `research_ledger.md:29` records zero generated V14 rows and zero runs. No V14 plan, matrix, runner, decision, provenance receipt, development output, or canonical output is committed. `handoff.md:14-16,82-85` keeps both plan design and execution at NO-GO.

### Failure modes/findings ordered by severity

1. **Critical/high/medium defects: none found.** No mathematical assumption change, claim-boundary overreach, blocking circular evidence, or hidden execution authorization was identified.

2. **Low, documented receipt limitation:** Exact-attempt reconciliation does not cover `BaseException`, process termination, power loss, memory exhaustion, or hostile mutation. The receipt is unkeyed, sequential, and non-durable. This is correctly bounded rather than overclaimed: `protocol-amendment-v14.json:27-32`; `source-self-review-v14.md:66-76`.

3. **Low, documented control limitation:** The real-hard-link control establishes branch behavior only on its temporary filesystem. The standalone receipt parser is structurally separate but is not a filesystem-race or durability theorem. See `revision-response-v14.md:59-67` and `tests/test_sgcp_embed_family.py:73-189,4825-5073`.

4. **Evidence boundary:** The recorded 81 focused and 225 full-suite test methods were not rerun in this review, as required. Their runtime results remain historical committed evidence only: `development-test-log-v14.md:31-115`.

5. **Research boundary:** Frozen B4 is the only standalone complete five-field oracle; B6/B8 remain replay controls, and external runtime/resource feasibility is unmeasured. No ECDLP advantage is established: `protocol-amendment-v14.json:23-35`; `contract.md:395-410,612-617`.

### Next concrete action

Obtain fresh exact-commit accounting and red-team reviews. Only if both return GO may the Coordinator authorize a separate, non-executable, hash-complete launch-plan design bound to this exact commit and these nine hashes, while preserving `maximum_runs=0`.

### Artifact paths

- [AGENTS.md](/tmp/sgcp-v14-review-371790d/AGENTS.md:1)
- [contract.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/contract.md:1)
- [specification.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/specification.json:1)
- [hypothesis.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/hypothesis.json:1)
- [protocol-amendment-v14.json](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/protocol-amendment-v14.json:1)
- [revision-response-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/revision-response-v14.md:1)
- [source-self-review-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/source-self-review-v14.md:1)
- [development-test-log-v14.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/development-test-log-v14.md:1)
- [handoff.md](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/handoff.md:1)
- [producer](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py:1)
- [verifier](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:1)
- [tests](/tmp/sgcp-v14-review-371790d/tests/test_sgcp_embed_family.py:1)
- [V13 red-team review](/tmp/sgcp-v14-review-371790d/experiments/EXP-SGCP-EMBED-002/pre-run-red-team-review-v13.md:1)
- [ledger.json](/tmp/sgcp-v14-review-371790d/ledger.json:126)
- [research_ledger.md](/tmp/sgcp-v14-review-371790d/research_ledger.md:29)