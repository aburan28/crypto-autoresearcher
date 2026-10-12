# Public-point rare-event study

This agent-free runner measures fixed bit-64 point-window events for selected,
published and random generators, with 64 ordinary-prime field controls. The
locked default samples contain 5,905,580,032 point observations, organized in
independent-start 256-point windows. Read [PROTOCOL.md](PROTOCOL.md) for exact
sample counts, inference families, power limits and storage scope.

On Debian/Ubuntu, install `build-essential libssl-dev python3-venv`, create a
Python virtual environment, and run `pip install -r requirements.txt`. No GitHub,
AWS, model, or private-key credential is needed. `prepare.py` additionally needs
PARI GP only when preparing new models; the checked public inputs are included.

From this directory:

```sh
python -m unittest -v test_study
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research.py --output /large-disk/rare-study
python verify.py /large-disk/rare-study
python analyze.py /large-disk/rare-study
```

Run the identical command to resume after an operational stop. The runner uses
an exclusive lock, checks hashes, and refuses source/config changes in the
same directory. Failed attempt files are preserved. Analysis and verification
are write-once; use their saved JSON rather than overwriting it.

For a new independent study, choose `--seed your-public-seed` and a new output
directory. `--workers 3` changes only concurrency. `--full-coordinates` persists
every full coordinate (hundreds of GB for this default sample); otherwise the
runner saves all measured bits and integer scores, all random-step scalars,
full rare/witness coordinate frames, and hashes of the transient xy streams.
The compact dataset needs roughly a few GB including an archive; reserve extra
space for failed attempts. Edit an input/config copy prospectively for a
smaller run and pass `--inputs file.json --config file.json`. Do not relabel
those outputs as this locked default experiment.

The ordinary controls use public fixed steps, not certified full-group
generators. Neither an event-rate comparison nor a negative observation is an
ECDLP security or attack-cost result. Rare effects outside the measured bits,
thresholds and powered rate range remain open.
