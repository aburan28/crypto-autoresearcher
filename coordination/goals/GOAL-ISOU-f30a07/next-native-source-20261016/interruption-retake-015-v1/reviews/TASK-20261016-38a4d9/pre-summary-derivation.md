# Independent source/raw derivation, before producer summaries

Task: TASK-20261016-38a4d9. Saved UTC: 2026-10-16T22:49:06.525258+00:00. One assigned joint: interruption_invocation_retention_binding. No repository mutation, test, scientific executable, new build, target or benchmark has been run. Tools so far are read-only Git/source/log inspection and Python byte/JSON/hash/tar metadata inspection; writes are private notes under the assigned temporary directory.

The frozen assignment, review plans (base, additive clarification, composed), handoff, PROTOCOL, bindings and native launcher were read as the required prospective contract. Those documents contain anticipated outcomes; I derive the actual observations below from source and original raw receipts rather than treating anticipated outcomes as observations. Producer source-bindings, metadata.py, correct-log-count.py, manifests and protected reports/graphs/summary files have not been semantically read. Directory listings exposed names only. No same-round sibling report or Coordinator parent discussion has been read.

The retained 12,224-byte replay_trace.rs equals Git 015fa7bb504ef63953e0e04e464bb266f4f207bf:tools/isogeny-cli/src/replay_trace.rs byte for byte (SHA256 30fa162ab24097380e5635c3cd720680e53a76510c89dbf1bd166ddb673166a3). That commit's tree is 5af766cd338b7a4639ab52337564ebe9267a4b23, matching the retained source-tree marker. Source contract: Trace::record serializes one record, writes newline and flushes the File before returning; this is a userspace flush, not an fsync/durable-media guarantee. Session::start takes an absolute fresh ISOGENY_REPLAY_TRACE path with create_new and begins total id0/parent null. stage begins interruption_fixture_wait id1/parent0. The ignored worker returns unless ISOGENY_TRACE_CONTROL_CHILD is present, then creates the Session and stage and sleeps10 seconds, with finish calls only after that sleep. Normal finish would emit stage end, total end and COMPLETED terminal. Forced process termination prevents those finish/drop paths.

The named parent takes ISOGENY_TRACE_UNIT_EVIDENCE if present, creates that directory fresh, canonicalizes it, and selects current_exe with exact interruption_worker, --ignored and --nocapture. It sets CONTROL_CHILD=1 and REPLAY_TRACE to retained/interrupted.jsonl, redirects child stdout/stderr to retained files, polls at5ms intervals for at most5s until the fixture begin is visible, calls child.kill (discarding the kill Result), then waits and asserts observed and exactly two begin records in total/fixture order. It writes control.json with observed=true, cryptographic_work=false, unfinished_stage_marked_complete=false and status.code(); status.code()==None/null does not report a measured signal number. Retention depends on UNIT_EVIDENCE presence: absent triggers remove_dir_all; present leaves the child trace, control and stdout/stderr. The fixture contains Session/stage/sleep only, no arithmetic.

The frozen launcher selects each existing native unit parent by --exact replay_trace::tests::flushed_begin_survives_bounded_child_interruption --nocapture --test-threads=1, reference first then candidate, with hash precheck, before/after checks, gtimeout20s plus5s hard grace and /usr/bin/time -l. It unsets inherited CONTROL_CHILD and REPLAY_TRACE for each parent and sets only UNIT_EVIDENCE to a fresh absolute per-arm retained path, with LC_ALL=C. It stops on a failed reference. The two per-arm native argv and retained environment records match that contract. Both arm parent stdout files show running1 test, the sole named parent ok, and 1passed/0failed/0ignored/0measured/85filtered; exit-code is0 and stderr empty. Each child stdout is only running1 test, with empty stderr and no completion line. Each trace has exactly2 valid JSONL rows, total/begin id0 then interruption_fixture_wait/begin id1 parent0, same positive PID within the arm; there is no end or terminal record. Reference PID14894; candidate PID14915. Both controls retain null child_exit_code, observed=true and unfinished=false. The parent passed its source assertions after wait; no independent signal9 telemetry is present.

