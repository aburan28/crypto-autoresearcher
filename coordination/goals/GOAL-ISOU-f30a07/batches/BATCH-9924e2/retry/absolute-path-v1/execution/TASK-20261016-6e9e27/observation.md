# Terminal observation: EXP-ISOU-e7eeb5 / TASK-20261016-6e9e27

This report describes retained observations only. The original candidate terminated at 2026-10-16T07:56:11Z; this postprocessing task T3213 starts no scientific worker, does not retry/reclaim T3150, and changes no mathematical status.

Fixed control RUN-ISOU-13a6b5 passed exit0. Candidate RUN-ISOU-f9546d has native RESULT.json and judgement/entry.json status CENSORED, reason TIMEOUT, score null. Its outer shell raw-result.json remains the original INCOMPLETE fallback (native_exit_code3); the shell expected a top-level entry.json while the native command retained RESULT.json and judgement/entry.json. That discrepancy is preserved, not repaired. The detailed native terminal receipt supplies the phase facts below.

| Phase | Native status | Operational wall ms | Sampled worker RSS bytes | Other facts |
|---|---|---:|---:|---|
| Constructor | PASS | 131134 | 80396288 | One eigenline, PARTIAL degree coverage; one explicit map |
| Fresh independent replay | TIMEOUT | 3600019 | 153567232 | Worker exit_code null after watchdog kill; score null |

Native sampling interval25ms; RSS cap8589934592bytes; monitor grace100ms; replay unavailable-memory samples0. Empty verifier stdout and stderr each retain SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855. A timeout is a censored verifier observation, not an algebraic counterexample or nonexistence result. The map is constructed but lacks completed independent replay admission.

Exact map: experiments/EXP-ISOU-e7eeb5/runs/RUN-ISOU-f9546d/native/construction/p192/ell-50341.json, 7656861bytes, SHA256 82e3951488c793c5901ecf1dfeb3ab072b7cda16730899330df7caa9832a170c. The judgement artifact copy has the same bytes. No map is regenerated. The tool is the pinned source6547d252889ac0e1089a0497bf80f05b884ab24e executable SHA2568e0ab524008d41098a816d117d563bbefa456959bb790a78e41efc41b05e6cc1.

Executor start 2026-10-16T06:53:58+00:00, end 2026-10-16T07:56:11+00:00: derived coarse elapsed 3733s at whole-second timestamp resolution. Total CPU is unavailable. Incidental ps samples are not terminal CPU receipts. Setup/build/coordinator time is not a measured complete campaign total. The worker phase times above remain their recorded operational observations, not an end-to-end performance claim. Executor exit3 and control exit0 remain unchanged in their original files.

Custody: native-files.sha256 hashes 200 original files across both run directories; native-evidence.tar.gz preserves exactly those files, SHA256 f130a61f313a5b78e9e76aab718ebd1e41125c49547287ba2f42ab24116b63b4. Original run bytes were hashed before and after packaging with no change. Original native-wrapper.log preserves the old Conductor session/epoch7, attempts_count4, lease loss and unsupported /bin/zsh checkpoint error. The old T3150 retry capacity4/4 is not reset or bypassed. Published goal_lanes ownership and native watchdog receipts describe the retained run separately from that expired Conductor lease. No missing authorization interval is silently repaired.

Next primary expanded-track action: freeze a same-map replay profiling implementation, with durable stage markers and unchanged acceptance; charge this baseline as right-censored at3600019ms. No larger construction, scientific promotion or point speedup ratio follows. Compact M8191 remains unexecuted and its external custody-upload decision remains pending. No blocked compact binary/control payload is included in this snapshot.
