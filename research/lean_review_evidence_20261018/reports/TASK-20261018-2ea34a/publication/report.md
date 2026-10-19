# Reduced publication v1: independent Lean workflow closure review

TASK-20261018-2ea34a · J3-closure-repair-controls · 2026-10-18

**Own-joint verdict: holds within the exercised contract.** This is my independently authored, versioned reduced publication of the same completed 44 passing checks. It records no new control execution. Mathematical fidelity was not reviewed, and no scientific status was changed.

The complete public list of all 44 exact control names and results is in [checks.json](checks.json). The revised [attestation](review_attestation.yaml) references the unchanged full local read record honestly; its public source references are explicitly incomplete. The [PDF](report.pdf) and editable [diagram](diagram.dot) summarize this same bounded record.

## Availability and original identities

Automatic approval review rejected publication of the full raw bundle because it contained internal workspace inventories and a cache artifact. The original report, checks, complete read attestation, raw controls and failures remain unchanged locally. This reduced packet omits them. These hashes identify the withheld originals; they do not provide their contents, authenticate execution, or make the underlying raw evidence publicly reproducible.

| Original local record | SHA-256 |
| --- | --- |
| report.md | `757da696989c39d40fccbcd2507bbeccf76ca009f9c38dcfe38259169843aca6` |
| checks.json | `f167564a451e0e1331c890d3d0588973741a68f0d8fe41b66a6b3497875155b3` |
| review_attestation.yaml | `0cd207c170c92bce07779e60f66f5d496cf2f4c754a6b6af5c9294bff3e1dfd3` |
| artifacts/source-read-details.json | `9b6476901f0a9c316e069e8a70fc383e760237c97c529b3045515af257b2c778` |

