#!/usr/bin/env python3
"""Publish observations and an explanation from the existing G3 run records."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import yaml

def fmt(x):
    return "missing" if x is None else f"{x:.6f}"

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--primary', type=Path, required=True)
    p.add_argument('--replay', type=Path, required=True)
    a=p.parse_args()
    out=a.out
    d=json.loads((out/'derived-summary.json').read_text())
    raw=json.loads((a.primary/'raw-result.json').read_text())
    manifest=yaml.safe_load((a.primary/'manifest.yaml').read_text())
    manifest2=yaml.safe_load((a.replay/'manifest.yaml').read_text())
    h1=hashlib.sha256((a.primary/'raw-result.json').read_bytes()).hexdigest()
    h2=hashlib.sha256((a.replay/'raw-result.json').read_bytes()).hexdigest()
    replay_equal=(a.primary/'raw-result.json').read_bytes()==(a.replay/'raw-result.json').read_bytes()
    replay={'control':'CTRL-REPLAY','primary_run':a.primary.name,'replay_run':a.replay.name,
            'same_raw_result_bytes':replay_equal,'primary_sha256':h1,'replay_sha256':h2}
    (out/'replay-check.json').write_text(json.dumps(replay,indent=2)+'\n')
    execution={'execution_report':{'experiment_id':'EXP-ECDLP-4c6a09',
               'implementation_commit':manifest['git_commit'], 'scientific_input_deviations':[],
               'runtime_differences_from_design': ['Rust 1.99.0 rather than design-container Rust 1.97',
                    'PARI 2.17.2 rather than design-container PARI 2.15.4',
                    'The full CTRL-REPLAY invocation overlaps the primary run on the four-CPU host'],
               'runs':{'completed':[a.primary.name,a.replay.name],
                       'invalid':[] if replay_equal else [a.primary.name,a.replay.name], 'failed':[]},
               'cells_per_invocation':d['cells'], 'ctrl_shape':raw['ctrl_shape'],
               'ctrl_replay':replay_equal, 'rank_arm':'skipped; no descent over number fields available',
               'missing_gamma_count':d['gamma_missing_total'],
               'data_quality':'limited to the existing bounded point-search implementation and declared toy inputs',
               'scientific_review_performed':False, 'asserts_nothing_about':'hypothesis status or ECDLP complexity'}}
    (out/'execution-report.yaml').write_text(yaml.safe_dump(execution,sort_keys=False))
    for r in [a.primary,a.replay]:
        shutil.copy2(Path('/workspace/solinas-runtime')/(r.name+'-process.json'),out/(r.name+'-process.json'))
    shutil.copy2('/workspace/solinas-runtime/run_g3.py',out/'run_g3.py')
    shutil.copy2('/workspace/solinas-runtime/build.log',out/'build.log')
    rows={}
    for s in ['P-192','P-224','P-256','P-384']:
        ss=next(g for g in d['groups'] if g['shape']==s and g['kind']=='solinas')
        gg=next(g for g in d['groups'] if g['shape']==s and g['kind']=='random_g')
        delta=raw['summary']['per_shape'][s]['gamma_solinas_minus_random_g']
        rows[s]=(ss,gg,delta)
    reg=raw['summary']['regression_gamma_vs_log_root_discriminant']
    comparison='\n'.join(f"| {s} | {ss['gamma_finite_n']}/{ss['cells']} | {fmt(ss['gamma_mean'])} | {gg['gamma_finite_n']}/{gg['cells']} | {fmt(gg['gamma_mean'])} | {fmt(delta)} |" for s,(ss,gg,delta) in rows.items())
    group_table='\n'.join(f"| {g['shape']} | {g['kind']} | {g['cells']} | {g['distinct_polynomials']} | {g['distinct_finite_curves']} | {fmt(g['final_D_mean'])} | {g['final_D_range']} | {fmt(g['reported_nontorsion_mean'])} | {g['height_finite_n']} | {fmt(g['height_mean'])} |" for g in d['groups'])
    primes='\n'.join(f"| {s} | {k} | {prime} | {bits} |" for s,k,prime,bits in d['solinas_instances'])
    wall=manifest['wall_clock_seconds']
    wall2=manifest2['wall_clock_seconds']
    theory=Path(__file__).with_name('theory.md').read_text()
    md=f'''# Solinas number-field experiment — observations and theory

Date: 2026-10-11 UTC. Experiment **EXP-ECDLP-4c6a09**; hypothesis
**H-ECDLP-4da36f**; goal **GOAL-ECDLP-001**. Original implementation:
[PR #2035](https://github.com/aburan28/crypto-autoresearcher/pull/2035),
commit `{manifest['git_commit']}`. This is an execution report and derived
explanation. It does not promote, reject, or close a research claim.

## Recorded outcome — measured unless labeled arithmetic

The complete documented input set produced **{d['cells']} cells** in
**{wall:.3f} seconds**. The full seeded replay produced the same raw JSON
bytes in **{wall2:.3f} seconds**: CTRL-REPLAY **{'passed' if replay_equal else 'FAILED'}**.
Both invocations retained seeds 1, 2, 3, 20 requested random fields per shape,
5 curves per field, and all 6 checkpoints through 100,000 candidate x attempts.
Completed cells by seed: `{d['counts_by_seed']}`.
Every cell reached the final work count: **{d['all_cells_reached_100000']}**.
Scientific process failures in these two invocations: none (see preserved
exit-code records). Timings overlap on the same four-CPU-quota host and are
execution measurements, not algorithmic performance bounds.

The following means are arithmetic on the recorded gamma values. Missing
gamma values are omitted from these means and explicitly counted; a missing
gamma means the runner had fewer than two positive-coverage checkpoints.
There are **{d['gamma_missing_total']} missing slopes out of {d['cells']} cells**.

| Shape | Solinas fitted/total | Solinas mean gamma | Random fitted/total | Random mean gamma | Solinas minus random |
|---|---:|---:|---:|---:|---:|
{comparison}

Recorded regression of gamma on natural log of field root discriminant:
slope **{fmt(reg['slope'])}**, runner's 99% bootstrap interval
**[{fmt(reg['ci99'][0])}, {fmt(reg['ci99'][1])}]**, **n={reg['n']}** fitted
non-rational-field cells. The interval is copied from the existing runner;
it resamples cells, not independent field clusters. Repeated fields and
curves therefore limit a confidence interpretation. No new significance
test or confidence interval is claimed. The pooled regression also has no
degree adjustment and is not a causal estimate of a discriminant effect.

The frozen specification compares absolute mean-gamma differences to 0.2
and asks whether the regression interval contains zero. These thresholds
are preserved; the table and interval expose the recorded values directly.
Its “within sampling error” comparison for point counts and heights does
not specify an executable statistical test, so no post hoc test has been
added here. The full scientific success criterion is not assessed.

![Construction and experimental question](construction.svg)

{theory}

## Recorded coverage and slopes

![Coverage](coverage.svg)

Lines are arithmetic means across all cells of an arm, including zero-point
cells. Shading is the observed minimum-to-maximum range, not uncertainty of
the mean. Search work counts candidate x attempts, not processor time.

![Recorded finite-search slopes](gamma.svg)

Dots are recorded cell values; diamonds are arithmetic means of nonmissing
values. Shared fields, repeated curves, and two signs of points are not
independent samples. These slopes concern a fixed finite search window.

![Root discriminant and recorded slopes](discriminant.svg)

The regression uses PARI's field discriminant whenever available. Non-Q
cells missing that control: **{d['nonq_cells_without_pari_nfdisc']}**.

## Exact tested scope and descriptive counts

The four labels identify NIST polynomial *shapes*. No deployed NIST-size
ECDLP was solved or searched. Solinas input primes in this run are:

| Shape | k, m=2^k | p=f(2^k) | p bits |
|---|---:|---|---:|
{primes}

All curves are `y^2=x^3+A*x+B` with the recorded A and B, nonsingular with
good reduction at the selected p according to the existing launcher.
The complete per-cell identities (defining polynomial, p, A, B, seed and
curve index) are in [cells.csv](cells.csv) and the raw JSON. No subgroup or
unknown-log challenge is selected; coverage is on the full curve's recorded
affine residues. Q is a degree-one control, not a comparison number field
of matching degree. The t^d-c arm exists only where the existing toy-prime
selector found an eligible field.

The next table is arithmetic on the raw records. “Distinct polynomials”
counts presentations, not field isomorphism classes. Distinct finite curves
counts the triples (p,A,B). Heights are means over the recorded finite
minimum-height values, not over missing entries. New-point counts are the
runner's non-rational/non-torsion classification, not independent ranks.

| Shape | Arm | Cells | Distinct polynomials | Distinct finite curves | Mean final D | D range | Mean reported new points | Height n | Mean min log-height/log p |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
{group_table}

## Required tail records — copied observations

Largest recorded gamma cell (ties use the first cell in run order):

```json
{json.dumps(d['largest_gamma_cell'],indent=2)}
```

Smallest recorded field root discriminant among degree > 1 cells (ties
use the first cell in run order):

```json
{json.dumps(d['smallest_nonq_root_discriminant_cell'],indent=2)}
```

## Reproduction and limits

Primary run: `{a.primary.name}`. Replay: `{a.replay.name}`.
Raw SHA-256 (both runs when replay passes): `{h1}`.
The manifests include exact source hashes, compiler/library versions,
timestamps, per-cell time, and the executed argv. Launch records include
dirty-tree state. The primary source tree was clean; the replay dirty state
contains the primary run's untracked output directory, with no source edits.
Source implementation and specifications were not changed.
The launch-file model label denotes the interface-stated GPT-6 family;
no provider model-ID probe or inference-usage counter was available. It is
not a verified resolved model identifier.

Exact scientific argv (primary output path shown):

```text
{manifest['command']}
```

This invokes the existing release binary with the specification's complete
arguments. Build command:

```sh
cargo build --release --locked --features pari --manifest-path experiments/EXP-ECDLP-4c6a09/implementation/Cargo.toml --bin g3
```

Build and run environment uses workspace-local rustup/cargo and extracted
Debian PARI packages, leaving system libraries unchanged:

```text
CARGO_HOME=/workspace/solinas-toolchain/cargo
RUSTUP_HOME=/workspace/solinas-toolchain/rustup
PATH=/workspace/solinas-toolchain/cargo/bin:$PATH
C_INCLUDE_PATH=/workspace/solinas-runtime/pari/usr/include/x86_64-linux-gnu:/workspace/solinas-runtime/pari/usr/include
LIBRARY_PATH=/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu
LD_LIBRARY_PATH=/workspace/solinas-runtime/pari/usr/lib/x86_64-linux-gnu
CARGO_BUILD_JOBS=2
```

Actual compiler: `{manifest['rustc']}`. Actual PARI:
`{manifest['gp_version']}`. Platform: `{manifest['platform']}`.
The launcher was built with the optional PARI feature enabled.
Each process was capped at 4 GiB virtual address space. CPU/RSS measurements
are preserved in the process JSON files beside this report; child usage
includes minor launch-time git/rustc subprocesses. Execution logs and raw
results remain in the original write-once run directories.

Controls observed: CTRL-SHAPE is `{raw['ctrl_shape']}` in raw output;
CTRL-REPLAY is `{replay_equal}` from literal byte comparison.
Random-g field selection uses the existing irreducibility admission
predicate; no separate independent field-certification phase was performed.
All rank-arm labels remain the launcher's explicit skipped label. The frozen
specification's comparisons require separate research interpretation and
review; this report preserves its metrics rather than changing its criteria.

Scope limits: fixed candidate budget, bounded square-root reconstruction,
power-basis and denominator restrictions, unequal prime sizes, replacement
sampling, shared curves, missing fitted slopes, no rank/independence
certificate, no arbitrary-target lift, and no end-to-end relation or ECDLP
recovery experiment. Low or high observed coverage concerns this algorithm
and these inputs only.

Proposed follow-up checks, not performed in this session: independently
reimplement the point-search/square-root arm; compare equal completed
coefficient shells at higher degrees; preregister an analysis accounting
for degree and repeated field/curve clusters; and use descent or independent
generators to measure rank gain over E(Q). An ECDLP claim would additionally
require arbitrary-target lifts or useful relations and complete recovery
costs. These are future checks, not extra trials attributed to this run.

Existing graph check: the tracked G3 experiment directory and ECDLP frontier
tree contained no existing SVG/Mermaid/DOT/Typst/PDF graph specific to this
experiment in this revision. No canonical graph or scientific status was
changed; all visuals here are new views of the cited observations.

## Sources and artifacts

All experiment citations have provenance **internal** (files inspected in
this session). The algebraic example and ring-map argument are **derived**
above. No external paper is being cited from memory.

- [Frozen specification](../../specification.yaml): declared controls,
  inputs, prediction, bounds, rank-arm omission and launcher.
- [Original G3 source](../../implementation/src/main.rs): measures and
  summaries, at the exact code revision recorded above.
- Shared `EXP-ECDLP-84af7b/implementation/nfield/src/field.rs`, `ecnf.rs`,
  `gp.rs`: arithmetic, bounded square-root reconstruction, point search,
  reduction, torsion classification and PARI discriminants; hashes are in
  each manifest.
- [Primary raw JSON](../../runs/{a.primary.name}/raw-result.json),
  [primary manifest](../../runs/{a.primary.name}/manifest.yaml),
  [primary launch record](../../runs/{a.primary.name}/launch.json),
  [primary stderr](../../runs/{a.primary.name}/stderr.log).
- [Replay raw JSON](../../runs/{a.replay.name}/raw-result.json),
  [replay manifest](../../runs/{a.replay.name}/manifest.yaml),
  [byte-comparison receipt](replay-check.json).
- [Derived summary](derived-summary.json), [all cell identities](cells.csv),
  [graph source](make_figures.py), [report generator](write_report.py),
  [PDF source](report.typ), [PDF](report.pdf).
'''
    (out/'report.md').write_text(md)
    typ_table=',\n'.join(f'[{s}], [{ss["gamma_finite_n"]}/{ss["cells"]}], [{fmt(ss["gamma_mean"])}], [{gg["gamma_finite_n"]}/{gg["cells"]}], [{fmt(gg["gamma_mean"])}], [{fmt(delta)}]' for s,(ss,gg,delta) in rows.items())
    typ=r'''#set page(paper: "a4", margin: (x: 18mm, y: 16mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: .65em)
#set heading(numbering: none)
#set table(stroke: .4pt + luma(75%), inset: 5pt)
#show heading.where(level: 1): set text(size: 18pt, fill: rgb("176b87"))
#show heading.where(level: 2): set text(size: 12pt, fill: rgb("176b87"))
= Solinas number fields
Experiment observations and a worked explanation · 11 October 2026 UTC

*EXP-ECDLP-4c6a09* · H-ECDLP-4da36f · GOAL-ECDLP-001

== Recorded execution
''' + f'''The existing complete input set finished *{d['cells']} cells* in *{wall:.1f} s*.
A full three-seed replay finished in *{wall2:.1f} s*. The raw results are
*{'byte-identical' if replay_equal else 'NOT byte-identical'}*. All recorded cells reached W=100,000.
These are observations; the scientific hypothesis has not been promoted.

#table(columns: (auto, auto, auto, auto, auto, auto),
  [Shape], [Solinas n], [Mean γ], [Random n], [Mean γ], [Difference],
  {typ_table}
)

“n” gives fitted/total cells. There are *{d['gamma_missing_total']} missing slopes* overall.
Means exclude missing values. Repeated fields and curves are retained;
the table does not assert independent sampling.

#figure(image("coverage.svg", width: 100%), caption: [
  Arithmetic mean coverage across all cells, including zero-point cells.
  Shading is observed min–max, not a confidence interval.])

#text(size: 8pt)[Primary {a.primary.name}; replay {a.replay.name}.
The two single-threaded invocations overlap on a host with a four-CPU quota.]

#pagebreak()
= How the construction works
#image("construction.svg", width: 100%)

== 1. Turn the short prime formula into exact algebra
Write $p=f(m)$, with $m=2^k$, and introduce a symbolic root $alpha$ with
$f(alpha)=0$. If $f$ is irreducible, $K=QQ(alpha)$ is a number field.
For $f(t)=t^3-t-1$, this means $alpha^3=alpha+1$.

== 2. Reduce the algebra back to the finite field
Because $f(m)=p equiv 0$ modulo $p$, substitution $alpha mapsto m$ defines
a ring map $ZZ[alpha] -> FF_p$. Fractions with invertible denominators
can also be reduced. This is not a map from all of the characteristic-zero
field $K$ to $FF_p$. At good reduction, elliptic-curve reduction respects
point addition.

== 3. See an actual point identity
Choose $m=4$, $p=59$ and $E: y^2=x^3-x+3$. Then
$alpha^3-alpha+3=4$, so $(alpha,2)$ is an exact point over $K$.
It reduces to $(4,2)$ because $4^3-4+3=63 equiv 4$ modulo 59.
This is a derived example below the experiment's prime cutoff, not a
measured trial or a rank claim. The discriminant $-16 dot 239$ is nonzero
modulo 59, so this example has good reduction.

== 4. Ask whether this supplies points efficiently
The experiment tries small power-basis coordinates for $x$, searches for
an exact square root of $x^3+A x+B$ in $K$, then counts distinct reductions.
Accepted roots are verified exactly; bounded reconstruction can miss roots.
It compares the same search rule in Solinas and random comparison fields.

== Why the discriminant and rank matter
The algebraic integers form a lattice with covolume proportional to
$sqrt(abs(D_K))$, where $D_K$ is the field discriminant. The root discriminant $abs(D_K)^(1/d)$ normalizes
by degree. Smaller discriminants motivate smaller coordinates; they do not
force the curve equation to have a square root. PARI supplies field
discriminants, which can differ from the defining-polynomial discriminant.

More discovered points do not certify greater rank: independent generators
must be proved independent. The number-field rank arm is explicitly skipped.

#pagebreak()
= What the measurements mean
#figure(image("gamma.svg", width: 92%), caption: [
  γ is a fitted log–log slope over up to the last three positive-coverage
  checkpoints. Dots are cell values; diamonds are arithmetic means.
  This is finite-search growth, not an asymptotic ECDLP exponent.])

#figure(image("discriminant.svg", width: 92%), caption: [
  Recorded field discriminants and fitted slopes. The interval is copied
  from the runner's cell bootstrap; it does not model shared-field or
  shared-curve dependence.])

Recorded regression: slope *{fmt(reg['slope'])}*, 99% interval
*[{fmt(reg['ci99'][0])}, {fmt(reg['ci99'][1])}]*, n={reg['n']}.
Non-Q cells without a PARI field discriminant: {d['nonq_cells_without_pari_nfdisc']}.

#pagebreak()
= Reproduction and remaining gaps
== Exact scope
Seeds 1, 2, 3; 20 requested random fields per shape per seed; 5 curves per
field; candidate checkpoints 300, 1,000, 3,000, 10,000, 30,000, 100,000;
8 auxiliary primes. Curves are $y^2=x^3+A x+B$ with seeded integer
coefficients from −20 to 20 and good reduction at the selected toy prime.
The CSV and raw JSON contain every defining polynomial, modulus and curve.
No subgroup or unknown discrete-log challenge was selected.

The NIST names label polynomial shapes; this is not a deployed-size
curve experiment. Rank and point independence are unmeasured. Heights are
logarithmic coefficient-height proxies, not canonical point heights. Random fields match degree and
polynomial weight, but can repeat and have different prime sizes.

== The gap to a discrete-log algorithm
The multiplicative number field sieve factors small norms into prime
ideals to obtain useful log relations. Elliptic-curve points add; small
coordinates do not supply the same factorization automatically. A usable
method would still need affordable lifts or relations for arbitrary target
points, justified independence, and full recovery costs against a baseline.
This run measures a supply of points and their coverage, not that method.

== Execution identity
Code revision: #text(size: 8pt)[{manifest['git_commit']}]

Compiler: #text(size: 8pt)[{manifest['rustc']}]

PARI: #text(size: 8pt)[{manifest['gp_version']}]

The release binary used the complete documented argv. Each process had a
4 GiB address-space cap. Manifests preserve source hashes, command,
timestamps and per-cell timing; launch records preserve dirty-tree state.
Sources were unchanged. CTRL-SHAPE is {raw['ctrl_shape']}; literal raw-byte
CTRL-REPLAY is {replay_equal}. All rank-arm records retain the skipped label.

== Evidence and source files
All experiment sources have internal provenance and were inspected in this
session. Algebraic identities above are derived. The source implementation
is in #link("https://github.com/aburan28/crypto-autoresearcher/pull/2035")[PR #2035].
The complete commands, prime table, counts, required extreme-cell records,
resource receipts and caveats are in the accompanying #link("report.md")[Markdown report].

Primary: #text(size: 8pt)[{a.primary.name}]

Replay: #text(size: 8pt)[{a.replay.name}]

SHA-256 of raw JSON:
#text(size: 7pt)[{h1}]

#link("../../runs/{a.primary.name}/raw-result.json")[Primary raw JSON] ·
#link("../../runs/{a.primary.name}/manifest.yaml")[Manifest] ·
#link("replay-check.json")[Replay check] · #link("cells.csv")[Cell identities]

The PDF, Typst source and SVG graph sources are communication artifacts.
No scientific status, canonical frontier graph or ledger record was changed.
'''
    (out/'report.typ').write_text(typ)
    print(json.dumps({'report':str(out/'report.md'),'same_raw_bytes':replay_equal,'cells':d['cells']}))

if __name__=='__main__':
    main()
