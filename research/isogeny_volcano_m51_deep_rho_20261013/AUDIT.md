# Four-level m=51 rho audit

## Controlling audit result

**Execution/integrity: PASS. Inferential validity: FAIL.** The run is a valid,
complete measurement record. The predeclared A/A practical-equivalence gate
did not pass, so every primary inferential/equivalence label is withheld. This
distinction is controlling: the run is neither discarded nor promoted.

## Requirement-to-evidence status

| requirement | status | evidence |
|---|---|---|
| Preserve the 16 frozen inputs | verified complete | `sha256sum -c FROZEN.sha256` passes; manifest SHA-256 `f1cae417...add3b` |
| Execute the exact primary schedule | verified complete | 20,480 records: 12,288 inference + 8,192 A/A; 3,556 units; 3,537 models |
| Correct native solves | verified complete | every record has `ok=1`; exact counter identities and planted-scalar verification passed |
| Bind every native setup | verified complete | all 3,556 execution units have bound setup certificates; 3,537 distinct `Pgen` values were independently reconstructed, checked on-curve, and checked with `[r]Pgen=O` |
| Preserve raw certified P/B endpoints | verified complete | 30/32 selected raw `bottom_b` values differ from `bottom_orbit_rep`; 4,800 B-arm rows on those pairs instantiate the raw child, not the canonical representative |
| Build/runtime integrity | verified complete | static ELF gate passed; eight Python/C literal RNG vectors matched; 17 self-tests passed |
| Seal the run tree | verified complete | 139/139 listed regular files verified; zero missing, extra, or symlink entries after quarantine |
| Recompute statistics independently | verified complete | level means, nine estimates, SEs, max-|T| intervals/p-values, bias, leave-one-out, influence, and all four A/A rows matched exactly |
| Pass the frozen A/A gate | **failed** | A lower endpoint `-0.153035934 < -0.15`; B upper endpoint `+0.159037783 > +0.15` |
| Release inferential/equivalence labels | **withheld** | analysis status `aa_alert_labels_withheld`; every contrast label `WITHHELD_AA_ALERT` |
| Run conditional setup robustness | not triggered by protocol | A/A pass was a mandatory precondition; `setup_robustness_decision.json` records `aa_gate_failed` |
| Establish causal conductor effect or weakness | not established | noncausal native endpoint comparison; gate failed; no transfer or end-to-end accounting |

The A and B intervals extend `0.003035934` and `0.009037783` bit beyond the
corresponding margin, and all A/A intervals include zero. The failed gate
cannot distinguish bias from insufficient precision and establishes neither
drift nor its absence. The frozen rule admits no inferential conclusion from
the primary family.

## Integrity identities

- frozen input manifest: `f1cae4171cbd8a2b6e230e8ba4de1f41cc2340bdc1e67a8465952951a15add3b`;
- selection binding: `a8c1ae2f128c09157c12c87ae3b04d81a2007e2d2970133313f50114eacb07df`;
- run tree manifest: `4f1cc09059d4f61f698e3633f358324aaa26368a3e475a7ebdfb5f2ff9f179cd`;
- primary tree manifest: `ba1d08f8a1552659cf454ca2fae7a946f235310ad45b9618584a319419521fe7`;
- primary records: `ebe8e47e1b124cdb8d1e329dfe6859c79223a73cefc90091ee926afde9f514eb`;
- copied full analysis: `14f7fee5513bfc936df2d56b39b4877017f262fbf1aedf8ee0d8845f17accb72`;
- deterministic archive: `d8d334f8f4e4b14ef2f05066d6230fb2d082fb869342355d92e161fdd019059e`.

The terminal record audit found all 20,480 record identifiers unique and every
record successful. It bound all 3,556 setup certificates and reconstructed all
3,537 distinct native generators. The raw-child check is particularly material:
30 of the 32 selected `bottom_b` values are not their canonical orbit
representatives, and all 4,800 B-arm records attached to those 30 pairs used the
Frobenius conjugates of the certified raw child. Thus the benchmark did not
silently substitute the population-identity representative for the certified
edge endpoint.

## Post-seal cache incident

After the scientific run had sealed—and after the deterministic archive had
already been created—an audit found one unmanifested file in the live run tree:

```text
inputs/__pycache__/analyze.cpython-312.pyc
size: 128069 bytes
SHA-256: 05f481604d93922e6ab61042aef67347b3de1685982de5ded602a1d310a0bd4c
observed birth time: 2026-10-13T13:20:44Z
```

The file was created when a delegated replication-sizing audit imported the
frozen `inputs/analyze.py` through `importlib` without Python `-B`. The file was
moved, recoverably, to
`/tmp/m51-rho-postseal-quarantine-20261013T132044Z/analyze.cpython-312.pyc`.
No manifest-listed byte changed. After quarantine, the live tree
again contained exactly the 139 files listed by its root manifest, every hash
passed, and no symlink or extra file remained. The independently produced
archive and its extracted audit copy never contained the cache. This incident
therefore records post-seal audit contamination of the live directory, not
contamination of the archived scientific bytes.

## Relocated replay limitation

The archive extracts and verifies at a new path, but the frozen analyzer cannot
currently replay there because the recorded cross-language RNG receipts embed
the original absolute execution path. The observed stop was
`RNG cross-language execution differs: 0`. No frozen input was patched around
that failure. Statistical quantities were instead independently recomputed
from the sealed records and matched exactly. The limitation remains a tooling
obligation: a future additive replay adapter would need to validate relocation
without weakening receipt checks.

## Host zombie audit

The pre-launch host baseline was 5,521 zombies. The post-run count was 5,524;
the three new entries were PID-1-owned `git` zombies born at `12:31:23`,
`12:51:48`, and `13:01:24` UTC. No rho runner child or native worker descendant
was left behind; the scientific run's attributable zombie delta was zero. The
existing PID-1-owned zombies cannot be reaped from inside this process
namespace and require an environment/namespace restart. This is operational
host state, not a scientific metric.

## Claim boundary

The allowed observation is a bounded association in calibrated native
`walk_ops` for this implementation, selected endpoint set, action, schedule,
and accounting interval. No map was evaluated. There is no causal conductor,
weak-curve, transfer, end-to-end, or security-bit claim. A fresh preregistered
replication is required for additional inference and cannot retroactively
change this run's failed gate.

## Residual audit limitations

- A successful row stores `ok=1` but not the recovered `kk` value or a complete
  collision transcript. The runner checked recovery online, but the terminal
  audit cannot re-derive every scalar solely from a stored collision witness.
- Setup certificate hashes and generators were checked, but the audit did not
  regenerate every full native lookup table byte for byte.
- Worker receipts do not retain child PIDs, so process-lineage evidence comes
  from the runner's cleanup checks and host-state audit rather than persistent
  PID records.
- Analyzer receipts bind the original absolute path, preventing a direct
  relocated analyzer replay as described above.
- The rho archive binds discovery selection/certificate hashes, but does not
  embed the separate discovery archive's full certificate bodies. Rechecking
  the degree-271 cyclic-kernel certificates therefore also requires the
  discovery evidence pack.
- No evaluator or dual was serialized; subgroup transport, exceptional points,
  map evaluation, recovery, and complete transfer cost remain untested.