There are16 raw files per arm,32 total. Every retained raw file equals the corresponding actual external output file byte for byte. The parent receipts give reference UTC22:24:08 and candidate22:24:10 on2026-10-16; launcher22:24:07--22:24:11. OS records give0.03 real,0.00 user,0.00 sys per arm with maximum resident bytes2,850,816 reference and2,818,048 candidate. These are operational fixture observations, not a reduction/algorithm speed measurement. The 0 signals received OS field does not measure the killed child's termination signal.

Build/source/feature linkage is supported by original-clean-build source/tree markers, empty before/after Git status, build and test exit0, logs explicitly naming the exact existing unit paths, separate feature arguments and current Cargo fingerprints. Reference fingerprint features[] and candidate[cached-fixed-modulus-reduction], both rustflags[]. The original Cargo manifest default is[] and declares the optional cached feature. Current .d files include replay_trace.rs. Current unit bytes hash to bf48ea22df2d8e1c2b94f1462cde3d1c4f64737d4cf6d3bca4623d5b4bef0a9c (37,614,112bytes) reference and cdb325a657f6da2d77bb4be8d8084b4d25f3552ba891bb622bf3fdff4e4f457e (37,609,376bytes) candidate, matching prospective bindings and new before/after receipts. Launcher hash98bc11563029aa04712bbd92217529c980a217d0513deb646248c7a02cb18028; current gtimeout hash96d98cb3adafdd41570802625f7511d7d340cbcd4cb7a7278d5706c282a59c33. Current fingerprints/bytes and historical build logs support a bounded engineering chain; they are not a hermetic rebuild or retroactive invocation-time unit hashes for the older execution. Old unit tests show the interruption parent passing with the worker ignored and no saved old retention is inferred. TIMEOUT/RESOURCE_MONITOR_UNAVAILABLE and intentional write-failure panic messages remain visible in those older logs; their passing test exit is not a statement that every resource monitor operated.

Raw custody command/output logs show the exact logical evidence name, store push --no-cache, pull, remote verify and cmp, client before/after hash aab28a781f807f4f3ef364336b04d2ff18a2bb8483e1c6d1494baf5c1c3a561a, transfer exit0, uploaded=true/replaced=false and a local readback path. Independently reading every retained readback byte gives683,995bytes and SHA2563e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044, equal to the full new archive bytes. These direct byte checks establish the retained readback identity; source/build provenance of the store client is separate and has not been invented. No network action was performed by this reviewer. Archive members, all external Git paths and producer map assertions still await separate checks after this note; this note does not pre-judge that remaining custody binding.

Original clean archive hashes to09347071c8857216ae1597898d345307fc2a4086930c4252150cc0c6e2081f76 (2,049,977bytes). Its25 selected original-clean-build members independently match every retained input byte. No original report/summary was opened for that comparison. New raw recomputations are embedded below; they were saved before producer maps/checkers/manifests. The source-read inventory tracks exact byte hashes, and later phase reads will be disclosed separately. Output truncation in one large source/log dump was addressed with a second focused extraction of all relevant build invocation, feature, result and warning lines and custody records.

