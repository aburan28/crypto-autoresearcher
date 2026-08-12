# Revision response: EXP-ECDLP-RECURSIVE-002 v3

The independent v2 pre-run audit returned `REVISE` at commit `878acef`. No
canonical experiment was launched. The additive-geometry protocol survived;
version 3 changes only the execution trust, provenance, and resource boundary.

| Audit item | Version 3 response | Required falsification test |
|---|---|---|
| S0-1 mutable plan/specification | Require an external approval lock by path and expected SHA-256. The lock binds experiment ID, exact approved base commit, specification SHA, compact execution-plan SHA, complete protocol-file hashes, Python runtime, and resource policy. Approved experiments cannot omit the plan; only unapproved draft runs have a development fallback. Locked argv forbids inline `-c`, uses an absolute interpreter, and requires `-I -S -B`. | Plan removal and a clean specification-only replacement with self-consistent internal hashes must both fail. Missing isolation flags must fail before reservation. |
| S0-2 forged predecessor | Manifest protocol fields and a runner receipt bind the planned argv, metadata, timeout, launch commit, lock/spec/plan/run digests, complete artifact hashes, and predecessor receipt. Verifier launch requires committed, Git-identical generator artifacts. | A schema-valid forged `completed_valid` predecessor with correct raw SHA but wrong command/seed/receipt must fail. |
| S1-1 descendant resources | A v3a adversarial probe showed that sampling alone misses a fast new-session child. Canonical locked runs now forbid child creation with `RLIMIT_NPROC=0` under a lock-bound non-root effective UID. Process-group and observed-descendant sampling remains defense in depth. | A locked script that immediately attempts a detached child must receive `OSError`; no marker may appear after the run. A root or mismatched-UID runtime must fail before launch. |
| S1-2 post-launch mutation | Recheck commit, tree state, and every protocol hash after process-group quiescence and before artifact publication. | A child that modifies a tracked protocol file and returns valid must be invalid. |
| S2-1 hard-link aliases | Reject duplicate device/inode identities in the protocol hash list and retain path/hash checks before and after execution. | A hard-link alias of a pinned file must fail before launch. |
| S2-2 accounting language | Distinguish child wall/CPU/RSS from post-child parsing/core hashing, and explicitly exclude process-monitor helpers plus receipt/manifest publication. | Manifest/prose fields must state the measured boundary exactly and make no full-wrapper resource claim. |

## Trust boundary

No signing key is configured. A receipt hash by itself is therefore not
unforgeable against an adversary who can rewrite the repository and fabricate
all files. The enforced substitute is:

1. an approval lock outside the mutable repository, supplied with an expected
   SHA-256;
2. an exact approved Git base commit and specification/plan digest in that
   lock;
3. source and runtime hashes checked by the audited runner;
4. generator artifacts committed without protocol-file changes before verifier
   launch; and
5. a recomputed manifest/receipt/artifact chain.

The final independent audit remains the human trust anchor for the approval
lock and approved commit. This does not claim protection if the operator
deliberately executes an unaudited launcher that ignores the lock.

The lock pins the Python executable, version, executable SHA-256, effective
UID, and no-descendant policy. Child `-I -S -B` disables environment paths,
site initialization, and bytecode writes. This is not a cryptographic digest
of the operating system or every system library.

Process sampling is not claimed as kernel containment. The preserved
sampling-only failure is `pre-run-adversarial-probe-v3a.md`: 12 of 12 fast
detached children escaped observation. The canonical scripts are frozen,
single-process Python programs, and the repaired locked-run boundary forbids
them from creating descendants. This boundary requires POSIX `RLIMIT_NPROC`
and a non-root effective UID; both are bound into the external approval lock
and runner receipt.

## Preserved mathematical boundary

- Generator SHA-256 remains
  `b3c9cd083af9e838c009bf76f83ac4fd6909c4c9160fcaada122d9f0a6de95bd`.
- Verifier SHA-256 remains
  `77b45770d29835166b6dc81a91b10fc44ae6c47f55d79535a6a3a85a4f60bc48`.
- Exact first-hit, mandatory controls, charged coordinate costs, finite ranks,
  six-of-nine aggregation, and nine distinct fields are unchanged.
- Rank, relation independence, sparse linear algebra, factor-base logarithms,
  target descent, exponent fitting, and deployment remain untested.

## Review-candidate verification

These are local implementation checks, not an independent `GO`:

- all 40 repository tests passed in 13.784 seconds;
- the isolated v2 verifier self-test passed all 51 mutation cases;
- all 20 checked-in research records validated;
- all 14 execution-plan protocol hashes replayed exactly; and
- `experiments/EXP-ECDLP-RECURSIVE-002/runs` did not exist.

Frozen review-candidate digests are:

| Object | SHA-256 |
|---|---|
| specification bytes | `ee36bde578dbf4f45b452fb45f63e6e90928e3574a577ed30a669516e5c53f07` |
| contract bytes | `8c7b7baa52102d5885e86e091903691e3d269742700df5a85235dd66f581a3cf` |
| compact execution plan | `d702cafb9c7da14b68761bf0275c9555b6bae191aecfd686cca06b9fdae2f1c2` |
| compact protocol-hash list | `834acd258d46dc5e77642a97e3243516708d0d1050fc4c8977d47cc7d1a03f55` |
| generator run object | `99c8785ba3d60032467e70e21a256601744e3356c950ab288c2cdedd5ba7a5e2` |
| verifier run object | `820c1d4c23826eb278dfde0b93a8b50de5b148a7a5d379b9d8d0802fcdd4f4fc` |

No third independent audit verdict exists yet.

## Next action

Finish the v3 launcher and adversarial tests, freeze its complete hash set, and
request a third pre-run audit. If it returns `GO`, make an approval-only commit,
generate the external lock for that exact commit, and obtain a final lock/commit
check before launching run `003`.
