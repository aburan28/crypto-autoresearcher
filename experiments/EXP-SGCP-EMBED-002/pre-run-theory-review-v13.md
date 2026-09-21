# Findings

No launch-plan-design blockers found.

- Mathematical/evidence defects: none.
- Implementation defects: none identified by static inspection.
- Wording defects: none requiring revision. V13 removes the unsupported real-exFAT claim and qualifies zero-artifact wording appropriately.
- Scope remains frozen: no generated V13 density row, canonical matrix, runner, launch plan, execution, budget increase, or ECDLP claim is authorized.

Repository provenance is confirmed:

- Detached `HEAD`: `e44edde4231604abd76e481b7b4ed90359e42d09`
- Direct parent: `4386d9722468fde9d963e1bc7e39fca7935463cb`
- Worktree and index: clean; no tracked or untracked changes reported.
- No files were modified. I did not execute the producer, verifier, tests, or experiments.

# Mathematical and scope checks

V13 faithfully repairs the V12 publication/state findings without changing the mathematical predicate, compiler, gate, or evidence boundary.

- The verifier’s only current input schema is V13; the explicit legacy set contains all V1–V12 schemas at [verify_sgcp_embed_family.py:30](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:30). Legacy routing returns no row reports and states that no mathematical checks executed at [verify_sgcp_embed_family.py:7005](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7005).
- The frozen density control remains exactly `p=19,a=2,b=9,q=23,B=4`; exactly three transient, noncanonical legacy semantic rows remain at B4/B6/B8 [development-test-log-v13.md:6](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/development-test-log-v13.md:6).
- The budget records 17 historical rows, zero additional V13 rows [specification.json:113](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:113), and `maximum_runs=0` [specification.json:206](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:206).
- Producer changes are confined to V12→V13 schema/protocol labels, error text, and the family-gate version label. Its mathematical routines are unchanged.
- Verifier mathematical changes are likewise renames/version labels; substantive additions are state-lifecycle and publication-boundary code.
- The curve grid remains 5–8 bits, seeds 101/211, B4/B6/B8, three coordinate families, and four null replicates [verify_sgcp_embed_family.py:65](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:65).
- The representative compiler remains `lexicographically_least_formal_per_nonidentity_2F_output_v2` [verify_sgcp_embed_family.py:50](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:50).
- The exact 168-row/672-cap objective and exactness policy remain frozen [specification.json:8](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:8), [specification.json:72](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:72), [specification.json:81](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:81).
- The positive gate changes only its version label [specification.json:231](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/specification.json:231).
- Claim taxonomy remains `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`, and `NOVELTY-UNVERIFIED`. Relation generation, rank, linear algebra, target descent, preprocessing crossover, rho improvement, exponent, deployment relevance, and ECDLP results remain explicitly excluded [contract.md:580](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:580).

# Independent vector

Using the fixed grid and public transcript accounting rules:

| Counter | Independent derivation | Total |
|---|---:|---:|
| Prime candidates | `2 × (2^4 + 2^5 + 2^6 + 2^7)` | 480 |
| Curve draws | `12+49+4+15+11+8+3+10` | 112 |
| Curve hashes | `3 × 112` | 336 |
| Point enumerations | `2 × (12+47+4+14+11+8+3+10)` | 218 |
| Predicate hashes | `72 + 150 + 12 × (15+9+18+23+53+41+105+69)` | 4,218 |

For predicate hashes:

- Least-x contributes zero.
- Single-Mobius contributes `24 × 3 = 72`.
- Two-Mobius contributes `50 × 3 = 150`.
- Null rows contribute `12 × 333 = 3,996`.

The completed canonical vector is therefore:

`480 / 112 / 336 / 218 / 4,218`

This agrees with the committed accounting contract [contract.md:280](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:280). The verifier’s corresponding transcript-only formulas are at [verify_sgcp_embed_family.py:637](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:637).

# Publication semantics

The new protocol is logically coherent for its stated controlled-workspace threat model.

- Data alone is unaccepted.
- The adjacent canonical receipt binds schema/protocol, experiment, exact destination basename, payload byte count, payload SHA-256, and a canonical self-digest [verify_sgcp_embed_family.py:7383](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7383).
- Acceptance is independently recoverable from visible content, rather than caller return: `publication_status` parses exact receipt keys/types and canonical bytes, verifies its self-digest, then snapshots and hashes the payload [verify_sgcp_embed_family.py:7399](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7399).
- Missing receipt plus data is `unaccepted_orphan`; malformed receipt is `unaccepted_invalid_receipt`; missing or mismatched payload is `unaccepted_receipt_mismatch` [verify_sgcp_embed_family.py:7413](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7413).
- Both destination names are no-overwrite. Receipt publication occurs only after data publication [verify_sgcp_embed_family.py:7536](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7536).
- Post-content-commit cleanup, fsync, stat, or close failures are represented as warnings rather than contradictory terminal exceptions [verify_sgcp_embed_family.py:7190](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7190), [verify_sgcp_embed_family.py:7291](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7291).
- Logical content acceptance is properly separated from durability and authentication. The documentation explicitly says the receipt is unkeyed, does not authenticate against a hostile same-user actor, and does not prove every durability syscall succeeded [development-test-log-v13.md:125](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/development-test-log-v13.md:125).

