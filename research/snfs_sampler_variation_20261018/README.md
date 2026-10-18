# Sampler support and within-input variation

Continuation of the field-lift observation card, using
`EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532`.

- [Report](report/REPORT.md), [PDF](report/report.pdf), and
  [observation YAML](report/observation.yaml).
- [Coefficient support](data/sampler-support.json),
  [exact cubic catalog](data/cubic-catalog.json), and
  [draw multiplicities](data/draw-multiplicities.json).
- [Within-input groups](data/within-input-groups.json),
  [all 48 trajectory rows](data/within-input-trajectories.csv), and
  [three weighting views](data/weighting-views.json).
- [Source hashes, timing and status](data/summary.json) and
  [mechanical replay receipt](verification.json).

These are saved-data summaries plus a finite reference calculation, not fresh
field/curve searches. Original rows and native `invalid_output` remain intact.
The reader makes interpretation and relevance calls. Higher-degree admissible
support and new fixed-input search replicas remain unmeasured here.

Replay into a fresh directory; neither command overwrites earlier outputs:

```sh
python3 research/snfs_sampler_variation_20261018/analyze.py --out /tmp/new-sampler-analysis
python3 research/snfs_sampler_variation_20261018/verify.py /tmp/new-sampler-analysis --receipt /tmp/new-sampler-check.json
```

Rendering uses matplotlib, PyYAML, Typst and PyMuPDF. The renderer reads the
published `data/` beside it and writes to a fresh output directory:

```sh
python3 research/snfs_sampler_variation_20261018/render_report.py --out /tmp/new-sampler-report
python3 tools/check_experiment_observation.py /tmp/new-sampler-report/observation.yaml --check-artifacts
```

The mechanical checker is authored and replayed by this session, not an
independent scientific review. CSV retains the standard writer's CRLF bytes;
authored-text whitespace checks exclude that recorded CSV.
