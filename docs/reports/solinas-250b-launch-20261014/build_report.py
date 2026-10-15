"""Render the fixed launch snapshot; never reads live scientific outcomes."""
from pathlib import Path
import json
import os
import subprocess
os.environ.setdefault('MPLCONFIGDIR', '/tmp/solinas-250b-launch-mpl')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/solinas-250b-launch-cache')
for name in ('MPLCONFIGDIR', 'XDG_CACHE_HOME'):
    Path(os.environ[name]).mkdir(exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TASK = REPO / 'tasks/solinas_250b'
PUB = TASK / 'publication/launch-20261014'


def main():
    snapshot = json.loads((PUB / 'progress-at-snapshot.json').read_text())
    launch = json.loads((PUB / 'launch.json').read_text())
    runtime = json.loads((PUB / 'runtime.json').read_text())
    series = json.loads((PUB / 'progress-series.json').read_text())
    subprocess.run(['dot', '-Tsvg', str(HERE / 'pipeline.dot'), '-o', str(HERE / 'pipeline.svg')], check=True)
    plt.rcParams.update({'font.size': 9, 'svg.fonttype': 'none', 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axis = plt.subplots(figsize=(8.1, 2.9), constrained_layout=True)
    axis.step([r['elapsed_this_invocation_seconds'] for r in series],
              [r['point_observations'] / 1e6 for r in series], where='post', color='#226488')
    axis.scatter([r['elapsed_this_invocation_seconds'] for r in series],
                 [r['point_observations'] / 1e6 for r in series], s=12, color='#226488')
    axis.set(xlabel='Recorded elapsed sampling time (seconds)', ylabel='Completed observations (millions)',
             title='Recorded launch progress — campaign-250b-20261014')
    axis.grid(alpha=.2)
    fig.savefig(HERE / 'progress.svg')
    plt.close(fig)
    points = f"{snapshot['point_observations']:,}"
    jobs = snapshot['completed_jobs']
    command = ' '.join(launch['command'])
    text = f'''# 250-billion campaign launch — 14 October 2026

**Execution observations only. The campaign was running at this snapshot;
the 250-billion study is incomplete.** No interim significance test, scientific
verdict or security claim is reported.

Measured snapshot: `{snapshot['snapshot_at']}`. **{points} point observations**,
{jobs} of {snapshot['requested_jobs']:,} chunks, {snapshot['window_observations']:,}
window observations and {snapshot['independent_start_windows']:,} start draws.
All {points} native finite/on-curve checks passed. All {jobs} completed chunks
passed independent score replay and separate coordinate-frame arithmetic checks.
Zero failed attempts and zero infrastructure stops were recorded at the snapshot.
Completed-chunk process CPU time sums to {snapshot['completed_chunk_cpu_seconds']:.3f}
seconds (measured; excludes in-flight chunks). Three worker processes remained active.

![Executed pipeline](pipeline.svg)

![Recorded progress](progress.svg)

The graph contains recorded progress values only, sourced from the fixed launch
publication's `progress-series.json`. It has no statistical uncertainty interval:
these are exact completed-observation counters, not estimated population rates.
Points inside a window are dependent; named cohorts share starts. The target does
not mean 250 billion independent or distinct field points.

## Fixed remaining scope

| Population | Planned windows per cohort/model | Cohorts/models |
| --- | ---: | ---: |
| P-192 motif candidate | 44,389,200 | 3 |
| P-224 parity candidate | 44,389,200 | 3 |
| P-224 long-run candidate | 177,556,850 | 3 |
| Ordinary-prime controls | 1,420,454 | 125 |

Exactly 976,562,500 window observations × 256 points = 250,000,000,000 point
observations, from 443,892,000 independent-start draws (derived prospective
arithmetic). Named steps are selected H, actual published G, and fresh public rG.
The 62 R and 63 C models include every eligible model in the frozen ordinary-prime
pools; primes are reused from earlier work. Coefficients and step x are matched,
group/step orders are unmatched. All 125 field/cardinality preparations passed
PARI checks and separate Python [N]H checks before launch.

The fixed primary family has 18 exact paired generator contrasts and 2 approximate
field comparisons. Alpha 0.0001/20 gives nominal 99.99% family confidence, subject
to the field-test approximation. The separate 30-rate CP interval family is nominal
at least 99.99% under independent windows. Their union is nominal 99.98%, subject
to the same approximation. No final tests or rate intervals exist yet; the analyzer
runs only after exact completion. No outcome-based stopping or sample enlargement.
These counts do not resolve every ultra-rare or localized effect.

## Retention and reproducibility

**Aggregate mode is running.** It retains exact marginal/joint event counts,
descriptor sums/squares, source and stream hashes, sealed per-chunk validity records,
and prospectively selected full-coordinate witness/example frames. Most individual
bit strings/scalars are not saved for later arbitrary ML searches. Full compact
retention remains an open storage requirement: approximately 60–70 GB, versus
about 550 MB initially free and no configured managed AWS identity. Old datasets
and archives remain intact. See the [storage problem](../../../problems/solinas-250b-storage-unavailable.md).

Source commit `{launch['source_commit']}` was pushed before sampling. The base
was `{launch['base_main']}`; its merge preserved already-published upstream files.
The runtime dirty tree contained only the untracked preparation report and new
launch-publication directory; frozen scientific source files were unchanged.
Python {runtime['python'].split()[0]}, NumPy {runtime['numpy']}, SciPy {runtime['scipy']};
{runtime['openssl']}. Model/policy/usage metadata were not exposed and remain null.

Exact launch command, with OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1:

```sh
{command}
```

The detached PID was {launch['pid']} and had parent PID 1 at the snapshot. The machine
must remain active. The identical command resumes sealed work after interruption;
source/config/storage changes or corrupt records are refused. Completion and final
analysis are automatic, without an agent per batch. Runtime is expected to take
days on this host; this is advisory, not a performance or attack-cost claim.

## Immutable records and next action

- [Launch and exact command](../../../tasks/solinas_250b/publication/launch-20261014/launch.json)
- [Fixed progress snapshot](../../../tasks/solinas_250b/publication/launch-20261014/progress-at-snapshot.json)
- [Snapshot checksums and chunk records](../../../tasks/solinas_250b/publication/launch-20261014/manifest.json)
- [Protocol and standalone script](../../../tasks/solinas_250b/README.md)
- [Exact identities and parameters](../../../tasks/solinas_250b/inputs.json)
- [Prospective power record](../../../tasks/solinas_250b/power-plan.json)
- [Historical preparation report](../solinas-250b-20261012/report.md)
- [Completed predecessor PR 2108](https://github.com/aburan28/crypto-autoresearcher/pull/2108)

P-192 identity: urn:ec-record:1:sha256:b4bdde6340ec696e5fa11f3baf1ef941462bc731a526029d2bdc9dc49812aa4b.
P-224 identity: urn:ec-record:1:sha256:e2397ca7cfb5bfad66d0ec042758a09a0ee496e566266b793d2a9f36cf555484.
Sources are internal artifacts, read in this session. This launch changes no
canonical mechanism graph or official research status. The next action is to
finish the fixed campaign and publish its sealed completion and locked analysis
in a fresh report. This PDF is a launch snapshot, not a final-results report.
'''
    (HERE / 'report.md').write_text(text)
    source = f'''#set page(paper: "a4", margin: (x: 17mm, y: 15mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: 0.6em)
= 250-billion campaign launch
14 October 2026. Execution observations only: the campaign is running and the
study is incomplete. No interim significance test or security verdict.

*Measured:* {points} checked point observations in {jobs} of 27,133 chunks;
{snapshot['window_observations']:,} window observations and {snapshot['independent_start_windows']:,} start draws.
Zero failures / infrastructure stops. All completed chunks passed score replay
and separate coordinate-frame checks. Snapshot: {snapshot['snapshot_at']}.

#image("pipeline.svg", width: 86%)
#image("progress.svg", width: 100%)
Graph: exact recorded counters, not population-rate estimates; no uncertainty
interval applies. Source: publication/launch-20261014/progress-series.json.
Within-window points are dependent; named cohorts share starts.

#pagebreak()
= Fixed scope, retention and resumption
#table(columns: (2fr, 1.3fr, 1fr), inset: 5pt,
  [Population], [Planned windows/arm or model], [Arms/models],
  [P-192 motif], [44,389,200], [3],
  [P-224 parity], [44,389,200], [3],
  [P-224 long run], [177,556,850], [3],
  [Ordinary-prime controls], [1,420,454], [125])

*Derived prospective total:* 976,562,500 windows × 256 = 250,000,000,000 point
observations; 443,892,000 start draws. Selected / published / fresh random steps;
62 R + 63 C ordinary models. All 125 model preparations checked before launch.
Primes reused; coefficients and step x matched; group/step orders unmatched.

*Locked inference:* 18 exact paired contrasts + 2 approximate field comparisons;
alpha 0.0001/20, nominal 99.99% primary family with a field-approximation caveat.
Separate 30-rate CP family, nominal at least 99.99% under independent windows;
union nominal 99.98%, subject to the approximation. No final inference yet.
Analysis runs automatically only after exact completion; no outcome-based stopping.

*Aggregate retention:* exact counts, hashes and fixed full-coordinate samples.
Most individual bit strings/scalars are not retained for later arbitrary ML.
Full compact data require approximately 60–70 GB; initial free capacity was about
550 MB, with no configured managed AWS identity. Existing data remain intact.

*Measured runtime:* {snapshot['completed_chunk_cpu_seconds']:.3f} completed-chunk CPU seconds, excluding
in-flight chunks. Three worker processes were active; detached PID {launch['pid']},
parent PID 1. Python {runtime['python'].split()[0]}, NumPy {runtime['numpy']}, SciPy {runtime['scipy']}.
Unknown model/usage metadata remain null.

*Source pushed before sampling:* #text(size: 8pt)[{launch['source_commit']}].
Runtime dirty paths were only the new publication/preparation report; scientific
source was unchanged. See runtime.json, compile.json and manifest.json in
tasks/solinas_250b/publication/launch-20261014/.

*Standalone/resumable command:* tasks/solinas_250b/README.md. The identical command
and output path resume checksum-sealed chunks. Changed source/config/storage or
corruption is refused. The machine must remain active; the run is expected to take
days. No agent is needed per batch. This is not an ECDLP-cost or speedup claim.

*Evidence:* the launch snapshot and sealed chunk records in publication/launch-20261014/;
exact public parameters and full curve UIDs in tasks/solinas_250b/inputs.json;
protocol/power records in the same task; predecessor PR 2108. Internal sources,
read in this session. No canonical mechanism graph or official status changes.
Next: fixed completion, locked final analysis and a fresh final-results report.
'''
    (HERE / 'report.typ').write_text(source)
    typst.compile(str(HERE / 'report.typ'), output=str(HERE / 'report.pdf'))
    print(json.dumps({'report': str(HERE / 'report.pdf'), 'snapshot_points': snapshot['point_observations'], 'campaign_complete': False}))


if __name__ == '__main__':
    main()