```json
{
  "tools/isogeny-cli/src/replay_trace.rs": {
    "bytes": 12224,
    "sha256": "30fa162ab24097380e5635c3cd720680e53a76510c89dbf1bd166ddb673166a3"
  },
  "source_equals_retained": true,
  "tools/isogeny-cli/Cargo.toml": {
    "bytes": 964,
    "sha256": "6b24fe009f5a0b956f52215e6db425c083db98a1e5287a00b14cda2a77e9c3ce"
  },
  "tree_at_source_commit": "5af766cd338b7a4639ab52337564ebe9267a4b23",
  "reference": {
    "current_executable": {
      "bytes": 37614112,
      "sha256": "bf48ea22df2d8e1c2b94f1462cde3d1c4f64737d4cf6d3bca4623d5b4bef0a9c"
    },
    "fingerprint": {
      "rustc": 12983045474342760211,
      "features": "[]",
      "declared_features": "[\"cached-fixed-modulus-reduction\", \"default\"]",
      "target": 8155962016789868214,
      "profile": 10220379689200424945,
      "path": 4942398508502643691,
      "deps": [
        [
          530211389790465181,
          "hex",
          false,
          2702858500045262307
        ],
        [
          4091053499939819895,
          "sha2",
          false,
          12301163282852665338
        ],
        [
          5157631553186200874,
          "num_traits",
          false,
          1280006019483413150
        ],
        [
          5330460842384404171,
          "serde_json",
          false,
          265776536849397182
        ],
        [
          5543998770925487919,
          "isogeny_algos",
          false,
          15590962762095086562
        ],
        [
          6557439603276904804,
          "serde",
          false,
          17127929131576636546
        ],
        [
          6960258817058176788,
          "rand",
          false,
          7813981908079778381
        ],
        [
          8841681343991089453,
          "blake3",
          false,
          16751637832065930653
        ],
        [
          11023519408959114924,
          "getrandom",
          false,
          15229142649261884204
        ],
        [
          11509331996780215580,
          "num_bigint",
          false,
          7929376516455235087
        ],
        [
          16332860131607790783,
          "build_script_build",
          false,
          860325098991038232
        ],
        [
          17003143334332120809,
          "subtle",
          false,
          9915568477630750618
        ]
      ],
      "local": [
        {
          "CheckDepInfo": {
            "dep_info": "release/.fingerprint/isogeny-cli-8734bd11e3dad22d/dep-test-bin-isogeny",
            "checksum": false
          }
        }
      ],
      "rustflags": [],
      "config": 2069994364910194474,
      "compile_kind": 0
    },
    "dep_mentions_trace": true,
    "raw_recomputation": {
      "selected": [
        [
          "replay_trace::tests::flushed_begin_survives_bounded_child_interruption",
          "ok"
        ]
      ],
      "result_fields": [
        "ok",
        "1",
        "0",
        "0",
        "0",
        "85"
      ],
      "events": [
        {
          "elapsed_ms_operational_only": 0,
          "event": "begin",
          "parent_id": null,
          "pid": 14894,
          "schema": "isogeny-replay-stage/v1",
          "stage": "total",
          "stage_id": 0,
          "status": null
        },
        {
          "elapsed_ms_operational_only": 0,
          "event": "begin",
          "parent_id": 0,
          "pid": 14894,
          "schema": "isogeny-replay-stage/v1",
          "stage": "interruption_fixture_wait",
          "stage_id": 1,
          "status": null
        }
      ],
      "control": {
        "child_exit_code": null,
        "cryptographic_work": false,
        "flushed_begin_observed_before_kill": true,
        "schema": "isogeny-trace-interruption-control/v1",
        "unfinished_stage_marked_complete": false
      },
      "parent_exit": 0,
      "raw_file_count": 16
    },
    "original_raw_equality": [
      {
        "relative_path": "build-features.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "environment.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "executable-after.sha256",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "executable-before.sha256",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "exit-code.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "finished-at.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "native-argv.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "os-time.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "parent.stderr.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "parent.stdout.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/child.stderr.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/child.stdout.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/control.json",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/interrupted.jsonl",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "source-commit.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "started-at.txt",
        "equal_to_retained_git_copy": true
      }
    ]
  },
  "candidate": {
    "current_executable": {
      "bytes": 37609376,
      "sha256": "cdb325a657f6da2d77bb4be8d8084b4d25f3552ba891bb622bf3fdff4e4f457e"
    },
    "fingerprint": {
      "rustc": 12983045474342760211,
      "features": "[\"cached-fixed-modulus-reduction\"]",
      "declared_features": "[\"cached-fixed-modulus-reduction\", \"default\"]",
      "target": 8155962016789868214,
      "profile": 10220379689200424945,
      "path": 4942398508502643691,
      "deps": [
        [
          530211389790465181,
          "hex",
          false,
          2702858500045262307
        ],
        [
          4091053499939819895,
          "sha2",
          false,
          12301163282852665338
        ],
        [
          5157631553186200874,
          "num_traits",
          false,
          1280006019483413150
        ],
        [
          5330460842384404171,
          "serde_json",
          false,
          265776536849397182
        ],
        [
          5543998770925487919,
          "isogeny_algos",
          false,
          15590962762095086562
        ],
        [
          6557439603276904804,
          "serde",
          false,
          17127929131576636546
        ],
        [
          6960258817058176788,
          "rand",
          false,
          7813981908079778381
        ],
        [
          8841681343991089453,
          "blake3",
          false,
          16751637832065930653
        ],
        [
          11023519408959114924,
          "getrandom",
          false,
          15229142649261884204
        ],
        [
          11509331996780215580,
          "num_bigint",
          false,
          7929376516455235087
        ],
        [
          16332860131607790783,
          "build_script_build",
          false,
          17100501451703371725
        ],
        [
          17003143334332120809,
          "subtle",
          false,
          9915568477630750618
        ]
      ],
      "local": [
        {
          "CheckDepInfo": {
            "dep_info": "release/.fingerprint/isogeny-cli-091b88e44789ba98/dep-test-bin-isogeny",
            "checksum": false
          }
        }
      ],
      "rustflags": [],
      "config": 2069994364910194474,
      "compile_kind": 0
    },
    "dep_mentions_trace": true,
    "raw_recomputation": {
      "selected": [
        [
          "replay_trace::tests::flushed_begin_survives_bounded_child_interruption",
          "ok"
        ]
      ],
      "result_fields": [
        "ok",
        "1",
        "0",
        "0",
        "0",
        "85"
      ],
      "events": [
        {
          "elapsed_ms_operational_only": 0,
          "event": "begin",
          "parent_id": null,
          "pid": 14915,
          "schema": "isogeny-replay-stage/v1",
          "stage": "total",
          "stage_id": 0,
          "status": null
        },
        {
          "elapsed_ms_operational_only": 0,
          "event": "begin",
          "parent_id": 0,
          "pid": 14915,
          "schema": "isogeny-replay-stage/v1",
          "stage": "interruption_fixture_wait",
          "stage_id": 1,
          "status": null
        }
      ],
      "control": {
        "child_exit_code": null,
        "cryptographic_work": false,
        "flushed_begin_observed_before_kill": true,
        "schema": "isogeny-trace-interruption-control/v1",
        "unfinished_stage_marked_complete": false
      },
      "parent_exit": 0,
      "raw_file_count": 16
    },
    "original_raw_equality": [
      {
        "relative_path": "build-features.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "environment.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "executable-after.sha256",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "executable-before.sha256",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "exit-code.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "finished-at.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "native-argv.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "os-time.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "parent.stderr.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "parent.stdout.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/child.stderr.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/child.stdout.log",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/control.json",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "retained/interrupted.jsonl",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "source-commit.txt",
        "equal_to_retained_git_copy": true
      },
      {
        "relative_path": "started-at.txt",
        "equal_to_retained_git_copy": true
      }
    ]
  },
  "launcher_sha256": "98bc11563029aa04712bbd92217529c980a217d0513deb646248c7a02cb18028",
  "gtimeout": {
    "sha256": "96d98cb3adafdd41570802625f7511d7d340cbcd4cb7a7278d5706c282a59c33",
    "bytes": 76760
  },
  "custody_recomputation": {
    "archive_bytes": 683995,
    "archive_sha256": "3e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044",
    "readback_bytes": 683995,
    "readback_sha256": "3e6ccad8ab3441f53e5f5781dc15272218884b241f300f0da0fa418d481a6044",
    "full_byte_equality": true
  },
  "old_archive": {
    "sha256": "09347071c8857216ae1597898d345307fc2a4086930c4252150cc0c6e2081f76",
    "bytes": 2049977,
    "selected_build_member_equalities": [
      {
        "member": "./candidate/build-command.txt",
        "bytes": 83,
        "sha256": "d8759674aefdb45cbae9c5b23e5bc718e50023c26604f046732986acbea2a706",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/build.exit",
        "bytes": 2,
        "sha256": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/build.stderr",
        "bytes": 9304,
        "sha256": "b06c0c2c82b388d583a49f5e014a5270422f53745467c3b955e912c99dd8dbb1",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/feature-arguments.txt",
        "bytes": 64,
        "sha256": "bbc202f7e368eae09a84dda7947140bf7f34eba838b8e3a8a59750fa75de94ef",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/git-status-after.txt",
        "bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/git-status-before.txt",
        "bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/tests.exit",
        "bytes": 2,
        "sha256": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/tests.stderr",
        "bytes": 12559,
        "sha256": "15d9c43e98ddb16f0fa0da987bf107f9daccb32582f974bc1a9c8205a49db00a",
        "equals_retained_build_input": true
      },
      {
        "member": "./candidate/tests.stdout",
        "bytes": 15425,
        "sha256": "6653824822daf2aaf180960f9d52f621282a460f250e4aa3fe61db1274343c4e",
        "equals_retained_build_input": true
      },
      {
        "member": "./explicit-build-environment.json",
        "bytes": 723,
        "sha256": "f59c4b58c984c91d02c2897b5995cb6984deeddf86c64d59719ceb75ecc67879",
        "equals_retained_build_input": true
      },
      {
        "member": "./flags.txt",
        "bytes": 97,
        "sha256": "5e90345ce9fccee2ee449a755068555c6f0398812ecda9b92821c21cb42fbdca",
        "equals_retained_build_input": true
      },
      {
        "member": "./host.txt",
        "bytes": 151,
        "sha256": "e36d53099a821e4ba5484f791025bfe67a1a2825568fd2b706aa5df6eff33892",
        "equals_retained_build_input": true
      },
      {
        "member": "./os.txt",
        "bytes": 63,
        "sha256": "28728fc359c1e375955048b222e1217021f0f6c0a936c906026e3f0311bfccbe",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/build-command.txt",
        "bytes": 83,
        "sha256": "d8759674aefdb45cbae9c5b23e5bc718e50023c26604f046732986acbea2a706",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/build.exit",
        "bytes": 2,
        "sha256": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/build.stderr",
        "bytes": 9304,
        "sha256": "e13e9cb9f3bc65497a1d4f5d670c1ee16e467ff918ccf56606af0dd0539b0602",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/feature-arguments.txt",
        "bytes": 22,
        "sha256": "3ca2207eaaf1dfe27510940220ed321701d80b0cd117cb9cde31bb4b8f1712be",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/git-status-after.txt",
        "bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/git-status-before.txt",
        "bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/tests.exit",
        "bytes": 2,
        "sha256": "9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/tests.stderr",
        "bytes": 12559,
        "sha256": "736e349317103ac9868e2650b219c561047cfcb7f9e8763fd8582ba2107edcd3",
        "equals_retained_build_input": true
      },
      {
        "member": "./reference/tests.stdout",
        "bytes": 15425,
        "sha256": "75ef518de4cad53d4df653bd689d93d37acbe82baacacd200c49a3c17bd80e41",
        "equals_retained_build_input": true
      },
      {
        "member": "./rustc.txt",
        "bytes": 203,
        "sha256": "dbd639801eacf9d8900b64719640b726c1ad6b3e8fc216b7f0b2eae7c256a602",
        "equals_retained_build_input": true
      },
      {
        "member": "./source-commit.txt",
        "bytes": 41,
        "sha256": "3266959ff44a44be35207cd0b3f4c12ef0229b94740b8c52cf12f303b75acd5c",
        "equals_retained_build_input": true
      },
      {
        "member": "./source-tree.txt",
        "bytes": 41,
        "sha256": "287314a07825126968029fb5cad2efca20548249f8c30e05cca5f709c9c1c746",
        "equals_retained_build_input": true
      }
    ]
  }
}
```