The already-public [57-file input manifest](https://github.com/aburan28/crypto-autoresearcher/blob/3cc4b0e56ed1919c2cf523cb51ecefb33d0b90e6/research/lean_review_evidence_20261018/closure-repair-inputs.json) and [review plan](https://github.com/aburan28/crypto-autoresearcher/blob/3cc4b0e56ed1919c2cf523cb51ecefb33d0b90e6/research/lean_review_evidence_20261018/closure-repair-plan.yaml) bind public source references at authority revision `3cc4b0e56ed1919c2cf523cb51ecefb33d0b90e6`. The original session matched all 57 frozen files to the declared hashes and local immutable Git blobs. The dispatcher reported independent public retrieval without credentials; this reviewer did not repeat that network retrieval.

## Exact public candidates

| Candidate | Immutable public revision |
| --- | --- |
| review | [e0765d49bad997ae9103b8d644efa5ec9421bbe4](https://github.com/aburan28/crypto-autoresearcher/tree/e0765d49bad997ae9103b8d644efa5ec9421bbe4) |
| crypto-autoresearcher | [171f43d363d414a5faf49bf74ed39ba0a29d7b8f](https://github.com/aburan28/crypto-autoresearcher/tree/171f43d363d414a5faf49bf74ed39ba0a29d7b8f) |
| crypto-lean | [5c4f359a3c1b0430d56a36f5da09d3969479f514](https://github.com/aburan28/crypto-lean/tree/5c4f359a3c1b0430d56a36f5da09d3969479f514) |
| crypto | [3d790e41f90986eeda7a5c264ba9a6cc125240d1](https://github.com/aburan28/crypto/tree/3d790e41f90986eeda7a5c264ba9a6cc125240d1) |
| cryptanalysis | [ebf0236cbe4ea8cba35c5cf90ea001565171d3a5](https://github.com/aburan28/cryptanalysis/tree/ebf0236cbe4ea8cba35c5cf90ea001565171d3a5) |

The relevant public implementations include the [receipt validator](https://github.com/aburan28/crypto-autoresearcher/blob/171f43d363d414a5faf49bf74ed39ba0a29d7b8f/orchestration/formal/receipts.py), [CLI](https://github.com/aburan28/crypto-autoresearcher/blob/171f43d363d414a5faf49bf74ed39ba0a29d7b8f/orchestration/formal/cli.py), [source-complete gate](https://github.com/aburan28/crypto-lean/blob/5c4f359a3c1b0430d56a36f5da09d3969479f514/tools/proof-gate.sh), and [active wrapper](https://github.com/aburan28/crypto-autoresearcher/blob/171f43d363d414a5faf49bf74ed39ba0a29d7b8f/research/lean_retrospective_20261018/summarize.mjs). These selected links are not a complete source-read inventory.

## Results from the completed controls

| Boundary | Recorded result |
| --- | --- |
| Exact identity and negative diagnostics | Real fresh counted receipt accepted. Wrong-name suffix rejected; all five tested explicit failure forms appended to pass text rejected. |
| Both legitimate formats | Actual archived counted and scoped zero-axiom receipts accepted. For each format, suffix and explicit failure attacks reject through the validator and active wrapper. Each attacked wrapper exits 1 with 64 accepted and one rejected. |
| Persistent hidden sources | True baseline exits 0; initial False baseline exits 1. Hidden False-to-True mutation, addition and deletion invalidate with exit 3 and no verification object. Three supplementary controls preserve successful real-worker checks before invalidation; the target remains unchanged. |
| Auxiliary-source gate | Registered and unregistered True modules each audit two theorems. Corresponding False/sorry modules both fail FAIL_audit with sorryAx. Tested Lakefiles remain unchanged. |
| Consumer bundle selection | Each consumer passes eleven fixture/project signatures without an elan default toolchain or environment override, using its directory pin. |
| Copies, new pins, restored history | Gate, auditor and selftest copies match. Both retrospective projects pin CryptoLean 5c4f359…; ten restored historical Lakefiles match the original immutable revision and stated restoration hashes. |

The 44 checks comprise the original 41 named checks plus three supplementary real-worker controls; the two aggregate selftests include 22 fixture/project cases. Counts are descriptive coverage, not probabilities or a proof of universal tool correctness.

## Explicit historical attribution

The active wrapper accepts 65 of 66 archived targets only when explicitly selecting verifier `2951f9b77d96606820be80bf61ee0d539cfbb4dd`; one target remains undischarged. Current-verifier selection and the tested wrong exact revision each reject all 65 existing-proof receipts, accepting zero and exiting 1. These are receipt-consistency results, not fresh rebuilds of all historical theorems. They do not attribute later repairs to historical executions or authenticate those executions.

## Material limitations and deviation

The original session trusted installed pinned Lean/Lake binaries, dependency binaries, the runtime/build system and immutable input-tree assumptions. Smoke/hidden controls used Lean 4.22.0; gate controls used Lean 4.35.0; the specified Python environment reported CPython 3.12.14. No independent kernel/binary rechecker was used. Pre/post hashes detect the exercised persistent changes but cannot exclude transient changes restored between snapshots. Fabricated complete JSON can fabricate hashes and logs. Live CI, proof generation, the installed console command, a complete historical rebuild and arbitrary hostile build systems were not exercised.

The original read-scope deviation remains material: while checking wrapper shape I read lines 1–95 of the prior `TASK-20261018-695548/review_attestation.yaml`, although the handoff named only its report.md. I disclosed this immediately; the plan and handoff remain unchanged. It exposed prior J3 inventory/attestation, not current control outcomes. No current-round sibling, J1/J2/J4 or synthesis report was read. Strict adherence to the named read allowlist was weakened; a declaration-level checker pass cannot erase that deviation. The full authoritative read list remains local under the identities above.

Two retained operational failures preceded recovery: shared-clone setup exited 128 on a missing promisor object; the first recovery-only wrapper launch lacked its runtime module path and produced no summary. Scratch object/source setup and an explicit runtime module path recovered these errors. Neither failure was counted as negative mathematical or control evidence; the unchanged full local record retains their outputs.

This publication narrows disclosure, not the recorded findings or the trust boundary. It supports only the tested workflow behavior and supplies no mathematical-fidelity, execution-authentication or universal-correctness verdict. Archival responsibility remains TASK-20261018-95bdb1.