# State-lifecycle semantics

The stated lifecycle properties follow from the static control flow.

- Every public call constructs a fresh `_VerificationState`, installs it through a `ContextVar`, closes it in `finally`, then restores the exact prior token [verify_sgcp_embed_family.py:7048](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7048).
- Actual work, reservation, registered-curve cache, owner thread, worker state, and closed state are all per-call fields [verify_sgcp_embed_family.py:504](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:504).
- Semantic access checks permit identity, closed state, and owner thread before use [verify_sgcp_embed_family.py:537](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:537).
- The path-worker wrapper rejects re-entry and installs an invocation-local identity token; the body independently requires both active state and the identical token [verify_sgcp_embed_family.py:6854](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:6854), [verify_sgcp_embed_family.py:7030](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py:7030).
- Nested public calls compose correctly because each installs a new state and restores the outer token afterward. Escaping exceptions still execute both worker cleanup and public-call closure.
- Copied-context cross-thread use fails the owner check; later same-thread use fails after the shared state object has been marked closed.
- The limitation is accurately scoped: this is ordinary call isolation, not a hostile same-process Python sandbox. Same-thread introspection or monkeypatching remains outside the threat model [contract.md:191](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/contract.md:191).

# Hash check

All nine SHA-256 values in [development-test-log-v13.md:18](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/development-test-log-v13.md:18) were recomputed from `git show HEAD:<path>` bytes. All match; mismatches: **zero**.

| Artifact | Recomputed SHA-256 |
|---|---|
| `src/sgcp_embed_family.py` | `bdab1fe6766553438932ae938cf6b33b5a2c56f32d1caccceaacbc4d3a177122` |
| `src/verify_sgcp_embed_family.py` | `a12d733ceb0faed254452891d73da5f53db53833013977694eac913e463d94dc` |
| `tests/test_sgcp_embed_family.py` | `6700ee5d44377b759a7e32040fa5a46cac6414b249e53a15e9f53a5c742c79a9` |
| `hypothesis.json` | `0cc2466c4fe132ff9f52261d080fec4bb1c370b0aa501e6c618c74269eff147a` |
| `specification.json` | `2d2363d94c1b16ffa12e071af75a8ad666f44f68e25f74c0d4f3205be80b2ce6` |
| `contract.md` | `c23a5a7cea1d131ad57d1d4c68f41dece506cacf6081ee33e48b7cf0469319ea` |
| `protocol-amendment-v13.json` | `639a2a85e67c6157948287eef87f9b2db13fe932bc795bb40f11f10d48217628` |
| `revision-response-v13.md` | `21b4584b2bff5c9064051351e2a3e912085ed105b455ae0d33f26fa10c4f46da` |
| `source-self-review-v13.md` | `830ecf7838ff1c827319e9a3e8e9a0697dd9a819538f34087b2eed78297058f9` |

# Limitations

- This was static launch-plan-design review only. Passing test claims and runtime fault-injection observations were not independently rerun.
- V13 now describes `ENOTSUP` only as forced control behavior and explicitly makes no real-filesystem/exFAT support claim [revision-response-v13.md:17](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/revision-response-v13.md:17).
- Zero-artifact wording is no longer historically ambiguous: it says no generated **V13** density row, canonical matrix, runner, launch plan, or run exists, while preserving V1 artifacts as historical [revision-response-v13.md:21](/tmp/sgcp-v13-review-e44edde/experiments/EXP-SGCP-EMBED-002/revision-response-v13.md:21).
- Receipt integrity is unkeyed and therefore not hostile same-user authentication.
- Receipt visibility proves logical content acceptance, not durable persistence through power loss.
- Frozen B4 remains the sole structurally independent complete five-field oracle; B6/B8 legacy rows do not widen evidence.
- No crypto-scale, attack, asymptotic, preprocessing, rho, or ECDLP conclusion follows.

# Handoff

Theory review supports proceeding only to the launch-plan-design gate at exact commit `e44edde4231604abd76e481b7b4ed90359e42d09`, subject to the separately required accounting, red-team, and Coordinator decisions.

This GO does not authorize a generated row, canonical matrix, runner, launch plan, execution, budget increase, or ECDLP claim. `maximum_runs=0` must remain unchanged.

GO for launch-plan design only