# Shifted-cover survey execution contract

Administrative preparation only. The survey retains both exact p4099 fixtures,
sixteen native atoms and the original sixty-four seed0 public sources. It
records every h=0..4098, all eighty membership tests per shift, with no early
stop or collector-yield selection:8,198 frames total. It measures complete
finite admissibility and public-source lift coverage; no collector, new base,
rank, subgroup symmetry, isogeny or attack advantage is implied.

Root owns git/checkpoint/release and scientific execution through the public
run skill. From the repository root, first commit/push exact native driver,
cover_frames.py and all administrative source. `SOURCE_COMMIT` below must be
that real source commit. No extra user approval is needed.

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_cover_survey_20261029/prepare.py protocol --source-commit SOURCE_COMMIT --out research/prime_field_cover_survey_20261029/protocol.json --freeze
```

Commit/push frozen protocol; update resume with exact source/protocol hashes,
command and guards; perform actual canonical `scripts/checkpoint.sh push` and
`gate`. Explicitly bind/release those committed bytes:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_cover_survey_20261029/prepare.py release --source-commit SOURCE_COMMIT --protocol research/prime_field_cover_survey_20261029/protocol.json --out research/prime_field_cover_survey_20261029/release.json --owner root-prime-field-cover-survey --authorize-root
```

Commit/push release. Once B1's sole compute process has ended, invoke the native
survey under the run skill:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_cover_survey_20261029/supervise.py --protocol research/prime_field_cover_survey_20261029/protocol.json --release research/prime_field_cover_survey_20261029/release.json --owner root-prime-field-cover-survey --out FRESH_RUN_DIRECTORY
```

The exclusive supervisor lease records source/host/ownership/PIDs.2GiB memory
and3,600s wall/CPU watchdog protect the host; they are not measured runtime or
research spending limits. The native driver checks committed inputs, sources,
interpreter, prospective protocol, explicit release and actual canonical S3
gate. It retains an admission receipt, survey, separate verification and phase
journal. No in-process restore; a retry needs fresh output.

Preserve every failure/stop. Root may losslessly gzip raw files before export,
retaining exactly one encoding per logical file. Then:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python research/prime_field_cover_survey_20261029/analyze.py --run FRESH_RUN_DIRECTORY --protocol research/prime_field_cover_survey_20261029/protocol.json
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python tools/experiment_protocol.py check-export FRESH_RUN_DIRECTORY/export.json --protocol research/prime_field_cover_survey_20261029/protocol.json --verify-files
```

Two survey fixture cells and two integrated oracle method cells share one
physical process. Duplicate exact counts must not be summed; reference costs
are empty. Whole-process diagnostic resources appear once in backend_record; each fixture’s native counters appear only in its survey row. All clocks have wall_valid=false. Unknown fixture cells
retain null counts; a complete collected cell remains unverified until the
separate complete verification checks all8,198frames and128source points.
An independent roots-set oracle and separate public-source arithmetic provide
an implementation check, not independent scientific review.

Export hashes all retained files, including final gzip bytes, status, phases,
receipts and logs. Artifact storage must preserve hydrated bytes at original
paths; subsequent storage manifests/receipts are separate immutable records.
Root's run report still requires a diagram and inspected PDF. No official
research-state record or model attestation is created here.
